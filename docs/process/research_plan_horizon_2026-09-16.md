# Horizon extension — USB-C meter, adopted practices, heterogeneous hardware (day 24 onward)

**Date:** 2026-09-16. **Author:** Fable writer seat, reconciling the Fable
horizon draft and the Astra design consult under the magistrate's eight
resolutions. **Continues:** [`research_plan_2026-09-16.md`](research_plan_2026-09-16.md)
(the base plan); its Terms, window arithmetic and table columns apply
unchanged. **Inputs:** the literature seat (record 21,
`docs/process_traces/2026-09-15-interactive-b0ae8462/21-rq-literature-and-best-practices-fable.md`),
lane WALL-METER-GAIN-01 (task-queue row A214; acceptance at
`docs/process/state_kernel.json` `/tasks/WALL-METER-GAIN-01/acceptance`),
decision D-018 (`docs/decision_log.md`, the boundary-id list), the checkout
facts named in §3a, and the web pages in §Sources. Anything no seat fetched
is **NEEDS-WEB**; anything no seat measured is **ASSUMED**; neither mark is
laundered by appearing in a table.

## What this document is and is not

The grade is secured by Paper A (merged) and Paper B (data-complete on day 3
of the base plan). **Nothing in this horizon is required for it.** Ed's stated
objective past Paper B is CV value: a venue or workshop paper with the advisor
as co-author, an artifact badge, and a reproducible tool people outside Apple
can cite. Every item is ranked by **CV value per Ed-hour** — an *Ed-hour* is
one hour of Ed's physical presence (plugging hardware, sitting at a friend's
machine, provisioning an account) or the dollars he pays — never by science
in the abstract. Seats do the unattended work; Ed's time is the scarce input.
Nothing here starts until the ruling box lands, except the read-only rig
inventory (§3a), which is authorized now.

## Terms (in addition to the base plan's)

**USB-C DC input** is the direct-current power on the cable between the
adapter and the laptop: everything the laptop draws (SoC, memory, backlight,
SSD, fans, charger circuit) after the adapter has converted from AC; the
adapter's own loss is upstream and invisible. **Wall power** (D-018's
`wall_meter`) is AC from the socket — a different boundary, never used for
this meter. A **boundary id** is the label every JouleWise energy number
carries naming the physical envelope it covers. A **meter mapping** is a
fitted relationship predicting USB-C DC input energy from `powermetrics`
counter energy for one laptop, one power configuration and a stated workload
range: slope, offset, interval, and **held-out error** — the largest miss
when the fit predicts blocks it was not fitted on. It is *not* a counter gain:
the slope mixes counter error with loads the counter does not cover, cable
and charger loss, and battery flow, and no arithmetic on one cable reading
separates them. **Battery participation** is the battery charging (adds to
the cable reading) or discharging (hides SoC draw) during a measurement.
**Board power** is what NVIDIA's management library (NVML) reports for a
card: the card, its circuitry and its memory, nothing on the host [26].
**Three rates** govern any counter: the *poll rate* (how often software
asks), the *update period* (how often the value changes; a sample between
updates is a **stale read**), and the *averaging window* (how long the sensor
averages internally). **Request total** is one whole request's energy,
prompt plus generation, unsplit. A **service boundary** is a phase edge seen
from the client (first streamed chunk arrives); a **device boundary** is the
edge at which the GPU finished the prompt work, from a device completion
event; only the second supports a phase claim. **Matched recipe** means the
same checkpoint at the same numerical representation on both platforms
(BF16 = 16-bit floating point); two "4-bit" artifacts from different
toolchains are not matched unless grouping, scales, zero points and excluded
tensors agree. **Offload** places weights or work in host memory and changes
both experiment and boundary, so a model that fits only with offload does
not fit. **MIG** slices one GPU into shared partitions; board power is then
not attributable. **Noisy neighbour** is another tenant's workload on the
same cloud host, invisible to our process list. **Placement** is which device
runs a request: **whole-request** gives one device the entire request;
**split-request** runs the prompt on one device, moves the key-value cache
(one key and one value vector per layer per token) to another and generates
there; **transfer cost** is that move's energy and time. **Ranging run** is a
preliminary pass of the full workload so the meter's range is fixed before
the counted runs (MLPerf Power [1]). **Artifact badge** is the ACM label for
a paper whose code and data reviewers could obtain (*Available*) and run
(*Functional*).

## Assumptions

- The horizon starts on day 24 (Paper D full set data-complete). The meter
  desk arm does not wait: it rides the base plan's Phase 0 desk day (A214
  clause (d)); any meter window completed earlier is subtracted from H1.
- Base-plan arithmetic: window ≈2.5 h wall, ≈2.25 h capture; 4–5 windows/day
  on the Mac; a refusal ≈20 min; 20% of every phase is reserve; every new
  model×phase cell on every platform needs its own floor window first; a
  reserve window is a newly authorized plan, never a silent retry.
- The POWER-Z KM003C arrives ≈17:00 PDT Wednesday 2026-09-17 (ASSUMED from
  the brief). Plugging it in is 15 minutes of Ed's hands.
- Ed owns the RTX 3080 Ti rig (ASSUMED current authority; the older hardware
  checklist called it borrowed). OS, driver and telemetry support are unknown
  until the §3a inventory runs.
- NVIDIA devices run their own copy of the unattended chain once ported;
  porting is seat work. The node-worker contract
  (`docs/contracts/node_worker_protocol.md`) is PROVISIONAL pending live
  hardware validation, so the port is a qualification, not a reuse.
- Byte sizes are weights only: parameters × bytes per parameter (BF16 2,
  INT8 1, 4-bit 0.5 before metadata), decimal GB, unless a fetched file size
  is cited. Official counts: Qwen3-8B 8.2 B, Qwen3-14B 14.8 B, Qwen3-30B-A3B
  30.5 B total / 3.3 B active [33–35]. The cache is sized in §3a.

## Ruling needed from the magistrate (blocks Leg 1 implementation only)

> **1. Reword A214 clause (b).** The registered acceptance says "the gain
> factor between the software counter and the meter, with its uncertainty,
> becomes a stated calibration of the total-energy scale." Proposed: "a
> workload-conditioned mapping from `powermetrics` counter energy to USB-C DC
> input energy for this laptop and power configuration — slope, offset,
> interval and held-out error — becomes the stated relationship between Paper
> B's counter scale and a physically measured input; it is not a counter
> gain, and no phase energy is multiplied by it." Clauses (a), (c), (d) stand.
>
> **2. A new boundary id.** D-018 defines `wall_meter: AC wall power (full
> system)`; the KM003C measures DC after the adapter. Proposed:
> `usbc_dc_input` — "DC power on the USB-C cable into the laptop; adapter loss
> excluded; battery flow logged and bounded per interval." Every meter number
> carries it.
>
> **3. Battery admission budgets** (proposed, not yet repository thresholds):
> an interval enters the mapping only if the upper bound on battery
> participation, including unobserved sub-intervals, is below **1% of the
> interval's DC input energy**, and, for any contrast, below **20% of the
> smallest energy difference the contrast intends to resolve**. A missing
> battery-sensor uncertainty means "unbounded", not zero. The 50 mA
> instantaneous screen (Leg 1) is the coarse trip; these budgets are the gate.

## Ranking by CV value per Ed-hour

| rank | item | Ed-hours | dollars | what it adds to the CV |
|---|---|---|---|---|
| 1 | USB-C DC mapping (Leg 1) | 0.25 + ≈1 (cables, logging host, battery hold) | 0 (meter bought) | closes the one row where Paper B is weaker than SPEC/MLPerf [1,2]; Paper B becomes venue-grade |
| 2 | adopted practices, desk items (Leg 2: warm-up rule, fixed-n rationale, thermal column) | 0 | 0 | three reviewer questions closed in Paper B's protocol section |
| 3 | adopted practices, diagnostic windows (Leg 2: counter granularity, sampler overhead) | 0 | 0 | the instrument section nobody has written for Apple silicon; feeds Paper F |
| 4 | artifact package + Zenodo DOI | 0.5 | 0 | ACM Available + Functional badges; a citable tool |
| 5 | whole-request placement on the owned 3080 Ti + matched 1.7B BF16 Apple cells (Leg 3a) | 4–8 once, then 0.5–1 per batch | ≈$3.40 per 25 h electricity (0.45 kW × 25 h × $0.30/kWh, ASSUMED ceiling) | Paper E's core on hardware Ed controls: a second vendor and a second instrument class |
| 6 | rented 80 GB card: matched 8B BF16, scaling roster, KV-cache week (Leg 3a/3b) | 2–4 once | $115–150 core; $263–343 full (§5) | Paper E's top class and the cells no owned card can hold |
| 7 | split-request transfer rider (Leg 3c) | 1 | ≈$40 adapter + cable (ASSUMED) | one figure in Paper E, with a stated attribution limit |
| 8 | friend's RTX 5080 sessions | 3–6 setup + 1–2 of the friend, then 2–4 per session | 0 | one more device-class point, Windows-conditioned; optional |
| 9 | multi-GPU interconnect on cloud (§4) | 0.5 | ≈$80/window [21] | weakest attribution in the program; not scheduled |

## Leg 1 — the USB-C meter (rows H1.1–H1.5)

**Forcing problem.** Apple documents its energy figures as estimates; record
21 §2 row 1 scores JouleWise *Not done* on the calibrated-analyzer practice
SPEC [2] and MLPerf Power [1] require. Until a physical meter has been read
against `powermetrics` under this load, every joule in Papers B–D is in
Apple's units. What the meter can supply is narrower than the registered lane
says (hence the ruling box): a mapping with a held-out error, at a named
boundary — not AC, not sub-percent, not phase-resolving, not a calibration
certificate, not a multiplier on any phase energy.

**What the meter physically measures.** A pass-through: adapter into one
end, the laptop's cable into the other, voltage and current logged on the
wire between. Its reading is USB-C DC input, minus nothing. The manufacturer
documents application logging at 1, 10, 50 or 1,000 samples/s with CSV
export, separate from the display refresh [32]; the retail accuracy,
converter and range figures (1%, 20-bit, 50 V / 6 A) are **NEEDS-WEB** — the
product page and manual refused the fetch (HTTP 403), and the one page that
loaded [31] confirms only HID over USB-C with no driver and `.csv`/`.log`
export. The delivered unit's specification sheet is recorded on arrival;
display resolution is never mistaken for accuracy, and no traceable
calibration is claimed without a calibration record.

**What the meter yields (the claim).** For each block *i* — ≥60 s of complete
requests, recovery tail included by a rule fixed before collection — fit

    E_DC,i = a · T_i + b · E_sw,i + ε_i

with `E_DC` the meter energy (J), `E_sw` the `powermetrics` package-plus-DRAM
energy for the same block (J), `T` the block duration (s), `a` an offset in
watts (loads outside the counter), `b` a dimensionless slope, `ε` the
residual. Fitting accounts for uncertainty on both axes; meter specification
error, timing, battery uncertainty and between-window variation are
propagated, and the meter's shared specification error does not shrink with
more samples. Reported: `b` and `a` with intervals; a slope per load family if
one common slope fails held-out; the largest held-out prediction error; raw
DC energy, counter energy, battery diagnostics and the admitted load range.
Jay et al. [5] found the software-versus-meter gap is a load-dependent slope,
which is why a ladder is fitted rather than one ratio read; their slope is
not a correction for this Mac.

**Worked example (illustrative, not data).** Two 120 s blocks: idle reads
720 J on the meter (6.0 W) against 144 J of package-plus-DRAM (1.2 W); the 8B
decode cell reads 4,560 J (38.0 W) against 3,780 J (31.5 W). Then
`b = (4560 − 720) / (3780 − 144) = 3840 / 3636 ≈ 1.056` and
`a = (720 − 1.056 × 144) / 120 ≈ 4.73 W` (backlight, SSD, charger, memory
outside the counter). A load-dependent gap shows as `b` whose interval
excludes 1 or as curvature across rungs; a constant offset as `a` alone. The
paper may print "on this laptop, over this load range, USB-C DC input energy
is predicted from the counter to within the held-out error"; it may not print
"the counter under-reports SoC energy by 5.6%".

**Battery participation (extends A214 clause (a)).** Battery current is
positive into the battery, read at 1 Hz from the battery registry (`ioreg -rn
AppleSmartBattery`, `InstantAmperage` and `Voltage`, **ASSUMED** field names;
sign, units, update period and missing-sample behaviour are established in
H1.1 by watching one charge and one short discharge). Two integrals per
interval: the signed battery-terminal energy `E_bat = ∫ V_bat · I_bat dt`
(positive = energy that entered the battery, subtracted; negative = discharge
that supplemented the adapter, added back) and the unsigned
`∫ |V_bat · I_bat| dt`, because charge and discharge can cancel in the signed
total while the battery buffered a great deal. Admission is by the
ruling-box budgets. **Worked numbers:** at 38 W a 120 s block holds 4,560 J,
so the 1% budget is 45.6 J = 0.38 W average ≈ 30 mA at 12.5 V. The **50 mA
instantaneous screen** (≈0.6 W) refuses any 1 Hz interval above it on the fly,
so a charge event is dropped the moment it starts; the block is then admitted
only if its unsigned integral is under budget. Holding at 100% needs an
adapter-dominated state: optimized charging off (**NEEDS-WEB** for the
setting on this build; no new charge-control utility during the campaign),
≥30 min settle after any cable change, and the 140 W adapter (ASSUMED
rating) verified to out-rate the laptop's peak (<100 W ASSUMED from `_v4`
traces; H1.1 verifies). A displayed "100%" is not evidence of taper. If
participation cannot be bounded, the fallback is a separately declared
experiment measuring *work plus return to the initial battery state*, which
characterizes an operational cycle and calibrates nothing per request.

**Time anchoring (clause (c)).** The 59 commanded one-second GPU pulses show
on the meter as steps of tens of watts, so the same edge fitting the software
side uses places the meter's samples on the wall clock without trusting the
meter's timestamps. Added: 5, 10 and 20 s GPU plateaus separated by unequal
quiet gaps, commanded on the Mac's monotonic clock (one that never jumps with
civil-time corrections), before and after every window; the clock mapping
fits offset and rate; a plateau's apparent lag is clock error *plus*
electrical response delay, so every plausible alignment is kept and interval
energy recomputed at the extremes. The logger is a second host first; if
H1.1 shows the logger's own draw on the measured Mac is below the idle floor,
the host decision is recorded and it may move. The original export is
archived, never a resample.

**Load ladder (the mechanics).** Rungs: idle; the 1.7B decode cell; the 8B
decode cell; the 30B-A3B prefill cell; the GPU pulse at three duty levels —
≥10 repeats per rung in ABBA order, ≥60 s per block. Two rungs, named before
collection (AP-1), are held out and predicted; H1.4 repeats the held-out set
on another day with fresh alignment and battery qualification. The meter
logs at 10 samples/s: a 2.5 h window is 2.5 × 3600 × 10 = 90,000 records, so
the logger is configured above that and wraparound proven absent. A ranging
run rides H1.1 (relevant only if the unit has selectable ranges, **NEEDS-WEB**).

| window | question id(s) | held constant | claim it feeds | paper section | prerequisite / NEEDS-WEB |
|---|---|---|---|---|---|
| Phase 0 desk day (base plan) | WALL-METER-GAIN-01 desk arm, clauses (a), (c), (d) | pulse workload + G2-a set, battery 100% | logger host decided; alignment + battery-integral tests landed (must-die mutants) | B: instrument | ruling box landed; meter plugged in (Ed, 15 min, after 09-17 17:00); HID logger (desk); logging rate [32] |
| H1.1 (day 24) | battery sign/taper check, logger-load re-check, plateau alignment, ranging run | as above | battery telemetry qualified; meter range fixed | B: instrument | desk arm PASS |
| H1.2–H1.3 | ladder: 7 rungs × ≥10 repeats, ABBA, 2 rungs held out | rungs pinned, battery 100% | `b`, `a` with intervals; held-out error | B: instrument | H1.1; adapter headroom verified |
| H1.4 | held-out rungs repeated on a different day | as H1.2 | day-to-day reuse of the mapping | B: instrument | fresh alignment + battery qualification |
| H1.5 | reserve | | | | |

**What a refusal costs here:** a battery excursion refuses the interval; a
failed hold or an over-budget block refuses the window (≈20 min plus one
slot). A mapping that fails held-out is published as workload-specific
slopes, not hidden.

## Leg 2 — literature practices not yet adopted

Already in the base plan: the IOReport cross-check arm and the
generation-length-1 arm (Phase 0 windows 0.5–0.6). The rest of record 21 §2's
*Not done / Partly / Differently* rows, each priced.

| practice (record 21 §2) | mechanism to add | cost | reviewer question it closes | lands in |
|---|---|---|---|---|
| counter update period / stale reads (Dauner [9], Yang [10] analogue) | run `powermetrics` at 10, 20, 50, 100, 200, 500 ms against the pulse train; count consecutive identical records (stale reads) per interval; read the IOReport cumulative counters at 1 kHz and record the step period at which they change; the finding is the shortest interval at which records are independent | 1 `DIAGNOSTIC_NO_PACK` window + 0.5 desk-day | "do your 100 ms averages alias a slower counter?" | B: instrument; F |
| sampler overhead at 100 ms (NAACL 2025, Cao [6]) | ABBA of the same request set with the sampler at 100 ms vs 1000 ms vs off; report tokens/s inflation and the sampler process's own CPU time; energy compared 100 ms vs 1000 ms (off has no energy) | 1 `DIAGNOSTIC_NO_PACK` window | "does the instrument change what it measures?" — NAACL found 15–50% time inflation for trackers | B: instrument; F |
| die temperature + ambient (SPEC [2], Watt Counts [43], Illusion [11]) | Apple silicon exposes no die temperature through `powermetrics`: the `smc` sampler is "on supported platforms" only [24] and is reported refused on Apple silicon (**NEEDS-WEB** on this build); `--samplers thermal` gives the thermal-pressure level, an instantaneous end-of-record value [24], already gated on. Add it as a per-record column; HID sensor-bus readers (`smctemp`-class) are **NEEDS-WEB**; ambient needs a sensor we do not own (USB logger ≈$20, ASSUMED) | 0.5 desk-day; 0 windows | "what was the chip's temperature and the room's?" — pressure level logged, temperature not readable, ambient not instrumented, stated as a limitation | B: limitations |
| explicit inference warm-up rule (Cruz; Illusion 3 iterations) | the draft states warm-ups only for calibration pulses (three, trimmed, §A.3.4). Write the inference rule the pack enforces or does not: proposed — the first member per model per window is a warm-up, discarded before any statistic; verify against the pack's member list and print the count | 0.25 desk-day | "was the first request cold?" | B: protocol |
| fixed pre-registered n vs adaptive stopping (Wilkins) | a paragraph: adaptive stopping makes n a function of the data, so the resolution bound becomes data-dependent and optional stopping can chase a result; pre-registered n with the floor gives a fixed decision rule whose cost is that a sub-floor contrast prints `not resolvable` instead of being rescued by more trials; the one-way prior ratchet is the only permitted growth | 0.25 desk-day | "why not repeat until the interval closes?" | B: protocol |
| MLPerf-style ranging run before fixed ranges [1] | rides H1.1 (Leg 1) | 0 extra | "was the meter's range fixed before the counted runs?" | B: instrument |
| Zenodo DOI + artifact README with time estimates (ACM badging; ICPE AE) | package the frozen packs, evidence bundles and reduction code; README lists each reproduction step with its measured wall time (e.g. "re-derive `b_fiducial_s`: 4 min on an M-series laptop"); mint a Zenodo DOI; state that FLOOR-BIND-01 limits third-party re-derivation (draft §9) and say so in the README — new hardware does not repair evidence provenance | 1–2 desk-days; Ed: 0.5 h | *Available* + *Functional* badges; *Results Validated* not claimable at submission | B: artifact appendix; E, F reuse the package |

Two windows and ≈4 desk-days in total; both windows sit in week H1 (§5).

## Leg 3 — heterogeneous hardware (Ed's original interest)

**Forcing problem.** Ed's original research interest was heterogeneous
hardware: the same request served by different device classes. The metrology
built for the Mac makes that question answerable properly for the first time
— a floor and a refusal per platform rather than a leaderboard — and the
cross-vendor replication of the phase-energy method is the *method-transfer
step inside* the placement study. The order is: qualify the instrument on
each platform, mint request-total floors, place whole requests, and only
then ask whether phases resolve at all.

### 3a — Whole-request placement across device classes (the core)

Each device serves whole requests. For one model, one recipe and one pinned
prompt population, every reachable device class gets its own floor window and
the same contrast design, giving per-device energy per request against
prompt length. The claim is an **energy-first placement rule**: which device
class should serve which model size and prompt length for the least energy
per request, above each platform's floor, printing `not resolvable` where the
floors forbid it — the energy analogue of Splitwise's phase-splitting
argument [14] across device classes. Numbers at different boundaries are
labelled and set side by side, never divided into an "Apple versus NVIDIA
efficiency" ratio: matching model and prompts does not repair a boundary
mismatch, and `usbc_dc_input` versus NVML board power is not like for like
either.

**Device classes Ed can reach.** M3 Max, 128 GB unified memory; Ed's rig with
an RTX 3080 Ti, 12 GB, no NVLink [37]; a friend's Windows rig with an RTX
5080, 16 GB GDDR7, no NVLink [23], occasionally and remotely; a rented single
80 GB card (H100 PCIe $3.29/h, SXM $4.29/h verified [21,38]; a single A100
80 GB at $1.39–3.99/h is a search snippet or a multi-GPU-section price,
**ASSUMED availability**). Jetsons are optional and unverified.

**Primary NVIDIA platform — gated on a read-only inventory (start now).** A
seat with SSH to the rig records, changing nothing: OS and kernel; driver
and CUDA version; `nvidia-smi -q` device identity, PCIe generation and width,
power limits; whether `power.draw.instant` and `power.draw.average` are
supported beside the generic `power.draw` (the 3080 Ti is an Ampere GA102
part, ASSUMED from its family, so its generic call is the one-second average
[26]); whether `nvmlDeviceGetTotalEnergyConsumption` returns a value on this
GeForce card (documented Volta and newer [26,27]; consumer support
**NEEDS-WEB**); and whether any other user or service holds the GPU.
**Decision rule (resolution 2):** if the rig runs Linux and exposes either an
instantaneous power field or the energy counter, the owned 3080 Ti is
primary, the rented 80 GB card secondary, the 5080 optional — near-zero
Ed-hours after one setup evening, complete control, and the port every other
platform reuses. If the rig runs Windows, or only the one-second-averaged
field exists so that even request totals of short requests cannot be
bounded, the rented Linux 80 GB card is primary and the 3080 Ti the
inexpensive secondary check. WSL2 lacks NVML utilization and process queries
[39], so a Linux guest cannot certify a quiet Windows host; vLLM documents
Linux, with WSL as a community route [40].

**What fits where (weights only; the cache is extra).** Per-token cache for
Qwen3-8B at 16-bit is 2 (K and V) × 36 layers × 8 KV heads × 128 head width ×
2 bytes = 147,456 bytes/token [36]; 4,096 tokens = 603,979,776 bytes, 8,192
tokens = 1,207,959,552 bytes per sequence. 4-bit metadata at four bytes per
128 weights adds P/32 bytes (0.256 GB for 8.2 B). The CUDA runtime reserves
≈0.5–2 GB. A nominal 16 GB card is 14.9 GiB.

| model / recipe | bytes | 3080 Ti 12 GB | 5080 16 GB | 80 GB cloud | M3 Max 128 GB |
|---|---|---|---|---|---|
| Qwen3-1.7B BF16 / INT8 / 4-bit | 3.4 / 1.7 / ≈0.9 GB | yes | yes | yes | yes |
| Qwen3-8B BF16 | 16.4 GB | no | **no** (16.4 GB = 15.27 GiB > usable) | yes | yes |
| Qwen3-8B INT8 / 4-bit | 8.2 / ≈4.4 GB | yes (INT8 leaves ≈2.8 GB: ≤8K tokens with runtime) | yes | yes | yes |
| OLMoE-1B-7B (7 B total, 1.3 B active [30]) INT8 / 4-bit | ≈7 / ≈3.9 GB | yes | yes | yes | yes |
| DeepSeek-V2-Lite (16 B total, 2.4 B active) Q4_K_M | 10.5 GB [28] | tight: ≈1 GB left; short prompts only | yes | yes | yes |
| Qwen3-14B 4-bit / BF16 | ≈8.1 / 29.6 GB | 4-bit yes | 4-bit yes | yes | yes |
| Qwen3-30B-A3B Q4_K_M / BF16 | 18.6 / 61.1 GB [29] | no | no | yes / yes (short context at BF16) | yes |
| Qwen3-32B BF16 / 4-bit | 65.6 / ≈18 GB | no | no | yes | yes |
| 70B-class 4-bit | ≈38 GB | no | no | yes | yes |

**Consequence for the matched recipe (resolution 3):** 8B BF16 fits neither
consumer card, so the matched 1.7B/8B BF16 comparison lives on the 80 GB
card; the owned card gives matched 1.7B only. The consumer cards' 8B cells
(INT8, 4-bit) are within-NVIDIA placement points against the 80 GB card at
the same CUDA recipe, which needs no Apple cell at all.

**Instrument on NVIDIA (the second instrument class).** NVML exposes
`nvmlDeviceGetPowerUsage` (board power, milliwatts) and
`nvmlDeviceGetTotalEnergyConsumption` (cumulative millijoules since driver
load) [26,27]. The counter read at the runtime's phase edges is the analogue
of the base plan's IOReport arm; the polled trace at 10 Hz is the analogue of
`powermetrics`. Before any floor is minted on a card the three rates are
characterized: GPU pulses of 50, 100, 250, 500, 1,000 and 5,000 ms with
varied gaps, polled in separate runs at 5, 20, 100 and 1,000 ms, retaining
instantaneous, average and cumulative fields where supported; counted are
stale reads, averaging, response delay, missed pulses and logger overhead.
Dauner's ≈100 ms counter behaviour [9,41] is platform-dependent, not a
specification; Yang's ≈25% runtime coverage at default `nvidia-smi` cadence
[10,42] is a sensor-mechanism problem, not only a slow poll; Watt Counts'
<1% agreement between 10 Hz and 200 Hz [43] is same-instrument consistency,
not physical accuracy. Every read follows a device synchronization or the
edge lands before the work finished [27]. Agreement between integrated power
and the cumulative counter is not an independent calibration; no board-gain
reference exists on any option. Clocks are recorded, not locked.

**Phase boundary on NVIDIA — the honest first result (resolution 5).** The
checkout's worker defines its phase edge as the first received stream chunk
(`joulewise/adapters/node_worker.py:341`, `phase_boundary_method:
first_stream_chunk`) and its adapter polls the generic `power.draw`
(`joulewise/adapters/nvidia_smi.py:40`). The first chunk is a service
boundary: it includes delivery delay and cannot silently become a device
phase edge. Therefore **request totals plus printed phase refusals are Paper
E's first NVIDIA result.** A phase claim needs (i) the device boundary
recorded in the worker — end of prompt work and start of generation by
device completion events, mapped to the host monotonic clock with a bound,
no synchronization wait added to one arm only; (ii) the sensor
characterization above; (iii) a rebuilt pre/post calibration acceptance
whose pulse widths and fit match the NVIDIA response (the Apple 9.724 ms /
10.164835 ms screens are not copied); (iv) a refusal rule counting effective
sensor intervals, not polls: proposed ≥5 characterized sensor intervals per
admitted phase plus a passing edge-uncertainty test — a one-second-averaged
field polled at 10 Hz supplies one observation per second, not ten. Apple
prompt lengths are preserved; if NVIDIA prefill is shorter than the sensor
resolves it prints unresolved, and a longer-prompt experiment is a new
declared experiment, not a replacement. A diagnostic inserted-gap arm (ten
requests with a predeclared 500 ms gap between phases) tests the
pulse-to-inference assumption and stays diagnostic because the gap changes
execution.

**What replaces the quiet-machine census.** On a Linux rig the census ports
directly: process list, `nvidia-smi --query-compute-apps` empty, NTP state,
NVML die temperature (better than the Mac, which exposes none); provisional
screens, frozen after diagnostics rather than copied from the Mac: host CPU
busy <5% of allocated capacity, idle board power within the larger of 3 W or
5% of its reference, start temperature within 3 °C of reference, 30 s of
stable idle before each stage; throttling and power-limit events logged
throughout. On the friend's Windows rig the same gates run from PowerShell
during agreed no-use intervals covering the whole host (remote desktop itself
creates GPU load). On cloud the census sees only our VM; MIG or shared slices
are refused; noisy neighbours are detected, not gated: the base plan's
fixed-workload references (three opening, one midpoint, three closing) give a
repeat spread, and a spread above the cell floor prints `not resolvable`.

**Floors on a hardware counter.** Per model×phase cell: ten repeated
absolute members plus ten identical-condition ABBA blocks (A and B the same
condition) = 10 + 10 × 4 = 50 members, references retained; interval corners
enumerated over all admissible clock positions, sensor-response uncertainty
and sampling gaps (2^10 = 1,024 corners per component at ten units), the
small-sample multiplier applied, each component's drift allowance added, the
maximum taken (draft §4's formulas); five further blocks held out to test
containment; the issued floor published before the contrast; a device
replacement is a new qualification. The two claim gates keep their meaning:
magnitude above floor, direction supported by interval and pre-registered
test; below floor is unresolved, never equivalent.

**Worked placement example (illustrative, not data).** Suppose the 8B INT8
whole-request cell at 2K prompt / 512 output measures 620 J on the M3 Max
(`soc_package`) and 480 J on the 3080 Ti (board), with request floors of 20 J
and 35 J; the 140 J difference exceeds both floors, so the rule prints "serve
8B INT8 at this shape on the 3080 Ti class, boundaries as labelled". If the
1.7B BF16 cell shows 95 J vs 88 J with floors of 6 J and 12 J, the rule
prints `not resolvable` — and that printed refusal is what a metrology
reviewer looks for.

**Window budget (owned rig, request totals):** five floor windows (1.7B BF16
matched, 1.7B INT8, 8B INT8, 8B 4-bit, OLMoE 4-bit; DeepSeek-V2-Lite rides at
short prompts), three placement-grid windows (p ∈ {512, 1K, 2K, 4K} × d ∈
{128, 512}, ABBA against the Mac's matching cells), one diagnostic, two
reserve = 11. On a dedicated rig these run back to back: ≈3 days.

### 3b — Matched cross-vendor recipe and method replication

**What transfers.** The procedure (integrate power over runtime-defined
phases; ABBA; separate magnitude and direction gates; printed refusals)
transfers after the qualification above. No number transfers: the Apple
timing-bound result is a hypothesis to retest, every threshold is
platform-specific, no cell inherits the M3's floor. Paper D's bytes law
transfers as an equation and a held-out test with separate platform
coefficients.

**The matched recipe (any cross-platform comparison).** The same Qwen3-1.7B
and 8B checkpoints in BF16 on both platforms, if both runtimes support it —
which requires **new BF16 Apple cells with their own floors**; the base plan's
4-bit MLX floors do not authorize a new numerical recipe, and "4-bit MLX" is
not "4-bit CUDA". Match prompt token ids, tokenizer, output length, thinking
mode, sampling policy, batch size, cache reuse and warm-up; greedy decoding
does not guarantee identical outputs across kernels, so actual output ids
are preserved and any fixed-token replay is a separately declared workload.
Legitimate comparisons: timing and resolvability of matched requests;
whether a mechanism's direction replicates within each platform's boundary;
whether the same functional form predicts held-out cells with separate
coefficients; labelled Apple counter estimates beside labelled NVIDIA board
estimates. **Within-platform** placement (3080 Ti versus the 80 GB card at
one CUDA recipe) and within-platform mechanism cells need no new Apple cell.

**Mechanism cells on NVIDIA.** MoE with all experts resident, routing and
executed bytes recorded (OLMoE-1B-7B, which Fernandez [16] found up to 54%
*more* energy than dense OLMo-1B; DeepSeek-V2-Lite at short prompts on the
owned card; the 30B-A3B-vs-32B contrast, ML.ENERGY v3's 3.56× [3], only on
the 80 GB card). Speculative decoding as joules per *accepted* token with
draft, rejected proposals and verification all counted (0.6B drafter + 8B
INT8 target = 9.4 GB fits the owned card; 70B targets only on 80 GB). KV
quantization on one model at fixed contexts with conversion work recorded
(FP8 and INT8 caches are different recipes). Scaling: freeze the equation,
fit 1.7B, 4B, 8B, ≈32B, hold 14B out, per platform. Each is a follow-on
module with its own floors, not hidden in another week's count.

### 3c — Split-request transfer cost (a bounded Paper E rider)

The split-request version needs the transfer cost, and here the instruments
run out. **Measurable:** Mac-side prefill plus serialize-and-send under
`powermetrics`, rig-side receive-deserialize-decode under NVML, each against
its own floor; and, if the Mac's Ethernet adapter is a USB-C dongle, the
KM003C sits between Mac and dongle and logs the dongle's DC draw — a genuine
second use of the meter. **Not measurable:** the switch, the cable, the rig's
on-board NIC (outside board power), and whether the Mac's Thunderbolt/USB4
controller is inside the package figure at all — the only public explanation
is "everything on the chip except memory" [25], which does not name the
controllers: **NEEDS-WEB**. **Practical blocker:** the cache format must be
portable; MLX and a CUDA runtime do not share one, so the bounded experiment
uses one runtime on both ends (llama.cpp, Metal on the Mac and CUDA on the
rig, with its cache save/load — **ASSUMED**, verify). **Size:** Qwen3-8B INT8
at 2K prompt → ≈0.3 GB cache → ≈2.4 s at 1 GbE, ≈1 s at 2.5 GbE; at 8K the
1,207,959,552-byte cache takes 9.664 s at 1 Gb/s, 3.865 s at 2.5, 0.966 s at
10 (ideal wire time, ASSUMED link rates, before serialization). **Order of
work:** fixed byte buffers, then a real saved cache, then decode from it with
output verified; sending, receiving, loading and inference measured
separately; a software rate sweep tests sensitivity to bandwidth, not the
electrical cost of a different network. One floor window per side, two
contrast windows (split vs whole on each device), one reserve = 5 windows;
Ed ≈1 h once for adapter and cable. **Stated attribution limit:** link energy
is bounded below by the dongle's measured DC and unbounded above on the rig
side; the split claim is device-side-only and boundary-labelled.

### 3d — The three NVIDIA sub-options compared

| | owned RTX 3080 Ti (12 GB; OS unknown) | friend's RTX 5080 (16 GB, Windows, remote) | rented 80 GB H100/A100, native Linux |
|---|---|---|---|
| models that fit | 1.7B all; 8B INT8/4-bit; OLMoE; 14B 4-bit; DS-V2-Lite (short prompts) | same roster + DS-V2-Lite full cache; 20–24B dense 4-bit conditional | everything through 70B 4-bit, 32B BF16, 30B-A3B BF16; 100–120B 4-bit NEEDS-WEB |
| instrument | NVML; instantaneous field + energy counter NEEDS-WEB + live probe; generic call 1 s-averaged [26] | same, separately for Windows and WSL2 [39] | full-device NVML; generic H100 call may be 1 s-averaged; no tenant meter |
| quiet control | full census port; machine can be dedicated | PowerShell census; agreed no-use intervals; cannot dedicate | our VM only; exclusive physical GPU required; neighbours detected by reference spread |
| unattended operability | yes on Linux, after the port (SSH from the Mac) | least reliable: sleep, reboots, desktop activity | yes; local scheduling survives operator disconnect; reallocation = re-qualification |
| $ cost | ≈$3.40 per 25 h electricity (ASSUMED) | 0 | $3.29–4.29/h + 5 setup h (§5) |
| Ed-at-machine hours | 4–8 once, 0.5–1 per batch | 3–6 + 1–2 of the friend, per-session scheduling | 2–4 once |
| RQs | placement core; method replication; small MoE; small speculative; KVQ on 8B; bytes-law lower rungs; matched 1.7B | one newer-architecture point, Windows-conditioned | matched 8B BF16; 30B-A3B vs 32B; 70B speculative; scaling roster; KV-cache week |

**Recommendation (resolution 2).** Primary the owned 3080 Ti, secondary one
rented 80 GB PCIe card, tertiary and optional the friend's 5080 — on Ed's
CV-per-Ed-hour objective, conditional on the inventory's decision rule; the
cloud-primary order applies the moment the rule says so. Multi-GPU cloud is
not scheduled.

## §4 — Interconnect and network questions, answered straight

| question | owned/borrowed hardware | rented cloud | attribution limit |
|---|---|---|---|
| how fast can the host move data to the 3080 Ti? | yes: host-to-GPU copies at recorded PCIe generation and width | yes on a suitable device | board energy covers GPU-side work only, not host memory or CPU |
| what does link bandwidth do to cache-transfer latency? | yes: Mac ↔ rig on a controlled local link (Leg 3c); cards/cables ASSUMED unknown | yes with two endpoints and known topology | timing and bytes measurable; NIC and switch energy never |
| NVLink vs PCIe for tensor parallelism? | no: one GPU per rig; neither consumer card has NVLink [23,37] | yes on a multi-GPU host (8×H100 SXM $3.99/GPU-h → ≈$80/window [21]) with the route verified from communication logs | sum of participating boards at TP=2 vs TP=1; NVSwitch fabric, host and NIC outside it |
| Splitwise/DistServe-style prefill/decode separation? | conditional on a compatible cache transfer (Leg 3c, one runtime both ends) | better with two compatible workers and a controlled link | service timing + board energy; never total system or network energy |
| multi-Mac over Thunderbolt vs Ethernet? | no: one Mac | not a rental product | one meter cannot bound two computers and the network at once |
| how many joules does the NIC or fabric consume? | not attributable | not attributable with tenant NVML | needs its own power measurement or an encompassing system meter |

Summary: on owned hardware, timing and bytes, plus Leg 3c's device-side
deltas with the dongle's DC as a lower bound on link energy; on rented
multi-GPU, sum-of-boards under tensor parallel with the fabric unattributed;
never NIC, switch or fabric joules, cross-node disaggregation energy, or any
multi-Mac question. Weakest fit for the metrology framing; ranked last. The
repository's Phase 3 gates (baseline readiness, feasibility verdict, offline
replay before live split) apply unchanged.

## §5 — Week-by-week horizon ladder from day 24 (this is the sequence)

| week | days | windows / desk | needs from Ed | Ed-hours | dollars | what it adds to the CV |
|---|---|---|---|---|---|---|
| H1 | 24–30 | meter H1.1–H1.5 (4 + 1 reserve); Leg 2 diagnostics (2); Leg 2 desk items; NVIDIA: rig inventory → 2 sensor/boundary diagnostic windows + 1 reserve on the primary platform; ≈3 meter + 6–9 NVIDIA desk blocks (seat work) | plug the meter in; cables, logging host, battery hold; one rig setup evening or account/access setup | 4–6 | 0 (≈$30 if cloud is primary: 3 windows) | Paper B carries a mapped scale and an instrument section no Apple study has; live worker proof; chosen NVML field; request totals as the first NVIDIA product |
| H2 | 31–37 | matched 1.7B/8B BF16 on **each** of Apple and the primary NVIDIA platform: 4 floor, 2 contrast, 1 held-out, 2 reserve = 9 each (8B on the 80 GB card); owned-rig placement study (11, §3a); artifact package + Zenodo DOI | protected machine availability; review of refused windows; Zenodo account | 2–3 + 0.5 | ≈$95 (9 cloud windows) + ≈$3 electricity | Paper E core: Ed's placement question answered across three device classes and two instrument classes, matched recipe, negative short-phase results printed; ACM badges |
| H3 | 38–44 | scaling roster on each primary platform: 5 decode-floor, 2 fit-grid, 1 held-out-model (14B), 2 reserve = 10; owned rig: 1 diagnostic, 2 request-floor, 1 request-contrast, 1 reserve = 5, plus within-platform mechanism riders (OLMoE, speculative 0.6B+8B, KVQ on 8B) as their floors allow | rig access and thermal stability checks | 4–7 | ≈$105 (10 cloud windows) | bytes law tested with 14B held out on a second vendor; consumer-device supplementary result |
| H4 | 45–51 | **preferred if the bytes law stood in H3:** KV-cache surface on each primary platform — Qwen3-8B at one fixed 8,192-token context, two cache precisions: 2 cache-condition floor, 2 contrast, 1 same-cell held-out session, 1 load-transfer diagnostic, 2 reserve = 8; **rider only if already cabled:** split-request (5), last because it has the weakest attribution; optional 5080 session (1 point), never on the critical path | adapter + cable if the rider runs; the 5080 session if it happens | 2–3 + (1) + (0–3) | ≈$85 (8 cloud windows) + ≈$40 adapter | one bounded KV-cache mechanism extension across vendors; transfer figure with its stated limit |
| H5+ | 52– | writing: Paper E to a venue; Paper F to a workshop; network feasibility (§4) only as a separately budgeted extension | none | 0 | 0 | two co-authored submissions past the capstone |

Ed's physical involvement across H1–H4: **12–19 hours** (Astra's estimate,
adopted), separate from writing and review. Apple and cloud windows may
overlap once both are independently armed and no assistant is using the
measured Mac. Adding 16K or 64K cache contexts in H4 needs further floors;
they are not hidden in the eight-window count.

**Cloud arithmetic (resolution 4).** The Fable draft priced 12 windows at
$1.39–4.29 per GPU-hour → $3.5–11 per 2.5 h window → **$40–130** [21,22].
Astra's count is adopted for planning: Paper E core = 3 diagnostic + 9
matched windows = 12 × 2.5 h + 5 setup hours = 35 billed hours at the verified
H100 prices ($3.29–4.29/h) → **$115–150** before storage and tax; the full
primary-NVIDIA plan = 3 + 9 + 10 + 8 = 30 windows → 80 billed hours →
**$263–343**, assuming instances are released between work periods (keeping
one device avoids re-qualification but raises the bill). If the owned rig is
primary, only the 80 GB-only cells (matched 8B, 30B-A3B/32B, 70B speculative,
part of the scaling roster) are rented and the bill falls toward the Fable
figure.

**Paper E — "What Carries Across Counters? Phase-Energy Resolution on Apple
Silicon and NVIDIA GPUs."** Headline to test: a common
calibration-and-refusal procedure yields defensible, platform-specific energy
decisions; which phases resolve and which uncertainty dominates depend on the
instrument. Results: the whole-request placement rule across three device
classes (energy per request by class, each above its own floor, `not
resolvable` printed where the floors forbid it, request totals plus printed
phase refusals on NVIDIA), the matched-recipe replication, and the scaling
and KV-cache tests with per-platform coefficients (Astra's Paper F folds in
here). Reviewer case: independent platform floors, device-boundary
qualification, held-out null tests, explicit negative results, a
`usbc_dc_input` arm whose physical scope is stated, boundaries labelled on
every number, a decision rule rather than a leaderboard.

**Paper F — "What `powermetrics` measures: a USB-C DC input mapping, counter
granularity and sampler overhead for Apple-silicon energy metrology."**
Headline: on one unit, the mapping from the software counter to USB-C DC
input across a load ladder (slope, offset, interval, held-out error), the
counter's update period, the sampler's own cost, and the time-anchoring
bound — the four facts record 21 found no Apple study states. ≈8 windows plus
desk time, most already inside H1–H2; workshop-length (HotCarbon or an
e-Energy workshop) with the advisor as co-author; the paper everyone
measuring on a Mac would cite, while Paper E is the one people outside Apple
cite.

## How we compare with industry standards after the horizon

SPEC and MLPerf Power require an external analyzer with ≤1% uncertainty,
calibrated yearly, ranged before the counted runs, sampling at 1 s for ≥60 s
[1,2]. After the horizon JouleWise has a consumer inline DC meter whose
retail-stated accuracy is 1% (**NEEDS-WEB** against the datasheet) with no
calibration certificate, at a different boundary (`usbc_dc_input`, adapter
loss excluded), ranged before the counted runs, sampled faster than the
standards require, and anchored to the workload by pulses rather than NTP (a
sub-100 ms bound against MLPerf's 800 ms tolerance). The honest sentence:
JouleWise's counter scale is *mapped* to a consumer meter's DC input with a
held-out error, not calibrated against an analyzer; its phase attribution
rests on `powermetrics`' time base and is cross-checked, not calibrated, by
the meter; the second instrument class (NVML) replicates the procedure and
its refusals, not the scale. Weaker than SPEC on the scale, stronger on
anchoring, repetition design and stated resolution — and it says so.

## What would change the order

1. **The ruling box rules differently** (e.g. keeps "gain" pending a second
   instrument). Leg 1 waits; every NVIDIA step proceeds unchanged.
2. **Battery participation cannot be bounded** (H1.1). Meter data stays
   diagnostic or the work-plus-recharge experiment is declared; no phase
   energy is ever multiplied by a slope.
3. **The logger cannot run without loading the Mac.** It stays on the second
   host; H1 slips one desk-day.
4. **The rig inventory finds Windows, or only the one-second-averaged
   field.** Cloud-primary order applies; the 3080 Ti becomes the secondary
   check and the cloud counts rise to Astra's full 30 windows.
5. **GeForce cards do not expose the NVML energy counter.** The owned-rig leg
   runs on the power field with the update-period characterization as its
   floor input; the "second instrument class" claim rests on whichever card
   keeps the counter.
6. **NVIDIA phases are shorter than the sensor response.** Request totals and
   printed refusals are Paper E's NVIDIA result; a longer-prompt study is a
   new declared experiment; faster polling is not a cure.
7. **A cloud device is shared, loses telemetry or changes identity.** Refuse
   it for claim collection; prefer a smaller owned-rig study.
8. **A model fits only with offload.** Shrink the resident roster; the
   scaling claim is not kept on the original roster.
9. **The cloud reference spread exceeds the floor in two consecutive
   windows.** Change instance type or provider before the third; the
   standing two-failures rule applies.
10. **The bytes law fails held-out on NVIDIA in H3.** That is a result; H4
    swaps to the split-request rider (if cabled) or a second mechanism
    module, not to more scaling windows.
11. **Ed's time budget shrinks.** Drop in this order: the 5080 sessions, the
    split-request rider, the KV-cache week, the cloud tier. The meter, the
    desk items and the owned-rig study survive any cut.

## Sources

Record 21 §4's list is reused by number [1]–[20]. Added by the Fable draft
([21]–[31]) and the Astra consult ([32]–[43]), each fetched unless marked:

21. Lambda GPU Cloud pricing, https://lambda.ai/service/gpu-cloud — 1×H100 PCIe $3.29/GPU/h; 1×H100 SXM $4.29; 1×A100 SXM 80 GB $3.99; 8×H100 SXM $3.99/GPU/h; no as-of date.
22. Runpod H100 page, https://www.runpod.io/gpu-models/h100 — H100 80 GB from $2.89/h (Secure), $1.99/h (Community); the A100 figures ($1.39 Secure, $1.19 Community) are search snippets, not fetched.
23. NVIDIA GeForce RTX 5080, https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/ — 16 GB GDDR7; total graphics power 360 W; no NVLink.
24. `powermetrics` manual mirror, https://ss64.com/mac/powermetrics.html — `smc` sampler "on supported platforms" includes temperature sensors; `thermal` sampler reports instantaneous thermal pressure.
25. Apple Developer Forums thread 709276, https://developer.apple.com/forums/thread/709276 — "package power" is everything on the chip except memory; excludes backlight and disk.
26. NVML Device Queries, https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html — `nvmlDeviceGetPowerUsage` in milliwatts, a one-second average on Ampere except GA100 and on newer architectures; explicit instantaneous and average fields exist, device support to be checked; `nvmlDeviceGetTotalEnergyConsumption` in millijoules since driver reload.
27. ML.ENERGY, "Measuring GPU energy: best practices", https://ml.energy/blog/energy/measurement/measuring-gpu-energy-best-practices/ — energy counter on Volta or newer; NVML reads must be synchronized with GPU execution.
28. mradermacher/DeepSeek-V2-Lite-GGUF, https://huggingface.co/mradermacher/DeepSeek-V2-Lite-GGUF — Q4_K_M 10.5 GB; Q8_0 16.8 GB.
29. unsloth/Qwen3-30B-A3B-GGUF, https://huggingface.co/unsloth/Qwen3-30B-A3B-GGUF — Q4_K_M 18.6 GB; Q8_0 32.5 GB; BF16 61.1 GB.
30. allenai/OLMoE-1B-7B-0924, https://huggingface.co/allenai/OLMoE-1B-7B-0924 — 7B total, 1.3B active parameters.
31. Alibaba buying guide for the POWER-Z KM003C, https://electronics.alibaba.com/buyingguides/chargerlab-power-z-km003c-guide-what-it-does-who-needs-it — HID over USB-C, no drivers; exports `.csv`/`.log`. The manufacturer's product page and the user manual (power-z.com; manuals.plus) returned HTTP 403; the sampling-rate, accuracy, ADC and range figures quoted in Leg 1 come from search snippets only and are NEEDS-WEB.
32. ChargerLAB, "How to use POWER-Z KM003C to record charging data offline", https://www.chargerlab.com/how-to-use-chargerlab-power-z-km003c-tester-to-record-charging-data-offline/ — application logging at 1, 10, 50 or 1,000 samples/s; CSV export; display refresh is a separate setting. The manual's technical table did not load through the available read path.
33. Qwen/Qwen3-8B model card, https://huggingface.co/Qwen/Qwen3-8B — 8.2 B parameters.
34. Qwen/Qwen3-14B model card, https://huggingface.co/Qwen/Qwen3-14B — 14.8 B parameters.
35. Qwen/Qwen3-30B-A3B model card, https://huggingface.co/Qwen/Qwen3-30B-A3B — 30.5 B total, 3.3 B activated per token.
36. Qwen3-8B `config.json`, https://huggingface.co/Qwen/Qwen3-8B/blob/main/config.json — 36 layers, 8 key-value heads, head width 128.
37. NVIDIA GeForce RTX 3080 / 3080 Ti, https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080-3080ti/ — 12 GB; no NVLink.
38. Lambda pricing page, https://lambda.ai/pricing — single H100 PCIe $3.29/h and SXM $4.29/h before tax; the A100 80 GB offer appears only in the multi-GPU section, so a single A100 at $2–4/h is ASSUMED availability.
39. NVIDIA CUDA on WSL user guide, https://docs.nvidia.com/cuda/wsl-user-guide/index.html — NVML queries missing under WSL2, including utilization and active compute processes.
40. vLLM GPU installation, https://docs.vllm.ai/en/v0.28.0/getting_started/installation/gpu/ — Linux documented; WSL and community routes for Windows.
41. Dauner et al., HotCarbon 2026, https://hotcarbon.org/assets/2026/paper-46.pdf — platform-dependent cumulative-energy behaviour and stale reads (record 21's [9]).
42. Yang et al., https://arxiv.org/abs/2312.02741 — default `nvidia-smi` cadence covers ≈25% of runtime (record 21's [10]).
43. Watt Counts, https://arxiv.org/html/2604.09048v1 — <1% difference between 10 Hz and 200 Hz polling on the same instrument.
