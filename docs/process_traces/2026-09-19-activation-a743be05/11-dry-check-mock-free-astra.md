```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Dry-check now executes the real installer and supervisor and consumes their artifacts; historical dispatch fails.","workspace":{"base_requested":"a997d30178fb2cb3239f83d779403660859c1146","base_mode":"descendant","head_start":"0ce9c338517b5dbc1d565e49e1cf2928ec4ce308","head_end":"0ce9c338517b5dbc1d565e49e1cf2928ec4ce308","upstream_end":"0959e613c96d7f33b2f0c2186bf90ca40afd6ef7","branch":null},"pathspec":["docs/process_traces/2026-09-19-activation-a743be05/02-arm-scripts-qpe01-pilot-n1-20260919/dry-check.py","docs/process_traces/2026-09-19-activation-a743be05/02-arm-scripts-qpe01-pilot-n1-20260919/README-sequence.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"smoke","cmd":"TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B docs/process_traces/2026-09-19-activation-a743be05/02-arm-scripts-qpe01-pilot-n1-20260919/dry-check.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DRY CHECK COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"DRY CHECK COMPLETE$"}},{"id":"V2","kind":"test","cmd":"TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/rehearsal-dispatch-regression.py docs/process_traces/2026-09-19-activation-a743be05/02-arm-scripts-qpe01-pilot-n1-20260919/dry-check.py","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["CalledProcessError: Command '['/bin/zsh', '/private/tmp/qpe01-arm-fixture-y6qh71a1/custody/chain.zsh']' returned non-zero exit status 2."]},"expected":{"exit_code":1,"tail_regex":"CalledProcessError.*exit status 2"}},{"id":"V3","kind":"test","cmd":"TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V4","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"Actual starting HEAD adds the copied arm-script baseline commit atop the requested head; HEAD remained unchanged.","needs":""}]}
```

## Change

Replaced manufactured plists and receipt bindings with real installer renders and a real verify-only supervisor receipt. Both renders use fresh directories; night/dead-man bytes must match. Corruption refusals now mutate real artifacts.

Step 5 required no changes. README documents execution, fixture HEAD substitution, remaining stubs, and Ed’s rule. Only the two listed files changed; no commits.

## Verification notes

Full dry-check output, exit **0**:

```text
PASS zsh -n arm-env.zsh
PASS zsh -n step0-precheck.zsh
PASS zsh -n step1-clone.zsh
PASS zsh -n step2-author.zsh
PASS zsh -n step3-notice.zsh
PASS zsh -n step4-publish-install.zsh
PASS zsh -n step5-verify-and-exit.zsh
PASS Python syntax: 8 shell heredocs and 2 helper scripts
PASS arm-env H is an ancestor of local origin/main (no fetch)
PASS fixture checkout HEAD equals fixture H (worktree HEAD)
PASS filled environment: local date, minute alignment, all seven boundaries
PASS unfilled environment refuses with exit 3
PASS actual authoring heredoc, generator, manifest, source-at-H and registration checks
PASS generated wrapper zsh -n (execution deferred to verify-only probe)
PASS second render refuses existing chain
PASS publication-safe guard accepts the staged wrapper (binds the published plan path)
PASS wrapper byte drift refuses
{"chain_sha256": "752ec536c9fdd4598f34568c336609e520b67d5436bb33de9abb662b831f590b", "input_digests": {"/private/tmp/qpe01-arm-fixture-succ79k_/custody/evidence_manifest.json": "sha256:9ef39ae9b10a4929314a3466612a48fab1cd908b5746866ef3584aad51903f30", "/private/tmp/qpe01-arm-fixture-succ79k_/stage/night_plan.json": "sha256:ba593e42d6394979adb49b3fdcfddb55fae015d17c6e5959ef81e81ae5f34dec"}, "payload_kind": "quiet_predicate_evidence"}
PASS real installer render-only on STAGED plan: evidence payload JSON and three plists
PASS actual notice heredocs: evidence body, byte binding, unaccepted template
PASS publication heredoc refuses unaccepted notice, owner NO and changed saved bytes
{"chain_sha256": "752ec536c9fdd4598f34568c336609e520b67d5436bb33de9abb662b831f590b", "input_digests": {"/private/tmp/qpe01-arm-fixture-succ79k_/custody/evidence_manifest.json": "sha256:9ef39ae9b10a4929314a3466612a48fab1cd908b5746866ef3584aad51903f30", "/private/tmp/qpe01-arm-fixture-succ79k_/custody/night_plan.json": "sha256:ba593e42d6394979adb49b3fdcfddb55fae015d17c6e5959ef81e81ae5f34dec"}, "payload_kind": "quiet_predicate_evidence"}
PASS real installer render-only on PUBLISHED plan: three plists; night/dead-man byte-identical
PASS fixture publication preserves bytes; real probe bindings accept the published plan and refuse the staged path
PASS real run_night.py preflight and schedule on published fixture
PASS real probe_night supervisor, verify-only chain, process identity and validate_probe_receipt
PASS real receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness
PASS actual step5 assertions on installer-produced plists; wrong schedule/argv/root/RunAtLoad refuse
DRY CHECK COMPLETE
```

The negative control used a disposable checkout at `0959e613`. It failed at the **first installer render**, before publication:

```text
CalledProcessError: Command '['/bin/zsh', '/private/tmp/qpe01-arm-fixture-y6qh71a1/custody/chain.zsh']' returned non-zero exit status 2.
```

The installer itself returned **1**, propagating that chain failure. [Full regression output](/tmp/rehearsal-dispatch-regression.log) and [replay harness](/tmp/rehearsal-dispatch-regression.py) remain available.

An initial installer-only mutation was correctly rejected earlier by manifest integrity checks; the historical checkout avoided that interference. The full repository suite was omitted for this tooling-only change; the composed arm-sequence test passed.

## Residual risk

Fixture census, courier discovery, and loaded-label responses remain explicitly stubbed. No live launchctl, powermetrics, collection, email, or network operations occurred. Next: lead reviews the two-file diff and performs final verification; fixture success does not certify the separate live arm pin.