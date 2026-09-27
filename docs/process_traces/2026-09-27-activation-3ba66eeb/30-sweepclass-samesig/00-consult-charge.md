# Consult SWEEPCLASS-SAMESIG-01: is the S1 static read-site sweep closable, and what should fix round 3 implement?

This is a **rule-11 standing-escalation consult**: two consecutive review rounds have failed with the same signature. It is not a third erratum round. You are one of several independent seats: Sol 6.0, Astra 6 and Opus 5.5 answer blind and in parallel, and a cold Fable 5.1 judge then rules with all the reports. Disagree freely with anything below, including the framing.

## Background, built from the ground up

**The science fence.** A JouleWise energy number counts only if the laptop was neither charging nor discharging while it was measured (Ed's binding directive #421). Every capture ("bundle") therefore carries two battery readings. The one function that reads them is `joulewise/battery_float.py`; its verdict is `pass`, `confounded` or `evidence_missing`. A bundle that is not `pass` must never contribute energy to a paper number.

**Stream S1** puts that gate in front of every bundle **reader**. `joulewise/bundle_read.py` provides:
- `BundleReader`, whose energy accessors (`trace_rows()`, `summary()`, …) refuse unless the reader's gate has passed;
- `authenticate_window_members`, the window-level gate;
- three **tolerant** accessors (`raw_summary`, `raw_metadata`, `raw_artifact_bytes`), which return bytes without gating. Some legitimate callers need them: the gate itself, historical tools, and non-claim diagnostics.

**The sweep** is a **test** (`amendment 51` and following) that statically parses every tracked Python file and lists each *read site*: a call of a tolerant accessor, or a raw energy-file path read. Every site must be either behind a gate the sweep can see, or in a closed allowlist with a class whose condition is true (`gate_body`, `tolerant_definition`, `historical`, `non_claim` (i)/(ii), …). The sweep is the mechanism that is meant to keep **future** code from adding an ungated energy read.

**The history of the same signature:**
1. The cold ruling BFGS-S1-SWEEPCLASS-01 wrote amendments 57–59: the classes, the gate-rebinding rules and the cache-slot guard.
2. The paired Opus refuter found RSW-1..RSW-9: 0 BLOCKER, 5 SHOULD-FIX, 4 NIT. Each is a Python form that evades the static rules: a bound-method alias or `getattr`-by-string; `_cache.update(...)`; rebinding a gate name by module-level assignment or local `def`; misclassified rows; raw-path reads not watched.
3. The erratum cold ruling upheld all nine and wrote amendments 57–60 restated.
4. Its paired Opus refuter found B-1..B-9: again 0 BLOCKER, 5 SHOULD-FIX, 4 NIT. Again each is an evasion form:
   - B-1: calls inside a `lambda`, a `def` nested under `if`/`try`/`with`/`for`, or module-level code are never visited;
   - B-2: the gate's *behaviour* is replaced by patching `battery_float.authenticate_bundle`, by a module attribute written in full, or by a `type()` subclass;
   - B-3: `r._path = other_bundle` after the gate passed;
   - B-4: a class held against its own condition (`envelope_gate.py` rows as `non_claim` (ii), although the envelope verdict licenses AP-5 numbers); the proposed fix is a behaviour-identical **production** change adding `reader.metadata()` before each `raw_summary()`;
   - B-5: caller checks count calls but not references (`map(extract_rows, …)`).

Both refuters state that **at the current tree no energy value reaches a claim artifact without a battery gate**. Every finding is a *latent* door: code someone could write in future that the static test would not flag. The SHOULD-FIX count went 5 → 5; it is not shrinking.

## The questions (answer each; give your reasons and name the evidence you ran or read)

- **Q1. Structure.** Is "a static sweep that recognises every way Python can reach an ungated read" closable at all? Or is each round's fix guaranteed to leave a next form (e.g. `exec`, `importlib`, `__dict__` writes, `functools.partial`, descriptors, `sys.modules` edits)? Is this the same signature, in the rule-11 sense?
- **Q2. Threat model.** Who writes the evasive forms? Consider decision D-161 (Ed, 2026-08-27): refusals aimed at an operator-only adversary are over-engineering, and fail-closed designs are reserved for physics, evidence and pre-registration. Consider also Ed's 2026-09-24 standing goal: gates must prevent bad science, and ceremony that catches nothing is dropped. Which of B-1..B-5 guard against a plausible *accidental* future ungated read (a real science risk), and which guard only against deliberate evasion?
- **Q3. Recommended design.** Choose, or propose better than:
  - **(a) Close B-1..B-5 as the refuter wrote them.** This is round three of the same shape.
  - **(b) Freeze.** Implement only the forms that are plausible *accidents*: the refuter's B-1 scope coverage looks like one (an ordinary nested def or `__main__` block), and B-5 references perhaps. Record the deliberate-evasion forms as a named limitation in 51 (h), and stop.
  - **(c) Move the guarantee to runtime.** Make the protection structural rather than syntactic: for example, tolerant accessors that require an explicit capability or token argument, a `BundleReader` that re-checks its gate on each energy access (e.g. binding the gate result to `_path` and its digest), or a runtime assertion at the claim-artifact writers that every contributing bundle's verdict is `pass`. The static sweep then shrinks to an inventory. Say which runtime check is smallest and where it lives, and whether it touches the frozen files (`battery_float.py` and the FT §E excluded list must stay byte-identical; the eight consumers must not import `battery_float`).
  - (d) Something else.
- **Q4. B-4.** Should the behaviour-identical production change in `envelope_gate.py` be made? When (before S1's allowlist closes, or as its own lane)? Or should the rows be reclassified truthfully?
- **Q5. What S1 fix round 3 implements next**, in order, as a short list, given your Q3 answer. What does *not* block S1's merge?
- **Q6. Stop rule.** What single criterion should end this lane's review rounds? Examples: "no finding that is reachable by an accidental edit", or "no ungated read at the tree plus runtime check X".

## Material (read what you need; absolute paths)

- S1 branch head `315364b2` (`feat/2026-09-26-bfgs-s1-bundles`; includes main `97082508`). Partial fix-round-3 tree `cbfa9dc3` (amendments 49, 50, 52–56 implemented; 51 blocked). Your working tree is a detached checkout of `315364b2`.
- Round 1: `/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-92472459/20-bfgs-s1/90-coldgate-sweep/` holds `00-charge.md` (sha256 prefix c56cb3c8), `21-coldgate-fable-ruling.md` (e8d33575) and `11-opus-contract-refuter.md` (693815ac).
- Round 2: `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/20-coldgate-sweep-erratum/` holds `00-charge.md` (683a014c), `21-coldgate-fable-erratum-ruling.md` (c18a04f6; §6 has amendments 57–60 as they stand, §8 has the fix-round-3 contents) and `11-opus-contract-refuter.md` (3057d03c; Section B has B-1..B-9 with probes).
- Code: `joulewise/bundle_read.py`, `joulewise/battery_float.py`, `joulewise/envelope_gate.py`, the sweep test (grep `tests/` for `OBSERVE_CALLERS` / `gate_body` / `tolerant_definition`).

## Output

A report of at most about 120 lines: Q1–Q6 answered in order, each with a one-line verdict first, then reasons. Tier any defect you find (BLOCKER / SHOULD-FIX / NIT). End with a 3-line recommendation.
