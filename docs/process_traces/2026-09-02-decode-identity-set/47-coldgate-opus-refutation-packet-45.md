# Opus contract-lens refutation — cold gate on packet 45 (Cure C, F-N5/F-N6, first-use gate rule)

Role: contract-lens REFUTER under `docs/process/coldgate_charter.md` §5. My charge is to attempt
FALSIFICATION of the packet's exhibits' claims, the cure texts, and the asserted application of the
controlling contract. I am not the judge. I have not seen the cold Fable seat's ruling.

---

## 0. Contamination disclosure (charter §4)

The following material was auto-loaded into my context by the harness BEFORE this charge, without my
requesting it. Charter §4 forbids it. **I used none of it as authority, rationale, background,
severity, or disposition**, and I flag below the one place where it collides with the merits:

1. `/Users/edr/.claude/CLAUDE.md` — global user rules, including a "Writing standard" section that
   states a **first-use test** in almost exactly the words packet question Q6 asks me to assess.
2. `/Users/edr/code/JouleWise/CLAUDE.md` — project instructions (Codex bridge, delegation routes).
3. `/Users/edr/code/JouleWise/CLAUDE.local.md` — private orchestration doctrine, "hard rules 1–11",
   including a **"rule 5"** about dropping review layers with zero unique catches over two sessions.
4. `~/.claude/projects/.../memory/MEMORY.md` — a ~45-entry auto-memory index.

**Firewall applied, and why it matters here.** Item 1 is the most dangerous: it would let me treat
the first-use rule as already-settled house style and wave Q6 through. I have instead assessed the
Q6 text *only* as a text, against the packet's exhibits and the tracked repo. Item 3 matters because
exhibit 41 §5 argues from an uncited **"rule 5"** — see finding **Q6-3**, where I show the tracked,
citable authority contradicts it. I reached that finding from `docs/orchestration.md`, a tracked file
exhibit 40 itself cites, not from the private doctrine file. Nothing else from items 1–4 informed
any conclusion below.

**See also §11.9 — a seal-integrity notice.** The cold adjudicating seat shares my scratch directory.
I did not open its ruling or its scripts; the fact is recorded there for the magistrate to rule on.

I read: the packet, all nine manifest exhibits, the contract at the pinned commit, and the code
(`joulewise/arm_readiness.py`, `joulewise/analysis_engine/inputs.py`, `tests/test_arm_readiness.py`
as the fixture builder). I did not open `RUN_STATE.md`, `docs/council_log.md`, files 39 or 43
(`*pause-state*`, narrative), or any scratchpad.

---

## 1. Integrity gates (charter §9)

| Item | Expected | Observed | Method |
|---|---|---|---|
| Checkout HEAD | `04e45f68` | `04e45f68` | `git rev-parse --short HEAD` |
| Charter sha256 | `099de884…c95d81` | `099de884…c95d81` | `shasum -a 256` |
| Packet sha256 | `b31dec0c…17381b` | `b31dec0c…17381b` | `shasum -a 256` |
| Validator | PASS | `"result":"PASS"` | `scripts/validate_gate_packet.py` |
| All 9 exhibits | expected == observed | 9/9 match | validator receipt |

Full receipt in §7. No mismatch; I do not REFUSE on §9 grounds.

**Commit-pin reconciliation (I checked this; it is clean).** The packet is assembled at `fc52bda6`;
my checkout is `04e45f68`. `git merge-base --is-ancestor fc52bda6 HEAD` → true, and the single
intervening commit touches only the four new trace files. `joulewise/arm_readiness.py`,
`joulewise/analysis_engine/inputs.py` and `docs/contracts/identity_pin_projection.md` are
byte-identical across the two commits, so every probe I ran at `04e45f68` is valid at the pinned
`fc52bda6`. Exhibit 45a is byte-identical to `git show fc52bda6:docs/contracts/identity_pin_projection.md`
(1042 lines, `diff` empty). **No custody defect here.**

---

## 2. Q2 — the five missing-file hops (F-N5): the exhibits' claim **STANDS**

I executed all five hops against a real settled lineage rather than reading line numbers. Method:
build one authentic consumption→start→settle chain via the repo's own fixture, confirm it
authenticates, then delete exactly one artifact and record
`LaunchLineageError.reason_code`. Control (unmutated) passes every time. Verbatim output in §7.1.

| # | Hop | Reason code **executed** | Emitting site |
|---|---|---|---|
| 1 | consumption receipt | `launch_consumption_missing` | `_read_launch_lineage_primary` `missing_code`, via `_read_v2_consumption` |
| 2 | pack root | `launch_binding_mismatch` | `_replay_consumed_arm`, "consumed arm pack root cannot be authenticated" |
| 3 | **launch manifest** | **`launch_consumption_invalid`** | `_read_exact_launch_reference`, "bound launch artifact is unreadable" |
| 4 | window plan root | `launch_binding_mismatch` | `authenticate_launch_lineage`, "launch manifest window root is unavailable" |
| 5 | **start / settle lifecycle receipts** | **`launch_lifecycle_incomplete`** | `_read_lifecycle_receipt` `missing_code` |

The landed paragraph at `:613-615` says a bundle whose arming-time paths no longer exist is refused
"(`launch_binding_mismatch`, or `launch_consumption_missing` when the consumption receipt itself is
gone)". **That parenthetical is wrong for hops 3 and 5.** F-N5 is confirmed by execution, not
inherited. I could not falsify it.

**Refuter's correction to the packet's own phrasing (NIT).** Packet §3 states F-N5 as "two of the
named refusal labels are not what the code emits." The paragraph names exactly two labels, and one
of them (`launch_consumption_missing`) is correct. The accurate statement is: *the paragraph's
blanket `launch_binding_mismatch` is wrong for two of the five hops.* Same defect, imprecise
description. Exhibit 44 E1 states it correctly ("names the wrong refusal label for two of the five
artifacts it binds"); the packet's §3 restatement drifts. **NIT.**

**Bonus falsification of the landed text that no exhibit raised.** `:611-613` says the gate "resolves
the recorded pack root strictly, **as it resolves** the consumption receipt…". The consumption
receipt is resolved with `Path(consumption_receipt).resolve(strict=False)` — explicitly NON-strict
(`_read_v2_consumption`). The landed sentence asserts uniform strictness that the code does not
have. Both Cure C texts happen to delete or rewrite this clause, so it does not survive either cure;
I record it because it is a third factual error in the same sentence, which bears on severity.

---

## 3. Q3 — pack-root provenance (F-N6): the exhibits' claim **STANDS**

Executed (§7.2):

- `CONSUMPTION_RECEIPT_KEYS` has **no** `pack_root`; a real on-disk consumption receipt has no key
  containing "root" at all.
- The `launch_lineage` mapping the bundle carries has **no** `pack_root` either.
- `arm["pack"]["pack_root"]` exists and is the sole recorded source; `_pack_record` writes
  `"pack_root": str(pack_root.resolve())`, and `_pack_record` is called at freeze/arm issuance
  (six call sites, five of them arm/freeze writers).
- `_replay_consumed_arm` reads `arm["pack"]["pack_root"]` — i.e. recovery is by replaying the
  consumption back to the **arm receipt**.

`:609` — "That root is the machine-absolute pack path recorded **when the arm was consumed**" — is
false. It is recorded when the arm was **issued**. F-N6 confirmed; I could not falsify it.

**Attempted falsification that failed, recorded honestly.** My probe showed
`authenticate_launch_lineage(...)["pack_root"]` (`/private/var/…`) differing textually from
`arm["pack"]["pack_root"]` (`/var/…`), which would have falsified *both* cures' "that root **is** the
path the arm receipt recorded". I traced it and it is a **fixture artifact**: the test's `setUp`
sets `self.arm["pack"]["pack_root"] = str(self.pack)` unresolved and mocks `_pack_record`. In
production `_pack_record` stores an already-`.resolve()`d string, so re-resolution is idempotent. I
withdraw the point. Residual, non-blocking: the value the gate uses is the *strict re-resolution* of
the recorded string, so the two can diverge if symlink topology changes between arm and analysis.
**NIT, not a blocker; no cure text need change.**

---

## 4. Q4 — grading both Cure C texts: **FALSIFIED — neither may land as written**

I attacked every behavioural clause of both texts. Executions in §7.3–§7.4.

### 4.1 Exhibit 41 §3 Cure C — two universals falsified by execution

**(41-A) BLOCKER — "for every registered bundle, `_read_bundle` re-reads the consumed arm receipt,
re-authenticates the pack it names, and requires every absolute path… to still resolve".**
FALSE. `authenticate_bundle_launch_lineage` begins:

```
if not launch_lineage_required(config):
    return None
```

`launch_lineage_required` returns true only when `config["run_metadata"]["tags"]` contains the
literal `launch_lineage_required`. **Executed:** a bundle without that tag returns `None` — no arm
receipt re-read, no pack re-authentication, no path resolution at all. The landed text was *correct*
here ("For successor packs…"; `:627` "Legacy evidence without successor launch lineage retains the
historical single-identity route"). Cure C's "every registered bundle" is a **regression introduced
by the cure**.

**(41-B) BLOCKER — "requires every absolute path the lineage records… to still resolve to the same
bytes it recorded", asserted in its own first-use table as "[BENCH] true for all five".**
FALSE for the window plan root. **Executed:** I injected a new file into the window plan root and
re-authenticated — it still **PASSED**. The window plan root is required to *resolve*
(`Path(manifest["window_plan_root"]).resolve(strict=True)`); its bytes are never digested or
compared. Only `window.env` and `window-chain.zsh` beneath it are digest-checked. The pack root is
likewise not "the same bytes" but a recomputed tree digest. So "all five" is false, and the
first-use table's `[BENCH]` marking on that row is an **unearned execution claim** — precisely the
failure mode the packet's own Q4 warns against ("a `file:line` citation is not proof").

**(41-C) MATERIAL — "the launch-lineage reason code belonging to the artifact that failed."**
This is not merely vaguer than the per-hop form; it asserts a per-artifact ownership of codes that
**does not exist**. A missing *launch manifest* emits `launch_consumption_invalid` — a code named
for the *consumption*, not the manifest. A reader applying Cure C's rule would predict a
manifest-flavoured code and be wrong. This directly defeats 41's stated reason for the family form
("closes F-N5 without requiring… a five-row code map that will drift"): it closes F-N5 by replacing
a wrong statement with an unfalsifiable-but-misleading one.

**(41-D) MATERIAL — "requires completion only when the caller asks for it."** At bundle loading the
caller is `_read_bundle`, which hardcodes `require_completion=False` (`inputs.py:2777`). Bundle
loading therefore *never* requires completion. The sentence is true of the underlying function and
misleading about the hop the paragraph is describing.

**(41-E) NIT — "input loading raises with the launch-lineage reason code."** The `LaunchLineageError`
is caught and re-raised as `AnalysisInputError(f"{exc.reason_code}: {path.name}: {exc}")`. At the
analysis boundary the code survives only as a **string prefix in a message**, not as a
machine-readable reason code. Both cures inherit this imprecision.

**Clauses of 41's Cure C I tried and FAILED to falsify (they stand):** the `arm receipt` bullet; the
`one-use consumption record` bullet including "does not record a pack root of its own"; the
`window plan root` bullet's `window.env`/`window-chain.zsh` direct-child requirement (enforced via
`expected_path` comparison → `launch_binding_mismatch`); "the seven refusal labels"
(`LAUNCH_LINEAGE_REASON_CODES` has exactly 7); "It does not re-derive the arm's own PASS/GO
decision" (`replay_arm_semantics=False`); "defined below" for
`consumer_identity_set_unauthenticated` (used `:620`, defined `:634`); and the final direct-call
sentence (executed, §7.2).

### 4.2 Exhibit 42 §2.3 Cure C (i)+(ii) — one universal falsified, two material defects

**(42-A) BLOCKER — "Before a bundle is admitted as analysis input, bundle loading authenticates its
launch lineage…".** Same falsification as 41-A, and **42 caused it deliberately**: its own first-use
table records `successor-lineage bundles | (c) deleted | "such bundles"`. Deleting the word
*successor* removed the exact qualifier that made the sentence true, and it also strands the later
"such bundles", whose antecedent is now "a bundle" generally. A first-use table that grades a
deletion PASS while the deletion falsifies the sentence is a demonstration that the vocabulary half
of the proposed gate **cannot see this defect class** — which is 41 §5's argument, now evidenced
against 42's own text.

**(42-B) MATERIAL — "reading five recorded files by their absolute paths".** Two of the five are
**directories**, not files (pack root, window plan root). Worse, the window plan root is not
"recorded" in the lineage at all: it is named by the **launch manifest**, one indirection further
out — as 42's own bullet (i) correctly says ("the absolute directory the launch manifest names").
Part (ii) contradicts part (i).

**(42-C) MATERIAL — bullet (i): the window plan root "is created outside the runs roots".** No code
enforces this. The only constraint on `window_plan_root` in `joulewise/` is
`Path(...).is_absolute()` (`arm_readiness.py:2577`); there is no runs-root containment check
anywhere. 42's own proof table marks this row "code-read + doc" and cites a **runbook**. Under the
packet's Q4 standard this clause fails, and it would install an unenforced operational convention
into an executable contract as though it were a property of the mechanism. **Delete it or mark it
explicitly as a convention the code does not check.**

**(42-D) NIT — bullet (i): the consumption receipt is "written beside the arm receipt".** They are in
**sibling directories**, not the same one: `…/<pack>/arm_readiness.consumptions/arm-0001.consumed.json`
versus `…/<pack>/arm_readiness.receipts/arm-0001.json` (executed paths, §7.2). "Beside" invites the
wrong mental model on a replication standard. The parenthetical path 42 gives is correct.

**Clauses of 42's Cure C I tried and FAILED to falsify (they stand):**
- The **order** claim — 42 marks it "code-read"; **I executed it and it holds.** Deleting *both*
  members of six different hop pairs always yields the earlier hop's code (§7.3). The claimed order
  consumption → pack root → manifest → window plan root → start/settle is correct. *I upgrade this
  row from "code-read" to EXECUTED.*
- All five per-hop reason codes (§7.1) — correct, and they are the F-N5 correction.
- "the arm cannot authorize a second launch" — enforced (`readiness_record_consumed`, "launch
  capability was already consumed", plus `O_EXCL` creation).
- The final direct-call sentence (executed, §7.2).
- "That root is the absolute path of the pack directory on the machine that armed it, copied into
  the arm receipt when the arm was issued" — correct, and it is the F-N6 correction.

### 4.3 Q4 verdict

**Neither text may land as written.** 42's (ii) is the better base — it carries the true per-hop
codes and a now-executed order claim — but requires three corrections: restore the successor/
marker-bearing qualifier (42-A), stop calling directories "recorded files" (42-B), and delete or
relabel the runs-roots claim (42-C). 41's Cure C requires (41-A), (41-B) and (41-C), of which
(41-C) is not a wording fix but a rejection of its central design choice.

---

## 5. Q5 — per-hop vs family: exhibit 41's family form is **FALSIFIED**; per-hop stands

The packet asks me to decide on the replication standard and on drift risk, and to say which I
weighted.

**I weight the replication standard, and I do so because drift risk turns out to be the weaker
consideration on this record — not because replication is axiomatically superior.**

- The family form is not a *less precise true* statement; per 41-C it is **misleading**. A reader
  told "the reason code belonging to the artifact that failed" will predict a manifest-named code
  for a missing manifest and get `launch_consumption_invalid`. The family form does not abstract the
  five-row map; it invites the reader to reconstruct a map that does not exist. A formulation whose
  cost is a *wrong inference* cannot be preferred on maintenance grounds.
- The drift argument is weakened by direct evidence in this record. Drift is real, but the
  five-row map is exactly the artifact a seam test pins, and this session demonstrates the map is
  **cheap to re-derive**: my §7.1 script re-establishes all five hops in one command in seconds. A
  contract fact that can be re-verified by one command per round is not a maintenance burden of the
  kind that justifies abstraction.
- Countervailing point I record against my own conclusion: the per-hop form does put five factual
  claims into prose that must be re-executed each time the layer changes. If the project ever lacks
  the executed-probe discipline the packet's Q6 rule is trying to install, the per-hop form degrades
  into five stale claims instead of one vague one. **The per-hop form is correct only if the Q6 rule
  (properly amended) actually lands.** They are a package.

**Per-hop (exhibit 42 form), with the 4.2 corrections applied.**

---

## 6. Q6 — the proposed rule text: **FALSIFIED — not installable as written**

Text under assessment (packet Q6): *"a pre-landing first-use table is mandatory for contract-prose
edits that add, move or rename defined terms or code literals, PAIRED with an executed probe for
every behavioural clause (a clause naming a reason code, an order, a provenance, or containing
before/after/first/then/only/never/always/every/all/each/strictly/exactly), both pasted by the writer
under Executed evidence before a verifier sees the text, the verifier re-running both."*

### Q6-1. BLOCKER (executed) — the mechanical trigger does not fire on the sentence carrying F-N6

Exhibit 41 §4 designs the trigger to be mechanical "so the writer cannot judge its way out", and its
coverage table claims formulation 4 catches **all six** historical defects including F-N6. I ran the
trigger over the landed paragraph, sentence by sentence (§7.5):

| Sentence | Fires? |
|---|---|
| 1 — *"That root is the machine-absolute pack path recorded when the arm was consumed."* (**this is F-N6**) | **DOES NOT FIRE** |
| 2 — the F-N5 sentence | FIRES (2 backticked codes; `before`, `never`, `strictly`) |
| 3 — *"Analysis of successor-lineage bundles therefore runs on the filesystem that armed them…"* | **DOES NOT FIRE** |
| 4 — the direct-call sentence | FIRES (backticked code) |

The F-N6 sentence contains no backticked identifier and none of the twelve trigger words. **The only
clause in the Q6 text that reaches it is "a provenance" — the one criterion that cannot be
mechanized**, which is exactly the judgment escape hatch the design set out to close. As written,
the rule either misses F-N6 or restores writer judgment. 41 §4's "covers all six" is falsified.

**Tested cure (§7.6):** add a provenance-verb list to the mechanical trigger —
`recorded | records | written | writes | issued | issues | copied | copies | stamped | stamps |
derived | derives | emitted | emits | armed | arms | carries | carried | resolves | resolved |
refuses | refused | replays | replayed`. Re-run: **all four sentences fire**, including 1 and 3.
Sentence 3 firing is a feature — it is an unproven behavioural consequence claim.

### Q6-2. BLOCKER — "an executed probe" lost its counterfactual

Exhibit 41 §4 specifies "an EXECUTED probe, pasted verbatim, **with its counterfactual**", and
grounds it in the standing lesson that cures proved against today's artifact kill nothing. The Q6
text drops "with its counterfactual". Without it, a writer satisfies the rule by pasting a happy-path
run that proves nothing. Every probe in §7 below pairs a control with a mutation for exactly this
reason; §7.3's order probe is only probative *because* it deletes two hops and shows which code wins.
**Restore the word.**

### Q6-3. BLOCKER — the attached drop test contradicts the controlling authority

Exhibit 41 §5 builds its drop test on an uncited **"rule 5"** — *"a layer with zero unique catches
over two sessions is dropped"* — with no file, no line, and no revision (charter §7 requires
"immutable revision and exact location"). Exhibit 40 cites the tracked authority; I verified it:

> `docs/orchestration.md:164-175` — "every review layer's unique catches are attributed and tallied
> per session under D-061 (C-027; **replaces the earlier two-zero-sessions auto-drop, which the
> integration-review zero/zero/five sequence falsified**): applicability is decided by PRE-DECLARED
> mechanical predicates; outcomes are classified accepted-unique-defect / duplicate /
> clean-verification / false-positive-suppression…; **three applicable exposures TRIGGER an
> expected-loss review decision, never automatic deletion**…"

41 §5 item 2 — "Zero unique catches across two consecutive qualifying sessions → **drop the layer**"
— is the very rule D-061 superseded, and the reason it was superseded (a layer that scored zero,
zero, then five) is the same failure mode 41's own noise-rate condition gropes toward. **Exhibit 40
is right and exhibit 41 is wrong on this point**, and exhibit 44 §3 propagated 41's version.

This is not an unresolved conflict of authority requiring REFUSE: the tracked primary source
resolves it plainly.

**The drop test I would record (D-061 shape, keeping 41's one genuine addition):**
> Applicability is decided by the rule's own mechanical predicate (a diff touching contract prose
> that adds/moves/renames a bolded defined term or a backticked code literal), declared before the
> session. Per applicable exposure, record: terms checked, behavioural clauses triggered, writer and
> verifier minutes, and each outcome classified accepted-unique-defect / duplicate /
> clean-verification / false-positive-suppression (suppression is not a catch). The vocabulary half
> and the behavioural half are tallied **separately**. After **three applicable exposures**, an
> expected-loss review decision is triggered — **never automatic deletion**. Additionally record the
> ratio of rows marked "pre-existing / waived" to rows flagged new; a ratio above 2:1 across two
> applicable exposures indicts the rule's **scoping**, not its value, and forces a re-cut of the
> predicate before any retirement question is asked.

### Q6-4. MATERIAL — the text is not the text Ed ratified

Exhibit 45c is admissible under charter §4 (its exact words are the object of Q6) and, to the
packet's credit, it supplies the checklist item, which is what makes this checkable. The checklist
item Ed answered read, in full: *"pre-landing first-use table as a mandatory gate for defined-term
contract edits, yes"*. The Q6 text adds three operative clauses Ed never saw: the **paired executed
probe**, the **"before a verifier sees the text"** ordering, and the **verifier re-running both**.
Calling that composite "as ratified by Ed's sentence in exhibit 45c" is unsupported paraphrase.

Two further weaknesses in the ratification itself, visible only because 45c is complete:
- Ed ratified checklist item 6 **as a block** of six sub-decisions and, in the same breath,
  **rejected one of them** ("30 min before a window seems too much"). A block assent immediately
  amended is not a considered per-item ratification of the first-use clause.
- "i trust you" is a **delegation**, not a specification; it cannot supply the operative details the
  text is missing.

I do not conclude Ed withheld approval — I conclude **the exhibit supports ratification of the
narrow checklist sentence, not of the Q6 composite.** The paired-probe half, which 41 §5 calls
mandatory and which my Q6-1/Q6-2 findings make load-bearing, still needs Ed.

### Q6-5. MATERIAL — five unenforceable or undefined terms

| Term | Defect | Minimum cure |
|---|---|---|
| "contract-prose edits" | no path scope; "prose" vs fenced blocks undefined | "a diff touching `docs/contracts/**.md` outside fenced code blocks" |
| "defined terms" | no mechanical marker | "a term set in `**bold**` within a defined-terms bullet block" |
| "code literals" | undefined | "a backtick-delimited token resolving to an identifier or string constant under `joulewise/`" |
| "move" | a line shift from an unrelated insertion above technically qualifies | "add, rename, or relocate **between sections**, as shown by the diff hunks" |
| "an order, a provenance" | not mechanically detectable — Q6-1 | replace with the extended word list of Q6-1 |

### Q6-6. MATERIAL — the rule states no consequence and no home

"Mandatory" names no failure action and no install location. A gate with no refusal is not a gate.
Add: *a landing record lacking either artifact is refused at review; the verifier records MISSING and
the round does not land* — and name the one file the rule lives in.

### Q6-7. NIT — "the verifier re-running both"

A table is not runnable unless produced by a script. Exhibit 44 §3 item 2 refers to "blind Fable's
script"; the rule must name it, and should say the verifier **re-derives independently from the
diff** rather than re-running the writer's artifact (41 §4's own stronger wording).

### Exact amended text I would install

> **Pre-landing proof gate for contract prose.** A diff that touches `docs/contracts/**.md` outside
> fenced code blocks, and that adds, renames, or relocates between sections either a `**bold**`
> defined term or a backtick-delimited code literal resolving to an identifier or string constant
> under `joulewise/`, must carry BOTH of the following in its landing record under **Executed
> evidence**, pasted by the seat that authored the text, at a commit preceding the verifying seat's
> brief:
> **(a) a diff-scoped first-use table**, generated by `<named script>`, with every term marked built
> before use / glossed at first use / deleted; and
> **(b) for every behavioural clause, an executed probe pasted verbatim together with its
> counterfactual** — a control showing the unmutated case passing and a mutation showing the claimed
> refusal, order, or provenance. A `file:line` citation is not admissible proof of a behavioural
> clause.
> A clause is **behavioural**, mechanically, if it contains a backtick-delimited identifier or
> reason code, or any of: `before after first then only never always every all each strictly
> exactly recorded records written writes issued issues copied copies stamped stamps derived derives
> emitted emits armed arms carries carried resolves resolved refuses refused replays replayed`.
> A verifying seat of a **different model family** independently re-derives (a) from the diff and
> re-executes every probe in (b), and diffs its results against the author's.
> **A landing record missing either artifact is refused at review; the verifier records MISSING and
> the round does not land.**
> Instrumentation and retirement follow `docs/orchestration.md:164-175` (D-061) with the vocabulary
> and behavioural halves tallied separately; see the drop test in Q6-3.

**Routing note (not my call, but stated because silence reads as concurrence):** the paired-probe
half is new relative to what exhibit 45c shows Ed ratified and should go back to Ed before install.

---

## 7. Q7 — the round-4 formulation: **STANDS**, with one contract-convention exception

Nothing in "magistrate writes a claim list, a seat writes the prose, a different-model verifier
re-executes every probe" is contrary to the charter. Charter §5 governs the composition of *this
gate*, not the authorship of a later fix round; charter §9's same-signature rule requires the next
spend be "a consult or redesign, not round three", and changing the axis of proof from citation to
execution **is** a redesign rather than a fourth authorship variant. I could not falsify it.

**One contract-convention exception no exhibit raised.** The contract's own status clause
(`docs/contracts/identity_pin_projection.md:10-11`) reads: *"The implementation in
`joulewise/identity_pins.py` is authoritative when this text and code differ."* The disputed
paragraph makes claims about `joulewise/arm_readiness.py` and `joulewise/analysis_engine/inputs.py`
— **two modules the contract's authority clause does not name**. So for exactly the sentences under
repair, the contract declares no tie-breaker against the code. Round 4's claim list should either
extend the status clause to name those modules or state that the lineage paragraph is descriptive of
external subsystems. **MATERIAL** — and it is the structural reason this paragraph has drifted from
the code four rounds running: nothing binds it to the modules it describes.

---

## 8. Q8 — packet hygiene: **FALSIFIED** (not neutrally assembled in three respects)

The packet is mechanically well-formed and its custody is sound (validator PASS; 45a byte-faithful;
the narrative pause-state files 39 and 43 are **correctly excluded** under charter §4 — I checked
that they exist and that their omission is proper, not suppression). Three defects remain.

**H1. MATERIAL — §5 instructs the seats not to lower a severity.** *"Do not lower F-N4's severity."*
Charter §8 reserves severity to the seat ("Severity is assessed independently of the verdict") and
§7 forbids a packet from altering authority. Scoping instructions ("do not re-litigate ruling (d)")
are legitimate; a **severity floor is a pre-committed finding**. Effect: it constrains Q4 and Q5,
where severity is exactly what is contested. *I record that I formed my own severities and was not
bound by this instruction; my findings raise, not lower, the paragraph's severity, so the defect did
not change my outcome — but it would have bound a seat that disagreed.*

**H2. MATERIAL — omitted exhibits 33–36, and Q1 cannot be answered without them.** The trace
directory contains `33-fix-round-3-brief.md`, `34-sol-266-fix-round-3-report.md`,
`35-bench-ruling-r3a-and-landing-47f083a2.md`, `36-delta-re-audit-3-brief.md`. None is in the
manifest. Q1 asks the seats to decide whether round 4 is "a second fix round on the same defect" and
to **individuate the defect** — a question that turns on what round 3 was *briefed* to fix (33), what
it *reported* fixing (34), and what actually *landed* (35). Worse, exhibit 44 §4 expressly argues
from file 33 ("the brief (file 33) had asked for it under R3-B only"), so the packet's own custody
exhibit reasons from a document the seats are not given. **Minimum cure: add 33, 34, 35 and 36 to
the manifest and re-freeze.**

**H3. MATERIAL — the packet disclaims recommendations that reach the seats through exhibit 44.** The
preamble states "This packet asks atomic questions; it offers no diagnosis and no recommendation."
Exhibit 44, in the manifest, contains a magistrate **recommendation directly on Q5** ("The
magistrate recommends the per-hop form to the cold gate") and asymmetric treatment of the dissent
("luna's answer was **the one convenient for the branch**" — a motive imputation, not a finding).
Partially mitigated: packet §3 labels 44 "custody, not authority", and 44 does carry the Opus
alternative and say "it may also reject both". Effect on me: none I can detect — I reached the
per-hop conclusion on 41-C, which 44 does not contain, and my Q5 reasoning rejects 44's stated
ground (drift/seam-test) as the weaker one. But charter §6 asks about neutral assembly, and a
recommendation plus a motive imputation against the sole dissenter is not neutral.

**H4. NIT — unexplained exhibit-lettering gap.** Exhibits run 45a, 45c with no 45b. I verified no
`45b-*` file exists, so nothing was withheld; the gap is cosmetic but invites exactly the suspicion
charter §6 tells me not to invent. Name it or re-letter.

**H5. NIT — §3's restatement of F-N5 drifts** from exhibit 44 E1's correct formulation (see §2).

**Not defects, checked and cleared:** the `fc52bda6` / `04e45f68` pin gap (code identical); exhibit
45a's fidelity; 45c's admissibility under charter §4 (source path, proposition, and the reason
non-narrative evidence is unavailable are all stated, with the checklist context that makes selective
quotation checkable — this is a well-built §4 exhibit); the exclusion of files 39 and 43.

---

## 9. Q1 — **REFUSE** (packet defect H2)

Not my assigned depth, but the charter requires me to answer or refuse. Individuating "the same
defect" requires the round-3 brief and landing record (files 33–35), which the packet omits (H2).
Charter §4: *"If ruling seems to require broader context than the packet supplies, that is a PACKET
DEFECT: say so and REFUSE the affected question rather than going looking."* I refuse rather than
reconstruct the defect boundary from the consult exhibits' characterizations of documents I was not
given. **Minimum cure: add files 33–36 to the manifest.**

I record that this REFUSE has no practical effect on convening: charter §3 item 4 fires independently
on the proposed process rule, and the packet states this. **REFUSE has no effect on the merits and
authorizes nothing** (charter §8).

---

## 10. Severity summary

| ID | Finding | Severity |
|---|---|---|
| 41-A | Cure C (41) "every registered bundle" false — marker-gated | **BLOCKER** |
| 41-B | Cure C (41) "same bytes… all five" false for window plan root; `[BENCH]` unearned | **BLOCKER** |
| 42-A | Cure C (42) "before a bundle is admitted" false; deleting "successor" caused it | **BLOCKER** |
| Q6-1 | Rule's mechanical trigger does not fire on the F-N6 sentence | **BLOCKER** |
| Q6-2 | "executed probe" lost its counterfactual | **BLOCKER** |
| Q6-3 | Drop test contradicts `docs/orchestration.md:164-175` (D-061) | **BLOCKER** |
| 41-C | Family-level reason-code form is misleading, not merely vague | MATERIAL |
| 41-D | "completion only when the caller asks" misleading at the bundle hop | MATERIAL |
| 42-B | "five recorded files" — two are directories; window plan root not lineage-recorded | MATERIAL |
| 42-C | "created outside the runs roots" unenforced by any code | MATERIAL |
| Q6-4 | Q6 text broader than what 45c shows Ed ratified | MATERIAL |
| Q6-5/6 | Undefined scope terms; no consequence, no home | MATERIAL |
| Q7-x | Contract status clause names only `identity_pins.py` | MATERIAL |
| H1 | Packet §5 pre-commits F-N4 severity | MATERIAL |
| H2 | Exhibits 33–36 omitted; Q1 undecidable | MATERIAL |
| H3 | Recommendation + dissent-motive imputation via exhibit 44 | MATERIAL |
| 41-E, 42-D, H4, H5, §2/§3 NITs | as recorded | NIT |

**Where I disagree with the magistrate's labeled disposition** (silence reads as concurrence,
charter §8): exhibit 44 §3 adopts "Cure C, in the blind-Fable per-hop form, verified by execution."
I agree with the **form** and disagree that either text is landable — 42's (ii) carries a BLOCKER
(42-A) that 44 does not record, introduced by 42's own first-use table. I also disagree with 44 §3's
adoption of 41's noise-rate drop test insofar as it inherits the superseded two-session auto-drop
(Q6-3), and with 44's implicit treatment of the Q6 composite as Ed-ratified (Q6-4).

---

## 11. Executed evidence

All commands run from `/Users/edr/code/JouleWise-wt-decode-id` at `04e45f68`, read-only; scripts
under `<scratchpad>/coldgate45/`.
Nothing was written under the checkout.

### 11.0 Integrity

```
$ git rev-parse --short HEAD
04e45f68
$ shasum -a 256 docs/process/coldgate_charter.md docs/process_traces/2026-09-02-decode-identity-set/45-coldgate-packet-fn4-cure-c.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
b31dec0c7fed3c1dcc4ad64f2c8dfc8289368be1c99d38c425435d13cc17381b  docs/process_traces/2026-09-02-decode-identity-set/45-coldgate-packet-fn4-cure-c.md

$ python3 scripts/validate_gate_packet.py --packet .../45-coldgate-packet-fn4-cure-c.md \
    --charter docs/process/coldgate_charter.md \
    --expected-packet-sha256 b31dec0c... --expected-charter-sha256 099de884...
{"binding_scope":"validation_time_observation_only","details":[], ... "result":"PASS",
 "schema":"coldgate-validator-receipt/v2"}
   exhibits: 9/9 expected_sha256 == observed_sha256
   exhibit_manifest_sha256: 5201b7ff0a28791807f811f7f75292b6c87ffa5f5d92c7dcb4956bc36969811b

$ git merge-base --is-ancestor fc52bda6 HEAD && echo YES_ANCESTOR
YES_ANCESTOR
$ git diff --stat fc52bda6 HEAD -- joulewise/arm_readiness.py joulewise/analysis_engine/inputs.py docs/contracts/identity_pin_projection.md
   (empty — no code or contract change between the pinned commit and HEAD)

$ git show fc52bda6:docs/contracts/identity_pin_projection.md > /tmp/.../contract_at_fc52bda6.md
$ diff /tmp/.../contract_at_fc52bda6.md .../45a-exhibit-identity_pin_projection-at-fc52bda6.md && echo IDENTICAL
IDENTICAL: exhibit 45a == contract@fc52bda6
```

### 11.1 The five missing-file hops (Q2 / F-N5) — `probe_hops.py`

Method: build one real settled lineage from `tests.test_arm_readiness.LaunchConsumptionV2Tests`,
verify the control authenticates, delete exactly one artifact (plus its `.sha256` sidecar where the
reader requires one), call `authenticate_launch_lineage(..., require_completion=False)`.

```
$ PYTHONPATH=. python3 .../probe_hops.py
=== control: does an unmutated settled lineage authenticate? ===
    PASS, pack_root = /private/var/folders/.../tmp8x5v3lqr/pack-v2

HOP 1  consumption receipt missing
    reason_code: launch_consumption_missing
    message: launch-lineage receipt is absent: .../arm_readiness.consumptions/arm-0001.consumed.json: [Errno 2] No such file or directory

HOP 2  pack root missing
    reason_code: launch_binding_mismatch
    message: consumed arm pack root cannot be authenticated: [Errno 2] No such file or directory: '.../pack-v2'

HOP 3  launch manifest missing
    reason_code: launch_consumption_invalid
    message: bound launch artifact is unreadable: .../arm_readiness.t0.inputs/launch-manifest.json: [Errno 2] No such file or directory

HOP 4  window plan root missing
    reason_code: launch_binding_mismatch
    message: launch manifest window root is unavailable: [Errno 2] No such file or directory: '.../arm-custody/window-plan'

HOP 5a start lifecycle receipt missing
    reason_code: launch_lifecycle_incomplete
    message: launch-lineage receipt is absent: .../arm_readiness.launch_lifecycle/arm-0001-launch.start.json: [Errno 2] No such file or directory

HOP 5b settle lifecycle receipt missing
    reason_code: launch_lifecycle_incomplete
    message: launch-lineage receipt is absent: .../arm_readiness.launch_lifecycle/arm-0001-launch.settle.json: [Errno 2] No such file or directory
```

Fixture caveat, recorded: `setUp` patches `_pack_record`. The patch is irrelevant to HOP 2 because
`Path(arm["pack"]["pack_root"]).resolve(strict=True)` raises **before** `_pack_record` is called
(`_replay_consumed_arm`, the `try` opening at the `recorded_pack_root` assignment).

### 11.2 F-N6 and the direct-call label (Q3) — `probe_fn6.py`

```
$ PYTHONPATH=. python3 .../probe_fn6.py
=== consumption receipt keys (sorted) ===
['arm_context_sha256','arm_receipt','assurance','boot_session_id','consumed_at_monotonic_ns',
 'consumed_at_utc','consumption_id','exec_argv','handoff_token_sha256','head_commit',
 'launch_manifest','pack_id','pack_sha256','plan_id','receipt_kind','schema_version',
 'volatile_checks','window_chain','window_environment','window_id']
  'pack_root' in consumption receipt: False
  any key containing 'root': []

=== arm receipt: arm['pack'] keys ===
['pack_digest_algorithm','pack_id','pack_root','pack_sha256','plan_id','plan_tree_path',
 'plan_tree_sha256','plan_tree_sidecar_path','plan_tree_sidecar_sha256','window_id']
  arm['pack']['pack_root'] = /var/folders/.../tmpr7xs0nyn/pack-v2

=== launch_lineage mapping keys (what the bundle carries) ===
['bracket_session_id','collection_boot_session_id','completion','consumption','pack_id',
 'plan_id','schema_version','settle','start','window_id']
  'pack_root' in launch_lineage: False

=== CONSUMPTION_RECEIPT_KEYS from the module ===
  'pack_root' present: False

=== analysis gate: unresolvable pack_root -> ? ===
  _frozen_consumer_identity_set -> frozenset()
  empty (not None) => _floor_request_or_refusal returns ('consumer_identity_set_unauthenticated',): True
```

Receipt locations (from the same run, establishing 42-D): consumption receipt at
`…/pack-v2/arm_readiness.consumptions/arm-0001.consumed.json`; arm receipt at
`…/pack-v2/arm_readiness.receipts/arm-0001.json` — sibling directories.

Supporting reads: `_pack_record` writes `"pack_root": str(pack_root.resolve())`;
`_frozen_consumer_identity_set` catches `OSError` among others and returns `frozenset()`;
`_floor_request_or_refusal` maps a non-`None` empty set to
`("consumer_identity_set_unauthenticated",)`.

### 11.3 The order claim (Q4 / exhibit 42) — `probe_order.py`

Method (counterfactual by construction): delete **both** members of a hop pair; the code emitted must
be the **earlier** hop's if the claimed order is real.

```
$ PYTHONPATH=. python3 .../probe_order.py
  removed 1_consumption + 2_packroot    -> launch_consumption_missing
  removed 2_packroot    + 3_manifest    -> launch_binding_mismatch
  removed 3_manifest    + 4_windowroot  -> launch_consumption_invalid
  removed 4_windowroot  + 5_start       -> launch_binding_mismatch
  removed 1_consumption + 5_start       -> launch_consumption_missing
  removed 2_packroot    + 5_start       -> launch_binding_mismatch
```

Every pair yields the earlier hop's code. Order **consumption → pack root → launch manifest →
window plan root → start/settle** is EXECUTED and confirmed.

### 11.4 Falsifying exhibit 41's two universals — `probe_universals.py`

```
$ PYTHONPATH=. python3 .../probe_universals.py
=== CLAIM A: 'for every registered bundle, _read_bundle re-reads the consumed arm receipt...' ===
  bundle WITHOUT the 'launch_lineage_required' tag -> None
  launch_lineage_required({'run_metadata':{'tags':['something_else']}}) = False
  => no arm receipt re-read, no pack re-authentication, no path resolution.
  CLAIM A is FALSE as an unrestricted universal.

=== CLAIM B: requires 'every absolute path ... to still resolve to the same bytes it recorded',
    asserted '[BENCH] true for all five' ===
  window plan root: .../arm-custody/window-plan
  contents before: ['window-chain.zsh', 'window.env']
  contents after : ['INJECTED-BY-REFUTER.txt', 'window-chain.zsh', 'window.env']
  re-authentication after mutating the window plan root: PASS
  => the window plan root is required to RESOLVE, but its bytes are never
     digested or compared. CLAIM B is FALSE for the window plan root.
```

### 11.5 The Q6 trigger, as written — `probe_trigger.py`

```
$ PYTHONPATH=. python3 .../probe_trigger.py
--- sentence 1 ---
   That root is the machine-absolute pack path recorded when the arm was consumed.
   TRIGGER: *** DOES NOT FIRE ***
--- sentence 2 ---
   Bundle loading authenticates the launch lineage before any evidence row exists: ...
   TRIGGER: FIRES -> backticked: `launch_binding_mismatch`, `launch_consumption_missing` | words: before, never, strictly
--- sentence 3 ---
   Analysis of successor-lineage bundles therefore runs on the filesystem that armed them; ...
   TRIGGER: *** DOES NOT FIRE ***
--- sentence 4 ---
   Called directly with a lineage whose pack root does not resolve, the gate refuses with `consumer_identity_set_unauthenticated`, ...
   TRIGGER: FIRES -> backticked: `consumer_identity_set_unauthenticated`
```

Sentence 1 is the F-N6 sentence. The trigger misses it.

### 11.6 The amended trigger — `probe_trigger2.py`

```
$ PYTHONPATH=. python3 .../probe_trigger2.py
sentence 1: FIRES   backtick=-  words=-  provenance-verbs=['recorded']
sentence 2: FIRES   backtick=['`launch_binding_mismatch`','`launch_consumption_missing`']  words=['before','never','strictly']  provenance-verbs=['recorded','resolves','refused','replays']
sentence 3: FIRES   backtick=-  words=-  provenance-verbs=['armed']
sentence 4: FIRES   backtick=['`consumer_identity_set_unauthenticated`']  words=-  provenance-verbs=['refuses']
```

### 11.7 Authority and code reads verified by direct inspection

```
$ sed -n '31,36p' docs/process/coldgate_charter.md
  4. Any proposed process rule (including amendments to this charter).      [exhibit 40's cite verifies]

$ sed -n '164,175p' docs/orchestration.md
  "...under D-061 (C-027; replaces the earlier two-zero-sessions auto-drop, which the
   integration-review zero/zero/five sequence falsified) ... three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion..."          [falsifies exhibit 41 §5]

$ grep -n "consumer_identity_set_unauthenticated" docs/contracts/identity_pin_projection.md
  620:  (use, inside the object paragraph)
  634:  (definition)                                     ["defined below" in 41's Cure C verifies]

$ grep -n "window_plan_root" joulewise/**/*.py | grep -v test
  arm_readiness.py:2577:  if not Path(str(manifest["window_plan_root"])).is_absolute():
  (no runs-root containment check anywhere)                             [falsifies 42's bullet (i)]

$ grep -n "already consumed" joulewise/arm_readiness.py
  8787: "readiness_record_consumed", "launch capability was already consumed"
  9763: "readiness_record_consumed", "launch capability was already consumed"   [42's single-use bullet stands]

  LAUNCH_LINEAGE_REASON_CODES (arm_readiness.py:222-232) has exactly 7 members   ["seven" stands]
  authenticate_launch_lineage calls _replay_consumed_arm(..., replay_arm_semantics=False)
                                                          ["does not re-derive PASS/GO" stands]
  inputs.py:2773 _read_bundle -> authenticate_bundle_launch_lineage(..., require_completion=False)
  inputs.py:2779 except LaunchLineageError -> raise AnalysisInputError(f"{exc.reason_code}: ...")
  no `except AnalysisInputError` between inputs.py:2904 and :3210      ["whole input set refused" stands]
  docs/contracts/identity_pin_projection.md:10-11 names only joulewise/identity_pins.py   [Q7 exception]
```

### 11.8 Files written

Mine, all outside the checkout:
`probe_hops.py`, `probe_fn6.py`, `probe_order.py`, `probe_universals.py`, `probe_trigger.py`,
`probe_trigger2.py`, `contract_at_fc52bda6.md`, `opus-refutation.md`.

### 11.9 SEAL-INTEGRITY NOTICE (charter §5) — raised, not exploited

On my closing sanity check (`ls` of my own scratch directory, run to confirm I had written nothing
under the checkout) I discovered that **the cold adjudicating seat has been given the same scratch
directory as me**. It contains, alongside my six probe scripts:

```
cold-fable-ruling.md
bundle.py   cascade.py   extras.py   hops.py   q3.py   tmp
```

None of these is mine. **I did not open `cold-fable-ruling.md` or any of the other seat's files, at
any point.** The only knowledge I have of them is the file listing above, produced after my
refutation was already written to disk in full; no conclusion in this document could have been
influenced by them, and none was.

Charter §5 requires: *"You do not see the refuter's output, nor it yours, before both are SEALED:
recorded verbatim and hash-pinned in the gate record."* Shared scratch storage makes that
independence a matter of each seat's restraint rather than of construction. It also means my own
in-progress file was readable by the cold seat throughout. I cannot attest to what the other seat
did or did not read.

**This is a defect in the gate's machinery, not in the packet, and I raise it under charter §9's
rule that a later gate may assess issuance machinery "only when that question is expressly
presented" — it is not presented here, so I make no finding about the validity of this gate's
outputs.** I record it so the magistrate can rule on it with the fact in hand.

**Minimum cure for future gates:** give each seat a scratch path the other cannot enumerate, and
have the synthesis record the two seats' output digests taken at seal time.

---

## 12. Verdicts

| Q | Verdict |
|---|---|
| Q1 | **REFUSE** — packet defect H2 (files 33–36 omitted); moot for convening, §3 item 4 fires independently |
| Q2 | **STANDS** — F-N5 confirmed by execution; the landed paragraph names the wrong code for hops 3 and 5 |
| Q3 | **STANDS** — F-N6 confirmed; pack root recorded at arm ISSUANCE; the consumption receipt carries none |
| Q4 | **FALSIFIED** — neither Cure C is landable; 3 BLOCKERs (41-A, 41-B, 42-A) plus 41-C/41-D/42-B/42-C |
| Q5 | **FALSIFIED for the family form (41)** — it is misleading, not merely vague; per-hop (42) stands with corrections |
| Q6 | **FALSIFIED** — not installable; trigger misses F-N6 (executed), counterfactual dropped, drop test contradicts D-061, text broader than 45c ratifies |
| Q7 | **STANDS** — with one contract-convention exception (status clause names only `identity_pins.py`) |
| Q8 | **FALSIFIED** — H1 severity floor, H2 omitted exhibits, H3 recommendation + dissent framing; custody itself clean |

Recorded as the permanent artifact charter §8 requires. I have not seen the cold seat's ruling.
