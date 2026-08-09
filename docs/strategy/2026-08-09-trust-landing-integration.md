# Trust landing — integration plan (T2, 2026-08-09) — durable, /clear-safe

The trust mint bar is PROVEN (decisive corrected + isolated-proven; attack
matrix ran end-to-end all-15-refused in the 3.5h run). Landing it revealed a
real **trust×recovery integration seam** on `calibration_ledger.py`. This doc
carries the exact remaining work so any continuation executes it cleanly.

## Method (verified, Sol bdltx9fh0): clean-branch resynthesis
Branch `impl/d117-postcollection-trust-clean` from origin/main (recovery
merged); 3-way merge of a89f279 (tag `safety/trust-a89f279-checkpoint`);
resolve conflicts (below); `git rm -r --cached` the custody content subdirs
(keep manifest); **sever dirty ancestry** with
`git commit-tree <tree> -p origin/main` (single parent = main, no 3.3GB blob
history); verify `git rev-list --objects HEAD | grep 'custody_store/[^/]*/'`
EMPTY; full suite green; PUBLISH release `fixture-d117-v2-production-v1` (CI
downloads the asset anonymously — no draft); PR → CI `d117-production-proof`
(authoritative decisive run) → D-121 → merge = MINT BAR LIFTS. Reversible until
merge; old branch preserved by tag + 55MB 1cae2bc bundle. The recorded T1
`git rm --cached + amend` procedure is INSUFFICIENT (only strips the tip; blobs
stay in the 1cae2bc parent) — do NOT use it.

## Conflict marker resolutions (Sol-analyzed, magistrate-adopted)
- **H1 imports (~L46): UNION** — keep BOTH `from authentication_io import (…)`
  (trust) AND `from calibration_exits import (REFUSAL_BY_CODE, RefusalCode)`
  (recovery). Both defined + used.
- **H2 (~L1323): KEEP HEAD `_decode_line`.** Trust's side is the deleted
  sidecar `_read_append_journal` (references removed `_append_journal_path`/
  `_valid_append_journal`). Do NOT splice it in; the legacy-journal read intent
  is carried by the surviving `_legacy_journal_metadata`.
- **H3 (~L3553): KEEP HEAD `_new_append_intent`.** Trust's side is the deleted
  sidecar `_record_append_recovery` (references removed `APPEND_RECOVERY_SCHEMA`/
  `_append_recovery_path`/`_atomic_private_write`). Recovery evidence now lives
  in immutable APPEND_INTENT_EVENT/ABANDONMENT_EVENT receipts.
- **H4 exports (~L5507): UNION** — ABANDONMENT_EVENT + CUSTODY_STORE_MANIFEST_NAME
  + CUSTODY_STORE_MANIFEST_SCHEMA (+ the following unchanged exports).
- **decision_log.md (L145, L7788): UNION** — D-120 (trust) section+row placed
  before the unchanged D-121…D-128; no entry dropped. (Exact D-120 text in Sol
  report `trust-conflict-out.md`.)

## R1 — the real integration work (blocker; a FRESH careful cycle, NOT a marker fix)
After markers resolve, recovery added **9 direct readable-I/O sites** in
`calibration_ledger.py` that trust's registration-at-read guard
(`tests/test_authentication_io.py`, which AST-scans this module and exempts only
4 named non-auth writers) will REJECT. Each needs a SECURITY judgment —
content-bearing read → route through `read_authentication_input`; descriptor-
only/writer op → narrowly justified classification in the guard (NEVER a broad
exemption — that silently weakens trust's central guarantee):
1. `_filesystem_type.read_text` — reads mountinfo (/proc-like); not an auth input → classify/exempt.
2. `_legacy_journal_metadata.read_bytes` — legacy journal content → likely route through auth helper.
3. `_open_slot_sidecar` os.open — descriptor → classify.
4. `inspect_calibration_ledger.read_bytes` — diagnostic ledger read → adjudicate (auth vs classify).
5. `open_append_descriptor` os.open — descriptor/write → classify.
6. `publish_genesis_payload` os.open — dirfd genesis (recovery FIX-A) → classify (descriptor-only).
7-8. `resolve_ledger_lease_identity` os.open ×2 — dirfd lease identity (recovery FIX-A) → classify.
9. `validate_frozen_reservation_plan.read_bytes` — reads the plan (content) → likely route through auth helper.
VERIFY: `python3 -m unittest tests.test_authentication_io` then full discovery,
BOTH green — needs the flake fix (impl/recovery-flake-fix) landed first so the
suite doesn't hang in test_calibration_exits.

## State
- Merge sits UNRESOLVED in throwaway worktree `…/scratchpad/trustclean`
  (reversible; `git merge --abort` anytime). a89f279 tag-preserved.
- Full Sol analysis: session scratchpad `trust-conflict-out.md`.
