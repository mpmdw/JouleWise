# Native exporter confirmation — Sol seat 1 — 2026-11-08

**Verdict: HOLD.** Reviewed exporter `1088f0ad5` on
`align/2026-11-08-exporter-confirm-sol1`, with engine `de4a54db9` and recompute
`7b9d215ff`. The original six findings are closed, and the real-producer
synthetic e2e reaches `release_v4` **AGREE**. One remaining supplied-reference
validation failure needs a fix. No production implementation changed.

## Original findings

| Finding | Confirmation |
|---|---|
| F1: producer fields refused | Real `prepare()` output is accepted, including `extra_sentinels` and `admission_sha256`. |
| F2: all-null inventory hides captures | The committed finalized manifest is inspected even for empty inventories; either direction of census disagreement refuses. Genuine empty attempts and retries still export. |
| F3: stale incremental custody | Every landed attempt is rebound to commit/path/successor/session root and its record/manifest digests; every landed file is rehashed. Changed configured records and changed prior bytes refuse. |
| F4: optional reference digests | All four external references require exact `{path, sha256}`. Required window/member/DC references are checked against placed bytes. The new reference matrix exercises each missing-digest position separately. H1 below concerns a different, supplied record-source reference. |
| F5: terminal result plan ownership | A foreign result `plan_id` refuses; a digest-valid stale watchdog latch also refuses. H1 bypasses the additional latch check when its source cannot authenticate. |
| F6: W1 stages unchecked | The roster is checked against the registered W1 plan, including ordinal, role, run id, stage, pair, condition, seed and model. The former stage witness passes. |

## H1 — supplied watchdog authentication failures silently disable its check

**MEDIUM, functional/operator failure:** `scripts/export_v4_series.py:654–659`
catches `ValueError` from `record.source('watchdog_state')` and treats the
source as absent. That exception includes a supplied source's SHA mismatch,
missing Git blob, or malformed JSON. A stale/copied path/hash descriptor can
therefore bypass terminal evidence validation instead of refusing.

The committed synthetic witness
`TerminalCustody.test_present_watchdog_with_wrong_digest_cannot_disable_its_stale_latch`
supplies a stale latch. With its correct digest, the exporter refuses
`terminal_evidence_mismatch` (separate positive control). With a wrong digest,
`WindowRecord.source()` demonstrably raises `source SHA-256 mismatch`, but
the exporter succeeds and emits C1 in both layouts with the same terminal
result digest. Neither layout carries the failed watchdog reference for a
consumer to recheck. This needs no race or mutable live evidence.

**Fix:** distinguish an actually omitted optional source from a supplied
source that cannot authenticate. Refuse unreadable supplied watchdog evidence
with a fixed terminal/record refusal code; retain the plan/result/latch checks.
The required-property witness is intentionally red, without `expectedFailure`.
A full release of the mutated export was not run; the executed finding is
successful export of both layouts despite the known source authentication failure.

## Other requested surfaces

- **DC span:** the exporter supplies unmodified, digest-bound metadata/events
  and no `member_span_ns`. The pinned engine computes production
  `harvest.member_spans`; the recompute independently restates that hull.
  The production-byte/hull witness passes, including a hull longer than the Episode.
- **A27:** classification, engine member/battery/aggregate printers and recompute
  public projections were inspected; the seal witness and release comparator pass.
  Anchor-sabotage retains its anchor role. Raw inputs require the sealed workflow;
  this is no general information-flow certification.
- **Refusals:** the native e2e's 27 refusal tests pass. Additional prefix-extension
  probes check prior metadata/events/turns before the next window can land.

## Verification and limits

All unittest invocations use `python3.13 -X faulthandler -B -m unittest -v MODULE`,
one module/process at a time. Environment:

```sh
PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
TMPDIR=/private/tmp/exporter-confirm-sol1-tmp
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1
JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=1 JOULEWISE_BACKUP_ROOTS=
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
JW_SYNTHETIC_CUSTODY_FENCE=1 JW_SYNTHETIC_CUSTODY_REPO="$PWD"
JW_SYNTHETIC_CUSTODY_TEMP=/private/tmp
PYTHONPATH="$PWD/tests/align/synthetic_custody_child:$PWD"
```

| Module | Result |
|---|---|
| `tests.v4_release.test_exporter_e2e` | 36 pass, including release AGREE; 397.359 s |
| `tests.v4_export.test_review_sol1` | 8 pass; 35.968 s |
| `tests.v4_export.test_review_sol2` | 11 pass, including A27/DC/stage; 65.176 s |
| `tests.v4_release.test_exporter_units` | 15 pass; 0.312 s |
| `tests.v4_export.test_confirm_sol1` | 3 pass, 1 intentional required-property failure (H1); 13.423 s |

The first e2e invocation used shared `/private/tmp`: 27 tests passed, but the
other class failed setup with `FileExistsError` at synthetic
`gen/w1/pilot7/pilot7-reference-x` (212.682 s). The unprotected shared fixture
cache is a plausible collision source; no competing process was inspected.
The isolated rerun is the green result above. No cache implementation changed.

My initial seat-1 invocation supplied the e2e's four-attempt config to a module
expecting three: six tests passed, two retry controls failed (43.169 s).
The final run supplied `windows[:3]` through `JW_V4_SOL1_SYNTHETIC_CONFIG`;
all eight passed. The confirmation module also ran before making its reference
list independent of the implementation (same result, 14.172 s). Total test time
including all invocations: **782.261 s (13 min 2 s)**. AST parsing and
`git diff --cached --check` pass.

No network, model downloads, full suite, real measurement/custody access,
coordination-state edits, new kernel tasks, subagents, push or merge. No MLX
code changed or native hardware validation ran. The lead retains live gates.

**Next exact step:** fix H1, make the new required-property witness green,
then rerun the focused exporter modules and real-producer release e2e at the
same pins. No new scientific ruling is needed to reject a supplied bad digest.
