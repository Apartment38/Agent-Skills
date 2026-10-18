# Verification recipes

Copy these shapes and adapt selectors/ports. Each produced real evidence.

## Drive a gesture without losing the automation context

In multi-document apps (parent UI plus embedded iframe), drive events from the
top-level document and read back with `browser_console(expression=...)`;
compute the target position from the embedded document's rect rather than
clicking a ref inside it, which can shift the automation's execution context.

```js
(async () => {
  const d = document;                        // top-level document
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const frame = d.querySelector('#frame');
  const fd = frame.contentDocument;
  const el = fd.querySelector('.target');
  fd.defaultView.scrollTo(0, el.getBoundingClientRect().top + fd.defaultView.scrollY - 150);
  await wait(700);
  const r = el.getBoundingClientRect();
  const f = frame.getBoundingClientRect();
  const x = f.left + r.left + r.width / 2;
  const y = f.top + r.top + 20;
  const overlay = d.querySelector('#overlay');
  overlay.dispatchEvent(new PointerEvent('pointermove', { clientX: x, clientY: y, bubbles: true }));
  overlay.dispatchEvent(new MouseEvent('click', { clientX: x, clientY: y, bubbles: true }));
  await wait(600);
  return JSON.stringify({
    crumbs: [...d.querySelectorAll('#inspector .crumb')].map((e) => e.textContent),
    status: d.querySelector('#status').textContent,
  });
})()
```

## Drag / resize with a full event sequence

Assert *during* the gesture, before `pointerup`, so you can distinguish a live
preview from the committed result:

```js
const handle = d.querySelector('.handle[data-dir="se"]');
const r = handle.getBoundingClientRect();
handle.dispatchEvent(new PointerEvent('pointerdown', {
  clientX: r.left, clientY: r.top, bubbles: true, button: 0, pointerId: 1, isPrimary: true }));
for (let i = 1; i <= 8; i++) {
  window.dispatchEvent(new PointerEvent('pointermove', {
    clientX: r.left + i * 10, clientY: r.top + i * 4, bubbles: true, pointerId: 1 }));
  await new Promise((res) => setTimeout(res, 25));
}
// mid-gesture: transient preview exists, readout is live
window.dispatchEvent(new PointerEvent('pointerup', {
  clientX: r.left + 80, clientY: r.top + 32, bubbles: true, pointerId: 1 }));
await new Promise((res) => setTimeout(res, 2500));   // commit round trip
```

## Prove persistence

1. UI says saved and shows the committed value.
2. `curl -s "http://127.0.0.1:<port>/api/resource" | head -c 400`.
3. Read the file on disk with `read_file(path, offset=..., limit=...)`, or
   locate the written value with `search_files(pattern="<value>", path="<dir>")`
   — never rely on the DOM alone for proof of a write.

Then assert the *absence* of what the design forbids, e.g.
`el.getAttribute('style') === null` after a source-only write. For CSS editors,
also confirm the write landed in the right at-rule context by printing the
`@media` block around the changed line.

## Capability-probe a third-party UI library

When a requirement names a specific library but it must run in an arrangement
it does not officially support (cross-document targets, shadow DOM, transformed
containers):

1. Integrate it behind the same hooks as the existing implementation so the
   downstream write path is identical whichever engine runs.
2. At attach time compare the library's rendered control-box rect with the rect
   you measured yourself; beyond a small tolerance, log the measured offset,
   tear it down, and fall back to your own engine.
3. Report the measured numbers and which engine shipped. Synthetic events
   reaching a library's private handlers is not proof it works — measure
   geometry and committed output.

## Portable preview and design-gallery checks

1. Enumerate the expected designs and routes, then assert that every linked
   generated file exists. Use the same route matrix for every direction rather
   than extrapolating from one working homepage.
2. Open a generated preview directly when file portability is promised; then
   run the repository build and repeat navigation from its actual output path.
   Check loaded assets and console errors in both contexts, because template
   engines may interpret inline script delimiters and rewrite asset locations.
3. Exercise route hashes (for example `#/publications`) separately from article
   anchors (`#setup`). Confirm anchors scroll within the article without mounting
   a different page, and that switching designs preserves the route rather than
   carrying over an unrelated heading hash.
4. Check mobile overflow against the configured viewport width, not just
   `innerWidth`: an overflowing layout can enlarge the layout viewport itself.
   For a 390px test, assert that
   `Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) <= 391`.
5. For canvas heroes, compare frames at separate times under normal motion and
   under emulated reduced motion. CSS animation overrides do not stop JavaScript
   draw loops; check that reduced motion produces a stable, nonblank composition.
6. Revisit animated routes and leave them again; verify teardown of timers,
   animation frames and listeners so navigation does not multiply background work.
7. Inspect gallery screenshots for alignment and legibility, but use DOM/computed
   values to validate suspected contrast or overflow defects rather than treating
   a visual critique's numerical guesses as measurements.
8. For a versioned revision, record old preview hashes before editing with
   `sha256sum <preserved-preview-paths>`, then create a new source/preview target.
   Check the new design identifier, visible labels, manifest entry and return link
   agree. After the build, run `sha256sum -c <checksum-file>` from the directory
   against which its relative paths were recorded. Follow the version-index link
   in built output and inspect its resulting URL and design identifier; merely
   listing the new version does not prove it opens the intended artifact.

## Alternating editorial lists and desktop navigation

1. Inspect the reference and source content separately. Identify masthead scale,
   image-to-text width ratio, row alternation, gutter and vertical rhythm before
   applying styling. Check author metadata before rendering bylines. In mockups,
   label provisional attribution as draft; in production, omit an absent author
   or identify the publisher explicitly rather than inventing authorship.
2. Render each publication once as an image link and adjacent text containing its
   byline, title link, summary and metadata. A practical desktop grid is
   `minmax(0, 2.1fr) minmax(0, 1fr)` with reversed columns on even rows. Count
   unique article destinations separately from links because both image and title
   link to the same entry. Retain filters and sample-content labels.
3. Inspect the covers after setting wide frames. For inline SVG covers, use
   `preserveAspectRatio="xMidYMid slice"` when edge-to-edge cropping is intended;
   changing the CSS aspect ratio alone can leave internal letterboxing. Inspect
   the resulting crop so important artwork is not lost.
4. Reuse the actual Home directory component and drag handlers when the requested
   navigation is the same desktop window, not a separately styled lookalike.
   Reserve space above the masthead for its initial placement. Reconcile drag
   bounds and document coordinates with the new page container; Home's minimum
   title-bar offset may not be appropriate on an editorial page.
5. On desktop, read every row's image and text `getBoundingClientRect()` values.
   Assert `(image.left < text.left) === (index % 2 === 0)`, and verify that image
   width dominates the text column. Assert masthead computed text alignment is
   centre and the expected number of rows/bylines is present. Capture a scrolled
   screenshot with multiple rows; the top viewport alone cannot show alternation.
6. At narrow widths, reset both explicit grid columns **and grid rows** for even
   entries, then assert `text.top > image.top` for every row. Check configured
   viewport overflow independently at typical mobile and smallest supported sizes;
   a responsive first row does not prove the reversed rows stack correctly.
7. Verify obsolete top navigation is absent from the rendered DOM, then drive
   directory links, title/image article links and the article's return link.
   Verify route-specific headers are removed/restored correctly after transitions
   and that the active directory item is updated. Native press/move/release and
   focused-title arrow keys must move the reused window, not just its diagnostics.

## Canvas tracking, pixel geometry, and pulsating glow

1. Compare a screenshot with the supplied reference before interaction testing.
   Inspect silhouette, opposite eye slopes, and apparent cell size. When the user
   requires the same shape, trace the boundary into normalized coordinates rather
   than substituting a generic ellipse or diagonal slash. Compare flat edges,
   curved lower boundaries, taper, spacing, and dominant colour separately.
   Confirm cells remain square after responsive resizing; a fixed low-resolution
   canvas stretched to a different aspect ratio can produce rectangles despite
   pixelated rendering.
2. Drive actual browser input at opposite edges. With CDP, call
   `Input.dispatchMouseEvent` using `type: 'mouseMoved'`, `x`, and `y`; for touch,
   use `Input.dispatchTouchEvent` with `touchStart` and `touchEnd`. Read clamped
   gaze values and capture the rendered canvas after each input.
3. Expose small diagnostics such as `data-pupil-x`, `data-pupil-y`,
   `data-pixel-size`, and `data-glow` when helpful. Assert opposite gaze values,
   but also inspect screenshots: changing metadata does not prove drawing changed.
4. Hold the pointer still and sample two frames at different pulse phases. Verify
   a slow glow change independent of gaze. For pixel-art references, inspect stepped
   palette/density changes rather than accepting a smooth blur as equivalent.
   Verify the base's square-dot lattice, dark cell gaps and Bayer/quantized density
   as well as pixel size: coarsening the canvas alone can retain a solid-block
   treatment that no longer matches the requested halftone style.
5. Emulate `prefers-reduced-motion: reduce` before loading. Compare timed captures
   to prove autonomous loops are static; then test direct pointer response separately
   if retained. A CSS override cannot freeze a JavaScript canvas loop.
6. Exercise desktop-window dragging with real press/move/release input when pointer
   capture is used. Drag from the initial corner to the opposite page edge, then
   repeat after scrolling and resizing. Read bounding rectangles and document
   coordinates before/after; account for scroll offsets when dragging absolute
   elements. Test touch and focused-title arrow keys, keep titles reachable, and
   confirm no horizontal overflow at narrow widths. Do not accept bounds inherited
   from a former small desktop container as full-page dragging. Synthetic events
   alone may not establish pointer capture.
7. Run syntax checks before browser tests after canvas edits. For Gaussian ripples,
   use `Math.exp(-Math.pow(distance / width, 2))` or parenthesize the exponent:
   JavaScript rejects a unary minus directly before exponentiation.
8. Repeat key checks on the repository's built preview and revisit other routes.
   Artwork changes must not break navigation, filters, installation tabs, or copy
   payloads, and route teardown must prevent duplicate animation loops.
9. For a full-background revision, assert the canvas rectangle covers the viewport
   on desktop and mobile and remains fixed during scrolling when that is the
   intended composition. Check that new scale texture reads as plates/seams rather
   than a plain grid. Search rendered text and selectors to prove removed copy and
   links are absent, rather than merely hidden.
10. For motion-triggered glow, capture stationary baseline, newly emitted local
    effects, their evolution, and a frame after their lifetime. Assert transient
    events expire and tracking intensity returns to baseline; test stationary
    pulse independently. Match the effect's motion language, not merely a changed
    colour: burning should show irregular upward flicker and drifting embers,
    not expanding circular wavefronts. Heat/event diagnostics corroborate genuine
    rendered changes but do not replace active/settled screenshots. Under reduced
    motion, test opposing input separately and compare idle pixel buffers to prove
    decorative motion freezes while any retained direct gaze response still works.

## Static-site theme conversion gates

1. Inspect the generator configuration, installed version, active layouts, real
   Markdown/front matter and asset-copy rules before changing the approved demo.
   Establish which addresses must remain stable and which data is merely sample.
2. Write a failing integration assertion against the site's real build before
   wiring new layouts. Assert recognizable source-post text and native article
   links, not just a theme identifier or the existence of an output directory.
3. Separate site-owned metadata/content from reusable layouts and browser assets.
   Render publication lists, article bodies, navigation and empty states on the
   server. Keep JavaScript for effects, dragging and copying; installation controls
   must display/copy commands, never execute them. Escape metadata and reject unsafe
   href/image schemes separately from rendering trusted Markdown content.
4. Run `npm run build` and the repository's test command against fresh generated
   output. Verify expected pages/assets and the absence of workshop, test and theme
   source pages. Preserve original demo artifacts independently; do not delete
   source archives while cleaning a generated-output directory.
5. Serve the generated site over HTTP and exercise Home, indexes, categories,
   articles, Projects, About and 404 with normal navigation, reload and back/forward.
   Test JS-disabled reading/navigation, missing metadata and genuinely empty
   categories. Test a non-root path prefix so root-relative paths do not conceal
   asset/link failures; production URLs need not support direct `file://` opening.
6. Exercise reuse in an isolated minimal generator project. Prove layout resolution
   and asset copying with the installed generator instead of guessing whether
   aliases accept absolute paths. Do not mark reuse or browser integration passed
   until that fixture and the assembled site's real interaction tests have run.

## Fixed-word SVG headings without a bundled font

Use this only when outlined artwork is appropriate and permitted; it avoids font
binary distribution, not the need to check publication rights.

1. Confirm the font actually selected by the renderer, for example
   `fc-match 'Requested Font'` on Linux. An export that silently selects a fallback
   is not evidence of the requested typography.
2. Create an SVG containing the approved heading text, explicit font family/size
   and explicit foreground colour. Convert it with:
   `inkscape source.svg --export-text-to-path --export-plain-svg --export-filename=heading.svg`.
   Verify the output has glyph paths and no live `<text>` elements or font binary.
3. Query the exported heading's bounds with
   `inkscape heading.svg --query-id=heading --query-x --query-y --query-width --query-height`.
   Set its viewBox using those measured bounds and the intended font-sized line
   box. Preserve the line-box scale across words rather than stretching every
   heading to the same width; a huge original canvas makes the artwork look tiny.
4. Render the decorative SVG inside a real heading containing the actual title
   text. Hide the duplicate text visually only when artwork is present, and use
   empty alt text/`aria-hidden` on the image. Size the image against the heading's
   responsive em-based line box and inspect desktop/mobile rendering.
5. Give external SVG images their own colour and explicit sizing. An SVG loaded
   through `<img>` does not inherit the host's `currentColor`, and selectors that
   sized an inline `<svg>` may no longer match. Recheck poster marks and seal icons
   when externalizing prototype artwork.

## Port / process checks

```bash
ss -ltnp 2>/dev/null                   # list listeners, find your port + pid
ps -o pid,etime,cmd -p <pid>           # how old that process is
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:<port>/
```

A stale process still listening is the usual explanation when a freshly
launched app behaves like a different project.
