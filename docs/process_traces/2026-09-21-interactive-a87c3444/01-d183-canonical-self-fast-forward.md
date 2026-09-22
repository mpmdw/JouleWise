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

### §6.4 Sol refuter (execution lens, gpt-5.6-sol high, read-only, on `98e05bba`) — VERDICT BLOCK on that head; delta re-audit on `c84f4db0` clears it

Executed by the refuter against the real functions with counterfactual repositories (its scripts: `/tmp/canonical_counterfactuals.py`, `/tmp/run_canonical_mutation.py`, `/tmp/pull_bound_probe.py`): (a) diverged upstream → refused (`Not possible to fast-forward`), HEAD unmoved; (b) deleted remote → refused, HEAD unmoved; (c) upstream on a branch without H → refused but HEAD moved and the structured evidence was discarded; (d) untracked file → fast-forwarded with evidence; (e) staged change → refused, HEAD unmoved. JSON serialisation of real records OK. Mutations on `98e05bba`: `may_fast_forward=True` killed by the loaded-agents test; the post-pull containment guard replaced by `pass` SURVIVED.

| Tier | Finding (on `98e05bba`) | Disposition |
| --- | --- | --- |
| BLOCKER | Wrong upstream moves canonical before refusal while discarding before/after/pull evidence. | Same finding as Opus #6; FIXED in `c84f4db0`: the refusal names `HEAD moved <before> -> <after>`; `clean_before` kept. The move itself is inherent to `pull --ff-only` and stays within the checkout's upstream branch; documented in contract item 1. |
| BLOCKER | `git pull --ff-only` unbounded and prompt-capable (`pull kwargs: {}`). | Same as Opus #7; FIXED in `c84f4db0`: `timeout=120`, `GIT_TERMINAL_PROMPT=0`, `TimeoutExpired` → refusal. |
| SHOULD-FIX | Post-pull containment guard not pinned by any test (mutation survived). | FIXED in `c84f4db0`: `test_canonical_fast_forward_that_still_lacks_h_refuses_and_keeps_evidence`. |

**Delta re-audit (lead, bench, `c84f4db0`, the refuter's own scripts re-pinned with `sed 's/98e05bba:/c84f4db0:/'` and the mutation's target text updated to the new refusal):**

- `pull_bound_probe.py` → `pull kwargs: {'timeout': 120, 'env': {'GIT_TERMINAL_PROMPT': '0'}}`; `return keys: ['after', 'before', 'clean_before', 'pull']`.
- `run_canonical_mutation.py postpull_pass` → `FAILED (failures=1)` over the five canonical tests: KILLED.
- `run_canonical_mutation.py license_true` → `FAILED (errors=1)`: KILLED.

Same-signature statement: the two blockers and the should-fix are one fix round; their signatures (unbounded subprocess, evidence discarded on refusal, unpinned guard) do not recur in the delta. No round three.

### §6.5 Terminal review (Fable, full session context)

Merge candidate = the records-only head after this section (sha in the PR ledger row 12). Diff read in full at the bench: one function pair plus a flag in `evidence_night.py`, `probe_command` env merge, five tests, four doc edits, D-183 row + body. Fences verified by reading and by the refuter's executed cases: no move while loaded (item 0 gate, mutation killed), no reset/force (only `pull --ff-only`), dirty refuses (case e), bounded and prompt-free (probe). Verdict: MERGE on green hosted checks.

## §7 Second artificial stop found the same night: a refused 09-16 night root blocked `check` (retired at the bench)

Successor activation 29ea94df's first live `check` (21:58 PDT, candidate t0 22:38) refused on two items: `census` (two interactive Claude windows, expected until Ed closes them) and `retained_roots`: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916` classified UNKNOWN because it has neither `night/courier.sent` nor `night/result.json`. Bench facts: that night ran 09-16 (gate GO 09:45; dead-man refused at 13:20 while the chain was alive; `night/refusal.json` = `night_chain_alive`; chain exited 20:52) and its durable record is on `origin/night-results/d079-epoch-25g83-derivation-n1-20260916` (`6725e481`). The root had sat there since 09-16 because the earlier arm scripts never inventoried retained roots; the new `check` does, and would have refused every arm from now on. Under D-183 and the retirement precedent (`~/night-archive/*-plan-root-retired-<epoch>` for the 09-13 and 09-15 roots) the lead retired it at 22:03 PDT: SHA256SUMS + lstat inventory written first, `mv` to `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-plan-root-retired-1790053407`, digests re-verified after the move (0 mismatches). Nothing deleted. Follow-up for the successor: `retained_roots` should classify a root with `night/refusal.json` plus a pushed durable branch as retained, not UNKNOWN (lane to register: RETAINED-ROOT-REFUSAL-CLASS-01).
