```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1-F4 are fixed and _v4 remains viable, but an implicit-preserve bypass reopens A94 and blocks landing.",
  "workspace": {"base_requested":"2fd7c920314333535ea2631bec887a19b964f834","base_mode":"exact","head_start":"2fd7c920314333535ea2631bec887a19b964f834","head_end":"2fd7c920314333535ea2631bec887a19b964f834","upstream_end":"83f66721a9e4c24c550f12f457adbba98fd646b6","branch":"fix/packauth-soundness-rows"},
  "pathspec": ["docs/process_traces/2026-08-26-t26-s3/delta/a94_implicit_preserve_probe.py","docs/process_traces/2026-08-26-t26-s3/delta/f1_constant_mutation_probe.zsh","docs/process_traces/2026-08-26-t26-s3/delta/f3_lifecycle_probe.py","docs/process_traces/2026-08-26-t26-s3/delta/histsem_timing_probe.py","docs/process_traces/2026-08-26-t26-s3/delta/scope_and_pin_inspection.zsh","docs/process_traces/2026-08-26-t26-s3/delta/report.md"],
  "unowned_dirty": ["docs/contracts/receipt_histsem_verifier.md","joulewise/arm_readiness.py","joulewise/arm_readiness_evidence.py","tests/test_arm_readiness_evidence_packauth.py","tests/test_receipt_histsem.py","docs/process_traces/2026-08-26-t26-s3/ (pre-existing non-delta paths)"],
  "verdict": {
    "overall": "REFUSE",
    "fixes": {
      "F1": "FIXED (constant reads are diagnostic-only; V6 kills reintroduction)",
      "F2": "FIXED (dated normative ruling contains every required choice and limit)",
      "F3": "FIXED (all lifecycle phases govern-refuse at both boundaries; see D3)",
      "F4": "FIXED (closed documented vocabulary; exact predecessor equality; no consumer)"
    },
    "acceptance": {
      "A93": "MET (normative ruling + V6)",
      "A94": "NOT MET (D1/V7)"
    },
    "findings": [
      {
        "id": "D1",
        "severity": "blocker",
        "title": "Flagless preserve detection is a naming heuristic, so echo can be recorded as regenerated",
        "file_line": "joulewise/arm_readiness_evidence.py:1103-1115,1180-1193",
        "failure_scenario": "A generator reads existing bytes under saved and returns zero. The name scan finds no preserve_current_frozen_bytes substring, invokes it bare, labels it regenerated from caller intent, and both author and histsem accept changed bytes (V7).",
        "suggested_cure": "Default-deny flagless generators except a closed reviewed-digest allowlist, or regenerate into an empty output tree. Require the explicit two-way flag for modern generators and pin V7 at both boundaries."
      },
      {
        "id": "D2",
        "severity": "should_fix",
        "title": "The normative ruling does not teach the custody/echo tautology mechanism from first principles",
        "file_line": "docs/contracts/receipt_histsem_verifier.md:109-174",
        "failure_scenario": "Custody coordinate and tautology are undefined, and echo lacks a concrete same-bytes example; the reader cannot reconstruct the self-confirming comparison or contrast it with derivation.",
        "suggested_cure": "Define both coordinates at first use, then show an echo accepting the same current plan_tree.json after mutation and contrast it with regeneration from pinned inputs."
      },
      {
        "id": "D3",
        "severity": "should_fix",
        "title": "F3's committed regression covers allocation only and the normative materialization reason code disagrees with runtime",
        "file_line": "tests/test_receipt_histsem.py:656-677; docs/contracts/receipt_histsem_verifier.md:163-165",
        "failure_scenario": "The regression raises only at TemporaryDirectory construction, so cleanup can regress unnoticed. Clone OSError returns histsem_git_unavailable although the contract promises histsem_history_unavailable for materialization.",
        "suggested_cure": "Test allocation, clone, and cleanup at arm/freeze with no leaks; then align clone classification with the contract or document the specific Git code."
      }
    ],
    "mint_hazard": {
      "projected_authorship": "PASS; all three emitters have the explicit two-way flag",
      "projected_histsem": "PASS via anchor+replay; bare projected check REFUSES",
      "scripts": "UNCHANGED; sidecars verify",
      "history_failure": "GOVERNED FAIL-CLOSED",
      "timing": "+2.245s/gate median; acceptable"
    }
  },
  "verification": [
    {"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness_evidence_packauth","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 27 tests in 52.959s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 27 tests.*OK"}},
    {"id":"V2","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_receipt_histsem","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 36 tests in 165.976s","","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 36 tests.*OK \\(skipped=1\\)"}},
    {"id":"V3","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 0.601s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 37 tests.*OK"}},
    {"id":"V4","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_readiness_schemas","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 23 tests in 0.047s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 23 tests.*OK"}},
    {"id":"V6","kind":"test","cmd":"zsh docs/process_traces/2026-08-26-t26-s3/delta/f1_constant_mutation_probe.zsh","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 1.262s","","FAILED (errors=6)","MUTATION_TEST_RC=1"]},"expected":{"exit_code":0,"tail_regex":"FAILED \\(errors=6\\).*MUTATION_TEST_RC=1"}},
    {"id":"V7","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B docs/process_traces/2026-08-26-t26-s3/delta/a94_implicit_preserve_probe.py","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["{\"after_exit\": 0, \"after_mode\": \"regenerated\", \"before_exit\": 0, \"before_mode\": \"regenerated\", \"capability\": {\"has_preserve_mechanism\": false, \"supports_boolean_optional_preserve_flag\": false}, \"tamper_admitted\": true}"]},"expected":{"exit_code":0,"tail_regex":"\\\"tamper_admitted\\\": false"}},
    {"id":"V8","kind":"smoke","cmd":"/Users/edr/code/JouleWise/.venv/bin/python -B docs/process_traces/2026-08-26-t26-s3/delta/f3_lifecycle_probe.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"cleanup\": {\"arm\": {\"reason_codes\": [\"histsem_history_unavailable\"], \"status\": \"REFUSE\"}, \"freeze\": {\"reason_codes\": [\"histsem_history_unavailable\"], \"status\": \"REFUSE\"}}, \"materialization\": {\"arm\": {\"reason_codes\": [\"histsem_git_unavailable\"], \"status\": \"REFUSE\"}, \"freeze\": {\"reason_codes\": [\"histsem_git_unavailable\"], \"status\": \"REFUSE\"}}}"]},"expected":{"exit_code":0,"tail_regex":"cleanup.*histsem_history_unavailable.*materialization.*histsem_git_unavailable"}},
    {"id":"V9","kind":"smoke","cmd":"/usr/bin/time -p /Users/edr/code/JouleWise/.venv/bin/python -B scripts/verify_receipt_histsem.py --repository-root .","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["  \"status\": \"PASS\"","}","real 49.03","user 22.99","sys 21.85"]},"expected":{"exit_code":0,"tail_regex":"\\\"status\\\": \\\"PASS\\\".*real"}}
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D1 makes A94 NOT MET; do not land.",
      "needs": "Cure flagless echo admission, pin both boundaries, re-audit."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No Metal device; live three-pack U11 was not replayed.",
      "needs": "Lead retains the clean-hardware runsheet gate."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD stayed 2fd7c920; branch ends 19 behind origin/main 83f66721.",
      "needs": "Lead owns integration and conflict review."
    }
  ]
}
```

## Findings

F1 = FIXED — the only production extraction of `CURRENT_FROZEN_RECEIPT_SHA256` is the total diagnostic extractor. Its value, status, and relation flow only into recorded checks/primaries; neither `_generator_invocation`, `_require_regenerated_generator_result`, the author verdict, nor the histsem verdict reads them. The physical `/tmp` mutation restored a constant-dependent refusal and the named regression failed in six variants, so it would catch reintroduction.

F2 = FIXED — the 2026-08-26 normative A93 section states the adopted choice, why refresh is impossible, the compatibility-only role, the rejected circular alternative, the exact regression name, and the honest limit for `pack_generator_check_status: PASS`. D2 is a remaining pedagogy defect, not an absence of the ruling.

F3 = FIXED — `histsem_history_unavailable` pre-existed this diff and fits workspace allocation/use/cleanup failures. Allocation and cleanup produce that code; bounded Git clone materialization produces the pre-existing, more specific `histsem_git_unavailable`. Both freeze and arm return governed REFUSE results, and the temporary tree is cleaned. D3 records that tests and normative prose do not pin that full distinction.

F4 = FIXED — exact predecessor equality is required for `names_predecessor`; unrelated readable values and unreadable extraction states have separate documented values. Exhaustive consumers show the relation is diagnostic only, so no unknown relation is interpreted as authority.

ACCEPTANCE A93 MET — evidence item: the adopted normative ruling plus `test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict`, calibrated by V6.

ACCEPTANCE A94 NOT MET — evidence item D1/V7: an implicit preserve generator can run bare and have echo output recorded as `regenerated`.

**D1 — blocker. Flagless preserve detection is a naming heuristic, so echo can be recorded as regenerated.** The classifier treats absence of the literal identifier substring `preserve_current_frozen_bytes` as proof that no preserve behavior exists. V7 changes the bytes consumed by a generator that accepts the already-present bytes under `saved`; both calls pass and are labeled `regenerated`. The author and histsem verifier share this path. This is the prohibited A94 self-confirmation and must be cured before landing.

**D2 — should_fix. The normative ruling does not teach the custody/echo tautology mechanism from first principles.** Derivation coordinate, regeneration, projected state, anchor, and replay receive useful mechanical definitions. `custody coordinate` and `tautology` are absent, while the late echo gloss has no concrete before/after byte example. Add those definitions at first use so the claim can be replicated from the contract alone.

**D3 — should_fix. F3's committed regression covers allocation only and the normative materialization reason code disagrees with runtime.** V8 proves current clone and cleanup failures are governed at both boundaries, but only allocation is durably tested. The contract also groups all materialization under `histsem_history_unavailable`, whereas clone execution returns `histsem_git_unavailable`. Pin all lifecycle phases and align the normative vocabulary.

The `_v4` mechanism itself remains operable in current code: each of the three emitting `_v3` generators exposes the explicit `BooleanOptionalAction`, so authentication selects `--no-preserve-current-frozen-bytes`; a U11-projected PACK_AUTH receipt passes via pre-projection anchor regeneration plus exact replay; and a bare check at the projected coordinate refuses. The unchanged verifier and pinset builder match their tracked sidecars, the full verifier validates all 99 already-committed receipts across nine packs, and shallow/missing/unresolvable history remains fail-closed. Median re-derivation overhead is 2.245 seconds at each pre-freeze or pre-arm gate, approximately 6.7 seconds for three packs at either stage, which is acceptable for the operator runsheet.

## Residual risk

The seat could not repeat the hardware-backed three-pack U11 projection because importing `mlx_lm` fails with `No Metal device available`. The conclusion for runsheet sections 3.2-3.7 therefore rests on the pack-generic current-code path, all three real generator capability classifications, focused projected author/histsem tests, unchanged script bytes, and the lead-owned live hardware gate; it is not presented as new live U11 evidence.
