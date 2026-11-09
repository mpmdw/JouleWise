# Native exporter confirmation — Sol seat 2

**Verdict: HOLD.** Reviewed `1088f0ad5` on
`align/2026-11-08-exporter-confirm-sol2`, 2026-11-08 PST. Synthetic only.
The original six defect reproducers are addressed, and the normal real-producer
synthetic e2e reaches `release_v4` **AGREE**. One remaining terminal-custody
refusal bypass prevents admission. No production code was changed.

## CF1 — MEDIUM: invalid present watchdog evidence silently disables its check

`scripts/export_v4_series.py:654-662` catches errors reading
`record.source('watchdog_state')` and substitutes `None`. This includes a
committed-source SHA-256 mismatch and invalid JSON. A readable snapshot lacking
`released_terminal_windows` also skips the check. Thus invalid present evidence
is treated as optional absence.

The native witness in `tests/v4_export/test_confirm_sol2.py` copies the
synthetic record repository, preserving the finalized manifest, restored raw
custody, plan, result and adjudication. It commits a stale watchdog snapshot:

1. With the correct snapshot digest, C1 refuses `terminal_evidence_mismatch`.
2. Changing only that source descriptor's digest to an incorrect 64-hex value
   makes export succeed: **all 22 C1 captures land in both layouts**.

Separate tests use real `GitEvidence.source` reads of synthetic committed
blobs. A matching release latch passes and a validly hashed stale latch refuses;
a wrong digest, unparseable snapshot, or present snapshot without the release
field is accepted. Four required-property tests fail, without xfail decorators.

This is a plausible incomplete/stale snapshot or record-writer failure, not a
forgery/race argument. The watchdog latch proves the empty agent/driver/plan
process census (`docs/align/next_arm_packet.md:81-86`). The exporter can process
the latest C window without running the next-arm packet's stronger source and
terminal checks (`align_v4_next_arm_packet.py:643-671`). Both builds receive
the same accepted result, without the failed watchdog provenance. **No changed
numeric result or release verdict on this mutated input was established**; the
executed failure is admission to both input layouts despite invalid terminal
custody.

**Required fix:** authenticate a present watchdog source and refuse read/digest/
parse errors; require its snapshot shape, release list and exact current
`plan_id:custody_root:result_sha256` key. If genuine absence remains supported,
distinguish it from invalid present evidence. Then rerun the new witnesses and
the exporter e2e. This requires no change to the estimand or sealing policy.

## Confirmation of prior findings and remaining surfaces

| Lead finding | Confirmation at this head |
|---|---|
| F1 — normal producer fields | Closed: actual `prepare()` state accepted; native fixture now uses that producer projection. |
| F2 — all-null inventory | Closed: finalized manifest is read even for zero captures; custody/inventory are compared both ways. Honest zero capture and retry remain supported. |
| F3 — stale incremental custody | Closed: landed state rebinds commit, path, successor and session root; record/manifest digests and every recorded landed-file digest are checked on each invocation. Changed bindings/files refuse. |
| F4 — optional reference digests | Original external-reference defect closed: allocation/U3/R1/registration require exact `{path, sha256}`. Required output references cover raw/plan/terminal, Episode, plist, config, kit, journal, metadata, events, turns and DC streams. **Present watchdog-source authentication remains incomplete (CF1).** |
| F5 — result plan ownership | Original wrong-plan result defect closed: plan IDs must match; a readable release list must contain the current key. **The error/shape paths remain open (CF1).** |
| F6 — W1 stages | Closed: ordinal/role/run ID/stage/pair/condition/seed/model are checked against the registered W1 plan before projection. |

The pinned engine (`de4a54db9`) and recompute (`7b9d215ff`) each derive the DC
member hull from the digest-bound production metadata/events. The exporter
ships those exact bytes and no `member_span_ns`; the seat-2 production-hull
witness checks this. A27 roster classification remains allocation-derived;
scored C sabotage seals, while 30B anchor sabotage keeps its anchor treatment.
The seat-2 executing battery-seal control and normal release comparator pass.
No additional plausible shared-input or A27 bypass was established in this
bounded review. This is not exhaustive public-output noninterference proof.

## Verification and handoff

All test modules ran sequentially, one module per process, with:

```sh
env PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  TMPDIR=/private/tmp/exporter-confirm-sol2.irIb05 PYTHONNOUSERSITE=1 \
  PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1 JW_B5_SYNTHETIC_ONLY=1 \
  JW_WP22_FULL=1 JOULEWISE_BACKUP_ROOTS= GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 python3.13 -X faulthandler -B -m unittest -v MODULE
```

| Module | Result |
|---|---|
| `tests.v4_release.test_exporter_e2e` | 36 pass, 343.178 s; `test_release_agrees` exits 0 / AGREE. |
| `tests.v4_export.test_review_sol1` | 8 pass, 60.996 s; no skips/xfails. |
| `tests.v4_export.test_review_sol2` | 11 pass, 119.337 s; no skips/xfails, including A27/DC controls. |
| `tests.v4_release.test_exporter_units` | 15 pass, 0.411 s. |
| `tests.v4_export.test_confirm_sol2` | 6 tests, 2 pass / 4 required-property failures, 14.561 s; CF1 reproduced. |

Seat 1 used `JW_V4_SOL1_SYNTHETIC_CONFIG` pointing to a three-attempt prefix
of this seat's completed native fixture (the module's supported input hook).
The original fixture bytes were retained; mutation tests copied the records
repository. The confirmation and seat-1 fences both reported zero forbidden
custody accesses and zero redirected home-custody probes.

Total unittest time including the initial setup failure was 546.586 s
(about 9 min 7 s), below the brief's budget. The full suite was not run, per
the brief. `python3.13 -X faulthandler -m compileall -q joulewise tests`
passed with `PYTHONPYCACHEPREFIX` under the private TMPDIR; `git diff --check`
also passed. The required read-only fixture census
(`python3.13 -X faulthandler -B scripts/fixture_orphan_census.py --fail-on-orphans`)
exited 2 because sandbox `ps` returned `PermissionError: Operation not permitted`.
Rows/count are unavailable; this is not a clean census. No process was signalled.

The initial e2e using shared default `/private/tmp` failed in fixture setup
(0 tests, 8.103 s) because synthetic bundle files disappeared. A shared-cache
collision is suspected, not proven. The seat-private TMPDIR rerun above passed.

The native fixture uses the real synthetic world/controller, kits, thermal
desk, finalize/pack/unpack and WindowRecord reader. Its plist, meter, U3 bar and
R1 references are synthetic as disclosed by runbook §6a. No real measurement
data, sealed study outcomes, model weights, network or hardware validation was
used. No MLX code/tests changed; native MLX, SMC/KM003C and real Air/JW-EXT
validation remain outside this sandbox review.

Changed files: this report and `tests/v4_export/test_confirm_sol2.py`.
Coordination files/kernel tasks are untouched. No delegation, push or merge.
**Next exact step:** lead makes CF1 fail closed, gets all six confirmation
tests green, then reruns the prior witnesses and native exporter e2e at the
chosen final pins before admitting the exporter.
