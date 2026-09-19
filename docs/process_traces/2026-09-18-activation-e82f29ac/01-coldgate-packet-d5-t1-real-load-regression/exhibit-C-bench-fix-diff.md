# Exhibit C — bench fix `05e90616..498ad1d0` (`git diff`)

```diff
diff --git a/tests/test_sample_quiet_predicate_evidence.py b/tests/test_sample_quiet_predicate_evidence.py
index dd88c57e..f65447a6 100644
--- a/tests/test_sample_quiet_predicate_evidence.py
+++ b/tests/test_sample_quiet_predicate_evidence.py
@@ -619,7 +619,17 @@ class LoadTests(unittest.TestCase):
         self.assertIsNone(report["error"], report["error"])
         periods = [p for worker in report["workers"] for p in worker["periods"]]
         fraction = sum(p["cpu_used_s"] for p in periods) / args.duration_s
-        self.assertAlmostEqual(fraction, .1, delta=.04)
+        late_s = sum(p["wake_late_s"] for p in periods)
+        # Over-burning is a budgeting defect under any scheduling: never allowed.
+        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores; late {late_s:.3f} s")
+        if late_s <= .12:
+            # The scheduler kept its wake promises: the tight two-sided check.
+            self.assertAlmostEqual(fraction, .1, delta=.04)
+        else:
+            # Scheduler starvation observed (delta re-audit D5-T1): the controller never
+            # catches up, so the deficit must be explained by the late wakes alone.
+            self.assertGreaterEqual(fraction, .1 - .04 - .1 * late_s / args.duration_s,
+                f"deficit not explained by late wakes: {fraction:.4f} cores; late {late_s:.3f} s")
         self.assertTrue(report["cleanup"])
         for child in report["cleanup"]:
             self.assertFalse(child["alive"])
```
