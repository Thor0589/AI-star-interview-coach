# agent.md
_Previously named `AGENTS.md`; update any remaining references to use `agent.md`._

This repository is a Python-based STAR interview coaching project centered on `STARMETHOD/`.

## Purpose
Provide consistent guidance for human and AI contributors working in this repo.

## Scope
- Root docs and project metadata live at repository root.
- Core application logic lives in `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD`.

## Working Rules
1. Prefer minimal, focused changes tied directly to the requested task.
2. Preserve existing behavior unless the task explicitly requires behavioral changes.
3. Keep secrets out of source control; use environment variables for API keys.
4. Update documentation when behavior, setup, or workflow changes.
5. Avoid adding new dependencies unless required.

## Doc Precedence
For contributor guidance in this repo:
1. Explicit user request
2. System/developer instructions from the active agent runtime
3. This `agent.md`
4. Supplemental docs (`CLAUDE.md`, `memory.md`, `README.md`)

## Suggested Validation
When applicable, run existing tests/checks already present in the repository before finalizing changes.
