# Consult brief: BETA attempts 4 and 5 were both removed by a stale calibration acceptance (block 5, second seal)

You are one of two blind seats. You do not see the other seat's answer. You are licensed to disagree with
anything in this brief, including its framing. Read-only: change nothing on the machine or in any repository;
write nothing outside the one report file your launcher names. Do not start `claude`, `codex` or any network
request. Do not run `sudo`.

## Facts the lead verified (2026-10-11 07:40 PDT)

- Measurement clone (the code that ran): `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18`.
  Harvest program (desk root, pinned): `/Users/edr/night-custody/desk/b5-harvest` at `0699abbb0881ce64b39c46ba07de568cc3848260`.
  Registration: `configs/campaigns/v5_claim_25g83/registration_block5.md` in the clone. Calibration
  pre-registration: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. Magistrate brief:
  `docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md` (in `/Users/edr/code/JouleWise-wt-b5-records`).
- BETA attempt 4 (`v5-b5-beta-a4-20261010T2237Z`, harvest archive `/Users/edr/night-archive/harvest-v5-b5-beta-a4-20261010T2237Z-r2`)
  and BETA attempt 5 (`v5-b5-beta-a5-20261011T0739Z`, archive `/Users/edr/night-archive/harvest-v5-b5-beta-a5-20261011T0739Z`)
  each ran a whole chain (driver verdict GO, chain exit 0, 125 of 125 bundles; 120 and 119 members succeeded)
  and each harvest says `verdict` COLLECTED, `claim_usable` false, one window reason:
  `calibration.bracket_acceptance_failed`.
- Attempt 4 ran while the Mac slept about 14 % of the window, and the consult of 2026-10-10 took the sleep as
  the cause. Attempt 5 did not sleep (a keep-awake job was loaded; `CLOCK_MONOTONIC_RAW` minus Python monotonic
  changed by 708 ns across the window), and it has the same reason.
- The harvest's bracket evaluation (`withheld/bracket-evaluation.json`; the lead printed status words and
  reason codes only, numbers masked) says the same thing for both: assessment `status` `failed`; `reasons`
  `["calibration_acceptance_bound_stale"]`; `acceptance.freshness.status` `stale`, `reason`
  `prospective_rederivation_required`, `stale_fields` empty, `stale_triggers`
  `["new_systematic_failure_challenges_preflight_screen"]`; `acceptance.drift` null (the drift comparison was
  never reached). The acceptance artifact is `d079_calibration_acceptance_v2_n24_25g83_r2`
  (artifact sha256 `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`). The listed mandatory
  triggers are `corpus_doubles_from_24_to_48`, `identity_field_change`,
  `new_systematic_failure_challenges_preflight_screen`, `new_valid_same_identity_capture_expands_observed_range`,
  `protocol_or_estimator_byte_change`. For ALPHA attempt 1 (second seal, claim-usable) and BETA attempt 1 the
  same file reads `fresh` and `passed_screen` with no reasons.
- The calibration ledger (`runs/calibration_observation_ledger.jsonl` in the clone, 478 rows): the only
  block-5 capture whose disposition is not `valid` is sequence 456, the `pre` slot of BETA attempt 3's
  session (`v5-b5-beta-a3-20261010T2151Z-calibration`), disposition `systematic-invalid` (a capture that was
  valid as a capture and whose alignment bound was above the pre-flight screen; that chain stopped itself
  five minutes in). Every capture of attempts 4 and 5 (sequences 464, 468, 474, 478) is `valid`, with bounds
  between 27.5 and 31.9 ms; the pre-flight screen is 36.46 ms. Attempt 2's session was aborted (its chain was
  stopped by an agent session); it has one `valid` pre capture.
- So the lead's reading, which you should test and may reject: BETA attempt 3's one systematic-invalid capture
  is a registered trigger that makes the calibration acceptance stale for every later harvest, whatever the
  later window does; attempts 4 and 5 were lost to it and not to anything in their own span; and any further
  window of any pack (BETA or GAMMA) armed unchanged will be removed the same way.
- An earlier audit seat's finding on the screen itself (not verified by the lead):
  `/Users/edr/night-archive/b5-consults/ed-1010-asks/thresholds-audit.md`: 36.46 ms is the largest of the 24
  captures the acceptance was derived from, so it rejects about 1 in 25 ordinary captures by construction.
- Standing doctrine from the owner that binds the decision: a rule is a past judgment about the physics, not a
  constraint; when evidence shows a better rule, write it through the normal gate (a two-seat consult on a
  science question; a prospective cold erratum for a registered rule; a new seal for code or files a window
  reads). Re-arming must never select on a science outcome: decisions may use verdict words, reason codes,
  counts and status words, never an energy.

## Questions (answer each; give file:line for every code or registration claim)

1. **Is the lead's reading right?** From the code and the ledger: which program decides `stale`, from which
   rows, and is BETA attempt 3's sequence 456 the trigger? Is there any other trigger present? Does anything in
   attempts 4 or 5 themselves contribute? Would a GAMMA window, or an ALPHA re-harvest, read stale today?
2. **What the registered rule requires next.** What do the pre-registration and the block-5 registration say a
   "prospective re-derivation" is: which captures enter it, how many new captures are needed (and of what
   kind, in how many sessions, how long each takes on this Mac), which program derives and issues the new
   acceptance artifact, which files change, and where each changed file lives (in the measurement clone, read
   by a window; or only read by the harvest)? State plainly whether the cure needs (a) nothing but desk work,
   (b) a prospective cold erratum, (c) a new seal and a new measurement clone, and why. Give the shortest
   lawful route from here to an armable BETA attempt 6, step by step, with an estimate of wall-clock hours and
   of measurement hours on the Mac.
3. **Is the trigger rule itself proportionate?** One above-screen capture in 14 block-5 bracket captures, with
   a screen set at the sample maximum of 24: is "any new systematic failure voids the acceptance for every
   later window until re-derivation" the right physics, or does it remove windows whose own two bracket
   captures are valid and inside the screen for no measurement reason? If you would change it, say to what,
   and by which gate. Keep separate what must be done now from what you would improve.
4. **Status of attempts 4 and 5.** They are not claim-usable under the sealed rule. Can a lawful later
   re-harvest under a re-derived acceptance change that (brief section 6 rule 4 speaks of a re-harvest that
   changes `claim_usable`), or does "prospective" exclude windows already run? For attempt 4 the sleep is a
   separate objection whatever the answer. Attempt 5 lost six members of one stage (14 of 20 succeeded,
   minimum 16 by the driver's count) and has no known physical objection.
5. **What else the next arm should carry.** Anything that would make the same trigger recur at once (for
   example: an above-screen pre capture stops the chain and makes the next acceptance stale again, about 1 in
   25 captures): name the cure and its gate.
6. **Could this have been seen earlier**, by a desk check before an arm that reads the acceptance freshness
   against the live ledger? Name the function to call. (The lead will add it to the arming steps.)

End your report with one line:
`RECOMMENDATION: <cause> ; <cure before the next arm> ; <gate each step needs> ; <status of attempts 4 and 5>`.

## Blinding (binding; from the magistrate brief, section 6, verbatim)

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

In addition, for this consult you may run a program over restricted files only if it prints structure only
(identifiers, counts, status words, reason codes and times of day), never an energy, a power or a token count.
The calibration ledger's alignment bounds (seconds) are calibration values, not claim energies, and may be read.
