# Task Log

A running journal of every task outcome — newest first. Successful shipped work
also appears in `CHANGELOG.md`; failures and abandoned attempts live only here so
they aid reminders and learning. Written by the `task-outcome-log` skill.

## 2026-07-22 — Enforce main branch protection from inside the repo
- **Outcome**: Failed
- **Summary**: Tried to turn on branch protection for `main` by committing a
  config file to the repo, so the protection rules would be version-controlled.
- **Reason**: GitHub branch protection / rulesets are server-side repo *settings*,
  not read from any file in the repo tree. No committed file enables them — it
  needs repo-admin access via Settings → Branches or the REST API.
- **Lesson / next step**: Version-controlled protection needs external automation
  (a Terraform provider or the "Settings" GitHub App), not a plain repo file. For
  now, set it once in the GitHub UI.

## 2026-07-22 — Add task-outcome logging (feature-dev Phase 8 + portable skill)
- **Outcome**: Completed
- **Summary**: Added a Phase 8 to the `/feature-dev` workflow and a standalone
  `task-outcome-log` skill so every multi-step task records its outcome —
  successes to the changelog, all outcomes (including failures) to this log.
- **Lesson / next step**: Dogfooding the skill on its own creation confirmed the
  create-if-absent path works and produced this first entry. Next: exercise it on
  a failed/abandoned task to confirm the reason + lesson fields read well.
