# Bench cure record after the round-4 verification (file 51), 2026-09-03 20:40 PDT

Magistrate at the bench (under the delegation threshold): seven edits to `docs/contracts/identity_pin_projection.md` curing file 51 S1–S4 and N4, plus the verifier's B1 cure step (the mechanical extraction is re-run below; row-by-row triage is delegated to the §5 fresh pass, which must re-derive it independently).

## Edits (old → new)

```
diff --git a/docs/contracts/identity_pin_projection.md b/docs/contracts/identity_pin_projection.md
index 6a5cdd11..87fa2b4c 100644
--- a/docs/contracts/identity_pin_projection.md
+++ b/docs/contracts/identity_pin_projection.md
@@ -465,7 +465,7 @@ probes runtime metadata or writes anything:
    resolves each declared member's `suite_manifest_ref` — a
    repository-relative path, of which only the part after the pack directory's
    name is kept — as a regular, non-symlink file whose resolved path stays
-   within the campaign pack, reads it, and requires its SHA-256 to equal the
+   below the campaign-pack directory, reads it, and requires its SHA-256 to equal the
    member's declared `suite_manifest_sha256`. A reference that cannot be
    resolved that way, a file that cannot be read, or a digest that differs
    refuses with reason code `readiness_identity_environment_dirty` ("declared
@@ -570,7 +570,8 @@ the current digest is available. The receipt status is `REFUSE` and carries the
 sorted refusal code. Errors raised before the frozen receipt can be
 authenticated escape to the readiness layer that maps projection evidence into
 the arm decision. That layer maps the same code into readiness refusal, but Arm
-may have issued nothing to bind.
+may have issued nothing to bind (`joulewise/identity_pins.py:2100-2234`;
+`joulewise/arm_readiness.py:5681-5729`).
 
 Arm re-verification calls the same `_derive_projection_units` comparison, so
 the common-profile equality, declared manifest membership, exact census, and
@@ -585,7 +586,7 @@ derivation never edits its declaration or census.
 - **U11** is the identity-pin projection subsystem and its projection-evidence
   row inside the U8 freeze receipt.
 - **Launch lineage** is the authenticated receipt chain from a collected bundle
-  back to the consumed arm authorization and its exact **pack digest**.
+  back to the consumed arm authorization and its exact **pack digest** (the SHA-256 of the committed campaign-pack tree).
 - An **arm receipt** is the record written when the arm ceremony authorizes one
   launch; that permission is the **single launch authorization**. Its
   `pack` (pack record) carries the **pack root**, meaning the
@@ -626,7 +627,7 @@ derivation never edits its declaration or census.
   `launch_binding_mismatch` (unavailable or mismatching bound path),
   `launch_lifecycle_incomplete` (missing required lifecycle receipt), and
   `consumer_identity_set_unauthenticated` (the analysis gate could not
-  authenticate the consumer identity set).
+  authenticate the consumer's distinct member identity set, built above).
 - The **exact-cell route** directly selects a bound floor cell only when the
   consumer has one scientific identity and the cell carries that same identity
   and runtime stack.
@@ -653,8 +654,9 @@ unit config-set digest against the receipt.
 Only a bundle whose configuration carries `launch_lineage_required` (the
 launch-lineage-required tag) is lineage-checked. An untagged bundle is admitted
 without a lineage read. Before a lineage-checked bundle is admitted as analysis
-input, bundle loading authenticates its launch lineage through the recorded
-paths and refuses at input loading (the bundle-to-analysis admission step), so
+input, bundle loading (the bundle-to-analysis admission step, called input
+loading below where it refuses) authenticates its launch lineage through the
+recorded paths and refuses at input loading, so
 the bundle never reaches this gate if a named artifact below is gone. The
 following hop list (the named artifact sequence) is not exhaustive of every
 launch-lineage check. In execution order (the order bundle loading checks
@@ -670,7 +672,7 @@ manifest at the path the consumption receipt recorded
 (`launch_consumption_invalid`); and the start and settle lifecycle receipts
 (`launch_lifecycle_incomplete`). When a named artifact and every later artifact
 in this list are gone, the earliest gone artifact emits its listed code. A
-receipt whose `.sha256` (sidecar suffix) sidecar is gone emits the same code as
+receipt whose `.sha256` sidecar (the digest file written beside it) is gone emits the same code as
 the missing receipt itself.
 
 Bundle loading uses `require_completion=False` (the **completion policy**):
@@ -729,7 +731,7 @@ them.
 
 ### What happens after arm
 
-The **ordinary launch step** authenticates and replays the arm receipt, pack
+The ordinary launch step authenticates and replays the arm receipt, pack
 digest, launch manifest, and one-use consumption record, as defined in
 §Analysis-gate definitions. It does not call
 `verify_frozen_projection`, `_derive_projection_units`, runtime `prepare`, or
```

## Mechanical first-use extraction re-run (verifier's `firstuse2.py` with DOC/ADDED pointed at this worktree and the diff vs 086d306f)

```
$ git diff -U0 086d306f -- docs/contracts/identity_pin_projection.md | <hunk parser> > added_lines_bench.txt   # 84 added lines
$ python3 firstuse2_bench.py
terms extracted: 93 (literals 21, NPs 72) | residue needing hand adjudication: 39

TERM                                     KIND     USE   DEF   DEFINED-BY
analysi consumption                      NP       13    -     NO DEFINITION FOUND
launch lineage sentence                  NP       13    -     NO DEFINITION FOUND
campaign pack directory                  NP       468   496   parenthetical gloss (the pack root)
arm decision                             NP       572   -     NO DEFINITION FOUND
layer map                                NP       572   -     NO DEFINITION FOUND
readiness refusal                        NP       572   -     NO DEFINITION FOUND
joulewise/identity pins.py 2100 2234     literal  573   -     NO DEFINITION FOUND
committed campaign pack tree             NP       589   -     NO DEFINITION FOUND
consumed arm authorization               NP       589   -     NO DEFINITION FOUND
arm ceremony authorize                   NP       590   -     NO DEFINITION FOUND
absolute path                            NP       593   -     NO DEFINITION FOUND
reviewed command                         NP       597   -     NO DEFINITION FOUND
one use record                           NP       600   -     NO DEFINITION FOUND
launched window                          NP       614   -     NO DEFINITION FOUND
launch lineage record                    NP       620   -     NO DEFINITION FOUND
absolute artifact path                   NP       622   -     NO DEFINITION FOUND
launch lineage refusal code used         NP       624   -     NO DEFINITION FOUND
analysi gate                             NP       629   682   parenthetical gloss ([S3 ruling (d)
consumer identity set unauthenticated    literal  629   -     NO DEFINITION FOUND
launch lineage required                  literal  654   -     NO DEFINITION FOUND
launch lineage required tag              NP       655   -     NO DEFINITION FOUND
untagged bundle                          NP       655   -     NO DEFINITION FOUND
lineage checked bundle                   NP       656   -     NO DEFINITION FOUND
bundle loading                           NP       657   -     NO DEFINITION FOUND
bundle to analysi admission step         NP       657   721   parenthetical gloss (3)
input loading                            NP       659   -     NO DEFINITION FOUND
execution order                          NP       662   -     NO DEFINITION FOUND
order bundle loading                     NP       662   -     NO DEFINITION FOUND
pack root recorded                       NP       667   -     NO DEFINITION FOUND
consumption receipt recorded             NP       669   -     NO DEFINITION FOUND
later artifact                           NP       673   -     NO DEFINITION FOUND
listed code                              NP       674   -     NO DEFINITION FOUND
.sha256                                  literal  675   -     NO DEFINITION FOUND
digest file                              NP       675   -     NO DEFINITION FOUND
receipt itself                           NP       676   -     NO DEFINITION FOUND
bundle loading use                       NP       678   -     NO DEFINITION FOUND
separate design decision                 NP       681   -     NO DEFINITION FOUND
s3 ruling                                NP       682   -     NO DEFINITION FOUND
analysi gate definition                  NP       736   -     NO DEFINITION FOUND
```

The extractor flags every two-or-more-word noun phrase in the added lines; a residue row is a term of art only if the reader must know it to replicate. The fresh pass triages every row (built / glossed at first use / ordinary phrase / defect) with line evidence. This record corrects file 50's description of its table as mechanical: that table was hand-enumerated (file 51 B1).

## Tests
```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs tests.test_arm_readiness_lifecycle | tail -3
[32mOK[0m ([33mskipped=4[0m)

```
