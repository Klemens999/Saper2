"""Aplikacja webowa do tlumaczenia i dubbingowania filmow na jezyk polski."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from . import pipeline
from .jobs import JobManager

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DUBBING_DATA_DIR", BASE_DIR.parent / "data"))

ALLOWED_UPLOAD_SUFFIXES = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpg", ".mpeg", ".ts", ".wmv",
}

app = FastAPI(title="Polski Dubbing AI", version="1.0.0")
manager = JobManager(DATA_DIR / "jobs")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((BASE_DIR / "static" / "index.html").read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "ffmpeg": pipeline.check_ffmpeg()}


@app.post("/api/jobs")
async def create_job(
    url: str = Form(""),
    voice: str = Form("marek"),
    model_size: str = Form("small"),
    burn_subtitles: bool = Form(False),
    file: UploadFile | None = File(None),
) -> JSONResponse:
    url = url.strip()
    has_file = file is not None and (file.filename or "") != ""
    if not url and not has_file:
        raise HTTPException(400, "Podaj link do filmu albo wgraj plik wideo.")
    if url and has_file:
        raise HTTPException(400, "Podaj albo link, albo plik - nie oba naraz.")
    if voice not in pipeline.VOICES:
        raise HTTPException(400, f"Nieznany glos: {voice}")
    if model_size not in pipeline.WHISPER_MODELS:
        raise HTTPException(400, f"Nieznany model Whisper: {model_size}")

    job = manager.create()

    input_file: Path | None = None
    if has_file:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_SUFFIXES:
            manager.cleanup(job.id)
            raise HTTPException(
                400, f"Nieobslugiwany format pliku: {suffix or '(brak rozszerzenia)'}")
        input_file = job.workdir / f"upload{suffix}"
        with input_file.open("wb") as out:
            shutil.copyfileobj(file.file, out)

    manager.submit(
        job,
        url=url or None,
        input_file=input_file,
        voice=voice,
        model_size=model_size,
        burn_subtitles=burn_subtitles,
    )
    return JSONResponse({"id": job.id}, status_code=202)


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    job = manager.get(job_id)
    if job is None:
        raise HTTPException(404, "Nie znaleziono zadania.")
    return job.to_dict()


@app.get("/api/jobs/{job_id}/download/{kind}")
def download(job_id: str, kind: str) -> FileResponse:
    job = manager.get(job_id)
    if job is None:
        raise HTTPException(404, "Nie znaleziono zadania.")
    with job.lock:
        if kind == "video" and job.result_video is not None:
            return FileResponse(job.result_video, media_type="video/mp4",
                                filename=f"dubbing_pl_{job_id}.mp4")
        if kind == "srt" and job.result_srt is not None:
            return FileResponse(job.result_srt, media_type="text/plain",
                                filename=f"napisy_pl_{job_id}.srt")
    raise HTTPException(404, "Plik nie jest jeszcze gotowy.")


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: str) -> dict:
    job = manager.get(job_id)
    if job is not None and job.status == "running":
        raise HTTPException(409, "Zadanie w trakcie przetwarzania - nie mozna usunac.")
    if not manager.cleanup(job_id):
        raise HTTPException(404, "Nie znaleziono zadania.")
    return {"ok": True}
