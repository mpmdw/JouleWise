# R12 triage-packet handoff — 2026-11-08

Branch: `align/2026-11-08-triage-packet`, initially clean at
`05b6d04cb` (`origin/align/2026-11-08-v4-r11`). Local commit only; no push.
Authority: task brief, protocol R12 B1–B3/current fixed-eight rule, and
`origin/align/2026-11-08-v4-opus-cold:docs/align/squeeze/fanout/v4-opus-cold-review.md`
MED-2a/MED-2b (also its L2/L3/L7 packet provenance findings).

Implemented a production off-MBP packet command with explicit committed record
and series input inventories, documented source projections and an
`--emit-triage-template`. Ten packet checks derive from authoritative source
artifacts, three remain current arm observations, and calibration derives from
authenticated per-window roster/capture/exclusion history. No check accepts an
operator-supplied triage pass. Record commit/digest, source digests, raw capture
identities, all 14 source owners and refusal bases are retained.

The command authenticates small exported blobs byte-for-byte in Git. Large raw
captures can instead remain in custody: their committed locator/digest/length
metadata is retained and explicitly labelled `committed_digest_inventory_only`.
Those locators are never opened or statted. It does not claim to have rehashed
opaque raw bytes. Push proof is ancestry from an explicit local remote-tracking
ref, not a network check. Git lazy fetching is disabled.

The fixed-eight predicate accepts a `type=lead_ruling` row with unique
`ruling_id` and `after_window` bound to the current two-zero-capture tail. It
resets only the trailing refusal latch; both attempts, counts, target and cap
remain. Historical KM003C gaps are tabulated without vetoing rails eligibility;
live samples/clock evidence must still exist. Quiet/meter observations expire,
and the consumer rechecks expiry at arm time. The persisted arm record retains
the exact packet bytes as base64, their SHA-256 and record commit.

Changed files:

* `scripts/align_v4_next_arm_packet.py`: builder, Git/source authentication, template, CLI.
* `joulewise/align/apple/v4_cadence.py`: additive ruling rows, observation expiry, MED-2b wording; fixed eight preserved.
* `scripts/align_v4_session.py`: retain packet bytes/hash/commit; use the arm clock for triage expiry.
* `tests/align/test_v4_next_arm_packet.py`: synthetic repositories and mock hardware only.
* `docs/align/next_arm_packet.md`: complete input contract, command and per-entry refusal map.
* `docs/align/pilot_protocol_v4.md`: builder pointer and MED-2a/MED-2b wire alignment.
* This report. No coordination-state, kernel, decision-log or generated-state-test edits.

Verification (modules run sequentially):

* `python3.13 -B -m unittest tests.align.test_v4_next_arm_packet`: **19 passed**, 55.389 s (final empty-marker replay).
* `python3.13 -B -m unittest tests.align.test_v4_cadence`: **16 passed**, 0.004 s.
* `python3.13 -B -m unittest tests.align.test_v4_registration`: **20 passed**, 19.433 s.
* `python3.13 -B -m unittest tests.align.test_v4_executed_closure`: **2 passed**, 3.124 s.
* `python3.13 -B -m unittest tests.align.test_protocol_v4_doc`: **6 passed**, 0.737 s.
* Focused `python3.13 -B -m compileall -q` over the four changed Python files: passed.
* `git diff --cached --check`: passed. Final targeted total: **63 tests passed**.

The new tests cover a passing W1 record, all 14 individual refusal paths,
R1→W1 N/A handling, exact native empty courier-marker custody, raw digest mismatch,
dirty-tree isolation, missing/unsafe/symlink sources, commit bindings, meter gaps,
quiet/meter freshness, changed-code desk requirements, eligibility/X5 adjudication,
two zero-capture records plus the retained lead ruling, packet expiry, exact arm
packet retention, fail-closed templates and exclusive output creation.

Earlier iterations: one refusal-message assertion failed because the last-passed
state was checked before the failed current desk; fixed by checking the current
desk first. Intermediate packet runs passed at 15, 17 and 19 tests. Two initial
test invocations were interrupted (exit 130); one had briefly overlapped another
test invocation. Subsequent module runs were sequential. The initial repeated-Git
reads were cached. Final source review found native `courier.sent` is created by
`touch`, so the fixture and builder now accept its authenticated empty blob.

Limits and exact next step:

* Software validation is synthetic, **PROVISIONAL for native readiness**. No real
  R1/W1 record, study outcome, sealed directory or measurement bytes were opened.
  No network, model downloads, MLX execution, full suite, B5 pipeline, hardware
  probe, campaign or quiet-window collection was run. The long analysis job was
  not inspected or touched.
* The record/series inventory and observation projections are new input contracts.
  There is no automatic native export adapter in this change. The custody/series
  lane must emit these from its actual exports, including R1 coverage/fault/meter
  tabulations and exhaustive installed code/config inventories. In particular,
  this command does not substitute an R1 slot aggregate for missing fault evidence.
* Before registration, integrate the pending cold fixes against the documented
  ruling row wire while preserving the current fixed-eight implementation (the
  cold-review branch itself predates that change). Lead owns the actual ruling ids,
  quiet/freshness policy, next roster, pool admission and any thermal remedy.
* Lead/native follow-up outside this sandbox: on the off-MBP desk, build from a real
  committed R1/W1 export and inspect every source binding/refusal; then exercise
  the guarded native arm in a clean lead-controlled session, confirming current
  hardware checks, expiry and persisted packet SHA. No MLX code changed here and
  no new MLX-native unit tests are required by this patch. Full WP22/native gates
  remain with their owning lanes; this report does not discharge them.
