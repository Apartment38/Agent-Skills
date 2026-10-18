---
name: agent-theme-copy
description: "Use when drafting agent theme microcopy and glyphs."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent, theme, microcopy, glyphs, faces, unicode]
    related_skills: []
---

# Agent Theme Copy

Create compact, internally consistent personality text for agent skins: status faces, thinking verbs, symbols, greetings, and other low-attention UI language. This skill supplies copy only; consult the relevant platform's theme schema before assigning keys or editing a theme.

## When to Use

- A user requests waiting or thinking faces, status verbs, decorative glyphs, or short agent-themed UI wording.
- A skin, terminal prompt, or chat interface needs a cohesive personality layer.
- Do not use for large ASCII scenes, image prompts, or theme configuration changes.

## Procedure

1. Infer the persona's baseline: composure, warmth, humor, formality, and visual motifs. Keep each item legible in monospaced UI.
2. Offer 6–10 alternatives per requested category unless the user asks for a single final value. Keep faces visually simple and compatible with ordinary Unicode fonts.
3. Make all categories feel like one character. Match status verbs to the persona's decision style rather than using generic activity labels.
4. Finish with a compact recommended set when the user may need one value per config key. Clearly label it.

## Design Rules

- Prioritize short forms that remain readable in narrow terminal and desktop status areas.
- Favor restrained expressions for reserved or professional personas; reserve exaggerated kaomoji for explicitly playful themes.
- Use symbols that retain their meaning without color. Pair compatible wing glyphs when the UI supports left and right ornaments.
- Avoid emoji-only faces unless the user explicitly wants an emoji-forward theme; rendering differs substantially between terminals.
- Avoid terms that imply actions the agent has not actually performed. For example, prefer `considering` over `verifying` unless verification is genuinely under way.

## Persona Translation

- Disciplined/protective: `assessing`, `reviewing`, `cross-checking`, clean stars or diamonds.
- Warm/service-oriented: gentle neutral faces, `standing by`, `preparing`, `attending`.
- Technical/sci-fi: sparse geometric marks such as `✦`, `✧`, `◇`, `◈`, `⟡`.
- Playful: expressive faces and lighter verbs, but test their visual weight against the rest of the theme.

## Verification

- Every proposed glyph is readable as plain text and does not rely on color for interpretation.
- The recommended face, verb, and ornament share the same emotional register.
- No proposed status text overstates task progress or certainty.
