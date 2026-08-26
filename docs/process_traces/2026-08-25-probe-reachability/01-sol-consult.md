# S-0 probe-reachability consult — Sol xhigh seat (verbatim)

Seat: Sol (`gpt-5.6-sol`, effort xhigh, sandbox read-only, `WRITE_SCOPE: none`),
run through the project Codex MCP bridge as thread
`01a03b39-47b5-71f2-a3ce-45f318ab5315`. Coordinated by an Opus lieutenant, whose
adjudication header — the lead-side replay of every claim — opens the record
below and is part of it.

Question put to the seat: estate 9 (BASE `5a034f84`) ran the §4 probe battery of
`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md` continue-on-fail, and six
probe blocks failed with one shared signature — the refusal each probe was
written to elicit is masked by an earlier gate in the real execution order. For
each failure the seat was asked to (i) trace the actual first-firing gate in
`joulewise/arm_readiness.py` at `5a034f84` and explain the ordering, (ii) derive
whether the intended gate is reachable by a better-shaped mutation from the same
case base and, if so, specify the exact mutation and the exact expected
`reason_codes` and detail, (iii) say plainly where a gate is unreachable at
freeze-replay/arm and name where it IS already exercised, and (iv) write the
replacement probe block.

Evidence the seat read: estate-9 transcripts under
`scratchpad/s0-clone-proof-r4/custody/transcripts/` and per-block logs under
`scratchpad/r5-blocks/block*-e9.log` (read-only; the estate was not modified),
plus `joulewise/arm_readiness.py` at `5a034f84`.

Received by the magistrate 2026-08-25 and recorded verbatim below. The
adjudication over this record is `02-MAGISTRATE-ADJUDICATION.md`; the cure it
authorises lands as runsheet revision r6.

---

All five predicted detail strings are real code strings at BASE. Verification complete — adjudicating ACCEPT.

## Adjudication (lead checks replayed)

**Session**: MCP thread `01a03b39-47b5-71f2-a3ce-45f318ab5315`, gpt-5.6-sol, effort xhigh, sandbox read-only, reverse Claude server disabled, one-hop headers. Envelope §2-valid: single final `BRIDGE_REPORT_V1`, status DONE, `pathspec: []`, flags `no_edits/read_only/custody_preserved`. No writes anywhere (worktree unchanged; estate untouched).

**Lead replay results — everything checked out:**
- All six actual transcript verdicts match Sol's table verbatim (I re-read every `.rc`/`.stdout.json` under `/private/tmp/claude-501/-Users-edr-code-JouleWise/eac3ed1d-1740-4cf1-9ab3-b4c539575666/scratchpad/s0-clone-proof-r4/custody/transcripts/`): 104 rc=2 `readiness_freeze_receipt_mismatch`; **105 rc=0 PASS, `mutated=false`, no gate fired at all**; 110-freeze-json rc=2 `readiness_receipt_namespace_anomalous` "sidecar mismatch for freeze-0004.json"; 119 rc=2 `readiness_evidence_digest_mismatch`; 121 rc=2 identity mismatch (same as 104); 123 rc=1 `histsem_pinset_invalid`.
- All six gate-ordering citations in `/Users/edr/code/JouleWise/joulewise/arm_readiness.py` at 5a034f84 verified line-level: `_pack_identity` binds `window_id`+`plan_sha256` (~4959); identity compare → `readiness_freeze_receipt_mismatch` at 6513–6521 before R1; namespace sidecar auth at 4713–4725 runs from 6848 before the plan-freeze-reference exactness check at 6503–6506; evidence digest auth at 5460–5465; arm entry calls `_gate_receipt_histsem` first at 7537–7546 with canonical-parse → `histsem_pinset_invalid` at 3792–3799.
- All five predicted expected-detail strings in the replacement blocks are real code strings (lines 3898, 4366, 4481, 4539, 5556) — not invented.

**One caveat for the cure PR**: the replacement blocks' expected `reason_codes`+`detail` are code-derived predictions, not yet executed — treat them as derived expectations to confirm on the next estate run, not as observed ground truth.

---

## Sol's raw report (verbatim deliverable)

### Findings

Evidence shorthand: `T` = estate-9 `custody/transcripts/`; `B` = estate-9 `r5-blocks/`; code locations refer to `/Users/edr/code/JouleWise/joulewise/arm_readiness.py` at `5a034f8441508b6b0991e862735c908bf871000f`.

| Probe | Intended | Verified estate-9 result | Actual first gate and ordering | Reachability |
|---|---|---|---|---|
| `104-plan-current` | `readiness_r1_dependency_manifest` | `rc=2`; `readiness_freeze_receipt_mismatch`; detail `"freeze receipt pack identity differs from committed pack bytes"` (`T/104-plan-current.{rc,stdout.json}`). `B/block36-e9.log` is only the later chmod rerun artifact. | The original mutation changes `window_identity.window_id`, not `plan_sha256`. `_pack_identity()` includes `window_id` at line 4959. Existing-receipt replay calls `_load_freeze_reference()` at 6874–6882, which compares identity at 6513–6520 before authenticating generic evidence at 6577–6598 and before R1 lifecycle validation at 5608–5619. | Reachable. Mutate `window_identity.evidence_root_id` instead: it changes normalized `plan_tree.json` but leaves every freeze identity term, calibration-plan digest, U11 binding, freeze receipt, and evidence receipt fixed. Expected `rc=1`, exactly `[readiness_r1_dependency_manifest]`, detail `"current dependency differs from its derivation binding: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4/plan_tree.json"`. |
| `105-plan-sibling` | `readiness_r1_dependency_manifest` | `rc=0`; `status=PASS`; `mutated=false`; `reason_codes=[]`. `B/block37-e9.log:5` records the failed runsheet assertion. | No refusal gate fired. The first pack's identity is unchanged. The changed-set computation at 4423–4458 subtracts all three allowlisted plan paths, while `_r1_manifest_dependencies()` at 4280–4309 derives dependencies only from the evidence source currently being authenticated. First-pack evidence does not name the second pack's v4 plan, so the replay returns PASS at 6902–6911. | The claim "first-pack replay rejects a sibling-plan mutation via `DEPENDENCY_MANIFEST`" is **unreachable by design**. The role is reachable by replaying the mutated second pack itself. Family-wide allowlist membership belongs to the `106–108` candidate-list vehicle. |
| `110-tamper-freeze-json` | `readiness_freeze_receipt_mismatch` | `rc=2`; `readiness_receipt_namespace_anomalous`; detail `"sidecar mismatch for freeze-0004.json"`. `B/block40-e9.log:1` records the assertion stop. | `generate_freeze_receipt()` scans the namespace at 6848 before replay. `scan_receipt_namespace()` authenticates each sidecar at 4713–4725, before `_load_freeze_reference()` can compare the plan pin at 6503–6506. | Reachable. After changing `issued_at_utc`, recompute the freeze JSON's GNU sidecar but leave the plan's recorded freeze SHA fixed. Namespace authentication passes, then the exact plan reference fails with detail `"plan freeze reference is not exact"`. |
| `123-c-to-s-later-rewrite` | `readiness_r1_dependency_changed_set` + authenticated bytes-differ detail | `rc=1`; `histsem_pinset_invalid`; detail `"committed receipt-histsem pinset is invalid"`. `B/block42-e9.log:5` records the stop. | Arm begins with `_gate_receipt_histsem(root)` at 7535–7546. The appended newline makes the committed pinset noncanonical at 3792–3799. This precedes `_load_freeze_reference()` at 7564 and all R1 validation. | Reachable. Canonically change `plan_sha256` in a sibling pinset row while leaving the armed first-pack row fixed. Pinset shape validation passes; target histsem verification examines only the target row at 3497–3519. R1 then compares the changed whole-file digest at 4364–4367. Expected `rc=1`, exactly `[readiness_r1_dependency_changed_set]`, with the requested authenticated detail. |
| `119-manifest-binding` | `readiness_r1_dependency_manifest` | `rc=2`; `readiness_evidence_digest_mismatch`; detail `"evidence item digest differs from authenticated bytes"`. `B/block43-e9.log:5` records the stop. | The evidence receipt was changed, but its digest remained stale in the frozen receipt's evidence item. `_authenticate_generic_evidence_item()` checks that binding at 5460–5465, before reading fact sources at 5531–5570 and before lifecycle validation at 5608–5619. | Reachable. Propagate the new evidence-receipt SHA into the frozen receipt, recompute its sidecar, then propagate that freeze SHA into the plan's freeze slot and plan sidecar. Leave `dependency_manifest_sha256` stale. The freeze slot is the enumerated subtraction at 4170–4213, so this propagation does not create a competing manifest failure. Expected exact detail: `"evidence source and receipt dependency-manifest bindings disagree"`. |
| `121-s6-r1` | `readiness_r1_dependency_manifest` | `rc=2`; `readiness_freeze_receipt_mismatch`; detail `"freeze receipt pack identity differs from committed pack bytes"`. `B/block44-e9.log:5` records the stop. | Same ordering as `104`: the `window_id` mutation changes `_pack_identity()` at 4959, and identity is compared at 6513–6520 before R1. | Reachable. Preserve the S-6 generator check, but mutate `window_identity.evidence_root_id`. Expected result is the same exact manifest refusal as amended `104`. |

D-154 remains consistent with this trace: v4+ `pack_root` is compared through its repository-relative projection, while other identity content remains authenticated. For `104` and `121`, the actual changed identity term is specifically `window_id`; `plan_sha256` would likewise fire first if the referenced calibration-plan bytes changed.

### Replacement blocks

#### 1. `104-plan-current`

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case plan-current "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK/plan_tree.json" <<'PY' \
  || die 'current-plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 probe current plan manifest-only mutation'

capture 104-plan-current "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 104-plan-current 1 \
  || die 'current-plan manifest probe did not return rc 1'
"$PY" - "$TRANS/104-plan-current.stdout.json" "$MANIFEST_CODE" "$FIRST_PACK" <<'PY' \
  || die 'current-plan mutation did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 104-plan-current || die 'current-plan probe traceback'
```

#### 2. `105-plan-sibling` (vehicle change: the second pack replays its own mutated plan)

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case plan-sibling "$PROBE_BASE")
"$PY" - "$CASE/$SECOND_PACK/plan_tree.json" <<'PY' \
  || die 'second-pack plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 probe second-pack plan manifest mutation'

capture 105-plan-sibling "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$SECOND_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$SECOND_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 105-plan-sibling 1 \
  || die 'second-pack manifest probe did not return rc 1'
"$PY" - "$TRANS/105-plan-sibling.stdout.json" "$MANIFEST_CODE" "$SECOND_PACK" <<'PY' \
  || die 'second-pack mutation did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 105-plan-sibling || die 'second-pack manifest probe traceback'
```

#### 3. Amended complete `110-*` class block

(Also repairs two latent failures block 40 had not yet reached: `freeze-sidecar` correctly produces `readiness_receipt_namespace_anomalous`, and the original `plan-json` mutation changed `window_id` and would reproduce the identity masking from `104` — it now changes `evidence_root_id`.)

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

cat > "$CUSTODY/tools/tamper_class.py" <<'PY'
import argparse, hashlib, json, pathlib
ap = argparse.ArgumentParser()
ap.add_argument("kind")
ap.add_argument("repo", type=pathlib.Path)
ap.add_argument("pack")
a = ap.parse_args()
root = a.repo / a.pack

def render(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    path.write_bytes(raw)
    return raw

def sidecar(path, raw):
    path.with_name(path.name + ".sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  " + path.name + "\n"
    )

def zero_sidecar(path, target):
    path.write_text("0" * 64 + "  " + target + "\n")

if a.kind == "source-json":
    p = root / "arm_readiness.sources/acceptance-owner.json"
    d = json.loads(p.read_text())
    d["primary_artifacts"][0]["sha256"] = "0" * 64
    render(p, d)
elif a.kind == "evidence-json":
    p = root / "arm_readiness.evidence/evidence-acceptance-owner.json"
    p.write_bytes(p.read_bytes() + b" ")
elif a.kind == "evidence-sidecar":
    p = root / "arm_readiness.evidence/evidence-acceptance-owner.json.sha256"
    zero_sidecar(p, "evidence-acceptance-owner.json")
elif a.kind == "freeze-json":
    p = root / "arm_readiness.freeze.receipts/freeze-0004.json"
    d = json.loads(p.read_text())
    d["issued_at_utc"] = d["issued_at_utc"].replace("2026-", "2027-", 1)
    raw = render(p, d)
    sidecar(p, raw)
elif a.kind == "freeze-sidecar":
    p = root / "arm_readiness.freeze.receipts/freeze-0004.json.sha256"
    zero_sidecar(p, "freeze-0004.json")
elif a.kind == "plan-json":
    p = root / "plan_tree.json"
    d = json.loads(p.read_text())
    d["window_identity"]["evidence_root_id"] += "-s0-tamper"
    raw = render(p, d)
    p.with_name("plan_tree.sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
    )
elif a.kind == "plan-sidecar":
    zero_sidecar(root / "plan_tree.sha256", "plan_tree.json")
elif a.kind == "pinset-json":
    p = a.repo / "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
    d = json.loads(p.read_text())
    d["packs"][0]["plan_sha256"] = "0" * 64
    render(p, d)
else:
    raise SystemExit("unknown class")
PY
chmod 0555 "$CUSTODY/tools/tamper_class.py"

tampered=0
for kind in source-json evidence-json evidence-sidecar freeze-json freeze-sidecar plan-json plan-sidecar pinset-json; do
  CASE=$(new_case "tamper-$kind" "$PROBE_BASE")
  "$PY" "$CUSTODY/tools/tamper_class.py" "$kind" "$CASE" "$FIRST_PACK" \
    || die "tamper driver failed for $kind"
  commit_case "$CASE" "S-0 per-class tamper $kind"
  capture "110-tamper-$kind" "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$CASE/$FIRST_PACK" \
    --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
    --step6-confirmation-table "$STEP6_TABLE" \
    --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
  case "$kind" in
    plan-json|pinset-json)
      expect_rc "110-tamper-$kind" 1 \
        || die "tamper class $kind did not return rc 1"
      ;;
    *)
      expect_rc "110-tamper-$kind" 2 \
        || die "tamper class $kind did not return rc 2"
      ;;
  esac
  no_traceback "110-tamper-$kind" || die "tamper class $kind failed ugly"
  tampered=$((tampered + 1))
done
test "$tampered" = 8 || die "ran $tampered tamper classes, expected 8"

"$PY" - "$TRANS" "$FIRST_PACK" "$MANIFEST_CODE" "$CHANGED_CODE" "$SUCCESSOR_PINSET" <<'PY' \
  || die 'one or more tamper classes returned the wrong exact refusal'
import json, pathlib, sys
t = pathlib.Path(sys.argv[1])
pack, manifest, changed, pinset = sys.argv[2:]
expected = {
    "source-json": (
        ["readiness_evidence_digest_mismatch"],
        "evidence fact source digest mismatch",
    ),
    "evidence-json": (
        ["readiness_evidence_digest_mismatch"],
        "evidence item digest differs from authenticated bytes",
    ),
    "evidence-sidecar": (
        ["readiness_evidence_digest_mismatch"],
        "evidence item digest differs from authenticated bytes",
    ),
    "freeze-json": (
        ["readiness_freeze_receipt_mismatch"],
        "plan freeze reference is not exact",
    ),
    "freeze-sidecar": (
        ["readiness_receipt_namespace_anomalous"],
        "sidecar mismatch for freeze-0004.json",
    ),
    "plan-json": (
        [manifest],
        f"current dependency differs from its derivation binding: {pack}/plan_tree.json",
    ),
    "plan-sidecar": (
        ["readiness_pack_digest_mismatch"],
        "plan-tree sidecar does not authenticate exact bytes",
    ),
    "pinset-json": (
        [changed],
        f"digest-conditional allowlist path {pinset!r}: "
        "bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest",
    ),
}
for kind, pair in expected.items():
    observed = json.load(open(t / f"110-tamper-{kind}.stdout.json"))
    if (observed.get("reason_codes"), observed.get("detail")) != pair:
        raise SystemExit(f"{kind}: {observed!r}")
PY
```

#### 4. `123-c-to-s-later-rewrite`

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case c-to-s-later-rewrite "$PROBE_BASE")
"$PY" - "$CASE/$SUCCESSOR_PINSET" "$FIRST_PACK" <<'PY' \
  || die 'later-rewrite sibling-row mutation failed'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
target = pathlib.PurePosixPath(sys.argv[2]).name
d = json.loads(p.read_text())
siblings = [row for row in d["packs"] if row["pack_id"] != target]
if not siblings:
    raise SystemExit("pinset has no sibling row")
siblings[0]["plan_sha256"] = "0" * 64
p.write_bytes(
    (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
)
PY
commit_case "$CASE" 'S-0 C-to-S probe: schema-valid sibling-row rewrite'

capture 123-c-to-s-later-rewrite "$PY" "$CASE/scripts/generate_arm_readiness.py" arm \
  --pack-root "$CASE/$FIRST_PACK" \
  --arm-context "$ARM_CONTEXT" \
  --window-custody-root "$CUSTODY/windows" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 123-c-to-s-later-rewrite 1 \
  || die 'later-rewrite probe did not return rc 1'
"$PY" - "$TRANS/123-c-to-s-later-rewrite.stdout.json" "$CHANGED_CODE" "$SUCCESSOR_PINSET" <<'PY' \
  || die 'later rewrite did not reach the authenticated C-to-S gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = (
    f"digest-conditional allowlist path {sys.argv[3]!r}: "
    "bytes at the reviewed HEAD differ from Ed's confirmed step-6 digest"
)
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 123-c-to-s-later-rewrite \
  || die 'C-to-S rewrite probe traceback'
```

#### 5. `119-manifest-binding`

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case manifest-binding "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK" <<'PY' \
  || die 'manifest-binding mutation driver failed'
import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1])

def render(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    path.write_bytes(raw)
    return raw

def sidecar(path, raw):
    path.with_name(path.name + ".sha256").write_text(
        hashlib.sha256(raw).hexdigest() + "  " + path.name + "\n"
    )

source_path = root / "arm_readiness.sources/acceptance-owner.json"
receipt_path = root / "arm_readiness.evidence/evidence-acceptance-owner.json"
plan_path = root / "plan_tree.json"

source = json.loads(source_path.read_text())
source["primary_artifacts"][0]["sha256"] = "0" * 64
source_raw = render(source_path, source)
source_sha = hashlib.sha256(source_raw).hexdigest()

receipt = json.loads(receipt_path.read_text())
old_manifest_sha = receipt["dependency_manifest_sha256"]
if old_manifest_sha == source_sha:
    raise SystemExit("mutation did not change the source digest")
for fact in receipt["facts"]:
    fact["source_sha256"] = source_sha
# Deliberately leave dependency_manifest_sha256 fixed.
receipt_raw = render(receipt_path, receipt)
sidecar(receipt_path, receipt_raw)
receipt_sha = hashlib.sha256(receipt_raw).hexdigest()

plan = json.loads(plan_path.read_text())
freeze_ref = plan["arm_attachments"]["arm_readiness"]["freeze_receipt"]
freeze_path = root / freeze_ref["path"]
freeze = json.loads(freeze_path.read_text())
matches = [
    item for item in freeze["evidence"]
    if item["path"] == "arm_readiness.evidence/evidence-acceptance-owner.json"
]
if len(matches) != 1:
    raise SystemExit(f"expected one acceptance-owner freeze item, got {len(matches)}")
matches[0]["sha256"] = receipt_sha
freeze_raw = render(freeze_path, freeze)
sidecar(freeze_path, freeze_raw)
freeze_ref["sha256"] = hashlib.sha256(freeze_raw).hexdigest()

plan_raw = render(plan_path, plan)
plan_path.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(plan_raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 authenticated manifest source-receipt conjunct'

capture 119-manifest-binding "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 119-manifest-binding 1 \
  || die 'manifest-binding probe did not return rc 1'
"$PY" - "$TRANS/119-manifest-binding.stdout.json" "$MANIFEST_CODE" <<'PY' \
  || die 'source/receipt conjunct did not reach DEPENDENCY_MANIFEST'
import json, sys
d = json.load(open(sys.argv[1]))
if (
    d.get("reason_codes") != [sys.argv[2]]
    or d.get("detail")
    != "evidence source and receipt dependency-manifest bindings disagree"
):
    raise SystemExit(repr(d))
PY
no_traceback 119-manifest-binding || die 'manifest-binding probe traceback'
```

#### 6. `121-s6-r1`

```zsh
source "${S0_ENV:?paste the assignment line from 000-source-line.txt first}"

# CONFIRMATION PAIR, re-pasted per block.
STEP6_TABLE="$CUSTODY/windows/family_publication/d117_step6_confirmation_table_v4.json"
test -f "$STEP6_TABLE" || die 'the promoted step-6 confirmation table is absent'
test -n "${ED_STEP6_CONFIRMED_SHA256:-}" \
  || die "Ed's step-6 confirmation digest (hC) is not pasted into this block"
"$PY" -c 'import re,sys; raise SystemExit(0 if re.fullmatch("[0-9a-f]{64}",sys.argv[1]) else 1)' \
  "$ED_STEP6_CONFIRMED_SHA256" \
  || die 'ED_STEP6_CONFIRMED_SHA256 is not a lowercase 64-hex digest'
test "$ED_STEP6_CONFIRMED_SHA256" = "$(cat "$TRANS/085-ed-step6-confirmed-sha256.txt")" \
  || die 'the pasted hC differs from the 085 witness of the §3.8 confirmation'

CASE=$(new_case s6-dual "$PROBE_BASE")
"$PY" - "$CASE/$FIRST_PACK/plan_tree.json" <<'PY' \
  || die 'S-6 plan mutation driver failed'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text())
d["window_identity"]["evidence_root_id"] += "-s0-s6-mutation"
raw = (json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
p.write_bytes(raw)
p.with_name("plan_tree.sha256").write_text(
    hashlib.sha256(raw).hexdigest() + "  plan_tree.json\n"
)
PY
commit_case "$CASE" 'S-0 S-6 dual-validator manifest-only mutation'

set +e
"$PY" "$CASE/$FIRST_PACK/generate_configs.py" --check \
  --pack-id d117_contrast_qwen25_1p5b_vs_7b_v4 \
  --family-suffix _v4 \
  --preserve-current-frozen-bytes \
  > "$TRANS/120-s6-preserve-check.txt" 2>&1
PRESERVE_RC=$?
set -e
if grep -Eq 'Traceback \(most recent call last\)|^[A-Za-z]+Error:' \
    "$TRANS/120-s6-preserve-check.txt"; then
  die "preserve-mode --check failed ugly (rc $PRESERVE_RC)"
fi
if [ "$PRESERVE_RC" = 0 ]; then
  printf 'disposition=ECHO-HOLE PRESENT\n' >> "$TRANS/120-s6-preserve-check.txt"
else
  printf 'disposition=ECHO-HOLE FIXED (governed nonzero check, rc %s)\n' \
    "$PRESERVE_RC" >> "$TRANS/120-s6-preserve-check.txt"
fi

capture 121-s6-r1 "$PY" "$CASE/scripts/generate_arm_readiness.py" freeze \
  --pack-root "$CASE/$FIRST_PACK" \
  --predecessor-pack-root "$CASE/${PRED_OF[$FIRST_PACK]}" \
  --step6-confirmation-table "$STEP6_TABLE" \
  --expected-confirmation-digest "$ED_STEP6_CONFIRMED_SHA256"
expect_rc 121-s6-r1 1 \
  || die 'S-6 R1 half did not return rc 1'
"$PY" - "$TRANS/121-s6-r1.stdout.json" "$MANIFEST_CODE" "$FIRST_PACK" <<'PY' \
  || die 'S-6 R1 half did not reach the exact DEPENDENCY_MANIFEST gate'
import json, sys
d = json.load(open(sys.argv[1]))
detail = f"current dependency differs from its derivation binding: {sys.argv[3]}/plan_tree.json"
if d.get("reason_codes") != [sys.argv[2]] or d.get("detail") != detail:
    raise SystemExit(repr(d))
PY
no_traceback 121-s6-r1 || die 'S-6 R1 probe traceback'
```

### Vehicle changes and existing coverage

- **The original `105` goal must move.** Per-pack R1 dependency manifests cannot make the first pack depend on an otherwise allowlisted sibling plan — the first-pack replay lawfully PASSes. Use the amended second-pack replay for live coverage. Keep family-wide allowlist exactness in `106-missing`, `107-extra`, and `108-unused`.
- Plan-tree manifest semantics are already directly exercised by `tests/test_arm_readiness_evidence.py:447–480` (a non-slot plan mutation producing `DEPENDENCY_MANIFEST`); the amended `104`, `105`, and `121` add estate-shaped replay coverage.
- C→S is already exercised by `110-tamper-pinset-json` and the six passing tests recorded in `122-c-to-s-unit-probes.txt`. The amended `123` remains useful because it reaches the same gate through the **arm** entry point without losing to target-pack histsem.
- Block 40 contained two latent post-first-failure mismatches (`freeze-sidecar` and `plan-json`); the complete amended `110-*` block repairs both.

---

**Key paths for the cure PR**: `/Users/edr/code/JouleWise/docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md` (the runsheet under repair), `/Users/edr/code/JouleWise/joulewise/arm_readiness.py` (gate code, unchanged), evidence at `/private/tmp/claude-501/-Users-edr-code-JouleWise/eac3ed1d-1740-4cf1-9ab3-b4c539575666/scratchpad/s0-clone-proof-r4/custody/transcripts/` and `/private/tmp/claude-501/-Users-edr-code-JouleWise/eac3ed1d-1740-4cf1-9ab3-b4c539575666/scratchpad/r5-blocks/`. Sol thread `01a03b39-47b5-71f2-a3ce-45f318ab5315` remains available for follow-ups via `codex-reply`.
