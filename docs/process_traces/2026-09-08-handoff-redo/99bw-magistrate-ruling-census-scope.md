# Magistrate ruling — ICLOUD-CUSTODY-LOCATOR-01: the mode census is a bounded governance aid, not the invariant (2026-09-08 ~11:40 PDT)

Trigger: the Astra delta on part 6 (99bv) found two further AST-census escape shapes (renamed forwarding parameter;
omitted replay default) after part 5's hatch (Opus 99bi) and part 6's cure — the third finding on the "census escape
shape" signature. Rule 11's standing trigger says the next spend is not round three of the same shape.

Disposition (magistrate, with written rationale rather than a further cold gate, because the property the census
guards is ALREADY held by construction and both refuters say so):
1. The invariant of record is the cold-gate ruling 99ak/13: issuing DEFAULT at `load_calibration_ledger_snapshot`
   and `_custody_reasons`, caller-supplied mode on every shared validator, entry guards on the four issuing entries,
   the planted-replacement fixture. A forgotten site can only LOSE the override, never gain replacement bytes. Opus
   99bu §4 and Astra 99bv §Residual confirm the chain and guards hold.
2. The AST census (tests/test_custody_mode_inventory.py + the 14-row allowlist) is a GOVERNANCE AID: it forces a
   reviewed edit for the shapes it detects (literal, alias, local, IfExp, dict, kwargs, second call, positional).
   Its documented limits now include, by name: forwarding through a parameter not named `mode`; omitted replay
   defaults on wrappers; callable-container dispatch; runtime-built dicts. No further census round will be run for a
   new shape; a new shape is recorded in the addendum's limits list. The census key moves to ordinal-within-function
   (Opus 99bu §2) so line shifts do not train reviewers past the reason text.
3. Opus 99bu §3 is a REAL production-path fix and lands as part 7: `_idle_admission_core_evaluation`
   (scripts/run_campaign.py ~:5257) takes a forwarded `mode` defaulting to issuing; only the completed-window replay
   path passes read_replay; the live AXI campaign path evaluates the bracket under issuing; the allowlist row's reason
   names claim-readiness emission; regression: live-capture path under a planted replacement observes absent.
4. After part 7: Astra execution delta on the part-7 diff only; magistrate terminal review; PR; replay; merge.
