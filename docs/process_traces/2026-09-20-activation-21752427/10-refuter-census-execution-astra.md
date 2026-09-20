```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Narrow cure holds; two should-fix findings.","workspace":{"base_requested":"7472a7c7","base_mode":"exact","head_start":"7472a7c757caeaf9b4a6d6fafe3d1b59e9809319","head_end":"7472a7c757caeaf9b4a6d6fafe3d1b59e9809319","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix"},{"id":"F2","severity":"should_fix"}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git diff --exit-code","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Findings

No blocker found in the narrow peer-pgrep cure.

**F1 — should_fix: the regressions permit unsafe output filtering.** Executed in `/tmp`: keeping the new constant, but removing stdout lines containing `/usr/bin/pgrep` and converting an emptied successful result to exit 1, survives all three new deterministic regressions, the argv pin, and 16 focused existing/new census tests.

Concrete counterexample: `42 /usr/bin/claude -p inspect /usr/bin/pgrep`. The unmodified implementation preserves this line and returns `night_refused_agent_present`; the mutant returns empty stdout, exit 1, and no refusal. This is a coverage defect; **the committed implementation does not filter it**. Add a foreign-agent case containing `/usr/bin/pgrep`, asserting refusal and exact evidence preservation.

**F2 — should_fix: an independent watchdog still falsely classifies the authorized driver as an agent.** Executed with modeled pgrep matching through the real `production_census` and `decide`: driver argv containing `--courier-bin /Users/edr/.local/share/claude/versions/2.1.260` produces `HOLD_CENSUS`, `empty=False`, and no signals. The harvest record independently documents this on driver PID 79018. This is pre-existing and distinct from the repaired peer-pgrep race; it can produce false holds/notices, although this path does not kill the chain. Handle courier configuration through census-safe argv in a separate bounded fix; broad pgrep-output filtering would introduce F1’s failure.

**Mutation results.** G = `test_census_does_not_match_peer_argv`; D = `test_peer_census_reaches_and_completes_chain`; A = `test_foreign_agent_alongside_peer_still_aborts_chain`; P = the production argv pin.

| Mutant | Killed by / result |
|---|---|
| Old `codex\|claude\|t3` | G, D, A, P |
| Partial `[c]odex\|claude\|[t]3` | G, D, A, P |
| Drop `-l`, retaining `-f` | P; G/D/A survive |
| New constant + pgrep-line post-filter | **SURVIVED** G/D/A/P and 16 focused census tests |

For old/partial patterns, G refuses the peer; D returns admission refusal exit 3 instead of completion exit 0; A returns exit 3 before chain launch instead of the expected running-chain abort exit 4. Baseline: four deterministic checks pass. All three native tests skip for every variant because process-list access is unavailable.

Replay: `/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/census-refute-mutations.py` and `/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/census-refute-focused.py`. Mutations were made only in the archived `/tmp/census-refute-7472a7c7` copy and restored afterward.

**1. Regex equivalence — proved and exercised.** A singleton character class `[c]` denotes exactly `c`, and `[t]` exactly `t`; concatenation and alternation therefore give identical languages for **all** input strings, including literal pattern text. Python `re`: 100,000 randomized strings plus 19 edge cases passed equivalence. Darwin `/usr/bin/grep -Eq`, `LC_ALL=C`: all 19 cases agreed.

Both patterns match `att3mpt`, `/opt/t3/`, `gpt3`, lowercase `claude.app`, and `猫codex🚀`. Neither matches `Claude.app`, `CODEX`, `GPT3`, Cyrillic-confusable `cоdex`, fullwidth `ｃｏｄｅｘ`, or `t³`. The cure changes the emitted pgrep argv, not the matching population for unchanged argv.

`grep -E '[c]odex'` is invisible to **both** patterns; it did not become invisible. That command alone is a grep process, not evidence of a running agent. An actual agent whose argv contains ordinary `claude`/`codex` remains visible. Deliberately disguised argv remains an existing limitation of name matching.

**2. Producers — imports and intercepted execution verified.** Driver `agent_census`, `_binding_census`, watchdog `production_census`, quiet-admission `sample_interval`, and t0 `_derive_process_census` all requested:

`('/usr/bin/pgrep', '-lf', '[c]odex|[c]laude|[t]3')`

`ARM_DISCOVERY_ARGV` intentionally requests `-f` without `-l`, using the identical shared pattern. Tracing `_authenticate_pack_launch_go` immediately after its import confirmed the same current constant. These checks intercepted subprocess/probe seams; no sampling ran.

`t0_rehearsal._AGENT_TOKEN_RE` is a separate case-insensitive, slash/whitespace-delimited classifier over recorded process argv. G8 uses it to bind the exiting agent PID before launch and reject agents in capture-time records. It does not generate pgrep argv and needs no bracket change.

Repository-wide exceptions, read only: `quiet_mac_prep.sh:38` retains advisory `codex exec|codex mcp|claude`; `prewindow_check.sh:149` retains the broader `codex|claude|t3|mcp-server|run_campaign|window-chain` ps/grep check. Neither is one of the shared production pgrep paths. Thus “all repository checks use one constant” would overstate the change.

Import replay: `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -c 'from pathlib import Path; exec(Path("/tmp/census-refute-inspect.py").read_text())'`.

**3. Differential test — alignment is justified, with a limited claim.** `raw` comes from pinned `git show a90ab4e8:joulewise/night_gate.py`, not the current file. Removing only the alignment in memory produced 22 failing subtests. The baseline requests the old key absent from current `FakeProbeSource.results`, causing `KeyError` → `night_probe_error`; the first comparison is baseline REFUSED versus current GO. Even with both fixture keys supplied, C3 probe citations and refusal evidence argv would differ intentionally.

Alignment correctly isolates evaluator semantics from the declared argv change. It does **not** demonstrate unchanged serialized receipt bytes or historical authentication compatibility. The aligned differential test passed.

**4. Retained receipts — executed validation passed 4/4.** All four named roots contain v2 `DIAGNOSTIC_NO_PACK` plans, old-pattern census journals, and `night/receipt.json` accepted by current `validate_receipt` with `[]` defects. None contains `night/go_receipt.json`. The pilot journal contains the stated PID 79146 peer-pgrep hit.

`_check_census` performs a fresh probe; it is not a retained-receipt validator. Replaying an old `ProbeResult.argv` as the response to a new request would fail `_run`’s request/result equality, but simply validating a retained night receipt does not take that path.

The exact comparison at `arm_readiness.py:10149` belongs to **TRANSACTION_PACK launch-GO authentication**. Executing that condition with otherwise valid synthetic fields rejects old argv and accepts new argv. Therefore a successor authenticator would reject an old-pattern pack GO if it reached this check; this particular incompatibility does not affect the four retained diagnostic receipts.

**5. Static guard — still correct and exercised.** `_census_clean` still checks `("codex", "claude", "t3")`; bracketed regex syntax does not change those substring matches. It lowercases inputs, so it is conservatively stricter than case-sensitive pgrep. The named derivation guard test passed. `gen_evidence_night.py:16,37` imports and applies the same guard to plan/path literals; its unsafe-`claude` generator regression also passed.

Read only: Darwin’s local pgrep manual explicitly excludes the caller and its ancestors by default. Driver probes are children; bind workers and sampler workers are descendants. `_BindLauncher` uses a thread and `Popen(start_new_session=True)`; creating a session does not change ancestry. Thus the live driver’s courier argument is excluded from its own descendant censuses, but remains visible to an independent watchdog.

**6. Handbook — byte comparison passed.** Both versions have one `ARM-RETRY-POLICY` region bounded by BEGIN/END markers, rather than two separate code-fenced blocks. Its entire 9,310 bytes are identical. All ten `## Executed —` blocks are byte-identical. Changes are confined to the current pattern sentence and rollout note.

**7. Remaining same-signature cases.** New census processes exclude one another only when their full argv has no other matching substring. Mixed rollout still fails: a new probe matches an old probe’s unbracketed argv. Matching helper paths, another driver’s courier argument, and sibling shells mentioning `~/.claude/shell-snapshots/...` also remain visible.

An active agent and its surviving helper tree are legitimately forbidden during acquisition, regardless of JouleWise ownership. An otherwise authorized driver matched solely through its dormant courier configuration is the F2 false positive. These distinctions preclude a general claim that JouleWise-owned processes can no longer match each other.

## Residual risk

Native pgrep returned exit 3 with `Cannot get process list`; native concurrency, stopped-peer, marker visibility, and ancestry behavior could not be independently exercised here. The lead’s reported 3/3 bench result in 47.9 seconds remains lead-supplied evidence.

An exploratory 157-test mutant run had 146 passes and 11 errors caused by missing Git metadata in the archive copy; those errors are not mutation kills. The subsequent focused 16-test runs passed for both baseline and survivor. No full-suite claim is made.

No repository files changed; final HEAD and clean status were verified. Next step: add F1’s evidence-preservation regression and separately disposition F2 before claiming broader self-match elimination.
