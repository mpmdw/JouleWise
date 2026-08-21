```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Pedagogy audit found eight replication-blocking mechanism gaps and thirteen first-use, shorthand, or worked-example defects.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "d7410caa5b1db8bedbd767b36ac17dc2c1b766b6",
    "head_end": "d7410caa5b1db8bedbd767b36ac17dc2c1b766b6",
    "upstream_end": "d7410caa5b1db8bedbd767b36ac17dc2c1b766b6",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    ".decisive-replay/"
  ],
  "verdict": {
    "findings": [
      {"id":"P01","severity":"blocker","location":"§2 lines 46–56","failure":"Pulse-edge estimator lacks a rebuildable algorithm and worked calculation."},
      {"id":"P02","severity":"blocker","location":"§2 line 54","failure":"Clock-anchor set and four-term bound cannot be reconstructed from the prose."},
      {"id":"P03","severity":"blocker","location":"§3 lines 90–116","failure":"Floor calculation omits a complete numerical path through guards, widening, and guard factor."},
      {"id":"P04","severity":"blocker","location":"§3 lines 128–145","failure":"Reference-repeatability bound and final drift-to-floor calculation are unspecified."},
      {"id":"P05","severity":"blocker","location":"§4 lines 171–175","failure":"Admission predicates and settling criteria are not operationally defined."},
      {"id":"P06","severity":"blocker","location":"§5 lines 197–206","failure":"Characterization pass criteria remain qualitative and cannot be replicated."},
      {"id":"P07","severity":"blocker","location":"§6 lines 224–226","failure":"Prompt-sizing choice cannot be recomputed from the disclosed numbers."},
      {"id":"P08","severity":"blocker","location":"§7 line 274","failure":"Sampler-cadence resolution refusal has no explicit decision rule."},
      {"id":"P09","severity":"should_fix","location":"title line 1","failure":"Title uses attribution-limited and detection floor before either is built or glossed."},
      {"id":"P10","severity":"should_fix","location":"abstract line 7","failure":"Eligible, admitted, drift, and pre-registered do technical work before definition."},
      {"id":"P11","severity":"should_fix","location":"§2 line 38","failure":"Governed, authenticated, frozen, sidecars, backend, and stack identity remain undefined criteria."},
      {"id":"P12","severity":"should_fix","location":"§2 lines 58–64","failure":"Bracket formula has no real-number substitution example."},
      {"id":"P13","severity":"should_fix","location":"§2 caption line 70; §3 lines 99–116; §4 line 179","failure":"ABBA precedes its definition, cooldown remains unspecified, and no numeric block is worked."},
      {"id":"P14","severity":"should_fix","location":"§3 lines 151–163","failure":"Two-gate mechanism lacks a numeric example exercising both decisions."},
      {"id":"P15","severity":"should_fix","location":"§4 lines 165–167","failure":"Fail-closed is used in the heading before its next-paragraph gloss."},
      {"id":"P16","severity":"should_fix","location":"§2 line 78; §4 lines 179–191","failure":"Custody, covariate, quarantine, generation, and related criteria fail first use."},
      {"id":"P17","severity":"should_fix","location":"§4 lines 187–191","failure":"v2 issuance, git tree state, origin/main, head commit, and strict replay leak implementation shorthand."},
      {"id":"P18","severity":"should_fix","location":"abstract line 7; §3 lines 118 and 137","failure":"a9, a10, and p2015-df-ph-prefill-abs-r01 appear as unexplained internal identifiers."},
      {"id":"P19","severity":"should_fix","location":"§6 line 220","failure":"Holm procedure has no concrete two-test threshold example."},
      {"id":"P20","severity":"should_fix","location":"§7 line 272","failure":"Estimator code name, packs, mint, paper-regime swap, and TASK_QUEUE.md leak internal workflow."},
      {"id":"P21","severity":"should_fix","location":"lines 21, 276, 288, 300, 324","failure":"NVML, continuous batching, speculative decoding, vLLM, TensorRT-LLM, NTP, and mixture-of-experts routing fail first use."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code -- docs/paper/draft-v1.md docs/paper/figures-plan.md docs/paper/draft-v1-review-round1.md docs/paper/draft-v1-review-round2-lensA.md docs/paper/draft-v1-review-round2-lensB.md docs/paper/draft-v1-review-round3-methods.md && for f in docs/paper/figures/fig1_boundary_attribution.svg docs/paper/figures/fig2_window_timeline.svg docs/paper/figures/fig3_decision_gates.svg; do rg -q '<title' \"$f\" && rg -q '<desc' \"$f\"; done && printf 'review inputs unchanged; 3 schematics carry title and description\\n' && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "review inputs unchanged; 3 schematics carry title and description",
          "## main...origin/main",
          "?? .decisive-replay/"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "review inputs unchanged; 3 schematics carry title and description"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The SVG viewer could not rasterize the schematics; element naming was checked from SVG labels, titles, descriptions, and legends.",
      "needs": ""
    }
  ]
}
```

## Findings

All locations refer to [draft-v1.md](/Users/edr/code/JouleWise/docs/paper/draft-v1.md). The first-use rows below cover every identified class-(c) failure; terms built or glossed at first use were not promoted into findings.

| ID | Location | Exact term or passage | Clause failed | Severity | Minimal fix shape |
|---|---|---|---|---|---|
| P01 | §2, ~46–56 | “observed power plateau,” “fits … lags jointly,” “converge,” “candidate evaluations” | First-use (c); why-chain lacks rebuildable algorithm and real-number example | blocker | State the fit objective, candidate parameters, acceptance rule, and work one 59-pulse capture from commanded/observed edges to its retained bound. |
| P02 | §2, ~54 | “every combination … consistent with” and “exactly affine” | First-use (c); estimator mechanism lacks equations and worked inputs | blocker | Define the admissible rate/anchor inequalities before “affine,” then carry five example clock pairs and labels through the four bound terms numerically. |
| P03 | §3, ~90–116 | \(F_{\mathrm{abs,point}}\), \(F_{\mathrm{cmp,point}}\), “joint corners,” “guard factor” | Why-chain worked example missing; replication impossible | blocker | Add one small real dataset and calculate residuals, both point guards, the registered guard factor, interval corners, and widened maxima step by step. |
| P04 | §3, ~128–145 | “derived reference-repeatability bound” and “settled reference corpus” | First-use (c); why-chain calculation missing | blocker | Give the derivation formula and settlement predicate, then show start/mid/end values producing the excursion, allowance, and final cell floor. |
| P05 | §4, ~171–175 | “thermal pressure must be nominal,” “quiet-state criteria,” “settling interval,” “identities … checked” | Criteria words are not operational predicates; replication impossible | blocker | Replace each criterion with its measured field, threshold, sampling duration, and refusal result, or point to a complete executable protocol included with the paper. |
| P06 | §5, ~197–206 | “good fit,” “what a passing result would establish,” “stabilize,” “test containment” | Why-chain decision criteria missing | blocker | For every table row, state the statistic, frozen threshold, sample unit/count, and accept/refuse rule, with one numeric worked example per mechanism. |
| P07 | §6, ~224–226 | “projected contrast is approximately 11.6 J” and “thin design margin” | Unpaid work; sizing decision cannot be reconstructed | blocker | Show the exact projected effect, cell floor, claim-side bound, required clearance, and arithmetic that selected 256 tokens. |
| P08 | §7, ~274 | “labels those windows not resolvable at the sampler’s cadence” | Undefined decision criterion | blocker | State the mechanical resolution rule—such as the required number or geometry of fully observed intervals—and apply it to a 0.121 s phase at 112 ms cadence. |
| P09 | Title, ~1 | “Attribution-Limited Detection Floors” | First-use (c): meanings arrive at lines 7 and 118 | should_fix | Retitle in plain physical language or add a subtitle that glosses both terms immediately. |
| P10 | Abstract, ~7 | “eligible,” “conditions admitted,” “measured drift,” “pre-registered comparison” | First-use (c) | should_fix | Replace each with its plain action at first use: passed listed entry checks, conditions allowed by those checks, slow within-session change, and fixed before data collection. |
| P11 | §2, ~38 | “governed,” “authenticated,” “frozen,” “sidecars,” “telemetry backend,” “stack identity” | First-use (c); unpaid criteria words | should_fix | Define the concrete writer/check/hash/immutability operation behind each word before using it, and delete glossary nouns not needed in the paper. |
| P12 | §2, ~58–64 | \(B_{\mathrm{op}}=\max(\ldots)\) | Why-chain worked example missing | should_fix | Substitute one actual pre-bound, post-bound, and screen into the equation and state the resulting operative bound and refusal comparison. |
| P13 | §2 caption ~70; §3 ~99–116; §4 ~179 | “ABBA,” “after cooldown,” “recovery-gated cooldowns” | First-use (c); why-chain example missing | should_fix | Define ABBA before Figure 1, give the exact cooldown exit criterion, and compute one block from four real energy values. |
| P14 | §3, ~151–163 | “two separate gates” | Why-chain worked example missing | should_fix | Add one numbered contrast with a point estimate, floor, interval, registered direction, and the resulting outcome at each gate. |
| P15 | §4, ~165–167 | Heading “Fail-closed collection protocol”; definition follows afterward | First-use (c) | should_fix | Put the plain-language definition into the heading or opening sentence before the term appears. |
| P16 | §2 ~78; §4 ~179–191 | “custody,” “covariate,” “quarantine,” “generation,” “strict verification” | First-use (c) | should_fix | Gloss each where it first appears or replace it with the physical action: retained hash record, time-imbalance adjustment, excluded retry directory, policy version, and byte-for-byte replay. |
| P17 | §4, ~187–191 | “v2 issuance,” “git,” “tree state,” “origin/main,” “head commit” | Shorthand leak; mechanism buried in repository implementation | should_fix | Move repository-specific mechanics to an artifact appendix and retain one plain sentence explaining what bytes and code revision a reader must verify. |
| P18 | Abstract ~7; §3 ~118, 137 | “window a10,” “window a9,” `p2015-df-ph-prefill-abs-r01` | Shorthand leak | should_fix | Introduce each as a dated diagnostic collection with its role, or move identifiers to a provenance table and use plain descriptions in the narrative. |
| P19 | §6, ~220 | “corrected together by the Holm procedure” | Why-chain worked example missing | should_fix | Show the ordered two-test \(p\)-values and their \(0.025/0.05\) comparisons, or the exact equivalent interval rule used by the implementation. |
| P20 | §7, ~272 | `d124_two_shared_edge_common_mode.v1`, “frozen packs,” “next mint,” “paper-regime swap,” `TASK_QUEUE.md` | Shorthand leak; unpaid workflow language | should_fix | Replace the paragraph with the estimator’s physical assumption and applicability rule; move code names and project workflow state to artifact documentation. |
| P21 | ~21, 276, 288, 300, 324 | “NVML,” “continuous batching,” “speculative decoding,” “vLLM,” “TensorRT-LLM,” “NTP,” “mixture-of-experts routing” | First-use (c) | should_fix | Expand or gloss each term at first use, even when it appears only in related work or future work. |

The three schematic figures pass the named-element requirement: their axes, sampler bars, timing band, phase boundary, ABBA points and brackets, drift line, arrows, gates, and outcomes are labeled in the SVGs. Figure 1’s boundary-attribution schematic also supplies a numerical \(0.030\text{ s}\times33\text{ W}\approx1\text{ J}\) example. The ABBA/window and decision-gate schematics do not supply real-number examples, so P13 and P14 remain.

Worst sections, ranked:

1. **§2, In-window calibration method** — the physical motivation is strong, but neither the pulse fit nor clock-anchor estimator can be rebuilt from the prose.
2. **§4, Fail-closed collection protocol** — admission depends on qualitative criteria and repository vocabulary rather than measurements and predicates an independent operator can apply.
3. **§3, Detection-floor composition** — equations are present, but the unshown path through validity, guard factors, interval corners, drift, and the two gates prevents end-to-end reproduction.

Overall verdict: **not ready for the replication bar**. A committee reader can understand the thesis and the physical boundary-attribution mechanism, and the schematics are unusually well labeled. They still cannot independently rebuild the calibration estimator, decide whether a run enters the corpus, reproduce a floor from raw member intervals, or reconstruct the workload-sizing and sampler-resolution decisions. The next pedagogy pass should prioritize operational equations and real-number end-to-end examples, then reorder or remove the class-(c) terminology and repository shorthand.

## Residual risk

This review deliberately did not assess factual fidelity, code/spec agreement, statistical validity, or bibliography accuracy. HTML-commented conditional replacement instructions were excluded from the professor-facing first-use audit because they do not render, though they would remain visible to anyone receiving the Markdown source. Visual inspection was limited to SVG structure and labels because the local viewer could not rasterize the files.