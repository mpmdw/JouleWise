# Bench cures after the delta re-audit (file 55), 2026-09-03 21:20 PDT — file 56

Two should-fixes from file 55: the analysis-gate alias was declared after its first use (:632 vs :647); 'modes' was unglossed at :591 (introduced by the L3 cure). Cures: the alias is declared at the first use inside the reason-code bullet and the later declaration removed; the pack-digest gloss now reads 'their paths, file modes and content digests' (the outer preimage carries content digests, not raw bytes — closes the disputed nit both ways).

```
diff --git a/docs/contracts/identity_pin_projection.md b/docs/contracts/identity_pin_projection.md
index efb59228..f3d1e2c4 100644
--- a/docs/contracts/identity_pin_projection.md
+++ b/docs/contracts/identity_pin_projection.md
@@ -588,7 +588,8 @@ derivation never edits its declaration or census.
   row inside the U8 freeze receipt.
 - **Launch lineage** is the authenticated receipt chain from a collected bundle
   back to the consumed arm authorization and its exact **pack digest** (a SHA-256 over the committed campaign-pack files —
-  paths, modes and bytes — computed by `committed_pack_tree_sha256`).
+  their paths, file modes and content digests — computed by
+  `committed_pack_tree_sha256`).
 - An **arm receipt** is the record written when the arm ceremony authorizes one
   launch; that permission is the **single launch authorization**. Its
   `pack` (pack record) carries the **pack root**, meaning the
@@ -629,8 +630,9 @@ derivation never edits its declaration or census.
   `launch_consumption_invalid` (invalid consumption-bound artifact),
   `launch_binding_mismatch` (unavailable or mismatching bound path),
   `launch_lifecycle_incomplete` (missing required lifecycle receipt), and
-  `consumer_identity_set_unauthenticated` (the analysis gate could not
-  authenticate the consumer's distinct member identity set, built above).
+  `consumer_identity_set_unauthenticated` (the analysis input gate — called the
+  analysis gate below — could not authenticate the consumer's distinct member
+  identity set, built above).
 - The **exact-cell route** directly selects a bound floor cell only when the
   consumer has one scientific identity and the cell carries that same identity
   and runtime stack.
@@ -644,8 +646,7 @@ derivation never edits its declaration or census.
 ### Analysis consumption
 
 For successor packs, every accepted bundle carries an authenticated launch
-lineage that resolves one pack root. The analysis input gate (called the
-analysis gate below) follows that
+lineage that resolves one pack root. The analysis input gate follows that
 already-authenticated root to the plan-pinned U8 readiness freeze receipt,
 authenticates its sidecar, requires its one
 `u11-freeze-projection` evidence binding to equal the plan's frozen projection
```

Mechanical check (grep, first use precedes declaration):
```
633:  `consumer_identity_set_unauthenticated` (the analysis input gate — called the
634:  analysis gate below — could not authenticate the consumer's distinct member
649:lineage that resolves one pack root. The analysis input gate follows that
591:  their paths, file modes and content digests — computed by
```
