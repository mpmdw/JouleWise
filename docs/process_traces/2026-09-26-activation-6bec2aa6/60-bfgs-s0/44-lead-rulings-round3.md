# S0 round 3: lead rulings on the seat's early return (report 43, F1 and F2). Magistrate 6bec2aa6.

Both questions concern the lead's own fix contract `41`. Neither amends cold-ruled text.

**R-F1 (C8(ii) is too broad). Amend C8(ii) to read:**

> (ii) Any call to `dataclasses.replace` (however imported) in a production module that imports `joulewise.battery_float` is flagged **unless** it is in `REPLACE_CALL_ALLOWLIST`: a test-module constant listing the pre-existing calls at base `64e39bb9`. There are nine. Each entry is keyed by `(repo-relative path, enclosing function qualname, ast.unparse(call))`, so an entry does not depend on line numbers.
> - Each entry's reason is `"predates PairVerdict (64e39bb9); cannot receive a PairVerdict"`.
> - The seat verifies that reason for each entry by showing that the replaced object's type is not `PairVerdict`: it quotes the first argument's type or origin at each site.
> - A self-test shows that (a) a new `dataclasses.replace` call in a module importing `battery_float` is flagged; (b) an allowlisted call is not; and (c) an allowlist entry that no longer matches any call fails the test, so the list can only shrink.

No production file outside WRITE_SCOPE is edited.

**R-F2 (the RED-proof rule for C10).** The C10 tests are **regression guards** for properties already true at `26ab7234`: no `skipped` state, no exemption, and the unreadable-kind branch.
- The universal RED-proof instruction applies to closures that change behaviour, not to guards over existing behaviour.
- Mark these tests in the report as "baseline-green guard (C10)".
- To show that each guard is not vacuous, give a mutation proof: temporarily introduce the property violation in a scratch copy (e.g. add `"battery_brackets"` to the exemption tuple), run the guard, show it RED, and revert. Paste the three mutation runs.
