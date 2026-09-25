# Cold Fable gate ruling — A291-FORGER-01 (R4-5 item 4, forger seat family)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold session, no loop context, foreground only, no subagents, no background tasks. Started 2026-09-24 19:50:05 PDT; ruling written ≈19:57 PDT. Worktree `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-forger` at detached HEAD `ff915979`.

## 0. Disclosure of auto-loaded context

The harness injected three files before I acted, none requested by me: the global `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the project memory index `MEMORY.md` (partial; 6 lines truncated). The memory index is loop-context narrative of the kind charter §4 forbids (it contains lines about A291 state). I did not open any memory file, did not use the index or either CLAUDE.md as evidence or authority, and every load-bearing conclusion below cites an exhibit, a git object, or a probe I ran. See finding F5 for the convening-hygiene consequence.

Not read, by rule: CLAUDE.local.md (absent; convene script asserts it), RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory files, any `docs/process_traces` file outside the packet directory. The exhibit-provenance probe in §1.3 compared bytes of two tracked files programmatically without printing or reading their content.

## 1. Pre-merits verification (charter §9)

### 1.1 Charter and packet digests

| item | expected | observed | method |
|---|---|---|---|
| charter `docs/process/coldgate_charter.md` | `…c95d81` (supplied in the convene message, independent of the packet) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256` + validator receipt field `digests.charter_sha256` |
| packet `00-charge.md` | `a57922d6e81595d16e060d38c543d271fcfa972c14d457e17dd03853165b2a4e` | identical | same |

Validator run 1 (deliberate typo `…c95d82`): `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2. Validator run 2 (`…c95d81`): `result: PASS`, rc=0, schema `coldgate-validator-receipt/v2`, `judge_handoff_bound: false`, all three exhibit digests observed == expected (`f48180cb…9e65`, `14692d3a…8923`, `63787c28…9b87`), `exhibit_manifest_sha256 d1a0ff49…1913`. The packet's own charter pin (`packet_charter_pin_sha256`) equals the trusted value. Merits opened only after run 2.

### 1.2 Revisions cited by the convene message exist here

`0fa4e6e3` (2026-09-24 05:43 −0700, "A291 fix round 2 (K)…"), `24ff94cb` (12:43, "A291 ownership-forgery harness (tests only…) — deliberately RED"), `6e2504b1` (18:51, "A291 round 3 seat P: R4-2 tests…"). `git cat-file -e` confirms `joulewise/scored_packer.py`, `tests/scored_ownership_oracle.py`, `tests/scored_roster_checker.py`, `tests/test_scored_ownership_forgery.py` all exist at both `24ff94cb` and `6e2504b1`. (They do not exist at this worktree's HEAD `ff915979`, which is a docs-pointer commit; nothing in T1 needed them.)

### 1.3 Exhibit provenance (charter §4 excerpt rule)

The exhibits carry no source-path / revision / line-range header. I cured this myself without reading the sources: a Python probe loaded `HEAD:docs/process_traces/2026-09-24-activation-278ebc9e/95-a291-final-texts-r4b.md` and `…/85-a291-final-texts-r4.md` into memory and tested whether each exhibit (minus its trailing `## 5.` marker line) is a substring. Result: `ex-95-texts-r4b.md` = bytes 0–6707 of a 6745-byte, 29-line file (lines 1–27 verbatim; the file's last commit is `c1985de2`, 2026-09-24 18:03 −0700); `ex-85-texts-r4.md` = bytes 0–8702 of an 8740-byte, 23-line file (lines 1–21 verbatim). Each exhibit is therefore the complete "Final texts" section of its source, not a selective quotation. The excerpts are admissible under §4 because their exact words (the family clause) are the object of T1.

### 1.4 The charge's factual premises

- "No third family is available": PROBED. `which` finds only `claude` (`~/.local/bin/claude`) and `codex` (`/opt/homebrew/bin/codex`); no `gemini`, `ollama`, `llama`, `mistral`, `grok`; `~/.local/bin` holds only claude/codex wrappers. Premise holds for this machine at 19:51 PDT.
- "P is Opus 5.5 (Claude family), K is Sol 6.0 (Codex family)": NOT independently verifiable from the packet (no seat manifest exhibited). It is consistent with the ruled seat constraints in `ex-95-texts-r4b.md:23` ("the harness author is Codex-family (ex-81b); P is neither that seat nor that family; K is not P's family"), which force P ∉ Codex family and K ∉ P's family. I rule conditionally on this premise and require it to be recorded (ruled text, clause (v)).
- "(1) harness GREEN … (3) all five mutants killed at the reference counts": (3) verified against `ex-100b-mutation-kills.md:30,38,46,54,62` (45, 2, 276, 355, 184) and `:39,55,63` (named differences `B1-singles-voided → refused:stale_derived`, `B1 → accepted`, `B1, B2 → accepted`), matching the reference kills in `ex-95-texts-r4b.md:25` exactly; control `:21–23` GREEN with pairwise 0 and the seven ruled named outcomes. (1) is asserted by the charge only; not needed for T1. (2) is stated pending by the charge itself.

## 2. T1 — who is the forger seat

### 2.1 Verdict

**REJECT the literal text; RULE replacement text (option (c), two independent seats, both must reach `COMPLETED_NO_ESCAPE`).** Exact text in §2.3.

### 2.2 Reasoning, from the exhibits

The clause under rule is at `ex-95-texts-r4b.md:27`: "**Forger seat:** family neither P's nor K's, …". Read with `ex-85-texts-r4.md:21` (identical family words in R4) and the seat rule at `ex-95-texts-r4b.md:23`, the clause encodes two separate independences, each with its own reason:

1. **Independence from P.** The forger attacks `_seal(registration, roster, finalize=True)`, whose ownership view P wrote (`ex-85-texts-r4.md:7`, R4-2). A same-family attacker is the most likely to share P's picture of what a legal roster is and to miss the same forgery shapes. This is the independence the mutation step cannot supply: m1–m5 are fixed by rule (`ex-95-texts-r4b.md:25`), so the forger is the only open-ended adversary in the gate.
2. **Independence from K.** K wrote the operator vocabulary (`ex-85-texts-r4.md:12`, R4-3 item 3: `drop_terminal_entry`, `duplicate_terminal_entry`, `copy_item_into_live_block`, plus the pre-existing operators) and the oracle and checker that adjudicate the forger's candidates (`ex-95-texts-r4b.md:27`). The forger's value over the exhaustive pair/triple sweep (`ex-95-texts-r4b.md:3`) is precisely the forgery shapes that vocabulary does not compose. A same-family attacker is the most likely to reinvent K's operators rather than new ones.

With only two families on the machine (§1.4), one seat can satisfy at most one of these. Option (a) alone (Astra 6) keeps independence 1 and drops 2. Option (b) alone (fresh Fable 5.1) keeps 2 and drops 1, and drops the more important one: the code under attack is P's. Option (c) is the only choice that preserves both independences the clause was written to secure, at the price of one extra 30-minute read-only seat. The charter gives me no presumption toward the cheaper option (§1, §2), and the exhibits give no evidence that a second seat harms anything: both seats are `WRITE_SCOPE: []`, each in its own `/tmp` archive, and the stop rule already treats any escape as a design defect requiring a consult (`ex-95-texts-r4b.md:27`), so two seats cannot produce conflicting remedies. Option (d) (a third family) is unavailable; "different model, same vendor" is the closest available approximation and I define family that way in the text so P and K can apply it without choosing.

Why "both must reach `COMPLETED_NO_ESCAPE`" rather than "either": the gate's existing semantics make a single `INCONCLUSIVE` non-passing (`ex-95-texts-r4b.md:27`); a two-seat gate that passed on one seat would be weaker than the one-seat gate it replaces. The conjunction keeps the gate at least as strong as either single-seat reading.

Why the Fable seat must be a **fresh headless session launched from the `/tmp` directory**: this very session demonstrates that a Claude session launched from a JouleWise checkout receives the project memory index unrequested (§0). A forger that has been told the named witnesses through memory or CLAUDE files is not "told nothing of the named witnesses". The launch conditions in clause (iii) are the minimum that make the "told nothing" requirement true in fact rather than in the brief.

### 2.3 Ruled text

**The family clause of R4-5 item (4) at `ex-95-texts-r4b.md:27` — the words "family neither P's nor K's," — is replaced by the following. Every other word of R4-5(4) stands verbatim, except the four conforming edits enumerated in (vii), which are required to make two seats implementable.**

> **Forger seats (two, independent):** because only two model families are available on the bench (Claude: Opus 5.5, Fable 5.1; Codex: Sol 6.0, Astra 6), "family" below means vendor family and "model" means the named model id. The gate runs two forger seats:
>
> (i) **Seat F-A:** model Astra 6 (Codex family, a model different from K's). Launched by the audited exec route with `WRITE_SCOPE: []`, cwd `/tmp/forger-<activation>-astra/`.
>
> (ii) **Seat F-C:** model Fable 5.1 (Claude family, a model different from P's). Launched as a fresh headless session with `WRITE_SCOPE: []`, cwd `/tmp/forger-<activation>-fable/`.
>
> (iii) **Isolation, both seats.** Each seat's directory holds exactly: `git archive <integrated head>` with `tests/` removed, the amended 02d, the glossary, and a runnable Python (unchanged from R4-5(4)). Neither directory is under any JouleWise checkout, worktree, or memory-keyed project path; no `CLAUDE.md`, `CLAUDE.local.md`, `.codex/`, `.claude/`, `.mcp.json` or memory directory is present in or above it other than the user-global ones the launcher cannot remove. The seat's first output line lists every file auto-loaded by its harness; if that list names any file under `docs/process_traces/`, `docs/process/`, a memory directory, RUN_STATE, TASK_QUEUE, or a council log, the magistrate records the seat `INCONCLUSIVE` (contaminated) without reading its candidates, and reruns it once under corrected launch conditions. Neither seat sees the other's directory, brief, candidates, or result; neither seat calls any other model.
>
> (iv) **Brief, both seats.** Identical text, the R4-5(4) charge verbatim: "compose a roster with forged ownership or formation that `_seal(registration, roster, finalize=True)` accepts"; 30 min wall each; told nothing of the named witnesses, the operators, the mutants, or the other seat; returns constructor code and seal results.
>
> (v) **Record.** The gate record states, for P, K, F-A and F-C, the model id and launch route as taken from each seat's launch manifest or report header (not from the brief), and asserts in one line: P ∉ Codex family; K ∉ P's family; F-A's model ≠ K's model; F-C's model ≠ P's model. A false or absent line is a gate failure.
>
> (vi) **Verdict aggregation.** Each seat is adjudicated separately under the unchanged R4-5(4) definitions (`ESCAPE`, `OUT_OF_ROUND`, `COMPLETED_NO_ESCAPE`, `INCONCLUSIVE`), candidates from both seats adjudicated by the same magistrate with the same oracle and checker at the same integrated head. Item (4) is `COMPLETED_NO_ESCAPE` only when both seats are `COMPLETED_NO_ESCAPE`. An `ESCAPE` from either seat is an escape under the unchanged stop rule. The rerun rule applies per seat: one `INCONCLUSIVE` on a seat reruns that seat once with a fresh session of the same model; a second `INCONCLUSIVE` on the same seat escalates. The two seats may run concurrently.
>
> (vii) **Conforming edits to the standing R4-5(4) words.** (1) "in `/tmp/forger-<activation>/`" reads "in the seat's directory named in (i)/(ii)". (2) "`COMPLETED_NO_ESCAPE` = the seat completed and every submitted candidate was adjudicated with no `ESCAPE`" is read per seat, with the item-level result given by (vi). (3) "one `INCONCLUSIVE` reruns once with a fresh seat, a second escalates" is read per seat as in (vi). (4) "Round 3 passes only when (1)–(3) pass and (4) is `COMPLETED_NO_ESCAPE`" is unchanged in words; "(4) is `COMPLETED_NO_ESCAPE`" means the aggregate of (vi).

Deciding exhibits: `ex-95-texts-r4b.md:23,27`; `ex-85-texts-r4.md:7,12,21`; probe §1.4 (no third family on the machine).

## 3. Findings (tiered; severity independent of verdict)

**F1 — BLOCKER (cured by §2.3).** R4-5(4) as written cannot be executed: the family clause has no satisfying seat on this machine (§1.4 probe). Until the replacement text is adopted, round 3 cannot pass by its own terms (`ex-95-texts-r4b.md:27`, "Round 3 passes only when (1)–(3) pass and (4) is `COMPLETED_NO_ESCAPE`").

**F2 — MATERIAL (missed by the charge; outside T1, a new rule is requested, not ruled).** Under the unchanged R4-5(4) text, a forger candidate that `_seal(finalize=True)` accepts and on which the oracle reports nothing and the checker reports neither `INV-10` nor `INV-11` is `OUT_OF_ROUND`, "not an escape" (`ex-95-texts-r4b.md:27`). The forger's own stated forgery mechanism plays no part in that classification. The oracle therefore caps the forger's power: a real forgery that the oracle also misses is filed, not stopped. This is exactly the class of defect the forger seat exists to find, since K wrote both the oracle and the operators (§2.2 point 2). Requested rule, for a separately convened question: "For every `OUT_OF_ROUND` candidate the record includes the seat's stated forgery rationale verbatim. If the magistrate cannot refute that rationale from the amended 02d text by cited clause, the candidate is classified `ESCAPE` (oracle gap) and the stop rule applies." I do not adopt this here because the charge fixed T1's scope to the family clause and stated everything else stands.

**F3 — MATERIAL (premise, addressed by clause (v)).** The identities "P = Opus 5.5, K = Sol 6.0" are asserted by the charge without an exhibit. They are consistent with the ruled seat constraints (`ex-95-texts-r4b.md:23`) but unverified. The ruled text makes the gate record carry them from launch manifests, so the family arithmetic is checkable after the fact.

**F4 — NIT (packet hygiene).** The exhibits lack the charter §4 provenance header (source path, immutable revision, line range). I established completeness myself (§1.3: both exhibits are their sources' full "Final texts" section, lines 1–27 and 1–21). Future packets should state it so a judge on a tighter budget need not probe.

**F5 — MATERIAL (convening hygiene; no effect on T1's merits).** The convene script launches the judge from a JouleWise worktree, so the harness auto-loads the project memory index and both CLAUDE files (§0), which charter §4 forbids the judge to read. The judge cannot decline an injection. Minimum cure for future cold gates: launch with cwd outside any memory-keyed project path (for example a `git archive` under `/tmp` plus the packet directory copied in), or a launcher flag that disables memory and CLAUDE loading, and require the judge's disclosure line as this ruling gives it. Clause (iii) of the ruled text applies the same cure to the Fable forger seat.

**F6 — NIT (ordering).** The charge states gate item (2), the full discover suite, is pending. Nothing in R4-5 forbids running (4) before (2) completes; the ruled text does not change that. Round 3 still passes only when (1)–(4) all pass, so a `COMPLETED_NO_ESCAPE` obtained before (2) is GREEN is not a pass.

**F7 — NIT (informational, mutation exhibit).** `ex-100b-mutation-kills.md:29` shows m1 implemented as `(len(live) <= 1 and len(term) <= 1) and (not live or held)`, retaining the superseded/terminal conjuncts for the live case, rather than the bare count relaxation named in `ex-95-texts-r4b.md:25`. This is the narrower (harder to kill) mutant of the same clause and was killed at the reference count 45, so it does not weaken (3). Recording it so the gate record does not describe m1 as the bare relaxation.

## 4. Disagreement with the lead's disposition

The charge labels no preferred option, so there is no labeled disposition to concur with or reject; it presents (a)–(d) symmetrically. I note that the charge's background paragraph ("Read literally, the text cannot be satisfied") is argument that I verified by probe (§1.4) before relying on it.

## 5. Probes not executed

None of the probes I planned were cut for budget. I did not run the discovery suite, any test, `sudo`, `launchctl`, `powermetrics` or `systemsetup`; I did not touch the canonical root, night-custody, any measurement directory, or LaunchAgents; I wrote only this file.

## 6. One-line result

T1: REJECT literal clause; RULED option (c): two independent forger seats, Astra 6 (≠ K's model) and fresh Fable 5.1 launched from `/tmp` (≠ P's model), each `WRITE_SCOPE: []`, 30 min, isolated per §2.3(iii), item (4) passes only when both are `COMPLETED_NO_ESCAPE`; findings F1 BLOCKER (cured), F2/F3/F5 MATERIAL, F4/F6/F7 NIT.
