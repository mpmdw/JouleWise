diff --git a/tests/test_install_night_agent.py b/tests/test_install_night_agent.py
index 554ea05b..7457c9b9 100644
--- a/tests/test_install_night_agent.py
+++ b/tests/test_install_night_agent.py
@@ -165,7 +165,24 @@ class InstallNightAgentTests(unittest.TestCase):
             return
         make_probe_fixture(self.root, plan)
         now = float(self.clock_file.read_text()) if hasattr(self, "clock_file") else time.time()
-        write_matching_probe_receipt(plan, python, now=now)
+        # The receipt's launch_context carries rendered-plist digests, and the
+        # rendered StartCalendarInterval depends on the local timezone. Render
+        # it under the same TZ the installer subprocess gets, or a runner whose
+        # own TZ differs (UTC on hosted CI) sees a false launch_context mismatch.
+        tz = self.environment.get("TZ")
+        saved = os.environ.get("TZ")
+        if tz is not None:
+            os.environ["TZ"] = tz
+            time.tzset()
+        try:
+            write_matching_probe_receipt(plan, python, now=now)
+        finally:
+            if tz is not None:
+                if saved is None:
+                    os.environ.pop("TZ", None)
+                else:
+                    os.environ["TZ"] = saved
+                time.tzset()
 
     def _controlled_python(self, now: float, *, spans: tuple | None = None) -> Path:
         """A subprocess clock seam; no production environment override exists."""
