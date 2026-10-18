---
name: llm-model-evaluation
description: Compare LLMs and configure Hermes model routes.
version: 1.1.0
author: Hermes
metadata:
  hermes:
    tags: [LLMs, Benchmarking, Ollama, Hermes, Routing]
---

# LLM Evaluation and Hermes Routing

Evaluate cloud and local models on the hardware and account that will actually serve them, then turn the evidence into Hermes default, fallback, and auxiliary routes. This skill does not claim that a marketing model list or an advertised context window is usable; it requires live inventory, measured context behavior, and explicit privacy choices. It uses Hermes tools, official model sources, and an OpenAI-compatible local endpoint; no new SDK is required.

## When to Use

- "Compare my local models with free cloud models."
- "Which model should be Hermes's default or fallback?"
- "Benchmark every Ollama model at a usable context."
- "Configure Hermes auxiliary vision, compression, approval, or review models."
- "My local model list changed; re-evaluate the choices."

## Prerequisites

- Load `hermes-agent` and its `references/providers-and-models.md` plus `references/configuration.md` before editing Hermes settings.
- Confirm cloud credentials with `terminal` using `hermes auth list`; use `hermes model --refresh` to refresh the authenticated catalog.
- Confirm each local OpenAI/Ollama-compatible endpoint and preserve its exact base URL and model IDs.
- Define the hardware-specific target context and exclusion policy before testing. Use a fixed completion length, one model at a time per host, a wall-time ceiling, and a minimum decode rate.
- Treat free cloud availability as time-bound. Record its refresh timestamp and do not send private code, secrets, customer records, or private media to it without an explicit user decision.

## How to Run

Use `terminal` to query live Hermes authentication and model selection, `web_extract`/`web_search` for official model evidence, `read_file` for saved benchmark JSON, and `write_file` for the dated report. Use `hermes fallback` for interactive fallback edits or `hermes config set` for safe configuration updates; do not hand-edit a live config file.

## Quick Reference

- `terminal`: `hermes auth list`
- `terminal`: `hermes model --refresh`
- `terminal`: `hermes fallback list`
- `terminal`: `hermes config check`
- `web_extract`: official model cards and benchmark documentation
- `read_file`: benchmark JSON and current config
- `references/hermes-routing.md`: Hermes config and auxiliary routing rules

## Procedure

1. Inventory live routes before researching names.
   - Use `terminal` to run `hermes auth list`, `hermes model --refresh`, and `hermes fallback list`.
   - Query every local endpoint's live model list. Preserve exact tags, serving host, reported native context, quantization, and model metadata.
   - Read the active config with `read_file`; record `model`, `fallback_providers`, and `auxiliary` separately.
   - Completion: every candidate has a provider, exact model ID, host, and availability timestamp.

2. Normalize model identity and context tiers.
   - Group aliases by underlying weights but keep tags distinct when context, template, speculative decoding, or hardware placement differs.
   - Set a realistic context per host. Do not equate a tag's advertised maximum with a viable agent setting.
   - Completion: each benchmark row names requested context, returned prompt-token count, and filled fraction.

3. Benchmark the serving configuration, not a toy prompt.
   - Build a near-full prompt with a fixed token reserve and a fixed small completion. Run one request at a time per host.
   - Save load time, prompt-evaluation tokens and duration, completion tokens and duration, wall time, requested context, filled fraction, and status.
   - Compute prompt-ingestion and decode tokens/sec separately through `terminal` or `execute_code`; never derive either mentally.
   - Mark a run `completed`, `insufficient_speed`, `time_limit_exceeded`, or `request_failed`.
   - Completion: raw machine-readable results contain every candidate and status, including failures.

4. Filter operationally unfit configurations without erasing evidence.
   - Exclude any configuration below the agreed decode floor or above the time ceiling from ranked assessment and routing recommendations.
   - Keep a short exclusions list stating that it is likely a poor fit for the tested hardware/context, not proof the base model is bad.
   - Completion: eligible and excluded records are separated programmatically and their totals reconcile to the raw inventory.

5. Research capability with comparable sources.
   - Use `web_extract` on official model cards, release notes, and benchmark documentation. Use `web_search` only to locate them.
   - Capture benchmark name, harness, pass@k, tool/runtime conditions, context, and whether results are vendor-reported. Compare scores only within the same benchmark and harness.
   - For agentic coding, prioritize Terminal-Bench, SWE-Bench, DeepSWE, or tool-use evidence. For vision, verify vision support and the serving parser/projector as well as benchmark claims.
   - Completion: each capability claim has an official URL and a stated evidence caveat.

6. Select routes by workload and privacy boundary.
   - Choose a free cloud default only when the authenticated catalog currently exposes it at zero price and its capability evidence fits the task.
   - Use the strongest measured local model as the first cross-provider failure fallback. Prefer an independent host for the final fallback.
   - Route compression, review, curator, and private repository work to local models unless the user explicitly accepts cloud processing. Use a lightweight local model for approval and title tasks only after it clears the needed latency threshold.
   - Completion: the recommendation states default, ordered fallbacks, context for each local route, auxiliary assignments, and the private-data route.

7. Validate Hermes configuration before applying it.
   - Load `references/hermes-routing.md`, then construct the smallest explicit configuration change using exact provider/model/base URL values verified above.
   - Use `terminal` with `hermes config set` or `hermes fallback`; run `hermes config check` and `hermes fallback list` after changes.
   - Read back the exact configuration target before claiming it changed. If the user asked only for recommendations, write a validated proposal instead of changing the active profile.
   - Completion: config validation passes and the resolved model/fallback state matches the recommendation.

8. Deliver a reproducible report.
   - Put the route table first: workload, primary, fallback, intended context, privacy boundary, and evidence status.
   - Include eligible measured results, a compact excluded list, source URLs, raw-results location, and configuration proposal location.
   - Completion: all declared counts reconcile and every recommendation is traceable to a live inventory, measurement, or cited capability source.

## Pitfalls

- A public model page does not prove that the active account can select the model. Use the authenticated picker/cache as availability evidence.
- A requested context is not a filled context. Verify returned prompt-token counts and preserve the filled fraction.
- Prompt ingestion and decode solve different problems; report both. Long-context work is often prefill-bound, interactive work decode-bound.
- Do not route to a `:free` model as if its availability were permanent. Date the observation and retain explicit local fallbacks.
- Do not recommend a full-context tag merely because it loads. A qualified smaller tag may be the only operationally sound route.
- Hermes fallback is failure recovery, not a content classifier. The agent cannot infer whether a prompt is proprietary; provide and state an explicit local route.
- Auxiliary routes have independent provider resolution. An explicit cloud auxiliary can still fall back through its task-specific chain; configure it deliberately rather than assuming the main fallback applies.

## Verification

Invoke through `terminal`: `hermes config check && hermes fallback list`. Then use `read_file` to confirm that benchmark counts, eligible/excluded totals, and the proposed or active route table agree.
