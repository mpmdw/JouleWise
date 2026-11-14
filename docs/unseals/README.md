# Owner unseal records

RL-53 W-8 makes each future unseal a committed owner instruction bound to a
particular verdict. This is an accident guard; custody remains a rule.

Write `docs/unseals/<block>-<YYYYMMDD>.json` with exactly these fields:

- `schema`: `joulewise.unseal_record.v1`.
- `given_by`, `given_at`: owner name and ISO timestamp with an offset.
- `words`: the owner's non-empty words, verbatim.
- `block`: block/release identifier, such as `block6` or `align-v4-W1`.
- `verdict_sha256`: the verdict file's 64-hex SHA-256 digest.
- `verdict_path`: repo-relative or custody-relative text; the reader never opens it.
- `paths_opened`: non-empty list of exact relative paths or fnmatch globs.
- `stays_sealed`: list of relative paths/globs, present even if empty.
- `seats_may_read`: non-empty list of seat or role names.
- `recorded_by`, `recorded_at`: recorder name and ISO timestamp with an offset.

Validate with `joulewise.unseal_record.load`, then commit the record. Unknown
keys, empty patterns, absolute paths and `..` segments refuse. Matching uses
normalized POSIX paths, is case sensitive, and follows fnmatch (`*` spans `/`).
`stays_sealed` wins. Patterns and `verdict_path` are never resolved or opened.

Before displaying outcomes, run:
`python3 scripts/show_outcomes_guard.py check --block B --verdict V --path P`.
The explicit verdict file is read only to hash its bytes. The check is silent
on exit 0, prints a refusal code on stderr at exit 1, and uses exit 2 for usage.
Omitting `--path` checks only the block/digest permission. Seat names preserve
the owner's instruction; this CLI does not authenticate its caller's role.

The selected record must match its regular-file blob in local Git `HEAD`.
Untracked or edited matching records refuse, as do ambiguous matches. A new
verdict digest needs a new unseal; records do not confer permission by date.

Block 5's unseal predates this rule and has no record. Its release tool keeps
its existing behavior. BYTES keeps its commitment journal instead.
