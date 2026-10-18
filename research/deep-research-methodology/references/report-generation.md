# Visual Report Generation

Distilled from Odysseus `src/deep_research.py` L127-176 and `src/visual_report.py`.

## Report-intent decision table

| When the question is... | Pick the intent | Prescribed structure |
|---|---|---|
| "Which X or Y is better?" | **Comparison** | Markdown table across stated criteria; include a recommended pick and the conditions under which each option wins |
| "How do I do X?" | **How-to** | Numbered steps, prerequisites, and common mistakes called out up front |
| "Is this claim true or false?" | **Fact-check** | Evidence for and against each claim, then an explicit verdict |
| "Show me the best product / tool / technique" | **Product** | Ranked list with pros/cons per entry and "where to buy" links |
| None of the above | **Default** (long-form) | Magazine-style report organized by the plan's sub-topics |

Every deliverable is organized by the sub-questions in the plan, not by the order sources were fetched. When a source genuinely serves two intents, follow the intent and mention the secondary fit in a short note.

## Length and quality bar

>= **1500 words**. Organized by the sub-questions identified at planning time, with inline citations throughout. Below that depth it is a summary, not a research report.

## Markdown -> HTML pipeline (visual_report.py)

Applies when producing the self-contained HTML deliverable rather than plain markdown:

| Step | Implementation | Line refs |
| --- | --- | --- |
| Markdown conversion | `python-markdown` with tables, TOC, and code-highlighting extensions | L77-85 |
| Sanitization | `nh3`, stripping scripts and event handlers while permitting `<details>`/`<summary>` | L38-48 |
| TOC generation | Scan `h2`/`h3`, build unique slugs | L103-157 |
| Styling | Injected CSS theme, light+dark via `prefers-color-scheme` | L8-10 |
| Security headers | CSP with `frame-ancestors 'none'` | middleware L114-123 |

Two dependencies only, both optional: `python-markdown` and `nh3`. Skip the HTML stage and hand over markdown when they are unavailable.

## Why sanitization is non-optional here

Report HTML is assembled from text fetched off the open web. Rendering it without `nh3` (or an equivalent allowlist sanitizer) hands every scraped page a path to script execution in whoever opens the report. Do not inline untrusted HTML into a deliverable without sanitizing first.

## Output landing spots

- Research report: the workspace ledger's final form, referenced by absolute path in the reply.
- Persistent state: `data/deep_research/{session_id}.json` upstream; use `$DRA_DIR` here (default `~/Documents/Hermes_Artifacts/`).
- Later retrieval from the document library; nothing is deleted automatically.

## Citation rules

- Every claim carries the URL it came from, attached at extraction time rather than backfilled.
- Distinguish sourced fact from inference explicitly; label speculation as speculation.
- Preserve disagreement between sources as a finding instead of averaging it into a false consensus.
- Never produce a plausible-looking citation for something unverified. Cut the claim or mark it unsourced -- fabricated sources are worse than gaps.
