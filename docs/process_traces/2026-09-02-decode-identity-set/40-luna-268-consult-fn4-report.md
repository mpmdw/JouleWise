# luna 268 (gpt-5.6-luna xhigh, read-only, wt-decode-id3 @ fbedfb04) — consult on packet file 38 (F-N4, fourth prose signature)

Custodied verbatim (scratchpad paths redacted). Headline: Q1 = (b) (distinct defect, same class; this consult suffices, one changed-formulation round; another same-shape failure meets the cold-gate trigger). Q2: Cure A not landable as written (retains the unglossed direct-call label; "EVERY path" over-cites); Cure B's window-root gloss CONTRADICTED (code: `window_plan_root`, lifecycle receipts in a sibling custody dir); proposes a third cure = Cure A with the label deleted/glossed and the path claim narrowed. Q3: mechanical first-use table would have caught F-N4, not S1 → two-pass gate (first-use table + clause-to-code ledger with ordering probe). Q4: propose to Ed as a narrowly scoped rule; it is itself a cold-gate item. Not yet synthesized — Opus and blind-Fable seats not launched (paused for usage).

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F-N4 is a distinct first-use defect in the recurring prose class; Cure A is incomplete, Cure B has a contradicted window-root gloss, and a two-pass pre-landing gate is the strongest fourth formulation.",
  "workspace": {
    "base_requested": "fbedfb04",
    "base_mode": "exact",
    "head_start": "fbedfb040805828a0b8a48bb6455dba57c0555a6",
    "head_end": "fbedfb040805828a0b8a48bb6455dba57c0555a6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "F-N4",
        "severity": "should_fix",
        "title": "The lineage paragraph introduces six lineage terms and the direct-call refusal label before definitions or glosses."
      },
      {
        "id": "F-CURE-A",
        "severity": "should_fix",
        "title": "Cure A removes most upstream vocabulary but retains consumer_identity_set_unauthenticated before its later explanation and cites too little to prove EVERY path."
      },
      {
        "id": "F-CURE-B",
        "severity": "should_fix",
        "title": "Cure B's window-root gloss is not supported and conflicts with the code's window_plan_root and separate lifecycle custody."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fbedfb040805828a0b8a48bb6455dba57c0555a6",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fbedfb040805828a0b8a48bb6455dba57c0555a6\\n## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "grep -n -E 'consumption receipt|launch manifest|window root|lifecycle receipts|launch_binding_mismatch|launch_consumption_missing|consumer_identity_set_unauthenticated' docs/contracts/identity_pin_projection.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "614:refused at input loading (`launch_binding_mismatch`, or",
          "615:`launch_consumption_missing` when the consumption receipt itself is gone) and",
          "620:`consumer_identity_set_unauthenticated`, the same label as any pack it cannot",
          "634:The gate refuses with `consumer_identity_set_unauthenticated` when successor",
          "671:digest, **launch manifest** (the JSON declaration of the reviewed command and"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "614:.*launch_binding_mismatch.*\\n615:.*launch_consumption_missing.*\\n620:.*consumer_identity_set_unauthenticated"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/arm_readiness.py | sed -n '10596,10682p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "10668:    return authenticate_launch_lineage(",
          "10669:        lineage, require_completion=require_completion",
          "10670:    )"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "10668:.*authenticate_launch_lineage"
      }
    }
  ],
  "flags": [
    {
      "id": "FL-1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test suite or live/moved-bundle replay was run; this was a read-only prose and source-evidence consult.",
      "needs": "Lead-owned implementation verification after disposition."
    },
    {
      "id": "FL-2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The proposed process gate is advice for Ed and was not installed.",
      "needs": "Ed/cold-gate disposition under the proposed-process-rule trigger."
    }
  ]
}
```

## Findings

### Q1 — classification

Answer: **(b)**.

The controlling trigger is exact:

> “Any second fix round on the same defect.”  
> `docs/process/coldgate_charter.md:29–39`

The standing structural rule separately says:

> “Two consecutive rounds failing with the same signature is a structural problem: the next spend is a consult or redesign, not round three.”  
> `docs/process/coldgate_charter.md:136–139`

F-N4 is the same recurring first-use/prose defect class, but it is a distinct defect in the §Analysis consumption paragraph at `identity_pin_projection.md:609–621`. S1 was the factual ordering error in the freeze-procedure paragraph; the prior synthesis records those as different paragraphs and different failure mechanisms (`32-magistrate-synthesis-s1-s3.md:37–52`). Therefore F-N4 is not a second fix round on the exact same defect, but the four-round signature warrants this consult. One changed-formulation round after this consult is justified; another same-shape failure would meet the cold-gate trigger.

### Q2 — cure grading

The replication bar is the charter’s burden-of-proof rule: load-bearing claims need primary, reproducible evidence (`coldgate_charter.md:70–78`).

#### Cure A

| Clause | First-use grade | Replication grade |
|---|---|---|
| Deletes consumption receipt, launch manifest, window root, lifecycle receipts, and the two upstream codes | PASS | PASS |
| Retains `launch lineage` | PASS: defined at `identity_pin_projection.md:584–585` | PASS |
| Says bundle loading authenticates before evidence construction | PASS | PASS with `inputs.py:2768–2782` and `arm_readiness.py:10608–10669` |
| Says it resolves EVERY arming-time path | PASS structurally | PARTIAL: `_replay_consumed_arm` proves the pack-root path only; the broader claim also needs `arm_readiness.py:10127–10252` |
| Retains `consumer_identity_set_unauthenticated` | FAIL: first used at :620, explained only at :634–659 | Direct-gate behavior is supported, but the literal still needs an inline gloss or deletion |

Cure A is therefore not landable as written. Its strongest defect is that it claims to remove upstream vocabulary while retaining the unglossed direct-call code literal. Its citation to `_replay_consumed_arm` alone also does not prove “EVERY path.”

#### Cure B

The inline structure passes the first-use test, but the factual glosses grade as follows.

Consumption receipt — **PROVEN**. The code creates the record, fsyncs custody, and explicitly identifies the no-clobber write as the single-use point:

```text
9751    consumption_dir = custody_pack_root / "arm_readiness.consumptions"
9755    # Python caller identity is not authenticated here.  This atomic
9756    # no-clobber primary is the only real enforcement and the single-use
9757    # linearization point; every later complete caller must lose this write.
9758    try:
9759        _exclusive_write(consumption_path, raw)
9760    except ArmReadinessError as exc:
9761        if exc.reason_code == "readiness_output_collision":
9762            raise ArmReadinessError(
9763                "readiness_record_consumed", "launch capability was already consumed"
9764            ) from exc
9766    _fsync_directory(consumption_dir)
```

Launch manifest — **PROVEN**. It is parsed as canonical JSON, validated against exact keys, and its command is compared with the consumed command:

```text
2569 def validate_launch_manifest(value: object) -> Mapping[str, Any]:
2570     manifest = _require_exact_keys(value, LAUNCH_MANIFEST_KEYS, "launch manifest")
2571     if manifest["schema_version"] != LAUNCH_MANIFEST_SCHEMA:
2575     _require_boot_session_id(manifest["boot_session_id"], "launch manifest.boot_session_id")
2576     _require_string(manifest["window_plan_root"], "launch manifest.window_plan_root")
2581     _validate_string_argv(manifest["prewindow_command"], "launch manifest.prewindow_command")
2582     _validate_string_argv(manifest["launch_command"], "launch manifest.launch_command")
```

```text
10193    try:
10194        manifest = validate_launch_manifest(
10195            parse_json_bytes(manifest_raw, require_canonical=True)
10196        )
10197    except ArmReadinessError as exc:
10198        raise LaunchLineageError("launch_consumption_invalid", str(exc)) from exc
10220    manifest_argv = list(manifest["launch_command"])
10221    if (
10222        manifest_path != Path(str(consumption["launch_manifest"]["path"])).resolve(strict=True)
10223        or manifest["boot_session_id"] != consumption["boot_session_id"]
10224        or manifest_argv != consumption["exec_argv"]
10225        or not _launch_argv_matches(
10226            manifest_argv, chain_path=chain_path, window_root=window_root
10227        )
```

Window root — **CONTRADICTED/unsupported**. The code calls it `window_plan_root`, resolves it strictly, and binds only `window.env` and `window-chain.zsh` beneath it. Lifecycle receipts are stored in a separate sibling custody directory:

```text
8939        window_root = Path(str(manifest["window_plan_root"])).resolve(strict=True)
8945    env_reference = _launch_artifact_reference(
8946        window_root / "window.env",
8951    chain_reference = _launch_artifact_reference(
8952        window_root / "window-chain.zsh",
```

```text
9781 def _lifecycle_receipt_path(consumption_path: Path, event: str) -> Path:
9782     consumption, _raw, _digest, resolved = _read_v2_consumption(consumption_path)
9783     return (
9784         resolved.parent.parent
9785         / "arm_readiness.launch_lifecycle"
9786         / f"{consumption['consumption_id']}.{event}.json"
```

The gloss should instead say: “the absolute window-plan directory whose `window.env` and `window-chain.zsh` are bound.”

Lifecycle receipts — **PROVEN**, with the location correction above. The writer creates start, settle, and completion records with predecessor/order bindings and no-clobber custody:

```text
9917    """Append one start/settle/completion receipt with no-clobber custody."""
9957        predecessor_event = "start" if event == "settle" else "settle"
9974        schema = (
9975            LAUNCH_SETTLE_RECEIPT_SCHEMA
9976            if event == "settle"
9977            else LAUNCH_COMPLETION_RECEIPT_SCHEMA
9979        kind = f"launch_{event}"
9985    receipt = {
9986        "schema_version": schema,
9987        "receipt_kind": kind,
9988        "receipt_id": f"{consumption['consumption_id']}-{event}",
10005   validate_launch_lifecycle_receipt(receipt)
10006   path = _lifecycle_receipt_path(consumption_path, event)
10011       _exclusive_write(path, raw)
```

Reason-code gloss — **PROVEN for the stated cases, but incomplete as a definition**. Missing consumption maps to `launch_consumption_missing`:

```text
8963    path = Path(consumption_receipt).resolve(strict=False)
8964    value, raw, digest = _read_launch_lineage_primary(
8965        path, missing_code="launch_consumption_missing"
```

```text
8856    except OSError as exc:
8857        raise LaunchLineageError(
8858            missing_code, f"launch-lineage receipt is absent: {path}: {exc}"
8859        ) from exc
```

A missing consumed-arm pack root maps to `launch_binding_mismatch`:

```text
9333        recorded_pack_root = Path(str(arm["pack"]["pack_root"])).resolve(
9334            strict=True
9348    except (ArmReadinessError, OSError) as exc:
9349        raise LaunchLineageError(
9350            "launch_binding_mismatch",
9351            f"consumed arm pack root cannot be authenticated: {exc}",
```

Bundle loading surfaces the reason code before constructing the evidence row:

```text
2773        launch_lineage = authenticate_bundle_launch_lineage(
2779    except LaunchLineageError as exc:
2780        raise AnalysisInputError(
2781            f"{exc.reason_code}: {path.name}: {exc}"
```

However, `launch_binding_mismatch` is broader than unresolved paths; it also covers changed artifact bytes and binding mismatches (`arm_readiness.py:9020–9026`, `:10222–10230`). Use “including when” rather than presenting the gloss as exhaustive.

I would write a third cure: Cure A with the direct label either deleted or locally glossed, and with the “EVERY path” claim narrowed to “the arming-time paths needed for the bundle,” citing `_read_bundle`, `authenticate_bundle_launch_lineage`, `_read_v2_consumption`, `_replay_consumed_arm`, and the manifest/lifecycle checks.

### Q3 — fourth formulation

Executed mechanically:

```text
$ grep -n -E 'consumption receipt|launch manifest|window root|lifecycle receipts|launch_binding_mismatch|launch_consumption_missing|consumer_identity_set_unauthenticated' docs/contracts/identity_pin_projection.md
612:resolves the consumption receipt, the launch manifest, the window root and the
613:lifecycle receipts, so a bundle whose arming-time paths no longer exist is
614:refused at input loading (`launch_binding_mismatch`, or
615:`launch_consumption_missing` when the consumption receipt itself is gone) and
620:`consumer_identity_set_unauthenticated`, the same label as any pack it cannot
634:The gate refuses with `consumer_identity_set_unauthenticated` when successor
671:digest, **launch manifest** (the JSON declaration of the reviewed command and
672:its inputs), and **one-use consumption record** (the durable proof that this
```

| Term | First-use line in paragraph | Definition line or result |
|---|---:|---|
| `launch lineage` | 610 | 584–585 — PASS |
| `pack root` / machine-absolute pack path | 609–611 | NONE; `campaign pack` is described at 34–35, but the exact term is not defined before use |
| `consumption receipt` | 612 | 672–673 later — FAIL |
| `launch manifest` | 612 | 671–672 later — FAIL |
| `window root` | 612 | NONE — FAIL |
| `lifecycle receipts` | 613 | NONE — FAIL |
| `launch_binding_mismatch` | 614 | NONE — FAIL |
| `launch_consumption_missing` | 615 | NONE — FAIL |
| `consumer_identity_set_unauthenticated` | 620 | 634–659 later — FAIL |

Yes, this would have caught F-N4 before landing. It would not have caught S1: S1 was a factual execution-order error, not a definition-order error. S1 requires a second pre-landing ledger mapping each factual clause to code and, for ordering claims, an executed positive/negative probe.

The fourth formulation should therefore be a two-pass gate:

1. Mechanical first-use table before landing, with inline gloss or prior definition required.
2. Clause-to-code verification for every new semantic sentence, including an ordering probe when the prose claims precedence.

The writer attaches both artifacts; an independent seat re-derives both before acceptance.

### Q4 — process rule

Yes, I recommend proposing a narrowly scoped mandatory gate to Ed: apply it to contract-prose edits that add, move, or rename defined terms or code literals. Do not apply it to whitespace or typo-only edits.

The per-edit cost is bounded: one writer-generated `grep -n` table, one independent re-run, and a few evidence lines in the landing record. Semantic or ordering prose additionally requires the clause-to-code ledger and a focused probe.

This is a proposed process rule and therefore itself meets the cold-gate trigger:

> “Any proposed process rule (including amendments to this charter).”  
> `coldgate_charter.md:31–36`

The two-session drop test should be:

- Session 1: run the gate on this lineage paragraph; record F-N4 as the expected unique catch.
- Session 2: run it on the next independent eligible contract-prose edit with a fresh writer/reviewer pair.
- Record applicability, terms checked, writer/reviewer time, unique catches, duplicates, false positives, and misses.
- Retain the rule if either session catches a unique defect or the measured cost is justified.
- If both applicable sessions produce zero unique catches and measurable overhead, send the retirement question to Ed for expected-loss review; do not auto-delete it. Current orchestration explicitly says three applicable exposures trigger review, “never automatic deletion” (`docs/orchestration.md:164–175`).

## Residual risk

No full test suite, P-8 regeneration/freeze/arm verification, hardware run, or fully moved authenticated bundle replay was performed.

## what this consult did NOT check

No files were written. I did not implement either cure, install the process rule, run `unittest discover`, or re-litigate the prior S3 content ruling.