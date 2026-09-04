# Bench cures after the §5 fresh pass (terra, 2026-09-03), file 53

Fresh-pass verdict at 28060067: NOT LANDABLE by two one-line cures (L1 stale citation, L2 unglossed 'runs root'); nits L3, L5, L6 also cured here; L4, L7, L8 left (pre-existing or intra-block ordering, recorded). Citations now name functions, not line ranges (the fresh pass's process observation).

```
diff --git a/docs/contracts/identity_pin_projection.md b/docs/contracts/identity_pin_projection.md
index 87fa2b4c..efb59228 100644
--- a/docs/contracts/identity_pin_projection.md
+++ b/docs/contracts/identity_pin_projection.md
@@ -570,8 +570,9 @@ the current digest is available. The receipt status is `REFUSE` and carries the
 sorted refusal code. Errors raised before the frozen receipt can be
 authenticated escape to the readiness layer that maps projection evidence into
 the arm decision. That layer maps the same code into readiness refusal, but Arm
-may have issued nothing to bind (`joulewise/identity_pins.py:2100-2234`;
-`joulewise/arm_readiness.py:5681-5729`).
+may have issued nothing to bind (`joulewise/identity_pins.py`
+`verify_frozen_projection`; `joulewise/arm_readiness.py`
+`_run_identity_arm_reverification`).
 
 Arm re-verification calls the same `_derive_projection_units` comparison, so
 the common-profile equality, declared manifest membership, exact census, and
@@ -586,7 +587,8 @@ derivation never edits its declaration or census.
 - **U11** is the identity-pin projection subsystem and its projection-evidence
   row inside the U8 freeze receipt.
 - **Launch lineage** is the authenticated receipt chain from a collected bundle
-  back to the consumed arm authorization and its exact **pack digest** (the SHA-256 of the committed campaign-pack tree).
+  back to the consumed arm authorization and its exact **pack digest** (a SHA-256 over the committed campaign-pack files —
+  paths, modes and bytes — computed by `committed_pack_tree_sha256`).
 - An **arm receipt** is the record written when the arm ceremony authorizes one
   launch; that permission is the **single launch authorization**. Its
   `pack` (pack record) carries the **pack root**, meaning the
@@ -618,7 +620,8 @@ derivation never edits its declaration or census.
   writing the consumption receipt; a second write of that same receipt is
   refused.
 - The **lineage locator** is the authenticated launch-lineage record stored in
-  a runs root beside the bundles it governs. The **recorded paths** are the
+  a runs root (the directory under which a launch's collected bundles are
+  written) beside the bundles it governs. The **recorded paths** are the
   absolute artifact paths named across the lineage locator, arm receipt,
   consumption receipt, launch manifest, and lifecycle receipts.
 - The **launch-lineage refusal codes used below** are
@@ -641,7 +644,8 @@ derivation never edits its declaration or census.
 ### Analysis consumption
 
 For successor packs, every accepted bundle carries an authenticated launch
-lineage that resolves one pack root. The analysis input gate follows that
+lineage that resolves one pack root. The analysis input gate (called the
+analysis gate below) follows that
 already-authenticated root to the plan-pinned U8 readiness freeze receipt,
 authenticates its sidecar, requires its one
 `u11-freeze-projection` evidence binding to equal the plan's frozen projection
@@ -679,7 +683,8 @@ Bundle loading uses `require_completion=False` (the **completion policy**):
 start and settle are required, while completion need not be present.
 Analysis of lineage-checked bundles runs on the filesystem that armed and
 launched them; relocating the lineage is a separate design decision, not a
-property of this gate ([S3 ruling (d)](../process_traces/2026-09-02-decode-identity-set/32-magistrate-synthesis-s1-s3.md#s3--machine-absolute-pack-root-split-ruled-d-for-this-lane)).
+property of this gate (the ruling that fixed this boundary is recorded in
+`docs/process_traces/2026-09-02-decode-identity-set/32-magistrate-synthesis-s1-s3.md`).
 Called directly with a lineage whose pack root does not resolve, the gate
 refuses with `consumer_identity_set_unauthenticated`, the same label as any pack
 it cannot authenticate.
```

Function names verified at HEAD: `grep -n 'def verify_frozen_projection\|def _run_identity_arm_reverification\|def committed_pack_tree_sha256'` → identity_pins.py:2379, arm_readiness.py:5681, arm_readiness.py:2750.

## Fresh-pass report (terra + wrapper adjudication), verbatim summary

See the wrapper's final message custodied below.
