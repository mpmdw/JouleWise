```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Not ARM-READY: G2-a requires authentic calibration-ledger continuity, clean-tree/environment closure, approved production coordinates and live prerequisite verification.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
    "head_end": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
    "upstream_end": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-08-handoff-redo/ (pre-existing untracked artifacts)",
    "/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/joulewise.egg-info/"
  ],
  "verdict": {
    "rows": [
      {"row": "Authorized desk preparation", "action": "start_now"},
      {"row": "Production identity, custody, schedule and acquisition-head selection", "action": "needs_ruling"},
      {"row": "Real G2-a arm", "action": "wait_for", "wait_for": "All blocking prerequisites below"},
      {"row": "Measurement during an agent session", "action": "do_not_start"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git -C /Users/edr/JouleWise-measurement-v5-20260910-1c83f2a status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "?? joulewise.egg-info/"]},
      "expected": {"exit_code": 0, "tail_regex": "joulewise\\.egg-info/"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "environment", "level": "blocking", "text": "Missing ledger; dirty clone; preflight-environment lock mismatch.", "needs": "Authorized magistrate remediation and replay."},
    {"id": "F2", "kind": "lead_ruling", "level": "blocking", "text": "Production coordinates remain placeholders.", "needs": "Rule identity, custody, T0, duration and final reviewed head."},
    {"id": "F3", "kind": "verification_gap", "level": "blocking", "text": "No sudo, hardware, installation, email or collection performed.", "needs": "Lead-controlled live verification after desk closure."}
  ]
}
```

## Scheduling matrix

`C` = `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a`; `PY=$C/.venv/bin/python`. `R` = requested `SHAKEDOWN-G2-RUNSHEET.md`; `P` = adjacent `preflight.sh`; `README` = requested plan-seat README. Commands/actions are prospective. “Yes” includes prerequisites still requiring verification.

| prerequisite | current state (verified how, file:line or command output) | exact fix command or action | owner | blocking for G2-a DIAGNOSTIC_NO_PACK yes/no |
|---|---|---|---|---|
| Reviewed clone and routing | Detached `1c83f2af…`; Python 3.13.1. Replayed validator: parser, registration, generator, syntax and routing PASS. | Freeze approved head; reconcile handback rewrite and newer driver changes before final pins. Revalidate if head changes. | magistrate desk | Yes |
| Clean measurement tree | `git status`: `?? joulewise.egg-info/`; fails P:71–76. Trace 67’s “harmless” statement conflicts with this gate. | Preserve metadata externally; resolve generated metadata through reviewed environment/ignore policy, then require empty status. Do not silently waive gate. | magistrate desk; seat implements authorized repair | Yes |
| Exact lock comparison | Without `PYTHONPATH`, diff empty. With P’s `PYTHONPATH=$C`, reproduced `installed_only=['joulewise==0.1.0']`. Source egg-info lacks `direct_url`; venv dist-info correctly says editable. | Resolve duplicate source metadata; replay `PYTHONPATH="$C" "$PY" -m pip freeze --exclude-editable` against normalized lock. Do not add JouleWise to lock merely to hide discrepancy. | magistrate desk | Yes |
| Physical ledger and custody | `$C/runs` absent. Loader reproduced missing/rollback. Pin sequence 76; absent bytes yield physical sequence 0 (calibration_ledger.py:2013–2048). | Restore authenticated ledger matching committed sequence/digest and its referenced custody from verified source; authenticate with custody replay enabled. Never initialize empty ledger or reset pin. | magistrate desk | Yes |
| Ledger applicability | Class skips pack C2 (`night_gate.py:377–380`), not calibration. G2-a explicitly checks inputs, readiness and bracket reservation (R:501–526). | Retain ledger gate and governed pre/post calibration. Missing+rollback describes one absent-history condition, not proof of two separate incidents. | magistrate desk | Yes |
| Model/runtime and probe inputs | Dry validator does not authenticate live model bytes/Metal. G2-a root absent. | Authenticate panel revisions/tokenizers/runtime; execute R:374–385 `build-probes`/`bind-window`, then R:501 `check`; four rungs, five small/one large members. | magistrate desk; seat preparation | Yes |
| Sudo preflight | P:171–180 requires executable powermetrics and passwordless authorization; not run. | `/usr/bin/sudo -n -l /usr/bin/powermetrics`; Ed repairs governed sudoers if refused. No password fallback. | Ed sudo/hardware | Yes |
| Quiet hardware and live gates | Unverified; `quiet_mac_prep.sh:47` actually samples, so unsuitable for this scout. | Ed verifies AC/high-power, lid/display/backlight, sleep and outstanding service preparation; governed clock, HID, thermal/load checks and empty census. Run `bash "$C/docs/process_traces/2026-08-28-live-smoke/preflight.sh" "$STAGED_PLAN"` in permitted lane. | Ed sudo/hardware | Yes |
| Rehearsal acceptance | Handback:26–75 still describes stub; no night plists found in inspected LaunchAgents directory. Absence does not prove acceptance. | Harvest result/courier/stand-down; record acceptance; uninstall from recorded stub checkout and archive discovered stub roots. | magistrate desk | Yes |
| Production schedule | Draft placeholders; illustrative 02:56/10800 passes dry validation only. | Rule ID/root/T0/budget; actual authorship ≤36h; enforce `T0+window+300 < next 07:00`. At 02:56, window must be `<14340s`. | magistrate desk | Yes |
| Fresh writable custody | `ls -lde`: night-custody is `edr:staff`, 0755; production root unspecified. No observed parent permission defect. | Select fresh nonsymlink root; `mkdir "$NIGHT_ROOT"`; verify Ed can traverse/write and ledger/probe roots permit their required writes. Preserve existing evidence. | magistrate desk | Yes |
| Chain and watchdog tolerance | Generator passes; watchdog:686 parses same v2; :717–736 fences full window/courier span beyond 03:30. Literal draft fails parsing. | Emit chain/sidecar per README; canonical-write resolved plan outside discovery. Check conflicts and watchdog health before publication. | magistrate desk | Yes |
| Email and clone installation | Not performed; installer:80–100 checks both heads/courier. | Follow README steps 5–6: render/lint both plists; email Ed and record delivery; confirm no NO; atomically publish; run clone’s `scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE"`. | magistrate desk | Yes |
| Stand-down | Cannot prove agent absence while scouting. | Exit agents by T0−25m; verify TERM/KILL fences −16/−15m and empty acquisition census. Launchd alone collects. | magistrate desk | Yes |
| Production pack/stage 3 | C2 explicitly `NOT_APPLICABLE/no_pack_by_design`. | None for G2-a; retain later G2-b/claim gates. | magistrate desk | No |