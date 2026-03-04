Read `specs/{active_feature}/agent-coordination.yml` and `specs/{active_feature}/orchestrator-state.yml`.

Find completed packages from the latest parallel phase. Check file declarations:
- (create: path): verify file exists.
- (update: path): check if multiple packages modified the same file.

No conflicts: confirm clean state, update orchestrator-state.yml.

Conflicts found:
1. List each conflicting file with the packages involved.
2. Show diff sections.
3. Offer: keep version A, keep version B, or manual merge.
4. Apply choice, update state.

After sync: run test suite to verify merged code.

$ARGUMENTS
