```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Choose option (b) for T-0 v1: rule deliberate operator fabrication out of model, correct the provenance claims, and remove the public injection seam; real operator-excluding provenance requires a new attested-app-plus-external-verifier architecture.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "4b32c18781afb7cf09c281637e94d2e896fde633",
    "head_end": "4b32c18781afb7cf09c281637e94d2e896fde633",
    "upstream_end": "900174a6ae6b1b527364dfa577f0beac62c62f3e",
    "branch": "impl/wo-t0-producer"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/phase_2/window_runbook.md",
    "joulewise/arm_readiness_evidence.py",
    "joulewise/arm_readiness_evidence_t0.py",
    "scripts/capture_t0_step.py",
    "scripts/prewindow_check.sh",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_capture_t0_step.py"
  ],
  "verdict": {
    "ruling": "OPTION_B_FOR_T0_V1",
    "post_delta_disposition": "REGISTERED_LIMITATION_NONBLOCKING",
    "findings": [
      {
        "id": "F4",
        "severity": "blocker",
        "summary": "The committed v1 consumer proves canonical bytes and same-boot temporal consistency, not producer origin; its no-human/derive-never-enter claims remain false until superseded by an explicit trusted-operator limitation and API/doc corrections.",
        "closure": "After the specified contract and public-interface deltas land, close F4 as a registered limitation rather than requiring local cryptographic provenance."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git -C ../wo-t0producer show 4b32c18781afb7cf09c281637e94d2e896fde633:joulewise/arm_readiness_evidence_t0.py | sed -n '449,498p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "value[\"finished_monotonic_ns\"] > now",
          "now - value[\"finished_monotonic_ns\"] > _MAX_T0_SEQUENCE_AGE_NS",
          "result = (value, identity)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "result = \\(value, identity\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git -C ../wo-t0producer show 4b32c18781afb7cf09c281637e94d2e896fde633:scripts/capture_t0_step.py | rg -n '^def capture_step|^    prompt:|^    execute:|^    monotonic_ns:|^    utc_now:'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "791:    prompt: Callable[[str], str] = input,",
          "792:    execute: Callable[..., subprocess.CompletedProcess[bytes]] = _execute,",
          "793:    monotonic_ns: Callable[[], int] = time.monotonic_ns,",
          "794:    utc_now: Callable[[], str] = readiness._utc_now,"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "monotonic_ns:.*time\\.monotonic_ns"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git -C ../wo-t0producer show 4b32c18781afb7cf09c281637e94d2e896fde633:joulewise/arm_readiness.py | sed -n '55,58p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"model\": \"single_authority_hash_bound_replay.v1\",",
          "\"independent_attestation\": False,"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"independent_attestation\": False"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent",
      "cwd": "../wo-t0producer",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F-RULING",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The branch must not merge while the historical no-human provenance requirement remains apparently promised but unenforced.",
      "needs": "Adopt option (b), land the exact contract/API deltas below, then reclassify F4 as a registered limitation."
    },
    {
      "id": "F-CONCURRENT",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Seven target-worktree paths became concurrently dirty after consultation began; this ruling is pinned to committed head 4b32c187.",
      "needs": "Lead must reconcile the concurrent fix round and verify that it does not silently claim cryptographic provenance."
    },
    {
      "id": "F-ENV",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox denied creation in $TMPDIR, so the focused temp-fixture test could not execute.",
      "needs": "Replay V4 in a writable lead-controlled environment; the ruling itself rests on committed-source inspection."
    }
  ]
}
```

## Findings

### F4 — Option (b) for v1; blocker until the contract is honest

The author authenticates canonical bytes, exact keys, typed monotonic values, current boot identity, freshness, and ordering. It does not authenticate which process produced those bytes. The test fixture itself hand-writes a synthetic 600-second capture that the author accepts, and `capture_step` publicly exposes `execute`, `monotonic_ns`, and `utc_now` injection.

This is the same trust-root class as the ledger’s malicious-trusted-writer exclusion, but a different consequence from the recorder race. The recorder ruling explicitly kept the concurrent unprivileged writer in model and accepted the limitation because post-grant receipt integrity remained intact. Here, forged historical dwell directly defeats T-0’s semantic purpose. Therefore the limitation is acceptable only through an explicit trusted-operator/no-concurrent-writer assumption—not by claiming integrity survives the attack.

A local HMAC, root-owned secret, Keychain key, or callable Secure Enclave key does not exclude Ed-as-administrator. It either exposes the key through administrator authority or gives the operator a signing oracle for fabricated payloads. Biometric presence proves authorization to sign, not that ten minutes elapsed. Apple’s Managed Device Attestation attests device and OS properties, not arbitrary userland command execution. [Apple’s documented scope](https://support.apple.com/guide/deployment/deploy-managed-device-attestation-dep54e5ac1fd/web) confirms that boundary.

A real option (a) exists only as a new architecture:

1. Replace the Python wrapper with one hardened, signed capture application that internally owns the entire E-4→E-9 sequence and accepts no transcript, timestamp, or generic signing payload.
2. Have an external verifier issue an unpredictable nonce before E-4.
3. Bind an App Attest assertion to the nonce, app/team/bundle/version, HEAD/tree/pack, boot UUID, monotonic transcript, exact argv, and output hashes.
4. Have the server validate app/device attestation, full-security/SIP state, nonce, and strictly increasing assertion counter, then countersign a receipt whose public key is pinned by the author.
5. Make the author accept only that countersigned receipt and its bound capture bytes.

App Attest supports this app-integrity, server-challenge, payload-assertion shape on macOS 27+, including anti-replay counters and security-state signals. [Apple’s WWDC26 specification](https://developer.apple.com/videos/play/wwdc2026/201/) describes those guarantees.

That trust root genuinely moves outside Ed: Apple’s Secure Enclave and attestation chain, the reviewed signed application, developer identity, and the remote verifier’s key/state. It is therefore not merely a local HMAC. It is also disproportionate to WO-T0-PRODUCER and introduces a server, application distribution, macOS-version dependency, and another correctness-critical implementation.

Recommended exact v1 deltas:

- In `docs/decision_log.md`, preserve the historical council wording but supersede D-134 clause 6 with:

  > Derive-never-enter is a production-interface and ceremony rule, not independent producer attestation. When faithfully invoked, the production CLI derives row values, command captures, timestamps, identities, and digests; operators supply only paths and registered irreducible observations. Consumers authenticate canonical bytes, same-boot freshness/order, and fresh current-state probes, but cannot prove that the T-0 input bytes originated in the shipped wrapper. Deliberate fabrication by the trusted operator/authority is outside the v1 single-authority threat model.

- Amend the D-078 acquisition paragraph to state that canonical/no-clobber publication prevents malformed or accidental replacement, not trusted-authority fabrication. Retain `single_authority_hash_bound_replay.v1` and `independent_attestation:false`; do not add a misleading signature field.

- In `joulewise/arm_readiness_evidence_t0.py`, narrow the module claim “every machine-observable condition is re-derived” to distinguish fresh current-state probes from trusted historical E-step captures.

- In `scripts/capture_t0_step.py`, make the production signature exactly `capture_step(step_id, pack_root, custody_root, window_plan_root)`. Resolve `input`, `_execute`, `time.monotonic_ns`, and UTC internally. Tests may patch private module functions, but no production/public callable should accept clock or execution dependencies. This is misuse resistance, not a security boundary.

- Add a signature regression test proving the four injectable parameters are absent. Keep the assurance test proving independent attestation is false.

- In runbook §5C, state that direct JSON authorship, modified library invocation, or input-file edits violate procedure but are not mechanically detectable in v1. Clarify that the terminal-review commit attests the reviewed tree and pack—not runtime capture provenance.

- Add the human handback record:

  > I personally performed §5A and invoked the unmodified production CLI for E-4 through E-9 on the recorded boot; I did not create or edit any `arm_readiness.t0.inputs` file or substitute clock/execution functions; E-7b remained under wrapper control until READY; launch followed successful author→ARM→verify→consume.

  Bind that attestation to operator identity, boot UUID, HEAD/tree/pack, all nine input hashes, and the arm/consumption receipts.

After these deltas, F4 should close as a registered limitation, not trigger another cryptographic patch round.

## Residual risk

Under option (b), a deliberately fabricating operator—or another same-UID writer present despite the zero-agent fence—can still manufacture acceptable historical dwell/order captures. Terminal review binds code and pack; the §5A tap binds the ceremony procedurally; neither is independent proof.

Under future option (a), residual trust moves to Apple’s attestation system, the signed capture app’s correctness, and the external verifier. Any generic payload-signing API, injectable clock/executor, or server that signs caller-supplied transcripts recreates F4 at the new boundary.