"""Prosty menedzer zadan: kazde zadanie dubbingu dziala w osobnym watku."""

from __future__ import annotations

import shutil
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import pipeline

# Wagi etapow w calkowitym pasku postepu (suma = 100).
STAGE_WEIGHTS = {
    "download": 10,
    "transcribe": 35,
    "translate": 10,
    "tts": 30,
    "mix": 15,
}
STAGE_LABELS = {
    "download": "Pobieranie filmu",
    "transcribe": "Transkrypcja mowy",
    "translate": "Tlumaczenie na polski",
    "tts": "Generowanie polskiego glosu",
    "mix": "Miksowanie i skladanie pliku",
}
STAGE_ORDER = list(STAGE_WEIGHTS)


@dataclass
class Job:
    id: str
    workdir: Path
    status: str = "queued"  # queued | running | done | error
    stage: str = ""
    progress: float = 0.0
    message: str = "Oczekiwanie w kolejce..."
    error: str = ""
    detected_language: str = ""
    result_video: Path | None = None
    result_srt: Path | None = None
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def to_dict(self) -> dict:
        with self.lock:
            return {
                "id": self.id,
                "status": self.status,
                "stage": self.stage,
                "stage_label": STAGE_LABELS.get(self.stage, ""),
                "progress": round(self.progress, 1),
                "message": self.message,
                "error": self.error,
                "detected_language": self.detected_language,
                "has_video": self.result_video is not None,
                "has_srt": self.result_srt is not None,
            }


class JobManager:
    def __init__(self, base_dir: Path, max_workers: int = 1):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Jeden worker: transkrypcja i TTS sa ciezkie, rownolegle zadania
        # tylko by sie dusily nawzajem.
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: dict[str, Job] = {}
        self._jobs_lock = threading.Lock()

    def create(self) -> Job:
        job_id = uuid.uuid4().hex[:12]
        workdir = self.base_dir / job_id
        workdir.mkdir(parents=True, exist_ok=True)
        job = Job(id=job_id, workdir=workdir)
        with self._jobs_lock:
            self.jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._jobs_lock:
            return self.jobs.get(job_id)

    def submit(self, job: Job, **pipeline_kwargs) -> None:
        self.executor.submit(self._run, job, pipeline_kwargs)

    def _run(self, job: Job, pipeline_kwargs: dict) -> None:
        def report(stage: str, pct: float, message: str) -> None:
            # Postep calkowity = suma wag ukonczonych etapow + czesc biezacego.
            done_before = sum(STAGE_WEIGHTS[s] for s in STAGE_ORDER[:STAGE_ORDER.index(stage)])
            overall = done_before + STAGE_WEIGHTS[stage] * min(max(pct, 0), 100) / 100
            with job.lock:
                job.stage = stage
                job.progress = min(overall, 99.9)
                job.message = message

        with job.lock:
            job.status = "running"
            job.message = "Start przetwarzania..."
        try:
            result = pipeline.run_pipeline(job.workdir, report, **pipeline_kwargs)
            with job.lock:
                job.status = "done"
                job.progress = 100.0
                job.message = "Gotowe!"
                job.detected_language = result.detected_language
                job.result_video = result.video_path
                job.result_srt = result.srt_path
        except pipeline.PipelineError as exc:
            with job.lock:
                job.status = "error"
                job.error = str(exc)
                job.message = "Wystapil blad."
        except Exception as exc:  # nieprzewidziane bledy tez pokazujemy
            with job.lock:
                job.status = "error"
                job.error = f"Nieoczekiwany blad: {exc!r}"
                job.message = "Wystapil blad."

    def cleanup(self, job_id: str) -> bool:
        with self._jobs_lock:
            job = self.jobs.pop(job_id, None)
        if job is None:
            return False
        shutil.rmtree(job.workdir, ignore_errors=True)
        return True
