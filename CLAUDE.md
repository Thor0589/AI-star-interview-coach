# CLAUDE.md

Claude guidance for working in `Thor0589/AI-star-interview-coach`.

## Primary Goal
Help maintain and improve the STAR interview coach while keeping changes small, safe, and easy to review.

## Codebase Orientation
- Main code folder: `/home/runner/work/AI-star-interview-coach/AI-star-interview-coach/STARMETHOD`
- Key files:
  - `app.py`: interactive app and UI flow
  - `star_method_coach.py`: STAR coaching engine
  - `unified_star_coach.py`: unified coaching pathway
  - `competency_questions.py`: competency prompt source
  - `models.py`: shared structures

## Expectations for Changes
1. Preserve existing user workflows unless task requires change.
2. Prioritize credential safety and configuration cleanup.
3. Keep docs synced with actual runtime behavior.
4. Avoid broad refactors unless explicitly requested.

## Cleanup Checklist (Living)
- [ ] Remove hardcoded secrets from runtime code
- [ ] Align and document single recommended entrypoint
- [ ] Prune stale/duplicate scripts where safe
- [ ] Confirm run instructions are accurate end-to-end
- [ ] Cut stable tag after cleanup and validation

## Handoff Behavior
When handing off work, summarize:
- what changed,
- what remains,
- any risks/blockers,
- exact files touched.
