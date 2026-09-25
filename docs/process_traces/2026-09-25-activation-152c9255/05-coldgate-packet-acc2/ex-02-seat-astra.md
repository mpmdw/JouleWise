```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt Interactive launch context with protocol v3; verify the installed path, then permit a fresh, explicitly registered continuation test with prospective derivation as fallback.",
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
    "recommendation": "A_WITH_REGISTERED_INSTALLED_PATH_CHECK",
    "findings": [
      {"id":"B1","severity":"blocker","text":"Session C supports adoption but does not verify the installed night-driver path."},
      {"id":"B2","severity":"blocker","text":"Keeping v3 preserves the old September captures' formal epoch; explicit prior-observation disposition is necessary."},
      {"id":"M1","severity":"should_fix","text":"The question incorrectly states that the detector requires two interior samples; production requires one whole interval."},
      {"id":"M2","severity":"should_fix","text":"The default-context CPU probe and nominal energy equivalence do not establish universally unbiased inference."},
      {"id":"M3","severity":"should_fix","text":"The existing simulation cannot establish general false-claim protection or reproduce the proposed full retained-corpus selection."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD && git rev-parse origin/feat/2026-09-24-acc-25g83-v4-rev4",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","032e966178c09d2aa672d877f80a333d610eb6ee","ea10e3c82a5dee26dc5ede04162b939455762181"]},
      "expected":{"exit_code":0,"tail_regex":"ea10e3c82a5dee26dc5ede04162b939455762181"}
    },
    {
      "id":"V2",
      "kind":"other",
      "cmd":"python3 -B -c 'for h in (0.126,0.132,0.237,0.248,0.279): print(f\"h={h:.3f} one_margin={0.5-2*h:.3f} two_margin={0.5-3*h:.3f}\")'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["h=0.126 one_margin=0.248 two_margin=0.122","h=0.132 one_margin=0.236 two_margin=0.104","h=0.237 one_margin=0.026 two_margin=-0.211","h=0.248 one_margin=0.004 two_margin=-0.244","h=0.279 one_margin=-0.058 two_margin=-0.337"]},
      "expected":{"exit_code":0,"tail_regex":"h=0.279 one_margin=-0.058 two_margin=-0.337"}
    }
  ],
  "flags": [
    {
      "id":"V3",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"Read-only council review. No installation, workload, privileged command, measurement, or test suite was run. Raw session-C idle cadence and CPU-probe medians were independently recomputed.",
      "needs":"The magistrate performs the prospectively registered live checks outside agent sessions."
    }
  ]
}
```

## Findings

- **BLOCKER B1:** Verify the cure through the installed measurement path before treating it as operationally accepted.
- **BLOCKER B2:** Explicitly dispose of prior same-epoch observations before reopening acceptance under v3.
- **MATERIAL M1:** Correct the interior requirement.
- **MATERIAL M2:** Narrow the causal and equivalence claims.
- **MATERIAL M3:** Treat the existing simulation as a limited stress test.
- **NIT:** None independently warrants delay.

These block the indicated downstream steps, not adoption of the proposed configuration change.

## Q1 — The cure

**Choose A: Interactive plus unchanged protocol v3.**

Set `ProcessType=Interactive` on `com.joulewise.night`, `com.joulewise.night.deadman`, and `com.joulewise.night-probe.<plan-id>`. The first two share one template; retaining that symmetry also avoids leaving the safety supervisor subject to the suspect scheduling treatment. The probe must represent the installed context. Leave the magistrate job unchanged. The renderer’s shared-template behavior is explicit in `joulewise/night_agent_install.py:608–629`; the separate probe template is loaded at `joulewise/night_agent_install.py:965–977`.

**MATERIAL M1:** `_fit_pulse` rejects an **empty** interior, not an interior containing fewer than two intervals (`joulewise/powermetrics_fiducial.py:751–761`). For a contiguous constant-spacing grid, an interior of width \(W\) guarantees one whole interval when \(W≥2h\), and two when \(W≥3h\).

With the nominal interior \(W=0.5\) s:

| Interval \(h\) | One-interval margin \(W−2h\) | Two-interval margin \(W−3h\) |
|---|---:|---:|
| 126–132 ms | 248–236 ms | 122–104 ms |
| 237–248 ms | 26–4 ms | −211 to −244 ms |
| 277–279 ms tail | −54 to −58 ms | −331 to −337 ms |

The source durations/inset are `joulewise/powermetrics_fiducial.py:63,97–102`; observed cadence ranges are `docs/process_traces/2026-09-24-interactive-4b/01-powermetrics-cadence-launch-context.md:41–44` and `docs/process_traces/2026-09-24-interactive-4b/21-session-results-and-stop.md:25–27`. Even the shortest authenticated pulse, 0.8 s, leaves 0.3 s interior: enough for one whole interval at a constant 132 ms, with 36 ms margin. These are geometric calculations, **not guarantees inferred from a median**; actual interval placement and gaps remain decisive.

The effect must reach the sampler and workload descendants. The harness really launches the production command as a child: at commit `845b1cc5`, `scripts/diagnostics/osctx_mvp/runner.py:59–67` sets the plist key, and `scripts/diagnostics/osctx_mvp/cell.py:113–144` launches `joulewise run` without an explicit QoS override. The retained plist confirms Interactive at `/Users/edr/osctx-mvp-01/sessionC1/C1/C1-01.2.I.a1/job.plist:14–22`; its child ancestry is recorded in `cell.json:73–104` in that same directory.

However, the recorded QoS is the **wrapper thread’s**, not every sampler/MLX thread’s (`cell.py:190–192` at that commit). Production additionally creates a new process session for its chain (`scripts/run_night.py:855–861`). Source inspection supports inheritance as the mechanism; it does not replace observing effective behavior through that chain.

C is rejected: longer pulses cannot fix the independent idle-baseline timeout. B adds protocol migration and longer excitation without a demonstrated need at the restored cadence.

**Executable text:** Install Interactive in the shared night/deadman template and separate probe template through the gated PR; retain v3 constants and hashes. Verify descendant cadence through Q2. Do not add per-child scheduling overrides unless that check demonstrates they are needed.

## Q2 — Sufficiency of the evidence

**Enough to adopt the configuration; insufficient to declare the installed path verified.**

**BLOCKER B1:** The missing evidence is a small transport check, not another equivalence experiment. Session C used a different wrapper and launch label. The production façade distinguishes real installation from fixture rehearsal and invokes a separate launchd probe before installation (`joulewise/evidence_night.py:829–850,1778–1792`). A verify-only custody probe does not demonstrate sampler cadence.

The smallest useful check is a **registered operational prefix to W1**, executed by the real installed night label, followed by W1’s first normal derivation slot:

1. Under Q5’s fixed conditions, collect one idle baseline using production’s sampler configuration and ordinary capture timeout.
2. Run the first unmodified v3 fiducial slot through the normal chain.
3. Pass only if the idle capture obtains its requested 300 records inside the existing 55 s bound; its median native interval is ≤150 ms; and the fiducial passes every existing protocol and anchor gate, including complete detection and nonempty interiors.
4. Record launch ancestry, rendered plist digest, frame distribution, and per-pulse interior counts. Continue W1 automatically on pass; otherwise terminate and diagnose. Do not repeat until one passes.

The timeout follows `joulewise/adapters/powermetrics.py:1464–1470`. The ≤150 ms operating criterion already has a declared purpose in `docs/process_traces/2026-09-24-interactive-4b/24-osctx-continuation-v2_5.md:26–32`: it provides practical timeout margin. It is not a new claim of historical equivalence.

Keep the idle prefix outside the corpus; retain the first fiducial slot under W1’s prespecified membership rule. Place the ordinary settling period after the prefix so the prefix does not change the calibration conditions.

**Executable text:** Seal this operational-prefix rule before W1, execute it without agents through the real installed job, and abort W1 on failure. Do not require a separate rehearsal night or another matched inference study.

## Q3 — Registration

Amend **`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`**. Preserve existing revisions and the held v4 draft; use a uniquely numbered **Revision 5** for this replacement.

The following dispositions replace R-ACC-2(a)–(l), whose full source is `docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:65`.

| Element | Disposition and reason |
|---|---|
| **(a) Epoch** | **Change:** retain v3 and the actual six-field epoch. Additionally bind the Interactive configuration, rendered-template hashes, display policy, and collection conditions into registration/admission. Launch context materially changes this instrument even though it is absent from the formal epoch tuple. |
| **(b) Windows** | **Change:** W1 first tests continuation. Only its FAIL branch requires W2. Keep the registered slot shape, settle, capture budgets, and separated starts. Retain ≥6 h separation for fallback W2 as modest coverage of changing background conditions—not a claim of independence or a magic thermal time constant. |
| **(c) Minimum** | **Keep n≥12 for prospective fallback derivation**, with a scoped D-126 amendment and matching issuer validation. Retain **all** valid registered members, not the first twelve. Twelve is an operating minimum, not proof of population coverage. Under exchangeable continuous observations, a subsequent draw exceeds a sample maximum with probability 1/13 rather than 1/20 at n=19. Later screens and uncertainty accounting therefore remain essential. |
| **(d) Stops/W3** | **Change:** after W1 closes, fewer than six retained observations means INCONCLUSIVE and stop for diagnosis. Otherwise apply the fixed continuation test once. PASS ends collection; FAIL runs W2. Open W3 only when fallback retained n remains below twelve after W2. No repeated continuation tests, discretionary top-ups, or selection of a favorable window. Require representation from both fallback windows; a wholly invalid window needs diagnosis. |
| **(e) Blindness** | **Change:** permit the declared W1 decision after its session is terminal. On FAIL, W1 remains part of fallback derivation, by a rule sealed beforehand. Afterwards permit only count-based scheduling until all required sessions terminate. This follows Ed’s “rules before data” definition, rather than pretending the W1 values were unseen. |
| **(f) Prior evidence** | **Keep disclosure; change disposition machinery.** Old captures inform diagnosis and design only. Their exclusion must be explicit and content-addressed; keeping v3 does not create a different formal epoch. |
| **(g) Old screen challenge** | **Drop as a successor-issuance barrier; keep as the continuation comparator and reported diagnostic.** Exceeding the old envelope defeats continuation, but is precisely why an honestly wider successor may be needed. It must not prohibit characterization itself. |
| **(h) Excursions** | **Change:** retain all valid members and report the existing excursion counts. Drop automatic issuance refusal at B>0.25 s and automatic phase-claim suspension solely from two B>0.075 s members. Those thresholds do not establish model invalidity, and “one sample interval” no longer describes 0.25 s. Investigate mechanisms and propagate the full resulting uncertainty; refuse unsupported claims through the actual physical and claim gates. An unresolved mechanism that invalidates those bounds remains a blocker. |
| **(i) Zero headroom** | **Keep:** S=max(quantized range, genesis floor), C=max(predecessor C,Q99,S), with explicit zero headroom when equal and refusal above C. This permits a repeatable instrument without reducing its charged allowance. Install the necessary dated arithmetic amendment. |
| **(j) Constants audit** | **Keep:** distinguish unchanged continuation constants from newly derived fallback constants. Inspect every consumer; neither cadence similarity nor a documentation label silently changes a comparator. |
| **(k) Simulation** | **Change:** preserve the old result as diagnostic evidence; exercise the actual revised enrollment, W1 branching, all-member retention, and downstream gates. Verify deterministic invariants and report model-dependent error/refusal rates. Do not use a finite zero count as a universal safety certificate or demand literal zero stochastic errors as an arbitrary release criterion. |
| **(l) Barrier basis** | **Change:** retain physical detection, support, clock feasibility, brackets, uncertainty propagation, custody, and prospective selection rules. Keep settle/cadence as controlled procedures, not uniquely physical constants. Drop calendar-day counting, compulsory second window after continuation PASS, and the categorical prohibition on continuation. |

**MATERIAL M3:** The existing simulation injects apparent effects at 80% of its timing allowance plus small noise. Its n=12 block-drift case uses only the first block, whereas the proposed corpus retains valid observations across windows. Its zero false admissions therefore neither proves a general error bound nor directly evaluates this collection rule. These limitations are visible in `docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README_acc_n12.md:5–16,20–35`.

**The continuation path is available again, prospectively and context-bound.** Cadence restoration makes the question plausible; it does not answer it. Use the existing comparators: retained m≥6, every B≤0.032898493715362 s, and range≤0.009724 s. These are verified in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:389–390,428–439`. PASS continues the r6 numerical envelope through the active acceptance lineage and a dated D-102 addendum; it does not issue a newly estimated envelope (`:443–470`). The addendum must make Interactive collection conditions enforceable.

**BLOCKER B2:** The n1/n2 observations cannot simply disappear. The current issuer refuses valid same-epoch observations outside the registration (`scripts/issue_calibration_acceptance_generation.py:1273–1290`). D-126 specifies disposition by content ID and recording the disposing decision in the successor’s prior set (`docs/decision_log.md:8492–8498`). Apply that mechanism explicitly, preserving the old FAIL/INCONCLUSIVE results. Also ensure those disposed observations cannot immediately retrigger staleness after continuation.

Neither n1/n2 nor qpe01 may supply new acceptance members. The former were already inspected and ruled out of derivation; the latter are idle-envelope observations, not fiducial captures. Both remain useful for mechanism analysis and disclosure (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/ex-22-packet-03-evidence-inventory.md:7–16`).

**Executable text:** Seal Revision 5 with the complete one-look W1/PASS/FAIL tree above, explicit prior-observation dispositions, and context-bound continuation authority. Implement and verify its issuer/consumer rules before capture; never relabel prior data as fresh or silently bypass a refusal.

## Q4 — Fate of the v4 work

**Salvage useful parts; preserve v4 as a named fallback, not the active plan.**

Retain the stale-number audit, zero-headroom implementation concept, cadence reporting, and simulation infrastructure after adapting them to Q3. Keep the reissue mechanism available, but do not manufacture r8 merely because an abandoned plan named it.

The held branch changes governed estimator files, including the detector and reducer. Cherry-picking its cadence reporting into `reduce.py` can itself require the atomic re-freeze; that cost is absent from a template-only cure (`docs/decision_log.md:10361–10375`). Initially, read-only postprocessing can report cadence without changing those pins.

**MATERIAL:** The replay establishes counterfactual interior coverage, not observed v4 clock validity or timeout viability. Its corrected pass criterion expressly separates fitted and unfitted captures (`docs/process_traces/2026-09-24-activation-278ebc9e/38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md:60–68`).

**Executable text:** Mark the existing PR superseded as the primary cure and preserve its branch/evidence. Activate an Interactive-plus-v4 fallback only if Q2 or the registered windows show actual `no_plateau_interior_intervals` failures despite verified Interactive ancestry. A baseline timeout instead triggers launch-context diagnosis; v4 alone is never that timeout’s remedy.

## Q5 — Science risk and contaminants

**MATERIAL M2:** No blanket invalidation or blanket rehabilitation of launchd-era evidence is justified.

Session C’s default-context probe supports “no observed slowdown in this CPU probe.” It does not measure default-context inference energy, GPU scheduling, or every workload. The probes were also cold versus post-workload comparators. The nominal energy interval is narrow, but the widened attribution interval crosses the declared equivalence margin. Small scatter cannot exclude stable context-correlated bias (`docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:17–25,38–45,70–88`).

Keep earlier launchd captures as diagnostic evidence with their recorded validity. Do not convert them into acceptance members or claims. The supplied inventory found no launchd-context MLX claim corpus; it does not prove all conceivable historical captures harmless (`docs/process_traces/2026-09-24-interactive-4b/03-launch-inventory-scout-sol.md:98–113,126–133`).

Window conditions:

- **Quit Wispr Flow and its helpers before settling.** This removes an observed, avoidable background consumer, rather than demanding zero operating-system activity. Its measured census contribution is documented at `docs/process_traces/2026-09-24-interactive-4b/26-continuation-results.md:49–66`. Quit agent processes too; sleeping agents were measurable.
- **Keep the display on at one recorded, fixed brightness for this initial acceptance and its claim windows.** Display-asleep transport remains untested. The existing evidence proves “on,” not measured brightness zero (`…/26-continuation-results.md:73–75,90`). Do not block this path on an unnecessary display-asleep experiment.
- **Land and verify clone relocation before the operational prefix/W1.** Fresh clone indexing is a systematic, avoidable exposure. Verify the actual parent exclusion; a `.noindex` suffix is insufficient. Exclusion does not eliminate app-donated Core Spotlight work (`docs/process_traces/2026-09-24-interactive-4b/29-spotlight-gap-measurement-clones.md:12–25`).
- **Retain network-time pause/restore under existing authority**, with recorded state verification and cleanup. A successful return code accompanied by an error message is not proof of the setting. Clock-anchor feasibility remains the decisive measurement check (`…/26-continuation-results.md:89`).

The paper should disclose launch ancestry/configuration, requested and delivered cadence, display conditions, background controls, the corrected causal inference, all selection amendments, and unresolved attribution limitations. Do not publish an exact claim of timer coalescing as the sole proven cause.

**Executable text:** Apply these admission conditions prospectively, retain historical classifications, and describe prior launchd data as diagnostic unless their own claim requirements independently pass. Require no repeat of session C solely to obtain a stronger verbal equivalence label.

## Q6 — Order of steps and authority

Replace R-ACC-6 with:

1. Cold ruling on this replacement design.
2. Gated desk changes: Interactive templates, context provenance/admission, Revision 5, prior-observation dispositions, continuation handling, and required fallback issuer arithmetic.
3. Land and verify clone relocation. Complete appropriate software checks and rendered-plist inspection. Reissue acceptance pins only if the selected changes actually move governed bytes.
4. Seal registration, protocol/template digests, ledger baseline, and the complete decision tree. Send the normal notice and honor NO.
5. Exit agents. Run the installed operational prefix and W1.
6. On operational failure or insufficient retention, stop and diagnose. On continuation PASS, land the authenticated context-bound D-102 continuation. On FAIL, run the registered fallback windows, then derive, cold-review, and issue the successor.
7. Regenerate downstream bindings against the actual accepted artifact. Check timing-support requirements using measured frames, not a nominal requested interval.
8. Arm the calibration science night required by COUNCIL-407-01 with fresh pre/post calibration and all standing gates.

**R-ACC-5 stands in substance:** preserve a stable build during the campaign; keep the previously ruled hold through 2026-11-30 and verify the actual build at admission. The date is a campaign-management boundary, not physical evidence (`docs/process_traces/2026-09-24-activation-278ebc9e/31-coldgate-packet-acceptance/20-coldgate-fable-acceptance-ruling.md:71`).

**MATERIAL authority correction:** The hold need not remain an Ed task if the magistrate can execute the reversible setting with existing authority. Likewise, existing authorized privileged interfaces do not automatically require new approval. Ed retains hardware actions, genuinely additional sudo authority, NO, and publication. Registration and routine operations are the council/magistrate’s responsibility (`docs/decision_log.md:12122–12128,12174`).

**Executable text:** Execute this dependency order under existing authority, using Ed only for an actual reserved action. Do not request a new design acknowledgment, a redundant quiet night, or a reissue whose only purpose is preserving the abandoned sequence.

## Q7 — What would prove this path wrong?

| Counterevidence | Where detected; consequence |
|---|---|
| Interactive does not restore cadence through the real descendants, or the baseline still times out | Operational prefix; stop before accepting the installed cure. |
| Cadence improves but v3 interiors still fail | First fiducial and subsequent slots; invoke the named Interactive-plus-v4 fallback. |
| Fresh timing bounds exceed the old envelope | W1’s fixed comparison; reject continuation and execute prospective derivation. |
| Background state or launch ancestry differs from registration | Admission and recorded census/context; refuse the affected window rather than generalize acceptance. |
| Large bounds reflect an invalid clock/support model rather than honest uncertainty | Existing physics checks plus mechanism review; block affected claims and repair the model. |
| Continuation or successor consumers ignore dispositions, changed pins, or context | Desk refusal tests and cold review; do not arm science. |

**BLOCKER:** Any demonstrated invalidity in the claimed uncertainty model remains a blocker even when cadence and repeatability look excellent.

**Executable text:** Record each outcome against this table. A failed prediction follows its named branch; do not relax its criterion after observing the result or keep sampling until continuation passes.

## Residual risk

The review did not establish display-asleep behavior, transport across workloads, or an unconditional energy-equivalence bound. Those are limits on interpretation and scope, not reasons to delay a narrowly registered display-on acceptance. No files were changed.

## Where I expect the other seats to be wrong

- Treating two interior samples as the existing detector requirement.
- Treating median cadence restoration as acceptance of the old timing envelope.
- Calling old v3 captures a different epoch merely because launch context changed.
- Using nominal energy agreement or a CPU microprobe to declare all launchd inference unbiased.
- Treating zero simulated false claims as proof, or requiring another full experiment to verify a configuration transport.

## Plain summary for Ed

Fix how the night job starts and keep the existing calibration pulses.
Check the fix once through the real night machinery, inside the planned calibration window.
Then test whether the old timing limits still fit; derive new limits only if they do not.
Keep the longer pulses ready for demonstrated pulse-detection failures.
Quit avoidable background apps, prevent clone indexing, and hold display conditions fixed.
Preserve the old recordings as diagnostic evidence, without relabeling them as fresh calibration.
The team can do this under existing authority; new approval is needed only for your reserved actions.