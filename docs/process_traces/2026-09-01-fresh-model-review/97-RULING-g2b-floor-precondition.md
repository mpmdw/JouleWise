# Ruling 97 — G2-b R-6: the aggregate-floor precondition is struck; pack-id spelling; ordering regression

Magistrate ruling, 2026-09-01 evening. Resolves the NEEDS-RULING recorded on
kernel row `V5-G2B-SHAKEDOWN-01` by ruling 89 R-6 ("the G2-b runsheet's
B-SUPPLY demands a real `_v5` aggregate-floor artifact before G2-b, but the
`_v5` floor-producer corpus is collected inside the transaction; one of the two
is wrong"). Three-seat consult on the packet before ruling (three-seat rule,
2026-08-26): Sol xhigh (execution), Opus 5 (contract lens), blind fresh Fable
(execution + fail-closed design). All three seats AGREE with R-6a/b/c below;
their amendments are adopted as R-6d..R-6g. Consult packet:
scratchpad `consult-r6-floor-precondition.md`; seat reports `out/97-sol-r6-consult.md`
and the two agent transcripts.

## Facts (each verified by the magistrate at head `ceae5c7f` after the seats corrected two packet citations)

F1. The finalizer never reads the aggregate floor before the member-cover
    gate. `finalize_prospective_analysis_manifest_v3`
    (`joulewise/analysis_manifest_v3.py:3807`) validates the prospective
    manifest (`:3840-3853`, no floor path passed) and then calls
    `_authenticate_finalization_inputs` (`:3339`), whose order is: verdict
    read `:3355-3372` → `_verify_basis_members` `:3373` (refuses
    `analysis_finalization_member_cover_mismatch` at `:3048` when the basis
    does not cover all 80 frozen members) → bracket `:3380-3414` → ledger and
    head `:3416-3479` → campaign-log row `:3562-3573` → **aggregate floor first
    touched at `:3575-3577`** (`_path_under_root`, then `_read_strict_object`).
    An absent floor path refuses `analysis_finalization_attachment_missing`
    at `:1503-1507` — a leg the one-block run never reaches.
F2. The refusal checker's `_copy_path`
    (`scripts/check_window_provenance.py:467-474`) is a lexical containment
    test only; it never requires the floor file to exist, and the finalizer
    runs on a `copytree` copy (`:503`), so no finalized bytes can land in real
    custody under any floor state.
F3. Bench probe (magistrate; reproduced independently by both agent seats
    with four to seven floor states): on the synthetic one-block fixture
    (`tests/test_check_window_provenance.py` `install_synthetic_finalization_fixture`
    + `_make_sliced_one_block_verdict`) the checker prints
    `PASS FINALIZE-REFUSAL observed={analysis_finalization_member_cover_mismatch}`
    with the floor valid, absent, `{}`, the `floors/` directory removed, and
    the floor path a symlink to `/etc/hosts`. The observed singleton is
    invariant under floor state.
F4. Nothing else on the G2-b night consumes the floor: repo-wide
    `aggregate_floor` hits are `analysis_manifest_v3.py`,
    `scripts/finalize_analysis_manifest.py`, the F2 leg of
    `check_window_provenance.py` (`:453,486,513,528`, all inside
    `_run_expect_refusal`), and `joulewise/analysis_engine/inputs.py`
    (`:828,1216,3078` — the claim gate over a FINALIZED manifest, which G2-b by
    construction never produces). `joulewise/arm_readiness.py` and
    `scripts/run_campaign.py` have zero hits.
F5. Physical order: `docs/process/v5-artifact-flow.md:13-15` — floor
    extraction over `$PRODUCER_RUNS_ROOT` → mint emitting the aggregate floor →
    finalization. The producer corpus is the transaction's ALPHA/BETA arms,
    and `V5-TRANSACTION-01` hard-depends on `L10-A-G2B-CONTRACT-PREFIX-01`,
    which hard-depends on `V5-G2B-SHAKEDOWN-01` (kernel). The `_v5` aggregate
    floor therefore cannot exist before G2-b. B-SUPPLY is the wrong one.
F6. Pack ids: `configs/campaigns/d117_contrast_v5/generate_configs.py:1123`
    composes `f"d117_floor_{MODEL_IDS[arm]}_v5"` from the panel ids
    `qwen3-1p7b` / `qwen3-8b` (`configs/model_panels/qwen3_4bit.json:5,38`).
    The runsheet's `:179-180` underscore spellings are errata.
F7. At this head the registry roster is still the `_v4` Qwen2.5 trio
    (`configs/arm_readiness/d117_row_registry_v2.json:532-536`) and
    `joulewise/arm_readiness.py:302-307` `_SUCCESSOR_PROFILE_PATTERNS` are
    Qwen2.5/underscore-only regexes that forbid hyphens. Ruling 89's phrase
    "registry roster" described the `_v4` roster; the `_v5` roster lands with
    `V5-IDENTITY-REPARAM-01` (session S0-A, in flight), whose scout (trace 84)
    did NOT inventory `:302-307`.

## Ruling

R-6a. **Struck.** The aggregate-floor clause of B-SUPPLY is removed for G2-b and
      for L10-A. No floor bytes are staged: `$CUSTODY_ROOT/floors/` is created
      EMPTY; the F2 command keeps
      `--aggregate-floor-artifact "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json"`
      as a path that lies under custody and does not exist. Wording: the path
      is *never reached* (F1) — it does not "satisfy" any check. An absent
      floor is a second, independent guarantee that no finalized manifest can
      be produced from the G2-b root; the immutability fence ("never consumed
      by a floor, mint, or claim") and the anti-substitution sentence
      (runsheet `:70-72`) stay verbatim. A sentinel file is REJECTED: it would
      be substitute bytes at the exact real-mint filename, which is what the
      fence forbids.
      The strike is surgical: B-SUPPLY's remaining demands — all three real
      `_v5` packs and their freeze/mint supply — survive (they are produced by
      `V5-DESK-DAY-01`).
R-6b. **Pack ids.** The generator's hyphenated form is canonical:
      `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`,
      `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`. The runsheet's `:179-180`
      are errata. Because of F7, the registry roster AND
      `_SUCCESSOR_PROFILE_PATTERNS` (`arm_readiness.py:302-307`) must be
      retargeted to these ids in `V5-IDENTITY-REPARAM-01`; the S0-A harvest
      check adds "`:302-307` patterns match the three ids; a positive
      coherent-roster test passes through `arm_readiness`'s production gate."
R-6c. F2's PASS line carries no information about the floor (F3). The
      runsheet therefore adds post-assertions, before AND after F2:
      `test ! -e "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json"` and
      `$CUSTODY_ROOT/floors/` empty. These, not the PASS line, are the
      transcript's proof that no floor bytes were staged. A non-default
      observed singleton stops the run (checker exits nonzero, `:538-545`);
      `analysis_finalization_attachment_missing` observed on the night is a
      STOP and a ruling, never a "stage a floor and rerun" — that would be the
      substitution the fence forbids.
R-6d. **Runsheet edits owed** (runbook stream, docs lane; the runsheet is a
      process trace, so the edit is a dated amendment block plus the
      corrected commands, never a rewrite of history): delete `:212`
      (`export AGGREGATE_FLOOR_ARTIFACT='NEEDS-RULING'`; the F2 command
      already uses the custody path); strike `:550` `test -f`, `:591` `cp -p`,
      `:593` `cmp -s`; `:149` tree comment becomes "empty by ruling 97; no
      floor bytes are staged for G2-b"; `:117-121` "Remaining ruling" closes
      citing this file; `:179-180` spellings corrected.
R-6e. **Ordering regression** (code lane, small): no test pins "member cover
      before floor read". Add to `tests/test_check_window_provenance.py`
      `test_sliced_verdict_one_block_default_refusal_and_mismatches` a leg
      that unlinks `fixture["floor_path"]` and asserts exit 0 with the
      member-cover singleton; and a direct-finalizer twin in
      `tests/test_analysis_finalizer.py` (sliced verdict, floor unlinked,
      `AnalysisManifestFinalizationError.reason_code ==
      "analysis_finalization_member_cover_mismatch"`). Counterfactual: a
      refactor that moves the floor read above `_verify_basis_members` fails
      both by name. Production call site: `_authenticate_finalization_inputs`.
R-6f. L10-B (ruling 89) explicitly inherits the floor's containment/symlink
      leg (`:1491-1507`), which G2-b/L10-A leave unexercised.
R-6g. Errata to the consult packet, recorded so the ruling's own citations are
      right: floor first opened at `:3575-3577` (not `:3464`);
      `docs/process/real-transaction-runbook.md` does not exist — the
      authority is `v5-artifact-flow.md:13-15`; the registry holds `_v4` ids.

R-6h. **Erratum 2 to ruling 89** (Sol seat F1, verified): ruling 89 `:47-49`
      says a refusal at the member-cover gate "has passed every custody,
      frozen-semantics, verdict-basis, bracket-byte and ledger-head check
      before it". False for the last two: `_verify_basis_members` runs at
      `:3373`, bracket authentication starts at `:3380` and ledger/head
      authentication at `:3416` — both AFTER member cover. What the L10-A
      singleton proves is: prospective-manifest validation (`:3840-3853`),
      verdict schema/status/basis (`:3355-3372`), and the present members'
      config/metadata/summary hashes and identity paths (`:2990-3048`). The
      finalizer's bracket and ledger legs (`:3380-3487`) are first exercised
      on real bytes in L10-C. On the G2-b night those same objects are still
      validated on real bytes by the E1 provenance run
      (`check_window_provenance.py --bracket-binding … --calibration-ledger …
      --head-pin …`, runsheet `:1244-1254`, production loaders at `:322,854`)
      — outside the finalizer. The L10 doc (PR #259, luna round 2 in flight
      under a brief that repeats the ruling-89 sentence) must state exactly
      this scope; the magistrate corrects it at harvest or in the delta
      re-audit fix round. Neither wording change alters the L10-A acceptance
      (kernel `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/acceptance`).

## Seat record

| Seat | Verdict | Unique catches |
|---|---|---|
| Sol xhigh (`out/97-sol-r6-consult.md`) | AGREE a/b/c, narrower wording | R-6h (ruling-89 proof-scope erratum); "this invocation cannot write" not "can never be written" |
| Opus 5 contract lens | AGREE a/b/c | M-1 `_SUCCESSOR_PROFILE_PATTERNS` (R-6b second half); M-2..M-5 runsheet strike list (R-6d); `:3464` and runbook-path errata (R-6g) |
| Blind Fable | AGREE a/b/c+amendment | ordering regression (R-6e); pre/post emptiness assertions (R-6c); symlink probe state; L10-B containment inheritance (R-6f) |

## Kernel effects (bench)

- `V5-G2B-SHAKEDOWN-01.status_note`: NEEDS-RULING → "RULED 97 (R-6a..g)";
  fences unchanged.
- `L10-A-G2B-CONTRACT-PREFIX-01.status_note`: floor absent by ruling 97;
  post-assertions R-6c part of the PASS record.
- `V5-IDENTITY-REPARAM-01` (to be added at S0-A harvest): acceptance gains
  R-6b's pattern check.
- New small row `G2B-FLOOR-ORDER-REGRESSION-01` (R-6e) or fold into the
  runbook-stream PR; magistrate's choice at harvest.
