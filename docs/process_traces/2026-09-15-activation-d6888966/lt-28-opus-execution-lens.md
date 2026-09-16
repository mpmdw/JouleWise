# lt-28 — The execution lens, as a fresh OPUS seat

Written 18:07 PDT 2026-09-15 (clock read). Audited head `3b339ac9`; engine
sha256 `756fe0f0…`, shell sha256 `26010c85…`, byte-identical at session end.
Evidence under `/tmp/exec-lens-out/`; the seat worked read-only in a complete
`cp -R` copy at `/tmp/opus-exec-lens`.

## Why an Opus seat and not a fourth Codex one

Three Codex attempts at this lens died on **their own harness** — a 180 s cap, a
0.12 s launchctl timeout, and a git-archive snapshot with no git metadata — never
reaching an attack. That is a tooling signature, not a code one, so the
magistrate directed a fresh Opus seat with a complete copy, an adapter timeout
≥ 2 s and no wall limit below 20 minutes. It ran ~700 installer invocations.

## VERDICT

```
class_1: NO
class_2: NO
```

**No witness for either**, across: an 88-run class-2 enumerated product (six
`print` faults × three call sites × both labels; teardown `bootout` rc {0,1,113}
× {leaves loaded, unloads}; uninstall in each world and twice in a row); 12
STAGED-branch teardowns; 26 class-1 clock advances at 11 seams; **112 signal
cases including SIGKILL at 14 seams**; 187 fault-biased and 310 success-biased
fuzz runs (148 of the latter exiting 0, which is precisely where class 1 would
live); 114 uninstall-focused fuzz runs; and an exhaustive 96-case start-state
matrix under REALISTIC launchd semantics (bootstrap of an already-loaded label
returns rc 5).

**All 23 D10 must-die mutants RED**, plus two sharper I4 variants.

Three corroborations worth keeping: the fake's own `bootout_before_remove`
oracle (both plists must exist at EVERY bootout) never tripped in ~700 runs;
`installed_agent_fence()` never returned `None` while the stub said a label was
loaded and the plan was span-active; and **from all 32 arbitrary starting machine
states — including I3-violating ones it planted — a single `--uninstall`
returned 0 (32/32) and the following install returned 0 (32/32)**, with the
installer refusing (exit 3) and leaving planted loaded-with-no-plist states
alone rather than "fixing" them.

## The methodology correction, which is the most valuable thing in the report

Its FIRST mutation pass returned "RED" for every mutant — and then a **null
control (an unedited copy) also came back RED**. It stopped, isolated the cause,
and found that a shell job started with `&` inherits **SIGINT as `SIG_IGN`**,
which children keep across `exec`, so the harness's
`os.kill(os.getpid(), SIGINT)` did nothing. It fixed the runner and re-ran
everything, and **three null controls then SURVIVED** — that is the baseline that
makes its verdicts mean anything. It declares its first pass void and says it
should not be cited.

A seat that runs a null control, discovers its own instrument is lying, and
throws away its own completed work is doing the thing this lane has needed all
day.

## Two should-fixes, BOTH IN THE ORACLE, not the product

**S1 — one uncovered cell, and it is the runbook's own worked example.** The
combination "commit gate refuses from `VERIFIED`" × "a teardown liveness query is
LOADED/UNKNOWN" has no test: `retention_product` only ever ENTERS retention via a
bootstrap failure, and the commit-refusal test uses clean queries. The engine is
CORRECT there (executed: rc 4, plists and sidecars retained). The gap is real:
the mutant `night_agent_install.py:394` → `if unresolved and self.state is not
State.VERIFIED:` **SURVIVES the whole suite**, silently turning the documented
exit 4 into exit 1. That matters because `NIGHT_HANDBACK` stops retirement and
successor arming on 4, while 1 is the different "failed restoration" row.

**S2 — six cells silently assert nothing under an inherited `SIG_IGN`.** The
signal cells depend on the inherited disposition at `PARSED`/`VALIDATED`/
`ADMITTED`, before the engine installs handlers. Under `&`, `nohup`, launchd or
most CI runners the transaction runs to completion and the cell reports a
SUCCESSFUL ARM where an interrupted rollback was expected — this lane's own
failure shape, appearing in the instrument.

**I verified S2 at the bench myself:** `signal.getsignal(signal.SIGINT)` is
`default_int_handler` in the foreground and `1` (`SIG_IGN`) under `&`.

**And S2 explains my own row-9 replay result.** The sharded full suite reported
`failures=1` in 6133 tests; shard 3 re-run alone passed 1433/1433. I had
hypothesised a 0.75 s adapter-timeout flake and started changing timeouts — that
guess was wrong and I reverted it uncommitted. The replay runs under a background
shell, so SIGINT is `SIG_IGN`, and the failure is S2's class. **The Opus seat's
diagnosis beat mine, and it had a null control where I had an inference.**

## Nits recorded (N3–N9)

N3 a dangling option value (`--plan` last) hits an unguarded `shift 2` and exits
1 instead of the documented usage 2 — folded into fix round 4. N4 the
`re-run --uninstall` remediation is unactionable in render-only mode. N5 an I/O
failure during uninstall exits 1, an outcome the runbook's §1.4 table does not
list. N6 a `launch_dir` that is a regular file escapes as a raw errno rather than
`unsupported plist destination`. **N7 `<custody_root>/night` is created 0o755 and
`run_night.py:1435` then skips its own 0o700 `mkdir` on `FileExistsError`, so the
night control directory stays world-listable — PRE-EXISTING, byte-identical
behaviour in the old zsh installer, flagged for its owner and out of this lane.**
N8 concurrent installers lose each other's `.prior` journal (D7 rejected a lock
file deliberately). N9 `installed_agent_fence` blocks forever on a FIFO plist —
watchdog code, operator-adversary class.

## What it could not verify, in its own words

Anything against real launchd (the D2 wire signature is pinned by a test, not
re-probed against this build); **durability — there is no `fsync` anywhere, so
`os.replace` gives atomicity but not persistence, and power loss is untested**;
the clock-reversal attack (attempted, no witness, claimed nothing); the D9 docs
migration as a whole; and `plan_span_active` itself.

Its own summary of the ship decision: *"I could not break I1–I4 … the three
constructions the design bets on — the single mutation channel, the
proof-carrying deletion, and the one commit predicate — held under every fault,
signal, kill, clock jump, hostile filesystem shape and randomised campaign I
could execute."*

## Disposition

S1, S2 and N3 are dictated to fix round 4 (Astra xhigh, pid 17236, launched
18:06:08), each with the executed witness the Opus seat supplied and, for S1, the
surviving mutant that must go RED. N4–N9 are recorded; N7 needs an owner outside
this lane.
