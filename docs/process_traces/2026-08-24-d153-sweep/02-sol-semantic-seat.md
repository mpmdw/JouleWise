# D-153 fixation-family semantic sweep — Sol seat (verbatim, via lieutenant coordinator)

Seat: Sol gpt-5.6-sol, effort xhigh, read-only sandbox, WRITE_SCOPE [],
reverse Claude server disabled; coordinated and independently replayed by an
in-session lieutenant agent whose verification notes are included.
Bridge thread: 01a0374f-099a-7dd3-b543-7e9f07229a58 (two turns: base sweep,
then the estate-6 confirmation-pair scope addendum; both turns closed with
valid final bridge-report/v1 envelopes, status DONE, no_edits).
Anchor: commit 7d586a691f3c97054b474ee0223558438f24d67e.
Received by the magistrate 2026-08-24 evening; recorded verbatim below.

---

## Lead verification replayed (coordinator's own checks, not Sol's word)

1. **F1 exact strings** — runsheet line 2689 greps `test_successor_pinset_is_byte_pinned_at_fixation`; the delta defines `test_successor_pinset_hs_byte_pin` (delta lines 67, 76); the new name appears **zero** times in the runsheet. Confirmed.
2. **Sentinel** — `S0-FIXATION-SUBSTITUTION-PENDING` agrees exactly (runsheet 3045/3050, delta 31/68). Confirmed.
3. **Estate-6 arm argv** — the §3.9 arm loop (runsheet 2135–2153) passes `--pack-root/--arm-context/--window-custody-root` and never `--expected-confirmation-digest`; the flag's only runsheet occurrence is prose at line 1899. Confirmed.
4. **Stale prose** — line 1934 ("After freeze ×3, successor verification and fixation") and line 2087 ("§3.9 Arm and verify all three after window closure and fixation"). Confirmed.
5. **Freeze-CLI interface gap (finding 48)** — at the pinned commit, the `freeze` subcommand takes only `--pack-root`, `--expected-confirmation-digest`, `--predecessor-pack-root`; **no confirmation-table-path flag exists anywhere in the CLI** (arm/verify derive the table via `--window-custody-root`; freeze has no such route). Confirmed by grep of the full argument surface. (File: `scripts/generate_arm_readiness.py`.)
6. **Estate-6 fork resolution** — runsheet lines 3216–3245 verbatim: "a step sequenced after the step that needs its output" is an **instrument failure** ("cured on main, re-ratified, and S-0 restarts from §1.1"), and "A `record_env` duplicate … the estate is superseded." Sol's no-NEEDS_RULING resolution (Option 2, fresh estate mandatory) is grounded in the instrument's own text. Confirmed.

One taxonomy note: Sol extended the (a)/(b)/(c) classification with an `N/A` class for pre-mint calls and marker-deferral lanes where the confirmation pair is contractually inapplicable — a correct refinement, explicitly flagged, not a dodge.

---

## RAW REPORT — Turn 1 (fixation-order semantic sweep)

Verdict key: `BROKEN` = executable or acceptance semantics cannot hold; `STALE-PROSE` = commands viable but text describes the pre-D-153 order or old delta contents.

| # | Site | Lines | Fixation-order assumption | Verdict | Minimal cure |
|---:|---|---:|---|---|---|
| 1 | S0-O3 revision record | 16–30 | `074-*` produced at mint, rechecked at fixation | OK | None — this is the correct producer/consumer cure shape |
| 2 | D-153 errata summary | 83–101 | Marker, arm, local green, all §4 probes at `$PINSET_MINT_HEAD`; fixation is §4.10 | OK | None |
| 3 | Retained r2→r3 history | 167–172 | Says delta applied in §3.7 before `tests.test_receipt_histsem` — r4 no longer does | STALE-PROSE | Say this was the r3 cure; D-153 moved application + byte-pin suite to §4.10 |
| 4 | Environment-state contract | 300–306 | `$PINSET_MINT_HEAD`/`$PROBE_BASE`/`$FIXATION_COMMIT` recorded only when computed | OK | None; `$FIXATION_COMMIT` has no executable pre-fixation consumer |
| 5 | Delta custody/authentication | 493–495, 560, 663–671, 949–1005, 1683–1728 | Delta authenticated before fixation; authentication ≠ application | OK | None |
| 6 | Pre-derivation histsem suite | 1541–1572 | Consumes only A2's digest-independent tests; no hS test present pre-fixation | OK | None — correct first coordinate of D-153 W1/D4 |
| 7 | Mint and `074-*` producer | 1732–1844 | Successor digest first exists at mint head; recording needs no fixation | OK | None |
| 8 | Explicit mint/fixation boundary | 1854–1862 | Everything through the probe battery at mint head, no fixation edit | OK | None |
| 9 | §3.8 lead sentence | 1934–1935 | Says marker construction runs "after … fixation" — it hasn't happened | STALE-PROSE | "After freeze ×3 and successor verification, before fixation…" |
| 10 | Marker + confirmation-table execution | 1941–2055 | Uses mint head, current successor bytes, mint-time digest pre-fixation | OK | None |
| 11 | Confirmation-table comparison wording | 2057–2060 | Says digest must equal what the delta "pinned"; command compares pre-fixation `074-*` | STALE-PROSE | "must equal the mint-time digest that §4.10 will pin"; update refusal text |
| 12 | §3.9 heading | 2087 | "after window closure and fixation" | STALE-PROSE | Rename: "after allowlist-contract closure, before fixation" |
| 13 | Arm head guard + probe-base binding | 2089–2123 | Requires `HEAD == PINSET_MINT_HEAD`, refuses if fixation already ran | OK | None |
| 14 | Clean-arm + returned census | 2174–2329 | Depends on fixation NOT having happened (ruled 112-path set, empty residue) | OK | None |
| 15 | §3.10 local-green half | 2335–2355 | Full suite at mint head; real minted successor vs A2 tests, no hS | OK | None — second real-successor coordinate before fixation |
| 16 | §3.10 published-green half | 2357–2366 | Explicitly defers until an accepted fixation head exists | OK | None — future post-fixation operation, not a premature consumer |
| 17 | §4 common base | 2117–2123, 2370–2390 | `$PROBE_BASE` = `$PINSET_MINT_HEAD`; code-name vars from pre-fixation candidate | OK | None; `$EVIDENCE_COMMIT` exceptions deliberate |
| 18 | Probe 4(a) ordinary changed path | 2392–2414 | Cut at `$PROBE_BASE`; needs `freeze-0004` + changed-set logic, not hS | OK | None |
| 19 | Probe 4(b.1) custody namespace | 2416–2463 | Mint-head clone; isolated `readiness_evidence_unreadable`, no R1 residue yet | OK | None |
| 20 | Probe 4(b.2) pack namespace | 2465–2497 | Cut at `$EVIDENCE_COMMIT` deliberately pre-freeze/mint/fixation | OK | None |
| 21 | Probe 4(c) plan mutations | 2499–2545 | Both cut at `$PROBE_BASE`; refusal supplied by pre-derivation code | OK | None |
| 22 | Probe 4(d) candidate-list variants | 2547–2593 | Head-independent; no fixation product consumed | OK | None |
| 23 | Probe 4(e) eight `110-*` replay cases | 2595–2659 | All cut at `$PROBE_BASE`; seven pack classes + successor structural/C→S refusal are pre-fixation mechanisms | OK | Keep the eight `110-*` probes pre-fixation |
| 24 | Successor-class table + byte-pin prose | 2661–2678 | Says byte-only tamper must fail "after fixation," then directs the check inside a pre-fixation case | BROKEN | Point the after-fixation clause forward to a post-`077-*` byte-pin probe; distinguish pre-fix `110-*` structural/C→S evidence from post-fix `118-*` hS evidence |
| 25 | `118-pinset-byte-pin` execution | 2680–2691 | Runs cut from `$PROBE_BASE` before the hS method exists AND greps the nonexistent old name | BROKEN | Move `118-*` after fixation: fresh case at `$FIXATION_COMMIT`, byte-only successor change, require failure of exact `test_successor_pinset_hs_byte_pin` |
| 26 | Probe 4(e.1) C→S unit + transaction paths | 2702–2793 | Mint-head candidate + `$PROBE_BASE` case; digest-conditional subtraction, not hS | OK | None |
| 27 | Probe 4(f) manifest binding | 2795–2831 | Cut at `$PROBE_BASE`; refusal is an A2/pre-derivation mechanism | OK | None |
| 28 | Probe 4(g) dual validator | 2833–2881 | Cut at `$PROBE_BASE`; neither validator needs fixation | OK | None |
| 29 | Probe 4(h) histsem enumeration | 2883–2942 | `072-*` at mint; enumeration/chain semantics, not hS | OK | None |
| 30 | Probe 4(i) poison mint/replay | 2944–2976 | Cut at `$EVIDENCE_COMMIT`, deliberately pre-everything | OK | None |
| 31 | §4.10 order + delta scope | 2980–3023 | Clone-only fixation after probes; delta contains only hS + loud-fail guard; real first-post-window ordering distinguished | OK | None; delta lines 9–19 and 54–95 agree |
| 32 | §4.10 substitution python (F3) | 3030–3047 | Digest equality and exactly-one-sentinel are load-bearing but use bare `assert` — vanishes under optimized Python | BROKEN | Replace both with explicit `if …: raise SystemExit(...)`; compute `count = text.count(sentinel)` once and refuse unless exactly one |
| 33 | Fixed-worktree suite labels | 3060–3071 | Suite runs after substitution but before the fixation commit exists; called "post-fixation" | STALE-PROSE | Call it "fixed-worktree pre-commit histsem suite" (or rerun after commit); add exact grep for `test_successor_pinset_hs_byte_pin` in `076-*` |
| 34 | Fixation diff check + commit message | 3073–3083 | Error text says "after window close" (base is mint head); commit message claims "SHA and counts" (counts moved pre-derivation; delta is hS-only) | STALE-PROSE | "after allowlist-contract closure"; commit as e.g. `S-0 pin successor hS byte digest at fixation` |
| 35 | Post-commit independent recomputation | 3086–3098 | Consumes `$FIXATION_COMMIT` only after it exists | OK | None |
| 36 | §5 `r4-2` acceptance | 3109–3118 | Requires whole probe battery + `077-*`, but execution stops at pre-fixation `118-*` before 4(e.1)–4(i) and fixation | BROKEN | After relocating `118-*`: state `110-*` pre-fix, `118-*` post-fix; retain `074-*` as mint-produced |
| 37 | §5 V-1.vi | 3122–3129 | Claims all eight classes in `110-*` AND `118-*` have independent refusals; `118-*` cannot exercise hS at its base and uses the wrong name | BROKEN | Bind seven ordinary classes + successor structural/C→S to pre-fix `110-*`; successor hS falsifier to post-fix `118-*` |
| 38 | §5 rh-8 / successor | 3130–3137 | Calls `020-*`/`090-*` an exact "window-close" contract; treats `rev-list PINSET_MINT_HEAD..FIXATION_COMMIT == 1` as first-post-window proof. Under A6 `090-*` is allowlist-contract closure; the rev-list proves only the clone's first post-mint commit | BROKEN | Rename to allowlist-contract closure; label rev-list clone-proof-only; record real first-post-r4-3-window fixation as a separate external transaction obligation |
| 39 | §5 custody surface | 3146–3156 | Delta authentication precedes application; doesn't imply fixation | OK | None |
| 40 | §5 fixation-delta item | 3157–3162 | Requires one sentinel + minted digest but calls pre-commit `076-*` "post-fixation" and never names the hS test | STALE-PROSE | Fixed-worktree/pre-commit wording; require exact hS method in `076-*` or post-fix `118-*` |
| 41 | §5 two-part green | 3170–3174 | Local green pre-fixation + conditional; published green separate later real-ref run | OK | None |
| 42 | Struck activation delta | 3163–3169, 3182–3188 | No unrelated 21-method activation/count change in fixation | OK | None; reinforces removing "and counts" from commit message |
| 43 | Failure semantics | 3194–3224 | Consumer-before-producer or nonexistent method name = instrument failure | OK | None; current `118-*` defect meets this clause — runsheet amendment, not bench improvisation |
| 44 | O-1 closing statement | 3251–3258 | Distinguishes real first-post-window fixation from §4.10's clone-proof-only late placement | OK | None |

**Exact-string verification (turn 1):** old name only at runsheet 2689; delta method at delta 67/76; new name absent from runsheet; sentinel identical both sides; delta names the moved A2 products (lines 14–19) and adds none of them; the pre-fixation committed test file has the A2 products but no `SUCCESSOR_PINSET_SHA256` or hS test — proving the current `118-*` case cannot exercise the intended guard.

---

## RAW REPORT — Turn 2 (estate-6 addendum: C→S confirmation-pair sweep)

Headline: **no active post-mint transaction/probe CLI invocation at this commit supplies the complete `C + hC` pair**, and the freeze CLI **cannot** accept the table path at all. Sol added an `N/A` class for calls where the pair is contractually inapplicable (pre-mint, marker deferral) rather than mislabeling them refusal probes.

| # | Site | Lines | Finding | Verdict | Minimal cure |
|---:|---|---:|---|---|---|
| 45 | Step-6 pair authority | contract 49–60, 143–181; runsheet 1903–1915, 1986–1988 | Digest-conditional successor gate requires BOTH custody table path and operator-supplied out-of-band `hC`; missing either → `DEPENDENCY_CHANGED_SET`. hS is not a substitute for hC | OK authority; violated below | Preserve the two-input distinction in every cure |
| 46 | Transaction arm loop `091-*` | 2025–2032, 2070–2077, 2135–2145 | Table derivable via `--window-custody-root`, but argv omits `--expected-confirmation-digest` | BROKEN (b) | Operator re-pastes `ED_STEP6_CONFIRMED_SHA256` in-block, validate, pass `--expected-confirmation-digest` to every arm; never into `env.sh` |
| 47 | Verification loop `092-*` | 2155–2162 | Table path from receipt custody, no hC; latent until cured arms produce receipts | BROKEN (b) | Reuse the in-block pasted value for every `verify` |
| 48 | Freeze CLI interface | `scripts/generate_arm_readiness.py` 28–46, 108–120; library 6680–6700 | `freeze` exposes only `--expected-confirmation-digest`, no table-path flag; forwards `step6_confirmation_table=None`. Post-mint replay cannot supply the complete pair | BROKEN interface | Add `--step6-confirmation-table` (Path) to freeze, forward it; focused forwarding + refusal tests |
| 49 | Probe 4(a) `101-*` | 2392–2406 | Omits both inputs; missing confirmation yields the same `$CHANGED_CODE` the probe expects — false-pass risk | BROKEN (b) | Supply both; assert refusal detail names the ordinary added path, not missing confirmation |
| 50 | Probe 4(b.1) `102-*` | 2426–2442, 2447–2462 | Copied custody supplies path indirectly; arm omits hC — contradicts 2438–2439's isolated-refusal claim | BROKEN (b) | Re-paste hC in-block; assert no R1 code appears |
| 51 | Probe 4(c) `104-*`/`105-*` | 2499–2545 | Post-mint replays omit the pair; missing-confirmation can fire before the intended `DEPENDENCY_MANIFEST` conjunct | BROKEN (b) | Re-paste per block; explicit path + digest via cured freeze CLI |
| 52 | Probe 4(e) eight `110-*` calls | 2595–2659 | All lack the pair; contaminates isolation for seven classes; for `pinset-json` a missing-confirmation refusal can substitute for the intended authenticated C→S mismatch | BROKEN (b) | Re-paste once per loop block, pass both to all eight; reject any transcript containing "no expected confirmation digest supplied" |
| 53 | Focused `122-*` unit battery | 2702–2719; test file 648–876 | Synthetic suite has a valid pair + deliberate negative cases; runsheet 2704–2708 declares the refusal legs | OK (a)/(c) | None |
| 54 | Later-rewrite arm `123-*` | 2771–2782 | Path inferred, hC omitted; expected `$CHANGED_CODE` could arise from missing confirmation, not the rewrite | BROKEN (b) | Re-paste hC; require detail equivalent to "bytes at reviewed HEAD differ from Ed's confirmed step-6 digest" |
| 55 | `119-*`/`121-*` replays | 2795–2831, 2833–2871 | Post-mint freeze replays with neither input | BROKEN (b) | Re-paste per block; pass pair through cured interface |
| 56 | Pre-mint freeze calls | 1625–1643, 1655–1666, 2465–2492, 2944–2965; library 6695–6699 | `050/060/103/140/141-*` run before the successor exists; library says absent digest is harmless here | OK N/A | Do NOT add confirmation inputs to these |
| 57 | Marker build + candidate replay | 1877–1926, 1944–2011; contract 183–220 | Disclosed deferral; passing confirmation alongside deferral is a contradiction | OK N/A | Do NOT "fix" `081-*`/`082-*` |
| 58 | Histsem/test-run invocations | 1541–1572, 1822–1826, 2335–2355, 2680–2691, 2883–2942, 3060–3071 | `033/072/093/118/130/131/076-*` are not live R1 consumers | OK for pair scope | Apply the `118-*` fixation cure but no operator hC injection |
| 59 | Published marker replay + green | 2357–2366, 3170–3174 | Future publication verification says "Ed-confirmed table" but specifies no pair-bearing argv or re-paste requirement; publication replay IS an enforcing lane | BROKEN spec (b) | Add explicit block: `--confirmation "$STEP6_TABLE"` + re-pasted `--expected-confirmation-digest`, committed-blob lane, four-way ref equality, `gate_admissible:true` |
| 60 | §5 consumer claims | 3109–3145, 3170–3174 | `r4-2`, V-2, V-1.vi, rh-8, two-part green assume clean authenticated consumers; the class-(b) transcripts cannot support them | BROKEN downstream | Require pair-bearing transcripts + absence of missing-confirmation detail |
| 61 | Estate-6 re-entry guard | 577–583, 2117–2133 | Rerunning the §3.9 block duplicates `FINAL_HEAD`, then `PROBE_BASE`, then `ARM_CONTEXT` — not just `ARM_CONTEXT` | BROKEN for same-block rerun | Do not rerun the original block in estate 6 |
| 62 | Estate-6 disposition | 3216–3245 | Missing consumer argument = instrument failure: amend on main, re-ratify, restart §1.1; `record_env` duplicate independently supersedes the estate | RESOLVED — no ruling needed | Strike/void estate 6 in writing, preserve failed `091-*` evidence, restart fresh after the erratum lands |

**Classification summary:** there is **no class-(a) live CLI call in the runsheet at this commit**. Class (a) exists only inside the synthetic `122-*` test's positive case (test file 729–743); its deliberate class-(c) matrix is test file 745–876 matching runsheet 2704–2708. Class (b): `091, 092, 101, 102, 104, 105, all 110-*, 119, 121, 123`, the PASS-side transcript check at 2721–2747 (downstream), and the unspecified published-replay block. N/A: `033, 050, 060, 072, 081, 082, 093, 103, 106–108, 118, 120, 130, 131, 140, 141, 076-*`, and the manual table/hC equality check at 2025–2060.

**Estate-6 continuation:** Option 1 (bespoke continuation reusing recorded `ARM_CONTEXT`) would need to skip three `record_env` calls, could not reuse `091/092-*` names without overwriting failed evidence, and conflicts with lines 3216–3224. Option 2 (strike estate 6, land + re-ratify the corrected instrument, restart fresh at §1.1) is **mandatory under the runsheet's own failure semantics** (3216–3224; 3238–3245 independently supersede the estate on a `record_env` duplicate). No NEEDS_RULING — the coordinator verified the cited text verbatim and concurs.

## Revised consolidated one-PR cure list (supersedes turn 1's)

1. **[NEW]** Repair the freeze consumer interface: add a confirmation-table-path option to `freeze`, forward to `generate_freeze_receipt`; tests for valid pair / missing path / missing hC / malformed hC / mismatched bytes.
2. **[NEW]** Standard per-block confirmation preamble in every post-mint enforcing block: operator re-pastes `ED_STEP6_CONFIRMED_SHA256`, lowercase-64-hex validation, explicit table path where needed. Never into `env.sh`, never recovered from `085-*`, never carried across blocks.
3. **[NEW]** Cure §3.9: re-paste hC once per block, pass to every `arm` and `verify`.
4. **[NEW]** Cure post-mint probes `101, 102, 104, 105, 110×8, 119, 121, 123` with the complete pair, re-pasted per block.
5. **[NEW]** Make probe refusals non-ambiguous: reject "no expected confirmation digest supplied"; assert mutation-specific detail (essential for `101`, `102`, `110-pinset-json`, `123`).
6. **[NEW]** Add the explicit published marker-replay command (pair-bearing, committed-blob lane, four-way ref equality, `gate_admissible:true`).
7. **[NEW]** Update §5 acceptance (`r4-2`, V-2, V-1.vi, rh-8, two-part green) to require pair-bearing evidence; preserve D-150 candidate deferral unchanged.
8. **[NEW]** Record estate 6 as superseded; preserve failed evidence; no same-estate continuation lane; do not weaken `record_env`.
9. **[CARRIED]** Relocate `118-*` after `077-*`: fresh case at `$FIXATION_COMMIT`, byte-only tamper, exact `test_successor_pinset_hs_byte_pin`, keep transcript name `118-pinset-byte-pin.txt`.
10. **[CARRIED]** Keep `110-*` pre-fixation; clarify the two coordinates.
11. **[CARRIED]** Harden §4.10 substitution: both bare asserts → explicit non-optimizable refusals (`if …: raise SystemExit`), single `count = text.count(sentinel)` requiring exactly one.
12. **[CARRIED]** Require `test_successor_pinset_hs_byte_pin` to appear in successful `076-*` and failing `118-*`.
13. **[CARRIED]** Repair stale fixation prose: lines 167–172, 1934–1935, 2057–2060, 2087, 3060–3071, 3157–3162.
14. **[CARRIED]** A6 vocabulary + commit content: "allowlist-contract closure" at line 3074; drop "counts"/"window close" from the fixation commit message; split clone-first-post-mint evidence from the real first-post-window obligation.
15. **[CARRIED+NEW]** Split §4(e)/§5 acceptance by coordinate and authenticator: pre-fix `110-*`; post-fix `118-*`; hS fixation evidence; separate `C + hC` evidence per enforcing consumer.

## Adjudication (coordinator)

Accepted. The known instances reproduce exactly as claimed; the new estate-wide finding — zero class-(a) live consumers plus the freeze-CLI table-path gap — is corroborated by the coordinator's independent argument-surface check and is the deepest expression of the shared cause: **the runsheet's consumers were written against interfaces and orderings that D-153/step-6 later moved out from under them**. The fixation delta itself needs no change. The one code change (cure 1) is outside the runsheet and will need its own WRITE_SCOPE when delegated. Estate 6 disposition requires no ruling; the instrument's own failure-semantics text (lines 3216–3245) mandates strike + fresh estate.
