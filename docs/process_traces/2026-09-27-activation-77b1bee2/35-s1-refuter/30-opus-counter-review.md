# Opus 5.5 counter-review of S1's merge candidate 4aefdd12 (gate rows 2 and 6)

Reviewer: Opus 5.5 (claude-opus-5-5). I worked read-only in every repository. Scratch files went to `/tmp/opus-s1cr-77b1bee2/`. I used no subagents, no Codex and no `claude -p`, and I did not read RUN_STATE, CLAUDE*, AGENTS, memory or skills. Everything was run on `/opt/homebrew/bin/python3` 3.14.7 with `PYTHONDONTWRITEBYTECODE=1`.

- **Candidate:** `/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2`, detached at `4aefdd12`, tree `6e0dfda7`. Its parents are `204424e6` (the S1 head) and `b69c39eb` (main).
- **S1's own diff:** `git diff 97082508 204424e6`. Here `97082508` is `merge-base(204424e6, b69c39eb)`. It covers 27 files: +6158/−81 overall, and +1737/−25 outside `tests/`.

**Summary.** The one finding that blocks the merge is new: **B-1**. The candidate's V1 suite is RED. S1's protected-path pin test compares the working tree against base `1417c0c4`, and that comparison includes `configs/calibration/`, which main's W1/W2 harvests changed. The S1 refuter's pass and the S1-A3-ROUTE-01 cold gate both predicted that V1 would stay green on the candidate. That prediction is false. Everything else holds.

---

## 1. Contract fidelity: is S1's diff exactly its ruled scope?

### 1.1 Scope membership (executed)

The WRITE_SCOPE is the last fix brief's list: `60-s1-fix3/10-fix-brief.txt`. That list is Final texts v1.1 §E for S1, plus `joulewise/envelope_gate.py` for amendment 63 (a) and `tests/test_battery_float_consumers.py` under amendment 36.

The set of files that `git diff --name-only 97082508 204424e6` lists (27) is a subset of that WRITE_SCOPE (27 entries). The two sets are in fact equal.

A second check confirms the file set. `git diff --name-only b69c39eb 4aefdd12` gives the same 27 files, so the merge adds nothing beyond S1's own changes.

`configs/battery_float/historical_captures.json` is absent, as v1.1 text 10 and §E require.

### 1.2 Production changes, commit by commit (executed: `git diff --name-only c^ c`, excluding `tests/`)

| Commit | Production and config paths | Ruled by |
|---|---|---|
| 24b79db3 | bundle_read, controller, publication_privacy, builder, historical_bundles.json | texts 7, 8, 11, 13 (T13); amendments 26 and 31 |
| b859317c | bundle_read, builder, historical_bundles.json | amendments 36–43 |
| 21213be7 | the eight consumers, calibration_bracketing, scored_reduce | texts 9, 10, 12; amendments 26 and 42 |
| 49d77c74 | builder | amendments 47 and 48 |
| cbfa9dc3 | the eight consumers, bundle_read, scored_reduce | amendments 49, 50 and 52–56 |
| 8953c7a5 | `joulewise/envelope_gate.py` only | amendment 63 (a) |
| 00b0dc68, 204424e6 | none (test-only) | RETURNS: "no production code is ruled inside S1"; R72-2 erratum |

**Amendment 63 (a), checked line by line.** The diff of `envelope_gate.py` has exactly the three ruled changes:

1. It adds `_gated_summary` immediately above `_manifest_record`.
2. In `analyze_envelope_gate`, the `summary_missing` read becomes `_gated_summary(reader)`.
3. In `_level_window_energy_records`, the loop's read becomes `_gated_summary(reader)`.

There is no `battery_float` import and no other change.

The seat did not add a production change of its own after the RETURNS ruling.

### 1.3 Owed items spot-checked in code (executed by grep; the tests ran in V1, below)

- **Amendment 26.** `bundle_read.authenticate_window_members` is at `bundle_read.py:282`. `GATE_EXCEPTIONS` is at `:279`. At `:332` and `:336`, a `BundleReadError` is re-raised as `CustodyUnreadable("<label>: …")`. The T12 row is at `tests/test_bfgs_window_consumers.py:322`.
- **Amendment 31, S1 clause.** `BundleReadError("events.jsonl missing")` is raised at `bundle_read.py:536`, and its row is at `tests/test_bundle_read.py:663`.
- **Text 10 constants.** `BFGS_HISTORICAL_LEDGER_SEQUENCE = 176` and `BFGS_HISTORICAL_CUTOFF_WALL_S = 1790462247` are at `calibration_bracketing.py:53-54`. They equal base `1417c0c4`'s ledger head (176) and its committer time (1790462247), which I checked by `git show` and `git log`.
- **Text 12.** The eight consumers call `authenticate_window_members`. The seven small diffs were read in full: aggregate, window_duration_margins, floor_extraction, extract_detection_floors, mint_floor_artifact, publication_privacy and envelope_gate. Each change is a gate statement, a status record, or an `except GATE_EXCEPTIONS: raise`.
- **Builder forward check** on the candidate: `forward check: byte-identical entries=69` (21 s).

I found no owed item missing and no production change without a ruling.

## 2. Fences (A5), all executed

| Check | Result |
|---|---|
| `shasum -a 256 joulewise/battery_float.py` | `4b4d7bb206250cc0…` (prefix `4b4d7bb20625` ✓) |
| blob of `battery_float.py` at 1417c0c4 / 4aefdd12 / working tree | `20e76af0…` ×3, IDENTICAL |
| blob of `reduce.py` | `82449d58…` ×3, IDENTICAL |
| blob of `bundle.py` | `364d38a0…` ×3, IDENTICAL |
| AST walk of the eight consumers for any `import` / `from` naming `battery_float`, or a dynamic import | none in all eight |

A5 holds.

## 3. Merge-with-main sanity

**The merge itself is clean.** `git merge-tree --write-tree 204424e6 b69c39eb` gives `6e0dfda7…`, which equals `4aefdd12^{tree}`. Main's four files are byte-identical to `b69c39eb`, and S1's 27 files are byte-identical to `204424e6`.

Main added four things since `97082508`:

- the ledger head pin, which moved from 176 to **276**;
- two committed verdict files, under `configs/calibration/battery_float_verdicts/…-w1-…` and `…-w2-…`;
- the census test, `tests/test_arm_readiness_evidence_t0.py`.

What I checked against those additions:

- **V1 on 4aefdd12** (the ten modules of the brief) ran **477 tests in 5119 s, FAILED (failures=1)**. The only failure is `tests.test_bundle_read.StrictAccessorTests.test_historical_set_bytes_and_protected_base_paths_are_pinned`, which is **B-1**. Earlier, V1 on `204424e6` was reported as 477 OK.
- **V2 plus main's census test on 4aefdd12:** `tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds tests.test_envelope_gate tests.test_arm_readiness_evidence_t0` ran **421 tests in 1596 s, OK**.
- **The ledger moved past S1's cutoff constant.** I checked whether this changes what S1 computes. I loaded the live ledger read-only (`/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl`, 276 rows) with the candidate's code, using `load_calibration_ledger_snapshot(..., mode="read_replay")`. The snapshot is valid, with 86 observations. Of the 23 observations that are valid and not historical imports:
  - 11 have sequence ≤ 176 and are classified `unobserved_historical`;
  - the **12 with sequence > 176** (194 … 268) all classify as **`pass`**.
  - `discover_calibration_candidates` returns 0 candidates both on the candidate and on a `git archive` of main.
- **The W1/W2 captures authenticate under S1's gate.** `battery_float.authenticate_capture` on every W1/W2 capture directory gives w1 `{'pass': 12}` and w2 `{'pass': 12}`.
  - The W1/W2 custody holds only `runs/instrument_validation/` and no `metadata.json` bundles, so there is no bundle for the historical set to admit. This answers the "observation outside the charge" in the cold gate's Opus refuter (`22-opus-refuter.md`): the W1/W2 artefacts are captures that pass.
- **The other S1 tests bound to a git commit** were re-read against main's change. They stay GREEN, and V1 confirms it:
  - `test_historical_boundary_and_prospective_missing` reads `git show 1417c0c4:…ledger_head.json`, the base, not the working tree.
  - The builder's `BASE` archive and `test_raw_capture_lane_files_match_main` (pinned to `97082508`) are also untouched, because main changed no lane file.

## 4. Findings

### BLOCKER

**B-1: S1's protected-path pin test is RED on the merge candidate, and would stay RED on main after every harvest.** The test is at `tests/test_bundle_read.py:558-588`; line 573 has `"configs/calibration", "configs/campaigns/d117_"` and line 586 has `git diff --exit-code --no-ext-diff 1417c0c4 -- *protected`.

What the test does: it runs `git diff --exit-code 1417c0c4 -- <protected>` against the **working tree**. Final texts v1.1 §E has the pin test assert that `configs/calibration/` and every `configs/campaigns/d117_*` tree are byte-identical to base. The purpose is to fence S1's own edits. The test, however, also catches anything main changes.

Executed evidence:

- `git diff --quiet 1417c0c4 <c> -- <protected list>` exits 0 at `204424e6`, and exits 1 at both `4aefdd12` and `b69c39eb`. The changed paths are `calibration_ledger_head.json` (176 → 276) and the two new verdict files.
- The single test on the candidate gives `FAILED (failures=1)`. Its diff shows `"sequence": 176` → `276`.
- The full V1 on the candidate has the same single failure.

Why this blocks: V1 is part of A4 and part of CI, and neither is green on the candidate. The damage also outlasts this merge:

- Once the test is on main, every future harvest PR fails it, because each harvest moves `calibration_ledger_head.json` and adds a verdict file. That includes the next scored or derivation window's pin commit.
- S3's new `_v5` trees also fail it. They are tracked and match `configs/campaigns/d117_*`, and a path that does not exist at `1417c0c4` shows up as a diff.

The S1 refuter (`11-refuter-report.md`, residual risk) and the cold gate (§6 order 1, "the merge changed no production file on either route") both inferred V1 green from "no production file changed". The test is sensitive to non-production files that main moves.

Closure: a test-only change of about three lines, which needs a ruling because tests inside S1 are ruled. Options, in order of preference:

- **(a)** Make the fence a commit-to-commit assertion of S1's own changes, `git diff --exit-code 1417c0c4 204424e6 -- <protected>`. It is stable forever and is what §E means.
- **(b)** Diff against `git merge-base HEAD <main ref>`. This depends on a ref that may be absent.
- **(c)** Keep the working-tree check for the code files only, and drop `configs/calibration` and `configs/campaigns/d117_*`.

For each option, show the test RED under a counterfactual in which S1's own commit touches a protected path, and GREEN on the candidate. Then re-run only `tests.test_bundle_read` and the builder check. The rest of V1 is 476/476 green on the candidate.

### SHOULD-FIX

- **S-1. The PR description obligations**, which the lead writes. These are text only, not code.
  - Text 15's verbatim sentence: "No transaction-pack window arms between the S1 merge and the completion and verification of S3's freeze for the pack it would use."
  - The refresh list `docs/paper/results-fill-registry.md:366-367, 774`.
  - From cold gate S1-A3-ROUTE-01 §6 order 2: lane BFGS-COOLDOWN-ANCHOR-01 and its order; BFGS-RAWCAPTURE-01 item 5 and its 78 (a) order; the two pre-checks; and amendment 77.
- **S-2. The 78 (b) capture pre-check script** (cold gate `21-coldgate-fable-ruling.md` §5.6, around `:310-334`) exits 1 for any `unobserved_historical` member. Its own text says such a member is not a refusal. This is the cold gate Opus refuter's SF-5, and I concur. It is not repository code, so it does not block the merge. Correct it before its first use, so that the stand-in check needs no judgment when it is applied.
- **S-3. The same class of problem is latent in `test_raw_capture_lane_files_match_main`** (`tests/test_bfgs_consumer_sweep.py:1917`). The test pins the working tree of the lane files to `97082508`. It is GREEN now, since main changed no lane file. But any change to those files on main, including lane BFGS-RAWCAPTURE-01's own fix, turns it RED. If that tripwire is intended, the lane's brief must name this test as a file it updates. Otherwise, fix it in the same ruling as B-1.

### NIT

- **N-1.** Text 10 says the historical constants are set "at the S1 merge base". The seat read that as S1's branch base `1417c0c4` (176), not main's head at merge time (now 276), and `test_historical_boundary_and_prospective_missing` pins that reading. This is the stricter reading for the science, since fewer captures are exempt. With main at 276, all 12 post-cutoff valid observations pass (§3), so nothing changes today. Record the reading in the PR description so that a later reader does not "correct" it to 276.

## 5. Anything else that blocks the merge of 4aefdd12

Only B-1. F1 and F2 are routed under row 1c by S1-A3-ROUTE-01, and I found no new fact about them (amendment 77 (b)). A1, A2 and A5 are unaffected by the merge. A5 is re-verified in §2.

Once B-1 is closed and `tests.test_bundle_read` is re-run GREEN, I see no remaining obstacle.

COUNTER-REVIEW: FAIL
