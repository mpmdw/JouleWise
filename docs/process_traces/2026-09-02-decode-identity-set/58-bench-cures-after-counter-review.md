# Bench cures after the Opus counter-review (file 57), 2026-09-03 21:50 PDT — file 58

SF1: the bold pack-digest definition now defers to the exact framing at step (2) instead of restating it partially. N1: the dead alias is removed ('called the gate below'). N3: '(each defined in §Analysis-gate definitions)'. N2 (line wrap) left.

```
diff --git a/docs/contracts/identity_pin_projection.md b/docs/contracts/identity_pin_projection.md
index f3d1e2c4..07dd54ab 100644
--- a/docs/contracts/identity_pin_projection.md
+++ b/docs/contracts/identity_pin_projection.md
@@ -587,9 +587,9 @@ derivation never edits its declaration or census.
 - **U11** is the identity-pin projection subsystem and its projection-evidence
   row inside the U8 freeze receipt.
 - **Launch lineage** is the authenticated receipt chain from a collected bundle
-  back to the consumed arm authorization and its exact **pack digest** (a SHA-256 over the committed campaign-pack files —
-  their paths, file modes and content digests — computed by
-  `committed_pack_tree_sha256`).
+  back to the consumed arm authorization and its exact **pack digest** (the SHA-256 that `committed_pack_tree_sha256`
+  computes over the committed campaign-pack files, framed exactly as step (2) of
+  §Analysis consumption states).
 - An **arm receipt** is the record written when the arm ceremony authorizes one
   launch; that permission is the **single launch authorization**. Its
   `pack` (pack record) carries the **pack root**, meaning the
@@ -630,9 +630,9 @@ derivation never edits its declaration or census.
   `launch_consumption_invalid` (invalid consumption-bound artifact),
   `launch_binding_mismatch` (unavailable or mismatching bound path),
   `launch_lifecycle_incomplete` (missing required lifecycle receipt), and
-  `consumer_identity_set_unauthenticated` (the analysis input gate — called the
-  analysis gate below — could not authenticate the consumer's distinct member
-  identity set, built above).
+  `consumer_identity_set_unauthenticated` (the analysis input gate, called the
+  gate below, could not authenticate the consumer's distinct member identity
+  set, built above).
 - The **exact-cell route** directly selects a bound floor cell only when the
   consumer has one scientific identity and the cell carries that same identity
   and runtime stack.
@@ -738,8 +738,8 @@ them.
 ### What happens after arm
 
 The ordinary launch step authenticates and replays the arm receipt, pack
-digest, launch manifest, and one-use consumption record, as defined in
-§Analysis-gate definitions. It does not call
+digest, launch manifest, and one-use consumption record (each defined in
+§Analysis-gate definitions). It does not call
 `verify_frozen_projection`, `_derive_projection_units`, runtime `prepare`, or
 the tokenizer (`scripts/launch_window.py:102-167,239-280`). Therefore a model,
 runtime, or tokenizer change after arm and before `execve`—the point where the
```
