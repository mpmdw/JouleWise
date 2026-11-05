# R0 coordination patch series — N5b, PR #661

For the lead of `lane/2026-11-05-align-r0-desk`. No R0 branch was edited.
These are reviewable patches against cached R0 commit
`49e78e1784b6b498ace68895d8fbdd2443214e9d`. Rebase onto the reviewed v4 lane
before applying; do not claim the cached Next-80B config is current.

Authority: the round-2 lead ruling N5b and
`origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md`.
**required free = amendment-1 window-1 bundles for two copies + 30,000,000,000
bytes**. There is no flat 80 GB threshold. Keep disk_path on the internal
measurement filesystem; external free space cannot satisfy it.

The amendment blob is absent from this clone's cached council tip. No numeric
W1 value or amendment SHA is invented: the example intentionally refuses with
null bytes and an invalid citation. The R0 lead must record the actual W1
per-copy bytes, verify they mean bundles (not weights or total gold scratch),
fill the full amendment SHA:path, review and commit that v4 config, then include
it in the six-ref census. The citation is a review binding; the scalar is not
mechanically extracted from prose. That review remains an explicit gate.

Apply each fenced diff as a separate R0 commit after reviewing it. Tests in
`tests/test_align_offload_r0_patch.py` apply the exact delivered diffs to the
cached base in a synthetic temp checkout and exercise extracted pure functions;
they never run R0, MLX, a hardware probe or a real inventory.

## Patch 1 — derive the disk gate from the reviewed window budget

Suggested R0 commit: `fix(r0): admit two W1 bundle copies plus the 30 GB floor`.

```diff
--- a/joulewise/align/r0_host.py
+++ b/joulewise/align/r0_host.py
@@ -115,7 +115,31 @@
     return sorted(rows, key=lambda row: row["path"])


+
+DISK_FLOOR_BYTES = 30_000_000_000
+AMENDMENT_PATH = "docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md"
+
+
+def required_free_bytes(config):
+    """Reviewed amendment-1 W1 bundles, two copies, plus the 30 GB floor.
+
+    The input belongs to the reviewed v4 R0 config, not an operator CLI flag.
+    No historical flat threshold or guessed amendment value is a fallback.
+    """
+    budget = config.get("disk_budget", {})
+    if set(budget) != {"window1_bytes_per_copy", "copies", "authority"}:
+        raise ValueError("disk_budget requires amendment-1 W1 bytes, copies and citation")
+    value = budget["window1_bytes_per_copy"]
+    if type(value) is not int or value <= 0 or type(budget["copies"]) is not int or budget["copies"] != 2:
+        raise ValueError("positive W1 bundle bytes per copy and exactly two copies required")
+    if not isinstance(budget["authority"], str) or not re.fullmatch(
+            r"[0-9a-f]{40}:" + re.escape(AMENDMENT_PATH), budget["authority"]):
+        raise ValueError("full amendment-1 commit:path citation required")
+    return value * 2 + DISK_FLOOR_BYTES
+
+
 def disk_census(config, pins, tick=lambda: None):
+    required = required_free_bytes(config)
     free = shutil.disk_usage(config["disk_path"]).free
     models = {}
     for tag, entry in config["models"].items():
@@ -138,10 +162,12 @@
                          "inventory": item["inventory"], "destination": item["destination"],
                          "observed": actual})
     covered = {row["label"] for row in offloads if row["pass"]}
-    return {"status": "pass" if free >= 80_000_000_000 and {"pilot8", "pilot9"} <= covered else "fail",
-            "free_bytes_after_present_weights": free, "required_free_bytes_after_weights": 80_000_000_000,
-            "design": {"W1_bytes_per_copy": 18_600_000_000, "W1_two_copies_bytes": 37_200_000_000,
-                       "D_two_copies_bytes": 52_900_000_000, "N_download_bytes": 44_860_367_003},
+    return {"status": "pass" if free >= required and {"pilot8", "pilot9"} <= covered else "fail",
+            "free_bytes_after_present_weights": free, "required_free_bytes_after_weights": required,
+            "design": {"W1_bytes_per_copy": config["disk_budget"]["window1_bytes_per_copy"],
+                       "W1_two_copies_bytes": required - DISK_FLOOR_BYTES,
+                       "floor_bytes": DISK_FLOOR_BYTES,
+                       "authority": config["disk_budget"]["authority"]},
             "models": models, "offloads": offloads,
             "note": "Download totals are diagnostics (mirror metadata can differ); free-space and offload hashes are gates."}

--- a/joulewise/align/r0_runner.py
+++ b/joulewise/align/r0_runner.py
@@ -14,7 +14,7 @@

 from joulewise.align import r0
 from joulewise.align.r0_host import (
-    QuietGuard, Refused, command, disk_census, host_snapshot, inventory, smc_enumeration,
+    QuietGuard, Refused, command, disk_census, host_snapshot, inventory, required_free_bytes, smc_enumeration,
 )

 CHECKS = ("host", "disk", "smc", "load", "template", "generated", "ladder", "long-decode", "memory")
@@ -34,7 +34,7 @@


 def validate_config(config):
-    if set(config) - {"schema", "models", "shade_cache", "disk_path", "custody_parents", "offloads"}:
+    if set(config) - {"schema", "models", "shade_cache", "disk_path", "custody_parents", "offloads", "disk_budget"}:
         raise ValueError("unknown R0 config field")
     if config.get("schema") != "joulewise.align.r0.config.v1" or set(config.get("models", {})) != {"N", "D"}:
         raise ValueError("R0 config requires schema v1 and models N and D")
@@ -55,6 +55,7 @@
         labels.add(row["label"])
         _path(row["inventory"])
         _path(row["destination"])
+    required_free_bytes(config)  # refuse missing/unreviewed amendment budget
     return config


--- a/docs/align/r0_desk.example.json
+++ b/docs/align/r0_desk.example.json
@@ -6,6 +6,11 @@
   },
   "shade_cache": "/Volumes/ALIGN_INPUTS/shade",
   "disk_path": "/Volumes/ALIGN_MODELS",
+  "disk_budget": {
+    "window1_bytes_per_copy": null,
+    "copies": 2,
+    "authority": "REQUIRED_FULL_SHA:docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md"
+  },
   "custody_parents": ["/Volumes/ALIGN_CUSTODY"],
   "offloads": [
     {"label": "pilot8", "inventory": "/Volumes/ALIGN_INPUTS/pilot8-source-inventory.json", "destination": "/Volumes/ALIGN_OFFLOAD/pilot8"},
```

## Patch 2 — preserve pilot measurement views as symlink records

Suggested R0 commit: `fix(r0): inventory pilot view links without following`.
Apply after patch 1. CLI --inventory and pilot-copy comparisons use
record_symlinks=True; model loading/inventories retain the default strict
materialized-file policy. A symlink row has path, type=symlink and exact target
text, never target bytes or target metadata. Preserve these links as links in
independent pilot copies. Blinded named directory entries still refuse before
stat or descent; no permission to inventory restricted content is granted.

```diff
--- a/joulewise/align/r0_host.py
+++ b/joulewise/align/r0_host.py
@@ -7,6 +7,7 @@
 from pathlib import Path
 import re
 import shutil
+import stat
 import subprocess
 import time
 from types import SimpleNamespace
@@ -79,41 +80,54 @@
             raise Refused(self.failure) from exc


-def inventory(root, tick=lambda: None):
-    """Hash regular files only; refuse symlinks and restricted subdirectories.
-
-    Operators supply a materialized local model mirror, rather than an HF cache
-    with links to another tree. This makes the hashed read boundary explicit.
-    """
+def inventory(root, tick=lambda: None, *, record_symlinks=False):
+    """Models stay materialized; pilot views record link text without following."""
     root = Path(root)
-    if "restricted" in root.parts or root.is_symlink() or not root.is_dir():
+    if ({"restricted", "withheld"} & {p.casefold() for p in root.parts} or
+            root.is_symlink() or not root.is_dir()):
         raise ValueError(f"not a materialized unrestricted directory: {root}")
     rows = []
-    def walk_error(exc):
-        raise exc
-    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
-        for name in dirs:
-            path = Path(directory) / name
-            if name == "restricted" or path.is_symlink():
-                raise ValueError(f"refusing directory: {path}")
-        for name in sorted(files):
+    def walk(directory):
+        # os.walk can stat a symlink target while classifying entries. Use
+        # lstat-style scandir metadata instead, even for dangling view links.
+        with os.scandir(directory) as entries:
+            children = sorted(entries, key=lambda entry: entry.name)
+        for entry in children:
+            if entry.name.casefold() in {"restricted", "withheld"}:
+                raise ValueError("refusing blinded directory entry")
             tick()
-            path = Path(directory) / name
-            if path.is_symlink() or not path.is_file():
+            path = Path(entry.path)
+            info = entry.stat(follow_symlinks=False)
+            name = path.relative_to(root).as_posix()
+            if stat.S_ISLNK(info.st_mode):
+                if not record_symlinks:
+                    raise ValueError(f"not a regular materialized file: {path}")
+                rows.append({"path": name, "type": "symlink", "target": os.readlink(path)})
+            elif stat.S_ISDIR(info.st_mode):
+                walk(path)
+            elif stat.S_ISREG(info.st_mode):
+                digest = hashlib.sha256()
+                size = 0
+                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
+                with os.fdopen(fd, "rb") as handle:
+                    opened = os.fstat(handle.fileno())
+                    if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
+                        raise ValueError("inventory file changed before open")
+                    for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
+                        tick()
+                        digest.update(chunk)
+                        size += len(chunk)
+                after = path.lstat()
+                if (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (
+                        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
+                    raise ValueError("inventory file changed")
+                rows.append({"path": name, "bytes": size, "sha256": digest.hexdigest()})
+            else:
                 raise ValueError(f"not a regular materialized file: {path}")
-            digest = hashlib.sha256()
-            size = 0
-            with path.open("rb") as handle:
-                for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
-                    tick()
-                    digest.update(chunk)
-                    size += len(chunk)
-            rows.append({"path": path.relative_to(root).as_posix(),
-                         "bytes": size, "sha256": digest.hexdigest()})
+    walk(root)
     if not rows:
         raise ValueError(f"empty inventory: {root}")
     return sorted(rows, key=lambda row: row["path"])
-


 DISK_FLOOR_BYTES = 30_000_000_000
@@ -156,7 +170,7 @@
         # been removed. No copying or deletion is performed here.
         import json
         expected = json.loads(Path(item["inventory"]).read_text())
-        actual = inventory(item["destination"], tick)
+        actual = inventory(item["destination"], tick, record_symlinks=True)
         ok = (isinstance(expected, list) and bool(expected) and expected == actual)
         offloads.append({"label": item["label"], "pass": ok,
                          "inventory": item["inventory"], "destination": item["destination"],
--- a/joulewise/align/r0_runner.py
+++ b/joulewise/align/r0_runner.py
@@ -195,7 +195,7 @@
             parser.exit(2, "Another R0 runner owns the machine lock\n")
         if args.inventory:
             guard.check(force=True)
-            rows = inventory(_path(str(args.inventory)), guard.check)
+            rows = inventory(_path(str(args.inventory)), guard.check, record_symlinks=True)
             with args.output.open("x") as handle:
                 json.dump(rows, handle, indent=2, sort_keys=True)
                 handle.write("\n")
```

Lead verification after rebase: run the native R0 inventory/config/disk tests
on synthetic roots, confirm dangling and measurement/ view links produce exact
link rows, confirm models still refuse links, then run the reviewed operator
inventories only after pause/retention authority. Run R0 hardware/model checks
outside this sandbox after the real v4 config and amendment citation are pinned.
Nothing in this patch authorizes deleting a pilot root.
