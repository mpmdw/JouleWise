# Cold-gate ruling 10 — GENERATOR-HEAD-FILE-BYTE-PIN-01 (kernel 244)

Judge: cold Fable 5.1 seat, worktree `JouleWise-wt-coldgate2-d0b83820` @ `a5905f67`, 2026-09-19 09:28–09:3x PDT. Foreground only; no subagents; nothing armed; no tracked file touched except this one.

**Disclosure.** Auto-loaded: `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md`, and the memory index `MEMORY.md` (index lines only). Not read: `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any narrative state doc.

**Trust anchors.** Validator run 1 with the deliberately mistyped charter sha (`…a880ff…`) → `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2. Run 2 with `099de884…a870ff…` → `PASS`, rc 0, packet `a06be7dc…`, all five exhibit digests observed = expected. Judged on that basis.

## Executed probes (all read-only, `git show 2f79e633:` unless stated)

1. `configs/calibration/calibration_ledger_head.json` = `{sequence 176, head_digest 0f7609ae…, schema …v1}`.
2. Both acceptances the v5 generator can bind (`calibration_acceptance_d079_v2.json` n19 and `…_n17_r6.json`) carry `ledger_cutoff = {76, 08456d50…, …v1}`; equals `LEDGER_HEAD_SHA256`.
3. `d117_floor_qwen3-1p7b_v5/generate_configs.py` lines 2503–2511: drift tuple of four `(path, sha)` pairs including `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)`; lines 2886–2890 emit `issued_ledger_head{path,file_sha256,head_sha256}`; line 1625 passes `--head-pin repo_path(LEDGER_HEAD_REL)` at RUN time. Pack bytes never depend on head-file bytes; only the constant is echoed.
4. `git grep issued_ledger_head 2f79e633 -- joulewise scripts tests` → empty. `git grep LEDGER_HEAD_FILE_SHA256 … -- tests scripts` → empty. No consumer of `file_sha256`.
5. `joulewise/calibration_ledger.py` 2609–2632: run-time loader refuses `physical < pinned` (`calibration_ledger_rollback`), and `baseline_sequence > pinned_sequence` or digest-not-in-chain (`calibration_ledger_baseline_missing`). `calibration_bracketing.py` 2020–2027 feeds the acceptance cutoff as that baseline. D-109 R1.4 anti-rollback is enforced at load time independent of any generator constant.
6. Correction to the packet's "three live v5 generators": `d117_contrast_v5` has NO byte pin on the head file (its only reference is the run-time `--head-pin` argv, line 2134). Exactly TWO live generators byte-pin: `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`. The other three `LEDGER_HEAD_FILE_SHA256` declarers are frozen `qwen25_1p5b_v1/v2/v3`; `qwen25_7b_v1/v2/v3` pin the same bytes through their `external input drift` map (line 596/599).
7. Frozen custody binds generator source: `d117_floor_qwen25_1p5b_v2/plan_tree.json` line 966–969 `"generator": {path, sha256 f55955c5…}`. Editing any frozen generator changes a custody-bound digest.
8. v5 pack dirs at main hold only `generate_configs.py` (contrast_v5 adds two D-166 JSONs): no committed pack tree, so editing the two live generators invalidates no custody.
9. Test run (allowed single module), refc worktree at `ff788ef7` (NOTE: one commit behind the packet's round-1 head `d3c8b355`; the N1 `head_mock` assertion is absent there): `tests.test_campaign_generator_core` → 7 tests OK, 3.8 s.

## Q1 — RULED: (a), amended by probe 6

Adopt B1 for the two live floor v5 generators that byte-pin the head file. `d117_contrast_v5` already conforms (no change). The nine frozen generators keep their byte pin and echo/preserve mode untouched: (b) fails burden (iii) because probe 7 shows frozen generator source digests are custody-bound in committed `plan_tree.json`; (c) fails burden (iv) by construction (every advance re-breaks the two live generators and their tests, one reviewed constant per night forever, on a file the append contract licenses to advance nightly; Exhibit B `advance-head-pin`). R1.4's "checked-in byte-pin trust model" describes the committed pin file as the trust anchor against the physical ledger; it never licenses a generator to freeze that file's bytes. Deciding exhibits: B (the contract advances the pin) + probe 5 (anti-rollback lives in the loader, not the constant) + probe 4 (the dropped field has no consumer).

**Exact code shape (both live floor v5 generators, identical edit):**

1. Delete the constant `LEDGER_HEAD_FILE_SHA256` (lines 211–213). Keep `LEDGER_HEAD_REL` and `LEDGER_HEAD_SHA256`.
2. Drift tuple (2503–2511): remove the row `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)`; the other three rows and the message `pinned input drifted: {path}` stay verbatim.
3. Immediately AFTER that loop (so the acceptance bytes are already verified) add and call:

```python
def verify_ledger_head_pin() -> dict[str, Any]:
    """D-109 R1.4: the committed head pin must be at-or-ahead-of this pack's acceptance cutoff."""
    pin_rel = LEDGER_HEAD_REL
    pin = json.loads((REPO_ROOT / pin_rel).read_text(encoding="utf-8"))
    cutoff = json.loads(
        (REPO_ROOT / acceptance_pin()["rel"]).read_text(encoding="utf-8")
    )["ledger_cutoff"]
    if cutoff["head_digest"] != LEDGER_HEAD_SHA256:
        raise ValueError(
            f"acceptance ledger cutoff drifted: {acceptance_pin()['rel'].as_posix()}"
        )
    if pin.get("ledger_schema") != cutoff["ledger_schema"]:
        raise ValueError(f"ledger head pin schema mismatch: {pin_rel.as_posix()}")
    sequence = pin.get("sequence")
    if (
        isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence < cutoff["sequence"]
    ):
        raise ValueError(
            f"ledger head pin behind the acceptance cutoff: {pin_rel.as_posix()}"
        )
    if sequence == cutoff["sequence"] and pin.get("head_digest") != cutoff["head_digest"]:
        raise ValueError(
            f"ledger head pin diverged from the acceptance cutoff: {pin_rel.as_posix()}"
        )
    return pin
```

   The returned `pin` is NOT written into any emitted byte (burden iv: pack bytes stay independent of the advancing pin).
4. Manifest (2886–2890): emit `"issued_ledger_head": {"path": LEDGER_HEAD_REL.as_posix(), "head_sha256": LEDGER_HEAD_SHA256}`. Do not add `sequence` or the live pin digest.
5. Preserve mode: untouched (the check reads `acceptance_pin()` so it binds n19 in preserve mode and r6 in successor mode; both cutoffs are 76/`08456d50…`, probe 2).

**Schema question.** Removing `file_sha256` is a manifest-field change with zero in-repo consumers (probe 4: `joulewise/`, `scripts/`, `tests/` empty). No consumer sweep beyond re-running that grep in the seat's landing record. The frozen packs' committed manifests keep their `file_sha256` (they are not regenerated), so no committed byte changes.

## Q2 — code change conforming to the contract; land AFTER PR #361

Not a contract amendment: no text in D-109 R1 or `calibration_ledger_append.md` §head pin changes; B1 conforms the two live generators to R1.4 (prefix relation, loader-enforced) and to the append contract's licensed advancement. It drops one generator-side mechanism, which is why it sits at this gate (rule 11), and this gate rules it dropped.

Sequence: AFTER #361 merges. #361 is test-only and restores CI; B1 is production and needs its own review lens on two generators. Landing B1 first would couple a red-CI repair to a production change.

Fixture disposition in the B1 lane (same PR):
- `tests/test_campaign_generator_core.py` ALPHA/BETA head fixture (Exhibit E) → REMOVE. Once B1 lands, that fixture would hide the semantic check from the only end-to-end run of the live generators. Its N1 "fixture fired" assertion goes with it.
- `tests/test_d117_floor_qwen3_v5_generate.py::generation_repository` → KEEP the clone and the working-tree generator copy (F1 grading), DROP the `calibration_ledger_head.json` byte write so the live generators run against the real committed pin.
- The five remaining modules' fixtures for FROZEN successor paths (`test_d117_v3_family`, `…qwen25_*_plan`, `test_d117_decode_contrast_plan`, `test_arm_readiness_registry` if it drives a frozen generator) → STAY permanently: a frozen generator is a frozen function of its declared inputs, and the fixture is the proof.

## Q3 — regressions the suite must prove after B1

Each against the two live floor v5 generators, in a disposable clone with a rewritten head-pin file:
1. Pin advanced past cutoff (e.g. `sequence 176`, any digest, schema v1) → `generate` succeeds; emitted tree byte-identical to a generate at `sequence 76`/cutoff digest (proves burden iv).
2. Pin rolled back below cutoff (`sequence 75`) → refuses `ledger head pin behind the acceptance cutoff: configs/calibration/calibration_ledger_head.json`, and no output byte written (write boundary untouched).
3. Pin `ledger_schema` altered → refuses `ledger head pin schema mismatch: …`.
4. Pin at the cutoff sequence with a different digest → refuses `ledger head pin diverged from the acceptance cutoff: …`.
5. `sequence` given as `true` or `"176"` → refuses as (2) (bool/str guard).
6. Acceptance bytes mutated (newline) → still `pinned input drifted: <acceptance path>` and still raised BEFORE the head check (loop order).
7. Emitted `issued_ledger_head` == `{path, head_sha256}` exactly; no `file_sha256` key; `head_sha256 == cutoff.head_digest`.
8. Preserve/echo mode on every frozen generator unchanged (existing tests, with their fixtures).
9. `--check` subprocess path (v5 generate test) passes with the real committed pin, no fixture.

Obsolete after B1: the ALPHA/BETA head fixture and `GENERATION_LEDGER_HEAD_*` constants' use for LIVE generators in `test_campaign_generator_core.py` (constants may stay if the frozen-path modules import them); the head-bytes write in `generation_repository`; any assertion that `issued_ledger_head` carries `file_sha256`. The bracketing prefix test and the anti-rollback loader regressions from #361 stay.

## Not executed

None of the packet's probes were skipped. Caveat only: the allowed test run was on `ff788ef7`, not the round-1 head `d3c8b355` the packet names, because that is what the refc worktree holds; the N1 assertion was therefore not exercised by this seat.
