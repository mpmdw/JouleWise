# RUN_STATE spool audit fixes, 2026-11-22

The Tier 1 build follows Gemini Deep Audit 4.1 and 4.2. The clean feature
worktree fast-forwarded to `origin/main` at `82b93c157` before edits.
Mission M0 found no active stop card. The implementation checks used
synthetic inputs and temporary bare repositories with a temporary home.

## Findings

| Finding | Disposition | Named regression |
| --- | --- | --- |
| F1 / 4.1 | Fixed in `7689a9dd6`. Only the seven exact historical pairs can use an unregistered owner, once each per render and only below a strictly higher pointer rank. The selected pointer and the JSON validator require a registered owner. | `test_gemini_4_1_unregistered_pointer_owner_is_refused` and seven companion tests |
| F2 / 4.2.1 | Fixed in `3cd3fd051`. A new add refuses while the caller's spool has pending requests. The caller can flush, then retry. | `test_gemini_4_2_1_pending_item_cannot_be_overtaken` |
| F3 / 4.2.2 | Fixed in `3cd3fd051`. The spool captures attachment bytes and mode. Replay stages from that snapshot and checks the staged byte identity. | `test_gemini_4_2_2_spooled_with_file_replays_original_bytes` |
| F4 / 4.2.3 | Fixed in `3cd3fd051`. Validation failures move to `failed/` with a `.reason` file. Flush continues in queue order and exits 2 after draining a queue with quarantines. Transient Git failures still stop flush with pending entries intact. | `test_gemini_4_2_3_stale_set_is_quarantined_and_later_items_land_in_order` |

Legacy queued requests with no attachments replay as before. A legacy request
with attachments goes to `failed/` because its original bytes are unavailable.

## F1 compatibility ruling

Seven of the 156 pointer declarations at the base use historical owner text
in items 316, 310, 292, 291, 291b, 290, and 289. The first strict trial
rejected item 316 with `INVALID_OWNER`. The lead approved a scoped exception
for the seven exact pairs in those superseded declarations. The exception
preserves the historical text and leaves all other block checks in force.

## Verification

The named regressions reproduced the audit findings on the original code.
The F1 cases verify exact pair matching, case sensitivity, repeat rejection,
strictly higher pointer rank, other block checks, and forged JSON rejection.
The writer regressions also cover legacy attachments, Git line-ending
normalization, and transient fetch failure.

All 107 focused tests passed on each of Python 3.13.18 and 3.14.6 across
`test_gen_current`, `test_run_state_items`, and `test_run_state_add`. On both
interpreters, `gen_current.py --check` exited 0 against `RUN_STATE.md` and
`CURRENT.json` read from the same `origin/main` revision,
`82b93c157e92e3ef510d1768c4043f88bd4bf799`. Explicit regeneration matched
the checked-in bytes on both interpreters. The check also exited 0 on each
interpreter after main advanced to `7eec25d6ab4cc8cf72b37532ad407cbb6ceefa13`.
The full suite runs in the draft PR's hosted CI. Tier 1 cross-family review
remains a lead gate.
