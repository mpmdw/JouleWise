# Registration fan-out handoff — 2026-11-08

Branch: `align/2026-11-08-v4-registration`, based on W1 R10
`d600baba029f70592bb8e792098338e4cd6811d3`. Local implementation only; no
push, network, weights, measurement launch, sealed outcomes or external study
path access. R1's lane/pin is untouched. Coordination-state files are untouched.

Installed chair 4/5/6/9/11/15/17/18/20 and WP19 prospectively in protocol v4,
with native/registration evidence explicitly pending. Added:

- A pending `registration_receipt.json` template and W1 readiness enforcement.
  A usable lead receipt binds the current and committed protocol, kit, desk,
  estimands, deviations, U3/WP19, R1 soak, slots/plan and relevant runtime code;
  both Stage A/B reports must be admitted, digest-bound and committed.
- Relative U3, k=3, floor 8.91 J; sample SD of signed relative replay
  differences, one-sided 90% chi-square upper SD limit for n<6, source digests,
  pairs, normal-theory false-fail rate and empirical exceedances. The v4 desk
  uses it; v3 retains its old defaults.
- Tokenizer-only all-turn X/Y history rendering from WP18 recorded outputs,
  live X-G ID/seed comparisons, source/config/tokenizer hashes and static
  warmup/reseed proof. WP19 failure predeclares the contrast INCONCLUSIVE.
  No tokenizer or model was opened here. Native tokenizer parity remains unproven.
- Completed-top-up battery predicate/OBC operator attestation and raw arm
  evidence; daytime offload verification with a <=24 h config-bound receipt,
  current disk check without SSD remount/rehash, explicit empty-offload waiver.
- V4-only delivery/stage/positive-direction contrast, U4 anchor demotion,
  per-position trajectory-count eligibility, sentinel/cohort/rebuild/warm-reference
  diagnostics and B-count bar. The session desk applies relative U3 and the
  frozen D cohort assertion. Missing observations remain unavailable.
- E_ref 5/17 correction; seed tag remains unchanged, with quantization label
  only; authenticated unobserved capture refuses consumers before runtime
  preparation; observer faults re-raise KeyboardInterrupt only (Ruling 76).

`D-C1` contrast-cap and U5-consequence proposals remain **PENDING LEAD RULING**
in protocol and deviations. Existing R10 contrast refusal/cap policy and U5
verdict handling remain unchanged. No new U5 waiver is granted.

Assumed authority: Ed's brief selects k=3 and the synthesis's narrowed chair
17, ordinal correction, label-only seed deviation, capture-loss refusal,
D8-1 scope correction, operator OBC attestation and daytime-offload approach.
Standing m>=39/max-threshold/test-cohort, KM003C and sealed full-reasoning
transcript rules are stated without introducing a v5 adversary/monitor or
changing v4 model/settings/thermal policy. Meter/transcript capture wiring is
the separate fan-out's responsibility.

Sources used from existing local refs (no fetch): registration synthesis
`eea648b09933bce93d49cef3a8e7da11ab88e18b`, squeeze design
`a832f4993c4f35f333634884b5905768078b8085`, reviewer2
`f01e47f295f36b5f77c06dd2d788bcaf88ff7f21`, tripwire directions
`028a705292461646c2cfcbe18b74f4c4a9b0a3ed`, prereg draft
`688d14b6eba63544fee5c60dcb850cdb7caf3813`, main items 202–210 at
`32ba4928573ce1981f8a953ab700f00dda9e94d1`; local protocol/residual,
chair/lead rulings, playbook, decision log and orchestration instructions.
External paths quoted by those documents were text only.

Changed files:

- `docs/align/pilot_protocol_v4.md`, `docs/align/v4/DEVIATIONS.md`, this report.
- `joulewise/align/apple/{v4_registration,v4_estimands,thermal_desk,thermal_gates}.py`.
- `scripts/{align_v4_kit,align_v4_session,align_v4_thermal_desk,align_v4_u3_bar,align_v4_wp19,align_v4_offloads,run_night}.py`.
- `configs/campaigns/align_v4/{README.md,plan_tree.json,registration/identity_pins.json,registration/registration_receipt.json}`.
  Generated changes are the kit generator digest/derived identity digest and
  README; anchors/member configs/seeds did not change. Regenerating the night
  template produced no diff.
- `tests/align/{test_v4_registration,test_v4_kit,test_protocol_v4_doc,test_thermal_desk,test_window_reference_custody,test_pilot3_cache,test_r1_round8_exec_review,test_w1_kit_r10}.py`.
  `test_v4_estimands.py` itself is unchanged; its existing tests were run.

Verification (Python 3.13; synthetic only): every behavior change had a
failing-first check before implementation. Initial registration checks failed
on absent APIs/receipt enforcement/ordinal rejection; additional red tests
covered battery/empty offloads, scripts, U4, marker retention, R1 soak and
session cohort enforcement. Capture fixture setup needed correction before
the meaningful pre-prepare refusal regression was exercised. SystemExit's
old escape was reproduced before correction. Existing tests were updated for
the new explicit arm attestation and registration evidence requirement.

Final commands, each selection in its own process:

| `python3.13 -B -m unittest ...` selection | Result |
|---|---|
| `tests.align.test_v4_registration` | 19 pass |
| `tests.align.test_v4_kit` | 116 pass |
| `tests.align.test_protocol_v4_doc` | 6 pass |
| `tests.align.test_v4_estimands` | 14 pass |
| `tests.align.test_thermal_desk` | 24 pass |
| `tests.align.test_window_reference_custody` | 5 pass |
| `tests.align.test_pilot3_cache` | 13 pass |
| `tests.align.test_thermal_gate` | 44 pass |
| `tests.align.test_w1_kit_r10` | 30 pass |
| `tests.align.test_v4_w1_synthetic` | 4 pass, 14 skipped (full WP22 opt-in not set) |
| `tests.align.test_r1_round8_exec_review.SwallowedSignalLatchTests` | 2 pass |
| `tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` | pass (success/failure x RuntimeError/SystemExit) |

Compileall over `joulewise`, `tests` and touched scripts passed. `git diff
--check` passed. Kit generation and template regeneration passed; kit `--check`
correctly refuses the pending R0/R1 leaves. `require_registration(Path.cwd())`
independently refuses the pending unsigned receipt. No full suite was run;
targeted test time was far below 20 minutes. Two early diagnostic modules
briefly overlapped; subsequent runs were strictly sequential.

Lead next steps / uncertainty:

1. Review this local commit and rule D-C1/U5 separately. Keep W1 blocked until
   real registration evidence exists. This lane does not sign either gate.
2. Export eligible pilot-4–10 pairs to the documented U3 input schema; run
   `align_v4_u3_bar.py --input <export> --output <new-file>`, audit eligibility
   and source custody, then commit it as `registration/u3_bar.json`. Shared
   pilot trajectories/windows limit the normal-theory SD calculation; publish
   the updated OC/series false-fail analysis. No pilot numeric bar was invented.
3. With authorized R1 evidence, run `align_v4_wp19.py --tokenizer <local-dir>
   --x-g-turns <explicit-X-G-jsonl> --output <new-file>`; commit the receipt.
   Native tokenizer/history/tool parity, and the interpretation of partial X-G
   identity, must be checked by the lead. Copy authenticated R1
   `soak_reference.json` to `registration/r1_soak_reference.json`; the receipt
   binds its bytes. Do not follow source_output paths in that JSON here.
4. Native battery/OBC, by-day offload, mount/unmount unified-log qualification
   and complete in-window mount audit remain required. This lane adds the
   arm/offload machinery and normative audit requirement, **not a qualified
   automatic in-window mount-log collector**. SoC/charger diagnostics stay
   unavailable where the existing bundle lacks those observations. Resolve
   that capture evidence at integration before calling these native gates met.
5. Verify the KM003C/full-transcript fan-out, fill R0/R1 and final W1 plan,
   regenerate/check kit, run full WP22 with `JW_WP22_FULL=1` on the integrated
   head, obtain Stage A/B review, and fill/sign the receipt. The header remains
   DRAFT because no registration gate has passed.
6. Outside this sandbox, run native `tests.align.test_cache_checkpoint_native`
   and `tests.align.test_thermal_mlx` with the authorized local artifacts, one
   module per process, plus WP19 and arm/mount qualification. MLX/Metal was
   not exercised here. D-series fit/threshold wiring, R1-vs-W1 token comparison
   and OC closure remain the lead's existing pre-D1 obligations; this is not
   a claim that all synthesis action-list items or v5 are implemented.

Local commit: the commit containing this report (`git log -1` on the branch).
