# Post-seal rebuttal round (charter §5, bounded: one round) — packet A267

Convened by the magistrate (activation d9990b3c) after BOTH outputs were sealed: `10-coldgate-fable-ruling.md` (sha256 bbeff5c42f3592f6f7b8c7dee32f1fd4a7ab898d8a760f67d80c7ee62092d0b0) and `11-opus-contract-refuter.md` (sha256 85f0437db50d60be48b5b213fca5ad08ad18f04cd8cbbcc6828a75e8628970dd). Inputs for this round, all in this directory: the frozen packet and exhibits (unchanged, sha 0e3dfe79…), files 10 and 11, and the lead's post-freeze executed evidence `12-lead-bench-probe-caps-lifted.md` (labeled; the caps lifted to 1.0 s: the fit alone refuses envelopes 01, 03, 04, 07, 10; 08 and 09 bounded at 5.08 / 5.35 ms, fitted rates −7.60 ppm).

Verified by the magistrate at the bench before this round (exhibit C1 exclusion list, verbatim): envelope 09 is excluded `['clock_anchor_unresolved', 'incomplete_interior_support', 'start_drift']` (drift 10.06 s > `start_drift_max_s` 10). The packet's prose named only 03 and 06; the refuter's finding is correct.

The judge rules the following atomic rebuttal questions. For each: SUSTAIN the ruling as issued, or AMEND it with exact replacement text, citing the deciding exhibit or executed probe; tier any new finding. The original ruling remains part of the record as issued; this round produces an addendum, not a rewrite.

## R1 — Absolute drift backstop (refuter BLOCKER 1 against ruling Q2)

The ruling's v3.1 caps are `{max_sustained_rate_ppm: 25, max_placement_bound_s: 0.005}` with the drift term uncapped and priced. The refuter: 25 ppm × 600 s = 15 ms admitted drift ≈ 0.6 J at 40 W, the same order as the ~1 J attribution limit, and the pilot precedes an idle-load-idle bracket (A20 `block_two`). Rule: does v3.1 carry an absolute drift backstop (`max_wall_minus_monotonic_span_s`, e.g. 15 ms = 25 ppm × 600 s, or another value with its derivation), or is the joule pricing in `error_bound_j` plus the consumer's declared use sufficient? If a backstop is ruled, give its value, its derivation, and the refusal detail code.

## R2 — Identity→caps binding (refuter MATERIAL 5 against ruling Q2)

The ruling says the record carries `"caps": V3_1_CAPS` verbatim and the identity is `CLOCK_METHOD_V3_1`. The refuter: a caller-supplied `caps` argument detaches identity from constants unless the identity→caps map is frozen and both caps are emitted. Rule: is the deriver's `caps` argument replaced by a method selector (`method="v3" | "v3.1"`) that resolves caps from a frozen module-level table, with the resolved caps emitted in every record (v3 records too, as a new key, or v3 records byte-identical and only v3.1 emitting)? Give the exact rule.

## R3 — Consult R2 / R3 bars in the regression set (refuter BLOCKER 2 against ruling Q4)

The 2026-08-18 design consult (exhibit B's source file, lines 100–115) carries R2 ("on all 34 currently resolvable corpus members, zero new refusals; point shift ≤ 1 ms; effective bound delta within ±0.25 ms") and R3 (kill tests independently exercising > 5 ms offset span and effective bound > 5 ms, among others). Neither was in exhibit B or the ruling's regression list. Rule: (i) is a corpus replay under the default method (v3) a required regression for the parameterisation change, and if the 34-member corpus is not on disk in this checkout what substitutes (state the substitute and its burden); (ii) do the existing v3 kill tests A16/A17 satisfy R3 unchanged, and must v3.1 add its own R3-shaped kills (> 25 ppm rate; placement > 5 ms)?

## R4 — Authenticated versus asserted OFF (refuter MATERIAL 4 against ruling Q1)

C2 proves the READ form is not in the sudoers slice. The ruling's Q1 rules give an asserted OFF from one set command's exact stdout at chain start. The refuter: consult I4 (B3) requires an *authenticated* admission; exhibit D's own method — `/usr/bin/log show --predicate 'process == "timed"'` over each envelope's span, refusing any envelope containing a `cmd,apply,src,adjtime` or `ntp_adjtime` line — is unprivileged and available. Rule: is a per-envelope post-capture `timed`-log attestation added to Q1 (who runs it — collector at envelope end, or the chain after each envelope; what it records; what it refuses; how `network_time_provenance` distinguishes `asserted` from `authenticated`), or is the set-command receipt sufficient for I4? Note the log is a ring buffer; state the timing constraint if the attestation is ruled.

## R5 — Q3 corrections (refuter MATERIAL 6 and 7)

The refuter: no integer-nanosecond anchor field exists (the endpoint is float64 `first_sample_end_point_epoch_s`); there are TWO 1 µs gates (`integrate` `span_mismatch` and `reduce_interior`'s per-rail check); "vacuous" is wrong because exact equality is a live gap detector. The ruling's Q3 rule already rounds the float endpoint once to integer ns and converts the rail-coverage test to integers. Rule: SUSTAIN with the corrected wording, or AMEND; state the exact wording that replaces "the 1 µs comparison is retained as an assertion that exact arithmetic makes vacuous".

## R6 — What the re-run can yield, and whether start drift is a precondition (refuter BLOCKER 3)

On this night's primary evidence, the full ruled disposition (Q1–Q3) would have retained {02, 05, 08, 11, 12} = 5 envelopes and 1 disjoint pair after the protocol's own `start_drift` exclusion removes 03, 06 and 09 (drifts 10.23, 10.18, 10.06 s; eleven of twelve envelopes drifted 7.75–10.23 s against a 10 s limit). Lane ENVELOPE-START-DRIFT-01 (A269, registered p3) owns the cause. Rule: does the corrected acceptance for this lane state that the pilot re-run is not prepared until the start-drift cause is named and cured or the interior offset budget is explicitly re-sized (a precondition), or is start drift left to its own lane with the re-run's "≥ 8 bounded envelopes or names a new cause" acceptance unchanged? This is lane ordering and acceptance text, not a process rule.

## Constraints

Same as the packet: read-only; foreground; no subagents; no `systemsetup`/`sudo`; probes as before; the single unit module at most once; wall budget 20 minutes; write the addendum to `14-coldgate-fable-rebuttal-ruling.md` in this directory (under 10 KB); ending before that file exists is a protocol failure.
