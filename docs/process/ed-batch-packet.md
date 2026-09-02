# Ed's batched session — the decision packet (assembled 2026-08-16; A1-A3 DECIDED 2026-08-17 → D-139)

> **STATUS: decisions A1, A2, and A3-defaults are RULED (D-139,
> docs/decision_log.md). Remaining: the B hardware batch, the A4 marker
> ruling, the environment-fingerprint semantics, and the final exact-byte
> publication confirmation at the transaction's irreversible point.**

One sitting, two kinds of items: **decisions only you can make** and **hands-on
qualification only you can run**. Everything here is a pointer to its ONE home;
nothing is restated. Estimated sitting: decisions ~45 min, hardware batch as
scheduled by the runbook items themselves.

## A. Decisions (paper/risk scope — nothing blocks agent work except A3)

**A1 — The in-process-adversary family (one call closes three items).**
Do you rule a deliberate same-UID/in-process adversary OUT of the threat model
on your single-operator machine? The three mechanisms already carry
trusted-operator registered limitations; this call decides whether any get the
stronger (costlier) cure:

- Recorder check-to-grant race → if OUT: WO-RECORDER-GRANT-IDENTITY drops to
  its registered limitation (saves a cold gate + implementation). Design is
  ready if you want it anyway: `docs/process_traces/2026-08-16-grant-identity-consult/`.
- T-0 capture provenance → if OUT: the trusted-operator MVP claim stands as
  registered (the option-(a) attested-capture architecture stays dead).
  Consult: `docs/process_traces/2026-08-15-t0-capture-provenance-consult/`.
- Launch-binding forged-context residual → already registered; the call makes
  it final. Custody: `docs/process_traces/2026-08-16-launch-f3-coldgate/`.

Magistrate recommendation (given your 2026-08-16 direction): rule OUT for all
three; spend nothing more on in-process defense.

**A2 — Gamma's scientific rulings (required before the production freeze +
L10 replay; the code accepts either branch of each).**
(i) prefill p256 test + direction; (ii) multiplicity family membership and m
(the consult recommends one Holm family, alpha=0.05, m=2, decode+prefill,
two-sided — a contrary ruling needs two justified m=1 families);
(iii) p256 floor: dedicated artifact vs governed p128→p256 transport.
ONE home: `docs/process_traces/2026-08-15-consumption-edge-consult/` (F2) +
the RULING-REQUIRED list in the decision log's WO-CONSUMPTION-EDGE entries.

**A3 — Phase-2 reserved approvals (rule-11 irreversible; the transaction
cannot run without these).** The plan presents options, decides nothing:
successor pack IDs/numbering (recommended: uniform `_v2`, freeze-0002
chain-monotonic with predecessor bindings), freshness semantics per row,
horizons, the family publication marker, and the final exact-byte publication
confirmation. ONE home: `docs/process_traces/2026-08-16-phase2-plan-consult/`
(R1 cl.6 maps each reserved item).

**A4 — Contrast-pack pending-ratification / TODO markers ruling** (carried
from T8; unchanged). See RUN_STATE's Ed-owed list for the pointer.

## B. Hands-on qualification (the hardware batch — unchanged from T8's list)

The expanded qualification script: D-127 sudoers install + exercise both
vectors; dress rehearsal E-4→E-9 + author→arm→verify→consume vs scratch
custody; sampler checklist; rail probe; backlight rows; **ED-Q-L9-3
quiet-state baseline** (gates the census WO — can ride ANY earlier tap);
a9/a10 desk replay; ED-QUAL-L4-1 decisive replay. ONE home: RUN_STATE
§Ed-owed + `docs/phase_2/window_runbook.md`.

**L10 `_v5` PRE-WINDOW — Ed's portion.** Review the preserved L10-A record,
including the G2-b verdict, bracket binding, exact finalizer-refusal result,
and matching before/after tree hashes, before recording GO for the claim-bearing
transaction ([V5-TRANSACTION-GO-01 acceptance](state_kernel.json#L5094),
[ruling 89 R-4](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L74)).

## What happens after this sitting

A1+A2 unblock gamma's production freeze; A3 unblocks the Phase-2 atomic
re-freeze (whose full transaction plan is custodied and whose staged payload
is verified at `impl/wo-detect-pulses-budget` @ e22e658); B closes the last
Phase-1 work order (census) and the operator-qualification rows. Then:
Phase-3 re-audit → READY-candidate council → windows.
