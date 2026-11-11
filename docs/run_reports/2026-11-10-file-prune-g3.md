# File prune g3: CA-42 retirement held by live ALIGN registration

Branch: `ops/2026-11-10-file-prune-g3-ca42`, based on g2 `a7bacd7b1`.
**No code or test retirement lands in this group. The whole coupled unit is
KEEP.** The brief explicitly defers ALIGN v4 changes and says an unsure
deletion is a KEEP. This is a concrete dependency conflict, not a request to
weaken any registration or pin.

## Binding gate and disposition

Independently reviewed, then verified directly by this seat, from local Git
source only:

`origin/align/2026-11-08-v4-r11` resolves to
`9abe6095f98da581e149bfd1fc2bc2d0a582b2a3`.

- `joulewise/align/apple/v4_registration.py:66` defines `EXECUTED_CLOSURE`;
  line 331 includes it in `ARTIFACTS`. Twenty proposed deletions are required
  artifacts: seven package files and thirteen scripts. `validate_receipt`
  (lines 485–518) requires the exact artifact set, reads each committed and
  working-tree file, refuses missing paths, and requires re-registration
  for strict byte changes. `launch_window.py` is explicitly strict.
- `scripts/align_v4_next_arm_packet.py:31` imports
  `arm_retry.terminal_window_release` and calls it at line 173.
- #668's replacement modules are absent from the live static inventory.
  Keeping old-name shims alone cannot satisfy the recomputed executed
  closure after `run_night.py` starts importing the extracted modules.

`docs/ops/FILE-PRUNE-G3.tsv` records all 30 KEEP decisions: the 27 attempted
removals plus arm_readiness, night_gate and the still-imported G2-a helper.
Twenty paths have the direct ALIGN artifact binding; the rest stay as one
coupled route. Earlier named ALIGN refs were also inspected and had no
retired imports. No ALIGN source, registration, digest or receipt was edited.

#668 (`origin/lane/2026-11-05-prune-s2`, `68a8d66c3`) remains held, not
superseded or falsely claimed integrated. It must land only with its owning
ALIGN inventory/registration migration, or after that lane releases the
binding. No module was duplicated in the reviewable stack.

## Attempted adaptation, retained for review only

A local uncommitted merge of #668 was exercised, then safely aborted after
this gate was found. That merge preserved frozen `scripts/run_campaign.py`,
`joulewise/whole_window.py` and `joulewise/b5_analysis/**` bytes. It used nine
reader-only arm_readiness exports for protected callers and thirteen retained
pack generators, kept hazard import isolation strict, and migrated the active
refusal table to extracted source paths while checking both original Git
snapshots separately. Original digest literals were not rewritten.

The non-landable tracked-source diff is preserved outside the stack at
`/private/tmp/jwsol-file-prune/g3-unlanded.patch` (4,063,965 bytes, SHA-256
`3c32b1ee5971b42e2d526f7ff596f6cfc993ccbd57d8f109816da7ba05e21263`).
It is a prototype, not a tested landing candidate: registry/timing/citation
cleanup was unfinished and the ALIGN gate is unresolved. The current branch
has none of those code changes. Do not apply it directly to a live lane.

Exploratory checks on that adaptation (Python 3.13, unittest, synthetic seams):

| Selection | Result |
|---|---|
| test_prune_s2_closure | 4 OK |
| test_prune_s2_readers | 6 OK, synthetic canonical bytes/refusals and stored-reader equivalence |
| test_process_observer | 3 OK |
| test_arm_readiness_schemas | 50 OK after allowing the tests' explicitly fictional `/synthetic-home` in the supplementary guard |
| test_network_time_off | 11 OK; mocked OFF command, no machine setting changed |
| test_arm_retry | 36 OK |
| test_scheduler_gates | 17 OK |
| test_arm_readiness_evidence_t0 | 34 OK, 4 existing native/probe skips; 93 seconds |
| five static test_import_graph methods | 5 OK; no dynamic arm/monitor or hardware capture |
| test_refusal_allowlist | initial migration issues fixed, then 26 OK, 1 existing skip |
| test_frozen_files | 4 OK |

The two main refusal-snapshot identities differ because the first prune
changed the inventory: the original S2 digest was retained against commit
`92026c1849c0f053e56bdac6110c079211db2c31`; the release archive's distinct
identity was checked separately, never substituted for the original.
Historical issuer fixture copiers were also corrected to use immutable source
rather than the reader-only shim; those last copier edits were not rerun
before the whole prototype was held. A five-test static import check briefly
overlapped the pending T0 module (about 0.3 seconds); other unittest selections
were serialized. No full suite or eight-worker test job was run.

## Reviewable-branch verification and companion files

No deletion means the pin registry, refusal inventory, number-coverage tables
and timing map must remain exactly as on g2. For this unchanged code tree: `python3 -B scripts/repin.py --write registry`
completed with a byte-identical registry; `--check` passed all 16 families.
`python3 -m compileall -q joulewise scripts tests` passed. Individual unittest
modules `tests.b5_analysis.test_frozen_files` (4), `tests.test_b5_seal_landing`
(9), and `tests.test_docs_freshness` (31) all passed. No live deleted-path references exist because no path
was deleted. Original registrations, source digests, evidence, bundles and
coordination files remain unchanged. No native MLX validation is claimed.

Independent source/metadata review: `prune_readers_review`, read-only in this
clone; no writes, tests, external paths or network. Its decisive catch was the
live ALIGN artifact inventory. Final retention decisions and source checks
were made here.

## NEEDS_RULING after independent groups finish

Question: should g3 stay held until the ALIGN owner migrates its executed
closure and registration, or should a new explicitly scoped joint migration
be commissioned after the active R1 gate?

Options considered: (1) KEEP the coupled unit; (2) authorize owning-lane
inventory/registration migration and then rebase/reverify #668. Filename shims
alone were rejected because the executed closure still changes.

Recommendation: option 1 now. The active lane is live and this brief expressly
forbids its modification. Blocked work: the CA-42 coupled retirement and #668
landing only. Next exact step: the ALIGN lead supplies that migration/release
ruling; g1/g2 and the independent g4 evidence remain reviewable meanwhile.

All other deferrals remain: B5 analysis and whole-window mirror, remote stack,
site/report pipeline, scored lane, BYTES, B6, x86 and port work. Coordination
state was not edited or registered.
