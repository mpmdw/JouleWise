```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"NEEDS_RULING: v2 component metadata changes D-079-commented producer pins without changing the r6 acceptance identity or digests.","workspace":{"base_requested":"c8ab5efb","base_mode":"exact","head_start":"c8ab5efbc541f2bf16697857b929717d08840b40","head_end":"c8ab5efbc541f2bf16697857b929717d08840b40","upstream_end":null,"branch":"feat/2026-09-04-fb-metadata"},"pathspec":["docs/process_traces/2026-09-04-peer-audit/49-fb-v2-ci-fix-2-report.md"],"unowned_dirty":[],"verdict":{"implementation":"no_change","acceptance":"needs_ruling"},"verification":[{"id":"V1","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest tests.test_mint_floor_artifact_generalized > /tmp/fb-v2-ci-fix-2-mint.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 83 tests in 32.620s","","FAILED (failures=4, errors=6, skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"Ran 83 tests in [0-9.]+s\\s+OK(?: \\(skipped=2\\))?$"}}],"flags":[{"id":"F1","kind":"lead_ruling","level":"blocking","text":"NEEDS_RULING: SYNTHETIC_PRODUCER_PIN_SHA256S and SYNTHETIC_PRODUCER_SET_SHA256 must change transitively with component hashes, but their comment says they move with a D-079 issuance; current acceptance remains d079_calibration_acceptance_v2_n17_r6 with both digests unchanged. No pins or test code were edited.","needs":"Rule whether the explicit fixture review may update these dependent self-hashes for PR #292 metadata alone and clarify their comment."},{"id":"F2","kind":"verification_gap","level":"blocking","text":"Stopped under the explicit pin-issuance gate. Regression, pin repair, matrix run, and both relocation reruns remain pending. Mint baseline fails.","needs":"After ruling, resume the authorized fixture repair and regression, then run the four permitted targets sequentially with R7F_CORPUS_ROOT."}]}
```

## Change

2026-09-05: investigation and report only. No test constants, comments, regression, production validators, or output were changed; no commit was made. The workspace started clean at the requested exact HEAD. Intake found no active stop card; this is the active A151 F+B metadata lane. Lead-owned state files were preserved under the exhaustive write allowlist.

**NEEDS_RULING — question:** May the explicit fixture review update the producer-pin and producer-set constants solely for the transitive PR #292 v2 discipline metadata change, despite their D-079 issuance comment, with the acceptance identity unchanged?

**Options considered:** (1) Authorize these dependent fixture self-hash updates and clarify that both component-byte changes and acceptance issuance can move them. (2) Retain the protected pins and leave this CI repair blocked pending a different lead-approved design. Downgrading discipline output or weakening validation is outside this task.

**Recommendation:** Option 1, as an explicit resumed ruling. Each producer includes its component artifact SHA-256, so its canonical self-hash necessarily changes when that component pin changes. This recommendation is advice only; the user explicitly required stopping in this situation.

**Completed:** Read the prior report and fixture comments, ran the authorized mint baseline, and independently proved the producer-pin dependency with `_fixture_canonical_sha256`. The current fixture with the old component constants reproduces both frozen producer pins and the producer-set constant exactly. Replacing only those two component-hash strings in detached producer dictionaries with the prior report's observed v2 component hashes changes all three protected constants while preserving every acceptance field.

**Blocked work:** Re-pinning any constants, the explanatory pin comment, the one v1-counterfactual/v2 regression, and acceptance verification. The two relocation methods and discipline matrix were not run after the explicit stop condition was established. There was no independent implementation that could establish the requested passing fixture regression without adjudicating the protected pins.

## Verification notes

V1 exact tail:

```text
----------------------------------------------------------------------
Ran 83 tests in 32.620s

FAILED (failures=4, errors=6, skipped=2)
```

The baseline again reports the nested mint-trust method `test_v2_assurance_and_git_containment_are_required_provenance` failing at component 0: pinned `8ac980a543bfa7d61d4f1e8e849ba6ca12d6ac16320592ae081da2a2bca70495`, observed `dae1d43209662a471c1ff1d283f151c4296da58a6456177a9543e6b6061391e7`. This is the module reached by production `arm_readiness_evidence._derive_mint_trust → _run_suite`, as established in report 48.

The CLI baseline also reports its component 0 changing from `6325b71a5b7826201e1d93a087a1a4e90854fb6edcf5149322bc50de4d272cf6` to `5d0b4bafbb106b3a2f577f642f9fdee7b426e20fdbbf8aeaa6f1b126806fdc03`. These production diagnostics are observations, not approved independent re-derivations. Full component/CLI fixture review remains pending. In particular, `_fixture_canonical_sha256` hashes compact canonical JSON, whereas `_fixture_artifact_sha256` hashes indented artifact JSON with a terminal newline; the two byte formats must not be confused.

The four failure methods were `test_default_only_v2_output_remains_byte_identical_to_golden_oracle`, `test_legitimate_report_reaches_legacy_authentication_after_preparse`, `test_phase0_base_floor_bytes_are_pinned`, and `test_production_cli_mints_and_names_every_custody_mismatch`. The six errors were `test_malformed_v2_producer_provenance_returns_errors_not_crash`, `test_mixed_four_cell_full_mint_is_cell_local_and_bound`, `test_synthetic_two_plan_four_cell_mint_passes`, `test_v2_assurance_and_git_containment_are_required_provenance`, `test_v2_mint_recomputes_rendering_but_never_fills_pins`, and `test_verdict_bracket_refuses_repin_to_earlier_authentic_session`. This report does not claim all failures are resolved or have the same cause.

Independent inspection command (executed successfully, exit 0; no mint implementation builds or hashes the candidate producers):

```sh
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B - <<'PY'
import copy
import json
from tests import test_mint_floor_artifact_generalized as fixture
pinset, _, _ = fixture.synthetic_v2_fixture()
producers = pinset['producer_plans']
for producer, digest in zip(producers, fixture.SYNTHETIC_COMPONENT_SHA256S):
    producer['component_artifact']['sha256'] = digest
old_pins = tuple(fixture._fixture_canonical_sha256(p) for p in producers)
old_set = fixture._fixture_canonical_sha256(producers)
assert old_pins == fixture.SYNTHETIC_PRODUCER_PIN_SHA256S
assert old_set == fixture.SYNTHETIC_PRODUCER_SET_SHA256
candidate = copy.deepcopy(producers)
# Component observations already recorded by the prior round's independent
# artifact-byte hash diagnostic; these are inputs, not newly approved pins.
observed_v2 = (
    'dae1d43209662a471c1ff1d283f151c4296da58a6456177a9543e6b6061391e7',
    'c12749ccf1691860c5635c08de5cafce9edf57f1f81604bead7951bc80925b9c',
)
for producer, digest in zip(candidate, observed_v2):
    producer['component_artifact']['sha256'] = digest
assert [p['calibration_acceptance'] for p in candidate] == [p['calibration_acceptance'] for p in producers]
print('Current acceptance:', json.dumps(producers[0]['calibration_acceptance'], sort_keys=True))
print('Old component pins recover BOTH frozen producer pins and producer-set pin exactly.')
for i, (old, producer) in enumerate(zip(old_pins, candidate)):
    new = fixture._fixture_canonical_sha256(producer)
    assert old != new
    print(f'producer[{i}]: {old} -> {new}')
new_set = fixture._fixture_canonical_sha256(candidate)
assert old_set != new_set
print(f'producer_set: {old_set} -> {new_set}')
print('NEEDS_RULING: protected producer pins move with component metadata while acceptance identity and both digests remain unchanged; no pins written.')
PY
```

Inspection output:

```text
Current acceptance: {"acceptance_id": "d079_calibration_acceptance_v2_n17_r6", "artifact_sha256": "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d", "derivation_rule_id": "joulewise.calibration_acceptance_bound.v2", "derivation_sha256": "18d09aa9d4accb16a8dff770de85cd7e7525bdb0b6e68f1de716e20fb8a9b9f3"}
Old component pins recover BOTH frozen producer pins and producer-set pin exactly.
producer[0]: 1d9bd87ab82f721ea08a013d97630683e665d5afb23455255899ebb8a642d74c -> 0a9d4d5f0cd046787575876ce9fd53ad01b2ea4097360c4aec5a2fa8b0ad8100
producer[1]: 509e6b38c155897c523320a7061253b115609e70bf4f9b95f8b17d1c96f009d1 -> a15195aabe749c18d55f12612f45d9afc890f490547e10366f3cee95c8cbf09a
producer_set: fe9c031e6fbcec9d1bc771ba2297972469c8a72140596d5655f37559e85c7065 -> 02fca6e419bc2506a8595987bc0680f8fa86b09b8afce51ccb9ca3ddd1ff8f26
NEEDS_RULING: protected producer pins move with component metadata while acceptance identity and both digests remain unchanged; no pins written.
```

Only the authorized mint test module ran as a top-level unittest target; no discovery suite or Claude/Codex launcher ran. The inspection only constructed fixture dictionaries in memory. No quiet-machine measurement was performed. The branch has no configured upstream.

