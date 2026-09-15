# lt-20 — Granted scope expansion (stub repair), and delta 3

Written 11:17 PDT 2026-09-15 (clock read). Head at delta-3 launch: **`073a9763`**.

## SCOPE EXPANSION — granted by the magistrate, recorded here and for the PR body

**Grant:** this lane's WRITE_SCOPE is extended by **`tests/test_run_night.py`**,
limited to **the launchctl stub text and any call-count / log assertions that
the stub change makes true**; the tests' behavioural assertions stay. This is a
**scope note, not a contract change** — no decision in the design adjudication,
no kernel clause, no refusal code and no invariant moves.

The magistrate bench-verified the premise before granting: at `d74b5ff1` both
uninstall tests fail with rc 4 "still loaded after bootout", and the stub at
`:1836/:1872/:1906` was `print -r -- "$*" >> "$LAUNCH_LOG"; exit 0` for **every
verb**.

Why it was needed: that stub answers `print` rc 0, so after a successful bootout
it still reports the label LOADED. Round 3's verified-bootout uninstall then
correctly concludes both labels survive and exits 4. **The production code was
right; the fixture encoded a launchd that cannot exist** — a real
`launchctl print` after a successful bootout returns non-zero. The two options
were to repair the fixture or to weaken the ruled uninstall block; the second
would have reverted cold gate 28, so the seat was forbidden it and so was I. I
did not grant the expansion myself: it is the magistrate's, never the
lieutenant's.

## The repair (seat pid 1183, Astra high, 11:08:48 → 11:14) — landed `073a9763`

All five stub sites now mirror the marker pattern already used by
`tests/test_install_night_agent.py:76-82`: every call still appended to
`LAUNCH_LOG`; `bootstrap` creates the label's marker; `bootout` removes it;
`print <label>` exits 0 only while that marker exists, 1 otherwise.

Both uninstall tests now observe **rc 0**, **both plists removed**, and the log
ending exactly `bootout / bootout / print / print` — a tail that was NOT asserted
before and now is, at `:1946` and `:1991`. **No existing assertion was changed or
removed and no call count needed adjusting**; AST comparison confirms the file is
identical outside the five stub strings and the two added tail assertions.
Mutation: reverting the marker-aware `print` to `exit 0` turns both tests RED
again at their unchanged rc assertions (`4 != 0`).

Lead-run at `073a9763`, each module separately: `test_run_night`,
`test_install_night_agent`, `test_magistrate_watchdog`, `test_night_gate`,
`test_docs_freshness`, `test_gen_state` — **all OK. The tree is green again.**

## Delta 3 (fresh Astra xhigh, pid 9917, launched 11:16:48)

Disposable detached worktree `wt-ref-iw-contract` at `073a9763`. Brief
`/tmp/magistrate-d6888966/brief-14-delta3.md`. Four tasks, exactly as directed:

1. **Isolated reversion of EACH of the three round-3 edits**, one at a time with the other two in place; each must turn its own regression RED.
2. **The same-signature question answered ONLY by synthesis 13 §Q3's two executed predicates**, quoted into the brief verbatim so no other definition can be substituted:
   - **class 1** — the installer exits 0 with either label loaded while a clock read taken after the commit gate is at or past `min(selected_span_close, install_close_epoch)`;
   - **class 2** — any path ends with a label loaded and its plist absent, **or** exits 0 while a label it attempted to bootout is still loaded.
   The brief says in terms that a clean NO backed by real attempts is as valuable as a finding, because this answer decides whether the lane proceeds or is redesigned.
3. **By-name re-run of both open survivor lists**: lt-04 §F4's 22 (enumerated in the brief with sites and counterfactuals) and lt-10-delta2's 8 `teardown` + 3 tail survivors (verbatim table). The **§Q5 must-die set** is named individually and is binding for landing: any survivor removing or defeating `trap - EXIT`, the `exit 4`, either `print` re-read, `cp -p`, the render-only guard, or the `:312` success guard must be RED. Diagnostic-wording survivors are text-only.
4. Hygiene: seven modules separately, §3 digest, and a judgement on **every** pre-existing test/assertion/fixture the round touched — explicitly including this stub repair and the `test_install_night_agent.py:216` count changes — asking whether any BEHAVIOURAL assertion was weakened or any case dropped.

## The stop condition I remain under

If delta 3 reports an executed class-1 **or** class-2 case at this head:
**no fix seat, no round 4** — I hand back, and the magistrate convenes the
redesign consult (three seats on a transactional installer: one Python state
machine with a single commit and a single teardown, the shell reduced to
argument parsing) and emails Ed. The count is per CLASS, not per site. The
decider is the magistrate.

If clean: fresh Opus counter-review (row 6, a NEW Opus seat — not me, since I
directed every fix round), replay at the final head (row 9), fresh-eyes on
post-review commits (row 10), refresh `lt-90`/`lt-91`. No PR, no merge.
