# Opus contract-lens refuter — ledger head pin vs. acceptance cutoff vs. generator pinned inputs

Read-only. Worktree `/Users/edr/code/JouleWise-wt-pinfix-d0b83820` @ `2f79e633`.

## Recommendation

**Split by authority. Land Part A now; do NOT fixture-stub the generator core test.**

- **Part A (lead authority, clears 1 of 3 failures).** `tests/test_calibration_bracketing.py:634-646`
  asserts `cutoff == pin`, an invariant no contract promises and the production loader already
  contradicts (`joulewise/calibration_ledger.py:2621-2632`). Rewrite to the prefix invariant; add the
  anti-rollback regression **no test currently executes** (Q3-A2).
- **Part B (cold gate / Ed).** The 3 LIVE v5 generators byte-pin a file the contract licenses to
  advance every night (`…d117_floor_qwen3-1p7b_v5/generate_configs.py:2507` vs
  `docs/contracts/calibration_ledger_append.md:286-295`) — a category error, not a stale constant: it
  re-breaks after every future night. Replace the byte pin with the semantic relation (pin
  at-or-ahead-of the acceptance cutoff); drop `file_sha256` from the emitted manifest. Dropping a
  mechanism → rule 11.
- **Interim if CI must be green first:** `expectedFailure`/skip the two generator-core tests, lane id
  in the reason. A skip is honest; a fixture stub reports green while the live generator still raises.

**Rejected.** (i) Bump the constant in all 12 generators — touches the 9 FROZEN ones, authenticated
pack-tree files (`docs/process_traces/2026-09-04-fanout/00-rulings-owed.md:63-64`). (ii) Delete the
drift loop — kills the acceptance/policy/neg8/prompt pins. (iii) Roll the pin back to 76 — forbidden by
D-109 R1.4 (`docs/decision_log.md:7517-7523`); bricks §0.4
(`docs/phase_2/derivation_night_runbook.md:532-542`).

## Q1 — invariant between `ledger_cutoff` and the committed pin

**(b). The contract is not silent — it already says (b).**

D-109 R1.4, `docs/decision_log.md:7511-7516`: "The acceptance artifact pins its **baseline** ledger
head. Evaluation ALSO requires the **independent current-head pin**, verifies **one complete
non-forked chain extension from baseline to current**." A relation permitting an *extension* cannot
require equality. The only equality D-109 states is physical-vs-committed (`:7521-7523`), a different
pair. Same for the contract's typed pin relation (`docs/contracts/calibration_ledger_append.md:278-284`:
`exact`/`physical_ahead`/`physical_behind`/`diverged`, all physical-vs-committed), with `:286-295`
licensing `advance-head-pin` as routine desk work. The runbook states the decoupling outright
(`docs/phase_2/derivation_night_runbook.md:2794-2799`): the terminal pin is committed before the next
night, while the pre-registration's `[SEQ]`/`[DIGEST]` "stay as the FIRST night's pin; they are the
registration's baseline, not a per-night field."

Production already implements (b): `joulewise/calibration_ledger.py:2621-2632` verifies the baseline
digest **is** `receipts[baseline_sequence-1]["receipt_digest"]` and refuses when
`baseline_sequence > pinned_sequence`; `joulewise/calibration_bracketing.py:2020-2027` supplies the
acceptance cutoff as that baseline. (a) is refuted by contract, runbook and code; it held only because
the pin had not moved since `a816036f`.

**Verifying it in CI:** the digest half is unverifiable — the physical ledger is git-ignored and
absent, and no committed prefix witness exists; only **ordering and schema** are checkable from
committed bytes. **Do not invent a prefix-witness artifact**: new contract surface, and the digest half
is already enforced twice at run time (`calibration_ledger.py:2609-2613`, `:2626-2632`). My one
amendment to the lead's (b): the test must **name the weaker property it proves** — today's failure
exists because `..._matches_committed_head_pin` named an unratified invariant confidently.

## Q2 — what `LEDGER_HEAD_FILE_SHA256` should mean

Neither option as posed. The generator **already carries both meanings as separate constants**:
`LEDGER_HEAD_SHA256 = 08456d50…` (`…qwen3-1p7b_v5/generate_configs.py:214-216`) is exactly the
acceptance cutoff digest (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:14`, verified
76 / `08456d50…`); `LEDGER_HEAD_FILE_SHA256 = 6bbe2625…` (`:211-213`) is the byte hash of the *live,
mutable* pin file. The acceptance binding is already present and correct; the file sha is a redundant
byte pin on an append-advancing file. Re-pointing it at "the acceptance" (the lead's leaning) is not
expressible — the cutoff is not a file — and duplicates `LEDGER_HEAD_SHA256`. **Delete it.**

It is inert: the pack passes `--head-pin repo_path(LEDGER_HEAD_REL)` (`:1625`), a **runtime** path
resolved at campaign execution, so pack behaviour never depended on generation-time bytes; and emitted
`issued_ledger_head.file_sha256` (`:2886-2890`) has **zero consumers** (`grep -rn issued_ledger_head`
outside `configs/` and `docs/` is empty). The pin in force at arm is recorded in arm evidence
(`…activation-d8ca3a36/21-arm-evidence-n1-20260919/night_probe_receipt.json`), so no provenance is lost.

**Frozen vs live.** Frozen = the 9 at `tests/test_campaign_generator_core.py:33-45`, each with a
committed pack (`…d117_floor_qwen25_1p5b_v2/plan_tree.json:23`); echo mode only; never edit. Live = the
3 v5 (`:25-31`): `d117_floor_qwen3-1p7b_v5/` and `-8b_v5/` hold **only** `generate_configs.py`, so
editing them invalidates no custody. **Correction to brief fact 2:** the failing tests do not run all
12; `GENERATOR_CASES` (`scripts/check_campaign_generator_core_parity.py:19-34`) is the 3 live ones only.

**Correct test behaviour:** `test_campaign_generator_core` proves the shared write boundary
(`:137-142`), not input freshness. Stubbing the head pin there — as `fixture_prefill_pin` stubs the
prompt pin (`:78-83`) — is legitimate **only after** the live generator stops refusing. The prompt pin
is stubbed because it is an *external* artifact the test must synthesize; the ledger head would be
stubbed to hide a real refusal of a real repo file.

## Q3 — minimal fix-forward

**A1 `tests/test_calibration_bracketing.py:634-646`** — replace `assertEqual(cutoff, pin)` and both
literals with: `cutoff["sequence"] <= pin["sequence"]`; `cutoff["ledger_schema"] ==
pin["ledger_schema"]`; `pin["head_digest"]` matches `[0-9a-f]{64}`; plus a separate genesis floor
asserted against the **r6 path** (not the active default): r6's cutoff is exactly 76 / `08456d50…` and
`pin["sequence"] >= 76`. Rename to `..._is_a_prefix_of_the_committed_head_pin`; docstring says CI
proves ordering + schema only, digest-in-chain being loader-enforced.

**A2 `tests/test_calibration_ledger.py`** — every `baseline_sequence=` in `tests/test_calibration*.py`
is 0, 1, `cutoff["sequence"]`, `plan.final_sequence`, `imported.sequence` or `base_sequence`: **no test
drives `baseline_sequence > pinned_sequence`**, so the D-109 anti-rollback branch at
`calibration_ledger.py:2630` has never executed. Add pin at N, cutoff at N+1 →
`calibration_ledger_baseline_missing` (complements `:637-645`, digest mismatch). This is the fence a
green-CI fix is most likely to be *believed* to cover.

**B1 (gated), the 3 live v5 generators** — remove `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)` from the
drift tuple (`…1p7b_v5:2503-2511`); immediately after, load the live pin and the acceptance artifact's
`ledger_cutoff` and refuse unless schemas match and `pin["sequence"] >= cutoff["sequence"]` (message
`ledger head pin behind the acceptance cutoff: <path>`). Drop `"file_sha256"` from
`issued_ledger_head` (`:2886-2890`), keep `head_sha256 = LEDGER_HEAD_SHA256`, assert in-generator it
equals `cutoff["head_digest"]`, delete `LEDGER_HEAD_FILE_SHA256`. **B2 frozen 9: no diff at all.**

**Regressions with B1:** (i) pin advanced past cutoff → `generate` succeeds, output byte-identical to
the pre-advance emit; (ii) pin rolled back below cutoff → refuses with the new message; (iii) pin
`ledger_schema` altered → refuses; (iv) drifted NON-ledger pinned input (acceptance bytes) on
regenerate → still `pinned input drifted`, preserve mode still exit 0 (shape proven at
`tests/test_arm_readiness_evidence_packauth.py:570-592`).



**Obsolete:** `assertEqual(cutoff, pin)` and the two pin literals (`:640-646`);
`LEDGER_HEAD_FILE_SHA256` in the 3 live generators.

**False-failure surface on the next pin advance.** Part A: none (226 > 76, schema unchanged). B1: none
— pack bytes no longer depend on the pin. Residual, named: (1) a successor acceptance with a cutoff
above 76 still passes A1, the floor being asserted against the r6 path; (2) `acceptance_pin()`
(`…1p7b_v5:492-512`) resolves to r6 in regenerate mode, so a successor issuance drifts the *acceptance*
pin and forces a new generation — intended, not a false failure; (3) under the FAIL route the pin
advances after nights 2 and 3, re-breaking the generator-core tests under today's code but not under B1.

## Q4 — authority boundary

- **Lead:** A1, A2. Correcting a test that over-asserted beyond D-109 R1.4 is not a contract change;
  no mechanism is dropped and a missing regression is added. Record as a defect note, not a ruling.
- **Cold gate / Ed (rule 11):** B1. Removing `calibration_ledger_head.json` from a pack's pinned-input
  set and `file_sha256` from the emitted manifest **drops a mechanism** and changes what an armed
  window's pack asserts about calibration authority — inside rule 11's enumerated prohibitions, and
  hardware/claim-adjacent. Packet question, narrow: *is a monotonically-advancing pin file admissible
  as a frozen byte pin in a generator's drift set?* Cite D-109 R1.4 and contract `:278-295`.
- **Ed only:** any change to the committed pin value or `advance-head-pin` semantics. Not proposed.
- **Line:** editing `tests/` to match an adopted contract clause = lead; editing
  `configs/campaigns/*/generate_configs.py` pin sets or any emitted-manifest field = gated. Neither
  part amends the contract text; B1 conforms code to `:278-295`.

## Q5 — where the lead is wrong

Agreed on Q1 **(b)**, amended: CI can prove only ordering + schema, and the test name must say so.

**Strongest disagreement — the fixture stub.** It makes CI green while the live v5 generators still
raise `ValueError: pinned input drifted` for the operator. Those packs are **unemitted** (only
`generate_configs.py` on disk), so emitting the next window's pack *requires* a successful regenerate.
The stub converts a loud, correctly-timed CI failure into a landmine that detonates at arm time, inside
a scarce quiet window, against the speed-pass directive (arm-to-t0 ≈ 10 min). It also weakens the test:
the generator-core suite is the only executed end-to-end proof the live generators run, and stubbing
the one input that refuses removes the signal that the pin set is unsound. The counter — "the
equivalence FAILED, so a successor acceptance forces a new generation anyway" — is true but does not
save the stub: under the FAIL route the pin advances after nights 2 and 3 too (runbook `:2794-2799`),
so a byte pin on the head file breaks again after every night, forever. Structural, not stale-constant.

**Second disagreement — Q2 framing.** "Acceptance cutoff" is the right semantics, wrong edit: that
binding already exists as `LEDGER_HEAD_SHA256`.

**Fences a naive green-CI fix would remove.** (1) `cutoff.sequence <= pin.sequence` — D-109
anti-rollback at `calibration_ledger.py:2630`, **unproven by any test**; deleting the bracketing test
leaves it with no committed-bytes guard. (2) The drift loop's other four pins. (3) The 9 frozen
generators' custody. (4) §0.4 head-equals-pin, if the pin is rolled back to 76.

## Commands run (all read-only)

- `git log -1 --oneline` → `2f79e633`; `git log -5 --` the pin file → `83831134`, `a816036f` (76), `e39b45e6` (126), `1278b9f7` (176); `cat` pin → 176 / `0f7609ae…`.
- `sed -n` reads of every file:line cited above (contract, decision_log, runbook, `calibration_bracketing.py`, `calibration_ledger.py`, the v5 + v2 generators, three test files, the parity script, `00-rulings-owed.md`).
- greps: `ledger_cutoff` → 6 production consumers; `calibration_ledger_head` in generators → 12 files, all pinning `6bbe2625…`; `issued_ledger_head` outside `configs/`+`docs/` → **empty, no consumers**.
- `python -c`: live pin file sha `6b2d37c8…` ≠ pinned `6bbe2625…`; r6 cutoff 76 / `08456d50…`, epoch 25F84. `ls` of the v5 pack dirs → no committed pack tree for either floor pack.
- `python -m unittest tests.test_campaign_generator_core -v` → **FAILED (errors=2)**: `pinned input drifted: configs/calibration/calibration_ledger_head.json` at `…qwen3-1p7b_v5/generate_configs.py:2511`.
- `python -m unittest …test_live_issued_anchor_authenticates_and_matches_committed_head_pin` → **FAILED**: `{76, 08456d50…} != {176, 0f7609ae…}`.
- `python` scan of all `baseline_sequence=` in `tests/test_calibration*.py` → **no case with baseline > pin**.
- Nothing written outside `/tmp/magistrate-d0b83820/`; no git state changed; no sudo/powermetrics/capture.
