Read:
- `.specify/memory/constitution.md`
- `specs/{active_feature}/spec.md`
- `specs/{active_feature}/plan.md`
- `specs/{active_feature}/orchestrator-state.yml`

Adopt the Review Agent role from `.specify/orchestrator/agents/review.md`.

For each completed work package (or specific one from arguments):
1. Read all files created/modified by the package.
2. Check against spec.md acceptance criteria.
3. Check constitution.md compliance.
4. Check code quality, security, error handling.
5. Produce review table: ID, severity, file, lines, issue, fix.
6. Verdict: APPROVE or REQUEST_CHANGES.

If REQUEST_CHANGES: record findings in state file, list tasks for Code Agent to redo, increment review round. If round > max: escalate to user.
If APPROVE: update package status to "reviewed" in state file.

$ARGUMENTS
