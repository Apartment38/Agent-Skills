#!/usr/bin/env python3
"""Audit Hermes tool-schema context overhead and the schema-selector hook surface.

Reports, from live definitions rather than from documentation:
  * how many tools are eager vs deferred, and the estimated token cost of each
  * whether native Hermes Tool Search activates, and at which tier
  * whether the core exposes a ``select_tool_schemas`` hook (Tool Slimmer's path)
  * the state of the Tool Slimmer index

Run with the launcher-resolved Hermes interpreter (see SKILL.md, "How to Run"):

    hermes --print-runtime-command      # first JSON array element is the interpreter
    "<interpreter>" -I scripts/audit_tool_overhead.py

Read-only: it writes nothing.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# HERMES_REPO is resolved before the bootstrap import, so it cannot come from
# hermes_constants yet. Override it when the repo lives outside the default.
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
HERMES_REPO = Path(os.environ.get("HERMES_REPO", HERMES_HOME / "hermes-agent"))

os.environ.pop("PYTHONHOME", None)
os.environ.pop("PYTHONPATH", None)
os.environ.pop("VIRTUAL_ENV", None)
sys.path.insert(0, str(HERMES_REPO))
sys._hermes_pin_default_home = True  # type: ignore[attr-defined]

import hermes_bootstrap  # noqa: E402,F401

if not os.environ.get("HERMES_HOME"):
    import hermes_constants  # noqa: E402

    os.environ["HERMES_HOME"] = str(hermes_constants.get_default_hermes_root())


def names(defs: list[dict]) -> list[str]:
    out = []
    for entry in defs:
        fn = entry.get("function") if isinstance(entry.get("function"), dict) else entry
        if fn.get("name"):
            out.append(fn["name"])
    return out


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> int:
    from model_tools import get_tool_definitions
    from tools.tool_search import assemble_tool_defs, estimate_tokens_from_schemas, load_config

    # skip_tool_search_assembly=True gives the real, uncollapsed catalog -- the only
    # honest baseline for measuring what deferral saves. Omitting it undercounts by
    # roughly half, because you receive the already-deferred payload.
    raw = get_tool_definitions(quiet_mode=True, skip_tool_search_assembly=True)

    section("Eager baseline (pre-assembly)")
    raw_bytes = len(json.dumps(raw))
    raw_tokens = estimate_tokens_from_schemas(raw)
    print(f"tool defs:          {len(raw)}")
    print(f"serialized bytes:   {raw_bytes:,}")
    print(f"est. tokens:        {raw_tokens:,}   (bytes / 4 heuristic)")

    section("Native Tool Search")
    cfg = load_config()
    print(f"enabled:            {cfg.enabled}   ('auto' is an alias of 'on' today)")
    print(f"listing:            {cfg.listing}")
    print(f"threshold_pct:      {cfg.threshold_pct}")
    print(f"listing_max_tokens: {cfg.listing_max_tokens}")
    print("activation rule:    activates whenever deferrable_tokens > 0 "
          "(or connections are granted); context_length is not consulted")

    res = assemble_tool_defs(raw)
    print(f"activated:          {res.activated}")
    print(f"tier:               {res.tier}   (0 passthrough, 1 listing, 2 bare bridge)")
    print(f"listing_form:       {res.listing_form}")
    print(f"deferred_count:     {res.deferred_count}")
    print(f"deferred_tokens:    {res.deferred_tokens:,}")

    section("Assembled payload (what the model actually sees)")
    asm_bytes = len(json.dumps(res.tool_defs))
    asm_tokens = estimate_tokens_from_schemas(res.tool_defs)
    print(f"tool defs:          {len(res.tool_defs)}")
    print(f"serialized bytes:   {asm_bytes:,}")
    print(f"est. tokens:        {asm_tokens:,}")
    if raw_tokens:
        print(f"saved per turn:     {raw_tokens - asm_tokens:,} est. tokens "
              f"({100 * (raw_tokens - asm_tokens) / raw_tokens:.1f}%)")
    print(f"visible names:      {sorted(names(res.tool_defs))}")

    section("Schema-selector hook surface (Tool Slimmer's path)")
    from hermes_cli.plugins import VALID_HOOKS

    print(f"VALID_HOOKS count:  {len(VALID_HOOKS)}")
    has_hook = "select_tool_schemas" in VALID_HOOKS
    print(f"select_tool_schemas present: {has_hook}")
    if not has_hook:
        print("=> Tool Slimmer's selector cannot register; it runs diagnostics only.")
        print("=> Its policy is skip_tool_slimmer_when_active, so if native Tool Search")
        print("   is active above, patching core to add the hook would change nothing.")

    section("Tool Slimmer index")
    index_path = Path(os.environ["HERMES_HOME"]) / "tool-slimmer" / "tool_index.json"
    print(f"path:               {index_path}")
    if index_path.exists():
        payload = json.loads(index_path.read_text())
        print("exists:             True")
        print(f"total_tools:        {payload.get('total_tools')}")
        print(f"checksum:           {str(payload.get('checksum'))[:12]}")
    else:
        print("exists:             False  (build it with scripts/rebuild_index.py)")

    section("Caveat on `hermes tool-slimmer status`")
    print("Its native_hermes_tool_search.active field inspects whatever schema set it")
    print("is handed. Fed pre-assembly defs (the index holds those), it reports False")
    print("even while Tool Search is genuinely active in live sessions. Trust the")
    print("'activated' line above, not that field.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
