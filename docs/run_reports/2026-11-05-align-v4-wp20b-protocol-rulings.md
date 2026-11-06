# WP20b — protocol rulings source blocked, 2026-11-05

**Partial; NEEDS_RULING on source custody.** Continued
`lane/2026-11-05-align-v4-wp20-protocol` from `262ff28a4`. No network or push.
The three WP14 blocks remain pending in the repository draft; prepared
replacements are preserved outside the repository until their source can be
verified against the committed rulings.

## Changes and commits

- [Protocol v4](../align/pilot_protocol_v4.md): clarified Ed's decided R1
  High Power A-B-A requirement. The narrow sudoers rule permits exactly
  `pmset -c powermode 0` and `pmset -c powermode 2`. It requires `sudo -n -l`
  verification, mode records before/after each segment, Automatic restoration
  on every exit path, and refusal if restoration is unavailable. Every other
  byte of the protocol is unchanged from `262ff28a4`.
- [answer.md](../../answer.md): current worker handoff, replacing the previous
  WP20 handoff. This report records the blocker and prepared continuation.
- Commit `d93029c7e`: `docs(align): make R1 High Power sudo rule explicit`.
  The subsequent local documentation commit is named
  `docs(align): record WP20b source blocker and prepared replacements`.
  Resolve both with `git log --oneline 262ff28a4..HEAD`.

No coordination state, kernel tasks, code, configs, fixtures or tests changed.
The earlier WP20 run report remains unchanged. No agents or consults were
invoked; invocation capture for this worker remains caller-owned.

## Source blocker and prepared work

Both source-availability checks failed with exit 128:

```text
git show-ref --verify refs/remotes/origin/lane/2026-11-05-align-v4-wp14-rulings
git cat-file -t a17ed96c8
```

Origin is an HTTPS remote. Fetching it would violate the task's no-network
rule. No network fetch was attempted. A question requesting the rulings text
or a local Git bundle under `/private/tmp` was sent during work; no answer
had arrived at handoff.

A local chair copy exists at `/private/tmp/jwsol/v4-wp14-rulings.md`, SHA-256
`124d14285d0e42bd384b71336b346a500515b27e85d2f55687dbda95d82a2689`.
It still says “Proposed location” and “Nothing was committed or pushed”. Its
equality to the task's committed source is **unverified**. It was read to
prepare all three replacements, citing WP14 §§(a), (b) and (c), without
admitting that copy as the final committed authority.

Prepared artifacts, not committed or applied:

- `/private/tmp/jwsol/v4-wp20b-protocol-candidate.md`: complete proposed draft,
  with the classifier, reference capture/consume contract, cited CLI registry
  route, source sections and line ranges, stale pending prose corrected,
  and Ed's exact sudo commands. All original section headings and Addendum FN
  are preserved; six unrelated sections are byte-identical.
- `/private/tmp/jwsol/v4-wp20b-replacements.patch`: candidate relative to the
  committed High Power clarification. SHA-256
  `6a66377b6037eb38eb6d505a627aa2f5aa248f3684e51fb1da74424f34605ab3`.
  `git apply --check` passes. Applying it is blocked on source verification.

## Verification and limits

Final repository documentation check:

```text
python3.13 -B /private/tmp/jwsol/v4-wp20b-partial-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md answer.md
```

PASS: **3 Markdown files, 6 local links, 124 citation ranges across 9 pinned
sources**, plan digest, heading/fence/table/whitespace checks, one reserved
Addendum FN, three still-pending ruling blocks, protected-file/write-scope
checks and exact preservation outside the power-rule paragraph.

Prepared-candidate check, explicitly using the unverified chair copy:

```text
python3.13 -B /private/tmp/jwsol/v4-wp20b-doc-check.py --draft-source --candidate docs/align/pilot_protocol_v4.md
git apply --check /private/tmp/jwsol/v4-wp20b-replacements.patch
```

PASS: **1 candidate Markdown file, 2 local links, 128 citation ranges over
9 Git sources plus 1 local draft**, zero pending-ruling blocks, two parsed
reference-role forms, all section headings preserved and six unchanged
sections. Checker output explicitly says `candidate_only: true` and
`rulings_commit_verified: false`. These checks establish syntax/source line
bounds and preservation, not committed-source equality or scientific review.

`git diff --check`, `git diff --cached --check` and
`git diff 262ff28a4..HEAD --check`: PASS. Final scope is the protocol,
answer.md and this report only. Unit tests: **0 run, 0 skipped**. Native tests:
**0 run**. No full suite, compileall, MLX import, model execution, process
census, measurement-data read, analysis pipeline or hardware collection was
run. This is documentation only, and the full suite is expressly prohibited.
No native test is required for the paragraph change; integration-native
qualification remains the lead's separate obligation.

The inherited WP20 checker initially failed because the shared execution plan
had gained the WP4b R0 wall-time appendix. The original cited 340-line plan
is a byte-identical prefix, recovered and hash-verified at
`/private/tmp/jwsol/v4-wp20b-plan-pinned.md`, SHA-256
`528c5217a5e279192bfc69a055a2db8bd5be2c2427d1a3ff2d136b46872e7b9e`.
The new checks use that snapshot; the protocol's existing plan pin stays
unchanged. This caught source drift, not a runtime or numerical defect.

## NEEDS_RULING and next exact step

**Question:** provide a local Git bundle containing `a17ed96c8`, or an
authoritative copy of its `docs/align/council-2026-11-05/WP14-RULINGS.md`.
Can the local chair copy be confirmed byte-identical to that committed file?

**Options considered:** network fetch (prohibited); treating the local draft
as the committed ruling (unverified); importing a local bundle and comparing
the actual committed file (recommended).

**Blocked work:** installing the three prepared WP14 replacements, validating
their final citations against committed bytes, and declaring WP20b complete.
No new scientific choice or Ed power-mode decision is requested. Ed's rule
installation and the driver's restore behavior remain external verification.

**Next:** import the supplied bundle locally, read the committed WP14 file,
compare it to the recorded chair copy, revise the candidate if needed, apply
the prepared patch, and run the candidate checker without `--draft-source`
or `--candidate`. Then commit the three ruling replacements and refresh this
handoff. The blind protocol registration gate and native qualification remain
pending; this work does not authorize arming R1 or W1.
