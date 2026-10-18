# Ollama per-model context-window recommendation

How to size `num_ctx` for a given model on a given box. The naive memory model is:

```
total_needed = weights_bytes + KV_cache_bytes(num_ctx) + overhead
```

where `KV_cache_bytes(num_ctx) = num_ctx x layers x 2 x heads_kv x head_dim x bytes_per_element`
(fp16 = 2). The model's **native** window is a ceiling, not a target — a 256K/1M context that
*fits* can still decode at 2-5 tok/s on the target CPU, which the user will experience as "frozen."

The real recommendation is `min(native_window, what_decode_speed_can_handle, what_VRAM_can_fit)`.

## Worked examples (from real sessions)

### Laptop: 32GB LPDDR5X shared, Arc iGPU, CPU-inference (lap587, ThinkPad X1 Carbon G13)
CPU + Arc iGPU share 32GB; weights come out of the RAM pool. For Q4_K_M (≈0.575B bytes/param
with headroom) assume ~24GB usable for inference after OS + iGPU:

| Model | Arch / KV note | Native ctx | Q4_K_M wt | Per-token KV (fp16) | 64K KV | 128K KV | **Rec num_ctx** | Why |
|---|---|---|---|---|---|---|---|---|
| gemma4:12b | dense, 48L, K=V, local:global 5:1 | 256K | ~7 GB | ~8 KB | ~0.5 GB | ~1 GB | **131072** | 128K fits with 15GB headroom; 256K native would push KV past the budget on 32GB |
| gemma4:26b (A4B MoE) | MoE, 30L, 6 global, K=V | 256K | ~19 GB | ~6 KB | ~0.4 GB | ~0.8 GB | **65536–131072** | 20GB total at 128K; 65536 is the safer default (leaves 12GB live) |
| qwen2.5-coder:7b | dense, 28L, 4 KV/hd, head_dim 128 | 128K (131072) | ~5 GB | **56 KB** | ~3.5 GB | ~7 GB | **65536** | 128K native but 56K/token makes 128K = 7GB; 65536 is the comfortable pick |
| qwen3.8:27b | hybrid: 16 full + 48 DeltaNet | 262144 (→1M YaRN) | ~17 GB | **32 KB** | ~2 GB | ~4 GB | **65536** | 23GB at 128K; 32768–65536 under heavy app load |
| granite4.1:8b | dense full-attn, 40L, 8 KV/hd, head_dim 128 | 512K | ~5 GB | **160 KB** | ~10 GB | ~20 GB | **32768–65536** | 64K KV alone = 10GB; above that it starves the 24GB pool |
| ornith:9b | hybrid (1.0-9B), 32L: 8 full + 24 DeltaNet | 262144 | ~7 GB | 32 KB | ~2 GB | ~4 GB | **131072** | Hybrid = cheap KV; 128K leaves 25GB; 262K also fits |
| lfm2.5:8b (A1B MoE) | 24L: 18 local conv + 6 GQA attention, 8 KV | 128K | ~5 GB | ~12 KB | ~0.3 GB | ~0.6 GB | **65536** | Cheap KV (conv is local); 128K also fits comfortably at 8GB total |

Rules of thumb from these numbers:
- **Hybrid models (DeltaNet / conv / local-attention) cut KV by 5-10x** vs dense at the same
  param size (Qwen3-27b's 32KB/token vs Qwen2.5-Coder-7B's 56KB/token vs Granite-8b's 160KB/token).
- Dense full-attention is the expensive case; always compute the KV term before recommending.
- MoE models: weights + activated experts dominate, KV is small — so you're weight-bound,
  not KV-bound. That is why gemma4:26b (19GB) barely fits where lfm2.5:8b (5GB) has 19GB headroom.

### Desktop: 64GB DDR5 + 7900 XTX 24GB VRAM, CUDA/ROCm/Vulkan offload (ziz)
**7900 XTX 24GB is the hard ceiling** (64GB RAM is irrelevant if the inference stack puts
everything on the GPU).

For **qwen3.8:27b** (per-token KV only 8 KiB fp16 because only 16 of 64 layers cache KV; the
48 DeltaNet layers are constant-state):

Context | KV (fp16) | KV (q8_0) | Total (fp16) | Fits 24GB?
--------|-----------|-----------|--------------|------------
8K       | 64 MiB    | 32 MiB    | ~17.2 GB     | yes, easily
32K      | 256 MiB   | 128 MiB   | ~17.4 GB     | yes, easily
128K     | 1 GB      | 0.5 GB    | ~18.1 GB     | yes
**256K**   | 2 GB      | 1 GB      | **~19.1 GB** | **yes — ~5GB headroom**
512K (YaRN)| 4 GB     | 2 GB      | ~21.1 GB     | yes, ~3GB headroom; close ComfyUI/browsers first
1M (YaRN)  | 8 GB      | 4 GB      | ~25.1 / 21.1 | over in fp16; fits only with q8_0 KV + idle GPU

**Bottom line:** 256K (262144) is the honest answer for agentic work; 512K for long-doc analysis
with everything else closed; 1M only in a dedicated single-shot mode with q8_0 KV (use llama.cpp
directly: `--cache-type-k q8_0 --cache-type-v q8_0` since Ollama can't do per-tensor KV quant the
way vLLM/llama-server can).

Caveat: VRAM is a single 24GB pool shared with gaming/ComfyUI. If a game or ComfyUI is active
*simultaneously*, drop to 32K–64K so the agent's KV stays under ~1GB and both apps coexist.

### Home server: 31GB RAM, old CPU (i7-3770K Ivy Bridge, no AVX2, DDR3), 8GB RX 5xx (Vulkan only)
**Decode speed is the binding constraint, not RAM.** 31GB easily holds weights + 32K-64K KV,
but the 2013 CPU crawls as KV grows. Set the ceiling by decode tolerance:

| Model | Agentic | PA / chat | Why |
|---|---|---|---|
| gemma4:12b (256K native) | **16384** | 8192 | 256K native = speed trap on a 2013 CPU; 16K is the honest interactive ceiling |
| gemma4:e4b (MoE) | 16384 | 8192 | MoE A4B = lighter per token than dense 12B; same decode profile |
| gemma4:e2b (MoE) | 16384 | 8192 | smallest = best latency; excellent for rapid PA loops |
| embeddinggemma | 2048 (fixed, don't override) | n/a | embedding models don't do chat; a bigger window just wastes memory |

`OLLAMA_CONTEXT_LENGTH=8192` is the sane floor for this box — bump to 16384 only for
agentic / tool-loop work, and expect 5-8 tok/s at 16K.

## How to compute it yourself

```
weight_gb     = param_B x bytes_per_weight / 1024     (Q4_K_M ≈ 0.575 B/param)
kv_bytes_tok  = layers x 2 (K+V) x kv_heads x head_dim x 2 (fp16)
kv_gb_at_ctx  = kv_bytes_tok x ctx / 2^30
fit = weight_gb + kv_gb_at_ctx <= target_budget_gb
```

Then sanity-check against **decode speed** on the target CPU. A 2013 i7 (no AVX2) is
roughly 3-8 tok/s at 16K context for a 7-12B model; the same model at 128K is 10-30x slower
per token (KV read bandwidth) and uninteractive. An X1-Carbon Lunar Lake is faster but has
only 32GB to share with the OS, so 128K on a 19GB model leaves little headroom. A 24GB GPU
can hold 256K on a hybrid 27B model and push it at 15+ tok/s — the same budget that would be
uninteractive on CPU-only.

## Output format

Always return:
1. A table: model / native ctx / arch / weight size / per-token KV / recommended num_ctx / why.
2. A one-line "global setting to try first" (e.g. `export OLLAMA_CONTEXT_LENGTH=65536`).
3. The ceiling per use-case (agentic / PA / long-doc), not just one number.
