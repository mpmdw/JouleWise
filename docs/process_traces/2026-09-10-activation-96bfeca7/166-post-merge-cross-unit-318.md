# Post-merge cross-unit integration review — main @ ce041b78 (PR #318)

Gate row 11, second half. READ-ONLY. Nothing modified; no git write commands run.

## Provenance of this review

`/Users/edr/code/JouleWise-wt-bk-96bfeca7` HEAD is `3f03130b` and does **NOT**
contain `ce041b78` (`merge-base --is-ancestor` → false). The commit object IS
present in that worktree's object store after `git fetch -q origin`
(`origin/main` == `ce041b78`), so every file citation below is read with
`git show ce041b78:<path>` and every `file:line` is a line number **at
ce041b78**, not in the working tree.

For question 5 the three test modules could not be run from that worktree
(wrong tree state). They were run from a read-only `git archive ce041b78 | tar
-x` extraction into `/tmp/ce041b78-check` — the tree of the merge commit
exactly, with the repo untouched. See §5.

**Verdict: CLEAN on the code path. Two should-fix items, both documentation /
pointer defects outside the merged diff (§4 is the material one). Three nits.**

---

## 1. Desk writer ↔ capture writer non-divergence — CONFIRMED (with one bounded gap)

`scripts/write_derivation_night_inputs.py` imports, from
`scripts/validate_powermetrics_fiducial.py` (the capture writer):

| Symbol | Import site | Kind |
|---|---|---|
| `POWER_METRICS` | `scripts/write_derivation_night_inputs.py:75` (module level) | sampler path constant |
| `PROTOCOL_ID` | `:94` (deferred, inside `_derive_planned_vectors`) | epoch field `pulse_protocol_id` |
| `RESIDUAL_REGION_METHOD` | `:95` | epoch field `estimator_revision` |
| `SAMPLING_INTERVAL_MS` | `:96` | epoch field `sampling_interval_ms` |
| `_planned_t1_bindings` | `:97` | the whole T1 vector |
| `_sysctl_identity` | `:98` | epoch fields `os_build`, `hardware_model` |
| `_AcceptancePreflightError`, `_derive_preflight_systematic_screen_s` | `:156-159` | stale-field diagnostic |

and, from `scripts/generate_g2a_probe_inputs.py` (`:64-69`),
`IDENTITY_EPOCH_NAME`, `T1_BINDINGS_NAME`, `_json_bytes`, `_sha256_bytes` —
i.e. the canonical filenames and the canonical serialization
(`json.dumps(indent=2, sort_keys=True)` + trailing newline,
`scripts/generate_g2a_probe_inputs.py:193-198`).

**Same functions on both sides — confirmed.** The capture writer's own preflight
builds its `planned_epoch` at `scripts/validate_powermetrics_fiducial.py:1905-1913`
from the *identical* symbols (`_sysctl_identity("kern.osversion")`,
`_sysctl_identity("hw.model")`, `SAMPLING_INTERVAL_MS`, `RESIDUAL_REGION_METHOD`,
`PROTOCOL_ID`) and its `planned_t1` at `:2003-2007` from the same
`_planned_t1_bindings` (defined `:765-777`). The T1 vector is therefore
produced by one function on both sides; the epoch's four constant fields are
one-homed by import; only the two `sysctl` reads are re-spelled.

**T1 is byte-identical by construction**, since `_planned_t1_bindings` itself
supplies `anchor_method_version` (`ACTIVE_CAPTURE_ANCHOR_METHOD`) and
`protocol_sha256` (`sha256_path(PROTOCOL_PATH)`) — the desk script cannot
choose them.

**Sampler binary is the production path — confirmed.**
`scripts/write_derivation_night_inputs.py:75,77`:
`from scripts.validate_powermetrics_fiducial import POWER_METRICS` then
`SAMPLER_BINARY = Path(POWER_METRICS)`. That name is re-exported from
`joulewise/adapters/powermetrics.py:50`, `POWER_METRICS = "/usr/bin/powermetrics"`
(imported into the capture writer at `scripts/validate_powermetrics_fiducial.py:56-57`).
The capture writer's `--sampler-binary` **default is the same object**
(`scripts/validate_powermetrics_fiducial.py:1718-1720`,
`default=Path(POWER_METRICS)`). Pinned by a source-level test:
`tests/test_write_derivation_night_inputs.py:322-326`
(`assertEqual(script.SAMPLER_BINARY, Path(writer.POWER_METRICS))`), which is
what killed refuter 136's F1 survivor (the former literal `Path("/usr/bin/powermetrics")`).

### N1 (nit, fail-closed) — the six-field *composition* is duplicated, not shared

The dict literal that assembles the epoch exists twice:
`scripts/write_derivation_night_inputs.py:101-108` and
`scripts/validate_powermetrics_fiducial.py:1905-1913`. The one-home test
(`tests/test_write_derivation_night_inputs.py:268-297`) pins that the *helpers
and constants* are imported and that patching the writer's module attributes
reaches the desk script — it does **not** pin that the two compositions agree.
Key-set drift is caught anyway (`_refuse_incomplete_vector` at `:119-120,124-142`
checks both vectors against `joulewise.calibration_ledger.IDENTITY_EPOCH_FIELDS` /
`T1_FIELDS`, and the capture writer is checked against the same tuples). The
uncaught case is a *value-source* change in the capture writer alone — e.g.
`kern.osversion` → `kern.osproductversion`. That is **fail-closed, not silent**:
the reserved slot's copy is compared to the capture's live vector at
`joulewise/calibration_ledger.py:4607-4613`, refusing with
`FINALIZATION_BINDING_CONFLICT` (same comparison at `:1687` and `:5844`). Cost of
the defect is a burned settle, never a wrong number. Low.

### N2 (nit) — the stale-field diagnostic takes a shorter authentication path than the night

The desk script asks `_derive_preflight_systematic_screen_s(planned_epoch, …)`
(`scripts/write_derivation_night_inputs.py:162-164`), which raises
`acceptance_artifact_epoch_mismatch` at
`scripts/validate_powermetrics_fiducial.py:400-410` **before** the
`decimal_derivation` validation at `:411-434`. The night's `--derivation-only`
path instead calls `_derivation_only_screen_basis()` (`:497-537`), which passes
`None` and therefore *does* run that validation, then computes stale fields by
the same comparison (`:1929-1936` vs `:401-405`). Consequence: on a stale
machine the desk script can print a stale-field line for an acceptance whose
`decimal_derivation` is malformed, and the night would then refuse at d01 with
`acceptance_artifact_derivation_invalid`. The stale-field *list* is correct
either way; only the "the artifact is otherwise sound" implication is
unverified. Low, diagnostic-only.

### N3 (nit) — `--acceptance` can point somewhere the night will not look

`--acceptance` (`:279-290`) defaults to `DEFAULT_ACCEPTANCE_BOUND_PATH`
(= `ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH`, `joulewise/calibration_bracketing.py:178`),
which is what `_derivation_only_screen_basis()` also reads when the night runs
(`scripts/validate_powermetrics_fiducial.py:513-517`, called with no
`acceptance_path` from `:1918`). A non-default `--acceptance` therefore makes the
desk diagnostic and the night's d01 judge different artifacts. Operator-only,
default-safe. Low.

---

## 2. Filenames: writer ↔ generator ↔ runbook — CONSISTENT

Canonical constants, the single home:
`scripts/generate_g2a_probe_inputs.py:71-72` —
`IDENTITY_EPOCH_NAME = "identity-epoch.json"`, `T1_BINDINGS_NAME = "t1-bindings.json"`.

* **Writer writes them**: `scripts/write_derivation_night_inputs.py:225-226`
  (`out_dir / IDENTITY_EPOCH_NAME`, `out_dir / T1_BINDINGS_NAME`) — by import,
  no literal.
* **Generator**: `scripts/gen_derivation_night.py` accepts arbitrary paths
  (`:840-841`), so it *expects* nothing by name; what it teaches is its example
  and its rendered region — `:651,653` and `:764-765`, both hyphenated at this
  merge (they were the underscore spelling before; see the merge diff).
* **Runbook revision 5** (`docs/phase_2/derivation_night_runbook.md`) is
  hyphenated everywhere the operator pastes: `:41`, `:586-587`, `:651-652`
  (the paste lines), `:868-869`, `:939-940`, `:1213-1214`, `:1959`. It also
  explicitly warns at `:1770` that "An underscore-spelled `identity_epoch.json`
  is a different file and reads as missing" — intentional, keep.
* Already-hyphenated adjacent surfaces: `docs/phase_2/window_runbook.md:206-207`,
  `scripts/ed_session/build_rehearsal_env.sh:46-47`,
  `docs/process_traces/2026-08-28-live-smoke/RUNSHEET.md:294-295,554-555`, and
  `SHAKEDOWN-G2-RUNSHEET.md:1700-1701,1776-1777` (fixed in this merge).

### Remaining underscore spellings at ce041b78 — complete list

| Site | Classification |
|---|---|
| `tests/test_gen_derivation_night.py:144,147,190-191,296-297,662-663,684-685,931,957` | **Nit (N4).** The suite's own fixtures are named `identity_epoch.json` / `t1_bindings.json`. Harmless (the generator takes paths), but the tests would not catch a regression of the hyphenation and the test corpus now teaches the spelling the runbook calls a trap. |
| `joulewise/arm_readiness.py:8092-8093` | **Nit (N5).** The synthetic rehearsal dry-run root writes underscore names and passes those exact paths into its own argv — internally self-consistent, never operator-facing, no real night reads them. |
| `docs/phase_2/derivation_night_runbook.md:1770` | Intentional — it is the warning itself. Fine. |
| `docs/process_traces/2026-09-10-activation-96bfeca7/{99,103,104,108,115,135}-*.md` | Historical trace records (drafts and the reports that found the defect). Fine. |

No underscore/hyphen mismatch remains on any **operative** path in `scripts/`
or `docs/phase_2/`.

---

## 3. Issuer corpus-floor one-home — CONFIRMED

* Validator constant: `joulewise/calibration_bracketing.py:256`,
  `ENVELOPE_MINIMUM_CORPUS_N = 17`, documented `:248-255` (ratified floor is 19;
  the n=17 anchor-v3 arc is the only ruled departure; guards `df = n-1`).
  Enforced at `:486-487` for `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` rows only.
* Issuer import: `scripts/issue_calibration_acceptance_generation.py:86`
  (`ENVELOPE_MINIMUM_CORPUS_N` in the `calibration_bracketing` import block),
  binding at `:379`, `RULED_ALTERNATIVE_CORPUS_SIZE = ENVELOPE_MINIMUM_CORPUS_N`.
* **Every use reads the imported name** — `:1157`, `:1161`, `:1784`, `:1792`.
  Those are all four occurrences; `grep RULED_ALTERNATIVE_CORPUS_SIZE` returns
  nothing else. No residual literal in any code path.
* Tied by test: `tests/test_issue_calibration_acceptance_generation.py`
  (`test_the_ruled_alternative_floor_has_one_home`, added in this merge) asserts
  equality **and** greps the issuer source for the import form and against
  `RULED_ALTERNATIVE_CORPUS_SIZE = 17`.

### Which literal `17` is which

Four literal `17`s remain in the issuer, **all in prose, none executable**:
`:58` (module docstring: "19, or 17 with…"), `:1152` and `:1154` (the comment
explaining the ruling), `:1782` (a help/refusal string: "a 17-member corpus").
These carry the *ruled-alternative floor* meaning, i.e. the same number the
constant now owns — they are restatements in human-readable text, so a future
change to `ENVELOPE_MINIMUM_CORPUS_N` would leave them lying. That is a
documentation-drift nit (**N6**), not a second code home; the tying test above
only guards the assignment line.

Separately, `17` appears with the **other** meaning as the r6 corpus size — the
active acceptance is `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`,
`acceptance_id = d079_calibration_acceptance_v2_n17_r6`
(`DEFAULT_ACCEPTANCE_BOUND_PATH`, `joulewise/calibration_bracketing.py:178`), and it
is quoted in the runbook's §0.8 paste example
(`docs/phase_2/derivation_night_runbook.md:651`). Historically these are the
same number for a reason — the floor was *derived from* the n=17 r6 arc
(`joulewise/calibration_bracketing.py:249-251`) — but they are two different
facts and only one of them is `ENVELOPE_MINIMUM_CORPUS_N`.

---

## 4. Pointers to the old trace draft `99-derivation-night-runbook-draft.md`

Exhaustive sweep over tracked `*.md` / `*.json` / `*.py` / `*.sh` / `*.zsh` at
ce041b78, excluding this activation's own trace directory (where such mentions
are by definition historical):

| Site | Text | Classification |
|---|---|---|
| `RUN_STATE.md:13` | "Start with … the derivation-night runbook draft **[99](docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md)**" | **STALE OPERATIVE POINTER (should fix).** This is the start-here list; it sends the next activation to the superseded draft, not to `docs/phase_2/derivation_night_runbook.md`. |
| `RUN_STATE.md:15` | "NEXT EXACT ACTION: … then the derivation-night arm **per runbook 99 rev 3** … produce identity-epoch and T1-bindings JSON at the desk (**the G2-a input generator writes both** — see record 134)" | **STALE OPERATIVE POINTER (should fix) — the material one.** Two defects in one clause: it names the draft as the operative runbook, and it names the *wrong tool*. Record 134 itself concluded the G2-a generator "cannot serve a derivation night (it authenticates the acceptance's epoch, which is exactly what is stale)"; PR #318 exists because of that. The correct instruction is `scripts/write_derivation_night_inputs.py` per runbook §0.8. |
| `docs/process/state_kernel.json:41` (A179 `status_note`) | "runbook record 99 rev 3; wrapper via `scripts/gen_derivation_night.py`" | **Stale operative pointer (should fix).** This is the ONE home; `TASK_QUEUE.md:793` and `:964` are its generated mirrors and will follow automatically. |
| `TASK_QUEUE.md:793`, `TASK_QUEUE.md:964` | same sentence, A179 | Generated mirror of kernel `:41` — do not hand-edit; fixed by fixing the kernel row. |
| `docs/process/state_kernel.json:5256` + `TASK_QUEUE.md:796,967` (A184) | "inert today (runbook 99 does not route through the subcommand)" | **Historical mention (fine).** A dated observation about the lane's state on 09-10, not an instruction to read the draft. Could be reworded at leisure. |
| `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md:955` | UPDATE ~19:50: "arm materials … per runbook 99 rev 3 (identity-epoch + T1-bindings JSON provenance is the open `[UNVERIFIED]`…)" | **Historical mention (fine, superseded in file).** The later UPDATE at `:958-965` (~20:55) names `docs/phase_2/derivation_night_runbook.md` revision 5 and the desk writer; DURABLE-STATE is append-only, so the last UPDATE governs. Worth one line in the next UPDATE saying §0.8's `[UNVERIFIED]` is closed. |
| `README.md` | no mention of either runbook | Fine — README's blurb is prose-level. |
| `AGENTS.md`, `MAGISTRATE_WATCHDOG.md`, `PROJECT_STATUS.md` | no hits | Fine. |

**Zero operative surfaces currently point at the tracked runbook.** Outside
its own text, `docs/phase_2/derivation_night_runbook.md` is referenced only
from trace records (`00-DURABLE-STATE.md:962` and this activation's records
101/133/137/139/141/142/144). The next bookkeeping commit should make
RUN_STATE and the A179 kernel row name the tracked file and the desk writer.

Related, same shape: the runbook's own changelog says §0.8's `[UNVERIFIED]` is
closed (`:37-38`) and that two `[UNVERIFIED]` blocks remain in substance
(`:56`) — verified: seven `UNVERIFIED` strings total, five of them changelog/
preamble prose (`:7,37,39,53,56`), two real open blocks at `:1150` (the 06:05
last-start cutoff) and `:1820` (the full refusal list). Consistent with the
merge message; nothing stale there.

---

## 5. Test run — PASS

Could not be run from `/Users/edr/code/JouleWise-wt-bk-96bfeca7` (HEAD
`3f03130b` does not contain `ce041b78`, and creating/advancing a worktree is a
git write). Run instead from a `git archive ce041b78` extraction at
`/tmp/ce041b78-check`, which is the merge tree byte-for-byte:

```
$ cd /tmp/ce041b78-check
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_write_derivation_night_inputs \
    tests.test_gen_derivation_night \
    tests.test_docs_freshness 2>&1 | tail -3

Ran 86 tests in 25.515s

OK
```

System `python3`, no MLX present — the desk-writer suite is MLX-free by
construction (`tests/test_write_derivation_night_inputs.py:8`, every machine
read mocked), and `test_docs_freshness` passed without a `.git` directory.

---

## Findings summary

**Blockers: none.**

**Should-fix (both documentation, both outside the merged diff):**

* **S1 — `RUN_STATE.md:15` names the wrong desk tool.** "the G2-a input
  generator writes both" is false for a derivation night and contradicts the
  merged runbook §0.8 and record 134. An operator following RUN_STATE would
  reach for `scripts/generate_g2a_probe_inputs.py`, whose acceptance-epoch
  authentication is exactly what is stale. Replace with
  `scripts/write_derivation_night_inputs.py`.
* **S2 — the operative runbook pointer is still the trace draft.**
  `RUN_STATE.md:13`, `RUN_STATE.md:15`, and `docs/process/state_kernel.json:41`
  (mirrored to `TASK_QUEUE.md:793,964`) say "runbook 99 rev 3"; the tracked
  operator document is `docs/phase_2/derivation_night_runbook.md` revision 5.

**Nits:** N1 duplicated epoch composition (fail-closed via
`FINALIZATION_BINDING_CONFLICT`); N2 desk stale-field diagnostic skips the
`decimal_derivation` check the night performs; N3 `--acceptance` override can
diverge from the night's fixed default; N4 `tests/test_gen_derivation_night.py`
fixtures use the underscore spelling; N5 `joulewise/arm_readiness.py:8092-8093`
synthetic seam likewise; N6 four prose `17`s in the issuer restate the now
one-homed floor.

The merged units themselves — desk writer, issuer import, generator example
filenames, runbook revision 5 — are mutually consistent and test-pinned.
