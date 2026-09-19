# Exhibit C — consult 07 (Astra xhigh) and the Opus contract refuter 07, verbatim, and the lead adjudication 07a

## Astra consult 07

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a test-only fix: preserve the advancing committed pin and existing generator drift checks; test the baseline-prefix invariant already implemented by production (docs/decision_log.md:7511; joulewise/calibration_ledger.py:2614).",
  "workspace": {
    "base_requested": "2f79e633",
    "base_mode": "exact",
    "head_start": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "head_end": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "upstream_end": "2f79e633e205a81b01040e8c98d1e092f8d53a9e",
    "branch": "fix/2026-09-19-head-pin-test-drift"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "The acceptance test incorrectly equates an immutable issuance cutoff with the advancing current head.",
        "location": "tests/test_calibration_bracketing.py:635",
        "authority": "docs/decision_log.md:7511"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Shared-generator mechanics tests depend on a mutable operational input unrelated to their assertions.",
        "location": "tests/test_campaign_generator_core.py:103",
        "production_fence": "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The same drift also breaks tests outside the quick tier, including the cited non-ledger drift regression before its intended mutation.",
        "locations": [
          "tests/test_arm_readiness_evidence_packauth.py:561",
          "tests/test_d117_floor_qwen3_v5_generate.py:774",
          "tests/test_d117_floor_qwen3_v5_generate.py:606"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_live_issued_anchor_authenticates_and_matches_committed_head_pin tests.test_campaign_generator_core",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1, errors=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_external_pinned_input_drift_is_checked_in_derivation_mode tests.test_calibration_ledger.CalibrationLedgerTests.test_proper_prefix_of_pinned_head_refuses_as_rollback tests.test_calibration_ledger.CalibrationLedgerTests.test_unpinned_physical_extension_refuses_stale_head tests.test_calibration_ledger.CalibrationLedgerTests.test_baseline_must_be_exact_member_of_current_chain",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_contrast_references_resolve_to_matching_floor_plan_digests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/pinfix-design-probe.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python /tmp/pinfix-focused-probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 8.440s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -l 'LEDGER_HEAD_FILE_SHA256' configs/campaigns --glob generate_configs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py",
          "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
          "configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py",
          "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
          "configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "generate_configs\\.py"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short --branch && git log -1 --format='%H'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## fix/2026-09-19-head-pin-test-drift...origin/main",
          "2f79e633e205a81b01040e8c98d1e092f8d53a9e"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2f79e633e205a81b01040e8c98d1e092f8d53a9e"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only consult completed. Proposed test changes were exercised through /tmp probes; no repository patch, full quick-tier run, canonical suite, hosted-CI query, or physical-ledger verification was performed.",
      "needs": "Lead implements and verifies the exact candidate; do not describe scratch results as main or hardware validation."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A two-file quick-tier repair does not repair the independently reproduced heavier-test failures at tests/test_arm_readiness_evidence_packauth.py:561 and tests/test_d117_floor_qwen3_v5_generate.py:606.",
      "needs": "Carry explicit dispositions for these failures; use physical fixture inputs for subprocess tests."
    }
  ]
}
```

## Findings

**Recommendation:** keep the committed pin advancing, preserve generator drift refusal, and repair the tests. Production already implements the required prefix relationship. I agree with Q1(b) and fixture isolation; I disagree with redefining the existing generator file hash as the acceptance cutoff in this fix. The governing distinction is explicit in `docs/decision_log.md:7511`, and the current generator checks exact file bytes at `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`.

**F1 — Q1: the invariant is an authenticated prefix, not equality.**

For cutoff **C**, committed pin **P**, and physical ledger **L**, require:

- Matching ledger schema.
- `C.sequence <= P.sequence`.
- The chain digest at exactly `C.sequence` equals `C.head_digest`.
- The authenticated physical terminal head equals **P**, with the remaining completeness and custody checks passing.

D-109 R1.4 explicitly requires a complete, non-forked extension from the acceptance baseline to the independent current head (`docs/decision_log.md:7511`). R2.1 defines the issuance cutoff as an exact sequence/digest pair (`docs/decision_log.md:7537`). D-116 records **76 as the issuance-time head**, not a permanent maximum (`docs/decision_log.md:7992`). The append contract expressly permits reviewed, committed advancement (`docs/contracts/calibration_ledger_append.md:286`), and the runbook distinguishes the frozen registration baseline from subsequent terminal pins (`docs/phase_2/derivation_night_runbook.md:2792`).

**This requires no production correction:** `load_calibration_ledger_snapshot` checks physical-head equality at `joulewise/calibration_ledger.py:2609`, exact baseline membership at `:2623`, and rejects a baseline beyond the pinned sequence at `:2630`. V5 exercised those conditions against actual synthetic ledger bytes and a committed pin.

**CI cannot prove the actual 76→176 ancestry from the pin file alone.** Its three fields contain no intermediate chain records (`configs/calibration/calibration_ledger_head.json:1`). A sequence comparison is a necessary consistency check, not authentication.

To prove actual ancestry in CI, supply the canonical extension receipts from cutoff+1 through the current pin—or the complete ledger—and verify their sequence, predecessor and receipt hashes against both trusted endpoints. Receipt hashing is defined at `docs/contracts/calibration_ledger_append.md:98`. That witness can be a separate evidence input; it need not—and cannot prospectively—be embedded in the immutable acceptance for future appends. The existing contract requires evaluation-time chain verification, but prescribes no hosted-CI witness format (`docs/decision_log.md:7511`).

For this repair, explicitly separate:

1. Checked-in artifact authentication and head/cutoff consistency.
2. Synthetic tests proving the production chain-verification algorithm.
3. Lead-owned verification of the real physical ledger.

Do not rename a bare `<=` assertion “prefix authentication.”

**F2 — Q2 and Q5: retain generation-input byte identity; separate it from acceptance authority.**

`LEDGER_HEAD_FILE_SHA256` currently means **the exact head-pin file bytes captured for that generator’s generation inputs**. `LEDGER_HEAD_SHA256` is a different value, and acceptance identity/digests are separately pinned (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:191`, `:211`, `:2878`). Making the file hash mean the acceptance cutoff would change both the accepted inputs and the meaning of serialized `issued_ledger_head.file_sha256`.

Two corrections to the supplied premises:

- The failing mechanics tests regenerate **three live v5 generators**, through `GENERATOR_CASES`; they do not regenerate all twelve (`scripts/check_campaign_generator_core_parity.py:19`, `tests/test_campaign_generator_core.py:75`).
- Twelve generators reference the ledger path, but only **five** declare `LEDGER_HEAD_FILE_SHA256` (V6). For example, the v5 contrast generator names the path in reservation argv at `configs/campaigns/d117_contrast_v5/generate_configs.py:2134`; that reference is not itself a frozen file-hash pin.

The existing custody classification is:

| Class | Generators/packs | Correct test behavior |
|---|---|---|
| Historical snapshots | `d117_floor_qwen25_1p5b_v{1,2,3}`, `d117_floor_qwen25_7b_v{1,2,3}`, `d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}` | Preserve committed bytes. Keep historical-custody and echo/authentication tests; do not require successful regeneration against today’s operational inputs. |
| Live generator sources | `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`, `d117_contrast_v5` | Exercise regeneration mechanics with explicit fixture inputs. Separately test real input-drift refusal. |

The census and historical self-containment assertions are at `tests/test_campaign_generator_core.py:25`, `:33`, and `:203`. Frozen state belongs to the receipt, not the README wording (`configs/campaigns/d117_floor_qwen25_1p5b_v2/README.md:5`).

**A later append does not universally mean “new family generation.”** It makes regeneration against a stale pinned input refuse. It does not require rewriting an existing frozen pack. Same-ordinal draft generation remains supported; frozen current identities require preserve mode (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:314`, `:328`). MIDCAMPAIGN-CURE-GENERATION-01 concerns **non-config cures during a running campaign**, not every legitimate ledger append (`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:58`).

Also, echo success is not sufficient PACK_AUTHENTICATION evidence: the existing test explicitly rejects promoting an echo result to generator PASS (`tests/test_arm_readiness_evidence_packauth.py:509`).

A prospective design could bind scientific eligibility to an immutable acceptance cutoff while retaining independent current-head authentication. That is a coherent separate proposal. It is unnecessary for restoring these tests.

**Q3 — exact minimal fix shape.**

The quick-tier unblock touches two test files. Add the ledger regressions and repair the cited non-ledger regression in two further test files:

| File | Proposed change |
|---|---|
| `tests/test_calibration_bracketing.py:597` | Rename the test to describe artifact authentication and head consistency. Replace `:635–646` with schema equality, `pin.sequence >= cutoff.sequence`, and digest equality **when sequences are equal**. Move the fixed `76` and `08456d50…` expectations onto the r6 **cutoff**. Retain all artifact byte-pin, identity, derivation and eligibility assertions. Add a comment that this test lacks the physical chain. |
| `tests/test_campaign_generator_core.py:103` | Within `assert_generation_uses_shared_write_boundary`, provide the historical head-file fixture for ALPHA/BETA. Narrowly intercept only `sha256_file(REPO_ROOT / LEDGER_HEAD_REL)`; delegate every other path to the real function. Use fixed fixture bytes whose independently checked SHA is `6bbe2625…`, rather than returning an arbitrary expected value. Apply the same fixture to normal and mutated source paths. Leave GAMMA and the boundary observer unchanged. |
| `tests/test_calibration_ledger.py:637` | Add non-genesis, physical-chain tests using temporary ledger/custody files and a temporary Git repository with committed pins. Cover the cases below. Existing helpers are at `:169–217`. |
| `tests/test_arm_readiness_evidence_packauth.py:541` | Before emitting the temporary successor, install and commit the generation-time head fixture **only inside this test’s disposable clone**. Preserve the acceptance-file newline mutation. Strengthen the refusal assertion to name the acceptance path, ensuring ledger drift cannot satisfy the negative oracle accidentally. |

Required regression cases:

- **Advanced pin:** finalize baseline A, append/finalize B, commit B’s pin, load using A’s cutoff; authentication succeeds.
- **Wrong cutoff digest:** same valid extended ledger and committed head, wrong baseline digest; `calibration_ledger_baseline_missing`.
- **Pin below cutoff:** roll the committed fixture pin below A; refuse. Also test a self-consistent shortened ledger/pin, so refusal cannot rely only on physical-head mismatch.
- **Physical rollback:** retain the existing rollback test at `tests/test_calibration_ledger.py:563`.
- **Non-ledger drift:** retain and repair the acceptance mutation at `tests/test_arm_readiness_evidence_packauth.py:565`. Its regenerate branch must refuse while echo remains classified as echo.
- **Frozen identity:** retain the earlier preserve-mode refusal; a frozen identity can refuse before reaching input validation (`configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:270`). Test the input-drift reason on the permitted successor-generation path, as the existing regression does.

Only the live-pin-equals-cutoff assertions and their test name become obsolete. Neither core counterfactual test is obsolete; their intended assertions must remain at `tests/test_campaign_generator_core.py:120` and `:180`.

No changes are needed to production ledger code, acceptance artifacts, committed pin, generators, frozen packs or sidecars. V5 passed ten scratch tests covering the replacement assertion, all seven core tests, physical-prefix counterfactuals and repaired non-ledger regression.

**Next-pin-advance surface:** these repaired tests have no new failure solely because the pin advances again. The structural assertion tolerates advancement, and mechanics fixtures remain fixed. Real regeneration against stale generation inputs still refuses intentionally (`configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`).

**F3 — the quick-tier repair does not establish full-suite green.**

The cited packauth test currently fails at its initial successful-emission assertion, before mutating the acceptance (V2; `tests/test_arm_readiness_evidence_packauth.py:561`). A v5 floor-generation test also fails on the ledger pin (V3; `tests/test_d117_floor_qwen3_v5_generate.py:774`). Both modules exceed the quick-tier weight threshold (`scripts/test_timings.json:70`, `:137`; selection at `scripts/quick_suite.py:98`).

The broader scratch experiment exposed an additional isolation detail: an in-process hash fixture does not reach the subprocess invoked at `tests/test_d117_floor_qwen3_v5_generate.py:592`. That subprocess needs a disposable repository containing the historical input bytes and must execute its generator there. The standalone parity tool likewise regenerates from ambient inputs through `scripts/check_campaign_generator_core_parity.py:132`.

Those are separate, named test-fixture repairs; do not weaken production drift checks to conceal them.

**Q4 — authority boundary.**

The recommended test-only repair implements an existing rule and changes no production admission behavior. D-109 already mandates the baseline/current distinction, and production already enforces it (`docs/decision_log.md:7511`; `joulewise/calibration_ledger.py:2614`). It therefore needs ordinary lead review and verification, not a new process ruling merely because a mistaken test changes.

The boundary is crossed by:

- Redefining `LEDGER_HEAD_FILE_SHA256` or allowing previously refused regeneration under a moved input.
- Replacing actual chain authentication with sequence-only comparison.
- Making a new committed CI witness a mandatory issuance or pin-advancement gate.
- Altering frozen-pack, acceptance-issuance, epoch or measurement rules.

Those change the contract or process and need the applicable cold-gate/Ed route. The recorded amendment principle explicitly treats changed refusal semantics as an amendment (`docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md:14`); rule-11 roles are at `docs/orchestration.md:64`.

D-161 retains physics, evidence, pre-registration and operator-mistake protections (`docs/decision_log.md:10691`). No numerical tolerance needs adjustment here.

**Alternatives rejected:** equality contradicts D-109; pin rollback contradicts required readiness; bulk repinning/regenerating historical packs violates their custody role; acceptance-cutoff reinterpretation changes production semantics unnecessarily; sequence-only “authentication” omits the required chain proof. Authorities are respectively `docs/decision_log.md:7511`, `docs/phase_2/derivation_night_runbook.md:532`, `tests/test_campaign_generator_core.py:203`, and `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2504`.

## Residual risk

Actual 76→176 ancestry was not verified: the physical ledger was outside this consult’s permitted inputs. The harvest record locates it in the retained clone/archive (`docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:52`). The proposal removes the three reproduced quick-tier failures, but full quick-tier green remains for the lead to verify after implementation.

Green tests confer no G2-a authorization. r6 binds 25F84 (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:20`); the retained 25G83 equivalence result is FAIL (`docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:71`).

Repository unchanged. Scratch probes remain at [focused probe](/tmp/pinfix-focused-probe.py) and [broader probe](/tmp/pinfix-design-probe.py). Next exact step: implement the four-file test repair, review the negative oracles, then run the quick tier and affected modules with the heavier-test failures explicitly dispositioned.
## Opus contract refuter 07

# Opus contract-lens refuter — ledger head pin vs. acceptance cutoff vs. generator pinned inputs

Read-only. Worktree `/Users/edr/code/JouleWise-wt-pinfix-d0b83820` @ `2f79e633`.

## Recommendation

**Split by authority. Land Part A now; do NOT fixture-stub the generator core test.**

- **Part A (lead authority, clears 1 of 3 failures).** `tests/test_calibration_bracketing.py:634-646`
  asserts `cutoff == pin`, an invariant no contract promises and the production loader already
  contradicts (`joulewise/calibration_ledger.py:2621-2632`). Rewrite to the prefix invariant; add the
  anti-rollback regression **no test currently executes** (Q3-A2).
- **Part B (cold gate / Ed).** The 3 LIVE v5 generators byte-pin a file the contract licenses to
  advance every night (`…d117_floor_qwen3-1p7b_v5/generate_configs.py:2507` vs
  `docs/contracts/calibration_ledger_append.md:286-295`) — a category error, not a stale constant: it
  re-breaks after every future night. Replace the byte pin with the semantic relation (pin
  at-or-ahead-of the acceptance cutoff); drop `file_sha256` from the emitted manifest. Dropping a
  mechanism → rule 11.
- **Interim if CI must be green first:** `expectedFailure`/skip the two generator-core tests, lane id
  in the reason. A skip is honest; a fixture stub reports green while the live generator still raises.

**Rejected.** (i) Bump the constant in all 12 generators — touches the 9 FROZEN ones, authenticated
pack-tree files (`docs/process_traces/2026-09-04-fanout/00-rulings-owed.md:63-64`). (ii) Delete the
drift loop — kills the acceptance/policy/neg8/prompt pins. (iii) Roll the pin back to 76 — forbidden by
D-109 R1.4 (`docs/decision_log.md:7517-7523`); bricks §0.4
(`docs/phase_2/derivation_night_runbook.md:532-542`).

## Q1 — invariant between `ledger_cutoff` and the committed pin

**(b). The contract is not silent — it already says (b).**

D-109 R1.4, `docs/decision_log.md:7511-7516`: "The acceptance artifact pins its **baseline** ledger
head. Evaluation ALSO requires the **independent current-head pin**, verifies **one complete
non-forked chain extension from baseline to current**." A relation permitting an *extension* cannot
require equality. The only equality D-109 states is physical-vs-committed (`:7521-7523`), a different
pair. Same for the contract's typed pin relation (`docs/contracts/calibration_ledger_append.md:278-284`:
`exact`/`physical_ahead`/`physical_behind`/`diverged`, all physical-vs-committed), with `:286-295`
licensing `advance-head-pin` as routine desk work. The runbook states the decoupling outright
(`docs/phase_2/derivation_night_runbook.md:2794-2799`): the terminal pin is committed before the next
night, while the pre-registration's `[SEQ]`/`[DIGEST]` "stay as the FIRST night's pin; they are the
registration's baseline, not a per-night field."

Production already implements (b): `joulewise/calibration_ledger.py:2621-2632` verifies the baseline
digest **is** `receipts[baseline_sequence-1]["receipt_digest"]` and refuses when
`baseline_sequence > pinned_sequence`; `joulewise/calibration_bracketing.py:2020-2027` supplies the
acceptance cutoff as that baseline. (a) is refuted by contract, runbook and code; it held only because
the pin had not moved since `a816036f`.

**Verifying it in CI:** the digest half is unverifiable — the physical ledger is git-ignored and
absent, and no committed prefix witness exists; only **ordering and schema** are checkable from
committed bytes. **Do not invent a prefix-witness artifact**: new contract surface, and the digest half
is already enforced twice at run time (`calibration_ledger.py:2609-2613`, `:2626-2632`). My one
amendment to the lead's (b): the test must **name the weaker property it proves** — today's failure
exists because `..._matches_committed_head_pin` named an unratified invariant confidently.

## Q2 — what `LEDGER_HEAD_FILE_SHA256` should mean

Neither option as posed. The generator **already carries both meanings as separate constants**:
`LEDGER_HEAD_SHA256 = 08456d50…` (`…qwen3-1p7b_v5/generate_configs.py:214-216`) is exactly the
acceptance cutoff digest (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:14`, verified
76 / `08456d50…`); `LEDGER_HEAD_FILE_SHA256 = 6bbe2625…` (`:211-213`) is the byte hash of the *live,
mutable* pin file. The acceptance binding is already present and correct; the file sha is a redundant
byte pin on an append-advancing file. Re-pointing it at "the acceptance" (the lead's leaning) is not
expressible — the cutoff is not a file — and duplicates `LEDGER_HEAD_SHA256`. **Delete it.**

It is inert: the pack passes `--head-pin repo_path(LEDGER_HEAD_REL)` (`:1625`), a **runtime** path
resolved at campaign execution, so pack behaviour never depended on generation-time bytes; and emitted
`issued_ledger_head.file_sha256` (`:2886-2890`) has **zero consumers** (`grep -rn issued_ledger_head`
outside `configs/` and `docs/` is empty). The pin in force at arm is recorded in arm evidence
(`…activation-d8ca3a36/21-arm-evidence-n1-20260919/night_probe_receipt.json`), so no provenance is lost.

**Frozen vs live.** Frozen = the 9 at `tests/test_campaign_generator_core.py:33-45`, each with a
committed pack (`…d117_floor_qwen25_1p5b_v2/plan_tree.json:23`); echo mode only; never edit. Live = the
3 v5 (`:25-31`): `d117_floor_qwen3-1p7b_v5/` and `-8b_v5/` hold **only** `generate_configs.py`, so
editing them invalidates no custody. **Correction to brief fact 2:** the failing tests do not run all
12; `GENERATOR_CASES` (`scripts/check_campaign_generator_core_parity.py:19-34`) is the 3 live ones only.

**Correct test behaviour:** `test_campaign_generator_core` proves the shared write boundary
(`:137-142`), not input freshness. Stubbing the head pin there — as `fixture_prefill_pin` stubs the
prompt pin (`:78-83`) — is legitimate **only after** the live generator stops refusing. The prompt pin
is stubbed because it is an *external* artifact the test must synthesize; the ledger head would be
stubbed to hide a real refusal of a real repo file.

## Q3 — minimal fix-forward

**A1 `tests/test_calibration_bracketing.py:634-646`** — replace `assertEqual(cutoff, pin)` and both
literals with: `cutoff["sequence"] <= pin["sequence"]`; `cutoff["ledger_schema"] ==
pin["ledger_schema"]`; `pin["head_digest"]` matches `[0-9a-f]{64}`; plus a separate genesis floor
asserted against the **r6 path** (not the active default): r6's cutoff is exactly 76 / `08456d50…` and
`pin["sequence"] >= 76`. Rename to `..._is_a_prefix_of_the_committed_head_pin`; docstring says CI
proves ordering + schema only, digest-in-chain being loader-enforced.

**A2 `tests/test_calibration_ledger.py`** — every `baseline_sequence=` in `tests/test_calibration*.py`
is 0, 1, `cutoff["sequence"]`, `plan.final_sequence`, `imported.sequence` or `base_sequence`: **no test
drives `baseline_sequence > pinned_sequence`**, so the D-109 anti-rollback branch at
`calibration_ledger.py:2630` has never executed. Add pin at N, cutoff at N+1 →
`calibration_ledger_baseline_missing` (complements `:637-645`, digest mismatch). This is the fence a
green-CI fix is most likely to be *believed* to cover.

**B1 (gated), the 3 live v5 generators** — remove `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)` from the
drift tuple (`…1p7b_v5:2503-2511`); immediately after, load the live pin and the acceptance artifact's
`ledger_cutoff` and refuse unless schemas match and `pin["sequence"] >= cutoff["sequence"]` (message
`ledger head pin behind the acceptance cutoff: <path>`). Drop `"file_sha256"` from
`issued_ledger_head` (`:2886-2890`), keep `head_sha256 = LEDGER_HEAD_SHA256`, assert in-generator it
equals `cutoff["head_digest"]`, delete `LEDGER_HEAD_FILE_SHA256`. **B2 frozen 9: no diff at all.**

**Regressions with B1:** (i) pin advanced past cutoff → `generate` succeeds, output byte-identical to
the pre-advance emit; (ii) pin rolled back below cutoff → refuses with the new message; (iii) pin
`ledger_schema` altered → refuses; (iv) drifted NON-ledger pinned input (acceptance bytes) on
regenerate → still `pinned input drifted`, preserve mode still exit 0 (shape proven at
`tests/test_arm_readiness_evidence_packauth.py:570-592`).



**Obsolete:** `assertEqual(cutoff, pin)` and the two pin literals (`:640-646`);
`LEDGER_HEAD_FILE_SHA256` in the 3 live generators.

**False-failure surface on the next pin advance.** Part A: none (226 > 76, schema unchanged). B1: none
— pack bytes no longer depend on the pin. Residual, named: (1) a successor acceptance with a cutoff
above 76 still passes A1, the floor being asserted against the r6 path; (2) `acceptance_pin()`
(`…1p7b_v5:492-512`) resolves to r6 in regenerate mode, so a successor issuance drifts the *acceptance*
pin and forces a new generation — intended, not a false failure; (3) under the FAIL route the pin
advances after nights 2 and 3, re-breaking the generator-core tests under today's code but not under B1.

## Q4 — authority boundary

- **Lead:** A1, A2. Correcting a test that over-asserted beyond D-109 R1.4 is not a contract change;
  no mechanism is dropped and a missing regression is added. Record as a defect note, not a ruling.
- **Cold gate / Ed (rule 11):** B1. Removing `calibration_ledger_head.json` from a pack's pinned-input
  set and `file_sha256` from the emitted manifest **drops a mechanism** and changes what an armed
  window's pack asserts about calibration authority — inside rule 11's enumerated prohibitions, and
  hardware/claim-adjacent. Packet question, narrow: *is a monotonically-advancing pin file admissible
  as a frozen byte pin in a generator's drift set?* Cite D-109 R1.4 and contract `:278-295`.
- **Ed only:** any change to the committed pin value or `advance-head-pin` semantics. Not proposed.
- **Line:** editing `tests/` to match an adopted contract clause = lead; editing
  `configs/campaigns/*/generate_configs.py` pin sets or any emitted-manifest field = gated. Neither
  part amends the contract text; B1 conforms code to `:278-295`.

## Q5 — where the lead is wrong

Agreed on Q1 **(b)**, amended: CI can prove only ordering + schema, and the test name must say so.

**Strongest disagreement — the fixture stub.** It makes CI green while the live v5 generators still
raise `ValueError: pinned input drifted` for the operator. Those packs are **unemitted** (only
`generate_configs.py` on disk), so emitting the next window's pack *requires* a successful regenerate.
The stub converts a loud, correctly-timed CI failure into a landmine that detonates at arm time, inside
a scarce quiet window, against the speed-pass directive (arm-to-t0 ≈ 10 min). It also weakens the test:
the generator-core suite is the only executed end-to-end proof the live generators run, and stubbing
the one input that refuses removes the signal that the pin set is unsound. The counter — "the
equivalence FAILED, so a successor acceptance forces a new generation anyway" — is true but does not
save the stub: under the FAIL route the pin advances after nights 2 and 3 too (runbook `:2794-2799`),
so a byte pin on the head file breaks again after every night, forever. Structural, not stale-constant.

**Second disagreement — Q2 framing.** "Acceptance cutoff" is the right semantics, wrong edit: that
binding already exists as `LEDGER_HEAD_SHA256`.

**Fences a naive green-CI fix would remove.** (1) `cutoff.sequence <= pin.sequence` — D-109
anti-rollback at `calibration_ledger.py:2630`, **unproven by any test**; deleting the bracketing test
leaves it with no committed-bytes guard. (2) The drift loop's other four pins. (3) The 9 frozen
generators' custody. (4) §0.4 head-equals-pin, if the pin is rolled back to 76.

## Commands run (all read-only)

- `git log -1 --oneline` → `2f79e633`; `git log -5 --` the pin file → `83831134`, `a816036f` (76), `e39b45e6` (126), `1278b9f7` (176); `cat` pin → 176 / `0f7609ae…`.
- `sed -n` reads of every file:line cited above (contract, decision_log, runbook, `calibration_bracketing.py`, `calibration_ledger.py`, the v5 + v2 generators, three test files, the parity script, `00-rulings-owed.md`).
- greps: `ledger_cutoff` → 6 production consumers; `calibration_ledger_head` in generators → 12 files, all pinning `6bbe2625…`; `issued_ledger_head` outside `configs/`+`docs/` → **empty, no consumers**.
- `python -c`: live pin file sha `6b2d37c8…` ≠ pinned `6bbe2625…`; r6 cutoff 76 / `08456d50…`, epoch 25F84. `ls` of the v5 pack dirs → no committed pack tree for either floor pack.
- `python -m unittest tests.test_campaign_generator_core -v` → **FAILED (errors=2)**: `pinned input drifted: configs/calibration/calibration_ledger_head.json` at `…qwen3-1p7b_v5/generate_configs.py:2511`.
- `python -m unittest …test_live_issued_anchor_authenticates_and_matches_committed_head_pin` → **FAILED**: `{76, 08456d50…} != {176, 0f7609ae…}`.
- `python` scan of all `baseline_sequence=` in `tests/test_calibration*.py` → **no case with baseline > pin**.
- Nothing written outside `/tmp/magistrate-d0b83820/`; no git state changed; no sudo/powermetrics/capture.

## Adjudication 07a

# Record 07a — adjudication of consult 07 (Astra xhigh, record 07) and the Opus contract refuter (record 07-opus): committed head pin vs. acceptance cutoff vs. generator pinned inputs (lead, 2026-09-19 08:1x PDT)

## What the two seats agreed on (adopted)

1. **Q1 = (b), a prefix relation, and the contract already says so.** D-109 R1.4 requires "one complete non-forked chain extension from baseline to current" (`docs/decision_log.md:7511-7516`); production enforces it at load time (`joulewise/calibration_ledger.py:2609-2632`: physical head = committed pin; baseline digest = the receipt digest at the cutoff sequence; refuse when `baseline_sequence > pinned_sequence`). The equality the failing test asserts (`tests/test_calibration_bracketing.py:634-646`) is an unratified invariant that held only because the pin had not moved since D-116. Executed this session: `epoch_equivalence_check` loaded the 176-row ledger under `require_committed_pin=True` with the r6 acceptance (cutoff 76 / `08456d50…`) and authenticated it — that is the 76 → 176 ancestry proof on the real ledger, in the n2 clone (harvest record 01).
2. **CI can prove ordering + schema only** (the physical ledger is git-ignored and absent); the rewritten test must say so in its name and docstring. No prefix-witness artifact is invented (both seats; Opus: new contract surface; Astra: cannot be embedded prospectively).
3. **The D-109 anti-rollback branch has no executing test** (Opus A2: every `baseline_sequence` in `tests/test_calibration*.py` is ≤ the pin). Add it.
4. The committed pin stays at 176; the nine frozen generators and their packs are not touched; the drift loop's other four pins are not weakened; the pin is never rolled back (D-109 R1.4; runbook §0.4).
5. Only the three LIVE v5 generators are exercised by the failing mechanics tests (`GENERATOR_CASES`), and only five generators declare `LEDGER_HEAD_FILE_SHA256` (lead-verified: `grep -l "^LEDGER_HEAD_FILE_SHA256"` → the three qwen25_1p5b historical + the two v5 floor generators). Brief 07's "twelve generators pin the file" was over-counted: twelve reference the path, five byte-pin it.

## Where they disagreed, and the ruling

**The generator-core mechanics test.** Astra: supply the generation-time head-file bytes as a fixture (intercept only `sha256_file(REPO_ROOT / LEDGER_HEAD_REL)`), because the test proves the shared write boundary, not input freshness, and the real drift refusal stays in production. Opus: do not stub — the live v5 packs are unemitted, so the next emission must regenerate and will refuse; a byte pin on a file the contract licenses to advance after every night is a category error (B1), and dropping that pin from the generators' drift set drops a mechanism → rule 11; interim = `expectedFailure` with a lane id.

**Ruled: Astra's fixture, with Opus's structural finding registered as a gated lane.** Reasons: (i) the mechanics test's assertion is the write boundary; a fixture that supplies the generator's declared inputs tests the generator as the function of its inputs it claims to be, and keeps the only end-to-end execution of the live generators in CI (an `expectedFailure` loses that proof until B1 lands); (ii) the operator-facing refusal at the next v5 emission is loud and names the file (`pinned input drifted: …calibration_ledger_head.json`), and the next v5 emission is not near (r6 binds 25F84; the equivalence check FAILED; no G2-a can be generated on this machine until an acceptance covers 25G83), so the "landmine inside a scarce window" cost is bounded to one reviewed constant bump, if it is ever paid before B1; (iii) B1 (remove the byte pin from the live generators' drift set, drop `issued_ledger_head.file_sha256`, assert the semantic relation instead) is exactly a rule-11 question — dropping a mechanism from what an armed pack asserts about calibration authority — and goes to the cold gate as lane **GENERATOR-HEAD-FILE-BYTE-PIN-01** (queue data, not ruled here). Opus's second point is accepted as a correction to brief 07: the acceptance binding already exists as `LEDGER_HEAD_SHA256`; "re-point the file sha at the acceptance" is not an edit that exists.

**The heavier-tier failures.** Astra found two more failures outside the quick tier on the same cause (`tests/test_arm_readiness_evidence_packauth.py:561` and `tests/test_d117_floor_qwen3_v5_generate.py:774`; the subprocess path needs a disposable repository carrying the historical input bytes, since an in-process fixture does not reach it). Both are in scope for the repair seat; if either proves larger than a fixture, the seat early-returns and the lead lanes it.

## Authority

Test-only repair conforming tests to an adopted contract clause (D-109 R1.4) plus a missing regression: lead authority (both seats, Q4). No production code, no generator, no committed pin, no frozen pack, no contract text changes. B1 is NOT implemented here.

## Findings for the record

- Hosted CI on main has been red on the quick tier since `22b92ec7` (03:12 PDT); the four green runs after it skipped the quick tier under the docs-only filter, so the badge misled. Lane **CI-DOCS-ONLY-SKIP-MASKS-RED-01** (queue data): a docs-only push should re-report the last full result, or the harvest record should check the last FULL run.
- The night-one harvest recorded "CI green" for `30118742` and did not re-check at `22b92ec7` after the pin landed; the n2 landing repeated the shape. Bench note for runbook §3 item 4: run the quick tier locally on the pin commit before landing (Ed's 09-16 ruling requires green LOCAL replay + quick tier; the pin commit is not docs-only).
