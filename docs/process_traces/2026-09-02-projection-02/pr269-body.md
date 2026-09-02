## V5-PREFILL-REALIZED-PROJECTION-02 — realize registered prompts with the collection encoder at freeze and arm

Rulings 141a P-1..P-10. Each config that registers a `prompt_token_expectation` is
realized through the real runtime adapter at freeze and at arm; the realized
`(token_count, token_ids_sha256, token_hash_domain)` triple must equal the
registered one, the rows are bound into `projection_input_sha256` and the frozen
receipt, and every check is a PASS-status row in the receipt. Legacy packs keep
their exact pre-catcher key set. Merge-base `c5fa8a49`; five files; merge-clean
against `a63d45bd`.

Contract: `docs/contracts/identity_pin_projection.md` (new, 755 lines) — envelope
schema + pasteable example, exact normalization predicates matching
`identity_pins.py:217-236`, a raw-config worked example with recomputable digests
(all independently recomputed by luna 181) and one refusal path, first-use pass.

### Gate record — V5-PREFILL-REALIZED-PROJECTION-02 (D-118 full gate, 141a P-8)

Commits over `origin/main` @ `c5fa8a49`:
- `717b1ddb` Sol xhigh implementation (seat 145), rulings 141a P-1..P-10
- `01a94592` bench cure of Opus contract refuter 151 (F1 hash-binding test, F3/F4/F7 nits)
- `d7bf2ffa` Sol fix round 2 (seat 155) — terra 149 EXE-01 + EXE-03 regressions
- `ae7dd3d8` bench cure of luna delta re-audit 157 (F1 receipt digest, F2 arm mapper)

| Seat | Lens | Findings | Disposition |
|---|---|---|---|
| 149 terra (Sol) | execution / mutation | EXE-01, EXE-02, EXE-03 (all blocker) | all CURED — tests at `test_identity_pins.py:1422`, `:1569`, `:1507`; mutants executed dead (155 V2/V3, 157 V2–V4). Six ruled P-10 mutants killed (149 V1–V6). |
| 150 luna (Sol) | causality | F1 post-arm realization gap (blocker); `transformers_version` filter | F1 RULED OUT as blocker → ruling 150a R-150-1; filter RULED unchanged → R-150-4. |
| 151 Opus 5 | contract | F1 should-fix + F2–F7 nits | F1 CURED (`01a94592`); F3/F4/F7 CURED; F6 CURED (`d7bf2ffa`); F2/F5 accepted, no action. |
| 155 Sol | fix round 2 | none (report `clean`) | Both new tests independently re-verified by 157. |
| 157 luna (Sol) | delta re-audit | F1, F2 (should-fix) | Both CURED in `ae7dd3d8`. |
| 159 Opus 5 | contract + process record (near-final) | CR-01 should-fix; CR-02 should-fix; CR-03 note | CR-01 = P-5's `status: "PASS"` unpinned (mutant survives 87 tests) → 1-line bench cure; CR-02 = no contract prose for the new evidence row → magistrate-owned (P-9 barred the implementer from docs). |

**Written dissent (ruling 150a, R-150-1).** luna 150 labelled F1 — no realization
recheck between the arm receipt and collection — a BLOCKER. The magistrate
DOWNGRADED it to SHOULD-FIX because the gap is pre-existing and not specific to
prompt realization: `_replay_consumed_arm` replays the whole arm receipt, so every
identity unit has the identical post-arm window, and projection-02 neither opened
nor widened it. Follow-up row: **`V5-LAUNCH-REALIZATION-RECHECK-01`** (agent lane,
hard-start dependency: projection-02 merged), with luna's regression adopted
verbatim. Fence R-150-3: no `_v5` night may be armed for CLAIM use until that row
lands; rehearsal and DIAGNOSTIC_NO_PACK nights are unaffected.

**Tests at head** (`ae7dd3d8`, named modules only): `tests.test_identity_pins
tests.test_mlx_runtime tests.test_arm_readiness_integration` → 87 tests, OK
(skipped=5). Wider modules at the last source-changing commit: 183 tests OK
(157 V9), 219 tests OK (149 V7–V11).

**Open, post-merge, by ruling:** (1) 141a P-8 — magistrate freezes and arms a
THROWAWAY generated `_v5` pack against the real Qwen tokenizers before any night
uses it (no real model was loaded by any seat); (2) D-121 terminal review must be
re-run over `d7bf2ffa`+`ae7dd3d8`; (3) ruling 150a R-150-2 follow-up row.

**Post-159 seats (contract doc + delta):**

| Seat | Lens | Findings | Disposition |
|---|---|---|---|
| 160 Sol xhigh | contract-doc author | — | landed in `ec3794e9` after 163/170 |
| 163 terra xhigh | pedagogy + fidelity of the contract doc | R-163-1..R-163-6 | ruling 163a; R-163-1..4 CURED by Sol 170 (`ec3794e9`, incl. sidecar exact-bytes + mutated-sidecar refusal test, mutant killed); R-163-5 launch-boundary recheck RULED to `V5-LAUNCH-REALIZATION-RECHECK-01`; R-163-6 title first-use → bench gloss `c2c1ff08` |
| 170 Sol xhigh | fix round (contract doc) | clean | verified by 181 |
| 181 luna xhigh | delta re-audit of 160+170 | F-163-6-TITLE (should-fix) only; every printed digest recomputed and matched | CURED `c2c1ff08` (7-line plain-words gloss; targeted tests 35+9 OK) |

**Magistrate apex pass (Fable, this PR):** read the full production diff
(`identity_pins.py`, `mlx_runtime.py`) line by line; integration tree = current
`main` (`a63d45bd`) + this branch, merge-clean, targeted modules
`test_identity_pins test_mlx_runtime test_d117_contrast_v5_pack test_night_gate
test_d165_dominance_closeout test_run_night test_docs_freshness` → 252 tests OK;
full suite on the integration tree running locally alongside CI.

**Fresh pass over post-review commit `c2c1ff08`:** prose-only (title gloss); no
code, no test, no contract clause changed; `tests.test_identity_pins
tests.test_docs_freshness` OK.

**Follow-ups registered at merge (kernel transaction):**
`V5-LAUNCH-REALIZATION-RECHECK-01` (R-150-2/R-163-5); 141a P-8 throwaway-pack
freeze+arm against the real Qwen tokenizers — currently BLOCKED by the decode
identity-multiplicity defect (consult 171 → cold gate 182/183, separate branch);
D-121 terminal review re-run over `d7bf2ffa`..`c2c1ff08`; Opus 159 §E process
proposal (clause→assertion map as a brief deliverable) queued for the cold gate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01YFcyS94GeJxpyFGBjPAHx4
