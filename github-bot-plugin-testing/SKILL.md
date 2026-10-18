---
name: github-bot-plugin-testing
description: Use when testing the Hermes GitHub bot Git wrapper.
---

# Isolated Git wrapper tests

Run wrapper tests with a clean child PATH so an already active Hermes Git middleware launcher cannot become the test wrapper's underlying Git executable. Preserve the absolute Python interpreter before changing the child PATH, retaining its installed dependencies:

    PYTHON=$(command -v python)
    env PATH=/usr/local/bin:/usr/bin:/bin HERMES_SOURCE=/path/to/hermes-agent "$PYTHON" -m unittest discover -s tests -v

Use an actual compatible Hermes checkout for HERMES_SOURCE to exercise plugin validation and profile-aware setup; omit it only when unavailable and report skipped integration tests. Keep all configuration writes and repositories disposable. Mock public API responses for setup tests, including malformed JSON, invalid IDs, HTTP failures, missing curl, and timeouts. Verify actual commit author and committer metadata with real Git, not only constructed argv.

## Verification of a plugin rename

After renaming a plugin, grep the whole tree for the old name and confirm every reference was updated before declaring the job done:
- Manifest (`plugin.yaml`): `name`.
- CLI registration (`ctx.register_cli_command`): command name.
- Code: launcher directory, middleware `source` identity, error/status strings.
- Documentation: install, enable, configure, status commands, and config-wizard text.
- Tests: temp-dir prefixes, hardcoded wrapper paths, `shell_command` expectations. Then run the suite and review `git diff --stat` for any missed references.

## Before claiming a regression

This suite's `tests/test_plugin.py` GitTests carry pre-existing failures that reproduce on the unmodified code: the wrapper hangs on `git --list-cmds=builtins` when a previously installed wrapper sits on PATH. Before attributing any test failure to a change, confirm it reproduces on the original (`git stash` then rerun, compare failure sites and counts). A failure present before and after your change is not a regression introduced by your work; a failure that appears only after the change is the one worth pursuing.
