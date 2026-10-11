SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/calibration_bracketing.py", "joulewise/b5/harvest.py", "tests/**", ".scratch-fix/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task. Commit nothing; leave your changes uncommitted in the working tree.

# Implement Erratum 3 in the harvest's desk program, exactly as the cold ruling admitted it

You work in `/Users/edr/code/JouleWise-wt-harvest-trigger`, branch `lane/2026-10-11-harvest-trigger-scope`, head
`0699abbb0881ce64b39c46ba07de568cc3848260` (the pinned harvest program; clean tree). A cold judge admitted a
prospective erratum to the sealed registration with corrections and wrote the complete rule: section D of
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/trigger-erratum/RULING.md`
(sha256 `becbf587bb84a61954060a19dc54f78517c088c8710e514d73bb31af0cdea260`). Read the whole ruling first
(sections A to E give the reasons and the code reading; section D is the rule), then the draft
`ERRATUM-draft1.md` beside it for the terms. **The rule is frozen: the program must implement section D
item by item; you may not change the rule.** If an item cannot be implemented exactly as written, do not
approximate it: implement everything else, and say in your report which item, why, and the nearest exact
behaviour.

## What to build (section D of the ruling is the authority; this list only orients you)

- Item 0: constant `ERRATUM_3_ADMITTED_AT_EPOCH_S = 1791738000` in `joulewise/b5/harvest.py` beside
  `ERRATUM_2_ADMITTED_AT_EPOCH_S`; the governed test is the same shape as Erratum 2's (int or float, not bool,
  finite, strictly greater).
- Item 1: keyword argument `trigger_scope` (`"sealed"` default, `"window_evidence"`, anything else raises) on
  `evaluate_calibration_bracket` and `calibration_bracket_for_bundles`; the wrapper passes it through in every
  call it makes; with `"sealed"` both return exactly what they return at this head, byte for byte, including
  the absence of the new keys. The harvest's one call passes `"window_evidence"` when and only when the
  attempt is governed. No other caller changes.
- Items 2 and 3: the window's own session; the three recorded-only events decided by EVENT, never by trigger
  name; with `"window_evidence"` the failing set at the second site is exactly
  `{"protocol_or_estimator_byte_change"}`; the own-pre-above-screen path stays as sealed.
- Items 4 and 5: every other failure exactly as sealed, in the present order.
- Item 6: the four new keys under `acceptance.prospective_rederivation` (present with `"window_evidence"`
  only), the order of `recorded_only_triggers`, and `acceptance.freshness.status`.
- Item 7: the flag condition unchanged; no flag code added, removed or reclassified.
- Item 8: `harvest.json` gains the top-level object `calibration_bracket` (written by every harvest of the new
  program, governed or not, with the exact keys and null/empty rules of item 8), `outputs` gains
  `withheld/bracket-evaluation.json` with its SHA-256, and `HARVEST_PROGRAM_FILES` gains
  `joulewise/calibration_bracketing.py`.
- Nothing of items 10 and 14 (claim consumers, the sensitivity bound): that is a later lane. Do not touch
  `joulewise/whole_window.py`, the analysis engine or any other file.

## Tests you must write and run (targeted modules only)

1. Sealed-scope identity: with `trigger_scope="sealed"` (and with the argument omitted) both functions return
   results equal to the pre-change behaviour on every bracket fixture the existing tests build, including a
   stale one. Assert it against values captured from the unmodified functions (for example by importing the
   module source at `git show 0699abbb0:joulewise/calibration_bracketing.py` into a separate module object
   inside the test, loaded from a string, and comparing outputs on the same inputs).
2. One test per item of section D items 2 to 6 and each line of the case list of item 5, including: another
   session's systematic capture recorded and bracket passed; with only the early return disabled the bracket
   would still fail at the second site (so assert the pass, which proves both sites); own valid capture below
   the range floor recorded and passed; doubling count at 48 or above recorded and passed;
   `protocol_or_estimator_byte_change` still fails; identity change still fails; own drift above the ceiling
   still fails; `bound_observations` None behaves as sealed whatever the scope; an invalid `trigger_scope`
   raises; the order (c), (b), (a) of `recorded_only_triggers`.
3. The worked example of section D (pre 28.00 ms, post 30.50 ms over a ledger shaped like the real one with a
   systematic capture in another session): status passed, operative bound 45.031 ms, the `harvest.json`
   object as the ruling prints it.
4. Harvest level: a governed plan (t0 above the constant) passes `"window_evidence"`, an ungoverned one passes
   `"sealed"` and still emits `calibration.bracket_acceptance_failed` on a stale ledger; `calibration_bracket`
   object in `harvest.json` in the governed, ungoverned and not-evaluated cases; the `outputs` digest; the
   checkout file list.
5. Two fixtures the ruling's gates name: (i) a stale ledger together with a stored verdict that records no
   source manifests (Erratum 2's recovery path in the stale state), governed; (ii) a GAMMA-shaped window in
   the stale state, governed. Each test prints or asserts the full list of window-removing codes that result.
   If any window-removing code arises FROM THE STALE STATE on a governed window, do not paper over it: report
   it as a defect with the code path. If the existing test helpers cannot build a GAMMA-shaped harvest
   fixture, say exactly what is missing and build the closest executed fixture.
6. The existing modules must still pass unchanged: `tests.test_calibration_bracketing`,
   `tests.test_harvest_b5_window`, `tests.test_harvest_b5_sources`, `tests.test_harvest_b5_p2harv`,
   `tests.test_harvest_b5_p3harv`, `tests.test_harvest_b5_rehearsal_compare`, `tests.test_bracket_binding_cli`.
   An existing test that pins the old checkout file list or the old `harvest.json` key set may be updated to
   the admitted text; list every such edit and why in the report.

## Hard rules

- Write only inside WRITE_SCOPE. Outside `tests/`, this lane may change exactly two files:
  `joulewise/calibration_bracketing.py` and `joulewise/b5/harvest.py`. Never edit the four pinned estimator
  files (`joulewise/reduce.py`, `joulewise/uncertainty_evidence.py`, `joulewise/powermetrics_fiducial.py`,
  `joulewise/adapters/powermetrics.py`), `joulewise/whole_window.py`, `scripts/**` or any config.
- Run only targeted test modules, with `PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest <module>`.
  Do not run `unittest discover` or `shard_tests.py`. No Homebrew command; no package install.
- No measurement work. Do not start another agent and do not call Claude or Codex by any route. No network.
- The owner's address and name go into no network request and no file.
- Scratch files go under `.scratch-fix/` in your working directory (inside WRITE_SCOPE), never under
  `/private/tmp` and never inside a custody root, runs root or harvest archive. Point `TMPDIR` there for
  tests. Delete `.scratch-fix/` before you end.
- Blinding. The block is blinded until its release event: nobody may learn a measured energy, power or
  duration of a claim window. You do not need any claim-window file for this task: do not open or run any
  program over `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/` or
  `/Users/edr/night-archive/harvest-v5-b5-*`. You may read the calibration ledger
  `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18/runs/calibration_observation_ledger.jsonl`
  (alignment bounds are calibration values). The passage below binds you word for word.

### The passage (from the magistrate brief, section 6; "you" is the magistrate, and it binds the seat the same way)

**What you may open before the release event** (the orchestrator's decision O-7 of 2026-10-07). The
registration's custody map (its section 8) lists the paths nobody may open before the release event and
calls the rest releasable. Decision O-7 gives you less than the map releases, on purpose: every file you do
not open is one that cannot leak a value into a record, an email or a repair. Where the two differ, follow
this list. Of everything a window and its harvest produce, you open only:

- `harvest.json` in a harvest's archive root: `verdict`, `claim_usable` and `exclude_window_reasons`, and
  also its member counts (`yield`), its list of failed collectors by name (`faults`) and `harvest_checkout`.
  You read them through the reading block of 4.5.
- `derived/code-identity.json` in the archive root (which paths differ between H_claim and the commit the
  window ran from).
- `night/hazard_result.json` in the window's custody root (the driver's verdict, the arm's verdict for each
  hazard, the yield counts for each stage, the reason codes the driver raised, the fault reasons), and the
  one word `result` of `night/g10.json`.
- `hazards/arm.json` in the window's custody root, the **arm record**: what the arm measured for each of the
  six hazards, its verdict for each, and so which hazard modules refused. Registration section 7.3 builds the
  **cause key** of an attempt that started no chain from this file (the cause key is what rule 1 below
  compares between two attempts of a pack: the hazard modules that refused, or the families of the
  window-removing codes), and the registration's custody map lists the file as a hazard measurement that may
  be read during the block (the orchestrator's decision of 2026-10-07 23:55 adds it to this list).

A consult seat that you convene may also read the monitor's contention journal,
`<custody root>/hazards/monitor/contention.jsonl` (process names and CPU shares). **Nobody opens
`derived/flags.jsonl`, `derived/exclusions.json` or `derived/window_flags.json`** (seal gate ruling SG-12):
they name, member by member, a reason code whose presence says something about a measured energy. The
harvest program reads them to compute `claim_usable`; you read `claim_usable` from `harvest.json`. Nobody
opens anything else under a custody root's `hazards/`, `flags/`, `operator-logs/` or `night/transcript/`, its
`night.log` or chain logs, a runs root, or an archive's `sources/` or `withheld/`, except a program that
prints structure only (the END STATE count below is one). Plan-time files written at the desk before t0 (the
plan, `window.env`, the staging directory) are not restricted. Testing that a file exists is not opening it.
Every brief you write for a seat carries this passage whole, from "What you may open" to here.


## Report

Item by item against section D (items 0 to 8): implemented where (file:line), tested by which test, and
anything not exactly implementable. The list of every existing test edited and why. The exact commands run
and their last lines (counts of tests, OK or FAILED). `git diff --stat`. Anything in the ruling's text you
found ambiguous while implementing, quoted.
