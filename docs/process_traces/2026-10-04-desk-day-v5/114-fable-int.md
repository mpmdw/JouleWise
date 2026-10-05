FINAL PASS: FAIL

# Cold final pass on PR #483 (`898c49a7`, feat/2026-10-05-v5-qualification-code)

Seat: Fable 5.1, cold, one session, read-only on the checkout. Scope read: the full `joulewise/` and `scripts/`
diff against `origin/main` (6,639 diff lines), ruling 76 with addenda A and B, record 42. Scratch only under
`/tmp/dd5-fable-int/`.

## Ruling in one paragraph

The admission side is sound: I found no path by which this change admits a window or a member that should be
refused, and the drift-corrected clock check is fail-closed and consistent across its four users. The change
fails on the other side. Two of the eight live qualification gates (G1 and G9) cannot return PASS on a real `s1`,
for reasons that are fixed by the code and independent of how the machine behaves. Both were confirmed by
execution. `s1` would run its one launch correctly, and the qualification harvest would then print
`verdict=FAIL` with `end_state=true`. That is exactly priority 5 (a good window refused only after the launch is
consumed). Do not arm `s1` on this head. `a1`/`a2` (arm-only, no harvest through G1/G9) are not affected.

The common cause of both blockers: every test at these seams feeds the evaluator a hand-written record or mocks
the evaluator. No test passes a real producer's output into the real evaluator.

## Findings

### B1. BLOCKER (priority 5). G9 rejects the custody layout that the plan writer, the night gate and the desk close-out all require

Terms: the *plan custody root* is `plan.custody_root` (holds the night directory, the T-0 inputs and the ARM
receipts). The *ARM custody root* is `arm_context.custody_root`. This change makes them two different,
non-nested directories ("two-root").

- Two-root is mandatory: `scripts/write_v5_qualification_plan.py:563`, `joulewise/night_gate.py:1232`
  (`root == custody and not legacy_rehearsal` refuses), `scripts/v5_s1_desk_closeout.py:152`.
- The qualification harvester loads the bundle from the plan custody root
  (`scripts/harvest_v5_qualification.py:42,75`), and G9 itself looks the ARM receipt up under
  `bundle.custody_root/<pack>/arm_readiness.receipts` (`joulewise/t0_rehearsal.py:1284`), so
  `bundle.custody_root` is the plan custody root.
- G9 then requires `desk_sources["custody"] == str(bundle.custody_root)` (`joulewise/t0_rehearsal.py:1293`).
  `desk_sources["custody"]` is the ARM custody root. The two are required to differ, so this line always fails:
  `desk backup roots differ from the s1 ARM/plan`.
- Independently, the close-out adds a fourth copy `night_custody` to both backups
  (`scripts/v5_s1_desk_closeout.py:155`; its own test asserts four keys, `tests/test_v5_s1_desk_closeout.py:108`),
  while G9 requires the copy set to equal the three registered sources (`joulewise/t0_rehearsal.py:1300`):
  `backup does not cover both s1 runs roots and custody`.

Evidence (scratch test `/tmp/dd5-fable-int/test_g9_native.py`, built on the PR's own passing G9 fixture):

```
baseline fixture (single root, three copies)      -> G9 PASS
+ night_custody copy, as the close-out writes     -> G9 FAIL | backup does not cover both s1 runs roots and custody
+ ARM custody root != bundle root, as required    -> G9 FAIL | desk backup roots differ from the s1 ARM/plan
```

Why the suite is green: `tests/test_v5_s1_qualification.py:195` builds the G9 fixture with
`sources["custody"] = str(self.root)` (single root, a layout the night gate refuses), and
`tests/test_harvest_v5_qualification.py` mocks `evaluate_qualification`.

Consequence: G9 FAIL -> `g9_not_passed`, `cause_classes=["qualification"]`, `end_state=true`
(`scripts/harvest_v5_qualification.py:93-94`), after the launch and after both create-once backup destinations
are used.

### B2. BLOCKER (priority 5). G1 fails any `s1` whose T-0 census was clean

G1 (as ruled in 76 decision 4, and implemented literally) passes a governed process only on exit 0, except the
agent census, which must exit 1 with empty stdout (`joulewise/t0_rehearsal.py:693-698`;
record construction `scripts/produce_t0_rehearsal_bundle.py:501-502`).

The `s1` driver wraps its whole run in the process journal (`scripts/run_night.py:4958`) and authors the T-0
evidence in-process (`scripts/run_night.py:2289`). The author's probes go through the journaled seam
(`joulewise/arm_readiness_evidence_t0.py:463`). Its process census runs four `pgrep` probes and *requires*
exit 1 with empty stdout on each (`joulewise/arm_readiness_evidence_t0.py:1797-1803`, `_expect_absent` at
`:1361`): `pgrep -x caffeinate`, the agent census, the browser census, the monitor census. So:

1. Three non-agent censuses must exit 1 for the author to admit the window, and must exit 0 for G1 to pass.
   A window the author admits is a window G1 fails.
2. The author's agent census is spawned with `wait()`, not `communicate()`, so the journal has no `output` event
   for it; the assembler records `stdout: None`; G1 requires `""`.
3. Same class, not separately executed by me: the group-absence census `pgrep -lf -g <pgid> .`
   (`scripts/run_night.py:4372`) treats exit 1 as the good answer and is journaled as an ordinary governed process.

Evidence (scratch test `/tmp/dd5-fable-int/test_g1_native.py`: the real `_execute_probe` under a real journal,
mapped with the assembler's rule, judged by the real `evaluate_g1`):

```
journaled: pgrep -x caffeinate -> exit 1, fd0 /dev/null ; browser census -> exit 1 ; ...
G1: FAIL | governed process 1 did not complete successfully | sequence_completed: False
```

This is a defect in ruling 76 decision 4 as much as in the code: the ruling registered one exit-1 process and
the driver has at least five. The cure needs a ruling addendum (a registered expected outcome per governed argv,
or a journal scope that excludes the author's own probes), not only a code patch.

### M1. MEDIUM (priority 3). `replay-locators.json` is on the public side and carries per-member timing

`joulewise/v5_qualification.py:287-288` writes `replay-locators.json` at the archive root, beside `harvest.json`
and outside the mode-0700 `withheld/` directory. Each source file row comes from `scripts/harvest_window.py:57`:
`{"mode", "size", "mtime_ns", "sha256"}`. For every member bundle that gives nanosecond modification times of
`config.json`, `events.jsonl`, `powermetrics.raw.txt` and `summary_metrics.json`, plus the byte size of the raw
sampler file. Differences of those times are per-member durations; the raw file size is proportional to stream
length. No energy or power value is exposed. The blindness test checks only `l10-a/record.json`
(`tests/test_harvest_v5_g2b_window.py:459-471`). Both harvesters are affected. Cure: write the locators under
`withheld/` (re-harvest reads them from the previous archive, which still works), or drop `size`/`mtime_ns`
from the public copy. Everything else I traced is structural: both `harvest.json` records, the stdout line
`verdict=...`, `l10-a/record.json`, the plan writer's refusal output, and the durable push (fixed allowlist at
`scripts/run_night.py:1275`, with the raw chain logs excluded for non-claim purposes at `:1377-1387`; the
`night/rehearsal-lifecycle/capture/` copies of raw sampler files are not on that allowlist).

### M2. MEDIUM (priority 4). The structural G2-b verdict depends on a qualification-only artifact

`scripts/harvest_v5_g2b_window.py:508` and `:592` make the G2-b harvest resolve and replay the G10 custody tree.
`replay_g10_custody` requires the copy at `<plan custody>/records/g10-custody/<name>`
(`joulewise/v5_qualification.py:167`), which only the qualification bundle assembler creates. If assembly has not
run or faulted, or a G10 locator digest has moved, the G2-b harvest ends REFUSED (or exits through
`preflight_refusal` before archiving). Ruling 76 decision 5 keeps producer faults out of the G2-b verdict; this
is REFUSED rather than RECOVER, so the letter holds, but a qualification-side fault still blocks the structural
verdict, and the two harvests acquire an undocumented order (assemble first, or the night-custody census changes
between harvests and re-harvest refuses with `reharvest_source_bytes_changed`).

### M3. MEDIUM (priority 1, latent, not this block). The frequency gate is enforced by pack directory name

Ruling 76 addendum B item 2 says: at every R0, arm only if the inequality holds. The code requires the gate file
only when `pack_root.name == "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"`
(`scripts/capture_t0_step.py:822`, `joulewise/arm_readiness_evidence_t0.py:775`). For any other pack the capture
records `t_stream_max_s: null` and the author, the ARM re-check and G4 all skip the inequality. The ALPHA/BETA
floor packs would arm with no frequency gate. The per-member `bounded` obligation still protects the joules, so
this is not an admission of a bad number, but it is a ruled arm condition that silently does not apply to claim
packs. Fix before any claim arm; no effect on `a1`/`a2`/`s1`.

### L1. LOW. Notes that do not change the ruling

- G10 inside the bundle: `evaluate_g10` looks for `anchor-movement.json` beside `records/positive-control.json`
  (`joulewise/t0_rehearsal.py:1709`), where the assembler never puts it, so the in-evaluator test is always the
  legacy absolute-movement form. The residual form is still enforced, by `replay_g10_custody` ->
  `verify_g10_custody` on the retained tree. Correct outcome, misleading code.
- `_qualification_observe` catches `BaseException` (`scripts/run_night.py`, new helper). An interrupt that lands
  inside the one HID probe is recorded as a producer fault and the driver carries on. Bounded (10 s probe) and
  it errs toward completing the window.
- The ledger head pin may now be any committed path in the checkout rather than the one fixed path
  (`joulewise/arm_readiness_evidence_t0.py` `_derive_ledger`). It stays bound to the pinned `window.env`; noted
  because it widens a claim-path input.
- Finalizer and provenance checker now replay the ledger from the acceptance cutoff
  (`joulewise/analysis_manifest_v3.py:3641-3656`, `scripts/check_window_provenance.py:314`). Read, not
  independently exercised.

## The five questions

1. **Admit what should be refused, or let a non-claim byte reach a claim path?** Nothing found. Live consumption
   still runs with `require_current_boot=True` and expiry (`joulewise/arm_readiness.py:10621-10629`); the relaxed
   launcher-identity and ARM-semantics replays apply only to historical replay. Qualification PASS cannot release
   measurements (`release_metrics` always refuses). `s1` bytes stay behind `claim_eligible=false` and
   `G2B_SHAKEDOWN` at the plan, GO, harvest and evaluator. Open item: M3.
2. **Does the drift-corrected check still catch a real reset?** Yes. The acceptance band is the same 10 ms wide
   as before, re-centred on the predicted drift `f_R0 x span`, in exact rational arithmetic
   (`joulewise/kernel_clock.py:88-95`). A step over 5 ms fails the residual; a rewrite of the frequency word
   fails the equality test; an unreadable or malformed probe fails closed. Right after a resync: R0's word is
   read before and after the reference batch and again after OFF (`scripts/capture_t0_step.py:748-763, 810-813`),
   so a word still being adjusted cannot become `f_R0`. The four users agree: author
   (`arm_readiness_evidence_t0.py:1205-1223`), ARM re-check including the live leg (`arm_readiness.py:6873-6950`),
   G4 replay bound to the custodied R0 probe (`t0_rehearsal.py:890-909`), helper and its verifier
   (`capture_t0_anchor_positive_control.py`). Two things I could not test here, both fail-closed: the sign
   convention of the frequency word and whether a kernel slew left over from the resync is still running at R0.
   Either would show as a refusal at `a1`, before any launch.
3. **Energy, power or per-member duration in a public output?** No energy or power. Per-member timing: M1.
4. **Can a producer fault abort a window or change a verdict?** It cannot abort the chain or change its exit
   code; every producer call is wrapped and the supervisor runs the driver without a timeout. Verdict coupling: M2.
5. **Refuse a good window after the launch is consumed?** Yes, always: B1 and B2.

## Required before `s1` arms

1. Cure B1 and B2, with a ruling addendum for B2.
2. Add one composed desk test with no mock at the seams: real journal -> `assemble` -> `evaluate_qualification`,
   and real `closeout` output -> G9, on a two-root fixture. Given that two of eight gates failed this way, treat
   G3, G5 and G8 as unproven on native producer output until that test exists; I did not trace them end to end.
3. Move or trim the public locators (M1).

## What I did not verify

- Nothing live: no clock, sudo, launchctl, sampler or model was run. All physical claims above are from code.
- The focused suite (`test_kernel_clock`, `test_v5_block4_clock`, `test_t0_anchor_positive_control`,
  `test_v5_s1_desk_closeout`, `test_v5_s1_qualification`, `test_harvest_v5_qualification`) passes: 78 passed,
  38 subtests passed, 261 s. It is green while B1 and B2 hold, which is the point of "Required" item 2. The
  whole suite was not run. The two scratch tests above ran and fail as shown.
- `scripts/assemble_v5_battery_boundaries.py`, the installer change in `joulewise/night_agent_install.py` and the
  window-sizing arithmetic were read once, not attacked.
