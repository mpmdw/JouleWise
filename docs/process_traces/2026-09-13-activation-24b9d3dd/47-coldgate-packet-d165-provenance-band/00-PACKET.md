# Cold-gate packet — GATE-SENSIBILITY-SWEEP-01 finding B1: the D-165 zero-point provenance band (`isclose(rel_tol=1e-9, abs_tol=1e-12)`) falsely refuses identical operands at large member-energy scale; rule its disposition (the lane's last open item; a registered decision-log band, so rule 11 sends it here)

Assembled 2026-09-13 ~10:30 PDT by the resident magistrate (activation 24b9d3dd). Mechanically assembled: exhibits are verbatim extracts at main (Exhibit B/C/D) or of the 96bfeca7 seat record (Exhibit A), plus one bench reproduction whose commands and output are pasted (Exhibit E). The magistrate wrote only this file and the one labelled "Reading" paragraph in Exhibit E.

## What was found

GATE-SENSIBILITY-SWEEP-01 (Ed, 2026-09-10: "no silly gates on accepting numbers … every tolerance sized to the instrument") inventoried 299 gates on the claim path; seat B's only demonstrated re-set candidate is B1 (Exhibit A). The D-165 replay consumer (`joulewise/dominance_closeout.py:963`, Exhibit B) and its upstream duplicate (`joulewise/floor_extraction.py:590`) both require the block's stored ABBA delta `(B1+B2−A1−A2)/2` (`detection_floor.py:abba_delta`) and the zero-shift contrast `z` (a coefficient-weighted `math.fsum` of the re-integrated member energies, `floor_extraction.py:2535`) to agree within `isclose(rel_tol=1e-9, abs_tol=1e-12)`; a mismatch refuses (`common_mode_zero_point_divergence_out_of_domain` / `_COMMON_MODE_ZERO_POINT_DIVERGENCE`). D-124 round 4 (Exhibit C) registered that band and states it "is a pure provenance guard and is not load-bearing for soundness": the shared half-width already charges `|z − delta|` outward once, so a nonzero divergence is accounted for, not hidden.

The two paths are different binary64 arithmetic on the same four numbers. Exhibit E reproduces seat B's counterexample through the production `abba_delta`: at member energies near 20,000 J the sequential path rounds to 1.82e-12 J while the compensated sum gives 0.0, and the guard refuses; at 20 J, 200 J and 2,000 J it admits. The refusal is therefore an artefact of the arithmetic, not evidence about the measurement, and it is above the energies of the planned G2-a probes but inside the range of a long block.

Facts the packet holds: D-161 (Exhibit C) keeps fail-closed refusals for physics and evidence classes and prunes operator-only ones; the shared bound's `64u × S_env` member-envelope pad already exists (D-124) and its scale set includes `|z|`; seat B proposed reusing exactly that allowance for the guard (`abs_tol = max(1e-12, 64u × S)`, Exhibit A) and warned that the upstream duplicate must move with it; the lane's kernel row (Exhibit D) closes when "the B1 disposition is recorded".

## Q1 — the disposition (rule one option, or write a better one)

- (i) KEEP the band unchanged; record B1 as a known, scale-bounded limitation (state the scale from Exhibit E) in the D-124 addendum; no code change.
- (ii) ADOPT seat B's scale-aware band at BOTH sites through one shared predicate: `abs_tol = max(1e-12, 64u × S)` with `u = 2^-53` and `S = max(1, member_envelope_integral_sum_j, |delta|, |z|, every |onset|, |offset| sweep value)`, `rel_tol=1e-9` unchanged; the once-only outward charge of `|z − delta|` unchanged; seat B's two counterfactual regressions (admit the identical-operand block; still refuse a delta moved by 1e-6 J).
- (iii) MAKE THE IDENTITY EXACT BY CONSTRUCTION: compute the zero-shift contrast through the same `abba_delta` formula on the four zero-shift member integrals (so `z == delta` exactly whenever the integrals equal the stored member energies), keep the band as it is (it then guards only genuinely different inputs), and record the change as the D-124 correction. The judge must say whether the re-integrated member energies at zero shift ARE the stored member energies byte-for-byte (Exhibit B's `_integrate` at `start_s + 0`, `end_s + 0`) — if not, (iii) does not remove the discrepancy and must be rejected.
- (iv) Other, with the same burden: no legitimate block may be refused for arithmetic alone; a block whose delta or zero point was actually altered by more than the instrument can resolve (~1 J attribution limit, ~5 J claim bar) must still refuse.

Deliver: the ruled option; for (ii)/(iii)/(iv) the exact predicate or formula, both sites named, and the regression specification (defect-shaped: the admit counterfactual and the refuse counterfactual, with the mutation each kills); the reason grounded in D-124's own text (a provenance guard that is "not load-bearing for soundness" versus D-161's classes); and a contract-change statement (does the emitted shared width, any receipt field or any registered constant change?).

## Q2 — the decision-log correction text

Whatever Q1 rules, D-124's round-4 paragraph currently asserts the band without the scale caveat. Write the dated addendum paragraph verbatim (one paragraph; it names the counterexample scale, the ruled disposition, the two sites, and — for (i) — the scale below which the band is known sound), in the style of the existing "dated addendum" entries in Exhibit C.

## Q3 — for the record

(a) Is B1 G2-a-blocking? State the member-energy scale at which the current band first refuses identical operands and compare it with G2-a probe energies (tens of joules). (b) Does GATE-SENSIBILITY-SWEEP-01 close on this ruling (its row says it closes when PR #314 has merged — it has, `0d4bb4fb` — and the B1 disposition is recorded), or does R2 (staged for D-138 as GATE-R2-COVERAGE-ULP-01) keep it open?

## Constraints on the judge

Read-only. Probes allowed: `git show <sha>:<path>`, `rg`/`grep`, `sed -n`, and Python arithmetic with the venv interpreter `/Users/edr/code/JouleWise/.venv/bin/python3` importing `joulewise.detection_floor` and reading `joulewise.floor_extraction` (single snippets; never the test suite). Do not edit any tracked file. Never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` read-only is allowed), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (ruled option; predicate/formula and sites; regression spec in a fenced block; contract-change statement; reason); Q2 (addendum paragraph verbatim in a fenced block); Q3; Executed probes. Plain words; define each term at first use (binary64, ulp, compensated sum, provenance guard, shared half-width).

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
299b1e6dd41059f473818a202c5e1c96138a8a28cdb5cf36deeff2018e241960  exhibit-A-seat-b-finding-b1.md
43978416ca3ad03a53838b9a5a1475bd062806eec0ba85b09f3063d4d32dbfa9  exhibit-B-code-sites.md
65e5b29a82a6b49638b91cf6ec898d2ed72280c32f4b77b64a7bb51cf5154058  exhibit-C-decision-log.md
b5d41a605b78935d01ae3161ea66906219c94b8d454dcba264d49baf67ce2ac3  exhibit-D-kernel-row.md
d4050e5f83b1bac0d4a2537532fc9b8c4a0e343eb443f1e691fea8a494bdda33  exhibit-E-bench-reproduction.md
```
