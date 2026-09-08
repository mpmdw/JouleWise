```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: G2-a is the first real window, but its emitted chain still targets the protected August checkout; unattended pack-bound nights additionally require unimplemented D-169 stage 3.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "head_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "upstream_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "Desk audits, fixture rehearsals, chain-generation and paper-artifact crosswalk",
        "action": "start_now"
      },
      {
        "row": "Select replacement measurement root, interpreter and reviewed acquisition head; retarget generated chain and preflight",
        "action": "needs_ruling"
      },
      {
        "row": "Prepare real G2-a probe inputs",
        "action": "start_now",
        "condition": "Isolated authorized desk estate; production binding waits for the replacement checkout and authenticated ledger."
      },
      {
        "row": "Harvest rehearsal-20260909, verify courier and stand-down, uninstall its night agents and retire stub roots",
        "action": "wait_for",
        "dependency": "Actual rehearsal completion and lead acceptance"
      },
      {
        "row": "Arm and collect DIAGNOSTIC_NO_PACK G2-a",
        "action": "wait_for",
        "dependency": "Rehearsal acceptance, corrected checkout binding, live prerequisites and email-then-arm handback"
      },
      {
        "row": "Issue G2-a selection/prompt pin, generate and freeze all three production packs, repeat clone proof",
        "action": "wait_for",
        "dependency": "Authenticated G2-a corpus and reviewed terminal ledger-pin advancement"
      },
      {
        "row": "Schedule D-169 stage-3 implementation and T0 rehearsal closure",
        "action": "needs_ruling",
        "dependency": "Owning unattended-lane staged ruling; implementation currently remains blocked behind NIGHT-REHEARSAL-01"
      },
      {
        "row": "Collect G2-b, ratify L10-A and transaction GO",
        "action": "wait_for",
        "dependency": "Real-pack estate proof and implemented unattended pack-bound launch"
      },
      {
        "row": "Collect ALPHA, then BETA, with G3 before each next arm; prove and mint floors before GAMMA",
        "action": "wait_for",
        "dependency": "G2-b, L10-A, launch-realization recheck and magistrate readiness gate"
      },
      {
        "row": "Run measurements from this agent session, move the August checkout, reuse rehearsal roots, or arm TRANSACTION_PACK on current code",
        "action": "do_not_start"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS generated Phase D matches pinned runbook bytes"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The requested immutable August checkout conflicts with the generated G2-a chain and preflight, which still require that exact checkout and the development interpreter.",
      "needs": "Name the replacement measurement root and interpreter, authorize the owning source changes, and select the reviewed head after those changes land."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "TRANSACTION_PACK explicitly refuses night_refused_class_unbuilt; no existing command completes the requested unattended pack-bound arm path.",
      "needs": "Complete and verify D-169 stage 3, including the GO-receipt consumer and T0 rehearsal obligations, before G2-b or campaign night installation."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No generated plan_tree.json exists for any of the three production v5 packs at the inspected head; authenticated G2-a selection, production custody and same-head proofs remain prerequisites.",
      "needs": "Collect G2-a, issue its pin, generate and authenticate the complete estate, and complete G2-b/L10-A before claim collection."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Committed NIGHT_HANDBACK and kernel status lag the supplied live-watchdog/rehearsal facts; several runbook authority and supply statements are also stale.",
      "needs": "Lead reconciles the harvested operational evidence and successor runbook without rewriting historical evidence."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only source inspection and in-memory chain rendering were performed; no live measurements, privileged probes, installers or full suite were run.",
      "needs": "Lead owns live verification and execution. Commands below are prospective, with unresolved inputs and missing implementations explicitly marked."
    }
  ]
}
```

## Scheduling matrix

**The first real window is G2-a, a non-claim prefill probe night. The first claim-bearing window is ALPHA, several gates later.** A successful stub qualifies scheduling, stand-down and reporting; it supplies neither measurement readiness nor campaign evidence.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| A. Audit chain emission, parser contracts, model/registration pins and fixture paths | start_now | Nothing | Separate desk estate; no live custody writes |
| B. Resolve replacement checkout and interpreter | needs_ruling | Magistrate’s path/routing decision | Generated chain currently redirects execution into the protected checkout |
| C. Prepare probe configurations and inspect ledger supply | start_now | Production binding needs B | Tokenization is desk work; do not change the shared interpreter or ledger |
| D. Accept `rehearsal-20260909`, harvest courier/stand-down evidence | wait_for | Its actual completion | Both night LaunchAgent labels, rehearsal custody, watchdog plan discovery |
| E. Publish reviewed G2-a plan and install both night agents | wait_for | B–D, machine prerequisites, notice email | Installation replaces the same two labels used by rehearsal |
| F. Collect G2-a | wait_for | E and empty production census | Entire Mac; all agent work stops |
| G. Select rung, advance reviewed ledger pin, generate/freeze/prove v5 estate | wait_for | F’s authenticated evidence | Production pack bytes, custody, Git head and model/runtime pins |
| H. Complete unattended pack-bound launch and T-0 qualification | needs_ruling | Owning staged schedule; kernel currently gates work behind D | Launch consumer, rehearsal evaluator, confirmation custody |
| I. G2-b → L10-A → magistrate GO | wait_for | G, H | Separate non-claim roots; actual quiet window |
| J. ALPHA → G3 → BETA → G3 → floor proof/mint → GAMMA | wait_for | I and launch-realization recheck | Claim custody, full-window budgets, frozen publication state |
| K. Comparison-paper suppliers and artifact crosswalk | start_now | Numerical fills wait for authenticated inputs | Separate paper branch; no changes to frozen measurement inputs |
| L. Live collection from an Astra seat; reuse stub or August checkout | do_not_start | Explicitly prohibited | Quiet-Mac fence and immutable evidence |

The September 5 fallback selected methods/diagnostics because G2-a, generated estate, G2-b/G3, authenticated paper suppliers and a feasible schedule were unproved. The old deadline is superseded by Ed’s current instruction; those evidence requirements remain. See `docs/process_traces/2026-09-05-readiness/02-magistrate-ruling-fallback.md:3` and `01-astra-readiness-assessment.md`, scheduling matrix R1–R10.

**Observed snapshot:** clean detached `e4ce8b3b`; local `origin/main` equals it. The protected measurement checkout remains `eeb4e133815d0c12486d597d9434a2c18c83c1c4`. No files were modified.

## Critical path

### 1. Resolve the checkout mismatch before producing a real plan

**NEEDS_RULING**

- **Question:** Which fresh measurement root and interpreter replace the August coordinates in the generated G2-a chain and its preflight?
- **Options considered:** advance the old checkout; point only the v2 plan at a fresh checkout; retarget the owning generated-chain/preflight sources and use a fresh checkout.
- **Recommendation:** the third option. Preserve `/Users/edr/JouleWise-measurement-20260813` unchanged. Use a newly named measurement checkout under `/Users/edr/`, outside every rehearsal `/private/tmp/...` root.
- **Blocked work:** a trustworthy real G2-a plan, and therefore every downstream production pack and claim window.

This is an execution mismatch, not merely stale prose:

- `scripts/gen_g2_phase_d.py:130` copies the fixed-variable block unchanged and substitutes only the G2-a date.
- That block sets the **old measurement root** and `/Users/edr/code/JouleWise/.venv/bin/python`: `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:253`.
- `preflight.sh:40` independently requires those exact coordinates.
- In-memory rendering for `20260910` confirmed both old literals survive. Exporting replacement variables before invoking the chain does **not** fix this: the chain overwrites them.

The lead should name:

```text
MEASUREMENT_ROOT=/Users/edr/JouleWise-measurement-v5-g2a-<date>-<head-prefix>
MEASUREMENT_HEAD=<full reviewed main commit AFTER routing corrections>
MEASUREMENT_PY=<reviewed, locked interpreter>
```

`e4ce8b3bece33db40de68b6c407a514fbaed9a26` is the inspected **desk baseline**, not a cleared acquisition head.

A fresh detached checkout is suitable for G2-a after the routing correction. For the later pack ceremony, detachment alone is insufficient: `reviewed_main()` requires a clean tree and `HEAD == refs/heads/main == refs/remotes/origin/main` (`joulewise/arm_readiness.py:5229`). Prefer an independent clone for the production estate, so development worktree branch movement does not silently change its local `main` reference.

After the lead names the root/head, the mechanical creation sequence is:

```sh
git clone --no-hardlinks /Users/edr/code/JouleWise "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$MEASUREMENT_HEAD"
git -C "$MEASUREMENT_ROOT" rev-parse HEAD
git -C "$MEASUREMENT_ROOT" status --porcelain=v1
```

The local-clone origin is only a transport source. The lead must configure and verify the intended publication remote before any reviewed-main/publication ceremony. Do not manufacture equality by pointing at a convenient unrelated ref.

**Owner:** magistrate/implementation seat for checkout creation, dependency locking, exact model verification and authenticated physical-ledger provisioning. **Ed-hands:** any missing privileged installation and physical machine state. D-171 delegates transaction GO, E-10 invocation and step-6 confirmation to automation; an additional per-window Ed GO is not owed (`docs/decision_log.md:10630`). The current instruction overrides D-171’s older permission to advance the August checkout.

### 2. Desk work that can start now

These are proposed commands for separately authorized scratch estates; this scout executed none of their writes.

**Chain preparation and static checks**

```sh
python3 -B scripts/gen_g2_phase_d.py --check

python3 -B scripts/gen_g2_phase_d.py \
  --emit-chain "$SCRATCH/chain.zsh" \
  --night-date "$NIGHT_DATE"

/bin/zsh -n "$SCRATCH/chain.zsh"
```

Produces an executable chain and `chain.zsh.sha256`. The current output is useful for the routing audit, **not for real installation**. The emitter’s sidecar and source-block contract are at `scripts/gen_g2_phase_d.py:116` and `:147`.

**Probe generation**

With `REPO` and `PY` bound to the isolated reviewed desk environment:

```sh
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" build-probes \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --small-members 5 --large-members 1
```

Produces the four-rung probe configurations, manifests, prompt ladder and input inventory. It performs model/tokenizer-dependent preparation, not a powermetrics capture. Production inputs must ultimately be authenticated in the chosen execution environment.

Once the actual ledger/root/head are settled:

```sh
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" bind-window \
  --root "$G2A_ROOT" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY" --power-policy "$POWER_POLICY" \
  --window-id "$G2A_WINDOW_ID" --session-id "$G2A_BRACKET_SESSION_ID" \
  --evidence-root-id "$G2A_EVIDENCE_ROOT_ID"

PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" check \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY"
```

Produces/authenticates the calibration plan, identity epoch, T1 bindings and bound input inventory. Exact recipe: `SHAKEDOWN-G2-RUNSHEET.md:373`; generated pre-collection check: `:500`.

**Readiness rehearsals**

Safe desk work includes fixture-backed checks of:

```sh
python3 -B -m unittest \
  tests.test_gen_g2_phase_d \
  tests.test_generate_g2a_probe_inputs \
  tests.test_arm_readiness_evidence_author \
  tests.test_arm_readiness_evidence_t0 \
  tests.test_capture_t0_step
```

Run in a disposable estate after inspecting each test’s external effects. No fixture receipt enters real custody.

Neither evidence-author CLI has a `--dry-run` option. The freeze author writes inside its pack and requires its own CLI repository to own that pack (`scripts/author_arm_readiness_evidence.py:41`). Therefore “authoring dry run” means a sacrificial committed estate with separate custody—not invoking the author against production and hoping it is observational.

A one-shot informational screen is possible:

```sh
bash scripts/prewindow_check.sh --window alpha
```

It should block while agents are present. It neither establishes T-0 evidence nor substitutes for the night gate. Do not run its 45-minute wait during desk work. It checks the checkout containing the script, not an arbitrary `REPO` export (`scripts/prewindow_check.sh:32`, `:147`, `:171`).

**Collision limits:** no installation/uninstallation, no sibling real-looking plan under `~/night-custody`, no live ledger reservation, no shared-venv relock, and no canonical/watchdog checkout movement while the rehearsal remains armed. All seats must exit before its fence; the watchdog does not own arbitrary peer sessions.

### 3. Accept the rehearsal, then retire its active scheduling state

The supplied `rehearsal-20260909` facts are newer than committed `NIGHT_HANDBACK.md`, which still describes September 3 (`:28`). Harvest the actual September 9 record:

```sh
python3 -B -m json.tool \
  /Users/edr/night-custody/rehearsal-20260909/night/result.json

python3 -B -m json.tool \
  /Users/edr/night-custody/rehearsal-20260909/night/receipt.json
```

The lead must verify:

- launchd-started driver, `REHEARSAL_ONLY`, successful stub chain;
- results branch and delivered **night-driver courier** message ID;
- applicable pre-night dead-man stand-down observation;
- watchdog stand-down evidence and empty production census.

A stub can run despite a gate refusal because the driver deliberately substitutes its built-in chain (`scripts/run_night.py:1169`). Thus `REHEARSAL_ONLY` alone does not prove quietness. The historical allowance for `night_refused_agent_present` cannot substitute for the watchdog’s required clean stand-down proof.

After completion and harvest, uninstall from the recorded installing checkout:

```sh
scripts/install_night_agent.sh \
  --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json \
  --hour 2 --minute 56 --uninstall
```

Uninstall does not require matching HEAD pins (`scripts/install_night_agent.sh:43`, `:170`).

Then the magistrate inventories **all** `REHEARSAL_STUB` roots and preserves them in an archive outside the watchdog’s one-level plan discovery. Do not delete their evidence. The exact move list must come from that inventory; this scout has not inspected live custody. Every stub root must leave the active discovery set before a real arm (`docs/process/MAGISTRATE_WATCHDOG.md:258`).

### 4. Author and install the first real G2-a v2 plan

**D-169 stage 2.** G2-a uses `DIAGNOSTIC_NO_PACK`: C2 is `NOT_APPLICABLE` with `no_pack_by_design`. It needs no production pack freeze, arm receipt or step-6 table. G2-b is expressly excluded from this class (`MAGISTRATE-RULING-UNATTENDED-STAGE1.md:95`, `:178`, `:217`).

Before publishing the plan, the lead must pin:

| Pin | Required value |
|---|---|
| Schema | `joulewise.night_plan.v2` and integer `schema_version: 2`, emitted by the canonical writer |
| Identity | Fresh `plan_id`; `receipt_class=DIAGNOSTIC_NO_PACK` |
| Time | Exact local date/time, timezone-derived epoch, positive integer `window_max_s`, truthful authorship time |
| Execution | Absolute real `measurement_root`, full `measurement_head`, driver `repo_head` |
| Chain | Reviewed absolute chain path and SHA-256 sidecar path; all embedded roots/interpreter agree |
| Custody | Fresh root, distinct from rehearsal, G2-b and claim custody |
| Registration | Exact current D-166 registration path/bytes |
| External inputs | Exact model revisions, environment lock, authenticated ledger and head pin, policy, probe inventory and calibration plan |

The schema accepts an exact key set; do not add convenience fields to the plan (`joulewise/night_gate.py:183`). Keep additional review metadata in the lead’s separate run card.

The current registration digest was independently checked:

```text
dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
```

It supersedes the old `1c0a4a11…` digest still printed in the original stage ruling (`joulewise/night_gate.py:28`).

After the corrected chain and its inputs pass review, the plan-writing command is:

```sh
cd "$MEASUREMENT_ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ["MEASUREMENT_ROOT"]).resolve(strict=True)
head = subprocess.check_output(
    ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
).strip()
assert head == os.environ["MEASUREMENT_HEAD"]
t0 = datetime.fromisoformat(os.environ["T0_ISO"])
assert t0.tzinfo is not None
custody = Path(os.environ["NIGHT_ROOT"]).resolve(strict=True)
chain = custody / "chain.zsh"
assert chain.is_file()
assert chain.with_name("chain.zsh.sha256").is_file()
assert not (custody / "night_plan.json").exists()
plan = NightPlan(
    plan_id=os.environ["PLAN_ID"],
    receipt_class="DIAGNOSTIC_NO_PACK",
    t0_epoch_s=t0.timestamp(),
    window_max_s=int(os.environ["WINDOW_MAX_S"]),
    authored_epoch_s=time.time(),
    repo_head=head,
    measurement_root=str(root),
    measurement_head=head,
    chain_path=str(chain),
    chain_sha256_path=str(chain.with_name("chain.zsh.sha256")),
    custody_root=str(custody),
    registration_path=str(root / D166_REGISTRATION_PATH),
)
print(write_night_plan(custody / "night_plan.json", plan))
PY
```

These environment values are **lead-frozen inputs**, not values this scout can invent.

Check the schedule before installation:

```text
t0 + window_max_s + 300 seconds < next 07:00 local
```

Equality refuses (`scripts/run_night.py:1117`). At 02:56, the acquisition budget must be **less than 239 minutes**. G2-a’s 2.5–3-hour estimate fits arithmetically; actual runtime/headroom still needs review (`SHAKEDOWN-G2-RUNSHEET.md:598`).

Render, inspect, send the notice, then install:

```sh
cd "$MEASUREMENT_ROOT"

scripts/install_night_agent.sh \
  --plan "$NIGHT_ROOT/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" \
  --render-only "$RENDER_ROOT"

/usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.plist"
/usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.deadman.plist"

# Magistrate sends and records the reviewed plan email to Ed here.
# Ed's NO cancels the arm.

scripts/install_night_agent.sh \
  --plan "$NIGHT_ROOT/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE"
```

`--render-only` writes files and creates the plan’s `night/` directory; it is not a pure check. Installation pins the driver head, measurement head and resolved courier executable, and uses two global labels (`scripts/install_night_agent.sh:80`, `:119`, `:156`).

**Ed-hands prerequisite:** verify physical power/lid/display/backlight state and any missing privileged configuration. Noninteractive privilege can be inspected without collecting:

```sh
/usr/bin/sudo -n -l /usr/bin/powermetrics
```

A failure goes to Ed for the governed installation; do not substitute a password prompt at night. The lock’s prescribed installation form is `python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"`, under the reviewed Python/environment, not an unpinned dependency refresh (`env/mac-measurement-lock.txt:2`).

### 5. Let launchd collect; agents remain absent

Do **not** manually invoke `run_night.py run` to “test” an armed production plan. It creates once-only records and starts the chain. The installed plist owns:

```sh
python3 scripts/run_night.py run --plan "$NIGHT_ROOT/night_plan.json"
```

This shows the driver entry point, not an additional launch instruction.

The watchdog requests stand-down at `t0−25 min`, TERM by `t0−16 min`, KILL by `t0−15 min`; owned-process absence and an empty census are required. The driver independently requires:

```sh
/usr/bin/pgrep -lf 'codex|claude|t3'
```

Expected: exit **1**, empty stdout. It repeats the census during collection and aborts on a hit. A seat cannot establish its own absence while running. See `MAGISTRATE_WATCHDOG.md:28` and `MAGISTRATE-RULING-UNATTENDED-STAGE1.md:58`.

The emitted G2-a chain performs, in order:

1. Input authentication.
2. Ledger readiness and bracket reservation.
3. Settling and governed pre-calibration with D-079 screen.
4. Small-model probes at 512/1024/2048/4096, five members each.
5. Large-model probes at all four rungs, at least one member each.
6. Governed post-calibration.
7. Recorded finalized/physical-ahead terminal boundary, preserving its pin candidate.
8. Authenticated counts receipt and summary.

The exact generated commands are at `SHAKEDOWN-G2-RUNSHEET.md:387`; the collector is `:486`, reservation `:512`, terminal assertions `:551`, summarizer `:574`. The summarizer produces:

```text
window-plan/d166-prefill-counts-receipt.json
window-plan/d166-prefill-resolvability-summary.json
```

The night driver separately produces `night/receipt.json`, `result.json`, chain markers, census records and courier records. A gate GO alone is insufficient: require successful chain completion **and** the authenticated four-rung summary. Preserve every failed occurrence.

### 6. G2-a → production estate: exact desk commands, gated on real evidence

After terminal-ledger review, the lead advances the pin with the recorded candidate:

```sh
"$PY" scripts/recover_calibration_ledger.py \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  advance-head-pin \
  --session-id "$G2A_BRACKET_SESSION_ID" \
  --expected-sequence "$EXPECTED_SEQUENCE" \
  --expected-digest "$EXPECTED_DIGEST" \
  --operator-identity "$OPERATOR_IDENTITY" \
  --attestation-reason "$ATTESTATION_REASON" \
  --execute
```

The sequence/digest must come from the preserved terminal candidate. This is reviewed desk advancement, never an in-window repair. Commit/review the pin before generating dependent custody (`SHAKEDOWN-G2-RUNSHEET.md:607`).

Then:

```sh
"$PY" scripts/select_g2a_prefill_length.py \
  --summary "$G2A_SUMMARY" --output "$G2A_SELECTION_RECORD"

"$PY" scripts/issue_g2a_prefill_prompt_pin.py \
  --selection-record "$G2A_SELECTION_RECORD" \
  --summary "$G2A_SUMMARY" \
  --prompt-ladder "$G2A_PROMPT_LADDER" \
  --input-inventory "$G2A_INPUT_INVENTORY" \
  --counts-receipt "$G2A_COUNTS_RECEIPT" \
  --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md \
  --output "$G2A_PROMPT_PIN"
```

The selector chooses the shortest qualifying rung; no qualifying rung means the ruled `collect_at_4096` disposition, not invented passing evidence (`SHAKEDOWN-G2-RUNSHEET.md:614`).

Generate all three packs in the authorized production estate:

```sh
"$PY" configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py \
  --output-root "$REPO" --prefill-prompt-pin "$G2A_PROMPT_PIN"

"$PY" configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py \
  --output-root "$REPO" --prefill-prompt-pin "$G2A_PROMPT_PIN"

"$PY" configs/campaigns/d117_contrast_v5/generate_configs.py \
  --output-root "$REPO" \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$G2A_SELECTED_PREFILL_LENGTH" \
  --prefill-prompt-pin "$G2A_PROMPT_PIN"
```

These produce configurations, manifests, plan trees, identities, extraction/analysis specifications and registered custody inputs. Repeat with `--check` using the same arguments.

Both floor generators now exist; the runsheet’s assertion that they do not is stale (`SHAKEDOWN-G2-RUNSHEET.md:675`; floor parser `generate_configs.py:3203`). All three actual `plan_tree.json` files were absent in this snapshot. Production generation cannot start now without the issued G2-a pin.

The pack-freeze sequence must include:

```sh
"$PY" scripts/project_identity_pins.py freeze "$PACK_ROOT"

"$PY" scripts/author_arm_readiness_evidence.py \
  --pack-root "$PACK_ROOT" --measurement-checkout "$REPO"

# Lead performs the governed evidence commit/publication steps.

"$PY" scripts/generate_arm_readiness.py freeze \
  --pack-root "$PACK_ROOT" --measurement-checkout "$REPO" \
  --predecessor-pack-root "$PREDECESSOR_PACK_ROOT"

"$PY" scripts/generate_arm_readiness.py dry-run \
  --pack-root "$PACK_ROOT" \
  --window-custody-root "$DRY_RUN_CUSTODY" \
  --rehearsal-id "$REHEARSAL_ID" \
  --synthetic-root "$SYNTHETIC_ROOT"
```

Repeat for all three packs. The ruled v5 predecessors are the authenticated **v3** packs, not invented v4 predecessors (`scripts/author_arm_readiness_evidence.py:66`). Preserve the returned receipt paths and actual ordinals.

This is not the complete publication ceremony: the lead must re-cut the estate-12 proof, changed-set/attestation stages, publication marker and confirmation table against the actual generated v5 estate. The established order is **build → render confirmation → confirm/hC → publication verify → promote**. A candidate marker or a dry-run PASS cannot replace that ceremony. The current generated estate does not yet supply its exact final heads, paths or confirmation route.

### 7. Stage 3 → G2-b → first claim window

**Hard implementation stop:** `joulewise/night_gate.py:738` returns `night_refused_class_unbuilt` for `TRANSACTION_PACK`. `scripts/launch_window.py:38` has no night-GO-receipt input. Do not invent a flag or label G2-b `DIAGNOSTIC_NO_PACK`.

D-169 stage 3 must deliver the pack-bound GO consumer, refusal/lineage registration and unattended T-0 rehearsal closure. D-171 already supplies the authority delegation; implementation and proof are still owed. The separate launch-realization recheck also gates CLAIM use (`docs/process/state_kernel.json:6170`, `:6328`).

Once those gates are installed, every pack-bound attempt needs a newly frozen 25-key `window.env`, then:

```sh
for step in clock-reference clock-disable quiet-mac-prep prewindow-check ledger-readiness ledger-reservation; do
  "$PY" scripts/capture_t0_step.py "$step" \
    --pack-root "$PACK_ROOT" \
    --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
    --window-plan-root "$WINDOW_PLAN_ROOT" || exit 1
done

ARM_CONTEXT_JSON="$(cat "$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.inputs/arm-context.json")"

"$PY" scripts/author_arm_evidence_t0.py \
  --pack-root "$PACK_ROOT" \
  --custody-root "$ARM_READINESS_CUSTODY_ROOT" || exit 1

"$PY" scripts/generate_arm_readiness.py arm \
  --pack-root "$PACK_ROOT" \
  --arm-context "$ARM_CONTEXT_JSON" \
  --window-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST" \
  > "$ARM_RESULT"
```

**Runsheet correction:** both its rehearsal and consuming sequences omit `author_arm_evidence_t0.py`. The capture tool explicitly returns that as the next step (`scripts/capture_t0_step.py:798`); the main runbook requires it (`window_runbook.md:1108`). Insert it in both sequences before ARM, with ARM the next new process after author exit.

Then obtain the exact returned receipt and verify:

```sh
export ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$ARM_RESULT")"
export LAUNCH_MANIFEST="$ARM_READINESS_CUSTODY_ROOT/$PACK_ID/arm_readiness.t0.inputs/launch-manifest.json"

"$PY" scripts/generate_arm_readiness.py verify \
  --pack-root "$PACK_ROOT" --arm-receipt "$ARM_RECEIPT" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"
```

The existing sole consuming launcher is:

```sh
"$PY" scripts/launch_window.py \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"
```

This command becomes an unattended instruction only after stage 3 installs its authenticated entry path. No standalone consume command is permitted.

T-0 gates are distinct: continuous 600-second clean dwell; the D-170 clock-liveness conjunct at issuance/ARM; applicable 20-minute volatile and six-hour procedural evidence horizons; and a 300-second arm-to-consume budget. Do not treat one duration as extending another.

For **G2-b**, first perform a separate ARM-ABORT attempt, never launch it, prove expiry, then collect a fresh T-0 set and launch exactly one non-claim A/B/B/A block. Preserve the root; keep `floors/` empty. Build bracket binding before the single whole-window verdict, run the provenance checker, and require exactly `analysis_finalization_member_cover_mismatch` from the scratch finalizer. See `SHAKEDOWN-G2-RUNSHEET.md:780`, `:1212`, `:1281`.

Then ratify **L10-A** at that same head. Its proof is deliberately limited; it does not prove successful full-campaign finalization (`docs/process/state_kernel.json`, `L10-A-G2B-CONTRACT-PREFIX-01`).

For the first claim campaign:

```text
G2-b + L10-A + launch-realization recheck + magistrate GO
  → ALPHA
  → G3
  → BETA
  → G3
  → L10-B on real floor corpus, real floor mint and independent reproduction
  → GAMMA
  → final G3 and L10-C
  → authenticated paper publication
```

After each complete claim window, build the binding and one verdict, then:

```sh
"$PY" scripts/check_window_provenance.py \
  --runs-root "$RUNS_ROOT" --pack-root "$PACK_ROOT" \
  --custody-root "$CUSTODY_ROOT" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --terminal-boundary-record "$TERMINAL_BOUNDARY_RECORD"

"$PY" scripts/record_window_duration_margins.py \
  --repository-root "$REPO" --pack-root "$PACK_ROOT" \
  --runs-root "$RUNS_ROOT" --receipt-root "$WINDOW_CUSTODY_ROOT" \
  --pack-identity "$WINDOW_ID"

bash scripts/backup_runs.sh "$RUNS_ROOT" "$BACKUP_DEST"

"$PY" scripts/extract_detection_floors.py \
  --runs-root "$RUNS_ROOT" \
  --spec "$WINDOW_PLAN_ROOT/extraction_spec.json" \
  --out "$WINDOW_CUSTODY_ROOT/detection-floor-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --consumption-semantics-id d078_minted_envelopes_v1 \
  --hash-bundles
```

Use the finalized-manifest checker mode when that artifact exists. These commands authenticate/check, record margins, back up and extract; **extraction is not minting**. The exact mint/publication inputs must come from the generated estate and L10-B record. Sources: `SHAKEDOWN-G2-RUNSHEET.md:1430`; `window_runbook.md:2155`.

Each floor’s estimate already includes 20% margin and totals **376.8 minutes** (`d117_floor_qwen3-1p7b_v5/generate_configs.py:3010`). A 02:56 start cannot fit. An illustrative 23:30 start would put estimated collection completion at 05:46:48, but scheduling must use reviewed measured budgets. GAMMA’s prefill and combined budgets remain explicitly empty (`d117_contrast_v5/generate_configs.py:2812`). No deadline pressure authorizes truncating membership or improvising window splits.

### 8. Ranked blockers and the paper’s artifact obligations

| Rank | Defect or unknown | Blocks |
|---|---|---|
| 1 | Emitted chain and preflight still require the protected August checkout/shared development Python | First real G2-a arm |
| 2 | Fresh post-watchdog rehearsal acceptance and its actual courier/clean stand-down record not yet harvested | Any real plan |
| 3 | Replacement checkout’s actual model/runtime, physical ledger continuity, sudo authorization and physical state unverified | G2-a collection |
| 4 | `TRANSACTION_PACK` unimplemented; T-0 evaluator/GO-consumer obligations remain | G2-b and unattended campaign arms |
| 5 | No G2-a issued pin or generated production estate; superseded prompt/registration custody must be regenerated and clone-proved | Pack freeze and G2-b |
| 6 | G2-b runsheet omits T-0 authoring; successor `window.env`, confirmation route and final heads are not materialized | Positive pack ARM |
| 7 | Launch-realization recheck, G2-b, L10-A and magistrate GO pending | First claim-bearing ALPHA arm |
| 8 | Floor windows exceed the 02:56 budget; GAMMA budget unknown | Valid later night plans |
| 9 | Production paper suppliers, width reproduction, successor rendering and empirical-refusal routes unproved | Comparison-paper claims, not pack-less G2-a |

**What the first window must supply to the paper**

The prospective protocol has **Figure P1**, a schematic, and no live numerical comparison tables. Former Tables 2/3 and associated fill rows are retired from the fallback article. A successor comparison paper needs an explicitly restored placement/supplier contract; do not fill historical slots opportunistically.

| Paper obligation | Required artifacts | Earliest supplying window |
|---|---|---|
| P.1 selected prefill length and exact workload identity | G2-a probe inventory, counts receipt, four-rung summary, selection record and runtime-verified prompt-pin bundle | G2-a |
| P.4 actual admission/accounting record | Raw power/runtime/environment records, calibration brackets, campaign log, preserved failures and terminal ledger candidate | G2-a supplies diagnostic observations only |
| Former Table 2 floor components and P.1 twelve-ratio hypothesis | ALPHA/BETA authenticated corpora, extraction, minted absolute/comparative cells, replay sidecars, full close-out census | Both floor windows; ALPHA alone is incomplete |
| Former Table 3 model means, contrasts, uncertainty, floor clearance and direction/Holm verdicts | GAMMA’s two registered 40-member contrasts, finalized manifest, claim verdicts, floor bindings and production suppliers | GAMMA after floors |
| Figure P1’s four outcomes | Authenticated comparison/claim verdict for any empirical annotation | GAMMA; the existing schematic needs no measured values |
| P.6 source reproduction | Source-member and width census, bracket/basis/estimator IDs, independently reconstructed-versus-published floors, clean-Git supply-map bindings and validator replay | Floor publication and later claim publication |
| P.8 archive | Frozen plans/receipts, policy, calibration acceptance, drift evidence, manifests, whole-window verdicts, failures/replacements and final claims | Accumulates throughout; complete only after close-out |
| P.9 refusal wording | Verified affected production-window/claim evidence and its issued reason | Only when such an authenticated event exists |

Binding passages:

- **P.1:** twelve required ratios; all authenticated/evaluable, equality at 2 passes; fixed prompt 0, forced 512 decode, exact model/tokenizer/template pins (`prospective-comparison-protocol.md:12`, `:35`).
- **P.3:** two directional comparisons share one Holm family; a missing contrast retains its slot (`:302`, `:333`).
- **P.4/P.9:** invalid evidence means refusal; usable below-floor evidence means not resolvable and does not establish equality (`:440`, `:618`).
- **P.6:** correct point values with coherently wrong widths do not establish reproduction (`:548`).
- **Figure P1:** remains explicitly schematic (`:417`).
- **Retired fills:** floor crosswalk at `results-fill-registry.md:196`; Outcome B at `:972`; empirical refusal at `:974`.

G2-a can justify a prospectively recorded length choice and report its diagnostic observations. It cannot supply v5 floors, model-comparison means, a dominance headline or an empirical comparison refusal. A missing campaign remains **unperformed**, not a measured refusal. The inserted-gap transfer study remains after campaign close and does not become first-window work.

**Next exact lead step:** rule the replacement measurement root/interpreter and assign the chain/preflight retargeting, while the resident magistrate completes the already-prepared rehearsal. All further real-arm commands remain gated on that correction and the harvested rehearsal record.