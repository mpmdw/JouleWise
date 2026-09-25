```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R2b cures list-kind and calibration presentation handling, but retains incompatible routing, read, and witness obligations; G0 also requires a pre-commissioning ruling.",
  "workspace": {
    "base_requested": "bee658c5",
    "base_mode": "exact",
    "head_start": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "head_end": "bee658c5acc4dd860a382317c40ec4421587a13a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "R1b selects unknown strings into R3's non-base refusal path, but G1 includes unknown-string presentation cases where base succeeds."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "R1b's presentation read restriction remains unqualified, contradicting A1 authentication and the pinned third-row witnesses."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "text": "R3's base-checks-before-handler order produces KeyError on the incomplete handler-less witness states that G4b requires to refuse typed."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "text": "A1 applies preparation-state selection and binding authentication to every evidence_night site, including pre-state path construction and the function that establishes those bindings."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "text": "The frozen projected corpus has zero wrapper=calibration plus c5=calibration cases for all five installer operations and driver.probe_dispatch; G0 requires NEEDS_RULING before P."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B /tmp/278ebc9e/r2bref/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PROBES_OK",
          "R3_CANDIDATE_CHECKS_FIRST => KeyError: 'roots_under'",
          "PROBES_COMPLETE",
          "PRESTATE_LOCATIONS third_kind=test_night handler=None returned=['custody_root', 'measurement_root', 'plan_id', 'staging']",
          "FINAL_PROBES_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FINAL_PROBES_OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "bee658c5acc4dd860a382317c40ec4421587a13a"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bee658c5acc4dd860a382317c40ec4421587a13a"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "P would have to choose between conflicting obligations. G0's zero-case stop condition is also established.",
      "needs": "Return these counterexamples to the magistrate before commissioning P; resolve routing domains, authentication exceptions, handler-check order, pre-state APIs, and calibration coverage."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Executed isolated functions extracted with git show and enumerated all frozen projected jobs; did not run the full differential harness or module suite.",
      "needs": ""
    }
  ]
}
```

## Findings

**D1 — disposition of 84b’s findings**

| Prior finding | Cured by R2b? |
|---|---|
| F1 | **Partly:** A3 supplies the missing hint, but R1b still forbids reads needed by A1 and the third-row witnesses. |
| F2 | **Yes for calibration presentation:** A2/R5b explicitly preserve base results; executed subject and render probes confirm what those results are. |
| F3 | **Yes:** R4b sends list-valued kinds to the exact base path, including successful presentation. |
| F4 | **Partly:** G4b pins assertions and adds independent witnesses, but their required behavior conflicts with R3’s ordering. |
| F5 | **Yes:** scratch mutations, lead-owned report commitment, and the prohibition on automatic further rounds are explicit. |
| F6 | **Partly:** G0 moves the check before P and supplies criteria; enumeration now establishes its zero-case stop condition. |

**D2 — the obligations cannot all hold as written.** References below use line numbers in the [addendum](</Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/83-coldgate-packet-b0-method/30-addendum/21-coldgate-fable-b0-addendum-ruling.md>).

| ID | Severity | Counterexample and exact proposed replacement |
|---|---|---|
| **F1** | **BLOCKER** | **Unknown strings still break G1.** Lines 44, 54, 58 and 62 route `"unknown_kind"` outside `BASE_KINDS` and require refusal. Frozen job `single.kind=unknown / evidence.notice_subject` exists; base returns the idle subject. R4b only cures non-strings. **Replace R1b’s selector definition and qualify R3:** “`select_kind(state)` never raises. It returns the string kind only when that kind is registered in `NIGHT_KINDS`; otherwise it returns `None`. An unregistered string executes the exact base path, preserving that site's success or refusal. Only a registered kind outside `BASE_KINDS` enters the new branch. This legacy fallback grants no admission or handler authority and overrides the no-handler requirement for unregistered presentation hints.” |
| **F2** | **BLOCKER** | **The read prohibition still contradicts authentication.** Line 54 says presentation functions perform no filesystem read absent at the same base site, without limiting that sentence to the base branch. A1 requires wrapper, sidecar and source authentication; G4b requires third-row subjects. The executed third-row subject reads all three files, whereas base `notice_subject` reads none. G3b permits such reads, so it does not repair R1b’s prohibition. **Replace that presentation sentence:** “When the selector is `None` or in `BASE_KINDS`, each presentation function performs exactly the base reads, in base order. For a registered kind outside `BASE_KINDS`, A1 authentication reads are explicitly permitted before row-specific output. The base-read restriction applies only to the base branch.” |
| **F3** | **BLOCKER** | **‘Base checks … then refuses’ cannot satisfy the pinned handler-less witnesses.** Line 58 orders base checks before the handler refusal. The first pinned witness supplies only chain-source bindings; base `render_notice` therefore raises `KeyError('registration_path')` before the required `Refused("notice has no approved evidence handler")`. Its minimal `prepare.json` similarly makes base `candidate_state` raise `KeyError('roots_under')`. Adding `kind` or changing refusal regexes cannot fix either exception. **Replace R3(+):** “For a registered non-base row, reject an unsupported site handler with the site's typed refusal before accessing fields required only by that handler. For supported handlers, preserve base validation order with row fields substituted. `notice_subject` is explicitly exempt from the handler requirement: after A1 authentication it may format the row's label even when `row.handler is None`. This exception also governs R5b and brief 10 §1(f).” |
| **F4** | **BLOCKER** | **A1 over-applies its state/binding requirement.** Line 44 governs “every” `evidence_night.py` site and allows non-base row-specific output only after authentication against `state["bindings"]`. Yet pinned lines 454–456 call `locations(..., third.kind)` without a state and require third-row paths. Also, base `prepare` obtains `state["bindings"]` by calling `sealed_candidate` (`2ea6a7ec:…:546`); that producer cannot require its own not-yet-produced bindings. **Replace A1’s scope sentence and append exceptions:** “At sites receiving an existing preparation state, selection uses its `kind` field. Before state or bindings exist, `prepare`, `locations`, and `prior_records` may use an explicit requested-kind hint for admission checks, deterministic path construction, and discovery; those operations grant no execution authority. `sealed_candidate` establishes bindings through wrapper/source validation and is not required to consume the bindings it is producing. Existing-state presentation requires authentication against those bindings. All legacy calls retain their exact base behavior.” |
| **F5** | **MATERIAL** | **G0 currently stops commissioning.** Line 78 requires both `wrapper="calibration"` and coherent `c5="calibration"` cases for every driver/installer operation. All five installer operations and `driver.probe_dispatch` project away `c5`, yielding **zero** such jobs. The six remaining driver operations each have one syntactic pair, whose coherence and branch reach still require execution. **Append to G0:** “At `eb8d745f`, G0 is NEEDS_RULING: the five installer operations and `driver.probe_dispatch` have no projected case containing both required discriminants. Do not commission P. A new magistrate ruling must define operation-specific calibration evidence and authorize any supplementary fixtures; neither P nor K may waive the criterion or edit the frozen G1 corpus.” |

**D3 — choices reserved to the magistrate.** P cannot decide whether unknown hints preserve legacy success, whether authentication overrides R1b’s read prohibition, whether unsupported handlers refuse before base checks, or which pre-state operations are exempt from A1. I recommend the replacements above. For G0, retain frozen G1 and separately authorize operation-specific calibration fixtures if the magistrate chooses to proceed.

**Probe tails** — replay with [probe.py](/tmp/278ebc9e/r2bref/probe.py):

```text
CASESET observations=99443
BASE_SUBJECT kind=[] => NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1
BASE_SUBJECT kind='calibration' => NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1
BASE_SUBJECT kind='unknown_kind' => NIGHT NOTICE — x (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 1
BASE_RENDER calibration idle_subject=True reads=["read_bytes:registration.json", "read_text:plan.json"]
BASE_PAYLOAD calibration=calibration reads=["read_text:chain.zsh"]
THIRD_SUBJECT handler=None => NIGHT NOTICE — test-night-1 (TEST; TEST_CLASS) — attempt 1 reads=["read_bytes:chain.zsh", "read_text:chain.zsh.sha256", "read_bytes:source.zsh"]
PINNED_RENDER => Refused: notice has no approved evidence handler
R3_BASE_CHECKS_FIRST => KeyError: 'registration_path'
R3_CANDIDATE_CHECKS_FIRST => KeyError: 'roots_under'
```

```text
G0_PROJECTED installer.render count=0 ids=[]
G0_PROJECTED installer.receipt_validation count=0 ids=[]
G0_PROJECTED installer.uninstall count=0 ids=[]
G0_PROJECTED installer.veto count=0 ids=[]
G0_PROJECTED installer.verify count=0 ids=[]
G0_PROJECTED driver.probe_dispatch count=0 ids=[]
```

## Residual risk

These are specification counterexamples, not verification of an R2b implementation. The probes executed extracted revision-specific functions with isolated fixtures and dependency adapters. The 99,443 figure is corpus enumeration, not a completed parity run. No repository files changed; no hardware or lifecycle commands ran.