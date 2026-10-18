# Ollama service + GPU diagnostics

## Find the REAL service (port, model dir, global ctx)
Ollama is rarely at defaults on a managed box. Discover the truth before trusting `localhost:11434`:

```bash
# Env + start command carry HOST / MODELS / CONTEXT_LENGTH
systemctl cat ollama.service | grep -E 'Environment=|ExecStart'
#   => OLLAMA_HOST, OLLAMA_MODELS, OLLAMA_CONTEXT_LENGTH
ss -tlnp | grep -E '11434|ollama'         # confirm actually listening
```

Observed in the field: custom port `0.0.0.0:55242`; models in `/mnt/data/ollama_models`
(or `/var/lib/ollama`); a baked-in `OLLAMA_CONTEXT_LENGTH=8192`. The `ollama list` / `ollama ps`
commands fail with "could not connect to ollama server" when the client can't find the non-default
port — read the unit's `OLLAMA_HOST` instead of assuming 11434.

Pulled models:
```bash
ls <OLLAMA_MODELS>/manifests/registry.ollama.ai/library/   # one dir per model family
curl -s http://<host>:<port>/api/tags   # name, parameter_size, quant, context_length, capabilities
```

## Which GPU backend is Ollama actually using? (Vulkan / ROCm / CUDA)
Don't guess — read the scheduler log, it names the device and backend:

```bash
nvidia-smi 2>/dev/null || echo "no nvidia"
lspci | grep -iE 'vga|3d'
ls /usr/share/vulkan/icd.d/                    # Vulkan ICD present?
vulkaninfo --summary 2>/dev/null | head        # GPU as RADV/VK device?
journalctl -u ollama --no-pager | grep -iE 'gpu|vulkan|rocm|cuda|device' | tail
```

Good (working offload) looks like:
```
... using device Vulkan0 (AMD Radeon RX 580 Series (RADV POLARIS10)) (8192 MiB, 6728 MiB free)
... library=Vulkan total="8.0 GiB" available="3.5 GiB"
llama_kv_cache: Vulkan0 KV buffer size = ...
clip_ctx: CLIP using Vulkan0 backend
```

### The ROCm-vs-Vulkan AMD rule
- Old AMD GCN/RDNA (RX 4xx/5xx/580, etc.) are **not** in ROCm's supported list, so the ROCm/HIP path is out.
- But Ollama's **Vulkan** backend (radvison) does support them. So an RX 580 CAN offload.
- If the journal shows `library=Vulkan` + your card, offload is already live — no config needed.

### VRAM-sized cards → hybrid CPU+GPU split
On an ~8GB card with a model near/at VRAM size (~7GB), Ollama does **hybrid split**: weights partly
in RAM, KV on GPU. The scheduler may log:
```
msg="llama-server model predicted to exceed available memory, evicting" predicted="6.7 GiB" ...
```
That is it falling back to CPU for the overflow — not a crash. Tune the amount kept on-GPU with
`--num_gpu N` / `PARAMETER num_gpu N` (N = # layers on GPU). Bump until load still fits.
Old CPU + old RAM still sets the decode floor, so GPU offload is a few× win, not 10-20×.

## Decoding speed
The `api/generate` response fields:
- `load_duration` (ns) — model load time (first call; cached after)
- `prompt_eval_count`, `prompt_eval_duration` (ns) — prefill
- `eval_count`, `eval_duration` (ns) — generation

**Gotcha:** in the API, `eval_duration` can mix prompt+decode, so a quick
`eval_count / eval_duration` can look absurd (>1000 to/s). For a clean decode number:
1. warm the cache (run once),
2. then measure a fixed `num_predict` (e.g. 64) by wall time, dividing decoded tokens by that time, or
3. quote `prompt_eval_*` (prefill) and `eval_duration` (decode) separately and don't present a
single blended to/s as if it were decode speed.

## Quick probe (any real port)
```bash
curl -s --max-time 20 http://<host>:<port>/api/generate \
  -d '{"model":"gemma4:e2b","prompt":"hi","stream":false,"options":{"num_predict":1,"num_ctx":2048}}'
```
A successful JSON (even empty choices) = the model loaded on whatever device Ollama picked.
