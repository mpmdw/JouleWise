# Fable cold pass: R0 `load` reference equivalence, PR #686 at `711f43731`

Reviewer: Claude Fable 5.1, no prior context on this lane. Range reviewed:
`origin/lane/2026-11-05-align-pilot10-benign` (`f3af22b94`) .. `lane/2026-11-06-r0-load-reference`
(`711f43731`). The executing review (`docs/align/reviews/2026-11-06-r0-load-reference-executing-review.md`,
Opus 5.5) covered `76cc22b7c`; commit `711f43731` after it is unreviewed and got the closest reading.
Evidence branch `lane/2026-11-06-r0-d-nll-diagnosis` @ `62bc719f7` was read from its own worktree.

## Verdict: ADMIT_WITH_FIXES

- No BLOCKER.
- One HIGH, introduced in the unreviewed commit `711f43731`: a non-finite NLL (the broken-runtime case
  the check exists for) now crashes the runner before the `load` verdict is written, leaving the
  record at `status: running`. It is not fail-open, but the designed `nll_not_finite` verdict is
  unreachable in a live run. One-line fix plus a runner-level test. Fix before the next live R0.
- Two MEDIUM: the main spurious-fail path for a healthy D (one greedy xhigh turn with a hard 4,096
  cap, untested on D, stops the whole R0), and the report's `authority` fields still naming
  FINAL-DESIGN §2.1 as the load bar's authority.
- Everything else checked holds: reference numbers recompute exactly from the evidence JSON, the
  provenance hashes match the diagnosis branch, the fail-closed paths behave, the D-pin exemption
  is narrow, no measurement path changes, and all six touched test modules pass in both
  interpreters.

## Findings

| Sev | Where | Finding | Action |
|---|---|---|---|
| **HIGH** | `joulewise/align/r0.py:456` (`"nll_losses": losses`, added in `711f43731`); `joulewise/align/r0_runner.py:89` (`allow_nan=False`), `:151-152` (`finally: progress({})`), `:241` | `load_coherence` now returns the raw 2,048 per-target losses. `nll_verdict` sanitizes mean and bins (`None`) and returns `nll_not_finite`, but the raw vector reaches the row. `save_report` serializes with `allow_nan=False`, so one NaN or inf loss raises `ValueError` inside `receipt`'s `finally: progress({})`. The exception escapes `receipt` (no `_StopChecks`, no `row.status`), the outer `except Exception` sets `report.status = fail`, and the outer `finally: save_report` raises again, so `execute` and `main` exit by traceback. **Reproduced** with the test `FakeBackend` through `r0_runner.execute(checks=["load"])`: for `[nan]*2048` and `[inf]*2048` the process raises `Out of range float values are not JSON compliant` and the on-disk `report.json` is left at `status: running`, `load: running`, with no `nll_verdict` reason; for a finite failing value the report records `load: fail` normally. Base `f3af22b94` recorded `nll_nats_per_token: None` and `fail` for the same input. A NaN forward pass is exactly the broken runtime/artifact case this check exists for, and the adversarial test (`test_empty_overflowing_and_mixed_nan_losses_never_pass`) covers `nll_verdict` only, not the report path. | Store `nll_losses` only when all values are finite (or map non-finite entries to `None`); the digest in `loss_profile.losses_sha256` already fixes the vector. Add a runner-level test that a NaN loss vector yields an on-disk `load: fail`, reason `nll_not_finite`. |
| **MEDIUM** | `joulewise/align/r0.py:381-404` (`generation_check`), `:38` (`GENERATION_CAP = 4096`), `:350` (`hit_cap`); `joulewise/align/r0_runner.py:22` (`load` not in `ACCEPTED_OUTCOMES`) | The main spurious-fail path for a healthy D. The generation bar is one greedy turn at the template default (renders as xhigh: the rerun NOTE places "Reasoning effort is set to xhigh" at tokens 40-100 of this very prompt) over the 41-tool SHADE prompt, and it must finish under 4,096 tokens with reasoning closed. There is no D generation evidence anywhere on this stack: the 2026-11-06 rerun stopped at `load`, and no pilot has run D. The protocol's own xhigh ladder rung tolerates up to 20% of turns hitting the cap and a median reasoning of up to 2,048 tokens, so by the protocol's expectations a single xhigh turn has a material chance of hitting 4,096 without any loop, before Qwen's greedy-loop caveat is counted. A cap hit fails `load`; `load` must `pass` (`ACCEPTED_OUTCOMES`), so without `--keep-going` the R0 stops there, and the note says the fallback (a seeded production sampler) needs a magistrate ruling. Cost of a false alarm is one R0 launch (about a minute plus up to 6-7 minutes of decode at the rerun's 11-12 tok/s) and a ruling cycle on the critical path. Fail-closed and fully recorded, so not HIGH. | Get the ruling now, before the live run, not after a failed one. Options that keep the check deterministic: on `hit_cap`/`unclosed_reasoning` only, record the turn and retry once with the seeded production sampler, both turns recorded; or run the generation turn after the ladder at the selected effort. Either needs the magistrate. |
| **MEDIUM** | `joulewise/align/r0_runner.py:107-112` (`authority`, `authority_amendment`); `docs/align/v4/R0-LOAD-REFERENCE-NOTE.md` §1 | Every report still records `authority: FINAL-DESIGN.md §§2.1,2.2,2.8` and amendment A1/A3/A5 as the bar. After this PR a `load: pass` would fail FINAL-DESIGN §2.1's own bar (D scores 11.04 against 3.0). The note calls itself a protocol change "for the magistrate and Ed under RUN_STATE items 181/183", so the ruling is pending, yet the record will present the new bar under the old authority. The table sha is in `implementation_sha256` and the row records `nll_mode`, which helps, but the header is what a reader uses. | Add the note (commit, blob) and, once given, the ruling to the report's authority fields. Doc/record mismatch, not a correctness bug. |
| LOW | `joulewise/align/r0.py:725` (markdown `brief`) | `nll_prompt_ids` is excluded from the markdown brief because it is a large array, but the new `nll_losses` (2,048 floats), `nll_loss_profile` and `nll_verdict.loss_profile` are not. `report.md` for `load` gains roughly 2,100 lines of floats and duplicated profile blocks. | Add `nll_losses` to the exclusion set; keep the profile and its sha. |
| LOW | `joulewise/align/r0.py:369-372` (`_accepts` call) | Carried from the executing review, still open: a dangling local `$ref` in a tool schema raises `KeyError`, which `except (TypeError, ValueError, RecursionError)` does not catch, so `load` fails by exception rather than by `arguments_schema_invalid`. Fail closed. All 41 real SHADE schemas pass per the executing review. | Cosmetic; add `KeyError`. |
| LOW | `joulewise/align/r0.py:424` | When a caller passes `references=` (the prequal path), `references_sha` is `sha256(json.dumps(references, sort_keys=True))` with default separators, which is neither the file-bytes sha the runner puts in `implementation_sha256` nor `_canonical_sha256`. Two different "table shas" for the same table. Prequal only; the live path reads the file bytes. | Use one canonical form. |
| LOW | `joulewise/align/r0_runner.py:224`, `joulewise/align/r0.py:594` | The greedy generation turn is nested at `load.generation.turn` with `raw_text`/`tool_calls`, so the D `tool-envelopes` receipt now counts it (the note says so). With `--keep-going`, a malformed greedy turn both fails `load` and lowers the tool-envelopes parse fraction. Acknowledged design; recorded here so the double count is not read as two independent failures. | None. |
| LOW | `joulewise/align/r0_mlx.py:45-51`, `joulewise/align/r0.py:179-197` | The reproduction tier keys on `MlxBackend.stack_versions`, which the constructor also pins by `RuntimeError`. So on the measurement Mac the stack can only ever equal the pins, and the first live run is `not_pinned` (no first-run mismatch). The coupling to note: a future pin bump in `r0_mlx.py` with a pinned table makes every run `reproduce_not_comparable` until a reviewed table edit. The note says this. | None; by design. |
| LOW | `configs/align/v4/r0_nll_reference.json` anchor entry | Dormant, as the executing review said: no R0 path can reach the anchor (`r0.PINS` holds D only; `main` refuses `models != {"D"}`). The null-fixture wildcard is now guarded against being a fallback for a revision with other entries. | Re-derive before any anchor use. |

## Checked and found correct

- **Unreviewed commit `711f43731`.** `_validate_reproduce` (r0.py:155-176) requires the pin's sha to
  equal `_canonical_sha256(profile)`, a nonempty `source`, the entry's revision, a sha-shaped fixture
  equal to the entry's (or any, for a null-fixture entry), nonempty string stack versions, 2,048
  targets, finite mean and eight bins averaging to the mean within 1e-6. `reproduction_verdict`
  (r0.py:179-197) fails closed on any missing or unequal `model_revision`, `fixture_sha256`,
  `stack_versions` or `targets`, including a backend that reports no stack, and only then
  compares at 1e-3 / 1e-2. `not_pinned` is reported and does not fail. The `wrong_tool` gate
  (r0.py:366-368) runs after the `unknown_tool` continue, so an unlisted name is still
  `unknown_tool` and a listed wrong name is `wrong_tool`; arguments are validated either way.
  `test_load_check_records_the_profile_and_a_later_run_reproduces_it` pins from
  `json.loads(json.dumps(report))`, so the operator's copy-from-report path round-trips
  bit-identically (Python float repr round-trips).
- **Reference numbers.** Recomputed from `results/qwen38_27b_stream.json` on the diagnosis
  worktree: `variants.hf32.start_0` has 2,048 per-token losses, mean 11.0642, bins
  4.5679 10.2525 10.3264 7.9248 13.1373 15.4235 15.8555 11.0259, exactly the shipped entry;
  deltas against hf32: mlx16 0.0211 / worst bin 0.2425, mlxq8 and mlxD 0.0286 / 0.2552, the
  two bit-identical, as the note and the test constant `D_MLX_BINS` state. The shipped bins
  average 11.064225 (validator tolerance 1e-3 against 11.0642).
- **Provenance hashes.** On `62bc719f7`: `scripts/stream27.py` sha256 `4af4fd79…bd642`, git blob
  `2e400192…af260`; `results/qwen38_27b_stream.json` sha256 `da18045e…85c4`;
  `results/per_layer_divergence_27b.txt` sha256 `a40e04d2…e0f2`. All match the table and the note.
- **Fail-closed paths.** Missing/unreadable/malformed table (`OSError`/`ValueError`, which covers
  `JSONDecodeError` and `UnicodeDecodeError`) gives `invalid_reference_config`; any other exception
  propagates and the runner records `fail`. No entry gives `no_reference` with no absolute fallback
  (`reference_entry` matches a null fixture only for `absolute` mode, and the validator forbids a
  null-fixture entry beside any other entry for its revision). A backend without `config.model.revision`
  and without `nll_reference_revision` resolves to `None`, which matches no entry. Entry lookup
  precedes the finiteness and count checks, so an unlisted model never gets a verdict on its
  numbers. `_finite` rejects bools. A changed template or tokenizer changes the fixture sha and
  therefore fails closed; a prompt shorter than 2,049 ids raises.
- **Greedy path.** `new_session(None, greedy=True)` builds `MlxEndpoint(sampler=None)`;
  `MlxBackend.chat` (r0_mlx.py:120) refuses a greedy/sampled mismatch in both directions and passes
  `temperature=0.0, seed=None`, which `MlxEndpoint.chat` (endpoint.py:541-546) accepts without flags;
  `generate_turn` gets no `sampler_policy`, the pinned greedy path. Every later check calls
  `new_session(...)` before chatting (r0.py:412, 431, 469, 491, 567), so the greedy session cannot
  leak into the ladder or long-decode. The short and echo diagnostics still run on the production
  sampler, so the sampled decode path is still exercised in `load`.
- **Effort rendering.** The ladder's xhigh rung passes no kwarg (r0.py:567); `generation_check`
  passes `None`, the same code path. The rerun NOTE finds the rendered prompt's system line
  "Reasoning effort is set to xhigh" at tokens 40-100 under the template default, which is the
  direct evidence that default == xhigh bytes (WP7 LOW said the same for the kit).
- **Generation verdict.** `tool_envelopes([row])` counts `<tool_call>` opens in the endpoint's
  visible text, so a call inside reasoning, a dangling second envelope, a malformed envelope, an
  unknown function, a wrong type and a missing required argument all fail (adversarial tests and
  canned-output tests exercise the production `parse_completion`/XML parser). `hit_cap` fails even
  with a parsed call. JSON-family envelopes are validated by the check itself.
- **Deadline.** `per_check_timeout` defaults to 7,200 s (runner and CLI); the whole `load` composite
  (short, NLL, two echo turns, one 4,096-token greedy turn) stays well inside it at the rerun's
  decode rate.
- **No measurement-data change.** `MlxEndpoint` is untouched. `MlxBackend.new_session` and `chat`
  gain keyword-only `greedy=False`; existing callers render and sample exactly as before.
  `nll_losses` is the previous 128-token single-cache loop with per-target evaluation
  (`mx.eval(losses, …)` instead of the sum); `nll()` is its mean. Only R0 uses it.
- **Other R0 checks.** `template`, `generated`, `ladder`, `long-decode`, `memory`, `smc` are
  unchanged. `tool-envelopes` gains the one greedy turn (LOW above). `implementation_sha256` gains
  the table bytes; the verdict row records the sha of the bytes actually read.
- **D-pin verifier (`f1ae2d3be`).** Only root-level `.cache/huggingface/` is exempt; `.cache/other`,
  `cache/huggingface` and `sub/.cache/huggingface` still fail. Pinned files are still matched by
  size and LFS sha. `bookkeeping()` is only used for the PASS message count.
- **Docs vs code.** The note, runbook and table description agree with the code on modes, keys,
  tolerances, reasons, the `reproduce` block, the greedy session, the cap, the requested-tool gate
  and the effort basis. The note's test list is accurate for the final head.

## Tests run

Each module in its own process, `nice -n 15 taskpolicy -b`, `TMPDIR=/private/tmp/jwfable686-tmp`,
from a fresh worktree at `711f43731` (`/Users/edr/code/CapstoneProject/jw-wt/fable686`).

| Module | venv-both (3.13, mlx 0.31.2) | python3.13 (homebrew 3.13.18) |
|---|---|---|
| tests.align.test_r0_load_reference (24) | OK | OK |
| tests.align.test_r0_load_reference_adversarial (13) | OK | OK |
| tests.align.test_r0_checks (29) | OK | OK |
| tests.align.test_r0_mlx (7) | OK | OK |
| tests.align.test_r0_scheduling (12) | OK | OK |
| tests.align.test_v4_verify_d_pins (5) | OK | OK |

Probe for the HIGH (scratch script, not committed): `r0_runner.execute(config, root, ["load"], ["D"],
guard=FakeGuard(), backend_factory=FakeBackend)` with `nll_losses` patched to `[nan]*2048`,
`[inf]*2048` and `[11.9]*2048` under the fake reference table. The first two raise
`ValueError: Out of range float values are not JSON compliant` out of `execute` and leave
`report.json` at `status: running` with `load: running`; the third returns `fail` and writes
`load: fail`.

## Ultrareview target

`/code-review ultra` on PR #686 (`lane/2026-11-06-r0-load-reference`): an admission-bar protocol
change with a new verdict table and a new generation gate.
