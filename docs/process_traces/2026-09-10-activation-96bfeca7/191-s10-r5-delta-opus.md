# 191 — S10 ROUND 5 read-only DELTA RE-AUDIT (refuter 174's fix round)

Target: `106244f9` on `feat/2026-09-10-epoch-continuation`; parent = round 4
`42638546`. Read via `git -C <s10 worktree> diff 42638546 106244f9`; all
execution in the read-only export `/tmp/s10-r5-export`
(`git archive 106244f9 | tar -x`), `PYTHONDONTWRITEBYTECODE=1`, no `timeout`.
**No repo was modified; no git write command was run; the S10 worktree,
`/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and every other
worktree were untouched.** Per the brief, S2 (CLI snapshot routing) and N1
(absolute paths in hashed bytes) are deferred to round 6 and are NOT
re-reported here.

**Verdict: NOT CLEAN — 0 blockers, 2 should-fix, 4 nits. Every item the brief
asked for (B1, S1, S3, N2) is genuinely closed, and the drift guard is real:
editing the contract alone goes red.** Both should-fix items are the SAME
SIGNATURE as 174's B1 — prose asserting a shape the code no longer has — in
places the fix round did not sweep; one of them is an operator-facing refusal
string INSIDE round 5's WRITE_SCOPE.

---

## Question-by-question

### (1) B1 — CLOSED, and the guard is mechanical

- **`screen_basis` key list equals what the code returns.**
  `docs/contracts/powermetrics_fiducial.md:154-157` documents exactly
  `["acceptance_id", "artifact_sha256", "preflight_level_screen_s", "epoch",
  "judged_epochs", "judged_epochs_basis", "continuation_refusals"]` — seven
  keys. `_derivation_only_screen_basis`
  (`scripts/validate_powermetrics_fiducial.py:520-553`) returns
  `{**preflight_record, "acceptance_id", "artifact_sha256",
  "preflight_level_screen_s", "epoch"}` where `preflight_record` is the
  four-key record built at `:411-419`; union = the same seven. Equality is
  asserted, not eyeballed (below).
- **Derivation-only precondition.** `powermetrics_fiducial.md:123-127` now
  reads "It REQUIRES the live identity epoch to differ from EVERY epoch the
  artifact judges (its own and any authenticated continuation), and refuses
  when any matches". Matches `main`'s
  `if planned_epoch in basis["judged_epochs"]` (`:1955-1961`).
- **`acceptance_preflight` documented ONCE.** Full key list +
  semantics at `powermetrics_fiducial.md:160-187`, with the explicit sentence
  "This contract is the one home for the artifact's preflight object."
  `epoch_continuation.md:193-200` no longer restates the fields; it points at
  `powermetrics_fiducial.md#derivation-only-capture-for-a-new-identity-epoch`
  — and that anchor resolves (heading at `powermetrics_fiducial.md:93`).
  `epoch_continuation.md:202-207` keeps only prose ("record the same fields in
  `screen_basis`"), no key list. The census gained the missing fourth caller
  row (`write_derivation_night_inputs._stale_identity_fields`,
  `epoch_continuation.md:306`), closing 174's S3 primary.
- **The drift test reads the contract, not a copy.**
  `tests/test_validate_powermetrics_fiducial.py:24-35` `documented_keys(name)`
  does `(writer.REPO_ROOT / "docs/contracts/powermetrics_fiducial.md").read_text()`
  (`REPO_ROOT` = the live checkout, `validate_powermetrics_fiducial.py:51`),
  regex-extracts the fenced JSON after "`<name>` has exactly these keys:",
  rejects duplicates, returns a set.
  `test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis`
  (`:51-58`) asserts set EQUALITY against a live-emitted preflight record and a
  live `_derivation_only_screen_basis()`; the artifact-side tests assert the
  same documented sets against the real hashed payloads
  (`…derivation_only.py:624` for `screen_basis`, `:792-793` for
  `acceptance_preflight` in both `instrument_evidence.json` and
  `manifest.json`, plus `:794` evidence == manifest).
- **Would editing the contract alone fail it? YES — executed.** Cuts W18/W19
  mutate only `docs/contracts/powermetrics_fiducial.md` (drop keys from each
  documented list); both `KILLED rc=1` by
  `test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis`
  (run below). Code-side additions are caught symmetrically by W16/W17
  (inject a stray `"unexpected"` key into evidence/manifest → killed by the
  ordinary key-set test).

### (2) S1 — CLOSED; EQUALITY, and named to say so

`tests/test_validate_powermetrics_fiducial_derivation_only.py:775-794`, inside
`test_ordinary_artifact_top_level_key_sets_require_deliberate_schema_changes`
(a real CLI capture, not a stub), does `self.assertEqual(set(evidence), {…27
names…})` and `self.assertEqual(set(manifest), {"schema_version",
"validation_id", "protocol_id", "pulse_count", "artifacts",
"acceptance_preflight"})`. Whole-set equality, so an ADDED key fails —
demonstrated by cuts W16/W17 (both killed). The name states the obligation.
Negative side kept: `assertNotIn("derivation_only", evidence)` /
`assertNotIn("screen_basis", evidence)` at `:772-773`.

### (3) S3 — CLOSED

`tests/test_write_derivation_night_inputs.py:98-109`
`test_continued_epoch_is_an_ordinary_night_and_writes_no_derivation_inputs`
uses the REAL continuation fixture — `registered_continuation(root)`
(`tests/fixtures/epoch_continuation/build.py:60-65`) builds an issued
continuation from synthetic primary evidence and `patch.dict`s
`bracket.EPOCH_CONTINUATION_REGISTRY` with `clear=True` — under
`mocked_machine(os_build=TARGET_EPOCH["os_build"])`, and asserts rc 2,
`"ORDINARY night, not a derivation night"` in stderr, empty stdout, and an
empty out-dir. The docstring sentence exists
(`scripts/write_derivation_night_inputs.py:36`, "A continued epoch
authenticated by the issued registry is an ordinary night") and the test
asserts it (`:110`). Mutation W20 (make the desk writer pass an unjudged
`os_build`) is killed by that test — correct counterfactual, real production
call site.

### (4) N2 — CLOSED, with a named refusal inside the envelope

`scripts/validate_powermetrics_fiducial.py:400-407`: `acceptance_id =
artifact.get("acceptance_id")`, and the guard now refuses
`_AcceptancePreflightError("acceptance_artifact_derivation_invalid")` when the
value is absent, non-`str`, or empty (`True` is not a `str`, so booleans
refuse too). `main` catches `_AcceptancePreflightError` on both branches
(`:1946-1952` derivation-only, `:1998-2004` ordinary) and emits
`RefusalCode.FROZEN_PROTOCOL_INVALID` with `context.reason =
acceptance_artifact_derivation_invalid`. Proven end-to-end through `main` for
`None`/`""`/`7`/`True` by
`test_invalid_acceptance_id_returns_named_cli_refusal_without_traceback`
(`tests/test_validate_powermetrics_fiducial.py:99-125`), which fails
explicitly if the CLI leaks any exception and asserts no capture directory is
created. Cuts W14/W15/W21 (restore the bare subscript, or neuter each conjunct
of the guard) are all killed by it.

### (5) Regression — GREEN

```
$ cd /tmp/s10-r5-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_validate_powermetrics_fiducial_derivation_only \
    tests.test_validate_powermetrics_fiducial \
    tests.test_write_derivation_night_inputs \
    tests.test_epoch_continuation tests.test_docs_freshness 2>&1 | tail -3
Ran 127 tests in 110.628s

OK
rc=0
```

Writer mutation runner — it DOES run in the export (it mutates files under the
export root only, and restores them). All eleven NEW cuts:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/writer_mutation_cuts.py \
    --cuts W11 W12 W13 W14 W15 W16 W17 W18 W19 W20 W21
W18 KILLED rc=1 …test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis
W19 KILLED rc=1 …test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis
W20 KILLED rc=1 …test_continued_epoch_is_an_ordinary_night_and_writes_no_derivation_inputs
W21 KILLED rc=1 …test_invalid_acceptance_id_returns_named_cli_refusal_without_traceback
cuts=11 killed=11 survivors=0 source_sha256_restored=true
rc=0
```

Sources verified restored after the run (sha256 of the three mutated paths
unchanged). The `--cuts` selection the seat added is sound: `originals` and
`hashes` are built from the SELECTED subset only, so unselected paths are
never opened, and the summary line counts `selected`, not `CUTS`.

### (6) SAME-SIGNATURE STATEMENT — 174's B1 class is NOT fully swept

Grepped `screen_basis`, `acceptance_preflight`, `stale_fields`,
`judged_epochs`, `derivation-only`/`derivation_only` across `docs/contracts/`
and `docs/phase_2/` (and, for completeness, all of `docs/`). Result:

| Doc | Site | State |
|---|---|---|
| `docs/contracts/powermetrics_fiducial.md` | `:121-187` | **CURRENT** (fixed this round; now the one home, machine-pinned) |
| `docs/contracts/epoch_continuation.md` | `:193-207`, census `:300-308` | **CURRENT** (restates nothing; points at the one home; census complete) |
| `docs/contracts/calibration_ledger.md` | `:31`, `:51` | **CURRENT** — defines "derivation-only capture" only; no keys, no epoch-equality clause |
| `docs/contracts/calibration_ledger_append.md` | `:339-341` | **CURRENT** — reason-code registry rows, no epoch semantics in the prose |
| `docs/contracts/d078_reason_registry_amendment.md` | continuation row | **CURRENT** (pinned by `test_d078_reason_registry`, cut W10) |
| `docs/phase_2/derivation_night_runbook.md` | `:1796`, `:666`, `:112` | **STALE ×3** — see D2 |
| `docs/phase_2/derivation_night_runbook.md` | `:1876-1894` (the "what is pinned where" table) | CURRENT — points at source, states no key list |
| `docs/decision_log.md` | `:6540-6544` | **STALE** (historical ruling text) — see D3 |

No doc outside `powermetrics_fiducial.md` enumerates the artifact key sets, so
the "two homes" half of B1 is genuinely closed. What is NOT closed is the
**epoch-equality clause** half: four operator-facing restatements of "the
acceptance's epoch" survive, and one of them is executable code.

---

## SHOULD-FIX

### D1 — the desk writer's own refusal STRING is false on exactly the path round 5 just tested, and the new test cannot catch it (in WRITE_SCOPE)

`scripts/write_derivation_night_inputs.py:181-187` raises:

```
"no identity field differs from the acceptance's epoch at "
f"{acceptance_path}: this machine still matches the acceptance in "
"force, so this is an ORDINARY night, not a derivation night: …"
```

On the continued-epoch path the FIRST clause is false: fields DO differ from
the acceptance's `identity_epoch` (that is why a continuation was issued); what
matches is a judged continuation. The operator reads "no identity field
differs", concludes the OS reverted or the wrong acceptance was read, and goes
back to §0.3 looking for something that is not there. The second clause
("still matches the acceptance in force") is the true one.

The new test asserts only the trailing substring
`"ORDINARY night, not a derivation night"`
(`tests/test_write_derivation_night_inputs.py:106`), so the false clause is
unpinned in both directions. This is 174's B1(b) exactly — prose asserting the
pre-continuation shape — one layer down, and it sits on a night-window desk
step.

Fix (one string + one assertion): "no identity field differs from any epoch
the acceptance judges at `<path>` (its own or an authenticated continuation):
this machine still matches the acceptance in force…", and assert the new
clause. Both paths are inside round 5's WRITE_SCOPE.

### D2 — three operator-facing runbook restatements of the pre-continuation rule (needs a round-6 NEEDS_SCOPE)

`docs/phase_2/derivation_night_runbook.md`:

- `:1796` — writer refusal table:
  "`calibration_derivation_only_epoch_unchanged` | `--derivation-only` was used
  while the live identity epoch **still matches the active acceptance's**.
  Derivation-only exists only when no acceptance binds the current epoch. |
  **Stop.** Either the OS reverted or the wrong acceptance was read."
  With a continuation registered the refusal fires when the epoch matches a
  CONTINUED epoch, so the stated cause is false and the two named causes omit
  the real third one ("a continuation was issued for this build; this is an
  ordinary night").
- `:666` — the desk-inputs writer refusal table row, cause column literally
  "Nothing is stale." — false on the continued-epoch path (D1's case, as the
  operator sees it).
- `:112` — glossary "Stale field": "A derivation night exists precisely because
  at least one field is stale; if none is, this is an ordinary night". The
  module docstring got the continuation sentence this round; its runbook mirror
  did not.

Not in round 5's WRITE_SCOPE; file it for round 6 with the scope grant, in the
same commit as D1 so the code string and the table agree.

---

## NITS

- **D3 — `docs/decision_log.md:6540-6544`** records the ruling text
  "requires the live six-field identity epoch to DIFFER from the artifact's"
  and "`screen_basis` naming the prior acceptance's ID, file SHA-256,
  `preflight_level_screen_s`, and epoch" (four fields). Both are superseded.
  Per the project's own convention this is a HISTORICAL ruling record and the
  correct remedy is a dated addendum pointing at the continuation ruling, not
  an edit — flagging so the choice is made deliberately rather than by
  omission.
- **D4 — the derivation-only artifact's TOP-LEVEL key set is still unpinned.**
  S1's equality pin covers the ordinary evidence and manifest only; the
  derivation-only tests pin `set(payload["screen_basis"])` but never
  `set(payload)`. A stray new top-level key on a derivation capture — the
  claim-bearing corpus for the next acceptance — would land silently. One
  `assertEqual(set(evidence), {…})` in
  `test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance`
  closes it.
- **D5 — a rename buried existing coverage.**
  `test_ordinary_mode_still_fills_a_bracket_kind_slot_unchanged` became
  `test_ordinary_artifact_top_level_key_sets_require_deliberate_schema_changes`,
  but its docstring still opens "The guard is kind-scoped, not a blanket
  ordinary-path refusal" and report 76 records a mutation cut killed by the OLD
  name. The test now has two jobs and announces one; a future trim of the
  key-set assertions could take the kind-scoped guard's only coverage with it.
  Split, or name it for both.
- **D6 — one prose count is outside the machine pin.**
  `powermetrics_fiducial.md:142` says "the **seven-key** provenance object".
  The drift test pins the JSON list, not the English numeral: a future key
  addition forces the list to change (test goes red until fixed) but leaves
  "seven-key" silently wrong. Either drop the numeral or derive it.
- (174's S3 secondary — the "reported an epoch mismatch without naming a field"
  branch at `write_derivation_night_inputs.py:175-179`, reachable in principle
  if a caller ever passes a superset epoch dict — remains without an assertion.
  The brief did not ask for it; noting it is still open.)

---

## Round-6 hand-off note (not a finding)

`judged_epochs_basis: "ledger_snapshot"` is now documented and tested but is
emitted by NO production path: the only caller that could own a snapshot is the
writer CLI, whose routing is deferred (`main:1996-1997` and `:1947` still call
the helpers with no `ledger_snapshot`), and the other three callers —
`generate_g2a_probe_inputs.py:660`, `write_derivation_night_inputs.py:163`, and
the import-time constant `validate_powermetrics_fiducial.py:577` — genuinely
have none. The contract states this limitation explicitly
(`powermetrics_fiducial.md:173-187`) and `epoch_continuation.md:193-197`
agrees, so round 5 is honest. **When round 6 wires the CLI snapshot, those two
paragraphs and the census row `epoch_continuation.md:302` must change in the
SAME commit or B1 recurs**; the two tests asserting `registry_pins_only` for the
CLI path (`…derivation_only.py:533` and `:645`) will go red and are the right
tripwire.

---

## Honesty check on the seat's report (186)

The envelope declares `status: blocked` / `completion: partial` with
`head_start == head_end == 42638546`, i.e. the seat reports having made NO
commit, while the audited round-5 commit is `106244f9`. The eight paths in
`pathspec` match `git diff --stat 42638546 106244f9` exactly (8 files,
+257/−27), no unowned change. Its V4 claim ("cuts=19 killed=19") excludes W09
and W10 as out of allowlist, disclosed in F2; I independently re-ran the eleven
NEW cuts and confirm 11/11 killed with sources restored. Its residual-risk
paragraph names the two deferred items accurately. Nothing in 186 overstates
what landed.
