# Exhibit F — standing rulings cited by the design, and what the pre-registration's latest revision does and does not license

All blocks are verbatim excerpts at commit `a90ab4e8`, with file path and line
range stated above each. Where the only primary record of a ruling is a process
trace or history document rather than the decision log, that is stated
explicitly, together with why no non-narrative source exists.

## F1 — D-161 THREAT-MODEL PRUNE (`docs/decision_log.md:207`, index row, and `:10685-10696`, body)

Index row, line 207, quoted whole:

```
| D-161 | THREAT-MODEL PRUNE (Ed, 2026-08-27, in-session, ratifying the magistrate's three-point proposal: "yes to all 3. right instincts"): the in-process adversary is already OUT of the threat model (D-139 A1; D-148 (6)) and the paper's §7 states a single trusted operator, so custody mechanisms whose ONLY defended-against actor is the trusted operator touching a file are over-engineering; this week they cost the operator three hand edits and blocked the mint twice. RULINGS: (1) the reviewed pinset gets a REVIEWED REFRESH LANE (`--refresh-row`, re-derives a row from the committed tree by the verifier's own code path, prints the diff, lands as an ordinary PR); the "no update lane" test becomes "no UNREVIEWED update" — stream S14; (2) THREAT-MODEL-PRUNE-01: enumerate from code (three-seat consult) every refusal whose only actor is the trusted operator and downgrade it to WARN-AND-RECORD or retire it; fail-closed STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION (missing calibration, unresolved anchor, absent floor, stale drift evidence, unfrozen plan, post-hoc analysis choice); prunes that the frozen `_v4` runbook or estate 11 depend on wait until after the transaction; (3) the paper's §7 says the repository is tamper-EVIDENT for the operator's own benefit, not tamper-PROOF against anyone (lands with the `_v4` fills). Ed's hands are no longer required for the W-10 pin. | adopted (Ed) |
```

Body, lines 10685–10696:

```
 10685	## D-161: threat-model prune (Ed, 2026-08-27)
 10686	
 10687	Index row carries the operative detail. Trace: the prune consult under
 10688	`docs/process_traces/2026-08-27-t26/threat-model-prune/` — three blind seats
 10689	+ `04-MAGISTRATE-RULING.md` (ADDENDUM, 2026-08-27 PM): the operative test is
 10690	MISTAKE vs DELIBERATE (fail-closed for physics/evidence, pre-registration and
 10691	operator mistakes; deliberate-only guards retire); the histsem pin is cured
 10692	ASYMMETRICALLY (historical-side equality stays B; current-side equality and
 10693	the delta list → warn after `_v4`); HISTPACK-PROMISOR-NOFETCH-01 RETIRED
 10694	unbuilt; only the refresh lane lands before the night; the post-transaction
 10695	prune waves (a)–(f) are enumerated in the ruling; refresh lane: stream S14,
 10696	`feat/pinset-refresh-row-lane`.
```

Operative for this packet: "fail-closed STAYS where the failure is
PHYSICS/EVIDENCE or PRE-REGISTRATION."

## F2 — D-181 WINDOWS RUN WHENEVER THE MACHINE IS QUIET (`docs/decision_log.md:227` index row; `:11886-11920` body)

Index row, line 227, quoted whole:

```
| D-181 | WINDOWS RUN WHENEVER THE MACHINE IS QUIET — no cadence rule (clean census, day or night, several windows per day when the gates pass; every soundness fence unchanged); Fable 5.1 is the final eyes on every merge (gate rows 7/12 unchanged, final head sha in row 12); the owner's hands step for the first pack night prepared and emailed; lanes INSTALL-WINDOWS-MULTI-01 → ARM-RETRY-CLASS-01 → ARM-CENSUS-IDLE-INTERACTIVE-01 promoted to the head of the agent lane behind the 09-15 harvest event | ratified by Ed (2026-09-14, directive issue #337; recorded verbatim, nothing installed by the entry) |
```

Body, lines 11886–11920, quoted contiguously through the whole of clause 1:

```
 11886	## D-181: Windows run whenever the machine is quiet; Fable 5.1 is the final eyes on every merge; the owner's hands step is prepared now (Ed, 2026-09-14)
 11887	
 11888	**Status:** ratified by Ed, 2026-09-14 16:43 PDT, as directive issue #337 (owner, at the
 11889	machine), verbatim in
 11890	`docs/process_traces/2026-09-13-activation-24b9d3dd/55-ed-directive-337-verbatim.md`.
 11891	Recorded by the headless magistrate (activation `24b9d3dd`) through this PR, the same
 11892	way issue #316 became D-180 (Ed's words: "Record this ruling as a dated decision-log
 11893	entry through a PR under the normal gate, the same way #316 became D-180; do not amend
 11894	rule text yourself outside that PR"); nothing below is installed in code, runbooks or
 11895	the night machinery by this entry — each clause names its implementation lane, and
 11896	until that lane lands the existing mechanism's limits remain facts, not rules (decided
 11897	≠ done: the ruling is in force from the moment it names; what the machinery cannot yet
 11898	do is a mechanism limit, as Ed's clause 1 says). The ruling is standing;
 11899	by its own text it applies after the night armed under directive #336
 11900	(`d079-epoch-25g83-derivation-n1-20260915`, t0 2026-09-15 02:56 PDT) and to every
 11901	window after it, and it does not touch that night. Forcing context (factual, no rule):
 11902	the 2026-09-13 night fired and was refused by its own t0 census (an interactive session
 11903	and agent desktop apps present); the 2026-09-14 morning install span closed without an
 11904	arm because the arm-time census never cleared; the ordinary documented recovery was a
 11905	new plan for the next calendar night, until directive #336's one-night owner
 11906	authorization of an evening install. Ed rules that the spacing was never a scientific
 11907	requirement.
 11908	
 11909	1. **Windows run as soon as the machine is quiet; no cadence rule.** Whenever the
 11910	   census is clean, day or night, several windows per day if the gates pass, with no
 11911	   artificial spacing (no "one night in three", no "only at 02:56", no minimum gap
 11912	   between windows). Ed keeps the machine quiet whenever he is not using it and will
 11913	   close every interactive session and quit the agent desktop apps on request; a
 11914	   notice email is enough. The soundness fences stay exactly as they are: physics and
 11915	   evidence refusals, pre-registration before data, the census at arm and at t0, the
 11916	   twelve-row gate, email-then-arm with Ed's NO overriding. Nothing else about timing
 11917	   is a rule. Implementation: the current machinery pins one plan at a fixed daily
 11918	   launchd minute inside the 02:45–03:30 belt with a single 07:00 dead-man and a
 11919	   calendar-day install span — a mechanism limit, not a scientific one. Lanes
 11920	   `INSTALL-WINDOWS-MULTI-01` (install spans as a list, dead-man per span),
```

Two clauses of this entry cut in opposite directions and are both quoted
above: "no artificial spacing" (line 11911) and "The soundness fences stay
exactly as they are: physics and evidence refusals... the census at arm and at
t0" (lines 11914–11916).

## F3 — the sensible-gates directive (2026-09-10)

STATUS OF THE SOURCE: this directive has no decision-log entry of its own. The
decision log carries only a consequence of it (F4). The only tracked record of
the directive's own words is a history document,
`docs/process/automation_history_2026-09-16.md`, which is narrative. It is
quoted here, contiguously and whole including its own ASSUMED caveat, ONLY
because the directive's exact words are the object of proposition 4 (whether a
proposed CPU cutoff is "scientifically adequate"), and because the brief in
exhibit G binds the implementer to that wording. Lines 145–155:

```
   145	- **Sensible gates (Ed, 2026-09-10 ~04:20).** "make sure there are no silly gates on accepting numbers … recall that
   146	  time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic compared to the
   147	  measurement". Every tolerance on the claim path is sized to the instrument, boundary-attribution limit ≈ 1 J and minimum difference required for a claim
   148	  ≈ 5 J (`docs/decision_log.md` D-078 cl.11), never to decimal places; measurement-validity and evidence refusals stay. The review of measurement checks
   149	  (lane GATE-SENSIBILITY-SWEEP-01) inventoried 299 gates and merged three repairs (R1/R3/R4) plus the prefill probe's idle setting (G2-a `idle_seconds 75`) in
   150	  PR #314 (`0d4bb4fb`), and sent the zero-point band (an `isclose(rel_tol=1e-9, abs_tol=1e-12)` comparison of two
   151	  binary64 routes over the same four numbers, D-165) to a cold gate, which ruled it scale-bounded: sound below 8,192 J
   152	  per run and not a blocker for the prefill probe (G2-a; cold gate 47; the directive is recorded in the assistant memory file
   153	  `sensible-gates-directive.md`; `TASK_QUEUE.md` GATE-SENSIBILITY-SWEEP-01 row; `docs/decision_log.md` D-124 addendum
   154	  2026-09-13). ASSUMED: the 1e-15 figure is Ed's recollection; the log shows a 1e-15 s quantization at
   155	  `decision_log.md:6667`, not a 1e-15 J tolerance.
```

The two instrument-sized numbers this cites — attribution limit approximately
1 J and claim-side bar approximately 5 J — are attributed to
`docs/decision_log.md` D-078 clause 11. The judge may verify that citation
directly; this packet does not excerpt D-078.

## F4 — the decision log's own record of the sensible-gates sweep: D-124 dated addendum (`docs/decision_log.md:11825-11842`)

```
 11825	### D-124 dated addendum — 2026-09-13 (cold gate 47, GATE-SENSIBILITY-SWEEP-01 B1): the zero-point provenance band is scale-bounded, and its re-set is ruled but not yet installed
 11826	
 11827	Round 4's `isclose(rel_tol=1e-9, abs_tol=1e-12)` band compares the stored ABBA delta
 11828	`(B1+B2-A1-A2)/2` with the zero-shift contrast `z` (a coefficient-weighted `fsum` of
 11829	freshly re-integrated member energies). These are two different binary64 routes over
 11830	the same four numbers: the sequential route rounds once when it forms `B1+B2` (and
 11831	once more if the members straddle a power of two), so `|z - delta| <= 0.375 x
 11832	ulp(B1+B2)`, a quantity that steps in powers of two. Consequences, bench-derived: the
 11833	band CANNOT refuse identical operands while the largest member is below 8,192 J,
 11834	whatever the operand pattern, nor below 16,384 J when the four members lie in one
 11835	binade; the first refusal on the packet's pattern is at exactly 16,384 J per member
 11836	(demonstrated at 20,000 J: sequential 1.8189894035458565e-12 J against `fsum` 0.0),
 11837	and an any-pattern refusal is demonstrated at a largest member of 8,625.6 J. A second
 11838	condition must hold for any refusal at all: `rel_tol` rescues the block unless its
 11839	true delta is smaller than about 1.7e-7 of the member scale (about 1.8 mJ at 20,000 J
 11840	members), so only blocks whose members nearly cancel are exposed. G2-a member
 11841	energies are tens of joules, three orders below the lowest refusing scale, so B1 is
 11842	not G2-a-blocking.
```

This is offered as the SHAPE a prior cold gate used to decide whether a
numeric threshold was adequate: it derived the threshold's behaviour
analytically, demonstrated the first refusing scale by execution, and compared
that scale with the actual measurement magnitudes. Proposition 4 asks for the
same class of showing about the busy-core cutoff. Nothing here decides
proposition 4.

## F5 — A212, the refusal fast-retry lane

The primary record and its explicit non-ratification are quoted in exhibit E
§E4. Repeated here only by reference so the judge reads it once, in the
context of proposition 9.

## F6 — the pre-registration's revision 3: what it licenses, and what it is silent on

`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, lines 509–526
and 538–553, quoted contiguously:

```
   509	This revision authorizes no window and licenses no measurement, exactly as
   510	revision 1 did not. The arm still goes through the standing gates and the
   511	email-then-arm handback, and Ed's NO overrides.
   512	---
   513	
   514	# Revision 3 (2026-09-17, cold-gate ruling 69, packet 69)
   515	
   516	STATUS: cold-gate ruling 69 (packet 69, activation 9853dd2b), paired Opus
   517	refutation 12 and magistrate synthesis 13; recorded by the magistrate; not a
   518	magistrate amendment (rule 11)
   519	
   520	Revision 1 above is sealed and revision 2 stands as written. Not one word of
   521	either is edited here. This revision does one thing and nothing else: it
   522	re-fills the `[CHAIN_SHA256]` field that revision 1 lists under "Fields filled
   523	at commit" as "a fact that does not exist yet; none is a scientific choice, and
   524	filling them does not reopen any rule above." Re-filling a field the sealed
   525	text designates non-scientific reopens no sealed rule; the authority for the
   526	re-fill is this ruling.
```

```
   538	## The one change
   539	
   540	Revision 1, "Sample.", pins the chain at the digest beginning b8bf5b0a85bb.
   541	For every capture night opened after this revision lands, that sentence is
   542	read with the digest below in place of the sealed value:
   543	
   544	Chain digest in force (revision 3): b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb
   545	
   546	That value is the SHA-256 of `scripts/night_chains/calibration_derivation_only.zsh`
   547	at the committed head the night is armed from, written by the magistrate in
   548	the same commit that records this revision, and verified three ways: the test
   549	`tests/test_preregistration_chain_digest.py` (ruling 69 Q4) fails unless the
   550	line above equals the tracked chain's digest; `python3
   551	scripts/gen_derivation_night.py --check` passes at that head; and the plan
   552	sidecar the night gate reads at t0 refuses `night_chain_digest_mismatch` if
   553	the bytes move afterwards.
```

Line 521 states the scope: "This revision does one thing and nothing else." The
one thing is the chain digest. The revision contains no sentence about
admission, machine quietness, the load average, a bind window, plan schema
versions, or what the gate may do between `t0` and the chain start. The
consult states the same conclusion at exhibit A §5 ("Revision 3 licenses a
digest refill, not new science semantics"). Whether admission semantics fall
inside or outside the sealed sample definition is for the judge; this exhibit
establishes only that revision 3 does not address them.
