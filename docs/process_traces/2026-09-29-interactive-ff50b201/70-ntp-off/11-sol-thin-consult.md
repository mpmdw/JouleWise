```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "CONSULT: NTP-THIN-01 — retain authenticated OFF admission; remove automatic ON and prospective log attestation, with explicit scientific and contract amendments.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "32ff901374024defa97fc3d137c5a699423676e7",
    "head_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "upstream_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"should_fix","summary":"Retain OFF receipt admission and explicitly satisfy the 600-second condition on every route."},
      {"id":"F2","severity":"should_fix","summary":"Clock fits are conditional checks, not proof that every harmful correction is detected."},
      {"id":"F3","severity":"should_fix","summary":"Main already restores ON and requires a frozen restore recipe; both need prospective amendment."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection",
      "cmd":"git diff --exit-code; git status --short --branch; git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","32ff901374024defa97fc3d137c5a699423676e7"]},
      "expected":{"exit_code":0,"tail_regex":"32ff901374024defa97fc3d137c5a699423676e7"}
    }
  ],
  "flags": [
    {"id":"F4","kind":"verification_gap","level":"nonblocking","text":"Read-only source/ruling inspection and arithmetic only; no suite, capture, clock command, log query, or live state verification executed.","needs":""},
    {"id":"F5","kind":"residual_risk","level":"nonblocking","text":"Removing H6 relies on permanent OFF as the prospective environmental condition; existing method text explicitly requires log attestation for evidence captures.","needs":"Record the replacement admission condition and supersession map before prospective captures."}
  ]
}
```
CONSULT: NTP-THIN-01

## Findings

**F1 — Minimum control and its placement**

I support leaving network time OFF permanently. Automatic restoration contributes nothing to measurement correctness under that operating policy. Keep a small, auditable OFF admission.

1. Before each capturing window, run `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off`.
2. Save argv, exit status, exact **separate stdout and stderr**, post-command wall and monotonic readings, boot identity, and window/plan identity. Save failed attempts too.
3. Admit only exit 0 and stdout byte-equal to `setUsingNetworkTime: Off\n`; refuse on an unavailable or unsaved receipt.
4. Prove the earliest capture reading is ≥600 s after the receipt on both clocks, within the same boot. Bind the receipt digest into the capture’s provenance and downstream corpus/binding.
5. Leave OFF on completion, refusal, crash, and recovery. No automatic ON command.

The supplied 20:34:38Z receipt contains both an `Error:-99` diagnostic and the Off line under one `output:` field. It does **not** establish separate stdout equality. Preserve it; use structured receipts for future windows. I did not recheck the setting.

**Exact main paths/functions that carry this control:**

| Route | Main entry points and required treatment |
|---|---|
| Derivation night | `scripts/run_night.py::run_night`, immediately before `_run_chain_once`; the capturing `Popen` is inside `_run_chain_once`. `scripts/night_chains/calibration_derivation_only.zsh` already reserves then performs its 600 s settle. Keep its pinned bytes if possible. |
| Evidence night | `joulewise/quiet_predicate_campaign.py::execute` → `establish_network_time_off` → `set_network_time`; OFF already precedes the protocol settle. `scripts/night_chains/quiet_predicate_evidence.zsh` dispatches here. |
| Evidence provenance | `scripts/sample_quiet_predicate_evidence.py::network_time_provenance` authenticates the receipt and records its digest. Extend this admission to verify timing/boot, rather than adding a second log architecture. |
| Pack night | The same `scripts/run_night.py::run_night` launch boundary covers `pack`. Require its chain’s first capture to satisfy the receipt interval; do not assume every pack chain waits 600 s. |
| Claim-window arm | `scripts/capture_t0_step.py::_command_for_step`, `_capture_step_with_dependencies`, `_validate_result` capture/check `clock-disable`; `joulewise/arm_readiness_evidence_t0.py::_derive_clock_probe` performs another exact OFF enforcement. |
| Claim launch | `scripts/launch_window.py::_assemble_launch_inputs` and `launch` authenticate the ARM and execute the frozen command; they do not themselves establish OFF. Carry authenticated receipt timing through this lineage. |

The claim runbook explicitly gives only a **180 s chain settle after final enforcement**. Its earlier ≥600 s quiet dwell does not prove ≥600 s after the later OFF command. Resolve this concretely: place the authoritative OFF before the existing 600 s dwell, or supply the remaining delay outside the pinned chain. Do not silently certify the current sequence against the new condition.

**F2 — H6, clock checks, and H7**

**Drop H6’s prospective system-log admission machinery under permanent OFF. But reject the justification that the existing fits detect every correction large enough to matter.**

`joulewise/uncertainty_evidence.py::derive_powermetrics_anchor_v3` explicitly states conditional containment, a possible non-affine excursion between stamps, and that a fitted rate cannot substitute for authenticated OFF. Its `STAMP_ORDER` contains five anchor readings. D8’s **129-reading audit** is additional historical evidence, not a universal five-stamp safeguard.

D8 sizes the distinction:

- Four of 24 captures were lost: +53.2 ms step, +4.39 ms slew, −35.9 ms slew, and a 0.47 ms arriving tail.
- W1-d01’s best line through all 129 readings departed by **170.2 µs**, below 250 µs; the five strict anchor readings nevertheless made the fit infeasible. “Residual below 250 µs” alone would have passed it.
- Accepted movements of +40.1 µs and −11.6 µs were covered by the allowance and charged drift. Their effect on C was **8.9 µs, 0.05%**.
- Standing-rate variation changed the sensitivity calculation by **505 µs in S, 3.7%**, and **554 µs in C, 2.9%**. Those are separate from the two small corrections.

Arithmetic I executed: 3 ppm gives **0.2592 s/day**, **0.594 ms/198 s**, and **1.8 ms/600 s**. The existing drift term must remain charged in full. The recorded 53.2 ms exponential tail is approximately **0.973 µs after 180 s**; the retained 600 s settle comfortably covers that recorded mechanism.

The 250 µs allowance is not automatically negligible in energy: using the method text’s pilot coefficient, 0.25 ms corresponds to **0.3925 J of conservative bound**, not a measured energy error.

Thus:

- **H5 survives**, with OFF receipt, timing, custody and refusal; its restore-ON sentence is deleted.
- **H6 goes** as prospective log-query/witness/marker admission. Replace its role with authenticated OFF admission plus unchanged clock/anchor refusals and uncertainty terms. Saved historical logs and verdicts remain evidence.
- **H7 survives as required report-only science**: state, standing rate, drift and B comparison with the predecessor, reported with first claim-bearing results. Remove its H6-dependent fields. Keep prospective registration before ON/OFF pooling.
- A known correction or material OFF/ON distribution discrepancy remains a scientific finding to adjudicate. Removing routine log queries does not license ignoring positive evidence of model failure.

Main’s method text presently says evidence captures require per-envelope log attestation. Explicitly amend that condition prospectively; removing calls while leaving that scientific claim operative would misdescribe admission.

**F3 — Reuse, retirement, and N2/N3**

Use a **fresh small branch from main**. The requested N1 comparison reports **2,666 insertions, 44 deletions across 12 files**, with a multiple-merge-base warning. A direct main-to-N1 comparison also shows substantial driver changes. Stripping N1 would retain unnecessary recovery and record interactions.

Reuse selectively from `c895f28b`:

- `OFF_ARGV`, bounded injected runner, `_command_receipt`, `_clock`, boot probe, and write-once receipt serialization.
- OFF stdout comparison and receipt/interval validation ideas.
- Focused failure, custody, identity and timing tests.
- Do **not** reuse `set_network_time_off` unchanged: it creates the restore marker first.

Drop ON receipts, restore-pending marker, `recover_network_time`, dead-man ON, log query/parser/witness, H6 reporting, NTP-specific P1–P3 proof/retry horizon, empty enforced-kinds rollout, and E2’s proof-dependent refusal-document rules.

Preserve ordinary child cleanup, truthful termination records, agent/quiet gates, and dead-man reporting. An orphan sampler can still contaminate energy; removing ON removes the NTP reason for the additional proof, not the physical need to control captures.

**N2 shrinks, but remains:** bind OFF provenance and interval admission into prospective member selection (`scripts/issue_calibration_acceptance_generation.py::_select_members`), issued-file validation and corpus verification. Preserve historical ON provenance and the no-pooling rule. No H6 replay, parser or exclusion catalogue is needed.

**N3 shrinks, but remains:** remove `restore_network_time` from `execute`’s `finally`; retire restore-dependent outcome/exit semantics; replace prospective `attest_network_time`/`pilot_summary` log exclusions with receipt admission. Preserve historical interpretation through an explicit prospective protocol boundary.

Main also hard-requires restoration doctrine: `joulewise/arm_readiness_evidence.py::_derive_doctrine_pin` derives `clock.restore_recipe.v1`, and `joulewise/arm_readiness.py` requires its restore facts. Amend these and `docs/phase_2/window_runbook.md §5A`; merely deleting the ON call is incomplete. `scripts/quiet_window_clock.sh::do_enable` and its instructions must cease being the ordinary close-out path.

Estimate, not a measured patch: **300–500 production changed lines plus 200–400 test lines**, approximately 8–12 source/test files, with registration/runbook changes additional.

**Supersession map — clause IDs in the texts inspected**

Mark each as **replacement or partial supersession**, preserving unaffected science and historical records:

- Science A3: **“H5” (§4.4)** restore sentence; **“H6” (§4.5)** in full; **“H7” (§4.6)** H6 dependencies only; **§4.7 item 3**, **§5**, **§6** enforcement/registration references accordingly. **D1, D3, D8 remain.**
- Enforcement design: **§3.2–§3.4** H6/ON artifacts and verdict architecture; **§3.6 “NR-1”–“NR-5”** H6 rollout tests; **§3.7** H6 exemption table. **NR-6** capturing-launch census can remain.
- Enforcement lifecycle: **§4.1** immediate-ON failure handling; **§4.3** restoration/recovery in full; **§4.4** unenforced-kind refusal; **§4.5** chain query/ON; **§5** query-window ruling in full.
- Enforcement integration: **§6.2–§6.3**, **§6.5–§6.6**, **“NT-C1”**, and **§6.7** H6-specific obligations; **§7.1 “H5”, “H6”, “H7”** replacement registration text.
- Bench checks **“B1”** ON portion, **“B2”–“B7”** log/ON obligations, **“B8”** H6/four-record requirements; retain a small OFF/rehearsal check.
- A1: **§4.2 “P1”, “P2”, “P3”** NTP proof; **§4.3** NTP sequence; **§4.6 “C1”–“C6”** added NTP sites; **§4.7 “T1”–“T10”** associated regressions; **§5 “D2”** recovery cure; **§6 “D3”, “D4”** parser/proof tests; **§7.2–§7.5** N1-specific fixes/desk action; **§8** lifecycle amendments.
- A2: **§3.1–§3.3 “E2”/“R3”** proof-dependent record rule; **§3.4 “R1”, “R2”** ON/proof predicates; **§3.5–§3.6**, **§5 “NIT-1”**, **§6–§7** associated N1 follow-up/gate obligations. Inherited non-NTP behavior such as **R5** is not thereby repealed.
- Cap A1: **“K2”** restore/H6 portions; **“K3”** log-count admission; **“R9”** H6 prerequisite; **§5 steps 2 and 11** H6 work; **“C5”** ON/H6 evidence requirements. Keep **C9** OFF refusal and every non-NTP cap/acceptance requirement.
- Main’s **“clock.restore_recipe.v1”** and its **“restore_after_both_backups”/“restore_after_verdict”** predicates, plus the runbook **§5A** ON close-out instruction.

**Other matters bearing on truth**

Permanent OFF does not establish long-term UTC accuracy. Main’s separate reference admission uses a **0.5 s ceiling**; at 3 ppm, drift from zero reaches that size in approximately **1.93 days**. Preserve report-only reference checks or explicitly replace their contract. Any necessary clock correction belongs between windows, followed by fresh OFF admission and settle.

Preserve the D-138/claim hold, cap gates, full drift term, 250 µs allowance, and scientific provenance. Thinning NTP does not discharge them.

## Residual risk

I inspected the named rulings, receipt, and relevant main/N1 source; I executed arithmetic and read-only Git checks. I did not replay captures, run tests, verify hardware state, or prove every pack chain’s timing. Editing estimator-file bytes remains subject to the existing D-138 transaction rules.

Leave network time OFF permanently.
Keep one authenticated OFF admission per window.
Drop H6 logs; do not claim fits prove all corrections harmless.
Keep H7 reporting and forbid unregistered state pooling.
Build fresh from main; shrink N2/N3 and amend restoration contracts.