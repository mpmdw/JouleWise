# Blind Fable seat — consult on F-N4 (fourth consecutive prose signature)

Packet head: `fbedfb04` (packet file 38). Seat model: Claude Fable 5.1
(`claude-fable-5-1`), fresh session, no loop context. Lens: pedagogy and
process. Read-only; `git status --short` empty after every command.

Worktree state when read: `/Users/edr/code/JouleWise-wt-decode-id`, branch
`fix/2026-09-02-decode-identity-set`, HEAD `2f3592c5`; `fbedfb04` is an
ancestor and `git diff --stat fbedfb04..HEAD` touches only trace files 37–40,
so the contract paragraph under review is byte-identical to the packet's.
Blindness kept: files 39/40 not opened. One incidental exposure: a
`grep -rn` across `docs/` matched one line of file 40, which was a verbatim
copy of contract line 672 (already in my evidence); no reasoning from any
other seat was read.

---

## 0. Two findings that change the questions

Before answering §3 in order, two things I executed alter the packet's
premises. I state them first because the rest depends on them.

**Finding X1 — the paragraph has an undetected FACTUAL defect (S1 class).**
The paragraph says every arming-time path that no longer exists is refused
with "`launch_binding_mismatch`, or `launch_consumption_missing` when the
consumption receipt itself is gone". I executed the missing-file hop for
three of the five named resolves and code-read the other two:

| Named resolve | File gone → reason code | How verified |
| --- | --- | --- |
| consumption receipt | `launch_consumption_missing` | EXECUTED (`_read_v2_consumption`) |
| pack root | `launch_binding_mismatch` | code-read `:9333–9352`; terra 267 executed |
| launch manifest | **`launch_consumption_invalid`** | EXECUTED (`_read_exact_launch_reference`, `:8996–9013`) |
| window root | `launch_binding_mismatch` | code-read `:10199–10205` |
| lifecycle receipts | **`launch_lifecycle_incomplete`** | EXECUTED (`_read_lifecycle_receipt`, `:9794–9798`) |

Two of five are wrong. Terra's B2 table (file 37) executed exactly the two
hops that agree with the paragraph and "proved" the manifest and lifecycle
rows by citing that a resolve *exists* at those lines, not by executing what
it emits. The packet's §4 premise ("the paragraph's CONTENT was proven by
terra") is therefore false, and packet §2's "the corrective … fixed the
FACTUAL class" is false for this paragraph. I am not re-litigating ruling
(d) — the limitation it states (the lineage layer is absolute; a relocated
bundle never reaches the gate) is true and I confirm it; the *labels* the
paragraph attaches are what is wrong. Severity: should-fix at minimum — a
contract clause that names the wrong refusal label is exactly the kind of
sentence a future test would be written against.

**Finding X2 — both candidate cures introduce new factual errors.** Cure A
says bundle loading resolves "EVERY path recorded at arming time — the pack
root among them". Only the pack root is recorded at arming time
(`_pack_record` `:5253` → `arm["pack"]["pack_root"]`, read at `:9333`). The
consumption-receipt path is recorded in the bundle's lineage stamp
(`:10127–10130`), the manifest path in the consumption receipt
(`consumption["launch_manifest"]`, `:10186`), the window root in the manifest
(`manifest["window_plan_root"]`, `:10200`), and the lifecycle paths in the
stamp (`value["start"]`, `:10233`). Cure B glosses the window root as "the
directory the window's evidence is written under"; it is the frozen window
*plan* directory holding `window.env`, the stage lists, `extraction_spec.json`,
`waivers.json` and `window-chain.zsh`, created "outside the runs roots"
(`docs/phase_2/window_runbook.md:166–176, 238–241`; code expects
`window.env` and `window-chain.zsh` under it, `:10206–10219`). Both cures
would land the S1 class again under the banner of fixing the pedagogy class.

---

## Q1 — classification (honest reading of rule 11)

Rule 11 has two separate triggers with different words:

1. *Mandatory cold-gate triggers:* "any second fix round on the same
   defect; any reversal or reinterpretation of a stop signal or verdict; any
   irreversible action; **any proposed process rule**; any turn ending in a
   'waiting' state on a scarce open resource."
2. *Standing escalation trigger:* "two consecutive rounds failing with the
   SAME SIGNATURE — same defect class, another missed call site, another
   failed formulation — is evidence of a structural problem, and the next
   spend is a CONSULT, not round three."

The rule itself distinguishes "same defect" (trigger 1) from "same defect
class" (trigger 2), so I read "same defect" as *the same finding being fixed
again*. F-N/F2/S1 were all about the freeze-procedure text (§6 steps 1/3 and
the paragraph at ~481–501); F-N4 is in a different paragraph (§Analysis
consumption, 609–621), dictated for a different ruling (S3). Under that
reading F-N4 is **not** "a second fix round on the same defect".

**Answer: (c).** A distinct defect of the same class — but the packet's
option (b) ("this consult suffices, then one changed-formulation round")
is not the honest consequence, for three reasons:

- **The escalation ladder is exhausted, not re-entered.** Trigger 2 already
  fired after round 2; round 3 *was* the consult (files 29–32); the
  consult-prescribed formulation then failed on the same class. The rule
  provides no "consult again, then one more round" rung. Its rationale is
  that same-signature repetition is "evidence of a structural problem"; a
  repetition *after* the consult is evidence the structural problem was
  misdiagnosed (the round-3 corrective aimed at the factual class only —
  packet §2 admits this). A fourth formulation of the *text* alone would be
  round five of the same experiment.
- **The cure is a process rule, so the cold gate is reached anyway.** Any
  fix that "breaks the pattern" (Q3/Q4) changes who runs the first-use table
  and when. That is "any proposed process rule" — trigger 1, enumerated. The
  packet concedes this in Q4. So the practical answer to "cold gate or not"
  is *yes*, by a different clause than (a).
- **X1 makes the dictation mechanism itself two-for-two on the factual
  class.** The magistrate-dictated text was factually wrong in the round-3
  consult packet (S1, caught by Sol 265 + blind Fable) and is factually wrong
  again in the round-3 landing (X1, uncaught). Same author, same
  formulation, same signature, two consecutive rounds. Trigger 2 fires for
  the *dictation pattern*, independently of F-N4. The party proposing to
  continue is the author of both erroneous texts; rule 11's stated reason
  for the cold seat — "stopping is what the loop-immersed agent demonstrably
  cannot judge from inside" — applies squarely.

What this means operationally: this consult is the mandated spend for F-N4;
the *landing* of the round-4 paragraph plus the process change goes to the
cold gate with an Opus contract-lens refuter; and the round-4 text should
not be magistrate-dictated prose verified by citation — it should be
verified by execution (see Q3) by a seat that did not write it. I do not
lower F-N4's severity; with X1 the paragraph's severity is higher than the
packet states, not lower.

---

## Q2 — grading the cures; a third cure

First-use test, applied mechanically: each term of art is (a) built before
use, (b) glossed at first use, or (c) deleted; anything else FAILS. Line
numbers are the current contract (`docs/contracts/identity_pin_projection.md`,
1042 lines). Definitions were located by pattern (`**term**`, "(the term)",
"term (", "term —", "term, meaning", "term is/means") with the script in
§Executed evidence, then hand-checked.

### 2.0 The paragraph as landed (baseline)

| Term (first use line) | Status | Where defined |
| --- | --- | --- |
| consumption receipt (612) | FAIL | nowhere; 672 defines **one-use consumption record** — same object, different name |
| launch manifest (612) | FAIL | 671 (bold), +59 lines after use |
| window root (612) | FAIL | nowhere in any contract |
| lifecycle receipts (613) | FAIL | nowhere in any contract |
| `launch_binding_mismatch` (614) | FAIL | no contract; only `arm_readiness.py` |
| `launch_consumption_missing` (615) | FAIL | no contract; only `arm_readiness.py` |
| evidence row (610) | FAIL — **missed by the packet** | nowhere; 636/647 are further uses |
| machine-absolute (609) | FAIL — missed by the packet | nowhere; "absolute path on the machine that armed it" is the plain gloss |
| arming-time paths (613) | FAIL — missed, and factually loose (X2) | "Arm" defined 148; "arming-time path" recorded only for the pack root |
| consumed arm (611; inherited from 585) | FAIL — missed | "consume" is never built; 148 says arm "is not the later process launch" but never says what consuming an arm is |
| successor-lineage (616; "successor packs" 598) | FAIL — missed; collides with **committed successor** (533), a different meaning | nowhere |
| design lane (618) | FAIL — missed (process jargon in a reader-facing contract) | nowhere |
| launch lineage (610) | pass | 584 (bold) |
| pack root (611) | pass for this paragraph | glossed 492 "(the pack root)" — but first used at 464, i.e. the R3-B text has its own first-use defect, missed by both seat tables |
| `consumer_identity_set_unauthenticated` (620) | pass (b) | glossed in the same sentence: "the same label as any pack it cannot authenticate"; fully built 634–659 |
| input loading (614) | pass (b) | glossed in-sentence by the parenthetical |

Packet §1 lists six failing terms; the mechanical run finds twelve. The
under-count matters for Q3: a hand-built table by a reader who already knows
the vocabulary is exactly how "evidence row" and "consumed arm" stay
invisible.

### 2.1 Cure A — delete the upstream vocabulary

Text: "…it replays the consumed arm and resolves EVERY path recorded at
arming time — the pack root among them — strictly, so a bundle whose
arming-time paths no longer exist is refused at input loading with a
launch-lineage reason code and never reaches this gate (…cites…)."

| Term | Status | Note |
| --- | --- | --- |
| consumption receipt, launch manifest, window root, lifecycle receipts | (c) deleted | pass |
| `launch_binding_mismatch`, `launch_consumption_missing` | (c) deleted | pass; and given X1 their deletion also removes a false claim |
| "every path recorded at arming time" | FAIL — new factual error (X2) | four of five paths are not recorded at arming time |
| "launch-lineage reason code" | (b) borderline | family named (`LAUNCH_LINEAGE_REASON_CODES`, `:222–232`) but not built; reader cannot say which codes |
| consumed arm | FAIL (inherited) | still not built |
| evidence row, machine-absolute, design lane, successor-lineage | FAIL (unchanged sentences kept) | Cure A only rewrites one sentence |
| replication bar | FAIL | a reader cannot rebuild the mechanism: which files, in what order, what refuses. "resolves every path" is the gist, not the mechanism |

Verdict: **do not land.** It passes the first-use test only by deleting the
mechanism, fails replication, and introduces an S1-class error while doing
so.

### 2.2 Cure B — gloss at first use

| Gloss | First-use status | Factual status |
| --- | --- | --- |
| consumption receipt — "the durable one-use record that this launch authorization was spent" | (b) pass | PROVEN (`validate_consumption_receipt`, `:8967`; `CONSUMPTION_RECEIPT_SCHEMA`, `:8972`); but leaves two names for one object (672 says "one-use consumption record") — the reader now has to notice they are the same |
| launch manifest — "the JSON declaration of the reviewed command and its inputs, defined in §What happens after arm" | (b) pass | PROVEN (`validate_launch_manifest` `:10192`; `manifest["launch_command"]` `:10221`); the forward pointer is fine because the gloss itself is complete |
| window root — "the directory the window's evidence is written under" | (b) in form | **FALSE (X2)** — it is the frozen window plan directory, created outside the runs roots |
| lifecycle receipts — "the per-stage records written as the window runs" | (b) weak | roughly true (`launch_start`/`launch_settle`/`launch_completion`, `:10236/:10245`) but "per-stage" is not built; the reader cannot name the stages |
| codes — "emitted when the replayed lineage does not resolve / when the consumption receipt itself is gone" | (b) in form | **inherits X1**: a gone manifest is `launch_consumption_invalid`, a gone lifecycle receipt is `launch_lifecycle_incomplete` |
| evidence row, machine-absolute, arming-time, consumed arm, design lane, successor-lineage | FAIL | not addressed |
| replication bar | partial | order of resolves still implicit ("as it resolves …") |

Verdict: **do not land as written.** The packet's own warning ("every gloss
is a new factual claim that must be PROVEN") is borne out: one gloss is
false and one inherits the paragraph's existing false claim. The packet's
other cost ("this contract then defines terms it does not own") is not a
real cost: the contract already defines **launch lineage** (584) which it
does not own either; there is no launch-lineage contract in
`docs/contracts/` (`ls` shows none) for these terms to live in, which is
the actual gap — see Cure C(i).

### 2.3 Cure C — build the vocabulary once, then say the mechanism in order with the true labels

Two edits. (i) puts the four nouns where the contract already keeps its
lineage vocabulary (the bullet block at 584–593), so the paragraph and any
future lineage paragraph use *defined* terms — first-use option (a), built
before use. (ii) rewrites the paragraph so it states the five resolves in
execution order with the label each actually emits, and deletes the
undefined process words.

**(i) Add to the vocabulary block after the **Launch lineage** bullet (584–585):**

> - The **consumption receipt** is the one-use record written beside the arm
>   receipt (`arm_readiness.consumptions/<arm receipt id>.consumed.json`)
>   when the arm is spent by a launch; it names the launch manifest and the
>   exact command. §What happens after arm calls the same file the one-use
>   consumption record.
> - The **launch manifest** is the JSON declaration of the reviewed command
>   and its inputs; the consumption receipt records its absolute path and
>   digest.
> - The **window plan root** is the absolute directory the launch manifest
>   names as holding the frozen window plan (`window.env`,
>   `window-chain.zsh`); it is created outside the runs roots.
> - The **lifecycle receipts** are the `start`, `settle` and (when present)
>   `completion` records written as the launched window runs, each chained to
>   its predecessor and to the consumption receipt.
> - **Consuming** an arm means spending its one launch authorization: the
>   launcher writes the consumption receipt and the arm cannot authorize a
>   second launch.

**(ii) Replace 609–621 with:**

> That root is the absolute path of the pack directory on the machine that
> armed it, copied into the arm receipt when the arm was issued. Before a
> bundle is admitted as analysis input, bundle loading authenticates its
> launch lineage by reading five recorded files by their absolute paths, in
> this order, and refuses at input loading — so the bundle never reaches this
> gate — if any is gone: the consumption receipt
> (`launch_consumption_missing`); the pack root recorded in the arm receipt,
> resolved strictly (`launch_binding_mismatch`); the launch manifest at the
> path the consumption receipt recorded (`launch_consumption_invalid`); the
> window plan root the manifest names (`launch_binding_mismatch`); and the
> start and settle lifecycle receipts (`launch_lifecycle_incomplete`).
> Analysis of such bundles therefore runs on the filesystem that armed them;
> making the lineage relocatable would be a separate design decision, not a
> property of this gate. Called directly with a lineage whose pack root does
> not resolve, the gate refuses with `consumer_identity_set_unauthenticated`,
> the same label as any pack it cannot authenticate.

Cure C first-use table (paragraph (ii), assuming (i) landed):

| Term | Status | Where |
| --- | --- | --- |
| pack directory / pack root | (a) | **campaign pack** 34; "(the pack root)" 492 — precedes 609 |
| arm receipt, arm was issued | (a) | **Arm** 148 ("may issue a launchable receipt") |
| consumption receipt | (a) | new bullet in 584–593 block |
| launch manifest | (a) | new bullet; 671 bold kept as the later restatement |
| window plan root | (a) | new bullet (renamed from "window root" to match `window_plan_root` and the runbook's `WINDOW_PLAN_ROOT`) |
| lifecycle receipts / start / settle | (a) | new bullet names the three kinds |
| launch lineage | (a) | 584 |
| consuming / consumed | (a) | new bullet |
| `launch_consumption_missing`, `launch_binding_mismatch`, `launch_consumption_invalid`, `launch_lifecycle_incomplete` | (b) | each glossed by the clause it sits in: "if <file> is gone: `<code>`" |
| `consumer_identity_set_unauthenticated` | (b) | in-sentence, unchanged |
| input loading | (b) | "before a bundle is admitted as analysis input … refuses at input loading" |
| evidence row | (c) deleted | replaced by "admitted as analysis input" |
| machine-absolute | (c) deleted | built as "absolute path … on the machine that armed it" |
| arming-time paths | (c) deleted | replaced by "recorded files by their absolute paths" (true for all five) |
| successor-lineage bundles | (c) deleted | "such bundles" |
| design lane | (c) deleted | "separate design decision" |

Cure C factual proof table — every clause is a claim; execution status is
marked honestly:

| Clause | Proof | Status |
| --- | --- | --- |
| pack root is copied into the arm receipt at arm issuance | `_pack_record` `:5253` `"pack_root": str(pack_root.resolve())`; read back from `arm["pack"]["pack_root"]` `:9333` | code-read (arm-time call site not executed by me) |
| order: consumption → arm/pack root → manifest → window plan root → start/settle | `authenticate_launch_lineage` `:10127–10130` → `:10133–10140` → `:10186–10198` → `:10200` → `:10233–10252` | code-read; `_read_bundle` calls it at `inputs.py:2773` with `require_completion=False` (`:2777`) |
| consumption receipt gone → `launch_consumption_missing` | `_read_v2_consumption` `:8963–8966` | EXECUTED |
| pack root gone → `launch_binding_mismatch` | `:9333–9352` | code-read; terra executed |
| manifest gone → `launch_consumption_invalid` | `_read_exact_launch_reference` `:8996–9013` | EXECUTED |
| window plan root gone → `launch_binding_mismatch` | `:10199–10205` | code-read (6-line try/except) |
| start/settle gone → `launch_lifecycle_incomplete` | `_read_lifecycle_receipt` `:9794–9798`; refs `:10233`, `:10242` | EXECUTED |
| consumption receipt lives at `arm_readiness.consumptions/<arm id>.consumed.json` beside the arm receipt | `:8977–8983` (namespace check); `:9317` (arm path `parent.parent / arm_readiness.receipts/…`) | code-read |
| window plan root holds `window.env`, `window-chain.zsh`, is outside runs roots | `:10206–10219` expected paths; runbook `:166–176, 238–241` | code-read + doc |
| lifecycle kinds start/settle/completion, chained | `:10236`, `:10245`, `:10259`; predecessor checks `:10281–10297` | code-read |
| direct-call refusal label | unchanged clause, proven by terra B2 | inherited |

If the magistrate wants fewer factual claims in the contract, the honest
minimal variant of (ii) names the family instead of per-hop codes: "…is
refused at input loading with one of the `launch_*` launch-lineage reason
codes (registry: `LAUNCH_LINEAGE_REASON_CODES`, `joulewise/arm_readiness.py`)".
I prefer the per-hop version: the paragraph exists to state a limitation
precisely, and per-hop codes are what a seam test pins. Either way the
executing seat that verifies Cure C must EXECUTE all five hops and paste
the outputs, not cite the lines — that is the lesson of X1.

**Recommendation: land Cure C (i)+(ii), verified by execution by a seat
other than its author, through the cold gate (Q1).**

---

## Q3 — the fourth formulation

**Would the magistrate's mechanical table have caught F-N4?** Yes. I ran it
(script in §Executed evidence) on 609–621: all six packet terms FAIL, plus
six more the packet missed (§2.0). Two observations about the tool:

- It produces false positives that need a human line-reader: "arm" (first
  use 147, bold 148 in the same bullet), "receipt" (title line 1, bold 7).
  Two of 21 in my run. Acceptable, but it means "mechanical" = script output
  plus writer triage, not script output alone.
- It also caught a first-use defect in the *proven* R3-B text ("pack root"
  used 464, glossed 492) that both Sol 266's and terra 267's hand tables
  missed — Sol cited line 34 for "pack root", which does not contain the
  phrase. Hand tables by vocabulary-fluent readers are the failure mode the
  script exists to replace.

**Would it have caught S1 or X1?** No; both are factual. What would: for
every clause of the form "refuses with `<code>`", "before `<step>`", or
"in this order", the landing record must carry an EXECUTED probe — command
and pasted output — not a `file:line` citation. Evidence that this is the
discriminator: terra's two executed hops were right; terra's citation-only
rows were where X1 hid. This is the prose analogue of the repo's
mutation-cure counterfactual rule ("today's-artifact cures kill nothing"):
a cited line proves a resolve exists, not what it emits.

**Where the structural problem actually is** (the packet asks whether the
gate is the right response or the problem is elsewhere):

1. *The brief never asked for the table on this paragraph.* File 33 asks
   for a first-use table under R3-B only ("First-use table for the new text
   in your report") and under R3-C asks only for clause verification. Packet
   §1 attributes the omission to the seat ("Sol 266's first-use table
   omitted the paragraph entirely"); it was brief-shaped. The writer's duty
   under Ed's standard is "run mechanically before delivering" — the writer
   here was the magistrate, who did not run it, and the brief did not
   delegate it for R3-C.
2. *Dictation is the vector for undefined vocabulary.* The four nouns in the
   paragraph are, verbatim, the blind Fable seat's enumeration in file 31 as
   quoted in file 32's S3 table. The magistrate carried consult-seat
   shorthand into a reader-facing contract. Consult prose is written for
   people who already know the words; a contract is not.
3. *Verification by citation.* Clause tables that cite lines let the
   factual class through in both round-3 texts (S1 in the packet, X1 in the
   landing).

**The fourth formulation** (all three parts; any one alone repeats a known
failure):

- **Author ≠ magistrate for contract prose.** The magistrate specifies the
  *claims* (a claim list: what the paragraph must say, each with the
  proving hop); a seat writes the prose. The magistrate has been the author
  of both factually-wrong round-3 texts and is the party proposing to
  continue; rule 11's separation of author from adjudicator should apply to
  contract text as it does to verdicts.
- **Writer runs the first-use script and pastes the triaged table in the
  landing record BEFORE the verifying seat sees it**; the verifying seat
  re-runs the script (not re-derives by hand) and diffs.
- **Every code/order clause carries an executed probe** in the landing
  record; the verifying seat re-executes and pastes; citations are not
  acceptable for those clauses.

---

## Q4 — process rule for Ed (not for installation by any seat)

**Recommendation:** make the pre-landing first-use table mandatory for
edits under `docs/contracts/` (not trace files, not run reports), in the
script-plus-triage form, paired with the executed-probe rule for
code/order clauses. Both are proposed process rules → cold gate/Ed per rule
11; nothing here is installed by this seat.

**Cost per edit.** Script run: seconds. Writer triage: roughly 1 minute per
five terms (my run: 21 terms, two false positives, ~5 minutes including
reading the definition lines). Verifying seat: re-run plus diff, ~2 minutes.
The executed-probe rule costs one small Python probe per code/order clause
(mine: 15 lines for five hops) — 10–20 minutes for a paragraph like this
one; it is the expensive half and the one that catches the expensive class.
Against that: this section has consumed four rounds, two consults, and one
cold-gate-bound landing.

**Two-session drop test (rule 5), stated so it cannot be gamed:** count
*writer-side* catches — terms the writer's pre-landing run flagged and the
writer fixed before the verifying seat saw the text. If over two sessions
of contract-prose edits that count is zero AND no post-landing auditor
finds a first-use defect, drop the gate. If writer-side catches are zero
but auditors still find defects, the gate is being skipped, not failing —
that is a compliance finding, not a drop. Keep the executed-probe rule on a
separate counter (factual catches), since dropping one must not drop the
other.

---

## Anomalies in the packet (for the magistrate)

1. §4 "the paragraph's CONTENT was proven by terra" — false for the
   reason-code parenthetical (X1); terra executed two of five hops.
2. §2 "fixed the FACTUAL class" — false for this paragraph (X1). Round 3
   produced both classes; the same-signature statement in file 37 §C
   answered NO on the factual class because the check was citation-based.
3. §1 attributes the missing first-use table to Sol 266; file 33 asked for
   it under R3-B only.
4. §1's six terms under-count: twelve fail (§2.0), including "evidence
   row", "consumed arm", and "successor" (which collides with **committed
   successor** at 533).
5. Cure A contains a new factual error ("every path recorded at arming
   time"); Cure B contains a false gloss (window root) and inherits X1.
6. Contract has two names for one object: "consumption receipt"
   (612, code) vs **one-use consumption record** (672). Cure C(i) reconciles.
7. Sol 266's first-use table cites "pack root" at line 34; the phrase first
   appears at 464 and is glossed at 492 — a first-use defect in the R3-B
   text that terra also did not flag.
8. Packet head `fbedfb04` vs worktree HEAD `2f3592c5`: benign (trace files
   only), noted for the record.

---

## Executed evidence (bench, this session; every command from the worktree root)

```
$ git rev-parse --short HEAD; git branch --show-current
2f3592c5
fix/2026-09-02-decode-identity-set
$ git merge-base --is-ancestor fbedfb04 HEAD && echo yes-ancestor
yes-ancestor
$ git diff --stat fbedfb04..HEAD      # only trace files 37,38,39,40
$ grep -n "launch_binding_mismatch\|launch_consumption_missing\|def _replay_consumed_arm\|def _read_v2_consumption\|def authenticate_bundle_launch_lineage" joulewise/arm_readiness.py
  (defs: _read_v2_consumption 8960; _replay_consumed_arm 9304; authenticate_bundle_launch_lineage 10608)
$ grep -n "authenticate_bundle_launch_lineage\|def _read_bundle" joulewise/analysis_engine/inputs.py
  39 import; 2735 def _read_bundle; 2773 call
$ grep -rn "lifecycle receipt\|window root" docs/contracts/*.md
  identity_pin_projection.md:612, :613 only          (packet's grep reproduced)
$ ls docs/contracts                                   (no launch-lineage contract)
$ grep -n -i "consum" / "window" / "lifecycle" / "successor" docs/contracts/identity_pin_projection.md
  (first-use lines quoted in §2.0)
$ sed -n '166,176p;238,241p' docs/phase_2/window_runbook.md   (WINDOW_PLAN_ROOT contents; "outside the runs roots")
```

Missing-file hops (`$S` = scratchpad; `hops.py` calls the three readers with
paths under `/nonexistent-blind-seat/`):

```
$ TMPDIR=$S/tmp-blind PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 python3 -B $S/tmp-blind/hops.py
consumption receipt gone -> launch_consumption_missing | launch-lineage receipt is absent: /nonexistent-blind-seat/arm_readiness.consumptions/arm-0001.consumed.json: [Errno 2] ...
launch manifest gone -> launch_consumption_invalid | bound launch artifact is unreadable: /nonexistent-blind-seat/launch-manifest.json: [Errno 2] ...
lifecycle receipt gone -> launch_lifecycle_incomplete | launch-lineage receipt is absent: /nonexistent-blind-seat/arm-0001.start.json: [Errno 2] ...
window root gone (inline resolve as :10200) -> launch_binding_mismatch   <-- SIMULATED from the code literal, not executed
$ git status --short        (empty)
```

Mechanical first-use table (`firstuse.py <lo> <hi> <terms…>`: first line
containing the term; first line matching a definition pattern; verdict):

```
$ python3 $S/tmp-blind/firstuse.py 609 621 "consumption receipt" "launch manifest" "window root" "lifecycle receipt" "launch_binding_mismatch" "launch_consumption_missing" "consumed arm" "arming-time" "machine-absolute" "launch lineage" "pack root" "consumer_identity_set_unauthenticated" "successor pack" "successor-lineage" "evidence row" "input loading" "design lane" "relocatable" "arm" "receipt" "campaign pack"
consumption receipt        612  None  FAIL (no definition anywhere)
launch manifest            612  671   FAIL (defined later, +59 lines)
window root                612  None  FAIL
lifecycle receipt          613  None  FAIL
launch_binding_mismatch    614  None  FAIL
launch_consumption_missing 615  None  FAIL
consumed arm               585  None  FAIL
arming-time                613  None  FAIL
machine-absolute           609  None  FAIL
launch lineage             584  584   pass
pack root                  464  492   FAIL-outside-para (+28)
consumer_identity_set_unauthenticated 620 None  FAIL by pattern (in-sentence gloss; hand-triaged to pass)
successor pack             598  None  FAIL
successor-lineage          616  None  FAIL
evidence row               610  647   FAIL (+37; 647 is a use, not a definition)
input loading              614  614   pass
design lane                618  None  FAIL
relocatable                617  617   pass
arm                        147  148   false positive (same bullet)
receipt                    1    7     false positive (title/intro)
campaign pack              34   34    pass
```

Scripts are in the scratchpad (`tmp-blind/hops.py`, `tmp-blind/firstuse.py`);
nothing was written under either checkout.
