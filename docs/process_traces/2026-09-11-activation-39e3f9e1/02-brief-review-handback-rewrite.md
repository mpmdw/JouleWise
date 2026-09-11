SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

CONTRACT-LENS REVIEW (read-only; temp files only under /tmp) of one docs-only commit, 944963b99509f0887aa367c21ac695ecd66b565f on branch feat/2026-09-11-handback-rehearsal-20260912, in this worktree. The commit rewrites docs/process/NIGHT_HANDBACK.md for tonight's REHEARSAL_STUB night rehearsal-20260912. Its authority is the arm runbook /Users/edr/code/JouleWise-wt-bk-39e3f9e1/docs/process_traces/2026-09-11-activation-58a3bcfc/13-arm-runbook-stub-20260912.md, §Step 0b (the three replacement sections, given there verbatim inside fenced markdown blocks) and its closing paragraph about the G2-a routing "interpreter field" sentence; the pins table in §Pins; and the dated addendum /Users/edr/code/JouleWise-wt-bk-39e3f9e1/docs/process_traces/2026-09-11-activation-3dab9c89/11-addendum-record13-installer-facts.md.

Answer, each with the command you ran and its output:
1. VERBATIM CHECK. Extract the three fenced replacement blocks from record 13 §Step 0b (## Purpose of this night, ## Where the results are, ## Next lane for rehearsal-20260912) and diff each against the corresponding section of docs/process/NIGHT_HANDBACK.md at HEAD. Report every byte-level difference. Known and intended: the third heading is the bare "## Next lane" (PR #321's heading) rather than "## Next lane for rehearsal-20260912". Anything else is a finding.
2. INTERPRETER PARAGRAPH. Show the G2-a routing paragraph at HEAD and state whether it now says which of driver/chain/preflight was pinned when, without implying the driver was already pinned before PR #321 (record 13 §Step 0b closing paragraph; ruling 06 §9).
3. NOTHING ELSE CHANGED. git diff <parent>..HEAD --stat must touch only docs/process/NIGHT_HANDBACK.md; the "Executed — rehearsal-20260909" and "Executed — rehearsal-20260911" history sections and the "**Standing rules**" block must be byte-identical to the parent. Show the check.
4. PINS ARITHMETIC. Recompute from Python (zoneinfo America/Los_Angeles): t0 2026-09-12 00:30:00 PDT = 1789198200; window close 1789199100; courier deadline 1789199400 (00:50); plan span / stand-down 1789196700 (00:05); TERM 1789197240; KILL 1789197300; dead-man 2026-09-12 07:00 = 1789221600. Confirm every number in the rewritten sections matches; list any that does not.
5. OTHER MENTIONS. grep -n 'rehearsal-20260911' docs/process/NIGHT_HANDBACK.md: only the retirement sentence, its record pointers, and the dated history section may name it. Report the lines.
6. WRITING-STANDARD FIRST-USE TEST on the three rewritten sections only: any term of art used before it is defined or glossed in this file (the file's earlier sections may define terms; cite where). Report as nits.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: MERGEABLE | MERGEABLE AFTER FIXES | NOT MERGEABLE and the claude-codex-report/v1 envelope.
