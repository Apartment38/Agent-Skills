# API Surface and Background Job Control

Distilled from Odysseus `routes/research_routes.py`, `src/research_handler.py` / `services/research/research_handler.py`, and `src/task_scheduler.py`. Load only when running Odysseus proper or scheduling research as a job -- reproducing the loop with Hermes tools needs none of this.

## REST endpoints

| Endpoint | Purpose | Refs |
| --- | --- | --- |
| `POST /api/research/start` | Start a session; resolves credentials via `_owned_enabled_endpoint()` | L112-130 |
| `GET /api/research/active` | Running tasks owned by the caller | L146-163 |
| `GET /api/research/status/{session_id}` | Progress for one task, after validating ID format and ownership | L165-174 |

Frontend streams progress over SSE and renders an SVG "synapse" tree of research nodes (queries, URLs, findings) via `createResearchSynapse`.

## Background job model

`ResearchHandler` orchestrates lifecycle so long research never blocks the FastAPI event loop:

| Method | Role | Refs |
| --- | --- | --- |
| `start_research()` | Resolve endpoint, spawn background `DeepResearcher` with `asyncio.create_task` | L52-104 |
| `get_status()` | Progress percent + step label, checking memory *and* disk | L106-130 |
| `cancel_research()` | Signal the researcher to stop, cancel the asyncio task | L131-145 |
| `generate_plan()` | Build the plan up front via `RESEARCH_PLAN_PROMPT` | L173-180 |

`_active_tasks` tracks running jobs with progress and ownership. State persists as JSON under `DEEP_RESEARCH_DIR` at `data/deep_research/{session_id}.json`. `get_status()` checking disk as well as memory is what lets a client reconnect to a job after a page refresh.

Port to Hermes when a research run exceeds one turn: write the ledger to `$DRA_DIR`, and let a resumed session recover progress by reading that file rather than depending on anything in chat context.

## Security and confinement

| Control | Mechanism | Refs |
| --- | --- | --- |
| Path confinement | `_research_json_path` + `_RESEARCH_SESSION_ID_RE` reject traversal | L53-62 |
| Owner scoping | `_owned_enabled_endpoint` / `_owns_in_memory` restrict tasks to their owner | L56-77, L131-144 |
| Model filtering | `_first_chat_model`, `_NON_CHAT_MODEL` blacklist excludes embeddings/TTS from selection | L29-41 |
| SSRF | `_public_http_url`, `_PinnedTransport` on fetch | content.py L73-115 |
| Report CSP | `SecurityHeadersMiddleware`, `frame-ancestors 'none'` | middleware L114-123 |

A user cannot spend another user's API key, and cannot reach another user's research by guessing an ID.

## Scheduled research

- `task_type="research"` tasks run through the `TaskScheduler`.
- Built-in `action_research` lets the scheduler trigger research as a job.
- Scheduled tasks get a default tool set via `compose_task_relevant_tools`.
- The parallel Hermes mechanism is `cronjob`, with output saved to workspace files.

## Note on the two upstream layouts

Newer tree: `routes/research/research_routes.py` + `services/research/research_handler.py`. Older: `routes/research_routes.py` + `src/research_handler.py`. Both were read; behaviour matches, only packaging moved. Cite the newer paths.
