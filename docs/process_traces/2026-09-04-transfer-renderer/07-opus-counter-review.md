# Opus counter-review — TRANSFER-RESULT-RENDERER-01 (gate ledger row 6, contract lens)

Seat: Opus 5, read-only in `/Users/edr/code/JouleWise-wt-transfer-renderer`,
branch `feat/2026-09-04-transfer-result-renderer` @ `0d5289b4`. Authority read:
R3 in `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md`;
traces 01..06 in this directory. `CLAUDE.local.md`, `RUN_STATE.md`, and
`TASK_QUEUE.md` were not read as authority. No commit, no push, one file written
(this one).

## VERDICT

**NOT LANDABLE** — two blockers, both demonstrated at the bench in this session,
both with cures smaller than a delegated fix contract (bench-sized: a signature
change and a four-line fail-closed guard).

Neither blocker repeats a prior signature: CR-01..CR-04 and the two delta rounds
addressed *internal* authentication (census, maximum selection, estimator
identity, reason semantics) and are cured. B1 and B2 below are new classes —
the *input channel* and the *output format*. So a further round is not a
same-signature third round under the standing escalation trigger; whether to run
it or consult is the magistrate's call, not this seat's.

## Executed evidence

All commands run from `/Users/edr/code/JouleWise-wt-transfer-renderer` this
session with `/Users/edr/code/JouleWise/.venv/bin/python`.

```
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python -m pytest tests/test_results_fill_transfer.py -q
1 passed, 42 subtests passed in 0.09s

$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 \
    python -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
Ran 13 tests ... OK

$ shasum -a 256 joulewise/powermetrics_fiducial.py
386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92  joulewise/powermetrics_fiducial.py

$ grep -rn "results_fill_transfer|render_transfer_fiducial_result" (py/md/json, excluding
  this trace dir and tests/test_results_fill_transfer.py)
joulewise/results_fill_transfer.py:122   # __all__ entry
joulewise/results_fill_transfer.py:638   # the definition
→ no production call site exists.
```

---

## BLOCKERS

### B1 — blocker — The renderer authenticates nothing: it takes caller bytes plus the caller's own digest of those same bytes

**Location.** `joulewise/results_fill_transfer.py:638-656`; the claim is at
`:643-647` ("The caller must supply the independently authenticated SHA-256 of
the exact issued bytes"), the check at `:654`.

**Text.** The only integrity gate is
`hashlib.sha256(issued_result_bytes).hexdigest() != expected_result_sha256`.
That compares the caller's bytes against the caller's digest of the caller's
bytes. It is a self-consistency check, not authentication: it can only fail if
the caller miscomputes its own hash. Nothing binds the bytes to a governed
artifact — no path is read, no registry-pinned digest is consulted, no
authentication session is entered. The module never imports
`joulewise/authentication_io.py`, which is the repo's governed-read convention
and supplies exactly the missing primitives (`read_authentication_input_nofollow`
at `:575`, `sha256_authentication_input` at `:605`, `direct_read_violations` at
`:623`). The word "independently" in the docstring is unpaid: nothing in the
signature or the body can enforce it, and no caller is obliged to honour it.

Every remaining custody field is shape-checked only — `file_sha256`,
`plan_sha256`, `pre_data_receipt_sha256` (`:205-212`), `bundle_sha256[].sha256`
(`:261-263`), `pulse_derived_timing_bound_source.artifact_sha256` (`:235-240`)
need merely be 64 lowercase hex characters. The one field with real external
force is `estimator_source_sha256`, pinned to a constant (`:45-47`, `:218-221`).
So the entire projection except the estimator identity is self-asserted, and the
one channel that could have anchored it — the byte digest — is supplied by the
same caller that supplies the bytes.

This is the class named in the counter-review brief as having broken two sibling
lanes. The bytes-plus-caller-digest shape is the dict shape wearing a hash.

**Counterfactual (executed, this session).** Starting from
`tests/fixtures/results_fill_transfer/supported.json`, I rewrote every edge
record to invented magnitudes, invented a pulse-derived bound of `0.999999`,
replaced `file_sha256` / `plan_sha256` / `pre_data_receipt_sha256` /
`pulse_derived_timing_bound_source.artifact_sha256` with `"a"*64` … `"d"*64`,
recomputed `result_id` with the module's own `transfer_result_id`, serialised,
hashed the result, and called the renderer with both:

```
validator errors: []
distinct rendered values: 1 | sites: 9
Diagnostic only: the largest composed inserted-gap edge-residual bound was
0.000002 s, no greater than the session pulse-derived timing bound of 0.999999 s;
this supports applying that timing bound to the studied inference boundary, but
it does not mint a floor or license a claim.
```

A wholly fabricated projection, with fabricated custody digests, renders the
`supported` sentence byte-identically into all nine paper sites. Nothing in the
module can tell it from an issued one.

**Live-reachability (honest calibration).** There is no production call site
(grep above), and TR-01 remains `STOP_FILL` / `VALUE_UNISSUED`. No forged
sentence can reach the paper today. The defect is in the API that the future
supplier will be wired to, which is precisely when nobody will re-audit the
signature. Fix it now, while it costs a signature.

**Cure shape.** Take the artifact by path and obtain the expected digest from a
governed source, not from the caller: read through
`joulewise.authentication_io` and compare against a digest resolved from the
registry row / authentication session. If — as is true today — no acceptance
digest can exist while the capture is fenced out and the value unissued, then
say so in the signature by refusing: the function should have no way to be
handed a digest by its caller. Keep the fixture tests by pointing them at
fixture paths under a test authentication root.

---

### B2 — blocker — The ruled six-decimal format prints a strict inequality as an equality at the real fixture magnitudes

**Location.** `joulewise/results_fill_transfer.py:606-607` (`_format_seconds`),
used at `:613-614` and `:622-623`. The relational check is correctly done on
unrounded Decimals at `:563` and `:570` — the defect is that the *printed*
sentence is not required to preserve the relation the check established.

**Text.** `not_supported` renders "was `<R>` s, **exceeding** … bound of `<B>` s".
The comparison is decided on unrounded values; the rendering truncates both to
six decimals (1 µs). The fixtures' real magnitudes are ~30 ms
(`pulse_derived_timing_bound_s = 0.030067931757111657`), so any near-boundary
result — exactly the case the diagnostic exists to adjudicate — differs by less
than 0.5 µs and prints identically on both sides.

**Counterfactual (executed, this session).** From
`tests/fixtures/results_fill_transfer/not_supported.json`, retuned the winning
edge record to a composed bound of `0.0300682` (interval `-0.0280682`/`0.02`,
anchor `0.002`, replays exactly) against a pulse bound of `0.0300679`,
recomputed `result_id`:

```
errors: []
Diagnostic only: the largest composed inserted-gap edge-residual bound was
0.030068 s, exceeding the session pulse-derived timing bound of 0.030068 s; this
does not support applying that timing bound to the studied inference boundary and
does not mint a floor or license a claim.
```

"was 0.030068 s, exceeding … 0.030068 s" goes into the Abstract, §7 and §10, nine
times. Every number in it is true; the sentence still reads as an error to any
reader, and to the advisor. A second instance exists at sub-microsecond
magnitudes (R = 2e-07 vs B = 1e-08 both print `0.000000`), but the 30 ms
near-tie above is the physically plausible one.

**Cure shape.** Fail closed inside the ruled format rather than change it: after
selecting the branch, if the outcome asserts a strict relation
(`supported` with R < B, or `not_supported`) and `_format_seconds(R) ==
_format_seconds(B)`, return `_stop_sites()`. Four lines, no ruling amendment
needed — refusing to render is always available to a `STOP_FILL` supplier. If
instead the magistrate prefers the pair to render, that is a format amendment to
R3 and belongs to the magistrate, not the seat.

---

## SHOULD-FIX

### S1 — should-fix — The acceptance test compares against its own copy of the sentences, not the registered bytes

**Location.** `tests/test_results_fill_transfer.py:36-56` (`EXPECTED_SENTENCES`
hardcoded), and a fourth literal at `:466`. The file contains no reference to
`docs/paper/results-fill-registry.md`.

**Text.** R4/B1 established the principle for this same registry: "the registry
must carry the exact professor-facing rendering strings … The test compares
against the registered bytes." The TR-01 row now does carry them — I verified by
extracting the three backticked literals from the row and diffing them against
the three rendered sentences; they match exactly today. But the test asserts
against a duplicate, and neither of the two registry tests
(`tests.test_paper_first_use_ledger`, `tests.test_paper_terms_lint`) inspects the
TR-01 row at all (grep for `TR-01` / `Diagnostic only` in both files: one
unrelated comment hit).

**Counterfactual.** Change one word in the registry row — "no greater than" to
"not greater than". The registry is the registered contract; the renderer now
publishes bytes that contradict it; `tests/test_results_fill_transfer.py` and
both registry tests stay green. The drift is undetectable by the suite.

**Cure shape.** Parse the three literals out of the TR-01 row (the same regex
used above works: `` `(Diagnostic only:[^`]+)` ``) and compare the rendered
sentences to the registered bytes with the placeholders substituted.

### S2 — should-fix — `ESTIMATOR_SOURCE_SHA256` is an unpinned constant

**Location.** `joulewise/results_fill_transfer.py:45-47`; the registry prose
block asserts the same digest as fact.

**Text.** I verified at the bench that the constant is the SHA-256 of
`joulewise/powermetrics_fiducial.py` in this tree (`386e8254…bab92`, `shasum`
output above), that the same digest is recorded in `origin/main` at
`configs/calibration/calibration_acceptance_d079_v2_n17_r5.json:40` as the pin
for that file, and that `ESTIMATOR_REVISION` matches `RESIDUAL_REGION_METHOD` at
`joulewise/powermetrics_fiducial.py:169`. Good — the source binding *is*
verifiable without the fenced producer. But no test asserts it. Grep of
`tests/test_results_fill_transfer.py` for `powermetrics_fiducial` returns nothing;
`ESTIMATOR_SOURCE_SHA256` appears only as an imported constant echoed into a
fixture comparison (`:17`, `:133`), which is circular.

**Counterfactual.** Add a comment to `joulewise/powermetrics_fiducial.py`. The
constant is now stale, the registry sentence "The existing estimator is fixed to
revision … and source SHA-256 386e…bab92" is now false, the validator now accepts
projections asserting a digest that identifies no file in the tree, and the whole
suite stays green.

**Cure shape.** One assertion:
`hashlib.sha256(Path("joulewise/powermetrics_fiducial.py").read_bytes()).hexdigest()
== ESTIMATOR_SOURCE_SHA256`.

### S3 — should-fix (authority, not code) — The registry diff adds unruled contract prose beyond the amended row

**Location.** `docs/paper/results-fill-registry.md`, the two paragraphs added
after the placement table, headed "**TR-01 v1 closed evidence and refusal
contract (R3 fix round 1).**"

**Text.** The diff against `origin/main` is a single hunk and touches nothing
else in the registry — the TR-01 row is rewritten as R3 ruled (token, schema,
public names, `b_fiducial_s` binding, the three sentences, nine sites, six
decimals, `diagnostic=true` / `claim_bearing=false`), and the OB-01 and OR-01
rows are untouched. Lens (2) is otherwise clean. But the added prose is *new
contract text*, not the ruled row amendment: it pins the estimator identity, the
ordered `reason_codes` enum, the census thresholds, the ordering rule and the
tie-break, and it now reads with registry authority. R3 authorises the row, the
token and the sentences; it does not authorise the seat to write standing
registry contract text of its own.

**Counterfactual.** A later seat reads the block as ruled authority and builds
the capture producer to its reason-code semantics; if the magistrate would have
ruled differently at the capture-acceptance gate, the producer is built to an
unratified spec and the divergence surfaces only after collection.

**Cure shape.** Either the magistrate ratifies the block explicitly (one line in
a dated addendum to the rulings), or it moves to this mission's trace directory
and the registry row cites it as seat-proposed.

### S4 — should-fix — Nobody is named to discharge the custody digests the fence leaves unchecked

**Location.** `joulewise/results_fill_transfer.py:205-266`; the registry row and
prose block.

**Text.** Under the R3 fence (capture producer on `d67ee56c` not adopted) it is
correct that `file_sha256`, `plan_sha256`, `pre_data_receipt_sha256`, the ten
`bundle_sha256[].sha256` values and the `b_fiducial_s` `artifact_sha256` are
shape-checked only. What is missing is the record of that debt: neither the
module docstring nor the registry row states that these digests are unverified
by construction and must be checked against the reviewed capture at the
acceptance gate. With B1 unfixed as well, the full authentication burden sits
outside this module and no artifact names its holder.

**Cure shape.** One sentence in the module docstring and one clause in the TR-01
row naming the capture-acceptance gate as the discharger.

---

## NITS

- **N1** — `:630` joins `reason_codes` with `";"` and no space; the registry row
  says only "semicolon-joined". Pin the exact separator in the row.
- **N2** — `:433` compares witness to winner with `dict(witness) != dict(winner_record)`.
  Python holds `1 == 1.0`, so an int-typed witness field matches a float-typed
  record while producing different canonical bytes and a different `result_id`
  preimage. Compare `canonical_json_bytes` instead.

---

## Verified clean (lens by lens, evidence-backed)

**(1) Numbers in sentences.** No rendered magnitude is derived, defaulted or
re-derived. `<R>` and `<B>` are formatted directly from the issued fields
`largest_composed_edge_residual_bound_s` and `pulse_derived_timing_bound_s`
(`:613-614`, `:622-623`); the branch relation is decided first, on unrounded
values, via `Decimal(str(v))` (`:563`, `:570`); nothing reads back the formatted
string. The `not_evaluated` sentence carries no magnitude at all. Subject to B2,
which is about the *printing*, not the sourcing.

**(3) Content-addressing.** `result_id` = `"tfr-"` + SHA-256 over canonical JSON
(`sort_keys`, `(",",":")`, `ensure_ascii=False`, `allow_nan=False`) of the whole
projection with `result_id` emptied (`:128-145`), recomputed and compared at
`:578-585`. The preimage therefore covers every field including all custody
digests, the census, every edge record and the witness — one changed byte of
content changes the id. The `b_fiducial_s` source binding is enforced literally
(`:231-234`) alongside its `artifact_sha256`. The estimator half of the source
binding is independently verifiable without the fenced producer (S2 above); the
capture half is not, by design of the fence (S4).

**(4) `not_evaluated` semantics.** A partial or absent capture cannot reach a
rendered magnitude. Executed: injecting a non-null
`largest_composed_edge_residual_bound_s` into the truthful 9-run/18-edge
`not_evaluated.json` yields `incomplete edge evidence requires null global
maximum and witness` and nine `STOP_FILL`s (`:409-411`). The truthful partial
renders the reason-only sentence. `source_capture_refused` requires a null
parent, zero counts, an empty `edge_records` and null comparison evidence
(`:497-501`, `:545-550`). `not_evaluated` with a complete comparison is refused
(`:575-576`); `supported` / `not_supported` with any reason code is refused
(`:559-560`, `:566-567`). Reason presence is an exact iff against the field
state (`:516-519`, `:539-544`), so a reason cannot contradict its own census.

**(5) Nine-site byte identity.** `TRANSFER_FIDUCIAL_RESULT_SITES` (`:28-38`) has
exactly nine entries spanning abstract/§7/§10 × outcome_a/outcome_b/refusal.
Both the render path (`:668`) and the refusal path (`:603`) use
`dict.fromkeys`, so all nine values are the *same string object* — byte identity
is structural, not asserted. Executed for all three fixtures: `len(set(values))
== 1`, `len(values) == 9` in each case. The rendered bytes equal the three
literals in the registered TR-01 row exactly (extracted and diffed this session).

**(6) Input channel — partially clean.** The dict channel is genuinely closed: a
`dict` returns nine `STOP_FILL`s, and so does a `str`, a wrong digest, and bytes
that do not match the supplied digest (all four executed). JSON parsing is
hardened — duplicate keys rejected (`:589-595`), `NaN`/`Infinity` rejected
(`:598-599`), UTF-8 decode errors caught. What remains open is that the byte
channel is still a caller channel: see B1.

**Ordering, census and maximum selection** (the cured CR-01 surface) re-checked
independently: bundle order with falling-before-rising is enforced by a strictly
increasing position index (`:375-396`), which also rejects duplicates and
foreign bundles; each composed bound must replay `max(|lower|,|upper|) + anchor`
exactly in Decimal (`:355-358`); the global maximum uses strict `>` so the
tie-break is first-in-order (`:427-434`) as the registry states.

## Test results

| Command | Result |
|---|---|
| `pytest tests/test_results_fill_transfer.py -q` | 1 passed, 42 subtests passed |
| `unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint` | 13 tests, OK |

Both with `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`. The whole suite was not
run, per the brief.
