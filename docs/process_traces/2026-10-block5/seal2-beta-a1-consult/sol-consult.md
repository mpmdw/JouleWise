```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend A provisionally; permitted evidence identifies the re-screen path but cannot identify its exact failure branch.",
  "workspace": {
    "base_requested": "224a264c5faaae90cdf56118df37e773a932700b",
    "base_mode": "exact",
    "head_start": "224a264c5faaae90cdf56118df37e773a932700b",
    "head_end": "224a264c5faaae90cdf56118df37e773a932700b",
    "upstream_end": "224a264c5faaae90cdf56118df37e773a932700b",
    "branch": "lane/2026-10-09-harvest-corpus-cap"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "The clean-bound re-screen was required, but the exact screen-failure branch remains unresolved.",
    "remediation": "Provisionally arm BETA unchanged at the next permitted t0, with the proposed structural inspection available to adjudicate that choice."
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
        "tail": [
          "## lane/2026-10-09-harvest-corpus-cap...origin/lane/2026-10-09-harvest-corpus-cap"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## lane/2026-10-09-harvest-corpus-cap\\.\\.\\.origin/lane/2026-10-09-harvest-corpus-cap$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "224a264c5faaae90cdf56118df37e773a932700b",
          "224a264c5faaae90cdf56118df37e773a932700b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^224a264c5faaae90cdf56118df37e773a932700b$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The evidence that distinguishes endpoint insufficiency, drift failure and replay failure is closed to this seat.",
      "needs": "Magistrate may authorize and run the proposed structural inspection."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The recurrence estimate is judgment under sparse, correlated evidence.",
      "needs": ""
    }
  ]
}
```

## Cause

**Exact physical cause unresolved. The normal deferred path necessarily calls the clean-bound re-screen; endpoint insufficiency is plausible, not established.**

The permitted BETA `harvest.json` confirms `COLLECTED`, false `claim_usable`, only `neg8.screen_failed`, and no collector faults. Its yield confirms the supplied stage counts. `derived/code-identity.json` records no changed window input. The permitted arm record says `GO`, with every hazard verdict `PASS`.

### Conditions, in code order

1. **Verdict absent:** `whole_window()` emits `whole_window.verdict_absent` and returns; this branch does **not** emit `neg8.screen_failed`. The reported verdict-file existence excludes it. **Malformed/non-object verdict:** it emits `whole_window.verdict_unauthenticated` and `neg8.screen_failed`, with `verdict_unreadable`, then returns. Bound validation elsewhere does not eliminate that possibility. [`joulewise/b5/harvest.py:4759–4778`]

2. For a readable object, `neg8_screen()` collects these reasons, in order:
   - `bracket_absent` if the core contains no bracket mapping;
   - otherwise `bracket_not_passed` if its decision differs from `passed`;
   - `neg8_conditions` if the core contains any string condition beginning `neg8_`, or the bracket contains any string condition.  
   The implementation accepts **all bracket string conditions**, not merely the registered subset. [`joulewise/b5/harvest.py:4892–4907`]

3. It determines newly lost references, clean-bound availability/requirement, and the collected-bound underived case. With no reasons and no survivor/clean-bound requirement, the stored screen stands. Otherwise, collected-bound or survivor cases call `_neg8_rescreen()`. [`joulewise/b5/harvest.py:4908–4938`]

4. `_neg8_rescreen()` cannot evaluate when, in order:
   - the bracket is absent;
   - conditions beyond the two underived codes exist **and** this is not a loss re-screen;
   - a required clean bound is unavailable, or no acceptable fallback bound exists;
   - neither recorded evaluation time parses;
   - source selection/authentication fails;
   - replay returns a problem or a non-mapping;
   - replay does not reproduce the stored bound-independent reference fields;
   - the subsequent exclusion replay fails or returns a non-mapping;
   - an exception occurs.  
   Source failures include unregistered policy, invalid evaluation basis, missing/invalid/unauthenticated source manifests, policy mismatch, invalid manifest members, failed basis projection, and `not_point_drift`. [`joulewise/b5/harvest.py:5242–5315`, `1104–1170`]

5. An evaluated re-screen clears the window failure **only** when its decision is `passed` and its conditions are empty. Otherwise, or when evaluation could not run, the harvest emits `neg8.screen_failed`. `references_insufficient` is attached when the selected structural bracket identifies that state. [`joulewise/b5/harvest.py:4945–4966`]

For a validated bound, the evaluator can still fail because freshness fails; references are missing, malformed or have incompatible counts; required reference summaries cannot be formed; or either claim family fails its endpoint drift comparison. Modern survivors require two or three references at each endpoint and zero or one midpoint, with matching family counts. More references than planned are invalid. [`joulewise/whole_window.py:2225–2293`, `2329–2340`, `2380–2440`]

The survivor bound adjusts for endpoint sample counts using the larger of the corpus envelope and prediction term. Losing a reference does not automatically fail a surviving `(3,1,2)` trajectory. [`joulewise/whole_window.py:1910–1958`, `1961–2024`]

### Which branches fit BETA

The magistrate’s supplied corpus count—one physics drop, a validated clean bound—sets the clean-bound requirement and the physics-loss re-screen flag. Thus, for a readable verdict, the harvest calls `_neg8_rescreen()` and permits it to reconsider stored conditions beyond underived. The “conditions beyond underived” guard cannot itself explain this window on that path. [`joulewise/b5/harvest.py:5385`, `5474–5477`, `4918–4938`, `5244–5245`]

All three substantive possibilities remain:

- **Insufficient survivors:** the original end endpoint already has only two succeeded references. One further harvest loss can leave fewer than two. A harvest loss at the start is also possible despite three runtime successes. Raw-valid means present bytes meeting the raw stream checks; it does not certify reference survival. [`joulewise/b5/harvest.py:7608–7627`, `91–127`; `joulewise/whole_window.py:2267–2293`]
- **Drift failure:** enough references survive, but either family fails the comparison against the clean, count-appropriate bound. A cleaned corpus can alter that bound. [`joulewise/whole_window.py:2083–2102`, `2146–2152`, `2329–2340`]
- **Replay/evidence failure:** the re-screen cannot run, or evaluates with non-drift evidence conditions. Collector `faults=[]` does not rule this out: these failures are recorded inside the screen result. [`joulewise/b5/harvest.py:5238–5245`, `5299–5352`]

A malformed verdict remains another possible early branch. I found no demonstrated harvest or verdict-writer defect.

The dropped **corpus** member is not evidence that an **end reference** was dropped. Those are separate populations.

### Spare and rc 1

A spare copies the stage’s first reference configuration, changing its identifier while preserving its role and sentinel position. It is therefore eligible to supply the same endpoint when it succeeds and survives validation. [`joulewise/b5/reference_spares.py:73–108`; `joulewise/whole_window.py:4968–5033`]

The chain computes `k = min(planned − succeeded, maximum_spares)` from summary statuses, then invokes that spare set once, after the normal settle and subject to the horizon. It uses the same runs root and `--max-failures k`; it does not retry a harvest-time contamination loss. [`joulewise/b5/chain.py:878–893`, `1245–1253`, `1256–1301`; `registration_block5.md:1151–1168`]

**Here the invoked spare supplied no additional harvested endpoint bundle.** The allowed yield has the original 125 planned/present bundles and no `.spares` roster stage. `yield_summary()` includes every spare found on disk, separately under its spare stage. Therefore a discovered spare bundle would have increased those counts. [`joulewise/b5/harvest.py:1851–1863`, `7680–7694`]

The invocation’s rc 1 is not a diagnosis of idle-admission failure. The runner returns 1 for member failures, blocked/invalid collection verdicts, claim-barrier conditions, or degraded stage verdicts. A failed invocation can leave no bundle. [`scripts/run_campaign.py:11494–11520`] The spare could have counted **by design**; the permitted harvest counts show it did not count **in this attempt**.

### Runtime losses and contention

My journal tally reproduces:

- BETA: **228/2,152** over-limit intervals; `XProtectRemediat` **77**, alone **61**; `mediaanalysisd` **76**, alone **72**; `syspolicyd` **8**, alone **6**.
- ALPHA: **165/2,081** over-limit intervals; no `XProtectRemediat`.
- BETA’s 77 `XProtectRemediat` records occur between journal lines **1795 and 1873**.

These tallies come from the permitted `hazards/monitor/contention.jsonl` files. The supplied stage tally places **114/379** over-limit intervals in the last science stage and **13/82** in the end stage, including **7** `syspolicyd` intervals.

That establishes substantial outside contention coincident with the losses. It does **not** establish the runtime condition of any failed member.

The controller aborts when its idle admission fails again after one retry. Admission tests CPU busy state, combined processor power and GPU idle state; in HAZARD mode evidence-only conditions are handled differently from measured threshold failures. [`joulewise/controller.py:1945–2002`, `2048–2097`, `2101–2112`; `joulewise/idle_admission.py:392–467`]

Separately, request-overlapping contention produces a harvest physics finding. That can remove a reference which succeeded at runtime. [`joulewise/hazards/contention.py:635–655`; `joulewise/b5/harvest.py:91–127`]

Thus the journal supports **contention as a plausible trigger for admission losses and later reference exclusions**. It cannot identify which admission criterion failed, distinguish admission abort from another terminal failure, or locate contention within an individual request. All bundles being present rules out the shared *pre-bundle* refusal explanation for the original members; it does not rule out admission aborts that left bundles.

## Recurrence

The local configuration supports recurring XProtect activity, **not a fixed 05:40 schedule**.

Under `/Library/Apple/System/Library/CoreServices/XProtect.app/Contents/Resources/`:

- `com.apple.XProtect.agent.scan.plist` and `com.apple.XProtect.daemon.scan.plist` register repeating `com.apple.xpc.activity` fast, ordinary and slow scans with `Interval` values **21600, 86400 and 604800** seconds.
- Their startup counterparts have `RunAtLoad=true`, with `LOGIN` or `START_UP` environment markers.
- The repeating entries are utility activities marked CPU/disk intensive and PowerNap eligible; battery eligibility differs by activity.

Those files launch `XProtect`; they do not identify the precise trigger for this window’s particular remediation subprocess. `/System/Library/LaunchDaemons/com.apple.security.xprotectd.plist` additionally configures a persistent, load-started service, without establishing the remediation scan’s wall-clock phase.

There is no `StartCalendarInterval` in the inspected scan plists. I cannot derive a guaranteed avoiding t0, even for the end references. A six-hour repeating fast activity also defeats treating an observed morning burst as the only possible burst. Scheduling away from this one occurrence is a heuristic, not a demonstrated cure.

**My judgment estimate for unchanged BETA attempt 2 being claim-usable is about 60%, with a broad plausible range of 30–85%.** This is not an estimated Bernoulli rate or confidence interval.

It rests on:

- a claim-usable unchanged ALPHA under the second seal;
- BETA retaining its corpus and cell minima despite runtime losses;
- only one screen loss among the four corpus-preserving chains stated in the brief;
- substantial recurrent background contention, and an end endpoint with little remaining redundancy.

The apparent three-of-four screen survival rate is encouraging but not transferable directly to BETA claim usability: different packs, machine states and correlated contention prevent that interpretation. A replay defect would make this estimate inappropriate; persistent drift could make it optimistic.

## Recommendation

**A — arm BETA attempt 2 unchanged, provisionally.**

1. The magistrate should consider running the structural projection below before final adjudication. I have not run it. This is a diagnostic opportunity, not a newly invented collection gate.
2. Unless it establishes a deterministic replay defect or another repeatable number-integrity failure, use the existing sealed clone and normal arming procedure at the next permitted t0. Preserve the existing midnight restriction and prescribed waits.
3. Change no threshold, endpoint minimum, reference roster or executed code on this evidence.
4. After the next harvest, classify its cause structurally. A second BETA loss in the same cause-key family goes through the registered anti-spiral consult route. [`registration_block5.md:4711–4723`]

No effective unattended daemon cure was demonstrated. Restarting an unrelated daemon, toggling Wi-Fi, or attempting further Apple-agent suppression would add disturbance without evidence that it removes this cause.

I do **not** recommend C now. If endpoint attrition proves recurrent, prospectively collecting additional independently scheduled endpoint references could be better science than weakening the minimum: it preserves replication while improving resistance to contamination. But one unresolved failure does not establish that redesign’s necessity, and a harvest-time replacement selected after seeing loss would need careful prospective rules. Current evidence also does not show the contention threshold is physically wrong.

I do **not** recommend D without a specific replay defect. A structural replay failure could change the recommendation to repair/re-harvest, but does not automatically prove the harvest wrongly removed the window.

I do **not** recommend E. The supplied **2 not-bounded of 477 recorded statuses** is far below the registered majority condition, and no cold-gate stop ruling was supplied. [`registration_block5.md:4748–4763`]

**GAMMA may not arm before BETA becomes claim-usable under the current registration.** The fixed ALPHA, BETA, GAMMA order is explicit in the registration, not merely the magistrate brief. [`registration_block5.md:4624–4629`] GAMMA now would not cure BETA’s unresolved cause and would introduce an unauthorized order change without a demonstrated physical advantage.

## Least sure

I am least sure whether the clean-bound re-screen **evaluated with insufficient end survivors**, **evaluated and failed drift**, or **could not evaluate**.

The one additional structural fact that would change my answer is that **branch classification**. In particular, an unevaluated result caused by deterministic source/replay disagreement would move my recommendation away from another unchanged collection and toward diagnosing the integrity failure first.

The runtime losses’ admission conditions are also unconfirmed. The process burst is strong temporal evidence, not proof of a particular failed predicate.

## Counts I would want

**Proposed only; not executed.** This program opens the closed screen artifact only if the magistrate authorizes it. It prints fixed labels, allowlisted status/code words and counts. It never prints identifiers, free-form problems, energies, bounds, ratios, durations or comparison operands.

```zsh
python3 -B - <<'PY'
import collections
import json
from pathlib import Path

archive = Path(
    "/Users/edr/night-archive/"
    "harvest-v5-b5-beta-a1-20261010T0742Z"
)
path = archive / "derived/neg8-screen.json"

def mapping(value):
    return value if isinstance(value, dict) else {}

def sequence(value):
    return value if isinstance(value, list) else []

def word(label, value, allowed):
    print(label, value if value in allowed else "unreadable")

conditions_allowed = {
    "neg8_drift_bound_underived",
    "neg8_idle_sub_drift_bound_underived",
    "neg8_drift_bound_stale",
    "neg8_bracket_abs_delta_exceeded",
    "neg8_bracket_idle_sub_abs_delta_exceeded",
    "neg8_bracket_missing",
    "neg8_bracket_reference_invalid",
}

problem_classes = {
    "bracket_absent",
    "conditions_beyond_bound_underived",
    "clean_bound_unavailable",
    "collected_bound_unavailable",
    "evaluation_time_unrecorded",
    "policy_unregistered",
    "evaluation_basis_invalid",
    "source_manifests_unrecorded",
    "source_manifest_path_invalid",
    "source_manifest_unauthenticated",
    "source_manifest_policy_differs",
    "source_manifest_members_invalid",
    "evaluation_basis_projection_failed",
    "not_point_drift",
    "rederivation_failed",
    "rederivation_invalid",
    "rederivation_differs_from_stored_bracket",
    "rederivation_raised",
}

print("screen_artifact_count", int(path.is_file()))
if not path.is_file():
    raise SystemExit(0)

data = mapping(json.loads(path.read_bytes()))
rescreen = mapping(data.get("rescreen"))
survivors = mapping(rescreen.get("survivors"))
stored = mapping(data.get("stored"))

print("evaluated_result_count",
      sum([rescreen.get("evaluated") is True]))
word("stored_decision", stored.get("decision"),
     {"passed", "failed", "flagged"})
word("rescreen_decision", rescreen.get("decision"),
     {"passed", "failed", "flagged"})
word("survivor_screen", survivors.get("survivor_screen"),
     {"references_insufficient", "more_references_than_planned",
      "invalid", "evaluated"})

counts = mapping(survivors.get("reference_counts"))
for position in ("start", "midpoint", "end"):
    value = counts.get(position)
    valid = type(value) is int and value >= 0
    print(position + "_count_record_count", int(valid))
    if valid:
        print(position + "_survivors", value)

conditions = sequence(rescreen.get("conditions"))
for code in sorted(conditions_allowed):
    count = sum(item == code for item in conditions)
    if count:
        print("rescreen_condition", code, count)
print("unclassified_condition_count",
      sum(not isinstance(item, str) or item not in conditions_allowed
          for item in conditions))

problems = sequence(rescreen.get("problems"))
classified = collections.Counter()
unknown = 0
for item in problems:
    prefix = item.partition(":")[0] if isinstance(item, str) else None
    if prefix in problem_classes:
        classified[prefix] += 1
    else:
        unknown += 1
for code, count in sorted(classified.items()):
    print("replay_problem", code, count)
print("unclassified_problem_count", unknown)
PY
```

Field justification:

- `screen_artifact_count` and `evaluated_result_count` count artifact/evaluation presence, not measured quantities.
- Decisions and `survivor_screen` disclose only closed categorical outcomes.
- Survivor fields count usable references at fixed positions; they contain no reference identity or measured magnitude.
- Condition counts disclose only registered categorical predicates, including drift pass/fail information expressly requested here; no operands or excess magnitude escape.
- Problem counts discard every suffix before printing and allowlist the category, preventing exception text or embedded values from escaping.
- Unclassified counts disclose only how many entries were suppressed.

The artifact’s fields are written at `joulewise/b5/harvest.py:5323–5352`; survivor counts and screen classifications originate at `joulewise/whole_window.py:2409–2444`.

No files changed. No tests, measurements, network requests, background tasks or additional agents started.