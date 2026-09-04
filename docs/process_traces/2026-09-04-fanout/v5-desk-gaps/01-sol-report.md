```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The ruled close-out arithmetic is present, but pack custody and reader-facing rendering require lead rulings before safe implementation.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc",
    "head_end": "849915bc",
    "upstream_end": "849915bc",
    "branch": "feat/2026-09-04-v5-desk-gaps"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/v5-desk-gaps/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_d165_dominance_closeout tests.test_render_results_fills",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "......................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 102 tests in 20.610s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "if rg -n 'detection_floor_extraction_spec|joulewise\\.(floor_mint_pinset|floor_mint_inputs)\\.v2' configs/campaigns/d117_contrast_v5; then exit 1; else echo 'NEEDS_RULING: no governed extraction specification, final pinset, or v2 input manifest exists in the source generator directory'; fi",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NEEDS_RULING: no governed extraction specification, final pinset, or v2 input manifest exists in the source generator directory"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "NEEDS_RULING"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport re\np = Path('docs/process_traces/2026-09-04-fanout/v5-desk-gaps/01-sol-report.md')\nt = p.read_text()\nfence = chr(96) * 3\nif t.startswith(fence + 'json\\n'):\n    t = t.split('\\n' + fence + '\\n', 1)[1]\nchecks = {\n'extraction specification': 'machine-readable file that names the measured members and calculation components',\n'final pinset': 'post-collection inventory of content hashes that the floor mint may consume',\n'input manifest': 'path map that points the mint to authenticated evidence',\n'generated pack': 'fixed collection plans, configurations, and manifests emitted by the source generator',\n'close-out artifact': 'authenticated decision record that binds the manifest, floor, and replay evidence',\n'successor renderer': 'new program that leaves the frozen historical renderer unchanged',\n}\nrows=[]\nfor term, gloss in checks.items():\n    first = t.lower().find(term)\n    end = t.find('.', first)\n    sentence = t[first:end].lower() if first >= 0 and end >= 0 else ''\n    rows.append((term, first >= 0 and gloss in sentence))\nfor term, ok in rows:\n    print(f'{term}: {\"PASS\" if ok else \"FAIL\"}')\nraise SystemExit(0 if all(ok for _, ok in rows) else 1)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "extraction specification: PASS",
          "final pinset: PASS",
          "input manifest: PASS",
          "generated pack: PASS",
          "close-out artifact: PASS",
          "successor renderer: PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "successor renderer: PASS"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "A final mint pinset contains hashes and observations that do not exist when the collection pack is frozen.",
      "needs": "Rule whether the pack carries non-mintable requirements while the final pinset and path manifest issue in post-collection custody."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The governing material does not choose one shared extraction specification or one specification per floor-producing model.",
      "needs": "Choose the extraction-artifact topology and its exact source and generated paths."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The close-out-backed paper rows name fields but do not fix the professor-facing component labels, sentence grammar, or authenticated renderer input envelope.",
      "needs": "Issue the rendering vocabulary, input envelope, and final-night completion evidence field."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The close-out-backed paper rows are absent at the requested head and exist only on the unmerged paper outcome branch.",
      "needs": "Land or explicitly nominate the paper outcome branch before vocabulary-synchronized renderer implementation."
    },
    {
      "id": "F5",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Writing the generated floor and contrast packs or the paper registry and skeleton is outside the exhaustive write allowlist.",
      "needs": "Expand scope only if this lane must commit generated packs or paper surfaces rather than source code and tests alone."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "configs/campaigns/d117_floor_qwen3-1p7b_v5/**",
      "configs/campaigns/d117_floor_qwen3-8b_v5/**",
      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/**",
      "docs/paper/**"
    ],
    "reason": "These are the generated pack destinations and paper surfaces named by the requested end-to-end closure.",
    "blocked_work": "The final generated artifacts and vocabulary-synchronized paper rendering cannot be landed in this lane.",
    "minimal_change": "Keep source implementation in the current allowlist; add only the generated destinations and exact paper files selected by the lead."
  }
}
```

## Change

An extraction specification is a machine-readable file that names the measured members and calculation components. A final pinset is the post-collection inventory of content hashes that the floor mint may consume. An input manifest is the path map that points the mint to authenticated evidence. A generated pack is the fixed collection plans, configurations, and manifests emitted by the source generator. A close-out artifact is the authenticated decision record that binds the manifest, floor, and replay evidence. A successor renderer is the new program that leaves the frozen historical renderer unchanged while producing reviewed paper text.

The audit compared the governing decisions, close-out contract, live task records, artifact-flow map, mint schemas, source generator, frozen renderer, focused tests, and the fresh paper audit. It also inspected the close-out-backed paper rows on the separate paper outcome branch because those rows are absent from the requested head.

The scoped implementation plan is:

| Work | Evidence required before editing | Acceptance |
|---|---|---|
| Generate floor extraction inputs | An issued topology and exact output paths | Regeneration produces the authenticated member census and a mutation of any member identity is refused |
| Issue mint inputs | An issued custody lifecycle for the final pinset and path manifest | Every final field is bound to authenticated post-collection evidence and the mint accepts the exact bytes |
| Adapt the close-out to paper fills | An issued input envelope, plain-language component vocabulary, and final-night completion field | The historical renderer remains byte-identical; the successor authenticates all sources, selects the close-out branch, and fills only licensed text |
| Replay end to end | All preceding inputs plus fixed examples | Repeated fixture execution produces identical bytes and cannot license live paper text |

Every design-bearing question is recorded below. No production code was changed because each available implementation route would choose an unsettled contract or cross the write boundary.

| Finding | Status | Options considered | Recommendation | Blocked work |
|---|---|---|---|---|
| The pre-collection pack cannot truthfully contain the final mint pinset because the final schema includes the extraction-report digest, bracket digest, terminal calibration-ledger head, observed drift, applied allowance, and emitted component hashes. | `NEEDS_RULING` | Freeze a non-mintable requirements record and issue final files after collection; append final files to the frozen pack; place unresolved placeholders in a file called final | Freeze the requirements record, then issue the final pinset and input manifest in append-only transaction custody after collection | Final pinset and usable input manifest |
| The evidence model supports either one extraction specification per floor-producing model or one shared specification spanning both models, but no reviewed source chooses between them. | `NEEDS_RULING` | Per-model specifications; one shared specification | Use one specification per floor-producing model because the mint authenticates each producer separately and the older production packs use that shape | Extraction-specification generator and pack inventory |
| The path fields in the mint input manifest are interpreted from the command's working directory, while the fixed transaction root is not known when the pack is authored. | `NEEDS_RULING` | Absolute post-collection custody paths; manifest-relative paths with a loader contract change | Use absolute paths in the post-collection manifest because that preserves the current loader contract | Input-manifest author and replay command |
| The current head has no close-out-backed paper rows; the separate paper outcome branch adds a below-threshold component slot and a refusal-stage slot. | `NEEDS_RULING` | Wait for that branch; copy its vocabulary into code before it lands | Land or nominate the paper branch first, then pin the successor to its exact registry and skeleton bytes | Vocabulary census and branch selector integration |
| The paper row says to list failed components but does not define reader-facing names or punctuation for cell identities and component kinds. | `NEEDS_RULING` | Print internal cell identities; map them to plain model-and-phase labels | Issue a closed mapping to plain labels such as model, prompt-processing or token-generation phase, and independent-edge or shared-error calculation | Below-threshold fill text |
| The close-out validator requires the finalized manifest, floor artifact, and replay sidecar bytes, while the paper row names only an authenticated close-out. | `NEEDS_RULING` | A successor input manifest naming all source files; direct command-line paths | Use a closed successor input manifest so replay and paper filling consume the same named byte set | Authenticated close-out adapter |
| The live sentence must wait for the final nightly campaign check, but no exact completion artifact or field is named for the renderer. | `NEEDS_RULING` | Trust an operator flag; require a hash-bound completion record | Require a hash-bound completion record with a closed schema and an exact completed status | Live dominance sentence and subtitle licensing |
| The live task asks for every current fill key, while the mission wording emphasizes only close-out-supplied rows. | `NEEDS_RULING` | Deliver a close-out-only adapter; deliver the full current renderer | Deliver the full successor after the input-length record and paper vocabulary land; keep a close-out projection as an internal stage rather than a second public renderer | Successor acceptance and end-to-end replay |

The mechanical first-use audit of changed prose uses exact first-occurrence searches. The table below is the pasted result from the replay command recorded as verification item `V3`.

| Term | First-use construction | Expected result |
|---|---|---|
| extraction specification | Defines it as the machine-readable member-and-component file | PASS |
| final pinset | Defines it as the post-collection content-hash inventory | PASS |
| input manifest | Defines it as the authenticated-evidence path map | PASS |
| generated pack | Defines it as the generator's fixed collection output | PASS |
| close-out artifact | Defines it as the authenticated decision record and names its bound sources | PASS |
| successor renderer | Defines it as the new program that preserves the historical renderer | PASS |

## Verification notes

The repository-wide test command was not run, as required by the mission preflight rule. Verification was intentionally limited to the pack, close-out, and frozen-renderer modules plus read-only contract probes.

## Residual risk

After the lead issues the rulings, the implementation checklist is: author the chosen extraction topology; add the requirements record to generator inventory; build the post-collection final-pinset issuer and input-manifest issuer; add collision-safe writes and counterfactual mutations; land the paper vocabulary; implement source-byte authentication and branch projection in the successor; require the final-night completion record; replay the full fixed example twice; and run only the focused modules named by the changed files.
