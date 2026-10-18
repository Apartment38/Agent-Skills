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

3. **Assign one owner per shared file.** Config files, manifests and list
   registries get claimed by a single task by name; tell the others they must
   not edit it, only report what it should contain.

4. **Forbid side effects you do not want.** Say explicitly whether installs,
   builds, test runs and git commits are allowed. Unsupervised installs scatter
   `node_modules` into unrelated directories.

5. **Ask for a machine-checkable report:** exact absolute paths created, what
   was verified, and how it was verified (parsed, rendered, built, unit-tested).
   Self-reported success without a verification method is noise.

6. **Verify the merged result yourself** before committing or reporting: build,
   run the test suite, and read critical files back. Do not trust that N
   independent reports compose into a working tree.

7. **Sweep for strays.** Search outside the target tree for directories the
   agents may have created (home root, sibling project dirs, scratch). Reconcile
   anything found before the session ends.

## Always-on rules

- Deleted files are a symptom: when two agents prune "unused" paths, each
  removes what the other just wrote. Assign deletion rights explicitly.
- Do not block your own turn waiting on sibling agents; continue independent
  work and act when their results arrive.
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
