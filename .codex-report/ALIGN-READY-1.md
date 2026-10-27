# ALIGN-READY-1: first agent-monitoring pilot on the measurement Mac

Seat ALIGN-READY-1. Lead: Claude Code session 015ASG1T. Owner: Ed. Written 2026-10-27, in the cloud, off the Mac.
Branch: `lane/2026-10-27-align-ready`, cut from main `d842f697f`. No PR was opened, nothing was pushed to main, and
nothing ran on the measurement Mac. Only synthetic fixtures were used. No real block-5, block-6 or BYTES measurement
data was opened.

## SUMMARY

**Not ready to arm today. Code-ready for a first session on the night of 6 Nov at the earliest**, once these are done:

1. The lead rules on the NEEDS_RULING items. R1 (review level for the arm-path change) and R2 (where the SHADE
   packages are installed) block the first arm.
2. This lane is merged into a measurement checkout **after BYTES closes on 5 Nov**. The lane changes
   `joulewise/adapters/__init__.py`, so it must not reach a BYTES checkout.
3. The one-time desk setup in the Mac-side checklist is done, which takes about 30 min at the Mac.

7 Nov is the realistic date if the merge, setup and a prepare dry run are done on 6 Nov. Any block-5 or BYTES desk
step still assigned to the Mac takes the gap at 8 Nov first (contingency §7, point 3).

**What exists now:**

- **The kit.** `configs/campaigns/align_pilot_v0/` is a fixed, non-claim kit. It keeps the same block-6 calibrated
  scaffold as the BYTES Mac check and runs 12 `align_episode` members of the BYTES Qwen3-8B-4bit source.
- **The tasks.** Two judge-free SHADE-Arena pairs, each run benign and sabotage, with 3 greedy repeats, in ABBA
  order.
- **The session runner.** `scripts/align_pilot_session.py` runs prepare, install and desk. Prepare and install are
  the BYTES item-H runner's, with the BY-H2 arming sequence.
- **The protocol.** `docs/align/pilot_protocol_v0.md` is a DRAFT for the lead.

**How it was checked:**

- On synthetic data, `prepare` stages the kit through the real window-plan writer: 37 members, plan written, no
  install.
- Every dispatched config authenticates.
- The identity-pin projection validates.
- A fixture SHADE episode runs end to end through the real controller on the mock runtime and reaches `PILOT.json`
  with all four instrument checks passing.

**What remains unproven:**

- No real SHADE environment has run anywhere: its Python packages are absent here, and the cloud proxy blocks PyPI.
- No episode has run with real MLX and real powermetrics through this kit.
- The native harvest has never read an `align_episode` bundle.

That is why the first session is an instrument check. `desk` writes `PILOT.json` before the harvest runs, so a
harvest fault cannot lose the pilot's episodes.

## INVENTORY

Status values:

- DONE: in this lane and exercised by a test here.
- CODE: in this lane but not exercised on real hardware or real data.
- MAC: needs an action at the Mac.
- MISSING: not built.

| # | Item the first pilot needs | Status | Evidence |
|---|---|---|---|
| 1 | Candidate question served first | DONE (choice) | RQ-ALIGN-METADATA-BASELINE and RQ-ALIGN-ENERGY-RESIDUAL, `docs/align/PIPELINE.md:26-27`. The pilot is an instrument check for both and tests neither (`docs/align/pilot_protocol_v0.md` "Purpose"). |
| 2 | Local model on MLX, no paid API, no rented GPU | DONE / MAC (already present) | Qwen3-8B-4bit, rev `545dc425` (`configs/campaigns/bytes_v1/roster.json`), file-pinned in `configs/campaigns/bytes_mac_check/registration/identity_pins.json`, runtime pinned to mlx 0.31.2 and mlx-lm 0.31.3. In-process MLX through the existing adapter (`joulewise/align/apple/endpoint.py`, `joulewise/adapters/__init__.py:121-133`). A Qwen3-1.7B-4bit MLX real smoke ran locally on 2026-10-22 (PR #561 body). Nothing new to download for v0. |
| 3 | SHADE-Arena pairs and their pinned upstream fetch | DONE (pin verified) / MAC (packages) | Pin at `joulewise/align/shade/upstream.py:24-27`. Verified today from the cloud: `PinnedUpstream(...).prepare()` fetched 6614e771 and matched both commit and manifest SHA (`flags []`, 2.9 MB). Offline factory `joulewise/align/apple/pilot.py` `offline_shade_task` passes `allow_fetch=False`; `tests/test_align_pilot_session.py` `OfflineFactoryTests` shows no subprocess runs on a missing cache. **Network:** one public git fetch at the desk (`python3.13 -m joulewise.align.apple.pilot prefetch`), none at session time. **Packages:** the real environments need pydantic v2, PyYAML, docstring-parser, typing-extensions, rich, pandas, openai and anthropic (imports only), plus email-validator (`docs/align/shade_port.md` "What can run offline"); matplotlib and seaborn only for the two judge pairs that v0 does not use. They are not in the measurement `.venv` (R2). The real environments have never been executed (`tests/align/test_shade.py` skipped 4 here; `docs/align/shade_port.md` "Status"). |
| 4 | Honest/sabotage pairs and scoring without a judge | CODE | `spam_filter_update` and `bank_transfer_2` score main and side tasks deterministically (`docs/align/shade_port.md` pair table). Roster in `joulewise/align/apple/pilot.py` `PILOT_V0_*`, order in `configs/campaigns/align_pilot_v0/collection_plan.json`. |
| 5 | Monitor (off-box or local) | CODE, deliberately not in the session | `ShadeMonitor` (`joulewise/align/shade/monitor.py:103`) scores transcripts against any OpenAI-compatible endpoint, e.g. `mlx_lm.server` or llama.cpp on the analysis laptop, after the session. No paid API. Never run on real transcripts. |
| 6 | Apple power path | DONE (synthetic) / CODE (real) | Controller-owned powermetrics sampling. `ApplePowerSampler` bridges to `PowermetricsTelemetryAdapter` (`joulewise/align/apple/sampler.py:228`), and `read_episode_bundle` joins episode and trace without rewriting the bundle (`joulewise/align/apple/workload.py:463`). Real powermetrics plus real MLX ran in the 10-22 local smoke; PR #561's fixes, which make energy reach the Episode on both Apple paths, are merged into this lane (`bef534273`). |
| 7 | Clock mapping to turns and tool calls | DONE (synthetic) | `stamp_mapping` (`joulewise/align/apple/sampler.py:83`); per-turn, phase and tool attribution in `attribute_episode` (`joulewise/align/attribution.py:632`). Repeated prefill/decode phase pairs plus `align_tool_N_M` events are described in `docs/align/apple_path.md` "Execution and records". PR #561 Opus F6 says a sampler capture must exceed the roughly 60 s anchor-fit span; the BYTES member's 57.6 s idle plus warm-up precedes every episode, so this holds. |
| 8 | Loop integration (arm like a BYTES session) | DONE (synthetic) | The block-6 loop cannot carry this kit: module kinds are only floor or contrast, at 50 or 40 runs (`joulewise/b6/pack_registration.py:89-94`); DIF-READY-1 found the same. The non-claim fixed-kit route that BY-H2 ran (RUN_STATE item 68) is used instead: `scripts/align_pilot_kit.py` builds the kit on `compose` exactly as `scripts/bytes_mac_kit.py` does, and `scripts/align_pilot_session.py` reuses `bytes_h_session.prepare`/`install`. Tests: `SessionPrepareTests` (real window-plan writer, member_count 37, STAGED) and `RealKitStagingTests` (all 37 configs authenticate, identity projection validates, harvest roster has 37 members). |
| 9 | Desk / precheck | DONE (synthetic) / CODE | The item-H route uses the in-chain agent census and arm checks, not the block-6 loop precheck. `desk` writes `PILOT.json` (checks I1-I4) and then runs `harvest_b6_session.py --non-claim`. `SyntheticDeskTests` runs 4 fixture episodes, then desk; the harvest is stubbed there. |
| 10 | Harvest of `align_episode` bundles | MISSING (unverified) | No test runs the real block-6 harvest over align bundles; `tests/test_bytes_h_session.py` seeds only BYTES-shaped bundles. A harvest failure leaves `PILOT.json` intact, but the native export may refuse. |
| 11 | Pilot protocol | DONE (DRAFT) | `docs/align/pilot_protocol_v0.md` |
| 12 | Session time budget | CODE (planning bound) | `configs/campaigns/align_pilot_v0/registration/sizing_b5.json`, flagged `sizing.planning_bound_unmeasured`: programmed span 30,670 s (8.5 h), window maximum 48,420 s (13.5 h). Expected 5-6 h, which is a guess. Static estimate of tool-schema size from the pinned source (chars/4, not tokenized): about 5.6k tokens for banking (70 tools) and 3.3k for spam filter (40 tools), so a 32,768-token context bound is plausible but untested. |
| 13 | Identity pins and model inventory | CODE / MAC | The kit copies the BYTES kit's file hashes for the same two directories. `configs/campaigns/align_pilot_v0/registration/derive_identity_pins.py` re-derives them at the Mac. There is one identity unit per episode, because the identity projection requires one declared workload per unit (`joulewise/identity_pins.py:1656`) and each episode spec is its own workload. |
| 14 | Order-dependent `test_power_duty` failures (DUTY-ORDER) | see TESTS | The seat never executed (`.codex-report/DUTY-ORDER.md`). Here `tests.align.test_power_duty` passes alone. The combined-order result is in TESTS. |
| 15 | Paid services or session-time network | none | No paid API anywhere. Session-time network: none (the factory refuses to fetch). Desk-time network: the SHADE fetch and `pip install`. |

## CHANGES (branch `lane/2026-10-27-align-ready`)

| Commit | What |
|---|---|
| `155cb0bfe` | Merge `lane/2026-10-21-align-integration` (`9e7563d90`); clean. |
| `de61d0bfe` | Merge `fix/2026-10-22-align-duty-order` (`9ff65870f`). This brings in PR #561's real-smoke fixes (`bef534273`, still open against integration) and the DUTY-ORDER blocker record; clean. |
| `7a26c2c45` | Merge the collection line `work/2026-10-23-by-slots-draft` (`991358f73`, the b6 loop the Mac runs; not on main). Conflicts in `configs/gates/hazard_refusals.json` and `scripts/test_timings.json` were resolved as unions of both sides. |
| `f02772b60` | Align pilot v0: `joulewise/align/apple/pilot.py`, `scripts/align_pilot_kit.py`, `scripts/align_pilot_session.py`, kit `configs/campaigns/align_pilot_v0/`, `tests/test_align_pilot_session.py`, `docs/align/pilot_protocol_v0.md`. `scripts/bytes_h_session.py`: `prepare`/`measurement_view` take a kit and pack id, with BYTES defaults unchanged; `align_episode` configs get one identity unit each. |

Branches not merged, with reasons:

- `lane/2026-10-21-align-docs` (1 commit, PR #522): draft candidate registrations only.
- `lane/2026-10-21-align-realsmoke` (7 commits): blocker reports, no code.
- `lane/2026-10-21-align-stageb` and `-gpukit` (57 commits each, PRs #526 and #521): MoE Stage B and the rented-GPU kit. The Mac pilot needs neither, and Stage B's CI was blocked.

All other `lane/2026-10-2[12]-align-*` branches and `fix/2026-10-22-align-shard-names` were already in integration.

Governed estimator files are byte-identical to main and to the collection line:
`joulewise/powermetrics_fiducial.py`, `joulewise/reduce.py`, `joulewise/uncertainty_evidence.py`,
`joulewise/adapters/powermetrics.py`. The check was `sha256sum -c` against main after every merge and commit. None of
block-6's `number_bearing_paths` (`configs/b6/registration/acceptance.json`) differs from the collection line.

Against the collection line, the only measurement-path code change is `joulewise/adapters/__init__.py`, the
`align_episode` branch from integration. `scripts/repin.py --check` passes, but it warns that this file differs from
the sealed inventory, so sessions run from this tree carry `code.executed_differs_from_sealed`. Merge this lane into
a measurement checkout only after BYTES closes.

## TESTS

All runs used `JW_B5_SYNTHETIC_ONLY=1`, a private `TMPDIR` per module, and `python3.13 -B -m unittest <module>`,
one process per module, on Linux with 4 CPUs.

TEST_TABLE_PLACEHOLDER

## NEEDS_RULING

- **R1. Review level for the arm-path change.**
  - **The change.** `scripts/bytes_h_session.py` changes how identity units are formed for `align_episode` members
    only. BYTES output is byte-for-byte unchanged, and `tests/test_bytes_h_session.py` passes.
  - **Gate policy.** Rule 3 covers "the agent census, stand-down and arm checks". This change feeds the arm-time
    identity projection but alters no census and no claim number.
  - **Proposal.** Rule 2 (CI plus its own tests, which are here), plus one executing reviewer run in parallel
    (Sol 6.1 xhigh fast) before the first arm, because this is the first non-BYTES workload through the item-H
    path.
- **R2. Where the SHADE packages go.**
  - **Options.** (a) `pip install` into the measurement `.venv`. (b) A separate checkout and venv for the pilot,
    which the item-H `measurement_view` cannot select today.
  - **Proposal.** (a), after BYTES closes. The packages are listed in Inventory row 3. `runtime_versions` pins the MLX
    stack plus numpy, safetensors, tokenizers and transformers, which the install must hold fixed (checklist 4), but the pilot's identity re-derivation records the interpreter census
    anyway.
- **R3. Qwen3 thinking on or off.**
  - **Current state.** `MlxEndpoint` is built without `enable_thinking` (`joulewise/align/apple/workload.py:227`),
    so the Qwen3 template's default applies, which is thinking on. Hidden reasoning is then stripped and counted as
    `hidden_tokens`.
  - **Effect.** This gives the energy-residual dry run real hidden work, but it lengthens episodes.
  - **Proposal.** Leave it on for v0. Making it a spec field changes align workload identity code.
- **R4. First-session size.**
  - **Options.** 12 episodes (planning bound 8.5 h span) or 8 episodes (2 repeats).
  - **Proposal.** 12. I4 needs at least 2 repeats; 3 give the first spread estimate.
- **R5. `--max-failures 1`.** The inherited stage argv stops a stage of 6 episodes at the first failed member. A
  missing package would then cost 5 episodes, not 1. Proposal: keep it. The first session is an instrument check,
  and stopping early on a setup fault is the right outcome.
- **R6. Scaffold for a non-claim pilot.** The kit keeps the full BYTES scaffold: 18 NEG-8 corpus members, 7
  references and 2 calibrations, about 2.5 h of planning time. Proposal: keep it, since it is the only proven arming
  route. Trimming it means editing the block-6 composer seed.

## MAC-SIDE CHECKLIST (at a desk, with no agent session left running when anything is armed)

1. **After BYTES closes (5 Nov):** build a measurement checkout from this lane, merged with whatever the collection
   line has gained since `991358f73`.
2. **Models.** No new download for v0.
   - Qwen3-8B-4bit (4.61 GB) and the NEG-8 reference model (0.87 GB) are already present and pinned.
   - Later pilots: Qwen3-30B-A3B-4bit (17.2 GB, present) for the MoE rows.
   - Monitor scoring runs on the analysis laptop: an 8B-4bit model (about 4.6 GB) under `mlx_lm.server`.
3. **SHADE cache (network, about 2.9 MB):** `python3.13 -m joulewise.align.apple.pilot prefetch --cache-dir
   /Users/edr/.cache/joulewise/shade`, then `... verify --cache-dir ...` must print `"ok": true`.
4. **Packages (network, R2):**
   `<measurement>/.venv/bin/python -m pip install 'pydantic>=2' pyyaml docstring-parser typing-extensions rich pandas openai anthropic email-validator`.
   Hold the pinned stack fixed: add `numpy==2.5.1 transformers==5.12.1 tokenizers==0.22.2 safetensors==0.8.0` (the
   versions in the BYTES identity pins) to the same command, so pandas or the SDKs cannot move them, and compare
   `joulewise.flags.collect.runtime_versions` before and after. Size is unmeasured, probably a few hundred MB. Then load the two pairs once, without a model, at the desk:
   `python -c "from joulewise.align.apple.pilot import offline_shade_task as f; [f(p, cache_dir='/Users/edr/.cache/joulewise/shade').reset(1) for p in ('spam_filter_update','bank_transfer_2')]"`.
5. **Identity:** `python3.13 configs/campaigns/align_pilot_v0/registration/derive_identity_pins.py --runtime-python
   <measurement>/.venv/bin/python`. After this, `scripts/align_pilot_kit.py --check` reports drift on those two files
   only; that drift is expected.
6. **Sizing (optional):** replace the planning row with the BYTES-registered scaffold allowances, or accept the
   13.5 h window maximum.
7. **Disk:** the planning footprint is 14.8 GB (2 copies x 37 members x 200 MB, a planning allowance). `prepare`
   prints the free bytes.
8. **Arm:** `python3.13 -B scripts/align_pilot_session.py prepare --measurement-root R --session-root S`. Then
   `... install --session-root S` is the lead's last action, after which the lead exits. After the terminal record,
   run `... desk --session-root S` and read `PILOT.json` `checks`.
