Read `.specify/orchestrator/orchestrator-config-template.yml` and `.specify/memory/constitution.md`.

Using the user's input (or ask if not provided), configure:
1. Autonomy mode: supervised | semi-auto | autonomous
2. Code agent count: 1-3
3. Quality gate thresholds (or accept defaults: 80% coverage, 3 max review rounds)

Generate `.specify/orchestrator/orchestrator-config.yml` with these settings.
Confirm configuration with a summary table.
Next step: /speckit.orchestrate.assign

$ARGUMENTS
