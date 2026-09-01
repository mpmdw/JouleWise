```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R1 arithmetic is sound, but the prefix contradiction, unrendered thinking policy, and non-atomic hash check require halting implementation.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-review",
    "base_mode": "exact",
    "head_start": "80912c8dffcac344608963a661791da0eb1d7ced",
    "head_end": "80912c8dffcac344608963a661791da0eb1d7ced",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "label": "HALT-IMPLEMENTATION",
    "findings": [
      {
        "id": "F-01",
        "severity": "blocker",
        "title": "R1 prefix invariant contradicts the ruling",
        "locations": [
          "docs/process_traces/2026-09-01-fresh-model-review/16-sol-g2a-executability-scout.md:226",
          "docs/process_traces/2026-09-01-fresh-model-review/16b-RULING-g2a-producers.md:59"
        ],
        "argument": "The producer requires token-ID prefix relations while R1 explicitly removes that requirement; rung-specific closings can produce legal R1 inputs that the producer rejects.",
        "minimal_change": "Remove the prefix requirement or replace R1 with a common-master-prefix design."
      },
      {
        "id": "F-02",
        "severity": "blocker",
        "title": "Thinking-off policy is not rendered on raw prefill",
        "locations": [
          "joulewise/adapters/mlx_runtime.py:936",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:1413"
        ],
        "argument": "Raw prompt_text is encoded directly; enable_thinking=false belongs to the chat-template pinset and never reaches this path.",
        "minimal_change": "Record explicit raw-prefill/no-chat-template semantics, or switch the probe to rendered prompts."
      },
      {
        "id": "F-03",
        "severity": "blocker",
        "title": "Selection authority hashes are not coupled",
        "locations": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py:890",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:904"
        ],
        "argument": "The pin accepts an arbitrary record_id/path and an independent g2a_record_sha256, so the two authorities can identify different records.",
        "minimal_change": "Require record_id == sha256:<g2a_record_sha256> and verify the referenced bytes."
      },
      {
        "id": "F-04",
        "severity": "blocker",
        "title": "Read-only precheck does not close the ordinary-manifest race",
        "locations": [
          "scripts/gen_g2_phase_d.py:149",
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:418",
          "scripts/run_campaign.py:3020"
        ],
        "argument": "The generated chain only checks file existence; run_campaign ignores manifest config_sha256 and launches a later child by path. A file can change after check and before launch, with only late or no detection.",
        "minimal_change": "Launch from an immutable snapshot or add a race-safe expected-hash boundary immediately before each child."
      },
      {
        "id": "F-05",
        "severity": "should_fix",
        "title": "Summary counts lack authenticated member and prompt provenance",
        "locations": [
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:449",
          "scripts/select_g2a_prefill_length.py:102"
        ],
        "argument": "The small_minimum_count/all_small_count_ge_5 mapping is correct, but the inline reducer trusts run IDs, roles, and counts and does not compare realized prompt token hashes to the ladder pin.",
        "minimal_change": "Authenticate config/member hashes, role/rung identity, and realized prompt count/hash before writing the summary."
      },
      {
        "id": "F-06",
        "severity": "should_fix",
        "title": "G2-a budget is plausible but not proven or guarded",
        "locations": [
          "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:209",
          "configs/campaigns/d117_contrast_v5/generate_configs.py:2835"
        ],
        "argument": "The 24-member/2-calibration evening is roughly 2.5–3 hours by transferred estimates, but the v5 prefill budget remains empty and no bracket budget guard exists.",
        "minimal_change": "Declare the G2-a budget and refuse reservation if the complete bracket cannot fit."
      },
      {
        "id": "F-07",
        "severity": "should_fix",
        "title": "Prompt candidate provenance hardcodes the 2048 closing sentence",
        "locations": [
          "configs/campaigns/d117_contrast_v5/generate_configs.py:1642",
          "docs/process_traces/2026-09-01-fresh-model-review/16b-RULING-g2a-producers.md:41"
        ],
        "argument": "For selected 512, 1024, or 4096 prompts, final_sentence is falsely reported as PROMPT_FINAL_SENTENCE even though R1 requires rung-specific closings.",
        "minimal_change": "Copy the selected ladder closing sentence and construction metadata verbatim."
      },
      {
        "id": "F-08",
        "severity": "nit",
        "title": "NONE ledger labels are too absolute",
        "locations": [
          "scripts/ed_session/build_rehearsal_env.sh:95",
          "joulewise/arm_readiness.py:7742",
          "scripts/calibration_ledger_bootstrap.py:510"
        ],
        "argument": "Rehearsal, synthetic, and issued-artifact producers exist, although none is a valid live G2-a producer.",
        "minimal_change": "Relabel these as rehearsal/synthetic/issued-only and retain no-production-G2-a status."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -c 'from tokenizers import Tokenizer; t=Tokenizer.from_file(\"/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer.json\"); s=\"The plan remains easy to audit.\"; f=\"The plan remains easy to audit and simple to review.\"; print(\"lengths\",len(t.encode(s,add_special_tokens=False).ids),len(t.encode(s,add_special_tokens=True).ids),len(t.encode(f,add_special_tokens=True).ids),len(t.encode(\" \".join([s]*291+[f]),add_special_tokens=True).ids))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "lengths 7 7 11 2048"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^lengths 7 7 11 2048$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 /Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer.json /Users/edr/jw_models/mlx-community/Qwen3-8B-4bit/tokenizer.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4  /Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer.json",
          "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4  /Users/edr/jw_models/mlx-community/Qwen3-8B-4bit/tokenizer.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "aeb13307.*Qwen3-(1\\.7B|8B)-4bit/tokenizer\\.json"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "L1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1's prefix requirement conflicts with its explicit no-prefix ruling.",
      "needs": "Choose common-prefix semantics or remove the prefix invariant."
    },
    {
      "id": "L2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R2 must distinguish panel decode policy from raw-prefill rendering.",
      "needs": "Record raw/no-template semantics or change workload path."
    },
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The current generated bracket does not invoke the proposed check and has no atomic hash boundary.",
      "needs": "Add immutable snapshot or race-safe runner enforcement."
    },
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The worktree has no local .venv; the runsheet-documented parent venv was used and tokenizers 0.22.2 imported successfully.",
      "needs": ""
    }
  ]
}
```

## Findings

1. **BLOCKER — F-01 — R1 has incompatible prompt invariants.** The bench confirms the repeat sentence is 7 IDs with or without specials, the closing sentence is 11 IDs, and 291 repeats plus that closing is exactly 2048. Thus 512/1024/4096 are unreachable as `7r+11`; their required closing lengths are respectively 8/15, 9/16, and 8/15 tokens. Qwen3’s `add_special_tokens=True` adds no BOS/EOS here: `/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer_config.json:2,229`; `16b-RULING-g2a-producers.md:23-36`. Both panel entries and both local tokenizer files share the same SHA: `configs/model_panels/qwen3_4bit.json:17,50`.

   The defect is that the scout still requires a token-ID prefix relation (`16-sol-g2a-executability-scout.md:226,332`) while R1 explicitly says it is not required (`16b-RULING-g2a-producers.md:59-60`). Per-rung closings make the legal R1 output non-prefix-equivalent.

   Exact token length largely dominates prefill cost. v5 requests 10 Hz (`generate_configs.py:493`), and the fiducial interval is 100 ms (`protocol_v3.json:18`). The survey’s 231/49 tok/s figures are decode planning estimates, not prefill rates (`00-SURVEY.md:242,244`). Historical prefill fitting places 2048 near 0.464 s and 4–5 overlapping samples (`02-opus-seat.md:22,41`); the first-token boundary is the actual phase boundary (`mlx_runtime.py:731-810`). The close content therefore has an unregistered last-token/content covariate even though exact token length is held constant.

   Minimal change: remove the prefix invariant and explicitly call the probe prompt-specific, or replace R1 with a single common token-prefix design if the intended claim is length-only.

2. **BLOCKER — F-02 — R2’s raw-path conclusion is correct, but its policy wording is not honest.** The workload docs state that `prompt_text` does not receive a chat template (`joulewise/workloads.py:3-5`); the adapter directly calls `encode(..., add_special_tokens=True)` (`mlx_runtime.py:931-940`), and `_v5` supplies raw `prompt_text` (`generate_configs.py:1413-1418`). The panel’s `chat_template_applied:true` and `enable_thinking:"false"` are decode rendering-pin fields (`qwen3_4bit.json:71-81`), not effective prefill settings. Greedy sampling is genuinely fail-closed in the adapter (`mlx_runtime.py:975-1005`).

   Minimal change: add explicit ladder/inventory fields such as `rendering_mode:"raw_prompt_text"`, `chat_template_applied:false`, and `thinking_policy:"not_applicable"`. Keep the panel’s true/false values for decode. Switching the probe to chat-rendered text would require rebuilding all exact counts.

3. **BLOCKER — F-03 — R3’s ID format is sound, but the pin validator permits split authority.** The selector emits deterministic bytes with sorted JSON and a final newline (`select_g2a_prefill_length.py:150-159`), so `sha256:<selection-record-bytes>` is stable for byte-identical serialization. No consumer requires semantic stability across differently formatted JSON; the estate contract uses the unprefixed `g2a_record_sha256` (`estate-12-delta-template.md:52-55,181-186`).

   However, `_load_prefill_prompt_pin` only requires a nonempty `record_id`/path and an independent 64-hex hash (`generate_configs.py:890-915`). A pin can therefore name record A while hashing record B. Require exact equality and verify the referenced bytes when issuing the pin.

4. **BLOCKER — F-04 — The one-time `check` cannot close the ordinary-manifest hash gap.** The generated bracket checks only that the plan, identity, T1, and manifest files exist (`gen_g2_phase_d.py:149-168`; runsheet `:418`). It does not invoke the proposed `check`.

   `run_campaign` discovers all top-level JSON except two sidecars (`run_campaign.py:1844-1851`), validates manifest shape and coverage but ignores `config_sha256` and most identity fields (`run_campaign.py:2999-3072`), runs doctor later (`:8030-8050`), and passes only the config path to the child (`:1513-1524,8364-8378`). Post-run normalized comparison (`:1253-1280,2822-2836`) is too late and can miss byte-only changes.

   Minimal change: create a private immutable/content-addressed snapshot and launch only from it, or add a race-safe expected-hash boundary immediately before each child. Rechecking a writable path without preventing a subsequent mutation is still insufficient.

5. **SHOULD-FIX — F-05 — R4’s selector mapping is correct but narrower than “every member.”** A4 specifies at least five small members, with large probes non-gating (`03-MAGISTRATE-RATIFICATION.md:53-62`). The summarizer correctly derives `small_minimum_count` and `all_small_count_ge_5` over small members (`SHAKEDOWN-G2-RUNSHEET.md:467-477`), and the selector qualifies on `small_members >= 5` plus the boolean (`select_g2a_prefill_length.py:102-108`). It does not require a large member; that is consistent only because large is explicitly non-gating.

   The current jq summary trusts manifest run IDs and roles and reads only the count from each summary. It does not authenticate config hashes or compare runtime prompt provenance. The adapter records realized prompt count and token-ID hash (`mlx_runtime.py:400-407`), while `_v5` sends text and re-encodes it rather than consuming pinned IDs (`generate_configs.py:1083-1090,1413-1418`). The authenticated summarizer should compare those realized values with the ladder pin before selection.

6. **SHOULD-FIX — F-06 — The evening probably fits, but the design does not prove or guard it.** There are eight stage invocations (`SHAKEDOWN-G2-RUNSHEET.md:415-422`), each preceded by a 600-second settle (`:209,359-378`), plus the pre-calibration settle (`:409`): 90 minutes fixed. Twenty-four members declare 30 seconds idle and 5 seconds warmup (`generate_configs.py:493,1415-1418`), another 14 minutes minimum. Historical member cadence is 148.1 seconds (`02-opus-seat.md:30`), about 59 minutes for 24 members. Two 59-pulse calibrations add several minutes (`protocol_v3.json:12-18`). This is plausibly 2.5–3 hours against the 2–4 hour target (`window_runbook.md:68-71`), but the v5 prefill budget is explicitly empty (`generate_configs.py:2835-2842`). Add a declared budget and pre-reservation refusal guard.

7. **SHOULD-FIX — F-07 — `prompt_candidate()` reports the wrong construction for three possible selections.** It always writes `PROMPT_FINAL_SENTENCE` as `final_sentence` (`generate_configs.py:1642-1644`), while R1 requires distinct closings per rung (`16b-RULING-g2a-producers.md:41-58`). The actual prompt text may be correct, but the audit artifact is false for 512, 1024, and 4096. Copy the selected ladder metadata verbatim.

8. **NIT — F-08 — The object ledger should distinguish “no production G2-a producer” from “no producer anywhere.”** The rehearsal builder writes identity/T1 files from a fixture (`build_rehearsal_env.sh:95-107`), synthetic arm readiness writes them too (`arm_readiness.py:7732-7745`), and calibration bootstrap can emit an issued artifact (`calibration_ledger_bootstrap.py:510-514`). None is valid live G2-a input production, so the implementation conclusion remains unchanged. The ledger should label these exceptions explicitly.

## Rulings I would change

- **NEEDS_RULING — R1:** Keep the arithmetic, no-BOS result, and shared-tokenizer result. Remove the producer’s prefix requirement, or replace the ruled construction with a common master token prefix. The current hybrid cannot be implemented consistently.

- **NEEDS_RULING — R2:** Keep raw prefill, but record that chat-template and thinking policies are not applied. If “thinking disabled” must be effective, the workload must become chat-rendered and all lengths must be regenerated.

- **R3:** Keep the `sha256:<bytes>` format. Add the equality invariant against `g2a_record_sha256` and verify the referenced path bytes.

- **R4:** Keep the five-small/one-large default and small-only ≥5 rule. Change the execution closure to an authenticated summary plus immutable hash boundary, and add a budget guard.

## Residual risk

No measurement or `[QUIET-MAC]` command was run. Historical timing and tok/s figures are transferred estimates, not new Qwen3 live evidence. The direct `tokenizers` bench confirms the pinned tokenizer behavior, but the eventual producer should still compare runtime-realized prompt count/hash against the ladder.

VERDICT: HALT-IMPLEMENTATION.