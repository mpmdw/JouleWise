# DOC-008 orchestration.md inserts (staged; NOT yet applied)

Status: DRAFT pending lead adjudication (C-027 spec wave, D-063 Stage 1).

These are the exact subsections that `docs/specs/c027/doc-008_state_kernel.md`
§7 directs to be added to `docs/orchestration.md` "after the
decomposition/per-stream description and before lead live gates." Editing
`docs/orchestration.md` is outside the DOC-008 Stage-1 tooling footprint
(that migration is adjudication-gated), so the drafted text is staged here
verbatim. Apply by copying both subsections into `docs/orchestration.md`
unchanged; then delete this file or mark it applied.

---

### One writer per working tree (the two-writer rule)

At most one process may write a working tree at a time. The lead counts as a
writer: lead bookkeeping, cleanup, formatting, conflict resolution, and
“small” post-review edits may not overlap a worker that can modify the same
tree. Parallel writers require separate worktrees/branches and disjoint
expected diff footprints. Review-only readers may overlap only when their
tools are guaranteed read-only.

Before taking write ownership, the writer must identify the tree and branch,
wait for every prior writer to finish or be explicitly stopped, inspect
`git status --short --branch`, and preserve all pre-existing changes. Before
lead bookkeeping begins, the lead must declare the tree quiescent. No cleanup
or generated-file refresh may run over another writer’s uncommitted work.

If overlap is discovered, stop new writes; capture the branch, HEAD, status,
and diffs for both owners; preserve both versions; and let the lead reconcile
them. Never resolve an ownership collision by discarding or reverting work by
inference.

Writer separation and reviewer separation are distinct. The author of a
change or test may not be its sole fresh reviewer/auditor. Any lead or worker
content edit after the last fresh review creates a new final-head review
obligation. Lead-owned live/hardware gates remain lead-owned and are not a
writer-separation violation.

### Credential-boundary push handoff

“Push green commits promptly” is an outcome, not permission to copy or bypass
credentials. If the current environment cannot authenticate, it must hand the
exact reviewed commit to a named authenticated pusher instead of accumulating
silent local-only state.

The blocked environment must: (1) finish the authorized local checks; (2)
record the repository, branch, remote, exact commit SHA, clean/dirty status,
and review/CI state; (3) name the authenticated pusher and an explicit
ISO-8601 deadline no later than the next dependent session or any claim of
remote/advisor freshness; and (4) record the handoff in the run report and the
live queue. If missing remote state makes restart unsafe, create an active stop
card. Credentials themselves are never transferred.

The authenticated pusher must verify that the received branch resolves to the
recorded SHA, rerun any environment-bound required gate, push that exact SHA to
the named remote/ref, and record the remote ref/SHA confirmation. If the SHA
changes, normal review and final-head rules reapply before push or merge.

Until remote confirmation exists, status must say `LOCAL_ONLY — PUSH PENDING`;
the project must not claim that GitHub, a PR, a deployment, or an advisor-facing
snapshot contains the change. A missed deadline becomes an explicit
`[ED-EXTERNAL]` blocker, not an informal “push when convenient” note.

---

Per the spec: this procedure does not expand commit, push, merge, or
deployment authority.
