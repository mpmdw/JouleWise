```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No code findings from static review and in-memory predicate probes; full integration execution and race timing are blocked by unavailable writable temporary storage.",
  "workspace": {
    "base_requested": "0fda6d95",
    "base_mode": "exact",
    "head_start": "6881709d092f0198a52c36d48b1332385a6a1bcf",
    "head_end": "6881709d092f0198a52c36d48b1332385a6a1bcf",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -m unittest tests.test_arm_readiness_lifecycle -k test_atomic_launch_capability_race",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-idle-rc']",
          "Ran 1 test in 0.043s",
          "FAILED (errors=1)",
          "real 1.07",
          "user 1.01",
          "sys 0.03"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_clock_probe_live_anchor_states_and_falsifier_boundaries_gate tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_original_arm_path_samples_once_and_passes_value_explicitly",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.004s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path\nfrom dataclasses import asdict\nimport unittest\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\nns={}\nsource=Path(\"tests/fixtures/arm_clock.py\").read_text()\nexec(source,ns)\ncase=ArmReadinessSchemaTests()\nr=case._clock_predicate_receipt()\nv=r[\"facts\"][0][\"value\"]\nfor p in (\"\",\"r0_\"):\n    v[p+\"anchor_realtime_ns\"]=ns[\"REALTIME_OFFSET_NS\"]+v[p+\"anchor_monotonic_raw_ns\"]\ndef passes(skew,drift):\n    a=ns[\"coherent_clock_anchor\"](raw_ns=v[\"anchor_monotonic_raw_ns\"],skew_ns=skew,drift_ns=drift)\n    return case._probe_passes(r,live_clock_anchor=dict(asdict(a),boot_session_id=r[\"boot_session_id\"]))\nfor s,d,want in ((1000000,5000000,True),(1000001,0,False),(1000,5000001,False)):\n    got=passes(s,d)\n    assert got is want\n    print(s,d,got)\nexec(source.replace(\"read_skew_ns=skew_ns\",\"read_skew_ns=2_000_000\"),ns)\nclass Mutation(unittest.TestCase):\n    def runTest(self): self.assertTrue(passes(1000000,5000000))\nout=unittest.TextTestRunner().run(Mutation())\nassert len(out.failures)==1 and not out.errors\nprint(\"MUTANT_KILLED; predicate-only, integration not executed\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AssertionError: False is not true",
          "Ran 1 test in 0.000s",
          "FAILED (failures=1)",
          "1000000 5000000 True",
          "1000001 0 False",
          "1000 5000001 False",
          "MUTANT_KILLED; predicate-only, integration not executed"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "MUTANT_KILLED; predicate-only, integration not executed"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check 0fda6d95..6881709d; git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "6881709d092f0198a52c36d48b1332385a6a1bcf"]
      },
      "expected": {"exit_code": 0, "tail_regex": "6881709d092f0198a52c36d48b1332385a6a1bcf"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The focused race invocation failed in tempfile.TemporaryDirectory before fixture construction. No repository files were changed.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Full integration/subprocess boundary tests, the full integration mutation, actual race CPU cost, and required concurrent-load/four-worker replay remain unverified. Predicate-only mutation evidence does not discharge these gates.",
      "needs": "Lead must execute the focused and concurrent acceptance checks in a writable test environment, recording exact tails, race outcome, shard count, timer slack and CPU timing."
    }
  ]
}
```

## Findings

None: **0 blockers, 0 should-fix, 0 nits in the reviewed code.** This is not an execution-gate approval. No seat report was assumed or credited.

**1. Determinism — supported by tracing.**

Before this diff:

- `tests/test_arm_readiness_integration.py:176` sampled `readiness._clock_reference.sample_anchor()` while installing evidence.
- Production `joulewise/arm_readiness.py:8690` separately called `_sample_live_clock_anchor()`, whose implementation at `:6723` calls `clock_reference.sample_anchor()`.
- `tests/test_arm_readiness_evidence_t0.py:562` sampled a live anchor for nonsynthetic R0 construction.
- `tests/test_launch_window.py:839` sampled `live_clock_anchor`, rewrote R0’s realtime offset, and supplied that sample to the author. The ARM child subsequently sampled independently.

Now:

- Integration evidence uses `coherent_clock_anchor()` at `tests/test_arm_readiness_integration.py:177`; integration setup patches the underlying sampler at `:314`.
- Lifecycle setup applies the same observation seam at `tests/test_arm_readiness_lifecycle.py:578`.
- Launch `_mint_v4_arm` defaults to the coherent sampler at `tests/test_launch_window.py:535`, obtains one anchor at `:572`, and supplies it to R0 construction and authoring at `:577` and `:842`.
- The child receives its specified observation through `clock_anchor_override` at `:617`.

The child trace is concrete: `_install_synthetic_identity_inputs` writes a numeric-dictionary override of `arm_readiness._sample_live_clock_anchor` into the fixture repository’s `sitecustomize.py` (`tests/test_arm_readiness_evidence_t0.py:294–309`). The child environment sets `PYTHONPATH` to that repository (`tests/test_launch_window.py:665`); the ARM subprocess uses that environment and repository cwd (`:853`). Python imports `sitecustomize` during startup.

Separately, `make_go_fixture` copies `tests/fixtures/arm_clock.py` into the replay repository (`tests/test_arm_readiness_lifecycle.py:420`). `make_author_fixture` starts from that fixture and copies the test modules that import the helper. The template merge into the launch repository retains it. Thus replay imports resolve locally; the ARM observation itself reaches the child as serialized numbers.

I found **no remaining ambient RAW/REALTIME sample on these exercised integration/real-ARM launch paths**. The general fallback at `tests/test_arm_readiness_evidence_t0.py:572` remains, but `_mint_v4_arm` supplies `sample_anchor`. Ordinary-monotonic expiry checks remain capable of refusing under sufficiently long delays.

**2. Real predicates — static integration confirmation; partial execution confirmation.**

Both new tests specify:

| Skew ns | Drift ns | Expected |
|---:|---:|---|
| 1,000,000 | 5,000,000 | PASS |
| 1,000,001 | 0 | REFUSE |
| 1,000 | 5,000,001 | REFUSE |

The integration test at `tests/test_arm_readiness_integration.py:333` asserts status, exact reason codes, one clock row, its verdict, and successful receipt verification for PASS. Each refusal must have exactly `["readiness_clock_preflight_refused"]`.

The subprocess test at `tests/test_launch_window.py:884` passes those observations through the bootstrap seam. `_mint_v4_arm` asserts return code 0/1, status, and exact reason codes (`:870`); the test checks the clock-row verdict.

V2 passed. V3 directly exercised the production `_predicate_passes` path using the new fixture and confirmed all three numeric outcomes. An **in-memory fixture mutation** replacing `read_skew_ns=skew_ns` with `read_skew_ns=2_000_000` killed the PASS assertion:

```text
AssertionError: False is not true
FAILED (failures=1)
MUTANT_KILLED; predicate-only, integration not executed
```

This does **not** establish that the complete new integration or subprocess tests executed successfully. Their fixtures require writable storage.

The additional census test also checks forbidden-process output, probe error, and stale output, with exact authoring refusal codes and unchanged published receipt bytes.

**3. Deletions, assertions and race authentication — no weakening found.**

AST comparison of test-function names produced:

```text
tests/fixtures/arm_clock.py: old=0 new=0 removed=[]
tests/test_arm_readiness_evidence_t0.py: old=68 new=68 removed=[]
tests/test_arm_readiness_integration.py: old=10 new=12 removed=[]
tests/test_arm_readiness_lifecycle.py: old=69 new=69 removed=[]
tests/test_launch_window.py: old=37 new=38 removed=[]
```

Every removed assertion was accounted for:

| Removed assertion at base | Replacement |
|---|---|
| Lifecycle `self.assertFalse(any(thread.is_alive() for thread in threads), "every concurrent consumer must reach a recorded outcome")` | Same no-live-thread assertion using `alive`, with alive names/count, completed consumer IDs, `execve.call_count` and partial outcomes (`:923`). |
| Launch `self.assertEqual(armed.returncode, 0, ...)` | Expected code remains 0 for PASS; explicitly 1 for newly added REFUSE cases (`:870`). |
| Launch `self.assertEqual(arm_result["status"], "PASS", arm_result)` | Expected status defaults to PASS, permits explicitly requested REFUSE, and adds exact reason-code checking (`:875`). |

The race retains eight consumers, the barrier, `join(timeout=30)`, exactly one `execve`, one `launch_consumption_invalid`, seven `readiness_record_consumed`, absence of `readiness_lock_unavailable`, consumption schema validation, and subsequent replay refusal (`tests/test_arm_readiness_lifecycle.py:936–962`).

Single assembly removes repeated caller-side authentication, but **each consumer still authenticates independently inside `_consume_launch_capability`**:

- GO admission (`joulewise/arm_readiness.py:10358`);
- full `_verify_arm_receipt`, sidecar/digest and supplied-context equality (`:10405`);
- current HEAD and volatile root/backup/lock checks;
- manifest/environment/chain loading and binding reconciliation;
- GO/ARM bindings, confirmation and current-boot/deadline checks (`:10486`);
- another ordinary-monotonic deadline check immediately before real exclusive creation (`:10533`).

The `O_EXCL` claim remains the linearization point. Existing handoff, artifact-reference, post-consumption verifier and `execve` mocks predate this diff; they are not newly introduced predicate bypasses.

**4. Cost — structural reduction established; elapsed/CPU improvement unmeasured.**

Previously the eight consumers each performed a caller-side `_verify_arm_receipt` during assembly and another during consumption: **16 primary ARM verification calls in the race portion**. Now there is one assembly plus eight consumer verifications: **9 calls**.

Those verifications replay pack/HEAD/registry/freeze bindings, discover and authenticate evidence, check lifecycle constraints, and rederive ARM rows. The change removes seven assemblies and seven associated verification calls: **43.75% fewer primary ARM verification calls**, not a demonstrated 43.75% reduction in total test CPU.

A rough equal-cost model applied to the historical ~91-second CPU observation gives approximately **51 seconds plus unchanged-cost effects**; setup, replay-after-race, caching and contention prevent a reliable point estimate.

The single timed attempt failed before construction:

```text
Ran 1 test in 0.043s
FAILED (errors=1)
real 1.07
user 1.01
sys 0.03
```

Those are **startup/error timings**, not race timings.

**5. Far-future realtime — no epoch-coupling defect found.**

The realtime offset already existed in the T0 fixture; this diff centralizes it and extends its use.

The relevant production readers are:

- `_sample_anchor`: integer/type validation (`joulewise/arm_readiness_evidence_t0.py:1066`);
- `_derive_clock_attestation`: compares R0 and author **REALTIME-minus-RAW offsets** (`:1166`);
- `_clock_probe_predicate_passes`: recomputes authored offset change and live-versus-authored offset change (`joulewise/arm_readiness.py:6782`, `:6828`);
- clock-reference construction/validation and rehearsal replay: preserve or compare numeric endpoints and recompute the same differences.

None compares this anchor realtime with wall-clock now, plan T0 epoch, or receipt UTC issuance. The shared offset cancels in the governed differences. T0 duration uses RAW; capture ordering, freshness, ARM expiry and launch deadlines use ordinary monotonic time. GO epoch/ISO validation does not derive its time from this anchor.

Consequently, 2e18 ns neither extends capability freshness nor inherently triggers these clock refusals. It also does not prove absolute live clock accuracy; reference observations are synthetic.

**6. Same-signature statement.**

No recurrence of either target signature was observed:

- `readiness_clock_preflight_refused` from ambient sampling;
- the race’s live-thread assertion after timed joins.

Execution stopped earlier with **a different signature**, `FileNotFoundError` from temporary-directory selection. Therefore this review cannot claim either historical signature is resolved under concurrency.

## Residual risk

The clock seam and race optimization are supported by reading and isolated execution. Required focused/subprocess integration, full integration mutation, and concurrent-load/four-worker evidence remain outstanding. The 30-second per-thread joins are unchanged and may still fail under severe load; added diagnostics make such a failure more informative.

The next exact step is lead-side execution in a writable test environment, recording timer slack, race CPU timing, focused and loaded outcomes, and the four-worker race result required by cold-gate 56 ADDENDUM-2. No files were changed, and no live hardware validation was performed.