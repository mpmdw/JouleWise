```json
{
  "schema":"claude-codex-report/v1",
  "genre":"implementation",
  "status":"findings",
  "completion":"partial",
  "summary":"Implemented D-165 consumer-side manifest attachment binding and regressions; required rebase remains blocked by workspace Git-metadata permissions.",
  "workspace":{"base_requested":"76dc0c08018b41ef26ea016155bb931bd41de010","base_mode":"exact","head_start":"76dc0c08018b41ef26ea016155bb931bd41de010","head_end":"76dc0c08018b41ef26ea016155bb931bd41de010","upstream_end":"c401bf91f59885ab55802f3c466612ab5d512c8a","branch":"feat/d165-dominance-closeout-core"},
  "pathspec":["docs/contracts/d165_dominance_closeout.md","joulewise/dominance_closeout.py","scripts/build_d165_dominance_closeout.py","tests/test_d165_dominance_closeout.py"],
  "unowned_dirty":[],
  "verdict":{"implementation":"implemented","acceptance":"pending_verification"},
  "verification":[
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".","----------------------------------------------------------------------","Ran 1 test in 0.017s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s\\n\\nOK"}},
    {"id":"V2","kind":"suite","cmd":"python3 -m unittest tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["...................................","----------------------------------------------------------------------","Ran 35 tests in 10.995s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 35 tests in .*s\\n\\nOK"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".","----------------------------------------------------------------------","Ran 1 test in 0.002s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in .*s\\n\\nOK"}},
    {"id":"V4","kind":"inspection","cmd":"python3 -c 'import hashlib; from configs.campaigns.d117_contrast_v5 import generate_configs as g; from joulewise.analysis_manifest_v3 import canonical_json_bytes; print(hashlib.sha256(canonical_json_bytes(g.dominance_criterion_registration())).hexdigest())'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"]},"expected":{"exit_code":0,"tail_regex":"^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"}},
    {"id":"V5","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[
    {"id":"F1","kind":"environment","level":"blocking","text":"Attempted `git rebase main` to flatten the pre-existing merge, but Git could not create `.git/worktrees/JouleWise-wt-closeout/rebase-merge` because that metadata is not writable in this workspace. `main` also advanced during the run.","needs":"Rebase this branch onto current main (`c401bf91…`) in an environment permitted to write Git worktree metadata, then rerun the focused suite."}
  ]
}
```

## Change

| Item | Cure | File:line | Regression |
|---|---|---|---|
| Raw source binding | Close-out records exact manifest and sidecar file-byte SHA-256 values; validator rechecks supplied bytes. | [core](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1322), [builder](/Users/edr/code/JouleWise-wt-closeout/scripts/build_d165_dominance_closeout.py:52) | [manifest drift](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:417) |
| Manifest attachment | Enforces `evidence.dominance_replay_sidecar` shape, digest, identity, and per-contrast block sets. | [core](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1130) | [guard matrix](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:760) |
| CLI | Reads raw files once and accepts `--finalized-manifest`, `--floor-artifact`, and `--replay-sidecar`. | [builder](/Users/edr/code/JouleWise-wt-closeout/scripts/build_d165_dominance_closeout.py:208) | [CLI parity](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:916) |
| Contract | Documents attachment shape, byte digests, named neither-branch stops, producer ownership, and correct manifest field paths. | [contract](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:179) | Focused suite |

## Guard table

| New guard | Named refusal | Regression |
|---|---|---|
| Attachment absent/incomplete | `manifest_lacks_replay_sidecar` | Builder matrix: manifest attachment |
| Attachment digest differs | `replay_sidecar_digest_mismatch` | Builder matrix: forged self-consistent sidecar |
| Attachment identity differs | `replay_sidecar_identity_mismatch` | Builder matrix: sidecar identity |
| Contrast block sets differ | `manifest_block_membership_mismatch` | Builder matrix: another campaign |
| Manifest bytes drift after close-out | Validator rejects `closeout.finalized_manifest_sha256` | `test_source_hash_mutation_refuses_validation` |

## Registration hash

Before and after: `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`.

## Verification notes

`git diff --stat`:

```text
 docs/contracts/d165_dominance_closeout.md |  51 ++++++-
 joulewise/dominance_closeout.py           | 173 ++++++++++++++++++++++-
 scripts/build_d165_dominance_closeout.py  |  47 +++++--
 tests/test_d165_dominance_closeout.py     | 220 ++++++++++++++++++++++++++++--
 4 files changed, 468 insertions(+), 23 deletions(-)
```

I chose rebase, not merge, to restore linear history, but it was blocked before edits by:

```text
git rebase main
error: could not create temporary .../.git/worktrees/JouleWise-wt-closeout/rebase-merge: Operation not permitted
```

No commit was made.

## Residual risk

The implementation is tested, but the branch remains unre-based and `main` advanced from `a20c7227…` to `c401bf91…` during this session.