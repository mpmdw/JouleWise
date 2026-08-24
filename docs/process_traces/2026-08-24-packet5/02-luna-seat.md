```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Operational review finds the packet path citation drift, an overbroad premise, and recommends γ for multi-night cure survivability.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
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
    "findings": [
      {
        "id": "F3",
        "severity": "blocker",
        "title": "Current night-of path is not executable as unattended T-0",
        "text": "D-149 requires a mechanically evaluated GO receipt, but the repository says the evaluator may still be built; E-10 remains a documented NO-GO target and the unattended launch/relaunch mechanism is a separate missing work order."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Fixation still breaks the current real transaction",
        "text": "The current S-0 interim ruling proves the fixation commit leaves tests/test_receipt_histsem.py as the sole relevant changed path and explicitly says this governs S-0 only; the real transaction remains gated by packet 5."
      },
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Packet citation and premise drift",
        "text": "scripts/arm_readiness.py does not exist; the implementation is joulewise/arm_readiness.py. Also, the changed-set refusal is not literally triggered by every commit: allowlisted paths are subtractable and the successor path is conditionally subtractable after C-to-S authentication."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "S-0 §3.9 is option-specific and must be rewritten after selection",
        "text": "The current §3.9 expects DEPENDENCY_CHANGED_SET at the fixation head. That expectation is truthful only for the current post-derivation fixation-commit ordering."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; test ! -e scripts/arm_readiness.py; test -e joulewise/arm_readiness.py; printf '%s\\n' 'arm_readiness_path_check=pass'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "a591a912a9e29ccff72cd7ca84851050ecb3fd93",
          "arm_readiness_path_check=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "arm_readiness_path_check=pass"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The packet names scripts/arm_readiness.py, but only joulewise/arm_readiness.py is tracked.",
      "needs": "Use the corrected path in synthesis."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The option must replace the S-0 interim fixation-refusal shape before the real transaction proceeds.",
      "needs": "Adjudicate α, β, or γ and update the real transaction contract."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "D-149 auto-GO and unattended launch are specified but not fully implemented.",
      "needs": "Close T0-UNATTENDED-01 and UNATTENDED-LAUNCH-01 before a no-hands night."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The current worktree contains three untracked packet observer artifacts not created or modified by this review.",
      "needs": "Preserve and adjudicate them separately."
    }
  ]
}
```

## Findings

### 1. Citation verification

- `scripts/arm_readiness.py:4296-4322` is incorrect as a path. The tracked implementation is `joulewise/arm_readiness.py`; its current changed-set logic is at `joulewise/arm_readiness.py:4295-4322`.

- The packet premise is too broad. The gate computes a whole-tree diff, subtracts the ordinary allowlist, and separately authenticates the conditional successor path before subtracting it: `joulewise/arm_readiness.py:4295-4314`. The resulting refusal is raised only when `relevant` remains nonempty: `joulewise/arm_readiness.py:4315-4321`.

- `reviewed_main` is not merely bare `HEAD`; it requires a clean tree and exact equality of `HEAD`, local `main`, and `origin/main`: `joulewise/arm_readiness.py:4755-4776`.

- The re-author claim is verified. A committed freeze receipt causes `reauthor_clean_frozen_pack`, and an orphan freeze sidecar also refuses: `scripts/reauthor_clean.py:256-272`. The runbook states that a frozen generation must be replaced by a new family generation rather than re-authored in place: `docs/phase_2/window_runbook.md:1058-1061`.

- D-151 is verified as the first post-window-close fixation commit with independent SHA recomputation and a digest-conditional successor path: `docs/decision_log.md:10172-10185`.

- The D-149 auto-GO receipt is not in `window_runbook.md`; its normative home is `docs/process/d149-go-receipt-template.md:1-7`. The template explicitly says an evaluator “may” be built and that manual filling remains the route until then: `docs/process/d149-go-receipt-template.md:58-66`.

- The packet’s operational concern is real: E-10 remains a documented target rather than current launch authority: `docs/phase_2/window_runbook.md:1143-1153`. The unattended ruling separately records that the launch/relaunch harness does not exist and emits `UNATTENDED-LAUNCH-01`: `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:113-118`, `:141-148`.

### 2. Common current T-0 sequence

The measurement checkout is an absolute `MEASUREMENT_REPO`, never a development checkout: `docs/phase_2/window_runbook.md:28-34`. Before the night, the operator verifies a clean checkout and exact reviewed `main`: `docs/phase_2/window_runbook.md:769-788`.

The current machine sequence is:

1. After S-0, Ed performs the ruled pre-campaign reboot; the no-reboot span then runs through campaign close: `docs/decision_log.md:178`.

2. Source `window.env`, change to the measurement checkout, and run the ordered E-4 through E-9a wrappers. The runbook forbids invoking wrapped commands separately: `docs/phase_2/window_runbook.md:870-902`.

3. Run the clock, quiet-prep, prewindow, ledger-readiness, and reservation captures: `docs/phase_2/window_runbook.md:904-974`.

4. Author T-0 evidence with `scripts/author_arm_evidence_t0.py`: `docs/phase_2/window_runbook.md:1001-1008`.

5. Immediately run `scripts/generate_arm_readiness.py arm`, then `verify`: `docs/phase_2/window_runbook.md:1087-1113`.

6. Produce the D-149 receipt before first capture. Its five conditions are council readiness, arm freshness, quiet machine, boot/clock discipline, and no-retry acknowledgement: `docs/process/d149-go-receipt-template.md:15-39`.

7. The current documented launch is one `scripts/launch_window.py` invocation, which consumes the capability and `execve`s the frozen chain: `docs/phase_2/window_runbook.md:1119-1142`. It is not yet production authority: `docs/phase_2/window_runbook.md:1143-1153`.

Ed’s confirmation is exact-byte confirmation of table `C`: the producer renders final bytes including literal `YES`, computes `hC`, presents both, and Ed’s yes names `hC`; the bytes are then promoted unchanged: `docs/contracts/d117_step6_confirmation_table.md:37-41`. `hC` is supplied out of band, and a consumer without it refuses without changed-set subtraction: `docs/contracts/d117_step6_confirmation_table.md:49-56`. Publication, scheduler pre-arm, and T-0 require `C`, its sidecar, Ed’s `YES`, clean state, semantic replay, and strict four-way head equality: `docs/contracts/d117_step6_confirmation_table.md:188-192`.

D-150b now delegates the mechanical comparison to the magistrate, with Ed notified rather than blocking the comparison: `docs/decision_log.md:177`. That does not remove the table’s authority or the requirement that `hC` be independently recomputed.

### 3. Per-option operational walkthrough

#### α — custody-external fixation bytes

1. Use the measurement checkout at the evidence-derivation/window-close head. Do not create a post-derivation Git commit.

2. Mint or otherwise finalize the successor pinset before that head is armed. This is mandatory unless the code is also changed to accept external successor bytes, because the current C→S gate reads the successor blob from the reviewed Git head: `joulewise/arm_readiness.py:4241-4252`.

3. Write a new external fixation record containing the successor digest/counts and the window/head binding into window custody. The current repository has external custody for the marker and confirmation table, but no fixation-record schema or producer: `docs/contracts/d117_step6_confirmation_table.md:8-12`, `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1988-1995`.

4. Build `C` over the finalized marker and successor bytes. Ed/magistrate confirms the exact `C` bytes and `hC` before publication and arm.

5. Run the common E-step sequence from the unchanged checkout. The changed-set diff is empty at arm time, so the current arm can remain on the same head.

Physical custody: the new fixation record, `C`, marker, and sidecars live outside the Git tree under window custody. The current contract’s sidecar is only transport integrity, not authentication: `docs/contracts/d117_step6_confirmation_table.md:43-56`.

The principal foot-guns are confusing the external fixation record with the committed successor blob, copying a stale external record, or placing `hC` inside an allowlisted repository path. The fixed-point rule explicitly forbids that last move: `docs/contracts/d117_step6_confirmation_table.md:58-62`.

#### β — arm after fixation, with fixation included in the derivation head

1. At window close, apply the reviewed fixation delta. The current S-0 procedure changes exactly `tests/test_receipt_histsem.py`: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1763-1783`.

2. Substitute the successor SHA and prove the changed path remains exactly that file: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1785-1810`.

3. Run the differential suite, commit the fixation, and update local and remote `main`: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1812-1835`.

4. Only now author the evidence receipts, so their `derivation_commit` is the fixation commit. Then run arm and verify from that same reviewed head.

5. Build and confirm `C` at the fixation head, supply `hC`, issue the D-149 receipt, and launch once.

Physical custody: the fixation bytes live in the Git commit, principally `tests/test_receipt_histsem.py`; the confirmation table and arm receipt remain external. D-151 itself defines fixation as the first commit after window close: `docs/decision_log.md:10178-10185`.

The foot-guns are order reversal, failing to push the fixation commit so four-way equality fails, and making any additional commit after evidence authoring. The operator must also avoid treating a stale pre-fixation evidence receipt as reusable.

#### γ — registered window-head-pinned arming

1. Create a window property containing the exact window head, tree, pack digest, and custody identity. Use a dedicated checkout pinned to that head, not a live development checkout. The current runbook does the opposite: it requires exact reviewed merged `main`: `docs/phase_2/window_runbook.md:769-771`.

2. Build `C` with the pinned window head/tree and successor digest. Confirm `C`/`hC` before arm. The current table already carries Git head/tree fields, but current consumers demand live four-way equality rather than a registered window property: `docs/contracts/d117_step6_confirmation_table.md:188-192`, `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md:68-76`.

3. Author T-0 evidence and arm against the pinned checkout. The arm receipt, D-149 GO receipt, launch manifest, and consumed capability must all cross-check the same window property.

4. Run the common E-step sequence and launch from that pinned checkout.

5. If `origin/main` advances afterward, the active window continues to use the registered pinned head. A cure commit is used only by registering a new window head and creating a new arm for the next night.

Physical custody: the pinned head/property is external window custody; the actual code remains in the pinned Git checkout; `C`, arm receipt, and GO receipt are external custody artifacts.

The foot-guns are accidentally launching from live `main`, registering a property whose tree or pack digest does not match the checkout, and treating ancestry as sufficient. The marker ruling rejected ancestry-only binding because an old published head remains an ancestor after `origin/main` advances: `docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md:68-76`.

### 4. Night-2 cure commit under D-150a

The current no-retry rule says a refusal ends the lane; a new attempt requires a newly frozen session: `docs/phase_2/window_runbook.md:1159-1172`. Any reboot or HEAD change voids authored receipts, and a frozen generation cannot be cleaned/re-authored in place: `docs/phase_2/window_runbook.md:1018-1024`, `scripts/reauthor_clean.py:263-272`.

- α: a cure commit on live `main` still invalidates the current strict four-way arm. The operator must preserve/abort the affected lane, create a new family generation, and repeat evidence, arm, and GO. The no-reboot span can continue, but the existing arm cannot be reused.

- β: same result after the initial reorder. The current arm is tied to the post-fixation derivation head; a night-2 cure becomes a later relevant change and requires a fresh transaction. β does not support an in-place hotfix.

- γ: the existing night-1 window survives a `main` advance because it is pinned. The operator lands the cure in a separate development/main checkout, registers a new window property at the cure commit, creates a new pinned measurement checkout, and performs fresh evidence authoring, arm, verify, GO, and launch for night 2. No reboot is required, but the frozen pack-generation rule may require a new family generation rather than re-authoring the old one: `docs/phase_2/window_runbook.md:1058-1061`.

No option safely injects a cure into an already-running foreground chain; launch is an exact frozen `execve` path and the capability is single-use: `docs/phase_2/window_runbook.md:1119-1142`.

### 5. New-mechanism build cost

Common to all three options:

- A mechanical D-149 evaluator for C2–C4; the current template leaves this as future work: `docs/process/d149-go-receipt-template.md:63-66`.
- The unattended launch/relaunch mechanism; the repository explicitly records it as absent and separately gated: `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:113-118`, `:141-148`.
- A real-transaction/S-0 rewrite and re-ratification, because the current S-0 §3.9 is an interim fixation-refusal proof only: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2112-2143`.

α-specific:

- Fixation-record schema, producer, sidecar, atomic custody placement, and recovery.
- Arm/publication changes to authenticate external fixation bytes.
- A rule deciding whether the successor pinset itself must already be committed or is also external; current code requires the reviewed-head Git blob: `joulewise/arm_readiness.py:4241-4252`.
- New S-0 probes proving external fixation cannot be swapped, stale, or confused with `C`.

β-specific:

- A transaction orchestrator that commits fixation before evidence derivation.
- A hard check that every arm receipt’s derivation head equals or contains the fixation commit.
- Revised sequencing for `C`, `hC`, Ed/magistrate confirmation, evidence authoring, and arm.
- New S-0 green-path proofs showing the changed set is empty at the post-fixation derivation head.
- A documented new-generation rollover for post-arm cures.

γ-specific:

- Window-head registry/property schema and append-only custody record.
- Pinned-checkout creation and launch enforcement.
- New head-binding logic across `reviewed_main`, arm, publication, scheduler pre-arm, T-0, GO receipt, and launch consumption; current code only implements live four-way equality: `joulewise/arm_readiness.py:4755-4776`.
- Explicit binding of window-close head, fixation head, pinned arm head, tree, pack, `C`, and `hC`.
- S-0 falsifiers proving that live-main advancement does not alter the pinned window, while a checkout/property mismatch refuses.
- New next-night rollover procedure and new-generation handling for cure commits.

### 6. S-0 §3.9 consequence

Current §3.9 is explicitly “after window closure and fixation”: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1988-1995`. Its interim ruling expects `DEPENDENCY_CHANGED_SET` at `$FIXATION_COMMIT`, with the residue exactly `['tests/test_receipt_histsem.py']`: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2112-2131`.

- α should replace that with a clean changed-set assertion and restore the eleven-kind arm-side census.
- β should also replace it with a clean changed-set assertion because fixation is part of the derivation head.
- γ should assert exact pinned-head equality and permit unrelated live-main advancement, while separately testing that a changed pinned checkout refuses. If γ retains post-derivation Git fixation, it must retain a two-head fixation relation; otherwise it should use β’s post-fixation derivation order.

### 7. Recommendation

For one fixed, single-head night, β is the simplest operator procedure: ordinary Git, strict four-way equality, and one obvious rule—fix first, author evidence second.

For the stated campaign spanning nights with a possible night-2 cure, I recommend γ. It is the only option that lets the operator land a cure on `main` without invalidating the already-armed window. The active window remains pinned; the cure becomes the next window’s explicitly registered head. α and β both require abandoning the current arm after a cure commit.

The recommendation is conditional on building the missing window-property and pinned-launch mechanisms. No option is executable tonight under the current `WINDOW-COUNCIL-GATE`, which prohibits quiet-Mac work while the repair program proceeds: `RUN_STATE.md:4695-4702`.

### 8. Strongest losing-side argument

β is the strongest alternative. It has the smallest semantic surface, reuses the existing strict four-way head binding, keeps fixation auditable in Git, and makes the night-of order mechanically understandable: fixation commit, push, evidence authoring, arm, verify, GO, launch. Its decisive weakness is the night-2 cure case: once armed, any later code commit still invalidates the current head/derivation relationship, so it cannot preserve the existing window while adopting the cure.

## Residual risk

The current runbook still labels the production E-10 path as NO-GO, and the workspace is globally barred from quiet-Mac execution. This review therefore assesses operational designs, not live hardware readiness.