# PR #795 round-7 builder, 2026-11-15

Status at this record: implementation and local synthetic verification complete; commit/push, hosted quick and PR-body readback pending. Their final receipts will be recorded in PR #795. No research admission or merge.

The lead requested all findings from Mythos/Sol round 6 on 413697d4b be fixed or explicitly
returned for research rulings. First read: scratch/look-r6/HANDOFF.md, then sol-look-r7's
blocked handoff, prepared patch and PR draft. Clean base 66fa7c452; Git access restored;
`git pull --rebase` already up to date. M0: no active stop card, agent lane only, queue
triaged here, unrelated work absent. No MBP contact, real custody read, live measurement,
merge, integration installation, or external message.

The implementation map is fit interface §7 and manifest §7f; the complete findings table
is the PR body at /Volumes/JW-EXT/scratch/sol-look-r7b/pr-body.md. N3's 2 s clock-fit
constant is retained under RL-173, pending the research lead. The four malformed reader
shapes and persisted coefficient validation contract remain questions. Real-recording
tests under tests/fixtures/km003c remain excluded; directory names only were listed.

Independent work used scratch-only, disjoint patches from rerun_guards, diagnostics and
mutant_regressions. Root reviewed and applied each patch; workers never wrote the shared
worktree or Git metadata. Their evidence is retained in sol-look-r7b/{rerun-worker,
diagnostics-worker,mutant-worker}. A fresh read-only cold_delta_review found the native
PM source-binding omission and T-runtime hashing; root fixed both and completed the final verification below. Root
retains final diff/verification/authority. No new Mythos/Claude seat was started under the
handoff's quota restriction. Fresh cross-model final-head review remains a lead gate.

The final focused suite passed 389 tests (2 optional-dependency skips), including FreezeCommit and the host-command guard. The separate optional-dependency schema run passed all 14 tests. Mutant and final handoff details follow below.
Canonical whole-repository discovery is excluded by the user's synthetic-only blinding
constraint: this is a focused synthetic package verification, not live custody admission.
FreezeCommit's synthetic look copy now omits tests/fixtures entirely. No advisor-visible
state changed, so PROJECT_STATUS.md is unchanged.

## Findings disposition and research questions

All Sol NEW-1 through NEW-7 are repaired (NEW-4 at the inherited 66fa7c452).
Mythos N1/N2/N4/N5/N6/N7/N9/N10 are repaired; N8 is disposed by the documented
non-admitting kept-R reproduction path. N11's code/help/receipt items and eleven
surviving guard mutants are repaired. N11's real-recording tests remain excluded.
The detailed per-item reasoning is in interface §7, manifest §7f and the PR table.

Research-lead questions, without a builder ruling:

- N3: retain RL-173's 2 s clock-fit excess line and disclose admitted small counter
  steps, or rule a different detector/bound. The constant is unchanged.
- N11: retain conservative refusal for p:null, payload with n=0, depth >64 and float
  rx, or expand support. No producer equivalence is claimed for those shapes.
- N11: define persisted-coefficient schema/code authentication at a file-reader
  boundary, keeping the existing predict function read-free.
- Confirm N8's non-admitting reproduction procedure and N9's stable fit provenance
  projection (custody.files retained; ledger position/local locators omitted).
- Carry forward the seven questions in look-r6/HANDOFF.md: both clock-fit signs;
  sub-threshold hidden holes; energy-fit interval scope; span-wide unreadable-stream
  exclusion and compressed-file refusal; ruling ids for hash corrections; whether
  desk custody is compressed; Q11's applied .08 and the outstanding five-world
  sentence. The builder has not issued new research or operational rulings.

## Gate yield and limitations

The independent delta reviewer found a native-PM source-binding omission and a
T-runtime hashing expansion before final verification. The lead added a blinded
native timing/state digest, skipped T runtime, and preserved already excluded
malformed A rows. Focused integration also caught stale file-list/message assertions
and the synthetic no-custody step-3 receipt compatibility path; these were corrected.
Initial working-snapshot runs, including pin comparisons invalidated by ongoing
source edits, are retained in scratch and are superseded by the final stable-tree
runs below. The first extra twin check used counts.soak_retries instead of the
actual top-level field; the corrected exact-equality check passed.

The final code stays at the existing estimator constants and has no live evidence.
Campaign seal/marker authentication remains upstream of these tools; reader file
hashes and their agreement are checked here. New Mythos/Claude seats remain excluded
under the handoff's quota instruction; the lead owns any final cross-model gate and
research admission. The fresh read-only Sol delta report is retained at
/Volumes/JW-EXT/scratch/sol-look-r7b/cold-review/REPORT.md; its compatibility follow-up
covers the final step-3 change and updated R-18 mutant anchors.

The twin was maintained independently from the interface only in the private
sol-look-r7b/twin directory. Its 68 tests passed after fixture provenance refresh;
R/E/P bytes and D/O/C scientific content remained unchanged. Root's final agreement
run includes the original nine sets and a tenth planted receipt/custody-map case.

## Final stable-tree verification

- Focused synthetic suite: **389 tests, OK (2 skips), 661.485 s**; includes the frozen
  committed-copy child, all look modules, prediction, both new regression modules,
  host-command sites and the expected-failure census. Command and output:
  /Volumes/JW-EXT/scratch/sol-look-r7b/focused-final3.log (private TMPDIR).
- Optional schema differential checks: **14 tests, OK**, using the already retained
  twin .schema_deps; no dependency installation or network fetch. Log:
  /Volumes/JW-EXT/scratch/sol-look-r7b/schema-differential.log.
- Independent twin: **10/10 D/O/C/P/cross comparisons pass** (the original nine plus
  the ruled soak/custody-map case), with explicit custody map and top-level soak
  print equality in the extra case. The twin's own suite is **68/68**. The established
  comparison tolerances and provenance exceptions are retained; no value tolerance
  was relaxed. Evidence: sol-look-r7b/agreement/{compare.log,compare_result_r6.json,
  EXTRA-CHECKS.txt}, twin/WIRE_UPDATE_TEST_RESULTS.txt.
- Mutant harness: **133 killed / 133, 0 survivors, 0 invalid** after an unmutated
  control pass. `python3 -B tests/cadence/mutants_fit_interim.py --jobs 3`; log:
  /Volumes/JW-EXT/scratch/sol-look-r7b/mutants-final2.log. All 133 anchors matched
  exactly once, including the eleven independent N11 survivors and the retargeted
  custody/R-18 guards.
- Manifest validate --repo: **ok, draft, 0 placeholders**. Dry pin: **0 changes**.
  Published manifest schema: 0 errors. Syntax checks, git diff --check and
  scripts/gen_state.py --check pass.

The required hosted quick result is recorded in PR #795 after this record is pushed;
local checks do not substitute for hosted CI. The final push and complete PR-body
readback remain the builder's last actions. Do not merge.

## Handoff

Next the builder commits and pushes this verified source with the requested Sol trailer,
checks the exact head's quick job using gh run list / gh run view, writes the complete
findings body from sol-look-r7b/pr-body.md and re-reads it for exact equality. The PR
body is the final hosted-CI/head receipt; this tracked report is the local verification
record. Next lead action: review N3/N11 and the carried questions above, arrange any
quota-dependent Mythos final-head gate, and retain draft status until research admission.
No merge is authorized by this handoff.
