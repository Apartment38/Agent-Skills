# Hermes Model and Auxiliary Routing

Load this reference when turning a comparison into a Hermes configuration.

## Verified configuration surfaces

- Main route: `model.provider`, `model.default`, and, for a custom endpoint, `model.base_url`.
- Cross-provider resilience: top-level `fallback_providers`, an ordered list whose entries require `provider` and `model`.
- Auxiliary routes: `auxiliary.<task>` for `vision`, `compression`, `skills_hub`, `mcp`, `approval`, `title_generation`, `review`, and `triage_specifier`.
- The current CLI helpers are `hermes model`, `hermes fallback`, `hermes config get`, `hermes config set`, and `hermes config check`.

## Primary and fallback rules

- Use `hermes model --refresh` before naming a cloud default. A cached `:free` model is account/time specific.
- Use `hermes fallback` to edit the chain interactively. It writes top-level `fallback_providers`.
- A local OpenAI-compatible fallback uses `provider: custom`, `model`, and its exact `base_url`.
- Fallback activates for exhausted retryable rate limits, server/connection failures, auth failures, not-found responses, or repeated malformed/empty responses. It is turn-scoped: each new user message attempts the primary again.
- A fallback resets prompt caching. Do not mistake switching providers during a long session for free reliability; it can make the next turn reread prior context.

## Auxiliary route rules

- Auxiliary tasks resolve independently. Setting `provider: auto` tries the main route, task fallback chain, then the main fallback chain.
- An explicitly selected auxiliary provider is preferred. On capacity failure it tries that task's `fallback_chain`, then the main model as a safety net.
- `base_url` on an auxiliary task bypasses provider resolution. Use it when the task must stay on a particular local endpoint.
- Do not send compression, curator, review, or private-code tasks to a free cloud route by accident. Prefer a direct local `base_url` for these tasks.
- Keep approval and title generation on a small local model only after measuring that host at its realistic context. They are low-stakes but frequent.

## Generic configuration shape

Use verified values only; this is a field map, not a copy-ready recommendation.

```yaml
model:
  provider: PROVIDER
  default: MODEL

fallback_providers:
  - provider: custom
    model: LOCAL_MODEL
    base_url: LOCAL_OPENAI_COMPATIBLE_URL

auxiliary:
  vision:
    provider: PROVIDER
    model: VISION_MODEL
    fallback_chain:
      - provider: custom
        model: LOCAL_VISION_MODEL
        base_url: LOCAL_OPENAI_COMPATIBLE_URL
  compression:
    provider: custom
    model: LOCAL_COMPRESSION_MODEL
    base_url: LOCAL_OPENAI_COMPATIBLE_URL
```

## Validation sequence

1. Use `terminal` to run `hermes config check` before editing.
2. Use `terminal` to apply model settings through `hermes config set` or configure fallbacks through `hermes fallback`.
3. Use `terminal` to run `hermes fallback list` and `hermes config get model`.
4. Read the active config with `read_file` only to verify the exact target after the write.
5. Start a fresh session for a real request-path test; a valid YAML file alone does not prove the model is reachable.
