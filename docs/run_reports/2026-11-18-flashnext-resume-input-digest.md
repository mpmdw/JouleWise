# Flash-Next resume input digests

2026-11-18 · Sol 6.2 · Tier 1 engineering · MacBook Air (`Mac16,13`)

The lead assigned the verified MED deferred by [PR #825](https://github.com/mpmdw/JouleWise/pull/825), merged at `01bd07fe7`. The finding is in `scratch/pl-d-flashnext-stream-converter/audit-1/FINAL-MESSAGE.md` line 8. RL-182 §2.1 classifies conversion as engineering. Mission M0 found a clean worktree at main `56b0780fb`, no remote branch for this seat and no active stop card. [RL-182 at `61e8c9c2c`](https://github.com/mpmdw/JouleWise/blob/61e8c9c2c/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19801-L19810)

## Change

The standalone resume checks each committed input digest before unlinking any staged source, starting another shard transfer or publishing a manifest. For files up to and including 256 MiB, the canonical digest is the plain SHA-256 recorded in pinned LFS metadata. Above that boundary the canonical digest hashes the concatenated binary chunk digests. Resume authenticates a retained full-size source against its pinned whole-file SHA-256 before recomputing the canonical digest. A v1 journal with a released chunked source must refuse because the pinned whole-file digest alone cannot authenticate the saved chunk digest. This also applies when reopening a completed job. Any staged file present at refusal is preserved. [Canonical port source at `97d780d59`](https://github.com/mpmdw/JouleWise/blob/97d780d59/scripts/align_convert_qwen4_exp.py#L70-L124)

The check uses the existing v1 journal and canonical manifest layout. It adds no transfer or disk allocation. The standalone host gate, disk reserve and one-source staging continue to apply. Code and tests are in `09462eb059a0081ed1e1b016c504b070a2f033cd`.

## Verification

- The standalone synthetic reproduction at the base published a one-bit change to `inputs` with identical payload file and tensor hashes. The refusal regression failed against the base and passes with `09462eb05`.
- `python3 -B -m unittest tests.test_align_stream_qwen4_exp` passed 15 tests, with one optional native test skipped in the default Python. The cases cover the v1 resume at the inclusive plain-hash boundary, a one-bit edit with the next partial shard staged, and interruption after journal commit and before unlink. They also cover substitution of the plain digest for a chunked digest, a released chunked source and a changed retained source whose canonical digest agrees with an edited journal. Refusals assert zero subsequent downloads or unlink calls, no final manifest and identical files before and after the refusal. The valid interrupted runs produce byte-identical manifests to uninterrupted conversion.
- A separate compatibility check created both valid interrupted jobs through the actual `56b0780fb` CLI code. The candidate resumed both and matched the uninterrupted manifest bytes.
- `NativeParityTests` passed on the Air using the already installed pinned MLX 0.31.2 and mlx-lm 0.31.3 environment and the two verified port files from `97d780d59`. The existing synthetic `maxfit` test matched canonical input, payload and tensor hashes and loaded the verified artifact.
- `git diff --check` passed. Hosted PR CI owns the canonical full suite. The run uses synthetic evidence throughout and real-weight validation remains PROVISIONAL.

## Independent audit and handoff

Astra 6.2 reviewed `09462eb059a0081ed1e1b016c504b070a2f033cd` against `56b0780fb` and ran the focused module. Its verdict was PASS with zero findings. The review checked the size boundary against the pinned source, the digest authority for both conventions, refusal before any source or artifact write, and recovery to identical manifest bytes. The released-source refusal is the specified fail-closed behavior. No further specification is needed within this scope.

The lead owns integration and merge after reviewing hosted CI on the draft head.
