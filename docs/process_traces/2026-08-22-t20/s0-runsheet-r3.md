# S-0 CLONE-PROOF RUNSHEET R3 — JouleWise `_v4` transaction

This is a bench runsheet, not an execution transcript. The magistrate executes
it in the throwaway clone defined in §1.1 and reads every transcript. It never
uses or reads `/Users/edr/JouleWise-measurement-20260818`.

R3 supersedes `s0-runsheet-r2.md`. R2 and its three dated amendment blocks are
retained unchanged as the record; nothing in them binds execution any more.

---

## Revision history

**r3 (2026-08-24).** A clean instrument. Amendments 1–3 are folded into the
body text — there are no amendment blocks below — and the fourteen findings of
the R-3 executability audit are cured. Binding records:

| Record | Custody path (2026-08-24 session) | What it settled |
|---|---|---|
| Packet 1 + 2 syntheses | `custody/transcripts/006`–`013` | registry-v1 census scope (the hyphen-form id constant is CORRECT ARCHIVAL RETENTION); the §1.3 classification fence (mechanical classification only; in-clone doc edits FORBIDDEN) |
| Packet 3 synthesis | `custody/transcripts/034`–`036` | U11 environment: remedy (a''), §3.2 runs under the pinned host measurement venv, read-only, zero installs anywhere; fresh estate; one-command-per-shell execution discipline |
| Custody anomaly | `custody/transcripts/035` | transcripts 031/032 of the r2 estate are VOID; compound scripts swallowed the failing gate assertions |
| Executability audit verdict | `custody/transcripts/037` | F-1…F-14; full cold re-ratification made mandatory; the instrument advances to r3 |

### What changed from r2 to r3

1. **Execution contract (F-4, F-5, R-5).** A new §0.1 states the shell contract:
   the executing shell is **zsh 5.9 with 1-based arrays**, and **no shell state
   survives between tool invocations**. Every variable, array and helper now
   lives in `$PROOF/env.sh`, written once in §1.1 and re-sourced by every
   command block. Every `for i in 0 1 2` / `${PACKS[0]}` construct is gone,
   replaced by value iteration and named pack variables. Every gate assertion
   inside a loop carries an explicit `|| die` instead of relying on `set -e`,
   which the 035 anomaly proved is not reliable inside compound constructs.
   `$MARKER_BRANCH` is read from the candidate manifest in `env.sh`.
2. **Custody tools execute from the clone (F-1).** §3.7 and §3.8 invoke
   `$CLONE/scripts/<tool>.py`, never `$INPUT/<tool>.py`. Each tool sets
   `REPO_ROOT = Path(__file__).resolve().parents[1]`, so a copy outside the
   repository cannot `import joulewise` at all. A new §3.6.1 pre-execution step
   asserts each executing file's SHA-256 against the manifest's `custody_tools`
   digest before any tool runs, so the split S-5 lane rule is preserved
   verbatim: candidate mode authenticates the executing bytes against a
   document written before execution, never against a self-recomputed sidecar.
3. **The fixation delta now exists (F-2).** `s0-fixation-delta.patch` and its
   GNU sidecar are committed beside this runsheet, digest-bound in the
   candidate manifest, and applied in §3.7 **before** the step that runs
   `tests.test_receipt_histsem`. R2 sequenced the apply after the suite run and
   named a delta that had never been authored; that combination made the step-6
   suite red by construction.
4. **§4(h) probes what it claims to probe (F-3).** An out-of-enumeration
   `--pinset` override refuses `histsem_pinset_invalid`, not
   `histsem_pinset_absent` (`arm_readiness.py:3176-3187`, and the committed
   `tests/test_receipt_histsem.py:146-165` asserts exactly that). The probe now
   runs inside a `new_case` clone where the enumerated successor member has been
   `git rm`'d and is passed as `--pinset`, which is the only path that reaches
   the `present == 0` branch at `arm_readiness.py:3223-3227`.
5. **§4(b) targets a reachable signal (F-6).** `arm` discovery runs with
   `include_pack=False` (`arm_readiness.py:7383`), so an unexpected file in the
   *pack's* evidence directory is invisible to it. The probe is now two probes:
   4(b.1) puts the unexpected file in the **window-custody** evidence namespace,
   which `arm` does scan; 4(b.2) puts it in the **pack** namespace and freezes
   from a case at `$EVIDENCE_COMMIT`, the mint path, where `include_pack`
   defaults to true.
6. **§3.3 names its tests honestly (F-7).** The §1.3 manifest now carries a
   mechanically generated `test_modules` array; §3.3 asserts the manifest
   declares exactly the two modules it runs.
7. **§5 matches the superseded-by-merge reality (F-8).** The acceptance box that
   demanded a candidate patch, four tool sidecars and a `$INPUT` tool set now
   demands the mechanical manifest, the clone-tool digest equalities, the
   fixation-delta digest equality, and the clone provenance line.
8. **Notes folded.** §4(g) states the governed-nonzero alternative as an
   admissible outcome (F-9). §3.9 tolerates `receipt_path: null` on an early
   governed refusal (F-12). `$SESSION` is an operator input, not a literal
   (F-13). The §1.3 sweep uses `grep -E`; there is no `rg` binary on this bench
   (F-14).
9. **Anchor map machine-checked.** The thirteen-anchor map was verified 13/13 at
   `d19df05` by the audit; §0.2 restates it and adds a mechanical re-check
   against `$BASE` so drift stops being a prose claim. The pinned mechanics map
   is re-derived at the same head, so the r2 wart "where this map and an inline
   citation disagree, THIS MAP governs" is gone: they agree.
10. **`$BASE` selection is a gate, not a literal.** R2 pinned `1ba04a8` and then
    overrode it in prose. §1.1 instead takes the green head as an operator input
    and gates it mechanically: it must contain this delta's exact bytes, the four
    custody tools, the v2 registry, and none of the `_v4` output.

---

# 0. HOW TO EXECUTE THIS INSTRUMENT

### 0.1 Execution contract — read before running anything

**The shell.** Commands run under **zsh 5.9**. Two consequences bind every
block below:

- **Arrays are 1-based.** `${PACKS[0]}` is the empty string, not the first
  pack. In r2 that silently dropped the third pack from every
  `for i in 0 1 2` loop and made every gate assertion after the first a no-op.
  R3 contains no numeric array indexing at all: loops iterate values
  (`for pack in "${PACKS[@]}"`), and the three packs also have named variables
  (`$FIRST_PACK`, `$SECOND_PACK`, `$THIRD_PACK`) for the places that need one
  pack by name.
- **`set -e` is not trustworthy inside compound constructs.** Custody 035
  records a `for` loop that continued past failed assertions and then wrote
  later steps' evidence with the wrong head. Every assertion in r3 therefore
  ends in `|| die '<message>'`. `die` prints and exits; it never depends on
  the shell's errexit context.

**No state survives between command blocks.** Each block below runs in a fresh
shell: exported variables, shell functions and `cd` are all gone by the next
block. Therefore:

- **`$PROOF/env.sh` is the single home of execution state.** §1.1 writes it
  once. It contains `set -euo pipefail`, every path variable, the pack arrays,
  and the helper functions. Heads computed mid-transaction
  (`$S0_BOOTSTRAP_HEAD`, `$EVIDENCE_DERIVATION_HEAD`, `$EVIDENCE_COMMIT`,
  `$FREEZE_COMMIT`, `$WINDOW_CLOSE_HEAD`, `$FIXATION_COMMIT`,
  `$FORGED_ORIGIN_MAIN_OID`, `$PROBE_BASE`) are **appended** to it by
  `record_env` at the moment they are computed.
- **Every command block below begins with the literal line**

  ```zsh
  source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
  ```

  Before pasting a block, prepend the one-line assignment that §1.1 writes into
  `$TRANS/000-source-line.txt` (it reads `S0_ENV=/abs/path/to/env.sh`). A block
  pasted without it aborts immediately on the `:?` guard. That abort is the
  guard working; it is never a reason to improvise the missing state.
- **One command block per shell invocation.** Do not concatenate two blocks
  into one call, and do not wrap a block in an outer script. This is R-5 of the
  packet-3 ruling and it is the direct cure for the 035 defect class.

**`record_env` refuses to redefine a name.** If a head is already recorded,
`record_env` stops rather than shadowing the earlier value. A re-run that trips
this is telling you the estate is no longer clean: start a fresh estate (§6),
do not delete the line.

**Transcripts.** Every tool run is captured as a stdout/stderr/rc triplet under
`$TRANS`. The magistrate reads every one. Authority: R4 r4-2; R5 V-2.

### 0.2 Anchor map — verified 13/13 at `d19df05`

The R-3 executability audit verified all thirteen anchors at `d19df05`
(2026-08-24). They are the drift tripwire for every inline citation in this
runsheet; §1.1 re-checks them mechanically against `$BASE` before any
transaction work.

| # | File | Line | Expected content at that line |
|---|---|---|---|
| 1 | `joulewise/arm_readiness.py` | 1050 | `class EvidenceLifecycleError(ValueError):` |
| 2 | `joulewise/arm_readiness.py` | 2025 | `- set(lifecycle["irrelevant_path_allowlist"])` |
| 3 | `joulewise/arm_readiness.py` | 3639 | `def _gate_receipt_histsem(pack_root: Path, *, require_published: bool = False) -> None:` |
| 4 | `joulewise/arm_readiness.py` | 4115 | `def _r1_changed_paths(` |
| 5 | `joulewise/arm_readiness.py` | 4300 | `allowlist = set(governed["irrelevant_path_allowlist"])` |
| 6 | `joulewise/arm_readiness.py` | 5266 | `def _authenticate_generic_evidence_item(` |
| 7 | `joulewise/arm_readiness.py` | 6265 | `def _load_freeze_reference(` |
| 8 | `joulewise/arm_readiness.py` | 6531 | `def generate_freeze_receipt(` |
| 9 | `joulewise/arm_readiness.py` | 6572 | `generation = _pack_generation(root.name)` |
| 10 | `joulewise/identity_pins.py` | 1826 | `def freeze_projection(pack_root: Path \| str) -> Mapping[str, Any]:` |
| 11 | `scripts/generate_arm_readiness.py` | 28 | `def _parser() -> argparse.ArgumentParser:` |
| 12 | `scripts/project_identity_pins.py` | 23 | `def parse_args(argv: list[str] \| None = None) -> argparse.Namespace:` |
| 13 | `scripts/verify_receipt_histsem.py` | 22 | `def _parser() -> argparse.ArgumentParser:` |

### 0.3 Pinned mechanics map — re-derived at `d19df05`

R2 carried ranges pinned at `1ba04a8` that had wholly drifted, plus a rule
saying the header map won on disagreement. R3 removes the disagreement: every
range below was re-derived at `d19df05` by symbol extraction, and every entry
names its symbol so the next drift is detectable by name rather than by line.

- R1 `EvidenceLifecycleError` is a `ValueError`, not an `ArmReadinessError`:
  `joulewise/arm_readiness.py:1050-1076`.
- Registry cross-check of conditional paths inside `validate_registry`:
  `:1999-2120` (the allowlist subtraction line is `:2025`).
- Histsem pinset chain loader `_load_histsem_pinset`: `:3168-3228`; the
  **only** promise of `histsem_pinset_absent` is its `present == 0` branch at
  `:3223-3227`; the out-of-enumeration override refuses
  `histsem_pinset_invalid` at `:3184-3187`.
- Whole-corpus verifier `verify_all_receipt_histsem`: `:3605-3636`.
- Freeze/arm histsem gate `_gate_receipt_histsem`: `:3639-3707`; its two call
  sites are freeze `:6556` and arm `:7319`.
- Changed-set enumeration `_r1_changed_paths`: `:4115-4163` (its
  `DEPENDENCY_CHANGED_SET` refusals at `:4148` and `:4160`).
- Dependency-manifest helper `_r1_manifest_dependencies` and the
  digest-conditional confirmed-path requirement
  `_require_confirmed_conditional_path`: `:4166-4253`.
- R1 primary gate `validate_r1_evidence_lifecycle`: `:4256-4399`. Allowlist
  subtraction plus conditional-path logic `:4300-4322`; manifest binding
  half 1 (source/receipt) `:4324-4341`; half 2 (nonempty/canonical plus
  derivation and current dependency) `:4342-4399`.
- Issued-acceptance census `_issued_d079` and the row-applicability rule that
  consumes it: `:5214-5254`.
- Evidence-directory namespaces `_evidence_directories`: `:5257-5263` — the
  `WINDOW_CUSTODY` namespace appears only when the custody pack root differs
  from the pack root, which is why §4(b) is two probes.
- Generic-item authentication `_authenticate_generic_evidence_item`:
  `:5266-5485` (its R1 refusals at `:5436`, `:5460`, `:5481`).
- Evidence discovery `_discover_evidence`: `:5488-5743`; the unexpected-output
  rejection is `:5514-5541`; `include_pack` defaults true and is passed False
  by arm `:7383` and verify `:7616`.
- Predecessor authentication and semantic replay
  `_authenticate_freeze_predecessor`: `:6098-6224`; predecessor derivation
  `_derive_freeze_predecessor`: `:6227-6262`.
- Freeze reference load / idempotent replay `_load_freeze_reference`:
  `:6265-6475`.
- `generate_freeze_receipt`: `:6531-6807`; generation gate `:6572`; the new
  mint unconditionally writes and plan-pins PASS **or** REFUSE at `:6760-6806`.
- `generate_arm_receipt`: `:7307-7553`; governed arm receipt construction and
  external write `:7519-7553`.
- Candidate/production tool-authentication lane `_family_tool_reference`:
  `:10207-10261`; the manifest digest reader `_candidate_manifest_tool_digest`:
  `:10160-10204`; marker construction `build_family_publication_marker`:
  `:10370-10514` (it writes the marker **and** its GNU sidecar at `:10502-10503`).
- U11 projection `joulewise/identity_pins.py:1826-1935`.
- Generic applicability rows `joulewise/arm_readiness_evidence.py:1709-1731`;
  authoring implementation `:2379-2618`.
- CLIs: freeze/arm/verify `scripts/generate_arm_readiness.py:28-186` (exit
  semantics `:169-186`: 0 PASS, 1 governed REFUSE, 2 raised
  `ArmReadinessError`); identity U11 `scripts/project_identity_pins.py:23-60`;
  histsem `scripts/verify_receipt_histsem.py:22-73`; evidence author
  `scripts/author_arm_readiness_evidence.py:25-112`.
- Generator preserve-mode echo hole
  `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1942-1955`;
  its CLI `:2657-2681`.
- Python is `>=3.11`, core dependencies are empty: `pyproject.toml:1-16`. Note
  that `[project.optional-dependencies]` is where `mac` lives — see §1.2.
- The v1 pinset byte pin is `tests/test_receipt_histsem.py:32` and is asserted
  with no update/reseal lane at `:138-145`; the explicit-override CLI refusal
  test at `:146-165` expects `histsem_pinset_invalid`.

### 0.4 Binding-source shorthand

- **R4** = `docs/process_traces/2026-08-20-go-session/v4-plan-ruling-r4draft.md`, cited by `r4-N`.
- **R5** = `docs/process_traces/2026-08-20-go-session/rulings-r5-consolidation.md`, cited by `S-N`, `V-1.i`–`V-1.vii`, or `V-2`.
- **RH-8** = `docs/process_traces/2026-08-20-go-session/rh-ruling.md`, item 8 and its normative annexes `rh-terra-debate.md` and `rh-opus-debate.md`.
- **SIT-C3** = `docs/process_traces/2026-08-20-go-session/ready-sitting-ruling.md`, C-3, with `readiness-sitting/seat-L5.md`, F2.
- **MARKER-A1** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md`, A-1.
- **HISTSEM-CONTRACT** = `docs/contracts/receipt_histsem_verifier.md`, especially "Pinset artifact and schema," "Gate integration," "Failure semantics," and "`_v4` transaction sequencing." Its rule-11 absence clarification supersedes the original library-absence wording without changing the explicit-CLI absence probe.
- **D-151** = `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`, adopting O-1-D and its incorporated nine-condition set.
- **D-150 / MARKER-RULING** = `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`; D-150 selects option (a), BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with the changed-set contract remaining 112.
- **REGISTRY-V2 RULING** = `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:124-131`; the RULED live coordinate is outer id `d117-row-registry-v2`, path `configs/arm_readiness/d117_row_registry_v2.json`.
- **S-1 MANIFEST** = `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md`, now merged to main; its §9 was an implementing-seat self-report and was independently reviewed before the merge.
- **PACKET-3 RULING** = `custody/transcripts/036-magistrate-synthesis-packet3.md` of the 2026-08-24 session, R-1 through R-5.
- **AUDIT** = `custody/transcripts/037-executability-audit-verdict.md`, findings F-1…F-14.

### 0.5 Authority for the boundaries

Lead ruling records Ed's mint license as granted, so license is not an S-0
blocker. Execution still stops at the reviewed-custody boundary in §1.3 and at
the Ed-confirmed step-6 publication boundary in §§3.7–3.9. Candidate-lane work
in this clone is never publication. Authority:
`docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`
(D-151 conditions 3–5) and
`docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`
(ratified items 1–3).

---

# 1. CLONE SETUP

### 1.1 Create the proof estate, the commit-exact clone, and `env.sh`

Four operator inputs are substituted into the first block, and only there:

- `SESSION` — the absolute path of this session's scratchpad root. It is an
  input, not a literal: r2 hard-coded a superseded session id.
- `BASE` — the green `main` head to clone. It is gated, not trusted: the
  assertions below require it to contain this instrument's fixation delta bytes,
  the four custody tools, and the v2 registry, and to contain none of the `_v4`
  output.
- `CI_RUN_ID` — the id of the green CI run for `$BASE`, conclusion-field
  verified. It is recorded as half of the provenance line.
- `MEASURE_PY` — the pinned host measurement interpreter (§1.2).

This block runs in Bash **or** zsh; every later block is zsh. It refuses if a
prior proof directory exists; custody and receipts are never reused.

```zsh
set -euo pipefail

SESSION=<absolute path of this session's scratchpad root>
BASE=<green main head SHA that satisfies the gate below>
CI_RUN_ID=<green CI run id for $BASE>

SOURCE=/Users/edr/code/JouleWise
PROOF="$SESSION/s0-clone-proof-r3"
CLONE="$PROOF/repo"
CUSTODY="$PROOF/custody"
TRANS="$CUSTODY/transcripts"
CASES="$PROOF/cases"
INPUT="$PROOF/input"

test ! -e "$PROOF" || { echo 'S-0 STOP: proof estate already exists'; exit 1; }
test "$(git -C "$SOURCE" rev-parse "$BASE^{commit}")" = "$BASE" \
  || { echo 'S-0 STOP: BASE does not resolve in the source repository'; exit 1; }
mkdir -p "$PROOF" "$CUSTODY" "$TRANS" "$CASES" "$INPUT" "$CUSTODY/tools"
git clone --no-local "$SOURCE" "$CLONE"
git -C "$CLONE" checkout --detach "$BASE"
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BASE" || { echo 'S-0 STOP: clone head'; exit 1; }
test -z "$(git -C "$CLONE" status --porcelain=v1)" || { echo 'S-0 STOP: dirty clone'; exit 1; }
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

cat > "$PROOF/env.sh" <<ENVEOF
set -euo pipefail

export SESSION=$SESSION
export SOURCE=$SOURCE
export BASE=$BASE
export CI_RUN_ID=$CI_RUN_ID
export PROOF=$PROOF
export CLONE=$CLONE
export CUSTODY=$CUSTODY
export TRANS=$TRANS
export CASES=$CASES
export INPUT=$INPUT
export PY=$PY
export S0_ENV=$PROOF/env.sh

# The pinned host measurement venv.  READ-ONLY use, in section 3.2 only.
export MEASURE_PY=/Users/edr/code/JouleWise/.venv/bin/python

export REGISTRY=\$CLONE/configs/arm_readiness/d117_row_registry_v2.json
export MANIFEST=\$INPUT/s0-candidate-manifest.json
export DELTA=\$CLONE/docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch
export SUCCESSOR_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json
export BASE_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json

export FIRST_PACK=configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4
export SECOND_PACK=configs/campaigns/d117_floor_qwen25_1p5b_v4
export THIRD_PACK=configs/campaigns/d117_floor_qwen25_7b_v4
PACKS=("\$FIRST_PACK" "\$SECOND_PACK" "\$THIRD_PACK")
typeset -A PRED_OF
PRED_OF=(
  "\$FIRST_PACK"  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
  "\$SECOND_PACK" configs/campaigns/d117_floor_qwen25_1p5b_v3
  "\$THIRD_PACK"  configs/campaigns/d117_floor_qwen25_7b_v3
)

die() { printf 'S-0 STOP: %s\n' "\$*" >&2; exit 1; }

record_env() {
  local name=\$1 value=\$2
  if grep -qE "^export \${name}=" "\$S0_ENV"; then
    die "\$name is already recorded in env.sh; a re-run needs a fresh estate"
  fi
  printf 'export %s=%s\n' "\$name" "\${(q)value}" >> "\$S0_ENV"
}

capture() {
  local label=\$1; shift
  set +e
  "\$@" >"\$TRANS/\$label.stdout.json" 2>"\$TRANS/\$label.stderr.txt"
  local rc=\$?
  set -e
  printf '%s\n' "\$rc" >"\$TRANS/\$label.rc"
}

expect_rc() {
  local label=\$1 expected=\$2
  test "\$(cat "\$TRANS/\$label.rc")" = "\$expected"
}

no_traceback() {
  local label=\$1
  ! grep -Eq 'Traceback \(most recent call last\)|^[A-Za-z]+Error:' \
    "\$TRANS/\$label.stdout.json" "\$TRANS/\$label.stderr.txt"
}

commit_case() {
  local repo=\$1 message=\$2
  git -C "\$repo" add -A
  git -C "\$repo" commit -m "\$message"
  git -C "\$repo" update-ref refs/remotes/origin/main "\$(git -C "\$repo" rev-parse HEAD)"
}

new_case() {
  local name=\$1 commit=\$2 target="\$CASES/\$name"
  test ! -e "\$target" || die "probe case \$name already exists"
  git clone --no-local "\$CLONE" "\$target" >/dev/null
  git -C "\$target" checkout --detach "\$commit" >/dev/null
  git -C "\$target" config user.name 'S-0 probe'
  git -C "\$target" config user.email 's0-probe.invalid'
  git -C "\$target" update-ref refs/remotes/origin/main "\$commit"
  printf '%s\n' "\$target"
}

if [ -f "\$MANIFEST" ]; then
  MARKER_BRANCH=\$("\$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["marker_branch"])' "\$MANIFEST")
fi
ENVEOF

printf 'S0_ENV=%s\n' "$PROOF/env.sh" > "$TRANS/000-source-line.txt"
git -C "$CLONE" rev-parse HEAD > "$TRANS/001-base-head.txt"
git -C "$CLONE" status --porcelain=v1 > "$TRANS/002-base-status.txt"
printf 'head=%s\nci_run_id=%s\nprovenance=merged candidate on main, green CI, conclusion-field verified\n' \
  "$BASE" "$CI_RUN_ID" > "$TRANS/003-clone-provenance.txt"
cat "$TRANS/000-source-line.txt"
```

Paste the line printed at the end as the assignment that precedes every block
from here on.

**`$BASE` gate.** Run next, in its own shell.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# The delta committed at BASE must be byte-identical to the delta this
# instrument was ratified with, proven by its own committed GNU sidecar.
DELTA_REL=docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch
git -C "$CLONE" show "$BASE:$DELTA_REL" > "$TRANS/004-base-delta.patch" \
  || die "BASE does not contain the r3 fixation delta"
DELTA_SHA=$(shasum -a 256 "$TRANS/004-base-delta.patch" | awk '{print $1}')
SIDECAR_SHA=$(awk '{print $1}' "$CLONE/$DELTA_REL.sha256")
test "$DELTA_SHA" = "$SIDECAR_SHA" \
  || die "fixation delta at BASE does not match its committed sidecar"

for tool in \
  scripts/build_v4_histsem_pinset.py \
  scripts/build_family_marker.py \
  scripts/verify_family_marker.py \
  scripts/verify_receipt_histsem.py
do
  git -C "$CLONE" cat-file -e "$BASE:$tool" || die "BASE lacks custody tool $tool"
done
git -C "$CLONE" cat-file -e "$BASE:configs/arm_readiness/d117_row_registry_v2.json" \
  || die "BASE lacks the v2 registry"

# BASE must contain NONE of the _v4 output that S-0 itself generates.
for absent in "$SUCCESSOR_PINSET" "$FIRST_PACK" "$SECOND_PACK" "$THIRD_PACK"; do
  if git -C "$CLONE" cat-file -e "$BASE:$absent" 2>/dev/null; then
    die "BASE already contains _v4 output at $absent"
  fi
done
printf 'delta_sha256=%s\ntools=4/4 present\nregistry_v2=present\nv4_output=absent\n' \
  "$DELTA_SHA" >> "$TRANS/003-clone-provenance.txt"
```

**Anchor-map re-check.** Run next, in its own shell. Any mismatch is a
precondition defect: stop, re-derive the map on main through the ordinary
review lane, and restart from a fresh estate.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

cat > "$CUSTODY/tools/s0_anchor_map.py" <<'PY'
#!/usr/bin/env python3
"""Re-check the thirteen pinned anchors against a committed revision."""
import json, subprocess, sys

ANCHORS = (
 ("joulewise/arm_readiness.py", 1050, "class EvidenceLifecycleError(ValueError):"),
 ("joulewise/arm_readiness.py", 2025, '- set(lifecycle["irrelevant_path_allowlist"])'),
 ("joulewise/arm_readiness.py", 3639, "def _gate_receipt_histsem(pack_root: Path, *, require_published: bool = False) -> None:"),
 ("joulewise/arm_readiness.py", 4115, "def _r1_changed_paths("),
 ("joulewise/arm_readiness.py", 4300, 'allowlist = set(governed["irrelevant_path_allowlist"])'),
 ("joulewise/arm_readiness.py", 5266, "def _authenticate_generic_evidence_item("),
 ("joulewise/arm_readiness.py", 6265, "def _load_freeze_reference("),
 ("joulewise/arm_readiness.py", 6531, "def generate_freeze_receipt("),
 ("joulewise/arm_readiness.py", 6572, "generation = _pack_generation(root.name)"),
 ("joulewise/identity_pins.py", 1826, "def freeze_projection(pack_root: Path | str) -> Mapping[str, Any]:"),
 ("scripts/generate_arm_readiness.py", 28, "def _parser() -> argparse.ArgumentParser:"),
 ("scripts/project_identity_pins.py", 23, "def parse_args(argv: list[str] | None = None) -> argparse.Namespace:"),
 ("scripts/verify_receipt_histsem.py", 22, "def _parser() -> argparse.ArgumentParser:"),
)

repository, revision = sys.argv[1], sys.argv[2]
report, ok = [], True
for path, line, expected in ANCHORS:
    blob = subprocess.run(["git", "-C", repository, "show", f"{revision}:{path}"],
                          check=True, capture_output=True).stdout.decode()
    lines = blob.splitlines()
    actual = lines[line - 1].strip() if 0 < line <= len(lines) else "<out of range>"
    match = actual == expected.strip()
    ok &= match
    report.append({"path": path, "line": line, "expected": expected.strip(),
                   "actual": actual, "match": match})
print(json.dumps({"revision": revision, "status": "PASS" if ok else "REFUSE",
                  "checked": len(ANCHORS),
                  "matched": sum(1 for item in report if item["match"]),
                  "anchors": report}, indent=2, sort_keys=True))
sys.exit(0 if ok else 2)
PY
chmod 0555 "$CUSTODY/tools/s0_anchor_map.py"
"$PY" "$CUSTODY/tools/s0_anchor_map.py" "$CLONE" "$BASE" \
  > "$TRANS/005-anchor-map.json" || die "anchor map drifted at BASE; see 005"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["matched"]==13, d["matched"]' \
  "$TRANS/005-anchor-map.json" || die "anchor map is not 13/13"
```

**Immutable line audit.** Run next, in its own shell. The ranges are the §0.3
map; each is a whole symbol, so a rename shows up as a shifted or empty extract
rather than as silently wrong bytes.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

for spec in \
  'joulewise/arm_readiness.py 1050,1076p;1999,2120p;3168,3228p;3605,3636p;3639,3707p;4115,4163p;4166,4253p;4256,4399p;5214,5263p;5266,5485p;5488,5743p;6098,6224p;6227,6262p;6265,6475p;6531,6807p;7307,7553p;10160,10261p;10370,10514p' \
  'joulewise/identity_pins.py 1826,1935p' \
  'joulewise/arm_readiness_evidence.py 1709,1731p;2379,2618p' \
  'scripts/generate_arm_readiness.py 28,186p' \
  'scripts/project_identity_pins.py 23,60p' \
  'scripts/verify_receipt_histsem.py 22,73p' \
  'scripts/author_arm_readiness_evidence.py 25,112p' \
  'tests/test_receipt_histsem.py 30,33p;138,165p' \
  'configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py 1942,1955p;2657,2681p' \
  'pyproject.toml 1,16p'
do
  source_file=${spec%% *}; line_ranges=${spec#* }
  git -C "$CLONE" show "$BASE:$source_file" | nl -ba | sed -n "$line_ranges" \
    || die "line audit failed for $source_file"
done > "$TRANS/006-pinned-line-audit.txt"
test -s "$TRANS/006-pinned-line-audit.txt" || die 'line audit is empty'
```

Authority: R4 r4-2, r4-3, r4-7 and the task's immutable-HEAD verification
requirement; R5 V-2.

### 1.2 The environment contract

**No `pip install` anywhere.** Not into the estate venv, not into the host, not
into any environment. `$PY` — the estate venv built in §1.1 — is stdlib-only
and is the interpreter for every step **except** §3.2.

**§3.2 is the one exception, and it is not an install.** R2's §1.1 claimed the
core command surfaces are stdlib-only. That sentence was false for §3.2 and was
never true on any host: `scripts/project_identity_pins.py freeze` on a real pack
resolves the pack's declared runtime backend and hashes its weight files
(`identity_pins.py:1826-1935` → `MlxRuntimeAdapter.prepare`), so it imports
`mlx_lm`. `pyproject.toml:1-16` predicts the exact structured refusal S-0
observed on 2026-08-24: `readiness_identity_artifact_unreadable`, rc 2, with the
"install the [mac] extra" message. Nothing was installed to cure this. Instead
§3.2 runs under the **pinned existing host measurement venv**,
`$MEASURE_PY = /Users/edr/code/JouleWise/.venv/bin/python`, read-only — the
locked environment of `env/mac-measurement-lock.txt`, verified on 2026-08-24 to
be Python 3.13.1 with `mlx_lm` 0.31.3 and `transformers` 5.12.1. §3.2 carries
four guards: clone-first import assertion before and after,
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, weight-file preconditions and a
digest post-condition against the committed `_v3` projection receipts, and the
interpreter path plus resolved versions recorded to transcript `029`.

Reading `/Users/edr/jw_models` (read-only hashing of weights) is permitted; it
is not the forbidden measurement checkout. Never run a dry-run, launch,
measurement, or quiet-Mac command in S-0. Exit code 134 anywhere in §3.2 is the
A85 abort firing outside pytest: STOP and escalate; never retry.

Authority: PACKET-3 RULING R-1; R4 r4-2, r4-3, r4-7; R5 V-2;
`pyproject.toml:1-16`.

### 1.3 Reviewed candidate inputs — hard precondition

**Superseded by merge.** The candidate merged to main before S-0 execution,
which is strictly stronger provenance than a patch plus a sidecar. The clone in
§1.1 is cut from a green merged head, which already contains the v2 registry,
all four custody tools, both contract documents, and this runsheet's fixation
delta — and correctly does **not** contain the generated `_v4` pack output.
What survives of the pre-merge design is exactly three things:

- **(a) the provenance line** — head SHA plus the green CI run id, recorded in
  `$TRANS/003-clone-provenance.txt` by §1.1 and gated by the `$BASE` block;
- **(b) the mechanical manifest** — generated below from committed bytes at the
  clone head, never hand-typed;
- **(c) every stop condition** — an `ED_RESERVED:` string, a digest mismatch, or
  a missing tool still stops execution.

`$INPUT` holds the generated manifest and nothing else. **No tool is ever
executed from `$INPUT`.** Each custody tool sets
`REPO_ROOT = Path(__file__).resolve().parents[1]` and inserts it at the front of
`sys.path`, so a copy outside the repository cannot `import joulewise` at all;
r2's `$INPUT/<tool>.py` invocations could not have run. Tools execute from
`$CLONE/scripts/`, authenticated against this manifest in §3.6.1.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" "$MANIFEST" "$BASE" "$CI_RUN_ID" <<'PY'
import hashlib, json, pathlib, subprocess, sys
clone, manifest_path, head, ci_run_id = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
root = pathlib.Path(clone)

def blob(relative):
    return subprocess.run(["git", "-C", clone, "show", f"{head}:{relative}"],
                          check=True, capture_output=True).stdout

tools = (
    "scripts/build_v4_histsem_pinset.py",
    "scripts/build_family_marker.py",
    "scripts/verify_family_marker.py",
    "scripts/verify_receipt_histsem.py",
)
delta = "docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch"
registry = json.loads(blob("configs/arm_readiness/d117_row_registry_v2.json"))
lifecycle = registry["freeze_evidence_lifecycle"]

manifest = {
    "schema_version": "joulewise.s0_candidate_manifest.v1",
    "head_commit": head,
    "ci_run_id": ci_run_id,
    "provenance": "merged-to-main; green CI; conclusion-field verified",
    "marker_branch": "BUILD-AT-BOUNDARY",
    "registry_id": registry["registry_id"],
    "registry_path": "configs/arm_readiness/d117_row_registry_v2.json",
    "refusal_vocabulary": {item["role"]: item["code"] for item in lifecycle["refusal_vocabulary"]},
    "custody_tools": {name: hashlib.sha256(blob(name)).hexdigest() for name in tools},
    "custody_inputs": {delta: hashlib.sha256(blob(delta)).hexdigest()},
    "test_modules": ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem"],
}
assert manifest["registry_id"] == "d117-row-registry-v2", manifest["registry_id"]
raw = json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
assert b"ED_RESERVED:" not in raw, "manifest carries an unresolved ED_RESERVED value"
manifest_path.write_bytes(raw)
print(json.dumps({"status": "PASS", "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                  "tools": len(tools), "inputs": 1}, indent=2, sort_keys=True))
PY

"$PY" -m json.tool "$MANIFEST" >/dev/null || die 'manifest is not valid JSON'
shasum -a 256 "$MANIFEST" > "$TRANS/007-manifest-sha256.txt"
cp -p "$MANIFEST" "$TRANS/008-s0-candidate-manifest.json"
```

The manifest digest is the candidate-mode tool authority. Sidecars prove
transfer integrity, but the executing marker tools are authenticated against the
already-written `s0-candidate-manifest.json` `custody_tools` digests, never
against committed blobs and never by recomputing a self-authenticating sidecar
(`arm_readiness.py:10160-10261`). Production and publication phases retain
committed-blob equality. Because the manifest is generated from the committed
bytes at `$BASE`, that equality is exact by construction; what §3.6.1 then
proves is that the executing worktree files were not modified after the manifest
was written. The *review* provenance comes from the merge plus green CI, not
from the manifest generating itself. Authority: MARKER-RULING split S-5; S-1
MANIFEST §§6 and 9.1 G-4.

If any input is absent, mismatched, or contains `ED_RESERVED:`, stop: this is
missing custody, not authority to improvise mechanism. Authority: R4 r4-5,
r4-7; R5 S-6, V-1, V-2.

**Registry-v1 literal sweep.** Before mint, perform the ruled literal-string
consistency sweep for the registry repoint. Frozen campaign evidence and
historical process traces retain their archival v1 bytes; they are never bulk
rewritten. Classify each of the eleven live surfaces as either a correct
archival reference retained or a stale live pointer already repointed by the
merged candidate, and append that per-file disposition to the transcript. There
is no `rg` binary on this bench; the sweep uses `grep -E`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

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
( cd "$CLONE" && grep -nE 'd117_row_registry_v1|d117-row-registry-v1' \
    "${LIVE_V1_SURFACES[@]}" ) > "$TRANS/009-registry-v1-literal-sweep.txt"
SWEEP_RC=$?
set -e
if [ "$SWEEP_RC" != 0 ] && [ "$SWEEP_RC" != 1 ]; then
  die "registry sweep failed with rc $SWEEP_RC"
fi

# The hyphen-form id constant in the library is IN SCOPE for this sweep and is
# ruled CORRECT ARCHIVAL RETENTION (packet 1).  Any OTHER joulewise/ hit stops.
set +e
( cd "$CLONE" && grep -rnE 'd117_row_registry_v1|d117-row-registry-v1' joulewise/ ) \
  > "$TRANS/010-joulewise-v1-hits.txt"
LIB_RC=$?
set -e
if [ "$LIB_RC" != 0 ] && [ "$LIB_RC" != 1 ]; then
  die "library sweep failed with rc $LIB_RC"
fi
"$PY" - "$TRANS/010-joulewise-v1-hits.txt" <<'PY'
import pathlib, sys
lines = [line for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip()]
allowed = 'joulewise/arm_readiness.py:46:ROW_REGISTRY_ID = "d117-row-registry-v1"'
unexpected = [line for line in lines if line.strip() != allowed]
assert not unexpected, unexpected
print("PASS: only the ruled archival id constant remains under joulewise/")
PY
```

Two rulings bind this clause's application:

1. *Census scope (packet 1, two-seat concurrence).* The sweep greps both
   literal forms while S-1 MANIFEST §7's census and its "no file under
   `joulewise/`" claim cover the underscore filename form only. The clause
   therefore also fires on the hyphen-form id constant
   `joulewise/arm_readiness.py:46` (`ROW_REGISTRY_ID = "d117-row-registry-v1"`),
   whose ruled disposition is **correct archival retention**: it is reachable
   only for v1-schema documents, selects nothing live
   (`ROW_REGISTRY_RELATIVE_PATH` at `:88` is the live pointer), and mirrors the
   documented `FREEZE_RECEIPT_V1_SCHEMA` retention pattern. That hit does not
   stop S-0. Follow-up naming row REGISTRY-ID-NAMING-01 is registered and fenced
   outside the transaction window.
2. *Fence (packet 2, magistrate synthesis adopting the refuter).* The
   classification lanes here admit **only** mechanical classification of hits
   into the two listed classes. Any hit whose disposition would require more
   than that — a repoint, a rewritten sentence, a resolved semantic conflict,
   any new `joulewise/` hit — is a candidate precondition defect: stop, correct
   the candidate on main through the ordinary review lane, and restart S-0 from
   a fresh estate. In-clone documentation edits are **forbidden** in S-0
   because DOCTRINE_PIN mints whole-file hashes of `window_runbook.md` and
   `decision_log.md` (`arm_readiness_evidence.py:799-888`): an in-clone edit
   would certify bytes no reviewed candidate ever contained.

At least `tests/test_arm_readiness_schemas.py` is a correct retention because it
pins the archival v1 SHA (`:420-422`). Authority: REGISTRY-V2 RULING
(`MAGISTRATE-RULING.md:124-131`); S-1 MANIFEST §7 and §9.3.1 item 3.

---

# 2. ALLOWLIST GENERATION

### 2.1 Generate, never hand-type, the base 112-path contract

This custody-only checker generates 37 exact paths per pack: 11 source JSONs,
11 evidence JSONs, 11 evidence sidecars, `freeze-0004.json` plus sidecar, and
`plan_tree.json` plus sidecar. The versioned successor pinset
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` is the 112th
allowlist entry in the membership sense; it **replaces**, rather than
supplements, the old v1 pinset in this slot. Projection receipts,
`producer_contract.json`, identity-projection paths, and every authenticator
path are intentionally absent because U11 precedes derivation and D-151's
fixed-point principle forbids authenticators in any allowlist. Authority: D-151
conditions 1, 2 and 7; S-1 MANIFEST §3.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

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

"$PY" - "$REGISTRY" <<'PY'
import json,sys
registry=json.load(open(sys.argv[1]))
assert registry["registry_id"] == "d117-row-registry-v2"
assert registry["schema_version"] == "joulewise.arm_readiness_row_registry.v2"
PY
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --shape-only | tee "$TRANS/020-allowlist-shape.json"
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_count"])' \
  "$TRANS/020-allowlist-shape.json")" = 112 || die 'allowlist shape is not 112'
```

The arithmetic is `3 × (11 + 11 + 11 + 1 + 1 + 1 + 1) + 1 = 3 × 37 + 1 = 112`.
R5 V-1 supplies the three 37-path packs (111); O-1-D supplies exactly
`configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` as the `+1`.
The old `legacy_receipt_histsem_pinset_v1.json` remains archival and byte-pinned
but is **not** in this allowlist. "112th entry" means membership; the stored
list is sorted, so the successor need not be physically last. The contract
remains pack-and-ordinal exact (`freeze-0004`, not a glob), and the
custody-external marker contributes zero tracked paths. The live registry
coordinate used throughout is outer id `d117-row-registry-v2`, path
`configs/arm_readiness/d117_row_registry_v2.json`; the archival v1 registry
remains untouched for frozen historical references. Authority: D-151 conditions
1–2 and Consequences; D-150 / MARKER-RULING opening constraints; REGISTRY-V2
RULING; S-1 MANIFEST §§3–4, 2.1, 8.3 and 9.3.1 item 3.

### 2.2 Applicability census

After the evidence-author commands in §3.4, assert the exact eleven generic
kinds.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

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
chmod 0555 "$CUSTODY/tools/check_census.py"
```

Any future issued-acceptance corpus growth must mechanically change the census
to 12 slugs per pack and the contract to 120 paths; no operator may preserve 112
by prose. Authority: R5 V-1.ii; `arm_readiness.py:5214-5254`;
`arm_readiness_evidence.py:1709-1731`.

---

# 3. FULL THREE-PACK TRANSACTION

`$PACKS`, `$PRED_OF`, `$FIRST_PACK`, `$SECOND_PACK` and `$THIRD_PACK` are
defined in `env.sh` (§1.1). There is no index arithmetic anywhere below;
`${PRED_OF[$pack]}` supplies each pack's predecessor by key.

### 3.1 Materialize the `_v4` roots from the reviewed generators

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

"$PY" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/021-emit-contrast-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_1p5b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/022-emit-1p5b-v4.txt"
"$PY" configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py \
  --pack-id d117_floor_qwen25_7b_v4 --family-suffix _v4 \
  --no-preserve-current-frozen-bytes | tee "$TRANS/023-emit-7b-v4.txt"

for pack in "${PACKS[@]}"; do
  test -f "$CLONE/$pack/plan_tree.json" || die "generator produced no plan tree for $pack"
done
git add -A
git commit -m 'S-0 bootstrap reviewed candidate and generated v4 roots'
S0_BOOTSTRAP_HEAD=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$S0_BOOTSTRAP_HEAD"
record_env S0_BOOTSTRAP_HEAD "$S0_BOOTSTRAP_HEAD"
printf '%s\n' "$S0_BOOTSTRAP_HEAD" > "$TRANS/024-bootstrap-head.txt"
```

Expected: each generator prints `generated <pack-id> ... 100 science configs`
with plan hashes; no evidence or `freeze-0004` output exists yet. Authority: R4
r4-3, r4-7; R5 V-1.i; generator CLI `:2657-2681`.

### 3.2 U11 on all three packs, before allowlist derivation

This is the one step that runs under `$MEASURE_PY`. It performs **no install**
of any kind. Run each of the three blocks below in its own shell.

**3.2.a — record and gate the runtime environment.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test -x "$MEASURE_PY" || die 'the pinned measurement interpreter is absent'
"$MEASURE_PY" - "$CLONE" > "$TRANS/029-u11-runtime-environment.txt" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import joulewise, mlx.core, mlx_lm, transformers
print("interpreter:", sys.executable)
print("python:", sys.version.split()[0])
print("joulewise.__file__:", joulewise.__file__)
print("mlx_lm:", mlx_lm.__version__)
print("transformers:", transformers.__version__)
PY
IMPORTED=$(grep -F 'joulewise.__file__:' "$TRANS/029-u11-runtime-environment.txt" | awk '{print $2}')
case "$IMPORTED" in
  "$CLONE"/joulewise/*) ;;
  *) die "clone-first import assertion FAILED before U11: joulewise resolved to $IMPORTED" ;;
esac

# Weight preconditions, from the committed _v3 projection receipts.
"$PY" - "$CLONE" <<'PY'
import json, pathlib, sys
clone = pathlib.Path(sys.argv[1])
predecessors = (
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3",
 "configs/campaigns/d117_floor_qwen25_1p5b_v3",
 "configs/campaigns/d117_floor_qwen25_7b_v3",
)
checked = 0
for pack in predecessors:
    receipt = clone / pack / "identity_pin_projection.receipts/projection-0001.json"
    value = json.loads(receipt.read_bytes())
    for unit in value["identity_units"]:
        for item in unit["model_file_inventory"]:
            path = pathlib.Path(item["resolved_path"])
            assert path.is_file(), f"declared weight file is absent: {path}"
            assert path.stat().st_size == item["size_bytes"], (str(path), path.stat().st_size, item["size_bytes"])
            checked += 1
print(json.dumps({"status": "PASS", "weight_files_checked": checked}, indent=2, sort_keys=True))
PY
```

The precondition checks presence and size, not digests. The digest equality is
proven as a **post-condition** in 3.2.c, where the `_v4` projection receipt's own
`model_file_inventory[].sha256` is compared against the committed `_v3`
receipt's for the same resolved path. That is the same evidence at zero extra
cost: `freeze_projection` hashes every weight file anyway, so a pre-hash would
mean hashing several gigabytes twice. This is a deliberate, recorded departure
from the letter of PACKET-3 RULING R-1(iii), which asked for a precondition; the
evidentiary content is unchanged and the placement is strictly later, so a
missing or moved weight file still stops the step before any mutation.

**3.2.b — the three freezes.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "030-u11-$label" "$MEASURE_PY" scripts/project_identity_pins.py freeze "$pack"
  rc=$(cat "$TRANS/030-u11-$label.rc")
  if [ "$rc" = 134 ]; then
    die "exit 134 in section 3.2 for $label: A85 SIGABRT outside pytest. STOP, escalate, never retry."
  fi
  test "$rc" = 0 || die "U11 freeze rc=$rc for $label"
  no_traceback "030-u11-$label" || die "U11 freeze traceback for $label"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True, d' \
    "$TRANS/030-u11-$label.stdout.json" || die "U11 freeze is not PASS/mutated for $label"
done
```

**3.2.c — post-conditions, then the derivation-head commit.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

# Clone-first import assertion AFTER the mutation.
"$MEASURE_PY" -c 'import sys; sys.path.insert(0,sys.argv[1]); import joulewise; print(joulewise.__file__)' \
  "$CLONE" > "$TRANS/029-u11-import-after.txt"
case "$(cat "$TRANS/029-u11-import-after.txt")" in
  "$CLONE"/joulewise/*) ;;
  *) die 'clone-first import assertion FAILED after U11' ;;
esac

# Weight-digest post-condition: the _v4 projections must have hashed the same
# weight bytes the committed _v3 projection receipts recorded.
"$PY" - "$CLONE" <<'PY'
import json, pathlib, sys
clone = pathlib.Path(sys.argv[1])
pairs = {
 "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4": "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3",
 "configs/campaigns/d117_floor_qwen25_1p5b_v4": "configs/campaigns/d117_floor_qwen25_1p5b_v3",
 "configs/campaigns/d117_floor_qwen25_7b_v4": "configs/campaigns/d117_floor_qwen25_7b_v3",
}
def inventory(pack):
    receipt = clone / pack / "identity_pin_projection.receipts/projection-0001.json"
    value = json.loads(receipt.read_bytes())
    return {item["resolved_path"]: item["sha256"]
            for unit in value["identity_units"] for item in unit["model_file_inventory"]}
compared = 0
for successor, predecessor in pairs.items():
    new, old = inventory(successor), inventory(predecessor)
    assert set(new) == set(old), (successor, sorted(set(new) ^ set(old)))
    for path, digest in new.items():
        assert digest == old[path], (path, digest, old[path])
        compared += 1
print(json.dumps({"status": "PASS", "weight_digests_compared": compared}, indent=2, sort_keys=True))
PY

git add -- "${PACKS[@]}"
git commit -m 'S-0 U11 identity-pin projections for v4 packs'
EVIDENCE_DERIVATION_HEAD=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$EVIDENCE_DERIVATION_HEAD"
record_env EVIDENCE_DERIVATION_HEAD "$EVIDENCE_DERIVATION_HEAD"
printf '%s\n' "$EVIDENCE_DERIVATION_HEAD" > "$TRANS/031-common-derivation-head.txt"
```

Expected: PASS, `mutated:true`, `projection-0001.json` and `.sha256`, and
updated plan bytes in each pack. Those paths are before
`$EVIDENCE_DERIVATION_HEAD`, so they are correctly absent from the 112.
Transcripts `031` and `032` are written **only** after this commit exists — the
r2 estate wrote them from a compound script that continued past failed
assertions, and both were voided (custody 035). Authority: PACKET-3 RULING R-1
and R-5; R4 r4-1, r4-2, r4-3; R5 V-1.i; `identity_pins.py:1826-1935`.

### 3.3 Terminal common-head evidence

The candidate must bind the exact common HEAD and tree and contain no
unresolved registry values. The manifest declares its terminal-review modules in
`test_modules`; the block asserts the declaration matches what it runs, so an
undeclared substitution is a failed proof rather than an unnoticed one. Do not
create any commit between the three author commands.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

git rev-parse HEAD 'HEAD^{tree}' > "$TRANS/032-terminal-common-head.txt"
test "$(git rev-parse HEAD)" = "$EVIDENCE_DERIVATION_HEAD" || die 'HEAD is not the derivation head'
test -z "$(git status --porcelain=v1)" || die 'tree is dirty before authoring'

"$PY" - "$MANIFEST" <<'PY'
import json, sys
declared = json.load(open(sys.argv[1]))["test_modules"]
expected = ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem"]
assert declared == expected, (declared, expected)
print("PASS: manifest declares exactly the two modules this step runs")
PY

set +e
"$PY" -m unittest -v \
  tests.test_arm_readiness_schemas \
  tests.test_receipt_histsem > "$TRANS/033-pre-author-tests.txt" 2>&1
PRE_AUTHOR_RC=$?
set -e
test "$PRE_AUTHOR_RC" = 0 || die "pre-author suite failed with rc $PRE_AUTHOR_RC; see 033"
```

Authority: R4 r4-3, r4-5; R5 V-1.iii, V-2; AUDIT F-7.

### 3.4 Author all 33 generic receipts at the common head, then one evidence commit

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

author_logs=()
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "040-author-$label" "$PY" scripts/author_arm_readiness_evidence.py --pack-root "$pack"
  expect_rc "040-author-$label" 0 || die "author rc for $label"
  no_traceback "040-author-$label" || die "author traceback for $label"
  author_logs+=("$TRANS/040-author-$label.stdout.json")
done
test "${#author_logs[@]}" = 3 || die "expected three author logs, have ${#author_logs[@]}"
"$PY" "$CUSTODY/tools/check_census.py" "${author_logs[@]}" \
  > "$TRANS/041-applicability-census.json" || die 'applicability census failed'
git add -- "${PACKS[@]}"
git commit -m 'S-0 common-head R1 evidence for all v4 packs'
EVIDENCE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$EVIDENCE_COMMIT"
record_env EVIDENCE_COMMIT "$EVIDENCE_COMMIT"
printf '%s\n' "$EVIDENCE_COMMIT" > "$TRANS/042-evidence-commit.txt"
```

The `test "${#author_logs[@]}" = 3` line is the direct guard against the r2
defect class: a loop that silently processed fewer packs than it claimed. Every
loop below that accumulates results carries the same cardinality assertion.

Expected: each output is PASS/`mutated:true`, with exactly the eleven kinds in
§2.2; the commit adds 11 source JSON + 11 receipt JSON + 11 sidecars per pack.
Authority: R4 r4-2, r4-3; R5 V-1.ii, V-1.iii; author CLI `:25-112`;
implementation `arm_readiness_evidence.py:2379-2618`.

### 3.5 Mandatory sacrificial pre-mint refusal check

Pinned mechanics answer the poison question **YES**: `generate_freeze_receipt`
evaluates refusals and then unconditionally writes and plan-pins the PASS **or**
REFUSE receipt at `arm_readiness.py:6760-6806`; replay authenticates and returns
that conclusion through `_load_freeze_reference` `:6265-6475`. Therefore, before
touching the primary clone's unbuilt freeze slots, mint all three in a
sacrificial clone and require PASS.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

PREFLIGHT=$(new_case pre-mint-clean "$EVIDENCE_COMMIT")
minted=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  set +e
  "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$PREFLIGHT/$pack" \
    --predecessor-pack-root "$PREFLIGHT/${PRED_OF[$pack]}" \
    > "$TRANS/050-preflight-$label.stdout.json" \
    2> "$TRANS/050-preflight-$label.stderr.txt"
  rc=$?
  set -e
  printf '%s\n' "$rc" > "$TRANS/050-preflight-$label.rc"
  test "$rc" = 0 || die "sacrificial preflight refused for $label (rc $rc): STOP before primary mint"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"], d' \
    "$TRANS/050-preflight-$label.stdout.json" || die "preflight not clean PASS for $label"
  minted=$((minted + 1))
done
test "$minted" = 3 || die "preflight minted $minted packs, expected 3"
```

Any REFUSE here is a **STOP before primary mint**. Authority: R4 r4-2 poison
question; R5 V-2; `arm_readiness.py:6265-6475,6760-6806`.

### 3.6 Primary freeze ×3 and freeze commit

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

frozen=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "060-freeze-$label" "$PY" scripts/generate_arm_readiness.py freeze \
    --pack-root "$pack" --predecessor-pack-root "${PRED_OF[$pack]}"
  expect_rc "060-freeze-$label" 0 || die "primary freeze rc for $label"
  no_traceback "060-freeze-$label" || die "primary freeze traceback for $label"
  "$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="PASS" and d["mutated"] is True and not d["reason_codes"] and d["receipt_path"].endswith("freeze-0004.json"), d' \
    "$TRANS/060-freeze-$label.stdout.json" || die "primary freeze not clean PASS for $label"
  frozen=$((frozen + 1))
done
test "$frozen" = 3 || die "froze $frozen packs, expected 3"
git add -- "${PACKS[@]}"
git commit -m 'S-0 freeze-0004 receipts for all v4 packs'
FREEZE_COMMIT=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$FREEZE_COMMIT"
record_env FREEZE_COMMIT "$FREEZE_COMMIT"
printf '%s\n' "$FREEZE_COMMIT" > "$TRANS/061-freeze-commit.txt"
```

Expected per pack: `status:PASS`, `mutated:true`, `freeze-0004.json`, its
sidecar, and updated `plan_tree.json`/sidecar. The predecessor path is supplied;
all IDs, hashes and ordinal 0004 are derived by code
(`arm_readiness.py:6227-6262`, `:6531-6807`). A primary REFUSE here is
recoverable only by abandoning this clone and restarting from `$EVIDENCE_COMMIT`
— §4(i) proves the refusal is plan-pinned. Authority: R4 r4-2, r4-3; R5 V-1.iv,
V-1.v; RH-8.

### 3.6.1 Authenticate the executing custody tools — before any tool runs

Every custody tool executes from `$CLONE/scripts/`. Before the first one runs,
each executing file's SHA-256 must equal the digest the reviewed manifest
records for its repo-relative path. This is the same comparison the library
performs internally in candidate mode (`arm_readiness.py:10160-10261`); doing it
here first means a mismatch stops S-0 at a named step instead of surfacing as a
`tool_mismatch` refusal in the middle of the marker build.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" "$MANIFEST" <<'PY'
import hashlib, json, pathlib, sys
clone, manifest_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
recorded = json.loads(manifest_path.read_bytes())["custody_tools"]
expected = {
 "scripts/build_v4_histsem_pinset.py",
 "scripts/build_family_marker.py",
 "scripts/verify_family_marker.py",
 "scripts/verify_receipt_histsem.py",
}
assert set(recorded) == expected, sorted(set(recorded) ^ expected)
for relative, digest in sorted(recorded.items()):
    executing = clone / relative
    actual = hashlib.sha256(executing.read_bytes()).hexdigest()
    assert actual == digest, (relative, actual, digest)
    # The builder is located as a SIBLING of the executing consumer
    # (arm_readiness.py:10717), so both must live in the same directory.
    assert executing.parent == clone / "scripts", executing
print(json.dumps({"status": "PASS", "tools_authenticated": len(recorded),
                  "lane": "candidate", "rule": "manifest digest, not committed blob"},
                 indent=2, sort_keys=True))
PY
"$PY" - "$CLONE" "$MANIFEST" <<'PY'
import hashlib, json, pathlib, sys
clone, manifest_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
inputs = json.loads(manifest_path.read_bytes())["custody_inputs"]
relative = "docs/process_traces/2026-08-22-t20/s0-fixation-delta.patch"
actual = hashlib.sha256((clone / relative).read_bytes()).hexdigest()
assert inputs[relative] == actual, (actual, inputs[relative])
sidecar = (clone / f"{relative}.sha256").read_text().split()[0]
assert sidecar == actual, (sidecar, actual)
print(json.dumps({"status": "PASS", "fixation_delta_sha256": actual}, indent=2, sort_keys=True))
PY
```

Authority: MARKER-RULING split S-5; S-1 MANIFEST §§6 and 9.1 G-4; AUDIT F-1.

### 3.7 Mint the versioned successor, close the 112-path window, then fix it

The reviewed custody tool executes from the clone. Its exact interface:

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test ! -e "$CLONE/$SUCCESSOR_PINSET" || die 'successor pinset output path is create-only and already exists'
"$PY" "$CLONE/scripts/build_v4_histsem_pinset.py" \
  --repository "$CLONE" \
  --base-pinset "$CLONE/$BASE_PINSET" \
  --historical-head "$EVIDENCE_COMMIT" \
  --current-head "$FREEZE_COMMIT" \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK" \
  --output "$CLONE/$SUCCESSOR_PINSET" \
  > "$TRANS/070-build-v4-pinset.json" || die 'successor pinset build refused; see 070'
```

The output path is create-only and must be absent before the command. The v1
artifact is an immutable member 1 of the code-enumerated chain
(`arm_readiness.py:3168-3228`) and is never modified. The successor is member 2
and carries exactly one row per `_v4` pack (three rows, 33 receipts total), with
no `(pack_id, pack_path)` duplicated across chain members; a tool that copies
the nine v1 rows into the successor is refused by the chain-integrity rule at
`:3215-3220`. Each new row derives `freeze-0004`, current and historical pack
hashes, plan hashes, receipt inventory and post-authoring delta from local Git
objects, sets `receipt_count:11`, and refuses network or fetch. Authority:
D-151 conditions 1, 3 and 6; `docs/contracts/d117_step6_confirmation_table.md`
exact `successor_pinset` schema; S-1 MANIFEST §§2.4 and 3.

The builder and verifier transcripts must adjudicate every normative-annex
component, not merely emit schema-valid JSON: mandatory `facts[].source_sha256`;
K5 historical recomputation against each receipt's recorded pack digest; K12
pinned current-tree digest; K7 zero-delete/custody-add/freeze-retarget delta
envelope as bootstrap hardening; the historical-versus-HEAD coordinate split;
derivation ancestry with `origin/main` hard in this clone-proof lane;
predecessor binding and predecessor-mode freeze gate; the HEAD differential
self-test using the unchanged pack-digest framing; and no fetch, repair,
checkout swapping, or network. K5 and K12 are load-bearing; K7 is layered
bootstrap hardening, never sole closure. Authority: RH-8 ruled design items 1–8
and normative annexes, especially consolidated items D2–D8 and D10–D15.

**Step 2 — assert the minted shape and close the window.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE/$SUCCESSOR_PINSET" "$TRANS/070-build-v4-pinset.json" <<'PY'
import json,sys
pinset=json.load(open(sys.argv[1])); build=json.load(open(sys.argv[2]))
assert build["status"] == "PASS", build
assert len(pinset["packs"]) == 3, len(pinset["packs"])
assert sum(row["receipt_count"] for row in pinset["packs"]) == 33
assert {row["pack_id"] for row in pinset["packs"]} == {
 "d117_contrast_qwen25_1p5b_vs_7b_v4",
 "d117_floor_qwen25_1p5b_v4",
 "d117_floor_qwen25_7b_v4",
}
PY
git -C "$CLONE" diff --exit-code -- "$BASE_PINSET" || die 'the v1 pinset member was modified'
git -C "$CLONE" add -- "$SUCCESSOR_PINSET"
git -C "$CLONE" commit -m 'S-0 mint v4 historical-semantics successor pinset'
WINDOW_CLOSE_HEAD=$(git -C "$CLONE" rev-parse HEAD)
git -C "$CLONE" update-ref refs/heads/main "$WINDOW_CLOSE_HEAD"
git -C "$CLONE" update-ref refs/remotes/origin/main "$WINDOW_CLOSE_HEAD"
record_env WINDOW_CLOSE_HEAD "$WINDOW_CLOSE_HEAD"
record_env PINSET_COMMIT "$WINDOW_CLOSE_HEAD"
printf '%s\n' "$WINDOW_CLOSE_HEAD" > "$TRANS/071-window-close-head.txt"
```

**Step 3 — close the contract at exactly 112 and verify the present chain.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" \
  --registry "$REGISTRY" --repo "$CLONE" \
  --derivation "$EVIDENCE_DERIVATION_HEAD" --head "$WINDOW_CLOSE_HEAD" \
  > "$TRANS/090-final-allowlist-contract.json" || die 'the 112-path window did not close; see 090'
capture 072-histsem-present "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --require-published \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK"
expect_rc 072-histsem-present 0 || die 'present-chain verification did not PASS'
no_traceback 072-histsem-present || die 'present-chain verification traceback'
```

`090-final-allowlist-contract.json` closes the changed-set window at exactly 112.
The successor is the sole digest-conditional class: allowlist membership makes it
eligible for subtraction but never authenticates it. Until Ed confirms the
unified step-6 table's `C → S` edge, no claim-bearing arm may use it. The
changed-set contract is a property of this closed window, not a standing
repository invariant, and no authenticator path enters it. Authority: D-151
conditions 2, 5, 7 and 8.

**Step 4 — apply the reviewed fixation delta. This precedes the suite run.**

The **first commit after window close** is the fixation commit. At this hard
review boundary, apply the reviewed mechanical fixation delta committed beside
this runsheet. Its digest was authenticated in §3.6.1 against both the manifest
and its own GNU sidecar. The operator does not invent the edits at the bench:
the delta owns them, and it substitutes exactly one value — the successor's
SHA-256, which cannot exist before the mint. The delta's header explains that
design choice in full.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

test -z "$(git status --porcelain=v1)" || die 'tree is dirty before the fixation delta'
git apply --check "$DELTA" || die 'the reviewed fixation delta does not apply cleanly: STOP'
git apply "$DELTA"
git diff --name-only > "$TRANS/073-fixation-changed-paths.txt"
test "$(cat "$TRANS/073-fixation-changed-paths.txt")" = 'tests/test_receipt_histsem.py' \
  || die 'the fixation delta touched something other than tests/test_receipt_histsem.py'
```

**Step 5 — substitute the one bench value and prove the substitution happened.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$CLONE" > "$TRANS/074-successor-sha256.txt" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
pinset = root / "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
digest = hashlib.sha256(pinset.read_bytes()).hexdigest()
target = root / "tests/test_receipt_histsem.py"
text = target.read_text(encoding="utf-8")
sentinel = '"S0-FIXATION-SUBSTITUTION-PENDING"'
assert text.count(sentinel) == 1, f"sentinel appears {text.count(sentinel)} times"
target.write_text(text.replace(sentinel, f'"{digest}"'), encoding="utf-8")
print(digest)
PY
if grep -qF 'S0-FIXATION-SUBSTITUTION-PENDING' "$CLONE/tests/test_receipt_histsem.py"; then
  die 'the fixation sentinel survived the substitution'
fi
grep -qF "$(cat "$TRANS/074-successor-sha256.txt")" "$CLONE/tests/test_receipt_histsem.py" \
  || die 'the substituted successor digest is not present in the fixed test file'
git -C "$CLONE" diff --name-only > "$TRANS/075-fixation-changed-paths-after-substitution.txt"
test "$(cat "$TRANS/075-fixation-changed-paths-after-substitution.txt")" = 'tests/test_receipt_histsem.py' \
  || die 'substitution widened the changed set'
```

**Step 6 — run the suite over the fixed file, then make the fixation commit.**

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem \
  > "$TRANS/076-histsem-differential-bytepin-tests.txt" 2>&1
HISTSEM_RC=$?
set -e
test "$HISTSEM_RC" = 0 || die "post-fixation histsem suite failed with rc $HISTSEM_RC; see 076"

git -C "$CLONE" diff --exit-code "$WINDOW_CLOSE_HEAD" -- "$BASE_PINSET" \
  || die 'the v1 pinset member changed after window close'
git -C "$CLONE" add -- tests/test_receipt_histsem.py
git -C "$CLONE" commit -m 'S-0 fix successor pinset SHA and counts after window close'
FIXATION_COMMIT=$(git -C "$CLONE" rev-parse HEAD)
test "$(git -C "$CLONE" rev-list --count "$WINDOW_CLOSE_HEAD..$FIXATION_COMMIT")" = 1 \
  || die 'the fixation commit is not the FIRST commit after window close'
git -C "$CLONE" update-ref refs/heads/main "$FIXATION_COMMIT"
git -C "$CLONE" update-ref refs/remotes/origin/main "$FIXATION_COMMIT"
record_env FIXATION_COMMIT "$FIXATION_COMMIT"
printf '%s\n' "$FIXATION_COMMIT" > "$TRANS/077-fixation-commit.txt"
```

**Step 7 — independent recomputation.** An independent reviewer recomputes the
successor SHA-256 and its pack/receipt counts from the committed blob at
`$FIXATION_COMMIT`, checks them against `074-successor-sha256.txt` and against
the substituted literal in `tests/test_receipt_histsem.py`, and later checks the
same SHA against Ed's exact step-6 table (§3.8). A mismatch is a mechanism
failure, not an invitation to reseal.

The local chain verification and fixation tests are necessary but remain
forged-`origin/main`-conditional in this clone. Transcript labels must say
exactly that; they must not say "suite green." R2's activation delta over the 21
`S0-BLOCKED` methods is STRUCK (see §5.1): those are A84/A85 work and no
activation edit over them belongs to the fixation commit. Authority: D-151
conditions 3–4 and Consequences; S-1 MANIFEST §§9.3 and 9.3.5; AUDIT F-2.

### 3.8 Family marker — D-150 option (a) only, custody-external

D-150 leaves one legal branch: `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL. It
contributes no tracked path and leaves the contract at 112.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

test "$MARKER_BRANCH" = 'BUILD-AT-BOUNDARY' \
  || die "manifest marker_branch is $MARKER_BRANCH, not BUILD-AT-BOUNDARY"
printf '%s\n' "$MARKER_BRANCH" > "$TRANS/080-marker-decision.txt"
```

After freeze ×3, successor verification and fixation, run the reviewed
constructor and consumer in explicit **candidate** mode. Candidate-mode tool
authentication compares the executing bytes — in `$CLONE/scripts/` — to the
digests recorded in `$MANIFEST`; it does not use committed-blob equality and
cannot be selected by sidecar presence (`arm_readiness.py:10207-10261`). The S-0
marker stays outside the Git worktree.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

mkdir -p "$CUSTODY/marker-candidate"
"$PY" "$CLONE/scripts/build_family_marker.py" \
  --repository "$CLONE" --head "$FIXATION_COMMIT" \
  --pack-root "$FIRST_PACK" --pack-root "$SECOND_PACK" --pack-root "$THIRD_PACK" \
  --output "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$MANIFEST" \
  > "$TRANS/081-marker-build.json" || die 'marker build refused; see 081'
test -f "$CUSTODY/marker-candidate/d117_family_publication_v4.json.sha256" \
  || die 'marker sidecar was not written'

"$PY" "$CLONE/scripts/verify_family_marker.py" \
  --repository "$CLONE" \
  --marker "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  --phase candidate \
  --candidate-manifest "$MANIFEST" \
  > "$TRANS/082-marker-verify.json" || die 'marker verification refused; see 082'

FORGED_ORIGIN_MAIN_OID=$(git -C "$CLONE" rev-parse refs/remotes/origin/main)
record_env FORGED_ORIGIN_MAIN_OID "$FORGED_ORIGIN_MAIN_OID"
"$PY" - "$TRANS/082-marker-verify.json" "$FORGED_ORIGIN_MAIN_OID" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"] == "PASS", d
assert d["phase"] == "candidate" and d["lane"] == "candidate", d
assert d["gate_admissible"] is False and d["publication_authorized"] is False, d
assert d["consulted_git"]["origin_main_commit"] == sys.argv[2], d["consulted_git"]
PY
printf 'FORGED_ORIGIN_MAIN_OID=%s\nclassification=forged-ref-conditional; not published PASS\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/084-local-green-classification.txt"
```

Expected marker schema: `joulewise.d117_family_publication_marker.v1`, all three
exact pack IDs, `freeze-0004` receipt IDs and hashes, common Git head and tree,
and candidate consumer PASS. The verification transcript must carry
`lane: "candidate"` and `gate_admissible: false`; a candidate receipt can never
gate publication. Authority: MARKER-RULING ratified items 1–3 and S-4, plus
Consequences; D-151 condition 4.

The marker and successor are the two immutable consumers of the unified table
`joulewise.d117_step6_confirmation_table.v1`. The table is custody-external and
has exactly the two edges `C → M` and `C → S`; its path is an authenticator and
never enters any allowlist. The lead renders the exact canonical candidate table
and GNU sidecar according to the ONE HOME,
`docs/contracts/d117_step6_confirmation_table.md`, presents digest `hC` to Ed,
and stops until Ed's YES names that digest. The literal YES is already in the
immutable bytes Ed hashes; no timestamp or self-digest is added.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

STEP6_CANDIDATE="$CUSTODY/step6-candidate/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_CANDIDATE" || die 'the rendered step-6 candidate table is absent'
test -f "$STEP6_CANDIDATE.sha256" || die 'the step-6 candidate sidecar is absent'
# ED_STEP6_CONFIRMED_SHA256 is transcribed from Ed's out-of-band YES over hC and
# pasted into THIS block; it is deliberately not recorded in env.sh.
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" || die "Ed's step-6 confirmation digest is not set"
test "$(shasum -a 256 "$STEP6_CANDIDATE" | awk '{print $1}')" = "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'the rendered table does not match the digest Ed confirmed'

"$PY" - "$CLONE" "$STEP6_CANDIDATE" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$SUCCESSOR_PINSET" "$FIXATION_COMMIT" <<'PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]); table_path=pathlib.Path(sys.argv[2])
marker_path=pathlib.Path(sys.argv[3]); successor=sys.argv[4]; head=sys.argv[5]
sys.path.insert(0, str(root))
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

# The successor digest Ed confirmed must be the one the fixation delta pinned.
test "$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["successor_pinset"]["sha256"])' \
  "$STEP6_CANDIDATE")" = "$(cat "$TRANS/074-successor-sha256.txt")" \
  || die "Ed's table names a successor digest different from the fixation pin"
```

The `sys.path.insert` in that block is required: `$PY` is the estate venv and
`joulewise` is importable only from the clone. R2 omitted it and would have
raised `ModuleNotFoundError`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

STEP6_CANDIDATE="$CUSTODY/step6-candidate/d117_step6_confirmation_table_v4.json"
PUBLISHED_DIR="$CUSTODY/windows/family_publication"
mkdir -p "$PUBLISHED_DIR"
cp -p "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$CUSTODY/marker-candidate/d117_family_publication_v4.json.sha256" \
  "$PUBLISHED_DIR/"
cp -p "$STEP6_CANDIDATE" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json"
cp -p "$STEP6_CANDIDATE.sha256" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json.sha256"
cmp "$CUSTODY/marker-candidate/d117_family_publication_v4.json" \
  "$PUBLISHED_DIR/d117_family_publication_v4.json" || die 'marker promotion is not byte-exact'
cmp "$STEP6_CANDIDATE" "$PUBLISHED_DIR/d117_step6_confirmation_table_v4.json" \
  || die 'table promotion is not byte-exact'
```

Promotion copies exact immutable bytes; it never edits either consumer or the
table. Authority: D-151 conditions 2–3; MARKER-RULING ratified items 1–2.

### 3.9 Arm and verify all three after window closure and fixation

The exact 112 window was already closed at `$WINDOW_CLOSE_HEAD` in §3.7; the
post-window fixation commit does not retroactively enlarge it. This clone proof
may arm only after the exact marker and Ed-confirmed table have been placed in
`$CUSTODY/windows/family_publication`. Any arm or verify result here is
non-claim-bearing and forged-ref-conditional; publication acceptance is the
separate published-green step in §3.10.

**Pre-declared expected refusal.** Under the stdlib `$PY`, the
`u11-arm-reverification` leg refuses with
`readiness_identity_artifact_unreadable` (`arm_readiness.py:7439-7448` calls
`_run_identity_arm_reverification`, which resolves the runtime backend the same
way §3.2 does). That refusal is EXPECTED and admissible here — the eleven
asserted `want` kinds below exclude the identity item — and it is pre-declared
so it is never read as a finding. Live arm-side U11 re-verification is proven by
the real transaction in the measurement environment, not by S-0.

**Early governed refusal tolerance.** `generate_arm_receipt` can return a
governed REFUSE with `receipt_path: null` before it writes any receipt (for
example when the family-publication or histsem gate refuses at
`arm_readiness.py:7319`). R2 asserted `d["receipt_path"]` unconditionally and
would have died on that shape. The block below records the null case, skips the
paired `verify` for that pack, and continues; a null receipt path for **all
three** packs is a STOP, because then nothing was armed at all.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

FINAL_HEAD=$(git -C "$CLONE" rev-parse HEAD)
test "$FINAL_HEAD" = "$FIXATION_COMMIT" || die 'HEAD is not the fixation commit'
record_env FINAL_HEAD "$FINAL_HEAD"
record_env PROBE_BASE "$FINAL_HEAD"

ARM_CONTEXT=$("$PY" -c 'import json,sys; r=sys.argv[1]; print(json.dumps({
"bracket_session_id":"s0-clone-proof", "pre_attempt_id":"s0-pre",
"post_attempt_id":"s0-post", "clock_route":"MANUAL",
"claim_runs_root":r+"/claim", "bound_runs_root":r+"/bound",
"custody_root":r+"/custody", "quarantine_root":r+"/quarantine",
"claim_backup_destination":r+"/backup-claim",
"bound_backup_destination":r+"/backup-bound", "waiver_path":r+"/waivers.json"}))' \
  "$CUSTODY/arm-context")
record_env ARM_CONTEXT "$ARM_CONTEXT"

armed=0
receipts=0
for pack in "${PACKS[@]}"; do
  label=$(basename "$pack")
  capture "091-arm-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" arm \
    --pack-root "$CLONE/$pack" --arm-context "$ARM_CONTEXT" \
    --window-custody-root "$CUSTODY/windows"
  no_traceback "091-arm-$label" || die "arm traceback for $label"
  rc=$(cat "$TRANS/091-arm-$label.rc")
  if [ "$rc" != 0 ] && [ "$rc" != 1 ]; then
    die "arm rc=$rc for $label (2 means a raised ArmReadinessError, not a governed refusal)"
  fi
  armed=$((armed + 1))
  ARM_RECEIPT=$("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("receipt_path") or "")' \
    "$TRANS/091-arm-$label.stdout.json")
  if [ -z "$ARM_RECEIPT" ]; then
    printf 'pack=%s rc=%s receipt_path=null (early governed refusal; verify skipped)\n' \
      "$label" "$rc" >> "$TRANS/096-early-governed-refusals.txt"
    continue
  fi
  receipts=$((receipts + 1))
  capture "092-verify-$label" "$PY" "$CLONE/scripts/generate_arm_readiness.py" verify \
    --pack-root "$CLONE/$pack" --arm-receipt "$ARM_RECEIPT"
  no_traceback "092-verify-$label" || die "verify traceback for $label"
  vrc=$(cat "$TRANS/092-verify-$label.rc")
  if [ "$vrc" != 0 ] && [ "$vrc" != 1 ] && [ "$vrc" != 2 ]; then
    die "verify rc=$vrc for $label"
  fi
done
test "$armed" = 3 || die "armed $armed packs, expected 3"
test "$receipts" != 0 || die 'every pack refused before writing an arm receipt: nothing was armed'
printf 'armed=%s receipts_written=%s\n' "$armed" "$receipts" > "$TRANS/097-arm-cardinality.txt"
```

The arm may be GO only if all non-S-0 custody and T0 prerequisites are
legitimately present. Otherwise a **governed**, non-null arm receipt and
canonical verify REFUSE (often `readiness_dependency_refused`) is acceptable;
S-0 must not fabricate T0 or measurement evidence. "All items cross the R1 gate"
concretely means, for each pack: all eleven generic evidence items are
discovered; neither the registry's `DEPENDENCY_CHANGED_SET` nor
`DEPENDENCY_MANIFEST` code appears; no traceback occurs; and an arm receipt is
written. Resolve the two candidate-owned spellings mechanically:

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$REGISTRY" "$CUSTODY/windows" <<'PY'
import json,pathlib,sys
reg=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]
codes={x["role"]:x["code"] for x in reg["refusal_vocabulary"]}
bad={codes["DEPENDENCY_CHANGED_SET"],codes["DEPENDENCY_MANIFEST"]}
root=pathlib.Path(sys.argv[2])
want={"ACCEPTANCE_OWNER","DOCTRINE_PIN","ESTIMATOR_IDENTITY","MINT_TRUST",
"MULTICELL_MINT","PACK_AUTHENTICATION","PACK_FAMILY","REASON_CODE_COVERAGE",
"RECEIPT_ORACLE","RECOVERY_LEDGER_TEST","THREE_WINDOW_REGRESSION"}
seen=0
for p in sorted(root.glob("*/arm_readiness.receipts/arm-*.json")):
 d=json.load(open(p)); kinds={e.get("receipt_kind") for e in d["evidence"]}
 assert want <= kinds, (str(p), sorted(want-kinds))
 assert not (bad & {r["code"] for r in d["refusals"]}), (str(p), sorted(bad))
 seen+=1
assert seen, "no arm receipts were found under the window custody root"
print(json.dumps({"status":"PASS","arm_receipts":seen,
 "crossed_actual_gate":"arm_readiness.py:4300-4322","forbidden_codes":sorted(bad)},
 indent=2, sort_keys=True))
PY
```

Authority: R4 r4-2; R5 V-1.iii, V-2; actual changed-set site
`arm_readiness.py:4300-4322`; CLI exit semantics
`scripts/generate_arm_readiness.py:169-186`; AUDIT F-12.

### 3.10 Two-part green record — local conditional, then PUBLISHED

Run the complete local suite. Record the forged remote-ref OID beside the
result. Even at return code 0, this transcript's classification is
**`LOCAL GREEN — FORGED-origin/main-CONDITIONAL at <OID>`**; neither its
filename nor its prose may say "suite green" or "published green."

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

test "$(git -C "$CLONE" rev-parse refs/remotes/origin/main)" = "$FORGED_ORIGIN_MAIN_OID" \
  || die 'the forged origin/main OID moved since the marker was verified'
set +e
"$PY" -m unittest discover -s tests > "$TRANS/093-local-forged-ref-conditional.txt" 2>&1
LOCAL_SUITE_RC=$?
set -e
test "$LOCAL_SUITE_RC" = 0 || die "local suite failed with rc $LOCAL_SUITE_RC; see 093"
printf 'classification=LOCAL GREEN — FORGED-origin/main-CONDITIONAL\noid=%s\n' \
  "$FORGED_ORIGIN_MAIN_OID" > "$TRANS/094-local-green-classification.txt"
```

Acceptance does **not** close here. After the lead actually publishes the
accepted fixation head, a clean checkout must prove strict four-way equality
(publication head == HEAD == local main == `origin/main`), run the complete
suite against that real published ref, and record `PUBLISHED GREEN` with its OID
in separate immutable custody. Candidate marker verification from §3.8 is not
reusable: publication verification must use the Ed-confirmed table,
committed-blob tool equality, semantic replay, and a transcript with
`lane: "published"` and `gate_admissible: true`. No S-0 clone command may forge
that claim. Authority: D-151 condition 4; MARKER-RULING ratified items 2–3 and
split S-1.

---

# 4. PROBE BATTERY

Each probe uses a fresh `new_case` clone at `$PROBE_BASE` (recorded in §3.9);
never reuse a case after a mutation. For R1 codes, extract the exact
candidate-owned spellings first.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CHANGED_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_CHANGED_SET"))' "$REGISTRY")
MANIFEST_CODE=$("$PY" -c 'import json,sys; r=json.load(open(sys.argv[1]))["freeze_evidence_lifecycle"]; print(next(x["code"] for x in r["refusal_vocabulary"] if x["role"]=="DEPENDENCY_MANIFEST"))' "$REGISTRY")
test -n "$CHANGED_CODE" || die 'DEPENDENCY_CHANGED_SET code is empty'
test -n "$MANIFEST_CODE" || die 'DEPENDENCY_MANIFEST code is empty'
record_env CHANGED_CODE "$CHANGED_CODE"
record_env MANIFEST_CODE "$MANIFEST_CODE"
printf 'DEPENDENCY_CHANGED_SET=%s\nDEPENDENCY_MANIFEST=%s\n' \
  "$CHANGED_CODE" "$MANIFEST_CODE" > "$TRANS/100-r1-code-map.txt"
```

Both codes are recorded in `env.sh`, so every probe block below gets them by
sourcing rather than by re-deriving.

### 4(a). Ordinary changed path refuses

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case ordinary-path "$PROBE_BASE")
printf 'S-0 ordinary-path probe\n' > "$CASE/s0-ordinary-probe.txt"
commit_case "$CASE" 'S-0 probe ordinary changed path'
capture 101-ordinary "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
rc=$(cat "$TRANS/101-ordinary.rc")
if [ "$rc" != 1 ] && [ "$rc" != 2 ]; then die "ordinary-path probe rc=$rc"; fi
grep -F "$CHANGED_CODE" "$TRANS/101-ordinary.stdout.json" > /dev/null \
  || die 'ordinary changed path did not produce the DEPENDENCY_CHANGED_SET code'
no_traceback 101-ordinary || die 'ordinary-path probe traceback'
```

Pass iff the exact registry code for `DEPENDENCY_CHANGED_SET` appears and no
pack bytes change. This probe reaches the R1 gate through the **replay** path:
at `$PROBE_BASE` the pack already carries a plan-pinned `freeze-0004`, so
`generate_freeze_receipt` enters `_load_freeze_reference` (`:6265-6475`), where
the changed-set gate runs. Authority: R4 r4-2; R5 V-1;
`arm_readiness.py:4115-4163,4300-4322`.

### 4(b). Unexpected output-directory file refuses

R2 ran this at the `arm` verb against the pack's own evidence directory. That
cannot work: `arm` calls `_discover_evidence` with `include_pack=False`
(`arm_readiness.py:7383`), so the pack namespace is dropped from the scan
(`_evidence_directories`, `:5257-5263`) and what actually refuses is the
pack-digest / changed-set code, not `readiness_evidence_unreadable`. The single
directory-inventory check at `:5514-5541` governs **both** namespaces, so it
takes two probes to exercise it in both.

**4(b.1) — window-custody namespace, at `arm`, pack untouched.** The custody
pack root is `<window custody root>/<pack name>` (`:7365`), and that namespace
IS scanned at arm. Nothing in the repository is modified, so this probe proves
exactly what r2's prose claimed: a governed arm REFUSE naming
`readiness_evidence_unreadable`, an external refusal receipt, and an unchanged
pack snapshot.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

PROBE_CUSTODY="$CUSTODY/probes/102-unexpected"
mkdir -p "$PROBE_CUSTODY/$(basename "$FIRST_PACK")/arm_readiness.evidence"
mkdir -p "$PROBE_CUSTODY/family_publication"
cp -p "$CUSTODY/windows/family_publication/"* "$PROBE_CUSTODY/family_publication/"
printf 'unexpected\n' \
  > "$PROBE_CUSTODY/$(basename "$FIRST_PACK")/arm_readiness.evidence/unexpected.txt"
BEFORE=$(git -C "$CLONE" rev-parse HEAD)
capture 102-unexpected "$PY" "$CLONE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CLONE/$FIRST_PACK" --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$PROBE_CUSTODY"
expect_rc 102-unexpected 1 || die 'custody-namespace probe did not return a governed REFUSE'
grep -F 'readiness_evidence_unreadable' "$TRANS/102-unexpected.stdout.json" > /dev/null \
  || die 'custody-namespace probe did not name readiness_evidence_unreadable'
no_traceback 102-unexpected || die 'custody-namespace probe traceback'
test "$(git -C "$CLONE" rev-parse HEAD)" = "$BEFORE" || die 'the probe moved the clone HEAD'
test -z "$(git -C "$CLONE" status --porcelain=v1)" || die 'the probe dirtied the clone'
```

**4(b.2) — pack namespace, at the freeze mint path.** `include_pack` defaults to
true and `generate_freeze_receipt` uses the default (`:6725`), so the pack
namespace is scanned there. The case is cut at `$EVIDENCE_COMMIT`, before
`freeze-0004` exists, so the mint path runs rather than the replay path — the
mint path performs no changed-set comparison (it passes `head_commit=None`), so
the unexpected-output signal is not masked. The refusal is written and
plan-pinned exactly as §4(i) proves for the poison case; the pack's **source and
evidence** bytes are unchanged, but `freeze-0004.json` and the plan pin are
written. That is the ruled mint semantics, not a probe defect.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case unexpected-pack-output "$EVIDENCE_COMMIT")
printf 'unexpected\n' > "$CASE/$FIRST_PACK/arm_readiness.evidence/unexpected.txt"
commit_case "$CASE" 'S-0 probe unexpected pack evidence output'
capture 103-unexpected-pack "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
expect_rc 103-unexpected-pack 1 || die 'pack-namespace probe did not return a governed REFUSE'
no_traceback 103-unexpected-pack || die 'pack-namespace probe traceback'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is True and "readiness_evidence_unreadable" in d["reason_codes"], d' \
  "$TRANS/103-unexpected-pack.stdout.json" \
  || die 'pack-namespace probe did not name readiness_evidence_unreadable on a written refusal'
git -C "$CASE" diff --exit-code -- "$FIRST_PACK/arm_readiness.sources" \
  || die 'the probe changed pack source bytes'
git -C "$CASE" diff --exit-code -- "$FIRST_PACK/arm_readiness.evidence" \
  || die 'the probe changed pack evidence bytes'
```

Pass iff both namespaces refuse through the directory-inventory check.
Authority: R4 r4-2; R5 V-2; `arm_readiness.py:5257-5263,5514-5541,6725,7383`;
the CLI enforces read-only pack snapshots for non-freeze verbs at
`scripts/generate_arm_readiness.py:95-105,108-168`; AUDIT F-6.

### 4(c). Non-freeze mutation in current **and** sibling plan trees

For each direction separately, mutate the existing schema-valid string
`window_identity.window_id`, re-render canonical JSON and its sidecar, commit,
then replay the first pack's freeze.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

cat > "$CUSTODY/tools/mutate_plan.py" <<'PY'
import hashlib,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text())
d["window_identity"]["window_id"] += "-s0-mutation"
raw=(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode(); p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  plan_tree.json\n")
PY
chmod 0555 "$CUSTODY/tools/mutate_plan.py"

CASE=$(new_case plan-current "$PROBE_BASE")
"$PY" "$CUSTODY/tools/mutate_plan.py" "$CASE/$FIRST_PACK/plan_tree.json"
commit_case "$CASE" 'S-0 probe current plan non-freeze mutation'
capture 104-plan-current "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
grep -F "$MANIFEST_CODE" "$TRANS/104-plan-current.stdout.json" > /dev/null \
  || die 'current-plan mutation did not produce the DEPENDENCY_MANIFEST code'
no_traceback 104-plan-current || die 'current-plan probe traceback'
```

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case plan-sibling "$PROBE_BASE")
"$PY" "$CUSTODY/tools/mutate_plan.py" "$CASE/$SECOND_PACK/plan_tree.json"
commit_case "$CASE" 'S-0 probe sibling plan non-freeze mutation'
capture 105-plan-sibling "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
grep -F "$MANIFEST_CODE" "$TRANS/105-plan-sibling.stdout.json" > /dev/null \
  || die 'sibling-plan mutation did not produce the DEPENDENCY_MANIFEST code'
no_traceback 105-plan-sibling || die 'sibling-plan probe traceback'
```

The mutation is a real file now rather than a shell function, because a shell
function defined in one block does not exist in the next. Pass iff both
directions refuse with the exact `DEPENDENCY_MANIFEST` code, despite
`plan_tree.json` and its sidecar being allowlisted. This is L5-F2's outstanding
mutation falsifier. Authority: R4 r4-2; SIT-C3 and seat-L5 F2; R5 S-6, V-1.vi;
`arm_readiness.py:4342-4399`.

### 4(d). Missing, extra, and unused candidate entries all fail

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

"$PY" - "$TRANS" "$REGISTRY" <<'PY'
import json,pathlib,sys
t=pathlib.Path(sys.argv[1]); json.load(open(t/"020-allowlist-shape.json"))
# Recreate from the registry rather than trusting transcript order.
reg=json.load(open(sys.argv[2]))["freeze_evidence_lifecycle"]["irrelevant_path_allowlist"]
assert len(reg)==112, len(reg)
(t/"020-candidate-exact.json").write_text(json.dumps(reg))
(t/"106-missing-list.json").write_text(json.dumps(reg[1:]))
(t/"107-extra-list.json").write_text(json.dumps(sorted(reg+["docs/s0-extra"])))
(t/"108-unused-observed.json").write_text(json.dumps(reg[:-1]))
PY

set +e
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/106-missing-list.json" > "$TRANS/106-missing.json"
MISSING_RC=$?
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" --shape-only \
  --candidate-list "$TRANS/107-extra-list.json" > "$TRANS/107-extra.json"
EXTRA_RC=$?
"$PY" "$CUSTODY/tools/s0_allowlist_contract.py" --registry "$REGISTRY" \
  --candidate-list "$TRANS/020-candidate-exact.json" \
  --observed-list "$TRANS/108-unused-observed.json" > "$TRANS/108-unused.json"
UNUSED_RC=$?
set -e
test "$MISSING_RC" = 2 || die "missing-entry variant returned rc $MISSING_RC, expected 2"
test "$EXTRA_RC" = 2 || die "extra-entry variant returned rc $EXTRA_RC, expected 2"
test "$UNUSED_RC" = 2 || die "unused-entry variant returned rc $UNUSED_RC, expected 2"
"$PY" - "$TRANS" <<'PY'
import json,pathlib,sys
t=pathlib.Path(sys.argv[1])
assert json.load(open(t/"106-missing.json"))["candidate_missing"]
assert json.load(open(t/"107-extra.json"))["candidate_extra"]
assert json.load(open(t/"108-unused.json"))["unused_allowlist"]
print("PASS: each variant names its own defect field")
PY
```

Pass iff the three reports respectively name `candidate_missing`,
`candidate_extra` and `unused_allowlist`, all with exit 2. The registry is the
RULED live coordinate; the candidate authors the previously absent
`freeze_evidence_lifecycle.irrelevant_path_allowlist` key there. Authority:
REGISTRY-V2 RULING; D-151 condition 8 and Consequences; R4 r4-2; R5 V-1.v.

### 4(e). Per-class tamper probes over every allowlisted path class

Install the exact tamper driver, then run one fresh case per class and replay
`freeze-0004` for the affected pack. Each mutation remains schema-shaped where
that is necessary to reach the intended authenticator.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

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
chmod 0555 "$CUSTODY/tools/tamper_class.py"

tampered=0
for kind in source-json evidence-json evidence-sidecar freeze-json freeze-sidecar plan-json plan-sidecar pinset-json; do
  CASE=$(new_case "tamper-$kind" "$PROBE_BASE")
  "$PY" "$CUSTODY/tools/tamper_class.py" "$kind" "$CASE" "$FIRST_PACK" \
    || die "tamper driver failed for $kind"
  commit_case "$CASE" "S-0 per-class tamper $kind"
  capture "110-tamper-$kind" "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
  test "$(cat "$TRANS/110-tamper-$kind.rc")" != 0 || die "tamper class $kind was ACCEPTED"
  no_traceback "110-tamper-$kind" || die "tamper class $kind failed ugly"
  tampered=$((tampered + 1))
done
test "$tampered" = 8 || die "ran $tampered tamper classes, expected 8"
```

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-source-json.stdout.json" > /dev/null || die 'source-json class'
grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-evidence-json.stdout.json" > /dev/null || die 'evidence-json class'
grep -F 'readiness_evidence_digest_mismatch' "$TRANS/110-tamper-evidence-sidecar.stdout.json" > /dev/null || die 'evidence-sidecar class'
grep -F 'readiness_freeze_receipt_mismatch' "$TRANS/110-tamper-freeze-json.stdout.json" > /dev/null || die 'freeze-json class'
grep -F 'readiness_freeze_receipt_mismatch' "$TRANS/110-tamper-freeze-sidecar.stdout.json" > /dev/null || die 'freeze-sidecar class'
grep -F "$MANIFEST_CODE" "$TRANS/110-tamper-plan-json.stdout.json" > /dev/null || die 'plan-json class'
grep -F 'readiness_pack_digest_mismatch' "$TRANS/110-tamper-plan-sidecar.stdout.json" > /dev/null || die 'plan-sidecar class'
grep -E '"histsem_[a-z0-9_]*(mismatch|invalid)"' "$TRANS/110-tamper-pinset-json.stdout.json" > /dev/null || die 'pinset-json class'
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
| successor pinset JSON (1) | change one governed `_v4` row's `plan_sha256` | a `histsem_*_mismatch` refusal and a C→S digest-condition refusal; after fixation, byte-only tamper must also fail the successor SHA assertion |

For the pinset byte authenticator additionally run, inside the
`tamper-pinset-json` case, the suite that carries the fixation pin. This is the
step the fixation delta exists to make meaningful: `SUCCESSOR_PINSET_SHA256` is
a literal, so a byte-only edit of the minted pinset fails here even when every
structural check would have passed.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CASES/tamper-pinset-json"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem > "$TRANS/118-pinset-byte-pin.txt" 2>&1
BYTE_PIN_RC=$?
set -e
test "$BYTE_PIN_RC" != 0 || die 'the tampered successor pinset PASSED the byte-pin suite'
grep -F 'test_successor_pinset_is_byte_pinned_at_fixation' "$TRANS/118-pinset-byte-pin.txt" > /dev/null \
  || die 'the byte-pin method did not run in the tampered case'
```

Pass iff **all eight** classes refuse through an independent digest, binding or
semantic-replay authenticator. For the successor class, the Ed-confirmed C→S
edge is load-bearing and "the test run itself" is never an authenticator. If any
class has no such authenticator, apply V-1.vi's digest-conditional subtraction
rule: it may not remain a static allowlist subtraction; remove that class from
the candidate allowlist, bind it in the authenticated derived manifest, and
reopen the mechanism proof. Authority: D-151 conditions 2–3; R5 V-1.iv, V-1.vi,
V-1.vii; RH-8; semantic replay `arm_readiness.py:6098-6224`.

### 4(e.1). Digest-conditional successor subtraction — actual C→S edge

The synthetic unit probe and the transaction probe are both mandatory. The
focused class must prove: the exact confirmed digest subtracts the successor; no
table, an absent or invalid table, a wrong path, a wrong digest, and any later
successor rewrite all refuse with the pre-existing `DEPENDENCY_CHANGED_SET`
role; and `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` is exactly the successor path.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"
cd "$CLONE"

set +e
"$PY" -m unittest -v tests.test_receipt_histsem.SuccessorPinsetDigestConditionTests \
  > "$TRANS/122-c-to-s-unit-probes.txt" 2>&1
CTOS_RC=$?
set -e
test "$CTOS_RC" = 0 || die "C-to-S unit probes failed with rc $CTOS_RC; see 122"

# Transaction PASS side: section 3.9's 091-* arms used Ed's exact table at
# $CUSTODY/windows/family_publication and must contain no R1 changed-set code.
checked=0
for p in "$TRANS"/091-arm-*.stdout.json; do
  if grep -F "$CHANGED_CODE" "$p" > /dev/null; then
    die "arm transcript $p carries the changed-set code"
  fi
  checked=$((checked + 1))
done
test "$checked" = 3 || die "checked $checked arm transcripts, expected 3"
```

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# Transaction refusal side: keep Ed's table fixed, mutate the committed
# successor bytes at a later reviewed head, and require DEPENDENCY_CHANGED_SET.
CASE=$(new_case c-to-s-later-rewrite "$PROBE_BASE")
printf '\n' >> "$CASE/$SUCCESSOR_PINSET"
commit_case "$CASE" 'S-0 C-to-S probe: later successor rewrite'
capture 123-c-to-s-later-rewrite "$PY" "$CASE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CASE/$FIRST_PACK" --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$CUSTODY/windows"
grep -F "$CHANGED_CODE" "$TRANS/123-c-to-s-later-rewrite.stdout.json" > /dev/null \
  || die 'a later successor rewrite was NOT refused by DEPENDENCY_CHANGED_SET'
no_traceback 123-c-to-s-later-rewrite || die 'C-to-S rewrite probe traceback'
```

Pass iff the valid transaction crosses the changed-set gate only against Ed's
exact table digest, while the later committed rewrite is refused by
`DEPENDENCY_CHANGED_SET` before it can be forgiven by allowlist membership. The
table and its sidecar are immutable during the probe. Authority: D-151
condition 2; `docs/contracts/d117_step6_confirmation_table.md` "Where the
`C → S` edge is enforced."

### 4(f). `DEPENDENCY_MANIFEST` conjunct — both halves

**Source/receipt half.** Coherently change a source and its facts'
`source_sha256`, re-sidecar the receipt, but deliberately leave the receipt's
`dependency_manifest_sha256` at its old value. This crosses the ordinary
source-digest authenticator and reaches `arm_readiness.py:4324-4341`.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case manifest-binding "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK" <<'PY'
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
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
grep -F "$MANIFEST_CODE" "$TRANS/119-manifest-binding.stdout.json" > /dev/null \
  || die 'the source/receipt conjunct half did not refuse with DEPENDENCY_MANIFEST'
no_traceback 119-manifest-binding || die 'manifest-binding probe traceback'
```

**Derivation/current dependency half.** The exact coherent current-plan and
sibling-plan commands are §4(c), transcripts `104-plan-current` and
`105-plan-sibling`. Both must contain `$MANIFEST_CODE` from
`arm_readiness.py:4342-4399`. All three outputs must be nonzero and
traceback-free. Both logical halves are conjunctive; one does not substitute for
the other. Authority: R5 S-6 and V-1.vi; SIT-C3; `arm_readiness.py:4324-4399`.

### 4(g). S-6 dual-validator falsifiers

In a fresh case make the coherent plan mutation from §4(c), then run both
genuinely different validators.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case s6-dual "$PROBE_BASE")
"$PY" "$CUSTODY/tools/mutate_plan.py" "$CASE/$FIRST_PACK/plan_tree.json"
commit_case "$CASE" 'S-0 S-6 dual-validator mutation'
set +e
"$PY" "$CASE/$FIRST_PACK/generate_configs.py" --check \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 --family-suffix _v4 \
  --preserve-current-frozen-bytes \
  > "$TRANS/120-s6-preserve-check.txt" 2>&1
PRESERVE_RC=$?
set -e
printf 'preserve_check_rc=%s\n' "$PRESERVE_RC" >> "$TRANS/120-s6-preserve-check.txt"

if [ "$PRESERVE_RC" = 0 ]; then
  printf 'disposition=ECHO-HOLE PRESENT (expected at the pinned candidate)\n' \
    >> "$TRANS/120-s6-preserve-check.txt"
else
  # Governed-nonzero alternative: the candidate deliberately fixed the echo
  # hole.  That is admissible, but only as a GOVERNED refusal -- a traceback or
  # a crash is a mechanism failure, not the fix.
  if grep -Eq 'Traceback \(most recent call last\)' "$TRANS/120-s6-preserve-check.txt"; then
    die "preserve-mode --check failed ugly (rc $PRESERVE_RC); this is not the governed fix"
  fi
  printf 'disposition=ECHO-HOLE FIXED (governed nonzero check, rc %s)\n' "$PRESERVE_RC" \
    >> "$TRANS/120-s6-preserve-check.txt"
fi

capture 121-s6-r1 "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
grep -F "$MANIFEST_CODE" "$TRANS/121-s6-r1.stdout.json" > /dev/null \
  || die 'the R1 half of the S-6 dual falsifier did not refuse'
no_traceback 121-s6-r1 || die 'S-6 R1 probe traceback'
```

Expected falsifier: preserve-mode `--check` returns 0 because it echoes
checked-out bytes into its comparison
(`generate_configs.py:1942-1955`), while R1 refuses the same mutation with
`$MANIFEST_CODE` (`arm_readiness.py:4342-4399`). Both dispositions are
admissible and both are recorded: if the candidate intentionally fixed the echo
hole, the first result becomes a **governed nonzero check** and the S-1 manifest
must say so. The R1 half is mandatory either way; only that half can fail this
probe. Authority: R5 S-6; SIT-C3; AUDIT F-9.

### 4(h). Histsem and pinset probes

Present was captured at `072-histsem-present` and must PASS before arm; because
this clone's reviewed ref is forged, that PASS is local and conditional, not
published green.

**Explicit absence must be probed through an enumerated member.** R2 passed an
invented path (`$CASES/definitely-absent-pinset.json`) as `--pinset` and expected
`histsem_pinset_absent`. That is unreachable: `_load_histsem_pinset`
(`:3168-3228`) rejects any override outside the closed enumeration with
`histsem_pinset_invalid` at `:3184-3187` before it ever reads a file, and the
committed `tests/test_receipt_histsem.py:146-165` pins exactly that behaviour.
The only path to `histsem_pinset_absent` is the `present == 0` branch at
`:3223-3227`, reached by naming an **enumerated** member that is absent from the
worktree. The probe therefore removes the successor member in a fresh case and
names it.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case histsem-successor-absent "$PROBE_BASE")
git -C "$CASE" rm -q -- "$SUCCESSOR_PINSET" || die 'could not remove the enumerated successor member'
commit_case "$CASE" 'S-0 probe: enumerated successor member absent'
test ! -e "$CASE/$SUCCESSOR_PINSET" || die 'the successor member is still on disk'
capture 130-histsem-absent "$PY" "$CASE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CASE" --pinset "$SUCCESSOR_PINSET" --require-published
expect_rc 130-histsem-absent 2 || die 'the absent-member probe did not exit 2'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["reason_codes"]==["histsem_pinset_absent"], d' \
  "$TRANS/130-histsem-absent.stdout.json" \
  || die 'the absent-member probe did not produce histsem_pinset_absent alone'
```

**The out-of-enumeration override is a second, distinct probe** — it proves the
closed enumeration is actually closed, which is the property r2's probe
accidentally exercised while claiming something else.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

ABSENT="$CASES/definitely-absent-pinset.json"
test ! -e "$ABSENT" || die 'the out-of-enumeration probe path already exists'
capture 131-histsem-out-of-enumeration "$PY" "$CLONE/scripts/verify_receipt_histsem.py" \
  --repository-root "$CLONE" --pinset "$ABSENT" --require-published
expect_rc 131-histsem-out-of-enumeration 2 || die 'the override probe did not exit 2'
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["reason_codes"]==["histsem_pinset_invalid"], d' \
  "$TRANS/131-histsem-out-of-enumeration.stdout.json" \
  || die 'an out-of-enumeration override did not refuse histsem_pinset_invalid'
```

Pass iff the closed v1→successor chain verifies, arms cross the actual
changed-set gate only under the confirmed C→S condition, an absent **enumerated**
member produces `histsem_pinset_absent`, an out-of-enumeration override produces
`histsem_pinset_invalid`, and all three malformed candidate variants of §4(d)
fail. D-151 condition 6 preserves the rule-11 clarification unchanged: an absent
enumerated member does not tighten the library's default HEAD-absence semantics;
only this explicit CLI/worktree verifier path promises `histsem_pinset_absent`.
Authority: D-151 conditions 2 and 6; RH-8 and normative annexes;
HISTSEM-CONTRACT "Failure semantics"; `verify_receipt_histsem.py:22-73`;
`arm_readiness.py:3168-3228`; `tests/test_receipt_histsem.py:146-165`; AUDIT F-3.

### 4(i). Poison question — direct code-path probe

Create a case at `$EVIDENCE_COMMIT`, delete one generic evidence pair, mint,
commit the refused mint, then replay unchanged.

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

CASE=$(new_case poison "$EVIDENCE_COMMIT")
git -C "$CASE" rm -q -- \
  "$FIRST_PACK/arm_readiness.evidence/evidence-acceptance-owner.json" \
  "$FIRST_PACK/arm_readiness.evidence/evidence-acceptance-owner.json.sha256"
commit_case "$CASE" 'S-0 poison input: missing evidence'
capture 140-poison-first "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is True and d["receipt_path"].endswith("freeze-0004.json"), d' \
  "$TRANS/140-poison-first.stdout.json" || die 'poison mint did not write a plan-pinned REFUSE'
commit_case "$CASE" 'S-0 poison refused freeze becomes plan-pinned'
capture 141-poison-replay "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}"
"$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["status"]=="REFUSE" and d["mutated"] is False and d["receipt_path"].endswith("freeze-0004.json"), d' \
  "$TRANS/141-poison-replay.stdout.json" || die 'poison replay was not idempotent'
```

At the pinned HEAD the expected answer is **YES**. Consequence: the clean
sacrificial PASS in §3.5 is mandatory before each primary mint; after a primary
REFUSE write, abandon the primary clone and restart from `$EVIDENCE_COMMIT` — do
not try to repair the plan-pinned refusal in place. If a candidate changes the
first result to `mutated:false` with no freeze or plan write, record **NO**,
retain the preflight as a defence-in-depth check, and verify no pack bytes
changed. Any third outcome (partial write, traceback, or replay not idempotent)
reopens the mechanism. Authority: R4 r4-2 poison question; R5 V-2;
`arm_readiness.py:6265-6475,6760-6806`.

---

# 5. ACCEPTANCE CHECKLIST

Evidence root: `$CUSTODY/transcripts` (all referenced artifacts are clone-proof
custody, never a measurement checkout). Check a box only after independently
reading its named artifacts.

- [ ] **r4-2** — One full three-pack sequence is evidenced by `030-*`, `031-*`,
  `032-*`, `040-*`, `042-*`, `050-*`, `060-*`, `061-*`, `070-*`–`077-*`,
  `080-*`–`085-*`, `090-*`, `091-*`, `092-*` and `097-*`; every pack crosses the
  actual changed-set gate; ordinary path, both unexpected-output namespaces,
  both plan-tree directions, candidate-shape triplet, C→S, and poison probes
  adjudicate as specified. Every cardinality assertion (`3` packs, `8` tamper
  classes, `3` arm transcripts) is recorded, not assumed.
- [ ] **V-2** — Lead/magistrate custody and nondelegation are recorded in
  `001-*` through `010-*`; S-6 both validators are `120-*`/`121-*`; governed arm
  and verify and every transcript have been read with no fail-ugly traceback.
- [ ] **V-1.vi / D-151 C→S** — All eight path classes in `110-*` and `118-*`
  have independent tamper refusals, including the two manifest halves;
  `122-*`/`123-*` prove that successor subtraction is conditional on Ed's exact
  table digest and that a later rewrite refuses; any unauthenticated class has
  triggered the derived-manifest reopen rather than being waived. Authority:
  D-151 condition 2.
- [ ] **rh-8 / D-151 successor** — The 112 arithmetic and exact window-close
  contract are PASS in `020-*`/`090-*`; present chain and arm crossing are
  `072-*`/`091-*`; explicit enumerated-member absence is `130-*` and the
  out-of-enumeration refusal is `131-*`; missing/extra/unused are
  `106-*`–`108-*`; all three `_v4` rows and local-Git provenance are in the
  create-only successor at `070-*`; the v1 member is byte-unchanged; fixation is
  the first post-window commit (`077-*` plus the `rev-list --count` assertion).
  Authority: D-151 conditions 1–3 and 6.
- [ ] **D-150 marker** — Only `BUILD-AT-BOUNDARY`, CUSTODY-EXTERNAL ran;
  candidate transcript `082-*` says `lane: candidate`, `gate_admissible: false`,
  and names the forged OID; the marker, table and authenticators are absent from
  every allowlist. Authority: MARKER-RULING opening constraints, ratified item 2
  and Consequences.
- [ ] **Custody surface (superseded-by-merge shape)** — The clone provenance
  line (`003-*`: head SHA, green CI run id, the `$BASE` containment gate) is
  present; the mechanically generated manifest and its digest are `007-*`/`008-*`;
  the four executing custody tools in `$CLONE/scripts/` matched their manifest
  `custody_tools` digests before any tool ran (§3.6.1); the fixation delta
  matched both its manifest `custody_inputs` digest and its committed GNU
  sidecar; the anchor map re-checked 13/13 at `$BASE` (`005-*`); and HEADs, Git
  statuses and complete stdout/stderr/exit-code triplets are present under the
  custody root. There is **no** candidate patch, no `$INPUT` tool set and no
  tool sidecar check in this lane: the merge supersedes all three. Authority:
  S-1 MANIFEST §§2.4, 4, 6 and 9.1 G-1/G-4; AUDIT F-1, F-8.
- [ ] **Fixation delta** — `s0-fixation-delta.patch` applied cleanly
  (`073-*`), touched only `tests/test_receipt_histsem.py` (`073-*`/`075-*`), its
  single sentinel was substituted with the minted successor digest (`074-*`),
  the sentinel does not survive anywhere in the fixed file, the post-fixation
  histsem suite is rc 0 (`076-*`), and Ed's confirmed table names the same
  successor digest. Authority: D-151 condition 3; AUDIT F-2.
- ~~S0-BLOCKED addendum~~ **STRUCK 2026-08-23 by magistrate ruling** (recorded in
  the S-1 fix-round packet and MANIFEST §9.3): the 21-method flip theory was
  DISPROVEN BY MEASUREMENT — the partition is S0-BLOCKED 0 / STRUCTURAL 17 /
  CRASH 4; none flips on the S-0 mint. S-0 acceptance is the proving-obligations
  checklist above ALONE. The 17 structural entries ride kernel row A84
  (FIXTURE-MODERNIZATION-01) and the 4 crash entries A85 (MLX-ACID-SIGABRT-01,
  which also requires A84).
- [ ] **Two-part green** — `093-*`/`094-*` are recorded only as local
  forged-`origin/main`-conditional with the exact forged OID; a separate clean,
  strict-four-way real-ref run records PUBLISHED GREEN before acceptance
  closure. No transcript calls local green "suite green." Authority: D-151
  condition 4.
- [ ] No command touched or read `/Users/edr/JouleWise-measurement-20260818`; no
  quiet-Mac measurement, freeze outside the clone, dry-run, arm launch, consume
  or publication occurred. §3.2's read-only use of
  `/Users/edr/code/JouleWise/.venv` and read-only hashing of
  `/Users/edr/jw_models` are the two permitted host reads and are recorded in
  `029-*`.

### 5.1 S0-BLOCKED set — STRUCK 2026-08-23

Historical text preserved in `s0-runsheet-r2.md` §5.1. The 21 methods are A84
(FIXTURE-MODERNIZATION-01) and A85 (MLX-ACID-SIGABRT-01) work; their markers are
`unittest.skip`, not `expectedFailure`, since the fix round. No activation delta
over them belongs to the S-0 fixation commit, and S-0 does not run a
21-method acceptance command.

---

# 6. FAILURE SEMANTICS

**Mechanism failures — trip V-1.vi and REOPEN to the derived authenticated
manifest.** An ordinary non-allowlisted path crosses; an unexpected evidence
output is accepted in either namespace; either current or sibling coherent
non-freeze plan mutation crosses R1; any missing/extra/unused candidate variant
is accepted; any one of the eight allowlisted classes lacks an independent
tamper authenticator; either `DEPENDENCY_MANIFEST` half crosses; S-6's R1
validator crosses; the successor contains a cross-member duplicate, is
subtracted without the exact C→S edge, remains forgiven after a later rewrite,
or differs from Ed's confirmed digest; an authenticator enters an allowlist;
histsem present does not gate arm or freeze; an absent enumerated member does
not produce `histsem_pinset_absent`; an out-of-enumeration override does not
produce `histsem_pinset_invalid`; or a refusal mint partially writes, fails
ugly, or cannot be safely screened by the sacrificial preflight. A candidate-lane
receipt with `gate_admissible:true`, or any local-green transcript presented as
published or suite green, is also a mechanism failure. The response is not "fix
a test expectation": derive an authenticated manifest, remove every
unauthenticated subtraction, rerun all of S-0, and preserve the failed
transcript. Authority: D-151 conditions 2, 4, 6 and 7; MARKER-RULING ratified
item 2; R5 V-1.vi, V-1.vii, V-2; R4 r4-2; RH-8.

**Instrument failures — STOP, amend on main through the review lane, restart
from a fresh estate.** A step whose environment or dependency precondition is
false; a cited anchor that has drifted; a command that names a file, flag or
refusal code that does not exist; a step sequenced after the step that needs its
output. These are not ordinary defects and they are not fixed at the bench: they
produced cold-gate packets 1, 2 and 3 and then the executability audit, and each
one cost a full estate. The 2026-08-24 record is the precedent — an instrument
defect is cured on main, re-ratified, and S-0 restarts from `§1.1`. Authority:
PACKET-3 RULING R-2 through R-4; AUDIT ruling.

**Ordinary defects — fix and restart the affected clean case or the whole
transaction as indicated.** Wrong CLI spelling, missing custody input, sidecar
checksum mismatch, malformed probe fixture that fails before reaching its
intended gate, transcript collision, or a legitimate non-S-0 T0 refusal after
all lifecycle gates crossed. A primary freeze REFUSE is recoverable only by
abandoning that primary clone and restarting from the committed evidence state
because §4(i) proves it is plan-pinned. A baseline candidate test failure, an
unresolved `ED_RESERVED:` value, an anchor-map or line-audit mismatch, an
11/112 count mismatch, or a dirty reviewed tree is a precondition defect: stop
before mint, correct the candidate, and start again. Authority: R4 r4-2, r4-3,
r4-5; R5 S-6, V-1, V-2.

**Execution defects — the estate is superseded.** A `record_env` duplicate, a
block executed without sourcing `env.sh`, two blocks concatenated into one
shell, or any transcript written by a step whose gate assertions did not all
pass. Custody 035 is the worked example: a compound script continued past failed
U11 assertions and wrote transcripts `031`/`032` with the bootstrap head. Both
files were voided and the estate was superseded. Void the affected transcripts
in writing, then restart from a fresh estate. Authority: PACKET-3 RULING R-4 and
R-5; custody 035.

---

# 7. RESOLVED R1 ITEMS AND ACTIVE CAUTIONS

### O-1 — RESOLVED by D-151

O-1-D is controlling: the successor path replaces v1 in the 112-member contract;
S-0 mints into the successor; subtraction is conditional on Ed's unified-table
C→S edge; and fixation is the first commit after window close. The refuted
113-path/test-source option is not an alternate lane. Authority: D-151 Ruling
and Consequences.

### O-2 — RESOLVED by D-150 / marker ruling

The sole branch is BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL, with no tracked marker
paths and a 112-path contract. Authority: D-150 / MARKER-RULING opening
constraints and Consequences; S-1 MANIFEST §4.

### O-3 — RESOLVED by the merge; the custody precondition changed shape

R2 held reviewed-candidate custody as a `$INPUT` precondition: an exported
patch, a binding manifest, and four tool/sidecar pairs. The candidate merged to
main with green CI before S-0 execution, which is strictly stronger provenance.
The precondition is now the `$BASE` containment gate plus the mechanical
manifest of §1.3, and the executing-tool authentication of §3.6.1. S-0 may
verify and execute those bytes but never invent them. Authority: S-1 MANIFEST
§§6, 9.1 and closing provenance; AUDIT F-1, F-8.

### O-4 — RESOLVED before execution

The §9.3.6 re-derivation finding was resolved by the independent seat plus the
fix round: the re-derivation path is proven live and the fixture defect is
cured. O-4 is discharged and the four
`tests/test_arm_readiness_evidence_author.py` methods are ordinary green. If any
of them is red at `$BASE`, that is a baseline candidate test failure under §6
"ordinary defects": stop before mint. Authority: S-1 MANIFEST §9.3.6 and its
fix-round disposition.

### O-5 — ACTIVE: the U11 leg proves less than the rest of S-0

§3.2 runs under a host interpreter that S-0 does not own, and §3.9's
`u11-arm-reverification` leg refuses by design under `$PY`. What S-0 therefore
proves about U11 is: the projection freezes deterministically against the same
weight bytes the committed `_v3` receipts recorded, from the clone's own code,
offline. What it does **not** prove is live arm-side U11 re-verification; that
is proven by the real transaction in the measurement environment. No S-0
transcript may claim otherwise. Authority: PACKET-3 RULING R-1; AUDIT
interpreter-split cross-check ("no dependence").
