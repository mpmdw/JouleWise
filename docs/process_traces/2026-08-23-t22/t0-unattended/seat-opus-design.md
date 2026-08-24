# T0-UNATTENDED-01 — machine-authored clock evidence (Opus design seat, blind)

**Row:** `T0-UNATTENDED-01` (TASK_QUEUE.md:638; `docs/process/state_kernel.json:3307`)
**Authority:** D-150 item 4 (`docs/decision_log.md:178`) + r4-6 B-δ
**Repo state:** `/Users/edr/code/JouleWise` @ `main` `33aa594`, read-only. (HEAD advanced to `75e5ae4` — a RUN_STATE bookkeeping commit from another stream — while this seat was reading; every cite below was re-verified against the working tree at `75e5ae4` and none moved.)
**Threat model:** D-139 A1 — in-process adversary OUT of model (`docs/decision_log.md:10053-10063`); the residual risk this class must catch is **bugs and drift**, not deception.
**Date of live measurements:** 2026-08-23, on Ed's M3 Max, agent session live, no window in progress. All measurements below are diagnostic-only; none is window evidence.

---

## 0. Cite verification (asked for explicitly)

**r4-6's cite `:884-889` is CORRECT at HEAD.** `joulewise/arm_readiness_evidence_t0.py:881-888` is the `_DerivedRow(...)` constructor for `clock.correct_and_prior_state`; its fourth positional argument — `source_kind` — is the string literal `"OPERATOR_ATTESTATION"` at **`:885`**, inside the cited span. r4-6's claim "CLOCK_ATTESTATION is OPERATOR_ATTESTATION by construction" is exact: the source kind is a hard-coded literal, not a derived value.

**The option-(b) PROBE hook exists and is already open.** `joulewise/arm_readiness.py:731`:

```python
"CLOCK_ATTESTATION": frozenset({"OPERATOR_ATTESTATION", "PROBE"}),
```

`PROBE` is already an admitted source for this evidence kind. The consuming predicate reads that frozenset at `arm_readiness.py:5788` (`admitted_sources = _EVIDENCE_SOURCE_KINDS[expected_kind]`) and accepts any fact whose `source_kind` is in it (`:5794`). **Therefore no new evidence kind, no registry vocabulary change, and no `SOURCE_KINDS` change is required.** This is the single most important structural fact in this design: the work order is a *derivation* change plus a *content-predicate* change, not a contract-vocabulary change. (Contrast: `arm_readiness.py:723-726` states the registry "deliberately remains the exact-key row/kind vocabulary" — we do not touch it.)

---

## 1. What the operator's "yes" actually supplies — and what it does not

Before designing a replacement, the thing being replaced has to be stated in physical terms, because the answer is much smaller than the ceremony around it.

Today's T-0 clock ceremony collects **two** operator inputs (`scripts/capture_t0_step.py:3-11` — "the only operator-supplied values are E-4's two registered irreducible observations"):

**Input 1 — the typed UTC literal.** Ed reads a clock he trusts (a phone) and types the UTC time. `capture_t0_step.py:543-582` compares it to `datetime.utcnow()` and refuses above **2.0 s** difference. The result is stored in `clock-attestation.json` and re-checked by the author at `arm_readiness_evidence_t0.py:540-551` (same 2.0 s bound), producing `comparison_delta_seconds`.

What this establishes, physically: **at one instant, the system wall clock agreed with an off-machine reference to within 2 seconds.** Nothing about any other instant. Nothing about rate. Nothing about the following 3.5 hours of capture.

**Input 2 — the pasted `systemsetup -getusingnetworktime` output.** Ed runs the privileged read himself and pastes the text. `capture_t0_step.py:762-780` stores it as a command capture with the sentinel argv `("operator-interactive", "network-time-prior-state")` (`:49-50`). The author re-checks the argv (`arm_readiness_evidence_t0.py:862-863`) and regex-extracts `Network Time: (On|Off)` (`:866-868`).

What this establishes: **it is a tautology.** Trace the consumers:

| Field | Writers | Readers |
|---|---|---|
| `prior_network_time` | `arm_readiness_evidence_t0.py:879` | **none in the repository** |
| `prior_systemsetup_state_captured` | `arm_readiness_evidence_t0.py:877` (hard-coded `True`) | `arm_readiness.py:805` (requires `True`) |
| `comparison_delta_seconds` | `arm_readiness_evidence_t0.py:878` | **none** |

(Verified by repo-wide grep excluding `.git` and `docs/process_traces`.)

`prior_systemsetup_state_captured` is set to the literal `True` unconditionally whenever the author gets that far; the predicate at `arm_readiness.py:805` then requires it to be `True`. The boolean carries **zero information** — its truth is decided by the author reaching line 877, which is decided by the argv and regex checks above it. `prior_network_time`, the only field carrying the actual observed state, **is read by nothing**. The restore path does not consume it either: restore is governed by its own separate predicate `clock.restore_recipe.v1` (`arm_readiness.py:810-814`), which binds close-out recipe hashes to the pack, not an observed prior state.

**Consequence, which drives the whole design:** retiring Input 2 costs **zero gate coverage**. It is not a measurement gate; it is an operational courtesy that was wired into a claim-bearing evidence row. Under the "every field earns its refusal" lens, `prior_network_time` and `prior_systemsetup_state_captured` are exactly the fields that do not.

That leaves **one** real thing to replace: *is the wall clock correct at T-0*, currently answered to ±2 s by a human reading a phone.

---

## 2. What the machine can observe — measured, not assumed

Four probes were run live today. Two are usable, one is not, and one is the platform tool the repo already uses.

### 2.1 Absolute correctness: SNTP quorum — USABLE, and 50× tighter than the human

Three mutually independent time services, queried with a direct SNTP client (48-byte UDP, no system daemon involved):

```
time.apple.com   stratum=1  rootdisp=0.18ms   OFFSET=+30.278ms  rtt=21.04ms
pool.ntp.org     stratum=2  rootdisp=10.16ms  OFFSET=+32.694ms  rtt=69.97ms
time.nist.gov    stratum=1  rootdisp=0.49ms   OFFSET=+39.198ms  rtt=64.00ms
```

Three independent operators (Apple, the NTP Pool volunteers, US NIST), agreeing within a 8.92 ms spread. The platform tool `/usr/bin/sntp` — **which `scripts/quiet_window_clock.sh:42` already uses** — independently reports the same thing through a completely different implementation:

```
$ /usr/bin/sntp -t 3 time.apple.com
+0.027688 +/- 0.017541 time.apple.com 17.253.4.45      (exit 0)
```

+27.7 ± 17.5 ms, agreeing with the raw-socket figure to 2.6 ms. **The machine measures its own wall-clock error to about ±20 ms. The human attestation's tolerance is 2 000 ms.** That is a factor of 100 in resolution and a factor of 4 in the enforced ceiling (see §3.2).

`sntp` failure behaviour, also measured, because refusal semantics depend on it:

| Condition | stdout/stderr | exit |
|---|---|---|
| success | one line `^[+-]d.d \+/- d.d <host> <ip>$` | `0` |
| unreachable host (`192.0.2.1`, `-t 2`) | 5 × "Exchange failed: Timeout", then "Clock select failed", ~4 KB of `sntp_exchange {…}` dumps | **69** |
| DNS failure (`.invalid`, `-t 2`) | 5 × "Exchange failed: DNS lookup failure" + dumps | **69** |

Two operationally load-bearing facts: `sntp` retries **five** times internally, so wall-clock cost on a dead server is ≈ 5 × `-t`; and it never exits 0 without a parseable offset line. With `-t 2` a dead server costs ~10 s, comfortably inside the author's `_PROBE_TIMEOUT_SECONDS = 45` (`arm_readiness_evidence_t0.py:54`) **only if each server is its own probe invocation**. Three servers in one `sntp` call could exceed 45 s and be SIGKILLed by `_execute_probe:402-406`, which would be reported as an execution failure rather than a clean refusal. Design consequence: **one `_fresh_probe` per server.**

### 2.2 Step/slew detection: the anchor — USABLE, and the human cannot supply it at all

Define the **anchor**:

> **ANCHOR** := `CLOCK_REALTIME` − `CLOCK_MONOTONIC_RAW`, both read as integer nanoseconds.

`CLOCK_REALTIME` is the wall clock — the one software adjusts. `CLOCK_MONOTONIC_RAW` is the free-running hardware counter — by definition *not* adjusted. Both advance from the same oscillator, so **oscillator error cancels in the difference**: if the crystal is 4 ppm fast, both readings run 4 ppm fast and ANCHOR does not move. ANCHOR moves *only* when software steps or slews the wall clock. It is a pure software-adjustment detector.

Measured on this machine, five samples over 2.8 s, each taken as RAW→REALTIME→RAW with the two RAW reads averaged to cancel read skew:

```
anchor_delta_ns=           0   read_skew_ns=625
anchor_delta_ns=        -209   read_skew_ns=1708
anchor_delta_ns=         291   read_skew_ns=4125
anchor_delta_ns=         395   read_skew_ns=4500
anchor_delta_ns=        -209   read_skew_ns=4458
```

**Noise floor: ±395 ns over 2.8 s. Read skew ≤ 4.5 µs.** The governed anchor ceiling in this project is **5 ms** (`scripts/quiet_window_clock.sh:7,14,60-62`; `docs/phase_2/window_runbook.md:499`) — 12 600× above the measured noise.

The long-baseline cross-check, same machine:

```
kern.boottime          = 1783962966 s   (2026-07-13 10:16:06Z)
CLOCK_MONOTONIC        = 3 573 895.457 s
CLOCK_MONOTONIC_RAW    = 3 573 908.602 s
CLOCK_REALTIME - boottime = 3 573 895.457 s   (== CLOCK_MONOTONIC, sub-ms)
```

`MONOTONIC_RAW − MONOTONIC = 13.145 s` accumulated over **41.36 days** = **3.68 ppm**. Read plainly: over six weeks the time daemon corrected this machine's wall clock by 13.1 seconds, i.e. the crystal runs ~3.7 ppm fast and `timed` has been quietly pulling it back. That number matters twice below.

*The design does not depend on which internal clock XNU adjusts.* It depends only on the measured property that ANCHOR is invariant when no adjustment occurs — which the rehearsal's positive control (§5.3) must confirm rather than assume.

### 2.3 Detector sensitivity, against the actual historical failure

The failure this whole clock ceremony exists for: on 2026-07-26 two window-C attempts died because the wall clock was being slewed against the monotonic clock at **+110 ppm** and then **−158 ppm**, producing 5.544 ms and 7.769 ms anchor excursions (`scripts/quiet_window_clock.sh:5-12`). Every environment gate passed; nothing else caught it.

Over a T-0 sequence, which is structurally **≥ 600 s** long (the prewindow idle proof, `_MIN_IDLE_NS = 600 * 1e9`, `arm_readiness_evidence_t0.py:51`, enforced at `:967-968`):

| Adjuster rate | ANCHOR movement over 600 s | vs 5 ms ceiling |
|---|---|---|
| this machine's benign crystal error, sync OFF | **0 ns** (cancels — §2.2) | — |
| steady `timed` correction of that crystal, 3.68 ppm | 2.2 ms | 0.44× — **not detected** |
| 2026-07-26 slew, +110 ppm | **66 ms** | **13.2× — detected** |
| 2026-07-26 slew, −158 ppm | **95 ms** | **19.0× — detected** |
| any step ≥ 5 ms (sleep/wake re-step, manual set) | ≥ 5 ms | **detected** |

Minimum detectable rate over a 600 s span = 5 ms / 600 s = **8.3 ppm**. The detector's threshold sits *between* this machine's benign behaviour (3.68 ppm, 2.3× below) and the pathological rates that actually cost windows (110–158 ppm, 13–19× above). That is the design's central quantitative claim, and it is falsifiable by re-running the two measurements above.

**Honest limits, stated because they bound the refusal:** (a) a slow steady discipline below 8.3 ppm is *not* caught by the anchor — it is caught instead by `CLOCK_PROBE`, which re-executes `sudo -n systemsetup -setusingnetworktime off` at authoring and refuses on nonzero exit (`arm_readiness_evidence_t0.py:891-916`); the two mechanisms are layered, not redundant. (b) With network time off, the wall and monotonic clocks derive from the same oscillator, so a *passing* anchor check is expected by construction — `quiet_window_clock.sh:118-128` says exactly this and forbids citing a green anchor as evidence of a quiet clock. **The anchor check is therefore admitted as a falsifier, never as a certifier.** Its value is its refusal; its pass asserts nothing. Field naming in §4 reflects that.

### 2.4 The prior network-time state: NOT machine-observable without new privilege — measured

All three non-privileged routes fail on this machine:

```
$ /usr/sbin/systemsetup -getusingnetworktime
You need administrator access to run this tool... exiting!

$ ls -l /Library/Preferences/com.apple.timed.plist
ls: No such file or directory

$ ls -l /private/var/db/timed/
ls: Permission denied
```

So automating Input 2 *would* require a new privileged command — precisely the sudo addition the r4-6 fence downgraded to observability-only. **§1 showed Input 2 is a tautology with no readers. The design therefore retires it instead of automating it, and the D-127 scope amendment adds nothing (§6).**

---

## 3. The evidence class

**Name:** machine-authored clock-discipline evidence for row `clock.correct_and_prior_state`.
**Evidence kind:** `CLOCK_ATTESTATION` — *unchanged*.
**Source kind:** `PROBE` — already admitted at `arm_readiness.py:731`.
**Freshness class:** `TIME_BOUND`, 6 h — *unchanged* (see §3.4 for why, and what it costs).

The class is three probes and one ordering constraint. Every element below either refuses or does not exist.

### 3.1 Probe R0 — pre-pin reference (in the T-0 capture sequence, before the disable)

A new governed T-0 step, `clock-reference`, replacing today's `clock-prior-state` step one-for-one in `STEP_ORDER`. It is an ordinary command capture — same `_COMMAND_SCHEMA`, same `_CAPTURE_KEYS` — so it inherits the whole existing authentication chain for free (canonical-JSON parse, boot-session binding, `started/finished_monotonic_ns`, the 60-minute liveness bound at `arm_readiness_evidence_t0.py:496-501`, and global ordering at `:1627-1637`).

Its argv is a new tracked collector, derived by `_command_for_step` exactly as the other steps are:

```
(<repo>/.venv/bin/python, <repo>/scripts/collect_clock_reference.py,
 --server, time.apple.com, --server, time.nist.gov, --server, pool.ntp.org,
 --timeout, 2)
```

Its **stdout is one canonical strict-JSON object** — no second artifact file, no new schema plumbing in the author beyond validating that object:

```json
{ "schema_version": "joulewise.arm_readiness_t0_clock_reference.v1",
  "anchor_realtime_ns": 1787536862057283000,
  "anchor_monotonic_raw_ns": 3573908601607083,
  "anchor_read_skew_ns": 625,
  "boot_session_id": "…",
  "samples": [ { "server": "time.apple.com", "exit_code": 0,
                 "offset_s": 0.027688, "uncertainty_s": 0.017541,
                 "peer_address": "17.253.4.45", "raw_line": "+0.027688 +/- 0.017541 …" },
               … ] } 
```

**What R0 refuses on (this is the pre-pin gate — the machine analogue of `quiet_window_clock.sh:69-93` "verifying the clock is correct before pinning it"):**

1. fewer than **2** servers returned `exit 0` with a parseable line → refuse (quorum);
2. the two-or-three surviving **correctness intervals** `[offset − uncertainty, offset + uncertainty]` have **empty common intersection** → refuse (the servers contradict each other; one is broken);
3. the worst-case bound `|midpoint(intersection)| + halfwidth(intersection)` exceeds **0.5 s** → refuse (do not pin a wrong clock);
4. `anchor_read_skew_ns` > **1 ms** → refuse (the sampler itself was preempted; the anchor reading is not trustworthy).

The intersection rule replaces a magic agreement threshold with a self-scaling one: a server on a slow path declares a wide interval and constrains little; a stratum-1 server on a fast path declares a narrow one and constrains a lot. Worked on today's numbers, using each `sntp`-style ± uncertainty (rtt/2 for the raw-socket run): apple `[19.8, 40.8] ms`, pool `[−2.3, 67.7] ms`, nist `[7.2, 71.2] ms` → intersection `[19.8, 40.8] ms` → midpoint 30.3 ms, halfwidth 10.5 ms → worst-case bound **40.8 ms ≤ 500 ms**, passing with **12× margin**. A server lying by a second, or a machine actually a second wrong, collapses the intersection or blows the bound.

The 0.5 s ceiling is **not a new policy number**: it is `MAX_OFFSET_S` from `scripts/quiet_window_clock.sh:30`, the value at which this project already refuses to pin a clock, with the same recorded rationale ("Pinning it now would bake that error into the whole window", `:88`). One home, reused. It is 4× tighter than the 2.0 s the operator path enforces.

### 3.2 Probe R1 — authoring-time reference (in the evidence author, zero staleness)

At authoring, the author runs **one `_fresh_probe` per server**, `("/usr/bin/sntp", "-t", "2", "<server>")`, and applies the *identical* quorum/intersection/ceiling rules as R0 (§3.1 rules 1–3). Same code path, same constants, evaluated on live output with no staleness whatsoever — this is what `PROBE` means everywhere else in this module (`_derive_clock_probe:891`, `_derive_powermetrics:1463`, `_maintenance_probe:981`).

R1 is the **gating** absolute-correctness measurement. R0's separate refusal exists because the pin happens between them: R0 says "the clock was right before we disabled sync", R1 says "the clock is right now, at authoring". Both are required; each has distinct refusal power. Querying a time server does not set the clock — `sntp <host>` without `-s`/`-S`/`-a` only reports, which `quiet_window_clock.sh:38-39` already relies on and which is confirmed by its running unprivileged above.

### 3.3 Probe R2 — anchor continuity across the T-0 sequence

The author samples ANCHOR in-process (RAW→REALTIME→RAW, midpoint, skew recorded) and compares to R0's:

```
anchor_delta = |ANCHOR_author − ANCHOR_R0|
span         = (author monotonic_raw) − (R0 anchor_monotonic_raw_ns)
```

**Refuses when:**

5. `span` < `_MIN_IDLE_NS` (600 s) → refuse. This is not a freshness check; it is a **lever-arm** check. Below 600 s the detector loses the sensitivity computed in §2.3, so a short T-0 would produce a green anchor result that means nothing. Reuses an existing constant rather than inventing one, and structurally forbids a rushed T-0.
6. `span` > `_MAX_T0_SEQUENCE_AGE_NS` (3600 s) → refuse (already enforced for the underlying capture at `:496-501`; restated here because R2's own arithmetic depends on it).
7. `anchor_delta` > **5 ms** → refuse. The governed anchor ceiling (`quiet_window_clock.sh:7`, `window_runbook.md:499`), reused, not re-derived.
8. author-side `anchor_read_skew_ns` > 1 ms → refuse (sampler health, as R0 rule 4).
9. R0's `boot_session_id` ≠ the author's live boot session → refuse (already enforced by `_capture:493`; the anchor arithmetic is meaningless across a reboot because `CLOCK_MONOTONIC_RAW` restarts).

### 3.4 Staleness bounds, end to end

| Interval | Bound | Where enforced | Change vs today |
|---|---|---|---|
| reference sample → authoring | **0 s** for R1 (in-process); ≤ 3600 s for R0 | `_fresh_probe`; `_capture:496-501` | today: up to 3600 s, with **no** in-process re-measurement at all |
| T-0 sequence span (anchor lever arm) | **600 s ≤ span ≤ 3600 s** | new, §3.3 rules 5–6 | today: no lower bound |
| authoring → arm consumption | 6 h (`_NONVOLATILE_EVIDENCE_VALIDITY_NS`, `:50`) | `arm_readiness.py:768` `TIME_BOUND` | **unchanged** |
| absolute wall error asserted | ≤ 0.5 s worst-case-bounded | §3.1 rule 3, §3.2 | today: ≤ 2.0 s point estimate |

**On the retained 6 h horizon — a disclosed weakness, inherited, not introduced.** `CLOCK_ATTESTATION` sits in `_NONVOLATILE_EVIDENCE_KINDS` (`:115-122`) at 6 h while nine live-state kinds sit at 20 minutes (`:102-114`). That concession was bought by the *cost of the human*: you cannot ask Ed to re-read his phone every twenty minutes. A machine probe costs ~1 s. **The principled class for machine-authored clock evidence is the 20-minute volatile tier**, and moving it there would make this class strictly stronger again.

I do **not** propose that move inside this work order, for a specific reason: `_VOLATILE_EVIDENCE_KINDS`/`_NONVOLATILE_EVIDENCE_KINDS` are cross-checked at import (`:123-128`), mirrored in the r1 lifecycle registry as `r1.time_bound.procedural_6h.v1`, and pinned by the in-flight C6 horizon-consistency assertion (`v4plan/opus-design.md:416`) that the `_v4` S-1 stream is landing now. Changing the tier means moving code constants, registry rows, and an assertion in lockstep with a live transaction — a collision, not a design improvement. **Recorded as a follow-on row (`T0-CLOCK-VOLATILE-01`), with the honest statement that the 6 h window between authoring and arm is covered only by boot binding and the per-window re-pin, not by the clock evidence itself.**

### 3.5 What the class is, in one paragraph a reader can rebuild from

At T-0 the machine asks three independent public time services what time it is, keeps only the servers that answered, intersects their stated uncertainty intervals, and refuses unless that intersection is non-empty and entirely within half a second of its own wall clock — once before it disables network time, and again, live, when it writes the evidence. Between those two moments it records the gap between the adjustable wall clock and the un-adjustable hardware counter, and refuses if that gap moved by more than five milliseconds over a span it also requires to be at least ten minutes long, because a gap that moves is software stepping the clock and ten minutes is the shortest span over which the historical failure rates are visible above the five-millisecond ceiling. It reads nothing privileged, prompts for nothing, and records the raw bytes of every server reply.

---

## 4. Evidence-equivalence argument (D-139 A1)

The claim to be argued: **the machine class is equivalent-or-stronger than the operator yes, under a threat model of bugs and drift rather than adversaries.**

Under D-139 A1 the question "could this be faked?" is out of model for *both* paths — and note the operator path is not the strong one on that axis anyway: `capture_t0_step.py:9-11` already registers that "v1 does not defend against deliberate operator fabrication", and the module docstring at `arm_readiness_evidence_t0.py:8-9` records producer origin as a trusted-operator limitation. A typed literal and a pasted string are as forgeable as a probe record. **A1 removes the only axis on which "a human did it" was ever an argument.** What remains is the axis A1 leaves live — does the evidence *detect the failure* — and there the comparison is not close:

| Question the evidence must answer | Operator yes | Machine class | Verdict |
|---|---|---|---|
| Is the wall clock correct at T-0? | one reading, ±2 s ceiling, single source | 2–3 independent sources, mutual-consistency test, 0.5 s worst-case-bounded ceiling, ~±20 ms resolution, twice (pre-pin + at authoring) | **stronger** — 4× tighter ceiling, 100× resolution, cross-checked |
| Did anything step or slew the clock during T-0? | **not answered at all** | ANCHOR over ≥600 s, 5 ms ceiling, catches ≥8.3 ppm and any ≥5 ms step; would have caught the 2026-07-26 failure 13–19× over threshold | **strictly new capability** |
| Was network time actually off? | not answered (the paste reports the *prior* state) | `CLOCK_PROBE` re-executes the disable and refuses on nonzero — **already PROBE today**, unchanged | equal |
| What was the prior network-time state? | recorded, **read by nothing** (§1) | retired | **equal** (zero coverage lost) |
| Can a reviewer recompute the verdict from custodied bytes? | no — the human's phone reading is unrecorded; only the typed literal survives | yes — every server reply line, exit code, argv, and both anchor samples are in the receipt's probe records | **stronger** |
| Failure mode when the check cannot be made | human improvises or the window waits for Ed | refuses (§7) | **stronger** |

Two residuals must be stated rather than argued away:

- **R-a. The SNTP reply is unauthenticated.** A network path that returns wrong time defeats R0/R1. This is an *adversary*, ruled out by D-139 A1 — and the quorum-plus-intersection rule means a single broken (not malicious) server is *detected*, which is the in-model failure. The human's phone was likewise NTP-fed and likewise unauthenticated, with a quorum of one.
- **R-b. The anchor pass is green by construction once sync is off** (`quiet_window_clock.sh:118-128`). Handled by admitting it as a falsifier only, and by naming its field so no downstream reader can mistake it for a quietness claim (§5.1).

---

## 5. Code-change shape

Five files. No registry change, no new evidence kind, no `SOURCE_KINDS` change.

### 5.1 `joulewise/arm_readiness.py` — the admissibility hook (≈12 lines)

`_PREDICATE_CONTENT_REQUIREMENTS` is matched with **subset** semantics (`_content_matches:5749-5753`: required keys must be present and equal; extra keys are allowed). So the base requirement must *shrink* to what both paths share, and each path's own requirements go into a source-discriminated branch. **The template already exists in this function** — `t0.background_quiet.v1` at `:5798-5808` does exactly this, requiring `closed_operator_observation` from OPERATOR_ATTESTATION facts and `fresh_maintenance_census` from PROBE facts. Mirror it:

```python
# :803-806  base requirement shrinks to the shared predicate
"clock.correct_and_prior_state.v1": {
    "independent_clock_attestation": True,
},

# inside _predicate_passes, beside the t0.background_quiet block at :5797
if predicate_id == "clock.correct_and_prior_state.v1":
    source_kind = fact["source_kind"]
    if source_kind == "OPERATOR_ATTESTATION" and value.get(
        "prior_systemsetup_state_captured"
    ) is not True:
        continue
    if source_kind == "PROBE" and not (
        value.get("reference_quorum_satisfied") is True
        and value.get("absolute_offset_within_ceiling") is True
        and value.get("unstepped_across_t0_sequence") is True
    ):
        continue
```

Two properties this shape buys, both required by the contract lens:

- **The operator path is not relaxed by one byte.** An OPERATOR_ATTESTATION fact must still carry `prior_systemsetup_state_captured: True`; moving it from the base dict to the branch changes nothing for that source. Attended T-0 remains available and remains exactly as strict as today.
- **A PROBE fact cannot satisfy the row by accident.** It must carry three new booleans that no existing producer emits, so a stale or foreign receipt fails closed rather than sliding through on the shared `independent_clock_attestation` key.

**Field naming is load-bearing.** `unstepped_across_t0_sequence` is deliberately phrased as the *absence of a detected step*, not as `clock_quiet`, because §2.3(b) forbids reading it as a cleanliness claim. Its docstring in the source must say so in one sentence: *"True means no adjustment above the 5 ms ceiling was detected between the reference sample and authoring; it does not assert that the clock is disciplined."*

### 5.2 `joulewise/arm_readiness_evidence_t0.py` — the T-0 author (≈90 lines net; ~35 deleted)

- **Delete** `_INTERACTIVE_PRIOR_STATE_ARGV` (`:143-146`) and `_systemsetup_argv`'s prior-state use.
- **`_CAPTURE_FILES`** (`:135-142`): replace `"clock-prior-state": "clock-prior-state.json"` with `"clock-reference": "clock-reference.json"`. `_CAPTURE_ORDER` (`:147`) follows automatically; `_capture` derives its reason-code key as `f"{step_id.replace('-','_')}_capture"` (`:469-471`), so `_RUNBOOK_ARTIFACT_REASON_CODES` (`:148-164`) swaps `clock_prior_state_capture` → `clock_reference_capture: "evidence_author_t0_clock_reference_missing"`.
- **Replace `_clock_attestation` (`:507-554`) with `_clock_reference`**: same shape — cached in `context.values`, reads via `_capture`, validates the parsed stdout object against a new `_REFERENCE_KEYS` set and `_REFERENCE_SCHEMA`, applies §3.1 rules 1–4. Retire `_ATTESTATION_SCHEMA`/`_ATTESTATION_KEYS` (`:42`, `:193-202`).
- **Add `_sntp_quorum(context, kind, servers)`**: one `_fresh_probe` per server (§2.1 — *not* one probe for all three), parse `^([+-][0-9]+\.[0-9]+) \+/- ([0-9]+\.[0-9]+) (\S+) (\S+)$` from the last non-empty stdout line of each `exit 0` probe, apply quorum + intersection + ceiling. Returns the interval and the probe tuple.
- **Add `_anchor_sample()`**: RAW→REALTIME→RAW via `time.clock_gettime_ns`, midpoint, skew. Reached through `context.clock` (`_DerivationClock`, `:241-257`) extended with a third callable so tests can drive it deterministically, consistent with how `monotonic_ns`/`utc_now` are already injected.
- **Rewrite `_derive_clock_attestation` (`:855-888`)** to: read R0; run R1; sample R2; enforce ordering `R0.anchor ≤ R0.started ≤ R0.finished ≤ disable.started` and `disable.finished ≤ R1/R2` (preserving the intent of today's chain at `:869-874`); return

```python
return _DerivedRow(
    "clock.correct_and_prior_state", kind,
    { "independent_clock_attestation": True,
      "reference_quorum_satisfied": True,
      "absolute_offset_within_ceiling": True,
      "unstepped_across_t0_sequence": True,
      # recomputable derivation inputs — recorded, not gating:
      "comparison_delta_seconds": offset_midpoint,
      "reference_bound_seconds": offset_worst_case,
      "reference_server_count": n,
      "anchor_delta_ns": anchor_delta,
      "t0_span_ns": span },
    "PROBE",                      # ← was "OPERATOR_ATTESTATION" at :885
    input_artifacts=(reference_identity, disable_identity),
    probes=tuple(sntp_probes),
    derivation={"reference_capture_sha256": …, "servers": [...]},
)
```

  Field discipline, stated so a reviewer can check it mechanically: **every boolean in `value` is a gate** (each appears in §5.1's predicate or in a §3 refusal); **every number is a derivation input** from which a reader recomputes those booleans; **nothing else appears.** Raw server bytes live in `probes`, which the receipt custodies verbatim — that is where evidence-of-record belongs, not in the value dict.
- **`_validate_capture_order` (`:1627-1637`)**: its refusal message names "E-4/E-5/E-7a/E-7b/E-8/E-9"; update the E-4 leg's wording. Mechanism unchanged.

### 5.3 `scripts/capture_t0_step.py` — the ceremony (≈70 lines deleted, ~15 added)

- **Delete** `_interactive_prior_state` (`:762-780`), the reference-time prompt path (`:540-599`), `INTERACTIVE_PRIOR_STATE_ARGV` (`:49-50`), `REFERENCE_TIME_PROMPT`/`PRIOR_STATE_PROMPT` (`:40-46`), and `CLOCK_ATTESTATION_SCHEMA` (`:39`). **After this change the script contains no `prompt(` call and no `stdin` read.**
- **`_command_for_step` (`:602-614`)**: `clock-prior-state` → `clock-reference`, returning the collector argv in §3.1. `STEP_ORDER`/`STEP_FILENAMES` follow.
- **Module docstring (`:3-11`)**: the sentence "the only operator-supplied values are E-4's two registered irreducible observations" becomes false in the good direction and must be replaced with the new statement — *the governed steps take no operator-supplied values; the trusted-operator limitation now attaches only to faithful invocation.* Leaving stale prose here would be exactly the "no word does unpaid work" failure.

### 5.4 `scripts/collect_clock_reference.py` + `joulewise/clock_reference.py` — new (≈120 lines)

Thin, tracked, deterministic: run `/usr/bin/sntp -t <timeout> <server>` per server, sample the anchor, emit one canonical strict-JSON object on stdout via `readiness.render_json`. No policy lives here — **the collector reports; the author refuses.** (If the collector also gated, a refusal would be recorded as a step failure rather than a named evidence refusal, and the reason-code surface would fork.)

It joins `_AUTHORING_ARTIFACTS` (`:56-60`) so `TERMINAL_REVIEW` binds its bytes to HEAD like the other three.

### 5.5 Tests

- Extend the named-refusal matrix (`tests/test_arm_readiness_evidence_t0.py:1174-1191`) — `CLOCK_ATTESTATION`'s row currently unlinks `clock-attestation.json`; it becomes `clock-reference.json`.
- **One defect-shaped regression per §3 refusal rule (nine).** Each must fail with `kind == "CLOCK_ATTESTATION"` and a distinct detail string. Following the module's existing convention, rules 1–9 share the `evidence_author_t0_clock_attestation_underivable` code (as today's ordering/argv/regex refusals all share it); only the missing-artifact case gets its own code. **Do not proliferate reason codes in this work order** — per-failure codes would be a convention change and belong in their own row, not smuggled in here.
- **Falsifier, mandatory:** an injected anchor pair differing by 5 ms + 1 ns must refuse, and by 5 ms − 1 ns must pass. A predicate no test can make fail is not a gate.
- **Contract test:** an OPERATOR_ATTESTATION fact lacking `prior_systemsetup_state_captured` must still fail `_predicate_passes` after the §5.1 edit (proves the attended path was not relaxed).
- **Contract test:** a PROBE fact carrying only `independent_clock_attestation: True` must fail (proves the shrunk base dict did not open a hole).

---

## 6. The D-127 scope amendment — **NULL, and that is the finding**

Enumerate what the design executes with elevated privilege:

| Operation | Privilege | Status |
|---|---|---|
| `sntp -t 2 <server>` ×3, R0 and R1 | **none** — ran unprivileged today | no grant needed |
| `clock_gettime(REALTIME/MONOTONIC_RAW)` | **none** | no grant needed |
| `sudo -n systemsetup -setusingnetworktime off` | privileged | **already granted** — `scripts/joulewise-network-time.sudoers:2` |
| `systemsetup -getusingnetworktime` | privileged | **not used — retired, not deferred** |

**The privileged-scope change r4-6 assumed necessary is not necessary.** r4-6 reasoned that unattended T-0 needs "a privileged-scope (D-127) change AND a code change". The first half does not survive §1's consumer trace: the only T-0 step that would have needed new privilege is the prior-state read, and that read feeds a boolean that is a tautology and a field with no readers. Retiring it is cheaper *and* strictly safer than automating it, and it leaves the r4-6 fence ("the sudoers `-getusingnetworktime` item remains observability-only") not merely honoured but moot.

The amendment that gets **recorded** — satisfying the acceptance line "The D-127 scope amendment is recorded" — is therefore a scope *closure*, and I propose this exact wording:

> **D-127.1 (scope closure, T0-UNATTENDED-01).** The D-127 privileged scope is **unchanged and now final**: exactly `/usr/sbin/systemsetup -setusingnetworktime off` and `… on`, as carried in `scripts/joulewise-network-time.sudoers` (4 lines, SHA-256 `7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`, `docs/phase_2/window_runbook.md:551-560`). Unattended T-0 requires **no new privileged command**. The `-getusingnetworktime` item — downgraded to observability-only by r4-6 — is **RETIRED, not deferred**: window T-0 no longer reads the prior network-time state, because that read fed one tautological boolean and one field with no consumers, while restore is governed independently by `clock.restore_recipe.v1`. Any future proposal to add a privileged `get` is a new decision, not an implied one.

### 6.1 Ed-hands sub-items — flagged explicitly

1. **🔴 ED-HANDS, BLOCKING, PRE-EXISTING — install the D-127 sudoers fragment and run the cold-credential exercise.** `RUN_STATE.md:975,1055` show this still open; the runbook procedure is `window_runbook.md:562-578`. **This is not new scope and this design does not add to it — but it is the actual gate.** Without it, `sudo -n systemsetup -setusingnetworktime off` prompts or fails, and `CLOCK_PROBE` refuses at `arm_readiness_evidence_t0.py:907-908` on *every* window, attended or not. Nothing in T0-UNATTENDED-01 can be accepted before it. Cost: one `sudo` command plus the three-line exercise.
2. **🔴 ED-HANDS, during the supervised rehearsal — the anchor positive control.** The design asserts ANCHOR moves when the clock is adjusted. Proving that requires *causing* an adjustment, which is privileged. Because the rehearsal is supervised by definition, this is the natural moment: with the machine outside any window, Ed re-enables network time and forces a resync while the collector samples; ANCHOR must move and the author must refuse. Cost: ~2 minutes. **Without it, §2.2's central mechanism is asserted rather than demonstrated** — the unit-level falsifier proves the predicate, not the platform coupling.
3. **🟡 ED / MAGISTRATE — ratify D-127.1 and this evidence class.** Per CLAUDE.local.md rule 11 the lieutenant is forbidden to ratify process rules or amend doctrine; and this design *retires* a check that a prior ruling installed. It needs the seat that can say yes.
4. **⚪ NOT REQUESTED — the `-getusingnetworktime` sudoers addition.** Explicitly recommended **against**. It would enlarge the privileged surface to purchase a field with no readers.

---

## 7. Refusal semantics on probe failure

**Universal disposition: every failure below is a `T0EvidenceAuthoringError` with `kind="CLOCK_ATTESTATION"`, which aborts authoring before any evidence namespace is published** (the existing behaviour asserted by `tests/test_arm_readiness_evidence_t0.py:1170-1172`: neither the sources nor the evidence directory exists after a refusal). There is no degraded mode, no partial receipt, and no path by which a clock failure yields a GO.

| Failure | Disposition |
|---|---|
| all three servers exit non-zero (no network / DNS down) | **REFUSE** — no reference, no GO |
| exactly one server answers | **REFUSE** — quorum is 2; a single source cannot be cross-checked |
| two answer, intervals disjoint | **REFUSE** — the sources contradict; one is broken |
| quorum fine, worst-case bound > 0.5 s | **REFUSE** — clock wrong; pinning would bake the error into the window |
| `sntp` missing / not executable | **REFUSE** — `_fresh_probe` wraps it as underivable |
| probe exceeds 45 s and is SIGKILLed (`:396-415`) | **REFUSE** — reported as execution failure |
| anchor delta > 5 ms | **REFUSE** — something stepped the clock |
| T-0 span < 600 s | **REFUSE** — detector below sensitivity; a pass would be meaningless |
| anchor read skew > 1 ms | **REFUSE** — sampler unreliable |
| boot session changed | **REFUSE** — anchor arithmetic invalid across reboot |
| `clock-reference.json` missing/non-canonical | **REFUSE**, `evidence_author_t0_clock_reference_missing` |

**Retry policy, and its boundary with D-078.** `sntp`'s five internal retries per invocation are the *only* retry (measured §2.1). The author does **not** re-invoke a failed probe, and the runner does **not** re-run a refused T-0. D-078's no-retry discipline governs *refused captures* — "a refused capture ends that lane with diagnosis, never re-arm-and-hope" (D-149 condition 5) — and a T-0 refusal precedes any capture, so no measurement lane has been consumed; the correct state is **idle, unarmed, diagnosable**, which r4-4 already names a safe state. But the temptation to "just run it again tonight" is exactly the sunk-cost continuation rule 11 exists to stop, so:

> **Operational rule (proposed, binds the unattended runner):** two consecutive T-0 refusals with the **same reason signature** are a structural signal, and the next spend is a **consult, not a third attempt** — CLAUDE.local.md rule 11's standing escalation trigger, applied here. The runner records the signature in the window custody record and stops scheduling that lane.

**Availability cost, stated plainly, because it is the real price of this design:** T-0 now depends on reaching a public time server. A domestic internet outage at 02:00 refuses the night. Mitigations inside fail-closed: three servers across three independent operators, DNS-resolved (so a single IP change does not strand us), 2 s timeout each, ~10 s worst case per server. Mitigation *rejected*: carrying forward an earlier reference sample plus an assumed drift rate (§8, alternative 3).

---

## 8. Zero-operator supervised rehearsal — acceptance design

The kernel's acceptance line — "A supervised rehearsal window completes end-to-end with zero operator actions at T-0 and a valid GO receipt" (`state_kernel.json:3311`) — is currently the *entire* specification of a term used nowhere else in the repo; no protocol, no criteria. It needs a definition before it can be met, and the definition must be **mechanically checkable**, because "nobody touched it" is precisely the kind of claim that cannot be re-verified later.

### 8.1 Definitions, built before use

- **Supervised** — Ed (or the lieutenant) is *watching* and may abort, but performs **no action that the T-0 sequence consumes**. Supervision is an abort capability, not an input. This is what makes it the right moment for the privileged positive control (§6.1 item 2), which happens *outside* the T-0 sequence.
- **Zero operator actions at T-0** — from the first governed step to the emission of the GO receipt: no prompt is answered, no capture carries an operator-supplied value, and no local human input device is used. Ed's terminal-review attestation and step-6 byte confirmation are **outside** T-0 (r4-3 places them before the evidence head) and are unaffected.

### 8.2 The three mechanical instruments (this is the part that must not be an honour system)

1. **stdin closure.** Run the entire T-0 sequence with `stdin` bound to `/dev/null`. §5.3 removes every `prompt(` from the ceremony; if any survived, it raises the existing EOF refusal (`capture_t0_step.py:545-549`) rather than hanging. **A surviving operator prompt becomes a loud refusal instead of a silent overnight stall** — this instrument is worth having even after the prompts are gone, precisely because it converts a regression into a failure.
2. **Receipt census.** Assert over the emitted receipts: no fact for `clock.correct_and_prior_state.v1` carries `source_kind == "OPERATOR_ATTESTATION"`; no capture's `argv[0] == "operator-interactive"`; no receipt anywhere in the T-0 set carries an OPERATOR_ATTESTATION source. (The third is broader than the row and is the one that catches a *different* operator dependency creeping back in.)
3. **HID idle witness.** `ioreg -c IOHIDSystem` exposes `HIDIdleTime` in nanoseconds since the last local keyboard/trackpad/mouse input, non-privileged — verified live today (`HIDIdleTime_ns=520602887901708`, i.e. ~6.0 days of no physical input on this machine, which is itself a fair picture of how it is operated). The repo already models this exact command in its environment tests (`tests/test_environment.py:52`). **Acceptance: `HIDIdleTime` sampled at authoring ≥ the T-0 span.** That is direct machine evidence that no human touched the machine for the entire sequence.
   *Boundary, stated because the instrument must not be over-read:* `HIDIdleTime` sees local HID only. A human typing over SSH would not move it. That gap is closed by (1) and (2) for anything the evidence consumes, by A1 for anything deliberate, and by the human supervisor for this one rehearsal.

### 8.3 Acceptance criteria (all must hold)

| # | Criterion | Instrument |
|---|---|---|
| A1 | Full T-0 sequence completes with `stdin=/dev/null`, no prompt, no hang | §8.2(1) |
| A2 | Zero OPERATOR_ATTESTATION facts in the T-0 receipt set; zero `operator-interactive` argvs | §8.2(2) |
| A3 | `HIDIdleTime` at authoring ≥ T-0 span | §8.2(3) |
| A4 | `clock.correct_and_prior_state` receipt: `source_kind == "PROBE"`, three gate booleans `True`, and `_predicate_passes` returns `True` against it | direct assertion |
| A5 | Recorded numbers are consistent: `reference_server_count ≥ 2`; `reference_bound_seconds ≤ 0.5`; `anchor_delta_ns ≤ 5e6`; `600e9 ≤ t0_span_ns ≤ 3600e9` | receipt arithmetic |
| A6 | A valid D-149 GO receipt is issued, all five conditions evaluated, per `docs/process/d149-go-receipt-template.md` | template |
| A7 | **Positive control:** with network time re-enabled and a resync forced (Ed's hands, outside T-0), a fresh collector run shows ANCHOR movement and the author **refuses** | §6.1 item 2 |
| A8 | **Negative controls, injected:** each of the nine §3 refusal rules refuses with `kind == "CLOCK_ATTESTATION"` | §5.5 |
| A9 | The window itself completes and its close-out is ordinary — the rehearsal is a *window*, not a dry run | close-out |

**A7 and A8 are the load-bearing ones.** A rehearsal that only shows the happy path proves the code runs, not that the gate gates. A green T-0 with a broken detector is exactly the 2026-07-26 failure mode with better paperwork.

### 8.4 Sequencing, and the honest scope flag

Precondition: §6.1 item 1 installed and exercised. Then S-0-style dry run against scratch custody → the supervised rehearsal window → A7/A8 at the bench → the row's own C-028 gauntlet.

**🔴 Scope flag the row does not currently carry — the runbook still makes the launch Ed's hands.** `docs/phase_2/window_runbook.md:1113-1131` specifies E-10 as "Ed's deliberate physical launch", and `:786-787` states "no automated word performs or authorizes the physical launch". D-149 supersedes that fence *for no-hands windows*, but the runbook text has not moved, and D-127 clause 4's relaunch harness and launchd fallback timer **do not exist in the repository** (no `.plist`, no `launchctl` outside unrelated tests). So: **this work order removes the T-0 *evidence* blocker to an unattended window; it does not remove the *launch* blocker.** For the rehearsal that is fine — a live agent session drives T-0 and exits before capture, which satisfies D-127 clause 2's zero-agent-during-capture rule unchanged. For a genuinely unattended *campaign* it is not, and A9 will make that visible. Recommend registering the runbook amendment + relaunch harness as their own row rather than letting this one quietly acquire them.

---

## 9. Risks

| # | Risk | Severity | Disposition |
|---|---|---|---|
| R1 | Internet outage at T-0 refuses the night (§7) | **medium** | Accepted, fail-closed. 3 independent operators; the existing `quiet_window_clock.sh:74-79` already refuses on the same condition, so this is not a new posture. Escalation after two same-signature refusals. |
| R2 | ANCHOR does not behave as modelled on this XNU version (e.g. `MONOTONIC_RAW` also adjusted) | **high if true** | **Closed only by A7's positive control.** The design measures rather than assumes, but a green rehearsal without A7 would leave this open. Do not accept the row without it. |
| R3 | 5 ms ceiling too tight → false refusals from ordinary jitter | low | Measured noise floor 395 ns over 2.8 s; margin 12 600×. Read-skew rule 4 catches a preempted sampler before it can masquerade as a step. |
| R4 | 0.5 s ceiling too tight for a long-idle machine | low | Measured 40.8 ms worst-case bound today, 12× margin. If sync has been off for days the machine free-runs at ~3.7 ppm ≈ 0.32 s/day (§2.2), so ~1.5 days of free-run would reach the ceiling — and refusing then is *correct*. |
| R5 | Retiring the prior-state read loses restore information | **low — verified nil** | `prior_network_time` has zero readers; restore is `clock.restore_recipe.v1`'s job (`arm_readiness.py:810-814`). Verified by grep, §1. |
| R6 | Three UDP queries at T-0 conflict with the offline posture | low | `OFFLINE_INPUT_INVENTORY`'s `no_network_fetch` (`:1454`) is about *measurement inputs* not being fetched, not about the interface being down; `quiet_window_clock.sh:42` already runs `sntp` at this exact point in the ceremony by design. ~150 bytes ×3, before the 180 s settle, before the chain starts. Should nonetheless be named in the window close-out. |
| R7 | 6 h horizon retained on now-cheap evidence (§3.4) | medium | Disclosed, follow-on row `T0-CLOCK-VOLATILE-01`. Do **not** fold into this row — it collides with `_v4` S-1. |
| R8 | Fix rounds on a nine-rule refusal surface introduce defects | medium | Rule 9 gauntlet: delta re-audit of every fix round; A8 re-run in full after each. |
| R9 | The row's acceptance is met while the campaign still cannot run unattended (launch blocker) | **medium** | §8.4 flag; register the runbook/harness work separately rather than expanding this row. |

---

## 10. Rejected alternatives

1. **Add `-getusingnetworktime` to the D-127 sudoers scope and automate the paste.** Rejected: it buys a tautological boolean and a field with no readers (§1) at the cost of a larger privileged surface and an Ed-hands install; and the r4-6 fence already downgraded it to observability-only, so it could not gate even if installed. *This is the alternative the work order's own framing assumed — it should be explicitly declined, not silently skipped.*
2. **Infer the prior network-time state from anchor drift** (sync on ⇒ adjuster visible). Rejected, **disproven by my own measurement**: with network time on, ANCHOR was stable to ±395 ns over 2.8 s — `timed` corrects episodically, not continuously, so absence of drift proves nothing about the setting. A detector that reads "quiet" on a machine whose sync is on is worse than no detector.
3. **Carry-forward reference: reuse an earlier SNTP sample plus an assumed drift rate when the network is down.** Rejected: it converts a hard measurement into an extrapolation exactly when the measurement failed, and the drift rate is not estimable at T-0 resolution (see 4). Relaxing a gate under the condition that made it fail is the shape of every eaten escalation trigger.
4. **Gate on projected wall error at window close** (measure free-run rate as `offset(R1) − offset(R0)` over the T-0 span, extrapolate). Rejected on arithmetic: the span is ~600 s and the per-sample uncertainty is ~±20 ms, so the implied rate carries ~±33 ppm of noise — larger than the 3.7 ppm being measured. It would also invent a new policy number (max projected error). The existing doctrine already handles it: `quiet_window_clock.sh:106-108` records the pin-time offset as the bound on absolute wall error for the window, and the close-out consumes it.
5. **Write a bespoke NTP client in the author** instead of shelling to `/usr/bin/sntp`. Rejected: `sntp` is a platform binary the repo already depends on (`quiet_window_clock.sh:42`), it reports its own uncertainty (which the intersection rule needs), and its stdout is custodiable verbatim as a probe record. A hand-rolled client is new attack surface, new bug surface, and — for the correctness-interval computation — reimplements what the tool already gives.
6. **Introduce a new evidence kind (e.g. `CLOCK_DISCIPLINE`).** Rejected: `CLOCK_ATTESTATION` already admits `PROBE` (`arm_readiness.py:731`), and "the registry deliberately remains the exact-key row/kind vocabulary; content and source admissibility are derived here" (`arm_readiness.py:723-725`). A new kind would mean registry vocabulary, freshness-class, and lifecycle-assertion changes for zero semantic gain.
7. **Delete the OPERATOR_ATTESTATION branch entirely** ("we're unattended now"). Rejected: it removes the attended fallback for no benefit, converts a two-source row into a single-source one, and would strand any already-custodied attended receipt. §5.1 keeps the operator path byte-identical in strictness.
8. **Publish the T-0 anchor for the window close-out to re-check** (proving no step across the whole 3.5 h capture, not just T-0). *Not rejected — deferred.* It is genuinely the strongest available extension, but no close-out consumer exists today, and a field nobody refuses on is prose. The raw anchor values are custodied in the probe records regardless, so building the consumer later costs nothing retroactively. Register as `WINDOW-ANCHOR-CLOSEOUT-01`.

---

## 11. Summary of what lands

- **No new privileged command. No new evidence kind. No registry change.** The `PROBE` hook was already open at `arm_readiness.py:731`.
- One source-discriminated predicate branch (`arm_readiness.py`, ~12 lines, mirroring the `t0.background_quiet.v1` template that already sits ten lines away).
- One rewritten derivation (`_derive_clock_attestation`), source kind `OPERATOR_ATTESTATION` → `PROBE` at `:885`.
- One new governed T-0 step and collector; **two operator prompts deleted; the ceremony script left with no stdin read at all.**
- Nine refusal rules, all fail-closed, all defect-shaped-tested; every value boolean is a gate, every value number is a recomputable derivation input.
- **Ed-hands: the pre-existing D-127 install/exercise (blocking, not new), the ~2-minute anchor positive control during the supervised rehearsal, and ratification of D-127.1.**
- **Flagged as outside this row:** the runbook's E-10 "Ed's hands" launch text and D-127 clause 4's unbuilt relaunch harness — the *launch* blocker to unattended campaigns, distinct from the *evidence* blocker this row removes.
