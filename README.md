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
- `app.py` captures user inputs and orchestrates the Streamlit workflow.
- `UnifiedSTARCoach` processes the selected competency/question into guided STAR coaching steps.
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
5. Configure API keys (environment variables) or provide them in the app sidebar at runtime (BYOK):
   ```bash
   export GEMINI_API_KEY="your_gemini_key"
   export OPENAI_API_KEY="your_openai_key"
   ```
   On Windows (PowerShell):
   ```powershell
   $env:GEMINI_API_KEY="your_gemini_key"
   $env:OPENAI_API_KEY="your_openai_key"
   ```
6. Run from the repository root:
    ```bash
    streamlit run STARMETHOD/app.py
    ```
   If no keys are supplied, the app runs in mock-response mode so you can still test the full UI flow.

## Security Note
Do **not** hardcode API keys in source files. Use environment variables (for example `GEMINI_API_KEY`) and secure secret management.

## Project Status
The project is active and in cleanup/standardization mode. Expect iterative improvements to structure, docs, and deployment readiness.

## License
MIT (see `LICENSE`).
