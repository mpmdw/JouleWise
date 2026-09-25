# Cold Fable gate ruling — A291-FORGER-02 (F-A escalation; disposition of F-C's nine OUT_OF_ROUND candidates)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold session, no loop context, foreground only, no subagents, no background tasks. Started 2026-09-24 20:04:39 PDT; ruling written ≈20:12 PDT. Worktree `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-forger2` at detached HEAD `f5c45ba4`.

## 0. Disclosure of auto-loaded context

The harness injected three files before I acted, none requested: the global `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the project memory index `MEMORY.md` (partial; 6 lines truncated). The memory index is loop-context narrative of the kind charter §4 forbids. I opened no memory file and used neither CLAUDE file as evidence or authority; every load-bearing conclusion below cites an exhibit, a git object, or a probe I ran. Not read, by rule: CLAUDE.local.md (absent; convene script asserts it), RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory files, any `docs/process_traces` file outside the packet directory. One probe (§1.3) located the contract's git blob by hash without printing any file outside the packet.

## 1. Pre-merits verification (charter §9)

### 1.1 Charter and packet digests

| item | expected | observed | method |
|---|---|---|---|
| charter `docs/process/coldgate_charter.md` | `…c95d81` (convene message, independent of the packet) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256` + validator receipt `digests.charter_sha256` |
| packet `00-charge.md` | `8fec694a25517ea84d60e6b375bbf77ec049f5cf2183eda6e24d9749b1320458` | identical | same |

Validator run 1 (deliberate typo `…c95d82`): `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2. Run 2 (`…c95d81`): `result: PASS`, rc=0, schema `coldgate-validator-receipt/v2`, `judge_handoff_bound: false`, all nine exhibit digests observed == expected, `exhibit_manifest_sha256 66e80530…685f`; the packet's own charter pin equals the trusted value. Merits opened only after run 2.

### 1.2 Revisions

The convene message names `0fa4e6e3`/`24ff94cb` for code evidence; the charge names `6e2504b1`/`36e470ca`. All four exist here. `36e470ca` (K's R4-3 landing) is an ancestor of `6e2504b1` (P's R4-2 landing; the integrated head named by the charge and by `ex-104-adjudicate.py:2`); their diff touches only `joulewise/scored_packer.py` and `tests/test_scored_packer.py`. I used the charge's pair, which is the integrated head under test; the convene message's pair is the packet-101 pair and is stale here (finding F6, NIT).

### 1.3 Exhibit provenance and probe inputs

- `ex-95-texts-r4b.md` is byte-identical to the exhibit of the same digest (`63787c28…9b87`) in the A291-FORGER-01 packet, whose provenance the prior judge established as the complete "Final texts" section (`ex-101-forger-ruling.md` §1.3). I did not re-derive that.
- The contract the forger was given, `/tmp/forger-278ebc9e-fable/CONTRACT-v4.1.md`, hashes to git blob `b4b1b176d9f0fde7bbf01d30ce274a48a90b707a`, which at HEAD is tracked as `docs/process_traces/2026-09-24-activation-278ebc9e/89-a291-contract-v4-1-inv11-closed.md` and as the R3 addendum exhibit `ex-89-contract-v4-1.md`. All contract citations below are to that blob by line ("C:n"). It is absent from the `6e2504b1` and `36e470ca` trees (it lives in the process tree, not the code tree).
- `/tmp/forger-278ebc9e-fable/` holds `forge_common.py` (`25500568…d16f`), `forge_candidates.py` (`04333495…64d7`), `forge_more.py` (`6d3f06ca…195b`) and a `joulewise/` snapshot; `/Users/edr/code/wt-278ebc9e-a291p3` is at `6e2504b1` exactly (`git rev-parse HEAD`). These are the inputs `ex-104-adjudicate.py` names.
- `ex-103-fa-runs-summary.txt` is a two-line magistrate paraphrase with no log path, digest or line range; the vendor message is quoted nowhere else. `ex-103b-fa-run2.md` is the seat's own null-final report and shows only that no candidate was submitted (`status: blocked`, `verdict.findings: []`). See finding F2.

### 1.4 Executed probes

P1 — `python3 ex-104-adjudicate.py` re-run from `/tmp` (rc=0): the twenty JSON rows are identical to `ex-104-fc-adjudication.jsonl` (diff empty); `LEN labels 20 captured 37` identical. The nine ACCEPTED rows carry oracle `[]` and checker rows drawn only from {INV-23, INV-36, INV-37, INV-38, INV-52}.

P2 — replay and the public entry on each of the nine accepted rosters (script `/tmp/coldgate-forger2-replay.py`, calling `_replay_roster(reg, r)` and `verify_executed_roster(reg, r, predictions)` at the `/tmp` snapshot of `6e2504b1`):

| candidate | `_replay_roster` | `verify_executed_roster` |
|---|---|---|
| C1 grandchild single | REFUSED `inv_38: event replay` | same |
| C2 root with pre-split parent | REFUSED `inv_39: root re-pack` | same |
| C2b root with terminal refusal | REFUSED `inv_39: root re-pack` | same |
| C3 retargeted terminal refusal | REFUSED `inv_38: event replay` | same |
| C4 phantom terminal refusals | REFUSED `inv_39: root re-pack` | same |
| C5 superseded flag on terminal single | REFUSED `inv_38: event replay` | same |
| C6 forged placement stage/attempt | REFUSED `inv_39: root re-pack` | same |
| C7 live placement into reported envelope 0 | REFUSED `inv_38: event replay` | same |
| C8 event-less reschedule | REFUSED `inv_38: event replay` | same |

P3 — code reading at `6e2504b1:joulewise/scored_packer.py`: `_seal` (l.273–310) checks digests only when `finalize` is false (l.282–288), then `_structure` then `_checked_derived` (l.289–290); the seal's refusal-code inventory contains no `inv_23`, `inv_36` or `inv_37` (grep of every `_need(...)` code); `requeue_overrun` runs `_seal` then `_replay_roster` at entry (l.413–414); `verify_executed_roster` runs both (l.492–493); `executed_status` calls `verify_executed_roster` first (l.499); `pack` alone finalizes without replay (l.389) but builds its own roster. `_replay_roster` (l.471–488) re-packs the root, asserts `registered_sha256` (`inv_39`), replays every event with per-event equality and asserts `state == roster` (`inv_38`).

P4 — contract text (blob `b4b1b176`): F column legend C:423 ("(a) refusal … refused with the typed refusal"); rows INV-23 C:545, INV-36 C:613, INV-37 C:620, INV-38 C:626, INV-52 C:644 are all "F: a; Chk: yes" with codes `inv_23`/`inv_36`/`inv_37`/`inv_38`/`inv_52`; INV-40 C:639 (`_seal` at entry of `requeue_overrun` and `reduce` and every public exit); FT-8 replay C:376; Q16 C:375; glossary Parent/Single C:63–64 and C:477; `superseded` iff C:212; §2.8 terminal type domain C:252 and uniqueness C:260; Q11 C:353; INV-10 C:467–469; INV-11 closed form C:471–473; INV-12 C:485–489. The charge's phrase "refuse contract violations 'before derived arithmetic'" occurs nowhere in the contract (grep for `arithmetic`, `before … derived`); it paraphrases the seal's code order at l.289–290.

Not executed: none of the planned probes was cut. I did not run the discovery suite, the test suite, `sudo`, `launchctl`, `powermetrics` or `systemsetup`; I touched no canonical, custody, measurement or LaunchAgents path; I wrote only this file.

## 2. U1 — who replaces F-A

### 2.1 Verdict

**REJECT "F-C alone"; REJECT Sol 6.0; RULE replacement text: F-A is replaced by a second fresh Fable 5.1 seat (F-B), and item (4) requires both F-B and F-C `COMPLETED_NO_ESCAPE`.** Exact text in §2.3.

### 2.2 Reasoning

1. **The escalation is real under the ruled text but its evidence is thin.** `ex-101-forger-ruling.md` §2.3(vi) gives one rerun per seat and escalation on the second `INCONCLUSIVE`. `ex-103b` proves run 2 submitted nothing (`verification: V1` only, `flags.F1: verification_gap`), which is `INCONCLUSIVE` by the unchanged R4-5(4) definition ("timeout without a submitted candidate, or unadjudicable output"). Whether the cause was a vendor content filter rests solely on the magistrate's two-line paraphrase (`ex-103`). I rule U1 on the proved fact (two `INCONCLUSIVE`, no candidate) and require the cause to be exhibited from the log (§2.3 clause (d); finding F2).
2. **Sol 6.0 is barred twice.** `ex-101` §2.3(i) and (v) require F-A's model ≠ K's model; Sol 6.0 is K's model by the charge's own premise, so a Sol seat would need an amendment the packet does not ask for. Independently, charter §9 forbids a third same-signature round without explicit justification: two consecutive Codex-route runs failed the same way on two differently worded briefs (`ex-102`, `ex-102a`), and the charge itself expects the same filter. No justification is offered. Not licensed.
3. **F-C alone is weaker than the gate ruled.** `ex-101` §2.2 rejected a one-seat pass on exactly this ground ("a two-seat gate that passed on one seat would be weaker than the one-seat gate it replaces"). A vendor refusal is not evidence that the seal is safe (`ex-103b` "Residual risk" says so itself). Converting the conjunction into a single seat because the second seat was refused would be a reinterpretation of a ruled gate (charter §9).
4. **A second fresh Fable seat preserves every ruled independence that remains available.** `ex-101` defines the operative notion as model id, not vendor (§2.3 preamble: "model" means the named model id; (ii) accepts Fable 5.1 as "a model different from P's"). A second Fable seat is ≠ P's model and ≠ K's family, satisfies (iii) isolation verbatim, and adds a genuinely independent 30-minute search: F-C's nine accepted shapes (`ex-104-fc-report.md`) show the Claude-family seat is not captured by P's picture of a legal roster, which was ex-101's stated worry about a same-family attacker. Opus 5.5 is P's model and excluded; no third vendor is on the bench (`ex-101` §1.4 probe, not re-run). The only cost is one read-only seat.
5. **Error control, not ceremony.** The value of the second seat is a second draw from the forgery space with no shared context; it is not a vote. Item (4) still fails on any `ESCAPE` from either seat under the unchanged stop rule.

### 2.3 Ruled text (replaces `ex-101` §2.3 clause (i) for this activation; every other clause of `ex-101` §2.3 stands verbatim)

> **(i′) Seat F-B (replacing F-A after two `INCONCLUSIVE` runs on the audited exec route, record items 97–98).** Model Fable 5.1 (Claude family, a model different from P's). Launched as a fresh headless session with `WRITE_SCOPE: []`, cwd `/tmp/forger-<activation>-fable-b/`, prepared exactly as (iii) requires and populated by a new `git archive <integrated head>` with `tests/` removed; the directory contains none of F-C's scratch files, briefs, candidates or results, and F-B is not told that F-C or F-A existed. Brief: `ex-102-brief.md` verbatim (not `ex-102a`). F-B's first output line is checked under (iii); if it lists any file other than the user-global `~/.claude/CLAUDE.md`, the seat is `INCONCLUSIVE` (contaminated) and reruns once.
>
> (a) **Aggregation.** Clause (vi) reads with F-B in place of F-A: item (4) is `COMPLETED_NO_ESCAPE` only when both F-B and F-C are `COMPLETED_NO_ESCAPE`. F-C's result (record item 99, `ex-104-fc-adjudication.jsonl`) stands and is not re-run.
>
> (b) **Record line, clause (v).** The gate record's one-line assertion reads: P ∉ Codex family; K ∉ P's family; F-B's model ≠ P's model; F-C's model ≠ P's model; F-B and F-C share no directory, brief output, or session; F-A: `INCONCLUSIVE` ×2 (vendor refusal, see (d)).
>
> (c) **Sol 6.0 not licensed.** No Codex-family forger run is licensed for this activation without a separately convened question stating why a third run would not fail with the same signature (charter §9).
>
> (d) **F-A cause of record.** Before item (4) is declared, the record carries, for each F-A run, the codex-run log path, its sha256, and the verbatim line range containing the vendor refusal text; absent that, F-A is recorded as "`INCONCLUSIVE` ×2, cause unexhibited" and nothing else is asserted about the vendor.

Deciding exhibits: `ex-101-forger-ruling.md` §2.2–2.3; `ex-103b-fa-run2.md` (`status: blocked`, no candidates); `ex-102`/`ex-102a` (two briefs, same outcome); charter §9.

## 3. U2 — the nine OUT_OF_ROUND candidates

### 3.1 Verdict

**AFFIRM the OUT_OF_ROUND classification of all nine (verified, P1). REJECT "must become seal-owned before A291 can merge". AFFIRM that the merge-time guarantee for these nine shapes rests on replay, which every public consuming entry runs (P3), and which refuses all nine (P2). REJECT the ex-101 F2 oracle-gap rule as drafted; RULE a narrower replacement (§3.4). None of the nine rationales is refutable from the contract (§3.2).**

### 3.2 Per-candidate refutability from the amended contract

A rationale is "refutable" if the contract permits the roster. I checked each against the blob `b4b1b176` clauses the seat cited.

| # | seat's rationale | contract check | refutable? | production refusal (P2) |
|---|---|---|---|---|
| C1 | single whose parent is a single; `superseded` on a `single_problem` block | C:63–64 Parent = created by `pack`, Single's parent is "its parent's id" (a Parent); C:212 `superseded` iff a `whole_block` retry that was split | **No** | `inv_38` |
| C2 | root (`events == []`) already split | C:471 glossary "Root roster: events == []" [FT-4]; C:64 single "created by a split"; C:212 | **No** | `inv_39` |
| C2b | root with terminal refusals and a voided parent | C:306 [FT-1] terminals arise only in a `requeue_overrun` call; root has none | **No** | `inv_39` |
| C3 | terminal entry with `type "bogus_type"`, foreign block/attempt/level | C:252 type domain is two literals; C:620–622 INV-37 predicate `(block_id, attempt)` names a voided placement of a block containing the item | **No** | `inv_38` |
| C4 | duplicated terminal entries for an unregistered (model, item) | C:260 `(model, item_id)` unique; C:437 INV-04 item identity | **No** | `inv_39` |
| C5 | `superseded` true on a terminal single | C:212 | **No** | `inv_38` |
| C6 | root placement with `stage single_problem`, `attempt 5` | C:616 INV-36 predicate "a root holds only `initial` placements with `attempt 0`"; C:353 Q11 | **No** | `inv_39` |
| C7 | live placement into a reported envelope | INV-18 (checker row C:43 text; ruled text quoted by the seat) | **No** | `inv_38` |
| C8 | placement with no creating event; block `attempt` ≠ latest placement | C:353 Q11 ("rises by exactly 1 per placement"); RD-2/RD-3 as quoted by the seat (not independently re-read; INV-36 checker row fired, P1) | **No** | `inv_38` |

Every one is a genuine contract violation that `_seal(finalize=True)` accepts. None violates INV-10 or the closed-form INV-11 (C:471–473): I confirm the oracle's `[]` on each is correct under the closed form, because in every case each (model, item) has exactly one live non-superseded holder or exactly one terminal entry. The round definition at `ex-95-texts-r4b.md:27` therefore classifies all nine `OUT_OF_ROUND`, and charter §9 forbids me to reinterpret that definition after the fact.

### 3.3 Seal-owned or replay-owned

1. **What the contract actually assigns.** The F column (C:423) says a violating input "on that path is refused with the typed refusal"; it does not say by `_seal`. INV-40 (C:639) places `_seal` at the entry of `requeue_overrun` and `reduce` and at every public exit; FT-8 (C:376) and Q16 (C:375) place replay at the same entries. The contract's own words for INV-38 (C:636) say "the replay's re-derivations are covered by INV-30 to INV-38 in the checker", i.e. the contract already treats event-provenance rows as replay-owned. Nothing in the contract requires the private function `_seal(finalize=True)` to refuse these five rows by itself, and the charge's "before derived arithmetic" premise has no contract text behind it (P4).
2. **What production does.** Every public entry that consumes a roster runs `_seal` then `_replay_roster` (P3, l.413–414, l.492–493, l.499); `pack` never consumes one. `_seal(finalize=True)` is reachable only from `pack`/`requeue_overrun` exits on rosters the module built (l.389, l.468) or from a direct private call, which is the forger's target and not a production path. All nine forged rosters are refused at the first public entry (P2), so no forged ownership, placement or terminal reaches the executed arithmetic.
3. **Therefore not a merge blocker.** Moving INV-23/36/37/38/52 into the seal would duplicate replay for these shapes and is a design choice for the INV-12 reconciliation queue that R4-5(4) already names, not a condition of the A291 merge. The rows are correctly replay-owned at `6e2504b1`.
4. **One genuine gap the round did not reach (finding F3, MATERIAL, K scope).** C1 satisfies neither the glossary (a single's parent is a Parent) nor INV-12's evident intent, yet the checker at `36e470ca` reported only INV-38 for it (P1): its INV-12 predicate (`tests/scored_roster_checker.py:558`, "single relation") accepts a single as a parent, exactly as the seal's `inv_12` does (l.264, `parent is not None`). Under the ruled text INV-12 alone is `OUT_OF_ROUND`, so the round result is unchanged, but the checker is supposed to be the independent oracle for INV-12 (C:485 "Chk: yes") and it shares the seal's blind spot. This must enter the INV-12 reconciliation queue as its first item.
5. **Typed-code conformance (finding F4, MATERIAL, harness gate scope).** The contract lists refusal codes `inv_23`, `inv_36`, `inv_37` (C:545, 613, 620) and the packer at `6e2504b1` has no such codes (P3); the refusals that actually fire are `inv_38`/`inv_39`. Whether K's harness witnesses for those rows assert the row code or the replay code is a gate-item (1)/(2) question I could not verify in budget. It is not a forger-round question and does not change U2, but it must be answered in the record before the final pass (§3.4 text (c)).

### 3.4 Ruled texts

**(a) Disposition of the nine (replaces nothing; implements `ex-95-texts-r4b.md:27` "recorded as OUT_OF_ROUND with its constructor and full checker row set, queued for the INV-12 reconciliation rule").** The gate record lists C1, C2, C2b, C3, C4, C5, C6, C7, C8 each with: constructor (`ex-104-fc-report.md` verbatim), seal result `ACCEPTED`, oracle `[]`, checker rows exactly as `ex-104-fc-adjudication.jsonl`, the seat's rationale verbatim, the judge's refutability verdict "not refutable" (§3.2), and the production refusal code from P2 (`inv_38` or `inv_39`). All nine are queued for the INV-12 reconciliation rule; C1 is queued first with the note "checker INV-12 predicate accepts a single as parent (`scored_roster_checker.py:558`); seal `inv_12` likewise (`scored_packer.py:264`)".

**(b) Oracle-gap rule (replaces `ex-101` F2's requested rule; requested here as a new rule for the same separately convened question).** "An accepted candidate is `OUT_OF_ROUND` only if (1) the oracle reports nothing and the checker reports neither INV-10 nor INV-11, **and** (2) `_replay_roster(registration, candidate)` at the integrated head refuses it. An accepted candidate meeting (1) that `_replay_roster` accepts is `ESCAPE` (production gap) and the stop rule applies, whether or not the magistrate can refute the seat's rationale. The record states the replay result for every accepted candidate." Reason: `ex-101` F2's text ("cannot refute the rationale → ESCAPE") would convert all nine present candidates into escapes and stop the lane for shapes that no public entry admits (P2); the discriminating fact is whether production refuses, not whether the magistrate can argue.

**(c) Typed-code line (record item before the final pass).** K's report states, for each of INV-23, INV-36, INV-37, INV-38, INV-52, the witness form actually asserted at the `requeue_overrun` entry path and the refusal code it asserts; where the asserted code is `inv_38`/`inv_39` rather than the row's listed code, the record says so in one line per row. If any of the five has no entry-path witness, that row is an open gate-item (1) defect, not a forger-round matter.

Deciding exhibits and probes: `ex-104-fc-adjudication.jsonl` (reproduced, P1); P2 table; `6e2504b1:joulewise/scored_packer.py` l.282–290, 413–414, 471–493; contract C:376, 423, 471–489, 545–644; `ex-95-texts-r4b.md:27`.

## 4. U3 — anything else before the final pass

1. **Gate item (2) result must be exhibited, not asserted.** The charge says the full suite "is running". Round 3 passes only when (1)–(4) all pass (`ex-95-texts-r4b.md:27`); a `COMPLETED_NO_ESCAPE` obtained before (2) is GREEN is not a pass. The final-pass packet must carry the suite's summary line with revision and time pin (NIT if present, BLOCKER if the final pass proceeds without it).
2. **Gate item (1) is asserted by the charge only** ("GREEN (bench)"); same requirement, same tiering.
3. **Contract copy pin.** The forger's `CONTRACT-v4.1.md` is blob `b4b1b176` (§1.3); the record should state that digest so "the amended 02d" resolves to bytes (NIT).
4. **Convene-message revision pair** (`0fa4e6e3`/`24ff94cb`) is the packet-101 pair, stale for this packet; harmless because both pairs exist, but the convene template should take the pair from the charge (NIT).

## 5. Findings (tiered; severity independent of verdict)

**F1 — MATERIAL (cured by §2.3).** R4-5(4) as amended by `ex-101` cannot pass as written: seat F-A is escalated with no successor named. Until §2.3 is adopted, item (4) is undecidable.

**F2 — MATERIAL (packet hygiene, U1).** The vendor-refusal cause is exhibited only as a two-line magistrate paraphrase (`ex-103`) with no log path, digest or line range (charter §7: derived claims need reproducible lineage). The proved fact is two `INCONCLUSIVE` runs (`ex-103b`), which is enough for U1; the cause enters the record only under §2.3(d).

**F3 — MATERIAL (checker gap, K scope; outside the round).** Checker INV-12 accepts a single as a single's parent (P1, C1 → INV-38 only), matching the seal's `inv_12` blind spot (l.264) and contradicting the glossary (C:63–64). Round result unchanged (INV-12 alone is `OUT_OF_ROUND`); first item of the INV-12 reconciliation queue (§3.4(a)).

**F4 — MATERIAL (typed-code conformance; harness gate scope).** Contract rows INV-23/36/37 list refusal codes the packer does not contain (P3); production refuses via `inv_38`/`inv_39`. Not a forger-round matter; must be stated per row before the final pass (§3.4(c)).

**F5 — NIT (charge premise).** "The seal is meant to refuse contract violations 'before derived arithmetic'" is quoted as if contract text; it is not (P4). The ruling on U2 rests on INV-40, FT-8 and Q16 instead.

**F6 — NIT (convene hygiene).** Convene message revision pair stale (§1.2); judge launched from a JouleWise worktree, so memory index and CLAUDE files were injected (§0). Same cure as `ex-101` F5.

**F7 — NIT (record).** `ex-104-fc-report.md` first line lists `~/.claude/CLAUDE.md` as auto-loaded; `ex-101` §2.3(iii) tolerates user-global files "the launcher cannot remove", so F-C is not contaminated. The record should say this explicitly rather than leave it to inference.

## 6. Disagreement with the lead's disposition

The charge labels no preferred option on U1 or U2. On U2 the charge's background paragraph adopts the seat's own diagnosis ("the exposure is the seal alone … replay catches the cases re-checked") for two candidates; I extended that to all nine by probe (P2) rather than rely on it. I disagree with the framing that these rows might "have to become seal-owned before A291 can merge": the contract assigns no such requirement (§3.3.1). I reject `ex-101` F2's oracle-gap rule as drafted (§3.4(b)).

## 7. One-line result

U1: REJECT F-C-alone and Sol 6.0; RULED F-B = second fresh Fable 5.1 seat, isolated per ex-101 (iii), brief ex-102 verbatim, item (4) = F-B ∧ F-C `COMPLETED_NO_ESCAPE`, F-A cause to be exhibited from the log. U2: AFFIRM all nine `OUT_OF_ROUND` (adjudication reproduced); none refutable from the contract; NOT seal-owned before merge, replay-owned per INV-40/FT-8, all nine refused by `_replay_roster` and `verify_executed_roster` at `6e2504b1`; ex-101 F2 rule REJECTED, replaced by the replay-conditioned rule §3.4(b); checker INV-12 single-as-parent gap queued first. U3: exhibit items (1) and (2) with pins before the final pass. Findings F1–F4 MATERIAL, F5–F7 NIT, no BLOCKER.
