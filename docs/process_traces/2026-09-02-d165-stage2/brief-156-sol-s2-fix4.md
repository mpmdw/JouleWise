ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: implementation
WRITE_SCOPE: ["joulewise/dominance_closeout.py", "docs/contracts/d165_dominance_closeout.md", "tests/test_d165_dominance_closeout.py", "scripts/mint_floor_artifact_generalized.py", "tests/test_mint_floor_artifact_generalized.py", "tests/test_d117_contrast_v5_pack.py"]

# D-165 stage 2 — fix round 4 under ruling 153a (Opus 153 contract lens + terra 152 execution lens)

Checkout: `/Users/edr/code/JouleWise-wt-closeout-s2` (branch
`feat/d165-closeout-stage2-emit`, head `6296ce93`, clean). Do not commit,
rebase, stash, checkout, or push — the magistrate commits. Edit ONLY the
files in WRITE_SCOPE. `TMPDIR` = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`;
scratch copies for mutants go there too. Python:
`/Users/edr/code/JouleWise/.venv/bin/python`. Named test modules only. No
real models. `tests.test_d117_contrast_v5_pack` at most twice.
`configs/campaigns/d117_contrast_v5/generate_configs.py` is NOT in scope and
must not change (its digest `1c0a4a11…` is pinned).

Read first: the ruling (copied below in full), then the two refuter reports:
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/153-opus-s2-contract.md`
(findings F1-F5, N1-N6) and
`…/scratchpad/out/152-terra-s2-exec.md` (F1). The refuters cite file:line on
this exact head.

## Ruling 153a (verbatim — no design latitude beyond what it leaves open)

R-5 (Opus F1, BLOCKER). The refused `common_mode_replay.result` shape
(`dominance_closeout.py:124-132, 791-803, 858-880, 1105-1111`) is DELETED.
Stage 1 fixed `result` at exactly seven keys. Zero denominator is a
malformed close-out input: the mint refuses to emit (the stage-1 fail-closed
path — find out what refusal the pre-`ec761c04` code raised when
`replay_common_mode_dominance` raised `ValueError(DOMINANCE_ZERO_DENOMINATOR_REASON)`
and restore exactly that; if nothing caught it, catch it at the single
build site and refuse with the existing malformed-input refusal, named in
your report). The contract paragraph added at
`docs/contracts/d165_dominance_closeout.md:190-195` is removed and the
deleted sentence justifying `…replay.v1` ("because no production sidecar
was emitted before this exact shape was fixed") is restored at `:144-145`.
Regression (new test): a mint whose replay hits the zero denominator
refuses with the named code, writes NO sidecar, and leaves NO `floor.json`
(rollback holds). Counterfactual input: a common-mode cell whose
corner-widened unguarded floor recomputes to exactly 0 J — construct it by
patching the recomputation in the test, not by changing production.

R-6 (Opus F2). The fixed `/tmp/joulewise-test-d165-phase0-floor-pin` path is
ruling R-4c and is NOT reopened. Docstring change only on the pin test:
say the digest is over the whole `floor.json` file and that the nine
provenance sha256 scalars (list them as now) are the PATH-SENSITIVE inputs,
which is why the literal path is load-bearing. No behaviour change.

R-7 (Opus F3). Clause-10 ownership census: walk every `joulewise/**/*.py`
and `scripts/**/*.py` module except the owner `joulewise/dominance_closeout.py`
and check each module's COMPILED code object (`compile(source, path, "exec")`,
then recurse through `co_consts` into nested code objects) for the literal
`joulewise.d165_dominance_replay.v1` — this catches every compiler-folded
form (plain, `+` chains, adjacent literals, placeholder-free f-strings)
without enumerating syntaxes. Keep the existing four-file map ONLY for the
reference-site assertion (each of the four consumers reaches the schema
through the ruled accessor / lazy read). Delete `_folded_string_constant`
if the co_consts walk subsumes it. Runtime-split forms (`join`, `%`,
`format`) are left open by ruling (D-161). Mutants to execute (scratch
copies): (i) a fifth module `joulewise/_probe_drift.py` containing the
literal via `"joulewise.d165_" + "dominance_replay.v1"`; (ii) the same via
a placeholder-free f-string; both must be KILLED by the census.

R-8 (Opus F4a). Move the `d165_replay_output_required_for_common_mode`
refusal from the bind loop (`scripts/mint_floor_artifact_generalized.py:4159-4171`)
to the estimator-selection gate (`:2614-2636`, immediately after the sink
write) per R-3 "at the first common-mode cell selection"; revert the
contract prose at `docs/contracts/d165_dominance_closeout.md:222-223` to
"selection". Regression: the existing missing-flag test additionally
asserts no bind-stage work ran (recomputation census sink empty or the
bind function never entered — pick the observable that exists).

R-10 nits. N3: `tests/test_d117_contrast_v5_pack.py:694` uses
`DOMINANCE_REPLAY_SIDECAR_ROLE` (import from `joulewise.analysis_manifest_v3`)
instead of the string. N4: `tests/test_d165_dominance_closeout.py:648` —
replace the tautological `validate(...) == []` with an assertion that
`build_d165_replay_sidecar` RAISES on an invalid input (one concrete
malformation). N5: restore the contract's defence-in-depth sentence ("A
finalized manifest without the role is nevertheless fail-closed at its
consumer … `manifest_lacks_replay_sidecar`") next to the refusal list.

R-11 (terra F1). Contract clause-7 wording only: "legacy D-134-form
four-row packs (no `dominance_criterion`) still validate and finalize
byte-identically"; pre-D-134 packs (`as_generated_pre_d134_freeze`) are
outside the promise and are retired by D-167. One sentence; no code.

## Verification (executed; tails in the report)

1. `python -m unittest tests.test_d165_dominance_closeout tests.test_floor_mint_estimator tests.test_mint_floor_artifact_generalized tests.test_analysis_manifest_v3 tests.test_analysis_finalizer tests.test_detection_floor` → OK, counts. `tests.test_d117_contrast_v5_pack` once → OK.
2. R-5 regression: run it; then a mutant that keeps the old refused-shape
   path (restore `_build_common_mode_refused_result` in a scratch copy)
   must FAIL it.
3. R-7 mutants (i) and (ii) KILLED (tails).
4. R-8: mutant that leaves the refusal at the bind site → the amended test FAILS.
5. `grep -rn "refused" joulewise/dominance_closeout.py` shows no
   `_COMMON_MODE_REFUSED_RESULT_KEYS` / `_build_common_mode_refused_result`.
6. `sha256sum configs/campaigns/d117_contrast_v5/generate_configs.py`
   unchanged vs `git show HEAD:...`; `git status --porcelain` lists only
   WRITE_SCOPE files. No `/tmp/joulewise-test-*` leftovers.

## Report

Envelope first (`claude-codex-report/v1`, genre `implementation`), then
under 80 lines: per-ruling change table (file:line ranges), the R-5
refusal name and its provenance (pre-`ec761c04` behaviour), mutant tails,
suite counts. Anything you could not do exactly as ruled: say so, do not
improvise.
