# Cold-gate ruling 47 — the D-165 zero-point provenance band (B1)

Judge: cold Fable 5.1 seat, 2026-09-13, worktree `JouleWise-wt-coldgate-census` at `7e5e7f81`. Validator: REFUSE on the typo charter sha (reason `charter_trusted_observed_mismatch`), then PASS on `099de884…c95d81` with packet `afd158e1…947f` and all five exhibit digests matching.

## Contamination disclosure

Auto-loaded before I read anything: `~/.claude/CLAUDE.md` (global rules), the worktree `CLAUDE.md` (bridge notes), and the memory index `MEMORY.md`, whose checkpoint lines mention this lane ("cold-gate packet 47", "B1 needs a decision-log correction, not G2-a-blocking"). I did not open any memory file, `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md` or any trace outside the packet directory. I read `docs/decision_log.md` only through Exhibit C plus a 7-line fidelity check at lines 8412–8418 and 12 lines under the D-165 addendum heading at 11270 for addendum style. Packet defect noted: Exhibit E's pasted script prints a boolean, but its pasted output shows `admit |z-d|=…` columns, so the script and output are not from one run. I re-ran the arithmetic myself (below) and every number matches.

Terms used here. **binary64**: the 64-bit floating-point number format Python floats use; every value is rounded to about 16 significant digits. **ulp**: unit in the last place, the gap between one binary64 number and the next; near 40,000 J it is 7.3e-12 J. **compensated sum**: `math.fsum`, which adds a list as if with unlimited precision and rounds once at the end. **provenance guard**: a check that two copies of the same quantity, carried by different routes, still agree, so a stale or substituted copy is caught. **shared half-width**: the block's emitted uncertainty term that both ABBA halves share; D-124 already adds `|z − delta|` to it outward once.

## Q1 — ruled option: (ii), one shared scale-aware predicate at both sites

**Why not (iii).** (iii) requires the re-integrated zero-shift member energies to equal the stored member energies byte-for-byte. They do not, by construction: the stored delta is built from `member.value_j` (`floor_extraction.py:2712`), and `value_j` is read from the bundle `summary.json` field `phase_energy_j.<phase>` by `_member_metric_value` (a stored reducer output), while the zero-shift contrast re-integrates `reader.summed_curve()` after subtracting an origin time (`floor_extraction.py:2430–2545`). Two different computations at two different times; the code itself already tolerates their disagreement (the anchor-envelope check at `floor_extraction.py:2092` compares the summary value to a re-derived `point_j` with the same `1e-9/1e-12` band). (iii) is rejected.

**Why not (i).** Keeping a band that a legitimate block fails for arithmetic alone is exactly the "silly gate" Ed ruled out, and the fix reuses a constant D-124 already registered. (i) would be defensible only if the failing scale were unreachable; a long block at ~10 W reaches it in under an hour.

**Predicate** (one function, private to `joulewise/floor_extraction.py`, imported by `joulewise/dominance_closeout.py`):

```
u = 2**-53
S = max(1.0, member_envelope_integral_sum_j, |delta|, |z|, max|onset_i|, max|offset_i|)
abs_tol = max(1e-12, 64 * u * S)
within_band = math.isclose(z, delta, rel_tol=1e-9, abs_tol=abs_tol)
```

Sites: `joulewise/dominance_closeout.py:963` (D-165 replay consumer; refuses with `_COMMON_MODE_ZERO_POINT_DIVERGENCE`) and `joulewise/floor_extraction.py:590` (upstream duplicate; refuses with `common_mode_zero_point_divergence_out_of_domain`). Both have every S input in scope (block fields at the consumer; `item.zero_point_contrast_j` / `member_envelope_integral_sum_j` at lines 639/648 upstream). The once-only outward charge of `|z − delta|` into the shared half-width is unchanged.

**Regression specification** (defect-shaped):

```
R-B1-ADMIT  (kills: reverting either site to abs_tol=1e-12, or any pad < 1.82e-12 J at S≈40,000 J)
  block members A1=20000.1, B1=20000.3, B2=20000.0, A2=20000.2 J built through the
  registered delta path (abba_delta) and the registered zero-shift builder
  (coefficient-weighted fsum), plus one ordinary valid second block; valid windows,
  authenticated shared bound, complete sweeps containing z by exact equality.
  Assert: old predicate refuses (|z−delta| = 1.819e-12 > 1e-12); new predicate admits at
  BOTH sites end-to-end (extraction reaches the D-165 consumer and the consumer admits);
  emitted shared_width_j still includes |z−delta| (compare against the width computed
  with z := delta; difference == |z−delta| before the 4-ulp outward step).
R-B1-REFUSE (kills: any pad or rel_tol loosened past the instrument, e.g. 64u*S*1e4,
             rel_tol=1e-3, or dropping the band entirely)
  same block, delta_j moved by +1e-6 J, z and envelope unchanged.
  Assert: both sites refuse with their existing reason strings.
  (Guaranteed while S < 1.4e8 J, where 64u*S first reaches 1e-6 J; the ~1 J
  attribution limit is six orders above the shift.)
R-B1-ONE-PREDICATE (kills: fixing one site only)
  assert dominance_closeout imports the floor_extraction predicate object (identity check),
  and run R-B1-ADMIT with the upstream site mutated back to 1e-12: must fail.
```

Note: R-B1-ADMIT does not distinguish `64u` from `1u` (both admit at this scale); the 64 factor is inherited from D-124's registered member-envelope pad, not pinned by this test.

**Contract-change statement.** The emitted shared width does not change (same composition, same `|z − delta|` charge). No receipt field changes; refusal reason strings are unchanged. No new registered constant: `64u` and the scale set `S` are D-124's own member-envelope pad and floored scale set (the set already includes `|z|`; adding `|delta|` and the sweep values is seat B's proposal and is ≤ the existing envelope sum in every legitimate block, so it only matters when a sweep value or delta is anomalously large, which is the refuse case). NOT EXECUTED: I did not verify whether the registered parameter hash `4d1c544f…` enumerates the band's `abs_tol`; if it does, the implementing PR must re-register the hash by D-124 addendum and add the superseded hash to the rejection regression, as the round-4 entry did.

**Reason grounded in D-124 and D-161.** D-124 round 4 states the band "is a pure provenance guard and is not load-bearing for soundness": the shared half-width already charges `|z − delta|`, so admitting a 1.8e-12 J divergence changes no reported number by more than that divergence, which is 12 orders below the ~1 J attribution limit. Under D-161's operative test (MISTAKE vs DELIBERATE) the guard still earns its place, because a stale or substituted `delta_j` is an operator mistake and the refuse counterfactual shows such a block still refuses. What D-161 does not license is a mistake-detector whose threshold is below the arithmetic noise of the two routes it compares: that refuses evidence, and evidence refusals are the class D-161 keeps only when the physics or evidence is actually in doubt. Sizing the band to `64u × S` is sizing it to the instrument that produces it, which is the binary64 arithmetic, exactly as GATE-SENSIBILITY-SWEEP-01 demands.

## Q2 — the D-124 dated addendum (verbatim)

```
### D-124 dated addendum — 2026-09-13 (cold gate 47, GATE-SENSIBILITY-SWEEP-01 B1): the zero-point provenance band is scale-aware

Round 4's `isclose(rel_tol=1e-9, abs_tol=1e-12)` band between the stored ABBA delta
`(B1+B2−A1−A2)/2` and the zero-shift contrast `z` (a coefficient-weighted `fsum` of
the re-integrated member energies) compares two different binary64 routes over the
same four numbers, and the sequential route alone rounds by up to three half-ulps of
the partial sums: below 2,048 J per member that error is at most 6.8e-13 J and the
band is sound, but on the bench it first refuses identical operands near 16,500 J
per member (demonstrated at 20,000 J: sequential 1.819e-12 J against fsum 0.0),
a scale a ~10 W block reaches in under an hour and far above G2-a's tens of joules.
Ruled (ii): both sites, `dominance_closeout.py` (D-165 replay consumer) and
`floor_extraction.py` (upstream duplicate), call one shared predicate with
`abs_tol = max(1e-12, 64u × S)`, `u = 2^-53`, `S = max(1, member envelope integral
sum, |delta|, |z|, every |onset| and |offset| sweep value)`, `rel_tol = 1e-9`
unchanged, the once-only outward `|z − delta|` charge unchanged; this reuses the
registered `64u × S_env` allowance and adds no constant. The guard remains a pure
provenance guard, not load-bearing for soundness; a delta moved by 1e-6 J still
refuses (guaranteed for S < 1.4e8 J). Regressions R-B1-ADMIT / R-B1-REFUSE /
R-B1-ONE-PREDICATE per cold-gate ruling 47. Option (iii), deriving z through
`abba_delta`, was rejected because the stored member energies are reducer summary
fields, not the extraction-time re-integration, so no construction makes them
byte-identical.
```

## Q3 — for the record

**(a) Not G2-a-blocking.** On the packet's operand pattern the current band first refuses at a member energy of about 16,500 J (scan of 1,088 scales from 1 J to 50 kJ, 69 refusals, none below 16,506 J; 200,000 random blocks with member energies from 100 J to 100 kJ, none refused below 16,725 J). Below 2,048 J per member it cannot refuse identical operands at all (worst sequential rounding 6.8e-13 J < 1e-12 J). G2-a probe energies are tens of joules, roughly three orders below the first observed refusal and two below the provable-safe bound. The band's failures are also not monotone in scale (200,000 J admits), which is why the fix is a pad, not a cutoff.

**(b) The lane closes on this ruling once the disposition is recorded** (the Q2 addendum in the decision log plus the kernel row's status note), which is the closing condition its own status note and terminal review 36 state. R2 does not hold it open: it is staged under D-138 with its own id, GATE-R2-COVERAGE-ULP-01. One tension for the magistrate to record, not to relitigate: the row's acceptance text says re-set gates land "with a defect-shaped test" before any G2-a number is consumed. The (ii) code change plus its three regressions should therefore be cut as a named follow-up (suggested id GATE-B1-PROVENANCE-BAND-01) through the ordinary gauntlet, explicitly marked non-G2-a-blocking on the (a) energies, so that the arithmetic fix does not itself become a silly gate on the first real numbers.

## Executed probes

1. `validate_gate_packet.py` twice: typo sha → REFUSE rc=2; correct sha → PASS rc=0, five exhibit digests match; `shasum -a 256` of the packet directory agrees.
2. `cat` of `00-PACKET.md` and exhibits A–E.
3. `grep`/`sed -n` on `joulewise/floor_extraction.py` (lines 105–120, 318–380, 440–480, 2020–2150, 2395–2570, 2690–2730, `_member_metric_value`), `joulewise/reduce.py` (`_integrate`), `joulewise/detection_floor.py` (`abba_delta` callers).
4. `git show 14212426:` fidelity checks of `dominance_closeout.py:963`, `floor_extraction.py:590–595`, `decision_log.md` 8412–8418 and the D-124/D-161/D-165 heading lines; the D-165 addendum's first 12 lines for style.
5. Venv arithmetic (read-only interpreter, `sys.path` pointed at this worktree): Exhibit E reproduced exactly at 20 / 200 / 2,000 / 20,000 J; the seat-B pad at 20,000 J = 2.842e-10 J admits; +1e-6 J refuses at every scale; refusal-onset scan and random-block scan as reported in Q3(a); worst-case sequential rounding bound `3·ulp(2m)/4` tabulated at 1,000 / 2,000 / 2,048 / 4,096 J.

Not executed: the test suite (forbidden); the parameter-hash coverage check (see Q1 contract statement); any live or fixture-level G2-a block.
