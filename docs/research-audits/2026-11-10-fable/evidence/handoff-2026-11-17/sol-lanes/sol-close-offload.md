[PR #807](https://github.com/mpmdw/JouleWise/pull/807) is **draft and unmerged**.

- Head: `588a4164b6c14663aaaa35e26a1c9f01cb8b62d8`
- [CI green](https://github.com/mpmdw/JouleWise/actions/runs/44008874817): 13,074 tests, zero failures/errors, 212 skips. Draft gate-ledger skipped.
- Review: **REFUSE**. One fresh Sol seat plus two deltas closed all four implementation findings; contract conflicts remain. The supplied wrapper was OS-blocked, so the seat used the built-in fallback.
- PR body read-back verified. No MBP contact.

Current prototype command, **not issued for production**:

```sh
/opt/homebrew/bin/python3 -B /Users/edr/code/jw-close-offload/scripts/close_offload.py --deadline "$CLOSE_DEADLINE_EPOCH"
```

Proposed standing text after integration/admission:

> After every Check, bundle push and MBP desk, run close-offload inside the close interval before any arm, F0 included. Await exit; every nonzero or unverified result holds the next arm. Keep newest outputs for GAP. Retain the materialized encrypted archive until cloud round-trip and SSD verification agree; require fresh pending-transfer CLEAR before arming.

**NEEDS_RULING:** RL-174 D was published during the build and requires the shared #804 backend, encryption, cloud round-trip and SSD retention. Should I **retarget to RL-174 D/#804 (recommended)**, or retain the original behavior under explicit owner exceptions? This blocks ADMIT and standing-item issuance under AGENTS.md’s contract-conflict rule.