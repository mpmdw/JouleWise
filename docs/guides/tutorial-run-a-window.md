# Run one diagnostic measurement window

This tutorial takes a clean checkout — repository files with no local edits —
through the smallest committed production-shaped campaign: a scheduled run
that uses real components rather than substitutes. It runs the model with
MLX, Apple's machine-learning runtime, while macOS `powermetrics`, a program
that records processor power, measures it. A **measurement window** is the
uninterrupted period in which the Mac is prepared, left untouched, measured,
checked, and backed up. A
**verdict** is the runner's recorded `passed` or `failed` decision after it
checks the resulting files. This window produces a real verdict, but it is
**diagnostic**: it tests whether the instrument's collection plumbing works.
It is not **claim-bearing**, meaning its result may not be used to support a
capstone conclusion about model energy. A planned, roughly 20-minute
end-to-end route is shorter, but it has no operator card yet, so it is not the
route taught here.

This tutorial is a procedure, not permission to collect. Before using it,
confirm that the current project status and the reviewed run card both say the
quiet-machine lane may proceed. If either says stop, do not arm or sample.

There is an important boundary in the current checkout. The committed
one-member campaign and its verdict are driven by `scripts/run_campaign.py`.
The newer `scripts/launch_window.py` accepts only a separately prepared,
fixed window pack — a directory whose exact files and commands were recorded
before measurement — plus an arm receipt recording that the pre-start checks
passed, a retained arming directory, and a launch manifest containing the
exact command to execute. The checked-in shakedown card describes a
known-workload timing capture and does not connect those launcher inputs to
the one-member campaign below. Do not point the launcher at the campaign directory or invent
the missing inputs. The final section shows the launcher's real command
surface so that you can recognize the handoff when an operator card supplies
those files.

## Prerequisites and installation

Use a Mac with Apple Silicon. The project requires Python 3.11 or later. The
configured model must already exist at the local path recorded in
`configs/campaigns/p2_015_smoke/production_shakedown/p2038_production_shakedown.json`;
do not silently substitute another model, because that would change the
experiment.

From the repository root, confirm that the checkout has no modified or
untracked files, then create the local Python environment and install the Mac
dependencies under the recorded constraints, which limit packages to the
versions recorded for this measurement environment:

```sh
git status --short --branch
python3 -m venv .venv
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
```

The sampler needs administrator rights. The repository documents a macOS
`sudoers` rule — a rule controlling which privileged command may run without
a password — limited to `/usr/bin/powermetrics`; collection then uses
non-interactive `sudo` instead of stopping mid-window for a password. An
administrator must install that rule outside this tutorial. Verify the
installed permission without starting the sampler:

```sh
sudo -n -l /usr/bin/powermetrics
```

If that command refuses, stop. Do not begin a window and do not broaden the
rule to unrelated commands.

## Prepare a quiet Mac

Power drawn by a browser tab, cloud synchronization, a backup, indexing, an
agent, or an awake display is physically mixed into the same processor power
samples as the model. That extra work can therefore look like model energy.
Connect the charger; finish or pause backups, updates, downloads, indexing, and
cloud uploads; close agents and browser automation; then leave the Mac
untouched for at least 10 minutes so idle-triggered maintenance can run before
measurement. Run the reviewed preparation script yourself; it closes
nonessential visible applications, reports rather than kills background
work, checks AC power and sampler permission, and requests transient display
sleep. It does not change persistent display settings.

```sh
bash scripts/quiet_mac_prep.sh
```

Read every line. Correct any `FAIL` before continuing. After this point, do
not touch the keyboard, trackpad, or display until the runner finishes.

## Understand the one-member configuration

The configuration schedules one repetition. It asks for power samples at
10 Hz — ten samples per second — records 30 seconds of idle power, and allows
5 seconds after warm-up.
The idle samples show what the already-on Mac consumes without the measured
request; the warm-up delay keeps model loading and first-use effects out of
the measured request. These are configured inputs, not numbers to tune after
seeing a result.

The physical and file flow is:

```text
[operator prepares Mac]
          |
          v
[runner arms display sleep and re-checks the machine]
          |
          v
[MLX runs the model while powermetrics samples processor power]
          |
          v
[run bundle: raw samples + event times + derived summary]
          |
          v
[shakedown gate (automated pass/fail check): strict check (rebuild and compare) -> independent reduction
 (recompute the summary from stored evidence) -> strict check -> evidence
 checks -> backup]
          |
          v
[campaign log: passed or failed verdict]
```

Square brackets name real stages, and each downward arrow means the next stage
starts only after the preceding stage finishes. A **run bundle** is the
directory containing the configuration, event times, raw sampler records,
parsed power trace, model
output, metadata, and `summary_metrics.json`. The last file is the marker that
the bundle finished.

## Arm and run the window

First confirm the runner's current options. This is safe before the quiet
period because help mode does not measure anything:

```sh
.venv/bin/python scripts/run_campaign.py --help
```

The **arming step** is the final transition from an interactive computer to
an untouched measurement machine. `--arm-quiet-mode` counts down, asks macOS
to sleep the display, and re-checks power, display, screensaver, thermal, and
background-load conditions before the member starts. The explicit 20-second
countdown gives you time to step away. Run this as the operator, not from an
agent session. `caffeinate -is` is the macOS utility that prevents idle system
sleep while the command runs without forcing the display awake:

```sh
/usr/bin/caffeinate -is .venv/bin/python scripts/run_campaign.py \
  configs/campaigns/p2_015_smoke/production_shakedown \
  --runs-dir runs/window_a_shakedown \
  --log runs/window_a_shakedown/campaign_log.jsonl \
  --backup \
  --shakedown-gate production_uncertainty_v1 \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json \
  --arm-quiet-mode \
  --arm-countdown-s 20 \
  --max-failures 1
```

Do not invent successful output. The run needs the physical Mac, the local
model, and administrator-authorized sampling, so this tutorial cannot predict
what your machine will report. A refusal is also a valid diagnostic result:
preserve it, read its reason, and do not rerun until the physical cause is
understood and removed.

## Find and read the verdict

The bundle lands at
`runs/window_a_shakedown/p2038-production-shakedown/`. The append-only runner
record — a log that gains new rows without rewriting old rows — lands at
`runs/window_a_shakedown/campaign_log.jsonl`. With bare
`--backup`, the runner calls `scripts/backup_runs.sh`, whose default
destination is `~/JouleWise-backup/runs/`.

In the campaign log, find the JSON object — a set of named fields and values — whose `record_type` is
`shakedown_gate` and whose `gate` is `production_uncertainty_v1`. `status:
passed` means the bundle passed strict checking, an independent reduction,
strict checking again, the production-evidence checks, and backup. `status:
failed` means `code` and `detail` name the failed stage. Passing proves only
that this diagnostic path worked for this run; it does not license an energy
claim. For the deeper distinction between a verifiable bundle whose derived
files can be rebuilt from its raw records, an admitted bundle allowed into a
later evaluation, a decision covering every member in a measurement window,
and a decision about what the capstone may state, continue with
[`instrument-guide.md`](instrument-guide.md).

## Where the guarded launcher fits

When a reviewed operator card supplies a fixed pack and all retained inputs
named below, the physical entry command has this parser-verified form, meaning
the current software that checks command-line flags accepts every flag. The
confirmation table records the independent human review of the prepared
family, and the confirmation fingerprint is the previously retained SHA-256
digest — a compact value that changes when the table's bytes change. It must
come from that earlier review, not be recomputed from the file at launch time.

```sh
.venv/bin/python scripts/launch_window.py \
  --pack-root "$PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST" \
  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
```

That launcher consumes a single-use authorization — a permission record that
cannot be reused — and replaces itself with the exact command stored in the
launch manifest. It is not a shortcut around the preparation above, and the
current checkout does not supply these inputs
for the one-member campaign. Use it only from the operator card that created
and names every shell variable in that command.

## What you should now be able to do

- Explain why the diagnostic result cannot support a capstone claim.
- Verify Python, Mac dependencies, and non-interactive sampler permission.
- Remove avoidable machine activity and recognize a failed quietness check.
- Identify the arm step and run the committed one-member campaign.
- Locate the run bundle, backup, and append-only verdict record.
- Distinguish the campaign runner from the guarded fixed-pack launcher.
