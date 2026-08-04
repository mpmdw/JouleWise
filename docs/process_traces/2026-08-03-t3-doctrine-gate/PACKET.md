# Rule-11 gate packet — T3 Code control-plane doctrine ratification

Status: FROZEN 2026-08-03 ~22:45 PT (Ed's bootstrap declaration
received; exhibit manifest stamped below). Any byte change after this
freeze = new candidate, new gate. Revised earlier tonight per the
charter design consult (record: `inputs/charter-consult-record.md`);
the first draft's admission of a whole narrative RUN_STATE block as
unscoped "custody input" was itself a consult-confirmed laundering
defect and is corrected below. Assembled by the lead MECHANICALLY;
lead views confined to labeled sections. Tracked per D-111 from birth.

## Exhibit manifest (sha256, stamped at freeze)

```
a2a087a470e879022cc1beae7cf8dc5fb84bb0cf25e453e0af7bcb755e460e6f  inputs/charter-consult-record.md
756bc8515b3086869073a5380475107af39fcca35ba64db80faef03af41b8a11  inputs/final-message-1f59-7ec.md
3ed20243c4c39016e70a458834b2f30ac5bc07ef5eff7bd80240bd0144c7bde0  inputs/final-message-2511-742.md
d303eaf2d9559ee38164b266a06b941d12ef8c87e43395c2466e825d563e9241  inputs/final-message-710c-75d.md
77dcf6c0efa1c1c5b89fda86246eb3b0027ae710db0f196a61efb032f9f32914  inputs/rollout-pins.txt
2d1f6fb6ab81eab0913fa38958eb46429e41f024c35eb319ec6732ed4ab75ccd  inputs/runstate-t3-block.md
```

## 1. Trigger (mandatory)

Rule-11 trigger #4: "any proposed process rule." Proposed: the rule-11
amendment adopting T3 Code as standing control plane (operating orders
1-5), Ed rulings R1-R3 (interim since 2026-08-03, ratification
explicitly deferred to this packet), and the standing cold-gate
charter. This packet's judging in a fresh t3 thread doubles as the
cold-packet-handoff acceptance gate, under the tightened criterion in
§5.

## 2. Questions presented (atomic; verdict per sub-question)

**Q1 — Operating orders** (each ratified separately as rule-11 text):
- 1a. t3 "Full access" mode PROHIBITED for this repo (maps to
  permission-bypass flags; Supervised/Auto only).
- 1b. No pattern-kills; kill only manifest-recorded PIDs verified by
  start-time + ancestry.
- 1c. t3 checkpoint-revert forbidden in the main tree; in a worktree it
  is a workspace mutation (stop writers, capture manifest/diff, record,
  re-baseline); a t3 checkpoint ref is never audit evidence; a t3
  checkmark is never an envelope.
- 1d. t3-native Codex threads are Ed-direct only; never targets for
  lead-delegated or gate-bearing work; material consumption of
  native-thread output requires a lead-authored ingestion note.
- 1e. Substantial background Sol rounds route through the tracked
  codex subagent (lifecycle visibility only; envelope/manifest ceremony
  unchanged underneath).

**Q2 — R1 cadence:** fresh-eyes sweep cadence is WORK-CHUNK-ANCHORED
(post-consumption of substantial rounds / merge waves / adjudications)
with a mechanical materially-consumed-invocation backstop counter.
Sub-question 2b: does this shape, if ratified, unblock D080-TRIGGER-01
(queue A52) as drawn?

**Q3 — R2 cold-gate mechanism** (split per consult Q6.4):
- 3a. Charter-suppression: a standing tracked charter replaces
  operating-doctrine ingestion for cold instances.
- 3b. Validation: external registry trust anchor
  (`docs/process/coldgate_charter_registry.md`) + launch-time expected
  digest independent of the packet + judge-side recompute, fail-closed
  (REFUSE ALL on mismatch); minimal validator per the registry spec.
- 3c. Composition: cold Fable judge + Sol contract-lens refuter, same
  frozen packet and same atomic questions, both outputs sealed
  (verbatim + hash-pinned) before synthesis; refuter charge =
  falsification of packet claims / lead disposition / contract
  application; override only by separately labeled written document
  citing both sealed outputs, presented to Ed.
- 3d. Ratify the charter TEXT at the §6-pinned digest.
- 3e. Effort-cap composition rule: when a standing Ed effort directive
  (e.g., "Sol high only") conflicts with a ruled gate composition's
  stated tier (e.g., R2's "Sol xhigh refuter"), which governs, and what
  must be recorded?

**Q4 — R3 compressed cutover:** ratify the compressed shadow cutover
(six acceptance gates during real work; rollback = pre-t3 mechanism per
route; TUI operation remains available), noting Sol's recorded dissent
(full-shadow preference) and the gate evidence in §5.

**Q5 — Provenance fold-in:** approve folding the rollout
`session_meta.originator` field (`t3code_desktop` vs wrapper values)
into the bridge-protocol §4/§6 amendment as the mechanical
native-vs-wrapper session discriminator.

## 3. Authority chain (checkable)

- Ed directive (TIER 1, 2026-08-03): T3 Code is the standing control
  plane — PRESENTATION/CONTROL plane only, never the compliance plane;
  envelopes, leases, manifests, WRITE_SCOPE, and every gauntlet layer
  unchanged and authoritative.
- Ed rulings R1-R3, given 2026-08-03 late night, interim-effective,
  with ratification deferred to this packet. Exact ruling text: exhibit
  E1.

## 4. Exhibits (scoped per charter §4)

**E1 — `inputs/runstate-t3-block.md`** — verbatim excerpt of the
RUN_STATE.md T3-CUTOVER checkpoint block at revision `e3612f5`.
Source: RUN_STATE.md (a narrative state document — forbidden class).
Admissibility: the operating-orders text, the R1-R3 ruling text, and
the gate/probe log lines are THEMSELVES the objects of Q1-Q4 (proposed
rule text being ratified; recorded gate evidence); no other canonical
home for the proposed text exists yet — that absence is part of what
this gate cures. LIMITATION: the night-plan paragraphs and any
narrative/urgency language in the block are contiguous context ONLY —
not authority, rationale, severity, or disposition evidence for any
question.
- E2 — `inputs/final-message-2511-742.md` — Sol design-consult final
  message, thread 019fcac1 (recaps + adopts the conclusions of thread
  019fca7c, lost to MCP recycle). Object: the design record behind
  R2/R3 (Q3, Q4).
- E3 — `inputs/final-message-1f59-7ec.md` — Sol night-plan review final
  message, thread 019fcafc. Object: Sol's recorded R3 dissent basis
  (Q4).
- E4 — `inputs/final-message-710c-75d.md` — native t3 thread final
  message, thread 019fcb0b. Object: native-discussion gate evidence
  (Q4) and originator-field provenance (Q5).
- E5 — `inputs/rollout-pins.txt` — sha256 pins of the three full
  transcripts (persist in ~/.codex/sessions; loss-insurance copies in
  .desk/t3-doctrine-gate/).
- E6 — `inputs/charter-consult-record.md` — the charter design-consult
  record incl. Sol's recorded disagreements and the lead's inline
  adjudications (Q3a-3d).
- E7 — commit `97d6e3d` (repo history) — isolated-native-write gate
  exercise (Q4).
- E8 — rollout
  `rollout-2026-08-03T21-32-32-019fcb0b-710c-75d2-8aaf-adb69680ea7d.jsonl`,
  `session_meta` field `originator: "t3code_desktop"` (verified live
  from the rollout file by the assembling session; cwd
  /Users/edr/code/JouleWise, cli 0.146.0) (Q5).
- E9 — commit `14c9f05` (Ed-authored RUN_STATE refinement, timed
  discriminator probe): in Auto mode the phone cards are POST-HOC
  NOTIFICATIONS, NOT GATES — execution never blocks on them
  (22:04:04→22:04:04, Ed instructed not to respond, file created in
  0 s); a tapped card ≠ an approval; the prior session's "permission
  prompts functioning" inference is corrected (its clicks were
  acknowledgments); notification cards are visually indistinguishable
  from approval prompts (legibility hazard, upstream-issue candidate);
  capability-profile matrix (mode × provider × blocking-semantics) to
  be filled (Q1a, Q4).
- E10 — Supervised-cell probe record (2026-08-03 ~22:26-22:28, fresh
  Fable thread, t3 mode "approve actions"): probe file
  `~/t3-supervised-probe.txt` mtime AND content `22:27:34` (verified
  by the assembling session via stat on the same machine), send time
  ~22:26±45s (Ed), first tap reported 22:27:45 (Ed), second approval
  card observably held the read-only `stat` readback until tapped.
  BONUS FINDING: the thread's own report claimed "ran without any
  permission prompt... went through immediately" — the model is BLIND
  to the approval layer (harness holds the tool call invisibly), so
  thread-side reports are inadmissible as evidence about approval
  semantics; operator observation + filesystem timestamps only
  (Q1a, Q4).

## 5. Acceptance-gate evidence (facts; Q4)

- isolated-native-write ✅ — E7.
- native-discussion ✅ — E4/E8; ingestion note = the E1 gate-log entry.
- phone-approval ✅ CLEARED (2026-08-03 ~22:27, E10) with the E9 Auto
  caveat: in t3 "Auto" mode the permission classifier SELF-APPROVED a
  sandbox-disabled home-dir write with no prompt relayed (E1 gate
  log), and Ed's timed discriminator probe established Auto-mode phone
  cards are post-hoc notifications, not gates (E9). The Supervised
  ("approve actions") cell then PASSED its timed probe (E10): a
  home-dir write sent ~22:26 executed at 22:27:34, at Ed's tap
  (reported ~22:27:45, within reporting noise), with a second pending
  card observably holding the readback command until its own tap.
  Doctrine split confirmed: Supervised gates and relays to the phone;
  Auto notifies post-hoc; anything requiring Ed's eyes uses a
  Supervised thread.
- checkpoint-restore: OPEN (scratch-repo probe not yet run).
- app-death recovery: OPEN (next real t3 quit/relaunch vs predeclared
  criteria).
- cold-packet-handoff: OPEN — clears per the consult-tightened
  criterion: preflight digest validation succeeds AND both instrument
  outputs are sealed AND the fresh-t3-thread judge returns non-REFUSE
  on the mechanism (Q3) and on these exact packet bytes. A REFUSE or
  protocol failure does NOT clear the gate.
- Probes (E1 gate log): CODEX_HOME default; CLAUDE.local.md absent in
  all worktrees (doctrine provably main-checkout-only); git common-dir
  writable from worktrees; t3 server single origin 127.0.0.1:3773 but
  bound 0.0.0.0 (LAN-exposed, ticket-auth'd; Ed to check the
  Network-access toggle).

## 6. Charter pin

Charter under ratification (Q3d): `docs/process/coldgate_charter.md`
v2, sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.
Trust anchor: `docs/process/coldgate_charter_registry.md` at the
freeze revision; the launch-time expected digest is supplied to the
judge from the registry, independently of this packet.

## 7. Bootstrap declaration (received; recorded verbatim)

Ed, 2026-08-03 ~22:44 PT, in-session, verbatim:

> Bootstrap declaration: I authorize charter digest
> 099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81
> solely as the procedural candidate for judging the t3-doctrine
> packet. Not ratification evidence.

Per the consult's self-referential-first-packet rule: this
authorization is not ratification evidence; any post-ruling byte
change = new candidate, new gate.

## 8. Recorded dissent and open tensions (must reach the judge)

- Sol R3 dissent: full-shadow preference over compressed cutover (E3);
  adopted position was Ed's R3.
- Sol charter-consult disagreements preserved in E6 (v1 suppression
  inadequacy; anti-lead framing; unstructured synthesis; packet-local
  hash insufficiency) — v2 adopted the corrections; the judge rules on
  v2 (Q3d).
- Ed effort directive (2026-08-03 evening): Sol HIGH only — in tension
  with R2's "xhigh refuter" spelling; Q3e presents the composition
  rule.

## 9. What the gate must return

Per-question verdicts AFFIRM / REJECT / REFUSE for Q1a-e, Q2 (+2b),
Q3a-e, Q4, Q5, with findings tiered BLOCKER / MATERIAL / NIT; any
charter text amendments by section (a REJECT on Q3d should name the
minimum cure); conditions on the three open acceptance gates; and the
Q3e composition rule stated as ratifiable text.

## Lead's disposition (labeled; the gate is free to reject it)

The lead proposes AFFIRM on all questions as presented, with Q3e
resolved as: Ed's standing effort directives govern over ruled
composition tiers; the deviation is recorded in the synthesis with the
judge's tier reasoning preserved, and a failed round under the capped
tier is the datum that justifies a one-off escalation request to Ed.
Basis: tonight's live evidence — two Sol-high gate instruments (B1
refuter, charter consult) both delivered blocker-grade unique catches
with no observed quality decline.
