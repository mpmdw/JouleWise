# 117 — Gate ledger row 10: final-head fresh-eyes review

- **Tree:** `/Users/edr/code/JouleWise-wt-epoch-integration`
- **HEAD (verified `git rev-parse HEAD`):** `1e15a3a509197d7f7382bb2c12f496ac7193ee54`, working tree clean
- **Range reviewed:** `d9612e68..HEAD` (16 commits; 14 files, +1406/-203)
- **Mode:** strictly read-only. No edits, no mutation cuts, no git state changes. Two test modules run (not the suite).
- **Reviewer:** Opus 5 (1M), fresh eyes, no seat context.

## VERDICT: **should_fix** — no blocker, no new seam break, no regression of a reviewed property. Three should_fix (two of them doc/process, one contract-sentence accuracy) and three nits.

---

## (1) New defect / seam break / regression of a reviewed property — NONE FOUND

| Reviewed property | Status | Evidence |
|---|---|---|
| Byte identity of bracket ledger receipts | **intact** | No receipt-writing code in the range. `joulewise/calibration_ledger.py` is untouched; `scripts/validate_powermetrics_fiducial.py` is untouched (only its test file's docstrings changed). |
| Six issued acceptance rows validate byte-identically | **intact, executed** | The one new validator term (`joulewise/calibration_bracketing.py:483-486`) is gated on `screen_rule != SCREEN_RULE_FLOORED_RANGE_ENVELOPE`, and all six issued rows are `range_equals_screen`, so it short-circuits before ever reading `corpus_n`. Executed: all six rows still `_registered_generation_row_is_complete() == True` (output below). |
| Ordinary writer path unchanged | **intact** | `git diff d9612e68..HEAD --stat` lists no production writer file. The chain's three-way dispatch changes only how the CALLER reads the writer's status. |
| Blindness | **intact** | `refuse_open_registration` (`scripts/issue_calibration_acceptance_generation.py:953`) is still called first, at `:1154`, before the snapshot refusal check and before every new fence (`:1191`, `:1197`, `:1209`, `:1213`) and before `_registration_observations`. Nothing new computes or prints a corpus statistic ahead of it. |
| Pre-registration / issuer agreement table (109 §4) | **one mis-described object** | See should_fix **S-3**. Behaviour is correct and slightly stronger than the prose; the prose names the wrong home for one of the two pins. |
| Fail-closed KeyError risk on the new fences | **safe** | `snapshot.bracket_session_by_id[session_id]` at `:1199` is a bare index, but `_registration_observations` (`:984-992`) already refused any session id absent from the ledger, and it runs first at `:1179`. `generation["corpus_n"]` at `:485` is guarded by `_GENERATION_ROW_REQUIRED_KEYS.issubset(...)` at `:395`, and both callers (`:745`, `:1844`) source `generation` from the module's own `_D102_GENERATION_DERIVATIONS`, never from artifact input. |
| Generated-region / chain-digest coherence | **in sync, executed** | `gen_derivation_night.py --check` → `PASS`, and the runsheet's baked digest `b8bf5b0a…c8cf` equals the live `shasum -a 256` of the tracked chain. |
| Runsheet's "the key set is exact" claim | **true, executed** | `NightPlan.from_mapping` accepts the example plan with 40-hex placeholders filled, and refuses both an extra key and a missing key. |

```
$ python3 -c "... _D102_GENERATION_DERIVATIONS / _registered_generation_row_is_complete ..."
d079_calibration_acceptance_v2_n19    | screen_rule= range_equals_screen | corpus_n= 19 | complete= True
d079_calibration_acceptance_v2_n19_r2 | screen_rule= range_equals_screen | corpus_n= 19 | complete= True
d079_calibration_acceptance_v2_n17_r3 | screen_rule= range_equals_screen | corpus_n= 17 | complete= True
d079_calibration_acceptance_v2_n17_r4 | screen_rule= range_equals_screen | corpus_n= 17 | complete= True
d079_calibration_acceptance_v2_n17_r5 | screen_rule= range_equals_screen | corpus_n= 17 | complete= True
d079_calibration_acceptance_v2_n17_r6 | screen_rule= range_equals_screen | corpus_n= 17 | complete= True
```

Targeted test modules run at HEAD (not the suite):

```
$ python3 -m unittest tests.test_gen_derivation_night -q               → Ran 40 tests  OK  (29.2 s)
$ python3 -m unittest tests.test_issue_calibration_acceptance_generation -q → Ran 109 tests OK (213.2 s)
```

`slot_end` log-line change (`slot_end slot=$slot` → `… disposition=valid|non-valid`) has **no production consumer**: `grep -rn slot_end` over `*.py`/`*.zsh`/`*.md` returns only the chain itself, `gen_derivation_night.py`'s anchor table, and three test files. No seam break.

---

## (2) New refusals are fail-closed and reachable — EXECUTED

### 2a. `prepare-candidate` without `--preregistration-sha256` → **argparse rc 2**

```
$ python3 scripts/issue_calibration_acceptance_generation.py prepare-candidate \
    --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
    --out /tmp/row10-out.json
usage: issue_calibration_acceptance_generation.py prepare-candidate
       [-h] [--ledger LEDGER] [--head-pin HEAD_PIN] [--repo-root REPO_ROOT]
       --preregistration PREREGISTRATION
       ...
       --preregistration-sha256 PREREGISTRATION_SHA256
       [--nights-ruling NIGHTS_RULING] [--slot-count-ruling SLOT_COUNT_RULING]
       [--epoch-catalog-id EPOCH_CATALOG_ID] [--acceptance-id ACCEPTANCE_ID]
       --out OUT
issue_calibration_acceptance_generation.py prepare-candidate: error: the following arguments are required: --preregistration-sha256
=== EXIT: 2 ===
$ ls /tmp/row10-out.json
ls: /tmp/row10-out.json: No such file or directory      # nothing written
```

Fail-closed: `required=True` on the parser, so the pin cannot be omitted and no output file is produced.

### 2b. `check --preregistration` on the real file, on the real machine → **comparison line printed, rc 3**

```
$ python3 scripts/issue_calibration_acceptance_generation.py check \
    --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md
Desk epoch watch (identity comparison only; no capture authorization)
ACTIVE acceptance: d079_calibration_acceptance_v2_n17_r6
field                  expected                    observed                    status
os_build               25F84                       25G83                       MISMATCH
hardware_model         Mac15,9                     Mac15,9                     match
powermetrics_sha256    unavailable                 b762e5bf…30c5               MISMATCH
mlx_version            unavailable                 unavailable                 MISMATCH
ledger: calibration_ledger_missing, calibration_ledger_rollback
mismatched fields: os_build, powermetrics_sha256, mlx_version
pre-registered powermetrics sha256 b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5: match
=== EXIT: 3 ===
```

**THE COMPARISON LINE (verbatim):**
`pre-registered powermetrics sha256 b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5: match`

(The column widths above are elided for this report; the executed output used the real `<64` widths. The `ledger:` refusal is an artefact of running the watch from an integration worktree that holds no calibration ledger, not a defect of the new flag.)

**Byte-identity of the watch without the flag — verified by diff of the two runs:**

```
$ python3 scripts/issue_calibration_acceptance_generation.py check   → EXIT 3
$ diff /tmp/row10-check-without.txt /tmp/row10-check-with.txt
8a9
> pre-registered powermetrics sha256 b762e5bf…30c5: match
```

Exactly one appended line, nothing else moved. The claim in `check()`'s comment holds.

### 2c. `gen_derivation_night.py --help` → **rc 0**, both new flags present and both new refusals reachable

```
$ python3 scripts/gen_derivation_night.py --help   → EXIT 0
usage: gen_derivation_night.py [-h] [--plan PLAN] [--session-id SESSION_ID]
                               [--window-id WINDOW_ID] [--evidence-root-id EVIDENCE_ROOT_ID]
                               [--calibration-plan CALIBRATION_PLAN]
                               [--identity-epoch-json IDENTITY_EPOCH_JSON]
                               [--t1-bindings-json T1_BINDINGS_JSON]
                               [--runs-root RUNS_ROOT] [--ledger LEDGER] [--head-pin HEAD_PIN]
                               [--slot-count SLOT_COUNT] [--allow-slot-count]
                               [--slot-count-ruling REF] [--out OUT] [--verify] [--check]
```

The two new round-4 refusals (`slot_count > MAX_DECLARED_SESSION_SLOTS`, and the parsed identity-epoch/T1 JSON validation) are covered by `test_a_slot_count_above_the_ledger_ceiling_refuses`, `test_the_identity_epoch_is_parsed_not_only_hashed` (six rejected shapes, all rc 2) and `test_the_t1_bindings_file_must_be_a_json_object`, all green above. Region check:

```
$ python3 scripts/gen_derivation_night.py --check   → EXIT 0
PASS generated derivation-night wrapper region matches
```

---

## (3) S6 contract sentences vs the merged parser — **ALL SIX MATCH**

`docs/contracts/calibration_ledger.md:159-166` names `--preregistration`, `--preregistration-sha256`, `--registration-session-id`, `--nights-ruling`, `--slot-count-ruling` on `prepare-candidate`, and `--preregistration` on `check`. Checked against the merged parser (`prepare-candidate --help`, `check --help`):

| Sentence names | In merged parser | Semantics match |
|---|---|---|
| `prepare-candidate --preregistration` (the file) | yes, `required` | yes |
| `prepare-candidate --preregistration-sha256` (its pinned digest) | yes, `required=True` | yes — `:1132-1139` refuses on digest mismatch |
| `prepare-candidate --registration-session-id` (repeated, one per night) | yes, `action="append"` | yes |
| `prepare-candidate --nights-ruling` | yes | yes — `:1191` `len(session_ids) != 3 and not args.nights_ruling` |
| `prepare-candidate --slot-count-ruling` | yes | yes — `:1197-1204` per-session `declared_slots != 12` |
| `check --preregistration` (optional, appends only) | yes, `default=None` | yes — executed in 2b |

The commit message's own marker `[flag names to confirm at merge]` (`6c581738`) was resolved by `6e3d79ff`; the resolution is correct.

---

## (4) Scope / rule 11 — ONE FLAG

### should_fix S-1 — ruled text edited in place in `docs/decision_log.md`

`docs/decision_log.md:6653-6663` (cold gate 46 clause **V7**) was rewritten in place by `6c581738` (S6 round 6): "inherited ceiling" → "predecessor ceiling", plus the added clause "carried on the successor's generation row as `predecessor_ceiling_s`". The *substance* is unchanged — the pre-existing text already defined the inherited ceiling as the predecessor generation's `maximum_budgetable_drift_s` — but this is an edit to the body of a RULED clause rather than a dated addendum. Rule 11 reserves amendment of ruled text; a terminology correction inside a ruling is exactly the class the addendum mechanism exists for (and cold gate 46 already carries dated addenda A-2/A-4/A-7/11, so the mechanism is live and cheap).

**Magistrate call required**, not a lieutenant one. Recommendation: convert to an A-numbered dated addendum and restore the V7 body, or ratify the in-place edit explicitly.

Everything else in the range is inside the seats' own files: `configs/calibration/preregistration_…md`, `docs/contracts/{calibration_ledger,powermetrics_fiducial}.md` (S6); `scripts/issue_calibration_acceptance_generation.py` + its tests (S4); `joulewise/calibration_bracketing.py` + `tests/test_calibration_bracketing.py` + `tests/fixtures/epoch_bootstrap/build.py` (S3); `scripts/gen_derivation_night.py`, `scripts/night_chains/calibration_derivation_only.zsh`, `tests/test_gen_derivation_night.py`, the generated `SHAKEDOWN-G2-RUNSHEET.md` region (S7); `tests/test_validate_powermetrics_fiducial_derivation_only.py` docstrings only (S1). No production file outside the epoch lane was touched.

---

## (5) Line-pin rot — **CLEAN, and net-negative**

```
$ git diff d9612e68..HEAD | grep -E '^\+' | grep -E '\.(py|zsh|md):[0-9]+'
(no output)
```

**Zero** new `<file>:<digits>` citations in added lines. The range REMOVES two:

- `scripts/issue_calibration_acceptance_generation.py` `derivation_sha256` docstring: `(':660', ':764')` → named-symbol reference to `_canonical_sha256`.
- `tests/test_validate_powermetrics_fiducial_derivation_only.py:728-731`: `joulewise/calibration_bracketing.py:676-687` → `joulewise.calibration_bracketing._valid_acceptance_bound` by symbol.
- The chain header replaced its five `reserve_calibration_window_bracket.py:82-106` / `:167-186` / `:1771` / `:1946` / `:1759-1761` pins with quoted anchor text.

Three PRE-EXISTING pins survive in `scripts/gen_derivation_night.py`'s docstrings (`run_night.py:414-444`, `:1576-1610`, `:947-955`). I spot-checked all three at HEAD; each still resolves to the code it claims (env assignment block, chain-sidecar digest comparison, deadman `07:00` roll-forward). Not rot, and not introduced here — noted only so a later sweep does not rediscover them. Minor: the module docstring says `run_night.py:414-444` while the emitted wrapper header says `:430-444` for the same fact; both pre-date `d9612e68`.

---

## Severity-tiered findings

### should_fix

**S-1 — ruled text edited in place.** `docs/decision_log.md:6653-6663`, commit `6c581738`. See §4. Rule 11: magistrate call.

**S-2 — the two homes now contradict each other on the 210-minute figure.** The same commit corrected the pre-registration (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:113-123`) to say the 210 min figure "is not a window at all: it is the install span 03:00–06:30", but cold gate 46 clause **V4** at `docs/decision_log.md:6647-6650` still reads:

> "The schedule fits with margin: 600 s settle + 11 × 600 s cadence + one ~8 min capture is 128 of **a 210 min window**."

That is precisely the conflation the pre-registration edit was made to retire, left standing in the ruling the pre-registration implements. Reproduce:
```
$ grep -n "128 of a 210 min window" docs/decision_log.md      → 6649
$ grep -n "is not a window at all" configs/calibration/preregistration_d079_epoch_25g83_rev1.md
```
Fixing it is an addendum, not an in-place edit (see S-1) — the two findings should be resolved together.

**S-3 — contract sentence names the wrong home for the powermetrics pin.** `docs/contracts/calibration_ledger.md:142-147`, "Epoch match" bullet:

> "`prepare-candidate` refuses when the pre-registration's recorded `/usr/bin/powermetrics` SHA-256, **or its recorded `os_build`, differs from the target identity epoch the registration declares**."

`powermetrics_sha256` is **not** an identity-epoch field. The six `IDENTITY_EPOCH_FIELDS` (`joulewise/calibration_ledger.py:110-117`) are `os_build`, `hardware_model`, `power_policy`, `sampling_interval_ms`, `estimator_revision`, `pulse_protocol_id`. The merged code is correct and in fact stronger than the sentence: `os_build` is compared against the target epoch (`scripts/issue_calibration_acceptance_generation.py:1213`), while `powermetrics_sha256` is compared against the **T1 bindings of every observation in the corpus** (`:1209-1212`, `observation.t1_bindings.get("powermetrics_sha256")`, required to be the singleton `{registered_powermetrics}`). Under the writing standard this is a first-use/accuracy defect: a reader replicating from the sentence would look for the pin in the wrong record. Rewrite the bullet to name the two homes separately. No code change needed.

### nit

**N-1 — the three-nights fence counts flag repetitions, not distinct nights.** `scripts/issue_calibration_acceptance_generation.py:1153` is `session_ids = tuple(args.registration_session_id)` with no uniqueness check anywhere before the fence at `:1191` (`len(session_ids) != PREREGISTERED_NIGHT_COUNT`); `:1234` then collapses to `registration = set(session_ids)`. So `--registration-session-id S --registration-session-id S --registration-session-id S` satisfies a fence whose stated purpose (`docs/contracts/calibration_ledger.md:148-153`) is that "a campaign that quietly ran a fourth night … is a different experiment". Read-verified, not executed (building the ledger fixture exceeded the window). **Not exploitable to issuance**: one night declares at most `MAX_DECLARED_SESSION_SLOTS` slots, far below the 19/17 corpus floor, and the emitted row's duplicated `registration_session_ids` (`:1419`) would fail `_registered_generation_row_is_complete`'s `len(set(session_ids)) == len(session_ids)`. Suggested one-line cure at the fence: compare `len(set(session_ids))`, or refuse duplicates at `:1153`.

**N-2 — the chain's rc-1 branch assumes rc 1 means "row finalized".** `scripts/night_chains/calibration_derivation_only.zsh:208-215, 232-236` states "The writer exits 1 when the capture's disposition is not 'valid' … the ledger row is FINALIZED either way", and the `else` branch comments "Anything else is a refusal (`emit_refusal` exits 2) or a crash". The refusal half is verified — all 74 `REFUSAL_INVENTORY` entries carry `process_exit == 2` (executed: `process_exit tally {2: 74}`) — but `scripts/validate_powermetrics_fiducial.py:2537` is `raise SystemExit(main())` with **no top-level exception guard**, so an uncaught exception in `main()` also exits **1**, is logged `disposition=non-valid`, and the night proceeds over an **unfinalized** slot. Blast radius is bounded to one further slot: the next capture hits the writer's `slot != expected_slot` refusal (`:1348`, `expected_slot = session.next_slot` at `:1326`) and exits 2, stopping the chain with the session open — which is the desired end state, just one settle later. Either narrow the header's claim or make the `rc == 1` branch conditional on the writer having emitted its JSON payload.

**N-3 — `_identity_epoch_value_ok` admits floats.** `scripts/gen_derivation_night.py:181-188` accepts `int | float` (bool excluded) for the non-string epoch fields; the comment justifies it for `sampling_interval_ms`, which is an integer in every issued acceptance and in the test fixture. A float `sampling_interval_ms` would clear the desk check and be discovered later. Tighten to `int` if the ledger's own rule is `int`.

### observation (no action)

- `check --preregistration` parses **both** pins but compares only the powermetrics one (`_, registered_powermetrics = preregistration_epoch_pins(text)`, `:296`). This matches the flag's own help text and loses nothing, because the watch table already prints the `os_build` MISMATCH row independently. Not a finding.
- `tests/fixtures/epoch_bootstrap/build.py:45-48` now bakes the **real** machine's `powermetrics_sha256` (`b762e5bf…30c5`) into the fixture. Deliberate and documented; it does couple the fixture to the current binary, so a future powermetrics update will require a fixture edit alongside the pre-registration.
- `_PREREGISTRATION_OS_BUILD = re.compile(r"os_build:\s*([A-Za-z0-9._-]+)")` uses `\s*`, which spans newlines; a pre-registration with a bare `os_build:` line followed by an unrelated token would capture that token. `findall` + `set` + exactly-one-match makes the failure mode a refusal in practice. Not worth a fix.

---

## Bottom line for the magistrate

The engineering in rounds S4 r5–r6, S7 r3–r4, S3 r6, S1 r3 and S6 r6 is sound: every new refusal I could reach is fail-closed, the six issued rows and the ordinary writer path are untouched, blindness still runs first, the watch is byte-identical without its new flag, all six contract-named flags exist in the merged parser, and the range removes more line pins than it adds (it adds none).

The one thing a lieutenant must not close alone is **S-1**: `6c581738` amended cold-gate-46 ruled text in place. **S-2** (the 210-min contradiction that ruling now carries) needs the same addendum, so both should go to the magistrate as one item.

