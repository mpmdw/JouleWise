# Record 90 — Opus contract-lens counter-review: EVIDENCE-PLAN-PATH-BINDING-01

Reviewer: Opus 5 (1M), read-only, worktree `/Users/edr/code/JouleWise-wt-ppopus-d0b83820`.
Subject: `9a0d8fa853cbdbad1177a0588891b23d4966d225` on `fix/2026-09-19-evidence-plan-path-binding`
(diff `a9e48ae9..9a0d8fa8`, four files). Nothing written outside `/tmp/magistrate-d0b83820/opus-90/`.

```
$ git -C /Users/edr/code/JouleWise-wt-ppopus-d0b83820 log -1 --format='%H %d%n%s'
9a0d8fa853cbdbad1177a0588891b23d4966d225  (HEAD, origin/fix/2026-09-19-evidence-plan-path-binding, fix/…)
EVIDENCE-PLAN-PATH-BINDING-01: the evidence wrapper binds the published plan path (ruling 87a)
$ git diff --stat a9e48ae9 9a0d8fa8
 joulewise/night_agent_install.py  |  5 ++++-
 scripts/gen_evidence_night.py     |  4 +++-
 tests/test_gen_evidence_night.py  | 20 +++++++++++++++++++-
 tests/test_night_agent_install.py | 30 ++++++++++++++++++++++++++++++
```

**Verdict: MERGE-WITH-FIXES.** The ruled mechanism is implemented correctly and the
regressions kill the obvious mutant. Two sub-blocker defects are worth ≤3 lines each at
the bench before the pilot arm; neither is reachable on today's production custody root,
so a magistrate who wants to arm tonight may merge as-is and land the fixes in the same
follow-up commit.

---

## 1. Contract fidelity — does the diff implement exactly ruling 87a?

Ruling 87a requires five things. All five are present; I found no extra behaviour.

| Ruled clause | Call site | Present |
|---|---|---|
| wrapper binds the DERIVED published path `<custody_root>/night_plan.json` (content, not argument) | `scripts/gen_evidence_night.py:48-49` | yes |
| `evidence_probe_bindings` compares against the same derivation | `joulewise/night_agent_install.py:897,900` | yes |
| …and additionally refuses an install whose plan path is not that published path | `joulewise/night_agent_install.py:898-899` | yes (see finding S1 on *how*) |
| fixture/tests move the plan to `<custody>/night_plan.json` | `tests/test_gen_evidence_night.py:48` (`plan.json` → `night_plan.json`) | yes |
| three regressions | `tests/test_gen_evidence_night.py:131`, `tests/test_night_agent_install.py:1900,1908` | yes |

No deviation in scope: nothing else in either module changed, no doc or lane file was
touched (the ruling defers lane registration to the next kernel touch), and the generator
still refuses everything it refused at `a9e48ae9`.

One observation that *strengthens* the ruling's premise rather than contradicting it. The
defect at main was worse than an install-time refusal: `joulewise/quiet_predicate_campaign.py:95`
reads the plan from `EVIDENCE_PLAN_PATH` at night time —

```python
def verify_environment():
    plan_path = Path(os.environ["EVIDENCE_PLAN_PATH"])
    plan = night_gate.NightPlan.from_mapping(json.loads(plan_path.read_text()))
```

— so after §1.4's `os.replace` moved the staged bytes away, a wrapper carrying the staging
path would have raised `FileNotFoundError` inside the chain and refused the night, not just
the install. The fix closes both.

## 2. Docs vs code — contradictions

**No contradiction found.** I grepped for the failure shapes named in the brief:

```
$ grep -rn "EVIDENCE_PLAN_PATH" . --exclude-dir=.git
./scripts/night_chains/quiet_predicate_evidence.zsh:7    ./scripts/gen_evidence_night.py:49
./joulewise/quiet_predicate_campaign.py:95,555           ./joulewise/night_agent_install.py:900
./tests/…                                    (no docs hit at all)
$ grep -rn "plan path|--plan argument|path given at" docs/process docs/phase_2 docs/contracts --include="*.md"
```

No sentence anywhere says the wrapper records "the plan path given at render time", and no
sentence permits installing from a staging path. The three prose sites that touch this rule
all agree with the code's *direction*:

- `docs/phase_2/derivation_night_runbook.md:717-718` — "The installer requires the resolved
  plan path to be `<custody_root>/night_plan.json`; staging is never an install destination."
- `docs/process/MAGISTRATE_WATCHDOG.md:35` — "The installer also requires the resolved plan
  path to be its own `<custody_root>/night_plan.json`."
- `docs/phase_2/derivation_night_runbook.md:1709` — "`plan_outside_custody_root` | 2 | Real
  install only: resolved `--plan` is not the plan's `<custody_root>/night_plan.json` …
  `--render-only` accepts a staged plan and renders that future published path into both plists."

They agree on direction but differ on **normalisation**: all three say *resolved*, and the new
check uses `Path(...).absolute()`. That is finding S1, not a doc bug.

Three omissions, all nit-grade (recorded as N2 below): the runbook's traceability row
`:3179` — "The plan is an INPUT to the generator, and the wrapper's bytes depend on the
plan's CONTENT not its path | `scripts/gen_derivation_night.py` …" — still names only the
derivation generator, though `scripts/gen_evidence_night.py` is now a second enforcement
site for the same invariant; and neither new refusal text (`evidence plan not at its
published path`, `evidence plan path mismatch`) appears in the runbook refusal table
(`:1704-1715`) or the `NIGHT_HANDBACK.md` cold-gate table (`:112-122`).
`docs/process/NIGHT_COURIER_PROMPT.md` carries no plan-path prose (`{custody_root}` only),
and `docs/contracts/*` has nothing on the evidence plan path.

## 3. Is `custody_root` guaranteed absolute, and equal to the publication directory?

**No — and that is a finding (S2).** The absoluteness guard is pack-only:

```python
# joulewise/night_gate.py:355   custody_root = require_text("custody_root")      # non-empty str, nothing more
# joulewise/night_gate.py:357   pack_night = None
# joulewise/night_gate.py:358   if is_pack:
# joulewise/night_gate.py:375-376     if not os.path.isabs(custody_root):
#                                         raise PlanError("night_plan_malformed", "pack custody_root must be an absolute path")
```

`_authenticate_pack_records` (`night_gate.py:772-776`, the only other guard — "custody_root:
non-absolute or symlinked") is likewise reached only for pack nights. An evidence plan is
`DIAGNOSTIC_NO_PACK` with `pack_night=None` (`gen_evidence_night.py:22-23` refuses anything
else), so **nothing on the evidence path requires `custody_root` to be absolute**. The
derivation generator guards itself — `scripts/gen_derivation_night.py:604`,
`window_custody_root=_require_absolute("window custody root", plan.custody_root)` — but
`gen_evidence_night.generate` applies only `_census_clean` and `_quote` (`:35-38`).

Executed (probe script at `/tmp/magistrate-d0b83820/opus-90/probe_paths.py`, run against the
unmodified worktree):

```
### PROBE 1: relative custody_root in an evidence plan
custody_root written into the plan: ../../../../tmp/qpe-fixture-rg2fkw6d/custody
NightPlan.from_mapping accepted a RELATIVE custody_root: ../../../../tmp/qpe-fixture-rg2fkw6d/custody
generator emitted EVIDENCE_PLAN_PATH = '../../../../tmp/qpe-fixture-rg2fkw6d/custody/night_plan.json'
is absolute: False
evidence_probe_bindings refused: evidence plan not at its published path
```

So a relative `custody_root` seals a **relative** plan path into the sealed wrapper bytes.
It is fail-closed (the install refuses, and the night would refuse too, since launchd gives
the chain no useful cwd), but the desk loses the catch and an arm attempt is spent.

Trailing slash is **benign** and I verified the reasoning rather than assuming it:
`PurePath` normalises `"/a/b/"` to `/a/b` and collapses interior doubled separators, and both
sides of the comparison run through the same `Path(...) / "night_plan.json"` construction, so
`/a/b/`, `/a/b`, and `/a//b` all derive the identical literal. `..` components are *not*
normalised by `pathlib`, so `custody_root="/a/b/../b"` would refuse at install — again
fail-closed, not a silent mismatch.

## 4. Consumers — do they all agree on the published path?

| Consumer | What it reads | Path it gets |
|---|---|---|
| `scripts/night_chains/quiet_predicate_evidence.zsh:7` | `: "${EVIDENCE_PLAN_PATH:?required}"` | the wrapper's export |
| `joulewise/quiet_predicate_campaign.py:95, 555` | `Path(os.environ["EVIDENCE_PLAN_PATH"])` | `<custody_root>/night_plan.json` after the fix |
| `scripts/run_night.py` driver | `--plan` from the plist's `ProgramArguments` | `Prepared.plan_path`, forced equal to the published path by `admit` |
| `scripts/run_night.py:3475` probe supervisor | `plan_path = plan_path.absolute()`, passed to `_evidence_probe_worker` → `evidence_probe_bindings` (`:3540, :3553`) | same |
| `scripts/magistrate_watchdog.py:286` | `self.root.parent.glob("*/night_plan.json")` | discovers exactly the published filename |
| installer, night + dead-man plists | `night_agent_install.py:608-612` `render()`: `plan_path = self.plan_path if require_published else (Path(self.plan.custody_root) / "night_plan.json").resolve()`; substituted into `@@PLAN@@` | published path in both modes |
| installer, probe plist | `night_agent_install.py:970-977` `render_probe()`: `"@@PLAN@@": str(prepared.plan_path)` | published path on the real install (admit ran first) |

They agree in production. The two normalisations in play are `.resolve()` (`admit`, `render`)
and `.absolute()` (the new check, the probe supervisor). On the real custody root they are
the same string —

```
$ ls -ld /Users/edr/night-custody /Users/edr /Users
drwxr-xr-x@ 9 edr  staff  288 Sep 19 03:13 /Users/edr/night-custody
drwxr-x---+ 72 edr staff 2304 Sep 19 17:58 /Users/edr
drwxr-xr-x  6 root admin  192 Sep  2 20:35 /Users
```

— no symlink on any component, so `.resolve()` is the identity there. Finding S1 covers the
case where it is not.

One narrow pre-existing asymmetry, out of ruling scope and recorded only for completeness:
`render()` substitutes the derived published path for the night and dead-man plists under
`--render-only`, but the probe branch delegates to `render_probe`, which always uses
`prepared.plan_path`. On a staged render-only dry check the probe plist would therefore name
the staging path while the other two name the future published path. No production path
reaches it (`validate_install:1141` skips probe validation whenever `--render-only` is set).

## 5. Tests — are these the ruled three, and do they kill the mutant?

The three regressions map one-to-one onto the ruling:

1. `tests/test_night_agent_install.py:1900 test_staged_render_then_atomic_publication_passes_bindings`
   — author at staging → render → `os.replace` into custody → bindings PASS.
2. `tests/test_night_agent_install.py:1908 test_staged_plan_refused_before_publication`
   — render from staging then probe from staging → refused, with the message anchored
   (`"^evidence plan not at its published path$"`).
3. `tests/test_gen_evidence_night.py:131 test_staged_and_published_plan_render_identical_bytes`
   — all four artefacts byte-identical whether rendered from the staged or the published path.

Baseline, both modules at HEAD from the worktree:

```
$ env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp …/.venv/bin/python -B -m unittest tests.test_gen_evidence_night
Ran 8 tests in 3.050s / OK
$ … -m unittest tests.test_night_agent_install
Ran 63 tests in 721.190s / OK
$ … -m unittest tests.test_run_night.EvidenceProbeTests tests.test_run_night.EvidenceProbeFailureTests
Ran 23 tests in 17.444s / OK
```

**Mutant 1 — restore `str(plan_path)` in the generator.** Scratch copy at
`/tmp/magistrate-d0b83820/opus-90/mutant` (`git archive HEAD | tar -x`, then sed on line 49;
the worktree was never touched). Killed twice, by two independent regressions:

```
FAIL: test_staged_and_published_plan_render_identical_bytes
AssertionError: '/tmp/qpe-fixture-ftohh4pv/staging/night_plan.json'
             != '/tmp/qpe-fixture-ftohh4pv/custody/night_plan.json'
Ran 8 tests / FAILED (failures=1)

ERROR: test_staged_render_then_atomic_publication_passes_bindings
  File ".../joulewise/night_agent_install.py", line 901, in evidence_probe_bindings
    raise ValueError("evidence plan path mismatch")
Ran 2 tests / FAILED (errors=1)
```

**Mutant 2 — delete only the new installer refusal** (lines 898-899), keeping the generator
fix. Scratch copy at `…/opus-90/mutant2`. Also killed, and the kill is informative: without
the guard the staged path is *accepted*, because after the generator fix the wrapper's
literal matches the derivation regardless of where the plan file sits.

```
FAIL: test_staged_plan_refused_before_publication
    with self.assertRaisesRegex(ValueError, "^evidence plan not at its published path$"):
AssertionError: ValueError not raised
Ran 2 tests / FAILED (failures=1)
```

So both halves of the ruled change are independently pinned.

## 6. Findings

### S1 — should_fix: the new guard uses a different path normalisation from `admit` and from the documented contract

**Call site.** `joulewise/night_agent_install.py:897-899`

```python
published_plan_path = Path(plan.custody_root) / "night_plan.json"
if Path(plan_path).absolute() != published_plan_path:
    raise ValueError("evidence plan not at its published path")
```

versus the same rule fifteen lines of logic earlier in the same module,
`joulewise/night_agent_install.py:588`:

```python
if require_published and self.plan_path != (Path(self.plan.custody_root) / "night_plan.json").resolve():
```

`.absolute()` prepends the cwd and stops; `.resolve()` additionally follows symlinks and
normalises `..`. Two consequences.

(a) *In production the new check is unreachable.* `validate_install` calls
`prepared.admit(...)` at `:1130` and only then `validate_probe_receipt(...)` at `:1141`, so on
any real install `plan_outside_custody_root` fires first with an identical predicate. The new
refusal therefore adds coverage only for direct API callers (the regression test, and
`run_night.py:3540`'s probe worker).

(b) *Where the two normalisations disagree, they are mutually unsatisfiable* — the install
becomes impossible, with a message that names neither contradiction. Executed:

```
### PROBE 2: custody_root reached through a symlink
plan.custody_root                      : /tmp/qpe-fixture-3sxj809k/link
Prepared.admit() demands --plan ==      : /private/tmp/qpe-fixture-3sxj809k/custody/night_plan.json
evidence_probe_bindings demands        : /tmp/qpe-fixture-3sxj809k/link/night_plan.json
  --plan = resolved form (what admit accepts): admit_ok=True;  bindings REFUSE: evidence plan not at its published path
  --plan = literal form  (what bindings want): admit_ok=False; bindings ACCEPT
  same file? True | st_ino equal: True
```

Both candidates name the *same inode*; no attack is being refused, only the operator.

**Counterfactual.** Today `/Users/edr/night-custody` and every parent is a real directory, so
this cannot fire. It fires the first time a custody root is reached through a symlink — which
this project already contemplates: the iCloud-offload practice archives and relinks retained
roots, and `NIGHT_HANDBACK.md:547-551` keeps clone and night root as retained production
custody after any night that opened a session. A relinked retained root makes every
subsequent evidence install unarmable.

**Fix (2 lines, bench-sized).** Test file identity by resolution, keep the sealed literal
content-derived:

```python
published_literal = Path(plan.custody_root) / "night_plan.json"          # content-derived; seals
if Path(plan_path).resolve() != published_literal.resolve():
    raise ValueError("evidence plan not at its published path")
if night_gate.chain_literal(chain.read_text(), "EVIDENCE_PLAN_PATH") != str(published_literal):
    raise ValueError("evidence plan path mismatch")
```

**Do not resolve in the generator.** `scripts/gen_evidence_night.py:48` must keep emitting the
unresolved literal: resolving there would make the sealed wrapper bytes depend on filesystem
state at render time, which is exactly the "bytes depend on content, never on path" invariant
(runbook §1.1b, `:1028-1031`) that ruling 87a exists to restore. A one-sided change to either
file alone re-breaks the pair, so this fix is only correct applied to the installer.

### S2 — should_fix: the evidence generator does not require `custody_root` to be absolute

**Call site.** `scripts/gen_evidence_night.py:35-38` census/quote loop and `:48` derivation;
compare `scripts/gen_derivation_night.py:604`, which guards the same field with
`_require_absolute`. `night_gate.NightPlan.from_mapping` enforces absoluteness only for pack
plans (`night_gate.py:375-376`, inside `if is_pack:`), and an evidence plan is never a pack.

**Counterfactual.** An evidence plan authored with `custody_root` relative (or containing
`..`) renders a wrapper whose `EVIDENCE_PLAN_PATH` is relative — proven above, probe 1. The
desk accepts it; the failure surfaces only at install (exit 2, message naming a path the
operator never typed), and if the S1 guard were ever relaxed it would surface at 02:56 inside
the chain, since launchd hands the job no useful cwd. The generator is the one place that can
catch it at the desk, before the notice is sent.

**Fix (1 line).** Import `_require_absolute` alongside `_quote`/`_census_clean` from
`scripts.gen_derivation_night` and call `_require_absolute("night custody root", plan.custody_root)`
in `generate()` before the derivation. It refuses as `GenerationRefusal`, which `main` already
prints as `REFUSED: …` and exits 2.

### N1 — nit: the new test class is defined after the module's `unittest.main()`

`tests/test_night_agent_install.py:1881-1883` ends with `if __name__ == "__main__":
unittest.main()`, and `EvidencePlanPublicationTests` is defined at `:1885`, after it (as
`EvidenceProbeReceiptTests` already was — pre-existing pattern). CI invokes
`python -m unittest -v tests.<module>` (`.github/workflows/ci.yml:113`, `:264`,
`d117-production-proof.yml:42`), which imports the module and collects everything, so
coverage is real. Only a direct `python tests/test_night_agent_install.py` would silently run
a subset. Counterfactual: a future operator debugging the arm by running the file directly
concludes the publication regressions passed when they never ran.

### N2 — nit: three documentation omissions (no contradiction)

- `docs/phase_2/derivation_night_runbook.md:3179` — the content-not-path invariant row names
  only `scripts/gen_derivation_night.py`; `scripts/gen_evidence_night.py` now enforces the
  same invariant and should be cited beside it.
- Neither `evidence plan not at its published path` nor `evidence plan path mismatch` appears
  in the runbook refusal table (`:1704-1715`) or `docs/process/NIGHT_HANDBACK.md:112-122`,
  so an operator who hits either has no documented recovery.
- `NIGHT_HANDBACK.md:592-594` ("An evidence payload instead binds the sealed manifest,
  harness and registration digests, and the tracked chain-source digest at the measurement
  commit") is accurate but silent on the plan-path binding the ruling just added.

### N3 — nit: dead census check on the staging path

`scripts/gen_evidence_night.py:35-38` still runs `_census_clean`/`_quote` over `str(plan_path)`
— a string that, after this change, is emitted nowhere. Harmless, and arguably worth keeping
as belt-and-braces, but it now refuses generation when the *staging directory* name contains
`codex`/`claude`/`t3` even though the wrapper can no longer carry it. The literal that does
get emitted is covered, since `plan.custody_root` is in the same tuple and the export loop
applies `_quote` at `:52`.

---

## Summary

| ID | Severity | One line |
|---|---|---|
| S1 | should_fix | `evidence_probe_bindings` compares with `.absolute()` where `admit` and the docs use `.resolve()`; under a symlinked custody root the two guards are mutually unsatisfiable (proven) |
| S2 | should_fix | `custody_root` is never required absolute on the evidence path, so a relative one is sealed into the wrapper (proven) |
| N1 | nit | new test class defined after `unittest.main()`; CI unaffected |
| N2 | nit | runbook traceability row and both refusal tables not updated |
| N3 | nit | census check on a staging path that is no longer emitted |

No blocker. Ruling 87a is implemented exactly, the three ruled regressions are present and
kill both the generator mutant and the installer-guard mutant, and no doc contradicts the
code. Both should_fix items are smaller than the brief needed to delegate them.
