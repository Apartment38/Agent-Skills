---
name: external-memory-providers
description: "Use when configuring external memory providers in Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, memory, plugins, providers, installation, verification]
---

# External Memory Providers

Install, configure, and verify third-party memory providers for Hermes Agent. Treat “installed” and “active in Hermes” as separate acceptance criteria.

## Principles

1. **Start from current authoritative documentation.** Load the `hermes-agent` skill and fetch both the provider’s installation page and its complete Hermes-integration page. Follow the documented recommended path; use a documented fallback only when a real compatibility constraint requires it.
2. **Keep dependencies outside Hermes’ managed venv.** Hermes updates may rebuild that venv. Prefer pipx or a dedicated persistent venv.
3. **Match Python ABIs at the bridge boundary.** A pipx environment may use a newer Python than Hermes. Adding its `site-packages` to Hermes’ `sys.path` is unsafe when native wheels are involved. Use a dedicated venv created with Hermes’ Python when a wrapper executes imports in-process.
4. **Use Hermes CLI for config.** Never hand-edit `config.yaml`; apply settings with `hermes config set`.
5. **Do not disable the shared memory toolset.** When replacing legacy file memory, disable only the built-in file/profile flags documented for the provider. A blanket `hermes tools disable memory` can also hide provider tools.
6. **Account for prompt caching.** Provider/tool changes apply to newly initialized sessions. Do not mutate an existing conversation’s system prompt or tool schema; restart the gateway and state clearly that an already-running TUI session must be replaced.

## Installation Workflow

### 1. Audit before changing state

Record:

- `hermes --version` and Hermes’ Python version/path
- provider package versions and installation environments
- provider installer/status output
- `hermes plugins list --plain --no-bundled`
- `hermes config get memory.provider`
- `hermes memory status`
- gateway status

Do not infer `[all]` or equivalent extras from the base package version. Import or inspect every capability dependency named by the provider’s docs.

### 2. Choose an isolation topology

- Use pipx when the provider communicates out-of-process or Hermes discovers a safe package entry point.
- Use a dedicated venv built from Hermes’ Python when Hermes imports provider code in-process and the package includes native extensions.
- Never treat `importlib.util.find_spec()` as compatibility proof. It locates modules without loading native code. Perform real imports under the interpreter that will execute the provider.

### 3. Install provider and bridge

Install the complete requested feature profile and its Hermes wrapper. If the wrapper ships an installer/status command, use it to create the persistent plugin bridge under `$HERMES_HOME/plugins/` and verify its import.

Enable user plugins explicitly when Hermes lists them as opt-in:

```bash
hermes plugins enable <manifest-name>
```

Provider selection and general-plugin enablement can be separate mechanisms. Verify both.

### 4. Configure without duplication

Set the external provider and, if instructed by provider docs, disable legacy file memory while retaining the memory toolset:

```bash
hermes config set memory.provider <provider>
hermes config set memory.memory_enabled false
hermes config set memory.user_profile_enabled false
```

Use the provider’s current documented keys rather than assuming these are universal.

### 5. Restart and verify

Restart the gateway only after install, enablement, and configuration are complete. Then verify:

- Gateway is active.
- Plugin bridge/status says installed and importable.
- General plugin list says enabled when hooks/tools depend on it.
- `hermes memory status` says the selected provider is installed, available, and active.
- Provider diagnostics have no actual error/failure records. Do not misread counters, measurements, skipped checks, or unset optional overrides as failures.

### 6. Exercise the Hermes agent path

A standalone SDK smoke test is necessary but insufficient. Load the provider through Hermes’ own memory-provider loader or start a fresh Hermes agent, then verify:

1. provider construction and initialization;
2. provider system-prompt block is active;
3. provider tool schemas are exposed;
4. write a uniquely tagged test memory;
5. recall that exact tag;
6. delete the test memory;
7. confirm the provider DB/path is the intended Hermes store.

Use assertions and fail the verification command if any step fails. Report exact observed versions/statuses, not plausible expectations.

## Common Pitfalls

- **Separate pipx venvs are not “alongside” for in-process imports.** The core and wrapper may each work alone while Hermes cannot safely import both.
- **Plugin discovered does not mean plugin enabled.** Provider discovery may succeed while hook/tool registration remains opt-in.
- **CLI command absent does not prove provider failure.** Hermes can load the provider while an installer omitted the sibling `cli.py` used for argparse discovery. Diagnose provider and CLI paths independently, then repair only with a tested bridge.
- **Gateway restart does not retrofit the current conversation.** New gateway and CLI sessions use the provider; an old TUI process retains its frozen prompt/tool surface.
- **A successful install command is not completion.** Require read-back configuration, active-provider status, and a real write/recall/cleanup cycle.

## Provider References

- Mnemosyne + Hermes integration, Python ABI handling, CLI bridge, and deterministic smoke test: `references/mnemosyne-hermes.md`
