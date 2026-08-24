## 1. **Replacement evidence class.**

Adopt a successor row, `clock.correct_and_pinned_state`, with predicate/fact ID `clock.correct_and_pinned_state.v1`, evidence kind `CLOCK_ATTESTATION`, and `source_kind: "PROBE"`. Do not silently reinterpret `clock.correct_and_prior_state.v1`: its name and required field `prior_systemsetup_state_captured` describe historical operator evidence. Preserve that predicate only for authenticating historical packs and receipts.

The unattended E-4 replacement writes canonical `clock-attestation.json` with this exact logical shape:

```json
{
  "schema_version": "joulewise.arm_readiness_t0_clock_machine_attestation.v1",
  "attestation_id": "machine-clock-<24 lowercase hex>",
  "producer": "scripts/capture_t0_step.py",
  "sample_policy_id": "clock.machine_reference.time_apple_3x_t5_quorum2.v1",
  "reference_source": "time.apple.com",
  "head_commit": "<40 lowercase hex>",
  "head_tree_oid": "<40 lowercase hex>",
  "pack_sha256": "<64 lowercase hex>",
  "boot_session_id": "<kern.bootsessionuuid>",
  "started_monotonic_ns": 0,
  "finished_monotonic_ns": 0,
  "samples": [
    {
      "sequence": 1,
      "argv": ["/usr/bin/sntp", "-t", "5", "time.apple.com"],
      "cwd": "<absolute reviewed repository>",
      "exit_code": 0,
      "stdout": "<raw bytes decoded with replacement>",
      "stderr": "<raw bytes decoded with replacement>",
      "started_monotonic_ns": 0,
      "finished_monotonic_ns": 0,
      "started_wall_time_unix_ns": 0,
      "finished_wall_time_unix_ns": 0,
      "offset_ns": 0,
      "uncertainty_ns": 0
    }
  ]
}
```

`attestation_id` is `machine-clock-` plus the first 24 hex characters of SHA-256 over the canonical object with `attestation_id` omitted. The evidence author recomputes it; it is carried into the source document’s `derivation.attestation_id`, preserving the existing attestation-ID-to-source-hash plumbing without claiming a human observer.

The probes are:

- Three predeclared, non-mutating invocations of `/usr/bin/sntp -t 5 time.apple.com`, without a shell, stdin, or inherited environment beyond the existing governed environment. These are one three-leg probe, not retries. Each subprocess has a 10-second hard timeout and the batch a 30-second ceiling.

- `/usr/sbin/sysctl -n kern.bootsessionuuid` before capture, at evidence authoring, and again before publication, as the existing author already requires.

- E-5’s unchanged `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`, followed by the author’s existing fresh re-execution of that exact command. Success requires exit code zero, empty stderr, and one normalized stdout line exactly `setUsingNetworkTime: Off`. This actively establishes the relevant postcondition; no privileged `get` is used.

- Bracketed Python `time.time_ns()` and `time.monotonic_ns()` reads immediately around each SNTP command and one final pair after the fresh `systemsetup off` enforcement. Both endpoints are recorded; the author rejects reversed or implausible ordering.

Every nonempty successful SNTP output line must match the existing Darwin shape:

```text
<signed decimal offset> +/- <nonnegative decimal uncertainty> time.apple.com <IPv4-or-IPv6 address>
```

Parsing uses exact decimal arithmetic and converts to integer nanoseconds; NaN, infinity, extra text, negative uncertainty, malformed addresses, or an unexpected hostname are invalid. At least two of the three command legs must produce valid samples. A transport failure in one leg is recorded but may be tolerated; fewer than two valid legs refuses. Every syntactically valid result participates—there is no best-result selection.

For valid sample `i`, the author computes:

```text
continuity_i =
    abs((final_wall_ns - sample_finished_wall_ns)
        - (final_monotonic_ns - sample_finished_monotonic_ns))

current_bound_i =
    abs(offset_ns_i)
    + uncertainty_ns_i
    + continuity_i
    + clock_read_bracket_width_ns

comparison_bound_ns = max(current_bound_i)
```

Admission requires `comparison_bound_ns <= 500_000_000` (0.5 seconds), the already-governed pinning threshold in `quiet_window_clock.sh`. This conservative current bound replaces the operator path’s `comparison_delta_seconds <= 2.0`: it includes reference uncertainty and any wall-versus-monotonic movement between the external observation and final T-0 sampling.

The emitted fact is:

```json
{
  "machine_clock_attestation": true,
  "independent_reference_quorum": true,
  "reference_source": "time.apple.com",
  "requested_probe_count": 3,
  "valid_probe_count": 2,
  "comparison_bound_ns": 0,
  "comparison_limit_ns": 500000000,
  "comparison_within_limit": true,
  "clock_continuity_delta_ns": 0,
  "network_time_off_enforced": true,
  "network_time_enforcement_count": 2,
  "boot_session_match": true
}
```

The existing T-0 source envelope remains `joulewise.arm_readiness_t0_evidence_source.v1`, bound to HEAD, tree, pack SHA-256, boot UUID, input hashes, raw probes, facts, and derivation. Its input artifacts are the machine `clock-attestation.json` and E-5 `clock-disable.json`; its probes include the fresh off-enforcement result. The receipt remains the existing evidence-receipt schema, with kind `CLOCK_ATTESTATION`, fact ID `clock.correct_and_pinned_state.v1`, and `source_kind: "PROBE"`.

Freshness is fail-closed:

- The reference capture must be on the current boot, correctly ordered before E-5, and no more than 3,600 seconds old when authored.
- The final wall/monotonic pair must be taken after fresh off-enforcement and no more than 5 seconds before the receipt validity origin.
- `CLOCK_ATTESTATION` receives the 1,200-second volatile horizon, not the current author’s six-hour procedural horizon.
- The existing 300-second arm-to-consume budget must remain available at ARM evaluation.
- HEAD, tree, pack, input hashes, and boot UUID are rechecked before atomic publication.

Under D-139-A1 this is stronger than the operator’s “yes”: it removes manual timestamp latency and transcription, retains raw reference output and uncertainty, tightens 2 seconds to a conservative 0.5-second bound, detects wall/monotonic movement across the disable-and-dwell sequence, actively establishes Off twice, and is mechanically bound to the boot, pack, checkout, and capture order. It does not claim resistance to malicious local code, forged NTP traffic, or a hostile time server; those are outside the ruled threat model.

## 2. **D-127 scope amendment text.**

> **D-127 amendment — T0-UNATTENDED-01 machine clock evidence.** CLOCK_ATTESTATION for successor unattended windows may be authored from the governed, unprivileged `/usr/bin/sntp -t 5 time.apple.com` reference probe, local wall/monotonic samples, current boot-session identity, and the already-authorized exact `/usr/sbin/systemsetup -setusingnetworktime off` vector. The successful exact off vector establishes the admission-relevant pinned-state postcondition; historical prior-state observation is not an admission requirement and restoration remains the existing unconditional exact `on` vector. No privileged operation is added. In particular, `/usr/sbin/systemsetup -getusingnetworktime` is not added to the sudoers capability and remains failure-tolerant observability in `quiet_window_clock.sh`; it neither satisfies nor refuses CLOCK_ATTESTATION. The existing exact-path, exact-argv `off`/`on` sudoers fragment remains byte-for-byte unchanged.

No new sudoers line is required.

[ED-HANDS] No new installation is introduced. If the already-installed D-127 `off`/`on` capability ever needs repair or reinstallation, the existing D-115 authenticated installation procedure remains Ed-only; agents must not widen or reinstall it.

## 3. **Code-change shape.**

In `joulewise/arm_readiness_evidence_t0.py`:

- Add the machine-attestation input schema and strict parser beside `_ATTESTATION_SCHEMA`, `_clock_attestation`, and the capture validators.
- Rename the current derivation to an explicitly legacy operator derivation. Preserve it only for historical `clock.correct_and_prior_state.v1` rows and existing-receipt reauthentication.
- Add `_derive_clock_machine_attestation` for `clock.correct_and_pinned_state`. It validates the canonical input, recomputes `attestation_id` and parsed SNTP values, takes the final clock pair, computes the nanosecond bound, consumes the shared fresh off-enforcement probe, and returns `_DerivedRow(..., source_kind="PROBE")`.
- Refactor `_derive_clock_probe` around a cached `_enforce_network_time_off` helper so `CLOCK_PROBE` and the successor `CLOCK_ATTESTATION` share one fresh exact execution and identical raw output.
- Make `_required_rows`, `_DERIVERS`, `_ROW_KIND`, capture-order validation, and the fifteen-row census profile-aware: historical registries select the old row; unattended successors select the new row, never both.
- Move `CLOCK_ATTESTATION` into the 20-minute volatile authoring horizon. Keep boot binding, artifact reauthentication, staged discovery, collision refusal, and atomic publication unchanged.
- Derive the machine clock row last and require receipt issuance within five seconds of its final clock pair.

In `joulewise/arm_readiness.py`:

- Leave `SOURCE_KINDS` and `_EVIDENCE_SOURCE_KINDS["CLOCK_ATTESTATION"]` unchanged; HEAD already admits `PROBE`.
- Retain `clock.correct_and_prior_state.v1 -> CLOCK_ATTESTATION` for historical receipts and add `clock.correct_and_pinned_state.v1 -> CLOCK_ATTESTATION`.
- Add successor content requirements for the fixed booleans and `comparison_limit_ns: 500000000`. Add a predicate-specific relational check requiring non-boolean integers, `2 <= valid_probe_count <= requested_probe_count == 3`, and `0 <= comparison_bound_ns <= comparison_limit_ns`.
- Leave the R1 freshness class as `TIME_BOUND`; only the authoring deadline changes to the approved 20-minute volatile horizon.
- Update the successor row registry/profile to replace the old clock row. Historical registries remain immutable.

In `scripts/capture_t0_step.py`:

- For successor profiles, replace interactive `clock-prior-state` with a noninteractive `clock-attestation` step that executes the fixed three-leg SNTP batch and writes the machine schema. Production must never call `input()`.
- Remove the trusted-clock and pasted-prior-state prompts from the successor route. Keep legacy parsing code private and reachable only when authenticating historical profiles.
- Keep `clock-disable`’s exact `sudo -n systemsetup -setusingnetworktime off` argv. Strengthen `_validate_result` to require the exact Off result line.
- Preserve controlled environment, no shell, stdin isolation, boot checks, canonical no-clobber publication, monotonic ordering, and raw stdout/stderr.
- Do not add any `-getusingnetworktime` execution. `quiet_window_clock.sh::sync_state` remains unchanged and observability-only.

The D-149 receipt template must also point C4 at the successor receipt/source and exact off-enforcement output, rather than a privileged state read. Tests should prove that successor authoring never invokes a prompt or `-getusingnetworktime`, while historical receipts remain authenticatable.

## 4. **Supervised-rehearsal acceptance design.**

Run one complete autonomous rehearsal using the reviewed production binaries and exact D-127 vectors, but dedicated rehearsal identities, roots, ledger, backup destinations, and workload outputs. It must exercise E-4 replacement through E-9, evidence authoring, ARM, verification, capability consumption, foreground launch, the full capture chain, close-out, backups, verdict, and automatic network-time restoration. No rehearsal artifact may enter a claim ledger or later be promoted.

“Supervised” means one named human observer—Ed or the designated lead—watches from a separate device or physically away from the measurement Mac. The observer has no remote shell, polling process, keyboard, mouse, password prompt, or corrective role. From the automated E-4 start until the foreground capture has begun, the observer records only timestamps and whether intervention occurred. During capture, the normal zero-agent fence applies and no agent or observer process remains on the Mac. Evidence is reviewed only after close.

Record in rehearsal custody:

- The full unattended launcher transcript and scheduler/session identity.
- All machine clock input, source, receipt, sidecar, arm, verification, consumption, GO, launch-lineage, capture, backup, close-out, and restore artifacts with SHA-256.
- Raw SNTP and both off-enforcement outputs, parsed bounds, boot UUID checks, and remaining freshness at ARM and consumption.
- Pre-launch and post-close process censuses.
- An observer record naming location/device, observation interval, and `operator_actions_at_t0: 0`.
- Any refusal, stderr, or automatic recovery action, including whether the observer touched nothing.

The GO receipt must begin with:

```text
REHEARSAL — NON-CLAIM — NO PRODUCTION AUTHORITY
receipt_class: T0_UNATTENDED_SUPERVISED_REHEARSAL
claim_eligible: false
acceptance_target: T0-UNATTENDED-01
```

It then carries the ordinary D-149 C1–C5 evidence and `VERDICT: GO`. Its window ID must begin `rehearsal-t0-unattended-`, and its custody root must be outside all production roots. Production consumers must mechanically reject this receipt class; that negative check is part of acceptance.

Pass requires: all five D-149 conditions green; `CLOCK_ATTESTATION` sourced from `PROBE`; comparison bound at most 500,000,000 ns; same boot throughout; at least 300 seconds of evidence lifetime remaining at consumption; zero prompts and zero operator actions; zero agents during capture; a consumed single-use launch capability; full window completion; backups and close-out present; and network time restored automatically. Any intervention, even one that would have made the run succeed, makes the rehearsal fail.

[ED-HANDS] If the rehearsal is intentionally placed after D-150a’s ruled pre-campaign reboot, that already-ruled reboot remains Ed’s action and occurs before unattended T-0 begins. It is not part of the replacement probe.

[ED-HANDS] If automatic restoration with the already-authorized exact `on` vector fails, Ed performs the existing recovery procedure. The rehearsal remains failed; recovery cannot retroactively qualify it.

## 5. **Failure semantics.**

- An SNTP spawn error, timeout, nonzero exit, or malformed output is retained in the attempt’s refusal record. One failed leg may be tolerated only by the predeclared two-of-three quorum. Fewer than two valid legs refuses with `evidence_author_t0_capture_clock_observation_invalid`; no additional query is launched.

- Any syntactically valid sample whose computed current bound causes `comparison_bound_ns > 500000000` refuses with `evidence_author_t0_capture_clock_observation_invalid`. It is never discarded as an outlier.

- A missing machine attestation refuses as `evidence_author_t0_clock_attestation_missing`. Wrong schema, keys, attestation ID, parsed values, ordering, age, checkout/pack identity, or same-boot binding refuses as `evidence_author_t0_clock_attestation_underivable`.

- An E-5 `systemsetup off` nonzero exit refuses as `evidence_author_t0_capture_command_failed`; a zero exit without the exact Off output refuses as `evidence_author_t0_capture_result_invalid`. Failure of the author’s fresh exact enforcement refuses the `CLOCK_PROBE`/authoring set as `evidence_author_t0_clock_probe_underivable`. No evidence namespace is published.

- An input hash changing during derivation refuses as `evidence_author_t0_input_changed`. A boot change before publication uses the same code. Existing namespace mismatches, expired receipts, and insufficient consume lifetime continue to refuse through `evidence_author_t0_existing_stale`, `readiness_record_expired`, or the R1 temporal-budget refusal.

- The optional `quiet_window_clock.sh` `-getusingnetworktime` observation is never an admission input. “Network-time state wrong” for this evidence class means that the exact governed setter cannot establish and report its Off postcondition.

Every refusal writes one append-only diagnostic record containing the window/pack/head/boot identity, failed leg, registered reason code, raw stdout/stderr, timestamps, and `lane_terminated: true`. Partial PASS evidence is never published.

The fixed three-leg reference batch is one attempt, not three retries. Under D-149 condition 5 and D-078, any final refusal ends that window lane. The same capture, window ID, attestation ID, custody namespace, ledger reservation, and launch capability are never reused. A later lane requires a recorded diagnosis and cause disposition, fresh identifiers and custody, and a new ordinary authorization path; “run it again and hope” is forbidden.

## 6. **Risks + rejected alternatives.**

- **Asynchronous operator attestation with a long horizon—rejected.** It remains presence-dependent, can cross a reboot or later clock slew, and says nothing about the state immediately consumed at T-0. Lengthening the horizon removes the very freshness that makes the observation useful.

- **Existing CLOCK_PROBE alone—rejected.** At HEAD it proves only that an exact setter invocation returned zero and labels the state Off. It does not establish that the wall clock was correct before pinning, retain an independent reference comparison, include uncertainty, or detect wall-versus-monotonic movement. It could successfully pin a wrong clock.

- **Adding passwordless `systemsetup -getusingnetworktime`—rejected.** It violates the r4-6 fence, adds privileged surface, and is unnecessary: two exact active Off enforcements provide the relevant postcondition. The existing `get` caller remains observability-only.

- **Single-point failures.** The design relies on Darwin `sntp`, its output parser, DNS/network reachability, and `time.apple.com`; three samples do not remove the shared-server dependency. It also trusts `systemsetup` success/output semantics and Python’s wall/monotonic APIs. A human looking at a separate device did not share all these software components. Raw output custody, exact decimal recomputation, quorum, distinct wall/monotonic checks, source pinning, adversarial parser tests, and the supervised full rehearsal mitigate—but do not eliminate—this common-mode risk.

- **Reference availability.** UDP/NTP loss can refuse an otherwise usable night. Two-of-three fixed quorum limits transient loss without introducing retries or best-result selection. Changing servers or quorum later is a versioned policy change, not a runtime fallback.

- **TOCTOU before T-0.** The external reference occurs before E-5 and the required quiet dwell. The final wall/monotonic comparison carries that reference forward and detects steps or slews; fresh Off enforcement, same-boot binding, the 20-minute receipt deadline, and the five-minute consume budget bound the remaining gap. A clock jump after the final sample and before launch can still escape this row; member-level time-anchor checks remain mandatory and would refuse affected capture evidence.

- **Probe traffic.** SNTP and DNS activity can disturb quietness briefly. The reference batch therefore runs before network-time disable and before the existing minimum 600-second clean dwell. Moving it after the dwell is rejected because it would invalidate the quiet interval; omitting the dwell is rejected because it would exchange evidence freshness for environmental contamination.

- **Silent semantic reuse of `clock.correct_and_prior_state.v1`—rejected.** Setting `prior_systemsetup_state_captured: true` without a prior read would be false evidence. The versioned successor makes the changed claim explicit while preserving historical authentication.