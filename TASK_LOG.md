# Task Log

A running journal of every task outcome — newest first. Successful shipped work
also appears in `CHANGELOG.md`; failures and abandoned attempts live only here so
they aid reminders and learning. Written by the `task-outcome-log` skill.

## 2026-07-22 — Add task-outcome logging (feature-dev Phase 8 + portable skill)
- **Outcome**: Completed
- **Summary**: Added a Phase 8 to the `/feature-dev` workflow and a standalone
  `task-outcome-log` skill so every multi-step task records its outcome —
  successes to the changelog, all outcomes (including failures) to this log.
- **Lesson / next step**: Dogfooding the skill on its own creation confirmed the
  create-if-absent path works and produced this first entry. Next: exercise it on
  a failed/abandoned task to confirm the reason + lesson fields read well.
