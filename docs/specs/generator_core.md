# Campaign generator common core

Status: scoped design and implemented desk-time core for `GENERATOR-CORE-01`.

## Forcing problem

The ten D-117 campaign generators on the 2026-09-04 base repeat the same
write-boundary validator. Nine also repeat the same generation-identity class.
Together with four small byte-rendering and inventory helpers, a direct
extraction would remove 1,533 lines. A correction to path safety or
successor-family identity therefore has to be repeated across files whose
scientific pins are otherwise different. The code-and-tests audit recorded this copy pattern in
`docs/process_traces/2026-09-02-hands-free-week/13-audit-code-tests-opus.md`,
section 3.2.

The generator source is itself part of successor pack output. Historical pack
generators also preserve frozen pack bytes. A refactor must therefore separate
shared executable mechanics from campaign-owned pins without pretending that
the self-emitted generator file can remain byte-identical.

## Options

1. Keep copying complete generators. This preserves local readability but
   retains ten independently repairable write boundaries and makes the next
   producer another multi-thousand-line clone.
2. Turn every campaign choice into one universal data schema. This would merge
   `GENERATOR-CORE-01` with the separately queued `MODULARITY-01` policy change
   and would require rulings about which scientific differences are data.
3. Extract only byte-identical mechanics and inject family pins through a small
   factory boundary. Historical generators keep their existing public names;
   campaign-specific planning and scientific definitions stay in their owning
   files.

## Recommendation

Use option 3 for unfrozen and future producers. `joulewise.campaign_generator_core` owns canonical JSON bytes,
SHA-256 sidecars, pack inventory, the desk-time write boundary, and the common
generation-identity implementation. Each generator imports those operations
and supplies its pack path, version suffix, freeze state, and arm-readiness
attachment. This is a mechanical extraction, not a new scientific contract.

The full-file parameterization in option 2 remains the job of `MODULARITY-01`.
Keeping that boundary explicit prevents a maintenance refactor from changing
registered campaign semantics.

The unfrozen `d117_contrast_v5` generator now uses this module. The nine
historical generators remain byte-for-byte unchanged pending the custody
ruling below; their local copies are frozen snapshots, not the recommended
shape for new work.

## Worked example

For a producer rooted at `configs/campaigns/example_floor_v6`, the producer
retains its model, workload, cell, and acceptance pins. It imports
`validate_generation_write_boundary` and constructs `GenerationIdentity` with
`make_generation_identity_class`, passing `PACK_REL`, `_v6`, its frozen-byte
mode, and callbacks to its authenticated freeze attachment. Before emitting
`calibration_plan.json`, it supplies the closed relative-path inventory to the
shared validator. A symlink at `example_floor_v6/condition_families` refuses
before any write. Changing a model pin still changes only the producer.

## Byte-parity boundary

Parity has two parts:

- For generated scientific and control artifacts, compare every relative path
  and byte except `generate_configs.py` between the pre-extraction generator
  and the extracted generator. The generator file is excluded because its new
  import is the change being made and because successor packs intentionally
  carry that source.
- For historical frozen packs, run each generator's existing check mode. It
  must reproduce or preserve every generator-owned artifact under the same
  frozen-byte rules.

The focused regression also requires all ten generator modules to expose the
same shared function objects. Restoring even one local validator or renderer
therefore fails the test even when its current behavior happens to match.

## Open integration ruling

The first attempted mechanical extraction made the repository's own committed
pack verifier refuse with `disk and committed bytes/mode differ for
generate_configs.py`. Those nine source files are inside the authenticated pack
trees. Updating their source digests would rewrite historical evidence, while
leaving them unchanged means the acceptance phrase “one shared module holds
the byte-identical core” is not literally true for historical snapshots.

NEEDS_RULING: decide whether historical, hash-pinned generator snapshots are
exempt from deduplication. Recommendation: exempt them, require the shared core
for every unfrozen and future producer, and do not refresh historical digests.

Separately, the next floor producers are already implemented, but not merged,
on `feat/2026-09-02-v5-floor-generator` at `557b7fc5`. They are not present on
the base of this worktree. Integrating them here by copying would create two
competing histories and bypass their recorded review chain.

NEEDS_RULING: choose how the third acceptance item is harvested.

- Option A: merge this common-core change first, then rebase the reviewed V5
  producer branch and replace its copied mechanics with shared-core imports.
- Option B: merge the reviewed V5 producer branch first, then resume this row
  with those two files present and extract them in the same parity pass.
- Option C: treat the parameterized contrast V5 consumer as the “next floor
  producer.” This is not recommended because it is not a floor producer.

Recommendation: Option A. It preserves the producer branch's review history,
makes its common-core adoption a small visible delta, and satisfies the row
without inventing a second producer implementation.
