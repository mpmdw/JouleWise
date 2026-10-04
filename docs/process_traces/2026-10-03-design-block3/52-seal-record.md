# Seal record: registration G2A-25G83-B3 (G2-a prefill resolvability probe, measurement block 3)

Recorded 2026-10-03 by the block-3 design seat (Opus 5.5).

## The sealed text

- File: `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`
- **sha256 `84dd04268a2aed17118bd98b87c10ebe38e5f1bce2ea330a02048537b0342476`** (the arm recipe's
  `REG_SHA256`; step2 checks the file at H against this line).
- Gate: cold registration gate G2A-25G83-B3, judge Claude Fable 5.1, cold, detached worktree at
  `4add670b` (design branch merged with main `295fe151` = PR #465), on the draft with sha256
  `5c224a91…d426`: first line **`SEAL: ADMIT`** ([51-seal-ruling.md](51-seal-ruling.md); session
  output [51-judge-stdout.txt](51-judge-stdout.txt)).
- Refuter: Claude Opus 5.5, independent findings first: **`REFUTER G2A-25G83-B3: AGREE`**, provided
  its D1-D3 are applied ([51r-seal-refuter.md](51r-seal-refuter.md);
  [51r-refuter-stdout.txt](51r-refuter-stdout.txt)).
- Changes from the judged draft to the sealed text, all from the two records, nothing else: T1-T5
  verbatim; the judge's optional F11 wording (§4 item 3, a guard failure before attempt 2 aborts the
  member); the refuter's D3 (§4 "Why 300 s": a voided large-model member does not gate); the Status
  line.
- Recipe (`40-g2a-b3-arm-recipe.md`): R2 verbatim; R1 as replaced by the refuter's D1 (heading-bounded,
  exact ``- `path` `` match), which supersedes the judge's optional F9.
- Charge item 5 said "600 s"; that text was stale (the wait was changed to 300 s before the gate on
  the code seat's clock audit). The gate ruled on 300 s (ruling F7).

## Code conditions and where they are met

- Block 2's seal conditions C1/C2 (clock-anchor member rule; chain summary copy is a check) are in
  `scripts/harvest_g2a_window.py` unchanged since block 2, with the block-2 tests.
- The §4 wait: PR #465 (merge `295fe151`), tests `tests/test_controller_retry_backoff.py`
  (ordering, no wait at 0 or on an admitted attempt 1, abort on a second rejection, guard re-check
  after the wait, strict admission validation of a retried bundle, clock-anchor sizing),
  `tests/test_schemas.py` (field bounds, production digest unchanged), `tests/test_gen_g2a_window.py`
  (one `POLICY` export, span 18,868), `tests/test_harvest_g2a_window.py` (policy from the inventory
  for both blocks; refusal of a non-claim-grade policy). Judge: 555 tests run, all pass (ruling §2).

## Pins (registration §12)

H is the first main commit containing both PR #465 and this record (the RUN_STATE block-3 HANDOFF
names it). At H these files have these digests (computed at `295fe151`; the records PR that carries
this file changes no code and neither chain-source document):

| File | sha256 |
|---|---|
| `scripts/gen_g2_phase_d.py` | `4969ececa3c904ed855fe1d493ec72a1a401925d3be2bdfe24ad3059b94228eb` |
| `scripts/generate_g2a_probe_inputs.py` | `f50c5c572787800012ba87b7bbf31ca812f10c35619cdf59ef177d7918807a64` |
| `scripts/summarize_g2a_prefill_probe.py` | `cd89549f3884c189d54edb2edb9233f6b14dffd9635cf33eab2ffb2bac51221b` |
| `scripts/select_g2a_prefill_length.py` | `d4ab41ecb0343e9ed4e34335e15eb674f166c309b5401f42a5fb2a4cb49dba15` |
| `scripts/harvest_g2a_window.py` | `0bb7afc6cd8930e2428bb822b1efd38bbe37794156723944dd5774c93af69225` |
| `scripts/run_night.py` | `ed8d1ee08ac721b0d02488551b9a4c1108523a9f335d50dedc62566839aef11e` |
| `scripts/run_campaign.py` | `e31cffe7d470f28cbb24478338dabbeecf02dbef34b7dbe7862d40ac169201b6` |
| `joulewise/controller.py` | `a9db79c1b36284c56384e00abc1351225929d7cd8d01973895fba7e98f3a9a3c` |
| `joulewise/schemas.py` | `f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b` |
| `joulewise/environment_admission.py` | `acd8b507f82334912cb769ba374bddc9683bdd1dbcf0300d3096186a1235ff9c` |
| `configs/campaign_policies/quiet_mac_p2_g2a_b3.json` | `04bdbec45cf3b609b33886c1487e9982f030564b3212e636f8cf4631b5d4edc7` |
| `configs/model_panels/qwen3_4bit.json` | `78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a` |
| `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` | `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` |
| `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` | `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` |
| `docs/phase_2/window_runbook.md` | `9f896208b3bb7a62b427b277c585ada6c128f01ffd0a7dd5d884d0eba842d7ba` |
| `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` | `2db0df12cd7017b0276cf906a8f22b8aa26853d85f5b6b15797a43c50c0f814f` |

Derived at H: `NIGHT_PROGRAMMED_SPAN_S` = 18,868 s; `WINDOW_MAX_S` = 21,600 s. Ledger seed for
`b3w1`: `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2/derived/terminal-ledger.jsonl`,
sha256 `84bb9aee4a9358c13491832e12e9e504c02fb838d1a167974a235e8d2942475b`, head = committed pin 392.

## H′ extensions

none

## Open obligations (not text changes)

- **D-166 amendment** (ruling 3): the decision log's D-166 row carries the ruling's citable sentence
  (appended in the records PR that carries this file).
- **Desk-day issuer (judge F5, refuter D2).** The desk-day change to
  `scripts/issue_g2a_prefill_prompt_pin.py` must do both of the following, by a gated PR:
  (a) accept a selection record only when its sha256 equals `selection.sha256` in a block-3
  `harvest.json` with verdict SELECT; (b) under the end state, accept exactly the registration
  sha256 and the block's RECOVER `harvest.json` records and emit 4096, with no selection record and
  no "no rung qualifies" condition. Until it lands, no `_v5` pin is issued from any block-3 window.
- **Trade recorded (refuter D4):** the mechanical end-state trigger (T1) could end the block on a
  majority of non-`bounded` anchors caused by a removable code defect; that costs a selection,
  never a number or a window, and the mechanical trigger is worth it.
- Not adopted, nits: refuter D5 (§3 policy bullet names "the GPU idle check" and omits two guard
  fields; values unchanged, no rule effect); judge F10, F12 (carried, no rule effect).

Later windows append their H′ pins below, each under its own `## H′ n pins` heading, never inside
`## H′ extensions`.

## H′ 1 pins (2026-10-04, activation df31cb27): the `b3w1` re-harvest runs from H′ 1

H′ 1 = `18100c46ebbfab5e25038db0136d1a976de076cb` (merge of PR #467), listed under §12 (ii). `b3w1`
(plan `d117-g2a-prefill-probe-20261004T1305Z`, armed at H `abe759d3`) ran GO with chain exit 0. Its
first harvest (at H) returned RECOVER with the single cause `calibration_ledger_baseline_missing`.
`scripts/harvest_g2a_window.py` gave the bracket decision a ledger view whose baseline was the window's
seed head (392); `joulewise/calibration_bracketing.py` requires the acceptance's `ledger_cutoff`
(376), as every other caller supplies. This was the first G2-a window whose bracket session finalized.
PR #467 makes the harvest agree with §6 ("against the acceptance in force"), so the change is §11
code-agrees-with-text, with no erratum. Its gates: Sol executing review FAIL → F1 fixed → delta PASS;
cold Fable final pass PASS
(`docs/process_traces/2026-10-04-activation-df31cb27/21-fable-final-pass.md`).

Re-harvest (recipe §6 from a worktree at H′ 1, `--read-only-sources`, fresh root):
`~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json` sha256
`8fca2228d66b8acbe06c128b50ecc8bd5579f8fde859dd04ad7bf9d6e5a9e814`, verdict SELECT, selection record
`derived/selection.json` sha256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`.
Terminal ledger `derived/terminal-ledger.jsonl` sha256
`6ee89e5a1b83c88d865a65cca71177d19a4b23b47d6af2979f92a6840857530e`. Pin advance 392 → 402, head
digest `3ce1676c…0c08`, merged with this entry. The first harvest's record is kept as
`windows/d117-g2a-prefill-probe-20261004T1305Z/harvest-r1-recover.json` (sha256 `e7636ebb…2242`).
Before the re-harvest, the measurement clone's `configs/calibration/calibration_ledger_head.json` was
restored to its committed bytes. The first harvest had written its pin advance there, byte-equal to
that archive's `derived/terminal-pin.json` (`d399ed06…aa98`; a copy is preserved at
`~/night-archive/df31-preserved/`), and the uncommitted pin made the input check refuse. The clone's
HEAD never moved.

Pins at H′ 1:

| File | sha256 at H′ 1 |
|---|---|
| `scripts/harvest_g2a_window.py` | `0d8bc1274bd9e3222385b352fd7136281a73316bdeb90dda5269db9351d547ff` (changed by #467) |
| the other fifteen files in the table above | unchanged (re-verified at `18100c46`) |
