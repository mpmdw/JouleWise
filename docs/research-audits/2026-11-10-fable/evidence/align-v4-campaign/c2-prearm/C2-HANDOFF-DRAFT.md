# C1-to-C2 desk worksheet

**DRAFT / INELIGIBLE · Unsigned.** The lead or explicitly authorized interim
lead owns a fresh C2 READY on main. The magistrate owns C1's terminal Check
and C2's registered execution. The desk and series owners supply evidence
for those decisions. This worksheet carries blank fields for those owners.
Its design authority is audit `56f239dd2`. Source names below refer to the
issued W1 pin `b2e01464d` unless specified. [Priority and ownership][priority] ·
[Registered handoff][b2] · [Release ownership][rl185]

## Carry from the C1 admission

Use the accepted C1 gate record for the completed W1 full desk and clearance,
W1 stamp count/pairing/gap and Pydantic disposition, the single four-binding
receipt and 102/101 witness, any applicable Part C carry or new-pin close,
RL-21 acceptance and analysis seal, and the signed manifest and W1 collection
admission. The C1 draft also specifies the four-sentinel C1 roster that
discharges W1's U4 consequence. C2 uses **C1's** U4 verdict for the next
roster. Carry the accepted receipt and frozen analysis and series evidence
subject to their existing exact-byte checks. The release-only print bindings and E17 disposition stay
under the adopted receipt and release rules. A pin change still owes its
applicable receipt, Part C carry check and current full desk. [C1 worksheet
from PR #844](../c1-prearm/C1-READY-DRAFT.md) · [C1 signature and freeze][c1] ·
[RL-21 seal][rl21] · [Admission][admission] · [Part C carry][part-c] ·
[Release ownership][rl185]

| Field | Producer | Verifier | Fill |
|---|---|---|---|
| Accepted C1 admission and receipt reference, authorized operational head/tree, receipt-to-runtime identity and any required carry disposition | Lead and signatory, with the series owner supplying the admitted manifest and W1 collection binding | Lead verifies C1 gate evidence, freeze and current pin. `v4_registration.require_registration` validates the pinned registration. `align_v4_series.require_admission(post_w1=True)` reads the existing exact-byte series admission | |

## C1 terminal Check and packet inputs

Distinguish C1's committed calibration predecessor from the latest host
attempt. An intervening attempt changes which host close the magistrate must
prove. The canonical series ledger determines the calibration predecessor.
[Latest record test][bound] · [Proven close and stop scopes][close]

| Field | Producer | Verifier | Fill |
|---|---|---|---|
| Terminal C1 Check, actual attempt and plan, result and chain closure, delivery and watchdog release | Native `run_night.py` result and chain markers, native courier delivery, `magistrate_watchdog.py` empty-process release latch. The magistrate records the Check | Magistrate verifies planned stages, references/brackets and cleanup, then reads the Check. The packet predicates `terminal_release_check` and `watchdog_latch_check` authenticate the result, plan, chain/delivery and exact latch. Release permits a terminal refusal to be recorded with its own disposition. [B1][b2] · [Terminal predicates][terminal] | |
| Latest attempted host entry, terminal receipt, clean restore and readback, absent jobs/fence/process group, copy stopped before soak, open stops or deviations | Magistrate's close and restore record, native job/census and copy receipts | Magistrate reads the latest attempted entry and proves the close. `align_v4_session.install` rechecks the host lock and restore and `watchdog_acceptance` checks the arm boundary. Apply the registered restore retry and halt/page on unproved restore. [Close and stop scopes][close] · [Host restore][install] | |
| C1 record path, commit and SHA-256, plus its `previous_record` link and predecessor identity. Ledger commit, `series/state.json` SHA-256 and refreshed pushed ref | Record owner packages the native sources and capture inventory. The series owner updates the canonical ledger. The magistrate checks committed and pushed references | `build_packet` authenticates source blobs, record digest and pushed ancestry and walks the links to R1/W1. The arm's `_record_bound` checks the last commit that changed the record path and the HEAD ledger's exact predecessor and digest. [Builder][build] · [History][history] · [Arm binding][bound] | |
| Finalized C1 manifest digest, verified restore reference, and admitted unpack receipt pointer/digest where applicable | `align_v4_harvest_off.cmd_finalize_manifest` and `cmd_unpack` on the pinned route. The desk owner returns the verified restore proof | `cmd_unpack` verifies manifest, transport, restored bytes and mirror. For the ruled successor contract, apply the receipt checks below before asserting finality for captures. [Issued unpack][unpack] · [RL-163][rl163] · [RL-183b][receipt] | |
| Quiet observation, policy, expiry and C1 light triage or completed final source references | Magistrate records the post-terminal quiet observation. The Air desk owner supplies `cmd_triage` or `cmd_desk` / `cmd_final` outputs from the verified restore | Builder `quiet()` uses the arm clock, frozen duration minima and freshness. `WindowRecord.final_evidence` / `eligibility` verify C1's sources, plan, exclusions, X5/U3 and captures. [Quiet check][build] · [Desk tools][desk] · [Eligibility][eligibility] | |
| C1 capture/fault tabulation, historical meter gaps and battery streak disposition | Light triage or guarded PILOT and desk supply the exact roster's X1–X8 coverage/fault rows, historical KM003C coverage and `v4_B_bar`. The lead supplies an applicable `battery_rulings` row | Builder `faults`, `meter_coverage` and `battery` re-read the authenticated sources. `next_arm_triage` records historical meter gaps as non-gating. The first B non-pass gives `automatic_resume` with fresh host top-up and OBC proof. A second consecutive non-pass needs the committed signed battery ruling. [B2][b2] · [Triage decisions][triage] | |
| Current artifact-set SHA-256, last passing record and its code commit and artifact-set SHA-256, and desk branch and pass/finality readback | `v4_registration.artifact_set_digest` hashes the arm tree's bound bytes. The series owner points `last_passed_record` to the passing desk and its code state | Builder `last_desk_state` verifies finality and desk PASS and uses `artifact_set_digest_at` on the committed code bytes. `full_desk` and `next_arm_triage` derive the requirement from the predecessor and those two digests. [Digest functions][digests] · [Desk branches][desk-branches] | |
| Packet pointer, file SHA-256, validity, canonical rebuild and arm-record readback | Desk owner runs `align_v4_next_arm_packet.py`. The magistrate runs the registered arm | `arm_checks` rebuilds with its own clock and computed digest. Only push tip fields and `packet_preflight` are ignored in canonical comparison. The arm judges its own rebuild and records its digest. [Canonical comparison][canonical] · [Arm readback][arm-readback] | |

### Desk and restore branches

- **C1 with unchanged bound bytes.** The builder can take `sources.light_triage`
  and the `running_off_mbp` desk stub for C1, with `last_passed_record` still
  pointing to the last actual pass. `member_eligibility` can be provisional
  and `full_desk_gate` can be `deferred`. Preserve pending holds and the R17
  deadline. C1 must be final before C3, or before any earlier arm that owes
  the full desk. The native producer's final `pilot`, `desk` and `exclusions`
  go in C1's record when already final or under C2's `previous_final` when
  finalized during C2. `previous_final.record_sha256` binds **C1's** index.
  If C1's deferred desk passes and C2 carries it, `last_passed_record` may
  point to C1 with `final_record` pointing to C2. A completed desk can be
  final and still fail `full_desk_gate`. A false `v4_B_bar` alone is handled
  by `battery_window`. [R17 record paths][r17] · [Desk branches][desk-branches] ·
  [History finality][history]
- **Changed bound bytes, or a W1 predecessor.** Hold the arm for completed
  final eligibility and a passing full desk on the current artifact set.
  A C1 PASS on other bytes cannot satisfy it. The W1 case belonged to the
  C1 gate. Apply the ordinary registration and freeze checks before using
  any changed pin. [B2][b2] · [Desk branches][desk-branches]
- **Receipt admission.** At `b2e01464d`, `cmd_unpack` verifies the restore
  and emits no unpack receipt. `WindowRecord._finalized_manifest` expects a
  manifest-body descriptor and finality uses the three desk sources with
  `final_adjudication_error`. This is the fixture interface. Actual series
  records are subject to the RL-163/RL-183b publication and signing hold.
  Before using the successor route, the lead verifies admission on the
  receipt-bound operational tree. Under that ruling the committed manifest
  is digest-only. After a verified restore, only `cmd_unpack` writes the
  canonical four-key receipt (`schema`, `window`, `plan_id`,
  `finalized_manifest_sha256`). A captured window needs that receipt as a
  direct or `previous_final` source. `cmd_final` and
  `WindowRecord.final_evidence` both check it through the ruled
  `unpack_receipt_error`, against the window being finalized, its own plan
  and its own committed manifest digest, including when C2 carries C1's
  receipt. A genuinely uncaptured window can be final on light triage.
  Supplemental captures still require the captured-window receipt check.
  PR #826 is prospective. The manifest body stays outside public Git before
  release.
  [Issued manifest and finality][issued-final] · [Issued unpack][unpack] ·
  [RL-163 disclosure rule][rl163] · [RL-183b receipt and hold][receipt] ·
  [PR #826](https://github.com/mpmdw/JouleWise/pull/826)

## Registered next window and outstanding holds

| Field | Producer | Verifier | Fill |
|---|---|---|---|
| Next registered window and attempt, fixed-eight result, retry/reserve debt, finality deadline | Series owner projects the already registered plan and binds the native record history in `series/state.json` | Builder `attempts` and `calibration_stop` derive bars and counts. `align_v4_series.calibration_rows` / `bind_packet` bind the next slot and manifest at the arm. [Sequence][series] · [Arm binding][series-bind] · [Fixed eight][fixed-eight] | |
| Frozen plan and cohort, seed/ordinal and sentinel roster, sizing/disk reservation | Series owner supplies the admitted plan projection. The existing `align_v4_series.generate(check=True)` verifies the matching registered kit | Magistrate rechecks via `prepare` and `validate_series_state`. The packet checks `cohort`, `thermal` and `sentinels` verify frozen identity and C1's U4 consequence. Two extra replay sentinels apply only on U4 inconclusive and contribute no count or held-out seed. Registered ceilings are 59,520 s ordinary and 62,400 s with the pair. [Freeze][freeze] · [Roster and sizing][roster] · [Kit verification][kit-check] | |
| C1 structural bar, thermal hold, held-window and authorized release references, if any | Desk reports U1–U3, native terminal/capture evidence and final exclusions. The lead supplies any applicable signed ruling with committed text | Builder `structural_bar` and `thermal` derive the bar and streak. `held_window_check` reads the authenticated chain and final exclusions and requires the committed ruling for a held reason. The arm runs this check independently of packet preflight. `--held-window-ruling` supplies the committed ruling path. [Structural bars][structural] · [Thermal holds][thermal] · [Held-window check][held] | |

An admitted captured C1 normally leads to C2. A first final zero-counted-capture
attempt selects C1's retry (`C1#2` after `C1`), with the same assignment,
seeds and sabotage placement. If the retry also yields zero, the slot is
barred, and the next eligible primary remains C2 if the other gates pass.
A captured structural bar likewise contributes no assignment and owes a
replacement. A provisional zero-capture or barred row holds at
`pending_final_eligibility`. Calibration runs C1–C8 in order and spends
C9–C14 only for structural replacements, in order. Keep eight final counted windows and at
least 39 eligible benign per pair for test entry. T1–T3 and T4–T5 follow the
separate registered test/reserve rules. Pending finality, insufficient
calibration and `escalate_to_lead` stop the affected arm. [Fixed eight][fixed-eight] ·
[Sequence and retry][series] · [Registered identities][rl185]

From C1 the thermal policy and cohort identity are frozen. U1–U3 FAIL bars
pool entry. An inconclusive U1–U3 alone does not create a structural bar.
Two consecutive C/T FAIL bars or a third since reset require a signed
`u1_u3_fail_escalation` ruling naming the triggering attempt. Zero-capture
attempts neither increment nor reset the thermal streak. Any applicable
unreleased harvest hold independently refuses the arm. Preserve RL-21's
analysis seal and keep held/barred windows out of release assignments.
[Freeze][freeze] · [Thermal holds][thermal] · [Held-window check][held] ·
[Release ownership][rl185]

## Air work during a C2 span

Before C2, the magistrate completes the C1 terminal Check, finalizes and
commits the record, and finishes approved MBP pack/hash/copy/transfer work
before the applicable quiet boundary. The Air desk owner returns C1 light
triage before the arm if using the provisional branch. If the full desk is
due, its final eligibility and current-byte PASS also precede the arm.
[Close boundary][close] · [Off-host runbook][r17] · [B2][b2]

During C2, the authorized Air desk owner may finish a **deferred C1 desk**
from the already verified off-host copy. That comprises verified restore
or fresh restore for a retry, guarded harvest and full desk, final eligibility
and off-host review/return of the permitted final sources for C2's record.
Any registered post-final reduction stays in its existing guarded lane.
Schedule this only outside the reservation for the authorized look rehearsal
and both stages, with the Air otherwise quiet as the desk route requires.
If the Air reservation delays finality, the R17 deadline still holds the
applicable arm. During C2 the MBP runs the measurement alone. [Air desk steps][air-desk] ·
[Look reservation][air-look] · [R17 deadline][r17]

## Lead READY, ordinary notice and native arm

| Field | Producer | Verifier | Fill |
|---|---|---|---|
| Fresh typed C2 READY on main, issuer and authority, typed header, signature, issue/expiry, effective event and authorized route | Lead or explicitly authorized interim lead issues the magistrate-owned typed item after substantive readiness | Magistrate verifies authority, expiry, exact scope and any launch condition from main. The only condition form is the launch record of an already-issued span. [Typed item schema][item] · [Priority][priority] · [Effectiveness][effective] | |
| Registered plan ID, pin/tree, kit and seal/receipt references, local and UTC t0, bound, latest end, deadman and runway | Magistrate's existing `align_v4_session.prepare` and shared plan renderer. The lead supplies authority and pin | Magistrate cross-checks the READY and exact admitted plan, `validate_series_state` and installer preflight. [Registered prepare][prepare] · [Revalidation][kit-check] | |
| Ordinary notice to Ed, delivery and authorized veto interval, timestamped post-interval read and immediate NO/stop/directive recheck | Magistrate sends the registered ordinary notice with the exact plan and times. Ed has veto | Magistrate verifies delivery and records actual checker, source, time and disposition before install. A pre-notice is a filler hint. [Notice rule][notice] · [F-10][f10] | |
| Fresh quiet/display state and dwell, restore/hygiene/thermal state, empty census, stop and copy checks, AC mode and mount census | Magistrate records current closed-host and quiet evidence. `arm_checks` observes series AC powermode and volume census | `quiet`, `arm_checks` and the registered installer read fresh evidence and enforce frozen quiet state, plan mode, absence of external/network/FUSE volumes and applicable hold scopes. [B2][b2] · [Native checks][native] · [Close scopes][close] | |
| Fresh charging predicate, completed top-up and OBC-off attestation, battery sampler stop, current live reader and monotonic probe/dwell order | Native battery observation and source-joined top-up evidence, magistrate's OBC-off attestation, `arm_checks` live reader probe | `battery_arm` checks fresh AC, ≥99%, not charging, current magnitude ≤200 mA and source-bound completed top-up within 30 minutes. The live reader must show aligned samples, a closing line and a consistent offset, then stop before dwell. [Battery predicate][battery] · [Live probe][live] · [Dwell record][arm-readback] | |
| Disk floor/reservation, network time OFF and frequency word 0, host-link disposition, collector/watchdog acceptance, runtime and weight identity, arm outcome or refusal and next eligible entry | `prepare` and `_arm_and_install` emit native attestations and disk, time, watchdog, arm and dwell records. The magistrate records host-link, restore and installer outcome | Magistrate reads the registered host/installer predicates and stop scopes fresh. Pre-dwell checks and writes precede the dwell stamp. The installer retains its handoff and post-install watchdog result. [Native install][install] · [Arm record and installer][arm-outcome] · [Stop scopes][close] | |

Before effectiveness the magistrate uses `SESSION_READY=no` and the
ordinary ladder. Effective READY takes priority at the next eligible proven
clean close and lets running work finish. Through qual-03's close a READY
posted between qualification spans takes effect at the second span's launch
record, then waits for its proven clean close. If the C2 arm refuses, record
the exact cause and release the ladder immediately to its next eligible rung
under the applicable stop. W1 or C1 priority and a campaign queue entry
supply no C2 authority. [W1 priority ruling][w1-priority] · [Effectiveness][effective] ·
[F-10][f10]

[priority]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17285-L17291
[w1-priority]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20155-L20172
[rl185]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20874-L20897
[c1]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19920-L19930
[rl21]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L428-L456
[part-c]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L14527-L14539
[rl163]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L15439-L15460
[receipt]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20457-L20535
[close]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18911-L18931
[air-look]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21017-L21025
[effective]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17710-L17715
[f10]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18827-L18832
[notice]: https://github.com/mpmdw/JouleWise/blob/56f239dd2/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L12657-L12663
[item]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/docs/process/run_state_item.schema.json#L1-L25
[b2]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L850-L902
[freeze]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L502-L505
[fixed-eight]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L941-L976
[roster]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/pilot_protocol_v4.md#L1008-L1035
[r17]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md#L103-L186
[air-desk]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md#L204-L227
[unpack]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_harvest_off.py#L173-L188
[desk]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_harvest_off.py#L196-L291
[admission]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_series.py#L267-L284
[series]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_series.py#L510-L631
[series-bind]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_series.py#L687-L744
[terminal]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L161-L199
[issued-final]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L221-L309
[eligibility]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L388-L465
[structural]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L317-L350
[canonical]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L491-L516
[build]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L621-L704
[desk-branches]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L743-L903
[thermal]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L779-L815
[history]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_next_arm_packet.py#L923-L973
[triage]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/apple/v4_cadence.py#L117-L256
[digests]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/apple/v4_registration.py#L433-L460
[battery]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/joulewise/align/apple/v4_registration.py#L656-L695
[prepare]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L46-L129
[kit-check]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1165-L1181
[live]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1205-L1225
[bound]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1228-L1262
[held]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1265-L1396
[native]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1400-L1466
[arm-readback]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1467-L1565
[install]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1725-L1819
[arm-outcome]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/scripts/align_v4_session.py#L1910-L2052
