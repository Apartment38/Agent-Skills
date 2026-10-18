---
name: verify-local-web-app
description: "Use when verifying a local web app end-to-end."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [verification, qa, browser, localhost, e2e]
    related_skills: [systematic-debugging, dogfood, spike]
---

# Verify Local Web Apps End-to-End

## When to Use

Use whenever you have built or changed a locally runnable web app and are about
to tell the user it works — especially apps that embed another document in an
iframe, apps whose correctness means writing files on disk, and any session
where you keep background servers running for your own testing.

Rendering correctly is not persisting correctly: the deliverable is evidence
that the real UI drove the real backend and that the result survived outside
the browser.

## Procedure

1. **Start deliberately, confirm readiness by request, not by sleep.**
   Launch with `background=true`, then poll health:
   `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<port>/`.
   A fixed sleep before the first check hides both slow boots and crashes.

2. **Wait for hot reloads to settle before driving the UI.**
   Editing app source makes dev servers restart or full-reload; navigating
   during that window leaves automation attached to a reloading document.
   Watch for the reload line in the server log, then navigate.

3. **Add user-visible error surfacing before verifying.**
   Wrap risky handlers (selection, render, commit) in try/catch that writes the
   message into the app's own status area and `console.error`s it. Console
   access can be lost mid-session, while the app's status text stays readable
   through a DOM query or screenshot.

4. **Drive the real UI, then re-read what the app rendered.**
   Dispatch a genuine event sequence, then read back status text, breadcrumbs,
   target lines and computed styles. In multi-document apps (parent UI plus
   iframe preview), dispatch from the top-level document and read with
   `browser_console(expression=...)` — see `references/verification-recipes.md`.

5. **Assert persistence on three independent axes.**
   API reflects it (`curl` the REST endpoint), disk contains it (read the real
   file with `read_file`, or locate the written value with `search_files`),
   and forbidden side effects are absent (e.g. no leftover `style` attribute
   when the app promises source-only writes).

6. **Stop every background server you started and prove the port is free.**
   List listeners with `ss -ltnp`, find your port's line, and match that pid
   with `ps -o pid,etime,cmd -p <pid>`.

## Always-on rules

- Verify the **user's actual project/path**, not the demo fixture that lives in
  your own repo. Reproduce their exact command, including tricky arguments.
- Use HTTP checks plus on-disk reads for anything about persistence; reserve
  browser automation for what only a browser can show (layout, overlay
  geometry, computed styles, gestures).
- When a third-party UI library "works", quantify it: measure its rendered
  geometry against your own measurement before claiming integration, otherwise
  report it as evaluated-and-rejected with the measured number.
- Re-run the whole test suite after fixing; verification without regression
  evidence is half-finished.
- For background-only studies, deliver separate self-contained HTML files with
  descriptive filenames, a canvas-only visible body, and no comparison controls,
  logos, captions or navigation. Verify real rendered motion, paused-pointer pixel
  differences (zero for autonomous variants), mobile fill and reduced-motion
  stability. For stylistic variants sharing a flow, compare seeded simulation
  signatures as well as inspecting their different rendered pixels.
- Run demo-builder tests in isolated source copies so tests cannot overwrite saved
  previews. A partial rebuild must retain the complete version manifest rather
  than replacing it with only the selected variants.
- For website design workshops, verify openable, navigable previews rather than
  accepting screenshots as the deliverable. Check every direction against the
  same route/content matrix, including gallery links and page-preserving design
  switching; a working gallery alone does not prove its destinations exist.
- Preserve every delivered design revision as a separately named, navigable
  version, including small requested changes. Copy its design-owned sources
  before editing, update identifiers and visible version labels together, and
  verify the new index link in both portable and built output. Compare prior
  preview checksums before/after; an unchanged screenshot does not prove the old
  artifact was preserved. Recreate missing historical treatments honestly rather
  than claiming an exact rollback without an archived artifact.
- For this user's Apartment38 Publications mockups, verify a large centred
  masthead, wide cover images alternating sides with narrower title/byline text,
  and the same draggable Home directory component in place of top navigation.
  Assert every row's geometry, stack image before text on narrow screens, and
  test navigation away and back so removed headers do not remain hidden/focusable
  or fail to restore on routes that retain them. See the editorial layout recipe.
- For reference-driven animated artwork, verify silhouette, apparent pixel size,
  and the selected base's grid/motion language against the reference before
  accepting functional tests. This user's explorable mockups require both visual
  fidelity and working interactions; a generic replacement effect is not enough.
- Test cursor tracking, autonomous pulse, touch response, and reduced-motion
  stability independently. Require visibly displaced pupils or highlights inside
  the artwork, not merely changing diagnostic attributes; isolate gaze from idle
  motion with reduced-motion captures. Keep movement-triggered glow local to the
  tracked features when requested, and prove its transient events expire after
  input stops. Verify the requested motion language: a burning effect requires
  upward flicker/embers rather than recoloured radial ripples.
- For cursor-reactive smoke or sand, apply a localized deformation to both the
  density field and grains, rather than drawing a cursor spotlight. Freeze ambient
  motion for opposing-input pixel comparisons, verify touch response separately,
  and check that the gust fades while the underlying drift continues. Sample the
  canvas itself to verify the intended black background and restricted hue range.
  For dust shedding, assert that particles escape the dense plume, cumulative
  emissions grow while the live pool stays bounded, and expired particles are
  recycled. Allow equal near-black RGB channels caused by alpha quantisation when
  checking hue; channel-order equality alone is not evidence of a warm colour.
- For gaze-driven deformation, isolate opposing inputs under reduced motion and
  compare rendered lid bounds plus nearby texture pixels. A moving pupil alone
  does not verify deformation of the whole eye and surrounding surface. Use a
  shared inverse deformation field for lids and texture so they remain attached.
  See the canvas interaction recipe.
- Verify full-background artwork and unrestricted window movement against the
  actual viewport/page, not the old hero or corner container. Check scroll,
  resize, touch dragging, keyboard movement, and recoverable title bars; a window
  moving within its original box does not satisfy page-wide dragging.
- Verify requested removals in the rendered DOM, not just screenshots or CSS.
  Hidden hero copy or links can remain focusable or exposed to assistive technology.
- For combined-template revisions, inspect and reuse the original template's
  actual component and motion rules, rather than guessing from the latest mockup.
  Verify shared inner-page chrome across filtered indexes, every article, projects,
  About and 404. Confirm logos, mastheads and directory navigation do not collide;
  preserve original card-grid geometry and test install/copy controls. For an
  engraved corner seal, compare source SVG, check rotation in rendered frames,
  clip overflow without covering text, and verify reduced-motion frames stay still.
- For a supplied GLSL logo effect, verify the actual source is unchanged, compile
  it in the matching WebGL version, and test rendered alpha, orientation, frame
  differences, layer order and route cleanup. A static fallback is not proof the
  shader ran. Explicitly enable SwiftShader for headless verification when needed;
  await the active/failed diagnostic state rather than assuming a fixed load delay.
- For named-font requests, distinguish a loaded font from fixed-word artwork.
  Verify actual font loading with `document.fonts.ready`, `document.fonts.check()`
  and rendered headings; a CSS family name alone proves nothing. Record license
  provenance and embedding flags, never clear restrictions, and reassess font
  distribution when converting a private prototype into a deployable theme.
  Where permitted, preserve fixed headings as SVG outlines paired with semantic
  heading text instead of bundling a restricted font binary. Do not claim the
  font loaded when artwork rendered, or treat outlining as proof of publication
  rights. See the outlined-heading recipe.
- When converting an approved demo into a generator theme, preserve its archived
  versions but verify the actual site with real content, native page URLs and
  server-rendered reading/navigation markup. Do not ship sample records or wrap
  the prototype SPA and call it a theme. Test the theme independently of the
  workshop, including JavaScript-disabled navigation, asset URLs and a fresh
  output build; a successful demo does not prove generator integration. See the
  static-site theme conversion gates.
- For Eleventy 3 themes, register layout aliases during plugin execution, using
  paths relative to `eleventyConfig.directories.layouts || directories.includes`.
  The `eleventy.directories` event is too late: the alias map has already been
  merged. Verify nested input/custom layout directories without replacing the
  site's includes directory.
- Capture pre-layout post bodies with `addPreprocessor(name, '*', function(data,
  content) { ... })` and `this.inputPath`; do not read a collection item's lazy
  content getter before rendering. That triggers a render-order failure. Declare
  helper imports as real package dependencies rather than trusting hoisting.
- Treat URL safety, path-prefix expansion, and HTML-attribute escaping as separate
  operations. In Liquid links/images use `value | url | escape`: a scheme-safe
  permalink can still contain quotes and markup. Exercise a quoted SVG-event
  permalink in an actual generator build, not only in the URL helper's unit tests.
- Test a theme's actual download after fresh extraction and dependency install,
  with no workshop files or prior output present. Apply the `url` filter to the
  path before building canonical URLs, as well as to links and assets, and verify
  path-prefix deployment in the copied installation.
- Compare unmodified shader output to the approved source at identical dimensions
  and uniforms before diagnosing a port regression. Raw RGBA8 readbacks can retain
  tiny RGB values where low alpha rounds to zero; require correct compositing and
  source fidelity rather than changing supplied GLSL to satisfy an over-strict
  zero-RGB assertion.
- Test portable previews both directly and in the repository's built output;
  template processing and rewritten output paths can break otherwise valid HTML.
  See the portable-preview checks in `references/verification-recipes.md`.

## Pitfalls

- **Touch release can fire document `pointerleave`.** Do not cancel a touch-created
  gust immediately on that event; distinguish `pointerType` and let its normal
  decay run. Test after touchEnd, not just during the press.
- **Re-bind listeners to documents that can navigate.** Handlers attached once
  at startup stay bound to a dead document after an embedded frame reloads;
  bind from the load handler and again on every mode/context switch.
- **Belt-and-braces default paths.** A helper defaulting to a repo-local demo
  path silently overrides caller intent; default to the current directory, never
  to a specific example project.
- **Assume foreign tools resolve paths against their own arguments.** Builders
  resolving relative directories against `process.cwd()` must run with the
  working directory set to the target, restored afterwards.
- **Treat a busy port as fatal.** Fall forward to a free port and print which
  one; otherwise the new process dies while an older instance keeps answering.
- **Empty-state silence.** When a resource list is empty (no stylesheets, no
  files), say so in the app's status rather than rendering an empty control.
- **Revert verification artifacts** with targeted patch edits before finishing;
  `git checkout` can also revert unrelated work made concurrently in the tree.

## Supporting files

- `references/verification-recipes.md` — synthetic gesture recipes, persistence
  assertions, third-party UI library capability probes, port/process checks.
