```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Built the scoped S2/S3 scratch prototype and passed both import-clean checks.",
  "workspace": {
    "base_requested": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "base_mode": "exact",
    "head_start": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "head_end": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/claim_hold.py",
    "joulewise/arm_readiness.py",
    "scripts/run_campaign.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B -c \"import joulewise.arm_readiness, joulewise.claim_hold\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B scripts/run_campaign.py --help",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["usage: run_campaign.py [-h]"]},
      "expected": {"exit_code": 0, "tail_regex": "usage: run_campaign.py"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full suite was not run, as directed.",
      "needs": "Lead runs the whole suite on the bench."
    }
  ]
}
```

## Change

S2 refuses a claim-eligible live GO receipt when the machine build is held; replay does not read the machine. S3 refuses a non-dry-run claim-bearing campaign before `run_campaign` starts. The machine-build reader uses `/usr/sbin/sysctl -n kern.osversion` through `subprocess.run`, returning `None` on failure.

Exact diff:

```diff
diff --git a/joulewise/claim_hold.py b/joulewise/claim_hold.py
new file mode 100644
--- /dev/null
+++ b/joulewise/claim_hold.py
@@ -0,0 +1,32 @@
+"""Operating-system-build holds on claim-bearing work."""
+
+from __future__ import annotations
+
+import subprocess
+
+
+CLAIM_HELD_OS_BUILDS: dict[str, str] = {
+    "25G83": "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
+}
+UNKNOWN_BUILD_HOLD = "UNKNOWN-OS-BUILD (a build that cannot be read is treated as held)"
+
+
+def claim_hold_for_os_build(os_build: object) -> str | None:
+    """The name of the hold on this build, or None if claims are allowed."""
+    if not isinstance(os_build, str) or not os_build:
+        return UNKNOWN_BUILD_HOLD
+    return CLAIM_HELD_OS_BUILDS.get(os_build)
+
+
+def machine_os_build() -> str | None:
+    """`/usr/sbin/sysctl -n kern.osversion`, stripped; None on any failure."""
+    try:
+        result = subprocess.run(
+            ["/usr/sbin/sysctl", "-n", "kern.osversion"],
+            capture_output=True,
+            text=True,
+            check=True,
+        )
+    except (OSError, subprocess.SubprocessError, UnicodeError):
+        return None
+    return result.stdout.strip() or None
diff --git a/joulewise/arm_readiness.py b/joulewise/arm_readiness.py
--- a/joulewise/arm_readiness.py
+++ b/joulewise/arm_readiness.py
@@ -28,6 +28,7 @@
 from joulewise import clock_reference as _clock_reference
+from joulewise.claim_hold import claim_hold_for_os_build, machine_os_build
 from joulewise.calibration_bracketing import (
@@ -10132,6 +10133,10 @@ def _authenticate_pack_launch_go(
         if go["purpose"] == "T0_REHEARSAL" and authorization["claim_eligible"]:
             raise _go_invalid("authorization.claim_eligible")
+        if authorization["claim_eligible"] and require_current_boot:
+            hold = claim_hold_for_os_build(machine_os_build())
+            if hold is not None:
+                raise _go_invalid("claim_hold: " + hold)
         confirmation = _go_record(go["confirmation_record"], "confirmation_record", night_root)
diff --git a/scripts/run_campaign.py b/scripts/run_campaign.py
--- a/scripts/run_campaign.py
+++ b/scripts/run_campaign.py
@@ -49,6 +49,7 @@
 from joulewise.bundle import sanitize_id_component  # noqa: E402
+from joulewise.claim_hold import claim_hold_for_os_build, machine_os_build  # noqa: E402
 from joulewise.arm_readiness import (  # noqa: E402
@@ -8986,6 +8987,15 @@ def main(argv: list[str] | None = None) -> int:
         if args.whole_window_verdict:
             return run_whole_window_verdict(args)
+        if not args.dry_run:
+            extension = load_campaign_policy(
+                args.campaign_policy
+            ).idle_admission_extension
+            if extension is not None and extension.claim_bearing:
+                hold = claim_hold_for_os_build(machine_os_build())
+                if hold is not None:
+                    print(hold, file=sys.stderr)
+                    return 2
         return run_campaign(args)
```

## Verification notes

The two requested smoke checks and `git diff --check` passed. The full suite remains for the lead’s bench run.