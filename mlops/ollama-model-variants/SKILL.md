---
name: ollama-model-variants
description: "Use when creating hardware-fit Ollama model variants."
version: 0.1.0
author: Erick McGhee, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ollama, local-models, coding, agents, benchmarking]
    related_skills: [ollama, hermes-agent]
---

# Hardware-fit Ollama model variants

Create, register and validate local model variants for Hermes and coding agents. Follow the ordered workflow below; produce real artifacts and measured results, not merely recommendations. This is a reusable procedure, not a snapshot of any particular machine's models or benchmarks.

## When to use

- The user wants local Ollama coding/agent models selected, right-sized, registered and tested.
- The user wants deployable Modelfiles, model cards and reproducible evidence for this machine.
- Do not run the workflow merely because the user asks to edit this skill.

## Prerequisites and authority

Load `ollama` and its `references/variant-registration-validation.md` for runtime and inheritance checks. Load `hermes-agent` before inspecting Hermes configuration or recommending its supported auxiliary-role configuration. Use current official documentation, not remembered model names or machine profiles.

Use `terminal` for runtime inspection and bounded inference, `web_search`/`web_extract` for primary sources, and file tools for artifacts. On Linux inspect system/user services, listeners and mount dependencies as needed. Do not assume a default port, model directory, GPU backend or physical machine identity.

Proceed autonomously with inspection, research, local file creation, variant registration and bounded testing. Obtain explicit approval before any new/replacement weight download. Explain necessary disruptive service changes before proceeding; ask only for genuinely required permission or missing information. Never request passwords in chat.

## Procedure

### 1. Locate the server and inventory installed models

- Locate the actual local Ollama server and query `/api/tags`.
- Distinguish a successful empty inventory from connection errors or an unavailable server. Diagnose unavailability before proceeding; inspect service logs, listeners, permissions and mount ordering rather than treating it as no models.
- If models exist, use them and continue to step 3. If none exist, follow step 2.
- Save the original response and endpoint. Completion: a successful inventory query, or an honestly reported blocker.

### 2. Recommend and install only approved suitable models

- Inspect CPU, physical core count, instruction support, RAM, GPUs, usable VRAM, GPU backend and free disk space. Reuse information already collected in this run.
- Research current candidates using publisher model cards, official generation configurations and Ollama documentation.
- Recommend a small complementary selection for coding and agentic tool use that fits the hardware. Consider quality, native structured tools, quantization, context-memory cost, speed and CPU offload. Include embeddings if useful for retrieval.
- Give exact Ollama tags, approximate download/storage requirements, hardware-fit rationale and tradeoffs. Clearly separate estimates from measurements.
- Ask for explicit approval of the selection, a subset or alternatives. Wait; silence is not approval. Do not download before approval.
- Install only approved tags, verify completion and inventory entries, and save approved selection plus exact downloaded tags.
- If the user declines all downloads and no bases exist, stop: variants require installed bases. If returning here from step 4 with only unsuitable bases, explain that no suitable coding/agent base was approved and stop that branch without silently using unsuitable models.
- Normal empty-inventory path: continue to step 3. When redirected here from step 4, refresh metadata for new models and return to step 4, reusing hardware findings.

### 3. Inspect hardware and runtime

- Reuse collected hardware facts; fill any gaps from the live system, not memory.
- Record Ollama version, endpoint, service settings, model store, installed models, quantization, total parameter counts, native context limits and capabilities.
- Query `/api/show` for each distinct model. Preserve templates, parameters, model/projector metadata and digests.
- Deduplicate aliases referencing identical models; inspect weight/projector identities as well as manifest digests. Retain all alias names in the inventory.
- Completion: an auditable inventory and hardware/runtime snapshot.

### 4. Check suitability first, then research each installed model

- Check that the installed models are appropriate for coding and agentic tool use and fit this hardware. Assess expected quality, native tool formatting, backend compatibility, memory fit and practical latency; a capability flag or ability to load is insufficient. Label provisional judgments until tested.
- If none of the models are a good fit, notify the user and follow step 2. Reuse hardware information already collected. Once appropriate models are installed, continue with step 4. This does not waive download approval.
- Treat embedding-only models as complementary retrieval models, not substitutes for a suitable generative coding/agent model. If some bases fit and others do not, document each model's role and limitations; do not present unsuitable variants as recommended agent choices.
- Research each distinct installed model using publisher cards, official generation configurations and Ollama documentation. Find model-specific sampling recommendations for coding, reasoning and agentic use.
- Record source URLs and distinguish publisher recommendations from hardware tuning choices. Do not impose a generic temperature across unrelated models. Identical values are valid only when sources justify them.
- Completion: per-model suitability findings and sourced generation settings.

### 5. Plan context variants

- Under 20B total parameters: one variant at the maximum context supported by the installed model and runtime.
- At or above 20B total parameters: two variants, one at a measured practical context with reasonable generation speed and minimal CPU offload on this PC, and another at half that practical context. Step 6 determines the final values before creation.
- Classify MoE by total, not active, parameters; effective-size marketing names are not total parameter counts.
- Do not claim extended context requiring unconfigured YaRN/RoPE scaling or another backend. Explain differences between advertised and locally supported limits.
- Embedding-only models receive their supported maximum context without generation parameters.
- If the required maximum cannot safely run locally, document the blocker; do not silently label a reduced size as maximum or exceed available resources.

### 6. Measure before choosing larger-model contexts

- Run sequential, bounded probes at candidate context sizes before fixing the >=20B variants. Set explicit output caps and timeouts allowing cold loads; avoid unbounded parallel stress tests.
- Record request payloads, prompt/output token counts, load/evaluation durations, wall time, GPU residency, CPU offload and host load. Inspect runner context allocation as well as saved configuration.
- Calculate decode tokens/sec as `eval_count / (eval_duration / 1e9)`. Record prompt throughput separately. Do not conflate load time, prefill and decode.
- Adjust context and supported per-model runtime settings based on results. Retain automatic GPU placement unless measurements justify overriding it.
- Explain the chosen speed/offload compromise; if no candidate is usable, return to the suitability/approval path rather than inventing a successful fit.
- Distinguish short-prompt performance at a large allocated context from filled-context performance. No throughput guarantees from brief probes.
- Record co-residency: sequential requests can leave multiple models loaded. Do not evict unrelated active workloads without justification or permission.

### 7. Name each variant by actual context

- Include family and size where needed, role, and actual context: for example `family-12b-agent:32k` or `family-embed:2k`. These are patterns, not installation recommendations.
- Define 1K=1024 tokens and record exact counts. If not divisible by 1024, use an exact token-count name rather than rounding.
- Never use ambiguous `max` or `medium` names. Preserve original tags and reject conflicting existing targets instead of silently overwriting unrelated variants.

### 8. Write deployable Modelfiles and model cards

- Inherit from installed base tags, preserving templates, tool formatting, stops, capabilities and multimodal components. Do not reconstruct from a lone GGUF if that drops projectors or renderer/parser behavior.
- Apply model-specific publisher sampling settings; explain unsupported controls or differences from the publisher's reference backend.
- Tune CPU threads, batching and supported options for the hardware. Distinguish conservative choices from measured optimizations; avoid forced GPU placement without evidence.
- Avoid unnecessary SYSTEM or TEMPLATE replacements that interfere with Hermes/coding clients.
- Explain request-level reasoning controls and client settings that cannot be encoded in a Modelfile. Do not invent runtime options.
- Each card records base tag/digest, total parameters, quantization, exact context, sampling/runtime choices, sources, hardware rationale, test coverage and limitations.

### 9. Register without downloading weights

- Preflight local base presence and digest, then create variants reusing installed weights. Preserve originals.
- Apart from explicitly approved step-2 installations, never pull additional or replacement weights. The reproducible installation script must fail on missing/mismatched bases rather than automatically downloading.
- Avoid global service changes. Explain a necessary disruptive change and obtain required permission before applying it.
- Read back exact registered targets before claiming success.

### 10. Validate every variant and distinct model

- Verify every saved context and parameter, inherited templates, capabilities, stops, system fields, metadata and multimodal components. Check built-in renderer/parser fields when applicable.
- Verify unchanged original digests and reused non-parameter layers by media type, digest and size. A changed provenance `from` annotation is not a changed weight layer.
- Check actual runner allocation where observable; saved `num_ctx` or `/api/ps` alone may not prove effective context.
- Run a basic structured tool-call smoke test per distinct generative base, inspecting tool name and arguments. Test both native and OpenAI-compatible paths when clients will use both. Never execute generated calls.
- Test embeddings for count, expected dimension, finite values and nonzero vectors; use truncation rejection where supported.
- Investigate failures within scope, retain evidence and report unresolved limits. A tools flag alone is not proof. Do not imply thinking, vision/audio, long-context quality or complex agent reliability was tested unless it was.
- Completion: explicit coverage and pass/fail results for every required target, not a plausible subset.

### 11. Save the bundle and recommend client roles

Save under `~/ollama-model-cards/` without destroying unrelated prior runs:
- Per-variant Modelfiles and readable cards.
- Manifest with exact names, bases/digests, parameters, contexts, aliases and artifact paths.
- Reproducible installation script with local-base/digest checks and no implicit pulls.
- Original/final inventories, hardware/runtime snapshot, benchmark requests/results and validation evidence.
- Approved selection and exact downloaded tags, if any; otherwise an explicit no-download record.
- README listing exact variant names, contexts, source links and instructions for remote Hermes/coding clients using the server's actual reachable endpoint, including `/v1` where appropriate.
- Explain client overrides, reasoning controls, output-token headroom, concurrency/co-residency assumptions and aliases covered by a single card. A bind address is not a client destination; local LAN checks do not establish reachability from another machine. Warn that a dummy API key does not authenticate Ollama.

At the end, recommend which local variants to use for the various Hermes auxiliary model roles. Load `hermes-agent` and consult https://hermes-agent.nousresearch.com/docs plus the installed version's documented configuration to enumerate real supported roles; do not invent role keys. Map each supported relevant role to an exact local model, or explicitly say none is suitable. Consider summarization/compression, vision, other supported auxiliary tasks, and retrieval embeddings where actually supported. Distinguish a model recommendation from a validated/configured integration. State untested modalities and client context/output limits. Do not modify Hermes defaults merely because a recommendation was requested.

Finish with a concise summary of existing/newly installed bases, created variants, validation results, material limitations, bundle path, endpoint and auxiliary-role recommendations.

## Pitfalls

- An unavailable server is not an empty inventory; mount-order failures do not justify replacing weights.
- Enough RAM to load does not imply useful coding/agent latency. Reassess suitability when probes contradict estimates.
- Maximum context under the <20B rule is not a promise that filling it is practical.
- All layers offloaded does not mean all tensors or buffers reside on GPU; record CPU-mapped components and KV allocations.
- Do not bake machine-specific model names, endpoints or historical speeds into future recommendations.
- Approval of variants is not approval of downloads, global reconfiguration or changing Hermes model defaults.

## Verification before reporting completion

Programmatically reconcile inventory, deduplicated bases, planned variants and actual results. Every named variant must have artifacts, read-back verification and documented test coverage. Check source links and installation-script safety. Run syntax checks on generated scripts and exercise registration/validation paths against the real server. Report blocked or untested criteria explicitly. Never substitute fabricated outputs for failed tools.
