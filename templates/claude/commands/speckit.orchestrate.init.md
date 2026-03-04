Read `.specify/orchestrator/orchestrator-config-template.yml` and `.specify/memory/constitution.md`.

Using the user's input (or ask if not provided), configure:
1. Code agent count: 1-3
2. Quality gate thresholds (or accept defaults: 80% coverage, 3 max review rounds)

Generate `.specify/orchestrator/orchestrator-config.yml` with these settings.
After generating plan/spec/tasks, ask the user what to improve and apply corrections.
Then run team analysis and generate implementation checklist questions.
For each question provide exactly three options where option 3 is your recommended answer.
After answers are applied, confirm readiness and instruct the user to run `/speckit.orchestrate.run`.

$ARGUMENTS
