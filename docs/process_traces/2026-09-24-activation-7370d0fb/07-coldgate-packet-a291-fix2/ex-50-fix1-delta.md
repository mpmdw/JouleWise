```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1–F4 meet their legal-roster checks, but resealing can bypass replay and malformed input can crash derived-value computation.",
  "workspace": {
    "base_requested": "01badd6a",
    "base_mode": "exact",
    "head_start": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "head_end": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "f1": "FIX INTRODUCED A NEW DEFECT",
    "f2": "FIXED",
    "f3": "FIXED",
    "f4": "FIXED",
    "same_signature": "YES",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "A caller-resealed roster enters the trusted cache and skips required replay",
        "location": "joulewise/scored_packer.py:222,331-334"
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "Non-terminal count with no positions raises ZeroDivisionError at requeue entry",
        "location": "joulewise/scored_packer.py:109"
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "title": "Second stress seed scarcely changes the generated reporting paths",
        "location": "tests/test_scored_packer_stress.py:76-85,108-127"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 52 tests in 183.348s",
          "OK",
          "STRESS seed=291013 registrations=300 calls=4263 checker_calls=4863 violations=0",
          "STRESS seed=291014 registrations=300 calls=4253 checker_calls=4853 violations=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 52 tests in .*s[\\s\\S]*OK[\\s\\S]*violations=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check 01badd6a 20cd29de",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": []
}
```

## Findings

**B1 — BLOCKER.** `_seal(..., finalize=True)` adds *any* roster it seals to `_TRUSTED_OUTPUTS`; [requeue_overrun](/Users/edr/code/wt-a65fb4fa-a291rev/joulewise/scored_packer.py:331) then skips replay for that cache entry. I mutated a returned root **in place** by setting a block’s `late` flag. Ordinary resubmission refused `inv_02`. After setting `sha256=None` and calling `_seal(..., finalize=True)` on that same object, `verify_executed_roster` refused `inv_39`, while `requeue_overrun` accepted it and returned a one-event roster. A stronger forged root with two live placements for one block was also accepted by `_seal` and requeue; the checker reported `INV-11` and `INV-36`, and full replay refused `inv_39`. Cache trust therefore needs provenance that a caller cannot create by resealing.

The cache did hold for the ordinary cases tested: a second `Registration` instance made from identical data reused the cache, a different registration refused `inv_01`, an in-place earlier-event digest change refused `inv_38`, and nine later outputs evicted the original entry and caused replay. The bypass requires the callable private finalize path.

**S1 — SHOULD-FIX.** The new [planned lever expression](/Users/edr/code/wt-a65fb4fa-a291rev/joulewise/scored_packer.py:109) gates division on `nonterminal` counts, then divides by the independently built `pos` lists. I moved every large level-1 block in a returned root from its envelope’s `blocks` to `voided_block_ids` without adding terminal refusals. Both `_derived` and `requeue_overrun` raised raw `ZeroDivisionError`; [the seal’s malformed-roster handler](/Users/edr/code/wt-a65fb4fa-a291rev/joulewise/scored_packer.py:202) did not turn it into a typed refusal. A normally produced history cannot reach this state: advance voids the old placement and creates the next, while terminal decisions record refusals. Partial positions with zero fully eligible parents correctly produce `null` on legal histories.

**S2 — SHOULD-FIX.** [The stress generator](/Users/edr/code/wt-a65fb4fa-a291rev/tests/test_scored_packer_stress.py:76) chooses mode with `i % 8` and size, count, and capacity mostly from `i`; the seed chiefly changes predictions within a narrow band, a completed-only branch, and capture keys after reporting. The two 300-registration runs hit **identical counts on 10 of 11 edges**; E2 was 1027 versus 1028. A diversity test needs seed-driven choices of legal report shapes, stages, boundary durations, and geometry, with per-seed variation asserted rather than only aggregate edge presence.

**F1–F4 audit.** F1’s intended arithmetic is fixed on valid rosters, with S1 introduced by its count/position split. On lens-37 R2, hand calculation `|(56+1+2+3+4)/5 − (5+6+7+8+9)/5|` is `6.199999999999999`; packer and checker both returned that value, and the checker accepted the roster. F2 is fixed: with one window omitted from a split parent, hand calculation `|(13+2+4+6+8)/5 − (1+3+5+7+9)/5|` is `1.5999999999999996`; packer and checker agreed, and both marked that cell’s spread exceeded. F3’s three requested regressions passed in the named suite. F4’s literal requirement passed: two seeds, 300 registrations each, zero checker violations, with the diversity limitation in S2.

For D2, legal replay does not leave two placements of one block live or leave a non-terminal block without a live placement. The forged duplicate-placement result above shows why the seal and cache boundary matters. Planned spread excludes partly terminal parents; executed spread excludes partly counted parents. The R2 and omitted-window probes agreed with those rules.

**D5: YES.** S1 repeats the class in question: a derived lever uses one parent population to decide whether to compute a value and another population to supply its positions. The duplicate-live cache probe also makes `_live` silently select one of two placements.

## Residual risk

The executed-status checks remain provisional until the A292 reducer calls the real verification entry. This review ran only the four named test modules and targeted read-only probes.