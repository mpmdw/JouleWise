# Opus counter-review — decode-identity, HEAD 3903696c (gate ledger item 6)

Worktree `/Users/edr/code/JouleWise-wt-decode-id`, branch `fix/2026-09-02-decode-identity-set`.
Branch is **124 behind / 32 ahead** of `origin/main`, so the origin/main diff is dominated by main-side work absent here; charge (4) is answered against `git merge-base` = `3e6243df`.

## Charge (1) — the three prose-only commits since 90689048

8 hunks, all in `docs/contracts/identity_pin_projection.md`. Every factual claim checked against code read this session:

| Claim (line at HEAD) | Verdict |
|---|---|
| :468 "resolved path stays **below the campaign-pack directory**" | TRUE, and stricter than the replaced "within the campaign pack": `_declared_manifest_path` rejects empty `relative_parts`, then `_resolve_config_path` requires containment + regular non-symlink (`identity_pins.py:1540-1566`, `:1495-1521`). |
| :572-574 citations `verify_frozen_projection` / `_run_identity_arm_reverification` | TRUE. `identity_pins.py:2379`, `arm_readiness.py:5681`; the latter calls the former and maps `IdentityPinProjectionError.reason_code` into readiness reasons — the sentence's exact claim. |
| :588-590 pack digest = SHA-256 over committed pack files, "their paths, file modes and content digests", by `committed_pack_tree_sha256` | Names a real function (`arm_readiness.py:2750`) and true as far as it goes, but **incomplete** — see SF1. |
| :622-624 lineage locator "stored in a runs root (the directory under which a launch's collected bundles are written)" | TRUE. `_publish_launch_lineage_locator` (`arm_readiness.py:9867`) writes the locator into the resolved root; call sites pass `claim_runs_root` / `bound_runs_root` (`:10059-10066`). |
| :633-635 `consumer_identity_set_unauthenticated` gloss, "distinct member identity set, built above" | TRUE in reader order: the term is bold-defined at :109, used here at :635. |
| :660-662 "bundle loading (the bundle-to-analysis admission step, called input loading below where it refuses)" | TRUE; `_read_bundle` at `joulewise/analysis_engine/inputs.py:2735`. |
| :680 "`.sha256` sidecar (the digest file written beside it)" | TRUE — `path.with_name(f"{path.name}.sha256")` written beside the locator. |
| :687-688 S3 ruling cited as a bare repo path | TRUE; file present in this branch's trace dir. |
| :740 `**ordinary launch step**` demoted to plain | Correct demotion; see N3. |

## Charge (2) — file 51 findings at HEAD

| Item | Closed? | Evidence |
|---|---|---|
| **B1** landing record called a hand-typed table "mechanical" | CLOSED | File 52 :81 pastes the mechanical re-run; :130 explicitly corrects file 50's description. |
| **S1** "bundle loading" vs "input loading" undeclared alias | CLOSED | :660-662 declares the alias at first use. |
| **S2** bold `**pack digest**`, `**ordinary launch step**` undefined | CLOSED | Pack digest glossed at :588-590 (but SF1); ordinary launch step de-bolded at :740. |
| **S3** "consumer identity set" used inside its own code's gloss | CLOSED | :633-635 now says "the consumer's distinct member identity set, built above" (defined :109). |
| **S4** collateral edits at :572 / :468 | CLOSED | :572 citations restored and verified; :468 kept as a deliberate, code-true improvement. |

## Charge (3) — professor read of §Analysis-gate definitions + §Analysis consumption

Both sections replicate except one term.

| Sev | ID | Finding |
|---|---|---|
| SHOULD-FIX | **SF1** | **Pack digest is glossed twice, and the two glosses disagree.** :588-590 (the *bold definition*) says "paths, file modes and content digests". :711-714 (step 2) says "each path, Git mode, byte length and content digest in path order". The code frames `path \0 mode \0 len(bytes) \0 sha256 \n` over `sorted(committed)` (`arm_readiness.py:2866-2874`). A reader rebuilding the digest from the *definition* gets a different value than the code produces. Cure is one line: make :588-590 match :711-714 or defer to it. |
| NIT | N1 | Dead alias: :633-634 promises "called the analysis gate below", but "analysis gate" never appears below — only "analysis input gate" (:649) and bare "the gate". The declaration is self-refuting as written. |
| NIT | N2 | Four added prose lines (:468, :590, :680, :688) run 85-124 cols, breaking the file's ~78-col prose wrap; bench cures were edited in place without re-wrapping. |
| NIT | N3 | :740-741 "…as defined in §Analysis-gate definitions" attaches ambiguously — readable as claiming "ordinary launch step" is defined there; it is not (the four named objects are). "(each defined in §Analysis-gate definitions)" removes it. |

## Charge (4) — path scoping (vs merge-base 3e6243df)

85 files, **no strays** — every path is inside the charge's allowlist: the contract doc; exactly two trace dirs (`2026-09-02-decode-identity-set`, `2026-09-02-fresh-fable-audit`); `joulewise/identity_pins.py`, `analysis_engine/{__init__,inputs}.py`, `detection_floor.py`; `tests/test_{analysis_inputs,analysis_integration,d117_contrast_v5_pack,detection_floor,identity_pins}.py`; `configs/campaigns/d117_contrast_v5/generate_configs.py`; `docs/contracts/d165_dominance_closeout.md`; `docs/decision_log.md` (+31); `docs/phase_2/gamma_arm_readiness.md`; `docs/specs/c027/p2-039_floor_artifact.md`. All match an earlier round's intended change.
`joulewise/arm_readiness.py` and `tests/test_arm_readiness*.py` appear in the origin/main diff but **not** the merge-base diff — main-side, not branch work.

## Tests

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs
..................
----------------------------------------------------------------------
Ran 18 tests in 63.870s

OK
```

## Verdict

**FIX FIRST** — one-line SF1 cure (align the bold pack-digest definition at :588-590 with the framing at :711-714); N1-N3 optional. No blockers; B1/S1-S4 all closed; no stray paths; the branch needs a rebase onto origin/main (124 behind) before merge anyway, so the cure is free.
