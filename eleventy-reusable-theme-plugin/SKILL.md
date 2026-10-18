---
name: eleventy-reusable-theme-plugin
description: "Use when building reusable Eleventy 3 theme plugins."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [eleventy, themes, testing]
    related_skills: [test-driven-development, systematic-debugging]
---

# Reusable Eleventy 3 theme plugins

## When to Use

Use for reusable Eleventy 3 plugins that own layouts and assets while preserving site-owned directories and metadata.

## Proven rules

- Register layout aliases during plugin execution, using `eleventyConfig.directories.layouts || eleventyConfig.directories.includes` as the effective root. Compute POSIX relative paths from that root to the module-owned layout files; do not assume absolute alias targets work.
- Do not register aliases in `eleventy.directories`: Eleventy 3.1.6 emits it after merging/copying `layoutAliases`, so late registrations do not reach layout resolution.
- Preserve site include/layout directory settings. Theme aliases can resolve files outside the input directory while ordinary Liquid includes remain site-owned.
- Capture actual pre-layout bodies using `addPreprocessor(name, '*', function(data, content) { bodies.set(this.inputPath, content); return content; })`. The callback receives data and content, not inputPath; the path is on `this`.
- Avoid reading collection-item `content`/`templateContent` during collection creation: their getters can throw premature-render errors. Normalize from captured bodies, preserving the original collection item separately.
- Ignore the entire module-owned theme directory for page discovery, and explicitly register its assets as passthrough. Verify both: ignoring theme sources must not prevent registered assets from copying.
- Run unrelated isolated Eleventy API fixture builds in separate Node processes. Module-level layout caches use input-relative keys and can leak aliases across fixtures when changing working directories in one process.
- Prove default input, nested input, custom layouts, unchanged site includes, opt-in legacy aliases, and asset passthrough with installed Eleventy API builds. Use the actual site's posts in fixtures when validating metadata and excerpts.
- Return summary text, not trusted HTML; verify Liquid `escape` remains required for entity-decoded markup. Keep configurable metadata in a theme namespace rather than replacing site-owned global data.
- Build heading TOCs from rendered HTML with a real parser and source locations; patch only ID attributes to preserve authored markup and escaped URLs. Reserve existing IDs before generating slugs, scope post headings to the article, and exclude hidden/decorative/navigation headings. Keep fragment links server-rendered and test heading-free posts.
- Make tick-to-label TOCs keyboard-accessible without JavaScript: a focusable post nav can reveal its list with `:focus-within`, while decorative ticks stay out of the tab order. Verify panel clearance against actual heading bounds, long-list scrolling, unchanged-active-section resizing, native anchor clicks, and no-JS hover/focus behaviour.
- Apply Liquid `escape` last to every dynamic `href`/`src`, after `url` or scheme validation: a valid root-relative permalink can still contain quotes and markup. Prove this with a real isolated Eleventy build using an explicit synthetic quoted/markup permalink, check every listing link, and entity-decode attributes to verify the original URL survives escaping; accept both `&#34;` and `&quot;` for escaped quotes.
