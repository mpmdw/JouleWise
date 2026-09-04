# Cold-gate packet — decode-identity lane after the two delta re-audits (F-B, F-N/F2), 2026-09-02

Mechanically assembled by the magistrate under the cold-gate charter
(`docs/process/coldgate_charter.md`, sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`,
registry `docs/process/coldgate_charter_registry.md:16`). Trigger: rule 11
"any second fix round on the same defect" — luna 259 (file 17) reports that
the round-1 closure of F-B has no biting test, and both delta re-audits
report a first-use prose defect on text that round 1 (F-N) and round 1b
(R-M5) each wrote. The magistrate does NOT classify (the party proposing to
continue does not classify its own defect); Q1 and Q2 ask the seats to.
Seats read ONLY this packet and the primary evidence it names. Read-only.

Checkout: `/Users/edr/code/JouleWise-wt-decode-id` (or a detached copy) at
`7c87fa71` = code head `9e4b7c35` + docs-only custody. Lane history is in
this directory: ruling `06-ruling-171a.md`; round-1 brief `13-…`, Sol 214
report `14-…`; round-1b brief `15-…`, Sol 258 report `16-…`; the two delta
re-audits `17-luna-259-…` (round 1) and `18-terra-260-…` (round 1b).

## Mechanism under review (built from the code)

`_frozen_consumer_identity_set` (`joulewise/analysis_engine/inputs.py`
~3860–4048) is the analysis gate's authentication of the frozen consumer
identity declaration. It reads the launch-lineage rows on the evidence
(each carries `pack_root` and `pack_sha256`), and — the F-B closure, added
by round 1 at commit `3ac6cffb` — re-verifies the pack's committed tree
digest against the lineage's `pack_sha256` BEFORE trusting any field of
`plan_tree.json`:

```
3896    try:
3897        pack_root = Path(next(iter(pack_roots))).resolve(strict=True)
3898        if committed_pack_tree_sha256(pack_root) != next(iter(pack_hashes)):
3899            return frozenset()
```

Every `return frozenset()` in that function is, since round 1b (`9e4b7c35`),
labelled `consumer_identity_set_unauthenticated` at the production caller.

F-B's origin (Opus 204 F1, file 12; brief file 07 line 46): before round 1,
the gate read `plan_tree.json` by bare path with no digest check, and a
SELF-CONSISTENT forgery — swapped `config_inventory`, recomputed
`config_set_sha256`, re-rendered receipts, sidecars and both `plan_tree`
references — made the gate return the prefill unit's set instead of the
decode set. The closure was "authenticate the pack inside the gate";
regression named by the brief: "the tampered-pack test" (F-D).

## The finding under Q1 (luna 259 F-B, blocker)

Sol 214's clause map (file 14, row F-B) names
`tests/test_analysis_inputs.py::FrozenConsumerIdentitySetTests::test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes`
as the biting test for the counterfactual "remove the committed-pack digest
comparison". That test (lines 751–766) builds a generated frozen pack, then
flips ONE BYTE in the projection receipt file and asserts refusal. The flip
is caught by the receipt's own byte-digest sidecar check, so the pack-tree
comparison never decides the outcome.

## Executed evidence (bench, this session, `/Users/edr/code/JouleWise-wt-decode-id2` at `3ac6cffb`, `TMPDIR` under the scratchpad; bytes restored, `git diff --exit-code` clean)

```
$ python3 - <<'EOF'      # replace line 3898's comparison by `if False:` on a copy, in place
p="joulewise/analysis_engine/inputs.py"; s=open(p).read()
old="        if committed_pack_tree_sha256(pack_root) != next(iter(pack_hashes)):\n            return frozenset()\n"
assert s.count(old)==1
open(p,"w").write(s.replace(old,"        if False:\n            return frozenset()\n"))
EOF
$ python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests
Ran 6 tests in 6.226s
OK
$ cp <scratch>/inputs.py.orig joulewise/analysis_engine/inputs.py && git diff --exit-code --stat && echo REVERTED-CLEAN
REVERTED-CLEAN
$ git log --format='%h %ad %s' --date=short -L3898,3899:joulewise/analysis_engine/inputs.py | grep -E "^[0-9a-f]{8} "
3ac6cffb 2026-09-02 Decode-identity fix round 1 (Sol 214): ruling 171a R-1..R-8 closures F-A..F-L, F-N..F-P
```

So with the F-B check disabled, the ENTIRE round-1 test class (all six
tests, including `…refuses_plan_receipt_config_set_mismatch`, which commits a
tampered `plan_tree` and is caught by the projection-vs-receipt
`config_set_sha256` equality) still passes. No test in the class exercises
the pack-tree comparison. The check itself was introduced by round 1.

## The finding under Q2 (luna 259 F-N should-fix; terra 260 F2 should-fix)

Round 1 closed F-N ("first-use ordering in
`docs/contracts/identity_pin_projection.md` ~563–600") by adding a
definitions block at lines 565–579. luna 259: "U11 is first embedded
unglossed in the earlier work-order bullet: `work_order` is
`D117-U11-IDPIN-PROJECTION`" — a fixed identifier string that contains the
token U11 before the definitions block. terra 260 (on round 1b's NEW
paragraph at ~602–614): "U11 receipt" (the composite) and "frozen
declaration" are not defined before first use; the paragraph leans on
"the authentication sequence above" and is not standalone. Quoted first
sentence (terra): "If successor launch lineage exists but the gate cannot
finish the authentication sequence above—for example, the lineage rows are
incomplete or disagree, the pack digest, U8 freeze receipt, U11 receipt, or
a sidecar does not authenticate, … — the floor resolution is refused with
`consumer_identity_set_unauthenticated`."

The writing standard in force (Ed, 2026-08-19): every term of art is built
or glossed at first use or deleted; a reader must be able to replicate the
mechanism from the text alone.

## Other open findings (first-round, no trigger; listed so the seats see the whole round-2 composition)

- luna F-G (should-fix): `_distinct_manifest_identity_refusal_reason`
  (`joulewise/identity_pins.py:~1571`) is killed only by a direct helper
  test with synthetic sets; nothing proves the production freeze path
  reaches the mismatch.
- luna F-COUPLING (should-fix):
  `test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell`
  mocks `_frozen_consumer_identity_set`, so it passes even if the real gate
  is eviscerated.
- terra F1 (should-fix): `_floor_engine_reasons`
  (`joulewise/analysis_engine/__init__.py:~207`) maps both new labels to
  `floor_transport_inapplicable` through its default branch; a mutant
  mapping them to `floor_row_missing` survives all four production-label
  tests; no test pins the mapping.
- Everything else in both re-audits: KILLED / verified (luna A1 12 of 13
  rows killed, two own mutants killed; terra A1 (a)–(f) killed, A2 four
  authentication exits all labelled correctly, A3 discriminator sound,
  wrapper seam pinned by three tests; 327 tests OK on both heads; digest
  `1c0a4a11…` unchanged).

## Questions for the seats

Q1 (classification — FIRST, independently). The F-B production check
exists and is correct; what is missing is a test that bites its removal.
Is "closure claimed with a non-biting test" a SECOND fix round on defect
F-B (rule 11 trigger met; the round-1 cure counted as round one), or a
first-round finding against the mutation-cure rule ("today's-artifact
cures kill nothing") that stands on its own? State the rule you applied.
Then: what is the DEFECT-SHAPED counterfactual input for F-B — describe
the fixture concretely (which bytes change, what stays self-consistent,
what the lineage still records) such that the pack-tree comparison is the
ONLY check that refuses it — and confirm by execution that such a fixture
is buildable from `FrozenConsumerIdentitySetTests._generated_frozen_gate_pack`
(or say what is missing).

Q2 (classification). Is terra F2 (new paragraph, round 1b) the same defect
as F-N (round 1's first-use closure) — a second round on F-N — or a new
first-use defect on new text? Is luna's F-N residual (the token U11 inside
the fixed identifier `D117-U11-IDPIN-PROJECTION` before the definitions
block) a first-use violation under the standard, or is an identifier not a
"use" of the term? Say what closes each: reorder, gloss in place, or a
standalone rewrite of the ~602–614 paragraph that a reader can rebuild the
two labels from without "above".

Q3 (composition of fix round 2). Given Q1–Q2: may F-B's biting test, F-G's
production-path test, F-COUPLING's unmocked test, terra F1's mapping pin,
and the prose cures land as ONE fix round (Sol, then a delta re-audit by a
different model), or does anything in the set require a separate ruling
first? Name any clause where the seat would refuse to let the magistrate
brief it without a ruled semantics.

Q4 (gating). The branch is not yet a PR. Until round 2 lands, what does a
consumer of the analysis output lose — in terms of what a self-consistent
forgery can do — given the production check IS present and only its test
is missing? Answer in the mechanism's terms, not process cost.

## Charter §9 expected digest

The charter digest above is supplied here for the seat to verify against
`docs/process/coldgate_charter_registry.md` independently of this packet.
