```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use Interactive launch context with v3, verify it in the installed night agent, and prospectively reopen the 25G83 acceptance path.",
  "workspace": {
    "base_requested": "032e9661",
    "base_mode": "exact",
    "head_start": "032e966178c09d2aa672d877f80a333d610eb6ee",
    "head_end": "032e966178c09d2aa672d877f80a333d610eb6ee",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "A: ProcessType=Interactive on the measuring night agent; retain protocol v3.",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "text": "A new acceptance must bind and check the installed measuring launch context; the present six-field epoch does not identify ProcessType."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "text": "Session C did not test display-asleep operation or the installed night agent. The first registered slot must check actual child cadence and v3 detection before the remaining slots proceed."
      },
      {
        "id": "M1",
        "severity": "should_fix",
        "text": "The old v4 simulation, stale-number audit, and equivalence disposition need a prospective v3/Interactive revision; old failed captures cannot become new corpus members."
      },
      {
        "id": "M2",
        "severity": "should_fix",
        "text": "The September idle pilots remain provisional, and nominal energy equivalence does not resolve the widened attribution interval."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B -c 'for h in (.126,.132,.237,.248,.274,.279,.419): print(f\"{h:.3f}s: interior margin {(.5-2*h)*1000:.0f} ms, 300-sample span {300*h:.1f}s\"); print(\"n12 coverage\",12/13,\"n19 coverage\",19/20)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "0.419s: interior margin -338 ms, 300-sample span 125.7s",
          "n12 coverage 0.9230769230769231 n19 coverage 0.95"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "n12 coverage 0\\.9230769230769231 n19 coverage 0\\.95"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This read-only seat did not operate an installed agent or measure display-asleep cadence.",
      "needs": "Check the first registered slot under the installed agent before continuing the window."
    }
  ]
}
```

## Findings

- **B1 — BLOCKER.** The registered identity has six fields, none of them launch context (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:17-25`). Acceptance and later brackets must record and verify the rendered `ProcessType=Interactive` night plist and the measuring child’s context. Otherwise a later default-context capture could be judged against an Interactive-context acceptance.

- **B2 — BLOCKER.** Session C tested a temporary Interactive job with the display on, and explicitly did not establish display-asleep transport (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:68-76`). Put a fixed cadence check in the **first registered slot of W1**, run by the actual installed night agent. This supplies real-path evidence without adding a separate campaign.

- **M1 — MATERIAL.** The held patch changes v3 to v4 and registers v4-specific rules. Its replay passing does not establish that v4 is needed after restoring cadence (`docs/process_traces/2026-09-24-activation-278ebc9e/38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md:60-64`). Preserve useful work, but write and seal a v3/Interactive revision before new data.

- **M2 — MATERIAL.** Session C’s energy ratio is nominally equivalent, while its worst-case attribution interval crosses the 3% bound. The default-context CPU probe is descriptive and was not paired with a completed default-context production run (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:15-26,36-45`).

## Residual risk

Timer coalescing is a supported mechanism, not a proof that no other night condition contributes. One evening, one model and prompt, and display-on testing limit transport (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:68-76`).

## Q1 — The cure

Choose **A: Interactive plus v3**. Put `ProcessType=Interactive` on `com.joulewise.night` and on the temporary `com.joulewise.night-probe.*` template, so the admission probe uses the intended context. Leave `com.joulewise.night.deadman` at its default: it supervises and does not collect samples. The night and dead-man labels currently render from one template, so the renderer must distinguish them rather than adding the key unconditionally. The installed night starts `run_night.py`; that driver starts the chain with `Popen`, and the adapter starts `powermetrics` as a subprocess. The context must reach those measuring children, verified from the rendered plist and observed child cadence, not assumed from the parent label (`configs/launchd/com.joulewise.night.plist.template:5-18`; `configs/launchd/com.joulewise.night-probe.plist.template:5-15`; `joulewise/night_agent_install.py:608-629`; `scripts/run_night.py:849-862`; `joulewise/adapters/powermetrics.py:1198-1209`).

The code asks for **one whole sample interval** inside a pulse interior, meaning two sample endpoints; the question’s “two whole samples” should not become a second detector requirement. With a 1.0 s pulse and 0.25 s inset at each end, interior width is 0.5 s. Phase-independent margin is `0.5 − 2h`: **236–248 ms** at Interactive’s observed 126–132 ms, versus **4–26 ms** at the quiet default-context 237–248 ms. The archived p95 of 274 ms already gives **−48 ms**; the reported 419 ms maximum gives **−338 ms**. These are phase guarantees, not predicted miss counts. The observed distributions and actual interior predicate are recorded at `docs/process_traces/2026-09-24-interactive-4b/01-powermetrics-cadence-launch-context.md:30-45`, `docs/process_traces/2026-09-24-interactive-4b/21-session-results-and-stop.md:24-29`, `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:7,39-41`, and `joulewise/powermetrics_fiducial.py:61-65,97-102,751-761`.

**Concern — BLOCKER:** require the installed-context check in Q2. **Executable text:** “Change only the measuring night label and temporary probe to `ProcessType=Interactive`; keep v3’s 1.0 s pulse and all existing detection gates. Render and verify each label separately, and record the sampler child’s delivered cadence.”

## Q2 — Sufficiency of the evidence

Session C is enough to **adopt and review the cure**, not enough by itself to declare an unattended acceptance window sound. Interactive completed every tested production run, with median idle cadence 131.8 ms and 300 samples taking 39.6 s against the production 55 s bound. The earlier 130 ms criterion failed; the purpose-based ≤150 ms and valid-run criterion passed (`docs/process_traces/2026-09-24-interactive-4b/24-osctx-continuation-v2_5.md:26-32`; `docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:28-35`; `joulewise/adapters/powermetrics.py:1464-1470`).

Use W1 slot 1 as the smallest real-path check. Before arming, register that its cadence result may be read immediately without reading `B`. Run the normal installed night job with the intended display state. Continue slots 2–12 only if the 300-sample idle capture finishes within 55 s, its median native interval is ≤150 ms, and the v3 capture detects all 59 pulse interiors. An isolated anchor failure remains an ordinary invalid slot and does not alone disprove the cadence cure; a cadence or interior failure stops the window for diagnosis. This is a prospective stop rule, so it does not select on a seen bound. The separate anchor mechanism occurred in 2/24 old captures (`docs/process_traces/2026-09-24-activation-278ebc9e/38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md:43-52`).

**Concern — BLOCKER:** session C left display-asleep operation untested. **Executable text:** “Seal the W1 slot-1 cadence stop before arming. Run slot 1 through the installed `com.joulewise.night` agent with the display asleep; continue only on the stated timeout, median-cadence, and 59-interior results. Record anchor failure separately.”

## Q3 — Registration

Append a new, dated revision to **`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`**; preserve revisions 1–3 as history. The held Revision 4 names v4 and therefore cannot simply be landed for this cure (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:128-147,514-525`; held branch diff of that file).

| R-ACC-2 element | Ruling for v3/Interactive | Reason |
|---|---|---|
| (a) Epoch and seal | **Change:** keep the six-field 25G83/v3 epoch; additionally bind the rendered Interactive measuring context and its verification as an operating condition. Seal final registration and chain bytes before W1. | Launch context changed delivered samples without changing any of the six identity fields (`docs/process_traces/2026-09-24-interactive-4b/01-powermetrics-cadence-launch-context.md:39-51`). |
| (b) Two 12-slot windows ≥6 h apart | **Keep as the successor fallback**, with the same settle, cadence and window budget. W1 first runs the fixed equivalence rule below. | Separate starts sample time-dependent host conditions; distinct calendar dates have no physical boundary. The 600 s settle and 600 s slot timing are registered at `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:99-114,143-147`. |
| (c) Retained n ≥12 | **Keep for a new successor**, conditional on a v3/Interactive simulation and the issuer/D-126 addendum. | Twelve makes the maximum a 92.3% next-draw screen under exchangeability, which can cost later capture yield; it cannot admit a capture above that screen. Brackets and claim intervals remain the safety gates. The held v4 simulation does not validate v3 (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:35-37,65`). |
| (d) Count-only W3 and futility | **Keep:** W3 only below 12 retained after W2; stop after W1 below 8 valid. Add the Q2 slot-1 cadence stop. | Counts measure whether the instrument is producing enough usable evidence, without selecting on `B`. |
| (e) Blindness | **Change narrowly:** the presealed D-102 equivalence branch may read W1 values when terminal; successor rules, membership and stops remain fixed beforehand. | Ed’s existing clarification defines blindness as rules fixed before data, and permits the fixed equivalence look (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:421-460,490-497`). |
| (f) Seen evidence | **Keep disclosure; exclude from membership.** | The eleven n1/n2 bounds were seen, and those captures used the defective default launch context; `qpe01` envelopes are a different protocol (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-03-evidence-inventory.md:5-16`). |
| (g) r6 screen challenge | **Drop as a successor issuance veto; report diagnostically.** | It would reject the already observed context-shifted data by construction; the new corpus must set its own level screen (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:31-33`). The r6 screen remains binding **only** for a prospective D-102 PASS. |
| (h) Excursions | **Keep no `B`-based exclusion and the `>0.075 s` count/`excursion_limited` disclosure. Reassess the v4 draft’s categorical `>0.25 s` issuance refusal before sealing v3 rules.** | Large bounds can make a phase split unusable, but a fixed “one sample interval” rationale no longer fits 126–132 ms cadence. A detected, feasible high bound is carried into the screen and claim interval; a physical fit failure already refuses (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:156-171`; `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:43-45,65`). |
| (i) S/C zero headroom | **Keep for a successor, with the dated D-125/code amendment.** | `S=C` gives zero budgetable excess and existing drift checks refuse above S; refusing issuance merely because the corpus is unusually tight has no physical benefit (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:232-248`). |
| (j) Stale-number audit | **Keep and revise for two branches.** | D-102 PASS carries r6 numbers unchanged; successor issuance derives new numbers. The held audit assumes v4 and a new successor throughout (held branch `37-acc-stale-number-audit.md`, lines 1–16). |
| (k) Simulation | **Change to v3 at Interactive and the tested display state; report its assumptions and false-admission counts before W1.** | The held v4 simulation’s interior geometry does not transfer to v3. A finite zero count is a check of the implemented gates, not proof of zero population risk. |
| (l) Barrier basis | **Keep the physical gates; add launch-context and slot-1 checks; drop distinct-day and the obsolete issuance challenge.** | The code’s whole-interior, SNR, anchor and authenticated bracket gates directly control detection and attribution (`joulewise/powermetrics_fiducial.py:751-770`; `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-02-acceptance-rules.md:11-12`). |

**D-102 is available again only prospectively.** Before W1, seal one fresh, single-look equivalence rule using the existing r6 operative comparisons: at least six valid resolved W1 captures, every `B ≤0.032898493715362 s`, and W1 range `≤0.009724 s`. PASS licenses nothing until a dated 25G83 continuation addendum lands; FAIL follows the presealed successor branch. If fewer than six resolve, follow the existing second-equivalence-window rule. Disclose that the 09-19 n2 test already failed under the old context; do not reclassify it as a PASS or erase it (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:387-393,421-470`; `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-02-acceptance-rules.md:9-10`). The old n1/n2 captures and all 09-23 `qpe01` envelopes remain diagnostic or design evidence, never members of the new prospective corpus (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-03-evidence-inventory.md:5-16`).

**Concern — MATERIAL:** the conditional W1 look and fallback membership must be written before W1, including the fewer-than-six branch. **Executable text:** “Append and seal a 25G83/v3/Interactive revision with the table’s dispositions and one prospective D-102 look. Implement the matching context guard and issuer changes; do not reuse any previously seen capture as a member.”

## Q4 — Fate of the v4 work

Close the held v4/rev4 PR **without merging it**, preserve its branch as a fallback, and name this trigger: the installed Interactive W1 slot-1 check fails from cadence/interior geometry, or W1 has fewer than eight valid slots because of interior misses despite the intended context. Return those failure bytes to council before activating v4. The deterministic v4 replay demonstrated zero geometric misses in 1,416 counterfactual pulses, but it tested the old slow-cadence problem (`docs/process_traces/2026-09-24-activation-278ebc9e/38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md:58-64`). Salvage the stale-number inventory, reissue *procedure* if a future pinned estimator change actually requires it, excursion diagnostics and simulation harness. A v3 launch-plist change alone does not justify repinning the v3 estimator as r8; r8 was the prerequisite for landing the v4 estimator-code change (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:34-35,63`).

**Concern — NIT:** do not describe the v4 replay as evidence of a changed macOS binary. **Executable text:** “Close the v4 PR as superseded by the launch-context cure; retain its branch and identified reusable work. Reopen a revised v4 plan only on the named real-agent failure.”

## Q5 — Science risk and contaminants

The default launch context is **operationally unusable for the tested production path**: three quiet attempts timed out while collecting the 300-sample idle baseline. Its compute bias remains unmeasured; two later cold default-context CPU probes took 0.98 times Interactive time, so “all inference was throttled” is unsupported (`docs/process_traces/2026-09-24-interactive-4b/21-session-results-and-stop.md:20-29`; `docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:36-45`). No claim-bearing launchd corpus was found. September fiducials remain useful for diagnosing failure; September idle pilots remain **provisional** for planning and cannot become a qualified idle cutoff or acceptance (`docs/process_traces/2026-09-24-interactive-4b/03-launch-inventory-scout-sol.md:98-124`). The paper should disclose the launch-context correction, 11/24 old fiducial validity, the nominal Interactive/shell comparison and its attribution limitation, and any absolute phase-split allocation sensitivity. A cadence ratio alone does not multiply the historical ~1 J or ~5 J bars (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-02-acceptance-rules.md:14-20`).

For window admission: quit Wispr Flow before quiet windows; it averaged 5.3–5.8% of a core in session C, an uncontrolled background load (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:47-66`). Test **display asleep** in the installed-agent slot and use the same recorded display state for derivation and later science brackets; session C’s display-on assertion cannot answer that question (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:5-11,73-76,89-90`). Land and verify PR #410’s clone relocation **before W1**: every fresh historical measurement clone was indexed, systematically adding work near measurement time (`docs/process_traces/2026-09-24-interactive-4b/29-spotlight-gap-measurement-clones.md:5-25`). Record network-time state, but do not make an ambiguous `systemsetup` return a new owner stop; clock-step and anchor gates decide validity. Session C’s calls returned rc 0 while logging `Error:-99`, and observed anchor bounds were ≤4 ms (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:87-90`).

**Concern — MATERIAL:** do not promote provisional September energy to a paper claim. **Executable text:** “Admit W1 only after clone relocation is verified, Wispr Flow is closed, display state is recorded and matched, and the ordinary quiet census passes. Preserve September records as labelled diagnostics; report actual clock and census flags.”

## Q6 — Order and authority

Replace R-ACC-6 with: desk PR for the Interactive measuring/probe context, dead-man-specific rendering, context verification, prospective v3 registration and conditional D-102 rule → revise the stale-number audit and v3 simulation → focused checks and cold science/code gate → land PR #410 and confirm clone exclusion → seal the registration and final chain/head pins → arm W1 with the ordinary notice-NO handback → use W1 slot 1 as the real-agent cadence check → finish W1 → execute the one presealed equivalence look → on PASS, land the D-102 continuation addendum; on FAIL, run W2 ≥6 h later and count-only W3 if needed, derive and cold-gate a successor → regenerate G2-a bindings and arm the first science night, which is the calibration night under COUNCIL-407-01. Existing registration distinguishes issuance from arm authorization and requires subsequent ordinary captures to use an issued acceptance (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:7-13,253-259`; `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:69-75`).

The council and magistrate own experiment design and the agent-runnable desk, Git, installation and verification steps. Ed retains hardware and sudo decisions, the right to say **NO** at the arm notice, and publication of claims; a separate registration acknowledgement is not required under the later D-184 addendum (`docs/decision_log.md:12168-12174`). **R-ACC-5 stands as an operational auto-update hold through November 30** because a build change invalidates the epoch, but it is not a scientific PASS criterion or a reason to wait on Ed when an authorized agent can set it. Verify the live build at arm; any change stops that epoch (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:69-73`; `docs/decision_log.md:12122-12128`).

**Concern — BLOCKER:** no science bracket is licensed by W1 PASS alone; the continuation addendum or successor artifact must land first. **Executable text:** “Execute the sequence above, recording the W1 branch and installed-context evidence. Send Ed the after-the-fact design summary and normal arm notice; reserve owner action for the four listed authorities.”

## Q7 — What would prove this path wrong

A real installed Interactive child delivering the old 237–248 ms tail, timing out its 300-sample baseline, or missing v3 interiors disproves transport from session C; **W1 slot 1** detects it. A display-asleep effect detects the same gap there. A high invalid rate despite good cadence points to anchor, SNR or another mechanism; W1’s named invalid reasons and the `<8/12` stop detect it. A D-102 FAIL with sound captures disproves continuation of the r6 envelope but leaves the prospectively registered successor route. A new acceptance that allows default-context brackets would disprove the binding implementation; desk tests and installed-plist verification must refuse it. A clock step, unexpected background process or Spotlight activity is detected by existing anchor, census and clone-location evidence, not by changing a threshold after seeing outcomes (`docs/process_traces/2026-09-24-interactive-4b/21-session-results-and-stop.md:24-29`; `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-02-acceptance-rules.md:7-12`; `docs/process_traces/2026-09-24-interactive-4b/29-spotlight-gap-measurement-clones.md:19-25`).

**Concern — MATERIAL:** a successful one-slot check supports the installed path, not every future night; each capture’s normal gates still apply. **Executable text:** “On any named failure, stop the affected window, preserve its evidence, and return the specific mechanism to council. Do not switch pulse protocols or reinterpret old values in place.”

## Where I expect the other seats to be wrong

- Treating the 130 ms harness criterion as a hard limit after its registered, purpose-based replacement passed.
- Adding v4 despite 236–248 ms phase-independent v3 margin at observed Interactive medians.
- Treating a temporary launchd harness as proof of the installed, display-asleep child context.
- Calling the default-context CPU probe proof of universal energy equivalence.
- Reusing the failed September captures as unseen acceptance members.

## For Ed

The slow power sampling followed how the overnight job was launched. An Interactive launch restored sampling close to its earlier speed in a controlled test. I recommend keeping the original one-second timing pulses and checking them in the first real overnight calibration slot. The older September measurements remain useful for diagnosis, but they do not issue a new acceptance. If a fresh calibration night fits the existing accuracy limits, the existing acceptance can continue; otherwise a new one is derived from fresh captures. No paper claim proceeds until that acceptance is recorded.