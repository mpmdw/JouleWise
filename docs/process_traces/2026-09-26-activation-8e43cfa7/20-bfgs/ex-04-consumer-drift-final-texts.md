# Cold addendum ruling CONSUMER-DRIFT-ESC-01-ADD (Fable 5.1, cold judge)

Ruled 2026-09-26, started about 01:05 PDT, in worktree `JouleWise-wt-ed17a643-cg-cd-add` at `9ba960c7`. BFG-D examined at `3e984ecc` from a `git archive` export in `/tmp/cgadd_tree` (no worktree registered; `git worktree list` showed zero `/tmp` entries throughout). Line numbers are at `3e984ecc` unless stated.

**Verdicts.** Z1: P3 AFFIRM (executed), P4 AFFIRM (executed; `check` rejects the flag at argparse), P5 AFFIRM (executed), R16 AFFIRM with the `parse` NIT adopted; R11 (`target_epoch`) AFFIRM; R18 AFFIRM; R19: **option (a), bounded**: A-7, the ledger refusal and the confounded declaration are mirrored through the shared collector and one policy; the "admissible" line's text is unchanged; its promise is **enumerated** in the docstring and in runbook `:3217` and §4.1 in the same PR, so every remaining unmirrored issuer refusal is named rather than implied. The refuter's full shared admission prefix (`assess_registration`) is REJECTED as the cure for this round, with the science reason in §2.5. Z2: final texts v1.1 in §3, complete; they supersede the ruling's §3 and §4 where they differ. Ed summary in §4.

## 0. Contamination disclosure and verification

- **Context received without asking.** The harness loaded the project `CLAUDE.md`, the global `~/.claude/CLAUDE.md`, and the one-line index `MEMORY.md` of the operating loop's memory into my system prompt before I read the charge. I did not open any memory file, `RUN_STATE.md`, `TASK_QUEUE.md`, council log, run report, or any `docs/process_traces` file outside this packet other than the BFG-D directory on the branch. The `git archive` export contains `RUN_STATE.md` and `TASK_QUEUE.md`; neither was opened. Nothing below cites the index. I record it because the charter's prohibition is on the material arriving at all.
- **Read set beyond the packet.** `docs/process/coldgate_charter.md`; on the branch: `bfg-d/06-harvest-final-obligations-v1.1-source.md` §4.4–§4.5, `bfg-d/15-parser-esc-ruling-source.md` §5.2 (grep hits), the issuer, `battery_float.py`, the fixture builder, the Revision-5 test class, and `docs/phase_2/derivation_night_runbook.md` §2.2, §2.2a, §4.1 and the return-code table at `:3215-3218`. Packets 10, 41 and 42 were not needed and were not opened. The exhibits ex-00 to ex-04 were not re-read; the ruling and refuter quote them and nothing here turns on them.
- **Manifest.** All three input digests matched by `shasum -a 256` before any input was read: `b8a9cf87…` (ruling), `94879aba…` (refuter), `7505eb84…` (charge). Charter digest observed `099de884…`, identical to the charge.
- **Commit pin.** `origin/feat/2026-09-25-bfg-d` is `7f007c59`; `git diff --stat 3e984ecc 7f007c59` is two review-report files under `bfg-d/11-review/`, no code. Ruled on `3e984ecc`.
- **Scratch.** `/tmp/cgadd_tree` (export) and `/tmp/cgadd_probe/probe.py`, a subclass of the branch's `BatteryFloatRevisionFiveTests` using its `fresh`, `prepare` and fixtures, with `_registered_dispositions` patched to `{}` and `observe_machine` patched to the registered digest exactly as the branch's runbook-shape test does. Interpreter python 3.14, `PYTHONDONTWRITEBYTECODE=1`. The class's own 26 tests ran green under the same run (`Ran 30 tests … OK`). No `sudo`, `launchctl`, `powermetrics`, installer or inference; no background task, subagent or watcher; `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `~/Library/LaunchAgents` untouched. Scratch removed after this file was written.

## 1. Executed evidence

Every line is verbatim probe output at `3e984ecc`. "check" is `issuer.main(["check", …])` with `--preregistration` and `--preregistration-sha256`; "prepare" is the class's `prepare` helper.

```
P3  clean_fixture (W1, W1-prime, W2 all pass, all recorded); check W1-prime W2
    check   0 ['registration admissible for prepare-candidate: yes']
    prepare 3 ['REFUSED: valid same-epoch observations outside this registration: W1-d01, … W1-d12; not issued (ruling 46 addendum A-7)']
P3c control, all three named: check 0 'yes' | prepare 3 'REFUSED: W3 was opened despite at least 12 valid observations after W2'
P4  fixture (W1 confounded, W1-prime, W2; all recorded)
    check W1-prime W2        5 ['… no', '  blocker: computed non-pass session omitted: W1']
    check W1 W1-prime W2     5 ['… no', '  blocker: session W1: battery=confounded']
    prepare --battery-confounded-session-id W1 -> 0, candidate exists True
    check … --battery-confounded-session-id W1 -> SystemExit 2 (argparse: unrecognized arguments)
P5  fresh W1, W2 (pass, recorded); pin re-serialised in the working tree
    check W1 W2  0 ['ledger: calibration_ledger_head_uncommitted', 'registration admissible for prepare-candidate: yes']
    prepare      3 ['REFUSED: ledger: calibration_ledger_head_uncommitted']
P5b control, committed pin: check 0 'yes' | prepare 0
```

**R16 inventory** (`grep -rn verdict_record --include='*.py' joulewise scripts tests`, non-test): `battery_float.py:511` (definition), issuer `:1450` (`_battery_verdict`, the harvest writer). Tests: `tests/fixtures/epoch_bootstrap/build.py:268`, `tests/test_battery_float.py`. **`parse`** is called only inside `battery_float.py` (`:320` in `observe`, `:442` in `validate_window`) and in `tests/test_battery_float.py`; no production consumer calls it.

**Cause, verified by reading.** P3: the dry run has no A-7 clause; the issuer's sweep is `:1723-1738`. P4: the `check` subparser (`:2226`) defines `--session-ids` only; `--battery-confounded-session-id` exists on `prepare-candidate` alone (`:2287`); `_dry_run_epoch_bound` acknowledges only `session_ids` (`:367`), and a named non-pass session is a blocker (`:275`) while the issuer refuses "named both" (`:1519-1520`), so no `check` input can say yes on the sanctioned replacement route. P5: `check` appends the ledger refusal to `errors` (`:436-437`) and, when a session is named, returns `dry_run_code` and never consults `errors` (`:478-488`); the issuer refuses on the same snapshot's `refusal_reasons` (`:1523-1524`). Both load the snapshot with identical arguments (`require_committed_pin=True, verify_custody=False, mode="read_replay"`), so the refusal set is the same object on both sides; only the dry run ignores it.

## 2. Z1. The four MATERIAL findings

### 2.1 P5 (R7/R11): the dry run derives S from a snapshot the issuer refuses. AFFIRM. MATERIAL.

Executed (§1). The ruling's "anywhere else: no" was true of primitive callers and false of the defect class the charge named. Cure in §3.5 step 0 and §3.7: one helper `refuse_ledger(snapshot)`, called by the issuer (replacing `:1523-1524`), by the harvest writer (replacing `:1409-1410`), by the collector as its first step, and by `registration_dry_run` before its loop, so a refused ledger is a blocker for every registration, Revision 5 or not. **`target_epoch` (R11) AFFIRM:** the ruling left the dry run passing the constant `REVISION_FIVE_EPOCH` (`:349`) while the issuer passes the registration's own epoch (`:1552`). Cure in §3.6: one helper `registration_target_epoch(snapshot, session_ids)`; both consumers call it; the dry run's broad trigger at `:205-211` is deleted and the battery gate runs exactly when the derived epoch equals `REVISION_FIVE_EPOCH`, as the issuer's `revision_five` does.

### 2.2 P4 (R13): the sanctioned replacement route can never read "admissible". AFFIRM. MATERIAL, false no.

Executed (§1): `prepare --battery-confounded-session-id W1` exits 0 and writes the candidate; no `check` input exits 0 on the same fixture, and `check` rejects the flag outright. Runbook §4.1 says "Expect rc 0 … Proceed to §4.2" and the return-code row `:3217` makes exit 0 the signal. On the replacement route the runbook therefore dead-ends: the operator is told to "clear the named blocker at the desk", and the blocker cannot be cleared by any desk action. Cure in §3.8: `check` accepts `--battery-confounded-session-id` with the issuer's meaning; the dry run acknowledges the declared set, not the named set; a named non-pass session stays a blocker (the issuer refuses "named both"). The ruling's `acknowledged = frozenset(session_ids)` is superseded.

### 2.3 R16: the producer backdoor. AFFIRM. MATERIAL. `parse` NIT adopted.

`verdict_record(session, …)["status"]` is a replay-only gate with no record authentication, the mirror image of F1; the ruling's guard never sees it because the caller names no primitive. Inventory in §1: exactly one production caller (`_battery_verdict`, `:1450`) and one test-fixture caller (`build.py:268`). Cure in §3.9: `verdict_record` joins the guarded names with those two allowlisted callers. `parse` also joins, with the two in-module callers (`observe`, `validate_window`) allowlisted; it costs two allowlist rows and closes the last route by which a consumer could re-derive a slot verdict from custody bytes. `observe` and `require_pass` (the live probe used by `night_gate`, `evidence_night`, `run_night`, `arm_readiness_evidence_t0`, `validate_powermetrics_fiducial`) stay unguarded: they read the live machine, not a window's custody bytes, and cannot produce a window verdict.

### 2.4 P3 and R18: the ruling's test (iii) locks in a false yes. AFFIRM. MATERIAL.

Executed (§1, P3): the restored-bytes state of the ruling's RAW-TAMPER fixture is `check 0 / prepare 3 (A-7)`. As written, (iii)'s "exit 0 or the honest next blocker" passes on a false yes. Cure: (iii) asserts parity in its restore arm (§3.10 test iii), which requires A-7 in the dry run, which §2.5 rules.

### 2.5 R19: the parity promise. Option (a), bounded. A-7 is mirrored; the promise is enumerated.

**What the dry run is for.** Under Revision 5 the count-only dry run is run after every harvest (§2.2a step vii) and before `prepare-candidate` (§4.1). Its only value is that "yes" predicts the issuer, so that the desk can stop, replace, or continue without reading a value. A "yes" the issuer refuses is worth nothing; a "no" the issuer would issue dead-ends the runbook.

**Why A-7 is mirrored (a), not merely documented (b).** A-7 is decided from the snapshot alone (valid rows, target epoch, owner session, pinned registry), reads no B value, and the collector already computes the owner set F it needs; the marginal cost is one derived field and one blocker line. P3 is a false yes in exactly F1's fixture shape, the shape the three rounds enforced parity on, and the `:336-340` docstring that carried the promise is deleted by this cure. Documenting A-7 as "not mirrored" would leave the desk saying "yes" on the one non-battery clause that the real A-R5b route (a confounded W1 plus a replacement) exercises whenever the operator names the registration wrongly. The dry run's blocker prints a count and the owner session ids, not attempt ids, per its own rule at `:372-374`; that is presentation, and the issuer's text is unchanged.

**Why the full shared prefix (`assess_registration`) is REJECTED for this round.** The issuer's pre-value prefix interleaves value-free clauses with the predecessor load, the registration-text pins, the corpus floor (which needs `_select_members`, which reads B values) and the A-7/W3 sweeps placed after `_select_members`. Sharing the whole prefix means either re-ordering the claim-bearing issuer's refusal precedence or giving the shared function two modes (stop-at-first for the issuer, collect-all for the dry run), and two modes are the drift this gate exists to end. The science does not need it: every remaining unmirrored refusal (§3.11 list B) is a registration-shape or value rule whose cure is a written ruling, a re-naming or a restore, never a capture, so none can cost a night; and whether W3 is needed is decided from the valid counts the dry run already prints. What the science needs is that the promise be **true as stated**: so the promise is stated exactly, as list A in the docstring and in the runbook, and a parity test matrix (§3.10 test x) holds every clause in list A to "same answer on both".

**Why not change the "yes" line's text.** The line is asserted byte-exact by the branch's tests and the runbook-shape test; changing it buys nothing the enumerated promise does not, and costs a text churn across tests and runbook. The line stays; its meaning is fixed by list A.

### 2.6 Smaller items from the refuter

- R21 mutant (f): ADOPT (§3.10 viii). R2 (the ruling's stated clock is after its mtime) and R3 (prefer `git archive`): both NIT, noted; this addendum used `git archive`.
- R23: the Ed summary is rewritten in §4 at five lines.
- The refuter's K3 item 2 (the cadence report never checks derivation kind, `cad:76`): AFFIRM as NIT; §3.7 row for `report_window` adds the kind check with the seam's refusal text; it does not go into the seam (ruling §3.1 rule 5 stands).

## 3. Z2. Consumer-drift final texts v1.1

This section is complete. Where it repeats the ruling's §3, the text is restated so that an implementer reads one document. Where it differs, this section governs. Everything in the ruling's §4 (K3: loader digest, serializer, obligations §4.5/R2-7, sweep-inventory NIT) stands and is repeated in §3.12.

### 3.1 The seam (`joulewise/battery_float.py`, after `compare_verdict`)

```python
@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedSlot:
    slot: str
    attempt_id: str
    verdict: str                      # "pass" | "battery_float_confounded" | "battery_float_evidence_missing"
    reasons: tuple[str, ...]
    pre_raw_sha256: str | None
    post_raw_sha256: str | None
    pre_update_age_s: float | None
    post_update_age_s: float | None
    delta_q_mah: int | None
    instrument_evidence_sha256: str | None

@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedVerdict:
    session_id: str
    preregistration_sha256: str
    status: str                       # the RECORDED status; it governs every consumer decision
    slots: tuple[AuthenticatedSlot, ...]
    file_sha256: str                  # sha256 of the committed record bytes
    commit: str                       # the single adding commit

class BatteryVerdictRefusal(RuntimeError):
    """Authentication of a committed harvest verdict failed. Never a verdict; every consumer refuses."""
    def __init__(self, code: str, session_id: str, detail: str) -> None:
        self.code, self.session_id, self.detail = code, session_id, detail
        super().__init__(REFUSAL_TEXT[code].format(id=session_id, detail=detail))

def authenticate_committed_verdict(
    repo_root: Path | str, *, session: Any, preregistration_sha256: str,
) -> AuthenticatedVerdict:
```

Rules:
1. The session id is `session.session_id`; no separate id argument.
2. `preregistration_sha256` must satisfy `_is_sha256`, else `BatteryVerdictRefusal("registration_digest_required", …)` before any I/O. `load_committed_verdict`'s parameter is narrowed to `preregistration_sha256: str` and `:591` loses its `is not None` arm.
3. Order: `validate_window(session)`; `CustodyFailure` → `custody_failure`. Then `load_committed_verdict(root, session.session_id, session=session, preregistration_sha256=…)`; `NoRecord` → `record_unauthenticated`; `authentication_io.V2AuthenticationInputError` → `record_unauthenticated` with `str(exc)` as detail. Then `compare_verdict(record, recomputed)`; non-`None` → `verdict_mismatch`. Each refusal chains the primitive exception as `__cause__`. Obligations v1.1 §4.4 step 3 order stands.
4. The result is built from the record: `status = record["status"]`, `slots` from `record["slots"]` with `reasons` as a tuple, `file_sha256`/`commit` from the loader. `CommittedVerdict` is not exposed.
5. No eligibility check in the seam; eligibility is the collector's (§3.5) and the cadence report's (§3.7).

### 3.2 Refusal codes and messages (`REFUSAL_TEXT`, one class, four codes)

| `code` | message |
|---|---|
| `registration_digest_required` | `battery-float registration digest missing or invalid for {id}` |
| `custody_failure` | `battery-float custody failure for {id}: {detail}; restore the custody bytes byte-exact from the harvest archive` |
| `record_unauthenticated` | `battery-float harvest verdict missing or uncommitted for {id}: {detail}` |
| `verdict_mismatch` | `battery-float harvest verdict for {id} cannot be re-established from raw bytes ({detail}); custody failure` |

The issuer appends `; not issued`; its three existing strings (`:1588-1606`) are byte-identical after migration.

### 3.3 Dry-run rendering of the four codes (`DRY_RUN_TEXT`, in the issuer module)

`custody_failure` → `battery custody failure: {detail}`; `record_unauthenticated` → `battery harvest verdict missing or uncommitted ({detail})`; `verdict_mismatch` → `battery harvest verdict cannot be re-established ({detail})`; `registration_digest_required` → `--preregistration and --preregistration-sha256 are required`. A code absent from the table renders `battery verdict refused ({code}): {message}` and is a blocker. The blocker line is `f"{'session' if id in session_ids else 'computed session'} {id}: {DRY_RUN_TEXT[code]}"`.

### 3.4 Two shared refusal helpers (issuer module, beside `refuse_repeated_sessions`)

```python
def refuse_ledger(snapshot: Any) -> None:
    """The issuer's ledger refusal (today :1523-1524), the ONE home of that text."""
    if snapshot.refusal_reasons:
        raise PrepareRefusal("ledger: " + ", ".join(snapshot.refusal_reasons))

def refuse_named_both(session_ids: Sequence[str], confounded_ids: Sequence[str]) -> None:
    if set(session_ids) & set(confounded_ids):
        raise PrepareRefusal("session named both as registration and battery-confounded")
```

Callers: `_prepare_candidate` (`:1519-1520` and `:1523-1524` replaced by calls), `_battery_verdict` (`:1409-1410` replaced), the collector (step 0), and `registration_dry_run` (§3.8).

### 3.5 The collector (issuer module, beside `_battery_computed_set`)

```python
@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedBatteryEpoch:
    target_epoch: Mapping[str, Any]              # types.MappingProxyType of the registration's own epoch
    computed_ids: frozenset[str]                 # R ∪ F ∪ S from _battery_computed_set
    eligible_ids: frozenset[str]                 # computed_ids that are present, derivation-kind and terminal
    verdicts: tuple[AuthenticatedVerdict, ...]   # one per eligible id, sorted by id
    non_pass_ids: frozenset[str]                 # {v.session_id for v in verdicts if v.status != "pass"}
    foreign_rows: tuple[tuple[str, str], ...]    # A-7: (attempt_id, owner session id), sorted by attempt id

def authenticate_battery_epoch(
    snapshot: Any, registration_ids: Sequence[str], *, repo_root: Path,
    target_epoch: Mapping[str, Any], preregistration_sha256: str,
) -> AuthenticatedBatteryEpoch:
```

In order: (0) `refuse_ledger(snapshot)`. (1) Authenticate every **named** id that is present, derivation-kind and terminal, sorted, through the seam. (2) `dispositions = _registered_dispositions()` (`PrepareRefusal` propagates). (3) `computed = _battery_computed_set(snapshot, set(registration_ids), target_epoch, dispositions)`. (4) Authenticate every remaining eligible id, sorted. (5) `non_pass_ids` as above. (6) `foreign_rows` = every `snapshot.observations` row with `classification_disposition == "valid"`, `dict(identity_epoch) == target_epoch`, `content_id not in dispositions`, and `bracket_session_id not in (set(registration_ids) | non_pass_ids)`; this is the issuer's `:1727-1735` predicate verbatim, with `computed_confounded` renamed. (7) Return the frozen result. No `continue` after a refusal, no partial collection, no caller-supplied prefiltered list. Named-first is required by `test_dry_run_never_reads_member_evidence_without_authentic_verdict` (`:2690`) and by `predates_battery_float`'s evidence read for unnamed sessions.

### 3.6 The target epoch (issuer module)

```python
def registration_target_epoch(snapshot: Any, session_ids: Sequence[str]) -> dict[str, Any]:
    """The registration's own epoch: the unanimous identity_epoch of the finalized rows of its
    named sessions that are present and terminal.  Refuses 'registration: its sessions hold no
    observations' when there are none and 'registration: rows disagree on the identity epoch'
    when they differ.  Both texts are the issuer's existing ones (:1550, :1645)."""
```

`_prepare_candidate`: `target_epoch = registration_target_epoch(snapshot, session_ids)` replaces `:1552`; the `:1548-1550` observations load and the `:1644-1646` disagreement check stay (all named sessions are terminal there, so the helper's answer equals `observations[0].identity_epoch`). `registration_dry_run`: see §3.8 step 2. The dry run's `revision_five_named` trigger (`:205-211`, `:238`) is deleted; the battery gate runs iff `target_epoch == REVISION_FIVE_EPOCH`, exactly the issuer's `revision_five`.

### 3.7 The policy and its two renderings

```python
@dataclasses.dataclass(frozen=True, slots=True)
class BatteryEpochPolicy:
    clean_declared: tuple[str, ...]   # declared ∩ {v.session_id} − non_pass_ids
    not_computed: tuple[str, ...]     # declared − {v.session_id}
    omitted: tuple[str, ...]          # non_pass_ids − declared
    over_bound: tuple[str, ...]       # sorted(non_pass_ids) if len(non_pass_ids) > 1 else ()
    foreign_rows: tuple[tuple[str, str], ...]   # epoch.foreign_rows

def battery_epoch_policy(epoch: AuthenticatedBatteryEpoch, *, declared: frozenset[str]) -> BatteryEpochPolicy:
```

One decision, two renderings, both in the issuer module:

- `refuse_battery_policy(policy)`: raises, in this order, the issuer's **unchanged** texts: when any of `clean_declared`, `not_computed`, `omitted` is non-empty, `PrepareRefusal("battery-confounded set mismatch: " + "; ".join(parts))` with the three parts worded and ordered exactly as `:1622-1630` (ids comma-joined); then when `over_bound`, `PrepareRefusal("more than one battery-float non-pass window in this epoch: " + ", ".join(over_bound) + "; the epoch stops and returns to council")`. It does **not** raise A-7: the issuer raises A-7 at its present place (`:1737-1741`, after `_select_members`) from `epoch.foreign_rows`, text unchanged (`"valid same-epoch observations outside this registration: " + ", ".join(attempt ids) + "; not issued (ruling 46 addendum A-7)"`), so the issuer's refusal precedence is unchanged.
- `dry_run_battery_blockers(policy) -> list[str]`: `clean session declared confounded: <id>` per id; `declared session is not a terminal derivation session of this registration or an A-7 foreign-row owner: <id>` per id; `computed non-pass session omitted: <id>` per id (the existing text, `:2770` stays byte-identical); `more than one battery-float non-pass window in this epoch: <ids>`; and, when `foreign_rows` is non-empty, `valid same-epoch observations outside this registration: <n> rows owned by <owner ids sorted, comma-joined> (ruling 46 addendum A-7)`. Counts and session ids only; never attempt ids (`:372-374`).

### 3.8 `check` and `registration_dry_run`

- The `check` subparser gains `--battery-confounded-session-id`, `action="append", default=[]`, help text identical to `prepare-candidate`'s. `check` passes `confounded_ids=[s for s in args.battery_confounded_session_id if s]` to the dry run.
- `registration_dry_run(snapshot, session_ids, *, repo_root=None, preregistration_sha256=None, confounded_ids: Sequence[str] = ())`. Existing direct callers stay valid.
- Body, in order: (1) `refuse_ledger`, `refuse_repeated_sessions(confounded_ids)`, `refuse_named_both` each inside `try`, `PrepareRefusal` → `blockers.append(reason)`; `battery_gate_blocked = True` on any. (2) `eligible_named = [s for s in session_ids if present, derivation-kind, terminal]`; if non-empty, `target_epoch = registration_target_epoch(snapshot, eligible_named)` inside `try`, `PrepareRefusal` → blocker and `battery_gate_blocked`. (3) If the gate is not blocked and `target_epoch == REVISION_FIVE_EPOCH`: require the digest (`:237-241` text unchanged, blocker `session <id>: --preregistration and --preregistration-sha256 are required` for each eligible named id, and `battery_gate_blocked`); else `epoch = authenticate_battery_epoch(snapshot, session_ids, repo_root=root, target_epoch=target_epoch, preregistration_sha256=digest)` inside `try`; `BatteryVerdictRefusal` → the §3.3 blocker and `battery_gate_blocked`; `PrepareRefusal` → its reason and `battery_gate_blocked`. (4) The per-session loop as today with the primitive calls `:243`, `:250`, `:263` deleted: the battery line `<id>: battery=<label> recorded=<recorded>` is rendered from `epoch`'s verdict for that id (`label` = the recomputed status the seam computed, exposed as `AuthenticatedVerdict.status` **of the record**, both stripped of `battery_float_`; since the seam refuses on any difference the two labels are equal and the line keeps its shape); a named non-pass session keeps the `valid=0 excluded=battery_<label>` line and the `session <id>: battery=<label>` blocker. When the gate is blocked, every member read is skipped (as today). (5) After the loop, when the gate is not blocked: `blockers.extend(dry_run_battery_blockers(battery_epoch_policy(epoch, declared=frozenset(confounded_ids))))`. (6) When `confounded_ids` is non-empty, the line `battery-confounded declared: <ids comma-joined>` is appended after the per-session lines; with no flag the output is byte-identical to today's. (7) `_dry_run_epoch_bound` (`:332-373`) and its call (`:315-317`) are deleted.
- `check` return code when a session is named: unchanged (the dry run's code). P5 now exits 5 because the ledger refusal is a blocker.

### 3.9 `_prepare_candidate` and the other consumers

| Site | Change |
|---|---|
| `_prepare_candidate` `:1519-1524` | `refuse_named_both(session_ids, named_confounded)`; `refuse_ledger(snapshot)`. |
| `_prepare_candidate` `:1552` | `target_epoch = registration_target_epoch(snapshot, session_ids)`. |
| `_prepare_candidate` `:1573-1612` | `epoch = authenticate_battery_epoch(snapshot, session_ids, repo_root=Path(args.repo_root), target_epoch=target_epoch, preregistration_sha256=args.preregistration_sha256)` inside `if revision_five:`; `except BatteryVerdictRefusal as e: raise PrepareRefusal(f"{e}; not issued") from e`. When not Revision 5, `epoch` is an empty `AuthenticatedBatteryEpoch` (empty sets and tuples, `foreign_rows` computed by the same predicate so A-7 keeps working for every generation, as `:1722-1735` does today with `dispositions = {}`). |
| `_prepare_candidate` `:1613-1640` | Replaced by `refuse_battery_policy(battery_epoch_policy(epoch, declared=frozenset(named_confounded)))`; `computed_confounded = set(epoch.non_pass_ids)`; `:1641` unchanged. |
| `_prepare_candidate` `:1722-1741` | The foreign list is `[attempt for attempt, _ in epoch.foreign_rows]`; the second `_registered_dispositions()` call at `:1723` is deleted; refusal text unchanged. |
| derivation notes `:1979-1989` | Serialized from `epoch.verdicts` (`session_id`, `status`, `file_sha256`, `commit`; `battery_confounded_sessions` entries add `slots` via `dataclasses.asdict`). Artifact field names unchanged. |
| `_battery_verdict` `:1409-1410` | `refuse_ledger(snapshot)`. Producer call `:1450` unchanged. |
| cadence `report_window` `:76-95` | Add the kind check: a session that is not `SESSION_KIND_DERIVATION` → `ValueError("session <id> is kind <kind>, not derivation")`. Then `verdict = battery_float.authenticate_committed_verdict(root, session=session, preregistration_sha256=preregistration_sha256)`; `except BatteryVerdictRefusal as e: raise ValueError(str(e)) from e`; `battery_verdict = verdict.status`. |
| `derive_record`, `epoch_equivalence_check` | Unchanged; they refuse Revision 5 first and call nothing. |
| `battery_float.verdict_record`, `parse` | Unchanged; guarded (§3.10). |

### 3.10 The guard (`tests/test_battery_float_consumers.py`)

An AST test over every tracked `*.py` under `joulewise/` and `scripts/` (walk the tree). Guarded names: `load_committed_verdict`, `validate_window`, `compare_verdict`, `verdict_record`, `parse`. It flags: (1) any `ImportFrom` of `joulewise.battery_float` naming a guarded name; (2) any `Attribute` whose `attr` is a guarded name and whose value resolves through the module's import aliases (`import … as`, `from … import … as`) to `joulewise.battery_float`; references, not just calls; (3) any `Name` bound by such an import; (4) any string `Constant` equal to a guarded name outside a docstring position. Inside `battery_float.py`, bare `Name` references to guarded names are flagged unless the enclosing function is allowlisted for that name.

**Allowlist, exactly six (file::function → names):** `joulewise/battery_float.py::authenticate_committed_verdict` → `validate_window, load_committed_verdict, compare_verdict`; `joulewise/battery_float.py::verdict_record` → `validate_window`; `joulewise/battery_float.py::observe` → `parse`; `joulewise/battery_float.py::validate_window` → `parse`; `scripts/issue_calibration_acceptance_generation.py::_battery_verdict` → `verdict_record`; `tests/fixtures/epoch_bootstrap/build.py::write_verdict_record` → `verdict_record` (the only test file the guard walks). Positive assertion: `authenticate_committed_verdict` contains a call to each of its three names. Self-test: the checker over a fixture holding `3e984ecc:358`'s body reports one violation; over an aliased import plus an attribute reference, two; over `verdict_record(...)["status"]` in a non-allowlisted function, one. Direct primitive use in test files is permitted only in `tests/test_battery_float.py`, `tests/battery_float_fixture.py`, `tests/fixtures/epoch_bootstrap/build.py` and `tests/test_validate_powermetrics_fiducial_derivation_only.py`; the issuer test's call at `:2484` migrates to the seam.

### 3.11 The parity promise (docstring of `registration_dry_run`, runbook `:3217`, runbook §4.1; same PR)

**List A, mirrored: the dry run says "no" wherever `prepare-candidate` refuses on one of these, and the answer agrees on both tools.** (1) ledger refusal (`refuse_ledger`); (2) a named session absent, not derivation-kind, or not terminal; (3) repeated ids; a session named both as registration and confounded; (4) the registration digest missing on a Revision 5 registration; (5) the battery gate for every computed window: custody, record, disagreement, through the seam; (6) the confounded declaration exact-set check and the one-replacement bound; (7) A-7 foreign rows; (8) pending or unresolved prior-set rows. **List B, not mirrored (issuer only):** the predecessor acceptance; the registration-text pins (`os_build`, `powermetrics`, Revision 5 launch-context pins); corpus floor; night count and W1/W2/W3 order; slot count; W1 futility; the W3 rule; member custody, plateau inset and screens. Every list B refusal is a written-ruling, re-naming or restore matter; none is cured by a capture.

Runbook `:3217` becomes: `check --session-ids …` | 0 | The registration passes every desk-mirrored issuer check (ledger, terminality, battery gate, confounded declaration and bound, A-7, prior-set rows). `prepare-candidate` may still refuse on the registration-shape and value rules it alone checks (§4.2 table). | Proceed to §4.2 …`. Runbook §4.1 gains, on the replacement route, `--battery-confounded-session-id "<WX>"` naming the excluded window, with one sentence: the dry run then says "yes" exactly when `prepare-candidate` with the same declaration issues. `runbook_dry_run_invocations()`'s test maps an invocation carrying the flag to the confounded fixture (`<S1>`→`W1-prime`, `<S2>`→`W2`, `<WX>`→`W1`) and expects 0.

Obligations v1.1 §4.5 is reissued in the same PR: the dry-run and cadence paragraphs say "through `authenticate_committed_verdict`", the dry-run paragraph names the declaration flag, the A-7 blocker and the ledger blocker, and the consumer list adds `epoch_equivalence_check` and drops the removed continuation gate (R2-7).

### 3.12 Tests (RED at `3e984ecc` where marked; GREEN after)

(i) Round 1: keep `:2767` and `:2450`; both flow through `battery_epoch_policy`.
(ii) Round 2: keep `:2707`, `:2725`; add `rerecord_verdict` on an unnamed W1 → blocker `path history is not a single adding commit`.
(iii) Round 3a, RED: unnamed W1 pre raw +1 byte; `check W1-prime W2` → 5, `blocker: computed session W1: battery custody failure: d01/pre expected …`; `prepare` → 3, same custody text, no candidate; restore byte-exact → **parity**: `check` and `prepare` agree, which on this fixture is `5` and `3` with A-7 on both (no `omitted`, no custody blocker).
(iv) Round 3b, RED both arms: record `pass` over confounded bytes → `check` 5 with `battery harvest verdict cannot be re-established (status recorded pass recomputed battery_float_confounded)` and no `omitted` blocker; record `evidence_missing` over passing bytes → the mismatch blocker and no `omitted` blocker; `prepare` 3 on both.
(v) Loader digest: `None`, `""`, 63 chars → `registration_digest_required`, `_git` never called; `load_committed_verdict(..., preregistration_sha256=None)` never returns a record.
(vi) Ordering: extend `:2690`: unnamed W1 tampered, named clean → `_read_member_evidence` never called in dry run or issuer.
(vii) Seam unit tests in `tests/test_battery_float.py`: one per code, `__cause__`, exact text, frozen result, record-not-recomputation for `status`/`slots`/`reasons`.
(viii) Mutation kills with the branch's `importlib` pattern: (a) delete the seam's `validate_window` call; (b) delete `compare_verdict`; (c) collector `except BatteryVerdictRefusal: continue`; (d) collector restricted to named ids; (e) dry run drops the policy call; (f) dry run's `BatteryVerdictRefusal` handler body → `pass`; (g) collector step (6) returns `()`; (h) collector step (0) deleted. Each must fail at least one of (i)–(iv), (x).
(ix) Cadence: tampered raw and disagreeing record → `ValueError` with §3.2 text; non-derivation session → the kind `ValueError`; `diagnostic_only` keyed off `verdict.status`; continuation and equivalence tests unchanged.
(x) **Parity matrix, RED at `3e984ecc` in rows P3, P4, P5.** Each row runs `check` (via `issuer.main`) and `prepare` on the same fixture and asserts both refuse on the same session id or both admit: P3 (clean epoch, W1 unnamed) → both A-7; P4 (confounded W1, declared on both) → `check` 0 and `prepare` 0; P4-undeclared → both `omitted: W1`; P4-named (W1 named and declared) → both `named both`; P5 (re-serialised pin) → both `ledger: calibration_ledger_head_uncommitted`; P5-control → both admit; clean-declared (`--battery-confounded-session-id W1` on the clean fixture) → both `clean session declared confounded`; target-epoch (a named session whose rows carry a non-Revision-5 epoch) → the battery gate is skipped on both and the digest is not required.
(xi) Target epoch: two named sessions with differing epochs → `check` blocker and `prepare` refusal both `registration: rows disagree on the identity epoch`.
(xii) Guard: the self-test in §3.10; the guard run over the `3e984ecc` tree (as a fixture directory) reports `issuer:243`, `:250`, `:263`, `:358`, `:1586`, `:1593`, `:1602`, `cad:81`, `:85`, `:93`.
(xiii) Runbook shapes: `:2742` extended per §3.11.

### 3.13 Held to the same pattern in this round (ruling §4 restated)

The loader's optional digest (§3.1 rule 2); the derivation-notes serializer (§3.9); obligations §4.5/R2-7 (§3.11); the sweep inventory's `UNGATED` labels and its `_dry_run_epoch_bound` row (`tests/test_battery_float_sweep.py:28-29, 46-50`), corrected when the function is deleted.

## 4. Plain summary for Ed (5 lines)

1. The desk "is the registration ready?" check and the real issuing tool disagree in four ways at the reviewed commit; I ran all four: altered or mismatched battery files, a spare window's stray rows, a legitimately replaced window (the desk can never say "ready"), and an uncommitted ledger pin.
2. No measurement number is exposed by any of them; the issuer still refuses. The harm is a wrong desk "ready" or a runbook dead end.
3. Cure: one function authenticates a window's battery verdict; one function walks the epoch and decides the battery, declaration, bound and stray-row rules; both tools call it and render one shared decision; the desk check gains the same "this window was excluded" flag the issuer has.
4. The desk check's promise is now written down exactly: which issuer refusals it mirrors and which it does not; a test holds every mirrored one to "same answer on both tools".
5. A mechanical test forbids any other code from calling the pieces, including the producer that writes verdict files. Nothing is armed; nothing here touches a window.

## 5. Verdict table

| Item | Verdict | Tier | Where |
|---|---|---|---|
| P5 / R7 ledger refusal ignored by the dry run | AFFIRM, executed | MATERIAL | §2.1, §3.4, §3.8 |
| R11 `target_epoch` not bound identically | AFFIRM | MATERIAL | §2.1, §3.6 |
| P4 / R13 replacement route can never read yes | AFFIRM, executed | MATERIAL | §2.2, §3.7, §3.8 |
| R16 producer backdoor; `parse` NIT | AFFIRM; NIT adopted | MATERIAL | §2.3, §3.10 |
| P3 / R18 test (iii) locks in a false yes | AFFIRM, executed | MATERIAL | §2.4, §3.12 (iii) |
| R19 parity promise | Option (a) bounded: A-7 mirrored; promise enumerated; full shared prefix REJECTED for this round | MATERIAL | §2.5, §3.11 |
| R21 mutant (f) | ADOPT | NIT | §3.12 (viii) |
| Refuter K3 cadence kind check | AFFIRM | NIT | §3.9 |
| Ruling §3.1–3.3, §3.5 (seam, codes, order, sites) | STAND, restated | — | §3.1–3.3, §3.9 |
| Ruling §3.4 policy `acknowledged = session_ids` | SUPERSEDED by the declared set | — | §3.7 |
| Ruling §4 K3 | STAND | — | §3.13 |

Scratch removed after this file was written: `rm -rf /tmp/cgadd_tree /tmp/cgadd_probe`.
