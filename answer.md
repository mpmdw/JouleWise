# WP20b handoff — source blocked

**Partial.** Clarified Ed's R1 High Power A-B-A ruling in
[protocol v4](docs/align/pilot_protocol_v4.md): exactly
`pmset -c powermode 0` and `pmset -c powermode 2`, narrow sudoers installation,
`sudo -n -l` verification, segment mode records, and Automatic restoration
on every exit path with refusal if restoration is unavailable.

Branch: `lane/2026-11-05-align-v4-wp20-protocol`, continued from `262ff28a4`.
Commit `d93029c7e`: `docs(align): make R1 High Power sudo rule explicit`.
The following local commit, `docs(align): record WP20b source blocker and prepared replacements`,
contains this answer and the [run report](docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md).
No push. Resolve both with `git log --oneline 262ff28a4..HEAD`.

**Blocker:** `a17ed96c8` and the WP14 remote-tracking ref are absent locally
(both availability checks exit 128). Origin is HTTPS; no fetch was attempted
because network is prohibited. A local chair copy exists, but its equality
to the committed rulings is unverified. The repository's three pending blocks
remain intact. Complete replacements are prepared in
`/private/tmp/jwsol/v4-wp20b-replacements.patch`; `git apply --check` passes.

Verification:

- `python3.13 -B /private/tmp/jwsol/v4-wp20b-partial-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md answer.md`
  — PASS: **3 Markdown files, 6 links, 124 citation ranges / 9 sources**,
  formatting, plan digest, Addendum FN, scope/protected files, and every
  protocol byte unchanged outside Ed's power-rule paragraph.
- `python3.13 -B /private/tmp/jwsol/v4-wp20b-doc-check.py --draft-source --candidate docs/align/pilot_protocol_v4.md`
  — PASS on the **unapplied candidate only**: 1 file, 2 links, 128 citation
  ranges / 9 Git sources plus 1 unverified draft, zero pending-ruling blocks,
  six unrelated sections byte-identical and all section headings preserved.
- `git apply --check /private/tmp/jwsol/v4-wp20b-replacements.patch`,
  `git diff --check`, `git diff --cached --check` and
  `git diff 262ff28a4..HEAD --check` — PASS.
- Unit tests: **0 run, 0 skipped**; native tests: **0 run**. Doc-only;
  no full suite, compileall, model/hardware work or real-data reads. Native
  integration checks remain lead-owned; none is required for this paragraph.

**NEEDS_RULING:** provide a local bundle containing `a17ed96c8` or confirm
  the chair copy against its committed file. A local bundle is recommended;
  network fetch is prohibited and the draft is not verified committed authority.
  Blocked: installing the prepared three replacements and their committed-source
  citation check. Next: import locally, compare the rulings, apply the patch,
  check without draft/candidate flags, then commit. No scientific ruling is
  being reopened, and no registration or live-readiness claim is made.

Files touched: protocol, answer.md and the new run report only. RUN_STATE.md,
TASK_QUEUE.md, the state kernel and tests/test_gen_state.py remain unchanged;
no kernel task was registered. The report records source hashes, plan-snapshot
recovery, uncertainties and the precise continuation.
