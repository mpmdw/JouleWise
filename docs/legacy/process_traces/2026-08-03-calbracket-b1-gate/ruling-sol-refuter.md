```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "B1 is confirmed on both sides; round 2 is licensed as a constrained local bench repair, with stronger interaction regressions and an independent final-head delta audit.",
  "workspace": {
    "base_requested": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "base_mode": "exact",
    "head_start": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "head_end": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "claim_status": "CONFIRMED",
        "title": "Round-1 guard is simultaneously fail-closed before preparation and fail-open for normalized implicit minted rows",
        "evidence": [
          "joulewise/whole_window.py:416-430",
          "joulewise/whole_window.py:438-449",
          "joulewise/whole_window.py:465-513",
          "joulewise/whole_window.py:3467-3474",
          "joulewise/whole_window.py:3567-3580",
          "joulewise/whole_window.py:4073-4083",
          "joulewise/whole_window.py:4110-4115",
          "joulewise/whole_window.py:4144-4159",
          "joulewise/whole_window.py:4703-4706"
        ]
      },
      {
        "id": "D1",
        "severity": "blocker",
        "claim_status": "PARTIALLY-CONFIRMED",
        "title": "Lead repair mechanisms are correct, but 'after or inside the seam' is too permissive",
        "ruling": "Place the normalized minted readiness requirement in _validate_row_uncached immediately after _current_core_rederivation_reasons has had its sole preparation opportunity; do not put it inside _prepare, do not call _prepare from consumers, and do not require session semantics equality.",
        "evidence": [
          "joulewise/whole_window.py:4332-4361",
          "joulewise/whole_window.py:465-513",
          "joulewise/analysis_engine/inputs.py:2815-2824",
          "joulewise/floor_extraction.py:1616-1631"
        ]
      },
      {
        "id": "P1",
        "severity": "should_fix",
        "claim_status": "PARTIALLY-CONFIRMED",
        "title": "Packet is substantively usable but its verbatim and completeness labels are not literally accurate",
        "evidence": [
          "/Users/edr/code/JouleWise/docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md:67-106",
          "/Users/edr/code/JouleWise/docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:53-58",
          "/Users/edr/code/JouleWise/docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:174-185",
          "/Users/edr/code/JouleWise/docs/decision_log.md:6995-7012",
          "/Users/edr/code/JouleWise/docs/decision_log.md:7024-7036"
        ]
      }
    ],
    "section8": {
      "a": "LICENSE round 2, conditioned on D1's exact placement constraint.",
      "b": "Second in-place patch is sound: remove the pre-_validate_row_uncached raw guard and consolidate normalized minted readiness with the post-preparation readiness enforcement. No structural consult is presently required.",
      "c": "Mandatory public-path regressions: fresh explicit minted plus valid snapshot accepts without manual _prepare; the same fresh call shape with pending snapshot refuses; implicit/default minted with no session refuses. Add mutants for early placement and raw-only comparison.",
      "d": "BENCH. The ruled code change is smaller than the delegation contract now needed to restate it.",
      "e": "Independent final-head delta audit must replay focused and canonical suites with writable TMPDIR, trace every named consumer, prove snapshot-object reuse/no reload, and mutate both failure mechanisms. Same-signature survival triggers consult, not round 3."
    },
    "consumer_paths": {
      "covered_by_ruled_repair": [
        "floor extraction primary verifier",
        "floor extraction drift-allowance secondary verifier",
        "floor mint authenticated consumption",
        "floor mint allowance re-derivation",
        "analysis input verifier",
        "analysis allowance verifier",
        "public secondary verifier with omitted session"
      ],
      "already_conformant_not_changed": [
        "direct runner max-bracket/salvage session path",
        "direct runner minted path",
        "asynchronous direct core-verdict path"
      ],
      "residual_bypass_if_exact_ruling_followed": []
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/cal-bracket-d079",
          "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
          "impl/cal-bracket-d079"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2e61ff96ea80186efa71efb9c9f6f00a16a70019.*impl/cal-bracket-d079"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from pathlib import Path; from unittest.mock import patch; from joulewise.calibration_ledger import CalibrationLedgerSnapshot,LEDGER_SCHEMA; from joulewise.whole_window import AuthenticatedConsumptionSession,MINTED_CONSUMPTION_SEMANTICS_ID,_row_consumption_semantics_id,_validate_row; s=CalibrationLedgerSnapshot(LEDGER_SCHEMA,Path(\"/nonexistent/ledger\"),0,\"a\"*64,(),(),()); x=AuthenticatedConsumptionSession(Path(\"/runs-root\"),{\"member\"},consumption_semantics_id=MINTED_CONSUMPTION_SEMANTICS_ID,calibration_ledger_snapshot=s); p=patch(\"joulewise.whole_window._validate_row_uncached\",return_value=(True,())); m=p.start(); a=_validate_row({\"consumption_semantics_id\":MINTED_CONSUMPTION_SEMANTICS_ID},Path(\"/runs-root\"),{\"member\"},consumption_session=x); n=m.call_count; b=_validate_row({},Path(\"/runs-root\"),{\"member\"}); p.stop(); print(\"explicit_fresh\",a,\"uncached\",n,\"prepared\",x._prepared); print(\"implicit\",_row_consumption_semantics_id({}),b,\"uncached\",m.call_count-n)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "explicit_fresh (False, ('whole_window_verdict_provenance_invalid',)) uncached 0 prepared False",
          "implicit d078_minted_envelopes_v1 (True, ()) uncached 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "explicit_fresh \\(True, \\(\\)\\).*prepared True.*implicit d078_minted_envelopes_v1 \\(False,"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "Static inspection of D-109, PACKET.md, all six custody inputs, and the requested code/test files at HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "D-109 R1 clauses 1-7 and R2 clauses 1-8 inspected",
          "six custody inputs inspected",
          "all named consumer call sites traced"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "all named consumer call sites traced"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This cold-gate review was intentionally read-only; filesystem-backed tests and the canonical suite were not rerun.",
      "needs": "Lead must run focused regressions and the canonical suite with writable temporary storage after applying round 2."
    }
  ]
}
```

## Findings

### B1 — blocker — CONFIRMED

Both halves of the refined finding are real.

The fail-closed order is unambiguous: a fresh session starts with `_prepared=False`, and `ready` therefore returns false (`joulewise/whole_window.py:438-449`). The guard returns at `joulewise/whole_window.py:4073-4083` before `_validate_row_uncached()` is called at `joulewise/whole_window.py:4110-4115`. The only established verifier-side preparation opportunity is deeper in `_current_core_rederivation_reasons()`, at `joulewise/whole_window.py:3467-3474`. The probe confirmed zero uncached calls and `_prepared=False`.

The fail-open normalization mismatch is equally direct: `_row_consumption_semantics_id()` defaults a missing or non-string declaration to minted semantics (`joulewise/whole_window.py:3567-3580`), while the guard compares the raw declaration (`joulewise/whole_window.py:4073-4081`). Implicit legacy rows remain intentionally replay-readable (`joulewise/whole_window.py:4703-4706`), so this is a reachable secondary-verifier bypass, not merely a malformed-row curiosity. The mocked probe isolates the guard bypass; it does not itself constitute an end-to-end valid-row acceptance test.

The named production paths all reach the defective verifier with fresh sessions:

- Floor extraction constructs the session and immediately calls the verifier at `joulewise/floor_extraction.py:1616-1631`; its allowance pass reuses that session at `joulewise/floor_extraction.py:1691-1697`.

- Floor minting constructs the session and immediately verifies at `scripts/mint_floor_artifact.py:520-535`; allowance re-derivation constructs another session with the caller’s same snapshot at `scripts/mint_floor_artifact.py:1148-1163`.

- Analysis loads one snapshot at `joulewise/analysis_engine/inputs.py:2677-2691`, threads it into the session at `joulewise/analysis_engine/inputs.py:2808-2824`, and reuses that session for allowances at `joulewise/analysis_engine/inputs.py:2851-2855`.

The round-1 tests have exactly the reported gap: the pending test manually calls `_prepare()` (`tests/test_whole_window_selection.py:1031-1062`), and the missing-session test supplies an explicit raw minted declaration (`tests/test_whole_window_selection.py:1064-1076`).

### D1 — blocker — PARTIALLY-CONFIRMED

The lead selected the correct two mechanisms, but “after or inside the preparation seam” admits unsound implementations.

The ruled placement is:

1. Remove the preflight raw-declaration guard at `joulewise/whole_window.py:4073-4083`.
2. Use the already-normalized `row_semantics` at `joulewise/whole_window.py:4144`.
3. After `_current_core_rederivation_reasons()` returns at `joulewise/whole_window.py:4332-4342`, require a present, ready session for normalized minted semantics—preferably consolidating this with the existing max-bracket/salvage readiness check at `joulewise/whole_window.py:4343-4361`.

“Inside `_prepare()`” is insufficient because no method exists to call when the session is missing, and `_prepare()` does not own row semantics (`joulewise/whole_window.py:465-513`). Do not add a session-semantics-equals-row-semantics requirement: floor extraction can construct a default max-bracket session while dispatching without an explicit semantics filter (`joulewise/floor_extraction.py:1616-1631`), and analysis likewise uses the constructor default (`joulewise/analysis_engine/inputs.py:2815-2824`). Such an equality check would introduce a new fail-closed break.

No consumer bypass remains under that exact placement. The direct runner is unaffected and already conformant: max-bracket/salvage constructs and prepares one session, then passes its snapshot into the core (`scripts/run_campaign.py:5211-5226`, `scripts/run_campaign.py:5255-5265`); the minted direct path loads one snapshot for the core at `scripts/run_campaign.py:5261-5265`; the asynchronous path also loads once and passes that object at `scripts/run_campaign.py:6754-6764`.

A second in-place patch is therefore sound. The seam is not presently structurally defective: `_prepare()` is an idempotent session operation (`joulewise/whole_window.py:465-484`), and both secondary-verifier surfaces converge on `_validate_row()` (`joulewise/whole_window.py:4725-4731`, `joulewise/whole_window.py:4916-4921`). Round 1 placed policy before the seam; it did not demonstrate that the seam cannot express the contract.

Section 8 ruling:

- (a) LICENSE round 2, only in the ruled shape above.

- (b) Use the constrained local consolidation; no consult is required before round 2.

- (c) Require public-path regressions with no manual `_prepare()`: valid fresh explicit minted accepts; fresh explicit minted with `calibration_ledger_pending` refuses with that reason; implicit/default minted without a session refuses. Mutating the check back before preparation and mutating normalized comparison back to raw must each make the relevant regression fail.

- (d) Execute at the bench. The cold gate has already supplied a more detailed contract than the small code change itself; rule 9 assigns such changes to the bench (`/Users/edr/code/JouleWise/CLAUDE.local.md:27`).

- (e) The delta re-audit must inspect the exact final head, independently trace every listed consumer, verify snapshot object identity/no reload, run focused and canonical suites with writable `TMPDIR`, and exercise both mutants. If the same early-placement/raw-normalization signature survives again—or another consumer bypass of that signature appears—rule 11 requires a consult rather than round 3 (`/Users/edr/code/JouleWise/CLAUDE.local.md:31-32`).

### P1 — should-fix — PARTIALLY-CONFIRMED

The packet is substantively sufficient to rule, but its hygiene claims are not literally exact.

The principal B1 prose is accurately represented, but the passage labeled “in full” is not verbatim: the packet converts the delta heading into a new quoted sentence and changes its punctuation/apostrophe form (`PACKET.md:67-93`; `inputs/streamB-delta.md:172-185`).

Section 5’s “not in dispute” summary is also incomplete. It retains B2, S1, reservation-first, chaining, head-pin, F1/F2, T1, and Window-A (`PACKET.md:101-106`), but omits the delta’s explicit retained checks for total-38 counting, prior-set subtraction, and budget boundaries (`inputs/streamB-delta.md:53-58`).

Finally, §4 omits D-109 R1.1’s sole-ledger authority and the entry’s applicability to every session construction (`docs/decision_log.md:6995-7012`). Those clauses materially explain why an implicit minted secondary-verifier bypass is prohibited. This does not change the gate result because the full D-109 entry was separately supplied as authority.

## Residual risk

No filesystem-backed or full-suite execution was appropriate in this read-only gate. Post-patch verification remains mandatory. If the exact local consolidation unexpectedly requires consumer-call-site changes, stop and consult: that would be new evidence that preparation ownership is structurally fragmented.