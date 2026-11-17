Committed and pushed **`9ef385b9f`** to `origin/audit/2026-11-10-fable`, with the required co-author trailer. Worktree is clean.

Both findings are fixed across all 30 unissued draft forms.

| F2 item | New date, PST | Draft status |
|---|---|---|
| p01 | Tue Nov 17 | READY |
| p02 | Wed Nov 18 | READY |
| p03 | Wed Nov 18 | READY |
| p04 | Fri Nov 20 | READY |

Live issuance prerequisites remain pending; READY counted/v4 work retains priority.

All three runners passed under **bash and zsh**, including pinned checks, mocks and staging. The universal regression passed **960 checks**.

Issued items **354, 355, 366, 367 and 372** all carry the defect, reproduced in both shells. Normal append-only closes preserve order; restoring, copying back or touching an older receipt can trigger it. No live occurrence is inferred.

RUN_STATE.md and prior evidence are unchanged. No MBP contact or custody access occurred. [Full report](/Volumes/JW-EXT/jw-wt/sol-f2-fix/docs/run_reports/2026-11-16-f2-item-fixes.md) includes the ancillary process-census limitation (`ps` denied).