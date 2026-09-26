"""DOC-008 state-kernel validity, work-selection fidelity, and drift tests."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gen_state  # noqa: E402

KERNEL_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.json")
SCHEMA_PATH = os.path.join(ROOT, "docs", "process", "state_kernel.schema.json")
GEN = os.path.join(ROOT, "scripts", "gen_state.py")
FIXTURE_DIR = os.path.join(ROOT, "tests", "fixtures", "state_kernel")

EXPECTED_IDS = {
    # 2026-09-25 activation 152c9255 bookkeeping seat: five ruled follow-ups, 250 + 5 = 255.
    "CLAIMGATE-GOLDEN-SWEEP-OPERATORS-01",
    "V1-ISSUANCE-GATE-EVIDENCE-CLASS-01",
    "HEADLINE-POWER-01",
    "CLAIMGATE-CG1-AMENDMENT-AJC1-01",
    "JCORRECT-NULL-CALIBRATION-WINDOWS-01",
    # 2026-09-25 activation 152c9255: seven follow-ups, 244 + 7 = 251.
    "CI-A291-TIMINGS-01",
    "A291-STRUCTURE-INDEX-01",
    "A291-DIGEST-FINALIZE-01",
    "A291-INV12-RECONCILE-01",
    "CLAIMGATE-V2-IMPL-01",
    "CLONE-ARM-MDFIND-01",
    "CLONE-RETENTION-01",
    # 2026-09-21 activation ce7c57a9 (RETAINED-ROOT-REFUSAL-CLASS-01 round 3, cold-gate Q6 A2-F1):
    # retire NIGHT-ROOT-RETENTION-DISCOVERY-01 (A230, delivered by the same PR): 221 - 1 = 220;
    # register MAGISTRATE-LAUNCH-WITHOUT-MCP-01 (264) and CANONICAL-REFUSAL-STRINGS-01 (265): 220 + 2 = 222.
    "MAGISTRATE-LAUNCH-WITHOUT-MCP-01",
    # 2026-09-21 activation ce7c57a9, packet 06 ruling Q3: register ARM-VOCABULARY-GLOSSARY-01 (266): 222 + 1 = 223.
    "ARM-VOCABULARY-GLOSSARY-01",
    # 2026-09-22 activation 22666c9f, harvest record 01 §8: register QPE01-CLOCK-DISCIPLINE-ANCHOR-01 (267), NIGHT-RESULTS-LARGE-FILES-01 (268), ENVELOPE-START-DRIFT-01 (269): 223 + 3 = 226.
    "QPE01-CLOCK-DISCIPLINE-ANCHOR-01",
    "NIGHT-RESULTS-LARGE-FILES-01",
    "ENVELOPE-START-DRIFT-01",
    # 2026-09-23 activation 7a0f14bd, D-182 addendum (Ed-ratified) + owner session record 7ec32e8b §2: register QPE01-ABORT-SUCCESSOR-01 (270), FSEVENTSD-CORECAPTURED-PREDICATE-01 (271): 226 + 2 = 228.
    "QPE01-ABORT-SUCCESSOR-01",
    # 2026-09-23 activation f2d6899b: A271 landed by PR #394, merge c741678b. Its t0 check is detection-only (lead ruling record 05, upheld by ruling 16 Q2); registration v4 recording is deferred per final pass record 32 §4.
    # 2026-09-23 activation 4158e658, directive #386 + owner session record 7ec32e8b (records 04, 07): register THROUGHPUT-01 (272), BLOCK-TWO-DESIGN-01 (273), PROMPT-AUDIT-01 (274), CENSUS-MULTILINE-ARGV-01 (275): 228 + 4 = 232.
    "THROUGHPUT-01",
    "BLOCK-TWO-DESIGN-01",
    "PROMPT-AUDIT-01",
    "CENSUS-MULTILINE-ARGV-01",
    # 2026-09-23 activation 4158e658 arm gate: register NOTICE-SUMMARY-V3-TEXT-01 (276): 232 + 1 = 233.
    # 2026-09-23 activation 1d3796d5: A276 retired after PR #397, merge 1c59cc6b.
    # 2026-09-23 activation f2d6899b: retire A234/A212/A271 and register A277/A278/A279: 233 - 3 + 3 = 233.
    # 2026-09-23 activation 1d3796d5: A277 retired after PR #399, merge 8175a7ad.
    # Register A280-A290: 233 - 2 + 11 = 242.
    "HEADLINE-SCORED-NIGHT-KIND-01",
    # 2026-09-23 activation d8cc9c0a: omnibus A281 superseded by cold-gated split; retained as shelved history.
    "HEADLINE-PURE-MODULES-GATE-01",
    # Register A291–A295; A281 stays in the kernel as shelved: 242 + 5 = 247.
    # 2026-09-25 activation 152c9255: HEADLINE-PACKER-RECUT-01 retired after PR #409, merge 75d04e9e.
    "HEADLINE-REDUCER-SEALED-01",
    "HEADLINE-ESTIMATOR-DECISION-TABLE-01",
    # A294/A295 completed in PR #403 (2026-09-24) and moved to the completed queue.
    "HEADLINE-AP5M-AMENDMENT-01",
    "HEADLINE-DECODING-AND-RUNTIME-01",
    "HEADLINE-AFFINE-LADDER-LEG-01",
    "HEADLINE-SCORER-AUDIT-01",
    "DIRECT-INSTALLER-SUCCESSOR-CHECK-01",
    "LINUX-CI-TERM-DELAY-01",
    "ARM-READINESS-ANCHOR-DELTA-LOAD-FLAKE-01",
    "BRIEF-MANDATED-WORDING-RULE-01",
    "D182-SUCCESSOR-CANNOT-RELICENSE-RULING-01",
    "QPE01-REGISTRATION-V4-CORECAPTURED-01",
    "BIND-SUPERVISION-RECV-STALL-FLAKE-01",
    "CANONICAL-REFUSAL-STRINGS-01",
    # 2026-09-20 activation 21752427, touch 6: register the successor runbook
    # doc lane RUNBOOK-TRACKED-COMMANDS-01; no retirements: 220 + 1 = 221.
    "RUNBOOK-TRACKED-COMMANDS-01",
    # 2026-09-20 activation 21752427, touch 2: retire CENSUS-SELF-MATCH-01 (PR #371)
    # and CI-LEGACY-FIXTURE-LINUX-01 (PR #370): 220 - 2 = 218; register
    # WATCHDOG-COURIER-PATH-HOLD-01 and TEST-FIXTURE-HOST-PATHS-01: 218 + 2 = 220.
    "WATCHDOG-COURIER-PATH-HOLD-01",
    "TEST-FIXTURE-HOST-PATHS-01",
    # 2026-09-20 activation 21752427, touch 3: retire EVIDENCE-INSTALLER-SPLIT-01;
    # register EVIDENCE-NIGHT-ENTRY-01 at the same rank 256: 220 - 1 + 1 = 220.
    "EVIDENCE-NIGHT-ENTRY-01",
    # 2026-09-19 activation a743be05: register INSTRUMENT-CADENCE-25G83-01: 218 + 1 = 219.
    "INSTRUMENT-CADENCE-25G83-01",
    # 2026-09-19 activation a743be05: register SUPERVISOR-RECEIPT-PAYLOAD-INIT-01: 219 + 1 = 220.
    "SUPERVISOR-RECEIPT-PAYLOAD-INIT-01",
    # 2026-09-19 evening, activation d0b83820 (ruling 87a): register the evidence
    # wrapper plan-path binding fix that blocks the pilot-night arm: 215 + 1 = 216.
    # 2026-09-19 evening (activation d0b83820): EVIDENCE-PLAN-PATH-BINDING-01 retired by removal after PR #365 merged (main 4f2aa185): 216 - 1 = 215.
    # 2026-09-19 evening, activation d0b83820 (ruling 83a): register the courier
    # diagnostic-persistence lane and the fixture temp-name census flake: 214 + 2 = 216.
    "COURIER-DIAGNOSTIC-PERSISTENCE-01",
    "FIXTURE-TMPNAME-CENSUS-SUBSTRING-01",
    # 2026-09-19 late afternoon, activation d0b83820 (ruling 79a): register the
    # courier-lock ownership redesign and the unwritable-custody reporting lane:
    # 212 + 2 = 214.
    "COURIER-LOCK-OWNERSHIP-FLOCK-01",
    "COURIER-UNWRITABLE-CUSTODY-01",
    # 2026-09-19 afternoon, activation d0b83820: register the unattended evidence
    # executor and file-based hosted test runner; retire the generator byte-pin
    # task after pull request #362 merged: 211 - 1 + 2 = 212.
    # 2026-09-19 evening (activation d0b83820): STAGE-A-EVIDENCE-EXECUTOR-01 retired by removal after PR #364 merged (main a9e48ae9): 216 - 1 = 215.
    "CI-SHARD-RUNNER-FILE-BASED-01",
    # 2026-09-19 headless activation d0b83820: equivalence night two FAILED (m = 7) and the ruling question went to Ed; head-pin drift consult + cold gate; magistrate registrations, not rulings.
    "REGISTRATION-NIGHT-COUNT-RULING-01",
    "INSTRUMENT-CADENCE-ATTRIBUTION-25G83-01",
    "CI-DOCS-ONLY-SKIP-MASKS-RED-01",
    "QUIET-LOAD-MEMORY-PROFILE-DIFFERENTIAL-01",
    "TEST-WRITES-PAPER-BUILD-ARTIFACT-01",
    # 2026-09-18 headless activation f0b608b7: arm record 21 follow-ups and record 19 root cause; magistrate registrations, not rulings.
    "NIGHT-GATE-CROSS-SEAM-TESTS-01",
    "QUIET-PREDICATE-STAGE-B-CONFIRMATION-01",
    "COURIER-SENT-FORMAT-PIN-01",
    # 2026-09-18 interactive session 5c919872: PR #358 closes NIGHT-GATE-QUIET-ADMISSION-01 by removal; three follow-ups registered.
    "BIND-REQUEST-PAYLOAD-CAP-01",
    "QUIET-JOURNAL-REPLAY-CONTRACT-01",
    "TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01",
    # 2026-09-17 interactive session 5c919872: gate redesign; magistrate registrations, not rulings.
    "QUIET-PREDICATE-EVIDENCE-01",
    "SPOTLIGHT-FSEVENTS-ATTRIBUTION-01",
    # 2026-09-23 activation f2d6899b: A234 landed by PR #393, merge ea4995d5; cold final pass record 25.
    # 2026-09-17 activation 9853dd2b: cold-gate convening coldness lane for the council (magistrate registration, not a ruling).
    "COLDGATE-CONVENE-DOCTRINE-FREE-01",
    # 2026-09-17 activation 9853dd2b: pre-registration chain-digest addendum lane (magistrate registration, not a ruling).
    "TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01",
    # 2026-09-17 activation 9853dd2b: four NIGHT-RESERVE-HANG-01 review findings;
    # magistrate registrations, not rulings.
    "PROBE-DRIVER-COPY-BINDING-01",
    "NIGHT-DOCUMENT-HASH-BOUND-01",
    "CUSTODY-REAPING-ATTRIBUTION-01",
    # 2026-09-16 activation 9853dd2b: watchdog clock-step magistrate registration, not a ruling.
    "WATCHDOG-BOOTID-CLOCK-STEP-01",
    # 2026-09-11 activation 36d3a823: four follow-ups; handback gloss evidence supplied.
    "PASS-ROUTE-RUNBOOK-CONTINUATION-01",
    "IDENTITY-PROBE-LIVE-VERIFY-01",
    "NIGHT-HANDBACK-GLOSS-01",
    "REPLAY-FIXTURE-LEAK-01",
    # T38j: record 39 blocks G2-a on a successor for the live OS-build epoch.
    "ACCEPTANCE-EPOCH-25G83-01",
    "POWERMODE-PREFLIGHT-RECORD-01",
    # T38c: six live follow-ups; DONE liveness-docs stays outside the kernel.
    "BRIDGE-BASELINE-ANCHORS-01",
    "UNIT-VOCAB-SHARED-01",
    "REGISTRY-ROW-PIN-DRIFT",
    "CLONE-READINESS-01",
    "CONTRACT-PIN-DRIFT-01",
    # D-180 (Ed, 2026-09-10): arm recoverability and steerability lanes.
    "REMOTE-CONTROL-BETWEEN-WINDOWS-01",
    "GATE-B1-PROVENANCE-BAND-01",
    "CALEXITS-RACE-FLAKE-01",
    # 2026-09-14 activation 24b9d3dd: cold gate 65 found no resolvable successor pack root on main.
    "PACK-ROOT-SUCCESSOR-V5-01",
    # 2026-09-15 activation d6888966: magistrate registrations, not rulings.
    "WATCHDOG-STALE-EXIT-CLASS-01",
    "NOTICE-TRANSPORT-FALLBACK-01",
    "PHASE-PARTITION-INVARIANT-01",
    # 2026-09-16 interactive session 5239df1e: equivalence-night stall root cause; magistrate registrations, not rulings.
    "NIGHT-RESERVE-HANG-01",
    "NIGHT-STALL-WALLCLOCK-ABORT-01",
    "FIXTURE-FAKE-VLLM-LEAK-01",
    # 2026-09-15 activation d6888966: GAMMA counter-review magistrate registrations, not rulings.
    "PLAN-TREE-ROOTS-CONTRACT-01",
    "ROOT-NAMESPACE-FALLBACK-01",
    # 2026-09-15 activation d6888966: record 19 bench replay magistrate registration, not a ruling.
    "WATCHDOG-CLI-TEST-TMP-DISCOVERY-01",
    # 2026-09-15 activation d6888966: cold gate 25 Q6 magistrate registration, not a ruling.
    "RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01",
    # 2026-09-15 activation d6888966: cold gate 28 Q4 F4 magistrate registration, not a ruling.
    "INSTALLER-BACKUP-WINDOW-01",
    # 2026-09-15 activation d6888966: cold gate 28 Q2 sibling magistrate registration, not a ruling.
    "WATCHDOG-INSTALLER-VERIFIED-BOOTOUT-01",
    # 2026-09-15 activation d6888966: lieutenant protocol finding, magistrate registration, not a ruling.
    "BRIDGE-BASELINE-COMPLIANCE-01",
    # 2026-09-15 activation 08ca8197 (restart census, registered at the
    # interactive session b0ae8462's request): remaining hygiene lanes after
    # the 2026-09-16 orphan-sentinel closure -- worktree prune and temp-dir hygiene.
    "WORKTREE-PRUNE-01",
    "TEMP-HYGIENE-IW-TMP-01",
    # 2026-09-15 activation 08ca8197: Ed's standing data-offload instruction
    # (relayed by the interactive session b0ae8462), registered as a lane.
    "DATA-OFFLOAD-ICLOUD-01",
    # 2026-09-25 activation ed17a643: TIER01-GATE-01 follow-up lanes (delta F2).
    "TIER01-PATH-GUARD-01",
    "TIER01-D118-RECONCILE-01",
    # 2026-09-26 activation ed17a643: battery-float lanes and a load-timing flake lane.
    "BATTERY-FLOAT-GATE-01",
    "HISTORICAL-BATTERY-STATE-01",
    "SCORED-CEILING-BATTERY-01",
    "TEST-LOAD-JOIN-LADDER-FLAKE-01",
    # 2026-09-15 activation 08ca8197: record 16 flag F3 (tests reach the canonical
    # checkout by literal path), registered at the interactive session's request.
    "TEST-CANONICAL-PATH-DEPENDENCY-01",
    # 2026-09-16 activation 08ca8197: Ed's remark on the cost of a t0 refusal
    # (relayed by the interactive session b0ae8462), registered as the fast-retry lane.
    # 2026-09-23 activation f2d6899b: A212 landed by PR #393, merge ea4995d5; cold ruling 16 Q1 and final pass record 25.
    # 2026-09-16 activation 08ca8197: pgrep -lf multi-line argv parse nit from the
    # interactive session's seats, registered at its request.
    "TEST-PGREP-DIALECT-MULTILINE-01",
    # 2026-09-16 activation 08ca8197: Ed's inline USB-C power meter purchase
    # (relayed by the interactive session b0ae8462), the calibrated-gain lane.
    "WALL-METER-GAIN-01",
    # 2026-09-16 activation 08ca8197: installer post-merge review nits (interactive
    # record 25), registered at that session's request.
    "INSTALLER-FOLLOWUPS-REBASE-01",
    "RUNBOOK-SOURCE-MAP-01",
    # Activation 96bfeca7: registered follow-ups; R2 stays on the D-138 branch.
    "NIGHT-STREAM-PATHS-01",
    # Activation 96bfeca7, final wave: doctrine install obligation, guard re-keying (ruling first), recover reason mapping.
    "ISOLATION-RULE-DOCTRINE-01",
    "V2-SURFACE-GUARD-REKEY-01",
    # T38l: Ed's ruling (directive issue 316) — the continuation mechanism and its desk-check follow-up.
    "EPOCH-CONTINUATION-01",
    "ISSUER-CHECK-CONTINUATION-AWARE-01",
    "CONTRACT-TEMPORAL-HEDGE-GUARD-01",
    "GATE-R2-COVERAGE-ULP-01",

    # 2026-09-08 D-176 decision 5: isolated pack-bound rehearsal successor.
    "NIGHT-PACK-REHEARSAL-01",
    # 2026-09-03 post-merge kernel batch. Thirteen rows, from four sources:
    # the decode-identity S3 ruling (d) and the packet-45 cold gate's two
    # residual nits; the 2026-09-02 code-and-tests audit's ranked five; the two
    # in-flight unattended-lane rows; and the four rows the 2026-09-02
    # fresh-Fable docs-vs-truth audit found RULED BUT NEVER REGISTERED (its A7
    # -- LINEAGE-RELOCATABLE-01, R7F-EXIT3-SEMANTICS-01, PREWINDOW-V5-PIN-01 and
    # CHARTER-V3-PACKET-INPUTS-01, which it counted as the 3rd-6th
    # "ruled != installed" instances since T26-RULING-INSTALL-01 was created to
    # cure exactly that pattern).
    "LINEAGE-RELOCATABLE-01",
    "LINEAGE-RESOLVE-RACE-01",
    "ONE-USE-CONSUMPTION-TEST-01",
    "RAW-CAPTURE-DIGEST-01",
    "SILENT-REFUSAL-TESTS-01",
    "CANONICAL-JSON-ONE-HOME-01",
    "INSTRUMENT-PATH-PIN-01",
    "GENERATOR-CORE-01",
    # 2026-09-08 T38 bookkeeping: WATCHDOG-INSTALL-01 retired (all four acceptance
    # items satisfied by the 09-06 install and the 00:51:55 activation); eight
    # rows added — six follow-ups from the handoff-redo gauntlets plus the two
    # open lanes (G2-a chain routing, iCloud backup probe).
    # 2026-09-08 T38b: routing and iCloud probe retired after main merges.
    "D169-STAGE3-01",
    "G2A-FIRST-WINDOW-01",
    "G2A-PREFLIGHT-ARGV-ASSERT-01",
    "ICLOUD-CUSTODY-LOCATOR-01",
    "WATCHDOG-NITS-01",
    "WINDOW-STATUS-GUARD-CENSUS-01",
    "CHARTER-V3-PACKET-INPUTS-01",
    # 2026-09-02 paper-d fixture-shape cold gate (files 38-42).
    "DG071-PROVENANCE-TEST-01",
    # 2026-09-03 V5 floor-generator counter-review CR-3 on branch
    # feat/2026-09-02-v5-floor-generator.
    "FLOOR-V5-DRIFT-REPIN-01",
    # 2026-08-27 T26 end-of-sprint kernel wave (WAVE-ROWS.md ledger: S5 sweep,
    # paper ruling item 16, D-156 Q1-B/Q4-B, S2 producers, S11 F4, D-160 R-3
    # in flight, D-158 A-5, D-160 R-4, D-158 R-3, S3 delta2 D4/D3, S9-04/09/10/11/12/13)
    "TRANSFER-FIDUCIAL-01",
    "SUPERSESSION-CHAINED-RECOVERY-01",
    "SUPERSESSION-CROSS-CONSUMER-DIVERGENCE-01",
    "T0-REHEARSAL-PRODUCERS-01",
    "COLLECTOR-MANIFEST-SHA-IDENTITY-01",
    "PIPELINE-SMOKE-TIER2-01",
    "PIPELINE-SMOKE-LIVE-01",
    # 2026-08-28 T27 second kernel wave (WAVE-ROWS.md post-#220 sections:
    # prune ruling R-7, D-160 addendum F2/F3 drafts, D-161 (1) lane on PR #228).
    "THREAT-MODEL-PRUNE-01",
    "BRACKET-EVALUATOR-PLAN-IDENTITY-01",
    "CONSUMPTION-SESSION-IDENTITY-PARAM-01",
    "PINSET-REFRESH-LANE-01",
    "GAMMA-UNIT-ROSTER-GUARD-01",
    "AUTHENTICATOR-ALLOWLIST-GUARD-01",
    "TRANSACTION-RULED-ARTIFACTS-01",
    "REISSUE-V3-GENERATION-GUARD-01",
    "L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01",
    # 2026-09-01 ruling 89 R-1: the pre-window prefix of the L10 ladder,
    # split out so V5-TRANSACTION-01 can gate on a row that closes before
    # the window (the parent row now closes after L10-C, post-transaction).
    "L10-A-G2B-CONTRACT-PREFIX-01",
    "RECORDER-SINGLE-OPERATOR-PREAMBLE-01",
    "ARM-PACKET-01",
    "CALEXITS-EVIDENCE-BYTES-01",
    "D144-SEATPASS-FOLLOWUPS",
    "ED-HANDS-BATCH-01",
    "EDQ-L9-3-CAPTURE-01",
    "MIDCAMPAIGN-CURE-GENERATION-01",
    # (PAPER-REPLAY-FENCE-01 closed 2026-08-25 on PR #189 (94a93e3a squashed
    # to main at b186710a): 43/43 fenced values live-re-derived and matched,
    # no joulewise/ or ESTIMATOR_CODE_PATHS-pinned file touched.)
    "PINSET-GRAMMAR-EXCLUSION-01",
    # (MLX-ACID-SIGABRT-01, CALEXITS-FOURTH-SHAPE-01 and PLANTEST-RGLOB-RACE-01
    # closed 2026-08-27 on PR #203. The first was cured there; the other two
    # were already cured on main -- ddb1f633 and a28b55bf -- and the rows simply
    # predated their cures. CALEXITS-EVIDENCE-BYTES-01 stays live: its reported
    # deterministic failure does not reproduce at the bench.)
    "REGISTRY-ID-NAMING-01",
    "V4-TRANSACTION-01",
    # D-167 replaces the retired Qwen2.5 _v3 windows and the three unstarted
    # readiness-sitting rows with the live Qwen3 _v5 chain and the later _v6
    # scored leg.
    "V5-G2A-PREFILL-PROBE-01",
    "V5-DESK-DAY-01",
    "V5-G2B-SHAKEDOWN-01",
    "V5-TRANSACTION-GO-01",
    "V5-TRANSACTION-01",
    "V5-NIGHTLY-G3-01",
    # D-168 registers the close-out chain and the 126-key renderer successor.
    "RENDERER-V5-SUCCESSOR-01",
    "D165-E2E-REPLAY-01",
    "V6-TOKEN-PIN-BINDING-01",
    "V6-SCORED-LEG-01",
    # 2026-09-02 projection-02 merge (PR #269): its ruling-150a follow-up (the
    # launch-step realization recheck) and the ruling-171a decode-identity fix
    # replace the retired projection-02 row.
    "V5-LAUNCH-REALIZATION-RECHECK-01",
    # 2026-09-02 bench sweep: the T26 cold-gate verdicts (items 1-4,
    # docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md)
    # were found uninstalled; one installing row plus the two Ed items the
    # ruling routed (E1 branch protection, E2 the D-118 N/A tier).
    "T26-RULING-INSTALL-01",
    # 2026-09-02 T26 fix round 1 (dx/t26-a cold gate B3): D-110 reconcile row.
    "D110-MINT-DEP-RECONCILE-01",
    # 2026-09-02 dx/t26-a cold gate: ruling A2 (prose scan row) + B4 (S9 rows)
    "R7F-DX-PROSE-SCAN-01",
    "S9-01B-REFUSAL-PRODUCER-CHECK-01",
    "S9-02-W10-SCOPE-P256-M1-01",
    "S9-03-GAMMA-PREFILL-PROMPT-OWNER-01",
    "S9-05-CAL-SCREEN-FLOOR-RULING-01",
    "S9-06-WINDOW-T0-GO-RECEIPT-GATE-01",
    "ED-D118-NA-TIER-E2-01",
    # 2026-08-25 T23-night kernel wave: the three D-153-sweep follow-ups the
    # rulings reserved for the kernel — synthesis R-5 (epoch lint), synthesis
    # R-4's registration of Opus finding 3f (consume-side supply line), and
    # the joint delta re-audit's adjudication item 4 (006-* guard strength).
    "LINE-AUDIT-GUARD-01",
    # [AGENT]
    # 2026-08-15 council Phase-1 repair program. The landed U11 identity
    # projection and FLOOR-COMMONMODE rows retired when these successors
    # entered the live kernel.
    # (WO-T0-PRODUCER and WO-MARGIN-RECORDER-AUTHZ retired 2026-08-15 when
    # #152/#151 merged; WO-RECORDER-GRANT-IDENTITY entered per the
    # recorder-race composed verdict.)
    # (WO-L2-REAUDIT retired 2026-08-16: delivered, Coverage VERIFIED,
    # custody docs/process_traces/2026-08-15-l2-reaudit/.)
    "WO-LAUNCH-BINDING", "WO-CONSUMPTION-EDGE",
    "WO-CENSUS-SEMANTICS",
    "WO-DETECT-PULSES-BUDGET",
    # (WO-RECORDER-GRANT-IDENTITY retired 2026-08-17 by D-139 A1 —
    # in-process adversary ruled out of model; registered limitation stands.)
    "WO-PROOF-RUNNABILITY-REPAIR",
    "P2-036", "P3-000", "P2-022", "P2-023",
    "P2-024", "P3-001b", "P2-004", "P2-005", "P2-016",
    "P2-048", "TOOL-01",
    "CI-003", "DOC-010",
    "DOC-008", "DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS",
    # audit close-out promotions (2026-07-15): deferred fix-wave orders
    "AUD-WO-033", "AUD-WO-034", "AUD-WO-035", "AUD-WO-036",
    "AUD-WO-037", "AUD-WO-038", "AUD-WO-039", "AUD-FOLLOWUPS",
    # D-078 confirmation-round-9 follow-up
    "FLOOR-BIND-01",
    # C-045 screen+budget gauntlet deferrals (2026-07-25).
    # CUSTODY-HARDEN-01 closed in PR #285 and left the live kernel.
    # 2026-07-25 attribution-limit adjudication (FLOOR-LABEL-01 completed
    # 2026-07-27 at 3055315 and left the live kernel)
    # 2026-07-29/30 mint-arc intake (82ca955; kernel rows added by ruling).
    # STACK-ID-BIND-01 completed 2026-07-30 in PR #88 (da83337).
    # MODULARITY-01 v2 closed in PR #285; its residuals remain preserved in
    # the D-174-shelved MODULARITY-FOLLOWUPS-01 row below.
    # 2026-07-30 cold-gate intake fold (D-088; PR #88 merge session).
    # COOLDOWN-JOIN-GAUNTLET-01 + QA-10A/QA-10B closed 2026-08-02 with
    # commit 3 (PR #93) and retired to the completed table.
    # MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95, v3 at audited head
    # e94d4a7) and retired to the completed table.
    "MINT-GENERALIZE-01",
    # 2026-08-02 successor session: TEST-SPEED-01 minted per the
    # checkpoint resume script (Ed-ratified three levers 2026-08-03).
    "TEST-SPEED-01",
    # COOLDOWN-JOIN-DA1-01 was folded in 2026-07-31 (D-093) as P2-015
    # retired, and closed the same day inside the gauntlet's commit 2
    # (e749c95, PR #91 67d268a); it left the live kernel at close-out.
    # AXI extension agenda (D-070 + binding xhigh sequencing amendments);
    # AXI-SB-ADAPTER minted 2026-07-16 on the AXI-SB supported verdict
    "AXI-SB-ADAPTER", "AXI-SD", "AXI-SE",
    # 2026-08-01 metrology adjudication session (D-098..D-101):
    # MET-VERDICT-ADJ-01 was minted, completed the same day (D-100), and
    # left the live kernel. MET-DANGLER-DISPOSITION-01 (+ folded
    # MEMBERSHIP-READER-FAILOPEN-01) closed 2026-08-02 with PR #94
    # (audited head 05d99b6) and retired to the completed table.
    # 2026-08-02 D-106 clause 3 minted D100-BII-BINDING-01 (b-ii
    # capture-identity fixes); closed 2026-08-03 under D-108 (PR #99
    # merged 32d72fd + the clause-(d) three-occurrence re-record) and
    # retired to the completed table.
    # 2026-08-02 D-105 registration (C3 gauntlet close-out)
    "C3-RECOGNIZER-EXACT-01",
    "CALEXITS-HYGIENE-FIXES-01",
    # 2026-08-22 T20 _v4-transaction registrations (D-150 item 4; D-151 +
    # marker-ruling consequences)
    "T0-CLOCK-ROW-RENAME-01",
    "T0-UNATTENDED-01",
    "T0-LIVENESS-BOUND-EMPIRICAL-01",
    "T0-PROBE-CENSUS-RESOURCE-01",
    "UNATTENDED-LAUNCH-01",
    # 2026-09-01 D-169 stage-1 split (MAGISTRATE-RULING-UNATTENDED-STAGE1,
    # cold gate coldgate-e10): night gate, night driver, launchd rehearsal
    "NIGHT-REHEARSAL-01",
    # FIXTURE-MODERNIZATION-01 closed in PR #285.
    # (CALWRITER-ACK-TIMEOUT-01 minted T20 on the second firing, broadened
    # to the shared driver at E-2, closed T22: H4 driver + 4s nominal cure,
    # both exclusive shards green at 42df510.)
    # (EVIDENCE-AUTHOR-GIT-TEARDOWN-01 registered on ERRATA E-1, fixed
    # ea90585 at the shared fixture site, closed same day on CI-green
    # acceptance — run conclusion-field-verified.)
    # 2026-08-02 two-lens extension consult (Ed ratifies S2)
    "NVIDIA-PORTABILITY-01",
    # 2026-08-03 sleep-window: production-default custody hardening deferred
    # from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake).
    "NODE-CUSTODY-DEFAULT-01",
    # 2026-08-03 16h runway: D-080 fresh-eyes trigger wiring
    # (sweep finding + Ed's concurrent-audit pattern). The D-112-parked
    # r06 disposition retired under D-113 in the 2026-08-05 batch.
    "D080-TRIGGER-01",
    # 2026-08-03 t3-drive chain mint (Ed directive ~23:55 + the t3-doctrine
    # gate synthesis): surviving agent-lane rows. COLDGATE-VALIDATOR-01
    # retired after PR #103 in the 2026-08-05 batch.
    "QUIET-GUARD-01", "SEC5A-REMOTE-01", "WO-T3-VIS-01",
    # 2026-08-05 registration batch: four agent-lane follow-ons.
    # (CODEX-BRIDGE-SANDBOX-01 closed 2026-08-25 with PR #191 — argv-capture
    # proof plus the source-level no-literal guard — and retired to the
    # completed table.)
    "T3-PROV-SCHEMA-01",
    "COLDGATE-HANDOFF-01", "CGV-HARDEN-01",
    # 2026-09-04 post-fan-out paper-supply program. The custody seam is the
    # active agent head; four supplier/cold-gate rows wait behind it, while
    # two governed receipt producers are independently queued. The Q-R1-2
    # composition proposal and doctrine-bearing skill distillation remain
    # blocked on their named cold gates.
    "PAPER-CUSTODY-SEAM-01",
    "D123-REPORTED-MEAN-SUPPLIER-01",
    "D165-OUTCOME-RENDERER-01",
    "GAMMA-CLAIM-RENDERER-01",
    "TRANSFER-RESULT-RENDERER-01",
    "WHOLE-WINDOW-STOP-RECEIPT-01",
    "CLAIM-NONISSUANCE-RECEIPT-01",
    "D173-PAPER-SUPPLY-COLD-GATE-01",
    "Q-R1-2-COMPOSITION-RULE-COLD-GATE-01",
    "SKILL-DISTILL-01",
    # Ruling 43 ratified ruling 17 as amended and opened six paper lanes.
    "DECISION-LOG-RATIFY",
    "D166-PROMPT0-01",
    # PR #285 closed MODULARITY-01 v2; the non-submission residue is retained
    # as a D-174-shelved successor record.
    "MODULARITY-FOLLOWUPS-01",
    # [QUIET-MAC]
    "MET-WINDOW-C-01",
    "P2-010", "P2-019", "P2-020",
    "P2-012", "P2-046B",
    # 2026-08-03 t3-drive chain mint: app-up vs app-down characterization
    # pair (NON-CLAIM), rank 7.
    "T3-CHAR-PAIR-01",
    # [ED-EXTERNAL]
    "ED-DATES-01", "P1-001", "P1-003", "P1-004", "P1-006",
}

TERMINAL_IDS = {"T0-CLEAN-TREE-CHECK-01", "KIND-TABLE-WINDOW-MUTANT-TEST-01",
                "ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01", "ESTIMAND-ENCLOSURE-01", "FB-PLANNING-METADATA-01", "D165-RELABEL-01", "PAPER-K",
                "CAL-REBRACKET-01", "P2-015-PREP", "P2-029", "P2-030", "P2-031", "P2-032", "P2-034",
                "AXI-SA", "AXI-SB", "AXI-SC", "P2-038", "P2-015-SMOKE", "SITE-02", "SPLIT-AP",
                "FLOOR-LABEL-01", "STACK-ID-BIND-01", "P2-015",
                "COOLDOWN-JOIN-DA1-01", "MET-VERDICT-ADJ-01",
                "COOLDOWN-JOIN-GAUNTLET-01", "QA-10A-JOIN-OMISSION",
                "QA-10B-EXISTING-RETRY",
                "MET-DANGLER-DISPOSITION-01", "MANIFEST-CONTRAST-01",
                "MEMBERSHIP-READER-FAILOPEN-01", "NVIDIA-RETENTION-FLAKE-01",
                "CAL-BRACKET-D079-01", "T3-AMEND-01",
                "COLDGATE-VALIDATOR-01", "WINB-R06-DISPOSITION-01",
                "CODEX-BRIDGE-SANDBOX-01",
                # 2026-08-27 T26 S5 test-reliability wave (PR #203).
                "MLX-ACID-SIGABRT-01", "CALEXITS-FOURTH-SHAPE-01",
                "PLANTEST-RGLOB-RACE-01",
                # 2026-08-27 T26 S3 pack-authentication soundness wave (PR #214).
                "FROZEN-RECEIPT-CONSTANT-STALE-01",
                "PACKAUTH-PRESERVE-TAUTOLOGY-01",
                # 2026-08-27 T26 S10 bracket-binding producer (PR #217).
                "BRACKET-BINDING-CLI-01",
                # 2026-08-28 T27 second kernel wave: retired unbuilt by the
                # threat-model prune ruling R-2 (D-161).
                "HISTPACK-PROMISOR-NOFETCH-01",
                # 2026-09-04 fan-out magistrate-rulings batch.
                "FLOOR-WORKLOAD-SIZING-01", "P1-008", "P2-027", "P2-035",
                "P2-047A", "P2-047B", "P2-050",
                "PHASE-SHARE-ESTIMAND-01", "PREWINDOW-REGEX-01",
                # 2026-09-04 merge-wave closures and retirements.
                "NIGHT-PLAN-PIN-01", "V5-DECODE-IDENTITY-SET-01",
                "EPOCH-LINT-01",
                # PR #285 terminal lanes. DOCS-VS-TRUTH and ONE-NAME-SWEEP
                # were fan-out seats rather than live kernel IDs, but their
                # terminal records belong in the completed table.
                "CUSTODY-HARDEN-01", "FIXTURE-MODERNIZATION-01",
                "DOCS-VS-TRUTH", "ONE-NAME-SWEEP",
                "R7F-EXIT3-SEMANTICS-01", "MODULARITY-01",
                "PREWINDOW-V5-PIN-01"}


def load_kernel():
    with open(KERNEL_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _adapt_retired_lane_heads(task_ids):
    """Rewrite frozen selection oracles to the current ruled lane heads.

    The oracles are hand-written and frozen; P2-015 was retired from the
    kernel on 2026-07-31, and R3 formally retired its former successor
    P2-006 on 2026-08-15. D-167 then retired D117-W-ALPHA and installed
    V5-G2A-PREFILL-PROBE-01 at rank 2 as the dependency-ready quiet-Mac
    head. The 2026-09-04 fan-out batch replaced P1-008 with ED-DATES-01.
    Patching here keeps the historical fixtures unchanged.
    """
    for index, task_id in enumerate(task_ids):
        if task_id in ("P2-015", "P2-006", "D117-W-ALPHA"):
            task_ids[index] = "V5-G2A-PREFILL-PROBE-01"
        elif task_id == "P1-008":
            task_ids[index] = "ED-DATES-01"
    return task_ids


def _adapt_retired_lane_heads_in_scenarios(scenarios):
    """Apply current ruled lane-head rewrites to frozen gate scenarios."""
    for scenario in scenarios:
        _adapt_retired_lane_heads(scenario["expected_selectable_task_ids"])
        for gate in scenario["active_global_gates"]:
            _adapt_retired_lane_heads(gate["allowed_task_ids"])
    return scenarios


def run_gen(*args):
    return subprocess.run(
        [sys.executable, GEN, *args], capture_output=True, text=True
    )


class TestKernelValidity(unittest.TestCase):
    def test_schema_declares_v3_work_selection_authority_contract(self):
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            schema = json.load(fh)
        self.assertEqual(schema["properties"]["schema_version"]["const"], 3)
        self.assertIn("active_global_gates", schema["required"])
        self.assertEqual(
            schema["properties"]["authority"]["const"],
            gen_state.AUTHORITY_NOTICE,
        )
        gate = schema["$defs"]["globalGate"]
        self.assertEqual(gate["properties"]["scope"]["properties"]["operation"]["const"],
                         "select")
        self.assertEqual(
            set(gate["properties"]["scope"]["properties"]["lanes"]["items"]["enum"]),
            set(gen_state.LANES),
        )
        self.assertTrue(
            {"p3_hardening_candidates", "p3_tooling"}.issubset(
                schema["$defs"]["task"]["properties"]["priority"]["enum"]
            )
        )

    def test_kernel_validates(self):
        gen_state.validate(load_kernel())

    def test_kernel_bytes_are_canonical(self):
        with open(KERNEL_PATH, "rb") as fh:
            raw = fh.read()
        self.assertEqual(raw, gen_state.canonical_bytes(json.loads(raw.decode("utf-8"))))

    def test_satisfied_decision_dependency_requires_named_test_regression(self):
        kernel = load_kernel()

        def dependency(path, label):
            return {
                "evidence": {"path": path, "label": label},
                "kind": "decision",
                "required": "fixture decision dependency",
                "scope": "close",
                "state": "satisfied",
                "strength": "hard",
                "target": "D-170",
            }

        with self.subTest(mutation="M6b README placeholder pointer"):
            with self.assertRaisesRegex(
                gen_state.KernelError,
                r"D-170.*test file under tests",
            ):
                gen_state._check_dependency(
                    dependency("README.md", "placeholder pointer"),
                    "tasks[T26-RULING-INSTALL-01].dependencies[0]",
                    kernel,
                )

        with self.subTest(mutation="named producer regression is accepted"):
            gen_state._check_dependency(
                dependency(
                    "tests/test_docs_freshness.py",
                    "test_open_decisions_name_an_installing_kernel_task",
                ),
                "tasks[T26-RULING-INSTALL-01].dependencies[0]",
                kernel,
            )

        with self.subTest(mutation="nonexistent test label"):
            with self.assertRaisesRegex(
                gen_state.KernelError,
                r"D-170.*name a test defined in",
            ):
                gen_state._check_dependency(
                    dependency("tests/test_docs_freshness.py", "test_does_not_exist"),
                    "tasks[T26-RULING-INSTALL-01].dependencies[0]",
                    kernel,
                )

    def test_invalid_kernels_rejected(self):
        base = load_kernel()
        # Gate-shaped mutations need a live gate; the audit gate was CLEARED
        # 2026-07-15 (Ed's adoption merge), so inject the frozen historical
        # gate artifact for mutation purposes.
        base["active_global_gates"] = copy.deepcopy(
            load_fixture("historical_audit_gate.json")["active_global_gates"])
        cases = [
            ("unknown top-level field", lambda k: k.update(surprise=1)),
            ("bad schema_version", lambda k: k.update(schema_version=1)),
            ("missing authority", lambda k: k.pop("authority")),
            ("altered authority", lambda k: k.update(authority="AUTHORITATIVE")),
            ("missing active_global_gates", lambda k: k.pop("active_global_gates")),
            ("bad gate operation",
             lambda k: k["active_global_gates"][0]["scope"].update(operation="run")),
            ("unknown gate lane",
             lambda k: k["active_global_gates"][0]["scope"]["lanes"].append("cloud")),
            ("duplicate gate id",
             lambda k: k["active_global_gates"].append(
                 copy.deepcopy(k["active_global_gates"][0]))),
            ("non-live gate allowlist ID",
             lambda k: k["active_global_gates"][0]["allowed_task_ids"].append("NOPE-1")),
            ("id/key mismatch", lambda k: k["tasks"]["P2-016"].update(id="P2-999")),
            ("terminal status", lambda k: k["tasks"]["P2-016"].update(status="done")),
            ("duplicate lane rank", lambda k: k["tasks"]["P2-016"].update(rank=1)),
            ("blocked without hard start dep", lambda k: k["tasks"]["ED-DATES-01"].update(status="blocked")),
            # P2-024 carries the pending edge these dependency-shaped
            # mutations need.
            ("queued with hard start dep", lambda k: k["tasks"]["P2-024"].update(status="queued")),
            ("dangling pending task dep",
             lambda k: k["tasks"]["P2-023"]["dependencies"][1].update(target="NOPE-1")),
            ("self-dependency",
             lambda k: k["tasks"]["P2-023"]["dependencies"][1].update(target="P2-023")),
            ("pending dep with evidence",
             lambda k: k["tasks"]["P2-023"]["dependencies"][1].update(
                 evidence={"path": "docs/decision_log.md", "label": "x"})),
            ("missing pointer target",
             lambda k: k["tasks"]["P2-016"]["authority"].update(path="docs/does_not_exist.md")),
            ("absolute pointer path",
             lambda k: k["tasks"]["P2-016"]["authority"].update(path="/etc/passwd")),
            ("pipe in goal", lambda k: k["tasks"]["P2-016"].update(goal="a | b")),
            ("unknown flag", lambda k: k["tasks"]["P2-016"].update(flags=["nope"])),
            ("quiet_mac without lead_only",
             lambda k: k["tasks"]["P2-019"].update(flags=[])),
            ("blocked_post_2m without P2-006 dep",
             lambda k: k["tasks"]["P2-022"].update(
                 flags=["blocked_post_2m"])),
            ("DOC-010 missing G6 dependency",
             lambda k: k["tasks"]["DOC-010"].update(
                 dependencies=[d for d in k["tasks"]["DOC-010"]["dependencies"]
                               if d["target"] != "G6"])),
        ]
        for name, mutate in cases:
            kernel = copy.deepcopy(base)
            mutate(kernel)
            with self.assertRaises(gen_state.KernelError, msg=name):
                gen_state.validate(kernel)

    def test_cycle_rejected(self):
        # The desk day already carries a pending hard start edge to G2-a;
        # closing the edge back from G2-a makes a genuine cycle. Both ends are
        # blocked so invariant 3 passes and the cycle check is what fires.
        kernel = copy.deepcopy(load_kernel())
        kernel["tasks"]["V5-G2A-PREFILL-PROBE-01"]["dependencies"] = [
            {"kind": "task", "target": "V5-DESK-DAY-01", "required": "cycle",
             "state": "pending", "strength": "hard", "scope": "start",
             "evidence": None}
        ]
        kernel["tasks"]["V5-G2A-PREFILL-PROBE-01"]["status"] = "blocked"
        with self.assertRaisesRegex(gen_state.KernelError, "dependency cycle"):
            gen_state.validate(kernel)


class TestRefreshedStateFidelity(unittest.TestCase):
    """Assertions against the final C-028 live-state refresh."""

    def setUp(self):
        self.kernel = load_kernel()
        self.tasks = self.kernel["tasks"]

    def test_exact_live_id_set(self):
        # The prior 67-row live set loses landed U11/FCM and R3-retired
        # P2-006, then gains three D-117 windows and seven Phase-1 work
        # orders (67 - 3 + 10 = 74); the 2026-08-15 refresh retires merged
        # WO-T0-PRODUCER (#152) and WO-MARGIN-RECORDER-AUTHZ (#151) and adds
        # WO-RECORDER-GRANT-IDENTITY and (2026-08-16) the proof-runnability
        # repair (74 - 2 + 2 = 74); the T9 close retires delivered
        # WO-L2-REAUDIT (73); D-139 A1 retires WO-RECORDER-GRANT-IDENTITY:
        # 73 - 1 = 73; the 2026-08-20 gate-1 fix gauntlet mints
        # RECEIPT-HISTSEM-01 (C1): 73 + 1 = 74; the D-144 seat pass mints
        # D144-SEATPASS-FOLLOWUPS (75); the 2026-08-20 sitting/plan close
        # retires REFREEZE-D147-CLOSE (74) and mints V4-TRANSACTION-01,
        # SITTING2-PRECONDITIONS-01, READY-WO-BATCH-01,
        # UNVERIFIED-REAUDIT-01, ED-HANDS-BATCH-01, PREWINDOW-REGEX-01:
        # 74 + 6 = 80; the S-4 refuter round splits out ED-MINT-LICENSE-01,
        # EDQ-L9-3-CAPTURE-01 and mints FREEZE-REPLAY-EXPIRY-01,
        # PROC-TEARDOWN-01, REAUTHOR-CLEAN-01, ARM-PACKET-01:
        # 80 + 6 = 86; the 2026-08-20 evening closure retires
        # FREEZE-REPLAY-EXPIRY-01, PROC-TEARDOWN-01, REAUTHOR-CLEAN-01
        # (PRs #162/#163/#164): 86 - 3 = 83; T19 registers four calexits
        # successor rows and retires RECEIPT-HISTSEM-01: 83 - 1 + 4 = 86;
        # T19 closure #2 retires the CI311 and census PID rows: 86 - 2 = 84;
        # the 2026-08-22 closure retires N-5-RECORD-AMENDMENT (record
        # amended per cold-pair-166 R2.3): 84 - 1 = 83; the same day closes
        # CALEXITS-TIMING-HYGIENE (audit delivered) and registers its
        # successor CALEXITS-HYGIENE-FIXES-01: 83 - 1 + 1 = 83; the T20
        # _v4-transaction wave registers T0-UNATTENDED-01, S1-CANDIDATE-01,
        # S0-RUNSHEET-R2 (D-150 item 4; D-151 + marker-ruling
        # consequences): 83 + 3 = 86; the T20 close-out registers
        # CALWRITER-ACK-TIMEOUT-01 on the flake's second same-day firing:
        # 86 + 1 = 87; the T20 errata wave registers
        # EVIDENCE-AUTHOR-GIT-TEARDOWN-01 (E-1, required-shard red):
        # 87 + 1 = 88; closed same day at ea90585: 88 - 1 = 87; the T22
        # merge-wave closure retires S1-CANDIDATE-01 (merged 3c098de,
        # CI green 42df510) and CALWRITER-ACK-TIMEOUT-01 (H4 driver +
        # nominal cure, both shards green 42df510) and registers
        # FIXTURE-MODERNIZATION-01 + MLX-ACID-SIGABRT-01:
        # 87 - 2 + 2 = 87; S0-RUNSHEET-R2 closed on the lead's completed
        # pre-execution read (anchor map + two execution-blocking defects
        # caught and fixed: builder chain composition f6a4c81, section-1.3
        # superseded-by-merge f692e26): 87 - 1 = 86; the T22 night T0
        # synthesis ruling (two-seat blind co-design + debate, converged)
        # registers UNATTENDED-LAUNCH-01 (launch-blocker separation, both
        # seats co-signed) and T0-CLOCK-ROW-RENAME-01 (coupled rename +
        # horizon churn, post-_v4 gated): 86 + 2 = 88; the 2026-08-24
        # kernel wave closes ED-MINT-LICENSE-01 (D-150 item 1 supersedes
        # the settings-rule form; the V4-TRANSACTION-01 dependency flips
        # to satisfied) and registers CALEXITS-EVIDENCE-BYTES-01
        # (pre-existing deterministic bench failure, distinct from both
        # diagnosed CI-red classes) and REGISTRY-ID-NAMING-01 (S-0
        # packet-1 cold-gate free finding, fenced post-_v4):
        # 88 - 1 + 2 = 89; the 2026-08-24 morning wave registers
        # CALEXITS-FOURTH-SHAPE-01 (run 32739939880's fourth terminal
        # shape on a both-cures branch), PLANTEST-RGLOB-RACE-01 (the
        # checkout_inventory scandir race, run 32745254371), and
        # PAPER-REPLAY-FENCE-01 (the retained §2-fill replay fence,
        # acceptance item 3 of the retention verification):
        # 89 + 3 = 92; the 2026-08-24 T23 evening wave registers the two
        # pending D-153 packet-5 work orders — WINDOW-STATUS-FREEZE-GUARD-01
        # (W4, the status publisher's commit inside the freeze span) and
        # MIDCAMPAIGN-CURE-GENERATION-01 (W5, the registered mid-campaign
        # cure limitation) — plus the two independent soundness rows from
        # the S-0 §3.4 round, FROZEN-RECEIPT-CONSTANT-STALE-01 and
        # PACKAUTH-PRESERVE-TAUTOLOGY-01, and the PR #182 pinset-builder
        # should-fix PINSET-GRAMMAR-EXCLUSION-01:
        # 92 + 5 = 97; the 2026-08-25 T23-night wave closes
        # PAPER-REPLAY-FENCE-01 (PR #189, 94a93e3a squashed to main at
        # b186710a; 43/43 fenced values live-re-derived and matched, no
        # joulewise/ or pinned-file change) and registers the three
        # D-153-sweep follow-ups the rulings reserved for the kernel —
        # EPOCH-LINT-01 (synthesis R-5, the three dependency kinds the
        # $TRANS producer/consumer sweep cannot see),
        # CONSUME-CONFIRMATION-SUPPLY-01 (synthesis R-4's registration of
        # Opus finding 3f), and LINE-AUDIT-GUARD-01 (joint delta re-audit
        # adjudication item 4):
        # 97 - 1 + 3 = 99; the 2026-08-25 T24 S-0-closure wave closes
        # CODEX-BRIDGE-SANDBOX-01 (PR #191, 9fd185ac: argv-capture proof plus
        # the source-level no-literal guard; all three acceptance bullets met)
        # and registers the two rows the S-0 close-out reserved —
        # MINT-CHECKOUT-DECLARATION-01 (D-154 ruling R-3, the mint-time
        # measurement-checkout declaration check that re-sites the locality
        # lens the R-1 replay cure retired, fenced outside the transaction
        # window) and ARM-PACKROOT-COMPARISON-01 (the PR #192 refuter's D7
        # finding: the two arm-side whole-dict pack comparisons repeat the
        # untruthful bytes-differ detail on a location-only difference):
        # 99 - 1 + 2 = 100; the 2026-08-26 T26 reconciliation closes
        # WINDOW-STATUS-FREEZE-GUARD-01 (already landed by D-155 W-2, PR #199
        # at 3c96b18f: freeze-span sentinel + tests/test_window_status_guard.py;
        # the row predated its cure):
        # 100 - 1 = 99; the 2026-08-27 T26 s1-consume-supply wave closes
        # CONSUME-CONFIRMATION-SUPPLY-01 (PR #204, 318f5a70:
        # scripts/launch_window.py gains --step6-confirmation-table and
        # forwards it at all four sites that already forward the digest, so
        # the real transaction's consume-side C-to-S gate refuses on
        # "bytes differ from the confirmed digest" rather than for want of an
        # input; seven regressions including a real-chain reach proof down to
        # _authenticate_confirmation_table):
        # 99 - 1 = 98;
        # the 2026-08-27 T26 S5 test-reliability wave closes
        # MLX-ACID-SIGABRT-01 (PR #203: the nanobind double-registration abort
        # cured code-side on both halves -- an adapter-owned handle on the
        # imported extension plus single-key sys.modules patching in
        # author_environment; the four ACID tests stay skipped on A84 alone),
        # CALEXITS-FOURTH-SHAPE-01 (already landed at ddb1f633: the
        # absent-pack-child shape of run 32739939880 classifies NO_PACK_CHILD
        # and the mutation test guards its completeness assertion; shapes A-E
        # each carry a synthetic-topology regression) and
        # PLANTEST-RGLOB-RACE-01 (already landed at a28b55bf: checkout_inventory
        # prunes the git object store before descending, with three
        # deterministic vanishing-directory regressions) -- the latter two rows
        # predated their cures:
        # 98 - 3 = 95; the 2026-08-27 T26 S6 wave closes
        # SUPERSESSION-DUP-REFUSAL-01 (PR #206, 36dcdd76: D-156's
        # write-time refusal in the supersession recorder -- a recognizable
        # same-bundle_id row in the target log, valid or not, refuses before
        # the candidate row is constructed, and a log the consumer reader
        # cannot reason about refuses under its own sibling code):
        # 95 - 1 = 94; the 2026-08-27 T26 S3 pack-authentication soundness
        # wave closes FROZEN-RECEIPT-CONSTANT-STALE-01 (PR #214: the adopted
        # ruling is that CURRENT_FROZEN_RECEIPT_SHA256 is never refreshed and
        # the authentication path stops depending on it -- refreshing is
        # impossible because a successor generator is emitted before its own
        # freeze receipt exists and editing it after the mint would change
        # frozen pack bytes; recorded normatively in
        # docs/contracts/receipt_histsem_verifier.md and pinned by
        # test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict).
        # Its branch-mate PACKAUTH-PRESERVE-TAUTOLOGY-01 closes on the same
        # PR after a magistrate-authorized second fix round cured the delta
        # re-audit's D1 blocker -- flagless-generator preserve detection was a
        # name scan, so an echo written under another identifier was recorded
        # as regenerated; flagless generators are now default-denied and
        # admitted only by exact SHA-256 membership in a closed allowlist of
        # reviewed historical generators, and the second fresh delta re-audit
        # returned no blocker findings with A94 MET:
        # 94 - 2 = 92;
        # 92 - 2 = 90; the 2026-08-27 T26 s4-d154-followons wave closes
        # MINT-CHECKOUT-DECLARATION-01 and ARM-PACKROOT-COMPARISON-01
        # (PR #208: the mint-time measurement-checkout declaration gate
        # with its ninth ruled registry vocabulary entry, and the
        # successor-scoped field-wise arm pack comparisons with truthful
        # per-branch details):
        # 92 - 2 = 90;
        # 90 + 18 = 108; the 2026-08-27 T26 end-of-sprint wave registered
        # the eighteen WAVE-ROWS.md ledger rows (GIT-FIXTURE-MAINTENANCE-SWEEP-01,
        # TRANSFER-FIDUCIAL-01, the two D-156 supersession residuals,
        # T0-REHEARSAL-PRODUCERS-01, COLLECTOR-MANIFEST-SHA-IDENTITY-01,
        # BRACKET-BINDING-CLI-01 (subsequently closed via PR #217),
        # T0-ENV-PARSER-UNIFY-01,
        # PIPELINE-SMOKE-TIER2-01, PIPELINE-SMOKE-LIVE-01, the two HISTPACK
        # rows from S3 delta2, and the six S9 should-fixes):
        # 90 + 18 = 108;
        # 108 - 2 = 106: the 2026-08-27 T26 S13 stream closes
        # HISTPACK-TEMP-CLEANUP-01 (PR #222: the histsem scratch checkout
        # is unwound before raising) and S10 closes BRACKET-BINDING-CLI-01
        # (PR #217 producer + PR #223 runbook); the 2026-08-28 T27 S12
        # stream closes T0-ENV-PARSER-UNIFY-01 (PR #221: one shared 25-key
        # window.env contract at both T-0 boundaries):
        # 106 - 1 = 105;
        # 105 - 1 + 4 = 108: the 2026-08-28 T27 second kernel wave retires
        # HISTPACK-PROMISOR-NOFETCH-01 unbuilt (threat-model prune ruling
        # R-2) and registers THREAT-MODEL-PRUNE-01 (prune ruling R-7),
        # BRACKET-EVALUATOR-PLAN-IDENTITY-01 and
        # CONSUMPTION-SESSION-IDENTITY-PARAM-01 (D-160 addendum F2/F3
        # drafts), and PINSET-REFRESH-LANE-01 as partial on PR #228
        # (D-161 (1)); PIPELINE-SMOKE-LIVE-01 re-scoped to D-162 G1/G2/G3:
        # 105 - 1 + 4 = 108. D-167 retires the three D-117 windows and the
        # three unstarted readiness-sitting rows, then installs eight _v5/_v6
        # rows: 108 - 6 + 8 = 110 exact live records. D-168 then registers
        # four close-out and renderer rows: 110 + 4 = 114. Ruling 89 R-1
        # (2026-09-01) splits L10-A-G2B-CONTRACT-PREFIX-01 out of the L10
        # row: 114 + 1 = 115. The D-169 stage-1 ruling (2026-09-01) splits
        # three night rows out of UNATTENDED-LAUNCH-01: 115 + 3 = 118; #258
        # registers its two realized-prefill rows: 118 + 2 = 120; IDS-CHECK
        # retired at the #258 merge (4a41d791): 120 - 1 = 119; the
        # NIGHT-GATE-01, NIGHT-DRIVER-01, D165-CLOSEOUT-CORE-01 retired at their
        # 2026-09-02 merges (PRs 264, 265, 261): 119 - 3 = 116;
        # D165-SIDECAR-EMIT-01 retired at its 2026-09-02 merge (PR 267):
        # 116 - 1 = 115; PROJECTION-02 retired (#269) while
        # LAUNCH-REALIZATION-RECHECK-01 and DECODE-IDENTITY-SET-01 registered
        # (6075389a): 115 - 1 + 2 = 116; 2026-09-02 T26 install wave registers
        # T26-RULING-INSTALL-01, ED-BRANCH-PROTECTION-E1-01,
        # ED-D118-NA-TIER-E2-01, and D110-MINT-DEP-RECONCILE-01: 116 + 4 = 120;
        # the dx/t26-a cold gate (2026-09-02, sections A2 and B4) registers
        # R7F-DX-PROSE-SCAN-01 and the five S9 rows not already in the kernel
        # (01b, 02, 03, 05, 06): 120 + 6 = 126; the T26 item-3 lane
        # (2026-09-02, PHYS-1 limitation) registers
        # T0-LIVENESS-BOUND-EMPIRICAL-01: 126 + 1 = 127; the census-guard
        # cold gate (2026-09-02, files 22-25) registers
        # T0-PROBE-CENSUS-RESOURCE-01: 127 + 1 = 128; the paper-d
        # fixture-shape cold gate (2026-09-02, files 38-42) registers
        # DG071-PROVENANCE-TEST-01: 128 + 1 = 129. The 2026-09-03 post-merge
        # kernel batch registers thirteen rows and retires none (retirements in
        # that batch are recorded as `shelved`, which keeps the row live in the
        # kernel and therefore in this set): 129 + 13 = 142; the V5
        # floor-generator counter-review CR-3 row adds one: 142 + 1 = 143.
        # The 2026-09-04 fan-out ruling batch retires nine rows (including
        # P2-047B with its retired P2-047A parent), then opens ED-DATES-01:
        # 143 - 9 + 1 = 135. The landing merge then retires NIGHT-PLAN-PIN-01,
        # V5-DECODE-IDENTITY-SET-01, and EPOCH-LINT-01 while registering the
        # custody seam, four suppliers, the D-173 and Q-R1-2 cold gates, two
        # governed receipt producers, and the held skill distillation:
        # 135 - 3 + 10 = 142. PR #285 then closes five of those live kernel
        # rows; ruling 43 opens six paper lanes and preserves modularity
        # residue in one shelved successor: 142 - 5 + 7 = 144.
        self.assertEqual(set(self.tasks), EXPECTED_IDS)
        self.assertEqual(len(self.tasks), 261)  # 2026-09-26 activation f8d6cab1: retire BFGD-VERDICT-MERGE-LIVENESS-01 after PR #426 merged (5d5a0b75); register HISTORICAL-BATTERY-STATE-01 and SCORED-CEILING-BATTERY-01 (Final texts v1.1 text 19); 260 - 1 + 2 = 261. 2026-09-26 activation ed17a643: register BATTERY-FLOAT-GATE-01, BFGD-VERDICT-MERGE-LIVENESS-01, TEST-LOAD-JOIN-LADDER-FLAKE-01; 257 + 3 = 260. 2026-09-25 activation ed17a643: register TIER01-PATH-GUARD-01 and TIER01-D118-RECONCILE-01 (TIER01-GATE-01 delta F2); 255 + 2 = 257. 2026-09-25 activation 152c9255 bookkeeping: 250 + 5 = 255. 2026-09-25 activation 152c9255: retire HEADLINE-PACKER-RECUT-01 after PR #409 merged (75d04e9e); 251 - 1 = 250. Same activation: seven follow-ups registered; 244 + 7 = 251. 2026-09-24 activation 278ebc9e: retire ED-BRANCH-PROTECTION-E1-01 (Ed applied branch protection, interactive 02a24110 record 01 §7); 245 - 1 = 244.  2026-09-24 activation a65fb4fa: retire A294/A295 after PR #403; 247 - 2 = 245.  2026-09-23 activation d8cc9c0a: A281 shelved, A291–A295 registered; 242 + 5 = 247. Earlier: 2026-09-23 activation 1d3796d5: retire A276/A277; register A280-A290: 233 - 2 + 11 = 242. # Earlier history follows.  # 2026-09-23 activation 4158e658 arm gate: register NOTICE-SUMMARY-V3-TEXT-01: 232 + 1 = 233. # 2026-09-23 activation 4158e658: register THROUGHPUT-01, BLOCK-TWO-DESIGN-01, PROMPT-AUDIT-01, CENSUS-MULTILINE-ARGV-01 (directive #386; owner session record 7ec32e8b records 04, 07): 228 + 4 = 232. # 2026-09-23 activation 7a0f14bd: register QPE01-ABORT-SUCCESSOR-01 (D-182 addendum, Ed-ratified) and FSEVENTSD-CORECAPTURED-PREDICATE-01 (owner session record 7ec32e8b §2): 226 + 2 = 228. # 2026-09-22 activation 22666c9f harvest record 01 §8: register QPE01-CLOCK-DISCIPLINE-ANCHOR-01, NIGHT-RESULTS-LARGE-FILES-01, ENVELOPE-START-DRIFT-01: 223 + 3 = 226. # 2026-09-21 activation ce7c57a9 packet 06 Q3: register ARM-VOCABULARY-GLOSSARY-01: 222 + 1 = 223. # 2026-09-21 activation ce7c57a9: retire NIGHT-ROOT-RETENTION-DISCOVERY-01, register MAGISTRATE-LAUNCH-WITHOUT-MCP-01 + CANONICAL-REFUSAL-STRINGS-01: 221 - 1 + 2 = 222. # 2026-09-20 activation 21752427, touch 6: register RUNBOOK-TRACKED-COMMANDS-01; no retirements: 220 + 1 = 221. 2026-09-19 activation a743be05 (Ed directives #367/#368, reply (c), rulings 04a/09a): register five lanes at ranks 254–258: 215 + 5 = 220. 2026-09-19 evening (activation d0b83820, PR #365 merged → main 4f2aa185): retires EVIDENCE-PLAN-PATH-BINDING-01 by removal: 216 - 1 = 215. 2026-09-19 evening (activation d0b83820, ruling 87a): registers EVIDENCE-PLAN-PATH-BINDING-01: 215 + 1 = 216. 2026-09-19 evening (activation d0b83820, PR #364 merged → main a9e48ae9): retires STAGE-A-EVIDENCE-EXECUTOR-01 by removal: 216 - 1 = 215. 2026-09-19 evening (activation d0b83820, ruling 83a after fresh-eyes 83): registers COURIER-DIAGNOSTIC-PERSISTENCE-01 and FIXTURE-TMPNAME-CENSUS-SUBSTRING-01: 214 + 2 = 216. 2026-09-19 late afternoon (activation d0b83820, ruling 79a after consult 79): registers COURIER-LOCK-OWNERSHIP-FLOCK-01 and COURIER-UNWRITABLE-CUSTODY-01: 212 + 2 = 214. 2026-09-19 afternoon (activation d0b83820): retires the generator byte-pin task after pull request #362 merged and registers the unattended evidence executor and file-based hosted test runner: 211 - 1 + 2 = 212. 2026-09-19 (headless activation d0b83820, n2-20260919 harvest FAIL, head-pin consult 07/07a and cold gate packet 09, records 01–30): registers REGISTRATION-NIGHT-COUNT-RULING-01, INSTRUMENT-CADENCE-ATTRIBUTION-25G83-01, GENERATOR-HEAD-FILE-BYTE-PIN-01, CI-DOCS-ONLY-SKIP-MASKS-RED-01, QUIET-LOAD-MEMORY-PROFILE-DIFFERENTIAL-01 and TEST-WRITES-PAPER-BUILD-ARTIFACT-01: 205 + 6 = 211. 2026-09-18 (headless activation 507514d5, PR #359 merged, hosted CI green on main 7faaf2d0, post-merge cross-unit look traced with no finding): retires TEST-LARGE-FRAME-ARGV-PORTABILITY-01 by removal: 206 - 1 = 205. 2026-09-18 (headless activation f0b608b7, arm record 21 follow-ups and record 19 root cause): registers TEST-LARGE-FRAME-ARGV-PORTABILITY-01, NIGHT-GATE-CROSS-SEAM-TESTS-01, QUIET-PREDICATE-STAGE-B-CONFIRMATION-01 and COURIER-SENT-FORMAT-PIN-01: 202 + 4 = 206. 2026-09-18 (interactive session 5c919872, PR #358 merged): retires NIGHT-GATE-QUIET-ADMISSION-01 by removal and registers BIND-REQUEST-PAYLOAD-CAP-01, QUIET-JOURNAL-REPLAY-CONTRACT-01 and TEST-BIND-SUPERVISION-ENV-SENSITIVITY-01: 200 − 1 + 3 = 202. 2026-09-17 (interactive session 5c919872, gate redesign after four zero-data nights): registers NIGHT-GATE-QUIET-ADMISSION-01, QUIET-PREDICATE-EVIDENCE-01, SPOTLIGHT-FSEVENTS-ATTRIBUTION-01 and WATCHDOG-EARLY-REFUSAL-RELEASE-01: 196 + 4 = 200. 2026-09-17 (activation 9853dd2b, arm record 77): registers TEST-WALLCLOCK-ABORT-FIXTURE-MARGIN-01 and NIGHT-ROOT-RETENTION-DISCOVERY-01 and retires PREREG-CHAIN-DIGEST-ADDENDUM-01 by removal (PR #355 merged): 195 + 2 - 1 = 196. 2026-09-17 (activation 9853dd2b, cold gate 69 pairing refuter B1): registers COLDGATE-CONVENE-DOCTRINE-FREE-01: 194 + 1 = 195. 2026-09-17 (activation 9853dd2b, abort-lane seat flag): registers PREREG-CHAIN-DIGEST-ADDENDUM-01: 193 + 1 = 194. 2026-09-17 (activation 9853dd2b, PR #350 and PR #352 merged, hosted CI green on main 5472ff53): retires DRIVER-REFUSAL-COLLISION-01 and CUSTODY-PASS-MEMO-01 by removal: 195 - 2 = 193. 2026-09-17 (activation 9853dd2b, NIGHT-RESERVE-HANG-01 reviews): registers CUSTODY-PASS-MEMO-01, PROBE-DRIVER-COPY-BINDING-01, NIGHT-DOCUMENT-HASH-BOUND-01 and CUSTODY-REAPING-ATTRIBUTION-01: 191 + 4 = 195. 2026-09-16 (activation 9853dd2b, launch record 00): registers WATCHDOG-BOOTID-CLOCK-STEP-01: 190 + 1 = 191. 2026-09-16 (interactive session 5239df1e, equivalence-night stall root cause): registers NIGHT-RESERVE-HANG-01, DRIVER-REFUSAL-COLLISION-01 and NIGHT-STALL-WALLCLOCK-ABORT-01: 187 + 3 = 190. 2026-09-16 (activation 0bd12d79, SIGARCH-article relay via the interactive session): registers PHASE-PARTITION-INVARIANT-01: 186 + 1 = 187. 2026-09-16 (activation 83d93f5a, Ed directive #349): registers NOTICE-TRANSPORT-FALLBACK-01: 185 + 1 = 186. 2026-09-16 (interactive session b0ae8462, merge wave): closes INSTALL-WINDOWS-MULTI-01, ARM-RETRY-CLASS-01, ARM-CENSUS-IDLE-INTERACTIVE-01, LEAD-MARGIN-01, FIXTURE-ORPHAN-SENTINEL-01 (PRs #341, #342, #343, #344, #345): 190 - 5 = 185. 2026-09-16 (activation 08ca8197, installer post-merge review): registers INSTALLER-FOLLOWUPS-REBASE-01 and RUNBOOK-SOURCE-MAP-01: 188 + 2 = 190. 2026-09-16 (activation 08ca8197, Ed meter purchase via the interactive session): registers WALL-METER-GAIN-01: 187 + 1 = 188. 2026-09-16 (activation 08ca8197, interactive nit): registers TEST-PGREP-DIALECT-MULTILINE-01: 186 + 1 = 187. 2026-09-16 (activation 08ca8197, Ed remark via the interactive session): registers REFUSAL-FAST-RETRY-01: 185 + 1 = 186. 2026-09-15 (activation 08ca8197, interactive record 16 F3): registers TEST-CANONICAL-PATH-DEPENDENCY-01: 184 + 1 = 185. 2026-09-15 (activation 08ca8197, Ed remark via the interactive session): registers LEAD-MARGIN-01: 183 + 1 = 184. 2026-09-15 (activation 08ca8197, Ed instruction via the interactive session): registers DATA-OFFLOAD-ICLOUD-01: 182 + 1 = 183. 2026-09-15 (activation 08ca8197, restart census): registers WORKTREE-PRUNE-01, TEMP-HYGIENE-IW-TMP-01 and FIXTURE-ORPHAN-SENTINEL-01: 179 + 3 = 182. 2026-09-15 (activation d6888966, lieutenant protocol finding): registers BRIDGE-BASELINE-COMPLIANCE-01: 178 + 1 = 179. 2026-09-15 (activation d6888966, cold gate 28 Q2 sibling): registers WATCHDOG-INSTALLER-VERIFIED-BOOTOUT-01: 177 + 1 = 178. 2026-09-15 (activation d6888966, cold gate 28 Q4 F4): registers INSTALLER-BACKUP-WINDOW-01: 176 + 1 = 177. 2026-09-15 (activation d6888966, cold gate 25 Q6): registers RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01: 175 + 1 = 176. 2026-09-15 (activation d6888966, record 19 bench replay): registers WATCHDOG-CLI-TEST-TMP-DISCOVERY-01: 174 + 1 = 175. 2026-09-15 (activation d6888966, GAMMA counter-review): registers PLAN-TREE-ROOTS-CONTRACT-01 and ROOT-NAMESPACE-FALLBACK-01: 172 + 2 = 174. 2026-09-15 (activation d6888966): registers WATCHDOG-STALE-EXIT-CLASS-01 and FIXTURE-FAKE-VLLM-LEAK-01: 170 + 2 = 172. 2026-09-14 20:55 (activation 24b9d3dd): closes ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 on Ed's probe record (record 75): 171 - 1 = 170. 2026-09-14 (activation 24b9d3dd, cold gate 65): registers PACK-ROOT-SUCCESSOR-V5-01: 170 + 1 = 171. 2026-09-14 (PR #330 merge of main): closes ESTIMAND-ENCLOSURE-01, FB-PLANNING-METADATA-01, D165-RELABEL-01 and PAPER-K (merged 2026-09-05/06, PRs #288/#290/#292/#293/#294): 174 - 4 = 170. Activation 24b9d3dd (2026-09-13) registers CALEXITS-RACE-FLAKE-01 (hosted race flake, p3): 173 + 1 = 174; the same day it closes NIGHT-CENSUS-CHATGPT-APP-01 (PR #334) and GATE-SENSIBILITY-SWEEP-01 (cold gate 47), registers GATE-B1-PROVENANCE-BAND-01: 174 - 2 + 1 = 173; earlier it registered ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 (ruling-first, from the pairing refuter on cold gate 05): 173 + 1 = 174. Activation c5048879 (2026-09-13) registers NIGHT-CENSUS-CHATGPT-APP-01 (ruling-first): 172 + 1 = 173. Activation f0d28baa (2026-09-12) closes FIXTURE-SENTINEL-CONTROLLER-01 (PR #324), RECOVER-SESSION-REFUSAL-WINDOW-EXHAUSTED-01 (PR #325) and GIT-FIXTURE-MAINTENANCE-SWEEP-01 (PR #326): 175 - 3 = 172; ARM-READINESS-FIXTURE-CLOCK-ORIGIN-01 (PR #327) was registered and closed in the same activation without a kernel row. Activation 36d3a823 adds four follow-ups; handback gloss evidence supplied.  T38l+ adds CONTRACT-TEMPORAL-HEDGE-GUARD-01; T38l adds EPOCH-CONTINUATION-01 and ISSUER-CHECK-CONTINUATION-AWARE-01; Activation 96bfeca7 final wave adds the doctrine-install obligation, the guard re-keying (ruling first) and the recover reason mapping; T38j adds the OS-build epoch blocker; Activation 96bfeca7 adds three follow-ups; T38g: D-180 (Ed, 2026-09-10) adds INSTALL-WINDOWS-MULTI-01, ARM-RETRY-CLASS-01, ARM-CENSUS-IDLE-INTERACTIVE-01, REMOTE-CONTROL-BETWEEN-WINDOWS-01; T38d + cold gate 44 lanes; NIGHT-GATE-STUB-CHAIN-01 (PR #309), FIXTURE-TIMEOUT-WALLCLOCK-01 (PR #310) and ARM-INTEGRATION-LOAD-01 (PR #311) DONE left the kernel

    def test_d176_ruling_installs_build_start_and_live_close_graph(self):
        # 2026-09-08 D-176 §5: this proves the installed scheduling boundary,
        # not live rehearsal acceptance; T38c separately records the merged consumer.
        ruling = (
            "docs/process_traces/2026-09-08-handoff-redo/"
            "78-coldgate-packet-d169-stage3/13-magistrate-synthesis.md"
        )
        def edges(task_id, scope):
            return {
                (d["kind"], d["target"], d["state"], d["strength"])
                for d in self.tasks[task_id]["dependencies"] if d["scope"] == scope
            }
        for task_id in ("UNATTENDED-LAUNCH-01", "T0-UNATTENDED-01", "D169-STAGE3-01"):
            with self.subTest(task=task_id):
                self.assertEqual(edges(task_id, "start"), {("decision", "D-176", "satisfied", "hard")})
        for task_id in ("UNATTENDED-LAUNCH-01", "D169-STAGE3-01", "NIGHT-PACK-REHEARSAL-01"):
            self.assertEqual(self.tasks[task_id]["authority"]["path"], ruling)
        self.assertIn(("task", "T0-UNATTENDED-01", "pending", "hard"), edges("UNATTENDED-LAUNCH-01", "close"))
        self.assertIn(("task", "UNATTENDED-LAUNCH-01", "pending", "hard"), edges("S9-06-WINDOW-T0-GO-RECEIPT-GATE-01", "close"))
        self.assertEqual(edges("D169-STAGE3-01", "close"), {
            ("event", "D176-DECISIONS-1-4-MERGED", "satisfied", "hard"),
            ("task", "NIGHT-PACK-REHEARSAL-01", "pending", "hard"),
        })
        self.assertEqual(edges("NIGHT-PACK-REHEARSAL-01", "start"), {
            ("task", "UNATTENDED-LAUNCH-01", "satisfied", "hard"),
            ("event", "UNINVENTORIED-REHEARSAL-CLONE-CUT", "pending", "hard"),
            ("task", "NIGHT-REHEARSAL-01", "pending", "hard"),
        })
        self.assertIn(("task", "NIGHT-PACK-REHEARSAL-01", "pending", "hard"), edges("V5-G2B-SHAKEDOWN-01", "start"))
        for task_id in ("UNATTENDED-LAUNCH-01", "T0-UNATTENDED-01", "D169-STAGE3-01"):
            self.assertTrue(gen_state._dependency_ready(self.tasks[task_id]))
        self.assertEqual(
            {d["target"] for d in gen_state._hard_start_blockers(self.tasks["NIGHT-PACK-REHEARSAL-01"])},
            {"UNINVENTORIED-REHEARSAL-CLONE-CUT", "NIGHT-REHEARSAL-01"},
        )
        rehearsal = self.tasks["NIGHT-PACK-REHEARSAL-01"]
        self.assertEqual(rehearsal["lane"], "agent")
        self.assertEqual(rehearsal["priority"], "p1_phase_gate")
        self.assertEqual(rehearsal["fences"], self.tasks["NIGHT-REHEARSAL-01"]["fences"])
        producers = self.tasks["T0-REHEARSAL-PRODUCERS-01"]
        self.assertNotIn("REHEARSAL_PRODUCER_WORK_ORDER", json.dumps(producers))
        self.assertTrue(producers["authority"]["path"].endswith("exhibit-A-consult-astra.md"))
        self.assertIn("179", producers["authority"]["label"])
        limitation = self.tasks["T0-LIVENESS-BOUND-EMPIRICAL-01"]["status_note"]
        self.assertIn("registered limitation through G2-b, not a launch gate", limitation)
        self.assertIn("close or be reruled before ALPHA", limitation)
        self.assertEqual(self.tasks["V5-TRANSACTION-GO-01"]["goal"],
                         "Satisfied by the magistrate's CAMPAIGN_TRANSACTION authorization record after G2-b (D-171 §3).")

    def test_schema_v3_work_selection_authority_notice(self):
        self.assertEqual(self.kernel["schema_version"], 3)
        self.assertEqual(
            self.kernel["authority"], gen_state.AUTHORITY_NOTICE
        )

    def test_terminal_ids_absent_from_kernel_present_in_completed_table(self):
        self.assertFalse(TERMINAL_IDS & set(self.tasks))
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        completed = queue_text.split("## Completed Queue Items", 1)[1]
        completed = completed.split("## Shelved Follow-Ups With Triggers", 1)[0]
        for tid in sorted(TERMINAL_IDS):
            self.assertIn(f"| {tid} |", completed)

    def test_ruling_43_paper_lanes_and_d174_scope_freeze(self):
        active = {"DECISION-LOG-RATIFY", "D166-PROMPT0-01"}
        self.assertEqual(
            {tid for tid in active if self.tasks[tid]["status"] == "active"},
            active,
        )
        prompt_acceptance = " ".join(
            self.tasks["D166-PROMPT0-01"]["acceptance"]["evidence"]
        )
        self.assertIn("dependency census", prompt_acceptance)
        self.assertIn("expected_pack_paths", prompt_acceptance)
        self.assertIn("D-138 successor-generation", prompt_acceptance)
        self.assertIn(
            "D-174",
            " ".join(self.tasks["DECISION-LOG-RATIFY"]["acceptance"]["evidence"]),
        )

        parked = {
            "WHOLE-WINDOW-STOP-RECEIPT-01",
            "CLAIM-NONISSUANCE-RECEIPT-01",
            "AUTHENTICATOR-ALLOWLIST-GUARD-01",
            "SKILL-DISTILL-01",
            "LINEAGE-RELOCATABLE-01",
            "MODULARITY-FOLLOWUPS-01",
            "TRANSFER-FIDUCIAL-01",
        }
        for tid in parked:
            with self.subTest(parked=tid):
                self.assertEqual(self.tasks[tid]["status"], "shelved")
                self.assertIn("D-174 scope freeze", self.tasks[tid]["status_note"])
        self.assertIn(
            "93d0d91c",
            self.tasks["AUTHENTICATOR-ALLOWLIST-GUARD-01"]["status_note"],
        )
        self.assertIn(
            "cold gate affirmed",
            self.tasks["LINEAGE-RELOCATABLE-01"]["status_note"],
        )

        with open(os.path.join(ROOT, "RUN_STATE.md"), encoding="utf-8") as fh:
            run_state = fh.read()
        self.assertIn("**T33 (2026-09-05)", run_state)
        self.assertIn("PR #286 is Paper-J with its row-9 full replay pending", run_state)
        self.assertIn("PR #287 is", run_state)
        self.assertIn("18:00 PT on 9 September", run_state)

    def test_stop_card_cleared_and_no_global_gate_live(self):
        # Earlier audit, T3, and readiness-council gates are cleared; their
        # mechanics remain covered by frozen fixtures below.
        self.assertIsNone(self.kernel["active_stop_card"])
        for task in self.tasks.values():
            self.assertIsNone(task["stop_card"])
        self.assertEqual(self.kernel["active_global_gates"], [])
        for tid in ("T3-CHAR-PAIR-01", "WO-T3-VIS-01", "SEC5A-REMOTE-01"):
            self.assertEqual(self.tasks[tid]["status"], "shelved")

    def test_axi_work_program_sequence_authority_and_window_fences(self):
        # AXI-S0 (2026-07-15), AXI-SA and AXI-SB (2026-07-16) completed and
        # left the live kernel; the Completed table owns their records.
        # AXI-SB-ADAPTER was minted on the SB supported verdict and takes
        # rank 11 with the verdict document as its authority (checked below
        # separately from the handoff-authority program rows).
        axi_ids = ("AXI-SD", "AXI-SE")
        self.assertEqual(
            {tid: self.tasks[tid]["rank"] for tid in axi_ids},
            {"AXI-SD": 13, "AXI-SE": 14},
        )
        adapter = self.tasks["AXI-SB-ADAPTER"]
        self.assertEqual(adapter["rank"], 11)
        self.assertEqual(adapter["status"], "queued")
        self.assertEqual(adapter["lane"], "agent")
        self.assertEqual(adapter["authority"]["path"],
                         "docs/specs/axi/sb_static_batch_verdict.md")
        self.assertTrue(any("Window A retains every quiet-Mac measurement slot"
                            in fence["rule"] for fence in adapter["fences"]))
        expected_authority_paths = {
            "docs/axi-handoff.md",
            "docs/decision_log.md",
            "docs/process_traces/2026-07-15-axi-xhigh-consult/response.md",
        }
        for tid in axi_ids:
            task = self.tasks[tid]
            self.assertEqual(task["lane"], "agent")
            pointer_paths = {task["authority"]["path"]}
            pointer_paths.update(fence["authority"]["path"] for fence in task["fences"])
            self.assertEqual(pointer_paths, expected_authority_paths)
            self.assertTrue(any("Window A retains every quiet-Mac measurement slot"
                                in fence["rule"] for fence in task["fences"]))

        self.assertEqual(self.tasks["AXI-SD"]["status"], "queued")
        # P2-015 retired 2026-07-31; AXI-SE's floors edge is satisfied.
        self.assertEqual(self._hard_start_targets("AXI-SE"), set())

    def _hard_start_targets(self, tid):
        return {
            d["target"] for d in self.tasks[tid]["dependencies"]
            if d["scope"] == "start" and d["strength"] == "hard"
            and d["state"] == "pending" and d["kind"] == "task"
        }

    def test_p2_015_retired_with_every_dependent_satisfied(self):
        # Retired 2026-07-31: claim-grade Window-A floors collected (a9/a10,
        # C, D), mint #1 mainline via PR #88, 7B and contrast windows passed.
        # Retirement convention is removal from the kernel, so no dependent
        # may be left holding a pending edge to it.
        self.assertNotIn("P2-015", self.tasks)
        dependents = {
            "AXI-SE", "P2-010", "P2-024",
        }
        for tid in sorted(dependents):
            dep = next(
                d for d in self.tasks[tid]["dependencies"]
                if d["target"] == "P2-015"
            )
            self.assertEqual(dep["state"], "satisfied", tid)
            self.assertIsNotNone(dep["evidence"], tid)
        for task in self.tasks.values():
            for dep in task["dependencies"]:
                if dep["target"] == "P2-015":
                    self.assertEqual(dep["state"], "satisfied", task["id"])

    def test_p2_006_formally_retired_without_live_dependency_edges(self):
        self.assertNotIn("P2-006", self.tasks)
        self.assertFalse({
            task["id"]
            for task in self.tasks.values()
            for dep in task["dependencies"]
            if dep["target"] == "P2-006"
        })
        with open(os.path.join(ROOT, "docs", "decision_log.md"),
                  encoding="utf-8") as fh:
            decision_log = fh.read()
        self.assertIn("P2-006 formally RETIRED from window selection", decision_log)

    def test_post_2m_event_gates_and_p2_023_chain(self):
        for tid in ("P2-022", "P2-023"):
            self.assertEqual(self.tasks[tid]["flags"], [])
            self.assertEqual(self.tasks[tid]["status"], "blocked")
            self.assertIn("D-041", self.tasks[tid]["authority"]["label"])
            pending_events = {
                dep["target"] for dep in self.tasks[tid]["dependencies"]
                if dep["kind"] == "event" and dep["scope"] == "start"
                and dep["strength"] == "hard" and dep["state"] == "pending"
            }
            self.assertEqual(pending_events, {"POST-2M-CORPUS"})
        self.assertIn("P2-022", self._hard_start_targets("P2-023"))

    def test_p2_016_conservatively_post_2m_at_parent(self):
        self.assertEqual(self.tasks["P2-016"]["flags"], [])
        self.assertEqual(self.tasks["P2-016"]["status"], "blocked")
        pending_start_events = {
            dep["target"] for dep in self.tasks["P2-016"]["dependencies"]
            if dep["kind"] == "event" and dep["scope"] == "start"
            and dep["strength"] == "hard" and dep["state"] == "pending"
        }
        self.assertEqual(pending_start_events, {"POST-2M-CORPUS"})

    def test_ed_dates_is_narrow_first_external_record(self):
        external = [
            task for task in self.tasks.values() if task["lane"] == "ed_external"
        ]
        self.assertEqual(min(task["rank"] for task in external), 1)
        dates = self.tasks["ED-DATES-01"]
        self.assertEqual(dates["rank"], 1)
        self.assertEqual(dates["status"], "queued")
        self.assertEqual(dates["dependencies"], [])
        combined = " ".join((dates["goal"], dates["acceptance"]["summary"]))
        self.assertIn("final-report", combined)
        self.assertIn("colloquium", combined)
        self.assertNotIn("borrow", combined.lower())

    def test_fanout_ruling_batch_dispositions(self):
        retired = {
            "FLOOR-WORKLOAD-SIZING-01", "P1-008", "P2-027", "P2-035",
            "P2-047A", "P2-047B", "P2-050",
            "PHASE-SHARE-ESTIMAND-01", "PREWINDOW-REGEX-01",
        }
        self.assertTrue(retired.isdisjoint(self.tasks))

        capture = self.tasks["EDQ-L9-3-CAPTURE-01"]
        regex_dep = next(
            dep for dep in capture["dependencies"]
            if dep["target"] == "PREWINDOW-REGEX-01"
        )
        self.assertEqual(regex_dep["state"], "satisfied")
        self.assertIsNotNone(regex_dep["evidence"])
        self.assertEqual(capture["status"], "queued")

        guard = self.tasks["QUIET-GUARD-01"]
        self.assertEqual(guard["dependencies"], [])
        self.assertIn("option-A", guard["status_note"])
        self.assertTrue(any(
            "Inactive host installation" in item
            for item in guard["acceptance"]["evidence"]
        ))

    def test_quiet_mac_all_lead_only_and_v5_g2a_is_queued_lane_head(self):
        # P2-015 (rank 1) retired 2026-07-31; MET-WINDOW-C-01 took rank 1
        # on 2026-08-01 but sits BLOCKED behind the D-100 repair + Ed 5A,
        # D-167 retired the D-117 sequence and installed G2-a, G2-b, and the
        # transaction at ranks 2/3/4. G2-a is the dependency-ready lane head.
        # The later scored _v6 leg adds one net quiet-Mac row, so 13 becomes
        # 14 after the D-167 replacement; T0-LIVENESS-BOUND-EMPIRICAL-01
        # (T26 item 3, PHYS-1 limitation, 2026-09-02) makes it 15; the
        # 2026-09-04 batch retires P2-047B with its retired harness parent.
        quiet = [t for t in self.tasks.values() if t["lane"] == "quiet_mac"]
        # 2026-09-18 headless activation f0b608b7 adds stage-B confirmation: 14 + 1 = 15.
        # 2026-09-25 activation 152c9255: JCORRECT-NULL-CALIBRATION-WINDOWS-01 adds one lead-only quiet-Mac row: 15 + 1 = 16.
        self.assertEqual(len(quiet), 16)
        for task in quiet:
            self.assertIn("lead_only", task["flags"])
        self.assertEqual(self.tasks["MET-WINDOW-C-01"]["rank"], 1)
        self.assertEqual(self.tasks["MET-WINDOW-C-01"]["status"], "blocked")
        self.assertEqual(
            self.tasks["MET-WINDOW-C-01"]["rank"],
            min(task["rank"] for task in quiet),
        )
        self.assertEqual(
            {
                tid: (self.tasks[tid]["rank"], self.tasks[tid]["status"])
                for tid in (
                    "V5-G2A-PREFILL-PROBE-01",
                    "V5-G2B-SHAKEDOWN-01",
                    "V5-TRANSACTION-01",
                )
            },
            {
                "V5-G2A-PREFILL-PROBE-01": (2, "queued"),
                "V5-G2B-SHAKEDOWN-01": (3, "blocked"),
                "V5-TRANSACTION-01": (4, "blocked"),
            },
        )
        # Ruling 171a R-9 (2026-09-02): the three _v5 packs cannot freeze until
        # decode units carry a declared manifest set. PR #278 satisfied that
        # edge; the remaining pending hard-start edge is G2-a.
        self.assertEqual(
            self._hard_start_targets("V5-DESK-DAY-01"),
            {"V5-G2A-PREFILL-PROBE-01"},
        )
        self.assertEqual(
            self._hard_start_targets("V5-G2B-SHAKEDOWN-01"),
            # 2026-09-08 D-176: G2-b also waits for the pack-bound rehearsal.
            {"V5-DESK-DAY-01", "NIGHT-PACK-REHEARSAL-01"},
        )
        self.assertEqual(
            self._hard_start_targets("V5-TRANSACTION-GO-01"),
            {"V5-G2B-SHAKEDOWN-01"},
        )
        # Ruling 89 R-1 (2026-09-01): the L10-A record gates the first
        # claim-bearing arm alongside Ed's GO.
        # Ruling 150a R-150-3 (2026-09-02): no _v5 claim night is armed before
        # the launch-step realization recheck lands.
        self.assertEqual(
            self._hard_start_targets("V5-TRANSACTION-01"),
            {
                "V5-TRANSACTION-GO-01",
                "L10-A-G2B-CONTRACT-PREFIX-01",
                "V5-LAUNCH-REALIZATION-RECHECK-01",
            },
        )
        queued = [t for t in quiet if t["status"] == "queued"]
        self.assertEqual(
            self.tasks["V5-G2A-PREFILL-PROBE-01"]["rank"],
            min(task["rank"] for task in queued),
        )
        self.assertEqual(
            self.tasks["V5-G2A-PREFILL-PROBE-01"]["status"], "queued"
        )

    def test_d168_closeout_rows_status_and_hard_start_dependencies(self):
        # D165-CLOSEOUT-CORE-01 (PR 261) and D165-SIDECAR-EMIT-01 (PR 267)
        # retired at their 2026-09-02 merges; the sidecar edge on the
        # end-to-end row is satisfied and only the renderer edge remains.
        expected = {
            "RENDERER-V5-SUCCESSOR-01": (
                "blocked", {"V5-G2A-PREFILL-PROBE-01"}
            ),
            "D165-E2E-REPLAY-01": (
                "blocked",
                {"RENDERER-V5-SUCCESSOR-01"},
            ),
        }
        for tid, (status, hard_dependencies) in expected.items():
            with self.subTest(tid=tid):
                self.assertEqual(
                    (
                        tid in self.tasks,
                        self.tasks[tid]["status"],
                        self._hard_start_targets(tid),
                    ),
                    (True, status, hard_dependencies),
                )

    def test_new_hardening_followups(self):
        self.assertEqual(self._hard_start_targets("P2-046B"), set())
        p2_038_dep = next(
            dep for dep in self.tasks["P2-046B"]["dependencies"]
            if dep["target"] == "P2-038"
        )
        self.assertEqual(p2_038_dep["state"], "satisfied")
        self.assertIsNotNone(p2_038_dep["evidence"])
        for tid in ("P2-048", "CI-003", "DOC-010"):
            self.assertEqual(self.tasks[tid]["status"], "shelved")

    def test_lane_inference_flags(self):
        for tid in ("P2-004", "P2-005"):
            self.assertEqual(self.tasks[tid]["lane"], "agent")
            self.assertIn("migration_inferred_lane", self.tasks[tid]["flags"])
        self.assertIn("provisional_until_live", self.tasks["P2-005"]["flags"])

    def test_doc_008_reopened_record_and_doc_010_two_part_fence(self):
        self.assertEqual(self.tasks["DOC-008"]["status"], "partial")
        self.assertEqual(
            {d["target"] for d in self.tasks["DOC-008"]["dependencies"]},
            {"DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS"},
        )
        for tid in ("DOC-008-INTAKE", "DOC-008-REFLECTION", "DOC-008-STATUS"):
            self.assertIn(tid, self.tasks)
        deps = self.tasks["DOC-010"]["dependencies"]
        self.assertEqual({d["target"] for d in deps}, {"DOC-008-proven-in-use", "G6"})
        for dep in deps:
            self.assertEqual(dep["kind"], "event")
            self.assertEqual(dep["scope"], "start")
            self.assertEqual(dep["strength"], "hard")
            self.assertEqual(dep["state"], "pending")
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        self.assertIn("| DOC-008 | P2 Next Slice | PARTIAL — REOPENED 2026-07-15 |",
                      queue_text)

    def _completed_queue_ids(self):
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue_text = fh.read()
        completed = queue_text.split("## Completed Queue Items", 1)[1]
        completed = completed.split("## Shelved Follow-Ups With Triggers", 1)[0]
        return {
            cells[1].strip()
            for line in completed.splitlines()
            if line.startswith("|")
            for cells in [line.split("|")]
            if len(cells) > 2 and cells[1].strip() not in ("ID", "---")
        }

    def _assert_pre_demotion_task_record_parity(self, tasks):
        snapshot = load_fixture("selection_semantics.json")[
            "pre_demotion_queue_snapshot"
        ]
        live_coverage = set(tasks)
        completed_ids = self._completed_queue_ids()
        for source_id, successor_ids in snapshot["documented_id_migrations"].items():
            self.assertTrue(
                set(successor_ids).issubset(set(tasks) | completed_ids),
                f"{source_id} migration successors missing",
            )
            live_coverage.add(source_id)
        # R3 is the formal retirement record for P2-006. Keep the frozen
        # pre-demotion snapshot intact while requiring both live absence and
        # explicit decision-log authority before treating the row as covered.
        formally_retired = {"P2-006"}
        self.assertTrue(formally_retired.isdisjoint(tasks))
        with open(os.path.join(ROOT, "docs", "decision_log.md"),
                  encoding="utf-8") as fh:
            decision_log = fh.read()
        self.assertIn("P2-006 formally RETIRED from window selection", decision_log)
        live_coverage.update(formally_retired)
        self.assertTrue(
            set(snapshot["task_ids"]).issubset(
                live_coverage | self._completed_queue_ids()
            ),
            "pre-demotion queue task record silently lost",
        )

    def test_pre_demotion_task_record_parity(self):
        self._assert_pre_demotion_task_record_parity(self.tasks)
        # SITE-02 and SPLIT-AP completed 2026-07-16 (PRs #68/#69) and left
        # the live kernel; the parity negative check keeps the still-live
        # recovered rows.
        for task_id in ("TOOL-01",):
            with self.subTest(negative_removed_task_id=task_id):
                mutated = copy.deepcopy(self.tasks)
                mutated.pop(task_id)
                with self.assertRaises(AssertionError):
                    self._assert_pre_demotion_task_record_parity(mutated)

    def test_recovered_task_semantics(self):
        self.assertEqual(self.tasks["TOOL-01"]["priority"], "p3_tooling")
        self.assertEqual(
            self.tasks["TOOL-01"]["status_note"],
            "lead personal tooling, non-repo",
        )
        for task_id in ("TOOL-01",):
            self.assertEqual(self.tasks[task_id]["lane"], "agent")
            self.assertEqual(self.tasks[task_id]["status"], "queued")
            self.assertEqual(self.tasks[task_id]["dependencies"], [])

    def test_phase_c_has_one_generated_work_selection_region_per_surface(self):
        with open(os.path.join(ROOT, "RUN_STATE.md"), encoding="utf-8") as fh:
            run_state = fh.read()
        with open(os.path.join(ROOT, "TASK_QUEUE.md"), encoding="utf-8") as fh:
            queue = fh.read()

        self.assertEqual(run_state.count(gen_state.RS_BEGIN), 1)
        self.assertEqual(run_state.count(gen_state.RS_END), 1)
        self.assertEqual(queue.count(gen_state.Q_BEGIN), 1)
        self.assertEqual(queue.count(gen_state.Q_END), 1)

        run_outside = run_state.split(gen_state.RS_BEGIN, 1)[0]
        run_outside += run_state.split(gen_state.RS_END, 1)[1]
        queue_outside = queue.split(gen_state.Q_BEGIN, 1)[0]
        queue_outside += queue.split(gen_state.Q_END, 1)[1]

        self.assertNotIn("RESTART HERE (next session)", run_outside)
        self.assertNotIn("## What Is Next", run_outside)
        self.assertNotIn("explicitly non-authoritative", run_outside)
        self.assertIn("authoritative for work selection", run_outside)
        self.assertIn("Historical restart snapshot", run_outside)
        self.assertIn("Historical Next-Work Snapshot", run_outside)

        self.assertNotIn("SOFTWARE-READY", queue_outside)
        self.assertNotIn(
            "| Rank | ID | Priority | Status | Task | Evidence / Acceptance |",
            queue_outside,
        )
        self.assertEqual(queue_outside.count("## Current Queue"), 1)
        self.assertIn("sole live work-selection view", queue_outside)


class TestWorkSelectionFidelity(unittest.TestCase):
    """Exact selection assertions against hand-written, frozen JSON oracles."""

    def _kernel_with(self, active_global_gates):
        kernel = copy.deepcopy(load_kernel())
        kernel["active_global_gates"] = copy.deepcopy(active_global_gates)
        # The synthetic-gate oracles predate transient active rows; a live
        # in-execution task (status "active") legitimately renders CONTINUE
        # under a select-scoped gate, so normalize it to queued here.
        close = kernel["tasks"].get("REFREEZE-D147-CLOSE")
        if close is not None and close.get("status") == "active":
            close["status"] = "queued"
        gen_state.validate(kernel)
        return kernel

    def _assert_oracle(self, kernel, oracle):
        self.assertSetEqual(
            gen_state.selectable_task_ids(kernel),
            set(oracle["expected_selectable_task_ids"]),
        )

    def test_frozen_historical_gate_artifact_suppresses_exactly(self):
        # The live-kernel equality pin was retired at gate clearance
        # (2026-07-15); the frozen artifact remains the migration fixture.
        oracle = load_fixture("historical_audit_gate.json")
        oracle["must_suppress_task_ids"].append("FLOOR-BIND-01")
        _adapt_retired_lane_heads(oracle["must_suppress_task_ids"])
        kernel = self._kernel_with(oracle["active_global_gates"])
        self._assert_oracle(kernel, oracle)
        selected = gen_state.selectable_task_ids(kernel)
        self.assertTrue(set(oracle["must_suppress_task_ids"]).isdisjoint(selected))

    def test_run_state_gate_suppresses_lane_heads_but_active_work_continues(self):
        gate_oracle = load_fixture("historical_audit_gate.json")
        head_oracle = load_fixture("cleared_audit_gate.json")
        head_oracle["expected_selectable_task_ids"][0] = "WO-LAUNCH-BINDING"  # 2026-09-16 merge wave: installer closed; existing rank order restores WO-LAUNCH-BINDING.
        _adapt_retired_lane_heads(head_oracle["expected_selectable_task_ids"])
        kernel = self._kernel_with(gate_oracle["active_global_gates"])
        rendered = gen_state.render_run_state(kernel)
        gate_id = gate_oracle["active_global_gates"][0]["id"]
        expected_by_lane = {
            kernel["tasks"][task_id]["lane"]: task_id
            for task_id in head_oracle["expected_selectable_task_ids"]
        }
        self.assertEqual(set(expected_by_lane), set(gen_state.LANES))

        restart = rendered.split("## Restart By Machine-State Lane", 1)[1]
        for index, lane in enumerate(gen_state.LANES):
            section = restart.split(f"### {gen_state.LANE_LABEL[lane]}", 1)[1]
            if index + 1 < len(gen_state.LANES):
                section = section.split(
                    f"### {gen_state.LANE_LABEL[gen_state.LANES[index + 1]]}", 1
                )[0]
            entries = [line for line in section.splitlines() if line.startswith("- ")]
            active = sorted(
                (task for task in kernel["tasks"].values()
                 if task["lane"] == lane and task["status"] == "active"),
                key=lambda task: (task["rank"], task["id"]),
            )
            if active:
                self.assertEqual(len(entries), len(active), lane)
                for entry, task in zip(entries, active):
                    self.assertTrue(
                        entry.startswith(
                            f"- CONTINUE — {gen_state.LANE_PREFIX[lane]}{task['rank']} "
                            f"`{task['id']}`:"
                        ),
                        entry,
                    )
                    self.assertNotIn("excluded by:", entry)
            else:
                self.assertEqual(len(entries), 1, lane)
                task_id = expected_by_lane[lane]
                task = kernel["tasks"][task_id]
                self.assertTrue(
                    entries[0].startswith(
                        f"- GATED — {gen_state.LANE_PREFIX[lane]}{task['rank']} `{task_id}` "
                    ),
                    entries[0],
                )
                self.assertIn(f"(excluded by: {gate_id})", entries[0])
            for entry in entries:
                self.assertNotIn("READY", entry)

    def test_clearing_gate_restores_exact_dependency_rank_heads(self):
        oracle = load_fixture("cleared_audit_gate.json")
        oracle["expected_selectable_task_ids"][0] = "WO-LAUNCH-BINDING"  # 2026-09-16 merge wave: installer closed; existing rank order restores WO-LAUNCH-BINDING.
        _adapt_retired_lane_heads(oracle["expected_selectable_task_ids"])
        kernel = self._kernel_with(oracle["active_global_gates"])
        self._assert_oracle(kernel, oracle)

    def test_allowlist_lane_matching_and_multi_gate_intersection(self):
        fixture = load_fixture("selection_semantics.json")
        for scenario in _adapt_retired_lane_heads_in_scenarios(
            fixture["scenarios"]
        ):
            with self.subTest(scenario=scenario["name"]):
                kernel = self._kernel_with(scenario["active_global_gates"])
                self._assert_oracle(kernel, scenario)

    def test_stop_card_precedes_gates_and_clear_restores_still_active_gate(self):
        fixture = load_fixture("selection_semantics.json")
        lane_oracle = next(
            scenario for scenario in _adapt_retired_lane_heads_in_scenarios(
                fixture["scenarios"]
            )
            if scenario["name"] == "lane_matching"
        )
        kernel = self._kernel_with(lane_oracle["active_global_gates"])
        stop_fixture = fixture["stop_card_precedence"]
        card = copy.deepcopy(stop_fixture["active_stop_card"])
        # Invariant 7 needs an active/blocked stop-card holder. The historical
        # fixture names retired P2-035; P2-024 is still blocked.
        stopped_task_id = stop_fixture["task_id"]
        if (stopped_task_id not in kernel["tasks"] or
                kernel["tasks"][stopped_task_id]["status"] not in ("active", "blocked")):
            stopped_task_id = "P2-024"
        kernel["active_stop_card"] = card
        kernel["tasks"][stopped_task_id]["stop_card"] = copy.deepcopy(card)

        with tempfile.TemporaryDirectory(prefix="state_kernel_stop_card.") as root:
            for name in os.listdir(ROOT):
                if name != "docs":
                    os.symlink(os.path.join(ROOT, name), os.path.join(root, name))
            docs = os.path.join(root, "docs")
            os.mkdir(docs)
            source_docs = os.path.join(ROOT, "docs")
            for name in os.listdir(source_docs):
                os.symlink(os.path.join(source_docs, name), os.path.join(docs, name))
            stop_cards = os.path.join(docs, "stop_cards")
            os.mkdir(stop_cards)
            with open(os.path.join(stop_cards, "fixture-active.md"), "w",
                      encoding="utf-8") as fh:
                fh.write("# Fixture Active Stop Card\n")

            with mock.patch.object(gen_state, "ROOT", root):
                gen_state.validate(kernel)
                self.assertEqual(gen_state.selectable_task_ids(kernel), set())
                stopped_queue = gen_state.render_queue(kernel)
                self.assertNotIn("| READY |", stopped_queue)
                self.assertNotIn("PARTIAL; READY", stopped_queue)
                self.assertIn("STOPPED — active stop card", stopped_queue)

                kernel["active_stop_card"] = None
                kernel["tasks"][stopped_task_id]["stop_card"] = None
                gen_state.validate(kernel)
                self._assert_oracle(kernel, lane_oracle)

    def test_priority_relabel_cannot_bypass_gate(self):
        oracle = load_fixture("historical_audit_gate.json")
        kernel = self._kernel_with(oracle["active_global_gates"])
        kernel["tasks"]["P2-004"]["priority"] = "p0_safety"
        gen_state.validate(kernel)
        self._assert_oracle(kernel, oracle)

    def test_only_both_doc_010_events_release_start(self):
        base = load_kernel()
        gate = {
            "id": "gate-fixture-doc-010",
            "summary": "Fixture gate permits DOC-010 in the agent lane.",
            "authority": ["Hand-written selection test setup"],
            "clearance": "Fixture-only clearance.",
            "scope": {"operation": "select", "lanes": ["agent"]},
            "allowed_task_ids": ["DOC-010"],
        }
        evidence = {
            "path": "docs/specs/c027/doc-008_state_kernel.md",
            "label": "DOC-008 state-kernel spec",
        }

        for only_target in ("DOC-008-proven-in-use", "G6"):
            with self.subTest(only_satisfied=only_target):
                kernel = copy.deepcopy(base)
                kernel["active_global_gates"] = [copy.deepcopy(gate)]
                task = kernel["tasks"]["DOC-010"]
                task["status"] = "blocked"
                dep = next(d for d in task["dependencies"] if d["target"] == only_target)
                dep["state"] = "satisfied"
                dep["evidence"] = copy.deepcopy(evidence)
                gen_state.validate(kernel)
                self.assertNotIn("DOC-010", gen_state.selectable_task_ids(kernel))

        kernel = copy.deepcopy(base)
        kernel["active_global_gates"] = [copy.deepcopy(gate)]
        task = kernel["tasks"]["DOC-010"]
        task["status"] = "queued"
        for dep in task["dependencies"]:
            dep["state"] = "satisfied"
            dep["evidence"] = copy.deepcopy(evidence)
        gen_state.validate(kernel)
        self.assertIn("DOC-010", gen_state.selectable_task_ids(kernel))

    def test_negative_gate_removed_and_allowlist_widened_fail_oracle(self):
        oracle = load_fixture("historical_audit_gate.json")

        removed = self._kernel_with([])
        with self.assertRaises(AssertionError):
            self._assert_oracle(removed, oracle)

        widened_gates = copy.deepcopy(oracle["active_global_gates"])
        widened_gates[0]["allowed_task_ids"] = ["ED-DATES-01"]
        widened = self._kernel_with(widened_gates)
        with self.assertRaises(AssertionError):
            self._assert_oracle(widened, oracle)

    def test_negative_doc_010_g6_drop_fails_validation(self):
        kernel = copy.deepcopy(load_kernel())
        kernel["tasks"]["DOC-010"]["dependencies"] = [
            dep for dep in kernel["tasks"]["DOC-010"]["dependencies"]
            if dep["target"] != "G6"
        ]
        with self.assertRaises(gen_state.KernelError):
            gen_state.validate(kernel)

    def test_gate_rendered_in_both_regions_and_forbidden_tasks_never_ready(self):
        gate = load_fixture("historical_audit_gate.json")["active_global_gates"]
        kernel = self._kernel_with(gate)
        run_state = gen_state.render_run_state(kernel)
        queue = gen_state.render_queue(kernel)
        for rendered in (run_state, queue):
            self.assertIn("## Active Global Work-Selection Gates", rendered)
            self.assertIn("gate-2026-07-13-comprehensive-audit", rendered)
            self.assertIn(gate[0]["clearance"], rendered)
            self.assertIn("Source of truth for work selection:", rendered)
            self.assertNotIn("Source of truth:", rendered)
        self.assertNotIn("- READY —", run_state)
        self.assertNotIn("| READY |", queue)
        self.assertNotIn("PARTIAL; READY", queue)

    def test_live_empty_gate_state_and_synthetic_gate_both_render_exactly(self):
        # The live kernel has no global gate. The synthetic all-lane allowlist
        # below separately pins gate mechanics.
        kernel = load_kernel()
        run_state = gen_state.render_run_state(kernel)
        queue = gen_state.render_queue(kernel)
        for rendered in (run_state, queue):
            self.assertNotIn("T3-2026-08-09-DAY", rendered)
            self.assertNotIn("WINDOW-COUNCIL-GATE", rendered)
            self.assertIn(
                "NONE — no global work-selection gate is active", rendered
            )
        self.assertEqual(
            gen_state.selectable_task_ids(kernel),
            {
                "ED-DATES-01",
                "V5-G2A-PREFILL-PROBE-01",
                "WO-LAUNCH-BINDING",  # 2026-09-16 merge wave: installer closed; existing rank order restores WO-LAUNCH-BINDING.
            },
        )
        self.assertNotIn("excluded by:", run_state)
        self.assertNotIn("GATED —", queue)

        gated = copy.deepcopy(kernel)
        gated["active_global_gates"] = [
            {
                "id": "SYNTHETIC-TEST-GATE",
                "summary": "fixture gate: pins gate rendering after the live gate lifted",
                "authority": ["test fixture (no real authority)"],
                "clearance": "cleared by deleting this fixture",
                "scope": {"operation": "select", "lanes": list(gen_state.LANES)},
                "allowed_task_ids": ["QUIET-GUARD-01"],
            }
        ]
        gen_state.validate(gated)
        run_state = gen_state.render_run_state(gated)
        queue = gen_state.render_queue(gated)
        for rendered in (run_state, queue):
            self.assertIn("SYNTHETIC-TEST-GATE", rendered)
            self.assertNotIn(
                "NONE — no global work-selection gate is active", rendered
            )
        self.assertIn("GATED — SYNTHETIC-TEST-GATE", queue)
        self.assertEqual(
            gen_state.selectable_task_ids(gated), {"QUIET-GUARD-01"}
        )


class TestGeneratorSelfConsistency(unittest.TestCase):
    """--check against the kernel itself via generator-produced fixtures."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="gen_state_test.")
        self.addCleanup(shutil.rmtree, self.tmp)
        self.run_state = os.path.join(self.tmp, "RUN_STATE.md")
        self.queue = os.path.join(self.tmp, "TASK_QUEUE.md")
        with open(self.run_state, "w", encoding="utf-8") as fh:
            fh.write(
                "# Run State\n\nLast updated: 2026-07-09 (manual)\n\n"
                f"{gen_state.RS_BEGIN}\n{gen_state.RS_END}\n\n## Hand-authored facts\n\nkept.\n"
            )
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(
                "# Task Queue\n\n## Current Queue\n\n"
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n\n## Completed Queue Items\n\nkept.\n"
            )
        self.paths = ["--run-state", self.run_state, "--queue", self.queue]

    def read(self, path):
        with open(path, "rb") as fh:
            return fh.read()

    def test_generate_then_check_is_clean_and_byte_stable(self):
        self.assertEqual(run_gen(*self.paths).returncode, 0)
        first_rs, first_q = self.read(self.run_state), self.read(self.queue)
        # --check: exact agreement with the kernel.
        check = run_gen("--check", *self.paths)
        self.assertEqual(check.returncode, 0, check.stderr)
        # Second generation changes no bytes.
        self.assertEqual(run_gen(*self.paths).returncode, 0)
        self.assertEqual(self.read(self.run_state), first_rs)
        self.assertEqual(self.read(self.queue), first_q)
        # Hand-authored text outside markers preserved.
        self.assertIn(b"## Hand-authored facts", first_rs)
        self.assertIn(b"## Completed Queue Items", first_q)

    def test_stdout_render_is_deterministic(self):
        a = run_gen("--stdout", "queue")
        b = run_gen("--stdout", "queue")
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        c = run_gen("--stdout", "run-state")
        d = run_gen("--stdout", "run-state")
        self.assertEqual(c.returncode, 0, c.stderr)
        self.assertEqual(c.stdout, d.stdout)

    def test_one_byte_drift_detected_read_only(self):
        run_gen(*self.paths)
        drifted = self.read(self.queue).replace(b"Source of truth", b"Source of trvth", 1)
        with open(self.queue, "wb") as fh:
            fh.write(drifted)
        check = run_gen("--check", *self.paths)
        self.assertEqual(check.returncode, 1)
        # --check is read-only even on failure.
        self.assertEqual(self.read(self.queue), drifted)

    def test_missing_and_duplicate_markers_fatal(self):
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write("# Task Queue\n\nno markers here\n")
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n"
                f"{gen_state.Q_BEGIN}\n{gen_state.Q_END}\n"
            )
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)
        with open(self.queue, "w", encoding="utf-8") as fh:
            fh.write(f"{gen_state.Q_END}\n{gen_state.Q_BEGIN}\n")
        self.assertEqual(run_gen("--check", *self.paths).returncode, 2)

    def test_invalid_kernel_exits_2(self):
        bad = os.path.join(self.tmp, "kernel.json")
        kernel = load_kernel()
        kernel["schema_version"] = 99
        with open(bad, "wb") as fh:
            fh.write(gen_state.canonical_bytes(kernel))
        self.assertEqual(
            run_gen("--check", "--kernel", bad, *self.paths).returncode, 2
        )

    def test_non_canonical_kernel_bytes_exit_2_on_check(self):
        loose = os.path.join(self.tmp, "kernel.json")
        with open(loose, "wb") as fh:
            fh.write(gen_state.canonical_bytes(load_kernel()))
        run_gen("--kernel", loose, *self.paths)  # populate regions first
        with open(loose, "w", encoding="utf-8") as fh:
            json.dump(load_kernel(), fh)  # then de-canonicalize the bytes
        self.assertEqual(
            run_gen("--check", "--kernel", loose, *self.paths).returncode, 2
        )


if __name__ == "__main__":
    unittest.main()
