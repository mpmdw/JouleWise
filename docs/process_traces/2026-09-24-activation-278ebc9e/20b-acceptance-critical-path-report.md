```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "No currently registered science night is armable on 25G83; instrument resolution and an issued live-epoch acceptance are the critical path to G2-a.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "bbe475e5c410d9177f41a47101029ff15109523f",
    "head_end": "bbe475e5c410d9177f41a47101029ff15109523f",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "25G83 instrument attribution and acceptance route", "action": "start_now"},
      {"row": "G2-a arm", "action": "wait_for", "dependency": "issued live-epoch acceptance, regenerated bindings, fresh arm checks"},
      {"row": "R-Q1/R-Q2 calibration night", "action": "wait_for", "dependency": "new registration, meter payload and claim gates; live-epoch acceptance for calibrated rails claims"},
      {"row": "MATH energy feasibility pilot", "action": "needs_ruling", "dependency": "prospective pilot registration and energy-boundary decision"},
      {"row": "_v5 G2-b", "action": "wait_for", "dependency": "G2-a selector, desk day, pack rehearsal and live-epoch calibration"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "E242 still says Ed's answer is pending although his 09-19 option (c) answer is recorded; Q2 READY does not discharge A159's A179 dependency.",
      "needs": "Lead reconciles the kernel and records the operative acceptance route before an arm."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The registered three-night FAIL route was stopped by Ed's option (c); neither 09-19 equivalence night counts. Instrument repair may require a new prospective acceptance design.",
      "needs": "Cold gate and Ed settle restore-versus-recharacterise and any replacement acceptance rule."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| 25G83 instrument work | `start_now` at the desk; schedule a quiet diagnostic only under its own approved plan | Cadence attribution, then restore or deliberate recharacterisation | Quiet machine and any calibration capture |
| G2-a | `wait_for` | A179 completion and fresh `bind-window`/check | One exclusive quiet window |
| R-Q1/R-Q2 calibration night | `wait_for` | Prospective registration, meter import and alignment, 32k desk smoke, calibrated rails basis for claims | One exclusive quiet window |
| MATH feasibility pilot | `needs_ruling` for a new energy pilot | Revised pilot registration and measurement boundary | Quiet energy capture; off-window problem sizing can proceed |
| `_v5` G2-b | `wait_for` | G2-a selector and desk day, pack rehearsal, calibrated brackets | One exclusive quiet window |

The council’s order is explicitly conditional: its G2-a READY premise was unverified, and its R-ORDER requires the calibration night to pass its own gates. [Council ruling, lines 50–54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:50).

## Critical path

**Q1 — A179 state.** Step 1, the bootstrap cold gate, and step 2, its derivation-session writer, ledger, issuer and night-chain implementation, are **done**. The pre-registration specifies three 12-slot windows on **distinct calendar days**, a required retained corpus of at least 19, and no outcome-driven top-ups. It is [the 25G83 pre-registration, lines 139–179](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:139); implementation landing is recorded at [RUN_STATE.md:204](/Users/edr/code/wt-278ebc9e-g2a/RUN_STATE.md:204). Ed then made those three nights the **FAIL fallback**, initially allowing a successful one-night equivalence check to continue r6. [D-102 addendum, lines 6719–6725 and 6758–6786](/Users/edr/code/wt-278ebc9e-g2a/docs/decision_log.md:6719).

Step 3’s *current eligible corpus* is **not started**. Two equivalence sessions on 09-19 produced INCONCLUSIVE and FAIL, but Ed chose option (c): **neither counts**, and no further derivation night is to be armed before resolving the changed instrument cadence. [Ed’s recorded answer, lines 1–19](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:1); [night-two harvest, lines 1–4 and 36–40](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:1). Thus step 4, corpus derivation and cold science gate, is **not started** for a successor. Step 5’s **25G83 successor** D-138 transaction is **not started**; the later r7 reissue is a different transaction and still says `os_build: 25F84`. Step 6, regenerated live-epoch G2-a inputs with a passing fresh-clone binding, is **not done**. [A179 acceptance text](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:1075); [r7 artifact, lines 3–26](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:3); [G2-a binder, lines 638–674](/Users/edr/code/wt-278ebc9e-g2a/scripts/generate_g2a_probe_inputs.py:638).

The 09-20–09-23 `qpe01` nights are **separate instrument/quiet-predicate pilots**, not A179 corpus sessions: Ed’s option (c) record says so expressly. They exercised the night machinery and measured observer overhead; the clean 09-23 rerun found the registered 0.05-core block-two level below the roughly 0.178-core observer floor. They do not issue a calibration acceptance or count toward its three days. [Ed’s answer, lines 11–18](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:11); [09-20 abort](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-20-activation-21752427/01-qpe01-pilot-n1-20260920-harvest-record.md:9); [09-23 result, lines 206–222](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-23-activation-5fe5a59b/01-qpe01-pilot-n1-20260923-0700-harvest-record.md:206).

**Q2–Q3 — What can go first?** A new `DIAGNOSTIC_NO_PACK` registration can acquire **descriptive** 25G83 data without a `_v5` pack: that class waives the pack condition only, and the `qpe01` lane demonstrates a separate evidence payload. It does **not** waive registration, census, or calibration refusals. The exact R-Q1/R-Q2 night is **not yet registered or payload-ready**; the council requires an immutable in-chain USB-C log, alignment, battery exclusions and reader-overhead segments. Its USB-C numbers must be labelled uncalibrated and boundary-mixed where applicable. A diagnostic or USB-C-only precursor is possible **after a prospective ruling and implementation**, but cannot inherit the project’s ~1 J rails attribution bound or make calibrated rails/floor claims from stale 25F84 acceptance. Claim-bearing whole-window reduction requires authenticated pre/post calibration and refuses absent or mismatched brackets. [Council R-Q1/R-Q2, lines 18–24](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18); [bundle contract, lines 605–639](/Users/edr/code/wt-278ebc9e-g2a/docs/contracts/run_bundle_layout.md:605); [D-079 epoch reason](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:15).

The same distinction applies to a **MATH feasibility pilot**: off-window problem and memory sizing can proceed; a quiet, descriptive energy pilot needs its revised registration and must label an uncalibrated boundary. It cannot silently supply the registered direct-energy J/attempt headline. `_v5` G2-b is further blocked by the G2-a selector/desk day and pack rehearsal, and its bracket binding still needs a valid live epoch. [Council R-Q3, lines 26–30](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:26); [Q3 queue row](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:703). **No existing registered science night is armable sooner than A179’s resolution today.** A newly ruled diagnostic could precede its completion, with its claims restricted to what that diagnostic actually validates.

**Q4 — Equivalence simulation.** M1 concerns the **one-night epoch-equivalence PASS/FAIL rule**, which the review estimates passes only 0.48 of unchanged-instrument cases at 12 retained captures. It is **not the three-night successor corpus’s issuance test**: that route uses prospective membership, retained-n, screen challenge, authenticated evidence and a cold science gate. Ed’s option (c) already stopped continuation from the failed equivalence nights. M1 matters if a *new* equivalence-based shortcut is proposed; it does not itself regenerate the acceptance or unblock G2-a. [Review, line 69](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:69); [corpus rules, lines 156–190](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:156); [council M1, lines 36 and 52–54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:36).

**Q5 — Shortest defensible calendar route.**

1. **Agent, now; no quiet window:** finish A243’s 25G83 cadence attribution and prepare restore-versus-recharacterise evidence. **Cold gate and Ed** settle the scientific acceptance rule and update the stale E242/A179 state. Ed’s 09-19 answer already resolves E242’s pending question; it is not permission to count either equivalence night. [A243](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:872); [Ed’s answer](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:9).
2. **Ed hardware/sudo plus agent-prepared plan; quiet window if needed:** verify the chosen physical remedy or deliberately recharacterise the sampler. Keep any diagnostic evidence separate from an acceptance corpus unless its prospective registration explicitly includes it.
3. **Cold gate/Ed, then agent:** issue a live-epoch acceptance by the newly ruled route. If the unchanged three-night fallback is reinstated, it requires **three distinct calendar days**, 12 slots per day, followed by derivation, cold science gate and the D-138 successor transaction. Starting those days on 09-24 gives **09-26 as only a conditional calendar floor** for the third capture, not a G2-a arm date. The roughly 4–5 quiet-window/day mechanism ceiling does not compress a distinct-day rule. [Pre-registration, lines 91–114 and 139–177](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:91).
4. **Agent, then one quiet window:** regenerate and authenticate G2-a inputs in a fresh clone; pass `bind-window`, check, rehearsal and live arm gates; arm the registered G2-a night without the optional meter rider if it is not ready. [G2-a scout, lines 70–88](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/17b-g2a-arm-scout-report.md:70).
5. **Agent/cold gate, with Ed for meter hardware; then one quiet window:** finish the R-Q1/R-Q2 registration, payload, meter alignment and desk smoke, and arm the calibration night with its claim boundary stated in advance. [Council, lines 18–24 and 54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18).

**Proposed revised night order:** first, one or more **instrument-resolution/acceptance windows** as the required prelude; then **G2-a**, **R-Q1/R-Q2 calibration**, and **G2-b or the MATH pilot**. This preserves the council’s science ordering while correcting R-ORDER’s unverified READY premise. If the lead wants the new calibration *diagnostic* before G2-a to obtain earlier descriptive science, that is a prospective change to R-ORDER and its claim boundary, requiring a recorded cold-gate ruling before it is armed.