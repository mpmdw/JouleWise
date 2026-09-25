# Cold Fable gate ruling — PR0-F1-01 (packet 29/pr0f1)

Judge: Claude Fable 5.1, fresh single session, worktree `JouleWise-wt-coldgate-152c9255-pr0f1` at `9ae33bd8`, 2026-09-25 (clock-read at start ≈10:30 PDT; ≈25 min used). Foreground only; no subagents or background tasks; no sudo/launchctl/powermetrics/systemsetup/pmset; canonical root, custody/measurement dirs, LaunchAgents and the stash untouched. Probes ran in a fresh clone `/tmp/cg-pr0f1-1b8bae45` checked out at `1b8bae45` (= `origin/test/2026-09-25-claimgate-pr0-golden`; `git status` clean before and after every probe; mutated files restored byte-for-byte). Only this ruling was written.

## 0. Disclosure and trust anchors

Auto-loaded by the harness before any action: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, the memory index `MEMORY.md` (truncated). None requested, none used. Not read: `CLAUDE.local.md`, RUN_STATE, TASK_QUEUE, council logs, run reports, memory files, any trace file outside this packet directory.

| Item | Expected | Observed | Method |
|---|---|---|---|
| Validator run 1 (deliberate typo `…5d82`) | REFUSE | `result: REFUSE`, `reason: charter_trusted_observed_mismatch`, rc=2 | `scripts/validate_gate_packet.py` as charged |
| Validator run 2 (`…5d81`) | PASS | `result: PASS`, rc=0, 3/3 exhibits `expected == observed`, manifest `b1dba943…8f974a` | same script |
| Charter sha256 | `099de884…5d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256` |
| Packet sha256 | `6f2ff2f9…df07c` | `6f2ff2f9d3b20676dd1700447ceb3cefe8f2ca2542595f4d14a8e375749df07c` | `shasum -a 256` |

## 1. Packet hygiene (charter §6)

- **H-1 (MATERIAL, affects Q1 and Q2).** The packet presents one pre-632 survivor. Enumerating the gated mutants of `_claim_issuance_gate` at `1b8bae45` (`_mutations`, sweep `:133-176`) gives 15 mutants, 7 of them before line 632; four survive the standing-test oracle (fact 6 below), not one. The seat's V5 probed only `620:if_false@4`; the aggregate run (V6) was interrupted, so the seat could not know. The proposal and the charge are argued about a single mutant; the ruling below covers all four because the same disposition must.
- **H-2 (MATERIAL, affects Q2).** The proposal's alternative ("wait for D-1's fix") is presented as the only other option and is asymmetric: it is not a cure at all (fact 7). A third option, one killing row, is not mentioned although acceptance v3 (B) already provides the row format.
- **H-3 (NIT).** The charge says "`origin/test/2026-09-25-claimgate-pr0-golden` at `1b8bae45`"; the seat report (ex-01) records `head_end: 576f3989`. `1b8bae45` is the seat's landing commit on top of `576f3989`; consistent, but the packet should say so.

## 2. Verified facts (all at `1b8bae45`; line numbers are `joulewise/paper_custody.py` unless marked)

1. **The mutated site.** `:620` is `if embedded_floor != ctx.raws[InputRole.FLOOR_ARTIFACT]:`; `:621` appends `"claim_floor_anchor_mismatch"`; `:622-623` return `_FamilyReplay(False, False, (), tuple(codes))` when any code exists; `:624` `_validate_floor_acceptance(ctx)`; `:625-627` build `contrasts` and raise `PaperCustodyRefusal("paper_custody_binding_mismatch")` on a subject not in the artifact; `:632` reads `artifact["evidence_class"]` (defect D-1, `KeyError`). `if_false@4` at `:620` is the `ast.If` at column 4 (sweep `:161-162`), i.e. the anchor check is forced false.
2. **The observable boundary records codes.** `_replay_family` (`:1339-1348`) returns `_FamilyReplay(False, False, (), (type(exc).__name__,))` for any non-`PaperCustodyRefusal` exception and re-raises `PaperCustodyRefusal` (`:1345-1346`). `_replay_record` (capture `:613-616`) records `authentic`, `admitted`, `validator_codes`, `grants`. So the anchor refusal is recorded as `["claim_floor_anchor_mismatch"]` and the D-1 refusal as `["KeyError"]`. They are **not** the same at the boundary.
3. **Why the mutant survives.** `_claim_gate_context` (capture `:594-610`) sets `raws[FLOOR_ARTIFACT] = base64.b64decode(artifact["inputs"]["floor_artifact"]["embedded_bytes_base64"])` (`:605-606`). `:620` compares `b64decode(embedded, validate=True)` of the same string with that value; they are equal by construction in every row. Both gate callers, `_issuance_gate` (`:640-665`) and `_invalid_issuance_gate` (`:668-679`), use this builder; the fixture-mode rows (`:196-199`) never reach `_claim_issuance_gate`; the validator corpus reads tracked bases only. So no golden input ever takes the true arc of `:620`. The mutant survives because the arc is **unexercised**, not because D-1 masks it. The same builder existed at `576f3989` (capture `:446`).
4. **The masking claim is refuted by a sibling mutant.** `617:ifexp_false@25` (forces `embedded_floor = None`) is **killed**: it changes `invalid_verdict_wire.validator_codes` to `["artifact.claim_verdicts_id: invalid canonical ID", "claim_floor_anchor_mismatch"]` and `real_v1_wire.pre.direct_call` to `{"raised": null}`. That is exactly the anchor-mismatch signature reaching the boundary and being distinguished, while D-1 exists.
5. **The oracle.** The exact worker command (sweep `:243-248`) compares `invariant` and `v1_golden_manifest_ids` byte-wise and every `transitions[*][*]["pre"]`. Golden transitions at `1b8bae45`: `V1-ISSUANCE-GATE-EVIDENCE-CLASS-01: [real_v1_wire]`, `WR-6: [v3_window_clean, v3_window_supersession_diverged]`; `real_v1_wire.pre = {"admitted": false, "authentic": false, "direct_call": {"key": "evidence_class", "raised": "KeyError"}, "grants": [], "validator_codes": ["KeyError"]}`.
6. **Probe (proxy oracle).** Because `_claim_issuance_gate` is reached only through `_issuance_gate()["pre"]` and `_invalid_issuance_gate()` (fact 3), I compared those two records, baseline vs mutant, for each of the 7 pre-632 mutants (0.8 s per run):

   | key | result |
   |---|---|
   | `604:comprehension_if_false_0@66` | killed (`StopIteration` in the direct call) |
   | `617:ifexp_false@25` | killed (fact 4) |
   | `620:if_false@4` | **survives** (identical records) |
   | `622:if_false@4` | killed (`invalid_verdict_wire` becomes `["KeyError"]`) |
   | `626:if_false@4` | **survives** |
   | `626:Or_delete_0@7` | **survives** |
   | `626:Or_delete_1@7` | **survives** |

   The 8 mutants at lines ≥ 632 (`632:if_false@8`, `632:Or_delete_0@11`, `632:Or_delete_1@11`, `644:ifexp_false@28`, `645:LtE_to_Lt@31:0`, `649:if_false@8`, `649:And_delete_0@11`, `649:And_delete_1@11`) cannot affect any `pre` and will survive; **none is listed** in `EQUIVALENT_MUTANTS` at `1b8bae45` (sweep `:59-64` holds only the two `claims.py` entries), so `--certify` will exit 2 on them too (v3 (C)(2), (C)(5)).
7. **Waiting for D-1 kills nothing.** After D-1 is fixed, `:620` is still false on every golden input (fact 3), so `620:if_false@4` and the three `:626` mutants survive exactly as now. The alternative in ex-03 does not resolve F1.
8. **Killing rows exist and were prototyped** (same seams as `_issuance_gate`: manifest validator → `[]`, `_validate_floor_acceptance` → `None`; `_gate_fixture()` inputs; `_claim_gate_context` then one field replaced):

   | row | change to `ctx` | unmutated | `620:if_false@4` | `626:if_false@4` | `626:Or_delete_0@7` | `626:Or_delete_1@7` |
   |---|---|---|---|---|---|---|
   | `floor_anchor_mismatch_wire` | `raws[FLOOR_ARTIFACT] += b"\n"` | codes `["claim_floor_anchor_mismatch"]` | codes `["KeyError"]` **kill** | unchanged | unchanged | unchanged |
   | `binding_mismatch_wire` | `subjects=("not-a-contrast",)` | `{"raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch"}` | unchanged | codes `["KeyError"]` **kill** | unchanged | codes `["KeyError"]` **kill** |
   | `empty_subjects_wire` | `subjects=()` | `{"raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch"}` | unchanged | message `paper_custody_not_issuable` **kill** | message `paper_custody_not_issuable` **kill** | unchanged |

   Every surviving pre-632 mutant is killed by at least one row. The rows' `pre` values are D-1-independent (each refuses before `:632`), so they are stable across the V1-ISSUANCE-GATE-EVIDENCE-CLASS-01 fix; `post` equals `pre` for all three.

## 3. Q1 — the masking claim: REJECT

The proposition "the mutation changes no observable output while D-1 exists" is false. Facts 2 and 4: the boundary records `validator_codes`, the anchor refusal and the D-1 refusal record different codes, and a sibling mutant that forces the anchor arc is killed today. Fact 3 gives the true cause: no golden input has a mismatching floor because the context builder derives the floor bytes from the artifact itself. The mutant is an uncovered-arc survivor, and it is one of four (fact 6). The charge's Q1 asked me to run the mutant through the golden comparison; I ran a proxy on the only two call sites instead (fact 6) and did not run the full `capture()` (§7). The seat's own V5 exit 0 and my proxy agree, so the survival is established; the *reason* given for it is what fails.

Deciding evidence: capture `:605-606`; `paper_custody.py:1347-1348`; probe row `617:ifexp_false@25` (fact 4).

## 4. Q2 — the proposal: REJECT; write another

- **`masked-by-D-1` entry: REJECT.** It would record a false proof in the certificate (§3) and needs a third proof class in `_validate_exceptions` (sweep `:314-328`) plus an amendment to v3 (C)(2), all to excuse a mutant that one row kills. It also leaves the three `:626` survivors unaddressed, so `--certify` would still exit 2.
- **Alternative (wait for D-1): REJECT.** Fact 7: it does not kill the mutant. It would block PR-0 on an unscheduled lane for nothing.
- **Ruled disposition: three real-wire rows, admitted by an explicit, bounded amendment to acceptance v3 (B).** No exception entry of any class is authorized for lines < 632. Exact text the magistrate is to issue, verbatim, as "PR-0 acceptance v3, amendment A1 (cold gate PR0-F1-01)":

> **A1.1 (replaces the sentence "No `paper_custody` rows (M-2)" in v3 (B)).** No `post.variants` or shim rows (M-2). Exactly three real-wire scenarios are added under `transitions["V1-ISSUANCE-GATE-EVIDENCE-CLASS-01"]`, each `{"pre": R, "post": R}` with `R` the record defined below; `pre` and `post` are identical because every scenario refuses before `paper_custody.py:632`. Each scenario builds `artifact, manifest, floor, sidecar = _gate_fixture()` and `ctx = _claim_gate_context(artifact, manifest, floor, sidecar)`, runs under the same two seams as `_issuance_gate` (`validate_finalized_analysis_manifest_v3` patched to `[]`, `_validate_floor_acceptance` patched to `None`), and records `_replay_record(custody._replay_family(ctx'))` if it returns, else `{"raised": type(exc).__name__, "message": str(exc)}`:
> 1. `floor_anchor_mismatch_wire`: `ctx'` = `ctx` with `raws[InputRole.FLOOR_ARTIFACT]` replaced by the same bytes followed by `b"\n"`. Expected record: `{"admitted": false, "authentic": false, "grants": [], "validator_codes": ["claim_floor_anchor_mismatch"]}`.
> 2. `binding_mismatch_wire`: `ctx'` = `ctx` with `subjects=("not-a-contrast",)`. Expected record: `{"raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch"}`.
> 3. `empty_subjects_wire`: `ctx'` = `ctx` with `subjects=()`. Expected record: `{"raised": "PaperCustodyRefusal", "message": "paper_custody_binding_mismatch"}`.
>
> A scenario whose captured record differs from the expected record above is a protocol failure of the round, not a golden to be accepted.
>
> **A1.2 (adds to v3 (C)(2)).** `EQUIVALENT_MUTANTS` may contain no key inside `_claim_issuance_gate` with line < 632 of any proof class; `--certify` exits 2 on such a key. The eight gated mutants of `_claim_issuance_gate` at lines ≥ 632 (`632:if_false@8`, `632:Or_delete_0@11`, `632:Or_delete_1@11`, `644:ifexp_false@28`, `645:LtE_to_Lt@31:0`, `649:if_false@8`, `649:And_delete_0@11`, `649:And_delete_1@11`) are listed with the existing `v1-wire-unreachable:` proof text exactly as v3 (C)(2) requires, and with no other key.
>
> **A1.3 (adds to v3 (D)(5)).** The PR body names the three A1.1 rows and the four pre-632 mutants each kills (`620:if_false@4` ← row 1; `626:if_false@4` ← rows 2 and 3; `626:Or_delete_0@7` ← row 3; `626:Or_delete_1@7` ← row 2).
>
> **A1.4.** Everything else in v3 stands. Same seat WRITE_SCOPE. This is the consult-ruled round that v3 (D) reserved after a non-empty gated `unlisted_survivors`; if gated `unlisted_survivors` is non-empty after it, the next spend is another consult, not a round.

Deciding evidence: fact 8 (prototype table) and fact 6.

## 5. Findings the charge missed

- **F-A (BLOCKER).** Three further pre-632 gated survivors at `:626` (fact 6). Any certification that lists only `620` fails. Cured by A1.1 rows 2-3.
- **F-B (BLOCKER).** `EQUIVALENT_MUTANTS` at `1b8bae45` holds none of the ≥632 `v1-wire-unreachable:` entries that v3 M-2/(C)(2) contemplated; `--certify` refuses on eight unlisted gated survivors regardless of F1. Cured by A1.2.
- **F-C (MATERIAL).** The seat's V6 (`--certify`) ended with `KeyboardInterrupt` (rc 130); no certificate exists and `test_sensitivity_certificate_pinned` errors. The next `--certify` must run to completion in the seat's foreground with a wall budget sized to 1,167 mutants (the seat measured 8 tests in 56 s; budget the sweep at hours, not minutes), or the round is not evidence.
- **F-D (NIT).** The `_validate_exceptions` regex (sweep `:318`) accepts any `equivalent:` proof whose row path exists; it does not check that the row actually kills the neighbour. The delta re-audit ((D)(6)) is the only check; keep it.

## 6. Severity ledger

| # | Tier | Finding | Ruled cure |
|---|---|---|---|
| 1 | BLOCKER | Masking proof false (facts 2-4); mutant is uncovered, not masked | REJECT `masked-by-D-1`; A1.1 row 1 |
| 2 | BLOCKER | F-A: three more pre-632 survivors at `:626` | A1.1 rows 2-3 |
| 3 | BLOCKER | F-B: no ≥632 exception entries listed | A1.2 |
| 4 | MATERIAL | Alternative (wait for D-1) kills nothing (fact 7) | REJECT |
| 5 | MATERIAL | H-1/H-2 packet asymmetry; F-C interrupted certification | A1.3; complete `--certify` |
| 6 | NIT | H-3, F-D | none required |

Disagreements with the labelled disposition: both the proposal and its alternative are rejected; the packet's "one survivor" framing is rejected (four). Concurrence: the seat's F1 finding that the mutant is not equivalent and that `v1-wire-unreachable` cannot apply below `:632` is affirmed; F2's "resume only under a ruling" is affirmed.

## 7. NOT EXECUTED

The full `capture()`-based worker command (sweep `:243-248`) on the `620` mutant was not run inside the budget; the proxy oracle over the only two gate call sites (fact 3) was run instead and agrees with the seat's V5. `--certify` was not run. The A1.1 rows were prototyped as records, not as golden entries; the round captures them. No refuter or magistrate contact (charter §4, §5).

**Plain summary for Ed (2 lines).** The "surviving mutant" is not hidden by the known bug; the snapshot simply never feeds the gate a mismatched floor, and three neighbouring checks have the same gap. Add three tiny recorded refusals to the snapshot (they kill all four), list the eight post-bug sites as already ruled, and certify; waiting for the bug fix would have changed nothing.
