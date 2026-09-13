# 01 — Harvest record: `d079-epoch-25g83-derivation-n1-20260913` (REFUSED at t0, agent present)

Activation `c5048879`, 05:35–05:52 PDT 2026-09-13. Runbook
`docs/phase_2/derivation_night_runbook.md` §2.0–§2.2 at `878bce6c` and
NIGHT_HANDBACK §Next lane at H. Preconditions: plan span completion boundary
05:31:00 PDT passed; `night/courier.sent` present (02:57:26).

## §2.0 Coordinates rebuilt from the frozen triple

| Value | Result |
|---|---|
| `PLAN_ID` / `MEASUREMENT_ROOT` / `H` | `d079-epoch-25g83-derivation-n1-20260913` / `/Users/edr/JouleWise-measurement-20260913-derivation` / `f90cb8c016662f8af6faa73d905fc472443432ab` |
| `PY` executable; clone HEAD = H; tree clean | yes; `f90cb8c0`; `git status --porcelain` empty |
| `night_plan.json` `custody_root` = `NIGHT_ROOT` | yes (`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913`) |
| Sidecar check | `chain.zsh` sha256 `569daedae03126d9eb819abd3b132baf860597dbe926a0db87311643a854df45` = `chain.zsh.sha256`; chain-source sidecar `b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf` |
| `gen_derivation_night.py --verify` (read-only re-derivation from the clone) | `VERIFIED …/chain.zsh sha256=569daeda…df45`, rc 0 |
| Exports read from the wrapper | `SESSION_ID` = plan id; `EVIDENCE_ROOT_ID` = `evidence-d079-epoch-25g83-derivation-n1-20260913`; `PLAN` = `<night root>/calibration_plan.json`; `RUNS_ROOT` = `<night root>/runs` (never created: no chain ran) |

## §2.1 What was read

- `night.log` (765 bytes): `2026-09-12T07:00:04 dead-man fired before the
  night's completion epoch 1789302660; standing down` (expected);
  `2026-09-13T02:56:02.507 night driver started`;
  `02:56:02.595 night gate verdict=REFUSED reason=night_refused_agent_present
  detail=pgrep exit 0; forbidden process output: 24974 claude / 24994 node
  …codex mcp-server … / 24996 …codex mcp-server … / 25641 ChatGPT.app …
  Codex (Service) …`; `night gate refused`; `durable record pushed
  branch=night-results/20260913` (×2); `courier attempt=1 heartbeat=True
  sent=True`.
- `night/result.json`: verdict `REFUSED`, `aborted_reason
  night_refused_agent_present`, `chain_exit_code null`, `chain_sha256 null`,
  `census_count 0`, started 1789293362.507 / ended 1789293362.5956 (89 ms).
  Artifact digests: `night.log` `56cabc88…873b39`, `receipt.json` =
  `refusal.json` `edfd6c39…53dc1` (byte-identical, 94226 bytes),
  `censuses.jsonl` `c6c50566…2ba90e`.
- `night/refusal.json`: C1 FAIL ("not evaluated after refusal"); C2
  `NOT_APPLICABLE` / `no_pack_by_design`; C3 FAIL — probe `/usr/bin/pgrep -lf
  codex|claude|t3`, exit 0, stdout the four processes above; C4/C5 FAIL after
  refusal (C5's measured pins all `f90cb8c0` per the courier's read).
- `night/censuses.jsonl`: the single refusing census (argv, exit 0, the
  refusal detail).
- Chain log `<night root>/operator_logs/derivation-chain.log`: ABSENT (no
  chain started; correct for this refusal).
- launchd streams: `launchd.night.err` 0 bytes (required EMPTY: met);
  `launchd.night.out` 2481 bytes, mtime 02:58:25 — the courier's own closing
  summary (its `claude -p` stdout is the driver's stdout); `launchd.deadman.out`
  / `.err` 0 bytes (09-12 07:00). Compared with the arm-time baseline
  (`night/` EMPTY): every file is this night's.
- `night/courier.sent`: message `1a09a3319d602a37`, to
  `claude.ai.copper531@passmail.net`, sent epoch 1789293446 (02:57:26), pid
  3777, verdict REFUSED, results branch `night-results/20260913`. Verified in
  the SENT thread at 05:38 (Gmail `get_thread`). `courier.json`: attempted 1,
  sent true, heartbeat seen, no error.
- Results branch `origin/night-results/20260913`: `f0a3131a` + `e2dd56d5`
  "record night 20260913" on top of `878bce6c` (four courier files under
  `docs/process_traces/night-results/20260913/`). Verified by fetch.

## Byte-exact preservation and inventory

- `lstat` inventory (size, mtime with ns, path) of every file in the night
  root except `results-clone/`, taken BEFORE anything else at 05:36:
  `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260913-harvest-20260913.lstat-inventory.txt`
  (20 files). Copy of the same inventory in this record's evidence dir.
- Byte-exact copy outside watchdog discovery: `cp -Rp` of the whole night root
  (242 MB with `results-clone/`) to
  `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260913-harvest-20260913`;
  `SHA256SUMS` (20 files, `results-clone/` excluded) written from the copy and
  checked against the original: every line OK.
- Nothing in the night root was moved, altered or deleted. Clone and night
  root are RETAINED (handback: production custody, inventory row).

## §2.2 Ledger dry run (counts and states only)

`check --session-ids d079-epoch-25g83-derivation-n1-20260913` from the clone:
epoch watch `os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256 d1dccad0…
→ b762e5bf… MISMATCH`, `hardware_model` and `mlx_version 0.31.2` match;
registration dry run: session `absent`, prefix pending/unresolved rows 0,
`registration admissible for prepare-candidate: no`, `blocker: session … is not
in the ledger`. Ledger unchanged since the arm: 76 records, sha256
`aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`, head pin
76 / `08456d50…94d7`.

## §2.5 The equivalence rule: nothing to judge

No session opened, so m has no value (not "m = 0 retained of 12": no slot
existed). `scripts/epoch_equivalence_check.py --session-id … --acceptance
configs/calibration/calibration_acceptance_d079_v2_n17_r6.json --out
/tmp/magistrate-c5048879/epoch-equivalence-record-1.json` from the clone:
`REFUSED: session d079-epoch-25g83-derivation-n1-20260913 is not in the
ledger`, rc 3, nothing written (a second run has nothing to compare). No
verdict is recorded. The governing text is the handback's own: an
`night_refused_agent_present` receipt "is a correct refusal — the rows ran and
refused — and the night is re-planned, never re-armed on the same plan."

## Uninstall (documented post-completion step)

05:39:52 PDT, FROM the clone: `scripts/install_night_agent.sh --plan
<night root>/night_plan.json --hour 2 --minute 56 --uninstall` rc 0.
`launchctl list | grep joulewise` → `com.joulewise.magistrate` only; both
`com.joulewise.night*.plist` files gone from `~/Library/LaunchAgents`; clone
HEAD still `f90cb8c0`, tree clean. NOTHING ARMED. The watchdog's
`fenced_checkouts` still lists only the canonical root.

## Findings

- **F1 (operator, not a defect).** The refusal was caused by an interactive
  session Ed launched on 09-12 (Paper-N) and its Codex MCP servers being alive
  at t0; the arm-time notice, the 12:54 heads-up (undelivered: Gmail expired)
  and notice issue #333 all asked for it to be closed before 02:31. The same
  processes held the watchdog in `HOLD_CENSUS` for the whole span.
- **F2 (lane, ruling-first).** The night census pattern `codex|claude|t3`
  also matched the ChatGPT desktop app's own Codex helper (`Codex (Service)
  … --standard-schemes=app,codex-sandbox …`). Registered as
  `NIGHT-CENSUS-CHATGPT-APP-01`: either the app is quit for every night (the
  09-08 notice already offered that) or the pattern is narrowed under a
  ruling; the magistrate does not change a gate rule at the desk.
- **F3 (observation).** `launchd.night.out` carries the courier's closing
  summary; the handback's EMPTY requirement is on `launchd.night.err` only,
  which was met.

## Next exact action

Re-plan as `d079-epoch-25g83-derivation-n1-20260915` (t0 Tue 2026-09-15
02:56:00 PDT, install Mon 2026-09-14 03:00–06:30 PDT) through the ordinary
runbook §0–§1.5 and NIGHT_HANDBACK email-then-arm. Precondition that only Ed
can satisfy: pid 24974 (and any interactive seat) closed and the ChatGPT app
quit before 02:31 on the night, or an explicit KILL from Ed.
