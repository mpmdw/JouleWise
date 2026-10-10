```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Both test corrections are implemented and both modules pass; the production-file mutation proof requires scope expansion.",
  "workspace": {
    "base_requested": "d435547e2d335ec75a90ad7a6558ada91074a6fb",
    "base_mode": "exact",
    "head_start": "d435547e2d335ec75a90ad7a6558ada91074a6fb",
    "head_end": "d435547e2d335ec75a90ad7a6558ada91074a6fb",
    "upstream_end": "d435547e2d335ec75a90ad7a6558ada91074a6fb",
    "branch": "lane/2026-10-10-harvest-screen-sources"
  },
  "pathspec": [
    "tests/test_harvest_b5_sources.py",
    "tests/test_analysis_integration.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the requested mutation proof would temporarily modify a production path outside WRITE_SCOPE. No out-of-scope write occurred.",
      "needs": "Resume with prospective scope expansion for joulewise/b5/harvest.py, or perform the mutation proof at the lead bench."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["joulewise/b5/harvest.py"],
    "reason": "The prescribed mutation-and-restoration proof requires writing this production file.",
    "blocked_work": "Run the mutated module and demonstrate both named tests fail, restore the production file byte for byte, then rerun successfully.",
    "minimal_change": "Temporarily remove recovery from the single clean-bound condition, then restore the original bytes."
  }
}
```

## Change

- **test_harvest_b5_sources.py:** Both named tests now set `neg8_clean_bound_required = False` and `neg8_collected_bound = self.bound` before asserting refusal. This isolates the recovery-specific requirement.
- **test_analysis_integration.py:** Added the harvest catalog call, with the requested `joulewise.b5.harvest.claim_neg8_sources` / Erratum 2 item 1 comment; raised the total to eight. The existing `set(catalog_calls)` importer expectation incorporates the new importer. Manifest expectations already matched actual counts and remain unchanged.

Catalog counts, previous expectation → actual and corrected expectation:

| Path | Before | After |
|---|---:|---:|
| `joulewise/analysis_engine/inputs.py` | 2 | 2 |
| `joulewise/b5/harvest.py` | absent | 1 |
| `joulewise/whole_window.py` | 1 | 1 |
| `scripts/run_campaign.py` | 4 | 4 |
| **Total** | **7** | **8** |

Catalog importers gain only `joulewise/b5/harvest.py`. Manifest calls and importers remain `joulewise/whole_window.py` and `joulewise/b5/harvest.py`, one call each, total two. Exact dictionary assertions still reject further call sites.

## Verification notes

Created temporary storage:

```sh
mkdir .scratch-fix
```

Baseline integration command, before correction:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -m unittest tests.test_analysis_integration
```

Exit 1; sole failure was the call-site fence:

```text
FAIL: test_campaign_provenance_aggregation_call_site_fence (tests.test_analysis_integration.SupersessionAwareCooldownJoinTests.test_campaign_provenance_aggregation_call_site_fence)
Ran 116 tests in 77.752s
FAILED (failures=1)
```

After corrections:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_sources
```

Exit 0:

```text
Ran 51 tests in 1.114s
OK
```

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -m unittest tests.test_analysis_integration
```

Exit 0:

```text
Ran 116 tests in 77.108s
OK
```

**NEEDS_SCOPE:** The mutation proof was **not run**. The exhaustive allowlist prohibits even temporary writes to `joulewise/b5/harvest.py`. Independent authorized work is complete; the next step is a lead-issued scope expansion for that exact path or lead execution of the proof.

Final checks, all exit 0:

```sh
git diff --check
git diff --stat -- joulewise
rm -r .scratch-fix
test ! -e .scratch-fix
```

Both Git checks printed nothing. Scratch storage is deleted. Changes remain uncommitted; no background task remains.

`git status --short`:

```text
 M tests/test_analysis_integration.py
 M tests/test_harvest_b5_sources.py
```