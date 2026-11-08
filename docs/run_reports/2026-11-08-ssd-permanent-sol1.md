# Permanent SSD study and amendment — Sol seat 1

2026-11-08. Docs-only task `ssd-permanent`.
Branch at intake: `align/2026-11-08-ssd-permanent-sol1`, provisioned from
`origin/align/2026-11-08-v4-r11`, HEAD `c3796bf49256cb9243976915234f05c529657132`.
The initial worktree was clean. The local commit contains only the two new
drafts and this report; no push, merge or runtime/config adoption.

## Intake and authority

Read repository AGENTS/CLAUDE conventions, Mission M0, orchestration/source-
of-truth/report guidance, generated stop card (NONE), current queue and
Do-Not-Do-Yet list, workspace-state pointers, and targeted decision-log
D-078 addendum and D-186. Selected Ed's explicit bounded documentation task
in the AGENT lane. Per the brief, coordination state is lead-owned:
RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json and
tests/test_gen_state.py were not edited; no task was registered.

Authority read from **repository Git objects only** includes local
`origin/main` `3809bdd14da5882659f17dc292200d4afbbd1579`, RUN_STATE items
210/212/213/214 (R11, dedicated measurement MBP, R12 cadence); latency
synthesis `55029b860:docs/perf/2026-11-08-latency-synthesis.md`; the v4
protocol and its pinned FINAL-DESIGN source `6eb1ff5be`; kit README,
deviations, R11 handoff and KM003C capture contract. The task supplies the
new permanent-drive ruling and drive-free R0/R1/Sunday planning facts;
these were not independently observed. No remote freshness is asserted.

Read the old study/amendment, SSD qualification module/CLI, external-volume
checks, their synthetic tests, and both SSD reviews, especially the corrected
physical-block inference and Q3 mean-versus-variance limitation. Absolute
data locations in source text were not followed. No network, model download,
real measurement-data access, Block-5 pipeline, hardware/process probe or
quiet-machine capture occurred. The running blinded job was untouched.
No additional agents or external consults were launched.

## Deliverables and findings

- [SSD-PERMANENT-STUDY.md](../align/v4/SSD-PERMANENT-STUDY.md): revised
  rationale, ranked B/B-unmount/B-cut/A modes, channel-by-channel effects,
  DC error budget, extended protocol/time bill, R1 bridge, automation and
  purchase requirements. Old study retained.
- [DRAFT-AMENDMENT-permanent-ssd.md](../align/v4/DRAFT-AMENDMENT-permanent-ssd.md):
  prospective replacement terms for the old DC carve-out, exact device/mode
  allowlist, internal-only window storage, manifest, qualification,
  continuity and fault consequences. Old amendment retained.
- This report is the handoff; no coordination or registered protocol change.

Recommend mounted/no-I/O B only if GPU Q1, operational Q5 and proposed QDC
all pass; otherwise test automatic whole-disk unmount, then independently
verified port-power cut. All accepted modes target zero normal Ed actions
per window. Writes/member-gap backups are outside this proposal. Unmounting
does not establish electrical off; command success does not establish VBUS
cut. Hub/host power and battery flow remain visible in the DC boundary.

Proposed QDC uses the approximately 2 J replay scale rather than 19–58 J
regression misfit: uncancelled mean error ±0.10 J by 90% equivalence interval,
added SD ≤0.60 J by a one-sided 95% upper bound, tightened if the qualified
endpoint is finer. The 4.4% SD-inflation interpretation needs independent
additivity, or the stated direct total-SD/covariance alternative. These
fractions/inference are recommendations requiring prospective adoption,
not historical constants, U3 or proven DC precision. Offsets and variance
must be assessed with block/serial/baseline uncertainty, without per-test-
block re-centering; v5 still needs its entire primary endpoint qualification.

The inherited kit costs 6.833 h; five blocks with a 30-min minimum quiet
settle cost 8.5 h per candidate nominally. Three independent candidates cost
25.5 h before setup/bridge/longer decode or precision extensions. Setup and
bridge allowances bring the base bill to 13.5–18.5 h for one or 30.5–35.5 h
for three. These are not completion bounds. The bridge may require full R1;
the total for statistically decisive long-span QDC remains unknown.

One absent→present transition cannot identify a presence effect independently
of time. The draft explicitly requires one-time qualification-session
repeated physical blocks with Ed, before permanent freeze, or returns
INCONCLUSIVE. Five blocks give two residual df; three give zero. Testing all
modes may extend beyond Sunday. An unavailable switching hub remains pending.

R0/R1 bytes stay valid for their recorded drive-free configuration. Transfer
of throughput/budget/G0/thermal settings requires a measured, digest-bound
bridge before W1. Removal/replacement/failure after freeze has a named
configuration-break consequence: preserve evidence, hold future arms, no
post-break pooling under old calibration, and prospective requalification/
new segment or series authority. R12 terminal-close/short-triage/off-MBP-desk
cadence remains; longer necessary SSD settling increases actual turnaround.

## Verification

Ran sequentially with Python 3.13, synthetic data/fake system calls only:

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_ssd_qualification` | 26 tests OK, 0.340 s unittest time |
| `python3.13 -B -m unittest tests.align.test_external_volume` | 23 tests OK, 0.004 s unittest time |
| Inline Python document checks | All local Markdown links stay inside the clone and resolve; balanced fences, final newlines and no adjacent duplicate prose lines |
| Inline arithmetic check | 24,600/30,600 s plans; 6.833/8.5/25.5 h; 0.10/0.60 J power conversions; 4.403% SD inflation agree with drafts |
| `git diff --cached --check` and final staged scope review | Passed; exactly these three new Markdown files |

No full suite, pytest, compileall or MLX execution was needed for this
docs-only change. The brief prohibits the full suite during the blinded job.
Existing synthetic tests are regression evidence for the reused kit, not
implementation or validation of QDC, B-unmount, B-cut or the R1 bridge.
Final diff review checked all seven requested topics, consistency between
study/amendment, local links, numeric units, draft labels and preserved
v4/v5 authority boundaries.

## Open questions and next exact step

The lead compares the two independent seat drafts and dispositions the
proposed numeric tolerance, variance/predictive inference, physical-block
schedule, mode choice and fault consequences **before adoption**. No answer
is needed to complete these draft deliverables. Decide final hardware before
series freeze; if buying, require 4 TB, fanless/predictable power and verified
macOS behavior, with an independently powered-off port only if B-cut is used.

Then implement the mode-aware kit/magistrate/manifest/event-audit extensions
and run clean-machine native qualification after active jobs and agents
exit. The lead must run actual KM003C clock/coverage/battery/custody checks,
SMC/powermetrics captures, mounted/unmounted/real-VBUS-cut comparisons,
offload/remount/fault cycles, long-span DC tests and native MLX fixed-work
decode/R1 bridge. Existing native MLX regression selections such as
`tests.align.test_thermal_mlx` and `tests.align.test_cache_checkpoint_native`
belong outside this sandbox if that runtime integration changes; no model
weights are to be downloaded for synthetic tests.

Uncertain until measured: APST/ASPM through USB4, actual plateau power and
wake/GC timers, unmount savings, true hub cut/no-backfeed, per-window identity
and passive audit feasibility, DC precision at sub-joule tolerances, slow
drift, battery headroom, offload/settle timing, R1-setting transfer and the
final 4 TB device's behavior. Nothing in the drafts claims these passed.
