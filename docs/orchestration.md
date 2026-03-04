# Multi-Agent Orchestration Guide

## Overview

Spec Kit Orchestrator extends the standard spec-driven development workflow with multi-agent coordination. Instead of a single AI agent executing all tasks sequentially via `/speckit.implement`, orchestration distributes work across specialized sub-agents that operate in parallel with structured review cycles.

## When to Use Orchestration

| Scenario | Recommendation |
|----------|---------------|
| Small feature, < 10 tasks | Standard `/speckit.implement` |
| Medium feature, 10-30 tasks, single domain | Standard or orchestrated |
| Large feature, 30+ tasks, multiple domains | Orchestrated |
| Multiple developers working simultaneously | Orchestrated with parallel Code Agents |
| High compliance requirements | Orchestrated with supervised mode |

## Setup

### Option A: New project

```bash
specify init my-project --ai copilot --orchestrate
```

This installs standard spec-kit templates plus orchestration templates and slash commands.

### Option B: Existing spec-kit project

Run the orchestration init command in your AI assistant:

```text
/speckit.orchestrate.init Set up semi-auto mode with 2 code agents
```

## Workflow

### Prerequisites

Complete the standard spec-kit flow first:

```text
/speckit.constitution  →  Project principles
/speckit.specify       →  Feature specification
/speckit.plan          →  Technical plan
/speckit.tasks         →  Task breakdown
```

### Orchestration steps

```text
/speckit.orchestrate.init    →  Choose mode + team composition
/speckit.orchestrate.assign  →  Auto-generate work packages from tasks
/speckit.orchestrate.run     →  Execute packages per agent role
/speckit.orchestrate.status  →  Check progress anytime
/speckit.orchestrate.review  →  Run quality review cycle
/speckit.orchestrate.sync    →  Merge parallel outputs
```

## Autonomy Modes

### Supervised

The orchestrator pauses after **every work package** and asks you to approve, retry, or abort. Best for: learning the system, high-risk features, regulated environments.

### Semi-auto

The orchestrator pauses after **each phase** (not each package). Within a phase, agents work without interruption. Best for: most projects, balanced control and speed.

### Autonomous

The orchestrator runs end-to-end without pausing. It only stops on test failures or CRITICAL review findings. Best for: well-tested codebases, experienced teams, prototyping.

## Agent Roles

### Orchestrator (you + AI assistant)

The AI assistant running the `/speckit.orchestrate.*` commands acts as the orchestrator. It reads the coordination plan, assigns work, tracks state, and manages review cycles. You provide oversight based on the autonomy mode.

### Architect Agent

Reviews architecture before implementation starts. Validates plan.md against constitution.md. Proposes refactoring when structural issues arise. Does NOT write implementation code.

### Code Agent

Implements tasks from assigned work packages. Follows file markers from tasks.md. Reports blockers to the orchestrator. Multiple instances can run in parallel on independent packages.

### Test Agent

Generates tests from spec.md acceptance criteria and API contracts. Runs the test suite after each implementation phase. Reports coverage against configured thresholds.

### Review Agent

Reviews completed work packages for constitution compliance, spec compliance, code quality, and security. Issues APPROVE or REQUEST_CHANGES verdicts. Maximum 3 rounds per package.

## File Reference

| File | Location | Purpose |
|------|----------|---------|
| `orchestrator-config.yml` | `.specify/orchestrator/` | Team and mode configuration |
| `agent-coordination.yml` | `specs/NNN-feature/` | Work package assignments and phases |
| `orchestrator-state.yml` | `specs/NNN-feature/` | Live execution state |
| `orchestrator.md` | `.specify/orchestrator/agents/` | Orchestrator role prompt |
| `architect.md` | `.specify/orchestrator/agents/` | Architect role prompt |
| `code.md` | `.specify/orchestrator/agents/` | Code Agent role prompt |
| `test.md` | `.specify/orchestrator/agents/` | Test Agent role prompt |
| `review.md` | `.specify/orchestrator/agents/` | Review Agent role prompt |

## Running Parallel Agents in Practice

When `/speckit.orchestrate.run` reaches a parallel phase, it lists the work packages and their agent prompts. To run them simultaneously:

1. **VS Code:** Open multiple Copilot Chat panels (split view). Paste each agent's package prompt into a separate panel.
2. **Claude Code:** Open multiple terminal sessions. Run each package in its own session.
3. **Cursor:** Use multiple composer windows.

After all parallel packages complete, confirm in the orchestrator session and run `/speckit.orchestrate.sync` to merge results.

## State Recovery

If your session is interrupted, orchestrator-state.yml persists on disk. Running `/speckit.orchestrate.run` again automatically resumes from the last completed work package. No special flags needed.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No orchestrator config found" | Run `/speckit.orchestrate.init` first |
| "No tasks.md found" | Complete `/speckit.tasks` before orchestrating |
| Review cycle stuck in loop | Check max_review_rounds in config, increase or escalate manually |
| File conflicts after parallel phase | Run `/speckit.orchestrate.sync` to resolve |
| State file corrupted | Delete `orchestrator-state.yml` and re-run — starts from beginning |
