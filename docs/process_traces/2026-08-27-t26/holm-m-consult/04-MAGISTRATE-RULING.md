# Magistrate ruling — the gamma analysis manifest is inadmissible as generated (D-157; T26, 2026-08-27)

Three seats (Sol xhigh, Opus 5, Fable 5) answered the same four questions
blind and converged on every load-bearing fact. This ruling binds the
pre-window worklist as **W-10** and gates the transaction night. Ed can
reverse it by a word; the arithmetic is below so the call is his.

## Findings (three-seat convergence, each verified at file:line)

F-1. The reported line (`analysis_manifest_v3.py:476`) is the LEGACY
one-contrast Splitwise family; m=1 is correct there. The real defect is
in the D-117 gamma pack generator
(`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`
~:948-986, ~:1521-1554): decode multiplicity m=1 with a "contingent on
unresolved ratification" note; the prefill_p256 contrast's test,
multiplicity and floor dependency left as `EMPTY … TODO(lead authority)`;
no top-level `families` block. D-139 A2 (2026-08-17) ruled exactly these
values and said they "enter the gamma prospective manifest's families
block at the production freeze". Nothing in D-140..D-155 executed it;
RUN_STATE §4 still carries them as RULING-REQUIRED; the `_v4` planning
corpus (nr-synthesis, packet-5, W-0..W-9) never mentions it.

F-2. The estate-10 `_v4` manifest preserved from the S-0 clone proof is
identical in kind (no `families`, decode m=1, prefill EMPTY,
`draft_status: as_generated_pre_d134_freeze`). The prospective validator
`validate_prospective_analysis_manifest_v3` has NO callers outside its
module and tests — the freeze path (U11 projection, readiness receipt,
`arm_readiness.py:4948-4963`) never validates the analysis manifest. So
S-0 passed end to end while minting bytes the consumption edge would
refuse post-window.

F-3. m is byte-bound: the `families` array is inside the semantics
projection digest (`analysis_manifest_v3.py:1531-1541`, `:1645-1659`),
the manifest SHA is pinned by `plan_tree.json`, finalization copies
`families` verbatim and requires equal semantic hashes (`:3661`), and
claim-time validation requires `family.m == len(contrast_ids)`
(`analysis_engine/artifact.py:1574-1577`). Post-mint correction is a
non-config cure → new family generation (D-140 no-repair, D-153).

F-4. Publishing two contrasts under m=1 would be anti-conservative
(FWER ≈ 9.75% not 5%) — but it is also mechanically unreachable, because
the edge refuses first. The live failure mode is a DEAD CLAIM EDGE after
a 168-hour campaign, not a wrong number.

## Rulings

R-1. **W-10 is added to the pre-window worklist and the transaction night
is gated on it.** Install D-139 A2 into the gamma generator by a
production resolver: ONE family `{holm, alpha 0.05, q null, m 2}` with
both contrast ids; `family_instance_id` stamped on both contrasts;
prefill test `two_sided`, direction positive, dedicated p256 floor
dependency; the full prospective top-key set (`freeze_status`,
`families`, `design`, `finalization_contract`, …); the contingent note and
TODO slots deleted; plan-tree digest recomputed; regenerate.

R-2. **Close the class, not just the instance.** The freeze/readiness path
gains an admission check: it runs `validate_prospective_analysis_manifest_v3`
(and null-p-value multiplicity admission, `len(p_values) == m`) on the
manifest it is about to pin, and REFUSES the mint on any finding with a
registered reason. This is the same defect shape as S0-O2, 3e/3f and
NR-13 — a contract-required input with no route or no check at the
producer — and it is the third time this session that shape has cost a
gate. Regressions: a generator emitting m=1 with two contrasts, or an
EMPTY prefill slot, or a missing `families` key, is refused AT THE MINT;
the regenerated manifest is admitted; the contingent-m=1 tests
(`tests/test_d117_decode_contrast_plan.py:2487-2502`) are replaced and a
PRODUCTION m=2 test added (the shared-m=2 fixture is explicitly "not a
production multiplicity ruling", `tests/test_analysis_manifest_v3.py:98-100`).

R-3. **R-2 touches the mint path, so S-0 re-runs as ESTATE 11** at the
new reviewed head before the transaction (D-155's own rule: the clone
proof is the proof). Cost per the seats: about half to one day of Sol
work plus ~10 min and three MLX freezes for the estate.

R-4. **The post-window "analyze under m=2" path is REJECTED** — all three
seats: it contradicts D-139 ("enter … at the production freeze") and
D-140 (no post-mint repair), it would be post-hoc family selection, and
the bytes as they stand are refused regardless of m.

R-5. **Changed-set consequence.** Generator and regenerated pack files
change before derivation, so they do not grow the `_v4` changed set; the
S8 scope note reports every file whose bytes change and whether any sits
in the 112-entry pinset or the D-151 conditions, and the runbook Phase A
re-declares the reviewed head at session time as it already does. If S8
finds a pinset or D-151 collision, that returns here as NEEDS-RULING
before the PR merges.

R-6. **Ed's date.** Earliest credible transaction night moves from
2026-08-28 to the first free night after W-10 merges and estate 11 is
green — realistically 2026-08-29/30. The alternative (mint on 08-28 with
the inadmissible manifest) buys nothing: the campaign would run and its
claim edge would refuse. Recorded as D-157.

## Custody

`01-sol-seat.md`, `02-opus-seat.md`, `03-fable-seat.md` (verbatim);
implementation stream S8 on `fix/d139-a2-gamma-families`, scope note under
`../d139-families/`.
