Read:
- `specs/{active_feature}/agent-coordination.yml`
- `.specify/orchestrator/orchestrator-config.yml`
- `.specify/orchestrator/agents/*.md`

If `specs/{active_feature}/orchestrator-state.yml` exists, resume from last completed package.

For each phase:
1. Sequential phases: execute packages one at a time, adopting the agent role from its prompt template.
2. Parallel phases: execute all eligible packages in parallel via delegated tasks and track their task/session IDs.
3. After each package: update orchestrator-state.yml.
4. After each phase: run tests, print progress summary.

After each phase, always pause for user confirmation before continuing.

After all phases: trigger review cycle.

$ARGUMENTS
