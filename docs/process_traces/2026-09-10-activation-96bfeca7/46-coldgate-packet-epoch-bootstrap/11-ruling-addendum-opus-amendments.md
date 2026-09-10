# 11 — Dated addendum to cold-gate ruling 10 (packet 46): Opus pairing amendments A-1…A-8, recorded 2026-09-10 ~08:45 PDT

Opus contract-lens refuter (rule 11 pairing; full report `12-opus-pairing-refuter-on-ruling-46.md`): **UPHOLD WITH AMENDMENTS**. The
resident magistrate records the eight amendments verbatim as this dated addendum and applies them to the seat briefs; the ruling's
disposition (mechanism ADOPTED; Ed's scientific defaults proposed) is unchanged and nothing is overruled. Three amendments cure blockers:

A-1 (B1, the recovery finalization path). The derivation-only classification rule binds every finalization path, not just the live writer's.
`resume_finalize_bracket_session` (`joulewise/calibration_ledger.py:5227–5387`) takes `systematic_screen_s: Decimal | None`; for a
`derivation`-kind session the caller passes `None`, the disposition collapses to `valid` or `ordinary-invalid`, and the `slot == "pre"` auto-abort
(`:5362–5371`) does not apply — a derivation session closes only on its last declared slot or an explicit abort. `scripts/recover_calibration_ledger.py`
joins seat S2: `--slot` becomes a free string validated against the session's declared slot list (`:172`, `:191`, `:204`), and `:437–453` must never pass
the active artifact's level screen into a derivation session. A mutation-kill regression names `recover_calibration_ledger.resume-finalize` as the
production call site.

A-2 (B2/S1, the corpus-size floor). D-126 cl.2 ratified the Q13 floor as `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19`, a corpus-SIZE floor guarding the
df=1 / t≈63.66 tail (`docs/process_traces/2026-08-07-u2-coldgate/PACKET-V2.md` §Q13; `SYNTHESIS-V2.md:58`), not the `0.010818` screen floor. The
constant is no longer in code, and the n=17 r-series was issued under D-145's anchor-v3 arc as a LOSS from a 19-member corpus, never as a corpus
pre-registered at 17. The default is therefore retained n ≥ 19 required. Expected retention is 24 × (30/38) × (17/19) = 16.95, so two nights of 12
slots do not reach it: the default is THREE agent-free nights of 12 declared slots (expected 25.4 retained), stopping at the third night regardless
of interim values. Ed may instead rule in writing that n = 17 is acceptable; nothing issues below 19 without that written ruling.

A-3 (B3, V7's default). V7's default is the full D-125 envelope, not its S half: `S = max(quantized new range, 0.010818)` AND
`C = max(inherited ceiling, new Q99)`. With C unfloored, D-125's ratified `successor_screen_exceeds_budget_ceiling` refusal fires whenever
Q99 ≤ 0.010818 — r6's own ceiling `0.010164834757777545` is below the floor, so r6 derived under the S-only rule would have refused, and
`screen + excess == maximum` (`calibration_bracketing.py:686`) would demand a negative excess. Seat S4 implements that refusal (absent from code
today) and the generation row carries the inherited ceiling.

A-4 (S4). Replace `0.042622083004156326` with `0.04262208300415633` (the Decimal sum of `0.03289849371536248 + 0.00972358928879385`) in both
occurrences, including the pre-registration text.

A-5 (S2, V1's reason). `evaluate_calibration_bracket` already refuses any session row as an unbound endpoint (`:1874–1882`); the barrier exists to
(a) keep the derivation rows out of the anti-withholding equality every caller must satisfy exactly (`:1597–1625`) and (b) prevent the blanket
`calibration_bracket_binding_missing` refusal a derivation row within `MAX_AGE_S` of an ordinary window would force. The mutation-kill regression must
use a counterfactual the existing session rule cannot kill: a derivation row present in the `registered_valid` universe with the skip removed at one
site only.

A-6 (S3/S5/N1, footprints). Amend A7: four sites consult `is_governed_open_bracket_extension`; `whole_window.py:664–668` fails on ANY snapshot
refusal reason, so claim consumers refuse for the duration of a derivation night by design. Add to S2's footprint `abort_bracket_session`
(`:4501–4547`), `resume_finalize_bracket_session` (`:5227–5387`), `joulewise/receipt_oracle.py:88–118`, `joulewise/arm_readiness.py:8147`,
`scripts/recover_calibration_ledger.py`, and the tests `test_calibration_ledger_custody.py`, `test_calibration_live_three_window.py`,
`test_mint_floor_artifact_generalized.py`, `test_powermetrics_fiducial.py`, `test_receipt_oracle.py`. S1 and S2 both touch
`test_powermetrics_fiducial.py`: S2 lands first, S1 rebases. The slot-set generalization is one mechanical sweep of every `BRACKET_SESSION_SLOTS`
use, enumerated by grep (~20 sites), not the four named sites.

A-7 (S6, completeness). `derivation_notes.excluded_members` is the successor's key; r6's `excluded_predecessor_members` is the predecessor-shaped
analogue. Entries carry `member_id`, `manifest_sha256`, `instrument_evidence_sha256` and no content id, so the prior-set match is by content id
derived from those two hashes. The completeness check ranges over prior-set rows that are valid, carry the target epoch, AND belong to a session of
this registration; a valid same-epoch row outside the registration refuses issuance rather than being absorbed.

A-8 (S7, authority). The desk epoch watch is PROPOSED for the magistrate's step-0, not adopted here: step-0 is a relaunch-contract cadence and its
amendment is Ed's. The MECHANISM half of the D-102 dated addendum commits with the same "adopted by cold gate, Ed veto window open" label as the
scientific half. V3 requires an affirmative Ed acknowledgment rather than silence, because A-2 makes the retained-n default a departure from a
ratified floor.

Nits carried (N1–N3): the ~16 further slot-set sites (A-6 sweep); the reserve CLI's per-slot flags become a list; an estimator-code rotation
mid-campaign also voids derivation captures (add beside the MLX/powermetrics clause in the pre-registration).

Consequences applied by the magistrate: seat S2's WRITE_SCOPE widened per A-1/A-6; S3's completeness check per A-7; S6's pre-registration per A-2/A-3/A-4
and the affirmative-acknowledgment label per A-8; S5 drops the MAGISTRATE_WATCHDOG.md sentence (the `check` tool lands; wiring into step-0 is proposed to
Ed). Calendar: three corpus nights (earliest 09-12, 09-13, 09-14; daytime quiet windows may compress if Ed allows) → derivation + cold science gate
09-14/15 → transaction → first G2-a ≈ 09-16.
