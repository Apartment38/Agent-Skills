# The Iterative Research Loop

Distilled from Odysseus `DeepResearcher` (src/deep_research.py, IterResearch-style) and the two DeepWiki descriptions of it.

## Core idea

Not "search once and summarize." An LLM drives every decision: what sub-topics exist, which queries to issue, what counts as evidence, and when to stop. Each round is **Think -> Search -> Extract -> Synthesize**, and the loop exits only on an explicit sufficiency verdict.

```
plan -> generate queries -> search -> fetch -> extract -> filter
   ^                                                       |
   |                                                  synthesize
   |                                                       |
   +---- stop? NO ------------------------------------ stop? YES -> report
```

## The five prompt stages

| Stage | Upstream constant | Job | Hermes action |
| --- | --- | --- | --- |
| Plan | `RESEARCH_PLAN_PROMPT` | Produce sub-questions + success criteria | `write_file` plan into ledger |
| Query gen | `QUERY_GEN_PROMPT` (L64-82) | Queries targeting missing info | Author queries from plan gaps |
| Extract | `EXTRACTOR_SYSTEM` (goal_based_extractor.py L6-23) | Pull relevant facts from raw page text | Filter page text against the goal |
| Synthesize | `SYNTHESIZE_PROMPT` (L84-101) | Integrate new findings, remove redundancy, resolve contradictions | Append folded findings to ledger |
| Stop | `STOP_PROMPT` (L103-125) | YES = comprehensive, stop; NO = keep going | Explicit YES/NO check vs criteria |

## Phase details

1. **Date grounding** -- `current_date_context()` injects today's date (L25-36). Without it the model queries as if it were at its training cutoff and misses recent material.
2. **Planning** -- done before the loop; also used by `ResearchHandler.generate_plan()`.
3. **Query generation** -- `num_queries` per round, driven by the plan *and* by what current findings still lack. Never regenerate queries already answered.
4. **Search + fetch + extract** -- see `search-and-extraction.md`.
5. **Synthesize then stop-check** -- order matters. Synthesize first, so the stop verdict evaluates the current report rather than raw evidence.

## Query synthesis guard

`ResearchHandler.synthesize_query()` converts conversation history into one focused query and includes an affirmation check: it refuses bare filler ("yes", "ok") and falls back to the original substantive user message (L92-135). Port this -- a single-word reply must not become a research topic.

## Defaults worth adopting

| Control | Source | Value | Why |
| --- | --- | --- | --- |
| Rounds | L77-82 | up to 8 | Hard cap prevents runaway loops |
| `extraction_concurrency` | extraction_controls test L38-39 | 4 | Backpressure semaphore; avoid rate limits and local exhaustion |
| `hard_timeout` | L307-310 | ~300 s per job | Guarantees termination |
| Final report length | L127-170 | >= 1500 words | Forces depth over summary |

## Resilience patterns

- **JSON repair** (L490-510): `strip_thinking` then manual regex repair. Applies when a child returns reasoning-wrapped or malformed structured output.
- **Synthesis resilience**: on failure, preserve the previous report and fall back to compiled findings rather than discarding the run.
- **Non-default timeouts**: planning and synthesis calls get their own timeouts, not an inherited 60 s; long synthesis legitimately exceeds it.
- **Redundancy registry**: `analyzed_urls` prevents reprocessing the same URL across rounds.

## Anti-patterns

- Skipping the plan and going straight to queries -- queries then optimize for coverage of nothing in particular.
- Holding findings in conversation instead of the ledger -- silently lost on compaction, and the stop check rubber-stamps an empty report.
- Letting the round cap be the *only* stop signal -- the STOP check is the real terminator; the cap is a safety net.
- Synthesizing raw search snippets without an extraction pass -- noise enters the report and compounds each round.
