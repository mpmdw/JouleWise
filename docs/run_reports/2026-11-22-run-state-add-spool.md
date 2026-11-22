# RUN_STATE spool audit fixes, 2026-11-22

The Tier 1 build follows Gemini Deep Audit 4.1 and 4.2. The clean feature
worktree fast-forwarded to `origin/main` at `82b93c157` before edits.
Mission M0 found no active stop card. The implementation checks used
synthetic inputs and temporary bare repositories with a temporary home.

## Findings

| Finding | Disposition | Named regression |
| --- | --- | --- |
| F1 / 4.1 | NEEDS_SPEC. Strict owner validation reproduced the compatibility failure described below. | `test_gemini_4_1_unregistered_pointer_owner_is_refused` in the local trial |
| F2 / 4.2.1 | Fixed in `3cd3fd051`. A new add refuses while the caller's spool has pending requests. The caller can flush, then retry. | `test_gemini_4_2_1_pending_item_cannot_be_overtaken` |
| F3 / 4.2.2 | Fixed in `3cd3fd051`. The spool captures attachment bytes and mode. Replay stages from that snapshot and checks the staged byte identity. | `test_gemini_4_2_2_spooled_with_file_replays_original_bytes` |
| F4 / 4.2.3 | Fixed in `3cd3fd051`. Validation failures move to `failed/` with a `.reason` file. Flush continues in queue order and exits 2 after draining a queue with quarantines. Transient Git failures still stop flush with pending entries intact. | `test_gemini_4_2_3_stale_set_is_quarantined_and_later_items_land_in_order` |

Legacy queued requests with no attachments replay as before. A legacy request
with attachments goes to `failed/` because its original bytes are unavailable.

## NEEDS_SPEC

At the base, 156 pointer declarations parse and produce the checked-in
`CURRENT.json` byte for byte. Seven historical declarations use owner text
outside `run_state_items.OWNERS`, in items 316, 310, 292, 291, 291b, 290,
and 289. The first is `research lead` at line 12638 in this base. The strict
trial rejected that block with `INVALID_OWNER` on both interpreters. The
generator checks every declaration and the writer calls the generator before
landing any item, so this would stop otherwise valid additions from both
writers.

The lead should choose between a lead-owned normalization of the seven
historical declarations before enforcing strict validation and a precisely
scoped historical exception. Normalize first if editing those declarations
is permitted, then rerun the named regression and regenerate against the
updated main. F1 needs that ruling before it can enter the branch.

## Verification

All four named regressions reproduced the failures on the original code. The
strict F1 trial passed its synthetic case and failed
`test_real_repository_agrees` on both interpreters.
The shipped writer regressions also cover legacy attachments, Git line-ending
normalization, and transient fetch failure.

The focused suites passed 99 tests each on Python 3.13.18 and 3.14.6 across
`test_gen_current`, `test_run_state_items`, and `test_run_state_add`.
`gen_current.py --check` passed on both interpreters. The typed-items check
and `git diff --check` passed. The full suite runs in the draft PR's hosted
CI. The Tier 1 post-build cross-family review remains a lead gate.
