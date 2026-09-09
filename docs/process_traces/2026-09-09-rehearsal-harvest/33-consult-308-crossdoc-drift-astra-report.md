```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S-A persists; T38d closes S-B; S-C remains should-fix; both requested nits are confirmed with qualifications.",
  "workspace": {
    "base_requested": "2aae25f69a6be0b11465129e353d1a27eb63c4cb",
    "base_mode": "exact",
    "head_start": "2aae25f69a6be0b11465129e353d1a27eb63c4cb",
    "head_end": "2aae25f69a6be0b11465129e353d1a27eb63c4cb",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 2
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Handback still identifies the initial cure commit as the cure under review",
        "locations": [
          "docs/process/NIGHT_HANDBACK.md:83",
          "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:84",
          "docs/process/state_kernel.json:3263"
        ]
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Handback uses prospective instruction and retains completed-night sections despite its between-nights invariant",
        "locations": [
          "docs/process/NIGHT_HANDBACK.md:4",
          "docs/process/NIGHT_HANDBACK.md:86"
        ]
      },
      {
        "id": "F3",
        "severity": "nit",
        "title": "Harvest count explanation omits the copied plan and leaves the source count undefined",
        "locations": [
          "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:56"
        ]
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "Recorded cure shape names a basis string different from the implemented measured field",
        "locations": [
          "docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md:78"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2aae25f69a6be0b11465129e353d1a27eb63c4cb"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2aae25f69a6be0b11465129e353d1a27eb63c4cb"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git rev-parse fix/2026-09-09-night-gate-stub-chain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5db38b5816bce05b67cabfe3eb621bf2b22aa3e6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5db38b5816bce05b67cabfe3eb621bf2b22aa3e6"
      }
    }
  ],
  "flags": []
}
```

## Findings

**F1 — should_fix; Opus S-A confirmed.** `NIGHT_HANDBACK.md:83` still presents `bb7090e2` as the cure under review; `21i:84` identifies the fix head as `5db38b58`. Git supports **initial cure `bb7090e2`, subsequent fix/current local cure-branch head `5db38b58`**. The bench artifacts establish the original defect, but cannot establish a later cure commit; Git is the primary evidence for that fact.

`RUN_STATE.md:19` correctly distinguishes the two commits. Kernel `:3263`, copied into both queue views, also distinguishes them, but incorrectly attributes that complete account to `NIGHT_HANDBACK §Executed`: the handback does not mention the fix-round commit.

Minimal correction: handback `at `5db38b58` (PR #309) under review`; remove or correct the kernel note’s attribution to the handback.

**F2 — should_fix; Opus S-C substantially confirmed.** The clause “the next plan’s author rewrites…” describes future required conduct, not an observed state. Its actor is broader than the opening’s “the magistrate.” “Under the same procedure” mitigates the reading but does not make this a RECORD-only sentence. This is evidence of ambiguous instructional wording, not proof that a valid rule amendment occurred.

More concretely, the opening requires standing template text between nights, while the retained sections describe the completed night and deleted root. The reconciliation makes the historical facts understandable but does not satisfy that stated template invariant.

A RECORD-only replacement for `:86–87`:

> RECORD: Harvest, uninstall, and removal for this night are complete; no next plan is armed. The three retained night sections describe the completed night.

This changes no actor or procedure. It also does **not** resolve the retained-template issue: the lead should apply the existing template requirement or refer its applicability to the cold gate/Ed.

**F3 — nit; Opus count concern confirmed, not a failed custody check.** There are 14 copied `night/` records, plus `night.log`, plus `night_plan.json`: **16 custody files**. The 17th manifest entry is `pre-uninstall-observations.txt`. The uninstall transcript separately prints `17`, without the counting command. That number cannot mechanically be equated to the manifest count or a count of regular custody files.

Suggested wording:

> custody-root count output was 17, with the counting command not captured; the harvest includes 14 `night/` records plus `night.log` and `night_plan.json`.

**F4 — nit; Opus cure-field concern confirmed.** At `5db38b58`, C5 records `chain_sha256: null` and **`chain_stub: built_in_stub_by_design`**. It does not record a C5 basis named `stub_by_design`. Replace that clause in `21i:78` with the actual field/value. “Landed” here means committed on the cure branch; this review does not establish a merge into main.

### Exhaustive repeated-fact comparison

Abbreviations:

- **H** — `docs/process/NIGHT_HANDBACK.md`
- **A** — `docs/process_traces/2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md`
- **I** — same directory, `21i-rehearsal-20260909-harvest-record.md`
- **D** — same directory, `00-DURABLE-STATE.md`; September 9 arm/relaunch/harvest sections
- **R** — `RUN_STATE.md`, header `:13` and T38d paragraph `:19`
- **K** — `docs/process/state_kernel.json`
- **Q** — `TASK_QUEUE.md`. Rehearsal rows **722/882**, cure rows **782/942**, clone rows **653/803**. Both generated views were checked.
- **B** — `docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/`
- **BH** — `B/night-harvest/`

“Consistent” compares the **same event and role**, not every hexadecimal string indiscriminately. Activation IDs are not commit SHAs; planned, executed, and later acceptance states are distinguished.

| Fact | doc:line | Value | Consistent? |
|---|---|---|---|
| Night identity/date | H:51,78–82; A:1,14; I:1,9; D:608,621,640,660; R:19; K:3463; Q:722/882 | `rehearsal-20260909`, September 9 | Yes |
| Receipt class | H:51; I:9,19; D:621; K:3355–3360,3463; Q:722/882 | `REHEARSAL_STUB` | Yes |
| Plan version | H:58; I:9; D:621,640 | v2 | Yes; both plan copies byte-identical |
| Actual arming activation | H:78; A:1; D:608; R:19; K:3463; Q:722/882 | `784a764e` | Yes |
| Earlier preparation versus arm attribution | H:52,78; A:1; D:608 | H’s original text says `1ef89702`; reconciliation identifies it as preparer and `784a764e` as actual armer | Explicitly reconciled history; template issue is F2 |
| Harvest activation | H:76; A:30; I:1,3; D:654; R:13,19 | `628c2eed`; I gives full UUID | Yes; BH pre-uninstall state and events excerpt agree |
| Armed measurement/driver/repository head | H:79; A:14; I:10,36,55; D:611,622,641 | `ae8f074f` | Yes; plan full SHA `ae8f074ffa554707a9eac95995ab8ec03235d118` |
| Actual frozen checkout | H:79; A:14; I:10; D:610–611,622,641 | `/private/tmp/joulewise-rehearsal-20260909-checkout` | Yes |
| Example versus actual checkout name | H:61,79–80,105; A:14; I:10 | `JouleWise-rehearsal-20260909-<sha>` example versus actual lowercase path above | Explicitly reconciled; not the same literal path |
| Future rehearsal clone naming/isolation | H:44–49; K:1089; Q:653/803 | `JouleWise-rehearsal-<date>-<sha>`, inventory-bearing head, rehearsal not inventoried/disjoint | Yes; future clone requirement, not a claim about the completed temporary checkout |
| Main/base snapshot | I:23,36,87; D:643 | `83ab38ed` | Yes; Git results ancestry supports it |
| Initial cure commit | R:19; K:3263; Q:782/942 | `bb7090e2` | Yes **as initial cure**, not latest fix head |
| Cure under review / fix head | H:83 versus I:84; R:19; K:3263; Q:782/942 | H `bb7090e2`; others identify fix `5db38b58` | **No — F1; Git supports `5db38b58`** |
| Cure branch | H:83; I:84; R:19; K:3263; Q:782/942 | `fix/2026-09-09-night-gate-stub-chain` | Yes |
| Cure PR | I:84; R:19; K:3263; Q:782/942 | **#309** | Yes; H omits it |
| Bookkeeping/arm-record PR | I:80; D:623,630,651,667; R:19 | **#308** | Yes |
| Arm-record branch | A:27; D:614 | `bookkeeping/2026-09-09-rehearsal-arm-record` | Yes as recorded branch; review checkout itself is detached |
| Results branch | H:82,99; A:18; I:12,22; D:629,650,661; R:19; K:3463; Q:722/882 | `night-results/20260909` | Yes |
| Results head | H:82; I:22,60,66; D:662; R:19; K:3463; Q:722/882 | `a84e0f7f` | Yes; BH removal:6–7 has full SHA |
| Courier result message ID | H:82; I:25,67; D:662; R:19; K:3463; Q:722/882 | `1a08599a4ff4d005` | Yes; BH courier.sent:1 |
| Arming email thread | H:65; A:10,28,31; I:30; D:619,638,659 | `1a0800cdb282c3f1` | Yes; B arm-blockB:2 |
| Harvest activation launch notice | I:30; D:659 | `1a085bc57dbfabbe` | Same value; not independently authenticated by a captured Gmail response |
| Harvest activation PID | I:3; D:658 | `82637` | Yes; BH pre-uninstall observations:48 |
| Courier marker PID | I:26; D:657 | `82210` | Yes; BH courier.heartbeat:1 and courier.sent:5 |
| Census courier PID versus marker PID | I:26,28–29; D:656–657 | Census `82106`; markers `82210` | Different artifact roles, now distinguished; BH events:19 supports `82106`. No shell/parent relationship established |
| Harvest watchdog attempt | I:3; D:654 | 5 | Yes; pre-uninstall state agrees |
| Harvest launch transitions/time | I:4; D:654 | seq **22–23**, **03:33:01 PDT**, D epoch `1788949981` | Yes at displayed precision; exact seq23 epoch `1788949981.162783` |
| Post-courier watchdog transitions | I:28–30; D:656–658 | `FENCED → HOLD_CENSUS → FENCED`, notice `transition-20-hold_census` | Yes; BH events:20,22 |
| Stand-down deadline | A:26; D:612,624,626,645 | `1788946260` = **02:31 PDT** | Yes |
| Night start/t0 | H:53,81; I:9; D:621,640; R:19; K:3463; Q:722/882 | `1788947760` = **02:56 PDT** | Yes; plan:14 |
| Window maximum | H:54,68; I:9; D:621,640 | **900 seconds** | Yes; plan:15 |
| Relaunch belt | H:54; D:624,646,656 | **02:45–03:30** | Yes |
| Installation timing | A:32–33; I:13,69–70; R:19; K:3463; Q:722/882 | Installed **01:57 on September 9**, not the previous morning | Yes; B arm-blockB:1,181–182 |
| Previous-morning dead-man observation | H:71–73; I:13,69–70; R:19; K:3463; Q:722/882 | **07:00** case not exercised by this night | Yes; log has no such line |
| T38d checkpoint/header | R:13,19 | **2026-09-09 ~04:20 PDT**, activation `628c2eed` | Yes; separate from I’s ~03:40 harvest-record timestamp |
| Result verdict | H:67,82,92; I:11,18,66; D:661; R:19; K:3463; Q:722/882 | `REHEARSAL_ONLY` | Yes; BH result:44 |
| Chain exit | H:67,82,92; I:18–20; D:661; R:19; K:3463; Q:722/882 | **0** | Yes; BH result:35 and chain.exited |
| Receipt verdict/reason | H:83; I:11,33; D:662; R:19; K:3463; Q:722/882 | `REFUSED`, `night_probe_error` | Yes; BH receipt:76,79 |
| Receipt defect cause | H:83; I:34–39; D:662–663; R:19; K:3463; Q:722/882 | Missing `chain.zsh`; gate attempts read for stub | Yes; BH receipt:62; main code corroborates |
| Acceptable stub refusal versus observed finding | H:69–70,113–114; A:22; I:41,72; D:625,631,646 | Only `night_refused_agent_present` accepted; observed `night_probe_error` is a finding | Yes |
| Stub chain behavior | H:57; I:38,85–86; K:3257; Q:782/942 | Built-in `sleep 2; echo REHEARSAL`; declared chain not executed | Yes |
| Cure C5 representation | I:78 versus K:3257; Q:782/942; cure code | I says basis `stub_by_design`; code says measured `chain_stub: built_in_stub_by_design`, `chain_sha256: null` | **No — F4; code at `5db38b58` supports latter** |
| Cure merge status | H:83; I:84–89; R:19; K:3262–3263; Q:782/942 | Under review/not merged; future behavior conditional on landing | Consistent record; no fresh remote merge-state claim |
| Historical arm state | A:1,11–14; D:608,621,640–642 | Armed/agents installed at those observations | Yes, historical |
| Completed execution/harvest | H:81–85; I:9–27; D:660; R:19; K:3375–3384,3463; Q:722/882 | Fired and harvested | Yes |
| Uninstall completion | H:84–85; I:54–59; D:664–665; R:19; K:3463; Q:722/882 | Night agents uninstalled, rc 0 | Yes; BH uninstall:2–6 |
| Checkout and plan-root removal | H:85; I:60–62; D:664; R:19; K:3463; Q:722/882 | Removed | Yes; BH removal:10–13 |
| Current armed/frozen state | H:85–86; I:62; D:665–666; R:19; K:3463; Q:722/882 | Nothing armed; frozen list canonical repo only where specified | Yes; captured state and cleanup evidence agree |
| Meaning of `DONE` | H:84–85 versus R:19; K:3462–3463; Q:722/882 | Harvest/uninstall/removal DONE; entire rehearsal acceptance BLOCKED/PARTIAL | **Consistent; different subjects. S-B closed** |
| Post-watchdog event | K:3375–3384; I:71–74; D:660; R:19; Q:722/882 | `POST-WATCHDOG-REHEARSAL-20260909` **satisfied**, evidence points to I | Yes; event occurrence does not close conditional acceptance |
| Rehearsal start dependency | K:3411–3417; R:19; Q:722/882 | **pending**, hard start dependency on `NIGHT-GATE-STUB-CHAIN-01` | Yes |
| Rehearsal lane/status | K:3459–3463; Q:722/882; R:19 | `agent`, rank 88, `blocked`; BLOCKED/PARTIAL | Yes |
| Cure lane/status | K:3259–3263; Q:782/942; R:19 | `agent`, rank 168, `active`/IN PROGRESS | Yes |
| Clone lane/status | K:1098–1102; Q:653/803 | `ed_external`, rank 166, `queued` rendered READY | Yes; note limits agent work to preparation |
| Clone-cut prerequisite | K:1102; Q:653/803; R:19; I:76–84; D:667–669 | Cure merge precedes rehearsal clone; cure → bookkeeping merge → clone/preparation → G2-a | Consistent; clone prerequisite is a status note, not a pending dependency object |
| Acceptance item 1 | I:65; R:19; K:3463; Q:722/882 | Not re-verified here/open | Yes; “open” does not assert missing historical cold-start evidence |
| Acceptance item 2 | I:66; R:19; K:3463; Q:722/882 | MET | Yes |
| Acceptance item 3 | I:67; R:19; K:3463; Q:722/882 | PARTIAL: send recorded, inbox receipt unverified | Yes |
| Acceptance item 4 | I:68; R:19; K:3463; Q:722/882 | Open/not yet; stage-1 email owed before diagnostic arm | Yes |
| Acceptance item 5 | I:69–70; R:19; K:3463; Q:722/882 | Open; cannot be met by this night | Yes |
| Acceptance item 6 | I:71–74; R:19; K:3463; Q:722/882 | MET conditional on cure landing | Yes |
| Second stub night | I:73–74; D:668–669; R:19; K:3463; Q:722/882 | **Unresolved / `needs_ruling`; cold gate or Ed** | Yes; no answer installed |
| Remote-control follow-up ordering | A:23; I:81; D:630–631,652,668 | Between windows, following harvest/preparation routing | Yes |

The following requested values appear in only one of the selected narrative documents, or need comparison with their primary artifact rather than another prose copy:

| Fact | doc:line | Value | Consistent? |
|---|---|---|---|
| Arm-record timestamp | A:3; B arm-launchctl-and-state:1 | `1788944302` = **01:58:22 PDT** | Exact match |
| Arm operation timestamp | A:32–33; B arm-blockB:1 | **01:57:32 PDT**, artifact epoch `1788944252` | Match; transcript labels block start, not a separately timestamped `os.replace` call |
| Plan authored epoch | D:621; B arm-night_plan:2 | `1788944188`; exact `1788944188.885739` = **01:56:28.885739** | Seconds abbreviated |
| Harvest-record timestamp | I:3 | `1788950400` = **~03:40 PDT** | Epoch/time agree; document timestamp, not captured copy-command time |
| Uninstall epoch | I:53; BH uninstall:1 | `1788950218` = **03:36:58 PDT** | Exact match |
| Removal epoch | I:51; BH removal:1 | `1788950258` = **03:37:38 PDT** | Exact match |
| Pre-uninstall watchdog clock | I:52–53; BH pre-uninstall observations:29 | `1788950204.064847`; delta **13.935153 s** | Matches to stated six-decimal precision |
| Courier send epoch | I:25; BH courier.sent:3 | `1788947852` = **02:57:32 PDT** | Exact match; log reports completed attempt at 02:57:33 |
| HOLD transition epoch | I:29; BH events:20 | Prose `1788947872`; artifact `1788947872.637474` | Truncated seconds, not exact equality |
| Return-to-FENCED epoch | I:29; BH events:22 | Prose `1788948174`; artifact `1788948173.967854` | Rounded seconds, not exact equality |
| First relaunch/exit | D:616,618,635; BH events | `8844a3d0`, spawn `1788944861`; prior exit `1788944349`; own exit `1788945287` | Artifact fractional epochs match displayed seconds |
| Second relaunch/exit | D:633,636; BH events:14,16 | `b1e2fd2f`, spawn `1788945764`, exit `1788945977` = **02:26:17**, attempt 4 | Epochs/activation match; attempt is not independently proven by the transition excerpt |
| Chain PID/PGID | I:19; BH chain.started:3–4 | `82053` / `82053` | Exact match |
| Arm census MCP pair | D:611; B arm-blockB:6–7 | `83123` / `83143` | Exact match |
| Leaked test PID | A:8; B pass3-pid58633-argv.txt | `58633` | Artifact names/records that PID |
| Other relaunch PID observations | D:619,638,643 | `81330`; `81638`; MCP pair `81651/81664` | Narrative-only in inspected custody; not independently authenticated here |
| Results parent | I:22; BH removal:4–7; Git ancestry | `d4d494ec` | Git confirms parent, then `83ab38ed` |
| Result versus harvested log digest | I:15–17; BH result:6 and SHA256SUMS:15 | `f894b3a4…` versus `28ee7ad6…` | Correct different byte scopes: first two lines versus all six |
| Four appended log timestamps | I:16–17; BH night.log:3–6 | `02:56:03.367167`, `02:56:10.980604`, `02:57:33.117809`, `02:57:35.070205`, PDT | Exact matches |
| Manifest/count arithmetic | I:50,56; BH SHA256SUMS:1–17; uninstall:7–8 | 17 manifest entries; 14 night records + log + plan + observation | **F3**, explanation incomplete; hashes pass |
| Receipt C1/C4, C2, C3 | I:34–35; BH receipt:9,14–18,27–30,37 | Not evaluated after refusal; `NOT_APPLICABLE/no_pack_by_design`; clean census but FAIL | Exact matches |
| Result census/abort fields | I:18–20; BH result:2,33–34 and censuses | Count 1, hits `[]`, abort null; pgrep rc 1/empty stdout | Exact matches |

### S-B and S-C exact disposition

**S-B: closed at this head.** The event has `state: "satisfied"` and a non-null harvest-record evidence pointer. The new cure dependency is `pending`, `hard`, `scope: "start"`. Rehearsal status remains `blocked`. Both generated queue views agree, and `gen_state.py --check` passes.

There is no contradiction between completed harvest/cleanup and incomplete NIGHT-REHEARSAL-01 acceptance.

Requested verbatim **H:1–10**:

```text
1  # Night handback
2
3  This file is what the night courier reads first (`NIGHT_COURIER_PROMPT.md`).
4  The magistrate rewrites the three sections below before every armed night
5  (ruling R-9, `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`)
6  and commits the rewrite with the night's plan. Between nights the sections
7  hold the standing template text, so a courier that reads this file on a
8  night nobody armed reports exactly that.
9
10 The courier does not decide anything from this file. A **chain** is the child
```

Requested verbatim **H:80–90**:

```text
80 `JouleWise-rehearsal-20260909-<sha>` example above; the arm record is
81 `docs/process_traces/2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md`. It fired at 02:56 PDT on 2026-09-09:
82 result `REHEARSAL_ONLY`, chain exit 0, results branch `night-results/20260909` at `a84e0f7f`, courier email `1a08599a4ff4d005`.
83 The receipt refused `night_probe_error` (the gate read `chain.zsh`, which the stub arm never writes) — a finding; the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `bb7090e2` under review, not yet merged, as lane
84 NIGHT-GATE-STUB-CHAIN-01; the plan is not re-armed on that signature. The §Next lane harvest, `--uninstall` from the stub checkout,
85 and removal of the stub checkout and plan root are DONE (record 21i); nothing is armed and the frozen-checkout list is empty apart
86 from the canonical repo. The standing rules below are unchanged; the next plan's author rewrites §Purpose, §Where the results are and
87 §Next lane for that plan under the same procedure.
88
89 ## Where the results are
90
```

### Mechanical evidence and command tails

Read the requested Opus report at the supplied absolute path. No files changed; HEAD stayed exact and the worktree stayed clean/detached.

```sh
python3 -B scripts/gen_state.py --check
```

Observed: **exit 0, empty stdout/stderr**.

```sh
git rev-parse fix/2026-09-09-night-gate-stub-chain
git log -3 --format='%h %s' a84e0f7f
git show 5db38b58:joulewise/night_gate.py | rg -n -C 3 'chain_stub|stub_by_design|chain_sha256.*None'
```

Relevant tails:

```text
5db38b5816bce05b67cabfe3eb621bf2b22aa3e6

a84e0f7f record night 20260909
d4d494ec record night 20260909
83ab38ed Merge checkpoint T38c into main (bookkeeping for a fresh session; consult 99gn)

1045-            {
1046-                "chain_path": plan.chain_path,
1047-                "chain_sha256_path": plan.chain_sha256_path,
1048:                "chain_sha256": None,
1049:                "expected_chain_sha256": None,
1050:                "chain_stub": "built_in_stub_by_design",
1051-            }
1052-        )
1053-    else:
```

Hash/count/plan replay, read-only:

```sh
python3 -B -c 'from pathlib import Path; import hashlib,json; p=Path("docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest"); rows=[l.split(None,1) for l in (p/"SHA256SUMS").read_text().splitlines()]; assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for h,n in rows); names=[n for h,n in rows]; print("SHA256SUMS: %d/%d OK"%(len(rows),len(rows))); print("night-record copies:",sum(n.startswith("night-") for n in names)); print("custody files:",sum(n.startswith("night-") or n in ["night.log","night_plan.json"] for n in names)); print("directory files:",sum(x.is_file() for x in p.iterdir())); print("unhashed extras:",", ".join(sorted(x.name for x in p.iterdir() if x.name not in names))); r=json.loads((p/"night-result.json").read_text()); log=(p/"night.log").read_bytes(); assert hashlib.sha256(b"".join(log.splitlines(keepends=True)[:2])).hexdigest()==r["artifacts"][0]["sha256"]; print("night.log result digest: first 2 of 6 lines MATCH"); assert (p/"night_plan.json").read_bytes()==(p.parent/"arm-night_plan.json").read_bytes(); print("arm/harvest plan: BYTE-IDENTICAL")'
```

Observed exit 0:

```text
SHA256SUMS: 17/17 OK
night-record copies: 14
custody files: 16
directory files: 21
unhashed extras: SHA256SUMS, removal-output.txt, uninstall-output.txt, watchdog-events-excerpt.txt
night.log result digest: first 2 of 6 lines MATCH
arm/harvest plan: BYTE-IDENTICAL
```

### Root cause and this-PR guard

**The hand-copy hypothesis is supported by the commit history.** Round 2 (`1b56c9d2`) inserted `bb7090e2` in H. Round 4 (`191f4c43`) updated I to `5db38b58` without changing H. Round 3 (`70d71f77`) separately repaired the PID attribution across prose. T38d subsequently copied the cure history into the kernel and its projections.

The source artifacts exist. What was missing was a single comparison of all prose copies **by fact identity and event time**. The generator protects kernel/projection equality; its successful check does not check H/A/I/D against those projections.

The following is a **one-off final-head check for this PR**, not a proposed repository process rule. It pins the reviewed numeric/identity inventory at this exact head, with F1’s precise correction applied to the expected handback. It compares ordered tokens, so swapping existing PIDs is detected even if the overall set of numbers remains unchanged. It also checks both queue copies and the event/dependency states.

Run after committing the lead’s corrections. A deliberate change to any other numeric fact requires updating the expected inventory from evidence, not accepting the candidate as its own baseline. This command does not decide F2 or validate arbitrary prose semantics.

```sh
python3 -B -c '
import difflib,json,re,subprocess
BASE="2aae25f69a6be0b11465129e353d1a27eb63c4cb"
P="docs/process_traces/2026-09-02-hands-free-week/"
H="docs/process/NIGHT_HANDBACK.md"
K="docs/process/state_kernel.json"
IDS=("NIGHT-REHEARSAL-01","NIGHT-GATE-STUB-CHAIN-01","CLONE-READINESS-01")
def git(*args):
    return subprocess.check_output(["git",*args],text=True)
def read(ref,path):
    return git("show",ref+":"+path)
def scopes(ref):
    out={H:read(ref,H)}
    for name in ("21h-rehearsal-20260909-arm-record.md","21i-rehearsal-20260909-harvest-record.md"):
        out[name]=read(ref,P+name)
    durable=read(ref,P+"00-DURABLE-STATE.md")
    out["durable-09-09"]=durable[durable.index("## ARMED — rehearsal-20260909"):]
    run=read(ref,"RUN_STATE.md")
    out["T38d"]="\n".join(l for l in run.splitlines() if l.startswith(("**Current checkpoint: T38d","**T38d (")))
    assert len(out["T38d"].splitlines())==2
    kernel=json.loads(read(ref,K))
    queue=read(ref,"TASK_QUEUE.md")
    for task in IDS:
        out["kernel:"+task]=json.dumps(kernel["tasks"][task],sort_keys=True)
        rows=[l for l in queue.splitlines() if re.match(r"^\| [AE]\d+ \| "+task+r" \|",l)]
        assert len(rows)==2,(task,len(rows))
        out["queue:"+task]="\n".join(rows)
        assert all(kernel["tasks"][task]["status_note"] in l for l in rows)
    rehearsal=kernel["tasks"][IDS[0]]
    deps={d["target"]:d for d in rehearsal["dependencies"]}
    assert deps["POST-WATCHDOG-REHEARSAL-20260909"]["state"]=="satisfied"
    assert deps["POST-WATCHDOG-REHEARSAL-20260909"]["evidence"]
    assert deps[IDS[1]]["state"]=="pending" and rehearsal["status"]=="blocked"
    assert "needs_ruling" in rehearsal["status_note"]
    return out
def tokens(s):
    return [t for t in re.findall(r"[A-Za-z0-9]+(?:\.[0-9]+)?",s) if any(c.isdigit() for c in t)]
head=git("rev-parse","HEAD").strip()
assert subprocess.run(["git","merge-base","--is-ancestor",BASE,head]).returncode==0
assert git("status","--porcelain")==""
expected=scopes(BASE)
old="at `bb7090e2` under review"
new="at `5db38b58` (PR #309) under review"
assert expected[H].count(old)==1
expected[H]=expected[H].replace(old,new)
actual=scopes(head)
bad=[]
for name in expected:
    if tokens(expected[name])!=tokens(actual[name]):
        bad.append(name)
        print("FAIL numeric/identity drift:",name)
        for line in difflib.unified_diff(tokens(expected[name]),tokens(actual[name]),fromfile="reviewed expected",tofile="candidate",n=1,lineterm=""):
            print(line)
print("PR308_FACT_GUARD: "+("FAIL" if bad else "PASS")+"; scopes="+str(len(expected))+"; mismatches="+str(len(bad)))
raise SystemExit(bool(bad))
'
```

Executed on the current head, exit **1**:

```text
FAIL numeric/identity drift: docs/process/NIGHT_HANDBACK.md
--- reviewed expected
+++ candidate
@@ -77,4 +77,3 @@
 09
-5db38b58
-309
+bb7090e2
 01
PR308_FACT_GUARD: FAIL; scopes=11; mismatches=1
```

Executed additional checks entirely in memory:

```text
F1 correction applied in memory:
PR308_FACT_GUARD: PASS; scopes=11; mismatches=0
exit 0

Then mutate I courier pid 82210 → 82106:
PR308_FACT_GUARD: FAIL; scopes=11; mismatches=1
exit 1

Then mutate I uninstall epoch 1788950218 → 1788950219:
PR308_FACT_GUARD: FAIL; scopes=11; mismatches=1
exit 1
```

**Next exact step:** lead dispositions F1–F4, applies authorized corrections, runs the final-head command plus `gen_state.py --check`, and retains the cold-gate/Ed question about a second stub night as unresolved.

## Residual risk

- This establishes committed artifact consistency, not current machine state, inbox delivery, or current remote PR merge status.
- The captured copy-command transcript is absent; harvest-before-uninstall ordering remains inferred. The raw uninstall count’s command is also absent.
- Relauch PID observations and Gmail identifiers without corresponding captured responses remain narrative evidence, as marked in the table.
- The proposed guard protects the reviewed numeric/identity inventory; actor, state, and wording changes still need contextual review.
- No suite or hardware campaign was run: this was read-only document/artifact review. The read-only generated-state check passed.