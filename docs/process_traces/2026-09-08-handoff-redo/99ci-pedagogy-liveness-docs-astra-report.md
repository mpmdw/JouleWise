```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Both lenses need fixes: terminology and reconstruction gaps, incomplete decision table, and overbroad mechanism claims.",
  "workspace":{"base_requested":"655b3368","base_mode":"exact","head_start":"655b3368b34d173bda9c5660343c3a2753c0ee97","head_end":"655b3368b34d173bda9c5660343c3a2753c0ee97","upstream_end":"ac092ccd507c2e369ac4642dfce31352769ee698","branch":"docs/2026-09-08-window-liveness-docs"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"A1","severity":"should_fix"},{"id":"A2","severity":"should_fix"},{"id":"A3","severity":"should_fix"},{"id":"B1","severity":"should_fix"},{"id":"B2","severity":"should_fix"}]},
  "verification":[{"id":"V1","kind":"inspection","cmd":"git diff --check ac092ccd 655b3368","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],
  "flags":[]
}
```

## Findings

**LENS A — writing standard**

**A1 — should_fix: First-use failures, in reading order.** Locations below refer to `docs/contracts/window_liveness.md`; grouped terms share the indicated line:

- 1: window, liveness, status-publication.
- 6: owner, publication; 7: live; 8: signal.
- 13: chain, campaign.
- 18: night-plan; 23: pid, hex; 24–25: started/exited marker meanings.
- 28: sealed evidence trees; 31: payload, nonce; 32: UTF-8, JSON object.
- 38: normalized, `lstart`, token; 39: resolved absolute path; 40: acquisition, `campaign.lock`.
- 43: exclusive lock, runs root, concurrent; 45: dispatching, measurement child; 46: speculative-decoding; 46–47: dry runs, maintenance/verdict-only.
- 48: usable start identity; 49: refusal; 50: stale-lock repair.
- 54: flush; 55: owned; 58: device number; 59: unlinking.
- 67: Path values, deduplicated; 71: reread/reconciliation.
- 76: child session; 77: settling; 81: descriptor; 82: process-group identifier/group leader; 83: Unix epoch.
- 85: probe identity; 89: open chain, valid `start_time`; 92: subprocess; 94: threat model.
- 97: usable recorded group; 105: monotonic-clock; 129: reaping; 132: UNKNOWN.
- 155: reused PID, stale; 162: structurally valid; 164: WARN.
- 174: lock-reclamation semantics, acquisition lifecycle.
- 238: commit-freeze sentinel; 240: stage, commit, push.
- 250: snapshot guard; 252: driver-managed; 254: registered; 255: uninstrumented; 258: launch fences.

Pointer additions also introduce unexplained chain/campaign, indeterminate, commit freeze, launch fences, custody, identity matching, and stale repair; linking elsewhere does not satisfy “AT first use.”

**A2 — should_fix: Neither mechanism is rebuildable from the example.** Lines 142–158 demonstrate whitespace normalization only: no complete six-field probe response, concrete reused timestamp, zombie/error trace, registry JSON, multi-parent census, or combined decision walkthrough. The exact date grammar and campaign validation predicates are omitted. The path listing is not an algorithm diagram; no labeled probe/census flow exists. The forcing problem—publication activity contaminating measurements—is missing from the contract itself. Lines 99–100 explicitly defer recovery behavior to implementation.

**A3 — should_fix: Table is not complete.** Lines 227–240 neither enumerate nor unambiguously partition LIVE/DEAD/UNKNOWN × start/exit-marker state × registry state. Missing precedence cases include malformed start plus valid exit, absent start plus invalid exit, and DEAD campaign with invalid/missing token. “Any refusal wins” cannot resolve whether those cases contribute a refusal.

**LENS B — fidelity to code**

**B1 — should_fix: Marker claims overgeneralize.** Lines 108–109 and 235 say invalid exits/malformed markers refuse. `joulewise/measurement_liveness.py:187–198` ignores every exit when start is absent, and bypasses malformed start contents when exit is valid. Lines 162 and 182 also overstate structural validity/repair refusal: DEAD campaigns bypass token validation (`:172–175`, `:204–212`).

**B2 — should_fix: “All selected parents are inspected” is false** (68). The outer exception handler terminates traversal at the first error (`measurement_liveness.py:229–262`). Publication still refuses safely.

Remaining mechanism correspondence, grouped by document sentence ranges; **M**=`joulewise/measurement_liveness.py`, **N**=`scripts/run_night.py`, **C**=`scripts/run_campaign.py`, **S**=`scripts/window_status.sh`:

- 3–8→S41–47/M41–68; 17–40→M71–72,100–131.
- 42–61→C3160–3203,7281–7288,8253–8261,8030–8035,8952–8957; M83–130.
- 63–72→M215–262; missing-parent behavior matches.
- 76–94→N105–125,360–385,431–452; atomic sequence matches.
- 96–112→N312–328,1387–1422; M159–201.
- 116–140,150–175→M25–68,166–212; probe rc semantics match.
- 178–218→M83–98,204–212; C3175–3184.
- 222–248→M266–272; S94–110.
- 250–258→M3–7,25,224–263.

The four pointers introduce no additional code contradiction.

## Residual risk

Static review only; no live measurement or test suite executed.