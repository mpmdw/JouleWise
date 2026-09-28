RULING: D138-25G83-DESIGN-01 ISSUED

# Cold design ruling D138-25G83-DESIGN-01 — how the epoch-25G83 calibration candidate becomes the issued, active calibration file

Judge: Claude Fable 5.1, cold session, 2026-09-27 18:14–18:28 PDT (wall clock of the bench machine, from `date`). Code read at `/Users/edr/code/JouleWise-wt-d138-scout-d528efb2` (HEAD `c772b019`; its only code difference from main `e7c8bcc6` is `tests/test_gen_state.py`, checked with `git diff --stat e7c8bcc6 HEAD -- joulewise scripts configs tests`). Every "executed" below was run by me in this session; probes are in `/tmp/cg-d138design-d528efb2/` (`probe0.py` `a1bfbf3c…`, `probe1.py` `9b0b438b…`, `probe2.py` `fcec0b7b…`). No repository file was modified except this one.

## 0. Contamination disclosure

1. **Injected by the session harness before the charge, not opened by me:** the owner's global instruction file (a writing standard and a list of skill names), the project instruction file (notes on the model bridge), and a one-line-per-entry index of the owner's memory store. The index includes lines such as "candidate dbad7cc7 cleared → D-138 next; claim-window HOLD", the owner directive that anything bearing on whether a number is true is mandatory, and the light-gate rule for documentation. I opened no memory file, no `RUN_STATE.md`, no `TASK_QUEUE.md`, no `AGENTS.md`, no `CLAUDE*.md`, and no skill file.
2. **Injected commit subjects.** The five most recent commit subjects were shown to me. One says "cap seats all route R". I use it for nothing; §10 item 6 mentions the possibility it implies and labels it unverified.
3. **Read beyond the packet, on purpose.** The addendum SCI-25G83-CANDIDATE-01-A2 was described as pending. Its ruling file existed when I looked (`40-sci-a2-network-time/21-ruling.md`, sha256 `b35d072b…91ba9c`). I read its verdict line, its disclosure text and its conditions on future windows, to place them. I did not re-judge its science. **The copy I read was the working file, last written 18:20:09 PDT, which differs in 5 lines from the copy committed at `a0fc4b85`** (`git diff --stat`). I did not compare the two. The lead copies D8, the rewording of D1 and D3, and H5 to H7 from whichever text is finally landed on main, and pins that file's digest, not the one above.
4. **What I took from the injected material:** the writing standard, as form. Nothing as evidence. Every fact below is cited to a file and line or to a probe I ran.
5. The scout report cites lines of `RUN_STATE.md` and `TASK_QUEUE.md`. I did not open them and rest nothing on them.

## 1. What is being decided, and the words used

The project measures energy. Its instrument has a timing uncertainty, and a **calibration acceptance file** (below: "the calibration file") states how large that uncertainty may be before a measurement is refused. It is a JSON file holding the calibration captures it was derived from and three numbers derived from them. Terms, each used below only in the sense given here:

| Term | Meaning |
|---|---|
| **Epoch** | The machine state a calibration is valid for: operating-system build, hardware model, power setting, sampling interval, estimator revision, pulse protocol. The old epoch is OS build 25F84; the new one is 25G83. |
| **B** | One capture's measured timing uncertainty, in seconds. |
| **Member** | A capture whose B enters the statistics. The new file has 12. |
| **S, C, level screen** | The three derived numbers. S = 0.013701 s: the largest change in B between the calibration before and after a measurement that is absorbed without comment. C = 0.01902064410651988 s: the largest such change that may be budgeted at all; above it the measurement is refused. Level screen = 0.038078579302948 s: the largest B accepted before a window starts. |
| **Candidate** | The file the preparation tool wrote, marked "not issued": `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json`, sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` (re-hashed by me). |
| **Issued file** | The same content marked "issued", under the name the owner approved, at `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json`. |
| **Loader** | `load_calibration_acceptance_bound` in `joulewise/calibration_bracketing.py:1127`. It is the only way production code reads a calibration file. It accepts a file only if (a) the sha256 of its bytes equals a digest written in the code, and (b) its content passes the validator `_valid_acceptance_bound` (`:712`). |
| **Pin** | A digest or identifier written into code or into another file, so that a change to the pinned thing is detected. |
| **Seal** | A digest stored inside the calibration file over its own content. There are two; §5.3 defines them. |
| **Ledger** | The append-only list of every calibration capture ever taken, valid or not. |
| **Prior set** | The calibration file's own copy of the ledger rows that existed when it was derived (86 rows here). |
| **Disposed row** | A ledger row that a written decision has set aside as diagnostic, never a member. Eleven rows of 2026-09-19 were set aside by decision `D-126-disposition-25G83-v3-2026-09-25`, because they were captured under a launch setting that stretched the sampler's frames. They are listed in `configs/calibration/observation_dispositions.json` ("the disposition file"). |
| **Window** | One scheduled measurement session. **Claim-bearing** means its results may be reported as findings. **Arming** is the step that authorises a window to start. A **pack** is the frozen set of plans and pins a claim-bearing window runs from. |
| **Default** | The calibration file the loader reads when the caller names none (`DEFAULT_ACCEPTANCE_BOUND_PATH`, `:199`). Today it is the old-epoch file, called R7. |
| **The transaction** | The one reviewed change that adds the issued file, teaches the loader to accept it, and moves the default to it. |

**The flow this ruling specifies:**

```
 candidate bytes (dbad7cc7…)      issuance text (lead-authored JSON:
 [gated by science rulings]        reason, D1–D8, holds, ruling digests)
            \                          /
             v                        v
        promotion tool  (new script; pure function of the two inputs)
                       |
                       v
        issued file bytes  --sha256-->  digest X
                       |                   |
                       v                   v
   loader validator (repaired §4)     code pin: registry row for the new id = X
                       |
                       v
   default moves R7 -> new file;  R7 stays registered and loads by explicit path
                       |
                       v
   arm admission list: new id present but HELD (§7) -> no pack naming it can arm
```

Named elements: *candidate bytes* and *issuance text* are the only inputs; the *promotion tool* is §5; *digest X* is the file pin of §6; the *loader validator* is the repaired check of §4; the *arm admission list* is `_issued_d079` in `joulewise/arm_readiness.py:6191`.

## 2. Facts I verified myself

| # | Fact | Evidence |
|---|---|---|
| V1 | The defect reproduces. The candidate, converted in memory to issued form with its row registered, fails validation, and the failing statement is line 989. | `probe1.py`: `False {'line': 989}`. |
| V2 | The cause is exactly eleven rows: marked valid, of the new epoch, from sessions `…-n1-20260919` and `…-n2-20260919`, and their identifiers equal the disposition file's eleven exactly. | `probe1.py`: `foreign valid target-epoch rows 11`, `foreign == disposed set exactly True`. |
| V3 | Skipping those eleven lets the file validate; skipping ten does not; an added twelfth foreign valid row that is not disposed still refuses. | `probe1.py`: `True`, `False`, `False`. |
| V4 | The disposition file's sha256 is `ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c`, 11 rows, one decision id. It equals the preparation tool's pin at `scripts/issue_calibration_acceptance_generation.py:516`. | `probe0.py`. |
| V5 | The loader checks the file's byte digest **before** it runs the validator (`calibration_bracketing.py:1179` then `:1181`). Every other route to a calibration file also ends in the loader (`:1254`). | Read. |
| V6 | The validator does not check the set of top-level keys, nor the keys of `issuance`, nor the keys of `derivation_notes`. A file with an extra note block validates. | `probe1.py`: `extra notes key + extra issuance key tolerated: True`. |
| V7 | None of the seven issued files carries a `candidate_not_issued` key, and each `issuance` block has exactly three keys: `status`, `claim_eligible`, `reason`. | `probe0.py`. |
| V8 | The candidate's bytes equal `json.dumps(parsed, indent=2, sort_keys=False) + "\n"` with Python's default ASCII escaping. They contain no byte above 127. The same holds for R7. | `probe0.py`: `roundtrip indent2 identical True`, `non-ascii bytes False`. |
| V9 | Converting to issued form leaves the input seal unchanged at `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011`, also when a note block is added. | `probe1.py`. |
| V10 | The pinset schema does **not** restrict which calibration identifiers may appear. `acceptance_id` is any non-empty string (`scripts/floor_mint_pinsets/schema_v2.json:166-168`). The screen value is forced only if the identifier is in one of two lists (`:716-792`). An identifier in neither list has its screen unconstrained. | Read. |
| V11 | The arm admission list is a literal set of eight identifiers ending at R7 (`arm_readiness.py:6209-6218`). A pack naming any other identifier is routed as a "successor" pack, which requires an evidence row whose author always refuses (`arm_readiness.py:6185`, `arm_readiness_evidence.py:979-988`). | Read, not run. |
| V12 | The authorisation record read at arm has seven keys and none names the calibration file (`night_gate.py:978`, `arm_readiness.py:10111`). | Read. |
| V13 | Every production caller that reads the default does so without naming a file: `whole_window.py:508`, `analysis_engine/inputs.py:1625,3123`, `scripts/run_campaign.py:4819`, `scripts/mint_floor_artifact.py:965,1743,2036`, and the evaluation itself at `calibration_bracketing.py:2015`. | `grep`, read. |
| V14 | An evaluation compares the measurement's epoch with the epochs the loaded file judges; any differing field makes the result "stale" (`calibration_bracketing.py:2113-2122`). | Read. |
| V15 | The four estimator files and the cap are as addendum A1 binding B1 requires: `386e8254…`, `b583f35a…`, `70f47086…`, `7b9c0d28…`; `DETECTION_PROJECTION_CELL_BUDGET = 165_000` (`powermetrics_fiducial.py:88`). | `shasum`, `grep`. |
| V16 | The committed ledger head pin is sequence 276, digest `476e2ae8…`, equal to the candidate's cutoff. | `configs/calibration/calibration_ledger_head.json`. |
| V17 | **The candidate and both science rulings are not on main.** `git cat-file -e e7c8bcc6:<path>` fails for all three. They exist only on the bookkeeping branch. | Executed. |
| V18 | The existing test that "admits" a synthetic candidate replaces the loader with a mock (`tests/test_acc_25g83_rev5.py:242-244`), so the validator never ran on a new-epoch file. This is why V1 was not caught earlier. | Read. |
| V19 | The rule of §4, prototyped in memory, accepts the real issued form, refuses nine counterfactuals, and leaves all seven older files validating. | `probe2.py`, table in §4.4. |

## 3. Disagreements among the three designs, resolved

| Question | Sol (scout) | Astra | Opus | Ruling | Why |
|---|---|---|---|---|---|
| Does the loader read the disposition file each time it loads? | Authenticate against the pinned file | Yes, read and check the raw-file digest | No; use a table written in code | **No read. Table in code.** | By V5 the issued file's bytes are already pinned, so its prior set and its declared decision cannot change without the loader refusing. A file read at load time can therefore only add one outcome: a correct calibration file refusing because the disposition file later gained rows for another epoch. The table is checked against the file by a test and by the preparation tool (§4.2). |
| Name of the shared module | `calibration_dispositions.py` | same | `observation_dispositions.py` | `joulewise/calibration_dispositions.py` | Matches the sibling modules `calibration_ledger.py`, `calibration_bracketing.py`. |
| `candidate_not_issued` | remove | set to false | delete | **Delete the key.** | V7: no issued file has it. Both forms validate (V6), so this is a consistency choice. |
| Where the disclosures sit in the file | `derivation_notes` | inside `issuance` | `derivation_notes.issuance_record` | `derivation_notes.issuance_record` | V7: every issued `issuance` block has the same three keys, and code echoes that block. Notes are where R7 carries its prose. |
| Extend the pinset schema for the new identifier? | Yes | Yes | No, leave it out as a hold | **Yes, extend.** | V10: leaving it out does not block anything. It leaves the new identifier's screen unchecked, which is the opposite of a hold. |
| Add the new identifier to the arm admission list? | Yes | Yes | Yes | **Yes, and mark it held** (§7.3). | V11 and V12. |
| Is hold H1 enforced in code now? | Separate field, procedural | Yes, at arm | Yes, a hold table checked at two arm sites | **Yes, in this change, at the admission list.** | §7.3. |
| Freeze `scripts/sim_acc_25g83_rev5.py` to R7? | not mentioned | not mentioned | yes (inference) | **Yes.** | It reads the default at `:226` to check a rule it simulated against R7. One line. |

## 4. Item 1 — the loader repair

### 4.1 The problem, in physical terms

A calibration derived from live captures must account for every valid capture of its own registered sessions: each is a member or a named exclusion. Otherwise members could be chosen after their values were seen. The validator enforces this ("completeness", `calibration_bracketing.py:971-1029`). It also refuses any valid new-epoch row from a session outside the registration (`:988-989`), because such a capture's conditions were never registered.

The eleven rows of 2026-09-19 are exactly that: valid, new epoch, outside the registration (sessions W1 and W2 of 2026-09-27). A written decision set them aside. The preparation tool knows the decision and kept the rows in the prior set, which is honest: they happened. The validator does not know the decision, so it refuses the file. The tool that writes and the code that reads disagree about one rule.

**Worked example.** The prior set has 86 rows: 53 valid, 31 ordinary-invalid, 2 systematic-invalid. Of the valid new-epoch rows, 12 are members, 1 is a named exclusion, and 11 are the disposed rows. Today the loop reaches the first disposed row, sees session `d079-epoch-25g83-derivation-n1-20260919`, which is not W1 or W2, and returns False. After the repair the loop skips that row because its identifier is in the decision's list, continues, and then requires members ∪ exclusions to equal the valid rows of W1 and W2, as before.

### 4.2 New module `joulewise/calibration_dispositions.py` — the one home

It imports nothing from `joulewise` except, if needed, the standard library. It holds:

1. `DISPOSITION_REGISTRY_RELATIVE_PATH = "configs/calibration/observation_dispositions.json"` and the absolute `DISPOSITION_REGISTRY_PATH`.
2. `DISPOSITION_REGISTRY_SHA256 = "ba1ba3fc596c9ef7f4014131e5cbc2012559f72bab41cafb89e004056790a63c"`, moved from the preparation tool (`:516`).
3. `DISPOSITION_DECISIONS`: a mapping from decision id to `{"mechanism": <the exact sentence now at tool :517-521>, "content_ids": frozenset of the eleven 64-hex identifiers}`. One entry today, keyed `D-126-disposition-25G83-v3-2026-09-25`.
4. `class DispositionRegistryError(ValueError)`.
5. `parse_disposition_registry(raw: bytes, *, expected_sha256: str) -> dict[str, str]`. A pure function of bytes. In order: the sha256 of `raw` must equal `expected_sha256`; the bytes must parse as JSON with duplicate keys rejected; the value must be a list; every row must have exactly the keys `content_id`, `disposing_decision_id`, `mechanism`; the identifier must be 64 lowercase hex; the decision must be a key of `DISPOSITION_DECISIONS`; the mechanism must equal that decision's sentence; no identifier may repeat. **If `expected_sha256` equals the module's own `DISPOSITION_REGISTRY_SHA256`, the parsed rows must equal the code table exactly**, in both directions. Returns `{content_id: decision_id}`.
6. `disposed_content_ids_for(declared) -> frozenset[str] | None`. `declared` absent (`None`) means the empty list. Returns `None` unless `declared` is a list of strings, sorted, without repeats, each a key of the table. Otherwise returns the union of those decisions' identifiers.
7. `decisions_disposing(prior_ids: set[str]) -> list[str]`: the sorted decision ids whose identifier set intersects `prior_ids`.

**What pins what.** The table is reviewed code, the same trust as the file digests in the loader. The disposition file is pinned by its sha256. The two are tied by item 5's equality, which runs in the preparation tool every time it reads the file and in test D1 below.

**Preparation tool changes** (`scripts/issue_calibration_acceptance_generation.py`):
- `DISPOSITION_REGISTRY`, `DISPOSITION_DECISION_ID`, `DISPOSITION_REGISTRY_SHA256`, `DISPOSITION_MECHANISM` stay as module-level names, now assigned from the shared module. Existing tests patch `issuer.DISPOSITION_REGISTRY_SHA256` and `issuer.DISPOSITION_REGISTRY` (`tests/test_acc_25g83_rev5.py:91,97,197,215,409`); they must keep working unedited.
- `_registered_dispositions(path=None)` keeps its signature and return type. It reads the bytes as today, calls `parse_disposition_registry(raw, expected_sha256=DISPOSITION_REGISTRY_SHA256)` with the name looked up at call time, and converts `DispositionRegistryError` to `PrepareRefusal` with the **same message texts** as today ("registry digest mismatch", "invalid or duplicate row", "unreadable"), because tests match on them.

### 4.3 The validator change

All inside the existing block `if prefix_mode == PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE:` (`:976`). Files of the seven older generations use the other prefix mode and never enter it, so they gain no new rule and no new dependency.

```
 prior set rows ──► for each row that is valid AND of the file's own epoch:
                        │
                        ├─ identifier in DISPOSED?  ── yes ──► skip (row stays in prior set)   [rule e]
                        │
                        ├─ session not W1/W2?       ── yes ──► REFUSE (line 989, unchanged)
                        │
                        └─ else add to REGISTRATION-VALID
 then:  members ∪ exclusions must equal REGISTRATION-VALID   (unchanged, line 1027)
```

*DISPOSED* is the set returned by `disposed_content_ids_for(prior["disposing_decision_ids"])`. *REGISTRATION-VALID* is the existing `registration_valid_ids`. Before the loop, in this order, each failing check returns False:

- **(a) Declaration well-formed.** `disposed_content_ids_for(prior.get("disposing_decision_ids"))` is not `None`.
- **(b) Declaration equals what the table implies.** `decisions_disposing(set(prior_ids))` equals the declared list (empty if absent). This is how the file's recorded decision ids bind: the file cannot declare a decision that disposes none of its rows, and cannot hold a disposed row without declaring its decision.
- **(c) Every disposed row is present.** DISPOSED is a subset of the prior set's identifiers. (This mirrors the tool's check at `:2058-2066`, and prevents a missing-key crash in (d).)
- **(d) No disposed row is inside the registration.** For each identifier in DISPOSED: its row's `session_id` is not a registration session, and it is not a member's identifier.
- **(e) The skip**, first statement inside the loop after the valid-and-own-epoch test.
- **(f) After the exclusions are collected:** DISPOSED and the exclusion identifiers do not intersect.

Nothing else in the validator changes. The prior-set size (86), the inventory {31, 2, 53} and the cutoff (276) are still checked against the registered row.

### 4.4 Tests, each with the change it must catch

All tests build the issued form with the promotion tool (§5) or from the committed issued file, and go through the real validator with **no mock of the loader** (V18). Where a test alters content, it recomputes the whole-file seal so that the refusal comes from the intended check, and it asserts the intended check by a paired control: the same alteration with that one check disabled must pass or fail differently. "Prototype" is my in-memory result from `probe2.py`.

| Id | Input | Expected | The wrong implementation it catches | Prototype |
|---|---|---|---|---|
| L1 | The committed issued file, loaded by path through `load_calibration_acceptance_bound` | loads | the unrepaired validator | True |
| L2 | One added valid new-epoch row in session n1, identifier `aa…a`, not in the table; row count registered as 87 | refuses | skipping by session name instead of by identifier | False |
| L3 | Declaration `["D-126-forged"]` | refuses | accepting unknown decisions | False |
| L4 | Declaration deleted; also emptied; also duplicated | refuses ×3 | ignoring the declaration and using the whole table | False ×3 |
| L5 | One disposed row removed from the prior set; count registered as 85 | refuses | dropping rule (c) | False |
| L6 | One disposed row's session changed to W1 | refuses | dropping rule (d) | False |
| L7 | Table patched to include a member's identifier | refuses | dropping rule (d), member arm | False |
| L8 | Table patched to lack one of the eleven | refuses | a table that drifted from the file | False |
| L9 | Each of the seven older issued files | loads, and the disposition file is **not opened** (assert by patching `Path.read_bytes`/`open` for that path to raise) | any new dependency for old files | True ×7 |
| D1 | sha256 of the disposition file equals the pin; `parse_disposition_registry` of its bytes equals the table | passes | table or file edited alone | — |
| D2 | The existing registry tests in `test_acc_25g83_rev5.py` | pass **unedited** | a refactor that changed messages or patch points | — |
| D3 | A scratch re-run of `prepare-candidate` at the change's head, with the recorded arguments, writes bytes whose sha256 is `dbad7cc7…b5b2` | equal | a refactor that changed the tool's output | lead's bench, §9 |

## 5. Item 2 — the issued bytes

### 5.1 A tool, not a hand edit

**New script `scripts/promote_calibration_candidate.py`.** A pure function of two files. It reads no ledger, no capture and no custody directory. Reviewers re-run it; a test re-runs it on every suite run. The candidate is **not** re-prepared: binding B3 forbids curing anything by re-preparation, the science rulings judged the bytes `dbad7cc7`, and a re-run would read custody again.

Inputs:
1. `--candidate <path>`; the tool refuses unless its sha256 is `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`.
2. `--issuance-text <path>`: the lead-authored JSON of §7.1.

Verbs: `--out <path>` writes the issued bytes (refuses to overwrite a file with different bytes); `--check <path>` exits non-zero unless the file at `<path>` equals the bytes the tool would write.

### 5.2 Field-by-field transform

Parse the candidate rejecting duplicate keys. Refuse unless: both of its seals verify as stored; `acceptance_id` is `d079_calibration_acceptance_v2_n12_25g83_r1`; `artifact_role` is `candidate`; `candidate_not_issued` is `true`. Then walk the candidate's top-level keys **in their existing order**:

| Key | Action |
|---|---|
| `schema_version`, `acceptance_id`, `decision_ids` | unchanged |
| `candidate_not_issued` | **deleted** |
| `artifact_role` | `"candidate"` → `"issued"` |
| `issuance` | **replaced whole** by exactly `{"status": "issued", "claim_eligible": true, "reason": <issuance text `reason`>}` in that key order. The candidate's `licence` sentence goes, as the tool's own comment requires (`:2246-2251`). |
| `ledger_cutoff`, `identity_epoch`, `prospective_rederivation`, `derivation_corpus`, `prior_observation_set`, `decimal_derivation` | unchanged |
| `backfill_candidate` | `status` → `"issued"`; `production_issuance_blocked` → `false`; `required_verification` → issuance text `required_verification`, which must begin `complete: `. `candidate_inventory` and key order unchanged. |
| `derivation_notes` | every existing key unchanged; two keys **appended** in this order: `network_time_provenance` (§7.2), `issuance_record` (§7.1) |
| `registered_generation_row` | unchanged, kept |
| `derivation_input_sha256` | recomputed; the tool refuses unless it equals `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011` |
| `derivation_sha256` | recomputed last |

### 5.3 The two seals and the file pin

- **Input seal** (`derivation_input_sha256`): a digest over the inputs of the arithmetic only: identifier, epoch, cutoff, the 12 member values, statistics, rounding, quantile proof, the operative numbers, and four fields of the registered row. Computed by the production function `derivation_input_sha256` (tool `:2329`). Labels and prose are outside it, so it must come out unchanged (V9). It is recomputed, never copied.
- **Whole-file seal** (`derivation_sha256`): a digest over every key except itself. Computed by the production function `derivation_sha256` (tool `:2315`), which calls the loader's own `_canonical_sha256` (`calibration_bracketing.py:654`): sorted keys, separators `,` and `:`, UTF-8, no ASCII escaping, no NaN. It changes, because labels and notes changed.
- **File pin**: sha256 of the bytes written. It goes into the loader's registry (§6).

### 5.4 Serialization

`json.dumps(issued, indent=2, sort_keys=False, ensure_ascii=True) + "\n"`, encoded UTF-8. This is the recipe that reproduces the candidate and R7 byte for byte (V8). Non-ASCII characters in the disclosure text (µ, §, –) are written as `\uXXXX` escapes; the whole-file seal is computed on the parsed values and is unaffected.

### 5.5 What must stay identical, and how it is shown

The tool ends with a self-check, and test P2 repeats it independently: parse the written bytes; for each path in this list, the parsed value equals the candidate's, and its serialized text is identical: `schema_version`, `acceptance_id`, `decision_ids`, `ledger_cutoff`, `identity_epoch`, `prospective_rederivation` (including the four estimator digests character for character, binding B1), `derivation_corpus` (12 members), `prior_observation_set` (86 rows and `disposing_decision_ids`), `decimal_derivation`, `backfill_candidate.candidate_inventory`, every pre-existing key of `derivation_notes`, `registered_generation_row`, `derivation_input_sha256`.

A line diff of candidate against issued file must show changes only in: the `candidate_not_issued` line; the `artifact_role` line; the `issuance` block; three lines of `backfill_candidate`; the closing line of the last pre-existing note (it gains a comma); the two appended note blocks; the `derivation_sha256` line.

### 5.6 Tests for the tool

| Id | Test | Catches |
|---|---|---|
| P1 | `--check` on the committed issued file passes; sha256 of that file equals the registry pin | hand-edited bytes; a stale pin |
| P2 | The protected-path comparison of §5.5, written without importing the tool's own comparison | a tool that alters a protected field and also mis-checks it |
| P3 | A candidate with one member value altered is refused (digest) ; with its digest check bypassed, refused again (input seal) | a tool that promotes unreviewed numbers |
| P4 | Issuance text lacking any of D1…D8, H1, or a ruling digest is refused | an issued file without its disclosures |
| P5 | The issued file's `registered_generation_row`, passed through `generation_row_for_registry`, equals the code row of §6 | code row and file row drifting apart |

## 6. Item 3 — the pin swap

### 6.1 Must change together

I checked the scout's census line by line against the code. It stands, with the corrections marked ★.

| Path | Change |
|---|---|
| `configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json` | new; tool output only |
| `joulewise/calibration_dispositions.py` ★ | new (§4.2) |
| `scripts/promote_calibration_candidate.py` ★ | new (§5) |
| `joulewise/calibration_bracketing.py` | (i) constants `EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH`, `EPOCH_25G83_R1_ACCEPTANCE_ID`, `EPOCH_25G83_R1_ACCEPTANCE_BOUND_SHA256`; (ii) a new entry in `ISSUED_ACCEPTANCE_REGISTRY` (`:147`); (iii) a frozen literal `_D102_N12_25G83_DERIVATION` with the two list fields as tuples, holding every key of the candidate's row including `predecessor_acceptance_id`, `d125_ruling` and `registration_revision: 5`, registered in `_D102_GENERATION_DERIVATIONS` (`:377`); (iv) `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` (`:198-199`) point to the new constants; (v) the §4.3 repair |
| `joulewise/arm_readiness.py` | §7.3 |
| `scripts/floor_mint_pinsets/schema_v2.json` | new list `n12Epoch25g83AcceptanceIds` with the one new identifier; a third conditional on **both** surfaces (`finalProducer` near `:716`, `pinRequirements` near `:1000`) forcing `bracket_screen_s` = `"0.013701"` and `allowance_rule` = `"max(observed_drift_s,0.013701)"` |
| `scripts/issue_calibration_acceptance_generation.py` | §4.2; and the two freezes of §6.3 |
| `scripts/epoch_equivalence_check.py` | §6.3 |
| `scripts/sim_acc_25g83_rev5.py` ★ | §6.3 |
| `tests/verify_calibration_acceptance_corpus.py` | bank the new generation (n 12, stored value is the member value, minimum, maximum, range, mean, standard deviation from the candidate's statistics); accept a `corpus_root` argument, because the members live under `/Users/edr/night-custody`, outside the repository (`:88-89` assumes inside) |
| Tests listed in §8.1 | re-point expectations that meant "R7" but read "the default" to the explicit R7 constants; add expectations for the new default. **No assertion is weakened or deleted.** |

`tests/test_floor_mint_pinsets_schema.py` gains one assertion that closes V10 for the future: every identifier in `ISSUED_ACCEPTANCE_REGISTRY` appears in exactly one of the schema's identifier lists.

### 6.2 What stays

- R7's file, registry entry, row and digest `9c3a29f6…fe16`, and those of the six older generations. The loader selects the pin by the file's own identifier (`:1175`), so R7 still loads when named by path, and still judges epoch 25F84.
- The disposition file, the registration document (`81b65f08…`), the ledger head pin, every existing pack and its frozen receipts. No pack is re-minted.
- The four estimator files and the cap (bindings B1, B2).
- `EPOCH_CONTINUATION_REGISTRY` stays empty.

### 6.3 Consumers frozen to R7

Three tools mean "R7" but read "the default". Each is changed to name R7:

1. Preparation tool `:1798-1800`: compare with `ANCHOR_V3_R7_ACCEPTANCE_ID`, not `ACTIVE_ACCEPTANCE_ID`. The refusal message keeps the words "requires r7 predecessor" (a test matches them). `:2553`: the default of `--predecessor-acceptance` becomes `ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH`.
2. `scripts/epoch_equivalence_check.py:699`: the default of `--acceptance` becomes the R7 path. Its required identifier is already R7 (`:152`).
3. `scripts/sim_acc_25g83_rev5.py:226`: load the R7 path.

Test for each: with the default moved, the tool's default argument resolves to the R7 file and the tool's R7 check passes. Counterfactual: the unfrozen code, under the moved default, fails that test (Opus executed this for item 1: 6 of 12 tests of `test_acc_25g83_rev5` fail at `:1798`).

### 6.4 What moves with the default, by design

The desk check (`:389`), the evaluation (`:2015`), and the ledger-baseline readers of V13. Their baseline becomes sequence 276, which equals the committed head pin (V16). §10 item 2 rules on the consequence for old-epoch measurements.

## 7. Item 4 — disclosures and the hold

### 7.1 Where they live: both places

**In the issuing record** (lead-owned, `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/00-issuing-record.md`): D1 to D8 in full, with D1 and D3 in the wording addendum A2 gives; H1 to H7; bindings B1 to B4 with the digests measured before issue and after merge; the owner's approval of the name (activation record item 17); digest X; the before-and-after replay of §10 item 2.

**In the issued file**, as `derivation_notes.issuance_record`, built by the tool from the issuance text:

```
"issuance_record": {
  "transaction": "D-138 issuance of epoch 25G83, design ruling D138-25G83-DESIGN-01",
  "source_candidate": {"relative_path": …, "file_sha256": "dbad7cc7…", "derivation_sha256": "fac6e6f8…"},
  "rulings": [ {"id": "SCI-25G83-CANDIDATE-01",    "relative_path": …, "file_sha256": "f9de51b7…"},
               {"id": "SCI-25G83-CANDIDATE-01-A1", "relative_path": …, "file_sha256": "be13ccba…"},
               {"id": "SCI-25G83-CANDIDATE-01-A2", "relative_path": …, "file_sha256": <as landed on main>} ],
  "disclosures": [ {"id": "D1", "text": …}, … , {"id": "D8", "text": …} ],
  "holds":       [ {"id": "H1", "text": …}, {"id": "H5", …}, {"id": "H6", …}, {"id": "H7", …} ],
  "claim_eligible_meaning": <the sentence of §7.4>,
  "hold_enforcement": "H1 is enforced outside these bytes, at the arm admission list; lifting it changes no byte of this file"
}
```

The text of each disclosure and hold is the ruling's own sentences, copied, not paraphrased. The tool requires `disclosures` to carry ids D1…Dn in order with n ≥ 8, and `holds` to include H1. **A later disclosure is one more list element in the issuance text; nothing in the tool or the validator changes.** That is how D8 was accommodated, and how a D9 would be.

The issuance text is `docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance/10-issuance-text.json`, with keys `reason`, `required_verification`, `network_time_provenance`, `issuance_record`. The lead writes it. The seat reads it and does not edit it.

### 7.2 The network-time block

Addendum A2 left to this gate whether the file carries a `network_time_provenance` block. **It does.** R7 carries one (I printed it from the R7 file: `per_member_state: "unknown_in_artifact"`), the clock method says this provenance travels with every record, and A2 found the candidate has none. A note block changes the whole-file seal and the file digest, which do not exist yet, and nothing else (V9). Content: `{"state": "on_during_both_capture_windows", "disclosure_id": "D8", "source_ruling": {path, sha256}, "text": <D8 verbatim>}`. I place the block; I do not rule on its science.

### 7.3 H1 is enforced in code, in this change

**Forcing problem.** Until now no claim-bearing window could run at 25G83, because no calibration file judged that epoch. Merging the transaction removes that obstacle. Windows are armed by an unattended loop. If H1 were only a sentence in a record, the moment of greatest risk would be the moment of merge. So the enforcement must merge with the file, or before it.

**Where.** The authorisation record read at arm does not name the calibration file (V12), so a check there would need new plumbing through the arm path; that is a design of its own. The admission list does see the pack's calibration identifier (V11), and an identifier it does not admit cannot arm. So:

In `joulewise/arm_readiness.py`:
```
_ISSUED_D079_IDS = frozenset({ …the eight existing…, "d079_calibration_acceptance_v2_n12_25g83_r1" })
# Identifiers that are issued but may not yet back a pack.  Each entry names its hold.
_CLAIM_HELD_ACCEPTANCE_IDS = {
    "d079_calibration_acceptance_v2_n12_25g83_r1": "H1-25G83-CAP-CADENCE (SCI-25G83-CANDIDATE-01-A1 §5.3)",
}
… return issued in _ISSUED_D079_IDS and issued not in _CLAIM_HELD_ACCEPTANCE_IDS
```

**Tests.**
- H-T1: a synthetic pack tree naming the new identifier gives `_issued_d079` False, the successor row is REQUIRED, and the evidence author refuses. Counterfactual: with `_CLAIM_HELD_ACCEPTANCE_IDS` patched empty, the same tree gives True and the row is NOT_APPLICABLE.
- H-T2: a tree naming R7 is admitted, before and after.
- H-T3: every identifier in `ISSUED_ACCEPTANCE_REGISTRY` is in `_ISSUED_D079_IDS`; every held identifier is in the registry.

**Release.** A reviewed change that deletes the entry and cites the written ruling closing the cap question by route R or route M. No flag, no environment variable.

**Known cost, stated plainly.** This holds every pack that names the new file, including a pack used for a rehearsal that carries no claim. H1 permits non-claim windows. The windows that gather H2's evidence run under the no-pack night class (the class W1 and W2 ran under) and are not affected. If a non-claim pack window at 25G83 is needed before H1 lifts, a separate lane designs a purpose-aware check; it is not part of this change.

**Not verified by me.** V11 was read, not run; H-T1 is what proves it. I also did not trace whether any route from the issued file to a reported result avoids packs altogether (for example a campaign script run by hand). §9 step 6 gives this to a refuter with a stop.

### 7.4 What `claim_eligible` means

`claim_eligible: true` in the file means: *these bytes are an authentic issued calibration, and its numbers may serve as the timing-uncertainty basis of a reported result.* It is a property of the file. It is not permission to start a window. Permission to start a claim-bearing window is separate; H1 withholds it, and H5 to H7 condition it.

It stays `true` because the loader requires it of any issued file (`:754`), because the science rulings judged the numbers fit for that use, and because writing `false` would force a second issuance with no number changed when H1 lifts. The sentence above goes into the file verbatim as `claim_eligible_meaning`.

H5 (network time OFF for every window) and H6 (per-capture log attestation) are conditions on future windows. They are recorded in the file and the issuing record. Their enforcement in the capture chain is its own lane and **must land before the next window at 25G83 of any kind**; it is not part of this change, and B2 is not engaged because A2 states H5 can be met from the arming session without touching a pinned file.

## 8. Item 5 — WRITE_SCOPE and the lead's bench

### 8.1 The one implementation seat — exhaustive list

```
configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json   (tool output only)
joulewise/calibration_dispositions.py                                  (new)
joulewise/calibration_bracketing.py
joulewise/arm_readiness.py
scripts/promote_calibration_candidate.py                               (new)
scripts/issue_calibration_acceptance_generation.py
scripts/epoch_equivalence_check.py
scripts/sim_acc_25g83_rev5.py
scripts/floor_mint_pinsets/schema_v2.json
tests/test_calibration_dispositions.py                                 (new)
tests/test_promote_calibration_candidate.py                            (new)
tests/test_calibration_bracketing.py
tests/test_acc_25g83_rev5.py
tests/test_floor_mint_pinsets_schema.py
tests/test_epoch_continuation.py
tests/test_issue_calibration_acceptance_generation.py
tests/test_epoch_equivalence_check.py
tests/test_arm_readiness_evidence_author.py
tests/test_calibration_exits.py
tests/test_calibration_writer_crash_matrix.py
tests/test_mint_floor_artifact_generalized.py
tests/test_powermetrics_fiducial.py
tests/verify_calibration_acceptance_corpus.py
```

Rules for the seat: nothing outside this list, including the four estimator files, the disposition file, the registration, any older calibration file, any pack, any document. If the suite shows a failure whose cure lies outside the list, the seat stops and reports the path; the lead amends the scope in writing. An amendment may add test files only, for re-pointing R7 expectations only.

### 8.2 The lead, at the bench

Before the seat starts:
1. **Land the records on main** (V17): the candidate, the two science rulings, addendum A2, this ruling and the design packet. A documentation-only change. Re-hash the candidate on main: `dbad7cc7…b5b2`.
2. **Write the issuance text** (§7.1) and commit it, so the seat's worktree contains it.
3. **Census check by execution.** In a scratch worktree, move the default in memory and run the whole suite once; list every failing test file. Compare with §8.1 and amend before launch. No seat ran the whole suite under the moved default; Astra names `test_issuer_corpus_root` and the mint suites as possible additions.

After the seat returns: §9 steps 1 to 4 and 9, the issuing record, the decision-log entry (including the amendment of the sentence "The issuer's A-7 check is the sole new registry consumer", `docs/decision_log.md:12199`, which the loader repair makes untrue), and the trackers.

## 9. Item 6 — verification and gate sequence

1. **Pre-issue re-hash, at the change's head, recorded:** candidate `dbad7cc7…`; its two seals `e7363bdd…`, `fac6e6f8…`; the four estimator files (V15) against B1 and against the candidate's own block; cap 165,000; registration `81b65f08…`; disposition file `ba1ba3fc…`; R7 file `9c3a29f6…`; ledger head 276 / `476e2ae8…` in the repository and in the W2 measurement checkout; the two battery verdict files at the digests of the scout's E4; the three science rulings. B2: none of `bda7ffe0`, `aeea07b6`, `ea10e3c8`, `5135c1d2` is an ancestor of the head, and `git diff origin/main...HEAD` names none of the four files.
2. **Independent replay**, by a seat that did not write the bytes: (i) `promote_calibration_candidate.py --check` passes and the file digest equals the pin; (ii) the line diff touches only the lines of §5.5; (iii) S, C and the level screen re-derived from the 12 member values in 80-digit arithmetic with an independently computed t-quantile; (iv) `verify-members --corpus-root /Users/edr/night-custody`: 12 PASS, custody digests equal before and after; (v) test D3, the scratch re-preparation, byte-equal to `dbad7cc7`; (vi) on the real ledger, read-only: the default evaluates "fresh" for a 25G83 identity, and R7 named by path evaluates "fresh" for a 25F84 identity.
3. **Old-epoch replay** (§10 item 2).
4. **Whole suite** on the head merged with current main: `/opt/homebrew/bin/python3 -B -m unittest discover -s tests`. Green, no new skip. The one known machine-dependent failure the scout saw (`test_live_probes_report_this_machine_against_the_active_epoch`, `os_build` read as `None` in a sandbox) is re-run on the bench, where it must pass.
5. **Mutation evidence, executed and recorded:** for L2, L4, L5, L6, L7, L8, P3, H-T1 and the three freezes of §6.3, the named wrong implementation is applied and the test is shown to fail.
6. **Two refuters with different charges.** Contract: authentication and pins (can any file other than the committed one load under the new identifier; can the table and the file disagree undetected; is any R7 consumer still reading the default). Hold: find any route from the issued file to a claim-bearing result that does not pass the admission list. **If one is found, the transaction stops until it is closed.**
7. **Pedagogy pass** on the issuing record and the decision-log entry, as its own review: every term built or glossed at first use.
8. **Re-audit of the difference** after every fix round.
9. **Cold final pass** on the final head: a fresh judge, given the final diff, the issuing record and this ruling, confirms each numbered item of this ruling is met. The merge is irreversible in effect, because other files may pin digest X afterwards.
10. **Merge** as one commit to main.
11. **Post-merge, on main:** the four estimator digests and the cap again (B1's second measurement); the loader reads the default and returns the new identifier; sha256 of the issued file equals the pin; R7 loads by path; `_issued_d079` refuses the new identifier. Recorded in the issuing record.

## 10. Item 7 — what stops or re-orders the transaction

1. **Re-order: records to main first** (V17). The tool and its tests read the candidate by path. Until it is on main the change cannot be built on main.
2. **Old-epoch measurements under the new default: mandatory check before merge.** Opus raised it; I confirm the mechanism from code (V13, V14): after the move, a recorded 25F84 measurement evaluated through the default is compared with a file that judges 25G83 only, and comes back "stale". R7's move never showed this, because R7 kept its predecessor's epoch. The lead runs one recorded 25F84 analysis at main and at the change's head and compares outputs.
   - Identical: proceed.
   - A clean refusal naming the stale calibration: proceed. A refusal cannot make a reported number wrong. It does mean old-epoch results can be re-evaluated only from a commit before the move, until a lane gives them a route that names R7. The issuing record says so, and the lane is opened.
   - **Any number that differs, or any refusal for another reason: stop.**
3. **Stop on B1 or B2.** Any mismatch in step 1. It is not cured by re-preparation (B3).
4. **Stop if H-T1 cannot be made to pass as written.** Then V11 is wrong, the hold is not mechanical, and the hold needs its own design before merge.
5. **Stop if the input seal does not come out `e7363bdd…`.** Then the transform touched an input of the arithmetic.
6. **Not a stop.** If the cap question is ruled by route R, binding B4 makes this file stale when the cap changes and forces a second issuance. I have one unverified indication that this is likely (§0 item 2). Issuing now still gives the machine a calibration that matches its epoch, and proves the loader repair and the promotion tool once. The hold of §7.3 means no claim rests on this file meanwhile.
7. **Before the next window of any kind at 25G83:** H5 and H6 of addendum A2. Outside this change; inside the lead's ordering.

## 11. Limits of this ruling

- I ran no test suite. The defect probe and the rule prototype are in-memory; they show the rule is right on the real candidate and on nine counterfactuals, not that an implementation is.
- V11, the arm routing, was read and not executed.
- I did not run the old-epoch replay of §10 item 2, nor trace every consumer of authentication-session records; my ruling against a load-time file read rests on V5, not on that trace.
- The test-file list of §8.1 is the scout's census plus three new files. It has not been checked by a whole-suite run under the moved default; §8.2 step 3 does that.
- L6 in my prototype may have refused at the completeness equality and not at rule (d); the paired control in §4.4 exists to separate them in the real test.

## Summary

1. The three designs agree on the shape and I adopt it: repair the loader so it skips exactly the eleven set-aside rows by identifier, using a table in one shared module; produce the issued file with a re-runnable tool from the gated candidate plus a lead-written text of disclosures D1–D8 and the holds; move the default and keep R7 loadable.
2. Where they disagreed I checked the code: the loader does not read the disposition file at load time; the pinset schema must be extended, because leaving the new name out checks nothing; and the hold on claim-bearing windows is enforced in code in this same change, at the list that admits calibration files to packs.
3. Before building: put the candidate and the rulings on main, and check what the moved default does to one old-epoch analysis; a changed number there, a broken estimator pin, or a hold test that cannot pass stops the transaction.
