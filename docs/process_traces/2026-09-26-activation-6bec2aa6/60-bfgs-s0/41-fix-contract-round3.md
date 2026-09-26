# S0 fix round 3: lead-written FIX contract with dictated closures (magistrate 6bec2aa6)

**Findings covered.** Lens reports 31 (Sol), 32 (Astra) and 33 (Opus) on `26ab7234`.
- Each closure below is dictated; implement it as written.
- Items marked **[ADD2]** are ruled by cold addendum 2 (`40-addendum2/21-…`); its text is quoted verbatim in the seat brief and governs.
- Every closure gets a defect-shaped regression test that is RED on `26ab7234` for the stated reason. Paste the RED proof.

## Closures (dictated)

- **C1 (Sol F3 / Astra R1, BLOCKER): an unreadable round journal.** In `authenticate_quiet_session`, `rounds.jsonl` is handled by what it contains:
  - **Missing:** zero rows. The refusal-shape envelope writes it empty.
  - **Empty:** zero rows.
  - **Any non-empty line that is not a JSON object, or a file that cannot be read:** raise `CustodyFailure("round journal unreadable: <reason>")`.

  A journal that cannot be parsed is never converted to zero rows.
  - Regression 1: a digest-mismatch journal raises.
  - Regression 2: the same journal replaced with malformed JSON also raises, where it currently passes.
- **C2 (Sol F2 / Astra R2, BLOCKER): spans.** **[ADD2 Q1]** governs the quiet span source. In `authenticate_pair`, whenever `span` is given, it must be a 2-tuple of non-bool ints with `0 ≤ start ≤ end`; anything else is `battery_float_evidence_missing: span malformed`. This applies at the span rung only, after custody, probe, parse and predicate, so a malformed span never preempts `CustodyFailure` (Astra R2's second half).
  - For kinds `bundle` and `quiet`, `span` is **required**: `span=None` is `evidence_missing: span required` (Opus N-1).
  - Regressions: a reversed span; a bool span; a float span; custody that raises despite a malformed span; bundle and quiet authenticated with `span=None`.
- **C3 (Sol F4 / Astra R5): symlinks.** Before reading a raw file, `lstat` every path component from the container root down to the file. Any symlink, or a resolved path outside the container, raises `CustodyFailure("raw path traverses a symlink: <component>")`. Open the file with `os.O_NOFOLLOW`.
  - Regression: a symlink to an outside file with matching bytes raises.
- **C4 (Sol F5 / Astra R3): duplicate keys.** Every JSON decode in the wrappers (`session.json`, `metadata.json`, `events.jsonl` lines, `rounds.jsonl` lines, `instrument_evidence.json`) uses an `object_pairs_hook` that raises `CustodyFailure("duplicate JSON key <k> in <file>")`.
  - Regression: a foreign value followed by the expected value raises.
- **C5 (Sol F6 / Astra R6 / Opus N-4): the fence and a missing flag.** In `evidence_night.check`, the fence evaluates `getattr(row, "battery_brackets", None) is True`. A missing attribute is a failed inspection that journals the normal refusal record; it never raises.
  - Regression: an injected kind without the attribute is refused, with the check journal written.
- **C6 (Opus S-4): stale `check.json`.** `require_fresh_check` also requires `checked["checks"]["battery_brackets"]["verdict"] == "pass"`, and otherwise refuses with `"check.json predates the battery_brackets fence"`.
  - Regression: a hand-written armable `check.json` without the row is refused.
- **C7 (Opus S-1): pins cover dependencies.** Extend the text-3 pins to each frozen function's module-level dependency closure. Compute the transitive closure over the `Name` loads that resolve to module-level functions, classes or assignments in `battery_float.py`. Pin `ast.get_source_segment` of each closure member in the same regenerable `FROZEN_FUNCTION_SOURCE_SHA256` table, keyed by name.
  - A self-test mutates `_signed` in a copy of the module and shows the pin RED.
- **C8 (Opus S-2): guard evasions.** Extend the text-4 guard. Outside `joulewise/battery_float.py`, over `joulewise/` and `scripts/`, flag:
  - (i) any load of `PairVerdict`, whether a bare from-imported name or an attribute through a `battery_float` module alias, except as the second argument of `isinstance`/`issubclass` or inside an annotation;
  - (ii) any call to `dataclasses.replace` (however imported) in a module that imports `joulewise.battery_float`;
  - (iii) any `getattr(<battery_float alias>, <str>)` call;
  - (iv) any `type(<expr>)(...)` call in a module that imports `joulewise.battery_float`.

  Self-tests: each of the four forgeries Opus executed (E7) is flagged, and the legitimate `isinstance` use is not.
- **C9 (Opus N-2): exit code.** Rung (c) treats `exit_code` as success only when `type(exit_code) is int and exit_code == 0`.
  - Regression: `False` and `0.0` are `evidence_missing`.
- **C10 (Opus N-5): fence tests.** Add dedicated tests that no `skipped` state exists for `battery_brackets`, and that it is not in the `("machine_quiet", "corecaptured")` exemption. Add a test for the unreadable-kind branch.
- **C11 (Opus N-6): the `PHASES` sweep.** Resolve aliased imports: `from joulewise import battery_float as bf`, `import joulewise.battery_float as x`, and `from joulewise.battery_float import observe [as o]`.
  - Self-test: an aliased out-of-set phase literal is flagged.
- **C12 [ADD2 Q2]: `bundle_sha256` and `authenticate_window_members`.** Placement and field as ruled.
- **C13 [ADD2 Q3]: capture identity binding.** As ruled.

## Out of scope for round 3 (the lead handles these)

- Recomputing the pins after rebasing onto A309 (#426) is lead bench work after #426 merges.
- The pin test must name `10-liveness/ex-01-dictated-closure-M1.md` as the `load_committed_verdict` baseline (A309 Fable obligation 2). The seat adds that docstring now.
