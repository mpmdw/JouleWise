```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "H-side registration checks work, but the new arm-check gloss is inaccurate and the SD test misses a false-data regression.",
  "workspace": {
    "base_requested": "c9e2bd14",
    "base_mode": "descendant",
    "head_start": "912345cd58a4f67ff3501aa72bd6961b01db699d",
    "head_end": "912345cd58a4f67ff3501aa72bd6961b01db699d",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 1
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "summary": "The new notice gloss says the arm checks run when the night is installed, although they run before installation.",
        "location": "joulewise/evidence_night.py:316"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "The SD label test uses zero envelopes; a retained-only calculation survives the entire campaign test module while making the label false.",
        "location": "tests/test_quiet_predicate_campaign.py:105"
      },
      {
        "id": "F3",
        "severity": "nit",
        "summary": "The required corecaptured sentence retains its earlier unconditional overclaim when the launch log cannot be measured.",
        "location": "joulewise/evidence_night.py:321"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 287 tests in 883.725s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 287 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a276-reaudit.exLiEj/mutants.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ""
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
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

**F1 — should_fix.** The rendered notice says the arm check means “the checks run when the night is installed.” In an offline lifecycle replay, `check` was ready and `notice.txt` existed while the published `night_plan.json` was still absent. The code requires a fresh check before writing the notice at [evidence_night.py:1286](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/evidence_night.py:1286), then requires that notice before `publish_install` proceeds at [line 1460](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/evidence_night.py:1460). “Before the night is installed” describes the order. The fix brief requested the current gloss, so the lead needs to resolve that wording conflict.

**F2 — should_fix.** The corrected SD label matches the *current* calculation: [quiet_predicate_campaign.py:1344](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/quiet_predicate_campaign.py:1344) takes every readable joule value from `values`, including excluded rows. But the label test calls `pilot_summary(..., [])`. With energies `[10, 12, 10, …]` and envelope 2 excluded, the current unfiltered SD is `0.5773502691896257` J and retained SD is `0.0` J. Changing line 1344 in the `/tmp` copy to use only `retained` made the reported “unfiltered” SD `0.0` J while **all 156 tests in `tests.test_quiet_predicate_campaign` still passed**. Add a nonempty excluded-energy assertion to bind the label to its computation.

**F3 — nit, retained from round 1.** The corecaptured sentence still promises refusal whenever the spawn condition is true. In an offline gate replay with a failed log read, `receipt.refusal` was `None` and C3 recorded `status: not_measured`. [night_gate.py:1519–1526](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/night_gate.py:1519) applies the spawn refusal only after a successful read. Qualifying the sentence for a readable log would preserve its required verbatim clause.

### Closure answers

- **X1: closed for production registration armability.** `sealed_candidate` launches the clone’s Python with `cwd=root`; `run` removes `PYTHONPATH` ([evidence_night.py:55](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/evidence_night.py:55), [line 272](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/evidence_night.py:272)). Its ruled, current-digest, and armability refusals use H’s `night_gate` at lines 246–251. `prepare` calls it before drafting, `check` reaches it through `sealed_state`, and `notice` calls it before output. In temporary production-path replays, `prepare` **passed** with the caller’s digest and armability policy patched wrong, and **refused** with `sealed candidate failed registration armability` when H’s policy was made to reject. The caller retains the intended sealed-binding hash check at line 289 and the window check; direct calls to `render_notice` can render a fabricated matching binding, but the production paths seal it first.
- **X2: closed.** Both affected evidence-night fixtures use `night_gate.QPE01_PILOT_REGISTRATION_PATH` ([test lines 67 and 2247](/Users/edr/code/wt-1d3796d5-ref-a276/tests/test_evidence_night.py:67)).
- **X3: text changes landed, with F1 and F3.** The renderer glosses busy cores, core-seconds, apparatus, and arm check; spells out “twelve” and “Two”; completes the mandated corecaptured sentence; and adds the git sentence. The git claim matches read-only `git show` in the measurement clone ([quiet_predicate_campaign.py:94](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/quiet_predicate_campaign.py:94)) and commit/push in a separate results clone ([run_night.py:1073](/Users/edr/code/wt-1d3796d5-ref-a276/scripts/run_night.py:1073), [line 1111](/Users/edr/code/wt-1d3796d5-ref-a276/scripts/run_night.py:1111), [line 1118](/Users/edr/code/wt-1d3796d5-ref-a276/scripts/run_night.py:1118)). The numeric bars retain their enforcing `>=` comparisons at [night_gate.py:850](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/night_gate.py:850) and [quiet_predicate_campaign.py:1024](/Users/edr/code/wt-1d3796d5-ref-a276/joulewise/quiet_predicate_campaign.py:1024); the consecutive abort uses the registered count at line 1645.
- **X4: label closed; semantic test gap F2.** The label at campaign line 1438 describes line 1344, and its exact wording is asserted in the summary text test.
- **X5: closed.** The only campaign production change in this delta is the SD label. The v2 test asserts its entire empty-fixture summary with that one relabeling.
- **X6: the specified regression assertions are present.** Five independent delta mutants below were killed at the named call-site tests. The additional SD computation mutant exposes F2; it was outside the fix brief’s mutant list.
- **X7: closed.** The pre-output refusal list includes the sealed-binding mismatch and H-side registration refusals at [evidence_night_entry.md:431](/Users/edr/code/wt-1d3796d5-ref-a276/docs/contracts/evidence_night_entry.md:431).

The next legitimate v3 arm has no observed new refusal: the registration file hashes to H’s current digest, H marks it armable and chain-binding, and the offline `prepare` replay passed.

| `/tmp` delta mutant | Result | Killing test |
|---|---|---|
| Bypass sealed-binding hash | Killed | `NoticeProtocolTextTests.test_notice_registration_binding_and_relative_clone_root` |
| Bypass H armability | Killed | `PrepareTests.test_sealed_registration_decisions_use_candidate_interpreter` |
| Resolve relative registration against custody | Killed | `NoticeProtocolTextTests.test_notice_registration_binding_and_relative_clone_root` |
| Make the git sentence claim publication never commits | Killed | `NoticeProtocolTextTests.test_v3_notice_states_bound_schedule_and_all_refusal_rules` |
| Restore the false “every captured envelope” SD label | Killed | `CampaignTests.test_summary_text_follows_registration_exclusion_rule` |

**Same-signature statement:** false generated text **yes** (F1; F3 predates this fix); unpinned sentence **yes in its data meaning** (F2, although the literal SD wording is pinned); caller-checkout registration import **no**.

## Residual risk

This was offline verification, not a live arm. A future v4 registration that removes `t0_non_observer_share_max` remains assigned to the registration-v4 lane. The repository was left clean and unchanged.