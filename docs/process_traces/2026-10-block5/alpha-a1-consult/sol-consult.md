```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Recurring contention is established, but its responsibility for the exclusions is unproved; recommend one unchanged ALPHA retry.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-b5-consult-sol",
    "base_mode": "exact",
    "head_start": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "head_end": "7e6158d669cbb6fb35761aee18abf363f07c5d36",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "The exclusion predicates are confirmed, but contention is only a probable contributor and the specific causal chain remains unresolved under blinding.",
    "remediation": "Proposed remediation is one unchanged ALPHA attempt 2 after the magistrate adjudicates this consult, retaining the existing physical and number-integrity gates."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "7e6158d669cbb6fb35761aee18abf363f07c5d36"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7e6158d669cbb6fb35761aee18abf363f07c5d36$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,collections,pathlib; p=pathlib.Path(\"/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/hazards/monitor/contention.jsonl\"); r=[json.loads(s) for s in p.read_text().splitlines()]; v=[x[\"values\"] for x in r if x[\"kind\"]==\"interval\"]; n=sum(any(y[\"cpu_s_per_s\"]>0.05 for y in x[\"outside_over_limit\"]) for x in v); print(\"journal_lines\",len(r)); print(\"intervals\",len(v)); print(\"over_limit_intervals\",n); print(\"interval_errors\",sum(x.get(\"error\") is not None for x in r if x[\"kind\"]==\"interval\"))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "journal_lines 1978",
          "intervals 1975",
          "over_limit_intervals 183",
          "interval_errors 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "journal_lines 1978\\nintervals 1975\\nover_limit_intervals 183\\ninterval_errors 0$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Permitted evidence cannot join contention intervals to excluded target units or establish which NEG-8 emission path fired.",
      "needs": "Consider authorizing the aggregate counterfactual counts proposed in the body."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "An unchanged retry will probably encounter background contention again and may again be unusable.",
      "needs": "Magistrate adjudication of the retry recommendation."
    }
  ]
}
```

## Causal chain

### Cause

**Confirmed harvest predicates**

- **`cell.below_minimum`:** the harvest delegates to the catalog-backed exclusion function. Any excluded constituent removes its unit; any target cell with a required stratum below its minimum removes the window. Floor quantities require both repeat and quad strata. The loaded catalog minimum is **5**, despite stale registration prose saying 8. This is not evidence of an 8-versus-5 harvest defect. Sources: `joulewise/b5/harvest.py:3736–3741,3779–3786`; `joulewise/flags/exclusions.py:297–368`; `configs/campaigns/v5_claim_25g83/flag_catalog.json:255–260,1355–1356`.

- **`neg8.bound_not_derived`, initial path:** emitted when neither the registered-corpus artifact nor an authenticated collected-subset artifact qualifies as derived. The latter must contain at least 10 committed members in committed order, authenticate its manifest and permitted omissions, validate the bound, and pass the HAZARD bundle rederivation checks. Missing/unreadable artifacts, manifest/pin/identity failures, unauthorized omissions, arithmetic validation failures or failed bundle rederivation can produce this code without a harvest fault. Sources: `joulewise/b5/harvest.py:4507–4611,4639–4747,899–980`.

- **`neg8.bound_not_derived`, subsequent physics path:** after an initial bound validates, the harvest removes bound members bearing one of six registered physics codes, then rebuilds and validates the bound. It emits the same window code if fewer than 10 remain, manifest reconstruction fails, rebuilding raises or validation fails. Unknown physics alone does not remove a corpus member. Sources: `joulewise/b5/harvest.py:91–93,5339–5438`; `joulewise/whole_window.py:136`.

**What the counts establish**

The permitted harvest record confirms 119 present/raw-valid, 114 succeeded, no failed harvest collectors and exactly the two stated window reasons. The permitted driver record additionally reports a collected corpus of **10 kept from 12 listed**. Code identity reports no changed window input.

There are only three unsuccessful science members: one decode quad constituent, one prefill repeat and one prefill quad constituent. Those collection failures alone leave every science stratum at least 9/10. Thus, under the correct roster, `cell.below_minimum` requires additional harvest losses: at least five further units in an affected stratum. A quad fails when any constituent is excluded; aggregate collection success cannot establish quad retention. Sources: `joulewise/flags/exclusions.py:332–347`; `joulewise/b5/harvest.py:3736–3741`.

For the corpus, **10 collected is sufficient initially but leaves no further-loss margin**. One additional physics-excluded bound member would suffice to make it underivable. That is a possible chain, not a finding that it occurred.

**Upstream families compatible with these counts**

The catalog’s member-excluding families are:

| Family | Relevant possibilities |
|---|---|
| `MEMBER_VALIDITY` | Unsuccessful/admission-aborted members; strict validation, reduction, clock-anchor, token/precheck, idle/cooldown, quiet-state or capture-pair failures |
| `PHYSICS_IN_SPAN` | Contention overlap or missing contention coverage; battery conditions/coverage; thermal pressure; clock steps; cadence/sample or span failures |
| `MODEL_IDENTITY` | Underivable member identity |
| `INSTRUMENT` | Unsuperseded binary-identity uncertainty |
| `ROSTER` | Placement, attempt, creation or identity failures |
| `RECORDS` | Malformed pre-harvest records still capable of carrying a member exclusion |

Sources: `configs/campaigns/v5_claim_25g83/flag_catalog.json`, entries having `effect=EXCLUDE_MEMBER`; applicability and propagation: `joulewise/flags/exclusions.py:201–295`.

“Raw-valid” and “succeeded” do not rule these out. `strict_deferred=119` also does not demonstrate harvest strict-validation success.

Corpus mint omissions have a narrower validity set: unsuccessful status, noncurrent strict mint, custody-triangle disagreement, precheck ineligibility and reduction mismatch. Additional corpus physics losses are limited to **contention, battery, thermal and clock-step** codes. Other source/authentication failures can prevent derivation without being authorized member omissions. Sources: `joulewise/whole_window.py:4435–4445,4660–4671`; `joulewise/b5/harvest.py:846–856,91–93,5367–5438`.

Reference losses ordinarily affect the survivor drift screen, potentially `neg8.screen_failed`; they do not directly explain these two codes. Sources: `joulewise/b5/harvest.py:4842–4885`.

**Contention findings**

Journal: `/Users/edr/night-custody/v5-b5-alpha-a1-20261008T2201Z/hazards/monitor/contention.jsonl`.

- **1,978 lines:** 1,975 intervals and three lifecycle/snapshot lines.
- **183/1,975 intervals exceeded the limit: 9.27%.**
- Zero interval errors; zero disagreements between an over-limit list and `clean=false`.
- Two intervals included exited-process carryover. Such carryover is already included in `outside_over_limit`; it must not be counted twice. Sources: `joulewise/hazards/contention.py:347–349,377–385,415–421`.

Counts below are **intervals containing the named offender**, so overlaps make them nonadditive:

| Process | Intervals |
|---|---:|
| `mediaanalysisd` | 77 |
| `corespotlightd` | 51 |
| `fseventsd` | 14 |
| `PerfPowerService` | 13 |
| `runningboardd`, `mobileassetd` | 10 each |
| `deleted` | 9 |
| `mds` | 7 |
| `cloudd`, `passd` | 6 each |
| `duetexpertd`, `triald_system` | 5 each |
| `accountsd`, `triald` | 4 each |
| `XprotectService`, `tccd`, `spindump`, `mds_stores` | 3 each |
| `modelcatalogd`, `TGOnDeviceInfere`, `routined`, `launchd`, `frauddefensed`, `photoanalysisd`, `IMDPersistenceAg` | 2 each |
| `powerlogHelperd`, `com.apple.Safari`, `analyticsd`, `amsondevicestora`, `contactsd`, `trustd` | 1 each |

**Temporal structure:** sequential deciles contain respectively **28, 22, 5, 13, 11, 14, 31, 20, 22, 17** dirty intervals; their denominators alternate 197 and 198. There are **134 dirty runs**, including 107 singletons, 20 pairs, four triples, two runs of four and one run of sixteen. Excess is distributed throughout the window, with clusters, rather than one continuously dirty process.

`fseventsd` occurs only in journal lines **225–238**, fourteen consecutive intervals. Even removing every interval where it was the sole offender leaves **171 dirty intervals**. `mediaanalysisd` occurs from lines **58–1947**, `corespotlightd` from **9–1816**. Neither is a single startup burst.

These command labels predominantly identify Apple background services. There is **no over-limit command label identifying our test worker, stub, Claude or Codex** among the 31 labels. `com.apple.Safari` is the clearest application-associated offender, but accounts for one interval. The journal does not prove service ownership, restartability, whether work was triggered by our collection, or whether it would also occur on a wholly idle Mac. In particular, `PerfPowerService` could be collection-associated OS work.

The harvest excludes for an outside process above the threshold in an interval overlapping a request, with member-span fallback if the request span is unavailable. It does not judge total outside CPU or kernel activity as this contender predicate. Sources: `joulewise/b5/harvest.py:3188–3224,6378–6380`; `joulewise/hazards/monitor.py:589–597`. Journal tallies confirm zero aggregate-limit judgments and zero intervals including `kernel_task`.

**Conclusion:** contention is a credible contributor, but neither its share of dirty intervals nor the collection counts prove that it caused either window exclusion. They cannot distinguish contention from the other validity/physics families, or initial bound failure from subsequent corpus depletion.

### Recurrence

**Another unchanged window encountering over-limit contention: very likely; my judgment is above 90%, not a calibrated probability.** Excess occurs in every decile and involves repeatedly active background services, including 77 `mediaanalysisd` and 51 `corespotlightd` intervals.

**Another unusable window: material risk, presently unquantifiable.** Interval prevalence is not unit-loss probability: request overlap, clustering, quad amplification and the corpus’s remaining margin matter. I would not convert 9.27% into an independent member-failure rate or invent a numerical window-failure probability.

## Remediation

### Recommendation

**(a) Arm ALPHA attempt 2 unchanged, after magistrate adjudication.**

1. Retain ALPHA-1 as collected, claim-unusable evidence.
2. Complete the ordinary closure/pin/harvest prerequisites, then prepare ALPHA-2 through the sealed procedure.
3. Preserve window code, thresholds, catalog effects, corpus minimum and cell minimum.
4. After the clean-session transition, let the existing arm evaluate physical readiness; harvest the completed attempt normally.
5. If ALPHA-2 is unusable for a shared cause family, return to consult before a third spend. Registration `7.3`, lines **2835–2839**, expressly allows a consult to authorize an unchanged attempt.

This recommendation does **not** assume contention disappears. It accepts stochastic contamination while retaining the rules that exclude contaminated units. The first attempt establishes recurring exposure, but not a demonstrated deterministic failure or a specific effective cure.

## Disproved alternatives

- **Five collection failures alone:** insufficient to explain a target stratum below five; corpus collection alone also meets ten.
- **Restart `fseventsd` as the cure:** its fourteen-interval cluster is real, but 171 dirty intervals remain without its sole contributions. No evidence connects that cluster to both exclusions.
- **Harvest used the obsolete minimum eight:** the exclusion function loads the supplied catalog, whose rule is five. No defect supporting route (d) was found.
- **Raise the contention threshold:** the journal establishes CPU activity, not a safe effect on number integrity. It supplies no defensible replacement threshold. Changing the limit to retain more units would need additional physical evidence, not merely a better yield.
- **END STATE:** the supplied clock count, 1 nonbounded of 116 recorded, does not meet the majority test. Source: registration `7.4`, lines **2848–2855**.

## Residual risk

### Least sure

I am least sure that the dominant loss mechanism is stochastic contention rather than a recurring harvest validity predicate.

**The additional structural fact that would change my answer:** whether every target stratum and the corpus would meet their minima if only `contention.request_overlap` losses were restored. A joint recovery would strengthen a contention-specific intervention; failure to recover would redirect the investigation to the remaining families.

### Counts I would want

**Not executed.** This opens restricted derived files and requires the magistrate’s authorization decision. It prints code names and integers only. Counterfactual retention is diagnostic; it does not authorize retaining contaminated data.

```python
import json
from pathlib import Path

root = Path(
    "/Users/edr/night-archive/"
    "harvest-v5-b5-alpha-a1-20261008T2201Z/derived"
)
code = "contention.request_overlap"
ex = json.loads((root / "exclusions.json").read_text())

for ci, cell in enumerate(ex["cells"], 1):
    if not cell["target"]:
        continue
    for si, stratum in enumerate(sorted(cell["minimum"]), 1):
        kept = cell["n_kept"][stratum]
        restored = sum(
            d["stratum"] == stratum
            and set(d["codes"]) == {code}
            for d in cell["dropped_units"]
        )
        print(
            "cell.below_minimum", ci, si,
            kept, cell["minimum"][stratum], kept + restored
        )

for path in (root / "neg8-corpus-physics.json",):
    if path.exists():
        corpus = json.loads(path.read_text())
        restored = sum(
            set(d["reasons"]) == {code}
            for d in corpus["dropped"]
        )
        kept = corpus["members_kept"]
        print(
            "neg8.corpus_member_dropped",
            kept, corpus["minimum_n"], kept + restored
        )

with (root / "flags.jsonl").open() as stream:
    for line in stream:
        flag = json.loads(line)
        if flag["code"] == "neg8.bound_not_derived":
            observed = flag.get("observed", {})
            print(
                "neg8.bound_not_derived",
                int(observed.get("source") == "corpus_physics"),
                int("clean_members_below_minimum"
                    in observed.get("problems", []))
            )
```

The output shapes follow `joulewise/flags/exclusions.py:350–364,387–406` and `joulewise/b5/harvest.py:5375–5379,5405–5406,5435–5438`. No files changed, no tests or measurements ran, and no network access was used.