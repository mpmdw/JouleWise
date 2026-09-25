# Cold Fable ruling — A291-PREMERGE-01 (packet 112)

Judge: Claude Fable 5.1, cold session, 2026-09-24 ≈21:15–21:45 PDT. Worktree `/Users/edr/code/JouleWise-wt-coldgate-278ebc9e-premerge` at `cb00fd66`, clean. Read-only apart from this file; nothing armed; no sudo/launchctl/powermetrics/systemsetup; no subagents or background tasks.

## 0. Disclosure, trust anchors, method

**Auto-loaded before I chose anything:** `~/.claude/CLAUDE.md` (global rules), the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (index lines only). None of them was used for any ruling below. I did not open CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory topic files, or any process trace outside the packet directory. Contract 02d, the R4/R4-2 final texts, and the AP-5M documents are not in the packet and were not read.

**Validator, run 1** (charter sha ending `…d82`, the deliberate typo): result `REFUSE`, reason `charter_trusted_observed_mismatch`, rc=2. Observed charter sha `099de884…95d81`.
**Validator, run 2** (charter sha ending `…d81`): result `PASS`, rc=0; packet sha observed `b087acf5…7192` = expected; all ten manifest exhibits observed = expected; exhibit manifest sha `ed507b47…4820`.
**Independent method:** `shasum -a 256` on both files agrees: charter `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, charge `b087acf55087affd158c4dbab1eaa0d2c16f3b4b90167c3b04d8d3230a9c7192`.

**Revisions verified.** `3fb98469` = round-3 lane head (20:35). `e3769062` = merge-candidate head = `origin/fix/2026-09-24-a291-merge-candidate`, parents `3fb98469` + `2bfcc7bb`. `0fa4e6e3` = round-2 head. `24ff94cb` = harness landing (RED). `6e2504b1` (head of ex-100b/104/106/107b/108b) is an ancestor of `3fb98469`. Blob `joulewise/scored_packer.py` is byte-identical at `6e2504b1`, `3fb98469` and `e3769062`: `56a43c860ce3c3942a5c1ed592e5f0661a788226`; `git diff --stat 3fb98469 e3769062 -- joulewise` is empty. So every lens and gate exhibit speaks about the production module that is in the candidate.

**Executed probe (git archive of `e3769062` and `0fa4e6e3` under `/tmp`, removed afterwards).** With `generate_case(291013, 0)` and a 1,200-deep nested list:

| input | `_seal` fin=False | `requeue_overrun` | `executed_status` | `_seal` fin=True |
|---|---|---|---|---|
| `sha256` deep, `e3769062` unfixed | RecursionError | RecursionError | RecursionError | n/a (inv_02 first) |
| `blocks[0].items[0]` deep, unfixed | RecursionError | — | — | — |
| `blocks[0].late` deep, unsealed, fin=True | — | — | — | REFUSED inv_52 (type check) |
| `0fa4e6e3` unfixed, same inputs | RecursionError | RecursionError | RecursionError | — |
| after the V1(b) text below | REFUSED inv_52 | REFUSED inv_52 | REFUSED inv_52 | — |
| `events[-1].sha256` deep, unsealed, fin=True, after fix | — | — | — | **RecursionError** (line 304 `_digest` is outside the try) |

On the fixed copy: `test_named_seal_regressions` + `test_a291_parent_facts_and_conserve_read_the_view_ast` OK (7.19 s); full `tests.test_scored_packer_fuzz` OK, census `inv_52: 23`, 51.4 s wall.

## 1. V1 — what lands before the final pass

Reading of the question: "before the final pass" = one post-review commit on `fix/2026-09-24-a291-merge-candidate`, then a fresh-eyes review of that commit. Anything that changes a ruled production function beyond the exception path, or that needs files outside the lane's twelve, goes to a follow-up lane.

### V1(a) `-> dict` on `_ownership` — AFFIRM the plan (lands now, same commit as (b)). NIT.
Deciding evidence: `git show e3769062:joulewise/scored_packer.py` line 70 reads `def _ownership(registration, roster):` (no annotation); ex-110a V4 shows `actual=None`; ex-111b §3 concurs. The ruled R4-2(a) text itself is not in the packet (see hygiene N1); the ruling does not depend on it because the annotation is behaviour-free.

Exact text, P, `joulewise/scored_packer.py` line 70:
```python
def _ownership(registration, roster) -> dict:
```
Exact text, P, `tests/test_scored_packer.py`, inside `test_a291_parent_facts_and_conserve_read_the_view_ast` immediately after the line `functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}`:
```python
        self.assertIsInstance(functions['_ownership'].returns, ast.Name)
        self.assertEqual(functions['_ownership'].returns.id, 'dict')
```

### V1(b) `RecursionError` → `PackingRefusal("inv_52")` plus regression test — lands now. MATERIAL (was should_fix in two lenses; confirmed by probe).
Deciding evidence: probe table above. Sol's cure (validate the `sha256` field only) is REJECTED: `blocks[0].items[0]` nesting escapes the same way (executed, both heads). Opus's two-site cure is AFFIRMED and was executed: it converts every public entry point (`requeue_overrun`, `verify_executed_roster`, `executed_status` all enter through `_seal(finalize=False)`, lines 413/492/499, whose try at 282–296 contains `_digest`, `_structure` and `_checked_derived`). `pack` is not reachable: `_predictions` line 61 type-checks every value before any JSON. Pre-existing at `0fa4e6e3` (same code shape at its lines 139/271), so this is not a round-3 regression and R4-2's "nothing else in the module changes" (a round-3 landing constraint) does not bar a separately reviewed post-review commit.

Exact text, P, `joulewise/scored_packer.py`, two sites and nothing else in the module:
line 170 (inside `_checked_derived`) and line 293 (inside `_seal`), each currently
```python
    except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError) as exc:
        raise PackingRefusal("inv_52", "malformed roster") from exc
```
become
```python
    except (KeyError, TypeError, ValueError, IndexError, StopIteration, AttributeError, RecursionError) as exc:
        raise PackingRefusal("inv_52", "malformed roster") from exc
```
(`RecursionError` last in the tuple; the detail string unchanged; the `ArithmeticError` clause unchanged.) K checks: `git diff 3fb98469 -- joulewise/scored_packer.py` is exactly three changed lines (70, 170, 293) and `grep -c RecursionError joulewise/scored_packer.py` prints `2`.

Exact text, P, `tests/test_scored_packer.py`, new method on `ScoredPackerTests` placed directly after `test_a291_packer_imports_nothing_from_tests_ast`, with `from tests.scored_case_generator import generate_case` added to the module imports:
```python
    def test_a291_deep_nesting_refuses_inv_52_not_recursion_error(self):
        case = generate_case(291013, 0)
        reg, first, last = case.reg, case.rosters[0], case.rosters[-1]
        deep = []
        cur = deep
        for _ in range(1200):
            nxt = []
            cur.append(nxt)
            cur = nxt
        pending = next(e for e in first['envelopes'] if e['kind'] == 'loaded' and e['observations'] is None)
        obs = [dict(block_id=b, status='not_started', elapsed_s=None) for b in pending['blocks']]
        for where in ('sha256', 'items'):
            m = copy.deepcopy(first)
            if where == 'sha256':
                m['sha256'] = deep
            else:
                m['blocks'][0]['items'][0] = deep
            with self.assertRaises(sp.PackingRefusal) as caught:
                sp._seal(reg, m)
            self.assertEqual(caught.exception.code, 'inv_52')
            with self.assertRaises(sp.PackingRefusal) as caught:
                sp.requeue_overrun(reg, m, pending['index'], obs)
            self.assertEqual(caught.exception.code, 'inv_52')
        m = copy.deepcopy(last)
        m['sha256'] = deep
        with self.assertRaises(sp.PackingRefusal) as caught:
            sp.executed_status(reg, m, {}, set())
        self.assertEqual(caught.exception.code, 'inv_52')
```
Expected: FAIL at `3fb98469` with `RecursionError` in the first `assertRaises`; PASS after the two-site change. K states both observations in the final-pass packet.

Re-gate for the post-review commit (exception path only; no legal roster or digest can change): `python3 -B -m unittest tests.test_scored_packer tests.test_scored_packer_fuzz tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_seal_regressions tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_named_regressions` all OK, plus the three AST tests by name. The 585 s forgery campaign and the mutation kills are NOT rerun for this commit; their evidence transfers because the changed lines are outside every mutated line (ex-100b sources: lines 81, 83, 86, 96, 98).

### V1(c) `scripts/test_timings.json` entries with forgery/stress "exclusive or split" — REJECT the charge's text; follow-up lane, nothing in timings before the final pass. MATERIAL.
Deciding evidence, all at `e3769062`: (i) `.github/workflows/ci.yml` lines 188–199: `exclusive = frozenset(overlay["exclusive_modules"])` and `ordinary = (m for m in discovered if m not in exclusive)`; an exclusive module runs only if a dedicated job exists (only `calibration-exits-exclusive` and `calibration-writer-crash-matrix-exclusive` exist, lines 230/266). A timings-only "exclusive" declaration for the forgery or stress module would therefore **silently remove it from CI** — a BLOCKER if landed as the charge words it. (ii) ci.yml line 194 asserts `seconds >= fallback_rejection_threshold_seconds` (300 in every existing declaration). (iii) `scripts/test_timings.json` `_provenance` prices every ordinary module from hosted MODULE PASS maxima; no local bench figure exists for the stress module (ex-111b: run stopped at ≈7 min), so an honest row cannot be written tonight. (iv) The cost of leaving the six modules unknown is scheduling only: `shard_tests.conservative_unknown_weight()` = 21.834 s per module reserves too little, so one ordinary shard runs long; no test is skipped (`select_modules` docstring: "unknown weights never mean cheap"; touched tier includes all unknown modules). (v) Splitting or env-flagging the campaigns edits `tests/test_scored_ownership_forgery.py` / `test_scored_packer_stress.py`, which are gate evidence and would need their own re-gate.

Exact text for the follow-up lane (name it `CI-A291-TIMINGS-01`; opens after merge, on the first hosted run of main that includes the lane):
1. Add to `seconds_by_module` one row per module `tests.test_scored_ownership_forgery`, `tests.test_scored_packer`, `tests.test_scored_packer_fuzz`, `tests.test_scored_packer_stress`, `tests.test_scored_registration`, `tests.test_scored_roster_checker`, each = the MAXIMUM hosted MODULE PASS seconds over both interpreters of that run; extend `_provenance` with the run id(s).
2. Any of the six whose row is ≥ 300 s becomes exclusive ONLY together with a dedicated ci.yml job modelled on `calibration-exits-exclusive` (validate-declaration step + `python -m unittest -v <module>`), in the same PR; K's check for that PR: `exclusive_modules` keys ⊆ job names' modules.
3. No test file changes in that lane. Env-flagging or splitting the campaigns, if ever wanted, is a separate lane with the forgery gate rerun.

### V1(d) R6-2 index cut in `_structure` — REJECT for the post-review commit; follow-up lane. NIT for the merge.
Deciding evidence: line 244 `placement = next(p for p in placements if p["block_id"] == bid and p["envelope_index"] == ix)`; uniqueness of `(block_id, envelope_index)` is enforced earlier at line 213 (`len(ids) == len(set(ids))` per envelope), so a dict index is behaviour-preserving on inputs that reach line 244, and a missing key raises `KeyError`, already in the line-293 tuple → same `inv_52`. But it edits a ruled production function on a hot path for the forgery and fuzz gates, so it needs the 585 s forgery module and the fuzz module rerun, which is more than the exception-path re-gate of (b). Cost is a runner obligation (ex-111b R6-2), not a merge defect.

Exact text for the follow-up (lane `A291-STRUCTURE-INDEX-01`, WRITE_SCOPE `joulewise/scored_packer.py` only): before the `for event in roster["events"]:` loop at line 232 insert `pindex = {(p["block_id"], p["envelope_index"]): p for p in placements}`; replace line 244 with `placement = pindex[(bid, ix)]`; gate = full `tests.test_scored_ownership_forgery`, `tests.test_scored_packer_fuzz`, `tests.test_scored_packer` GREEN and Sol's V2 probe (ex-110b) re-run with the 131-event total reported.

## 2. V2 — R6-1 (level/night confound in `pack`) — AFFIRM: gates the first REGISTERED night, not this merge

Deciding evidence: `git show e3769062:joulewise/scored_packer.py` lines 365–382: buckets are filled first-fit in block order (blocks are generated level by level), then envelopes interleave the two models bucket-by-bucket; nothing in `_seal`/`_derived` compares a level's mean envelope index with the night midpoint (the only lever check is `drift_lever_slots` across models within a level, line 301 `inv_28`). Opus's probe (ex-111b, `{1:4,2:4,3:4,4:14,5:14}` of 20) is consistent with that code; I did not rerun it (NOT EXECUTED, budget). The candidate produces no roster and arms nothing, so the confound cannot affect any measurement until a registered-mode night is packed; it is not a merge defect. Whether the contract requires a level-position check I cannot verify (contract not in packet, hygiene N1); the ruling stands on code alone.

Where it is decided — AFFIRM the magistrate's venue (the headline redesign work with its council and cold gate) and ADD one rule so the decision cannot be skipped. Proposed rule text (charter trigger 4; for ratification by the magistrate, recorded in the A291 record):
> **R6-1 gate.** No `registered`-mode registration is armed until its arming packet cites, by immutable path and digest, ONE of: (i) a landed `pack` ordering change whose test asserts, on a fixture with unequal model speeds (8B predictions ≥ 2× 1.7B), that every level's mean envelope index lies within ±2 envelopes of the night's mean for each model, re-gated by the full forgery, fuzz and stress modules; or (ii) a reducer specification stating that envelope index enters the difficulty-axis model as a covariate, with the estimator named. The arm notice for that night quotes the chosen option. Pilot-mode nights are exempt.

## 3. V3 — the final-pass packet (MERGE / NO-MERGE on an exact sha)

The packet for the next Fable pass must contain, each as a manifest-hashed exhibit:
1. **The sha.** The post-review commit `S` on `fix/2026-09-24-a291-merge-candidate` AFTER re-merging current `main` (`main` is at `25cde215`; `e3769062`'s main-side parent is `2bfcc7bb`, one docs-only commit behind — MATERIAL M2). State `S`, its parents, `git merge-base main S`, `git diff --stat main...S` (expected: the same 12 files, +4,223 plus the (a)/(b) delta), and blob shas of `joulewise/scored_packer.py` and `tests/test_scored_packer.py` at `S`.
2. **The diff** `git diff 3fb98469 S -- joulewise tests scripts .github` verbatim, expected to touch exactly `joulewise/scored_packer.py` (lines 70, 170, 293) and `tests/test_scored_packer.py` (import + two assertions + one method), nothing else.
3. **Re-gate outputs at `S`** (commands of §1 V1(b)): full tails with `Ran N tests … OK`; the new test's FAIL-before/PASS-after pair; the three AST tests by name; `grep -c RecursionError` = 2.
4. **Evidence transfer statement** for the gate items not rerun: mutation kills m1–m5 (ex-100b, at `6e2504b1`), F-C/F-B forger adjudications (ex-104, ex-106), entry witnesses (ex-108b), bench 10/10 at `3fb98469` — each with the blob sha of the module they ran against and the proof that blob is unchanged except at the three ruled lines (`git diff 6e2504b1 S -- joulewise/scored_packer.py`).
5. **F-C replay evidence** (MATERIAL M3): ex-104 contains no `REPLAY` lines; the charge's "all refused by replay" is supported only for F-B (ex-106 `REPLAY CHECK`, nine `inv_38`). Supply the F-C replay adjudication for its nine OUT_OF_ROUND candidates or restate F-C's status as "COMPLETED_NO_ESCAPE, replay refusals not exhibited".
6. **Full-suite result** for the lane branch (the charge says it is running): the per-module tails for the six new modules and the wall time of `tests.test_scored_packer_stress`, which also seeds V1(c).
7. **The two lens reports and the counter-review** (ex-110a, 110b, 111b) with the disposition of every finding: F1 Astra → landed; F1 Sol → landed (two-site form); R6-1 → V2 rule; R6-2 → runner obligation + `A291-STRUCTURE-INDEX-01`; R6-3 → runner obligation; CI cost → `CI-A291-TIMINGS-01`; duplicated operators → follow-up.
8. **Entry-witness code note** (ex-108b F1): the INV-23/36/37 witnesses assert `inv_38`/`inv_38`/`inv_11`, not the rows' listed codes; the final pass must see this stated, not just "witnesses exist".
9. **The R4-2 final text** (at least items (a) and (e) verbatim with revision), so the `-> dict` claim and the "nothing else changes" clause can be checked rather than taken from lens paraphrase.
10. **Charter pin + validator receipt** for the new packet, and the PR body's gate ledger draft.

The final pass rules MERGE only if items 1–3 verify by its own execution and items 4–9 are present; a missing item is a REFUSE of that pass, not a NO-MERGE.

## 4. Findings

| # | Tier | Finding | Verified by |
|---|---|---|---|
| M1 | MATERIAL | `RecursionError` escapes the typed-refusal contract at every public entry point on both `0fa4e6e3` and the candidate; Sol's `sha256`-only cure is insufficient; the two-site cure works. | probe table §0 |
| M2 | MATERIAL | Candidate `e3769062` is behind `main` (`25cde215`, docs-only); the final-pass sha must be the re-merged commit. | `git log -1 --format=%P e3769062`; `git rev-parse main` |
| M3 | MATERIAL (hygiene) | Charge says both forgers' OUT_OF_ROUND candidates were "all refused by replay (ex-104, ex-106)"; ex-104 has no replay lines. Affects V3 item 5 only. | `grep -c REPLAY ex-104` = 0; ex-106 = 9 |
| M4 | MATERIAL | Charge's V1(c) wording "marked exclusive" would, as a timings-only edit, drop the module from CI; requires a dedicated job. | ci.yml 188–199, 230, 266 |
| M5 | MATERIAL (follow-up) | After the fix, `_seal(finalize=True)` on an UNSEALED roster with deep nesting in `events[-1].sha256` still raises `RecursionError` (line 304 `_digest` outside the try). Not reachable through any public entry point (each validates via `_seal(finalize=False)` first); reachable by direct `_seal(finalize=True)` callers such as the forger charge. Follow-up text: wrap `_digest`'s body in `try: … except RecursionError as exc: raise PackingRefusal("inv_52", "malformed roster") from exc`, gated like V1(d). | probe §0 last row |
| N1 | NIT (hygiene) | Packet cites R4-2 ("nothing else in the module changes", the `-> dict` signature) and contract §3.1/§3.2 without exhibiting them; rulings above avoid depending on their wording. | packet listing |
| N2 | NIT (hygiene) | `09-convene-script.sh` sits in the packet directory but is not in the manifest; the convene prompt names `24ff94cb` as a probe base while the charge names `3fb98469`/`e3769062`/`0fa4e6e3`. I used `e3769062` and `0fa4e6e3`. | `ls`, charge vs prompt |
| N3 | NIT | ex-108b F1: entry witnesses assert codes other than the rows' listed codes; the charge omits this. | ex-108b table |
| N4 | NIT | Six new test modules absent from `scripts/test_timings.json`; scheduling-only effect. | `grep scored scripts/test_timings.json` = none |

## 5. Verdict summary

- **V1(a)** AFFIRM — lands now; exact texts §1.
- **V1(b)** AFFIRM Opus's two-site form, REJECT Sol's field-only cure — lands now with the named regression test; exact texts §1.
- **V1(c)** REJECT as worded — follow-up lane `CI-A291-TIMINGS-01`; nothing in timings before the final pass.
- **V1(d)** REJECT for now — follow-up lane `A291-STRUCTURE-INDEX-01`.
- **V2** AFFIRM — R6-1 gates the first registered night, decided in the headline redesign council/cold gate; new rule text proposed in §2 for ratification.
- **V3** ruled — packet contents §3, items 1–10.

Disagreements with the lead's labelled disposition: V1(c) (lead's "exclusive or split" text rejected) and the F-C replay claim (M3). Everything else concurs. Nothing here authorises a merge; the final pass does that on sha `S`.
