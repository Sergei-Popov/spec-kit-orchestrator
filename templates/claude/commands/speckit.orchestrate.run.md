Read:
- `specs/{active_feature}/agent-coordination.yml`
- `.specify/orchestrator/orchestrator-config.yml`
- `.specify/orchestrator/agents/*.md`

If `specs/{active_feature}/orchestrator-state.yml` exists, resume from last completed package.

For each phase:
1. Sequential phases: execute packages one at a time, adopting the agent role from its prompt template.
2. Parallel phases: list all packages with their agent prompts. Ask user to run them in separate sessions. Wait for confirmation.
3. After each package: update orchestrator-state.yml.
4. After each phase: run tests, print progress summary.

Mode behavior:
- supervised: pause after each work package for approve/retry/abort.
- semi-auto: pause after each phase.
- autonomous: continue. Pause only on test failure or CRITICAL review finding.

After all phases: trigger review cycle.

$ARGUMENTS
