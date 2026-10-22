## PROGRESS

- Done (slice 1): finding 2 committed-fixed input/provenance, missing/malformed unavailable behavior, measured-unused disclosure; finding 7 exact measured_c assertion and imported WAIT constant.
- Verified: 18 bytes_gates tests and 6 plan_inputs tests pass. Real augmented H main exits 2, writes /tmp/byc5f1/C5.json; all 12 P values exactly equal the director's committed-fixed targets. Reviewer re-derivation agrees. Sealed diff is empty.
- Next: finding 1 shared disk validation + PRECHECK P + smoke retention decision and boundary tests; finding 3 stopped-before-model main test; finding 6 smoke metadata; finish findings 4/8 report revisions and importer checks. Planner equality on all 12 updated P values remains to run.
- Open: director owns real replay, commits/push and PR #547 CI. No real session trees read. All edits uncommitted, local by-c5 HEAD cf716ce00bf7341a1a62e3a2e96206f23f3eb013. Intake disk available 44 GiB (>25 GiB gate).
- Evidence /tmp/byc5f1/: C5.json, H-C5.stdout, rederive.log, step1-tests.log, plan-inputs-tests.log, sealed.log. run.py gives each invocation a fresh TMPDIR and deletes it afterward.

## SUMMARY

Fix round in progress; not complete.
C5 now uses H's committed 4,046,531,103 B fixed-artifact allocation.
The measured 1,266,544,640 B partial-session allocation is labelled unused disclosure.
The committed source path, SHA-256 and JSON pointer are recorded in C5.
Missing or malformed committed fixed input makes all disk lines unavailable, never a measured fallback.
All twelve augmented-H P values match the director's exact byte targets.
Finding 7 is fixed; findings 1/3/6 and final report/check work remain.

## FIX LOG

| Finding | Disposition / evidence |
|---|---|
| 1 major | Pending: PRECHECK shared helper, smoke accounting, twelve-pack boundaries and reviewer probe. |
| 2 major | Code fixed in bytes_gates.committed_fixed/calculate/main. GatesTests.test_committed_fixed_source_override_and_missing_never_fallback checks integer delta, provenance, invalid types, missing CLI input and no fallback. Real H targets agree; planner equality pending. |
| 3 minor | Pending stopped-before-model main repro and unavailable dependent lines. |
| 4 minor | Form unchanged as directed; final R6 text/sensitivity disclosure pending. |
| 5 nit | No change needed: maximum of two whole summed bases; reviewer rederive confirms stated deltas. |
| 6 nit | Pending smoke metadata native requirement. |
| 7 nit | Fixed: ReplayTests.test_nine_plus_h_replay_and_integer_boundaries uses exact int/int equality; plan_inputs imports SESSION_WAIT_BUDGET_S from sealed plan, unchanged. |
| 8 nit | Partial report correction; full final report refresh pending. Scope grant acknowledged for native raw-byte producer. |
| BY-MERGE | No change needed in this lane; hand-forward recorded below. |

## PRECHECK END TO END

Pending finding 1.

## P PER SUB-PACK (committed fixed)

Source: configs/campaigns/bytes_mac_check/registration/sizing_b5.json at /packs/bytes-mac-check/disk_derivation/fixed_retained_bytes.
Real H C5 input and exact rational allowances are preserved in /tmp/byc5f1/C5.json; stdout /tmp/byc5f1/H-C5.stdout.
Rates r_s=1,805,538.5168827055 B/s; r_w=1,285,759.0452694688 B/s.
WAIT=12,999,877,322 B; committed fixed=4,046,531,103 B; measured fixed unused=1,266,544,640 B.
c=2; measured c=0.8020750916018277 (disclosure).

| pack | stream basis | wall basis | B | P | planner equality |
|---|---:|---:|---:|---:|---|
| bytes-s1-p1 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | pending updated-P run |
| bytes-s1-p2 | 21883930645 | 21697490999 | 21883930645 | 73814147037 | pending updated-P run |
| bytes-s2-p1 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | pending updated-P run |
| bytes-s2-p2 | 22841465166 | 22967763886 | 22967763886 | 75981813519 | pending updated-P run |
| bytes-s3-p1 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | pending updated-P run |
| bytes-s3-p2 | 24053464961 | 24709054674 | 24709054674 | 79464395095 | pending updated-P run |
| bytes-s4-p1 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | pending updated-P run |
| bytes-s4-p2 | 27547300445 | 26855538139 | 27547300445 | 85140886637 | pending updated-P run |
| bytes-s5-p1 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | pending updated-P run |
| bytes-s5-p2 | 22901363715 | 21700998244 | 22901363715 | 75849013177 | pending updated-P run |
| bytes-s6-p1 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | pending updated-P run |
| bytes-s6-p2 | 14585071383 | 16382541368 | 16382541368 | 62811368483 | pending updated-P run |

Reviewer rederive command (exit 0):
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/rederive.log /Users/edr/night-archive/forward-20261021/BY-C5/review-r1/rederive.py /Users/edr/code/JouleWise-by-c5 /tmp/byc5f1/MEASUREMENTS.raw.json /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv 4046531103`
Compare P_committed_fixed column; its P column deliberately uses measured-fixed as the old baseline.

## STOPPED-EARLY C5

Pending finding 3. Real H main exits 2 because completeness and thermal lines fail (thermal_level 1), not a program fault.

## TESTS RUN

All runs set JW_B5_SYNTHETIC_ONLY=1 and PYTHONDONTWRITEBYTECODE=1, use /opt/homebrew/bin/python3.13 -B, and get a fresh /tmp/jwtmp-byc5f1.* TMPDIR removed after completion.

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B -c '<temporary-directory subprocess runner>'`: child `-m unittest tests.test_bytes_gates`; 18 tests, 3.040 s, exit 0, no skips/environment failures, /tmp/byc5f1/step1-tests.log.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/plan-inputs-tests.log -m unittest tests.b6.test_plan_inputs`: 6 tests, 0.017 s, exit 0, no skips/environment failures.
- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B /tmp/byc5f1/run.py /tmp/byc5f1/H-C5.stdout scripts/bytes_gates.py --runs /tmp/byc5f1/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/byc5f1/MEASUREMENTS.raw.json --disk-evidence /tmp/byc5f1/disk_h.json --out /tmp/byc5f1/C5.json`: exit 2, JSON written, all twelve exact expected byte targets pass.
- `git diff --check`: exit 0.

## SEALED INVENTORY

Command: `git diff --name-only bda481d5a -- <all 682 keys of configs/campaigns/v5_claim_25g83/sealed_inventory.json files>`; exit 0, empty stdout (also includes uncommitted work). Log /tmp/byc5f1/sealed.log.

## DECISIONS I MADE

- Director disposition 2 supersedes old which-text-wins item 5: fixed comes solely from committed H sizing. --committed-sizing can override the file, with identical pointer/type validation; no measured fallback.
- Missing/malformed committed fixed is disk.committed_fixed_missing, a desk flag; no new refusal site or harvested flag catalog entry.
- Finding 7 exact measured_c equality is bit identity of the same integer division. WAIT imports the sealed constant; no sealed source edits.
- Keep C5's member-wall form and maximum of two whole summed bases as instructed; report details still pending.
- Local-route prohibition on Git writes overrides commit/push rules. Director should commit this slice as `BY-C5 fix1 slice 1: committed fixed provenance and exact constants`, then push only lane/2026-10-22-bytes-c5-gates.

## Clause map

| Clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| committed fixed only, recorded provenance | scripts/bytes_gates.py committed_fixed/calculate/main | test_committed_fixed_source_override_and_missing_never_fallback | Use measured fixed or omit source hash: exact P delta/provenance assertion fails. |
| absent committed input is unavailable, no fallback | scripts/bytes_gates.py committed_fixed/calculate | same test, invalid input loop and main missing-file check | Fall back to measured fixed: disk statuses and CLI exit assertions fail. |
| measured c exact division | tests/test_bytes_gates.py ReplayTests | test_nine_plus_h_replay_and_integer_boundaries | Perturb measured_c by any representable amount: equality fails. |

## OPEN ISSUES

- Remaining authorized fix-round work listed in PROGRESS; no completion claim.
- BY-MERGE: pass1 ancestors carry changes to sealed files relative to main (plan.py, driver.py, hazards/clock.py and others); resolve in BY-MERGE, never in this lane.
- Director re-runs real replay with updated fixed from C5; prior 0/10 evidence uses old fixed. Reviewer reports committed-fixed also 0/10; worker has not read real session trees.
- Draft PR #547, last supplied CI: 20 pass, gate-ledger fails at cf716ce00. No network/CI query attempted.

## NEEDS_RULING

none
