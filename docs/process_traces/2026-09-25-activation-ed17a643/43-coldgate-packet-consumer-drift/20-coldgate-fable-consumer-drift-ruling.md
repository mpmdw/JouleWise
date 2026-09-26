# Cold-gate ruling CONSUMER-DRIFT-ESC-01 (Fable 5.1, cold judge)

Ruled 2026-09-26, about 01:00–01:35 PDT, in worktree `JouleWise-wt-ed17a643-cg-cd` at `05790305`. BFG-D examined at `3e984ecc` in a detached `/tmp` worktree. All line numbers are at `3e984ecc` unless stated.

**Verdicts.** K1 AFFIRM: the drift is real, executed twice at `3e984ecc`, and confined to `_dry_run_epoch_bound`; a third, latent hole (an optional registration digest in the loader) is named. K2 AFFIRM with the exact final text in §3: one seam `authenticate_committed_verdict` in `battery_float.py`, one epoch collector `authenticate_battery_epoch` in the issuer module, the obligations v1.1 §4.4 order **stands** (replay, then load, then compare), one AST guard with a two-entry allowlist, and a named test matrix that includes all three rounds. K3: hold the loader's optional digest, the derivation-notes serializer and the obligations §4.5 consumer list (R2-7) to the same pattern in the same fix round; nothing else in BFG-D has the signature. Ed summary in §5.

## 0. Contamination disclosure and verification before the merits

- **Context I received without asking.** The harness loaded the project `CLAUDE.md`, the global `~/.claude/CLAUDE.md`, and the one-line-per-entry index `MEMORY.md` of the operating loop's session memory into my system prompt before I read the charge. I did not open any memory file, `RUN_STATE.md`, `TASK_QUEUE.md`, council log, run report or scratchpad. The index lines carry loop context (checkpoint names, standing directives); I have not used any of it in this ruling, and nothing below cites it. I record it because the charter's §4 prohibition is on the material arriving at all.
- **Read set beyond the packet.** `docs/process/coldgate_charter.md`; on the branch, `bfg-d/06-harvest-final-obligations-v1.1-source.md` (§4.3–§4.6, §4.10), `bfg-d/12-fix-contract-r5.md` (FX-5–FX-9), grep hits only in `bfg-d/15`, `18`, `20`, `11-review/05`; the production and test code named below; `docs/phase_2/derivation_night_runbook.md` grep hits for the `check` invocations. Packets 10, 41 and 42 were not needed and were not opened.
- **Charter digest.** Expected (from the charge): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Observed: identical, by `shasum -a 256 docs/process/coldgate_charter.md` in this worktree. The exhibit manifest's five digests all matched by `shasum -a 256` before any exhibit was read.
- **Commit pin.** `git fetch origin feat/2026-09-25-bfg-d` returned `7f007c59`, one commit past the charged `3e984ecc` (its message: "round-2 delta reports"; a docs commit). I ruled on `3e984ecc` as charged; nothing here depends on `7f007c59`.
- **Write-scope deviation (disclosed).** A detached worktree `/tmp/cg-bfgd` at `3e984ecc` (registered in the shared `.git/worktrees`, removed with `git worktree remove` after this file was written) and one probe script `/tmp/cg-probe/probe_f1.py`, whose fixtures went to `tempfile` directories. Interpreter Homebrew python 3.14.7, `PYTHONDONTWRITEBYTECODE=1`. No `sudo`, `launchctl`, `powermetrics`, installer or inference; `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and `~/Library/LaunchAgents` untouched. No background task, subagent or watcher.

## 1. Executed evidence

**E1. Caller inventory** (`git grep -n -E '(load_committed_verdict|validate_window|compare_verdict)' 3e984ecc -- '*.py'`, excluding `tests/`; the `window_duration_margins.py` hits are `validate_window_duration_margins_receipt`, a different function):

| Production caller | `validate_window` | `load_committed_verdict` | `compare_verdict` |
|---|---|---|---|
| `joulewise/battery_float.py` `verdict_record` (producer) | `:514` | — | — |
| issuer `registration_dry_run`, named loop | `:243` | `:250` | `:263` |
| issuer `_dry_run_epoch_bound`, computed loop | **absent** | `:358` | **absent** |
| issuer `_prepare_candidate` | `:1586` | `:1593` | `:1602` |
| `scripts/calibration_cadence_report.py` `report_window` | `:81` | `:85` | `:93` |

Test callers: `tests/test_battery_float.py` (30 hits), `tests/test_issue_calibration_acceptance_generation.py:2484`, `tests/test_validate_powermetrics_fiducial_derivation_only.py:680`. No `getattr`/`importlib` access to the three names in production (`git grep` for `getattr\(\s*battery_float`, `battery_float.__dict__`, `importlib.*battery_float`: one hit, in a test). Aliased import exists (`arm_readiness_evidence_t0.py:37`, `from joulewise import battery_float as _battery_float`), so the guard in §3.6 must resolve aliases.

**E2. Reproduction** (`/tmp/cg-probe/probe_f1.py`, a subclass of the branch's own `BatteryFloatRevisionFiveTests` using its `fresh`, `dry_run`, `prepare` helpers, so the fixtures are the production test fixtures; `_registered_dispositions` patched to `{}` exactly as the branch's tests do). Observed lines, verbatim:

```
RAW-TAMPER  check rc 0 | registration admissible for prepare-candidate: yes | blockers: []
RAW-TAMPER  prepare rc 3 | candidate exists False
            REFUSED: battery-float custody failure for W1: d01/pre expected 5003c76c… observed 77a023e0…; restore the custody bytes byte-exact from the harvest archive; not issued
DISAGREE2   honest W1 status: battery_float_confounded   (record then rewritten to status "pass", raw bytes untouched)
DISAGREE2   check rc 0 | registration admissible for prepare-candidate: yes | blockers: []
DISAGREE2   prepare rc 3 | REFUSED: battery-float harvest verdict for W1 cannot be re-established from raw bytes (status recorded pass recomputed battery_float_confounded); custody failure; not issued
DISAGREE    (record rewritten to evidence_missing over passing bytes)
            check rc 5 | blockers: ['  blocker: computed non-pass session omitted: W1']
            prepare rc 3 | REFUSED: battery-float harvest verdict for W1 cannot be re-established from raw bytes (status recorded battery_float_evidence_missing recomputed pass); custody failure; not issued
NAMED-TAMPER (W1 named) check rc 5 | blocker: session W1: battery custody failure: d01/pre expected …
```

Fixture in every case: W1, W1-prime, W2 all Revision-5, terminal, with committed records; `check --session-ids W1-prime --session-ids W2` (W1 unnamed but computed).

**E3.** The four existing round-1/round-2 regression tests (`…omitted`, `…without_an_authentic_verdict`, `…recorded_under_another_registration`, `…never_reads_member_evidence…`) pass at `3e984ecc` (`Ran 4 tests … OK`). They cover omission and `NoRecord` for an unnamed session and never alter raw bytes or the record's content: that is exactly the gap round 3 fell through.

## 2. K1. Is the drift real, and is it anywhere else? AFFIRM. MATERIAL.

**Real.** E2 shows two distinct unnamed-session paths on which `check` exits 0 and prints "admissible: yes" while `prepare-candidate` refuses and writes nothing: altered raw bytes (custody failure) and a committed record that disagrees with intact raw bytes (in the pass direction). In the non-pass direction the dry run blocks, but with `computed non-pass session omitted: W1`, which tells the operator to name W1 as confounded; the issuer's truth is a custody refusal with a different cure (restore or re-harvest). That is the same drift in a third costume: the dry run's exclusion-shaped answer where the issuer's answer is a refusal. Cause, verified by reading: `_dry_run_epoch_bound` `:353-366` calls `load_committed_verdict` (`:358`) and then uses `record["status"]` (`:366`); it never calls `validate_window` or `compare_verdict`. The docstring `:336-340` ("never says admissible where prepare-candidate refuses") is false for custody and disagreement.

**Tier.** MATERIAL, as both deltas tiered it. No B value is printed or written; the issuer refuses; the harm is a wrong desk stop/continue decision for W1/W2 and a wasted window, plus three rounds of the same signature. It becomes BLOCKER for the final pass only in the sense of §4: BFG-D must not pass the final gate with the pattern uncured.

**Anywhere else.** No. The named dry-run loop (`:243-280`), the issuer (`:1586-1608`) and the cadence report (`:81-95`) each perform replay, load and compare, and the NAMED-TAMPER line in E2 shows the named path catching the same tamper. `issue_epoch_continuation.derive_record` (`:84-88`) and `epoch_equivalence_check` (`:470-474`) refuse any Revision-5 session before reading anything and call no primitive. The `battery-verdict` writer (`_battery_verdict` `:1393-1470`) calls only `verdict_record`, the producer.

**One latent hole with the same shape**, not yet exploited by any caller: `load_committed_verdict(…, preregistration_sha256: str | None)` skips the registration identity check when passed `None` (`battery_float.py:591`). FX-7 (fix round 1) was three consumers doing precisely that. Every current caller passes a value, but the parameter's type invites the next drift. The cure is in §3.1 and §3.7 item (v).

## 3. K2. The cure, as exact final text. AFFIRM (both consults' shared core), with the amendments stated.

### 3.1 The seam (`joulewise/battery_float.py`, placed after `compare_verdict`)

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
    """The ONLY way a consumer obtains a battery verdict (obligations v1.1 §4.4 step 3, §4.5).

    Replays the window from raw bytes, loads the committed record under the
    registration digest, requires ``compare_verdict`` to find no difference,
    and returns a frozen result.  Raises ``BatteryVerdictRefusal``; nothing
    else escapes except programmer errors.
    """
```

Rules the seam must satisfy:

1. The session id is `session.session_id`; there is no separate id argument (Astra's form; one fewer thing that can disagree).
2. `preregistration_sha256` is required and must satisfy `_is_sha256`; otherwise `BatteryVerdictRefusal("registration_digest_required", …)` before any I/O. The seam never passes `None` to the loader.
3. Order: `validate_window(session)` first; `CustodyFailure` → `custody_failure`. Then `load_committed_verdict(root, session.session_id, session=session, preregistration_sha256=…)`; `NoRecord` → `record_unauthenticated`; `V2AuthenticationInputError` from `authentication_io` (a malformed committed file, today an uncaught traceback) → `record_unauthenticated` with `str(exc)` as the reason. Then `compare_verdict(record, recomputed)`; a non-`None` difference → `verdict_mismatch`. Each refusal chains the primitive exception as `__cause__`.
4. The result is built from the **record** (never from the recomputation): `status = record["status"]`, `slots` from `record["slots"]` with `reasons` as a tuple, `file_sha256`/`commit` from the loader. `CommittedVerdict` (a `dict`) is not exposed; Astra's point that a frozen dataclass wrapping a dict is not immutable is correct and adopted.
5. No eligibility check (terminal, derivation-kind) lives in the seam. Eligibility is the collector's single job (§3.4) and the cadence report's existing check; the seam stays free of ledger imports because `night_gate` imports this module on every arm path (`battery_float.py:548-550`).

### 3.2 Refusal codes and exact messages (`REFUSAL_TEXT`)

| `code` | message |
|---|---|
| `registration_digest_required` | `battery-float registration digest missing or invalid for {id}` |
| `custody_failure` | `battery-float custody failure for {id}: {detail}; restore the custody bytes byte-exact from the harvest archive` |
| `record_unauthenticated` | `battery-float harvest verdict missing or uncommitted for {id}: {detail}` |
| `verdict_mismatch` | `battery-float harvest verdict for {id} cannot be re-established from raw bytes ({detail}); custody failure` |

One class, four codes. Sol's single-class form is adopted; Astra's six subclasses are not: nothing catches them separately, and `session_ineligible` and `authentication_input_failure` are folded into the collector and `record_unauthenticated` respectively. The issuer appends `; not issued`, so its three existing refusal strings (`:1588-1606`) are byte-identical after migration and the issuer tests keep their assertions.

### 3.3 The order. Obligations v1.1 §4.4 step 3 order STANDS: replay, then load, then compare.

Sol proposes load-first. REJECT. (a) §4.4 step 3 and §4.5 fix replay-first for every consumer, and the branch's tests assert the resulting messages (e.g. the `recorded=absent` line with a recomputed label, `test_dry_run_names_the_recorded_verdict_and_blocks_without_one`). (b) Every outcome of either order is a refusal, so the order has no soundness content; changing it is a semantic change with no benefit, and the escalation rule says centralize, not redesign. (c) Custody-first reports the more useful state: a window with damaged raw bytes cannot get a record from `battery-verdict` until restored (`:2516-2521` test), so custody is the blocking cure whether or not a record exists. Sol's objection that the named dry run prints a recomputed `battery=<status>` label before authentication is noted and REJECTED as a defect: the label is instrument state, not a B value, and §4.5 specifies that line. The seam computes it; the dry run prints it.

### 3.4 The single collector for S, and who calls it

The set-derivation helper `_battery_computed_set` (`:1285-1317`) is already the single collector of the computed ids and is already shared (`:349`, `:1577`). The drift was never in deriving C = R ∪ F ∪ S; it was in what each consumer did with C's members. The cure is therefore one function that owns the loop:

```python
@dataclasses.dataclass(frozen=True, slots=True)
class AuthenticatedBatteryEpoch:
    computed_ids: frozenset[str]        # R ∪ F ∪ S, from _battery_computed_set
    eligible_ids: frozenset[str]        # computed_ids that are derivation-kind and terminal
    verdicts: tuple[AuthenticatedVerdict, ...]   # one per eligible id, sorted by id
    non_pass_ids: frozenset[str]        # derived here, after complete authentication

def authenticate_battery_epoch(
    snapshot: Any, registration_ids: Sequence[str], *, repo_root: Path,
    target_epoch: Mapping[str, Any], preregistration_sha256: str,
) -> AuthenticatedBatteryEpoch:
```

in `scripts/issue_calibration_acceptance_generation.py`, beside `_battery_computed_set`. It, in order: (1) authenticates every **named** id that is present, derivation-kind and terminal, sorted, through the seam; (2) `dispositions = _registered_dispositions()` (the pinned registry; its `PrepareRefusal` propagates unchanged); (3) `_battery_computed_set(...)`; (4) authenticates every remaining eligible id, sorted; (5) returns the frozen collection or raises. Named-first matters: `predates_battery_float` (`battery_float.py:481-503`) opens `instrument_evidence.json` for unnamed sessions, and `test_dry_run_never_reads_member_evidence_without_authentic_verdict` (`:2690`) asserts that scan never runs when a named session lacks a record. There is no `continue` after a refusal, no partial collection, no caller-supplied prefiltered list.

Policy, one pure function, also in the issuer module:

```python
def battery_epoch_policy(epoch: AuthenticatedBatteryEpoch, *, acknowledged: frozenset[str]) -> tuple[str, ...]:
    """Omitted non-pass ids (non_pass_ids - acknowledged) and the one-replacement bound, as blocker texts."""
```

returning `computed non-pass session omitted: <id>` per omitted id and `more than one battery-float non-pass window in this epoch: <ids>` when `len(non_pass_ids) > 1`.

Callers, exhaustively: `registration_dry_run` and `_prepare_candidate` call `authenticate_battery_epoch` **once each**, before any `_read_member_evidence` call (`:285`, `:1210`), and pass its result to `battery_epoch_policy` (dry run: `acknowledged = frozenset(session_ids)`; issuer: `acknowledged = frozenset(named_confounded)`). The issuer keeps its exact-set check `:1613-1632` text unchanged, reading `epoch.non_pass_ids` in place of `computed_confounded` and `{v.session_id for v in epoch.verdicts}` in place of `battery_results`. `_dry_run_epoch_bound` is deleted. `report_window` calls the seam only (one window; no set). `derive_record` and `epoch_equivalence_check` call nothing (they refuse Revision 5 first).

The dry run's existing per-consumer differences are presentation and stay: named non-pass → the `valid=0 excluded=battery_<status>` line and blocker (§4.5); the issuer requires the explicit declaration.

### 3.5 Call-site changes at `3e984ecc`

| Site | Change |
|---|---|
| issuer `registration_dry_run` `:230-280` | Delete the primitive calls `:243`, `:250`, `:263`. Before the `for session_id in session_ids` loop, if any named session is Revision 5 and terminal: require the digest (`:237-241` text unchanged), then `epoch = authenticate_battery_epoch(...)` inside `try`; `BatteryVerdictRefusal` → `blockers.append(f"{'session' if e.session_id in session_ids else 'computed session'} {e.session_id}: {DRY_RUN_TEXT[e.code]}")`, set `battery_gate_blocked`, and skip every member read; `PrepareRefusal` → its reason as a blocker. Inside the loop, the battery line is rendered from `epoch`'s verdict for that id. |
| issuer `_dry_run_epoch_bound` `:332-373` and its call `:315-317` | Delete. Replace `:315-317` with `blockers.extend(battery_epoch_policy(epoch, acknowledged=frozenset(session_ids)))` when the gate is not blocked. |
| issuer `_prepare_candidate` `:1573-1612` | Replace with `epoch = authenticate_battery_epoch(...)`; `except BatteryVerdictRefusal as e: raise PrepareRefusal(f"{e}; not issued") from e`. Keep `:1613-1640` with the substitutions in §3.4; the bound check reads `battery_epoch_policy`. |
| issuer derivation notes `:1979-1989` | Serialize from `epoch.verdicts` (`session_id`, `status`, `file_sha256`, `commit`; `battery_confounded_sessions` entries add `slots` as `dataclasses.asdict`). Field names in the artifact unchanged. |
| cadence `report_window` `:78-95` | Replace with `verdict = battery_float.authenticate_committed_verdict(root, session=session, preregistration_sha256=preregistration_sha256)`; `except BatteryVerdictRefusal as e: raise ValueError(str(e)) from e`; `battery_verdict = verdict.status`. |
| `battery_float.verdict_record` `:511-533` | Unchanged; it is the producer. |
| `battery_float.load_committed_verdict` `:543` | Signature tightened to `preregistration_sha256: str`; `:591` loses the `is not None` arm. |

`DRY_RUN_TEXT` maps the four codes to the §4.5 shapes so the branch's existing dry-run assertions stay green: `custody_failure` → `battery custody failure: {detail}`, `record_unauthenticated` → `battery harvest verdict missing or uncommitted ({detail})`, `verdict_mismatch` → `battery harvest verdict cannot be re-established ({detail})`, `registration_digest_required` → `--preregistration and --preregistration-sha256 are required`. A code absent from the table renders as `battery verdict refused ({code}): {message}` and is still a blocker: the default branch fails closed.

### 3.6 The guard (`tests/test_battery_float_consumers.py`)

An AST test over every tracked `*.py` under `joulewise/` and `scripts/` (walk the tree, not a hand-kept list). For each file it parses the source and flags:

1. any `ast.ImportFrom` of `joulewise.battery_float` whose names include a primitive (`load_committed_verdict`, `validate_window`, `compare_verdict`);
2. any `ast.Attribute` whose `attr` is a primitive name and whose value resolves, through the module's `import`/`from … import … as …` aliases, to `joulewise.battery_float` (this catches `battery_float.validate_window`, `_battery_float.validate_window`, and bare references assigned to another name; references, not just calls);
3. any `ast.Name` bound by such an import;
4. any string `ast.Constant` equal to a primitive name outside a docstring position (closes `getattr(mod, "validate_window")`).

**Allowlist, exactly two entries:** `joulewise/battery_float.py::verdict_record` → `validate_window` (the producer), and `joulewise/battery_float.py::authenticate_committed_verdict` → all three. Inside `battery_float.py` the guard additionally asserts, positively, that `authenticate_committed_verdict` contains a call to each of the three names, so the seam cannot be hollowed out without failing the guard.

**Self-test:** the guard's checker function runs over a fixture string containing the deleted `_dry_run_epoch_bound` body from `3e984ecc:358` and must report one violation; over a fixture with an aliased import and an attribute reference it must report two. A guard that cannot fail is not a guard.

Test files may call the primitives directly only in `tests/test_battery_float.py`, `tests/battery_float_fixture.py`, `tests/fixtures/epoch_bootstrap/build.py` and `tests/test_validate_powermetrics_fiducial_derivation_only.py`; the issuer test's direct call at `:2484` migrates to the seam. The residual (`exec`, `eval`, hand-built AST) is review discipline; both consults say so and I agree.

### 3.7 Tests (each must be RED at `3e984ecc` where the defect exists there, and GREEN after)

(i) **Round 1, omission.** Keep `test_dry_run_blocks_one_computed_non_pass_session_omitted` (`:2767`) and the issuer's `test_omission_clean_declaration_and_overlap_refuse` (`:2450`); both now flow through `battery_epoch_policy`.

(ii) **Round 2, swallowed NoRecord.** Keep `:2707` and `:2725`; add the delete-and-re-add route (`build_module.rerecord_verdict`) on an **unnamed** W1: blocker text `path history is not a single adding commit`.

(iii) **Round 3a, missing replay.** The E2 RAW-TAMPER fixture as a test: unnamed W1's `battery_float.pre.ioreg` gets one appended byte; `check W1-prime W2` → exit 5 with `blocker: computed session W1: battery custody failure: d01/pre expected …`; `prepare-candidate` → 3, same custody text, no candidate; restore the bytes byte-exact → the custody blocker clears (exit 0 or the honest next blocker). RED at `3e984ecc` (E2: `check rc 0`).

(iv) **Round 3b, missing compare, both directions.** E2 DISAGREE2 (record `pass`, bytes confounded) → `check` exit 5 with `blocker: computed session W1: battery harvest verdict cannot be re-established (status recorded pass recomputed battery_float_confounded)`, and the assertion that **no** `omitted` blocker appears; E2 DISAGREE (record `evidence_missing`, bytes pass) → the mismatch blocker and again no `omitted` blocker. RED at `3e984ecc` in both (E2: `rc 0` and the wrong blocker respectively).

(v) **Loader digest.** `authenticate_committed_verdict(root, session=s, preregistration_sha256=None)` and `""` and a 63-character string → `registration_digest_required`, no filesystem or git access (patch `_git` to assert not called). `load_committed_verdict(..., preregistration_sha256=None)` → `TypeError` or refusal, never a record.

(vi) **Ordering.** Extend `:2690`: with named W1-prime, W2 clean and unnamed W1 tampered, `_read_member_evidence` is never called, in both the dry run and the issuer (`_select_members`).

(vii) **Seam unit tests** in `tests/test_battery_float.py`, reusing the scratch-git fixture at `:436`: one test per code, `__cause__` is the primitive exception, `str(refusal)` equals the §3.2 text, the result is frozen (`dataclasses.FrozenInstanceError` on assignment; `slots` and `reasons` are tuples), and `status`/`slots` come from the record, not the recomputation (a record whose `reasons` differ from the recomputation still authenticates, since `reasons` are not compared, and the result carries the recorded reasons).

(viii) **Mutation kills**, with the branch's own `importlib`-mutant pattern (`tests/test_battery_float.py:757-766`): (a) delete the `validate_window` call in the seam; (b) delete the `compare_verdict` call; (c) in the collector, wrap the seam call in `except BatteryVerdictRefusal: continue`; (d) in the collector, restrict the loop to named ids; (e) in the dry run, drop the `battery_epoch_policy` call. Each mutant must fail at least one of (i)–(iv). Mutants (a)–(b) must also fail the guard's positive assertion.

(ix) **Cadence and consumers.** `report_window` on a tampered raw file and on a disagreeing record → `ValueError` carrying the §3.2 text; `diagnostic_only` keyed off `verdict.status`; the continuation and equivalence refusals (`test_epoch_continuation`, `test_epoch_equivalence_check`) unchanged and still green.

## 4. K3. What else in BFG-D should be held to this pattern before the final pass

Required in the same fix round (all named above): the loader's optional digest (§2, §3.5 last row); the derivation-notes serializer, which is a fourth reader of verdict objects (`:1979-1989`); and obligations v1.1 §4.5's consumer list, which both deltas (ex-03 F2, ex-04 F2) report still omits `epoch_equivalence_check` and still describes the removed continuation gate. §4.5 is being reissued by this ruling anyway (the dry-run and cadence paragraphs now say "through `authenticate_committed_verdict`"), so R2-7 lands in the same text change. The sweep inventory's stale `UNGATED` labels and its issuer row naming `_dry_run_epoch_bound` (`tests/test_battery_float_sweep.py:28-29, 46-50`) are NIT and are corrected when the function is deleted.

Not required, recorded for the lead: the dry run mirrors only the battery gate, not the issuer's A-7 foreign-row refusal or the "W3 opened despite 12 valid observations" rule. My two clean control fixtures exited `check 0 / prepare 3` on those grounds. That is a property of a count-only desk check on a synthetic fixture, and it is outside this charge, but the runbook's row "`check … 0 | Registration would be admissible`" (`derivation_night_runbook.md:3217`) is broader than what `check` verifies. Consider narrowing that sentence; do not add gates to the dry run for it.

Packet hygiene, one defect: the charge's background sentence "The same deltas cleared the parser … and all other closures" understates its own exhibits, both of which carry R2-7 as an open finding (ex-03 F2 MATERIAL, ex-04 F2 NIT). No effect on K1 or K2; it is why R2-7 is named in this section rather than assumed closed.

## 5. Plain summary for Ed

1. The quick "is the registration ready?" desk check and the real issuing tool disagree: if a window's raw battery-probe files are altered, or its committed verdict file does not match those files, the desk check says "ready" while the issuer refuses. I reproduced both at the reviewed commit. No measurement number is exposed; the risk is a wrong stop/continue decision for W1/W2.
2. Cause: three tools each re-implement the same three-step check, and the third copy skipped two steps. This is the third round with that shape.
3. Cure: one function does the whole check and hands back a read-only result or refuses; one function walks the epoch's windows; a mechanical test forbids anyone else from calling the pieces. Order of the steps is unchanged from the September 25 ruling.
4. Same round: a loophole where the record-loader can be told "skip the registration-digest check", and the stale consumer list in the obligations text.
5. Nothing else in the branch has this shape. Nothing is armed and nothing here touches a window.

## 6. Disagreements and concurrences (silence reads as concurrence)

- With Sol (ex-01): REJECT load-before-replay (§3.3); REJECT treating the recomputed label print as a defect (§3.3). ADOPT the single refusal class, the assessment function shape, and the AST guard over all production files.
- With Astra (ex-02): REJECT six exception subclasses and the seam-level eligibility check (§3.1 item 5, §3.2); ADOPT id-from-session, required digest, frozen-not-dict result, named-first collector order, all-or-refuse collection, both-direction disagreement tests, mutation kills, and reference-level (not call-level) guard resolution.
- With the charge's framing: the "single collector for S" already exists (`_battery_computed_set`); what was missing is the single **authenticating loop** over it (§3.4).
- With the lead: no labeled disposition was presented; the questions were posed neutrally.

## 7. Verdict table

| Q | Verdict | Tier | Where |
|---|---|---|---|
| K1 drift real | AFFIRM, executed (E2) | MATERIAL | §2 |
| K1 anywhere else | AFFIRM "no" for callers; one latent hole (optional digest) | MATERIAL | §2 |
| K2 seam, refusals, order | AFFIRM; order stands (replay → load → compare) | — | §3.1–3.3 |
| K2 collector and callers | AFFIRM: `authenticate_battery_epoch`, called once by dry run and issuer | — | §3.4–3.5 |
| K2 guard and allowlist | AFFIRM: two allowlist entries, alias-resolving, self-tested | — | §3.6 |
| K2 tests | AFFIRM: (i)–(ix), with RED-at-`3e984ecc` requirements | — | §3.7 |
| K3 | loader digest, serializer, §4.5/R2-7 in the same round; nothing else | MATERIAL / NIT | §4 |

Scratch removed after this file was written: `git worktree remove --force /tmp/cg-bfgd`; `rm -rf /tmp/cg-probe`.
