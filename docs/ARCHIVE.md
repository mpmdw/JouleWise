# Archive: files removed from main on 2026-11-06

On 2026-11-06 about 8,100 files were removed from `main` in the hard prune
([run report](run_reports/2026-11-06-repo-prune.md); current tools are listed in
[CANONICAL.md](../CANONICAL.md)). Most were process traces, legacy docs, old run reports and
reviews, and stale campaign configs. A smaller set was dead or superseded code with its
tests.

Nothing was rewritten out of history. The last `main` before the prune is kept in two refs
that will never be deleted or moved:

- tag `archive/pre-prune-2026-11-06` (annotated)
- branch `archive/pre-prune-2026-11-06`

Both point at commit `eeea6d5cfac225bfa3609a9ca443eca66918ca2a`.

## Getting an old file back

```sh
git fetch origin --tags

# read one file
git show archive/pre-prune-2026-11-06:docs/process_traces/2026-10-27-l9-restart/ED-RULING.md

# list what was under a removed folder
git ls-tree -r --name-only archive/pre-prune-2026-11-06 -- docs/legacy/

# restore a folder into a scratch directory (outside the repo, or ignored)
git archive archive/pre-prune-2026-11-06 docs/stream_logs | tar -x -C /tmp/jw-archive

# see when a file was removed, and what removed it
git log --diff-filter=D --oneline -- <path>
```

On GitHub, the same file is at
`https://github.com/mpmdw/JouleWise/blob/archive/pre-prune-2026-11-06/<path>`. Markdown links
in kept documents that pointed at removed files were rewritten to that form.

Plain-text citations of removed paths (for example in `docs/decision_log.md`, `RUN_STATE.md`
or `TASK_QUEUE.md` prose) were left as written. They are history: read them with the
`git show` form above.

## Bringing a file back to main

Only when a live tool reads it or a current runbook needs it. Restore it with
`git checkout archive/pre-prune-2026-11-06 -- <path>`, say why in the PR, and add the reader
to [CANONICAL.md](../CANONICAL.md) if it is the current tool for a job.
