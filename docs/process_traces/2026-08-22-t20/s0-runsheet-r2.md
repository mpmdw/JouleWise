# S-0 CLONE-PROOF RUNSHEET R2 — JouleWise `_v4` transaction


**ANCHOR MAP AT THE EXECUTION HEAD (lead pre-execution read, 2026-08-23,
verified at the merged head): the S-1 merge shifted every
`joulewise/arm_readiness.py` anchor below by the candidate's insertions.
The recomputed authoritative positions are:**
- `EvidenceLifecycleError` (a `ValueError`): `:1050`
- changed-set enumeration `_r1_changed_paths`: `:4115`
- allowlist subtraction + conditional-path logic: `:4300` (registry
  cross-check of conditional paths: `:2025`)
- generic-item authentication `_authenticate_generic_evidence_item`: `:5266`
- freeze reference load: `:6265`; `generate_freeze_receipt`: `:6531`
  (generation gate `:6572`); histsem gate `_gate_receipt_histsem`: `:3639`
**Non-arm_readiness anchors (identity_pins `:1826`, generate CLI `:28`,
identity CLI `:23`, histsem CLI `:22`) verified UNMOVED. Where this map
and an inline citation below disagree, THIS MAP governs.**

**PIN UPDATE (2026-08-23): the assembly pin advances to the MERGED candidate head on main (the merge wave e6a6520 + subsequent green head at execution time). The mechanics-map line anchors below were verified at 1ba04a8; re-verify the enumerated anchor set at the execution head before running (lead pre-execution read step). The §9.3.6 open finding was RESOLVED by the independent seat + fix round: the re-derivation path is proven live (fixture defect cured); O-4 is discharged.**

Assembly target: repository commit `1ba04a83b6dacc2ea904c7936901922857ac89d4` (`1ba04a8`). This is a bench runsheet, not an execution transcript. The magistrate executes it, lead-executed, in the throwaway clone below and reads every transcript. It never uses or reads `/Users/edr/JouleWise-measurement-20260818`.

Lead ruling records Ed’s mint license as granted, so license is not an S-0 blocker. Execution still stops at the explicit reviewed-custody boundary in §1.3 and at the Ed-confirmed step-6 publication boundary in §§3.7–3.9. Candidate-lane work in this clone is never publication. Authority for this R2 boundary: `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md` (D-151 conditions 3–5) and `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md` (ratified items 1–3).

Binding-source shorthand used below:

- **R4** = `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`, cited by `r4-N`.
- **R5** = `docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md`, cited by `S-N`, `V-1.i`–`V-1.vii`, or `V-2`.
- **RH-8** = `docs/process_traces/2026-08-20-go-session/rh-ruling.md`, item 8 and its normative annexes `rh-terra-debate.md` and `rh-opus-debate.md`.
- **SIT-C3** = `docs/process_traces/2026-08-20-go-session/ready-sitting-ruling.md`, C-3, with `readiness-sitting/seat-L5.md`, F2.
- **MARKER-A1** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md`, A-1.
- **HISTSEM-CONTRACT** = `docs/contracts/receipt_histsem_verifier.md`, especially “Pinset artifact and schema,” “Gate integration,” “Failure semantics,” and “`_v4` transaction sequencing.” Its rule-11 absence clarification supersedes the original library-absence wording without changing the explicit-CLI absence probe.
- **D-151** = `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`, adopting O-1-D and its incorporated nine-condition set.
- **D-150 / MARKER-RULING** = `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`; D-150 selects option (a), BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with the changed-set contract remaining 112.
- **REGISTRY-V2 RULING** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:124-131`; the RULED live coordinate is outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`.
- **S-1 MANIFEST** = `/Users/edr/code/JouleWise-wt-s1/docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md` at worktree head `c1b87f63fd47507dd1504693ad45347a4f2c55aa`; its §9 is an implementing-seat self-report pending independent review.

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

**SUPERSEDED-BY-MERGE (lead pre-execution ruling, 2026-08-23): the
candidate MERGED to main (3c098de wave; CI green 42df510,
conclusion-field-verified) before S-0 execution, which is strictly
stronger provenance than a patch + sidecar. The patch-acquisition and
git-apply steps below are MOOT: the clone in §1.1 is cut from the
merged head, which already contains the registry v2, all four custody
tools with committed sidecars, and both contract docs — and correctly
does NOT contain the generated `_v4` pack outputs (S-0 generates
those). What survives of this section: (a) record the clone identity
in the transcript (head SHA + the green CI run id) as the provenance
line; (b) the lead generates `$INPUT/s0-candidate-manifest.json`
MECHANICALLY from committed bytes at the head — custody_tools =
{repo-relative tool path: sha256 of the committed blob} for the four
tools, marker_branch "BUILD-AT-BOUNDARY", plus the head SHA — with the
generation command captured in the transcript (candidate-mode tool
authentication reads this manifest; runsheet §3.8 and the S-5 lane
rule are unchanged); (c) every stop condition below (ED_RESERVED
strings, digest mismatch, missing tool) still stops execution. The
historical §1.3 text follows unmodified as the record of the
pre-merge design.**

Pinned HEAD contains neither the three `_v4` roots nor the reviewed candidate. The S-1 candidate manifest names one patch export, one binding manifest, and four custody tools. Place these lead-reviewed custody inputs in `$INPUT` before proceeding:

1. `s0-candidate.patch` and GNU sidecar `s0-candidate.patch.sha256`. The lead exports this patch at gauntlet close from the accepted candidate head; it is deliberately absent from the S-1 worktree before that point. It implements the ruled registry/code/contracts/tests but contains no generated `_v4` pack output.
2. `s0-candidate-manifest.json`. It binds the accepted candidate head, patch SHA, exact changed paths, test commands, R1 refusal vocabulary, the single marker branch `BUILD-AT-BOUNDARY`, and a `custody_tools` object containing the pre-execution SHA-256 of all four repo-relative tool paths.
3. `build_v4_histsem_pinset.py` and `build_v4_histsem_pinset.py.sha256`.
4. `build_family_marker.py` and `build_family_marker.py.sha256`.
5. `verify_family_marker.py` and `verify_family_marker.py.sha256`.
6. `verify_receipt_histsem.py` and `verify_receipt_histsem.py.sha256`.

This enumeration is the candidate’s actual custody surface: the four tool sidecars exist in S-1, while `s0-candidate.patch[.sha256]` is a lead export at gauntlet close. No alternative marker branch or consumer exists in this runsheet. Authority: S-1 MANIFEST §§2.4, 4, 6, and 9.1 G-1; MARKER-RULING “Adjudicated splits” S-5 and “Consequences.”

```bash
cd "$INPUT"
shasum -a 256 -c s0-candidate.patch.sha256
shasum -a 256 -c build_v4_histsem_pinset.py.sha256
shasum -a 256 -c build_family_marker.py.sha256
shasum -a 256 -c verify_family_marker.py.sha256
shasum -a 256 -c verify_receipt_histsem.py.sha256
MARKER_BRANCH=$("$PY" -c 'import json; d=json.load(open("s0-candidate-manifest.json")); assert d["marker_branch"] == "BUILD-AT-BOUNDARY"; print(d["marker_branch"])')
"$PY" - "$INPUT" <<'PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1])
manifest=json.loads((root/"s0-candidate-manifest.json").read_text())
names={
 "scripts/build_family_marker.py":"build_family_marker.py",
 "scripts/verify_family_marker.py":"verify_family_marker.py",
 "scripts/build_v4_histsem_pinset.py":"build_v4_histsem_pinset.py",
 "scripts/verify_receipt_histsem.py":"verify_receipt_histsem.py",
}
assert set(manifest["custody_tools"]) == set(names)
for relative,name in names.items():
 digest=hashlib.sha256((root/name).read_bytes()).hexdigest()
 assert manifest["custody_tools"][relative] == digest, (relative,digest)
PY
cd "$CLONE"
git apply --check "$INPUT/s0-candidate.patch"
git apply "$INPUT/s0-candidate.patch"
"$PY" -m json.tool "$INPUT/s0-candidate-manifest.json" >/dev/null
git diff --binary "$BASE" > "$TRANS/003-applied-candidate.diff"
shasum -a 256 "$INPUT/s0-candidate.patch" \
  "$INPUT/s0-candidate-manifest.json" \
  "$INPUT/build_v4_histsem_pinset.py" \
  "$INPUT/build_family_marker.py" \
  "$INPUT/verify_family_marker.py" \
  "$INPUT/verify_receipt_histsem.py" > "$TRANS/004-input-sha256.txt"
```

The manifest digest is the candidate-mode tool authority: sidecars prove transfer integrity, but executing marker tools are authenticated against the already-reviewed `s0-candidate-manifest.json` `custody_tools` digests, never against committed blobs and never by recomputing a self-authenticating sidecar. Production/publication phases retain committed-blob equality. Authority: MARKER-RULING split S-5; S-1 MANIFEST §§6 and 9.1 G-4.

If any input is absent, mismatched, contains `ED_RESERVED:`, or its manifest and patch disagree, stop: this is missing custody, not authority to improvise mechanism. The S-1 manifest at `c1b87f6` is still not itself lead acceptance, and its patch export remains deferred until gauntlet close. Authority: R4 r4-5, r4-7; R5 S-6, V-1, V-2; S-1 MANIFEST status, §§6 and 9.

Before mint, perform the ruled literal-string consistency sweep for the registry repoint. Frozen campaign evidence and historical process traces retain their archival v1 bytes; they are never bulk-rewritten. Classify each of the eleven live surfaces below as either a correct archival reference retained or a stale live pointer already repointed by the reviewed candidate, and append that per-file disposition to `005-registry-v1-literal-sweep.txt`:

```bash
cd "$CLONE"
LIVE_V1_SURFACES=(
  docs/decision_log.md
  docs/phase_2/alpha_arm_readiness.md
  docs/phase_2/beta_arm_readiness.md
  docs/phase_2/gamma_arm_readiness.md
  docs/phase_2/window_runbook.md
  tests/test_arm_readiness_evidence_t0.py
  tests/test_arm_readiness_integration.py
  tests/test_arm_readiness_lifecycle.py
  tests/test_arm_readiness_registry.py
  tests/test_arm_readiness_schemas.py
  tests/test_d117_decode_contrast_plan.py
)
set +e
rg -n 'd117_row_registry_v1|d117-row-registry-v1' \
  "${LIVE_V1_SURFACES[@]}" > "$TRANS/005-registry-v1-literal-sweep.txt"
SWEEP_RC=$?
set -e
test "$SWEEP_RC" = 0 -o "$SWEEP_RC" = 1
```

At least `tests/test_arm_readiness_schemas.py` is a correct retention because it pins the archival v1 SHA. No file under `joulewise/` may retain the v1 live pointer. Any unclassified or stale live hit is a candidate precondition defect; correct the reviewed candidate and restart rather than editing it ad hoc in S-0. Authority: REGISTRY-V2 RULING (`MAGISTRATE-RULING.md:124-131`, including the literal-string consistency sweep); S-1 MANIFEST §7 and §9.3.1 item 3.

**AMENDMENT (2026-08-24, cold-gate packets 1 and 2; custody
`s0-clone-proof/custody/transcripts/006–013` of the 2026-08-24 session).**
Two rulings bind this clause's application:

1. *Census scope (packet 1, two-seat concurrence).* The sweep pattern
   above greps BOTH literal forms while MANIFEST §7's census and its
   "no file under `joulewise/`" claim cover the underscore filename
   form only. The clause therefore also fires on the hyphen-form id
   constant `joulewise/arm_readiness.py:46` (`ROW_REGISTRY_ID =
   "d117-row-registry-v1"`), whose ruled disposition is CORRECT
   ARCHIVAL RETENTION: it is reachable only for v1-schema documents,
   selects nothing live (`ROW_REGISTRY_RELATIVE_PATH` at `:88` is the
   live pointer), and mirrors the documented
   `FREEZE_RECEIPT_V1_SCHEMA` retention pattern. That hit does not
   stop S-0. A follow-up naming row (REGISTRY-ID-NAMING-01) is
   registered and fenced outside the transaction window.
2. *Fence (packet 2, magistrate synthesis adopting the refuter).* The
   classification lanes here admit ONLY mechanical classification of
   hits into the two listed classes. Any hit whose disposition would
   require more than that — a repoint, a rewritten sentence, a
   resolved semantic conflict, any new `joulewise/` hit — is a
   candidate precondition defect: stop, correct the reviewed candidate
   on main through the ordinary review lane, and restart S-0 from a
   fresh estate. In-clone doc edits are FORBIDDEN in S-0 because
   DOCTRINE_PIN mints whole-file hashes of `window_runbook.md` and
   `decision_log.md` (`arm_readiness_evidence.py:799-830`): an
   in-clone edit would certify bytes no reviewed candidate ever
   contained. The four class-(b) doc hits found 2026-08-24 were cured
   on main under this rule (Q1-RESTART executed).

# 2. ALLOWLIST GENERATION

### 2.1 Generate, never hand-type, the base 112-path contract

Install this custody-only checker. It generates 37 exact paths per pack: 11 source JSONs, 11 evidence JSONs, 11 evidence sidecars, `freeze-0004.json` plus sidecar, and `plan_tree.json` plus sidecar. The versioned successor pinset `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` is the 112th allowlist entry in the membership sense; it **replaces**, rather than supplements, the old v1 pinset in this slot. Projection receipts, `producer_contract.json`, identity-projection paths, and every authenticator path are intentionally absent because U11 precedes derivation and D-151’s fixed-point principle forbids authenticators in any allowlist. Authority: D-151 conditions 1, 2, and 7; S-1 MANIFEST §3.

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
PINSET = "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"

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

REGISTRY="$CLONE/configs/arm_readiness/d117_row_registry_v2.json"
"$PY" - "$REGISTRY" <<'PY'
import json,sys
registry=json.load(open(sys.argv[1]))
assert registry["registry_id"] == "d117-row-registry-v2"
assert registry["schema_version"] == "joulewise.arm_readiness_row_registry.v2"
PY
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --shape-only | tee "$TRANS/010-allowlist-shape.json"
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_count"])' "$TRANS/010-allowlist-shape.json")" = 112
```

The arithmetic is `3 × (11 + 11 + 11 + 1 + 1 + 1 + 1) + 1 = 3 × 37 + 1 = 112`. R5 V-1 supplies the three 37-path packs (111); O-1-D supplies exactly `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` as the `+1`. The old `legacy_receipt_histsem_pinset_v1.json` remains archival and byte-pinned but is **not** in this allowlist. “112th entry” means membership; the stored list is sorted, so the successor need not be physically last. The contract remains pack-and-ordinal exact (`freeze-0004`, not a glob), and the custody-external marker contributes zero tracked paths. Authority: D-151 conditions 1–2 and Consequences; D-150 / MARKER-RULING opening constraints; S-1 MANIFEST §§3–4.

The live registry coordinate used throughout this runsheet is outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`. The archival v1 registry remains untouched only for frozen historical references. Authority: REGISTRY-V2 RULING (`MAGISTRATE-RULING.md:124-131`); S-1 MANIFEST §§2.1, 8.3, and 9.3.1 item 3.

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

### 3.7 Mint the versioned successor, close the 112-path window, then fix it

The reviewed custody tool’s exact interface is:

```bash
"$PY" "$INPUT/build_v4_histsem_pinset.py" \
  --repository "$CLONE" \
  --base-pinset "$CLONE/configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json" \
  --historical-head "$EVIDENCE_COMMIT" \
  --current-head "$FREEZE_COMMIT" \
  --pack-root "${PACKS[0]}" --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" \
  --output "$CLONE/configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json" \
  > "$TRANS/070-build-v4-pinset.json"
```

The output path is create-only and must be absent before the command. The v1 artifact is an immutable member 1 of the code-enumerated chain and is never modified. The successor is member 2 and carries exactly one row per `_v4` pack (three rows, 33 receipts total), with no `(pack_id, pack_path)` duplicated across chain members; a tool that copies the nine v1 rows into the successor is refused by the chain-integrity rule. Each new row derives `freeze-0004`, current/historical pack hashes, plan hashes, receipt inventory and post-authoring delta from local Git objects, sets `receipt_count:11`, and refuses network/fetch. Authority: D-151 conditions 1, 3, and 6; `docs/contracts/d117_step6_confirmation_table.md` exact `successor_pinset` schema; S-1 MANIFEST §§2.4 and 3.

The builder/verifier transcript must adjudicate every normative-annex component, not merely emit schema-valid JSON: mandatory `facts[].source_sha256`; K5 historical recomputation against each receipt’s recorded pack digest; K12 pinned current-tree digest; K7 zero-delete/custody-add/freeze-retarget delta envelope as bootstrap hardening; the historical-vs-HEAD coordinate split; derivation ancestry with `origin/main` hard in this clone-proof lane; predecessor binding and predecessor-mode freeze gate; the HEAD differential self-test using the unchanged pack-digest framing; and no fetch, repair, checkout swapping, or network. K5 and K12 are load-bearing; K7 is layered/bootstrap hardening, never sole closure. Authority: RH-8 ruled design items 1–8 and normative annexes, especially consolidated items D2–D8 and D10–D15.

```bash
SUCCESSOR_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json
"$PY" - "$CLONE/$SUCCESSOR_PINSET" "$TRANS/070-build-v4-pinset.json" <<'PY'
import json,sys
pinset=json.load(open(sys.argv[1])); build=json.load(open(sys.argv[2]))
assert build["status"] == "PASS"
assert len(pinset["packs"]) == 3
assert sum(row["receipt_count"] for row in pinset["packs"]) == 33
assert {row["pack_id"] for row in pinset["packs"]} == {
 "d117_contrast_qwen25_1p5b_vs_7b_v4",
 "d117_floor_qwen25_1p5b_v4",
 "d117_floor_qwen25_7b_v4",
}
PY
git -C "$CLONE" diff --exit-code -- configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json
git -C "$CLONE" add -- "$SUCCESSOR_PINSET"
git -C "$CLONE" commit -m 'S-0 mint v4 historical-semantics successor pinset'
WINDOW_CLOSE_HEAD=$(git -C "$CLONE" rev-parse HEAD)
PINSET_COMMIT=$WINDOW_CLOSE_HEAD
git -C "$CLONE" update-ref refs/heads/main "$WINDOW_CLOSE_HEAD"
git -C "$CLONE" update-ref refs/remotes/origin/main "$WINDOW_CLOSE_HEAD"
printf '%s\n' "$WINDOW_CLOSE_HEAD" > "$TRANS/070-window-close-head.txt"

"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --repo "$CLONE" \
  --derivation "$EVIDENCE_DERIVATION_HEAD" --head "$WINDOW_CLOSE_HEAD" \
  > "$TRANS/090-final-allowlist-contract.json"
capture 071-histsem-present "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --require-published \
  --pack-root "$CLONE/${PACKS[0]}" --pack-root "$CLONE/${PACKS[1]}" \
  --pack-root "$CLONE/${PACKS[2]}"
expect_rc 071-histsem-present 0
cd "$CLONE"
"$PY" -m unittest -v tests.test_receipt_histsem \
  > "$TRANS/072-histsem-differential-bytepin-tests.txt" 2>&1
```

`090-final-allowlist-contract.json` closes the changed-set window at exactly 112. The successor is the sole digest-conditional class: allowlist membership makes it eligible for subtraction but never authenticates it. Until Ed confirms the unified step-6 table’s `C → S` edge, no claim-bearing arm may use it. The changed-set contract is a property of this closed window, not a standing repository invariant, and no authenticator path enters it. Authority: D-151 conditions 2, 5, 7, and 8.

The **first commit after window close** is the fixation commit. At this hard review boundary, apply the separately reviewed mechanical fixation/activation delta. In `tests/test_receipt_histsem.py` it adds the successor SHA literal and recomputed successor counts as **new assertions without touching any v1 assertion**, and renames the then-false `test_differential_self_test_all_nine_packs`. *(STRUCK 2026-08-23 with the §5.1 addendum: the 21 methods are A84/A85 work, not S-0 acceptance; no activation delta over them belongs to the fixation commit.)* The exact edits and new test name are owned by the reviewed delta; the operator does not invent them at the bench. An independent reviewer recomputes the successor SHA and counts from the minted bytes and later checks the same SHA against Ed’s exact step-6 table. Authority: D-151 condition 3 and Consequences; S-1 MANIFEST §§9.3 and 9.3.5.

```bash
# STOP until the reviewed fixation/activation delta has been applied.
"$PY" - "$CLONE" <<'PY'
import pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1])
changed=set(subprocess.check_output(
 ["git","-C",str(root),"diff","--name-only"],text=True).splitlines())
allowed={
 "tests/test_receipt_histsem.py",
 "tests/test_arm_readiness_evidence_t0.py",
 "tests/test_arm_readiness_integration.py",
 "tests/test_arm_readiness_dry_run.py",
 "tests/test_arm_readiness_lifecycle.py",
 "tests/test_d117_decode_contrast_plan.py",
}
assert "tests/test_receipt_histsem.py" in changed
assert changed <= allowed, sorted(changed-allowed)
PY
git -C "$CLONE" diff --exit-code "$WINDOW_CLOSE_HEAD" -- \
  configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json
git -C "$CLONE" add -- \
  tests/test_receipt_histsem.py \
  tests/test_arm_readiness_evidence_t0.py \
  tests/test_arm_readiness_integration.py \
  tests/test_arm_readiness_dry_run.py \
  tests/test_arm_readiness_lifecycle.py \
  tests/test_d117_decode_contrast_plan.py
git -C "$CLONE" commit -m 'S-0 fix successor pinset SHA and counts after window close'
FIXATION_COMMIT=$(git -C "$CLONE" rev-parse HEAD)
test "$(git -C "$CLONE" rev-list --count "$WINDOW_CLOSE_HEAD..$FIXATION_COMMIT")" = 1
git -C "$CLONE" update-ref refs/heads/main "$FIXATION_COMMIT"
git -C "$CLONE" update-ref refs/remotes/origin/main "$FIXATION_COMMIT"
printf '%s\n' "$FIXATION_COMMIT" > "$TRANS/073-fixation-commit.txt"
```

The local chain verification and fixation tests are necessary but remain forged-`origin/main`-conditional in this clone. Transcript labels must say exactly that; they must not say “suite green.” Authority: D-151 conditions 3–4.

### 3.8 Family marker — D-150 option (a) only, custody-external

D-150 leaves one legal branch: `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL. It contributes no tracked path and leaves the contract at 112. Record that single decision in `$TRANS/080-marker-decision.txt`. Authority: D-150 / MARKER-RULING opening constraints and Consequences; S-1 MANIFEST §4.

```bash
printf '%s\n' "$MARKER_BRANCH" > "$TRANS/080-marker-decision.txt"
```

After freeze x3, successor verification, and fixation, run the reviewed constructor and consumer in explicit **candidate** mode. Candidate-mode tool authentication compares the executing `$INPUT` bytes to the digests already recorded in the reviewed `$INPUT/s0-candidate-manifest.json`; it does not use committed-blob equality and cannot be selected by sidecar presence. The S-0 marker stays outside the Git worktree. Authority: MARKER-RULING split S-5 and Consequences; S-1 MANIFEST §§6 and 9.1 G-4.

```bash
mkdir -p "$CUSTODY/marker-candidate"
"$PY" "$INPUT/build_family_marker.py" \
  --repository "$CLONE" --head "$FIXATION_COMMIT" \
  --pack-root "${PACKS[0]}" --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" \
  --output "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$INPUT/s0-candidate-manifest.json" \
  > "$TRANS/081-marker-build.json"
"$PY" "$INPUT/verify_family_marker.py" \
  --repository "$CLONE" \
  --marker "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$INPUT/s0-candidate-manifest.json" \
  > "$TRANS/082-marker-verify.json"
FORGED_ORIGIN_MAIN_OID=$(git -C "$CLONE" rev-parse refs/remotes/origin/main)
"$PY" - "$TRANS/082-marker-verify.json" "$FORGED_ORIGIN_MAIN_OID" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"] == "PASS"
assert d["phase"] == "candidate" and d["lane"] == "candidate"
assert d["gate_admissible"] is False and d["publication_authorized"] is False
assert d["consulted_git"]["origin_main_commit"] == sys.argv[2]
PY
printf 'FORGED_ORIGIN_MAIN_OID=%s\nclassification=forged-ref-conditional; not published PASS\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/084-local-green-classification.txt"
```

Expected marker schema: `joulewise.d117_family_publication_marker.v1`, all three exact pack IDs, `freeze-0004` receipt IDs/hashes, common Git head/tree, and candidate consumer PASS. The verification transcript must carry `lane: "candidate"` and `gate_admissible: false`; a candidate receipt can never gate publication. Authority: MARKER-RULING ratified items 1–3 and S-4, plus Consequences (`lane` / `gate_admissible`); D-151 condition 4.

The marker and successor are the two immutable consumers of the unified table `joulewise.d117_step6_confirmation_table.v1`. The table is custody-external and has exactly the two edges `C → M` and `C → S`; its path is an authenticator and never enters any allowlist. The lead renders the exact canonical candidate table and GNU sidecar according to the ONE HOME, `docs/contracts/d117_step6_confirmation_table.md`, presents digest `hC` to Ed, and stops until Ed’s YES names that digest. The literal YES is already in the immutable bytes Ed hashes; no timestamp or self-digest is added. Authority: MARKER-RULING ratified item 2; D-151 conditions 2 and 7.

```bash
STEP6_CANDIDATE="$CUSTODY/step6-candidate/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_CANDIDATE"
test -f "$STEP6_CANDIDATE.sha256"
# ED_STEP6_CONFIRMED_SHA256 is transcribed from Ed's out-of-band YES over hC.
test -n "${ED_STEP6_CONFIRMED_SHA256:-}"
test "$(shasum -a 256 "$STEP6_CANDIDATE" | awk '{print $1}')" = \
  "$ED_STEP6_CONFIRMED_SHA256"
"$PY" - "$CLONE" "$STEP6_CANDIDATE" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$SUCCESSOR_PINSET" "$FIXATION_COMMIT" <<'PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]); table_path=pathlib.Path(sys.argv[2])
marker_path=pathlib.Path(sys.argv[3]); successor=sys.argv[4]; head=sys.argv[5]
from joulewise import arm_readiness as r
raw=table_path.read_bytes(); table=r.validate_step6_confirmation_table(
 r.parse_json_bytes(raw, require_canonical=True))
assert table_path.with_name(table_path.name+".sha256").read_bytes() == r.gnu_sidecar(
 hashlib.sha256(raw).hexdigest(), table_path.name)
assert table["git"]["head_commit"] == head
assert table["registry"]["registry_id"] == "d117-row-registry-v2"
assert table["registry"]["path"] == "configs/arm_readiness/d117_row_registry_v2.json"
assert table["family_publication"]["marker"]["sha256"] == hashlib.sha256(marker_path.read_bytes()).hexdigest()
assert table["successor_pinset"]["path"] == successor
assert table["successor_pinset"]["sha256"] == hashlib.sha256((root/successor).read_bytes()).hexdigest()
assert table["successor_pinset"]["pack_count"] == 3
assert table["successor_pinset"]["receipt_count"] == 33
PY
printf '%s\n' "$ED_STEP6_CONFIRMED_SHA256" > "$TRANS/085-ed-step6-confirmed-sha256.txt"

PUBLISHED_DIR="$CUSTODY/windows/family_publication"
mkdir -p "$PUBLISHED_DIR"
cp -p "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json.sha256" \
  "$PUBLISHED_DIR/"
cp -p "$STEP6_CANDIDATE" \
  "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json"
cp -p "$STEP6_CANDIDATE.sha256" \
  "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json.sha256"
cmp "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$PUBLISHED_DIR/d117_family_publication_v4.json"
cmp "$STEP6_CANDIDATE" \
  "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json"
```

Promotion copies exact immutable bytes; it never edits either consumer or the table. The reviewer now recomputes the successor digest/counts from the committed blob, compares them both to the fixation assertions and to `table.successor_pinset`, and records the match. A mismatch is a mechanism failure, not an invitation to reseal. Authority: D-151 conditions 2–3; MARKER-RULING ratified items 1–2.

### 3.9 Arm and verify all three after window closure and fixation

The exact 112 window was already closed at `WINDOW_CLOSE_HEAD` in §3.7; the post-window fixation commit does not retroactively enlarge it. This clone proof may arm only after the exact marker and Ed-confirmed table have been placed in `$CUSTODY/windows/family_publication`. Any arm/verify result here is non-claim-bearing and forged-ref-conditional; publication acceptance is the separate published-green step below. Authority: D-151 conditions 3–5 and 8; MARKER-RULING ratified item 3.

```bash
FINAL_HEAD=$(git -C "$CLONE" rev-parse HEAD)
test "$FINAL_HEAD" = "$FIXATION_COMMIT"

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

### 3.10 Two-part green record — local conditional, then PUBLISHED

After the §7 open-finding disposition has been applied by its owning independent seat *(the S0-BLOCKED flip precondition is STRUCK 2026-08-23 — see §5.1)*, run the complete local suite. Record the forged remote-ref OID beside the result. Even when return code 0, this transcript’s classification is **`LOCAL GREEN — FORGED-origin/main-CONDITIONAL at <OID>`**; neither its filename nor its prose may say “suite green” or “published green.” Authority: D-151 condition 4; S-1 MANIFEST §§5, 9.3, and 9.5.

```bash
test "$(git -C "$CLONE" rev-parse refs/remotes/origin/main)" = "$FORGED_ORIGIN_MAIN_OID"
cd "$CLONE"
set +e
"$PY" -m unittest discover -s tests \
  > "$TRANS/093-local-forged-ref-conditional.txt" 2>&1
LOCAL_SUITE_RC=$?
set -e
test "$LOCAL_SUITE_RC" = 0
printf 'classification=LOCAL GREEN — FORGED-origin/main-CONDITIONAL\noid=%s\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/094-local-green-classification.txt"
```

Acceptance does **not** close here. After the lead actually publishes the accepted fixation head, a clean checkout must prove strict four-way equality (publication head == HEAD == local main == `origin/main`), run the complete suite against that real published ref, and record `PUBLISHED GREEN` with its OID in separate immutable custody. Candidate marker verification from §3.8 is not reusable: publication verification must use the Ed-confirmed table, committed-blob tool equality, semantic replay, and a transcript with `lane: "published"` and `gate_admissible: true`. No S-0 clone command may forge that claim. Authority: D-151 condition 4; MARKER-RULING ratified items 2–3 and split S-1.

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
reg=json.load(open("configs/arm_readiness/d117_row_registry_v2.json"))["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]
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

Before this block, write the exact registry list to `010-candidate-exact.json`. Pass iff the three reports respectively name `candidate_missing`, `candidate_extra`, and `unused_allowlist`, all with exit 2. The registry is the RULED live coordinate: outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`; the candidate authors the previously absent `freeze_evidence_lifecycle.irrelevant_path_allowlist` key there. Authority: REGISTRY-V2 RULING (`MAGISTRATE-RULING.md:124-131`); D-151 condition 8 and Consequences; R4 r4-2; R5 V-1.v.

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
 p=a.repo/"configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"; d=json.loads(p.read_text())
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
| successor pinset JSON (1) | change one governed `_v4` row’s `plan_sha256` | a `histsem_*_mismatch` refusal and a C→S digest-condition refusal; after fixation, byte-only tamper must also fail the new successor SHA assertion |

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

Pass iff **all eight** classes refuse through an independent digest, binding, or semantic replay authenticator. For the successor class, the Ed-confirmed C→S edge is load-bearing and “the test run itself” is never an authenticator. If any class has no such authenticator, apply V-1.vi’s digest-conditional subtraction rule: it may not remain a static allowlist subtraction; remove that class from the candidate allowlist and bind it in the authenticated derived manifest, then reopen the mechanism proof. Authority: D-151 conditions 2–3; R5 V-1.iv, V-1.vi, V-1.vii; RH-8; semantic replay `arm_readiness.py:6161-6185`.

### 4(e.1). Digest-conditional successor subtraction — actual C→S edge

The synthetic unit probe and the transaction probe are both mandatory. The focused class must prove: the exact confirmed digest subtracts the successor; no table, an absent or invalid table, a wrong path, a wrong digest, and any later successor rewrite all refuse with the pre-existing `DEPENDENCY_CHANGED_SET` role; and `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` is exactly the successor path. Authority: D-151 condition 2; S-1 MANIFEST §§8.2 condition 2 and 9.1 G-2.

```bash
cd "$CLONE"
"$PY" -m unittest -v \
  tests.test_receipt_histsem.SuccessorPinsetDigestConditionTests \
  > "$TRANS/122-c-to-s-unit-probes.txt" 2>&1

# Transaction PASS side: §3.9's 091-* arms use Ed's exact table at
# $CUSTODY/windows/family_publication and must contain no R1 changed-set code.
for p in "$TRANS"/091-arm-*.stdout.json; do
  ! grep -F "$CHANGED_CODE" "$p"
done

# Transaction refusal side: keep Ed's table fixed, mutate the committed
# successor bytes at a later reviewed head, and require DEPENDENCY_CHANGED_SET.
CASE=$(new_case c-to-s-later-rewrite "$PROBE_BASE")
printf '\n' >> "$CASE/$SUCCESSOR_PINSET"
commit_case "$CASE" 'S-0 C-to-S probe: later successor rewrite'
capture 123-c-to-s-later-rewrite "$PY" "$CASE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CASE/${PACKS[0]}" --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$CUSTODY/windows"
grep -F "$CHANGED_CODE" "$TRANS/123-c-to-s-later-rewrite.stdout.json"
no_traceback 123-c-to-s-later-rewrite
```

Pass iff the valid transaction crosses the changed-set gate only against Ed’s exact table digest, while the later committed rewrite is refused by `DEPENDENCY_CHANGED_SET` before it can be forgiven by allowlist membership. The table and its sidecar are immutable during the probe. Authority: D-151 condition 2; `docs/contracts/d117_step6_confirmation_table.md` “Where the `C → S` edge is enforced.”

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

Present was captured at `071-histsem-present` and must PASS before arm; because this clone’s reviewed ref is forged, that PASS is local/conditional, not published green. Explicit absence is exercised without deleting or touching a real checkout. Authority for the transcript classification: D-151 condition 4.

```bash
ABSENT="$CASES/definitely-absent-pinset.json"
test ! -e "$ABSENT"
capture 130-histsem-absent "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --pinset "$ABSENT" --require-published
expect_rc 130-histsem-absent 2
grep -F 'histsem_pinset_absent' "$TRANS/130-histsem-absent.stdout.json"
```

Then rerun §4(d) missing/extra/unused with the 112 literal. Pass iff the closed v1→successor chain verifies, arms cross the actual changed-set gate only under the confirmed C→S condition, explicit absence produces `histsem_pinset_absent`, and all three malformed candidate variants fail. D-151 condition 6 preserves the rule-11 clarification unchanged: an absent enumerated member does not tighten the library’s default HEAD-absence semantics; only this explicit CLI/worktree verifier path promises `histsem_pinset_absent`. Authority: D-151 conditions 2 and 6; RH-8 and normative annexes; HISTSEM-CONTRACT “Failure semantics”; `verify_receipt_histsem.py:22-73`; `tests/test_receipt_histsem.py:62-80`.

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

- [ ] **r4-2** — One full three-pack sequence is evidenced by `030-*`, `032-*`, `040-*`, `042-*`, `050-*`, `060-*`, `061-*`, `070-*`–`073-*`, `080-*`–`085-*`, `090-*`, `091-*`, and `092-*`; every pack crosses the actual changed-set gate; ordinary path, unexpected output, both plan-tree directions, candidate-shape triplet, C→S, and poison probes adjudicate as specified.
- [ ] **V-2** — Lead/magistrate custody and nondelegation are recorded in `001-*` through `004-*`; S-6 both validators are `120-*`/`121-*`; governed arm+verify and every transcript have been read with no fail-ugly traceback.
- [ ] **V-1.vi / D-151 C→S** — All eight path classes in `110-*` through `118-*` have independent tamper refusals, including the two manifest halves; `122-*`/`123-*` prove that successor subtraction is conditional on Ed’s exact table digest and that a later rewrite refuses; any unauthenticated class has triggered the derived-manifest reopen rather than being waived. Authority: D-151 condition 2.
- [ ] **rh-8 / D-151 successor** — The 112 arithmetic and exact window-close contract are PASS in `010-*`/`090-*`; present chain and arm crossing are `071-*`/`091-*`; explicit CLI absence is `130-*`; missing/extra/unused are `105-*`–`107-*`; all three `_v4` rows and local-Git provenance are in the create-only successor at `070-*`; the v1 member is byte-unchanged; fixation is the first post-window commit. Authority: D-151 conditions 1–3 and 6.
- [ ] **D-150 marker** — Only `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL ran; candidate transcript `082-*` says `lane: candidate`, `gate_admissible: false`, and names the forged OID; the marker, table, and authenticators are absent from every allowlist. Authority: MARKER-RULING opening constraints, ratified item 2, and Consequences.
- [ ] Candidate patch and sidecar, binding manifest, all four custody tools and sidecars, marker decision, HEADs, Git statuses, and complete stdout/stderr/exit-code triplets are present under the custody root. Candidate-mode executing bytes match the reviewed `$INPUT` manifest digests. Authority: S-1 MANIFEST §§2.4, 4, 6, and 9.1 G-1/G-4.
- ~~S0-BLOCKED addendum~~ **STRUCK 2026-08-23 by magistrate ruling** (recorded in the S-1 fix-round packet and MANIFEST §9.3): the 21-method flip theory was DISPROVEN BY MEASUREMENT — the partition is S0-BLOCKED 0 / STRUCTURAL 17 / CRASH 4; none flips on the S-0 mint. S-0 acceptance is the proving-obligations checklist above ALONE. The 17 structural entries ride kernel row A84 (FIXTURE-MODERNIZATION-01) and the 4 crash entries A85 (MLX-ACID-SIGABRT-01, which also requires A84).
- [ ] **Two-part green** — `093-*`/`094-*` are recorded only as local forged-`origin/main`-conditional with the exact forged OID; a separate clean, strict-four-way real-ref run records PUBLISHED GREEN before acceptance closure. No transcript calls local green “suite green.” Authority: D-151 condition 4.
- [ ] No command touched or read `/Users/edr/JouleWise-measurement-20260818`; no quiet-Mac measurement, freeze outside the clone, dry-run, arm launch, consume, or publication occurred.

### 5.1 S0-BLOCKED set — STRUCK 2026-08-23 (historical text preserved below; see the struck checklist entry for the ruling and the A84/A85 rows that own these tests now; the markers are unittest.skip, not expectedFailure, since the fix round)

Each method arrived at S-0 marked `@unittest.expectedFailure` with the reason `S0-BLOCKED: requires minted _v4 packs`. In the reviewed post-window activation delta, remove that expected-failure status only when the fixture is rebound to the minted family; then require an ordinary PASS. A method that passes before S-0 mint is itself a finding. The exact acceptance set is:

- `tests/test_arm_readiness_evidence_t0.py` (7): `test_arm_consumes_volatile_receipts_within_short_horizon`, `test_mocked_forbidden_process_evidence_expires_before_arm`, `test_forbidden_process_started_after_authoring_expires_before_arm`, `test_acid_authored_fifteen_then_real_arm_generator_reaches_go`, `test_acid_real_boot_session_then_real_arm_generator_reaches_go`, `test_synthetic_acid_is_hermetic_to_system_timezone`, `test_synthetic_acid_ignores_wall_clock_48_hours_in_future`. Authority: S-1 MANIFEST §9.3.5, “Dominant cause — V1_GRANDFATHERING.”
- `tests/test_arm_readiness_integration.py` (5): `test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle`, `test_same_head_pack_terminal_evidence_and_final_arm_bindings_go_stale`, `test_verification_recomputes_current_pack_bytes_despite_skip_worktree`, `test_missing_arm_only_evidence_refuses_and_bound_source_mutation_stales_go`, `test_identity_arm_evidence_symlink_escape_refuses`. Authority: S-1 MANIFEST §9.3.5, “Dominant cause — V1_GRANDFATHERING.”
- `tests/test_arm_readiness_dry_run.py` (4): `test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots`, `test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change`, `test_dry_run_refuses_a_dirty_or_nonreviewed_checkout`, `test_dry_run_rehearsal_root_and_id_are_single_use`. Authority: S-1 MANIFEST §9.3.5, “Dominant cause — V1_GRANDFATHERING.”
- `tests/test_arm_readiness_lifecycle.py` (4): `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`, `test_boot_session_change_voids_verification_and_consumption`, `test_self_wrong_role_and_ordinal_violations_refuse`, `test_historical_predecessor_resolves_and_still_anchors_the_chain`. The first two are V1_GRANDFATHERING; the third is the marker-first gate-shadowing case; the fourth is the `_v4`/`_v3` historical-pairing case. Authority: S-1 MANIFEST §9.3.5, dominant-cause list plus “Gate shadowing” and “Historical pairing.”
- `tests/test_d117_decode_contrast_plan.py` (1): `test_authenticated_freeze_transition_preserves_frozen_bytes`, the intervening-generator-chain case. Authority: S-1 MANIFEST §9.3.5, “Generator chain.”

Run the manifest-declared exact-method command and preserve its verbose transcript as `095-s0-blocked-21-green.txt`; a module-only aggregate that does not identify all 21 is insufficient. Authority: S-1 MANIFEST §9.3.5.

# 6. FAILURE SEMANTICS

**Mechanism failures — trip V-1.vi and REOPEN to the derived authenticated manifest:** an ordinary nonallowlisted path crosses; an unexpected evidence output is accepted; either current or sibling coherent non-freeze plan mutation crosses R1; any missing/extra/unused candidate variant is accepted; any one of the eight allowlisted classes lacks an independent tamper authenticator; either `DEPENDENCY_MANIFEST` half crosses; S-6’s R1 validator crosses; the successor contains a cross-member duplicate, is subtracted without the exact C→S edge, remains forgiven after a later rewrite, or differs from Ed’s confirmed digest; an authenticator enters an allowlist; histsem present does not gate arm/freeze; explicit-CLI absence does not produce `histsem_pinset_absent`; or a refusal mint partially writes, fails ugly, or cannot be safely screened by the sacrificial preflight. A candidate-lane receipt with `gate_admissible:true`, or any local-green transcript presented as published/suite green, is also a mechanism failure. The response is not “fix a test expectation”: derive an authenticated manifest, remove every unauthenticated subtraction, rerun all of S-0, and preserve the failed transcript. Authority: D-151 conditions 2, 4, 6, and 7; MARKER-RULING ratified item 2; R5 V-1.vi, V-1.vii, V-2; R4 r4-2; RH-8.

**Ordinary defects — fix and restart the affected clean case or the whole transaction as indicated:** wrong CLI spelling, missing custody input, sidecar checksum mismatch, malformed probe fixture that fails before reaching its intended gate, transcript collision, or a legitimate non-S-0 T0/refusal after all lifecycle gates crossed. A primary freeze REFUSE is recoverable only by abandoning that primary clone and restarting from the committed evidence state because §4(i) proves it is plan-pinned. A baseline candidate test failure, unresolved `ED_RESERVED:` value, line-audit mismatch, 11/112 count mismatch, or dirty reviewed tree is a precondition defect: stop before mint, correct the reviewed candidate, and start again. Authority: R4 r4-2, r4-3, r4-5; R5 S-6, V-1, V-2.

# 7. RESOLVED R1 ITEMS AND ACTIVE CAUTIONS

### O-1 — RESOLVED by D-151

O-1-D is controlling: the successor path replaces v1 in the 112-member contract; S-0 mints into the successor; subtraction is conditional on Ed’s unified-table C→S edge; and fixation is the first commit after window close. The refuted 113-path/test-source option is not an alternate lane. Authority: D-151 Ruling and Consequences.

### O-2 — RESOLVED by D-150 / marker ruling

The sole branch is BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with no tracked marker paths and a 112-path contract. The prior alternative branch is absent from R2. Authority: D-150 / MARKER-RULING opening constraints and Consequences; S-1 MANIFEST §4.

### O-3 — reviewed-candidate custody remains a hard precondition

The S-1 worktree is at `c1b87f63fd47507dd1504693ad45347a4f2c55aa`, but its manifest still says the candidate is not lead-reviewed or accepted; §9 is the implementing seat’s self-report and its independent finish-round audit is outstanding. The four tool sidecars exist, while `s0-candidate.patch[.sha256]` remains a deliberate lead export at gauntlet close. S-0 starts only when the accepted patch, manifest, and all four tool/sidecar pairs are in `$INPUT`; it may verify and execute them but never invent them. Authority: S-1 MANIFEST status, §§6, 9.1, and closing provenance.

### O-4 — S-0-visible caution: §9.3.6 re-derivation finding is not in S0-BLOCKED

Four `tests/test_arm_readiness_evidence_author.py` methods remain ordinary failures, not expected failures and not members of the 21-test addendum:

- `test_source_tamper_refuses_without_overwriting_any_receipt` expects `"invalid"` but reaches `reviewed HEAD changed relevant path(s)`.
- `test_coordinated_source_receipt_rewrite_refuses_without_overwrite` expects `"differs from freshly derived bytes"` but reaches the same HEAD-change gate.
- `test_authoring_is_deterministic_valid_and_boot_bound` reaches `untracked pack directory: b'arm_readiness.evidence'`.
- `test_authored_evidence_makes_synthetic_pack_freeze_pass` reaches `ARM re-derivation refused: primary artifact is not byte-identical to HEAD: configs/campaigns/d117_floor_qwen25_1p5b_v4/plan_tree.json`.

The implementing seat staged the coherent-rewrite adversary through four successive barriers: untracked authored evidence; disk/committed source mismatch; reviewed HEAD moved; then, even after advancing `refs/remotes/origin/main`, all 33 authored source/evidence paths still counted as reviewed-HEAD changes. Its recorded finding is therefore that authoring/ARM re-derivation refusals appear unreachable from a fixture because an earlier HEAD-comparison gate always owns the case. Whether this is a candidate defect (gate too broad and semantic re-derivation swallowed) or a contract disposition (HEAD custody legitimately subsumes re-derivation under R1) belongs to the gauntlet’s independent seat. S-0 does not relabel these four as S0-BLOCKED, does not force them green by weakening assertions, and cannot record either local or PUBLISHED green until the owning disposition is applied. Authority: S-1 MANIFEST §9.3.6 in full.
