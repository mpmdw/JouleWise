# Final-head fresh-eyes review — D-176 (gate ledger row 10, Opus)

Read-only in `/Users/edr/code/JouleWise-wt-int-d176`, head `7d1cffb0`, scope
`git diff origin/main...HEAD`. No suite run; static reads plus `git`, `ast.parse`,
and a mechanical pin checker. Skimmed 99gg and the 99ey ruling first; nothing below
re-litigates them.

## Verdict

**No BLOCKER.** Two SHOULD-FIX (both documentation integrity, not launch safety),
two NITs.

## What I checked and found clean

**(a) The merge `7d1cffb0`.** `tests/test_run_campaign.py` is the only file both
parents touched (`comm` over each parent's delta from the merge base). The merged
file carries *both* sides intact: main's locator-lane additions (`ast`/`inspect`/
`SimpleNamespace` imports, `mode="issuing"` assertions, the new
`test_campaign_core_callers_keep_replacement_custody_replay_only`) appear in
`diff 7d1cffb0^1..7d1cffb0`, and D-176's narrowed mock — `real_run = subprocess.run`
at `:332` with the `command != ["child"]` passthrough — is the sole hunk in
`diff 7d1cffb0^2..7d1cffb0`. The two changes are in different test classes and do
not interact. `ast.parse` succeeds on the merged file and on all eight changed
production modules.

**(c) Cross-unit coherence.**
- Argv/argparse: `scripts/run_night.py:1255-1262` emits exactly
  `--pack-root --arm-receipt --arm-readiness-custody-root --launch-manifest
  --night-plan --go-receipt --step6-confirmation-table --expected-confirmation-digest`;
  `scripts/launch_window.py:42-59` declares that set and nothing else on the launch
  path (`--lifecycle-event` omitted → `launch()`). Exact match, eight flags.
- Six keys: producer `joulewise/night_gate.py:128-131` (`_PACK_NIGHT_KEYS`, enforced
  exact at `:296-297`) == consumer `joulewise/arm_readiness.py:9992-9994`
  (`_require_exact_keys(plan["pack_night"], {...})`). Same six, both exact-set.
- G7 control uses the *production* launcher: `scripts/run_night.py:1372` calls the
  same `_pack_launcher_argv` builder as GO and `subprocess.run`s it
  (`:1375`) — no test double, no alternate entry.

**(d) Fail-open scan.** Every path I traced refuses rather than launches.
`launch_window.py:110-111` refuses `readiness_usage_invalid` when either
`--night-plan` or `--go-receipt` is absent (argparse leaves them optional, so this
is the real gate — it is present and precedes all IO). `_admit_pack_launch_go` runs
*before* pack-root/ARM/manifest IO in both `_assemble_launch_inputs`
(`launch_window.py:118`) and `_consume_launch_capability`
(`arm_readiness.py:10357`). `scripts/run_night.py:1179-1180` refuses GO unless the
receipt verdict is GO *and* every condition row is PASS. A G7 presentation that does
not yield exit 2 with exactly one reason code becomes `unexpected_launch_result`
(`run_night.py:1385`), which `validate_g7_control` rejects → verdict FAIL. An absent
`g7_control` record yields `evaluate_g7` FAIL `g7_control_pending`
(`t0_rehearsal.py:880`), never a skip, and `compose_overall_verdict`
(`t0_rehearsal.py:247-257`) is FAIL-dominant over all ten evaluators. The writer's
`del fields["pack_night"]` (`night_plan_writer.py`) only fires for a packless plan
whose `pack_night` is already `None`; a non-pack plan carrying a binding still fails
`NightPlan.from_mapping`.

**(e) Leakage.** Only `configs/production_custody_inventory.json` and operator docs
carry `/Users/edr` paths — deliberate, plan-pinned census content, no secrets.

**§10.3 addendum pins** (`arm_readiness.py:3064`, `:3156`, `:9990`;
`t0_rehearsal.py:703`; `tests/test_t0_rehearsal.py:787`, `:980`) all land exactly on
the final head.

## SHOULD-FIX

**S1 — §9 traceability pins drifted on the final head.** A mechanical check of all
186 `path:line` (`symbol`) pins in `docs/contracts/pack_night_go_receipt.md` finds
**55 stale (43 unique targets), drift up to 139 lines**. Two land inside the *wrong
function*: `:782` pins `joulewise/arm_readiness.py:9891` as
`_authenticate_pack_launch_go` (actual `:9966`; `:9891` is inside
`_authenticate_go_purpose`, which also raises `_go_invalid` — a reader would verify
the wrong code), and `:766` pins `scripts/run_night.py:1272` as `run_night` (actual
`:1411`). Others: `arm_readiness.py:10231`→`10306` (`_consume_launch_capability`),
`:2742`→`2757` (`validate_pack_night_go_receipt`), `night_gate.py:918`→`945`
(`evaluate_night`), `tests/test_arm_readiness.py:2268`→`2348`. The drift was
introduced by D-176's own later commits (seat 4 g7-control, the fix rounds) inserting
lines above pinned symbols without repinning §9. §9 is the replication surface the
contract itself points reviewers to ("contract §9 final pins"); under PD-1 these
should be recomputed once at the final head.

**S2 — one §9 pin names a test that does not exist.** `:885` cites
`tests/test_rehearse_t0_unattended.py:34` (`test_inventory_must_equal_head_bytes`).
No such name exists in `tests/`; the real test is
`test_inventory_must_equal_plan_repo_head_bytes` at `:61`. Name *and* line are wrong,
so the §10.3-item-4 row currently has no verifiable test evidence.

## NIT

**N1 — installer asymmetry.** `scripts/install_night_agent.sh` now derives
`custody_root` from the `NightPlan`-validated parse on the install path (a
tightening), but the new `else` branch keeps the raw
`json.load(...)["custody_root"]` read for uninstall. Harmless for a removal, but the
two paths now trust the plan differently; worth a one-line comment saying why.

**N2 — new tracked absolute-path inventory.** `configs/production_custody_inventory.json`
is added with four `/Users/edr/...` deployment roots. This is by design (the census
must be frozen, byte-pinned to `repo_head`, and not derived from the running clone —
`arm_readiness.py:253-275`), so it is an accepted disclosure rather than a defect;
recording it so the next reviewer does not re-flag it.
