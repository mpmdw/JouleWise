# Magistrate disposition of the Opus 5 counter-review (file 17), gate item 6 (2026-09-02)

Opus 5, contract lens, at `68db7e98`: BLOCKER 0 / SHOULD-FIX 8 / NIT 4 /
not-a-defect 1. C1 (ruled-relation fidelity, term by term, clock typing),
C2 (11-site census by AST), C3 (three boundary regressions, mutation-
verified 3/3 and 3/3) and C4 (terra 229 DOC-ADDITIVITY disposition) all
confirmed. Every finding below was re-verified at the bench before its
disposition (Executed evidence).

## Dispositions

| Finding | Severity | Disposition | Where |
| --- | --- | --- | --- |
| F-1 wrong clock named in the ruling amendment (`CLOCK_MONOTONIC`) | should-fix | ACCEPTED, bench | `MAGISTRATE-RULING-T0-UNATTENDED.md` line 159 now names the ordinary monotonic clock (`time.monotonic_ns`, `CLOCK_UPTIME_RAW` on Darwin) and excludes `CLOCK_MONOTONIC_RAW` |
| F-2 "11 sites × 45 s" asserted, not enforced | should-fix | ACCEPTED, bench | `test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census` counts `_fresh_probe` call sites by AST (R1's own site excluded), asserts 11, and derives the constant as `(11 × _PROBE_TIMEOUT_SECONDS + 105) s`; a twelfth site fails it (counterfactual below) |
| F-3 equality test manufactures an invariant with `_MIN_IDLE_NS` | should-fix | ACCEPTED, bench | that equality test is REPLACED by the F-2 test; the coincidence with `_MIN_IDLE_NS` is stated in the docstring and deliberately not pinned. The "moves only by cold gate" fence is now live in the kernel (F-7) |
| F-4 production cites D-170, absent on main | should-fix (merge-order) | CURED by merge order | #273 (t26-a) merged first (`e0f258ed`); `git show origin/main:docs/decision_log.md | grep -c D-170` → 8 at the bench; main merged into this branch at `c582120d` |
| F-5 dangling addendum anchor | should-fix | ACCEPTED, bench | file 12's addendum appended to `COLD-GATE-RULING.md` as `## Addendum 2026-09-02 — item 3 drift-envelope rationale`; the slug the link uses (`addendum-2026-09-02--item-3-drift-envelope-rationale`) now resolves (the kernel row's fallback pointer uses the same anchor and `gen_state --check` validates it) |
| F-6 addendum restates the relation on `validity_origin` | nit | ACCEPTED as written, no edit | equivalence rests on RF-18 (`valid_until == validity_origin + 6 h`), enforced elsewhere; the addendum's form is the one the reader of that file has, the code's form is the ruled one. Recorded, not rewritten |
| F-7 kernel still forbids what the code does | should-fix | ACCEPTED, bench | fence text at the `cold-gate packet: ruling-status semantics` entry and the `T0-UNATTENDED-01` status note refreshed to say the 5 s bound was STRUCK (T26 item 3, D-170) and replaced by the 600 s liveness bound; kernel row `T0-LIVENESS-BOUND-EMPIRICAL-01` (file 11) registered (quiet_mac, lead_only, structured fallback → cold gate); `TASK_QUEUE.md` regenerated; `test_gen_state` literals 126 → 127, quiet-Mac 14 → 15 |
| F-8 duplicate negative-boundary test | nit | RECORDED, kept | harmless; pins the rewritten lower half in its new algebraic form |
| F-9 ruling's "cannot false-refuse a healthy night" premise falsified, uncorrected | should-fix | ACCEPTED, bench — dated correction, disclosed to Ed | a `### Correction to item 3's "cannot false-refuse a healthy night" premise` subsection follows the addendum in `COLD-GATE-RULING.md`: the premise is withdrawn (§6.3.1's 715 s fixed subtotal > 600 s), the ruled number / `<=` / labelling / clock typing are unchanged, and the obligation is the kernel row. This corrects a cold-gate ruling's stated premise, not its verdict; the magistrate is not overruling the cold seat and Ed sees the paragraph |
| F-10 43-code reason-code census test out of the ruling's scope | should-fix (scope) | RECORDED, kept | it kills M8 (terra 212 F3); Opus grants it is defensible. Scope discipline noted for the next lane: a mutation-kill that expands a census belongs in its own row |
| F-11 fixture comment gives the wrong reason for the ARM's `10**30` | nit | ACCEPTED, bench | comment now states the real reason (`sample_arm` has no clock PROBE fact, so the liveness conjunct never runs against it) |
| F-12 fix round un-installed the ruled labelling + pointer to the ruling file | should-fix | ACCEPTED, bench | the conjunct's comment (`arm_readiness.py:6478`) again reads "COLD-GATE-RULING item 3: a liveness/hang detector, NOT a metrology bound" with the 11 × 45 + 105 provenance and the §6.3 / §6.3.1 pointers (three lines). The magistrate's own fix brief F-8 caused this; recorded in MAGISTRATE-NOTES as the lane's one un-installation |
| F-13 stale-looking line citation pinned to the landing commit | not-a-defect | RECORDED | accurate as written |

C7 (Opus): no same-signature recurrence across the refuter and delta
rounds; the one miss was the delta re-audit checking that a change
*happened* rather than that a ruled requirement *survived* it (F-12).
Accepted as the lane's process finding; carried to the Ed follow-up
email with the rule-11 items.

## Post-review code commits (operation-loop §5)

`joulewise/arm_readiness.py` (comment only), `tests/test_arm_readiness_schemas.py`
(comment only), `tests/test_arm_readiness_evidence_t0.py` (one test
replaced by the census-derivation test), `tests/test_gen_state.py` (two
literals), the kernel + `TASK_QUEUE.md`, and the three ruling/addendum
docs. A fresh pass over this commit is required before merge and is
recorded in MAGISTRATE-NOTES.

## Executed evidence (bench, this session; `TMPDIR=<scratchpad>/tmpbench4`)

```
$ git show origin/main:docs/decision_log.md | grep -c "D-170"
8
$ git show origin/main:docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md | grep -c "^## Addendum 2026-09-02"
1                                  (the item-4 addendum from t26-a; item 3's was still unapplied → F-5 stood)
$ grep -n "^## Addendum 2026-09-02 — item 3" docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md
334:## Addendum 2026-09-02 — item 3 drift-envelope rationale              (after the bench edit)
$ git show e40e7502:joulewise/arm_readiness.py | grep -n "not a metrology bound"
6479:        # not a metrology bound.  ...                                      (the landing had the labelling; fea89b72 removed it — F-12 confirmed)
$ python3 scripts/gen_state.py && python3 scripts/gen_state.py --check && echo CHECK-OK
CHECK-OK
$ python3 -m unittest tests.test_gen_state tests.test_docs_freshness
Ran 65 tests ... OK
$ python3 -m unittest tests.test_arm_readiness_evidence_t0 -k probe_census -v
test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census ... ok
```

F-2 counterfactual (AST census on the module text with one `_fresh_probe`
call added inside `_thermal_probe`, no file written):

```
base post-R1: 11
mutant post-R1: 12 -> test would fail: True
```

Three touched modules after all edits:

```
$ python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness tests.test_arm_readiness_schemas
OK (skipped=7)
```
