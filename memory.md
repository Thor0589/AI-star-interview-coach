# memory.md

## Current Snapshot
- Repository: `Thor0589/AI-star-interview-coach`
- Focus area: STAR interview coaching workflows and project cleanup/hardening
- Current state: baseline docs refreshed for maintainability and handoff continuity

## Handoff Notes
- Legacy/experimental artifacts may still exist under `STARMETHOD/` and should be rationalized before a stable release tag.
- Priorities remain: documentation clarity, API key safety, and aligning runtime entrypoints.

## Immediate Next Steps
1. Confirm primary app entrypoint and remove ambiguity.
2. Remove hardcoded credentials and enforce environment-based configuration.
3. Clean up stale files and verify end-to-end run instructions.
4. Tag a release only after cleanup and validation.

## Session Update (2026-04-23)
- Completed backend-proxy migration for Gemini calls using `backend/server.py` (FastAPI) and `STARMETHOD/gemini_proxy_client.py`.
- Removed Gemini/OpenAI BYOK sidebar key-entry flow from `STARMETHOD/app.py` and replaced with passive backend health indicator.
- Frontend no longer references direct Gemini host; Gemini requests are routed through `/api/gemini` via proxy helper.
- Added security/config scaffolding: `.env.example`, updated `requirements.txt`, and README backend/frontend run instructions.

### Decisions
- Chose FastAPI because the codebase is Python-first and no backend previously existed.
- Implemented non-streaming proxy only (`POST /api/gemini`) because current frontend does not use streaming.

### Blockers / Remaining
- End-to-end live Gemini smoke test is pending valid local `GEMINI_API_KEY` in runtime environment.
- Consider future refactor to centralize repeated prompt-call snippets in `STARMETHOD/app.py`.

### Next Step
1. Run backend + Streamlit with a valid server-side `GEMINI_API_KEY` and verify live response path.
2. Rotate previously exposed Gemini key immediately.
