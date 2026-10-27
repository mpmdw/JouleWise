# Tier D: BYTES as a registered design with its instrument-check evidence

<!-- Use when the primary-block release lands but the BYTES analysis cannot finish (stage 1 not committed by about
15 November). Decided by completion, not by any result. Replaces ../paper1.md abstract Part 2 sentence, §6.5,
§6.6 and the conclusion's BYTES branch. §6.1 to §6.4 (question, design, analysis, extension) stay as written: they
are the registered design. -->

## Abstract, Part 2 sentence (replaces)

In a second part, BYTES, we register a test of whether decode energy per token on the same laptop follows the
bytes a model reads per token, its resident size or its decode time, using mixture-of-experts models to separate
bytes read from bytes held; we report its design, its collection and the checks of its instruments, and its
results will follow.

## §6.5 (replaces the section)

### 6.5 Status of the test

**[BRANCH D.1 — the fit set was collected; the analysis did not finish]** BYTES collection closed at its registered
end with {{FILL: P1-BYD-STRUCT | per sub-pack and pass: sessions attempted and counting, cause families, kept units per model; structure only}}.
The energies remain blinded: the hidden pack and configuration factors have not been divided out, and the
held-out models' rows remain in the withheld store. Stage 1, the commitment of the rival lines, had
{{FILL: P1-BYD-STAGE | "not been run" or "been committed (predictions SHA-256 and commit)"}} at submission. Because the predictions are committed
before held-out rows are unblinded, and the design, the family sizes and every output sentence are fixed, the
result can be released later without any choice made in the light of this paper's Part 1 results.
**[END BRANCH D.1]**

**[BRANCH D.2 — the fit set itself could not be collected]** The three fit-set models could not all be collected
before the registered end ({{FILL: P1-BYD-FITSET | which fit-set models lack a counting session, and why}}), so the rival lines cannot be drawn and the
registered test of H1 is impossible. As the contingency registered for this case, Part 2 reports decode energy per
token across the models that were collected, as a measured table without the law test:
{{FILL: P1-BYD-TABLE | per collected model and boundary: e with interval, τ, P̄ and BW, by the registered cell estimator, released under the registered stage rules for the models concerned}}. These values are L1 instrument results; no
hypothesis word, active-or-resident answer or H2 fit is printed. **[END BRANCH D.2]**

**Instrument-check evidence (not used for claims).** Before collection the laptop's BYTES-specific instruments were
checked in non-claim sessions: a resolvability check for the 8-bit model, the meter's clock fit and sample
continuity, the battery-term timing, the clock-rate hold, the disk budget and a drift-transfer test for the three
longest regimes. {{FILL: P1-BYD-CHECKS | per check: what was measured, its registered use, and its outcome word (for the drift-transfer test, "pass not established" for all three regimes and the registered scale retained); no energy from these checks is used for any claim}} These checks set gates and sensitivity lines only.

**Synthetic validation.** The analysis and its independent twin agreed on every printed field in nineteen synthetic
agreement campaigns, and the HC3 intervals' plain 95% coverage in 400 synthetic campaigns per simulated world was
at least 0.9475, above the registered floor of 0.93.

**When results follow.** {{FILL: P1-BYD-WHEN | the planned dates of the stage-1 commitment and stage-2 release, conditional on completion, never on results}}

## §6.6 (replaces)

The known-bytes stream test, which decides how the rails-versus-rest split of memory energy is read, was
{{FILL: P1-BY-KB-STATE | "run, outcome recorded and reported with the results" or "not yet run"}}.

## §9, conclusion (replaces the BYTES branch)

For BYTES we report a registered design whose rival predictions will be committed before its held-out models are
unblinded, so that its answer, whichever it is, will say what drives decode energy per token on this laptop.
