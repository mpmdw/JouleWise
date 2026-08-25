# D-153 fixation-family semantic sweep — Opus contract-lens seat (verbatim)

Seat: Opus (general-purpose agent, contract lens, independent of the Sol seat).
Anchor: commit 7d586a69 (branch fix/s0-074-sequencing).
Received by the magistrate 2026-08-24 evening; recorded verbatim below.

---

## DERIVED TIMELINE (from D-153 A1/A2/A6 + the delta alone)

Epochs, in execution order in the clone:

- **E0** `$BASE` = `$EVIDENCE_DERIVATION_HEAD` — post-W1 candidate. `tests/test_receipt_histsem.py` already holds: `SUCCESSOR_PINSET`, `SUCCESSOR_PACK_COUNT/RECEIPT_COUNT/PACK_IDS`, `test_successor_member_shape_when_present` (skips while the member is absent), `test_differential_self_test_all_governed_packs`, chain-derived corpus totals, `SuccessorPinsetDigestConditionTests`. Verified against 7bf3dcfa: W1 landed, and the file at 7d586a69 == the file at HEAD.
- **E1** `$EVIDENCE_COMMIT` → **E2** `$FREEZE_COMMIT` — successor JSON still absent; changed set carries no digest-conditional member.
- **E3** `$PINSET_MINT_HEAD` (== `$PINSET_COMMIT`) — **allowlist-contract closure**. Successor JSON exists. `074-successor-sha256.txt` produced here (S0-O3 cure). `$PROBE_BASE` == this head. Test file **unchanged** from E0: no `SUCCESSOR_PINSET_SHA256`, no `test_successor_pinset_hs_byte_pin`.
- **E3.5** hC confirmed (§3.8) — no commit; the step-6 table and its digest are custody-external, promoted to `$CUSTODY/windows/family_publication/`. From here on the digest-conditional successor path is *dischargeable* — and only if a consumer is handed the pair.
- **E4** `$FIXATION_COMMIT` (§4.10, last commit) — `SUCCESSOR_PINSET_SHA256` (64-hex) and `test_successor_pinset_hs_byte_pin` first exist. `073/075/076/077` produced here.

Line-coordinate epochs of the test file: W1 shifted everything from ~line 145 down by **+22**; fixation adds +7 at ~45 and +21 at ~224. Any citation into that file must name which of the three coordinate systems it is in.

---

## FINDINGS

### F0 — BLOCKER, and it invalidates the stated basis of D-153 finding 1. `arm_readiness.py:4426-4465`; runsheet 2214-2240, 2404, 2522, 2535, 2651-2658, 2730-2731, 2780, 2869
The conditional-path loop raises **before** the `relevant` raise:

```
for conditional_path in sorted(outstanding & conditional):
    ...  _require_confirmed_conditional_path(...)   # raises DEPENDENCY_CHANGED_SET
relevant = sorted(outstanding)
if relevant: raise DEPENDENCY_CHANGED_SET
```

Both paths carry the **same registry role and therefore the same code**. So at any post-E3 head with no hC supplied, the refusal is always the C→S one, never the "ordinary path" one — regardless of what else is outstanding. Consequences:

1. R4-O1's recorded diagnosis (2218-2225: "`tests/test_receipt_histsem.py` is a changed path outside the ruled 112 → `DEPENDENCY_CHANGED_SET`") is **unproven and probably wrong**: pre-D-153 the arm at `$FIXATION_COMMIT` would have raised on the *conditional* path first. D-153's cure (take the test file out of the changed set) therefore does not remove the refusal — which is exactly what estate 6 recorded.
2. Every runsheet assertion that greps for `$CHANGED_CODE` / `$MANIFEST_CODE` alone cannot distinguish the two causes. **Epoch verdict: the runsheet has no assertion capable of falsifying its own R1 story.**
- **Cure:** every R1-code assertion asserts the refusal *detail* shape, not just the code (e.g. `"digest-conditional allowlist path"` must be **absent** from 101/104/105/110-*/119/121, and **present** in 123). Re-open the R4-O1 record: its cause attribution is not established.

### F1 — BLOCKER (known-open, confirmed and widened). 2680-2691
`grep -F 'test_successor_pinset_is_byte_pinned_at_fixation'` — the method's real name is `test_successor_pinset_hs_byte_pin`, **and** neither name exists at E3. The case is cut from `$PROBE_BASE`. Renaming the grep does not cure it. Worse: `test "$BYTE_PIN_RC" != 0` will likely still pass at E3 (the tamper reddens `test_full_corpus_verifies_two_coordinates_and_facts` via the verifier), so the probe would pass for a reason that has nothing to do with a byte pin if the grep were merely deleted.
- **Cure:** move this entire sub-block to **§4.10, after step 3**, cutting a fresh case at `$FIXATION_COMMIT` with the `pinset-json` tamper re-applied there; grep `test_successor_pinset_hs_byte_pin`; assert the failure names *that* method. Renumber `118-*` or record it as positional-historic like 074.

### F2 — BLOCKER (new). 2672, 2674-2678
Table row: "after fixation, byte-only tamper must also fail the successor SHA assertion" — honest about the epoch, but the block below it runs pre-fixation, so the row is the only place the ordering is stated and the code contradicts it. Separately, 2674-2678's "the suite that carries the fixation pin" is false at E3, and the tamper used (`packs[0].plan_sha256 = 0*64`, canonically re-rendered) is **not** byte-only — a genuinely byte-only tamper is already caught pre-fixation by the canonicality check at `tests/test_receipt_histsem.py:201-202`. The property the delta exists for (a re-canonicalised re-mint of identical shape) is exercised by **no probe in the runsheet**.
- **Cure:** with F1's move, add a shape-preserving re-mint tamper case (identical `pack_count`/`receipt_count`/`pack_ids`, canonical bytes, different `plan_sha256`) at `$FIXATION_COMMIT`; that is the only case in which hS is the sole discriminator.

### F3 — BLOCKER family: the C→S supply line after §3.8 (coordinator addendum)
Mechanics verified in code: `--expected-confirmation-digest` exists on `freeze`/`arm`/`verify` (`scripts/generate_arm_readiness.py:30-71`); the **table path** is auto-resolved only in `generate_arm_receipt` (`arm_readiness.py:7479`) and `verify_arm_receipt` (`:7733`). `_authenticate_confirmation_table` (`:10764-10778`) raises `confirmation_missing` if **either** the digest **or** the path is None.

Classification of every post-§3.8 consumer invocation:

| # | Site | Invocation | Verdict |
|---|---|---|---|
| **3a** | 2139-2141 | §3.9 `arm` ×3 | **omits defectively** — estate 6's recorded refusal. Path resolves from `--window-custody-root "$CUSTODY/windows"`; only the digest is missing. Runsheet-curable. |
| **3b** | 2156-2157 | §3.9 `verify` ×3 | **omits defectively** — path resolves from the receipt's custody root; digest missing. Runsheet-curable. |
| **3c** | 2777-2779 | §4(e.1) later-rewrite `arm` | **omits defectively, and it is the load-bearing one.** Without the pair the refusal is "no expected confirmation digest supplied", not "bytes differ from Ed's confirmed digest" (`:4364-4366`). The probe as written proves **nothing** about a later rewrite. It is a deliberate-refusal leg *only when the pair IS supplied*. |
| **3d** | 2454-2456 + prose 2438 | §4(b.1) `arm` into `PROBE_CUSTODY` | **omits defectively.** The block does copy the table into `$PROBE_CUSTODY/family_publication` (2450), so the path resolves; the digest is missing. Prose at 2438 ("this arm carries no R1 code at all, so `readiness_evidence_unreadable` is the refusal under test in isolation") is **false as written** and the isolation claim fails. |
| **3e** | 2400, 2520, 2533, 2639 (×8), 2819, 2867 | every `freeze` cut from `$PROBE_BASE` | **structurally unsatisfiable — NOT runsheet-curable.** `generate_freeze_receipt` has a `step6_confirmation_table` parameter but the CLI never passes one and does no default resolution, so the path is always None. Per F0's ordering this raises **before** the manifest/digest checks at `:4467-4542`, so `104/105/119/121` (expect `$MANIFEST_CODE`) and the `plan-json` tamper class die; the remaining tamper classes may or may not be masked depending on where each authenticator sits relative to `validate_r1_evidence_lifecycle` — determine per class, do not assume. `generate_freeze_receipt`'s own docstring states the requirement ("Once that pinset exists, the same replay path requires both the table and its out-of-band expected digest and fails closed without them") — the CLI cannot meet it. **This is the third instance of the S0-O2 signature: a contract-required input with no supply line.** It predates D-153 and D-153 did not touch it. |
| **3f** | `scripts/generate_arm_readiness.py:73-76` | `consume` | no `--expected-confirmation-digest` at all. Out of S-0's path (consume is retired to `launch_window.py`), but the real transaction's consume-side C→S enforcement needs a supply line too. Register, don't fix here. |
| — | 2715 | §4(e.1) `SuccessorPinsetDigestConditionTests` | **correct epoch** — class exists post-W1, fixtures are self-contained. |
| — | 2478, 2952 | 4(b.2), 4(i) cases at `$EVIDENCE_COMMIT` | **correct epoch** — pre-mint, no conditional path. |
| — | 2907, 2924 | 4(h) `verify_receipt_histsem.py` | **correct epoch** — different tool, no R1 gate. |

**Cure for 3a-3d, respecting the custody rule:** `ED_STEP6_CONFIRMED_SHA256` is deliberately operator-pasted per block and never in `env.sh` (2028-2029). §3.8 already writes it to `$TRANS/085-ed-step6-confirmed-sha256.txt` (2055) *after* the equality check against the rendered table. Downstream blocks should read **085**, with a guard (`test -s`, `[0-9a-f]{64}` regex, write-once), and a sentence in place saying why: the value entered the record only through Ed's paste, so 085 is a custody transcript, not a self-recompute. Do **not** cure by `shasum -a 256 "$STEP6_CANDIDATE"` in each block — that authenticates the table against itself, which `_authenticate_confirmation_table`'s own docstring forbids. Re-pasting per block also satisfies the rule but multiplies transcription risk across ~6 sites; recommend 085 plus one re-paste at §3.9 as the operator's own confirmation.
**Cure for 3e:** code question, NEEDS_RULING, same shape as S0-O2. Either `freeze` gains a table-path flag (contract-consistent; the parameter already exists), or §4's replay probes are re-cut from a head where the successor is not yet in the changed set — which destroys 4(a)'s stated replay mechanism (2410-2413). Recommend the flag.

### F4 — defect. 2087
Heading: "### 3.9 Arm and verify all three **after window closure and fixation**". Both halves wrong: §3.9 runs at E3, before fixation; and "window closure" is the A6-reserved term for the r4-3 commit-freeze close. The section body (2089-2091) says the opposite of its own heading.
- **Cure:** "3.9 Arm and verify all three at the allowlist-contract closure head".

### F5 — defect. 1934
"After freeze ×3, successor verification **and fixation**, run the reviewed constructor and consumer" — §3.8 runs at E3. Pre-D-153 residue.
- **Cure:** delete "and fixation".

### F6 — defect. 2057, 2060
Comment "must be the one **the fixation delta pinned**" and die "different from **the fixation pin**". At §3.8 nothing is pinned; 074 is the mint-time record.
- **Cure:** "…must equal the mint-time successor digest recorded at §3.7"; die message likewise.

### F7 — defect. 3076
Commit message `'S-0 fix successor pinset SHA **and counts** after **window close**'`. Two epoch errors in the permanent record: A2 moved the counts into W1, so this commit changes no counts; and "window close" is reserved.
- **Cure:** `'S-0 fixation: pin successor pinset SHA-256 (hS) after the allowlist-contract closure'`.

### F8 — defect. 3074
Die: "the v1 pinset member changed **after window close**". Vocabulary.
- **Cure:** "…after the allowlist-contract closure".

### F9 — defect. 3130
§5: "The 112 arithmetic and exact **window-close contract** are PASS". Vocabulary.
- **Cure:** "allowlist-contract closure".

### F10 — defect. 3136
§5: "fixation is the first **post-window** commit". In the clone proof it is the first commit after the allowlist-contract closure; the clone proof has no commit-freeze window at all. Citing this box as evidence of post-window fixation is exactly the misuse §4.10's own note (2989-2995) forbids.
- **Cure:** "fixation is the first commit after the allowlist-contract closure (clone-proof-only placement; see §4.10)".

### F11 — defect, contract-bearing. 2357-2359
"After the lead actually publishes **the accepted fixation head**, a clean checkout must prove strict four-way equality…". Under **A3** the published head is green *without* the byte pin, and under **A1** fixation is the first commit *after* the window close. Binding publication acceptance to the fixation head is the same collision A6 was written to break.
- **Cure:** the published-green head is the window-close head; fixation follows publication. State that, and cite A1+A3.

### F12 — defect. 3159
§5 Fixation-delta box: "its single sentinel was substituted with the minted successor digest (`074-*`)". Post-S0-O3, 074 is the *mint-time record* the substitution is checked against; the substitution evidence is 075 plus the sentinel-absence grep and the step-2 stdout.
- **Cure:** "…substituted with the digest recomputed at fixation and proven equal to the mint-time record (`074-*`); the substitution is evidenced by `075-*` and the sentinel-absence check".

### F13 — defect, silent. 453-455, 904, 2894, 2942
All citations into `tests/test_receipt_histsem.py` are in **pre-W1 coordinates**, read at a post-W1 head. Verified against 7bf3dcfa^ vs 7bf3dcfa:
- `:138-145` "byte pin asserted with no update/reseal lane" → pre-W1 that was `test_pinset_is_byte_pinned_and_has_no_update_lane` at 138-144; **post-W1 it is 160-166**. `:138-145` now lands inside the builder-interface option tuple.
- `:146-165` "the explicit-override CLI refusal test expects `histsem_pinset_invalid`" (cited three times: 455, 2894, 2942) → pre-W1 that was `test_verifier_cli_refusal_is_canonical_and_exit_two` at 146-164; **post-W1 it is 220-238**. `:146-165` now lands on the builder tail + the byte-pin test.
- `:32` "the v1 pinset byte pin" → `:32` is `PINSET` (the path); the pin literal `PINSET_SHA256` is `:33`. Off-by-one; the `30,33p` audit range covers both, so low severity.
- §1.3's line-audit spec at 904 (`30,33p;138,165p`) therefore extracts the **wrong region** and cannot notice: the loop only asserts the concatenated output is non-empty (912). The 2026-08-24 "anchor remap round 3" re-derived 116 `arm_readiness.py` sites and never touched the test file, even though W1 shifted it +22 in that band.
- **Cure:** remap to `160,166p;220,238p`, fix the three prose citations, and add the test file to the AST anchor map (`s0_anchor_map.py`) so a symbol-level check catches the next shift. Note the coordinates are valid for E0-E3 only; anything cited post-fixation shifts again.

### F14 — defect (non-epoch, found in passing). 1993-1994 vs 2353-2354
§3.8 writes `$TRANS/084-local-green-classification.txt` containing a *marker* classification; §3.10 writes `$TRANS/094-local-green-classification.txt` containing the actual local-green classification. Two transcripts, same basename stem, different meanings, and §5 cites `084-*` (3111) and `093-*/094-*` (3170) as distinct evidence.
- **Cure:** rename 084 to `084-marker-forged-ref-classification.txt` and update 3111.

### F15 — note. 1831-1834, 3110
Transcript ordinals no longer track execution order (074 at §3.7, 073/075/076/077 at §4.10). Disclosed in place at 1831-1834, so not a defect — but §5's `070-*`–`077-*` range (3110) presents it as one contiguous mint-side family inside the "one full three-pack sequence" box. Add "(073, 075-077 are produced at §4.10; 074 is positional-historic)".

---

## WHAT THE S0-O3 SWEEP COULD NOT HAVE CAUGHT, AND WHY

The S0-O3 sweep's domain was: *every `$TRANS/` path, produced before it is read*. That relation is satisfied by **F1, F2, F3a-f, F4-F14**. Specifically:

- **F1/F2** — the consumed thing is a **test method name inside a suite**, not a `$TRANS/` artifact. `118-pinset-byte-pin.txt` is produced and consumed in the same block, so the producer/consumer graph is clean; the broken dependency is "does this symbol exist in the tree at this head", which the sweep does not model.
- **F3a-f** — the missing input is a **CLI flag** carrying a **custody-external** value (hC) and a custody-external file (the step-6 table). Neither is a `$TRANS/` path. Estate 6 found it only by executing.
- **F0** — the defect is that two distinct raise sites share one registry code; nothing about ordering of transcripts. Only reading `arm_readiness.py:4426-4465` surfaces it.
- **F13** — file line coordinates; no transcript involved, and the one mechanical check that touches them (§1.3's line audit) asserts only non-emptiness, so it is green over the wrong lines.
- **F4-F12** — prose, headings, die strings, a commit message, §5 boxes. No artifact edge at all.
- **F12** specifically is the sweep's blind spot in its purest form: 074 *is* produced before it is read, so the sweep passes; the defect is in what the §5 citation **claims** 074 evidences.

**Generalization:** three dependency kinds sit entirely outside the sweep — (i) symbol existence at a head (test methods, module constants), (ii) custody-external inputs and CLI flags, (iii) file line coordinates. A mechanical epoch-lint covering all three is what the next cut needs; a fourth producer/consumer sweep will return clean and find none of F0-F3.
