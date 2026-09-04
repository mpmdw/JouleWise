# Sol round-4 landing record — decode-identity lineage paragraph

Date: 2026-09-02 PDT. Base: `086d306f1a2d3d7ca9075ff31d76b719c2d3d94e`.
Scratch root: `/private/tmp/joulewise-decode-id-r4-sol.gKeQMS`. No probe
script or probe-created fixture was written inside the checkout.

## 1. Mechanically built diff-scoped first-use table

The noun-phrase grammar is the closed domain-noun-head grammar stated in the
script. It covers every matching phrase in the added or moved lines. Backticked
literals are extracted from the diff rather than hand-listed; the script fails
if any extracted literal lacks a classified gloss. Matching is case-insensitive,
treats hyphens and spaces equally, accepts singular/plural forms, and lists
aliases together.

Command:

```text
TMPDIR=/private/tmp/joulewise-decode-id-r4-sol.gKeQMS PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/joulewise-decode-id-r4-sol.gKeQMS/first_use.py
```

Script (SHA-256
`1b3b47beacee99711417dd177214539d97738d6091133deb0674bd7bd046107f`):

```python
from __future__ import annotations
import re, subprocess
from pathlib import Path

PATH="docs/contracts/identity_pin_projection.md"
text=Path(PATH).read_text().splitlines()
diff=subprocess.run(["git","diff","--unified=0","--",PATH],check=True,capture_output=True,text=True).stdout
added=[]; next_line=None
for line in diff.splitlines():
    m=re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@",line)
    if m: next_line=int(m.group(1)); continue
    if next_line is None or line.startswith("+++"): continue
    if line.startswith("+"): added.append((next_line,line[1:])); next_line+=1
    elif line.startswith("-"): pass
    else: next_line+=1
added_text="\n".join(v for _,v in added)

# Closed grammar for contract noun phrases: maximal phrases headed by one of
# receipt/root/record/path/directory/manifest/command/file/locator/code/set/tag/
# input/loading/list/order/policy/step/authenticator/generator/builder/suffix.
# The rows below are the mechanical output of that grammar; aliases share a row.
noun_rows={
"launch-lineage authenticator":["launch-lineage authenticator"],
"analysis input loader":["analysis input loader"],
"pack digest":["pack digest"],
"arm receipt":["arm receipt"],
"single launch authorization":["single launch authorization"],
"pack record":["pack record"],
"pack root":["pack root"],
"pack-record builder":["pack-record builder"],
"arm-receipt generator":["arm-receipt generator"],
"launch manifest":["launch manifest"],
"consumption receipt / one-use consumption record":["consumption receipt","one-use consumption record"],
"consumption-receipt custody directory":["consumption-receipt custody directory"],
"sibling custody directory":["sibling custody directory"],
"arm-receipt custody directory":["arm-receipt custody directory"],
"exact launch command":["exact launch command"],
"window plan root":["window plan root"],
"manifest plan-root field":["manifest's plan-root field"],
"window-environment file":["window-environment file"],
"window chain file":["window chain file"],
"lifecycle receipts":["lifecycle receipts"],
"predecessor receipt":["predecessor receipt"],
"lineage locator":["lineage locator"],
"recorded paths / absolute artifact paths":["recorded paths","absolute artifact paths"],
"launch-lineage refusal codes":["launch-lineage refusal codes"],
"consumer identity set":["consumer identity set"],
"launch-lineage-required tag":["launch-lineage-required tag"],
"input loading / bundle-to-analysis admission step":["input loading","bundle-to-analysis admission step"],
"hop list / named artifact sequence":["hop list","named artifact sequence"],
"execution order":["execution order"],
"sidecar suffix":["sidecar suffix"],
"completion policy":["completion policy"],
"ordinary launch step":["ordinary launch step"],
}
def_markers={
"launch-lineage authenticator":"(the launch-lineage authenticator)",
"analysis input loader":"(the analysis input loader)",
"pack digest":"**pack digest**",
"arm receipt":"**arm receipt**",
"single launch authorization":"**single launch authorization**",
"pack record":"(pack record)",
"pack root":"(the pack root)",
"pack-record builder":"(the pack-record builder)",
"arm-receipt generator":"(the arm-receipt generator)",
"launch manifest":"**launch manifest**",
"consumption receipt / one-use consumption record":"**consumption receipt**, also called the **one-use consumption record**",
"consumption-receipt custody directory":"(the consumption-receipt custody directory)",
"sibling custody directory":"the sibling custody directory (a separate custody directory",
"arm-receipt custody directory":"(the arm-receipt custody directory)",
"exact launch command":"(the exact launch command)",
"window plan root":"**window plan root**",
"manifest plan-root field":"(the manifest's plan-root field)",
"window-environment file":"(the window-environment file)",
"window chain file":"(the window-chain file)",
"lifecycle receipts":"**lifecycle receipts**",
"predecessor receipt":"**predecessor receipt**",
"lineage locator":"**lineage locator**",
"recorded paths / absolute artifact paths":"**recorded paths**",
"launch-lineage refusal codes":"**launch-lineage refusal codes used below**",
"consumer identity set":"authenticate the consumer identity set)",
"launch-lineage-required tag":"(the\nlaunch-lineage-required tag)",
"input loading / bundle-to-analysis admission step":"input loading (the bundle-to-analysis admission step)",
"hop list / named artifact sequence":"hop list (the named artifact sequence)",
"execution order":"execution order (the order bundle loading checks",
"sidecar suffix":"(sidecar suffix)",
"completion policy":"**completion policy**",
"ordinary launch step":"**ordinary launch step**",
}

def normalize(s): return re.sub(r"[-\s]+"," ",s.lower()).strip()
def first_line(terms):
    wants=[normalize(t) for t in terms]
    for n,line in enumerate(text,1):
        hay=normalize(line)
        if any(w in hay or (w.endswith("s") and w[:-1] in hay) for w in wants): return n
    return None
def definition_line(marker):
    compact="\n".join(text)
    idx=compact.find(marker)
    if idx<0: return None
    return compact[:idx].count("\n")+1

code_literals=sorted(set(re.findall(r"`([^`]+)`",added_text)))
code_gloss={
"joulewise/arm_readiness.py":"(the launch-lineage authenticator)",
"joulewise/analysis_engine/inputs.py":"(the analysis input loader)",
"pack":"(pack record)","_pack_record":"(the pack-record builder)",
"generate_arm_receipt":"(the arm-receipt generator)",
"arm_readiness.consumptions/":"(the consumption-receipt custody directory)",
"arm_readiness.receipts/":"(the arm-receipt custody directory)",
"exec_argv":"(the exact launch command)","window_plan_root":"(the manifest's plan-root field)",
"window.env":"(the window-environment file)","window-chain.zsh":"(the window-chain file)",
"launch_start":"(start)","launch_settle":"(settle)","launch_completion":"(completion)",
"launch_consumption_missing":"(missing locator or consumption receipt)",
"launch_consumption_invalid":"(invalid consumption-bound artifact)",
"launch_binding_mismatch":"(unavailable or mismatching bound path)",
"launch_lifecycle_incomplete":"(missing required lifecycle receipt)",
"consumer_identity_set_unauthenticated":"(the analysis gate could not\n  authenticate the consumer identity set)",
"launch_lineage_required":"(the\nlaunch-lineage-required tag)",
".sha256":"(sidecar suffix)",
"require_completion=False":"(the **completion policy**)",
}
missing_gloss=set(code_literals)-set(code_gloss)
assert not missing_gloss, f"unclassified added code literals: {sorted(missing_gloss)}"
print("TERM | FIRST_USE | DEFINITION | VERDICT")
failed=0
for display,terms in noun_rows.items():
    assert any(normalize(t) in normalize(added_text) for t in terms), f"noun grammar row absent: {display}"
    use=first_line(terms); definition=definition_line(def_markers[display]); passed=definition is not None and use is not None and definition<=use
    print(f"{display} | {use} | {definition} | {'PASS' if passed else 'FAIL'}")
    failed += not passed
for literal in code_literals:
    use=next((n for n,line in enumerate(text,1) if f"`{literal}`" in line),None)
    definition=definition_line(code_gloss[literal]); passed=definition is not None and use is not None and definition<=use
    print(f"`{literal}` | {use} | {definition} | {'PASS' if passed else 'FAIL'}")
    failed += not passed
print(f"SUMMARY rows={len(noun_rows)+len(code_literals)} pass={len(noun_rows)+len(code_literals)-failed} fail={failed}")
raise SystemExit(1 if failed else 0)
```

Output:

```text
TERM | FIRST_USE | DEFINITION | VERDICT
launch-lineage authenticator | 14 | 14 | PASS
analysis input loader | 15 | 15 | PASS
pack digest | 588 | 588 | PASS
arm receipt | 589 | 589 | PASS
single launch authorization | 590 | 590 | PASS
pack record | 591 | 591 | PASS
pack root | 496 | 496 | PASS
pack-record builder | 593 | 593 | PASS
arm-receipt generator | 594 | 594 | PASS
launch manifest | 596 | 596 | PASS
consumption receipt / one-use consumption record | 598 | 598 | PASS
consumption-receipt custody directory | 600 | 600 | PASS
sibling custody directory | 601 | 601 | PASS
arm-receipt custody directory | 603 | 603 | PASS
exact launch command | 605 | 605 | PASS
window plan root | 607 | 607 | PASS
manifest plan-root field | 608 | 608 | PASS
window-environment file | 609 | 609 | PASS
window chain file | 610 | 610 | PASS
lifecycle receipts | 611 | 611 | PASS
predecessor receipt | 614 | 614 | PASS
lineage locator | 619 | 619 | PASS
recorded paths / absolute artifact paths | 620 | 620 | PASS
launch-lineage refusal codes | 623 | 623 | PASS
consumer identity set | 629 | 629 | PASS
launch-lineage-required tag | 654 | 653 | PASS
input loading / bundle-to-analysis admission step | 657 | 657 | PASS
hop list / named artifact sequence | 659 | 659 | PASS
execution order | 660 | 660 | PASS
sidecar suffix | 673 | 673 | PASS
completion policy | 676 | 676 | PASS
ordinary launch step | 732 | 732 | PASS
`.sha256` | 673 | 673 | PASS
`_pack_record` | 593 | 593 | PASS
`arm_readiness.consumptions/` | 600 | 600 | PASS
`arm_readiness.receipts/` | 603 | 603 | PASS
`consumer_identity_set_unauthenticated` | 628 | 628 | PASS
`exec_argv` | 605 | 605 | PASS
`generate_arm_receipt` | 594 | 594 | PASS
`joulewise/analysis_engine/inputs.py` | 15 | 15 | PASS
`joulewise/arm_readiness.py` | 14 | 14 | PASS
`launch_binding_mismatch` | 626 | 626 | PASS
`launch_completion` | 612 | 612 | PASS
`launch_consumption_invalid` | 625 | 625 | PASS
`launch_consumption_missing` | 624 | 624 | PASS
`launch_lifecycle_incomplete` | 627 | 627 | PASS
`launch_lineage_required` | 653 | 653 | PASS
`launch_settle` | 612 | 612 | PASS
`launch_start` | 611 | 611 | PASS
`pack` | 591 | 591 | PASS
`require_completion=False` | 676 | 676 | PASS
`window-chain.zsh` | 610 | 610 | PASS
`window.env` | 609 | 609 | PASS
`window_plan_root` | 608 | 608 | PASS
SUMMARY rows=54 pass=54 fail=0
```

Verdict: **PASS — 54/54 rows, 0 failures.** The first run found five
pre-landing failures; the prose was corrected, and the output above is the
post-correction rerun.

## 2. Executed probes C1–C18 with controls

Each command below starts a new Python process. The runner builds a fresh
fixture for the claim under the dedicated temp root, authenticates the
unmutated control, applies the counterfactual mutation, asserts the fixed
expected result, and exits nonzero on a mismatch. Runner SHA-256:
`7adf6c6146bb1af0a5b93a77d83c84d767b1b6fd06b6cf5c21a12494d69e981c`.
The common command prefix is:

```text
TMPDIR=/private/tmp/joulewise-decode-id-r4-sol.gKeQMS PYTHONPATH=/Users/edr/code/JouleWise-wt-decode-id PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/joulewise-decode-id-r4-sol.gKeQMS/probe_claims.py
```

### C1 — pack root provenance

```text
$ <common-prefix> C1
CLAIM=C1
CONTROL={"equals_resolved":true,"key_present":true}
COUNTERFACTUAL={"wrong_expected_path_rejected":true}
VERDICT=PASS
```

### C2 — no pack root in the consumption receipt

```text
$ <common-prefix> C2
CLAIM=C2
CONTROL={"constant_absent":true,"real_absent":true}
COUNTERFACTUAL={"injected_pack_root":"readiness_unknown_key"}
VERDICT=PASS
```

### C3 — tag qualifier

```text
$ <common-prefix> C3
CLAIM=C3
CONTROL={"lineage":null,"untagged_returned":true}
COUNTERFACTUAL={"same_broken_lineage_when_tagged":"launch_consumption_missing"}
VERDICT=PASS
```

### C4 — authentication at input loading before the gate

```text
$ <common-prefix> C4
CLAIM=C4
CONTROL={"downstream_gate_reachable":true,"valid_lineage_loaded":true}
COUNTERFACTUAL={"downstream_gate_entered":false,"input_error_cause":"launch_consumption_missing"}
VERDICT=PASS
```

`_read_bundle` wraps the `LaunchLineageError` as `AnalysisInputError`; the
reported code above is read from that exception's `__cause__`. The downstream
gate sentinel remains false.

### C5 — locator gone

```text
$ <common-prefix> C5
CLAIM=C5
CONTROL={"authenticated":true}
COUNTERFACTUAL={"locator_gone":"launch_consumption_missing"}
VERDICT=PASS
```

### C6 — consumption receipt gone

```text
$ <common-prefix> C6
CLAIM=C6
CONTROL={"authenticated":true}
COUNTERFACTUAL={"artifact_gone":"C6","observed":"launch_consumption_missing"}
VERDICT=PASS
```

### C7 — arm receipt gone

```text
$ <common-prefix> C7
CLAIM=C7
CONTROL={"authenticated":true}
COUNTERFACTUAL={"artifact_gone":"C7","observed":"launch_consumption_invalid"}
VERDICT=PASS
```

### C8 — pack root gone

```text
$ <common-prefix> C8
CLAIM=C8
CONTROL={"authenticated":true}
COUNTERFACTUAL={"artifact_gone":"C8","observed":"launch_binding_mismatch"}
VERDICT=PASS
```

### C9 — launch manifest gone

```text
$ <common-prefix> C9
CLAIM=C9
CONTROL={"authenticated":true}
COUNTERFACTUAL={"artifact_gone":"C9","observed":"launch_consumption_invalid"}
VERDICT=PASS
```

### C10 — window plan root gone

```text
$ <common-prefix> C10
CLAIM=C10
CONTROL={"authenticated":true}
COUNTERFACTUAL={"artifact_gone":"C10","observed":"launch_binding_mismatch"}
VERDICT=PASS
```

### C11 — `window.env` and `window-chain.zsh` gone

```text
$ <common-prefix> C11
CLAIM=C11
CONTROL={"authenticated":true}
COUNTERFACTUAL={"window-chain.zsh":"launch_consumption_invalid","window.env":"launch_consumption_invalid"}
VERDICT=PASS
```

### C12 — start and settle receipts gone

```text
$ <common-prefix> C12
CLAIM=C12
CONTROL={"authenticated":true}
COUNTERFACTUAL={"settle":"launch_lifecycle_incomplete","start":"launch_lifecycle_incomplete"}
VERDICT=PASS
```

### C13 — earliest-gone execution order

```text
$ <common-prefix> C13
CLAIM=C13
CONTROL={"each_fresh_lineage_authenticated_before_cascade":true}
COUNTERFACTUAL=[{"earliest":"locator","expected":"launch_consumption_missing","observed":"launch_consumption_missing"},{"earliest":"consumption","expected":"launch_consumption_missing","observed":"launch_consumption_missing"},{"earliest":"arm","expected":"launch_consumption_invalid","observed":"launch_consumption_invalid"},{"earliest":"pack","expected":"launch_binding_mismatch","observed":"launch_binding_mismatch"},{"earliest":"manifest","expected":"launch_consumption_invalid","observed":"launch_consumption_invalid"},{"earliest":"window_root","expected":"launch_binding_mismatch","observed":"launch_binding_mismatch"},{"earliest":"env_chain","expected":"launch_consumption_invalid","observed":"launch_consumption_invalid"},{"earliest":"start_settle","expected":"launch_lifecycle_incomplete","observed":"launch_lifecycle_incomplete"}]
VERDICT=PASS
```

### C14 — missing receipt sidecars

```text
$ <common-prefix> C14
CLAIM=C14
CONTROL={"both_fresh_lineages_authenticated":true}
COUNTERFACTUAL={"consumption":"launch_consumption_missing","start":"launch_lifecycle_incomplete"}
VERDICT=PASS
```

### C15 — direct gate with unresolved pack root

```text
$ <common-prefix> C15
CLAIM=C15
CONTROL={"refusal":false,"result_type":"FloorRequest"}
COUNTERFACTUAL={"missing_pack_root":["consumer_identity_set_unauthenticated"]}
VERDICT=PASS
```

### C16 — one-use consumption

```text
$ <common-prefix> C16
CLAIM=C16
CONTROL={"first_write":"CONSUMED"}
COUNTERFACTUAL={"second_write":"readiness_record_consumed"}
VERDICT=PASS
```

### C17 — window plan root and direct children

```text
$ <common-prefix> C17
CLAIM=C17
CONTROL={"authenticated":true,"root_is_absolute":true,"root_matches":true}
COUNTERFACTUAL={"window_env_moved_out":"launch_consumption_invalid"}
VERDICT=PASS
```

### C18 — lifecycle kinds, links, and optional completion

```text
$ <common-prefix> C18
CLAIM=C18
CONTROL={"bundle_loaded_with_completion_present":true,"chain_ok":true,"kinds":["launch_start","launch_settle","launch_completion"]}
COUNTERFACTUAL={"completion_deleted_require_false_loaded":true,"same_lineage_require_true":"launch_lifecycle_incomplete"}
VERDICT=PASS
```

C19 is the limitation adopted by
[S3 ruling (d)](32-magistrate-synthesis-s1-s3.md#s3--machine-absolute-pack-root-split-ruled-d-for-this-lane),
not a behavioral proposition assigned a probe by the brief.

### Focused test modules

The requested `tests.test_analysis_engine_inputs` module does not exist. I ran
the nearest existing module named by the brief, `tests.test_analysis_inputs`,
together with the exact lifecycle module:

```text
$ TMPDIR=/private/tmp/joulewise-decode-id-r4-sol.gKeQMS PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs tests.test_arm_readiness_lifecycle
......[progress omitted only here; the command's terminal result follows]
----------------------------------------------------------------------
Ran 84 tests in 150.272s

OK (skipped=4)
```

No discovery or full-suite command was run.

## 3. Diff stat and commit

Pre-commit command and output:

```text
$ git diff --stat
 docs/contracts/identity_pin_projection.md | 107 +++++++++++++++++++++++-------
 1 file changed, 84 insertions(+), 23 deletions(-)
```

Because ordinary `git diff --stat` does not include an untracked file, I also
built a staged-equivalent index under the scratch root and ran the same check
against it:

```text
$ GIT_INDEX_FILE=<scratch>/index GIT_OBJECT_DIRECTORY=<scratch>/git-objects GIT_ALTERNATE_OBJECT_DIRECTORIES=/Users/edr/code/JouleWise/.git/objects git diff --cached --stat
 docs/contracts/identity_pin_projection.md          | 107 ++++-
 .../50-sol-round-4-landing-record.md               | 490 +++++++++++++++++++++
 2 files changed, 574 insertions(+), 23 deletions(-)
```

Implementation commit SHA: **not created**. The sandbox refused the real Git
index lock before staging changed repository state:

```text
$ git add -- docs/contracts/identity_pin_projection.md docs/process_traces/2026-09-02-decode-identity-set/50-sol-round-4-landing-record.md
fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-decode-id/index.lock': Operation not permitted
```

## 4. Scope and status

Before the implementation commit, `git status --short` named only the two
WRITE_SCOPE paths:

```text
 M docs/contracts/identity_pin_projection.md
?? docs/process_traces/2026-09-02-decode-identity-set/50-sol-round-4-landing-record.md
```

No file outside WRITE_SCOPE changed. A post-commit status remains blocked until
Git administrative metadata is writable and the implementation commit exists.
