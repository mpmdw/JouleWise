```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend explicit phases, authenticated container-bound evidence, envelope-level quiet brackets, fail-closed claims, and the existing three v5 successors; identify custody, attachment, scheduling, and PR-split gaps.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "exact",
    "head_start": "64e39bb937e79c710886acf13fbfab295526aa18",
    "head_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "upstream_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "BFG-S evidence and compatibility contracts", "action": "needs_ruling"},
      {"row": "BFG-S implementation", "action": "wait_for", "wait_for": "Cold adoption of evidence, historical-boundary, and split contracts"},
      {"row": "Three existing v5 successor packs", "action": "wait_for", "wait_for": "Reviewed BFG-S code and existing v5 authoring prerequisites"},
      {"row": "Nine frozen Qwen2.5 pack rewrites", "action": "do_not_start"},
      {"row": "Non-derivation measurement arms", "action": "wait_for", "wait_for": "BFG-S verification and applicable successor readiness"},
      {"row": "ex-02 section 4.11 amendment", "action": "wait_for", "wait_for": "Revision 5 epoch issued or stopped"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "64e39bb937e79c710886acf13fbfab295526aa18",
          "64e39bb937e79c710886acf13fbfab295526aa18"
        ]
      },
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
      "text": "Non-derivation authentication needs an explicit trust anchor and a controller pre-finalization route; a frozen dataclass or adjacent checksum alone does not supply either.",
      "needs": "Adopt the Q2 contract before implementation."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "ex-03 F-1 explicitly requires re-freezing in the same PR; the scout proposes a separate successor-pack PR.",
      "needs": "Explicitly supersede the same-PR sentence if adopting the recommended split."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The scout omits attachment raw-byte retention, the post-collection session rewrite, and consequences of added probe latency for QPE scheduling.",
      "needs": "Include the Q12 obligations in the implementation charge."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This is a static design consultation. No implementation, test suite, hardware probe, or measurement campaign was executed.",
      "needs": "Lead owns implementation verification and live gates."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Evidence contract and historical boundary | needs_ruling | This consultation’s adjudication | Authentication, failure classification, replay compatibility |
| Code, F-1, consumer guards and tests | wait_for | Adopted contracts | Battery module, controller, readers, collectors |
| Three `_v5` successor packs | wait_for | Reviewed code and existing `_v5` prerequisites | Sources, evidence, receipts, family publication |
| Nine frozen pack trees | do_not_start | — | Immutable historical bytes |
| Non-derivation arms | wait_for | Code verification and applicable readiness | Measurement machine |
| §4.11 amendment | wait_for | Revision 5 issued or stopped | Predicate, registered text and module pin |

These are design recommendations for the magistrate, not installed rulings.

## Q1 — Observation phases

**Decision:** add explicit phases. The complete enumeration is:

```text
arm_check
publish_install
t0
validate_install
t0_power_row
slot_pre
slot_post
quiet_pre
quiet_post
bundle_pre
bundle_post
```

**Reason:** preserve `slot_pre/post` for captures already written by the fiducial writer, including ordinary calibration captures; use `quiet_pre/post` for collector envelopes and `bundle_pre/post` for controller runs. Quiet observations bind to the session UUID and scheduled envelope identity; bundle observations bind to the writer’s run ID and authenticated config identity. Their slot identity is null. Add an explicit run-ID field rather than silently overloading a derivation identity. Retain the observation schema as an explicitly ruled additive extension; reject phase/owner-kind disagreement during authentication. No `round_pre/post` phases are needed under Q3.

**Failure prevented:** accepting a valid observation from a different kind of window, or treating a null-slot record as a valid derivation slot.

## Q2 — Non-derivation verdict and custody

**Decision:** introduce a container-bound evidence seal and one consumer helper:

```text
battery_float.authenticate_window_pair(
    *,
    source: AuthenticatedWindowSource,
    expected_identity: WindowIdentity
) -> AuthenticatedWindowEvidence
```

**Reason:** the derivation seam’s terminal ledger and committed verdict cannot be imitated with an ordinary dictionary. `AuthenticatedWindowSource` must carry an independently authenticated owner identity, the expected digest of the enclosing evidence document, retained raw bytes or a constrained reader, authenticated measurement boundaries and boot identity, and any sealed battery verdict. For a quiet envelope, the document is the final session record bound to its night/envelope receipt; for a bundle, it is metadata bound to the run’s capture evidence and subsequently its completed-bundle receipt. A proposed `joulewise.battery_window_evidence.v1` seal records those identities, document/raw digests, predicate identity, status, and module digest. Its expected digest comes from trusted producer state or an authenticated enclosing receipt—not a checksum found beside the same mutable files. At initial controller reduction, use a scoped producer-owned snapshot before finalization; subsequent replay authenticates the completed capture. This explicitly accommodates the existing reduce-before-finalize lifecycle without changing `reduce.py` or `bundle.py`.

The helper’s refusal classes should be:

- `source_unauthenticated`: missing or invalid enclosing authentication.
- `identity_mismatch`: wrong owner, registration, run/session, attempt, phase or measurement support.
- `custody_failure`: a pinned document or recorded raw digest no longer authenticates.
- `record_invalid`: ambiguous structure, duplicate members, unsafe paths or invalid domains.
- `verdict_mismatch`: a sealed verdict disagrees with replay.

An authentic source that records no observation, a failed probe, or matching but stale/unparseable bytes produces `battery_float_evidence_missing`; an authentic predicate failure produces `battery_float_confounded`. Neither admits a claim.

**ex-02 distinction:** digest-recorded bytes that disappear or change are custody failure even when the original probe failed. They cannot become a replacement-triggering instrument verdict. Record the module digest for reconstruction; do not refuse solely because it changed. Refuse a changed verdict. Add only the named in-module parser access to the AST allowlist, with its self-test; consumers use the new seam.

**Failure prevented:** swapping observations between captures, laundering deleted evidence into an exclusion, and mistaking internally consistent hashes for authenticated provenance.

## Q3 — Quiet collector bracket unit

**Decision:** bracket the **600-second envelope only**.

**Reason:** the collector runs one power recorder across its rounds, and the pilot retains and pairs envelope interiors. Per-round battery probes would execute inside that recorder’s capture and change the apparatus whose energy and observer cost are being measured. Place pre before observer accounting and the first envelope stamp; place post after recorder teardown, the final stamp and observer accounting. Keep the absolute schedule, interior and deadline unchanged. If pre fails, retain its record/raw bytes and a structured zero-capture refusal; start neither recorder nor rounds, and perform no local retry. If collection exits early, attempt post only after teardown and the last estimator stamp are established. An absent post remains missing; later desk recovery cannot manufacture a contemporaneous post observation.

**Failure prevented:** measurement contamination by repeated probes, collecting after failed admission, and promoting an interrupted envelope through otherwise complete rounds. Endpoint-only coverage remains an explicit limitation.

## Q4 — QPE-01’s frozen exclusions

**Decision:** **(b), refuse the pilot claim on any non-pass envelope; leave the exclusion list unchanged.**

**Reason:** battery authentication is a prerequisite to trusting this pilot’s scientific output. It must run over the complete expected envelope inventory before existing exclusions, pairing, sizing or stop decisions can produce a claim. Battery failure must not be translated into `collect_error` and then quietly discarded while the remaining envelopes size block two. Retain diagnostics and reasons, but emit a pilot refusal with no usable sizing or scientific stop conclusion. This does not revise v3’s selection algorithm or add a replacement route: successful admission uses the same registered analysis, while failure withholds the entire claim. The BFG-S ruling should state this external prerequisite explicitly. Selective battery exclusion or altered collection scheduling would instead require v4 registration.

**Failure prevented:** an unregistered retention rule hiding behind an existing exclusion name, particularly one that permits pooling the surviving envelopes.

## Q5 — Controller failures and unsupported targets

**Decision:** every **claim-bearing measured window** requires an authenticated passing pair; every finalized diagnostic failure bundle need not contain a successful post read.

**Reason:** after pre succeeds, any failure before post leaves the run non-successful. Preserve existing cleanup and failure-bundle finalization. Attempt post at most once, after sampler teardown and all relevant closing stamps; failure to establish teardown is a reason to leave post absent, not to probe beside a possibly live sampler. A recovered passing post does not erase the original runtime failure. A failed pre stops before baseline sampling. Non-Mac targets and Macs without an applicable battery source do not receive an automatic pass: their physical applicability needs an authenticated, separately ruled policy. Mock execution may remain useful as explicitly synthetic diagnostics, but synthetic evidence cannot satisfy the physical claim gate.

**Failure prevented:** failure-path salvage becoming successful scientific reduction, fabricated post observations, and host/platform or mock labels becoming battery bypasses.

## Q6 — Historical bundles and prospective enforcement

**Decision:** exempt a **fixed, authenticated historical set**, rather than infer contract version from bundle metadata.

**Reason:** define a cold-approved historical manifest \(H\), frozen at adoption, containing exact bundle/capture identities and digests of every immutable input consumed by replay. Pin the manifest’s bytes in reviewed code or an existing authenticated registry. Authentication must include metadata, config, events, traces, relevant attachments and raw files—not merely `(run_id, config_sha256)`, a date, `git_commit`, or a “legacy” flag. The exact prospective boundary is: **every input not byte-authenticated as a member of \(H\) requires BFG-S evidence**, including unidentified older inputs and captures made with old software after adoption. A matching historical input preserves only its historical replay status; it does not acquire a battery pass or become eligible for a new BFG-S campaign. Until the historical inventory is approved, \(H\) is empty.

**Failure prevented:** removing the new key, backdating metadata, or copying an old identity to obtain an exemption. It also preserves reproducibility for specifically authenticated historical work without granting an open-ended legacy route.

## Q7 — Scored-reducer evidence

**Decision:** require an immutable `AuthenticatedCaptureWindowSet`, produced by a new `bundle_read.authenticate_scored_capture_windows(...)` loader.

**Reason:** a 64-character `bundle_sha256` says nothing unless a producer has authenticated the corresponding bytes. The loader takes authenticated registration/execution bindings and bundle locators, verifies completed bundles using the existing complete-bundle digest algorithm, invokes the Q2 seam, and returns entries bound to registration digest, roster-in-force digest, block ID, attempt, envelope index, run ID, bundle digest and measurement support. It should also bind the energy inputs—`gross_j` and anchor terms—to that same capture, so a clean battery bundle cannot accompany another bundle’s energy. `scored_reduce.reduce(..., *, window_evidence=...)` verifies exact correspondence before consuming scores or energy. The evidence object is an output of authentication, not a caller-constructed mapping whose `passed` field is trusted.

Refuse:

- Missing evidence for any supplied capture window or required live capture.
- Duplicate entries, even byte-identical duplicates; check before constructing a dictionary.
- Extra or unknown entries.
- Any identity, digest, support or energy-binding mismatch.
- Any non-pass live capture or custody/authentication refusal.

A block genuinely recorded as not started needs no invented bundle. Shared bundle evidence may cover multiple blocks only when authenticated execution provenance establishes their distinct supports.

**Failure prevented:** substituting a clean bundle’s battery result for a dirty capture, silently overwriting duplicate evidence, and scoring authenticated-looking caller-supplied numbers.

## Q8 — Calibration bracketing

**Decision:** gate **at the loader before physics**, and require the resulting proof at the evaluator.

**Reason:** `_load_calibration_candidate_unbounded` currently computes physics before `_candidate_from_observation` finishes binding the candidate to its ledger observation. Pass authenticated ledger/source bindings into the loader so parent evidence and battery custody are established before `verify_stored_evidence_physics` or bound extraction. Carry the resulting proof with the candidate; the evaluator rejects direct prospective candidates without it before accessing their bound. Historical compatibility uses an explicit pinned capture inventory tied to authenticated ledger receipts and artifact digests, analogous to Q6. The already pinned genesis acceptance remains a schema fixture under its existing non-production restriction; it does not exempt arbitrary candidate captures. A prospective target cannot choose historical compatibility merely because its acceptance generation or protocol is old.

**Failure prevented:** evaluating a confounded bound before checking its evidence, bypassing the loader through direct candidates, and confusing a historical acceptance artifact with permission to use unverified new endpoints. Preserve the complete-ledger enumeration check: do not silently remove rejected candidates and select a favorable remainder.

## Q9 — Frozen transaction packs

**Decision:** “re-freeze” means successor generations. Retire all nine old packs from future transaction arms, preserving their historical bytes; use the three existing `_v5` successors of the `_v3` families.

**Reason:** the current code already supplies the naming and predecessor mapping in `_RULED_V5_PREDECESSOR_PACK_IDS`. There is no reason to mint nine branches of successors or invent `_v4_bfgs` names. The six `_v1/_v2` packs remain historical ancestors; the three `_v3` packs remain authenticated immediate predecessors. Their continuing use as immutable calibration-plan inputs does not authorize their old transaction readiness.

| Immediate predecessor | Successor |
|---|---|
| `d117_floor_qwen25_1p5b_v3` | `d117_floor_qwen3-1p7b_v5` |
| `d117_floor_qwen25_7b_v3` | `d117_floor_qwen3-8b_v5` |
| `d117_contrast_qwen25_1p5b_vs_7b_v3` | `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` |

Authoring order:

1. Land reviewed BFG-S code and satisfy the existing `_v5` scientific/design prerequisites.
2. Complete and review all three successor plan trees and registered inputs.
3. Author sources/evidence against that reviewed code; commit the required pre-freeze bytes.
4. Freeze each successor with its explicitly mapped `_v3` predecessor.
5. Commit the new receipts and plan-tree pins, then complete the existing family-publication and confirmation checks before transaction admission.

The receipt ordinal follows its predecessor: the `_v3` receipt is `freeze-0003`, so these successors receive **`freeze-0004`**, despite `_v5` in their names. The current code derives that ordinal; the older runbook’s suffix-equals-ordinal description should not override it.

**Failure prevented:** rewriting historical custody, reviving obsolete campaigns, and creating successor identities that the installed registry cannot authenticate.

## Q10 — Wall-meter windows

**Decision:** the separate **WALL-METER-GAIN-01 bar remains mandatory**.

**Reason:** the ruled float predicate screens endpoint instrument state for powermetrics windows. It does not establish net battery energy over a wall-meter capture. The capacity-register difference is diagnostic and cannot supply the missing energy bound. Wall-meter claims remain unavailable until the separate registered method bounds battery energy or excludes the battery path by design.

**Failure prevented:** presenting a thermal-state screen as an energy-conservation correction.

## Q11 — PR split

**Decision:** adopt code → successor packs as the dependency order, with a separately gated §4.11 amendment; **explicitly amend the same-PR requirement before using two PRs**.

**Reason:** successor evidence should authenticate reviewed production code, which makes a separate pack PR sensible. However, ex-03 §8 F-1 expressly says “Re-freeze … in the same PR.” The scout’s proposal is therefore not already authorized by the cited texts. The cold ruling should replace that sentence with an explicit two-PR dependency and retain the prohibition on non-derivation arms until applicable readiness passes. The later predicate/text/code-pin amendment depends on Revision 5 issuing or stopping, not inherently on pack completion. If it changes a source pinned by an already frozen successor, that successor needs its own governed update before another arm; “third PR” must not imply readiness survives arbitrary code changes.

**Failure prevented:** silently weakening a ruling through scheduling language, arming between partially completed PRs, or treating a later predicate change as pin-neutral.

## Q12 — Additional truth-bearing gaps

**Decision:** add the following obligations to the implementation charge.

**Reason:** the scout identifies the principal sites, but those sites alone do not establish that observations belong to the measured inputs or that the new work leaves registered measurement semantics intact.

- **Calibration attachments need more than F-1’s deletion.** `_load_instrument_calibration_attachment` copies only manifest-listed artifacts. The battery raw files deliberately are not in that frozen manifest set. Authenticate and retain them through their evidence-record digests before physics, then cover embedded attachment replay in `BundleReader.metadata()` so unchanged `reduce.py` cannot consume an ungated calibration attachment.

- **Quiet-session sealing must account for clock attestation.** `record_attestation` rewrites `session.json` after the collector exits. A seal of the collector’s initial bytes will then fail legitimately. Preserve a sealed collector document plus authenticated annotation, or seal the final annotated document while preserving the producer’s original battery bindings. Do not “repair” a mismatch by recomputing its expected digest.

- **Probe latency has registered consequences.** QPE-01 has a 620-second pitch, 600-second envelope, 20-second gap, ten-second collector-start exclusion and two-second subsequent-spawn abort. Pre consumes start slack; post consumes a gap already used by parsing, cleanup and attestation. Test these interactions with bounded slow probes. Preserve scheduled deadlines and report actual drift; do not shift the interior, extend capture, shorten cleanup or hide the added CPU cost.

- **Replay checks need measurement support, not just file identity.** Authenticate boot/clock domains, finite timestamps, pre/post order, and containment of baseline, capture and sentinel stamps. A valid pair from the right directory is insufficient if its timing does not bracket the claimed measurement.

- **A fresh probe is not necessarily a fresh gauge update.** Keep the ruled gauge-age test and disclose endpoint sampling. Do not require `UpdateTime` to advance between short brackets without a ruling. Do not introduce the future-age fix early; the current negative-age limitation remains until §4.11.

- **Failure inventory must survive filtering.** Validate expected envelopes and captures before existing exclusions or “complete row” filters. Missing directories, missing post records and custody failures cannot disappear through `continue`, optional-dictionary defaults or tolerant readers.

- **The AST guard must cover new producer shortcuts.** A new seal writer must not become another replay-only consumer backdoor. Name its allowed callers and test actual controller, summary, scorer and bracket consumer paths.

**Failures prevented:** ungated calibration bounds, legitimate attestation being misclassified as tampering, altered measurement timing, misplaced observations, accidental early predicate amendments, and selective disappearance of inconvenient evidence.

## Critical path

Cold adoption of Q1/Q2/Q4/Q6/Q8 and the Q11 split precedes implementation. Reviewed code precedes successor-source authoring and freeze. Applicable successor verification precedes transaction arms. Revision 5 issuance or stop independently gates the indivisible §4.11 amendment.

No repository files changed. Verification was static inspection plus clean-worktree/base checks; no suite or hardware measurement ran.

| Qn | Decision | Confidence |
|---|---|---|
| Q1 | Add explicit quiet and bundle phases | high |
| Q2 | One container-authentication seam with an independent trust anchor | med |
| Q3 | Envelope brackets only; failed pre prevents capture | high |
| Q4 | Whole-pilot claim refusal; frozen exclusions unchanged | high |
| Q5 | Passing pair required for claims; diagnostic failures may lack post | high |
| Q6 | Fixed byte-authenticated historical set; everything else prospective | med |
| Q7 | Authenticated capture-window set bound to identities, bytes and energy | high |
| Q8 | Loader gate before physics, evaluator proof check | high |
| Q9 | Three existing `_v5` successors; nine old packs retired from arms | high |
| Q10 | Retain WALL-METER-GAIN-01 | high |
| Q11 | Split is sound only with explicit supersession of “same PR” | high |
| Q12 | Add attachment, sealing, timing and completeness obligations | high |