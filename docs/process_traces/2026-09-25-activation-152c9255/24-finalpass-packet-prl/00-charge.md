# Charge — cold Fable final pass PRL-FINALPASS-01: PR-L, the launch-context cure for the 25G83 calibration

Assembled 2026-09-25 09:28 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## What you rule on

- **Merge candidate:** branch `feat/2026-09-25-acc-launch-context` at head **99495ba9f9273cf44cf28a74a14b33cfec2d817c**, diff vs `origin/main` `95521871`.
- **What it implements:** acceptance rulings v2.1 R1, R2, R3, R6 and R16 (`docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md` §5, on main).
  - `ProcessType=Interactive` in the night and probe templates.
  - An installer refusal on the parsed rendered plists.
  - A test that no QoS override exists.
  - A 300-frame probe cadence phase: median ≤ 150 ms, max ≤ 200 ms, within 55 s.
  - A refusal for plans whose measurement root lies outside custody.

## Review history (exhibits)

- Opus contract lens `ex-01`: B1 plus S1–S3.
- Astra execution lens `ex-02`: F1–F3.
- Delta re-audit 1 `ex-07`: all nine items closed, plus SF1.
- Delta re-audit 2 `ex-10`: all closed, plus S-1. S-1 was then fixed by a worker-level test, mutation-proven live, at the head.
- The lead's bench run outside the sandbox `ex-06`: 524 tests OK.
- Real-path probe controls: `ex-11-positive-control` (Interactive: 125.6 ms median, pass) and `ex-11-negative-control` (default launchd context: 173.2 ms median, max 262 ms, refused).

## Questions

- **L1.** Verify the diff implements R1, R2, R3, R6 and R16 exactly. Verify that no D-138 pinned file changes: `joulewise/powermetrics_fiducial.py`, `joulewise/reduce.py`, `joulewise/adapters/powermetrics.py` and `joulewise/uncertainty_evidence.py` must be byte-identical to `95521871`.
- **L2.** **Rule the magistrate's provisional reading** (record 00 item 51). R16's "any newly authored plan" does not apply to pack plans whose purpose is `T0_REHEARSAL`. The ruled rehearsal-disjointness rule requires their measurement root to lie outside `~/night-custody`, so without the exemption every post-cutoff rehearsal plan would be refused. The exemption is keyed narrowly to an authenticated T0 authorization record, and the disjointness rule still applies after it; see ex-07 and ex-10. AFFIRM or REJECT it, and give the text.
- **L3.** Run the touched test modules in your worktree: `tests.test_night_gate`, `tests.test_night_agent_install`, `tests.test_run_night_probe_cadence`, `tests.test_run_night_probe_worker_cadence`, `tests.test_launch_context_no_qos_override`, `tests.test_arm_retry` and `tests.test_evidence_arm_sequence`. `tests.test_run_night` takes about 3 minutes; run it if your budget allows.
- **L4.** Anything the reviewers missed that would make a real arm fail or measure the wrong thing.
- **L5.** Rule MERGE, FIX-FIRST (with exact texts), or REFUSE.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or real `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root), `/Users/edr/night-custody` or `~/Library/LaunchAgents`.
- The discovery suite and background tasks are not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
18512512392bbc99f0f6525a1c875b9e7357f4cd47ba93813ef6410c3d6fbb9d  ex-01-opus-contract-lens.md
81acaedb8badcfd4725daa3ea5f88414752bf1eb0def1c590d9c80a5ea6235cf  ex-02-astra-exec-lens.md
d498309ff43fe2b785a882d2db233c3255582f0547c3ab873ae5c7b4965ef9c9  ex-06-lead-bench-run.md
9a92c41ee2c6990c74c217d3f63a93bb47c2655cc4c501361c4cdf3294691c98  ex-07-delta-reaudit.md
8d65fb51fc7dedeb1df57e1aa961809406e94422f9056345794e4498e4ad6a6d  ex-10-delta2-reaudit.md
566be3fcd7237e15e2561a55e48c6e88bcef46f1855b9b222b87a31cb3d2a43f  ex-11-negative-control.md
ab975ccf220bbab4f4ab2c8347d73f09e1e8856f96ebf0e73c88b8c4cc707a23  ex-11-positive-control.md
```
