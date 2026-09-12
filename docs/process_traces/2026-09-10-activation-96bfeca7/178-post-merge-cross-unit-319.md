# Record 178 — Post-merge cross-unit integration review of PR #319 (EPOCH-EQUIVALENCE-01) at main e95bc22a

Gate row 11, second half. READ-ONLY. Nothing was modified; no git write command was run.

Checkout read: `/Users/edr/code/JouleWise-wt-bk-96bfeca7` HEAD = `39f5fcb6ed085183456b3c9630cfe1cc957d0f66`,
which CONTAINS `e95bc22a` but is not equal to it, so the tree was exported and all work below ran in
`/tmp/e95bc22a-check` (`git archive e95bc22a | tar -x`). Every file:line in this report is at e95bc22a.

## Verdict

**CLEAN on the merged unit's internal consistency (questions 1, 2, 3, 6).** The runbook block, the
script's argparse, the pre-registration, the D-102 addendum and the tool's printed constants agree
exactly; the pins parser still parses one os_build and one sampler sha from the revised
pre-registration; the three test modules are green.

**Three SHOULD-FIX findings outside the merged unit** (questions 4 and 5): the continuation route's
code census is larger than the runbook's "smallest change" sentence implies (F-1), the operative
pointers in RUN_STATE/README/TASK_QUEUE/state_kernel still describe the superseded three-night
default and would keep G2-a blocked forever on a predicate the default path can no longer satisfy
(F-2), and §2.5's "run it twice and compare byte for byte" cannot be executed as written (F-3).
Two NITs.

---

## 1. Runbook §2.5 invocation vs the script's argparse vs §2.0's exports — CLEAN

The §2.5 block (`docs/phase_2/derivation_night_runbook.md:1713-1720`):

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/epoch_equivalence_check.py \
  --session-id "$SESSION_ID" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --repo-root "$MEASUREMENT_ROOT" \
  --out "$NIGHT_ROOT/epoch-equivalence-record.json"
```

**Flags.** All five exist in `build_parser()` with the spelling used:
`--session-id` (`scripts/epoch_equivalence_check.py:670-673`), `--ledger` (`:674-677`),
`--head-pin` (`:678-684`), `--repo-root` (`:689-692`), `--out` (`:693-699`).
`--acceptance` (`:685-688`) and `--force` (`:700-703`) are correctly not passed.

**Defaults.** §2.5's claim that "`--acceptance` is left at its default, which resolves against the
checkout the SCRIPT lives in" is true: `DEFAULT_ACCEPTANCE_BOUND_PATH` = `ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH`
(`joulewise/calibration_bracketing.py:178`, `:126-128`), rooted at the importing module's
`Path(__file__).resolve().parents[1]`. Same for `--ledger` / `--head-pin` defaults
(`joulewise/calibration_ledger.py:104-108`), which the runbook overrides explicitly anyway.
The generation lock the prose promises is real: `reference_envelope()` refuses any acceptance other
than r6 by id.

**Exit codes.** §2.5's sentence "Exit code 0 is PASS, 4 is FAIL, 5 is INCONCLUSIVE; 3 means the tool
refused" matches the code exactly: `REFUSAL_EXIT = 3`, `FAIL_EXIT = 4`, `INCONCLUSIVE_EXIT = 5`
(`scripts/epoch_equivalence_check.py:121-123`), mapped at `VERDICT_EXITS` (`:599-603`) and returned
at `run()` (`:638`) and `main_args()` (`:718-721`). `MINIMUM_RETAINED_M = 6` (`:127`) matches
issue 316's "m < 6" branch, and the branch is evaluated BEFORE the comparisons (`:478`, `:569`),
as §2.5 requires.

**Variables.** The block interpolates six: `$MEASUREMENT_ROOT`, `$PY`, `$SESSION_ID`,
`$CALIBRATION_LEDGER`, `$LEDGER_HEAD_PIN`, `$NIGHT_ROOT`. **All six are exported earlier**, and all
six are exported in §2.0 itself (`:1399-1416`), which is the right place because §2 runs in the
harvesting activation's fresh shell:

| Variable | Exported at |
|---|---|
| `MEASUREMENT_ROOT` | `derivation_night_runbook.md:1401` (§2.0; also §0.2) |
| `PY` | `:1403` (§2.0; also `:282` in §0.2) |
| `NIGHT_ROOT` | `:1405` (§2.0; also `:328` in §0.2) |
| `CALIBRATION_LEDGER` | `:1407` (§2.0; also `:331` in §0.2) |
| `LEDGER_HEAD_PIN` | `:1408` (§2.0; also `:332` in §0.2) |
| `SESSION_ID` | `:1414-1415` (§2.0, `eval`'d out of the sha-verified `chain.zsh`, then re-`export`ed) |

**Nothing the §2.5 block uses is unexported.** The §2.0 block also verifies `test -x "$PY"`, the head
equality, and the wrapper's sidecar digest before the `eval`, so `SESSION_ID` is not trusted blind.

## 2. Same rule and constants across the four surfaces — CLEAN

```
$ cd /tmp/e95bc22a-check && PYTHONDONTWRITEBYTECODE=1 python3 scripts/epoch_equivalence_check.py --print-envelope-only; echo rc=$?
Reference envelope (the acceptance in force; issue 316)
  acceptance_id: d079_calibration_acceptance_v2_n17_r6
  artifact: configs/calibration/calibration_acceptance_d079_v2_n17_r6.json  sha256 0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d
    loaded by joulewise.calibration_bracketing.load_calibration_acceptance_bound
  screen rule registered for this generation: range_equals_screen
  corpus n = 17 (artifact derivation_corpus.n; registry corpus_n; they agree)
  raw corpus maximum_s = 0.03289849371536248  [artifact decimal_derivation.source_statistics]
  raw corpus range_s   = 0.00972358928879385  [artifact decimal_derivation.source_statistics]
  OPERATIVE level screen   preflight_level_screen_s   = 0.032898493715362  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  OPERATIVE bracket screen bracket_screen_s           = 0.009724  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  budget ceiling           maximum_budgetable_drift_s = 0.010164834757777545  [validator registry _D102_GENERATION_DERIVATIONS operatives]
    artifact decimal_derivation.ratified_operatives agrees with the registry on all three, or this tool refuses
    NOTE: the operative comparators differ from the raw statistics by quantization; no floor is in force under this screen rule; issue 316 rules the OPERATIVE value is the one compared against.
rc=0
```

Cross-check of every printed constant against the three prose surfaces:

| Constant | Tool (above) | Pre-registration rev 2 | D-102 addendum | Runbook §2.5 |
|---|---|---|---|---|
| level screen (operative) | `0.032898493715362` | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:389`, `:438` | `docs/decision_log.md` addendum ("level screen `0.032898493715362` s") | `:1640` table row, `:1679` |
| bracket screen (operative) | `0.009724` | `:390`, `:439` | addendum ("bracket screen `0.009724` s") | `:1641`, `:1680` |
| budget ceiling | `0.010164834757777545` | `:391` | addendum | `:1642` |
| raw maximum | `0.03289849371536248` | `:389`, `:405` | addendum | `:1640`, `:1653` |
| raw range | `0.00972358928879385` | `:390`, `:399` | addendum | `:1641`, `:1648` |
| corpus n | `17` | `:389` context | addendum ("n = 17") | `:1643` |
| screen rule | `range_equals_screen` | `:415` | addendum | `:1662` |
| floor NOT in force | `0.010818` named as belonging to the successor rule | `:412-415` | addendum | `:1657-1663` |
| m threshold | `MINIMUM_RETAINED_M = 6` | `:430` ("If m < 6 … INCONCLUSIVE") | addendum (same quote) | `:1671`, `:1680`, `:1691` |

All four agree, including the two quantization deltas (`4.1071120615e-7 s` and `4.8e-16 s`) and the
direction of each (bracket screen marginally more permissive, level screen marginally stricter).
Pre-registration `:392` additionally registers `max_budgetable_excess_s = 0.000440834757777545`,
which the runbook does not restate — correct, since the check compares against the two screens only.

## 3. `preregistration_epoch_pins` on the revised pre-registration — CLEAN

Signature: `scripts/issue_calibration_acceptance_generation.py:806`
`def preregistration_epoch_pins(text: str) -> tuple[str, str]` — it demands EXACTLY ONE distinct
value for each of `_PREREGISTRATION_OS_BUILD` and `_PREREGISTRATION_POWERMETRICS`, raising
`PrepareRefusal` on "absent" or "ambiguous (N values)" (`:809-821`). Call sites: `:308` (`check
--preregistration`) and `:1183` (`prepare-candidate`).

```
$ cd /tmp/e95bc22a-check && PYTHONDONTWRITEBYTECODE=1 python3 -c "... spec_from_file_location('issuer', 'scripts/issue_calibration_acceptance_generation.py') ...
    print(m.preregistration_epoch_pins(open('configs/calibration/preregistration_d079_epoch_25g83_rev1.md').read()))"
('25G83', 'b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5')
rc=0
```

Revision 2's 227 added lines did NOT introduce a second os_build spelling or a second sampler digest,
so the `check --preregistration` sampler line and `prepare-candidate`'s in-code enforcement both still
resolve. (Note: `prepare-candidate` also pins the file's own sha256 against `--preregistration-sha256`
at `:1177-1181`, so any arm materials carrying revision 1's digest are now stale by construction —
expected, and the runbook's arm step already says to pin the digest at arm time.)

## 4. Census: every site that compares machine identity against the acceptance's identity epoch

Six sites were named in the brief; here is what each actually does at e95bc22a, plus one the brief
did not name and one that behaves in REVERSE after a continuation.

### (a) Sites that refuse TODAY and must be proven to pass after a continuation

1. **`joulewise/calibration_bracketing.py` evaluate path.**
   `identity_epoch = artifact["identity_epoch"]` at `:2031`; observed vector built from
   `ACCEPTANCE_IDENTITY_FIELDS` at `:2046-2048`; `stale_fields` at `:2049-2053`; `freshness_status`
   at `:2054`; recorded in the result block at `:2069-2080` (`"basis": "exact_identity_epoch"`); the
   **refusal** is `:2105-2106` — `if stale_fields: return result, ("calibration_acceptance_bound_stale",)`.
   This is the reason ordinary capture is dead today.

2. **`scripts/validate_powermetrics_fiducial.py` ordinary preflight.**
   `_derive_preflight_systematic_screen_s()` at `:366-408`: `expected_epoch = artifact.get("identity_epoch")`
   at `:396`; the equality at `:399-404`; the **refusal** `_AcceptancePreflightError("acceptance_artifact_epoch_mismatch", stale_fields=...)`
   at `:405-408`. The planned epoch it is handed is built at `:1951-1958`.

3. **`scripts/generate_g2a_probe_inputs.py`.** Two distinct comparisons:
   - `_derive_live_vectors()` calls `_derive_preflight_systematic_screen_s(planned_epoch)` at `:660`
     with the live `kern.osversion`/`hw.model` vector built at `:652-659`, so it inherits site (2)'s
     refusal and cannot emit inputs today. Entry from `main` at `:921-924`.
   - The `check`/verify path re-reads the written `identity_epoch.json` and compares it with a freshly
     derived live vector: `identity != current_identity` → `raise G2AProbeError("identity_epoch_mismatch")`
     at `:1226-1230` (inventory reference validated at `:1205-1207`).

4. **`scripts/issue_calibration_acceptance_generation.py check`.** The desk epoch watch's `expected`
   vector takes its first two WATCH_FIELDS from the acceptance's own `identity_epoch` at `:270-272`
   (the remaining fields come from the ledger's last T1 row, `:290-295`); the live vector is
   `observe_machine()` at `:297`; `mismatched_fields()` at `:298`; **rc 3** is returned at `:342`
   (`return 3 if errors or mismatches or preregistration_failed else 0`) when no `--session-ids` is
   named — which is exactly the rc the runbook's §0.3 expects today. After a continuation this flips
   to rc 0, and §0.3's title ("`check` must exit 3, and that is the expected result") becomes
   pre-continuation-only text.

### (b) The site that would NEWLY REFUSE after a continuation — the inverse guard

5. **`scripts/validate_powermetrics_fiducial.py` derivation-only guard.**
   `_derivation_only_screen_basis()` (`:495-535`) deliberately skips the epoch EQUALITY, and the
   writer then recomputes the stale-field list itself at `:1931-1935` and refuses when it is **EMPTY**:
   `RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED` at `:1936-1941`, with the comment at `:1926-1930`
   stating the design ("an EMPTY list is the refusal"). **Consequence for the continuation PR:** the
   moment the acceptance in force binds 25G83, `--derivation-only` capture becomes impossible. That
   is correct by design, but it means the FAIL-route fallback (§3's nights two and three, and any
   later re-derivation night) cannot run from a checkout whose acceptance has already been continued.
   The continuation PR must state this explicitly, and the runbook's FAIL row (`:1693`) should not be
   read as "continue, then still keep the fallback open in the same tree".

### (c) `joulewise/arm_readiness.py` — NO identity-epoch comparison

Grep for `calibration_acceptance|acceptance_bound|_derive_preflight|preflight_level_screen` in
`joulewise/arm_readiness.py` returns only the id ALLOWLIST `_issued_d079()` at `:6142-6168`, whose
set at `:6161-6167` ends with `"d079_calibration_acceptance_v2_n17_r6"`. It routes
`SUCCESSOR_ACCEPTANCE_ONLY` readiness rows (`applicability_for_row`, `:6128-6140`; call sites
`:7516, :7636, :7971, :8695, :8968, :9010` via `successor_acceptance=not _issued_d079(tree)`).
The only `identity_epoch` construction in the module (`:8081-8093`, `:8158`) is the SYNTHETIC
rehearsal seam (`"os_build": "synthetic"`), not a live comparison.
**Census item:** a continuation that keeps the id `d079_calibration_acceptance_v2_n17_r6` leaves this
allowlist correct. A continuation that RE-ISSUES under a new id would not —
`default_acceptance_id()` (`scripts/issue_calibration_acceptance_generation.py:842-851`) mints
`d079_calibration_acceptance_v2_n{n}_{os_build.lower()}_r1`, which is absent from `_issued_d079`,
absent from `_D102_GENERATION_DERIVATIONS` (`joulewise/calibration_bracketing.py:357`), and absent
from `epoch_equivalence_check`'s r6 lock. Every `SUCCESSOR_ACCEPTANCE_ONLY` row would silently flip
from NOT_APPLICABLE to REQUIRED.

### F-1 (SHOULD-FIX) — the continuation's byte-level census is 19 files, not a "smallest change"

Runbook `:1692` (the PASS row of the outcomes table) says: "If the epoch-freshness refusal in the loader or the issuer blocks continuation,
land the SMALLEST change that removes it through the ordinary pull-request gate". The D-102 addendum
says the same. Neither says WHERE the continued epoch is recorded. Every refusal in §(a) above reads
`artifact["identity_epoch"]` out of the artifact FILE
(`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`) — a decision-log addendum alone
clears none of them. Editing that file's `identity_epoch` in place changes its byte digest, and that
digest is replicated in **19 tracked non-trace files**:

```
joulewise/calibration_bracketing.py:130-131   (ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256, the code pin)
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/{plan_tree.json, generate_configs.py, arm_readiness.sources/acceptance-owner.json}
configs/campaigns/d117_floor_qwen25_1p5b_v3/{plan_tree.json, generate_configs.py, arm_readiness.sources/acceptance-owner.json}
configs/campaigns/d117_floor_qwen25_7b_v3/{plan_tree.json, generate_configs.py, arm_readiness.sources/acceptance-owner.json}
configs/campaigns/d117_contrast_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py
configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py
configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json
configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json
docs/process/ed-s5-mint-decision-2026-08-19.md
tests/test_d117_v3_family.py:23
tests/test_mint_floor_artifact_generalized.py:6288
tests/test_powermetrics_fiducial.py:1574
```

Several of those are FROZEN campaign packs and mint-floor extraction specs — claim-bearing bytes that
exist precisely so they do not move. So the continuation is a design decision with a real fork
(edit-in-place and re-pin 19 sites and their frozen packs, vs. issue a new artifact file and take the
`_issued_d079` / `_D102_GENERATION_DERIVATIONS` / r6-lock consequences of §(c)), not a mechanical
"smallest change". **Recommend:** the continuation PR's brief carries this census and the fork is
ruled before implementation, not discovered inside it. Nothing in the merged unit is wrong; the gap
is that the merged unit's PASS row understates the size of the act it authorizes.

## 5. Stale operative pointers

`tests.test_docs_freshness` is green (see §6), so no mechanical gate catches any of these.

| File:line | Text | Classification |
|---|---|---|
| `RUN_STATE.md:15` — "the derivation-night arm **per runbook 99 rev 3**" | The runbook is at **revision 6** at e95bc22a (`docs/phase_2/derivation_night_runbook.md:59`, `:65-66` record the rev-6 changes; §7 fact table `:2140`, §8 `:2211`). "runbook 99" is trace-record shorthand for `docs/process_traces/2026-09-10-activation-96bfeca7/99-derivation-night-runbook-draft.md`, superseded by the tracked file. | **stale operative pointer (fix)** — it is the NEXT EXACT ACTION line; an operator following it reads a superseded revision. |
| `RUN_STATE.md:15` — "produce identity-epoch and T1-bindings JSON at the desk (**the G2-a input generator writes both** — see record 134)" | Runbook rev 6 §0.8 names `scripts/write_derivation_night_inputs.py` (present at e95bc22a, 13275 bytes) as the desk-inputs writer, named at `:622` and `:647` and run as `"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"` (`:665`), with an explicit "It must be run with `$PY`" fence (`:655-661`). | **stale operative pointer (fix)** — it names the wrong tool for a step the runbook now owns. |
| `RUN_STATE.md:15` — "Open for Ed: … **V3 affirmative acknowledgment (three nights × 12, retained n ≥ 19)**" | V3 was ANSWERED by directive issue 316: NO as default, affirmed only on FAIL (`docs/decision_log.md` addendum, Decision 1). | **stale operative pointer (fix)** — it keeps a closed question on Ed's open list. |
| `README.md:16` — "the rules written down before any data exists (**three nights of twelve captures; no value examined before the third night closes**)"; and "the first derivation capture night is proposed to Ed by the documented handback; **the diagnostic G2-a window follows only once the successor acceptance is issued**" | Night one is now the equivalence check; blindness is "every rule fixed before data, not no one may look" (addendum, Ed's clarification); on PASS the first G2-a window follows the CONTINUATION ADDENDUM, with no successor issued. | **stale operative pointer (fix)** — this is the standing plain-language now/next blurb, i.e. Ed's and the advisor's view of the plan, and it states the superseded default. |
| `TASK_QUEUE.md:793` and `:964` (A179, ACCEPTANCE-EPOCH-25G83-01 Note) and `docs/process/state_kernel.json` `/tasks/ACCEPTANCE-EPOCH-25G83-01/status_note` (line 41) — "Remaining phases: (3) agent-free corpus nights (**3 × 12 slots**; … **runbook record 99 rev 3**) … Open for Ed: … **V3 affirmative acknowledgment**" | Same three defects in the lane's own status note, in both the queue and the kernel. | **stale operative pointer (fix)** |
| `TASK_QUEUE.md:793`/`:964` and `state_kernel.json` `/tasks/ACCEPTANCE-EPOCH-25G83-01/{goal,acceptance}` — the lane's registered acceptance requires "**D-138 atomic successor transaction** … and regenerated G2-a inputs" and "bind-window and check pass **at the transaction head**" | On the DEFAULT path (PASS → continuation addendum) no successor is issued and no D-138 transaction occurs, so the lane's registered acceptance is unsatisfiable by its own expected outcome. | **stale operative pointer (fix)** — see F-2. |
| `TASK_QUEUE.md:777` and `:948` (A159, G2A-FIRST-WINDOW-01) and `state_kernel.json:2536` — BLOCKED on "**Successor calibration acceptance issued for the live epoch, with fresh-clone bind-window and check passing at the D-138 transaction head**" | Same: the blocker predicate names an event the default path no longer produces. | **stale operative pointer (fix)** — see F-2. |
| `TASK_QUEUE.md:796`, `:967` and `state_kernel.json:5256` (A184) — "inert today (**runbook 99** does not route through the subcommand)" | Names a superseded artifact, but the substantive claim (the runbook does not route through `recover_calibration_ledger.py`'s session-refusal subcommand) is still true at rev 6. | **nit** — rename to the tracked runbook; no operative consequence. |
| `RUN_STATE.md:2771` ("costless for the three nights"), `RUN_STATE.md:3251` ("three-nights scheduling") | Inside earlier dated T-block entries. | **historical mention (fine)** — dated record of what was true then. |
| `PROJECT_STATUS.md` | No match for `25G83`, `epoch`, `three night`, `runbook 99`, or the G2-a generator. | **no pointer, nothing to fix.** |

### F-2 (SHOULD-FIX) — the default path cannot unblock G2-a as the queue is written

Both the lane row A179 and the G2-a lane A159 gate on "successor acceptance issued … at the D-138
transaction head". Under issue 316's default (PASS → continuation addendum, no successor, no D-138
transaction), `G2A-FIRST-WINDOW-01` would remain BLOCKED forever on a predicate the winning branch
never produces — against the standing objective of real G2-a numbers as soon as possible. The
continuation PR (or a bookkeeping commit before it) must re-state A179's acceptance and A159's
blocker as a two-branch predicate: **PASS → the dated D-102 continuation addendum has landed and the
epoch refusals in §4(a) are proven cleared in a fresh clone; FAIL → the existing successor/D-138
text.** This is a doctrine/acceptance change, so it is the magistrate's call, not a sweep's.

### F-3 (SHOULD-FIX) — §2.5's two-checkout replication cannot be run as written

`derivation_night_runbook.md:1730-1733` instructs: "Run it twice — once from the clone, once from a
second checkout at the same head — and compare the two records byte for byte before recording a
verdict." The only invocation given (`:1713-1720`) hardcodes `--out "$NIGHT_ROOT/epoch-equivalence-record.json"`,
and the tool refuses a pre-existing `--out` without `--force`:

```
scripts/epoch_equivalence_check.py:186-189
    if resolved.exists() and not force:
        raise EquivalenceRefusal(f"--out {out} already exists; pass --force to overwrite it")
```

So the second run exits 3 (refusal), and `--force` would OVERWRITE the first record — destroying the
very bytes the comparison needs. No second `--out` path, and no second `--repo-root`, appears
anywhere in the file (`grep -n "second checkout\|epoch-equivalence-record\|epoch_equivalence_check"`
returns only `:1703, :1715, :1719, :1725, :1731`). The fix is one line of runbook text (a distinct
`--out`, e.g. `…-record-b.json`, plus the second checkout's own `--repo-root`), not a code change —
below the bench-vs-session threshold, but it must land before the check is run for real, because the
operator will hit it at the desk at the one moment the night's verdict is being recorded.

### NIT-1 — `--repo-root` for the second checkout is unspecified
The block pins `--repo-root "$MEASUREMENT_ROOT"`. §2.5's replication paragraph says the second
checkout "runs its own copy", but `--repo-root` is what the `read_replay` custody path resolves
against (`scripts/epoch_equivalence_check.py:621-628`), and the runbook never says whether the second
run keeps `$MEASUREMENT_ROOT` or points at its own tree. Fold into the F-3 edit.

### NIT-2 — §0.3's "`check` must exit 3" is pre-continuation-only
`derivation_night_runbook.md:372` is correct today and becomes false the moment a continuation lands
(`issue_calibration_acceptance_generation.py:342`). Worth one clause so a post-continuation reader
does not treat rc 0 as a failure of the runbook.

### Non-finding checked and cleared
The new `custody_read_replay_allowlist.json` entry carries an absolute `"line": 621`, which at
e95bc22a is indeed the `load_calibration_ledger_snapshot(` call in `run()`. This is NOT the
V2-SURFACE-GUARD-REKEY-01 (A183) fragility class: `tests/test_custody_mode_inventory.py:226-232`
keys on `(file, function, ordinal)` and only sanity-checks that `line` is a positive int, so an
insertion above line 621 will not re-red the guard.

## 6. Test evidence

```
$ cd /tmp/e95bc22a-check && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_equivalence_check tests.test_docs_freshness tests.test_gen_state 2>&1 | tail -3
Ran 101 tests in 12.243s

OK
```

## Summary of findings

| ID | Severity | One line |
|---|---|---|
| F-1 | should-fix | The continuation's byte-level census is 19 tracked files pinning the r6 artifact digest, several of them frozen claim-bearing packs; the PASS row's "smallest change" sentence understates a design fork that should be ruled before implementation. |
| F-2 | should-fix | A179's registered acceptance and A159's blocker both gate on a successor issuance / D-138 transaction the default (PASS) path never produces, so G2-a stays blocked forever as written. |
| F-3 | should-fix | §2.5's "run it twice, compare byte for byte" is unexecutable: one hardcoded `--out`, and the tool refuses an existing `--out` without `--force` (which destroys the first record). |
| S-1..S-5 | stale operative pointers (fix) | `RUN_STATE.md:15` ×3 (runbook 99 rev 3; G2-a generator writes the desk inputs; V3 open for Ed); `README.md:16` ×2 (three-nights default; G2-a only after a successor is issued); A179 status note in `TASK_QUEUE.md:793/:964` + `state_kernel.json:41`. |
| NIT-1 | nit | `--repo-root` unspecified for the second checkout. |
| NIT-2 | nit | §0.3's "`check` must exit 3" needs a post-continuation clause. |
| — | historical (fine) | `RUN_STATE.md:2771`, `:3251`; A184's "runbook 99" (`TASK_QUEUE.md:796/:967`, `state_kernel.json:5256`) is a nit rename only. |

Questions 1, 2, 3 and 6: **CLEAN**. The merged unit is internally consistent and green. Every
should-fix is a cross-unit or downstream-pointer defect, none of them in the PR #319 diff itself.
