```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"none","summary":"NEEDS_RULING: unchanged executors require custody writes forbidden by the brief.","workspace":{"base_requested":"cea87cca","base_mode":"exact","head_start":"cea87cca","head_end":"cea87cca","upstream_end":"e68aa6a0","branch":"feat/2026-09-20-evidence-night-entry"},"pathspec":[],"unowned_dirty":[],"verdict":{"implementation":"no_change","acceptance":"needs_ruling"},"verification":[],"flags":[{"id":"F1","kind":"lead_ruling","level":"blocking","text":"Generator writes sealed artifacts at plan.chain_path under custody; installer reads them there.","needs":"Rule on custody artifact creation versus executor changes."}]}
```

## Change

No files changed. Completed authority review and executor inspection; workspace remains clean.

**NEEDS_RULING — Question:** May preparation create custody’s wrapper, sidecars and manifest while leaving `night_plan.json` unpublished, or must custody remain entirely absent?

The requested combination cannot use the unchanged executors:

- `scripts/gen_evidence_night.py:26–28` requires output to equal `plan.chain_path`; `--out` cannot redirect it.
- Lines 65–73 create the wrapper, both sidecars and manifest under that path, including its parent directory.
- `joulewise/night_agent_install.py:1150–1181` reads the wrapper from `plan.chain_path`, its sidecar, and the manifest’s sealed literal path.

Thus artifacts are placed beside **the chain**, not beside the staged plan.

**Options considered:**

1. Permit custody artifact creation, keeping the plan staged until notice acceptance. This matches the existing bench procedure and preserves unchanged executors.
2. Require all artifacts to remain staged. This needs a revised executor contract and expanded write scope for generator/installer support; redirecting output or rewriting sealed paths would violate current bindings.

**Recommendation:** Option 1 for this bounded slice, if the lead accepts that custody boundary. Otherwise authorize a separate executor change first.

**Blocked work:** The preparation contract, implementation and end-to-end tests depend on this ruling. No independent implementation was made that would presume its answer.

## Verification notes

Read-only inspection established the conflicting paths. Tests were not run; there are no test tails or runtime-success claims.

Slice B remains deferred: lifecycle façade operations, handbook/runbook checklist, and pre-arm checks. Notice transport, publication and installation remain beyond slice A. No plan-id or venv-injection decision was made.

Next exact step: provide the custody-boundary ruling and resume this session.