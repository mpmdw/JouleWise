**Verdict: MERGEABLE.** No blockers. Four should-fix items, which can ride this change or a follow-up lane, and four nits.

**What I ran**
- At c9e2bd14: `python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign` passed: 285 tests OK, exit 0, 733 s. The machine was shared with the Sol refuter seat, which is why it took so long.
- Counterfactual: I made a throwaway worktree at 313efcca with the new test files, then removed it. All three new tests fail there, with 4 failures:
  - "Refused not raised" for v2.
  - "'8,020-second program' not found" (the old text says 7,800).
  - the unfiltered-SD label is missing, in both summary subtests.
- I rendered the v3 notice directly. It works with both an absolute and a relative registration path.

**(1) Each notice and summary sentence checked against the code that enforces it**
- **"8,020-second program fits inside the 9,000-second window": true.** It is computed from the registration (600 + 11×620 + 600), matching `quiet_predicate_campaign.py:1474-1482`. `manifest_for` at :158 enforces plan window = 9000 s.
- **"at or above 0.5 busy cores refuses the night at the arm check or at t0": true.**
  - `night_gate.py:190` sets `T0_NON_OBSERVER_SHARE_MAX = 0.5`.
  - `:846-851` compares with `>=` inside `_check_machine`. That runs on both paths: `evaluate_dynamic_hard` at :1727 with `legacy_load=False` (arm check), and `evaluate_night` at :1772 (t0).
  - The notice takes the number from the registration field, not the gate constant. `test_night_gate.py:1474` asserts the two are equal, so they cannot drift apart.
- **"30 or more core-seconds inside an envelope excludes that envelope": true.** `quiet_predicate_campaign.py:1024` keeps a process when `total >= rule["bar_core_seconds"]`.
- **"2 such exclusions in a row end the night": true.** Lines 1643-1645 count `consecutive_non_observer` and raise `NonObserverAbort` when it reaches `abort_after_consecutive`.
- **corecaptured sentence: true with one caveat.** `night_gate.py:1526` refuses when `spawns.count > corecaptured_loop.SPAWNS_MAX`, and `SPAWNS_MAX = 2`. But the check lets the night through when the log read fails: lines 1520-1521 record `"status": "not_measured"` and no refusal follows. So "the night is refused … if" is not unconditional. The wording is mandated, so this is a nit.
- **Summary v3 sentence: true.** The new unfiltered-SD label matches `:1344` (all envelopes with a non-None joule value, excluded ones included).

**(2) Acceptance clauses**
- Every clause has a test that fails on 313efcca and passes now.
- The notice tests call `render_notice` directly with a hand-built state. The only test that goes through `notice()` is the lifecycle test, which now binds real v3 but does not assert any of the v3 sentences. The acceptance text names `render_notice` itself, so this is acceptable.

**(3) Can the new refusal block the next legitimate arm?**
- The next arm pins `PROTOCOL_PATH`, which is v3 (digest `69321c69…`). That equals `QPE01_PILOT_REGISTRATION_SHA256` and is armable, so the refusal cannot fire.
- **S1 (should-fix), evidence_night.py:277-289.** The armability decision imports `night_gate` from the checkout running the command, not from the candidate commit H. That breaks the module's own rule at :482, "Author with H's code, never the caller checkout's imports", and the lesson "every evidence lens runs in the clone's python".
  - Counterexample after A278 lands v4: `prepare` without `--head` sets H from `ls-remote` (:373). If the running checkout has not pulled v4 yet, `prepare` reaches `render_notice` at :539, after the clone and venv build, and refuses with the misleading "unknown or superseded".
  - It fails closed and resumes after a pull, so this is not a blocker.
  - Cure: put the armable/current check inside `sealed_candidate`'s code, which runs in H's interpreter. If "the running checkout knows H's registration was superseded" should also refuse, keep that as a separate refusal with its own message.
- Once v4 lands, v3 plans are correctly refused.
- **S2 (should-fix).** `tests/test_evidence_night.py:67` and :2175 hard-code `pilot_protocol_v3.json`. After A278 both will raise Refused("superseded"). They should use `night_gate.QPE01_PILOT_REGISTRATION_PATH`.
- If v4 drops `t0_non_observer_share_max` (arm_retry.py hints "For v4 … the CPU cutoff is a sealed plan parameter"), `render_notice` raises KeyError instead of Refused. A278's brief should name this.

**(4) The dropped git-show sentence**
- Dropping it is right, but the seat's count is wrong. A night runs at least 17 read-only `git show`s, not 1 + 8:
  - 1 at the t0 chain check (`night_gate.py:1356`).
  - 8 from `verify_environment` → `manifest_for` for the executor's `run` (`MANIFEST_PATHS` has 8 files).
  - 8 more for the recorder subprocess (`quiet_predicate_campaign.py:1528` launches `… record`, and `main()` at :1737 calls `verify_environment()` first).
- The driver also runs `checkout -B`, `commit` and `push` in the results clone (`run_night.py:1084`, 1111, 1118).
- **N1 (nit).** The notice now says nothing about git activity during the night. Consider a true replacement sentence (read-only `git show` checks in the measurement clone; the results are committed and pushed from a separate results clone).

**(5) Terms undefined for a reader with no project grounding**
- **S3 (should-fix, Ed's writing standard).** The new lines use four undefined terms:
  - "busy cores": never glossed.
  - "core-seconds": the queue row's own gloss, "busy cores times seconds", was not carried over.
  - "measurement apparatus": means the night's own process tree.
  - "the arm check": never defined, and "t0" sits beside "at its start" as a second name for the same moment.
- **S4 (should-fix).** The rendered line reads "After 600 seconds settling, 12 600-second idle envelopes …". "12 600" can be read as 12,600 seconds; the old text said "twelve". The sentence "2 such exclusions…" starts with a digit.
- **N2 (nit).** The corecaptured line is lowercase with no full stop. A prefix such as "At t0, " plus a full stop would still contain the mandated wording verbatim.

**(6) Other nits**
- **N3.** `docs/contracts/evidence_night_entry.md:431-433` lists the refusals that happen before output. It does not list the two new ones: "registration differs from sealed binding" and "unknown or superseded". This needs a bookkeeping edit outside this change's write scope.
- **N4.** "every captured envelope" in the summary leaves "captured" undefined; "every envelope with a joule value" says what the code does. The summary still never prints the retained-only `single_envelope_sd_j` (1.84 J on the 07:00 night). Relabelling the unfiltered figure is an adequate cure for harvest §7 item 2.
- The second clause of the refusal condition at evidence_night.py:288 is redundant. It is harmless.

The repo is unchanged by this review; the throwaway worktree has been removed and pruned.