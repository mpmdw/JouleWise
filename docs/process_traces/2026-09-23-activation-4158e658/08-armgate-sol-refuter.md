```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "ARM AFTER CURES: v3 execution bindings and schedule check out, but the notice and generated summary make false claims.",
  "workspace": {
    "base_requested": "26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15",
    "base_mode": "exact",
    "head_start": "26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15",
    "head_end": "26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "ARM AFTER CURES",
    "cures": [
      "Correct render_notice: name registration v3, the 620 s pitch and 8,020 s span, the 0.5-core gate, and the per-process 30 core-second exclusion with its two-consecutive abort; remove the false first-night and one-git-show claims.",
      "Correct the generated summary.md sentence saying busy cores are never an exclusion input.",
      "Pin a new head, clone and staged plan; rerun the tracked check, notice, veto, publish-install and verify sequence."
    ],
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "question": "Q4",
        "text": "The notice says busy cores are only descriptive, gives a 7,800 s span, calls this the first evidence night, and claims exactly one git show. The v3 rule excludes envelopes at 30 core-seconds per non-observer process; the schedule needs 8,020 s; prior pilot nights exist; t0 calls one chain-source git show and manifest verification calls git show for eight tracked files. The notice omits the 0.5-core gate and 620 s pitch."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "question": "Q5",
        "text": "The pinned campaign generates summary.md with 'Busy cores are recorded covariates and never an exclusion input.' That is false for v3 and would misdescribe the night's own exclusions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD; git status --porcelain; git diff --stat 3a411784 HEAD -- joulewise scripts configs; shasum -a 256 configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json scripts/night_chains/quiet_predicate_evidence.zsh",
      "cwd": "/Users/edr/JouleWise-measurement-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15-qpe01-pilot-n1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD 26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15; status and diff --stat empty",
          "v3 sha256 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616",
          "chain source sha256 568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "69321c693b.*568a2771"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n 'pilot_summary\\(|Busy cores are recorded covariates|non_observer_busy\\(|require_observer_marked\\(|record_covariates\\(|def execute\\(' joulewise/quiet_predicate_campaign.py",
      "cwd": "/Users/edr/JouleWise-measurement-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15-qpe01-pilot-n1",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1614: require_observer_marked(support)",
          "1615: non_observer = non_observer_busy(...)",
          "1669: report = pilot_summary(...)",
          "1441: Busy cores are recorded covariates and never an exclusion input."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Busy cores are recorded covariates"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import glob,json,plistlib,pathlib; p=pathlib.Path(glob.glob(\"/Users/edr/night-plan-staging/qpe01-pilot-n1-20260923-0700-*\")[0]); q=json.loads((p/\"prepare.json\").read_text()); print(plistlib.loads((p/\"render/com.joulewise.night.plist\").read_bytes())[\"StartCalendarInterval\"]); print(plistlib.loads((p/\"render/com.joulewise.night.deadman.plist\").read_bytes())[\"StartCalendarInterval\"]); print(q[\"schedule\"][\"boundaries\"])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "night: Month 9 Day 23 Hour 7 Minute 0; deadman: Hour 10 Minute 35",
          "boundaries: 1790171400, 1790171520, 1790171640, 1790171700, 1790172000, 1790181000, 1790181300, 1790184900"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1790184900"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Direct custody wrapper and retained-root inspection NOT EXECUTED under the custody-tree restriction. In-memory regeneration from the pinned generator and eight-file manifest produced wrapper SHA-256 464697de98a0c66938a5fa969a6460f2ce160c2346706069d3ab9eddd296fb87, matching prepare.json.",
      "needs": "Lead's tracked check must verify the published custody bytes and retained roots before arming."
    }
  ]
}
```

## Findings

**F1 — MATERIAL (Q4).** The exact false notice lines are:

> Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds; no top-up or automatic repeat.  
> During the night exactly one read-only git show verifies chain bytes in the clone; no commit, push, checkout or fetch (87a F2).

It also calls this the “first idle-variance evidence night.” The v3 schedule is **600 + 11 × 620 + 600 = 8,020 s**. The notice must describe the 0.5-core t0 predicate and v3 envelope exclusion before it is sent.

**F2 — MATERIAL (Q5).** The generated `summary.md` repeats the false “never an exclusion input” claim. Correct the pinned code and stage a new candidate.

**Q1–Q3 execution result.** The plan names H for both heads, the stated plan ID, roots, v3 path, t0 and 9,000 s window. Its staged hashes match; the clone is clean at H, and the requested diff is empty. The v3 registration and chain-source digests match their clone bytes. The rendered night and dead-man calendars, clone `.venv` interpreter paths, and all listed schedule boundaries check out. Code tracing shows `run_night.py` launches the pinned wrapper; its regenerated bytes match the staged wrapper digest, and it dispatches to the v3 campaign with the per-envelope rule, observer-marking guard and two-consecutive abort. The plan’s **v2 night-plan schema** is the expected plan format; its registration points to **protocol v3**.

## Residual risk

Published custody bytes and stale retained roots were **NOT EXECUTED** in this review. The lead’s tracked check must settle those before any arm.