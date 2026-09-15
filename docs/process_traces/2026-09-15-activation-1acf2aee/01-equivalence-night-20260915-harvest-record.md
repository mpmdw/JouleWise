# 01 — Harvest record: `d079-epoch-25g83-derivation-n1-20260915` (REFUSED at t0, machine not quiet)

Activation `1acf2aee`, 05:37–05:50 PDT 2026-09-15. Runbook
`docs/phase_2/derivation_night_runbook.md` §2.0–§2.5 and NIGHT_HANDBACK
§Next lane at H `27957b60`. Preconditions: plan span completion boundary
05:26:00 PDT passed (t0 1789466160 + `window_max_s` 9000); `night/courier.sent`
present (02:57:39).

## §2.0 Coordinates rebuilt from the frozen triple

| Value | Result |
|---|---|
| `PLAN_ID` / `MEASUREMENT_ROOT` / `H` | `d079-epoch-25g83-derivation-n1-20260915` / `/Users/edr/JouleWise-measurement-20260915-derivation` / `27957b6066104fa470dded61a3db06e723c728f0` |
| Clone HEAD = H; tree clean | `27957b60`; `git status --porcelain` empty |
| `night_plan.json` | schema v2, class `DIAGNOSTIC_NO_PACK`, `custody_root` = `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260915`, `measurement_head` = `repo_head` = H, `registration_path` `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`, authored 1789428403.26 (16:26:43 09-14) |
| Sidecar check | `chain.zsh` sha256 `356a0810032539663aca548b1223ad55b4e49c89519cfa0a04b8ec6821dc70ac` = `chain.zsh.sha256`; chain-source sidecar `b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf` (the tracked chain, unchanged since the 09-13 plan) |
| `gen_derivation_night.py --verify` (read-only re-derivation from the clone, six emit flags) | `VERIFIED …/chain.zsh sha256=356a0810…dc70ac`, rc 0 |

## §2.1 What was read

- `night.log` (494 bytes, four driver lines + two push lines):
  `02:56:03.527900 night driver started`; `02:56:03.733247 night gate
  verdict=REFUSED reason=night_refused_not_quiet detail=load_average predicate
  failed (maximum 2.0)`; `02:56:03.738698 night gate refused`; `02:56:22
  durable record pushed branch=night-results/20260915`; `02:57:39 courier
  attempt=1 heartbeat=True sent=True`; `02:57:41 durable record pushed` again.
  No 09-14 07:00 dead-man line: the agents were installed 16:26 on 09-14 under
  directive #336's evening-install authority, after that day's 07:00, so no
  dead-man ever fired on this plan (the courier flagged this as a discrepancy
  against the handback's expected line; it is explained, not a defect).
- `night/result.json` (copy in `01-evidence/`): verdict `REFUSED`,
  `aborted_reason night_refused_not_quiet`, `chain_exit_code null`,
  `chain_sha256 null`, `census_count 0`, started 1789466163.527894 / ended
  1789466163.733711 (206 ms). Artifact digests: `night.log` `e5126330…96413`,
  `receipt.json` = `refusal.json` `ccb20923…69df` (byte-identical, 5186
  bytes), `censuses.jsonl` `d3fc84c1…07c7a`.
- `night/refusal.json`: C1 FAIL ("not evaluated after refusal"); C2
  `NOT_APPLICABLE` / `no_pack_by_design`; **C3 FAIL** — five probes:
  `pgrep -lf codex|claude|t3` exit 1, stdout EMPTY (agent census clean);
  screensaver `idleTime` 0; `pmset -g batt` AC power, 80 %, not charging;
  `pmset -g` sleep 0 (prevented by powerd), displaysleep 0; `sysctl -n
  vm.loadavg` `{ 2.55 2.57 2.54 }` → `load_1m` 2.55 > `LOAD_MAX` 2.0
  (`joulewise/night_gate.py:1206`). C4 FAIL after refusal. **C5 PASS**:
  "window, plan freshness, measurement HEAD, and chain identity passed" —
  driver, measurement and plan heads all `27957b60`, chain sha256 equal to
  the expected, observed 1789466163.53 inside [t0, t0 + 9000].
- `night/censuses.jsonl`: one census record, exit 1, empty stdout, no refusal.
- Chain log `<night root>/operator_logs/derivation-chain.log`: ABSENT (no
  chain started; correct for this refusal). `runs/` never created.
- launchd streams: `launchd.night.err` 0 bytes (required EMPTY: met);
  `launchd.night.out` 1671 bytes, mtime 02:57:52 — the courier's closing
  summary; `launchd.deadman.out` / `.err` absent (the dead-man had not fired
  when the agents were uninstalled at 05:43). Compared with the arm-time
  baseline (`night/` EMPTY at record 52): every file is this night's.
- `night/courier.sent`: message `1a0a48017dad6a3e`, to
  `claude.ai.copper531@passmail.net`, sent epoch 1789466259 (02:57:39), pid
  47535, verdict REFUSED, reason `night_refused_not_quiet`. `courier.json`:
  attempted 1, sent true, heartbeat seen, no error. (This seat's Gmail scope
  is send-only; the inbox copy was not read.)
- Results branch `origin/night-results/20260915`: `ba0c4252` + `04630025`
  "record night 20260915" on top of `b41dadb7`. Verified by fetch at 05:38.

## Byte-exact preservation and inventory

- `lstat` inventory (size, mtime_ns, path) of every file in the night root
  except `results-clone/`, taken BEFORE anything else at 05:42:10:
  `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260915-harvest-20260915.lstat-inventory.txt`
  (18 files; copy in `01-evidence/`).
- Byte-exact copy outside watchdog discovery: `cp -Rp` of the whole night root
  to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260915-harvest-20260915`;
  `SHA256SUMS` (18 files, `results-clone/` excluded) written from the copy and
  checked against the original with `shasum -c`: 0 non-OK lines (copy in
  `01-evidence/`).
- Nothing in the night root was moved, altered or deleted. Clone and night
  root are RETAINED.

## §2.2 Ledger dry run (counts and states only)

`check --session-ids d079-epoch-25g83-derivation-n1-20260915` from the clone,
rc 5: epoch watch `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256
d1dccad0… → b762e5bf… MISMATCH`, `hardware_model Mac15,9` and `mlx_version
0.31.2` match; registration dry run: session `absent`, prefix pending or
unresolved rows 0, `registration admissible for prepare-candidate: no`,
`blocker: session … is not in the ledger`. Ledger unchanged since the arm:
76 records, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`,
head pin sequence 76 / `08456d50…94d7`.

## §2.5 The equivalence rule: nothing to judge

No session opened, so m has no value. `scripts/epoch_equivalence_check.py
--session-id d079-epoch-25g83-derivation-n1-20260915 --acceptance
configs/calibration/calibration_acceptance_d079_v2_n17_r6.json --out
/tmp/magistrate-1acf2aee/epoch-equivalence-record-1.json` from the clone:
`REFUSED: session d079-epoch-25g83-derivation-n1-20260915 is not in the
ledger`, nothing written (the output directory stayed empty; a second run
has nothing to compare). No verdict is recorded. The ONE ACTION under the
handback's own text — "A receipt refusing `night_refused_agent_present`,
`night_refused_not_quiet` or `night_refused_hid_idle` is a correct refusal —
the rows ran and refused — and the night is re-planned, never re-armed on the
same plan" — is: re-plan as a new plan; no re-arm of this plan. That action
is taken by this record (the plan is retired from the schedule below) and by
the successor plan, which is gated on the machine being quiet.

## Uninstall (documented post-completion step)

05:43:23 PDT, FROM the clone: `scripts/install_night_agent.sh --plan
<night root>/night_plan.json --hour 2 --minute 56 --uninstall` rc 0.
`launchctl list | grep joulewise` → `com.joulewise.magistrate` only; both
`com.joulewise.night*.plist` files gone from `~/Library/LaunchAgents`; clone
HEAD still `27957b60`, tree clean. NOTHING ARMED. The watchdog's
`fenced_checkouts` still lists only the canonical root.

## Findings

- **F1 (machine, not a defect; not an agent).** The refusal was caused by
  system load alone: at t0 the agent census was empty and every other C3
  probe passed. At 05:37 the same load persists (2.60 / 2.79 / 2.65) and its
  source is `fseventsd` (pid 553, root) at ~184 % CPU with 4721 CPU-minutes
  accumulated over a 12-day uptime. The fsevents client driving it cannot be
  identified without sudo (`sample`, `lsof /dev/fsevents` and `fs_usage` all
  refuse); Spotlight `mds_stores` and Time Machine are idle. Until the load is
  below 2.0 at t0 any successor plan refuses on the same predicate, so the
  successor is gated on Ed clearing or explaining the load (email
  `1a0a51594dc05767` names it). The predicate itself (`LOAD_MAX` 2.0) is a
  physics-side quiet fence and is not touched at the desk.
- **F2 (observation).** The courier's "missing 09-14 07:00 dead-man line"
  discrepancy is explained by the evening install (§2.1 above); the handback's
  expected-line text assumes the ordinary 03:00–06:30 install. No cure needed
  beyond INSTALL-WINDOWS-MULTI-01, whose notice text names every span.
- **F3 (observation).** An orphaned test-fixture process (`vllm serve
  /fake/model`, Python pid 96525, 10 days old, 0 % CPU, parent 1) is alive on
  the machine. It is outside the census pattern and contributes no load; noted
  for Ed, not killed by this seat.

## Next exact action

Release `N1-20260915-HARVESTED-AND-S2-5-ACTION-TAKEN` in the kernel with this
record as evidence (INSTALL-WINDOWS-MULTI-01 → queued, agent rank 0, D-181
cl.1), then start INSTALL-WINDOWS-MULTI-01 and PACK-ROOT-SUCCESSOR-V5-01 at
the desk. Successor night: a NEW plan through runbook §0–§1.5 and
NIGHT_HANDBACK email-then-arm, from a fresh clone at the then-current reviewed
H, only after the load source is cleared (1-minute load below 2.0 with the
census clean) — never a re-arm of this plan.
