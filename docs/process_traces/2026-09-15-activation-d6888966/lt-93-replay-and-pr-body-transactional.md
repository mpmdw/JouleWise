# lt-93 — Row 9 replay and PR body DRAFT (successor to lt-91)

Written 19:26 PDT 2026-09-15 (clock read). Final head **`0ba6ce54`**.

## Row 9 — the replay, lieutenant-run

Run by me in the integration worktree `/Users/edr/code/JouleWise-wt-iw-txn` at
`0ba6ce54`, working tree clean:

```
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/shard_tests.py --workers 4 --split
```

18:27 → 19:24 PDT. Exact tail:

```
MODULE PASS tests.test_window_status_guard tests=11 failures=0 errors=0 skipped=0 seconds=2.734
SHARD SUMMARY index=4/4 modules=62 tests=1856 failures=0 errors=0 skipped=9 result=PASS
WORKERS SUMMARY shards=4 modules=234 tests=6135 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
```

**234 modules, 6135 tests, 0 failures, 0 errors, PASS.**

And the acceptance script at the same head:

```
class_1: NO
class_2: NO
ENGINE_SHA256 756fe0f0dd530caee8e9ec99afe11f1185ce2e1e02d99c410d92d37383b4273f
```

### Why this replay is worth more than its predecessor

The previous replay, at `53d95227`, reported **`failures=1`** in 6133 tests with
`failed_shards=3`, while shard 3 re-run alone passed 1433/1433. I hypothesised a
0.75 s adapter-timeout flake and started editing timeouts; **that guess was wrong
and I reverted it uncommitted.** The Opus execution lens then found the real
cause with a null control: a process started with `&` inherits `SIGINT` as
`SIG_IGN`, children keep it across `exec`, and six signal cells therefore
asserted nothing — reporting a successful arm where an interrupted rollback was
expected. `shard_tests.py` runs its shards exactly that way.

**This replay ran under the same background shell and passed**, which is the
evidence that fix round 4's S2 cure works where the failure actually lived. A
green replay before that fix would have been green for the wrong reason.

## PR body draft — NOT opened; the magistrate opens and merges

### Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-28-opus-execution-lens.md |
| 2 | Paired distinct lenses: contract + execution | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-28-opus-execution-lens.md |
| 3 | Lead-written FIX contract with dictated closure shapes | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-25-T1-rulings-R1-R7.md |
| 4 | Delta re-audit of every fix round | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-30-delta-fix-rounds-2-3.md |
| 5 | Same-signature statement from every delta | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-30-delta-fix-rounds-2-3.md |
| 6 | Opus counter-review on the near-final head | NOT-RUN |
| 7 | Apex Fable code-reading diff gate | NOT-RUN |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-27-refuters-fixes-delta.md |
| 9 | Lead unpiped full-suite replay on the integration tree | RUN docs/process_traces/2026-09-15-activation-d6888966/lt-93-replay-and-pr-body-transactional.md |
| 10 | Final-head fresh-eyes review after every post-review commit | NOT-RUN |
| 11 | CI green on final head + post-merge cross-unit review | NOT-RUN |
| 12 | Magistrate terminal review of the exact merge candidate | NOT-RUN |

### Summary

INSTALL-WINDOWS-MULTI-01, rebuilt. Four rounds of the previous zsh installer each
passed review and were each broken by the next audit — not four bugs but one
topology: invariants enforced by inspecting call sites, with the defect class
reappearing one site further along each time. A three-seat redesign consult
(Astra, Opus, blind Fable — all three recommending it) produced adjudication 34,
and this branch implements it.

The engine is `joulewise/night_agent_install.py`: a transactional state machine,
stdlib-only, Python 3.9-compatible because `--uninstall` must run under
`/usr/bin/python3` (3.9.6 here — a rehearsal night was lost to that on
2026-09-11). `scripts/install_night_agent.sh` drops from 387 lines to 81: argv
parsing, the MIN_PYTHON check, `exec`.

Three constructions replace enumeration. **A single mutation channel** — three
mutators, nothing else touches `launch_dir` or launchctl. **A commit predicate
that is the only road to exit 0**, evaluated once on a clock read taken after the
last launchd mutation. **Deletion that requires an absence proof** —
`require_absent(label)` returns a token `remove_plist`/`restore_prior` demand, so
"delete without proof" is a type error rather than a review finding.

The defect that stopped the previous design is answered by D2: liveness is
three-valued — LOADED iff rc 0; ABSENT iff rc 113 **and** stderr carries the
exact `Could not find service "<label>" in domain for user gui: <uid>` line;
**everything else is UNKNOWN, and UNKNOWN counts as loaded.** The old code read
any non-zero rc as "not loaded", so a query that merely ERRORED (rc 9) was proof
of absence and plists were deleted under a live job.

### Verification

Acceptance at `0ba6ce54`: **`class_1: NO`, `class_2: NO`**. The executed witness
for the old killer — `bootout` rc 1 with `print` rc 9 — is now
`rc 4` with **both plists retained**, where the old shell exited **0** having
deleted both.

Replay: 234 modules, 6135 tests, 0 failures, 0 errors, PASS.

Independent execution lens (fresh Opus seat): ~700 installer invocations —
enumerated class-2 products, 112 signal cases including SIGKILL at 14 seams,
611 fuzz runs across three bias profiles, an exhaustive 96-case start-state
matrix under realistic launchd semantics — **no class-1 or class-2 witness**, and
**all 23 D10 must-die mutants RED**. From all 32 arbitrary starting machine
states, including planted I3 violations, one `--uninstall` returned 0 (32/32).

Delta auditors on every fix round: isolated reversions per change, must-die
re-runs with no new survivors, and the same-signature question answered only by
the two executed predicates.

### Known limitations, stated plainly

No verification against real launchd: every run used a stateful fake, and the D2
wire signature is pinned by a test rather than re-probed against this macOS
build. **No `fsync` anywhere** — `os.replace` gives atomicity, not durability, so
power loss (as distinct from SIGKILL, tested at 14 seams) is untested.
Concurrent installers can lose each other's `.prior` journal; D7 rejected a lock
file deliberately on the premise of one sequential operator. `<custody_root>/night`
is created world-listable (0o755) — **pre-existing, byte-identical to the old
installer**, flagged for its owner outside this lane.

### Residual risk — Bridge protocol §7

See `lt-92`, which names every session that ran without a baseline manifest or
lease (the lieutenant's, before 12:06 PDT; and the magistrate's own seats today),
what compensated (lead-only pathspec commits, independent refuters and deltas,
bench re-runs of every decisive verification), and the disposition: recorded as a
process finding, not re-run, with **BRIDGE-BASELINE-COMPLIANCE-01** going to the
council / cold gate.

## Commit series

| Sha | What |
|---|---|
| `8f334b8f` | D9 operator docs |
| `e867dee9` | the three-valued fake launchctl |
| `6dc86461` | the system-interpreter import guard |
| `490be1a3` | the engine (D1–D8/D10) |
| `96dee838` | fix round 1 — contract-refuter findings |
| `3b339ac9` | fix round 2 — the oracle correction |
| `53d95227` | fix round 3 — the caller tests |
| `d626bf64` | removal of a worthless assertion I wrote |
| `0ba6ce54` | fix round 4 — the Opus lens's two oracle defects + N3 |
