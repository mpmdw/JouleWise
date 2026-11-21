# RL-181 counted transfer kit rebind, 2026-11-20

Tier 2. Signing target none. Audit base `eaaa1fd560cd457f4e4ccef316be62af920d08e1`
is the parent of the acceptance freeze. The seat branch had no remote head or
existing PR at intake. Mission M0 found no active stop card. RUN_STATE item 481
and its current pointer concern the magistrate's separate lane. This work
uses public source, public kit definitions and synthetic inputs.

## Acceptance freeze

The executable contract was commit
`9753759b0ede9e015cc96f9e0a11d70d8c4d72a1`, before any generator edits.
It follows RL-181 §3.3 and rows 13–14 at `71a83f666`, the old transfer
draft bindings at that revision, the recovered builder at `4e5c2ad1d`
and rows 3–5 of the transfer gate table. The original builder was replayed
in a private scratch overlay against its original pin and seed inventory.
All 61 artifacts matched both historical revisions. The roster hash was
`173f75c45475ab2c2cd01402d570d5c8740cbf8c24fa85c5127b76b22dc4e01f`.
Kit 01 was
`a018bf05c67e0417cb2a3e5cf0f8a3073a7fac9502670f823b10d868539cefd3`.

Nine tests ran against the untouched audit implementation. Three passed
(historical commitments, layout and first unused seeds, and nonseed
fields). The six failures were:

| Baseline failing test | Observed cause |
| --- | --- |
| `test_admitted_pin_and_all_frozen_paths` | Kit 01 still named `ab32a6c91` with old runner and launcher hashes. |
| `test_roster_halted_queues_and_unissued_items` | The roster still named `ab32a6c91`. |
| `test_build_reproducible_and_confined` | The baseline had no builder entry point. |
| `test_shifted_ordinal_including_a_miss_seed_collision_and_split_l` | The baseline had no builder layout validator. |
| `test_stale_path_stale_digest_and_active_queue` | The baseline had no candidate validator. |
| `test_validates_and_runs_one_synthetic_full_span` | The baseline had no candidate or mock entry point. |

## Candidate and verification

The generator uses the historical transfer kits as templates and rehashes
their 38 paths from Git blobs at
`6e9d42f1dd3d308bc9239143d0d634ab965e50e1`. Only
`scripts/cadence_legs_runner.py` and `scripts/launch_cadence_span.py`
have different path hashes. The admitted `gen-legs` supplies the layout
and seed draws. The seed inventory pins the audit base and the runner's
public kit definitions, covering 38 definitions including stability 15
and 16. Independent draws checked the first eligible master and all six
leg seeds at each place. All 120 leg seeds are fresh against the inventory
and within the candidate family. The rebound drafts reproduce the original
ordinal layouts and seed bytes. The old drafts are the same planned places.

Each build validates all 20 kits against the admitted Git blobs (760 path
comparisons), checks all 20 queue bindings and their halt decisions, and
plans all 20 six-leg rosters from a fixed synthetic t0. The planner's minimum
launch budget is its launch deadline minus that t0, including the retry and
cleanup allowances. The table contains plan estimates in seconds.

| Place | Master seed | L caps in order | Expected (s) | Worst (s) | Minimum launch (s) |
| --- | --- | --- | ---: | ---: | ---: |
| 01 | 2026111806 | 4096 → 3724 | 12,310 | 24,750 | 27,260 |
| 02 | 2026111800 | 3151 → 4096 | 12,262 | 24,750 | 27,260 |
| 03 | 2026111804 | 3724 → 4096 | 12,310 | 24,750 | 27,260 |
| 04 | 2026111801 | 4096 → 3151 | 12,262 | 24,750 | 27,260 |
| 05 | 2026111802 | 4096 → 3724 | 12,310 | 24,750 | 27,260 |
| 06 | 2026111805 | 3151 → 4096 | 12,262 | 24,750 | 27,260 |
| 07 | 2026111803 | 3724 → 4096 | 12,310 | 24,750 | 27,260 |
| 08 | 2026111807 | 4096 → 3151 | 12,262 | 24,750 | 27,260 |
| 09 | 2026111811 | 4096 → 3724 | 12,310 | 24,750 | 27,260 |
| 10 | 2026111810 | 3151 → 4096 | 12,262 | 24,750 | 27,260 |
| 11 | 2026111815 | 3724 → 4096 | 12,310 | 24,750 | 27,260 |
| 12 | 2026111808 | 4096 → 3151 | 12,262 | 24,750 | 27,260 |
| 13 | 2026111809 | 4096 → 3724 | 12,310 | 24,750 | 27,260 |
| 14 | 2026111812 | 3151 → 4096 | 12,262 | 24,750 | 27,260 |
| 15 | 2026111813 | 3724 → 4096 | 12,310 | 24,750 | 27,260 |
| 16 | 2026111818 | 4096 → 3151 | 12,262 | 24,750 | 27,260 |
| 17 | 2026111819 | 4096 → 3724 | 12,310 | 24,750 | 27,260 |
| 18 | 2026111817 | 3151 → 4096 | 12,262 | 24,750 | 27,260 |
| 19 | 2026111814 | 3724 → 4096 | 12,310 | 24,750 | 27,260 |
| 20 | 2026111816 | 4096 → 3151 | 12,262 | 24,750 | 27,260 |

## Reproduction and checks

From the audit worktree, with `SEAT` pointing to the private scratch directory:

```sh
D=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer
for candidate in candidate-a candidate-b; do
    python3.13 -B "$D/build_kits.py" build --seat-dir "$SEAT" --output-dir "$SEAT/$candidate"
done
diff -qr "$SEAT/candidate-a" "$SEAT/candidate-b"
TMPDIR="$SEAT" python3.13 -B -m unittest discover -v -s "$D/tests"
```

Both builds passed. The directory comparison found zero differences and
all 61 hashes verified in each directory. The focused contract passed all
nine tests in 302.910 seconds, including a six-leg synthetic span with
rc 0 and zero stops. The six fixture refusals cover the shifted ordinal
after a miss, seed collision, split L pair, stale frozen path, stale kit
digest and active queue. Generator commit
`c5c2f92acf10ef591ae6e96a5720e50ae595f59d` leaves the frozen test
bytes intact. The general suite is assigned to the draft PR's hosted CI
because the local canonical suite includes tests that signal real processes.

## Opus handoff

The private seat holds the candidate at `candidate-a/` and its digest
manifest at `TRANSFER-CANDIDATE.sha256`. Run
`shasum -a 256 -c ../TRANSFER-CANDIDATE.sha256` from the candidate root.
The roster provides the logical repository-relative paths and SHA-256
bindings for every kit and halted draft queue.

| File | SHA-256 |
| --- | --- |
| `date-place-roster.json` | `520aba154df6d87f9d86870721a17cfe92fc20694356da27184f237121ff04e5` |
| `cl-transfer-01.v1.1.json` | `746de4d01655e67402df60b017d281f84f91b2e11d41dcbd96023c30c2b2eb2a` |
| `TRANSFER-CANDIDATE.sha256` | `c948abdc5abd7a19823bffb7d791a1f3fd3ee4080686492e28673a7caa5bd243` |

Opus verifies the local candidate against the manifest, accepts its bytes
and publishes their immutable source revision. The registration owner uses
that revision and the roster and kit digests for the main registration.
The 20 queues are halted and expired. The 20 item drafts are unissued and
have no assigned dates. The lead owns scheduling and launch decisions.

`NEEDS_SPEC` is empty for the generator contract.
