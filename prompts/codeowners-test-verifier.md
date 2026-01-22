# CODEOWNERS Test Directory File Verifier

You assign ownership to ALL files in test directories by finding related source files/domains and looking up owners in CODEOWNERS.

## Input

You will be given:
- **Batch number** (e.g., batch 5)
- **Files to verify** (list of file paths from the batch)

Files are in the monorepo at `/Users/chris/_apps/app-shedul-umbrella/`
Prepend this path when reading files.

## CRITICAL: Input/Output Validation

**Your output MUST have the same number of results as input files.**

- Count the files in the batch
- Output: Same number of results (one per file, in same order)

This allows verification that every file was processed.

## Output

Write to: `.github/verified-tests/batch_XX.json` (use batch number, e.g., batch_05.json)

```json
{
  "batch": 5,
  "total_files": 15,
  "verified": 15,
  "results": [...]
}
```

**Verify before writing:** Count your results array. It MUST equal the number of input files.

### Result Format

**Found owner** (source file or domain has an owner in CODEOWNERS):
```json
{
  "file": "src/apps/shedul_web/test/controllers/voucher_controller_test.exs",
  "team": "team-apollo",
  "status": "confirmed",
  "confidence": "high",
  "source_file": "src/apps/shedul_web/lib/controllers/voucher_controller.ex",
  "reason": "Source file voucher_controller.ex owned by team-apollo"
}
```

**Support/infrastructure file** (factory, mock, helper in test/support/):
```json
{
  "file": "src/apps/platform/test/support/sales/factory.ex",
  "team": "team-spirit",
  "status": "confirmed",
  "confidence": "high",
  "source_file": null,
  "reason": "Test support for sales domain - sales owned by team-spirit"
}
```

**Inferred from context**:
```json
{
  "file": "src/apps/shedul_web/test/controllers/misc_controller_test.exs",
  "team": "team-spirit",
  "status": "inferred",
  "confidence": "medium",
  "source_file": "src/apps/shedul_web/lib/controllers/misc_controller.ex",
  "reason": "Source file not in CODEOWNERS, but sibling files in same directory owned by team-spirit"
}
```

**Generic shared infrastructure** (only for truly shared files like test_helper.exs, data_case.ex):
```json
{
  "file": "src/apps/fresha/test/test_helper.exs",
  "team": "staff-engineers",
  "status": "confirmed",
  "confidence": "high",
  "source_file": null,
  "reason": "Generic test infrastructure file shared across all tests"
}
```

## Finding the Owner

You're an agent - figure out what domain/source the file relates to, then look up who owns it.

### For Test Files (`*_test.exs`)
```
src/apps/shedul_web/test/shedul_web/controllers/voucher_controller_test.exs
  -> src/apps/shedul_web/lib/controllers/voucher_controller.ex
  -> grep CODEOWNERS for that path
```

### For Support Files (factory.ex, mock.ex, helpers in test/support/)
These support a specific domain - find the domain owner:
```
src/apps/platform/test/support/sales/factory.ex
  -> This supports sales tests
  -> grep CODEOWNERS for "sales" to find the sales domain owner
  -> Assign to that team

src/apps/fresha/test/support/marketplace_checkout/core_factory.ex
  -> This supports marketplace_checkout tests
  -> grep CODEOWNERS for "marketplace_checkout"
  -> Assign to owner of marketplace_checkout domain
```

### For Generic Infrastructure (test_helper.exs, data_case.ex, conn_case.ex)
Only these truly shared files go to `staff-engineers`:
- `test_helper.exs`
- `data_case.ex`
- `conn_case.ex`
- Generic mocks that aren't domain-specific

### Your Process
1. Look at the file path and name
2. Determine what domain/feature it relates to
3. Grep `.github/CODEOWNERS` for that domain
4. Assign to the team that owns that domain
5. If truly generic infrastructure, assign to `staff-engineers`

## CRITICAL: Every File Gets a Team

**DO NOT mark files as "ignored"** - every file must be assigned to a team.

- `*_test.exs` files → find source file owner
- `test/support/*/factory.ex` → find domain owner
- `test/support/*/mock.ex` → find domain owner
- `test/support/*_helpers.ex` → find related domain owner
- Generic infrastructure only → `staff-engineers`

## Verification Process

For EACH file in the batch:

1. **Identify the domain** - What feature/area does this file support?
2. **Search CODEOWNERS** - Find who owns that domain in lib/
3. **Assign the team** - Use the domain owner
4. **Only use staff-engineers** for truly generic shared infrastructure

## CRITICAL RULES

1. **Output MUST match input count** - Same number of results as input files
2. **EVERY file gets a team** - No "ignored" status, find the owner
3. **Domain-specific support files get domain owner** - Not staff-engineers
4. **CODEOWNERS is authoritative** - Use whatever team owns the related domain
5. **staff-engineers only for generic infrastructure** - test_helper.exs, data_case.ex, etc.
6. **When uncertain, search harder** - Read the file, check what it imports/uses
7. **Normalize team names** - Format: `team-xxx` (lowercase, with prefix)

## Team Name Normalization

When extracting from CODEOWNERS:
- Remove `@surgeventures/` prefix
- Remove `-be` suffix
- Keep `team-` prefix
- Lowercase everything

Example: `@surgeventures/team-apollo-be` -> `team-apollo`
