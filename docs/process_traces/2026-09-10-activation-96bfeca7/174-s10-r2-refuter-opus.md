# 174 — S10 ROUND 2 read-only refuter (contract + execution lenses)

Target: `e187723701df35553fb0dbb1a694743613f95916` ("S10 round 2", Astra xhigh,
brief 168) on `feat/2026-09-10-epoch-continuation`; parent = round 1
`c75da300f72e1ccc28473d856c9abce8e61f9882`.
Read via `git show $R2:<path>` / `git diff c75da300 $R2`; all execution in the
read-only export `/tmp/s10-r2-export` (`git archive $R2 | tar -x`),
`PYTHONDONTWRITEBYTECODE=1`. **No repo was modified; no git write command was
run; the S10 worktree, `/Users/edr/code/JouleWise` and `/Users/edr/night-custody`
were not touched.** Round-1 refuter findings B1/S1/S3 are excluded by the brief.

**Verdict: NOT CLEAN — 1 blocker (contract lens, doc-vs-code), 3 should-fix,
4 nits. The round-2 CODE is, as far as I can break it, correct: every
semantic claim in items (2)(3)(4)(5) checks out, and the three mutation
claims I was asked to assess are real kills.** The blocker is that the
governing artifact contract was left saying the opposite of what the code now
writes, and that doc was outside WRITE_SCOPE with no NEEDS_SCOPE filed.

---

## BLOCKER — B1: `docs/contracts/powermetrics_fiducial.md` is now false about the bytes of both capture artifacts, and it was out of WRITE_SCOPE with no NEEDS_SCOPE raised

`docs/contracts/powermetrics_fiducial.md` is self-declared as the "Contract for
`runs/instrument_validation/<validation_id>/` artifacts" (line 3). Round 2
changes those artifacts and leaves that contract unamended. Three separate
clauses are now wrong:

**(a) `screen_basis` key count.** `docs/contracts/powermetrics_fiducial.md:141`:

> `screen_basis`, an object with **exactly four keys** — `acceptance_id` …
> `artifact_sha256` … `preflight_level_screen_s` … and `epoch` …

`scripts/validate_powermetrics_fiducial.py:547-553` now returns **seven**:

```python
    return level_screen_s, {
        **preflight_record,          # judged_epochs, judged_epochs_basis, continuation_refusals
        "acceptance_id": acceptance_id,
        "artifact_sha256": sha256_path(path),
        "preflight_level_screen_s": str(level_screen_s),
        "epoch": dict(epoch),
    }
```

Concrete failing input: any `--derivation-only` capture (e.g. the existing
`tests/test_validate_powermetrics_fiducial_derivation_only.py:578`
`test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance`
fixture) writes `instrument_evidence.json` whose `screen_basis` has 7 keys. A
consumer or auditor written from the contract — `assert len(basis) == 4`, or a
schema with `additionalProperties: false` — refuses every derivation capture
taken from this commit forward. The contract explicitly frames these as fields
inside HASHED bytes ("Provenance is recorded in hashed bytes, not in prose",
line 132), which is exactly the class of statement that must not drift.
The seat's own test was updated to expect the new keys
(`…derivation_only.py:642-643`), so the code and the tests agree and only the
governing contract dissents — the "ruled-not-installed" shape inverted.

**(b) derivation-only refusal rule.** `docs/contracts/powermetrics_fiducial.md:122-125`:

> It REQUIRES the live identity epoch to differ from **the artifact's epoch**,
> and refuses when they match

`scripts/validate_powermetrics_fiducial.py:1945` now refuses when the planned
epoch equals **any judged epoch**. Concrete input: machine at 25G83, a valid
continuation registered, `--derivation-only` → rc 2
`calibration_derivation_only_epoch_unchanged`. A reader implementing the
contract predicts the capture proceeds (25G83 ≠ 25F84, the artifact's epoch).
That is the opposite answer, on the gate whose whole purpose is to stop a
screen bypass.

**(c) undocumented new top-level key.** The contract enumerates the ordinary
artifact shape (lines 133-149 for the derivation-only additions; 289-296 for
the directory/schema listing; 297+ for the evidence bindings) and never
mentions `acceptance_preflight`, which round 2 adds unconditionally to BOTH
ordinary artifacts (`…fiducial.py:2470, 2498`). `manifest.json` keeps
`schema_version: joulewise.instrument_validation_manifest.v1` while gaining a
new always-present top-level key.

`docs/contracts/epoch_continuation.md:156-166` documents the new shape — so the
repository now has **two homes** describing the same hashed artifact and one of
them is wrong. `docs/contracts/powermetrics_fiducial.md` was not in brief 168's
WRITE_SCOPE; the correct move was `NEEDS_SCOPE`, and the seat's report
(reports/169) neither amends nor mentions it.

Fix: amend `powermetrics_fiducial.md` (a) to the true key list, (b) to "differs
from every epoch the acceptance judges", (c) to name `acceptance_preflight` —
under an explicit scope grant. Cheap; the code does not need to change.

---

## SHOULD-FIX

### S1 — the ordinary path is **no longer byte-identical** to the parent, and nothing in the suite pinned it in either direction

Answer to the brief's question (1): **yes, the bytes change**, with an EMPTY
continuation registry, on an ordinary 25F84 capture. Verified by executing the
export's own writer against the live r6 acceptance
(`joulewise.calibration_bracketing.EPOCH_CONTINUATION_REGISTRY` is `{}`, 0
entries):

```
$ python3 -c "from scripts import validate_powermetrics_fiducial as w; rec={}; \
  w._derive_preflight_systematic_screen_s(None, preflight_record=rec); print(rec)"
```

emits, into `instrument_evidence.json` AND `manifest.json`, exactly:

```json
  "acceptance_preflight": {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r6",
    "continuation_refusals": [],
    "judged_epochs": [
      { "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
        "hardware_model": "Mac15,9", "os_build": "25F84",
        "power_policy": "ac_high_power",
        "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        "sampling_interval_ms": 100 } ],
    "judged_epochs_basis": "registry_pins_only"
  }
```

**(1a) Does any consumer break? No — I could not break one.** Checked:
- `scripts/issue_calibration_acceptance_generation._read_member_evidence:884-904`
  authenticates a member against `observation.artifact_sha256` **recorded at
  finalization**, not against a golden — so a new-format capture is
  self-consistent and a pre-change capture is untouched.
- `joulewise/controller.py:399`, `joulewise/reduce.py:1237`,
  `joulewise/calibration_bracketing.py:1520` compare `schema_version` for
  equality and then read named keys. No strict unknown-key rejection exists on
  either payload (`grep` for allowlists / `set(evidence…)` in the ledger,
  arm_readiness and bracketing found none).
- `rederive_artifact` (`…fiducial.py:1224-1300`) reads only named keys and
  returns before the ordinary write path; `--rederive-from` is unaffected.
  (It also does not carry `acceptance_preflight` forward into the v2 re-emission
  — harmless, v1/v2 40-pulse legacy only.)
- The `instrument_evidence_sha256` values pinned in
  `configs/calibration/calibration_acceptance_d079_v2*.json` and in
  `tests/fixtures/d117_v2_production/**` are digests of PAST captures held as
  static files; the writer never regenerates them. No fixture pins a
  writer-regenerated evidence digest.
- Mixed-shape corpora are fine: nothing asserts member schema homogeneity.

**(1b) The S1 "ordinary path byte-identical" property is broken — and it was
never a suite test, so nothing went red.** Report 90 established it as a one-off
harness witness (fixed absolute paths, `JW_FAKE_TIME_ORIGIN`, `--attempt-id`),
not as a `test_*`. `grep -rn "byte_identical|ordinary_path"` over `tests/`
returns no writer-artifact test; the two ordinary-path tests that exist
(`…derivation_only.py:723`, `:847`) assert rc/disposition and
`_classify_capture` behaviour and pin no artifact key. So round 2 did **not**
silently alter what those tests pin — it altered something **no test pins at
all**, which is the worse half of the answer.

Ask: add one regression that pins the ordinary artifacts' top-level key set
(positive AND negative: `acceptance_preflight` present, `derivation_only` /
`screen_basis` absent), so the next schema change to a claim-bearing capture
cannot land silently. This is the same defect class as B1 seen from the test
side.

### S2 — `judged_epochs_basis: "registry_pins_only"` is justified in the contract by a premise that is false for exactly the claim-bearing captures

`docs/contracts/epoch_continuation.md:150`: "The capture writer has **no ledger
snapshot** at its identity preflight."

The writer imports `load_calibration_ledger_snapshot`
(`scripts/validate_powermetrics_fiducial.py:88`), `--ledger` / `--head-pin` have
production defaults (`:1731-1732`), and the writer already builds a snapshot at
`:1333` inside the slot-reservation authentication. In bracket mode — the mode
that produces acceptance-corpus members — the ledger is always present. So the
degradation is a **design choice**, not a constraint, and it is applied to the
captures that matter most.

Concrete consequence: a continuation whose cited derivation session is absent
from / non-terminal in the real ledger still authenticates at capture time
(`authenticate_epoch_continuation:224-235` skips the whole `ledger_snapshot is
not None` block), so the writer will take a capture on that epoch and finalize
it `valid` (proven end-to-end by
`…derivation_only.py:491` `test_ordinary_continued_epoch_capture_requires_registered_continuation`,
which asserts `disposition == "valid"`). Claim-time
`evaluate_calibration_bracket` then re-authenticates WITH the snapshot, refuses,
and the whole night's captures are unusable. Fail-closed, but the loss lands
after the hardware window is spent — the expensive place.

Fix: either pass the snapshot when `args.ledger` resolves (and label the record
`verified_terminal_derivation_session`), or state in the contract that this is a
deliberate ordering choice with the wasted-window consequence named. As written
the doc asserts an impossibility that is not one.

### S3 — the "production identity-comparison census" is still incomplete: `scripts/write_derivation_night_inputs.py` is a fourth production caller, and round 2 flipped its behaviour

`docs/contracts/epoch_continuation.md:248-258` presents an exhaustive census.
It omits `scripts/write_derivation_night_inputs.py::_stale_identity_fields`
(`:563-604` in the export), which calls
`_derive_preflight_systematic_screen_s(planned_epoch, acceptance_path=…)`, keys
off `exc.reason == "acceptance_artifact_epoch_mismatch"`, and reads
`exc.context["stale_fields"]`.

Concrete behaviour flip introduced by round 2: machine at 25G83 with a valid
registered continuation → the preflight now **returns normally** instead of
raising, so `_stale_identity_fields` falls through to its terminal
`NightInputsRefusal` ("this machine still matches the acceptance in force, so
this is an ORDINARY night, not a derivation night"). Before round 2 the same
machine got `stale_fields == ["os_build"]` and the desk-inputs writer produced
derivation-night inputs. That is the correct new semantics in my reading — but
it is an operator-visible change on the derivation-night path, and it is in
neither the census, the seat's report, nor any test.

Secondary: the empty-`stale_fields` branch at
`write_derivation_night_inputs.py:~577` ("reported an epoch mismatch without
naming a field") became reachable in principle, because
`…fiducial.py:413-422` now raises whenever `identity_epoch not in judged_epochs`
even if the field-wise comparison yields `[]`. It is unreachable in practice
(every caller passes exactly the six `IDENTITY_EPOCH_FIELDS`, and a six-field
dict equal on all six IS in `judged_epochs`); it becomes reachable the moment a
caller passes a superset dict. Worth one assertion, not a redesign.

---

## NITS

- **N1 — absolute filesystem paths can enter hashed, claim-bearing bytes.**
  `joulewise/calibration_epoch_continuation.py:273-275` records
  `{"reason": …, "continuation_id": …, "detail": str(exc)}` for a broad
  exception set including `OSError`. For a registered-but-missing continuation
  file, `str(exc)` is `[Errno 2] No such file or directory:
  '/Users/edr/code/JouleWise/tests/fixtures/epoch_continuation/issued.json'`.
  Round 2 is what routes that list into `instrument_evidence.json` and
  `manifest.json` (`…fiducial.py:409, 2470, 2498`). Two costs: the capture's
  bytes become dependent on the checkout's absolute path (destroying precisely
  the path-independence report 90 went to trouble to establish), and the
  operator's filesystem layout is published in claim evidence. Bound `detail` to
  the `ContinuationRefusal` field name (the `ValueError` branch already is one).
- **N2 — one bare subscript defeats a fail-closed guard.**
  `…fiducial.py:406` uses `artifact["acceptance_id"]`. A `KeyError` there is not
  an `_AcceptancePreflightError`, so `main`'s handler (`:1987-1993`) misses it
  and the writer exits with a traceback instead of a refusal envelope; it also
  makes the graceful `acceptance_artifact_derivation_invalid` check at
  `:539-545` dead for that case. Unreachable today (the acceptance is pinned by
  `acceptance_id` in `ISSUED_ACCEPTANCE_REGISTRY`, so a bound artifact always
  has one) — hence nit, not blocker. `artifact.get("acceptance_id")` + the
  existing named refusal costs one line.
- **N3 — the diagnostic is registered by a bespoke assertion, not by the
  mechanism.** `tests/test_d078_reason_registry.py:33-40` regex-matches one row.
  `CONTINUATION_INVALID` is not added to the enumerated vocabulary union in
  `test_code_vocabularies_are_present_in_d078_amendment` (`:60-80`), so a
  *future* continuation reason code is not covered by the D-078 mechanism. A
  `CONTINUATION_REASON_CODES` frozenset joined to that union would close it.
- **N4 — recording asymmetry.** `joulewise/calibration_bracketing.py:2128-2129`
  adds `acceptance.continuation_refusals` only when non-empty; the writer always
  records `"continuation_refusals": []`. Harmless, but two readers of the same
  concept now need two cases.

---

## Answers to the numbered questions

**(1) Byte invariants.** Bytes CHANGE (exact added object above). (a) No
consumer breaks — evidence/manifest digests are recorded at finalization, not
pinned as goldens; the three `schema_version` gates compare equality only; no
unknown-key rejection exists; no fixture pins a regenerated evidence sha.
(b) The S1 ordinary-path byte-identity property is **broken**, but it lived only
in report 90's ad-hoc witness; no suite test pinned the ordinary artifact shape,
so nothing was silently *altered* — the invariant was simply unguarded. See S1.

**(2) Ordinary-path semantics — correct.** `judged_epochs` is
`tuple[MappingProxyType, ...]` (`calibration_epoch_continuation.py:294`) and
`identity_epoch` is a plain `dict`; `dict in tuple_of_mappingproxy` works
because `mappingproxy.__eq__` delegates to the underlying dict — verified in the
export:
`{'a':1,'b':2} in (MappingProxyType({'a':1,'b':2}),) is True`, and a superset
dict is correctly `False`. With `ledger_snapshot=None`, reading
`acceptance_judged_epochs:279` → `load_epoch_continuations:251` →
`authenticate_epoch_continuation:140`, the following are STILL enforced:
registry byte pin (`:156-157` `sha256(raw) == registered["file_sha256"]`),
candidate marker absence (`:151` `"candidate_not_issued" not in value`),
`verdict == "pass"` (`:168`), and all three acceptance references
(`:162-167`: `acceptance_id`, `acceptance_file_sha256`,
`acceptance_derivation_sha256`) — plus schema, `decision_ids`, the
self-derivation hash, the rule cross-check and the reproduced equivalence
arithmetic. **Only** the `if ledger_snapshot is not None` block (`:225-235`) is
skipped. The degradation IS stated in the contract
(`epoch_continuation.md:143-157`) — accurately as to WHAT is skipped; its
*justification* is the false premise in S2.

**(3) Derivation-only guard — correct, and the new-epoch path is unchanged.**
`basis["judged_epochs"]` is a `list[dict]`
(`…fiducial.py:407` `[dict(epoch) for epoch in judged_epochs]`, flowed through
`**preflight_record` at `:548`), and `planned_epoch` is a 6-key dict, so
`in` is plain dict equality. A continued epoch refuses with
`RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED` — the pre-existing code, no new
mint (`:1946-1950`), proven by
`tests/test_validate_powermetrics_fiducial.py:72`
(`rc == 2`, `code == DERIVATION_ONLY_EPOCH_UNCHANGED`, and no capture directory
created). A genuinely new epoch still passes exactly as before: with the
registry empty, `judged_epochs == (original,)` and the old
`if not stale_fields` and the new `in` agree on every 6-key input — they can
only diverge when `planned_epoch` is a strict superset of the artifact's
epoch, which no caller produces (all six `IDENTITY_EPOCH_FIELDS`, and
`authenticate_epoch_continuation:172` pins continued epochs to exactly that
set with per-field type equality). The parent's `stale_fields` variable had no
downstream use, so deleting it loses nothing recorded.

**(4) G2-a proof — it exercises the real delegation, not just the writer.**
`tests/test_validate_powermetrics_fiducial.py:86`
`test_g2a_live_vectors_use_real_continuation_preflight` calls
`probe._derive_live_vectors(...)` — the real
`scripts/generate_g2a_probe_inputs.py:638-672` — with only `_sysctl_identity`,
`writer.sha256_path` and `mlx.core` stubbed; the acceptance loader, the writer
preflight and continuation authentication are all real. Its second half is the
part that makes it a proof of delegation rather than of the writer: with
`EPOCH_CONTINUATION_REGISTRY` cleared it asserts
`G2AProbeError … acceptance_artifact_epoch_mismatch`, i.e. the generator's
result depends on the writer preflight's verdict. Genuine.

**(5) Reason registry — correctly formatted and enforced.**
`docs/contracts/d078_reason_registry_amendment.md:24-34` appends a section with
its own `| Reason code | Semantics |` table; the row
`` | `calibration_epoch_continuation_invalid` | … | `` matches the test's
`(?m)^\| `<code>` \| .+ \|$` and the file is concatenated into the governing
text by `_d078_registry_text()`. The amendment's prose ("records a rejected
continuation in `acceptance.continuation_refusals`") matches the code —
`joulewise/calibration_bracketing.py:2129` writes
`result["acceptance"]["continuation_refusals"]`. Test result below. See N3 for
the mechanism gap.

**(6) Mutation claims W01 / W06 / W09 — all three are real kills** (assessed by
reading the cut and the named test; the runner mutates the working tree in
place, so I did not execute it here):
- **W01** `identity_epoch not in judged_epochs` → `identity_epoch != expected_epoch`
  (`tests/fixtures/epoch_continuation/writer_mutation_cuts.py:22-23`). Killing
  test is the end-to-end CLI capture at `…derivation_only.py:491`, whose second
  phase registers a continuation for 25G83 and asserts `returncode == 0`. Under
  the cut, 25G83 ≠ 25F84 raises `acceptance_artifact_epoch_mismatch` → rc 2 →
  the `assertEqual(completed.returncode, 0)` fails. Kills.
- **W06** `if planned_epoch in basis["judged_epochs"]` → `if planned_epoch ==
  basis["epoch"]` (`:32-33`), killed by
  `test_derivation_only_refuses_continued_epoch_before_capture`. Under the cut
  the continued epoch no longer matches the original, so the branch falls
  through to `DERIVATION_ONLY_SESSION_KIND_REQUIRED`; the test's
  `assertEqual(refusal["code"], DERIVATION_ONLY_EPOCH_UNCHANGED.value)` fails.
  Kills, and it is defect-shaped (it is the exact pre-round-2 semantics).
- **W09** deletes the `_derive_preflight_systematic_screen_s(planned_epoch)`
  call from `generate_g2a_probe_inputs.py:660` (`:38-39`), killed by the G2-a
  test. The first half of that test would survive the cut; the
  registry-cleared half (`assertRaisesRegex(G2AProbeError,
  "acceptance_artifact_epoch_mismatch")`) is what kills it. Correct
  counterfactual + named production call site, per the mutation-cure rule.
  Coverage nit: no cut collapses the `identity_epoch is not None and …`
  conjunction to each operand, and none cuts `judged_epochs` to
  `judged_epochs[1:]` (would prove the ORIGINAL epoch is still judged) — that
  case is covered by an existing test (`…derivation_only.py:723`) rather than by
  a cut.

**(7) Test batch — GREEN, rc 0, `test_calibration_exits` included (it does NOT
need the real machine; it runs the fixture sampler and passed here).**

```
$ cd /tmp/s10-r2-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_validate_powermetrics_fiducial_derivation_only \
    tests.test_validate_powermetrics_fiducial \
    tests.test_epoch_continuation \
    tests.test_d078_reason_registry \
    tests.test_calibration_exits
...
----------------------------------------------------------------------
Ran 119 tests in 574.759s

OK
rc=0
```

Zero `FAIL:`/`ERROR:` lines. Python 3.14.7 (Homebrew), export at
`/tmp/s10-r2-export`, nothing written outside `/tmp`.

---

## Scope / honesty of the seat's own report (169)

- The envelope's `pathspec` and "6 modified files, 3 additions, all
  allowlisted" match `git diff --stat c75da300 $R2` exactly (9 paths:
  2 docs, 1 script, 3 test files, 3 new fixture files). No unowned change.
- `EPOCH_CONTINUATION_REGISTRY` is `{}` at this commit (verified by import) and
  the issued acceptance registry and acceptance bytes are unchanged — "no
  continuation issued" is true, so nothing here grants a judged epoch in
  production yet.
- V13/V14 (the `os_build=None` identity-probe failure reproducing on the
  baseline checkout at `7107657d`) is a correct environmental diagnosis in
  shape; I did not re-run it (it needs the other worktree, which is outside my
  read-only fence). It remains a lead-side live-verification item.
- What the report does NOT declare, and should have: that the ORDINARY capture's
  hashed artifacts changed shape (it says "Both capture artifacts retain
  `acceptance_preflight`" in the Change section but never flags the byte
  delta on the empty-registry ordinary path), and that
  `docs/contracts/powermetrics_fiducial.md` — outside WRITE_SCOPE — is
  contradicted by the change (B1). The correct move was `NEEDS_SCOPE`.
