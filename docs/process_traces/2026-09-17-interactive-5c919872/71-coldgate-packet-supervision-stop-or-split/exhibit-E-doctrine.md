# Exhibit E — the escalation and stop rules the judge applies

Three sources. Each is pinned; each block is byte-exact `nl -ba <file> | sed -n
'<a>,<b>p'` output; the stated proposition is what the block is offered for and
nothing more.

## E1. `docs/orchestration.md` — the cold gate's definition and the repeated-signature route

Source path: `docs/orchestration.md`, tracked in this repository; read at
`/Users/edr/code/JouleWise` with `git rev-parse HEAD` =
`80dbcb4cfee5b09b77b4f1ab86c1e52deee35977`; file sha256
`e335d13d925025a26a6588f77075c85f8c85382d8e8ebcbcc6935dbfc36eafc4`; the file's
own last change is commit `353720d20813f3f7a70650056c89fbcca11b5b25`. Lines
51-75, which is the whole "three role names" list plus its closing sentence, so
the lieutenant and magistrate definitions bracketing the cold-gate bullet are
visible and the bullet cannot be read out of its list. Proposition addressed:
what a cold gate is and what sends the merge question to it — the sentence at
line 67-69 is what consult 19 cites as `docs/orchestration.md:64` (exhibit A
§A3, `Authority`).

```
    51	Three role names recur in the project record:
    52	
    53	- The **magistrate** is the designated lead. It decomposes work, rules on
    54	  design questions, adjudicates review findings, performs the final contextual
    55	  review of the exact merge candidate, and retains merge authority. That last
    56	  review is non-delegable under D-121.
    57	- A **lieutenant** coordinates bounded implementation or review lanes and
    58	  assembles their evidence. It does not decide process-policy changes,
    59	  measurement or funding scope, calendar commitments, irreversible actions,
    60	  or whether to add or remove a review mechanism. D-080 records the process-
    61	  policy subset; D-119 records the measurement, scope, and calendar boundary.
    62	  Those questions return to the magistrate or Ed, according to the owning
    63	  decision.
    64	- A **cold gate** is an independent adjudication from a fresh session that has
    65	  not inherited the working lane's assumptions. The gate receives a
    66	  mechanically assembled evidence packet and is paired with a distinct
    67	  contract-focused reviewer. A repeated defect signature after a fix round
    68	  sends the next spend to a consult and returns the merge question to this
    69	  gate (D-087/D-088). Proposed process rules and other triggers named by an
    70	  owning decision use the same route; the magistrate records the disposition
    71	  and any dissent rather than serving as a reviewing seat.
    72	
    73	These roles distribute reading and coordination; they do not transfer final
    74	verification, hardware operation, scientific scope, or publication authority.
    75	
```

## E2. `docs/process/coldgate_charter.md` §3 — the mandatory convening triggers

Source path: `docs/process/coldgate_charter.md`, same checkout and revision;
file sha256 `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`,
which is the digest pinned in this packet's Charter pin section and supplied to
the judge independently in the convening prompt. Lines 29-40 (§3 entire,
including its closing paragraph). Proposition addressed: whether this gate was
mandatory and what a trigger does and does not establish. The judge holds this
file whole and should read §§1, 2, 4, 8 and 9 there rather than here; §9's
second bullet — "Two consecutive rounds failing with the same signature is a
structural problem: the next spend is a consult or redesign, not round three.
If the packet shows this pattern, licensing another same-shape round requires
explicit justification." — is the operative authority for Q2, and it is in the
charter itself, not in this exhibit.

```
    29	## 3. Mandatory convening triggers
    30	
    31	1. Any second fix round on the same defect.
    32	2. Any reversal or reinterpretation of a stop signal or prior verdict.
    33	3. Any irreversible action (deletion, merge waves, measurement-window
    34	   commitments, claim publication).
    35	4. Any proposed process rule (including amendments to this charter).
    36	5. Any turn ending in a "waiting" state on a scarce open resource.
    37	
    38	A trigger explains why review was mandatory. It creates no presumption
    39	about the answer, severity, or adequacy of the packet.
    40	
```

## E3. The project's adversarial-review practice on delta re-audits and same-signature partitions

Source path: `/Users/edr/.claude/skills/adversarial-review/SKILL.md`; file
sha256 `cc14a626e6c67ab01675a524d287f6e73d44fbd859b6226c2443776b880ba3dd`, read
2026-09-17. This file is an operating-doctrine document and therefore falls
under charter §4's prohibition unless its exact words are the object of a
question. It is offered ONLY for Q2, which asks whether a fourth same-shape
round may be licensed, and specifically for the "prior-record test" sentence,
because the four rounds' partition into "the same signature" is the very thing
Q2 turns on. Non-narrative primary evidence for that test does not exist: the
charter states the two-round rule (§9) but not the test for whether a partition
counts, and no contract or code encodes it. If the judge holds that this
excerpt's completeness or neutrality cannot be verified, charter §4 directs a
REFUSE of Q2 on that ground; the charter §9 rule stands independently either
way. Three bounded excerpts, each with enough surrounding context to be checked
for selective quotation.

Lines 97-112 — the C-028 delta-re-audit amendment, from its heading:

```
    97	## C-028 arc amendments (2026-07-11; empirically validated over ~16 refuters)
    98	
    99	- **Delta re-audit after EVERY fix round.** Twice this arc a fix round
   100	  introduced fresh defects (p2041: symlink crash; p2037: unit-mismatch +
   101	  strata crash in newly-reachable paths). A bounded re-audit of only the
   102	  fix delta caught both. Fix rounds are first drafts, not closers.
   103	- **Blocker refuter pairs get DISTINCT lenses (contract-authority vs
   104	  reachability/execution), not two identical skeptics.** Split verdicts
   105	  are the system working: B1 (p2041) and F1 (p2037) both split
   106	  confirmed-vs-refuted, and the lead's synthesis (narrowed rulings) was
   107	  better than either verdict alone. Never resolve a split by majority —
   108	  synthesize from both evidence chains.
   109	- **Arc verdict distribution** (~16 refuters): ~70% confirmed, ~15%
   110	  narrowed, ~15% refuted. The narrowings carried the most value
   111	  (prevented over-fixing); the refutations killed convergent two-lens
   112	  findings via one empirical corpus check. Refuters that EXECUTE
```

Lines 189-200 — "Read the whole delta, not its verdict word":

```
   189	## Read the whole delta, not its verdict word (2026-08-07, twice in one session)
   190	
   191	A delta re-audit's headline and its qualifiers are the same document, and
   192	the qualifiers are where the residue lives. Two failures the same day:
   193	
   194	1. A delta returned CLEAN on an authentication fix; a later cross-model
   195	   counter-review found the class alive one level down. The earlier delta
   196	   had NAMED the gap and the CLEAN verdict was accepted anyway.
   197	2. A delta reported two defect classes dead PLUS three fixes as PARTIAL.
   198	   The lead acted on the headline, opened the PR, and no ruling was ever
   199	   recorded on the PARTIALs — so "closed" entered the record when the
   200	   honest status was "closed as implemented, not as specified."
```

Lines 224-235 — the attack-shaped-regression and prior-record-test bullets, ending
at the next heading:

```
   224	  adjudicator's own ruling (schema-impossible hop) before the paired refuter
   225	  caught it.
   226	- Fix-round regression lists must be ATTACK-shaped, not only honest-path and
   227	  null-path: the round-2 list had no complete-but-foreign-inputs attack and
   228	  the delta found the hole in one probe. "Defect-shaped regressions" reads as
   229	  attack-shaped.
   230	- Failure-class partitions (deciding whether round N is "the same signature"
   231	  as round N-1) require the PRIOR-RECORD test: the partition must already be
   232	  drawn in the record BEFORE the failure it explains (contemporaneous, not
   233	  post-hoc). Mechanism-level re-partition without that test renders the
   234	  standing escalation trigger unfireable — the trigger-eating hazard.
   235	
   236	## Verify a "mutation-verified" claim the expensive way
```
