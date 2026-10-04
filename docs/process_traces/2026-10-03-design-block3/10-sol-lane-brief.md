# Implementation seat: lane G2A-B3-RETRY-BACKOFF-01 (delayed idle-admission retry for measurement block 3)

Repository worktree: `/Users/edr/code/JouleWise-wt-db3-code` (branch
`feat/2026-10-03-g2a-b3-retry-backoff`, based on main `871a43f6`). Commit your work on this branch
(do not push; the lead pushes). You have licence to disagree with any instruction below; if a rule
here would make the code wrong, stop and say why instead of improvising.

## Why

Measurement block 2 (the G2-a prefill resolvability probe; registration
`configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md`) lost its recovery window `w2`
when member `g2a-small-p2048-r03` failed idle admission twice. Both attempts failed only on
`cpu_busy_ratio_p95_exceeded` during an ≈6-minute macOS maintenance burst. Attempt 2 starts about
0.5 s after attempt 1 (`joulewise/controller.py` around lines 1106-1123), so the one retry cannot
outwait a multi-minute burst. The orchestrator ruled (record
`docs/process_traces/2026-10-03-design-block3/00-design-record.md` on branch
`design/2026-10-03-block3`): a new block 3, whose policy file waits 600 s before the one retry,
with the admission criteria unchanged; production behaviour byte-identical.

## What to build

1. **Policy field.** `joulewise/schemas.py` `IdleAdmissionPolicy`: optional key
   `retry_backoff_s` (a finite, non-negative int or float, not bool, at most 1800; absent means
   0). The production file `configs/campaign_policies/quiet_mac_p2_production.json` must stay
   byte-identical and parse to backoff 0. If `CampaignPolicy` (or anything else) serializes the
   policy into run metadata or hashes a re-serialization, a backoff of 0 must serialize exactly
   as today (omit the key), so no existing digest changes. Check every `to_mapping`/digest path.
2. **Controller wait.** In `joulewise/controller.py`, when attempt 1 is not admitted and its
   post-capture guard passed: if `retry_backoff_s > 0`, wait that long using the controller's
   clock abstraction (`self._clock.sleep`, so FakeClock tests run instantly), then continue
   exactly as today (the `before_attempt_2` guard, attempt 2, the `after_attempt_2` guard, abort
   on a second rejection). Record the wait in the admission record under a NEW key (for example
   `environment_admission["retry_backoff"] = {"requested_s": ..., "start_s": ..., "end_s": ...}`),
   never as an entry in `guard_observations` or `attempts`: `joulewise/environment_admission.py`
   (lines ~430-470) requires exactly the phases before/after each attempt and monotonic attempt
   timing. Nothing else changes: same criteria, exactly one retry, same abort reason text, same
   promotion of attempt 2.
3. **Block-3 policy file.** New `configs/campaign_policies/quiet_mac_p2_g2a_b3.json`: the
   production file with `"retry_backoff_s": 600` added under `idle_admission` and `policy_id`
   `quiet-mac-p2-g2a-b3`; same formatting as the production file (sorted keys, indent 2, trailing
   newline). Check whether any code requires `policy_id`, `profile` or `policy_version` to take a
   specific value (search the package and scripts) and report it; do not change other fields.
4. **G2-a chain uses the block-3 policy.** `scripts/gen_g2_phase_d.py`: the emitted G2-a chain's
   `POLICY` export must point at `$MEASUREMENT_CHECKOUT/configs/campaign_policies/quiet_mac_p2_g2a_b3.json`
   (substitute it the way `integrated_g2a_chain` pins `CALIBRATION_LEDGER`; the runsheet source
   bytes stay untouched; require exactly one substitution). Put the policy's relative path in ONE
   constant that the generator, the span sizing and the tests share.
5. **Span.** `programmed_span_s()` reads the block-3 policy (not production) for its dwells, and
   adds an explicit allowance for delayed retries: `IDLE_RETRY_ALLOWANCE_COUNT = 4` retries, each
   costing `retry_backoff_s` + the member's `idle_seconds` + 30 s (guards and slice overhead).
   Update the comment block above it (keep its style: the formula and the reason). Update the
   pinned span in the tests (`tests/test_gen_g2a_window.py` pins 17248 today) to the new value and
   report the new `NIGHT_PROGRAMMED_SPAN_S` and `ceil((span + 2700)/60)*60`.
6. **Harvest binds the window's own policy.** `scripts/harvest_g2a_window.py` (line ~188, bracket
   policy) and `scripts/generate_g2a_probe_inputs.py` `check_harvest_inputs` (line ~1349) hard-code
   the production policy path. Make both use the campaign policy that the window's input inventory
   binds (`g2a-input-inventory.json` → `campaign_policy.path`, resolved inside the measurement
   root, sha checked by the existing `check` path), refusing a path outside
   `configs/campaign_policies/`. A block-2 window archive must still harvest (its inventory binds
   the production file).

## Audits to report (read, do not change unless in scope)

- Every consumer that might assume attempt 2 follows attempt 1 closely, or that the powermetrics
  stream is short: the adapter keeps ONE sampler live from before attempt 1 through the measured
  window (`joulewise/adapters/powermetrics.py` `begin_admission_window_sampling`,
  `_capture_idle_slice`), so a 600 s wait adds ≈600 s (≈300 MB) of frames to the stream that ends
  up in the member's `powermetrics.plist`. Check strict validation (`joulewise/cli.py` strict
  path), `joulewise/environment_admission.py`, `joulewise/whole_window.py`, `joulewise/reduce.py`,
  `joulewise/uncertainty_evidence.py` (clock-anchor fit: which records does it fit, and does a
  longer stream change its span/rate tests?), the summarizer and harvest. Say for each whether a
  long inter-attempt gap changes any verdict, and how you know (test or code line).
- Any per-member or per-stage wall timeout in `scripts/run_campaign.py` or the controller that a
  600 s wait could hit.
- **You must not edit** `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`,
  `joulewise/adapters/powermetrics.py` or `joulewise/reduce.py` (pinned estimator files). If the
  right fix needs one of them, stop and report.

## Tests

- Schema: absent → 0; valid values; bool, negative, non-finite, > 1800, and string refused;
  production file parses to 0 and its bytes are unchanged; block-3 file parses to 600.
- Controller (FakeClock harness already used by the admission tests, e.g. `tests/test_idle_admission.py`
  or `tests/test_run_campaign.py`): backoff 0 → no sleep and an admission record identical to
  today's; backoff 600 with attempt 1 rejected → exactly one 600 s sleep between attempt 1's end
  and the `before_attempt_2` guard, attempt 2 runs, the record carries `retry_backoff`; attempt 1
  admitted → no sleep; attempt 2 rejected → abort with the same reason; and a bundle produced
  with a backoff passes the same strict admission validation (`environment_admission_refusals`
  and the measured-window check) as one without.
- Generator: chain `POLICY` line names the block-3 file exactly once; the new span literal;
  `--check` still passes.
- Harvest: policy read from the inventory for both a block-3-style and a block-2-style fixture.
- Run: the touched test modules plus `tests/test_gen_g2a_window.py`, `tests/test_harvest_g2a_window.py`,
  `tests/test_summarize_g2a_prefill_probe.py`, `tests/test_generate_g2a_probe_inputs.py` (if it
  exists), `tests/test_idle_admission.py`, `tests/test_schemas.py`, `tests/test_run_campaign.py`
  with `.venv/bin/python -B -m unittest`. If you add or change a file read by the custody replay,
  update `tests/fixtures/custody_read_replay_allowlist.json` the way commit 9e2b1004 did and run its
  consuming test.

## Write scope (exhaustive)

WRITE_SCOPE: ["joulewise/schemas.py", "joulewise/controller.py", "configs/campaign_policies/quiet_mac_p2_g2a_b3.json", "scripts/gen_g2_phase_d.py", "scripts/generate_g2a_probe_inputs.py", "scripts/harvest_g2a_window.py", "tests/test_schemas.py", "tests/test_idle_admission.py", "tests/test_run_campaign.py", "tests/test_gen_g2a_window.py", "tests/test_harvest_g2a_window.py", "tests/test_generate_g2a_probe_inputs.py", "tests/test_controller_retry_backoff.py", "tests/fixtures/custody_read_replay_allowlist.json"]

Never write under `/Users/edr/night-g2a`, `/Users/edr/night-custody`, `/Users/edr/night-archive`.
Never run powermetrics, sudo, launchctl or a model. Do not read any `summary*.json`, `counts*.json`
or `selection*.json` under those roots (registration blindness).

## Report

End with: files changed; the commit sha; the new span and window values; each test command with
its pass count; the audit table (consumer → effect of a long inter-attempt gap → evidence); and any
finding outside scope.
