# 141 — PR #316 contract-lens + final-head fresh-eyes review (gate ledger rows 2, 6, 10)

- Branch: `feat/2026-09-10-derivation-night-inputs` @ `7a0511d6a5b214175de29ddb76835f16987702e2`
- Base: `main` @ `d18bc2b3`
- Tree: `/Users/edr/code/JouleWise-wt-s8-night-inputs` (read-only; `git status --porcelain` empty at entry and exit)
- Reviewer: Opus 5, contract lens + final-head fresh eyes
- Prior evidence consumed: execution refuter 136 (F1/F2 fixed at `9854c961`), records 134/135/137, lead diff gate 138

## VERDICT: **MERGEABLE AFTER FIXES**

**Row 2 (contract): PASS.** Every clause checked against executed behaviour matched — all seven
refusals reproduced verbatim, the three printed lines confirmed, §0.3 matches record 134, all 38
§7 symbols resolve, all arithmetic ties to the live constants.
**Row 10 (fresh eyes): PASS.** Exact declared scope, no ruled text, no line pins, no volatile
literals, all tests green.
**Row 6 (writing standard): FAIL for §0–§2** — four high should-fixes, none of which blocks the
merge (the runbook lands as DRAFT that authorises nothing) but all of which must close before the
runbook is used to arm a night.

---

## 1. CONTRACT (row 2) — PASS

### 1a. §0.8 clauses vs the script's argparse and behaviour — MATCH

`python3 scripts/write_derivation_night_inputs.py --help` executed. Flag table at
runbook L451–456 matches argparse exactly:

| Runbook clause | Executed result |
|---|---|
| `--out-dir` required, no default | `required=True`, no default — confirmed in `--help` usage line |
| `--power-policy` default `ac_high_power`, "imported from the wrapper generator's own `CHAIN_POWER_POLICY`" | `default=CHAIN_POWER_POLICY`; `gen_derivation_night.CHAIN_POWER_POLICY == 'ac_high_power'` (executed) — imported at `write_derivation_night_inputs.py` module head, not restated |
| `--acceptance` default "the active acceptance" | `default=str(DEFAULT_ACCEPTANCE_BOUND_PATH)` → `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` (executed) |
| `--force` off by default | `action="store_true"` |

**"On success it exits 0 and prints three lines" (L471) — CONFIRMED.** Executed with the
machine reads mocked in-process (planned epoch differing from the acceptance in `os_build`):

```
rc=0
stale identity fields vs /…/calibration_acceptance_d079_v2_n17_r6.json: os_build
IDENTITY_EPOCH_JSON=/…/identity-epoch.json sha256=88b1fbe795a79ddbccf730c8f03462bef39df93893a20a2d0e093104a00b0131
T1_BINDINGS_JSON=/…/t1-bindings.json sha256=c171dca070e2943b8612be0483743c501e4e6a056633fd9705a066b7fc33a45b
```

Three lines, last two in the documented `NAME=<path> sha256=<64 hex>` paste-line form.
The runbook's rendering at L476–480 is shape-accurate.

### 1b. The seven refusal rows — ALL SEVEN REPRODUCED, wording matches

Each executed with machine reads mocked in-process where needed. All returned **rc 2**,
all printed `refused: <reason>` on **stderr**, all wrote **nothing**.

| # | Runbook row | Executed stderr (verbatim) |
|---|---|---|
| R1 | nothing stale → ORDINARY night | `refused: no identity field differs from the acceptance's epoch at /…/calibration_acceptance_d079_v2_n17_r6.json: this machine still matches the acceptance in force, so this is an ORDINARY night, not a derivation night: the writer's --derivation-only mode would refuse these inputs at d01 with the settle already spent. Run the ordinary window path instead` |
| R2 | wrong interpreter / MLX | `refused: machine vector derivation failed: ModuleNotFoundError: No module named 'mlx'` — reproduced **unmocked** under the MLX-free `python3`, byte-identical to the runbook's quoted string at L437–438 |
| R3 | empty fields | `refused: identity epoch fields are empty on this machine: ['os_build']; the night's reserve step refuses an empty binding, so fix the machine read (an absent MLX or an unreadable sampler is the usual cause)` — and the out-dir was verified **empty** afterwards (`R3 files written? []`) |
| R4 | overwrite without `--force` | `refused: refusing to overwrite ['/…/identity-epoch.json', '/…/t1-bindings.json']; a night may already be pinned to those bytes. Pass --force only when you intend to invalidate any wrapper already generated from them` — and `--force` on the same inputs returned **rc 0** |
| R5 | `--out-dir` not a directory | `refused: --out-dir /…/nope is not an existing directory; create the night root first, so that this script never invents the custody location the night's evidence is filed under` |
| R6 | empty `--power-policy` | `refused: --power-policy is empty; the identity epoch's power_policy field must be a non-empty value (the chain captures under 'ac_high_power')` |
| R7 | unauthenticable acceptance | `refused: the acceptance at /…/bad.json could not be read as an issued artifact (acceptance_artifact_unauthenticated), so no stale field can be established; name a readable issued acceptance with --acceptance` |

The "nothing is written, never one file of the pair" clause (L488–489) is structurally
true: `write_night_inputs` performs both `write_bytes` calls (L231–232) only after every
refusal has passed, and the two are the module's only write operations (grepped: no other
`write_bytes`/`write_text`/`open(`/`mkdir`/`unlink`/`rmtree`).

The order-of-operations sentence at L458–469 matches the code path
`_derive_planned_vectors` → `_refuse_incomplete_vector` ×2 → `_stale_identity_fields` →
`_refuse_overwrite` → write.

### 1c. §0.3 worked example vs record 134 — MATCH

Record 134 (`/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/`, line 4) records:
`os_build 25F84 → 25G83 MISMATCH`, `powermetrics_sha256 d1dccad0… → b762e5bf… MISMATCH`,
`hardware_model` and `mlx_version 0.31.2` match, `mismatched fields: os_build, powermetrics_sha256`,
appended line `pre-registered powermetrics sha256 b762e5bf…: match`, `rc 3`.

Runbook §0.3 L212–230 reproduces all six facts identically, including the appended-line
literal and rc 3. The §0.3 "two mismatching fields is the expected shape, not one" gloss
and the `match`/`MISMATCH`-simultaneously trap disambiguation (L269–278) are correct and
are the strongest pedagogy in the document.

### 1d. §7 symbols exist in the merged tree — ALL RESOLVE

`git grep` at HEAD over `scripts/ joulewise/ tests/` for all 38 cited symbols
(`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WATCH_FIELDS`,
`observe_machine`, `mismatched_fields`, `registration_dry_run`, `DRY_RUN_INADMISSIBLE_EXIT`,
`SUCCESSOR_MINIMUM_CORPUS_SIZE`, `RULED_ALTERNATIVE_CORPUS_SIZE`, `SCREEN_CHALLENGE_MEMBER_LIMIT`,
`PREREGISTERED_NIGHT_COUNT`, `PREREGISTERED_SLOTS_PER_NIGHT`, `preregistration_epoch_pins`,
`_PLAN_KEYS`, `PLAN_MAX_AGE_S`, `NIGHT_GATE_REASON_CODES`, `NIGHT_DRIVER_REASON_CODES`,
`MAX_DECLARED_SESSION_SLOTS`, `CHAIN_ANCHORS`, `CHAIN_POWER_POLICY`, `_validated_identity_epoch`,
`_validated_json_object`, `programmed_span_s`, `_census_clean`, `_validated_ruling`,
`_next_deadman_epoch`, `build_spec`, `render_wrapper`, `_run_chain_once`, the three
`DERIVATION_*` refusal codes, `IDENTITY_EPOCH_NAME`, `T1_BINDINGS_NAME`,
`_planned_t1_bindings`, `_sysctl_identity`, `ENVELOPE_MINIMUM_CORPUS_N`)
returned **zero MISSING**. All nine cited non-Python files exist.

§7's stated discipline — "Citations are by SYMBOL … never by line number" — holds; see §4 below.

### 1e. Arithmetic — CONSISTENT

Executed against the live module:

```
programmed_span_s(12)            = 7680     (defaults 600 / 600 / 480)
PRE_SETTLE_ALLOWANCE_S           = 300
7680 + 300                       = 7980     ← generator's hard floor, matches §1.2 L817
EXAMPLE_WINDOW_MAX_S             = 9000     ← matches §1.2 L798
9000 - 7680                      = 1320     ← matches the Δ ≤ 1320 bound
1789221600 - 1789206960 - 301    = 14339    ← matches the §1.2 epoch worked example, and 9000 ≤ 14339 ✓
```

The docstring of `programmed_span_s` states the same decomposition
("600 + 11 x 600 + 480 = 7680 s for the pre-registered twelve") that §1.2 L780–784 prints.
§1.2 also explicitly disambiguates the two unrelated 300 s budgets (pre-settle allowance,
spent inside the window; courier allowance, spent after it) at L838–841 — exactly the kind
of collision the writing standard demands be called out, and it is.

---

## 2. Writing standard (row 6 counter-review) — **FAIL for §0–§2**

The runbook carries a **§Terms section at L68–117 (before §0)** and a **§8 first-use table at
L1533–1592**, and its arithmetic core is genuinely excellent. But the mechanical first-use test
and the replication test both fail, and two of the failures have operational teeth.

### First-use failures (verified individually)

**W-1 — `wrapper` (first body use L186, §0.2; built L566, §1.1a).** Load-bearing three times
before definition: L186, L314–318 (§0.5's entire `[CHAIN_SHA256]` rule turns on "NOT any night's
wrapper digest" and "three nights produce three different wrappers" — unintelligible without the
term), and L396. Then five more times in §0.8 (L396, 409, 419, 425, 496). **Absent from §Terms.**

**W-2 — `fence` is equivocal, and the collision is unacknowledged.** §Terms L105 builds it as
"a half-open local-time interval in which the watchdog refuses to launch or adopt a session:
`[02:45:00, 03:30:00)` and `[07:00:00, 07:01:00)`". §2.3 L1046/L1055 uses the same word for a
different object entirely — "the blindness fence", "The fence is installed in code, not left to
discipline" — a code-enforced prohibition on reading captured values. §8 L1552 lists only the
time-interval sense.
**Operational consequence, verified:** the §Terms gloss says the fence blocks launching "a
session", and §Terms L73 defines **Session** as "a ledger capability that reserves several
attempts". §1.2's worked example arms `t0 = 2026-09-12 02:56:00 PDT` (L846) — **inside
`[02:45:00, 03:30:00)`**. An operator applying the runbook's own glossary mechanically would
conclude the runbook's own worked example is fenced. (`docs/process/MAGISTRATE_WATCHDOG.md:31`
and `:52` confirm the belt "forbids launch"; the real referent is the *watchdog's supervisor*
session, not a ledger session and not the night's `t0` — but nothing in the runbook says so.)

**W-3 — `the writer` denotes two different programs, inside §0.8, with no marked convention.**
L406 "the writer that produces them" = the **desk** writer. L459 "the capture writer's own
helpers" = `validate_powermetrics_fiducial.py`. Then the bare form flips between them with no
signal: L464 "the value **the writer** measures at 03:10" (capture), L493 "refused by **the
writer** at `d01`" (capture), **L501 "Run the writer at each night's arm" (desk)**, L504 "the
capture writer compares". This is the writing standard's "unpaid work" failure in its literal
form, in the section this review was asked to contract-check.

**W-4 — `night root` / `<NIGHT_ROOT>` (first use L408, §0.8; built L567, §1.1a).** It is the
operand of §0.8's first runnable command (L445, `--out-dir "$NIGHT_ROOT"`) and of the refusal
remedy "Create it first" (L497), but its meaning ("the custody directory the plan calls
`custody_root`") and its path convention (L538, `/Users/edr/night-custody/<PLAN_ID>`) arrive
two sections later.

**W-5 — `tracked chain` (L313, §0.5), bolded as a term, unglossed.** §0.5 tells the operator to
put "the **tracked chain's** SHA-256" into `[CHAIN_SHA256]`, but the chain's path
(`scripts/night_chains/calibration_derivation_only.zsh`) does not arrive until L551/L599, and no
`shasum` command is given for it (contrast L326, which does give one for the pre-registration).

Also unbuilt where used: **frozen calibration plan / `PLAN`** (L593, required flag L665 — never
built anywhere, absent from §8); **settle** doing technical work at L493 ("with the settle already
spent") 278 lines before it is explained at L771; **the live preflight** (L467); **C1–C5 / C2**
(L1010, L517, never enumerated); **`[DD]`** (L307, a blank expanded nowhere).

**Passes, recorded so the check is auditable:** identity epoch (L51), T1 bindings (glossed at
use, L209–211), stale field (L81), tripwire (L728), sidecar (L616), pre-settle allowance (L807,
and explicitly disambiguated from the courier allowance at L838–843), courier (L108), dead-man
(L102), handback (L108), blindness (L99), dispatch (L635), desk recovery (L1099), `$PY` (L177/L181).
`written-ruling escape` does not occur in §0–§2.

### Replication failures — the arm is NOT replicable from the text alone

**R-1 (most serious) — five shell variables are used in runnable commands and assigned nowhere.**
Verified exhaustively: the entire 1592-line file contains **exactly four** assignments —
`H` (L139), `REMOTE_URL` (L164), `MEASUREMENT_ROOT` (L165), `PY` (L177). But
`$NIGHT_ROOT`, `$SESSION_ID`, `$EVIDENCE_ROOT_ID`, `$CALIBRATION_LEDGER`, `$LEDGER_HEAD_PIN`
and `<WINDOW_CUSTODY_ROOT>` appear in command blocks at L445, L662–667, L734–738, L756, L1011,
L1024–1026 and L1105–1109. **§0.8's own writer invocation (L445) is among them.** An operator
pasting §0.8's block as written runs it with an empty `--out-dir`.

**R-2 — §1.1b step 3 and §1.4 contradict each other on the plan's path.** L662 runs generation
with `--plan "$NIGHT_ROOT/night_plan.json"`, and I confirmed by executing
`gen_derivation_night.py --help` that `--plan` is an **input** ("frozen v2 night plan JSON (emit
mode)") — so the plan must already exist at that path during §1.1b. But §1.4 L971–973 requires
atomically moving the staged plan **into** `<NIGHT_ROOT>/night_plan.json` with "target must not
pre-exist and must not be a symlink". Either the step-3 path is wrong or the §1.4 move is
impossible. The staging path is never named. Worse, if the plan really does sit at its
discoverable path during §1.1b, the night is discoverable **before** the §1.4 email — contradicting
§0.7 (L375) and the fixed email-then-arm order at L954–955.

**R-3 — §1.4, the arm itself, contains no commands.** L971–984: "install both agents FROM
`<CLONE>`" names no installer, no launchd labels, no plist paths; "reassert the pins", "run the
final raw census", "record the post-install `night/` inventory" are all uncommanded. It defers to
"Runbook 68 §Block B" as "the executable template" — and **runbook 68 is cited four times (L159,
L845, L947, L978) with no path**; its only locator is §7 L1512 ("record 12 of this trace
directory"), 370 lines past the point of use.

**R-4 — the harvest cannot be run by the activation that must run it.** §2 L999 assigns the
harvest to the *next* activation, and §1.5 L990 says the frozen triple carries only
`(<PLAN_ID>, <CLONE>, <H>)`. But §2.1/§2.2/§2.4 commands need `$SESSION_ID`, `$CALIBRATION_LEDGER`,
`$LEDGER_HEAD_PIN`, `<NIGHT_ROOT>` and `<WINDOW_CUSTODY_ROOT>` — none carried, none reconstructible
from the triple as written.

**R-5 — uncommanded setup steps that everything downstream depends on.** L173 "Build the clone's
virtual environment from the lock" (no command, no lock file, no tool — yet `test -x "$PY"` at
L178 depends on it); L190–194 the ledger "restored byte-exact from the canonical ledger" (no
command, no source path); §0.6 L356–370 the census (no commands for "stop all own seats…"; the
three substrings the night's own census matches appear only at L1365); §0.7 L372–377 (four
preconditions, zero checks); §0.4 L300 "Record the head pin's sequence and digest now" (path not
given until L679).

**R-6 — ordering circularity.** §1.1b makes writing the desk inputs step 1 and authoring the plan
step 2, but `<NIGHT_ROOT>` = `custody_root` = `/Users/edr/night-custody/<PLAN_ID>` (L538), so the
plan id must be fixed *before* step 1 can name a directory. Nothing says who creates that directory
or with what command (L453 "It must already exist"; L497 "Create it first").

**Minor:** L165's `<NIGHT_DATE>` format is never stated (L528's `<PLAN_ID>` example uses
`<YYYYMMDD>` while §1.2's examples are ISO); and L207–212 watches four fields against an epoch of
six (L51) without saying why the other four are unwatched, so the operator cannot judge whether an
unwatched field's drift matters before arming.

### What does meet the bar
§0.3's inverted-rc gloss with the recorded worked table (L216–291), §1.1a's forcing problem and
five wrapper steps (L546–613), and §1.2's whole arithmetic (L767–933) are replicable and genuinely
well built — 7680, the 7980 floor, 9000, Δ ≤ 1320 and the two unrelated 300 s budgets are all
rebuildable from the text alone.

---

## 3. Docs freshness — PASS

```
python3 -m unittest tests.test_docs_freshness tests.test_d078_reason_registry
Ran 44 tests in 0.840s
OK
```

**Volatile-literal rule — CLEAN.** `grep -n 'PR #\|Ran [0-9]\+ tests\|\bCodex\b\|\bSol\b\|\bAstra\b\|\bOpus\b\|\bFable\b' docs/phase_2/derivation_night_runbook.md` → **zero hits**.
No PR numbers, no test counts, no orchestration model names anywhere in the 1592-line runbook.
Seats are referred to only as "seat S8" / "record 135" / "record 134", which is the durable form.

---

## 4. Row 10 fresh eyes on the whole diff — PASS

**Scope — exactly the four declared items, nothing more.**
```
docs/phase_2/derivation_night_runbook.md           | 1592 ++++
docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md |    8 +-
scripts/gen_derivation_night.py                    |    8 +-
scripts/issue_calibration_acceptance_generation.py |    6 +-
scripts/write_derivation_night_inputs.py           |  326 ++++
tests/test_issue_calibration_acceptance_generation.py |   10 +
tests/test_write_derivation_night_inputs.py        |  351 +++++
7 files changed, 2292 insertions(+), 9 deletions(-)
```

- **Ruled text untouched — VERIFIED.** No `configs/calibration/preregistration_*` and no
  decision-log file appears in the stat. `configs/` is absent from the diff entirely.
- **No line pins — VERIFIED.** `git diff d18bc2b3..HEAD -- scripts/ docs/phase_2/ | grep '^+.*\.py:[0-9]'` → **zero hits**.
- **No scope excursion.** The new writer's only side effects are the two `write_bytes` calls
  into `--out-dir` (L231–232). It opens no ledger — `tests/test_write_derivation_night_inputs.py:235`
  pins this by source-forbidding `load_calibration_ledger_snapshot`, `read_replay`,
  `DEFAULT_LEDGER_PATH`, `DEFAULT_HEAD_PIN_PATH`, `_authenticate_ledger_and_acceptance`.
- **Refuter 136 F1/F2 cures confirmed present and tested.** `tests/…:322`
  `test_the_sampler_path_is_the_writers_own` (F1, source-pinned to the imported `POWER_METRICS`
  one home at `scripts/write_derivation_night_inputs.py:74`), and `tests/…:330`
  `test_an_unreadable_acceptance_refuses_by_name_and_writes_nothing` (F2) — the latter I also
  reproduced independently as R7 above.
- **The one-home import is behaviour-preserving.** Executed:
  `ENVELOPE_MINIMUM_CORPUS_N = 17`, `RULED_ALTERNATIVE_CORPUS_SIZE = 17` — same value as the
  replaced literal, now by import. `tests/test_issue_calibration_acceptance_generation.py:2022`
  pins it by source text *and* asserts the old literal is absent, so a silent revert fails.
- **The regenerated region is self-consistent.** `gen_derivation_night.example_spec` and
  `render_region` both moved to `identity-epoch.json` / `t1-bindings.json`, and the
  SHAKEDOWN-G2-RUNSHEET generated region matches — proven by `tests.test_gen_derivation_night`
  passing in the run below (it resolves the region against the generator's bytes).

---

## 5. Tests — ALL GREEN

```
$ python3 -m unittest tests.test_write_derivation_night_inputs \
                      tests.test_gen_derivation_night \
                      tests.test_issue_calibration_acceptance_generation
Ran 169 tests in 75.226s
OK
```

MLX-free interpreter, first module:
```
$ /opt/homebrew/bin/python3 -m unittest tests.test_write_derivation_night_inputs
Ran 15 tests in 0.016s
OK
# /opt/homebrew/bin/python3 = 3.14.7; importlib.util.find_spec('mlx') -> None (confirmed MLX-free)
```

The writer's 15 tests run green with no MLX present, which is the property the suite needs:
the machine reads are genuinely mocked, not incidentally satisfied by the dev machine.

---

## Findings, severity-tiered

### BLOCKERS — none for the merge
All code in the diff is correct, tested and in scope. The runbook lands with **STATUS: DRAFT,
authorises nothing** (L3–4), which is the correct handling for a document with the replication
gaps below. The §2 findings are **must-fix-before-arm**, not must-fix-before-merge.

### SHOULD-FIX (high) — must be closed before this runbook is used to arm a night

**S-1 — R-1: five shell variables used in runnable commands, assigned nowhere.**
`docs/phase_2/derivation_night_runbook.md:445` (§0.8's own writer invocation), :662–667, :734–738,
:756, :1011, :1024–1026, :1105–1109. Only `H`, `REMOTE_URL`, `MEASUREMENT_ROOT`, `PY` are ever
assigned (:139, :164, :165, :177). Fix: export `NIGHT_ROOT`, `SESSION_ID`, `EVIDENCE_ROOT_ID`,
`CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`, `WINDOW_CUSTODY_ROOT` where first used, exactly as §0.2
L177 already does for `$PY` — the changelog at L22 claims this discipline ("`$PY` is now exported
where it is first used rather than assumed") but applied it to one variable only.

**S-2 — R-2: §1.1b step 3 and §1.4 contradict each other on the plan's path.**
`:662` vs `:971–973`. `--plan` is an input (verified by executing `--help`), so the target of
§1.4's `os.replace` pre-exists and the move is impossible as written; and the night would be
discoverable before the §1.4 email, contradicting §0.7 `:375`. Name the staging path and make the
two sections agree.

**S-3 — R-4: the frozen triple does not carry what the harvest needs.**
`:990` carries `(<PLAN_ID>, <CLONE>, <H>)`; §2 needs `$SESSION_ID`, `$CALIBRATION_LEDGER`,
`$LEDGER_HEAD_PIN`, `<NIGHT_ROOT>`, `<WINDOW_CUSTODY_ROOT>`. Either widen the triple or state the
derivation from `<PLAN_ID>`.

**S-4 — R-3: §1.4 defers the arm to a pathless "Runbook 68".** Cited at `:159`, `:845`, `:947`,
`:978`; the only locator is `:1512`. Give the path at first use.

### SHOULD-FIX (low)

**S-5 — `scripts/write_derivation_night_inputs.py:38` states a false safety property, rendered
into operator-facing `--help`.** The docstring says the script "never touches `configs/calibration`"
and then, three lines later, "reads the acceptance artifact". Executed:
`DEFAULT_ACCEPTANCE_BOUND_PATH = /…/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
— the default `--acceptance` **is** in `configs/calibration` and is read on every successful run.
`argparse` passes `description=__doc__`, so the false claim is printed by `--help`. Behaviour is
correct and harmless (read-only, never written, never pinned); only the claim is wrong, and no test
pins it (`tests/…:235` forbids only ledger symbols). **Fix: `never touches` → `never WRITES into`.**
One word. The runbook does *not* inherit the defect (§0.8 L455 and §6 L1447 are both correct).

**S-6 — W-3: `the writer` denotes two programs inside §0.8.** `:464`, `:493` (capture) vs `:501`
(desk). Reserve the bare form for one, or always qualify.

**S-7 — W-2: `fence` is equivocal and its gloss contradicts the runbook's own worked example.**
`:105` (time interval, "a session") vs `:1046`/`:1055` (blindness prohibition); and `:105` read with
`:73`'s definition of Session appears to fence `:846`'s `t0 = 02:56:00 PDT`. Split the two senses and
say that the fenced "session" is the watchdog's supervisor, not a ledger session and not the night's `t0`.

**S-8 — W-1/W-4/W-5: `wrapper`, `night root` and `tracked chain` are used in §0 and built in §1.1a.**
`:186`/`:314–318`/`:396` ; `:408`/`:445` ; `:313`. Fix: add `wrapper` and `night root` to §Terms
(`:68–117`) reusing §8's existing one-liners, and give the chain's path at `:313`.

### NITS

**N-1 — `scripts/write_derivation_night_inputs.py:251` — the `--help` epilog under-describes
stdout.** It says "paste **both** lines" and lists two; the script prints **three**. The runbook is
more accurate (L471). §0.8 L482 requires recording all three, so an operator following `--help`
alone would miss the stale-fields line.

**N-2 — `scripts/issue_calibration_acceptance_generation.py:86` — import not alphabetised.**
`ENVELOPE_MINIMUM_CORPUS_N` inserted between `ACTIVE_ACCEPTANCE_ID` and `ACCEPTANCE_BOUND_SCHEMA`.
Cosmetic only — **no CI lint risk confirmed**: `pyproject.toml` selects no linter and none of
`ci.yml`, `d117-production-proof.yml`, `gate-ledger.yml`, `site.yml` runs one.

**N-3 — runbook §0.8 L458–469 omits `_refuse_overwrite` from its stated order of operations**
(it runs between the stale check and the write, `write_night_inputs` L226). The refusal itself is
documented two rows later, so nothing is missing from the operator's picture.

---

## Summary

**The code is sound and the contract holds end to end.** All seven refusals reproduce with the
runbook's exact wording and rc; the three printed lines are as documented; §0.3 matches record 134
fact for fact; all 38 §7 symbols resolve; the 7680 / 7980 / 9000 / 1320 arithmetic ties to the live
constants; the diff is exactly its declared scope with no ruled text, no line pins and no volatile
literals; the refuter-136 cures are present with defect-shaped regressions; 169 + 15 + 44 tests green,
including 15 green under a confirmed MLX-free interpreter.

**The runbook is not yet an arming document.** Its arithmetic and mechanism sections (§0.3, §1.1a,
§1.2) are the best-built prose this lane has produced, but a next-activation operator cannot arm from
it: six variables its own commands interpolate are never assigned (including in §0.8), §1.1b and §1.4
contradict each other on the plan's path in a way that also breaks §0.7's discoverability fence, the
harvest needs five values the frozen triple does not carry, and the arm step itself has no commands
and points at a pathless runbook 68. Three terms (`wrapper`, `night root`, `tracked chain`) do
load-bearing work in §0 and are built in §1.1a; `fence` and `the writer` each denote two different
things without acknowledgement, and the `fence` gloss appears to forbid the runbook's own worked
example.

**Recommendation: merge, then close S-1…S-4 before any arm.** The DRAFT banner already encodes
exactly this, and landing the promoted runbook plus the tested desk writer is strictly better than
holding them. S-5 and N-1 are one-line bench fixes in the script and, by rule 9's bench threshold,
smaller than the contract needed to delegate them.
