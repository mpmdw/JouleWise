# pack_root identity consult — Sol seat (verbatim, via lieutenant coordinator)

Seat: Sol gpt-5.6-sol, effort xhigh, read-only sandbox, WRITE_SCOPE [],
reverse Claude server disabled; one round; coordinated and load-bearing
citations replayed by an in-session lieutenant agent.
Bridge thread: 01a03a4a-89c9-7c93-b787-e74f2dc0e682. BASE_HEAD 9fd185ac
(contains f82247ee); line anchors verified at that head. Envelope: valid
final BRIDGE_REPORT_V1, status DISCUSSION, flags no_edits, read_only,
estate8_required, legacy_v3_ruling_preserved. Received by the magistrate
2026-08-25 midday; recorded verbatim below.

---

## Sol's recommendation (with a real disagreement)

**Adopt a refined option (a) — but successor-scoped, not global.** For registry-governed `_v4`+ generations, compare `pack_root` as repository-relative structural identity (both sides projected via `_repository_and_pack_relative`, line 2713); keep the serialized absolute path in receipt bytes as provenance; leave `_v3` and earlier comparison semantics untouched.

**The disagreement with the magistrate's leaning:** a global code cure would silently contradict a standing ruling — `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md` lines 138-141 pins `_v3` ordinary replay to the absolute path `/Users/edr/JouleWise-measurement-20260818` and defines a location mismatch there as a *location refusal, not corruption*. I verified this citation directly. Scoping the relative comparison by the registry's `family_publication_first_generation` (= 4, `configs/arm_readiness/d117_row_registry_v2.json` ~line 514, verified) cures S-0 §4 and all future generations without superseding the archival ruling.

Key findings, each verified or spot-checked by the coordinator:

1. **Integrity value of the absolute comparison:** none for bytes (no digest content), but it does carry *location binding* — and dropping `pack_root` entirely would be too weak (a byte-identical pack at a different repo-relative path would pass). The cure keeps the repo-relative path as identity and discards only the clone-specific prefix.
2. **Execution-boundary doctrine:** `resolve_frozen_plan` governs the argv literal, not receipt authentication; the resolver and absolute `--plan` literal are untouched.
3. **The comparison is the outlier:** the histsem verifier is location-agnostic by contract (`docs/contracts/receipt_histsem_verifier.md` §"Archival location rule", ~line 131 — verified: "never compares a freeze [receipt's root to the checkout]"), with a test proving a foreign absolute root still verifies (`tests/test_receipt_histsem.py` ~286); the marker lane records `pack_path` repo-relative by design.
4. **Test gap:** no test today mints, clones to a second absolute path, and replays — which is why CI never caught this.
5. **No other consumer:** the coordinator's own grep confirms no code subscripts `pack_identity["pack_root"]`; the only semantic consumer is the whole-map equality at 6448, and `_validate_pack_identity` (1480-1490) constrains it to a string only. Pinned receipts/pinsets keep their bytes and digests — nothing published changes.
6. **Losing options refuted:** (b) directory swap moves live estate custody twice per probe with an unrecoverable mid-swap crash state and fixes no future clone/CI/second-machine replay; worktrees still have a different absolute root and still refuse; symlink/bind-mount/chroot tricks are privileged, platform-specific, and recreate the recovery problem; re-minting breaks the C/M/S and predecessor digest chains.
7. **Estate cost, faced honestly:** the cure is claim-affecting enough (it broadens successor replay acceptance) to require a recorded ruling **plus estate 8** — Sol judges one clean re-execution cheaper than a permanently fragile ritual, and flags estate 7's blocked cases as never having tested their intended gates.

**Minimal diff shape:** one comparison helper immediately before `_load_freeze_reference`; replace only the equality at line 6448. Exact comparison for all fields except `pack_root`; for governed v4+ generations, require both recorded and current absolute roots to be canonical POSIX paths ending component-for-component in the current `pack_relative`, then compare the projection. Edge cases: no `resolve(strict=True)` on the historical path (validate lexically — it need not exist); no `normcase` (Git's spelling is the identity); pack outside a Git repo keeps refusing via `_repository_and_pack_relative`. No changes to `_pack_identity`, receipt rendering, the validator, or `resolve_frozen_plan`. Regression list: cross-clone idempotent replay, wrong-suffix rejection, non-pack_root mutations still refuse, v3 stays location-bound, histsem foreign-root PASS retained.

**Open questions Sol returns to the magistrate:** (1) preserve vs. explicitly supersede the v3 absolute-coordinate ruling — the S-0 cure does not require supersession; (2) whether a future receipt schema should add an explicit `pack_path` field (unnecessary and digest-breaking for this cure).
