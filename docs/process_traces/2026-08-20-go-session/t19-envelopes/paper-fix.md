```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Rebuilt the paper's core mechanisms and first-use pedagogy; unavailable claim-era evidence remains explicitly fenced rather than invented.",
  "workspace": {
    "base_requested": "3d0b48a",
    "base_mode": "exact",
    "head_start": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "head_end": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "upstream_end": null,
    "branch": "impl/paper-pedagogy-r4"
  },
  "pathspec": [
    "docs/paper/draft-v1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check -- docs/paper/draft-v1.md && printf 'diff-check: clean\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "diff-check: clean"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "diff-check: clean"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "if rg -n '8\\.611855|1\\.869502' docs/paper/draft-v1.md; then exit 1; else printf 'banned-literal grep: 0 matches\\n'; fi && if sed '/<!-- CONDITIONAL-INSERT-TIGHTER-FLOOR/,$d' docs/paper/draft-v1.md | sed 's/<!--.*-->//g' | rg -n '11\\.6|\\ba9\\b|\\ba10\\b|anchor-v2|\\bn=19\\b'; then exit 1; else printf 'rendered superseded-era grep: 0 matches\\n'; fi",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "banned-literal grep: 0 matches",
          "rendered superseded-era grep: 0 matches"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rendered superseded-era grep: 0 matches"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; import re,subprocess,hashlib; p=\"docs/paper/draft-v1.md\"; b=subprocess.check_output([\"git\",\"show\",\"HEAD:\"+p],text=True); c=Path(p).read_text(); o=re.findall(r\"<!--.*?-->\",b,re.S); n=re.findall(r\"<!--.*?-->\",c,re.S); it=iter(n); assert all(x in it for x in o); m=\"<!-- CONDITIONAL-INSERT-TIGHTER-FLOOR\"; assert b[b.index(m):]==c[c.index(m):]; t=r\"\\[(?:F|C)_[A-Za-z0-9_]+\\]\"; assert re.findall(t,b)==re.findall(t,c); print(\"comment-and-token-preservation: pass; original_comments=%d current_comments=%d conditional_sha256=%s\"%(len(o),len(n),hashlib.sha256(c[c.index(m):].encode()).hexdigest()))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "comment-and-token-preservation: pass; original_comments=27 current_comments=55 conditional_sha256=1be762067b210f8b0043dad0116ea4ea0dc408981c9d8bb5ac854c1d81cb733d"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "comment-and-token-preservation: pass"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -c 'from decimal import Decimal as D; from pathlib import Path; import json,re; r=json.loads(Path(\"docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json\").read_text())[0]; f=D(r[\"b_fiducial_v3_lexeme\"]); a=r[\"anchor_v3\"]; z=D(str(a[\"effective_clock_anchor_bound_s\"])); assert f-z==D(\"0.0289329345611147592\"); q=sum(D(str(a[k])) for k in (\"anchor_only_bound_s\",\"wall_minus_monotonic_span_s\",\"stamp_resolution_s\",\"numeric_padding_s\")); assert q==D(\"0.0011349971959968977402\"); c=json.loads(Path(\"configs/calibration/calibration_acceptance_d079_v2_n17_r6.json\").read_text()); v=[D(x[\"b_fiducial_s\"]) for x in c[\"derivation_corpus\"][\"members\"]]; x=D(\"0.026415695490612106\"); y=D(\"0.02501695592329986\"); assert x in v and y in v and max(x,y)+max(abs(x-y),D(\"0.009724\"))==D(\"0.036139695490612106\"); s=Path(\"docs/paper/draft-v1.md\").read_text().split(\"<!-- CONDITIONAL-INSERT-TIGHTER-FLOOR\",1)[0]; e=re.findall(r\"<!-- evidence: ([^ >]+) -->\",s); assert all(Path(p).exists() for p in e); print(\"artifact-replay: pass; evidence_comments=%d pulse_residual=%s anchor_sum=%s operative_bound=0.036139695490612106\"%(len(e),f-z,q))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "artifact-replay: pass; evidence_comments=28 pulse_residual=0.0289329345611147592 anchor_sum=0.0011349971959968977402 operative_bound=0.036139695490612106"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "artifact-replay: pass"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "P01, P02, P03, P04, P06, P07, P13, P14, and P19 require raw or fresh values that do not exist in the current artifacts; their remaining substitutions are fenced as contradictions or TODO-EVIDENCE.",
      "needs": "Supply or authorize the missing raw values, fresh results, and characterization limits, or accept the explicit evidence-fenced partial disposition."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The analysis manifest still carries pre-D-139 Holm m=1/TODO semantics, while binding decision D-139 requires a two-test family with m=2; the draft follows D-139.",
      "needs": "Reconcile the production manifest before freeze."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full unit suite was not run because the only modification is Markdown; targeted structure, provenance, arithmetic, first-use, and claim-integrity checks passed.",
      "needs": ""
    }
  ]
}
```

## Change

The revised [draft-v1.md](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a96c43-ea39-4170-96e5-126b77b16301/scratchpad/wtPAPER/docs/paper/draft-v1.md) now gives operational equations, predicates, diagrams, and first-use definitions without modifying the governed comment block or bracket tokens.

| Finding | Disposition | Result |
|---|---|---|
| P01 | contradiction | Rebuildable pulse objective, search, acceptance, convergence, ruled-out criterion, diagram, and aggregate arithmetic added. The requested maximum pulse’s commanded/fitted edges are absent from the retained derivation. |
| P02 | contradiction | Five-stamp roles, clock inequalities, causal intersection, refusal rules, diagram, and four-term composition added. The artifact omits the five raw paired readings. |
| P03 | TODO-EVIDENCE | Full absolute/comparative formulas, guard factor, exact corner enumeration, refusal cap, and diagram added; fresh claim-admissible arrays do not exist. |
| P04 | TODO-EVIDENCE | Exact settled-corpus predicate, triplicate-end reference formula, excursion, allowance, and final-floor equations added; fresh references and current corner maxima are unavailable. |
| P05 | fixed | Every admission and recovery criterion now names its measured field, threshold, duration, retry behavior, and refusal result. |
| P06 | contradiction | Each characterization row now states its statistic and independent unit, but the registry confirms that fixed counts, limits, and output files do not exist; rows therefore return “protocol incomplete.” |
| P07 | contradiction | Historical scaling and the required current clearance equation are explicit. D-139 requires a dedicated 256-token floor, but the current floor, claim bound, projection, and margin are unavailable. |
| P08 | fixed | Positive-overlap geometry, minimum three-record rule, refusal label, and real diagnostic calculation added. |
| P09 | fixed | Title replaced with plain physical language. |
| P10 | fixed | Abstract replaces or immediately glosses all technical criteria. |
| P11 | fixed | Authentication, fixed inputs, identity checks, files, and corpus vocabulary are defined by concrete operations. |
| P12 | fixed | Current-estimator bracket values are substituted through the operative-bound equation. |
| P13 | TODO-EVIDENCE | ABBA is defined before use and cooldown is operationally complete; fresh four-run energies, midpoint times, and cooldown records are unavailable. |
| P14 | TODO-EVIDENCE | Both gates, directions, refusal outcomes, and exact booleans are worked symbolically; fresh contrast values are unavailable. |
| P15 | fixed | Fail-closed is defined before first use. |
| P16 | fixed | Custody, quarantine, strict verification, time imbalance, editions, and related actions are built before use. |
| P17 | fixed | Repository mechanics were removed from rendered prose; only the physical byte/code-revision verification obligation remains. |
| P18 | fixed | Internal collection and campaign identifiers were removed from rendered prose. |
| P19 | TODO-EVIDENCE | Holm’s two-test ordering and 0.025/0.05 comparisons are explicit; fresh ordered p-values do not exist. |
| P20 | fixed | Workflow shorthand was replaced by the physical shared-edge assumption and applicability/refusal rule. |
| P21 | fixed | All listed serving, timing, and accelerator terms are expanded or glossed at first use. |

Worked examples added and their evidence:

- Pulse-capture aggregate calculation and missing-edge fence — `docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json`.
- Clock four-term composition and missing-stamp fence — the same derivation.
- Operative bracket substitution — `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`.
- Floor, guard, and corner path — `joulewise/detection_floor.py`; fresh arrays remain TODO-EVIDENCE.
- Reference-repeatability and drift/final-floor path — `configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`, `joulewise/whole_window.py`, `docs/phase_2/detection_floor.md`, and `docs/paper/results-fill-registry.md`.
- Two-gate decision example — `docs/paper/results-fill-registry.md`; fresh values remain TODO-EVIDENCE.
- ABBA and cooldown example — `docs/paper/results-fill-registry.md`; fresh block values remain TODO-EVIDENCE.
- Characterization-row substitutions — `docs/paper/results-fill-registry.md`; missing limits and results are explicitly fenced.
- Holm thresholds — `docs/decision_log.md`; p-values remain TODO-EVIDENCE.
- 256-token sizing relation — campaign consumer declaration and `docs/decision_log.md`; current decision inputs remain TODO-EVIDENCE.
- Sampler-overlap diagnostic — `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`, `docs/process_traces/2026-08-20-go-session/readiness-sitting/seat-L3.md`, and `joulewise/reduce.py`.

The mechanical first-use rerun stripped HTML comments and inspected the rendered source before the conditional block. It found 23 explicit definitions/glosses and zero targeted shorthand leaks. Newly introduced technical terms are built where first used:

- Abstract: detection floor, allowed, refusal, diagnostic, fixed before collection.
- §2 glossary/method: authenticated, registered, issued, residual bound, ruled out, converges, admissible set, bracket screen, pre-flight screen, ABBA, cooldown exit criterion.
- §3: guard factor, corner widening, settled reference corpus.
- §4: fail-closed, settling interval, quarantine, strict verification, capture-method era, time imbalance, estimand.
- §6–§8: Holm procedure, overlapping-record rule, continuous batching, speculative decoding, NVML, NTP, vLLM, TensorRT-LLM, and mixture-of-experts routing.

Both prohibited literals have zero draft matches. The rendered superseded-era scan also has zero matches. All 27 original HTML comments remain in order, the conditional block is byte-identical, and all registry bracket tokens are unchanged. No new superseded-era magnitude entered the rendered text.

## Verification notes

The main deviation is evidentiary: where the requested numerical substitution cannot be reconstructed from repository artifacts, the draft uses an explicit TODO-EVIDENCE or contradiction instead of fabricated values.

The other conflict is D-139 versus the stale analysis manifest. Named-decision precedence was applied, so the paper describes Holm correction for two tests.

## Residual risk

The lead should double-check the settled-reference formula against `joulewise/whole_window.py`, reconcile the analysis manifest with D-139, and decide whether the evidence-fenced P01/P02/P03/P04/P06/P07/P13/P14/P19 dispositions are acceptable until the next collection supplies the missing values.