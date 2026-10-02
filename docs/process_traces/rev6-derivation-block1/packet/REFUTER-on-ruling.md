REFUTER: AGREE

# Refuter, Phase 2: on the judge's ruling `COLD SCIENCE GATE: ADMIT`

Ruling read: `/Users/edr/code/JouleWise-coldgate-judge/docs/process_traces/rev6-derivation-block1/packet/RULING-judge.md`
(30039 bytes, first line `COLD SCIENCE GATE: ADMIT`). My Phase 1 file, `REFUTER-independent.md`, was written before
I opened the ruling. Its bottom line was **correct application: YES**, with one upstream finding (F1) that the gate had
to name and rule on rather than pass silently.

## Why AGREE

I compared each of the ruling's executed results with my own, and every one matches:

| Quantity | Value | Ruling | Mine |
|---|---|---|---|
| Members | n = 24, the same 24 ids and lexemes, 0 exclusions, 0 foreign rows | = | = |
| Prior set | 110 rows (77 / 31 / 2) | = | = |
| Sessions | seq 278 and 328 opened after the pin row 276 `476e2ae8…` | = | = |
| min, max, range | as in the candidate | = | = |
| mean, SD | 0.028444120869643095; 0.003803438860221064 | = | = |
| s_within | 0.003888840415839957 at df 22 | = | = |
| t quantiles | 2.06865761041904865151, 2.80733568376999900293 (df 23); 2.07387306790402616585, 2.81875606060014349853 (df 22) | = | = |
| P95, Q99, Q99_within | 0.01112705033143238; 0.015100307220104515; 0.01550217418713139 | = | = |
| S, C | S 0.014531; C 0.01550217418713139, set by Q99_within | = | = |
| C − S, level screen | 0.00097117418713139; 0.036462861644980 | = | = |
| ICC, ρ1 | ICC 0; ρ1 −0.180124… = −29/161 over 22 pairs | = | = |
| Window medians ÷ S | 0.0102451738… | = | = |
| Diagnostics | screen challenge 4 (C1-d03, C1-d09, C2-d04, C2-d08), diagnostic, not a veto; prior max + range 0.04262208300415633, not exceeded | = | = |
| Count replay | NEXT_WINDOW then CLOSE_AND_DERIVE | = | = |

Some of the ruling's claims overlapped nothing in my Phase 1, so I checked them now with executed commands:

- **All 376 receipt digests recompute** as sha256 of each row's canonical JSON without `receipt_digest`: 376/376.
- **Finalized 25G83 dispositions** are 47 valid and 25 ordinary-invalid, as the ruling says.
- **Thermal condition (d)**: both `night/receipt.json` files hold `"cpu_speed_limit": null`, and the `pmset -g therm`
  text is "No thermal warning level has been recorded…". This is the vacuous-pass the ruling describes in §6.2.
- **Load figures**: 1.59 and 0.45, as stated.
- **§9 ratio**: Q99_within / Q99 = 1.026613 < r = 1.026634, as stated.

### The ruling caught both of my Phase 1 findings and disposed of F1 soundly

**F1, the network-time receipt wording.** This is ruling §6 item 1. The ruling found the same facts I did:

- both windows' stdout reads `Network Time is already off.`;
- the sealed text in §5 requires stdout to be exactly `setUsingNetworkTime: Off`;
- the recognizer was widened by `2431dcaa` (21:13 PDT), after the seal `46643f1d` (15:09 PDT) and after the refused
  `c1-20261001T0137Z` attempt;
- the registration was not amended.

The ruling holds that condition (f) is met in substance. It notes:

- the receipt proves the required end state: OFF, exit 0, same boot, about 1245 s before the first capture on both
  clocks;
- under the sealed "stays OFF" policy, the literal wording could only ever appear after an ON→OFF resync, which §5
  merely *allows*;
- the gap must be closed by an erratum or a written ruling **before the successor issues**.

That matches my own physical judgment: the purpose of D-186 is served, and R9 shows zero clock-movement or empty-fit
refusals. It is also the disposition I asked for, named and ruled rather than passed silently. Requiring an erratum
before D-138 is the right place to put the cure.

**F2, the gitignored `.log` files.** This is ruling §6 item 4. The ruling verified the custody originals against
`MANIFEST.sha256`. My own check covered only the cross-match of those digests with the harvest inventories.

## Defects in the ruling, none of which changes the outcome

1. **Transcription slip in §4.1, ICC row.** The ruling prints "MSB 1.36e-5 below MSW 1.51e-5, F = 0.0009". My Decimal
   recomputation gives MSB = **1.36296…e-8** and MSW = 1.51231e-5. The ruling's own F = 0.0009 is consistent only
   with MSB ≈ 1.36e-8 (1.36e-5 / 1.51e-5 would give F ≈ 0.90). ICC = max(0, ·) = 0 either way, and the figure is
   report-only.
2. **The quantile route is not fully independent of the issuer's.** The ruling's route (§4.2) is A&S 26.7.3/26.7.4
   with Machin's π, which is the same mathematics as the issuer's second, closed-form route. Only the code is new. The
   integration check the ruling adds is at float precision, about 12 places. This does not affect the result. My
   route shares no mathematics with either issuer route: a hypergeometric series for I_y(1/2, df/2), exact
   half-integer Γ, π by the Gauss–Legendre AGM. It reproduces all four quantiles to 20 dp, with forward residuals
   ≤ 1e-89.
3. **F1's disposition does not engage §5's "a change to any of them voids this revision".** Read strictly, the
   post-seal recognizer change is a change to the §5 "Network time" item. The ruling's purposive reading resolves the
   literal stdout clause, but it does not say why the voiding sentence does not reach a change in how the receipt is
   recognized. My answer is that it does not. The registered operating condition, network time OFF and settled
   ≥ 600 s on the same boot, is unchanged and is evidenced; only the recognition of an equivalent macOS statement of
   that state changed. The erratum the ruling requires should state this explicitly, so the D-138 gate does not
   inherit an open question.

## Not verified by me

The ruling states that the custody `night.log` and `derivation-chain.log` files show twelve `slot_start`/`slot_end`
pairs and no `slot_unused`, abort or `window_exhausted` line. My brief limited reads to `runs/instrument_validation/`,
so I did not open those files. The claim is consistent with what I did verify:

- the ledger holds 12 claim/finalization pairs per session, all valid;
- the harvest-inventory digests of those logs equal the packet `MANIFEST`.

## Bottom line

The ruling's ADMIT is correct. Its arithmetic and membership findings match my independent re-derivation exactly. It
missed nothing material that I found. Its one substantive judgment, F1, reaches the same conclusion I did and sets
the right precondition: an erratum or written ruling before the successor issues. The three defects above are a
transcription slip, a weaker-than-claimed independence of the quantile route, and an unaddressed voiding sentence.
None of them changes a member, a statistic, an operative or the verdict.
