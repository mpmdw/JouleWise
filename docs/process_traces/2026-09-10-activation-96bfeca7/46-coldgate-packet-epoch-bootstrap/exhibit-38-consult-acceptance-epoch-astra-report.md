```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed mandatory epoch refusal; no 25G83 observations exist in the sequence-76 ledger, and new-epoch capture plus issuance requires a governed bootstrap/rollover mechanism before G2-a.",
  "workspace": {
    "base_requested": "d84da72e85e94cdb1e3364597da8ac17f295f7ed",
    "base_mode": "informational",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import json; from pathlib import Path; from scripts.validate_powermetrics_fiducial import _derive_preflight_systematic_screen_s, _AcceptancePreflightError; a=json.loads(Path(\"configs/calibration/calibration_acceptance_d079_v2_n17_r6.json\").read_text()); e=a[\"identity_epoch\"]; print(\"25F84 comparator\",_derive_preflight_systematic_screen_s(e)); e={**e,\"os_build\":\"25G83\"};\ntry: _derive_preflight_systematic_screen_s(e)\nexcept _AcceptancePreflightError as x: print(\"25G83\",x.reason,x.context)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "25F84 comparator 0.032898493715362",
          "25G83 acceptance_artifact_epoch_mismatch {'stale_fields': ['os_build']}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "25G83 acceptance_artifact_epoch_mismatch.*os_build"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib,collections; p=pathlib.Path(\"/Users/edr/JouleWise-measurement-v5-20260910-d84da72e/runs/calibration_observation_ledger.jsonl\"); rows=[json.loads(s) for s in p.read_text().splitlines()]; print(\"receipts\",len(rows)); print(\"epochs\",dict(collections.Counter(r[\"identity_epoch\"][\"os_build\"] for r in rows))); print(\"finalizations\",sum(\"finalization\" in r[\"event\"] for r in rows)); print(\"last_capture\",rows[-1][\"capture_wall_time_s\"]); print(\"fixture_equal\",p.read_bytes()==pathlib.Path(\"tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl\").read_bytes())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "receipts 76",
          "epochs {'25F84': 76}",
          "finalizations 38",
          "last_capture 1785592112.1952288",
          "fixture_equal True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fixture_equal True"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import hashlib,json,pathlib; p=pathlib.Path(\"/usr/bin/powermetrics\"); current=hashlib.sha256(p.read_bytes()).hexdigest(); r=json.loads(pathlib.Path(\"tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl\").read_text().splitlines()[-1]); old=r[\"t1_bindings\"][\"powermetrics_sha256\"]; print(\"historical_powermetrics_sha256\",old); print(\"current_powermetrics_sha256\",current); print(\"binary_changed\",old!=current)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "historical_powermetrics_sha256 d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69",
          "current_powermetrics_sha256 b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5",
          "binary_changed True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "binary_changed True"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the live calibration writer requires an issued matching-epoch acceptance before capture; current issuance validation also assumes a single-epoch, historical-import-only baseline. There is no installed new-epoch bootstrap/rollover route.",
      "needs": "Cold gate must rule the nonclaim derivation-capture mechanism, prospective corpus design and size, ledger rollover semantics, successor identity authority, and atomic fan-out; Ed must resolve any amendment to his metrology rules, including the retained D-125 floor conflict."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The supplied checkout is detached at 078a13a4, older than bench head d84da72e. Relevant later files were inspected through the local d84da72e Git object; origin/main remained d84da72e. No checkout was moved.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "blocking",
      "text": "Both OS build and the powermetrics executable differ from the historical calibration bindings. No sequence-76 observation covers either current binding.",
      "needs": "Acquire and authenticate a ruled new-epoch derivation corpus, then issue and consume a matching acceptance prospectively."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only consult: no hardware capture, custody replay, canonical suite, edits, or Git writes. Night custody and the rehearsal checkout were not accessed. hw.model sysctl was sandbox-denied; the hardware-model comparison uses the supplied bench fact.",
      "needs": "Lead owns subsequent custody verification, implementation checks and agent-free live validation."
    }
  ]
}
```

## Causal chain

The machine now reports `25G83`; the active r6 acceptance binds `25F84`. The producer obtains the live epoch and calls the authenticated preflight derivation, which correctly refuses before writing the window inventory. Therefore `check → input_inventory_unreadable` is a downstream consequence, not a separate failure. The isolated read-only replay reproduced exactly `stale_fields=['os_build']`.

Relevant code is unchanged between this checkout and bench head except where identified below. References to the September 10 activation records were read at `d84da72e`.

## Remediation

**Q1. This is a required physics/evidence-transfer refusal.**

D-102 states:

> “Freshness = exact identity epoch, no calendar hard expiry: the artifact binds {os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}; any change → calibration_acceptance_bound_stale.”

It immediately requires prospective re-derivation after an identity change and forbids fitting the threshold to the observation it judges. See [decision_log.md:6474](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/decision_log.md:6474).

This is implemented consistently:

- The six fields, including `os_build`, are defined in [calibration_ledger.py:100](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_ledger.py:100); reservations require the complete vector at `:774`.
- Preflight compares the supplied live vector with the issued artifact at [validate_powermetrics_fiducial.py:394](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/validate_powermetrics_fiducial.py:394).
- Bracket evaluation independently compares the measured identity and returns stale at [calibration_bracketing.py:1531](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_bracketing.py:1531).
- T1 explicitly requires calibration and collection to use the same OS build **and powermetrics binary**. The binding contract says “any bound-field change invalidates the calibration and a new run is required.” See [powermetrics_fiducial.md:77](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/powermetrics_fiducial.md:77) and `:163`.

D-079 establishes provenance-bound screens; D-102 makes freshness executable; D-138 governs changed estimator inputs and successor issuance. D-161 preserves fail-closed physics/evidence and preregistration guards ([decision_log.md:10399](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/decision_log.md:10399)). The methodology’s environment checks do not replace those instrument bindings ([measurement_methodology.md:38](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/measurement_methodology.md:38)).

**No cross-OS acceptance-transfer test or equivalence exception is defined.** Replaying old raw evidence under corrected estimator code is an established procedure; it does not demonstrate behavior of a different OS/binary. A new transfer exception would need a separately ruled evidence protocol. The refusal establishes missing transfer evidence, not proof that the updated instrument performs worse.

**Q2. The route requires governed bootstrap work before the capture night.**

The available tools do less than “collect 17, run an issuer” suggests:

| Tool | Actual capability and limitation |
|---|---|
| `scripts/validate_powermetrics_fiducial.py --allow-live` | Captures one observation, either standalone or in a predeclared bracket slot. **Both paths first require the current matching-epoch acceptance** at `:1701–1720`. Thus standalone capture currently hits the same bootstrap problem. |
| Its `--rederive-from … --output …` mode | Re-emits compatible **40-pulse v1/v2** validation evidence. It neither collects new evidence nor derives a new 59-pulse acceptance: `:1099–1117`, `:1625–1640`. |
| `scripts/calibration_ledger_bootstrap.py --prepare-issued-artifact` | Prepares exact issuance bytes from an authenticated historical-import plan and pinned template; the mode does not write the acceptance. Historical import is **genesis-only**, not a way to add future observations to this existing ledger. [calibration_ledger.md:15](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/calibration_ledger.md:15), `:253`. |
| `scripts/reissue_calibration_acceptance.py` | Produces `candidate_not_issued=true`, retaining the predecessor’s members and changing code/protocol pins. Changed members, thresholds or science-facing fields produce `STOP`. It has no new-epoch/new-corpus option. [reissue_calibration_acceptance.py:249](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/reissue_calibration_acceptance.py:249), `:479`, `:552`. |
| Historical bespoke derivation/build scripts | D-145 explicitly says the generic reissue tool cannot check v3 generations because it compares stored scalars. The r3–r6 route used bespoke raw-evidence derivation/build scripts; execution records name scratch `build_r5.py` and `build_r6.py`. These are precedents, not an installed general issuer. [decision_log.md:187](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/decision_log.md:187); `docs/process_traces/2026-08-19-refreeze-execution/reports/S1-fix2b-report.md:166`. |
| `tests/verify_calibration_acceptance_corpus.py` | Generation-indexed verification of the member table and statistics; rejects an unregistered generation. Verification support, not an issuer. [verify_calibration_acceptance_corpus.py:19](/Users/edr/code/JouleWise-wt-gate-sweep-b/tests/verify_calibration_acceptance_corpus.py:19), `:70`. |

The `issue_*` scripts presently found under `scripts/` issue statistics and the G2-a prompt pin, not a D-079 acceptance. `derive_estate_anchors.py` likewise does not issue this acceptance.

**Observation count:** r6 contains **17 retained calibration observations**, each with 59 measured pulses, plus three warmups. Its 17 arose from re-deriving the original 19-member corpus and excluding two unsound clock-anchor members; it is not a standing minimum for every new epoch. The cold science review explicitly explains that reduction ([03-cold-science-review.md:68](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:68)); the artifact records the selection at [calibration_acceptance_d079_v2_n17_r6.json:47](/Users/edr/code/JouleWise-wt-gate-sweep-b/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:47).

The new epoch therefore needs a **prospectively ruled sample size, sampling schedule, exclusion rules and stopping rule**. Seventeen captures in one session are not automatically equivalent to the historical multi-day repeatability sample.

For planning **if n=17 is ruled**:

- 17 × 59 = **1,003 measured pulses**, plus **51 warmups**.
- At the supplied **4–8 minutes per observation**, capture time is **68–136 minutes**.
- One initial ten-minute settle gives **78–146 minutes** before other overhead; ten minutes before every observation would instead give **238–306 minutes**.
- Two observations per ordinary bracket would require **nine windows/18 observations**, before invalid captures. That is arithmetic, not an authorized substitute sampling plan.
- The 59-pulse rationale is separate: `1 − 0.95**59 = 0.9515054747505769`; it concerns the within-observation calibration bound, not the required number of observations. Protocol: [powermetrics_fiducial.md:27](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/powermetrics_fiducial.md:27), `:58`.

All such captures belong to **agent-free `[QUIET-MAC]` work**. This denotes machine state, not necessarily darkness; the existing unattended schedule adds calendar constraints.

There is **no `CALIBRATION_ONLY` night class**. The installed classes are `DIAGNOSTIC_NO_PACK`, `REHEARSAL_STUB`, and `TRANSACTION_PACK` ([night_gate.py:27](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/night_gate.py:27)). A separately reviewed derivation-only chain could be proposed under `DIAGNOSTIC_NO_PACK`; the class does not currently solve the writer’s acceptance prerequisite. Riding ordinary pack pre/post brackets also cannot bootstrap an acceptance that those brackets already require.

The ordered route is:

| Step | Owner | Required result | Conditional calendar, PDT |
|---|---|---|---|
| 1. Rule the bootstrap and rollover | **Cold gate**, paired contract reviewer; **Ed** for changes to his scientific rules | Rule how new-epoch observations can be captured without licensing G2-a/claims; freeze corpus design and stopping/disposition rules; rule multi-epoch ledger handling and successor identity authority. Keep the current refusal intact. | Desk work from **Sep 10**. No capture date is assured until this closes. |
| 2. Implement and review that mechanism | **Magistrate**, normal implementation/review pipeline | A dedicated, nonclaim derivation route preserving reservations, raw evidence, all failures and epoch identity; new-generation validation/issuance support; focused and canonical checks. | Sep 10–11 **only if scope and review fit**; otherwise slide the schedule. |
| 3. Finish the existing rehearsal and prepare the derivation night | **Magistrate** | Accept the actual Sep 11 rehearsal harvest, clear ownership, retire its stub, publish a fresh plan/notice and install from its pinned measurement checkout. | Earliest ordinary arm opportunity: **Sep 11, 03:00–06:30**, after rehearsal clearance. |
| 4. Capture the ruled corpus | **Ed-hardware lane**, executed by the reviewed unattended driver; all agents absent | Current `25G83`/binary bindings, fixed protocol, complete capture/disposition custody. No G2-a outcomes used to fit the acceptance. | Earliest ordinary capture night: **Sep 12**, conditional on steps 1–3. Replaces the proposed Sep 12 G2-a allocation. |
| 5. Harvest, derive and adjudicate | **Magistrate + cold science gate**; **Ed** for retained reserved questions | Authenticate the complete ledger extension and raw corpus; derive decimal statistics, quantiles, screens, budget and triggers; independently replay. Resolve the existing D-125 screen-floor conflict before selecting successor semantics. | **Sep 12 desk**, optimistically; more nights if the ruled design or observed failures require them. |
| 6. Land the atomic successor transaction | **Magistrate**, after gates | Issue the new acceptance and all dependent pins together; retain prior artifacts unchanged; include staged R2; complete final verification and clone proof. | **Sep 12–13**, conditional on clean review. |
| 7. Bind and arm G2-a | **Magistrate** | Rebuild live vectors, inventory, calibration plan and chain screen; `bind-window` and `check` pass; fresh head/notice/plan and normal night gates. | Practical planning target: **arm Sep 13 → first G2-a Sep 14**. |
| 8. Run and harvest G2-a | **Agent-free driver**, then **magistrate** | Fresh pre/post brackets, the full probe ladder, preserved terminal ledger boundary, followed by desk selection/prompt-pin work. | **Sep 14**, or later if any prerequisite slips. |

This is a **conditional planning scenario**, not a newly ruled calendar. Sep 13 G2-a is only technically possible if corpus harvest, scientific review, issuance, fan-out, verification and arming all finish within the Sep 12 arm opportunity; that compression is not a credible default. An earlier daytime/manual window requires its own valid scheduling/authority route.

The current draft explicitly targets Sep 12 G2-a at 02:56 with `WINDOW_MAX_S=13500`, and requires rehearsal acceptance first. It must be superseded rather than silently repurposed: `d84da72e:docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md:24`, `:61`; activation cutoff at `13-activation-checklist-2026-09-11.md:43`.

**D-138 transaction contents:** new acceptance identity/bytes, active registry/default, generation-specific arithmetic and verification expectations, applicable pack/extraction/acceptance-owner pins, T1 projections, readiness evidence and regenerated chains must agree at landing. Historical issued generations remain unchanged. D-138 forbids making the suite green by replacing the production pin invariant with fixtures ([decision_log.md:10072](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/decision_log.md:10072)); the earlier cold science gate requires atomic fan-out at [03-cold-science-review.md:111](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:111).

That transaction must carry:

`docs/process_traces/2026-09-10-activation-96bfeca7/15-r2-coverage-ulp-staged-for-d138.patch`

and its four staged regressions. The lead’s note explicitly assigns them to this transaction and identifies R2 as a rare endpoint false-refusal repair, not today’s epoch blocker (`15-lead-note-r2-staged-for-d138.md:3–13`, at `d84da72e`).

**Q3. The current G2-a chain cannot run without a valid acceptance.**

`DIAGNOSTIC_NO_PACK` exempts the **pack condition C2**, not calibration. C1 and C3–C5 must still pass ([night_gate.py:435](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/night_gate.py:435)). Relevant consumption points are:

| Boundary | Acceptance/identity dependency |
|---|---|
| Producer `bind-window` | Derives live epoch, authenticates the screen, loads r6, binds its ID/path/hash and ledger cutoff. `d84da72e:scripts/generate_g2a_probe_inputs.py:652`, `:677`, `:844`. |
| Producer `check`, including chain startup | Re-derives current epoch/T1, compares saved vectors, reloads acceptance/cutoff and checks the bound plan. Same file `:1226`. |
| Bracket reservation | Carries the exact epoch/T1 into both reserved slots. [reserve_calibration_window_bracket.py:106](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/reserve_calibration_window_bracket.py:106). |
| Pre **and** post calibration writer | Authenticates issued bytes, protocol and all four estimator-source hashes; compares live epoch before hardware work. It also uses the derived level comparator to classify final observations, including `systematic-invalid`. [validate_powermetrics_fiducial.py:364](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/validate_powermetrics_fiducial.py:364), `:1701`, `:2213`. |
| Writer source/launch binding | Reads `DEFAULT_ACCEPTANCE_BOUND_PATH`; where launch lineage is required, verifies it against the pack’s acceptance reference. Same file `:730`, `:790`. This conditional pack binding does not remove the unconditional epoch check. |
| G2-a shell chain | Runs producer `check`, reserves the bracket, captures pre, enforces `b_fiducial_s <= 0.032898493715362`, attaches that calibration to every stage, then captures post. The chain explicitly requires regeneration/re-hashing after successor issuance. [SHAKEDOWN-G2-RUNSHEET.md:448](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:448), `:500`, `:536`. |
| Campaign/window evaluation | Loads acceptance to obtain the authenticated ledger baseline; bracket evaluation independently checks epoch, freshness and budget. [run_campaign.py:4809](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/run_campaign.py:4809), [whole_window.py:507](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/whole_window.py:507), [calibration_bracketing.py:1516](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_bracketing.py:1516). |
| Night driver | No direct acceptance loader or OS exception. It verifies the selected chain digest and executes that chain. [run_night.py:1577](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/run_night.py:1577). |
| Later claim/floor consumers | Acceptance is also consumed by `analysis_engine/inputs.py:1625,3123`, `mint_floor_artifact.py:965,1743,2036`, `mint_floor_artifact_generalized.py:3596`, and `floor_mint_estimator.py:142`; registration/pin inventories include `arm_readiness.py:6160` and `scripts/floor_mint_pinsets/schema_v2.json:182`. These are successor fan-out surfaces, not additional G2-a exemptions. |

The summation/prompt-pin tools preserve bound identity inputs rather than issue acceptance; see Q5.

A diagnostic exemption from these checks would be **a new rule**. The resident magistrate cannot make it: [MAGISTRATE_RELAUNCH_PROMPT.md:20](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:20) routes rule amendments to the cold gate or Ed. The proposed derivation-only bootstrap is therefore a separately governed prerequisite, not a bypass for G2-a.

**Q4. No current-epoch observations exist in this ledger; mixed-history support is not the same as mixed derivation support.**

I read the named production clone’s ledger, without opening its custody locators:

| Fact | Observed result |
|---|---|
| Receipts | **76**, comprising 38 historical-import reservations and 38 finalizations |
| Distinct observations | **38**, not 76 |
| `identity_epoch.os_build` | **25F84 on all 76 rows** |
| Earliest capture | **2026-07-22 14:55:37.090072 PDT** |
| Latest capture / final row | **2026-08-01 06:48:32.195229 PDT**, attempt `20260801T064830-c76f5d1c`, `systematic-invalid` |
| Terminal digest | `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7` |
| Comparison with committed fixture | **Byte-identical** |

The same final row is [calibration_observation_ledger.jsonl:76](/Users/edr/code/JouleWise-wt-gate-sweep-b/tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl:76). The contract independently records the 38-observation interpretation at [calibration_ledger.md:227](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/calibration_ledger.md:227).

The ledger alone cannot date the subsequent upgrade. However, local installation history records **macOS 26.6.2 at `2026-09-03T03:37:44Z` = September 2, 20:37:44 PDT** ([InstallHistory.plist:5141](/Library/Receipts/InstallHistory.plist:5141)). `sw_vers` currently reports that version and `25G83`. `SystemVersion.plist` is readable and has August 12, 19:51:55 PDT timestamps; those file timestamps are **not** the observed installation date.

On mixed epochs:

- The ledger stores epoch per observation and can retain different epochs; same-epoch trigger counting is explicitly filtered at [calibration_bracketing.py:1803](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_bracketing.py:1803).
- The **current issued-artifact validator** requires exactly one `d079_epoch`, equal to the acceptance’s identity, and every derivation member must link into its prior set: [calibration_bracketing.py:522](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_bracketing.py:522), `:562`.
- Its baseline-prefix validator rejects **any live observation** before the issuance cutoff and requires every prefix epoch to map into that catalog: same file `:1349–1385`.
- Bootstrap preparation refuses a receipt that cannot map to exactly one artifact epoch: [calibration_ledger_bootstrap.py:289](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/calibration_ledger_bootstrap.py:289).

Consequently, **appending valid 25G83 observations is not sufficient to make the existing issuer accept them**. A ruled prospective-generation representation is needed. Recommended ruling: preserve the canonical history, represent its epochs honestly, and select a preregistered epoch-pure derivation corpus. An explicitly anchored separate epoch ledger is an alternative for the gate to assess; silently resetting/relabeling the existing ledger is not.

**Q5. Additional bindings and consequences.**

| Surface | Consequence of the update |
|---|---|
| **Powermetrics executable** | Independently changed: historical SHA `d1dccad0…fe69`; current `/usr/bin/powermetrics` SHA **`b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5`**. New captures must carry it. Calibration attachment checks the actual executable hash ([controller.py:456](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/controller.py:456)); reducer checks measured OS/model fields ([reduce.py:1625](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/reduce.py:1625)). |
| **Production policy JSON** | No literal OS-build pin. It still requires brackets and production environment admission. Its `0.01` drift field is explicitly treated as a legacy, non-operative comparator by acceptance evaluation. [quiet_mac_p2_production.json:2](/Users/edr/code/JouleWise-wt-gate-sweep-b/configs/campaign_policies/quiet_mac_p2_production.json:2); [calibration_bracketing.py:1518](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/calibration_bracketing.py:1518). |
| **Environment-admission reference provenance** | No hidden `25F84` reference requirement. The flag means policy binding plus campaign/per-run snapshot hashes exist. Current snapshots must be captured and their evaluations replay consistently; an old snapshot is not refreshed by changing a label. [controller.py:978](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/controller.py:978); `d84da72e:joulewise/environment_admission.py:246`. |
| **D-166 registration** | The canonical registration pins dominance-ratio semantics, not OS build. OS change alone does not authorize changing its bytes or threshold. Its night-gate digest remains binding. [d166_dominance_criterion_registration.json:1](/Users/edr/code/JouleWise-wt-gate-sweep-b/configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json:1); [night_gate.py:34](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/night_gate.py:34). |
| **G2-a prompt pin** | No direct OS field. It binds selected length, prompt/tokenizer/panel and authenticated selection/count evidence. The source inventory binds epoch/T1 files, so the downstream pin must come from the new valid G2-a evidence. [summarize_g2a_prefill_probe.py:171](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/summarize_g2a_prefill_probe.py:171); [issue_g2a_prefill_prompt_pin.py:413](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/issue_g2a_prefill_prompt_pin.py:413), `:475`. |
| **`arm_readiness_evidence_t0`** | Authenticates the epoch/T1 input files and checks exact reservation-slot equality; no hardcoded old OS. Recreate inputs and receipts for the actual epoch. Captures and launch manifests also require the current boot session, so pre-update/pre-reboot evidence cannot be reused. [arm_readiness_evidence_t0.py:1586](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/arm_readiness_evidence_t0.py:1586), `:1623`, `:554`, `:832`. |
| **Stack/floor identities and pack pins** | Stack identity includes OS version. NEG-8 freshness includes explicit `os_build_change` and calibration-identity-change triggers. Pack generators select exact acceptance pins, requiring successor fan-out. [identity_pins.py:360](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/identity_pins.py:360); [whole_window.py:1348](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/whole_window.py:1348); [generate_configs.py:459](/Users/edr/code/JouleWise-wt-gate-sweep-b/configs/campaigns/d117_contrast_v5/generate_configs.py:459). |

## Disproved alternatives

- **Ledger restoration failed:** the inspected production ledger matches the committed fixture exactly. The supplied bench custody replay remains separate evidence.
- **The acceptance expired by age:** D-102 explicitly has no calendar hard expiry; this is an identity change.
- **Updating only `os_build` would suffice:** external byte pins, epoch-history consistency, the changed executable and missing current-epoch evidence independently prevent that.
- **The pre/post pair can bootstrap its own screen:** the writer refuses first, and self-fitting violates D-102.
- **Seventeen is an already authorized new-epoch requirement:** it is the retained historical population, not a prospective sampling rule.

## Residual risk

The retained **D-125 floor conflict** is directly relevant to new issuance: the queue still reserves to Ed whether the current `0.009724` screen supersedes or violates the lineage floor `0.010818` ([TASK_QUEUE.md:655](/Users/edr/code/JouleWise-wt-gate-sweep-b/TASK_QUEUE.md:655)). Neither this consult nor the resident magistrate should settle it implicitly while deriving a successor.

**Next exact step:** assemble the cold-gate packet for the new-epoch capture/ledger/issuance mechanism, with the sample-design question and D-125 conflict explicit. Keep G2-a unarmed until that mechanism is installed, the new evidence is accepted, and the atomic reissue passes verification.