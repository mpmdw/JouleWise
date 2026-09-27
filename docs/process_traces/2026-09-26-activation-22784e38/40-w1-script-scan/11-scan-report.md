```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Static scan found two confirmed three-plist assertion failures, a retired notice address, and two publication checks that do not enforce their observations.",
  "workspace": {
    "base_requested": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "base_mode": "exact",
    "head_start": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "head_end": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/",
    "docs/process_traces/2026-09-26-activation-22784e38/20-coldgate-sweep-erratum/11-opus-contract-refuter.md",
    "docs/process_traces/2026-09-26-activation-22784e38/40-w1-script-scan/"
  ],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","file":"step2-desk.zsh","line":106,"type":"confirmed failure"},
      {"id":"F2","severity":"blocker","file":"step3-notice.zsh","line":43,"type":"confirmed failure"},
      {"id":"F3","severity":"blocker","file":"step3-notice.zsh","line":47,"type":"retired recipient"},
      {"id":"F4","severity":"should_fix","file":"step4-publish-install.zsh","line":71,"type":"census gate gap"},
      {"id":"F5","severity":"should_fix","file":"step4-publish-install.zsh","line":10,"type":"directive gate gap"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git rev-parse HEAD; git status --short --branch",
      "cwd":"/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1",
      "observed":{"result":"pass","exit_code":0,"tail":["97082508f3648ff8575c94b0cdfcf657ba440142","## HEAD (no branch)"]},
      "expected":{"exit_code":0,"tail_regex":"## HEAD \\(no branch\\)"}
    },
    {
      "id":"V2",
      "kind":"other",
      "cmd":"zsh step2-desk.zsh; zsh step3-notice.zsh; zsh step4-publish-install.zsh; zsh step5-verify-and-exit.zsh",
      "cwd":"/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts",
      "observed":{"result":"not_run","exit_code":null,"tail":["NOT EXECUTED"]},
      "expected":{"exit_code":0,"tail_regex":"STEP5 OK"}
    }
  ],
  "flags": [
    {"id":"R1","kind":"verification_gap","level":"nonblocking","text":"Steps 3–5, live census, owner directives, battery reread, launchd probe, and install were NOT EXECUTED.","needs":"Lead performs live gates."}
  ]
}
```

## Findings

**F1 — confirmed step 2 failure.** [step2-desk.zsh:105](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/step2-desk.zsh:105) says `render-only emitted exactly night and dead-man plists`; line 106 asserts:

```python
assert {p.name for p in paths} == {"com.joulewise.night.plist", "com.joulewise.night.deadman.plist"}
```

The staged directory contains three plists. Main adds the plan probe to render targets at [night_agent_install.py:1392](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/night_agent_install.py:1392). Replace those two lines with:

```python
print("CHECK: render-only emitted exactly night, dead-man and plan probe plists", flush=True)
assert {p.name for p in paths} == {"com.joulewise.night.plist", "com.joulewise.night.deadman.plist", f"com.joulewise.night-probe.{os.environ['PLAN_ID']}.plist"}
```

**F2 — confirmed step 3 failure.** [step3-notice.zsh:42](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/step3-notice.zsh:42) says `render evidence contains night and dead-man`; line 43 asserts `assert set(render)=={"com.joulewise.night","com.joulewise.night.deadman"}`. The corrected step 2 context necessarily includes the probe; main’s label construction is at [night_agent_install.py:820](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/night_agent_install.py:820). Replace with:

```python
print("CHECK: render evidence contains night, dead-man and plan probe", file=sys.stderr, flush=True)
assert set(render)=={"com.joulewise.night","com.joulewise.night.deadman",f"com.joulewise.night-probe.{e['PLAN_ID']}"}
```

**F3 — retired address.** [step3-notice.zsh:47](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/step3-notice.zsh:47) has `print("To: claude.ai.copper531@passmail.net")`. Replace exactly with `print("To: claude2.glaring610@passmail.net")`. No step sends email. Step 3 only generates the body; [README-sequence.md:64](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/README-sequence.md:64) assigns sending to the lead.

**F4 — final census is recorded but does not block publication.** [step4-publish-install.zsh:71](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/step4-publish-install.zsh:71) is:

```zsh
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
```

For `DIAGNOSTIC_NO_PACK`, main returns zero even with foreign PIDs or workloads: [arm_census.py:55](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/arm_census.py:55), [arm_census.py:309](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/arm_census.py:309). The notice booleans are then trusted by [arm_retry.py:159](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/arm_retry.py:159). Replace line 71 with:

```zsh
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN" | tee "$ATTEMPT_DIR/arm-census-final.json"
"$PY" -B -c 'import json,sys; v=json.loads(open(sys.argv[1]).readline()); assert not (v["foreign_pids"] or v["workloads"] or v["diagnostics"]), v' "$ATTEMPT_DIR/arm-census-final.json"
```

**F5 — fresh directives are recorded but do not block publication.** [step4-publish-install.zsh:10](/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/step4-publish-install.zsh:10) fetches `directives-prepub.json` and only prints it. `retry_allowed` reads the previously filled `veto_clear` value, without reading this fresh file ([arm_retry.py:153](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/arm_retry.py:153)). Preserve the existing line and append:

```zsh
"$PY" -B -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d == [], "open owner directive requires review before publication"' "$ATTEMPT_DIR/directives-prepub.json"
```

This conservatively stops on any open owner directive for lead review.

The repaired ledger source and epoch-watch expectations are supported by the recorded step 2 output. No additional stale CLI flag, JSON key, receipt field, or step 5 assertion was confirmed. The probe receipt’s three labels, 300-frame cadence, and custody bound match [night_agent_install.py:843](/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1/joulewise/night_agent_install.py:843). I found no proposed change that relaxes the battery, digest, ledger, epoch-watch, or probe checks.

## Residual risk

Steps 3–5 are **NOT EXECUTED**. Their manual notice acceptance, battery reading, live probe, launchd state, and owner channels remain live gates. Also, rerunning step 2 from its beginning against the current staging will fail its existing `not target.exists()` assertion at line 90; the staged plan already exists. Resume from the failed render assertion under the lead’s controlled procedure.