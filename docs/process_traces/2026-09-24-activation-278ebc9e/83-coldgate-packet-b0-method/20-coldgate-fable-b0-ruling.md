# Cold-gate ruling — B0-ESC-01 (Fable 5.1, cold judge)

Judge: Claude Fable 5.1, fresh non-interactive session, 2026-09-24 17:07–17:2x PDT, worktree `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-b0` at `18be79b9`. Foreground only; no subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup, no writes other than this file. Discovery suite not run.

## 0. Disclosure and trust anchors

**Auto-loaded before I acted (harness injection, not opened by me):** `/Users/edr/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (truncated). None was used as evidence or authority. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, any process trace outside the packet directory. Under `/tmp/278ebc9e/` I opened only the harness output archives `b0par-final-v3/{diffs.jsonl.gz,summary.json}` (primary artifacts named by exhibit 80b); the other files there (council/seat logs) were listed by `ls` and not opened.

**Validator, run 1 (deliberate typo):** expected charter `…c95d82`, observed `…c95d81`, packet expected = observed `e92031b3…dffd48` → `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2.
**Validator, run 2:** expected charter `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, observed identical; packet expected = observed `e92031b3280c8c91c5f6f418ffa2e58d91e0cd6a7b5107bfe922bb85a0dffd48`; all 14 exhibit digests observed = expected; `result: PASS`, rc=0, schema `coldgate-validator-receipt/v2`.
**Independent method:** `shasum -a 256` on both files reproduced both digests. Harness digests in `ex-80c-*` (`b0_corpus.py d9d72976…`, `b0_runner.py 2c3fbdac…`) match `git show eb8d745f:` of those files (verified); `tests/test_b0_idle_parity.py` at eb8d745f is `89b57cf5…9bc5`.

## 1. Executed probe: what the 19,615 outcome mismatches are

Source: `/tmp/278ebc9e/b0par-final-v3/diffs.jsonl.gz` (33,066 records; runner classification at `eb8d745f:tests/parity/b0_runner.py:838-841`: `outcome` = any non-`calls` field differs; `dependency_calls` = only the ordered call list differs; `new_private_api` = the `diagnostic.custody_row` entry point; `unauthenticated_selection` = the two F4 cases).

| Class | Records |
|---|---:|
| outcome | 19,615 |
| dependency_calls (extra/reordered reads, equal results) | 11,763 |
| new_private_api | 1,686 |
| unauthenticated_selection (72b.F4.bare_idle, bare_stripped) | 2 |

Outcome records partition into **four mechanisms with one root cause** (constant `KIND` lookups replaced by disk reads that can fail, run at places or in an order base never had):

| Mechanism | Operations | Outcome records | Signature (base → candidate) | Code |
|---|---|---:|---|---|
| **M1 presentation reads** | notice_subject 2,572; notice_unused 2,497; clone_census 2,572; render_notice 3,257; candidate_payload_kind 2,407 | **13,305 (68 %)** | base returns the subject / draft / pgrep argv / kind; candidate raises `Refused`: "candidate payload kind unreadable" 5,214, "candidate chain digest mismatch" 4,318, "candidate chain source unreadable" 1,959, "symlink/path collision" 1,287, "differs from sealed binding" 502 | base `2ea6a7ec:joulewise/evidence_night.py:296` formats fields only; head `bee658c5:…:341,346` call `selected_candidate_row(state)` |
| **M2 sealing reorder** | sealed_candidate 967; sealed_state 961; sealed_state_published 961 | 2,889 (15 %) | "sealed candidate failed wrapper sidecar" → "payload kind unreadable" (570) / "no approved evidence handler" (249); "sealed-byte drift" → "no approved evidence handler" (190+185); "dirty clone" → "differs from sealed binding" | `bee658c5:joulewise/evidence_night.py:689` runs before `checkout_ok` at `:691`; `:249` |
| **M3 cleanup second read** | driver.cleanup 1,111; courier_cleanup 1,083 | 2,194 (11 %) | return `None` → "evidence outcome/cleanup unavailable: ValueError: night payload kind unavailable" (563) / "night payload kind differs from authenticated receipt" (378); `night/refusal.json` and `evidence_outcome.json` written at base, absent at head (290/276) | receipt parsed by `json.loads(read_bytes())` at `bee658c5:scripts/run_night.py:1379`, then re-read as text in `_custody_row` at `:1009` |
| **M4 type before refusal** | prepare 210; uninstall 176; veto 150; candidate_state 150; verify (part of 399); prepare_fresh 2 | ≈ 690 (4 %) | `Refused(...)` → `TypeError` | `NIGHT_KINDS.get(state.get("kind"))` at `bee658c5:joulewise/evidence_night.py:639` |
| residual | installer.verify / receipt_validation | ≈ 540 | same texts as M1/M2 reached through the installer | same helpers |

The 11,763 `dependency_calls` records are the same root cause with equal results (e.g. `prepare.json` read twice plus `chain.zsh`, both sidecars and the source read where base read none). Answer to the charge's question: **not many mechanisms; four, one of which is two-thirds of the count, and all four are already-named findings** (Astra F1's notice_subject point = M1; 72b F2 = M2; 72b F1/F4 = M3; 72b F3 = M4). The mismatches are distributed by mechanism across surfaces, not concentrated in one surface.

## 2. Rulings

### P1 (design) — REJECT (a), REJECT (c), REJECT plain (b); RULE design (d): idle-default routing with base code for base kinds

- (a) "drive the harness GREEN" is the same-shape third round charter §9 forbids after two same-signature failures. REJECT.
- (c) per-surface PRs would not reduce the mechanism count (§1: every surface carries the same four); it only multiplies gate cycles. REJECT as the primary design; permitted only as the stop-rule fallback below.
- (b) plain "validate as base, then route" cannot admit the test-only third row (base validation hard-codes the idle literals) and, as Astra's executed notice_subject probe shows, base success does not always establish kind identity. It is a subset of (d). REJECT as written.
- **(d) AFFIRMED with the exact rules below** (Opus ex-79 Q2(d) Rules 1–4 plus Astra ex-78 R1's legacy-boundary ruling, which I now issue). Deciding exhibit: §1 partition; `2ea6a7ec:joulewise/evidence_night.py:586-593` shows base already reads `state.get("kind")` from `prepare.json` and compares it to `KIND`, so using that already-read field as a **selector with idle fallback** is not a new authority.

**Rule text (paste into the brief):**

> R1 (one total selector per surface, reads nothing new). Each surface obtains its row through one function that (i) reads only data the base already read at that site, with the base's parser and encoding, (ii) is wrapped so it never raises (`except Exception: return None`), and (iii) returns `None` whenever it is not certain. Presentation paths (`notice_subject`, `render_notice`, `clone_census`, `notice_unused`, `candidate_payload_kind`) take the kind from the `state` mapping they are given and perform NO filesystem read. `candidate_state`, `uninstall`, `veto`, `verify` use only `prepare.json` as base did. Cleanup takes its kind from the C5 receipt object `_evidence_cleanup_error` already parsed with `json.loads(read_bytes())`; `_custody_row` is DELETED. Wrapper/sidecar/source authentication happens only where base already performed it (`sealed_candidate`, `sealed_state`, gate C5/C3, installer receipt validation), in base order.
>
> R2 (base kinds run base code). `BASE_KINDS = frozenset({"quiet_predicate_evidence", "calibration"})`. If the selector returns `None` or a member of `BASE_KINDS`, the site executes the base code path with the base constants, in base order, producing base bytes and base refusal texts.
>
> R3 (new behaviour only outside BASE_KINDS). Only a kind outside `BASE_KINDS` reaches either (i) the same validation sequence driven by that row's fields, or (ii) the typed "no approved handler" refusal. Since the production table contains only `BASE_KINDS`, every new refusal text is unreachable in production. Where driving the checks from the row would reorder them, use an explicit `elif kind not in BASE_KINDS:` branch and leave the idle lines untouched (duplicated code in the new branch is accepted).
>
> R4 (type before lookup). `state.get("kind")` is checked with `isinstance(kind, str)` before any table lookup; a non-string falls to the base refusal text.
>
> R5 (legacy boundary, ruling on Astra R1). An operation that at `2ea6a7ec` succeeded without authenticated kind evidence keeps that behaviour for `BASE_KINDS`. This is a fixed legacy operation, not an inferred identity: it can never select a handler outside `BASE_KINDS`, arm, acquire a ruled registration digest, or grant successor release.
>
> NEEDS_RULING, not a silent change, if any base text, base order, or base file effect must change to satisfy R1–R5.

### P2 (harness as acceptance test) — write a different text

The charge's proposed gate ("zero outcome mismatches on the idle row, zero parity mismatches except named new-private-API diagnostics") is too weak in two places and undefined in one. Call-order and extra-read differences ARE parity violations for this PR: they are the exact defect class (a read base never did is a failure mode base never had), and the runner already treats them so (`parity_failed` at `eb8d745f:tests/parity/b0_runner.py:860-862`). The private-API carve-out becomes moot once `_custody_row` is deleted (the diagnostic op then reports `absent_at_base` on both sides, `:711-713`).

**Gate text G1 (paste verbatim):**

> G1. `python3 -B tests/parity/b0_runner.py --candidate-ref <FIX_HEAD_SHA> --output /tmp/278ebc9e/b0par-r2-<sha8>` from a clean `git archive eb8d745f` copy of `tests/parity/` and `tests/test_b0_idle_parity.py` (digests `d9d72976…f77e`, `2c3fbdac…e8e8`, `89b57cf5…9bc5` must match), run by the checker seat K, not the fix seat. PASS requires, in `summary.json`: `mismatches == 0`, `outcome_mismatches == 0`, `parity_mismatches == 0`, `new_private_api == 0`, `authority_failures == []`, `new_refusal_texts == []`, `observations == 99443`, `seed == 278097879`, plus `--self` on the same day giving `mismatches == 0`. The candidate is named by commit sha; a worktree path is not acceptable evidence. No text or path normalisation may be added to the runner.

**Additions (required):**
- G2 fuzz: each selector function from R1 called alone on ≥ 10,000 random byte strings and mutated wrappers never raises (report the command and count).
- G3 shape: every `Refused(`/`ValueError(`/new `refusal_code` added in `git diff 2ea6a7ec..<FIX_HEAD>` sits inside a `kind not in BASE_KINDS` guard; `_custody_row` absent; presentation functions contain no `read_text`/`read_bytes`/`open` call.
- G4 third-row unit tests (brief 10 §1(f)) route or refuse typed; unknown kinds refused (the harness cannot express a third row; only base kinds exist there).
- G5 `test_base_archive_byte_goldens` and `test_refusal_parity` green, expected bytes unchanged (`git diff 2ea6a7ec..<FIX_HEAD> -- tests/test_night_kinds.py` shows no golden edits).
- G6 baseline reconcile: the brief-10 V1 module suite at `<FIX_HEAD>` is green except tests that K shows failing at exact `2ea6a7ec` in the same environment on the same day, listed by test id (72b R1 names four).
- G7 mutations (both must be killed, commands pasted): (i) hard-code idle at one site → a third-row test fails; (ii) move one new check ahead of `checkout_ok` → G1 fails.
- G8 (calibration row): K confirms the corpus contains at least one valid-calibration seed case per `driver.*` and `installer.*` operation; if not, this is a NEEDS_RULING back to the magistrate, not a harness edit by P. (Whether it already exists: NOT VERIFIED by me; corpus axes at `eb8d745f:tests/parity/b0_corpus.py:18-31` include calibration values but I did not confirm a valid-calibration seed.)

### P3 (seats, scope, independence, gate before merge) — write a different text

> Seat P (fix, implementation genre): a different model family from the harness author of eb8d745f; effort highest available. Starts from `bee658c5` on `feat/2026-09-24-a280-b0-kind-dispatch`; reshapes to R1–R5; `WRITE_SCOPE` = brief 10's list verbatim, which excludes `tests/parity/*` and `tests/test_b0_idle_parity.py` (read-only; any edit = protocol failure). May run the harness locally; its result is not evidence. Returns NEEDS_RULING on any base-text/order/effect change. Wall 3 h.
> Seat K (checker, review genre, read-only, different family from P): runs G1–G8 on P's committed sha from a clean archive; pastes the full `summary.json`; runs the Opus-style contract lens by reading (R1–R5, G3). K's report is the merge evidence.
> Independence: harness frozen at eb8d745f before P starts; P never sees K's output; K never sees P's local harness runs.
> Gate before merge: G1–G8 PASS from K, plus `git diff --check 2ea6a7ec..<FIX_HEAD>` clean, plus the packet-committed K report. Merge remains a charter §3(3) trigger; this ruling does not pre-authorise the merge or waive any standing merge gate.
> Stop rule: if G1 is red after this ONE round, PARK (no round 4); do not split per (c) unless the red inventory is confined to one surface, in which case a single per-surface slice may be re-briefed with the cumulative corpus as gate.

This round is licensed under charter §9 **only because it is a redesign with a new acceptance test**; the brief must be titled "B0-R2 redesign (d)", not "fix round 2".

### P4 (proceed or park) — AFFIRM proceed on the merits; REFUSE the schedule comparison

Decidable from the packet: the harness exists and is self-consistent (base-vs-base 0), the redesign is fully specified, the cost is one seat plus one checker, and design (d) is neutral to whatever the scored row later looks like. Parking would let the branch drift from main and the corpus go stale. **Proceed with exactly one round.**

REFUSED part: "B0 is refused standing at COUNCIL-407-01 R-A280" and "waits on A291 and the headline redesign" appear only in the charge's narrative; no exhibit quotes them. Defect: unsupported premise; minimum cure: an exhibit quoting COUNCIL-407-01 R-A280 by revision and line range. Charter §9: if that is a governed verdict refusing standing, nothing here lifts it. The fix round runs on a branch (reversible) regardless; the **merge** is blocked until standing is shown granted or lifted by whoever issued it.

### P5 (anything else) — findings

| Tier | Finding | Effect | Cure |
|---|---|---|---|
| MATERIAL | `ex-80c-parity-summary-v3.json:candidate` is a worktree path, not a sha; the charge's "round 1 bee658c5" row is inferred from ex-80b's header, not pinned | P1 counts rest on an unpinned candidate | G1 requires `--candidate-ref`; K re-runs v3-equivalent by sha before P starts (≈ 5 min) |
| MATERIAL | 72b R1: the module suite is not green at base (4 failures, 1,648 s); ex-47b reports "603 OK" in a different environment | "V1 green" is environment-dependent | G6 as written; K lists the base-failing ids |
| MATERIAL | Astra R1 (legacy operations succeed without authenticated kind) was flagged `blocking` and left unruled through two rounds | contradictory obligations drove both same-signature failures | R5 issued above |
| NIT | Charge says "20 entry points"; coverage lists 28 operations, 20 with differences | none | say "28 operations, 20 differing" |
| NIT | `new_refusal_texts` carries 4 absolute fixture-path variants of one symlink text | report noise only | none required; do not normalise comparison |
| NIT | ex-80b `workspace.base_requested` is bee658c5 (branch base), while the oracle is 2ea6a7ec | reader confusion | brief wording only |

Packet hygiene otherwise: complete, both sides of each option presented, no cherry-picked excerpts found; the three consults are independent and reach compatible cures.

## 3. Final texts B0-R2 (paste verbatim into the fix brief)

1. Title: "B0-R2 redesign (d) — idle-default routing, base code for base kinds; acceptance = eb8d745f parity harness G1".
2. Rules R1–R5 exactly as in §P1.
3. Gate G1 exactly as in §P2, plus additions G2–G8.
4. Seats P and K, independence, merge gate and stop rule exactly as in §P3.
5. Standing clause: "Merge blocked until COUNCIL-407-01 R-A280 standing is shown granted or lifted by its issuer, cited by revision."

## 4. Not executed

- A fresh full harness run (≈ 270 s) was not executed; I analysed the committed v3 archive instead, whose harness digests match eb8d745f. A by-sha re-run is assigned to K (G1).
- G8's calibration-seed presence: NOT VERIFIED.
- The 603-test module suite: NOT RUN (out of scope for a cold judge).

Ruling stands as issued; override requires the charter §5 written override.
