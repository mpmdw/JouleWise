# Permanent SSD study and amendment — Sol seat 2

Brief date: 2026-11-08. Branch: `align/2026-11-08-ssd-permanent-sol2`, already
provisioned at `c3796bf49256cb9243976915234f05c529657132` with upstream
`origin/align/2026-11-08-v4-r11`. Working tree was clean at intake.
**Docs only; no adoption, hardware qualification or registration is claimed.**

## Delivered

- [SSD-PERMANENT-STUDY](../align/v4/SSD-PERMANENT-STUDY.md): replaces the old
  study's DC exception with a measured configuration-constant proposal; ranks
  B, B-unmount, B-cut, then rejected A; specifies mode-aware qualification,
  MBP time, R1 transfer, magistrate/manifest changes and 4 TB purchase requirements.
- [DRAFT-AMENDMENT-permanent-ssd](../align/v4/DRAFT-AMENDMENT-permanent-ssd.md):
  a prospective normative draft with one-device/one-mode admission, zero
  routine Ed actions, internal-only window writes, Q1/Q5/QDC, a pre-W1 boundary
  and CONFIGURATION_BREAK / REQUALIFY consequence.
- This run report. The old study/amendment and all code/config/tests remain
  unchanged. RUN_STATE, TASK_QUEUE, state kernel and test_gen_state were not
  edited; the user's explicit coordination-state fence overrides local M0/
  close-out instructions. No kernel task was registered.

The important numerical distinction is constant **power** versus constant
**energy**: a 5 W offset adds 1,500 J to an extra 300 s. The proposed QDC
budgets are ±0.10 J mean unexplained energy and ≤0.60 J added SD (95% upper
bound), scaled to the supplied ~2 J replay reference rather than 19–58 J
regression residuals. These are proposals for lead scientific adoption, not
existing constants or a measured DC resolution. At 1,800 s they correspond to
0.056/0.333 mW for coherent mean/SD errors, which may be unresolvable with the
available controls and meter/battery uncertainty. The study says so explicitly.

Reuse preserves five physical blocks / 125 slots / 6.833 h / 2 residual df;
the old runner's write-labelled slots and mount-based presence logic require
changes before quiet/unmounted/off operation. No executable QDC exists yet.
One candidate plus selected-mode maximum-window endurance is 23.367 h minimum;
all three plus endurance are 37.033 h minimum, excluding endpoint-length
controls, precision extensions, settling and handling. A full R1 repeat adds
about 18.71 h before retries/brackets/harvest. These are not promises that the
campaign fits a short Sunday visit or normal turnaround.

## Authority and safety

Read repository AGENTS/CLAUDE, M0, targeted restart/stop-card/workspace/queue
sections (no active stop card), orchestration and targeted D-018/D-043 text;
the task's explicit docs lane overrides ordinary queue selection. Read the
old study/amendment, SSD kit/source/tests and executing/burn reviews, protocol
v4, R1 runtime contract and KM003C integration. Read local Git objects for
RUN_STATE 210–214 (`origin/main` at `3809bdd14da5882659f17dc292200d4afbbd1579`),
latency synthesis (`55029b860adc775fc2ef10a8f9aff19f30af05d2`), adopted squeeze
agreement and final-design authority. The working-tree RUN_STATE predates those
items; the brief plus local object text supply the current ruling. No remote
freshness was verified. Two initially guessed document/ref paths were absent;
their actual local Git paths/remote-tracking refs were subsequently resolved.

No network, process/job inspection, measurement capture, model weights or MLX
execution. No sealed Block-5 analysis or real measurement bundle was read.
No filesystem path under `/Users/edr` outside this clone was followed; Git's
permitted shared object store is the only allowed Git-managed exception.
Absolute data paths seen in source documents were treated as text. No real
restricted directory or coordination state was inspected through a data path.
No delegation or external consult was used; this is one independent seat for
the lead's later comparison.

## Verification

All tests ran sequentially, one unittest module per process:

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_ssd_qualification` | 26 passed, 0.331 s |
| `python3.13 -B -m unittest tests.align.test_external_volume` | 23 passed, 0.004 s |
| Inline `python3.13 -B` local-link/fence and arithmetic check | PASS: both docs' relative links resolve within clone; 125 slots/24,600 s/2 df; power budgets, 23.367/37.033 h and Gaussian df=2 upper-bound factor 4.415 reproduced |
| `git diff --cached --check` | PASS before commit |

**49 tests passed.** These exercise existing synthetic kit behaviour, not the
new proposal or hardware. Full suite was explicitly prohibited and unnecessary
for three Markdown files; no code/MLX changes required compileall. No new test
was written to mirror prose. Final staged review is limited to the three
requested/report Markdown additions; old documents and protected state are
unchanged. Local commit identity is supplied in the final handoff and Git log;
no push was made.

## Open decisions and next exact step

The lead compares this seat's draft with the independent seat, then rules on
the proposed QDC budgets/inference method, selected mode and R1 transfer scope
before adopting text. Default recommendation is full R1 repeat in the selected
configuration; absent-drive R1 remains valid for its own configuration but is
not automatically portable. D-043 losing-rule annotations belong to adoption,
not this still-unadopted proposal.

Native work must occur outside this sandbox/active job in a clean,
lead-controlled quiet session: meter samples/clock/custody/battery flow;
absent-vs-candidate idle/decode and long-span controls; GPU Q1/Q5 plus QDC;
no-I/O and maximum-window state residency; electrical VBUS/backfeed/reset tests
if B-cut; unmount/remount/crash recovery; and final R1 thermometry/throughput/
budget/cap/duty transfer. These require the real measurement MLX/Metal stack;
the synthetic tests above discharge none of them. Any later implementation
should also run existing native `tests.align.test_thermal_mlx` and
`tests.align.test_cache_checkpoint_native` on the lead's Metal-capable host
where relevant to changed wiring, plus the actual native R1/WP19 gates.

Uncertain: actual DC replay SD; whether submW stability is attainable or even
resolvable; independent-block count required; APST/ASPM/daemon wake behaviour;
hub macOS electrical compatibility; exact remount/offload/settling latency;
Sunday availability for repeated physical controls; and final drive identity
if Ed purchases. No products were looked up. A mode lacking controls or a
decisive interval remains PROVISIONAL/INCONCLUSIVE. Nothing here authorizes
unplugging per window, in-window writes or live work during the blinded job.
