# Read a refusal

The Mac's sensors report CPU, GPU, and Neural Engine power, so the model's work
and background work on those three processor channels arrive in the same
measurements. A busy background
process can raise the measured power; a missing record from the **power
sampler**, the program that records processor power over time, can hide when
that happened; an incomplete **calibration**, the stored reference observations
used to check the instrument's timing and response, can leave those properties
unproved. In any of those cases, printing an energy number would turn missing
knowledge into false precision.
JouleWise therefore produces a **refusal**: the instrument declines to produce
a number or support a capstone statement, records the condition that prevented
it, and preserves the evidence already collected.

A **reason code** is the exact, stable text stored for one such condition. A
**detail message** is the accompanying plain description or recorded values.
Read both: the code lets software recognize the condition, while the detail
locates the physical or procedural cause in this run.

JSON is a text format that stores named fields and values.

```text
[physical event or missing record]
                 |
                 v
[script checks the required condition]
                 |
                 v
[exact reason code plus detail]
                 |
                 v
[retained JSON record; no doubtful number or capstone statement]
```

Each bracketed rectangle names a stage. Each downward arrow means that the
stage above supplies the facts used by the stage below. The last rectangle is
the forcing result:
the instrument keeps an explainable stop instead of silently filling a gap.

## Where to look

`scripts/run_campaign.py` is the main measurement runner. A **campaign** is the
scheduled set of individual model runs that the runner executes. One such run
is a **member**. An individual run's
`summary_metrics.json` stores `status`, `failure_reason`, and
`failure_message`. The runner also appends JSON objects to
`campaign_log.jsonl`: a `campaign_verdict` object classifies collected member
directories as usable, `waived` (accepted only under an explicit recorded
exception), failed, or missing, and an
`idle_admission_whole_window_verdict` object records the **idle-admission**
decision — “idle admission” being the code's name for quiet-machine
acceptance: whether stored evidence proves that the Mac was sufficiently idle
for the whole measurement window and that required references are present. A
**member directory** is the retained directory for one scheduled model run. A
**whole-window verdict** is one decision over the exact set of member
directories in the uninterrupted measurement period. The runner can also copy
the exact appended whole-window object to a separate file named with
`--whole-window-verdict-output`.

### Find one

Both records are plain text: the member file is one JSON object, and the
campaign log is one JSON object per line. Set the two names, then run:

```sh
CAMPAIGN='replace-with-campaign-directory-name'
MEMBER='replace-with-member-directory-name'
python3 -m json.tool "runs/$CAMPAIGN/$MEMBER/summary_metrics.json"
grep '"record_type": "idle_admission_whole_window_verdict"' \
  "runs/$CAMPAIGN/campaign_log.jsonl" | python3 -m json.tool --json-lines
```

The first command prints one member's outcome. The second selects every
whole-window decision from the append-only campaign log — a file that gains
new rows without rewriting older rows — and formats each JSON line. Preserve
the original files; these commands only read them.

Before measurement, the instrument must be **armed** — given a single-use
authorization to launch one exact, already-fixed set of files. That fixed set
is called a **pack**: a directory whose configurations, execution order, and
commands were recorded and fingerprinted before measurement.
`scripts/generate_arm_readiness.py` checks the pack and pre-start evidence,
while `scripts/launch_window.py` checks the
single-use permission record and starts the recorded command. Both print JSON
with `status: REFUSE` and a `reason_codes` list when preparation or launch
cannot proceed. After
measurement, `scripts/record_window_duration_margins.py` prints
`status: REFUSE`, one `reason`, and one `detail` when it cannot write its
duration receipt, the retained calculation of whether the measured stages —
prompt processing and token generation, the two physically different parts of
an inference request — ran long enough for the prepared plan. These terminal messages are records to
preserve; do not assume a refusal wrote a receipt unless its output names one.

## Codes from an individual run

The individual-run vocabulary is enumerated in `joulewise/schemas.py`:

- `did_not_fit` — the workload did not fit the device capacity available to
  the runtime.
- `runtime_unavailable` — the model runtime or a resource it needed could not
  be started or loaded.
- `telemetry_unavailable` — the power sampler could not supply measurements.
- `format_unavailable` — the selected runtime process could not exchange the required
  data format.
- `permission_denied` — the operating system denied a required operation,
  commonly access to the power sampler.
- `transport_unavailable` — the local-process or remote-machine connection
  failed.
- `unsupported_workload` — the selected runtime does not implement this kind
  of model request.
- `cleanup_failed` — temporary runtime or sampler resources remained after
  the run tried to remove them.
- `unknown_error` — an unexpected failure reached the final safety fallback;
  use `failure_message` and `logs/controller.log`, the detailed event log
  written by the **controller** — the code that starts the model runtime and
  sampler, runs one member, and classifies whatever went wrong — to locate it.

The controller records `did_not_fit`, `format_unavailable`,
`unsupported_workload`, `runtime_unavailable`, and `telemetry_unavailable` as
unsupported. These are structural incompatibilities: retrying the same
workload on the same hardware and software cannot repair them. It records
permission, connection, cleanup, and unexpected failures as failed operations
that may change after the setup or environment is corrected. Neither kind
supplies an energy result.

## Codes attached to a whole-window member

The whole-window member-condition enumeration is in
`joulewise/whole_window.py`. Here **quiet-machine acceptance** means the stored
evidence proves that the Mac was sufficiently idle under the selected policy,
the recorded set of required checks and ceilings; it does not mean merely that
the model command finished.

- `cpu_admission_unenforced` — the central processor quietness check was not
  enforced.
- `cpu_baseline_sample_count_insufficient`,
  `cpu_baseline_telemetry_malformed`, or `cpu_baseline_telemetry_missing` —
  the before-run central-processor samples were too few, unreadable, or absent.
- `cpu_busy_ratio_p95_exceeded` — the 95th-percentile central-processor busy
  fraction — the level exceeded by only the busiest 5% of recorded samples,
  chosen over the average so that a short burst of background work cannot hide
  inside a quiet mean — exceeded the policy ceiling.
- `processor_combined_power_w_p95_exceeded` — the corresponding 95th-percentile
  combined processor power exceeded the policy ceiling.
- `gpu_idle_admission_not_passed` or `gpu_idle_admission_unknown` — the
  graphics processor was not shown idle, or its state could not be decided.
- `environment_admission_failed` or `environment_admission_missing` — the
  stored power, display, screensaver, thermal, or background-load check failed
  or was absent.
- `thermal_pressure_elevated_in_window` — macOS detected heat-related
  operating pressure during the measured interval.
- `idle_admission_attempt_ledger_invalid` — the stored sequence of quietness
  checks and retries was missing, malformed, or inconsistent.
- `whole_window_bundle_invalid` — a member failed the strict bundle check,
  which reloads required files and rejects missing, malformed, or inconsistent
  evidence.

## A retained failed whole-window record

The retained diagnostic artifact
`docs/process_traces/2026-07-24-diagnostic-extraction/diagnostic_details.json`
contains this actual object. One reason code contains `neg8`, the internal name
of the repeated reference workload; it is a label in the code, not a measured
quantity.

```json
{
  "covered_bundle_count": 104,
  "reasons": [
    "cpu_baseline_telemetry_missing",
    "environment_admission_missing",
    "idle_admission_attempt_ledger_invalid",
    "instrument_calibration_bracket_missing",
    "neg8_bracket_missing",
    "whole_window_bundle_invalid",
    "whole_window_campaign_membership_unresolved"
  ],
  "record_count": 3,
  "status": "failed"
}
```

Field by field: `covered_bundle_count` says the recorded verdict rows covered
104 member directories. `record_count` says three matching verdict rows were
found. Those counts do not cancel any failed condition. `reasons` says that
before-run processor samples and environment evidence were missing; the retry
history was invalid; the calibration observations taken around the measured
work were missing; the check comparing a known repeated workload at the start
and end was missing; at least one member directory was invalid; and the runner
could not prove the intended campaign membership, meaning the scheduled list
of member directories for this campaign. `status: failed` is therefore the
only defensible result.
The surrounding artifact explicitly marks its computed values as diagnostic,
not evidence for a capstone statement.

## A retained close-out refusal

A retained execution report from a deliberately discarded rehearsal run — one
performed only to make the pipeline fail on purpose and record how it fails —
has `L10` in its real filename; that fragment is an internal review-seat label
with no instrument meaning. The report at
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L10-SACRIFICIAL-FULL-LIFECYCLE-report.md`
summarizes two earlier refusals from the duration-recorder script without their
detail text:

```json
{"reason": "pack_identity_invalid", "status": "REFUSE"}
```

Current code always emits `detail`, so do not treat the
two-field quotation as the current output schema:

```json
{"detail":"<run-specific explanation>","reason":"pack_identity_invalid","status":"REFUSE"}
```

`reason` says the operator-supplied pack identity did not equal the identity
derived from the prepared plan. A **pack identity** is the plan-derived name
that binds the prepared files to the intended measurement. `status` says the
script stopped and wrote no duration receipt. The retained quotation contains
no `detail` field; the current-schema example above uses a placeholder rather
than inventing run-specific text.

## What you should now be able to do

- Find a member failure in `summary_metrics.json` and a window refusal in
  `campaign_log.jsonl`.
- Separate the stable reason code from its run-specific detail.
- Translate the common run and whole-window codes into physical or procedural
  causes.
- Walk through a refusal object field by field without treating member counts
  as permission to ignore a failed condition.
- State why a refusal must be preserved rather than retried, and name the file
  to which its reason code was written.
