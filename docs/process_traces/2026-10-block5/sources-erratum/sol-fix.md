```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented authenticated catalog recovery; prospective cold erratum and rehearsal-copy verification remain required.",
  "workspace": {
    "base_requested": "224a264c5faaae90cdf56118df37e773a932700b",
    "base_mode": "exact",
    "head_start": "224a264c5faaae90cdf56118df37e773a932700b",
    "head_end": "224a264c5faaae90cdf56118df37e773a932700b",
    "upstream_end": null,
    "branch": "lane/2026-10-10-harvest-screen-sources"
  },
  "pathspec": [
    "joulewise/b5/harvest.py",
    "joulewise/whole_window.py",
    "tests/test_harvest_b5_sources.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Registration reading is option (b); authenticated catalog recovery changes the registered source and bracket-comparison rules.",
      "needs": "Prospective cold erratum and harvest-program pin before use."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox denied creation of the required scratch directory. Real rehearsal-copy reproduction and comparison were not run.",
      "needs": "Resume with the designated scratch directory writable and complete the rehearsal checks."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The supplied facts do not establish the spare manifest's execution field or its child's refusal cause.",
      "needs": "Magistrate may run the proposed structural count program."
    }
  ]
}
```

## Change

### Root cause

The source-loss mechanism is proved. Its attribution to the actual spare remains conditional on that manifest recording an absent member as `invoked`.

- Campaign authentication validates manifest shape and writer attestations. It does **not** require an invoked member’s bundle to exist. See [campaign_provenance.py:54](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/campaign_provenance.py:54) and [campaign_provenance.py:1040](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/campaign_provenance.py:1040).
- The writer groups policy-matching manifests for a HAZARD_PACK root and includes only `invoked` ordinary members in membership resolution. An absent bundle becomes `terminal_absent`. See [run_campaign.py:7750](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:7750), [run_campaign.py:7884](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:7884), and [run_campaign.py:7580](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:7580).
- In the ordinary block-5 consumption route, **any** terminal-absent occurrence rejects the entire candidate. The fallback selects directories with summaries, supplies no manifest roles, and returns `source_manifests=()`. See [run_campaign.py:8018](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:8018) and [run_campaign.py:8106](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:8106).
- Those fallback sources become evaluations with `declared_role=None`; the core therefore finds no NEG-8 references. The writer serializes empty source descriptors at both locations. See [run_campaign.py:7440](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:7440), [run_campaign.py:7171](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:7171), and [run_campaign.py:8590](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:8590).
- The pinned harvest then returns `source_manifests_unrecorded` before considering the catalog. See [harvest.py:1127](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:1127).

The hypothesis is too broad as written. A bundle-less spare recorded as `blocked_before_invoke` does **not** erase the sources: that member never enters ordinary membership resolution. Both cases are tested.

The spare generator preserves the reference role; the chain changes the config directory and failure budget while retaining the runs root. See [reference_spares.py:73](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/reference_spares.py:73) and [chain.py:1245](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/chain.py:1245).

For an invoked child that leaves no bundle, `missing_after_run` makes its status failed, increments failures, and records invoked provenance. The collection-only return site is [run_campaign.py:11404](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:11404); the relevant failure handling starts at [run_campaign.py:11220](/Users/edr/code/JouleWise-wt-harvest-sources/scripts/run_campaign.py:11220). This explains the runner’s nonzero result **if that path was taken**. The child’s actual refusal cause cannot be identified from the supplied facts.

Reproduction completed on authenticated **in-memory synthetic bytes**, using the unchanged writer:

1. Three manifests produce role-bearing sources.
2. Adding an authenticated manifest containing an invoked, absent spare empties the writer’s source list.
3. The writer’s core produces a failed missing bracket with no claim families.
4. The pinned harvest reports `source_manifests_unrecorded`.
5. The changed harvest evaluates the surviving `(2, 1, 2)` references.

The reproduction is [test_harvest_b5_sources.py:176](/Users/edr/code/JouleWise-wt-harvest-sources/tests/test_harvest_b5_sources.py:176), included in the test command below.

The requested scratch-copy reproduction was blocked:

```sh
mkdir -p /Users/edr/night-archive/b5-consults/beta-a1/fix/scratch
```

Exit 1:

```text
mkdir: /Users/edr/night-archive/b5-consults/beta-a1/fix/scratch: Operation not permitted
```

### Registration reading

**Option (b). The fix needs a prospective cold erratum.**

The survivor rule requires two references at each endpoint and permits runtime and harvest losses: [registration_block5.md:1178](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:1178). That does not independently authorize another source route.

The controlling passages say:

- Fallback campaign manifests are unauthenticated and used only to name references, never to supply an energy or passing screen. Their re-screen cannot run: [registration_block5.md:4053](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:4053).
- Re-screening uses the references named by the verdict and first must reproduce the stored endpoints and estimand: [registration_block5.md:2892](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:2892) and [registration_block5.md:2906](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:2906).
- Section 7.2’s “Harvest problems first” rule does not itself authorize rebuilding missing verdict sources: [registration_block5.md:4641](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:4641).
- Item 11.4 permits desk-side changes to these files and requires a program pin; it does not replace the source rule: [registration_block5.md:5519](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:5519).

The text contains no authenticated-catalog recovery instruction. This is therefore more than correcting the program to match an existing rule. Section 10 prohibits rule changes for armed or completed attempts and requires prospective cold errata: [registration_block5.md:5144](/Users/edr/code/JouleWise-wt-harvest-sources/configs/campaigns/v5_claim_25g83/registration_block5.md:5144). The current text does not authorize applying this recovery to the completed attempt.

### The fix

- **Harvest:** added `claim_neg8_sources`, using the existing all-or-nothing authenticated catalog reader, registered-policy check, manifest membership checks, safe paths, and duplicate checks. Recovery occurs only when the existing selector reports `source_manifests_unrecorded`. Invalid recorded descriptors or digests retain their existing failure behavior. See [harvest.py:1173](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:1173) and [harvest.py:5165](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:5165).
- **Harvest:** retains failed and absent invoked references outside the role-less evaluation basis. An absent invoked spare is `bundle_absent`. Recovery requires the clean bound and runs the existing exclusion pass directly; it cannot compare against the missing reference bracket. The derived re-screen records `reference_source=claim_campaign_manifests_authenticated`; failed screens also disclose the source through the existing observed field. See [harvest.py:5108](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:5108), [harvest.py:5318](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:5318), and [harvest.py:5383](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py:5383).
- **Whole-window:** added a recovery-only keyword to prevent the legacy single-reference endpoint protocol from passing a block-5 recovery. The default preserves existing callers. Too few survivors produce the existing invalid-reference condition and `references_insufficient`. See [whole_window.py:4881](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/whole_window.py:4881) and [whole_window.py:5206](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/whole_window.py:5206).
- **Tests:** added authenticated byte fixtures in memory, writer reproduction, recovery regression, negative controls, and comparison against the pinned harvest.
- **CLI script:** unchanged; its existing archive records carry the disclosure.

The recovery uses the same loss predicates, custody triangle, strict-validation callback, fresh reference evidence, freshness evaluation, and count-adjusted evaluator. It does not weaken the bound or endpoint requirement. Exceeded statistics, insufficient references, excess references, invalid authentication, policy differences, and missing clean bounds still fail. No exclusion code was added.

## Verification notes

### Tests

Final command:

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -c 'import tempfile, unittest; tempfile.tempdir="/Users/edr/night-archive/b5-consults/beta-a1/fix/scratch"; unittest.main(module=None, argv=["unittest", "tests.test_harvest_b5_sources", "tests.test_neg8_survivors.CountAdjustedBoundTests", "tests.test_neg8_survivors.SurvivorScreenEvaluatorTests"])'
```

Exit 0; 34 tests; result line:

```text
OK
```

The tests cover:

- Empty sources, an authenticated bundle-less spare, and survivor recovery.
- A valid role-less evaluation basis that omits failed and absent references.
- Insufficient endpoints, legacy-pair recovery, excess references, and bound exceedance.
- Bad attestations, policy differences, duplicate membership, invalid basis, and invalid recorded sources.
- Strict/custody losses and unreadable-energy losses before reduction.
- Byte-identical derived output and equal emitted flags against the pinned harvest for recorded sources.

Early fixture assertions failed and were corrected: existing guards can precede authentication diagnostics, and an overfull bracket need not contain a survivor diagnostic field. The final run passes.

`git diff --check` exited 0. The final scope check reported:

```text
WRITE_SCOPE_OK paths=3
```

The completed `corpus18-20261009T1949Z` rehearsal comparison was **not run**. The required scratch directory could not be created. The synthetic comparison against the pinned program is not a substitute for that check. Existing file-backed test classes also remain unrun under this scratch restriction.

All changes remain uncommitted. No claim-window files were inspected or processed; no measurement, network request, additional agent, or background task was started.

## Residual risk

The implementation is contingent on the erratum. It is not ready for acceptance under the sealed source-selection rule.

Real rehearsal-copy verification remains outstanding. The supplied facts also leave the actual spare’s execution kind and child refusal cause unconfirmed.

Next exact step: resume with the designated scratch directory writable, complete the requested rehearsal reproduction and before/after comparison, and obtain the prospective cold erratum and program pin before use.

## Counts I would want

To confirm whether the actual spare supplied an absent **invoked** reference, and whether its operational row survived, the magistrate could run this program. I did not run it. It emits fixed labels, closed-list words, and integer counts only.

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 - "$CLAIM_RUNS_ROOT" <<'PY'
import sys
from collections import Counter
from pathlib import Path
from joulewise import campaign_provenance as cp
from joulewise import whole_window as ww

try:
    root = Path(sys.argv[1])
    catalog = cp.load_authenticated_campaign_catalog(root)
    print("catalog", "authenticated" if catalog is not None else "failed",
          len(catalog or []))
    if catalog is None:
        raise SystemExit(0)

    counts = Counter()
    absent = set()
    for record in catalog:
        for member in record.value["members"]:
            slot = ww._neg8_position(member.get("role"),
                                     member.get("sentinel_position"))
            if slot not in ("start", "midpoint", "end"):
                continue
            execution = member.get("execution")
            if execution not in ("invoked", "existing", "blocked_before_invoke"):
                execution = "other"
            for bundle_id in member["bundle_ids"]:
                counts[(slot, execution)] += 1
                path = ww._safe_source_path(root, bundle_id)
                if execution == "invoked" and path is not None and not path.is_dir():
                    absent.add(bundle_id)

    for slot in ("start", "midpoint", "end"):
        for execution in ("invoked", "existing", "blocked_before_invoke", "other"):
            print("reference", slot, execution, counts[(slot, execution)])
    print("invoked_reference_absent", len(absent))

    rows = cp.load_campaign_log_rows(root / "campaign_log.jsonl")
    print("log", "readable" if rows is not None else "failed")
    exits = Counter()
    refusal_present = 0
    for row in rows or []:
        if row.get("run_id") not in absent or "exit_code" not in row:
            continue
        code = row.get("exit_code")
        bucket = "zero" if type(code) is int and code == 0 else \
                 "one" if type(code) is int and code == 1 else \
                 "two" if type(code) is int and code == 2 else "other"
        exits[bucket] += 1
        refusal_present += int(isinstance(row.get("child_refusal"), str)
                               and bool(row["child_refusal"]))
    for bucket in ("zero", "one", "two", "other"):
        print("absent_reference_log_exit", bucket, exits[bucket])
    print("absent_reference_child_refusal_recorded", refusal_present)
except Exception:
    print("scan", "failed")
    raise SystemExit(1)
PY
```