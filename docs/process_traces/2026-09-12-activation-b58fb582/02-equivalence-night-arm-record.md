# 02 — Arm record: `d079-epoch-25g83-derivation-n1-20260913` (DIAGNOSTIC_NO_PACK, equivalence night), t0 2026-09-13 02:56:00 PDT

Activation `b58fb582`, headless. Runbook followed:
`docs/phase_2/derivation_night_runbook.md` **revision 7** at H (last
runbook commit `53310262`, merged `18ab2cc4`, PR #322), §0–§1.5, plus
NIGHT_HANDBACK. Scripts executed are in [`02-arm-evidence/`](02-arm-evidence/)
(`exports.zsh`, `20-clone.zsh`, `21-clone-finish.zsh`, `30-desk.zsh`,
`40-arm.zsh`, `41-recover.zsh`) with their outputs; `SHA256SUMS` covers
the directory. STATUS: see §Executed at the end — this file is written
before the arm block and completed after it.

## Frozen checkout triple (runbook §1.5, contract fields exactly)

| Field | Value |
|---|---|
| `plan_id` | `d079-epoch-25g83-derivation-n1-20260913` |
| `root` | `/Users/edr/JouleWise-measurement-20260913-derivation` |
| `head` | `f90cb8c016662f8af6faa73d905fc472443432ab` |

## §0 preconditions, executed

| Step | Evidence | Result |
|---|---|---|
| 0.1 H | `f90cb8c0` on origin/main (pushed 01:00:48 PDT; direct bookkeeping commit per file 11 §Exact activation Git sequence). Carries: handback rewrite, inventory row, pre-registration fills, inventory pin test → 5. Focused suites OK (record 00); Opus verification record 01. CI at H: see §Executed. | H fixed |
| 0.2 clone | `git clone --no-hardlinks` + `checkout --detach H`; remote main == H asserted; venv `python3.13` 3.13.1, `pip install -c env/mac-measurement-lock.txt -e ".[mac]"` + `charset-normalizer requests urllib3`; lock diff EMPTY (run without `PYTHONPATH` — with `PYTHONPATH=<clone>` set, `pip freeze --exclude-editable` lists the editable project from its `joulewise.egg-info`, a freeze artefact, not a package drift; recorded in `20-clone-output.txt` / `21-clone-finish-output.txt`); `joulewise` imports from the clone; mlx 0.31.2 / mlx_lm 0.31.3; ledger restored byte-exact from the canonical FILE (sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`, 76 records) and authenticated with `verify_custody=True` at sequence 76 digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`; `git status --porcelain=v1 --untracked-files=all` EMPTY | PASS 01:03:07 |
| 0.3 check | rc 3; `os_build 25F84 → 25G83 MISMATCH`, `hardware_model Mac15,9 match`, `powermetrics_sha256 d1dccad0… → b762e5bf… MISMATCH`, `mlx_version 0.31.2 match`; `mismatched fields: os_build, powermetrics_sha256`. `check --preregistration`: same table + `pre-registered powermetrics sha256 b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5: match`, rc 3 | expected shape |
| 0.4 ledger | no `ledger:` refusal line; head pin 76 / `08456d50…94d7` (the `[SEQ]`/`[DIGEST]` fill) | PASS |
| 0.5 pre-registration | committed inside H with the five fields filled; tracked chain sha256 `b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf` (= the `[CHAIN_SHA256]` fill); **pre-registration sha256 at H `84b820b9069c5b7b34b35e1b8fcd1c436c54ded04cbb24c6c985bbc867ce0b5c`**, blob `87d4fb716b4b72ea3253261a2565726a0042ca5c` | pinned |
| 0.6 census | no own seats/background jobs at the arm (CI watcher and clone tasks finished); classification by ancestry in the arm block step 4 | see §Executed |
| 0.7 discoverable | `print -rl -- /Users/edr/night-custody/*/night_plan.json(N)` → empty; no stand-down, no STOP, directives `[]`, thread: no NO | PASS |
| 0.8 desk inputs | `write_derivation_night_inputs.py --out-dir <night root>` with `$PY`, rc 0: `stale identity fields vs …calibration_acceptance_d079_v2_n17_r6.json: os_build`; `IDENTITY_EPOCH_JSON=…/identity-epoch.json sha256=b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607`; `T1_BINDINGS_JSON=…/t1-bindings.json sha256=8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98` | PASS |

## §1.1b arm order, executed at the desk (01:03 PDT)

1. Clone, clean tree, desk inputs — above.
2. Staged plan authored with `joulewise.night_plan_writer.write_night_plan`
   at `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-n1-20260913/night_plan.json`
   (`authored_epoch_s` 1789200196.934819 = 01:03:16.9 PDT; copy in
   `02-arm-evidence/staged-night_plan.json`): v2, `DIAGNOSTIC_NO_PACK`,
   `t0_epoch_s` 1789293360, `window_max_s` 9000, both heads H,
   `chain_path` `<night root>/chain.zsh`, `registration_path` =
   `night_gate.D166_REGISTRATION_PATH`.
3. Wrapper emitted from the clone: `emitted <night root>/chain.zsh sha256=569daedae03126d9eb819abd3b132baf860597dbe926a0db87311643a854df45`.
   Frozen calibration plan literal: `PLAN_ID='plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3'`,
   `PLAN_SHA256='9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072'`;
   `WINDOW_END_EPOCH_S='1789302360'`; `SLOT_COUNT 12 / SETTLE_S 600 / SLOT_CADENCE_S 600 / SLOT_CAPTURE_BUDGET_S 480`.
   `EVIDENCE_ROOT_ID='evidence-d079-epoch-25g83-derivation-n1-20260913'` —
   **registered here** (record 00 decision 2). `SESSION_ID` = plan id.
4. `--verify`: `VERIFIED … sha256=569daeda…df45` rc 0.
5. `/bin/zsh -n` rc 0. Driver preflight from the clone:
   `{"preflight": "ok", "python": "<clone>/.venv/bin/python", "version": "3.13.1", "modules": [scripts.run_night, joulewise.arm_readiness, joulewise.arm_readiness_evidence_t0, joulewise.t0_rehearsal, joulewise.night_gate, joulewise.measurement_liveness]}`.

## §1.2 arithmetic (verified with zoneinfo at this activation)

t0 1789293360 (02:56:00 PDT 09-13); t0+9000 = 1789302360 (05:26:00);
courier deadline 1789302660 (05:31:00); next 07:00 = 1789308000;
slack 5340 s = 89 min; strict maximum window 14339 s ≥ 9000. Δ budget 1320 s.

## §1.4 email, then arm

Notice `1a094a59a84b53be` on thread `1a0800cdb282c3f1`, accepted ~01:04:40
PDT, read back with label SENT (this is also NIGHT-REHEARSAL-01 acceptance
item 4, the stage-1 email, sent before `install_night_agent.sh` arms the
first DIAGNOSTIC_NO_PACK plan). `notice-evidence.txt` written to the staging
directory (copy in `02-arm-evidence/`). Ed's NO on the thread stands the
night down.

## What the arm record must carry (runbook §1.5 table)

| Item | Value |
|---|---|
| 1. Frozen plan and gate registration | plan_id `d079-epoch-25g83-derivation-n1-20260913`; frozen calibration plan sha256 `9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072` (= wrapper `PLAN_SHA256`); `registration_path` `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` = `night_gate.D166_REGISTRATION_PATH`, sha256 in the clone `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` |
| 2. Scientific pre-registration | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`; sha256 `84b820b9069c5b7b34b35e1b8fcd1c436c54ded04cbb24c6c985bbc867ce0b5c`; H `f90cb8c016662f8af6faa73d905fc472443432ab`; blob `87d4fb716b4b72ea3253261a2565726a0042ca5c` |
| 3. Rule and instructions | D-102 dated Ed addendum: commit `12162263` (2026-09-10; wording fix `07995051`); runbook revision 7, commit `53310262` (merged `18ab2cc4`) |
| 4. Capture inputs | wrapper `chain.zsh` sha256 `569daedae03126d9eb819abd3b132baf860597dbe926a0db87311643a854df45`; identity-epoch `b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607`; T1 bindings `8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98`; `EVIDENCE_ROOT_ID` `evidence-d079-epoch-25g83-derivation-n1-20260913` |
| 5. FAIL-route nights 2/3 | not applicable to night one |

## Executed — ARMED 2026-09-12 03:00:23 PDT

`40-arm.zsh` ran in the foreground from 03:00:18 to 03:00:23 PDT, rc 0
(full transcript `02-arm-evidence/arm-block-output.txt`). Step by step:

| Step | Observed |
|---|---|
| 0 span/stop | arm clock 1789207218.5 = 03:00:18.5 PDT, inside 03:00–06:30; local-time check of 1789293360 = `2026-09-13 02:56`; dead-man arithmetic holds; no `standdown.request`, no `STOP` |
| 1 pins | `notice-evidence.txt` non-empty; clone HEAD = H; tree clean; `git fetch origin main` then `merge-base --is-ancestor H origin/main` PASS |
| 2 wrapper | `--verify`: `VERIFIED …/chain.zsh sha256=569daedae03126d9eb819abd3b132baf860597dbe926a0db87311643a854df45` |
| 3 staged plan | all assertions PASS (`DIAGNOSTIC_NO_PACK`, 9000 s, both heads H, D-166 registration hash `dfe55f8d…1ac265`, authored 01:03:17 within 36 h of now and of t0, now < t0 − 1500 s, same filesystem device) |
| 4 census | `ps … grep -E 'claude (daemon run\|bg-spare\|bg-pty-host)\|--resume'` matched only the grep itself; `launchctl list` = `com.joulewise.magistrate` only; no discoverable plan; `pgrep -fl 'codex\|claude\|t3'` rc 0 with two hits, pids 94366 and 94373 (the Codex MCP server this activation's harness starts), ancestry `[94366, 94352, 94349]` / `[94373, 94366, 94352, 94349]` through the lock pid 94352 → OWN; foreign matches `[]`. Both die with this activation, long before t0. |
| 5 publication | `os.replace` → `PUBLISHED /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/night_plan.json` |
| 6 install | `scripts/install_night_agent.sh --plan <night root>/night_plan.json --hour 2 --minute 56 --python <clone>/.venv/bin/python` from the clone: driver preflight `{"preflight": "ok", "python": "<clone>/.venv/bin/python", "version": "3.13.1", "modules": [scripts.run_night, joulewise.arm_readiness, joulewise.arm_readiness_evidence_t0, joulewise.t0_rehearsal, joulewise.night_gate, joulewise.measurement_liveness]}`; `validated pins: repo_head=f90cb8c0… measurement_root=/Users/edr/JouleWise-measurement-20260913-derivation measurement_head=f90cb8c0…`; both agents loaded |
| 7 inspect | `launchctl list`: `com.joulewise.night` (0), `com.joulewise.magistrate` (0), `com.joulewise.night.deadman` (0). `plutil -p` night: `StartCalendarInterval` Hour 2 Minute 56, `WorkingDirectory` the clone, `ProgramArguments` = clone venv python, `<clone>/scripts/run_night.py run --plan <night root>/night_plan.json --courier-bin /Users/edr/.local/share/claude/versions/2.1.268`, `RunAtLoad` false, stdio to `<night root>/night/launchd.night.{out,err}`, PATH `/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin`. Dead-man: Hour 7 Minute 0, same program/root, `dead-man` subcommand, `RunAtLoad` false, stdio `launchd.deadman.{out,err}`. `night/` baseline: EMPTY (`[]`). Published plan `cmp` equal to the staged copy; sha256 `a6e83d14b3143dd5313e30c0f5a0f4688bb23ceb3b5c4f8c91378221533e2131`. Power: AC, battery 80 % not charging, `powermode 0`. |

**Frozen triple in force:** `(d079-epoch-25g83-derivation-n1-20260913,
/Users/edr/JouleWise-measurement-20260913-derivation, f90cb8c016662f8af6faa73d905fc472443432ab)`.
The watchdog renders it into the next relaunch prompt from the published
plan; the clone must not be moved, fast-forwarded or checked out until the
night completes.

**Expected observations before the harvest:** the 07:00 PDT 2026-09-12
dead-man firing stands down with one `night.log` line and nothing else in
`night/`; the watchdog's plan span opens at 02:31:00 PDT 09-13 with its
stand-down request to whichever activation is then alive; the night agent
fires at 02:56:00 PDT 09-13.

This activation exits after this record is pushed (no own background work
remains; the two MCP server processes die with it).
