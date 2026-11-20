# Evidence-night cleanup flake: Fable cold review

Date: 2026-11-11 02:44 PST. Reviewer: Fable 5.2 (cold).
Target: `fix/2026-11-11-evidence-night-flake` @ `10d5d63f73755e5bcc9d740b0db1a29a09c95b8e`
(fix `e094ba445`, base `origin/main` `f6b1573bd`).

**Verdict: ADMIT.** The one-flag fix is correct, minimal and cannot change a measured byte. The mechanism
is demonstrated: a detached Git maintenance child outlives `prepare` and writes into the measurement
clone. The hosted `ENOTEMPTY` traceback itself was not reproduced by the author or by me, so the link
from that mechanism to the CI symptom is strongly supported but not proven. Hosted CI reruns are the
remaining confirmation (A-F1). No code change is required before merge.

## Read and not read

Read: `git diff origin/main...HEAD` (all six files), the author report
`docs/run_reports/2026-11-11-evidence-night-flake.md`, `scripts/stress_evidence_night_cleanup.py`,
`joulewise/evidence_night.py` (`run`, `checkout_ok`, the clone block of `prepare`, `probe_command`,
`canonical_fast_forward`), `tests/git_fixture.py` (head), the touched test and the `PrepareTests` fixture,
and registration §11 items 1-2 of `configs/campaigns/v5_claim_25g83/registration_block5.md` (sealed-inventory
rule only).

Not opened: `docs/analysis/b5/RESULTS.md`, `REDERIVATION.md`, `rederivation.tsv`,
`hand_checks_phase2.tsv`, any seat-4 report, RL-38 to RL-42, `RUN_STATE.md`, anything under
`docs/paper/paper1/`, and any custody, night-*, archive, restricted or real-session content. One
disclosure: a `git grep -l` for the SHA-256 of main's `evidence_night.py` (looking for digest pins)
printed the names of several `docs/process_traces/**` manifests and `SHA256SUMS` files. Only file names
were printed; none was opened. All runs used synthetic fixtures in the native macOS temp directory.

## Checks

Environment: MacBook Air, Apple Git 2.50.1, Python 3.13.18.

| # | Check | Result |
|---|---|---|
| 1 | `stress_evidence_night_cleanup.py --runs 20`, fixed tree | 20 passed, 0 failures, 0 errors, 0 live children, 0 writes after return (5.99 s) |
| 2 | Same, with `origin/main`'s `joulewise/evidence_night.py` checked out | 20 failures, 0 errors, 20 live children after return, 20 post-return write observations. Changed paths: packs, `objects/info/{commit-graph,packs}`, `info/refs`, reflogs. Late commands: `gc --auto`, `pack-refs`, `reflog expire`, `repack`. Matches the report's before/after table. |
| 3 | Unforced witness: the real test (full-repository clone, no hook, no forced GC settings) with main's `evidence_night.py` | FAILS on the new Trace2 assertion: `fetch` starts `git maintenance run --auto --quiet --detach`. With the fix it passes. So the detached child is launched on every real prepare, not only under the harness's forced settings. |
| 4 | `python3.13 -B -m unittest tests.test_evidence_night` (fixed tree) | 168 tests, OK (493 s, machine loaded by my part-B runs) |
| 5 | Other maintenance triggers in `prepare` | None. `clone`, `checkout`, `merge-base`, `rev-parse`, `status` and `ls-remote` never run auto-maintenance. The single `fetch` was the only trigger in the clone block. |
| 6 | Other triggers in the module | `canonical_fast_forward` runs `git pull --ff-only`, which does trigger auto-maintenance, but in the persistent canonical checkout, not in a directory anyone deletes (A-F3). |
| 7 | Flag support | `git fetch --no-auto-maintenance` exists since Git 2.29 (October 2020). Accepted by Apple Git 2.50.1 here; Apple Git >= 2.39 and hosted Ubuntu Git both have it. I did not query the MBP's Git version (no SSH from a review seat). |
| 8 | Production bytes | The flag changes only whether housekeeping is spawned. Refs, HEAD, index, working tree and object content are identical; only pack layout and timing under `.git` differ. Nothing in `evidence_night.py` digests `.git` (it is only `safe_path`- and `lexists`-checked). The flag is per-invocation, so `.git/config` is unchanged. One fewer background writer during preparation is, if anything, quieter. |
| 9 | Corroboration | `tests/git_fixture.py` already disables maintenance for fixture repositories for this same failure class. The production-made clone in `prepare` was the one repository those controls could not reach, because clones do not inherit local config. |

## Findings

| # | Sev | Finding | Required action |
|---|---|---|---|
| A-F1 | Low | The hosted `ENOTEMPTY` was not reproduced. What is shown: a writer outlives the CLI on every prepare (check 3), it survives the return in 4 of 200 unforced local runs (author), and when held it writes below the clone (check 2). That is sufficient cause for a cleanup race, but another contributor on Ubuntu is not excluded. | None before merge. Treat the flake as closed only after hosted CI stays green over several runs of this test; reopen if `ENOTEMPTY` recurs with no `maintenance` child in the trace. |
| A-F2 | Low (lead ruling, not a code defect) | `joulewise/evidence_night.py` is listed in `configs/campaigns/v5_claim_25g83/sealed_inventory.json`, and main's copy still equals the sealed hash (`3f0820ba...`). This PR is the first change to that file since H_claim `c27485347`. Under registration §11 item 2, every window inventories `joulewise/` whole, so a window armed with that inventory in force would list this file as a changed path. Main already differs from H_claim in 128 files under `joulewise/` and `scripts/`, so this adds one path to an existing drift rather than creating it. | Lead to confirm which inventory governs the next armed night, and that this path is covered by the planned re-issue or successor seal, before the fix reaches a measurement head. |
| A-F3 | Info | `git pull --ff-only` in `canonical_fast_forward` can still detach maintenance. Harmless in production. Tests that pull into a temporary canonical checkout rely on the fixture's maintenance controls. | None. If a canonical-checkout test ever flakes the same way, check that its fixture came from `init_git_fixture`. |
| A-F4 | Info | The stress harness cannot run when `TMPDIR` contains `claude` or `codex` (the test's census-clean draw fails), and then prints `errors=20` with zero live children, which reads like a pass on the leak counters. My first attempt under the session scratchpad hit this; all counts above are from the native temp directory. | Optional: make the harness refuse such a `TMPDIR` up front with a clear message. |
| A-F5 | Info | The Trace2 assertion keys on the word `maintenance` in a child's argv. Git older than 2.29 would spawn `gc --auto` directly and pass vacuously. No supported platform is that old. | None. |
