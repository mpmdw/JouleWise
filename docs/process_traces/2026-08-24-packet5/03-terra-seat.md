```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Condition 3 must be amended as part of an explicit window-head arm lane; whole-tree R1 is intentional, but the current live-HEAD consumers make the present transaction unarmable after fixation.",
  "workspace": {
    "base_requested": "a591a912a9e29ccff72cd7ca84851050ecb3fd93",
    "base_mode": "exact",
    "head_start": "a591a912a9e29ccff72cd7ca84851050ecb3fd93",
    "head_end": "a591a912a9e29ccff72cd7ca84851050ecb3fd93",
    "upstream_end": "a591a912a9e29ccff72cd7ca84851050ecb3fd93",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "packet5-refuter-terra.codex-observer.jsonl",
    "packet5-refuter-terra.log",
    "packet5-refuter-terra.status"
  ],
  "verdict": {
    "alpha": "REFUTED",
    "beta": "REFUTED",
    "gamma": "SURVIVES-WITH-CONDITIONS",
    "framing": "The whole-tree R1 diff is an intended conservative window contract, not a defect; the unratified live-HEAD-only arm/consume architecture creates the real incompatibility.",
    "condition_3": "AMENDMENT_REQUIRED"
  },
  "findings": [
    {
      "id": "F1",
      "severity": "blocker",
      "title": "The current live-main implementation makes a real post-fixation arm refuse.",
      "evidence": [
        "joulewise/arm_readiness.py:4115-4163",
        "joulewise/arm_readiness.py:4295-4321",
        "docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2121-2143"
      ]
    },
    {
      "id": "F2",
      "severity": "blocker",
      "title": "Custody-external relocation of the fixation literal has no present non-replaceable authenticator.",
      "evidence": [
        "joulewise/arm_readiness.py:4198-4253",
        "joulewise/arm_readiness.py:10551-10596",
        "docs/contracts/d117_step6_confirmation_table.md:43-62"
      ]
    },
    {
      "id": "F3",
      "severity": "should_fix",
      "title": "A window-head lane requires coordinated changes to marker, arm replay, launch, and scheduler consumers; a clarification cannot change those rejection rules.",
      "evidence": [
        "joulewise/arm_readiness.py:4755-4777",
        "joulewise/arm_readiness.py:7477-7482",
        "joulewise/arm_readiness.py:7556-7576",
        "joulewise/arm_readiness.py:10639-10669",
        "scripts/launch_window.py:107-135"
      ]
    }
  ],
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba joulewise/arm_readiness.py | sed -n '4115,4163p;4256,4322p;5450,5485p;7307,7500p;7556,7635p;7798,7905p;9158,9262p;10551,10596p;10639,10669p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "nl -ba docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md | sed -n '15,80p'; nl -ba docs/process_traces/2026-08-22-t20/o1-coldgate/opus-contract-refutation.md | sed -n '1031,1073p'; nl -ba docs/contracts/d117_step6_confirmation_table.md | sed -n '43,62p;139,192p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "jq -r '.freeze_evidence_lifecycle.irrelevant_path_allowlist[]' configs/arm_readiness/d117_row_registry_v2.json | awk 'BEGIN{n=0; bad=0} {n++; if($0 !~ /^configs\\//) bad++} END {if (n != 112 || bad != 0) exit 1; print \"allowlist_count=112; non_configs=0\"}'; git diff --check; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "allowlist_count=112; non_configs=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "allowlist_count=112; non_configs=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Choose and authorize an explicit window-head arm/consume contract, or reject gamma and redesign the transaction; the existing live-main path cannot cleanly arm after condition-3 fixation.",
      "needs": "Magistrate ruling and a reviewed amendment package."
    }
  ]
}
```

## Findings

### F1 — condition 3 needs amendment, but the framing must be narrowed

The decisive code is intentionally whole-tree: `_r1_changed_paths` runs `git diff --name-only … derivation..current_head --` with no pack pathspec (`joulewise/arm_readiness.py:4115-4163`), and the lifecycle gate refuses every remaining relevant path (`joulewise/arm_readiness.py:4295-4321`). The 112 registry entries all begin `configs/`; its first and last entries establish that scope (`configs/arm_readiness/d117_row_registry_v2.json:212-220,320-325`).

R4 independently records the exact consequence: at fixation, the sole residue is `tests/test_receipt_histsem.py`, and states that this is the reason Packet 5 gates the real transaction (`s0-runsheet-r4.md:2121-2143`). There is no repair lane after freeze: `reauthor_clean.py` refuses a generation with its committed freeze receipt (`scripts/reauthor_clean.py:263-268`).

So the broad framing attack fails: whole-tree R1 is a conservative design, not an accidental defect. Condition 8 expressly calls it “a **window property, not a standing invariant**” (`opus-contract-refutation.md:1069-1073`). But the transaction currently has no executable way to use that property after fixation. That is a real contract/mechanism incompatibility.

A clarification is insufficient. `reviewed_main` defines exactness as clean `HEAD == local main == origin/main` (`arm_readiness.py:4755-4777`), arm generation refuses otherwise (`arm_readiness.py:7477-7482`), and arm verification rejects a later head as stale (`arm_readiness.py:7556-7576`). The amendment should preserve condition 3’s “first commit after window close” fixation rule, while adding an exact, authenticated window-head coordinate and changing the live-head requirements that presently contradict it.

### Option verdicts

- **Alpha — REFUTED.** The ruling’s controlling text is: “**no authenticator path ever enters any allowlist**” (`MAGISTRATE-RULING-O1.md:70-74`). Moving the fixation literal out of Git does not solve the fixed-point problem: today `_require_confirmed_conditional_path` authenticates `C → S` only by calling `_authenticate_confirmation_table`, then comparing the current-head pinset blob to the table digest (`arm_readiness.py:4198-4253`). That helper trusts an operator-supplied `expected_confirmation_digest`; its sidecar is explicitly not an authenticator (`arm_readiness.py:10551-10596`; `d117_step6_confirmation_table.md:43-56`).

  Therefore, under alpha, the operator supplies the reference, the code compares external bytes to it, and no current mechanism pins that reference before the external bytes can be replaced. The project itself records the remaining boundary: “`hC` is an unauthenticated operator-supplied string; no code pins that literal” (`run_reports/2026-08-23-t21-t22-session.md:492-496`). Alpha recreates the O-1 impossibility off-tree, with weaker auditability.

- **Beta — REFUTED.** The premise slightly overstates condition 3. Arming is not itself a Git commit, so it does not literally violate condition 3’s requirement: “Fixation: the first commit **after window close**” (`opus-contract-refutation.md:1043-1048`).

  It does, however, violate condition 5’s controlling prohibition: “no claim-bearing arm occurs in [the mint→fixation] interval” (`MAGISTRATE-RULING-O1.md:62-65`). No other D-151 condition literally forbids an external arm before fixation. Independently, current launch cannot use it after fixation: `launch_window.py` first calls `_verify_arm_receipt` (`scripts/launch_window.py:107-135`), and verification requires the current `reviewed_main` equal the receipt’s one (`arm_readiness.py:7571-7576`). Thus beta fails both the D-151 residual boundary and the current mechanism.

- **Gamma — SURVIVES-WITH-CONDITIONS.** It is the only coherent direction: preserve whole-tree R1 and bind an arm to the actual window-close head. This fits condition 8’s window-property doctrine, but it is not implemented.

  Current failures are concrete:

  - A detached/window-pinned checkout fails arm exactness (`arm_readiness.py:4755-4777,7477-7482`).
  - The publication marker requires its head equal the current `origin/main`, then strict four-way equality (`arm_readiness.py:10639-10669`).
  - A later `verify` recomputes `reviewed_main` and calls the receipt stale (`arm_readiness.py:7556-7576`). The existing regression explicitly commits a later file, moves `origin/main`, then expects `verify_arm_receipt` to fail (`tests/test_arm_readiness_integration.py:317-323`).
  - Production launch calls that verifier before consumption (`scripts/launch_window.py:107-135`); consumption also treats `same_head` as volatile (`arm_readiness.py:8710-8760`).
  - Campaign writer admission requires the current checkout head equal the consumption head (`arm_readiness.py:9576-9602`, `9158-9262`).

  Some later archival/claim readers do tolerate a later head: `authenticate_launch_lineage` defaults `require_current_boot=False` and disables semantic arm replay (`arm_readiness.py:9167-9220`); whole-window and analysis-input callers use that default (`whole_window.py:1622-1629,2400-2411`; `analysis_engine/inputs.py:895-909`). That tolerance cannot rescue gamma, because launch and campaign admission have already failed earlier.

  Required conditions: a signed/persisted `window_head` identity; marker/table semantics binding that identity rather than current `origin/main`; arm/verify/launch/scheduler rules that authorize only that immutable checkout; and an explicit rule for later claim replay. This is an amendment package, not an interpretive note.

`WINDOW_STATUS.md` is not an arm-receipt consumer, but it is an additional whole-tree hazard: its publisher writes, commits, and pushes `WINDOW_STATUS.md` (`scripts/window_status.sh:92-104`), a path outside the 112 configs-only allowlist. Any such post-derivation status commit adds another changed-set residue.

### Strongest argument against this conclusion

Condition 3 itself never says “arm only at fixation HEAD”; beta shows that its wording constrains the first *commit*, not a non-committing arm. Condition 8 already calls the changed-set a window property, and later analysis readers intentionally tolerate historical lineages. A magistrate could therefore retain condition 3 verbatim and add only an implementation interpretation for gamma.

That is plausible—but not sufficient under the current governing instrument: condition 4’s published-green path requires strict current-head equality (`s0-runsheet-r4.md:2316-2324`), and production arm/launch code actively refuses the proposed interpretation. The operative transaction contract must be amended somewhere explicit; labeling it a clarification would conceal that semantic change.