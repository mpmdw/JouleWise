```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The eleven-site census is correct, but 600 s is not a proven successful-path bound; the separate metrology rationale also omits admitted initial clock error.",
  "workspace": {
    "base_requested": "6075389a13df206205651175a7a9d52135df6fde",
    "base_mode": "exact",
    "head_start": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "head_end": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "upstream_end": null,
    "branch": "feat/2026-09-02-t26-liveness"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "T26-PHYS-1",
        "severity": "should_fix",
        "file:line": [
          "joulewise/arm_readiness_evidence_t0.py:427-466",
          "joulewise/arm_readiness_evidence_t0.py:1246-1291",
          "joulewise/arm_readiness_evidence_t0.py:1555-1567",
          "joulewise/arm_readiness_evidence_t0.py:1739-1809",
          "joulewise/identity_pins.py:1298-1364",
          "joulewise/adapters/mlx_runtime.py:273-295",
          "joulewise/arm_readiness.py:6478-6485"
        ],
        "scenario": "All eleven fresh probes can succeed in 44 s each and the eleven fixed post-R1 Git invocations can succeed in 11 s each: 11*44 + 11*11 = 605 s before ordinary file/CPU work. More directly, the post-R1 offline-input row can successfully return from an untimed mlx_lm.load after 601 awake seconds.",
        "what_code_does": "The 45 s timeout covers only process.wait, not TemporaryFile/Popen setup, output reads, or other derivation work. Post-R1 also has eleven fixed Git calls with 20 s timeouts, additional Git calls per external pin, untimed filesystem scans/hashing, and untimed runtime identity re-derivation. The final predicate nevertheless refuses any ordinary-clock elapsed time above 600 s.",
        "what_physics_says_should_happen": "A liveness refusal can be called hang detection only if every successful prerequisite has a compatible end-to-end deadline. Here a semantically successful, awake derivation can exceed 600 s, so the bound can false-refuse a real night."
      },
      {
        "id": "T26-PHYS-2",
        "severity": "should_fix",
        "file:line": [
          "joulewise/arm_readiness.py:6442-6446",
          "joulewise/arm_readiness.py:6504-6511",
          "joulewise/clock_reference.py:110-121",
          "docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md:193-213"
        ],
        "scenario": "An admitted R1 bound B=0.499 s plus 3.68 ppm free-run for the real-path maximum oldest-sample age of 1830 s gives 0.499 + 0.0067344 = 0.5057344 s. Under the clock receipt's standalone 6 h + 600 s + 30 s envelope it gives 0.5808064 s. With no wall-clock step or slew, both realtime-minus-RAW anchor deltas remain 0.",
        "what_code_does": "It admits reference_bound_seconds through 0.5 s and the anchor gates only changes in realtime-minus-CLOCK_MONOTONIC_RAW. They do not enforce oscillator error relative to external time.",
        "what_physics_says_should_happen": "The ruling's 0.5/3.68ppm calculation assumes zero initial error. A metrology guarantee must add the admitted initial bound to accumulated drift. This does not justify restoring 5 s, but it means the claimed drift-plus-anchor safety is not established for every value the predicate accepts."
      }
    ],
    "answers": {
      "1": {
        "answer": "The census is exactly eleven post-R1 _fresh_probe call sites: network-time enforcement (:1216), maintenance (:1318), thermal (:1365), four process censuses (:1723-1726), powermetrics (:1801), and AC/low-power/supply (:1836-1838). Each reaches process.wait(timeout=45) through :427-466. Thus the timed-wait subtotal is strictly below 495 s, nominally leaving 105 s.",
        "other_work": "Post-R1 work also includes probe setup/output I/O; Git commit-message plus five terminal-review artifacts (:1246-1291); command-capture, launch-manifest, window.env, window-chain and arm-context reads (:516-565, :813-939); root/lock scans (:990-1038); three ledger artifacts and ledger/input parsing (:1484-1655); external-artifact authentication and live identity re-derivation (:1739-1783), including untimed model load/projector/cleanup; launch namespace scans (:1887-1896); backup resolve/access/disk_usage (:1914-1927); and final validation/UTC sampling (:2323-2325).",
        "worst_case": "No finite successful-path maximum follows from the code. Even bounded subprocess ceilings include at least eleven fixed Git invocations at 20 s each, so 495 + 220 = 715 s before per-pin Git calls and untimed work. Therefore 600 s has no guaranteed margin. Eleven-sites-times-45 is a correct site census, but 'plus 105 s covers the successful path' is false."
      },
      "2": "Example: ordinary R1 finish U=1000 s; then 8 h sleep plus 100 s awake work; validity origin U=1100 s, so liveness sees 100 s and passes. RAW and realtime each advance 28,900 s, leaving both realtime-minus-RAW deltas at 0 ms; the boot ID is unchanged, so both 5 ms gates pass. R1 completion is 28,900 wall seconds old, or conservatively 28,930 s for the oldest batch leg. D-150 does not exclude this: its six-hour deadline is code-stamped on the same sleep-blind ordinary clock. This is a real limitation but exactly the scenario admitted by L1, not a new finding. The machine currently reports monotonic implementation mach_absolute_time() and RAW-minus-ordinary about 87,777.23 s.",
      "3": "The new liveness conjunct itself is invariant: both evaluations use the receipt's stored valid_until and stored r1_batch_finished value, with no new ordinary-clock read. The whole clock predicate is not a pure function of the receipt. Issuance passes the NOT_APPLICABLE sentinel (:2342-2349; arm_readiness.py:6488-6489); ARM supplies a freshly sampled realtime/RAW anchor and current boot ID (:6398-6411, :8366-8377). ARM also separately uses evaluated_at_monotonic_ns for expiry (:8271-8289). Thus arm can differ because of the live anchor, boot, or expiry, but elapsed time alone cannot change the stored liveness relation.",
      "4": "For the CLOCK_ATTESTATION receipt considered alone, equality with valid_until is admitted because consumers use deadline < now or now > deadline. R1-completion age at that instant is [21600,22200] s; adding the permitted 0-30 s R1 batch gives oldest-leg age [21600,22230] s. On the complete real-night path, volatile evidence has a 1200 s deadline and ARM must preserve the 300 s consume budget; the absolute latest final consumption is validity_origin+1200, so completion age is [1200,1800] s and oldest-leg age [1200,1830] s. The registry's literal 21600 s receipt horizon matches the code, and the runbook correctly says it does not extend volatile evidence. It does not mean the R1 sample itself is at most six hours old. No T-0 six-hour statement was found under docs/contracts; the governing text is the registry, decision log, and runbook.",
      "5": "No physics singles out 5 s. At 3.68 ppm: 5 s contributes 18.4 us; the 30 s batch contributes 110.4 us; 600 s contributes 2.208 ms; batch plus 600 s contributes 2.3184 ms; six hours contributes 79.488 ms; and 6 h+600 s+30 s contributes 81.8064 ms. With the observed 40.8 ms R1 bound, that totals 122.6064 ms, leaving 377.3936 ms below 0.5 s. But code admits B up to 0.5 s, leaving zero drift headroom. Therefore 600 s is execution/liveness policy, physically unproven as a metrology bound; restoring 5 s would not repair the additive-bound issue."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_schemas tests.test_t0_rehearsal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 166 tests in 216.334s",
          "OK (skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 166 tests.*OK \\(skipped=7\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import ast,pathlib; t=ast.parse(pathlib.Path(\"joulewise/arm_readiness_evidence_t0.py\").read_text()); xs=sorted(n.lineno for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==\"_fresh_probe\" and 1115<n.lineno<2325); print(len(xs), xs)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "11 [1216, 1318, 1365, 1723, 1724, 1725, 1726, 1801, 1836, 1837, 1838]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^11 \\[1216, 1318, 1365, 1723, 1724, 1725, 1726, 1801, 1836, 1837, 1838\\]$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check 6075389a..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live nap, arm, or night-custody experiment was run; those actions were prohibited. Clock behavior was established from code, the repository's recorded Darwin measurement, and a read-only local clock inspection.",
      "needs": ""
    }
  ]
}
```

## Findings

- T26-PHYS-1 — should_fix: The 600 s constant can false-refuse a successful authoring. The eleven probe sites are correctly counted, but 45 s bounds only each child wait. At least eleven additional fixed Git processes have 20 s ceilings, and MLX identity re-derivation includes an untimed model load. The code therefore provides no finite end-to-end successful-path bound.

- T26-PHYS-2 — should_fix: The metrology rationale treats the 500 ms admission ceiling as drift headroom, but it is also the permitted initial R1 error bound. Stable oscillator drift is invisible to the realtime-minus-RAW anchor. Even the complete path’s shorter 1830 s maximum can cross 500 ms from an admitted 499 ms starting bound.

## Residual risk

The sleep case is genuine: same-boot sleep advances realtime and `CLOCK_MONOTONIC_RAW` together while `time.monotonic_ns()` remains still. It is not mitigated by D-150, but it is already accurately recorded as L1. No files were written, and no night custody root was accessed.