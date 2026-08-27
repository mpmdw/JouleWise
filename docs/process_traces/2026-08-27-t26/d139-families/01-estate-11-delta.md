# S-0 estate 11 — the delta W-10 forces (D-157 R-3)

D-157 R-3: "R-2 touches the mint path, so S-0 re-runs as ESTATE 11 at the new
reviewed head before the transaction." This file is the mechanical delta the
estate-11 operator applies to `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`
and `…/real-transaction-runbook.md`. It is a HANDOFF, not an edit: this stream
was fenced from both documents, and neither was touched.

Derived by the implementing session and reproduced verbatim; the magistrate
should have the estate-11 operator re-derive line numbers at the reviewed head,
because every anchor below is position-dependent.

## What actually changed on the mint path

One new pre-write predicate, `_admit_bound_analysis_manifest`, called from
`generate_freeze_receipt` after predecessor authentication and before the first
write. Nothing else in the freeze sequence moved.

## Runsheet sections affected

§0.2, §0.3, §1.1, §1.3, §3.3, §3.5, §3.6, §4(b.2), §4(i), §5, §6.
Runbook: Phase A anchor checks, C5, C7, C8, §5.2.

**No command text changes in §3.5/§3.6 or runbook C8.** The primary-freeze
invocation is unchanged.

## §0.2 anchor map — 15 anchors become 16

Add the new symbol anchor and renumber:

```python
("joulewise/arm_readiness.py", 4966, "symbol", "_admit_bound_analysis_manifest",
 "def _admit_bound_analysis_manifest("),
("joulewise/arm_readiness.py", 5504, "symbol", "_authenticate_generic_evidence_item",
 "def _authenticate_generic_evidence_item("),
("joulewise/arm_readiness.py", 6570, "symbol", "_load_freeze_reference",
 "def _load_freeze_reference("),
("joulewise/arm_readiness.py", 6844, "symbol", "generate_freeze_receipt",
 "def generate_freeze_receipt("),
("joulewise/arm_readiness.py", 6885, "statement", "generate_freeze_receipt",
 "generation = _pack_generation(root.name)"),
```

`matched == 15` becomes `matched == 16`; `15/15` becomes `16/16`; the
"fifteen anchors" prose and comments become sixteen.

## §0.3 immutable-audit spec — the arm-readiness range list

```
'joulewise/arm_readiness.py 1050,1076p;1999,2120p;3168,3228p;3605,3636p;3639,3707p;4115,4163p;4166,4253p;4256,4399p;4966,5058p;5309,5358p;5361,5580p;5583,5838p;6193,6319p;6322,6357p;6360,6570p;6626,6902p;7403,7649p;10256,10357p;10466,10610p'
```

(`4966,5058p` is the new predicate's range.)

## §1.3 candidate manifest and §3.3 pre-author tests — a third module

```python
"test_modules": ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem", "tests.test_mint_analysis_admission"],
```

and its assertion:

```python
expected = ["tests.test_arm_readiness_schemas", "tests.test_receipt_histsem", "tests.test_mint_analysis_admission"]
```

and the command:

```zsh
"$PY" -m unittest -v \
  tests.test_arm_readiness_schemas \
  tests.test_receipt_histsem \
  tests.test_mint_analysis_admission > "$TRANS/033-pre-author-tests.txt" 2>&1
```

Runbook C5's "exactly two" becomes three and names
`tests.test_mint_analysis_admission`.

## §5 abort semantics — one qualification, and it matters at the machine

The runsheet's blanket prose that every primary-mint refusal WRITES and SPENDS
THE SLOT is no longer true of every refusal. Analysis admission refuses BEFORE
any write: it raises `ArmReadinessError` (CLI rc 2), creates no receipt
namespace, leaves `plan_tree.json` unchanged, and does not spend the freeze
slot. The operator can therefore fix the manifest and re-run the same freeze.
Once admission passes, the existing evaluated-REFUSE poison semantics are
unchanged.

## §4 probes — no expected refusal set changes

- §4(b.2) still reaches `readiness_evidence_unreadable`: an admissible R-1 gamma
  manifest passes admission first.
- §4(i) still writes and replays its plan-pinned evidence REFUSE.
- Receipt-replay probes return before the new predicate.
- Floor-pack probes carry no analysis binding and take the explicit
  non-applicability branch.
- No new readiness reason code enters any expected set: admission reuses the
  registered `readiness_schema_invalid` (validator findings, detail carries the
  underlying `analysis_prospective_*` codes) and `readiness_pack_digest_mismatch`
  (byte tamper).

## Cost

Per the three consult seats: about 10 minutes of estate wall time plus three MLX
freezes, on top of the reviewed-head re-cut.

---

# Second delta, from a different stream: the mint-time measurement-checkout declaration (D-154 R-3, PR #208)

Appended by the S4 stream on 2026-08-27, under the magistrate's ruling that the
pinned `s0-runsheet-r4.md` is **not** edited and that this file is the authority
for what the **r5 cut** carries into estate 11. Same handoff discipline as the
section above: this stream was fenced from the runsheet and did not touch it.
Line numbers are anchors at r4's current bytes and are position-dependent —
re-derive them at the reviewed head.

**This supersedes one sentence of the W-10 delta above.** That section says
"**No command text changes in §3.5/§3.6 or runbook C8. The primary-freeze
invocation is unchanged.**" That was true of W-10's own change. It is no longer
true of the head estate 11 runs at: PR #208 makes `--measurement-checkout` a
**required** argument of `scripts/generate_arm_readiness.py freeze` and of
`scripts/author_arm_readiness_evidence.py`. Both parsers declare it
`required=True` and call `parse_args` before their exception handlers, so an
invocation that omits it prints argparse usage and **exits 2** — no JSON, no
`status`, no reason code. Three runsheet call sites therefore stop working
verbatim at the new head, and each must gain the flag in r5.

## What the flag means, and why the value differs per call site

The declaration names, as an absolute path, the working copy that the mint is
authorised to take its pack bytes from. It is **supplied, never inferred**: the
code reads it from the argument and from nowhere else, and the mint fails closed
without it. The gate resolves the repository that owns the pack and the declared
path, and refuses unless they are the **same physical directory**, with the
reason code `readiness_r1_measurement_checkout`.

So the value is not a constant — **it is whichever checkout is performing that
particular freeze.** For §3.6 that is the estate's own repository root; for
§3.5's sacrificial screen it is the throwaway case clone, because the clone is
what performs that freeze. Declaring the estate root at §3.5 would refuse and
destroy the screen, whose whole purpose is a clean PASS from the same code the
primary mint runs. (Same ruling as runbook C7.)

## The three call sites, with exact strings

**1. §3.4 evidence authoring — r4 `:1771`.** Runs with cwd at `$CLONE`.

```sh
  capture "040-author-$label" "$PY" scripts/author_arm_readiness_evidence.py --pack-root "$pack"
```

becomes

```sh
  capture "040-author-$label" "$PY" scripts/author_arm_readiness_evidence.py --pack-root "$pack" --measurement-checkout "$CLONE"
```

This CLI mints nothing itself, but it **prints the freeze command the operator
runs next**, and it embeds the declaration in what it prints. Without the flag
here it emits a command that dies at argument parsing.

**2. §3.5 sacrificial pre-mint screen — r4 `:1813-1816`.** Runs against
`$PREFLIGHT`, the `new_case pre-mint-clean` clone.

```sh
  "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$PREFLIGHT/$pack" \
    --predecessor-pack-root "$PREFLIGHT/${PRED_OF[$pack]}" \
```

becomes

```sh
  "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze \
    --pack-root "$PREFLIGHT/$pack" \
    --measurement-checkout "$PREFLIGHT" \
    --predecessor-pack-root "$PREFLIGHT/${PRED_OF[$pack]}" \
```

`$PREFLIGHT`, **not** `$CLONE` — see the paragraph above. This is the runsheet's
instance of the runbook C7 ruling.

**3. §3.6 primary freeze ×3 — r4 `:1841-1842`.** Runs with cwd at `$CLONE`.

```sh
  capture "060-freeze-$label" "$PY" scripts/generate_arm_readiness.py freeze \
    --pack-root "$pack" --predecessor-pack-root "${PRED_OF[$pack]}"
```

becomes

```sh
  capture "060-freeze-$label" "$PY" scripts/generate_arm_readiness.py freeze \
    --pack-root "$pack" --measurement-checkout "$CLONE" \
    --predecessor-pack-root "${PRED_OF[$pack]}"
```

`$CLONE` is `"$PROOF/repo"` (r4 `:683`), the estate's repository root and the
checkout that performs this freeze. It is absolute, which the gate requires — a
relative declaration refuses.

## §5 abort semantics — the r5 cut should also carry the runbook's §5.2 change

PR #208's companion docs change rewrote how the runbook tells the operator to
decide whether a refused mint spent the create-only `freeze-0004` slot. **Do not
port a list of "refusals that spend nothing" into r5.** Two attempts to
enumerate that set were both refuted — the first claimed one case, the second
three, and a fresh reviewer found at least seven more reachable pre-write
refusals — so the enumeration was abandoned as the wrong shape: any list is a
snapshot that goes stale as the code changes, and an incomplete one converts a
recoverable typo into an abandoned attempt.

The rule r5 should carry instead is the observable one: the slot is spent if and
only if `PACK_ROOT/arm_readiness.freeze.receipts/freeze-0004.json` **exists**.
Absent → nothing was written, correct the cause and re-issue. Present →
terminal, whatever verdict the file contains. That predicate is total,
conservative in the safe direction, and cannot go stale.

## No other runsheet change

No probe expectation changes: the declaration gate adds no refusal to any §4
probe's expected set, and none of the §4 cases invoke `freeze` or the evidence
author with their own command text. The `--measurement-checkout` value is the
only argument in the runsheet written as an absolute path rather than the bare
relative form, because a relative declaration refuses.

> **This file is co-owned by two T26 streams and merges by APPEND.** The
> D-139/A2 gamma-families stream (branch `fix/d139-a2-gamma-families`) owns the
> sections describing the `_admit_bound_analysis_manifest` mint-path delta —
> the anchor map, the immutable-audit ranges, the affected runsheet and runbook
> sections. This branch (PR #214, T26 S3 pack authentication) contributes only
> the section below. Neither stream's text is reproduced on the other's branch,
> so whichever lands second appends its own section and never rewrites the
> other's. If you are resolving a conflict here, the resolution is "keep both".

## S-1 manifest builder-digest re-pin (S3 D6)

Contributed by the T26 S3 pack-authentication stream (PR #214); it sits in this
handoff because it is another mechanical delta the estate-11 operator carries,
and for no other reason.

### What is wrong

A **custody tool** is one of the four scripts the S-0 operator executes from the
clone during the transaction. Before the first one runs, §3.6.1 recomputes each
executing file's SHA-256 and refuses if it differs from the digest recorded for
that path — this is how the operator learns that the file about to run is the
file that was reviewed.

Two records claim to hold those digests, and they are not the same kind of
thing:

1. `s0-candidate-manifest.json`, whose `custody_tools` map the runsheet
   **computes from the blobs at the reviewed head** at §1.3
   (`s0-runsheet-r4.md:1185`) and which §3.6.1 reads at `:1882`. This is the
   record on the enforcement path.
2. `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md` §6 "Tool
   digests" (lines 184–198), a **hand-transcribed** block recomputed once, at
   the fix-round head on 2026-08-23. Nothing recomputes it. It is a review
   record, not an enforcement input.

Record 2 is now false for one of the four tools:

| Tool | S-1 §6 records | Builder bytes + `.sha256` sidecar today | Agrees |
|---|---|---|---|
| `build_family_marker.py` | `e51617f9…` | `e51617f9…` | yes |
| `verify_family_marker.py` | `68be9c6e…` | `68be9c6e…` | yes |
| **`build_v4_histsem_pinset.py`** | **`29335e6f…`** | **`d72c1560…`** | **NO** |
| `verify_receipt_histsem.py` | `394ed199…` | `394ed199…` | yes |

Full values: recorded
`29335e6fcfe8e97a78212f44e44a96e869d3179afb3411cda74f2a8070b978fa`; actual
`d72c156030d9dc477671924677bff70624aaf878868fb0b5ec3ac4035990b23a`.

### How it drifted, exactly

Two commits changed the builder after S-1 §6 was transcribed, and each one moved
the digest:

| Commit | Date | Subject | Builder SHA-256 after it |
|---|---|---|---|
| `f6a4c81d` | 2026-08-23 | Fix the pinset builder's chain composition (lead pre-execution read catch) | `95d55935…` |
| `cd46e165` | 2026-08-24 | Cure the `_v4` pinset builder's unsatisfiable pre-authoring gate (projection custody) | `d72c1560…` |

The tracked sidecar `scripts/build_v4_histsem_pinset.py.sha256` followed both
moves and reads `d72c1560…` today, so the sidecar mechanism worked. Only the
hand-transcribed block went stale — the failure mode S-1 §6 names in its own
preamble ("a hand-transcribed digest block does not update itself, which is
precisely the drift the `.sha256` sidecar regression exists to catch for the
tools"). It caught it for the tools and not for itself.

### Reproduce it

```zsh
cd <clone>
for f in build_family_marker verify_family_marker build_v4_histsem_pinset verify_receipt_histsem; do
  printf '%s  actual=%s  sidecar=%s\n' "$f" \
    "$(shasum -a 256 scripts/$f.py | cut -d' ' -f1)" \
    "$(cut -d' ' -f1 scripts/$f.py.sha256)"
done
sed -n '194,198p' docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md
```

### Consequence, stated precisely

**The transaction is not blocked and no gate is weakened.** §3.6.1 authenticates
against the generated `s0-candidate-manifest.json`, which is cut from the
reviewed head immediately before execution, so the executing builder is checked
against its own reviewed bytes either way. What is wrong is the **review
record**: a reader who audits the transaction by reading S-1 §6 — the natural
thing to do — is told the reviewed builder is `29335e6f…`, sees `d72c1560…` on
disk, and must either conclude the tool was tampered with or spend the time this
section saves. With the mint imminent, that is a live cost.

### What estate 11 does

Estate 11 re-pins the value. When it re-cuts the reviewed head it recomputes all
four tool digests with the command above and records them in its own estate
artifacts, so the estate-11 record is true at its own head.

**Do NOT edit `docs/process_traces/2026-08-22-t20/s1-candidate/MANIFEST.md`.**
That file is the pinned record of what S-1 reviewed on 2026-08-23; rewriting a
digit inside it would destroy the very evidence that shows the drift happened
and would make the estate-11 correction unfalsifiable. The pinned record stays
as written and this section is the correction that supersedes it — the same
"receipts govern over descriptive bytes" shape the freeze packs already use.
