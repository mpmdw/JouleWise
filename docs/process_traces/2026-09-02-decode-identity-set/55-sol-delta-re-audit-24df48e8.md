# Delta re-audit of 24df48e8 (Sol xhigh + wrapper replay), verbatim

Replay complete. All three of Sol's load-bearing claims reproduce from the worktree. Report follows.

## Delta re-audit of 24df48e8 — Sol xhigh (read-only) + lead replay

**Route:** project MCP `codex`, model `gpt-5.6-sol`, effort `xhigh` (requested tier = applied tier; trigger: adversarial review with code-read factual claims), sandbox `read-only`, `on-request`, reverse Claude server disabled, cwd `/Users/edr/code/JouleWise-wt-decode-id`. Thread id `01a06a64-b2e8-7ca1-a9bb-ab2adcecfe65`. Envelope: valid `bridge-report/v1`, status `DISCUSSION`, flags `no_edits, head_match, not_landable`. No repository writes (worktree clean before and after).

**HEAD:** `24df48e8070377f8bc5fadd0ac085191c37c1817` — verified by Sol and by me.

### Cure-by-cure

| Finding | Cure | Closes? | Facts (Sol read, lead replayed) |
|---|---|---|---|
| L1 stale `:2100-2234` cite | names `verify_frozen_projection` + `_run_identity_arm_reverification` | YES | Both exist: `joulewise/identity_pins.py:2379`, `joulewise/arm_readiness.py:5681`. "Maps the same code into readiness refusal" is accurate: the wrapper catches `IdentityPinProjectionError` / `ArmReadinessError` and returns `[exc.reason_code]` (`arm_readiness.py:5726-5729`); `generate_arm_receipt` routes those to `desk.identity_pin_projection` → `_receipt_refusal(code)` → arm `REFUSE` / `NO_GO` (Sol cites `:8355-8369`, `:6670-6697`, `:8395`, `:8425-8426`). "Code" is the dynamic reason code, not one literal. |
| L2 "runs root" unglossed | "(the directory under which a launch's collected bundles are written)" | YES | Actual locator writer is `_publish_launch_lineage_locator` (`arm_readiness.py:9867`; `path = resolved_root / LAUNCH_LINEAGE_LOCATOR_BASENAME` at `:9891`), not `bundle._writer_launch_lineage` (`bundle.py:87`, which authenticates/reads at bundle create `:933`). Bundles are created at `root / run_id` below that root. Gloss accurate. |
| L3 pack-digest gloss | "a SHA-256 over the committed campaign-pack files — paths, modes and bytes — computed by `committed_pack_tree_sha256`" | PARTIAL | `arm_readiness.py:2750`, framing `:2849-2874` replayed: domain prefix `joulewise.committed_pack_tree_sha256.v1\n` (`:46`), then per committed path (bytewise sorted, set from `git ls-tree HEAD`): `path\0mode\0len(raw)\0sha256hex(raw)\n`; outer SHA-256 over that frame. Raw bytes are verified against the Git blob and mode-checked (`readiness_pack_digest_mismatch`) but enter the outer hash only via length + content digest. Sol: "FALSE literally". Lead: the digest IS a deterministic function of exactly paths, modes and bytes, so as a plain-words first-use gloss it is defensible; the precise framing is at `:708`. **What is not defensible:** "modes" appears at `:591` with no plain gloss anywhere earlier (`grep` shows only `mode` = work-order mode at `:184-227`, a different thing); next mention is "Git mode" at `:708`. First-use defect introduced by the cure. |
| L5 alias undeclared | "The analysis input gate (called the analysis gate below)" at `:647-648` | **NO** | Replayed: `grep -n` shows "the analysis gate" at **`:632`**, fifteen lines BEFORE the declaration at `:647-648`. "Below" is factually false and the term's meaning still arrives after first use — the exact defect class L5 named. |
| L6 `[S3 ruling (d)]` shorthand | plain sentence pointing to trace file 32 | YES | File 32 records "ruled (d) for this lane" and the machine-absolute boundary (Sol: `:67-90`); contract `:684-687` states the boundary in plain words before the pointer. |

L4, L7, L8 are recorded as uncured in file 53; not re-adjudicated.

### Scope check (`git diff --name-only origin/main...HEAD`, outside the three named families)
`configs/campaigns/d117_contrast_v5/generate_configs.py`, `docs/contracts/d165_dominance_closeout.md`, `docs/decision_log.md`, `docs/phase_2/gamma_arm_readiness.md`, `docs/specs/c027/p2-039_floor_artifact.md`, `joulewise/analysis_engine/__init__.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/detection_floor.py`, `joulewise/identity_pins.py`, `tests/test_analysis_inputs.py`, `tests/test_analysis_integration.py`, `tests/test_d117_contrast_v5_pack.py`, `tests/test_detection_floor.py`, `tests/test_identity_pins.py`. Sol and lead lists agree. Whether each was scoped by earlier rounds is for the magistrate; the five non-`identity_pin_projection.md` doc paths (`d165_dominance_closeout.md`, `decision_log.md`, `gamma_arm_readiness.md`, `p2-039_floor_artifact.md`, `generate_configs.py`) are the ones to confirm against round briefs. Commit 24df48e8 itself touches only the contract + trace files 53/54.

### Findings (lead-synthesized; Sol's tier noted where it differs)

- **SHOULD-FIX** — `docs/contracts/identity_pin_projection.md:632` vs `:647-648`: L5 not closed; "called the analysis gate below" is false. Bench cure: either write "analysis input gate" at `:632` or move the alias declaration to the first use. (Sol rated NIT; lead raises to SHOULD-FIX because a fix-round cure that does not close its finding, and file 53 presumably records it as closed, is a false landing claim.)
- **SHOULD-FIX** — `:591`: "modes" unglossed at first use (introduced by the L3 cure). Bench cure: "paths, file modes (executable or not) and bytes" or similar.
- **NIT (disputed)** — `:590-591` "over ... bytes": Sol reads as literally false (outer preimage holds length + content-digest, not raw bytes); lead reads as acceptable plain gloss since `:708` gives the exact framing. Magistrate's call; a two-word fix ("...and the bytes' digests") would satisfy both readings.
- BLOCKER: none.

### Verdict
**NOT LANDABLE as-is** (Sol's verdict; lead concurs). Two bench-sized prose cures (`:591`, `:632`/`:647-648`) then a two-line delta re-check — both below the delegation threshold, so bench work per rule 9.

Files: `/Users/edr/code/JouleWise-wt-decode-id/docs/contracts/identity_pin_projection.md`, `/Users/edr/code/JouleWise-wt-decode-id/joulewise/arm_readiness.py`, `/Users/edr/code/JouleWise-wt-decode-id/joulewise/identity_pins.py`, `/Users/edr/code/JouleWise-wt-decode-id/joulewise/bundle.py`, `/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-decode-identity-set/53-bench-cures-after-fresh-pass.md`, `/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-decode-identity-set/54-terra-fresh-pass-report.md`.
