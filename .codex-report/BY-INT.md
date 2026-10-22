# BY-INT — BYTES pass-1 integration

## SUMMARY

Integration in progress on `lane/2026-10-22-bytes-pass1`.
Verified B2 base `0743a7b90c70f896f0cf82551d4e2ac33b9b1f02`.
B4 is merged first, preserving NR1 and Q1/Q2.
Only synthetic fixtures are authorized; every run sets `JW_B5_SYNTHETIC_ONLY=1`.
No measurement window, launch job, production pack state, or main push is authorized.

## MERGES

1. B4 `0b6023dcc`: pending merge commit (this commit). Conflict: `tests/fixtures/bytes/campaign.py`, two hunks. Combined B2's fixture defaults and synthetic-parameter manifest (unequal durations, signed clock latency, 50 ms sample phase, independent random edge phase, 10 ms minimum arrival latency, reference drift) with B4's `subpack_sessions` / `uncollected_sessions` and configuration keys. Governing: Addendum 7 item 12 and Addendum 8 item 4 (`docs/design/bytes_pack_design.md` at `298a292a7`); `docs/process_traces/2026-10-21-magistrate-a017b694/B2-NR1-RULING.md` items 1, 3, 5; `docs/process_traces/2026-10-21-magistrate-283e9802/B2-NR1-COLD-DISPOSITION.md` M1; `docs/process_traces/2026-10-20-magistrate-af419b16/B6-RULING.md` Q1 and Q2; `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md` blinding ruling items 1–3. Other paths merged automatically; generated drafts came from the B4 generator output.
2. B3 `0c04bb181`: pending.
3. H `c10b6895f` exactly (including B5 `20e6984c9`): pending.
4. Manifest/KV `99c9099d8`: pending.
5. Registration `91b20d7c2`: pending.
6. Regeneration: pending.
7. `origin/main`: pending.

## GENERATED

Pending final generators and reproduction checks.

## B4 OPEN ITEMS

Pending Q2 regression, catalog SHA, and README correction.

## TESTS RUN

Seat setup ran; zsh 5.9 and Python 3.13.5. Its `/opt/homebrew` mkdir lacked Unix ownership. Created only the requested Python symlink through the managed local Docker daemon, mounted only `/opt`; `/opt/homebrew/bin/python3.13 --version` succeeds. No test run yet.

## END-TO-END

Pending CLI stage chain and scratch-only `open_packs`.

## CI

Draft PR pending first push.

## DECISIONS I MADE

- Combined orthogonal fixture controls; kept B2's ruled stress settings instead of B4's older equal-duration defaults.
- Preserve C_j as pass-averaged joules divided by mean decode time (M1); Q1 missing-file pass flags and survivor fallback; Q2 fixed-module evaluation of committed content with disclose-only provenance flags.
- User write scope overrides repository end-of-work bookkeeping and whole-suite instructions. No unrelated files will be edited and no full suite will run locally.

## OPEN ISSUES

Remaining integration steps and acceptance checks are in progress.

## NEEDS_RULING

none
