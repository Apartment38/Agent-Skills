---
name: hermes-local-tts
description: Set up and troubleshoot Hermes on-device TTS providers.
version: 1
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [tts, kittentts, piper, local, hermes-agent, voice, audio, setup]
    related_skills: [hermes-agent]
---

# Hermes on-device TTS (KittenTTS + Piper)

## When to use
- User wants faster or fully-local TTS (no API key, no cloud dependency).
- Hermes TTS times out or is slow. The default `neutts` provider runs a ~748M
  model on CPU and can exceed the 120s synthesis timeout. This is the #1 reason
  users look for an alternative.
- User mentions KittenTTS, Piper, or asks to switch TTS providers.

## Provider landscape (Hermes built-ins)
Hermes supports: edge, elevenlabs, openai, minimax, mistral, gemini, xai,
deepinfra, **neutts (local)**, **kittentts (local)**, **piper (local)**.

| Provider | Size | CPU speed | Voices | On-device? | Notes |
|---|---|---|---|---|---|
| `kittentts` | ~25MB | ~6x realtime | 8 expressive | yes | Fastest on-device |
| `piper` | ~75MB | ~3-5x realtime | 904 speakers | yes | Best voice variety |
| `neutts` (default) | ~748MB | ~1.2x realtime | 1 (cloned) | yes | **Slow on CPU — times out** |
| `edge` | — | instant | 322 | no (cloud) | No key needed but needs network |

For Discord/Telegram voice bubbles: Edge emits MP3; KittenTTS & Piper emit WAV
(`tools/tts_tool.py` converts via ffmpeg when MP3/Opus is requested). ffmpeg must
be installed system-wide (`which ffmpeg`).

## Install (into Hermes' venv — NOT installed by default)
```bash
VENV=~/.hermes/hermes-agent/venv/bin
$VENV/pip install piper-tts

# CRITICAL: the PyPI default `kittentts` (0.1.3) CANNOT resolve HF repo IDs.
# It passes the repo id straight to onnxruntime as a local file path and fails
# with NO_SUCHFILE. Install the KittenML 0.8.1 wheel, which has get_model()
# resolution that downloads from the Hub:
$VENV/pip install "https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl"
```
Verify both import:
```bash
$VENV/python -c "from kittentts import KittenTTS; print('ok')"
$VENV/python -c "from piper import PiperVoice; print('ok')"
```
Deps usually already in the venv: `soundfile`, `onnxruntime`, `huggingface_hub`.
Models auto-download on first synthesis (KittenTTS via `get_model`; Piper via
`python -m piper.download_voices` into `~/.hermes/cache/piper-voices/`).

## Configure — config file is WRITE-PROTECTED
You CANNOT `write_file` or `patch` `~/.hermes/config.yaml` directly — Hermes
refuses agent writes ("Refusing to write to Hermes config file… Edit directly or
use 'hermes config'"). Always use dotted keys via the CLI:
```bash
H=~/.hermes/hermes-agent/venv/bin/hermes
$H config set tts.provider kittentts
$H config set tts.kittentts.model "KittenML/kitten-tts-nano-0.8-int8"
$H config set tts.kittentts.voice Jasper          # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
$H config set tts.piper.voice en_US-lessac-medium  # any piper voice name
```
Schema warnings ("'tts.kittentts.speed' is not a recognized config key — saved
anyway") are **benign**: Hermes reads these via `.get()` at runtime, so they are
honored. Don't be alarmed.

### Config keys Hermes actually reads (from tools/tts_tool.py)
- `kittentts`: `model` (def `KittenML/kitten-tts-nano-0.8-int8`), `voice` (def
  `Jasper`), `speed`, `clean_text`
- `piper`: `voice` (def `en_US-lessac-medium`), `voices_dir`, `use_cuda`,
  `speaker_id`, `length_scale`, `noise_scale`, `noise_w_scale`, `volume`,
  `normalize_audio`
- To switch per-message without changing config, call the text_to_speech tool
  with `provider: "piper"` (or `"kittentts"`, `"edge"`).

## Verify end-to-end (no agent UI needed)
```bash
cd ~/.hermes/hermes-agent && venv/bin/python - <<'PY'
import yaml, os
from tools.tts_tool import _generate_kittentts, _generate_piper_tts, _check_kittentts_available, _check_piper_available
cfg = yaml.safe_load(open(os.path.expanduser("~/.hermes/config.yaml"))).get("tts", {})
print("kitten", _check_kittentts_available(), "piper", _check_piper_available())
_generate_kittentts("test one two", "/tmp/k.wav", cfg)
_generate_piper_tts("test one two", "/tmp/p.wav", cfg)
PY
```
Then send a real voice message via the `text_to_speech` tool (omit `provider`
to use the config default — confirms the production path honors the new config).

## Pitfalls (this session hit all of these)
1. **PyPI `kittentts` 0.1.3 is broken for Hermes.** Symptom:
   `onnxruntime NO_SUCHFILE: Load model KittenML/kitten-tts-nano-0.8-int8 failed:
   File doesn't exist`. Fix: install the 0.8.1 wheel (see Install).
2. **`neutts` default is slow** — if a voice message times out, switch off it.
3. **Config direct edit is blocked** — always `hermes config set`.
4. **First synthesis downloads the model** (KittenTTS ~7s, Piper ~3s on first
   call). Cached runs are fast (KittenTTS ~4.6s, Piper ~1.4s on this host).
5. Schema "not a recognized key" warnings are safe to ignore.

## References
- `references/provider-reference.md` — full provider/speed/voice table and the
  exact config-schema details mined from `tools/tts_tool.py`.
