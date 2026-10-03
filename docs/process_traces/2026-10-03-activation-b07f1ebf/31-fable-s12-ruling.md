## Ruling on PR #460 (`scripts/gen_g2_phase_d.py`) under registration §11 and §12

**What the change is.** PR #460 swaps the order of two steps in `integrated_g2a_chain`, so the window-id rename now runs before the three explicit path pins instead of after (`scripts/gen_g2_phase_d.py:84-99`). The rest of the module is identical between `4205713c` and `b39d7015` when compared as syntax trees.

**Why only one line can move.** The rename rewrites only lines matching `^export G2A_[A-Z_]+=` whose value contains the runsheet id (`scripts/gen_g2_phase_d.py:88-90`). The pins rewrite `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` and `G2A_ROOT` (`scripts/gen_g2_phase_d.py:91-93`). The first two are not `G2A_`-prefixed, so the rename never touches them in either order. `G2A_ROOT` is therefore the only export whose final value depends on the order.

**Measured, not just argued.** I ran the old function (extracted from `4205713c`) and the new one on the same rendered chain:

| Inputs | Result |
|---|---|
| Plan id `d117-g2a-prefill-probe-20261003T0742Z`, root `/Users/edr/night-g2a/<plan id>` (the recipe's shape, `40-g2a-arm-recipe.md:100,106`) | Exactly one line differs: `export G2A_ROOT=…20261003T0742ZT0742Z` becomes `…20261003T0742Z` |
| Same plan id, root not containing the runsheet id | Byte-identical |
| Date-only plan id, root named by it | Byte-identical |

In the new chain the window id, bracket session id, pre and post attempt ids, evidence root id, `G2A_PLAN_ID`, `JOULEWISE_NIGHT_PLAN_ID`, both ledger paths and `NIGHT_PROGRAMMED_SPAN_S=17248` are the same bytes as from the old code. `tests.test_gen_g2a_window` passes (12 tests) and `gen_g2_phase_d.py --check` passes.

**No rule in §§3-10 can move.**
- **§3 operating condition** (`registration_block2.md:56-100`): machine, acceptance, models, probe-input producer, ledger and network time are untouched. The Chain item is still "the zsh chain emitted … by the recorded G2-a window command" (`:81-84`), with the same screen literal and the same `--check`.
- **§3 void clause** (`:99-100`): it fires on a change to an item in §3, and none changed. The registration defines H as "a main commit containing lane G2A-NIGHT-25G83-01" (`:274-275`), which the merged head also is.
- **§4 window shape** (`:102-131`): order, settles, stages, brackets and `window_max_s` are unchanged; the span and 19,980 s match the seal record (`52-seal-record.md:55`).
- **§§5-10**: receipt, validity, verdict, analysis and blindness code live in files this PR does not touch.

**No probe input, id, captured byte or admission can move.**
- Of the nine pinned files, only the generator's digest changed: `69903ae2…` (`52-seal-record.md:45`) to `76a7f043558df361b5ab191d5b3cdc327f39e0c702599fed6faac925243c7c46`. The other eight equal the seal record's table (`:46-53`), and the registration is still `8e45a0e0…` (`:8`).
- Probe inputs are built and bound by `generate_g2a_probe_inputs.py` (unchanged) before the chain exists (`40-g2a-arm-recipe.md:219-223`).
- The old chain was fail-closed: it pointed at a nonexistent directory and stopped at the inspection step (`2026-10-03-activation-b07f1ebf/00-session-record.md:19-26`). Nothing was published, no agent installed, no notice sent (`:14-15`). No data of this block exists.
- The new chain reads the same directory that `build-probes`, `bind-window` and `check` already use. That is what §3 presupposes when it says the inventory is re-authenticated "inside the chain before anything is reserved" (`registration_block2.md:78-80`).

**It is the §11 class.** §2 fixes the plan-id form with the `THHMMZ` suffix (`:48-49`), and §4.1 says the chain is authored by `--new-g2a-window` "and nothing else" (`:110-111`). The generator at H could not emit a working chain for that id form with the recipe's root. The fix makes it honour its own `--g2a-root` argument. This is "a fix that only makes code agree with this text" (`:269-270`); it changes no rule, so there is nothing for an erratum to settle (`:268-269`).

**The one wrinkle: "later window".** §12's H′ sentence literally covers "any later window" (`:284-287`), and w1 has not been armed. I do not read that as forcing a new seal, for three reasons:
1. §11 is not limited to later windows.
2. §12's closing "Any other difference needs a new seal" (`:287-288`) is about the kind of difference between H′ and H, and this is the licensed kind.
3. The refuter's D1 extended H′ precisely to "a NULL window whose cause was a code defect: its fix changes a §12-pinned script" (`51r-seal-refuter.md:171-187`), noting it "saves a cold gate, not a number" (`:234`). The strict reading would require burning a guaranteed-null window at H to reach the same H′ and the same chain bytes; that protects no number.

**Conditions (bookkeeping, not a new seal).**
- **H′ scope.** H′ is the merged main head. Between the sealed H (`ac4efb3d`) and `b39d7015`, the only pinned file that differs is `scripts/gen_g2_phase_d.py`; re-verify this at the merged head before arming.
- **Seal record.** Before arming, extend `52-seal-record.md` under line 58 with the H′ sha, the generator digest `76a7f043…`, and the other eight pins restated as unchanged (`40-g2a-arm-recipe.md:436`). PR #460 does not do this yet.
- **Say it plainly.** The extension should state that w1 itself is armed from H′, citing the aborted pre-publication attempt, so the record is not read as "w1 at H".
- **Recipe edit.** The change at `40-g2a-arm-recipe.md:236` passes `MEASUREMENT_HEAD` to the desk inspection, which the driver supplies itself (`scripts/run_night.py:633`). The recipe is not a §12 pin and this touches no window rule.

RULING: EXTEND-SEAL-WITH-H-PRIME
