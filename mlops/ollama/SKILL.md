---
name: ollama
description: "Ollama context sizing, GPU offload, service discovery."
version: 1.0.0
metadata:
  hermes:
    tags: [Ollama, local-LLM, num_ctx, context-window, KV-cache, GPU-offload, Vulkan, ROCm, AMD, CPU-inference, systemd]
---

# Ollama — serving, context sizing, GPU offload

Use this when the user runs models through Ollama and you need to: recommend a
context-window size per model; fix a model truncating too early; figure out whether
a GPU is actually being used (especially old AMD); or find where a non-standard
Ollama service is running.

Distinct from `llama-cpp` (choosing quant/GGUF + low-level server flags) and
`serving-llms-vllm` (high-throughput OpenAI-API server). Ollama is the server/config
layer on top of the same llama.cpp kernel.

## First: find the REAL service
Ollama is almost never at the defaults on a managed box. Before trusting any
`localhost:11434` call, locate the actual endpoint and model dir:

```bash
# Port + model store + global defaults are set in the systemd unit env
systemctl cat ollama.service 2>/dev/null | grep -E 'Environment=|ExecStart'
#   -> OLLAMA_HOST, OLLAMA_MODELS, OLLAMA_CONTEXT_LENGTH
ss -tlnp | grep -E '11434|ollama'          # confirm it is actually listening
```

Real examples from the field:
- service on a **custom port** (e.g. `0.0.0.0:55242`, not 11434),
- models in a **non-standard dir** (`OLLAMA_MODELS=/mnt/data/ollama_models` or `/var/lib/ollama`),
- a global `OLLAMA_CONTEXT_LENGTH=8192` already baked in (so the "default" is 8K, not the stock 2K-4K).

Query what is actually loaded, with the **real** port:
```bash
curl -s --max-time 5 http://<host>:<port>/api/tags | head -c 4000
# gives: name, parameter_size, quantization_level, context_length, capabilities
```

List of pulled models on disk:
```bash
ls <OLLAMA_MODELS>/manifests/registry.ollama.ai/library/   # one dir per model family
```

## The num_ctx default-truncation trap (most common bug)
Ollama's default context is version- and configuration-dependent. Current documentation describes VRAM-based defaults; older versions used small fixed defaults. Inspect the service environment and actual runner allocation. A model that reports a 128K/256K/1M native limit can still run with a much smaller context unless overridden.
When the user says "the model forgets / stops mid-answer / truncates", this is the
usual cause, **not** the model's native window.

Three ways to set it:
```bash
# 1) Global env (coarse; a good default floor)
export OLLAMA_CONTEXT_LENGTH=65536
# 2) Baked into a tag (Modelfile) — survives restarts
printf 'FROM qwen3.8:27b\nPARAMETER num_ctx 65536\n' > Modelfile
ollama create my-qwen -f Modelfile
# 3) Per-request (cleanest for a varying laptop budget; no re-tag)
curl -s http://<host>:<port>/api/chat -d '{"model":"q","options":{"num_ctx":65536},"messages":[...]}'
```
Do not assume `ollama run` accepts `--num_ctx` or `--num_gpu`: check the installed CLI help (0.32.13 does not). Use Modelfile `PARAMETER` values, native API `options`, or supported interactive `/set parameter` commands instead.

## Sizing a context window (methodology)
The real ceiling is `min(memory, native_window, decode_speed_on_this_cpu)`. On a
CPU-only box the **decode speed**, not RAM, is usually the binding constraint — a slow
CPU + old RAM (e.g. a 2013 i7 + DDR3) will *load* a 256K context but crawl at a few
tokens/s. Set ceilings by use-case tier, not by the reported max:

- **Agentic / standard** (tool loops, code): ~16K
- **Personal assistant / chat**: ~8K
- **Long-doc / batch**: 32K, only if the user accepts the decode cost
- Past that = offline batch work, not interactive.

**KV cache is the memory term** (per token, fp16):
```
per_token_bytes = 2 (K+V) x <KV-caching layers> x num_kv_heads x head_dim x 2
```

Two corrections that cut the naive estimate:
1. `<KV-caching layers>` ≠ num_hidden_layers for **hybrid** models. Local/sliding-window,
   DeltaNet/linear-attention, and conv (Qwen3, Gemma local:global, LFM, Mamba-family) keep
   KV only on a fraction of layers — often the 5:1 "global" ones.
2. **K=V sharing** (some Gemma/Longcat-style) reuses keys as values → ~2x less KV again.

So the full-attention `num_hidden_layers` figure is an **upper bound**; hybrid + K=V models fit
far larger contexts than a naive table suggests. Read the model config for the true KV-head
count, head_dim, and *global-only* layer count before quoting a memory ceiling.

Full worked per-model tables across three hardware tiers are in
**[references/context-sizing.md](references/context-sizing.md)**.

## GPU offload: ROCm vs Vulkan (AMD gotcha)
Do NOT reflexively conclude "old AMD RX 5xx can't do LLM inference — it's a hardware limit."
That lore is true for **ROCm/HIP only**. Modern Ollama (llama.cpp) also has a **Vulkan**
backend that covers old AMD GCN cards (RX 4xx/5xx/580) — ROCm does not, Vulkan does. So
"can I offload my RX 580?" is often **already yes, via Vulkan**.

How to verify which backend is actually being used (don't guess):
```bash
nvidia-smi 2>/dev/null || echo "no nvidia"
lspci | grep -iE 'vga|3d'
ls /usr/share/vulkan/icd.d/                      # Vulkan ICD present?
vulkaninfo --summary 2>/dev/null | head          # GPU shows as RADV/VK device?
journalctl -u ollama --no-pager | grep -iE 'gpu|vulkan|rocm|cuda|device' | tail
#   want lines like:  ... using device Vulkan0 (AMD ... RX 580 ...) (8192 MiB, ...)
#   ... or  library=CUDA / library=ROCm for the respective paths
```

Reading the result:
- **`library=Vulkan` + your card in the log** → offload is live. No config needed; that's the path that unlocked the old AMD card.
- **Small-VRAM card (~8GB) with a model near/at VRAM size** → Ollama does a **hybrid CPU+GPU split**. If measurements justify overriding automatic placement, tune `PARAMETER num_gpu` or native API `options.num_gpu`. The scheduler may log "model predicted to exceed available memory, evicting" — that's it falling back to CPU, not a crash.
- **Old GCN + old DDR3 CPU** → GPU offload helps (a few×, not 10-20×) because CPU memory bandwidth is still the floor. Expect modest wins and slower-than-NVIDIA decode.

## Benchmarking (ground the speed claims)
```bash
curl -s http://<host>:<port>/api/generate \
  -d '{"model":"gemma4:12b","prompt":"hi","stream":false,"options":{"num_predict":64,"num_ctx":2048}}'
# read: load_duration, prompt_eval_count/duration, eval_count/eval_duration
```
Calculate decode throughput as `eval_count / (eval_duration / 1e9)`; durations are nanoseconds. Report prompt throughput using its separate count/duration, and wall time separately because it includes loading and other overhead. Save raw responses and verify suspicious values against runner timing logs. Distinguish short-prompt measurements at a large allocated context from filled-context performance; one does not establish the other.

## Common issues

- **"Model truncates / loses context early"** → num_ctx default is tiny (2K-4K). Override it (3 ways above); check `OLLAMA_CONTEXT_LENGTH` in the unit env.
- **"RX 580 / old AMD not being used"** → it may *already be* used via Vulkan; grep the journal before assuming a hardware wall.
- **"Model won't load / evicted"** → VRAM too small for full-GPU; it's splitting to CPU. Fine but slower; lower `num_gpu` or pick a smaller model.
- **"Can't reach ollama / list fails"** → service on a custom port, or not started. `systemctl cat` for the real `OLLAMA_HOST`, or start with `ollama serve`.
- **"Why is it slow?"** → on CPU-only boxes the binding constraint is decode speed + RAM bandwidth, not context fit. Don't inflate num_ctx for speed's sake.

## Output format (when recommending context windows)
Return a compact table: model / role, agentic ctx, PA ctx, long-doc ctx, and a one-line
"why" (fits VRAM? hybrid split? decode-bound?). Then a ready-to-use `num_ctx` per model.

## References

- **[references/variant-registration-validation.md](references/variant-registration-validation.md)** — no-download inheritance, exact-context registration, structured tool/embedding tests, memory accounting and client documentation.
- **[references/context-sizing.md](references/context-sizing.md)** — KV-cache formula, worked per-model tables per hardware tier, per-model num_ctx.
- **[references/service-and-gpu-diagnostics.md](references/service-and-gpu-diagnostics.md)** — finding the real service/port/model dir, verifying GPU backend (Vulkan/ROCm/CUDA), benchmarking decode, journalctl patterns.
