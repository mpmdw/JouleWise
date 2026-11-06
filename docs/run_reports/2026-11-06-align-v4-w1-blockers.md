# 2026-11-06 — ALIGN v4 W1-readiness blockers (lane/2026-11-06-v4-w1-blockers)

Branch `lane/2026-11-06-v4-w1-blockers`, cut from `origin/lane/2026-11-06-v4-r1-integrated`
@ `a2193446d`. Source of the blocker list: the off-Mac prequal inventory
(`lane/2026-11-06-align-v4-prequal` @ `0494d5b3d`, `docs/align/v4/PREQUAL.md`, Remaining 3).

Order of work:
1. Merged PR #686 (`lane/2026-11-06-r0-load-reference` @ `c712318e5`) with `--no-ff`. It
   merged cleanly, and the prequal targets its new R0 load check.
2. Cherry-picked the three prequal commits (`41e9f2c5d`, `105e78c69`, `0494d5b3d`). They
   applied cleanly. `joulewise/align/r0_mlx.py`, which both sides touched, auto-merged:
   `backend_config` is shared and `stack_versions` is kept.
3. Fixed the blockers below. Each behaviour change has a test that fails on the pre-fix tree.
   This was checked by copying the new tests onto the pre-fix head and running them there:
   24 kit failures or errors, 12 prequal, 1 r0_host.

No model weights were loaded. No measurement-Mac or restricted path was read.

## 1. `w1_disk_gate` was never called

- `scripts/align_v4_session.py install` now needs `--w1-disk-config` (the validated R0 desk
  config, read with `r0_runner.validate_config`). The order is:
  1. `kit.require_w1_ready`;
  2. the AC powermode check;
  3. `w1_disk_check`, which calls `joulewise.align.r0_host.w1_disk_gate`;
  4. the shared installer.
- If the gate returns anything but `pass`, the arm is refused and the installer is never
  called. The refusal names the free bytes, the requirement and every offload row. On a
  pass, the receipt is kept as `<session>/staging/w1_disk_gate.json`.
- `align_pilot_session.main` gained an optional `install_options` hook. The v3 defaults are
  unchanged.
- R0's report-only disk row now carries `w1_requirement`. It reports what the gate will
  require: bytes needed, whether free space would pass now, the shortfall, and the offload
  labels re-hashed at arm. It uses the gate's own constant
  (`r0_host.W1_REQUIRED_FREE_BYTES` = 80 decimal GB), so the two cannot diverge. The R0
  markdown prints it.
- Runbook step 2 names the call site.

## 2. `sizing_b5.json` was missing

- What consumes it: `bytes_h_session.prepare` (`registration.load_sizing`, span,
  footprint, disk terms, member count) and `b6.plan_inputs.build` (`programmed_span_s`,
  `T_stream_max_s`).
- FINAL-DESIGN B8 says W1 sizing comes from R1. So it cannot be committed before R1 without
  inventing member costs.
- What the kit now does instead:
  - The R1-filled copy of `night_plan.template.json` is committed as
    `configs/campaigns/align_v4/registration/w1_plan.json`.
  - `build_files` validates it with `validate_align_v4_w1_plan.validate`. That function now
    takes an in-memory `collection_plan`.
  - The kit then derives `registration/sizing_b5.json` (`kit.derive_sizing`):
    - per-member `member_s` from R1;
    - `programmed_span_s` = ceil(scaffold + Σ member_s);
    - `window_max_s`;
    - `T_stream_max_s` = max member_s ≤ 1,800 s;
    - disk per member = ceil(pilot-3 OLS bundle_bytes(member_s) + largest positive residual),
      plus the measured pilot-3 scaffold bytes, two copies. The law is read from the frozen
      `align_pilot_v3` sizing at `83e2dac59`, as in FINAL-DESIGN §2.5.
  - At the Amendment-1 planning member_s this reproduces span 26,927 s, window 44,640 s and
    **18.71 GB per copy** (tested).
- Until `w1_plan.json` exists, `--check`, `prepare` and `install` (`kit.require_w1_ready`)
  refuse with: `sizing_b5.json is not derivable yet … FINAL-DESIGN B8 … commit it as
  registration/w1_plan.json …`. If `sizing_b5.json` is stale or absent beside a committed
  plan, they refuse as well.
- The derived file loads through `registration.load_sizing` and `plan_inputs`.

## 3. The D artifact sha was null (WP11)

`registration/inputs.json` WP11 now holds three entries.

**`identity_unit`:**
- the pinned source, name and revision `815b83c0`;
- `model_artifact_sha256` = folded `a8d1c5c963787dd9dc524912e05d409172124da773d196e8f5123820b4c36b30`;
- `flags: ["runtime_stack_unobserved"]`;
- the kit adds `stack_identity: {}`, as for the inherited 30B units.

**`artifact_inventory`:** the R0 re-run's governed `model_artifact_identity` verbatim
(`records/2026-11-06-align-r0-v4-rerun` @ `a1c2e8900`, `report.json`
`/checks/3/load/model_artifact_identity`, model-load `pass` on Mac15,9).

**`local_file_verification`:** status `verified`, plus:
- the record's sha256 (`857ed285…`);
- the pins file sha256;
- a scope note. It covers the weight shards only. The non-weight files go through
  `align_v4_verify_d_pins.py`. The same run's load (NLL) failure is a separate verdict.

Independent check: `kit.validate_d_identity` requires every shard's sha256 and size to equal
the HF LFS pin in `configs/align/v4/qwen38-27b-8bit-hf-pins.json`. The folded sha must
recompute **from the pins alone** (it does: `a8d1c5c9…6b30`). The unit, inventory and
verification must agree. `require_w1_ready` and the prequal `kit` check run it whenever
WP11 is filled. Tampering with a hash, a size, the root, the revision or the status is
refused (tested).

Regenerated kit:
- the D units in `identity_pins.json` carry the 64-hex sha and load through
  `registration.load_identity_pins`;
- `--check` no longer lists WP11.

## 4. WP18 X/Y `max_turns` and token fixtures

These values cannot be derived off the Mac:
- FINAL-DESIGN §2.5: `max_turns` = that member's recorded pilot-7 turn count.
- Amendment 1: both arms stop at the recorded pilot-7 turn count.
- CHAIR ruling 9(d).
- Plan WP18: inputs are the b-e25 and b-e18 `align_turns.jsonl` from the pilot 6-7 offload
  copy and `p7-PILOT.json`, owned by the lead and the magistrate on the Mac.

The committed pilot-7 configs only carry the 12-turn ceiling and a 120 s guard. The design
forbids using them as a fallback. The pilot-7 desk record carries no per-member turn counts.

The placeholder stays, but the kit message now says exactly what it needs:
- `align-pilot-v3-episodes-b-e25` (spam/sabotage, index 16) and `-b-e18` (spam/benign,
  index 14);
- recorded pilot-7 turn count, never the 12-turn ceiling;
- the fixture sha source and the authority.

## 5. `R0.reasoning_effort`

The kit message reads `R0: R0.reasoning_effort stays a placeholder until R0 passes.` A
filled but invalid value gets the same sentence, plus the valid rungs.

`require_ready` now appends a reason for every pending owner (`PENDING_REASONS`) after the
unchanged `v4 kit BLOCKED by placeholders: <paths>` prefix.

## Prequal (`joulewise/align/prequal.py`, on this branch)

- **Sibling NLL entry.** The sibling has its own explicit reference entry in
  `configs/align/v4/prequal_sibling_nll_reference.json`:
  - mode `reference`;
  - keyed by `87e768fb…` and fixture `792beb56…ac42`;
  - HF fp32 0.4669;
  - bins from `lane/2026-11-06-r0-d-nll-diagnosis` `results/qwen35_08b_stream.json`;
  - D's ±0.10 / ±0.5 bar.

  The upstream 0.8B revision was not recorded by the diagnosis. `Qwen/Qwen3.5-0.8B` main
  has had no commit since 2026-03-02, so it is `2fc06364`. This basis is recorded in the
  entry.
- **Sibling revision.** `SiblingBackend` sets `nll_reference_revision`, so the verdict can
  never borrow D's entry.
- **`check_load`.** It passes that table to `r0.load_coherence`. It now requires:
  - `nll_verdict.status == pass` on the sibling's own entry;
  - R0's generation check to have run end to end: rendered prompt, greedy first attempt,
    decoded tokens, `tool_envelopes` accounting, a verdict, and no `schema_ref_unresolved`.

  The generation outcome and R0's overall load status are reported as diagnostics.
- **`d-pin-verifier`.** Now reflects PR #686 (`f1ae2d3be`): top-level `.cache/huggingface/`
  bookkeeping is counted, not compared, and a nested path still fails.
- **New `w1-plan` check (the R1 kit checks).** It verifies:
  - the template has no drift;
  - the validator refuses the PENDING_R1 template only for its placeholders;
  - L1 and fit-rule self-tests reproduce the planning span 26,927 s;
  - at `--stage w1`, the committed `w1_plan.json` validates against inputs and r1_slots,
    with `sizing_b5.json` beside it.
- **`kit` check.**
  - Readiness is `require_w1_ready`.
  - A filled WP11 must bind the pins at any stage.
- **`implementation_sha256`** adds the NLL tables, the validator and `inputs.json`.

## Still blocking W1 (by design)

- WP18: Mac-side.
- `R0.reasoning_effort`: until R0 passes.
- R1: `B_D`, `I_D`, `T_dead`, `thermal_policy`, r1_slots, and the filled `w1_plan.json`
  (which yields `sizing_b5.json`).
- WP15: `runtime_entrypoint`.

## Tests

Every run was one module per process, under `nice -n 19 taskpolicy -b`, with
`TMPDIR=/private/tmp/jwr4-tmp` and `/private/tmp/jwsol/venv-both/bin/python`.

All of these passed on the code head `14d15d46e`. This report is the only later change, and it adds docs only.

| Module | Result |
|---|---|
| tests.align.test_v4_kit | Ran 54, OK |
| tests.align.test_v4_prequal | Ran 33, OK (skipped=3: tokenizer tier, needs JW_PREQUAL_HF) |
| tests.align.test_r0_host | Ran 20, OK |
| tests.align.test_v4_w1_plan | Ran 10, OK |
| tests.align.test_r0_checks | Ran 29, OK |
| tests.align.test_r0_load_reference | Ran 34, OK |
| tests.align.test_r0_load_reference_adversarial | Ran 13, OK |
| tests.align.test_r0_documentation / _scheduling / _integration / _progress / _dispositions | 3 / 12 / 3 / 3 / 3, OK |
| tests.align.test_v4_verify_d_pins / test_v4_powermode_record / test_window_reference_custody | 5 / 7 / 4, OK |
| tests.align.test_r0_mlx / test_thermal_gate | 7 / 39, OK |
| tests.align.test_v4_w1_synthetic | Ran 18, OK (skipped=14); with `JW_WP22_FULL=1`: Ran 18, OK (expected failures=2) |
| tests.test_align_pilot_session | Ran 16, OK |
| tests.align.test_pilot2 / test_pilot2_round1 / test_pilot3 / test_pilot4 | 11 / 18 / 7 / 18, OK |
| tests.align.test_decode_budget / test_apple_endpoint | 21 / 9, OK |

There is also an end-to-end runner smoke test:
`scripts/align_v4_prequal.py --offline --only r0-config,kit,w1-plan,d-pin-verifier`. All
four checks pass, and the report is `incomplete` (exit 3), as designed.

The sibling-model `load` check was not run live, because this lane loads no model weights.
Its new logic is covered with a faked `load_coherence` and a faked backend.
