FINAL PASS: PASS

Cold final pass on PR #470, `git diff 8fa002f7..2a682b2e` (2 commits, `joulewise/window_duration_margins.py` +91, `tests/test_window_duration_margins.py` +170).
Reviewer: Fable 5.1, 2026-10-04. Scratch: `/tmp/dd5-fable-rc/`. Checkout left clean (`git status --short` empty at end).

No BLOCKER or MAJOR finding. One MINOR (stale line citations outside the diff) and four NITs. Nothing below blocks merge.

## What I ran

| Check | Result |
|---|---|
| `pytest tests/test_window_duration_margins.py tests/test_custody_mode_inventory.py` at `2a682b2e` | 49 passed, 37 subtests passed (280.8 s) |
| New path resolver on the three frozen packs (`probe_packs.py`) | 320 member references, 240 distinct source configs; every source hashes to its pin; every `config.run_id` equals its bundle id; all `repetitions == 1`; 0 unknown-key warnings; 0 pairs normalizing to the same run hash |
| Current `_config_sha256(from_mapping(source))` vs real runner-written `config.json` (`src_vs_run.py`) | 174 of 174 real bundles match (`runs_window_contrast_20260730` 47, `runs_window_7bfloor_20260729` 57, `runs_window_metrologyB_20260801` 70); source bytes equal run bytes in 0 of 174 |
| Round trip of real `config.json` through current `from_mapping` → `to_dict` (`roundtrip.py`) | 198 of 198 reproduce their own bytes, and `metadata.config_sha256` binds in 198 of 198 (adds 24 bundles from the 10-04 g2a harvest) |
| 12 targeted mutants in a scratch copy (`mutate.py`) | 12 of 12 killed |
| Path resolver vs symlink/escape inputs (`escape.py`) | out-of-root symlink, symlinked directory, `..`, absolute path, empty, non-string all refuse `pack_pin_invalid` |
| Plan tree swapped (with sidecar rewritten) between the two reads (`treeswap.py`) | refuses both inside and outside a read session |

## Question 1 — is anything admitted that a sound reading refuses?

No. The chain at `window_duration_margins.py:602-641` is three hash equalities plus the pre-existing run-id check at :647:

1. sha256(source file bytes) == registry pin (:613)
2. sha256(`<run>/config.json`) == runner-normalized hash of the parsed source (:618-631)
3. `metadata.json` `config_sha256` == sha256(`<run>/config.json`) (:633-641)

Case by case:

- **Source path outside pack or repository; symlinks.** `_safe_relative_path` (:202-211) resolves symlinks and requires the result under the governing root. Probe output: `sub/link_out.json -> REFUSE`, `dirlink/outside.json -> REFUSE`, `../outside.json -> REFUSE`, absolute `-> REFUSE`. An in-root symlink to an in-root file is admitted, which is harmless: step 1 pins content, so the path is only a locator and cannot substitute different bytes.
- **Plan tree changed between reads.** Refused twice over. Inside the session (the only production path, `derive_window_duration_margins` :1025) the session's first-digest registry refuses first: `in-session: REFUSE authoritative_input_invalid | ... v2_authentication_input_changed`. Without a session the explicit check at :515-516 refuses: `sessionless: REFUSE pack_pin_invalid | plan_tree.json changed after authentication`.
- **GAMMA versus floor source roots.** Root selection at :528-532 uses the same predicate as `_pack_inventory` :396, on bytes proven equal to the authenticated tree. On the real packs, floor paths resolve repository-relative and GAMMA paths pack-relative, with all pins matching. Forcing either root for both pack kinds is killed by tests (mutants M6, M7).
- **Metadata mismatch.** Missing, wrong, and pin-valued `config_sha256` all refuse (:635). Mutants M4 (check dropped) and M4b (pin also accepted) are killed.
- **Science-row agreement.** A registered member needs exactly one science row whose `config_sha256` equals the registry pin (:540), and every registered member must be covered (:548). Mutants M8, M9, M10 killed.
- **Two source configs that normalize to the same run bytes.** Admitted by construction, and I judge that sound. The file on disk must still be byte-identical to the pinned source (step 1). What cannot be distinguished is a run launched from a different file that parses to the same `BenchmarkConfig`. The runner only ever holds the parsed config: `cli.py:292` parses, `controller.py:302-304` (`_prepare_suite_manifest_for_new_bundle`, :717-769) returns `config` unchanged on every path, and `controller.py:333` hands it to the writer. Two such sources are the same experiment. `run_id` is inside the normalized bytes and :647 requires it to equal the bundle id, so two different members can never collide (0 collisions across the frozen packs).

## Question 2 — is `_config_sha256` exactly the writer's serialization?

Yes. `controller.py:3394-3397` and `bundle.py:950-954` are the same expression: `json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"`, UTF-8, sha256. The campaign runner launches the source path directly (`scripts/run_campaign.py:1536`, `run <config_path> --runs-dir`), with no intermediate rewrite.

Drift evidence against real output: 174 of 174 July–August bundles equal the current-code normalization of their in-repo source config, so no default-filling drift has accumulated across roughly two months of schema changes. The same 174 show the old comparison could never pass (0 byte-equal), confirming the defect this change fixes.

Two limits on that evidence, stated plainly:

- I found no on-disk bundles for the three frozen d117 packs (searched `/Users/edr/code/JouleWise` and `/Users/edr/night-archive` to depth 4), so no real member of those packs has been run through the new code end to end. The evidence is the 174 older real bundles plus fixture bundles written by the real `RunBundleWriter`.
- `repetitions > 1` members get a rewritten `run_id` (`controller.py:2983`) and would refuse under step 2. All frozen-pack members have `repetitions == 1`, so this does not arise today; it fails closed if it ever does.

## Question 3 — do the tests kill what they claim?

Yes. Each mutant was applied to a scratch copy of the module and run against the seven new tests:

| Mutant | Killed by |
|---|---|
| M1 old byte comparison (run bytes vs pin) | `test_gamma_pack_relative_sources_authenticate_runner_serialization` (first failure; the run stopped there with `-x`) |
| M2 source-pin check dropped | `test_source_config_bytes_must_match_pack_pin` |
| M3 normalized run-config check dropped | `test_nondefault_run_config_refuses_even_with_metadata_hash_rebound` |
| M11 normalized hash computed from the run config instead of the source | same test as M3 |
| M4 metadata binding dropped; M4b pin also accepted | `test_metadata_config_hash_must_bind_runner_bytes` |
| M5 tree_sha binding dropped | `test_frozen_pack_pins_authenticate_source_not_runner_bytes` |
| M6 / M7 source root forced to repository / pack | GAMMA test / floor tests |
| M8 / M9 / M10 science pin, duplicate row, coverage | `test_science_inventory_must_bind_unique_registered_source_paths` |

The fixture change matters: `_write_bundle` now creates bundles with the real `RunBundleWriter` (test file :555-558), so the PASS-path tests exercise true runner bytes rather than a hand-written `config.json`. `test_frozen_pack_pins...` also asserts writer bytes equal `_config_sha256` on a real pack config, which guards future divergence between `bundle.py` and `controller.py`.

## Findings

**MINOR — stale line citations in a paper-facing artifact (outside the diff; follow-up, not a merge blocker).**
`scripts/paper_prefill_resolvability_projection.py:58` and `:733` cite `joulewise/window_duration_margins.py:801-803` and `:1091-1093` for the sample-count-margin field. The same strings are committed in `docs/paper/round7/prefill-resolvability-projection.json:19358` and `.md:86,88`. They were already off by one at the parent (the code sat at 802-804 and 1093). After this change the code is at `:885-887` and `:1180`, and line 801 is now an unrelated `consumption_semantics_id=` argument. Evidence: `sed -n '801,803p'` at HEAD, and `grep -n '"sample_count_margin": ('` → 885. Fix by citing the symbol (`_member_row`, `validate_window_duration_margins_receipt`) instead of line numbers.

**NIT — tree-binding test covers only the explicit check.**
`test_frozen_pack_pins...` passes a wrong digest (`"0" * 64`) rather than changing the file between reads. That kills removal of :515 (M5), which is what the second commit added. In production the session registry already refuses a changed tree before :515 is reached, so the explicit check is defence in depth for sessionless callers. No action needed; recorded so the redundancy is not later mistaken for the sole guard.

**NIT — unreachable check.**
`window_duration_margins.py:1038-1043` ("pack registries disagree on config sha256") can no longer fire: `_member_input_paths` :521-527 refuses the same condition first, with the same reason code. Harmless dead code.

**NIT — one reason code for four causes.**
`member_config_mismatch` now covers unreadable config, source-pin mismatch, invalid source, normalized mismatch, metadata mismatch, and run-id mismatch. Tests assert the reason code only. The mutants show each cause is still individually killed, so coverage is real; only operator diagnosis relies on the detail string.

**NIT — exception net around the source parse (not verified to be reachable).**
`:622` catches `SchemaError`, `ValueError`, `TypeError`. If `BenchmarkConfig.from_mapping` could raise anything else on a pinned source, it would surface as a traceback rather than a structured refusal. Either way no receipt is written, so this is fail-closed. I did not find an input that triggers it; all 240 frozen sources parse cleanly.

## Ruling

Merge. The change replaces a comparison that could never succeed (0 of 174 real bundles byte-equal to their source) with a transitive chain of exact hash equalities, each link individually tested, and it admits nothing the pinned source does not determine.
