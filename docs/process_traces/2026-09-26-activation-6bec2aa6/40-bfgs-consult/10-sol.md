```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "BFG-S can use distinct non-derivation phases, externally anchored pair authentication, an envelope-level quiet gate, and three new v5 pack freezes while preserving frozen protocols and packs.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "exact",
    "head_start": "64e39bb937e79c710886acf13fbfab295526aa18",
    "head_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "BFG-S code, compatibility boundary, and tests", "action": "start_now"},
      {"row": "Three v5 pack authorings and freezes", "action": "wait_for", "event": "Reviewed BFG-S code head and settled evidence contract"},
      {"row": "Revision 5 predicate, custody text, and module pin amendment", "action": "wait_for", "event": "Revision 5 epoch issued or stopped"},
      {"row": "Non-derivation measurement arm", "action": "wait_for", "event": "BFG-S code and applicable pack freeze complete"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["64e39bb937e79c710886acf13fbfab295526aa18"]},
      "expected": {"exit_code": 0, "tail_regex": "64e39bb937e79c710886acf13fbfab295526aa18"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The proposed non-derivation custody anchor, historical allowlist, and pack disposition require the magistrate's cold-gate ruling before implementation is final.",
      "needs": "Rule the Q1–Q12 decisions and identify the trusted custody receipts and historical bundle inventory."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Endpoint battery readings cannot detect a charging excursion that begins and ends inside a window; the registered disclosure already states this limitation.",
      "needs": "Keep that disclosure with non-derivation claims and retain the separate wall-meter energy bar."
    }
  ]
}
```

## Q1 — Observation phases

**Decision:** Use the exact enumeration `arm_check | publish_install | t0 | validate_install | t0_power_row | slot_pre | slot_post | quiet_pre | quiet_post | bundle_pre | bundle_post`. A quiet record binds its `session_id` and envelope index; a bundle record needs an additive `run_id` identity field. Neither uses a fabricated slot. Distinct phases let replay check the expected container, identity, raw path, and pre/post order. Reusing `slot_pre/post` with a null slot would let an ordinary bundle masquerade as a derivation slot or pass a weak identity check.

## Q2 — Verdict and custody

**Decision:** Add `battery_float.authenticate_non_derivation_window` as the sole replay entry for quiet sessions and bundles. It takes the kind, container root, expected session or run identity, measured-window stamps, the *externally authenticated digest of the final parent record*, and the parent’s `pre`/`post` records. For quiet collection the parent is the final `session.json` after clock attestation; for a bundle it is `metadata.json`. A night custody receipt or authenticated campaign bundle manifest must bind that parent digest to the session or bundle. The helper verifies that binding, phases, identity, fixed custody-relative paths, raw digests, probe outcomes, fresh reparsing, predicates, and bracket order. It refuses an absent or mismatched parent anchor, identity or phase mismatch, duplicate record, bad path, raw custody damage, or a stored/replayed verdict disagreement; it returns `confounded` for an authentic predicate failure and `evidence_missing` for an authentically recorded failed, stale, malformed, or absent observation. Under ex-02’s distinction, **once a digest is recorded, missing or changed bytes are custody failure, never an exclusion**. The existing writable `session.json` or `metadata.json` alone cannot authenticate itself; relying on its own digest fields would permit replacement of both a reading and its alleged fingerprint.

## Q3 — Quiet collector unit

**Decision:** Bracket each **600-second envelope**, once before its first collector stamp and once after its final stamp and observer accounting; do not probe every 30-second round. The envelope is the unit retained by `pilot_summary`, while round probes would run inside its power and clock support and change the measured observer load. A failed pre read is recorded before recorder start, then collection stops with no claim-bearing envelope. If capture starts but exits before post, cleanup should attempt a post read after the measured span; if none is recorded, the retained partial envelope is `evidence_missing` and cannot contribute energy. This prevents an early exit from turning an unbracketed partial capture into a clean envelope.

## Q4 — QPE-01 protocol

**Decision:** Choose **(b): fail closed**. Any non-pass battery envelope makes the pilot’s claim refuse; retain its bytes and diagnostic rows, and leave the frozen exclusion list untouched. This is a prospective, directive-required admission refusal, applied before energy selection, rather than a newly invented exclusion that changes which envelopes enter the frozen statistic. The claim cannot silently gain a replacement or top-up route. If the project wants battery failure to exclude one envelope while the rest remain claim-bearing, that is a new registered v4 protocol requiring its own cold gate. Diagnostic-only treatment would let a known confounded envelope affect the pilot’s number.

## Q5 — Controller failures and targets

**Decision:** A successful, real Mac bundle whose measured window is claimed must carry an authenticated passing pre/post pair. If execution fails after pre, stop sampling and salvage custody, attempt post outside the final sampler and anchor spans, and finalize the **failed** bundle with its actual partial or non-pass evidence; no later passing post converts the failed run to success. A bundle that failed before a measured window began need not invent a post. Mock and non-Mac targets carry an explicit non-claim applicability outcome checked against their authenticated config and provenance; they never synthesize an Apple battery pass. Thus not every finalized diagnostic or failure bundle needs a post, but every claimed measured bundle does. This prevents both a missing-post success and the loss of useful failure evidence.

## Q6 — Historical bundles

**Decision:** Exempt a **fixed, authenticated historical set** for diagnostic re-reduction. Before BFG-S activation, inventory its members by complete bundle digest and an existing committed pack or custody receipt that binds the bundle identity and bytes; freeze that allowlist in the reviewed change. The exact prospective boundary is the BFG-S production merge commit **H**: every bundle outside that already fixed set, including a bundle produced later by an old binary, requires the new battery key and pair. A historical replay exemption does not make a battery-free bundle eligible for a new claim. `metadata.git_commit`, timestamps, `passed`, and the existing `(run_id, config_sha256)` legacy pair are writable within a bundle and cannot grant the exemption. This avoids rejecting every preserved replay while preventing an attacker from labeling a new capture “old.”

## Q7 — Scored reducer evidence

**Decision:** `scored_reduce.reduce` should take a `CaptureBatteryEvidenceIndex` produced by a `bundle_read` custody loader from an authenticated campaign bundle manifest, not a caller-authored map of `passed` values. Each entry binds `(registration_sha256, roster_sha256, block_id, attempt, envelope_index, bundle_sha256)` to the verified bundle digest, parent metadata digest, and `authenticate_non_derivation_window` result. The reducer checks **exactly one** matching, passing entry for every capture window before `_check_window` or score contribution; missing entries, duplicate keys or bundle hashes, a mismatched window identity or digest, and any non-pass or custody refusal stop reduction. The producer must verify the actual finalized bundle against the externally pinned digest; a frozen Python object by itself is not an authentication boundary. This closes the present route where a caller supplies only a plausible `bundle_sha256` string.

## Q8 — Calibration candidates

**Decision:** Gate at the **loader before `verify_stored_evidence_physics` reads a bound**, and check again at the evaluator boundary for directly supplied candidates. The loader authenticates the capture’s parent evidence and both raw files, then returns provenance bound to the ledger observation; the evaluator rechecks that provenance against the authenticated ledger and cannot trust a fabricated `CalibrationCandidate` carrying a ready-made `b_fiducial_s`. The historical boundary is an authenticated ledger head and row inventory fixed at BFG-S activation H: genesis imports and earlier battery-free ordinary rows remain available for their historical or diagnostic roles but are excluded, symmetrically in discovery and the evaluator’s complete candidate universe, as prospective claim endpoints. Every later finalized ordinary candidate needs the float proof. This prevents an old candidate from judging a new window and a direct caller from bypassing the loader with a stored B value.

## Q9 — Transaction packs

**Decision:** “Re-freeze” means **new successor pack bytes and new no-clobber receipts**, never edits to the nine frozen packs. Retire all six `_v1`/`_v2` Qwen2.5 packs from future arms. Preserve the three `_v3` packs as authenticated predecessors for the three planned `_v5` successors: `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`, and `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`. The current `d117_contrast_v5` directory is a parameterized generator; it is not the final contrast pack ID. The code’s ruled predecessor map binds each `_v5` to its corresponding Qwen2.5 `_v3`, and the new receipts should be `freeze-0004` following each predecessor’s `freeze-0003`. Author in this order: merge reviewed BFG-S code; generate the three `_v5` pack trees; review their registration and predecessor bindings; author fresh readiness sources and evidence against that code head; commit those inputs; run the freeze command with the specified `_v3` predecessor; commit and verify each new receipt and plan-tree pin. Editing any of the nine frozen source trees would invalidate their committed digests and custody chain.

## Q10 — Wall meter

**Decision:** Float is **insufficient on its own** for a wall-meter energy claim. Retain WALL-METER-GAIN-01’s separate requirement for a registered bound on net battery energy over the capture, either measured as a correction from the wall side or excluded by design. The ±200 mA readings screen instrument state at two points; they neither integrate battery energy nor detect an excursion between those points. Treating them as an energy bound would make the wall-meter gain number unsupported.

## Q11 — PR split

**Decision:** The scout’s order is right, with a firm activation fence: first land BFG-S code, F-1’s controller attachment fix, custody and historical boundaries, consumer guards, and focused tests; then author and freeze the three `_v5` successors from the reviewed code head; only after the Revision 5 epoch **issues or stops** land ex-02 §4.11’s single predicate/text/code-pin amendment. No non-derivation arm occurs between the code change and its applicable pack freeze. The first PR must retain the current registered `update_age_s ≤ 180` predicate and replay any committed Revision 5 verdicts for agreement. Combining the later `abs(update_age_s) ≤ 180` change with BFG-S now could make issuance disagree with its harvest verdict by design.

## Q12 — Additional truth risks

**Decision:** Add three explicit review checks. First, prove the external digest anchors proposed in Q2 exist and are consumed by *every* claim path; `session.json`, `metadata.json`, and `BundleReader.raw_metadata()` can otherwise bypass a self-consistency check. Second, audit consumers beyond the named reducer—especially floor extraction, campaign reduction, reports, figures, and direct calibration evaluation—so none promotes a diagnostic or historically exempt result into a new claim; extend ex-04’s AST guard only with narrow named calls to the new helper. Third, make the post-read failure and raw-file write failure tests distinguish custody damage from an authentically recorded probe failure. These checks prevent a correct parser and a correct primary consumer from coexisting with an unguarded path to a number. The ruled endpoint-only limitation remains an explicit disclosure.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| BFG-S code and tests | start_now | Cold ruling on the evidence and historical contracts before final merge | Battery module, quiet collector, controller, readers, calibration and scored consumers |
| Three `_v5` pack freezes | wait_for | Reviewed BFG-S code head and generated pack inputs | New pack sources, evidence, receipts and plan-tree pins |
| Revision 5 §4.11 amendment | wait_for | Epoch issued or stopped | Predicate, registered “Window verdict” text and module pin |
| Non-derivation arm | wait_for | BFG-S code and applicable pack freeze complete | Measurement custody and claim admission |

## Critical path

1. Rule the custody anchor, historical inventory, and pack names; implement and review BFG-S without changing the registered future-time predicate.
2. Author and freeze the three new `_v5` packs against that reviewed code.
3. Open non-derivation arms only after their code and custody gates pass. Keep the §4.11 amendment behind the Revision 5 issued-or-stopped event.

| Q | Decision | Confidence |
|---|---|---|
| 1 | Explicit quiet and bundle phases | High |
| 2 | Shared replay helper plus external parent-digest anchor | Medium |
| 3 | One pair per 600-second envelope | High |
| 4 | Fail the pilot claim on any non-pass envelope | High |
| 5 | Require post for claimed measured bundles; preserve failed bundles | High |
| 6 | Fixed, digest-authenticated historical replay set | Medium |
| 7 | Receipt-produced evidence index with exact one-to-one binding | Medium |
| 8 | Loader gate before physics and evaluator recheck | High |
| 9 | Three `_v5` successors from `_v3`; retire six older packs | High |
| 10 | Keep WALL-METER-GAIN-01 | High |
| 11 | Code, packs, then post-epoch amendment | High |
| 12 | Audit outer anchors and every claim consumer | Medium |