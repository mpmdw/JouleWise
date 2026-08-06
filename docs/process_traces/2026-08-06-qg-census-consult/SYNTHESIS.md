# Synthesis — quiet-guard census/custody closure consult (2026-08-06, Fable magistrate)

## Trigger

Standing escalation trigger FIRED (rule 11): the
observation-failure→absence class failed two consecutive rounds by
different formulations (round 2 introduced a registry-unaware retry;
round 3's protected-set fix omitted the lease owner and matched by PID
only). Per doctrine the next spend was this consult, not fix round 4.

## Magistrate admission on the record

The round-2 lead contract seeded the class: dictating "bounded retry
for transiently unobservable UNRELATED pids" introduced the
protected-set ENUMERATION concept in service of an availability
requirement no call site actually needed. The enumeration kept missing
members (registry-unaware, then lease-owner-less) and degraded identity
to PID. The structural diagnosis — fail-open-vs-fail-closed must not
depend on a caller-supplied enumeration — was confirmed by the consult.

## Adjudication: Option C adopted in full (zero dissent)

1. **custody_roots first-class state** — lease owner + every registry
   entry; retained with the lease; only lease clearance clears.
2. **recover() owns the proof under one lock** — state read, kernel
   inventory, exact candidate observation, clearance; the privileged
   helper supplies acknowledgment only; protected-set plumbing deleted.
3. **KERN_PROC_ALL single-snapshot inventory** (PID/ppid/microsecond
   start) as presence/topology authority; KERN_PROCARGS2 only for
   custody candidates; no /bin/ps in the census path (the consult
   showed the ps-enumerator's own exited row makes universal
   fail-closed over ps self-refusing).
4. **No semantic re-snapshot within an invocation** — candidate churn
   refuses with byte-identical custody; a fresh operator invocation is
   the availability boundary; PID reuse is detected via the
   start-time anchor (PID_REUSED classification).
5. **Round-2 availability requirement REVOKED** (retained: bounded
   low-level acquisition retries pre-acceptance; candidate narrowing
   as the honest availability win).

Sol's design out-ranked both magistrate options (A universal-refusal
over ps was disqualified; B's authoritative-function union remains an
omission surface). Scorecard: another cross-model design win for the
peer on structure; the magistrate's contribution was the structural
diagnosis and the revocation license.

## Disposition

Implementation launched same session (xhigh, consult-as-spec); five
consult-named regressions + ps-removal regression mandatory; delta
re-audit follows; the class's signature counter resets only when a
delta audit accepts the new shape. Live-Darwin payload validation and
installed-path checks remain lead-owned gates before any real
installation.
