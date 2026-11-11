# w1-p3 qualification

## Round 2 — stopped on inventory and reachability conflicts

Date: 2026-11-11. Branch: `ops/2026-11-11-w1-p3-qualification`.
Starting HEAD and requested remote base both:
`fe8d8ef5cd757ef3fe58474679e8c3c2e1d65e8d`. Starting worktree clean.
Round 1's report is
[`interp-energy-desk/w1-p3-qualification-sol-report.md`](interp-energy-desk/w1-p3-qualification-sol-report.md).

**Disposition: NEEDS_RULING.** No test exception was installed. The brief's
explicit stop condition applies: the dynamic inventory contains unrelated
changes. Independently, the code-derived qualification driver route reaches
the network-time getter, so the required separation assertion cannot honestly
pass on this tree. Production code, configuration, fixtures, sealed module,
and lead-owned coordination state remain unchanged.

### Baseline and exact census

Baseline command (one module, Python 3.13, installed host guard):

```text
python3.13 -B -m unittest tests.test_v5_block4_x12b
```

Baseline result (exit 1):

```text
Ran 11 tests in 201.861s
FAILED (failures=2)
```

The failures are
`RegisteredRosterTests.test_ast_literal_argv_census_has_no_missing_registration`
(first assertion: `scripts.run_night:4479`, getter) and
`RegisteredRosterTests.test_governed_calls_and_dynamic_builders_have_reviewed_inventory`.
Captured output: `/private/tmp/w1-p3-round2-red.log` (local scratch).
The log's network-time/anchor messages are from the existing synthetic
positive-control fixture, not real host observations. No second module or
full suite was started. Total module test time was approximately 3.4 minutes.

After the baseline finished, invoked only the original literal-census method
with `assertIsNotNone` replaced **in memory** by a failure collector. The
registration calls, argv evaluator, source scan, and checked-in tests were
unchanged. This prevents the first missing row from hiding later assertions:

```text
scripts.run_night:4479: ('/usr/bin/sudo', '-n', '/usr/sbin/systemsetup', '-getusingnetworktime')
scripts.run_night:1657: ('git', '/fixture', '-c', 'user.name=JouleWise courier', '-c', 'user.email=joulewise-courier@example.invalid')
scripts.run_night:1656: ('git', 'init', '--bare', '-q', '/fixture')
Total: 3
```

`/fixture` is the existing evaluator's representative dynamic argument, not
the literal production Git prefix. The exact source expressions and sites
are recorded below. No other missing registration appeared.

### Introducing commits

Read-only `git log -S` searches restricted to `scripts/run_night.py` establish:

| Site at starting HEAD | Source expression | Introduction |
| --- | --- | --- |
| `scripts/run_night.py:1656`, `_publish_terminal_result` | `["git", "init", "--bare", "-q", str(repository)]` | `c80d4d638` (`-S '"init", "--bare"'`) |
| `scripts/run_night.py:1657`, `_publish_terminal_result` | `["git", "--git-dir=" + str(repository), "-c", "user.name=JouleWise courier", "-c", "user.email=joulewise-courier@example.invalid"]` | `c80d4d638` (`-S 'user.name=JouleWise courier'`) |
| `scripts/run_night.py:4479`, `NETWORK_TIME_QUERY_ARGV` | `('/usr/bin/sudo', '-n', '/usr/sbin/systemsetup', '-getusingnetworktime')` | `19a862dc8` (`-S 'getusingnetworktime'`); `c6d25d963` subsequently added `_leave_network_time` and its getter use (`-S 'def _leave_network_time('`) |

The three named commits do **not** map one-to-one to the three argv literals:
both Git expressions came from `c80d4d638`; the getter literal predates its
additional leave-OFF consumer in `c6d25d963`.

### Dynamic inventory stop condition

Replayed the existing `governed_callsite_inventory` AST algorithm against the
same four source modules and compared row multisets with the checked-in
`tests/fixtures/v5_qualification/process_argv_inventory.json`. No differences
in the author, capture, or night-gate modules. Driver differences:

```text
ADDED
('_publish_terminal_result', 'observed_run', 'args')
('run', 'observed_run', 'args')
('_run_night', 'argv assignment', "['/bin/zsh', '-c', 'sleep 2; echo REHEARSAL']")
('_run_night', 'argv assignment', "['/bin/zsh', str(chain_path)]")

REMOVED
('run_night', 'argv assignment', "['/bin/zsh', '-c', 'sleep 2; echo REHEARSAL']")
('run_night', 'argv assignment', "['/bin/zsh', str(chain_path)]")
```

The two `args` rows describe the new courier's nested forwarding helper (the
existing walker also inventories its body under the outer function). The
two assignment moves are a separate wrapper refactor, **not** the three
requested calls. `git log -S 'def _run_night(' -- scripts/run_night.py`
identifies `99a90e9c6` as the wrapper introduction. Per condition (a), neither
the fixture nor the general census/registration logic was changed to absorb
this unrelated drift.

### Reachability method and conflict

Used the inventory's existing source mechanism (`ast.parse` on repository
Python source), without executing the driver or reading a night plan:

1. Read `driver_argv` from the AST of
   `scripts/write_v5_qualification_plan.py:705`; its command is `run` for
   s1/s2. Follow that command's comparison/return in the driver's `_main`
   dispatcher, deriving `run_night` as the entry point.
2. Build same-module function-call edges from `ast.Call` nodes, including
   calls in callbacks/lambdas. Derive getter consumers by references to
   `NETWORK_TIME_QUERY_ARGV`, rather than listing consumer names by hand.
3. Breadth-first traversal yields both paths below. Check the relevant
   branch conditions in the source: the qualification command does not set
   `dry_arm`; `run_night` installs `_HOST_STATE_CLOSE` and invokes it in
   `finally`. Host close calls the common power-mode cleanup. With a usable
   lock and no deferred chain/foreign owner, cleanup selects either restore
   or leave based on the OFF obligation; **both** branches query the getter.
   There is no qualification-purpose exclusion at this cleanup boundary.

```text
writer driver_argv -> dispatcher 'run' -> run_night:4755
  -> _close_night_host:4617 -> _close_ac_powermode:4543
     -> _leave_network_time:4482 -> NETWORK_TIME_QUERY_ARGV:4479
     -> _restore_network_time:4501 -> NETWORK_TIME_QUERY_ARGV:4479
```

Also reproduced the path with a synthetic cleanup diagnostic: derive the
`run` command from the writer AST; invoke the real `driver._main` dispatcher;
replace only the `_run_night` admission/measurement body with a synthetic
stage containing a fixture plan and probe; use a fake acquired host lock,
fake power restoration, an absent marker under `/private/tmp`, and a false
OFF-obligation result. The real `run_night`, `_close_night_host`,
`_close_ac_powermode`, and `_leave_network_time` then execute. The fixture
probe records argv without launching a process. All filesystem effects are
in a temporary synthetic root; no real plan or custody is opened.

```text
Qualification command derived from writer: ['run']
Real dispatcher/wrapper/common cleanup result: 0
Synthetic probe calls: [('/usr/bin/sudo', '-n', '/usr/sbin/systemsetup', '-getusingnetworktime')]
Separation predicate FAILS on unchanged production cleanup: qualification cleanup reaches NETWORK_TIME_QUERY_ARGV
```

This verifies the cleanup reachability conflict, not a complete qualification
execution or hardware validation. It does not claim every attempt passes the
cleanup guards. A plain name-only graph could overapproximate other guarded
branches; the real cleanup reproduction is why this finding cannot be
dismissed as just such an overapproximation. The diagnostic exits 0 after
checking that the separation assertion raises; that is **not** a green result
for the requested separation predicate.

**Green and mutant:** not run. No production/test change was made after the
stop condition. There is no passing separation predicate to mutate: the
unchanged source already reaches the getter. Do not report an expected-failure
wrapper or a narrower choice of roots as satisfying condition (b).

### PARKED FOR THE RESEARCH LEAD

**register these calls in the sealed module at the next registration, or never**

- Bare Git init at `scripts/run_night.py:1656`, exact expression above.
- Terminal-delivery Git prefix at `scripts/run_night.py:1657`, exact expression
  above. These two belong to the newer terminal publisher. Its normal
  `_durable_record` dispatch is guarded by `plan_id.startswith("align-")`.
  That supports their intended separation from the historical qualification
  publisher, but this stopped run does not claim a complete proof across all
  callers/plan identities.
- Network-time getter at `scripts/run_night.py:4479`, exact tuple above.
  **It cannot currently be described as outside qualification:** the shared
  terminal cleanup route reaches it. The requested three-call classification
  needs a lead ruling before test-side exceptions can be added.

### Ruling needed and handoff

Question: how should round 2 proceed given the unrelated inventory drift and
the getter's common qualification cleanup route?

Options considered:

1. Grant a separate test-fixture refresh for the wrapper refactor, and revise
   the getter requirement to reflect its actual terminal-cleanup reachability
   (or authorize an appropriate prospective production change separately).
2. Define a narrower qualification observation boundary, with an authoritative
   code/contract basis excluding cleanup, and revise the acceptance criterion
   accordingly. Merely choosing narrower graph roots would not prove the
   current criterion.
3. Keep the brief unchanged; leave this registration repair blocked.

Recommendation: option 1. Preserve the sealed module and require a new brief
before changing the asserted qualification boundary. Blocked work: exception
constant, stale-entry guards, passing reachability assertion, mutation proof,
inventory repair, and after-change green run.

Only this report is changed. No network, real measurement/custody reads,
analysis pipeline, model downloads, coordination-state writes, or push.
`git diff --check` passes. The forbidden production/configuration/coordination
paths have no diff against the starting base. The sealed module's SHA-256
remains `833b19ad013ed117ff2f0ab5834ce558a7b35227d0e9ba0332f9a07233b21ef1`.
No code changed, so compilation and native MLX checks are not applicable.
