# Magistrate ruling 16c — the blind design seat on 16b (luna, report 24)

Date: 2026-09-01. Seat: Fable magistrate. Input: `24-luna-design-g2a.md`
(gpt-5.6-luna, effort max, read-only, detached at main 80912c8d; blind to
the two implementation streams, which ran concurrently by design so a
design blocker could halt them early). Luna's verdict was
HALT-IMPLEMENTATION with two `NEEDS_RULING` flags. The streams finished
before the seat did, so each finding is ruled here as either a change to
the ruling, an item for the G2-a fix round, or a refusal with reason.

| # | Luna severity | Ruling | Where it lands |
|---|---|---|---|
| F-01 R1 prefix contradiction | blocker | **Resolved by R1.5, not a contradiction.** The scout (`16-…:226,332`) asked for a token-ID prefix relation across rungs; 16b R1.5 removed it. The ruling supersedes the scout; the implementation has no prefix check. Luna's deeper point stands and is recorded: with per-rung closing sentences the last 8–11 tokens differ across rungs, an unregistered content covariate on a length-only probe. Accepted as a non-effect for a resolvability probe (one closing sentence in 512–4096 tokens cannot move the phase-window overlap count); the ladder's `generation_method` already names the closing per rung, so the covariate is disclosed, not hidden. R1 stands. | ladder doc sentence (fix round, item D-1) |
| F-02 R2 wording dishonest | blocker → **should-fix** | **Accepted.** The panel's `enable_thinking:"false"` / `chat_template_applied:true` are decode-arm rendering pins; the probe's raw `prompt_text` never meets the chat template (`workloads.py:3-5`, `mlx_runtime.py:931-940`). No measurement changes; the label does. The ladder and inventory gain `rendering_mode: "raw_prompt_text"`, `chat_template_applied: false`, `thinking_policy: "not_applicable_raw_prefill"`; the panel's hash stays bound (it still pins the decode arm the selected rung feeds). R2 amended accordingly; the runsheet sentence says "raw prompt text, no chat template, so the thinking switch is never rendered; the panel is hash-bound for the decode arm". Not a blocker: nothing measured would differ. | fix round D-2 (shared schema amendment) |
| F-03 split selection authority | blocker | **Accepted.** The issuer writes `record_id` and `g2a_record_sha256` from the same bytes (R3), but `_load_prefill_prompt_pin` (`generate_configs.py:890-915`) does not require `record_id == "sha256:" + g2a_record_sha256`, so a hand-edited pin can name one record and hash another. Both sides close it: the issuer asserts equality before writing; the loader refuses inequality with a named reason. Loader edit is allowed under the registration-bytes-frozen guard (golden readback hash unchanged). | fix round D-3 |
| F-04 check-then-launch race | blocker → **refused as pre-launch guard; accepted at the evidence boundary** | A file mutating between `check` and a child launch requires the operator to edit inputs during their own bracket — D-161's operator-only adversary, where a refusal is over-engineering. The soundness requirement is that mutated inputs cannot become *evidence*: the summarizer authenticates every run's realized config hash and realized prompt token-ID hash/count (the adapter records them, `mlx_runtime.py:400-407`) against the inventory and ladder before any count enters the summary. That is luna's F-05, ruled below. No snapshot launcher, no runner change. | — |
| F-05 summary lacks realized provenance | should-fix | **Accepted, and it is the F-04 cure.** If stream 2's summarizer does not already compare realized `prompt_token_count` and token-ID hash per run against the ladder rung, and config sha256 against the inventory member, it must; a mismatch refuses the rung with a named reason (not a silent count of zero). | fix round D-4 (conditional on report 30) |
| F-06 budget not proven | should-fix | **Accepted in prose, refused as a mechanical guard.** Luna's arithmetic (8 × 600 s settles + pre-cal settle ≈ 90 min; 24 members × ~148 s ≈ 59 min; two 59-pulse calibrations; ≈ 2.5–3 h against the 2–4 h target) goes into the runsheet's G2-a preparation block as the declared budget with each term named. A reservation-refusal guard defends against nothing but the operator's own clock. | fix round D-5 |
| F-07 `prompt_candidate` hardcodes the 2048 closing | should-fix | **Accepted.** `generate_configs.py:1642-1644` reports `PROMPT_FINAL_SENTENCE` as `final_sentence` for any selected rung; for 512/1024/4096 the audit record would be false. The pin carries `closing_sentence` (R1.4); `prompt_candidate` copies it and the `generation_method` from the pin. Registration bytes unchanged (guarded by the golden readback). | fix round D-6 |
| F-08 NONE-ledger labels | nit | Noted; the scout is a trace record, not edited. | — |

## Net effect on 16b

R1, R3, R4 stand. R2 is amended by F-02 (labels only). Two loader-side
changes to `generate_configs.py` (F-03 equality, F-07 provenance copy) are
authorised for the fix round under the standing guard that the reviewed
registration's canonical serialization keeps its SHA-256 (the golden
readback test runs before and after). The `HALT-IMPLEMENTATION` verdict is
not adopted: none of the eight findings changes a measured quantity or a
selection outcome; they change labels, provenance copies, and one loader
equality check. The G2-a fix round (after refuters 29 terra-contract and
30 luna-execution land) carries D-1…D-6 above alongside their findings.
