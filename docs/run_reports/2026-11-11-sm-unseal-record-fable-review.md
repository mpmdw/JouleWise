# Fable cold review: `sm-unseal-record` (RL-53 W-8; audit section 8.2 item 7)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 04:40 PST. Reviewed head `981c7d506`
(`feat/2026-11-11-sm-unseal-record`, base `origin/main`). Builder: Sol xhigh, one round.

**Verdict: ADMIT.** One follow-up is named below; it is on another branch and does not block this merge.

## What the PR does

- `joulewise/unseal_record.py`: the record the research lead asked for in RL-53 W-8. One JSON file per unseal in
  `docs/unseals/<block>-<YYYYMMDD>.json` with exactly these fields: who gave it and when, the owner's words, the
  block, the SHA-256 of the verdict it follows, the paths it opens, what stays sealed, which seats may read, and
  who recorded it.
- `require_unseal(...)`: finds the one record for a block whose digest equals the given verdict's. It refuses
  when there is none, when the digest differs (a new verdict needs a new unseal), when two match, when a
  requested path is not opened or is listed as staying sealed, and when the matching record is not the committed
  blob at `HEAD` (an edited or untracked record gives no permission).
- `scripts/show_outcomes_guard.py check --block B --verdict V [--path P]`: hashes the verdict file given on the
  command line and asks `require_unseal`. Exit 0 allowed, 1 refused, 2 usage.
- `docs/unseals/README.md` says how to write a record. No record is added: Block 5's unseal predates the rule,
  and BYTES keeps its commitment journal.
- `scripts/release_b5.py` is unchanged.

## What I did

- Read the module (248 lines), the guard (46 lines) and the README.
- Ran `python3.13 -B -m unittest tests.test_unseal_record`: 31 tests, OK, with the default temp directory.
- Checked that neither program opens, resolves, globs or stats any path named inside a record; only the record
  files and the verdict passed on the command line are read. The tests count opens to prove it.
- Mutation-tested ten points, ten killed: `stays_sealed` ignored; `paths_opened` ignored; any digest accepted;
  the committed-at-HEAD check removed; ambiguity accepted; `..` accepted in a path; unknown keys accepted; any
  block accepted; an edited record accepted against its committed blob; a symlinked record accepted.

## Findings

- **S-1 (follow-up, another branch).** No v4 or Block 6 tool calls the guard yet. The release tools are on
  `align/2026-11-08-v4-release-tools`, which this PR does not touch. The seat's report names the call sites:
  `scripts/release_v4.py` before any outcome display, `scripts/compare_v4_recompute.py` before its restricted
  output is shown, and `scripts/b6_unblind.py` after argument parsing. Disposition: a seat on that branch once
  the orchestrator says which line the release tools will ship from.
- **S-2 (informational).** Patterns use `fnmatch`, so `*` also matches `/`. The README says so. A record that
  opens `derived/*` opens everything below `derived/`. Writers should list what stays sealed explicitly.
- **S-3 (informational).** `seats_may_read` is recorded, not enforced: the guard has no way to know which seat
  is calling. The README says so. It is a guard against accident, as the ruling describes.

## Not covered

- Python 3.11 locally; CI runs it.
