---
name: isolated-wayland-acceptance
description: "Use when testing native Wayland apps autonomously."
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [wayland, native-apps, acceptance-testing, isolation]
    related_skills: [systematic-debugging, test-driven-development]
---

# Isolated Wayland acceptance

## When to Use

Use for autonomous native Wayland application verification, including portal/input integration, display authority, self-occlusion and output geometry acceptance.

Use a disposable compositor session when native-app testing otherwise repeatedly requires the human's desktop or permission dialogs. Keep all state inside the explicitly authorized project directory; do not broaden permission to change host configuration or install desktop entries.

## Acceptance procedure

1. **Set the boundary.** Keep compositor state, configuration, desktop-entry staging and evidence inside the authorized project. Use the private session when autonomous testing would otherwise require repeated human intervention; do not expand permission to alter the human desktop.
2. **Build the exact artifact.** Run targeted regression tests and build the executable that the live harness will launch. After integration, rerun the complete workspace/all-target gates; passing a standalone probe does not validate the application coordinator.
3. **Prepare identity and consent.** Stage the application's desktop entry in the private XDG data directory with an Exec that resolves to the actual test binary. Observe each private authorization stage before acting: a saved shortcut assignment may eliminate a dialog on later runs, so blindly clicking its former button can confirm the picker instead.
4. **Prepare the fixture.** Calibrate its global origin from delivered pointer events. Activate the intended fixture/output before launching a chooser when using fixed test coordinates, then observe the actual dialog placement before injecting input; a dialog can follow the previously active monitor. Compute each target from that output's observed origin plus the fixture-local point, not a remembered global coordinate from another color patch. Take the active-picking mouse/focus baseline after authorization dialogs close; report authorization focus changes separately rather than demanding zero changes across startup.
5. **Run independent cases.** Verify successful selection and its exact output, right cancellation, Escape cancellation and post-close key pass-through, idle timeout, and relevant failures. For self-occlusion, use different lens and underlying colors and compare against an independent cursor-free screenshot after recovery.
6. **Expand geometry deliberately.** Place fixtures on named outputs using ordinary xdg-toplevel fullscreen requests, verify actual configure dimensions and delivered local coordinates, then exercise scale/origin/transform combinations. Record output mode, logical size, origin, scale and negotiated video dimensions before and after capture/screenshot operations. If geometry changes during the case, stop the acceptance assertion and investigate that change; do not relax coordinate validation on an unproven rounding hypothesis. Fixture placement alone is not picker-routing acceptance, and a smaller negotiated stream is not proof of physical-resolution sampling.
7. **Preserve and close.** Save each case's result, traces and screenshots immediately, before reusing fixtures or changing focus. Read back closure effects and ensure private test processes are reaped. Keep experimental/default-path changes gated on the whole acceptance matrix, not one successful case.

Read [integrated acceptance recipes](references/integrated-acceptance.md) for the command sequence, Escape two-press check, self-occlusion assertions and output-matrix preparation.

## Isolation

- Give the lab its own D-Bus, Wayland socket, XDG_RUNTIME_DIR (0700), HOME, config/data/cache/state directories, PipeWire and portal services. Construct a minimal environment rather than copying credential-bearing variables.
- Assert private runtime, bus and Wayland identities before every command or input injection. Automate only disposable lab dialogs, never human-session consent dialogs.
- On KWin virtual outputs, keep a fake-input device alive so pointer seat capability persists between short-lived input helpers.
- PipeWire capture can remain Paused without a session manager. WirePlumber's policy-only profile can link private streams without loading audio/camera hardware monitors.
- A portal backend may autoactivate the frontend before the supervisor starts it. An explicitly supervised frontend can use its documented --replace option on the PRIVATE bus to avoid duplicate-process normal exit being mistaken for service failure.
- Make supervisor lifetime shorter than the input holder's bounded lifetime, or handle expected holder expiration explicitly. Reap private services on shutdown.

## Evidence discipline

- Successful input roundtrips prove processing, not delivery. Calibrate fixture origin from observed pointer events; compare mouse counters, keyboard enter/leave and focus before and after selection/cancellation.
- Cursor submission, screenshots, buffer release and wl_surface.frame callbacks are not genuine presentation acknowledgments. When actual display authority is required, require the relevant commit's wp_presentation Presented event.
- Probe cursor-role presentation separately from ordinary window presentation: a visible cursor image and frame callbacks can coexist with absent Presented events. Do not infer software-plane fallback or reliable presentation from increasing cursor-buffer size.
- Test selection, right cancellation and idle timeout separately. None proves held-button failure safety, scaling, output switching or integrated Escape lifecycle.
- Preserve real JSON results, traces and private screenshots in project evidence directories, not global memory. Do not preserve environment files or secrets. Snapshot acceptance counters before subsequent fixture activation changes them. Prototype feasibility is not production acceptance.
- Verify the shipped executable's stdout and stderr separately: assert the exact selected color on stdout and keep diagnostics on stderr. A no-sample confirmation must be a real error, not a successful exit accompanied by a failure log.
- Label test totals precisely when examples reuse production modules; repeated test executions are not additional unique behaviors. Label checks run during concurrent edits as snapshots and rerun final gates after all writers finish.

## Normal-overlay self-occlusion experiment

A tested alternative uses a normal input-transparent, keyboard-noninteractive lens plus separate full-pointer-input, keyboard-noninteractive shields.

Track every potentially captured submitted lens footprint, not only the last displayed position. Before sampling an intersecting source neighborhood, invalidate selection and submit a fully transparent non-null buffer while retaining mapping. Require genuine hide presentation; then accept only fresh VIDEO with PTS later than local CLOCK_MONOTONIC receipt of that acknowledgment. Verify the advertised presentation clock and reject missing/uncomparable timestamps. Cursor-only metadata updates must retain old video PTS and cannot satisfy freshness. Ignore stale-generation feedback; bound history without silently evicting contamination.

This ordering argument is specific to the inspected KWin implementation, not a generic PipeWire guarantee. Validate the transparent mapped hide and fresh-video recovery live. Compare the uncovered target against an independent cursor-free screenshot, using different lens and underlying colors so recursive capture cannot accidentally pass. Displayed magnifier authority does not promise instantaneous equality with an independently animating source.
