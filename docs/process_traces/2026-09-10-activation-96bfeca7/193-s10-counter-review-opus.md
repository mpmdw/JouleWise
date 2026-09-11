# 193 — S10 counter-review (Opus, gate row 6, fresh non-author)

- Head: `cfeba22f1fa0a52781c14d59b7139c120e035506` ("S10 round 7"), base `bc1d7ef9`.
- Export: `/tmp/s10-cr-export` (`git archive` of the head), `PYTHONDONTWRITEBYTECODE=1`.
  No repo was modified; no git write command was run.
- Authority read: directive issue 316, `153-continuation-synthesis.md`,
  `docs/contracts/epoch_continuation.md`, `docs/contracts/powermetrics_fiducial.md`,
  `docs/phase_2/derivation_night_runbook.md`. Prior reports were not consulted for
  verdicts; every finding below is independently derived from the export.

## Verdict

**Not clean — two should-fix, four nits. No blocker.** The mechanism itself is
sound: the four trigger semantics match the contract, the no-continuation
evaluation record is byte-identical in shape to base, the six acceptance
artifacts are untouched, the registry is empty, and 51/51 core mutation cuts
are killed. Both should-fix items are *documentation truth* defects outside the
Python: one sentence in a contract that names itself "the one home" is now
false, and the runbook that Ed's ruling names as the operating authority for the
equivalence night contains no PASS route and an instruction that literally
forbids the ruling's step 2.

## Execution evidence (all run this session in the export)

| Command | Result |
| --- | --- |
| `python3 -m unittest tests.test_epoch_continuation tests.test_calibration_bracketing` | `Ran 153 tests ... OK (skipped=1)`, rc 0 |
| `python3 -m unittest tests.test_mint_policy_resolver_guard tests.test_docs_freshness tests.test_custody_mode_inventory tests.test_d078_reason_registry` | `Ran 53 tests ... OK`, rc 0 |
| `git diff bc1d7ef9 cfeba22f -- configs/calibration/ \| wc -l` | `0` — the six acceptance artifacts are byte-identical to base |
| `python3 tests/fixtures/epoch_continuation/mutation_cuts.py` | `cuts=51 killed=51 survivors=0 source_sha256_restored=true`, rc 0 |
| `python3 tests/fixtures/epoch_continuation/writer_mutation_cuts.py` | `cuts=23 killed=23 survivors=0 source_sha256_restored=true`, rc 0 |
| `EPOCH_CONTINUATION_REGISTRY` | empty — `joulewise/calibration_bracketing.py:178` (`= {}`) |
| Operative literals in the contract's worked example | `preflight_level_screen_s = "0.032898493715362"`, `bracket_screen_s = "0.009724"` read live from `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`; both match `docs/contracts/epoch_continuation.md:270-271` exactly |

The one skip is not in `tests.test_epoch_continuation` (a `-v` run of that module
alone reports no skipped test); it is pre-existing in `tests.test_calibration_bracketing`.

## Findings

### SHOULD-FIX 1 — a contract that calls itself "the one home" carries a sentence round 6 made false

`docs/contracts/powermetrics_fiducial.md:191-193`, exact text:

> Until the CLI supplies its ledger snapshot here, a file-authenticated
> continuation can pass capture preflight but fail the session cross-check at
> claim time.

Lines 178-181 of the *same paragraph* already say the opposite:

> The writer CLI loads its custody-verified snapshot before identity preflight,
> passes it to both preflight helpers, and records `"ledger_snapshot"`.

The code agrees with 178-181, not with 191-193:
`scripts/validate_powermetrics_fiducial.py:1950-1954` loads
`preflight_snapshot = load_calibration_ledger_snapshot(args.ledger, args.head_pin,
require_committed_pin=True, verify_custody=True, mode="issuing")` unconditionally
in `main()`, and passes it at `:2009-2010` (ordinary) and `:1957-1959`
(derivation-only). The conditional sentence was true at round 5 and became
residue at round 6. The same file declares at `:161` "This contract is the one
home for the artifact's preflight object", so a reader who trusts the one home
is told a live gap exists that does not.

Fix: delete the sentence, or re-scope it to the identity-only helper callers
(G2-a vectors, the desk-inputs writer, the import-time screen constant), which
genuinely do still skip the session cross-check under `registry_pins_only`.

### SHOULD-FIX 2 — the runbook has no PASS-route action, and its blindness fence contradicts the ruling's step 2

The lens asked whether "runbook §2.5's PASS action" agrees with the contract and
the code. **There is no §2.5.** `docs/phase_2/derivation_night_runbook.md`
sections run `2.0 Rebuild the night's coordinates` (1341), `2.1 What to read`
(1388), `2.2 The one mid-campaign query` (1405), `2.3 What NOT to read — the
blindness fence` (1430), `2.4 The writer-status dispatch` (1450), then `3. Nights
2 and 3` (1524). The string "equivalence" does not appear anywhere in the file.
The branch updated the runbook's glossary (`:110-115`) and two refusal rows
(`:668`, `:1798`) and stopped there.

The gap is not cosmetic. Ed's ruling item 1 names this runbook as the operating
authority for night one ("run by the merged chain exactly as built ... runbook
docs/phase_2/derivation_night_runbook.md"), and item 2 requires that after the
night closes "the magistrate READS the night's retained values and applies this
rule". Runbook `:1432-1436` says, in the same campaign's §2:

> Do not open, print, extract, summarise, or ask any agent about ANY captured
> value: no `b_fiducial_s`, no minimum, maximum, range, mean or SD, no screen,
> no statistic, and no comparison against one. ... Leave it until §4.

Followed literally on the equivalence night, that forbids exactly the step Ed
ruled. The fence's own justification at `:1438-1441` is the three-night
derivation's pre-registration logic ("so that nothing can be chosen after seeing
values"), which the ruling explicitly displaces for this night ("blindness for
this campaign means 'every rule fixed before data', which this issue satisfies,
not 'no one may look'"). Nothing in the merged text tells the operator which
regime applies to the night in front of them.

Fix (smallest that resolves it): a §2.5 "If this is the equivalence night" that
(a) states the fence of §2.3 governs the three-night derivation campaign only,
(b) names the read that is permitted — retained `b_fiducial_s` values, `m`,
max, min, range — (c) states the fixed rule verbatim with the two operatives,
and (d) routes PASS to `scripts/issue_epoch_continuation.py prepare-candidate`
and FAIL to `§3 Nights 2 and 3` with night one counting as registration night
one. The code side for this already exists and needs no change.

### NIT 1 — the tool's glossary fails the first-use test on two terms

`python3 scripts/issue_epoch_continuation.py --help` (identical prologue on both
subcommands). It does build the load-bearing terms — "identity epoch" is glossed
at first use as "the machine's six-field identity", "judged epoch" as "an
identity that acceptance may evaluate", the level and bracket screens by what
they cap. Two terms fail:

- **"equivalence night."** Exact text: "Acknowledged rows are exactly the
  equivalence night's finalized attempts". The term never appears before this
  sentence and is never built. A reader cannot determine *which* night's
  attempts are acknowledged — the whole acknowledgment rule is therefore not
  replicable from the help text.
- **"the range-expansion trigger."** Exact text: "these bypass only the
  range-expansion trigger." Named as if already known; nothing in the help says
  what range expansion is or why bypassing it is the narrow exemption. The very
  next sentence relies on the contrast ("Systematic failures remain triggers").

One clause each fixes both, e.g. "the equivalence night — the single twelve-slot
derivation session this continuation is derived from" and "range expansion, the
trigger that fires when a later value falls outside the acceptance's corpus
minimum or maximum". Note the contrast: the runbook does this correctly, with a
dedicated §8 first-use table.

### NIT 2 — code stricter than the contract on resolved rows' anchor detail

`joulewise/calibration_epoch_continuation.py:243`:
`_require(not slot["anchor_v3_resolved"] or slot["anchor_v3_detail"] is None,
"slots.anchor_v3_detail")` — a **resolved** row must carry a null detail.
`docs/contracts/epoch_continuation.md:61-63` states only the converse ("Every
`valid` row with `anchor_v3_resolved: false` must name a non-empty
`anchor_v3_detail`"). The code's extra requirement is right (it stops a resolved
row carrying an exclusion story), but it is unstated, so an issuer writing to the
contract could produce a file the loader refuses. One sentence.

### NIT 3 — mutation runners are not reachable from the test suite

`grep -n "mutation_cuts" tests/test_epoch_continuation.py` returns nothing; both
runners are standalone `__main__` scripts, and
`tests/fixtures/epoch_continuation/README.md:36` further requires the writer
runner to "Run this command alone, without another test run or writer using the
checkout" (it edits source bytes in place and restores them in `finally`). CI
therefore never re-executes the 51 + 23 cuts, so a later refactor can silently
un-kill them without any red. This matches the repo's existing fixture pattern,
so it is not a regression introduced here — recorded so the next session does
not assume the cuts are self-maintaining.

### NIT 4 — an epoch-mismatch refusal can now fire with an empty `stale_fields`

`scripts/validate_powermetrics_fiducial.py:410-418`. Base computed `stale_fields`
first and refused only if non-empty; the head refuses whenever
`identity_epoch not in judged_epochs` and then reports `stale_fields` computed
against the **original** epoch. If a caller ever passes an epoch mapping with an
extra key, the mapping is unequal to every judged epoch while every shared field
matches, producing `acceptance_artifact_epoch_mismatch` with `stale_fields: []`
— the state the base comment (deleted at `:1963-1970`) singled out as
meaningful. Unreachable from `main()`, where `planned_epoch` is built with
exactly the six fields at `:1937-1944`, so it is a latent shape issue only.

## Lens 4 — the 25F84 path with an empty registry

**Byte-identical in shape to base; no new keys.** Cited from the export:

- `joulewise/calibration_bracketing.py:2034` — `identity_epoch = artifact["identity_epoch"]`,
  the same object `acceptance_judged_epochs` copies, so the two cannot diverge.
- `joulewise/calibration_epoch_continuation.py:363-364` — with an empty registry
  the return is `(MappingProxyType(dict(acceptance_artifact["identity_epoch"])),)`
  and nothing else; `refusal_details` and `continuation_details` stay empty
  because `load_epoch_continuations` iterates `registry.items()` (`:326`).
- `calibration_bracketing.py:2062-2065` — `matched_epoch` is either that single
  proxy (when the observed identity matches) or the `identity_epoch` fallback;
  `dict()` of either equals `dict(identity_epoch)`. Line `:2093`
  (`"expected_identity_epoch": dict(matched_epoch)`) therefore emits exactly the
  base value in both the fresh and the stale case.
- `:2092` — `matched_continuation` is `None`, so `basis` is the base string
  `"exact_identity_epoch"`.
- `:2126-2127` — `if matched_continuation is not None:` is false, so no
  `continuation_id` / `continuation_file_sha256` / `session_id` / `m` / `verdict`
  / `ledger_cross_check` key is added to `freshness`.
- `:2128-2129` — `if continuation_refusals:` is false, so
  `acceptance.continuation_refusals` is **absent**, not `[]`.
- `:2131-2132` — the `reason` key is likewise added only when refusals exist.

Receipt hashes over the evaluation record are therefore unchanged on the
no-continuation path, which is what `epoch_continuation.md:196-200` promises.

One asymmetry worth knowing (deliberate, disclosed, not a defect): the *capture
writer's* record is unconditional. `scripts/validate_powermetrics_fiducial.py:2494-2495`
and `:2522-2523` add a top-level `acceptance_preflight` to every ordinary
capture's `instrument_evidence.json` and `manifest.json`, carrying
`"continuation_refusals": []` when nothing refused. That is pinned by
`powermetrics_fiducial.md:170-175` and by the round-5 top-level key-set tests, so
future ordinary captures deliberately change shape relative to base while the
bracket evaluation record deliberately does not. The two contracts state opposite
conventions for the same field name; a half-sentence in `epoch_continuation.md`
saying why (hash stability for the claim-time record, self-describing provenance
for the capture) would close the reading.

## Lens 1 — cross-unit consistency table

| Claim | Doc | Code | Consistent |
| --- | --- | --- | --- |
| A continuation is a **separate** issued artifact; no new acceptance generation, no operative/corpus/pin change | `epoch_continuation.md:13-24`; synthesis 153 "Decision: Opus's shape" | `configs/calibration/` diff = 0 lines; `EPOCH_CONTINUATION_REGISTRY` separate from `ISSUED_ACCEPTANCE_REGISTRY` (`calibration_bracketing.py:175-178`) | **y** |
| Judged epochs = original + authenticated continuations | `epoch_continuation.md:15-16` | `calibration_epoch_continuation.py:348-364` | **y** |
| **Freshness**: observed vector must equal one judged epoch; a continuation match reports `basis: "epoch_continuation"` + id, file hash, session, `m`, verdict, cross-check | `epoch_continuation.md:239-244` | `calibration_bracketing.py:2062-2073, 2092-2093, 2126-2127`; `Continuation.evaluation_record()` at `calibration_epoch_continuation.py:165-173` supplies exactly those six fields | **y** |
| **Doubling counted per judged epoch, never summed**, acknowledged valid rows included | `epoch_continuation.md:245-248, 263` | `calibration_bracketing.py:2350-2359` — a per-epoch list comprehension over `judged_epochs` with `any(count >= threshold)`; `acknowledged_attempt_ids` is not consulted here | **y** |
| **Range expansion exempts exactly the acknowledged attempt IDs**, over any judged epoch | `epoch_continuation.md:249-252` | `calibration_bracketing.py:2361-2377` — `observation.attempt_id not in acknowledged_attempt_ids and dict(observation.identity_epoch) in judged_epochs` | **y** |
| **Systematic failure keeps every row**, including acknowledged ones | `epoch_continuation.md:253-256, 258-263` | `calibration_bracketing.py:2382-2389` — judged-epoch filter only, **no** acknowledgment term; the asymmetry is pinned by mutation cut C21 (adding the exemption is killed) | **y** |
| Envelope holds over **every disclosed valid bound, resolved or not**; `m` counts the resolved; invalid rows excluded | `epoch_continuation.md:59-60, 67-72` | `calibration_epoch_continuation.py:258-266` appends to `lexemes_all_valid` for every `valid` row and to `lexemes` only when resolved; `envelope_holds_over_all_valid` at `:85-104`; nine cuts (C34-C45) around it all killed | **y** |
| Envelope check has **no minimum count**; empty set vacuous | `epoch_continuation.md:72` | `calibration_epoch_continuation.py:102-104` (`not values or max-min <= bracket`); cuts C41/C42 pin it | **y** |
| `m < 6` → inconclusive; PASS = all `<= L` and range `<= S` | `epoch_continuation.md:99-102`; issue 316 item 2 | `equivalence_statistics` `:126-128`, `MINIMUM_RETAINED = 6` `:29` | **y** |
| Reference operatives are r6's ratified operatives, not fitted | issue 316 item 2; `epoch_continuation.md:94-97, 270-271` | `continuation_rule` `:67-82` reads the registry and cross-checks the artifact's `ratified_operatives`; live artifact values match the doc literals exactly | **y** |
| Tool **refuses** a systematic-failure night (`night_contains_systematic_failure`, exit 3, writes nothing) | `epoch_continuation.md:46-49` | `issue_epoch_continuation.derive_record`; cut C22 (`classification_disposition == "systematic-invalid"` → `False`) killed by `test_prepare_refuses_systematic_failure_night_without_writing` | **y** |
| Tool **refuses** an envelope violation unconditionally (exit 3), also below `m=6` | `epoch_continuation.md:83-89` | cuts C31/C46 killed; `unresolved_valid_row_exceeds_envelope` raised at `calibration_epoch_continuation.py:265-266` for the loader | **y** |
| Loader refuses candidate markers, wrong byte pins, non-PASS verdicts, wrong schema/derivation hash, duplicate keys | `epoch_continuation.md:155-162` | `calibration_epoch_continuation.py:187-206`, `_json_object:138-151` | **y** |
| Only open-session state reasons tolerated in the snapshot; the continuation's own session must be terminal | `epoch_continuation.md:164-172` | `SNAPSHOT_STATE_REFUSALS:33-40`; `:274-280`; cuts C47-C50 killed | **y** |
| Derivation-only refuses a planned epoch equal to **any** judged epoch | `epoch_continuation.md:226-231`; `powermetrics_fiducial.md:124-127`; runbook `:1798` | `validate_powermetrics_fiducial.py:1966-1972` (`if planned_epoch in basis["judged_epochs"]`) | **y** |
| Desk-inputs writer treats a continued epoch as an ordinary night | `epoch_continuation.md:332`; runbook `:110-115`, `:668` | `write_derivation_night_inputs.py:181-187` refusal text names the judged-epoch condition | **y** |
| Diagnostic `calibration_epoch_continuation_invalid` registered; outer refusal stays `calibration_acceptance_bound_stale` | `d078_reason_registry_amendment.md:24-34`; `epoch_continuation.md:196-204` | `calibration_bracketing.py:2128-2133`; `CONTINUATION_INVALID` at `calibration_epoch_continuation.py:28` | **y** |
| Registry starts empty; issuance is a later governed transaction | `epoch_continuation.md:21-24, 336-337` | `calibration_bracketing.py:175-178` | **y** |
| CLI supplies a custody-verified snapshot to both preflight helpers | `powermetrics_fiducial.md:178-181`; `epoch_continuation.md:214-221` | `validate_powermetrics_fiducial.py:1950-1954, 1957-1959, 2009-2010` | **y** |
| "Until the CLI supplies its ledger snapshot here …" | `powermetrics_fiducial.md:191-193` | contradicted by the three code sites above and by `:178-181` | **n — SHOULD-FIX 1** |
| PASS route has an operator action in the runbook | issue 316 items 2-3 | no §2.5; §2.3 fence at `:1430-1441` forbids the required read | **n — SHOULD-FIX 2** |
| Every term of art built or glossed at first use in the tool's help | Ed's writing standard | "equivalence night", "range-expansion trigger" unbuilt | **n — NIT 1** |

## Lens 2 — merge-ability

- `git diff bc1d7ef9 cfeba22f --stat`: 22 files, +3676 / -57. Three production
  modules touched (`calibration_bracketing.py` +59/-... , the new
  `calibration_epoch_continuation.py`, `validate_powermetrics_fiducial.py`), one
  new script, four docs, the rest tests and fixtures.
- **Debug residue: none.** Every added `print` is CLI or mutation-runner output
  (`issue_epoch_continuation.py:1249,1260,1281,1316` in diff coordinates; the two
  runners' progress lines). No `TODO`/`FIXME`/`breakpoint`/`pdb`, no absolute
  `/Users/` or `/tmp/` path in any added line.
- **Volatile literals: none found.** The only dates are `2026-09-10` in the D-078
  amendment heading and in a test's `--d102-addendum-date` argument — both
  correct as fixed historical facts, neither consulted at runtime.
- **Hand-typed operative digits: verified, not trusted.** The contract's worked
  example (`epoch_continuation.md:270-274`) and the S9 fixtures
  (`s9-*.json`) carry `0.032898493715362` and `0.009724`; I read both live from
  `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` this session
  and they agree character for character. The raw corpus statistics quoted
  alongside (`0.03289849371536248`, `0.00972358928879385`) match issue 316's own
  text. `tests/fixtures/epoch_continuation/README.md:15-16` states the tests
  derive both comparators from the acceptance registry rather than the fixture
  literal, which is the right dependency direction.
- **Overbuild / duplication: none.** The lens's specific worry —
  duplicated fixture builders between `tests/fixtures/epoch_bootstrap` and
  `tests/fixtures/epoch_continuation` — does not hold:
  `tests/fixtures/epoch_continuation/build.py:12-14` imports `SESSION_ID`,
  `Slot` and `build_derivation_ledger` from `tests.fixtures.epoch_bootstrap.build`
  and adds only the continuation-specific prepare-then-unmark step.
  `epoch_bootstrap/` contains just `__init__.py` and `build.py`; nothing was
  forked.
- The four guard tests named in the brief pass (53 tests, rc 0), which covers the
  docs-freshness and D-078 reason-registry pins on the new prose.

## Lens 3 — three cut→test claims, assessed by reading

1. **`(bracket, evaluate_calibration_bracket, systematic-failure filter →
   + "attempt_id not in acknowledged_attempt_ids", test_systematic_row_in_the_equivalence_night_still_fires)`**
   — **valid.** The test (`tests/test_epoch_continuation.py:545-565`) relabels one
   *acknowledged* finalized row `systematic-invalid` and asserts at `:562` that
   its `attempt_id` is in `loaded[0].acknowledged_attempt_ids`, then at `:565`
   that `observed_triggers == ["new_systematic_failure_challenges_preflight_screen"]`.
   Under the cut that exact row is filtered out, `observed_triggers` is empty,
   and both `:564` and `:565` fail. The chain is real: the trigger appends at
   `calibration_bracketing.py:2387-2389`, which drives the stale update at
   `:2394-2406` and hence the `calibration_acceptance_bound_stale` reason the
   test also pins. This is the cut that guards the one asymmetry the whole
   acknowledgment design rests on.
2. **`(continuation, authenticate_epoch_continuation, bool(slot["anchor_v3_detail"]) → True,
   test_unresolved_valid_row_requires_nonempty_anchor_detail)`** — **valid.**
   The require at `calibration_epoch_continuation.py:244-245` is
   `disposition != "valid" or anchor_v3_resolved or bool(anchor_v3_detail)`;
   with the third disjunct forced `True` a valid-unresolved row with a null or
   empty detail no longer refuses. The test (`:658-672`) sets
   `slots[-1]["anchor_v3_detail"]` to `None` and to `""` in subTests and asserts
   `loaded == ()` and `details[0]["detail"] == "slots.anchor_v3_detail_required"`;
   under the cut the file authenticates, `loaded` has length 1, and both
   assertions fail in both subTests.
3. **`(issuer, derive_record, 'disposition == "valid" and resolved' → "resolved",
   test_only_valid_resolved_values_are_retained_but_all_finalized_acknowledged)`**
   — **valid.** The test (`:647-656`) builds 6 valid-resolved `0.025`, 3
   `ordinary-invalid` `0.9` (resolved, since no `unresolved_detail` is passed),
   and 3 valid-unresolved `0.026`, then asserts `payload["evidence"]["m"] == 6`
   at `:651`. Under the cut the three invalid-but-resolved `0.9` rows are
   retained, so `m` becomes 9 and `:651` fails immediately; independently `0.9`
   is far above the level screen, so the verdict would also flip to `fail` and
   preparation would exit non-zero before the payload existed. The test's second
   assertion (`len(acknowledged_attempt_ids) == 12`) correctly stays satisfied
   either way, which is the right separation: acknowledgment is over *finalized*
   rows, retention over *valid and resolved* ones.

I also executed the full continuation runner rather than relying on the seat's
count: `cuts=51 killed=51 survivors=0 source_sha256_restored=true`, rc 0.

## Closing note on the two mutation runners

Both runners were executed here rather than taken from the seat's report:
51/51 and 23/23 cuts killed, zero survivors, source SHA-256s restored in both.
One honest caveat: I started them concurrently, which
`tests/fixtures/epoch_continuation/README.md:36` asks against because the writer
runner edits source bytes in place. Both nonetheless reported
`source_sha256_restored=true` and exited 0, and the continuation runner
re-verifies its three target files' hashes after every single cut. If the lead
wants an uncontested count on the merge record, re-run them serially in a fresh
export; I would not hold the branch for it.
