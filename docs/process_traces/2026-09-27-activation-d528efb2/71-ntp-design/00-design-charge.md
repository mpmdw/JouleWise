# Design consult NTP-ENFORCE-DESIGN-01: enforce network time OFF (H5) and per-capture timed-log attestation (H6) in code, on every 25G83 capture route

You are ONE of several blind, independent design seats (decision log D-144 co-design); a cold Fable judge rules afterwards. You advise; disagreement is useful.

## Facts (verify; cite file:line). Read-only checkout: your worktree (main `9eab16f8` plus records).

- **Why:** during the W1/W2 calibration windows of 2026-09-27 macOS network time was ON; the time daemon's corrections cost 4 of 24 captures and moved two members by microseconds. The cold addenda A2/A3 (`docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/21-ruling.md`, `31-addendum-ruling.md`) set the conditions, final text in A3 §4.4–§4.6: **H5** network time OFF ≥ 600 s before the first capture of every 25G83 window, by `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` (exit 0 and exact output `setUsingNetworkTime: Off`), receipt saved, restored ON after with a receipt; **H6** one window query of the `timed` log after the last capture with a **coverage witness** (a `[com.apple.timed:data]` line older than the first capture's 180 s lead) and a per-capture marker search; failure → `network_time_unattested` (all captures) or `network_time_slew_attested` (that capture); such a capture is never a calibration member, bracket endpoint or claim-bearing capture; seven defect-shaped tests. **H7** first OFF-window comparison. These must be in force before the NEXT 25G83 window of any kind (calibration, evidence, claim).
- **The scout's map:** `docs/process_traces/2026-09-27-activation-d528efb2/70-ntp-enforce-scout/report.md` (read whole). Its central finding: the calibration writer finalizes a `valid` ledger row **during each slot**, before the window-wide H6 witness can exist, so a later H6 document does not revoke the row. It proposes an immutable window-attestation artifact plus mandatory downstream admission checks (member set at issuance; bracket binding; claim evaluation), versus a pending-to-final ledger protocol.
- The evidence chain (`joulewise/quiet_predicate_campaign.py`) already does OFF/restore and a per-envelope query (whose header-only case A3 says is insufficient). The pack path checks OFF at arm only (`joulewise/arm_readiness_evidence_t0.py:1225-1256`).
- Constraints: the four D-138-pinned estimator files (`joulewise/powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`) must not change (decision log D-138). A concurrent transaction (D-138) is rewriting calibration authority in `joulewise/calibration_bracketing.py` and adds `joulewise/claim_hold.py` (a build-keyed claim hold); design so the two compose. Registration amendments for H5–H7 need the owner's signature.

## Questions

1. **The architecture:** attestation artifact + admission checks, pending-to-final ledger, or other — where is the H6 verdict produced, stored (custody, digest), and CONSUMED on each route (derivation calibration → issuance; ordinary bracket pre/post → bracket binding and evaluation; evidence/idle nights → harvest; claim pack windows → claim evaluation)? What makes it impossible for an unattested capture to become a member, endpoint or claim input (the "no route" property), and what test enumerates the consumers?
2. **H5 lifecycle** per route: who sets OFF, where the receipt lives, how ≥600 s is proved on both clocks, and how ON is restored on every exit path (including crashes and stand-down).
3. **The exact module/file plan** (new helper module, which chains/scripts change, which tests), the WRITE_SCOPE for one implementation seat, and the order relative to D-138 and the cap route R windows.
4. **What needs the owner** (registration amendment text for H5–H7) and what needs a live bench check (the real passwordless command, the old-log case).
5. Risks: what would make the attestation lie (log retention, time-zone/offset parsing, a query run late), and how the design refuses rather than passes in each case.

## Output

≤ 1,500 words, plain language, every claim cited or marked as inference; first line `SEAT: <model> — NTP-ENFORCE-DESIGN-01`. Read-only; modify no repository file; no git writes; never run `systemsetup -set…` or `sudo`; no capture; no battery read.
