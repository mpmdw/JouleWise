# Opus 5 counter-review (operation-loop §5 row 6) of the near-final head `7e888d82` — custodied verbatim (scratchpad paths redacted)

Lens: contract + integration, read-only, detached copy at `7e888d82`. Brief: the magistrate's Agent prompt (items 1–5). Disposition: file 29/30.

---

All checks complete. Here is my counter-review.

---

# Opus 5 counter-review — `fix/2026-09-02-decode-identity-set` @ `7e888d82`
**Lens: contract + integration** (operation-loop §5 row 6). Read-only; nothing modified in any checkout.

## Contamination disclosure

My context was auto-loaded, before I saw the branch, with:

- `/Users/edr/.claude/CLAUDE.md` (global writing standard + orchestration pointers)
- `/Users/edr/code/JouleWise/CLAUDE.md` (project bridge/delegation policy)
- **`/Users/edr/code/JouleWise/CLAUDE.local.md`** — the full private orchestration doctrine (hard rules 1–11, magistrate/lieutenant/cold-gate topology)
- `~/.claude/projects/-Users-edr-code-JouleWise/memory/MEMORY.md` — ~45 memory entries including `ruled-not-installed-pattern`, `packet-facts-bench-verified`, `mutation-cure-counterfactual-rule`, `docs-are-context-code-is-truth`

This is not a cold seat. Two concrete effects I can name: the `ruled-not-installed-pattern` memory primed me to diff ruling clauses against code line-by-line (which produced finding **S2**), and the global writing standard's first-use test primed the contract-prose reading (**S1**). Everything below is cited to branch primary evidence and was executed this session; I did not carry any verdict from the lane's own trace files.

I also **did not reproduce** the lane's claims from files 25/26/27 — I read file 27 only to learn what the lane already dispositioned, so I would not re-report it.

---

## Findings

### BLOCKER — none

I looked specifically for: a path that admits an undeclared consumer identity; a reason code that crashes a downstream validator; a frozen byte that moved. None found. `ordered_reason_codes` (`joulewise/analysis_engine/claims.py:224-225`) **raises** `ValueError` on unregistered codes, but neither new code can reach it — the total `else` at `joulewise/analysis_engine/__init__.py:221-222` translates them to `floor_transport_inapplicable` first. The `TRANSPORT_REASON_CODES` census (`joulewise/detection_floor.py:307-308`) and its closed-set test (`tests/test_detection_floor.py:3712-3713`) were both updated. R-9's registration digest is intact (pasted below). I did not manufacture a blocker to fill the tier.

---

### SHOULD-FIX 1 — the contract affirmatively denies a production check that exists and is tested

`docs/contracts/identity_pin_projection.md:481-486` states, verbatim:

> The identity projection authenticates the inventoried configuration bytes. It
> does not independently open the suite-manifest files to recompute their
> digests; manifest-file authentication remains with the pack and suite gates.
> Within this contract, an unauthenticated manifest binding means a configuration
> digest or reference not present as the exact declared pair, and that condition
> refuses in step 4.

The code does exactly what that paragraph denies. `joulewise/identity_pins.py:1612-1628`, inside `_derive_projection_units`, unconditionally opens every declared manifest file and recomputes its digest before the config loop runs:

```
1612            manifest_path = _declared_manifest_path(pack_root, manifest_ref)
1614                observed_manifest_sha = _sha256_bytes(manifest_path.read_bytes())
1621            if observed_manifest_sha != manifest_sha:
1624                    f"declared suite manifest is unauthenticated: {manifest_ref}",
```

The behaviour is deliberate and pinned by two tests (`tests/test_d117_contrast_v5_pack.py:1074` `test_generated_v5_pack_refuses_tampered_declared_manifest_bytes`, `:1105` the arm-verify sibling).

**How it got there:** `git log -S` shows the denial sentence landed in the original cure `d0e59351`, and fix round 1 `3ac6cffb` added the contradicting check. Nobody updated the paragraph. `grep` over the entire lane trace for `independently open|manifest-file authentication|_declared_manifest_path|declared suite manifest is unauthenticated` returns **zero hits** — no reviewer in three execution passes touched it.

**Failure scenario.** A freeze refuses with `readiness_identity_environment_dirty` / `declared suite manifest is unauthenticated: configs/campaigns/d117_contrast_v5/…`. The operator opens the ONE home for this gate, reads that manifest-file authentication "remains with the pack and suite gates," and debugs the wrong subsystem. Worse for replication: the contract's numbered freeze procedure (steps 1–6, `:456-479`) omits this check entirely, so anyone rebuilding the gate from the text — the stated bar — builds a gate that accepts a manifest file whose bytes were swapped after declaration.

**Why not a blocker:** the code is *stricter* than the contract, so nothing unsound is admitted. This is a false statement in a binding contract, not a hole.

---

### SHOULD-FIX 2 — ruling 171a R-2's explicit removal clause was not executed

`docs/process_traces/2026-09-02-decode-identity-set/06-ruling-171a.md:43-45` rules:

> The generator NEVER derives the declaration by reading emitted configs and never re-types it from `workload_for()`; `generate_configs.py:1334`'s hardcoded `DECODE_PROMPT_TOKENS["A"]` is removed with it.

The first half landed — `declared_identity_workload_profile` (`configs/campaigns/d117_contrast_v5/generate_configs.py:1494-1518`) no longer calls `workload_for()` on the decode branch. The second half did not. The literal survives at `configs/campaigns/d117_contrast_v5/generate_configs.py:1321`:

```
1321            "prompt_tokens": DECODE_PROMPT_TOKENS["A"],
```

and `workload_for("decode", …)` is still reachable at `configs/campaigns/d117_contrast_v5/generate_configs.py:1798`, which writes `plan_tree.json`'s `stack_scope.measurement_arms.decode.workload`.

**Failure scenario.** The `_v5` plan tree will describe the decode arm as having `prompt_tokens = <arm A's token count>` for both arms, and with no `suite_manifest_set` — i.e. the plan tree's own descriptive workload contradicts the rotating declaration this lane exists to install, and mis-states arm B. I confirmed there is **no production consumer** of `stack_scope[*].workload` (`grep -rn stack_scope --include="*.py"` finds only generators and `tests/test_d117_floor_qwen25_7b_plan.py:1141`), which is why it is not a blocker. But this is the `ruled-not-installed` pattern precisely: a ruling clause with an implementation instruction that never reached code, and the `_v5` pack is still draft, so it is cheap to fix now and expensive after freeze.

---

### SHOULD-FIX 3 — the new gate binds floor resolution to an absolute path recorded on the arming machine

`joulewise/analysis_engine/inputs.py:3897`:

```
3897        pack_root = Path(next(iter(pack_roots))).resolve(strict=True)
```

`pack_roots` comes from the bundle's launch lineage, and `joulewise/arm_readiness.py:5257` records it as `str(pack_root.resolve())` — a **machine-absolute** path. `resolve(strict=True)` raises `OSError` when that path does not exist, and `OSError` is inside the function's catch-all (`inputs.py:4034-4042`), so the result is `frozenset()` → `("consumer_identity_set_unauthenticated",)`.

The codebase already treats this field as non-portable **elsewhere**: `joulewise/arm_readiness.py:7074-7094` defines `repository_relative_projection` specifically so two recorded `pack_root`s are compared by their repository-relative suffix, returning the detail code `repository_relative_location` (`:7104`). The new analysis gate uses the absolute string directly, with no such projection.

**Failure scenario.** A reviewer, CI job, or fresh clone re-runs analysis on a valid, byte-identical bundle from a checkout at a different filesystem path than the one that armed the launch. Step (2) of the eight-step gate cannot even be attempted; the floor is refused and the artifact reports `consumer_identity_set_unauthenticated` — a label whose contract meaning (`identity_pin_projection.md:605-630`) is "the frozen declaration could not be authenticated," sending the operator to hunt a forged pack when the pack merely moved. For a capstone whose claims must be reproducible from a clone, this is a reproducibility barrier wearing a forgery label.

**Distinct from the accepted residual.** File 27's accepted residual is a *test-coverage* gap ("a missing-root refusal test is a first-round item"). This is a production-semantics and label-fidelity point, and the existing `repository_relative_projection` precedent is the evidence that the codebase already decided absolute `pack_root` equality is the wrong comparison.

---

### NIT 1 — `floor_request_for_evidence` is now a public API function with zero production callers

The branch moved production from the public wrapper to the private `_floor_request_or_refusal` (`joulewise/analysis_engine/__init__.py:388`). Result: `floor_request_for_evidence` is defined at `joulewise/analysis_engine/inputs.py:4193`, exported in `inputs.__all__` at `:4555`, imported at `joulewise/analysis_engine/__init__.py:49` — and **never called**. I verified `grep -rn floor_request_for_evidence joulewise/ scripts/ configs/` returns only the definition, the `__all__` entry, and the dead import, and that `'floor_request_for_evidence' in joulewise.analysis_engine.__all__` is `False`. Production now reaches an underscore-private across a module boundary while the documented seam is dead. Consequence today is cosmetic (coverage is fine — the round-2 brief added production-seam tests alongside the wrapper tests).

### NIT 2 — the decision-log addendum cites the wrong ruling clause

`docs/decision_log.md:8462` says "several members use the **R-1** domain-separated set digest." The domain-separated set digest is ruled in **R-5** (`06-ruling-171a.md:61-68`); R-1 is "exact identities stay exact." A reader following the pointer finds no preimage. Harmless in practice because the preimage is fully specified at `identity_pin_projection.md:355-370`, but the decision log is the binding record.

### NIT 3 — identity refusal masks concurrent binding problems

`joulewise/analysis_engine/__init__.py:410` (`if request_refusal_reasons:`) takes precedence over `:425` (`elif request_factory is None and (…binding problems…)`). When a bundle has *both* an identity refusal and floor-binding problems, the artifact now reports only the identity code and drops `("artifact_schema_invalid", *binding_reasons)`. Diagnostic loss only — I verified both collapse to the same engine bucket `floor_transport_inapplicable` via `__init__.py:221-222`, so no claim-level output changes.

### NIT 4 — CI timing map is now materially stale for the two fattened modules

`.github/workflows/ci.yml:19-23` shards 4 ways by LPT packing over `scripts/test_timings.json`, pricing unmeasured modules at `unknown_module_weight_seconds = 29.834`. I verified `tests.test_analysis_inputs` and `tests.test_d117_contrast_v5_pack` are **both absent** from `seconds_by_module`, and that the branch does not touch the timings file — while adding +798 and +609 lines of pack-generating tests to exactly those two modules. Measured this session: `FrozenConsumerIdentitySetTests` alone is **33.5 s** on this M3 Max, against a 29.8 s price for the whole module. Not a failure (the `test` job has no `timeout-minutes`), only shard imbalance. A timing re-harvest is the cheap fix.

**Explicitly NOT a finding — one I checked and dropped.** The two new codes are absent from `docs/decision_log.md`. I checked whether the decision log's closed vocabularies cover them: `decision_log.md:3144-3195` is the *engine* set (`claims.REASON_CODES`), and `grep -n "transport_group_incomplete\|cadence_harder_than_calibration" docs/decision_log.md` returns **nothing** — the transport set's ONE home is `docs/specs/c027/p2-039_floor_artifact.md:605-630`, which *was* correctly updated and whose own rule (`:629-630`) says "Adding a reason is an additive schema-compatible change." No amendment is owed.

---

## R-1 … R-8 clause table

| Clause | Verdict | Production evidence | Notes |
|---|---|---|---|
| **R-1** exact identities not redefined; option (a-i)/(a′) rejected | **MET** | `scientific_config_identity_sha256` unchanged (`joulewise/identity_pins.py:236-244`); replacement matching untouched in diff | Negative clause; verified by absence from the diff |
| **R-2** generator declares closed set from the rotation rule, never folded, never re-typed from `workload_for()` | **MET in substance, one clause unexecuted** | `configs/campaigns/d117_contrast_v5/generate_configs.py:1479-1500` (`decode_declared_suite_manifest_set`, from `STAGE_SPECS` × `decode_prompt_index`), `:1502-1518` | See **S2**: `DECODE_PROMPT_TOKENS["A"]` at `:1321` not removed, still reachable at `:1798` |
| **R-3** (i)-(iv) freeze compares declaration to emission, fail-closed | **MET** | (i) `identity_pins.py:1636-1655`; (ii) `:1662-1673`; (iii) `:1682-1694` (`manifest_counts != declared_counts`); (iv) same + `:1662-1673` | Prefill single-member path preserved by the `elif` at `:1730` |
| **R-4** one identity per manifest class; #identities == #manifests | **MET** | `identity_pins.py:1695-1706` (`divergent_manifests`), `:1707-1719` (`_distinct_manifest_identity_refusal_reason`) | |
| **R-5** unit config-set digest, fixed domain string, no new key; representative triple replaced | **MET** | `identity_pins.py:247-258` (`identity_unit_config_set_sha256`), `:250` domain `joulewise.identity_unit_config_set.v1`; representative triple replaced at `:1832-1856`; `expected_config_sha` at `:1938` | S1 (set-iteration order) closed: `sorted(set(...))` at `:249`. Digest arithmetic verified live, below |
| **R-6(a)** consumer identities non-empty + SUBSET of frozen set; exact-cell stays single-identity | **MET** | `inputs.py:4082-4091` (subset gate), `:4127-4133` (`consumer_identity is None` skips exact-cell) | |
| **R-6(b)** floor sites NOT changed; single-identity digest pinned byte-identical | **MET** | `mint_floor_artifact*.py` absent from the diff; `detection_floor.py` diff is the 2-line reason census only | Pin test **executed, passed** (below) |
| **R-7** D-131 cl.2 replacement text + cl.3 rider | **MET** | `docs/decision_log.md:8438-8463`, quoted verbatim vs ruling `06:86-105`; S3 `prefill_p256`→`p<N>` propagated to `docs/phase_2/gamma_arm_readiness.md:11-14` and `docs/contracts/d165_dominance_closeout.md:61,66-69`; roster enforced in code at `generate_configs.py:2826-2860` + `:3233` | Nit 2: `:8462` cites R-1 for the R-5 digest |
| **R-8** red-first regression + counterfactuals (i)-(vi) | **MET** | (i) `tests/test_d117_contrast_v5_pack.py:933`; (ii) `:1234`; (iii) `:1268`; (iv) `:1296`; (v) `:1327`; (vi) `tests/test_identity_pins.py` `test_single_identity_set_digest_matches_committed_v3_receipt` | Commit order confirms red-first: `00bc1e18` (tests) precedes `d0e59351` (cure) |

**No clause is satisfied only by a test.** Every R-1…R-7 obligation has a production line above. R-8 is by construction a test clause.

### Clause evidence executed this session

```
$ TMPDIR=…/tmp-opus-cr python3 -m unittest -v \
    tests.test_identity_pins.SharedDerivationTests.test_single_identity_set_digest_matches_committed_v3_receipt \
    tests.test_identity_pins.SharedDerivationTests.test_identity_unit_set_digest_uses_sorted_distinct_hashes \
    tests.test_identity_pins.SharedDerivationTests.test_common_profile_projection_removes_only_member_manifest_binding
test_single_identity_set_digest_matches_committed_v3_receipt … ok
test_identity_unit_set_digest_uses_sorted_distinct_hashes … ok
test_common_profile_projection_removes_only_member_manifest_binding … ok
Ran 3 tests in 0.006s
OK

$ TMPDIR=…/tmp-opus-cr python3 -m unittest -v tests.test_analysis_inputs.FrozenConsumerIdentitySetTests
… 12 tests …
Ran 12 tests in 33.541s
OK
```

R-5's contract worked example, recomputed live rather than transcribed:

```
domain             : joulewise.identity_unit_config_set.v1
manifest one       : ea6cbc2e9870340c7b9ec85d64ec861ce53b7ca6f927bf72eff73add97f36732
doc claims         : ea6cbc2e9870340c7b9ec85d64ec861ce53b7ca6f927bf72eff73add97f36732
manifest two       : f6130adccb590d06e952c8034fc36e080884980444a1ce441ee1c303cac58c3b
doc claims         : f6130adccb590d06e952c8034fc36e080884980444a1ce441ee1c303cac58c3b
set digest fwd     : 7462f88bc7188c4630ab27e554a1be4a59aeae310a5fe16936b320c505caf4c9
set digest reversed: 7462f88bc7188c4630ab27e554a1be4a59aeae310a5fe16936b320c505caf4c9
doc claims         : 7462f88bc7188c4630ab27e554a1be4a59aeae310a5fe16936b320c505caf4c9
single-identity    : True
```

All three digests in `identity_pin_projection.md:824-878` reproduce exactly, order-independently. R-9's registration digest:

```
$ shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b  …
```
unchanged, and pinned in production at `joulewise/night_gate.py:27`.

---

## Item 2 — caller table

| Callee | Caller (production) | file:line | What it does with the return | Breaks on new labels? |
|---|---|---|---|---|
| `_frozen_consumer_identity_set` | `_floor_request_or_refusal` | `joulewise/analysis_engine/inputs.py:4082` | Tri-state branch (`None` / empty / non-empty). Never string-matched | No |
| `_floor_request_or_refusal` | `_resolve_contrast_floor` | `joulewise/analysis_engine/__init__.py:388` | `isinstance(…, tuple)` discriminates; tuple stored verbatim into `FloorResolution(reason_codes=…)` at `:422` | No |
| `_floor_request_or_refusal` | `floor_request_for_evidence` | `joulewise/analysis_engine/inputs.py:4202` | Collapses tuple → `None` | No — but this wrapper has **no production caller** (Nit 1) |
| `floor_request_for_evidence` | *(none)* | — | Dead. Import at `__init__.py:49`; `inputs.__all__:4555`; not in `analysis_engine.__all__` | n/a |
| `_floor_engine_reasons` | `_analysis_reasons` | `joulewise/analysis_engine/__init__.py:1229` | `reasons.extend(...)` → `ordered_reason_codes(...)` at `:1233` | No — total `else` at `:221-222` maps both new codes to `floor_transport_inapplicable` **before** the validator |

**Reason-code registries and enumerators, all checked:**

| Surface | file:line | Status |
|---|---|---|
| `TRANSPORT_REASON_CODES` (declared "Closed v1") | `joulewise/detection_floor.py:293,307-308` | **Updated** ✓ |
| Closed-set assertion | `joulewise/detection_floor.py:4416` | Passes; defensive only (codes are minted in `inputs.py`, not here) |
| Closed-set test | `tests/test_detection_floor.py:3695,3712-3713` | **Updated** ✓ — mutant "remove both codes" is killed only here |
| `ordered_reason_codes` — raises on unknown | `joulewise/analysis_engine/claims.py:219-234` | Unreachable by new codes; correct to leave `ENGINE_REASON_CODES` untouched |
| `reason_kinds` DATA/CONTRACT/DEAD/LOCK partition | `joulewise/analysis_engine/reason_kinds.py:87`; `tests/test_reason_code_partition.py:167` | Unaffected; would trip if either code were ever added to `ENGINE_REASON_CODES` — a useful tripwire |
| Renderer mapping reason → human text | *(none exists in `joulewise/`)* | No KeyError risk |
| `artifact.py` floor-resolution reason wire | `joulewise/analysis_engine/artifact.py:2255-2258` | `_string_list` only, **no enum** — open wire. Pre-existing for all 17 codes, not a branch defect |
| `artifact.py` claim-evaluation reason wires | `:1319-1323, 1693-1699, 1907-1911` | `try/except ValueError` → appends schema error; fails closed. New codes never reach these |
| Docs reason-code census | `docs/specs/c027/p2-039_floor_artifact.md:605-630` | **Updated** ✓, same order as the code tuple |
| Engine vocabularies in decision log | `docs/decision_log.md:3115-3143, 3146-3195` | Different vocabulary; no amendment owed (see dropped finding) |
| Exact string matches on floor literals | `__init__.py:215,217,219`; `output_identity.py:789`; `scripts/claims_lint.py:1475` | None reachable by the new codes |

One integration consequence worth the magistrate's eye, not a finding: because of the `else` collapse, `scripts/claims_lint.py:1575-1583` ("caveat must surface every exact artifact reason code") operates on the translated vocabulary, so a **published caveat can never name an identity failure** — it will say `floor_transport_inapplicable`. The distinction survives only in `floor.resolutions[*].reason_codes`. That is consistent with `identity_pin_projection.md:602-603` ("The analysis output distinguishes two identity failures"), since the artifact does carry them — but the claim wire does not, and the contract does not say so.

---

## Item 5 — frozen-surface check (verbatim, unabridged)

The check **is not empty.** Command and complete output:

```
$ git diff 3e6243df8943f6a4ec152cab7ea791a8a161efea 7e888d82 -- \
    docs/paper/draft-v1.md \
    configs/campaigns/d117_contrast_v5/generate_configs.py \
    configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/
```

`docs/paper/draft-v1.md` and `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/` are **clean**. `configs/campaigns/d117_contrast_v5/generate_configs.py` is not — 115 lines changed: `+ABBA_POSITIONS` (`:176`), `+render_suite_manifest_bytes` (`:1118`), `+decode_declared_suite_manifest_set` (`:1479`), `+declared_identity_workload_profile` (`:1502`), `+validate_gamma_identity_unit_roster` (`:2826`), the `build_tree` workload swap (`:2634`), and the suite-bytes renderer swap at `:3065`.

**This is expected, not a violation, and the brief's premise is what is wrong.** Ruling 171a **R-2** (`06-ruling-171a.md:36-45`) *orders* the generator to change: "The generator declares, per decode unit, in `declared_identity.workload_profile`: `suite_manifest_set` = …". R-7 likewise requires the roster enforcement. The file cannot be a frozen surface for this lane.

I verified the surface that actually is frozen did not move:

```
$ git ls-tree -r --name-only 7e888d82 configs/campaigns/d117_contrast_v5/
configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json
configs/campaigns/d117_contrast_v5/generate_configs.py

$ git diff <merge-base> 7e888d82 --name-only -- configs/
configs/campaigns/d117_contrast_v5/generate_configs.py
```

The `_v5` **pack bytes are not committed** — only the generator and the registration JSON — and the pack is draft (`generate_configs.py:229` `PRESERVE_CURRENT_FROZEN_BYTES = False`, `:230` `PACK_STATUS = DRAFT_STATUS`, with a constructor downgrade guard at `:271-277`). So no frozen bytes were rewritten, and R-9's registration digest is byte-identical (pasted above).

---

## Merge-ability (item 4)

- **Git fixtures are safe on a fresh runner.** `.github/workflows/` sets no git identity anywhere, but the new helper configures its own: `tests/test_d117_contrast_v5_pack.py:364-365` sets `user.name`/`user.email` before any `commit_fixture` (`:367-370`). The cross-module reuse at `tests/test_analysis_inputs.py:346-356` goes through `init_fixture_git`, so it inherits the identity. The pre-existing `tests/test_identity_pins.py:84-85` helper is byte-identical to merge-base — this risk class is pre-existing and already handled.
- **No `$HOME`, network, hardware probe, or fixed temp path** in the new tests; all 21 new temp roots use `tempfile`. No sockets, so the macOS path-length limit is not in play.
- **Nothing off-lane.** All 44 files map to a ruling clause: `d165_dominance_closeout.md` and `gamma_arm_readiness.md` are the S3/R-7 `prefill_p256`→`p<N>` corrections the ruling explicitly ordered preserved (`06:25-27`), and `detection_floor.py` +2 / `test_detection_floor.py` +2 are the required reason-code registration. The 29 trace files are the lane's own custody.
- Only Nit 4 (stale timings) is a genuine merge-time consideration.

---

## What this pass did NOT check

- **No mutation testing and no mutant table** — deliberate, per brief; three execution-lens passes already ran. I did not independently re-derive any mutant verdict from files 10/11/17/18/26.
- **No full test suite.** I ran 15 tests in 2 targeted invocations. `python3 -m unittest discover` was forbidden and not run; I have no evidence about the other ~40 modules, and specifically none about whether the branch regresses any pre-existing test.
- **No live P-8 runbook re-run** — R-9's closure evidence (regenerate + freeze/verify all three `_v5` packs) is the magistrate's live bench duty and is unexecuted here. I verified R-9's *digest* invariant only.
- **No hardware, no measurement, no `[QUIET-MAC]` interaction.**
- **I did not audit the statistical or floor-arithmetic content** of `detection_floor.py` beyond the 2-line reason census, nor `mint_floor_artifact*.py` (R-6(b) says they are unchanged; I confirmed by absence from the diff, not by reading them).
- **I did not verify the eight-step gate paragraph clause-by-clause against a live failing fixture per step.** I read all eight steps at `identity_pin_projection.md:605-630` against `inputs.py:3870-4042` and found the code order and strictness consistent (code filters the U11 row by `schema_version` then checks `evidence_id`/namespace/status — stricter than the prose, not looser), but I executed counterfactuals for none of the eight individually. File 26 claims all eight were proven by another seat; I did not re-verify that claim.
- **I did not read files 07/13/22/23/24/25/26** except file 27, to stay independent. If any of my three should-fix items was already raised and knowingly dispositioned in those files, I would not know — though the zero-hit grep for S1's subject matter across the whole trace directory suggests S1 at least is new.
- **Contamination caveat stands:** a genuinely cold seat might weigh these findings differently.

**Bottom line: no blocker. Three should-fix items, all cheap and all pre-freeze — S1 (contract denies a live, tested check), S2 (an R-2 clause never installed), S3 (absolute `pack_root` defeats floor resolution from any other checkout, under a misleading label).** S1 and S2 are documentation/generator hygiene the magistrate can rule on directly; S3 is the one with a production-semantics consequence and is the item I would put in front of a cold gate before the P-8 freeze run.