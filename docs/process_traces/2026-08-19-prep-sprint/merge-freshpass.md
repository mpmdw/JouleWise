# Fresh-pass pre-merge review — impl/r2-s0-mint-resolver

**Range reviewed:** `d59d36f..4597ad4` as assigned, **extended to `b92b43d`** (see B2).
**Worktree:** `/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0`
**Mode:** READ-ONLY. Nothing modified. Working tree clean throughout.
**Date:** 2026-08-19

---

## Verdict

**The claim-bearing work is clean.** Classes 1 and 2 — the three identity-pin
projection freezes, the three `freeze-0003` mints, and the confirmation table —
verify completely against recomputed primary evidence with **zero findings**.
Every digest asserted anywhere in the range was recomputed independently and
matched.

**All findings are in classes 3 and 4** (bookkeeping and authority docs). Two are
blockers, both cheap to fix, and neither touches a receipt or a digest. One is a
genuine hazard for an autonomous successor; one is a gate-record scope defect.

---

## Class 1 — S5 mint commits: VERIFIED CLEAN

Commits `3d05982`, `6fd8bce`, `74632e3` (projections) and `5e38f1e`, `eb7f6c6`,
`94dc3b3` (freezes).

### Per-receipt verification (all three packs)

| Check | 1p5b | 7b | contrast |
|---|---|---|---|
| `receipt_id` = `freeze-0003` | PASS | PASS | PASS |
| `status` = `PASS` | PASS | PASS | PASS |
| `pack_root` path-bound to `/Users/edr/JouleWise-measurement-20260818/...` | PASS | PASS | PASS |
| predecessor names the corresponding `_v2` pack | PASS | PASS | PASS |
| predecessor `freeze_receipt.sha256` = specified value | PASS | PASS | PASS |
| no `supersedes` key | PASS | PASS | PASS |
| `.sha256` sidecar = recomputed digest | PASS | PASS | PASS |

Recomputed freeze-0003 digests (`shasum -a 256`), each matching its sidecar:

- 1p5b `0abfddb13fe8c5e69df3e6be5e2e7efe28d3690b6947d5ed850fcb9652f6ec64`
- 7b `f232d076d54408851e5728b3f14e9b04e086d809bca3e1cdac0c3641e072578c`
- contrast `f32bd3a8e4dbd04bc5b1635818ba34394984d1d201d16f02efc21f0b01f31c73`

Predecessor `freeze_receipt.sha256` values match the three specified digits-for-digit,
**and** match a fresh `shasum` of the actual `_v2` receipt files on disk:

- `configs/campaigns/d117_floor_qwen25_1p5b_v2/arm_readiness.freeze.receipts/freeze-0002.json` → `1277103b4209…b89666` ✓
- `configs/campaigns/d117_floor_qwen25_7b_v2/arm_readiness.freeze.receipts/freeze-0002.json` → `decd8cdc6a58…1842d0` ✓
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/arm_readiness.freeze.receipts/freeze-0002.json` → `18855647c38e…f9607e` ✓

The predecessor blocks also carry `identity_receipt.sha256` and `pack_sha256`.
Both were recomputed and both match — the `pack_sha256` values via
`joulewise.arm_readiness.committed_pack_tree_sha256` on the `_v2` roots
(`95f7c51c…`, `e5ec0f74…`, `2fe51b03…`). No unverified predecessor field remains.

`supersedes` appears nowhere in any `freeze-0003.json`. (It occurs elsewhere in
the pack dirs — `generate_configs.py`, `plan_tree.json`, `producer_contract.json`,
`projection-0001.json`, contrast `README.md` — which is expected and unrelated.)

### Scope containment

`git diff --name-status` per commit confirms **nothing outside the three `_v3`
pack dirs changed** in any of the six mint commits. No stray doc, test, or
config edit rode along.

### plan_tree / producer_contract deltas are exactly the attachments

The raw diffs are alarming — up to 7,103 changed lines on a file whose byte
length moves by ~530. **This is pure canonicalization, not content churn.** The
freeze tooling re-emits `plan_tree.json` with sorted keys; the pre-freeze file
was in insertion order (`"schema_version"` first → `"acceptance_policy"` first).

I parsed before/after JSON and diffed order-insensitively. The complete semantic
delta per commit:

**Projection commits** — `arm_attachments/identity_pin_projection`:
`state` `"unprojected"` → `"frozen"`; `projection_receipt` `null` → dict; and per
identity unit, `config_set_sha256` / `model_artifact_sha256` /
`runtime_identity_sha256` `null` → str. That is 2 units (1p5b, 7b) and 4 units
(contrast). The two floor packs additionally update
`downstream_contract/producer_contract/sha256`, with the identical change
mirrored into their `producer_contract.json`.

**Freeze commits** — exactly one key each:
`arm_attachments/arm_readiness/freeze_receipt` `null` → dict.

**No other semantic change in any file.** This satisfies "deltas are exactly the
projection/freeze attachments."

### Asymmetry checked and cleared

`74632e3` did not touch a `producer_contract.json` for the contrast pack while
the two floor commits did. **Not a defect:** the contrast pack has no
`producer_contract.json`, in `_v3` *or* `_v2`, and its `downstream_contract` is
`"binding_mode": "declaration_only"` (analysis manifest + consumer family
declaration only). Structural, not a regression.

### Additional integrity checks (not requested, run anyway)

- Every `plan_tree.sha256`, `projection-0001.sha256`, and
  `freeze-0003.json.sha256` sidecar matches its file at HEAD.
- `plan_tree.downstream_contract.producer_contract.sha256` equals the actual
  `producer_contract.json` digest on both floor packs.
- The `freeze_receipt` and `projection_receipt` blocks embedded in each
  `plan_tree.json` carry shas equal to the actual receipt files.
- `pack_identity.plan_sha256` equals a fresh hash of `calibration_plan.json`,
  and equals `plan.actual_sha256` in `plan_tree.json`, on all three packs.
- All 11 D-134 evidence receipts per pack are present, `PASS`, and digest-match
  their referenced files. 11 × 3 = the documented **33**. (The freeze receipt's
  `evidence` array holds 12 entries per pack: the 11 plus the U11 projection
  receipt — the "33" figure is correct as a count of S4-authored evidence.)
- Row registry sha matches `configs/arm_readiness/d117_row_registry_v1.json` on
  all three; 14 rows each, 13 `PASS` + 1 `NOT_APPLICABLE`
  (`desk.acceptance_successor`), `refusals: []`, profiles ALPHA/BETA/GAMMA.

---

## Class 2 — Confirmation table: VERIFIED CLEAN

`docs/process/ed-s5-mint-decision-2026-08-19.md`, table under "Confirmation
table (COMPLETE …)".

Receipt shas — all three equal my recomputed file digests (values above). ✓

Committed tree digests — recomputed at HEAD via
`joulewise.arm_readiness.committed_pack_tree_sha256`, which is HEAD-bound and
cross-checks git against disk:

| Pack | Table | Recomputed |
|---|---|---|
| 1p5b | `1e3f1fa31027e57053c7d26bacf2f373cf2c9ed840ee2bb3befafd99302d63f6` | identical |
| 7b | `6d0b9b758d6a37a69a88827cb47ac58566d957099a3e714143d2e6508a93e45f` | identical |
| contrast | `0d07194143702b266267f0faa7b051695ffb5e1c56dc7a69d0b2dca8aaa883ef` | identical |

The digests are stable from `94dc3b3` through `b92b43d` — no pack byte moved
after the last mint. The table is safe to publish as-is.

The r6/r5 acceptance shas (`0227bca3…`, `92b9c060…`), the two moved r6 pins, and
the 99-row S4 manifest were independently confirmed. Only the S4 evidence rollup
digests (`0e353456…` / `1421ea4e…` / `653f22c0…`) are truncated in the table and
were not expanded — they are cited as "full manifest in session custody."

---

## BLOCKERS

### B1 — The kernel says the canonical run is in flight; RUN_STATE says it was killed

`docs/process/state_kernel.json`, task `REFREEZE-D147-CLOSE`:

> `"status_note": "S0-S5 executed 2026-08-19; freeze-0003 x3 minted and landed (8b2b021); r6 live; canonical at the frozen head in flight"`

`RUN_STATE.md:133-135`:

> "the final-canonical run and the fresh-pass reviewer were killed mid-run — **BOTH GATE INPUTS ARE UNSATISFIED** and must be rerun from scratch"

The row was written in `75cb868`, before the stop. `881e1bd` and `c00c7bb`
recorded the stop in RUN_STATE only; the kernel row was never corrected.

This matters because RUN_STATE itself names the kernel the authority for work
selection, and D-149 just made the window lane self-starting. A `/loop`
successor that selects work from the kernel is told gate input 1 is already
running and will not rerun it. Fix the `status_note` before merge.

### B2 — The pinned fresh-pass range omits the governance commit, and HEAD moved during review

Two coupled scope defects.

**(a) Range disagreement.** `RUN_STATE.md:143` pins gate 2 to
`d59d36f..75cb868`. `RUN_STATE.md:29` and `:90` (T15-PREP, T14-GO) both say
`d59d36f..HEAD`. Under the narrow formulation, `0e96dbb` — the D-149 commit that
rewrites three kernel fences and changes T-0 GO authority for all three
claim-bearing windows — is **outside the fresh-pass range**. It is also outside
the D-144 seat pass, which
`docs/process_traces/2026-08-19-r1-r2-codesign/16-d144-seatpass-packet.md:11-12`
scopes to `joulewise/ scripts/ configs/ tests/` with "docs/ and RUN_STATE
excluded — covered by the fresh-pass gate." `state_kernel.json` lives under
`docs/`. Neither gate covers it.

**(b) Post-review commit.** HEAD was `4597ad4` when this review began and
`b92b43d` when it ended — `b92b43d` "Shakedown-v3 first-light run card (prep item
6b)" landed mid-pass, at 18:50. Rule-4's gate shape requires a fresh pass over
any post-review commit.

I extended coverage to both. **`0e96dbb` and `b92b43d` are substantively clean**
(`b92b43d` is a docs-only run card; its quoted r6 band literals
`[0.02317490442656863, 0.03289849371536248]` are exactly the r6 artifact's
17-member min/max). The blocker is the **gate record**, not the content: correct
the pinned range to `d59d36f..b92b43d` and reconcile the three formulations
before recording gate 2 as satisfied, or the merge is logged as reviewed over a
range that excludes a governance change to claim-window authority.

---

## SHOULD-FIX

### S1 — Kernel window rows name two pack generations at once

`75cb868`'s message says "window rows -> _v3", but only
`acceptance.evidence[0]` moved. At HEAD each of `D117-W-ALPHA` / `-BETA` /
`-GAMMA` still reads:

> `"goal": "Run the frozen ALPHA pack d117_floor_qwen25_1p5b_v1 …"`

against `"…d117_floor_qwen25_1p5b_v3 is used only after council READY…"` in the
same row. The binding gate text is right and the human-facing selection text is
wrong. This propagates verbatim into `TASK_QUEUE.md:527-529` and `:616-618`.

### S2 — Window row status_notes still demand the re-freeze that just executed

Same three rows: "council Phase 2 requires **the ruled successor re-freeze**
before the re-audit and READY-candidate sitting." Executed and landed.

### S3 — `WINDOW_STATUS.md` hazard banner is stale and warns against a satisfied condition

`WINDOW_STATUS.md:2-5` still reads "**Do not reboot before the S5 freeze-0003
mints land**" and gives an expiry of ~2026-08-20T16:51Z. The mints landed.
`| Updated | 2026-08-17` is two days stale. `75cb868` did not touch this file.

### S4 — README banner contradicts the blurb four lines below it and breaks the plain-language bar

The new blurb itself is acceptable — plain, physical, no bare decision IDs. But
`README.md:12-19`, untouched, still says:

> "**🟡 MACHINE: BETWEEN RUNS — D-117 pre-window state.** … Current work is the
> **ten-item U1-U10 instrument-readiness repair path**"

"U1-U10" and "D-117 pre-window state" are internal shorthand on the
advisor-facing surface, and the U1-U10 path is not current work. This is
consistency-sweep item **S2** at
`docs/process_traces/2026-08-19-refreeze-execution/reports/consistency-sweep.md:190`
("README banner names a superseded work program") — `75cb868` applied S1 and
skipped it.

### S5 — README "Next:" understates the gate count

`README.md:41-42`: "**Next:** merge the transaction to main (gates are
green-pending the final full-suite run)". Written 17:37; by 17:40 T13-STOP had
both gate inputs killed and had added a third gate (the D-144 seat pass, "a
ruled requirement … not optional"). Reads as one run from merge; the tree says
three unsatisfied gates.

### S6 — Test-pin arithmetic comment now contradicts its own assertion

`tests/test_gen_state.py:278-287`. The comment still derives
"73 - 1 = **72** exact live records" immediately above
`self.assertEqual(len(self.tasks), 73)`. The pin change is otherwise **exactly
additive** as specified — one `EXPECTED_IDS` entry, the count bump, and the
active-row normalization in `_kernel_with` — and I confirm
`scripts/gen_state.py --check` exits 0 and `tests.test_gen_state` runs 40 tests
OK at HEAD. Only the comment needs the `+ REFREEZE-D147-CLOSE = 73` term.

### S7 — RUN_STATE never records the pause; T15-PREP still advertises live work

`RUN_STATE.md:13` "T15-PREP active — prep sprint running", `:15` header "**ACTIVE
NOW**", items 3 and 6 shown `[assembling]` — yet `4597ad4` ("…before pause") and
`b92b43d` landed items 3, 6 and 6b. To be precise: **no prep item is falsely
claimed done**; items 4, 5, 7 are absent from the tree and absent from any
done-claim. The defect is the inverse — completed items shown in progress under
an "active" header.

### S8 — T13-STOP's unqualified stop order carries no supersession pointer

`RUN_STATE.md:123`: "**NOTHING IN FLIGHT; RESUME ONLY ON ED'S EXPLICIT GO**".
T14-GO, 60 lines above, issues that go. Newest-first ordering makes this
chronologically coherent, but the file's own convention for exactly this case
(`RUN_STATE.md:477`, "superseded by T9 above; kept as record") is not applied —
and this file's stated job is to orient a cleared-context successor.

### S9 — Gate count disagrees across three documents

T14-GO (`RUN_STATE.md:89-93`) enumerates **three** gate inputs. T15-PREP `:60`
says "all **four** gates (T14-GO item 1)". T13-STOP `:140-150` numbers 1-3 as
gates with 4 being the merge wave itself. The miscount propagates into
`16-d144-seatpass-packet.md:7` — "merge gate **3 of 4**".

### S10 — D-149's decision-log entry never points at the template it makes authoritative

`docs/process/d149-go-receipt-template.md:66` asserts "The template is
authoritative either way (D-149)", but the D-149 body in `docs/decision_log.md`
names no ONE-home path — unlike every neighbour (D-146/D-147 cite
`docs/process_traces/…`; D-143/D-144/D-145 all cite custody). The template
landed 22 minutes after the decision entry and nothing links them. The D-149
entries are otherwise correctly formatted for the file.

---

## NITS

- **N1** — The 7,100-line `plan_tree.json` diffs are key re-sorting, not content
  (verified above). Worth a note in the tooling docs: freeze re-emits canonical
  JSON, so mint diffs are not eye-reviewable and must be checked semantically.
- **N2** — `docs/run_reports/2026-08-19-t12-t13-session.md:26-27` says the
  co-design custody dir holds "15 files"; `4597ad4` made it 16 without updating
  the count. Separately `docs/decision_log.md`'s D-144 body says "14 files" — two
  behind, and that one is standing policy rather than a point-in-time record.
- **N3** — Run report line 34 labels `8018a4b` as "S0 resolver/kernel"; `8018a4b`
  is "S0 fix round 1" and the kernel commit is `cef3306`. Defensible as the stage
  head, reads as the kernel commit.
- **N4** — Run report canonical addendum is an unfilled placeholder (lines
  118-121), honestly flagged in T13-STOP `:153-154`. Bookkeeping debt, not a
  false claim.
- **N5** — `d149-go-receipt-template.md:6-7` says the five conditions are the
  D-149 index row's "**verbatim** in order" — they are faithful paraphrases,
  correct in substance and order. Line 23 calls the 6-h horizon "procedural"
  where the code constant is `_NONVOLATILE_EVIDENCE_VALIDITY_NS`.
- **N6** — The deferred D-149 evaluator script **is** durably recorded
  (`d149-go-receipt-template.md:63-66`, not commit-message-only), but it sits in
  no queue: T15-PREP item 6 asked for "script + receipt template", only the
  template landed, and there is no `TASK_QUEUE.md` or kernel row for the script.
  Nothing will schedule it.
- **N7** — D-149's three fences moved their authority pointer from a specific
  council-verdict file to `docs/decision_log.md`, a ~9,000-line file, while the
  fence rule text still requires "a READY-candidate council verdict" whose
  custody pointer is now gone.
- **N8** — `16-d144-seatpass-packet.md:13` names `d10881b` as the merge head at
  assembly time when HEAD was already `79a4cd0`; self-correcting ("use the live
  head") but stale on arrival. Its pool time "(23:34 PST)" disagrees with
  T13-STOP `:148` / T14-GO `:87` / T13 `:183`, all ~23:22. Substantively the
  packet faithfully implements T13-STOP item 3, and custody numbering 01..16 is
  contiguous with 16 the correct next index.
- **N9** — `docs/process/ed-s5-mint-decision-2026-08-19.md:24` says "**RULED
  (D-148.1): Option 2**"; `docs/decision_log.md:171` records "S5 mint route =
  **OPTION B**", and the packet's own fallback list is numbered `1.` then `3.`
  with no option 2. D-148 *is* recorded (index row + body, landed in `d59d36f`,
  one commit before the range); the `.1`–`.7` sub-numbering used throughout
  RUN_STATE and the kernel is never defined in the log, which writes `(1)…(7)`.
- **N10** — `README.md:45-46` has no blank line between the blurb and `## Current
  State`. Pre-existing, not introduced here.

---

## Confirmed-correct claims (recomputed, worth recording)

- "NO MERGE HAS OCCURRED" ✓ — `8b2b021` is not an ancestor of `origin/main`;
  `75cb868` exists only on this branch.
- T14-GO's allowlist claim ✓ — `/Users/edr/code/JouleWise/.claude/settings.local.json`
  carries the entries T14-GO says Ed added.
- D-149 template ↔ decision log: C1–C5 map 1:1 onto the five index-row
  conditions; the 20-min / 6-h horizons match
  `joulewise/arm_readiness_evidence_t0.py:49-50` exactly.
- "3,755 ran … one bookkeeping red" ✓ against
  `suite-logs/canonical-6f00d05.log` (`Ran 3755 tests`, `FAILED (failures=1,
  skipped=95)`).
- "836→~1,440 lines" guide growth ✓ (836 pre-`3efea49`, 1446 now); consistency
  sweep M1..M9 ✓; D-148.6/.7 at `CLAIMS_STATUS.md:10-11` ✓.
- `scripts/gen_state.py --check` exits 0 at HEAD; `tests.test_gen_state` 40/40 OK.
