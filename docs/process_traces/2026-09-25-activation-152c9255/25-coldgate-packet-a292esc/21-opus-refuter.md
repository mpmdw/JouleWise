The generated-witness cure (P1) works: 15 generated witnesses kill M033, M045 and M050, and the oracle agrees with every baseline code. The 1e12 J bound (P2) does not close the crashes it claims to close. **Verdict: P1 AFFIRM with amendments. P2 AFFIRM the bound value, but its text as written is REJECTED (one BLOCKER, several MATERIAL).**

# Refuter report: A292-ESC-01, magistrate proposal `ex-10`

The attack ran on a /tmp clone at `660b32d7` (`/tmp/refuter-a292esc`). The probe scripts are in `/tmp/refuter-a292esc-work/`. Mutants were built by editing the source text in memory. Nothing else was written.

## What I ran

**P1 check.** Each case replaces one record (or the nested `energy_bound_terms_j`) with a container that keeps its key names: list, tuple, frozenset, `dict_keys`, or an `OrderedDict` copy with valid values.

| Target | Baseline | M033 | M045 | M050 |
|---|---|---|---|---|
| window, all 5 containers | `window_keys` | TypeError ×4, **accepts (OK)** on OrderedDict | `window_keys` | `window_keys` |
| anchor terms, all 5 | `window_domain` | `window_domain` | TypeError ×4, **accepts** on OrderedDict | `window_domain` |
| row, all 5 | `row_keys` | `row_keys` | `row_keys` | TypeError ×4, **accepts** on OrderedDict |

- All three mutants die.
- `check_reduction` agrees with every baseline code.
- The OrderedDict witness is the strongest: the mutant *returns success* where the baseline refuses, so the kill does not depend on the mutant crashing.

**P2 check.** P2 was patched into a copy of the reducer:
- `gross 10**1000` and `anchor 10**5000` now refuse with `window_domain`.
- `10**12` exactly and `1e12` are accepted; `10**12+1` and `nextafter(1e12, inf)` refuse.
- 2^53 > 10^12, so every integer up to the bound converts to float exactly.
- `fsum` of 10^6 windows at 1e12 J gives 1e18 with no overflow.
- **`prompt_tokens = 10**5000` still raises an uncaught ValueError under P2.**

## BLOCKER

**B1 — P2 does not close the JSON crash** (`ex-10:11-15`).
- A score row's `prompt_tokens` is type `I` with no upper limit (reducer `scored_reduce.py:116`). It is summed into `cells` (:269) and copied into `items` (:211), then hashed as canonical JSON. That hits Python's 4300-digit limit.
- Verified: baseline, P2, and P2 with `<` all raise the uncaught ValueError.
- `attempt` and `envelope_index` are safe: they must equal roster values, so an oversized value refuses as `window_unknown`/`window_binding`/`window_envelope` before any serialisation. `generated_tokens` is capped by `cap_tokens_arm`.
- Corrected text for E2's wire conventions (`ex-e2:57`):
  > `I` int with `type(v) is int` and 0 ≤ v ≤ 10**12; `N` finite number, `type(v) in (int, float)`, |v| ≤ 10**12 (the bound is the exact real 10^12; int and float compare exactly). Out-of-bound values take their record's domain code (`window_domain` / `row_domain`). AMENDMENT of E2 v1.1.

## MATERIAL

**M1 — P2 weakens a ruled refusal** (`ex-10:12`).
- "every energy field (`gross_j` …) must satisfy 0 ≤ v ≤ 1e12 J" admits `gross_j = 0`.
- E2 rules `gross_j N > 0` (`ex-e2:78`), and the existing test refuses 0 (`tests/test_scored_reduce.py:269`).
- Corrected: *"`gross_j`: 0 < v ≤ 10**12. `E_clock_anchor_shift_bound_j`, when not null: 0 ≤ v ≤ 10**12."*

**M2 — A generator that only violates rules leaves the new bound's boundary mutant alive** (`ex-10:6`).
- Verified: the `<=`→`<` flip on the bound refuses every violating input exactly as the baseline does.
- Only an *accepted* value exactly at the bound kills it. `gross_j > 0` already has its zero witness, but P1 generates violations only, so installing P2 creates a third survivor round of the same class.
- Add: *"For every comparison predicate, the generator also emits the value exactly on the boundary, which must be accepted (`gross_j` = 10**12 and = 1e12; anchor = 0 and = 10**12; `generated_tokens` = cap), and the first value past it, which must refuse (`10**12+1`, `math.nextafter(1e12, math.inf)`)."*

**M3 — The expected code for a wrong container cannot be derived from E2** (`ex-10:7` vs `ex-e2:90,100`).
- E2's `window_keys` / `row_keys` say "key set != schema", but a list has no key set. The code (`*_keys`) is currently read from the reducer and oracle, which P1 forbids.
- Amend the code table:
  > `window_keys`: record is not exactly `dict` (`type(w) is dict`) or key set != schema. `row_keys`: likewise. `window_domain` includes `energy_bound_terms_j` not exactly `dict`.
- Refusing dict subclasses loses nothing, because `json.load` never produces one.

**M4 — "Exactly one fault" is not well defined when fields depend on each other** (`ex-10:6`).
- `roster_sha256` is checked against the stamp in force at the window's own `envelope_index`, and that check runs before the envelope check (E2 order at `ex-e2:116`; existing test `test_window_binding_uses_declared_index_before_envelope_mismatch`).
- So a one-field change to `envelope_index` yields `window_binding`, not `window_envelope`.
- Add: *"Dependent fields are recomputed to keep other predicates true (`roster_sha256 = in_force(mutated envelope_index)`). If the fault makes an earlier-ordered predicate unsatisfiable, the expected code is that earlier predicate's code."*
- Also name the base fixtures: `_night()` for live keys, and `_terminal_night()` plus `_inputs(optional=True)` for voided and terminal keys. Without them, `window_unstarted` and a null anchor on a non-live key cannot be generated.

**M5 — Mutants can be silently declared "equivalent"** (`ex-10:8`).
- Nothing stops the sweep's author from declaring M033/M045/M050 "equivalent: both reject the input".
- Add: *"Equivalent means the same return value, or the same (`ReductionRefusal`, `.code`), on every input the verifier admits. An uncaught non-`ReductionRefusal` exception is never equivalent to a refusal. Each equivalence proof is checked by the cold gate, not by the sweep's author."*
- M077's proof, which relies on verified rosters, meets this standard.

**M6 — The generator can be silently weakened later.**
- Add: *"The generator reads a frozen predicate table (record type, predicate id, E2 clause, code, violating values, boundary values). A test asserts that the table equals the frozen list (count and ids) and that each row yields at least one case."*
- The sweep's mutant catalogue must be enumerated mechanically from the AST, with its count recorded in the gate ledger (M001–M111 plus the new bound operands).

**M7 — P2 reverses an existing test and part of a prior disposition, but does not say so.**
- `tests/test_scored_reduce.py:285` (`test_positive_zero_and_large_integer_anchor`) asserts that a `10**1000` anchor is **accepted**, and Astra F3 was closed on that basis (`ex-08:160`).
- The round-2 harness text must replace it with: *"`test_anchor_zero_and_bound_accepted_above_bound_refused`: 0 and 10**12 accepted; 10**12+1 and 10**1000 refuse `window_domain`."*
- It must also add *`test_prompt_tokens_bound`* (from B1).
- Otherwise the harness seat has to choose between the old test and the new ruling.

## NIT

- **Ambiguous "anchor"** (`ex-10:14`). "Integer anchors" could be read as the registration's `anchor_j` (`scored_registration.py:28`). Say `energy_bound_terms_j.E_clock_anchor_shift_bound_j`.
- **Wrong rationale** (`ex-10:12`). 1e12 is not "sized to the instrument". It is a guard that keeps the arithmetic exact and the serialiser safe; the ~1 J / ~5 J limits concern resolution, not range, so nothing contradicts them. Reword to: *"refuses only unphysical values: exact in float (≤ 2^53) and overflow-safe for any window count."*
  - It also catches no plausible unit slip. A 10^4 J block reported in mJ is 10^7 and in µJ is 10^10, both under the bound. Unit checks stay the capture producer's job.
- **Lane closure.** The claim that "A292-AGGREGATE-OVERFLOW-01 closes" (`ex-10:15`) holds only once B1's bound on `prompt_tokens` is added.
- **Scope wording** (`ex-10:6`). "Every predicate in E2's domain definition" should read "every per-record predicate of check-order phases 3–4 (keys, domain, and each later per-record check) plus the nested terms object". The survivors sat in *keys*, not domain.

## Physics (P2)

- `gross_j` is the energy measured over one block's capture window; a block on this machine is about 10^2–10^4 J.
- The anchor term is the energy uncertainty from shifting the clock anchor, roughly power × anchor offset; physically a few J or less.
- 10^12 J is 278 MWh, eight or more orders of magnitude above either quantity. **The bound value is right; only its text needs fixing (M1, B1).**
- Nothing in E2, the ruled K11 text it cites, or the registration checks contradicts an upper bound. It is an amendment and should be labelled one.
