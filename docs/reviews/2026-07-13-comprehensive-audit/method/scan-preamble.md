# Shared scan preamble (every Batch 1 Sol session; driver fills {{...}})

BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "review",
  "ROLE": "{{ROLE}}",
  "OBJECTIVE": "{{OBJECTIVE}}",
  "AUTHORITY": [
    "docs/reviews/2026-07-13-comprehensive-audit/report.md (frozen charter; §2 your cell's definition, §3 register/receipt contract, §4 severity rules)",
    "AGENTS.md"
  ],
  "WRITE_SCOPE": [],
  "BASE_HEAD": "e3fc14a01ca047e779fa7924fdf128b25762d063",
  "ACCEPTANCE": ["One valid receipt JSON object per the contract below; findings only with auditable evidence."],
  "VERIFICATION": ["Read every manifest file; run read-only commands as needed; state what you did NOT examine."],
  "EARLY_RETURN": ["NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "bridge-report/v1"
}
END_BRIDGE_TASK_V1

You are one cell of the JouleWise comprehensive audit (charter frozen
2026-07-13). Audit object: the pinned tree at BASE_HEAD above — post-pin
commits are the audit's own artifacts and are OUT of scope. You change
nothing; fixes become work orders later. "Large" and "complicated" are not
blockers; blocker is reserved for evidence corruption/loss, claim
invalidation, canonical-reproducible-flow failure, or an architecture defect
making the next roadmap gate unsafe (roadmap: multi-node/NVIDIA-Orin split,
campaign scale-up — see AGENT_PLAN.md phase index).

Your file manifest (your EXACT scope; do not roam outside it, but you MAY
follow a call/import across the boundary to VERIFY a claim — say so in the
receipt):

{{MANIFEST}}

Findings: assign only `severity` (blocker|should-fix|nit) — verification
tiers are assigned downstream. Every finding needs auditable evidence in
`evidence_refs`: file:line, command+result, behavior trace, contract ref, or
a bounded absence-search description ("grepped X across Y; no consumer").
No evidence, no row. Propose one `proposed_disposition` per finding:
keep|simplify|delete|fix|investigate. Ids are {{CELL_ID}}-001, {{CELL_ID}}-002, …

Return EXACTLY this, in order:
1. One fenced json block: your RECEIPT —
   {"scan_id": "{{CELL_ID}}", "scope_examined": [...paths or globs actually read...],
    "exclusions": [...manifest paths you did not read + why...],
    "checks_performed": [...commands/traces you actually ran...],
    "uncertainties": [...what you could not determine...],
    "rows": [ {finding rows per the charter §3 schema: id, mission_tags,
      domain, seams, finding, consequence, counterevidence, severity,
      proposed_disposition, evidence_refs} ... ]}
   rows MAY be [] — a clean cell is a valid result; your scope_examined
   proves the scan was complete, not lazy.
2. The bridge-report/v1 envelope (sentinel + one JSON line; status
   DISCUSSION; pathspec []; verification = what you actually ran).

{{LENS}}
