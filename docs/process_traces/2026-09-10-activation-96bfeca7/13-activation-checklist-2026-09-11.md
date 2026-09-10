# Activation checklist — 2026-09-11, proposed G2-a arm for 09-12

PROPOSED (magistrate ruling due after rehearsal acceptance). Preparation
only; this is not a harvest, acceptance or arm record.

The activation is expected after 03:30–04:00 PDT on 09-11, beyond the stub's
03:16 completion and the fixed `[02:45,03:30)` belt. It must still verify
courier/process clearance; a clock alone cannot establish safe relaunch.
Target record/push/exit by 06:30 on 09-11. Absolute exit boundary for the
proposed new plan is **02:31 PDT on 09-12**, epoch **1789205460**. Do not
remain resident until that deadline after arming.

Working inputs: file 11 (handback and exact inventory row), file 12 (runbook
68), runbook 67, and the actual record
`../2026-09-09-rehearsal-harvest/123-rehearsal-20260911-arm-record.md`.
The brief calls it `123-arm-record-rehearsal-20260911.md`; that basename is
not present. Packet 04 and record 05 were read from the lead's sibling
`/Users/edr/code/JouleWise-wt-bk-96bfeca7` worktree; preserve them with the
lead's handoff. No clone/arm action in this checklist was run by the drafter.

## Ordered plan and time budget

Budget is an operational allocation, not a measured completion guarantee.
At a 03:30 launch, start the first row immediately; at 04:00, keep the same
latest milestones and use the spare 30 minutes. If a prerequisite fails,
follow the table below. Do not squeeze an unresolved gate into the window.

| Step | Target belt on 09-11 (PDT) | Allowance / completion condition |
|---|---|---|
| 1. Launch email and intake | 03:30–04:05 | 5 min after actual launch; acknowledge pending notices and directives |
| 2. Preserve and inspect rehearsal harvest | 04:05–04:25 | 20 min; evidence, inbox/remote and process checks |
| 3. Decide items 4/5/6 | 04:25–04:35 | 10 min; accept 5/6 only if evidenced; keep 4 pending new send |
| 4. Uninstall/retire stub | 04:35–04:45 | 10 min; preserved evidence and cleared ownership first |
| 5. Handback/inventory tests and H | 04:45–05:15 | 30 min; repair merged, tests green, reviewed direct main commit pushed |
| 6. Fresh clone at H | 05:15–05:35 | 20 min allowance; clean locked venv, ledger/custody and model checks |
| 7. Runbook 68 Block A | 05:35–05:55 | 20 min; desk inputs, staged canonical plan, twin rendered |
| 8. Step 3b | 05:55–06:00 | 5 min; own background work stopped; evidence recorded |
| 9. Block B, email then arm | 06:00–06:20 | Start no later than 06:05; all installation finishes before 06:30 |
| 10. Record, push, exit | 06:20–06:30 | 10 min; durable frozen triple, actual evidence, no own background work |

Hard stop: **if Block B cannot start by 06:05 PDT, do NOT arm; author the
notice for 09-13 instead.** This is **PROPOSED for this activation**: runbook
67 contains no 06:05 rule, but record 123's 03:00:10 timeline records that
operational last-start cutoff. The 25-minute reserve fits verification and
recording before the 06:30 installation close. Missing it is not permission
to install in the 07:xx hour. New 09-13 coordinates require fresh identities,
head/handback review, date-derived probe root and recomputed times; do not
reuse the 09-12 commands or silently edit an already published plan.

### 1. Launch email and intake

Read the new prompt's frozen-checkout list, `magistrate.lock`, state and
pending notices, stop/standdown requests, and owner-authored open directive
issue bodies at the work-slice boundary. Send the required launch email
under the activation's standing authority, record actual Gmail acceptance,
and acknowledge pending notices only after acceptance. State the harvest
and proposed 09-12 arm schedule and any blocker. The launch email is **not**
the later stage-1 arm notice: it precedes H and cannot close item 4.

Keep the canonical checkout `/Users/edr/code/JouleWise` fenced: perform no
Git operation there. Use the authorized linked worktree for bookkeeping,
remote queries, fetches and later worktree removal. The only canonical
supply read in the clone recipe is the ignored ledger file, as ruled.
Never start a measurement or full quiet preflight inside this activation.

### 2. Harvest rehearsal-20260911

Check the actual launch is beyond 03:16 and outside the belt. Preserve the
following before any uninstall or deletion, in the activation's allocated
harvest evidence directory outside `~/night-custody/*/night_plan.json`
discovery. Do not mutate the originals to make acceptance pass.

| Exact file/location | Check and retained evidence |
|---|---|
| `/Users/edr/night-custody/rehearsal-20260911/night_plan.json` | Match the byte copy `123-arm-evidence/arm-night_plan.json`, SHA-256 `a7447608c7c7dc0a3d2a3f6ab56489bd509c9206e8574746c1cf01d113c887bc`; frozen H `57ddad20226c6921d81a87b9d78e61950c14a74f` |
| `night/result.json` beneath that root | Actual verdict, chain exit, receipt/refusal locator, abort/refusal details |
| `night/receipt.json`, `night/refusal.json` as applicable | Actual C1–C5 rows; preserve any refusal and its exact reason/detail |
| `night/courier.sent`, `night/courier.json` | Actual send time/message ID; separately verify email in Ed's inbox |
| `night/chain.started`, `night/chain.exited`, `night/censuses.jsonl` | Launchd-origin/lineage evidence, actual chain termination and empty production census; compare recorded identities, not PID alone |
| `night/launchd.night.out`, `.err`, `night/launchd.deadman.out`, `.err` | Preserve whether present/absent, complete bytes, sizes and nanosecond mtimes; do not exclude stream files from item 5 |
| `/Users/edr/night-custody/rehearsal-20260911/night.log` | 09-10 pre-night dead-man line with actual timestamp, before 09-11 `night gate verdict=` line |
| `123-arm-evidence/arm-blockB-output.txt` | Baseline was `post-install night/ baseline: []` at 09-10 04:10:58; compare all current directory entries and pre-T0 timestamps |
| `123-arm-evidence/com.joulewise.night.plist`, `com.joulewise.night.deadman.plist`, and `render/` | Actual installed calendars/argv and source checkout, plus current launchd evidence; stub exit status 3 alone does not mean refusal |
| `night-results/20260911` on origin | Verify remote existence and exact SHA; fetch/read the result artifacts from the authorized linked worktree, compare to custody; a local branch or claimed push is insufficient |
| Shared recorded campaign/process custody per `docs/contracts/window_liveness.md` | Establish no live or indeterminate chain/campaign ownership before updates/deletion; a send marker clears neither |

Use the actual record 123 §Harvest pointer and runbook 67 §Expected
observations. The expected dead-man message is exactly:

```text
dead-man fired before the night's completion epoch 1789121760; standing down
```

It should have fired at 07:00 on **09-10**, epoch 1789048800. The number
inside the message is the **completion epoch**, not the line timestamp.
Retain every entry in `night/`, including launchd stream files. If it is
impossible to attribute a file to or exclude it from that firing, report the
ambiguity instead of treating it as empty evidence. Preserve the full root
byte-exact outside watchdog discovery and compare the copy before removal;
retain a separate `lstat` inventory of the original with sizes/mtime_ns.
A backup copy's copied timestamps do not replace the original inventory.

### 3. Acceptance decision: NIGHT-REHEARSAL-01 items 4/5/6

The following four bullets are **verbatim from runbook 67, §Expected
observations and harvest acceptance**:

- The 09-10 dead-man stand-down line precedes the 09-11 `night gate verdict=`
  line, and `night/` holds nothing from that dead-man firing. Record any
  deviation; do not silently exempt a file from this wording.
- A green `receipt.json` verdict is exactly `REHEARSAL_ONLY`, with C5 measured
  `chain_stub: built_in_stub_by_design`, `chain_sha256: null` and
  `expected_chain_sha256: null`. Refuter 62 spells out C1/C3/C4/C5 `PASS`,
  C2 `NOT_APPLICABLE` (`no_pack_by_design`); expected `result.json` is
  `REHEARSAL_ONLY` with `chain_exit_code: 0`.
- A `night_refused_agent_present` receipt can close item 5 only if its
  dead-man evidence passes; item 6 remains open. Any other refusal is a
  finding to cure first. Do not infer a refused receipt from launchd exit 3:
  the normal completed stub branch sets that status regardless of the gate
  verdict (`run_night.py:1672–1675`).
- The courier deadline is 03:16 PDT on 09-11, epoch `1789121760`. Preserve
  send evidence; a send record alone does not verify inbox delivery.


Item 4's acceptance text is **verbatim from
`docs/process/state_kernel.json`, NIGHT-REHEARSAL-01 acceptance evidence**:

> The stage-1 plan email (first armed date; launches without Ed's hand unless he replies NO) is sent before install_night_agent.sh arms a DIAGNOSTIC_NO_PACK plan

Decision now: pass/fail items 5 and 6 from the retained observations; item 4
remains PENDING until step 9's actual new notice acceptance. Do not require
an impossible already-sent H-pinned notice before H exists, and do not mark
the whole task closed while its email item is pending. The magistrate records
rehearsal acceptance and the proposed G2-a coordinates after 5/6 pass;
Block B closes 4 before publication/installation. Item 1 was already closed
by derivation 70/capture 104; a stub cannot re-prove the capture-timeout seam.
Inbox and remote-branch gaps remain gaps even with a green result.

### 4. Uninstall the stub and remove its disposable checkout/plan root

Only after evidence preservation, reviewed acceptance disposition and
recorded process clearance, run runbook 67's exact uninstall command FROM
the stub checkout. Do not invoke it from development or the new clone.

```zsh
cd /private/tmp/joulewise-rehearsal-20260911-checkout
scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260911/night_plan.json --hour 2 --minute 56 --uninstall
```

Runbook 67 quotes the uninstall command and requires evidence preservation;
record 123 supplies `git worktree remove`. The guarded removal sequence
below makes those instructions concrete. `HARVEST_ARCHIVE` is the allocated,
verified copy of the whole stub custody root; it must be outside discovery.
Inspect/record stream metadata before copying. Do not create the archive by
moving away unread evidence. No `--force`, checkout reuse or evidence loss.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?authorized linked worktree}"
: "${HARVEST_ARCHIVE:?verified archive copy of the whole stub custody root}"
export BOOKKEEPING_ROOT HARVEST_ARCHIVE
cd "$BOOKKEEPING_ROOT"
test "$PWD" != /Users/edr/code/JouleWise
python3 -B - <<'PY'
import os, subprocess
from pathlib import Path
archive = Path(os.environ['HARVEST_ARCHIVE']).resolve(strict=True)
parent = Path('/Users/edr/night-custody').resolve()
assert archive != parent and parent not in archive.parents
assert (archive/'night_plan.json').is_file()
assert (archive/'night.log').is_file()
rows = subprocess.check_output(['launchctl','list'], text=True)
labels = {line.split()[-1] for line in rows.splitlines() if line.split()}
assert not {'com.joulewise.night','com.joulewise.night.deadman'} & labels
PY
diff -qr /Users/edr/night-custody/rehearsal-20260911 "$HARVEST_ARCHIVE"
git worktree remove /private/tmp/joulewise-rehearsal-20260911-checkout
rm -r -- /Users/edr/night-custody/rehearsal-20260911
```

Export `BOOKKEEPING_ROOT` and `HARVEST_ARCHIVE` before the command block.
If a checkout is dirty or removal fails, preserve it and return the precise
blocker; do not force-remove. Verify the two night labels and discoverable
stub plan are absent, then remove the completed stub triple from the next
relaunch prompt. Never apply this deletion recipe to a production corpus.

### 5. Fill the handback, append inventory, test, commit H to main

Follow **file 11 §Exact activation Git sequence** in the authorized linked
worktree. It creates a fresh bookkeeping branch from fetched `origin/main`,
requires the reviewed gate-repair merge as an ancestor, and pushes the
reviewed two-file commit directly to remote main without force.

Fill file 11's §Executed fields with the actual harvest verdict, chain exit,
receipt/refusal, courier message/inbox evidence, results SHA, dead-man line
time and `night/` inventory, plus cleanup/acceptance records. Paste its four
courier sections into NIGHT_HANDBACK, replace the H-CLONE marker with
`/Users/edr/JouleWise-measurement-v5-20260911-g2a`, and keep the introduction
and existing Standing rules bytes unchanged. The live text says
`repo_head = measurement_head = H = this commit`.

Append file 11's exact five-key JSON row to
`configs/production_custody_inventory.json`, retaining existing rows:
`deployment_id=JouleWise-measurement-v5-20260911-g2a`, measurement root as
above, custody null, ledger at that clone's `runs/calibration_observation_ledger.jsonl`,
and the supplied notes. No SHA in the path: inventory must be inside H.
The new inventory root need not exist at commit/test time. The reader keeps
missing roots in the census; the plan's measurement checkout must exist
later during authentication. The focused test uses temporary fixtures and
can pass CI without `/Users/edr`. See file 11's exact source anchors.

Before committing, run precisely:

```zsh
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tests.test_rehearse_t0_unattended tests.test_docs_freshness tests.test_run_night tests.test_magistrate_watchdog
python3 scripts/gen_state.py --check
```

Review the diff, then the two-file staged diff. Commit/push under the supplied
small direct-bookkeeping convention and derive full H from that commit.
Verify remote main equals H; no clone cut or consolidated notice before that.
If tests expose required additional state changes, the lead applies its own
scope/authority rules; do not wave away a failure or edit generated regions.
H remains fixed even when the arm record later advances bookkeeping.

### 6. Fresh clone at H, locked environment and authenticated supply

Execute **file 12 §Fresh clone at H** once. It clones GitHub independently
into `/Users/edr/JouleWise-measurement-v5-20260911-g2a`, detaches at H,
reconstructs the locked venv, requires an empty normalized lock diff and
clean all-untracked status, restores exactly 76 ledger records with the
specified SHA-256, calls `load_calibration_ledger_snapshot(...,
verify_custody=True)`, and checks both models' revision/source and exact
tokenizer/template digests. The absolute iCloud custody locations remain
in use; copy no custody directories. Preserve all readiness output.

Prefer this fresh cut to fast-forwarding/renaming the provisional
`/Users/edr/JouleWise-measurement-v5-20260910-078a13a` clone. Its 078a13a4
cut, successful lock/ledger authentication and supplied tokenizer matches
are provisional evidence. A fresh cut follows the trusted recipe and
avoids inherited absolute venv/editable paths. Record 05 itself leaves model
authentication undone; the later match comes from the brief, so recheck at H.

### 7. Runbook 68 Block A

Stop own Monitor/background tasks before its first raw census (record 123's
parser finding). Check ownership of all matching processes; do not signal
foreign sessions. Run Block A from the final clone: inventory bytes at H,
clean lock/tree, fresh staging/night/probe roots, successor draft, full
build-probes/bind-window/check, generator `--check` and `--emit-chain`,
`validate_plan.py --draft`, canonical `write_night_plan`, then twin-only
plist rendering and inspection. Preserve `block A rc=0` only on actual
success. No discoverable plan, bracket reservation or capture is started.

### 8. Step 3b

Repeat the own-background stop with actual task-control results; classify
the daemon/spare/pty/resume census by ancestry. Do not invent task IDs,
ignore multiline output, or claim another activation is own. Finish Block B,
record/push and exit in this same turn.

### 9. Runbook 68 Block B: email then arm

Start by 06:05, inside the 09-11 03:00–06:30 install span. Record machine,
power, thermal/load, clock, screensaver and timer observations; the stub's
powermode exemption does not apply. Resolve any unmet production admission
prerequisite. Recheck Ed's available NO relay and owner directive issues.

Send the consolidated notice **after H and stub retirement, before plan
publication**. Record the actual accepted Gmail message/thread IDs/time and
NO-channel limitation in staging and the arm record. Close item 4 here.
The notice includes all pins and the first real date, 09-12 02:56 PDT /
09:56 UTC, 12,600-second budget, 06:31 courier deadline and 02:31 exit
boundary; launch requires no Ed hand unless he replies NO. No invented
24-hour or fixed minimum notice delay applies.

Final byte/device/time/census checks immediately precede `os.replace` into
`NIGHT_ROOT/night_plan.json` and installer invocation FROM the final clone.
Inspect both installed labels/calendars/argv, finish before 06:30, preserve
baseline `night/` listing, and require actual `block B rc=0`. On failure,
use runbook 68's attempt-local uninstall/preserve/unpublish recovery; do not
leave an unsuccessful half-published arm or remove a loaded checkout.

### 10. Record, push and exit

Execute runbook 68 step 8 with the activation's allocated record/evidence
paths in its authorized linked worktree. Record actual activation/PID,
H/handback, all timing, send evidence, census/ancestry/task stops, readiness,
plan/chain/plists, power/timer and initial inventory. Push the bookkeeping
record; verify remote SHA and report a failed push honestly.

The durable pointer and next relaunch prompt must retain exactly
(`d117-g2a-prefill-probe-20260912`,
`/Users/edr/JouleWise-measurement-v5-20260911-g2a`, H) until completion.
Exit with no own background tasks, preferably by 06:30 on 09-11 and
absolutely before **02:31 on 09-12**. Do not wait resident for acquisition.
The next harvest cannot start at 03:30 just because the fixed belt ends:
the new plan's closed completion boundary is 06:31, and missing delivery
or running/indeterminate recorded processes can extend the hold.

## What can go wrong and what to do

| Condition | Required response |
|---|---|
| Rehearsal receipt `night_refused_agent_present` | Preserve exact census/refusal. Item 5 may close only with passing dead-man evidence; item 6 stays open. Do not arm G2-a; obtain a fresh compliant stub/lead disposition. Never count agent-present refusal as quietness. |
| Any other rehearsal refusal | Preserve result/receipt/refusal, cure the cause before re-arming, and do not repeat the same plan/signature. A launchd exit 3 by itself is not a refusal. Diagnostic arm remains blocked. |
| Dead-man wrote anything into `night/`, including launchd stream files, or evidence cannot exclude that | Record the exact names/sizes/mtime_ns and log ordering against baseline `[]`. Item 5 is not met under its literal criterion; escalate to the magistrate/owning authority. Do not redefine “only a log line” or exempt stream files locally. |
| Ed NO on notice thread or owner-authored directive issue | Before arm, stop/redirect as instructed and preserve notice evidence. Record inability to read a thread honestly and use the available relay. A directive can override full-chain choice until arm. After arm, issues and watchdog stop refs are not night kill switches: use the governed notice-thread stand-down/recovery path; do not promise unseen polling. |
| Canonical checkout still fenced (expected) | No Git operation in `/Users/edr/code/JouleWise`; use linked worktrees and GitHub fresh clone. Only the ruled ledger file read is part of this recipe. Do not move any active frozen checkout. |
| Gate-repair PR merged and reviewed | Verify repair ancestry in the new main handback/inventory commit H, cut at H, repeat readiness, then arm only after the other gates pass. |
| Gate-repair PR not merged | Magistrate rule from the brief: R1 environment admission is on the member-acceptance path; prefer waiting one day over arming without it. Do **not** arm at the pre-repair head. Prepare the 09-13 notice/coordinates and wait for merge/review; consumption also awaits full `GATE-SENSIBILITY-SWEEP-01` closure. |
| Claude usage exhaustion mid-activation | The weekly 16:00 PDT 09-10 reset has already passed; it is not proof of remaining capacity or courier readiness. Preserve progress/actual failure. Before publication leave only nondiscoverable staging. After publication inspect installed state on the next safe activation; recover a failed partial arm from the pinned clone before any new plan. If fully armed, preserve its frozen triple and exit; never move it or relaunch through a fence. Watchdog usage backoff does not excuse a missed 06:05/06:30 cutoff. |
| Missing inbox proof, missing remote results branch, incomplete process clearance | Keep acceptance/cleanup pending as appropriate; a send marker, local result or chain-exit expectation cannot replace the missing evidence. Preserve and escalate, do not delete. |
| H changes, inventory bytes differ, clone is dirty, or ledger/model/lock check fails | Stop before publication; repair/review in the owning lane, re-cut/revalidate at the correct H as needed. Never refresh the pinned clone after authoring or reset ledger history. |
| 06:05 last-start or 06:30 installation deadline missed | No new arm. Preserve staging and author the 09-13 notice after coordinate/head review. If already published but unsuccessful, use attempt-local recovery; report actual surviving state. |

## Draft verification

The drafting session inspected the inventory reader/test and ran
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_rehearse_t0_unattended -q`:
8 tests, OK. The proposed row is compatible in principle; it was not applied.
File 12 records the executed Python epoch command and exact outputs. All
harvest, H, clone, validation, notice, installation and recording steps above
remain future, lead-owned work. This draft closes no live acceptance gate.
