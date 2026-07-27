"""Pipeline dubbingu: pobranie filmu -> transkrypcja -> tlumaczenie -> TTS -> miks audio.

Wszystkie ciezkie zaleznosci (faster-whisper, yt-dlp, edge-tts, deep-translator,
pydub) importowane sa leniwie wewnatrz funkcji, dzieki czemu serwer startuje
szybko, a bledy brakujacych pakietow pojawiaja sie dopiero przy uzyciu danego
etapu.
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Sygnatura: report(stage, procent 0-100, komunikat dla uzytkownika)
ProgressFn = Callable[[str, float, str], None]

VOICES = {
    "marek": "pl-PL-MarekNeural",
    "zofia": "pl-PL-ZofiaNeural",
}

WHISPER_MODELS = {"tiny", "base", "small", "medium", "large-v3"}

# Maksymalne przyspieszenie polskiej kwestii, zeby zmiescila sie w slocie
# czasowym oryginalnej wypowiedzi. Powyzej tej wartosci mowa robi sie
# nienaturalna, wiec pozwalamy kwestii wystawac poza slot.
MAX_TEMPO = 1.9


@dataclass
class Segment:
    start: float
    end: float
    text: str
    text_pl: str = ""
    audio_path: Path | None = None


@dataclass
class PipelineResult:
    video_path: Path
    srt_path: Path
    detected_language: str = ""
    segments: list[Segment] = field(default_factory=list)


class PipelineError(RuntimeError):
    """Blad etapu pipeline'u z komunikatem zrozumialym dla uzytkownika."""


def _run(cmd: list[str], error_hint: str) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-800:]
        raise PipelineError(f"{error_hint}\n{tail}")


def _ffprobe_duration(path: Path) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        raise PipelineError(f"Nie udalo sie odczytac dlugosci pliku: {path.name}")


def _has_audio_stream(path: Path) -> bool:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return bool(proc.stdout.strip())


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


# ---------------------------------------------------------------------------
# Etap 1: pozyskanie wideo
# ---------------------------------------------------------------------------

def download_video(url: str, workdir: Path, report: ProgressFn) -> Path:
    import yt_dlp

    target = workdir / "source.mp4"

    def hook(d: dict) -> None:
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes")
            if total and done:
                report("download", 100.0 * done / total, "Pobieranie filmu...")

    opts = {
        "outtmpl": str(workdir / "source.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "progress_hooks": [hook],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except Exception as exc:  # yt-dlp rzuca wlasne typy bledow
        raise PipelineError(f"Nie udalo sie pobrac filmu z podanego linku: {exc}")

    if target.exists():
        return target
    candidates = [p for p in workdir.glob("source.*") if p.suffix != ".part"]
    if not candidates:
        raise PipelineError("Pobieranie zakonczone, ale nie znaleziono pliku wideo.")
    return candidates[0]


# ---------------------------------------------------------------------------
# Etap 2: transkrypcja (faster-whisper)
# ---------------------------------------------------------------------------

def extract_audio_for_asr(video: Path, workdir: Path) -> Path:
    wav = workdir / "asr_input.wav"
    _run(
        ["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "pcm_s16le", str(wav)],
        "Nie udalo sie wyodrebnic sciezki audio z filmu (czy plik zawiera dzwiek?).",
    )
    return wav


def _transcribe_pass(model, wav: Path, total: float, vad_filter: bool,
                     report: ProgressFn) -> tuple[list[Segment], str]:
    raw_segments, info = model.transcribe(str(wav), vad_filter=vad_filter)

    segments: list[Segment] = []
    for seg in raw_segments:
        text = seg.text.strip()
        if text:
            segments.append(Segment(start=seg.start, end=seg.end, text=text))
        report("transcribe", min(100.0, 100.0 * seg.end / total),
               "Transkrypcja mowy...")
    return segments, info.language


def _load_whisper_model(model_size: str):
    from faster_whisper import WhisperModel

    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return WhisperModel(model_size, device="cuda", compute_type="float16")
    except Exception:
        pass
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe(wav: Path, model_size: str, report: ProgressFn) -> tuple[list[Segment], str]:
    report("transcribe", 0, f"Ladowanie modelu Whisper ({model_size})...")
    model = _load_whisper_model(model_size)

    total = max(_ffprobe_duration(wav), 0.01)

    # Filtr VAD (wykrywanie aktywnosci glosowej) potrafi blednie uznac spiew
    # z podkladem muzycznym za brak mowy, wiec przy pustym wyniku probujemy
    # jeszcze raz bez niego, zanim zglosimy blad.
    segments, language = _transcribe_pass(model, wav, total, True, report)
    if not segments:
        report("transcribe", 0, "Nie wykryto mowy z filtrem VAD - probuje bez niego...")
        segments, language = _transcribe_pass(model, wav, total, False, report)

    if not segments:
        raise PipelineError("Nie wykryto mowy w filmie - nie ma czego dubbingowac.")
    return segments, language


# ---------------------------------------------------------------------------
# Etap 3: tlumaczenie na polski
# ---------------------------------------------------------------------------

def translate_segments(segments: list[Segment], source_lang: str, report: ProgressFn) -> None:
    from deep_translator import GoogleTranslator

    if source_lang == "pl":
        for seg in segments:
            seg.text_pl = seg.text
        return

    translator = GoogleTranslator(source="auto", target="pl")
    batch_size = 20
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i + batch_size]
        try:
            translated = translator.translate_batch([s.text for s in batch])
        except Exception:
            # Fallback: pojedynczo, zeby jeden zly fragment nie polozyl calosci.
            translated = []
            for s in batch:
                try:
                    translated.append(translator.translate(s.text))
                except Exception:
                    translated.append(s.text)
        for seg, text_pl in zip(batch, translated):
            seg.text_pl = (text_pl or seg.text).strip()
        report("translate", 100.0 * min(i + batch_size, len(segments)) / len(segments),
               "Tlumaczenie na jezyk polski...")


# ---------------------------------------------------------------------------
# Etap 4: synteza mowy (Edge TTS) + dopasowanie tempa do slotow czasowych
# ---------------------------------------------------------------------------

async def _tts_one(text: str, voice: str, out_mp3: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out_mp3))


def synthesize_segments(segments: list[Segment], voice_key: str, workdir: Path,
                        total_duration: float, report: ProgressFn) -> None:
    from pydub import AudioSegment

    voice = VOICES.get(voice_key, VOICES["marek"])
    tts_dir = workdir / "tts"
    tts_dir.mkdir(exist_ok=True)

    loop = asyncio.new_event_loop()
    try:
        for idx, seg in enumerate(segments):
            if not seg.text_pl:
                continue
            mp3 = tts_dir / f"seg_{idx:04d}.mp3"
            wav = tts_dir / f"seg_{idx:04d}.wav"
            try:
                loop.run_until_complete(_tts_one(seg.text_pl, voice, mp3))
            except Exception as exc:
                raise PipelineError(
                    f"Blad syntezy mowy (Edge TTS) dla fragmentu {idx + 1}: {exc}")

            tts_len = len(AudioSegment.from_file(mp3)) / 1000.0

            # Slot konczy sie na poczatku nastepnej wypowiedzi (albo na koncu
            # filmu), zeby kwestie nie nachodzily na siebie.
            slot_end = segments[idx + 1].start if idx + 1 < len(segments) else total_duration
            slot = max(slot_end - seg.start, 0.5)
            tempo = min(max(tts_len / slot, 1.0), MAX_TEMPO)

            filters = f"atempo={tempo:.3f}" if tempo > 1.01 else "anull"
            _run(
                ["ffmpeg", "-y", "-i", str(mp3), "-filter:a", filters,
                 "-ac", "2", "-ar", "44100", str(wav)],
                f"Nie udalo sie przetworzyc audio fragmentu {idx + 1}.",
            )
            seg.audio_path = wav
            report("tts", 100.0 * (idx + 1) / len(segments),
                   f"Generowanie polskiego glosu ({idx + 1}/{len(segments)})...")
    finally:
        loop.close()


def build_voice_track(segments: list[Segment], total_duration: float, workdir: Path) -> Path:
    from pydub import AudioSegment

    track = AudioSegment.silent(duration=int(total_duration * 1000) + 2000, frame_rate=44100)
    for seg in segments:
        if seg.audio_path is None:
            continue
        clip = AudioSegment.from_file(seg.audio_path)
        track = track.overlay(clip, position=int(seg.start * 1000))

    out = workdir / "voice_track.wav"
    track.export(out, format="wav")
    return out


# ---------------------------------------------------------------------------
# Etap 5: miks (ducking oryginalu) i zlozenie wyjsciowego pliku
# ---------------------------------------------------------------------------

def mix_and_mux(video: Path, voice_track: Path, srt: Path | None,
                workdir: Path, burn_subtitles: bool, report: ProgressFn) -> Path:
    out = workdir / "output.mp4"
    report("mix", 10, "Miksowanie sciezek audio...")

    if _has_audio_stream(video):
        # Sidechain: oryginalne audio jest automatycznie sciszane tylko wtedy,
        # gdy gra polski lektor - muzyka i efekty zostaja slyszalne miedzy
        # kwestiami.
        filter_complex = (
            "[1:a]asplit=2[sc][voice];"
            "[0:a][sc]sidechaincompress=threshold=0.02:ratio=12:attack=20:release=400[ducked];"
            "[ducked][voice]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            "alimiter=limit=0.95[aout]"
        )
    else:
        filter_complex = "[1:a]anull[aout]"

    cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(voice_track),
           "-filter_complex", filter_complex]

    if burn_subtitles and srt is not None:
        # Wypalanie napisow wymaga reenkodowania wideo.
        srt_escaped = str(srt).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        cmd += ["-map", "0:v", "-map", "[aout]",
                "-vf", f"subtitles='{srt_escaped}'",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    else:
        cmd += ["-map", "0:v", "-map", "[aout]", "-c:v", "copy"]

    cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
    _run(cmd, "Nie udalo sie zlozyc koncowego pliku wideo.")
    report("mix", 100, "Skladanie pliku wyjsciowego...")
    return out


# ---------------------------------------------------------------------------
# Napisy SRT
# ---------------------------------------------------------------------------

def _srt_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments: list[Segment], path: Path) -> Path:
    lines = []
    for i, seg in enumerate(segments, start=1):
        lines.append(str(i))
        lines.append(f"{_srt_timestamp(seg.start)} --> {_srt_timestamp(seg.end)}")
        lines.append(seg.text_pl or seg.text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Calosc
# ---------------------------------------------------------------------------

def run_pipeline(workdir: Path, report: ProgressFn, *,
                 url: str | None = None,
                 input_file: Path | None = None,
                 voice: str = "marek",
                 model_size: str = "small",
                 burn_subtitles: bool = False) -> PipelineResult:
    if not check_ffmpeg():
        raise PipelineError(
            "Brak ffmpeg/ffprobe w systemie. Zainstaluj ffmpeg i sprobuj ponownie.")
    if model_size not in WHISPER_MODELS:
        model_size = "small"

    if url:
        report("download", 0, "Pobieranie filmu...")
        video = download_video(url, workdir, report)
    elif input_file is not None:
        video = input_file
    else:
        raise PipelineError("Nie podano ani linku, ani pliku wideo.")

    total_duration = _ffprobe_duration(video)

    report("transcribe", 0, "Przygotowanie audio do transkrypcji...")
    wav = extract_audio_for_asr(video, workdir)
    segments, language = transcribe(wav, model_size, report)

    report("translate", 0, "Tlumaczenie na jezyk polski...")
    translate_segments(segments, language, report)

    srt = write_srt(segments, workdir / "napisy_pl.srt")

    report("tts", 0, "Generowanie polskiego glosu...")
    synthesize_segments(segments, voice, workdir, total_duration, report)
    voice_track = build_voice_track(segments, total_duration, workdir)

    output = mix_and_mux(video, voice_track, srt, workdir, burn_subtitles, report)

    return PipelineResult(video_path=output, srt_path=srt,
                          detected_language=language, segments=segments)
