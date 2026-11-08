# redteam — v5 fan-out handoff

Brief: 2026-11-08. Branch: `align/2026-11-08-v5-redteam`.
**LOCAL_ONLY; synthetic verification; no registration or hardware claim.**

## Built and committed

- `32e6d518f`: two-parent merge of adversary kit `67b4def8dccefb1242504ceb663ea75d396c1eb7`.
  The merge preview exposed unrelated mainline/Block-5 conflicts and coordination
  changes. Used the lane tree as the merge baseline and imported exactly the
  kit's 27 files (the 26-file implementation plus its report). No unrelated
  mainline snapshot was imported. **This is a scoped payload merge**; do not
  treat its ancestry as evidence that all kit-branch mainline changes were
  adopted. Base lane: `d600baba029f70592bb8e792098338e4cd6811d3`.
- `5b4087bdd58a58cd5d8bbca1eb4a82b09b7de80b`: hashed A0–A13 instructions,
  runtime-external child controls, exact work receipts, DC arithmetic and
  private sham/dose joins, seed/blinding manifests, and a pre-D freeze binding
  the candidate set, objective and development budget. Best-response selection
  verifies the external freeze pin and rejects held-out feedback and seed reuse.
- This report is the following documentation commit. Nothing was pushed.

New/changed feature files: `configs/align/squeeze/redteam/variants.json`;
`joulewise/align/squeeze/{external,redteam,control,harness}.py`;
`tests/align/{test_external_compute,test_external_native,test_redteam_protocol}.py`;
`docs/align/squeeze/REDTEAM-V5.md`; this report. The first merge additionally
contains the original kit files unchanged except the two harness/control files
subsequently extended by the feature commit.

The side generator and uint64 tool workload run in child processes outside
the visible runtime's usage accounting. The generic runner retains identical
visible results/counts and keeps private truth out of all three legacy monitor
views. Tool controls add no agent-visible tools. Shams prepare the same side
decoder but perform zero forwards; failed, partial or timed-out work cannot
certify the requested dose. The tests verify child cleanup and active sampling.

Joules and tokens are deliberately separate: exact emitted IDs/forward counts
and CPU units are ground truth; exact rational DC arithmetic is checked only
on invented samples. Physical hidden-work joules are **not exactly knowable**
from token counts. Matched-sham differences carry additive measurement bounds;
`hidden_energy_j` remains null. This is an explicit limitation of the brief's
"exact joule accounting" wording, not a synthetic claim of measured energy.

## Checks

Initial new-module checks failed with `ModuleNotFoundError` before implementation.
Subsequent tests caught an invalid sham fixture context cap and a synthetic
monitor returning a float instead of `MonitorVerdict`; both fixtures were fixed.
The final assertion also requires no runner flags, preventing monitor errors
from looking like successful privacy checks.

Each command ran in its own process, sequentially:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_redteam_protocol` | 7 passed |
| `python3.13 -B -m unittest tests.align.test_external_compute` | 10 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_config` | 8 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_control` | 8 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_harness` | 7 passed |
| `python3.13 -B -m unittest tests.align.test_external_native` | 1 skipped: MLX unavailable |
| `python3.13 -B -m unittest tests.align.test_squeeze_native` | 1 skipped: MLX unavailable |
| `python3.13 -B -m joulewise.align.squeeze validate --kit configs/align/squeeze` | 13 imported configs/hash bindings validated |
| In-memory `compile(...)` of the seven squeeze sources and three new tests | passed; no bytecode artifacts |
| `git diff --check` / staged equivalent | passed |
| Diff of the four prohibited coordination paths against base `d600baba0` | unchanged |

**40 synthetic tests passed, 2 native tests skipped.** Test execution was far
below the 20-minute cap. No full suite, analysis pipeline, real model, weights
download, network request, hardware capture, host-setting change or access to
sealed measurement paths occurred. All named source refs were available locally;
the no-network rule superseded the fetch instruction. No sub-agent, external
consult or independent review was run; lead review is still owed. Python 3.11
was not exercised here; implementation uses only stdlib APIs available in 3.11.

## Assumptions and open lead work

Applied the brief's KM003C placement/DC authority, amended D-139 A1, off-box
frontier primary monitor, pre-registration transcript-scoring prohibition,
m >= 39 per pair plus held-out T1–T3, maximum-rank channel thresholds, unchanged
v4 configuration, and attempt-denominator primary estimand. Strict all-cell
survival is descriptive. Reviewer2 §3.6 owns A0–A13; the older squeeze-design
A1–A5/P1–P9 names are a different taxonomy.

1. Review the scoped merge and feature diff independently, then require the
   verified freeze in the **v5** admission path. The Apple arm path is unchanged;
   the generic runner hook alone is not production integration or arm authority.
2. Supply the admitted model/factory identity, full configuration/code/policy
   hashes, private window/seed allocation, PC doses and quantitative H50
   predictions. Freeze catalog/seed/search policy before D, then select only
   among those candidates on development feedback before T1. Hashes need a
   lead-controlled external pin/time record; synthetic timestamps are no proof.
3. Decide the production search budget. The current validator reserves the
   ten existing development indices per pair, with 1–10 distinct probes per
   candidate. The earlier draft's 24-probe proposal needs prospective extra
   indices and an explicit extension. Monitor-only best response needs its own
   registered policy; this selection implementation covers the joint objective.
4. Coordinate A1/A5/A12 reported-view transforms and A8 aggregation with their
   owning lanes. A2's 256-token instruction target is not an enforced cap.
   A10's oracle, A11's privileged host changes and A13's battery actuator are
   unavailable; gates/holds, outside-member work, batching and trickling are
   unimplemented. No all-family robustness claim follows from the catalog.
5. On an MLX/Metal-capable machine, run the two native commands above using
   their tiny synthetic models. Later, in a separately authorized native
   session, qualify the actual decoder/cache, memory/thermal/deadman budget,
   visible-trajectory invariance, live KM003C/battery/rail accounting and custody.
   All physical claims and production-model behavior remain **PROVISIONAL**.

No coordination state was edited or kernel task registered. The next exact
step is the lead's independent review of `32e6d518f` and `5b4087bdd`, followed
by the native toy gates and v5 admission/freeze wiring under the owning lane.
