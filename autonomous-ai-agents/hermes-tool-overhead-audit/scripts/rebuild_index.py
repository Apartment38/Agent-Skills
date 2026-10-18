#!/usr/bin/env python3
"""Rebuild the Tool Slimmer index from Hermes' live tool definitions.

Run after changing toolsets, installing plugins, or adding MCP servers. Writes
$HERMES_HOME/tool-slimmer/tool_index.json, which has no expiry and is what the
Tool Slimmer CLI reads.

    hermes --print-runtime-command      # first JSON array element is the interpreter
    "<interpreter>" -I scripts/rebuild_index.py

Idempotent: running it twice over an unchanged catalog yields the same checksum.

Do NOT write live_tool_schemas.json by hand -- that snapshot expires after 3600s
and requires a real session_id, so a fabricated one is a misleading artifact.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
HERMES_REPO = Path(os.environ.get("HERMES_REPO", HERMES_HOME / "hermes-agent"))
SLIMMER_SRC = Path(
    os.environ.get("TOOL_SLIMMER_SRC", HERMES_HOME / "plugins" / "tool-slimmer" / "src")
)

os.environ.pop("PYTHONHOME", None)
os.environ.pop("PYTHONPATH", None)
os.environ.pop("VIRTUAL_ENV", None)
sys.path.insert(0, str(HERMES_REPO))
sys.path.insert(0, str(SLIMMER_SRC))
sys._hermes_pin_default_home = True  # type: ignore[attr-defined]

import hermes_bootstrap  # noqa: E402,F401

if not os.environ.get("HERMES_HOME"):
    import hermes_constants  # noqa: E402

    os.environ["HERMES_HOME"] = str(hermes_constants.get_default_hermes_root())

from model_tools import get_tool_definitions  # noqa: E402
from hermes_tool_slimmer.index_store import IndexStore  # noqa: E402


def live_schemas() -> list[dict]:
    """Normalized {name, description, parameters} catalog for every enabled tool."""
    raw = get_tool_definitions(quiet_mode=True, skip_tool_search_assembly=True)
    out = []
    for entry in raw:
        fn = entry.get("function") if isinstance(entry.get("function"), dict) else entry
        name = fn.get("name")
        if not name:
            continue
        out.append(
            {
                "name": name,
                "description": fn.get("description") or "",
                "parameters": fn.get("parameters") or {},
            }
        )
    return out


def main() -> int:
    schemas = live_schemas()
    if not schemas:
        print("ERROR: no tool schemas returned; refusing to overwrite the index", file=sys.stderr)
        return 1
    store = IndexStore()
    payload = store.rebuild(schemas)
    print(f"indexed {payload['total_tools']} tools -> {store.path}")
    print(f"checksum {payload['checksum'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
