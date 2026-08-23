# S-1 CANDIDATE MANIFEST — the `_v4` reviewed candidate custody (2026-08-22)

**Status: COMBINED FIX ROUND COMPLETE; REVIEWED TWICE AND REFUTED BOTH TIMES;
FIXES APPLIED AND MEASURED; NOT YET DELTA-RE-AUDITED, NOT ACCEPTED.** This
manifest is the binding record of what the S-1 implementation contains and what
it does not. §8's verdicts were authored by the conformance-audit seat against
`bd7ebc1`; §9 records the finish round that closed them; **§10 records the
combined fix round of 2026-08-23**, which answered two independent reviews of
`c1b87f6` — an independent writer≠reviewer seat verdict (REFUTED: 3 blockers,
12 should-fix, 4 nits) and a fresh read-only G-2 security refuter (REFUTED:
1 blocker, 3 should-fix, 1 nit). A §8 verdict flips only where the mechanism
genuinely changed.

**G-11 (red outside the four reviewed modules) is CURED and re-measured, and
all four blockers across the two reviews are cured.** What remains open is
stated as open and counted in §10.1: of the 21 review findings, 15 are cured,
4 are partial, 1 is NOT addressed, and 1 was never a branch regression. The
round also INTRODUCED defects of its own, in two groups: **four** that it
found by running the code and CURED within the round (§10.4, including one
24-failure regression that only the repository-radius run could see), and
**three** plus two prose defects that a source-level audit found and that
remain OPEN (§10.1). All are recorded here rather than left for the next
reviewer to find. Two structural partials (§10.3) await artifacts only S-0 can
produce. **A delta re-audit of this round has NOT been performed.**
This candidate still cannot be handed to S-0 on this document's authority
alone.

Kernel row: `S1-CANDIDATE-01` (TASK_QUEUE.md rank A81; acceptance at
`docs/process/state_kernel.json` `/tasks/S1-CANDIDATE-01/acceptance`).

## 1. Coordinate

| Item | Value |
| --- | --- |
| Worktree | `/Users/edr/code/JouleWise-wt-s1` |
| Branch | `impl/s1-candidate` |
| Audited commit (§8 verdicts) | `bd7ebc13f6f631f73a64b54b5b13ae29a4d491dc` |
| Finish-round head (§9 verdicts) | `b1c6beedc363d7bf57b3035068a11190ccb55a4e`. **The claim previously made here — that this was "the last COMMIT BEARING CODE" — was FALSE (nit 16)**, and it mattered: it is why §9.4's frozen-surface check had never been run at a head that actually bore code. `c1b87f6` changed `joulewise/arm_readiness.py` and `joulewise/arm_readiness_evidence.py`, and the 2026-08-23 fix round changed code again. |
| Reviewed head (§10 verdicts) | `c1b87f63fd47507dd1504693ad45347a4f2c55aa` — the head both independent reviews audited |
| Fix-round head (§10) | `8d51f76fa532607da45e45789e343fcf31fc8bce` — the last commit bearing code. The commit adding §10 is documentation-only and changes no digest recorded here; §10.5's frozen-surface re-verification was run at this commit. |
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

SHA-256, GNU coreutils form (`<64 hex><two spaces><basename>`), **recomputed at
the fix-round head on 2026-08-23** and superseding the values this section
carried at `b1c6bee`. Those earlier values had gone stale for three artifacts
that later rounds edited — a hand-transcribed digest block does not update
itself, which is precisely the drift the `.sha256` sidecar regression exists to
catch for the tools. Digests marked **(changed)** moved after `b1c6bee`:

```
e51617f9cdbbcac2e8e5558c5422c701e3091476c267d11427189bfc3a82f50b  build_family_marker.py
68be9c6e76eaa17fec49d1b72597189f89c5f80587fa2b5a1e270e1b48e49b19  verify_family_marker.py   (changed)
29335e6fcfe8e97a78212f44e44a96e869d3179afb3411cda74f2a8070b978fa  build_v4_histsem_pinset.py
394ed1992c26cff150c8a9bfe026ba787e99a37428e3ee4010fe381a29b0d860  verify_receipt_histsem.py
```

`verify_family_marker.py` changed because the fix round gave it the
`--expected-confirmation-digest` flag; its tracked `.sha256` sidecar was
regenerated in the same commit and verifies.

Governance artifacts, same form and head:

```
7a1642130eedaa528059c59304fa32813cc884b5f0b9c338634946ef105297b7  d117_row_registry_v2.json
246e48f411172ef7b3b5c4754c288002b2e51bddf7d55d9f51393ee77896e6d3  d117_step6_confirmation_table.md   (changed)
a1773f7c3696d11267a644c9310c052b02c2499c5498ce92036977501c48417c  receipt_histsem_verifier.md        (changed)
```

Both contracts changed because the fix round amended them; the registry is
unchanged since `b1c6bee`.

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
(`git diff --binary 5523003..<accepted head>`), and exporting it before
gauntlet close would pin a digest that every subsequent fix invalidates —
demonstrated twice over since this paragraph was written, as the head moved
from `b1c6bee` to `c1b87f6` and then through the 2026-08-23 fix round. The
head in that command is deliberately left unbound here for the same reason. The lead exports it —
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
| **G-2** D-151 condition 2 | **ABSENT** | **PRESENT** | `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` names the conditional class; `_require_confirmed_conditional_path` enforces the C→S edge (table present, canonical, sidecar-consistent, schema-valid, naming this path, and the bytes **committed at the reviewed HEAD** hashing to Ed's confirmed digest); every other outcome refuses `DEPENDENCY_CHANGED_SET`. **Corrected 2026-08-23 (§10, seat should-fix 6 + refuter G2-1):** the confirmation path is threaded from the arm, freeze, verification, marker-replay, scheduler-G7, launcher-CLI and evidence-authoring (`_authenticate_existing_r1`) entry points, and Ed's out-of-band digest `hC` is threaded beside it as `expected_confirmation_digest` and never derived by any consumer. The threading is NOT uniform and the asymmetry is recorded rather than claimed away: arm, verification and the scheduler default a missing path to campaign custody (`<window_custody_root>/family_publication/<STEP6_CONFIRMATION_TABLE_NAME>`), while `generate_freeze_receipt` passes the argument through without a default. All branches fail closed, so there is no bypass; the freeze asymmetry is harmless in the intended order (the pinset does not exist at freeze time) and remains an ordering fragility, NOT a cure. The contracts' claims are true as qualified here. |
| **G-3** split S-2 | **ABSENT** | **PRESENT** | `FAMILY_PUBLICATION_FIRST_GENERATION` is deleted. The threshold is a reviewed registry value at `freeze_evidence_lifecycle.successor_policy.family_publication_first_generation` (= 4), read by `_family_first_generation`. **Corrected 2026-08-23 (§10, refuter G2-4):** the threshold was optional, and a registry that simply omitted it validated, whereupon freeze set `None` and SKIPPED publication — a dormant fail-OPEN edge. The key is now MANDATORY: `successor_policy` is validated by exact-key match over all five keys, so an omitted threshold is refused at registry load (`readiness_schema_invalid`) instead of disengaging the gate. Pre-`_v4` fixtures therefore DECLARE the family threshold and fall BELOW it — the threshold is family policy, not a per-pack knob — rather than deleting the key. |
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

### 9.3 G-11 (CURED) — the candidate was red on 149 tests

**This was not among the ten gaps and was larger than any of them.**

The audit's "87 green" was green for the four modules it ran. Running the
whole arm-readiness blast radius (28 modules, 549 tests) at the audited commit
`bd7ebc1` gave **36 failures + 113 errors = 149 failing tests**. Measured, not
inferred; the same 549 tests at the finish-round head gave 140 failing, and a
name-by-name comparison showed **zero failures introduced by that round** — it
removed nine.

G-11 is now **CURED** under a lease extension and three magistrate rulings
(recorded below).

**A denominator caveat first, because it bears on every count here.** The
28-module blast radius re-derived for this round (modules under `tests/`
matching `arm_readiness`, `d117_row_registry` or `family_marker`) runs **1368**
tests, not the 549 this section originally cited. Both sets are 28 modules, so
the two figures are NOT interchangeable and the original 149 is **not**
like-for-like with anything below. The honest comparison is therefore the
per-module before/after table, measured by this seat on both sides:

The "after (fix round)" column is measured at the fix-round head by the
close-out seat on 2026-08-23, one module per `python3 -m unittest` invocation
with `PYTHONDONTWRITEBYTECODE=1`. "skipped" replaces the earlier "expected"
because `@unittest.expectedFailure` has been eliminated entirely (§10.2).

| module | before | after (finish round) | after (fix round, measured 2026-08-23) |
|---|---|---|---|
| `test_arm_readiness_lifecycle` | 46 tests, 14F+26E = 40 | 47 tests, **OK**, 4 expected | 47 tests, **OK**, 4 skipped |
| `test_arm_readiness_evidence_t0` | 25 tests, 49E | 25 tests, **OK**, 7 expected | 25 tests, **OK**, 7 skipped |
| `test_arm_readiness_integration` | 9 tests, 1F+9E = 10 | 9 tests, **OK**, 5 expected | 9 tests, **OK**, 5 skipped |
| `test_d117_decode_contrast_plan` | 22 tests, 13F | 22 tests, **OK**, 1 expected | 22 tests, **OK**, 1 skipped |
| `test_arm_readiness_dry_run` | 5 tests, 4E | 5 tests, **OK**, 4 expected | 5 tests, **OK**, 4 skipped |
| `test_arm_readiness_registry` | 5 tests, 3F | 5 tests, **OK** | 5 tests, **OK** |
| `test_arm_readiness_evidence` | 11 tests, 1F+1E = 2 | 11 tests, **OK** | 12 tests, **OK** |
| `test_arm_readiness_evidence_author` | 24 tests, 2F+12E = 14 | 24 tests, 2F+2E = 4 | 24 tests, **OK** |

**135 failing → 0 across the eight modules that carried the defect.** The four
that remained red at the finish-round head were §9.3.6's "open finding"; that
finding was a MISDIAGNOSIS and is retracted in full below (§9.3.6 as rewritten),
and the four tests are now ordinary green. One test was added in the finish
round (lifecycle 46 → 47) and one in the fix round (evidence 11 → 12).

The four candidate modules and the two enumeration/launcher modules, measured
in the same way at the same head: `test_receipt_histsem` 21 tests **OK**;
`test_arm_readiness_schemas` 23 tests **OK**; `test_family_marker` 21 tests
**OK**; `test_scheduler_gates` 40 tests **OK**; `test_launch_window` 16 tests
**OK**; `test_s0_blocked_enumeration` 1 test **OK**. Total across all fourteen
modules: **275 tests, zero failures, zero errors, 21 skips** — and those 21
skips are exactly the enumerated partition of §10.2, asserted mechanically.

**The former whole-radius figure is STRUCK.** This section previously recorded
`Ran 1368 tests ... FAILED (failures=2, errors=2, expected failures=21)` and
called the 21 an S-0 acceptance criterion that "must flip green in the clone
proof." Both statements are withdrawn:

- The 1368-test figure was a `unittest` run over a narrower radius (28 modules,
  13 min) and does **not** characterise the repository (~3,880 tests plus
  ~19,700 subtests). It is not like-for-like with any other count in this
  manifest and must not be compared to one. The repository-radius measurement
  is §9.3.7 below.
- The 21-must-flip addendum encoded the **disproven** S0-BLOCKED theory. The
  measured `S0-BLOCKED` set is **empty** (§10.2), so the addendum gated
  nothing. It is STRUCK from S-0's acceptance by magistrate ruling R1 of
  2026-08-23; S-0's acceptance reverts to its primary, always-authoritative
  form — the runsheet r2 §5 proving-obligations checklist, which never depended
  on fixtures.

Two cautions carry forward unchanged. This is a LOCAL run and must never be
reported as D-151 condition 4's published green; and §9 remains a self-report
from the implementing seat. E3's writer≠reviewer audit HAS now been performed
for the finish round (the independent seat verdict of 2026-08-23, answered in
§10) — but NOT for the fix round itself, which is what the pending delta
re-audit must cover.

#### 9.3.1 What was actually wrong — three causes, not one

The original diagnosis named only the first. The second and third were found
by measurement while curing it, and each was larger than the first.

1. **Fixture registry installation (as diagnosed).** `ROW_REGISTRY_RELATIVE_PATH`
   moved `v1 → v2` as ruled, but six test modules installed
   `configs/arm_readiness/d117_row_registry_v1.json` into their temporary
   repositories by hardcoded name, so `load_registry` raised `FileNotFoundError`
   on the v2 path. Cured: fixtures install the candidate registry at the live
   coordinate, and recorded receipt references now read `registry_id` from the
   registry the fixture actually installed instead of hardcoding a generation.

2. **The registry had already advanced to the `_v4` family.** The ruled v2
   registry's `successor_policy.successor_pack_ids` installs
   `d117_floor_qwen25_1p5b_v4` / `_7b_v4` / `contrast_..._v4`, and
   `_plan_profile` admits a successor only on exact pack-id match. Every
   fixture built `_v2` packs, so all of them were refused with
   `successor ID … is not installed by the R1 registry`. Cured per ruling 1:
   fixtures carry the ruled `_v4` ids. S-0 mints pack BYTES; the IDs are
   council-ruled values this candidate's own registry already installs, so a
   synthetic fixture carrying one exercises the admit path and mints nothing.

3. **Frozen packs bind the ARCHIVAL coordinate by design.** The committed
   `_v1`, `_v2` and `_v3` campaign packs' `plan_tree.json` all record
   `d117_row_registry_v1.json` / `d117-row-registry-v1` / sha `d248fdc5…`.
   That is not drift — it is exactly why the ruling keeps v1 in-tree and
   sha-pinned, so frozen recorded references keep resolving. Cured per ruling
   2: `test_plan_tree_slots_bind_profiles_and_never_name_future_arm_receipt`
   now asserts BOTH halves explicitly, citing `MAGISTRATE-RULING.md:124-131` —
   the archival half per pack inside the loop, and the live half after it
   (`ROW_REGISTRY_RELATIVE_PATH` is the v2 coordinate, `registry_id` is
   `d117-row-registry-v2`, and the two shas provably differ). **No frozen pack
   bytes were touched.**

#### 9.3.2 Ruling option 3 — proven dead, and discharged

The ruling's option 3 allowed a fixture to model the pre-`_v4` era by keeping
`_v2` ids with the archival v1 registry installed as that fixture's registry.
**That configuration cannot be built.** `load_registry`
(`joulewise/arm_readiness.py:2688`) resolves exactly one coordinate,
`ROW_REGISTRY_RELATIVE_PATH`, so a fixture repository holding only the v1 file
fails outright with `cannot read row registry: … d117_row_registry_v2.json`;
installing both files does not help, because `_registry_reference` then loads
v2 and `_plan_profile` refuses the `_v2` pack as not installed. The mechanism
was built, proven dead by execution, and removed rather than left as a
documented-but-unusable knob. The only pre-`_v4` packs that still resolve are
generation-1 ones, which short-circuit through `_PROFILE_BY_PACK` before the
registry is consulted — that path works and needs no special handling.

#### 9.3.3 Two dissolved premises — reconstructed, not retired

Per the second ruling, the PROPERTY outranks the premise: where the refusal a
test needs is reconstructible in the ruled configuration, the test is rewritten
to it rather than blocked.

- **`test_predecessor_authenticates_outside_the_live_map_and_resolver`** proves
  that a predecessor the live lookups refuse still authenticates from its own
  recorded bytes. Only its second refusal broke: the old premise leaned on the
  registry-FREE `_plan_profile`, where `_v1` matched no successor shape, and
  `_v3` does match. `resolve_frozen_plan` never stopped refusing. Reconstructed
  on the PRODUCTION admission path — `_plan_profile(predecessor, registry)`,
  which refuses because the registry does not install `_v3`. This is the
  stronger assertion: the shape-only route is documented as a pre-registry
  convenience for construction tools, not the admission gate. **Green.**

- **`test_r1_lifecycle_is_dormant_for_historical_v1_registry_and_profile`** →
  renamed `test_r1_lifecycle_grandfathers_a_historical_v1_pack_and_profile`.
  Dormancy is now **structurally unreachable**, not merely unobserved:
  `_r1_lifecycle_registry_for_pack` returns `None` only for a non-R1 schema,
  and the repoint leaves one R1 registry for every pack. The safety concern it
  protected — a v1-era pack must not be silently swept into R1 semantics —
  survives in a different mechanism, an explicit grandfathering refusal, and
  that is what the test now asserts (`V1_GRANDFATHERING` →
  `readiness_r1_v1_grandfathering`). **Green.** Nothing was retired and no
  property was left vacuous.

#### 9.3.4 Two candidate defects cured under the lease extension

Both files are the candidate's own and neither is in the r6-pinned set
(verified).

1. **`joulewise/arm_readiness.py` — absent predecessor directory failed ugly.**
   `generate_freeze_receipt` evaluated
   `Path(predecessor_pack_root).resolve(strict=True)` inside the
   family-publication gate CONDITION, so a missing directory escaped as a bare
   `FileNotFoundError` instead of a governed refusal. It was unreachable while
   no registry carried a generation threshold — the `and` short-circuited on
   `family_first_generation is None` — and the ruled registry supplies
   `family_publication_first_generation: 4`, which made it live. The
   predecessor is now resolved once, and an unreadable root raises the governed
   `_successor_chain_refusal` (`readiness_successor_chain_invalid`). No new
   reason codes. Regression added:
   `test_absent_predecessor_directory_refuses_with_the_governed_code`, which
   names an absent pack at a GATED generation so it exercises the branch the
   threshold guards.

2. **`joulewise/arm_readiness_evidence.py:1441` — the closed refusal census did
   not know the candidate's own codes.** Seven `readiness_r1_*` codes are
   resolved BY ROLE from the ruled registry's
   `freeze_evidence_lifecycle.refusal_vocabulary` at the moment of refusal, so
   they deliberately never appear as literals in the runtime source: the
   registry, not the module, is the code/type authority, and the registry-load
   closure check is what keeps them registered. They are now listed in the
   module's `dynamic` set with that authority comment, mirroring the same cure
   applied to `dynamic_or_defensive` in
   `tests/test_arm_readiness_integration.py`. The two sets must stay in step.

#### 9.3.5 The 21 blocked tests — RECLASSIFIED BY MEASUREMENT (2026-08-23)

**This section's original claim was false and is retracted.** It stated that
every entry was marked `@unittest.expectedFailure` with the reason string
`S0-BLOCKED: requires minted _v4 packs` and a docstring, and that all 21 must
flip green in the S-0 clone proof. The independent seat refuted this and the
refutation was reproduced. What was wrong, precisely:

1. **`@unittest.expectedFailure` passes on ANY exception**, so all 21 asserted
   nothing — an import error and a security-relevant refusal ceasing to fire
   both read as "expected."
2. **There was no reason string at all.** `unittest.expectedFailure` has
   signature `(test_item)` and sets exactly one attribute,
   `__unittest_expecting_failure__`. The quoted text was a trailing SOURCE
   COMMENT on the decorator line, attached to nothing, absent from every
   report, and invisible to tooling — so the set could not be mechanically
   enumerated at all, while being made an S-0 acceptance criterion.
3. **The reason was measured-wrong for the dominant cause** (see below).
4. **3 of 21 had a docstring**, not 21 of 21.
5. **One entry could never flip green** under any mint (it asserts membership
   of a static code dict, and S-0 mints bytes, not source-map entries).

The cure and the measured partition are recorded in §10.2. In summary: every
`@unittest.expectedFailure` is gone (zero remain anywhere in `tests/`),
replaced by `@unittest.skip("<CLASS>: <measured cause>")`, which takes a real
reportable argument and cannot swallow arbitrary exceptions; and the measured
partition is **`S0-BLOCKED` = 0, `STRUCTURAL-BLOCKED` = 17,
`CRASH-BLOCKED` = 4**. No test in this repository is unblocked by S-0's byte
mint. The groups below are preserved for their per-test detail, RELABELLED to
the measured classes.

**Group 1 — STRUCTURAL-BLOCKED, fixture schema (14).** Originally filed as
"V1_GRANDFATHERING (18 of 21)"; the four ACID tests listed under
`test_arm_readiness_evidence_t0.py` are excluded here and appear as Group 4,
because they abort the interpreter rather than fail. The fixtures author
legacy-schema PACK evidence. Under the R1 registry a PASSING freeze requires
R1-schema evidence, so authoring refuses with
`legacy generic freeze evidence may not enter the R1 lifecycle`
(`joulewise/arm_readiness.py:5322`).

**Why this is NOT an S-0 blocker — the correction.** That refusal has two
conjuncts, and both are properties of THIS BRANCH: its own registry repoint,
and `make_go_fixture` authoring legacy generic freeze evidence while R1
requires content/execution receipt schemas. **Minting `_v4` pack bytes changes
neither conjunct**, so no byte S-0 produces can flip these tests — independently
reproduced by two seats. The original text attributed them to the "complete
pack fixture with a passing freeze receipt" work item §9.2 assigned to S-0;
that attribution is withdrawn. The real cure is fixture modernization, tracked
as kernel row `FIXTURE-MODERNIZATION-01` (A84) and NON-GATING for S-0, because
S-0 proves the transaction on REAL R1 artifacts in its clone, not on fixtures.

- `tests/test_arm_readiness_evidence_t0.py` (3): `test_arm_consumes_volatile_receipts_within_short_horizon`,
  `test_mocked_forbidden_process_evidence_expires_before_arm`,
  `test_forbidden_process_started_after_authoring_expires_before_arm`
- `tests/test_arm_readiness_integration.py` (5): `test_alpha_beta_gamma_end_to_end_pass_and_no_hash_cycle`,
  `test_same_head_pack_terminal_evidence_and_final_arm_bindings_go_stale`,
  `test_verification_recomputes_current_pack_bytes_despite_skip_worktree`,
  `test_missing_arm_only_evidence_refuses_and_bound_source_mutation_stales_go`,
  `test_identity_arm_evidence_symlink_escape_refuses`
- `tests/test_arm_readiness_dry_run.py` (4): `test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots`,
  `test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change`,
  `test_dry_run_refuses_a_dirty_or_nonreviewed_checkout`,
  `test_dry_run_rehearsal_root_and_id_are_single_use`
- `tests/test_arm_readiness_lifecycle.py` (2): `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`,
  `test_boot_session_change_voids_verification_and_consumption`

**Group 2 — STRUCTURAL-BLOCKED, gate shadowing (1).** `tests/test_arm_readiness_lifecycle.py::test_self_wrong_role_and_ordinal_violations_refuse`.
Its self-reference leg mints with the pack as its OWN predecessor; with
`family_publication_first_generation: 4` a `_v4` self-predecessor engages the
family-publication gate FIRST, so the mint RETURNS a REFUSE record carrying
`readiness_r1_family_publication` ("marker_absent: registry-installed family
has no marker") instead of RAISING `readiness_successor_chain_invalid`.
Confirmed by direct probe. The property is intact but shadowed until a real
`_v4` family marker exists.

**Group 3 — STRUCTURAL-BLOCKED, historical pairing (1).**
`tests/test_arm_readiness_lifecycle.py::test_historical_predecessor_resolves_and_still_anchors_the_chain`
asserts the successor's predecessor is a `_PROFILE_BY_PACK` entry — true only
of the `_v2`/`_v1` pairing. The ruled family's predecessor is `_v3`, which is
neither a map entry nor an installed successor. `_PROFILE_BY_PACK`
(`joulewise/arm_readiness.py:287-291`) is a **static code dict** holding only
the three `_v1` ids, so **this test can never flip green under any mint**: S-0
mints bytes, not source-map entries. It was therefore wrong to list it as
S0-BLOCKED under any theory.

**Disposition (magistrate ruling R2, 2026-08-23): neither retired nor
reconstructed now.** The property under test — predecessor-chain
authentication — is real and safety-relevant, so the test must be reconstructed
rather than deleted; but reconstruction needs real `_v4`→`_v3` receipt chains
that exist only AFTER S-0 mints. The honest STRUCTURAL skip therefore stands,
carrying a pointer to its owning row. **Recorded design for that
reconstruction:** replace the static `_PROFILE_BY_PACK` map-membership
assertion with an authenticated runtime `_v4`→`_v3` predecessor proof supplying
a valid synthetic family-publication marker. The false map-membership assertion
must be REPLACED, never preserved in any form. Assigned to
`FIXTURE-MODERNIZATION-01` (A84) as its post-mint item.

**Group 4 — CRASH-BLOCKED (4).** The four ACID tests in
`tests/test_arm_readiness_evidence_t0.py`:
`test_acid_authored_fifteen_then_real_arm_generator_reaches_go`,
`test_acid_real_boot_session_then_real_arm_generator_reaches_go`,
`test_synthetic_acid_is_hermetic_to_system_timezone`,
`test_synthetic_acid_ignores_wall_clock_48_hours_in_future`. These ride a
**pre-existing process-level `SIGABRT` (exit 134)** at
`joulewise/adapters/mlx_runtime.py:1159`, reached under pytest, which aborts
the interpreter at ~9% of a full-suite run. **Not a branch regression:** it
reproduces at merge-base `5523003`, verified by extracting the base tree with
`git archive`. They are `skip` and not `xfail` for a mechanical reason: an
`expectedFailure` marker cannot contain a process-level abort — a test that
kills the interpreter does not make the suite green, it makes the suite
UNCOLLECTABLE. Tracked as kernel row `MLX-ACID-SIGABRT-01` (A85).

**Group 5 — STRUCTURAL-BLOCKED, generator chain (1).** `tests/test_d117_decode_contrast_plan.py::test_authenticated_freeze_transition_preserves_frozen_bytes`
drives the committed `_v1` generators with `--family-suffix _v2`; the generated
`_v2` pack is refused at admission, yielding
`readiness_row_registry_mismatch` where the test expects
`readiness_successor_chain_invalid`. Driving them to `_v4` needs the
intervening `_v3` chain, which is S-0's mint.

#### 9.3.6 RETRACTED FINDING — "the re-derivation refusals are unreachable from a fixture"

**This section previously escalated a dilemma to the gauntlet's independent
seat: was the reviewed-HEAD gate over-broad (a candidate DEFECT), or does HEAD
custody legitimately subsume the semantic re-derivation check (a CONTRACT
change)? The independent seat answered: NEITHER. The finding was a
misdiagnosis — a fixture defect — and it is retracted in full.**

**What was actually wrong.** The 112-entry changed-set allowlist is
**pack-name-exact** to the three `_v4` packs, deliberately and with no globs
(`docs/contracts/receipt_histsem_verifier.md:145-146`). Three of the four
staged tests built a pack named `d117_floor_qwen25_1p5b_v1` — the default at
`tests/test_arm_readiness_evidence_author.py:103`. Those 33 paths are absent
from the allowlist **the candidate itself authored**, so gate 4
(`joulewise/arm_readiness.py:4308-4314`) fired. The walk through four gates
never checked whether the fixture's pack was in that allowlist.

**Proven by execution, not argument.** Rename the fixture pack to an
allowlisted `_v4` one and run the *identical* variant-4 coherent rewrite: gate
4 does not fire, control reaches `_r1_rederive_at_arm`, and it refuses with
`DOCTRINE_PIN ARM re-derivation differs from authored semantics`
(`joulewise/arm_readiness_evidence.py:1852`). The candidate's own fourth test
already used `_v4` and landed exactly on the re-derivation raise at
`arm_readiness.py:5470`; the original text recorded that and failed to draw the
inference. An alternative hypothesis — that the fixture merely failed to
repoint the receipt's own `derivation_commit` — was tested and **refuted**: the
construction is circular, since rewriting the receipts is itself a change to
those same paths, so `git diff N..N+1` returns the same 33 paths and gate 4
fires again.

**Why this was a blocker and not a nit.** Per the S-0 runsheet's mechanism
proof, the listed authenticator for the 99 allowlisted source/evidence/sidecar
paths is `readiness_evidence_digest_mismatch` — a digest check, which a
coherent rewrite defeats **by construction**. Semantic replay is the ONLY
remaining authenticator for those paths. Adopting the "legitimately subsumed"
horn would have removed the independent authentication that makes the 112-path
allowlist lawful under V-1(iii) — the exact ground on which D-151 refused
Option 1. The misdiagnosis would have propagated a false conclusion into the
ruling this candidate implements.

**Cure applied (§10).** The fixtures were retargeted to an allowlisted pack;
the wrong-expectation at `tests/test_arm_readiness_evidence_author.py:645` (it
expected `"differs from freshly derived bytes"`, the **legacy v1-path**
message at `joulewise/arm_readiness_evidence.py:2194`, where the R1 path emits
`"ARM re-derivation differs from authored semantics"`) was corrected; and the
variant-4 in-test comments at `:569-578` and `:627-633`, which asserted as
FACT the claim this retraction refutes ("every integrity gate passes and only
re-derivation is left" — when measured, the added commit is what *creates* the
`DEPENDENCY_CHANGED_SET` refusal), were rewritten to state what the fixture
actually does. **All four tests are now ordinary green**, measured at the
fix-round head; `test_arm_readiness_evidence_author` runs 24 tests, OK.

**Meta-observation carried forward (from the independent seat).** Both of that
seat's cheap-to-fix blockers shared one signature: the implementer reasoned
carefully to a conclusion and never ran the cheapest falsifier. §9.3.6 walked
four gates without checking whether the fixture's pack was in the allowlist it
had itself authored; the 21 markings were written without running one of them
to see what actually raised. That is a two-round same-signature pattern, and it
is why this fix round was conducted **measurement-first**: every claim in §10 is
backed by a run recorded in this document, and the fix round's own three
defects (§10.4) were likewise found by running the modules, not by reasoning
about them.

#### 9.3.7 Repository-radius measurement at the fix-round head

This replaces the struck 1,368-test figure with a measurement over the **whole
repository**, taken at the fix-round head on 2026-08-23 by the close-out seat:

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q          # whole repository, no -k, no deselection

3746 passed, 116 skipped, 19692 subtests passed in 2679.33s (0:44:39)
exit code 0
```

**Zero failures, zero errors, and nothing deselected.** Two properties of that
line are worth stating explicitly, because each answers a specific finding:

1. **The suite now runs to completion under pytest.** Seat item 15 recorded
   that it could not: a process-level `SIGABRT` at
   `joulewise/adapters/mlx_runtime.py:1159`, reached through the four ACID
   tests, aborted the interpreter partway through and made those tests
   *uncollectable* rather than merely red — so the seat's own completing run
   required `--deselect` on all four. Those four now carry `CRASH-BLOCKED`
   skip decorators, and a skipped test never reaches the aborting code, so the
   run completes with no deselection and no special invocation.
   **This is NOT a cure for A85.** The abort still exists in the adapter and
   still reproduces at merge-base; it is merely no longer *reached*. A85
   remains open, and its acceptance still requires the abort itself to stop
   firing.
2. **The branch is green at repository radius, which it was not before this
   round's final repair.** The first full run at this head returned
   `24 failed`. Every one of those 24 — 18 test failures plus 6 subtest
   failures — was the single stale test double of §10.4 item 4, and **nothing
   else in the repository failed**. That is why the figure above is quoted
   from the run made AFTER that repair (commit `8d51f76`); the earlier
   24-failure run is recorded here rather than discarded, because it is the
   evidence that the repair was needed and that its blast radius was exactly
   what §10.4 claims.

**On comparing this to the independent seat's number.** The seat measured
`6 failed, 3763 passed, 95 skipped, 4 deselected, 17 xfailed, 19674 subtests
passed in 2904.34s` at **base parity** — a different tree from this branch,
which adds and modifies tests. The two totals are therefore **not
like-for-like** and must not be subtracted from one another; that is the exact
error the struck 1,368-test figure committed. What can be said without
arithmetic sleight of hand is qualitative and still strong: this branch needs
no deselection where the base required four, and it reports no failures where
the base reported six — two of which the seat identified as a pre-existing
non-deterministic flake in `tests/test_calibration_exits.py` that captures an
ambient process command line. That flake did not fire in either full run made
during this round, which is a property of the flake, not evidence that it is
cured.

The two cautions of §9.3 continue to govern this figure: it is a LOCAL run and
must never be reported as D-151 condition 4's published green.

### 9.4 Frozen surfaces

**Correction (nit 16).** This section originally recorded a re-verification at
`b1c6bee`, described in §1 as "the last COMMIT BEARING CODE." That was false:
`c1b87f6` changed both `joulewise/arm_readiness.py` and
`joulewise/arm_readiness_evidence.py`, so the frozen-surface check had never
been run at the actual head. It has since been re-run twice at a real head —
independently by the seat at `c1b87f6`, and by the close-out seat at the
fix-round head (§10.5) — and all five surfaces are IDENTICAL by **blob OID**
against merge-base `5523003` at both, which is a stronger check than the
recorded SHA-256 because it compares the committed objects rather than the
working tree.

SHA-256 against merge-base `5523003`; all five **IDENTICAL** (unchanged, and
re-confirmed byte-for-byte at the fix-round head):

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
— a net +12 test methods). No test was deleted, and no assertion was weakened.

**Correction (seat should-fix 11).** This section claimed that "four tests that
were `inspect.getsource` + `assertIn` string greps were rewritten as
behavioural tests." Measured across `tests/`, `getsource` occurrences went
**9 at merge-base `5523003` → 13 at `c1b87f6`** — the finish round added source
greps on net while claiming to have removed them. The fix round cured this:
measured at the fix-round head the count is **10**, i.e. three of the four were
genuinely converted to behavioural assertions, and exactly **one net-new grep
remains** versus merge-base, at
`tests/test_arm_readiness_integration.py:597`
(`inspect.getsource(evidence_author._derive_reason_code_coverage)`). That one
is recorded here rather than claimed away. `tests/test_family_marker.py` now
contains **zero** `getsource` greps: the two source-string assertions the seat
flagged as redundant with the behavioural test were deleted, and the test that
carried them survives as what it always genuinely proved — that the builder
CLI exposes its four runsheet-exact options.

The two-part-green caution of §5 is unchanged and still governs: this is a
LOCAL run and must never be reported as D-151 condition 4's published green.

---

## 10. COMBINED FIX ROUND (2026-08-23)

This section is the record of the round that answered two independent reviews
of `c1b87f6`. Unlike §9 it is **measurement-first**: every count below was
produced by a run made during this round and recorded here, and the round's own
defects (§10.4) were found by running the code rather than by reasoning about
it. Where a finding is not cured, this section says so and says what remains.

### 10.1 What was reviewed, and by whom

| Review | Seat | Verdict | Findings |
|---|---|---|---|
| Whole-candidate audit | Independent writer≠reviewer seat, deliberately not the implementer, read-only | **REFUTED** | 3 blockers, 12 should-fix, 4 nits, 2 observations |
| G-2 security lens | Fresh read-only refuter, distinct lens (contract vs execution) | **REFUTED** | 1 blocker, 3 should-fix, 1 nit |

Both documents are custodied beside this manifest as `s1-seat-verdict.md` and
`s1-refuter-g2.md`. Their finding IDs are used verbatim below.

**Per-finding disposition.** Every verdict below was checked at source against
the mechanism, not accepted from a report; "CURED" means the code or the test
demonstrably does the thing, and a cure that only moved a claim into prose is
labelled as such. **The round did NOT close everything, and this table is the
honest count. Of the 21 review findings: 15 CURED, 4 PARTIAL (items 4, 6, 11,
12), 1 NOT ADDRESSED (item 10), 1 N/A as not a branch regression (item 15).
The round additionally INTRODUCED 3 defects and left 2 prose defects of the
B-3 class — all five recorded below rather than left for the delta reviewer to
find. Eight items are therefore open, plus the structural historical-pairing
skip of §10.3.**

| Finding | Disposition | Evidence |
|---|---|---|
| **B-1** re-derivation "unreachable" | **CURED** | Fixtures retargeted registry-side (`tests/test_arm_readiness_lifecycle.py:96-142`); the variant-4 test now lands on the R1 re-derivation raise (`tests/test_arm_readiness_evidence_author.py:667-670`). §9.3.6 retracted in full. |
| **B-2** vacuous S0-BLOCKED markings | **CURED** | §10.2; `tests/test_s0_blocked_enumeration.py` asserts the partition mechanically. |
| **B-3** in-test comments assert the refuted claim | **CURED** | `tests/test_arm_readiness_evidence_author.py:599-602,652-655` now say the commit CREATES the changed set. |
| **G2-1** Ed's digest never authenticated | **CURED** | §10.1.1 below — traced and adversarially replayed. |
| 5 wrong-expectation | CURED | Now expects `ARM re-derivation differs from authored semantics`. |
| 7 no closure check on conditional paths | CURED | `joulewise/arm_readiness.py:2025-2032` refuses at registry load; falsified by a patched-constant test, not a literal. |
| 8 tautological/vacuous scheduler tests | CURED | Per-`check_id` `assertEqual` over the full map; catch-all pinned separately. |
| 9 dead predecessor-refusal stub | CURED | `tests/test_family_marker.py:549-557` runs the v5-over-v4 case; the stub's `raise` is now live. |
| 13 implied assertion / unpinned classes | CURED | Positive boot-binding assertion; the full 30-entry freshness map is pinned. |
| 14 dual-coordinate archival pin | CURED (prose) | The false "must keep resolving" comment is replaced by an accurate one. Correct fix: the finding WAS the false comment. |
| 17 hand-mirrored `dynamic` sets | CURED | `tests/test_arm_readiness_integration.py:593-635` derives the set by AST parse; the mirrored literal is gone. |
| 18 unnamed scope expansion | CURED (prose) | `joulewise/arm_readiness.py:6583-6586` names it an intentional fail-closed expansion. |
| 19 minor test nits | CURED | Exact per-case diagnostics; `assertLessEqual`; comments tokenize-stripped before the grep. |
| 16 "last COMMIT BEARING CODE" false | CURED | §1 coordinate table and §9.4 corrected; frozen surfaces re-verified at a real code-bearing head (§10.5). |
| **G2-2** conditional refusal escapes raw | **CURED** | All five anchors converted to governed refusals, incl. `scheduler_gates.py:936-941`. |
| **G2-3** unenumerated pinset override | **CURED** | `joulewise/arm_readiness.py:3176-3189` refuses any `pinset_path` resolving outside the enumerated coordinate; the refuter's exact probe is now a test. |
| **G2-4** dormant threshold fails open | **CURED** | Threshold mandatory; `generate_freeze_receipt` no longer swallows the missing-threshold error. |
| **G2-5** G7 post-verify re-read TOCTOU | **CURED** | `scheduler_gates.py:894-898` binds the digests computed inside the verifier; both re-reads deleted. |
| 15 pytest `SIGABRT` | **N/A — not a branch regression** | Reproduces at merge-base; the four tests carry `CRASH-BLOCKED` skips; tracked as A85. |
| **10 G7 PASS never exercised against a real marker** | **NOT ADDRESSED** | Still mocked in every G7 PASS test. Structural — see §10.3 partial 1. |
| 4 ungoverned escape at the library boundary | **PARTIAL** | The named leak is closed at its root (`validate_step6_confirmation_table` no longer calls the `ArmReadinessError`-raising primitive) plus a defensive conversion. **But `generate_arm_receipt` still has no `ArmReadinessError` catch-all**, so the library boundary remains strictly weaker than `scheduler_gates.py:936-941`. |
| 6 confirmation-table defaulting asymmetry | **PARTIAL** | `_authenticate_existing_r1` is now threaded and the misleading claim is corrected (§9.1 G-2 row). **The asymmetry itself is unchanged:** arm/verification/scheduler default to campaign custody; freeze, `_verify_arm_receipt`, `verify_consumed_launch` and the authoring entry point pass a bare `None`. All fail closed. |
| 11 source greps went 9 → 13 | **PARTIAL** | 10 at this head; one net-new remains (§9.5). |
| 12 `test_every_check_id_has_a_raise_site` | **PARTIAL** | Now an AST walk, so comments and docstrings no longer satisfy it. Still a PRESENCE scan, not reachability, and its `IfExp` clause harvests both branches of any conditional diagnostic assignment whether or not it feeds a raise. |

**Three defects the round INTRODUCED** (found by the same source-level audit,
verified by this seat, recorded as open rather than left for the delta reviewer
to discover):

- `joulewise/arm_readiness.py:10742` — `assert table is not None and table_raw
  is not None` is load-bearing control flow in the published lane. Under
  `python -O` the assert is stripped and `table["git"]` raises a bare
  `TypeError` — an ungoverned escape of exactly the class findings 4 and G2-2
  were written to cure. Reachable only if the invariant breaks, but the project
  does not accept bare exceptions at this boundary.
- `joulewise/arm_readiness.py:10302-10305` — `_family_member` now converts
  every residual `ArmReadinessError` into
  `FamilyPublicationError("evidence_set_mismatch")`. Fail-closed and governed,
  but registry/schema/structural faults are now DIAGNOSED as an evidence-set
  mismatch, widening what that check_id means inside a closed enumeration.
- `joulewise/arm_readiness.py:3369` — `verify_receipt_histsem_pack` gained a
  private `_pinset_rows` keyword that bypasses `_load_histsem_pinset` entirely.
  It is underscore-private, reached only from two internal call sites and one
  test, and is NOT exposed by any CLI — so it is not the G2-3 lane reopened —
  but it is an in-process override of the enumeration G2-3 just closed, and
  nothing asserts it is unreachable from an external caller.

Two further prose defects of the B-3 class were noted and are recorded, not
cured: `_require_confirmed_conditional_path`'s docstring
(`joulewise/arm_readiness.py:4207-4217`) still enumerates only the old
admission conditions and never mentions the out-of-band digest that is now the
authenticator; and `generate_freeze_receipt:6572` calls
`_family_first_generation` unguarded, a fail-ugly path defended only by a check
in a different module.

#### 10.1.1 G2-1 — the blocker, traced

Both and only both consumers of the confirmation table `C` route through
`_authenticate_confirmation_table` (`joulewise/arm_readiness.py:10551`): the
changed-set subtraction at `:4231` and the marker/publication verifier at
`:10672`. That function, **in this order**:

1. `:10564-10567` — a `None` expected digest refuses `confirmation_missing`.
   Nothing is read.
2. `:10569-10575` — a non-64-hex digest refuses `confirmation_mismatch`.
3. `:10578-10584` — only NOW are `C` and its sidecar read, the sidecar being a
   transport-integrity guard and explicitly **not** an authenticator, since it
   is made from the same bytes it accompanies.
4. `:10585-10589` — `sha256(C) != expected_confirmation_digest` refuses.
5. `:10590-10595` — only after that equality holds is
   `validate_step6_confirmation_table` called. **No table semantics — including
   the literal `authority == "ED"` and `decision == "YES"` — are parsed or
   trusted before the digest matches.**

The subtraction ordering is unchanged and still correct: `outstanding.discard`
runs only on a clean return (`:4302-4313`). **No consumer derives `hC`**: every
entry point defaults it to `None` and fails closed, and it arrives only from an
explicit operator flag on the four CLIs. The refuter's attack is replayed as a
test at `tests/test_launch_window.py:511-689` — a real repository, committed
attacker pinset bytes, a canonical `C` carrying the actual successor digest
with literal `ED`/`YES` and a matching sidecar — and the launcher exits 2 with
`readiness_r1_dependency_changed_set`, subtracting nothing and never reaching
`execve`, both with no digest and with a wrong one; only the true `sha256(C)`
subtracts.

**Residual risk, stated plainly.** `hC` is an **unauthenticated
operator-supplied string**. The trust root moved from repository bytes —
forgeable by whoever writes `C` — to an out-of-band input, which is what the
refuter demanded. But nothing in code binds that string to Ed.
`docs/contracts/d117_step6_confirmation_table.md:52-56` says the post-fixation
standing source is the literal pinned in the D-151 fixation commit; **no code
pins that literal**, so that half of the contract is prose. An adversary who
also controls the invocation, or an operator who computes `hC` from the file
rather than from transaction custody, still forges. This is the honest boundary
of the cure and belongs in the S-0 runsheet's operator discipline.

### 10.2 The blocked-test partition — measured and machine-readable

This is the cure for seat blocker **B-2**, whose five distinct defects are
enumerated and retracted in §9.3.5.

**`@unittest.expectedFailure` is eliminated.** Zero decorators remain anywhere
in `tests/`. It was the wrong tool twice over: it passes on ANY exception (so a
security-relevant refusal ceasing to fire reads as "expected"), and it takes no
argument, so the reason it was documented with was a source comment attached to
nothing and invisible to every report and every tool.

Each blocked test now carries `@unittest.skip("<CLASS>: <measured cause>")`,
which takes a real reportable argument, plus a docstring. The classes are:

| Class | Count | Meaning |
|---|---|---|
| `S0-BLOCKED:` | **0** | No test in this repository is unblocked by S-0's byte mint. |
| `STRUCTURAL-BLOCKED:` | 17 | 14 fixture-schema + 3 named singletons (§9.3.5 groups 1, 2, 3, 5). |
| `CRASH-BLOCKED:` | 4 | The ACID tests riding the pre-existing `SIGABRT` (§9.3.5 group 4). |

**The measured `S0-BLOCKED` set is EMPTY.** That is the substantive result of
this round, and it is why magistrate ruling R1 of 2026-08-23 STRUCK the 21-test
flip addendum from S-0's acceptance: the addendum encoded a theory that
measurement disproved, and since the set is empty it gated nothing. S-0's
acceptance reverts to its primary, always-authoritative form — the runsheet r2
§5 proving-obligations checklist (r4-2/V-2 obligations, the full probe battery,
and the D-151/marker additions), which never depended on fixtures at all. The
runsheet r2 §5.1 amendment recording that strike is a lead edit applied at the
pre-execution read of the runsheet; this round does not touch the runsheet.

The partition is not a prose claim. `tests/test_s0_blocked_enumeration.py`
asserts it mechanically by AST parse over every `tests/test_*.py`: it requires
zero `expectedFailure` decorators, the exact counts 0/17/4 totalling 21, and —
for every blocked test — exactly one class prefix, a non-empty cause clause
after the prefix, and a non-empty docstring. A future edit that reintroduces an
`expectedFailure`, or adds a blocked test without a machine-readable cause,
fails that test.

### 10.3 The two honest partials

Recorded as OPEN, not as cured.

**Partial 1 — FIX-10 (G-7's PASS direction) is a post-S-0 item.** The seat's
item 10 is that G7's PASS path has never been exercised against a real family
marker; `verify_family_publication_marker` is mocked and the on-disk marker in
those tests is the literal `b"marker"`. This cannot be closed at this head for
a structural reason, not a scheduling one: a genuine PASS requires the three
real `_v4` packs and a real published marker, which are **S-0's outputs and do
not exist yet**. Recorded as a post-S-0 obligation rather than papered over
with a better mock.

**Partial 2 — the historical-pairing test remains a STRUCTURAL skip.**
`test_historical_predecessor_resolves_and_still_anchors_the_chain` can never
flip green under any mint, because it asserts membership of a static code dict
(`_PROFILE_BY_PACK`) and S-0 mints bytes, not source-map entries. Per
magistrate ruling R2 it is **neither retired nor reconstructed now**: the
property is real and safety-relevant, so it must be reconstructed rather than
deleted, but reconstruction needs real `_v4`→`_v3` receipt chains that exist
only post-S-0. The skip carries a pointer to the row that owns the
reconstruction, and the design is recorded in §9.3.5 group 3.

### 10.4 The fix round's OWN defects, found by measurement

Fix rounds introduce defects. This section records the **four of ONE CLASS**
that were found by **running** the code rather than by reasoning about the diff
— the discipline the seat's meta-observation demanded. All four share a single
signature: **a surface the round moved on ONE SIDE ONLY.** Three further
defects of a different class, found by source-level audit rather than by
execution, are recorded in §10.1 and remain OPEN. These four are recorded here
because a reader who sees only the green result would not know the round had to
be corrected to reach it.

1. **A stale hand-built argument namespace.**
   `tests/test_arm_readiness_lifecycle.py::install_launch_manifest` constructs
   an `argparse.Namespace` by hand for `launch_window.launch()`. The round
   added `expected_confirmation_digest` to that CLI and updated the sibling
   builder in `tests/test_launch_window.py`, but not this one, so the launcher
   raised `AttributeError`. Cured by mirroring the parser, which supplies
   `None`.
2. **A signature fence pinned on one side.**
   `tests/test_arm_readiness_evidence_author.py` asserted the public authoring
   signature was exactly `("pack_root",)`, while the library had already
   RE-FOUNDED that same fence at import time
   (`_assert_public_author_signature`) around the widened three-tuple. The test
   now mirrors the library exactly and additionally pins that both step-6
   parameters are keyword-only with a `None` default; the anti-injection
   assertions are untouched. **This one widens a fence originally established
   by a cold-gate synthesis, and is flagged as the first item for the delta
   re-audit** — see §10.7.
3. **A synthetic registry that predates a new closure check.**
   `tests/test_arm_readiness_evidence.py::resolved_r1_row_registry` shipped an
   empty allowlist, which the round's new registry-load closure check —
   the cure for the fail-OPEN `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` drift —
   correctly refuses. Cured by having the synthetic ROW registry carry the real
   conditional paths, for the same reason it already carries the real refusal
   vocabulary. Note that the check behaved exactly as designed: it failed
   CLOSED on a registry that did not enumerate the path it governs.

4. **A test DOUBLE whose signature no longer matched the function it stands
   in for — and the one defect the module-level verification could not see.**
   `tests/test_arm_readiness.py::_verify_with_launch_recipe_replay` patches
   `_derive_arm_semantics_for_verification` with a `side_effect=` double whose
   signature accepted only `launch_binding_cache`. Production now also passes
   `step6_confirmation_table` and `expected_confirmation_digest`, so `TypeError`
   was raised **from inside the mock** and the tests failed for a reason
   unrelated to what they assert. Blast radius **24**: 18 test failures plus 6
   subtest failures, being 3 methods across the 6 modules that inherit the
   shared `LaunchConsumptionV2Tests` mixin. Cured by mirroring the production
   signature, naming both parameters explicitly rather than swallowing them
   with `**kwargs`, so the next signature change fails loudly at the double
   instead of drifting silently.

   **Why this one matters out of proportion to its size.** It was invisible to
   the twelve-module joint verification because `tests/test_arm_readiness.py`
   — the module that DEFINES the shared mixin — was not in that set, which had
   been derived from the reviews' scope. Only the repository-radius run found
   it. It was also the ENTIRE delta between this branch and the independent
   seat's baseline: of the 24 failures in the first full run, all 24 were this
   one defect and **nothing else in the repository failed**.

**The systematic response, because this was the FOURTH of one class.** Rather
than fix a fourth instance and re-run — the shape the standing escalation
trigger exists to interrupt — every signature-bearing double was
cross-referenced against every changed signature mechanically: all functions in
the eight touched modules were AST-diffed between `c1b87f6` and the fix-round
head, yielding **22 functions whose signature changed** and **9
`side_effect=<named function>` doubles targeting them**. The other 8 accept
`*args, **kwargs` or `**_kwargs` — and `tests/test_scheduler_gates.py:310`
deliberately reads `expected_confirmation_digest` — so the one repaired above
was the only broken one. No further instances remain.

An earlier mechanical sweep for the other shapes of this class — every
hand-built namespace feeding an `args.<attr>` reader, every `inspect.signature`
and arity pin, every `__all__` census, every CLI flag-list assertion, and every
"these two sets must stay in step" pair — found **no others** that are
test-enforced. It did find three stale hand-transcribed digests in §2.4 of this
manifest, which are corrected there. **Note the gap it left:** that sweep did
not cover mock doubles, which is exactly where defect 4 was hiding. The lesson
is recorded rather than smoothed over.

**These four are not the whole story.** A separate source-level audit of the
round's diff against both review documents found three further defects the
round introduced, of a DIFFERENT class — not one-sided mirrors but new code
paths — together with two prose defects. They are recorded in §10.1 and are
open, not cured.

### 10.5 Frozen surfaces, re-verified at the fix-round head

The four r6-pinned estimator sources and the archival v1 registry, compared to
merge-base `5523003` **by blob OID** — the committed objects, not the working
tree — at the fix-round head. All five **IDENTICAL**:

```
9a552db781ab  joulewise/powermetrics_fiducial.py             IDENTICAL
bc2b4544fc4b  joulewise/uncertainty_evidence.py              IDENTICAL
8fa6db3c444f  joulewise/adapters/powermetrics.py             IDENTICAL
82449d582092  joulewise/reduce.py                            IDENTICAL
434f1f6d33fe  configs/arm_readiness/d117_row_registry_v1.json IDENTICAL
```

Their SHA-256 values are unchanged from those recorded in §9.4 and re-confirmed
byte-for-byte at this head. This closes nit 16's real consequence: the check
had never been run at a commit that actually bore code.

### 10.6 Kernel rows to register in the next kernel wave

Two rows are drafted and carried forward by this round. Both are **P3 Backlog,
READY [AGENT]**, and both are **NON-GATING for S-0**.

- **A84 `FIXTURE-MODERNIZATION-01`** — modernize the arm-readiness test
  fixtures so `make_go_fixture` authors R1 content/execution receipt schemas
  instead of legacy generic freeze evidence, unblocking the 14
  `STRUCTURAL-BLOCKED` fixture-schema tests that stop at
  `joulewise/arm_readiness.py:5322`; and, as its POST-MINT item, reconstruct
  `test_historical_predecessor_resolves_and_still_anchors_the_chain` as an
  authenticated runtime `_v4`→`_v3` predecessor proof with a valid synthetic
  family-publication marker, REPLACING (never preserving) the false
  `_PROFILE_BY_PACK` map-membership assertion. Non-gating because S-0 proves
  the transaction on REAL R1 artifacts in its clone, not on fixtures.
- **A85 `MLX-ACID-SIGABRT-01`** — cure the pre-existing process-level `SIGABRT`
  (exit 134) at `joulewise/adapters/mlx_runtime.py:1159`, reached under pytest
  via the four ACID tests, which aborts the interpreter partway through a
  full-suite run and makes those tests uncollectable rather than merely red.
  NOT a branch regression: it reproduces at merge-base `5523003`, verified by
  extracting the base tree with `git archive`. Any cure is adapter-side and
  must not touch the four r6-pinned estimator sources.

The full paste-ready row text for both, with acceptance evidence and fences, is
carried in the round's lead packet (`s1-fixround-packet.md`, custodied beside
this manifest).

### 10.6b Fix-round commits, and the state they leave

```
d3101d6  WIP: combined fix round — streams A+B reconciled, pre-final-verification
134c05d  S-1 fix round: ruled seam cure + three defects found by joint verification
8d51f76  S-1 fix round: repair the fourth one-sided mirror — a test double's signature
<this>   S-1 fix round: MANIFEST rewritten from measured results  (documentation-only)
```

State at `8d51f76`, all measured during this round:

- **Repository radius:** `3746 passed, 116 skipped, 19692 subtests passed`,
  exit 0 — zero failures, zero errors, nothing deselected (§9.3.7).
- **The fourteen review-scope modules:** 275 tests, zero failures, zero errors,
  21 skips, one `unittest` invocation per module (§9.3).
- **The blocked partition:** `S0-BLOCKED` 0, `STRUCTURAL-BLOCKED` 17,
  `CRASH-BLOCKED` 4, asserted mechanically (§10.2).
- **Frozen surfaces:** all five IDENTICAL to merge-base `5523003` by blob OID
  at this exact head (§10.5).

### 10.7 What the delta re-audit must check

This section is a **self-report by the seat that ran the fix round**, and by
the same rule §9 was held to, it cannot grade itself. The round has NOT been
independently audited. A delta re-audit over the whole range
`c1b87f6..<fix-round head>` is required before acceptance, and these are its
charges, in priority order:

1. **The widened authoring-signature fence (§10.4 item 2) — FIRST ITEM.** The
   public `author_arm_readiness_evidence` signature grew from `("pack_root",)`
   to a three-tuple, and BOTH the library's import-time assertion and the
   mirroring test were written by the seats that widened it. Confirm against
   the 2026-08-12 cold-gate synthesis that two keyword-only, `None`-defaulted
   CUSTODY inputs are admissible under a fence whose stated purpose is to admit
   no OUTCOME-BEARING seam — and that they carry no outcome. If that reading is
   wrong, the correct cure is to revert the authoring-path threading, not to
   relax the fence.
2. **G2-1's closure, adversarially.** The cure makes the operator-supplied
   digest mandatory and refuses before parsing any table semantics. Re-run the
   refuter's own attack and the six bypasses. Confirm in particular that the
   expected digest is NEVER derived from the table it authenticates, on any
   path, and that every consumer that omits it REFUSES rather than proceeding.
3. **The fix round's edits to the reviews' own findings.** Every disposition in
   §10.1 was verified at source by this seat, but the seat is the interested
   party. Spot-check the CURED verdicts against the mechanism, and confirm that
   nothing recorded as cured is merely a prose claim.
4. **The retraction of §9.3.6.** Confirm that retargeting the fixtures to an
   allowlisted pack genuinely reaches the re-derivation refusal — that the four
   tests are green for the RIGHT reason and not because an assertion was
   weakened.
5. **The struck 21-flip addendum.** Confirm the measured `S0-BLOCKED` set is
   genuinely empty — i.e. that no test now carrying `STRUCTURAL-BLOCKED` would
   in fact flip on S-0's mint. A misfiled test here would silently remove a
   real S-0 acceptance obligation.
6. **The two honest partials (§10.3)** are genuinely structural, not
   scheduling convenience.
7. **The three defects this round introduced and the two prose defects**
   (§10.1). They are recorded, not cured. Decide whether the `-O`-strippable
   `assert` in the published lane, the widened `evidence_set_mismatch`
   diagnosis, and the private `_pinset_rows` override are acceptable at this
   head or must be cured before acceptance. None is a blocker in this seat's
   judgement; that judgement is exactly what wants an independent check.
8. **The residual on G2-1** (§10.1.1): `hC` is an unauthenticated
   operator-supplied string, and the contract's "literal pinned in the D-151
   fixation commit" is prose that no code enforces. Decide whether that pin
   must become code before S-0, or whether it is operator discipline recorded
   in the runsheet.


---

*§1–§8 audited and authored by the S-1 conformance seat (writer ≠
implementer), 2026-08-22, against `bd7ebc1`. Every mechanical count, digest,
and the three top-severity findings (G-2, G-3, G-4) were re-verified at source
by the audit seat rather than accepted from a delegated report.*

*§9 authored by the finish-round implementer seat, 2026-08-22, against
`b1c6bee`. It is a self-report and is marked as one: E3's writer≠reviewer
audit has NOT been performed for this round, and acceptance requires an
independent seat over §9's claims. That audit HAS since been performed — the
independent seat verdict of 2026-08-23 — and its findings are dispositioned in
§10.1; §9's corrected regions carry their corrections inline.*

*§10 authored by the fix-round close-out seat, 2026-08-23, against
`8d51f76`. **It is a self-report and is marked as one.** Every count in it was
produced by a run made during the round and recorded in it, and every finding
disposition was checked at source rather than accepted from a delegated report
— but the seat that ran the round cannot grade the round. The delta re-audit
charged in §10.7 is required before acceptance, and §10.1 deliberately records
the three defects this round introduced, plus the four it introduced and
cured, rather than leaving any of them to be found.*
