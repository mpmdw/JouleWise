# 01 — Harvest record: `d079-epoch-25g83-derivation-n1-20260917` (REFUSED at t0, `night_refused_not_quiet`)

Activation `8789ee70` (watchdog attempt 47, pid 27554), launched 18:09:13 PDT 2026-09-17 after the armed span; launch email `1a0b2117abf4e24a`; `notice.ack` written; no directives; runbook §2.0–§2.5 at main `087813e0` and NIGHT_HANDBACK §Next lane standing rules. Preconditions: completion boundary 18:05:00 PDT passed; `night/courier.sent` present (15:32:27, message `1a0b17fdd4f8043a`, verified in the SENT thread with the courier's 15:32:43 follow-up `1a0b1802fbda0f2a`). A cooperative `standdown.request` arrived during the slice; this record was written under it (durable state first, then the stand-down email, then exit).

## §2.0 Coordinates rebuilt from the frozen triple

| Value | Result |
|---|---|
| `PLAN_ID` / `MEASUREMENT_ROOT` / `H` | `d079-epoch-25g83-derivation-n1-20260917` / `/Users/edr/JouleWise-measurement-20260917-derivation` / `92c178f863ccc9a9742f080108433a5afd148b2e` |
| `PY` executable; clone HEAD = H; tree clean | yes; `92c178f8`; `git status --porcelain` empty (before and after every step below) |
| `night_plan.json` `custody_root` = `NIGHT_ROOT` | yes |
| Sidecar check | `chain.zsh: OK` against `chain.zsh.sha256` (`f36010d6…aaa6e76`); chain-source sidecar `b5beea46…bead6fb` |
| Exports read from the wrapper | `SESSION_ID` = plan id; `EVIDENCE_ROOT_ID` = `evidence-d079-epoch-25g83-derivation-n1-20260917`; `PLAN` = `<night root>/calibration_plan.json`; `RUNS_ROOT` = `<night root>/runs` (never created: no chain ran) |

## §2.1 What was read

- `night.log` (556 bytes, copied to `01-harvest-evidence/night.log`): `15:30:01.732 night driver started`; `15:30:01.837 night gate verdict=REFUSED reason=night_refused_not_quiet detail=load_average predicate failed (maximum 2.0)`; `night gate refused`; `durable record pushed` (15:30:10 and 15:32:29); `courier attempt=1 heartbeat=True sent=True`. No dead-man line (19:05 never reached before the uninstall).
- `night/result.json`: verdict `REFUSED`, `aborted_reason night_refused_not_quiet`, `chain_exit_code null`, `chain_sha256 null`, `census_count 0`, `calibration_refusal null`, started 1789684201.7325 / ended 1789684201.8377 (105 ms); `receipt_class DIAGNOSTIC_NO_PACK`; artifacts `night.log` `7f67054f…`, `receipt.json` = `refusal.json` `478fb0bd…` (byte-identical), `censuses.jsonl` `2ac654b6…`.
- `night/refusal.json`: C1 FAIL (not evaluated after refusal); C2 `NOT_APPLICABLE` / `no_pack_by_design`; **C3 FAIL — `load_1m` 3.66 (raw `{ 3.66 3.87 4.06 }`) against the fixed maximum 2.0**; agent census `pgrep -lf codex|claude|t3` exit 1, stdout EMPTY (no agent present); AC attached (battery 85%); HID idle 0; C4 FAIL after refusal; C5 measured `chain_sha256` `f36010d6…` = wrapper digest, `measurement HEAD` at H.
- `night/censuses.jsonl`: the single launch census (exit 1, empty).
- Chain log `<night root>/operator_logs/derivation-chain.log`: ABSENT (no chain started; correct for this refusal). No ledger session opened, nothing captured; `runs/` never created.
- launchd streams: `launchd.night.err` 0 bytes (required EMPTY: met); `launchd.night.out` 2005 bytes (the courier's closing summary); no dead-man streams (never fired). Compared with the arm-time baseline (`night/` EMPTY): every file is this night's.
- `night/courier.sent`: epoch 1789684347, message `1a0b17fdd4f8043a`, courier pid 26429, verdict REFUSED. `courier.json`: attempted 1, sent true, heartbeat seen, no error.
- Results branch `origin/night-results/d079-epoch-25g83-derivation-n1-20260917`: `9bdc1296` + `73c7f122` on `087813e0`; all eight files under `docs/process_traces/night-results/<plan id>/` are BYTE-IDENTICAL to `night/` (cmp, this record's evidence).
- Load cause (courier sample at 15:32, not part of the gate record): `mediaanalysisd` 114% CPU, `fseventsd` 77%, five `mdworker_shared`; load 4.57 / 4.96 / 4.54. This activation at 18:10–18:19: load 1.29–1.50; `fseventsd` (pid 101) at 85–100% CPU continuously, 1152 CPU-minutes since the 09-15 19:55 boot (≈41% of one core averaged over 46 h), RSS only 24 MB; `mediaanalysisd` and Spotlight idle; `/System/Volumes/Data/.fseventsd` link count 65535 (entry count saturated), directory 11.7 MB, mtime 18:17:44; no user-space files modified in the preceding 2–3 minutes under `/private/tmp`, `$TMPDIR`, `~/code`, `~/night-custody`, `~/Library`, `~/.claude`, `~/.codex`, `/private/var/folders`, `/private/var/db`; zero orphan `fake vllm` fixtures. Root cause is NOT established: attribution needs root (`sudo fs_usage -w -f filesys`, `sudo ls /System/Volumes/Data/.fseventsd | wc -l`, `sudo du -sh` of it) — an Ed action.

## Byte-exact preservation and inventory

- `lstat` inventory (size, mtime ns, path; `results-clone/` excluded), taken BEFORE anything else at 18:15: `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260917-harvest-20260917.lstat-inventory.txt` (22 files; copy in `01-harvest-evidence/`).
- `cp -Rp` of the whole night root (253 MB with `results-clone/`) to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260917-harvest-20260917`; `SHA256SUMS` (22 files) written from the copy and checked against the LIVE root: 22 OK, 0 non-OK (copy in `01-harvest-evidence/`).
- Nothing in the night root was moved, altered or deleted. The plan root is NOT retired by this activation (the launch charge forbids moving a plan directory this session did not author; precedent 24b9d3dd record 48 retires a refused root as the §1.4 precondition of the NEXT arm). The clone is retained and inert.

## §2.2 Ledger dry run (counts and states only)

`check --session-ids d079-epoch-25g83-derivation-n1-20260917` from the clone (`01-harvest-evidence/22-check.txt`): epoch watch `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256 d1dccad0… → b762e5bf… MISMATCH`, `hardware_model` and `mlx_version 0.31.2` match; registration dry run: session `absent`, prefix rows 0, `admissible for prepare-candidate: no`, `blocker: session … is not in the ledger`; rc 5. Ledger unchanged since the arm: 76 records, sha256 `aa806848…`, head pin sequence 76 / `08456d50…`.

## §2.5 The equivalence rule: nothing to judge

No session opened, so m has no value. `scripts/epoch_equivalence_check.py --session-id … --ledger … --head-pin … --repo-root <clone> --out /tmp/magistrate-8789ee70/epoch-equivalence-record-1.json` (never under the plan root): `REFUSED: session … is not in the ledger`, rc 3, nothing written (`01-harvest-evidence/25-equivalence.txt`). Outcome of the night: **REFUSED-NO-DATA**; per NIGHT_HANDBACK §Next lane a `night_refused_not_quiet` receipt is a correct refusal — the night is re-planned as a NEW plan id, never re-armed on this one. A219 (NIGHT-RESERVE-HANG-01) cannot be retired on this night: no reservation ran, so there is no real `custody_elapsed_s` beside the probe's 3.575 s.

## Uninstall (documented post-completion step)

`scripts/install_night_agent.sh --plan <night root>/night_plan.json --uninstall` run FROM the clone at 18:16:24 PDT: **rc 0**; `launchctl list` shows no `com.joulewise.night*`; only `com.joulewise.magistrate.plist` remains under `~/Library/LaunchAgents`; clone tree clean (`01-harvest-evidence/…-uninstall-20260917.log`). NOTHING IS ARMED.

## Findings for the successor (registration, not rulings)

1. **Machine not quiet for science even below the load gate**: `fseventsd` burning ~0.9 of a core continuously would contaminate every floor of an equivalence night whose tolerances are ~5 J, and the 2.0 load predicate would NOT refuse it (load 1.3–1.5 now). Do not arm until the churn is attributed and cleared (Ed: the three root commands above; the 09-15 restart cleared it for under two days). Candidate lane NIGHT-GATE-LOAD-ATTRIBUTION-01: the not-quiet refusal and the arm desk block should record the top CPU consumers (`ps -Ao pid,pcpu,command -r | head`) so a refusal names its cause; any per-process quietness rule goes to the cold gate.
2. **Handback not rewritten for this plan** (courier finding): NIGHT_HANDBACK §Purpose / §Where / §Next lane at H still describe `n1-20260916`; ruling R-9 requires the rewrite with the night's plan. Candidate lane HANDBACK-REWRITE-CHECK-01: the arm step-4 checks compare the handback's plan id with the staged plan's before publication.
3. Hosted CI: main `087813e0`, `df71fe6f`, `88d73392`, `f0db2bb5`, `3fc54a6a` all green; H `92c178f8` red only on the fixture flake fixed forward by PR #356 (A229 evidence).
