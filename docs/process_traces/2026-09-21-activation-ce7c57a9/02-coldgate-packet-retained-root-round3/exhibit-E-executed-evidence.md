# Exhibit E — executed evidence at the magistrate bench, activation ce7c57a9, 23:2x PDT 09-21

## E1 Queue drift at af85b38a (worktree wt-retention3-29ea94df, clean, detached at af85b38a)
```
$ python3 -B scripts/gen_state.py --check
rc=1
```

## E2 CI runs that check (.github/workflows/ci.yml at main ecefd46a)
```
111:        run: python scripts/gen_state.py --check
```

## E3 Seat exit records
```
delta-2 rc=0 status=OK semantic_status=findings completion=complete run_status=OK scope_action=passed 
delta-3 rc=0 status=OK semantic_status=findings completion=complete run_status=OK scope_action=passed 
```

## E4 Full sharded replay of af85b38a
RUNNING at packet assembly (detached job replay.pid 31158); result will be appended to record 03, not to this packet.
