# 37 — Opus counter-review, CONTRACT lens: partial-record enclosure

Seat: Opus, contract lens. Branch `feat/2026-09-04-estimand-enclosure` vs
`origin/main`. Counter-reviews 32 and refuter 35 (NOT REFUTED). Governing: 43
§Q-17-1, cold ruling 41 §Q-17-1, estimand clause `decision_log.md:10949-10951`.

## Executed evidence (this session, this worktree)

- `git diff origin/main -- joulewise tests/goldens docs/contracts` → **empty,
  exit 0**. Q(1) answered: reducer, goldens, contracts byte-identical to main.
  Branch diff: 6 files, +855/-0 — registry (+1 line), script, test, 3 traces.
- `python3 -m unittest tests.test_partial_record_enclosure -v` → **Ran 8, OK**.
- `import scripts.render_results_fills` → `PE-01 in REGISTRY_ROWS` is **False**,
  86 rows unchanged; the row regex (`scripts/render_results_fills.py:106`)
  matches only backticked-token rows, so the new row cannot mis-license a fill.
- `shasum -a 256 scripts/paper/partial_record_enclosure.py` →
  `2d3e2c6bd83b5795d08ab8a6721eafde210e54831afb4c686a053ee6dba8aa05`, 10 642 B.

## Q(3) authentication path — PASS

No raw JSON for inputs (`json` only for stdout `dumps`). It reuses the installed
strict layer: `scripts/paper/partial_record_enclosure.py:267`
`with V2AuthenticationReadSession():` (same class as
`joulewise/window_duration_margins.py:941`,
`scripts/mint_floor_artifact_generalized.py:1766`); `:222,224-228` `BundleReader`
with typed `config()`/`metadata()`/`events()`; curves and windows via
`summed_curve` (`joulewise/bundle_read.py:352`) and `phase_windows` (`:576`) —
both citations verified; `:241` `validate_bundle(bundle, strict=True)`; `:179`
digests via `sha256_authentication_input` (`joulewise/authentication_io.py:605`).
Non-composition is structural, not merely asserted: the script writes no
artifact (stdout only) and nothing under `joulewise/` imports it.

## Q(4) fixed-window scope — PASS

In the output (`"scope": FIXED_WINDOW_SCOPE`, `:149`, constant `:47`), enforced
by the absence of any window-selection argument (`_parser`, `:273-276`),
asserted at `tests/test_partial_record_enclosure.py:158`, and named in the row's
supplier column plus its `FIXED_WINDOW_ONLY` label.

## Findings

**C-1 — BLOCKER. The row does not pin the "PINNED DESK SCRIPT."**
`docs/paper/results-fill-registry.md:922` names the script path with no digest.
This registry already has an installed producer-pin grammar — lines 739/742
(`- XS = scripts/paper_excursion_decomposition.py, sha256 12d0293b…`; likewise
`AS`), machine-checked at `scripts/check_paper_round7_artifacts.py:105,347,377`.
As landed, any later edit to the script silently changes what the DERIVE row
authorises.

Preferred cure (in-file, no new tooling — the registry already pins digests
inline, e.g. DG-071 at `:646`): insert into the supplier cell after the path —

> `` , SHA-256 `2d3e2c6bd83b5795d08ab8a6721eafde210e54831afb4c686a053ee6dba8aa05`, 10,642 B ``

Do **not** instead add a `- PES = …` line to the abbreviation block at
`:737-742`: that block is R7-scoped and its checker's `SOURCE_RE` enumerates only
`XD|XS|F4|AQ|AS`, so such a line is unchecked decoration unless
`scripts/check_paper_round7_artifacts.py:105` is widened too.

Alternate reading: "pinned" in Q-17-1 may mean "pinned to this submission", not
a reducer field — under which this is should-fix. The magistrate should settle
it; the cure is one cell edit and re-runs nothing either way.

**C-2 — BLOCKER. No committed regression that a tampered bundle is refused.**
Q-17-1 requires *authenticated inputs*. All eight landed tests drive
`enclose_phase` or the clean fixture; none exercises
`bundle_strict_validation_failed` (`:241-245`), digest drift,
`bundle_not_real_directory` (`:155-158`), `bundle_census_nonregular_member`
(`:174-177`), or `phase_summary_window_mismatch` (`:248-252`). The only tamper
evidence is refuter 35's ephemeral desk probe
(`injected_digest_drift=v2_authentication_input_changed`), not in the repo.
Proposed test (adds `shutil`, `tempfile`): `copytree` the tracked
`strict_seed_bundle` fixture to a temp dir, mutate
`summary_metrics.json["phase_energy_j"]["decode"] += 1.0`, then assert
`enclosure.derive_bundle(bundle)` raises `EnclosureRefusal` with `reason` in
`{"bundle_strict_validation_failed", "v2_authentication_input_changed"}` — the
repo-resident form of refuter 35's drift probe.

**C-3 — SHOULD-FIX. Non-composition wording narrower than ratified.** Ratified
(`decision_log.md:10949-10951`): "it is **reported, never composed into any
bound**." The row says "never compose the diagnostic into a floor, uncertainty
term, or claim bound" — three enumerated kinds, inviting the reading that a
fourth is permitted. Replace that clause with the ratified words:
`; the diagnostic of allocation ambiguity at the registered window is reported, never composed into any bound`

**C-4 — SHOULD-FIX. Row grammar deviates from its own table.** The column is
*Exact marker or anchor*; OB-01, TR-01 and OR-01 each put a backticked token
there and each carry `TOKEN_MISSING` for exactly the state PE-01 is in. PE-01
puts prose there and omits `TOKEN_MISSING`. The preamble (`:915-918`) also scopes
these rows to placements added to `draft-v2-skeleton.md`, which PE-01 has none
of. Proposed: marker cell → `` `[FILL:PE-01]` ``; add `TOKEN_MISSING`.

**C-5 — SHOULD-FIX. Three invented freeze labels.** File census: bare
`APPENDIX_ONLY` once (this row) vs 20 `APPENDIX_ONLY_REGISTRY_BOUND`;
`FIXED_WINDOW_ONLY` and `NON_CLAIM_BOUND` once each, vs 53 `NON_CLAIM_BEARING`.
Proposed freeze cell:
`SUPPLIER_NAMED / VALUE_UNISSUED; TOKEN_MISSING; APPENDIX_ONLY_REGISTRY_BOUND; NON_CLAIM_BEARING; FIXED_WINDOW_ONLY`
— keeping only `FIXED_WINDOW_ONLY` as new, defined once in Rules.

**C-6 — SHOULD-FIX. Sources cell mis-cites its authority.** `AUTH` is defined at
`:90` as "D-119 and D-121 through D-124". None authorises this row; the authority
is gate-17 Q-17-1 plus D-174, under which registry listing is what makes the
figure "selected" (Q-17-5). Cite `AUTH, D174`; add the `D174` key if undefined.

**C-7 — SHOULD-FIX. Refusal reasons string-sniff a frozen module.** `:235-238`
picks the machine-readable reason via `if "power_w" in detail and "finite" in
detail` on a `BundleReadError` message. `joulewise/` is frozen byte-identical to
main by this ruling, so main may reword that message and silently reclassify a
non-finite refusal as `bundle_read_failed`. Catch the reader's typed condition,
or drop the special case and emit `bundle_read_failed` with the detail attached.

**C-8 — NIT. Wrong file:line, repeated in seat report 32.** The docstring (`:9`)
and report 32 cite the integration function as `joulewise/reduce.py:157`;
`_integrate` is at `reduce.py:167` (157 is inside `_interpolate`, `:150`). PD-1.

**C-9 — NIT.** `:43` imports the private `joulewise.reduce._integrate`; nothing
contracts that name and the branch may not edit `joulewise/`, so a rename on
main breaks the desk script with no test on main catching it.

**C-10 — NIT (overbuild, keep).** `bundle_not_real_directory` (`:155-158`) and
`bundle_census_nonregular_member` (`:174-177`) are operator-adversary refusals of
the kind D-161 prunes; they sit in the evidence carve-out (guarding a digest
census), so keep — flagged only so this is not read as precedent elsewhere.
Nothing else is overbuilt: the census, `phase_summary_window_mismatch`, and the
window union each earn their place under "each record counted once".

## Verification tail

`python3 -m unittest tests.test_reduce` in this worktree: **Ran 132 tests in
346.676s — OK**, exit 0. Matches refuter 35's `132 / 348.886s / OK` at the same
head, as expected given the empty protected-path diff.

## Verdict

**NOT LANDABLE as-is** — on C-1 and C-2 only, both cheap and local: one
supplier-cell digest and one test. Neither touches `joulewise/`, goldens,
contracts, or any number. C-3 to C-6 should ride the same edit; C-7 to C-10 may
be deferred. With C-1/C-2 cured (C-1 downgradable if the magistrate reads
"PINNED" as "this submission only"), the landing satisfies 43 §Q-17-1 and is
**LANDABLE**.
