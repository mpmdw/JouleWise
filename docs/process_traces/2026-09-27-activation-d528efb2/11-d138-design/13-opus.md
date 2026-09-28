SEAT: Opus 5.5 — D138-25G83-DESIGN-01

Blind seat. Tree `81c229c0`, read-only. Probes and scratch: `/tmp/d138-design-d528efb2/opus/` (`probe1-3.py`, `swap_runner.py`, `mut2.py`). "Executed" means I ran it this session. "Inference" means I did not.

## 0. What I executed

- **The defect reproduces.** I flipped the candidate to issued form in memory, registered its row and resealed. `_valid_acceptance_bound` returns False. The only cause is the completeness loop (`joulewise/calibration_bracketing.py:985-989`). Eleven target-epoch rows marked `valid` sit in sessions n1/n2 of 2026-09-19, outside the registration. All eleven are in the pinned registry (`probe1.py`). With exemption by content id patched in, the artifact validates (`probe2.py`). No other check fails.
- **The transform keeps the input seal.** The issued form has the same `derivation_input_sha256` (`e7363bdd…`) as the candidate. The candidate's bytes are exactly `json.dumps(indent=2, sort_keys=False)+"\n"` of its own parse, so the issued bytes can be written the same way.
- **Swapping the live default in memory breaks tests.** With the default moved to 25G83: `test_calibration_bracketing` 16 of 93 fail, `test_acc_25g83_rev5` 6 of 12 fail (every one on the check at issuer `:1798`), `test_arm_readiness_evidence_author` 0 of 24 fail. The unswapped baselines are all green. Most failures are R7 expectations read through the moving default. They are not science defects.

## 1. Loader repair

**Where the shared code lives:** a new module, `joulewise/observation_dispositions.py`. The loader cannot import from `scripts/`, but the issuer already imports from `joulewise/` (issuer `:95-128`). The module holds:
- the registry path;
- `REGISTRY_SHA256 = "ba1ba3fc…"`, moved from issuer `:516`;
- the per-decision mechanism text, moved from `:512` and `:517`;
- one strict parser (rejects duplicate keys, requires the exact key set, requires 64-hex ids);
- `DISPOSED_CONTENT_IDS = {"D-126-disposition-25G83-v3-2026-09-25": frozenset(<the 11 ids>)}`.

**The pin.** The loader does not read the registry file at load time. It uses the code-pinned set of eleven ids, keyed by decision id. That set is authenticated to the file two ways:
- a test computes the file's sha256, checks it equals `ba1ba3fc…`, and checks that the parsed file equals the table exactly;
- the issuer's `_registered_dispositions` (`:1326`) reads the file, checks the same digest, parses with the shared parser, and requires equality with the table.

Existing tests patch `issuer.DISPOSITION_REGISTRY_SHA256` (`tests/test_acc_25g83_rev5.py:91,215,409`). So the shared reader should take the pin as an argument, and the issuer should keep its module-level alias.

Why no file read at load time:
- Today the loader authenticates only by code pins plus the artifact's pinned bytes. Everything else per generation is already frozen in code (`:343-346`).
- A whole-file digest check at load time would break this generation's authentication the first time a later epoch appends a disposition.
- Reads inside a v2 authentication session are recorded as inputs (`authentication_io.py:404-427`). A new read would change what every mint or evaluation records. (Inference: I did not trace every consumer of those records.)

**The rule**, inside the existing `import_plus_live` block (`:976`). All of it is executed in `probe3.py`:
- (a) `prior_observation_set.disposing_decision_ids` is absent (meaning none) or a sorted, unique list, every entry in the table. The candidate carries `["D-126-disposition-25G83-v3-2026-09-25"]` (issuer `:2293`). This is the binding to the recorded decision ids.
- (b) The declared list must equal the decisions that dispose at least one prior row. This mirrors the issuer at `:2067-2070`.
- (c) Every disposed id must be in the prior set. This mirrors the issuer's `absent_disposed` check (`:2058-2066`). It also closes a crash: without it, the lookup raises `KeyError`.
- (d) No disposed row may belong to a registration session.
- (e) At `:988`, a valid target-epoch row from outside the registration is skipped only if its **content id** is in the disposed set. Every other foreign valid row still refuses.

Disposed rows stay in the prior set, so `prior_observation_count` (86) and the inventory check (`:937-947`) are unchanged.

**Defect-shaped tests.** Each test is listed with the mutant it kills. The mutation results are executed.

| Test | Expect | Mutant it kills |
|---|---|---|
| T1: the real issued bytes load | loads | the unrepaired loader |
| T2: an extra undisposed valid row in n1 | refuses | exempting by session instead of content id |
| T3: a forged decision id | refuses | (subsumed by (b); keep as a test) |
| T4: the declaration deleted | refuses | ignoring the declaration and using the whole table |
| T5: a disposed row dropped, count re-registered | refuses | removing rule (c) |
| T7: the table disposes a member | refuses | removing rule (d) |
| T8: registry file digest, and file equals table | pass | table edited without the file, or the reverse |
| T9: every older generation still loads byte-identically | loads | any collateral change |

## 2. Issued bytes

Start from the gated bytes `dbad7cc7`. Change only the following:
- delete `candidate_not_issued`;
- `artifact_role`: `candidate` → `issued`;
- replace the whole `issuance` block with `{status: issued, claim_eligible: true, reason: <one sentence citing D-138 and the two rulings>}`. The `licence` sentence goes, as issuer `:2256-2260` intends;
- `backfill_candidate`: set `status: issued`, `production_issuance_blocked: false`, `required_verification: "complete: …"`. The inventory {31, 2, 53} is unchanged;
- add `derivation_notes.issuance_record` (§4);
- recompute `derivation_sha256` by the production recipe: canonical sha256 of everything except that key (`_canonical_sha256`, `:654`; issuer `derivation_sha256`, `:2315`);
- write the file as `json.dumps(indent=2, sort_keys=False)+"\n"`, keeping key positions.

**Byte-identical** (checked by a path-level diff script): `acceptance_id`, `decision_ids`, `ledger_cutoff`, `identity_epoch`, `prospective_rederivation` (the four estimator pins character for character, per B1), `derivation_corpus`, `prior_observation_set` (including `disposing_decision_ids`), `decimal_derivation`, every other `derivation_notes` key, and `registered_generation_row`. Keep that last one: the input seal reads it (`:2342`), and a test can then assert that the code row equals `generation_row_for_registry(artifact row)`. **`derivation_input_sha256` is recomputed and must equal `e7363bdd…`.** It is not copied.

**Do not re-run the prepare step to produce the bytes:**
- B3 forbids curing anything by re-preparation (addendum `:137`).
- The gate ruled on `dbad7cc7`.
- A re-run re-reads custody.

A mechanical transform can be proved exactly. A scratch replay (§5) is verification only.

## 3. Pin swap (one commit; the pattern of `ddfb25e9`)

**Must change together:**
1. Add the new file `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`.
2. In `calibration_bracketing.py`:
   - new path, id and sha256 constants;
   - a new `ISSUED_ACCEPTANCE_REGISTRY` entry (`:147`);
   - the `_D102_GENERATION_DERIVATIONS` row as a frozen literal, with tuples (`:377`);
   - `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` (`:198-199`);
   - the §1 repair.
3. Add the new id to the `_issued_d079` allowlist in `joulewise/arm_readiness.py:6209-6218`. Without it, every 25G83 pack is treated as a successor-acceptance pack. That pack type needs the `ACCEPTANCE_SUCCESSOR` evidence row, and `_derive_acceptance_successor` always refuses to produce it (`arm_readiness_evidence.py:979-988`), so every arm would refuse. **Judge's item:** the comment at `:6204-6208` reserves the successor route for corpus-growth successors. A new-epoch bootstrap is not one; that reading is mine.
4. Freeze the Revision 5 predecessor check in `scripts/issue_calibration_acceptance_generation.py:1798` to `ANCHOR_V3_R7_ACCEPTANCE_ID`, and the `--predecessor-acceptance` default at `:2553` to the R7 path. Route `_registered_dispositions` through the shared module.
5. In `scripts/epoch_equivalence_check.py:699`, change the `--acceptance` default to the R7 path. The required id is already the R7 constant (`:152`).
6. `tests/verify_calibration_acceptance_corpus.py`: add the 25G83 expectations (stored lexeme is the member value).
7. Re-point the R7-expecting tests to the explicit R7 constants. No assertion is weakened.

**Moves with the default by design:** the desk watch (`check`, issuer `:389`); `evaluate_calibration_bracket` (`:2015`); the ledger-baseline readers `whole_window.py:508`, `run_campaign.py:4819` and `analysis_engine/inputs.py:1625,3123`. Their baseline becomes 276, which equals the committed head pin (`configs/calibration/calibration_ledger_head.json`). The generate_g2a, validate_powermetrics_fiducial and write_derivation_night_inputs defaults also move.

**Stays on R7:** R7 keeps its registry entry, row and bytes, and still authenticates by explicit path (executed). `scripts/sim_acc_25g83_rev5.py:226` simulated against R7 and should be frozen to it (inference).

**Deliberately not extended:** `scripts/floor_mint_pinsets/schema_v2.json:180-192`. Its allowance constants are per screen family (0.010818 and 0.009724). Admitting screen 0.013701 is a new family, and floor mints are claim products under H1. Add a test that asserts the id is absent until H1 lifts.

## 4. Disclosures and the hold

**Both places.** The issuing record carries the full text. The artifact carries `derivation_notes.issuance_record` with:
- the transaction id;
- the two rulings by path and sha256 (`21`: `f9de51b7…`; `31`: `be13ccba…`);
- D1–D7 as the rulings' own sentences;
- H1 verbatim, plus: "enforced outside these bytes by `ACCEPTANCE_CLAIM_HOLDS`; lifting it changes no byte of this artifact".

That text is covered by `derivation_sha256`, so it cannot be stripped without breaking the file pin. It is not covered by the input seal.

**`claim_eligible` stays true.** It should mean "these numbers may serve as the uncertainty basis of a claim", which the gate ruled. H1 holds windows, not this issuance (addendum `:222`). Writing false into the bytes would do two bad things:
- it would force a loader change that every consumer echoing the bit would have to learn (`:754`, `:2136`);
- under route M it would force a re-issue with no number changed.

**Enforce H1 mechanically now.** The headless loop arms windows. Add `ACCEPTANCE_CLAIM_HOLDS = {<25G83 id>: "H1-25G83-CAP-CADENCE"}` to `calibration_bracketing.py`. Refuse `claim_eligible=true` at the claim chokepoints when the acceptance the window binds is held. There are two chokepoints: `night_gate.py:995-999` and the GO validation at `arm_readiness.py:10111-10132`. Both already restrict claim eligibility to `CAMPAIGN_TRANSACTION` purposes.

Tests:
- a claim-eligible transaction under 25G83 refuses;
- the same with claim-eligible false passes;
- counterfactual: with the hold map empty, the claim-eligible case passes.

The hold is lifted only by a reviewed PR that removes the entry and cites the ruling. Fallback if the judge wants this PR narrower: a separate hold PR that merges before any claim-bearing 25G83 plan is drafted. A procedural hold alone relies on the loop remembering it.

## 5. Verification and gate

**Pre-issue re-hash**, at the issuing head, recorded before the issue and again on merged main:
- both candidate copies (`dbad7cc7`);
- the four estimator files against B1, and against the candidate's estimator pins;
- the protocol sha `9eaf92f8…`;
- the preregistration `81b65f08…`;
- R7 file `9c3a29f6…` and R7 `derivation_sha256` `2c7dab72…`;
- the disposition registry `ba1ba3fc…`;
- the head pin (276, `476e2ae8…`);
- the two battery verdicts at their recorded commits.

Also check that `DETECTION_PROJECTION_CELL_BUDGET` is still 165000. B2 check: none of `bda7ffe0`, `aeea07b6`, `ea10e3c8` or `5135c1d2` is an ancestor of the issuing head, and `git diff origin/main...HEAD` shows nothing on the four files.

**Independent replay** (a seat other than the one that wrote the bytes; the exact-byte parts delegated under D-150b):
- (i) The path-diff equals the §2 list. The input seal recomputes to `e7363bdd…`. The whole-file seal recomputes by the production recipe.
- (ii) The statistics re-derive from the 12 member lexemes in 80-digit arithmetic with an independent t-quantile: S = 0.013701, C = max(0.010164834757777545, Q99, S) = 0.01902064410651988.
- (iii) `verify-members --corpus-root /Users/edr/night-custody` gives 12 PASS, with custody digests unchanged before and after.
- (iv) A scratch replay of `prepare-candidate` from the issuing head is byte-identical to `dbad7cc7`. This proves the disposition refactor preserves behaviour.
- (v) On the real ledger, read-only: the new default evaluates fresh against 25G83 identity, and R7 by explicit path still judges a 25F84 bundle.

**Full suite:** green, with no new skips. Mutation probes for T2, T4, T5, T7 and the hold test are executed and recorded.

**Gate sequence:**
1. Ed names the id.
2. A Sol 6.0 seat implements in a linked worktree, with an exhaustive `WRITE_SCOPE` (the §3 files plus the new module and tests).
3. The lead runs the bench re-hash and replays.
4. Two distinct-lens refuters review: Opus on contract (authentication, pins), Sol xhigh on execution (tests, mutations).
5. Delta re-audit after every fix round.
6. A cold Fable final gate on the final head (irreversible action).
7. Merge.
8. Post-merge re-hash and B2 check, recorded with H1.

## 6. Name

Keep `d079_calibration_acceptance_v2_n12_25g83_r1`.
- The id is inside the input seal (issuer `:2343-2344`). Renaming would change a sealed input of the gated derivation.
- The name states the schema, corpus size and epoch.
- `r1` restarts per epoch, so a B4 cap re-issue becomes `_r2`. Nit: the n17 lineage used `r` as a family-wide counter (r3–r7). The issuing record should say which reading applies here.

The name must be settled **before** the bytes are written.

## 7. Stop or re-order

1. **Re-order:** ask Ed for the name first, because of the seal.
2. **Possible stop (mandatory under #421).** Production code never passes an explicit acceptance (every caller uses the default, `:2013`). So after the swap, any re-evaluation of recorded 25F84 bundles is judged against 25G83 identity and may come back stale. The R7 precedent never exposed this, because R7 kept the same identity. Before merge, re-run one existing 25F84 analysis before and after the swap and diff the outputs. If they differ, freeze that path to the acceptance recorded in the bundle. That would be a separate step. (Inference: I did not run it.)
3. **Judge's items:** the `_issued_d079` routing reading (§3.3) and the floor-mint omission (§3).
4. **For the magistrate:** if the cap council is about to choose route R, r1 is soon stale (B4). Issuing still earns a live default that matches the machine and exercises the swap once. It is not a stop.
