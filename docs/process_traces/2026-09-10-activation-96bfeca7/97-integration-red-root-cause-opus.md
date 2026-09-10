# Root cause + fix: integration head 51565cee RED (three clusters)

Worktree `/Users/edr/code/JouleWise-wt-epoch-integration`, branch
`feat/2026-09-10-epoch-integration`, HEAD `51565cee` (unchanged — no commit, checkout, stash,
reset or push; edits left in the working tree). No `[QUIET-MAC]`, no sudo, no live powermetrics.
`PYTHONDONTWRITEBYTECODE=1` on every subprocess.

All three clusters are closed. **None of the fourteen failing results was a defect in the S2
production code**: cluster A is a missing fixture file in the *authoring test fixture repository*,
cluster B is a pure line-number shift of eight already-classified I/O sites, cluster C is one
missing census row for the branch's new script.

## Touched paths (3)

- `tests/test_arm_readiness_evidence_author.py` (+6 lines: one copy-list entry + comment)
- `tests/test_authentication_io.py` (8 line pins updated in `CLASSIFIED_NON_AUTHENTICATION_READS`)
- `tests/fixtures/custody_read_replay_allowlist.json` (+1 row)

No production file was changed; no `joulewise/` or `scripts/` file was touched.

---

## Cluster A (10 of 14) — the nested focused suite's failing test, recovered

### Recovering the id

`_run_suite` → `_execute_unittest_suite_subprocess`
(`joulewise/arm_readiness_evidence.py:628-786`) runs the focused suite in an isolated child
(`sys.executable -I -B -c _SUITE_SUBPROCESS`, `cwd=repository`, env stripped to
`JOULEWISE_SUITE_REPOSITORY` / `JOULEWISE_SUITE_TEST_IDS` / `LANG=C` / `LC_ALL=C`). The child's
JSON payload **does** carry a `failed_ids` list (built at
`joulewise/arm_readiness_evidence.py:608-611` and emitted in the `print(json.dumps(...))` block),
but `_parse` never reads that key, so the id is dropped before the refusal is raised. Rerunning the
same child by hand against the same fixture repository recovers it
(`/tmp/rc-seat/repro_a.py`, which builds the fixture through
`tests.test_arm_readiness_evidence_author.make_author_fixture` under the same three mock patches
the relocation test uses, then invokes `evidence._SUITE_SUBPROCESS` verbatim):

```
FIXTURE_REPO /var/folders/.../T/tmpzbtpa4vh/repo
RC 0
tests_run 92 failures 0 errors 1
FAILED_IDS [
 "tests.test_calibration_ledger.DerivationSessionSlotTests.test_production_ledger_fixture_parses_and_reserializes_byte_identically"
]
```

Traceback (same test rerun inside the kept fixture repository with the same interpreter,
`/opt/homebrew/bin/python3` 3.14.7, `env -i LANG=C LC_ALL=C`):

```
ERROR: test_production_ledger_fixture_parses_and_reserializes_byte_identically
  File "/tmp/rc-seat/fixture-repo/tests/test_calibration_ledger.py", line 3829,
    in test_production_ledger_fixture_parses_and_reserializes_byte_identically
    raw = self.PRODUCTION_LEDGER.read_bytes()
FileNotFoundError: [Errno 2] No such file or directory:
  '/private/tmp/rc-seat/fixture-repo/tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl'
```

### Root cause

The assumption is a **fixture data path**, not an absolute path, a `git` invocation or an
environment variable. S2's new `DerivationSessionSlotTests` pins the 76-row production ledger
prefix through a class constant computed relative to the test module
(`tests/test_calibration_ledger.py:3148-3155`):

```python
PRODUCTION_LEDGER = (
    Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    / "d117_v2_production" / "issued" / "calibration_observation_ledger.jsonl"
)
```

That resolves correctly in a normal checkout, so the module passes standalone (92 tests). The
`RECOVERY_LEDGER_TEST` deriver (`joulewise/arm_readiness_evidence.py:2427`) runs the same module
**inside the minimal authoring fixture repository** built by
`tests/test_arm_readiness_evidence_author.py:make_author_fixture` (line 104). That repository is
deliberately minimal: an explicit copy list of ~30 files, every `joulewise/**/*.py` and
`scripts/**/*.py`, one `tests/fixtures/calibration_live_three_window/scenario.json`, and one
config campaign tree. It does **not** contain `tests/fixtures/d117_v2_production/`, so
`__file__`-relative resolution lands on a path that exists in the real checkout and not in the
fixture repository → `FileNotFoundError` → `errors=1` → `EvidenceAuthoringError: focused suite
refused` at `arm_readiness_evidence.py:781`, which is what every relocation call site reports.

"Relocation" was a red herring in the diagnosis sense: the copy is minimal, not merely moved. Any
test added to `tests.test_calibration_ledger` that reads a repository file must have that file in
the authoring fixture repository.

### Fix (test-side; the assumption is in the fixture, not in production)

`tests/test_arm_readiness_evidence_author.py:146-151` — one entry added to the existing
`_copy_primary` list (which already carries `.json`/`.md` data files, so this uses the established
route), with the reason recorded inline:

```python
        "tests/test_calibration_ledger.py",
        # RECOVERY_LEDGER_TEST runs `tests.test_calibration_ledger` as a focused
        # suite INSIDE this minimal repository, so every file that suite reads
        # must exist here too.  `DerivationSessionSlotTests.PRODUCTION_LEDGER`
        # reads the committed 76-row production ledger prefix by a path relative
        # to the test module, which resolves into this fixture repository.
        "tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl",
```

The file is committed at this head (`tests/fixtures/d117_v2_production/issued/…`, introduced by
`add914ac` on main), and `make_author_fixture` ends with `git add .` + commit, so the copy is part
of the fixture repository's reviewed HEAD and passes the author's SHA-binding gates.

### Proof the cluster is closed

Same repro after the fix:

```
RC 0
tests_run 92 failures 0 errors 0
FAILED_IDS []
```

plus the real relocation call sites in the verification run below
(`tests.test_arm_readiness_dry_run`, `tests.test_launch_window`,
`tests.test_arm_readiness_evidence_author`).

---

## Cluster B (1 of 14) — not eight new direct-IO sites; eight line-shifted classifications

### Root cause

The guard `tests/test_authentication_io.py:400` keys each sanctioned site by
`path:function:LINE:call` in `CLASSIFIED_NON_AUTHENTICATION_READS`
(`tests/test_authentication_io.py:58-97`). All eight reported "violations" are the **same eight
sites already classified there**, shifted by exactly **+121 lines** by S2's insertion above them:

| classified (main) | reported (51565cee) | statement at both lines |
|---|---|---|
| `_filesystem_type:2862:read_text` | `:2983:` | `lines = mountinfo.read_text(encoding="utf-8").splitlines()` |
| `_open_slot_sidecar:2966:os.open` | `:3087:` | `descriptor = os.open(` |
| `resolve_ledger_lease_identity:2914:os.open` | `:3035:` | `parent_descriptor = os.open(` |
| `resolve_ledger_lease_identity:2928:os.open` | `:3049:` | `object_descriptor = os.open(` |
| `publish_genesis_payload:3242:os.open` | `:3363:` | `descriptor = os.open(` |
| `open_append_descriptor:3297:os.open` | `:3418:` | `descriptor = os.open(` |
| `repair_calibration_ledger:3928:os.fdopen` | `:4049:` | `with os.fdopen(descriptor, "r+b", closefd=False) as handle:` |
| `abandon_calibration_ledger_tail:3985:os.fdopen` | `:4106:` | `with os.fdopen(descriptor, "r+b", closefd=False) as handle:` |

Decisive evidence that S2 added **no** direct readable I/O at all:

```
$ git diff origin/main..HEAD -- joulewise/calibration_ledger.py \
    | grep "^+" | grep -E "read_text|read_bytes|os\.open|os\.fdopen|\bopen\("
(no output)      # 287 insertions, 47 deletions, zero added read-capable I/O calls
```

So the per-site question the brief asks ("read that must be routed, or write/lock primitive?") was
already answered on main for each of the eight, and those answers still hold verbatim because the
statements are byte-identical: two are lock/inode descriptors (`_open_slot_sidecar`,
`resolve_ledger_lease_identity` ×2 — fd used for `fstat`/pathname binding, never content), one is a
staging descriptor for newly written genesis output (`publish_genesis_payload`), one is the writer
lane's `O_RDWR` descriptor factory whose read-consumers are classified at their own sites
(`open_append_descriptor`), two are the recovery/operator-lane repair scans of
possibly-corrupt physical bytes where registration is inapplicable because the bytes' integrity is
the thing under repair (`repair_calibration_ledger`, `abandon_calibration_ledger_tail`), and one is
Linux `mountinfo`, which is OS filesystem topology and not project evidence (`_filesystem_type`).
Nothing was newly exempted and no new marker was invented — only the eight line numbers moved.

### Fix

`tests/test_authentication_io.py:58-97` — the eight `LINE` fields in
`CLASSIFIED_NON_AUTHENTICATION_READS` updated `+121`, every classification comment left intact.

### Residual risk (not closed, deliberately)

This guard pins absolute line numbers, so *any* future edit above these sites re-reds the suite
even when nothing about the I/O changed — exactly the failure mode the custody-mode inventory
explicitly designs out (`tests/test_custody_mode_inventory.py:
test_line_shift_does_not_require_allowlist_edit`, which keys on
`(file, function, ordinal)` and treats `line` as documentation only). Re-keying
`CLASSIFIED_NON_AUTHENTICATION_READS` on `(file, function, ordinal, call)` would remove a recurring
mechanical red without weakening the guard. That is a design change to a v2-surface guard, so I did
not make it here; recorded for adjudication.

---

## Cluster C (3 of 14) — one missing census row for the branch's new script

### Root cause

`tests/test_custody_mode_inventory.py` is an executable census: it walks every scanned file for
calls into `CUSTODY_CALLS` with `mode="read_replay"` and requires each such call to carry an
allowlist row in `tests/fixtures/custody_read_replay_allowlist.json` keyed
`(file, function, ordinal)` — the point being that opting a call site into replay custody (which
skips issuing-mode verification) is a reviewed act with a written one-line reason, and that a
*new* replay call cannot ride in on an existing row (`test_second_call_requires_its_own_allowlist_row`),
while a mere line shift must not force an edit (`test_line_shift_does_not_require_allowlist_edit`).

The branch's new `scripts/issue_calibration_acceptance_generation.py` calls
`load_calibration_ledger_snapshot(..., mode="read_replay", ...)` at line 96 inside `check`, the
first (and only) replay call in that function — hence the uncensused row
`('scripts/issue_calibration_acceptance_generation.py', 'check', 1)`. This is a missing row, not a
behavioural defect: `check` is a read-only desk epoch watch that prints an identity comparison
table and returns 3 on mismatch; it never mints, appends a receipt, publishes a binding, or
finalizes an analysis manifest, and the only other subcommand (`prepare-candidate`) returns 64
unimplemented (`scripts/issue_calibration_acceptance_generation.py:141-147`).

### Fix

`tests/fixtures/custody_read_replay_allowlist.json` — one row inserted in the file's existing
path-sorted position (after `scripts/extract_detection_floors.py`, before
`scripts/recover_calibration_ledger.py`):

```json
  {
    "file": "scripts/issue_calibration_acceptance_generation.py",
    "function": "check",
    "ordinal": 1,
    "line": 96,
    "reason": "Read-only desk epoch watch replays the existing ledger snapshot to compare identity fields and print a table; it never mints, appends a receipt, publishes a binding, or finalizes an analysis manifest, and the only other subcommand returns 64 unimplemented."
  },
```

Only what exists at this head is censused (15 rows total).

### What S4 will need (informational — NOT added here)

S4's `prepare-candidate` implementation and `--session-ids` dry run will each need their own row
**if and only if** they pass `mode="read_replay"` into a `CUSTODY_CALLS` function (an `"issuing"`
call needs no row, and a `mode` forwarded from a parameter is censused at the issuing caller, not
at the shared callee):

- `("scripts/issue_calibration_acceptance_generation.py", "<the function that literally holds the
  call>", 1)` — for the census the function name is the enclosing `def` (dotted for nesting, e.g.
  `"main.prepare"`), so a replay call placed directly in a new `prepare_candidate(args)` needs
  `function: "prepare_candidate", ordinal: 1`.
- If the `--session-ids` dry run adds a **second** replay call inside `check`, it needs its own row
  with `ordinal: 2` (ordinals count replay calls per function, in source order); the existing
  ordinal-1 row will not cover it.
- Each row needs a non-empty single-line `reason` and a positive `line`; `line` is validated but not
  part of the key, so a later shift does not force an edit.

---

## Verification run

### Command (exact)

```
cd /Users/edr/code/JouleWise-wt-epoch-integration && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_author \
  tests.test_authentication_io tests.test_custody_mode_inventory tests.test_launch_window \
  tests.test_calibration_ledger tests.test_calibration_ledger_custody tests.test_docs_freshness \
  > /tmp/rc-seat/verify.log 2>&1; rc=$?; echo "VERIFY_RC=$rc"
```

### Tail (all eight modules in one process, rc captured)

```
.........................................
----------------------------------------------------------------------
Ran 253 tests in 673.696s

OK (skipped=1)
KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer
VERIFY_RC=0
```

`VERIFY_RC=0`. 253 tests, 0 failures, 0 errors, 1 skip. Every previously failing result passes,
including all ten cluster-A relocation results
(`test_production_minted_dry_run_survives_repository_relocation`, the three
`ProductionArmRelocationLaunchTests` with their eight subtests, and
`test_authored_evidence_makes_synthetic_pack_freeze_pass`), the surface guard
(`test_marked_v2_surface_has_no_direct_readable_io`), and the three custody-census tests.

The `usage: python3.14 -m unittest ... unrecognized arguments: --allow-uncommitted-head-pin` line
early in the log is a test's own captured argparse refusal, not a harness error; the module it
belongs to reports PASS.

### Per-cluster targeted tails

Cluster B alone: `python3 -m unittest tests.test_authentication_io` → `Ran 22 tests in 1.019s / OK`.
Cluster C alone: `python3 -m unittest tests.test_custody_mode_inventory` → `Ran 7 tests in 34.151s / OK`.
Cluster A nested path alone (`/tmp/rc-seat/repro_a.py`): `tests_run 92 failures 0 errors 0 FAILED_IDS []`.

---

## Byte-identity note (cluster B)

No production bytes were changed by this seat, so S2's byte-identity witnesses are untouched by
construction: `joulewise/calibration_ledger.py` and
`scripts/reserve_calibration_window_bracket.py` are byte-identical to `51565cee`
(`git status --porcelain` lists only the three test/fixture paths above).

## Not closed

1. **The guard's line pins (cluster B, recommendation only).** `CLASSIFIED_NON_AUTHENTICATION_READS`
   keys on absolute line numbers, so this red recurs on any future insertion above
   `joulewise/calibration_ledger.py:~2900`. Re-keying it the way the custody census is keyed
   (`file, function, ordinal`) is a guard design change and needs a ruling.
2. **`_run_suite` discards the nested failure detail.** The child already reports `failed_ids`
   (`joulewise/arm_readiness_evidence.py:608-611`) and `_parse` drops it, so every future nested
   refusal costs a bespoke reproduction like this one. Surfacing `failed_ids` in the
   `EvidenceAuthoringError` message would be a small, evidence-preserving change to production
   code; I did not make it because it touches the authoring path's refusal text, which is
   contract-adjacent.
3. **S4's future census rows** are specified above but deliberately not added — only what exists at
   this head is censused.
