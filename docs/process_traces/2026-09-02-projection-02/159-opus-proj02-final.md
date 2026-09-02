# 159 — Opus near-final counterreview, `feat/v5-prefill-realized-projection-02` @ `ae7dd3d8`

Seat: operation-loop §5 near-final counterreview. Lens: CONTRACT + PROCESS RECORD.
Checkout: `/Users/edr/code/JouleWise-wt-proj02-b`, detached at
`ae7dd3d83c8b19a565b885bba02b6e6765736129`, read-only, git state untouched
(`git status --porcelain` empty throughout; no checkout/stash/rebase run).
Merge-base with `origin/main`: `c5fa8a495e3a0ec74fd13bc7c1dd613626cee6f6`.
Diff: 4 files, +779/-18 — `joulewise/adapters/mlx_runtime.py`,
`joulewise/identity_pins.py`, `tests/test_identity_pins.py`,
`tests/test_mlx_runtime.py`.

Ruling 141a was NOT present in this checkout; read from
`/Users/edr/code/JouleWise/docs/process_traces/2026-09-01-fresh-model-review/141a-RULING-projection-02.md`
(byte-identical to the scratchpad copy `proj02-rulings.md` — `diff` empty).

**VERDICT: READY, conditional on one ≤2-line bench cure (CR-01).**
No blockers. One SHOULD-FIX regression gap on a ruled P-5 clause, demonstrated
with a surviving mutant no prior seat ran; one SHOULD-FIX contract-prose gap
that is magistrate-owned by P-9; one process-record escalation flag.

---

## A. P-1..P-10 → pinning tests on `ae7dd3d8`

All ten are pinned except one clause inside P-5 (CR-01). No P-item is unpinned
in full, so no BLOCKER arises from section A.

### P-1 — realize with the COLLECTION encoder, compare the triple

| Where | Assertion |
|---|---|
| `tests/test_mlx_runtime.py:481` `test_identity_projection_metadata_realizes_registered_prompt_with_collection_encoder` | `:519` `assertEqual(tokenizer.encode_calls, [(prompt_text, True)])` — pins BOTH that the registered `prompt_text` (not a synthesised prompt) is what gets encoded AND `add_special_tokens=True`. `:520-528` `assertEqual(projection["prompt_realization"], {token_count, token_ids_sha256: prompt_token_ids_sha256(token_ids), token_hash_domain: PROMPT_TOKEN_HASH_DOMAIN})` — pins that the row is the `prompt_provenance` triple and nothing else. |
| `tests/test_identity_pins.py:1244` `test_freeze_mismatch_names_all_differing_fields` | `:1264-1267` `assertEqual(raised.exception.observed["differing_fields"], ["token_count","token_ids_sha256","token_hash_domain"])` — pins that the comparison against `workload_profile.prompt_token_expectation` happens inside `_derive_projection_units`. |

Production sites: `mlx_runtime.py:341-347` (gate + `_prompt_for_workload` +
`prompt_provenance`), `identity_pins.py:1531-1550` (compare).
STILL PINS. Killed mutant of record: `add_special_tokens=False` (terra 149 V1,
`False != True`).

### P-2 — emission gate: row ONLY for expectation-bearing configs; legacy key set exact

| Where | Assertion |
|---|---|
| `tests/test_mlx_runtime.py:450` `test_identity_projection_metadata_omits_realization_without_expectation` | `:465-467` `assertEqual(set(projection), {"model","tokenizer","sampler","output_policy"})` — a hard-coded literal, not derived from the code under test. |
| `tests/test_identity_pins.py:1174` `test_legacy_projection_probe_and_checks_keep_exact_key_sets` | `:1203-1213` `assertEqual(set(metadata), {"platform","machine","device","quantization","adapters","workload_provenance"})` over the CAPTURED hashed input; `:1214` `assertEqual(len(checks), 1)`; `:1218` `assertNotIn("prompt_realizations", metadata)`. |

Production sites: `mlx_runtime.py:341`, `identity_pins.py:1399-1402`
(`if realization_configs:`), `:1470-1476` (filter).
STILL PINS. Killed mutant of record: unconditional row (terra 149 V5).

### P-3 — per-config, not representative; one prepare / one cleanup

| Where | Assertion |
|---|---|
| `tests/test_identity_pins.py:1220` `test_freeze_checks_every_registered_config` | `:1240-1241` `assertIn("configs/member-2.json", str(exc))` **and** `assertNotIn("configs/member-1.json", ...)` — kills a `configs[0]`-only implementation and also kills row/config mis-pairing (a reversed zip would name member-1). |
| `tests/test_identity_pins.py:1507` `test_runtime_probe_prepares_and_cleans_up_once_for_two_configs` (added `d7bf2ffa`) | `:1559-1562` `len(prepare_calls) == 1`, `prepare_calls[0] is configs[0]`, `len(cleanup_calls) == 1`; `:1563` `assertEqual(projection_calls, configs)` — exactly one projector call per config, representative reused not re-probed; `:1564-1567` row order == config order. This test drives the REAL `_runtime_probe_metadata` (`RUNTIME_PROBE_METADATA(...)` at `:1555`), stubbing only the adapter resolvers — it is the only projection test that enters the real function to completion. |

STILL PINS. Killed mutants: `configs[0]` only (terra 149 V2); per-candidate
prepare/cleanup (Sol 155 V3 `2 != 1`, luna 157 V4).

### P-4 — refusal vocabulary; no new codes

| Clause | Where | Assertion |
|---|---|---|
| mismatch → `readiness_identity_environment_dirty` naming EVERY differing field | `tests/test_identity_pins.py:1244` | `:1261-1263` reason code; `:1264-1267` all three fields in `differing_fields`; `:1268-1269` each field name appears in the message; `:1270` config path in the message. |
| unrealizable → `readiness_identity_artifact_unreadable` with the config path | `:1333` `test_projection_refuses_unavailable_registered_realization` | `:1348-1351` reason code + `assertIn("configs/member-1.json", ...)` (missing-row arm); `:1377-1380` same for the real `RuntimeWithoutProjection` arm. Also `:1422` digit-string test `:1440-1444`. |
| frozenset / `arm_readiness.py:233-246` / `len == 56` census / D-078 test byte-unchanged | verified at head, not just at `717b1ddb` | `git diff c5fa8a49 ae7dd3d8 -- joulewise/arm_readiness.py` → 0 lines; `IDENTITY_PIN_PROJECTION_REASON_CODES` (`identity_pins.py:38-46`) not in the diff; `tests/test_arm_readiness_schemas.py` not in the diff; `test_projection_reason_vocabulary_is_closed` (`tests/test_identity_pins.py:1700`) unchanged by the diff. |

STILL PINS.

### P-5 — check rows, `shared_mint_projection`, `expected == observed`, digest binding

| Clause | Where | Assertion |
|---|---|---|
| one check per expectation-bearing config | `tests/test_identity_pins.py:1382` `test_projection_check_ids_carry_shared_mint_projection` | `:1401` `assertEqual(len(prompt_checks), 2)`; `:1402-1405` `[check_id.split(":")[1] …] == ["configs/member-1.json","configs/member-2.json"]`. |
| `check_id` contains `shared_mint_projection` | same | `:1406-1411` `all("shared_mint_projection" in check["check_id"] for check in receipt["checks"])` — over ALL checks, from the FROZEN receipt on disk. |
| `expected == observed` on PASS | same | `:1412-1414` `all(check["expected"] == check["observed"] …)`. |
| four-key envelope | same | `:1415-1420` `all(set(check) == {"check_id","status","expected","observed"} …)`. |
| **status is `PASS`** | **NOWHERE** | **CR-01 — see §D. Mutant `"status": "PASS"` → `"OBSERVED"` at `identity_pins.py:1557` survives all 87 tests.** |
| rows go into `probe_metadata` so `projection_input_sha256` binds them | `:1569` `test_projection_input_sha256_binds_realization_rows` (added `01a94592`, extended `ae7dd3d8`) | `:1601-1616` the CAPTURED `probe_metadata["prompt_realizations"]` equals the two ordered expectation rows; `:1617-1619` the returned digest equals `canonical_json_sha256` of that captured input; `:1621-1632` the FROZEN receipt's `pack.projection_input_sha256` equals the same digest. |
| no receipt / receipt-unit fields added | `identity_pins.py:97-145` | `RECEIPT_FIELDS` / `RECEIPT_UNIT_FIELDS` / `UNIT_FIELDS` / `CHECK_FIELDS` unchanged; only the module-private `_PROMPT_REALIZATION_FIELDS` (`:135-139`) was inserted. Enforced at runtime by `_require_exact_keys(check, CHECK_FIELDS, …)` (`:721`). |

PINNED except the `status` value — the one clause where a ruled word ("One
**PASS** check") has no biting assertion.

### P-6 — freeze escapes before any write; arm re-derives and REFUSEs with pack bytes unchanged

| Where | Assertion |
|---|---|
| `:1220` | `:1242` `assertEqual(pack_bytes(self.pack), before)` after the freeze refusal. |
| `:1272` `test_arm_reverification_refuses_each_prompt_realization_drift` | three subtests, one per field: `:1325` `result["status"] == "REFUSE"`; `:1326-1329` `reason_codes == ["readiness_identity_environment_dirty"]`; `:1330` `observed["differing_fields"] == [field]`; `:1331` pack bytes unchanged. Freeze happens under a clean probe first, so the test proves arm RE-REALIZES rather than trusting the frozen PASS. |
| `:1422` digit-string subtest `path="arm_reverification"` | `:1497-1505` REFUSE + `readiness_identity_artifact_unreadable` + pack bytes unchanged, and (added `ae7dd3d8`) the same code out of the full arm mapper `arm_readiness._run_identity_arm_reverification` (`:1491-1495`, asserted `:1502-1504`). |

STILL PINS. Killed mutant of record: trust the frozen PASS at arm (terra 149
V6, `'PASS' != 'REFUSE'`, 3 failures).

### P-7 — legacy-receipt invariant

(a) exact legacy key set — pinned twice, see P-2 (`tests/test_identity_pins.py:1203-1218`,
`tests/test_mlx_runtime.py:465-467`); both are literals, so the "expectation derived from
the code under test" failure mode is absent.
(b) no issued receipt is rewritten — `git diff --name-only c5fa8a49 ae7dd3d8` lists four
source/test files and zero receipt files; verified at head, not just at `717b1ddb`.
(c)/(d) are ruling facts about `_v1`–`_v3` staleness and the first `_v5` freeze — not
test-pinnable, and correctly so.
STILL PINS.

### P-8 — gates

Process clause, not test-pinned. Record state, §E. Two P-8 obligations remain
OPEN and are correctly post-merge: the D-121 terminal review must be retriggered
by the post-review commits `d7bf2ffa`/`ae7dd3d8`, and the magistrate's THROWAWAY
`_v5` freeze+arm against the real Qwen tokenizers must precede any night use.

### P-9 — WRITE_SCOPE

`git diff --name-only c5fa8a49 ae7dd3d8` → exactly `joulewise/adapters/mlx_runtime.py`,
`joulewise/identity_pins.py`, `tests/test_identity_pins.py`, `tests/test_mlx_runtime.py`.
No kernel, decision-log, council-log, run-report, RUN_STATE or TASK_QUEUE edit.
Per-commit: `717b1ddb` all four; `01a94592` `identity_pins.py` + `test_identity_pins.py`;
`d7bf2ffa` and `ae7dd3d8` `test_identity_pins.py` only. SATISFIED.

### P-10 — seven named tests + six mutants

All seven present with the exact ruled names:
1 `tests/test_mlx_runtime.py:481`; 2 `tests/test_mlx_runtime.py:450`;
3 `tests/test_identity_pins.py:1220`; 4 `:1244`; 5 `:1272`; 6 `:1333`; 7 `:1382`.
All six ruled mutants executed and killed by terra 149 (V1–V6 table in
`out/149-terra-proj02-exec.md`); the three post-fix mutants re-executed and
killed by luna 157 (V2–V4). SATISFIED.

---

## B. Refuter findings ledger — disposition of every finding

| # | Seat | Finding | Disposition |
|---|---|---|---|
| EXE-01 | 149 terra (blocker) | digit-string `token_count` coercion mutant survives 219 tests | **CURED, test-only** — production guard was already strict (`identity_pins.py:1262-1274`); the gap was coverage. `d7bf2ffa` added `test_digit_string_token_count_refused_at_freeze_and_arm_reverification` (`tests/test_identity_pins.py:1422`). Mutant executed dead: Sol 155 V2 `FAILED (failures=2)`; luna 157 V3 re-confirmed. Extended `ae7dd3d8` to the full arm mapper. |
| EXE-02 | 149 terra (blocker) | dropping rows from the hashed `probe_metadata` survives | **CURED** — `01a94592` added `test_projection_input_sha256_binds_realization_rows` (`:1569`). Mutant executed dead: luna 157 V2 `KeyError`, exit 1. |
| EXE-03 | 149 terra (blocker) | extra per-candidate prepare/cleanup unobserved | **CURED** — `d7bf2ffa` added `test_runtime_probe_prepares_and_cleans_up_once_for_two_configs` (`:1507`). Mutant executed dead: Sol 155 V3 `2 != 1`; luna 157 V4. |
| 149 residual | 149 terra | no real Qwen tokenizer exercised | **RULED, post-merge** — 141a P-8 final sentence: the magistrate freezes and arms a THROWAWAY generated `_v5` pack against the real Qwen tokenizers before any night uses it. Not a merge blocker; carried in §E. |
| F1 | 150 luna (blocker) | no last-mile realization recheck between arm and collection | **RULED OUT as a blocker** — ruling 150a R-150-1 (`150a-RULING-post-arm-recheck.md:48-52`): true but PRE-EXISTING and not specific to prompt realization (`_replay_consumed_arm` replays every identity unit the same way); projection-02 "neither opened nor widened it" (`:26-29`). Recorded SHOULD-FIX, deferred to `V5-LAUNCH-REALIZATION-RECHECK-01` (R-150-2, `:54-64`) with luna's regression adopted verbatim; fenced by R-150-3 (`:66-69`): no `_v5` night armed for CLAIM use until it lands. Written dissent from luna's BLOCKER label stands. |
| F2 | 150 luna (nonblocking) | no real Qwen3 load | Same as 149 residual — RULED, P-8. |
| (150 body) | 150 luna | `transformers_version` filtered out of the frozen probe (`identity_pins.py:1377-1388`) | **RULED, no change** — 150a R-150-4 (`:71-75`): deliberately outside the frozen probe per ruling 44c; the realization rows bind encoder BEHAVIOUR, and adding the version would refuse on harmless patch upgrades. |
| F1 | 151 Opus (should-fix) | P-5 binding clause has no regression | **CURED** — same cure as EXE-02, `01a94592`. |
| F2 | 151 Opus (nit) | ruled test name arrived by rename, not addition | **ACCEPTED, no action** — old body retained plus a new key-set assertion; no doc/CI reference to the old name (Opus grepped the checkout). |
| F3 | 151 Opus (nit) | two inert f-strings | **CURED** `01a94592` — `grep 'f"identity projection probe failed"\|f"runtime cleanup failed"' joulewise/identity_pins.py` → no match at head. |
| F4 | 151 Opus (nit) | cleanup-failure detail named an arbitrary config | **CURED** `01a94592` — the `finally` block now carries the comment "Cleanup is per unit, not per config: naming the last-visited realization path here would misdirect the reader" and the two cleanup refusals no longer append a config path. |
| F5 | 151 Opus (nit) | representative's realization bound twice (`workload_provenance` and `prompt_realizations`) | **ACCEPTED, benign** — verified again at head: `build_stack_identity` (`identity_pins.py:255-330`) reads only `model`/`tokenizer`/`sampler`/`output_policy`, so nothing reaches `realized_stack_identity`, `runtime_identity_sha256`, or any receipt field. Redundant payload inside the hashed input only; P-5's "no receipt fields added" holds. |
| F6 | 151 Opus (nit) | prepare/cleanup counts asserted only one level up | **CURED** `d7bf2ffa` — `:1507` drives the real `_runtime_probe_metadata` and counts prepare/cleanup/projection calls directly. |
| F7 | 151 Opus (nit) | comment cited "Ruling 44c P-2" | **CURED** `01a94592` — `identity_pins.py:1399` now reads `# Ruling 141a P-2:`. |
| — | 155 Sol fix2 | implementation report, `status: clean`, no findings | N/A. Its two tests re-verified independently by luna 157. |
| F1 | 157 luna delta (should-fix) | P-5 test covered derivation only; deleting the receipt's digest field left it green | **CURED** `ae7dd3d8` — `tests/test_identity_pins.py:1621-1632` freezes the pack and asserts `receipt["pack"]["projection_input_sha256"] == projection_input_sha256`. |
| F2 | 157 luna delta (should-fix) | EXE-01 test called `verify_frozen_projection` directly, bypassing the arm mapper | **CURED** `ae7dd3d8` — `tests/test_identity_pins.py:1486-1504` calls `arm_readiness._run_identity_arm_reverification` and asserts `reasons == ["readiness_identity_artifact_unreadable"]` plus `pseudo_receipt["status"] == "REFUSE"`. |
| (157 note) | 157 luna delta | a telemetry-only no-op survives the EXE-03 test | **ACCEPTED, out of contract** — luna's own words; P-3 governs the runtime lifecycle, not telemetry call counts. |

**Nothing is STILL OPEN without a ruling.** No BLOCKER arises from section B.

---

## C. Contract prose — grade: SHOULD-FIX (magistrate-owned)

`grep -rn "prompt_realizations\|projection_input_sha256\|token_ids_sha256" docs/contracts/`
returns **six hits, all in `docs/contracts/run_bundle_layout.md:401-439`, and none of them
about this mechanism**: they describe the *run-bundle* suite rollup
(`joulewise.suite_prompt_token_ids.v1`), a different artifact on a different path.
`prompt_realizations` and `projection_input_sha256` appear **nowhere** in `docs/contracts/`.

The branch introduces a new hashed evidence row (`probe_metadata.prompt_realizations`,
one object per expectation-bearing config) and a new check family
(`…:shared_mint_projection:prompt_realization`) and adds **zero** contract text.

Three findings, stated against Ed's writing standard:

1. **There is no `docs/contracts/` home for the identity-pin projection receipt at all.**
   This is PRE-EXISTING, not caused by this branch. The de facto home is
   `docs/decision_log.md` D-149 cl.1 (`:8400-8409`), which says
   `projection_input_sha256` "binds the closed declaration, config, model-file, and
   live-probe inventory rather than the final tree." The new rows land inside the
   live-probe inventory, so the existing sentence is not *falsified* by the branch — but
   it silently absorbs a new mechanism, which is exactly the failure mode of a word doing
   unpaid work. A reader of that clause cannot learn that a registered prompt is
   re-encoded, with which encoder, or what happens on drift.
2. **Replication test: FAILS.** From `docs/` alone a reader cannot rebuild the mechanism.
   Missing: that the catcher re-encodes `workload_profile.prompt_text` with the collection
   encoder at `add_special_tokens=True`; that the compared object is the triple
   `(token_count, token_ids_sha256, token_hash_domain)` under domain
   `joulewise.prompt_token_ids.v1`; that mismatch is
   `readiness_identity_environment_dirty` and unrealizability is
   `readiness_identity_artifact_unreadable`; the `check_id` shape; and a worked example
   with real numbers (e.g. a 4-token prompt, its digest, and the refusal message).
3. **First-use test:** "realization", "projection input", and "expectation-bearing" are
   terms of art with no gloss anywhere in `docs/`; they exist only in process traces and
   ruling text, which are not documentation.

**Grade: SHOULD-FIX, not BLOCKER.** No ruling required contract text: 141a P-9's
WRITE_SCOPE is exhaustive and lists four code/test files, explicitly reserving the
decision log and kernel to the magistrate — the implementer was *forbidden* to write it.
The obligation therefore sits with the magistrate, and the natural home is a D-149
amendment clause (or a new `docs/contracts/identity_pin_projection.md` that finally gives
the receipt a ONE home). Recommend it ride with the merge bookkeeping, not the PR branch.

---

## D. Test run and a novel mutant

### Suite (head, `ae7dd3d8`)

```
cd /Users/edr/code/JouleWise-wt-proj02-b
TMPDIR=<scratch>/opus159-tmp PYTHONDONTWRITEBYTECODE=1 \
  /Users/edr/code/JouleWise/.venv/bin/python -m unittest \
  tests.test_identity_pins tests.test_mlx_runtime tests.test_arm_readiness_integration
→ Ran 87 tests in 8.800s / OK (skipped=5) / exit 0
```

(The 5 skips are pre-existing `@unittest.skip` guards, unchanged by the diff.)

### Mutant M-159 — `"status": "PASS"` → `"OBSERVED"` at `joulewise/identity_pins.py:1557`

**Why this one, and why nobody ran it.** Every prior mutant attacked *what is
compared* (the triple, the per-config loop, the encoder flag) or *what is hashed*
(the binding). None attacked *what the emitted check says about itself*. P-5's
first sentence is "One **PASS** check per expectation-bearing config in the
existing four-key check envelope" — three of those four words are pinned
(`len == 2`, the `shared_mint_projection` substring, `expected == observed`, the
key set) and the fourth, the status literal, is not. It is the only ruled word in
P-1..P-10 with no assertion behind it. Method: `git archive ae7dd3d8` into scratch,
one-character-class edit, no other change (`diff` against
`git show ae7dd3d8:joulewise/identity_pins.py` → the single line 1557).

**Result: the suite does NOT kill it.**

```
cd <scratch>/opus159-tmp/m-status
TMPDIR=<scratch>/opus159-tmp PYTHONDONTWRITEBYTECODE=1 \
  /Users/edr/code/JouleWise/.venv/bin/python -m unittest \
  tests.test_identity_pins tests.test_mlx_runtime tests.test_arm_readiness_integration
→ Ran 87 tests in 8.552s / OK (skipped=5)   ← MUTANT SURVIVES
```

`tests/test_arm_readiness_evidence_t0.py:2690-2691` *does* carry
`all(check["status"] == "PASS" …)` — the tripwire ruling 141a P-5 names — but its
fixture is a legacy `synthetic/decode` pack with no `prompt_token_expectation`
(`grep prompt_expectation tests/test_arm_readiness_evidence_t0.py` → no match), so
the tripwire never sees a prompt-realization check and cannot bite. Executed to be
sure, against the same mutant tree:

```
python -m unittest tests.test_arm_readiness_evidence_t0
→ Ran 62 tests in 186.547s / OK (skipped=7)   ← the named P-5 tripwire also survives
```

Nothing in
`_derive_projection_units`' own validation constrains the value either:
`_require_exact_keys(check, CHECK_FIELDS, …)` (`identity_pins.py:721`) checks keys,
not values.

**CR-01 — SHOULD-FIX. Production consequence is real, not cosmetic.**
`"OBSERVED"` is outside `RECEIPT_STATUSES = frozenset({"PASS", "REFUSE"})`
(`joulewise/arm_readiness.py:269`). An expectation-bearing freeze receipt carrying it
would be rejected as `readiness_schema_invalid` at `arm_readiness.py:2195`, `:2311`,
`:2516`, and any check status other than `PASS` also appends
`readiness_ledger_preflight_refused` at `:7936`. So the failure mode this gap leaves
unguarded is: the FIRST real `_v5` freeze produces a receipt arm readiness cannot
consume — the P-8 throwaway rehearsal would surface it, at the cost of the rehearsal,
and a regression that reintroduced it later would reach a night. Consistent with
ruling 150a's framing, the cost is a wasted night, not a corrupted claim; hence
SHOULD-FIX, not BLOCKER.

**Cure (bench-sized, below the delegation threshold — 141a §9 "smaller than the
contract needed to delegate it"):** one line in
`test_projection_check_ids_carry_shared_mint_projection`
(`tests/test_identity_pins.py:1382`), beside the three assertions already there:

```python
self.assertTrue(all(check["status"] == "PASS" for check in receipt["checks"]))
```

Counterfactual input: M-159 above. Production call site: `identity_pins.py:1557`.
This mirrors the T0 tripwire's own assertion, so the two tripwires agree in shape.

### CR-02 — contract prose. See §C. SHOULD-FIX, magistrate-owned.

### CR-03 — observation, not a finding (worth the record)

`scientific_config_identity` (`identity_pins.py:217-236`) returns the whole typed
config minus `run_id` and volatile tags, so `workload_profile.prompt_token_expectation`
is INSIDE the single-scientific-identity invariant (`:1470-1476`). A unit mixing
expectation-bearing and legacy configs is therefore already refused as
`readiness_identity_environment_dirty` before the realization loop runs, and
`realization_configs` is always all-or-nothing. Consequences worth recording so a
later reader does not misread the code: (a) P-3's per-config loop is defence in depth,
not a reachable mixed case — the members of a `_v5` unit are scientifically identical
repetitions, so their realizations are identical by construction; (b) the
`representative_path` fallback at `identity_pins.py:1321-1329` (representative not in
`realization_configs`) is unreachable today; (c) a mutant that gates the filter on the
representative instead of per config is therefore semantically EQUIVALENT, which is
why I did not spend the mutant budget there.

---

## E. Process-record flag for the magistrate — same-signature repetition

Four seats each found exactly one instance of the SAME defect class:

- 151 Opus F1 — a ruled clause (P-5 binding) with no biting assertion;
- 149 terra EXE-02 — the same clause, found independently;
- 157 luna F1 — the ruled clause's cure covered derivation but not the frozen receipt;
- 159 CR-01 (this seat) — a ruled *word* in the same clause (`PASS`) with no assertion.

Per CLAUDE.local.md rule 11's STANDING ESCALATION TRIGGER, two consecutive rounds with
the same signature means "the next spend is a CONSULT, not round three." I am round
four on that signature. The consult's output is not another refuter: it is the
**clause → assertion map** that §A of this report already is. The structural cure is to
require that map as a deliverable of the implementation brief — every quoted phrase of
the ruling paired with the assertion that bites it, written BEFORE the refuter fan-out —
so that "ruled but unpinned" is caught by construction instead of one clause per seat.
Recommend the magistrate record this as a process finding at the apex pass; it is a
rule proposal, so by rule 11 the lieutenant may not adopt it alone.

---

## PR gate record (drop-in block, 38 lines)

```markdown
### Gate record — V5-PREFILL-REALIZED-PROJECTION-02 (D-118 full gate, 141a P-8)

Commits over `origin/main` @ `c5fa8a49`:
- `717b1ddb` Sol xhigh implementation (seat 145), rulings 141a P-1..P-10
- `01a94592` bench cure of Opus contract refuter 151 (F1 hash-binding test, F3/F4/F7 nits)
- `d7bf2ffa` Sol fix round 2 (seat 155) — terra 149 EXE-01 + EXE-03 regressions
- `ae7dd3d8` bench cure of luna delta re-audit 157 (F1 receipt digest, F2 arm mapper)

| Seat | Lens | Findings | Disposition |
|---|---|---|---|
| 149 terra (Sol) | execution / mutation | EXE-01, EXE-02, EXE-03 (all blocker) | all CURED — tests at `test_identity_pins.py:1422`, `:1569`, `:1507`; mutants executed dead (155 V2/V3, 157 V2–V4). Six ruled P-10 mutants killed (149 V1–V6). |
| 150 luna (Sol) | causality | F1 post-arm realization gap (blocker); `transformers_version` filter | F1 RULED OUT as blocker → ruling 150a R-150-1; filter RULED unchanged → R-150-4. |
| 151 Opus 5 | contract | F1 should-fix + F2–F7 nits | F1 CURED (`01a94592`); F3/F4/F7 CURED; F6 CURED (`d7bf2ffa`); F2/F5 accepted, no action. |
| 155 Sol | fix round 2 | none (report `clean`) | Both new tests independently re-verified by 157. |
| 157 luna (Sol) | delta re-audit | F1, F2 (should-fix) | Both CURED in `ae7dd3d8`. |
| 159 Opus 5 | contract + process record (near-final) | CR-01 should-fix; CR-02 should-fix; CR-03 note | CR-01 = P-5's `status: "PASS"` unpinned (mutant survives 87 tests) → 1-line bench cure; CR-02 = no contract prose for the new evidence row → magistrate-owned (P-9 barred the implementer from docs). |

**Written dissent (ruling 150a, R-150-1).** luna 150 labelled F1 — no realization
recheck between the arm receipt and collection — a BLOCKER. The magistrate
DOWNGRADED it to SHOULD-FIX because the gap is pre-existing and not specific to
prompt realization: `_replay_consumed_arm` replays the whole arm receipt, so every
identity unit has the identical post-arm window, and projection-02 neither opened
nor widened it. Follow-up row: **`V5-LAUNCH-REALIZATION-RECHECK-01`** (agent lane,
hard-start dependency: projection-02 merged), with luna's regression adopted
verbatim. Fence R-150-3: no `_v5` night may be armed for CLAIM use until that row
lands; rehearsal and DIAGNOSTIC_NO_PACK nights are unaffected.

**Tests at head** (`ae7dd3d8`, named modules only): `tests.test_identity_pins
tests.test_mlx_runtime tests.test_arm_readiness_integration` → 87 tests, OK
(skipped=5). Wider modules at the last source-changing commit: 183 tests OK
(157 V9), 219 tests OK (149 V7–V11).

**Open, post-merge, by ruling:** (1) 141a P-8 — magistrate freezes and arms a
THROWAWAY generated `_v5` pack against the real Qwen tokenizers before any night
uses it (no real model was loaded by any seat); (2) D-121 terminal review must be
re-run over `d7bf2ffa`+`ae7dd3d8`; (3) ruling 150a R-150-2 follow-up row.
```
