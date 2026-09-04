WRITE_SCOPE: ["joulewise/night_gate.py","scripts/run_night.py","scripts/install_night_agent.sh","tests/test_night_gate.py","tests/test_run_night.py","tests/test_install_night_agent.py","docs/process/NIGHT_HANDBACK.md","docs/process_traces/2026-09-03-night-plan-pin/**"]
ORIGIN: claude-fable-5 magistrate via Claude Code Sol bridge | BRIDGE_ORIGIN: claude | BRIDGE_HOPS_REMAINING: 0 | GENRE: implementation | EFFORT: high
BASE_HEAD: 12ec41d274bd3e7dfdb10800000604bd6ddff8f3
BASELINE_MANIFEST: .codex-bridge/baselines/planpin-20260903-sol-fix-01.json
BASELINE_DIGEST: sha256:8042e52dc59f99a8cc3abc306f4f7c19451ff66b6ac4768340213613cf5da2e2
EARLY_RETURN: NEEDS_SCOPE, NEEDS_RULING
SESSION_MODE: delegated

BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "implementation",
  "ROLE": "implementation seat, FIX ROUND 1 on NIGHT-PLAN-PIN-01 (same objective as the landing; cures six refuter findings)",
  "OBJECTIVE": "Cure execution-refuter findings B1, S1, S2, L1, L2, N1 against the landed night-plan-pin change, with one defect-shaped test per cure, and write docs/process_traces/2026-09-03-night-plan-pin/06-sol-fix-round-1-report.md.",
  "AUTHORITY": [
    "AGENTS.md (delegated-session write authority; WRITE_SCOPE exhaustive)",
    "docs/contracts/bridge_protocol.md (bridge-protocol/v1.1)",
    "docs/process_traces/2026-09-03-night-plan-pin/00-landing-brief.md (the original landing brief: design lean, gate-order rule R-3, no new refusal codes, code registries exact)",
    "docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md (your predecessor seat's report + clause map)",
    "Magistrate rulings inline below (this brief)"
  ],
  "WRITE_SCOPE": [
    {"path": "joulewise/night_gate.py", "match": "exact"},
    {"path": "scripts/run_night.py", "match": "exact"},
    {"path": "scripts/install_night_agent.sh", "match": "exact"},
    {"path": "tests/test_night_gate.py", "match": "exact"},
    {"path": "tests/test_run_night.py", "match": "exact"},
    {"path": "tests/test_install_night_agent.py", "match": "exact"},
    {"path": "docs/process/NIGHT_HANDBACK.md", "match": "exact"},
    {"path": "docs/process_traces/2026-09-03-night-plan-pin", "match": "subtree"}
  ],
  "BASE_HEAD": "12ec41d274bd3e7dfdb10800000604bd6ddff8f3",
  "BASELINE_MANIFEST": ".codex-bridge/baselines/planpin-20260903-sol-fix-01.json",
  "BASELINE_DIGEST": "sha256:8042e52dc59f99a8cc3abc306f4f7c19451ff66b6ac4768340213613cf5da2e2",
  "ACCEPTANCE": [
    "B1: in joulewise/night_gate.py the measurement/driver head probe block runs AFTER both plan-age checks; an aged (or future-authored) plan whose probe raises refuses night_plan_stale (night_plan_malformed) and NOT night_probe_error; a test pins this order.",
    "S1+S2: one positive production-path test in tests/test_run_night.py: scratch measurement root whose HEAD == plan measurement_head while REPO_ROOT HEAD differs, real make_probes(), gate passes the stale check; plus a mutation-shaped assertion that the probe output is stripped (a probe returning the head with a trailing newline must still compare equal, i.e. dropping .strip() fails the test).",
    "L1: scripts/install_night_agent.sh refuses a non-absolute measurement_root and a measurement_head that is not exactly 40 lowercase hex, exit 3, message naming the field and reason; tests for both.",
    "L2: a v1 plan (no measurement_root / measurement_head keys) on the INSTALL path exits 3 with a retirement message (v1 retired, re-author under v2) instead of a Python KeyError traceback; test.",
    "N1: docs/process/NIGHT_HANDBACK.md sentences at ~lines 21-22, 63, 67-70 rewritten to the v2 behaviour; the rest of the file byte-identical (git diff shows only those hunks).",
    "Gate order (R-3) preserved: window guard -> age checks -> head probes+stale compare -> census. Refusal-code registries in joulewise/night_gate.py and tests/test_night_gate.py unchanged (no new codes).",
    "Named test modules pass; original two mutation probes and four new ones each show a named failing test; report file exists before the turn ends."
  ],
  "VERIFICATION": [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent",
    "zsh -n scripts/install_night_agent.sh",
    "git diff --stat; git status --porcelain (only WRITE_SCOPE paths dirty)",
    "six mutation probes (see Mutation probes section), each restored and restore verified by sha256"
  ],
  "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "claude-codex-report/v1 (runner-injected implementation genre; see the runner contract appended to this prompt and follow ITS verdict shape exactly)"
}
END_BRIDGE_TASK_V1

# FIX ROUND 1: NIGHT-PLAN-PIN-01 (night plan pins the measurement checkout)

You are the same seat role as the landing (`01-sol-landing-report.md`), on a
fresh thread. Worktree `/Users/edr/code/JouleWise-wt-planpin`, branch
`feat/2026-09-03-night-plan-pin` @ `12ec41d2` (the landing is COMMITTED at
this head; you start from a clean tree). Effort: high (named fix contract).

Hard limits (unchanged from the landing brief):

- Do NOT `git commit`, `git add`, `git stash`, or `git checkout` anything;
  the magistrate commits. Edit files in place only.
- Never touch `~/Library/LaunchAgents`, `~/night-custody`, or
  `/Users/edr/JouleWise-measurement-20260813` (read-only reference at most).
- Never start `claude` or `codex` (bridge depth is one hop). Never start any
  `[QUIET-MAC]` measurement.
- `WRITE_SCOPE` is exhaustive; anything else -> finish authorized work, then
  `NEEDS_SCOPE` naming the path. Python bytecode caches (`__pycache__/`,
  `*.pyc`) are NOT a scope matter: the runner records them separately and
  never as violations, so do not return NEEDS_SCOPE over them. Run every
  python invocation with `PYTHONDONTWRITEBYTECODE=1` anyway.
- Never run `python -m unittest discover`; run named modules only.
- Read `docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md`
  first (your predecessor's report; the clause map rows a..i are what the
  refuter attacked). `05-refuter-execution.md` may be ABSENT in the trace
  directory; if so, the refuter's findings are restated authoritatively
  below and you need nothing else.

## Findings and required cures

### B1 (blocker) — probe order vs age checks

Site: `joulewise/night_gate.py` ~`:604-608` — the block

```python
    try:
        measurement_checkout_head = probes.measurement_head(plan.measurement_root)
        checkout_head = probes.checkout_head()
    except Exception as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
```

and the `rows["C5"].measured.update({...})` right after it run BEFORE the
two age checks at ~`:624-631` (`authored_epoch_s > now` ->
`night_plan_malformed`; `now - authored_epoch_s > PLAN_MAX_AGE_S` ->
`night_plan_stale`). Consequence: an aged or future-authored plan whose
measurement root is missing / not a git repo refuses `night_probe_error`
instead of the age code. The age checks need no probe, so they must come
first.

Cure: move the probe `try` block AND the C5 `measured.update` below both age
checks (age checks may record `authored_epoch_s` in C5 themselves if you want
the row populated on an age refusal — your call, say which in the report).
The R-3 window guard (`night_window_*`) still precedes everything, and the
census still follows the stale compare. Keep
`test_window_refusal_performs_no_command_or_file_or_head_probe`
(`tests/test_night_gate.py:437`) green.

Test (error-shaped order regression, `tests/test_night_gate.py`): fake probe
source whose `measurement_head` (and/or `checkout_head`) RAISES, plan aged
> 36 h -> refusal reason `night_plan_stale` (not `night_probe_error`); and a
sibling assertion or second test with `authored_epoch_s` in the future ->
`night_plan_malformed`. Assert the probe was not invoked (call count 0) if
the fake exposes counts. Name the tests so the registry at
`tests/test_night_gate.py:~779-794` (refusal-code -> test-name registry) stays
exact — do not add codes; if the registry maps code -> ONE test name, keep
the existing names as the registered ones.

### S1 + S2 (should-fix) — clause (c) test blind to root swap and to strip

S1: `tests/test_run_night.py:1125`
`test_moved_real_measurement_checkout_refuses_as_stale` stays green if the
production `measurement_head` probe (`scripts/run_night.py` ~`:276-282`)
ignored its `root` argument and read `REPO_ROOT` instead (the test only pins a
MOVED scratch repo, so any mismatch passes). S2: dropping `.strip()` on the
probe's stdout (`scripts/run_night.py` ~`:282`) makes a matching real plan
refuse stale, and no test notices.

Cure — ONE new positive production-path test in `tests/test_run_night.py`
(next to `:1125`): init a scratch git repo under the test's temp root
(`_init_git_repo` helper already exists there), set the plan's
`measurement_root` to it and `measurement_head` to its HEAD; assert that
`REPO_ROOT`'s HEAD (`git -C REPO_ROOT rev-parse HEAD`) differs from that
scratch HEAD (it necessarily does — different repos — assert it anyway so the
test documents the discriminator); build probes with the REAL
`make_probes().measurement_head` (as the existing test does) and a fake
`checkout_head` returning the plan's `repo_head` or anything; time within
the window and plan fresh; evaluate; assert the refusal is NOT
`night_plan_stale` and NOT `night_plan_malformed` (the gate proceeds past R-6
— use whatever the existing "dev-tree movement is informational" test in
`tests/test_night_gate.py:460` asserts on, e.g. the census probe ran or the
C5 row records `measurement_checkout_head == plan.measurement_head`). Under
the S1 counterfactual (probe reads REPO_ROOT) this refuses stale -> test
fails.

Strip assertion (S2): in the SAME test or a tight sibling, call the
production probe directly through a probe runner whose stdout carries a
trailing `"\n"` (the real `git rev-parse` does), and assert the returned
value `== pinned_head` exactly (no newline) — e.g. assert
`probe(str(measurement)) == pinned_head` and `not probe(...).endswith("\n")`.
Removing `.strip()` fails it. If `make_probes()` takes no runner injection,
use the real runner: real `git` emits the trailing newline, so
`assertEqual(pinned_head, probe(str(measurement)))` already bites; state in
the report which form you used and why it bites.

### L1 (low) — installer accepts a relative root and any head string

Site: `scripts/install_night_agent.sh` ~`:51-60` (install path). Add, before
the git probes: `measurement_root` must be absolute (zsh: `[[ "$measurement_root" == /* ]]`),
else `print "plan measurement_root must be an absolute path: <value>" >&2; exit 3`;
`measurement_head` must match `^[0-9a-f]{40}$` (zsh: `[[ "$plan_measurement_head" =~ '^[0-9a-f]{40}$' ]]`
— confirm the regex form works under `zsh -n` and at runtime in your test),
else `print "plan measurement_head is not 40 lowercase hex: <value>" >&2; exit 3`.
Apply the same hex check to `repo_head` on the install path if it is cheap
(say so). Tests in `tests/test_install_night_agent.py`: install with
`measurement_root: "."` -> exit 3, stderr names `measurement_root`; install
with `measurement_head` = 40 UPPERCASE hex or a 39-char string -> exit 3,
stderr names `measurement_head`. Uninstall path unchanged (checks nothing).

### L2 (low) — v1 plan dies with a KeyError traceback on install

Site: same script, the `python3 -c '... json.load(...)["measurement_root"]'`
one-liners (~`:51-52`). A v1 plan lacking the keys raises KeyError; the shell
then continues or dies noisily. Cure: read the plan once with a small python
snippet (or per-key `.get`) and, if `schema != "joulewise.night_plan.v2"` or
either key is missing, `print` a retirement message to stderr —
`plan schema joulewise.night_plan.v1 is retired; re-author under joulewise.night_plan.v2 (missing measurement_root/measurement_head)` — and `exit 3`. Do this on the INSTALL path.
On the uninstall path the script must keep working for a v1 plan (it reads
only `custody_root`; F9: an uninstall must never be refused) — add an
assertion for that to the existing uninstall test or a new one. Test: write a
v1 plan (schema literal `joulewise.night_plan.v1`, no v2 keys), run install
with the stub launchctl/claude -> exit 3, stderr contains `retired` and
`joulewise.night_plan.v2`, and does NOT contain `Traceback` or `KeyError`.

### N1 (nit, docs) — NIGHT_HANDBACK.md still describes the dev-HEAD gate

`docs/process/NIGHT_HANDBACK.md`: the sentences around lines 21-22
("the installer checks `repo_head` before the uninstall branch"), 63, and
67-70 ("the gate compares the plan's `repo_head` to the CANONICAL checkout
HEAD" / "must not be pulled or moved between the re-arm and the night's
completion") describe the OLD behaviour. Rewrite ONLY those sentences to the
v2 behaviour: the gate compares the plan's `measurement_head` to the HEAD of
the plan's `measurement_root` (the measurement checkout of record,
`/Users/edr/JouleWise-measurement-20260813`); the installer checks BOTH pins
(`repo_head` == driver checkout HEAD, `measurement_head` == measurement
checkout HEAD) on install and NEITHER on `--uninstall`; ordinary daytime
work on the dev checkout no longer invalidates an armed night, only moving
the measurement checkout does. Keep it factual about history (that night WAS
re-armed under the old rule) — do not rewrite the narrative, only the
mechanism sentences. Every other byte of the file stays identical: verify
with `git diff --stat docs/process/NIGHT_HANDBACK.md` and paste the hunks.

## Mutation probes (run each, paste the observed failure, restore, verify restore by sha256)

Original two (must still bite after your edits):

1. `joulewise/night_gate.py`: stale compare
   `if measurement_checkout_head != plan.measurement_head:` ->
   `if checkout_head != plan.repo_head:` -> run `tests.test_night_gate`.
2. `scripts/install_night_agent.sh`: `if (( ! uninstall )); then` ->
   `if (( 1 )); then` -> run `tests.test_install_night_agent`.

New four:

3. Probe order: move the probe block back above the age checks -> run
   `tests.test_night_gate` -> your B1 test FAILS (name it).
4. REPO_ROOT swap: in `scripts/run_night.py` `measurement_head`, replace
   `root` with `str(REPO_ROOT)` in the git command -> run
   `tests.test_run_night` -> your S1 test FAILS.
5. Strip removal: drop `.strip()` from the `measurement_head` probe's return
   -> run `tests.test_run_night` -> your S2 assertion FAILS.
6. Relative root at install: remove the isabs guard -> run
   `tests.test_install_night_agent` -> your L1 test FAILS. (Optionally also
   the hex guard and the L2 schema guard; paste if you run them.)

Restore each edit and prove it: `shasum -a 256 <file>` before the mutation
and after the restore, prefixes equal. Run the full three-module command
once more at the very end and paste its tail.

## Report — write BEFORE ending your turn

`docs/process_traces/2026-09-03-night-plan-pin/06-sol-fix-round-1-report.md`
containing: (1) a finding -> cure -> test table (finding id, production
site `file:line` after your edit, test method `file:line`, counterfactual
that fails it); (2) the clause-map DELTA for the rows you touched (rows a, c,
i from the landing map, plus new rows for B1 order, S1 root, S2 strip, L1
isabs, L1 hex, L2 retirement) under a `## Clause map` heading, same three
cells per row as `01-sol-landing-report.md`; (3) verbatim test tails for the
three-module command (before your edits, after); (4) the mutation table: six
rows, mutation -> command -> observed failing test line(s) -> restore sha
prefix match; (5) the `git diff --stat` and the NIGHT_HANDBACK.md hunks;
(6) any judgment call you made (where the C5 row is populated on an age
refusal; regex form; whether repo_head got the hex check) with the
alternative you rejected; (7) "Magistrate follow-ups" for anything you saw
but could not touch.

FINAL message: the runner-injected `claude-codex-report/v1` implementation
envelope — follow the runner's schema and verdict vocabulary EXACTLY (the
previous seat's envelope was rejected rc=65 for using the review-genre verdict
shape). JSON header under 8192 bytes: all evidence lives in the report file;
the header carries one `verification` entry per command (exact replay cmd,
result, 1-3 line tail), `pathspec` = exactly the files you changed, and
`flags` only for real NEEDS_SCOPE / NEEDS_RULING / residual risk. Do not end
your turn before the report file exists.
