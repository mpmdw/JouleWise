# S-0 CLONE-PROOF RUNSHEET — JouleWise `_v4` transaction

Assembly target: repository commit `1ba04a83b6dacc2ea904c7936901922857ac89d4` (`1ba04a8`). This is a bench runsheet, not an execution transcript. The magistrate executes it, lead-executed, in the throwaway clone below and reads every transcript. It never uses or reads `/Users/edr/JouleWise-measurement-20260818`.

Lead ruling records Ed’s mint license as granted, so license is not an S-0 blocker. Execution still stops at the explicit custody/ruling boundaries in §§1.3, 3.7, and 3.8.

Binding-source shorthand used below:

- **R4** = `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`, cited by `r4-N`.
- **R5** = `docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md`, cited by `S-N`, `V-1.i`–`V-1.vii`, or `V-2`.
- **RH-8** = `docs/process_traces/2026-08-20-go-session/rh-ruling.md`, item 8 and its normative annexes `rh-terra-debate.md` and `rh-opus-debate.md`.
- **SIT-C3** = `docs/process_traces/2026-08-20-go-session/ready-sitting-ruling.md`, C-3, with `readiness-sitting/seat-L5.md`, F2.
- **MARKER-A1** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md`, A-1.
- **HISTSEM-CONTRACT** = `docs/contracts/receipt_histsem_verifier.md`, especially “Pinset artifact and schema,” “Gate integration,” “Failure semantics,” and “`_v4` transaction sequencing.” Its rule-11 absence clarification supersedes the original library-absence wording without changing the explicit-CLI absence probe.

## Pinned mechanics map

All source anchors below were checked with `git show 1ba04a8:<path> | nl -ba`; they are not working-tree line numbers. The historical R4 labels `arm_readiness.py:3105-3113`, `:3212`, `:4143-4150`, and `:5344-5348` have drifted. At the pinned HEAD their actual sites are:

- changed-set enumeration: `joulewise/arm_readiness.py:3916-3964`; allowlist subtraction/refusal: `:4038-4049`;
- manifest binding half 1: `:4051-4067`; nonempty/canonical and derivation/current dependency half 2: `:4070-4126`;
- issued-acceptance census: `:4956-4982`; generic applicability derives from hard-coded acceptance plus registry rows in `joulewise/arm_readiness_evidence.py:1688-1710`;
- freeze semantic replay: `joulewise/arm_readiness.py:6161-6185`;
- freeze predecessor histsem gate: `:6255-6268`; replay: `:6284-6335`; new mint writes either PASS or REFUSE and pins it: `:6363-6442`;
- arm histsem gate: `:6943-6961`; governed arm receipt construction: `:6987-7135`;
- R1 `EvidenceLifecycleError` is a `ValueError`, not an `ArmReadinessError`: `:962-988`;
- generic output inventory rejection: `:5248-5265`;
- U11 writes projection receipt/sidecar and plan bytes: `joulewise/identity_pins.py:1826-1935`;
- generator preserve-mode echo hole: `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1942-1950`; CLI: `:2638-2681`;
- evidence author CLI and required successor freeze command: `scripts/author_arm_readiness_evidence.py:25-28,31-80`; the author derives the generic census at `joulewise/arm_readiness_evidence.py:1688-1710,2335-2567`;
- freeze/arm/verify CLI: `scripts/generate_arm_readiness.py:28-58,61-73,89-161`; identity U11 CLI: `scripts/project_identity_pins.py:23-60`; histsem CLI: `scripts/verify_receipt_histsem.py:22-73`;
- Python is `>=3.11`, core dependencies are empty: `pyproject.toml:5-14`;
- current byte pin is literal at `tests/test_receipt_histsem.py:30-31` and asserted with no update/reseal lane at `:53-60`; explicit absent pinset expects `histsem_pinset_absent` at `:62-80`.

Immediately after §1.1 has defined the paths and created the clone, and before doing any transaction work, preserve the immutable line audit:

```bash
for spec in \
  'joulewise/arm_readiness.py 962,988p;3916,3964p;4038,4127p;4956,4982p;5248,5265p;6161,6185p;6242,6443p;6943,7135p' \
  'joulewise/identity_pins.py 1826,1935p' \
  'joulewise/arm_readiness_evidence.py 1688,1710p;2335,2567p' \
  'scripts/generate_arm_readiness.py 28,73p;89,161p' \
  'scripts/project_identity_pins.py 23,60p' \
  'scripts/verify_receipt_histsem.py 22,73p' \
  'tests/test_receipt_histsem.py 30,80p' \
  'configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py 1942,1950p;2638,2681p'
do
  source_file=${spec%% *}; line_ranges=${spec#* }
  git -C "$CLONE" show "$BASE:$source_file" | nl -ba | sed -n "$line_ranges"
done > "$TRANS/000-pinned-line-audit.txt"
```

Authority: R4 r4-2 and the task’s immutable-HEAD verification requirement; R5 V-2.

# 1. CLONE SETUP

### 1.1 Create an empty proof estate and a commit-exact clone

Run in Bash. Refuse if a prior proof directory exists; do not reuse custody or receipts.

```bash
set -euo pipefail
SESSION=/private/tmp/claude-501/-Users-edr-code-JouleWise/b1bba5d6-4e1e-4264-aa06-4d6ed22e445c/scratchpad
SOURCE=/Users/edr/code/JouleWise
BASE=1ba04a83b6dacc2ea904c7936901922857ac89d4
PROOF="$SESSION/s0-clone-proof"
CLONE="$PROOF/repo"
CUSTODY="$PROOF/custody"
TRANS="$CUSTODY/transcripts"
CASES="$PROOF/cases"
INPUT="$PROOF/input"

test ! -e "$PROOF"
test "$(git -C "$SOURCE" rev-parse "$BASE^{commit}")" = "$BASE"
mkdir -p "$PROOF" "$CUSTODY" "$TRANS" "$CASES" "$INPUT"
git clone --no-local "$SOURCE" "$CLONE"
git -C "$CLONE" checkout --detach "$BASE"
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BASE"
test -z "$(git -C "$CLONE" status --porcelain=v1)"
git -C "$CLONE" switch -c s0-transaction
git -C "$CLONE" config user.name 'S-0 clone-proof magistrate'
git -C "$CLONE" config user.email 's0-clone-proof.invalid'
git -C "$CLONE" config gc.auto 0
git -C "$CLONE" config maintenance.auto false
git -C "$CLONE" update-ref refs/remotes/origin/main "$BASE"

python3 -c 'import sys; assert sys.version_info >= (3,11), sys.version'
python3 -m venv "$PROOF/venv"
PY="$PROOF/venv/bin/python"
"$PY" -c 'import sys; assert sys.version_info >= (3,11); print(sys.version)'
git -C "$CLONE" rev-parse HEAD > "$TRANS/001-base-head.txt"
git -C "$CLONE" status --porcelain=v1 > "$TRANS/002-base-status.txt"
```

No `pip install` is required: the core command surfaces are stdlib-only. Never install the `mac` extra and never run a dry-run, launch, measurement, or quiet-Mac command in S-0. Authority: R4 r4-2, r4-3, r4-7; R5 V-2; `pyproject.toml:5-14`.

### 1.2 Install transcript helpers

```bash
capture() {
  local label=$1; shift
  set +e
  "$@" >"$TRANS/$label.stdout.json" 2>"$TRANS/$label.stderr.txt"
  local rc=$?
  set -e
  printf '%s\n' "$rc" >"$TRANS/$label.rc"
}
expect_rc() {
  local label=$1 expected=$2
  test "$(cat "$TRANS/$label.rc")" = "$expected"
}
no_traceback() {
  local label=$1
  ! grep -Eq 'Traceback \(most recent call last\)|^[A-Za-z]+Error:' \
    "$TRANS/$label.stdout.json" "$TRANS/$label.stderr.txt"
}
commit_case() {
  local repo=$1 message=$2
  git -C "$repo" add -A
  git -C "$repo" commit -m "$message"
  git -C "$repo" update-ref refs/remotes/origin/main "$(git -C "$repo" rev-parse HEAD)"
}
new_case() {
  local name=$1 commit=$2 target="$CASES/$name"
  test ! -e "$target"
  git clone --no-local "$CLONE" "$target" >/dev/null
  git -C "$target" checkout --detach "$commit" >/dev/null
  git -C "$target" config user.name 'S-0 probe'
  git -C "$target" config user.email 's0-probe.invalid'
  git -C "$target" update-ref refs/remotes/origin/main "$commit"
  printf '%s\n' "$target"
}
```

Authority: R4 r4-2 (full transcript); R5 V-2 (magistrate reads every transcript).

### 1.3 Required reviewed candidate inputs — hard precondition

Pinned HEAD contains neither the three `_v4` roots nor a resolved R1 candidate registry. Place these lead-reviewed custody inputs in `$INPUT` before proceeding:

1. `s0-candidate.patch` and GNU sidecar `s0-candidate.patch.sha256`, implementing the ruled R1 registry, r4-5’s two `EvidenceLifecycleError` fail-closed catches, the `_v4` generator/consumer changes, S-6 test surfaces, and the selected marker consumer/token branch—but **not** generated `_v4` pack outputs.
2. `s0-candidate-manifest.json`, binding the patch SHA, exact changed paths, test commands, R1 refusal vocabulary, and marker branch.
3. `build_v4_histsem_pinset.py` and sidecar: a reviewed, deterministic custody tool whose CLI is exactly the one in §3.7 and which constructs rows from Git objects and newly minted receipts without network access.
4. For marker option (a), `build_family_marker.py`, `verify_family_marker.py`, and sidecars; for option (b), `verify_family_marker.py` and sidecar. Their exact bytes and selected branch must be named by the candidate manifest.

```bash
cd "$INPUT"
shasum -a 256 -c s0-candidate.patch.sha256
shasum -a 256 -c build_v4_histsem_pinset.py.sha256
test -f verify_family_marker.py
shasum -a 256 -c verify_family_marker.py.sha256
MARKER_BRANCH=$("$PY" -c 'import json; d=json.load(open("s0-candidate-manifest.json")); assert d["marker_branch"] in {"BUILD-AT-BOUNDARY","UNBUILT.v0"}; print(d["marker_branch"])')
if test "$MARKER_BRANCH" = BUILD-AT-BOUNDARY; then
  test -f build_family_marker.py
  shasum -a 256 -c build_family_marker.py.sha256
fi
cd "$CLONE"
git apply --check "$INPUT/s0-candidate.patch"
git apply "$INPUT/s0-candidate.patch"
"$PY" -m json.tool "$INPUT/s0-candidate-manifest.json" >/dev/null
git diff --binary "$BASE" > "$TRANS/003-applied-candidate.diff"
shasum -a 256 "$INPUT/s0-candidate.patch" \
  "$INPUT/s0-candidate-manifest.json" \
  "$INPUT/build_v4_histsem_pinset.py" \
  "$INPUT/verify_family_marker.py" > "$TRANS/004-input-sha256.txt"
```

If any input is absent, mismatched, contains `ED_RESERVED:`, or its manifest and patch disagree, stop: this is missing custody, not authority to improvise mechanism. Authority: R4 r4-5, r4-7; R5 S-6, V-1, V-2.

# 2. ALLOWLIST GENERATION

### 2.1 Generate, never hand-type, the base 112-path contract

Install this custody-only checker. It generates 37 exact paths per pack: 11 source JSONs, 11 evidence JSONs, 11 evidence sidecars, `freeze-0004.json` plus sidecar, and `plan_tree.json` plus sidecar. The RH pinset is the 112th path. Projection receipts, `producer_contract.json`, and identity-projection paths are intentionally absent because U11 precedes derivation.

```bash
mkdir -p "$CUSTODY/tools"
cat > "$CUSTODY/tools/s0_allowlist_contract.py" <<'PY'
#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, sys

ROOTS = (
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4",
 "configs/campaigns/d117_floor_qwen25_1p5b_v4",
 "configs/campaigns/d117_floor_qwen25_7b_v4",
)
SLUGS = (
 "acceptance-owner", "doctrine-pin", "estimator-identity", "mint-trust",
 "multicell-mint", "pack-authentication", "pack-family",
 "reason-code-coverage", "receipt-oracle", "recovery-ledger-test",
 "three-window-regression",
)
PINSET = "configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"

def expected():
    paths=[]
    for root in ROOTS:
        paths += [f"{root}/arm_readiness.sources/{s}.json" for s in SLUGS]
        paths += [f"{root}/arm_readiness.evidence/evidence-{s}.json" for s in SLUGS]
        paths += [f"{root}/arm_readiness.evidence/evidence-{s}.json.sha256" for s in SLUGS]
        paths += [f"{root}/arm_readiness.freeze.receipts/freeze-0004.json"]
        paths += [f"{root}/arm_readiness.freeze.receipts/freeze-0004.json.sha256"]
        paths += [f"{root}/plan_tree.json", f"{root}/plan_tree.sha256"]
    paths.append(PINSET)
    return sorted(paths)

ap=argparse.ArgumentParser()
ap.add_argument("--registry", type=pathlib.Path, required=True)
ap.add_argument("--repo", type=pathlib.Path)
ap.add_argument("--derivation")
ap.add_argument("--head", default="HEAD")
ap.add_argument("--candidate-list", type=pathlib.Path)
ap.add_argument("--observed-list", type=pathlib.Path)
ap.add_argument("--shape-only", action="store_true")
a=ap.parse_args()
reg=json.loads(a.registry.read_text())
life=reg["freeze_evidence_lifecycle"]
candidate=(json.loads(a.candidate_list.read_text()) if a.candidate_list else
           life["irrelevant_path_allowlist"])
exp=expected()
bad_forbidden=[p for p in candidate if "identity_pin_projection" in p or p.endswith("/producer_contract.json")]
result={"status":"PASS", "expected_count":len(exp), "candidate_count":len(candidate),
 "candidate_missing":sorted(set(exp)-set(candidate)),
 "candidate_extra":sorted(set(candidate)-set(exp)),
 "candidate_not_sorted_unique":candidate != sorted(set(candidate)),
 "forbidden":bad_forbidden}
if not a.shape_only:
    if a.observed_list:
        observed=json.loads(a.observed_list.read_text())
    else:
        if not a.repo or not a.derivation: ap.error("full check needs --repo and --derivation")
        raw=subprocess.check_output(["git","-C",str(a.repo),"diff","--name-only","-z",f"{a.derivation}..{a.head}","--"])
        observed=sorted(x for x in raw.decode().split("\0") if x)
    result.update({"observed_count":len(observed),
      "unused_allowlist":sorted(set(candidate)-set(observed)),
      "changed_not_allowlisted":sorted(set(observed)-set(candidate)),
      "observed_missing_from_literal":sorted(set(exp)-set(observed)),
      "observed_extra_to_literal":sorted(set(observed)-set(exp))})
ok=all(not v for k,v in result.items() if k not in {"status","expected_count","candidate_count","observed_count"})
ok &= len(exp)==112 and len(candidate)==112
result["status"]="PASS" if ok else "REFUSE"
print(json.dumps(result, indent=2, sort_keys=True))
sys.exit(0 if ok else 2)
PY
chmod 0555 "$CUSTODY/tools/s0_allowlist_contract.py"

REGISTRY="$CLONE/configs/arm_readiness/d117_row_registry_v1.json"
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --shape-only | tee "$TRANS/010-allowlist-shape.json"
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_count"])' "$TRANS/010-allowlist-shape.json")" = 112
```

The arithmetic is `3 × (11 + 11 + 11 + 1 + 1 + 1 + 1) + 1 = 3 × 37 + 1 = 112`. This reconciles R5 V-1’s literal 111 with RH-8’s COLD-PASS amendment: V-1 supplies the three 37-path packs (111), RH-8 adds exactly `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json` (112). It remains pack-and-ordinal exact (`freeze-0004`, not a glob). R4 r4-1’s conditional two tracked marker paths are addressed in §3.8: the **base** contract is 112; a tracked option-(a) marker would make 114 and needs an explicit Ed amendment. Authority: R4 r4-1; R5 V-1.i, V-1.ii, V-1.v; RH-8.

### 2.2 Applicability census

After each evidence-author command in §3.4, assert the exact eleven generic kinds:

```bash
cat > "$CUSTODY/tools/check_census.py" <<'PY'
import json,sys
want=sorted(["ACCEPTANCE_OWNER","DOCTRINE_PIN","ESTIMATOR_IDENTITY","MINT_TRUST",
 "MULTICELL_MINT","PACK_AUTHENTICATION","PACK_FAMILY","REASON_CODE_COVERAGE",
 "RECEIPT_ORACLE","RECOVERY_LEDGER_TEST","THREE_WINDOW_REGRESSION"])
for p in sys.argv[1:]:
 d=json.load(open(p)); assert d["status"]=="PASS" and d["mutated"] is True
 assert sorted(d["authored_kinds"])==want, (p,d.get("authored_kinds"))
print(json.dumps({"status":"PASS","packs":len(sys.argv)-1,"generic_kinds":want}))
PY
```

Any future issued-acceptance corpus growth must mechanically change the census to 12 slugs per pack and the contract to 120 paths; no operator may preserve 112 by prose. Authority: R5 V-1.ii; `arm_readiness.py:4956-4982`; `arm_readiness_evidence.py:1688-1710`.

# 3. FULL THREE-PACK TRANSACTION

Use these arrays throughout:

```bash
cd "$CLONE"
PACKS=(
  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
  configs/campaigns/d117_floor_qwen25_1p5b_v4
  configs/campaigns/d117_floor_qwen25_7b_v4
)
PREDS=(
  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
  configs/campaigns/d117_floor_qwen25_1p5b_v3
  configs/campaigns/d117_floor_qwen25_7b_v3
)
```

### 3.1 Materialize the `_v4` roots from the reviewed generators

```bash
"$PY" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/020-emit-contrast-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_1p5b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/021-emit-1p5b-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/022-emit-7b-v4.txt"
git add -A
git commit -m 'S-0 bootstrap reviewed candidate and generated v4 roots'
S0_BOOTSTRAP_HEAD=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$S0_BOOTSTRAP_HEAD"
```

Expected: each generator prints `generated <pack-id> ... 100 science configs` with plan hashes; no evidence or freeze-0004 output exists yet. Authority: R4 r4-3, r4-7; R5 V-1.i; generator CLI `:2638-2681`.

### 3.2 U11 on all three packs, before allowlist derivation

```bash
for i in 0 1 2; do
  label=$(basename "${PACKS[$i]}")
  capture "030-u11-$label" "$PY" scripts/project_identity_pins.py freeze "${PACKS[$i]}"
  expect_rc "030-u11-$label" 0
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True' \
    "$TRANS/030-u11-$label.stdout.json"
done
git add -- "${PACKS[@]}"
git commit -m 'S-0 U11 identity-pin projections for v4 packs'
EVIDENCE_DERIVATION_HEAD=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$EVIDENCE_DERIVATION_HEAD"
printf '%s\n' "$EVIDENCE_DERIVATION_HEAD" > "$TRANS/031-common-derivation-head.txt"
```

Expected: PASS, `mutated:true`, `projection-0001.json` and `.sha256`, and updated plan bytes in each pack. Those paths are before `EVIDENCE_DERIVATION_HEAD`, so they are correctly absent from the 112. Authority: R4 r4-1, r4-2, r4-3; R5 V-1.i; `identity_pins.py:1826-1935`.

### 3.3 Terminal common-head evidence

The reviewed candidate must bind the exact common HEAD/tree and contain no unresolved registry values. Run its manifest-declared terminal-review checks now; the transcript must show that all three packs use the one `EVIDENCE_DERIVATION_HEAD` and its tree OID. Do not create any commit between the three author commands.

```bash
git rev-parse HEAD HEAD^{tree} > "$TRANS/032-terminal-common-head.txt"
test "$(git rev-parse HEAD)" = "$EVIDENCE_DERIVATION_HEAD"
test -z "$(git status --porcelain=v1)"
"$PY" -m unittest -v \
  tests.test_arm_readiness_schemas \
  tests.test_receipt_histsem > "$TRANS/033-pre-author-tests.txt" 2>&1
```

The candidate manifest’s additional test commands are mandatory and are appended verbatim to `033-pre-author-tests.txt`; an undeclared substitution is a failed proof. Authority: R4 r4-3, r4-5; R5 V-1.iii, V-2.

### 3.4 Author all 33 generic receipts at the common head, then one evidence commit

```bash
author_logs=()
for i in 0 1 2; do
  label=$(basename "${PACKS[$i]}")
  capture "040-author-$label" "$PY" scripts/author_arm_readiness_evidence.py \
    --pack-root "${PACKS[$i]}"
  expect_rc "040-author-$label" 0
  no_traceback "040-author-$label"
  author_logs+=("$TRANS/040-author-$label.stdout.json")
done
"$PY" "$CUSTODY/tools/check_census.py" "${author_logs[@]}" \
  > "$TRANS/041-applicability-census.json"
git add -- "${PACKS[@]}"
git commit -m 'S-0 common-head R1 evidence for all v4 packs'
EVIDENCE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$EVIDENCE_COMMIT"
printf '%s\n' "$EVIDENCE_COMMIT" > "$TRANS/042-evidence-commit.txt"
```

Expected: each output is PASS/`mutated:true`, with exactly the eleven kinds in §2.2; the commit adds 11 source JSON + 11 receipt JSON + 11 sidecars per pack. Authority: R4 r4-2, r4-3; R5 V-1.ii, V-1.iii; author CLI `:25-80` and author implementation `:2335-2567`.

### 3.5 Mandatory sacrificial pre-mint refusal check

Pinned mechanics answer the poison question **YES**: `generate_freeze_receipt` evaluates refusals at `arm_readiness.py:6363-6397` but unconditionally writes and plan-pins the PASS or REFUSE receipt at `:6398-6442`; replay authenticates and returns that conclusion at `:6284-6331`. Therefore, before touching the primary clone’s unbuilt freeze slots, mint all three in a sacrificial clone and require PASS.

```bash
PREFLIGHT=$(new_case pre-mint-clean "$EVIDENCE_COMMIT")
for i in 0 1 2; do
  label=$(basename "${PACKS[$i]}")
  set +e
  "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$PREFLIGHT/${PACKS[$i]}" \
    --predecessor-pack-root "$PREFLIGHT/${PREDS[$i]}" \
    > "$TRANS/050-preflight-$label.stdout.json" \
    2> "$TRANS/050-preflight-$label.stderr.txt"
  rc=$?
  set -e
  printf '%s\n' "$rc" > "$TRANS/050-preflight-$label.rc"
  test "$rc" = 0
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"]' \
    "$TRANS/050-preflight-$label.stdout.json"
done
```

Any REFUSE here is a **STOP before primary mint**. Authority: R4 r4-2 poison question; R5 V-2; code `arm_readiness.py:6284-6442`.

### 3.6 Primary freeze x3 and freeze commit

```bash
cd "$CLONE"
for i in 0 1 2; do
  label=$(basename "${PACKS[$i]}")
  capture "060-freeze-$label" "$PY" scripts/generate_arm_readiness.py freeze \
    --pack-root "${PACKS[$i]}" --predecessor-pack-root "${PREDS[$i]}"
  expect_rc "060-freeze-$label" 0
  no_traceback "060-freeze-$label"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"] and d["receipt_path"].endswith("freeze-0004.json")' \
    "$TRANS/060-freeze-$label.stdout.json"
done
git add -- "${PACKS[@]}"
git commit -m 'S-0 freeze-0004 receipts for all v4 packs'
FREEZE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$FREEZE_COMMIT"
printf '%s\n' "$FREEZE_COMMIT" > "$TRANS/061-freeze-commit.txt"
```

Expected per pack: `status:PASS`, `mutated:true`, `freeze-0004.json`, its sidecar, and updated `plan_tree.json`/sidecar. The predecessor path is supplied; all IDs, hashes, and ordinal 0004 are derived by code (`arm_readiness.py:6242-6253,6336-6353`). Authority: R4 r4-2, r4-3; R5 V-1.iv, V-1.v; RH-8.

### 3.7 Construct and prove `_v4` histsem pinset rows — unresolved boundary

The reviewed custody tool’s exact interface is:

```bash
"$PY" "$INPUT/build_v4_histsem_pinset.py" \
  --repository "$CLONE" \
  --base-pinset "$CLONE/configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json" \
  --historical-head "$EVIDENCE_COMMIT" \
  --current-head "$FREEZE_COMMIT" \
  --pack-root "${PACKS[0]}" --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" \
  --output "$CLONE/configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json" \
  > "$TRANS/070-build-v4-pinset.json"
```

It must append exactly one row per `_v4` pack, preserve the nine earlier rows byte-for-byte as parsed values, derive `freeze-0004`, current/historical pack hashes, plan hashes, receipt inventory and post-authoring delta from local Git objects, set `receipt_count:11`, and refuse network/fetch. Then:

The builder/verifier transcript must adjudicate every normative-annex component, not merely emit schema-valid JSON: mandatory `facts[].source_sha256`; K5 historical recomputation against each receipt’s recorded pack digest; K12 pinned current-tree digest; K7 zero-delete/custody-add/freeze-retarget delta envelope as bootstrap hardening; the historical-vs-HEAD coordinate split; derivation ancestry with `origin/main` hard in this clone-proof lane; predecessor binding and predecessor-mode freeze gate; the HEAD differential self-test using the unchanged pack-digest framing; and no fetch, repair, checkout swapping, or network. K5 and K12 are load-bearing; K7 is layered/bootstrap hardening, never sole closure. Authority: RH-8 ruled design items 1–8 and normative annexes, especially consolidated items D2–D8 and D10–D15.

```bash
git -C "$CLONE" add -- configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json
git -C "$CLONE" commit -m 'S-0 add v4 historical-semantics pinset rows'
PINSET_COMMIT=$(git -C "$CLONE" rev-parse HEAD)
git -C "$CLONE" update-ref refs/remotes/origin/main "$PINSET_COMMIT"
capture 071-histsem-present "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --require-published \
  --pack-root "$CLONE/${PACKS[0]}" --pack-root "$CLONE/${PACKS[1]}" \
  --pack-root "$CLONE/${PACKS[2]}"
expect_rc 071-histsem-present 0
cd "$CLONE"
"$PY" -m unittest -v tests.test_receipt_histsem \
  > "$TRANS/072-histsem-differential-bytepin-tests.txt" 2>&1
```

**Do not execute this subsection past pinset construction until Open Item O-1 is ruled.** RH-8 requires the new pinset bytes to be one of the 112 post-derivation paths, but HISTSEM-CONTRACT SHA-pins the entire pinset in `tests/test_receipt_histsem.py:30-31,53-60` and forbids an update/reseal lane. Updating that literal after freeze would add `tests/test_receipt_histsem.py` as a 113th changed path; not updating it makes the normative baseline test fail. The current sources provide no operation satisfying both. Authority: RH-8 and normative annexes; HISTSEM-CONTRACT “Pinset artifact and schema” and “`_v4` transaction sequencing”; R5 V-1.

### 3.8 Family marker — fork on the open Ed ruling

Execute exactly one branch and record the selected branch in `$TRANS/080-marker-decision.txt`.

```bash
printf '%s\n' "$MARKER_BRANCH" > "$TRANS/080-marker-decision.txt"
```

**Option (a), BUILD-AT-BOUNDARY.** After freeze x3 and pinset verification, run the candidate manifest’s reviewed marker constructor and consumer. The S-0 instance stays outside the Git worktree so the base changed-set remains 112:

```bash
mkdir -p "$CUSTODY/marker-candidate"
"$PY" "$INPUT/build_family_marker.py" \
  --repository "$CLONE" --head "$PINSET_COMMIT" \
  --pack-root "${PACKS[0]}" --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" \
  --output "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  > "$TRANS/081-marker-build.json"
"$PY" "$INPUT/verify_family_marker.py" \
  --repository "$CLONE" \
  --marker "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  > "$TRANS/082-marker-verify.json"
```

Expected: schema `joulewise.d117_family_publication_marker.v1`, all three exact pack IDs, freeze receipt IDs/hashes, common Git head, and consumer PASS. If Ed requires the canonical marker and sidecar tracked at `configs/campaigns/d117_family_publication_v4.json[.sha256]`, R4 r4-1’s conditional clause changes 112 to **114**; do not track them under a 112 contract.

**Option (b), UNBUILT token.** Make no marker file. Assert that the reviewed candidate registry/consumer contains the exact `UNBUILT.v0` token, then run its canary and require governed publication refusal:

```bash
"$PY" "$INPUT/verify_family_marker.py" \
  --repository "$CLONE" --expect-token UNBUILT.v0 --publication-canary \
  > "$TRANS/083-marker-unbuilt-canary.json"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and "UNBUILT.v0" in str(d)' \
  "$TRANS/083-marker-unbuilt-canary.json"
```

Expected: governed REFUSE and an explicit publication limitation; arming proof may continue but family publication may not. Authority: MARKER-A1 option (a)/(b); R4 r4-1, r4-2, r4-3; R5 V-1.iv. This fork is intentionally unresolved, not guessed.

### 3.9 Final 112-contract check, arm and verify all three

This step is reachable only after O-1 is resolved without violating the ruled contract.

```bash
FINAL_HEAD=$(git -C "$CLONE" rev-parse HEAD)
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --repo "$CLONE" \
  --derivation "$EVIDENCE_DERIVATION_HEAD" --head "$FINAL_HEAD" \
  > "$TRANS/090-final-allowlist-contract.json"

ARM_CONTEXT=$("$PY" -c 'import json,sys; r=sys.argv[1]; print(json.dumps({
"bracket_session_id":"s0-clone-proof", "pre_attempt_id":"s0-pre",
"post_attempt_id":"s0-post", "clock_route":"MANUAL",
"claim_runs_root":r+"/claim", "bound_runs_root":r+"/bound",
"custody_root":r+"/custody", "quarantine_root":r+"/quarantine",
"claim_backup_destination":r+"/backup-claim",
"bound_backup_destination":r+"/backup-bound", "waiver_path":r+"/waivers.json"}))' \
  "$CUSTODY/arm-context")

for i in 0 1 2; do
  label=$(basename "${PACKS[$i]}")
  capture "091-arm-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" arm \
    --pack-root "$CLONE/${PACKS[$i]}" --arm-context "$ARM_CONTEXT" \
    --window-custody-root "$CUSTODY/windows"
  no_traceback "091-arm-$label"
  rc=$(cat "$TRANS/091-arm-$label.rc"); test "$rc" = 0 -o "$rc" = 1
  ARM_RECEIPT=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["receipt_path"]; print(d["receipt_path"])' \
    "$TRANS/091-arm-$label.stdout.json")
  capture "092-verify-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" verify \
    --pack-root "$CLONE/${PACKS[$i]}" --arm-receipt "$ARM_RECEIPT"
  no_traceback "092-verify-$label"
  vrc=$(cat "$TRANS/092-verify-$label.rc"); test "$vrc" = 0 -o "$vrc" = 2
done
```

The arm may be GO only if all non-S-0 custody/T0 prerequisites are legitimately present. Otherwise a **governed**, non-null arm receipt and canonical verify REFUSE (often `readiness_dependency_refused`) is acceptable; S-0 must not fabricate T0 or measurement evidence. “All items cross old `:3212`” concretely means, for each pack: all eleven generic evidence items are discovered; neither the registry’s `DEPENDENCY_CHANGED_SET` nor `DEPENDENCY_MANIFEST` code appears; no traceback occurs; and an arm receipt is written. Resolve the two candidate-owned spellings mechanically:

```bash
"$PY" - "$REGISTRY" "$CUSTODY/windows" "$TRANS" <<'PY'
import json,pathlib,sys
reg=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]
codes={x["role"]:x["code"] for x in reg["refusal_vocabulary"]}
bad={codes["DEPENDENCY_CHANGED_SET"],codes["DEPENDENCY_MANIFEST"]}
root=pathlib.Path(sys.argv[2]); trans=pathlib.Path(sys.argv[3])
want={"ACCEPTANCE_OWNER","DOCTRINE_PIN","ESTIMATOR_IDENTITY","MINT_TRUST",
"MULTICELL_MINT","PACK_AUTHENTICATION","PACK_FAMILY","REASON_CODE_COVERAGE",
"RECEIPT_ORACLE","RECOVERY_LEDGER_TEST","THREE_WINDOW_REGRESSION"}
for p in sorted(root.glob("*/arm_readiness.receipts/arm-*.json")):
 d=json.load(open(p)); kinds={e.get("receipt_kind") for e in d["evidence"]}
 assert want <= kinds, (p,want-kinds)
 assert not (bad & {r["code"] for r in d["refusals"]}), (p,bad)
print(json.dumps({"status":"PASS","packs":3,"crossed_actual_gate":"arm_readiness.py:4038-4049","forbidden_codes":sorted(bad)}))
PY
```

Authority: R4 r4-2; R5 V-1.iii, V-2; actual changed-set site `arm_readiness.py:4038-4049`; CLI exit semantics `scripts/generate_arm_readiness.py:126-161`.

# 4. PROBE BATTERY

Each probe uses a fresh `new_case` clone. `PROBE_BASE=$FINAL_HEAD`; never reuse a case after a mutation. For R1 codes, extract exact candidate-owned spellings:

```bash
PROBE_BASE=$FINAL_HEAD
CHANGED_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_CHANGED_SET"))' "$REGISTRY")
MANIFEST_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_MANIFEST"))' "$REGISTRY")
printf 'DEPENDENCY_CHANGED_SET=%s\nDEPENDENCY_MANIFEST=%s\n' "$CHANGED_CODE" "$MANIFEST_CODE" > "$TRANS/100-r1-code-map.txt"
```

### 4(a). Ordinary changed path refuses

```bash
CASE=$(new_case ordinary-path "$PROBE_BASE")
printf 'S-0 ordinary-path probe\n' > "$CASE/s0-ordinary-probe.txt"
commit_case "$CASE" 'S-0 probe ordinary changed path'
capture 101-ordinary "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
test "$(cat "$TRANS/101-ordinary.rc")" = 2 -o "$(cat "$TRANS/101-ordinary.rc")" = 1
grep -F "$CHANGED_CODE" "$TRANS/101-ordinary.stdout.json"
no_traceback 101-ordinary
```

Pass iff the exact registry code for `DEPENDENCY_CHANGED_SET` appears and no pack bytes change. Authority: R4 r4-2; R5 V-1; `arm_readiness.py:3916-3964,4038-4049`.

### 4(b). Unexpected output-directory file refuses

```bash
CASE=$(new_case unexpected-output "$PROBE_BASE")
printf 'unexpected\n' > "$CASE/${PACKS[0]}/arm_readiness.evidence/unexpected.txt"
commit_case "$CASE" 'S-0 probe unexpected evidence output'
capture 102-unexpected "$PY" "$CASE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CASE/${PACKS[0]}" --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$CUSTODY/probes/102-unexpected"
expect_rc 102-unexpected 1
grep -F 'readiness_evidence_unreadable' "$TRANS/102-unexpected.stdout.json"
no_traceback 102-unexpected
```

Pass iff canonical governed arm REFUSE includes `readiness_evidence_unreadable`, an external refusal receipt is written, and the pack snapshot is unchanged. Authority: R4 r4-2; R5 V-2; `arm_readiness.py:5248-5265,6987-7135`; the CLI enforces read-only pack snapshots at `scripts/generate_arm_readiness.py:76-85,89-125`.

### 4(c). Non-freeze mutation in current **and** sibling plan trees

For each direction separately, mutate the existing schema-valid string `window_identity.window_id`, re-render canonical JSON and its sidecar, commit, then replay the first pack’s freeze:

```bash
mutate_plan() {
  local repo=$1 rel=$2
  "$PY" - "$repo/$rel" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text())
d["window_identity"]["window_id"] += "-s0-mutation"
raw=(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode(); p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  plan_tree.json\n")
PY
}
CASE=$(new_case plan-current "$PROBE_BASE")
mutate_plan "$CASE" "${PACKS[0]}/plan_tree.json"
commit_case "$CASE" 'S-0 probe current plan non-freeze mutation'
capture 103-plan-current "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
grep -F "$MANIFEST_CODE" "$TRANS/103-plan-current.stdout.json"

CASE=$(new_case plan-sibling "$PROBE_BASE")
mutate_plan "$CASE" "${PACKS[1]}/plan_tree.json"
commit_case "$CASE" 'S-0 probe sibling plan non-freeze mutation'
capture 104-plan-sibling "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
grep -F "$MANIFEST_CODE" "$TRANS/104-plan-sibling.stdout.json"
```

Pass iff both directions refuse with the exact `DEPENDENCY_MANIFEST` code, despite `plan_tree.json` and its sidecar being allowlisted. This is L5-F2’s outstanding mutation falsifier. Authority: R4 r4-2; SIT-C3 and seat-L5 F2; R5 S-6, V-1.vi; `arm_readiness.py:4093-4126`.

### 4(d). Missing, extra, and unused candidate entries all fail

```bash
"$PY" - "$TRANS" <<'PY'
import json,pathlib,sys
t=pathlib.Path(sys.argv[1]); json.load(open(t/"010-allowlist-shape.json"))
# Recreate from the registry rather than trusting transcript order.
reg=json.load(open("configs/arm_readiness/d117_row_registry_v1.json"))["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]
(t/"010-candidate-exact.json").write_text(json.dumps(reg))
(t/"105-missing-list.json").write_text(json.dumps(reg[1:]))
(t/"106-extra-list.json").write_text(json.dumps(sorted(reg+["docs/s0-extra"])))
(t/"107-unused-observed.json").write_text(json.dumps(reg[:-1]))
PY
set +e
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/105-missing-list.json" > "$TRANS/105-missing.json"; test $? = 2
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/106-extra-list.json" > "$TRANS/106-extra.json"; test $? = 2
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" \
  --candidate-list "$TRANS/010-candidate-exact.json" \
  --observed-list "$TRANS/107-unused-observed.json" > "$TRANS/107-unused.json"; test $? = 2
set -e
```

Before this block, write the exact registry list to `010-candidate-exact.json`. Pass iff the three reports respectively name `candidate_missing`, `candidate_extra`, and `unused_allowlist`, all with exit 2. Authority: R4 r4-2; R5 V-1.v; RH-8.

### 4(e). Per-class tamper probes over every allowlisted path class

Install the exact tamper driver, then run one fresh case per class and replay `freeze-0004` for the affected pack. Each mutation remains schema-shaped where that is necessary to reach the intended authenticator.

```bash
cat > "$CUSTODY/tools/tamper_class.py" <<'PY'
import argparse,hashlib,json,pathlib
ap=argparse.ArgumentParser(); ap.add_argument("kind"); ap.add_argument("repo",type=pathlib.Path); ap.add_argument("pack")
a=ap.parse_args(); root=a.repo/a.pack
def render(p,d): p.write_bytes((json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode())
def zero_sidecar(p,target): p.write_text("0"*64+"  "+target+"\n")
if a.kind=="source-json":
 p=root/"arm_readiness.sources/acceptance-owner.json"; d=json.loads(p.read_text())
 d["primary_artifacts"][0]["sha256"]="0"*64; render(p,d)
elif a.kind=="evidence-json":
 p=root/"arm_readiness.evidence/evidence-acceptance-owner.json"; p.write_bytes(p.read_bytes()+b" ")
elif a.kind=="evidence-sidecar":
 p=root/"arm_readiness.evidence/evidence-acceptance-owner.json.sha256"; zero_sidecar(p,"evidence-acceptance-owner.json")
elif a.kind=="freeze-json":
 p=root/"arm_readiness.freeze.receipts/freeze-0004.json"; d=json.loads(p.read_text())
 d["issued_at_utc"]=d["issued_at_utc"].replace("2026-","2027-",1); render(p,d)
elif a.kind=="freeze-sidecar":
 p=root/"arm_readiness.freeze.receipts/freeze-0004.json.sha256"; zero_sidecar(p,"freeze-0004.json")
elif a.kind=="plan-json":
 p=root/"plan_tree.json"; d=json.loads(p.read_text()); d["window_identity"]["window_id"]+="-s0-tamper"; render(p,d)
 raw=p.read_bytes(); p.with_name("plan_tree.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  plan_tree.json\n")
elif a.kind=="plan-sidecar": zero_sidecar(root/"plan_tree.sha256","plan_tree.json")
elif a.kind=="pinset-json":
 p=a.repo/"configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json"; d=json.loads(p.read_text())
 d["packs"][0]["plan_sha256"]="0"*64; render(p,d)
else: raise SystemExit("unknown class")
PY

for class in source-json evidence-json evidence-sidecar freeze-json freeze-sidecar plan-json plan-sidecar pinset-json; do
  CASE=$(new_case "tamper-$class" "$PROBE_BASE")
  "$PY" "$CUSTODY/tools/tamper_class.py" "$class" "$CASE" "${PACKS[0]}"
  commit_case "$CASE" "S-0 per-class tamper $class"
  capture "110-tamper-$class" "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
  test "$(cat "$TRANS/110-tamper-$class.rc")" != 0
  no_traceback "110-tamper-$class"
done

grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-source-json.stdout.json"
grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-evidence-json.stdout.json"
grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-evidence-sidecar.stdout.json"
grep -F 'readiness_freeze_receipt_mismatch' "$TRANS/110-tamper-freeze-json.stdout.json"
grep -F 'readiness_freeze_receipt_mismatch' "$TRANS/110-tamper-freeze-sidecar.stdout.json"
grep -F "$MANIFEST_CODE" "$TRANS/110-tamper-plan-json.stdout.json"
grep -F 'readiness_pack_digest_mismatch' "$TRANS/110-tamper-plan-sidecar.stdout.json"
grep -E '"histsem_[a-z0-9_]*(mismatch|invalid)"' "$TRANS/110-tamper-pinset-json.stdout.json"
```

The complete enumerated classes and counts are:

| Class (count) | Representative mutation | Expected authenticator/refusal |
|---|---|---|
| source JSON (33) | change one primary-artifact digest without changing its receipt | `readiness_evidence_digest_mismatch` |
| evidence JSON (33) | change one receipt byte | `readiness_evidence_digest_mismatch` |
| evidence sidecar (33) | replace its digest with 64 zeroes | `readiness_evidence_digest_mismatch` |
| freeze JSON (3) | change its still-valid timestamp | `readiness_freeze_receipt_mismatch` |
| freeze sidecar (3) | replace its digest | `readiness_freeze_receipt_mismatch` |
| plan-tree JSON (3) | coherent non-freeze mutation plus corrected sidecar | `$MANIFEST_CODE` (also §4(c)) |
| plan-tree sidecar (3) | replace its digest only | `readiness_pack_digest_mismatch` |
| RH pinset JSON (1) | change one governed row’s `plan_sha256` | a `histsem_*_mismatch` refusal; byte-only tamper must also fail the SHA-pin test |

For the pinset byte-authenticator additionally run inside the `tamper-pinset-json` case:

```bash
set +e
cd "$CASES/tamper-pinset-json"
"$PY" -m unittest -v tests.test_receipt_histsem \
  > "$TRANS/118-pinset-byte-pin.txt" 2>&1
test $? != 0
set -e
cd "$CLONE"
```

Pass iff **all eight** classes refuse through an independent digest, binding, or semantic replay authenticator. If any class has no such authenticator, apply V-1.vi’s digest-conditional subtraction rule: it may not remain a static allowlist subtraction; remove that class from the candidate allowlist and bind it in the authenticated derived manifest, then reopen the mechanism proof. Authority: R5 V-1.iv, V-1.vi, V-1.vii; RH-8; semantic replay `arm_readiness.py:6161-6185`.

### 4(f). `DEPENDENCY_MANIFEST` conjunct — both halves

1. **Source/receipt half:** coherently change a source and its facts’ `source_sha256`, re-sidecar the receipt, but deliberately leave the receipt’s `dependency_manifest_sha256` at its old value. This crosses the ordinary source-digest authenticator and reaches `arm_readiness.py:4051-4067`:

```bash
CASE=$(new_case manifest-binding "$PROBE_BASE")
"$PY" - "$CASE/${PACKS[0]}" <<'PY'
import hashlib,json,pathlib,sys
r=pathlib.Path(sys.argv[1]); src=r/"arm_readiness.sources/acceptance-owner.json"
rec=r/"arm_readiness.evidence/evidence-acceptance-owner.json"
s=json.loads(src.read_text()); s["primary_artifacts"][0]["sha256"]="0"*64
sraw=(json.dumps(s,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode(); src.write_bytes(sraw)
d=json.loads(rec.read_text()); new=hashlib.sha256(sraw).hexdigest()
for fact in d["facts"]: fact["source_sha256"]=new
# Intentionally do not change d["dependency_manifest_sha256"].
rraw=(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode(); rec.write_bytes(rraw)
rec.with_name(rec.name+".sha256").write_text(hashlib.sha256(rraw).hexdigest()+"  "+rec.name+"\n")
PY
commit_case "$CASE" 'S-0 manifest source-receipt conjunct'
capture 119-manifest-binding "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
grep -F "$MANIFEST_CODE" "$TRANS/119-manifest-binding.stdout.json"
no_traceback 119-manifest-binding
```

2. **Derivation/current dependency half:** the exact coherent current-plan and sibling-plan commands are §4(c), transcripts `103-plan-current` and `104-plan-sibling`. Both must contain `$MANIFEST_CODE` from `arm_readiness.py:4070-4126`.

All three outputs must be nonzero and traceback-free. Both logical halves are conjunctive; one does not substitute for the other. Authority: R5 S-6 and V-1.vi; SIT-C3; `arm_readiness.py:4051-4126`.

### 4(g). S-6 dual-validator falsifiers

In a fresh case make the coherent plan mutation from §4(c), then run both genuinely different validators:

```bash
CASE=$(new_case s6-dual "$PROBE_BASE")
mutate_plan "$CASE" "${PACKS[0]}/plan_tree.json"
commit_case "$CASE" 'S-0 S-6 dual-validator mutation'
set +e
"$PY" "$CASE/${PACKS[0]}/generate_configs.py" --check \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 \
  --preserve-current-frozen-bytes \
  > "$TRANS/120-s6-preserve-check.txt" 2>&1
PRESERVE_RC=$?
set -e
test "$PRESERVE_RC" = 0
capture 121-s6-r1 "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
grep -F "$MANIFEST_CODE" "$TRANS/121-s6-r1.stdout.json"
```

Expected falsifier: preserve-mode `--check` returns 0 because it echoes checked-out bytes into its comparison, while R1 refuses the same mutation with `$MANIFEST_CODE`. If the candidate intentionally fixes the echo hole, the manifest must say so and the first expected result becomes a governed nonzero check; the R1 half remains mandatory. Authority: R5 S-6; SIT-C3; generator `:1942-1950`; R1 manifest `:4093-4126`.

### 4(h). Histsem and pinset probes

Present was captured at `071-histsem-present` and must PASS before arm. Explicit absence is exercised without deleting or touching a real checkout:

```bash
ABSENT="$CASES/definitely-absent-pinset.json"
test ! -e "$ABSENT"
capture 130-histsem-absent "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --pinset "$ABSENT" --require-published
expect_rc 130-histsem-absent 2
grep -F 'histsem_pinset_absent' "$TRANS/130-histsem-absent.stdout.json"
```

Then rerun §4(d) missing/extra/unused with the 112 literal. Pass iff present -> histsem PASS then arms cross the actual changed-set gate; explicit absent -> `histsem_pinset_absent`; and all three malformed candidate variants fail. HISTSEM-CONTRACT’s later rule-11 clarification is recorded: the *library’s default HEAD pinset absence* returns ordinary readiness; only this explicit CLI/worktree verifier path promises `histsem_pinset_absent`. Authority: RH-8 and normative annexes; HISTSEM-CONTRACT “Failure semantics”; `verify_receipt_histsem.py:22-73`; `tests/test_receipt_histsem.py:62-80`.

### 4(i). Poison question — direct code-path probe

Create a case at `EVIDENCE_COMMIT`, delete one generic evidence pair, mint, commit the refused mint, then replay unchanged:

```bash
CASE=$(new_case poison "$EVIDENCE_COMMIT")
git -C "$CASE" rm -- \
  "${PACKS[0]}/arm_readiness.evidence/evidence-acceptance-owner.json" \
  "${PACKS[0]}/arm_readiness.evidence/evidence-acceptance-owner.json.sha256"
commit_case "$CASE" 'S-0 poison input: missing evidence'
capture 140-poison-first "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is True and d["receipt_path"].endswith("freeze-0004.json")' \
  "$TRANS/140-poison-first.stdout.json"
commit_case "$CASE" 'S-0 poison refused freeze becomes plan-pinned'
capture 141-poison-replay "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/${PACKS[0]}" --predecessor-pack-root "$CASE/${PREDS[0]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is False and d["receipt_path"].endswith("freeze-0004.json")' \
  "$TRANS/141-poison-replay.stdout.json"
```

At pinned HEAD the expected answer is **YES**. Consequence: the clean sacrificial PASS in §3.5 is mandatory before each primary mint; after a primary REFUSE write, abandon the primary clone and restart from `EVIDENCE_COMMIT`—do not try to repair the plan-pinned refusal in place. If a candidate changes the first result to `mutated:false` with no freeze/plan write, record **NO**, retain the preflight as a defense-in-depth check, and verify no pack bytes changed. Any third outcome (partial write, traceback, or replay not idempotent) reopens the mechanism. Authority: R4 r4-2 poison question; R5 V-2; `arm_readiness.py:6284-6442`.

# 5. ACCEPTANCE CHECKLIST

Evidence root: `$CUSTODY/transcripts` (all referenced artifacts are clone-proof custody, never a measurement checkout). Check a box only after independently reading its named artifacts.

- [ ] **r4-2** — One full three-pack sequence is evidenced by `030-*`, `032-*`, `040-*`, `042-*`, `050-*`, `060-*`, `061-*`, `080-*`, `090-*`, `091-*`, and `092-*`; every pack crosses actual `arm_readiness.py:4038-4049`; ordinary path, unexpected output, both plan-tree directions, candidate-shape triplet, and poison probes adjudicate as specified.
- [ ] **V-2** — Lead/magistrate custody and nondelegation are recorded in `001-*` through `004-*`; S-6 both validators are `120-*`/`121-*`; governed arm+verify and every transcript have been read with no fail-ugly traceback.
- [ ] **V-1.vi** — All eight path classes in `110-*` through `118-*` have independent tamper refusals, including the two manifest halves; any unauthenticated class has triggered the digest-conditional subtraction/reopen rather than being waived.
- [ ] **rh-8** — The 112 arithmetic and exact final contract are PASS in `010-*`/`090-*`; present histsem and arm crossing are `071-*`/`091-*`; explicit absence is `130-*`; missing/extra/unused are `105-*`–`107-*`; all three `_v4` pinset rows and their local-Git provenance are in `070-*`.
- [ ] Candidate patch SHA, manifest, pinset builder, marker decision, HEADs, Git statuses, and complete stdout/stderr/exit-code triplets are present under the custody root.
- [ ] No command touched or read `/Users/edr/JouleWise-measurement-20260818`; no quiet-Mac measurement, freeze outside the clone, dry-run, arm launch, consume, or publication occurred.

# 6. FAILURE SEMANTICS

**Mechanism failures — trip V-1.vi and REOPEN to the derived authenticated manifest:** an ordinary nonallowlisted path crosses; an unexpected evidence output is accepted; either current or sibling coherent non-freeze plan mutation crosses R1; any missing/extra/unused candidate variant is accepted; any one of the eight allowlisted classes lacks an independent tamper authenticator; either `DEPENDENCY_MANIFEST` half crosses; S-6’s R1 validator crosses; histsem present does not gate arm/freeze, explicit-CLI absence does not produce `histsem_pinset_absent`, or the 112 candidate malformed variants cross; a refusal mint partially writes, fails ugly, or cannot be safely screened by the sacrificial preflight. The response is not “fix a test expectation”: derive an authenticated manifest, remove every unauthenticated subtraction, rerun all of S-0, and preserve the failed transcript. Authority: R5 V-1.vi, V-1.vii, V-2; R4 r4-2; RH-8.

**Ordinary defects — fix and restart the affected clean case or the whole transaction as indicated:** wrong CLI spelling, missing custody input, sidecar checksum mismatch, malformed probe fixture that fails before reaching its intended gate, transcript collision, or a legitimate non-S-0 T0/refusal after all lifecycle gates crossed. A primary freeze REFUSE is recoverable only by abandoning that primary clone and restarting from the committed evidence state because §4(i) proves it is plan-pinned. A baseline candidate test failure, unresolved `ED_RESERVED:` value, line-audit mismatch, 11/112 count mismatch, or dirty reviewed tree is a precondition defect: stop before mint, correct the reviewed candidate, and start again. Authority: R4 r4-2, r4-3, r4-5; R5 S-6, V-1, V-2.

# 7. OPEN ITEMS

### O-1 — NEEDS_RULING: RH pinset rows versus the no-update byte pin

Question: how can S-0 append the mandatory post-freeze `_v4` pinset rows while retaining both the exact 112 post-derivation changed set and the normative literal SHA assertion over the entire pinset?

Facts: RH-8 requires the three rows after freeze x3 and adds only the pinset path (111 -> 112). HISTSEM-CONTRACT requires the literal pinset SHA in `tests/test_receipt_histsem.py:30-31,53-60` with no update/reseal lane. The final pinset bytes cannot be known at evidence derivation because freeze receipts include newly minted, code-derived content. Updating the test after derivation creates path 113; leaving it unchanged fails the mandated byte-pin test.

Options considered:

1. Amend the ruled contract to 113 and authorize the exact test path plus a one-time reviewed literal update.
2. Rule a different stable authentication construction whose already-pinned bytes can authenticate append-only `_v4` rows without changing the test path; this requires a reviewed code delta before S-0.
3. Waive the `_v4` rows or the byte pin. Not recommended: each contradicts a binding RH obligation.

Recommendation: option 2 if a stable authenticated-root design already exists and can be reviewed before candidate derivation; otherwise the narrow, explicit 113-path amendment in option 1. Blocked work: §3.7 commit onward, final contract, histsem present, arm/verify, and acceptance closure. All earlier assembly remains executable.

### O-2 — Ed’s V6 marker ruling

Ed must select MARKER-A1 option (a) BUILD-AT-BOUNDARY or option (b) `UNBUILT.v0`. Under (a), Ed must additionally rule whether S-0 custody-external construction suffices for the 112 proof or whether the two canonical tracked paths are required, in which case R4 r4-1 makes the changed set 114. Under (b), the governed publication-refusal canary and explicit limitation are mandatory. This does not block runsheet assembly because §3.8 forks both ways; it blocks a single bench execution until selected.

### O-3 — Missing reviewed candidate custody

Pinned HEAD has no `_v4` roots and no resolved R1 candidate registry. The patch, manifest, exact marker helper/consumer for the selected branch, and deterministic pinset-row builder described in §1.3 are not present in the authoritative commit. Their lead-reviewed bytes and SHA sidecars must be placed in `$INPUT`; S-0 may verify and execute them but may not invent them. This is missing custody, not a license to expand scope.
