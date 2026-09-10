# 10 — Cold Fable design memo: bootstrapping a new calibration identity epoch (25F84 → 25G83)

**Contamination disclosure.** This seat ran as a fresh non-interactive session on the detached worktree at 58d4696b. I read only the brief, exhibit 38 (Astra's consult), exhibit 39 (the lead's record), and the code and contracts they cite; every line number below was read this session on this worktree (origin/main is d84da72e; none of the cited files differed in the regions cited). I did not open RUN_STATE.md, TASK_QUEUE.md, docs/process/, other process traces, .claude/, or any CLAUDE*.md, and I did not look for the Astra or Opus seats' output. One unavoidable contamination: the harness injected the global and project CLAUDE.md text and a one-line-per-entry memory index into my system prompt. Those index lines told me, before I read the brief, that a G2-a window had been prepared for 09-12 02:56, that a "sensible gates" directive exists (tolerances sized to the instrument, roughly 1 J to 5 J), and that "quiet" means machine state rather than night. I opened none of the memory files. Nothing below depends on those lines except where I flag it. No hardware, custody, or rehearsal checkout was touched. No edits, no git writes.

Terms used below. *Identity epoch*: the six-field vector {os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id} that an acceptance binds (`joulewise/calibration_ledger.py:100-107`). *Acceptance*: the issued JSON artifact whose corpus statistics set the two operative screens. *Observation*: one 59-pulse fiducial capture written as a ledger reservation plus finalization (`docs/contracts/powermetrics_fiducial.md:27-29`). *b_fiducial_s*: the per-observation calibration bound, the largest onset/offset residual (`powermetrics_fiducial.md:58`). *Bracket screen*: the corpus range, quantized to 1 µs, used to judge pre/post drift; *pre-flight level screen*: the corpus maximum, used to judge one observation's level (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` field `decimal_derivation.rounding`). *Derivation-only*: an observation captured to build a future acceptance, never to license a measurement.

## D1. Derivation-only capture route — recommendation

**Add one mode flag, `--derivation-only`, to the existing writer, and run it under the existing `DIAGNOSTIC_NO_PACK` night class with a new chain file. No new night class, no new writer.**

Why the writer refuses today. `main` builds the live epoch from sysctl (`scripts/validate_powermetrics_fiducial.py:1701-1709`) and calls `_derive_preflight_systematic_screen_s(planned_epoch)` (`:1711-1713`); that function authenticates the active issued artifact (`:364-392`) and raises `acceptance_artifact_epoch_mismatch` when any field differs (`:394-404`). The refusal is emitted before the ledger lifecycle begins (`:1744-1757`) and before any hardware work. The screen it returns is later used for exactly one thing: labelling a `valid` capture `systematic-invalid` when its bound exceeds the corpus maximum (`:2213-2219`).

What the new mode does, in order:
1. Requires `--allow-live` as today (`:1526`, refusal at `:1657-1660`) and refuses if combined with bracket mode `--session-id`/`--slot` (`:1586-1595`) or `--rederive-from` (`:1582`). Derivation-only captures are standalone, reservation-first appends (`:1744-1746`).
2. Still authenticates the ACTIVE issued artifact for its protocol and estimator pins (`:385-392`), because a new-epoch observation must be replayable under the same estimator bytes that will derive the successor. Then, instead of refusing on epoch mismatch, it REQUIRES the mismatch: if the live epoch equals the active artifact's epoch the mode refuses with a new reason `derivation_only_epoch_already_issued`. This is what keeps the mode from being a bypass: it can only run when no ordinary capture could.
3. Records everything the ordinary path records: the six-field epoch and the full T1 vector including `powermetrics_sha256` and the MLX version (`:1740-1744`; exhibit 38 V3 shows the binary hash on every ledger row), the raw plist and events under content hashes, and `manifest.json`. Adds one manifest field `capture_role: "derivation_only_nonclaim"` and `preflight_level_screen: null` so the bundle says on its face that no screen judged it. Ledger receipt keys are an exact set (`joulewise/calibration_ledger.py:643-644`, `:1041`), so the marker goes in the bundle manifest, not the receipt.
4. Disposition: `valid` or `ordinary-invalid` only. `systematic-invalid` is impossible because there is no same-epoch screen; the writer sets `preflight_systematic_screen_s = None` and skips the comparison at `:2213-2219`. For information only, the writer also records in the manifest whether the bound exceeded the PRIOR artifact's screen (`0.032898493715362`); see D3 for how that is used.

What it does not license, structurally. Every consumer that turns an observation into a claim compares the observation's or the acceptance's epoch to its own: the bracket evaluator returns `stale` on any field difference (`joulewise/calibration_bracketing.py:1531-1536`), the corpus-doubling trigger counts only same-epoch valid rows (`:1803-1810`), the prior-set validator maps every prefix row into the artifact's epoch catalog or refuses (`:1370-1377`), and the ordinary writer refuses at `:394-404`. A 25G83 row therefore cannot be consumed by any 25F84 artifact, and no 25G83 artifact exists until D4 issues one. No G2-a, floor, or claim path changes. The G2-a chain's own screen line (exhibit 38 Q3, runsheet `:500`) and `bind-window` remain untouched and still refuse.

Night shape. `DIAGNOSTIC_NO_PACK` exempts only pack condition C2 (`joulewise/night_gate.py:435-441`); C1 and C3–C5 still apply, and the class requires a registration path (`:341`). The driver executes the chain file bound by path and digest in the plan (`scripts/run_night.py:1168`, `:1240`). So the change is one new chain script: 600 s settle once, then a fixed loop of N standalone `--derivation-only --allow-live --power-policy ac_high_power` captures with a fixed idle gap, no bracket session, no probes, no pack. The window plan's `window_max_s` bounds the loop (`night_gate.py:269-270`).

Minimal change list (D1):
- `scripts/validate_powermetrics_fiducial.py:_parser` (`:1523` region): add `--derivation-only`; refuse with `--session-id`, `--slot`, `--rederive-from`.
- `scripts/validate_powermetrics_fiducial.py:main` (`:1711-1719`): branch on the flag; call a new `_authenticate_active_artifact_for_derivation_only(planned_epoch)` that reuses `:364-392` and inverts the epoch test; set `preflight_systematic_screen_s = None`.
- `scripts/validate_powermetrics_fiducial.py:main` (`:2213-2219`): skip the systematic comparison when the screen is `None`; write the two manifest fields.
- New chain `scripts/night_chains/calibration_derivation_only.sh` (naming to match the G2-a chain's home) plus its digest in the night plan.
- Tests: refusal matrix for the three flag conflicts and for `derivation_only_epoch_already_issued`; a fixture run under `--identity-epoch-json-for-test` (`:1573`) proving a 25G83 row appends with `valid` and that `evaluate` on the r6 artifact still reports `stale` for it.

## D2. Ledger representation — recommendation

**One canonical ledger carrying both epochs; the successor selects an epoch-pure corpus by pre-registered rule. Reject a second anchored ledger.**

Facts. The ledger already stores a full epoch per row (`calibration_ledger.py:100-107`, reservations require the complete vector at `:774-785`). Claim evaluation requires one immutable snapshot threaded through every consumer and exact agreement with the committed head pin (`docs/contracts/calibration_ledger.md:12-14`); the head pin is the anti-rollback boundary (`:189`). Historical import is genesis-only (`:15-18`).

What blocks the successor today, all in issuance validation, none in the ledger:
- `_prior_set_matches_import_cutoff_prefix` refuses if any row at or before the cutoff is not an import row (`calibration_bracketing.py:1363-1364`) and requires every row's epoch to map to exactly one catalog entry (`:1370-1377`).
- The issued-artifact validator requires the catalog to be exactly `{"d079_epoch"}` equal to the artifact's identity (`:522-525`) and every prior observation's `epoch_id` to be `"d079_epoch"` (`:562`).
- The bootstrap preparer refuses a receipt that maps to other than one artifact epoch (`scripts/calibration_ledger_bootstrap.py:289-296`); it is not on this path and needs no change.

Pros of the canonical ledger: no second writer, no second head pin, no second custody chain; the 25F84 history stays visible in the successor's prior set, so the successor can prove it did not roll back or fork (`calibration_ledger.md:53-55`, `:220-222`); one snapshot per consumer is preserved. Cons: three validator relaxations (below), and the successor's prior set grows to 38 plus 2N rows. Cons of a separate ledger: a fresh genesis ledger cannot carry the r6 prefix, so the successor's prior set would begin at zero and the anti-rollback continuity between generations would rest on prose; a second `DEFAULT_LEDGER_PATH`/head pin (`calibration_ledger.py:95-98`) would touch every consumer that threads the snapshot. Relabelling existing rows is forbidden by the ledger's never-rewrite rule (r6 itself records exclusions in notes rather than editing rows: r6 JSON `:562-563`).

Minimal change list (D2), all keyed per generation so r6 and predecessors keep validating byte-identically (`calibration_bracketing.py:468-476` selects expectations by the artifact's own id):
- `calibration_bracketing.py:_D102_GENERATION_DERIVATIONS` (`:218`): add `epoch_catalog_ids` and `prior_prefix_mode` (`"import_only"` for existing generations, `"import_plus_live"` for the successor).
- `calibration_bracketing.py:load_calibration_acceptance_bound` region (`:522-525`, `:562`): compare the catalog key set and `epoch_id` values against the generation's registered set instead of the literal `{"d079_epoch"}`.
- `calibration_bracketing.py:_prior_set_matches_import_cutoff_prefix` (`:1363-1364`): under `import_plus_live`, accept finalized live rows with a content id; keep the exact tuple comparison at `:1366-1385`.
- Contract: `docs/contracts/calibration_ledger.md` gains a short "Epoch bootstrap" section stating that live rows of a not-yet-issued epoch are non-claim-bearing until a successor names them.

## D3. Corpus design and stopping rule — recommendation and pre-registration text

Arithmetic first. r6's 17 members were captured over four days (5, 6, 1, 5 per day from member ids 20260722–25), range 23.175–32.898 ms. D-102 cl.2 notes the corpus spans four days on purpose (`docs/decision_log.md:6483-6485`). Historical attrition: 38 observations became 30 valid, 2 systematic-invalid, 6 ordinary-invalid (`decision_log.md:7710`), so about 79 % of attempts return `valid`. The pulse train alone is about 196 s (3 warmups plus 59 one-second pulses, gaps 1.5 s plus a van der Corput term, 5 s baselines each side; `powermetrics_fiducial.md:27-29`); the brief's 4–8 min per observation includes sampler start, artifact writing, and countdown. The chance that the next valid same-epoch capture exceeds the corpus maximum is 1/(n+1): 5.6 % at n=17, 5.0 % at n=19, 4.0 % at n=24. The two-draw prediction uses t(p, n−1) (r6 JSON `two_draw_prediction_derivation`), so n≥17 keeps the quantiles near r6's.

One-night design (window 03:00–06:30, 210 min; the draft plan's `window_max_s` 13500 s = 225 min per exhibit 38): 10 min settle + 24 attempts × (6 to 8 min) + 23 gaps × 1 min = 177 to 225 min. Fits only at the 6-min pace; at 8 min it overruns. Expected retained ≈ 24 × 0.79 ≈ 19. All members share one boot and one night; between-night variation is unsampled.

Two-night design: 2 × (10 min settle + 14 attempts × 8 min + 13 min gaps) = 2 × 135 min. Expected retained ≈ 28 × 0.79 ≈ 22. Samples two boots and two nights, which is the nearest feasible analogue of r6's four-day spread. **Recommend two nights**, with the one-night plan as the fallback if Ed prefers calendar over spread.

Exclusion rules carry over from r6: an observation whose anchor-v3 fit is `affine_clock_fit_empty` is excluded and recorded in `derivation_notes.excluded_predecessor_members`-style notes (r6 JSON `:535-563`); ordinary-invalid captures are never members. On the "new systematic failure" clause for a fresh epoch: D-102 says a trigger observation is judged under the PRIOR artifact (`decision_log.md:6481-6483`). r6 IS the prior artifact, so each new-epoch capture is compared to r6's level screen 0.032898493715362 s for information (D1 step 4). That comparison does not exclude anything from the new corpus; excluding by the old screen would fit the new threshold to itself. It does gate issuance: see rule 6 below.

Pre-registration text (to be committed before the first capture, verbatim):

> **Epoch-bootstrap corpus rule, generation d079_v2 under os_build 25G83, powermetrics sha256 b762e5bf…1330c5.**
> 1. Members are ledger rows with event `finalization`, disposition `valid`, sequence > 76, identity epoch exactly {25G83, Mac15,9, ac_high_power, 100, joint_loss_sublevel_interval_branch_v2, powermetrics_pulse_fiducial_v3}, whose anchor-v3 replay from primary bytes resolves. Rows whose replay returns `affine_clock_fit_empty` are excluded and listed by attempt id in the derivation notes.
> 2. Capture plan: two DIAGNOSTIC_NO_PACK nights, 14 attempts each, one 600 s settle per night, 60 s idle between attempts, fixed order, no operator or agent present. Attempts are not repeated to replace failures.
> 3. Stopping rule: stop when both planned nights have run. If retained n < 17, run one further identical night; never lower 17. If retained n ≥ 17 after night one and Ed has pre-authorized the one-night fallback, night two may be cancelled only by a decision recorded before night two's arm.
> 4. Statistics are computed exactly as r6: decimal minimum, maximum, range, mean, sample SD; t(0.975, n−1) and t(0.995, n−1) two-draw predictions; bracket screen = range quantized to 1e-6 s ROUND_HALF_EVEN; pre-flight level screen = maximum quantized to 1e-15 s; max budgetable drift = the 99 % two-draw prediction.
> 5. No member value, screen, or statistic is examined before the corpus is closed under rule 3.
> 6. Systematic-shift check: if the new corpus maximum exceeds r6's maximum by more than r6's range (0.032898 + 0.009724 = 0.042622 s), or if more than two retained members exceed r6's level screen, issuance halts for Ed's written review. The check informs; it never edits membership.

Ed decides (scientific rules): the retained minimum (17), the night count, rule 6's thresholds, whether the D-125 lineage floor 0.010818 s applies to the successor's bracket screen as max(range, floor) or is retired (exhibit 38 residual risk). The magistrate decides: attempt count within the window, gap length, chain file contents, arm dates.

## D4. Successor issuance — recommendation

The reissue tool cannot do this: it deep-copies the predecessor's members and STOPs on `member_set_changed` (`scripts/reissue_calibration_acceptance.py:249-262`, `:479-486`). The bootstrap preparer is import-only (`calibration_ledger.md:15-18`). The historical route used bespoke build scripts (exhibit 38 Q2). Recommend a tracked, parameterized issuer, `scripts/issue_calibration_acceptance_generation.py`, so D5 is one command next time:

1. Load the ledger snapshot at head, verify the committed head pin, select members by the pre-registered rule.
2. Replay anchor-v3 per member from content-hashed primary bytes at the governed cell budget, exactly r6's `per_member_procedure` (r6 JSON `:521-522`).
3. Compute the decimal statistics and operatives (D3 rule 4; D-102 cl.4 semantics `decision_log.md:6490-6497`).
4. Emit `configs/calibration/calibration_acceptance_d079_v2_n<N>_25g83_r1.json` with `prior_observation_set` covering sequences 1..head under a two-entry catalog, `ledger_cutoff` at head, `prospective_rederivation.triggers` with `corpus_doubles_from_<N>_to_<2N>`, and `derivation_notes` naming the predecessor, the excluded attempts, the rule-6 outcome, and the r6-screen comparison per member.

Registration (all keyed by the new id): `calibration_bracketing.py` new id and sha constants and `ISSUED_ACCEPTANCE_REGISTRY` entry (`:160-171`), `ACTIVE_ACCEPTANCE_ID`/`DEFAULT_ACCEPTANCE_BOUND_PATH` (`:173-174`), a new `_D102_N<N>_25G83_DERIVATION` in the table (`:218`); `tests/verify_calibration_acceptance_corpus.py:EXPECTED_BY_ACCEPTANCE_ID` (`:24`, unregistered ids refuse at `:70-73`) with `stored_lexeme_is_member_value: False`.

D-138 atomic transaction (`decision_log.md:10072-10080` forbids fixture re-keying to go green): successor bytes; the registry, default, and generation table above; the 29 tracked files that pin the r6 id by name (my grep this session: `joulewise/arm_readiness.py`, `scripts/floor_mint_pinsets/schema_v2.json`, six campaign `generate_configs.py`, three `plan_tree.json`, three `acceptance-owner.json`, two floor-mint extraction specs, eleven tests, the verifier); regenerated packs, T1 projections, and chains with re-hashed digests; the staged R2 patch `15-r2-coverage-ulp-staged-for-d138.patch` and its four regressions; the cold science gate's atomic fan-out clause (`docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:111`). The D-125 floor question must be answered before step 3 chooses the bracket screen.

Honest desk estimate: issuer + validator relaxation + writer flag + tests through the gauntlet: 1.5–2 desk days (the writer's crash matrix and exit tests are large). Derivation, replay, and cold science gate after the corpus closes: 0.5–1 day. Fan-out, pack regeneration, clone proof: 0.5–1 day. Total about 3–4 desk days, of which about 2 precede the first night.

## D5. Recurrence — proposed standing shape (not ruled here)

- **Lane template `EPOCH-BOOTSTRAP-<build>`** with fixed steps: (1) confirm mismatch at the desk; (2) commit the pre-registration text with the build and binary hash filled in; (3) arm the derivation chain for the ruled night count; (4) run the issuer; (5) cold science gate on rule 6 and the statistics; (6) D-138 transaction from a generated pin inventory. With D1–D4 landed, a future update costs the ruled nights plus about one desk day.
- **Earlier detection.** Today the mismatch surfaces at `bind-window` during the dry run (exhibit 39), which is already at the desk. Move it earlier still with a daily desk probe at magistrate wake: compare sysctl `kern.osversion`, the powermetrics sha256, and the MLX version to the active artifact's epoch and T1; on mismatch, open the lane the same morning instead of at the next dry run. The macOS update installed 09-02 and was noticed 09-10 (exhibit 39); a daily probe closes that eight-day gap.
- **Ask Ed** whether automatic macOS updates should be deferred during a campaign (hardware/sudo, Ed's lane). Pausing updates between the corpus night and the last claim night is the cheapest recurrence control there is.
- **Pin inventory generator**: a script that lists every file naming the active id (the 29 above) so the D-138 transaction's scope is computed, not remembered.

## Calendar (PDT; conditional on the cold-gate ruling landing 09-10 and the rehearsal harvest occupying the 09-11 window per exhibit 39)

| Step | One-night design | Two-night design |
|---|---|---|
| Ruling + pre-registration committed | 09-10 | 09-10 |
| D1/D2 implementation through gauntlet | 09-10 to 09-11 desk | same |
| Corpus night(s), 03:00–06:30 | 09-12 | 09-12 and 09-13 |
| Derivation + cold science gate | 09-12 desk | 09-13 desk |
| D-138 transaction landed | 09-12 to 09-13 | 09-13 to 09-14 |
| Bind + arm G2-a | 09-13 | 09-14 |
| Earliest G2-a night | 09-14 | 09-15 |

A daytime quiet window (machine-state quiet, not darkness; exhibit 38) could pull night two of the two-night design onto 09-12 daytime if the unattended schedule allows, which would recover the one-night calendar without giving up the two-boot spread. That is Ed's call.

## Risks

1. The one-night plan at the 8-min pace overruns the 210-min window; retained n could fall below 17 in a single night and force a second night anyway.
2. Rule 6 could halt issuance if 25G83's powermetrics behaves differently; that is the rule working, but it adds an Ed round trip.
3. The validator relaxation in D2 touches the same function that authenticates every past generation; the tests must prove r6, r5, r4, r3, n19 still load byte-identically.
4. Writer surface: `--derivation-only` inverts one refusal; a mistaken flag on a matching epoch must refuse, and the test at D1 must prove it.
5. The 29-file fan-out is large; any pin missed leaves a stale-id path that fails at arm time, not at merge time.
6. The D-125 floor conflict, if left open, silently decides the successor's bracket screen.

## Questions for Ed

1. Retained minimum n=17 and two nights, or one night with the fallback in rule 3?
2. Rule 6 thresholds: "max exceeds r6 max by more than r6 range" and "more than two members over r6's level screen" — acceptable, or do you want tighter?
3. D-125: does the lineage floor 0.010818 s apply to the successor's bracket screen, or is the successor's own range operative as in r6?
4. May a daytime quiet window serve as the second corpus night?
5. Should automatic macOS updates be deferred for the campaign's duration?
