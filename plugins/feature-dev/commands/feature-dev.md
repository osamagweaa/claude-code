---
description: Guided feature development with codebase understanding, architecture focus, and automatic logging of every task outcome to a task log and changelog
argument-hint: Optional feature description
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach: understand the codebase deeply, identify and ask about all underspecified details, design elegant architectures, implement, then log the outcome — success, failure, or abandonment — to the task log, and (for shipped work) the changelog.

## Core Principles

- **Ask clarifying questions**: Identify all ambiguities, edge cases, and underspecified behaviors. Ask specific, concrete questions rather than making assumptions. Wait for user answers before proceeding with implementation. Ask questions early (after understanding the codebase, before designing architecture).
- **Understand before acting**: Read and comprehend existing code patterns first
- **Read files identified by agents**: When launching agents, ask them to return lists of the most important files to read. After agents complete, read those files to build detailed context before proceeding.
- **Simple and elegant**: Prioritize readable, maintainable, architecturally sound code
- **Use TodoWrite**: Track all progress throughout
- **Log every outcome**: Whether the task succeeds, fails, or is abandoned, automatically record it (see Phase 8) — unless the user directly says not to log this task. Every attempt goes to the task log so failures aid reminders and learning; successful, shipped work additionally goes to the changelog.

---

## Phase 1: Discovery

**Goal**: Understand what needs to be built

Initial request: $ARGUMENTS

**Actions**:
1. Create todo list with all phases
2. If feature unclear, ask user for:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding and confirm with user

---

## Phase 2: Codebase Exploration

**Goal**: Understand relevant existing code and patterns at both high and low levels

**Actions**:
1. Launch 2-3 code-explorer agents in parallel. Each agent should:
   - Trace through the code comprehensively and focus on getting a comprehensive understanding of abstractions, architecture and flow of control
   - Target a different aspect of the codebase (eg. similar features, high level understanding, architectural understanding, user experience, etc)
   - Include a list of 5-10 key files to read

   **Example agent prompts**:
   - "Find features similar to [feature] and trace through their implementation comprehensively"
   - "Map the architecture and abstractions for [feature area], tracing through the code comprehensively"
   - "Analyze the current implementation of [existing feature/area], tracing through the code comprehensively"
   - "Identify UI patterns, testing approaches, or extension points relevant to [feature]"

2. Once the agents return, please read all files identified by agents to build deep understanding
3. Present comprehensive summary of findings and patterns discovered

---

## Phase 3: Clarifying Questions

**Goal**: Fill in gaps and resolve all ambiguities before designing

**CRITICAL**: This is one of the most important phases. DO NOT SKIP.

**Actions**:
1. Review the codebase findings and original feature request
2. Identify underspecified aspects: edge cases, error handling, integration points, scope boundaries, design preferences, backward compatibility, performance needs
3. **Present all questions to the user in a clear, organized list**
4. **Wait for answers before proceeding to architecture design**

If the user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 4: Architecture Design

**Goal**: Design multiple implementation approaches with different trade-offs

**Actions**:
1. Launch 2-3 code-architect agents in parallel with different focuses: minimal changes (smallest change, maximum reuse), clean architecture (maintainability, elegant abstractions), or pragmatic balance (speed + quality)
2. Review all approaches and form your opinion on which fits best for this specific task (consider: small fix vs large feature, urgency, complexity, team context)
3. Present to user: brief summary of each approach, trade-offs comparison, **your recommendation with reasoning**, concrete implementation differences
4. **Ask user which approach they prefer**

---

## Phase 5: Implementation

**Goal**: Build the feature

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:
1. Wait for explicit user approval
2. Read all relevant files identified in previous phases
3. Implement following chosen architecture
4. Follow codebase conventions strictly
5. Write clean, well-documented code
6. Update todos as you progress

---

## Phase 6: Quality Review

**Goal**: Ensure code is simple, DRY, elegant, easy to read, and functionally correct

**Actions**:
1. Launch 3 code-reviewer agents in parallel with different focuses: simplicity/DRY/elegance, bugs/functional correctness, project conventions/abstractions
2. Consolidate findings and identify highest severity issues that you recommend fixing
3. **Present findings to user and ask what they want to do** (fix now, fix later, or proceed as-is)
4. Address issues based on user decision

---

## Phase 7: Summary

**Goal**: Document what was accomplished

**Actions**:
1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made
   - Files modified
   - Suggested next steps

---

## Phase 8: Logging (Task Log + Changelog)

**Goal**: Record what happened with this task so it becomes a durable record — for reminders, learning from failure, and project tracking.

**When this runs**: On EVERY outcome — whether the feature was **completed**, **failed**, or **abandoned** — UNLESS the user gave a direct instruction not to log this task (e.g. "don't log this", "no worklog/changelog"). Reaching an end state, even an unsuccessful one, is itself worth recording.

There are two destinations, with different rules.

### 8a. Task log — always (records every outcome)

1. Locate the task log. Check, in order: `docs/TASK_LOG.md`, `TASK_LOG.md`, `WORKLOG.md`. Use the first that exists; otherwise create `docs/TASK_LOG.md`.
2. Prepend a new entry (newest first) capturing:
   - **Date** and a short **task title**
   - **Outcome**: `Completed` | `Failed` | `Abandoned`
   - **Summary**: what was attempted or built
   - For `Failed` / `Abandoned`: the **Reason** it stopped, and a **Lesson / next step** so the failure teaches something
3. Match the file's existing entry style if it already has one; otherwise use a simple, consistent format like the example below.

```
## 2026-07-19 — OAuth Google/GitHub sign-in
- **Outcome**: Failed
- **Summary**: Attempted an OAuth provider abstraction plus routes/middleware
- **Reason**: Provider callback conflicts with the existing session middleware
- **Lesson / next step**: Make session middleware provider-agnostic before retrying
```

### 8b. Changelog — successful, shipped work only

1. **Only if** the outcome is `Completed` and verified, also record it in the project changelog. Failed and abandoned work does NOT go in the changelog — release notes describe what shipped, not what was tried.
2. Locate the changelog: `CHANGELOG.md`, `CHANGELOG`, `docs/CHANGELOG.md`, `HISTORY.md` — first that exists; otherwise create `CHANGELOG.md` using the [Keep a Changelog](https://keepachangelog.com) convention with an `## [Unreleased]` section.
3. **Match the existing file's style exactly** (heading levels, bullet character, tense, and Added / Changed / Fixed grouping). Add **one** concise, user-facing entry under the unreleased section, and **avoid duplicates** — refine an equivalent existing entry rather than adding a second.

**Finally**: add any file you touched here to the Phase 7 list of modified files, and tell the user exactly what you logged and where.

**Keep entries short**: a line or two each — the task log is a running journal, the changelog is release notes.

---
