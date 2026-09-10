# 45 — Magistrate synthesis over the three blind design seats (Astra 41, cold Fable 42, Opus 43b): new-epoch calibration bootstrap

Written 2026-09-10 ~08:25 PDT by the resident magistrate (activation 96bfeca7) AFTER reading all three memos. This is a synthesis and a
proposal for the cold gate (packet 46); the magistrate rules nothing here. Ed owns the scientific rules (D3, D-125) and may veto any default.

## Where the three seats agree (adopt unless the cold gate objects)

1. **D1 mechanism:** a `--derivation-only` mode of the existing writer `scripts/validate_powermetrics_fiducial.py`, run under the existing
   `DIAGNOSTIC_NO_PACK` class by a new pinned chain; no new night class; C1/C3–C5 untouched. The mode still authenticates the active artifact's
   bytes/protocol/estimator hashes (`_derive_preflight_systematic_screen_s(identity_epoch=None)` already exists for that), REFUSES if the live
   epoch equals the active artifact's (so it can never substitute for a same-epoch check), refuses in bracket mode, records the measured epoch
   and the full T1 vector (incl. the powermetrics sha256) in the hashed evidence, and licenses nothing: no 25G83 acceptance exists until D4.
2. **D2 ledger:** ONE canonical ledger carrying both epochs; per-row epoch already exists; a separate anchored ledger is rejected (second head pin,
   consumer routing, rollback surface). Issuance validation is what must change, keyed per generation so r3–r6 keep validating byte-identically:
   a registered multi-entry epoch catalog; a corpus-purity check (every member's row carries the target epoch); the cutoff-prefix rule accepting
   finalized live rows for the registered generation.
3. **D4 issuer + transaction:** the predecessor-reissue tool cannot do this (copies the predecessor's members, STOPs on change); build a tracked,
   parameterized prospective-corpus issuer (Astra/cold Fable) rather than another bespoke `build_r7.py` (Opus precedent), so D5 becomes one
   command; Decimal semantics per D-102 cl.4; both df 18/19 quantiles; generation rows in `calibration_bracketing.py` and
   `tests/verify_calibration_acceptance_corpus.py` (`stored_lexeme_is_member_value: True` for a fresh capture). The D-138 atomic transaction carries
   the successor bytes, default flip, registry, generation arithmetic, the ~29 files pinning the r6 id (Opus grep), regenerated packs/T1/chains,
   the fan-out surfaces from consult 38 Q5, and the staged R2 patch + four regressions. Historical generations byte-identical.
4. **D5:** a standing `EPOCH-ROLLOVER-<build>` lane template; a DAILY desk epoch watch (sysctl kern.osversion, hw.model, sha256 of
   /usr/bin/powermetrics, MLX version vs the active artifact's epoch and the last ledger row's T1) at magistrate wake / step-0 — the update landed
   09-02 and was found 09-10 at bind-window: eight days; a pin-inventory generator so the transaction scope is computed; ask Ed to defer macOS updates.

## Decisive catches (adopt; each seat's own best finding)

- **Opus R1 (fatal if ignored):** the successor's `ledger_cutoff` must ADVANCE past the bootstrap rows and its prior set must include them.
  With cutoff 76, every bootstrap row is a post-cutoff "new observation"; one `systematic-invalid` bootstrap capture would fire
  `new_systematic_failure_challenges_preflight_screen` and hard-stale the successor at issuance (`calibration_bracketing.py:1876–1882, 1837–1850`).
- **Opus (membership):** the corpus must be every `valid` observation of the registration; excluding a valid same-epoch row outside the retained
  min/max fires `new_valid_same_identity_capture_expands_observed_range` (`:1811–1826`). Outcome-based selection is mechanically self-defeating.
- **Astra (extension admission):** `append_pending_receipt` requires the physical head to equal the committed pin (`calibration_ledger.py:5495`);
  after the first standalone observation of a night that equality no longer holds, so a night of N standalone captures needs a registered-extension
  rule (baseline is an exact ancestor; every intervening attempt belongs to this registration, in order, finalized; next slot unused and within the
  registered bound; no foreign extension) under the writer lease/append lock; the night never commits Git; terminal pin candidates emitted. THE COLD
  GATE MUST VERIFY THIS AGAINST CODE (does the existing bracket-session path already handle two observations per night, and how?).
- **Opus R2 (permanent):** bootstrap rows are ordinary live `valid` rows and enter the anti-withholding equality check forever; an unreadable
  bootstrap custody directory refuses every future window → pinned custody manifest + backup before the transaction; a regression pinning the refusal.
- **Opus gap:** the identity epoch does not include the powermetrics binary hash (only the T1 vector does); a Rapid Security Response could swap the
  binary without moving kern.osversion → the desk watch must cover the binary explicitly; not a contract change now.

## Divergences for the cold gate to rule

| # | Question | Astra 41 | Cold Fable 42 | Opus 43b | Magistrate proposal |
|---|---|---|---|---|---|
| V1 | Evidence status of a derivation observation | distinct schema `status="non-claim-bearing"`, `screen_evaluation=not_applicable`; a derivation observation kind in the ledger; candidate discovery skips the kind | ordinary `valid`, manifest `capture_role=derivation_only_nonclaim`, `preflight_level_screen: null` | ordinary `valid`, `derivation_only: true` + `screen_basis` (prior r6) in the hashed evidence; rows enter the prior set as members | Opus: the rows MUST be ordinary `valid` corpus members (D2/R1) and nothing can consume them until a 25G83 artifact exists; mark provenance in the hashed bytes; add ONE structural barrier: `_candidate_from_observation`/attachment refuse a row whose evidence carries `derivation_only: true` unless the consuming artifact's epoch equals the row's (already implied by the epoch check) — verify redundancy, do not add a parallel schema |
| V2 | Classification during bootstrap | no screen; large valid bounds retained; novel failures → science gate | judged under r6 for information; rule 6 systematic-shift check gates issuance | judged under r6 (D-102 cl.2 judge-under-prior), `systematic-invalid` excluded from the corpus; ≥2 such → not issued, Ed rules | Opus/cold: judge under the prior artifact (that is the doctrine); the screen-challenge threshold is Ed's (default: ≥2 systematic-invalid halts issuance) |
| V3 | Corpus size / nights | 20 attempts, ≥19 retained, 2×10 (n≥19 from D-126) | 2×14 attempts, retained ≥17; rule 3 fallback | target 20 valid, 2×10, min 12; one-night n=20 fits at 6 min/obs | Ed's. Default to propose: TWO nights, 12 attempts each (≈97 min/night at 8 min), retained ≥17 (r6's n) with n≥19 preferred; membership = every valid; no top-ups; Opus's one-night 20 as the fallback if Ed prefers calendar |
| V4 | Inter-observation spacing | 600 s slot interval | 60 s idle | back to back | Magistrate's: 60 s idle after the single 600 s settle (thermal state re-checked by the writer per capture) — cheapest; the cold gate may prefer Astra's 600 s slots for cooling parity with the r6 corpus (multi-day, sparse); rule it |
| V5 | Issuer | new `bootstrap_calibration_epoch.py` (check/capture/prepare_candidate) | new `issue_calibration_acceptance_generation.py` | bespoke build script per precedent | one tracked parameterized issuer (D5); name per the cold gate |
| V6 | Ledger validator relaxation shape | generation-indexed prospective prefix, `import_plus_live` | same | drop the import-marked clause; replace literals 38 / 2N with generation-registered counts; add purity check | Opus's concrete edits inside the generation-keyed frame |
| V7 | D-125 floor for the successor's allowance | inherit lineage envelope `S=max(inherited S,Q95)` etc. | Ed decides; max(range, floor) or retire | `A_floor = max(new corpus range, 0.010818)` | Ed's; default `max(new range, 0.010818)` (never weakens the bound); the successor derivation must NOT settle it implicitly |

## Pre-registration text — proposed default for Ed (commit before the first capture; Ed may veto or amend by reply/directive)

Base: Opus's text (epoch incl. the binary hash; two agent-free windows on distinct days; 600 s settle then observations with 60 s idle; classification
under r6 recorded in the evidence; membership = every `valid` observation; mechanism-named outcome-independent exclusions only (clock-anchor
feasibility, protocol gates, recorded interruption) with rows retained; stopping: 12 attempts per night, until 20 valid or the window's usable time;
fewer than 17 valid after two nights → not issued, a third window scheduled with the shortfall recorded first; screen challenge: ≥2 `systematic-invalid`
under r6 → not issued, Ed rules; no G2-a/floor/claim output is an input). Plus cold Fable's rule 5 (no member value examined before the corpus closes)
and rule 6's alternative threshold (max exceeds r6 max by more than r6 range) as a second, recorded diagnostic.

## Calendar (conditional on the cold-gate ruling today and the rehearsal harvest tomorrow)

Implementation D1/D2/V6 + issuer + tests through the gauntlet: ~1 desk day (Opus) to 14–28 h (Astra) → start today with fan-out seats; corpus
nights 09-12 and 09-13 (or 09-12 day+night if Ed allows a daytime quiet window); derive + cold science gate 09-13; D-138 transaction 09-13/14;
bind/arm 09-14; first G2-a 09-15 (two-night) / 09-14 (one-night). The 09-11 activation harvests the rehearsal and, if the ruling and the implementation
have landed, prepares the corpus-night plan under the new runbook; otherwise desk work.

## What the cold gate is asked to rule (packet 46)

R-a the D1/D2/D4/D5 mechanism as synthesized (with the decisive catches) — a proposed contract/process mechanism, so a cold-gate ruling is required;
R-b the divergences V1–V6 (V3 and V7 are Ed's: rule the DEFAULTS to propose and the veto window);
R-c the pre-registration text to propose to Ed;
R-d the implementation decomposition (disjoint-footprint seats) and gate shape;
R-e whether the D-102 dated addendum and the calibration_ledger.md contract section are within the cold gate's authority to adopt (rule 11: the cold
    gate adjudicates packets; Ed may veto) or must wait for Ed.
