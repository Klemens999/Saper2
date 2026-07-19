# 🎬 Polski Dubbing AI

Aplikacja webowa, która bierze **dowolny film** (link, np. YouTube, albo plik z dysku)
i automatycznie **tłumaczy go na język polski i dubbinguje** — w stylu lektora:
oryginalna ścieżka dźwiękowa jest inteligentnie wyciszana tylko wtedy, gdy mówi
polski głos, więc muzyka i efekty dźwiękowe pozostają słyszalne.

Całość działa na **darmowych** usługach — bez żadnych kluczy API.

## Jak to działa (pipeline)

| Etap | Narzędzie | Koszt |
|------|-----------|-------|
| 1. Pobranie filmu z linku | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | darmowe |
| 2. Transkrypcja mowy z timestampami | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (lokalnie, CPU) | darmowe |
| 3. Tłumaczenie na polski | deep-translator (Google Translate) | darmowe |
| 4. Synteza polskiego głosu | [edge-tts](https://github.com/rany2/edge-tts) (głosy neuronowe Microsoftu: Marek / Zofia) | darmowe |
| 5. Dopasowanie tempa kwestii do czasu oryginalnych wypowiedzi | ffmpeg `atempo` | darmowe |
| 6. Miks: ducking oryginału (sidechain compression) + polski głos | ffmpeg | darmowe |
| 7. Polskie napisy `.srt` (opcjonalnie wypalane na obrazie) | ffmpeg | darmowe |

## Wymagania

- Python 3.10+
- **ffmpeg** i **ffprobe** w `PATH`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: `winget install ffmpeg`
- Dostęp do internetu (pobieranie filmów, tłumaczenie, Edge TTS; sam Whisper działa lokalnie)

## Instalacja i uruchomienie

```bash
cd dubbing-app
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # serwer na http://127.0.0.1:8000
```

Otwórz **http://127.0.0.1:8000** w przeglądarce:

1. Wklej link do filmu **albo** przeciągnij plik wideo.
2. Wybierz głos lektora (Marek/Zofia) i jakość transkrypcji.
3. Kliknij „Przetłumacz i zdubbinguj" i obserwuj pasek postępu.
4. Pobierz gotowy **MP4 z polskim dubbingiem** oraz **napisy SRT**.

> Przy pierwszym użyciu wybrany model Whisper zostanie automatycznie pobrany
> (np. `small` ≈ 460 MB) i zapisany w cache — kolejne uruchomienia są szybkie.

## Opcje

- **Głos lektora** — `Marek` (męski) lub `Zofia` (żeński), neuronowe głosy pl-PL.
- **Jakość transkrypcji** — model Whisper od `tiny` (najszybszy) do `large-v3`
  (najdokładniejszy). Na CPU polecany jest `small` lub `base`.
- **Wypalanie napisów** — nanosi polskie napisy bezpośrednio na obraz
  (wymaga przekodowania wideo, więc trwa dłużej).

## API (dla integracji)

- `POST /api/jobs` — multipart: `url` **lub** `file`, opcjonalnie `voice`,
  `model_size`, `burn_subtitles`. Zwraca `{"id": "..."}`.
- `GET /api/jobs/{id}` — status i postęp zadania.
- `GET /api/jobs/{id}/download/video` — gotowy MP4.
- `GET /api/jobs/{id}/download/srt` — polskie napisy.
- `DELETE /api/jobs/{id}` — usuwa zadanie i jego pliki robocze.

## Wydajność

- Transkrypcja działa lokalnie na CPU (`int8`), z filtrem VAD pomijającym ciszę.
- Zadania przetwarzane są w tle (kolejka jednowątkowa — ciężkie etapy nie
  duszą się nawzajem), a frontend odpytuje o postęp.
- Kwestie lektora są automatycznie przyspieszane (do 1.9×), aby zmieściły się
  w slocie czasowym oryginalnej wypowiedzi.
- Pliki robocze każdego zadania trzymane są w `data/jobs/<id>/` i można je
  usunąć jednym żądaniem `DELETE`.

## Uwagi prawne

Dubbinguj tylko materiały, do których masz prawa (własne filmy, materiały na
wolnych licencjach itp.). Pobieranie treści z serwisów wideo może naruszać ich
regulaminy.
