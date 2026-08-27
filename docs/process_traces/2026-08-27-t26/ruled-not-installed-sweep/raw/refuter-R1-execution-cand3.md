```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "CAND-3 is confirmed: _v4 science stages pass manifest-free stage directories to the collector, producing null provenance that the finalized-v3 claim join cannot select.",
  "workspace": {
    "base_requested": "0dd3b6dc",
    "base_mode": "informational",
    "head_start": "f4eac40b1ecb7003297d4393876fd942d8751548",
    "head_end": "f4eac40b1ecb7003297d4393876fd942d8751548",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "CANDIDATES.md"
  ],
  "verdict": {
    "result": "CONFIRMED",
    "findings": [
      {
        "id": "CAND-3",
        "severity": "blocker",
        "summary": "The v4 collector receives numbered science-stage directories containing no recognized analysis manifest, records analysis_manifest_id null, and the current finalized-v3 claim path selects no matching cooldown provenance.",
        "cure": "Emit a stable v3 collection manifest ID, pass the pack-root v3 manifest explicitly to every science-stage run_campaign invocation, add v3 validation in the collector, and persist that ID in campaign provenance."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "find configs -type f \\( -name 'analysis_manifest.json' -o -name 'analysis_manifest_v3.json' \\) -print",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/analysis_manifest_v3.json",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/analysis_manifest_v3.json",
          "configs/campaigns/splitwise_decode_v1/analysis_manifest_v3.json",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "analysis_manifest_v3\\.json"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; from pathlib import Path; from scripts.run_campaign import load_analysis_manifest; paths=[Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3\"),Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/01_decode_contrast_blocks_01_05\")]; [print(\"%s: analysis_manifest.json=%s analysis_manifest_v3.json=%s return=%r\" % (p,(p/\"analysis_manifest.json\").is_file(),(p/\"analysis_manifest_v3.json\").is_file(),load_analysis_manifest(p))) for p in paths]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3: analysis_manifest.json=False analysis_manifest_v3.json=True return=None",
          "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/01_decode_contrast_blocks_01_05: analysis_manifest.json=False analysis_manifest_v3.json=False return=None"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "return=None"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; from pathlib import Path; from types import SimpleNamespace; import joulewise.analysis_engine.inputs as x; raw={\"schema_version\":x.CAMPAIGN_PROVENANCE_SCHEMA_V1,\"analysis_manifest_id\":None,\"session_id\":\"s\",\"first_physical_run_id\":\"b1\",\"members\":[{\"execution\":\"invoked\",\"run_id\":\"b1\",\"bundle_ids\":[\"b1\"],\"preceding_campaign_cooldown\":{\"result\":\"first_run_exempt\",\"session_id\":\"s\",\"following_run_id\":\"b1\"}}]}; x.load_authenticated_campaign_catalog=lambda *a,**k:[SimpleNamespace(path=Path(\"campaign-null.json\"),value=raw)]; x.supersession_entry_validation_results=lambda *a,**k:([],[]); x.load_campaign_log_rows=lambda *a,**k:[]; print(\"manifest_id=v3-id -> %r\" % x.campaign_cooldown_evidence(Path(\"/read-only\"),\"v3-id\")); print(\"manifest_id=None -> %r\" % x.campaign_cooldown_evidence(Path(\"/read-only\"),None))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "manifest_id=v3-id -> {}",
          "manifest_id=None -> {'b1': {'result': 'first_run_exempt', 'verified': True, 'session_id': 's', 'manifest': 'campaign_manifests/campaign-null.json', 'raw_artifact': None}}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "manifest_id=v3-id -> \\{\\}"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The v4 roots do not yet exist in this checkout and could not be generated under the read-only mandate; the generator's v4 identity transformation was executed without writes and returned the v4 stage directory plus only analysis_manifest_v3.json.",
      "needs": ""
    }
  ]
}
```

## Findings

CAND-3 — blocker — CONFIRMED.

The freeze transaction itself does not collect: it generates `_v4` roots from the `_v3` generators ([s0-runsheet-r4.md:1482](/Users/edr/code/JouleWise-wt-s9-r1/docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1482)), then performs readiness dry-runs with no real arm ([real-transaction-runbook.md:1054](/Users/edr/code/JouleWise-wt-s9-r1/docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1054)). Collection begins on later physical windows.

On those windows, `launch_window.py` authenticates the launch manifest and `execve`s its frozen command unchanged ([launch_window.py:143](/Users/edr/code/JouleWise-wt-s9-r1/scripts/launch_window.py:143), [launch_window.py:239](/Users/edr/code/JouleWise-wt-s9-r1/scripts/launch_window.py:239)). The chain reads repository-relative stage-directory lines and passes each exact directory to `run_campaign.py` ([window_runbook.md:1456](/Users/edr/code/JouleWise-wt-s9-r1/docs/phase_2/window_runbook.md:1456), [window_runbook.md:1480](/Users/edr/code/JouleWise-wt-s9-r1/docs/phase_2/window_runbook.md:1480)). Thus `config_dir` is a numbered science-stage directory, not the pack root or a derived staging directory. The frozen gamma graph demonstrates that shape directly ([plan_tree.json:2507](/Users/edr/code/JouleWise-wt-s9-r1/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/plan_tree.json:2507)); v4 generation mechanically substitutes the generation identity during serialization ([generate_configs.py:284](/Users/edr/code/JouleWise-wt-s9-r1/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:284), [generate_configs.py:514](/Users/edr/code/JouleWise-wt-s9-r1/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:514)).

The generator writes `analysis_manifest_v3.json` only at the pack root ([generate_configs.py:2110](/Users/edr/code/JouleWise-wt-s9-r1/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:2110)); numbered stages receive only their configs and `order_manifest.json` ([generate_configs.py:647](/Users/edr/code/JouleWise-wt-s9-r1/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:647)). Freeze writes only its receipt and updates `plan_tree.json` ([arm_readiness.py:7004](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/arm_readiness.py:7004)); arm/dry-run explicitly detect any pack-byte mutation ([generate_arm_readiness.py:115](/Users/edr/code/JouleWise-wt-s9-r1/scripts/generate_arm_readiness.py:115)). Packaging handles completed bundle directories, not campaign configs ([package_bundle_pack.py:774](/Users/edr/code/JouleWise-wt-s9-r1/scripts/package_bundle_pack.py:774)). No searched route materializes the v3 file under the collector basename.

The collector hardcodes `analysis_manifest.json`, returns `None` when absent, and has only v2-versus-v1 validation dispatch ([run_campaign.py:195](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:195), [run_campaign.py:1201](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:1201)). The apparent AXI copy writes an already-loaded v2 manifest into run evidence after dispatch; it cannot seed `config_dir` ([run_campaign.py:6506](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:6506), [run_campaign.py:7354](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:7354)).

`new_campaign_provenance` is the only producer and converts the missing state to `analysis_manifest_id: null` ([run_campaign.py:2987](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:2987)); subsequent writes only serialize that dictionary ([run_campaign.py:3018](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:3018)). The repair route only re-attests existing bytes ([run_campaign.py:3154](/Users/edr/code/JouleWise-wt-s9-r1/scripts/run_campaign.py:3154)).

Finally, this is on the current v3 claim path: `_cmd_analyze_claims` calls `analyze_claims` ([cli.py:2003](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/cli.py:2003)), which calls `load_analysis_inputs` before any legacy branch ([analysis_engine/__init__.py:1657](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_engine/__init__.py:1657)). Finalized v3 supplies its non-null collection identity ([inputs.py:634](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_engine/inputs.py:634), [analysis_manifest_v3.py:3644](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_manifest_v3.py:3644)); the cooldown join requires exact equality ([inputs.py:2143](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_engine/inputs.py:2143), [inputs.py:2191](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_engine/inputs.py:2191)), leaving members with `campaign_cooldown_evidence_missing` ([inputs.py:3443](/Users/edr/code/JouleWise-wt-s9-r1/joulewise/analysis_engine/inputs.py:3443)).

Concrete cure: emit a stable v3 collection ID, pass the pack-root v3 manifest explicitly into every stage invocation, validate v3 in the collector, and persist that same ID.

## Residual risk

The `_v4` roots are transaction outputs and are absent from this checkout. I therefore executed the generator’s v4 identity transformation read-only rather than generating the directories; it returned the expected v4 stage `config_dir` and only the root-relative `analysis_manifest_v3.json` output.