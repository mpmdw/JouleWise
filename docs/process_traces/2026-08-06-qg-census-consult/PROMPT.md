# CONSULT — quiet-guard census/custody observation invariant: closure shape (NOT fix round 4)

## Role and bounds

You are Sol, design peer (rule 2; 1 round; license to disagree).
Read-only; WRITE_SCOPE: none. The standing escalation trigger has
FIRED: the observation-failure→absence class has now failed two
consecutive rounds by different local formulations. Branch
`impl/quiet-guard` @ efe504a.

## Defect history (read the reports; same directory
/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/)

- Round 1 (qg-fix2): original convergent blocker — observe() failures
  conflated with ABSENT; census silently dropped unobservable PIDs;
  false-zero could release custody. Fixed and verified closed.
- Round 2 (qg-fix3): a bounded census re-snapshot retry was added for
  AVAILABILITY (transient churn aborting recovery). The lead's
  contract dictated "retry only for UNRELATED pids" — introducing a
  PROTECTED-SET ENUMERATION concept. Sol implemented the retry
  registry-unaware; audit qg-delta2.md proved a registered PID could
  vanish via retry. Count 1.
- Round 3 (qg-fix4): protected set threaded from recovery; audit
  qg-delta3.md proves the LEASE OWNER (custody-relevant but not a
  registry entry in quiet_held/recovery_required with empty registry)
  is omitted, and protection matches by PID ONLY (PID reuse across
  snapshots defeats it). Count 2 → trigger FIRED.

The magistrate's own diagnosis, offered for refutation: the recurring
failure is STRUCTURAL — "enumerate the identities that deserve
fail-closed treatment" keeps missing members and degrading identity to
PID. Each round patches the enumeration; the class regenerates.

## Question: the correct closure shape

- **Option A (magistrate's lean): eliminate the enumeration.** The
  census retry NEVER converts any unobservable PID to absent: a
  re-snapshot may only help a transient RESOLVE to observable; if any
  PID listed in snapshot 1 remains unobservable/absent-without-
  observation at the bound, the census REFUSES entirely. No protected
  set exists; universally fail-closed. The availability benefit
  narrows to genuinely-resolving transients — under rigor-first
  (D-113 clause 8) that trade is acceptable; recovery under heavy
  churn refuses and is re-runnable. Analyze: does ANY legitimate
  recovery scenario require dropping a PID that was listed and then
  became unobservable? (A process that EXITS between snapshots — how
  is clean exit distinguished from observation failure in the current
  primitives? If exit-vs-failure cannot be reliably distinguished,
  does A over-refuse in routine operation, and how badly?)
- **Option B: keep the protected set but derive it from ONE
  authoritative state function** (registry entries + lease owner +
  future custody holders) with FULL-identity matching (pid, start
  time, executable, argv digest), never PID-only, with a test pinned
  to the state schema so a new custody-bearing field cannot be added
  without extending the function.
- **Option C: your better shape.** Explicitly invited.

Also answer: (1) whether ps-listing + per-PID observation is the right
primitive at all, or whether the census should be built purely from
the sysctl table walk it already trusts (one snapshot source, fewer
partial-failure modes); (2) the availability question honestly — is
refuse-and-rerun acceptable for the privileged recovery path given its
call sites in joulewise/quiet_guard.py; (3) the minimal discriminating
regression set for the chosen shape, including a PID-reuse case and a
lease-owner case; (4) whether any part of the round-2 availability
requirement should simply be REVOKED (the lead is prepared to revoke
it — it was the weakest requirement in the stack and seeded the
class).

## Output

claude-codex-report/v1 envelope, genre=consult. Ranked recommendation
with rationale; explicit answers to (1)-(4); disagreement licensed.
One round; the magistrate synthesizes and decides. Emit the report as
your FINAL MESSAGE.
