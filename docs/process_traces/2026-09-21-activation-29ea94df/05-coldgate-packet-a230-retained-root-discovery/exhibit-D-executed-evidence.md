# Exhibit D — executed evidence, 2026-09-21 21:58–22:05 PDT, activation 29ea94df (every block is verbatim command output)

## D1 first live `check` on candidate `qpe01-pilot-n1-20260921-2238-20260921-2238-1790055480-7e35d16ae07489364375d28bd41057d9aa4cfa48` (H 7e35d16a): stderr and rc
```
REFUSED: pre-arm checks failed: retained_roots, census; see /Users/edr/night-plan-staging/qpe01-pilot-n1-20260921-2238-20260921-2238-1790055480-7e35d16ae07489364375d28bd41057d9aa4cfa48/lifecycle/check.json
rc=2
```

## D2 `lifecycle/check.json`: per-check verdicts and the `retained_roots` inventory (python extraction; census PID lists omitted, verdict shown)
```
armable: False  launchctl_bin: launchctl  fake_launchctl: False
canonical -> pass
census -> fail
courier -> pass
night_agents -> pass
retained_roots -> fail
retry -> pass
sealed -> pass
supervisor -> pass
{
 "inventory": [
  {
   "classification": "UNKNOWN",
   "evidence": [],
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night_plan.json"
  },
  {
   "classification": "retained",
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night/result.json"
   ],
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json"
  },
  {
   "classification": "retained",
   "evidence": [
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/courier.sent",
    "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night/result.json"
   ],
   "plan": "/Users/edr/night-custody/d079-epoch-25g83-derivation-n2-20260919/night_plan.json"
  },
  {
   "classification": "retained",
   "evidence": [
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/courier.sent",
    "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night/result.json"
   ],
   "plan": "/Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json"
  }
 ],
 "verdict": "fail"
}
census foreign_pids: [67916, 67937, 67941, 68088, 68109, 68111, 74488, 75861, 75865, 85234] own_pids: [75833, 75838, 85310, 85313]
```

## D3 the 2026-09-16 root: `ls -la /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916` and `ls -la /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night`
```
total 168
drwxr-xr-x@ 14 edr  staff    448 Sep 16 13:20 .
drwxr-xr-x@ 11 edr  staff    352 Sep 21 21:58 ..
-rw-r--r--@  1 edr  staff  45076 Sep 16 09:24 calibration_plan.json
-rwxr-xr-x@  1 edr  staff   8916 Sep 16 09:24 chain.zsh
-rw-r--r--@  1 edr  staff    119 Sep 16 09:24 chain.zsh.chain-source.sha256
-rw-r--r--@  1 edr  staff     76 Sep 16 09:24 chain.zsh.sha256
-rw-r--r--@  1 edr  staff    246 Sep 16 09:24 identity-epoch.json
drwxr-xr-x@ 13 edr  staff    416 Sep 16 20:52 night
-rw-r--r--   1 edr  staff    358 Sep 16 13:20 night.log
-rw-------@  1 edr  staff    851 Sep 16 09:24 night_plan.json
drwxr-xr-x   3 edr  staff     96 Sep 16 20:52 operator_logs
drwxr-xr-x  33 edr  staff   1056 Sep 16 13:20 results-clone
drwxr-xr-x   3 edr  staff     96 Sep 16 09:45 runs
-rw-r--r--@  1 edr  staff    541 Sep 16 09:24 t1-bindings.json

total 488
drwxr-xr-x@ 13 edr  staff     416 Sep 16 20:52 .
drwxr-xr-x@ 14 edr  staff     448 Sep 16 13:20 ..
-rw-r--r--   1 edr  staff  200071 Sep 16 20:52 censuses.jsonl
-rw-------   1 edr  staff      90 Sep 16 20:52 chain.exited
-rw-------   1 edr  staff     112 Sep 16 09:45 chain.started
-rw-r--r--   1 edr  staff     105 Sep 16 20:52 chain.stderr.log
-rw-r--r--   1 edr  staff   17391 Sep 16 20:52 chain.stdout.log
-rw-r--r--   1 edr  staff       0 Sep 16 13:20 launchd.deadman.err
-rw-r--r--   1 edr  staff       0 Sep 16 13:20 launchd.deadman.out
-rw-r--r--   1 edr  staff    1405 Sep 16 20:52 launchd.night.err
-rw-r--r--   1 edr  staff       0 Sep 16 09:45 launchd.night.out
-rw-------   1 edr  staff    4212 Sep 16 09:45 receipt.json
-rw-------   1 edr  staff     340 Sep 16 13:20 refusal.json
```

## D4 `cat /Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night/refusal.json`, `chain.started`, `chain.exited`, `chain.stderr.log`
```
{
  "plan_id": "d079-epoch-25g83-derivation-n1-20260916",
  "receipt_class": "DIAGNOSTIC_NO_PACK",
  "refusal": {
    "detail": "chain process group is still alive or cannot be disproven",
    "evidence": {
      "pgid": 20946
    },
    "reason": "night_chain_alive"
  },
  "schema": "joulewise.night_refusal.v1",
  "verdict": "REFUSED"
}

{
  "epoch_s": 1789577102.829459,
  "pgid": 20946,
  "pid": 20946,
  "start_time": "Wed Sep 16 09:45:02 2026"
}

{
  "epoch_s": 1789617139.0360892,
  "exit_code": -15,
  "monotonic_ns": 89823770936916
}

{"event": "calibration_pre_reserve_authorized", "session_id": "d079-epoch-25g83-derivation-n1-20260916"}
```

## D5 `python3 -c` summary of `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night_plan.json` (plan id, t0, head) and `ls ~/Library/LaunchAgents | grep -i joulewise`
```
{'plan_id': 'd079-epoch-25g83-derivation-n1-20260916', 't0_epoch_s': 1789577100.0, 'window_max_s': 9000, 'measurement_head': '32243adca1bfc8822e8001e4bac58000d591aa4f', 'schema': 'joulewise.night_plan.v2', 'receipt_class': 'DIAGNOSTIC_NO_PACK'}
com.joulewise.magistrate.plist
```

## D6 harvest archive of that root: `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/SHA256SUMS` (20 entries) checked against the archive copy and against the LIVE root
```
archive: OK=20 FAILED=0
live root: OK=20 FAILED=0
./calibration_plan.json
./chain.zsh
./chain.zsh.chain-source.sha256
./chain.zsh.sha256
./identity-epoch.json
./night.log
./night/censuses.jsonl
./night/chain.exited
./night/chain.started
./night/chain.stderr.log
./night/chain.stdout.log
./night/launchd.deadman.err
./night/launchd.deadman.out
./night/launchd.night.err
./night/launchd.night.out
./night/receipt.json
./night/refusal.json
./night_plan.json
./operator_logs/derivation-chain.log
./t1-bindings.json
live root file count: 7705 (results-clone/ alone: 7685)
```

## D7 the other three discovered roots, for symmetry: markers present
```
d079-epoch-25g83-derivation-n1-20260916: courier.sent=n result.json=n refusal.json=y chain.started=y chain.exited=y
d079-epoch-25g83-derivation-n1-20260919: courier.sent=y result.json=y refusal.json=n chain.started=y chain.exited=y
d079-epoch-25g83-derivation-n2-20260919: courier.sent=y result.json=y refusal.json=n chain.started=y chain.exited=y
qpe01-pilot-n1-20260920: courier.sent=y result.json=y refusal.json=y chain.started=y chain.exited=y
```

## D8 today's census classification (from D2's `check.json`): sessions, own chain, foreign set; then `ps -o pid,ppid,command` for the PIDs in the caller's own session tree
```
argv: ['/usr/bin/pgrep', '-lf', '[c]odex|[c]laude|[t]3']
own_pids: [75833, 75838, 85310, 85313]
foreign_pids: [67916, 67937, 67941, 68088, 68109, 68111, 74488, 75861, 75865, 85234]
receipt_class: DIAGNOSTIC_NO_PACK
session root 67916 exempt False descendants [67937, 67941, 73498, 73499, 73573, 74488, 82693, 85234, 85236] workloads []
session root 68088 exempt False descendants [68109, 68111] workloads []
session root 75838 exempt False descendants [75861, 75865, 75867, 75892, 85310, 85313, 85358] workloads []
instruction: Magistrate, all owned agents, MCP children and helpers must be gone before REQUEST.
verdict: fail reason: None
  PID  PPID COMMAND
75833     1 /opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python /Us
75838 75833 /Users/edr/.local/bin/claude -p You are the top-level JouleWise magistrate, relaunched headless at 2026-09-21T21:50:57.817051-07
75861 75838 node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=fa
75865 75861 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex mcp-s
```

## D9 the prior real arm (plan `qpe01-pilot-n1-20260920`, armed 2026-09-19 23:16 PDT by the bench script set) recorded the SAME shape and proceeded: `arm-census-final.json` and the census line of `notice-evidence.txt` from its retired staging directory `/Users/edr/night-archive/qpe01-pilot-n1-20260920-staging-retired-1790052975/arm-attempts/000001/`
```
{"diagnostics": [], "discovery_argv": ["/usr/bin/pgrep", "-f", "codex|claude|t3"], "foreign_pids": [97440, 97445], "own_pids": [76616, 76624, 76677, 97423, 97427], "plan_sha256": "463d25f07860a86f2a0255a327ab3385490b718932b42c8feb234c252972920e", "receipt_class": "DIAGNOSTIC_NO_PACK", "sessions": [{"descendant_pids": [76616, 76624, 76677, 76678, 97440, 97445], "exempt": false, "root_pid": 97427, "workloads": []}], "workloads": []}
diagnostic only; existing all-agents-closed rule still applies

8:census (step 3, two 30 s apart): foreign_pids [97440, 97445] = this activation's own idle codex mcp-server helper (descendants of root pid 97427), workloads []; no seat/Workflow/foreign session (no other bin/claude process)
```
