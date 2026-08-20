# ROW L5-PACK-READINESS-CUSTODY — pack / readiness / custody (GATING)
Original verdict: NOT-READY (0 blockers / 3 should-fix / 2 nits / coverage 16/18)
Not flagged UNVERIFIED on coverage at the sitting (only L2 was) — but the council ruled the
work-order program **NOT CERTIFIED COMPLETE** because every seat's universe was self-nominated
(`council-verdict.md` §VERDICT ¶3). See the COVERAGE sub-row.

**Assembly conditions.** Verified in the read-only worktree `wtS0`, branch
`impl/r2-s0-mint-resolver`, at HEAD **`b92b43d`** (the brief pinned `d10881b`; the branch advanced
twice during assembly). `main` = `origin/main` = `0099382`; 51 commits on HEAD not on main.
Executed probes below ran in throwaway clones under the scratchpad
(`scratchpad/cleanclone` @ `b92b43d`, `scratchpad/baselineclone` @ `ac3fe1d`), never in `wtS0`;
both clones were `git status --porcelain`-clean at exit and have since been deleted (every probe
below is reproducible with `git clone --shared --no-checkout <repo> <dst> && git checkout <sha>`).
The branch kept advancing while this row was written (observed `7305e0d` at file-write time).

---

## L5-F-1 (should_fix) — Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; CI-green status unexplained

### (a) Original finding (VERBATIM)
> - [should_fix] [L5] Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; CI-green status unexplained

Seat-report text (VERBATIM, `seat-reports/L5-PACK-READINESS-CUSTODY-report.md` §4 F-1):
> **F-1 SHOULD-FIX — Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; their CI-green status is unexplained.** `tests/test_d117_floor_qwen25_1p5b_plan.py:30-35` exec-imports the pack generator at module import, which writes `__pycache__/generate_configs.*.pyc` **into the frozen pack**; the inventory test (`:259-264`, unfiltered rglob) then fails. Reproduced from a byte-clean tree on python3.13 **and CI's python3.11**; same pattern in the 7B test; the contrast test already carries the fix (`test_d117_decode_contrast_plan.py:59-65`, commit `e286e75` — "passed fresh and failed every rerun"). Failure scenario: (a) the plan-test literal pin is the principal automated catch for committed plan_tree drift (F6) — if CI is red or red-masked on these modules, that catch layer is not real; (b) running these tests in the measurement checkout leaves `__pycache__` in the frozen pack, after which **every** `committed_pack_tree_sha256` caller (t0 author, arm, consume) refuses "untracked pack directory" until manual cleanup — an arm-night tripwire (refusal executed live). Fail-closed, but a falsely-green integrity test is exactly the charter's anti-ritual target.

Citation: `sitting-packet-FINAL.md` §4 (should-fix titles); seat report §4 F-1, §3 falsifier F6,
§1 universe row U17, §5 unexecuted obligation 1. No refuter was assigned to L5 (0 blockers), so
this finding carries **no refuter verdict** — it is single-lens by construction.
Post-verdict adjudication: none; folded into the council's Phase-1 should-fix batch.

### (b) What changed since 2026-08-15

**Repairs (all merged to main).**
- `c94e0b0` "Post-merge integration round 2: freeze-transaction-shaped registry fixture + **in-pack
  bytecode cure**" — adds the import-time guard now at
  `tests/test_d117_floor_qwen25_1p5b_plan.py:40-47`:
  ```
  # Loading a pack generator by file location writes __pycache__ INTO the
  # tracked v1 pack, where sibling arm-readiness fixtures then copy it as a
  # pack file and fail on a build byproduct. Suppress the cache write for
  # this one load and restore the interpreter default.
  _PREVIOUS_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
  sys.dont_write_bytecode = True
  ```
  WHERE it lives: **merged to main**.
- Defence in depth: the inventory rglobs now filter `__pycache__` at
  `tests/test_d117_floor_qwen25_1p5b_plan.py:147, 312, 415, 470, 1605` (`checkout_inventory` and
  `test_exact_inventory_and_content_hashes`).
- `d3aa15f` "D-117 plan tests: make the successor-generation contract freeze-independent"
  (2026-08-18) — a **different** clean-tree failure in the same modules
  (`test_successor_generation_threads_plan_identity_and_lineage` failed once the `_v2` family was
  committed and frozen). WHERE it lives: **merged to main**.
- `235c5ea` "…plan-test fixture loops skip committed successor artifacts (the round-4 boundary
  refuses symlinked write targets — each test generates its own successors)". **merged to main**.

**Executed delta evidence (this assembler).**

| head | interpreter | module | result |
|---|---|---|---|
| `ac3fe1d` (audit baseline) | 3.13.1 | `tests.test_d117_floor_qwen25_1p5b_plan` | **FAILED (failures=1)**, 18 tests — `AssertionError: Items in the first set but not the second: '__pycache__/generate_configs.cpython-313.pyc'` at `test_exact_inventory_and_content_hashes` |
| `ac3fe1d` | 3.13.1 | same, **2nd run** | **FAILED** again; pack polluted: `configs/campaigns/d117_floor_qwen25_1p5b_v1/__pycache__/generate_configs.cpython-313.pyc` present |
| `b92b43d` (current) | 3.13.1 | `…1p5b_plan` | **OK**, 21 tests, 5.6 s |
| `b92b43d` | 3.13.1 | `…7b_plan` | **OK**, 20 tests |
| `b92b43d` | 3.13.1 | `…decode_contrast_plan` | **OK**, 22 tests, 44.8 s |
| `b92b43d` | 3.13.1 | `…1p5b_plan` **re-run** | **OK** (the "failed every rerun" symptom is gone) |
| `b92b43d` | **3.11** (`/opt/homebrew/bin/python3.11`, CI's supported floor) | `…1p5b_plan` | **OK**, 21 tests |
| `b92b43d` | **3.11** | `…7b_plan` | **OK**, 20 tests |

After all runs at `b92b43d`, no `__pycache__` directory exists in any pack and
`git status --porcelain` is empty. The seat's reproduction is therefore confirmed **at the audit
baseline** and the repair is confirmed **at the current head on both interpreters**.

**What is NOT closed: the "CI-green status unexplained" half.** Mechanically checked offline in
both clones using CI's own sharding code (`scripts/shard_tests.py`, `.github/workflows/ci.yml:38-63`):
- At `ac3fe1d`: all three modules are discovered, none is in `exclusive_modules`
  (`{tests.test_calibration_exits, tests.test_calibration_writer_crash_matrix}`), and
  `partition_modules` places `…1p5b_plan` in **shard 3** and `…7b_plan`/`…decode_contrast_plan` in
  **shard 4**. CI sets no `PYTHONDONTWRITEBYTECODE`.
- At `b92b43d`: `…1p5b_plan` → shard 2; `…7b_plan` + `…decode_contrast_plan` → shard 3.
So at the baseline head CI *did* schedule a module that fails deterministically from a clean tree.
Why the merge was recorded green is still unexplained; resolving it needs the Actions log
(no network in this environment).

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED on the defect; STILL-OPEN on the CI-truth question.** The code defect is
executed-proven cured on main across both interpreters, with the baseline failure reproduced for
contrast. What the seat is adjudicating is the finding's second clause: whether an integrity catch
layer whose CI history was demonstrably capable of being green-while-broken can be trusted without
pulling the actual run logs — the council named this L5's highest-value follow-up.

### (d) Skeptical probes
1. Pull the Actions log for PR **#149** (`ac3fe1d`) and read the shard-3/shard-4 jobs on 3.11 and 3.14. Did `tests.test_d117_floor_qwen25_1p5b_plan` run, and did it pass? If it passed, the local deterministic failure needs an explanation before the catch layer is trusted.
2. Re-run the assembler's baseline reproduction independently: clone at `ac3fe1d`, `python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan`. Confirm the `__pycache__` assertion and that `git status` stays clean (the pollution is gitignored — invisible to git, visible to `rglob` and to `committed_pack_tree_sha256`'s untracked-directory refusal).
3. Run the three plan modules at the sitting head on 3.11 and 3.14 in a byte-clean clone, twice each, then `find configs/campaigns -name __pycache__`. Any hit reopens the arm-night tripwire.
4. `sys.dont_write_bytecode` is suppressed only around **one** `exec_module` call. Grep every test module that exec-imports a pack generator (`grep -rn "exec_module" tests/`) — is any other loader unguarded, including the new `_v3`-family tests added by `1d3873b`?
5. The `__pycache__` filters in the inventory tests weaken the very assertion that catches stray pack files (`readiness_pack_not_committed`). Prove the filter cannot mask a real untracked artifact: add a stray non-`__pycache__` file in a scratch copy and confirm the inventory test still fails.

---

## L5-F-2 (should_fix) — Generator `--check` echo hole in preserve mode

### (a) Original finding (VERBATIM)
> - [should_fix] [L5] Generator --check echo hole in preserve mode: plan_tree.json, plan_tree.sha256, producer_contract.json are compared against themselves

Seat-report text (VERBATIM, §4 F-2):
> **F-2 SHOULD-FIX — Preserve-mode `--check` echo hole.** In the current frozen state, all three generators **echo** `plan_tree.json`, `plan_tree.sha256`, and `producer_contract.json` from disk into the "generated" output (`d117_floor_qwen25_1p5b_v1/generate_configs.py:1803-1813,1987-1998`; 7B `:2185-2193`; contrast `:1683-1697`), so `--check` compares those files with themselves and reports "verified" (F6 executed: tampered sha printed as verified). The D-134 freeze receipt binds calibration_plan + registry + evidence but **not plan_tree bytes** — plan_tree is the in-pack authority root whose cross-commit integrity currently rests only on the plan-test literal (see F-1), the off-repo baseline manifest, and merge review. Work order: bind a plan_tree digest at freeze (attachment-excluded hash in the freeze or projection receipt) or restore genuine regeneration for these members.

Citation: `sitting-packet-FINAL.md` §4; seat report §4 F-2, §3 falsifier F6 (the executed echo),
§7 work order WO-L5-2.

### (b) What changed since 2026-08-15

**Generator work landed (all merged to main), but it changed the SEMANTICS, not the self-comparison.**
- `b6b5e6d` "Round 4: symlink-safe closed write inventory (refuse-before-any-write on resolved
  ancestors/targets) + authenticated freeze-transition regression (genuine on-disk receipts;
  preservation flag can never flip status)".
- `7402855` "Terminating dual-generation fix (consult-adopted): target identity drives every
  path/semantic/status emission; **preservation is custody replay only**".
- `5292cf7` "Round 6: freeze-neutral successor wording, dead frozen-emission branches removed,
  C1 inverted freeze regression (cold-gate verdict 2026-08-18)".
- Ruling: `docs/decision_log.md:174` **D-141** "GENERATOR WRITE-BOUNDARY + FREEZE-LOADER REGISTERED
  RESIDUALS (cold gate 2026-08-18 ratification + delta-8 ratification)": the symlink-substitution
  boundary is a **registered residual** (`docs/risk_register.md` R-019, line 39/366); the
  `_load_freeze_reference` v1-schema acceptance inside a `_v2` pack is R-020 (line 40/390).
  WHERE they live: **merged to main** (trace `3f9d759`).

**The echo hole itself persists — read at HEAD.** `configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py`:
```
def _generate(output_root: Path) -> tuple[int, str, str]:
    outputs = validate_generation_output_inventory(active_generation())
    validate_generation_write_boundary(output_root, outputs)
    if active_generation().preserve_current_frozen_bytes:
        for relative in sorted(outputs, key=lambda path: path.as_posix()):
            write_bytes(output_root, relative, (REPO_ROOT / relative).read_bytes())
```
and `check_current` (`:2556-2563`) generates into a `TemporaryDirectory` and then compares against
`check_root`. So in preserve mode **every** output file — not just the three named — is copied from
the checkout and compared with itself. The hole is now wider in scope, and is the *only* mode in
which a frozen successor pack can be `--check`ed at all (see F-4 below).

**The alternative remedy ("bind a plan_tree digest at freeze") did NOT land.** Read
`configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`:
`pack_identity` = `{pack_id, pack_root, plan_id, plan_path: "calibration_plan.json",
plan_sha256: 9ab4776f…, window_id}` — the string `plan_tree` does not appear anywhere in the
receipt. What IS new is `predecessor.pack_sha256 = 95f7c51c…`
(`pack_digest_algorithm joulewise.committed_pack_tree_sha256.v1`), i.e. the receipt binds the
**predecessor's whole committed tree**, transitively covering the `_v2` plan_tree — but not its own.
WHERE freeze-0003 lives: **branch-only** (`5e38f1e`, `eb7f6c6`, `94dc3b3`).

### (c) Candidate disposition for the seat
**STILL-OPEN.** Neither of the finding's two named remedies executed: `--check` still compares
preserve-mode outputs against themselves, and the freeze receipt still does not bind `plan_tree`
bytes. The seat is adjudicating whether the new `predecessor.pack_sha256` chain binding plus the
repaired plan-test literal (F-1) constitute an equivalent catch layer, or whether the in-pack
authority root remains unbound at its own freeze.

### (d) Skeptical probes
1. Re-run the seat's F6 falsifier at the sitting head: in a disposable clone, tamper one science row in `configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json`, regenerate its `.sha256` sidecar, commit, then run the generator `--check --preserve-current-frozen-bytes`. Does it still print the tampered sha as "verified"?
2. Then check which layers DO catch it: `committed_pack_tree_sha256` (digest rotates), the plan-test literal pin, and the baseline manifest. The manifest pins only `_v1` digests (`docs/process/audit-baseline-manifest.json`, `head_commit ac3fe1d2…`) — so for the `_v3` family that catch layer **does not exist**. How many independent catches remain?
3. `python3 -c "import json;print('plan_tree' in json.dumps(json.load(open('configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json'))))"` → expect `False`.
4. Does `freeze-0003`'s `predecessor.pack_sha256` actually recompute today? Run `joulewise.arm_readiness.committed_pack_tree_sha256` over `configs/campaigns/d117_floor_qwen25_1p5b_v2` and compare to `95f7c51c…`. If the chain binding is the substitute catch, it must verify.
5. R-019/R-020 were closed as **registered residuals** under "single-operator generation discipline" (D-141, citing D-139 A1 *by analogy* — D-139 A1's own scope is the measurement environment). Is the analogy sound for a desk-time generator run on a machine that also runs agent fleets?

---

## L5-F-3 (should_fix) — Pre-arm sequence unregistered; the §5C dry-run receipt is stale by binding

### (a) Original finding (VERBATIM)
> - [should_fix] [L5] Pre-arm sequence unregistered: measurement checkout must advance and the §5C dry-run must be re-executed at the final head (dry-run-0001 is stale by binding)

Seat-report text (VERBATIM, §4 F-3):
> **F-3 SHOULD-FIX — Pre-arm sequence unregistered; the §5C dry-run receipt is stale by binding.** The measurement checkout sits at `49dcc49`, which **does not contain the arm-critical t0 author** (#149). After it advances, `_latest_dry_run_binding` (`arm_readiness.py:3402-3425`) requires the dry-run to bind the current head + committed digest; `dry-run-0001` binds `49dcc49`/`6246b618…`, so any arm at the baseline head refuses `readiness_dry_run_stale`. Mechanically fail-closed — but no register (RUN_STATE ED-OWED, 70h plan, ED-QUALIFICATION script) carries the required steps: advance checkout → re-execute §5C dry-run at the final head under the night's custody root → E-steps/t0/arm. The freeze log's X-8 line ("the freeze + dry-run pair discharges the validator role") reads as if the existing receipt carries over; it does not.

Citation: `sitting-packet-FINAL.md` §4; seat report §4 F-3, §7 work order WO-L5-3. Cross-confirmed
by L7's should-fix ("Mandatory pre-arm sequence is undocumented…") and ED-L7-2
(`sitting-packet-FINAL.md` §5).

### (b) What changed since 2026-08-15

**Checkout half — DONE.** A second measurement checkout exists:
`/Users/edr/JouleWise-measurement-20260818` at HEAD **`94dc3b3`** (the contrast freeze-0003
commit), `git status --porcelain` empty. The old `/Users/edr/JouleWise-measurement-20260813`
remains at `49dcc49`. freeze-0003's `pack_identity.pack_root` names the **20260818** checkout, so
the frozen `_v3` bytes are bound to it. Note `94dc3b3` is **not** the current repo head `b92b43d`
— the checkout is already behind by the S5-confirmation, S6-bookkeeping, D-149 and T14/T15 commits.

**Dry-run half — NOT DONE.** `find /Users/edr/JouleWise-window-custody -name "dry-run-*.json"`
returns exactly one file:
`/Users/edr/JouleWise-window-custody/d117_floor_qwen25_1p5b_v1/arm_readiness.dry_run.receipts/dry-run-0001.json`
— `issued_at_utc 2026-08-14T03:04:35Z`, `status PASS`, `arm_disposition NOT_APPLICABLE`,
`pack.pack_id d117_floor_qwen25_1p5b_v1`,
`pack.pack_root /Users/edr/JouleWise-measurement-20260813/configs/campaigns/d117_floor_qwen25_1p5b_v1`.
**No dry-run receipt exists for any `_v2` or `_v3` pack, at any head, in any custody root.**
The staleness enforcement the finding cites is intact: `_latest_dry_run_binding`
(`joulewise/arm_readiness.py:5881`, consumed at `:5936` and `:6169`) still returns
`readiness_dry_run_stale` (`:5929`).

**Registration half — PARTIAL.** `docs/process/rehearsal-operator-card.md` (added by `ad14ac4`
"Dress-rehearsal builder + operator card (terra rounds 1-5): measurement-checkout execution,
scratch custody topology, SMOKE/BOUNDARY/ED-FIRST markings, documented E-8 stop boundary",
**merged to main**) now registers a sequence: §1 Build → §2 Terminal review (ED-FIRST) → **§3 Part
A D-134 dry-run** → E-4/E-5 → E-7a/E-7b → E-8 → E-9a/b/ARM/verify/E-10. Its own status table marks
Build, Part A dry-run, E-4, E-5 and E-8 **BOUNDARY-PROVEN** (i.e. not executed) and E-7/E-9/ARM
**ED-FIRST**. The registered dry-run command targets
`--pack-root …/configs/campaigns/d117_floor_qwen25_1p5b_v2` under
`--window-custody-root …/ed-qual-20260817/rehearsal/arm-readiness-custody` — a **scratch rehearsal**
on the `_v2` pack, expressly "qualification choreography evidence, never claim evidence".
The newest operational document, `docs/process/window-run-cards/shakedown-v3-first-light.md`
(`b92b43d`, **branch-only**), lists six block steps (census+GO receipt, one calibration capture,
reduction, in-band check, idle baseline, custody close) and contains **no dry-run, arm, verify or
consume step at all**.

### (c) Candidate disposition for the seat
**STILL-OPEN (checkout advanced, dry-run absent, registration partial and scratch-scoped).**
The seat is adjudicating whether a pre-arm sequence registered only as a rehearsal card against the
`_v2` pack — every step of which is marked unexecuted — plus a run card with no receipt ceremony,
discharges a finding whose substance is that no register carries the production steps.

### (d) Skeptical probes
1. `find ~/JouleWise-window-custody -name "dry-run-*.json"` at the sitting. If the only hit is still the `_v1` receipt from 2026-08-14, no `_v3` arm can pass `_latest_dry_run_binding`.
2. `git -C /Users/edr/JouleWise-measurement-20260818 rev-parse HEAD` vs the sitting head. `94dc3b3` at assembly. A dry-run executed now would bind a head that the merge wave is about to move again — which head is "final"?
3. Read `docs/process/rehearsal-operator-card.md` §3: it targets `d117_floor_qwen25_1p5b_v2`, not `_v3`. Is there any registered pre-arm sequence for the pack family that will actually be armed?
4. `docs/process/window-run-cards/shakedown-v3-first-light.md` — confirm it contains no arm/verify/consume step, then ask under what authority a capture block runs with no receipt ceremony. (Its preconditions cite `docs/process/d149-go-receipt-template.md`, added by `79a4cd0`, branch-only.)
5. ED-L7-2 ("fresh §5C lead dry-run PASS at the final reviewed head on the measurement checkout") and EDQ-L2-2 are ED-QUALIFICATION rows that charter amendments 11-12 require closed at a READY-candidate sitting. Is there closure evidence for either?

---

## L5-F-4 (nit) — `--check` prints "verified unfrozen draft" on frozen packs

### (a) Original finding (VERBATIM)
> - [nit] [L5] --check prints 'verified unfrozen draft' on frozen packs

Seat-report text (VERBATIM, §4 F-4):
> **F-4 NIT** — `--check` prints "verified **unfrozen draft**" on frozen packs (`generate_configs.py:149-157,2168-2171`; M-2-acknowledged byte-preservation cosmetics).

### (b) What changed since 2026-08-15
- Ruling: **D-140** (`docs/decision_log.md:173`, cold gate 2026-08-18, three-seat concurrence,
  composed verdict `docs/process_traces/2026-08-18-freeze-semantics-coldgate/14-composed-verdict.md`,
  trace commit `3f9d759`, **merged to main**): *"'Freeze-aware' status = dynamic `target_status`
  from the authenticated attachment + the fail-closed non-preserve guard + option-(d) freeze-neutral
  emitted wording (round 6/7: `as_generated_pre_d134_freeze` + authority-naming fields)."*
- Code at HEAD (`configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:2657-2680`):
  `status = identity.target_status` — the printed word is now the **dynamic** authenticated freeze
  state, not the static `DRAFT_STATUS` constant. Landed via `7402855` and `5292cf7`
  (**merged to main**).

**Executed at `b92b43d` in a clean clone:**

| pack | invocation | exit | last line |
|---|---|---|---|
| `d117_floor_qwen25_1p5b_v1` | `--check` | 0 | `verified unfrozen draft: 100 science configs; …` |
| `d117_floor_qwen25_7b_v1` | `--check` | 0 | `unfrozen draft check passed: 100 science configs, …` |
| `d117_contrast_…_v1` | `--check` | 0 | `checked D-117 gamma unfrozen draft: …` |
| all three `_v2` | `--check` | **1** | `generation failed: the current frozen identity requires preserve mode` |
| all three `_v3` | `--check` | **1** | `generation failed: the current frozen identity requires preserve mode` |
| `d117_floor_qwen25_1p5b_v3` | `--check --preserve-current-frozen-bytes` | 0 | `verified d117_floor_qwen25_1p5b_v3 frozen by d134 receipt: 100 science configs; …` |
| `d117_floor_qwen25_7b_v3` | same | 0 | `d117_floor_qwen25_7b_v3 frozen by d134 receipt check passed: …` |
| `d117_contrast_…_v3` | same | 0 | `checked D-117 gamma d117_contrast_qwen25_1p5b_vs_7b_v3: …` |

Cause of the default refusal, read at HEAD: the `_v3` generator's
`CURRENT_FROZEN_RECEIPT_SHA256` (`:75-77`) is `1277103b…` — the **freeze-0002** sha — while the
`_v3` plan_tree's `arm_attachments/arm_readiness.freeze_receipt` names `freeze-0003.json`, sha
`0abfddb1…`. `PRESERVE_CURRENT_FROZEN_BYTES` (`:221-224`) therefore evaluates **False**, and the
constructor guard (`:274-278`) refuses: *"the current frozen identity requires preserve mode"*.
The same refusal is documented as expected behaviour in `d3aa15f`'s commit body.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED for the successor families (the wording is now dynamic and truthful);
STILL-OPEN for the `_v1` packs.** The seat is adjudicating a second, newly-executed fact the
finding did not contemplate: on every frozen successor pack the default `--check` now **exits 1**,
so L5's own positive probe 3 ("Generators `--check` ×3 at the baseline bytes: exit 0") reproduces
only with an explicit `--preserve-current-frozen-bytes`, and only the unfrozen-labelled `_v1` packs
verify by default.

### (d) Skeptical probes
1. Run all nine generators with a bare `--check` at the sitting head and record exit codes. Is a fail-closed guard that fires on **every frozen pack by default** a feature (D-140's "fail-closed non-preserve guard") or an operator trap on arm night?
2. Compare `CURRENT_FROZEN_RECEIPT_SHA256` in each `_v3` generator against that pack's own `plan_tree.json → arm_attachments.arm_readiness.freeze_receipt.sha256`. They differ for the alpha pack. Is `target_status` derived from the authenticated attachment (truthful) or from the stale constant?
3. `grep -rn "generate_configs.py --check" docs/` — does any runbook, run card, or operator card instruct `--check` **without** the preserve flag? If so, the documented command now fails.
4. Confirm the `_v1` packs (still printing "unfrozen draft") are genuinely out of the arm path at the sitting — the kernel's `D117-W-ALPHA.goal` still names `d117_floor_qwen25_1p5b_v1`.

---

## L5-F-5 (nit) — M-2 decision-log remedy wording diverges from the implemented preserve-bytes behavior

### (a) Original finding (VERBATIM)
> - [nit] [L5] M-2 decision-log remedy wording diverges from the implemented preserve-bytes behavior

Seat-report text (VERBATIM, §4 F-5):
> **F-5 NIT** — decision-log M-2 remedy wording ("regenerates the sidecar-consistent text") vs the implemented preserve-bytes behavior; `alpha_arm_readiness.md:31-35` states the operative reading. Consistency-sweep material so a future session doesn't "fix" frozen bytes.

### (b) What changed since 2026-08-15
- `c0b7068` "R4 (council Phase 0): M-2 execution note — remedy shipped forward-only, override
  standing until re-freeze retires it; soundness remanded to its own cold gate". Body inserted at
  `docs/decision_log.md:9014-9030` directly beneath the original M-2 ruling (`:9004-9013`):
  *"the remedy as ruled ('regenerates the sidecar-consistent text via the canonical path') did NOT
  execute as written — #149 shipped freeze-aware status FORWARD-ONLY under
  PRESERVE_CURRENT_FROZEN_BYTES, and the three frozen packs still carry `draft_status:
  "unfrozen_draft"` at the audit baseline (verified by the cold adjudicator and sweep-S3).
  Preserving frozen bytes was the correct engineering call…"*. WHERE it lives: **merged to main**.
- `docs/decision_log.md:9406` "**M-2 GATE AMENDMENT** — separate entry (heading added 2026-08-15;
  recorder-race gate mechanic caught it misfiled inside the recorder adoption entry)", executing
  the remanded cold gate's composed verdict
  (`docs/process_traces/2026-08-15-m2-coldgate/composed-verdict.md`): engineering core UPHELD;
  the "overrode a NO-GO reading" premise **STRICKEN**; the "every arm packet must cite this ruling"
  duty **STRICKEN**; retirement occurs at successor freeze only if the generator work makes
  draft_status freeze-aware; scope capped at the three 2026-08-13 receipt hashes.
  WHERE it lives: **merged to main**.
- Successor semantics now carry their own authority: **D-140** (`decision_log.md:173`) extends
  receipts-govern-over-bytes to ALL successor packs *by its own authority*, expressly because
  M-2 clause (d) bars citing the 2026-08-13 override beyond its three receipt hashes.

### (c) Candidate disposition for the seat
**READY-EVIDENCE-ATTACHED.** The divergence is now recorded in the decision log itself, as a dated
execution note plus a gate amendment, and successor packs are governed by a separate ruling rather
than by an extended M-2. The seat is adjudicating whether M-2's retirement condition is satisfied
by the `_v3` family's `as_generated_pre_d134_freeze` bytes and dynamic status line — and if so,
whether anything records that retirement.

### (d) Skeptical probes
1. `sed -n '9004,9032p' docs/decision_log.md` — is the execution note adjacent to the ruling it corrects, so a future session cannot read the stale remedy alone?
2. The M-2 execution note still says *"Every arm packet must cite this ruling until the Phase-2 re-freeze regenerates truthful freeze-aware status text"*, while the GATE AMENDMENT clause (b) **strikes** that duty. Two entries in the same file give opposite instructions — which governs, and does any arm packet cite M-2 today?
3. Has M-2 retired? The `_v3` family is frozen with `as_generated_pre_d134_freeze` bytes and a dynamic status line — clause (c)'s condition. No decision-log entry records the retirement. Should the sitting record it, or is the override still standing?
4. `docs/phase_2/alpha_arm_readiness.md:31-35` — does the "operative reading" text still match the implemented behaviour after `7402855`/`5292cf7`?

---

## L5-COVERAGE — 16 of 18 universe classes examined; universes self-nominated

### (a) Original finding (VERBATIM)
Seat verdict table (`sitting-packet-FINAL.md` §2): `| L5-PACK-READINESS-CUSTODY | GATING |
NOT_READY | 16/18 | 0 | 3 | 2 | 8 | 4 | 1 |`.

Seat report §1 (VERBATIM):
> | U17 | CI behavior of the pack-integrity plan tests | **NO — no network; see finding 1** |
> | U18 | Live arm-night executions (t0 author, dry-run at final head, arm/verify/consume, U11 live verify) | **NO — T-0/lead work by design; covered by 58 landed tests** |
>
> **Coverage: 16/18** universe classes examined; the two unexamined classes are listed plainly above and in §5.

Governing ruling (`council-verdict.md` §VERDICT, VERBATIM):
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

### (b) What changed since 2026-08-15
- **NO independent re-enumeration of L5's universe exists.** `ls docs/process_traces/` shows only
  L2's re-audit (`2026-08-15-l2-reaudit`, custody commit `0f886d3`) among post-council re-audits.
- **The universe has grown substantially.** L5's audited universe was three `_v1` packs (154+154+135
  files), their generators, 33 evidence receipts, 3 freeze receipts, 3 U11 projection receipts, one
  measurement checkout and one custody root. At the sitting head there are **nine** packs
  (`_v1`/`_v2`/`_v3` × 3), **two** measurement checkouts (`…20260813` @ `49dcc49`,
  `…20260818` @ `94dc3b3`), 99 evidence receipts, freeze-0002 and freeze-0003 chains, and new
  custody roots (`ed-qual-20260817`, `shakedown-20260818`, `profiler-pilot-20260818`).
- **U17 (CI behavior) is still unexamined by execution** — no network here. Partially substituted:
  the assembler proved offline that the modules are discovered, non-exclusive and shard-assigned at
  both `ac3fe1d` (shards 3/4) and `b92b43d` (shards 2/3), and executed the modules locally on 3.13
  and CI's floor 3.11 (all OK at the current head; deterministic FAIL reproduced at `ac3fe1d`).
  The Actions-log question itself is untouched.
- **U18 (live arm-night executions) is still unexamined** and is now *more* open than at the audit:
  no dry-run receipt exists for the successor family (see F-3), and the arm/verify/consume chain has
  never run against `_v3`.
- **Phase-3 baseline supersession has not happened.** `docs/process/audit-baseline-manifest.json`
  still pins `head_commit ac3fe1d2…`, `origin_main ac3fe1d2…` and the three `_v1` pack digests, and
  lacks the ruled `pack_digest_algorithm` field (council: "Manifest conditions at supersession",
  cold §B.2 / Opus S11). Last touched by `694442c`. For the `_v3` family the manifest is not a catch
  layer at all.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a 16/18 denominator that was self-nominated, never
independently re-enumerated as the verdict ordered, and now describes roughly a third of the
artifacts actually in scope — measured against a baseline manifest that does not cover the
operative pack family.

### (d) Skeptical probes
1. Independently enumerate L5's universe at the sitting head and compare to 18. Count all nine packs, both measurement checkouts, both freeze chains, and every custody root created since 2026-08-15.
2. Re-run L5's own integrity sweep (every sidecar, pin, receipt, namespace inventory) against the `_v3` family, not the `_v1` family it was run on. Does it still return ALL-PASS?
3. Re-run the eight falsifiers (N1, N2, F1–F6) against a `_v3` pack. F4 (receipt replayed across packs) and F5 (evidence replayed across packs) are now testable across three *generations* of the same pack lineage — a case that did not exist at the audit.
4. Is there a supersession baseline manifest? If not, what immutable reference binds the `_v3` digests, and who recorded them?
5. ED-QUAL-L5-1 (real `sudo systemsetup` capture validated against `arm_readiness_evidence_t0.py:838-861`) is this seat's only ED row. Charter amendments 11-12 require ED-QUALIFICATION rows closed at a READY-candidate sitting. Where is its closure evidence?

---

## L5-UNEXECUTED — CI log verification for the floor-pack plan-test shard (council's named highest-value follow-up)

### (a) Original obligation (VERBATIM)
`sitting-packet-FINAL.md` §6:
> - [L5] CI log verification for the floor-pack plan-test shard (no network in the audit sandbox): whether #149's CI genuinely ran and passed tests.test_d117_floor_qwen25_{1p5b,7b}_plan — finding 1 makes this the highest-value follow-up; a refuter with network should pull the actions log.

Seat report §5 item 1 (VERBATIM):
> 1. **CI log pull for the floor-pack plan-test shard** (no network here) — highest-value refuter follow-up for F-1.

### (b) What changed since 2026-08-15
- **NOT DISCHARGED.** No network in this environment; no custodied Actions log for PR #149 exists
  in the repo (searched `docs/process_traces/`, `docs/evidence/`, `docs/run_reports/`).
- **Partial offline substitution executed by this assembler** (see F-1(b) for the full table):
  - The modules are discovered by `shard_tests.discover_test_modules()` and are **not** in
    `scripts/test_timings.json` `exclusive_modules` at either head — so CI schedules them:
    at `ac3fe1d`, `…1p5b_plan` → shard 3, `…7b_plan` + `…decode_contrast_plan` → shard 4;
    at `b92b43d`, shard 2 and shard 3.
  - CI sets no `PYTHONDONTWRITEBYTECODE` (`.github/workflows/ci.yml`), and the shard runner
    (`scripts/shard_tests.py` `run_shard`) plain-imports each module — the baseline pollution path
    is live under CI.
  - The modules FAIL deterministically at `ac3fe1d` on 3.13 (reproduced twice, fresh and re-run)
    and PASS at `b92b43d` on 3.13 and on CI's floor 3.11.
- Net: the mechanical premise of the question is now settled (CI *did* schedule the failing
  modules); the empirical answer (what the #149 run actually reported) still requires the log.

### (c) Candidate disposition for the seat
**STILL-OPEN — the council's named highest-value follow-up remains undischarged**, but the
question is now sharper: it is no longer "were they run?" (mechanically, yes) but "why was the
merge green when they deterministically fail from a clean tree at that head?"

### (d) Skeptical probes
1. With network: `gh run list --branch <#149 head> --limit 20` then `gh run view <id> --log` for the 3.11/3.14 shard-3 and shard-4 jobs at `ac3fe1d`. Search the log for `MODULE START tests.test_d117_floor_qwen25_1p5b_plan` and its result line.
2. If the log shows PASS, reconcile it against the reproduced local FAIL — candidate explanations to test: a differently-ordered import inside the shard process that pre-suppressed bytecode; a runner filesystem that refused the `.pyc` write; or a checkout state that differed from a clean clone.
3. If the log shows FAIL or the job is missing, ask what merged #149 and whether the same path is open for the pending merge wave (D-148 clause 2 pre-authorizes it "on gates-green").
4. Also pull CI for the current branch head. `d3aa15f`, `235c5ea`, `b6b5e6d`, `7402855`, `5292cf7`, `c94e0b0` are on main, but the 51 branch commits carrying the `_v3` family have no verified CI status in-repo.

---

## ROW-LEVEL OPEN ITEMS
- **F-2 (echo hole): NO REPAIR of either named remedy.** Preserve mode still copies committed bytes into the "generated" output and compares them with themselves (`generate_configs.py` `_generate` + `check_current`), now for the whole output inventory rather than three files; and `freeze-0003.json` contains no `plan_tree` binding (verified: the string does not occur in the receipt). The adjacent generator work (`b6b5e6d`, `7402855`, `5292cf7`, D-141) changed semantics and closed the *accidental* symlink class, but left the self-comparison intact; the symlink and v1-schema-in-`_v2` residuals were **accepted as registered residuals** R-019/R-020, not fixed.
- **F-3 (dry-run): NOT DONE.** No dry-run receipt exists for any `_v2` or `_v3` pack in any custody root; the only receipt is `dry-run-0001` (2026-08-14) bound to `_v1` at `/Users/edr/JouleWise-measurement-20260813`. `readiness_dry_run_stale` enforcement is intact, so an arm would refuse.
- **F-3 (registration): PARTIAL and scratch-scoped.** `rehearsal-operator-card.md` registers the sequence but targets the `_v2` pack in a scratch rehearsal and marks every step BOUNDARY-PROVEN or ED-FIRST (none executed). The current operational document, `shakedown-v3-first-light.md`, contains no dry-run/arm/verify/consume step at all.
- **F-4 for the `_v1` packs: NOT REPAIRED** — all three `_v1` generators still print "unfrozen draft" and exit 0 on a bare `--check`.
- **NEW, previously unrecorded (executed):** every frozen successor generator (`_v2` ×3 and `_v3` ×3) **exits 1** on a bare `--check` with `generation failed: the current frozen identity requires preserve mode`, because each generator's `CURRENT_FROZEN_RECEIPT_SHA256` names the *predecessor's* freeze receipt (`_v3` alpha: constant `1277103b…` = freeze-0002 vs the pack's attached freeze-0003 `0abfddb1…`). L5's positive probe 3 does not reproduce on the operative family without an explicit `--preserve-current-frozen-bytes`.
- **The CI-truth question (council's highest-value L5 follow-up) is undischarged.** No network; no custodied Actions log in-repo. Offline work narrowed it: the failing modules were genuinely shard-scheduled at `ac3fe1d` and fail deterministically there, so the green-merge record needs an explanation, not just a re-run.
- **No independent coverage re-enumeration for L5** exists, though `council-verdict.md` makes it a standing packet element; the universe has grown from 3 packs / 1 checkout to 9 packs / 2 checkouts / 3 new custody roots.
- **No Phase-3 baseline-manifest supersession exists.** `audit-baseline-manifest.json` still pins `ac3fe1d2…` and the `_v1` digests, so for the `_v3` family the manifest is not a catch layer.
- **The operative artifacts are branch-only.** The `_v3` packs, freeze-0003 receipts, `ed-s5-mint-decision-2026-08-19.md`, the D-149 GO-receipt template and the shakedown run card all live on `impl/r2-s0-mint-resolver`, not on `main` (`0099382`). The run card's own precondition demands the merge wave land first.
- **ED-QUAL-L5-1 closure evidence not located** in `docs/process_traces/`, `docs/process/ed-*.md`, `TASK_QUEUE.md` or `RUN_STATE.md` (searched by grep for `ED-QUAL-L5`).
- **Assembly-head drift:** verified at `b92b43d`, not the brief's `d10881b`. Re-pin any sha to the sitting head.
