## 1. AGREEMENTS

- Co-sign: no new privileged command or sudoers line is needed; `-getusingnetworktime` stays observability-only.
- Co-sign: retain `CLOCK_ATTESTATION`, use `source_kind: PROBE`, and exploit the already-open admissibility hook.
- Co-sign: retire the information-free prior-state requirement from the PROBE branch while preserving historical operator receipts.
- Co-sign: reuse the governed 0.5-second pinning ceiling and capture raw SNTP outputs, uncertainty, argv, peer address, timing, boot, HEAD, and pack identity.
- Co-sign: require both a pre-disable correctness observation and an author-time correctness observation; they protect different boundaries.
- Co-sign: all failures are fail-closed, publish no partial PASS namespace, and cannot trigger re-arm-and-hope.
- Co-sign: the anchor is a falsifier only; a green anchor must never be described as proof that the clock is quiet.
- Co-sign: the rehearsal must exercise a complete window, not merely unit tests or an ARM dry run.
- Co-sign: the attended operator branch should remain available for historical authentication, but successor unattended execution must contain no prompt or operator-supplied value.

## 2. DISAGREEMENTS (with grounds)

**(a) SERVER TOPOLOGY — VERDICT: adopt Opus’s diverse topology, with stricter predeclaration and interpretation.**

Three Apple-only legs provide transport redundancy but no reference-source diversity; a shared Apple service or implementation drift can make all three agree incorrectly. Under D-139-A1, malicious replies are out of model, but correlated operational bugs and drift remain in model, so independent operators add real evidence.

The synthesis should use the fixed, versioned roster `time.apple.com`, `pool.ntp.org`, and `time.nist.gov`, one governed invocation per hostname, with:

- No runtime substitution or fallback hostname.
- At least two successful hostname legs.
- All successful, parseable legs included in the intersection; never discard an inconvenient successful result as an outlier.
- The resolved peer address and raw line recorded for every leg.
- A failed NIST leg tolerated by the two-of-three rule; no special retry beyond `sntp`’s fixed internal behavior.
- `pool.ntp.org` described honestly as a rotating volunteer population, not a stable server identity. Its runtime peer is evidence-bearing.
- Rehearsal qualification of the exact roster, parser, timeout, and expected NIST request cadence.

NIST rate limiting and Pool rotation are availability/reproducibility costs, but they fail closed and are cushioned by quorum. They do not outweigh the common-mode weakness of Apple-only sampling.

One terminology correction: Darwin `sntp`’s `+/-` value is an uncertainty estimate, not a certified correctness bound. The intersection is therefore an **agreement-interval gate**, not a formal Marzullo correctness proof. Its arithmetic is sound as a conservative operational screen, but the synthesis should not claim more metrological authority than the tool supplies.

**(b) ANCHOR FALSIFIER — VERDICT: adopt it, and let it subsume my original continuity term.**

`CLOCK_REALTIME − CLOCK_MONOTONIC_RAW` is available on this Darwin/Python platform at HEAD (`CLOCK_MONOTONIC_RAW == 4`). The physics and arithmetic are sound:

- `5 ms / 600 s = 8.33 ppm`.
- 110 ppm produces 66 ms over 600 seconds, 13.2 times the threshold.
- 158 ppm produces 94.8 ms, 19.0 times the threshold.

It would therefore refuse the recorded incident-class slews if they persist long enough to produce their observed 5.544/7.769 ms excursions.

My original `continuity_i` used ordinary `time.monotonic_ns()`. The bench’s long-baseline observation—ordinary `CLOCK_MONOTONIC` tracking `CLOCK_REALTIME − boottime` while RAW differs—shows that ordinary monotonic can share discipline with wall time on this platform. A wall-vs-ordinary-monotonic subtraction may therefore cancel the very adjustment being sought. That term should not survive independently.

The merged design should carry:

- R0 diverse SNTP before disable: safe-to-pin absolute correctness.
- R1 diverse SNTP at authoring: current absolute correctness.
- One RAW anchor delta across the ≥600-second T-0 sequence: intermediate step/slew falsifier.
- No second wall/ordinary-monotonic continuity gate.

The RAW anchor does not replace SNTP: it cannot certify absolute UTC correctness or detect common oscillator error. SNTP does not replace the anchor: two correct endpoint readings could miss an intermediate adjustment that later unwound. They are complementary.

Two qualifications should survive synthesis:

- The reported ±395 ns is an observed five-sample range, not a characterized “noise floor.” It supports ample margin but should not be published as a calibrated floor.
- Platform coupling needs the proposed supervised positive control. A passing anchor alone proves nothing; the rehearsal must demonstrate that a controlled wall-clock adjustment moves the anchor and crosses the refusal path when the movement exceeds 5 ms.

**(c) REHEARSAL MECHANICS — VERDICT: merge both designs; neither set is sufficient alone.**

Opus’s instruments establish that no operator input was consumed. My receipt class prevents a successful rehearsal artifact from acquiring production authority. The merged acceptance table should be:

| Gate | Mechanical evidence | Pass condition |
|---|---|---|
| Noninteractive execution | Top-level T-0 stdin and every governed subprocess stdin bound to `/dev/null` | Complete sequence with no EOF refusal, prompt, or hang |
| Receipt/source census | Census of every T-0 receipt, source, and command capture | Zero `OPERATOR_ATTESTATION` facts; zero `operator-interactive` argv; clock fact is `PROBE` |
| Local-input witness | Strictly parsed `IOHIDSystem/HIDIdleTime` sampled at authoring | `HIDIdleTime >= measured T-0 span`; absent/ambiguous output fails rehearsal |
| Clock mechanics | Raw R0/R1 server records, intersection arithmetic, RAW anchor endpoints | Quorum/intersection/0.5-second gates pass; `600 s <= span <= 3600 s`; anchor delta ≤5 ms |
| D-149 evaluation | Ordinary C1–C5 receipt evidence and hashes | `VERDICT: GO`, with all five conditions mechanically green |
| Rehearsal separation | Mandatory receipt fields and dedicated custody/ledger/roots | `receipt_class: T0_UNATTENDED_SUPERVISED_REHEARSAL`, `claim_eligible: false`, rehearsal-prefixed window ID |
| Production rejection | Feed the valid rehearsal receipt to the production consumer | Mechanical refusal specifically because rehearsal receipts carry no production authority |
| Zero-agent capture | Pre-launch census and launch/exit lineage | Agent exits before capture; no agent process during capture |
| Full lifecycle | Launch, consumption, capture, backups, close-out, restore records | Complete end-to-end rehearsal window; no intervention |
| Falsifier controls | RAW-anchor positive control plus injected boundary tests | `5 ms + 1 ns` refuses; `5 ms − 1 ns` passes; platform adjustment visibly moves RAW anchor |

The supervisor’s observation record remains useful but additive. `/dev/null`, receipt census, and HID idle are the mechanical proof. HID idle covers local devices only; remote interactive input is instead constrained by closed stdin, source/capture census, process evidence, and D-139-A1.

## 3. LAUNCH-BLOCKER SEPARATION

**VERDICT: co-sign; it is a separate blocker and must become a separate dependency.**

At HEAD, the runbook still says E-10 is “Ed’s deliberate physical launch” and that no automated word performs or authorizes that launch. D-149 supplies authority for no-hands GO; it does not implement a scheduler or launcher.

D-127 clause 4 separately specifies fresh-session relaunch, liveness proof, bounded retries, and an independent launchd fallback timer. Repository inspection shows the policy text but no corresponding launchd artifact or completed fallback mechanism. Removing operator clock input therefore does not, by itself, make the campaign scheduler self-launching or self-recovering.

T0-UNATTENDED-01 should own only:

- Machine-authored clock evidence.
- Removal of T-0 prompts.
- The supervised zero-operator rehearsal.
- The mechanically scoped D-149 GO receipt.

A separate row—e.g. `UNATTENDED-LAUNCH-01`—should own:

- The E-10 runbook amendment.
- Autonomous initial foreground launch.
- Verified post-window relaunch.
- Liveness proof and bounded retry policy.
- Independent launchd fallback.
- Zero-agent-during-capture preservation.

Production campaign windows should depend on both rows. Absorbing the launch harness here would conflate evidence semantics with process lifecycle, expand the gauntlet unexpectedly, and make a green clock rehearsal appear to prove machinery it never exercised.

## 4. HORIZON NOTE — ATTACK IF WRONG

**VERDICT: the coordinator is correct; retract my 1,200-second receipt-horizon proposal.**

D-150 item 2 explicitly rules that the two T-0 kinds remain at six hours, and HEAD stamps `CLOCK_ATTESTATION` with `r1.time_bound.procedural_6h.v1`. Moving it to the 20-minute tier inside T0-UNATTENDED-01 would contradict a specific Ed ruling, not merely tighten an implementation default.

Mechanical SNTP recency should instead be enforced at **evidence issuance**, without covertly shortening the ruled consumption horizon:

- R0 pre-disable reference: same boot; ordered before E-5; `600_000_000_000 <= author_anchor_raw_ns − R0_anchor_raw_ns <= 3_600_000_000_000`.
- R1 authoring batch: total batch duration ≤30,000,000,000 ns.
- R1 completion to the receipt validity origin: ≤5,000,000,000 ns.
- Therefore the oldest participating R1 result is at most 35 seconds old at issuance.
- The receipt’s deadline must equal that recorded validity origin plus exactly `21_600_000_000_000` ns.
- RAW anchor delta must be ≤5,000,000 ns, with both samples on the same boot and read skew ≤1,000,000 ns.

These must be numeric predicate relations, not another hard-coded `True` field. The fact should carry R0/R1 start/end monotonic stamps, RAW anchor stamps, the validity origin, and the six-hour deadline; `_predicate_passes` recomputes the inequalities and deadline relation.

The six-hour rule then honestly means what D-150 authorized: evidence can be consumed up to six hours after a demonstrably fresh issuance. If synthesis instead wants SNTP to be at most minutes old **at consumption**, that is an effective horizon reduction and requires a new ruling; it must not be smuggled in as “predicate recency.”