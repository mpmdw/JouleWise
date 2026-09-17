```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "No confirmed seam defect; fixture integration passed, while native probe and suite green gates are blocked by sandbox process/identity restrictions.",
  "workspace": {
    "base_requested": "53a954c0bec8e124b2cf55f0e60be9748347ca1e",
    "base_mode": "exact",
    "head_start": "53a954c0bec8e124b2cf55f0e60be9748347ca1e",
    "head_end": "53a954c0bec8e124b2cf55f0e60be9748347ca1e",
    "upstream_end": "d7561fb6e35f14df245a3bc566f9d46c574bbac2",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "execution": "Real chain, reservation CLI and custody worker exercised against committed fixture pins and three finalized observations. Direct verify-only emitted exactly two JSON lines; its verify_only object had eight fields and three correct code digests. Probe receipt bound all six inputs. Ledger/pin unchanged; no chain.started or refusal on success.",
    "stall": "CUSTODY_BUDGET_S=3 in pinned fixture wrapper: chain exit 2; driver exit 3 (existing EXIT_REFUSED), REFUSED/night_calibration_refused/calibration_ledger_custody_timeout; phase reservation; document inventoried; fake courier launched. Latest elapsed 4.741 s within 3 s budget + 3 s tolerance. FIFO entered, ledger/pin unchanged, no session row or late append, worker PIDs gone, lease reacquired.",
    "strict": "Interrupted claim: execute and verify-only chain exits 2 with calibration_ledger_recovery_required; driver REFUSED with exact code; ledger/pin preserved.",
    "abort": "Fake nonempty mid-chain census plus existing refusal document: driver exit 4, ABORTED/night_aborted_agent_present; document retained as evidence.",
    "install": "Receipt from real probe with only census proof faked passed full validate_install, real preflight and actual HEAD checks; fake launchctl bootstrapped both jobs. One-byte identity-epoch change refused with exit 2 naming epoch.json.",
    "merge": "Seat A touched 13 files; seat B touched 17; intersection empty. Against origin/main: 30 files, 3412 insertions, 253 deletions.",
    "artifacts": "Replay: /tmp/int-refute/integration_refute.py. Evidence: /tmp/int-refute-evidence/ and /tmp/int-refute-integration-full-install.log. No repository writes. Baseline digest, index, HEAD and clean worktree verified at completion."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_exits tests.test_calibration_ledger_custody tests.test_calibration_custody_worker tests.test_validate_powermetrics_fiducial_derivation_only tests.test_calibration_ledger tests.test_authentication_io tests.test_run_night tests.test_night_gate tests.test_night_agent_install tests.test_install_night_agent tests.test_gen_derivation_night tests.test_issue_calibration_acceptance_generation",
      "cwd": "/tmp/int-refute",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: None is not an instance of <class 'str'>",
          "Ran 684 tests in 2133.242s",
          "FAILED (failures=1, skipped=4)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 scripts/quick_suite.py --tier quick --workers 4",
      "cwd": "/tmp/int-refute",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error: campaign start identity unavailable",
          "AssertionError: 2 != 1",
          "QUICK SUMMARY tier=quick modules=153 excluded=83 failures=1 seconds=241.898 result=FAIL"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "failures=0.*result=PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B integration_refute.py",
      "cwd": "/tmp/int-refute",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"check\": \"probe-native\", \"rc\": 2, \"outcome\": \"refused\", \"refusal_code\": \"probe_process_survived\"}",
          "{\"check\": \"validate-install-real-receipt\", \"status\": \"admitted\", \"actual_heads\": true}",
          "{\"check\": \"integration-summary\", \"failures\": []}"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"failures\": \\[\\]"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B axi_identity_diagnostic.py",
      "cwd": "/tmp/int-refute",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.174s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "build",
      "cmd": "python3 -m compileall -q scripts joulewise && /bin/zsh -n scripts/night_chains/calibration_derivation_only.zsh",
      "cwd": "/tmp/int-refute",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff origin/main --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" 30 files changed, 3412 insertions(+), 253 deletions(-)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "30 files changed"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "/bin/ps -p $$ -o lstart= -o stat=",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 127,
        "tail": ["zsh:1: operation not permitted: /bin/ps"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".+"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Mandatory unmodified probe 2 exits 2 at scripts/run_night.py:2115: refused/probe_process_survived. pgrep reports 'Cannot get process list'; ps is denied. Receipt parsing and bindings succeed, but native cleanup proof cannot pass. V3 repeats using the existing tests' _probe_group_absent seam; that successful receipt is fixture evidence, not launchd validation.",
      "needs": "Lead rerun the retained harness in an environment permitting process census and require probe-native rc=0/outcome=ok; retain the production launchd gate until independently verified."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Quick tier: only tests.test_axi_controller_events failed (two assertions at lines 309 and 360); campaign identity unavailable. Both pass with only identity observation faked and custody redirected to /tmp (V4). The tests, run_campaign.py and measurement_liveness.py are unchanged from origin/main.",
      "needs": "Rerun the unmodified quick tier with working process identity observation."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Focused suite's sole failure is test_live_probes_report_this_machine_against_the_active_epoch at tests/test_issue_calibration_acceptance_generation.py:346: os_build is None. /usr/sbin/sysctl -n kern.osversion exits 1 with 'Operation not permitted'. The failing test and issuer implementation are unchanged from origin/main.",
      "needs": "Rerun that live identity test with sysctl access."
    }
  ]
}
```