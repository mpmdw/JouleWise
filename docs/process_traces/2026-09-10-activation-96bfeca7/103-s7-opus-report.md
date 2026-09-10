# 103 — Seat S7 report: the derivation-night chain wrapper generator

Worktree `/Users/edr/code/JouleWise-wt-s7-night-wrapper`, branch
`feat/2026-09-10-epoch-s7-derivation-night-wrapper`, base HEAD `aea38b1a`.
No git state changes; no captures; no `[QUIET-MAC]` work; no sudo.
Every scout-cited line was re-read in this worktree before being relied on.

## 1. What landed

### `scripts/gen_derivation_night.py` (new, 533 lines)

Emitter for the plan-pinned wrapper. Emit mode is `--plan <night plan>` plus the
five required inputs; with no `--plan` it renders/`--check`s the reviewed
example region in the runsheet.

| Piece | Where | What it does |
|---|---|---|
| `render_wrapper` | `:137-250` | Pure function, spec → wrapper bytes. Routing preamble (mirrors the runsheet's reviewed "Emitted routing and common variables" fence, runsheet `:1534-1598`), literal `export` block, frozen-plan re-derivation, tracked-chain digest check, `exec` + per-slot bindings. |
| `emit` | `:258-276` | Writes the wrapper `0o755`, its own sidecar `<out>.sha256` in the strict `shasum` form `run_night._sidecar_digest` accepts (`scripts/run_night.py:97-105`), and the tracked-chain sidecar `<out>.chain-source.sha256`. |
| `build_spec` | `:284-391` | Validates the plan through the driver's own `NightPlan.from_mapping` (never invents field names), resolves defaults, and raises every refusal. |
| `render_region` / `replace_region` / `main --check` | `:427-470`, `:502-543` | The reviewed example region + drift tripwire. |
| Refusals | `GenerationRefusal` `:68`, checks at `:82-91` (census), `:278-282` (absolute paths), `:296-322` (slot count, dead-man, out path/sidecar vs plan) | Non-zero exit 2 with a printed reason; nothing is written. |

The wrapper it emits, in order:

1. routing preamble — `MEASUREMENT_ROOT` present/absolute/control-char-free,
   `MEASUREMENT_HEAD` a 40-hex SHA-1, then three equality checks against the
   literals this wrapper was frozen with (`NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`,
   `MEASUREMENT_HEAD`), then `git -C … rev-parse HEAD` equality, then
   `export REPO/PY/PYTHONPATH/MEASUREMENT_CHECKOUT` exactly as G2-a derives them;
2. the literal `export` block (13 required + 6 pinned knobs, §2);
3. `test -f` on `$PLAN`, `$IDENTITY_EPOCH_JSON`, `$T1_BINDINGS_JSON`, then
   in-wrapper re-derivation of the frozen plan's `plan_id` (`/usr/bin/jq -er`)
   and SHA-256 (`/usr/bin/shasum … | /usr/bin/awk`), each compared to its
   arm-time literal — the G2-a two-liner (`gen_g2_phase_d.py:250-252`) turned
   into a refusal instead of an assignment;
4. `( cd "$REPO" && /usr/bin/shasum -a 256 --status -c <sidecar> )` against the
   emitted `<out>.chain-source.sha256`, whose path column is the clone-relative
   `scripts/night_chains/calibration_derivation_only.zsh`;
5. `exec /bin/zsh "$REPO/scripts/night_chains/calibration_derivation_only.zsh"`
   followed by 24 repeated flags (12 `--slot-attempt-id`, 12
   `--slot-custody-locator`; 48 argv tokens) for `d01..d12`.

`exec`, not `source`: the chain resolves `REPO` from its own `$0`
(`calibration_derivation_only.zsh:40-41`).

### `scripts/night_chains/calibration_derivation_only.zsh` (header only)

`:2` SKELETON banner deleted; `:16-37` rewritten from "UNLANDED SURFACE" to
"LANDED SURFACE, re-read at this HEAD" with the flags' current file:line
(`reserve_calibration_window_bracket.py:82-106`, `:167-186`;
`validate_powermetrics_fiducial.py:1771`, `:1946`, and `--slot` at `:1759-1761`,
which is now free-form "exact predeclared slot name", so `d01..dNN` are
accepted); the "lead's call" open question resolved in favour of the wrapper;
`:36` "future frozen plan" → "plan-pinned wrapper". **No executable byte
changed** — verified by `zsh -n` and by the 91-test chain suite passing
unchanged.

### `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`

One new section appended at EOF, `:1612-1740`, holding the generated region
between `<!-- BEGIN GENERATED: derivation-night-wrapper -->` and its END marker:
the arm command and one fully rendered example wrapper from placeholder
coordinates plus the **live** digest of the tracked chain. Appending at EOF is
what keeps `gen_g2_phase_d.py`'s pinned fence inventory `[(1534,1598),(328,351),
(374,385),(389,564),(575,587)]` (`gen_g2_phase_d.py:124`) and its runbook
`PINNED_ANCHORS` unmoved; `gen_g2_phase_d.py --check` still prints PASS, and a
test pins that.

### Tests

- `tests/test_gen_derivation_night.py` (new): 18 tests, 3.2 s.
- `tests/test_issue_calibration_acceptance_generation.py`:
  `test_chain_source_carries_no_pack_probe_or_git_step` (`:556`) now asserts the
  SKELETON banner is **absent** and the wrapper statement present;
  `test_chain_header_pins_its_hand_written_and_landed_flag_surface` (`:578`,
  renamed) pins the landed-surface paragraph **and re-checks the writer's CLI
  source**, so the header cannot go stale silently again;
  `test_chain_forwards_its_argv_verbatim_into_the_reservation` (`:606`) is new.
  `run_chain` gained one keyword, `argv` (`:352`, `:395`), defaulting to `None`
  (behaviour unchanged for every existing caller) —
  the minimum needed to drive the chain with a non-empty `"$@"`, which nothing
  did before. Flagged as a scope judgment call (§6).

## 2. Plan-field → wrapper-variable table

The night plan's key set is closed and exact (`joulewise/night_gate.py:112-127`)
and there is **no `night_root` key** — the night root is `custody_root`.

| Wrapper `export` | Source | Note |
|---|---|---|
| `SESSION_ID` | `--session-id` | input, never minted; every attempt id derives from it |
| `WINDOW_ID` | `--window-id`, default plan `plan_id` | |
| `PLAN_ID` | `plan_id` of `--calibration-plan` **file** | re-derived in-wrapper by `jq` and compared |
| `PLAN_SHA256` | SHA-256 of `--calibration-plan` bytes | re-derived in-wrapper by `shasum` and compared |
| `PLAN` | `--calibration-plan` (absolute) | the frozen **calibration** plan, not the night plan |
| `EVIDENCE_ROOT_ID` | `--evidence-root-id` (required) | no defensible default; not invented |
| `RUNS_ROOT` | `--runs-root`, default `<custody_root>/runs` | G2-a parity (runsheet `:1558`) |
| `WINDOW_CUSTODY_ROOT` | plan `custody_root` | G2-a parity (runsheet `:1557`) |
| `CALIBRATION_LEDGER` | `--ledger`, default `<measurement_root>/runs/calibration_observation_ledger.jsonl` | runsheet `:1573` |
| `LEDGER_HEAD_PIN` | `--head-pin`, default `<measurement_root>/configs/calibration/calibration_ledger_head.json` | runsheet `:1574` |
| `IDENTITY_EPOCH_JSON` | `--identity-epoch-json` (required) | see §7 open question 1 |
| `T1_BINDINGS_JSON` | `--t1-bindings-json` (required) | see §7 open question 1 |
| `WINDOW_END_EPOCH_S` | `int(plan.t0_epoch_s + plan.window_max_s)` | integer literal (chain's `<->` guard, `:69-75`) |
| `SLOT_COUNT` | `--slot-count`, default 12 | pinned so the flag list and the loop can never disagree (scout Q4) |
| `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S` | 600 / 600 / 480 | pinned, not inherited (§6 decision D5) |
| `SLEEP`, `DATE` | `/bin/sleep`, `/bin/date` | pinned, not inherited (§6 decision D5) |
| `REPO`, `PY`, `PYTHONPATH`, `MEASUREMENT_CHECKOUT` | derived from `$MEASUREMENT_ROOT` | the G2-a preamble, verbatim in shape |
| plan `measurement_root` / `measurement_head` / `plan_id` | equality checks | a wrapper frozen for one plan refuses another |
| plan `chain_path` / `chain_sha256_path` | `--out` default and validation | refuse unless `--out == chain_path` and `chain_sha256_path == chain_path + ".sha256"` |
| plan `receipt_class` | refusal | `TRANSACTION_PACK` is refused: a derivation night is `DIAGNOSTIC_NO_PACK` |

## 3. Cut table — every test, its mutation, and the kill

Each cut applied to production source, ONE test run, source restored and
SHA-256-verified identical. All twelve killed their test (rc 1).

| # | Cut | Test | Result |
|---|---|---|---|
| 1 | drop the `WINDOW_END_EPOCH_S` export | `…test_every_required_chain_variable_is_exported_with_its_plan_value` | Ran 1, FAILED (failures=1), restored |
| 2 | `int(t0 + window_max_s)` → `int(window_max_s)` | `…test_window_end_is_the_integer_sum_of_t0_and_window_max` | Ran 1, FAILED (1), restored |
| 3 | dead-man check → `if False:` | `…test_a_plan_that_overruns_the_dead_man_refuses` | Ran 1, FAILED (1), restored |
| 4 | census loop → `for substring in ():` | `…test_a_census_substring_anywhere_in_the_night_refuses` | Ran 1, FAILED (2 subtests), restored |
| 5 | delete the `shasum -c` line from the rendered wrapper | `…test_the_wrapper_refuses_when_the_tracked_chain_bytes_change` | Ran 1, FAILED (1), restored |
| 6 | delete the in-wrapper frozen-plan digest comparison | `…test_the_wrapper_refuses_a_swapped_frozen_plan` | Ran 1, FAILED (1), restored |
| 7 | bind only slot `d01` | `…test_twenty_four_binding_flags_satisfy_the_real_reservation_parser` | Ran 1, FAILED (1), restored |
| 8 | sidecar → `SHA256 (name) = digest` (BSD tag form) | `…test_the_sidecar_is_the_strict_form_the_driver_accepts` | Ran 1, FAILED (1), restored |
| 9 | put `datetime.now()` in the wrapper header | `…test_two_emissions_of_one_plan_are_byte_identical` | Ran 1, FAILED (1), restored |
| 10 | slot-count guard → `if False:` | `…test_a_slot_count_other_than_the_pre_registered_twelve_refuses` | Ran 1, FAILED (1), restored |
| 11 | delete `"$@" \` from the chain's reservation (`:155`) | `DerivationChainSkeletonTests.test_chain_forwards_its_argv_verbatim_into_the_reservation` | Ran 1, FAILED (errors=1), restored |
| 12 | re-add a `# SKELETON:` banner to the chain | `DerivationChainSkeletonTests.test_chain_source_carries_no_pack_probe_or_git_step` | Ran 1, FAILED (1), restored |

The end-to-end launch test (`…test_the_wrapper_reaches_the_reservation_with_all_bindings`)
is killed by cuts 1, 5, 6 and 7 as well; it is the integration lens, not a
single-defect lens.

**How the launch test works.** A `tempfile` fixture builds a real one-commit git
clone containing only the tracked chain and a fake `.venv/bin/python`; the
wrapper is then run exactly as `run_night._run_chain_once` runs it — argv
`["/bin/zsh", <wrapper>]`, `stdin=DEVNULL`, and an environment of **only**
`PATH` plus the four driver variables (`run_night.py:430-444`, pinned by
`tests/test_run_night.py:348-380`). The fake interpreter records each argv and
exits 3 on the reservation, so the chain stops there — the test never sleeps
600 s, never captures, and never touches a real ledger. It asserts the readiness
call comes first with `--phase pre-reserve`, then the reservation with
`--slot-count 12` and twelve of each binding flag, ending in `--execute`.

## 4. Test runs (rc captured in a variable)

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night
Ran 18 tests in 3.171s
OK                                                        rc=0

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation
Ran 91 tests in 93.130s
OK                                                        rc=0

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_gen_derivation_night \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_run_night tests.test_docs_freshness
Ran 222 tests in 84.864s
OK                                                        SUITE_RC=0

$ PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q \
    scripts/gen_derivation_night.py tests/test_gen_derivation_night.py \
    tests/test_issue_calibration_acceptance_generation.py
compileall_rc=0

$ python3 scripts/gen_derivation_night.py --check
PASS generated derivation-night wrapper region matches                rc=0
$ python3 scripts/gen_g2_phase_d.py --check
PASS generated Phase D matches pinned runbook bytes                   rc=0
$ /bin/zsh -n scripts/night_chains/calibration_derivation_only.zsh     rc=0
```

## 5. Footprint

```
$ git status --short
 M docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
 M scripts/night_chains/calibration_derivation_only.zsh
 M tests/test_issue_calibration_acceptance_generation.py
?? scripts/gen_derivation_night.py
?? tests/test_gen_derivation_night.py
```

Exactly the WRITE_SCOPE. No other worktree, no canonical checkout, no
`~/night-custody` path was written. `docs/phase_2/window_runbook.md` was read
only — the region went to the runsheet (§6, D2).

## 6. Decisions

- **D1 — separate generator, not a mode of `gen_g2_phase_d.py`.** Extending it
  would shift its `PINNED_ANCHORS` line numbers and couple two nights'
  emitters (scout Q3). Separate file, same patterns.
- **D2 — the region lives in the runsheet, not the runbook.** The runsheet is
  where `gen_g2_phase_d.py` *writes* generated regions; the runbook is where it
  *reads* pinned source. This region is generated, so it mirrors the runsheet
  side. Appended at EOF so no pinned anchor or fence line number moves.
- **D3 — the wrapper is rendered from Python literals, not extracted from a
  markdown fence.** Every line of a derivation wrapper is parameterised by the
  plan, so there is no reviewable static source to extract; the reviewable
  artifact is the *rendered example* in the region, and `--check` is the
  tripwire. The example embeds the live tracked-chain digest, so editing the
  chain without re-running the emitter fails `--check`.
- **D4 — `PLAN_ID`/`PLAN_SHA256` are literals AND re-derived in the wrapper.**
  The brief allowed either. Literal-only would trust a file swapped after
  arming; derive-only would lose the arm-time freeze. Both, compared, costs six
  lines of zsh and refuses in either direction.
- **D5 — the wrapper pins `SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`,
  `SLOT_CAPTURE_BUDGET_S`, `SLEEP` and `DATE` as well as the 13.** The driver
  hands the chain `os.environ.copy()` (`run_night.py:426`), so any of these
  left in the arming operator's shell would silently retime the night — an
  inherited `SLEEP` pointing at a fake clock would skip the settle entirely.
  The chain's own defaults are unchanged; the wrapper just states them.
- **D6 — the wrapper refuses another plan's coordinates.** Three equality
  checks (`NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD`) mean a
  wrapper emitted for night A cannot be pinned by night B's plan and run
  silently on B's clone.
- **D7 — `--out` defaults to the plan's `chain_path` and refuses any other
  value**, and `chain_sha256_path` must be `chain_path + ".sha256"`. The plan
  and the emitted artifact cannot disagree about where the wrapper is.
- **D8 — census refusal covers every emitted literal**, not only the three the
  brief names (session id, night root, out path): `pgrep -lf` matches whole
  command lines, and the ledger path, runs root and frozen-plan path all appear
  in the chain's child argv. The refusal names the offending field.
- **D9 — the tracked-chain sidecar uses a clone-relative path column** and the
  wrapper `cd "$REPO"` before `shasum -c`, so the check follows the clone rather
  than the arm machine's absolute layout.
- **D10 — scope judgment call:** `run_chain` in
  `tests/test_issue_calibration_acceptance_generation.py` gained one optional
  `argv` keyword (default unchanged). Without it the required `"$@"` test cannot
  drive the chain with a non-empty argv without duplicating the whole 40-line
  harness. Every pre-existing test is byte-for-byte unaffected in behaviour (91
  tests still OK). Flagging rather than assuming.

## 7. Open questions for the arm checklist

1. **Where do `identity_epoch.json` and `t1_bindings.json` come from?**
   Unresolved. Runbook 68 (record 12 of this trace) is **not present** in the
   bookkeeping worktree, so I could not verify its producer; the G2-a analogue
   is `generate_g2a_probe_inputs.py bind-window` (runsheet `:378-385`), and the
   new epoch issuer is the obvious candidate for the derivation night. The
   wrapper therefore takes both as **explicit required inputs** and only checks
   that they are absolute and present at run time. **The arm checklist must name
   their producer and their custody location before the first arm.**
2. **The clean-tree check is still procedure, not code.** The gate verifies
   `git rev-parse HEAD == measurement_head` (`night_gate.py:1006-1029`) but
   nothing excludes uncommitted edits in the clone. The wrapper's `shasum -c`
   now closes this for **the capturing chain specifically** (a dirty chain
   refuses before the reservation), but not for the rest of the clone —
   `recover_calibration_ledger.py`, `reserve_calibration_window_bracket.py` and
   `validate_powermetrics_fiducial.py` are still bound only by HEAD. The arm
   must run `git status --porcelain` on the measurement clone and record it, as
   the G2-a clone-cut record does.
3. **`EVIDENCE_ROOT_ID` has no derivable default.** It is a required flag; the
   arm checklist must state the value and where it is registered.
4. **One wrapper per night** (three nights, three session ids, three plans) —
   the generator refuses to reuse one wrapper across plans (D6), so the arm
   emits three. This matches the frozen-bytes model; confirm it is what the
   campaign wants.
5. **Custody-locator convention unverified against the writer.** The wrapper
   emits `$RUNS_ROOT/instrument_validation/${SESSION_ID}-dNN`, matching the
   chain header `:30-31` and the chain's `--output-root` (`:198`), but I did not
   verify the writer's directory-naming rule; scout question 5 stands, and a
   mismatch is a mid-night refusal.
6. **`ACCEPTANCE-EPOCH-25G83-01` still blocks any arm.** Nothing here authorizes
   a night; this is desk work only.

---

# Fix round 1 (2026-09-10, on top of 94e4fc89)

Both refuter reports read first (104 execution, 105 contract). Same worktree,
same WRITE_SCOPE, no git state changes. Every item below has a defect-shaped
test and a mutation cut (single test, `Ran 1`, source SHA-256-restored,
`PYTHONDONTWRITEBYTECODE=1`).

## Blockers

**1. F1 / B-1 — the chain digest is now a LITERAL in the wrapper's bytes.**
`render_wrapper` emits
`[ "$(sha256_of "$REPO/scripts/night_chains/calibration_derivation_only.zsh")" = '<hex>' ] || route_refuse …`
using a `sha256_of()` helper it also defines; the unpinned
`shasum --status -c <sidecar path>` check is gone. The false comment is
replaced by a true one: *the plan pins the wrapper's digest, and the capturing
chain's digest is a literal in those bytes, so the plan-pinned digest moves
whenever the capturing chain moves.* The third file
(`<wrapper>.chain-source.sha256`) is still emitted but is now **advisory only**
— labelled as such in the wrapper's comment, in `emit`'s docstring, and in the
generated region's file table.
Tests: `test_the_chain_digest_is_a_literal_in_the_wrapper_bytes` (edit the
clone's chain → re-emit → **wrapper bytes must change**, and the new digest must
appear in them) and `test_rewriting_the_advisory_sidecar_cannot_move_the_pin`
(104 F1(a)'s exact attack: edit the chain, rewrite the sidecar, launch → refusal
before `exec`, `calls == []`; then delete the sidecar entirely and confirm the
night still runs — proof that nothing trusts it).

**2. B-2 — a window that cannot hold the programmed span is refused.**
`programmed_span_s(n) = settle + (n-1)·cadence + budget` (600 + 11×600 + 480 =
**7680 s** for twelve) plus `PRE_SETTLE_ALLOWANCE_S = 300` for the chain's
pre-settle preflight/readiness/reservation and the driver's own pre-launch work.
The refusal states both numbers:
`window_max_s 3600 < required 7680 + 300 = 7980 s: the programmed span of 12
slots is settle 600 + 11 x cadence 600 + budget 480, plus the pre-settle
allowance; lengthen the window rather than shortening the schedule`.
`--allow-slot-count` recomputes the requirement rather than bypassing it.
Tests: `test_a_window_too_short_for_the_programmed_span_refuses` (3600 refuses,
7979 refuses, **7980 emits**, 9000 emits) and
`test_the_span_constants_are_the_chains_own_defaults`, which resolves each
constant against the chain's own anchor line (`SETTLE_S="${SETTLE_S:-600}"` etc.)
so the arithmetic can never quietly diverge from the file it describes.

## Should-fix

**3. F3 — the chain is digested from `plan.measurement_root`**, i.e. the clone
the night runs, never `REPO_ROOT` (the checkout the generator happens to execute
in). Test: `test_the_chain_is_digested_from_the_measurement_clone` makes the
clone's chain differ from the generator's, asserts the wrapper carries the
clone's digest and **not** the generator's, and then launches it successfully.

**4. F4 — every in-wrapper refusal prints `FAIL <reason>`.** The three bare
`test -f` lines became `[ -f "$X" ] || route_refuse '<name> is missing'`.
Test: `test_every_in_wrapper_refusal_prints_a_reason` asserts, for each of the
three files, `rc == 1`, `stderr.strip() == "FAIL <reason>"` exactly, and nothing
ran.

**5. S-1 — `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON` carry literal SHA-256
pins**, compared in-wrapper like `PLAN`. Their bytes are copied verbatim into
every slot record by the reservation, so a swapped file silently changes what
every capture is bound to. Test: `test_modified_identity_or_t1_bytes_refuse`.

**6. S-2 — all chain citations are anchor texts, not line numbers.**
`CHAIN_ANCHORS` holds nine exact chain lines; the module docstring, the export
block's comment, and the two citations baked into every night's artifact quote
them. Test: `test_every_chain_citation_resolves_to_a_real_chain_line` requires
each anchor to occur **exactly once** in the chain, requires the generator source
to contain no `calibration_derivation_only.zsh:<n>` citation at all, and checks
the two anchors that reach the emitted wrapper.

**7. S-4 — the region documents the third file and the arm order.** New
subsections: a three-row file table (wrapper / plan-pinned sidecar / ADVISORY
ONLY sidecar, each with its role) and a five-step arm order — cut the clone at H
and record `git status --porcelain` → author the plan → generate → re-emit and
assert byte equality → `zsh -n` and install — plus a paragraph enumerating every
generation-time refusal. First-use test applied: "wrapper", "night root",
"programmed span", "dead-man", "advisory" and "`zsh -n`" are each glossed in
plain words at first use. Test:
`test_the_region_documents_the_third_file_and_the_arm_order`.

## Nits

**8a. F5 — the pack guard became a receipt-class ALLOW-LIST** (`!=
DIAGNOSTIC_NO_PACK`). The old form was, as 104 found, unreachable for the plan
shape a reviewer would try, because `NightPlan.from_mapping` refuses a pack plan
without `pack_night` first; the allow-list is reachable and now tested through a
`REHEARSAL_STUB` plan (a class whose chain the driver never runs at all), which
also closes 105's N-1. Test: `test_a_non_diagnostic_receipt_class_refuses`.

**8b. F6 — `--allow-slot-count` now requires `--slot-count-ruling <ref>`**,
prints `DEPARTURE this night declares N slots, NOT the pre-registered 12
(cold-gate ruling 46 §R-c); authority: <ref>` to stderr, and writes a
`DEPARTURE FROM THE PRE-REGISTRATION` block naming the ruling into the emitted
wrapper's header. Test:
`test_departing_from_twelve_slots_requires_a_named_ruling`.

**Not done, by instruction:** S-3 (the runbook draft's plan table) is the
writer's revision and was not touched.

## Fix-round cut table

| # | Cut | Test | Result |
|---|---|---|---|
| R1 | `chain_sha256=` sha256(chain) → `"0"*64` | `test_the_chain_digest_is_a_literal_in_the_wrapper_bytes` | Ran 1, FAILED (1), restored |
| R1b | neuter the in-wrapper chain-digest comparison | `test_rewriting_the_advisory_sidecar_cannot_move_the_pin` | Ran 1, FAILED (1), restored |
| R2 | window-fit check → `if False:` | `test_a_window_too_short_for_the_programmed_span_refuses` | Ran 1, FAILED (1), restored |
| R3 | digest the chain from the generator's own repo | `test_the_chain_is_digested_from_the_measurement_clone` | Ran 1, FAILED (1), restored |
| R4 | restore the silent `test -f "$PLAN"` | `test_every_in_wrapper_refusal_prints_a_reason` | Ran 1, FAILED (1), restored |
| R5 | drop the identity-epoch digest pin | `test_modified_identity_or_t1_bytes_refuse` | Ran 1, FAILED (2 subtests), restored |
| R6 | rot the `forward_argv` anchor text | `test_every_chain_citation_resolves_to_a_real_chain_line` | Ran 1, FAILED (1), restored |
| R7 | allow-list → old pack-only guard | `test_a_non_diagnostic_receipt_class_refuses` | Ran 1, FAILED (1), restored |
| R8 | ruling requirement → `if False:` | `test_departing_from_twelve_slots_requires_a_named_ruling` | Ran 1, FAILED (1), restored |
| R9 | delete the ADVISORY ONLY row from the region | `test_the_region_documents_the_third_file_and_the_arm_order` | Ran 1, FAILED (2), restored |

10/10 killed. Two pre-existing tests needed their fixtures widened, not their
assertions weakened: `test_window_end_is_the_integer_sum_of_t0_and_window_max`
used a 600 s window (now 8000 s, still with the fractional t0 the integer cast
must survive) and `test_a_slot_count_other_than_the_pre_registered_twelve_refuses`
now passes `--slot-count-ruling`.

## Fix-round runs and footprint

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_gen_derivation_night tests.test_issue_calibration_acceptance_generation \
    tests.test_run_night tests.test_docs_freshness
Ran 233 tests in 76.345s
OK                                                SUITE_RC=0

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night
Ran 29 tests in 4.797s
OK                                                FINAL_GEN_RC=0   (final bytes)

compileall_rc=0
PASS generated derivation-night wrapper region matches        d_rc=0
PASS generated Phase D matches pinned runbook bytes           g2_rc=0

$ git status --short
 M docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md
 M scripts/gen_derivation_night.py
 M tests/test_gen_derivation_night.py
```

`tests/test_issue_calibration_acceptance_generation.py` and
`scripts/night_chains/calibration_derivation_only.zsh` needed no fix-round edit;
the chain's bytes are unchanged from 94e4fc89, so the digest the wrapper now
bakes in is the reviewed one.

## What the fix round did NOT change

- The attestation shape (plan → wrapper → chain) and the `exec`-with-24-bindings
  mechanism are unchanged; B-1 changed *where the chain digest lives*, not the
  design.
- No driver, gate, schema or chain behaviour was touched.
- Open questions 1 (identity-epoch / T1 provenance), 2 (clean tree) and 3
  (`EVIDENCE_ROOT_ID`) still stand for the arm checklist. 105 CLOSED my open
  question 5 (custody locator): the writer computes
  `out_dir = output_root / attempt_id` in bracket mode, which is byte-identical
  to the locator the wrapper declares — no mid-night mismatch. The clean-tree
  requirement is now also written into the region's arm order as step 1.
