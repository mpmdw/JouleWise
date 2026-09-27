```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend deterministic decoys for all nine recorded service basenames; the second pgrep snapshot cannot close F1.",
  "workspace": {
    "base_requested": "2b4f0a86",
    "base_mode": "exact",
    "head_start": "2b4f0a865f44766e4234c741b3506a1ad342660e",
    "head_end": "2b4f0a865f44766e4234c741b3506a1ad342660e",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "c",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "tests/test_arm_readiness_evidence_t0.py",
        "line": 2789,
        "text": "The second pgrep snapshot can miss a recorded-service hit from the first snapshot if that process exits between calls."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check 97082508 2b4f0a86",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — SHOULD-FIX.** Choose **(c)**. Spawn negative decoys for all nine recorded service basenames and check their PIDs in the existing `pgrep -f` result. Those checks use the same snapshot as the positive decoys and do not depend on a service staying alive for a later read. A bounded retry still has a final exit window; accepting the race leaves F1 open.

Proposed minimal diff against [tests/test_arm_readiness_evidence_t0.py](/Users/edr/code/JouleWise-wt-census-rev-3ba66eeb/tests/test_arm_readiness_evidence_t0.py:2718):

```diff
@@
         cases = (
@@
         )
+        # Rebuild full executable paths where the recorded argv was truncated.
+        service_paths = tuple(
+            str(
+                Path(
+                    next(
+                        argv.split(" ", 1)[0]
+                        for argv in _RECORDED_CENSUS_SERVICE_ARGV
+                        if basename in argv
+                    )
+                ).parent / basename
+            )
+            for basename in _RECORDED_CENSUS_SERVICE_BASENAMES
+        )
         for pattern, positives, negatives in cases:
             with self.subTest(pattern=pattern):
+                negative_markers = negatives + service_paths
                 decoys = [
                     subprocess.Popen([marker, "30"], executable="/bin/sleep")
-                    for marker in positives + negatives
+                    for marker in positives + negative_markers
                 ]
@@
-                    # hit's full argv is then read back per PID for the text
-                    # checks (lane TEST-CENSUS-MULTILINE-ARGV-01).
+                    # hit's full argv is then read back per PID for a pattern
+                    # check (lane TEST-CENSUS-MULTILINE-ARGV-01).
@@
                     reported = {int(line) for line in probe.stdout.splitlines()}
-                    for decoy, marker in zip(decoys, positives + negatives, strict=True):
+                    for decoy in decoys:
+                        self.assertIsNone(decoy.poll())
+                    for decoy, marker in zip(
+                        decoys, positives + negative_markers, strict=True
+                    ):
@@
-                    # The recorded-service check also runs over the whole
-                    # ``-lf`` text, continuation lines included, so a hit that
-                    # exits before its ``ps`` read below cannot hide a service.
-                    listed = subprocess.run(
-                        ["/usr/bin/pgrep", "-lf", pattern],
-                        capture_output=True, text=True, check=False,
-                    )
-                    self.assertIn(listed.returncode, (0, 1), listed.stderr)
-                    for basename in _RECORDED_CENSUS_SERVICE_BASENAMES:
-                        self.assertNotIn(basename, listed.stdout)
                     for pid in sorted(reported):
@@
                         self.assertEqual(shown.returncode, 0, shown.stderr)
                         self.assertIsNotNone(re.search(pattern, shown.stdout), shown.stdout)
-                        for basename in _RECORDED_CENSUS_SERVICE_BASENAMES:
-                            self.assertNotIn(basename, shown.stdout)
```

The reconstructed paths were checked against the recorded corpus: they yield nine distinct absolute paths with the intended executable basenames. **This does not strictly dominate the original test’s guarantees.** The original single `pgrep -lf` output checked arbitrary live hits, including one that exited immediately afterward. This proposal guarantees coverage of the nine recorded service identities through controlled decoys, but gives up that incidental transient-hit check.

**Stop criterion:** on a process-table-capable Mac, the focused test passes with all decoys alive after each probe, every service decoy absent, and the positive and newline-argv decoys reported. A pattern broadened to include one recorded service must then fail on that service’s decoy.

## Residual risk

An unrecorded service argv could match during a production census and disappear before the test’s per-PID `ps` read. The deterministic decoys cover the nine recorded identities; they do not prove the absence of every possible live false positive. No live test was run in this read-only consult.

RECOMMEND: c