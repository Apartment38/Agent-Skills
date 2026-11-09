# Integrated native application acceptance

Use this recipe after a standalone Wayland experiment passes and the behavior is integrated into the real application. Keep all commands and input tied to the private compositor's verified environment.

## 1. Verify the artifact before opening portals

For a Cargo workspace, use the real project's equivalent of:

```sh
cargo test --offline --locked --workspace --all-targets
cargo clippy --offline --locked --workspace --all-targets -- -D warnings
cargo fmt --all -- --check
cargo build --release --offline --locked -p "$PICKER_PACKAGE"
```

Exercise help/version and invalid option combinations without portal startup. Reject unsupported combinations before requesting permissions. Preserve the default backend while an opt-in path is still undergoing acceptance; build success is not permission to promote it.

Record which artifact and verification snapshot the live case uses. Do not count included capture/portal tests in several examples as distinct new behaviors.

## 2. Establish private application identity

Copy the application's packaging desktop entry into the lab's own XDG data applications directory. For an uninstalled development executable, point the private copy's Exec to the actual built binary; do not assume the lab PATH contains the project's output directory. Leave the public packaging entry appropriate for normal installation and do not install a host entry merely to make the test pass.

Wait for the actual ScreenCast authorization stage, inspect the private chooser, and select only the monitors supported by the implementation under test. Then observe the GlobalShortcuts stage separately. An application with a saved private assignment may proceed without another shortcut dialog. Check whether the worker is already active before clicking any remembered approval coordinates.

Never transfer this automation to the human session's consent dialogs.

## 3. Capture the correct focus baseline

Launch a native fixture that logs delivered pointer coordinates, button press/release counters, keyboard enter/leave, activation and shutdown. Calibrate its origin from a known global pointer move and the resulting local event rather than reusing a window position from a previous run.

Take the active-picking baseline only after consent dialogs close and the picker is ready. Authorization can legitimately move focus; compare active-picking counters to the post-authorization baseline and preserve both phases in the evidence.

Persist the result and corresponding fixture trace before creating another fixture or changing output configuration. Later expected focus changes must not be confused with picker-induced focus loss.

## 4. Selection and self-occlusion

1. Place the pointer on a controlled static source and require the exact lens commit's genuine Presented event.
2. Capture the current lens footprint in an independent cursor-free screenshot.
3. Move the pointer into that old footprint where the lens color differs from the underlying fixture. This makes recursive capture distinguishable from a correct sample.
4. Require the transparent mapped hide's Presented event and a validated CLOCK_MONOTONIC receipt cutoff.
5. Require newly decoded VIDEO PTS strictly greater than that receipt cutoff. Reused pixels from cursor-only metadata updates must not qualify.
6. Require the new visible commit's Presented event, then independently screenshot the uncovered source and compare its RGB with the authorized sample.
7. Confirm with a complete left press/release pair. Assert the exact output color, unchanged fixture mouse/focus counters during picking, lens/shield removal and explicit closure of both portal sessions.

Keep raw application diagnostics separate from stdout so a success assertion cannot accidentally match an earlier diagnostic color. Do not infer instantaneous agreement with an independently animating source from this static recovery case; test displayed-commit authority on animation separately.

## 5. Integrated Escape lifecycle

1. Subscribe to Activated before binding the shortcut, validate the effective bare Escape trigger, and do not map input shields until authorization succeeds.
2. While the picker is active and has genuinely presented a sample, inject one Escape in the private session.
3. Require typed cancellation, worker shutdown, lens/shield removal and explicit GlobalShortcuts and ScreenCast closure. Verify the fixture remains alive and focused, without a delivered Escape press that would terminate it.
4. After closure, inject a second Escape. Require the fixture's own Escape handler and normal shutdown. This distinguishes merely ignoring callbacks from actually releasing the global shortcut.

Test right cancellation and idle timeout separately. Neither this two-press check nor a successful cancellation establishes cleanup safety while another mouse button remains held. A bounded failure exit must not be presented as proof of no orphan release/click-through.

## 6. Output matrix preparation

Add an exact-name fullscreen-output option to the test fixture if needed, using standard xdg-toplevel fullscreen requests rather than manipulating human windows. Preserve the requested output name exactly. Verify the compositor's actual configure size and delivered local pointer position after the request; omit the fixture's ordinary minimum-window-size restriction when it would interfere with a smaller fullscreen test output.

Prepare separate fixtures on primary and secondary outputs. Test authorized monitor matching by compositor-space origin, fractional scale, negative origins and supported transforms. During output transitions, require genuine hide acknowledgment for the old visible lens before rebuilding it on another output, preserve dirty footprints until a qualifying fresh-video barrier, and reject stale-generation feedback. If a combination is unsupported, report that explicit failure rather than allowing stale coordinates or the first stream in an array to stand in for the active output.

Fixture fullscreen success is only setup evidence. Claim routing acceptance only after the real picker follows the pointer to the correct authorized stream, presents the corresponding sample and returns the independently verified color.
