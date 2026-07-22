---
name: task-outcome-log
description: >-
  Log the outcome of any multi-step task — completed, failed, or abandoned — so
  every attempt becomes a durable record for reminders, learning from failure,
  and project tracking. Use at the natural END of any non-trivial task, in any
  project or surface (Claude Code, Cowork, file-backed work): a feature, a fix, an
  investigation, a migration, a research or ops task. Runs on EVERY outcome unless
  the user directly says not to log. Successful, shippable work additionally gets a
  changelog entry; failures and abandoned work go only to the task log. Skip
  trivial one-shot questions or single-line edits — there is no "task" to track.
---

# Task Outcome Log

Record what happened with a task so it is not lost when the conversation scrolls
away. A finished task — even a failed one — is worth a line: a failure you write
down is a lesson; a failure you forget just repeats.

This skill is **task-type agnostic**. It applies to coding, research, ops,
writing — any multi-step work, on any surface that can persist a file.

## When to run

At the natural END of any multi-step task, on EVERY outcome:

- **Completed** — the task reached its goal and was verified.
- **Failed** — you hit a blocker you could not get past.
- **Abandoned** — the task was dropped, deferred, or superseded before finishing.

**The one exception:** if the user directly tells you not to log this task
("don't log this", "no worklog"), skip it.

**Do NOT log** trivial one-shot exchanges (a single question, a quick lookup, a
one-line edit) — there is no "task" to track. Log real, multi-step work.

## Where to log

### 1. Task log — always (records every outcome)

This is the running journal of every outcome.

1. Find the task log. Check, in order: `docs/TASK_LOG.md`, `TASK_LOG.md`,
   `WORKLOG.md`. Use the first that exists; otherwise create `docs/TASK_LOG.md`
   (or `TASK_LOG.md` at the repo root if there is no `docs/` directory).
2. Prepend a new entry (newest first) with:
   - **Date** and a short **task title**
   - **Outcome**: `Completed` | `Failed` | `Abandoned`
   - **Summary**: what was attempted or done, in a line or two
   - For `Failed` / `Abandoned`: the **Reason** it stopped, and a
     **Lesson / next step** so the record teaches something
3. If the file already has an entry style, match it; otherwise use this format:

```
## 2026-07-19 — Add rate limiting to the API
- **Outcome**: Failed
- **Summary**: Tried a token-bucket middleware on the gateway
- **Reason**: Shared Redis instance was unreachable from the gateway pod
- **Lesson / next step**: Confirm the network policy to Redis before re-attempting
```

### 2. Changelog — successful, shippable work only

Only when the task is `Completed`, verified, AND represents a user-facing change
worth release notes (typically code that shipped):

1. Find the changelog: `CHANGELOG.md`, `CHANGELOG`, `docs/CHANGELOG.md`,
   `HISTORY.md` — first that exists; otherwise create `CHANGELOG.md` using the
   [Keep a Changelog](https://keepachangelog.com) format with an
   `## [Unreleased]` section.
2. Match the file's existing style exactly (headings, bullet character, tense,
   and Added / Changed / Fixed grouping). Add **one** concise, user-facing entry
   under the unreleased section, and **avoid duplicates**.
3. Failed and abandoned work never goes here — release notes describe what
   shipped, not what was tried.

## No writable workspace? (e.g. a plain chat)

If there is no filesystem to write to, do not silently drop the record: present
the same entry inline as a short **"Task outcome"** block at the end of your
reply, so the user can copy it into their own tracker.

## Keep it short

One entry per task, a line or two each. The task log is a journal; the changelog
is release notes. Always tell the user exactly what you logged and where.
