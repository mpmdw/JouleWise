# 2026-11-05 — Measurement MBP offload and gold setup runbook

Authored `docs/align/mbp_offload_and_gold_setup.md` on
`lane/2026-11-05-mbp-offload-runbook`, based on local `origin/main`
`427cc6d302c4a3731b69b4b5f4bb2c725acc5285`. This is documentation only.
No operation in the runbook was executed. No measurement data, external home
directory, real restricted directory, or network source was accessed.
Git object reads through the permitted shared alternates were used for code
and records on the port and ALIGN-kit branches.

The 14 steps cover machine/SSD identification; explicit ALIGN pause and
launchd disable/restore; read-only inventory; a cited KEEP list; cloud quota,
throughput and time admission; complete source/archive SHA-256 verification;
post-upload eviction/re-download verification; an independent full restore;
one-root Ed-only deletion with KEEP-overlap checks and per-manifest logging;
actual space reclamation; disk budget; isolated venvs and storage exclusions;
immutable official HF revision and LFS-oid verification; gold-parity handoff;
and a fresh-plan restoration of ALIGN.

Records consulted include DATA-OFFLOAD-ICLOUD-01 in TASK_QUEUE, the original
offload registration, the July archive/prune report, November pilot offload
records, BLOCK5-TRANSFER and its committed manifests, B5/B6/BYTES registration
custody, current restart/queue gates, M0, orchestration, targeted decisions and
Goal 11 on `origin/port/qwen4-exp-mlx` at
`1643e9aac43ebfc10443a31c30a0cdc506bcbfc6`. The pinned ALIGN config was read at
`8d1ab6e2c1c8f17fac0b20485f519d197e463c38`.

Key findings and conservative choices:

- The SSD size, current free bytes, cloud quota and throughput are unmeasured.
  The runbook measures them before making a capacity/time claim. Its nominal
  download admission is 491.2 GB available, with conversion output additional.
- B5 release/recompute runs on the analysis laptop. The verified transfer
  does not cover every original MBP root, and records explicitly retain B5
  originals and post-sequence-376 calibration captures until release. These
  remain KEEP; this runbook supplies no B5-original deletion command.
- The old July offload used some sampled verification and left single-copy
  traces. That is not enough for this brief. Full cloud re-reading and a
  second independent copy/restore precede irreplaceable deletion here.
- APFS-shared pilot roots reclaimed less space than their summed sizes.
  Only a measured df gain of at least 450 billion bytes meets the target.
- Exact model revisions are recorded for Qwen3-30B-A3B-4bit
  (`d388dead1515f5e085ef7a0431dd8fadf0886c57`) and Qwen3.8-27B-8bit
  (`815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`). Their restoreability and open
  registration dependencies must be established before optional offload.
  The older 27B record proves BYTES-extension use, not current ALIGN use.
- Main's mac extra requires transformers below 5.13. The 5.22.1 reference
  therefore uses its own venv; measurement venvs stay intact.

Validation performed on documentation only:

- `python3.13 -B -m unittest tests.test_docs_freshness` — PASS, 31 tests,
  0.891 seconds initially, 1.498 seconds on the final documentation check.
  No full suite, pipeline or hardware check was run.
- Extracted the runbook's 21 zsh fences and parsed each using
  `/bin/zsh -n` on stdin — PASS. Extracted the four Python heredocs and parsed
  with `ast.parse` — PASS. No shell block or embedded Python was executed.
- Final whitespace check, citation review, changed-path review and protected
  file comparison — PASS; four cross-branch source citations resolved, and
  `git diff --cached --check` and the protected-path diff exited zero. These checks
  establish syntax and documentation consistency, not operational validity
  on the measurement Mac.

Only two files are intended to change: the runbook and this dated report.
RUN_STATE, TASK_QUEUE, state_kernel and test_gen_state were not edited;
no kernel task was registered, per the brief. No commit was pushed.

Open dependencies: the local refs do not contain
`lane/2026-11-05-align-flashnext-gold-parity`. Its actual CLI, reviewed harness
commit, exact torch version, conversion interface and end-to-end commands
cannot be verified offline. A question was sent to the task owner; the
runbook has an explicit STOP and an expected input/output contract, rather
than fabricated flags. The official HF checkpoint commit is also not recorded
in the available sources; the future MBP operator must resolve/approve a full
SHA and exact bytes before download. No claim of a runnable gold command or
complete hardware setup is made.

Next exact step: the lead supplies the gold-parity lane's reviewed commit and
CLI so step 12 can be completed; Ed then starts step 1 on the actual MBP in a
lead-controlled non-measurement window. If KEEP obligations prevent 450 GB
reclamation, retain custody and obtain approved external storage or an
explicit retention ruling.
