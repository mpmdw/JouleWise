# F2 product queue and qualification-pin drafts, 2026-11-18

Tier 0, synthetic verification. Mission M0 found no active stop card. The direct builder brief selected the audit-line product drafts under RUN_STATE items 422 and 425. After fetching, the clean seat was already at the F2 pieces commit `e26a566c1f2c9eaf12e47f75bb6e2facb2eaea46`. That commit was also the fetched audit head.

## Admitted F2 pin

Part 1 was committed and pushed first as `61377dc45e9be3163466ef33e57dc0281423fdbc`. It fills the 14 stability and three finite F2 instrument queues with expiry `2026-11-24T12:35:29-08:00`. The 201 one-leg entries retain their original bytes except for the wrapper's expiry field.

At `2d347f721552fe03bdd19f113e7bad7a7c24908e`, `joulewise/cadence/queue.py:67–75,86–100` parses an ISO timestamp with an explicit offset. Lines 249–254 compare the queue expiry to the current time. The CLI is in `scripts/cadence_queue.py`, and the validation path has no commit-age input. For an unexpired queue, fast-forward by **2026-11-24 12:35:29 PST**. The default expiry is 6 days 12 hours of elapsed time from generation, expressed in America/Los_Angeles.

- PASS, pinned `validate-queue` with the audit checkout as `--kits-root`, 17 of 17 queues and 201 entries.
- PASS, `f2-stab/tools/validate_kit.py` against `f2-inst-01`, 14 of 14 stability kits under each of the two batch-window arguments.
- PASS, three generator regression tests, including byte equality except for expiry for every draft, offset rejection and default expiry across a daylight-saving change. Regeneration with the recorded expiry reproduced the committed folder byte for byte.

The command arguments, outputs and queue hashes are recorded with the filled files. [Filled queue index](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-ready/README.md) · [Verification](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-ready/VERIFICATION.json)

## Qualification pin

Part 2 uses PR #812's then-current head `df261f6a235e976be8859ab5314af737a08f6d7d`. It adds two kits, 24 one-leg item drafts, two queues with expiry `2026-11-24T12:43:05-08:00`, and one appended manifest section.

| Kit | First-hit seed | Candidates | SHA-256 | Work bound | Minimum launch budget | Synthetic mock |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| f2-stab-15 | 2026112669 | 1226 | `45029d6835cac335b9648ef8ed8b8dad8229decc0c637d549d48156026c71e40` | 5,850 s | 8,360 s | L001, exit 0, stops [] |
| f2-stab-16 | 2026113603 | 2160 | `eb5bf2476901825c5eba69d9e92ef8ad6506dad9c7c0f5231ce63acdc8151aec` | 5,850 s | 8,360 s | L001, exit 0, stops [] |

- PASS, ascending first-hit search with the selected pin's `generate_legs`, repeated with that pin's `gen-legs` CLI at each hit.
- PASS, the existing `f2-stab/tools/validate_kit.py` CLI against f2-inst-01 on both pre-pin drafts at `2d347f721` with `--batch-window 02:00-02:35`. That CLI requires the base pin. The builder calls its unchanged `validate_cells` on the same pre-pin layout and verifies that the selected pin's `pin-kit` changes only `frozen`. The selected pin's `validate-kit --repo` then verifies the final bytes and frozen digests.
- PASS, qualification pin's `validate-queue` for both filled queues, first against the staged audit layout and again against the actual audit checkout.
- PASS, `plan --t0 1795032000` on all 24 sole-leg rosters. The 5,850 s work bound holds. The 8,360 s minimum launch budget includes 1,950 s for the soak retry and 560 s for reserves. The issue notes carry forward the shared template's 900 s margin over its pin's minimum. Both `mock --legs L001 --t0-local 2026-11-18T12:00` calls closed with zero stops.
- PASS, two new and four existing stability tooling tests. Regeneration with the recorded pin and expiry reproduced all eight generated files. Both magistrate READMEs fit the 30-line limit.

The focused checks use both pins' actual CLI source and the real kit bytes. The canonical full suite was skipped for this evidence and standalone tooling change. The repository CI workflow is configured for PRs and pushes to main.

The magistrate uses the admitted merged pin after the lead regenerates the drafts. The first native span is a product filler and owes the independent F-3 (c) hand-read on clean close. [Qualification-pin index and prior hand-read template](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/qual-pin/README.md) · [Synthetic verification](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/qual-pin/VERIFICATION.json)

## Lead handoff

Review the linear branch `align/2026-11-18-f2-stab-ready` for fast-forward to the audit line. Regenerate from its checkout root. Set `PINNED_CHECKOUT` to a clean checkout of `2d347f721` for the weekly queues, and set `MERGED_PIN` to the full merged qualification runner SHA once available.

```sh
python3.13 -I -B docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-ready/tools/fill_queues.py --runner-repo "$PINNED_CHECKOUT"
python3.13 -I -B docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/tools/build_qual_pin_kits.py --pin "$MERGED_PIN"
```

**NEEDS_SPEC** — none for the fetched pins.
