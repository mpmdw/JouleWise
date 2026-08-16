```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a caller-verified canonical path identity passed verbatim, with an immutable grant-set accessor and exact post-grant delta checks; reject sampled-fd and inode-keyed formulations as the default cure.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "0418bfc1e338ca5fe228f9cf7ff5a999701a03d8",
    "head_end": "0418bfc1e338ca5fe228f9cf7ff5a999701a03d8",
    "upstream_end": "0418bfc1e338ca5fe228f9cf7ff5a999701a03d8",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "caller_verified_identity_verbatim",
    "anchors_resolved": true,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "question": "Q1",
        "text": "Do not adopt the round-2 sampled-fd formulation or a st_dev/st_ino grant key as full closure: hardlink and bind-style aliases collapse to one object identity and violate the existing literal-path authorization boundary."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "question": "Q1-Q2",
        "text": "Change allow_governed_extraction_spec to accept one canonical caller-verified string identity verbatim, perform no filesystem lookup in the callee, migrate the recorder and both mint paths, and state the Python caller-forgery boundary explicitly."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "question": "Q3",
        "text": "Expose an immutable read-only snapshot of governed identities and require exact before/after grant-set verification; the recorder's postcondition should be the singleton intended identity."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "question": "Q4",
        "text": "The future cold gate must execute deterministic persistent-swap, swap-and-revert, hardlink-restore, alias, caller-forgery, and mutation-kill probes at the new identity boundary, plus the full governed-reader regression stack."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "question": "Q5",
        "text": "D-138 does not stage authentication_io.py, but frozen-pack readiness evidence hashes that module; if adopted, merge and gate this work before the one-time Phase-2 re-freeze, otherwise defer it through the current pack lifecycle."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -n \"def allow_governed_extraction_spec|authentication\\.allow_governed_extraction_spec|def _allow_governed_extraction_spec|_allow_governed_extraction_spec\\(\" joulewise/authentication_io.py joulewise/window_duration_margins.py scripts/mint_floor_artifact_generalized.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/mint_floor_artifact_generalized.py:1759:    _allow_governed_extraction_spec(comparative_inputs.spec_path)",
          "scripts/mint_floor_artifact_generalized.py:3683:                _allow_governed_extraction_spec(paths.spec_path)",
          "joulewise/authentication_io.py:349:    def allow_governed_extraction_spec(self, path: Path | str) -> None:"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "joulewise/authentication_io\\.py:349:"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_authentication_io tests.test_window_duration_margins tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_authentication_session_allows_only_named_governed_spec_vocabulary",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The managed read-only environment has no writable temporary directory, so the focused baseline suite could not initialize.",
      "needs": "Run the focused suites and attack harness in the writable future implementation/cold-gate worktree."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Ed's risk-appetite choice between implementing this work order and retaining only the registered limitation remains open.",
      "needs": "Rule proceed-or-defer before the one-time Phase-2 successor re-freeze."
    }
  ]
}
```

## Findings

### F1 — blocker — Q1: reject inode-keyed and sampled-fd closure

Recommendation: use a caller-verified canonical path identity passed verbatim.

The round-2 “fd-identity” proposal was not a stable-descriptor capability. It sampled `(st_dev, st_ino)` before the grant and re-statted the pathname after the read while the grant still re-resolved the path. REPLAY E restored a hardlink to the original inode before the second sample, so both tuples matched although the grant had registered the attacker-selected identity. That exact defeat is recorded at [`coldgate-opus-refuter-findings.md:22-23`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/process_traces/2026-08-15-recorder-race-coldgate/coldgate-opus-refuter-findings.md:22>).

A true fd design is different: the authority plane must own or duplicate an already-open descriptor and parse bytes from that same open-file description. A raw integer fd is insufficient because descriptor numbers are reusable. That design survives REPLAY E’s temporal trick, but it has substantially larger reader/lifetime/recording blast radius and an fd alone does not prove which pathname obtained it.

`(st_dev, st_ino)` as the grant key shares the alias defect:

- Hardlinks intentionally have the same tuple.
- Bind mounts may expose the same underlying object through another namespace path.
- Inode reuse introduces another session-lifetime concern.
- It changes the contract from “this literal committed path” to “any alias of this filesystem object.”

The existing ledger avoids claiming otherwise: it requires `st_nlink == 1` and distinct lock/ledger tuples at [`calibration_ledger.md:138-147`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/contracts/calibration_ledger.md:138>).

| Mechanism | Disposition | Reason |
|---|---|---|
| Caller-verified canonical string, accepted verbatim | Adopt | Smallest cure; preserves literal-path semantics; namespace swaps cannot alter the value added to the grant set. |
| True owned-fd grant and same-fd read | Defer | Strongest object binding, but requires a new fd-reader/capability lifecycle across recorder and mint. |
| Pre/post fd-stat comparison | Reject | This is the exact hardlink-restoration formulation defeated by REPLAY E. |
| `(st_dev, st_ino)` grant key | Reject | Authorizes every hardlink/object alias and cannot represent the ruled literal-path boundary. |
| Caller-side content/no-follow precheck | Reject | Still leaves callee re-resolution; already rejected by the composed verdict. |

The recommended signature should be visibly identity-based and preferably keyword-only:

```python
allow_governed_extraction_spec(*, verified_identity: str) -> None
```

The callee may perform lexical validation—absolute/canonical spelling and `.json` suffix—but must not call `resolve`, `realpath`, `samefile`, `stat`, or reopen the path. This closes the executed check-to-grant race, not every filesystem TOCTOU.

Python honesty is binding: this cannot be described as authenticating the caller, creating an unforgeable capability, or defending against arbitrary code already executing in-process. It proves only that a trusted caller’s immutable identity is not reinterpreted by the callee. That matches the launch-binding precedent: “Python does not authenticate its caller” at [`decision_log.md:9203-9208`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/decision_log.md:9203>).

### F2 — should_fix — Q1/Q2: API blast and resolved anchors

All anchors below resolved at HEAD `0418bfc1e338ca5fe228f9cf7ff5a999701a03d8`.

| Anchor | Confirmed location |
|---|---|
| Grant definition and offending callee re-resolution | [`authentication_io.py:349-363`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/authentication_io.py:349>) |
| Existing immutable records accessor | [`authentication_io.py:344-347`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/authentication_io.py:344>) |
| Path-reader identity and grant membership | [`authentication_io.py:408-423`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/authentication_io.py:408>) |
| No-follow and ingest membership consumers | [`authentication_io.py:437-475`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/authentication_io.py:437>) |
| Recorder’s already-resolved contained identity | [`window_duration_margins.py:200-209`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/window_duration_margins.py:200>) |
| Recorder guard, grant, and pinned read | [`window_duration_margins.py:410-438`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/joulewise/window_duration_margins.py:410>) |
| Mint grant wrapper | [`mint_floor_artifact_generalized.py:1255-1261`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/scripts/mint_floor_artifact_generalized.py:1255>) |
| Two-component mint grants | [`mint_floor_artifact_generalized.py:1758-1759`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/scripts/mint_floor_artifact_generalized.py:1758>) |
| Multi-cell mint per-component grant | [`mint_floor_artifact_generalized.py:3673-3685`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/scripts/mint_floor_artifact_generalized.py:3673>) |
| Direct API regression | [`test_mint_floor_artifact_generalized.py:5518-5568`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/tests/test_mint_floor_artifact_generalized.py:5518>) |

Those are all production grant users:

1. The floor-pack branch of the margin recorder.
2. The two-component mint, granting its absolute and comparative specs.
3. The v2 multi-cell mint, granting each component spec.

The implementation blast radius is therefore `authentication_io.py`, `window_duration_margins.py`, the generalized mint wrapper, and their three owning test modules. No other production call site was found.

### F3 — should_fix — Q3: F-10 accessor and proof

Add beside the existing `records` property:

```python
@property
def governed_extraction_spec_identities(self) -> frozenset[str]:
    with self._lock:
        return frozenset(self._governed_spec_vocabulary_identities)
```

Never return the live set or a mutable proxy.

For the recorder, whose contract permits exactly one grant:

```python
before = authentication.governed_extraction_spec_identities
if before:
    refuse(...)
authentication.allow_governed_extraction_spec(
    verified_identity=registry_identity
)
after = authentication.governed_extraction_spec_identities
if after != {registry_identity} or after - before != {registry_identity}:
    refuse(...)
```

For mint’s legitimate repeated/multiple grants, the generic postcondition is `after == before | {identity}`. The recorder retains the stronger singleton condition.

This proves that the persistent session grant set gained exactly the intended identity and no attacker-selected identity. It directly detects the old re-resolution behavior. It does not prove file bytes, inode provenance, read consumption, or caller honesty; the authenticated read records and SHA pins retain those responsibilities. F-10’s executed basis and caveats are at [`coldgate-opus-refuter-findings.md:40-41`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/process_traces/2026-08-15-recorder-race-coldgate/coldgate-opus-refuter-findings.md:40>).

### F4 — should_fix — Q4: future cold-gate packet

The packet should contain the final diff, exact heads, resolved anchor table, complete grant-user census, old race harness, and these executed attacks:

- Persistent ALPHA→BETA swap at the grant boundary: intended ALPHA identity only; BETA absent from grants and records; read refuses `authoritative_input_invalid` before census.
- REPLAY D swap-and-revert: safe success is acceptable only if the grant set is exactly ALPHA and BETA never appears. The old defect was attacker influence over authorization, not process success by itself.
- REPLAY E hardlink restoration: same expected result as D; additionally prove the two paths share `(st_dev, st_ino)` while the alias does not inherit a path-string grant.
- Direct hardlink and directory-alias reads: alias identity must not receive the vocabulary exemption.
- Bind-mount alias on a platform capable of executing it; otherwise record `NOT_APPLICABLE`, not PASS.
- Direct arbitrary-identity call from Python: demonstrate that it is accepted as a documented in-process trust boundary, preventing an unforgeability overclaim.
- Concurrent uninstrumented 400/1200-style swap loops as corroboration, never as the decisive proof.
- Mutations: restore `.resolve()` inside the grant; remove the F-10 delta check; return the live mutable set; replace the string key with the inode tuple. Each must kill a named regression.

Held-property regressions should include [`test_window_duration_margins.py:139-305`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/tests/test_window_duration_margins.py:139>), authentication-session tests, both mint paths, the real frozen-pack census, strict forbidden-vocabulary cases, the canonical suite, and the post-merge readiness-evidence regeneration checks.

### F5 — should_fix — Q5: sequencing

`authentication_io.py` is not in D-079’s four-file pin set. The issued artifact names only `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, and `reduce.py` at [`calibration_acceptance_d079_v2.json:39-44`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/tests/fixtures/d117_v2_production/issued/calibration_acceptance_d079_v2.json:39>). D-138’s same list and staging rule resolve at [`decision_log.md:9609-9628`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/decision_log.md:9609>).

Therefore this WO does not ride `impl/wo-detect-pulses-budget`. The branch diff is code/test-disjoint from the recorder-grant footprint.

However, all three frozen packs’ MINT_TRUST, MULTICELL_MINT, recovery-ledger, and three-window source records hash `authentication_io.py`—12 source files total. A representative binding is [`multicell-mint.json:113-117`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.sources/multicell-mint.json:113>). Changing the mint wrapper or its tests also changes explicitly recorded primary/test hashes at [`multicell-mint.json:268-286`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.sources/multicell-mint.json:268>).

Recommended sequence:

1. Take Ed’s proceed/drop ruling.
2. If proceeding, implement and cold-gate on an independent branch.
3. Merge before Phase 2’s single successor re-freeze.
4. Build the re-freeze at the combined head containing this WO and the staged detect-pulses work, regenerating readiness evidence once.
5. If not landed before that transaction, defer through the current pack lifecycle; do not force a second re-freeze.

This follows the “re-freeze once, atomically, last” order at [`council-verdict.md:97-100`](</private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtG-grantconsult/docs/process_traces/2026-08-15-readiness-council/council-verdict.md:97>) while keeping the WO cleanly droppable.

## Residual risk

The recommended string identity closes the executed check-to-grant re-resolution, not the separate `resolve()`-then-`open()` window inside the authentication reader or in-place mutation of an already-open inode. Current post-read SHA pins bound receipt integrity, but no stronger filesystem-atomicity claim is licensed.

No dynamic race probes ran in this read-only consult. The focused baseline suite also could not initialize because the environment exposes no writable temporary directory. The future rule-11 gate must supply the executed evidence.