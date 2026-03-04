---
agent: speckit.orchestrate-status
name: 'speckit.orchestrate-status'
description: "Orchestration Status — displays current progress of the orchestrated development workflow"
---

Read `specs/{active_feature}/orchestrator-state.yml` and
`specs/{active_feature}/agent-coordination.yml`.

Display:
- Feature name
- Current phase (N/total)
- Per work-package: status icon, agent, task progress
- Overall progress percentage
- Active blockers or errors

If no state file exists, tell user to run /speckit.orchestrate-init first.
Read-only — do not modify any files.

$ARGUMENTS
