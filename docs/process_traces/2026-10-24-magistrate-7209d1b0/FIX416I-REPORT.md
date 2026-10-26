```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Custody smoke witness and legacy fallback implemented; pre-collection NULL replay needs a lead ruling.",
  "workspace": {
    "base_requested": "7a3b585db",
    "base_mode": "exact",
    "head_start": "7a3b585db737209449bcc82aadb026f661e3d512",
    "head_end": "7a3b585db737209449bcc82aadb026f661e3d512",
    "upstream_end": null,
    "branch": "integrate/2026-10-24-416"
  },
  "pathspec": [
    "configs/gates/hazard_refusals.json",
    "joulewise/b6/export_runs.py",
    "joulewise/b6/smoke.py",
    "tests/b6/test_export_runs.py",
    "tests/b6/test_smoke.py"
  ],
  "unowned_dirty": [
    ".scratch-416C/",
    ".scratch-416E/",
    ".scratch-416F/",
    ".scratch-416G/"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/fix416i/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_export_runs tests.b6.test_smoke tests.b6.test_chain_smoke_reduction tests.hazards.test_refusal_allowlist tests.test_bytes_gates tests.test_fix573i_restore",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 140 tests in 75.098s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 140 tests"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/fix416i/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416i/main/scripts/witness_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "WITNESS PROBE PASS: FIXTURE WITNESS EXPORTS 19 REMOVED REFERENCES; LEGACY EXPORTS UNWITNESSED; INCONSISTENT AND DIGEST-MISMATCH STOP"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WITNESS PROBE PASS:"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=/private/tmp/fix416i/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416i/main/scripts/replay_archives.py --retry",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "TOTAL 25 REAL STOPS 1 CSV IDENTICAL 24 SIDECAR IDENTICAL 24; 13 BYTES SMOKES STOPS 0 UNWITNESSED 13; REAL SOURCE METADATA UNCHANGED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "TOTAL 25 REAL STOPS 0 CSV IDENTICAL 25 SIDECAR IDENTICAL 25; 13 BYTES SMOKES STOPS 0 UNWITNESSED 13; REAL SOURCE METADATA UNCHANGED"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/fix416i/main JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /private/tmp/fix416i/main/scripts/plain_membership_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PLAIN MEMBERSHIP PROBE PASS: BEFORE OMITTED; AFTER STOPS; ACCEPTANCE EXCLUSION PRINTS UNCOLLECTED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PLAIN MEMBERSHIP PROBE PASS:"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the unconditional planned-reference union stops the real NULL archive h2-20261023T051434Z, which has no roster or bundles and only window exclusions. This conflicts with the required 25 zero-stop byte-identical exports.",
      "needs": "Authorize an authenticated pre-collection NULL exception preserving the empty export, accept the 24/25 result, or provide another ruling."
    }
  ]
}
```

## Change

**NEEDS_RULING:** the requested changes are implemented and uncommitted. The 25/25 zero-stop acceptance bar conflicts with the unconditional plain-path hardening on the pre-collection NULL archive. No exception was invented.

- `joulewise/b6/smoke.py:272`: preserve the pinned clone’s exact pre-reduction bytes beside the reduced tree and commit the witness with the smoke pack. Before: the only full tree was an incidental default-branch results clone. After: preparation owns the witness; the fixture proves it matches `git show <pin>:.../plan_tree.json` even when the claim working tree is dirty.
- `joulewise/b6/export_runs.py:144`: accept only the two archived pack witness locations, verify SHA256SUMS and reproduce reduction. Results-clone trees are ignored. Without a witness, keep the surviving-stage beyond-keep behavior and disclose removed stage ids; `:566` forces non-claim and `:754` writes the sidecar note. Relative archive paths, witnesses missing despite inventory entries, unlisted or dangling witnesses, and invalid compressed witnesses retain storage stops.
- `joulewise/b6/export_runs.py:206`: union planned reference ids on the plain path too. The before/after fixture probe exports zero rows for the lost reference before the patch, stops afterward, and prints one uncollected row with blank request columns when acceptance excludes it. `tests/b6/test_export_runs.py:623` covers the same rule. H and BY-H2 have 123/123 and 73/73 planned/roster ids, with no differences.
- `joulewise/b6/export_runs.py:481`: restore the epoch-float noise-floor acknowledgement and the lead’s ceiling ruling, and state that powermetrics does not take this path. The 0.13 mJ bar is unchanged.
- `configs/gates/hazard_refusals.json:3245`: update the four membership entries’ protection text and the changed witness refusal name/guard. No new explicit collection refusal site was added; the NULL replay exposes a new stop through the broadened plain-path membership rule. Preparation/export integration coverage is in `tests/b6/test_smoke.py:176`; witness and fallback coverage is in `tests/b6/test_export_runs.py:475`.

**Witness probe** (APFS clone of real r1-alpha; fixture witness seeded from a tree that reproduces the reduced tree; production pin provenance is proved separately by the preparation fixture):

| Case | Result | Rows | Uncollected | Removed-stage rows | Sidecar |
|---|---|---:|---:|---:|---|
| before-control | exported | 27 | 23 | 19 | — |
| before-no-default-tree | stopped | — | — | — | — |
| with-witness | exported | 27 | 23 | 19 | — |
| no-witness | exported | 8 | 4 | 0 | unwitnessed |
| inconsistent-witness | stopped | — | — | — | — |
| digest-mismatch | stopped | — | — | — | — |

The old missing-default-tree cause is `ValueError: missing or inconsistent archived registered tree`. The retained present-witness causes are `ValueError: inconsistent archived registered tree witness` and `ValueError: SHA256SUMS digest mismatch`, each carried by a desk-side `StorageStop`. Full paths and exceptions are in `witness-results.json`.

**Real-plan replay** (fresh starting-module vs final-module exports, same per-archive blinding keys; equality is exact CSV and session-sidecar bytes):

| Archive | Before rows | After rows | Stops | CSV / sidecar identical |
|---|---:|---:|---:|---|
| H | 123 | 123 | 0 | yes / yes |
| BY-H2 | 73 | 73 | 0 | yes / yes |
| r1-alpha-smoke-0 | 4 | 4 | 0 | yes / yes |
| r1-beta-smoke-0 | 4 | 4 | 0 | yes / yes |
| r1-gamma-smoke-0 | 6 | 6 | 0 | yes / yes |
| r2-alpha-smoke-0 | 4 | 4 | 0 | yes / yes |
| r2-beta-smoke-0 | 4 | 4 | 0 | yes / yes |
| r2-gamma-smoke-0 | 6 | 6 | 0 | yes / yes |
| r3-alpha-smoke-0 | 4 | 4 | 0 | yes / yes |
| r3-beta-smoke-0 | 4 | 4 | 0 | yes / yes |
| r3-gamma-smoke-0 | 6 | 6 | 0 | yes / yes |
| r4-alpha-smoke-0 | 4 | 4 | 0 | yes / yes |
| MT-20261016T2114Z smoke | 4 | 4 | 0 | yes / yes |
| MT-20261017T1735Z smoke | 4 | 4 | 0 | yes / yes |
| MT-20261017T2215Z smoke | 4 | 4 | 0 | yes / yes |
| r1-alpha session | 125 | 125 | 0 | yes / yes |
| r1-beta session | 125 | 125 | 0 | yes / yes |
| r1-gamma session | 107 | 107 | 0 | yes / yes |
| r2-beta session | 125 | 125 | 0 | yes / yes |
| r2-gamma session | 107 | 107 | 0 | yes / yes |
| r3-alpha session | 125 | 125 | 0 | yes / yes |
| r3-beta session | 125 | 125 | 0 | yes / yes |
| r3-gamma session | 107 | 107 | 0 | yes / yes |
| r4-alpha session | 125 | 125 | 0 | yes / yes |
| BY-H2 pre-collection NULL | 0 | — | 1 | blocked |

**Forced BYTES smoke replay** (all are existing witness-free archives; every successful sidecar is non-claim with `removed_stage_references: "unwitnessed"` and the exact reduction `removed` ids):

| Smoke | Rows | Uncollected | Populated reference requests | Stops |
|---|---:|---:|---:|---:|
| r1-alpha-smoke-0 | 8 | 4 | 2 | 0 |
| r1-beta-smoke-0 | 8 | 4 | 2 | 0 |
| r1-gamma-smoke-0 | 10 | 4 | 2 | 0 |
| r2-alpha-smoke-0 | 8 | 4 | 1 | 0 |
| r2-beta-smoke-0 | 8 | 4 | 2 | 0 |
| r2-gamma-smoke-0 | 10 | 4 | 2 | 0 |
| r3-alpha-smoke-0 | 8 | 4 | 2 | 0 |
| r3-beta-smoke-0 | 8 | 4 | 2 | 0 |
| r3-gamma-smoke-0 | 10 | 4 | 2 | 0 |
| r4-alpha-smoke-0 | 8 | 4 | 2 | 0 |
| MT-20261016T2114Z smoke | 6 | 4 | 0 | 0 |
| MT-20261017T1735Z smoke | 8 | 4 | 0 | 0 |
| MT-20261017T2215Z smoke | 8 | 4 | 1 | 0 |

Full paths, plan SHA-256, CSV/sidecar SHA-256 and counts: `replay-results.json`. Real archive file sizes, mtimes and modes are unchanged across the replay; source hash bindings are `replay-source.json` and `witness-source.json`.

**Decisions made:** use a witness beside the reduced pack tree, so existing harvest copies it without a new plan/harvest contract; preserve exact pinned bytes rather than reserializing; use `removed_stage_ids` for the reduction’s full removed list; force unwitnessed exports non-claim; require all present custody witness candidates to agree; do not use any results-clone copy as an export candidate; do not exempt NULL archives without a ruling.

**Exact §6 sentences for the lead** (the plain-path sentence is subject to the NULL ruling; do not claim 25 zero-stop replays yet):

Each planned reference on the plain path is included in the harvest membership check even when its roster entry is absent; without collected bytes it must have an acceptance member exclusion or the desk export stops with its cause.

For a smoke, smoke.prepare preserves the pinned checkout's exact pre-reduction plan_tree.json bytes as smoke-registered-tree.json beside the reduced tree; harvest archives this custody-owned witness and lists its digest in sources/SHA256SUMS. The exporter uses only this witness to recover the complete registered stage walk, including stages removed by keep 0, verifies its archived digest, and requires reduce_tree(witness, smoke_reduction.keep) to equal the archived reduced tree. Results-clone copies are never candidates because they follow origin's default branch rather than the pinned claim checkout.

When the witness is absent, the non-claim smoke export continues: references belonging to surviving stages retain the smoke keep rule and print uncollected beyond the kept prefix with blank request columns; references of removed stages are not enumerated, and the session sidecar records removed_stage_references: "unwitnessed" and removed_stage_ids from the reduced tree's smoke_reduction.removed record. A witness that is present but unlisted, missing despite an inventory entry, digest-invalid, malformed or inconsistent with the reduced tree stops desk export with its storage cause. Roster or assessment success still denies an uncollected exception.

Replayed through the BYTES branch, all 13 existing block-6 smokes export without a witness and disclose their removed stage ids as unwitnessed. An archive-clone fixture with a witness restores and prints the 19 removed-stage references as uncollected with blank request columns; removing that witness continues export with the sidecar disclosure, while digest mismatch or reduction inconsistency stops with its cause.

**Final SHAs**

HEAD start/end and remote integration ref: `7a3b585db737209449bcc82aadb026f661e3d512`. No commit, push or branch operation was performed in this worktree; source changes remain uncommitted.

| File | SHA-256 |
|---|---|
| `configs/gates/hazard_refusals.json` | `594e2f24a01f11c08628eee2e1d6a01dad2756887523c7c7c11d0100b0f57b5f` |
| `joulewise/b6/export_runs.py` | `6df129e8c7c2e97fe18f1696a2f3d38fe19b5832d96f0e6ab6f7ea32415d1a0d` |
| `joulewise/b6/smoke.py` | `436f3b16199ec8ee9cbcbacc83fccc507e5c1ced4effab94772b68c73fbf78b1` |
| `tests/b6/test_export_runs.py` | `cb31512aaea0d25610e84831c04724e3d60788d127a3a58667bd8f3d3e676355` |
| `tests/b6/test_smoke.py` | `52e92746de144fbe42759df242a9a737365b776bbda0a50676b5b510ccc631ba` |

## Verification notes

- Full unittest discovery was not run; this bounded seat used the requested suites and no live/model lane.
- The first scratch replay harness resolved baseline registration relative to the copied module under TMPDIR. It was corrected to use the real source location for `__file__`, then rerun. Earlier harness logs are retained; the final table uses only the corrected replay.
- The initial replay source-binding assertion rejected the source updates made during its run. All 38 cases were rerun after freezing the source; the final tables use that rerun, and both replay/probe source manifests match the final file hashes.
- All outputs, fixtures and APFS clones are under `/private/tmp/fix416i/main`. Real archives were read only. Free disk stayed 69 GiB, above the 60 GiB gate. No live arm, runner, night or smoke command, model load, or forbidden machine command was run. Unowned scratch directories were preserved.
- The lead owns registration edits, bookkeeping, final verification and commits. Those paths were not modified.

## Residual risk

**NEEDS_RULING question:** should `/Users/edr/night-bytes/h2-20261023T051434Z/archive`, the authenticated pre-collection NULL archive, retain its empty export despite having no member exclusions, or should the plain-path rule stop it?

**Options considered:** (1) a narrowly authenticated NULL exception; (2) retain the unconditional rule and accept 24/25; (3) another lead-specified rule. **Recommendation:** (1), preserving the existing no-collection result while retaining the hardening for collected archives. The archive’s digest-verified exclusions say `status: "NULL"`, `claim_usable: false`, reason `window.null`; its digest-verified flags record `records.window_not_launched` at the census. **Blocked work:** implementing any exception and satisfying the 25/25 bar. **Next exact step:** the lead rules on this case, then resumes this seat or applies the ruling and reruns V1–V3 before committing.
