# Trust rework F1/F2 ruling consult — response of record (2026-08-08)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge, from the
trust worktree at checkpoint 97fd4c1. Charge: the implementing
session's two NEEDS_RULING authority conflicts (issued estimator pin
vs mandated reduce.py conversion; absolute custody locators vs
checked-in fixture) — the magistrate's proposed rulings were
presented with license to disagree, and both were out-designed.

**MAGISTRATE ADOPTION (Fable, 2026-08-08): ADOPTED IN FULL,
superseding the magistrate's proposed R1/R2.** R1: reduce.py reverts
byte-identical (the issued pin is senior; inventory confirmed exactly
four pinned files, only reduce.py drifted); boundary pre/post hashing
REJECTED on a concrete A->B->A TOCTOU proof; instead a
registration-aware path capability (injected by BundleReader only
while a v2 session is active) registers the exact bytes returned to
the pinned component; AST exception is the exact (path, issued-sha)
pair with a five-callsite characterization guard; the production
open-auditor stays corroborating, bidirectional-equality evidence.
R2: relocation table REJECTED; content-addressed custody store
adopted (--calibration-custody-store ROOT, resolution by receipt
content_id, no fallback, all-or-nothing, every artifact
digest-checked against the receipt's artifact_sha256 map, strict
store manifest proven equal to the ledger-derived projection, SHA
carried through snapshot -> provenance -> post-bind validation).
Declared production inputs count as 'unpatched' for the decisive
regression; monkeypatching and authority substitution remain
forbidden. The 7-step sequencing and two-commit split bind the
resumed session.

---

## R1 — REJECT as stated; retain the senior-pin premise

`reduce.py` must revert byte-for-byte, but boundary pre-hashing plus post-return SHA verification is not TOCTOU-equivalent to registration at the actual read.

A concrete A→B→A attack exists:

1. Boundary registers authentic `raw/powermetrics.plist` bytes A.
2. The path is transiently replaced with B.
3. [`_derive_anchor_context`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/trust/joulewise/reduce.py:1738) parses B and derives its anchor. B can retain identical power values and relative spacing while changing the absolute timestamp anchor.
4. The path is restored to A.
5. [`_verify_instrument_calibration`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/trust/joulewise/reduce.py:1172) later reopens and authenticates A.
6. Post-return verification also sees A.

Both boundary hashes pass although computation consumed B. The test-only open auditor records only the path, so it also passes. This is exactly the attack registration at the returned-byte read would catch.

The second defect is assurance coverage: a fixture auditor samples executed branches. The AST guard universally constrains source. Excluding a module from the AST guard and relying on one fixture is therefore weaker, particularly because `reduce.py` discovers manifest members dynamically.

### Better ruling text

> Every source file whose exact bytes are pinned by the issued acceptance artifact remains byte-identical. For an issued-pinned component reached during v2 authentication, registration MUST occur on the exact bytes returned to that component, not merely before and after delegation.  
>  
> `BundleReader` SHALL inject, only while a v2 session is active, a registration-aware path capability whose `read_bytes`, `read_text`, and readable `open` operations delegate to `V2AuthenticationReadSession`. Path derivation through `/`, `parent`, and `resolve` MUST preserve that capability. The byte-identical `reduce.py` therefore performs its historical calls while the underlying path object registers the exact returned bytes.  
>  
> The AST exception is an exact `(path, issued_sha256)` exception, not a module-category exemption. For `joulewise/reduce.py`, a characterization guard MUST pin its issued SHA and its exact five direct-readable callsites in `_verify_instrument_calibration` and `_derive_anchor_context`; any callsite or byte change refuses the build. The production open auditor remains corroborating evidence and MUST prove bidirectional equality between observed evidence opens and registry records, but it is not the primary enforcement mechanism. Post-return re-verification may remain defense in depth.

This preserves `reduce.py` while restoring genuine registration-at-read. An unanticipated path read by the pinned component is registered automatically; the boundary does not need a second path-discovery algorithm.

## Exact issued source-pin inventory

The issued artifact’s `prospective_rederivation.estimator_code_sha256` contains exactly four source paths ([artifact](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/trust/configs/calibration/calibration_acceptance_d079_v2.json:39)):

| Issued-pinned file | SHA-256 |
|---|---|
| `joulewise/powermetrics_fiducial.py` | `21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3` |
| `joulewise/uncertainty_evidence.py` | `77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7` |
| `joulewise/adapters/powermetrics.py` | `7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca` |
| `joulewise/reduce.py` | `5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615` |

The first three still match exactly. Only `joulewise/reduce.py` changed in checkpoint `97fd4c1`, to `342068b5bec36888c16548f352d8ff29a0b9f946516942054c16941ce8359680`.

Therefore:

- `reduce.py` is the only checkpoint conversion that must revert.
- No other converted file is covered by the issued estimator-source pin.
- The AST exclusion needed by this rework is exactly `reduce.py@5118849d…`, not all four modules.
- The artifact separately pins protocol identity, but that is not another source-file entry.

## R2 — REJECT the arbitrary relocation table; adopt a content-addressed custody store

The table can be made safe, but it introduces an unnecessary selector. The ledger already contains the right selector: every finalization binds its original locator, unique `content_id`, and complete five-file artifact-hash vector into the receipt chain.

The issued prefix contains 76 receipts: 38 reservation/finalization pairs, 38 unique absolute locators, and 38 unique finalization content IDs. D-116 also explicitly locates integrity in the committed hash chain rather than the custody pointer ([decision](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/trust/docs/decision_log.md:7588)).

### Better design

> Add an optional production input `--calibration-custody-store ROOT`. When absent, custody resolution is exactly the current locator-based behavior, byte-for-byte.  
>  
> When present, every custody-bearing final observation resolves deterministically to `ROOT/<receipt.content_id>/`; there is no locator-to-path table and no fallback to the historical absolute locator. The original locator remains untouched in the authenticated receipt and continues to participate in its digest.  
>  
> Resolution MUST use no-follow, contained directory/file reads and authenticate every governed artifact against the receipt’s exact `artifact_sha256` map. A missing content directory, missing artifact, symlink, non-regular file, hash mismatch, null content ID, duplicate content identity, or mixed legacy/store resolution refuses with the existing custody-invalid domain. Extra store entries are never read or registered.  
>  
> A canonical strict-JSON store manifest SHALL declare the ledger schema/head and the exact content-ID/full-hash projection expected from the authenticated snapshot. The loader MUST prove exact equality with the ledger-derived projection; the manifest never supplies content identities or hashes. Its exact SHA is registered and carried through `CalibrationLedgerSnapshot` into mint provenance and post-bind validation.

This eliminates duplicate targets, partial mapping, locator normalization, and arbitrary destination selection by construction. The fixture becomes 38 deterministic content-ID directories containing the five issued artifacts each.

### If a relocation table is retained anyway

Its minimum validation contract is:

- Strict JSON registration, not `raw`; exact bytes are hashed, but JSON suffix/type cannot be downgraded.
- An expected table SHA supplied through the production input contract.
- Closed schema with ledger schema, head sequence, and head digest; all must equal the authenticated snapshot.
- Exact locator keys as receipt strings—no normalization before identity matching.
- Exact set equality with every distinct locator dereferenced by that snapshot: no missing keys, extras, subset mode, or fallback.
- Relative targets beneath one declared root only; reject absolute targets, `..`, dot components, NULs, symlinks, and non-directories.
- Reject duplicate canonical targets unconditionally. Although differing receipt hashes would normally expose the collision, injectivity avoids collapsing custody instances and makes fixture completeness mechanical.
- Each row must declare the receipt content ID and full artifact-hash projection, both exactly equal to the ledger; the ledger remains senior.
- Every governed member must be opened no-follow, registered at the exact read, and digest-checked.
- The table must be loaded and registered before the first relocated resolution and reverified before output.
- Active relocation must be all-or-nothing. An absent table alone selects legacy behavior.
- The table SHA/mode must be carried in `CalibrationLedgerSnapshot`, emitted in final artifact provenance, and compared during post-bind validation.

Mapping into the repository is not itself content substitution—the issued hashes still govern—but it creates mutation and Git-gate masking risks. The decisive attack fixture should copy mutable custody outside the clean worktree so custody-domain refusals are actually reached.

Disclosure alone is insufficient. The upstream whole-window verdict should not become host-storage-dependent, but the mint’s evidence-binding/post-bind side must verify that its relocation/store provenance equals the authenticated ledger snapshot. Otherwise the output can disclose a hash without proving that hash governed the consumed snapshot.

A production CLI table/store argument does count as “unpatched” provided it is documented production behavior, uses the ordinary custody loader with every check still enabled, has byte-identical absent behavior, and has no test-only branch. “Unpatched” forbids monkeypatching or authority substitution; it does not forbid declared authenticated inputs.

## Sequencing ruling

One resumed session can complete the work, but the dependency order is mandatory:

1. Revert `reduce.py` and prove SHA `5118849d…`.
2. Implement the v2 path-capability exception, exact SHA/callsite guard, ABA regression, and focused pin tests.
3. Implement and test the content-addressed custody resolver and its absent-mode parity.
4. Freeze the store/manifest schema, then assemble and verify the 38-member fixture.
5. Prove one authentic production-CLI mint and production open/registry equality.
6. Replace the decisive regression wholesale; then add shadow-removal attack legs and the per-domain mutation matrix.
7. Run the two v1 byte-parity tests, focused suites, `git diff --check`, and the full unpiped suite last.

These should be separate reviewable commits—trust mechanics first, fixture/regression second—but do not require separate implementation sessions or an intervening merge.

Checks performed: `git status`, checkpoint `97fd4c1` diff/stat and targeted source diffs, adopted consult and blocked report, D-079/D-116 authority, issued artifact/code pin comparison, exact SHA-256 recomputation, 76-row ledger/custody-manifest census, and relevant reducer/ledger/session call paths; no files changed and no test suite run.