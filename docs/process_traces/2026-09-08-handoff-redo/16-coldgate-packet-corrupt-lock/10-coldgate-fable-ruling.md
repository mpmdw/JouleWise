# Cold-gate Fable ruling: corrupt-lock recovery (packet 2)

**Contamination disclosure.** The harness injected CLAUDE.md (global and project) and the memory index one-liners into my context before I read anything; I could not unload them. I read only the packet (sha256 verified a53faccf…), exhibits A–E, `scripts/magistrate_watchdog.py` and `docs/process/MAGISTRATE_WATCHDOG.md` at this checkout (main, e4ce8b3b), and the same two files plus the test file from commit objects 898e5305 and b3eeee9a (needed because the handoff helpers are not on main and exhibit B does not include the landing). No RUN_STATE, AGENTS, memory files, or doctrine.

## Executed evidence

Matrix (foreground, `git archive b3eeee9a` into /tmp, exhibit-B block extracted from the doc and exec'd with a mocked process table, corrupt bytes `{torn`, `{}`, `[]`; identical results for all three):

| process table | lock removed |
|---|---|
| empty | yes |
| saved owned pair live (100,T) | no |
| saved pid reused (100,T2) | yes |
| unrecorded `claude -p … --resume --reply-on-resume` pid 84232 | **yes** |
| unrecorded `claude -p resume` pid 84232 | **yes** |
| unowned interactive `--resume --reply-on-resume` | no |
| `claude daemon run` | no |

`handoff_process_role` of the headless shape is `None`; `_is_interactive_claude` is False. R1 reproduced.

Tick probe (`decide()` at b3eeee9a, corrupt lock, state `{}`, midday, no plans): headless resident live and no twin → `LAUNCHING`, lock unlinked. Resumed twin live → `HOLD_UNSAFE dead_lock_resumed_twin`, lock kept. Empty table → `LAUNCHING`, lock unlinked.

## Findings

1. **R1 is confirmed and is a real overlapping-ownership path.** The saved inventory binds to whatever step 3 recorded, not to the corrupt lock's owner. A stale or unrelated inventory plus an unrecorded headless resident removes protection. The block cannot prove owner absence from that input.

2. **The packet's P rationale is factually wrong on its safety claim.** "The watchdog's own tick already refuses to launch on an invalid lock" is false at 898e5305, b3eeee9a and main. `read_lock` maps corrupt bytes to `{}`; `owned_process({} …)` returns None; the tick treats that as a dead owner and unlinks unless a `--resume --reply-on-resume` interactive twin is visible (898e5305:1359-1367; main:1219-1222 has not even the twin check). The watchdog spawns exactly a headless `claude -p` session (`session_argv`, b3:1451-1461), so corrupt lock plus a resident whose supervisor died equals: next tick unlinks, launches a second resident. This is the R1 failure with no operator involved, sitting in code, not in a doc block. Both dispositions in the packet leave it open. Exhibit D's "live lock validated by PID and start token" is silently not the rule for an unparseable lock.

3. **Failure-mode test.** P as written: the doc block is fail-closed, but the tick can unlink while a possible owner is alive (finding 2), so P fails the test. F2: a command-shape census is a classifier over `ps` text; a renamed binary, a wrapper, or a test stub escapes it, and the tick still has the finding-2 path. F2 fails the test too.

4. **A binding identity exists and is unused.** `state.json` carries `resident_session` in the lock schema with PID, start token and activation (b3:2099-2107 already uses it for drain adoption). It is the second copy of the same ownership record the lock holds. Recovery bound to that record needs no classifier: pair live → refuse; pair absent, no twin, no daemon → owner proven gone, unlink; `resident_session` missing or malformed → fail closed. The doc block should take the same record, never a step-3 inventory, which describes the interactive twin's tree and not the lock owner.

5. **D-161 question.** D-161 retires guards against a deliberate operator. A corrupt lock is a mistake state, and the guarded outcome is two magistrates owning one night, which is evidence-and-physics territory (double census, double custody writes). D-161's MISTAKE-vs-DELIBERATE test keeps this refusal. D-161 does apply to one thing: it licenses the Ed-hands fallback when the durable record is also gone, instead of demanding a mechanism for a state no evidence can resolve.

6. **Cost accounting for the hands-free week.** With finding 4, the common corrupt-lock case (resident crashed, state.json intact) recovers unattended and provably. Only "lock and state both unreadable" stalls to Ed, which is correct because nothing on disk can then name the owner.

## Disposition

Third disposition, call it **B (bind)**: revert the exhibit-B inventory mechanism; in both the tick's dead-lock branch and the step-4 block, treat `read_lock() == {}` as "consult `state["resident_session"]`", refuse if that pair is live, if any resumed twin is live, if any daemon is live, or if the record is absent or malformed; unlink only when the pair is provably absent. Regression: the tick matrix above (headless resident live, corrupt lock, populated `resident_session` → HOLD, lock kept; record absent → HOLD, lock kept; pair gone → unlink). Document Ed-hands recovery only for the both-unreadable case. NOT EXECUTED: a live-process run; all tables were injected.

**Verdict: neither P nor F2; rule B (bind recovery to the durable `resident_session` record, fail closed without it), and fix the tick's own corrupt-lock unlink first.**
