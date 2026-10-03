# Seal record: registration G2A-25G83-B2 (G2-a prefill resolvability probe, measurement block 2)

Recorded 2026-10-02 by the block-2 design seat (Opus 5.5).

## The sealed text

- File: `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md`
- **sha256 `8e45a0e0f7ac7431c809ac780954308e7df813e57d6c4c2643641d0c5bcda5b8`** (the arm recipe's
  `REG_SHA256`; step2 checks the file at H against this line).
- Gate: cold registration gate G2A-25G83-B2, judge Claude Fable 5.1, cold, detached worktree at
  `e8681d61` (design branch `cd71d2cf` merged with PR #458 head `8a8635a7`), on the draft with
  sha256 `2188e0e6…a78d`: first line **`SEAL: ADMIT`** ([51-seal-ruling.md](51-seal-ruling.md);
  session output [51-judge-stdout.txt](51-judge-stdout.txt)).
- Refuter: Claude Opus 5.5, independent findings first: **`REFUTER G2A-25G83-B2: AGREE`**
  ([51r-seal-refuter.md](51r-seal-refuter.md); [51r-refuter-stdout.txt](51r-refuter-stdout.txt)).
- Changes from the judged draft to the sealed text, all from the two records, nothing else:
  T1-T8 verbatim (T2a: the chain is unchanged, so a failed large-model stage ends the window
  RECOVER); the refuter's D1 replacement for T6's third sentence (every later window, not only a
  recovery window, may use a head H′); the judge's two optional nits F12 (worked example states
  100 ms records) and F13 ("refusal reason code in the driver's result record"); the Status line.

## Code conditions (ruling §5) and where they are met

- **C1** (a member is valid only with `uncertainty_evidence.clock_anchor.status == "bounded"`) and
  **C2** (the chain's summary copy is a check; byte equality only when every member is valid):
  PR #458 commit `d5b28bb8`, tests in `tests/test_harvest_g2a_window.py`:
  `test_c1_clock_refused_small_members_are_invalid_and_window_recovers`,
  `test_c1_missing_anchor_record_is_invalid`, `test_c1_clock_refused_large_member_leaves_select`,
  `test_c1_low_count_with_bounded_anchor_stays_valid`,
  `test_c2_chain_copy_with_invalid_small_member_recovers_not_refused`,
  `test_c2_chain_copy_with_invalid_large_member_selects`, `test_c2_chain_copy_equal_when_all_valid`;
  T8's capture class: `test_t8_capture_made_is_recorded_from_the_archive_copy`,
  `test_t8_capture_file_under_raw_sets_capture_made`. 30 tests, OK (lead, 2026-10-02 21:30 PDT).

## Pins (registration §12)

H is the first main commit containing both PR #458 and this record (RUN_STATE's block-2 HANDOFF
names it). At H these files have these digests (computed from PR #458 at `d5b28bb8`; later
commits in that PR touched tests and records only; re-verified by the lead after #458 merged as
`08de38b9`, on this branch merged with it, all nine equal; the arm's step2 re-hashes what it needs
at H):

| File | sha256 |
|---|---|
| `scripts/gen_g2_phase_d.py` | `69903ae27ea01e40e311a157feac36edb4e2fddff052246cca712b3f0915ad16` |
| `scripts/generate_g2a_probe_inputs.py` | `f95570f7e070fd87e5f03d251dcd1221ae3f1be180b417185793590bae91efcf` |
| `scripts/summarize_g2a_prefill_probe.py` | `b14bd5b1b4ba6f21e4c396918c00c7e50b8ae128b7e6cbe799be2f0215da03e1` |
| `scripts/select_g2a_prefill_length.py` | `d4ab41ecb0343e9ed4e34335e15eb674f166c309b5401f42a5fb2a4cb49dba15` |
| `scripts/harvest_g2a_window.py` | `ed490aab5a68c5f3f0e4b17558bbc9a495e8b030c6540938ffced4856cebabb6` |
| `scripts/run_night.py` | `ed8d1ee08ac721b0d02488551b9a4c1108523a9f335d50dedc62566839aef11e` |
| `configs/model_panels/qwen3_4bit.json` | `78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a` |
| `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` | `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` |
| `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` | `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` |

Span literal at H: `NIGHT_PROGRAMMED_SPAN_S = 17248`; `WINDOW_MAX_S = 19980`. Ledger seed at H:
the Revision 6 C2 clone ledger, sha256 `3c9b6844…72fb`, 376 records, pin sequence 376.

Later windows append their H′ pins below (registration §12, T6 with D1).

### H′ 1 (2026-10-03, activation b07f1ebf): `w1` itself arms from H′

H′ = `0fbadb63945dab8c6b24427f0c76b80762734776` (merge of PR #460). The first `w1` arm attempt
(t0 1791013320, plan `d117-g2a-prefill-probe-20261003T0742Z`) stopped at recipe step2 before anything
was published: the generator doubled the plan-id suffix of `G2A_ROOT`, so the chain would have refused
at its input assertions. PR #460 fixed this (Sol executing review PASS, Fable final pass PASS), and the
cold Fable ruling `docs/process_traces/2026-10-03-activation-b07f1ebf/31-fable-s12-ruling.md` classified
it as a §11 fix: RULING EXTEND-SEAL-WITH-H-PRIME, no new seal. So `w1` is armed from H′, not from H.

Pins at H′ (re-verified against the table above at `0fbadb63`):

| File | sha256 at H′ |
|---|---|
| `scripts/gen_g2_phase_d.py` | `76a7f043558df361b5ab191d5b3cdc327f39e0c702599fed6faac925243c7c46` (changed by #460) |
| the other eight pinned files | unchanged from the table above |
| `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md` | `8e45a0e0f7ac7431c809ac780954308e7df813e57d6c4c2643641d0c5bcda5b8` (unchanged) |

The arm head may be a later main commit that differs from H′ by records only; the arm record names it.

## Disclosures

1. **D2 (refuter): no real member bundle at H has been shown with a `bounded` clock anchor.** C1
   makes a member valid only when its stored anchor is `bounded`. The refuter found 271 retained
   real bundles under the older envelope method, all `bounded`, and no real member bundle under the
   method the members use at H. This seat may not run a capture (no powermetrics), so the first
   window is the test. If its RECOVER cause is that most members' anchors are not `bounded`, the
   arm recipe (§7) stops the block and sends it to a consult instead of arming `w2`, so at most
   one window can be spent on this.
2. #416 pre-arm triple audit: not triggered (registration §9; amended directive: before any
   claim-bearing run). The judge could not verify the directive's wording without reading memory
   and marked that sentence unverified by the gate; the claim boundary of §9, which the judge
   confirmed, is what makes the block diagnostic.
3. The gate ran while PR #458's executing review was in flight; the review then returned MERGE
   with one doc finding (fixed), and the lead commits after the judged head (`4cacd72b`, `d5b28bb8`)
   are the ruling's own conditions plus the staged-plan authoring fence; both were reviewed by a
   Sol delta review and the cold Fable final pass on PR #458 (records 32, 36).
