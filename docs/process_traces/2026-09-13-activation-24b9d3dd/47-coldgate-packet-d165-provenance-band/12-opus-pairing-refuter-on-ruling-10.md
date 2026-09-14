# Opus 5 pairing refuter (contract + physics lens) on cold-gate ruling 47

Read-only in `JouleWise-wt-coldgate-census` at `7e5e7f81`; arithmetic on the canonical venv interpreter with `PYTHONPATH` on this worktree. No tracked file edited; test suite not run.

## VERDICT: AMEND

Option (ii) — one shared scale-aware predicate — is **AFFIRMED**. Four amendments precede writing the addendum. **A-1 is blocker-grade**: the predicate *as the ruling places it* admits an unbounded divergence on a reachable input.

## 1. Arithmetic: Exhibit E reproduces; both stated scale numbers are wrong

Exhibit E reproduced exactly (20 / 200 / 2,000 J admit; 20,000 J refuses, gap `1.8189894035458565e-12`).

Derivation (`u = 2^-53`). `abba_delta` computes `((b1+b2) − a1) − a2`, then halves. With the true delta near zero: `fl(b1+b2)` rounds by ≤ `ulp(b1+b2)/2`; subtracting `a1` is **exact** when all four members share a binade (partial sum on the coarse grid, `a1` on the finer one) and rounds by ≤ `ulp/4` only when they straddle a power of two; the last subtraction is exact by Sterbenz (delta ≈ 0 forces `t2 ≈ a2`); `fsum` is exactly rounded and every `0.5·x` is exact, so `z` is the once-rounded exact value. Hence `|z − delta| ≤ 0.375·ulp(b1+b2)`, **quantised in powers of two**; refusal needs it > 1e-12, i.e. `b1+b2 ≥ 2^14`.

- First refusal on the packet's pattern is **exactly 16,384.0 J** per member, not "≈16,500 J": 16,383.9 admits (gap 9.09e-13), 16,384.0 refuses (gap 1.819e-12). 16,506 is a scan-grid artefact.
- Provably sound below **8,192 J** for *any* operand pattern, and below **16,384 J** for same-binade members. The ruling's 2,048 J is true but 4× loose.
- Any-pattern counterexample the ruling's scan missed, largest member **8,625.6 J**: `A1=7866.7731078908755, B1=8299.331116021545, B2=8193.042721109765, A2=8625.600729240432` → `delta=0.0`, `z=1.3642420526593924e-12`, **REFUSES**.
- "200,000 random blocks, none below 16,725 J" does not reproduce: **400,000 uniform-random blocks refused at no scale at all.**

That last point exposes a second necessary condition the ruling never states. `isclose` takes `max(rel_tol·max(|z|,|delta|), abs_tol)`, so a block is exposed only when its **true delta is below ≈1.7e-7 × member scale** (≈1.8 mJ at 20 kJ members): bench at 20 kJ, delta 1e-6 J refuses, delta 3e-3 J admits. Any block with a physically meaningful delta is never refused at any scale. Real defect, narrower than ruled.

## 2. The ruled predicate — A-1 (BLOCKER) and the ~1 J question

Bench: 20 kJ identical operands, `S = 40,000.3`, `abs_tol = 2.842192e-10` vs gap 1.819e-12 → **admits**; delta `+1e-6 J` → gap 1e-6 vs `abs_tol` 2.842e-10, `rel` 1e-15 → **refuses**. Both counterfactuals hold. `64u = 7.105427e-15`; `abs_tol` hits 1e-6 J at `S = 1.4074e8 J` (ruling confirmed) and **1 J only at `S = 1.4074e14 J`** — 4.5e5 years at 10 W. Unchanged `rel_tol=1e-9` admits 1 J once `max(|z|,|delta|) ≥ 1e9 J`, equally unreachable and pre-existing. On **validated finite** inputs, no blocker.

**A-1 (BLOCKER): the predicate as placed reads an unvalidated input.** Upstream, the envelope sum is the raw loop variable `raw_envelope_sum`; its finiteness/sign check is `floor_extraction.py:601–607`, **after** the guard at 590. `math.isclose(z, delta, rel_tol=1e-9, abs_tol=inf)` returns `True` (bench-checked), so a block with `member_envelope_integral_sum_j = +inf` gives `S = inf` and the guard admits **any** divergence, ≫ 1 J included; a non-numeric value raises an uncaught `TypeError` instead of refusing. The consumer is safe only incidentally (`dominance_closeout.py:574–587` validates first). **Mandatory cure:** hoist the existing `envelope_sum = _common_mode_finite(raw_envelope_sum)` block (601–607) above the guard and build `S` from `envelope_sum`. Add to `R-B1-REFUSE`: *a block with `member_envelope_integral_sum_j = float("inf")` and `|z−delta| = 1.0 J` must refuse with `common_mode_precondition_failed` at both sites.*

The ruling's scope citation is wrong: "639/648 upstream" sits in `_common_mode_floor_from_block_inputs`, a **different function** assembling the argument lists, not the guard's scope.

## 3. Two sites, import cycle, contract statement — A-2

**The ruling's module placement is backwards and would cycle.** `floor_extraction.py:99` already top-level imports `from joulewise.dominance_closeout import split_common_mode_block_width`; the repo says so at `dominance_closeout.py:905–909` ("Local import prevents a module cycle…"), three lines above the guard. **A-2 — replace the Q1 "Predicate" preamble with:**

> Predicate (one function, `common_mode_provenance_band_ok(...)`, defined in `joulewise/dominance_closeout.py` beside `split_common_mode_block_width`, which `joulewise/floor_extraction.py` already imports at top level at line 99 — the cycle-free direction; the reverse would require the lazy in-function import pattern of `dominance_closeout.py:905–909`).

Stronger than the ruling: `dominance_closeout.py:588–596` **already computes the ruled `S`** — `max(member_envelope_sum, 1.0, abs(delta), abs(zero_point), *|onset|, *|offset|)`, then `extrema_pad = 64.0 * (math.ulp(1.0)/2.0) * S`, and `math.ulp(1.0)/2.0 == 2**-53 == u`. Factor that `max(...)` into `common_mode_provenance_scale_j(...)` and call it from all three places. This corrects the contract statement too: the ruling calls "adding `|delta|` and the sweep values" seat B's proposal — **it is not; the registered code already floors S over all of them.**

**Parameter hash — the ruling's NOT-EXECUTED item, executed.** `two_shared_edge_common_mode_registration()` (`detection_floor.py:665–708`) carries no tolerance field, so the band's `abs_tol` is not enumerated and **no re-registration is required**. `4d1c544f…` is stale: live `COMMON_MODE_PARAMETER_SHA256` is `dd61d38811ddadb2aecb8df4a533b715c8ca74bb031896d09688c9b76b69ed38`, and `4d1c544f…` is already rejected (`tests/test_detection_floor.py:1228`). Replace the contract statement's closing sentences with: *"Executed: the registered parameter payload (`detection_floor.py:665–708`) carries no tolerance field, so the live hash `dd61d388…` is unaffected; no re-registration."*

Emitted width unchanged (`dominance_closeout.py:612–615` charges `abs(zero_point − delta)` outward once inside `_outward_four`, computed before the guard); reason strings unchanged. **Contract-change statement AFFIRMED** apart from these corrections.

## 4. Rejection of option (iii) — AFFIRMED; verified on the file

`floor_extraction.py:2710–2713` builds the delta from `member.value_j`, which comes from `_member_metric_value` (`1839–1845`): `phases = summary.get("phase_energy_j"); raw = phases.get(...)` — a **stored reducer summary field**. The contrast at `2534–2543` is `math.fsum(coefficients[position] * _integrate(curve, start_s + onset_s, end_s + offset_s) …)` — a **fresh re-integration** of the trace curve. Different computations over different artefacts; (iii) is correctly rejected. The corroborating point holds: `floor_extraction.py:2092–2097` already tolerates summary-vs-re-derived disagreement in the same band, and is **not** exposed, because both its operands are of member-energy magnitude so `rel_tol·20,000 ≈ 2e-5 J` governs. One addendum clause should say so, or a later reader will "fix" that site too.

## 5. Q2 addendum — A-3, exact replacement text

Defects: the two wrong scale numbers; "three half-ulps of the partial sums" is an unbuilt term and not the mechanism; the near-zero-delta precondition is omitted, overstating exposure; and it is written in the present indicative as if installed — the **ruled-not-installed** failure the T26 sweep catalogued. Replacement, verbatim:

```
### D-124 dated addendum — 2026-09-13 (cold gate 47, GATE-SENSIBILITY-SWEEP-01 B1): the zero-point provenance band is scale-bounded, and its re-set is ruled but not yet installed

Round 4's `isclose(rel_tol=1e-9, abs_tol=1e-12)` band compares the stored ABBA delta
`(B1+B2-A1-A2)/2` with the zero-shift contrast `z` (a coefficient-weighted `fsum` of
freshly re-integrated member energies). These are two different binary64 routes over
the same four numbers: the sequential route rounds once when it forms `B1+B2` (and
once more if the members straddle a power of two), so `|z - delta| <= 0.375 x
ulp(B1+B2)`, a quantity that steps in powers of two. Consequences, bench-derived: the
band CANNOT refuse identical operands while the largest member is below 8,192 J,
whatever the operand pattern, nor below 16,384 J when the four members lie in one
binade; the first refusal on the packet's pattern is at exactly 16,384 J per member
(demonstrated at 20,000 J: sequential 1.8189894035458565e-12 J against `fsum` 0.0),
and an any-pattern refusal is demonstrated at a largest member of 8,625.6 J. A second
condition must hold for any refusal at all: `rel_tol` rescues the block unless its
true delta is smaller than about 1.7e-7 of the member scale (about 1.8 mJ at 20,000 J
members), so only blocks whose members nearly cancel are exposed. G2-a member
energies are tens of joules, three orders below the lowest refusing scale, so B1 is
not G2-a-blocking.
RULED, NOT YET INSTALLED (option (ii)): both sites -- `dominance_closeout.py` (the
D-165 replay consumer) and `floor_extraction.py` (the upstream duplicate) -- are to
call one shared predicate with `abs_tol = max(1e-12, 64u x S)`, `u = 2^-53`,
`S = max(1, member envelope integral sum, |delta|, |z|, every |onset| and |offset|
sweep value)`, `rel_tol = 1e-9` unchanged and the once-only outward `|z - delta|`
charge unchanged. `S` and the `64u` factor are not new: `split_common_mode_block_width`
already computes exactly this scale and pad for the registered member-envelope term,
and the shared predicate is to be factored out of it, so no constant is added and the
registered parameter hash `dd61d388...` (which enumerates no tolerance) does not move.
The guard remains a pure provenance guard, not load-bearing for soundness; a delta
moved by 1e-6 J still refuses. The code change and its regressions R-B1-ADMIT /
R-B1-REFUSE / R-B1-ONE-PREDICATE are tracked as GATE-B1-PROVENANCE-BAND-01 and are
not a fence on G2-a. Option (iii), deriving `z` through `abba_delta`, was rejected:
the stored member energies are `summary.json` `phase_energy_j` reducer fields
(`floor_extraction.py:1839-1845`, consumed at 2710-2713) while `z` re-integrates the
trace curve (2534-2543), so no construction makes them byte-identical. The same
`1e-9/1e-12` band at `floor_extraction.py:2092` is unaffected: there both operands
are of member-energy magnitude, so `rel_tol` governs.
```

## 6. Q3 — AFFIRMED, with A-4

(a) Conclusion affirmed, numbers amended per §1: not G2-a-blocking, three orders of margin (tens of joules against a lowest possible refusal at 8,192 J).

(b) Affirmed on the kernel: `GATE-R2-COVERAGE-ULP-01` is its own `queued` row riding the `ACCEPTANCE-EPOCH-25G83-01` D-138 transaction, so it does not hold the lane open; `GATE-SENSIBILITY-SWEEP-01`'s note names exactly two closing conditions, PR #314 merged (`0d4bb4fb`) and the B1 disposition recorded.

The code change belongs in a registered follow-up, not now; `GATE-B1-PROVENANCE-BAND-01` is free (absent from the kernel). **A-4:** cut the row *in the same commit* as the addendum, not promised, with `dependencies: []`, a status note carrying the 8,192 J floor and "not a G2-a fence", and the A-1 cure as an acceptance clause — without it the follow-up installs a predicate strictly weaker than the one it replaces on malformed input.

## 7. Left out

- **`64u` is unpinned by the ruling's own regressions** (1u also admits at 20 kJ), as its note concedes. Since §3 factors the scale *out of* `split_common_mode_block_width`, `R-B1-ONE-PREDICATE` should assert identity of the **shared scale helper** used by pad and band — pinning the 64 by construction, better than an import-identity check.
- **Exhibit A cites `decision_log.md:8114–8138` for the "not load-bearing" sentence; it is at line 8418.** Do not propagate the stale citation.
- **Packet defect confirmed independently:** Exhibit E's script prints a bare boolean but its output shows `admit|REFUSE |z-d|=…` columns — script and output are not one run. Every number still reproduces exactly.
- "Failures are not monotone in scale" is right and now *explained*: the error is a power-of-two quantum of `ulp(B1+B2)`, present or absent depending on whether the partial sum lands on the grid — hence a pad, never a scale cutoff.

### Executed probes

Venv snippets: Exhibit E reproduction; binade table 2^10–2^17; 0.5 J scan 15,000–18,000 J; 400,000 uniform-random blocks; 600,000 adversarial near-zero-delta mixed-magnitude draws; 2,000,000 draws capped below 8,192 J; ruled-predicate admit/refuse counterfactuals; `isclose` with `abs_tol=inf`/`nan`; `64u` crossings at 1e-6 J and 1 J; live `COMMON_MODE_PARAMETER_SHA256` and registration payload. `sed`/`grep`: `floor_extraction.py` (99, 500–665, 1839–1860, 2070–2100, 2700–2725), `dominance_closeout.py` (562–618, 905–918), `detection_floor.py` (660–712), `docs/decision_log.md`, `docs/process/state_kernel.json`. Not executed: the test suite; any live or fixture G2-a block.
