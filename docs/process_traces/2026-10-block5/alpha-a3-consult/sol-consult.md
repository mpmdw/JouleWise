```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Choose (b): hold ALPHA attempt 4 for a verified owner restart, with a structural failure census before re-arming.",
  "workspace": {
    "base_requested": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "base_mode": "exact",
    "head_start": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "head_end": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "upstream_end": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "branch": "lane/2026-10-07-harvest-lane"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "Nine corpus survivors necessarily prevent the bound, but the three runtime failures remain unclassified.",
    "remediation": "Hold the next arm for a verified owner restart and first check the aggregate runtime failure classification."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The permitted evidence does not classify the corpus members' runtime failures or identify the parent of find.",
      "needs": "Magistrate should decide whether to authorize the proposed counts-only census before the next arm."
    }
  ]
}
```

## Causal chain

### Cause

**The crucial correction: two nonzero corpus-stage exits do not establish two physical attempts at the three failed members.**

The chain deliberately retries into the same root. It recovers members that have **no bundle**, preserves successful bundles, and never remeasures existing failed bundles (`joulewise/b5/chain.py:226–235`). The retry decision counts summary statuses; it does not inspect failure causes (`chain.py:812–835`). The retry follows an ordinary settle, with no contention-conditioned wait (`chain.py:1216–1235`).

The campaign runner implements that restriction:

- A readable existing summary selects `skip complete`, even when its status is failed (`scripts/run_campaign.py:3024–3038`).
- Existing failed evaluations make that campaign invocation fail; the branch continues without launching the member (`run_campaign.py:10731–10753`, `10854–10863`).
- An existing incomplete bundle selects `incomplete existing`, requiring inspection or relocation rather than automatic execution (`run_campaign.py:3037–3038`, `10865–10894`).

Thus an admission abort on pass one can make the retry fail **deterministically on the retained bundle**, even if the machine has become clean. That says nothing by itself about whether a fresh-root attempt 4 would meet the original physical condition.

**Runtime conditions that produce a nonsucceeded corpus member:**

| Condition | Effect | Can this stage retry repair it? |
|---|---|---|
| Idle admission remains physically inadmissible after its internal retry | The enabled abort policy raises a stage failure. The admission evaluator tests CPU busy ratio, processor combined power, and GPU idle admission. | No, once the failed bundle exists. |
| Runtime, model, transport, telemetry, controller, or writing exception; adapter returns failure | The controller records failed or unsupported status, according to its closed failure-reason mapping. | No existing failed bundle is remeasured. A transient refusal leaving no bundle can be retried. |
| Reducer cannot read required artifacts or encounters a reduction error | Structured failed summary. | No. |
| Process interruption, death, or member cap | Failed, incomplete, or absent evidence; campaign timeout is also a failed outcome. | Only if no bundle remains; incomplete existing bundles block execution. |
| A pre-bundle refusal | No summary/bundle to count as succeeded. | Yes, if the refusal disappears and the collection horizon permits the retry. |

Code: admission policy `configs/campaign_policies/quiet_mac_p2_b5.json:25–39`; physical admission predicates `joulewise/idle_admission.py:413–456`; internal retry and abort `joulewise/controller.py:1945–2002`; failure mapping `controller.py:185–195`; exception handling `controller.py:1616–1644`; failed-bundle preservation `controller.py:2599–2632`; adapter failure handling `controller.py:3711–3715`; reducer failures `joulewise/reduce.py:2639–2667`, `2699–2712`; member timeout handling `run_campaign.py:11125–11149`, `11226–11236`.

**The monitor’s outside-process threshold is not itself the runtime admission predicate.** A contention overlap is a harvest-time member flag (`joulewise/b5/harvest.py:3208–3224`). Outside work can also cause the separate idle-admission predicates to fail, but the journal does not prove that happened.

Likewise, the HAZARD controller records environment-guard failures instead of aborting at those guard sites (`controller.py:1877–1903`, `2178–2191`). Missing admission evidence alone is admitted and flagged; a measured threshold failure retains retry/abort behavior (`controller.py:2101–2129`). Thermal and contention journal findings therefore cannot simply be equated with nonsucceeded summary status.

**Harvest exclusions:**

- `neg8.bound_not_derived` means no accepted, validated bound: absent/unreadable artifact, failed arithmetic or corpus authentication, failed member rederivation, or insufficient eligible members. The initial emission is at `harvest.py:4547–4608`; physics pruning can emit it again when fewer than ten clean members remain or clean-bound derivation fails (`harvest.py:5405–5438`).
- `neg8.screen_failed` means the bracket is absent, not passed, or carries NEG-8 conditions, unless the applicable survivor/subset re-screen runs and passes without conditions (`harvest.py:4890–4955`). An unavailable bound prevents that re-screen (`harvest.py:5235–5239`).

For attempt 3, the permitted harvest fields confirm **9/12 corpus successes**, both exclusions, and no collector faults. The driver's permitted corpus record confirms nine kept. Nine cannot support the bound: the mint refuses below ten (`joulewise/whole_window.py:4704–4720`). An invalid or absent bound adds both underived conditions to the screen (`whole_window.py:2204–2212`).

**Both exclusions are therefore entailed by the short corpus.** They are not evidence of two independent defects. However, the permitted evidence cannot establish that underivation was the screen’s *only* failure.

The start-reference count **2/3 does not independently fail the screen**. Two surviving references at each endpoint are supported (`whole_window.py:141`, `2267–2273`; registration `configs/campaigns/v5_claim_25g83/registration_block5.md:615–625`). Runtime success also does not guarantee harvest survival, so another start-reference loss remains possible.

**Contention: front-loaded, but not confined to startup.**

My recount of attempt 3’s permitted journal:

- **1,916 lines:** 1 session start, 1 snapshot, **1,913 intervals**, 1 session end.
- **173 dirty intervals** overall.
- Interval ordinals **1–180:** 49 dirty; **181–360:** 32 dirty.
- The remaining **1,553 intervals:** 92 dirty.
- All **31 `find` intervals** occur at ordinals **74–104**, involving two process identities; 18 have `find` alone.
- First 180 intervals include `find` 31, `fseventsd` 13, `mediaanalysisd` 10, `airportd` 7, and smaller counts of other processes. Counts overlap.
- `mediaanalysisd` occurs in **73 intervals**, alone in **72**, spanning ordinals **26–1888**.
- `signpost_reporte` occurs in **17 intervals**, all in ordinals 181–360; `corespotlightd` occurs in **8**, all between ordinals 199–326.

Source: `/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z/hazards/monitor/contention.jsonl`, interval records only.

Startup concentration is clear. Exact overlap with the corpus members’ admission or request spans cannot be established from the allowed files: the permitted driver stage entries contain kind, identifier, and return code, without stage timing.

**`find` ownership is unresolved.** “Outside” means outside the recorded process-tree closure, not necessarily an OS job; an orphan of ours could also be outside (`joulewise/hazards/contention.py:321–333`, `366–380`). The journal’s offender entries contain no parent PID.

The plan-time chain contains no `find` command. Repository backup tooling does invoke it (`scripts/backup_runs.sh:34`). An OS launcher also exists: `com.apple.locate` invokes `/usr/libexec/locate.updatedb`, which launches `find` (`/System/Library/LaunchDaemons/com.apple.locate.plist:5–12`; `/usr/libexec/locate.updatedb:92`, `130–131`). But that plist is disabled by default and has a weekly schedule (`com.apple.locate.plist:7–8`, `23–30`). None of this identifies the observed parent. Live ancestry inspection was unavailable in this sandbox. I would not label `find` an OS job or kill it on this evidence.

### Recurrence

**My operational estimate for an unchanged attempt 4 is about 25% claim-usable, with low confidence.**

Basis:

- There are two completed chains, zero claim-usable results; the NULL attempt is a different failure mechanism.
- A simple uniform-prior model on those two completed-window outcomes gives 25% predictive success. This is a decision estimate, not a calibrated machine probability.
- The supplied runtime corpus counts give 19 successes in 24 planned members. Treating these as independent with success probability 19/24 would give about **53%** probability of at least ten successes in twelve. That optimistic calculation omits harvest physics losses and every other window gate.
- The independence assumption is visibly poor: attempt 3 has 81 dirty intervals in its first 360, with `find` concentrated in one contiguous range, and persistent `mediaanalysisd` activity across the journal.
- The supplied first attempt reached ten with no margin, then lost the bound at harvest. Attempt 3 never reached ten. The corpus is the fragile part, even though the science cells now meet their minimum.

A shared deterministic corpus failure could make that estimate much too high. A one-off startup job could make it too low. The retained-bundle retry behavior prevents treating the retry as another independent sample.

## Remediation

### Recommendation

**(b): hold attempt 4 for the owner’s restart; do not arm unchanged meanwhile.**

1. **First obtain the structural census below, if the magistrate authorizes it.** A shared deterministic model/runner/reducer failure would defeat the proposed machine-state cure and should redirect work before another arm.

2. **Keep no window armed while awaiting the owner.** Prepare the handoff and continuation procedure at the desk. The owner’s authorization is already given; the missing event is his physical restart and FileVault login.

3. **Owner runs the approved Spotlight disable, then restarts between windows:**

   ```sh
   /bin/launchctl disable gui/501/com.apple.corespotlightd
   sudo /sbin/shutdown -r now
   ```

   The two photo-analysis disables already exist, according to the brief. Do not repeat the SIP-refused bootout as if it were a new cure.

4. **After login, verify before publishing the next arm:**

   ```sh
   /bin/launchctl print-disabled gui/501
   /bin/launchctl print gui/501/com.apple.mediaanalysisd
   /bin/launchctl print gui/501/com.apple.photoanalysisd
   /bin/launchctl print gui/501/com.apple.corespotlightd
   /usr/bin/pgrep -x mediaanalysisd
   /usr/bin/pgrep -x photoanalysisd
   /usr/bin/pgrep -x corespotlightd
   /usr/sbin/sysctl -n kern.boottime
   ```

   Check that all three labels remain disabled, no target process is running, and boot time changed. Repeat the process checks after the login startup work settles. The registered arm must then independently pass all six hazards.

5. **Resume from the same sealed collection clone**, with fresh attempt roots and the ordinary notice/arm procedure. Verify the watchdog resumed after login. Repeat the service checks before later packs.

Why hold: the prior immediately executable cure failed, while the restart has a specific, checkable mechanism for removing the persistent photo-analysis agents. Attempt 3 still records `mediaanalysisd` in 73 intervals, 72 alone. There is no demonstrated equally effective magistrate-only cure here. An unchanged window while awaiting the restart risks another unusable corpus and complicates the owner’s safe restart opportunity.

**I do not recommend changing the minimum or contention limit from these data.** The observed burden establishes poor yield, not that admitted contaminated measurements would be valid. Twelve needing ten is operationally fragile at the observed loss rate, but two chains do not establish that a verified machine-state cure cannot make it adequate.

If that cure fails with classified physical admission losses, my preferred prospective change is **a predeclared corpus spare stage using new bundle identities**, bounded in advance and triggered only by runtime status or directly measured physical conditions. Preserve every original bundle; include every eligible collected corpus member in the bound with its actual sample size. Do not rerun until a desired energy or bound appears. Merely adding more same-root retries will not repair the existing failed-bundle path (`chain.py:226–235`).

Such a collection change requires a cold erratum, new seal, and block restart at ALPHA (`registration_block5.md:2857–2868`, `3031–3035`). I would not run unchanged windows in parallel while building it.

## Disproved alternatives

- **Start reference 2/3 necessarily invalidates the screen:** false; two endpoint survivors are supported.
- **Retry rc 1 proves the three members physically failed again:** false; existing failed bundles are not remeasured.
- **A harvest defect is needed to explain attempt 3:** no; nine is below the registered and implemented bound minimum.
- **END STATE:** not supported. The supplied count is 2 unbounded of 233 recorded statuses; the rule requires more than half (`registration_block5.md:2848–2854`).

## Residual risk

### Least sure

I am least sure **whether the three corpus failures were physical admission aborts or a shared operational failure**.

The one additional fact most likely to change my recommendation is the **aggregate failure classification of those three, together with whether their failed summaries already existed before the stage retry**. A common deterministic failure moves me from restart-first to fixing that failure. Physical threshold aborts strengthen restart-first, without proving which journal process caused them.

Missing bound already prevents the screen; the permitted evidence cannot exclude another screen cause. Restart may remove the photo agents while leaving other startup work or a wrongly calibrated admission criterion.

No files changed. No tests, measurements, network calls, or background tasks were run.

### Counts I would want

**Proposed only; not run.** This reads closed corpus records and the closed retry snapshot, so the magistrate must decide whether it is permitted. It prints only fixed code names and integers, never member identities, error text, timestamps, or measured values.

```sh
python3 -B - <<'PY'
import json
from collections import Counter
from pathlib import Path

counts = Counter()
statuses = {"succeeded", "failed", "unsupported"}
reasons = {
    "did_not_fit", "format_unavailable", "unsupported_workload",
    "runtime_unavailable", "telemetry_unavailable",
    "model_identity_mismatch", "permission_denied",
    "transport_unavailable", "cleanup_failed", "unknown_error"
}
conditions = {
    "cpu_baseline_telemetry_missing",
    "cpu_baseline_telemetry_malformed",
    "cpu_baseline_sample_count_insufficient",
    "cpu_busy_ratio_p95_exceeded",
    "processor_combined_power_w_p95_exceeded",
    "gpu_idle_admission_not_passed",
    "gpu_idle_admission_unknown"
}
phases = {
    "validate", "prepare", "idle_baseline", "warmup",
    "measured_run", "idle_drift_sentinel", "cleanup", "reduce"
}

def read_object(path):
    try:
        value = json.loads(path.read_bytes())
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}

try:
    custody = Path(
        "/Users/edr/night-custody/v5-b5-alpha-a3-20261009T0644Z"
    )
    root = Path(
        "/Users/edr/night-b5/v5-b5-alpha-a3-20261009T0644Z/"
        "runs_d117_floor_qwen3-1p7b_v5_bound"
    )
    manifest = read_object(Path(
        "configs/campaigns/neg8_reference_corpus_v5/"
        "derivation/settled_corpus.json"
    ))
    snapshot = read_object(
        custody / "night/transcript/neg8-corpus-before-retry.json"
    )
    before = {
        row.get("bundle_path"): row
        for row in snapshot.get("members", [])
        if isinstance(row, dict)
    }
    counts["snapshot.readable"] = int(bool(snapshot))

    for member in manifest.get("members", []):
        relative = member.get("bundle_path")
        if not isinstance(relative, str):
            counts["probe.invalid_manifest_path"] += 1
            continue
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            counts["probe.invalid_manifest_path"] += 1
            continue

        bundle = root / rel
        summary = read_object(bundle / "summary_metrics.json")
        status = summary.get("status")
        label = status if status in statuses else "missing_or_other"
        counts["final." + label] += 1

        old = before.get(relative, {})
        if old.get("summary_present") and old.get("status") != "succeeded":
            counts["retry.preexisting_nonsucceeded_summary"] += 1
            if status != "succeeded":
                counts["retry.preexisting_still_nonsucceeded"] += 1
        if old and not old.get("summary_present") and summary:
            counts["retry.new_summary"] += 1

        if status == "succeeded":
            continue

        reason = summary.get("failure_reason")
        counts["failure." + (
            reason if reason in reasons else "missing_or_other"
        )] += 1

        metadata = read_object(bundle / "metadata.json")
        admission = metadata.get("environment_admission", {})
        if not isinstance(admission, dict):
            admission = {}
        counts["member.admission_aborted"] += int(
            admission.get("decision") == "abort"
        )

        attempts = admission.get("attempts", [])
        for ordinal, attempt in enumerate(attempts[:2], 1):
            if not isinstance(attempt, dict):
                continue
            cpu = attempt.get("cpu_admission", {})
            if not isinstance(cpu, dict):
                cpu = {}
            for code in set(cpu.get("conditions", [])) & conditions:
                counts["admission.attempt_" + str(ordinal) + "." + code] += 1

        try:
            event_lines = (bundle / "events.jsonl").read_bytes().splitlines()
        except Exception:
            event_lines = []
        for line in event_lines:
            try:
                event = json.loads(line)
            except Exception:
                continue
            if isinstance(event, dict) and event.get("event_type") == "failure":
                phase = event.get("phase")
                counts["failure_stage." + (
                    phase if phase in phases else "other"
                )] += 1

    for code, count in sorted(counts.items()):
        print(code, count)
except Exception:
    print("probe.failed", 1)
PY
```

The admission record and failure-event fields used here are authored at `joulewise/controller.py:1846–1855`, `2599–2604`, `3671–3685`; the retry snapshot fields are authored at `joulewise/b5/chain.py:829–837`.