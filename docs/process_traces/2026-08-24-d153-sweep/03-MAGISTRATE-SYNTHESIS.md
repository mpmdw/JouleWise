# Magistrate synthesis — D-153 fixation-family / confirmation-supply sweep

Magistrate: Fable 5, T23 session, 2026-08-24 evening.
Trigger: the standing escalation trigger (CLAUDE.local rule 11) fired on the
second same-signature defect. Instances, in discovery order, all found by
LIVE EXECUTION of estate 6 or by this consult:

1. **S0-O3** — §3.8 consumed transcript `074-*`, produced only in §4.10
   (cured, refuted SOUND, merged as PR #186).
2. **F1/118** — §4(e)'s byte-pin probe greps a test method that exists only
   after fixation, under a name the fixation delta does not define.
3. **Estate-6 §3.9 arm refusals** — all three arms REFUSE with "no expected
   confirmation digest supplied": the runsheet never passes `hC` to any live
   consumer.

Seats: `01-opus-contract-lens-seat.md` (Opus, epoch-timeline lens, findings
F0–F15) and `02-sol-semantic-seat.md` (Sol gpt-5.6-sol xhigh via audited
bridge, findings 1–62 + consolidated cure list), both anchored at 7d586a69.
Cross-model per the model-diversity directive; the seats were independent and
their overlap is near-total, which is itself evidence the haul is real.

## Shared root cause (both seats, one sentence)

The runsheet's consumers were written against interfaces and orderings that
D-153 and the step-6 contract later moved out from under them — and the
runsheet had no assertion class capable of noticing (same refusal code for
different causes; line-number citations audited only for non-emptiness;
symbol-existence never checked against the executing head).

## Rulings

**R-1 — The consolidated cure list is ADOPTED**: Sol's fifteen items
(02-sol §"Revised consolidated one-PR cure list"), amended by the
Opus-only findings:

- item 16: **F13** — remap the `tests/test_receipt_histsem.py` citations to
  post-W1 coordinates (`160,166p;220,238p` in §1.3), fix the three prose
  citations, and add that file to the `s0_anchor_map.py` AST anchor map;
- item 17: **F14** — rename `084-*` to `084-marker-forged-ref-classification.txt`
  and repoint §5;
- item 18: **F0 record correction** — R4-O1's cause attribution is REOPENED:
  the recorded diagnosis ("test file outside the ruled 112") is unproven
  because the conditional-path raise precedes the ordinary-path raise and both
  carry the same code. The detail-shape assertions (Sol cure 5, extended per
  Opus F0: "digest-conditional allowlist path" must be ABSENT from
  101/104/105/110-*/119/121 and PRESENT in 123) make attribution mechanical
  in the next estate; the R4-O1 record gains an erratum note, not a rewrite;
- item 9 amendment: **F2 case design** — the post-fixation `118-*` tamper must
  be the SHAPE-PRESERVING canonical re-mint (identical pack_count /
  receipt_count / pack_ids, canonical bytes, different `plan_sha256`): a naive
  byte tamper is already caught pre-fixation by canonicality, so only the
  re-mint case isolates hS as the discriminator;
- item 19: **F11** — §3.10's published-green half names the WRONG head: under
  A1+A3 the published head is the window-close head (green without the byte
  pin) and fixation is the first commit after it; binding publication
  acceptance to "the accepted fixation head" recreates the collision A6
  broke. (Divergence resolved: Sol #16 judged only the temporal deferral,
  which is fine; Opus F11 judged the head identity, which is wrong as
  written. Both observations stand.)

**R-2 — hC supply shape (the one true split verdict, synthesized).**
Sol: operator re-pastes `hC` per block, never recovered from `085-*`.
Opus: read `085-*` (it is transaction custody per the contract's own
definition) plus one §3.9 re-paste.
RULING: **Sol's shape, with Opus's witness.** Every post-mint enforcing block
carries the operator-pasted `ED_STEP6_CONFIRMED_SHA256`, validated as
lowercase-64-hex, and additionally asserts equality against `085-*` — as a
CROSS-CHECK, never a source. Rationale: the contract's image is "supplied by
the operator to every consumer through its explicit input"; the rehearsal
should rehearse exactly that, and the re-paste's failure mode is a loud
refusal (cheap), while a custody-file read's failure mode is silent norm
drift toward in-band supply. The 085 equality check converts transcription
typos into immediate, well-named failures, which answers Opus's
transcription-risk objection. Opus's recommendation is recorded as dissent.

**R-3 — Estate 6 is STRUCK.** Not discretionary: the runsheet's own failure
semantics (lines 3216–3245 at 7d586a69) classify a missing consumer argument
as an instrument failure ("cured on main, re-ratified, and S-0 restarts from
§1.1"), and the `record_env` duplicates independently supersede the estate.
Estate-6 custody is preserved READ-ONLY; its `091-*` REFUSE transcripts are
retained as live negative-leg evidence (the C→S gate demonstrably refuses
without hC), and its instrument-correction notes stand. Estate 7 is cut only
after the cure PRs land AND re-ratification is recorded.

**R-4 — Two implementation streams, C-028 gauntlet each:**
- **Code stream** (own PR, own WRITE_SCOPE): `freeze` gains
  `--step6-confirmation-table` (Path), forwarded to `generate_freeze_receipt`;
  tests for valid pair / missing path / missing hC / malformed hC /
  mismatched bytes. The consume-side supply line (Opus 3f) is registered as a
  kernel row, NOT fixed here.
- **Runsheet stream** (own PR): cure items 2–19 on the runsheet, r4→r5
  revision-history entry naming this sweep as authority.
Each stream gets a cross-model refuter (runsheet stream: Sol xhigh; code
stream: Opus or Fable contract lens — the implementer being Sol), then a
joint delta re-audit of both final heads together, then merge. That joint
PASS plus this ruling constitutes the RE-RATIFICATION the failure semantics
require.

**R-5 — Epoch-lint work order (kernel row).** Opus's generalization is
adopted as a work order: a mechanical lint for the three dependency kinds the
producer/consumer sweep cannot see — (i) symbol existence at the executing
head, (ii) contract-required CLI inputs at every invocation, (iii) file line
coordinates. Runs at every future runsheet revision. Registered in the state
kernel; not blocking the cure PRs.

**R-6 — Scorekeeping (rule 2).** Opus-only catches: F0, F11, F13, F14, F2's
case design. Sol-only catches: the freeze-CLI interface gap as BROKEN-interface
(48), the zero-class-(a) headline, estate-6 disposition from the runsheet's
own text, the published-replay spec gap (59), the `record_env` triple-duplicate
(61). Both: everything else. Cross-model diversity earned its cost on this
packet; neither seat alone would have produced the full cure list.
