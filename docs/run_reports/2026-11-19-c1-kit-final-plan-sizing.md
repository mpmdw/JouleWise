# 2026-11-19 C1 filled-plan sizing rehearsal

Row 21 · Tier 0 · synthetic build and CI handoff. The final C1 plan, disk
reservation, admission, and kit remain open. Item 471 reserves W1 promotion
to the lead.

## Pins and scope

| Role | Ref or commit |
|---|---|
| Authoring base and PR target | `origin/ops/2026-11-11-w1-presign` at `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, tree `c904864e46879a4adfbdf0b467d4da1ee5928285` |
| Separate draft branch | `align/2026-11-19-c1-kit-final-plan-sizing` |
| Synthetic regression | `86163a75db39120f489022fadd4e8895052a0869` |
| Rulings and prior handoff | `origin/audit/2026-11-10-fable` at `c39ec79931db9da0155cc39623ca9f581e4aebb7` |
| Prior pending-W1 rehearsal | PR #844 head `4eb6a3350420ec4c6bb4081b222f85082f9d3a07`, merged at `188014f9589ca1e7fca779ff85ac1e6595e9f456` on the audit line |
| Process | `origin/main` at `366dcf9c8dc8622e07a90714d9033dbfbf5fa842`, `docs/process/PIPELINE.md:10–18,36–64` |

The worktree started clean at the W1 pin. The assigned remote branch and
PR were absent at intake. Mission M0 found no active stop card. The Row 21
dispatch selects this desk-only check. RLD 15504–15514 sets the escalated
form and gives C1 sizing to the lead. RLD 19784–19787 owns the separate
W1-signing and C1-arming gates. P4 940–949, 1006–1033 and 1324–1361 define
the C1 shape, escalation and seeded positions. [Research rulings](https://github.com/mpmdw/JouleWise/blob/c39ec79931db9da0155cc39623ca9f581e4aebb7/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L15504-L15514) · [P4 at the W1 pin](https://github.com/mpmdw/JouleWise/blob/b2e01464d6d4fbf2901ff4d4154df9455104a12a/docs/align/pilot_protocol_v4.md#L1006-L1033) · [PR #844 handoff](https://github.com/mpmdw/JouleWise/blob/188014f9589ca1e7fca779ff85ac1e6595e9f456/docs/run_reports/2026-11-18-c1-kit-and-ready-handoff.md#L11-L62)

## Entry points and verification

The test uses a temporary Git repo with invented scaffold, mock configs,
registration markers and tagged blobs. It uses standard package imports.
The manifest is produced by the public `candidate` subcommand. The CLI
passes exercise `series.main` → `series.generate` → `series.build_files`
with the W1 plan absent. Ordinary and escalated C1 have the same first
22 members. The escalated plan has ordinals 1–24, anchors 1–4, midpoint
after 11 (stage counts 11 and 13), sentinels at 5/22/23/24, and sixteen
fresh members at 6–21. There are seven benign and one seeded instructed
member per pair, with instructed ordinals 6 and 11. Ordinals 23/24 replay
W1:5 as supplemental diagnostics and count toward nothing.

The filled passes call `series.derive_sizing` on the actual
`plan_tree.json` and `collection_plan.json` emitted for each form. The
real `w1.read_w1_plan_bytes` reads invented bytes written to `w1.W1_PLAN`
in that repo. The minimal W1 plan has six rows. The full kit generator
routes a present W1 plan through the W1 validator and requires further
registration inputs, so the filled passes use the sizing helper.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_v4_series_r20.C1FilledPlanSizingTests
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --root "$fixture"
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --extra-sentinels 2 --root "$fixture"
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --extra-sentinels 2 --root "$fixture" --check
git diff --cached --check
```

The focused command creates its own fixture and passed all three tests.
For the separate script CLI readback, `$fixture` was an empty disposable
Git root initialized with `tests.git_fixture.init_git_fixture` and populated
by `C1FilledPlanSizingTests.seed_materializer`. The ordinary and escalated
materializations and the clean `--check` exited 0. Flipping one byte of the
escalated `registration/sizing_b5.json` produced exit 1 with
`ValueError: series kit drifted`. The focused test checks the same refusal
at `series.main` and verifies the edited bytes survive the refusal.

The Python test change requires the hosted Python 3.13 sharded suite. The
docs-only shortcut is inapplicable. Local verification used the named
synthetic class. Broad local discovery would include installer and real
process-signal test paths outside this seat's authorized scope.

## Synthetic sizing readback

The toy disk law is intercept 1, slope 1, largest positive residual 0 and
scaffold 1 byte. Filled anchor seconds are 100/110/120/130, so their upper
bytes are 101/111/121/131. Every non-anchor, including all sentinels, uses
the largest D row and upper bytes `ceil(1 + seconds)`. Each footprint is
`2 * (sum(member_upper_bytes) + 1)`.

| Form and input | Members | D max (s) | Programmed span (s) | Window max (s) | Ceiling (s) | Two-copy bytes |
|---|---:|---:|---:|---:|---:|---:|
| Ordinary, 400/600 | 22 | 600 | 16,255 | 33,960 | 59,520 | 22,566 |
| Escalated, 400/600 | 24 | 600 | 17,455 | 35,160 | 62,400 | 24,970 |
| Escalated, 400/700 | 24 | 700 | 19,455 | 37,200 | 62,400 | 28,970 |

- The 400/600 input SHA-256 is
  `b0ab8ca29ddd403e2a13842781d736fbf2718de9cc12373af3d8ff9b4137fcb4`
  in both forms. The 400/700 input SHA-256 is
  `0ec339ab969e5df4452238648c24bae4fff3595aa23d8f4f868d448df04c9ceb`.
  Each `sources.w1_plan_sha256` matches the raw fixture bytes. The filled
  packs have empty `flags`, and an unchanged input repeats the same
  serialized sizing bytes.
- With no plan, the emitted sizing carries a null `w1_plan_sha256` and
  `sizing.planning_allowances_pending_r1_w1_plan` in `flags`. The pending
  allowances are `3131.27 / 4` s per anchor and `1800` s per other member.
- The 400/1,801 fixture raised `ValueError` with `a member exceeds
  1,800 s`. The diagnostic's computed window maximum was 59,220 s,
  below 62,400 s, so this case isolates the member cap.

## Condition 13 blob comparison

Git tree metadata showed all ten paths present on the base. Each branch
blob ID matched `b2e01464d`. No inherited absence or mismatch surfaced.

| Path | Blob ID on base and branch |
|---|---|
| `scripts/align_r1_rehearsal.py` | `33c6876e6a988bee93fc49a0ba554f7c2c3bf277` |
| `scripts/align_r1_runtime.py` | `96b249a6eb44c4de2887aeeadff089c3040d8cfa` |
| `joulewise/align/apple/r1_runtime.py` | `261761f1a5e39220614b74d53d125022278502db` |
| `joulewise/align/apple/r1_runtime_contract.py` | `1ef822bee6d3b4951ad24cd1991ea31741d30161` |
| `joulewise/align/apple/smc_enumeration.py` | `8a1a96dcb10ebb16809717af15918d5366b0d31c` |
| `joulewise/align/apple/thermal_gates.py` | `b46769d70df02de09dbeb07e4c0020c472477dcb` |
| `configs/align/v4/r1_runtime.json` | `bf8479b26774b4d6a7bb3d44c6e2d662ddeb199e` |
| `joulewise/align/apple/r1_phase_table.py` | `e412bb4389aae4e4239b47842512db178d4b53a2` |
| `joulewise/align/apple/workload.py` | `ff30c29178ad9ccceab96140c569b8f14afa16e9` |
| `joulewise/align/apple/thermal.py` | `e7cbd6808c5a407524e3a85254090a46c33fa910` |

## Lead readback on the accepted pin

Once the lead has the accepted R1-filled W1 plan and its required
registration inputs, record the accepted full head and run the two
escalated materialize commands above with that root. Read C1's
`collection_plan.json`, `plan_tree.json`, and `registration/sizing_b5.json`.
Compare the ordered members, midpoint and supplemental replay fields.
In sizing, match `sources.w1_plan_sha256` to the accepted W1 plan's
exact bytes and `sources.series_manifest_sha256` to the accepted
manifest's bytes. Record the disk law commit and parameters. Read
`packs.align-v4-c1` for `flags`, `align_members`, `member_seconds`,
`T_stream_max_s`, `member_upper_bytes`, `disk_derivation`,
`estimated_footprint_bytes`, `programmed_span_s`, `window_max_s` and
`window_ceiling_s`. Confirm that the pending flag is absent, the real
member maxima fit the caps, and the two-copy footprint uses the accepted
law and scaffold. The lead owns disk reservation, admission, final kit
acceptance and any retarget or merge.

NEEDS_SPEC — none for the synthetic Row 21 comparison.
