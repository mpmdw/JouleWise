```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "SEAT: gpt-6-sol — NTP-ENFORCE-DESIGN-01: use sealed window attestation with mandatory admission checks; resolve the pack chain source before implementation.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "descendant",
    "head_start": "d5f624b6e1f1a059ef21e49a5f2ea5c03eead3c6",
    "head_end": "d5f624b6e1f1a059ef21e49a5f2ea5c03eead3c6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "text": "A ledger-valid capture can currently reach membership before the post-window H6 verdict exists."},
      {"id": "F2", "severity": "blocker", "text": "The checked-in source and harvest consumer for a claim pack's window-chain.zsh are not identified; that route cannot be declared enforced yet."},
      {"id": "F3", "severity": "should_fix", "text": "Make H5 receipts and the H6 roster digest mandatory inputs to every prospective admission boundary, including replay and finalization."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor 9eab16f8 HEAD; git status --porcelain=v1; git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["d5f624b6e1f1a059ef21e49a5f2ea5c03eead3c6"]},
      "expected": {"exit_code": 0, "tail_regex": "d5f624b6e1f1a059ef21e49a5f2ea5c03eead3c6"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n 'window-chain.zsh|window_chain.zsh|WINDOW_CHAIN' scripts joulewise configs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["joulewise/arm_readiness_evidence_t0.py:907:        raise _underivable(kind, \"window-chain.zsh overrides the sibling quarantine binding\")"]},
      "expected": {"exit_code": 0, "tail_regex": "window-chain.zsh"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Identify the exact pack window-chain source and claim harvest consumer before assigning a complete implementation scope.",
      "needs": "Lead supplies their exact paths and resolves composition with the concurrent D-138 calibration_bracketing.py and claim_hold.py transaction."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No command, capture, test, or live bench action was run; this was a read-only design inspection.",
      "needs": "Lead-controlled bench verifies the real passwordless OFF/ON commands and a query older than retained log."
    }
  ]
}
```

## Findings

**SEAT: gpt-6-sol — NTP-ENFORCE-DESIGN-01**

**F1 — Choose a sealed window attestation plus admission checks.** The writer hashes evidence and finalizes each slot before a whole-window query can exist; its `valid` row must remain historical, not silently rewritten. The issuer currently selects `valid` observations, while bracket construction accepts `valid` pre/post rows. A pending-to-final ledger would change that lifecycle more broadly. [Writer](scripts/validate_powermetrics_fiducial.py:2636), [chain](scripts/night_chains/calibration_derivation_only.zsh:243), [issuer](scripts/issue_calibration_acceptance_generation.py:1255), [brackets](joulewise/calibration_bracketing.py:1337). **Inference:** make H6 an additional, mandatory admission condition for *prospective* 25G83 captures; preserve the separately governed W1/W2 issuance. [A3](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:179).

The window supervisor should save the exact H5 OFF and ON receipts, one raw whole-window `log show` output, and a write-once verdict manifest in window custody. The manifest should bind the plan/window identity, full declared and attempted roster, each attempt and capture content ID, paired-clock bounds, query argv/exit/query times, raw-output SHA-256, witness line and timestamp, marker lines, and per-capture verdict. Pin its digest in the harvest or issuance record and authenticate both raw bytes and roster completeness on every read. Missing, substituted, or unmatched rows mean `network_time_unattested`. A valid later recovery query gets a new immutable attempt; it never edits the old result. This follows A3’s query, witness, verdict, and recovery rules. [A3](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:174).

The common admission reader must be called when the issuer selects members **and** when the issued artifact is validated; when bracket bindings are built **and** revalidated; when evidence summaries harvest envelopes; and when claim evaluation and finalization consume a measurement roster. Bind the attestation digest into prospective acceptance and bracket outputs. A claim window with any failed claim input gets a whole-window hold, retaining every attempted row and its cause; it must not select clean survivors. Existing downstream bracket readers include campaign evaluation, whole-window evaluation, analysis finalization, and minting. [Issuer](scripts/issue_calibration_acceptance_generation.py:1255), [bracket validator](joulewise/calibration_bracketing.py:1384), [evidence harvest](joulewise/quiet_predicate_campaign.py:1289), [campaign](scripts/run_campaign.py:4977), [whole window](joulewise/whole_window.py:602), [finalization](joulewise/analysis_manifest_v3.py:3652), [mint](scripts/mint_floor_artifact_generalized.py:2261). **Inference:** a consumer-census regression should enumerate those entry points, pass an authentic-looking ledger-valid capture with a bad or absent H6 record through each, and require refusal even on replay.

**F2 — The pack route needs one identified owner.** Pack arming already executes and checks the exact OFF command, but GO and the launcher do not establish the later 600-second interval, H6, or an ON receipt. The pack consumes a pinned `window-chain.zsh`; the inspected repository references it but does not identify a generic checked-in capture-chain producer. Name that producer and its harvest/evaluation consumer before declaring the “no route” property complete. [Arm probe](joulewise/arm_readiness_evidence_t0.py:1225), [GO](scripts/run_night.py:2085), [launcher](scripts/launch_window.py:170), [scout](docs/process_traces/2026-09-27-activation-d528efb2/70-ntp-enforce-scout/report.md:18). Compose H6 refusal with the concurrent build-keyed `claim_hold.py` as an independent hold predicate, rather than changing the hold’s build key or using it as the attestation store. **Inference.**

**F3 — Put H5 under the window supervisor on every route.** After verify-only and reservation, set OFF before the settle; save argv, exact stdout, exit, and completion times on wall and monotonic clocks. Refuse the first paired reading unless OFF exited 0, stdout is exactly `setUsingNetworkTime: Off`, and **both** elapsed clocks show at least 600 seconds on the same boot. Check the actual reading, not the scheduled sleep. The derivation chain currently settles before slots; the evidence chain already toggles before settle and restores in `finally`. [A3](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:152), [derivation](scripts/night_chains/calibration_derivation_only.zsh:207), [evidence](joulewise/quiet_predicate_campaign.py:1622), [restore](joulewise/quiet_predicate_campaign.py:1764). Run H6 promptly after the last actual reading, then attempt ON in `finally` on success, refusal, stand-down, and signal handling; save even a failed ON attempt. **Inference:** `finally` cannot cover SIGKILL, power loss, or process death, so a separate startup/recovery supervisor must attempt ON, retain its receipt, and block another arm while restoration is unresolved.

Use A3’s exact whole-window query and a `[com.apple.timed:data]` witness strictly older than the first reading minus 180 seconds. Parse each syslog timestamp’s explicit UTC offset; reject malformed or ambiguous timestamps instead of treating them as zero markers. Search **individual marker lines**, with each interval widened from both paired clocks. A failed query, bad first-line header, missing witness, incomplete output, or missing capture record makes all affected captures unattested; a marker makes its capture slew-attested. Keep the evidence chain’s existing immediate query and require **both** verdicts. [A3](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:174), [current offset loss](joulewise/quiet_predicate_campaign.py:535), [immediate query](joulewise/quiet_predicate_campaign.py:695).

**Implementation seat and order.** A first, exact repository `WRITE_SCOPE` can be: `joulewise/network_time_window.py`, `joulewise/quiet_predicate_campaign.py`, `scripts/night_chains/calibration_derivation_only.zsh`, `scripts/gen_derivation_night.py`, `scripts/validate_powermetrics_fiducial.py`, `scripts/issue_calibration_acceptance_generation.py`, `joulewise/calibration_bracketing.py`, `scripts/build_bracket_binding.py`, `scripts/run_night.py`, `joulewise/whole_window.py`, `scripts/run_campaign.py`, `joulewise/analysis_manifest_v3.py`, `scripts/mint_floor_artifact_generalized.py`, and their exact matching `tests/test_*.py` paths, plus new `tests/test_network_time_window.py`. This is a **future proposal**, not this seat’s authority. The lead should replace the test shorthand with exact filenames and add the located pack producer/consumer paths before issuing that scope. Do not edit D-138’s four pinned estimator files. Integrate `calibration_bracketing.py` only after the concurrent D-138 change is settled. Current-candidate issuance precedes H5/H6 implementation; enforcement and the owner-sealed successor registration precede every next 25G83 window. Cap R8, H6, then R9 run before B is read. [D-138](docs/decision_log.md:10361), [cap sequence](docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md:191). The owner’s amendment must state H5’s exact command and 600 seconds, H6’s witnessed 180-second rule and both exclusions, and H7’s per-capture state/rate/drift recording and no ON/OFF pooling without a prior registered rule. [A3](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:152), [H7](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:197).

## Residual risk

Carry A3’s seven defect-shaped cases, especially header-only, wrong-category witness, markers at −179/−181 seconds, and the **real** old-log query. Add tests for a late query, timezone offset, truncated output, a missing roster member, a ledger-valid excluded member/endpoint, and one failed measurement in a claim pack. A query run late passes only if its required witness still exists; otherwise every capture is unattested. The live bench must verify actual passwordless OFF/ON output, restore recovery, fresh witness availability, and the old-log failure before an agent-free capture. [A3 tests](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:185), [retention limit](docs/process_traces/2026-09-27-activation-d528efb2/40-sci-a2-network-time/31-addendum-ruling.md:240).