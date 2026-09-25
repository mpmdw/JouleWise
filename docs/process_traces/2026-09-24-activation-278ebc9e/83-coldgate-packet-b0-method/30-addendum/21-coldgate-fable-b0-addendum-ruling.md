# Cold-gate ruling — B0-ESC-01 addendum (Fable 5.1, cold judge)

Judge: Claude Fable 5.1, fresh non-interactive session, 2026-09-24 17:19–17:4x PDT, worktree `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-b0b` at `d71bad59`. Foreground only; no subagents, no background tasks, no sudo/launchctl/powermetrics/systemsetup; no discovery suite; no write other than this file. Nothing armed.

## 0. Disclosure and trust anchors

**Auto-loaded before I acted (harness injection, not opened by me):** `/Users/edr/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (truncated by the harness). None was used as evidence or authority. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, any memory file, any process trace outside `…/83-coldgate-packet-b0-method/30-addendum/`. I did not open `/tmp` archives; every code fact below comes from `git show <rev>:<path>` in this worktree.

**Validator run 1 (deliberate typo):** expected charter `…c95d82`, observed `099de884…c95d81`; packet expected = observed `9f27e42e…31c4c` → `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2.
**Validator run 2:** expected charter `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` = observed; packet expected = observed `9f27e42e3efffb5b8601d085088fbccea011afcc2373fa970920bcfa2ca31c4c`; all 4 exhibit digests observed = expected; `result: PASS`, rc=0, schema `coldgate-validator-receipt/v2`.
**Independent method:** `shasum -a 256` on both files reproduced both digests. `git cat-file -t` confirms `2ea6a7ec`, `7647bb2e`, `bee658c5`, `eb8d745f` are commits; `feat/2026-09-24-a280-b0-kind-dispatch` = `bee658c5`, `test/2026-09-24-b0-idle-parity` = `eb8d745f` (local and origin).

## 1. Executed probes (primary evidence)

| # | Probe | Result |
|---|---|---|
| E1 | `2ea6a7ec:joulewise/evidence_night.py:296-297` | base `notice_subject` uses `kind_row(KIND)`; it never touches `state["kind"]`. |
| E2 | Refuter V1 re-executed by me (base function extracted by `ast`, `KIND`/`kind_row` stubbed) | idle subject for `kind` = `"calibration"`, `[]`, `"test_night"`, `None`, and key absent. F3's factual premise holds. |
| E3 | `2ea6a7ec:joulewise/evidence_night.py:371-404` | base `prepare` refuses `kind != KIND` (`:374`), then writes `state = dict(schema=SCHEMA, kind=kind, …)` (`:404`) into `prepare.json`. `state["kind"]` is therefore a **base-authored field of the sealed preparation state**, not a new field. |
| E4 | `2ea6a7ec:joulewise/evidence_night.py:586-595` | base `candidate_state` reads `prepare.json` and refuses `state.get("kind") != KIND` with "candidate is not a completed, owned preparation". |
| E5 | `2ea6a7ec:joulewise/evidence_night.py:306,322,352-353` | base `render_notice` **reads** the registration bytes and the plan text, and prints `bindings["chain_source_path"]`/`_sha256` from `state` without reading the source. |
| E6 | `2ea6a7ec:joulewise/evidence_night.py:1057-1068` | base `candidate_payload_kind` **reads** custody `chain.zsh` and returns `probe_payload_kind(...)`. It exists at base (also `clone_census` at `:1026`). |
| E7 | `bee658c5:joulewise/evidence_night.py:311-337,340-348,639,669-673,689` | `selected_candidate_row` reads `chain.zsh`, `chain.zsh.sha256` and the source at presentation time (M1); `NIGHT_KINDS.get(state.get("kind"))` at `:639` (M4); `:689` runs the selector before `checkout_ok` (M2). Refusal text "no approved evidence handler" exists at `:253,:348,:671,:673`. |
| E8 | `bee658c5:tests/test_night_kinds.py:409-467` and `:561-602` | both third-row witnesses build `state` **without a `kind` key** and expect `notice_subject`/`render_notice` to select `TEST` from custody `chain.zsh` + `bindings`, then refuse after chain/source drift. F1's factual premise holds. The first witness also expects `prepare(kind="test_night")` → "invalid or unresolved kind" and `candidate_state` → "completed, owned preparation". |
| E9 | `joulewise/night_kinds.py`: `handler` field count = 0 at `2ea6a7ec`, 4 at `7647bb2e` and `bee658c5` (`:47` default `None`, idle `:86` `"evidence"`, calibration `:123` `"calibration"`) | `handler` is a round-0 addition; the calibration row **has** a handler. Base table has exactly two rows (`2ea6a7ec:joulewise/night_kinds.py:48-87`). |
| E10 | `eb8d745f:tests/parity/b0_corpus.py:18,20,31,49-79` | `kind` axis = idle/list/object/integer/null/unknown/calibration/missing; no `test_night` anywhere; 28 operations incl. `evidence.clone_census`, `evidence.candidate_payload_kind`, `diagnostic.custody_row`. F4's premise holds. |
| E11 | `eb8d745f:tests/parity/b0_runner.py:680-681,712-714,838-841,860-862` | classification and `parity_failed` as ex-20 states; `diagnostic.custody_row` reports `absent_at_base` when `_custody_row` is missing. |

## 2. Q1 — amend BOTH brief 10's third-row obligations AND R1/R4/R5; do not PARK

**Root of F1.** Brief 10 §1(a) forbids "a bare `state["kind"]`" as a second authority, and the round-1 seat obeyed it by inventing `selected_candidate_row` (E7), which is the M1 mechanism behind two-thirds of the outcome mismatches. E3–E4 show the premise of §1(a)'s example is false: `state["kind"]` is written by base `prepare` after base's own kind refusal and is checked by base `candidate_state`. It is the sealed preparation's own field, not a new one. The bindings (E5) remain the authority for any non-base output. So the cure is to amend §1(a)'s example, keep its intent (no escalation from a state field), and amend R1 so that new authentication reads happen only on the non-base branch. The bee658c5 witnesses (E8) are round-1 artifacts inside P's WRITE_SCOPE, not brief text; they must carry the `kind` hint.

**F2 — MATERIAL, not BLOCKER.** §1(d) names installer/driver/`zero_capture_facts` sites, not the presentation sites; §1(a) says a handler-less non-idle kind "refuses exactly as today", and today `notice_subject` succeeds (E1–E2). Calibration has a handler (E9), so it is not "a row with no approved handler". The conflict is definitional; it is cured by defining the phrase.

**F3 — BLOCKER by consequence.** R4 as written invents a refusal at sites where base has none (E2); P following it would burn the single licensed round on a G1 red (`kind=list` is a corpus axis, E10). Refuter's replacement text AFFIRMED with one tightening: a non-string is simply the selector returning `None`.

**Missed by the charge and by both sides — MATERIAL.** R1's sentence "perform NO filesystem read" and G3's "presentation functions contain no `read_text`/`read_bytes`/`open` call" are **unsatisfiable against base**: base `render_notice` reads registration and plan (E5) and base `candidate_payload_kind` reads `chain.zsh` (E6). Applied literally they force a behaviour change at two base sites (a G1 red or a NEEDS_RULING). Cured in R1b and G3b below.

**Verdicts.** F1 AFFIRMED as BLOCKER (cured below, with the witness amendment the refuter's own text lacks: a "hint from existing state fields" does not exist in E8's states). F2 re-tiered MATERIAL. F3 AFFIRMED BLOCKER. F4, F5, F6 AFFIRMED MATERIAL; texts below. PARK REJECTED: the defects are text defects curable here, the fix runs on a branch (reversible), and charter §9's redesign requirement is already met.

### Exact amendments to brief 10 (P and K read these as overriding the quoted sentences)

> **A1 (replaces §1(a) sentences 3–4, "The kind must come … not acceptable, because it would create a second authority.")**
> The kind selector at every `evidence_night.py` site is the `kind` field of the preparation state that base `prepare` writes into `prepare.json` (`2ea6a7ec:joulewise/evidence_night.py:404`) and base `candidate_state` checks (`:593`). The selector grants no authority: a selector value in `BASE_KINDS` or `None` runs the unchanged base path; a selector value outside `BASE_KINDS` may produce row-specific output only after the custody wrapper `chain.zsh`, its `.sha256`, and the row's chain source have been authenticated against `state["bindings"]["chain_source_path"]` and `["chain_source_sha256"]`, and otherwise refuses typed. Those authentication reads live only on the non-base branch.

> **A2 (appended to §1(d))**
> "A row with no approved handler" means: `row is None`, or `row.handler is None`, or `row.handler` names no dispatch target at that site. The `calibration` row (`handler="calibration"`) takes the base calibration path at these sites, unchanged. `BASE_KINDS` never take a typed no-handler refusal anywhere.

> **A3 (appended to §1(f), first bullet)**
> Every third-row witness supplies `"kind": <third.kind>` in each `state` mapping and in each `prepare.json` it writes. A witness state lacking `kind` must produce base bytes, never third-row output. Adding a third-row row-specific output that is reachable without the authenticated wrapper/source is a failure of the witness.

### Exact rule texts (replace R1, R4, R5; R2 and R3 stand with the one addition shown)

> **R1b (one total selector per surface, reads nothing new).** Each surface obtains its row through one function `select_kind(state) -> str | None` that (i) reads nothing: it returns `state.get("kind")` if that value is a `str`, else `None`; (ii) never raises. Sites that at `2ea6a7ec` read `prepare.json` (`candidate_state`, `uninstall`, `veto`, `verify`) read it exactly as base did and pass the resulting mapping to `select_kind`. Presentation functions (`notice_subject`, `render_notice`, `clone_census`, `notice_unused`, `candidate_payload_kind`) perform no filesystem read that `2ea6a7ec` does not perform at the same site, in the same order (base `render_notice` reads registration then plan; base `candidate_payload_kind` reads `chain.zsh`; the others read nothing). Cleanup takes its kind from the C5 receipt object that `_evidence_cleanup_error` already parses with `json.loads(read_bytes())`; `_custody_row` is DELETED. Wrapper/sidecar/source authentication for `BASE_KINDS` happens only where base already performed it (`sealed_candidate`, `sealed_state`, gate C5/C3, installer receipt validation), in base order. Authentication for a kind outside `BASE_KINDS` happens inside that kind's branch only, per A1.

> **R2 (unchanged) plus:** `BASE_KINDS` is defined once in `joulewise/night_kinds.py` as `BASE_KINDS = frozenset({"quiet_predicate_evidence", "calibration"})` and is an allowlisted literal in `tests/test_kind_dispatch_literals.py`.

> **R3 (unchanged) plus:** for a kind outside `BASE_KINDS` the non-base branch runs the base checks in base order with the row's fields substituted for idle constants, then refuses `Refused("<site> has no approved evidence handler")` when `row.handler != "evidence"`, using the exact `<site>` prefixes already present at `bee658c5:joulewise/evidence_night.py:253,348,671`. `notice_subject` for a non-base row needs no handler (it formats the row's label after A1 authentication).

> **R4b (type before lookup).** `select_kind` returns `None` for any non-`str` `state.get("kind")`. A `None` selector executes that site's exact base path, including its base success or base refusal. No refusal may be invented at a site where base has none.

> **R5b (legacy boundary).** An operation that at `2ea6a7ec` succeeded without authenticated kind evidence keeps that exact result for `BASE_KINDS` and for `None`. This is an explicit exception, for those legacy operations only, to any reading of brief 10 §1(d) that would require a typed refusal there. The exception grants nothing: such an operation can never select a handler outside `BASE_KINDS`, arm, acquire a ruled registration digest, or grant successor release. Newly admitted operations and rows outside `BASE_KINDS` without a handler refuse typed.

> NEEDS_RULING, not a silent change, if any base text, base order, or base file effect must change to satisfy A1–A3 or R1b–R5b.

## 3. Q2 — PARK not ruled; conditional disposition if the stop rule parks later

Not applicable now. If G1 is red after round R2b and B0 parks: (1) unpark condition = a written magistrate ruling, presented to Ed, that fixes the scored row's `NightKind` fields (after A291 round 3 and the AP-5M v5 draft settle) AND extends the `eb8d745f` corpus with a third-row `kind` axis, citing both by commit sha; (2) branch `feat/2026-09-24-a280-b0-kind-dispatch` stays unmerged and unrebased at its last commit, tagged `park/b0-<sha8>`; nothing on it is cherry-picked to main; (3) `test/2026-09-24-b0-idle-parity` at `eb8d745f` stays frozen as the oracle of idle bytes at `2ea6a7ec` and is re-based to a new main only by a new ruling with a fresh base-vs-base `0/0` run.

**Standing — REFUSE (same defect as ex-20 P4).** "B0 has no granted standing under R-A280" appears only in the charge narrative; no exhibit quotes COUNCIL-407-01 R-A280 by revision and line. Minimum cure: that excerpt. Charter §9: nothing here lifts a governed refusal of standing; the round runs on a branch; the merge stays blocked until standing is shown granted or lifted by its issuer.

## 4. Q3 — Final texts B0-R2b (paste verbatim; harness decides wherever it can)

1. **Title:** "B0-R2b redesign (d) — idle-default routing by the preparation's own `kind` field, base code for base kinds; acceptance = eb8d745f parity harness G1".
2. **Brief 10 amendments A1–A3** exactly as in §2.
3. **Rules R1b, R2(+), R3(+), R4b, R5b** exactly as in §2.
4. **Gates.** G1, G2, G5, G6 exactly as in ex-20 §P2. Replacements:
   > **G0 (before P is commissioned; replaces G8).** K lists, per `driver.*` and `installer.*` operation in `eb8d745f:tests/parity/b0_corpus.py:49-79`, the exact corpus case ids whose base-side observation reached the calibration branch (`wrapper="calibration"` with a coherent `c5="calibration"` receipt, and a base result that is neither a kind refusal nor `TypeError`). Any required operation with zero such cases → NEEDS_RULING to the magistrate before P starts. K pastes the list in its report.
   > **G3b (shape).** Every `Refused(`/`ValueError(`/new refusal code added in `git diff 2ea6a7ec..<FIX_HEAD>` sits inside a branch guarded by `kind not in BASE_KINDS` (or `row.handler` on that branch); `_custody_row` absent from `<FIX_HEAD>`; for each presentation function in R1b, `git diff 2ea6a7ec..<FIX_HEAD>` adds no `read_text`/`read_bytes`/`open`/`Path(...).read` call outside a `kind not in BASE_KINDS` branch. K checks by reading the diff and pastes the hunks.
   > **G4b (third-row witnesses).** K runs `tests/test_night_kinds.py` third-row tests at `<FIX_HEAD>`; K reads `git diff bee658c5..<FIX_HEAD> -- tests/test_night_kinds.py` and confirms the only changes to the two witnesses at `bee658c5:435-467,584-602` are (a) adding `"kind": third.kind` to state dicts and `prepare.json` payloads, (b) refusal-text changes P lists in its report by old→new pair. K adds, in a `/tmp` scratch copy only, two witnesses and pastes their tails: (i) `kind="test_night"` hint with the idle wrapper/source bytes → typed refusal, never idle output; (ii) idle `kind` (or no `kind`) with third-row wrapper bytes → bytes equal to base. P may add tests; P may not delete or weaken any assertion in the two pinned witnesses.
   > **G7b (mutations, K only, in disposable `git archive <FIX_HEAD>` copies under `/tmp`; diagnostic, never replacing the committed-sha G1 run).** (i) hard-code idle at one site → a third-row witness fails; (ii) move one non-base check ahead of `checkout_ok` in `sealed_state` → G1 fails. Commands and failing test ids pasted.
5. **Seats** exactly as ex-20 §P3, with these sentence replacements: "K performs G7b mutations only in disposable `/tmp` archives. The lead commits K's report after reviewing it; K commits nothing." **Stop rule:** "If G1 is red after this one round, PARK B0 under §3 above. A per-surface slice requires a new written magistrate ruling and counts as a new round; this text grants no automatic exception."
6. **Order of operations:** G0 → P commissioned → P commits `<FIX_HEAD>` → K runs G1–G7b → lead commits K report → merge gate (ex-20 §P3 unchanged, plus standing clause).
7. **Standing clause (unchanged):** "Merge blocked until COUNCIL-407-01 R-A280 standing is shown granted or lifted by its issuer, cited by revision."

## 5. Findings (tiered; severity independent of verdict)

| Tier | Finding | Deciding evidence | Cure |
|---|---|---|---|
| BLOCKER | F1: brief 10 §1(a) example + bee658c5 witnesses (no `kind`) vs R1 selector; the refuter's own F1 text does not cure it (no hint field exists in E8's states) | E3, E4, E8 | A1, A3, R1b |
| BLOCKER | F3: R4 invents a refusal where base succeeds; `kind=list` is a corpus axis, so the one licensed round would go red | E2, E10 | R4b |
| MATERIAL | Missed: R1 "NO filesystem read" and G3 read-ban are unsatisfiable against base `render_notice` and `candidate_payload_kind` | E5, E6 | R1b, G3b |
| MATERIAL | F2: "no approved handler" undefined; calibration has a handler; §1(d) does not cover presentation sites | E9, brief §1(a)/(d) | A2, R5b |
| MATERIAL | F4: G4 does not pin witnesses; corpus has no third row | E8, E10 | G4b |
| MATERIAL | F5: read-only K asked to mutate; committer unnamed; automatic slice exception | ex-20 §P3 text | item 5 |
| MATERIAL | F6: G8 undefined and post-hoc | ex-20 G8 "NOT VERIFIED" | G0 |
| NIT | ex-20 §1 says base `render_notice` "formats fields only"; it reads two files | E5 | wording only |
| NIT | Charge summary calls the refuter's F4–F6 "should_fix"; the refuter's table tiers them MATERIAL | ex-84b:37,123-128 | none |
| NIT | `handler` is not a base field; brief 10 §1(d)'s "approved handler" has meaning only from `7647bb2e` on | E9 | A2 covers it |

Packet hygiene: complete for the questions posed; the charge takes no position; both the ruling and the refuter are presented whole. No cherry-picking found. The standing premise remains unsupported (REFUSED above).

## 6. Not executed

- Full parity run on any candidate (none needed: no new candidate exists; ex-20's v3 counts were not re-derived).
- G0's calibration-case enumeration: assigned to K; NOT VERIFIED by me (E10 shows calibration values on the `wrapper`, `c5` and `kind` axes only).
- The 603-test module suite: NOT RUN.

Ruling stands as issued; override requires the charter §5 written override citing both sealed outputs.
