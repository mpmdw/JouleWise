# Exhibit A — fix round 2 diff, branch `feat/2026-09-18-quiet-predicate-evidence-harness`, `3df43458..37ca3c35` (verbatim `git diff`)

```diff
diff --git a/tests/test_sample_quiet_predicate_evidence.py b/tests/test_sample_quiet_predicate_evidence.py
index f65447a6..ad3fc64a 100644
--- a/tests/test_sample_quiet_predicate_evidence.py
+++ b/tests/test_sample_quiet_predicate_evidence.py
@@ -5,6 +5,7 @@ import json
 import os
 from pathlib import Path
 import plistlib
+import resource
 import subprocess
 import sys
 import tempfile
@@ -15,10 +16,15 @@ from unittest.mock import Mock, patch
 from scripts import sample_quiet_predicate_evidence as harness
 
 
+# Measured child start-up CPU ≈ 0.19 s on this host, record 12; the floor is sized to the instrument, not to delivery.
+STARTUP_CPU_S = 0.5
+
+
 class FakeClock:
     def __init__(self):
         self.now = 0.0
         self.used = 0.0
+        self.ratio = 1.0
 
     def monotonic(self):
         return self.now
@@ -36,7 +42,7 @@ class FakeClock:
         self.now = max(self.now, deadline)
 
     def burn(self, count):
-        self.now += count * .00001
+        self.now += count * .00001 * self.ratio
         self.used += count * .00001
 
 
@@ -599,8 +605,7 @@ runpy.run_path(script, run_name="__main__")
 class LoadTests(unittest.TestCase):
     @unittest.skipUnless(sys.platform == "darwin", "native QoS requires macOS")
     def test_real_load_tracks_point_one_core_and_guards_worker_budget(self):
-        # +/- .04 cores permits .12 CPU seconds of startup, timer and scheduling
-        # variation in a 3 s calibration-only window; it still rejects 1 core.
+        # The controller promises a measured CPU ceiling and no catch-up, never delivery.
         # Use 500 ms periods: this host can coalesce sleeps by ~150 ms, longer
         # than a 100 ms period, and the controller deliberately never catches up.
         # Check config BEFORE launch so the cores mutation cannot burn a core.
@@ -614,22 +619,32 @@ class LoadTests(unittest.TestCase):
             args = harness.parser().parse_args(["load", "--cores", "0.1", "--duration-s", "3",
                 "--period-ms", "500", "--qos", "user-initiated", "--profile", "scalar",
                 "--seed", "1", "--log", str(Path(tmp) / "load.json")])
+            before = resource.getrusage(resource.RUSAGE_CHILDREN)
             harness.load(args)
+            after = resource.getrusage(resource.RUSAGE_CHILDREN)
             report = json.loads(Path(args.log).read_text())
         self.assertIsNone(report["error"], report["error"])
         periods = [p for worker in report["workers"] for p in worker["periods"]]
-        fraction = sum(p["cpu_used_s"] for p in periods) / args.duration_s
-        late_s = sum(p["wake_late_s"] for p in periods)
-        # Over-burning is a budgeting defect under any scheduling: never allowed.
-        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores; late {late_s:.3f} s")
-        if late_s <= .12:
-            # The scheduler kept its wake promises: the tight two-sided check.
-            self.assertAlmostEqual(fraction, .1, delta=.04)
-        else:
-            # Scheduler starvation observed (delta re-audit D5-T1): the controller never
-            # catches up, so the deficit must be explained by the late wakes alone.
-            self.assertGreaterEqual(fraction, .1 - .04 - .1 * late_s / args.duration_s,
-                f"deficit not explained by late wakes: {fraction:.4f} cores; late {late_s:.3f} s")
+        claimed_s = sum(p["cpu_used_s"] for p in periods)
+        fraction = claimed_s / args.duration_s
+        charged_s = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
+        # The controller promises a measured CPU ceiling and never catches up; it
+        # promises nothing about CPU the scheduler declines to hand out (D5-T1,
+        # cold-gate ruling 10 + refutation 12). Delivery is reported, never asserted;
+        # budgeting is proved by test_cpu_budget_overshoot_and_frozen_duty.
+        self.assertLessEqual(fraction, .1 + .04, f"over-burned: {fraction:.4f} cores")
+        for period in periods:
+            self.assertLessEqual(period["cpu_used_s"],
+                period["budget_cpu_s"] + period["overshoot_bound_cpu_s"] + 1e-9,
+                f"period {period['period']} burned past its budget: {period}")
+        self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")
+        # Kernel cross-check on the reaped child (rusage folds in at load()'s join):
+        # what the worker claims can never exceed what the OS charged it, and the
+        # OS-charged total is bounded by the ceiling plus the child's start-up CPU.
+        self.assertGreaterEqual(charged_s, claimed_s - .01,
+            f"kernel charged {charged_s:.3f} s < worker claimed {claimed_s:.3f} s")
+        self.assertLessEqual(charged_s, .14 * args.duration_s + STARTUP_CPU_S,
+            f"child burned {charged_s:.3f} s of kernel-accounted CPU in {args.duration_s} s")
         self.assertTrue(report["cleanup"])
         for child in report["cleanup"]:
             self.assertFalse(child["alive"])
@@ -637,6 +652,32 @@ class LoadTests(unittest.TestCase):
             with self.assertRaises(ProcessLookupError):
                 os.kill(child["pid"], 0)
 
+    def test_late_initial_scheduling_never_catches_up(self):
+        clock = FakeClock(); clock.now = 2.0          # first wake 2 s after start
+        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
+        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .1, delta=.001)
+        self.assertEqual([p["period"] for p in periods], [4, 5])
+        self.assertLessEqual(sum(p["cpu_used_s"] for p in periods) / 3, .14)
+        for p in periods:
+            self.assertLessEqual(p["work_budget_cpu_s"], .1 * p["elapsed_s"] + 1e-9)
+            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
+            self.assertLess(p["wake_late_s"], 1e-3)
+            self.assertGreaterEqual(p["cpu_used_s"], p["work_budget_cpu_s"] - p["max_quantum_cpu_s"])
+            self.assertLessEqual(p["overrun_cpu_s"], p["overshoot_bound_cpu_s"])
+            self.assertAlmostEqual(p["wake_late_s"], 0.0, delta=2e-4)   # lateness is blind to this
+
+    def test_preempted_burn_exits_on_the_wall_deadline(self):
+        clock = FakeClock(); clock.ratio = 100.0      # burn advances wall 100x thread CPU
+        periods = harness.duty_periods(.1, 3, .5, clock.burn, clock, start=0.0)
+        self.assertAlmostEqual(sum(p["cpu_used_s"] for p in periods), .03, delta=.001)
+        self.assertEqual(len(periods), 6)
+        self.assertLessEqual(periods[-1]["end_mono_s"], 3.0 + 1e-9)      # window still honoured
+        for p in periods:
+            self.assertLessEqual(p["work_budget_cpu_s"], .1 * p["elapsed_s"] + 1e-9)
+            self.assertLessEqual(p["cpu_used_s"], p["budget_cpu_s"] + p["overshoot_bound_cpu_s"] + 1e-9)
+            self.assertLess(p["cpu_used_s"], p["work_budget_cpu_s"])
+            self.assertLess(p["wake_late_s"], .05)
+
     def test_cpu_budget_overshoot_and_frozen_duty(self):
         clock = FakeClock()
         periods = harness.duty_periods(.2, 9, .1, clock.burn, clock)
```
