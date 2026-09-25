```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"STAND WITH LISTED CORRECTIONS: numerical results reproduce; interpretation and disclosures need correction.",
  "workspace":{"base_requested":null,"base_mode":null,"head_start":"e0934a593e94a44801e248c5954c7a726b99dff0","head_end":"e0934a593e94a44801e248c5954c7a726b99dff0","upstream_end":"e0934a593e94a44801e248c5954c7a726b99dff0","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"result":"STAND WITH LISTED CORRECTIONS","findings":[{"id":"F1","severity":"should_fix"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"}]},
  "verification":[{"id":"V1","kind":"inspection","cmd":"git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},"expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}}],
  "flags":[]
}
```

## Findings

**F1 — Qualify energy equivalence.** The registered v2.5 verdict reproduces, but “What this establishes” §2 overstates attribution. Say **nominal statistical equivalence under amended v2.5; attribution unresolved**. Put “widened interval crosses δ: yes” beside the verdict. The disclosed [0.861, 1.161] and v2.3 INCONCLUSIVE-by-attribution are consistent; drift ratios are 5.351–11.969%. Explain Astra’s dissent explicitly: repeatability cannot exclude stable arm-correlated bias. State that C3 and R5 changed after observing stage0U.

**F2 — Narrow mechanism claims.** Replace §1 with the tested configuration’s three session-2 timeout failures. Later, noncontemporaneous D probes demonstrate no observed slowdown for that probe; they do not establish universally unthrottled compute or prove timer coalescing as the sole cause. B demonstrates sensitivity to large slowdown. The installation gate, July/night/display-asleep limitations, unmeasured D bias, and non-claim-bearing designation are appropriate. Brightness zero is not established by the recorded display-on assertion.

**F3 — Correct census and chronology.** Independently reproduced seven flagged cells and approximately the listed CPU totals. Label the totals **13 cells including warm-up**, versus 12 inferential cells. List actual flag contributors omitted from the table: runningboardd, PerfPowerServices, ControlCenter, mds_stores. Flags concern census intervals overlapping sampling windows, with allowlisted processes excluded—not necessarily request-time interference. Wispr averages 5.3–5.8% per cell; “throughout” overstates temporal resolution. Session began **00:17:58**, accepted cells **00:21:39**, ended **01:15:48**; signpost_reporter consumed **24.66 CPU-s during warm-up**, so clarify “settled before t0.” “Valid” means diagnostic-valid: raw claim prechecks retain environment/calibration barriers.

Independent recomputation used only ledger-selected, nondiscarded raw summaries, whose hashes matched:

| Block | log(SH/I), E | log(SH/I), R |
|---|---:|---:|
| 01 | .003690872 | −.006092893 |
| 02 | −.002345323 | −.005280610 |
| 03 | −.002254119 | −.002974012 |
| 04 | −.001635338 | −.005767369 |
| 05 | .001090327 | −.004312531 |
| 06 | .000889727 | −.007389375 |

Using sample SD and independently calculated \(t_{.996875,5}=4.525716259\):

| Metric | Log mean; SD | Recomputed ratio [interval] | Write-up |
|---|---|---|---|
| E | −.000093976; .002400246 | .999906 [.995482, 1.004350] | .99991 [.99548, 1.00435] |
| R | −.005302798; .001523039 | .994711 [.991916, .997514] | .99471 [.99192, .99751] |

Both intervals lie inside [.97, 1.03]. Absolute E contrast also matches. Arm log-E SDs: **0.2966%, 0.2168%**; maximum idle baseline **0.2071 W**.

R5 matches: **131.8474 ms**, **39.5542 s/300**, zero invalid I attempts; 130-ms fails, amended criterion passes.

Probe medians match: **I 7.694060; SH 7.613914; D 7.556131; B 57.273547 s**; ratios **1, .989583, .982073, 7.443866**. These pool 18 repeats per I/SH arm and six per D/B arm.