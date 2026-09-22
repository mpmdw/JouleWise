# Record 01 — D-183: no artificial owner stops; `check` fast-forwards the canonical checkout itself

Interactive session `a87c3444` (Fable 5.1, Ed at the machine), 2026-09-21 21:37–23:xx PDT.

## §1 Forcing problem (executed evidence)

At 21:37 PDT Ed asked what was going on ("haven't got an email in a while").
Bench observation from the canonical checkout and the custody root:

- `git status -sb` in `/Users/edr/code/JouleWise`: `## main...origin/main [behind 157]`, HEAD `0959e613`.
- `state.json`: activation `21752427` ACTIVE since `Sun Sep 20 03:19:26 2026`, supervisor pid 80188; heartbeat 21:30 09-21.
- `RUN_STATE.md` on `origin/main` (pointer of 16:40 09-20): "THE ONE OWNER ACTION (unchanged since 05:10): fast-forward `/Users/edr/code/JouleWise`".
- Gmail sent items to `claude2.glaring610@passmail.net`: last message 05:10 PDT 09-20 (`1a0beb3c25241ce3`); nothing after.
- The stall: 05:10 09-20 → 21:40 09-21, about 40 h, with nothing armed and every merged PR green. The only precondition was a clean fast-forward the relaunch prompt forbade the headless session from performing ("Perform no git operation in the canonical root").

Ed's ruling (verbatim, 21:50 PDT): "make sure no more idiotic stops artificially, you have gh auth for a reason"; "obviously idiotic and should not have a 40h stall, def fix stuff like that, the process is meant to prevent bad science not work for 40h".

## §2 Actions at the bench

1. 21:40:47 `git -C /Users/edr/code/JouleWise pull --ff-only` → HEAD `7e35d16a`; `git merge-base --is-ancestor 980f8d64 HEAD` → true (cure present).
2. The holding activation's hold watch saw it, pushed its exit block (`9e0a4995`) and exited; the watchdog logged `clean activation exit` (event 283) then a 300 s `BACKOFF_USAGE` (event 284). Its exit note records that the headless session's Gmail auth had expired, so its exit email never went out (preserved on disk).
3. Fix branch `fix/2026-09-21-canonical-self-fast-forward` in worktree `JouleWise-wt-selfff` off `9e0a4995`.

## §3 The change

- `joulewise/evidence_night.py`: `canonical_status`, `canonical_fast_forward` (clean tree → `git pull --ff-only` → re-check H; evidence `{before, after, pull}`), `canonical_check(..., may_fast_forward)`; `check` passes `may_fast_forward = <night_agents check passed>`.
- `tests/test_evidence_night.py`: `test_canonical_fast_forwards_itself_when_nothing_is_loaded` (old → tip; `fast_forward` null and no pull when H present), `test_canonical_fast_forward_refuses_dirty_tree_and_loaded_agents`, and the amended `test_canonical_must_contain_h_and_be_clean` (no upstream → `fast-forward failed`, HEAD unmoved).
- Docs: `MAGISTRATE_RELAUNCH_PROMPT.md` (one licensed move; exit-for-successor instead of holding), `MAGISTRATE_WATCHDOG.md` line 189, `docs/contracts/evidence_night_entry.md` item 1 (+ the "no command fast-forwards" sentence), `docs/decision_log.md` D-183.

Soundness fences unchanged: nothing moves while a night label is loaded or a plist is present (item 0 failed → pull not licensed); no reset or force; dirty trees refuse; the supervisor-freshness rule (records 19/21) still refuses the session's own stale supervisor, which is now the documented hand-off, not a hold.

## §4 Bench evidence

- Targeted: `pytest -q tests/test_evidence_night.py -k 'canonical or census_fix'` → `4 passed, 90 deselected in 3.09s` (after fixing one assertion slice, `c[-3:]` → `c[-2:]`, in the new test).
- Full affected modules (`test_evidence_night`, `test_docs_freshness`, `test_identity_pins`, `test_schemas`, `test_magistrate_watchdog`): see §6.

## §5 Reviews

- Opus counter-review (contract lens): see §6.
- Sol refuter (execution lens, counterfactual repos + mutation probe): see §6.

## §6 Results (filled as they land)

### §6.1 Full affected modules, round 1 (head `98e05bba`)

`pytest -q tests/test_evidence_night.py tests/test_docs_freshness.py tests/test_identity_pins.py tests/test_schemas.py tests/test_magistrate_watchdog.py` → `2 failed, 300 passed, 1 skipped, 1044 subtests passed in 177.16s`. Both failures in `test_docs_freshness` (decision index vs bodies; dangling `D-183` references): the D-183 index row existed but its `## D-183:` body did not. Fixed by appending the body; `tests/test_docs_freshness.py` → `31 passed, 383 subtests passed`.

### §6.2 Opus counter-review (contract lens, on `98e05bba`) — VERDICT FIX-FIRST, no BLOCKER

Findings and dispositions (lead-triaged; nothing silently applied):

| # | Tier | Finding | Disposition |
| --- | --- | --- | --- |
| 1 | NIT | Contract parenthetical for item 0 omitted "discovery known" (code is the conservative superset). | FIXED: contract item 1 text now lists all three conditions. |
| 2 | SHOULD-FIX | Prompt licensed a bare hand-run `pull --ff-only` with a weaker prose precondition than the code's. | FIXED: prompt licenses the move via `check`, or by hand only after confirming no `com.joulewise.night*` label loaded and no plist on disk. |
| 3 | SHOULD-FIX | Stale-supervisor refusal after an in-check move surfaced only as the generic `pre-arm checks failed`; a headless loop could re-run `check` forever. | FIXED: the refusal text names the hand-off ("commit, push and exit so the watchdog's successor arms (D-183)") and `check` re-raises exactly the stale case as its own cause (other supervisor causes stay generic — two existing tests pin that). |
| 4 | SHOULD-FIX | No test for the post-pull still-lacks-H branch. | FIXED: `test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence` (upstream advances without the fix; HEAD moves old → other; refusal names both shas). |
| 5 | SHOULD-FIX | No test of the records-19/21 hand-off after an in-check move. | FIXED: `test_fast_forward_makes_the_resident_supervisor_stale_and_says_so` (supervisor started before the move refuses with the named hand-off; one started after passes). |
| 6 | SHOULD-FIX | Evidence of a pull that moved the tree was discarded when the check then refused. | FIXED: the still-lacks-H refusal carries before/after shas in its cause; `clean_before` observation retained in the evidence. |
| 7 | SHOULD-FIX | The pull had no timeout and inherited stdin: an unreachable remote or credential prompt would hang the unattended loop — the stall class D-183 removes. | FIXED: `FAST_FORWARD_TIMEOUT_S = 120`, `GIT_TERMINAL_PROMPT=0`, `TimeoutExpired` → refusal; `test_canonical_fast_forward_is_bounded_and_prompt_free` pins both. `probe_command` gained an `env` merge parameter. |
| 8 | NIT | Clean-before-move observation dropped. | FIXED with 6. |
| 9 | NIT | Still-lacks-H message differed from the documented cause prefix. | FIXED: prefix `canonical fast-forward failed:` on every refusal of the move. |
| 10 | NIT | Divergent upstream and plist-present-but-ABSENT branches untested. | ACCEPTED as nits: divergence is a real `--ff-only` rejection routed through the same `returncode` refusal the no-upstream test exercises; plist presence is item 0's existing coverage. |
| 11 | NIT | TOCTOU between the item-0 sample and the pull for a *different* candidate's install (seconds wide, single-operator machine). | ACCEPTED: the per-candidate lock does not cover it; the pull is fast-forward-only and the other candidate's own `check` re-observes. Recorded, not fixed. |
| 12 | NIT | Pull stdout/stderr recorded verbatim could carry a remote URL. | ACCEPTED: the remote is a public GitHub URL without credentials; revisit if a credential-bearing remote is ever configured. |

### §6.3 Full affected modules, round 2 (after the Opus fixes)

`pytest -q tests/test_evidence_night.py tests/test_docs_freshness.py tests/test_magistrate_watchdog.py` → `224 passed, 692 subtests passed in 175.07s`, exit 0. Two fix iterations inside the round, both test-side: a wrapped runner that delegated to the real `probe_command` let a real `pgrep` see the live successor magistrate (never delegate past the fixture runner), and the bounded-pull test first expected the canonical reason on the raised line (only night_agents, census and the stale-supervisor case are re-raised verbatim; canonical stays under the generic line).
