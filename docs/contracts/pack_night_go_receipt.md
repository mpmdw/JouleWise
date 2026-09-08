# Pack-night GO receipt — D-176 seat-1 contract draft

Status: **DRAFT for the Opus contract refuter; wire details in §8 need a lead
ruling before this text is sufficient to implement.** No code or live gate is
closed by this document. D-176 is adopted by cold gate + Opus refuter + magistrate
synthesis 2026-09-08 (Ed may veto).

The ruling of record is
[`13-magistrate-synthesis.md`](../process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/13-magistrate-synthesis.md).
Its six decisions select the judge's
[`10-coldgate-fable-ruling.md`](../process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/10-coldgate-fable-ruling.md)
text and the expressly adopted amendments from
[`11-coldgate-opus-refutation.md`](../process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/11-coldgate-opus-refutation.md).
Those sources govern; this draft does not adopt the refuter's rejected schema
name or environment route.

## 1. Terms and production order

A **pack** is the frozen set of inputs for one governed measurement plan. A
**pack night** uses receipt class `TRANSACTION_PACK`, including the G2-b
shakedown and the isolated T-0 rehearsal. **ARM** is the authenticated, perishable
readiness authorization for that pack. **T-0** is the final readiness sequence
before launch. **GO** is permission to consume the already verified ARM once,
only after conditions C1–C5 pass. **Custody** means the retained on-disk evidence
location used to authenticate and replay a transaction. A **digest** is a SHA-256
hash of the actual file bytes; re-digest means read those bytes again and compute
the hash again, not trust a caller's previously parsed object.

A **monotonic** timestamp is elapsed nanoseconds on the same boot session's
ordinary monotonic clock. It is not UTC and not `CLOCK_MONOTONIC_RAW`. A
**consumption record** is the durable record written atomically when the one-use
ARM launch capability is spent. The **linearization point** is that single
successful no-clobber (`O_EXCL`) write: racing or replayed callers cannot both
spend the same ARM. **hC** is the digest of the step-6 table already confirmed in
the retained transcript, not a digest freshly adopted as authority at T-0.

The night driver (`scripts/run_night.py`) is the only GO producer. Its first act
remains the governed agent census, a process-list check for agent presence. Pack
preparation precedes ARM verification and does not receive premature measurement
GO. After ARM verification, the driver authenticates the transaction authorization,
confirmation record, T-0 evidence, boot/clock evidence, quiet census and no-retry
state, evaluates C1–C5, and only then produces
`joulewise.pack_night_go_receipt.v1`. The launch consumer is
`joulewise/arm_readiness.py::_consume_launch_capability`; the launcher is
`scripts/launch_window.py`; replay is
`joulewise/arm_readiness.py::verify_consumed_launch`.

In the tables, **producer** means the night driver after ARM verify; **consumer**
means the launch-capability callee's own read and authentication; **replay** means
`verify_consumed_launch` authenticating the retained record and its referenced
bytes again. A binding must equal independently authenticated launch context;
copying the same untrusted label twice is not a binding check.

## 2. Exact GO schema and bindings

The following is the judge's exact top-level key list, expanded into a table.
Every key is required. The schema is `joulewise.pack_night_go_receipt.v1`; the
legacy `joulewise.t0_unattended_d149_go_receipt.v1` is RETIRED and REFUSED, never
grandfathered, including at rehearsal gate G5. No `receipt_id`, `path` or
`window_id` key is silently added to this list; §8 identifies the unresolved
GO-reference wire contract. The window identity is authenticated through the pack
and existing launch context, and controls the rehearsal-purpose predicate in §6.

| Key | Type | Bound-to | Checked-where |
|---|---|---|---|
| `schema_version` | string | `joulewise.pack_night_go_receipt.v1` exactly | Producer, consumer, replay; G5 |
| `receipt_class` | string | `TRANSACTION_PACK` exactly | Producer, consumer, replay; G7 refuses rehearsal class |
| `purpose` | string | Authenticated authorization purpose: `G2B_SHAKEDOWN`, `CAMPAIGN_TRANSACTION` or `T0_REHEARSAL` | Producer, consumer, replay; launch-realization recheck and L10 |
| `plan_id` | string | Authenticated pack-night plan and pack identity | Producer, consumer, replay |
| `pack_id` | string | Authenticated pack identity | Producer, consumer, replay |
| `pack_sha256` | SHA-256 string | Verified frozen pack bytes and authorization's pack digest | Producer, consumer, replay |
| `arm_receipt` | object | Verified ARM identity, digest and expiry; exact nested keys below | Producer, consumer, replay |
| `boot_session_id` | string | Verified ARM and current launch boot session | Producer, consumer, live replay |
| `t0_evidence` | array of objects | Fifteen ARM_ONLY evidence receipts plus capture-step records; each path and digest authenticated | Producer, consumer, replay; G2/G5 |
| `launch_manifest_sha256` | SHA-256 string | Authenticated launch manifest bytes already held by launch consumer | Producer, consumer, replay |
| `window_environment_sha256` | SHA-256 string | Authenticated `window.env` bytes already held by launch consumer | Producer, consumer, replay |
| `window_chain_sha256` | SHA-256 string | Authenticated chain bytes, also equal to authorization's permitted chain digest | Producer, consumer, replay |
| `repo_head` | string | Reviewed repository revision in authenticated plan/launch context | Producer, consumer, replay |
| `measurement_root` | path string | Pinned measurement checkout in authenticated plan | Producer, consumer, replay |
| `measurement_head` | string | Pinned measurement checkout revision in authenticated plan | Producer, consumer, replay |
| `confirmation_record_sha256` | SHA-256 string | Actual step-6 confirmation-record bytes and the plan's bound digest | Producer, consumer, replay |
| `authorization_record_sha256` | SHA-256 string | Actual transaction-authorization bytes and the plan's bound digest | Producer, consumer, replay |
| `census` | object | Governed agent-census invocation, result and time; exact nested keys below | Producer, consumer, replay; G8 |
| `issued_epoch_s` | number | Recorded wall-clock issuance time in seconds; does not replace monotonic validity | Producer, consumer, replay |
| `issued_monotonic_ns` | integer | Issuance on the authenticated boot session's ordinary monotonic clock | Producer, consumer, live replay |
| `valid_until_monotonic_ns` | integer | No later than `arm_receipt.valid_until_monotonic_ns` | Producer, consumer, live replay |
| `conditions` | array of objects | C1–C5, each with condition id, status and authenticated evidence | Producer evaluates; consumer and replay require all five PASS; G5 recomputes |
| `verdict` | string | `GO` required for consumption | Producer, consumer, replay |

Nested key lists are also the judge's lists:

| Object | Required keys and types | Binding and check |
|---|---|---|
| `arm_receipt` | `receipt_id`: string; `sha256`: SHA-256 string; `valid_until_monotonic_ns`: integer | Equal the ARM receipt that itself replays to PASS/GO in custody; GO expiry cannot exceed ARM expiry |
| Each `t0_evidence` item | `path`: path string; `sha256`: SHA-256 string | Re-read each retained receipt/capture-step record and compare its digest; authenticate its pack/attempt membership and underlying evidence |
| `census` | `argv`: array of strings; `exit_code`: integer; `stdout_sha256`: SHA-256 string; `monotonic_ns`: integer | Governed production predicate, exactly exit 1 and empty stdout, with authenticated timestamp lineage; an exit 0, output on exit 1, exit 2 or timeout cannot establish absence |
| Each `conditions` item | `condition_id`: string; `status`: string; `evidence`: array | Exactly C1, C2, C3, C4 and C5 each present and PASS; authenticate the underlying evidence, not declared PASS alone |

C1 is the purpose-bound transaction authorization in §4. C2 is the verified pack
ARM ceremony. C3 proves the machine quiet through the production census. C4 proves
boot and clock validity. C5 enforces the no-retry bound. G2-b, campaigns and
pack-bound rehearsal receive no `no_pack_by_design` exemption. All five conditions
must PASS before GO; a missing, incomplete, stale or condition-failing receipt
cannot permit `execve`, the operating-system call that starts the measurement
chain.

## 3. Consumption and replay

`_consume_launch_capability` gains three required keyword arguments:
`go_receipt`, `authenticated_go_receipt`, and `go_receipt_sha256`. Each defaults
to `_MISSING_LAUNCH_CONTEXT`, the existing missing-argument sentinel. An omitted
keyword refuses with `readiness_usage_invalid`; no caller can skip GO validation
by taking a direct callee route.

Within the callee, re-read `go_receipt` from disk, recompute its SHA-256, compare
it with `go_receipt_sha256`, and compare the parsed result with
`authenticated_go_receipt`. Authenticate the underlying receipts against custody
and the independently held launch context. Require every table binding above,
including ARM `receipt_id` and `sha256`, pack digest, boot session and all three
launch digests. Require `receipt_class == TRANSACTION_PACK`, `verdict == GO`, all
five conditions `PASS`, and
`issued_monotonic_ns <= now_monotonic_ns < valid_until_monotonic_ns` with GO expiry
no later than ARM expiry. Validate purpose and the rehearsal window/root predicates
in §6. Re-read and re-digest the confirmation and authorization records and compare
both against the plan and GO bindings. A CLI check alone is insufficient.

The two ruled GO refusal codes are:

| Code | Exact responsibility |
|---|---|
| `launch_go_receipt_missing` | GO file is missing |
| `launch_go_receipt_invalid` | Every other GO authentication, binding, class, purpose, condition or validity failure; `detail` names the field, or the refused class for G7 |

Before either code emits, complete stage-1 R-8's three registration steps:
(1) add both to `LAUNCH_LINEAGE_REASON_CODES` in `joulewise/arm_readiness.py`;
(2) document each exact spelling in `docs/contracts/d078_reason_registry_amendment.md`;
(3) install its emission site and a regression that demonstrates the refusal.
These are launch-family codes, not additions to the frozen readiness-row registry
or `REASON_CODE_COVERAGE`. The route is stage-1 R-8 and
`seat-opus-unattended-design.md` §Q2 (lines 101–115), in the 2026-09-01 unattended
trace. This draft does not itself register or emit them.

The consumption schema becomes `joulewise.arm_readiness_launch_consumption.v3`.
Keep the existing consumption identity, pack/plan/window, ARM path/digest,
launch-file references, argv and other v2 bindings, and add the judge's fields:

| Addition | Required nested keys and types | Purpose |
|---|---|---|
| `go_receipt` | `receipt_id`: string; `sha256`: SHA-256 string; `purpose`: string; `receipt_class`: string | Persist the exact authenticated GO identity, digest, purpose and class at the ARM one-use write; GO identity/path details still need §8 ruling |
| `step6_confirmation` | `table_path`: path string; `table_sha256`: SHA-256 string | Persist the authenticated confirmation pair for the child |

The authenticated `purpose` and `claim_eligible` are both bound into consumption
and read by the launch-realization recheck and L10 (the later launch-to-claim
verification ladder). A `G2B_SHAKEDOWN` can never become claim-eligible by changing a
label later. The placement of `claim_eligible` in the exact v3 wire object is an
unresolved detail in §8; it must not be dropped merely because the judge's v3
addition list omits it.

Update the schema's key set, `validate_consumption_receipt` and
`verify_consumed_launch`'s expected identity together. Put v2 into the legacy
branch: it may replay historically only with `require_current_boot=False`. It
cannot satisfy a live v3 launch. `verify_consumed_launch` must re-read GO bytes
from the recorded path, recheck the digest and all bindings, and refuse live
replay of any record lacking `go_receipt`. Historical replay does not promote a
record into present launch authority.

The existing ARM consumption `O_EXCL` write remains the sole one-use point. Do
not add a second GO-consumed lock. A replay loses the existing ARM lock; a new ARM
has a new receipt id and cannot use a GO bound to the old ARM. A forged GO must
survive authentication of the ARM it names and all underlying evidence. Mutation
between CLI verification and the callee is caught by the callee's own reads.

## 4. Transaction authorization record

The transaction authorization is a mode-0600 (owner read/write only), create-once
record in transaction custody. Its SHA-256 is bound into the pack-night plan and
into GO. It replaces stage-1 R-4's `TRANSACTION_PACK` C1 cell. The D-149 template's
old C1 “council verdict” line must cite D-167 plus D-176 when its producer lands.

| Ruled key | Type | Bound-to / check |
|---|---|---|
| `purpose` | string | One of the three purposes below; agrees with GO and consumption |
| `claim_eligible` | boolean | Authenticated claim eligibility; retained in consumption and checked by realization and L10 |
| `pack_sha256` | SHA-256 string | Exact frozen pack, equal to GO and verified ARM context |
| `permitted_chain_sha256` | SHA-256 string | Exact permitted launch chain, equal to GO's `window_chain_sha256` and actual chain bytes |
| `permitted_blocks` | integer | Authorized block count; G2-b permits exactly one |
| `authority` | authority reference | The authorizing decision/record for this purpose; exact wire representation is not pinned by the ruling |

| Purpose | Authorization and claim boundary |
|---|---|
| `G2B_SHAKEDOWN` | Magistrate authorization under D-167 clause 1 and D-171 §3; names exact pack, attempt and permitted chain; `claim_eligible=false`, `permitted_blocks=1`. It is NOT `V5-TRANSACTION-GO-01` and does not discharge it. |
| `CAMPAIGN_TRANSACTION` | Authority `V5-TRANSACTION-GO-01`, delegated to the magistrate by D-171 §3; issuable only after the G2-b verdict is custodied. Claim eligibility remains subject to that authorization and all downstream claim checks. |
| `T0_REHEARSAL` | D-176 decision 4's isolated, non-claim pack-bound rehearsal; accepted only with the rehearsal window prefix and disjoint roots in §6. It supplies no campaign claim authority. |

C2–C5 are identical and required to PASS. `DIAGNOSTIC_NO_PACK` for G2-b is
rejected. The adopted Opus sentence also requires naming the exact attempt; the
ruling does not supply its field or reference encoding (§8).

## 5. Step-6 confirmation custody and transport

Use the existing retained `085-ed-step6-confirmed-sha256.txt` transcript as the
confirmation source. Write one create-once, mode-0600
`step6_confirmation_record.json` in transaction custody with these keys:

| Key | Type | Bound-to / check |
|---|---|---|
| `table_path` | path string | Location of the already confirmed step-6 table |
| `table_sha256` | SHA-256 string | hC, the digest Ed confirmed; later readers re-hash the table against this fixed value |
| `transcript_sha256` | SHA-256 string | Actual retained confirmation transcript bytes |
| `confirmed_at` | confirmation timestamp | Retained confirmation event; its precise wire encoding is not specified by the ruling |

The plan binds this record's SHA-256, and GO repeats that binding. The driver
reads hC from this authenticated record. Never derive the expected digest from
whatever table happens to be present at T-0. Both
`--step6-confirmation-table` and `--expected-confirmation-digest` are REQUIRED
for a `TRANSACTION_PACK` launch, including when there are no digest-conditional
paths in the changed set. The driver passes both to the launcher by **argv**,
the process's command-line argument list. Regressions must prove refusal when
either is omitted.

The child chain's `--lifecycle-event start` reads `step6_confirmation` from the
authenticated v3 consumption record when the flags are absent, then re-hashes the
table and compares it with `table_sha256`. Explicit flags, when supplied, must
agree with that authenticated pair; they are not a new confirmation authority.

The environment route is FORBIDDEN. hC is not passed through `execve`'s
environment, and `window.env`'s 25-key allowlist remains exact. The ruled runbook
sentence is: “hC lives only in transaction custody; it reaches the launcher by
argv and the child by the consumption record.” The plan and record survive a
magistrate relaunch on disk; session memory carries no confirmation authority.
The integrated child-route regression must assert that hC is absent from the
child's environment.

## 6. Rehearsal and G7

G2-a discharges NO rehearsal gate. Only after `run_night.py` explicitly sets
`stdin=subprocess.DEVNULL` may G2-a contribute observational G1 execution records,
G8 census lineage and G9 launch/courier/dead-man records. `DEVNULL` connects file
descriptor 0 (standard input) to `/dev/null`, so unattended descendants cannot
inherit interactive input.

Closure requires one isolated, non-claim, pack-bound night run by the driver.
Its pack window id begins `rehearsal-t0-unattended-`. Its custody, ledger, runs
and backups are dedicated and disjoint from an independently established census
of production roots. The consumer accepts `purpose=T0_REHEARSAL` ONLY on that
prefix with disjoint roots. It refuses EVERY other purpose on a prefixed id with
`launch_go_receipt_invalid`. No launcher `--allow-rehearsal` flag is introduced.

The successful rehearsal uses the pack-night schema with
`receipt_class=TRANSACTION_PACK` and `purpose=T0_REHEARSAL`. Separately, G7
presents a valid `T0_UNATTENDED_SUPERVISED_REHEARSAL`-class receipt in the existing
rehearsal schema to the real production launcher. Preserve the class-specific
`launch_go_receipt_invalid` refusal, with the class in `detail`, and prove the
absence of any `.consumed.json` and capture. A made-up invalid object or a
validator-only check does not establish this production-entry refusal.

G1–G10 all must PASS on authenticated producer evidence; no `UNRULED` or
`INCOMPLETE` counts as success. G5 evaluates `joulewise.pack_night_go_receipt.v1`
and recomputes C1–C5 from authenticated evidence. The privileged-anchor positive
control remains Ed-owned and must be surfaced as NEEDS-ED, never assumed or
replaced by software fixtures. The ARM T-0 evidence author is substantially
implemented; the GO producer and rehearsal-bundle producers are unwritten at the
ruling's inspected baseline.

The source checklist is
[exhibit A §R4](../process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/exhibit-A-consult-astra.md#r4--t-0-rehearsal-needs-producers-authentication-and-an-executable-acceptance-route),
lines 161–181: the remaining-mechanism table is at 167–177, with G4's existing
clock recomputation explicitly preserved at 179. The table is not copied into a
new trace. `T0-REHEARSAL-PRODUCERS-01`'s G7-stays-UNRULED fence is released only by
a dated addendum when `UNATTENDED-LAUNCH-01` merges; that merge is not asserted here.

## 7. Installation order and required replays

Seat 1 drafts this contract and an Opus refuter reviews it before code. After the
contract lands, seat 2 builds the producer and night-driver orchestration and
seat 3 builds the consumer, consumption v3 and verify replay in parallel
worktrees. Seat 4 builds rehearsal purpose/G7 after seat 2. Every seat follows
the C-028 gauntlet: bounded write scope, independent audit, distinct refuter
lenses, and a delta re-audit after each fix, including a mutation-shaped audit
that deletes or corrupts one gate and proves the relevant assertion fails.

Build may precede `NIGHT-REHEARSAL-01` harvest. Live pack rehearsal hard-starts
only after `UNATTENDED-LAUNCH-01` merges AND `NIGHT-REHEARSAL-01` is harvested.
A second cold gate on the integrated head and the real plan bytes precedes the
first pack-bound night. No code evidence closes a live obligation. G2-b waits on
`NIGHT-PACK-REHEARSAL-01`; the liveness margin is a registered limitation through
G2-b and must close or be reruled before ALPHA. The rehearsal, ARM-ABORT and G2-b
provide the three real receipt bundles for that empirical check.

Focused replay list from exhibit A (lines 279–290), verbatim:

- Missing GO, malformed/incomplete receipt, each failed C condition, expired evidence, wrong boot/head/pack/ARM/manifest/confirmation.
- A fully valid rehearsal receipt refused **by class**, before consumption.
- Mutation between CLI verification and callee consumption.
- Duplicate timers and crashes before/after consumption: at most one launch; no automatic re-arm.
- Confirmation transport through the real child start route.
- Agent-census exit 0, exit 1 with output, exit 2, timeout, and helper-name variants.
- Dead-man before the night, during preparation/capture, and with ambiguous termination; no premature courier.
- Producer-emitted rehearsal evidence only, with omitted/wrong namespace, stale HID evidence, arbitrary PASS labels, incomplete root census and fabricated positive-control fields rejected.
- Author/ARM timing boundaries and refusal codes, without substituting software fixtures for the physical positive control.
- Historical strict-schema replay and clean-clone pack proof at the final integrated head.

The judge adds three required cases: (a) a rehearsal-prefixed id with a
non-rehearsal purpose is refused; (b) a v2 consumption record is refused on live
replay; (c) hC is absent from the child's environment. Also require the adopted
Opus F6 omission regression for each mandatory confirmation flag, even when the
changed set has no conditional path. The same producer regression must fail when
the GO check is deleted to close both `UNATTENDED-LAUNCH-01` and S9-06.

## 8. NEEDS_RULING — remaining wire details

The exact lists above are preserved, without guessed extra keys. The following
questions prevent this draft from being independently replicable as an exact
wire contract. They do not prevent installation of the decision or kernel graph.

| Question | Options considered | Recommendation | Blocked work |
|---|---|---|---|
| Where is the replay GO path recorded, and how is its `receipt_id` derived? Judge line 11 requires replay “by the recorded path” but omits `path` from its v3 `go_receipt` list; line 9 gives GO no `receipt_id`. | Adopt Opus's `go_receipt.path` addition plus an explicit identity derivation; or rule a deterministic locator/identity using the judge's existing fields. | Adopt the explicit Opus path field and have the lead pin the receipt-id derivation. Do not silently enlarge the exact GO keys. | Exact v3 identity/path layout and independently reproducible replay. |
| Where does v3 store `claim_eligible`, and where does authorization name the exact attempt? Judge line 17 requires the first binding but line 11 omits its location; synthesis decision 2 adopts Opus's exact-attempt requirement without a field encoding. | Add named fields; or identify an existing authenticated reference and define its exact encoding and equality checks. | Lead pins `claim_eligible` placement and an explicit attempt binding; both remain mandatory. | Exact authorization/v3 key sets and downstream realization/L10 bindings. |
| What exact encodings are used for authorization `authority`, confirmation `confirmed_at`, and each condition's `evidence` entry? | Specify JSON types and reference formats; or adopt a named existing schema with exact field mapping. | Reuse named existing formats where applicable, with explicit mappings in the ruling. | A second implementer cannot produce byte/schema-compatible records from the adopted text alone. |

These are implementation-contract questions for the lead, not invitations to
re-decide the six adopted outcomes. Nothing in this draft licenses a missing
binding while the question is open. No additional repository write scope is
needed to complete this document after a ruling.

## 9. D-170 clause map

This map gives the contract installation site for each independent proposition,
the ruling clause it installs, the future production site and the counterfactual
that the implementing seat must make fail. `J` means the packet's
`10-coldgate-fable-ruling.md`; `S` means `13-magistrate-synthesis.md`; `O` means
`11-coldgate-opus-refutation.md`. All three full paths are linked above. `G` means
`docs/contracts/pack_night_go_receipt.md` (this document).

Runtime production and test sites are **NOT PINNED** because this is the
before-code seat. The named targets below identify where the implementation
must land; they do not claim production or biting tests exist. Each successor
seat must replace its NOT PINNED cells with actual `file:line` and test-method
locations. All such rows go to the Opus refuter as findings under D-170's clause
map rule. Graph installation assertions are in the installation report.

| Clause / source phrase | Contract installation | Production site | Biting assertion | Counterfactual |
|---|---|---|---|---|
| J:9 “produced only by the night driver after ARM verify” | G §1 | NOT PINNED: seat 2, `scripts/run_night.py` | NOT PINNED: producer ordering regression | Issue GO before ARM verification |
| J:9 exact key `schema_version`; J:11 “every binding equals” | G §2 / `schema_version` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `schema_version` producer-to-consumer regression | Omit `schema_version` or accept its mismatched binding |
| J:9 exact key `receipt_class`; J:11 “every binding equals” | G §2 / `receipt_class` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `receipt_class` producer-to-consumer regression | Omit `receipt_class` or accept its mismatched binding |
| J:9 exact key `purpose`; J:11 “every binding equals” | G §2 / `purpose` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `purpose` producer-to-consumer regression | Omit `purpose` or accept its mismatched binding |
| J:9 exact key `plan_id`; J:11 “every binding equals” | G §2 / `plan_id` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `plan_id` producer-to-consumer regression | Omit `plan_id` or accept its mismatched binding |
| J:9 exact key `pack_id`; J:11 “every binding equals” | G §2 / `pack_id` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `pack_id` producer-to-consumer regression | Omit `pack_id` or accept its mismatched binding |
| J:9 exact key `pack_sha256`; J:11 “every binding equals” | G §2 / `pack_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `pack_sha256` producer-to-consumer regression | Omit `pack_sha256` or accept its mismatched binding |
| J:9 exact key `arm_receipt`; J:11 “every binding equals” | G §2 / `arm_receipt` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `arm_receipt` producer-to-consumer regression | Omit `arm_receipt` or accept its mismatched binding |
| J:9 exact key `boot_session_id`; J:11 “every binding equals” | G §2 / `boot_session_id` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `boot_session_id` producer-to-consumer regression | Omit `boot_session_id` or accept its mismatched binding |
| J:9 exact key `t0_evidence`; J:11 “every binding equals” | G §2 / `t0_evidence` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `t0_evidence` producer-to-consumer regression | Omit `t0_evidence` or accept its mismatched binding |
| J:9 exact key `launch_manifest_sha256`; J:11 “every binding equals” | G §2 / `launch_manifest_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `launch_manifest_sha256` producer-to-consumer regression | Omit `launch_manifest_sha256` or accept its mismatched binding |
| J:9 exact key `window_environment_sha256`; J:11 “every binding equals” | G §2 / `window_environment_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `window_environment_sha256` producer-to-consumer regression | Omit `window_environment_sha256` or accept its mismatched binding |
| J:9 exact key `window_chain_sha256`; J:11 “every binding equals” | G §2 / `window_chain_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `window_chain_sha256` producer-to-consumer regression | Omit `window_chain_sha256` or accept its mismatched binding |
| J:9 exact key `repo_head`; J:11 “every binding equals” | G §2 / `repo_head` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `repo_head` producer-to-consumer regression | Omit `repo_head` or accept its mismatched binding |
| J:9 exact key `measurement_root`; J:11 “every binding equals” | G §2 / `measurement_root` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `measurement_root` producer-to-consumer regression | Omit `measurement_root` or accept its mismatched binding |
| J:9 exact key `measurement_head`; J:11 “every binding equals” | G §2 / `measurement_head` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `measurement_head` producer-to-consumer regression | Omit `measurement_head` or accept its mismatched binding |
| J:9 exact key `confirmation_record_sha256`; J:11 “every binding equals” | G §2 / `confirmation_record_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `confirmation_record_sha256` producer-to-consumer regression | Omit `confirmation_record_sha256` or accept its mismatched binding |
| J:9 exact key `authorization_record_sha256`; J:11 “every binding equals” | G §2 / `authorization_record_sha256` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `authorization_record_sha256` producer-to-consumer regression | Omit `authorization_record_sha256` or accept its mismatched binding |
| J:9 exact key `census`; J:11 “every binding equals” | G §2 / `census` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `census` producer-to-consumer regression | Omit `census` or accept its mismatched binding |
| J:9 exact key `issued_epoch_s`; J:11 “every binding equals” | G §2 / `issued_epoch_s` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `issued_epoch_s` producer-to-consumer regression | Omit `issued_epoch_s` or accept its mismatched binding |
| J:9 exact key `issued_monotonic_ns`; J:11 “every binding equals” | G §2 / `issued_monotonic_ns` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `issued_monotonic_ns` producer-to-consumer regression | Omit `issued_monotonic_ns` or accept its mismatched binding |
| J:9 exact key `valid_until_monotonic_ns`; J:11 “every binding equals” | G §2 / `valid_until_monotonic_ns` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `valid_until_monotonic_ns` producer-to-consumer regression | Omit `valid_until_monotonic_ns` or accept its mismatched binding |
| J:9 exact key `conditions`; J:11 “every binding equals” | G §2 / `conditions` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `conditions` producer-to-consumer regression | Omit `conditions` or accept its mismatched binding |
| J:9 exact key `verdict`; J:11 “every binding equals” | G §2 / `verdict` table row | NOT PINNED: seat 2 producer and seat 3 consumer/replay | NOT PINNED: missing/wrong `verdict` producer-to-consumer regression | Omit `verdict` or accept its mismatched binding |
| J:9 “arm_receipt {receipt_id, sha256, valid_until_monotonic_ns}” | G §2 nested ARM row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | ARM identity or expiry mismatch accepted |
| J:9 “t0_evidence [{path, sha256}]” | G §2 nested evidence row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Omit a required evidence member or accept wrong bytes |
| J:9 “census {argv, exit_code, stdout_sha256, monotonic_ns}” | G §2 nested census row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Treat erroneous or output-bearing census as absence |
| J:9 “C1..C5 each {condition_id, status, evidence[]}” | G §2 nested conditions row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Accept missing condition or unauthenticated PASS label |
| J:11 “three required keywords” / “readiness_usage_invalid” | G §3 keyword paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Direct caller omits any GO keyword and consumes |
| J:11 “re-reads the bytes, recomputes the digest” | G §3 callee paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Mutate GO between CLI and callee and still consume |
| J:11 “now_monotonic ∈ [issued, valid_until)” | G §3 callee paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Accept before issuance or at expiry |
| J:11 “launch_go_receipt_missing” | G §3 refusal table | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Missing file reaches consumption |
| J:11 “launch_go_receipt_invalid” | G §3 refusal table | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Wrong binding/class/purpose reaches consumption |
| J:11 “registered by R-8” | G §3 registration paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Emit code absent from family, documentation or refusal regression |
| J:11 “go_receipt {receipt_id, sha256, purpose, receipt_class}” | G §3 v3 table; §8 question 1 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Consumption drops GO identity/digest/purpose/class |
| J:11 “step6_confirmation {table_path, table_sha256}” | G §3 v3 table | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Consumption drops authenticated confirmation pair |
| J:11 “v2 joins the legacy branch” / “require_current_boot=False” | G §3 legacy paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | v2 passes live replay |
| J:11 “re-reads the GO bytes by the recorded path” | G §3 replay paragraph; §8 question 1 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Replay trusts a recorded hash without reading GO bytes |
| J:13 “No second lock” | G §3 one-use paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Duplicate timer spends one ARM twice or a second GO lock is introduced |
| J:17 “mode 0600, create-once, in transaction custody” | G §4 record paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Overwrite authorization or create it outside custody |
| J:17 “sha256-bound into the pack-night plan” | G §4 record paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Swap authorization after plan freeze |
| J:17 “purpose” | G §4 authorization key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Purpose differs across authorization, GO and consumption |
| J:17 “claim_eligible” | G §4 authorization key row; §3 v3 prose; §8 question 2 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Shakedown is relabeled into a claim |
| J:17 “pack_sha256” | G §4 authorization key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Authorize one pack and launch another |
| J:17 “permitted_chain_sha256” | G §4 authorization key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Run a different chain |
| J:17 “permitted_blocks” | G §4 authorization key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | G2-b authorization permits more than one block |
| J:17 “authority” | G §4 authorization key row; §8 question 3 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Unbound authority is accepted as C1 |
| J:17 “G2B_SHAKEDOWN” / “claim_eligible=false” | G §4 purpose table | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | G2-b authorization carries claim eligibility |
| S decision 2; O §2 “exact pack, attempt, permitted chain” | G §4 purpose table; §8 question 2 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | An authorization from a different attempt is reused |
| S decision 2; O §2 “does not discharge it” | G §4 purpose table | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | G2-b C1 discharges V5-TRANSACTION-GO-01 |
| J:17 “issuable only after G2-b's verdict is custodied” | G §4 campaign-purpose row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Issue campaign authorization before verdict custody |
| J:17 “C2–C5 identical” / “DIAGNOSTIC_NO_PACK ... REJECTED” | G §4 final paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Skip ARM or other conditions by changing G2-b class |
| J:21 “085-ed-step6-confirmed-sha256.txt” | G §5 source paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Adopt current table hash without original confirmation |
| J:21 “table_path” | G §5 confirmation key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Swap the confirmed table locator |
| J:21 “table_sha256 (= hC)” | G §5 confirmation key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Accept a table whose bytes do not match hC |
| J:21 “transcript_sha256” | G §5 confirmation key row | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Accept changed confirmation transcript bytes |
| J:21 “confirmed_at” | G §5 confirmation key row; §8 question 3 | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Omit the confirmation event timestamp |
| J:21 “plan binds that record's sha256” | G §5 transport paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Swap confirmation record after plan freeze |
| S decision 3 adopting O F6 “both ... REQUIRED” | G §5 required flags paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Omit either flag with no conditional changed path and launch |
| J:21 “launcher by argv” | G §5 argv paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Driver supplies no authenticated confirmation pair |
| J:21 “child by the consumption record” | G §5 lifecycle paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Child starts without re-hashing table against authenticated v3 pair |
| J:21 “environment ... REJECTED” / “25-key allowlist stays exact” | G §5 environment paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | hC reaches child environment or allowlist expands |
| J:25 “G2-a discharges NO gate” | G §6 opening paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | G2-a is counted as rehearsal closure |
| J:25 “stdin=subprocess.DEVNULL” | G §6 opening paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Descendant inherits interactive standard input |
| J:25 “purpose=T0_REHEARSAL” / “prefixed id with disjoint roots” | G §6 purpose paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Accept rehearsal purpose without prefix or with production roots |
| J:25 “refuses every other purpose on a prefixed id” | G §6 purpose paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Non-rehearsal purpose accepted on rehearsal-prefixed window |
| J:25 “class refusal plus ... absence of any .consumed.json” | G §6 G7 paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | A validator-only rejection counts as production G7 or writes consumption |
| J:25 “No --allow-rehearsal flag” | G §6 purpose paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | A launcher override bypasses class/purpose check |
| S decision 1; J:25 “G5 ... pack_night_go_receipt.v1” | G §2 retirement; §6 G5 paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Legacy unbound D-149 v1 passes G5 |
| J:25 “positive control stays Ed-owned” | G §6 G5 paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Fixture or declaration closes the physical positive control |
| S decision 4 adopting O F3 “GO producer ... do not [exist]” | G §6 baseline paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Report ARM evidence author as an existing GO producer |
| J:33 “released by dated addendum when ... merges” | G §6 checklist paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Release G7 UNRULED fence before consumer merge |
| S decision 6; J:39 “before code” / seats 2, 3, 4 | G §7 opening paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Code scope issued before contract refutation/landing or seat 4 before seat 2 |
| J:39 “C-028 gauntlet, mutation-shaped audit” | G §7 opening paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | A green happy path substitutes for gate-deletion regression |
| J:39 “consult's replay list verbatim” and additions (a)–(c) | G §7 replay list and final paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | Drop any ruled replay case |
| J:39 “second cold gate ... real plan bytes” | G §7 gate paragraph | NOT PINNED: future runtime/lead gate; no code scope in seat 1 | NOT PINNED: implementing seat must pin a defect-shaped assertion | First pack-bound night occurs without integrated-head/real-plan gate |
