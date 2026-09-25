# Seat K report: A291 fix round 2, independent checker

All of seat K's texts are implemented and committed in three commits on `fix/2026-09-24-a291-fix2-checker`, not pushed. The new fuzz module is RED at 20cd29de: properties (a), (b) and (d) fail. The checker, stress and registration modules are green. There are no NEEDS_RULING items. Nothing I changed touches FT-6/7/9/10, the registration keys, the role identities or the cell structure of contract v4.

## Where each K text is implemented

**Text 7, item-centric `_derived`** (`tests/scored_roster_checker.py:273`)
- The outer loop runs over (level, model, registered item). An item's parent is its registered slice, `q // block_size`, not a roster block.
- Planned gate: the parent has no refused item. Executed gate: every item of the parent is located by a captured window.
- Every parent with at least one located item gets a position. The shortfall / `spread_exceeded` flag and the null rule follow A291-POP-1.
- Float order follows X-4: positions summed in item order, means taken over parents in `k` order.
- The helper `_window_of` (`:249`) maps each (model, item) to the envelope index of its single live listing. It uses `groupby`/`product`/`itemgetter`; there is no loop over parents.

**Text 7, `check_executed`** (`:832`)
- It validates first, then calls `_derived(..., captured_window_keys)`. `drift_exceeded` is false when the lever is null or `max_gap` is undefined.
- Two new helpers: `_unreported` (`:824`) and `_window_keys_ok` (`:828`).
- Its signature and return shape are unchanged.

**Text 7, `refresh_derived`** (`tests/test_scored_roster_checker.py:145`)
- It is a second, deliberately different derivation. It walks envelope by envelope, stamping each live item with its envelope index, then reads the registered slices.
- It builds fresh dicts and does not call the checker.

**Text 3, checker INV-11 row** (`tests/scored_roster_checker.py:578`)
- (a) exactly one holder that is not superseded, not terminal, and listed in exactly one envelope; (b) exactly one terminal entry and no holder listed anywhere; exactly one of (a) and (b) must hold.
- The INV-10 row is unchanged and still reports an empty block.

**Text 7 (C5), R4d checker witness** (`tests/test_scored_roster_checker.py:830`)
- It uses the same fixture, report loop and appended block `large:decode:1:999` as text 6, resealed with `c.digest`.
- It asserts that `check_roster` returns a list, without raising, whose `inv_id` set contains INV-10.
- The packer entries are imported inside the test only; `tests.test_scored_packer` is never imported.

**Text 2, `_detail`**: defined identically at `tests/test_scored_roster_checker.py:37` and `tests/test_scored_packer_fuzz.py:29`.

**Text 7, `generate_case(seed, i)`** (`tests/scored_case_generator.py:99`)
- Every choice is drawn from `random.Random(f'A291:{seed}:{i}')`: block size, n, cap, prediction, pilot or registered mode, and every observation.
- Observations are legal by construction: a completed prefix, at most one cut-off, then not-started, with elapsed values summing to at most `interior_s`.
- The signature is `signature()` at `:90`, exactly the ex-10 B8 tuple.

**Text 8, new stress test** (`tests/test_scored_packer_stress.py:124`)
- 60 cases per seed.
- On each final roster (the checker replays every event, so this covers every intermediate step) it runs `check_roster == []` and `verify_executed_roster`, and checks that `executed_status` equals `check_executed` on a seeded 75 % key sample.
- It asserts E1–E11 are covered for each seed and that signatures differ for at least 60 % of case indices. Measured: 60/60 differ.
- `test_seeded_300_registration_sequences`, `run_case`, `_report` and `r2_four_envelope_roster` are unmodified.

**Text 7, fuzz module** (`tests/test_scored_packer_fuzz.py`)
- The ten operators are at `:42`–`:120`. Operator 5 removes a single from `blocks` only; operator 9 only alters an event with `k < len(events)-1`.
- `reseal` (`:33`) is the ex-10 B8 text verbatim.
- Bases are every roster of four `generate_case` runs (`CASES`, `:24`). Intermediate mutants go to `requeue_overrun` with all-keep observations `(completed, 0.01)`. Final mutants go to `executed_status` with a seeded 75 % key sample. Each mutant is submitted both resealed and unresealed.
- Properties (a)–(f) are separate tests at `:204`–`:227`. The legal corpus is the `generate_case` runs themselves plus `executed_status` on each final roster.

## V1: fuzz at 20cd29de (RED)
```
FAIL: test_a_entry_points_return_or_raise_packing_refusal
AssertionError: non-PackingRefusal exception: 8 rows; first: (op1_live_to_voided, 291013:10, k=25, sealed=True, final=False, outcome=('crash', 'ZeroDivisionError', 'division by zero'), checker=['INV-11', 'INV-27', 'INV-38']); ... (op6_flip_superseded, 291013:10, k=28, sealed=True, ... ('crash', 'ZeroDivisionError', ...), checker=['INV-11', 'INV-12', 'INV-27', 'INV-32', 'INV-38'])
FAIL: test_b_checker_violation_implies_refusal   (same 8 rows: checker reports violations, packer crashes instead of refusing)
FAIL: test_d_refusal_census
AssertionError: Items in the second set but not the first: 'inv_12' 'inv_11'
Ran 6 tests in 55.603s
FAILED (failures=3)
FUZZ cases=4 submissions=1798 census={'inv_02': 334, 'inv_03': 198, 'inv_38': 508, 'inv_39': 8, 'inv_52': 46, 'stale_derived': 696}
```
Why each fails:
- **(a) and (b):** these are the E1 shape. Voiding a cell's last live parent (operator 1), or flipping `superseded` (operator 6), makes today's `_derived` divide by zero before any seal check. The same happens resealed and unresealed.
- **(d):** today's `_structure` has no INV-11 or INV-12 row, so neither code is ever emitted.
- **(c), (e), (f) pass at 20cd29de.** Every operator gets a resealed non-digest refusal. Checker-clean mutants are refused only with `inv_38`/`inv_39`. The legal corpus got zero refusals and nothing emitted `internal:`.
- **E2 (duplicate live placement accepted) does not show up here.** In ex-10 E2 the forged roster was sealed by the packer itself (`_seal(finalize=True)`). A resealed mutant submitted through the public entries is not sealed by the packer, so it is replayed and refused (`stale_derived`/`inv_39`).

## V2: head `04962287`
```
Ran 28 tests in 267.480s
OK
GENERATOR seed=291013 cases=60 edges={'E1': 298, 'E10': 170, 'E11': 30, 'E2': 432, 'E3': 1041, 'E4': 212, 'E5': 54, 'E6': 84, 'E7': 95, 'E8': 24, 'E9': 7}
GENERATOR seed=291014 cases=60 edges={'E1': 311, 'E10': 171, 'E11': 36, 'E2': 480, 'E3': 1122, 'E4': 206, 'E5': 61, 'E6': 89, 'E7': 75, 'E8': 24, 'E9': 8}
GENERATOR signatures differ 60/60
STRESS seed=291013 registrations=300 calls=4263 checker_calls=4863 violations=0 ...
STRESS seed=291014 registrations=300 calls=4253 checker_calls=4853 violations=0 ...
```
So the new item-centric checker agrees with the packer exactly on every legal roster in both corpora.

## V3
```
diff --check: clean
git status --short: (empty)
 tests/scored_case_generator.py      | 119 ++++
 tests/scored_roster_checker.py      | 156 +++---
 tests/test_scored_packer_fuzz.py    | 234 ++++++
 tests/test_scored_packer_stress.py  |  28 +
 tests/test_scored_roster_checker.py |  93 ++--
 5 files changed, 525 insertions(+), 105 deletions(-)
```
Commits: `8afca9b9` (checker, INV-11, `refresh_derived`, R4d witness), `0b60ebab` (generator, variation test, fuzz), `04962287` (window lookup and executed validation rewritten so they no longer copy the old checker's lines).

## V4: independence declaration
I did not read `joulewise/scored_packer.py` or `tests/test_scored_packer.py`, in any checkout or commit. I did not open the 02-*/03-*/06-* consult and plan files of activation 7370d0fb, or anything under `wt-7370d0fb-a291p`.

Two disclosures:
- I listed the packer module's public names and the signatures of its public callables with `dir()` and `inspect.signature`.
- One background command also printed `dir(sp)` including private attribute names. That was names only, no source.

I did not run the similarity screen against the packer, because that would mean inspecting it. Instead I ran a proxy screen against my own pre-round checker at 20cd29de, which the ruling confirms is a 29/33 transcription of the packer's `_derived`:

| New function | vs its old counterpart |
|---|---|
| `_derived` | 6/27 = 0.22 (generic lines) |
| `_window_of` | 2/15 = 0.13 |
| `refresh_derived` | 5/23 = 0.22 |

`check_executed` scores 9/14 against the old `check_executed`, but the matched lines are checker-only `_bad`/INV/`violations` lines and the docstring. The real screen is still the delta re-audit's job.

**Files I read:**
- My own five in-scope files and `tests/test_scored_registration.py`.
- ex-02d contract v4: the heading list, §0.4, §1.2, §3.4–§4.2, §5 rows C/F/G, §6, §10.
- ex-10 in full, ex-21 in full, and ex-31.
- The addendum-2 ruling in full, and the addendum-3 ruling §0–§2.
- ex-37 excerpts B1/B2/M1.
- `ex-41-astra-similarity.py`, `ex-41-astra-similarity_evasion.py`, `ex-41-astra-targeted.py`.

## Notes for the magistrate
- **H set for the extended screen:** `_window_of` (reached from `_derived`) and `_static_checks`. I changed `_static_checks` for the INV-11 row, and it is reachable from `check_executed` through `check_roster`. `_unreported` and `_window_keys_ok` have fewer than 5 normalised lines, so they are not scored.
- **Fuzz `CASES`:** I picked four short runs that contain splits. Two of them (291013:10 and 291014:3) contain cells whose last live parent operator 1 can void. That choice is what makes (a) reachable at 20cd29de.
- **Runtime:** the fuzz takes about 55 s. The stress module takes about 4.5 min, of which the new test is about 97 s.

The claude.ai Anthropic Economic Index connector needs authorization in its claude.ai connector settings. This round did not use it.
