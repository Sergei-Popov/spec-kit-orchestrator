Read these files for context:
- `.specify/memory/constitution.md`
- `specs/{active_feature}/spec.md`
- `specs/{active_feature}/plan.md`
- `specs/{active_feature}/tasks.md`
- `.specify/orchestrator/orchestrator-config.yml`

Analyze tasks.md and create work packages:
1. Group related tasks by domain (3-8 tasks per package).
2. Assign to agent roles: architectural tasks → Architect, source code → Code Agent, test files → Test Agent, review → Review Agent.
3. Respect dependency order: models → services → endpoints → tests → review.
4. Mark parallel-safe packages (no shared files).
5. Organize into phases: Foundation → Implementation → Verification → Quality Gate.

Generate `specs/{active_feature}/agent-coordination.yml` with:
- work_packages: list of {id, title, agent, tasks, dependencies, priority, status, user_stories}
- execution_phases: list of {phase, name, packages, type: sequential|parallel}

Present the plan as a summary table. In supervised/semi-auto modes, wait for approval.

$ARGUMENTS
