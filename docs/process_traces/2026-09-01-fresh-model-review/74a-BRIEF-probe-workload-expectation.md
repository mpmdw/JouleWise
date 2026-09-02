ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["scripts/generate_g2a_probe_inputs.py", "tests/test_generate_g2a_probe_inputs.py"]

# main is RED: G2-a probe workload vs the realized-prefill v5 workload (cross-PR integration, #257 × #258)

Checkout: `/Users/edr/code/JouleWise-wt-probe-fix` (branch
`fix/2026-09-02-probe-workload-expectation`, base = `origin/main` HEAD; report
`git rev-parse HEAD`). LINKED WORKTREE: do NOT commit, stash, checkout, rebase
or push; leave the tree dirty. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Do NOT run canonical `unittest discover`. Run only
`python3 -m unittest tests.test_generate_g2a_probe_inputs tests.test_d117_contrast_v5_pack`
(today: 22 tests, errors=1, skipped=1 / 28 OK).

FORBIDDEN (NEEDS_SCOPE if a passing chain needs them):
`configs/campaigns/d117_contrast_v5/generate_configs.py` (frozen registration
bytes; its arm-aware `workload_for` at `:1324-1352` is the AUTHORITY you match,
never the thing you change), `joulewise/**`, anything under `runs*/`.

## The defect

`tests/test_generate_g2a_probe_inputs.py:444`
`test_probe_workload_shape_matches_v5_prefill_except_diagnostic_name` calls
`d117_v5.workload_for("prefill")` with no arm. PR #258 (D-166 realized prefill
check, ruling
`docs/process_traces/2026-09-01-fresh-model-review/44c-RULING-realized-prefill-check.md`)
made the v5 prefill workload arm-aware: it now carries
`prompt_token_expectation = {schema_version: "joulewise.prompt_token_expectation.v1",
token_hash_domain: "joulewise.prompt_token_ids.v1", token_count: len(PREFILL_TOKEN_IDS[arm]),
token_ids_sha256: PREFILL_TOKEN_IDS_SHA256[arm]}` and refuses a missing arm
(`prompt_realization_registration_missing: prefill arm`). PR #257 (the probe)
merged beside it; main's CI is red on this one test (also visible on PR #265).

## What to do — the magistrate's preferred shape, with licence to disagree

The probe ladder rungs already carry realized `prompt_token_ids` and
`prompt_token_ids_sha256` (`scripts/generate_g2a_probe_inputs.py:97-98`,
computed via `joulewise.provenance.prompt_token_ids_sha256`). Give the probe
workload (`:484-490`) the SAME `prompt_token_expectation` block, built from the
rung's realized ids, so the probe run is checked by the harness exactly as a
claim-bearing prefill run is — the probe is diagnostic, but it should exercise
the same path. Then make the test call `workload_for("prefill", arm)` for an
arm whose `PREFILL_TOKEN_IDS`/`PREFILL_TOKEN_IDS_SHA256` are patched to the
rung's ids (extend the existing `mock.patch.multiple`), and keep the
except-name shape equality STRICT (no key exclusions).

Before you build it, verify and REPORT: (1) that the probe's
`prompt_token_ids_sha256` and the v5 generator's `_token_ids_sha256` produce the
same digest for the same id list (same domain string — cite both lines; if they
differ, that is a NEEDS_RULING, not something to paper over); (2) where the
harness consumes `prompt_token_expectation` at run time (grep `joulewise/` for
the key) and what it does on mismatch — state whether adding it to the probe
changes probe-run behaviour beyond adding the realized check; (3) whether the
by-name pin/mismatch refusals in the probe issuer (`f16e3bd9`) already cover the
ids you will now expose in the workload. If you conclude the probe should NOT
carry the expectation (e.g. the harness would refuse probe runs for a reason you
can name), return `NEEDS_RULING` with the argument instead of choosing the
weaker fix (excluding the key from the comparison) on your own.

Regression evidence is EXECUTED: the amended test must FAIL on a TMPDIR copy of
the base with your test file copied over (paste the failing line) and pass
after. Add one test that the probe config's `prompt_token_expectation.token_count`
equals the rung's `prefill_tokens` and its sha equals the rung's
`prompt_token_ids_sha256`. Mutant: probe emits the expectation with
`token_count` off by one → which test fails.

## Report

`claude-codex-report/v1` envelope first, genre `implementation`. Under 60 lines:
the three verification answers with file:line; the executed pre-fix failing line;
the mutant result; the exact test commands and tails (22 → N OK; 28 OK).
