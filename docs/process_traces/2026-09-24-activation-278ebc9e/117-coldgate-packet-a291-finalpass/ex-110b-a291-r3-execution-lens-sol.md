```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One malformed-roster exception escapes the typed refusal boundary; legal edge rosters and deterministic replay passed focused probes.",
  "workspace": {
    "base_requested": "0fa4e6e3",
    "base_mode": "exact",
    "head_start": "3fb98469f9077f836909651c005b0fbdcafa582d",
    "head_end": "3fb98469f9077f836909651c005b0fbdcafa582d",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "location": "joulewise/scored_packer.py:35,283,293-296",
        "witness": "A valid sealed roster whose sha256 is replaced by 1,200 nested lists raises RecursionError from both _seal and requeue_overrun, rather than PackingRefusal.",
        "cure": "Validate the digest field before copying the roster and convert RecursionError from digest processing into PackingRefusal."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nfrom joulewise import scored_packer as sp,scored_registration as sr\nfrom tests.test_scored_registration import fixture\ng,p=fixture();reg=sr.Registration.from_mapping(g);r=sp.pack(reg,p)\nv=0\nfor _ in range(1200):v=[v]\nr['sha256']=v\ntry:sp._seal(reg,r)\nexcept BaseException as exc:print('DEEP_SHA',type(exc).__name__,getattr(exc,'code',None))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DEEP_SHA RecursionError None"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DEEP_SHA RecursionError None"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nimport time\nfrom joulewise import scored_packer as sp,scored_registration as sr\nfrom tests.test_scored_registration import fixture\nfrom tests.scored_roster_checker import check_roster\ng,p=fixture(n=14,block_size=1,mode='pilot',cap=1.0)\nreg=sr.Registration.from_mapping(g); r=sp.pack(reg,p)\nprint('ROOT',len(r['envelopes']),len(r['blocks']),flush=True)\ntotal=time.monotonic()\nfor k in range(131):\n e=next(e for e in r['envelopes'] if e['kind']=='loaded' and e['observations'] is None)\n obs=[dict(block_id=bid,status='not_started',elapsed_s=None) for bid in e['blocks']]\n begin=time.monotonic();r=sp.requeue_overrun(reg,r,e['index'],obs);dt=time.monotonic()-begin\n if k+1 in (1,50,100,130,131):print('EVENT',k+1,'SECONDS',round(dt,3),'TOTAL',round(time.monotonic()-total,3),flush=True)\nprint('CHECKER_ROWS',len(check_roster(g,r,p)),flush=True)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EVENT 130 SECONDS 1.403 TOTAL 88.498",
          "EVENT 131 SECONDS 1.423 TOTAL 89.92",
          "CHECKER_ROWS 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EVENT 131 SECONDS [0-9.]+ TOTAL [0-9.]+\\nCHECKER_ROWS 0"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The registration contract sets no maximum item count. Replay cost grows with history; the 131-event probe took 89.92 seconds overall, with a 1.423-second final call. No runtime limit is specified.",
      "needs": "Profile larger legal registrations before assigning a runtime gate."
    }
  ]
}
```

## Findings

| ID | Severity | Finding and cure |
|---|---|---|
| F1 | should_fix | [The digest copy](/Users/edr/code/wt-278ebc9e-r3lens-sol/joulewise/scored_packer.py:35) can raise `RecursionError` before `_seal` produces a typed refusal. The same malformed input escapes through `requeue_overrun`. Validate the digest field before copying and translate recursion failures to `PackingRefusal`. |

**Accepted clauses probed:** block size 1, an uneven final slice, registered and pilot packing, fully terminal cells, executed status, and repeat-run digest determinism. The registered short-slice terminal roster had 12 events, 110 terminal entries, zero checker violations, and executed status equal to the checker’s result. Two identical registered histories produced identical event digests.

**Probe tails:** `PACK 5 1 pilot 11 0 True`; `PACK 11 2 registered 12 0 True`; `EXECUTED_AGREES True`; `HISTORY_DETERMINISTIC True EVENTS 10`; `seal RecursionError None`; `requeue RecursionError None`. The checkout remained clean. Per the seat instruction, I ran focused probes only.

## Residual risk

The contract has no largest registration size. At 131 events, the measured sequence remained valid but took 89.92 seconds to build; the final `requeue_overrun` call took 1.423 seconds. There is no specified runtime threshold against which to classify that cost as a defect.