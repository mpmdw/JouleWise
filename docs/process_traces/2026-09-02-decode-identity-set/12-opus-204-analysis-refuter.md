# 204 — Opus refuter, analysis-path / consumer lens (R-6(a))

Worktree `/Users/edr/code/JouleWise-wt-decode-id3` @ 1a608089; line numbers post-cure (`d0e59351`). **No BLOCKER.** Every failure path I probed is fail-closed, and the committed v3 path is provably unchanged.

## Findings

- **F1 — MATERIAL — `joulewise/analysis_engine/inputs.py:3886-3888`.** The declared set is rooted in `pack_root/plan_tree.json`, read by path with **no digest check inside the gate**: a self-consistent forgery (swapped `config_inventory`, recomputed `config_set_sha256`, re-rendered + re-sidecarred the projection receipt, the freeze receipt, and both `plan_tree` refs) made the gate return the *prefill* unit's set `365b4a41…` instead of the honest decode `604f6e22…`. *Fix:* re-verify the pack inside the gate — the lineage dict already carries `pack_sha256` (`arm_readiness.py:10371`) — or thread the authenticated `plan_tree_sha256` in.
- **F2 — MATERIAL — `inputs.py:4081`, `:4122`.** The fail-closed `if matches or same_condition_seen: return None` guard now sits *inside* the `consumer_identity is not None` block, so a multi-identity `_v5` decode unit whose family has a same-condition exact cell silently takes a transported floor where the old code refused. *Fix:* keep the `same_condition_seen` scan and its refusal unconditional; gate only the per-cell identity comparison on single-identity.
- **F3 — MATERIAL — `tests/test_analysis_inputs.py:438`, `:453`.** The only `floor_request_for_evidence` test **mocks** `_frozen_consumer_identity_set`; nothing runs gate + caller together, and the gate's negative paths (absent/tampered receipt, `config_set_sha256` mismatch, legacy multi-identity refusal at `inputs.py:4065`) have zero coverage — gutting the gate body to `return frozenset()` leaves that test green. *Fix:* add a tampered-pack test asserting `floor_request_for_evidence` returns `None`, plus a multi-identity-without-lineage test.
- **F4 — NIT — `inputs.py:3877-3882`.** `pack_roots` silently *drops* rows whose lineage mapping lacks a `pack_root` string, adopting them into another row's pack. *Fix:* require every authenticated row to carry the same non-empty `pack_root`.
- **F5 — NIT — `inputs.py:4051-4054`.** `scientific_config_identity(row.raw_config)` is computed, discarded, then recomputed inside `scientific_config_identity_sha256`. *Fix:* hash what's in hand.
- **F6 — NIT — `joulewise/analysis_engine/__init__.py:422-423`.** Any authentication failure collapses to `unavailable_floor_resolution`, indistinguishable from an ordinary no-match, so a broken receipt chain reads as "no floor". *Fix:* emit a distinct reason code.

*Out of scope:* at 06:24:53, mid-session, another seat left an uncommitted `# MUTANT M4` edit in `joulewise/identity_pins.py:1617-1620` in this shared worktree (since reverted). It postdates all my runs (mtime-verified) and does not touch the consumer gate. I did not touch it.

## Answers

**1. Call path / weakest hop.** `BundleEvidence.launch_lineage` (set at `inputs.py:2771` from `authenticate_bundle_launch_lineage`) → `row["pack_root"]` (`:3878`) → `pack_root/plan_tree.json` (`:3886`) → `identity_pin_projection` must be `frozen` (`:3892-3896`) and `arm_readiness.freeze_receipt` `{path,sha256}` (`:3897-3902`) → freeze receipt bytes, digest **and** GNU sidecar checked (`:3903-3925`), `status == PASS` (`:3930`) → its single `identity_pin_projection_receipt.v1` item, required to be `u11-freeze-projection`/`PACK`/`PASS` **and** to equal `projection["projection_receipt"]` (`:3943-3951`) → projection receipt bytes, digest + sidecar checked (`:3952-3977`) → the unique unit whose `consumer_bindings[].family` matches (`:3980-3990`) → every `config_inventory` row digest-checked (`:3993-4006`) → recomputed set must equal `config_set_sha256` (`:4007-4012`). Everything from the freeze receipt down is authenticated. Two hops are not: `pack_root` (a bare string off the lineage dict) and `plan_tree.json` (path read, no digest). **`plan_tree.json` is the weakest hop** — root of trust for the whole chain, and F1 shows a forged chain passing it. It is redeemed only *non-locally*: `authenticate_launch_lineage` → `_replay_consumed_arm` recomputes `_pack_record` (`arm_readiness.py:5242-5264`, including `plan_tree_sha256` over the on-disk bytes) and compares every key against the armed record (`:7045-7050`), so a tampered `plan_tree` makes the *bundle* refuse at load and the row never reaches the gate. The gate neither restates nor re-checks that invariant. Third, softer hop: the unit is chosen by **family-id string match** only, and family ids are not pack-unique — floor pack `d117_floor_qwen25_1p5b_v3` declares consumer family `sw-decode-a-qwen25-1p5b`, the same string the contrast pack uses — so the lookup's correctness rests entirely on `pack_root` being the evidence's own pack.

**2. Absent / unreadable / old-code receipt.** It refuses; it never degrades. Fifteen distinct failure sites return `frozenset()` (`:3883` … `:4012`) plus the catch-all `except (AnalysisInputError, ArmReadinessError, IdentityPinProjectionError, KeyError, OSError, TypeError, ValueError)` at `:4013-4022`, and the caller converts a non-`None` empty set into a refusal at `:4060-4064`. Measured on a copied v3 pack: receipt absent, freeze receipt absent, tampered sidecar, `state→draft`, bogus freeze sha, and a duplicated unit family all returned `frozenset() REFUSE`. Old receipts: the gate never reads `suite_manifest_set`; it re-derives the set from `config_inventory` and checks it against `config_set_sha256`. R-5 keeps the one-identity digest byte-identical, so every pre-cure single-identity receipt still authenticates (18/18 committed d117 units). A pre-cure *multi-identity* receipt would fail the set digest and refuse — and none can exist, since the old declaration-equality check refused to freeze such a unit. Note the gate trusts the freeze-time R-3/R-4 checks rather than re-checking the declaration.

**3. Cross-unit binding.** No, not for `_v5` A vs B. `decode_suite_manifest(arm, i)` embeds `condition_id: family_id("decode", arm)` and `CHAT_TEMPLATE_SHA256[arm]` (`configs/campaigns/d117_contrast_v5/generate_configs.py:1447-1457`), so **A and B share no manifest sha**, and `scientific_config_identity` also carries model/revision — the declared sets are disjoint. The subset check is sufficient rather than accidentally safe, because (i) `pack_root` comes from the row's own authenticated lineage and must be unique across rows (`:3877-3882`), (ii) `_require_common_launch_lineage` (`:3038-3068`, called at `:3223`) already forces one launch for the whole corpus, and (iii) an identity *is* the config content, so membership means the row ran that declared config. A unit-id / plan-reference cross-check would be belt-and-braces, not a fix. Residual: the gate does not require the evidence to cover the declared census — left to the manifest's per-entry `config_sha256` binding, and R-6(a) ruled "non-empty subset", so this is ruled-compliant.

**4. Exact-cell route.** Confirmed single-identity-only. `consumer_identity` is `None` whenever `len(consumer_identities) > 1` (`:4076-4080`), and the whole exact-cell scan, match and `FloorRequest` return sit inside `if consumer_identity is not None:` (`:4081-4123`). No other branch reaches it — the only other `FloorRequest` construction is the transport return at `:4152-4163`, which never consults an identity. Caveat: the `same_condition_seen` refusal was swept inside the same guard (F2). Also confirmed benign: `_consumer_stress_for_evidence` (`:988-1080`) reduces with `min`/`max` only, so a heterogeneous prompt mixture *widens* the envelope and makes transport stricter — no understatement path.

**5. Tests.** `test_u8_freeze_receipt_reaches_committed_v3_member_identity_set` (`:340-367`) runs the **real** `_frozen_consumer_identity_set` against the **real committed pack** `d117_floor_qwen25_1p5b_v3`, so the chain, sidecars and set digest are genuinely exercised — but the row is hand-built as `launch_lineage={"pack_root": str(pack)}` (`:353`), a shape the test invents (it would still pass if production stopped putting `pack_root` at that level), and `expected` is recomputed with the same `scientific_config_identity_sha256`, so the *chain* is pinned, not the value. `test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell` (`:369-459`) tests the real `floor_request_for_evidence` but **mocks** the gate at `:438`/`:453`; gutting the gate body leaves it green (only test 1 fails). Deleting the function makes `mock.patch` raise, so a fake cannot survive deletion — but it survives evisceration, which is the mutation that matters (F3).

**6. Effect on the committed v3 corpora — provably none.** (a) The hash changed name, not bytes: the removed inline `sha256(json.dumps(identity, sort_keys=True, separators=(",",":"), allow_nan=False))` and `scientific_config_identity_sha256` (`identity_pins.py:240-244`) agree on 6/6 sampled v3 decode configs. (b) `identity_unit_config_set_sha256` returns the lone member hash for a one-identity unit (`identity_pins.py:255-256`), so all four v3 contrast units and all six v3 floor units recompute their stored `config_set_sha256` from their own `config_inventory` with zero digest mismatches. (c) Running the real gate over every committed d117 pack (v1/v2/v3 contrast, both v3 floor packs): **18/18 units resolve to exactly one identity**, so the new subset test at `:4060-4064` reduces to the old `len(consumer_identities) != 1` test and `consumer_identity` stays non-`None` — the exact-cell block runs verbatim. The only way to lose a previously-binding row is a gate refusal, and no committed pack refuses. Campaigns with no `plan_tree.json` (`neg8_reference_corpus`, `p2_015_*`, `metrology_v1`, `splitwise_decode_v1`, `window_references`) cannot carry `launch_lineage_required` lineage and take the `return None` legacy branch (`:3874`), untouched.

## Commands run (verbatim tails)

```
$ python3 -m unittest tests.test_analysis_inputs -v   -> Ran 7 tests in 0.022s / OK
$ python3 -m unittest tests.test_identity_pins        -> Ran 38 tests in 6.373s / OK
$ python3 -m unittest tests.test_analysis_integration.AnalysisIntegrationTests.\
      test_production_request_factory_reaches_predeclared_transport -> Ran 1 test in 0.612s / OK
$ grep -rho '"condition_family_id": *"[^"]*"' scripts/floor_mint_pinsets | sort -u
"condition_family_id": "df-ph-decode"
$ python3  # real gate vs every committed d117 pack (scratch probe)
d117_contrast_qwen25_1p5b_vs_7b_v1  sw-decode-a-qwen25-1p5b  -> 1   [16 further rows, all -> 1]
d117_floor_qwen25_7b_v3             sw-prefill-p256-b-qwen25-7b -> 1
$ python3  # fail-closed probes on a copied v3 pack
baseline copy                       -> ['604f6e2210e8e7a9ed60b33dd425d4271f3ca0e14b13f521511052efaa1de313']
projection receipt ABSENT           -> frozenset() REFUSE
freeze receipt ABSENT               -> frozenset() REFUSE
projection sidecar TAMPERED         -> frozenset() REFUSE
plan_tree state->draft (no sidecar) -> frozenset() REFUSE
plan_tree freeze sha BOGUS          -> frozenset() REFUSE
receipt unit family DUPLICATED      -> frozenset() REFUSE
restored                            -> ['604f6e2210e8e7a9ed60b33dd425d4271f3ca0e14b13f521511052efaa1de313']
$ python3  # F1 forgery + control, v3 digest reproduction, hash equivalence
FORGED CONSISTENT CHAIN -> ['365b4a419e1b804ce7032d38ef31a66baae7ff87475a7185d693d8286bfe5234']
expected honest set     -> 604f6e22...
inventory swapped, config_set_sha256 NOT recomputed -> frozenset() REFUSE
sw-decode-a-qwen25-1p5b n_ids 1 digest_ok True sha_bad 0   (+3 further v3 units, all True/0)
configs 6 legacy==new 6
```

same_signature: n/a (first round)
