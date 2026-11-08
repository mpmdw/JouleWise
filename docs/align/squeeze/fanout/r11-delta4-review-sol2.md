# R11 delta4 review — Sol2

2026-11-08. Reviewed `9891d679b..48a4d1d76` on
`align/2026-11-08-v4-r11-delta4-sol2`. **Verdict: ADMIT_WITH_FIXES.**

No substantive packet forgery in the exercised cases armed, and I found no new blinding or
custody bypass. The packet rebuild and delta3 repairs are substantially installed.
Three bounded implementation follow-ups and one stale-test repair remain below.
These do not justify interrupting R1 or redesigning W1. Prefer fixing them before
the final strict receipt is frozen; F1 must be fixed before processing a captured
calibration retry. This is code-review admission, not native W1 arm readiness.

## Findings

**F1 — MEDIUM: a valid `C1#2` retry loses its registered U3 comparison scope.**
`joulewise/align/apple/thermal_desk.py:888` looks up `checks_by_window[window]`
literally. The merged policy has C1–C8, while the new retry wire accepts Cn#k.
The same valid D replay passes as C1 and becomes `inconclusive` as C1#2, with
reason `U3 comparisons exceed the frozen series scope`. The session turns that
into a failed U3 desk check, obstructing the next arm/eligibility after a genuine
zero-capture retry. Normalize a validated retry id to its counted slot for the
policy lookup, retaining the full attempt id in records and reports. Do not add
another comparison or calibration slot. Witness:
`IntegrationWitnesses.test_zero_capture_retry_keeps_the_registered_u3_scope_of_its_counted_slot`.

**F2 — MEDIUM, standing-rule compliance: U3 admission caches a successful decision.**
`joulewise/align/apple/v4_u3.py:266` decorates `validate_cached` with `lru_cache`;
`v4_registration.validate_u3` calls it on the admission path. Two validations of
the same serialized bar invoke `derive` only once. This conflicts with the brief's
SPEED-TOOLBOX rule: never cache decisions; admission paths never read caches.
Make admission validation uncached, including its use of cached derivation helpers
where that rule applies. No speed improvement is claimed here. The complete bar
is the current key, and source/gate custody checks with `root` still run outside
this cache: this witness proves skipped validation, **not** acceptance of an
edited bar, stale gate bytes, or a forged packet. Witness:
`IntegrationWitnesses.test_u3_admission_recomputes_validation_instead_of_caching_a_decision`.

**F3 — LOW: the actual `pushed_tip` field is not excluded from canonical equality.**
`scripts/align_v4_next_arm_packet.py:294` strips only top-level fields, but
`committed()` emits the tip under `checks.record_committed.pushed_tip` at line 409.
Advancing the local remote-tracking ref to a descendant containing only an
unrelated note leaves `_record_bound` true, yet the actual arm refuses on packet
inequality. Keep that volatile tip at the excluded top level, or exclude that
exact nested field; preserve every substantive comparison and rebuild the push
reachability check. Rebuilding the supplied packet is an immediate workaround.
Witness: `PacketBoundaryTests.test_pushed_tip_only_advance_does_not_stale_the_committed_sources`.

**F4 — MEDIUM, test drift after the R0 fill: two R1 runtime tests still require pending R0.**
`tests/align/test_r1_runtime.py:184` passes the now-filled production runtime
config to `main`, expecting `PENDING R0`; it reaches native `/bin/ps`, which the
sandbox refuses, and returns 3 instead of 2. At line 202 the production D
templates are still expected to have pending effort, although the integration
correctly fills `medium`. Create explicit synthetic pending-input fixtures and
assert that refusal precedes any host command. Keep the production R0 fill and
the R0-L3 contention behavior. These are two existing failed tests, separate
from the three new red witnesses; no capture or model was started.

## Requested review coverage

- **Packet authority:** read the Opus review directly with `git show` from the
  specified review ref. The arm runs the real builder and judges its own packet.
  Added actual-arm witnesses reject edited status, basis, sources, record/series
  digest, calibration rows, desk digest, added preparation time, missing expiry,
  an expired packet, a dead meter and a broken history link. Only the named
  top-level preflight/tip metadata is ignored (F3 covers the misplaced real tip).
- **History and rulings:** hash links, ancestry, ordered counted attempts,
  committed ruling-text digests and Cn#k ordering have passing existing tests.
  The new actual-arm battery witness admits the first non-pass, refuses the
  second, admits a signed disposition backed by committed text, then rejects an
  edited text digest. There are **16 entries, 15 gating**.
- **Arm observations:** current clock, meter, battery/top-up, powermode and
  volumes remain arm-computed. Quiet state still uses a fresh committed
  observation pending the separately owned condition-waits receipt; I do not
  claim that native quiet producer is delivered here.
- **Delta3:** both witness modules pass; allowlist is empty; builder and all four
  launchd templates are bound and strict. The committed dynamic trace includes
  `night_driver_hazard_pack` (two passing tests); fresh production-supervisor and
  minimal-W1 tracing tests pass. G1 rejects an old window after the canonical
  ledger moves. G3 refuses unlisted, unsupervised, hashless and hash-mismatched
  streams while salvaging covered members of a listed, matching unclosed stream.
- **Integration:** ancestry checks confirm `5d9b66dd4`, `d9d1098c6`, `9c40e4e5d`
  and `6d20e787a` are merged. R0 effort is `medium`; the runtime sensor config
  carries TV0h/Tf08, F0Ac/F1Ac and its recorded R0 digest. That digest was treated
  as text; I did not open its capture. The pre-L3 fatal contention branch is gone
  from `QuietGuard`; SMC uses one redo then flag, largest single non-kernel_task
  process, with aggregate-only load/display wakes nonfatal and tooling/census
  refusals retained. Synthetic R0 tests pass. W1 blocker, export, battery and
  independent U3 arithmetic suites pass, as does the full synthetic W1 run.

## Verification

Python 3.13.18, one module per process, serial. Test subprocesses used a resolved
`TMPDIR=/private/tmp/jw-r11-delta4-sol2`, `JW_WP22_FULL=1`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and a temporary host-state
directory. Total test wall time was about six minutes, including the initial
nine-witness run and its ten-witness rerun. No full-suite discovery was run.

All **25 touched test modules, 581 tests**, passed, with one optional real-capture
replay skipped and one pre-existing WP22 expected failure:

| Module suffix (`tests.align.` unless marked) | Tests |
|---|---:|
| test_km003c | 23 |
| test_r0_checks | 33 |
| test_r0_host | 59 (1 skip) |
| test_r11_delta3_sol1 / test_r11_delta3_sol2 | 18 / 13 |
| test_r11_delta_sol1 / test_r11_delta_sol2 | 8 / 6 |
| test_smc_classifier_v4 / test_smc_quiet | 27 / 34 |
| test_v4_cadence / test_v4_dynamic_closure | 30 / 10 |
| test_v4_kit | 116 |
| test_v4_next_arm_packet / test_v4_next_arm_packet_opus_witnesses | 27 / 5 |
| test_v4_powermode_record / test_v4_r11 | 9 / 27 |
| test_v4_receipt_tiers / test_v4_record_binding | 8 / 6 |
| test_v4_registration / test_v4_topup | 22 / 19 |
| test_v4_w1_blockers | 16 |
| test_v4_w1_synthetic | 22 (1 expected failure) |
| test_w1bm_sol1 / test_w1bm_sol2 | 12 / 12 |
| tests.hazards.test_smc_enumeration | 19 |

The optional R0 replay decorator calls `Path.is_file()` on a prohibited real
capture during module import. A temporary harness intercepts `os.stat` for paths
outside the clone under `/Users/edr`, returning ENOENT **before** calling the real
stat; an audit hook also refuses opens/listings there. This skips that replay
without consulting its path. The harness first had import/error-handling setup
errors; after correction `test_r0_host` passed 59 tests with that one skip. Logs,
the guard and serial runners are in the temporary directory above.

Additional modules, still one per process:

| Command target | Result |
|---|---|
| `tests.align.test_r1_runtime` | 33 tests, **2 failures**, F4 |
| `tests.align.test_r1_runtime_e2e` | 2 OK |
| `tests.align.test_v4_executed_closure` | 4 OK |
| `tests.align.test_protocol_v4_doc` | 6 OK |
| `tests.align.test_r11_delta4_sol2` | 10 tests, **3 intentional failures**, F1–F3; 7 pass |

Touched/existing modules were run through
`python3.13 -B /private/tmp/jw-r11-delta4-sol2/run_module.py MODULE` to apply the
sealed-path guard. The final witness command was the ordinary
`python3.13 -B -m unittest tests.align.test_r11_delta4_sol2` with the environment
above. Witness AST parsing and `git diff --check` also passed.

## Handoff

Only `tests/align/test_r11_delta4_sol2.py` and this report were added. Production
code, raw evidence, coordination state and registration artifacts were preserved.
No network, weights, Block 5 analysis or real measurement-data read was used.

Next exact step: lead dispositions F1–F4, makes the small code/test repairs and
reruns the affected modules individually before generating the final strict
receipt. No new scientific ruling appears necessary for these repairs. Any
native MLX/R1/W1 smoke, live meter/top-up, quiet-state evidence and final signed
registration gates remain lead-controlled work outside this sandbox; none was
validated here. The review does not establish that the custody/series export
adapter or R1's live outputs are ready. No new MLX implementation was added.
