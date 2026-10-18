---
name: hermes-tool-overhead-audit
description: Audit Hermes tool-schema context overhead and deferral.
version: 0.1.0
author: Erick, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, tools, context-window, tokens, tool-search, tool-slimmer, diagnostics]
    related_skills: [hermes-agent]
---

# Hermes Tool-Overhead Audit

Measure what the tool catalog actually costs in the context window, and establish
whether Tool Search or Tool Slimmer is really selecting tools — from live
definitions and source, never from documentation or from a plugin's own status
line. Read-only apart from an optional index rebuild.

## When to Use

- "Do tools affect the context window?" / "Why is my agent dumber / forgetting things?"
- Tool schemas look expensive and you want real numbers, not the bytes/4 folklore
- A Tool Slimmer index is missing, or its status output looks contradictory
- Deciding whether to patch Hermes core to wire a schema-selector hook
- After adding MCP servers or plugins, to re-measure the deferred payload
- Don't use for: prompt-caching or compression tuning (that is `hermes-agent`),
  or for measuring conversation-history growth

## Prerequisites

- Hermes installed; repo at `$HERMES_HOME/hermes-agent` unless `HERMES_REPO` says otherwise
- Nothing else — both scripts are stdlib + Hermes imports, no network

## How to Run

Python must be the **launcher-resolved interpreter**, never a bare `python3`:

1. `terminal(command='hermes --print-runtime-command')` — a JSON array whose first
   element is the interpreter path.
2. `terminal(command='"<interpreter>" -I <script>')`

The `-I` flag isolates the process, which is why both scripts re-insert the repo
path and `import hermes_bootstrap` themselves.

## Quick Reference

| Need | Command |
|---|---|
| Full overhead + hook + index audit | `"<interpreter>" -I scripts/audit_tool_overhead.py` |
| Rebuild the Tool Slimmer index | `"<interpreter>" -I scripts/rebuild_index.py` |
| Plugin's own view | `terminal(command='hermes tool-slimmer status')` |
| Core hook surface | see Procedure step 3 |

## Procedure

1. **Measure the eager baseline.** Call `model_tools.get_tool_definitions(quiet_mode=True,
   skip_tool_search_assembly=True)` and estimate tokens with
   `tools.tool_search.estimate_tokens_from_schemas`. Completion criterion: you have a
   tool count, byte size, and token estimate for the *uncollapsed* catalog.

   The `skip_tool_search_assembly=True` flag is not optional. Without it you receive the
   already-deferred payload and will undercount by roughly half.

2. **Measure the assembled payload.** Pass the same defs to
   `tools.tool_search.assemble_tool_defs(raw)`. Report `activated`, `tier`,
   `listing_form`, `deferred_count`, `deferred_tokens`, and the token delta.
   Completion criterion: you can state tokens saved per turn and as a percentage.

3. **Check the selector hook surface.**
   ```python
   from hermes_cli.plugins import VALID_HOOKS
   print("select_tool_schemas" in VALID_HOOKS, len(VALID_HOOKS))
   ```
   Completion criterion: a boolean. If absent, any plugin needing that hook is
   diagnostics-only, and its startup log will say so.

4. **Check the index.** `IndexStore().path` under `$HERMES_HOME/tool-slimmer/`.
   Completion criterion: `total_tools` matches step 1's count, or you rebuild it.

5. **Only then advise.** If native Tool Search reports `activated: True`,
   recommend leaving it alone — see Pitfalls.

## Pitfalls

- **`hermes tool-slimmer status` reports `native_hermes_tool_search.active: false`
  while Tool Search is genuinely active.** That field only checks whether the bridge
  tool names appear in whatever schema set it was handed, and the index stores
  *pre-assembly* defs with no bridge in them. Trust `assemble_tool_defs().activated`.
  This single line has cost more time than every other item here.
- **Patching core to add `select_tool_schemas` buys nothing while native Tool Search
  is active.** Tool Slimmer's own policy is `skip_tool_slimmer_when_active`; its
  selector returns `None` with `skip_reason: native_hermes_tool_search_active`. Verify
  activation *before* proposing a source patch, and never patch for a no-op.
- **`enabled: auto` is not a budget-gated mode.** `should_activate()` returns True
  whenever `deferrable_tokens > 0` (or connections are granted); `context_length` is
  accepted but not consulted. Do not "tune" a threshold that has no effect.
- **Do not fabricate `live_tool_schemas.json`.** It expires after 3600s and requires a
  real `session_id`. A hand-written one is a misleading artifact. `tool_index.json`
  has no expiry and is what the CLI reads — rebuild that instead.
- **Skills are cheap; tools are not.** Skills use progressive disclosure (~3k-token
  index); tool schemas ship in full on every request. When diagnosing context pressure,
  count tools first.
- **`toolset` is absent from API tool defs** (`{"type": "function", "function": {...}}`).
  Index documents will show `toolset: None`; that is expected, not a build failure.
- The shell snippets in Quick Reference use `<interpreter>` placeholders deliberately —
  resolve the path at run time rather than hardcoding a per-machine toolchain path.

## Verification

- `scripts/audit_tool_overhead.py` prints every section and exits 0.
- Baseline and assembled counts differ when Tool Search is active (e.g. 57 eager →
  22 visible); if they are identical, Tool Search is not activating and you should
  say so rather than reporting a saving.
- `scripts/rebuild_index.py` run twice yields the same `checksum` — proof of
  idempotence and that the catalog is stable between runs.
- The reported `total_tools` in the index equals the eager tool-def count.
