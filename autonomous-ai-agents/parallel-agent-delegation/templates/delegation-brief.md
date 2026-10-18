# Delegation brief template

Fill this in per task; send the rendered text as the subagent's `goal` (or as
`context`).

```text
TARGET
  Absolute root : /abs/path/to/target/
  You own ONLY  : <explicit file paths or directories>
  Create/modify : NOTHING outside the absolute root above. 
                  Other agents own sibling paths; writing them corrupts their work.

FORBIDDEN
  - No writes outside the root above (no ~/ copies, no scratch project dirs).
  - No package installs unless explicitly allowed below.  Allowed: no
  - No git commits / branch operations.  (unless allowed: no)
  - No deleting files owned by other agents. If something looks unused,
    report it instead of removing it.

SHARED FILES (single owner per line)
  - /abs/path/eleventy.config.js -> owned by another task; DO NOT EDIT,
    report required changes instead.

DELIVERABLE
  <what must exist, precisely>

VERIFY (pick what is possible and say how)
  - parse / typecheck: <command>
  - render or build: <command>
  - assertions run: <what was actually executed>
  Do not claim "verified" for anything you did not execute.

REPORT
  1. Exact absolute paths created or modified.
  2. Verification actually run, with the command and its outcome.
  3. Anything you could NOT verify (be explicit).
  4. Suspected collisions with another agent's files.
```
