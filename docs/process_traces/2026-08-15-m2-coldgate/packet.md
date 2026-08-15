# REMANDED M-2 COLD-GATE PACKET — mechanically assembled 2026-08-15

Authority: council-verdict.md Disposition 2 (M-2 retroactive review REMANDED — the original
submission lacked primaries and the reviewed party wrote the charge sheet). This packet attaches
the primary record verbatim. The cold Fable §C analysis (cold-fable-ruling.md §C) is ADVISORY
INPUT only. Assembly is scripted extraction; zero magistrate prose beyond this header and the
question statement.

## THE QUESTION FOR THE PAIRING
(i) Was the M-2 override sound on the merits? (ii) Is the landed remedy sound given it shipped
forward-only (regeneration deliberately did not happen)? (iii) Does any reliance need re-review?
(iv) Standing: the override was ruled unilaterally despite rule-11's mandatory trigger (recorded
as cured-for-this-instance by the council; the pairing may affirm or dispute that cure).

## PRIMARY 1 — the M-2 ruling as entered (decision_log.md, verbatim)
```
**M-2 RULED (magistrate):** the frozen packs' `draft_status:
"unfrozen_draft"` and README "not armable" lines are GENERATOR-OWNED
DESCRIPTIVE TEXT that predates the freeze machinery; the freeze receipts
and plan-tree pins are the AUTHORITATIVE state. Remedy: the chain-fix
batch teaches the generators a freeze-aware status line (mirroring the
existing freeze-aware D-134 attachment handling) and regenerates the
sidecar-consistent text via the canonical path; until that lands, the
freeze receipt's presence governs and the §5C gate's placeholder-text
NO-GO reading is OVERRIDDEN for exactly this field by this ruling (scoped,
recorded — the packet cites it).

**M-2 EXECUTION NOTE (magistrate, 2026-08-15 — factual record per council-verdict R4;
the override's soundness is REMANDED to its own cold gate, see
docs/process_traces/2026-08-15-readiness-council/council-verdict.md Disposition 2):**
the remedy as ruled ("regenerates the sidecar-consistent text via the canonical path")
did NOT execute as written — #149 shipped freeze-aware status FORWARD-ONLY under
PRESERVE_CURRENT_FROZEN_BYTES, and the three frozen packs still carry
`draft_status: "unfrozen_draft"` at the audit baseline (verified by the cold
adjudicator and sweep-S3). Preserving frozen bytes was the correct engineering
call; the recorded consequence is that this ruling, scoped as transitional, is the
STANDING operative instrument for the current packs' lifetime: the freeze receipt's
presence governs, and the §5C placeholder-text NO-GO reading remains overridden for
exactly this field. Every arm packet must cite this ruling until the Phase-2
re-freeze regenerates truthful freeze-aware status text, at which point this
override RETIRES.
```

## PRIMARY 1b — the R4 execution note as entered (decision_log.md, verbatim)
```
**M-2 EXECUTION NOTE (magistrate, 2026-08-15 — factual record per council-verdict R4;
the override's soundness is REMANDED to its own cold gate, see
docs/process_traces/2026-08-15-readiness-council/council-verdict.md Disposition 2):**
the remedy as ruled ("regenerates the sidecar-consistent text via the canonical path")
did NOT execute as written — #149 shipped freeze-aware status FORWARD-ONLY under
PRESERVE_CURRENT_FROZEN_BYTES, and the three frozen packs still carry
`draft_status: "unfrozen_draft"` at the audit baseline (verified by the cold
adjudicator and sweep-S3). Preserving frozen bytes was the correct engineering
call; the recorded consequence is that this ruling, scoped as transitional, is the
STANDING operative instrument for the current packs' lifetime: the freeze receipt's
presence governs, and the §5C placeholder-text NO-GO reading remains overridden for
exactly this field. Every arm packet must cite this ruling until the Phase-2
re-freeze regenerates truthful freeze-aware status text, at which point this
override RETIRES.
```

## PRIMARY 2 — the overridden §5C gate text (window_runbook.md:265-290, verbatim)
```

The freeze update to `plan_tree.json` uses the pack generators' established
two-space, insertion-order JSON rendering. This is an intentional,
load-bearing byte contract, not an oversight: changing it to sorted-key
rendering would make the matching pack generator's post-freeze
`generate_configs.py --check` disagree with the frozen bytes. Do not “tidy”
that serialization.

For the three packs frozen on 2026-08-13, the committed D-134 freeze receipt
and its plan-tree pin are authoritative over the legacy `unfrozen_draft`
wording that remains byte-frozen in `draft_status` and `README.md`. Do not
repair those committed bytes. The 2026-08-14 M-2 ruling in
`docs/decision_log.md` requires the generators to emit freeze-aware status and
README text only for future regenerated packs while preserving current-pack
`--check` byte identity.

After the freeze changes and every other pack byte are reviewed and
committed, the final pack digest is
`joulewise.committed_pack_tree_sha256.v1`. It is the SHA-256 of this exact
framing:

```text
b"joulewise.committed_pack_tree_sha256.v1\n" +
for each committed file, sorted by raw UTF-8 path bytes:
  relative_path + NUL + git_mode + NUL + byte_length + NUL +
  lowercase_sha256_of_file_bytes + LF
```

## PRIMARY 3 — the #149 remedy code (generator freeze-aware status, verbatim)
#149 merge commit stat (ac3fe1d):
```
ac3fe1d Readiness tooling: registry reconciliation + arm-time evidence author + chain-fix batch (union of #146/#147/#148 + integration fixes) (#149)
 .../generate_configs.py                            |  121 +-
 .../d117_floor_qwen25_1p5b_v1/generate_configs.py  |  147 +-
 .../d117_floor_qwen25_7b_v1/generate_configs.py    |  146 +-
 docs/phase_2/alpha_arm_readiness.md                |   16 +-
 docs/phase_2/three_night_freeze_manifest.md        |   15 +-
 docs/phase_2/window_runbook.md                     |  208 +-
 joulewise/arm_readiness_evidence_t0.py             | 2043 ++++++++++++++++++++
 scripts/author_arm_evidence_t0.py                  |   86 +
 scripts/ed_session/rail-probe.sh                   |  224 +++
 scripts/ed_session/sampler-checklist.sh            |  144 ++
 scripts/prew
```
generator freeze-aware sites:
```
146-    "74ccdaec74497c3aa7c074ef1129ec2bf2cc01d8ac14d3d07be77ab468599688"
147-)
148-
149:def freeze_aware_status(freeze_reference: object) -> str:
150-    """Return future-pack status without rewriting the 2026-08-13 frozen bytes."""
151-
152-    if not isinstance(freeze_reference, dict):
153-        return DRAFT_STATUS
154-    if freeze_reference.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256:
155-        return DRAFT_STATUS
156-    return FROZEN_STATUS
157-
158-
159-ARM_READINESS_ATTACHMENT = plan_arm_readiness_attachment(
160-    REPO_ROOT / PACK_REL,
161-    "ALPHA",
162-    REPO_ROOT,
163-)
164-_FREEZE_REFERENCE = ARM_READINESS_ATTACHMENT["freeze_receipt"]
165-PRESERVE_CURRENT_FROZEN_BYTES = (
166-    isinstance(_FREEZE_REFERENCE, dict)
167-    and _FREEZE_REFERENCE.get("sha256") == CURRENT_FROZEN_RECEIPT_SHA256
168-)
169:PACK_STATUS = freeze_aware_status(_FREEZE_REFERENCE)
170-
171-
172:def freeze_aware_projection(generated: dict[str, Any]) -> dict[str, Any]:
173-    if not PRESERVE_CURRENT_FROZEN_BYTES:
174-        return generated
175-    current = json.loads(
176-        (REPO_ROOT / PACK_REL / "producer_contract.json").read_text(
177-            encoding="utf-8"
178-        )
179-    )
180-    return current["identity_pin_projection"]
181-
182-
183-SUCCESSOR_REGENERATION_RULE = (
184-    "A successor acceptance artifact issuing before arm REQUIRES pack regeneration "
185-    "(packs are unfrozen drafts; the D-125 lineage-envelope alternative is recorded "
186-    "as a freeze-time lead decision)."
187-    if PACK_STATUS == DRAFT_STATUS
188-    else "A successor acceptance artifact issuing before arm REQUIRES a newly "
189-    "generated and newly frozen pack; the D-134 freeze receipt is authoritative."
190-)
191-
192-MODEL = {
193-    "name": "Qwen2.5-1.5B-Instruct-4bit",
194-    "family": "qwen2.5",
195-    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit",
196-    "revision": "8b403126fc14f14cfc99bb4cfa72ecbc129ea677",
197-    "weight_format": "mlx",
--
708-    )
709-
710-
711:def freeze_aware_reservation_plan_arguments(
712-    preserve_current: bool,
713-) -> list[dict[str, str]]:
714-    if preserve_current:
715-        return []
716-    return [literal("--plan"), repo_path(PACK_REL / "calibration_plan.json")]
717-
718-
719-def stage_graph(
720-    stage_manifest_refs: dict[str, dict[str, Any]],
721-    external_inputs: dict[str, dict[str, Any]],
722-) -> list[dict[str, Any]]:
723-    bracket_args = [
724-        literal("--ledger"), binding("ledger_path"),
725-        literal("--head-pin"), repo_path(LEDGER_HEAD_REL),
726:        *freeze_aware_reservation_plan_arguments(PRESERVE_CURRENT_FROZEN_BYTES),
727-        literal("--session-id"), binding("bracket_session_id"),
728-        literal("--window-id"), tree_pointer("/window_identity/window_id"),
729-        literal("--plan-id"), tree_pointer("/plan/plan_id"),
730-        literal("--plan-sha256"), tree_pointer("/plan/actual_sha256"),
731-        literal("--evidence-root-id"), tree_pointer("/window_identity/evidence_root_id"),
732-        literal("--runs-root"), binding("claim_runs_root"),
733-        literal("--pre-attempt-id"), binding("pre_attempt_id"),
734-        literal("--post-attempt-id"), binding("post_attempt_id"),
735-        literal("--pre-custody-locator"), binding("pre_calibration_dir"),
736-        literal("--post-custody-locator"), binding("post_calibration_dir"),
737-        literal("--identity-epoch-json"), binding("identity_epoch_json"),
738-        literal("--t1-bindings-json"), binding("t1_bindings_json"),
739-        literal("--execute"),
740-    ]
741-    capture_common = [
742-        literal("--allow-live"),
743-        literal("--output-root"), binding_path("claim_runs_root", "instrument_validation"),
744-        literal("--session-id"), binding("bracket_session_id"),
745-    ]
746-    pre_capture = capture_common + [
747-        literal("--slot"), literal("pre"),
748-        literal("--attempt-id"), binding("pr
```

## PRIMARY 4 — current pack bytes at HEAD (verbatim)
```
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:3:  "draft_status": "unfrozen_draft",
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/calibration_plan.json:3:  "draft_status": "unfrozen_draft",
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/consumer_family_declaration.json:3:  "draft_status": "unfrozen_draft",
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/order_manifest.json:3:  "draft_status": "unfrozen_draft",
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/plan_tree.json:780:  "draft_status": "unfrozen_draft",
configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/plan_tree.json:949:    "draft_status": "unfrozen_draft",

```

## PRIMARY 5 — L5 seat finding (verbatim excerpt)
```
pair discharges the validator role") reads as if the existing receipt carries over; it does not.

**F-4 NIT** — `--check` prints "verified **unfrozen draft**" on frozen packs (`generate_configs.py:149-157,2168-2171`; M-2-acknowledged byte-preservation cosmetics).

**F-5 NIT** — decision-log M-2 remedy wording ("regenerates the sidecar-consistent text") vs the implemented preserve-bytes behavior; `alpha_arm_readiness.md:31-35` states the operative reading. Consistency-sweep material so a future s
```

## PRIMARY 6 — sweep-S3 (verbatim)
```
### S3. The decision log's M-2 remedy describes a regeneration that deliberately did not happen
- `docs/decision_log.md:8881-8893` — "Remedy: the chain-fix batch teaches the generators a freeze-aware status line … **and regenerates the sidecar-consistent text via the canonical path**; until that lands, the freeze receipt's presence governs". Truth: the shipped behavior is forward-only — `configs/campaigns/*/generate_configs.py` gained `freeze_aware_status()` but runs under `PRESERVE_CURRENT_FROZEN_BYTES`, so the frozen packs still read `"draft_status": "unfrozen_draft"` (`calibration_plan.json:3`) and "The pack is not armable." (`README.md:5`). That resolution is recorded in `docs/phase_2/alpha_arm_readiness.md:30-35` and RUN_STATE.md:55-56 but **not** in the policy home. **Fix:** append a one-line M-2 execution note: forward-only; the frozen packs' legacy wording is permanently overridden by the freeze receipt.
```

## ADVISORY INPUT — cold-fable-ruling.md §C (already custodied; the pairing reads it AFTER forming its own view)
Path: docs/process_traces/2026-08-15-readiness-council/cold-fable-ruling.md §C