# Flash-Next resume after source release

2026-11-19 · Sol 6.2 · Tier 1 engineering · RL-182 §2

PR #838 required a retained copy to authenticate a committed journal row that used the canonical chunk-composite digest. PR #825 releases each source shard after committing its row. The two-release synthetic regression reproduced the refusal on the pre-fix converter at `0ccbe6577`.

Mission M0 found no active stop card. After the host pause, the only local change was the uncommitted converter edit. The fetch found no pushed branch or prior PR for this lane. The code and regression commit `961318c10f9c54537adc1dcf558774344fc5c19e` is based on `6640a6671`.

## Change and verification

A resume now streams each released committed source from byte zero using the existing pinned downloader. Each read is bounded by 8 MiB and the remaining canonical chunk length. The same bytes feed the whole-file LFS SHA-256 and the canonical digest. The journal row passes only when the pinned checksum, journal input digest and existing output span digests all match. Resume logs each verified released shard and a byte total. A present source still uses the prior checks. The journal authentication finishes before cleanup, new conversion work or manifest publication.

| Finding or acceptance case | Regression in `961318c10` | Result |
| --- | --- | --- |
| A resume after two releases must reuse committed output and match uninterrupted conversion | `test_resume_after_two_released_chunked_shards_matches_uninterrupted` exercises fragmented bounded reads, staging inventory, conversion calls, progress output and byte-identical manifests | PASS |
| A one-bit edit to a released row must refuse | `test_resume_refuses_one_bit_tamper_of_committed_input_digest` checks canonical plain and composite digests | PASS |
| Changed upstream bytes must refuse even with a matching journal digest | `test_resume_refuses_released_source_with_wrong_lfs_checksum` | PASS |
| Truncation or a network failure must refuse | `test_resume_refuses_truncated_released_source` and `test_resume_refuses_released_source_on_network_failure` | PASS |
| Retained-source verification and prior resume behavior must continue to work | Focused module, including retained incomplete-source and altered-source refusals and the interrupted partial-download and completed-manifest cases | PASS |

Each refusal regression checks zero unlink calls, byte-for-byte preservation of existing job files and the absence of a completed manifest. The former released-chunked-source refusal assertion was replaced by the new successful resume case. Existing transfer-count assertions now account for the replay of released plain-digest shards, including on a completed-job check.

- Python 3.14 `python3 -B -m unittest tests.test_align_stream_qwen4_exp tests.test_check_gate_ledger` passed 61 tests with one optional native parity skip.
- Python 3.13 `python3.13 -B -m unittest tests.test_align_stream_qwen4_exp` passed 19 tests with one optional native parity skip.
- `git diff --check` passed. Hosted PR CI owns the canonical full suite on this lane. Local evidence uses synthetic fixtures. Live validation remains PROVISIONAL.

## Independent review and handoff

The read-only executing reviewer checked `961318c10` against `6640a6671` and compared the digest implementation with the pinned canonical code at `97d780d59`. The reviewer ran `python3 -B -m unittest tests.test_align_stream_qwen4_exp` with native parity disabled. Nineteen tests passed and the optional native test skipped. The reviewer returned PASS with zero findings. The reported resume blocker is fixed by `961318c10` and the covered refusal paths passed. NEEDS_SPEC has no entries.

The lead owns merge and any later real-weight validation. The draft PR ledger records hosted verification on its final head.
