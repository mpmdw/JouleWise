# Magistrate synthesis — D-169 stage 3 (interactive magistrate, 2026-09-08 ~09:40 PDT; Ed present, may veto)

Inputs: cold Fable ruling `10-coldgate-fable-ruling.md` (UPHELD WITH AMENDMENTS, six decisions) and the Opus
contract-lens refutation `11-coldgate-opus-refutation.md` (AMEND on 1, 3, 4, 5; UPHOLD 2; "sound with amendments
1 and 3"). Both were read against the consult (exhibit A) and the code at 71588d6a. They converge on every
load-bearing point; where they differ the synthesis below says which text governs and why.

## Ruling of record (adopted; to be recorded as D-176)

1. **GO receipt.** One new schema, `joulewise.pack_night_go_receipt.v1` (the judge's name governs; the Opus
   "d149 v2" naming is the same object), produced only by the night driver after ARM verify, with the judge's exact
   key list (plan, pack id + sha256, arm receipt id/sha256/validity, boot session, T-0 evidence set, launch manifest /
   window environment / window chain sha256s, repo head, measurement root/head, confirmation-record sha256,
   authorization-record sha256, census, issued/valid_until monotonic, C1–C5 conditions, verdict). The
   `joulewise.t0_unattended_d149_go_receipt.v1` schema is RETIRED and REFUSED, never grandfathered (Opus F1/F2;
   judge §4). Consumption: `_consume_launch_capability` gains required GO keywords defaulting to the missing
   sentinel, re-reads the bytes, recomputes the digest, and refuses on any binding mismatch, wrong class, non-GO,
   any non-PASS condition, or a monotonic time outside [issued, valid_until); two ruled codes
   (`launch_go_receipt_missing`, `launch_go_receipt_invalid`) registered by R-8 before emission. Consumption record
   → `launch_consumption.v3` adding `go_receipt{…}` and `step6_confirmation{…}`; v2 goes to the legacy branch and
   replays only with `require_current_boot=False`; `verify_consumed_launch` re-reads the GO bytes and refuses a live
   replay of a record without `go_receipt` (Opus F4, judge §1). No second lock: the existing O_EXCL consumption
   write is the linearization point (Opus F5).
2. **G2-b.** Stays `TRANSACTION_PACK` with full C2–C5; C1 becomes an authenticated, purpose-bound transaction
   authorization record (0600, create-once, in transaction custody, sha256-bound into the plan) with `purpose ∈
   {G2B_SHAKEDOWN, CAMPAIGN_TRANSACTION, T0_REHEARSAL}`, `claim_eligible`, `pack_sha256`, `permitted_chain_sha256`,
   `permitted_blocks`, `authority`. The G2-b record is a magistrate authorization under D-171 §3 naming the exact
   pack, attempt, permitted chain and `claim_eligible: false`; it is NOT `V5-TRANSACTION-GO-01` and does not
   discharge it (Opus §2 text added to the judge's §2). `DIAGNOSTIC_NO_PACK` for G2-b is rejected.
3. **Confirmation custody.** The judge's design governs: a create-once `step6_confirmation_record.json` in
   transaction custody (table path, table sha256 = hC, transcript sha256, confirmed_at), bound into the plan; hC
   reaches the launcher by argv and the child by the authenticated v3 consumption record; the environment route is
   REJECTED. Opus F6 is ADOPTED on top: for a `TRANSACTION_PACK` launch both `--step6-confirmation-table` and
   `--expected-confirmation-digest` become REQUIRED with an omission-refusal regression (today they are optional and
   a pack night whose changed set holds no conditional path would launch with no confirmation at all).
4. **Rehearsal obligations.** G2-a discharges no gate; it may contribute observational records only after
   `run_night.py` sets `stdin=subprocess.DEVNULL`. The closing rehearsal is one isolated pack-bound night on a
   rehearsal pack with a `rehearsal-t0-unattended-` window id and disjoint custody; its GO receipt has
   `purpose=T0_REHEARSAL`, accepted by the consumer only on a prefixed id with disjoint roots; G7 becomes real by
   presenting the rehearsal-class receipt to the production launcher and recording the class refusal. The consult's
   "T-0 producer substantially implemented" sentence is corrected per Opus F3: the ARM T-0 EVIDENCE author exists;
   the GO producer and the rehearsal-bundle producers do not.
5. **Kernel graph.** The judge's rows govern (UNATTENDED-LAUNCH-01 re-rooted on this ruling and owning the consumer
   + S9-06 closure; D169-STAGE3-01 retargeted; NEW NIGHT-PACK-REHEARSAL-01; T0-UNATTENDED-01 re-rooted; the stale
   `REHEARSAL_PRODUCER_WORK_ORDER` pointer replaced by the G1–G10 table; T0-LIVENESS-BOUND-EMPIRICAL-01 a registered
   limitation through G2-b; V5-TRANSACTION-GO-01 text amended). Opus F8 is ADOPTED as the installation rule: every
   clause names the file, symbol, or JSON pointer it installs into, and the bookkeeping seat's acceptance includes
   `tests.test_gen_state`.
6. **Order and gate shape.** Seat 1 = the contract `docs/contracts/pack_night_go_receipt.md` (exact key list, D-170
   clause map), drafted from this synthesis and refuted by Opus before any code; seats 2 (producer + night-driver
   orchestration) and 3 (consumer + consumption v3 + verify replay) in parallel worktrees after the contract lands;
   seat 4 (rehearsal purpose + G7) after seat 2; each under the C-028 gauntlet with the consult's replay list plus the
   judge's three additions; build may precede NIGHT-REHEARSAL-01's harvest; a second cold gate on the integrated head
   and the real plan bytes precedes the first pack-bound night.

## Failure-mode tests (both seats agree they pass under the adopted text)
Forged receipt: must carry the sha256 of an arm receipt that replays to GO in custody. Replayed receipt: the arm
receipt id is single-use at the O_EXCL point. CLI-then-callee mutation: the callee trusts only bytes it read.
Census bypass: unchanged, still the driver's first act. Pre-registration drift: pack sha256 and chain sha256 are
bound into the GO and re-checked at consumption. Class relabeling: purpose and claim_eligible are bound into the
consumption record and read by the realization recheck.

## Disposition
Adopted as D-176 (Ed may veto). Next: a seat installs the decision-log entry, the kernel graph of §5, and drafts the
seat-1 contract from §1–§4 for the Opus refuter; no implementation scope is issued before that contract lands.
