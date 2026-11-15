# Seat: mythos, #790

`date`: Sat Nov 14 21:39:15 PST 2026. Head `dd09ba7ea`, base `c3f4bacd8`, worktree `/Volumes/JW-EXT/scratch/mythos-790/wt` (clean before and after). Synthetic records only. Nothing pushed, no PR edit or comment.

## Verdict: ADMIT WITH FIXES

The code does what RL-148 §2 and RL-156 §3.1 ask, and I found no defect in it. One fix is owed before the merge and needs no new head: the "costs no Part C" claim must disclose an import edge (finding 1). One stale docstring is in a touched file (finding 2). The rest is optional.

## The five checks

1. **Receipt path closed: yes, for D.**
   - **Cap.** `check_r1_budget_and_policy` pins `thermal_policy.g0_cap_s` to the re-derived `g0_cap_w1.value_s`, which is clamped to at least 600 s (`align_v4_kit.py:683`, `:1010`). My probe refused 200, 599, 599.999, 0, `True`, an absent cap, a hand-edited `g0_cap_w1` slot and `heavy: false`.
   - **Key.** Refused by `require_ready` first (`:1088`), by `check_r1_budget_and_policy` (`:1007`) and by the plan validator (`validate_align_v4_w1_plan.py:157`), also when its value is `None`.
   - **File.** Refused by existence, also when it is a directory.
   - **Arm.** `prepare` and `install` both run `generate(check=True)` (`align_v4_session.py:56`, `:1695`). Later windows clone W1 member 5.
   - **CLI, environment, templates.** `sign` and `--draft-out` are rejected by argparse. None of the changed files reads an environment variable, and no code path reads a G0 cap from one. No `g0_cap_receipt` remains under `configs/`.
   - **`thermal_gates`.** It still accepts a 200 s cap with a well-formed stanza and checks nothing about the digest, so the kit is the only barrier.
   - **Contrast members.** They can still arm below 600 s (R11). D cannot carry that: `gate_policy_fields` strips `contrast_fit` for D.
   - **Base against head.** Over 260 perturbed synthetic records, nothing refused at base is admitted at head. 47 are newly refused, all by the new timeout count. Every head admission carries 600, 625 or 1,200 s.
   - **Residuals.** Findings 3 and 5.

2. **Deletions break no caller.** An AST diff gives 12 kit names, `sign` and `_draft`, and `RECEIPT_ONLY` deleted. `git grep` finds none of them outside the test that asserts they are gone. No `receipt=` call or `--draft-out` use remains. Tests are below.

3. **Pins are exact.** The generator wrote 30 files into a scratch root and none differs from the committed bytes.
   - `align_v4_kit.py` is `3c46faa2…56ce`, the `plan_tree.json` generator value.
   - `plan_tree.json` is `b4711a5e…a622`, the `tree_sha256` in `identity_pins.json`.
   - The template regenerates byte-identically.

4. **No changed path is in any of the three lists.** The 17 changed paths have nothing in common with:
   - the ten `R1_EXECUTED_SOURCES`;
   - the five named Part C files;
   - the 37 frozen paths of `cl-dev-01.json` at `589748f15`, which hashes to `c76344c5…66d7`.

   The claim is true as stated. Finding 1 is the caveat.

5. **The partial handling of the row-1 LOW is sound.**
   - **The refusal cannot trip on a driver row.** In `thermal_gates._wait`, a timed-out G1 writes one `thermal.gate_timeout:` flag and one interval (`:623-646`). Hold timeouts use another prefix, and the driver counts by that prefix (`align_r1_rehearsal.py:790`).
   - **Refusing an unflagged at-cap wait would refuse valid rows.** An unobserved G1 runs to the cap and is flagged `thermal.state_unobserved`, not a timeout (`:620-622`).
   - **The flag does not change the arithmetic.** When any wait is at or above the cap, `max(cap, largest)` equals `largest`.
   - **Base against head.** Over 4,000 random rows, the 1,266 admitted by both have identical arithmetic, 2,734 are newly refused and none is newly admitted.

## Findings

1. **LOW (claim; no code). "Costs no Part C" holds on the lists, but Part C imports the changed kit.**
   - **Evidence.**
     - `run_align_r1_smoke.py:348` launches `align_r1_followup_kit.py`, which imports `align_v4_session` (`:22`), which imports `align_v4_kit` (`:34`). Importing the follow-up kit loads `scripts/align_v4_kit.py`.
     - The R1 driver imports six kit names lazily (`align_r1_rehearsal.py:151`, `:1273`, `:1529`, `:1792`) and reads `night_plan.template.json` through them.
     - Part C's stack preflight reads `identity_pins.json`.
   - **Nothing reached has changed.**
     - The six names are AST-identical between base and head: `DEADMAN_FACTOR`, `L1_MARGIN_S`, `MEMBER_CAP_S`, `l1_t_dead`, `w1_inter_member_idle_s`, `r1_g0_timeout_s`.
     - The template lost only the receipt slot; the driver reads `members`.
     - The pins changed only `tree_sha256`; the preflight reads `runtime_versions`.
   - **Fix.** Say this in the PR body's scope check, and have the lead record it at the merge under RL-156 §4.1 so the research lead's cold pass confirms the carry explicitly.

2. **LOW (text). Stale docstring in a touched file.** `scripts/align_r1_to_w1_chain.py:11` still reads "6 decide: the R10-2 budget procedure (writes a receipt draft when needed)".
   - **Fix.** "the budget procedure (RL-148 section 2; prints the step, drafts nothing)". It moves no pin.

3. **LOW (optional). The generator without `--check` still writes a receipt-armed D config.**
   - **Evidence.** With `g0_cap_s` 200 and the key in the inputs, `build_files` returned a D spec carrying both, and `validate_gate_policy` accepted it.
   - **Limits.** This holds only while no `registration/w1_plan.json` is committed; after that the plan validator inside `build_files` refuses. `--check`, `prepare` and `install` refuse in every case, so it cannot arm.
   - **Fix.** Call `refuse_ruling_1f_receipt` at the top of `build_files`. In the PR body, change "before any policy reaches it" to "before any prepare or install".

4. **LOW (optional). The unflagged count is recorded where few will look.**
   - **Evidence.** `g1_waits_at_cap_unflagged` appears only under `typical_case.runs` in `decide`'s JSON. `--check` discards it, and `decide` adds no `notes` line as it does for the duty bar and the contrast. The count compares against W1's `turn_cap_s`, which is the cap R1 armed only when the picks did not change.
   - **Fix.** One `notes` line in `decide` when any run's count is above zero.

5. **NIT. A dangling symlink at the receipt path is not refused.** `Path.exists()` is false for it. It is harmless because nothing reads the path.
   - **Fix.** `os.path.lexists`, if the kit is opened again.

6. **NIT. Leftovers.**
   - The test name `..._on_receipt_and_no_receipt_paths` (`test_v4_r11.py:74`).
   - The `RoleCapTests` docstring.
   - `test_pr777_attack_repros.py:239` asserts on a key that no longer exists, so it is vacuous.
   - `align_v4_kit.py:1438` pops a key no D policy can carry.
   - `max_fitting_b_d` has no production caller left.

7. **NOTE. Docs outside the diff still describe the signed-receipt route as live.**
   - `docs/align/r1_runtime_contract.md:163` and `docs/align/v4/U3-transfer.md:44`.
   - `pilot_protocol_v4.md:374` and `:387-399`, which is registration text and is left for RL-148's amendment, as the PR says.
   - No DEVIATIONS row records the retirement; RL-156 §3.1 did not ask for one.

## Tests run at `dd09ba7ea`

`python3.13 -B -m unittest`, one module at a time, `PYTHONPATH=.:tests`, private TMPDIR.

| Module | Result |
|---|---|
| `test_w1_kit_r10` | 21 OK |
| `test_v4_r11` | 27 OK |
| `test_rl149_typical_case` | 13 OK |
| `test_v4_w1_plan` | 12 OK |
| `test_w1_tf08_record` | 12 OK |
| `test_v4_registration` | 24 OK |
| `test_r1_runtime_e2e` | 2 OK |
| `test_w1_prequal`, whole module | 42 OK in 1,484 s (second attempt) |
| `test_w1_prequal` classes `ChainTests`, `KitReadyTests`, `SizingTests` | 1, 1, 2 OK |

- **Prequal, first attempt.** It was stopped at 1,800 s after 15 passes and no failure. Load average was 30 to 37 on 10 cores while it ran. I could not list processes, so I cannot say whether that was the module's own workers or other jobs.
- **Also OK (23 further modules).** `test_r1_to_w1_chain` 6, `test_identity_pins` 42, `test_v4_kit` 116, `test_w1_rl122_kit` 14, `test_pr777_attack_repros` 15, `test_v4_executed_closure` 6, `test_v4_dynamic_closure` 10, `hazards.test_refusal_allowlist` 24, `test_v4_prequal` 36, `test_v4_w1_synthetic` 22, `test_v4_receipt_tiers` 8, `test_r1_round5_exec_review` 7, `test_r1_round2` 14, `test_r1_round3` 8, `test_r1_round6_lows` 18, `test_km003c` 25, `test_w1_3a_desk` 26, `test_protocol_v4_doc` 6, `test_r1_turn_counts_export` 13, `test_smoke_review_sol1` 21, `test_r1_rehearsal` 79, `test_rl145_part_c` 31, `test_r1_followup` 12.
- **Counts** match the PR body wherever it lists them.
- **CI.** `gh pr checks 790` shows all 12 `test` shards passing on this head.

## Not checked

- The whole suite locally.
- The pins at the two intermediate commits.
- A dynamic trace of a real Part C; finding 1 rests on static reading and an import probe.
- The parallel seat's report, which I have not seen.

Probes and logs are in `/Volumes/JW-EXT/scratch/mythos-790/probe` and `testlogs`. I added a second worktree at the base for the comparisons and removed it afterwards.