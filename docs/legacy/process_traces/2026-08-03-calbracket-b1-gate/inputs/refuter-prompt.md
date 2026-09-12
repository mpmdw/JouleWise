BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "review",
  "ROLE": "contract-lens adversarial refuter (rule-11 cold-gate, CAL-BRACKET-D079-01 audit blocker B1)",
  "OBJECTIVE": "Attempt to refute (a) the delta re-audit's B1-refined finding and (b) the lead's proposed round-2 disposition, against the code at HEAD and the D-109 contract; then rule on packet section 8 items (a)-(e) from the contract lens. Read-only.",
  "AUTHORITY": [
    "docs/decision_log.md entry D-109 (R1 clauses 1-7, R2 clauses 1-8) — the governing contract; read the FULL entry, not only the packet's excerpts",
    "/Users/edr/code/JouleWise/docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md — the mechanically assembled gate packet",
    "/Users/edr/code/JouleWise/docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/ — six verbatim custody inputs (impl prompt/report, audit, fix prompt, fix-1 report, delta re-audit)",
    "AGENTS.md (repository receiver rules)",
    "Lead ruling: effort HIGH is in force by Ed directive; this session is one half of a two-refuter cold gate and must judge independently — do not defer to the lead's section-7 disposition or to the delta re-audit's framing; both are objects under review."
  ],
  "WRITE_SCOPE": [],
  "BASE_HEAD": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
  "ACCEPTANCE": [
    "Every claim of fact about the code carries file:line evidence verified at HEAD 2e61ff9 in this worktree, not quoted from the reports.",
    "Charges 1-4 below are each answered explicitly, including a named list of consumer paths the proposed disposition does or does not cover.",
    "A verdict on packet section 8 (a)-(e) is returned, including an explicit ruling on whether a second in-place patch is sound or whether the guard-placement defect signals a structural problem requiring escalation.",
    "No file is modified anywhere; pathspec is []."
  ],
  "VERIFICATION": [
    "Static code inspection of joulewise/whole_window.py, joulewise/floor_extraction.py, scripts/mint_floor_artifact.py, joulewise/analysis_engine/inputs.py, tests/test_whole_window_selection.py at HEAD",
    "Cross-check of the six custody inputs and the full D-109 entry against the packet text",
    "Read-only python probes are permitted if useful (no file writes; no test-suite mutation)"
  ],
  "EARLY_RETURN": ["NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "claude-codex-report/v1"
}
END_BRIDGE_TASK_V1

You are the CONTRACT-LENS REFUTER half of a rule-11 cold gate on CAL-BRACKET-D079-01 audit blocker B1 (a proposed second fix round). A separate Opus refuter covers the other lens. Your job is adversarial: try to break the delta re-audit's finding and the lead's proposed disposition before either is acted on. Your output will be recorded verbatim in the gate record.

Working tree: you are launched in the worktree for branch impl/cal-bracket-d079 at commit 2e61ff96ea80186efa71efb9c9f6f00a16a70019. All code citations must be from THIS tree at THIS commit. The gate packet and custody inputs live in the main checkout and are referenced by absolute path in AUTHORITY above; read them there (read-only).

Context in brief (verify everything yourself; do not trust this summary):
- D-109 landed a Sol-delegated implementation (commit 8383113); an independent audit found blockers B1, B2 and should-fix S1; fix round 1 (commit 2e61ff9, this HEAD) claimed to close all three; the delta re-audit closed B2 and S1 but found B1 PERSISTS IN REFINED FORM.
- The delta re-audit's refined B1 claims two simultaneous defects at this HEAD: (i) FAIL-CLOSED — the new guard at joulewise/whole_window.py:4073-4083 runs before the preparation seam (_prepare() reached via _validate_row_uncached() -> _current_core_rederivation_reasons() at ~:3468), so a freshly constructed minted session with a valid ledger snapshot is refused before preparation is ever attempted, breaking legitimate consumers in floor extraction, floor minting, and analysis input loading; (ii) FAIL-OPEN — the guard compares the RAW row declaration while _row_consumption_semantics_id() defaults a missing declaration to d078_minted_envelopes_v1, so implicit/default minted rows bypass the guard entirely.
- The lead's section-7 disposition (NOT benched, NOT prototyped): move the guard after/inside the preparation seam, compare normalized semantics via _row_consumption_semantics_id(), and add two interaction-shaped regressions (fresh minted session WITHOUT manual _prepare() expecting acceptance; implicit/default minted row with no session expecting refusal).

YOUR FOUR CHARGES:

1. REFUTE THE FINDING. Is the claimed fail-closed path and fail-open path actually real at 2e61ff9? Verify against the code, not the report. Trace the actual call order: does the early return at :4073-4083 really precede any _prepare() opportunity on the production consumer paths (floor_extraction.py:1616, :1877; scripts/mint_floor_artifact.py:520, :529; analysis_engine/inputs.py:2815, :2820)? Does _row_consumption_semantics_id() really default a missing declaration to d078_minted_envelopes_v1 while the guard compares raw? If either half of the finding is wrong, exaggerated, or mis-located, say so with file:line proof.

2. REFUTE THE DISPOSITION. Does the lead's proposed shape (guard after/inside the preparation seam + normalized-semantics comparison + the two named regressions) actually satisfy D-109 R1.2 (reservation-first refusal semantics) and R1.4 (ONE immutable ledger snapshot threaded through EVERY consumer path: session, direct runner, secondary verifier) on every consumer path? Enumerate the consumer paths you checked. Name any path the disposition leaves uncovered (a residual bypass) and any way it introduces a NEW fail-closed break. If the disposition is under-specified in a way that matters (e.g., "after or inside the seam" admits a wrong placement), say exactly what constraint is missing.

3. PACKET HYGIENE. Compare the packet (PACKET.md) against the six custody inputs and the full D-109 entry. Does the packet omit, soften, or misframe any material evidence? Check in particular that its verbatim quotations are actually verbatim and that section 5's "what is NOT in dispute" list matches the delta re-audit.

4. RULE ON SECTION 8 (a)-(e) from the contract lens: (a) LICENSE or REFUSE round 2; (b) the ruled repair shape — you may rule an alternative, including structural options neither round has tried; (c) the mandatory regression shape; (d) execution route (bench vs delegated), noting rule 9's bench-vs-session threshold; (e) conditions on the post-round-2 delta re-audit. Include an explicit ruling on whether a second in-place patch is sound, or whether a guard placed on the wrong side of a preparation seam signals a structural problem (e.g., the seam itself is the wrong shape) that should escalate to a consult instead of round 2.

Hard requirements:
- file:line evidence for EVERY finding, verified at this HEAD.
- Findings must be severity-tagged (blocker / should-fix / observation) and each must state REFUTED / CONFIRMED / PARTIALLY-CONFIRMED against the claim it addresses.
- You are read-only: modify NO file, run NO write operations, create NO files. WRITE_SCOPE is [] and exhaustive.
- Do not run any test that writes outside a temp sandbox; prefer static inspection and read-only probes.
- One hop only: never invoke Claude by MCP, `claude -p`, or any other launcher.
- End with the required report envelope. A missing, duplicated, malformed, or non-final required envelope is protocol failure, never success.
