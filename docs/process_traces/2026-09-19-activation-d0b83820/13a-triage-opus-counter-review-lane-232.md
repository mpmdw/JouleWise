# Record 13a — lead triage of Opus counter-review 13 (lane 232 harness at `d74b1be5`), fix round 4 contract (2026-09-19 08:3x PDT)

Every finding is dispositioned here, none silently applied (rule 2). None is a blocker; none amends a process rule or a published evidence schema beyond the harness's own PROVISIONAL summary. The starvation-class finding S2 is ruled by the principle cold gate packet 08 already fixed (delivery is reported, never asserted; lifecycle checks stay but are sized to the instrument), so no new gate is convened; the surviving site was outside rounds 2/3's scope, not a failed fix.

| # | Disposition | Ruled fix shape (seat implements exactly this) |
|---|---|---|
| S1 | ACCEPT | In `load()`'s `finally`, after the cleanup ladder: if any cleanup row has `alive` true or `exitcode` not 0, set `report["error"]` (if still None) to a string naming the pids and exit codes (`"worker cleanup escalated: pid 123 exitcode -15"`); `main`'s exit code then follows. Mirrors `production_round`'s residue rule. |
| S2 | ACCEPT | First join grace 0.5 s → 5 s (the file's own convention: `stop_process` grace 5, `production_round` cleanup +5). Keep the test's `assertEqual(child["exitcode"], 0)`; with S1 it can only fire after `report["error"]` has already named the escalation. |
| S3 | ACCEPT, bounded | `collect`: count rounds with `status == "error"`; write `session["error_rounds"] = n` always; set `session["error"]` (and thus a non-zero exit) ONLY when no round completed with status ok — one flaky round must not abort a campaign chain (Ed's sensible-gates directive); the rows already carry each round's status honestly. |
| S4 | ACCEPT | Pop `reference_reason` / `alignment_model_reason` when the sibling value is not None, mirroring `collect` lines ~737–738. |
| S5 | ACCEPT | Add `boot_id` to the `summarize` group key and emit it in each group; if rows carry an OS build field, add it too and emit it. Rows from different boots or builds are never pooled into one mean or one Δ (D-078 lesson). Update the empty/reasoned-null paths accordingly and the tests that pin the group shape. |
| S6 | ACCEPT | One darwin-only test: after `set_qos("background")` the calling thread's class read back through `pthread_get_qos_class_np(pthread_self(), &cls, &prio)` (ctypes on `/usr/lib/libSystem.B.dylib`) is `0x09`; after `set_qos("user-initiated")` it is `0x19`. Run it in a spawned subprocess or restore the class afterwards so the test runner's own thread is not left at background QoS. |
| S7 | ACCEPT, delete | Remove `stop_process` and its two tests (`tests/…:509–523`); `PowerRecorder` owns termination. Test count: 45 − 2 + 1 (S6) = 44. |
| N1 | ACCEPT | Reword the `STARTUP_CPU_S` comment: headroom on the kernel-charged CPU ceiling; measured child start-up plus unreported CPU ≈ 0.34–0.35 s on this host (records 06/11), floor 0.5 s. |
| N2 | ACCEPT | `.get` chain at `aggregate` ~:978 so a foreign `rounds.jsonl` reaches the `ValueError` refusal path, not a `KeyError` traceback. |
| N3 | ACCEPT | Register `children`/`connections` before `Process.start()` (or close both pipe ends if `start()` raises). |

Not accepted as a change: the counter-review's optional `stationarity` assertion in the real-load test (a real-scheduler quantity; the three direct `stationarity` tests are the oracle).

Order: fix round 4 (seat, Astra high, `WRITE_SCOPE: [scripts/sample_quiet_predicate_evidence.py, tests/test_sample_quiet_predicate_evidence.py]`, brief 18) → lead diff read → delta re-audit round 4 (fresh read-only seat, all ten findings re-verified, mutation set re-run, both same-signature statements) → full sharded replay at the new head (record 14 at `d74b1be5` becomes the pre-round baseline) → PR with the twelve-row ledger → terminal review.
