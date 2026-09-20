```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"[read/executed] Ship A.","workspace":{"base_requested":"f2427b24","base_mode":"exact","head_start":"f2427b24","head_end":"f2427b24","upstream_end":"e1e7d6a7","branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"should_fix"}]},"verification":[{"id":"V2","kind":"inspection","cmd":"git diff --stat","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"V1","kind":"environment","level":"nonblocking","text":"[executed] pgrep exits 3: Cannot get process list.","needs":"Lead native bench replay."}]}
```

## Findings

**F1 — blocker: overlapping censuses can abort a clean night.**

[read/executed] Confirmed mechanism. Darwin’s `/usr/share/man/man1/pgrep.1` specifies full-argument matching with `-f`, excluding the calling process and its ancestors—not sibling probes. The retained journal contains 21 empty censuses followed by exactly `79146 /usr/bin/pgrep -lf codex|claude|t3`. This proves one probe matched another; it does **not** prove both probes returned mutual hits.

[read] Two corrections to the supplied call graph materially increase the exposure:

- Worker 79142 executes `run_night._bind_worker_result` → `_binding_census` → `agent_census`, not `quiet_admission.sample_interval`.
- `smoke_observation_round` schedules a census immediately and every **30 seconds**, within repeated sampling rounds throughout each 600-second envelope. The sampler’s closing census and `quiet_predicate_campaign.record_covariates` add further probes. This is not one chain census per 600 seconds.

[read] The watchdog’s `production_census` also calls `agent_census(make_probes())`; it can collide with driver or chain probes. The separate T-0 author literal can collide whenever executions overlap; that overlap was not established for this night. The courier is an actual Claude process: overlap with acquisition should remain forbidden. Normal reporting follows proven cleanup, and `dead_man` checks chain absence before its census/courier path.

[read; calculation] For scan durations \(d_1,d_2\), the possible overlap interval is approximately their sum. Assuming independent uniform phase against a 30-second driver cadence, overlap opportunity is approximately `(d1+d2)/30`. Hypothetical 1–10 ms scans give 0.0067–0.067% per competing invocation. These are illustrative bounds, not measured failure probabilities; recurring phases need not be independent. During settle, collector and recorder have not started, eliminating those competitors—not the watchdog.

[read; recommendation] Ranked cures:

| Rank | Option | Judgment |
|---|---|---|
| 1 | **A: bracketed pattern, shared constant** | Ship. Same regex language for agent argv; rewritten probe argv no longer contains a matching substring. No evidence filtering or new synchronization. |
| 2 | B: post-filter | Defensible with authenticated process identity and retained raw output, but adds exclusion policy, parsing and exit-status normalization unnecessarily. |
| 3 | D: interprocess lock | Requires every producer/checkout to cooperate; adds lock ownership, deadlines and failure paths. Missed callers preserve the defect. |
| 4 | E: structured executable/argv census | Potential longer-term improvement, but broader implementation and population-policy changes than this repair needs. |
| 5 | C: exclusion flags | Darwin documents no selective “exclude other pgrep” option. `-v` inverts matching; PID/group restrictions would change the population. |

[executed] Darwin `grep -E` confirms both patterns match `codex`, `claude`, `t3`, and static paths containing those substrings. Both match an **old** census argv; neither matches the bracketed argv. Therefore all concurrently active producers must use the fix, including the watchdog’s checkout. A patched measurement clone alone is insufficient.

[read; recommendation] Centralize the T-0 author on `AGENT_CENSUS_ARGV`. The driver, watchdog, quiet sampler and arm discovery already derive from it. Preserve `_check_census` consistency checks, error refusal, ancestor handling and static substring guards. The uninstall census at `night_agent_install.py:983` uses a label/plan-specific pattern, not this agent pattern; exclude it from this repair.

**[read/executed] Registration and receipt consequences**

[read/executed] `quiet_predicate_campaign.MANIFEST_PATHS` hashes both `quiet_admission.py` **and `night_gate.py`**. Consequently, even the minimal constant change requires fresh artifacts at the new committed measurement HEAD: manifest, generated wrapper, wrapper digest, plan and probe receipt. A dirty file fails `tracked_bytes`; an old manifest fails comparison against the new HEAD. Never rewrite retained custody.

[read/executed] The frozen registration binds the chain-source digest, not the sampler/module digests or census argv. Its current registration and chain digests both verify. Leaving `scripts/night_chains/quiet_predicate_evidence.zsh` and `pilot_protocol_v1.json` unchanged requires **no registration hash change or re-ruling** for this cure. Editing `quiet_admission.py` would change the manifest unnecessarily; its import already picks up the fix.

[read/executed] All four named retained roots have v2 `DIAGNOSTIC_NO_PACK` plans/receipts and no `night/go_receipt.json`. `arm_readiness.py:10149` belongs to `_authenticate_pack_launch_go`, which requires `TRANSACTION_PACK`; it does not invalidate these roots. No compatibility clause is needed for them. Keep historical argv intact.

[read; recommendation] Do not add unconditional dual-argv acceptance. Historical **transaction-pack** replay does share that strict comparator; if such receipts require replay under new code, handle compatibility through authenticated producer/version lineage as a separate bounded change. That population was not established here.

**F2 — should_fix: add a mutation-sensitive regression and verify the deployed producer set.**

[executed] Offline counterfactual execution through production `agent_census` and `_binding_census` produced:

| Input | Baseline | In-memory candidate |
|---|---|---|
| Another probe carrying the current census argv | Refused | Clean |
| Each agent name in a command line | Refused | Refused |
| Malformed/failed binding probe | Refused | Refused |

[executed] This used Darwin’s regex engine with injected process-list input, not live hardware evidence. Eight existing census tests also passed. Replay:

`/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/census_regression_review.py`

[read; proposed tests] Add these counterfactuals:

1. **`test_census_does_not_match_peer_argv`**: supply a peer command constructed from the production constant; exercise `agent_census` and `_binding_census`. Old constant must fail the zero-peer-hit assertion; bracketed constant passes. This is the deterministic unit regression.
2. **`test_native_concurrent_census_has_no_peer_hits`**: two processes, 1,000 synchronized invocations each; record actual peer PIDs. Require zero peer hits using the production argv and at least one old-pattern control hit. Scheduler-dependent old-control failure means inconclusive reproduction, never a passing cure.
3. **`test_native_stopped_peer_and_agent_controls`**: pause an owned, successfully exec’d `pgrep`, acknowledge its stopped state, then census it. Resume/reap in `finally`. This widens overlap deterministically. Separate owned marker processes carrying each agent name must remain visible. In an active agent session, assert peer-PID absence—not globally empty stdout.
4. **Driver regression** in `test_run_night.py`: the peer-only counterfactual reaches `_run_chain_once` without agent abort after the cure; adding a foreign-agent command still aborts. Update literal pins and receipt fixtures.

[read; proposed WRITE_SCOPE / diff plan] Exact implementation-seat allowlist; each row describes the bounded change:

| File | Change |
|---|---|
| `joulewise/night_gate.py` | Bracketed shared argv; explain peer exclusion. |
| `joulewise/arm_readiness_evidence_t0.py` | Consume shared argv instead of duplicate literal. |
| `scripts/gen_derivation_night.py` | Correct argv comment; retain substring guard. |
| `tests/test_night_gate.py` | Update pins; deterministic peer regression and agent controls. |
| `tests/test_run_night.py` | Update pins; driver abort/preservation regression. |
| `tests/test_arm_census.py` | Update derived discovery/receipt expectations. |
| `tests/test_quiet_admission.py` | Update expected shared census invocation. |
| `tests/test_arm_readiness_evidence_t0.py` | Update author expectations and shared-argv coverage. |
| `tests/test_arm_readiness_schemas.py` | Update newly authored GO fixture argv. |
| `tests/test_arm_readiness_integration.py` | Update census probe selector. |
| `tests/test_gen_derivation_night.py` | Correct explanatory docstring; preserve guard test. |
| `tests/test_agent_census_concurrency.py` | New native peer and positive-control tests. |
| `docs/process/NIGHT_HANDBACK.md` | Current pattern, coordinated rollout and fresh-artifact instructions. |

[read; recommendation] No writes to `arm_readiness.py`, registration, chain template, retained receipts or historical reports. The handbook’s September 13 literal is historical evidence: preserve it. The inspected receipt contract does not quote the literal and needs no mechanical replacement.

**[read/executed] Additional night-record observations**

- Raw power evidence contains **three frames**, all timestamped `2026-09-20 07:50:03`. `no_native_second_rollover` is consistent with the aborted capture. `reduce_interior` initializes `native_samples=0` and returns early for an unresolved anchor; that field does not establish zero raw samples. No second clock defect demonstrated.
- `envelopes_attempted: 0` counts the list appended after collector completion, despite envelope 1 having started. This is misleading bookkeeping, not evidence that collection never launched.
- Watchdog records at epoch `1789890224.744066` and `1789890525.978812` matched driver 79018 because its `--courier-bin` argument contains `/claude/versions/…`. A will not remove that existing static-string match. It explains `HOLD_CENSUS`, separately from the fatal peer-pgrep hit.

## Residual risk

[executed] Native reproduction was unavailable: 2,000 calls per pattern all returned process-list errors. Direct replay, `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'`, exits 3 with `Cannot get process list`. Those runs provide neither collision counts nor valid runtime measurements.

[executed] Repository remained clean at the requested detached HEAD. No full suite, network, launchctl or quiet-window collection ran.

[read; recommendation] Next: implement the bounded change, run focused tests plus the canonical suite, then have the lead execute native peer controls and the real installer/probe rehearsal with fresh artifacts and every active census producer updated.