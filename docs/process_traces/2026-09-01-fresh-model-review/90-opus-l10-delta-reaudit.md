# 90 — Opus 5 delta re-audit of the L10 fix round (commit 1eef148f, PR #259)

Seat: Opus 5, read-only, contract + pedagogy lens; reviewed at branch head 244f339c. Verdict: NEEDS FIX ROUND.

## Delta re-audit — `1eef148f` (PR #259), read-only

Reviewed at branch head `244f339c` (the merge that brought kernel commit `f022abd9` onto the branch). All line refs are at that head.

---

### 1. RULING FIDELITY (R-1..R-5)

| Item | Verdict | Evidence |
|---|---|---|
| R-1 ladder (L10-A/B/C, roles) | **IMPLEMENTED** | `v5-l10-rehearsal-phase.md:48-53` (three corpora), `:160-164` (L10-A gates `V5-TRANSACTION-01`, does not close the row), `:226-231`, `:273-277` |
| R-1 L10-A PASS = singleton `analysis_finalization_member_cover_mismatch` | **IMPLEMENTED** | `:216-218`, `:370-375` — "Any other reason, a successful finalization, a nonzero tree comparison, or a write outside L10 custody is FAIL" |
| R-2 G2-b byte-unchanged + tree hash before/after | **IMPLEMENTED** | `:132-144` (`g2b-tree-before.sha256`), `:207-209` (`g2b_tree_hash` + `cmp`). *Not stated:* that fence[2] stays verbatim — the doc never quotes or names the immutability fence it is operating under (NIT) |
| R-1 `proof_scope` ∈ three literals | **IMPLEMENTED, matches kernel exactly** | `:337-340` vs `state_kernel.json` `/tasks/L10-*/acceptance` |
| R-4 lane = BENCH everywhere | **IMPLEMENTED** | `:151-154`; `grep ED-FIRST` returns zero hits across all three files; `ed-batch-packet.md:62-66` shrunk to "Review the preserved L10-A record" |
| R-1/F3 ED-L10-1 never executed | **IMPLEMENTED** | `:18-20`, cite verified — `ROW-L10.md:501` literally reads "NO CLOSURE EVIDENCE LOCATED — still Ed-owed" |
| R-3 "spent window" sourced to D-167(1) | **IMPLEMENTED** | `:43-46`, `:403-404`; anchor `decision_log.md#L10407` lands on the D-167 heading, the ruling (1) text is at `:10409` (NIT) |
| R-5 §D stops attributing an L10 clause to `V5-TRANSACTION-01` | **DEVIATING** | `:396` — the false attribution is gone, but the replacement sentence "`V5-TRANSACTION-01` carries no L10 clause in the kernel today" is now **itself false** at this head, and the doc never cites the installed gate. See BLOCKER-1 |
| R-5 item 5 (claim edge "begins at Strict validation") | **DEVIATING** | `:22-25` re-cites the same unsourced claim to `[artifact flow]` + `89-…:39-58`; neither says the claim edge begins at strict validation, and the historical ruled item 1 ("Build the prospective manifest twice") is still upstream of it. See SHOULD-FIX-4 |
| R-5 items 6/7 (BLOCKED, per-step head check labelled own refusals) | **IMPLEMENTED** | `:57-60`, `:69-74`, `:146-149`, `:408-411` (§E now says "adds its own refusals") |
| R-5 item 9 (`QUALIFICATION_ONLY_…` labelled NEW) | **IMPLEMENTED** | `:39-42` "is a new literal for this phase, rather than a token inherited from the ALPHA rehearsal card" |
| R-5 item 10 (licence precedes the rule) | **IMPLEMENTED** | `:332-334` now precedes `:370+` |
| R-5 item 2 (self-contradiction with synthetic item 2) | **IMPLEMENTED** | `:10-16` |

---

### FINDINGS

**BLOCKER-1 — L10-A step 5 as written cannot reach PASS; it dies before the member-cover gate.**
`v5-l10-rehearsal-phase.md:195-206` passes `--custody-root "$CUSTODY_ROOT"` together with `--runs-root "$RUNS_ROOT"`, `--whole-window-verdict "$RUNS_ROOT/…"`, `--bracket-binding "$RUNS_ROOT/…"`. In refusal mode every one of those is pushed through `_copy_path` (`scripts/check_window_provenance.py:467-474`, called at `:506-517`), which raises `AssertionFailure: finalizer input is outside --custody-root and cannot be copy-safe` for any path not under `--custody-root`. The doc's own §C1 defines `CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"` (`:89`) and `RUNS_ROOT` as the **separate, isolated** G2-b shakedown root (`:93`, `:114`). The command was lifted verbatim from `SHAKEDOWN-G2-RUNSHEET.md:1136-1149`, where `$RUNS_ROOT` lives *inside* `$CUSTODY_ROOT`. The ruled PASS criterion is therefore unreachable.
*Fix:* stage/point `--custody-root` at a root that contains the G2-b runs root (or ditto the G2-b root under an L10 custody staging dir and pass that), and state the containment requirement explicitly at `:196`.

**BLOCKER-2 — §D contradicts the kernel at this head; the installed gate is never cited.**
`:396` "`V5-TRANSACTION-01` carries no L10 clause in the kernel today" and `:397-399` "Ruling 89 R-1 **installs** L10-A as a bench kernel edit" are stale by one merge. `state_kernel.json` `/tasks/V5-TRANSACTION-01/dependencies[0]` (line 5141) is a **hard start** dep on `L10-A-G2B-CONTRACT-PREFIX-01`, "the L10-A record (proof_scope L10_A_G2B_CONTRACT_PREFIX) exists and is ratified before the first claim-bearing arm (ruling 89 R-1)". Neither row id — `L10-A-G2B-CONTRACT-PREFIX-01` nor `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01` — appears anywhere in the three edited docs (`grep`, zero hits).
*Fix:* rewrite `:396-401` to cite the installed row by id and the dep pointer `/tasks/V5-TRANSACTION-01/dependencies[0]`, and name the parent row that closes only after L10-C.

**BLOCKER-3 — all seven `v5-artifact-flow.md` line citations point at the wrong rows.**
The same commit rewrote the flow table (deleting the standalone Strict-validation and Reduction stage rows, inserting L10-A/B/C at lines 12/14/15) but left the L10 doc's anchors on the *old* numbering. Verified against `git show b28be255:docs/process/v5-artifact-flow.md`:

| L10 doc | cites | old row | new row 
|---|---|---|---|
| `:186` reduction FAIL | `#L13` | Reduction | **Collection** |
| `:252` extraction FAIL | `#L14` | Floor extraction | **L10-B** |
| `:271` mint FAIL | `#L15` | Mint | **L10-C** |
| `:302` finalization FAIL | `#L16` | Finalization | **Floor extraction (production)** |
| `:316` claim-gate FAIL | `#L17` | Claim gate | **Mint (production)** |
| `:328` results-fill FAIL | `#L18` | Results fills | **Finalization (production)** |
| `:175` strict-valid FAIL | `#L12` | Strict validation | L10-A (coincidentally related) |

*Fix:* repoint each to the surviving row, and restore Strict-validation and Reduction rows to `v5-artifact-flow.md` (see SHOULD-FIX-4).

**BLOCKER-4 — four `state_kernel.json` line anchors and one in `ed-batch-packet.md` are wrong at this head.** They were correct at `1eef148f` and drifted when `f022abd9` (+109 lines) merged in.

| Cite | Claims to be | Actually at that line | Correct line |
|---|---|---|---|
| `:28`, `:72`, `:129` `state_kernel.json#L1927` | kernel fence | `"evidence": null,` | 1952 (or 2027) |
| `:412`, `:416` `#L1936` | kernel L10 fence | `"fallback": null,` | 1959 / 2034 |
| `:119` `#L4883` | G2-b acceptance | `"target": "V5-G2A-PREFILL-PROBE-01"` | 4980 |
| `:400` `#L5022` | V5 transaction acceptance | `{` | 5118 |
| `ed-batch-packet.md:65` `#L5094` | GO-01 acceptance | D-167 evidence-immutability fence in a different row | 5203 |

*Fix:* re-derive all kernel anchors at the merged head; kernel line anchors are volatile — prefer the JSON pointer (`/tasks/<id>/fences/1`) as the doc already does elsewhere.

**SHOULD-FIX-1 — a known-false code citation is carried twice.** `:221` and `:376` cite `joulewise/analysis_manifest_v3.py:2590,2598` for `analysis_finalization_member_cover_mismatch`. Those lines are prospective-manifest messages ("must contain ten unique blocks", "must contain exactly 40 rows") belonging to `analysis_prospective_member_cover_mismatch` — a **different reason code**. The doc adds the correct pair (`:2986,3048`) beside it, so it publishes a right and a wrong citation for the same rule. *Fix:* delete the `2590,2598` pair (inherited from the ruling; the ruling inherited it from the Opus seat).

**SHOULD-FIX-2 — broken relative path, ×2.** `:222` and `:377` link `../joulewise/analysis_manifest_v3.py#L2986`; the doc lives in `docs/process/`, so this resolves to `docs/joulewise/…`, which does not exist. *Fix:* `../../joulewise/`.

**SHOULD-FIX-3 — `$PACK_ROOT` does not exist and disagrees with the FIRST CHECK probes.** `:92` sets `PACK_ROOT=…/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (only produced by pack generation; absent at this head), so `:108` `test -d "$PACK_ROOT/arm_readiness.freeze.receipts"` fails today — while `:64-65` probe `configs/campaigns/d117_contrast_v5` (the *generator* directory, which does exist). Nothing in the doc tells the reader these are two different things. *Fix:* one sentence distinguishing generator source from generated pack, and state that §C1 runs only after pack generation.

**SHOULD-FIX-4 — the claim-edge definition's source no longer contains two of its seven stages.** `:22-25` names Strict validation and Reduction as claim-edge stages citing `[artifact flow]`, but this commit deleted both rows from `v5-artifact-flow.md` (they were `:12` and `:13` at `b28be255`). The flow doc is titled "the command and artifact map" yet no longer maps the production strict-validation or reduction commands at all. *Fix:* restore both stage rows to the flow table.

**SHOULD-FIX-5 — §C1 is one-shot but the doc says it is re-run per part.** `:80-82` says `PRODUCER_RUNS_ROOT`/`CAMPAIGN_RUNS_ROOT` "are set when their respective post-collection parts begin", i.e. §C1 is entered again days later; `:110` `test ! -e "$L10_CUSTODY_ROOT"` then fails on every re-entry. *Fix:* guard the create-once assertion to L10-A only.

**SHOULD-FIX-6 — L10-C depends on variables exported only inside L10-B.** `:311` uses `$PRODUCER_RUNS_ROOT` (exported at `:234`) and `:297`/`:312` use `$AGGREGATE_FLOOR_ARTIFACT` (exported at `:259`, pointing at the *rehearsal* mint output `l10-b-aggregate-floor.json`, not the production floor). L10-C runs after the last consuming arm, in a fresh shell. *Fix:* re-export both in the L10-C preamble and state explicitly which floor artifact L10-C consumes.

**SHOULD-FIX-7 — three citations do not say what the citing sentence claims.**
- `:31-32` sources the definition of "transaction head" to `ruling 89 R-5` (`#L80`); R-5 is the writing-standard fix-round item and defines no such thing.
- `:72-74` sources "The missing G2-a config producer is outside this phase" to R-5; R-5 says nothing about a G2-a config producer.
- `:155-156` defines **BOUNDARY-PROVEN** citing `[artifact flow]` with no line; the string "BOUNDARY-PROVEN" does not occur in `v5-artifact-flow.md`.
Also flagged in the brief: `:35` cites `real-transaction-runbook.md` file-level with no line for "custody"; the runbook's closest support is `:395`/`:1361` (campaign root outside the repository, `CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"`) — supportable but must be pinned to those lines.

---

### 3. PEDAGOGY — terms failing the first-use test

| Term | First use | Status |
|---|---|---|
| **member cover** | `:216` (in the reason code), `:371` | **FAILS — load-bearing.** The entire L10-A PASS is "the run refuses with member-cover mismatch." The doc never says what a member cover is, that the frozen plan has 80 members / ten blocks, that the G2-b block is one of them, or *why* a refusal is the desired outcome. A reader cannot tell a PASS from a bug. |
| **strict validation** | `:22`, step at `:166` | **FAILS.** No gloss. Its former one-line gloss ("prove a stored summary follows from raw evidence") was deleted from the flow table by this same commit. |
| **reduction** | `:22`, step at `:177` | **FAILS.** Same; former gloss "rebuild the summary without changing the bundle" deleted. |
| **finalization** | `:22`, steps at `:188`/`:287` | **FAILS.** Never glossed; former gloss "bind post-collection identities without reading an effect estimate" deleted. |
| **bracket binding / whole-window verdict / "NR-14 order"** | `:116-117` | **FAILS.** Three unglossed terms in one clause, and "NR-14" carries **no citation at all** (it is defined in `SHAKEDOWN-G2-RUNSHEET.md:22` → `04-MAGISTRATE-RULING.md:103-166`). |
| **verdict basis** | not present in the doc | n/a |
| custody root, scratch custody copy, `proof_scope`, custody, claim edge, production pack, transaction head, spent window, BENCH, FIRST CHECK, BOUNDARY-PROVEN | `:26-46`, `:57`, `:151-156`, `:337-339` | **PASS** — all glossed in plain words at or before first use; the transaction-head gloss even gives the comparison mechanism. |
| tree hash | `:117`, mechanism at `:139-142` | NIT — term precedes its definition by 22 lines. |

**Replication failures (steps that cannot be executed from the text alone):**
1. `:167` "For each manifest-declared `$RUN_ID`" — no command, file, or field for enumerating run ids.
2. `:239-241` "Set `COLLECTION_MANIFEST_ID`, `EVALUATION_BASIS_SHA256`, `CONSUMPTION_SEMANTICS_ID` from the authenticated inputs" — no path, no field, no command.
3. `:254-256` "Set `FINAL_PINSET_SHA256` and `CALIBRATION_CUSTODY_STORE` from the authenticated inputs" — same.
4. `:197-204` consumes `$CUSTODY_ROOT/prospective/*`, `$CUSTODY_ROOT/calibration/*`, `$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json` **pre-window**. The doc never says who stages them. Per `SHAKEDOWN-G2-RUNSHEET.md:1152-1156`, incomplete staging yields `analysis_finalization_prospective_invalid` — which this doc's `:219-221` rule scores as **FAIL**. A reader will hit that trap.
5. `:301` "Set `FINALIZED_MANIFEST` to the emitted finalized-manifest path" — no filename or pattern.
6. `:100` `EVIDENCE_ROOT_ID='declared-floor-producer-evidence-root-id'` and `:99` `CALIBRATION_LEDGER` are bare placeholders with no derivation instruction.

**NIT — L10-A's step numbers do not render.** `:166`/`:177`/`:188` are `1.`, `2.`, `5.` in one Markdown ordered list; CommonMark takes the start from the first item and renumbers, so step 5 renders as "3." (L10-B `3./4.` and L10-C `5./6./7.` render correctly because their lists *start* at those numbers). *Fix:* break the list before `5.` or use an explicit non-list heading.

### 4. KERNEL COHERENCE

The kernel shape is exactly right and matches R-1: `L10-A-G2B-CONTRACT-PREFIX-01` (lane `agent`, three acceptance rows naming the singleton reason, `proof_scope L10_A_G2B_CONTRACT_PREFIX`, and equal before/after tree hashes) is a hard **start** dep of `V5-TRANSACTION-01`; the parent `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01` has a hard **close** dep on `V5-TRANSACTION-01` and a start dep on L10-A, with "L10-A alone does not close it (ruling 89 R-1)". The `proof_scope` literals in `:339` match the kernel byte-for-byte. **The drift is entirely doc-side:** §D describes the kernel as it was before `f022abd9` (BLOCKER-2), and no row id is ever named (BLOCKER-2, BLOCKER-4).

### 5. Mechanical

Covered above: BLOCKER-1 (command cannot run), BLOCKER-4 + SHOULD-FIX-2 (anchors/paths), SHOULD-FIX-3 (`$PACK_ROOT` absent), SHOULD-FIX-5/6 (shell continuity), NIT (list numbering). All five referenced scripts exist; `--expect-finalize-refusal`, `--scratch-dir`, `--expected-refusals` all exist as documented (`check_window_provenance.py:431-450`); `committed_pack_tree_sha256` exists (`joulewise/arm_readiness.py:2736`). `g2b_tree_hash` (`:139-142`) is sound.

---

### VERDICT: **NEEDS FIX ROUND**

The ruling's *substance* landed well — the ladder, the BENCH lane, the singleton-reason PASS, the tree-hash proof, the `proof_scope` literals, the struck ED-FIRST, the ED-L10-1 correction and eight of the ten Q5 sentences are all implemented and correctly sourced, and the kernel rows match R-1 exactly. But the round fails on its own terms in four places. BLOCKER-1 is the serious one: the copied-verbatim step-5 command passes a `--runs-root` outside `--custody-root`, so `_copy_path` refuses before the finalizer is ever called and the ruled PASS criterion is unreachable as written — a defect a delta re-audit exists to catch, since the sentence describing the command is correct and only the command is wrong. BLOCKER-3 and BLOCKER-4 are a systematic citation collapse: this is a fix round whose whole mandate was "every sentence is sourced to a citation that says it," and thirteen citations now point at the wrong line, seven of them broken by an edit made in the same commit. BLOCKER-2 leaves §D asserting the opposite of the kernel at the head it will be merged into. And the pedagogy pass regressed rather than advanced: deleting the Strict-validation, Reduction and Finalization rows from the flow table removed the only plain-language glosses those three stages had, while **member cover** — the term the entire L10-A verdict turns on — is still never explained, so a reader cannot distinguish the ruled PASS from a staging bug. Fix the step-5 custody containment, re-derive every anchor at the merged head, rewrite §D against the installed row ids, and build the five failing terms at first use; then re-audit the delta.
