```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Decision packet and conditional arm-runbook draft complete: no supported short-chain reduction exists; prepare the full-chain fallback with 12600 seconds, subject to the magistrate resolving Ed's short-first instruction and the clone custody route.",
  "workspace": {
    "base_requested": "078a13a461abd124c29796798da5107fe00190a6",
    "base_mode": "informational",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": "078a13a461abd124c29796798da5107fe00190a6",
    "branch": "HEAD"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "Independent production clone and locked-environment preparation", "action": "start_now"},
      {"row": "Short-first versus full-chain first attempt", "action": "needs_ruling"},
      {"row": "Production custody routing and inventory registration", "action": "needs_ruling"},
      {"row": "Final PLAN_ID, NIGHT_ROOT, T0 and WINDOW_MAX_S", "action": "wait_for", "wait_for": "NIGHT-REHEARSAL-01 acceptance and magistrate ruling"},
      {"row": "2026-09-11 04:30, 05:00 or 05:30 full-chain launch", "action": "do_not_start"},
      {"row": "2026-09-12 02:56 full-chain fallback", "action": "wait_for", "wait_for": "Rehearsal acceptance, cleared production preparation, notice and authorized installation"},
      {"row": "Consume G2-a numbers", "action": "wait_for", "wait_for": "Authenticated acquisition and GATE-SENSIBILITY-SWEEP-01"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["078a13a461abd124c29796798da5107fe00190a6"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "078a13a461abd124c29796798da5107fe00190a6$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -c 'print(\"morning_max_seconds\", [int(h*3600)-301 for h in (2.5,2,1.5)]); print(\"0256_max_seconds\", 4*3600+4*60-301); print(\"full_chain_budget_seconds\", 12600); print(\"settles_seconds\", 9*600); print(\"members_seconds\", 24*148)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "morning_max_seconds [8699, 6899, 5099]",
          "0256_max_seconds 14339",
          "full_chain_budget_seconds 12600",
          "settles_seconds 5400",
          "members_seconds 3552"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "members_seconds 3552$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The existing generator cannot produce Ed's requested short first window through supported flags or environment overrides. The recommended unchanged full chain is not short.",
      "needs": "Resolve short-first versus unchanged full-chain fallback; do not silently substitute the latter."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Scout 64 records 38 absolute calibration custody locators. Copying their directories into the clone does not retarget issuing-mode authentication.",
      "needs": "Rule original-location consumption or a governed local-store route; authenticate sequence 76 with verify_custody=True."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Final window coordinates remain dependent on rehearsal acceptance. Production deployment inventory and final handback/head binding also require lead disposition.",
      "needs": "Record acceptance, final coordinates, reviewed acquisition head and production inventory evidence before publication."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The 99cd draft hard-codes the old clone. The cited historical run_night.py:1117 inequality is at line 1465 here. Arm record 123 is absent from this checkout.",
      "needs": "Use a successor draft, refresh source anchors, and attach lead-held arm record 123."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Only source inspection, permitted ls checks and arithmetic were performed. No tests, measurements, census, installer, custody authentication or network Git operations ran. Git status was prohibited, so unowned_dirty is not a cleanliness certification. Night-custody freshness remains uninspected.",
      "needs": "Lead performs the prospective checks and execution below."
    }
  ]
}
```

## Scheduling matrix

**Recommendation:** prepare the unchanged full G2-a chain as the dependable route to usable diagnostic numbers, with **`WINDOW_MAX_S=12600`**. Prepare **2026-09-12 02:56 PDT** as the explicit overnight fallback. This requires a ruling on Ed’s **SHORT first-window** instruction; a 3½-hour allocation must not be described as short.

An earlier **September 11 daytime** quiet slot remains possible under the existing install rule: install during 03:00–06:30, then launch later that day. Do not defer automatically to September 12 merely because the morning slots fail.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Independent clone, locked venv, static supply preparation today | start_now | Reviewed cut head; custody routing where applicable | New production clone only |
| Rehearsal harvest and acceptance | wait_for | Completion after 03:16; activation outside the 02:45–03:30 belt; process termination and delivery evidence | Existing rehearsal custody and global night-agent labels |
| Literal short first capture | needs_ruling | Supported implementation and normal gates, or disposition of the full-chain alternative | Generator, timing policy and evidence semantics |
| September 11 04:30/05:00/05:30, unchanged full chain | do_not_start | Cannot fit honestly | Strict 07:00 boundary |
| Earlier September 11 daytime full-chain alternative | needs_ruling | Accepted rehearsal, quiet-slot availability, short-first disposition | Whole Mac; install still must finish before 06:30 |
| September 12 02:56, full chain with 12,600 seconds | wait_for | Acceptance, clone readiness, coordinates, notice, installation | Whole Mac from exit boundary through acquisition |
| Consume resulting numbers | wait_for | Authenticated corpus and sensibility sweep | Selector, prompt pin and later production estate |

The supplied **ARMED** rehearsal state, machine readings, model-byte presence and Claude reset time are accepted facts, not re-measured here. Arm record `123-arm-record-rehearsal-20260911.md` is absent from this checkout; the lead must attach that evidence. Runbook 67 supplies the corresponding schedule and separation rules. Its old “nothing armed” context does not override the supplied arm fact.

### Q1. What is “short”?

The emitter inventories five runsheet shell blocks and emits four: common routing, G2-a exports, governed bracket, and summarizer. It **excludes the desk producer**. It substitutes the date only. [Generator, lines 118–146](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/gen_g2_phase_d.py:118)

The exact emitted sequence is:

| Stage, in execution order | Work and approximate time | Source |
|---|---|---|
| Routing and exports | Verify checkout HEAD, derive clone interpreter; establish date-derived roots. Seconds, unmeasured. | Runsheet 1534–1598, 328–351 |
| Input assertions/authentication | Require inventory, frozen plan and ladder; run `generate_g2a_probe_inputs.py check`. Seconds to minutes depending on tokenizer/custody reads; unmeasured. | Generator 134–138; runsheet 501–507 |
| Ledger readiness and reservation | `recover_calibration_ledger.py readiness --phase pre-reserve`, then `reserve_calibration_window_bracket.py … --execute`. No capture yet. Seconds to minutes; unmeasured. | Runsheet 509–530 |
| Pre-calibration settle | **600 seconds**. | Runsheet 534–535, 1596 |
| Pre-calibration | Governed fiducial capture: 20-second countdown, display sleep, 59 measured pulses, three warmups and baselines; session-status lookup. Approximately **4–8 minutes**, an engineering allowance, not measured runtime. | Runsheet 427–445; fiducial sources below |
| Pre-calibration screen | Require `b_fiducial_s ≤ 0.032898493715362`. Seconds. | Runsheet 453–475 |
| Small, 512 tokens | 600-second settle + five members × historical 148 seconds = **1,340 seconds / 22m20s**, plus stage startup. | Runsheet 477–498, 540–548, 600–605 |
| Small, 1,024 tokens | Same planning estimate: **22m20s** plus startup. | Same |
| Small, 2,048 tokens | Same planning estimate: **22m20s** plus startup. | Same |
| Small, 4,096 tokens | Same planning estimate: **22m20s** plus startup. | Same |
| Large, 512 tokens | 600-second settle + one member × 148 seconds = **748 seconds / 12m28s**, plus startup. | Same |
| Large, 1,024 tokens | Same planning estimate: **12m28s** plus startup. | Same |
| Large, 2,048 tokens | Same planning estimate: **12m28s** plus startup. | Same |
| Large, 4,096 tokens | Same planning estimate: **12m28s** plus startup. | Same |
| Post-calibration | Same governed capture, approximately **4–8 minutes**. There is **no additional explicit 600-second post settle**. | Runsheet 550–551 |
| Terminal boundary | Record finalized session, `physical_ahead`, `calibration_ledger_head_mismatch`, and non-null terminal pin candidate. Leave tracked pin unchanged. | Runsheet 552–563 |
| Summary | Authenticate members and write counts receipt and four-row summary; require all four rungs and ≥5 small members each. Seconds to minutes, unmeasured. | Runsheet 575–587 |
| Driver reporting/courier | Separate **300-second courier allowance** in scheduling arithmetic. Actual branch publication/delivery must be harvested. | `run_night.py` 958–959 |

Source: [complete G2-a runsheet block](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:316).

Each `run_stage` invokes `run_campaign.py` with the production policy, pre-calibration custody, `--arm-quiet-mode --arm-countdown-s 20 --max-failures 1`. The eight stages therefore also contain eight 20-second countdowns. Do not claim that the historical 148-second cadence is a measured prediction for every model/rung.

Each probe config uses one repetition, one warmup run, **512 output tokens**, 10 Hz power sampling, 30-second idle sampling and five-second warmup sampling. [Probe config, lines 467–498](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/generate_g2a_probe_inputs.py:467)

Calibration arithmetic, excluding initialization, sampler readiness, reduction and custody processing:

- Measured train: `59 × 1 + Σ(j=1…58)[1.5 + vdC₂(j)] = 174.203125 s`.
- Three warmups and their gaps: `3 × (1 + 1.5) = 7.5 s`.
- Three five-second baselines: `15 s`.
- Countdown and display pause: `20 + 5 s`.
- Programmed subtotal per calibration: **221.703125 s**.

Sources: [pulse constants/schedule](/Users/edr/code/JouleWise-wt-g2a-prep/joulewise/powermetrics_fiducial.py:355), [capture sequence](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/validate_powermetrics_fiducial.py:1769), lines 1940–2035.

Thus:

```text
Settles                         9 × 600 = 5400 s
Historical member cadence      24 × 148 = 3552 s
Two programmed calibrations              443.40625 s
Subtotal                                 9395.40625 s = 2h36m35s
Eight explicit stage countdowns          160 s
Conservative subtotal                    9555.40625 s = 2h39m15s
Plus imports, model/rung differences, custody, reduction and other overhead
```

The runsheet’s **2.5–3 hours** is a planning estimate, not a hard upper bound. My proposed **12,600 seconds** adds 30 minutes beyond its three-hour upper estimate.

| Option | Arithmetic and availability | Evidence value | Recommendation |
|---|---|---|---|
| **(a) Unchanged full chain** | Existing implementation. Allocate **12,600 s**, plus 300 s courier. | Can produce the complete authenticated corpus used by later G2-a selection. Still diagnostic/non-claim. | **Prepare this fallback now; obtain the short-first ruling.** |
| **(b) Supported reduction** | **None below the existing minimum.** Emitter flags are only `--check`, `--emit-chain`, `--night-date`. Producer flags exist, but lengths must equal `[512,1024,2048,4096]`, small members ≥5 and large members ≥1. `SETTLE_S=600` is unconditionally exported by the chain. | No valid reduced option to classify. Increasing counts is supported; reducing below the present 24-member minimum is not. | Do not advertise one. |
| **(c) Smallest timing change** | Add an explicit, hash-bound emitter settle parameter, defaulting to 600; a reviewed 60-second setting would save `9×540=4860 s` (**81 min**). Arithmetic subtotal becomes about **78m15s** before overhead. A provisional 100-minute allocation would need runtime review. | Retains all probes/brackets and could retain consumption utility **only after** a physics/contract ruling on shorter settling and normal implementation gates. | Probably cannot responsibly land today. |
| **(c), if “short” means one capture** | A separate minimal smoke-chain profile, with corresponding input/plan validation and an explicitly incomplete-G2-a result contract. Existing full-summary assertions cannot simply be retained. | Real raw capture and plumbing proof; **not** the complete input for current G2-a selection. | Separate bounded implementation; no same-day readiness promise. |

The apparent reduction flags are constrained explicitly in [producer lines 302–316](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/generate_g2a_probe_inputs.py:302); emitter options are at [lines 378–399](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/gen_g2_phase_d.py:378).

**NEEDS_RULING:** retain literal short-first and implement it, or permit the unchanged full-chain attempt as the first real window. I recommend the latter for the fastest path to usable numbers, but this report does not override Ed’s sequencing.

A small `WINDOW_MAX_S` does not shorten the chain. The inspected `_run_chain_once` loop monitors process completion and census; it does not turn the budget into a reduced experiment. Deliberately underbudgeting is not option (b). [Driver, lines 420–507](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/run_night.py:420)

### Q2. Candidate slots and notice timing

For the requested morning slots:

```text
W + 300 < seconds from T0 to 07:00
W is an integer
Wmax = seconds-to-07:00 − 301
```

| September 11 T0 | Largest permitted `WINDOW_MAX_S` | Duration | Latest theoretical install/exit boundary | Time available from 03:30 for harvest through exit |
|---|---:|---:|---|---:|
| 04:30 | **8,699** | 2h24m59s | 04:05 | 35 min |
| 05:00 | **6,899** | 1h54m59s | 04:35 | 65 min |
| 05:30 | **5,099** | 1h24m59s | 05:05 | 95 min |

All three maximal budgets yield **06:59:59** after adding courier time. One second more refuses.

Those exit times are boundaries, not useful installation targets: installation, evidence recording and actual process exit must fit before the closed span begins. The available preparation interval is smaller if the first activation starts after 03:30.

**All three fail for the full chain.** Even omitting calibrations and overhead, settles plus members are `5400+3552=8952 s`, exceeding the 04:30 allowance by 253 seconds. At 05:30, the settles alone exceed the allowance.

More generally, a three-hour window plus courier needs `T0 < 03:55`. An activation starting at 03:30 cannot harvest, arm and exit 25 minutes before such a T0. The proposed 3½-hour allocation needs `T0 < 03:25`, even earlier.

For September 12:

| Quantity | Proposed full-chain fallback |
|---|---|
| Installation | September 11, after acceptance, entirely within 03:00–06:30 PDT |
| T0 | **2026-09-12T02:56:00-07:00** |
| T0 epoch | **1789206960** |
| Exit boundary | September 12 **02:31 PDT** |
| `WINDOW_MAX_S` | **12,600**, 3h30m |
| Acquisition allocation ends | **06:26 PDT** |
| Courier deadline | **06:31 PDT** |
| Margin before 07:00 | **29 minutes** |
| Strict integer maximum | **14,339 seconds** |

A 10,800-second budget would end its courier allocation at 06:01, but provides no margin beyond the runsheet’s three-hour estimate. I prefer 12,600.

The enforced inequality is now at [driver line 1465](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/run_night.py:1463); `:1117` is a historical anchor.

**Actual notice rule—ordering, not an invented minimum interval:**

> “The consolidated notice with these pins is sent after commit H and before the plan is moved into place.”

[NIGHT_HANDBACK, lines 69–70](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process/NIGHT_HANDBACK.md:69)

> “arm email with pins before the move”

[D-175, lines 11151–11154](/Users/edr/code/JouleWise-wt-g2a-prep/docs/decision_log.md:11151)

For the real diagnostic transition, handback lines 129–133 require retirement of the stub and **then** the stage-1 email before any `DIAGNOSTIC_NO_PACK` plan is armed. D-175’s underlying synthesis also requires no NO when the move begins. Neither cited rule specifies 24 hours, one hour, or another fixed notice lead time.

Consequently, notice latency alone does not prohibit a same-morning arm. Actual harvest/acceptance, clone work, handback commit, email acceptance, publication, installation, recording and exit must all fit. A failed rehearsal acceptance, unresolved custody route, or missed install close defeats either candidate.

**Earlier daytime possibility:** installing September 11 before 06:30 for a ruled **09:00** launch is mechanically compatible with these rules. With 12,600 seconds, courier allocation ends **12:35 September 11**, before the next 07:00 on September 12. The installer refuses the entire **07:xx hour**, but not 09:00. This example is a candidate, not evidence that the Mac is available. [Installer lines 108–114](/Users/edr/code/JouleWise-wt-g2a-prep/scripts/install_night_agent.sh:108)

### Q3. Proposed plan inputs

These are proposals for the magistrate **after rehearsal acceptance**.

| Input | Recommended overnight proposal |
|---|---|
| `PLAN_ID` | `d117-g2a-prefill-probe-20260912` |
| Class | `DIAGNOSTIC_NO_PACK` |
| `NIGHT_ROOT` | `/Users/edr/night-custody/d117-g2a-prefill-probe-20260912` |
| `T0_ISO` | `2026-09-12T02:56:00-07:00` |
| `WINDOW_MAX_S` | `12600` |
| Generated probe root | `/Users/edr/JouleWise-shakedown-g2/g2-a-20260912` |
| Generated window ID | `d117-g2a-prefill-probe-20260912` |
| Bracket session | `d117-g2a-prefill-probe-20260912-calibration` |
| Attempts | `d117-g2a-prefill-probe-20260912-cal-pre`, `…-cal-post` |
| Evidence ID | `evidence-d117-g2a-prefill-probe-20260912` |

The night ID is a separate field from the generated calibration identities; matching the generated window ID is a naming recommendation, not a schema requirement. It satisfies the draft validator’s single-component pattern, `[A-Za-z0-9][A-Za-z0-9._-]*`. The canonical writer delegates field validation to `NightPlan`; it does not invent a date-based naming rule. [Validator lines 30–50](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/validate_plan.py:30)

Observed read-only collision checks:

```text
/Users/edr/JouleWise-shakedown-g2/g2-a-20260911
    No such file or directory
/Users/edr/JouleWise-shakedown-g2/g2-a-20260912
    No such file or directory
/Users/edr/night-plan-staging/d117-g2a-prefill-probe-20260912
    No such file or directory
/Users/edr/JouleWise-measurement-v5-20260910-078a13a
    No such file or directory
```

**Night-custody collision status is UNVERIFIED:** the explicit no-touch instruction took precedence over checking that tree. The lead must check absence, including symlinks, before creating the ruled root.

If the magistrate selects September 11 daytime, consistently substitute `20260911` throughout. A second same-date attempt cannot escape a probe-root collision by changing only `PLAN_ID`: the generator still derives the same probe root. Preserve the first attempt and return for a ruling.

### Q4. Clone readiness checklist for today

**Head-selection rule:** use a fresh GitHub `main` snapshot, reviewed with all required acquisition-path changes landed, rather than the old clone or an arbitrary moving “latest” head. Today’s inspected candidate is:

```text
078a13a461abd124c29796798da5107fe00190a6
```

Resolve the actual remote head at the bench. If it differs, review the successor before cutting; do not silently adopt it. For the final arm, freeze the reviewed acquisition head associated with the committed new handback. A required successor handback/code change means re-cut/re-pin and repeat affected validation **before authoring the plan**. Later unrelated bookkeeping does not move an already frozen measurement checkout.

Today’s clone can be prepared provisionally before rehearsal acceptance. It cannot be certified as the final armed clone while final handback/head selection remains open.

The production deployment must also be inventoried. Current inventory lines 24–28 still name the old clone. Preserve retained entries and record the new deployment in lead-owned inventory evidence. Resolve its relationship to the final head explicitly; do not chase a self-referential “commit containing its own SHA-named path.” [Scout 64, lines 413–427](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process_traces/2026-09-09-rehearsal-harvest/64-scout-clone-readiness-astra-report.md:413)

The following commands are **prospective bench instructions**, not executed here.

**1. Select and record the reviewed remote head; cut an independent clone.**

```bash
set -euo pipefail
export CUT_DATE=20260910
export REVIEWED_HEAD='<RULED: full reviewed GitHub-main cut head>'
export REMOTE_URL=https://github.com/mpmdw/JouleWise

remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
test "$remote_main_head" = "$REVIEWED_HEAD"
# If unequal, stop and review/select the successor; do not silently repin.

export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-v5-${CUT_DATE}-${REVIEWED_HEAD:0:7}"
test ! -e "$MEASUREMENT_ROOT"
test ! -L "$MEASUREMENT_ROOT"

git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$REVIEWED_HEAD"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$REVIEWED_HEAD"
git -C "$MEASUREMENT_ROOT" merge-base --is-ancestor "$REVIEWED_HEAD" origin/main
git -C "$MEASUREMENT_ROOT" remote get-url origin
git -C "$MEASUREMENT_ROOT" status --porcelain=v1 --untracked-files=all
```

Use GitHub, as directed; the runsheet’s local canonical-clone transport is superseded for this execution.

**2. Reconstruct the locked environment exactly.**

```bash
cd "$MEASUREMENT_ROOT"
export PYTHONDONTWRITEBYTECODE=1
export GIT_OPTIONAL_LOCKS=0
export PYTHONPATH="$MEASUREMENT_ROOT"

python3.13 --version
# Expected reviewed interpreter: Python 3.13.1.
python3.13 -m venv .venv
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3

export PY="$MEASUREMENT_ROOT/.venv/bin/python"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
```

That is the [runsheet’s exact locked creation recipe, lines 1517–1521](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1517), with `PYTHONPATH` set as the preflight sets it. The three extra packages are intentional reconstruction pins. The lock is a **constraints** file, not a replacement dependency list. [env/README, lines 43–53](/Users/edr/code/JouleWise-wt-g2a-prep/env/README.md:43)

The preflight compares exactly these normalized strings at lines 87–97. An extra `joulewise==0.1.0` is a failure, even when the source metadata is ignored by Git.

**3. Verify editable metadata and clean-tree state.**

```bash
git check-ignore -v joulewise.egg-info/
git status --porcelain=v1 --untracked-files=all
"$PY" -m pip list --editable
"$PY" -B -c 'import joulewise; print(joulewise.__file__)'
"$PY" -B -c 'import mlx, mlx_lm; print("PASS mlx imports")'
```

Expected: `*.egg-info/` is governed by `.gitignore:48`; no untracked/modified gate failures; editable installation identifies this clone; import resolves inside it; normalized lock diff is empty. Ignoring egg-info fixes the Git symptom only. If the lock still fails, inspect/rebuild the fresh environment through the governed recipe; do not delete evidence or loosen the lock.

**4. Enumerate and restore authentic calibration supply.**

99co specifies this source ledger:

```bash
export LEDGER_SOURCE=/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl
mkdir -p "$MEASUREMENT_ROOT/runs"
test ! -e "$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
rsync -a --checksum "$LEDGER_SOURCE" "$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
cmp "$LEDGER_SOURCE" "$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
shasum -a 256 "$LEDGER_SOURCE" "$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
```

This reads the canonical ledger as supply; it does not use or mutate the canonical Git checkout. If that read is also fenced at the bench, obtain an authorized byte-exact export and record its provenance.

Enumerate **every nested `custody_locator`**, including bracket-slot records, not just top-level observation rows:

```bash
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
ledger = Path(os.environ["LEDGER_SOURCE"])
locators = set()
def visit(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "custody_locator":
                assert isinstance(child, str) and child
                locators.add(child)
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)
for line in ledger.read_text().splitlines():
    if line.strip():
        visit(json.loads(line))
for locator in sorted(locators):
    print(locator)
print("locator_count =", len(locators))
PY
```

Scout 64 records **76 ledger rows**, **38 distinct absolute locators** under the iCloud backup tree, and ledger SHA-256:

```text
aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f
```

Those are cited prior observations, not fresh measurements. [Scout 64, lines 429–509](/Users/edr/code/JouleWise-wt-g2a-prep/docs/process_traces/2026-09-09-rehearsal-harvest/64-scout-clone-readiness-astra-report.md:429)

For each enumerated directory, use a ruled, collision-free destination under the clone’s `runs/`, preserving its complete contents:

```bash
# Repeat for every enumerated locator, using the lead's recorded source→destination map.
src='<RULED: exact source custody directory>'
dst='<RULED: corresponding fresh directory under the new clone/runs>'
test -d "$src"
test ! -e "$dst"
test ! -L "$dst"
mkdir -p "$dst"
rsync -a --checksum "$src/" "$dst/"
diff -qr "$src" "$dst"
```

Retain the full map and byte/listing comparisons. Do not reduce the copy set to a few conveniently recent calibrations.

**The routing ruling is indispensable.** Relative locators resolve against `repo_root`; absolute ones stay absolute. Issuing mode does not use backup-root relocation. A local mirror does not make the live loader consume it. An empty inherited `JOULEWISE_BACKUP_ROOTS` can also disable backup-locator probing. [Ledger lines 1786–1791](/Users/edr/code/JouleWise-wt-g2a-prep/joulewise/calibration_ledger.py:1786), [4690–4711](/Users/edr/code/JouleWise-wt-g2a-prep/joulewise/calibration_ledger.py:4690)

Options:

- **Original-location route:** authenticate the unchanged absolute locations and separately retain the mandated local copies. This is the least implementation work if original supply is reliably readable.
- **Governed local-store route:** use the existing store mechanism only after confirming every live caller receives the governed store binding. Passing `calibration_custody_store=` to one desk invocation does not wire the chain.

Recommendation: first establish whether original-location consumption can pass today; otherwise return the local-store integration question. Never rewrite ledger locators, reset the pin, or initialize an empty ledger.

**5. Authenticate from the clone with custody enabled.**

For the ruled original-location route:

```bash
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot

root = Path(os.environ["MEASUREMENT_ROOT"])
pin = root / "configs/calibration/calibration_ledger_head.json"
expected = json.loads(pin.read_text())
assert expected["sequence"] == 76
assert expected["head_digest"] == \
    "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7"

snapshot = load_calibration_ledger_snapshot(
    root / "runs/calibration_observation_ledger.jsonl",
    pin,
    repo_root=root,
    verify_custody=True,
)
assert not snapshot.refusal_reasons, snapshot.refusal_reasons
assert snapshot.head_sequence == expected["sequence"]
assert snapshot.head_digest == expected["head_digest"]
print(f"PASS custody authentication sequence={snapshot.head_sequence}")
PY
```

Preflight’s `verify_custody=False` does **not** discharge this requirement.

**6. Finish static readiness.**

Run the generator’s separate `--check`; verify exact model/tokenizer/template supply; prepare a **successor 99cd draft** with the new root, both full heads and absolute registration path. Its old JSON is not retargeted by shell exports. Use `validate_plan.py --draft "$SUCCESSOR_DRAFT"`.

**Sudo/Ed classification and armed-rehearsal exclusions:**

- Clone, venv, ledger/custody reads and copies, static validation and user LaunchAgent installation need **no new privileged setup or per-window Ed GO**.
- The known authorization check is `/usr/bin/sudo -n -l /usr/bin/powermetrics`; the full preflight invokes it. Acquisition later uses authorized powermetrics privilege. These are uses of `sudo`, not outstanding password/setup requests.
- Ed is needed only if actual hardware/access prerequisites are unavailable or require his intervention. Supplied AC sleep/powermode and authorization facts leave no demonstrated Ed setup task.
- While rehearsal is armed, prepare only independent production/staging estates outside its protected span. **Do not install/uninstall either global night label, publish a second discoverable plan, change the rehearsal checkout, alter its custody, or move any frozen head.**
- Do not execute the full preflight, chain, calibration, campaign, driver or quiet-window check as a “smoke test” from this scout. A census is observational, but its expected agent hit is not quiet-machine acceptance. No census-shaped task authorizes continuing inside the protected span.
- Nothing here requires `/private/tmp`; use `/Users/edr/night-plan-staging/…`. Leave the existing rehearsal `/private/tmp` tree entirely alone.
- Defer all real `night-custody` staging/publication to the authorized post-harvest arm procedure.

### Q5. Runbook 68 draft

The draft below uses the unchanged full-chain recommendation. It is conditional on resolving **short-first**, rehearsal acceptance, final coordinates and custody routing.

99cd steps 3–6 are retained where applicable. Necessary adaptations are marked: new clone pins, successor draft, and runbook-67 validation twin. No block was executed.

````markdown
# Runbook 68 — first real G2-a DIAGNOSTIC_NO_PACK window

DRAFT / NOT ARMED / PROVISIONAL.

This runbook becomes executable only after the magistrate fills every
<RULED: …> value, records rehearsal acceptance, and resolves whether Ed's
short-first instruction permits the unchanged full chain.

Recommendation carried by this draft: full generated chain, 12600 seconds;
overnight fallback 2026-09-12 02:56 PDT. Neither is a ruling.

## Pins and preconditions (step 0)

| Pin | Value |
|---|---|
| Plan ID | <RULED: fresh PLAN_ID; proposed d117-g2a-prefill-probe-20260912> |
| Class/schema | DIAGNOSTIC_NO_PACK / joulewise.night_plan.v2 / integer 2 |
| Final acquisition head H | <RULED: full reviewed main-reachable acquisition SHA> |
| Handback commit | <RULED: committed concrete-night handback and its relation to H> |
| Measurement root | <RULED: independent production clone path at H> |
| Both plan heads | repo_head = measurement_head = H |
| Night custody | <RULED: fresh /Users/edr/night-custody/PLAN_ID> |
| T0 | <RULED: offset-aware whole-minute ISO; proposed 2026-09-12T02:56:00-07:00> |
| Window | <RULED: positive seconds; proposed 12600> |
| Install span | <RULED: dated 03:00–06:30 PDT span; proposed September 11> |
| Exit boundary | <RULED: derived T0−1500 s; proposed September 12 02:31 PDT> |
| Courier deadline | <RULED: derived T0+WINDOW_MAX_S+300; proposed September 12 06:31 PDT> |
| Probe root | <RULED: /Users/edr/JouleWise-shakedown-g2/g2-a-YYYYMMDD derived from T0> |
| Production inventory evidence | <RULED: reviewed deployment inventory record> |
| Ledger/custody route | <RULED: authenticated issuing route and restoration evidence> |
| Bookkeeping estate/record paths | <RULED: authorized linked worktree and allocated paths> |

Step 0 acceptance boundary:

1. NIGHT-REHEARSAL-01 is accepted from actual harvest evidence, including
   required dead-man observation, non-refused rehearsal, courier delivery,
   launchd origin and applicable process-absence evidence.
2. The lead has preserved rehearsal evidence, uninstalled both rehearsal
   agents from their installing checkout, and retired its discoverable plan
   by the governed handback. Never reuse its checkout or roots.
3. No active or indeterminate recorded chain/campaign ownership remains.
   courier.sent alone does not establish this.
4. standdown.request is absent, no prior discoverable plan conflicts, and
   only the magistrate LaunchAgent remains before this installation.
5. Clone, interpreter, ledger, model supply and probe-input readiness are
   established. The whole machine will be available through chain exit.
6. Current activation identity comes from magistrate.lock. Prove that its
   PID is an ancestor of the foreground census process.
7. Reuse runbook 67's raw only-own census and ancestry procedure, lines
   109–130. Run ps -axo pid=,ppid=,command= and
   pgrep -fl "codex|claude|t3"; retain raw output and return codes.
   Own means this activation and attached descendants. A foreign,
   indeterminate, orphaned or reparented process aborts the arm.
   The stub-specific idle-interactive exception is not applied to this
   real diagnostic night.
8. No full preflight or live capture is launched by an active agent to
   demonstrate quietness. The unattended driver owns its first census.
9. Finish the arm record and exit before the closed T0−25-minute boundary.

The notice follows the committed handback and precedes publication.
Record new message/thread IDs. Ed's NO cancels.
If the activation cannot read the thread, record the actual relay channel
and limitation; do not claim a read that did not occur.

## Block A — production readiness, staged authoring and validation (steps 1–3)

Step 1: use the independently prepared production clone. Do not create a
worktree from the canonical repository or use any rehearsal checkout.

Set these exports again in every foreground tool shell:

```sh
set -euo pipefail
export MEASUREMENT_ROOT='<RULED: production clone>'
export MEASUREMENT_HEAD='<RULED: full H>'
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export PYTHONPATH="$MEASUREMENT_ROOT" PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
export PLAN_ID='<RULED: fresh PLAN_ID>'
export NIGHT_ROOT='<RULED: fresh absolute night-custody root>'
export T0_ISO='<RULED: offset-aware T0>'
export WINDOW_MAX_S='<RULED: positive seconds>'
export TRACE="$MEASUREMENT_ROOT/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export RENDER_ROOT="$STAGE/render"
export SUCCESSOR_DRAFT="$STAGE/night_plan.draft.json"
export INSTALL_START_ISO='<RULED: dated 03:00 PDT install opening>'
export INSTALL_END_ISO='<RULED: dated 06:30 PDT install closing>'
cd "$MEASUREMENT_ROOT"
export NIGHT_DATE="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; t=datetime.fromisoformat(os.environ["T0_ISO"]); assert t.tzinfo is not None; print(t.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d"))')"
```

Step 2: inspect fresh paths, including symlinks. NIGHT_ROOT, STAGE and the
date-derived probe root must not contain a prior attempt. Re-check even if
the decision packet reported absence.

Confirm detached HEAD == H, clean tree including all untracked files,
empty normalized lock diff under PYTHONPATH=MEASUREMENT_ROOT, correct
imports and authenticated ledger/custody sequence 76. Preserve the
readiness transcripts. Confirm H's GitHub-main reachability.

Create fresh STAGE and preserve foreground Block A output there.
Use the final clone's actual H in all validation. Build a successor draft
by copying the historical draft into STAGE and replacing only its
measurement_root, measurement_head, repo_head and absolute registration
path. Preserve the coordinate placeholders for resolve_draft.
Do not edit the historical 99cd artifact or assume exports retarget it.

From 99cd step 3, create the fresh night root only after collision review:

```sh
"$PY" -B -c 'import os; from pathlib import Path; Path(os.environ["NIGHT_ROOT"]).mkdir(parents=True)'
```

This creates no discoverable night_plan.json.

Prepare the complete desk inputs; never source the full chain:

```sh
export REPO="$MEASUREMENT_ROOT"
export G2A_ROOT="/Users/edr/JouleWise-shakedown-g2/g2-a-$NIGHT_DATE"
export CALIBRATION_LEDGER="$REPO/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$REPO/configs/calibration/calibration_ledger_head.json"
export POLICY="$REPO/configs/campaign_policies/quiet_mac_p2_production.json"
export POWER_POLICY=ac_high_power
export G2A_WINDOW_ID="d117-g2a-prefill-probe-$NIGHT_DATE"
export G2A_BRACKET_SESSION_ID="$G2A_WINDOW_ID-calibration"
export G2A_EVIDENCE_ROOT_ID="evidence-$G2A_WINDOW_ID"

PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" build-probes \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --small-members 5 --large-members 1
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" bind-window \
  --root "$G2A_ROOT" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY" --power-policy "$POWER_POLICY" \
  --window-id "$G2A_WINDOW_ID" --session-id "$G2A_BRACKET_SESSION_ID" \
  --evidence-root-id "$G2A_EVIDENCE_ROOT_ID"
PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" check \
  --root "$G2A_ROOT" \
  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \
  --ledger "$CALIBRATION_LEDGER" \
  --head-pin "$LEDGER_HEAD_PIN" \
  --campaign-policy "$POLICY"
```

This authenticates inputs before bracket reservation. No calibration
reservation, campaign or powermetrics capture runs in Block A.

Step 3: 99cd step 4 emission, unchanged:

```sh
"$PY" -B scripts/gen_g2_phase_d.py --check
"$PY" -B scripts/gen_g2_phase_d.py --emit-chain "$NIGHT_ROOT/chain.zsh" --night-date "$NIGHT_DATE"
/bin/zsh -n "$NIGHT_ROOT/chain.zsh"
```

Write the staged canonical plan. This is 99cd's writer block with two
necessary successor-draft adaptations: --draft and resolver's draft path.

```sh
"$PY" -B - <<'PY'
import hashlib, os, runpy, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from joulewise.night_gate import NightPlan, D166_REGISTRATION_SHA256
from joulewise.night_plan_writer import write_night_plan

trace = Path(os.environ['TRACE'])
draft = Path(os.environ['SUCCESSOR_DRAFT'])
author = time.time()
author_iso = datetime.fromtimestamp(author, timezone.utc).isoformat()
subprocess.run([os.environ['PY'], '-B', str(trace/'validate_plan.py'),
    '--draft', str(draft),
    '--t0', os.environ['T0_ISO'], '--window-max-s', os.environ['WINDOW_MAX_S'],
    '--plan-id', os.environ['PLAN_ID'], '--custody-root', os.environ['NIGHT_ROOT'],
    '--authored-at', author_iso], check=True)
resolver = runpy.run_path(str(trace/'validate_plan.py'))['resolve_draft']
mapping = resolver(draft, t0=os.environ['T0_ISO'],
    window_max_s=int(os.environ['WINDOW_MAX_S']), plan_id=os.environ['PLAN_ID'],
    custody_root=os.environ['NIGHT_ROOT'], authored_at=author_iso)
mapping['authored_epoch_s'] = author
plan = NightPlan.from_mapping(mapping)
root = Path(plan.measurement_root).resolve(strict=True)
assert str(root) == plan.measurement_root
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'], text=True).strip() == plan.repo_head == plan.measurement_head == os.environ['MEASUREMENT_HEAD']
custody = Path(plan.custody_root).resolve(strict=True)
assert str(custody) == plan.custody_root
assert not (custody/'night').exists() and not (custody/'night').is_symlink()
assert not (custody/'night_plan.json').exists() and not (custody/'night_plan.json').is_symlink()
chain = Path(plan.chain_path)
generator = runpy.run_path(str(root/'scripts/gen_g2_phase_d.py'))
expected = generator['render_g2a_night_chain'](generator['RUNSHEET_PATH'].read_text(), os.environ['NIGHT_DATE']).encode()
assert chain.read_bytes() == expected
assert Path(plan.chain_sha256_path).read_text() == hashlib.sha256(expected).hexdigest() + '  chain.zsh\n'
assert hashlib.sha256(Path(plan.registration_path).read_bytes()).hexdigest() == D166_REGISTRATION_SHA256
staged = Path(os.environ['STAGED_PLAN'])
assert not staged.exists() and not staged.is_symlink()
print(write_night_plan(staged, plan))
PY
```

Use actual authorship time. Require freshness through T0 (≤36 hours);
never backdate or future-date the author field.

99cd step 5 time derivation, unchanged:

```sh
export NIGHT_HOUR="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.fromisoformat(os.environ["T0_ISO"]).astimezone(ZoneInfo("America/Los_Angeles")).hour)')"
export NIGHT_MINUTE="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.fromisoformat(os.environ["T0_ISO"]).astimezone(ZoneInfo("America/Los_Angeles")).minute)')"
```

Runbook-67 staging adaptation: render a validation twin, because
--render-only creates custody_root/night. Keep that write in STAGE.
Use dataclasses.replace on the parsed real staged plan, changing only
custody_root, chain_path and chain_sha256_path to STAGE/validate/custody.
Write it with write_night_plan to STAGE/validate/night_plan.json.

```sh
scripts/install_night_agent.sh \
  --plan "$STAGE/validate/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" \
  --render-only "$RENDER_ROOT"
/usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.plist"
/usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.deadman.plist"
```

Compare real and twin mappings: exactly the three custody paths differ.
Inspect driver checkout, interpreter invocation, resolved courier, local
schedules, WorkingDirectory and RunAtLoad=false. Confirm the real
NIGHT_ROOT/night still does not exist.

The installer revalidates the real plan during installation. Rendering
does not prove the live gate passes.

Record Block A rc=0 only after all checks actually succeed.

## Between blocks — step 3b own-background stop

Stop all own delegated seats, background jobs and keepalive work through
the activation's actual task controls. Record real task IDs/results.

Inspect:
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'

Classify matches by ancestry. Do not signal foreign sessions.
Repeat runbook 67's raw only-own census immediately before publication.
After step 3b, finish Block B, record and exit in the same turn.

## Block B — email, final census, move, install, inspect (steps 4–7)

Step 4: re-establish the same exports and pins. Confirm actual time is
inside the ruled dated install span and enough time remains to complete
installation, verification, recording and exit.

Record:
pmset -g batt
pmset -g custom
defaults -currentHost read com.apple.screensaver idleTime
sysctl -n vm.loadavg
pmset -g therm
sysctl -n kern.bootsessionuuid

These are arm-time observations, not capture validation.
Supplied powermetrics authorization may be cited; any renewed check is
sudo -n -l /usr/bin/powermetrics, never a password prompt.
Keep all real production-policy gates; do not copy the stub's
“powermode recorded, not gated” exemption.

Require:
- machine local time agrees with America/Los_Angeles at T0;
- whole-minute T0 and installer hour/minute match;
- T0 + WINDOW_MAX_S + 300 < next 07:00 local;
- current time and expected record/exit fit before T0−1500;
- no standdown/NO, prior plan conflict or unresolved process ownership;
- H remains pinned and reachable;
- final root/chain/digest/registration are unchanged.

Step 5 — 99cd email-then-arm:
Send Ed the reviewed notice with ID, class, absolute root, both full heads,
local/UTC T0, duration, chain/digest, custody, courier deadline and
cancellation instructions. Record actual send acceptance and message/thread
IDs. Confirm no NO through the available channel and record any limitation.

No email is sent by this draft. The arming activation sends under its
standing authorization.

Step 6: retain a byte copy of the staged plan. Check that staging and
NIGHT_ROOT are on the same filesystem; a failed cross-device rename must
not be replaced with a copy. Re-run the immediate census and all dated
window/standdown checks.

99cd step 6 publication/install, unchanged:

```sh
"$PY" -B - <<'PY'
import os
from pathlib import Path
target = Path(os.environ['NIGHT_ROOT'])/'night_plan.json'
assert not target.exists() and not target.is_symlink()
os.replace(os.environ['STAGED_PLAN'], target)
PY
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE"
```

Record actual installation start/end times.

Step 7: inspect both installed labels and plist bytes:
com.joulewise.night and com.joulewise.night.deadman.

Require:
- night calendar = ruled NIGHT_HOUR/NIGHT_MINUTE;
- dead-man calendar = 07:00;
- WorkingDirectory = MEASUREMENT_ROOT;
- ProgramArguments point to that clone's scripts/run_night.py,
  respectively run/dead-man, and the final absolute plan path;
- RunAtLoad = false;
- courier executable is the reviewed resolved executable;
- installation finished before the ruled 06:30 close.

Preserve the armed plan bytes, both plists, transcripts and initial night/
listing with sizes and timestamps.

On publication/install/verification failure, use the governed recovery
procedure for this attempt: uninstall its two labels from this clone,
preserve attempted bytes and unpublish only this attempt's plan.
Do not remove a checkout while either agent remains loaded.
Do not overwrite prior evidence or improvise cleanup of another plan.

Record Block B rc=0 only after actual success.

## Record and exit (step 8)

Write a 21h-shaped arm record in the authorized linked bookkeeping estate.

Include:
- actual activation ID/PID, timestamps and install start/end;
- handback commit, H, clone path and frozen triple;
- ruled T0/window, all derived deadlines and first firing times;
- notice IDs/time, NO evidence and channel limitation;
- Block A/B commands, output and return codes;
- step-3b stops, census outputs and ancestry classification;
- clone/lock/model/ledger-custody/input validation evidence;
- power, display/screensaver, thermal/load and clock observations;
- exact chain digest and armed plan bytes;
- rendered/installed plist evidence and initial night/ inventory;
- remaining provisional claims.

Copy staging evidence into <RULED: allocated arm-evidence directory>.
Review the exact authorized bookkeeping diff, then commit/push under the
lead's existing authority. Record any publication failure honestly.
Do not move H as bookkeeping advances.

Update the durable pointer and future relaunch prompt with:
(PLAN_ID, MEASUREMENT_ROOT, MEASUREMENT_HEAD).

Next action: harvest this specific night only after the protected span
closes and recorded chain/campaign ownership is cleared. End the activation
with no own background work, before T0−25 minutes. Do not wait resident
until T0. Never manually run run_night.py run as a test.

## Expected observations and harvest acceptance

For the proposed September 12 02:56 / 12600-second plan:
- install on September 11 within the ruled span;
- first dead-man firing on September 11 at 07:00 should stand down because
  the plan's completion epoch is still in the future;
- acquisition begins September 12 at 02:56;
- acquisition allocation ends 06:26, courier deadline 06:31;
- the next headless harvest waits beyond the closed completion boundary,
  courier marker and actual process termination. An early chain exit alone
  does not authorize early magistrate resumption.

Retain night.log and all applicable night/ artifacts:
receipt.json, result.json, chain.started, chain.exited,
censuses.jsonl, chain.stdout.log, chain.stderr.log,
courier.heartbeat, courier.sent, courier.json and launchd output/error logs.
Preserve refusal.json if present; do not manufacture an expected absence.

A green diagnostic gate has verdict GO; C1/C3/C4/C5 PASS and
C2 NOT_APPLICABLE/no_pack_by_design.
Require result chain_exit_code=0 and no abort.
GO alone is insufficient: driver result verdict can remain GO when the
chain exits nonzero.

The probe root must retain:
- prefill-probe-configs/ and order manifests;
- window-plan/calibration_plan.json;
- window-plan/identity-epoch.json and t1-bindings.json;
- window-plan/g2a-input-inventory.json;
- window-plan/prefill-prompt-ladder.json;
- runs/campaign_log.jsonl;
- all 24 expected member bundles;
- pre/post runs/instrument_validation/<attempt-id>/ custody;
- operator-logs/window-chain.log and pre/post calibration logs;
- transcript/g2a-post-bracket-terminal-boundary.json;
- window-plan/d166-prefill-counts-receipt.json;
- window-plan/d166-prefill-resolvability-summary.json.

Require the recorded terminal boundary:
session_state=finalized,
pin_relation=physical_ahead,
refusal_code=calibration_ledger_head_mismatch,
terminal_head_pin_candidate non-null.
The tracked ledger pin remains unchanged during the window.

Courier reports the actual verdict, chain exit code, refusal reason/detail,
night-results/YYYYMMDD branch and watchdog liveness information.
Record actual send evidence and separately verify inbox delivery and remote
branch existence. A send marker does not prove inbox delivery.
The results branch contains driver artifacts; it is not proof that the
separate probe corpus was backed up.

Harvest authenticates every expected member and complete four-rung summary.
The summarizer reads runs/<run_id>/summary_metrics.json and metadata.json;
the count is:
window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count.

Before any G2-a number is consumed, close GATE-SENSIBILITY-SWEEP-01.
Then perform the reviewed terminal-pin advancement and owning desk checks.
Selection consumes d166-prefill-resolvability-summary.json.
Prompt-pin issuance additionally consumes:
d166-prefill-counts-receipt.json,
prefill-prompt-ladder.json,
g2a-input-inventory.json and the selection record.

These are real diagnostic capture results, not claim-bearing campaign
numbers. G2-a does not mint a pack and its bundles are not reused as G2-b
campaign members.

After evidence preservation and process clearance, uninstall this plan's
night agents from MEASUREMENT_ROOT and retire its discoverable plan through
the governed handback. Preserve production clone and raw probe custody;
do not copy the stub's disposable-root deletion instruction.

## Fact table — source locations at inspected 078a13a4

| Fact | Source lines |
|---|---|
| Hard rehearsal start dependency; coordinates still need ruling | docs/process/state_kernel.json:2453–2490 |
| Sensibility sweep before consuming numbers | state_kernel.json:2632–2658; RUN_STATE.md:15 |
| Install span remains 03:00–06:30 | state_kernel.json:2767–2793 |
| Canonical staged authoring and clone-based installation | 99cd README.md:96–220 |
| Successor draft required for new clone | scout 64:394–411 |
| Only-own census, step 3b, twin and record shape | runbook 67:39–51, 89–130, 189–214, 310–366 |
| Render-only creates custody/night | scripts/install_night_agent.sh:117–125 |
| Installer pins, courier and both labels | install_night_agent.sh:81–103, 191–216 |
| Notice ordering and diagnostic transition | docs/process/NIGHT_HANDBACK.md:69–74, 129–144 |
| D-175 ordering; specifically eight stub conditions | docs/decision_log.md:11146–11155 |
| Plan-span and fixed-belt boundaries | docs/process/MAGISTRATE_WATCHDOG.md:42–56 |
| Full-chain block inventory and date-only emission | scripts/gen_g2_phase_d.py:118–158 |
| Full probes/brackets/count outputs | SHAKEDOWN-G2-RUNSHEET.md:328–605 |
| Locked venv reconstruction | SHAKEDOWN-G2-RUNSHEET.md:1499–1529 |
| Driver first census and strict dead-man inequality | scripts/run_night.py:1417–1465 |
| GO does not imply chain_exit_code=0 | scripts/run_night.py:1676–1692 |
| Exact summary source field/files | scripts/summarize_g2a_prefill_probe.py:287–294, 474–479 |
| Courier content | docs/process/NIGHT_COURIER_PROMPT.md:3–17 |

## UNVERIFIED

This is an unexecuted draft. Final rulings, current source/head review,
custody routing/authentication, live machine predicates, install outputs,
process absence, launchd firing, captures, corpus validity, courier delivery
and results publication remain lead-owned verification.
````

### Q6. Refusals most likely to waste the window

Desk checks eliminate configuration mistakes; they cannot certify future quietness or capture-time success.

| Risk | Pre-arm check and limitation |
|---|---|
| **Calibration ledger missing, rollback, stale pin or invalid custody** | Restore exact ledger and every referenced directory; run the clone loader with **`verify_custody=True`**, requiring sequence 76 and exact digest. Resolve absolute-locator routing. Preflight’s custody-disabled pass is insufficient. |
| **Lock diff or dirty clone** | Run the exact normalized lock comparison with `PYTHONPATH` set to the clone; inspect all-untracked Git status and editable metadata. The new egg-info ignore does not fix duplicate package-distribution metadata. |
| **Model/tokenizer/template mismatch** | Check both exact panel revisions and local sources; run `build-probes`/`check`; hash `tokenizer.json` and the UTF-8 `chat_template` string using the adapter’s convention. File presence and a revision string alone do not establish complete weight-byte provenance. Preserve available model supply evidence. |
| **Clock/attestation confusion** | For this v2 diagnostic, C4 checks canonical boot UUID plus finite epoch/monotonic observations. Check local timezone, T0 conversion and UUID at the desk. **Do not import the pack-only independent clock-reference/T0 attestation ceremony as an extra G2-a prerequisite.** Capture-time clock-anchor validity remains a live instrument obligation. |
| **HID/screensaver refusal** | Run `/usr/bin/defaults -currentHost read com.apple.screensaver idleTime`; the night gate requires output exactly `0`. This predicate is the screensaver setting, not a sampled “minutes since keyboard input” value. Actual display-asleep/screensaver-disengaged admission remains governed inside capture. |
| **Thermal, load, AC or display failure** | Inspect `pmset -g batt`, `pmset -g`, `pmset -g custom`, `pmset -g therm`, `sysctl -n vm.loadavg`. Night gate requires AC, a valid displaysleep field, load ≤2 and any reported CPU speed limits equal to 100. Campaign policy additionally requires thermal nominal, display asleep and low-power mode off. Supplied `sleep=0` does not prove the other predicates. |
| **Agent census or prior measurement ownership** | Complete raw only-own arm census with ancestry; stop own background work; clear prior chain/campaign ownership. At launch the driver needs empty production census and repeats it every 30 seconds. No active scout can prove its own future absence. |
| **07:00 arithmetic or wrong launchd calendar** | Calculate strict inequality, whole-minute local time and first firing date; compare installed calendars to T0. Largest integer limits are 8,699/6,899/5,099 for the requested morning slots. Do not confuse declaration of `WINDOW_MAX_S` with measured runtime. |
| **Stale draft, chain or registration** | Use successor draft, exact cloned generator output, GNU SHA sidecar, canonical writer, correct registration digest, actual authorship time and both head pins. Revalidate before publication. |
| **Pre-calibration screen or capture failure** | Authenticate calibration supply and unchanged D-079 screen; preserve real power-mode evidence and let the quiet machine settle. No desk check can prove the new pre-slot bound or capture-timeout seam will pass. Do not lower the screen or retry opportunistically inside the window. |
| **Courier unavailable, usage/auth failure or incomplete backup** | Verify resolved executable and prior accepted rehearsal delivery evidence. The supplied September 10 16:00 bucket reset improves scheduling context but does not prove later availability. Verify send, inbox and remote publication independently; preserve the separate probe corpus. |

C4 and quiet predicates are explicit in [night gate lines 1136–1298](/Users/edr/code/JouleWise-wt-g2a-prep/joulewise/night_gate.py:1136). The stronger capture policy is in [quiet_mac_p2_production.json](/Users/edr/code/JouleWise-wt-g2a-prep/configs/campaign_policies/quiet_mac_p2_production.json:6).

## Critical path

- **Rehearsal harvest → accepted NIGHT-REHEARSAL-01 → final coordinate ruling and diagnostic arm.**
- **Reviewed clone head + locked environment + ruled custody route → authenticated production readiness → final handback/plan validation.**
- **Short-first disposition → choice of unchanged chain or separately gated short implementation.**
- **Committed handback + validated staged plan → notice → final census → atomic publication → installation → record and exit.**
- **Successful acquisition + courier/process clearance → harvest → sensibility sweep and reviewed terminal-pin handling → G2-a consumption.**

The next bench action is the independent GitHub clone and locked-environment preparation at a reviewed main head, alongside resolution of the custody route. Final arming remains behind rehearsal acceptance and the short-first ruling.