---
name: parallel-agent-delegation
description: "Use when delegating work to multiple subagents."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagents, parallelism, file-ownership]
    related_skills: [verify-local-web-app, claude-code, codex]
---

# Parallel Agent Delegation

Use when fanning work out to several subagents in one `delegate_task` call,
especially when they create or edit files. Most cost overruns and corrupted
trees here come from two agents believing they own the same file.

## When to Use

Any multi-agent fan-out where the tasks touch the same repository, directory, or
project — file creation, refactors split by area, or build-then-test splits.

## Procedure

1. **Slice before dispatching, by path.** Give every task exclusive ownership
   of named files or directories. Two agents may not write the same file, and
   no file may be left unassigned. Prefer fewer, clearly larger slices over many
   overlapping ones.

2. **State absolute paths in every task brief.** Relative paths resolve against
   a different working directory inside some agents, which is how work lands in
   `~/fixture` instead of `~/Projects/app/fixture`. Include an explicit
   "create nothing outside this tree" line.

3. **Assign one owner per shared file and agree cross-file APIs before dispatch.**
   Config files, manifests and list registries get claimed by a single task by
   name; tell the others they must not edit them, only report required changes.
   For producer/consumer splits, put exact function signatures, field types,
   ownership/cloning rules, error propagation, and timestamp meanings in every
   affected brief. Assign caller adaptation to one owner; otherwise each agent
   can implement a locally sensible interface that does not compose.

4. **Forbid side effects you do not want, including verification side effects.**
   Say explicitly whether installs, builds, test runs, formatting, live app
   launches, input injection, and git commits are allowed. Unsupervised installs
   scatter `node_modules` into unrelated directories. Repository-wide formatters
   also violate file ownership: use read-only formatting checks across the tree,
   and restrict formatting writes to owned files using the project's language
   edition/settings. Reserve native window launches and desktop input for the
   integration owner so parallel workers cannot disrupt the same live test.

5. **Ask for a machine-checkable report:** exact absolute paths created, what
   was verified, and how it was verified (parsed, rendered, built, unit-tested).
   For source research, require exact source URLs/functions, the ordering or API
   contract established, and the uncertainty that still requires execution. If
   a long report must survive a handoff, assign an authorised project-local report
   path explicitly; a clipped live transcript is not a durable findings document.
   Self-reported success without a verification method is noise.

6. **Verify the merged result yourself** before committing or reporting: build,
   run the test suite, and inspect critical integration seams. Do not trust that
   N independent reports compose into a working tree. While writers are active,
   label cross-file build failures as integration snapshots, route findings to
   the relevant owner, and do not patch that owner's files concurrently. After
   all relevant handoffs land, rerun the complete gates against the integrated
   tree; earlier passing checks do not verify later edits.

7. **Sweep for strays.** Search outside the target tree for directories the
   agents may have created (home root, sibling project dirs, scratch). Reconcile
   anything found before the session ends.

## Always-on rules

- Deleted files are a symptom: when two agents prune "unused" paths, each
  removes what the other just wrote. Assign deletion rights explicitly.
- Do not block your own turn waiting on sibling agents; continue independent
  work and act when their results arrive.
- Match delayed completion notifications to their exact job and attempt before
  changing course; an older failed attempt does not invalidate a later verified
  retry. Inspect that attempt's stage/error and the newer acceptance evidence
  rather than automatically rerunning input, permissions or state-changing work.
  Handle already-accounted-for notifications internally; send another user-facing
  status only when the result changes the task, reveals a blocker or needs a decision.
  A delayed readiness event is not a fresh health check.
- If a child is no longer active but its result was not delivered, recover its
  completed report using the recorded handle before continuing dependent work.
  Do not keep describing finished research as running or substitute partial live
  log snippets for the missing findings; do not poll transcripts of running children.
- When a worker stops from quota, cancellation or another interruption, first
  recover its owned files and run the narrow build/test target before deciding
  to restart it; a failed delegation can leave useful compiling code. Reclaim
  ownership only after the writer has stopped, inspect unfinished documentation
  and wiring, and distinguish tests actually rerun from the child's partial claims.
  Do not ask the user to repeat an already-authorised task merely because the
  worker did not return its final report.
- Honor the newest stop request across the whole task tree: stop active writers,
  shut down task-owned test resources, and record unfinished ownership/state in the
  handoff. A later completion notification does not authorize resuming the stopped
  work. A separately requested checkpoint review may remain read-only; do not turn
  it into another implementation or auto-fix cycle.
- When results land after you have already finished and committed, check
  working-tree state and stray files, then decide what still needs doing — do
  not assume the tree is clean, and do not assume their work conflicts.
- Keep the number of agents writing to one artifact as low as possible; fan out
  across read-only analysis freely, across writes sparingly.

## Pitfalls

- **Shared-name collisions.** Two briefs describing "the CSS files" or "the
  config" route to different paths per agent; name exact absolute paths.
- **Convention drift.** Agents seeing a partially built tree adopt another's
  layout mid-flight, leaving two conventions in one project; lock the layout in
  the brief.
- **Trusting unrun verification.** Reports claiming a build or render passed
  without evidence usually mean it was judged structurally; reproduce it.
- **Cleanup collisions.** One agent deleting its own "now-dead" files can
  delete a sibling's deliverable — see always-on rule above.

## Supporting files

- `templates/delegation-brief.md` — copy-and-fill task brief enforcing path
  ownership, forbidden side effects, and a verifiable report format.
