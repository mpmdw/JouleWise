```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Contract review completed: two should-fix findings; registration, probe bindings, frozen sizing and authoring refusals otherwise satisfy the rulings.",
  "workspace": {
    "base_requested": "087bf3afc9f46e11edce9ab0376b0a8f7e2762df",
    "base_mode": "exact",
    "head_start": "087bf3afc9f46e11edce9ab0376b0a8f7e2762df",
    "head_end": "087bf3afc9f46e11edce9ab0376b0a8f7e2762df",
    "upstream_end": "6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 2, "nit": 0},
    "review_range": "0c529f99..087bf3afc9f46e11edce9ab0376b0a8f7e2762df",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "Evidence cleanup dispatch introduces an external-wrapper requirement for legacy courier delivery",
        "call_site": "scripts/run_night.py:1243,1273",
        "counterfactual": "The same completed calibration fixture with a missing wrapper attempts one mocked courier launch at 0c529f99 and zero at HEAD. A REHEARSAL_STUB with its intentionally absent external chain has the same regression."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "Pilot reduction never evaluates the observer-floor stop condition",
        "call_site": "joulewise/quiet_predicate_campaign.py:338",
        "counterfactual": "Twelve constant-energy envelopes with 60 observer CPU-seconds per 600-second envelope produce three proposed pairs and no decision. Passing their 0.1-core observer floor to the existing helper instead produces no cutoff qualifies."
      }
    ],
    "contract_checks": {
      "C1": "PASS. night_gate.py:45-54 defines the digest-keyed table; :1403-1428 refuses unknown registrations with night_refused_registration. :1180-1192 measures the tracked template at measurement_head, compares the wrapper literal and checkout source, and populates C5 without trusting the advisory sidecar. :1408-1417 binds registration to that measurement and prevents borrowing D-166 for evidence. :1431-1435 adds metadata while preserving the calibration detail literal. An ordinary calibration wrapper naming the evidence registration cannot PASS C1: its measured chain-source digest is absent. EvidenceRegistrationTests.test_evidence_cannot_borrow_d166_and_calibration_cannot_borrow_pilot passes.",
      "C2": "PASS. Schema: quiet_predicate_campaign.py:24. Shared one-literal dispatch and probe payload kind ambiguous refusal: night_gate.py:68-81; worker run_night.py:3356-3364; installer night_agent_install.py:793-801. Verify-only exits through the template's lines 11-12 and campaign main :463-468 before execution; verify_environment :103-105 performs import checks. Freshness mirrors v1 at installer :930-938 versus :813-830. Bindings :888-914 and validation :946-951 rederive the manifest; campaign :31-90 compares all manifest files against measurement_head and current bytes. Calibration worker receipt is byte-identical to 0c529f99 on the frozen fixture. Plain-language amendments are present: NIGHT_HANDBACK.md:88 registration refusal, :124-125 payload refusals, :136 table authority, :568-582 payload-specific receipt bindings; derivation_night_runbook.md:3049 adds the evidence verify-only row.",
      "C3": "PARTIAL: R2. Protocol lines 16-37 freeze 600-second settle, 12 x 600-second envelopes, +60/480-second interiors, no load, evidence_busy_cores.jsonl, eight envelopes and four disjoint pairs. Campaign :207-230 and :300-308 apply named mechanisms; busy_cores is read only for descriptive output at :341-354. :321-337 preserves original disjoint pairs and uses sample SD with df=n-1 and the upper-90% chi-square factor; tests verify n=6 -> 1.762 and n=4 -> 2.266. :263-283 implements delta=1 J, max(3,ceil(8*s_upper^2)), and stop above 24. The size stop is connected; the observer-floor stop is not. Block-two upper-bound evidence appropriately remains future work. Protocol SHA-256 is 8fd65255d2167e1817a04f0326002a33d03f4947c1fb2977913b2b099fd76f2f, equal to the table constant. No evidence-generator or campaign CLI override route exists.",
      "C4": "PASS. gen_evidence_night.py:22-25 refuses non-DIAGNOSTIC_NO_PACK, v4 and alternate/calibration templates; :29-43 rejects existing or calibration-shaped chains. :74-80 accepts no protocol override flags. Campaign manifest_for :54-69 authenticates the frozen protocol and window. gen_derivation_night.py and calibration_derivation_only.zsh are byte-identical to 0c529f99. The derivation class, twelve-slot and named-ruling refusal tests pass; its pre-existing explicitly ruled override remains unchanged.",
      "C5": "PASS for the template and rendered fixture. No matches from rg -n -i 'codex|claude|t3' over the generated wrapper, representative execution argv, custody paths, evidence template, generator and campaign module. gen_evidence_night.py:35-38 checks plan ID, measurement/custody roots, wrapper and plan paths; gen_derivation_night.py:69,154-161 supplies the substring refusal. No armed production evidence plan was supplied.",
      "C6": "PARTIAL: R1. Calibration worker probe bytes match 0c529f99; admission differs only by registration_label and registration_ruling, with the original detail unchanged. The 100-test focused replay includes the existing admission compatibility and new probe compatibility tests. Nine additional fence tests finish OK with one census-dependent skip. Driver _terminate_process_group, _stop_probe_group, _courier_argv, _wait_for_courier and dead_man are AST-identical to base; installer changes only its existing validate_probe_receipt function plus new evidence functions. Courier behavior is nevertheless changed by the new unconditional cleanup dispatch."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_run_night.EvidenceProbeTests tests.test_run_night.EvidenceProbeFailureTests tests.test_run_night.CalibrationProbeByteCompatibilityTests tests.test_night_agent_install.EvidenceProbeReceiptTests -v > /tmp/stagea-contract-focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 100 tests in 20.468s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 100 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-contract-oracles.py > /tmp/stagea-contract-oracles.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ORACLES_COMPLETE: no live collect, load, power, courier, or install was launched"]},
      "expected": {"exit_code": 0, "tail_regex": "ORACLES_COMPLETE"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-contract-stub.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REHEARSAL_WITHOUT_EXTERNAL_CHAIN base attempted=1 mock_launches=1", "REHEARSAL_WITHOUT_EXTERNAL_CHAIN head attempted=0 mock_launches=0"]},
      "expected": {"exit_code": 0, "tail_regex": "head attempted=0 mock_launches=0"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-contract-structure.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["BASE_AST_IDENTICAL _terminate_process_group", "BASE_AST_IDENTICAL _stop_probe_group", "BASE_AST_IDENTICAL _courier_argv", "BASE_AST_IDENTICAL _wait_for_courier", "BASE_AST_IDENTICAL dead_man"]},
      "expected": {"exit_code": 0, "tail_regex": "BASE_AST_IDENTICAL dead_man"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n -i 'codex|claude|t3' /tmp/stagea-contract-census.txt scripts/night_chains/quiet_predicate_evidence.zsh scripts/gen_evidence_night.py joulewise/quiet_predicate_campaign.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check 0c529f99 HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "E1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Contract-lens review only. A calibration supervisor test skipped because process census is unavailable in this sandbox. Fixture cleanup assertions are not live hardware evidence.",
      "needs": "Lead retains full execution-suite, process-census and live verification."
    }
  ]
}
```

## Findings

1. **R1 — Preserve legacy courier delivery when no external wrapper exists.**  
   The new [cleanup check](/Users/edr/code/JouleWise-wt-sarefc-d0b83820/scripts/run_night.py:1243) reads `plan.chain_path` before establishing that this is an evidence night. Any read failure suppresses delivery at [the courier entry point](/Users/edr/code/JouleWise-wt-sarefc-d0b83820/scripts/run_night.py:1273).

   This breaks legitimate `REHEARSAL_STUB` plans, whose [built-in command](/Users/edr/code/JouleWise-wt-sarefc-d0b83820/scripts/run_night.py:2911) needs no external chain. It also changes calibration delivery when the completed night’s wrapper becomes unavailable. Both counterfactuals produced **base: one mocked launch; HEAD: zero**. Restrict evidence cleanup using preserved, authenticated payload identity, and add regressions that exercise the real courier function.

2. **R2 — Connect measured observer cost to the observer-floor stop.**  
   [The summary calls `stop_branch` with only `s_upper`](/Users/edr/code/JouleWise-wt-sarefc-d0b83820/joulewise/quiet_predicate_campaign.py:338). The helper’s [observer-floor condition](/Users/edr/code/JouleWise-wt-sarefc-d0b83820/joulewise/quiet_predicate_campaign.py:279) is therefore unreachable from pilot reduction.

   A fixture with twelve constant-energy envelopes and **0.1 core of observer cost** reported three pairs and `"no decision"`. Supplying that floor to the existing helper correctly yielded `"no cutoff qualifies"`. Connect the measured observer floor to the summary’s stop evaluation; keep it separate from envelope exclusions.

## Residual risk

All C1–C6 checks have answers above. Execution-lens X1–X5 were not assigned. The focused run passed **100 tests**; nine additional fence tests completed with **one census-dependent skip**. No live collection, load, power sampling, installation, or courier launch occurred. The worktree remains clean and unchanged.