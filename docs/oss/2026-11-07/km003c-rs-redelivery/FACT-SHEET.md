# km003c-rs: a re-delivery longer than 8 samples is integrated twice

Facts only, gathered read-only on 2026-11-07, for Ed to restate in his own
words. Nothing here has been built, run or posted. Plan item: §4.D of
`docs/research-audits/2026-11-07/oss-contributions.md` (branch
`origin/research/2026-11-07-oss-contributions`).

## Upstream and pin

- Repo: https://github.com/okhsunrog/km003c-rs. It is the original repo, not
  a fork. The maintainer is okhsunrog (Danila Gornushko, per the `Cargo.toml`
  authors field), with 341 commits. Three other contributors have 1-7 commits
  each; dependabot is one of them.
- License: MIT OR Apache-2.0 (`Cargo.toml:15`, plus `LICENSE-MIT` and
  `LICENSE-APACHE`). There is no CONTRIBUTING file and no CLA.
- Pinned commit: `71f69e4a35c1184cc114a62145b8a8241d3e13e9`. It is the tip of
  `main`, pushed 2026-11-04 ("Capture PD messages and ADC samples together in
  the CLI"). Re-checked via the GitHub API on 2026-11-07: still the tip,
  `pushed_at` 2026-11-04T17:32:04Z, `open_issues_count` 0.
- `km003c-lib/src/measurement.rs` at the pin is git blob
  `4348b4d8b1efe1d0c6434c282c4bc60f520379e9`, sha256
  `444c07e571c6df00c4f6eafeb41c8e8efd0dd2bccd2ccc3ed2d3cdf7a021bf86`.

## The problem

`MeasurementAccumulator::push()` (`km003c-lib/src/measurement.rs:104-195`)
places AdcQueue samples on device time and integrates charge and energy.
Sometimes the meter sends a run of samples a second time. If that run is
longer than `MAX_CONSECUTIVE_REJECTED_SAMPLES = 8`, the accumulator restarts
continuity partway through the run. It then accepts the rest of the run again
and integrates it a second time.

This has three effects:

- Elapsed device time comes out too long.
- Signed and throughput charge and energy count the integral over the
  repeated stretch twice.
- The repeated samples appear twice in the accepted stream. That stream feeds
  the egui and Slint plots, the CLI `pd capture --adc` CSV, and recordings.

## Evidence that the meter re-delivers samples

1. **The maintainer's own note.** `km003c-egui/WEB.md:262-267` was added in
   `11f054b` (2026-10-19, PR #54). It says a 336.55 s recording had "8
   discarded sequence samples and two non-unit sequence transitions. One
   repeated older sequence block was accepted after the accumulator's
   resynchronization threshold". The PR #54 body says this "remains
   documented as a limitation".
2. **The JouleWise capture.** This is
   `tests/fixtures/km003c/redelivery1000_slice.jsonl` on JouleWise `main`
   (sha256 `0a9978ae4080c4001c7b6b8cfaa3ea7965b60c57b8bd160f2e381a13cfa933ca`).
   It was recorded at 1000 SPS with 30 polls 40 ms apart, and holds 1227
   samples in 30 transfers.
   - Transfer 14 carries sequences 49772..49816.
   - Transfer 15 carries 63 samples. Its first 27 are 49790..49816, which are
     byte-identical copies of the last 27 samples of transfer 14. It then
     continues with 49817..49852.
   - Every other step is +1. The capture holds 1200 unique samples, from
     49250 to 50449.
   - 63 is the largest transfer in the capture. The upstream comment at
     `adcqueue.rs:114` says "5-48 samples".

## Minimal repro

The repro is synthetic: 1000 SPS, with every sample at a constant 5 V and 1 A.

1. Push 49790..=49816 (27 samples).
2. Push 49790..=49816 again.
3. Push 49817.

**Correct result:** every sample in step 2 is rejected. Sample 49817 has
`elapsed_us` 27 000, energy 37.5 µWh and 27 discarded samples.

**Result at the pin (hand trace):**

- 49790..49797 are rejected. The 8th rejection sets `previous = None`.
- 49798 is accepted as a new start, with delta 0.
- 49799..49816 are accepted again and integrated again.
- Sample 49817 lands at 45 000 µs with 62.5 µWh.
- 19 repeated samples are emitted, and only 8 are counted as discarded.

The observed sequence shape is 49250..=49816, then 49790..=50449:

| | elapsed | accepted | discarded |
|---|---|---|---|
| correct | 1 199 000 µs | 1200 | 27 |
| at the pin | 1 217 000 µs | 1219 | 8 |

On the real samples the pin integrates 18 intervals twice, adding 1.30 J
(the slice's mean power is 73.3 W). The kit author computed this from the
capture's own sample values, without running any upstream code.

## Root cause (pinned commit)

- `measurement.rs:18-24`: `MAX_CONSECUTIVE_REJECTED_SAMPLES = 8`. Its doc
  comment explains why it exists: after a stall the 16-bit, 1 kHz counter can
  wrap, and the next sample then looks out of order. It was added as a fix
  for a stall of about 33 s at 2 SPS (`CHANGELOG.md:165-168`).
- `measurement.rs:118-121`: a backward step of k ticks shows up as
  `delta_ticks = 65536 - k`, which fails
  `delta_ticks <= max_forward_sequence_ticks(rate)` (`:32-35`). An exact
  duplicate gives `delta_ticks = 0`, which fails `delta_ticks != 0`. Either
  way the sample is rejected.
- `measurement.rs:127`: every rejected sample increments
  `consecutive_rejected_samples`. A re-delivered sample and a sample after a
  long stall are counted the same way.
- `measurement.rs:132-135`: at 8, `previous = None`.
- `measurement.rs:116`: the next sample takes the `None => (0, 0)` arm. It
  becomes a new continuity start in the middle of the re-delivered run.
- `measurement.rs:139-157`: the remaining re-delivered samples step +1 from
  that start, so they pass the check. They are integrated (`:148-155`) and
  added to `elapsed_us` (`:157`).

**Size of the error.** Take a re-delivered run of N samples that ends with a
copy of the last accepted one.

- For N ≥ 9, the pin rejects 8 samples and accepts N − 8 again.
- It adds N − 9 extra sample periods to elapsed time, and integrates charge
  and energy over them a second time.
- For N ≤ 8 there is no time error.
- The observed event had N = 27: +18 ms and 19 duplicate rows.

**How often it happens:**

- The JouleWise slice was cut to contain the event, so it gives no rate.
- The maintainer's note suggests one such event in his 336.55 s recording.
- Behaviour at 2, 10 and 50 SPS is unknown.

## Proposed fix (`fix.patch`)

The patch adds 32 lines and touches only `measurement.rs`.

- A new constant `MAX_REDELIVERED_SAMPLES = 64`.
- A new function `is_redelivered(previous, current, rate)`. It returns true
  when a rejected sample lies exactly on the sample grid
  (`behind_ticks % step == 0`) and at most 64 samples behind the last
  accepted one (behind 0 means a duplicate).
- In `push()`, such a sample is still rejected and still counted in
  `discarded_sequence_samples` and `cumulative_discarded_sequence_samples`.
  It no longer increments `consecutive_rejected_samples`, so it cannot
  trigger the restart.
- Nothing else changes. A stall that lands far behind still restarts after 8
  samples. The existing test `continuity_restarts_after_a_run_of_rejected_samples`
  (`:422-448`) puts its rejected samples 25 535 ticks behind, which is more
  than 64.

**Why the grid check matters.** Re-delivered samples are exact copies, so
they always sit a whole number of steps behind.

- At 2, 10 and 50 SPS the step does not divide 65536 (the remainders are 36,
  36 and 16). A stall therefore ends off the grid, unless it lasts a multiple
  of 125, 25 or 5 counter wraps (about 2.3 h, 27 min and 5.5 min).
- At 1000 SPS the step is 1 and every position is on the grid. There only the
  64-sample window separates a re-delivery from a stall.
- At the slower rates the window is wide in ticks: 64 samples is 32 000 ticks
  at 2 SPS, 6 400 at 10 SPS and 1 280 at 50 SPS. A rejected sample at 2 SPS is
  always less than 33 036 ticks behind, so at 2 SPS nearly every on-grid
  rejected sample counts as re-delivered, and the restart there rests on the
  grid argument alone.

**Coverage.** The fix handles re-delivered runs of up to 72 samples. Any
window of 19 or more fixes the observed N = 27.

**A wider alternative, not in the patch.** The plan names a high-water mark of
unwrapped device time, with host arrival time to tell a stall of more than
half a wrap from a re-delivery. `push()` has no host time today, so this
would change the public API. That choice belongs to the maintainer.

## The tests (`failing-test.patch`)

The patch adds 45 lines, only in the `measurement.rs` tests module. It adds
two `#[test]`s that use the module's existing `sample()` helper (the second
feeds the accumulator from a plain `for` loop rather than an iterator chain
ending in `.last()`, to stay clear of clippy's `double_ended_iterator_last`):

- `a_redelivery_longer_than_the_restart_threshold_is_not_integrated_twice`
  is the synthetic repro above. At the pin its first assertion should fail
  with `left: 45000, right: 27000`.
- `an_observed_1000_sps_redelivery_keeps_device_time` replays the captured
  sequence numbers only, with no sample values and no device identifiers.
  At the pin it should fail with `left: 1217000, right: 1199000`.

Predicted `cargo test -p km003c-lib --lib measurement::tests` output:

- At the pin: `8 passed; 2 failed`.
- With the fix: `10 passed`.

These outcomes come from a hand trace and have not been observed.

Other in-repo callers keep their current results, by hand trace:

- `km003c-cli/src/pd.rs:606-610`: a duplicate 44 at 50 SPS is still one
  discarded sample.
- `km003c-egui/src/gpu_plot.rs:508-514` and the hardware-only
  `recording/writer.rs:424` test only feed increasing sequences.

## Risk

- **Behaviour change.** Every re-delivered sample now counts as discarded
  (8 → 27 for the observed event), and duplicate rows no longer reach plots
  or recordings. `WEB.md:265-267` would then describe the old behaviour.
- **Stalls just short of a whole wrap (1000 SPS).** If a stall lasts up to
  64 ms less than a whole number of counter wraps (65.536 s each), its first
  new sample lands 0-64 ticks behind the last accepted one. The patched code
  then drops up to 65 samples one by one, instead of restarting after 8.
  The time across such a stall is lost either way: a restart adds 0 and the
  fix adds one step.
- **Longer re-deliveries.** Runs longer than 72 samples still restart and are
  still integrated twice.
- **Unverified build.** The patches apply cleanly to the pin. This was
  checked with `git apply --cached` on a scratch index; nothing was checked
  out. They are rustfmt-clean with the repo's `max_width = 120` (rustfmt
  1.9.0). They have not been compiled, clippy-checked or tested. A second
  agent repeated the apply (both orders give blob `8a7babec…`) and the
  rustfmt check, and re-traced both tests by hand to the same numbers.
- **Hardware confirmation.** The maintainer will probably ask for checks at
  50 and 1000 SPS on real hardware. Only Ed can supply them.

## Related, out of scope

- **CLI statistics.** `km003c-cli/src/adc.rs:124-135` (`adc stream`
  statistics) never rejects a sample. A step back of 26 adds 65 510 ticks to
  elapsed time and warns "65509 samples dropped". No energy is integrated on
  that path.
- **Protocol-research docs.** `adcqueue.md` in km003c-protocol-research
  documents a `(seq - last) & 0xFFFF` drop count (per the plan). It reads a
  re-delivery the same way. This is the separate docs PR.

## Corrections to the plan's §4.D

- **Severity formula.** The plan says "(N − 8) sample periods". The trace
  gives N − 9 periods (N − 8 repeated samples). The +18 ms for N = 27 in the
  plan agrees with N − 9.
- **Python package.** The plan says "PyPI km003c 0.4.0 … carries the same
  bug". At the pin, the Python module (`km003c-lib/src/python.rs`, module
  init from `:377`) registers no `MeasurementAccumulator`. Neither
  `python/km003c/` nor `test_bindings.py` mentions it. Python users never
  run this code path.
- **Novelty.** The plan says there is "no report of the bug". That holds for
  issues: there are 66 issues and PRs, none open, and none matches
  "redeliver", "continuity" or "resynchron". But the symptom is already
  documented by the maintainer (`WEB.md:265-267`, PR #54). What is new is the
  mechanism, the cost per event, a failing test and a fix.

## Static review

Reviewer verdict (independent read-only static review, 2026-11-07): **ready-with-caveats**. Nothing upstream was executed, built, installed or imported; the kit has not been run (status UNRUN).

Review text as relayed to the lead by the workflow. The relay cut the text off partway through, so it ends mid-sentence; any corrections the reviewer made are already in the kit files above.

```text
VERDICT: ready-with-caveats

WHAT I CHECKED (read-only; nothing upstream executed, built or imported)
- Bug is real as described. Re-read km003c-lib/src/measurement.rs at 71f69e4a (blob 4348b4d8…). Lines 24, 116, 118-121, 127, 132-135, 139-157 are exactly as the fact sheet cites. Hand trace of the synthetic repro: pin accepts 49798 as a delta-0 restart, re-integrates 49799..49816, lands 49817 at 45 000 us / 62.5 uWh / 47 accepted / 8 discarded; correct is 27 000 / 37.5 / 28 / 27. Observed-sequence trace: pin 1 217 000 us, 1219 accepted, sample_index 1218; fix 1 199 000, 1200, sample_index 1199, 27 discarded. All match the kit. N-9 severity formula confirmed.
- Maintainer evidence confirmed: km003c-egui/WEB.md:262-267 text matches; GitHub API: PR #54 body says "acceptance of a repeated older block after resynchronization remains documented as a limitation", merged 2026-10-19. Pin is still the tip of main (pushed_at 2026-11-04T17:32:04Z); open_issues_count 0; issue search for redeliver/continuity/resynchron/duplicate finds only closed PRs.
- Patches apply to the pin: `git apply --cached` on a scratch index (GIT_INDEX_FILE in my scratchpad, no checkout), both orders, identical blob. Hunk contexts and line offsets (23/32/124 -> 23/43/148) verified by eye against the numbered source.
- Fix addresses the root cause: redelivered sample (on-grid, <= 64 samples behind, incl. behind 0 duplicate) is still counted in both discard counters but returns before `consecutive_rejected_samples` increments, so the restart cannot fire mid-run. Existing tests re-traced: restart test (25 535 behind) still restarts; duplicate/out-of-order test (behind 0 and 10) still 2 discarded; cli pd.rs:606-610 duplicate 44 at 50 SPS still 1 discarded. Grid arithmetic (65536 mod 500/100/20 = 36/36/16; wraps 125/25/5) checked. `u16::is_multiple_of`, `wrapping_sub`, Copy `GraphSampleRate` all already used in the file; MSRV 1.97 fine.
- Fixture: JouleWise origin/main redelivery1000_slice.jsonl sha256 0a9978ae… matches; first batch record decodes to sequence 49250 at the offsets model_push.py uses (k:"b", p: hex, 20-byte samples).
- Contribution rules: no CONTRIBUTING/CLA; README:543-545 "Contributions welcome!"; license MIT OR Apache-2.0. CI gates: fmt, test and clippy -D warnings with --all-targets and --all-features, doc -D warnings, MSRV 1.97, edition 2024, Keep-a-Changelog Unreleased section. rustfmt.toml = max_width 120 only.
- Local toolchain: /opt/homebrew/bin/{cargo,rustc,cargo-fmt,cargo-clippy,rustfmt} -> Cellar/rust/1.97.1; ~/.rustup exists but no ~/.cargo/bin, so `which cargo` is Homebrew's. RUN-ME's toolchain story holds.

CORRECTIONS APPLIED (all under /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/)
1. failing-test.patch: second test used `(..).chain(..).filter_map(..).last()`. That is a DoubleEndedIterator, and clippy's `double_ended_iterator_last` (warn-by-default since 1.86; both CI and `repro.sh regress` use -D warnings) can fire even though `next_back()` would be sema
[relayed excerpt ends here]
```
