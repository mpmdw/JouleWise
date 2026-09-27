```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Recommend B with session-bound per-night roots; consumer validation and archive verification need explicit changes, and this seat incurred historical-value exposure.",
  "workspace": {
    "base_requested": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "base_mode": "exact",
    "head_start": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "head_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "upstream_end": "670756f3fbb366d9c40a7a128766c9afc5d331cf",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "B",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Strict outcome-blind compliance was not achieved: historical measurements appeared in inspected documentation and verifier constants."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Issuance needs an explicit external-custody contract; per-night roots provide the cleanest archive boundary."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Adding root flags alone leaves verifier admission and path-containment gaps."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "Primary-file authentication must not be reported as complete raw-custody or ledger-history verification."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Historical reissue value semantics already conflict with the corpus verifier's r6/r7 semantics."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/custody-consult-astra-77b1bee2/probe.py topology",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "locators=24 outside_repo_refusals=24 nonempty_primary_files=48"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "locators=24 outside_repo_refusals=24 nonempty_primary_files=48"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/custody-consult-astra-77b1bee2/probe.py red",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "RED: current issuer cannot encode declared sibling external custody"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "external custody accepted"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/custody-consult-astra-77b1bee2/probe.py synthetic",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "verifier_new_generation=refused_before_custody_resolution",
          "SYNTHETIC_BASELINE_PROBES=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SYNTHETIC_BASELINE_PROBES=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/custody-consult-astra-77b1bee2/probe.py legacy-pins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "r6: issued_byte_pin_matches; source_directory projections are relative",
          "r7: issued_byte_pin_matches; source_directory projections are relative"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "r7: issued_byte_pin_matches"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "670756f3fbb366d9c40a7a128766c9afc5d331cf"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^670756f3fbb366d9c40a7a128766c9afc5d331cf$"
      }
    }
  ],
  "flags": [
    {
      "id": "blindness",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Historical measurement summaries and banked historical verifier constants were exposed during reads. No W1/W2 ledger or primary-file value fields were opened. The literal outcome-blind restriction was nevertheless violated.",
      "needs": "Treat this as a qualified technical review, not a compliant blind ruling; obtain a fresh blind seat if required for adjudication."
    },
    {
      "id": "coverage",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Executed probes exercised extracted production functions with synthetic inputs and locator-only projections. No real prepare-candidate, full suite, production-loader validation, or post-change GREEN run was performed.",
      "needs": "Implement under a separate authorized scope, then run focused integration tests and the canonical suite before governed issuance."
    }
  ]
}
```

## Findings

### F1 — BLOCKER: this seat cannot certify strict blindness

The intake read exposed historical measurement summaries in `RUN_STATE.md`; inspecting the corpus verifier also exposed its banked historical measurements. That violates the literal restriction even though **no W1/W2 measured values were opened or used**.

The technical findings below remain useful, but this report should not count as a compliant blind adjudication. No repository files were changed, no other seats’ answers were read beyond the explicitly required scout report, and no agents were called.

### F2 — BLOCKER: choose B, with roots bound to existing session identities

**I recommend B.** Each night is already an independently named custody unit. Let its logical root ID be its existing ledger session ID. A reader can then supply independently restored W1 and W2 directories without reconstructing a common parent, renaming extracted archives, or changing issued bytes.

A is viable if preserving a common archive layout is an explicit permanent contract. Its smaller member schema does not outweigh that extra filesystem-layout obligation here.

The locator-only probe reproduced **24 outside-repository refusals**, twelve per night, and found 48 nonempty primary files. These are custody-locator counts, not an independently verified count of valid captures.

The current helper’s restriction is explicit at [issuer:896](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:896). One correction to the forcing premise: the refusal can be **predicted blindly**, but the real command is not blind. `_select_members` reads evidence at line 1220 and obtains the stored lexeme at line 1237 before calling the path helper at line 1244.

**Proposed artifact delta**

Retain acceptance schema v2 and introduce a generation-selected custody layout:

- Add `derivation_corpus.source_roots`, keyed by registered session ID. Each entry has an exact descriptor such as `{"kind":"external-night-v1"}`.
- Add `source_root_id` to each new-generation member.
- Keep `source_directory` relative to that night root, for example `runs/instrument_validation/<attempt_id>`.
- Register a custody-layout selector for the new generation. Existing generations default to their existing legacy layout.
- Require each member’s root ID to equal the session ID of its matching prior-observation row. Validate the content-ID **and attempt-ID** linkage.
- Store no machine-local archive path in these descriptors.

The external root set must be determined from registration identity and locator topology before inspecting outcomes. Missing or unexpected mappings refuse the operation; they never remove members.

**Minimum coherent change set**

| Site | Required change |
|---|---|
| New `joulewise/calibration_corpus_custody.py` | Shared descriptor validation, canonical relative-path validation, and contained directory/file access. Keep filesystem resolution separate from production artifact validation. |
| [Issuer:896](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:896), `:1203`, `:1827`, `:2021`, `:2201`, `:2371` | Add repeatable `--custody-root SESSION_ID=PATH`; thread bindings through selection; emit root descriptors and member references. Keep `--repo-root` as the actual measurement checkout. |
| [Verifier:73](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:73), `:87`, `:165` | Admit the new generation’s value semantics and expected reconstruction; resolve members through explicit root bindings; retain legacy resolution. |
| [Reissue:127](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/reissue_calibration_acceptance.py:127), `:172`, `:552`, `:584` | Accept the same bindings and use the shared resolver. Preserve descriptors and member references unchanged during a pin-only reissue. |
| [Validator:850](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:850), `:873`, `:950` | Validate the generation-specific root schema, member key set, paths, and root/session linkage without opening custody. |
| Issuer, reissue, validator tests; new resolver/verifier tests | Add external-topology integration coverage and the refusal matrix below. |
| Runbook issuance instructions and custody contract | Document original-locator preparation versus caller-located archive replay, archive completeness, and restoration commands. |

At preparation, these flags **describe the original locations**. Require the derived relative path to resolve back to the original ledger locator, and continue authenticating that original locator. Do not allow the flag to substitute replacement bytes during issuance.

The new descriptor and member references enter `derivation_sha256` and the eventual issued byte pin. Keep physical archive locations out of both. The narrower `derivation_input_sha256` intentionally excludes paths; its existing recipe need not change merely for relocation ([issuer:2258](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:2258)).

**Compatibility and D-138**

Leave r6/r7 artifacts, IDs, registry pins, and generation rows unchanged. Their absent root descriptor means legacy resolution. Missing descriptors for a generation registered as external must refuse, rather than falling back to legacy behavior. V4 confirmed the existing r6/r7 file hashes still match their pins; it did not run their value-reading loaders.

The production loader remains an exact-byte artifact authenticator, with no custody-directory I/O ([loader:1171](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:1171)).

The scout also over-compresses the D-138 dependency. None of the minimum resolver changes touches the four estimator-pinned files listed at [bracketing:206](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_bracketing.py:206). Thus the compatibility patch does not inherently stale r7 or require an immediate reissue. **Actual successor issuance** still needs the new generation registration, issued artifact pin, dependent pins, and lead-owned atomic transaction ([D-138:10363](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/decision_log.md:10363); [runbook:3154](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:3154)).

**No sanctioned no-code cure found**

There is an existing mechanism the scout omitted: `JOULEWISE_BACKUP_ROOTS`. It remaps configured historical iCloud prefixes for read/replay; other locators remain unchanged. Issuance hashing explicitly rejects a nonempty override ([ledger:5354](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_ledger.py:5354); [contract:451](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/contracts/calibration_ledger_append.md:451)). It cannot repair these night-root locators.

Likewise, using the custody parent as `--repo-root` would break its separate committed-head-pin responsibility ([ledger:1278](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_ledger.py:1278)). I would prefer no code change only if an already-authorized artifact resolver existed; the inspected consumers provide none.

### F3 — BLOCKER: root flags alone do not complete the consumer repair

The consumer map needs these corrections:

- **Verifier admission:** an unbanked acceptance ID refuses before custody resolution ([verifier:76](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:76)). The new generation requires explicit support. Keep historical banked expectations; for a preparation-time candidate, use an explicitly non-authoritative verification route.
- **Path syntax:** containment after `resolve()` does not reject absolute paths or `..` paths that happen to end inside the root.
- **File containment:** checking the directory does not stop `instrument_evidence.json` itself being a symlink outside it.
- **Basename:** reissue checks it at line 175; the corpus verifier does not.
- **Validator:** it currently requires only a string for `source_directory`; an artifact-level root descriptor is not already validated merely because extra corpus fields are tolerated.

The synthetic probes confirmed that standalone reissue authentication currently accepts an absolute path inside the root, an internally resolving `..` path, an ignored unknown root descriptor, and an escaping primary-file symlink.

Use raw-string canonical POSIX-path checks before normalization: reject empty paths, absolute paths, `.`/`..` components, duplicate separators, and ambiguous separators. Then enforce directory and file containment. Reuse the existing no-follow authenticated reader where suitable ([authentication I/O:281](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/authentication_io.py:281)); checking only `directory.resolve()` is insufficient.

**Defect-shaped tests**

| Test | RED/current observation | Required GREEN |
|---|---|---|
| Synthetic checkout plus two external night roots | Existing issuer helper refuses; V2 exits 1 | Preparation emits all eligible members with session-bound root IDs; both consumers reopen them |
| New-generation verifier | V3 refuses before path resolution | Explicit new-generation/candidate support verifies primary bytes and reconstructs statistics |
| Missing, duplicate, unknown, or wrong-session root mapping | Root metadata currently ignored by standalone reissue helper | Refuse before member-value parsing; no fallback search |
| Absolute member path, including one inside root | Accepted by reissue probe | Refuse |
| `..`, including a path resolving inside root | Accepted by reissue probe | Refuse |
| Directory symlink escape and individual primary-file symlink escape | Primary-file escape accepted | Refuse both |
| Wrong basename with otherwise matching bytes | Reissue checks; verifier lacks check | Every filesystem consumer refuses |
| One-byte manifest/evidence mutation | Primary mutation rejected by probe | Retain refusal |
| One-byte raw-trace mutation with JSON files unchanged | Reissue probe accepts | Full custody verification refuses |
| Independently relocated W1/W2 archives | No explicit per-night mapping today | Identical artifact and scientific seals; only caller bindings differ |
| Missing file/root | Must not become an exclusion | Whole verification/preparation refuses |
| Legacy r6/r7 | Existing pins match | Artifact bytes remain unchanged; legacy loader and path behavior remain valid |

Also test that root/path failures occur before the member-value reader is called. Successful relocation must preserve member IDs, order, digests, exclusions, and numerical outputs.

### F4 — SHOULD-FIX: distinguish preserved commitments from completed custody verification

The naming change can preserve the evidential chain without rewriting any ledger row or primary bytes. Content identity is already path-independent: it hashes the two primary-file digests ([ledger:269](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/calibration_ledger.py:269)).

But the existing consumers do less than a full raw replay:

- `_read_member_evidence` compares only manifest and instrument-evidence digests, even though `artifact_hashes` can return other governed hashes ([issuer:1043](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/issue_calibration_acceptance_generation.py:1043)).
- Verifier and reissue authenticate those same two files; they do not verify every raw file.
- Revision 5’s battery check authenticates its battery raw files, which is a separate check from validating the powermetrics trace ([battery_float:435](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/joulewise/battery_float.py:435)).

V3 demonstrated that a one-byte synthetic raw-trace mutation passes reissue authentication and the isolated issuer member reader. This is not evidence that the entire preparation command was executed or bypassed.

**What a future reader can establish**

With the issued repository state and the two restored night roots, the repaired tools can:

1. Authenticate the issued artifact against its registry pin.
2. Bind each member to its declared night and matching prior-set identity.
3. Authenticate manifest and instrument-evidence bytes.
4. For this fresh-capture generation, compare the stored lexeme and reconstruct the acceptance statistics.
5. Verify raw bytes against digest fields in the authenticated primary documents—provided that raw verification is actually implemented or separately invoked.

Preserving the hashes preserves a commitment to the raw bytes; it does not prove that archived raw bytes remain available and correct.

Reconstructing the **original ledger history and selection decision** additionally requires the complete ledger prefix through the cutoff, its committed head pin, and relevant registration/verdict records. The artifact’s prior-set projection cannot reconstruct that history. Do not assume “repository plus night roots” includes the measurement checkout’s untracked ledger. Explicitly inventory and preserve that replay material in the issuance/archive packet.

**Archive and science implications**

Both A and B are outcome-neutral if mappings are fixed from registration identities and paths. Either becomes scientifically dangerous if missing custody causes a member to be dropped, if multiple archive candidates are searched until one passes, or if mappings are changed after examining outcomes. Refuse the whole operation on missing or corrupt custody.

The unissued-root immobility rule remains intact ([runbook:2573](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/phase_2/derivation_night_runbook.md:2573)). B does not authorize moving these originals.

For separately authorized post-issuance archiving, record per-night file inventories and hashes, preserve the ledger replay material, and verify restoration. Existing iCloud practice distinguishes local hashing from verified upload and restoration ([archive report:14](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/docs/run_reports/2026-07-28-icloud-archive-prune.md:14)). A cloud placeholder is not readable evidence. Later archive relocation changes only caller bindings; issued descriptors and digests stay fixed.

### F5 — SHOULD-FIX: do not promise historical reissue GREEN from path compatibility alone

The verifier explicitly assigns r6/r7 `stored_lexeme_is_member_value=False` and rejects equality with the superseded stored scalar ([verifier:61](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/tests/verify_calibration_acceptance_corpus.py:61), `:97`).

Reissue instead unconditionally requires stored-lexeme equality and then copies that value into the candidate ([reissue:204](/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2/scripts/reissue_calibration_acceptance.py:204), `:265`).

That is a pre-existing semantic incompatibility, not an external-root defect. Preserve r6/r7 artifact and loader compatibility, but do not claim their real-corpus reissue path is already green. Resolve historical re-derivation semantics separately; do not weaken the legacy verifier’s rule to make a custody patch pass.

## Residual risk

The [scratch probes](/tmp/custody-consult-astra-77b1bee2/probe.py) use AST-extracted production functions, synthetic evidence, and locator-only projections. Their filesystem-reader shim matches ordinary no-session reads. They establish the reported local behaviors, not end-to-end issuance or live scientific validity.

No implementation was made, so post-change GREEN remains prospective. The next step is a compliant blind ruling, followed by a separately authorized implementation and integration-test scope.

RECOMMEND: B