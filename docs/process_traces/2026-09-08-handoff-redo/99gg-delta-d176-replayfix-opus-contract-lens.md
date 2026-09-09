# Delta re-audit — D-176 replay-fix seat (Opus, contract lens)

Read-only: `git diff` in `/Users/edr/code/JouleWise-wt-int-d176` (branch
`int/2026-09-08-d176-seats-2-3`, uncommitted seat edits) plus static reads of
production. No suite executed.

## Verdict

**No BLOCKER.** All four rulings are honored as written; no refusal is relaxed,
no exact-key assertion loosened, and the one mock change *narrows* an
over-broad mock rather than mocking away a check. Two NITs below.

## A — sixth exact key `pack_root` (watchdog CLI)

Honored. `tests/test_magistrate_watchdog_cli.py:202-215` adds `pack_night` with
exactly the six keys `pack_id, pack_root, pack_sha256, attempt_ordinal,
authorization_record, confirmation_record`. That is the exact set enforced by
`joulewise/night_gate.py:295-297` (`"pack_night keys must be exact"`) and by
the consumer at `joulewise/arm_readiness.py:9994-9997`. The plan is
`receipt_class="TRANSACTION_PACK"` (`tests/test_magistrate_watchdog_cli.py:158`),
and `night_gate.py:1103` requires `pack_night` for that class — so the fixture
was previously *invalid*, not over-strict. `pack_root = root/"packs"/plan_id`
satisfies `night_gate.py:305` (absolute, non-symlink, basename == `pack_id`);
record paths sit under `custody_root`, satisfying the escape check at
`night_gate.py:332`. **No exact-key set was widened or relaxed.**

## B — pack-class digest at consumption (fiducial)

Honored, and the seat's framing is true, not a story.

- The digest replay is already gated on class: `arm_readiness.py:9991`
  (`if plan["receipt_class"] != "TRANSACTION_PACK": raise _go_invalid`) precedes
  the `committed_pack_tree_sha256(pack_root)` call at `:9997-10004`. The check
  cannot fire for a non-pack class, so ruling B's fix-the-call-site branch was
  moot and the fixture branch is the right one.
- The class is a pack class: the fixture plan is built with
  `"receipt_class": "TRANSACTION_PACK"` at `tests/test_arm_readiness.py:110`.
- Committing is what production does: the untracked refusal lives in production,
  `joulewise/arm_readiness.py:3149-3157` — `readiness_pack_not_committed`,
  `f"untracked pack entry: {extra!r}"` (and `:3145-3151` for directories). The
  base fixture already mirrors this at `tests/test_arm_readiness.py:191-196`
  (git init, add, commit, then `arm["pack"]["pack_sha256"] =
  committed_pack_tree_sha256(...)`). The fiducial setUp wrote
  `calibration-acceptance.json` into the pack *after* that, so the file was
  untracked; the fix commits it and recomputes. Same shape as the base fixture.
- The recompute is not "compute the expected value to make it pass": the
  consumer compares the live digest against **both** `binding["pack_sha256"]`
  (from the plan) and `arm["pack"]["pack_sha256"]` (`arm_readiness.py:10005`).
  The plan is built lazily inside `_consumer_inputs`
  (`tests/test_arm_readiness.py:441`) via `install_pack_night_launch_inputs`,
  which re-reads the ARM receipt **from disk** (`:78`) and copies
  `arm["pack"]["pack_sha256"]` into `plan["pack_night"]` (`:117`). The seat's
  trailing `_install_attested_launch_recipe()` ends in `_rewrite_arm()`
  (`tests/test_arm_readiness.py:361`), which is what puts the new digest on
  disk. Without that call the fixture would be *inconsistent*, not stricter.
  The three-way equality is preserved end to end.

## C — the narrowed subprocess mock (run_campaign)

Honored, and verified rather than accepted. `committed_pack_tree_sha256` shells
out: `arm_readiness.py:3070` → `_run_git` at `:3031-3038`, which calls
`subprocess.run(("git", "-C", ...))`. The test patched
`run_campaign_module.subprocess.run` — the same module object — so the old
broad mock did swallow the GO replay's Git and produce
`launch_go_receipt_invalid`. `tests/test_run_campaign.py:332` binds
`real_run = subprocess.run` *before* the patch context, and `:335-338` passes
everything except the synthetic `["child"]` argv through to real Git.
`_run_git` passes a **tuple**, so `command != ["child"]` is unambiguously true
for it. The asserted expectation `launch_lineage_conflict`
(`tests/test_run_campaign.py:373`) is **retained**, not downgraded — the fix
restores the assertion the test was written to make. A genuinely broken GO
replay still raises `launch_go_receipt_invalid` and fails the assertEqual.

## D — F6 pins and the fixture-factory split

Pins verified with grep: `joulewise/t0_rehearsal.py:703` = `def evaluate_g5`;
`tests/test_t0_rehearsal.py:980` = `class PackGoReplayTests`;
`tests/test_t0_rehearsal.py:787` =
`def test_legacy_bundle_fails_g5_even_with_passing_g7_control`. All three land
exactly. `§10.5 items 6–9` is correct — §10.5 numbers 1–9, with the addendum
items at 6, 7, 8, 9 (`docs/contracts/pack_night_go_receipt.md:1342, 1351, 1359, 1366`).

`_set_up_fixture(..., existing_context=True)` has exactly one caller,
`tests/test_t0_rehearsal.py:440`; `_fixture_root` is fully removed (no
remaining references anywhere in `tests/`). `exist_ok=existing_context` is
semantically right and is a **tightening**: the default is now `False`, so a
fresh case that finds pre-existing context dirs raises. The six roots are
siblings under `<root>/context` (`tests/test_arm_readiness_schemas.py:157-162`)
with no nesting and no duplicates, and `mkdir(parents=True)` always creates
parents with `exist_ok=True` internally — so a genuinely fresh case cannot trip
it. Only the rehearsal factory, which deliberately reuses `self.base`, opts out.

## NIT-1 — contract edit is an in-place ruling amendment, not a dated addendum

`docs/contracts/pack_night_go_receipt.md:1179-1183` appends the invariant to the
body of §10.3 clause 5, a dated ruling ("§10.3 seat-2 rulings (2026-09-08)").
The file's own convention for post-hoc corrections is a dated addendum
subsection — `#### §10.3 addendum — finding-5 refusal representation
(2026-09-08)` at `:1207`. Prefer that shape so the original ruling text stays
readable as issued.

## NIT-2 — the invariant asserts enforcement without citing it

The paragraph states "every pack file … is committed before preparation" as a
production property, but cites nothing. The enforcing refusal is
`joulewise/arm_readiness.py:3155-3157` (`readiness_pack_not_committed`,
`untracked pack entry`), reached from `committed_pack_tree_sha256`; the
class gate is `arm_readiness.py:9991`. A one-clause citation would let a reader
replicate the claim instead of trusting it.

## Contract-conflict scan (asked in item 2)

Grepped the contract for `untracked`, `committed_pack_tree_sha256`,
`pack_sha256`, "pack tree", "pack root". Only two `untracked` occurrences: `:1089`
(unrelated, a pre-existing untracked *file* in the seat's WRITE_SCOPE prose) and
the new `:1180`. The new paragraph is consistent with `:163` (the `pack_night`
row: recompute at preparation, GO and consumption), `:187`, `:258-259` (the
consumption recompute), `:406` and `:886`. **No clause anywhere permits an
untracked entry in a pack tree, and none exempts any class other than by the
existing TRANSACTION_PACK gate.** No conflict.
