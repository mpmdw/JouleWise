# 151 — Opus design consult: continuing r6 onto identity epoch 25G83 (blind)

Checkout read: `/Users/edr/code/JouleWise-wt-epoch-integration` @ 7107657d. Read-only; nothing modified.

## Decisions first

- **Q1: none of (A), (B), (C) as framed. Recommend (D): a separately-governed, byte-pinned CONTINUATION artifact + a loader that treats a registered continuation as an additional APPLICABLE epoch.** r6 is untouched and stays live.
- **Q2: after (D), one loader change closes the only production refusal.** The powermetrics sha does **not** stale r6 (it is not an identity field). The desk `check` watch still prints MISMATCH/rc 3 and should be taught the continuation. Every campaign pinset stays valid *because* r6 stays live — this is the decisive economic argument against (A)/(B).
- **Q3: nothing in the issuer blocks counting night one as registration night one.** Its only blindness gate is ledger state. No code change needed.
- **Q4: S9's record should be a fully re-derivable transcript; the Q1 tool re-derives 100 % of the science and cross-checks only non-science provenance.**

## Q1 — the mechanism

### Why (A) is not available (this is the load-bearing finding)

`_valid_acceptance_bound` resolves the artifact's TARGET epoch as the single `prior_observation_set.epoch_catalog` entry whose six-field vector equals `identity_epoch` (`joulewise/calibration_bracketing.py:757-762`, `:820`, `:853`), then enforces **PURITY**: every corpus member's own prior-set row must carry that target epoch id (`:918-925`). r6's 17 members are all `d079_epoch` = `os_build 25F84` (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:21`, `:180`). An "r7 carrying `identity_epoch.os_build = 25G83` with the same corpus" therefore **fails validation** — by design, because that check exists precisely to stop a previous-epoch corpus from setting the new epoch's screens. Making (A) work means weakening the anti-contamination fence that PR #315 just built. Reject.

(B) is worse: `derivation_sha256` is the canonical hash of **every** other top-level key (`:677`, `:781`; issuer `scripts/issue_calibration_acceptance_generation.py:1636-1646`), so an in-place amendment re-pins both the file sha and the derivation sha, breaks "retained byte-identical forever" (`derivation_notes.predecessor.relationship`), and invalidates every downstream pin. Reject.

(C) — a table in code — is the right *topology* but the wrong *custody*: the evidence for a scientific continuation would live as a Python literal instead of an authenticated artifact.

### (D) the recommendation

**Artifact delta: none to any acceptance file.** A new file `configs/calibration/epoch_continuation_d079_r6_25g83.json`, schema `joulewise.calibration_epoch_continuation.v1`:

```
schema_version, continuation_id, decision_ids: ["D-102"],
acceptance_id: "d079_calibration_acceptance_v2_n17_r6",
acceptance_file_sha256, acceptance_derivation_sha256,   # what it continues, pinned
continued_identity_epoch: {six fields, os_build 25G83},  # differs from the acceptance in >=1 field
ruling: {channel: "directive issue 316", d102_addendum_date, authority: "owner"},
rule: {level_screen_s, operative_bracket_screen_s, source: "r6 ratified_operatives", m_minimum: 6},
evidence: {ledger: {schema, head_sequence, head_digest}, session_id, session_kind: "derivation",
           session_state, declared_slots: 12,
           slots: [{attempt_id, content_id, manifest_sha256, instrument_evidence_sha256,
                    disposition, anchor_v3_resolved, anchor_v3_detail, b_fiducial_s}] x12,
           m, retained_max_s, retained_min_s, retained_range_s},
verdict: "pass", derivation_sha256   # canonical hash of all other keys, same rule as the acceptance
```

Registered in a new `EPOCH_CONTINUATION_REGISTRY` in `calibration_bracketing.py` keyed by `continuation_id` with a `file_sha256` pin, exactly mirroring `ISSUED_ACCEPTANCE_REGISTRY` (`:136-175`).

**r7's `derivation_sha256` question is moot: there is no r7.** r6's stays `18d09aa9…`, which is why `configs/campaigns/*/plan_tree.json`, `*/generate_configs.py` and `*/arm_readiness.sources/acceptance-owner.json` (all of which pin `0227bca3…` **and** `18d09aa9…`) need no churn. Any option that mints a new live generation re-pins ~8 campaign config trees plus the floor-mint pinsets (`scripts/mint_floor_artifact_generalized.py:2301-2302`).

**Loader change (the smallest that is not a workaround), two parts, both in `evaluate_calibration_bracket`:**

1. Freshness (`:2046-2054`, `:2106`): if `stale_fields` is non-empty, look for a registered, byte-authenticated, `verdict == "pass"` continuation whose `acceptance_id` equals this artifact's, whose `acceptance_file_sha256`/`acceptance_derivation_sha256` equal the loaded artifact's, and whose `continued_identity_epoch` equals `observed_identity` **field-for-field**. On a hit: `status = "fresh"`, `basis = "epoch_continuation"`, and the record carries `continuation_id`, the continuation's file sha, the session id, `m`, and the verdict. On any miss: today's `calibration_acceptance_bound_stale`, unchanged. **Operative comparators are not touched at all** — screens still come from `decimal_derivation.ratified_operatives` via the generation registry (`:2044`, `acceptance_generation_operatives` `:505-520`).
2. **Trigger scope — mandatory, not optional.** Three prospective triggers match observations by `dict(observation.identity_epoch) == dict(identity_epoch)`: corpus doubling (`:2320-2326`), range expansion (`:2331-2344`), systematic failure (`:2347-2354`). Leaving them as-is means that after continuation **no 25G83 capture can ever fire them** — continuation would silently disable the very guard that catches the instrument moving. The matching set must become `{identity_epoch} ∪ {continued epochs}`. I recommend including corpus doubling too (it only ever stales *earlier*, which is the safe direction). The artifact's `triggers` vocabulary is validated as an exact set (`:797-805`) and must **not** change.

**Tool: a new script `scripts/issue_epoch_continuation.py`.** Not a reissue sub-command — `reissue_calibration_acceptance.py` reconstructs a whole acceptance candidate from a predecessor (`:241-260`), the wrong shape. Not an issuer sub-command — that mints a generation from a corpus. Follow the r2..r6 precedent: emit with a `candidate_not_issued` marker; a separate governed transaction removes it and adds the registry row.

**What the tool must AUTHENTICATE (re-derive, never trust a file):** load the ledger snapshot with `require_committed_pin=True`; require the named session present, `session_kind == SESSION_KIND_DERIVATION`, state terminal, `len(declared_slots) == 12`; for each finalized slot re-read `manifest.json` + `instrument_evidence.json`, require they hash to the ledger row's recorded digests, recompute `content_id_from_artifact_hashes`, call `anchor_v3_replay_outcome` for resolved/not, and require the stored `b_fiducial_s` lexeme equals the row's `exact_bound_lexeme_s` (the issuer's `_select_members` pattern, `scripts/issue_calibration_acceptance_generation.py:1040-1120`); require every retained row's identity epoch unanimous, equal to `continued_identity_epoch`, and differing from the acceptance's in ≥1 field; recompute `m` and refuse (`INCONCLUSIVE`) if `m < 6`; recompute max/range in `Decimal` and compare against the operatives read from the **authenticated** r6 via the registry, not from any record.

**Tests:** continuation authenticates → `freshness.status == "fresh"`, `basis == "epoch_continuation"`, screens byte-identical to the 25F84 path; sha-rotated continuation file → stale; continuation naming a different acceptance id or a 25G83 vector differing in one field → stale; `verdict != "pass"` → stale; a 25G83 valid capture outside the corpus range → range-expansion trigger fires and stales (the mutation that proves part 2); tool refuses on m<6, non-terminal session, ≠12 declared slots, hash mismatch, epoch disagreement; r6 file sha and derivation sha unchanged (freeze test).

## Q2 — surfaces that still refuse on 25G83

| Surface | Refuses? | Science-bearing |
|---|---|---|
| Loader identity freshness, `calibration_bracketing.py:2046-2054`, `:2106` | yes, until the (D) change | **yes** — the one that matters |
| `whole_window.py:247`, `analysis_engine/claims.py:64` | consume `calibration_acceptance_bound_stale`; no own epoch logic | yes, but fixed upstream |
| Prospective triggers `:2320-2354` | no refusal — they go **silent**, which is worse | **yes** (part 2 above) |
| `powermetrics_sha256` | **does not stale r6** — not in `IDENTITY_EPOCH_FIELDS` (`calibration_ledger.py:110-117`); `:1465` only checks a capture against its own evidence | no |
| Desk `check` epoch watch, `issue_calibration_acceptance_generation.py:114`, `:290-330` | yes, rc 3 (os_build + powermetrics both MISMATCH) | no — identity comparison only, authorizes nothing; but if the runbook gates on rc 0 it reads as a permanent failure, so teach it the continuation |
| `check --preregistration` | matches `b762e5bf…` (prereg line 135) — that is the FAIL route, correct as-is | yes |
| Campaign pins `0227bca3…`/`18d09aa9…` in `configs/campaigns/*` ×8, `arm_readiness.sources/acceptance-owner.json` | **no churn under (D)**; would all need re-pinning under (A)/(B) | no |
| `arm_readiness.sources/acceptance-owner.json` pins `joulewise/calibration_bracketing.py` sha | regenerate after any loader edit (true of every option) | no |
| `preregistration_d079_epoch_25g83_rev1.md` | stays on file un-withdrawn, per the ruling | n/a |

No other `25F84` literal outside `configs/calibration/*.json` and `tests/`.

## Q3 — FAIL route: can night one count as registration night one?

**Yes, with no code change.** The issuer's blindness gate is `refuse_open_registration` (`scripts/issue_calibration_acceptance_generation.py:991-1011`), which refuses only while a named session is **not terminal** — its docstring says so explicitly ("nothing is computed or reported before every session of the registration is terminal"). There is no "has anyone read the values" predicate anywhere in the file. The other refusals are all ledger-state: `refuse_repeated_sessions` (`:965-989`), `_registration_observations` requires each session present and `session_kind == SESSION_KIND_DERIVATION` (`:1013-1036`), unanimous identity epoch (`:1222-1227`), `distinct_nights == PREREGISTERED_NIGHT_COUNT` unless `--nights-ruling` (`:1229-1237`), 12 declared slots per session unless `--slot-count-ruling` (`:1238-1247`), and B-1 `os_build`/`powermetrics_sha256` equal to the pre-registration pins (`:1248-1262`). A night-one session run by the merged chain as a 12-slot derivation session on 25G83 satisfies every one of them, and the three-night count is only evaluated at issuance time when all three ids are named together. The magistrate reading its values leaves no trace the issuer can or does inspect.

## Q4 — what the S9 desk tool should emit

Emit a **transcript, not a verdict to be believed**. Required: `schema_version`; `tool_sha256`; ledger path + `{ledger_schema, head_sequence, head_digest}` as read; `session_id`, `session_kind`, `session_state`, ordered `declared_slots`; per slot `{attempt_id, content_id, manifest_sha256, instrument_evidence_sha256, disposition, anchor_v3_resolved, anchor_v3_detail, b_fiducial_s lexeme or null}`; `m`; `retained_min_s/max_s/range_s` as lexemes; the reference block `{acceptance_id, acceptance_file_sha256, acceptance_derivation_sha256, level_screen_s, operative_bracket_screen_s, source_path_in_artifact}`; the rule text with its constants and `m_minimum`; `verdict` and `rc`.

The Q1 tool **re-derives** every one of those from the ledger and the primary bytes — head pin, session kind/state/slot count, each slot's two hashes and content id, each anchor-v3 outcome, each `b_fiducial_s`, `m`, min/max/range, both r6 operatives, and the verdict — and **refuses, naming the field, on any disagreement**. It merely **cross-checks** `tool_sha256`, the emit timestamp and `rc`, which are provenance, not science. Net effect: S9's record is a witness the continuation tool can contradict, never an input it depends on — which is what keeps `judge_under_prior_artifact_never_self_fit` honest, since every retained value is judged against r6's own authenticated operatives and nothing in r6 is refitted.

## Where I disagree with the brief

1. **Candidate (A) is not merely larger, it is refused by the code** (`:918-925`). The brief presents it as the leading candidate; it cannot validate without weakening the cross-epoch purity fence. This is the main substantive disagreement.
2. **The brief asks whether r7's `derivation_sha256` equals r6's.** Under (D) the question dissolves, and that is a feature: preserving r6's `18d09aa9…` is what spares ~8 campaign pin trees and the floor-mint pinsets. If the magistrate nonetheless prefers a new generation, note that `derivation_sha256` covers all keys (`:677`, `:781`), so equality is impossible in principle and the churn is unavoidable.
3. **The brief does not mention the trigger-scope hole.** I regard widening the identity match at `:2320-2354` as *part of* the minimal change, not a follow-up: a continuation that leaves it unfixed buys 25G83 capture by switching off the guard that would detect the instrument actually having moved. Shipping freshness without it would be the defect I would refute.
4. **Brief fact 1's parenthetical worry about the sampler sha is unfounded** — `powermetrics_sha256` is not an identity-epoch field, so it never staled r6.
