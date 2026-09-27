# ISSUANCE-CUSTODY-OUTSIDE-REPO-01: council synthesis (magistrate 77b1bee2, Opus 5.5)

The seats, all blind, on [20-consult-charge.md](20-consult-charge.md), with the scout as the Sol seat:

| Seat | Recommends | Report |
|---|---|---|
| Sol 6.0 xhigh | A: an artifact-level logical `source_root` plus validator, verifier and reissue changes | [11](11-sol-scout-report.md) |
| Astra 6 high | B: per-night roots keyed by session id, validator member-key change | [12](12-astra-consult.md) |
| Opus 5.5 | C: one issuer flag, no verifier or reissue change, a provenance note | [13](13-opus-consult.md) |
| Fable 5.1 (cold) | C: a session- and capture-bound naming function, a read-only `verify-members` command, an optional fixed-text note; the issuer only | [14](14-fable-consult.md) |

**Adopted: design C as Fable §5.1 specifies it (sites 1–8), with these rulings.**

**Why C.**
- It is the smallest change: R7 of statement item 6(d) requires it, and the precedent is Revision 2's "the smallest change that removes it".
- Both Fable and Opus executed probes showing that the verifier (`--repo-root`, caller-supplied) and the reissue tool (`--corpus-root`) already resolve members from a caller-named root. The validator checks only that `source_directory` is a string.
- So A's descriptor would go unenforced without a validator change.
- B changes the member key set that the production loader compares for exact equality (`calibration_bracketing.py:876–883`). That is the largest change, and it sits on the loader's path.
- C gets B's per-session binding from fields the ledger already has: the first stored path part must equal the row's session id. It also closes A's weakness (probe P1): containment alone would admit a capture from another session's night directory under the same parent.

**Rulings on the open points.**
1. **Flag name: `--corpus-root`**, not `--custody-root`. Opus: the runbook uses `custody_root` for the per-night directory, and the reissue tool already names the same concept `--corpus-root`.
2. **Site 6 (the fixed-text note): adopted.** Opus and Fable both recommend it. `derivation_notes.member_custody` holds fixed text: what the stored paths are relative to, and the `verify-members` command. It holds no absolute path, and the validator admits it unchanged.
3. **Fable's guard F2 is binding.** `--corpus-root` flows to the naming function and nothing else. The ledger, the head pin, the battery records and the git lookups stay on the run checkout. The Opus BLOCKER says the same: `--repo-root` cannot be pointed at night-custody.
4. **Astra's hardening, folded into the new function and `verify-members` (F3):**
   - raw-string canonical POSIX checks before any normalization (reject empty, absolute, `.`/`..` components, duplicate or trailing separators);
   - containment of the directory and of each primary file, with symlinks not followed (reuse the no-follow reader in `joulewise/authentication_io.py:281` where it fits);
   - root and path failures refuse before any member-value parser is reached, wherever the existing order allows;
   - a missing file or root refuses the whole run and never drops a member.
5. **Not in this repair (R7), registered as lanes:**
   - **CORPUS-PATH-GUARD-READERS-01:** the verifier and reissue tool accept absolute or `..` stored paths (Opus P4/P9, Astra, Fable F6). The issuer and `verify-members` guard new artifacts. This must land before any reissue of the new generation.
   - **CORPUS-RAW-REPLAY-01:** the member checks authenticate `manifest.json` and `instrument_evidence.json` only, not every raw file (Astra F4).
   - **ISSUANCE-ARCHIVE-PACKET-01:** the ledger is gitignored, so the post-issuance archive must hold the ledger file, the head pin and the verdicts with the night directories, keeping the `<plan_id>/runs/instrument_validation/<id>` layout (Astra F4, Fable F3, Opus). This must land before any offload.
   - **REISSUE-HISTORICAL-LEXEME-01:** pre-existing; reissue requires stored-lexeme equality, but r6/r7 are non-member-value (Astra F5).
   - **DRYRUN-MEMBER-CUSTODY-01:** the count-only dry run should gain a value-blind member-path check (addendum N3, Opus).
6. **Dissent recorded.**
   - Sol (A): a descriptor makes the root explicit in the artifact. Answered by site 6's note plus the session binding.
   - Astra (B): independent per-night restores without a common parent. Answered: `verify-members` takes one parent, and a reader can place two restored night directories under any directory `P`. The cost of B's loader change outweighs that convenience. This is recorded for the cold gate on the final diff.
   - Astra's seat also self-reported reading historical (r-generation) summaries in RUN_STATE. No W1/W2 value was read; this is disclosed.

**Next:** a Sol 6.0 xhigh implementation seat under an enforced WRITE_SCOPE; then Opus and Sol lenses; then the fresh cold gate on the final diff (addendum §6.1). That gate is also statement item 6(c)'s ruling. Then the PR under the full tier, then the prepare step.
