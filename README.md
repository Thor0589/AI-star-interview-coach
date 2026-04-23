# AI STAR Interview Coach

AI-powered coaching tools to help users build stronger behavioral interview answers using the STAR framework (Situation, Task, Action, Result).

## Features
- Guided STAR story creation workflows
- Competency-based and question-based prompting
- Story evaluation and feedback helpers
- Multiple scripts/prototypes under `STARMETHOD/`

## Repository Structure
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/app.py` – Streamlit-style interactive app entrypoint (current UI implementation)
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/gemini_proxy_client.py` – Frontend helper that routes all Gemini requests to the backend proxy
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/backend/server.py` – FastAPI backend proxy for Gemini requests (`/api/health`, `/api/gemini`)
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/star_method_coach.py` – Core STAR coaching logic
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/unified_star_coach.py` – Unified coaching flow logic
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/models.py` – Shared models/types

## Architecture
Data flow for the main coaching path:
`app.py` -> `gemini_proxy_client.py` -> `backend/server.py` -> Gemini API
- `app.py` captures user inputs and orchestrates the Streamlit workflow.
- `gemini_proxy_client.py` ensures the browser-facing app only talks to local backend routes.
- `backend/server.py` holds the server-side `GEMINI_API_KEY`, applies validation/rate limits/timeouts/model allowlist, and forwards approved requests upstream.
- `competency_questions.py` provides the competency-aligned prompt source used by the coaching flow.

## Quick Start
1. Use Python 3.9+.
2. Clone and enter the repository:
   ```bash
   git clone https://github.com/Thor0589/AI-star-interview-coach.git
   cd AI-star-interview-coach
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
   On Windows (PowerShell):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Copy environment variables and configure server-side secrets:
   ```bash
   cp .env.example .env
   ```
6. Set `GEMINI_API_KEY` in `.env` (server-side only). Optionally set `OPENAI_API_KEY` for OpenAI-backed feedback paths.
7. Run the backend proxy:
   ```bash
   uvicorn backend.server:app --reload --port 8000
   ```
8. In another terminal, run the Streamlit frontend:
   ```bash
   streamlit run STARMETHOD/app.py
   ```
9. Frontend/Backend local communication:
   - Streamlit frontend: `http://localhost:8501`
   - Backend proxy: `http://localhost:8000`
   - Frontend proxy target is configurable via `GEMINI_PROXY_BASE_URL`.
10. If `GEMINI_API_KEY` is unset, `/api/health` reports `geminiConfigured: false` and Gemini requests are rejected cleanly by the backend.

## Security Note
The previous client-side BYOK model let users enter keys in the browser session, which increased exposure risk. The safer model is backend proxying: keep `GEMINI_API_KEY` only in server-side environment variables and forward requests from the backend.

Treat any previously exposed Gemini key as compromised and rotate it immediately.

## Project Status
The project is active and in cleanup/standardization mode. Expect iterative improvements to structure, docs, and deployment readiness.

## License
MIT (see `LICENSE`).
