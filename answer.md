# WP20b handoff — complete

Applied all three WP14 rulings in [protocol v4](docs/align/pilot_protocol_v4.md),
citing `a17ed96c8` and §§(a)–(c): the model-free sensor classifier,
capture/consume reference custody, and cited CLI registry selection.
Zero PENDING-RULING blocks remain. Every section is retained; six unrelated
sections are byte-identical. Ed's R1 High Power A-B-A requirement remains
explicit: exactly `pmset -c powermode 0` and `pmset -c powermode 2`, with
Automatic restoration on every exit path and refusal if restoration is unavailable.

Branch: `lane/2026-11-05-align-v4-wp20-protocol`. Continued from actual
HEAD `8c6e9f450`, preserving the earlier WP20b commits after `262ff28a4`.
New protocol commit: `687257f35` — `docs(align): install WP14 rulings in protocol v4`.
The subsequent handoff commit is named
`docs(align): complete WP20b handoff after source verification`.
No push. List the new commits with `git log --oneline 8c6e9f450..HEAD`.
Earlier `d93029c7e` contains Ed's power-rule wording; the source blocker
recorded in `8c6e9f450` is now resolved.

Verification:

- `python3.13 -B /private/tmp/jwsol/v4-wp20b-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md answer.md`
  — PASS: **3 Markdown files, 6 local links, 128 citation ranges / 10 sources**,
  2 parsed reference forms, zero pending-ruling blocks, all section headings
  retained, 6 unchanged sections, formatting, source pins and protected-file scope.
- Committed WP14 bytes equal `/private/tmp/jwsol/v4-wp14-rulings.md`;
  the pinned plan is a byte-identical prefix of the current plan — PASS.
- `git diff --check`, `git diff --cached --check`, and
  `git diff 262ff28a4..HEAD --check` — PASS.
- Unit tests: **0 run, 0 skipped**. Native tests: **0 run, 0 skipped**.
  Doc-only; no full suite, model execution, hardware work or real-data reads.
  The run report lists the lead's separate integration-native obligations.

Files touched: protocol, answer.md and the existing WP20b
[run report](docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md).
Coordination state and kernel tasks remain untouched.

No new ruling is needed to finish WP20b. Implementation/native qualification,
Ed's sudoers installation and restore verification, and the protocol's blind
registration gate remain pending with their owners. The legacy source prose
still says “Proposed location” / “Nothing was committed”; its actual committed
bytes are now verified. Next: lead reviews these commits, integrates them with
WP14/WP15–WP17, and completes the separate registration/live gates.
