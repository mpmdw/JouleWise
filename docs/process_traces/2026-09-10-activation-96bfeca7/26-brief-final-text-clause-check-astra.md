SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Final clause-by-clause check of the two contract paragraphs at `5b85d401` (gpt-6-astra, xhigh, genre review, read-only; third model family after a cold Fable ruling and an Opus pairing refuter)

Read `git show 5b85d401:docs/contracts/measurement_methodology.md` — the admission paragraph (starts "Each admission attempt records its start and end times as clock readings", ~lines 71–100) and the cooldown bullet (starts "- Between live repetitions, cooldown v2 holds", ~lines 300–360). Read the code they describe at the same commit: `joulewise/environment_admission.py` (lines 15–30, 74–132, 140–200), `joulewise/controller.py::cooldown_gate` (lines 2440–2640), `joulewise/schemas.py::CooldownPolicy`, `joulewise/adapters/powermetrics.py:325–340`.

History you must NOT repeat: this text is the fourth revision (rounds 2, 3 by a cold Fable seat, 4 by an Opus refuter's dictated amendments). Each earlier revision was found to contain at least one clause not true of the code or one term used before it was built. The prior findings, all now applied: universal "every policy" scoped to the 30 s window; elapsed interval = positive integer nanoseconds; release mean is overlap-weighted and built before use; "strict reduction" glossed; file-level refusals named; NaN duration credited nothing; rounding term = upper bound, two ULP per reading.

Deliver ONE table with a row per SENTENCE of both paragraphs (number them; quote ≤ 12 words): verdict TRUE-OF-CODE (file:line) / FALSE (the contradicting code, quoted) / UNVERIFIABLE (why); and a second column for the writing standard: every term of art in that sentence built or glossed at or before first use? (name the term if not). Execute the arithmetic sentences with `python3 -c` (ULP 0.238 μs; 0.954 μs; 0.477 μs per reading; 2.86 μs / 3.34 μs; 12/13 ULP edge; 20/21 readings for 10 μs; 40 × 0.75 s → 19 μs; 30 s / 1 ms → ~14 ms; ~210,000 readings for 100 ms) and run `python3 -m unittest tests.test_gate_sensibility_rounding tests.test_docs_freshness` (gate on rc). Then a verdict: APPROVE (zero FALSE, zero unbuilt-term rows) or a list of the exact minimal edits (old sentence → new sentence) that would make it approvable. Nits about style that do not affect truth or first-use go in a separate short list and are not blocking.

Read-only; no edits; no git writes; no checkout (refs are shared; use `git show`). Report claude-codex-report/v1, genre review, header < 8192 bytes.
