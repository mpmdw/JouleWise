```json
{"schema":"claude-codex-report/v1","genre":"root_cause","status":"findings","completion":"complete","summary":"Evidence render dispatch fails.","workspace":{"base_requested":"010ff2e0","base_mode":"exact","head_start":"010ff2e0a558756faffa7562dd7709062d5b1666","head_end":"010ff2e0a558756faffa7562dd7709062d5b1666","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"cause":"confirmed","remediation":"proposed"},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/evidence-arm-consult.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["FIXTURE COMPLETE; no launchctl, measurement or courier execution"]},"expected":{"exit_code":0,"tail_regex":"FIXTURE COMPLETE"}}],"flags":[]}
```

## Causal chain

**1. P1 — blocks the arm; confirmed by execution.** `joulewise/night_agent_install.py:1140` chooses reservation inspection from the existence/content of the calibration **source**, instead of the selected wrapper’s payload kind. `scripts/run_night.py:604` consequently executes the evidence wrapper with calibration inspection switches.

Before publication, evidence verification cannot open its sealed published plan. After publication, verification succeeds but produces no NUL-separated reservation argv; `run_night.py:608` rejects it. Publishing earlier therefore cannot repair this defect.

V1 executed the actual shell installer against a `/tmp` measurement fixture. Relevant output:

```text
STAGED actual shell render rc=1: CalledProcessError; no plists/night records
STAGED verify/argv invocation rc=2: EVIDENCE_REFUSED missing night_plan.json
PUBLISHED actual shell render rc=1: input_digests: chain did not describe reservation arguments
```

**2. P2 — separate arm-readiness blocker in the handback; read-only finding.** `docs/process/NIGHT_HANDBACK.md:180`, `:490`, `:529`, and `:545` still prescribe the prior derivation night, calibration ledger/equivalence checks, and its uninstall plan. The courier reads this document (`scripts/run_night.py:1171`; `docs/process/NIGHT_COURIER_PROMPT.md:7`). This does not crash installation or collection, but violates the document’s own before-every-night rewrite requirement at `:4` and supplies incorrect post-night instructions. Rewrite its Purpose/Where/Next sections for the evidence night before arming; retain the PROVISIONAL and no-block-two limits.

**3. P3 — cosmetic failure attribution; read-only finding.** `scripts/run_night.py:3476` initializes the supervisor receipt as calibration. A timeout before evidence dispatch can retain calibration fields and receive `calibration_ledger_custody_timeout` at `:3520`. Installation still correctly refuses. A separate diagnostic improvement could represent “payload kind undetermined” until dispatch; this is not another happy-path arm blocker.

**Q2: remaining path audit.** The requested step4, step5, helper and dry-check records were inspected through local Git objects at `86a1af6e`, without accessing another worktree.

| Call / assumption | Finding, severity, minimal action |
|---|---|
| `retry_allowed`, publication, candidate checks | V1: initial empty-history notice accepted; `os.replace` preserved bytes; staged and published `--publication-safe` checks passed. `joulewise/arm_retry.py:116` does not demand a calibration session. No fix. |
| Ledger exports and pins | `night_agent_install.py:759` and `:869` read `CALIBRATION_LEDGER`/`LEDGER_HEAD_PIN` only in calibration bindings/validation. Evidence dispatch at `:800` and `run_night.py:3580` bypasses them. V1 confirmed the direct calibration helper refuses this wrapper, while evidence bindings pass. No evidence ledger or fabricated pin should be added. |
| Probe worker and environment | V1: real `_evidence_probe_worker` at `run_night.py:3530` passed using the published, resolved path. `_chain_environment:574` removes inherited inspection switches; evidence worker deliberately restores only verify-only. Its inherited `CUSTODY_BUDGET_S` is unused by the evidence executor: cosmetic, no fix required. |
| Receipt kind / budget arithmetic | Evidence validation at `night_agent_install.py:925` rejects calibration receipt kinds and custody fields. It never reaches calibration’s `elapsed × 3 × 1.5` check at `:843`. Supervisor strips calibration fields after evidence dispatch at `run_night.py:3511`. V1/V2 passed. No fix. |
| Real install / step5 | V1 passed `validate_install`, receipt validation, `Prepared.admit(require_published=True)` at `:587`, and production plist rendering at `:608`. Calendars, published argv, interpreter, WorkingDirectory and RunAtLoad matched staged rendering. No further calibration assumption found. |
| Night driver → chain → courier | V1 executed the real driver and wrapper with deliberately corrupted manifest bytes, forcing refusal before collection. Output: `REAL driver -> refusing wrapper -> mocked courier: rc=5 chain_exit=2 gate=GO refusal preserved`. `GO` describes gate admission; exit/refusal/evidence outcome describe payload failure. Courier delivery was mocked. |
| Courier/result fields | `run_night.py:1570` retains null calibration fields; `_calibration_refusal:624` returns None when absent. Cosmetic compatibility fields, not required evidence inputs. Evidence inventory `:1001`, cleanup `:1296`, and prompt `:1190` support evidence artifacts. No schema change needed; repair the stale handback above. |
| Pack fields | Evidence is v2 DIAGNOSTIC_NO_PACK, with no serialized pack fields. Candidate checks enforce this; `run_night.py:3010` enters pack handling only for TRANSACTION_PACK. V1 exercised the packless path. No fix. |
| Uninstall | Read-only: `night_agent_install.py:532`, `:1199` perform generic label teardown without calibration bindings, ledger reads or receipt-budget validation. No evidence-specific fix. Actual launchctl cleanup remains unexecuted. |

## Remediation

**Q1: adopt payload-based static inspection, with two qualifications.**

For an evidence wrapper, authenticate its sidecar, call `quiet_predicate_campaign.verify_manifest`, validate the sealed `EVIDENCE_PLAN_PATH` against the content-derived future published path, and report digests of the **actual supplied plan bytes**, wrapper and manifest. Do not execute the chain. `verify_manifest` already accepts staging: V1 printed `STAGED verify_manifest=PASS published_plan_absent=True`.

This is static authentication, not literally hashing alone: manifest verification also performs read-only Git-object comparisons. Keep that distinction in the implementation and notice.

Do **not** reuse `evidence_probe_bindings` unchanged or weaken its publication check at `night_agent_install.py:903`. Factor shared static authentication if useful; require publication only for probe/install. Preserve the existing calibration branch and legacy render behavior. In particular, indiscriminately decoding every chain as UTF-8 would break existing binary/stub render inputs: `tests/test_install_night_agent.py:103` uses `/bin/true`, including the staged-stub test at `:575` (read-only observation).

Retain these refusals:

- Ambiguous, duplicate, unknown or mixed payload declarations.
- Missing/mismatched wrapper sidecar; manifest digest, per-file HEAD bytes, chain source or ruled registration mismatch.
- Wrong evidence class, v4 policy, frozen window, or published-plan literal.
- Existing night records, stale/future plan, HEAD mismatch, invalid schedule, past t0, closed installation span, and hour/minute mismatch.
- Probe/install from an unpublished location; stale/wrong-kind/failed receipt; binding drift, incorrect verify marker, collection/load started, or cleanup unproven.

**Named regression tests and counterfactual inputs:**

- `test_staged_evidence_render_never_executes_chain`: published plan absent, calibration source present; fail on any wrapper/reservation invocation.
- `test_evidence_render_authenticates_inputs`: individually alter sidecar, manifest, tracked harness/source, registration and rehashed wrong published literal; each refuses before plist writes.
- `test_render_keeps_admission_refusals`: expired t0/cutoff, stale plan, wrong HEAD and existing night result; each still refuses.
- `test_published_probe_still_requires_publication`: supply staged or unrelated same-byte plan; probe/install refuse.
- `test_calibration_render_compatibility`: calibration wrapper and legacy no-inspection fixture; compare digest output and plist bytes with baseline.
- `test_staged_stub_render_compatibility`: existing `/bin/true` staged-stub fixture remains accepted.

**Q3: the missing test is the composed arm sequence.** Coverage supports this explanation; reviewer intent cannot be inferred. `EvidenceFixture` originally authors directly at the published path (`tests/test_gen_evidence_night.py:48`). PR #365’s staging regression (`tests/test_night_agent_install.py:1894`) performs publication and bindings but never calls installer render-only. The bench dry-check likewise bypasses that call and manufactures matching plists (`dry-check.py:158`). Thousands of passing component tests cannot exercise an omitted transition.

Add **`tests/test_evidence_arm_sequence.py::EvidenceArmSequenceTests.test_staged_arm_reaches_install_render`**, using an extended `EvidenceFixture` containing launchd templates, the retired-v1 fixture needed by schedule imports, a temporary interpreter link and inert courier executable:

1. Author with `write_night_plan` at staging; run the real evidence generator.
2. Run the actual installer render-only path with NullAdapter while the published plan is absent.
3. Assert three rendered plists, unchanged sealed artifacts, no chain/capture/launchctl/courier invocation, and published argv for night/deadman.
4. Atomically publish; assert unchanged bytes and successful real `evidence_probe_bindings`.
5. Validate a fixture receipt with real bindings, explicitly model supervisor cleanup, require published admission, and render through NullAdapter.
6. Compare actual calendars, argv, WorkingDirectory and RunAtLoad; assert no ledger/budget/pack dependency.

Do not mock reservation inspection, manifest verification, bindings or plist rendering. This test fails for both the old staging-path binding and the current render dispatch defect.

**Yes: bench `dry-check.py` should additionally run real installer render-only and consume its actual plists.** Keep this ordinary-suite test as the durable integration gate.

## Disproved alternatives

- **Teach evidence an argv mode:** unnecessary calibration coupling; changing the frozen chain source also affects its registration digest.
- **Drop render-only:** loses staged admission and the step5 comparison artifacts. The published probe does not replace those checks.
- **Seed a ledger or relax custody arithmetic:** neither is required downstream; execution and dispatch inspection refute this remedy.

V2 command:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_gen_evidence_night tests.test_night_agent_install.EvidencePlanPublicationTests tests.test_night_agent_install.EvidenceProbeReceiptTests tests.test_run_night.EvidenceProbeTests tests.test_run_night.EvidenceProbeFailureTests
```

Output tail: `Ran 39 tests in 18.382s` / `OK`.

## Residual risk

V1’s successful staged rendering used an explicitly isolated in-memory replacement of the faulty inspection call; no repair was applied. Cleanup proof was synthetic. Launchd installation/uninstall, successful collection and external delivery remain unverified.

No repository edits. Final `git status --short --branch` returned `## HEAD (no branch)`; HEAD remained unchanged. Next: implement the bounded render fix and integration test, correct the evidence handback, then have the lead verify the exact repaired arm sequence.