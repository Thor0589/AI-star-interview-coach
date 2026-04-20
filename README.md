# AI STAR Interview Coach

AI-powered coaching tools to help users build stronger behavioral interview answers using the STAR framework (Situation, Task, Action, Result).

## Features
- Guided STAR story creation workflows
- Competency-based and question-based prompting
- Story evaluation and feedback helpers
- Multiple scripts/prototypes under `STARMETHOD/`

## Repository Structure
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/app.py` – Streamlit-style interactive app entrypoint (current UI implementation)
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/star_method_coach.py` – Core STAR coaching logic
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/unified_star_coach.py` – Unified coaching flow logic
- `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD/models.py` – Shared models/types

## Architecture
Data flow for the main coaching path:
`app.py` -> `UnifiedSTARCoach` -> `competency_questions.py`

## Quick Start
1. Use Python 3.9+.
2. Create and activate a virtual environment.
3. Install required packages, including `openai`, `streamlit`, `colorama`, and `requests`.
4. Run from the repository root.

Example launch:
```bash
streamlit run STARMETHOD/app.py
```

## Security Note
Do **not** hardcode API keys in source files. Use environment variables (for example `GEMINI_API_KEY`) and secure secret management.

## Project Status
The project is active and in cleanup/standardization mode. Expect iterative improvements to structure, docs, and deployment readiness.

## License
MIT (see `LICENSE`).
