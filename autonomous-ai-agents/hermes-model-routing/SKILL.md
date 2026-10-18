---
name: hermes-model-routing
description: "Use when routing Hermes models. Configure routes."
version: 1.0.0
---

# Hermes Model Routing

Configure Hermes model, fallback, and auxiliary routes from live account availability and measured local performance. Optimize the configured route, not a generic leaderboard.

## Procedure

1. Discover the active state before recommending or changing it.
   - Load the `hermes-agent` skill, then inspect `~/.hermes/config.yaml`, `hermes auth list`, `hermes fallback list`, and `hermes config check`.
   - Inspect the authenticated model-picker catalog or cache for exact free model IDs, record its refresh time, and treat `:free` availability as volatile.
   - Query every intended local endpoint's live tags and use the exact tag that was benchmarked.

2. Establish the route policy.
   - Default to a currently available free cloud model only for non-sensitive work when that is the user's stated policy.
   - Always provide an explicit local route for proprietary repositories, secrets, customer data, and private images; a cloud default cannot infer data sensitivity.
   - Put independently hosted local endpoints in ordered `fallback_providers`; use `provider: custom` plus the endpoint's `/v1` base URL for each entry.

3. Gate and assign models.
   - Benchmark at the context window that the eventual Hermes route will use, nearly fill it, and save prompt and decode rates separately.
   - Exclude any candidate gated out for timeout or decode throughput from comparative ranking and all automatic routes. Mention it only as likely unsuitable for that host/context, not as a judgment of base-model capability.
   - Route compression, curator, and review to capable local models because they can receive accumulated conversation or repository context.
   - Assign inexpensive local models to approval, title generation, and profile description only after confirming their short-task performance is sufficient.
   - Use cloud vision only for non-private images, with an explicit local vision fallback when available.

4. Produce a reviewable configuration fragment.
   - Give the default, ordered fallbacks, and every auxiliary task as concrete YAML with exact provider/model/base URL values.
   - State whether the fragment was recommended or applied. Do not edit the active profile without an explicit request.
   - Validate generated YAML; after an applied edit, run `hermes config check` and read back `hermes fallback list`.

## Pitfalls

- Configure an explicit auxiliary `fallback_chain` when a primary provider is selected; Hermes does not silently spend through unrelated authenticated providers behind an explicit route.
- Use `fallback_providers` rather than the legacy singular fallback key; the list preserves intended ordering and is what the Hermes fallback manager writes.
- Keep free-cloud defaults and private-data routes distinct; account availability does not create permission to send proprietary inputs externally.
- Do not place models excluded by the benchmark gate in automatic fallbacks or auxiliary routes; a fallback that violates the operating threshold merely moves the outage downstream.
- Preserve the exact model tag in config; similarly named Ollama tags can differ in baked context, prompt template, or placement.
