# Estate 12 delta template — symbol-pinned `_v5` clone proof

Status: **TEMPLATE; not authority to run a quiet-machine measurement.** This is
the estate-12 procedure delta over the S-0 procedure in
`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`, the completed estate-10
record, and the real-transaction runbook. It replaces estate 11's frozen line
coordinates. It does not rewrite those historical records.

Authority, in order:

1. `MAGISTRATE-DISPOSITION.md` R-1 through R-3;
2. `070-HALT-RECORD.md` and `001-STEP-INDEX.md`;
3. `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`,
   especially G2-a, Desk day, and G2-b;
4. `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`; and
5. S-0 plus `docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md`.

Everything not changed below remains inherited. A conflict or an unresolved
parameter is a HALT, never permission to recover an old `_v4` literal or infer
an answer from a nearby path.

## 0. Estate invariants

- Estate 12 is a throwaway, commit-exact, full clone. No shallow clone, shared
  worktree, dirty source checkout, or later moving branch is an estate.
- The cut is one named full Git object ID, `BASE`, whose completed successful CI
  run is recorded by provider, run ID, conclusion, and completion time. `BASE`
  must contain the merged `_v5` generator and the reviewed pinset lane.
- Anchors are derived **at the cut** from the embedded spec in
  `scripts/derive_estate_anchors.py`. Line numbers are evidence outputs. They
  are never copied back into the specification.
- Any missing or ambiguous symbol/content pin is the R-2 halt condition. Do not
  substitute text search, the nearest similarly named symbol, or a prior map.
- Pack generation is desk work and happens only after the G2-a selection and
  prompt pin are reviewed. No live G2-a or G2-b step runs while an agent session
  is active.
- The anchor map is a drift tripwire, not an integrity control. Integrity still
  comes from the named green commit, committed blob digests, custody-tool
  authentication, and the transaction's own receipts.

## 1. Parameters and their only resolution sources

Every estate instantiation starts by copying this table into its custody record
and filling the Value column from the named source. `TBD`, an empty value, or a
value obtained from a different source halts the estate.

| Parameter | Value at this cut | Resolution source |
|---|---|---|
| `SOURCE_REPOSITORY` | parameter | Repository URL/path recorded by the cut operator; clone uses `--no-local` and no depth limit. |
| `BASE` | parameter | Newest named head selected by the lead with completed/successful CI after all required `_v5` and pinset-lane merges. Record the CI run beside it. |
| `ESTATE_ROOT` / `CLONE` / `CUSTODY` | parameter | Fresh estate-12 custody allocation; `CLONE=$ESTATE_ROOT/repo`, `CUSTODY=$ESTATE_ROOT/custody`. |
| `G2A_SELECTION_RECORD` | parameter | `SHAKEDOWN-G2-RUNSHEET.md` Desk-day command output `d166-prefill-selection.json`. |
| `G2A_SELECTION_RECORD_SHA256` | parameter | SHA-256 recomputed from the exact reviewed selection-record bytes; it must equal the custodied `.sha256`. |
| `PREFILL_LENGTH` | parameter | `.collection_prefill_tokens` in the reviewed selection record. This is also the selected value on PASS and is 4096 on the ruled no-clear branch. |
| `PREFILL_PROMPT_PIN` | parameter | Reviewed `joulewise.prefill_prompt_pin.v2` artifact for `PREFILL_LENGTH`; its `g2a_record_sha256` must equal `G2A_SELECTION_RECORD_SHA256`. There is currently no authority to invent its path or bytes. |
| `GAMMA_PACK_ROOT` | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` after generation | The merged generator's configured `PACK_REL`, then the generated `plan_tree.json` and `analysis_manifest_v3.json`; all three must agree. |
| `ALPHA_PACK_ROOT`, `BETA_PACK_ROOT` | parameter | The two producer plan references emitted by the generated gamma `plan_tree.json`, resolved under the clone. Their materialization command comes from the reviewed producer-pack generation record; the gamma generator does not supply that command. |
| `PACK_ROOTS` | parameter | Ordered `[GAMMA_PACK_ROOT, ALPHA_PACK_ROOT, BETA_PACK_ROOT]` after all three exist and authenticate. |
| `PREDECESSOR_ROOT[pack]` | parameter | Each pack's reviewed generation/predecessor declaration and readiness registry. Never derive it by changing `_v5` to another suffix. |
| `SUCCESSOR_PINSET` | parameter | Output path declared by the reviewed successor-pinset mint command for these exact three pack IDs. Do not reuse the historical `_v4` filename by analogy. |
| `AGGREGATE_FLOOR_ARTIFACT` | parameter | Exact aggregate-floor path emitted by the real `_v5` mint and authenticated by the generated analysis/finalization supply. This is also the G2 runsheet's remaining ruling; no placeholder is executable. |
| `EXPECTED_CONFIRMATION_DIGEST` | parameter | Real estate-12 step-6 out-of-band `hC`, carried as a frozen input into G2-b; never recomputed from the confirmation-table bytes. |

The producer roots, successor-pinset path, aggregate-floor path, and `hC` are
deliberately parameterized. If their named records do not yet exist, the
estate records the missing input and stops at that boundary.

## 2. Cut and derive the anchor map

Run in a new empty `ESTATE_ROOT`. The clone is full and isolated; no command in
this block writes the source repository.

```zsh
set -euo pipefail
export PY=/Users/edr/code/JouleWise/.venv/bin/python
export ESTATE_ROOT=<fresh-estate-12-root>
export CLONE="$ESTATE_ROOT/repo"
export CUSTODY="$ESTATE_ROOT/custody"
export SOURCE_REPOSITORY=<recorded-source>
export BASE=<full-green-object-id>

test ! -e "$CLONE"
/bin/mkdir -p "$ESTATE_ROOT" "$CUSTODY/transcripts"
git clone --no-local "$SOURCE_REPOSITORY" "$CLONE"
git -C "$CLONE" checkout --detach "$BASE"
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BASE"
test -z "$(git -C "$CLONE" status --porcelain --untracked-files=all)"
git -C "$CLONE" show -s --format='%H%n%T%n%cI%n%s' HEAD \
  > "$CUSTODY/transcripts/001-base.txt"
```

Record the successful CI selection evidence as
`002-base-ci-authority.json`. It must name this exact `BASE`, not only a branch.
Then derive and custody the map before any pack generation or S-0 mutation:

```zsh
"$PY" "$CLONE/scripts/derive_estate_anchors.py" "$CLONE" \
  --output "$CUSTODY/estate-12-anchor-map.json"
"$PY" "$CLONE/scripts/derive_estate_anchors.py" "$CLONE" \
  --print-embedded-spec > "$CUSTODY/estate-12-anchor-spec.json"
/usr/bin/shasum -a 256 \
  "$CLONE/scripts/derive_estate_anchors.py" \
  "$CUSTODY/estate-12-anchor-spec.json" \
  "$CUSTODY/estate-12-anchor-map.json" \
  > "$CUSTODY/transcripts/003-anchor-custody.sha256"
"$PY" - "$CUSTODY/estate-12-anchor-map.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
assert value["schema_version"] == "joulewise.estate_anchor_map.v1", value
assert value["anchor_count"] == len(value["anchors"]), value
assert len([key for key in value["anchors"] if key.startswith("legacy.")]) == 15
assert value["anchors"]["legacy.14"]["symbol_or_content_pin"].endswith(
    "test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane"
)
PY
```

Exit 2 with `anchor_symbol_missing`, `anchor_symbol_ambiguous`,
`anchor_content_missing`, or `anchor_content_ambiguous` is **HALT — PROCEDURE
DRIFT**. Preserve stderr and the unmodified spec. A resolver or spec change goes
through ordinary review and requires a fresh estate.

The embedded inventory contains the historical 15 anchors, #14 under its ruled
new name, AST-derived immutable-audit ranges (including W-10), exact
`PINSET`/`PINSET_SHA256` citations, and the `_v5` dominance, prefill refusal,
MLX identity-pin, reviewed pinset-lane, and G2-a selection surfaces.

## 3. Estate-11 corrections carried forward

### 3.1 S3 D6 is a supersession record

Before executing a custody tool, recompute all four tool digests and compare
each with its tracked GNU `.sha256` sidecar:

- `scripts/build_family_marker.py`;
- `scripts/verify_family_marker.py`;
- `scripts/build_v4_histsem_pinset.py`; and
- `scripts/verify_receipt_histsem.py`.

Custody the exact values at `BASE`. Estate 11's
`040-s3d6-tool-digest-repin.txt` supersedes S-1 `MANIFEST.md` §6; the historical
manifest remains immutable. Estate 12 appends a new cut-specific supersession
record and never edits either older record. A byte/sidecar mismatch halts before
the tool runs.

### 3.2 ED-STEP convention

Number every user-hands action in execution order as `ED-STEP-001`,
`ED-STEP-002`, and so on. For each, record preconditions, the exact command or
question shown, Ed's answer/action, exit status, and resulting artifact hashes.
Permission prompts are approved only when reached; no earlier statement stands
in for the live prompt.

If the estate halts before an Ed step, record one `ED-STEP-SKIPPED` row naming
the unreached step and the prior halt. If no Ed step was scheduled before the
halt, record `ED-STEP-SKIPPED: none; first Ed step not reached`, as estate 11
did. A skipped or declined step is never silently converted to PASS.

## 4. G2-a pin gate — generation cannot precede it

This is desk work after G2-a. First authenticate the record and select only its
ruled collection coordinate:

```zsh
test -f "$G2A_SELECTION_RECORD"
test -f "$G2A_SELECTION_RECORD.sha256"
test "$(/usr/bin/shasum -a 256 "$G2A_SELECTION_RECORD" | /usr/bin/awk '{print $1}')" = \
  "$(/usr/bin/awk '{print $1}' "$G2A_SELECTION_RECORD.sha256")"
export G2A_SELECTION_RECORD_SHA256="$(/usr/bin/shasum -a 256 \
  "$G2A_SELECTION_RECORD" | /usr/bin/awk '{print $1}')"
export PREFILL_LENGTH="$(/usr/bin/jq -er '.collection_prefill_tokens' \
  "$G2A_SELECTION_RECORD")"
/usr/bin/jq -e '
  (.status == "selected" and
   .selected_prefill_tokens == .collection_prefill_tokens)
  or
  (.status == "refused" and .selected_prefill_tokens == null and
   .collection_prefill_tokens == 4096 and
   .refusal.fallback_action == "collect_at_4096")
' "$G2A_SELECTION_RECORD"
/usr/bin/jq -e --arg sha "$G2A_SELECTION_RECORD_SHA256" \
  --argjson length "$PREFILL_LENGTH" '
    .schema_version == "joulewise.prefill_prompt_pin.v2" and
    .g2a_record_sha256 == $sha and .prefill_length == $length and
    .prompt_tokens == $length
  ' "$PREFILL_PROMPT_PIN"
```

Absent/malformed records, a hash mismatch, a prompt-pin mismatch, or any
unresolved marker halt before generator invocation. No default prefill length
and no placeholder record hash is permitted.

## 5. Prove the merged generator into the real pack location

Run the merged generator itself, with no temporary `--output-root`, so its
production output is the real repository location. The generator stages bytes
internally before publishing them.

```zsh
cd "$CLONE"
"$PY" configs/campaigns/d117_contrast_v5/generate_configs.py \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PREFILL_LENGTH" \
  --prefill-prompt-pin "$PREFILL_PROMPT_PIN" \
  > "$CUSTODY/transcripts/010-v5-generate.txt"
test -d "$GAMMA_PACK_ROOT"
"$PY" configs/campaigns/d117_contrast_v5/generate_configs.py \
  --check \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PREFILL_LENGTH" \
  --prefill-prompt-pin "$PREFILL_PROMPT_PIN" \
  > "$CUSTODY/transcripts/011-v5-check.txt"
```

Authenticate the generated `plan_tree.json`, analysis manifest, four stage
manifests, four condition-family files, 80 member configs, the exact model-pin
pair on every member, the two dominance registrations, and
`frozen_semantics_sha256`. Resolve `ALPHA_PACK_ROOT` and `BETA_PACK_ROOT` from
the producer references in those authenticated bytes. Do not edit a generated
path or manufacture the two producers from the gamma naming pattern.

Estate 12 may proceed only after the reviewed producer procedure has
materialized both producer roots at those exact references. Require all three
pack generators/checkers to reproduce the bytes in their real locations and
custody their commands and hashes. If no reviewed producer procedure exists,
record that missing resolution source and halt here.

Commit the generated roots in the estate clone before the S-0 mutation band;
record that commit as `PACK_GENERATION_HEAD`. This is estate evidence only and
is never pushed from the throwaway clone.

## 6. Freeze/mint band — S-0 with `_v5` substitutions

Run the S-0 §§1.2–5 and real-runbook C2–C10 mechanics with `PACK_ROOTS` and
`PREDECESSOR_ROOT[pack]` from §1. The following changes are mandatory:

1. Candidate-manifest and immutable-audit evidence consume the custodied
   symbol-derived map. They never contain copied source line numbers.
2. The pre-author suite is exactly
   `tests.test_arm_readiness_schemas`, `tests.test_receipt_histsem`, and
   `tests.test_mint_analysis_admission`, plus the `_v5` pack tests required by
   the generated manifest-surface adjacency policy.
3. U11 projects each of the three real packs in the measurement-capable estate
   environment, one pack per `freeze -> assert -> commit` unit. These are live
   Ed prompts and use the resolved pack roots verbatim.
4. Author all generic readiness evidence at one common derivation head with
   `--measurement-checkout "$CLONE"`; custody the exact emitted freeze commands.
5. The sacrificial screen uses a fresh full throwaway clone and declares that
   clone as `--measurement-checkout`. All three screens must PASS before any
   primary create-only slot is touched.
6. Primary readiness freeze uses each exact resolved pack/predecessor pair and
   the estate clone's absolute `--measurement-checkout`. Assert PASS, mutation,
   empty reasons, receipt sidecar, and plan-tree pin for every pack.
7. On any primary refusal, decide recoverability only by the filesystem:
   `PACK_ROOT/arm_readiness.freeze.receipts/freeze-0004.json` absent means the
   slot is untouched; present means it is spent and this estate is terminal.
   Do not maintain a refusal-code catalogue.
8. Authenticate all four executing custody tools against the candidate
   manifest and their tracked sidecars. Mint the successor pinset only with the
   reviewed builder command and resolved `SUCCESSOR_PINSET` path.
9. The reviewed refresh lane is the only permitted way to update existing
   pinset current-side fields or custody-tool sidecars:
   `scripts/refresh_receipt_histsem_pinset.py --refresh-row <exact-pack-id>`
   and, when ruled, `--refresh-tool-sidecars`. Preserve its printed diff,
   publication checks, pre/post whole-pinset verification, and ordinary review
   boundary. It never hand-adds a successor row and never changes historical
   fields.
10. Build and verify the family marker, obtain the live step-6 `hC`, arm all
    three packs, run the local-green and probe batteries, and preserve the
    fixation record exactly as S-0 requires. Record every Ed interaction under
    §3.2's convention.

The band ends only when all three packs have green freeze/arm receipts, the
successor pinset verifies with `--require-published`, marker/confirmation
custody is complete, the probe battery is green, and pack regeneration remains
byte-identical. A partial band is not a partial PASS.

## 7. G2-b handoff

Estate 12 does not execute G2-b. It emits one handoff record containing:

- `BASE`, `PACK_GENERATION_HEAD`, evidence/freeze/pinset/marker heads, and the
  custodied anchor-map/spec hashes;
- exact `PACK_ROOT`, `ALPHA_PACK_ROOT`, `BETA_PACK_ROOT`, and predecessor roots;
- `PREFILL_LENGTH`, selection-record path/hash, and prompt-pin path/hash;
- exact aggregate-floor path/hash from the real mint;
- publication marker, table, sidecars, and out-of-band `hC`;
- the clean reviewed head G2-b must use and proof that no G2-b T-0 receipt
  predates it; and
- PASS/REFUSE plus transcript paths for generator check, U11, authoring,
  sacrificial screens, primary freezes, successor-pinset verification, marker,
  arm, probes, fixation, and all ED-STEP rows.

The receiving procedure is
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` at
"G2-b — evening before the transaction." Resolve its `PACK_ROOT`, floor pack
roots, `AGGREGATE_FLOOR_ARTIFACT`, and `EXPECTED_CONFIRMATION_DIGEST` only from
this handoff. Preserve G2-b's own B10 physical-ledger gate, fresh T-0,
ARM-ABORT expiry, one-block boundary, post-bracket physical-ahead stop, reviewed
head-pin refresh, re-freeze/re-attestation, binding-before-verdict order, and
exact finalizer refusal. Estate PASS is supply for G2-b; it is not G2-b PASS and
is not measurement evidence.

## 8. Terminal record

The estate terminal record states exactly one of:

- `PASS`: every §6 condition and the §7 handoff are complete;
- `HALT-PROCEDURE-DRIFT`: an anchor/spec or inherited-procedure surface no
  longer resolves;
- `HALT-MISSING-RESOLUTION-SOURCE`: a parameterized producer, pinset, aggregate
  floor, or confirmation input has no reviewed source;
- `HALT-INSTRUMENT`: a named S-0 mechanism check refused; or
- `HALT-ED`: a required Ed action was declined or unavailable.

It also lists reached and skipped ED steps, every commit object, every immutable
custody artifact with SHA-256, and confirms that nothing was pushed and no
quiet-machine G2 step ran from the estate session.
