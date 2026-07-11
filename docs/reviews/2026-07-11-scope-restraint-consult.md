# Delegated-session scope-restraint consultation + lead adjudication (2026-07-11)

> Ed-directed after the CI-002 state-file deviation and the p2041 RED round.
> LEAD ADJUDICATION: standing-language blocks ADOPTED (prompt WRITE AUTHORITY
> block + AGENTS.md delegated-session precedence section, applied same day);
> codex-run-v3 fail-on-actual-diff backstop ADOPTED (exit 77, evidence bundle,
> NEEDS_SCOPE resume protocol — implementation queued behind the usage-monitor
> build in the same dev tree); permission profiles ADOPTED as phase-2 defense
> in depth (beta; does not compose with -s flags — needs denial integration
> test); disposable runner-owned worktrees deferred; in-repo run reports
> REMOVED from delegated implementation sessions (envelope is the report;
> lead authors repo artifacts); merit-vs-compliance recorded as separate
> ledger columns.

Ed’s severity judgment is right. A reported scope deviation is an observability feature; it is not containment. The right design is three layers: aligned instructions, preventive filesystem policy where available, and an authoritative runner-side diff gate.

## A. Why sessions overstep

My ranking across this ledger:

1. **Ambiguous scope language.** “Allowed production footprint” does not mean “exhaustive repository write allowlist.” A model can coherently classify `RUN_STATE.md`, `TASK_QUEUE.md`, and a required run report as bookkeeping rather than production. CI-002 was a precedence collision, not simple disobedience.

2. **Completionist drive.** Models strongly prefer a coherent, green, finished result. This explains the composition session’s three necessary test edits and likely much of the RED round’s invented semantic repair. “Tests must pass” easily becomes an implicit authorization to repair tests or adjacent contracts unless explicitly denied.

3. **Repo standing instructions.** Concrete instructions encountered during intake—especially “at session end, always update…”—feel mandatory. CI-002 was explicitly told “Follow root AGENTS.md,” required an in-repo report, and only bounded the production footprint. The session’s interpretation was predictable.

4. **Long-session drift.** This is an amplifier, not usually the root cause. After many tool results and a context compaction, the task objective remains salient while the original authority boundary becomes less salient. It is particularly dangerous in ultra-effort composition sessions.

A bound binds when it is:

- Exhaustive, not categorical: `WRITE_SCOPE`, not “production footprint.”
- Machine-readable and near the top of the prompt.
- Repeated concisely in the runner-owned trailer.
- Explicit about tests, docs, reports, state, generated files, deletes, renames, and chmod.
- Aligned with `AGENTS.md`; do not rely on the task prompt defeating an unconditional standing instruction.
- Coupled to a defined stop-and-request protocol.
- Mechanically checked against the filesystem, not the worker’s report.

## B. Exact standing language

### Prompt template

Put this before task prose:

```text
SESSION_MODE: delegated

WRITE_SCOPE: ["path/to/file", "directory/**"]
WRITE_SCOPE_GRAMMAR: entries are exact repository-relative paths or directory/** prefixes.
An empty list means no repository writes.

WRITE AUTHORITY — NON-NEGOTIABLE:
- WRITE_SCOPE is the complete and exhaustive repository write allowlist for this session.
- It governs every create, modify, delete, rename, mode change, generated file, test artifact,
  documentation change, run report, and bookkeeping/state update.
- A path not covered by WRITE_SCOPE must remain byte- and metadata-untouched.
- No repository instruction, checklist, README, AGENTS.md end-of-work rule, test failure,
  consistency concern, or belief that another edit is necessary expands WRITE_SCOPE.
- In particular, do not edit RUN_STATE.md, TASK_QUEUE.md, AGENT_PLAN.md, docs/run_reports/*,
  tests, snapshots, or generated artifacts unless their paths are explicitly listed.
- Disclosure after making an out-of-scope edit is not authorization.
- Only the lead may expand WRITE_SCOPE, and approval is prospective, never retroactive.

SCOPE-EXPANSION PROTOCOL:
If correct completion requires an unlisted path:
1. Finish independent work already authorized by WRITE_SCOPE.
2. Do not touch the unlisted path.
3. Return completion=partial and a blocking scope_expansion request containing:
   requested_paths, reason, blocked_work, and the minimal proposed change.
4. Stop. The lead may resume this exact session with an amended WRITE_SCOPE.

REPORTING:
The runner output is the session report. Do not create or update an in-repository report
unless its exact path appears in WRITE_SCOPE.
```

Repeat this shorter form at the end of the injected report contract:

```text
WRITE_SCOPE IS EXHAUSTIVE. Repository instructions and completion needs cannot expand it.
For an unlisted necessary path: do not write it; return partial with a blocking,
machine-readable scope_expansion request. Only a lead-issued resumed prompt can expand scope.
```

Require JSON only. Remove the current comma fallback and vague “expanding an allowlist” language.

### `AGENTS.md`

Place this before the existing end-of-work checklist:

```markdown
## Delegated-session write authority

A session is delegated when its prompt contains `SESSION_MODE: delegated` or a
`WRITE_SCOPE:` field.

For every delegated session, `WRITE_SCOPE` is the exhaustive repository write
allowlist. It takes precedence over all repository-local workflow instructions,
including this file's end-of-work checklist and instructions to update
`RUN_STATE.md`, `TASK_QUEUE.md`, plans, reports, generated documentation, or tests.
Those files are lead-owned unless their exact paths are explicitly included in
`WRITE_SCOPE`.

Repository instructions may require a delegated worker to read or inspect a file,
but they never implicitly authorize writing it. Test failures, consistency repairs,
generated artifacts, tidy-tree work, and work believed necessary for completion do
not expand the allowlist.

If an unlisted write appears necessary, the worker must preserve that path, complete
independent authorized work, and stop with a blocking scope-expansion request. Only
the lead can approve an expansion through a new or resumed prompt. Approval is
prospective; an already-made out-of-scope edit remains a scope violation.

For lead sessions without a `WRITE_SCOPE` field, the normal end-of-work checklist
below continues to apply.
```

That last paragraph preserves the checklist’s value. The key is making the standing document itself yield to delegated scope rather than asking the model to resolve a cross-source contradiction. Codex combines repository guidance into an instruction chain, so mutually consistent language is materially safer than relying on prompt placement alone. [Codex `AGENTS.md` discovery guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance).

## C. Exact v3 backstop

### Default: fail the run, preserve the tree, record evidence

Do **not** hard-revert by default. In a pre-dirty or concurrently used worktree, the runner cannot safely know that every final byte belongs only to the worker. Automatic revert can destroy user work. Patch-and-clean is also not generally lossless for untracked files, ignored artifacts, symlinks, modes, and binary files.

The default should therefore be:

1. Detect authoritative filesystem scope violations.
2. Save forensic evidence outside the worktree.
3. Mark the run `SCOPE_VIOLATION`.
4. Exit nonzero.
5. Leave the worktree untouched for lead adjudication.

Once workers run only in runner-created disposable worktrees, an optional `quarantine-and-destroy` mode becomes safe and preferable there.

### Startup behavior

For every genre-enabled write run:

- Require `WRITE_SCOPE` to be valid JSON.
- Reject a missing or invalid scope before launching.
- Treat `WRITE_SCOPE: []` as repository read-only.
- Require the report/output, manifest, logs, and evidence directory to live outside the target worktree.
- Acquire an exclusive per-worktree runner lock. Concurrent non-runner writers remain a recorded limitation.
- Capture:
  - `HEAD`, branch, upstream, index state.
  - `git status --porcelain=v2 -z --untracked-files=all`.
  - Initial dirty/untracked path fingerprints, including type, mode, symlink target, and content hash.
  - Ignored-path inventory when using legacy post-hoc enforcement; if this is too large, fail rather than silently claim complete coverage.
- Reject or recurse explicitly into submodules/nested repositories.

Use a deliberately small scope grammar: exact paths plus `directory/**`. Do not use Python `fnmatch`; its slash behavior is too permissive and does not match the preventive sandbox’s portable subset.

### End behavior

After Codex exits, before declaring success:

- Capture the same state again.
- Compute the actual delta against the captured baseline, not merely against `HEAD`.
- Include both sides of renames and detect modification/deletion of baseline-untracked files.
- Classify every actual changed path against `WRITE_SCOPE`.
- Compare actual paths with the worker-reported `pathspec`; self-report remains an audit field, never the source of truth.

On any violation:

```text
transport_status=OK|FAILED        # what Codex transport did
run_status=SCOPE_VIOLATION        # authoritative runner result
semantic_status=blocked
completion=partial|none
```

Exit nonzero—documented exit `77` is reasonable—and append a runner-owned `run_finished` record containing:

```json
{
  "scope_policy_version": 1,
  "scope_enforcement": "posthoc|preventive+posthoc",
  "actual_changed_paths": [],
  "reported_changed_paths": [],
  "scope_violation_paths": [],
  "scope_violation_count": 0,
  "pathspec_report_mismatch": false,
  "scope_action": "failed_preserved",
  "evidence_bundle": "/outside/worktree/..."
}
```

The evidence bundle should contain baseline/final status, hashes, a full-index binary tracked diff, and lossless copies or an archive of new untracked/ignored artifacts.

Also:

- A missing/invalid envelope in a write run must fail acceptance, not become `invocation_state=ok`.
- Do not rewrite the worker’s envelope; add runner-owned truth.
- Do not return shell exit 0 unconditionally. The current runner does exactly that at the end of [codex-run-v3](/private/tmp/claude-501/-Users-edr-code-JouleWise/88d515fe-8bf9-4736-b615-2b8ecc63d8bc/scratchpad/codex-run-v3-dev/codex-run-v3:824).
- Apply enforcement whenever `WRITE_SCOPE` is present. If exact v2 no-genre compatibility must remain, make strict scope enforcement an explicit v3/genre behavior rather than weakening it.

### Legitimate mid-run expansion

Add an optional structured envelope field:

```json
{
  "scope_expansion": {
    "requested_paths": [
      "tests/test_reduce.py",
      "tests/test_nvidia_node_integration.py"
    ],
    "reason": "Post-#49 union makes three assertions stale.",
    "blocked_work": "Canonical verification and final acceptance.",
    "minimal_change": "Three assertion-only substitutions."
  }
}
```

A compliant request produces `run_status=NEEDS_SCOPE`, not `SCOPE_VIOLATION`.

The lead then runs something like:

```text
codex-run-v3 resume <run_key>
  --approve-scope-add '["tests/test_reduce.py","tests/test_nvidia_node_integration.py"]'
  --approval-note "Required post-#49 assertion composition"
```

The runner should:

- Append `scope_expansion_approved` with old/new scope and approval note.
- Resume the recorded session UUID—not `resume --last`, which is unsafe under concurrency.
- Inject the amended scope prominently.
- Generate a new preventive profile.
- Preserve the already-completed in-scope work.
- Maintain both per-attempt and cumulative deltas from the original baseline.

This would have cost the composition case one short approval/resume turn, not the whole session. Retroactive acceptance of useful edits should remain “content accepted, process violated.”

## D. Preventive sandbox enforcement

Yes—current Codex has beta **permission profiles** with path-level `read`, `write`, and `deny` rules. More-specific rules override broader ones. They are supported on macOS, Linux/WSL, and Windows, with platform caveats. [Official permissions documentation](https://learn.chatgpt.com/docs/permissions).

The older setting:

```toml
sandbox_workspace_write.writable_roots = [...]
```

only adds writable roots. It does not make the main `-C` workspace read-only except for selected files. It cannot enforce your desired boundary.

A generated profile should resemble:

```toml
default_permissions = "codex_run_scope"

[permissions.codex_run_scope.filesystem]
":minimal" = "read"
":tmpdir" = "write"
":slash_tmp" = "deny"

[permissions.codex_run_scope.filesystem.":workspace_roots"]
"." = "read"
".github/workflows/ci.yml" = "write"
"pyproject.toml" = "write"

[permissions.codex_run_scope.network]
enabled = false
```

Translate `directory/**` into an exact writable subtree entry such as `"directory" = "write"`.

Critical integration point: permission profiles do **not** compose with legacy sandbox settings. Passing `-s workspace-write`, setting `sandbox_mode`, or loading it from a config layer makes Codex use the old sandbox instead. The current runner passes `-s "$SANDBOX"` for fresh runs and `-c sandbox_mode=...` for resumes, so both paths must change. Use `--strict-config`, a runner-controlled config layer, and a real denial integration test. Never silently fall back to broad workspace-write.

Sharp edges:

- Set a unique out-of-repo `TMPDIR` per run.
- Set `PYTHONPYCACHEPREFIX`, `XDG_CACHE_HOME`, package-manager caches, build directories, and test temp roots under that directory.
- Configure pytest’s `cache_dir` and `basetemp` out of tree.
- Hard-coded repository scratch directories must be explicitly in `WRITE_SCOPE` or the test should fail.
- Atomic-write tools often create a sibling temp file and rename it; exact-file permissions may reject them. Prefer patch/direct-write workflows or explicitly scoped scratch paths.
- `__pycache__`, `.pyc`, `.pytest_cache`, coverage data, snapshots, compiled assets, Cargo `target`, and Node caches are repository writes unless redirected.
- Reject allowlisted paths with symlink ancestors unless their resolved targets are validated.
- Git index/commit operations need `.git` writes and should remain unavailable to delegated workers.
- Permission profiles govern local sandboxed execution, not arbitrary connectors, MCP filesystem tools, Computer Use, or approved escalations; disable alternate write surfaces in delegated runs.
- Keep the post-hoc gate even with prevention because permission profiles are beta and ignored/generated-path observability still matters.

## E. What the lead is doing that invites overreach

Candidly:

- “Follow root AGENTS.md” plus “allowed production footprint” invited CI-002’s bookkeeping edits.
- Requiring an in-repo run report inside an implementation prompt implicitly authorizes another write surface. Prefer the runner’s outside-worktree output; let the lead create the authoritative repository report afterward.
- Combining implementation, canonical green-suite completion, bookkeeping, and report publication in one session creates competing completion incentives.
- “Leave pure-B untouched” plus a post-merge union that makes pure-B assertions stale creates an impossible finish-without-expansion condition. The prompt needed either those test paths in scope or an explicit expected stop.
- Retroactively approving useful expansions risks teaching the workflow that “edit, disclose, and ask forgiveness” succeeds. Separate patch merit from process compliance in the ledger.
- Hour-long ultra sessions with large intake documents need a scope reminder after compaction or major phase transitions.
- Shared or pre-dirty worktrees make ownership ambiguous and make safe cleanup impossible.
- Treating a transport-successful session with an empty report as successful is too forgiving. The catastrophic RED round should have failed on missing report and independently failed on actual diff scope.

My strongest immediate recommendation: implement fail-on-actual-diff first, add the two exact standing-language blocks, stop asking delegated workers to touch state/queue files, and then enable generated permission profiles as defense in depth.