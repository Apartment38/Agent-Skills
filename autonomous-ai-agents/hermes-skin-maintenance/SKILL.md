---
name: hermes-skin-maintenance
description: "Use when maintaining Hermes skins. Verify complete colors."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, skins, themes, yaml, tui, desktop, cli]
---

# Hermes Skin Maintenance

Use this skill to audit, extend, or repair an existing Hermes skin while preserving its visual character across the CLI, TUI, and desktop app.

## Authority and scope

- The canonical cross-surface color contract is `SKIN_COLOR_TOKENS` in `apps/shared/src/skin.ts` in the Hermes Agent repository. Fetch the raw file from the branch requested by the user, or `main` when no revision is specified.
- A skin can contain legacy or niche keys, but token coverage must be measured only against the canonical list. Do not delete compatible extras merely because they are absent from that list.
- Resolve the active Hermes home from `$HERMES_HOME`; if unset, use `~/.hermes`. Never hand-edit `config.yaml`.

## Procedure

1. Load the Hermes theming guidance if available and inspect the target skin YAML.
2. Fetch and parse `SKIN_COLOR_TOKENS`; do not infer the list from an old template.
3. Compute the missing keys programmatically from the skin's `colors` mapping.
4. Add only missing canonical keys. Preserve existing values and assign new colors by semantic family rather than inventing unrelated hues:
   - `background`: a dark or light base that fits the established skin.
   - primary/text/border: reuse the existing heading, body, and structural palette.
   - tool/thinking: inherit the skin's accent and secondary-label colors unless an intentional contrast distinction exists.
   - diff/status/syntax: map positive→ok, warning/number→warn, negative→error; use a slightly stronger shade for word-level diffs and critical status.
   - terminal chrome: reuse prompt/accent/text hierarchy consistently.
5. Keep all values as quoted six-digit `#rrggbb` colors.
6. Validate the YAML and verify that every canonical token is now present.
7. Apply the edited skin with `hermes config set display.skin <name>` and read back `hermes config get display.skin` before reporting success.

## Verification checklist

Report these exact checks:

- Target file path and embedded skin `name` agree.
- YAML parses successfully.
- `missing_tokens=none` against the fetched canonical `SKIN_COLOR_TOKENS`.
- The active skin resolves to the target name after applying it.

## Pitfalls

- The skin's existing palette may intentionally omit `background`; adding it is still necessary for reliable desktop/TUI base-surface rendering.
- `status_bar_bad` and `status_bar_critical` are distinct. Do not stop at the older, smaller template palette.
- When changing the configured model provider in the same session, remove an inherited custom `model.base_url` after selecting an OAuth provider; otherwise an old local endpoint may remain in the configuration. Verify the selected provider's auth status before declaring the migration complete.
- Do not modify bundled or user-owned Hermes skills. Create or update a curator-managed companion skill instead.
