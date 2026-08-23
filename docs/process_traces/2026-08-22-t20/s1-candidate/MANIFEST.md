# S-1 CANDIDATE MANIFEST — the `_v4` reviewed candidate custody (2026-08-22)

**Status: FINISH ROUND COMPLETE FOR THE TEN AUDITED GAPS; STILL NOT
LEAD-REVIEWED, STILL NOT ACCEPTED.** This manifest is the binding record of
what the S-1 implementation contains and what it does not. §8's verdicts were
authored by the conformance-audit seat against `bd7ebc1`; §9 records the
finish round that closed them, re-verified at source, and it flips a §8 verdict
only where the mechanism genuinely changed.

**One NEW blocker, larger than any of the ten gaps, was found during the
finish round and is NOT cured: the candidate is red on 149 tests outside the
four modules it was ever run against (§9.3, gap G-11).** The cure is
mechanical but lies outside the finish round's write lease. This candidate
still cannot be handed to S-0.

Kernel row: `S1-CANDIDATE-01` (TASK_QUEUE.md rank A81; acceptance at
`docs/process/state_kernel.json` `/tasks/S1-CANDIDATE-01/acceptance`).

## 1. Coordinate

| Item | Value |
| --- | --- |
| Worktree | `/Users/edr/code/JouleWise-wt-s1` |
| Branch | `impl/s1-candidate` |
| Audited commit (§8 verdicts) | `bd7ebc13f6f631f73a64b54b5b13ae29a4d491dc` |
| Finish-round head (§9 verdicts) | `b1c6beedc363d7bf57b3035068a11190ccb55a4e` |
| Finish-round tree | `d36e8b9d7b3f24f937ce0202665b14eff0cebc7b` |
| Baseline (merge-base with `main`) | `55230038dd517e250e47d0685b093110f610b3e8` |
| Diff under audit | `git diff 5523003...bd7ebc1` (14 files, +3578 / -78) |
| Diff at finish-round head | `git diff 5523003...b1c6bee` (18 files, +5061 / -88) |
| Worktree cleanliness | clean at both points (`git status --porcelain` empty) |

`main` has since advanced one commit (`ae2a0f2`, a `RUN_STATE.md`
bookkeeping-only change). Every comparison in this manifest is taken
against the **merge-base** `5523003`, so the advance does not affect any
verdict below.

## 2. Changed paths and their roles

Fourteen paths change. "Role" names what the path is FOR in the `_v4`
transaction; "authority" names the ruling that ordered it.

### 2.1 Governance artifacts (data the code reads)

| Path | Δ | Role | Authority |
| --- | --- | --- | --- |
| `configs/arm_readiness/d117_row_registry_v2.json` | +977 (new) | The R1 candidate registry: the ruled `d117-row-registry-v2` coordinate carrying the 112-path changed-set allowlist, the eight-code R1 refusal vocabulary, the 29 evidence freshness policies with D-150 horizons, and `successor_policy` (the tracked `_v4` roster). | D-151 cond. 1 + 8; D-150 (2) |

The v1 registry `configs/arm_readiness/d117_row_registry_v1.json` is
**byte-identical to the baseline** (verified by SHA-256 against
`5523003`) and remains in the tree as the archival companion, as ruled.

### 2.2 Contract documents (the normative prose)

| Path | Δ | Role | Authority |
| --- | --- | --- | --- |
| `docs/contracts/d117_step6_confirmation_table.md` | +131 (new) | The ONE HOME for the unified step-6 confirmation table `joulewise.d117_step6_confirmation_table.v1`: its two sections (family-publication, successor-pinset), its custody rule, and the acyclic two-consumer digest graph. Neither consumer contract may restate it. | Marker ruling ¶2 |
| `docs/contracts/receipt_histsem_verifier.md` | +41/−? | The chain contract amendment: the governed pinset becomes a **closed, ordered, code-enumerated chain** of two versioned members; adds the un-enumerated-file-governs-nothing rule, the cross-member duplicate-identity refusal, and the unchanged-absence-semantics paragraph. Defers the confirmation schema to the ONE home above. | D-151 cond. 1 + 6 |

### 2.3 Library code

| Path | Δ | Role | Authority |
| --- | --- | --- | --- |
| `joulewise/arm_readiness.py` | +1141 | Carries five distinct deltas: (a) `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` constant → 2-tuple and the chain-read loops in `_load_histsem_pinset` / `_gate_receipt_histsem`; (b) `ROW_REGISTRY_RELATIVE_PATH` repointed `v1 → v2` (`:87`); (c) the family-publication marker schema, builder core, verifier core, and the `_gate_family_publication` library-boundary gate; (d) the `readiness_r1_family_publication` CUSTODY reason code plus the registry-load closure check (`:1881-1888`); (e) r4-5's two `EvidenceLifecycleError` catches at the arm and verification entry points (`:7161`, `:7377`). | D-151 cond. 1/6; marker ruling ¶4, splits S-1/S-3/S-4 |
| `joulewise/arm_readiness_evidence.py` | +31 | Evidence-side adjustments consequential to the registry v2 coordinate and the chain read. | D-151 cond. 1 |
| `joulewise/scheduler_gates.py` | +296 | Scheduler gate receipt bumped to `joulewise.window_scheduler_gate_receipt.v2` with the explicit **G7** family-publication gate: exact-key `family_publication` block, `GATE_IDS` seven wide, the six-code G7 reason set, nulls-on-refusal, and `go_eligible` bound to the G7 verdict. | Marker ruling ¶6 |

### 2.4 Custody tools (executed by S-0, not by CI)

| Path | Δ | Role |
| --- | --- | --- |
| `scripts/build_family_marker.py` | +64 (new) | Builds the family-publication marker at the freeze boundary into custody OUTSIDE the repository. |
| `scripts/verify_family_marker.py` | +124 (new) | Verifies a marker: digest equality, semantic replay of the three `freeze-0004` receipts, strict four-way head equality, and (non-candidate phases) the confirmation-table C→M edge. |
| `scripts/build_v4_histsem_pinset.py` | +331 (new) | Mints the successor pinset artifact (§3) from the three post-freeze packs. |
| `scripts/verify_receipt_histsem.py` | +1/−1 | Docstring only, to name the chain. CLI flags are byte-identical to baseline — the ruled "CLI unchanged" condition. |

### 2.5 Tests

| Path | Δ | New test functions |
| --- | --- | --- |
| `tests/test_family_marker.py` | +294 (new) | 11 |
| `tests/test_receipt_histsem.py` | +64 | 3 |
| `tests/test_scheduler_gates.py` | +95 | 2 |
| `tests/test_arm_readiness_schemas.py` | +65 | 4 |

Twenty test functions added; **zero pre-existing tests deleted, renamed, or
weakened**. The only two deletion lines in the whole `tests/` diff are
count tightenings: `len(READINESS_REASON_CODES)` 47 → 55 and
`len(receipt["gates"])` 6 → 7.

## 3. The successor pinset path binding

The successor artifact is

```
configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json
```

**This file is deliberately NOT PRESENT in the candidate tree.** It is
minted by S-0 after the three `freeze-0004` artifacts exist, by
`scripts/build_v4_histsem_pinset.py`. Its path is bound in three places at
candidate time, and only its path — never its bytes:

1. As the **112th entry** of the changed-set allowlist. The arithmetic is
   exact and verified: 3 packs × 37 paths = 111 pack paths, plus this one
   successor path = 112. The allowlist contains no other non-pack path;
   the OLD `legacy_receipt_histsem_pinset_v1.json` is NOT in it (the
   successor replaces it in the `+1` slot). "112th entry" is the
   membership sense — the list is stored sorted, so the successor path
   sits at sorted index 7, not at the end. No ruled number is amended.
2. As member 2 of the code-enumerated chain tuple
   `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` in `joulewise/arm_readiness.py`.
3. As the `path` value the step-6 confirmation table's `successor_pinset`
   section must equal (checked in `validate_step6_confirmation_table`).

**Custody consequence.** Because the file is absent, every chain test in
this candidate runs against synthetic members in temporary directories.
No test has ever exercised the real successor bytes. That is expected at
S-1; it means the chain's behaviour against the real artifact is first
observed during S-0 and must be transcribed there.

**Gap (see §8.6, G-2): the digest side of this binding does not exist.**
The path is subtracted from the changed set unconditionally.

## 4. The marker branch

Per **D-150 item (3)**, Ed ruled the marker as **option (a),
BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL**:

- The marker is built after the freeze x3 boundary by
  `scripts/build_family_marker.py`, and it lives in **transaction custody
  outside the Git worktree** — it is not a tracked repository file.
- Therefore r4-1's conditional two tracked marker paths do **not** engage,
  and the changed-set contract stays at **112**, not 114. The registry's
  allowlist was verified to contain no `family_publication` path
  (asserted in `tests/test_arm_readiness_schemas.py:373`).
- Option (b) `UNBUILT.v0` is dead and its runsheet branch is removed by the
  separate S0-RUNSHEET-R2 work order (A82), not here.
- The builder enforces custody-externality itself: an `--output` inside the
  repository refuses with `output_in_tree`.

## 5. Test commands and the lead-run record

The four modules that carry this candidate's regressions:

```bash
cd /Users/edr/code/JouleWise-wt-s1
python3 -m unittest \
  tests.test_family_marker \
  tests.test_scheduler_gates \
  tests.test_arm_readiness_schemas \
  tests.test_receipt_histsem
```

**Lead-run record:** `Ran 87 tests ... OK` — four modules, recorded
2026-08-22 ~22:45 PT, and **independently re-run by the audit seat at
audit time with the identical result** (87 tests, OK, ~101 s, worktree
left clean).

Two cautions that belong on this record:

- 87 green is green **for what is asserted**. §8.6 shows a large fraction
  of the ruled regression union is not asserted at all; a green run is not
  evidence of the coverage the ruling ordered.
- This is a LOCAL suite run. It is not, and must never be reported as, the
  two-part green of D-151 condition 4 (local green in the S-0 clone is
  forged-`origin/main`-conditional; acceptance closure requires PUBLISHED
  green).

## 6. Tool digests

SHA-256, GNU coreutils form (`<64 hex><two spaces><basename>`), computed at
the **finish-round head `b1c6bee`**. Three of the four tools changed in the
finish round; the digests recorded against `bd7ebc1` are superseded and are
preserved only in this repository's history.

```
e51617f9cdbbcac2e8e5558c5422c701e3091476c267d11427189bfc3a82f50b  build_family_marker.py
9a4d9d10c4f5c07df81a3673efeb1b3d14787c93a42292a074a2e00d1c1e10b9  verify_family_marker.py
29335e6fcfe8e97a78212f44e44a96e869d3179afb3411cda74f2a8070b978fa  build_v4_histsem_pinset.py
394ed1992c26cff150c8a9bfe026ba787e99a37428e3ee4010fe381a29b0d860  verify_receipt_histsem.py
```

Governance artifacts, same form and commit:

```
7a1642130eedaa528059c59304fa32813cc884b5f0b9c338634946ef105297b7  d117_row_registry_v2.json
2316688a29285a0778d5d7134e55aee73568c561a17695a1913d32ef5e7766f6  d117_step6_confirmation_table.md
23e75396b14ebd28b11c49e1e7346259594e3d4d363ec590d4cc26dabdf2d63f  receipt_histsem_verifier.md
```

**The four `.sha256` sidecars now exist** beside their tools
(`scripts/<tool>.py.sha256`), in the same GNU form, and verify with
`shasum -a 256 -c`. S-0 runsheet §1.3 runs exactly that check.
`tests/test_family_marker.py::test_custody_tool_sidecars_exist_and_are_current`
fails the suite if a tool is edited without regenerating its sidecar, so they
cannot silently go stale.

**The §6 caution that forbade in-tree sidecars is DISCHARGED.** It existed
because `_family_tool_reference` selected candidate mode by the mere PRESENCE
of a `<tool>.sha256` file, so an in-tree sidecar would have silently disabled
the production committed-blob rule. The finish round removed that selector
entirely (gap G-4, §9.1): the lane is chosen by an explicit `phase` argument,
and candidate mode authenticates against the reviewed `$INPUT` manifest rather
than against any sidecar. Nothing in the gating path now reads these files.

**`s0-candidate.patch` is still not in either tree, by design.** The patch is
the export of this branch against the merge-base
(`git diff --binary 5523003..b1c6bee`), and exporting it before gauntlet close
would pin a digest that every subsequent fix invalidates. The lead exports it —
with its GNU sidecar — at gauntlet close, from the accepted head, and records
that head's OID beside it in `$INPUT`. Nothing in this round fabricates one.

**The reviewed `$INPUT` manifest binding (new, required by G-4's cure).**
Candidate-mode tool authentication reads `s0-candidate-manifest.json` (S-0
runsheet §1.3 item 2) and expects one binding in it:

```json
{"custody_tools": {"scripts/verify_family_marker.py": "<64 hex sha256>", "...": "..."}}
```

The digest must be recorded there BEFORE the tool runs — that is what makes
candidate mode non-tautological. The S0-RUNSHEET-R2 work order (A82) owns
writing this key into the runsheet's manifest description.

## 7. The literal-sweep transaction-time obligation

Repointing `ROW_REGISTRY_RELATIVE_PATH` from `d117_row_registry_v1.json`
to `..._v2.json` leaves the old literal string in the tree. A sweep at
candidate commit finds **66 files** containing `d117_row_registry_v1`.
They fall into three classes, and only one class is a live obligation:

| Class | Count | Disposition |
| --- | --- | --- |
| Frozen campaign evidence (`configs/campaigns/**` freeze receipts and `plan_tree.json` for the `_v1`/`_v2`/`_v3` generations) | 18 | **Must not change.** These are historical evidence bytes; rewriting them would invalidate the receipts that reference them. |
| Historical process traces and run reports (`docs/process_traces/**`, `docs/run_reports/**`) | 37 | **Must not change.** Records of positions taken at a past evidence state; the supersession discipline forbids rewriting them. |
| **Live surfaces requiring transaction-time classification** | **11** | Each must be individually classified as (a) a correct historical/archival reference to be retained, or (b) a stale live pointer to be repointed. |

The eleven live surfaces:

```
docs/decision_log.md
docs/phase_2/alpha_arm_readiness.md
docs/phase_2/beta_arm_readiness.md
docs/phase_2/gamma_arm_readiness.md
docs/phase_2/window_runbook.md
tests/test_arm_readiness_evidence_t0.py
tests/test_arm_readiness_integration.py
tests/test_arm_readiness_lifecycle.py
tests/test_arm_readiness_registry.py
tests/test_arm_readiness_schemas.py
tests/test_d117_decode_contrast_plan.py
```

No file under `joulewise/` retains the v1 literal — the code constant flip
is complete.

At least one of these is a **correct retention**, not drift:
`tests/test_arm_readiness_schemas.py` deliberately pins the archival v1
file's SHA-256 to prove it stays byte-identical. The obligation is
CLASSIFICATION with a recorded disposition per file, not a bulk
find-and-replace. It is discharged at transaction time, before the S-0
line audit, and its output is a per-file disposition list.

## 8. CONFORMANCE

Verdicts are the audit seat's, taken against the diff at `bd7ebc1` with
file:line evidence. `PRESENT` = the mechanism is implemented and does what
the ruling requires. `PARTIAL` = implemented with a named hole.
`ABSENT` = not implemented.

### 8.1 Kernel row S1-CANDIDATE-01 acceptance evidence bullets

| # | Acceptance bullet | Verdict | Evidence |
| --- | --- | --- | --- |
| E1 | Every artifact the S-0 runsheet §1.3 requires exists **with sha256 sidecars and a binding manifest** | **PARTIAL** | Artifacts exist (§2). No `.sha256` sidecar file exists for any tool; no `s0-candidate.patch` exists. This manifest discharges the "binding manifest" clause only. |
| E2 | D-151 conditions 1, 2, 6, 8 each implemented **and named in the manifest** | **PARTIAL** | 1 PRESENT, 6 PRESENT, 8 PRESENT, **2 ABSENT** (§8.2). All four are named here. |
| E3 | Marker ruling baseline + all six splits implemented; regression set = the union of both seats' lists with a writer≠reviewer audit | **PARTIAL** | Baseline 5 of 6 PRESENT, 1 PARTIAL; splits 3 PRESENT, 1 PARTIAL, **1 ABSENT** (§8.4, §8.5). The regression union is substantially incomplete (§8.6). The writer≠reviewer audit is this document. |

Both fences hold:

- **Fence — no authenticator path in any allowlist:** HOLDS. The 112-entry
  allowlist contains zero paths matching `d117_step6_confirmation` or
  `family_publication`, asserted mechanically at
  `tests/test_arm_readiness_schemas.py:372-373` and re-verified
  independently by this audit.
- **Fence — the four r6-pinned estimator sources stay byte-identical:**
  HOLDS. Verified by SHA-256 against merge-base `5523003`:
  `joulewise/powermetrics_fiducial.py`
  (`386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`),
  `joulewise/uncertainty_evidence.py`
  (`257cda08be1b41ec9607e6c8e68a9b583cfeb71355700b4e6793075976112a5f`),
  `joulewise/adapters/powermetrics.py`
  (`70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4`),
  `joulewise/reduce.py`
  (`7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`).
  All four IDENTICAL.

### 8.2 D-151 conditions 1 / 2 / 6 / 8

| Condition | Verdict | Evidence |
| --- | --- | --- |
| **1a** chain contract amendment (governed pinset → closed, ordered, code-enumerated chain) | PRESENT | `docs/contracts/receipt_histsem_verifier.md` §"Governed identity and activation" now enumerates two members, adds "an unenumerated pinset-like file governs nothing" and the duplicate-refusal rule. |
| **1b** constant → tuple | PRESENT | `arm_readiness.py:2788-2791` — `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` is a 2-tuple (was a bare `Path`). |
| **1c** gate loops over members | PRESENT | `arm_readiness.py:3566` `for relative_path in RECEIPT_HISTSEM_PINSET_RELATIVE_PATH:` inside `_gate_receipt_histsem`. |
| **1d** `verify_all` union | PRESENT | `arm_readiness.py:3524-3535` — roots and per-pack verification both derive from the unioned `rows`. |
| **1e** existing refusal codes only | PRESENT | The chain code raises only `histsem_pinset_invalid`, `histsem_pinset_absent`, `histsem_history_unavailable`, all pre-existing (`:1079-1084`); that frozenset has no diff hunk. |
| **1f** CLI unchanged | PRESENT | `scripts/verify_receipt_histsem.py` diff is one docstring line; every flag byte-identical. |
| **1g** activation model unchanged | PRESENT | Engagement is still identity-only `(pack_id, pack_path)` membership, `:3607-3611`, same shape as baseline `:3499-3503`. |
| **2** digest-conditional successor subtraction | **ABSENT** | `arm_readiness.py:4146-4151`: `allowlist = set(governed["irrelevant_path_allowlist"]); relevant = sorted(set(changed_paths) - allowlist)` — an unconditional set subtraction. `validate_r1_evidence_lifecycle` takes no confirmation-table argument and neither production caller has one to pass. `validate_step6_confirmation_table` has exactly one caller (`:10183`, the marker verifier) and validates only the C→M edge; **no C→S edge exists anywhere** — nothing hashes the successor pinset's bytes against `table["successor_pinset"]["sha256"]`. See §8.6 G-2. |
| **6a** closed enumeration (un-enumerated file governs nothing) | PRESENT | Both readers iterate the code tuple only; no glob, scan, or config-driven member list. Regression: a rogue valid pinset dropped alongside is ignored (`tests/test_receipt_histsem.py:69-72`). |
| **6b** cross-member duplicate `(pack_id, pack_path)` → `histsem_pinset_invalid` | PRESENT | `arm_readiness.py:3122-3130` (library) and `:3594-3601` (gate). Note the rule is implemented **twice**, and only the library copy is tested — a drift hazard (§8.6 G-8). |
| **6c** absent enumerated member keeps `:36` absence semantics unchanged | PRESENT | Missing member → `continue` (`:3103-3108`, `:3577-3578`); only all-absent reaches the pre-existing behaviour. The gate returns ordinary readiness (`:3605-3606`), preserving the rule-11-settled `test_committed_pinset_deletion_gate_returns_normally`. No new `histsem_pinset_absent` path is introduced. |
| **8a** registry allowlist key authored (`freeze_evidence_lifecycle.irrelevant_path_allowlist`, absent at HEAD, would `KeyError`) | PRESENT | Key exists in `d117_row_registry_v2.json` with 112 unique sorted entries; the baseline v1 registry has **no** `freeze_evidence_lifecycle` object at all, so the `KeyError` the ruling predicted is cured. |
| **8b** allowlist = 112 with the successor path as the 112th entry | PRESENT | Independently counted: 112 total = 3 × 37 pack paths (111) + the successor pinset path (1). Unique, sorted. The old `_v1` pinset path is correctly ABSENT (replaced, not added to). |

### 8.3 The ruled v2 registry coordinate

| Item | Verdict | Evidence |
| --- | --- | --- |
| Outer id is `d117-row-registry-v2` | PRESENT | `registry_id: "d117-row-registry-v2"`, `schema_version: joulewise.arm_readiness_row_registry.v2`, 35 rows. Asserted at `tests/test_arm_readiness_schemas.py:362-364`. |
| `ROW_REGISTRY_RELATIVE_PATH` delta in the same tree | PRESENT | `arm_readiness.py:87` now `configs/arm_readiness/d117_row_registry_v2.json` (baseline `:80` was v1). |
| v1 file untouched vs baseline | PRESENT | SHA-256 identical to `5523003`; the path appears in no diff hunk. |

### 8.4 D-150 horizon values in the registry

Counted directly from the 29 `evidence_policies` entries:

| Ruled value | Required | Found | Verdict |
| --- | --- | --- | --- |
| 168h generic freeze-time kinds (`604_800_000_000_000` ns, `r1.execution_bound.freeze_generic_168h.v1`) | ten | **10** — ACCEPTANCE_OWNER, ACCEPTANCE_SUCCESSOR, ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION, REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION | PRESENT |
| 24h B-2 no-lane kinds (`r1.execution_bound.no_r1_lane_24h.v1`) | four | **4** — DRY_RUN_REHEARSAL, GIT_CHECKOUT, IDENTITY_PIN_PROJECTION, PRIVILEGE_INSTALLATION | PRESENT |
| 6h T-0 kinds (`r1.execution_bound.t0_procedural_6h.v1`) | two | **2** | PRESENT |

### 8.5 The marker ruling — ratified baseline and six splits

| Item | Verdict | Evidence |
| --- | --- | --- |
| **B1** two artifacts; marker immutable from build; binds only the confirmation CONTRACT (schema id + required YES), never the table's digest/path/time | PRESENT | Schema `arm_readiness.py:68`; canonical JSON + GNU sidecar written with `O_EXCL` (`:10023-10026`, `:4487`). `_FAMILY_MARKER_KEYS` (`:9465-9481`) is exactly 13 keys; the only confirmation-facing field is `publication_authority`, validated as exactly `{confirmation_schema, required_decision: "YES"}` (`:9691-9700`). **No table digest, path, or time anywhere in the marker** — the hash cycle is genuinely avoided. |
| **B2** unified two-section step-6 table; ONE contract home; no consumer restates it | PRESENT (one drift) | `STEP6_CONFIRMATION_TABLE_SCHEMA` (`:72`); validator `:9737` with both `family_publication` (`:9765`) and `successor_pinset` (`:9792`) sections. `receipt_histsem_verifier.md` defers explicitly rather than forking. **Drift:** the contract doc states `pack_count == 3` and `receipt_count == 33`, but `:9803-9805` accepts any non-negative int. |
| **B3** custody `candidate/` → `published/`; digest equality PLUS semantic replay of the three freeze-0004 receipts; publication + pre-arm both; T-0 full re-verify; execve hash-equality only | PARTIAL | Semantic replay is real and load-bearing (`:10125-10145`, via `_family_member`/`_freeze_evidence_for_arm`, requiring v2 schema, `receipt_id == "freeze-0004"`, `status == "PASS"`). **Hole:** the `candidate/` → `published/` custody LAYOUT does not exist — no such directories anywhere; the distinction is a derived label from the operator-supplied `--phase` flag (`:10231`), with no promotion step. `lane_inconsistent` is in the closed check-id set but is never raised. Nothing prevents `--phase publication` inside the S-0 clone with its forged `origin/main`, which would emit `gate_admissible: true`. Also: `phase="t0"` is never passed by the library (all three consults pass `"pre-arm"`), so T-0 receipts misreport the consult point; and no execve-boundary check exists in this diff. |
| **B4** `readiness_r1_family_publication` typed CUSTODY, registered, with a registry-load closure check; closed code-enumerated `check_id` frozenset | PRESENT | Code + type registered (`:202`, `:226`, `:240`) and in the registry vocabulary. **The closure check is real and reachable:** `:1881-1888` raises `readiness_row_registry_mismatch` ("not closed by code/type authority") for any registry code absent from `READINESS_REASON_CODES` or typed differently; chain `load_registry:2616 → validate_registry:1946 → :1967 → :1881`, firing before the role census. This genuinely cures the `_receipt_refusal` → `readiness_internal_error` explosion hole both blind seats shared. `FAMILY_PUBLICATION_CHECK_IDS` (`:532-567`) is a literal frozenset of 32 ids, enforced in the exception constructor (`:9458-9462`). **Caveat:** 7-8 of the 32 ids are never raised anywhere (§8.6 G-5). |
| **B5** engagement bound to tracked registry bytes, never marker presence; deleting the marker REFUSES; freeze-time engagement predecessor-only | PRESENT at the library; PARTIAL at the scheduler | `_gate_family_publication:10247-10272` consults the committed `successor_policy.successor_pack_ids` roster; a non-roster pack disengages, a roster pack with no marker RAISES `marker_absent`. Freeze-time gate is on the PREDECESSOR pack root (`:6385-6395`) — the bootstrap cure holds. **Deviation:** scheduler `_evaluate_g7` (`scheduler_gates.py:851-931`) performs **no roster consult**, so any non-`_v4` pack refuses G7 and can never reach GO. Fail-closed, so not a soundness hole, but it is not the ruled predicate. |
| **B6** scheduler receipt v2 + explicit G7 (exact-key block, GATE_IDS seven wide, G7 reason set, nulls-on-refusal) | PRESENT | `SCHEDULER_GATE_RECEIPT_SCHEMA` v2 (`:30`); `GATE_IDS` seven wide (`:38`); `FAMILY_PUBLICATION_KEYS` 8-key exact block (`:172-183`) validated at `:446-450`; `G7_REASON_CODES` six codes registered per-gate and typed CUSTODY (`:100-140`) with per-refusal enforcement `:377-393`; nulls-on-refusal enforced `:494-524`; `go_eligible` bound at `:550-552`. |
| **S-1** strict four-way head equality at all three live consult points | PRESENT | All three consults funnel through `verify_family_publication_marker:10106-10110`, which requires `live["clean"] is True`, `live["exact_match"] is True`, and full-dict `marker["publication_git"] == live`. `reviewed_main:4591-4613` computes exactness from `HEAD` == `refs/heads/main` == `refs/remotes/origin/main` plus a clean porcelain status. **No ancestry / `merge-base --is-ancestor` path exists in the family-marker code.** |
| **S-2** generation threshold as a tracked, reviewed REGISTRY value (not code prose) | **ABSENT** | `arm_readiness.py:531` `FAMILY_PUBLICATION_FIRST_GENERATION = 4` is a bare code literal, used at `:6388`, `:9545`, `:9987`. `grep -c generation d117_row_registry_v2.json` = **0**; `_R1_SUCCESSOR_POLICY_KEYS` (`:587-592`) has no generation field. The one regression asserts only that the identifier STRING appears in the source. This is the ruled repair for Sol's false-predicate finding, and it is not implemented as ruled. See §8.6 G-3. |
| **S-3** library-boundary publication gate (a direct arm invocation refuses an unpublished family without the scheduler) | PRESENT | `generate_arm_receipt:7145-7160` calls `_gate_family_publication` directly with no scheduler involvement; the refusal flows to `refusals` (`:7224`) → `status = "REFUSE"` (`:7244`) → `arm_disposition = "NO_GO"` (`:7275`). Mirrored on the verification path `:7362-7376`. |
| **S-4** terminal-review binds `head_tree_oid` | PRESENT (self-consistency only) | `:9681-9690` exact-keys `terminal_review` to `{evidence_kind: "TERMINAL_REVIEW", head_tree_oid}`, requires a 40-hex OID equal to `publication_git["head_tree_oid"]`, else `terminal_review_mismatch`. **Caveat:** the check is intra-document; the marker's field is never compared against the LIVE tree of `publication_head`, nor tied to an actual TERMINAL_REVIEW evidence receipt (the marker replay path uses `_authenticate_generic_evidence_item` and never reaches `validate_terminal_review_head_tree`). The composite arm-time gate does cover the evidence receipt; the marker alone does not. |
| **S-5** candidate-mode tool hash (production = committed-blob equality; S-0 candidate mode verifies against the reviewed `$INPUT` manifest sidecars) | **PARTIAL — bypassable** | `_family_tool_reference:9821-9843`. Two defects, both verified at source by this audit: (i) **mode is selected by filesystem presence, not by lane** — `if sidecar_path.exists():` routes to candidate mode, so dropping a `<tool>.sha256` beside a production tool skips committed-blob equality entirely; (ii) **the candidate branch is tautological** — `digest` is computed from the tool's own current bytes at `:9828` and then compared against `gnu_sidecar(digest, name)`, i.e. "does this sidecar match this file". A modified tool passes by regenerating its own sidecar. The reviewed `$INPUT` manifest is never opened and no `$INPUT` path is threaded into the function. Additionally, `_gate_family_publication` never passes `consumer_tool`, so executing-tool equality is skipped at every library and scheduler consult — it runs only on the CLI verifier. See §8.6 G-4. |
| **S-6** `publication_state` | NOT RULED (noted) | Implemented as a single-valued constant `"PUBLISHED"` (`:9988`), validated as exact at `:9547`. No `CANDIDATE` value; lane distinction is carried entirely by the verifier's `phase`/`lane`. Within the implementer's discretion. |

### 8.6 GAPS — what a finish round must close

Ordered by severity. G-1 through G-4 block acceptance of the kernel row.

**G-1 — Named deliverables absent.** No `s0-candidate.patch` exists in
either tree, and no `.sha256` sidecar file exists for any of the four
custody tools. The kernel row requires "s0-candidate.patch + manifest +
custody tools with sha256 sidecars". Digests are recorded in §6; the
files are not minted. Mint sidecars into custody staging only, never
beside the in-tree scripts (§6 caution).

**G-2 — D-151 condition 2 is not implemented (mechanism gap).** The
successor pinset path is subtracted from the R1 changed set by
unconditional allowlist membership (`arm_readiness.py:4146-4151`). This is
exactly the "permanent hole" shape the condition was written to forbid:
whatever bytes sit at that path — the Ed-confirmed pinset, a later
mutation, an attacker's rewrite — are forgiven, forever, for every future
arm. The contracts assert the opposite is built
(`receipt_histsem_verifier.md`: "The successor class is digest-conditional
on Ed's single step-6 confirmation table";
`d117_step6_confirmation_table.md:114`: "The changed-set/histsem consumer
validates the entire table and the C → S edge"), so the documentation is
currently **false**. Two aggravating details:
(a) `scripts/build_v4_histsem_pinset.py:232` writes
`"published_anchor": "D-151:joulewise.d117_step6_confirmation_table.v1#successor_pinset"`
as a hard-coded STRING — it makes the artifact NAME the anchor while
binding nothing to it, so the emitted JSON reads as if the edge exists;
(b) `tests/test_arm_readiness_schemas.py:370` **codifies the gap as the
spec** (`assertIn(successor, allowlist)`), so the test suite would fail if
someone implemented the digest condition. The fix must thread the
confirmation table into `validate_r1_evidence_lifecycle`, subtract the
successor path only when its current bytes hash to
`table["successor_pinset"]["sha256"]`, and amend that assertion.

**G-3 — Split S-2 not implemented as ruled.** Move
`FAMILY_PUBLICATION_FIRST_GENERATION` out of code into a reviewed registry
field under `freeze_evidence_lifecycle.successor_policy`, add it to
`_R1_SUCCESSOR_POLICY_KEYS`, and replace the source-grep regression with a
behavioural one. Related residual: `_gate_family_publication:10262` still
uses the literal predecessor-in-CURRENT-roster predicate, which is the
adjacent-generation falsity S-2 was raised to cure — it holds only while
`_v4` is the roster.

**G-4 — Split S-5 production rule is bypassable.** Select tool-hash mode
by `phase`, not by sidecar file presence; and make the candidate branch
compare against the digest recorded in the reviewed `$INPUT` manifest
rather than recomputing from the tool's own bytes. Add a regression that
runs a MODIFIED tool against both modes.

**G-5 — Dead entries in the closed diagnostic set.** Eight of the 32
`FAMILY_PUBLICATION_CHECK_IDS` are never raised anywhere in `joulewise/`
or `scripts/`: `marker_self_digest_mismatch`, `lane_inconsistent`,
`registry_dormant`, `head_unpublished`, `history_shallow`,
`git_unavailable`, `internal_error`, and `family_incoherent` (raised only
in `scheduler_gates`, never in the library).
`scheduler_gates.py:843` maps `head_unpublished` → the consequently
unreachable `scheduler_family_unpublished`. Because
`test_diagnostic_check_ids_are_exact_closed_enumeration` pins the set as
exact, it LOCKS IN the dead entries. Each needs either an implementation
with a falsifier or a ruled retirement.

**G-6 — Candidate-lane laundering is undefended.** No consumer inspects a
verification receipt's `lane` / `gate_admissible` fields;
`lane_inadmissible` guards only an unknown `phase` ARGUMENT. A
candidate-lane receipt produced in the S-0 clone (forged `origin/main`)
is not mechanically distinguishable at G7 or at the arm gate. This is the
D-151 condition 4 extension the marker ruling ¶2 names.

**G-7 — The verifier's semantic-replay path is behaviourally untested.**
The ~180 lines of `verify_family_publication_marker`
(`arm_readiness.py:10071-10245`) are never executed against a real
fixture repository. One live fixture would unlock roughly fifteen
currently-uncovered tamper cases at once. This is the single
highest-leverage test item.

**G-8 — The regression union the ruling ordered is substantially
incomplete.** Against Sol's item-9 list (10 regressions) and Opus's
T1–T27 tamper cases plus 11 mechanism tests, honest coverage is:

| Seat list | Covered | Partial | Not covered |
| --- | --- | --- | --- |
| Sol item-9 regressions (10) | 2 | 4 | 4 |
| Opus T1–T27 tampers | 4 | 5 | 17 (+1 N/A) |
| Opus mechanism tests (11) | 3 | 3 | 5 |

Named must-adds, highest first:

1. **Bootstrap (Sol S7 = Opus T-B1/T-B2), NOT COVERED.** Mint
   `freeze-0004` for a registry-installed `_v4` pack with no marker →
   must PASS; a `_v5`-shaped predecessor freeze over an unpublished
   `_v4` → must REFUSE. The current test is a source grep containing a
   whitespace-literal negative assertion that any reformat defeats. Opus
   calls a bootstrap deadlock the highest carried risk: if this is wrong,
   the family can never be created.
2. **Arm-receipt half of marker deletion (Sol S5 = Opus T24), PARTIAL.**
   The refuse-don't-disengage half is covered with the exact
   `marker_absent` check_id; the half that proves an arm receipt carries
   `readiness_r1_family_publication` is missing. Opus names this "the
   single most important test in the suite" — it is also the only
   behavioural proof of split S-3.
3. **Rollback falsifier (Sol S3 = Opus T18), NOT COVERED.** The refuter
   that DECIDED split S-1 has no regression: nothing verifies a marker
   whose `publication_head` is a mere ancestor of `origin/main`.
4. **G7 digest substitution (Sol S10), NOT COVERED.**
   `test_g7_pass_binds_marker_table_and_verification_receipt` asserts only
   `^[0-9a-f]{64}$` shape, against a marker file whose contents are
   literally `b"marker"` with the verifier patched out. Assert digest
   EQUALITY against the real bytes in at least one unpatched path.
5. **`_g7_scheduler_code` mapping:** six branches, zero tested; the
   existing assertion is the generic `assertIn(code, G7_REASON_CODES)`.
6. **Gate-side duplicate-identity branch** (`:3595-3601`) untested — only
   the library copy at `:3122-3130` is exercised.
7. **Builder determinism (T-D1) and custody-externality (T-O1):** the
   builder is never EXECUTED in any test; `--help` plus source greps only.
   Add two builds into distinct empty custody dirs → byte-identical; an
   in-tree `--output` → `output_in_tree`; and `git status --porcelain`
   empty after a build (the mechanical proof the 112 contract is
   untouched). Note an inconsistency to reconcile: the verifier's in-repo
   guard raises `marker_unreadable`, not `output_in_tree`.
8. **Fault injection for the two `EvidenceLifecycleError` catches.** Both
   catches EXIST and are symmetric (`:7161-7167`, `:7377-7383`), but the
   regression `test_r4_evidence_lifecycle_escape_sites_are_caught` is an
   `inspect.getsource` substring search — it would pass against an
   unreachable handler, or one that swallows the error without emitting
   the governed refusal.

**G-9 — Test-quality defects in what WAS written** (these are why 87 green
overstates coverage):

- **Six of the twenty new tests are source greps, not behaviour** —
  including the tests standing in for splits S-2 and S-3. A
  `getsource` + `assertIn` pins a string; it cannot fail when the
  mechanism does.
- **Generic-assertion violations of the bar Opus set** ("each tamper must
  produce its SPECIFIC sub-code — a test that only asserts 'some refusal'
  would pass against a gate that refuses for the wrong reason"):
  `test_confirmation_missing_unknown_and_wrong_successor_refuse` asserts
  `assertIn(check_id, FAMILY_PUBLICATION_CHECK_IDS)`, which passes for any
  registered code.
- **Fixture digest collision:** `tests/test_family_marker.py` uses
  `SHA = "0"*64` for EVERY digest field in both the marker and the
  confirmation fixtures, so any cross-field comparison bug (comparing
  `pack_sha256` where `freeze_receipt.sha256` was meant) is invisible to
  the whole schema test class. Give each field a distinct digest.
- **Misleading PASS record:** the verifier's `checks[]` array
  (`:10208-10226`) is a hardcoded literal list, not a record of checks
  actually executed — it reports `predecessor_mismatch: PASS` for a check
  that never runs.

**G-10 — Nits.** Contract/code drift on `pack_count`/`receipt_count`
(§8.5 B2); unused `exc` binding at `:7151`; stale "All six gate
evaluations" comment at `scheduler_gates.py:1038`; missing blank lines
before `evaluate_scheduler_gates` (`:971`).

### 8.7 What this audit did NOT establish

- No claim is made about behaviour against the REAL successor pinset
  bytes; that artifact does not exist yet (§3).
- The 87-test green is a LOCAL run; the D-151 condition 4 two-part green
  (published) is untouched by this candidate and remains an S-0
  obligation.
- The `execve` hash-equality leg of marker-ruling ¶3 is not implemented in
  this diff and was not traced to another owner; it needs a disposition.

---

## 9. FINISH ROUND (2026-08-22, head `b1c6bee`)

§8 above is preserved unedited as the record of the position taken at
`bd7ebc1`. This section states what changed and re-states each verdict at the
finish-round head. A verdict flips only where the mechanism genuinely changed;
where it did not, it says so.

### 9.1 Per-gap disposition

| Gap | Was | Now | What actually changed |
| --- | --- | --- | --- |
| **G-1** named deliverables | PARTIAL | **CURED (patch deferred by design)** | Four `.sha256` sidecars minted beside their tools, GNU form, `shasum -c` clean, with a regression that fails on staleness. `s0-candidate.patch` is exported by the lead at gauntlet close from the accepted head (§6) — deliberately not fabricated here. |
| **G-2** D-151 condition 2 | **ABSENT** | **PRESENT** | `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` names the conditional class; `_require_confirmed_conditional_path` enforces the C→S edge (table present, canonical, sidecar-consistent, schema-valid, naming this path, and the bytes **committed at the reviewed HEAD** hashing to Ed's confirmed digest); every other outcome refuses `DEPENDENCY_CHANGED_SET`. The confirmation path is threaded from the arm, freeze, verification, and marker-replay entry points; absent, it fails closed. The contracts' claims are now true. |
| **G-3** split S-2 | **ABSENT** | **PRESENT** | `FAMILY_PUBLICATION_FIRST_GENERATION` is deleted. The threshold is a reviewed registry value at `freeze_evidence_lifecycle.successor_policy.family_publication_first_generation` (= 4), read by `_family_first_generation`. `successor_policy` validation is a required core plus one named optional key, so pre-`_v4` lifecycle registries still validate and a registry without the value refuses (`registry_dormant`) rather than defaulting. |
| **G-4** split S-5 | **PARTIAL — bypassable** | **PRESENT** | Lane selection by explicit `phase`, never by file presence. Candidate mode opens the reviewed `$INPUT` manifest and compares against the digest recorded there before the tool ran; the tautology is gone. Both CLIs gain `--phase` (default: the strict production rule) and `--candidate-manifest`. |
| **G-5** dead check_ids | 8 named dead | **CURED, and the list was wrong** | Set 32 → 29. Real raise sites for `registry_dormant`, `lane_inconsistent`, `marker_self_digest_mismatch`, `head_unpublished`, and `predecessor_mismatch` — a **ninth** dead id the audit's list missed, found by a new mechanical test that asserts every member has a raise site. Retired with grounds, citing this round in code and in the exactness test: `history_shallow`, `git_unavailable`, `internal_error`. |
| **G-6** candidate-lane laundering | undefended | **PRESENT** | `require_gate_admissible_verification()` checks a verification receipt's `lane` / `gate_admissible` / `publication_authorized` against its own `phase`: incoherent → `lane_inconsistent`; coherent but candidate or non-PASS → `lane_inadmissible`. Called by **both** consumers — the library arm gate and scheduler G7. |
| **G-7** replay untested | untested | **PARTIAL — real fixture, unbuilt packs** | `FamilyMarkerLiveFixtureTests` runs the verifier against an actual Git repository (tracked v2 registry, four-way-exact refs, real marker + sidecar in external custody) and walks a tamper ladder to each specific diagnostic. It found two live defects: member-pack read failures escaped as bare `ArmReadinessError` and the CLI mislabelled them `registry_mismatch`; now `roster_mismatch` / `plan_binding_mismatch`. **Still uncovered:** the member-replay PASS direction, which needs the three `_v4` packs (unbuilt until S-0). |
| **G-8** regression union | substantially incomplete | **PARTIAL** | Closed: the rollback falsifier that decided split S-1 (item 3) — the fixture reproduces the ancestry trap and asserts equality refuses it; G7 digest **equality** against real bytes (item 4); all six `_g7_scheduler_code` branches plus total coverage of the closed set (item 5); builder determinism/custody-externality **executed**, with `git status` proven unchanged after a build (item 7); freeze-time predecessor-only engagement (item 1, bootstrap half). **Open:** the arm-receipt half of marker deletion (item 2), the gate-side duplicate-identity branch (item 6), and fault injection for the two `EvidenceLifecycleError` catches (item 8). See §9.2. |
| **G-9** test quality | 6 greps, collisions | **PRESENT** | Fixture digests are distinct per field (were all `"0"*64`, blinding the whole schema class to cross-field comparison bugs). Generic `assertIn(check_id, CHECK_IDS)` assertions replaced by exact per-tamper diagnostics, plus two new tamper cases. The verification receipt's `checks[]` array now records the checks actually executed, in code order, instead of a literal that reported `predecessor_mismatch: PASS` for a check that never ran. Four source greps replaced by behavioural tests. |
| **G-10** nits | open | **CURED** | Contract/code drift closed by making the code match the contract (`pack_count == 3`, `receipt_count == 33` are now enforced, were "any non-negative int"); unused `exc` binding removed; the "All six gate evaluations" comment says seven; blank lines restored before `evaluate_scheduler_gates`. |

Consequential verdict flips in §8, and only these:

- §8.1 **E2** PARTIAL → **PRESENT**: D-151 conditions 1, 2, 6, 8 are now all
  implemented and named here.
- §8.2 condition **2** ABSENT → **PRESENT** (G-2).
- §8.5 **S-2** ABSENT → **PRESENT** (G-3); **S-5** PARTIAL → **PRESENT** (G-4);
  **B2**'s recorded drift is closed (G-10).
- §8.1 **E1** and **E3** stay **PARTIAL**: E1 because the patch is exported at
  gauntlet close, E3 because the regression union is still incomplete (§9.2)
  and the writer≠reviewer audit of the finish round has not been performed —
  this section is the implementer's own record, and it needs an independent
  seat before acceptance.
- §8.5 **B3**, **B5**, **S-4** stay **PARTIAL/caveated**: the `candidate/` →
  `published/` custody LAYOUT still does not exist, `phase="t0"` is still never
  passed by the library, the execve-boundary check is still absent, scheduler
  `_evaluate_g7` still performs no roster consult (fail-closed, but not the
  ruled predicate), and the marker's `head_tree_oid` is still only
  self-consistent. None of these was in this round's work order.

### 9.2 What the finish round did NOT cure, with grounds

1. **The arm-receipt half of marker deletion (G-8 item 2)** — Opus called it
   "the single most important test in the suite" and it is the only
   behavioural proof of split S-3. A real arm receipt carrying
   `readiness_r1_family_publication` needs a complete pack fixture with a
   passing freeze receipt; the three `_v4` packs do not exist until S-0 mints
   them, and the existing integration fixtures that could stand in are red for
   an unrelated reason (§9.3). What IS proven behaviourally: the gate engages
   from the tracked roster and refuses `marker_absent` when a roster pack has
   no marker, and the refusal record is the registry's own typed CUSTODY
   entry. The end-to-end receipt remains an S-0 observation.
2. **Gate-side duplicate-identity branch (G-8 item 6)** and **fault injection
   for the two `EvidenceLifecycleError` catches (G-8 item 8)** — both need the
   same pack fixture. The `getsource` regression for item 8 remains, and it
   remains as weak as the audit said it was.
3. **G-7's member-replay PASS direction** — see the table; the first
   observation belongs to S-0 and must be transcribed there.
4. **§8.5's B3/B5/S-4 caveats and §8.7's execve leg** — out of this round's
   scope, restated above so they are not lost.

### 9.3 G-11 (NEW, BLOCKER) — the candidate is red on 149 tests

**This was not among the ten gaps and is larger than any of them.**

The audit's "87 green" was green for the four modules it ran. Running the
whole arm-readiness blast radius (28 modules, 549 tests) at the audited commit
`bd7ebc1` gives **36 failures + 113 errors = 149 failing tests**. Measured, not
inferred; the same 549 tests at the finish-round head give 140 failing, and a
name-by-name comparison shows **zero failures introduced by this round** — it
removed nine.

Two distinct causes, both consequences of ruled changes:

1. **The registry repoint (dominant, ~140 tests).** `ROW_REGISTRY_RELATIVE_PATH`
   moved `v1 → v2` as ruled, but six test modules install
   `configs/arm_readiness/d117_row_registry_v1.json` into their temporary
   repositories by hardcoded name. Those fixtures now build repositories the
   code cannot read: `load_registry` raises `FileNotFoundError` on the v2 path.
   This is manifest §7's "literal-sweep transaction-time obligation" — but §7
   sized it as an 11-file *classification* exercise, and it is in fact a
   *fixture-installation* debt that red-lines the suite. Affected:
   `tests/test_arm_readiness_lifecycle.py`, `tests/test_arm_readiness_integration.py`,
   `tests/test_arm_readiness_evidence_t0.py`, `tests/test_arm_readiness_registry.py`,
   `tests/test_d117_decode_contrast_plan.py`, and `tests/test_arm_readiness_dry_run.py`
   (via a shared helper).
2. **Two one-line assertions** in `tests/test_arm_readiness_evidence.py`:
   `test_r1_lifecycle_is_dormant_for_historical_v1_registry_and_profile`
   asserts `ROW_REGISTRY_SCHEMA` where the repoint now yields
   `R1_ROW_REGISTRY_SCHEMA`, and `resolved_r1_row_registry()` builds a
   synthetic registry whose `test_r1_*` refusal codes the ruled registry-load
   closure check now rejects (it should use the production vocabulary).

**Why it is not cured here:** every one of those files is outside the finish
round's 17-path write lease, and `WRITE_SCOPE` is exhaustive — additional
scope is never inferred from tests. The remedy is mechanical and the diagnosis
above is precise enough to execute directly; it needs a lease extension
covering those six test modules, and it must land before S-0, whose runsheet
runs the suite.

A related in-scope defect WAS cured: the same closure check was firing inside
`validate_r1_lifecycle_registry` for **every** caller-supplied lifecycle
registry, not just the tracked one. It now fires on the registry-LOAD path the
marker ruling names (`validate_registry`), which is the only path where an
unregistered code can explode into `readiness_internal_error`. That alone
fixed nine of the 149.

### 9.4 Frozen surfaces, re-verified at `b1c6bee`

SHA-256 against merge-base `5523003`; all five **IDENTICAL**:

```
386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py
257cda08be1b41ec9607e6c8e68a9b583cfeb71355700b4e6793075976112a5f  joulewise/uncertainty_evidence.py
70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4  joulewise/adapters/powermetrics.py
7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  joulewise/reduce.py
d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5  configs/arm_readiness/d117_row_registry_v1.json
```

The no-authenticator-in-any-allowlist fence also still HOLDS: the 112-entry
allowlist contains zero paths matching `d117_step6_confirmation` or
`family_publication`, and the successor pinset path — the one entry that is
allowlisted — is now digest-conditional rather than unconditionally forgiven.

### 9.5 Finish-round commits

```
23e185d  G-2: implement D-151 condition 2 — digest-conditional successor subtraction
dd17cd8  G-4 + G-3: phase-selected tool hash, and S-2's threshold into the registry
40bb7a3  G-5 + G-6 + G-7 + G-9: dead diagnostics, lane laundering, live fixture, test quality
096a94e  G-1 + G-8: mint the four tool sidecars; S-3 refusal-record proof
b1c6bee  G-10: seven-gate comment, blank lines before evaluate_scheduler_gates
```

Four-module test record at `b1c6bee`: **99 tests, OK** (was 87 at `bd7ebc1`
— a net +12 test methods). Four tests that were `inspect.getsource` +
`assertIn` string greps were rewritten as behavioural tests and renamed to say
what they now prove; no test was deleted, and no assertion was weakened. The
two-part-green caution of §5 is unchanged and still governs:
this is a LOCAL run and must never be reported as D-151 condition 4's
published green.

---

*§1–§8 audited and authored by the S-1 conformance seat (writer ≠
implementer), 2026-08-22, against `bd7ebc1`. Every mechanical count, digest,
and the three top-severity findings (G-2, G-3, G-4) were re-verified at source
by the audit seat rather than accepted from a delegated report.*

*§9 authored by the finish-round implementer seat, 2026-08-22, against
`b1c6bee`. It is a self-report and is marked as one: E3's writer≠reviewer
audit has NOT been performed for this round, and acceptance requires an
independent seat over §9's claims.*
