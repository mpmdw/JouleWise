```json
[
  {
    "title": "Envelope field types are referenced but never defined",
    "file": "docs/contracts/bridge_protocol.md",
    "line_hint": "146-174",
    "severity": "should-fix",
    "argument": "The ratified pin requires five required fields with types. The field list describes meanings, while line 174 merely refers to their “existing types” without normatively defining them. The example is insufficient contract authority, especially because consumers already enforce strings and arrays.",
    "suggested_fix": "Explicitly define status and summary as strings, and pathspec, verification, and flags as arrays of strings; retain the status enum and unknown-key tolerance."
  },
  {
    "title": "Re-close idempotence excludes retained-lease outcomes",
    "file": "docs/contracts/bridge_protocol.md",
    "line_hint": "403-412",
    "severity": "should-fix",
    "argument": "The ratified pin requires idempotent re-close, but the contract only makes an already-complete, already-released close a no-op. NEEDS_SCOPE, NEEDS_RULING, PARTIAL, and non-OK scope verdicts remain waiting_lead with retained leases. scripts/bridge correspondingly appends another waiting_lead event when the same close is retried, and tests cover idempotence only for DONE.",
    "suggested_fix": "Define identical re-close behavior for every previously recorded close outcome, including retained-lease outcomes, while still permitting a later resumed close with a new status. Align scripts/bridge and add waiting/non-OK idempotence tests."
  },
  {
    "title": "Session-close has no disposition for BLOCKED or FAILED statuses",
    "file": "docs/contracts/bridge_protocol.md",
    "line_hint": "395-408",
    "severity": "should-fix",
    "argument": "BLOCKED and FAILED are valid bridge-report/v1 statuses, and the operating skill directs the lead to pass the returned STATUS to session-close after writes. The wrapper contract maps only DONE/DISCUSSION, NEEDS_*/PARTIAL, and scope verdicts; scripts/bridge rejects BLOCKED and FAILED at argument parsing. A well-formed blocked or failed write session therefore cannot be recorded through the preferred ceremony.",
    "suggested_fix": "Normatively map BLOCKED and FAILED—preferably to waiting_lead with the lease retained and the actual bridge status recorded—or explicitly specify a separate recovery path and update consumers. Align the CLI choices and tests."
  },
  {
    "title": "Forward-effort tier prose remains duplicated outside its one home",
    "file": "CLAUDE.md",
    "line_hint": "16-18; also .claude/agents/codex.md:26-28 and .claude/commands/codex.md:9-11",
    "severity": "should-fix",
    "argument": "The ratified one-home pin places effort-tier prose only in .claude/skills/codex/SKILL.md and requires the agent, command, and CLAUDE.md to compress to pointers. All three still restate the high/xhigh/ultra selection semantics after their pointers, preserving three drift-prone copies.",
    "suggested_fix": "Replace each recap with a pure pointer such as “Select and pass effort per .claude/skills/codex/SKILL.md §Effort selection.” Keep adapter injection, receiver, sandbox, and no-bypass guardrails explicit."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Contract-authority review found four should-fix consistency gaps: undefined envelope types, incomplete re-close idempotence, missing BLOCKED/FAILED close semantics, and duplicated forward-effort tier prose.","pathspec":[],"verification":["Read git diff main...HEAD and all 12 touched files, including the complete amended contract and every named consumer document.","Inspected scripts/bridge session-open/session-close implementation and focused wrapper tests; inspected reverse-adapter validation and tests.","git diff --check main...HEAD: OK.","Python AST parsing for scripts/bridge and both focused test modules: OK; node --check scripts/claude-bridge-mcp.mjs: OK.","Attempted python3 -m unittest tests.test_bridge tests.test_claude_bridge_mcp; execution was sandbox-blocked before assertions because no writable temporary directory was available.","Scope audit: HEAD equals bad3465ad4613ce120efd13d69eed5397b773985; worktree and index are clean; no files changed."],"flags":[]}