```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "W1 uses the existing v2 derivation route, but the seal is not on main and several W1 arm inputs remain unverified.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "c6814dd891db361156c45434490342a3e1dd9da3",
    "head_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "upstream_end": "c6814dd891db361156c45434490342a3e1dd9da3",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Revision 5 seal on main", "action": "wait_for"},
      {"row": "W1 desk inputs and custody directory", "action": "wait_for"},
      {"row": "W1 email, publication and install", "action": "do_not_start"},
      {"row": "PR-L follow-up nits", "action": "start_now"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "HEAD \\(no branch\\)"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --stat main...feat/2026-09-25-rev5-seal",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["2 files changed, 25 insertions(+), 2 deletions(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "2 files changed"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "test -d /Users/edr/night-custody/measurement",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "verification_gap", "level": "blocking", "text": "The Revision 5 seal is on feat/2026-09-25-rev5-seal, not main at inspected HEAD.", "needs": "Merge and review the seal, then select H."},
    {"id": "F2", "kind": "verification_gap", "level": "blocking", "text": "W1 t0, registered evidence-root ID, selected frozen calibration-plan source and arm notice acceptance were not established.", "needs": "Lead supplies and records these before authoring and publication."},
    {"id": "F3", "kind": "environment", "level": "blocking", "text": "/Users/edr/night-custody/measurement does not currently exist.", "needs": "Create it before authoring the W1 clone."},
    {"id": "F4", "kind": "residual_risk", "level": "nonblocking", "text": "The runbook still describes equivalence-night branches and its old clone path; PR-L final pass lists post-merge nits.", "needs": "Use the Revision 5 ruling and record the runbook deviations."}
  ]
}
```

## Scheduling matrix

| Row | Action | Wait for | Collision surface |
|---|---|---|---|
| Q1 — W1 identity | **W1 is derivation window one**, with a `joulewise.night_plan.v2` / version 2 `NightPlan`, `receipt_class="DIAGNOSTIC_NO_PACK"`, and a `derivation` ledger session. It runs `scripts/gen_derivation_night.py`’s per-night `chain.zsh` wrapper, which authenticates and executes `scripts/night_chains/calibration_derivation_only.zsh`. The driver invokes the wrapper as `/bin/zsh <chain_path>`. Twelve slots use a 600 s settle, 600 s start-to-start pitch and 480 s final capture budget: 7,680 s programmed, 7,980 s generator minimum, **9,000 s plan window**. The old 03:00–06:30 “210 min install span” is historical; the current configured span is local **00:00–24:00**, with install complete strictly before `t0−10 min`. [Revision 5:610–614](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L610), [plan schema and fields:33–44, 359–373](joulewise/night_gate.py#L359), [generator:74–96, 516–537](scripts/gen_derivation_night.py#L516), [wrapper and driver:925–985](docs/phase_2/derivation_night_runbook.md#L925), [schedule:1563–1584, 1628–1640](docs/phase_2/derivation_night_runbook.md#L1563). | Seal on main and W1 coordinates. | The `night_kinds["calibration"]` row has no plan prefix, protocol path, receipt class, window or generator; the evidence façade cannot author this W1. [night_kinds.py:71–92](joulewise/night_kinds.py#L71) |
| Q2 — runbook §0.1–0.4 | **(b) §0.1:** H must include merged PR-L, PR-R **and the sealed Revision 5**, not just the older lane and handback. **(b) §0.2:** change `MEASUREMENT_ROOT` to `/Users/edr/night-custody/measurement/JouleWise-measurement-${NIGHT_DATE}-derivation-${WINDOW_ID}` and first run `mkdir -p /Users/edr/night-custody/measurement`. Keep the fresh GitHub clone, detached H, locked venv and byte-exact ledger restoration. **(a) §0.3:** run both `check` commands; rc 3 is expected only with the explained old-acceptance mismatch, while the preregistered sampler line must say `match`. **(a) §0.4:** authenticate the copied ledger and head-equals-pin. [runbook:271–329, 435–542](docs/phase_2/derivation_night_runbook.md#L271), [R16:82](docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md#L82), [custody precondition:67](docs/process_traces/2026-09-25-activation-152c9255/24-finalpass-packet-prl/20-fable-final-pass-prl.md#L67). | New H. | Old clone path fails R16. |
| Q2 — runbook §0.5–0.8 | **(b) §0.5:** require the *sealed* Revision 5 bytes and pin their SHA-256 in the arm notice; the old V3/equivalence explanation at lines 615–624 is obsolete **(c)**. **(a) §0.6:** agent-free census, including `"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"` and the final repeat. **(a) §0.7:** no active/unknown sibling, loaded agent, standing NO or stop. **(a) §0.8:** clean clone and fresh `write_derivation_night_inputs.py` outputs; use r7 as the operative predecessor where Revision 5 amends r6 references. Also record display state, powerd assertions and brightness, and quit Wispr Flow at arm under R7 **(b)**. [runbook:544–697, 699–888](docs/phase_2/derivation_night_runbook.md#L544), [Revision 5:602–612](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L602), [R7:73](docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md#L73). | Desk inputs and clean census. | §0.8’s frozen-plan source and §0.2’s evidence ID have no W1 literal in the runbook. |
| Q2 — runbook §1.1–1.3 | **(a) §1.1, §1.1a, §1.1b:** v2 plan, staged authoring, wrapper generation, byte re-derivation and `zsh -n` remain. **(a) §1.2:** 9,000 s remains; the v4 quiet-admission authoring paragraphs are **(c)** for W1. **(b) §1.3:** keep `schedule --plan`, all-day configured install span and `t0−10 min` close; delete the “distinct calendar days” FAIL-route claim. W2 uses ≥6 elapsed hours. [runbook:892–923, 1024–1175, 1184–1240, 1563–1640](docs/phase_2/derivation_night_runbook.md#L892), [Revision 5:610–614](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L610). | Authored plan. | A v4 bind policy or old calendar-day rule would change the registered experiment. |
| Q2 — runbook §1.4–1.5 | **(b) §1.4:** retain email → publication → `scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe` → ordinary install; explicitly inspect the v2 probe receipt’s 300-frame cadence, ≤55 s, median ≤150 ms, max ≤200 ms and three `Interactive` rendered labels. The runbook’s publication block places the probe after publication; its short illustrative probe command at 2085–2087 uses `$PLAN`, not `$STAGED_PLAN`. **(a) §1.4a:** same-candidate retry and fresh notice rules remain. **(b) §1.5:** record Revision 5, PR-L commit, both template digests, rendered-plist digests, probe receipt and R16 clone prefix; PASS/FAIL-equivalence and three-night evidence rows are **(c)**. [runbook:1817–1842, 1980–2043, 2067–2088, 2248–2305, 2351–2410](docs/phase_2/derivation_night_runbook.md#L1817), [R2/R6/R15:68–72, 81](docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md#L68). | Accepted notice, then published plan. | Publication is the irreversible discovery boundary. |
| Q3 — gaps on inspected main | **Blocking:** sealed Revision 5 is only on `feat/2026-09-25-rev5-seal`; main’s text still has three launch-context placeholders. The custody measurement directory is absent locally. W1’s actual `t0`, W1-specific evidence-root ID and chosen frozen `calibration_plan.json` are **UNVERIFIED**. The canonical ledger exists locally, but its current head-equals-pin and custody authentication were **UNVERIFIED** because this scout did not perform arm checks. R16-a text exists in the PR-L final pass, but I could not find it installed alongside R16 in the acceptance ruling; that final pass explicitly asks for this before the W1 notice. **Nonblocking:** PR-L nits 2–6, including retention of raw probe frames, were expressly deferred past W1. Code, Interactive templates, v3 protocol file, disposition registry, cadence-report script and the v2 plan writer are present. [Revision 5:600–608](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L600), [runbook inputs:379–415](docs/phase_2/derivation_night_runbook.md#L379), [R16-a/final-pass condition:40–42, 63–74](docs/process_traces/2026-09-25-activation-152c9255/24-finalpass-packet-prl/20-fable-final-pass-prl.md#L40), [cadence script:1–12](scripts/calibration_cadence_report.py#L1). | Seal merge, input selection, custody creation and R16-a disposition. | No W1 arm is presently reviewable as a fully specified plan. |

The exact writer API is `write_night_plan(path: str | os.PathLike[str], plan: NightPlan) -> Path`. Its W1 call is `write_night_plan(STAGED_PLAN, NightPlan(...))`; the writer supplies `schema="joulewise.night_plan.v2"` and `schema_version=2` when it serializes the packless, non-quiet plan. [night_plan_writer.py:18–50](joulewise/night_plan_writer.py#L18). The full `NightPlan` argument mapping is:

```python
NightPlan(
    plan_id=PLAN_ID,                         # W1 fresh ID; runbook §0.2
    receipt_class="DIAGNOSTIC_NO_PACK",     # runbook §1.1 / generator default route
    t0_epoch_s=W1_T0_EPOCH_S,               # chosen future, minute-aligned start: UNVERIFIED
    window_max_s=9000,                      # runbook §1.2
    authored_epoch_s=int(time.time()),     # authoring clock, within 36 h
    repo_head=H,                            # reviewed post-seal main commit
    measurement_root=MEASUREMENT_ROOT,      # R16 custody child
    measurement_head=H,                     # same reviewed commit
    chain_path=NIGHT_ROOT + "/chain.zsh",   # generated wrapper
    chain_sha256_path=NIGHT_ROOT + "/chain.zsh.sha256",
    custody_root=NIGHT_ROOT,
    registration_path=D166_REGISTRATION_PATH,
    pack_night=None,                        # code default
    quiet_admission=None,                   # code default
)
```

The schema, required fields and optional defaults are in [night_gate.py:359–373](joulewise/night_gate.py#L359); the plan values and D166 path are in [runbook §1.1:892–923](docs/phase_2/derivation_night_runbook.md#L892). `EVIDENCE_ROOT_ID` and the frozen calibration-plan source are **wrapper-generator inputs**, not `NightPlan` fields; the generator requires them and has no default for either. [gen_derivation_night.py:844–898](scripts/gen_derivation_night.py#L844).

## Critical path

**Q4 — ordered W1 arm checklist.** The following is a command template for the lead’s later foreground arm session. Its three positional inputs are deliberately unresolved: `$1` is the minute-aligned W1 `t0` epoch, `$2` is the registered W1 evidence-root ID, and `$3` is the reviewed repository-relative frozen calibration-plan path. Supplying them from an actual arm record is required; the prior night’s `evidence-$PLAN_ID` convention and plan choice do not establish W1’s values. The seal merge and whole-suite review are prerequisites, not actions this scout performed. [runbook:379–415, 1024–1096](docs/phase_2/derivation_night_runbook.md#L379), [prior arm example:22–48](docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/step2-desk.zsh#L22).

```zsh
# Run only after the seal is merged and the reviewed H is green.
set -euo pipefail
export TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
export W1_T0_EPOCH_S="$1" EVIDENCE_ROOT_ID="$2" FROZEN_PLAN_REL="$3"
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
git fetch origin main
export H="$(git rev-parse origin/main)"
git merge-base --is-ancestor a47d6c06df6489a52bc2547589a46c2cae3ffc97 "$H"
export NIGHT_DATE="$(date -r "$W1_T0_EPOCH_S" +%Y%m%d)"
export WINDOW_ID=w1-a
export PLAN_ID="d079-epoch-25g83-derivation-$WINDOW_ID-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID"
export MEASUREMENT_ROOT="/Users/edr/night-custody/measurement/JouleWise-measurement-$NIGHT_DATE-derivation-$WINDOW_ID"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export PLAN="$NIGHT_ROOT/night_plan.json"
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export ARM_ATTEMPT=1 ATTEMPT_DIR="$STAGE/arm-attempts/000001"
test $((W1_T0_EPOCH_S % 60)) -eq 0
test ! -e "$MEASUREMENT_ROOT"; test ! -L "$MEASUREMENT_ROOT"
test ! -e "$NIGHT_ROOT"; test ! -L "$NIGHT_ROOT"
test ! -e "$STAGE"; test ! -L "$STAGE"
mkdir -p /Users/edr/night-custody/measurement "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
cd "$MEASUREMENT_ROOT"
python3.13 -m venv .venv
"$PY" -m pip install -q -c env/mac-measurement-lock.txt -e ".[mac]"
"$PY" -m pip install -q -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) <("$PY" -m pip freeze --exclude-editable | sort)
mkdir -p runs
rsync -a --checksum "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
cmp "$LEDGER_SOURCE" "$CALIBRATION_LEDGER"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
shasum -a 256 configs/calibration/preregistration_d079_epoch_25g83_rev1.md
shasum -a 256 configs/calibration/powermetrics_fiducial/protocol_v3.json
git show 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87:configs/launchd/com.joulewise.night.plist.template | shasum -a 256
git show 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87:configs/launchd/com.joulewise.night-probe.plist.template | shasum -a 256
"$PY" scripts/issue_calibration_acceptance_generation.py check
"$PY" scripts/issue_calibration_acceptance_generation.py check --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"
cp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
cmp "$FROZEN_PLAN_REL" "$CALIBRATION_PLAN"
```

The two `check` invocations above normally return **3** for the explained stale predecessor; they need separate captured return codes and review of every printed field before proceeding. A plain `set -e` shell would stop at rc 3, so the lead must run that pair under the runbook’s controlled `set +e`/`set -e` pattern and inspect the output, not treat every rc 3 as permission. Ledger authentication and head-equals-pin must also be performed as in the prior arm’s [step1-clone.zsh:21–45](docs/process_traces/2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/step1-clone.zsh#L21). The seal digest on the branch inspected here is `497847c4adcae3d8a9bfef99148c602579cca2b4adec1893c1980e7b366fd191`; it must be re-read **inside H**. The PR-L template digests inspected were `e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8` and `1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd`. [Revision 5 sealing rule:608](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L608).

Then author and verify the staged plan, census, schedule and render. This is the exact v2 writer route, with W1’s new root:

```zsh
"$PY" -B - <<'PY'
import os, time
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH
from joulewise.night_plan_writer import write_night_plan
e = os.environ
p = NightPlan(
    plan_id=e["PLAN_ID"], receipt_class="DIAGNOSTIC_NO_PACK",
    t0_epoch_s=int(e["W1_T0_EPOCH_S"]), window_max_s=9000,
    authored_epoch_s=int(time.time()), repo_head=e["H"],
    measurement_root=e["MEASUREMENT_ROOT"], measurement_head=e["H"],
    chain_path=e["NIGHT_ROOT"] + "/chain.zsh",
    chain_sha256_path=e["NIGHT_ROOT"] + "/chain.zsh.sha256",
    custody_root=e["NIGHT_ROOT"], registration_path=D166_REGISTRATION_PATH)
write_night_plan(e["STAGED_PLAN"], p)
PY
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json"
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" --verify
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN"
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" \
  --plan "$STAGED_PLAN" --python "$PY"
```

Before publication, create attempt `000001`, preserve the exact plan bytes and send **one accepted NIGHT_HANDBACK notice** through the authorized mail tool. Its body must include: W1/Revision 5 explanation from R14; `PLAN_ID`, `DIAGNOSTIC_NO_PACK`, attempt 1 and plan SHA-256; full H as repository and measurement head; clone, custody and runs roots; local/UTC `t0`, 9,000 s window, courier completion, dead-man and `t0−8 min` exit; notice acceptance/open, `t0−10 min` exclusive install close and listed install span; sealed registration and protocol-v3 digests; PR-L commit and both template digests; wrapper, tracked chain, frozen plan and both desk-input paths/digests; the `Interactive` render evidence; “reply NO to stop.” Record actual accepted time, message ID, thread ID and all observable NO/directive channels. [runbook:1817–1842, 2008–2040](docs/phase_2/derivation_night_runbook.md#L1817), [R14–R15:80–81](docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md#L80). **Sending the notice is an external act.** No message was sent by this scout.

Only after accepted notice and a fresh clear veto/census observation, execute the runbook’s `retry_allowed` publication check, then its `os.replace(STAGED_PLAN, PLAN)` boundary. The next exact commands are:

```zsh
# Publication is irreversible for this arm attempt.
# First run §1.4's retry_allowed check with the accepted notice.json
# and the saved ATTEMPT_DIR/plan.json; then atomically publish.
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"
"$PY" -B - <<'PY'
import os
from pathlib import Path
source = Path(os.environ["STAGED_PLAN"])
target = Path(os.environ["PLAN"])
assert not target.exists() and not target.is_symlink()
os.replace(source, target)
PY
# The temporary probe uses launchd and the real 300-frame sampler.
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
r = json.loads((Path(os.environ["NIGHT_ROOT"]) / "night_probe_receipt.json").read_text())
c = r["cadence"]
assert r["schema"] == "joulewise.night_probe_receipt.v2"
assert r["outcome"] == "ok" and r["ProcessType"] == "Interactive"
assert c["count"] == 300 and c["elapsed_s"] <= 55
assert c["median_ms"] <= 150 and c["max_ms"] <= 200
assert all(x["ProcessType"] == "Interactive" for x in r["launch_context"].values())
print(c)
PY
# Installation is an irreversible launchd mutation for this attempt.
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
launchctl list | grep joulewise
plutil -p "$HOME/Library/LaunchAgents/com.joulewise.night.plist"
plutil -p "$HOME/Library/LaunchAgents/com.joulewise.night.deadman.plist"
```

That publication excerpt is **not a substitute for the runbook’s notice and `retry_allowed` check**: without actual accepted IDs and observed veto state, inserting invented `notice.json` values would violate the arm procedure. The runbook’s complete pre-publication assertions, rendered-agent comparison and installed-calendar inspection are at [§1.4:2192–2305](docs/phase_2/derivation_night_runbook.md#L2192). The probe pass thresholds are enforced by code at [run_night.py:3712–3774](scripts/run_night.py#L3712) and [night_agent_install.py:827–877](joulewise/night_agent_install.py#L827). **No installer, launchctl or powermetrics command was run in this scout.**

**Q5 — harvest and W2.** Harvest W1’s terminal result, courier, custody and ledger exactly as §2 requires; preserve the raw plists and uninstall both agents from W1’s clone before another arm. Then run `"$PY" -B scripts/calibration_cadence_report.py --window "W1=$NIGHT_ROOT/runs/instrument_validation"` before reading any B value; `median_of_capture_medians_ms > 150` stops W2. Next run the count-only session dry run; fewer than 6 valid of 12 also stops W2. The old §2.5 equivalence PASS/FAIL/INCONCLUSIVE calculation is obsolete. If both stops clear, review and commit W1’s terminal pin candidate, make W2’s fresh plan, clone, session and notice, and schedule W2 at least **6 elapsed hours** after W1; distinct calendar dates are no longer required. After W2, a third window is allowed only on a count-only result below 12 valid. [Revision 5:610–614](configs/calibration/preregistration_d079_epoch_25g83_rev1.md#L610), [cadence report:33–79](scripts/calibration_cadence_report.py#L33), [runbook harvest and old route:2469–2515, 2804–2840](docs/phase_2/derivation_night_runbook.md#L2469).