# W1 reliability round 7 — RL-26, local Sol seat `rel-r7`

Base: `ops/2026-11-10-w1-reliability` at `d92dc9206`. Work branch:
`ops/2026-11-10-w1-reliability-r7`. Local commits only; no push.

## Authority and intake

Read RL-26 from local `origin/audit/2026-11-10-fable` at
`9f536d8764ebd4d35e6edf9e23e6f0a3fbc253d6`,
`docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
`docs/align/v4/DEVIATIONS.md` quotes its complete Ruling paragraph verbatim.
The earlier `_NAMED_ARTIFACTS`/receipt-template edit exceeded the round-4
"no registration code" scope; RL-26 ratifies it and requires this deviation
entry before W1 STRICT re-registration. No registration receipt was issued
or changed in this round.

Mission M0: read AGENTS/CLAUDE, the playbook, source map, orchestration,
targeted decision-log clock-policy text, restart/status/workspace sections,
queue and Do-Not-Do-Yet fences, and relevant round-4/round-6 handoffs. There
was no active stop card. The explicit brief selects this bounded AGENT
reliability task over the general queue. The starting tree was clean. No
delegation or consult was used.

The brief overrides coordination writes and the canonical full-suite rule:
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` remain unchanged; no kernel task was registered.

## Changes and acceptance

| Requirement | Implemented behavior and witness |
|---|---|
| D-01 | Deviation row records the scope overrun, ratification and W1 STRICT coverage, followed by the exact RL-26 ruling and its Git source. |
| Arm condition (a) | `clock_frequency_preflight.zero_helper` records the installed sudoers-command path, its SHA-256 and `source: {path, sha256}`. The source digest comes from the measurement source checkout's registration receipt, and the source bytes must match it. Every successful preflight records the pair, including no-op arms. Missing/unreadable binaries needed for zeroing produce `clock.frequency_helper_unreadable`, retain the source digest/read error and before/after probes, and refuse before invoking the helper or installer. Invalid/missing source bindings produce `clock.frequency_helper_source_unbound`. |
| Arm condition (b) | `clock_frequency_pre_t0` holds a separately validated timex probe, read-start/read-finish wall times and the bound plan's t0. It is read after arm checks and the disk gate, immediately before the arm record is written and before the quiet-dwell stamp. It uses the same read-only kernel reader as the preflight. The immutable arm record is durable before installer handoff. Unavailable/unreadable probes or a passed t0 refuse with a named cause; an earlier refusal leaves this unattempted field null. |

The final probe is the session's last pre-t0 kernel frequency read, not a
prepare-time value or a claim that it occurred exactly at t0. The existing
launchd hazard arm runs after t0. No new frequency magnitude/zero-word
threshold was added: a passing nonzero word still needs no zeroing; an
absent unused helper is recorded with a null binary digest/read error and
does not itself refuse. The final word is diagnostic evidence under RL-26.

`tests/test_w1_reliability_r7.py` uses temporary helper/source/receipt bytes,
synthetic timex records, host-command answers and a mocked installer. Its
temporal witness stages prepare word 0, early-install word 1, then changes
the host to word 2 after arm checks. The installer sees word 2 already on
disk. Other witnesses cover missing/unreadable needed binaries, unused
binary absence, source drift, an unreadable last probe, expired t0 and a
read that starts before t0 but finishes after it.

Legacy frequency fixtures now provide temporary installed-helper bytes and
a synthetic source-binding receipt. The series production replay supplies
the same source binding and keeps the real preflight/final reader with
injected timex probes. Battery/cadence-only fixtures explicitly isolate
both OS clock checks. None is native clock-setting evidence.

Files changed:

- `docs/align/v4/DEVIATIONS.md`
- `scripts/align_v4_session.py`
- `tests/test_w1_reliability_r7.py`
- `tests/test_w1_reliability_r3.py`
- `tests/align/test_v4_kit.py`
- `tests/align/test_v4_series.py`
- `tests/align/test_v4_series_e2e.py`
- this report

## Verification

All checks are targeted unittest invocations, serially, on synthetic inputs.
Common environment: `JW_B5_SYNTHETIC_ONLY=1 PYTHONNOUSERSITE=1
GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ALLOW_PROTOCOL=file`.
Test Git remotes, where exercised by the registered generator, are local
temporary bare repositories. No full suite ran.

Commands use `python3.13 -B -m unittest <target>`:

| Target | Result |
|---|---|
| `tests.test_w1_reliability_r7` before implementation | Expected red: 9 tests, 5 assertion failures and 4 missing-field errors. Both requested conditions failed first. |
| `tests.test_w1_reliability_r7` after implementation | Original 9 passed; final 10 passed after adding the read-crossing-t0 edge case. |
| `tests.test_w1_reliability_r3` | 14 passed, including the C helper contract harness with fake syscalls. No real clock adjustment. |
| `tests.test_w1_reliability_r4.FrequencyTests` | 17 passed. |
| `tests.test_w1_reliability_r5.FrequencyTests` | 1 passed. |
| `tests.align.test_v4_executed_closure` | 4 passed. |
| `tests.align.test_v4_dynamic_closure` | 10 passed. |

Ran the registered generator, with the common environment above:

```sh
python3.13 -B scripts/align_v4_dynamic_trace.py --out /private/tmp/jwsol-rel-r7-dynamic-closure.json
```

Exit 0 in approximately 6m17s (377.26 s from the redirected log's creation
and final-write timestamps). All nine scenario suites succeeded, covering
416 targeted cases and 186 executed paths; `not_bound: []`,
`not_strict: []`. The generator does not inventory skips. The generated JSON
was copied over `docs/align/v4/dynamic_closure_trace.json` and verified
byte-identical to both the generated file and its prior committed bytes.
Consequently this regenerated file has no Git diff. SHA-256:
`e74bb7dff18025ff43d3726a174f55cd1329e34ca6670bed15673121005b25ee`.
No runtime code changed after regeneration.

`python3.13 -m compileall -q joulewise tests`, AST parsing of the changed
session script, STRICT-membership checks and `git diff --check` passed.
The four prohibited coordination paths were also compared directly with
`d92dc9206`: byte-unchanged. Total test runtime, including failing-first,
development checks and the generator, was approximately seven minutes,
under the approximately twenty-minute budget.

Current-round changed STRICT-bound paths are
`scripts/align_v4_session.py` and `docs/align/v4/DEVIATIONS.md`.
The source binding in `_NAMED_ARTIFACTS` and receipt template is already
present in the parent branch; this round leaves both files unchanged.
The trace remains STRICT-bound despite its unchanged bytes. The complete
integrated reliability branch, not merely these two paths, still needs
fresh W1 STRICT registration coverage.

Checks caught two evidence defects before implementation: missing installed
helper/source pairing (and permissive unreadable-helper handling), and the
absence of a distinct late pre-t0 probe. The final focused/closure checks
found no remaining failure. No numerical study result was evaluated; no
three-session mechanism-pruning conclusion is drawn from this one run.

The required session-end command
`python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` could not
observe processes: exit 2,
`{"error": "PermissionError: [Errno 1] Operation not permitted: 'ps'"}`.
Rows and count are unavailable; no clean census is claimed. No process was
signalled or cleaned, and this observation limit does not change the code
verification results.

## Local commits

- `083916410` — `fix(align): record RL-26 helper and pre-t0 arm evidence`.
- This report is the subsequent local documentation commit on the same branch.

No push, merge or deployment was performed.

## Boundaries, uncertainty and next exact step

No network, model downloads, real measurement inputs, analysis pipeline,
real restricted/custody directory, privileged host command, installation,
arm, launchd operation or MLX execution was performed. No external data path
cited by repository text was followed. The running blinded analysis job was
not operated. Git-object reads were repository operations under the allowed
shared-store exception. The initial authority command returned the full
research-lead audit, including surrounding Block-5 discussion, before later
reads were narrowed to RL-26. This session does not claim blindness to that
audit text. No custody outcome is reproduced here, and these procedural
changes use no study outcome.

Read the speed toolbox from local `origin/main`. This is reliability work;
no throughput optimization, batching or decision cache was introduced. No
measurement estimand, engine, seed, clock threshold or measured-episode
batch size changed.

Hardware behavior remains **PROVISIONAL**. A pair of digests does not prove
that an installed binary was built from that source; provisioning/build
provenance and the real sudoers path/ownership remain lead checks. Native
clock reads, OFF/zero/read-back and launchd timing have not been established
by these synthetic tests. No MLX code changed; existing native MLX/W1 smoke
gates remain lead-owned outside this sandbox.

Next exact step: the lead reviews/integrates these local commits, includes
the changed STRICT-bound session script and deviation log (and regenerated
closure trace if its bytes change) in W1 STRICT re-registration, and checks
the actual installed helper digest/source pair and final pre-t0 probe on a
clean native session before arming. Previously owed helper provisioning,
meter, restoration, delivery/watchdog and integrated W1 smoke gates remain.
No new research ruling is requested.
