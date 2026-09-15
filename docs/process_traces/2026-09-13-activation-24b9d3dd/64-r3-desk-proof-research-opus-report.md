# 64 — Research for directive #337 ruling 3 (the Ed-hands desk proof of ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01): what `scripts/author_arm_evidence_t0.py` needs, how a pack root is built, what refuses (Opus 5 read-only research agent, delivered 2026-09-14 ~17:05 PDT)

Verbatim final report of the read-only Opus research agent (worktree wt-bk-24b9d3dd; nothing written outside /tmp).

---

**Headline:** the tool exists and does what the acceptance says, but the acceptance's success branch is *all-or-nothing*: the `t0.no_stray_keepawake` source record is written only if **all fifteen** T-0 rows derive (`joulewise/arm_readiness_evidence_t0.py:2318-2401` — sources/receipts are staged and published only after the loop, `_validate_capture_order`, and staged discovery all pass). A refusal anywhere writes **nothing** but the REFUSE JSON. So "just run it with no browser open" cannot produce the evidence; the full six-step T-0 capture ceremony must pass first. Second hard finding: **no pack root in current `main` can carry the tool past its first check** (§A2). Both are magistrate work, and both are cheap to fix in a throwaway clone.

## 0. Facts read (citations)

| Claim | Evidence |
|---|---|
| CLI is exactly `--pack-root` + `--custody-root`, both required | `scripts/author_arm_evidence_t0.py:25-27`; signature assertion `joulewise/arm_readiness_evidence_t0.py:2409-2414` |
| pack's repo must equal the CLI's own repo | `scripts/author_arm_evidence_t0.py:33-42`; again at `joulewise/arm_readiness_evidence_t0.py:2255-2262` |
| exit 0 = PASS JSON on stdout; exit 2 = REFUSE JSON (`status`,`kind`,`reason_codes`,`detail`) | `scripts/author_arm_evidence_t0.py:55-82` |
| row order; census is **10th of 15** | `joulewise/arm_readiness_evidence_t0.py:103-117`; order enforced identical at `:946-963` |
| nine rows precede it: `clock.correct_and_prior_state`, `clock.network_time_off`, `desk.terminal_review`, `t0.background_quiet`, `t0.campaign_lock_absent`, `t0.display_thermal_idle`, `t0.fresh_roots_waivers`, `t0.ledger_reservation`, `t0.machine_readiness` | same, `:104-112` |
| census = 4 probes in order keep-awake, agent, browser, monitor; each must be `exit 1` + empty stdout | `:1724-1741`, `_expect_absent` `:1316-1318` |
| the two ruled argv | `:57-58` — browser `"/Contents/MacOS/(Safari\|Google Chrome\|Chromium\|firefox)( \|$)"`, monitor `"powermetrics\|window-chain\|run_campaign\|tail -f\|(^\|/)watch( \|$)"` |
| probe record fields are exactly `argv,cwd,exit_code,stdout,stderr` (no label) | `_ProbeResult.evidence()` `:284-291` |
| source record path `<custody>/<pack_id>/arm_readiness.t0.sources/t0-no-stray-keepawake.json` | `:45`, `_slug` `:370-371`, `_source_path` `:374-375` |
| receipt `…/arm_readiness.evidence/evidence-t0-t0-no-stray-keepawake.json` (+`.sha256`) | `:46`, `:378-379`, `:2350-2352` |
| six required captures, in order, ≤60 min old, same boot session | `_CAPTURE_FILES:170-177`, `_capture:520-569`, `_MAX_T0_SEQUENCE_AGE_NS:52`, `_validate_capture_order:2266-2279` |
| census probes refuse unless the R1 clock batch already finished | `_fresh_probe:480-497` + `:1124` |
| T-0 span must be **≥600 s and ≤3600 s** | `_MIN_IDLE_NS:51`, checks `:1165-1169` |
| HEAD must carry `JouleWise-Terminal-Review: PASS`, `-Tree-Oid`, `-Pack-Sha256` incl. this pack | `:1257-1280`; duplicated in `scripts/capture_t0_step.py:215-252` |
| HEAD must equal `refs/heads/main` **and** `refs/remotes/origin/main`, tree clean incl. untracked | `joulewise/arm_readiness.py:5542-5564` |
| the six capture commands (incl. `sudo -n systemsetup -setusingnetworktime off`, `quiet_mac_prep.sh`, `prewindow_check.sh --wait --timeout-min 45`, a real `reserve_calibration_window_bracket.py … --execute`) | `scripts/capture_t0_step.py:472-545`, `:406-416` |
| `window.env` exact-key contract + window-plan root must sit inside the custody root | `scripts/capture_t0_step.py:265-360` |
| custody/window/runs roots are arbitrary absolute paths — **no** hardcoded location | `scripts/capture_t0_step.py:284-296`; `joulewise/arm_readiness_evidence_t0.py:2264-2266`; roots read from `arm-context.json` `:996-1013` |
| **no** `launchctl`, `night_plan.json`, or `night-custody` check anywhere in the author, the capture tool, `quiet_mac_prep.sh`, or `prewindow_check.sh` | grep over those five files: zero hits |

## A. Magistrate preparation (exact, in order)

**A1 — fresh clone + venv.** Do *not* touch `/Users/edr/JouleWise-measurement-20260915-derivation` (armed night). Clone/venv commands are the locked ones at `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1508-1522`; stay **on `main`** (do *not* `checkout --detach` — `reviewed_main` requires `HEAD == refs/heads/main == refs/remotes/origin/main`).

```sh
export CLONE=/Users/edr/JouleWise-desk-proof-20260915
test ! -e "$CLONE" && git clone --no-hardlinks /Users/edr/code/JouleWise "$CLONE"
cd "$CLONE" && git rev-parse HEAD                 # expect origin/main = 6d2d62d8 (or later)
python3.13 -m venv .venv
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
        <(.venv/bin/python -m pip freeze --exclude-editable | sort)   # must be empty
```

**A2 — pick a usable pack. This is the blocker.** I resolved every committed pack read-only in the worktree:

* the three `_v1` packs resolve a profile (`joulewise/arm_readiness.py:415-419`) but their `plan.path` is *repository*-relative, so `resolve_frozen_plan` refuses ("frozen plan is missing… `configs/campaigns/…/calibration_plan.json`"); only `d117_contrast_qwen25_1p5b_vs_7b_v1` resolves, and **its** `plan_tree.roots` uses `claim_leaf`/`bound_leaf`, which `_root_observation` rejects (it requires `claim_root_leaf`/`bound_root_leaf`, `joulewise/arm_readiness_evidence_t0.py:1014-1020`) — refusal at row 5, before the census;
* the `_v2`/`_v3` packs have the right shape but are not installed by the live registry, whose `successor_pack_ids` name three `_v5` Qwen3 packs that **do not exist** (`configs/arm_readiness/d117_row_registry_v2.json`; `_plan_profile` `joulewise/arm_readiness.py:4446-4472`).

Verified read-only: patching `successor_pack_ids` to `{"ALPHA":"d117_floor_qwen25_1p5b_v3", …}` makes `d117_floor_qwen25_1p5b_v3` resolve **ALPHA**, its frozen plan resolve pack-relative (`calibration_plan.json`), its roots carry `claim_root_leaf`/`bound_root_leaf`, and its ARM_ONLY row census equal the ratified fifteen. `_v3` matches the approved successor name shape (`joulewise/arm_readiness.py:420-433`), and the registry bytes must equal HEAD's (`:4520-4530`) — so **commit the patch in the throwaway clone**. The T-0 author never loads the freeze reference (no `freeze` symbol appears in `arm_readiness_evidence_t0.py`), so the `_v3` pack's stale registry-v1 pin does not bite here (it *would* bite `generate_arm_readiness.py arm`, which the desk proof does not run).

**A3 — build the desk roots** (nothing under `/Users/edr/night-custody/`; arbitrary roots are accepted, see §0). Model it on `scripts/ed_session/build_rehearsal_env.sh:91-175`, which is the working template for exactly this: it mkdirs the roots, copies the committed 76-row ledger fixture, derives `identity-epoch.json`/`t1-bindings.json` from its last receipt, writes `waivers.json` = `[]`, extracts `window-chain.zsh` from the runbook with one `REPO=` line, and emits the 25-key `window.env`. Do not reuse the script as-is (it hardcodes `/Users/edr/JouleWise-measurement-20260818` and branch `integration/phase2-transaction`, `:6-8`). Layout:

```
/Users/edr/desk-proof-arm-census/
  arm-readiness-custody/            <- --custody-root, = ARM_READINESS_CUSTODY_ROOT
    window-plan/                    <- --window-plan-root (must be inside custody)
      window.env  window-chain.zsh  waivers.json  extraction_spec.json
      before_midpoint_stages.txt  after_midpoint_stages.txt
  window-custody/  quarantine/      <- CUSTODY_ROOT=WINDOW_CUSTODY_ROOT, QUARANTINE_ROOT
  runs_d117_floor_qwen25_1p5b_v3/   <- RUNS_ROOT leaf must equal plan_tree claim_root_leaf
  runs_d117_floor_qwen25_1p5b_v3_bound/
  backups/claim  backups/bound      <- distinct, writable, ≥20 GiB free (evidence_t0:1916-1941)
  inputs/calibration_observation_ledger.jsonl   identity-epoch.json   t1-bindings.json
```
Ledger route (this is what the August rehearsal could not solve): set `LEDGER_HEAD_PIN=$CLONE/configs/calibration/calibration_ledger_head.json` (committed; the check is on the **pin**, not the ledger — `joulewise/calibration_ledger.py:1268-1288`, `:2149-2154`) and `CALIBRATION_LEDGER=` a copy of `tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl`. Verified: that fixture is 76 rows ending `08456d50…`, exactly the committed pin's `sequence`/`head_digest`. Production ledger untouched.

**A4 — terminal-review commit** (after A2's registry commit), verbatim shape from `docs/process/rehearsal-operator-card.md:30`: compute `TREE_OID` and `PACK_SHA256` (`committed_pack_tree_sha256`), `git commit --allow-empty --cleanup=verbatim` with the three trailers, then `git update-ref refs/heads/main HEAD && git update-ref refs/remotes/origin/main HEAD`. Then `git status --porcelain=v1 --untracked-files=all` must print nothing (the `.venv` must be ignored — check this; it is the likeliest silent trip).

**A5 — magistrate dry gate (no sudo, no measurement, agents may be running).** Run the real tool with no captures present:

```sh
cd "$CLONE" && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/author_arm_evidence_t0.py \
  --pack-root "$CLONE/configs/campaigns/d117_floor_qwen25_1p5b_v3" \
  --custody-root /Users/edr/desk-proof-arm-census/arm-readiness-custody
```
Expected **exactly**: exit 2 and `{"status":"REFUSE","kind":"CLOCK_ATTESTATION","reason_codes":["evidence_author_t0_clock_attestation_missing"],…}` (`_RUNBOOK_ARTIFACT_REASON_CODES:181`, reached via `_capture:531-537`). Any other reason code means A1-A4 are not yet right, and Ed must not be called. This gate proves the pack, registry, repo-match, terminal review, plan, and pack digest all pass without spending Ed's evening.

## B. Ed's command block

Preamble: AC power, low-power mode off, no browser, no Claude Code/Claude app/ChatGPT app/codex MCP server, no `caffeinate`, display asleep, passwordless-sudo for `systemsetup` and `powermetrics` installed. The whole block must finish **within 60 minutes** of step 1 and take **at least 10 minutes** (`_MIN_IDLE_NS`); step 4 alone needs ≥600 s of clean dwell (`scripts/prewindow_check.sh:37,188-190`). Step 2 turns network time **off**; restore it at the end.

```sh
export CLONE=/Users/edr/JouleWise-desk-proof-20260915
export PACK=$CLONE/configs/campaigns/d117_floor_qwen25_1p5b_v3
export CUSTODY=/Users/edr/desk-proof-arm-census/arm-readiness-custody
export WPLAN=$CUSTODY/window-plan
cd "$CLONE"
for step in clock-reference clock-disable quiet-mac-prep prewindow-check ledger-readiness ledger-reservation; do
  .venv/bin/python scripts/capture_t0_step.py "$step" \
    --pack-root "$PACK" --custody-root "$CUSTODY" --window-plan-root "$WPLAN" || break
done
.venv/bin/python scripts/author_arm_evidence_t0.py --pack-root "$PACK" --custody-root "$CUSTODY"
/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on   # ALWAYS, even after a refusal
```
(Run the loop body one step at a time if you want to see each capture; `quiet-mac-prep` needs the display asleep and `prewindow-check` blocks for ~10-45 min.)

**Success looks like:** exit 0 and a JSON object with `"status":"PASS"`, `"authored_rows"` listing all fifteen, `"mutated":true`, and 30 `receipt_paths`. Then read the record:

```sh
/usr/bin/python3 -m json.tool \
  "$CUSTODY/d117_floor_qwen25_1p5b_v3/arm_readiness.t0.sources/t0-no-stray-keepawake.json"
```
It must show `"kind":"PROCESS_CENSUS"`, `facts[0].value` = `{"absent_process_classes":["agent","browser","keep_awake","monitor"],"fresh_process_census":true}`, and a `probes` array of exactly four entries **in this order** — `["/usr/bin/pgrep","-x","caffeinate"]`, `["/usr/bin/pgrep","-lf","codex|claude|t3"]`, then the two ruled ones (`…-lf`, `/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)` and `powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)`) — each with `"exit_code": 1` and `"stdout": ""`. Those last two entries *are* the acceptance evidence. There is no `label` field; the classes are positional.

## C. Preconditions, refusals, earliest safe time

* **Nothing refuses on the armed night's mere existence.** Verified by grep: neither `author_arm_evidence_t0.py`, `capture_t0_step.py`, `arm_readiness_evidence_t0.py`, `quiet_mac_prep.sh` nor `prewindow_check.sh` mentions `launchctl`, `com.joulewise`, `night_plan`, or `night-custody`. Installed-but-idle launchd agents do not match anything.
* **Live processes do refuse, twice.** `pgrep -lf 'codex|claude|t3'` must return exit 1 with empty stdout (`_derive_process_census`/`_expect_absent`), and `prewindow_check.sh:147-152` independently blocks on `ps aux | grep -E "codex|claude|t3|mcp-server|run_campaign|window-chain"`. The magistrate watchdog (which spawns `claude`) and any Codex MCP server must be gone. `quiet_mac_prep.sh:38` also prints an agent census.
* Therefore: **do not run this while the night is live.** Earliest safe time is after the courier deadline 05:31 PDT 2026-09-15, after both night agents are uninstalled, and after every agent session on the machine is closed. Running it earlier risks colliding with the night driver's own window and would almost certainly refuse at the agent probe anyway.
* Other refusals Ed should preserve rather than retry around: `quiet_mac_prep.sh:92-99,115` (display awake / screensaver / HID idle), `:47-50` (sudo -n powermetrics), row 12 `sudo -n powermetrics -i 200 -n 1` (`arm_readiness_evidence_t0.py:1803-1812`), row 13 AC power + low-power-mode-off + known-wattage adapter (`:1837-1863`), row 15 ≥20 GiB free on both backup dests (`:1916-1941`).
* The three T-0 output namespaces are no-clobber; a clean retry needs them removed (`docs/process/rehearsal-operator-card.md:128`), and every retry restarts the ≤60 min clock.

## D. Open questions / what I could not resolve

1. **Is the acceptance meant to require a full PASS?** As written it demands the emitted record, which the code only writes on a fifteen-row PASS, while also saying an earlier refusal "is reported". Those coexist only if the reported-refusal branch leaves the lane open. If the magistrate wants a cheaper proof, that is a ruling (a run that reaches row 11+ and refuses there also proves the census passed, but rows 1-9 still cost the whole ceremony).
2. **The A2 registry patch is a governance act**, not a mechanical one: it makes a throwaway clone's registry name a pack the real registry does not install. It never leaves the clone, but it is a "reinterpretation of an installed roster" and, by rule 11, looks like cold-gate material.
3. **Untested end-to-end.** No run of this tool has ever completed on this machine — verified: `git log --all --diff-filter=A -- '*t0-no-stray-keepawake*' '*arm_readiness.t0.sources*'` is empty, and no `arm_readiness.t0.*` directory exists under the measurement clones, `night-custody`, or `night-archive`. The August 2026 rehearsal stopped at E-8 on `calibration_ledger_head_uncommitted` (`docs/process/rehearsal-operator-card.md:14,79`). §A3's pin/fixture route is my read of `calibration_ledger.py:1268-1288,2149-2154` and has **not** been executed; the magistrate should prove steps 5-6 of §B against the scratch ledger before booking Ed.
4. **Closest prior evidence** is not a run of this tool but the hand-run probes at `docs/process_traces/2026-09-13-activation-24b9d3dd/34-coldgate-packet-arm-census-browser-probe/exhibit-C-live-probes.md:32,59,64-65`: pre-#335 browser `exit 0`, 22 lines; monitor `exit 0` on `watchdogd`; agent `exit 0`, 22 lines against Ed's own session. Post-#335 the two ruled patterns are expected to collapse to `exit 1`; the agent probe is exactly why this must be Ed's hands, not a seat's.
5. I did not verify that `.venv` is gitignored in a fresh clone (it must be, or A4's clean-tree check fails), nor did I run `prewindow_check.sh` or any capture — all of that is measurement-adjacent and outside my read-only scope.
