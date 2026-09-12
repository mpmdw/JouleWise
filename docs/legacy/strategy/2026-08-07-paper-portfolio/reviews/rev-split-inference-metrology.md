# Counter-review: "From One Boundary to Two: Fail-Closed Energy Metrology for Split LLM Inference"

**Reviewer:** Opus 5, adversarial lens (contract + feasibility). **Charge:** kill it.

## Verdict

**WEAK** — and the headline version (split-vs-monolithic energy winner, wall-meter dependent) is a **KILL**.
The proposal is the most honest of the ambitious directions and the only one that serves the original
split axis, but it (i) proposes a joint error budget whose dominant term is unmeasured and probably an
order of magnitude larger than every effect it wants to claim, (ii) depends on hardware the project does
not own and a decision (D-092) that forbids assuming it, (iii) requires a runtime stack for which no
adapter, no artifact lineage, and no calibration exist — which is why it quietly reuses *none* of the
D-117 data while claiming it reuses all of it, and (iv) budgets three nights for building a second
instrument that took four months and nine adversarial rounds the first time. There is a genuine, small,
fundable paper inside it. It is not this one.

## Scores (1-10)

| Axis | Score | One-line |
|---|---|---|
| novelty | **4** | Split case study is derivative *and* operationally irrelevant as configured; the cross-boundary budget idea is real but underdeveloped. |
| feasibility | **2** | Two hardware gates never closed, no llama.cpp adapter, no cross-device fiducial exists, meter not owned, laptop AC boundary is battery-buffered. |
| mvp_leverage | **3** | High method reuse (§§3-5), near-zero data reuse — by its own admission. |
| venue_fit | **4** | ICPE full track will reject one unsizable replay pairing; WIP/workshop plausible for the metrology remnant only. |
| original_goals | **9** | This *is* the split axis, honestly scoped, honestly silent on spec-decode/MTP/MoE/KDA. Real credit here. |

## Fatal flaws

**F1 — The joint error budget is not constructible, and the proposal's own arithmetic understates it by
~10x.** The Mac term is known: ~1 J per phase member, 30 ms edge x 33 W (`docs/paper/draft-v1.md:84`).
The GPU term is *unknown by the project's own admission*: `docs/JouleWise_Hardening_Proposal.md:453`
lists "nvidia-smi cadence and averaging characterization" as an unexecuted Phase-7 promotion item, and
`joulewise/adapters/nvidia_smi.py:401-402` computes `interval_ms = 1000/power_hz` — i.e. the harness
*assumes the requested poll rate is the instrument cadence*. That is precisely the class of assumption
D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
internal update period is not the poll period; at a 350 W board, a 100 ms edge is ~35 J and a 1 s edge is
~350 J. Four stages x two edges. Against effects the proposal itself sizes at 10-200 J, **the budget is
plausibly larger than every claimable quantity in the paper.** The proposal spots this ("a 100 ms
uncertain edge on a high-power PC can be tens of joules") and then does not act on it: no composite bar
is stated, S2/S3 are unchanged, and contribution 2 still promises transfer floors. A referee reads that
as knowing the study is unsizable and submitting anyway.

**F1b — There is no cross-device fiducial, so the method's core does not transport.** The project's
distinguishing move is an *in-window physical* pulse-train fiducial (`joulewise/powermetrics_fiducial.py`,
`calibration_bracketing.py`). It is intrinsically within-machine: you cannot inject a Mac power pulse and
observe it on a 3080 Ti. The proposal substitutes an ordinary software clock bound ("both clocks produce a
prospective bound smaller than 25% of the shortest claimed interval") while retaining D-078's rhetoric of
calibration. The only shared physical channel that could bracket both clocks is the wall meter — borrowed,
single, 100 ms-cadenced. **This is the deepest flaw: the paper inherits the vocabulary of the calibrated
instrument without its mechanism.**

**F2 — Both endpoint boundaries structurally exclude the quantity the paper is about, and the repo already
ruled on it.** D-049 (`docs/decision_log.md:2673`): on nvidia-smi ends, board power excludes host
CPU/NIC/DRAM, so "transfer energy measured at a discrete-GPU end is near-zero by construction." D-018:
powermetrics = cpu+gpu+ane, an SoC subsystem proxy excluding display/storage/PSU. An M3 Max MacBook Pro
has no Ethernet port — the 1GbE/2.5GbE link runs through a Thunderbolt/USB-C adapter drawing outside the
SoC rails. So sender NIC energy is outside the Mac boundary and receiver host/NIC energy is outside the
GPU boundary: **transfer energy, the load-bearing new quantity, is unmeasurable at both endpoints.**
D-049 already picked the remedy (wall meter, or explicit board-only lower bounds). The proposal takes the
wall meter, which lands it in F3.

**F3 — The wall-meter plan is internally contradictory and physically unsound for a laptop.**
(i) *Contradiction:* one meter on a shared strip cannot mint "sender, receiver, combined-wall and
composite" floors (contribution 2). Sender and receiver wall floors require two meters. Unrepaired.
(ii) *Battery buffer:* a MacBook Pro at the AC boundary is charge-buffered; macOS charges
opportunistically, so second-scale AC draw is decoupled from SoC power. MLPerf Power's battery rule is
quoted in this project's own draft (`draft-v1.md:26,182`) — and the proposal violates it without mention.
First-page referee kill. (iii) *Baseline swamping:* the "unused reference node remains powered and idle"
adds ~60-100 W of PSU-inclusive idle to the combined boundary, with nonlinear efficiency in load, against
10-200 J effects; the WT310E's 0.1% rdg + 0.1% rng at a ~400 W range is ~0.4 W of systematic error, i.e.
~12 J over a 30 s composite window — comparable to the effect. The proposal says the meter spec "must
enter the floor calculation" and never does the arithmetic. (iv) *Standing decision:* D-092 ratified the
meter but recorded **no hardware, C8 conditional, "not assumed by any campaign plan."** The proposal's
headline assumes it.

**F4 — Existing-material compliance is rhetorical.** MLX prompt-cache state is not portable to CUDA;
D-015's hard rule forces same-runtime both ends, which means llama.cpp/GGUF. The repo has
`adapters/{mlx_runtime,vllm_runtime,mock_*}.py` and **no llama.cpp adapter**. So the paper needs a new
runtime adapter, a new artifact/quantization lineage (not the pinned MLX 4-bit Qwen2.5 rev `8b40312`),
re-run determinism/output-identity machinery, and — because floors are stack-specific — **a full floor
re-mint under a runtime that has never been calibrated.** The proposal concedes it in its last section
("D-117 MLX results are *not* direct monolithic comparators for a llama.cpp split stack"), which
contradicts its own claim two paragraphs earlier that it "reuses all three D-117 datasets as the validated
one-boundary baseline." Under Ed's binding constraint this proposal reuses §§3-5 prose and **zero data**.
That is permissible only if stated plainly; it states the opposite.

**F5 — Schedule is off by a large factor, on the project's own record.** Three 2-4 h windows + a pilot +
a contingency, to stand up a *second, harder* instrument. Cost of the first: P0 instrument repair =
nine adversarial confirmation rounds and PR #79; D-078 through D-117 = ~4 months; and `CLAIMS_STATUS.md`
§1 today reads **"VALID — NONE at this checkpoint."** Zero citable numbers exist. Meanwhile the
prerequisites are worse than the proposal's list: `TASK_QUEUE.md` E6/P1-006 is still `READY
[ED-EXTERNAL]` and A23/P2-005 records the NVIDIA lane as fixture-first with "protocol pins remain
provisional until the external live-promotion rows execute" — **the 3080 Ti has never produced a live
bundle and its telemetry access has never been confirmed.** P1-004 (measured topology) is open; 2.5GbE is
aspirational in the plan, not evidenced as owned. Add schema v0.2, composite bundles, two importers,
cross-clock propagation, portability spikes, D-048 pre-registered predictions, D-049 per-cell boundary
labels — on top of the three *blockers* the D-117 memo already carries for the existing windows (F1
bracket-session capability, F2 pinset v2, F3 successor-artifact path). Honest re-cost: 8-12 windows and a
semester, not three nights.

**F6 — Novelty is thin in both directions.** As systems: the repo's own `related_work_draft.md` already
surveys Revisiting Disaggregation Energy (EuroMLSys'26, 2xA100 PCIe, higher energy), DualScale (16xH100,
IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
scp a 56-448 MiB cache, decode on a consumer GPU over 1GbE — is not disaggregation as the field means it;
it is a deployment nobody proposes, whose crossover is dominated by link bandwidth, answering a question
whose answer is both predictable and uninteresting. As metrology: Silicon Showdown already demonstrated
the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
repairing it needs the bridge hardware that isn't owned.

*Credited, in fairness:* the kill-criteria section is the best-shaped in the portfolio; the "~5 J is only
a Mac phase-design reference" paragraph is exactly the right instinct; the honest statement that live
split is stretch and that portability failure caps the work at synthetic metrology is correct discipline.
The proposal is not naive — it is under-costed and one step short of following its own best insight.

## Three strengthening moves (if kept)

1. **Invert the paper: make the refusal the result, and drop the meter.** Kill the split-vs-monolithic
   winner claim and contribution 4. Ship a *boundary-composability* paper: pre-register the composite
   budget arithmetic before any collection; add the one cheap missing empirical input — a **GPU-side
   cadence/averaging characterization** (pulse-train step-load on the 3080 Ti, no LLM, no Mac, closes
   hardening Phase-7 item 4 and costs one non-quiet evening on owned hardware); then publish "the
   two-boundary composite budget is ~N J against candidate effects of 10-200 J, therefore the split
   comparison is REFUSED, and here is the exact operating domain where it would resolve (payload >= X GiB,
   link <= Y Gb/s, board TDP <= Z W)." Falsifiable, entirely owned-hardware, and it makes the fail-closed
   machinery do the most interesting work in the paper. This is the version that fits ICPE WIP.
2. **Build a shared physical fiducial or declare its impossibility as the finding.** Replace the NTP-shaped
   clock criterion with a cross-device *power-step* fiducial: a pre-registered train of fixed-size
   transfers whose starts/stops appear as power steps on both endpoints, with the cross-clock bound derived
   from observed step alignment rather than from a software clock. This is the only construction that
   preserves continuity with D-078's actual mechanism. If it cannot produce a bound under 25% of the
   shortest claimed interval, that failure is the headline — and a better one than a crossover plot.
3. **Fix the runtime accounting and the two contradictions, then re-cost in the open.** State plainly that
   the split stack is llama.cpp/GGUF and therefore a *new instrument* needing its own calibration regime
   and floor mints, with the honest 8-12-window budget attached — or drop the real-split arm to future work
   under D-092/C8's existing conditional framing. Separately: delete the sender/receiver wall floors from
   contribution 2 (one meter cannot mint them), and add battery-charge neutralization with verified steady
   state as a hard admission gate before any wall-boundary claim, per the MLPerf rule the draft already
   cites.

**Disposition recommendation:** do not fund as a second paper. Fund move 1 as a ~1-evening desk+bench
probe; if the GPU cadence characterization comes back at 100 ms or better *and* a cross-device power-step
bound lands under the 25% criterion, revisit. Otherwise this direction's correct home is a quantified
future-work section in the MVP paper — which is exactly where D-092 already put it.
