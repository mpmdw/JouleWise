# 21 — Opus contract-lens refuter: CONSUMER-DRIFT-ESC-01

Seat: Opus 5.5 (paired refuter to the Fable cold gate). Worktree `JouleWise-wt-ed17a643-cg-cd-ref` at `05790305`. Code under test: BFG-D `3e984ecc`.

**Contamination disclosure.** Before this task I had read the charge, the five exhibits and the code listed below, and nothing else. The session's system context contains the operator's memory index (one-line summaries). None of those lines concerns this defect. I did not read RUN_STATE, TASK_QUEUE, council logs, run reports, or process traces outside this packet. Exhibit digests match the charge manifest (`shasum -a 256`, all five equal).

**Ref note.** `origin/feat/2026-09-25-bfg-d` is now `7f007c59`, not `3e984ecc`. The only difference is two review-report files under `bfg-d/11-review/`; no code differs (`git diff --stat 3e984ecc 7f007c59`). Everything below is pinned to `3e984ecc`, taken as a `git archive` export at `/tmp/opusref_tree`.

**Terms used below.**
- **Dry run.** `check --session-ids …`, implemented by `registration_dry_run` plus `_dry_run_epoch_bound`. It prints "registration admissible for prepare-candidate: yes/no" and exits 0 or 5.
- **Issuer.** `prepare-candidate`, implemented by `_prepare_candidate`. It exits 3 on refusal and writes no candidate.
- **Parity.** The dry run says "yes" exactly when the issuer would issue. A **false yes** says "yes" where the issuer refuses. A **false no** says "no" where the issuer issues.
- **Computed set.** The sessions whose battery verdict the epoch must account for: named ∪ foreign-row owners ∪ S (obligations §4.4 step 2).

---

## Phase 1 — independent answers

### K1. Is F1 real, and is the drift anywhere else?

**F1 is real. I reproduced it in both directions.** I used the branch's own `BatteryFloatRevisionFiveTests` fixtures (real ledgers, real Git commits, real raw ioreg bytes, with only the disposition registry mocked to `{}` exactly as the branch tests do). The probe is `tests/opusref_probe.py` in the /tmp export. The existing class's 52 tests also passed under the same run: `Ran 56 tests … OK`.

```text
P1 raw tamper, unnamed W1 (W1-d01 pre.ioreg + 1 byte); named W1-prime, W2
P1 dry 0 ['registration admissible for prepare-candidate: yes']
P1 prepare 3 ['REFUSED: battery-float custody failure for W1: d01/pre expected 5003c76c… observed cd3552e1…; restore … ; not issued'] False

P2 forged-pass record: W1's raw bytes are honestly confounded (honest status battery_float_confounded);
   W1's committed record claims status "pass", all slots "pass"; it authenticates (committed with the pin)
P2 dry 0 ['registration admissible for prepare-candidate: yes']
P2 prepare 3 ['REFUSED: battery-float harvest verdict for W1 cannot be re-established from raw bytes (status recorded pass recomputed battery_float_confounded); custody failure; not issued'] False
```

P2 is the direction that matters for the science. The committed record says a confounded window floated, and the dry run believes it, because `_dry_run_epoch_bound` (`issuer:357-367`) reads `record["status"]` straight after `load_committed_verdict`. It never calls `validate_window` or `compare_verdict`. The issuer still refuses, so no bad number can issue. The cost of F1 is therefore a wrong stop/continue decision at the desk, not a corrupted acceptance. That sets its severity: MATERIAL (it misleads the operator), not a science BLOCKER.

**Every caller of the three primitives at 3e984ecc** (`git grep` plus reading each site; production code only):

| Site | `validate_window` | `load_committed_verdict` | `compare_verdict` | Complete? |
|---|---|---|---|---|
| `battery_float.verdict_record` (producer) | `bf:514` | — | — | producer; it is correct that it does not load a record |
| `registration_dry_run`, named loop | `issuer:243` | `issuer:250` | `issuer:263` | yes |
| `_dry_run_epoch_bound`, computed loop | **absent** | `issuer:358` | **absent** | **no (F1)** |
| `_prepare_candidate` | `issuer:1586` | `issuer:1593` | `issuer:1602` | yes |
| `calibration_cadence_report.report_window` | `cad:81` | `cad:85` | `cad:93` | yes |

Test-only callers: `tests/test_battery_float.py` (many), `tests/test_issue_calibration_acceptance_generation.py:2484`, `tests/test_validate_powermetrics_fiducial_derivation_only.py:680`, and `tests/fixtures/epoch_bootstrap/build.py:268` (it calls `verdict_record`). No other production module calls the three primitives. Other `battery_float` importers use only the live probe: `observe`, `require_pass`, `IOREG_BATTERY_ARGV` and `PROBE_TIMEOUT_S` in night_gate, evidence_night, night_agent_install, arm_readiness_evidence_t0, run_night and validate_powermetrics_fiducial. `issue_epoch_continuation` and `epoch_equivalence_check` refuse Revision 5 outright and call no primitive. No production code reads `battery_float_verdicts/*.json` directly; the only non-test hit is a help string at `issuer:2236`.

**Every derivation of the computed set, or of a gate that depends on it:**

1. `_battery_computed_set` (`issuer:1285-1317`), called at `issuer:349` (dry run) and `issuer:1577` (issuer). The inputs differ. The dry run passes the constant `REVISION_FIVE_EPOCH` and the named ids. The issuer passes the registration's own `target_epoch` (`observations[0].identity_epoch`, `issuer:1552`) and the registration ids. The two agree when the registration is Revision 5.
2. **The skip rule is duplicated.** "Skip if absent, not derivation-kind, or not terminal" is copied at `issuer:353-356` and `issuer:1582-1584`.
3. **The Revision-5 trigger is derived twice, differently.** The dry run sets `revision_five_named` if *any* terminal Revision-5 derivation session exists in the ledger (`issuer:205-211`). The issuer checks `target_epoch == REVISION_FIVE_EPOCH` (`issuer:1553`). The dry run's trigger is the broader one, so this is safe.
4. **The A-7 sweep re-derives the foreign component** (`issuer:1723-1738`). It uses the same predicate as `foreign_owners`, minus `computed_confounded`. **The dry run has no A-7 sweep at all.**
5. `_registration_observations` and `refuse_open_registration` run only in the issuer.

**The drift is wider than F1. Three more parity breaks were executed.**

```text
P3 clean epoch (all three windows authentic pass), W1 unnamed; named W1-prime, W2
P3 dry 0 ['registration admissible for prepare-candidate: yes']
P3 prepare 3 ['REFUSED: valid same-epoch observations outside this registration: W1-d01 … W1-d12; not issued (ruling 46 addendum A-7)']

P4 legitimate one-replacement epoch (W1 confounded, declared)
P4 dry ('W1-prime','W2') 5 ['… no', '  blocker: computed non-pass session omitted: W1']
P4 dry ('W1','W1-prime','W2') 5 ['… no', '  blocker: session W1: battery=confounded']
P4 prepare(--battery-confounded-session-id W1) 0 True

P5 pin working-tree bytes differ from HEAD (re-serialised); names W1, W2; via issuer.main(["check", …])
P5 check rc 0 ['ledger: calibration_ledger_head_uncommitted', 'registration admissible for prepare-candidate: yes']
P5 prepare rc 3 ['REFUSED: ledger: calibration_ledger_head_uncommitted']
```

- **P3 (MATERIAL, false yes, not a battery defect).** F1's own reproduction has an unnamed W1 with valid rows. That shape is refused by A-7 even when W1's bytes are intact. The Astra control line `CONTROL restored_raw check=0 admissible=yes` (ex-02) is therefore itself a false yes. Astra did not run prepare on that control. A cure limited to battery parity leaves P3 standing.
- **P4 (MATERIAL, false no).** The dry run has no input corresponding to `--battery-confounded-session-id`. The sanctioned one-replacement registration can therefore never read "admissible", yet the issuer issues it. This matters because the charge makes the dry run the stop/continue decision for W1 and W2: a false no here means capturing a night that is not needed.
- **P5 (MATERIAL, false yes).** When `--session-ids` is non-empty, `check` returns `dry_run_code` and ignores `errors` (`issuer:407-409` and `issuer:477-488`). The dry run then derives the computed set from a snapshot that the issuer refuses (`issuer:1523-1524`). Any ledger refusal reason (`head_uncommitted`, `head_mismatch`, `rollback`, `custody_invalid`) produces the same false yes.
- **Unexecuted, source only (NIT).** `load_committed_verdict` can raise `authentication_io.V2AuthenticationInputError(RuntimeError)` from `ingest_git_authentication_input` (`bf:564`). No consumer catches it, so the result is a traceback. That fails closed, but `check` then exits 1, not 5.

**The one-sentence finding for K1.** The dry run is a second, partial copy of the issuer. Three rounds found three of its missing battery clauses. Executed evidence shows at least three further missing or divergent clauses that do not involve battery at all (A-7, the confounded declaration, ledger refusals). The defect class is "the dry run re-implements the issuer", not "consumers re-implement the battery gate".

### K2. The cure. My position, then attacks on both consults.

**K2.1 — The sole per-window API: agree with the consults, with three amendments.**

```python
# joulewise/battery_float.py
class BatteryVerdictRefusal(RuntimeError):          # ONE concrete class; no subclasses
    code: str      # "request_invalid" | "session_ineligible" | "custody_failure"
                   # | "record_unauthenticated" | "verdict_mismatch"
    session_id: str
    detail: str

@dataclass(frozen=True, slots=True)
class AuthenticatedVerdict:
    session_id: str
    preregistration_sha256: str
    status: str
    slots: tuple[AuthenticatedSlot, ...]   # frozen; reasons as tuple[str, ...]
    file_sha256: str
    commit: str

def authenticate_committed_verdict(
    repo_root: Path | str, *, session: Any, preregistration_sha256: str,
) -> AuthenticatedVerdict
```

- **Amendment A: one class, no subclass family.** This is where I part from Astra. Astra's six subclasses (`BatteryRecordRefusal`, `BatteryCustodyRefusal`, …) re-create round 2's shape exactly: a consumer can write `except BatteryRecordRefusal: continue` and swallow only the missing-record case while still refusing custody. With a single type and a `code` field, a selective swallow has to be written as `if e.code == …`, which the guard can flag (K2.4, rule 5).
- **Amendment B: take the id from `session`, not as a parameter.** This follows Astra; Sol's signature takes both. My check: at `3e984ecc` a mismatched `session_id` and `session` is caught only indirectly, by the slot-binding digests. The parameter is a degree of freedom with no use.
- **Amendment C: normalise `V2AuthenticationInputError` inside the API.** It becomes `record_unauthenticated`, with the cause preserved, so no traceback leaks out as exit 1.

**K2.2 — Order: §4.4 stands.** The order is replay (`validate_window`), then load, then compare, and nothing returns until all three succeed. Sol proposes load first. At 3e984ecc the order changes only which message a window broken in two ways shows. The existing tests pin custody-before-record precedence (`test_m1…`, `test_e8…`), and §4.5 prescribes the dry run's `battery=<status> recorded=absent` line, which needs the replay to have run first. Reordering is an unforced semantic change. Keep §4.4. The recomputed label is a battery state, not a measured value, so printing it does not break blindness.

**K2.3 — One shared assessment, not just one shared collector. This is the substantive amendment to both consults.** Both consults share the *battery* loop only. P3, P4 and P5 show that the dry run drifts on clauses that are not battery clauses. The structural cure is for the dry run to call the issuer's own admission prefix, not to share one more helper:

```python
# scripts/issue_calibration_acceptance_generation.py
@dataclass(frozen=True)
class RegistrationAdmission:
    target_epoch: Mapping[str, str]
    computed_ids: frozenset[str]           # R ∪ F ∪ S, before the skip rule
    eligible_ids: frozenset[str]           # after the skip rule
    verdicts: Mapping[str, AuthenticatedVerdict]   # MappingProxyType over eligible_ids
    non_pass_ids: frozenset[str]
    issues: tuple[str, ...]                # every refusal text the issuer would raise, in issuer order

def assess_registration(snapshot, registration_ids, *, declared_confounded_ids,
                        repo_root, preregistration_sha256) -> RegistrationAdmission
```

It performs, in the issuer's order, every check that does not read a B value:
1. `snapshot.refusal_reasons`;
2. repeated or open sessions;
3. the target epoch;
4. the battery loop through `authenticate_committed_verdict`;
5. the exact confounded-set check;
6. the one-replacement bound;
7. A-7.

`_prepare_candidate` calls it and raises `PrepareRefusal(issues[0])` if `issues` is non-empty. `registration_dry_run` calls it and renders every issue as a blocker. `check` gains `--battery-confounded-session-id`, the same flag with the same meaning. A battery refusal inside the loop becomes an issue and stops the loop, exactly as the issuer stops. Otherwise the dry run and the issuer would stop at different points.

This is the "don't re-implement the issuer" cure. It makes P1, P2, P3, P4 and P5 all impossible by construction. Clauses that do read B values (plateau, screens, corpus size, night count) stay issuer-only, and the dry run's "yes" must then be worded to match: `registration admissible for prepare-candidate (pre-value checks): yes`. Otherwise "yes" still promises more than the dry run checks.

If the gate declines this as scope growth, the minimum acceptable cure is both consults' battery collector **plus** A-7 and `refusal_reasons` in the dry run **plus** the declaration flag, each with an executed parity test. A battery-only cure leaves P3 and P5 as live false yeses.

**K2.4 — The guard. Sol's version is too broad, and both versions miss the producer backdoor.**

Rules, as an AST test over every tracked `.py` under `joulewise/` and `scripts/`:
1. Outside `battery_float.py`, any reference, whether a call, an attribute, an import, an alias, or a **string literal** equal to one of the forbidden names, fails. The forbidden names are `load_committed_verdict`, `validate_window`, `compare_verdict`, `parse`, `CommittedVerdict`, `VERDICT_DIRECTORY` and `verdict_relative_path`. The string-literal ban closes `getattr(battery_float, "validate_window")`, the one hole Sol's flag F1 admits.
2. **The producer backdoor, which neither consult closes.** `verdict_record(session, …)` is public and returns a replayed status with no record authentication. A consumer calling `verdict_record(...)["status"]` is a replay-only gate, the mirror image of F1. Allowlist: exactly one caller, the `battery-verdict` harvest writer in the issuer (`issuer:1450`), plus `tests/fixtures/epoch_bootstrap/build.py`.
3. **Inside `battery_float.py`, allowlist (enclosing function, callee) pairs, not the whole file.** The pairs are `authenticate_committed_verdict → {validate_window, load_committed_verdict, compare_verdict}` and `verdict_record → validate_window`. Sol's "forbid outside battery_float.py" lets any new helper in that module, for example a `quick_status()` that only loads, pass the guard. Astra's rule 2 is correct here.
4. Test files: direct primitive use only in `tests/test_battery_float.py`, `tests/test_validate_powermetrics_fiducial_derivation_only.py` and the fixture builder. The existing `issuer.battery_float.validate_window` call at `test_issue…:2484` either moves or is named explicitly.
5. `except` clauses that catch `BatteryVerdictRefusal`, or a base class of it (`RuntimeError`, `Exception`, `BaseException`, or a bare `except`), may appear only inside `assess_registration`, the cadence `main`, and the dry-run renderer. Each such handler body must re-raise or append to the issues list. It must never be only `continue` or `pass`. This is the mechanical check against "catch the refusal and carry on".
6. `registration_dry_run` and `_prepare_candidate` must each call `assess_registration` exactly once. Neither may call `_battery_computed_set` or `_registered_dispositions`, or read `snapshot.observations`, for battery or A-7 purposes.
7. The guard must fail at `3e984ecc`. It is proved by running it on the pre-cure tree: it must name `issuer:358`, `issuer:243` and the other sites.

**K2.5 — Tests.** Every row below runs through both `check` (via `issuer.main`) and `prepare-candidate`, with **the same assertion on both**: either both refuse on the same session id, or both admit.

| # | Round | Fixture | Expected |
|---|---|---|---|
| T1 | R1 | unnamed W1 authentically confounded; also evidence-missing; also zero valid rows | both refuse "omitted" without the declaration; both admit with it (this also closes P4) |
| T2 | R2 | unnamed W1: file deleted / modified / re-added / wrong registration / separate pin commit / malformed JSON bytes | both refuse `record_unauthenticated`, W1 never vanishes |
| T3 | R3a (F1) | unnamed W1: pre and post raw bytes altered, and deleted | both refuse `custody_failure`; restoring the bytes clears it |
| T4 | R3b (P2) | unnamed W1: forged-pass record over confounded raw bytes, **and** the reverse (forged non-pass over a clean window) | both refuse `verdict_mismatch` |
| T5 | P3 | clean epoch, W1 unnamed with valid rows | both refuse A-7 |
| T6 | P5 | pin working tree ≠ HEAD | both refuse `ledger: …` |
| T7 | precedence | two authentic non-pass sessions plus one custody failure | both refuse custody, not the epoch stop |
| T8 | order | any T2–T4 failure | `_read_member_evidence` and the pre-A-R5b evidence scan are never called |
| T9 | immutability | mutate `AuthenticatedVerdict.status` or `.slots[0].reasons` | `FrozenInstanceError` or `TypeError` |
| T10 | cadence | T2–T4 applied to the window being reported | refuses; only an authentic non-pass sets `diagnostic_only` |

A mutation sweep must kill each of these seams: delete replay; delete compare; delete load; swallow the refusal; filter the computed set to named ids; drop A-7 from the assessment; drop the declaration input. Each mutation must turn at least one of T1–T6 red. **T1–T6 are parameterised by "affected session is named / unnamed".** The three rounds all escaped because custody tests covered only named sessions.

### K3. Hold anything else to this pattern? Summary for Ed.

1. **Yes, the dry run as a whole** (K2.3). It is the only second implementation of the issuer's admission logic. Every round and every P-probe is the same root cause.
2. **The cadence report:** move it to the sole API. It already does all three steps, but its eligibility check is weaker. It accepts any terminal session and never checks derivation kind (`cad:76`). The API's `session_ineligible` fixes that as a side effect.
3. **The continuation and equivalence tools:** no change. They refuse Revision 5 outright. The guard (rule 1) is what stops them silently re-acquiring a partial gate later.
4. **Stale spec text (NIT).** The code no longer matches obligations §4.3 in two places. §4.3 says `git log --no-renames`; the code uses `--full-history` (`bf:573-574`). §4.3 says the pin-commit binding is "not checked"; the code checks it (`bf:607-619`). The API's final text must be written from the code as ruled after the ESC rulings, not by citing §4.3.

**For Ed (≤5 lines):**
> The desk check that tells us whether W1 and W2 are "ready" was a hand-written second copy of the issuer, and each review found another clause it had dropped. I confirmed the latest one and found three more: an unnamed window, a spare-window rule, and a stale ledger.
> None of these can let a bad number through, because the issuer itself still refuses; the harm is a wrong "stop" or "keep capturing" call.
> The cure: the desk check calls the issuer's own pre-measurement checks instead of copying them, and a code scan fails the build if anyone copies them again.

---

## Phase 2 — refutation of the Fable ruling

Ruling read at 00:58 PDT from `/Users/edr/code/JouleWise-wt-ed17a643-cg-cd/…/20-coldgate-fable-consumer-drift-ruling.md` (30 231 bytes, mtime 00:56:15, size unchanged after a 30 s settle). Each item names a ruling section. Verdicts are AGREE, BLOCKER, MATERIAL or NIT. The evidence is the Phase 1 probes P1–P5 unless stated otherwise.

**Net.** The ruling's core is sound and I concur with it: the seam, the single refusal class, the order, the all-or-refuse collector, the required digest, and the guard with a self-test. Its E2 matches my P1 and P2 independently, down to the same expected digest `5003c76c…`. I have **no BLOCKER**. I have **four MATERIAL** findings. All four come from one claim, "Anywhere else: No" (§2), which my executed P3, P4 and P5 falsify. The ruling's own test (iii) then locks one of those false yeses in.

| # | Ruling item | Verdict | Evidence and required change |
|---|---|---|---|
| R1 | §0 disclosures, charter digest, commit pin | AGREE | Same `7f007c59` observation as mine; digests match. |
| R2 | §0 "Ruled … about 01:00–01:35 PDT" | NIT | The file's mtime is **00:56:15 PDT** and my clock read 00:58:34 when I read it. The stated time is after the file was written. Correct it to the actual time. |
| R3 | §0 write-scope deviation (a `git worktree add` registered in the shared `.git/worktrees`) | NIT / AGREE | Disclosed, and verified removed: `git worktree list` shows no `/tmp` entries, and `/tmp/cg-bfgd` and `/tmp/cg-probe` are absent. A `git archive` export would have avoided writing shared Git metadata. Record this in the charter as the preferred form. |
| R4 | §1 E1 caller inventory | AGREE | It is identical to my table. The ruling's check for `getattr`/`importlib` also covers a hole I only closed by a rule. |
| R5 | §1 E2 DISAGREE (a non-pass record over passing bytes gives the wrong blocker, "omitted") | AGREE, and it adds to Phase 1 | I did not run this direction. It is a real third costume: the operator gets an exclusion-shaped cure where the truth is a custody refusal. My T4 reverse arm covers it. |
| R6 | §2 K1 "Real", tier MATERIAL | AGREE | Same tier and the same reasoning: the issuer refuses, and the harm is the desk decision. |
| R7 | §2 K1 "**Anywhere else. No.**" | **MATERIAL** | This is true for *primitive callers*. It is false for the defect class the charge names: a consumer that drifts from `_prepare_candidate`. Executed at `3e984ecc`: **P5**: with an uncommitted pin, `check` exits 0 with "admissible: yes" and prints `ledger: calibration_ledger_head_uncommitted` in the same output, while `prepare` exits 3 with `REFUSED: ledger: calibration_ledger_head_uncommitted`. The cause is that `check` returns `dry_run_code` and ignores `errors` (`issuer:408`, `issuer:488`). That is the battery collector running on a snapshot the issuer refuses. It sits inside this charge's own K1 words ("every place that derives the computed session set S"). **Cure, one line and in scope:** `authenticate_battery_epoch` raises (or the dry run blocks) when `snapshot.refusal_reasons` is non-empty. Add a test T6 that is RED at `3e984ecc`. |
| R8 | §3.1 seam, rules 1–5 | AGREE | Id from session, required digest, result built from the record, not a dict. Rule 5 (no eligibility check in the seam) is acceptable given the `night_gate` import-surface constraint the ruling cites. |
| R9 | §3.2 one class, four codes; `; not issued` suffix keeps the issuer's strings byte-identical | AGREE | This matches my Amendment A. The single class is also what makes a selective swallow visible. |
| R10 | §3.3 order stands (replay → load → compare) | AGREE | Same conclusion and reasons as my K2.2. |
| R11 | §3.4 "The drift was never in deriving C" | MATERIAL (same root as R7) | P5 shows C derived from a refused snapshot. In addition, the ruling's `authenticate_battery_epoch` takes `target_epoch`, but §3.5 never says what the dry run passes. Today the dry run hard-codes `REVISION_FIVE_EPOCH` (`issuer:349`) and the issuer passes the registration's own epoch (`issuer:1552`). **Required:** state that the dry run derives `target_epoch` exactly as the issuer does (from the named sessions' rows, unanimous, else a blocker), so the two consumers cannot pass different epochs. |
| R12 | §3.4 named-first order and the all-or-refuse collection | AGREE | This preserves `test_dry_run_never_reads_member_evidence_without_authentic_verdict`. It is a correct improvement on my K2.3 sketch, which ordered the checks by the issuer's sequence without naming this constraint. |
| R13 | §3.4 policy: dry run `acknowledged = frozenset(session_ids)`, and "named non-pass → blocker … stay[s]" | **MATERIAL** | This keeps **P4**, an executed false no. In the sanctioned one-replacement epoch (A-R5b), the dry run blocks when W1 is unnamed ("omitted") and also when it is named ("battery=confounded"). No `check` input reads "admissible", while `prepare --battery-confounded-session-id W1` exits 0 and writes the candidate. The runbook row `derivation_night_runbook.md:3217` makes `check` exit 0 the signal to "Proceed to §4.2". On the replacement route that signal can never be given. **Required:** `check` accepts `--battery-confounded-session-id` (same name, same exact-set check via `battery_epoch_policy(acknowledged=declared)`). A named non-pass session stays a blocker, as today, because the issuer refuses "session named both" (`issuer:1519-1520`). Add a parity test: the P4 fixture with the declaration gives check 0 and prepare 0. |
| R14 | §3.5 call-site table | AGREE | The `DRY_RUN_TEXT` default branch fails closed. The `'session'` / `'computed session'` prefix keeps the existing unnamed-session assertions (`test_…:2718`, `:2737`) byte-identical. |
| R15 | §3.5 `load_committed_verdict` narrowed to `preregistration_sha256: str` | AGREE | Belt and braces, given that the guard also forbids direct calls. |
| R16 | §3.6 guard: primitives are the three names; allowlist is two entries | **MATERIAL** | The **producer backdoor** stays open. `battery_float.verdict_record(session, …)` is public and returns `{"status": …}` computed from `validate_window` alone. A consumer that does `verdict_record(...)["status"]` has a replay-only gate with no committed-record authentication, which is the mirror image of F1. The guard as written does not flag it, because the consumer never names a primitive. Today's production callers are exactly one, `_battery_verdict` (`issuer:1450`), plus the fixture builder `tests/fixtures/epoch_bootstrap/build.py:268`. **Required:** add `verdict_record` to the guarded names with exactly those two callers allowlisted. The same reasoning as the ruling's own optional-digest item (§2, rated MATERIAL "not yet exploited … invites the next drift") applies, so the tier is the same. NIT in the same row: also guard `battery_float.parse`, which can re-derive a slot verdict from custody bytes. No consumer calls it today; the live-probe sites use `observe` and `require_pass`, which stay unguarded. |
| R17 | §3.6 self-test ("a guard that cannot fail is not a guard") | AGREE | This is better than my rule 7. |
| R18 | §3.7 (iii) "restore the bytes byte-exact → the custody blocker clears (**exit 0 or the honest next blocker**)" | **MATERIAL** | In the named fixture (W1, W1-prime and W2 with valid rows; `check W1-prime W2`) the restored state **is my P3**: `check` exits 0 "admissible: yes" and `prepare` exits 3 with `REFUSED: valid same-epoch observations outside this registration: W1-d01 … W1-d12; not issued (ruling 46 addendum A-7)`. The ruling's own §4 records the same (its "two clean control fixtures exited `check 0 / prepare 3`"). As written, (iii) passes on a false yes and encodes it as the regression baseline. **Required, either one:** (a) the restore arm asserts **parity**, meaning check and prepare agree, which forces A-7 into the shared collector (the collector already computes the foreign-owner set F; A-7 is F's valid undisposed rows minus the acknowledged non-pass ids, one more frozen field); or (b) the fixture's unnamed W1 carries zero valid rows, so A-7 cannot fire, and the ruling separately takes up R19. Option (a) is the structural one. |
| R19 | §4 "do not add gates to the dry run for [A-7 / W3]"; "consider narrowing that sentence" | **MATERIAL** (disagree) | The dry-run promise that the three rounds enforced is the parity sentence of cold ruling BFG-D-PARSER-ESC-01 §5.2: "the dry run never says 'admissible' where `prepare-candidate` refuses" (quoted at `issuer:336-340`). This ruling deletes the function that carries that docstring and does not say whether the promise survives. P3 is a false yes in **exactly F1's fixture shape**, and `runbook:3217` turns exit 0 into "Proceed". The ruling calls this "a property of a synthetic fixture", but W1 plus a replacement with valid rows is the real A-R5b route, not an artefact of the fixture. **Required:** the ruling must choose, as final text, one of two options. (a) Mirror A-7 in the shared assessment; the cost is one derived field plus one blocker line. (b) Formally narrow the promise: the output line becomes `registration admissible for prepare-candidate (battery gate only): yes`, and runbook:3217 changes in the same PR. A "consider" leaves the fourth-round drift route open by default. I recommend (a), because the collector already holds F. |
| R20 | §3.7 (i), (ii), (iv)–(vii), (ix) | AGREE | (iv) with its "no `omitted` blocker" assertion is the right discriminator for R5. |
| R21 | §3.7 (viii) mutation kills (a)–(e) | NIT | Add (f): in `registration_dry_run`, replace the `BatteryVerdictRefusal` handler body with `pass`. The five listed mutants all sit in the seam, the collector or the policy. The handler that turns a refusal into a blocker is the last place a swallow can happen, and it is exactly round 2's shape. Tests (iii) and (iv) would kill it, but name it so the kill is recorded. |
| R22 | §4 K3: derivation-notes serializer, R2-7 in the same round, sweep inventory NIT, packet-hygiene note | AGREE | The serializer is a real fourth reader; good catch. |
| R23 | §5 Ed summary, item 5 "Nothing else in the branch has this shape" | NIT, dependent on R7 and R19 | This is contradicted by P3, P4 and P5 unless R19(b) is chosen. The five items also run well past five *lines*; the charge says "at most 5 lines". |
| R24 | §6 concurrences and rejections of Sol and Astra | AGREE | These match my Phase 1 on every overlapping point: one class, order stands, id from session, frozen result, reference-level guard. |

**What the ruling must change before it is final (all MATERIAL, none BLOCKER):**
1. **R7/R11.** The collector refuses on `snapshot.refusal_reasons`. The dry run derives `target_epoch` as the issuer does. Add T6 (P5).
2. **R13.** `check` accepts `--battery-confounded-session-id`. Add the P4 parity test.
3. **R16.** Guard `verdict_record`, with two allowlisted callers.
4. **R18/R19.** Either mirror A-7 in the shared assessment and assert check/prepare parity in (iii), or formally narrow the "admissible" line and runbook:3217. "Consider" is not final text.

**Scratch.** The /tmp probes used for Phase 1 are removed at the end of this session (`/tmp/opusref_tree`, `/tmp/opusref_issuer.py`, `/tmp/opusref_bf.py`, `/tmp/opusref_test.py`).
