```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed two unnamed-session false-admissibility paths; recommend one authenticated-verdict boundary plus an all-or-refuse computed-set collector and enforced consumer architecture.",
  "workspace": {
    "base_requested": "3e984ecc",
    "base_mode": "exact",
    "head_start": "3e984ecc3b598506c12d652e391b85c6c3c22dd8",
    "head_end": "3e984ecc3b598506c12d652e391b85c6c3c22dd8",
    "upstream_end": "7f007c597535468bf5f05136fd42c15df632fb75",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "A", "action": "start_now", "work": "Lead-owned implementation of the shared authenticated-verdict boundary"},
      {"row": "B", "action": "wait_for", "wait_for": "A", "work": "Shared computed-set authentication and policy migration"},
      {"row": "C", "action": "wait_for", "wait_for": "A and B", "work": "Consumer architecture and adversarial regression gates"},
      {"row": "D", "action": "do_not_start", "work": "Accept this baseline as fixing dry-run parity"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git grep -n -E '(load_committed_verdict|validate_window|compare_verdict)\\(' 3e984ecc -- '*.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "3e984ecc:tests/test_validate_powermetrics_fiducial_derivation_only.py:680:        verdict = battery_float.validate_window(session)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "battery_float\\.validate_window\\(session\\)"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/bfg_consumer_probe_3e984ecc.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CONTROL clean check=0 prepare=0",
          "REPRO raw_tamper check=0 admissible=yes prepare=3 reason=custody_failure_W1 output_absent=yes",
          "CONTROL restored_raw check=0 admissible=yes",
          "REPRO record_disagreement check=0 admissible=yes prepare=3 reason=verdict_mismatch_W1 output_absent=yes",
          "PROBE COMPLETE; fixtures synthetic and confined to /tmp"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PROBE COMPLETE; fixtures synthetic and confined to /tmp"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B /tmp/bfg_call_inventory_3e984ecc.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["AST direct-call inventory complete"]
      },
      "expected": {"exit_code": 0, "tail_regex": "AST direct-call inventory complete"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse origin/feat/2026-09-25-bfg-d",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "3e984ecc3b598506c12d652e391b85c6c3c22dd8",
          "7f007c597535468bf5f05136fd42c15df632fb75"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "7f007c597535468bf5f05136fd42c15df632fb75"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "At the requested baseline, check admits an unnamed computed session despite raw custody failure or record/replay disagreement.",
      "needs": "Implement and independently verify the structural cure before accepting the dry-run gate."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The local origin/feat/2026-09-25-bfg-d reference differs from the requested commit. Inspection and reproduction remained pinned to clean detached HEAD 3e984ecc.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| A — Authenticated window API | start_now | Lead assigns implementation | `joulewise/battery_float.py` |
| B — Complete-set collector and consumer migration | wait_for | A’s API | Issuer, dry run, cadence |
| C — Architecture and defect tests | wait_for | A/B implementation | Consumer tests and canonical suite |
| D — Accept baseline as repaired | do_not_start | C passes and lead reviews | Registration stop/continue decision |

**A — A wrapper is necessary, but insufficient.**

The current selector is already shared. The remaining freedom is that each caller decides which selected sessions to authenticate, which authentication steps to perform, and whether failures disappear. Remove all three choices.

Add this sole consumption API to `joulewise/battery_float.py`:

```python
def authenticate_committed_verdict(
    repo_root: Path | str,
    *,
    session: CalibrationBracketSession,
    preregistration_sha256: str,
) -> AuthenticatedVerdict:
    ...
```

Derive the session ID from `session`; do not accept an independently supplied ID. Require a valid, nonoptional registration digest at runtime. Reject nonterminal, nonderivation, or empty sessions before returning any verdict.

The function must perform **all three existing operations**, including `compare_verdict(...) is None`, before constructing its result. Preserve the existing issuer’s replay-before-load order during this extraction: obligations §4.4 explicitly specifies that order. This preserves refusal precedence and avoids introducing a separate semantic change merely to centralize the boundary.

Use a frozen, slotted result containing:

- Session ID and registration digest.
- Recorded status.
- Verdict file SHA-256 and adding commit.
- Immutable slot records, with tuples for reasons and other collections.
- Any retained complete record as immutable bytes, rather than a mutable dictionary.

A frozen dataclass containing the current `CommittedVerdict(dict)` would **not** be immutable. Do not expose either that dictionary or mutable nested slots. Preserve the existing comparison field set; expanding comparison semantics is a separate decision.

Return authenticated non-pass verdicts normally. **Authentication failure is an exception; authenticated non-pass is a verdict.** Only the latter can participate in exclusions or replacement counts.

Use one exception family rooted in `BatteryVerdictRefusal(RuntimeError)`, with stable `code`, `session_id`, and `detail` fields. Proposed exact messages:

| Type / code | Message |
|---|---|
| `BatteryRegistrationRefusal` / `registration_digest_required` | `battery-float registration digest missing or invalid for {id}` |
| `BatterySessionRefusal` / `session_ineligible` | `battery-float session ineligible for {id}: {reason}` |
| `BatteryRecordRefusal` / `record_unauthenticated` | `battery-float harvest verdict missing or uncommitted for {id}: {reason}` |
| `BatteryCustodyRefusal` / `custody_failure` | `battery-float custody failure for {id}: {detail}; restore the custody bytes byte-exact from the harvest archive` |
| `BatteryReplayRefusal` / `verdict_mismatch` | `battery-float harvest verdict for {id} cannot be re-established from raw bytes ({difference}); custody failure` |
| `BatteryInputRefusal` / `authentication_input_failure` | `battery-float authentication input failure for {id}: {reason}` |

Wrap `NoRecord`, `CustodyFailure`, and the authentication layer’s `V2AuthenticationInputError` explicitly, preserving exception causes. Normalize malformed record shapes to an authentication refusal at the loader boundary; do not blanket-catch programmer errors.

The issuer adds its existing `; not issued` presentation. Dry run adds a blocker and exits 5. Cadence translates the shared refusal into its CLI error. None converts a refusal into a non-pass status.

**B — Make complete-set authentication a second boundary.**

Keep one implementation of the existing selection rule, currently at [issuer:1285](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:1285):

- `R`: registration IDs.
- `F`: owners of undisposed, valid target-epoch observations outside `R`.
- `S`: terminal derivation sessions owning a finalized target-epoch row, with the current disposition and authenticated pre-A-R5b exemptions.
- Computed IDs: `C = R ∪ F ∪ S`.

Preserve the distinction between `S` and the full computed set `C`. In particular, exemptions inside `S` must not erase an ID independently contributed by `R` or `F`.

Introduce this shared issuer/dry-run collector:

```python
def _authenticate_battery_computed_set(
    snapshot: CalibrationLedgerSnapshot,
    registration_ids: frozenset[str],
    *,
    repo_root: Path,
    target_epoch: Mapping[str, str],
    preregistration_sha256: str,
) -> AuthenticatedBatteryEpoch:
    ...
```

It owns the pinned disposition-registry load, calls the selector once, applies the existing terminal/derivation eligibility rule once, and authenticates every required session through `authenticate_committed_verdict`.

It returns **one complete immutable collection or raises**. No partial dictionary, no `continue` after an authentication failure, no caller-provided prefiltered session list. Record computed IDs and the eligible IDs separately so the contract’s existing skip rule is explicit and testable.

Authenticate named eligible sessions first, then derive/authenticate the remainder. This preserves the existing early refusal before the pre-A-R5b evidence scan when a named session lacks an authentic record. Reuse those authenticated results within the invocation; do not replay named sessions twice.

The collection derives `non_pass_ids` internally, after complete authentication. Move shared omission and replacement-bound policy into one pure function accepting this collection:

```python
def _battery_epoch_issues(
    epoch: AuthenticatedBatteryEpoch,
    *,
    acknowledged_nonpass_ids: frozenset[str],
) -> tuple[BatteryPolicyIssue, ...]:
    ...
```

The issuer supplies `--battery-confounded-session-id`; dry run supplies the non-pass sessions included in its named set. Preserve their existing presentation differences: a named non-pass remains a dry-run blocker, while the issuer requires explicit exclusion declarations. Both use the same authenticated non-pass set and one-replacement bound.

This is battery-gate parity, not a claim that a one-window desk check satisfies every final issuance requirement.

**Exact migration sites at `3e984ecc`:**

| Site | Change |
|---|---|
| [issuer:243](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:243), `registration_dry_run` | Remove its local replay/load/compare sequence. Obtain the complete authenticated collection before named-session member classification. Render battery lines from its results. |
| [issuer:333](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:333), `_dry_run_epoch_bound` | Remove snapshot/registry/record I/O. Make it a renderer of shared policy issues, or delete it. It must consume the already authenticated collection. |
| [issuer:1573](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:1573), `_prepare_candidate` | Replace selection and authentication loop with the same collector. Use the shared non-pass policy. |
| [issuer:1979](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_calibration_acceptance_generation.py:1979), derivation notes | Serialize immutable authenticated results while preserving artifact fields. |
| [cadence:78](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/calibration_cadence_report.py:78), `report_window` | Replace local replay/load/compare with the window API. Its scope remains the requested window. |

The current dry run reads named-session member evidence **before** checking unnamed computed sessions. Authenticate the complete required set before that classification work. Fixing only line 358 would leave this ordering exposure.

**C — Enforce the architecture and test the actual failure dimensions.**

Add an AST architecture test over all tracked production Python files, not just a hand-maintained consumer list:

1. Outside `battery_float.py`, forbid imports, references, or calls to the three primitives. Resolve import aliases and reject attribute references, so assigning a primitive to another name also fails.
2. Inside `battery_float.py`, allow primitive use only in `authenticate_committed_verdict`, plus `verdict_record → validate_window` for production of the first record.
3. Allow direct primitive testing only in explicitly named test files.
4. Restrict verdict-file reads and construction of authenticated result objects to their owning module.
5. Enforce issuer/dry-run use of the complete-set collector; `_dry_run_epoch_bound` must have no ledger, filesystem, selector, or primitive dependency.

An AST rule proves the permitted dependency structure, not arbitrary Python behavior. Pair it with integration and mutation tests. Otherwise a caller can simply omit the shared API entirely and still pass a “no direct primitive calls” check.

Required test matrix:

| Defect | Fixture and assertion |
|---|---|
| Round 1: omitted non-pass | Unnamed W1 is authentically confounded or evidence-missing; named replacement/W2 are clean. Dry run refuses omission; issuer refuses without the matching exclusion declaration. Include W1 with only ordinary-invalid rows. |
| Round 2: swallowed `NoRecord` | Unnamed W1 has absent/uncommitted/deleted/modified/re-added verdict, wrong registration digest, or separate verdict/pin commits. Every path refuses; W1 never vanishes from the computed set. |
| Round 3: missing replay | Alter or delete unnamed W1’s pre/post raw bytes or ledger-bound evidence. Dry run exits 5, issuer exits 3, no candidate appears. Restore byte-exact bytes and show the custody refusal clears. |
| Round 3: missing comparison | Commit a W1 record with a wrong compared field while leaving authentic raw bytes intact. Both paths refuse disagreement. Include disagreement in both status directions. |
| Precedence | Two authenticated non-pass sessions plus a custody failure: authentication refusal occurs before replacement counting or exclusions. |
| Selection | Exercise all `R/F/S` contributions, registry exemption, authentic pre-A-R5b exemption, named override, aborted sessions, and contract-prescribed skips. Assert authenticated-result IDs equal the required eligible set. |
| Ordering | On failure in any computed session, member-value/classification readers are never called. Nonterminal named sessions produce counts/refusal without replay. |
| Immutability | Attempts to mutate status, slots, reasons, or provenance cannot alter the authenticated result. |
| Consumer coverage | Cadence refuses every authentication failure and marks only authenticated non-pass as diagnostic-only; continuation still refuses Revision 5 outright. |

Mutation tests must kill: removing replay, removing comparison, swallowing a refusal, filtering to named sessions, and deleting omission/bound checks. Vary both the affected session and whether it is named; the current tests overconcentrate custody coverage on named sessions.

**Complete primitive-caller inventory.**

The executed commit-pinned grep and AST inventory agree:

| Production caller | `validate_window` | `load_committed_verdict` | `compare_verdict` |
|---|---:|---:|---:|
| `battery_float.verdict_record` | `joulewise/battery_float.py:514` | — | — |
| `registration_dry_run` | issuer:243 | issuer:250 | issuer:263 |
| `_dry_run_epoch_bound` | **absent** | issuer:358 | **absent** |
| `_prepare_candidate` | issuer:1586 | issuer:1593 | issuer:1602 |
| `calibration_cadence_report.report_window` | cadence:81 | cadence:85 | cadence:93 |

Every direct test call is:

- `tests/test_battery_float.py`:
  - `validate_window`: 233, 259, 267, 272, 277, 282, 331, 345, 354, 358, 363, 372, 376, 381, 391, 394, 399, 468, 543, 635, 641.
  - `load_committed_verdict`: 441.
  - `compare_verdict`: 468, 544, 547, 549, 552.
- `tests/test_issue_calibration_acceptance_generation.py:2484`: `validate_window`.
- `tests/test_validate_powermetrics_fiducial_derivation_only.py:680`: `validate_window`.

The named dry run, issuer, and cadence currently perform all three operations, but share the same future drift exposure through duplicated orchestration. The harvest writer is necessarily different: it creates the first record through `verdict_record`, so cannot require an existing committed verdict.

[Continuation:81](/Users/edr/code/JouleWise-wt-ed17a643-bfgd-astra/scripts/issue_epoch_continuation.py:81) now refuses Revision-5 sessions before member reads. It has no primitive calls at this commit. Do not accidentally reopen that branch while migrating consumers.

**Executed evidence and limits.**

The [reproduction script](/tmp/bfg_consumer_probe_3e984ecc.py) passed the three existing omission/missing-record/wrong-registration regressions, then independently reproduced:

```text
CONTROL clean check=0 prepare=0
REPRO raw_tamper check=0 admissible=yes prepare=3 reason=custody_failure_W1 output_absent=yes
CONTROL restored_raw check=0 admissible=yes
REPRO record_disagreement check=0 admissible=yes prepare=3 reason=verdict_mismatch_W1 output_absent=yes
```

Fixtures and Git commits were confined to `/tmp`; the probe mocked machine identity and the disposition registry, while exercising actual fixture ledger/record authentication and raw replay. This is synthetic regression evidence. The [AST inventory script](/tmp/bfg_call_inventory_3e984ecc.py) inspects source directly from the requested commit.

No repository files changed. No implementation prototype or canonical suite was run; this was a read-only design consult.

## Critical path

A defines the only authenticated window result. B makes successful authentication of the complete required set a prerequisite for consumer policy. C verifies both boundaries and kills the three historical defect mutations. Lead review and the canonical suite follow implementation before D can be reconsidered.