# BY-INT — BYTES pass-1 integration

## SUMMARY

Integration in progress on `lane/2026-10-22-bytes-pass1`.
Verified B2 base `0743a7b90c70f896f0cf82551d4e2ac33b9b1f02`.
B4 is merged first, preserving NR1 and Q1/Q2.
Only synthetic fixtures are authorized; every run sets `JW_B5_SYNTHETIC_ONLY=1`.
No measurement window, launch job, production pack state, or main push is authorized.

## MERGES

1. B4 `0b6023dcc`: `e564d4db75137f307ee726f7d8f92dd7916e6bb9`. Conflict: `tests/fixtures/bytes/campaign.py`, two hunks. Combined B2's fixture defaults and synthetic-parameter manifest (unequal durations, signed clock latency, 50 ms sample phase, independent random edge phase, 10 ms minimum arrival latency, reference drift) with B4's `subpack_sessions` / `uncollected_sessions` and configuration keys. Governing: Addendum 7 item 12 and Addendum 8 item 4 (`docs/design/bytes_pack_design.md` at `298a292a7`); `docs/process_traces/2026-10-21-magistrate-a017b694/B2-NR1-RULING.md` items 1, 3, 5; `docs/process_traces/2026-10-21-magistrate-283e9802/B2-NR1-COLD-DISPOSITION.md` M1; `docs/process_traces/2026-10-20-magistrate-af419b16/B6-RULING.md` Q1 and Q2; `docs/process_traces/2026-10-20-magistrate-4b350f47/RECORD.md` blinding ruling items 1–3. Other paths merged automatically; generated drafts came from the B4 generator output.
2. B3 `0c04bb181`: resulting head `990763f02e021e28bbae6d7b5d78fd71d4374e0d`; no conflicts.
3. H `c10b6895f` exactly (including B5 `20e6984c9`): resulting head `33fda48b643b82b6d2aab0e573a36c1af18d4897`; no conflicts. Later H branch commits were excluded.
4. Manifest/KV `99c9099d8`: resulting head `4f6237d46d7ed8bd87e1f50e2a4b4d961c18492e`; no conflicts.
5. Registration `91b20d7c2`: resulting head `e7ffa7c8c1e55b18e6dd9bb48035b416979e75ca`; no conflicts. Twelve registrations auto-merged B4 flag effects with registration-lane estimators and notes.
6. Regeneration: `scripts/bytes_plan_trees.py` produced no tracked differences. `--check` and `scripts/bytes_mac_kit.py --check` pass. `scripts/build_b6_flag_catalog.py --check` exits 1: inherited B4 catalog entries are absent from its builder. Exact-file scope expansion requested; builder untouched pending reply.
7. `origin/main` at `ef520743cec50833a8ee6af37388610bef22798e`: resulting head `5f89a9e0051b64f74454a193f9f3e9f20db7d65a`; no conflicts. Auto-merges in `configs/gates/hazard_refusals.json`, `tests/test_b5_plan.py`, and `tests/test_night_agent_install.py` required no manual changes.

## GENERATED

Commands (all with `JW_B5_SYNTHETIC_ONLY=1` and `/opt/homebrew/bin/python3.13 -B`):

- `/workspace/JouleWise/scripts/bytes_plan_trees.py`: exit 0; no tracked differences.
- `/workspace/JouleWise/scripts/bytes_plan_trees.py --check`: exit 0.
- `/workspace/JouleWise/scripts/bytes_plan_trees.py --output-root /tmp/by-int/regenerated`: exit 0; all 39 emitted files equal both the generator bytes and checkout bytes (12 plan trees, 12 registrations, 12 collection plans, smoke keep, loop, pass order).
- `/workspace/JouleWise/scripts/bytes_mac_kit.py --check`: exit 0.
- `/workspace/JouleWise/scripts/build_b6_flag_catalog.py --check`: exit 1, inherited three-code builder omission. Scope request pending; repository builder unchanged.

Per-file generator hashes: `/tmp/by-int/generated.json`, SHA-256 `38f9e6a9c7f4963ce123b5661cbd8e127949a6e30a9931a465b8472016bd9923`.

## B4 OPEN ITEMS

- Added `Q2CommitmentCLIChainTests.test_changed_module_evaluates_original_commitment_and_labels_rebuild` to `tests/test_bytes_analysis.py`. It runs CLI processes for comment-only provenance and a deliberately defective central fit line, then checks C1 evaluated as committed, C2 separately, immutable prediction bytes, module digests, exact field lists, and both disclose-only flags. No new comparison bar.
- Before: test replay with `scripts/bytes_analyze.py` from `c2dad351e` and the integrated arithmetic/fixture: 1 test, 2 failing subtests, exit 1 (`frozen line/fit-point mismatch`). After: integrated CLI, 1 test, both cases pass, exit 0, 26.999 s. Logs `/tmp/by-int/q2-before.log` and `/tmp/by-int/q2-after.log`.
- Catalog SHA filled in Appendix A: `4cd222c4fd7cc43e1e2625f9afae6f6cc742b40876241fb5cc5864d8ee7eaa4f`.
- README: both passes now say 1/1, with optional pass 2 governed by the analysis (Addendum 6).
- Inherited builder mismatch remains pending the exact-file scope grant for `scripts/build_b6_flag_catalog.py`. An in-memory addition of precisely the existing three entries makes its output byte-identical to the catalog; no catalog value needs changing.

## TESTS RUN

Seat setup ran; zsh 5.9 and Python 3.13.5. Its `/opt/homebrew` mkdir lacked Unix ownership. Created only the requested Python symlink through the managed local Docker daemon, mounted only `/opt`; `/opt/homebrew/bin/python3.13 --version` succeeds. No test run yet.

## END-TO-END

- Retained production-shaped synthetic CLI chain: `/tmp/by-int/e2e.py`; 12 R6 sub-pack sessions, 1,000 science runs (10 models × 2 passes × 50), 156 references (13 × 12), 456 clock-free visible rows and 700 withheld rows. CLI exits: blinded 0; unreleased fit 1; fit 0; blinded post-commit 0; held-out with fit-only keys 1; released held-out 0. `h1.json`: 360 rows; `h2.json`: 12 groups; `unavailable.json`: empty. Commitment unchanged, SHA-256 `f6cf713c6683ba083161510edc6532dfe83182496dd808db69e77ca499b51fd6`. This supplemental fixture passes the integration SHA as the synthetic post-commit locator; the repository subset-release tests exercise an actual separately committed prediction directory. The supplemental summary initially used the wrong flat export locator, then was read back from the retained per-subpack directories; all CLI expectations had already passed. Summary `/tmp/by-int/e2e/summary.json`, SHA-256 `6fd36ff91d7597c9e5eaf396ef28e97f25bc79a721e07dd1714e876cb08d772f`.
- `open_packs`: scratch clone `/tmp/by-int/open-packs` at `5f89a9e0051b64f74454a193f9f3e9f20db7d65a`; real subprocess Git runner, no live state. Opened exactly alpha, beta and gamma; all twelve BYTES packs rejected only as draft. Every registration and loop hash unchanged. Before = after: alpha `3a999f88068ded30398575816fc45040541597ea283415ec307b11f0cc1dee0d`; beta `1cdb1026b4e4db28757980d26ff01faa95752862d5088fd2f9704d9a33ab76e3`; gamma `722ddf2bab8d4f143f8520f6e6d401af533ffa6560dfe60c8827dc2c3ca05563`; loop `5f120d7310b7240a81d5e12927e082112555950a2a8879ffadeabc7a6c7f370f`.
- `JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census`: exit 0; `unlisted`, `stale`, `miscounted`, `guard_changed`, `scope_gaps` all `[]`.

## CI

Draft PR #535, https://github.com/mpmdw/JouleWise/pull/535, against main; gate-ledger intentionally NOT-RUN pending lead gates.

## DECISIONS I MADE

- Combined orthogonal fixture controls; kept B2's ruled stress settings instead of B4's older equal-duration defaults.
- Preserve C_j as pass-averaged joules divided by mean decode time (M1); Q1 missing-file pass flags and survivor fallback; Q2 fixed-module evaluation of committed content with disclose-only provenance flags.
- User write scope overrides repository end-of-work bookkeeping and whole-suite instructions. No unrelated files will be edited and no full suite will run locally.

## OPEN ISSUES

Remaining integration steps and acceptance checks are in progress.

## NEEDS_RULING

none
