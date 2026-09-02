# Cold-gate ruling 182 — consult 171 (decode-unit identity; D-131 cl.2 amendment)

Cold Fable instance, fresh session. Read-only on `/Users/edr/code/JouleWise` (main @ a63d45bd).
Line numbers below are MAIN unless marked `wt:` (the packet's `identity_pins.py:1445-1466/:1614`
are worktree `JouleWise-wt-proj02-b` @ a37b0b9f, unmerged branch `feat/v5-prefill-realized-projection-02`;
on main the same code sits at `identity_pins.py:1364-1389` and `:1453`).

## Verdict: UPHOLD WITH AMENDMENTS (three amendments, one of them load-bearing)

Facts re-verified at the bench on the generated pack `scratchpad/p8/root/.../d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`:
- `A/decode` and `B/decode`: 20 configs, 8 `scientific_config_identity_sha256`, histogram 4/4/2/2/2/2/2/2, 8 manifests;
  prefill units 20/1. `declared_identity` matches ZERO of the 20 decode configs (declared has `prompt_tokens: 42`,
  no manifest fields; configs carry `suite_manifest_ref/_sha256`, no `prompt_tokens`) — `generate_configs.py:1305-1315`
  (`workload_for`, hardcodes `DECODE_PROMPT_TOKENS["A"]`), `:1862-1875` (emitted decode workload), `:2572-2588`
  (declaration built from `workload_for`). So the FIRST refusal is the declaration check `identity_pins.py:1376-1382`,
  not the multiplicity check `:1384-1389`. Both must be cured; the draft names only the second.
- Floor plans `d117_floor_qwen3-*_v5` exist in neither root (`ls configs/campaigns` → qwen25 floors only).
- Registration digest is a pure function of `dominance_criterion_registration()` (`generate_configs.py:489`), pinned at
  `tests/test_d165_dominance_closeout.py:1770`, `tests/test_night_gate.py:188`; no option touches it.

## Soundness or engineering?
The REFUSAL is a soundness fence (pre-registration: a declared identity that describes no emitted config, and a
unit pin `config_set_sha256` that would bind only one of eight member identities — `identity_pins.py:1498-1503`).
D-161 permits fail-closed here. The CHOICE among cures is engineering, ruled on soundness tie-break (D-044 exactness,
evidence lineage): (d) keeps exact identities and every downstream exact-match consumer (`analysis_engine/inputs.py:2947-2950`
replacement matcher; `whole_window.py:3569-3577` NEG-8 same-condition gate) untouched. The census check (draft item 3)
is pre-registration consistency (rotation rule vs emitted artefacts) — admissible under D-161, cheap, keep it.

## Q-A — is (d)+census strictly better than (a-i)? YES, on soundness; (a-i) is cheaper only in file count.
(a-i) moves identity onto a config-carried field (`workload_profile.suite_manifest_set_sha256`): (i) an operator-entered
claim inside the config, against D-131 cl.3 "derive; never enter" (`decision_log.md:8416-8422`); (ii) a `BenchmarkConfig`
closed-vocabulary change (schema contract, `publication_privacy.py` allowlist, pinned config hashes); (iii) it makes a
prompt-7 bundle identity-equal to a prompt-1 manifest entry in the replacement matcher (`inputs.py:2947-2950`, fallback
`matching_entry_ids[0]`) — an evidence-lineage loosening bought for bookkeeping. (d)'s missed-site cost is a late REFUSE,
which is the failure mode this repo prefers. UPHOLD (d). Sol's "(a) still yields 8 hashes because of the `decode-prompt=`
tag" is moot under (d): the set holds eight exact identities, tags included.

## Q-B — serialize the set hash into configs? NO. Configs unchanged (uphold the lean), with a placement amendment (A2).

## Q-C — what the synthesis dropped (load-bearing)
**C1 — the "producer and consumer carry EQUAL unit-set hashes" clause is unsatisfiable and must be struck.** Scientific
identity keeps every non-calibration tag (`identity_pins.py:221-230`): `d117-contrast-…-v5`, `production-window`,
`comparative-contrast`, `df-condition=<family>` differ between a floor pack and a contrast pack. v3 proves it: floor
`alpha` `config_set_sha256` bf0ea6a3… vs consumer `A/decode` 604f6e22… with byte-identical declared workload
(`configs/campaigns/d117_floor_qwen25_1p5b_v3/identity_pin_projection.receipts/projection-0001.json`,
`…d117_contrast_qwen25_1p5b_vs_7b_v3/…/projection-0001.json`). No code compares producer vs consumer `config_set_sha256`
(grep: only `identity_pins.py:1499`, the mint's OWN producer pin `mint_floor_artifact_generalized.py:2346-2353`, and the
key list `detection_floor.py:2098`). Floor→consumer binding is condition-family TRANSPORT: `analysis_manifest_v3.py:3395-3420`
(`allowed_consumer_condition_families` + `condition_family_sha256`), `inputs.py:3933-3960`; the exact-cell route
`inputs.py:3905-3915` is taken only when a floor cell shares the consumer's family id. Ruling as drafted would make GAMMA
unbindable to any floor. Sol's text was carried into draft items 2 and 5 without this check.
**C2 — the analysis gate is a subset check, not equality.** `inputs.py:3881` (`len(consumer_identities) != 1 → None`)
runs BEFORE both routes, so a freeze-only cure leaves the pack unanalysable (Fable seat, verified). But evidence may be a
legitimate subset of the 20 members (exclusions, LOO `inputs.py:3927-3929`); equality would refuse valid evidence.
**C3 — no new exact-key field.** `RECEIPT_UNIT_FIELDS`/`MODEL_RUNTIME_CONFIG_FIELDS` are exact-key validated
(`identity_pins.py:73-76, 59-66, 513-517`); adding `identity_unit_config_set_sha256` breaks every committed receipt that
arm-readiness tests load. `declared_identity.workload_profile` is a free mapping (`:62-71`, `:509-513`) — the set and
census live there. The mint compares per-component `scientific_config_identity_sha256` to the producer pin
(`mint_floor_artifact_generalized.py:2329-2353`), so a single-identity unit's pin must stay the raw scientific hash.
**C4 — nine committed receipts are not a constraint.** Any edit to `identity_pins.py` already changes
`source_file_sha256` (`:1143-1196`) and refuses arm re-verification of every frozen receipt (`:1846-1850`, `:2001-2005`);
tests pin those receipts by bytes, not re-derivation. Opus's "conditional derivation" is adopted for C3, not for them.

## Amendments (exact replacement text)
**A1 — draft item 2 becomes:** "Unit binding by closed SET. For each projection unit, `config_set_sha256` is the unit's
config-set digest: when the unit's members yield one scientific identity it is that hash (byte-compatible with the shared
mint pin and every committed receipt); otherwise it is
`SHA256("joulewise.identity_unit_config_set.v1" ‖ "\n" ‖ "\n".join(sorted(unique member scientific hashes)))`.
The declared closed set (manifest ref, effective sha256, declared member count per manifest) is recorded in
`declared_identity.workload_profile.suite_manifest_set` and the common profile in the sibling keys; freeze compares each
config's workload minus `suite_manifest_ref/_sha256` to the common profile, requires each config's manifest sha to be a
declared member, requires every declared member to be emitted, and refuses any extra, missing, or duplicate member.
Cross-pack floor binding is UNCHANGED: condition-family transport (`analysis_manifest_v3.py:3395-3420`); no
producer↔consumer config-set equality is required or checked."
**A2 — the analysis gate (`inputs.py:3881`) becomes:** "consumer evidence identities must be non-empty and a SUBSET of
the frozen consumer unit's declared set (source: the frozen receipt bound by the U8 readiness record); any identity
outside the set refuses; the exact-cell route stays single-identity-only." `_source_regime`
(`mint_floor_artifact.py:786-787`, reused by the generalized mint) and the producer-pin compare (`…generalized.py:2346-2353`)
gain the same set semantics ONLY IF the ALPHA/BETA plans rotate prompts — that is a floor-plan design decision to be
pre-registered when those plans are generated (draft item 7's closure evidence covers it); a single-prompt floor needs no
mint change. The magistrate should decide the floor's prompt regime before ALPHA/BETA generation, not in this ruling.
**A3 — D-131 cl.2 replacement text:** "GAMMA retains exactly four ordered units (`A/decode`, `A/prefill_p<N>`,
`B/decode`, `B/prefill_p<N>`; N is the G2-fixed prefill length). Each unit binds an independently declared, closed set of
exact scientific-config identities, digested into `config_set_sha256` as the unit's config-set digest (one member: the
scientific hash; several: the domain-separated set digest). Within a unit, the declared per-manifest member census —
computed from the pre-registered rotation rule, never folded from the emitted configs — must equal the emitted census at
freeze; a missing, extra, duplicate, or unauthenticated member refuses. Which manifest a member binds is a realization
fact recorded per config. Floor producer and consumer units bind through condition-family transport; their config-set
digests are not required to be equal." Cl.3 rider: "Raw config bytes and inventory bindings remain authoritative for
member identity; declaration compares the projected common profile plus declared set, never a re-typed workload."
Draft items 1, 3, 4, 6, 7, 8 stand. Item 6 adds counterfactual (iv): declaration re-typed from `workload_for()` → REFUSE
at `identity_pins.py:1376-1382` (the first live refusal, currently uncovered — fixtures derive declared FROM config,
`tests/test_identity_pins.py:134,246`).

## Sequencing (upheld) and one process note
Separate branch off the projection-02 merge head; red generated-pack freeze test first (Sol F3 recipe), cure second;
arming forbidden until U8 passes (`decision_log.md:8431-8436`). Process note for the log: two seats plus the synthesis
carried "producer/consumer sets equal" from prose to draft contract text without opening a committed receipt; the
pre-transaction "decided ≠ done" sweep should include one receipt-level check of any cross-pack equality clause.
