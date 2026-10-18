# Hermes TTS provider reference (mined from tools/tts_tool.py)

## Full provider comparison (Hermes built-ins)
| Provider | Quality | Cost | API key | On-device | Model size | CPU speed | Voices |
|---|---|---|---|---|---|---|---|
| edge | Good | Free | none | no | — | instant | 322 (74 langs) |
| elevenlabs | Excellent | Paid | ELEVENLABS_API_KEY | no | — | fast | many |
| openai | Good | Paid | VOICE_TOOLS_OPENAI_KEY | no | — | fast | 6 |
| minimax | Excellent | Paid | MINIMAX_API_KEY / MINIMAX_CN_API_KEY | no | — | fast | many |
| mistral (Voxtral) | Excellent | Paid | MISTRAL_API_KEY | no | — | fast | many |
| gemini | Excellent | Free tier | GEMINI_API_KEY | no | — | fast | many |
| xai | Excellent | Paid | XAI_API_KEY | no | — | fast | many |
| deepinfra | Good | Paid | DEEPINFRA_API_KEY | no | — | fast | many |
| neutts | Good | Free | none | **yes** | ~748MB | ~1.2x realtime | 1 (cloned) |
| **kittentts** | Good | Free | none | **yes** | ~25MB | ~6x realtime | 8 expressive |
| **piper** | Good | Free | none | **yes** | ~75MB | ~3-5x realtime | 904 speakers |

## Local provider config schema (read via .get() at runtime)
### kittentts (tools/tts_tool.py `_generate_kittentts`)
- `model`: default `KittenML/kitten-tts-nano-0.8-int8` (also available:
  kitten-tts-micro-0.8 ~41MB, kitten-tts-mini-0.8 ~80MB)
- `voice`: default `Jasper` — options: Jasper, Bella, Luna, Bruno, Rosie, Hugo,
  Kiki, Leo
- `speed`: 0.5–2.0 (default 1.0)
- `clean_text`: true expands numbers/currencies/units (default true)
- Output: WAV @ 24kHz via soundfile; converted to MP3/Opus by ffmpeg if needed.

### piper (tools/tts_tool.py `_generate_piper_tts`)
- `voice`: default `en_US-lessac-medium` — any piper voice name (auto-downloaded
  via `python -m piper.download_voices` into `voices_dir`)
- `voices_dir`: default `~/.hermes/cache/piper-voices/`
- `use_cuda`: false (requires onnxruntime-gpu)
- advanced knobs (only passed if present): `length_scale` (1.0=normal, 2.0=half
  speed), `noise_scale` (0.667), `noise_w_scale` (0.8), `volume` (1.0),
  `normalize_audio` (true), `speaker_id` (int; bool rejected)
- Output: WAV; converted to MP3/Opus by ffmpeg if needed.

### neutts (default before this change)
- `model`: `neuphonic/neutts-air-q4-gguf` (also `neuphonic/neutts-nano`); runs
  in a separate process that exits after synthesis
- `device`: cpu (or cuda)
- `ref_audio` / `ref_text`: optional voice-clone reference
- SLOW on CPU (~748MB); replacement target.

## Venv / import checks
- venv: `~/.hermes/hermes-agent/venv/bin`
- `from kittentts import KittenTTS` (require KittenML 0.8.1 wheel, NOT PyPI 0.1.3)
- `from piper import PiperVoice`
- Pre-present deps: soundfile, onnxruntime, huggingface_hub, torch
- System: `ffmpeg` required for MP3/Opus output conversion

## Observed timings (this host, CPU)
| Engine | first call (model download) | cached |
|---|---|---|
| kittentts | 7.5s | 4.6s |
| piper | 2.9s | 1.4s |
| neutts (old default) | timed out @120s | — |
