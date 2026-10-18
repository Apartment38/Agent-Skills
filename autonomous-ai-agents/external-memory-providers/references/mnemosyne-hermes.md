# Mnemosyne with Hermes Agent

Version-scoped field notes validated with `mnemosyne-memory 3.15.1`, `mnemosyne-hermes 0.5.0`, and Hermes `v0.21.0 (2026.8.31)`. Re-check current upstream docs before reuse.

## Authoritative pages

- Installation: `https://docs.mnemosyne.site/getting-started/installation`
- Hermes plugin: `https://docs.mnemosyne.site/api/hermes-plugin`

The installation guide recommends pipx for `mnemosyne-memory[all]`. The plugin page says not to install into Hermes’ managed venv and documents a standalone-venv fallback plus `mnemosyne-hermes install --force`.

## Safe topology when pipx and Hermes Python differ

Mnemosyne includes native dependencies (`onnxruntime`, `sqlite-vec`, `ctransformers`, `llama-cpp-python`). If pipx chooses a different Python minor than Hermes, do not point an in-process wrapper at that pipx `site-packages` tree.

Create a persistent venv using Hermes’ Python and install both distributions there:

```bash
HERMES_PY="$HERMES_HOME/hermes-agent/venv/bin/python"
TARGET="$HERMES_HOME/mnemosyne-venv"
uv venv --python "$HERMES_PY" --clear "$TARGET"
uv pip install --python "$TARGET/bin/python" --upgrade \
  'mnemosyne-memory[all]' mnemosyne-hermes
"$TARGET/bin/python" -c \
  "import mnemosyne, mnemosyne_hermes, fastembed, sqlite_vec, ctransformers, llama_cpp, mcp"
```

Install the persistent wrapper bridge:

```bash
"$TARGET/bin/mnemosyne-hermes" install \
  --mode wrapper --python "$TARGET/bin/python" --force
```

Then configure and enable:

```bash
hermes config set memory.provider mnemosyne
hermes config set memory.memory_enabled false
hermes config set memory.user_profile_enabled false
hermes plugins list --plain --no-bundled
# Use the exact manifest name shown; for v0.5.0 packaging it may be hermes-mnemosyne.
hermes plugins enable hermes-mnemosyne
hermes gateway restart
```

Do not grant tool-override permission unless the current manifest/docs explicitly require replacement of a built-in tool. Mnemosyne’s namespaced tools do not inherently require it.

## Wrapper CLI omission workaround

In the validated versions, wrapper mode created `$HERMES_HOME/plugins/mnemosyne/__init__.py` and `plugin.yaml` but omitted `cli.py`. The provider worked, yet `hermes mnemosyne ...` was absent because Hermes’ argparse discovery requires `<provider-dir>/cli.py`.

A direct symlink to the package’s `cli.py` was insufficient: Hermes imports that file through a synthetic package before executing wrapper `__init__.py`, so the standalone venv was not yet on `sys.path`. A working sibling shim is:

```python
"""CLI bridge for the persistent Mnemosyne Hermes wrapper."""
from __future__ import annotations
import sys as _sys
_SITE = "/absolute/path/to/mnemosyne-venv/lib/python3.11/site-packages"
if _SITE not in _sys.path:
    _sys.path.insert(0, _SITE)
from mnemosyne_hermes.cli import *  # noqa: F401,F403,E402
```

Write it to `$HERMES_HOME/plugins/mnemosyne/cli.py`, substituting the actual site-packages path. Verify:

```bash
hermes mnemosyne version
hermes mnemosyne stats
hermes mnemosyne doctor --no-fix
```

Treat this as a version-scoped compatibility repair. Re-check whether a newer installer now emits `cli.py` before applying it.

## Deterministic Hermes-loader smoke test

Run from the Hermes source directory with Hermes’ Python. The test must use `plugins.memory.load_memory_provider`, initialize against `$HERMES_HOME`, write a UUID-tagged global memory, recall the exact tag, and delete it afterward. Also assert:

- `provider.name == "mnemosyne"`
- `provider.is_available()`
- provider beam initialized without `_init_error`
- `# Mnemosyne Memory` appears in `system_prompt_block()`
- `get_tool_schemas()` is non-empty
- DB path resolves under `$HERMES_HOME/mnemosyne/data/`

Use `handle_tool_call("mnemosyne_remember", ...)`, `handle_tool_call("mnemosyne_recall", ...)`, and `handle_tool_call("mnemosyne_forget", ...)`; parse JSON and assert statuses. Cleanup is part of the test.

## Reading diagnostics correctly

`hermes mnemosyne doctor --no-fix` may display a low-looking `Checks passed: X/Y` count because only literal statuses such as `OK`/`YES` count as passes; rows containing numeric measurements and unset optional environment overrides still contribute to `Y`. Inspect the JSONL diagnostic log for actual failure/error statuses before concluding the system is unhealthy.

Healthy evidence includes:

- Python/package/dependency imports OK
- embeddings model identified
- sqlite-vec available
- SQLite quick-check OK
- foreign keys enabled
- working-vector coverage complete with zero missing/orphan vectors
- gateway logs contain no Mnemosyne initialization errors

Zero episodic vectors is expected before consolidation; working-memory vector coverage proves embeddings are active.
