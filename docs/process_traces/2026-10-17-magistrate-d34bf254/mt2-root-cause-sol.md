```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed: the cap skip is misclassified as structural and as a smoke stage failure; both successful members are falsely excluded by a validator that still enforces block 5's CPU busy-fraction rule.",
  "workspace": {
    "base_requested": "33816e4aa4c0b4150a35bebb0b1c46a49c56498c",
    "base_mode": "descendant",
    "head_start": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
    "head_end": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
    "upstream_end": "f3ef7804b85f3c2b3aae39363bf0c1b6f646ae6c",
    "branch": "lane/2026-10-16-b6-round2"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-rootcause/tmp/sol-rootcause PYTHONPATH=/Users/edr/night-custody/measurement/JouleWise-measurement-20261017T1619Z-b6 /opt/homebrew/bin/python3.13 -B - <<'PY'\nfrom pathlib import Path\nfrom dataclasses import replace\nimport json\nfrom joulewise.b6.acceptance import ACCEPTANCE,evidence_from_archive\nfrom joulewise.b6.archive import plan_tree,executed_porcelain\nfrom joulewise.b6.smoke import classify\np=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20261017T1619Z-b6')\ns=Path('/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z');a=s/'archive';pp=s/'custody/night_plan.json';plan=json.loads(pp.read_text());reg=s.parents[1]/'registration'\ne=evidence_from_archive(a,plan,reg);e=replace(e,runtime={**e.runtime,'_b6':{**e.runtime['_b6'],'smoke':True}})\nt,pr=plan_tree(a,plan,e.pack_id);code=json.loads((a/'derived/code-identity.json').read_text());code.update(repo_root=str(p),status_porcelain=executed_porcelain(a,plan,pp))\nf=ACCEPTANCE.prepare(ledger_path=s/'measurement/runs/calibration_observation_ledger.jsonl',plan_tree=t,registration_dir=reg,code_identity=code,pack_root=pr)\nr=ACCEPTANCE.evaluate(f,e)\nfor i,st in enumerate(e.stages):\n print('STAGE',st.stage_id,st.expected_count,[{'run_id':m.run_id,'status':m.status,'bundle_present':m.runtime.get('bundle_present'),'bytes_missing':'member.bytes_missing' in m.flags,'physical_flags':[x for x in m.flags if f.catalog.entry(x)['klass']=='PHYSICS']} for m in st.members])\nprint('ACCEPTANCE',json.dumps({'structural':r.structural,'reasons':r.reasons,'structural_failures':r.record.get('structural_failures'),'physics_stop':r.record.get('physics_stop'),'physical_stop_kind':r.record.get('physical_stop_kind')}))\nz=json.loads((s/'smoke-result.json').read_text());ok=all(st['rc'] in st['success_exit_codes'] for st in z['stages'])\nfor stages_ok in [ok,True]: print('CLASSIFY',stages_ok,classify(stages_ok=stages_ok,driver_exit=z['driver_exit'],harvest_exit=z['harvest_exit'],acceptance_result=r,flags=z['flags']))\nprint('V1_DONE')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CLASSIFY False fail",
          "CLASSIFY True physics",
          "V1_DONE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "V1_DONE"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-rootcause/tmp/sol-rootcause PYTHONPATH=/Users/edr/night-custody/measurement/JouleWise-measurement-20261017T1619Z-b6 /opt/homebrew/bin/python3.13 -B - <<'PY'\nfrom pathlib import Path\nimport copy,json\nfrom joulewise.environment_admission import environment_admission_refusals\nfrom joulewise.b6.idle_wait import busy_fraction_only\nfrom joulewise.b5.harvest import _Harvest,_precheck_structure,build_roster\ns=Path('/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z');a=s/'archive';r=build_roster(a/'sources/repo/configs/campaigns/d117_floor_qwen3-1p7b_v5',a/'sources/repo')\nclass Recorder:\n def __init__(self): self.roster=r\n def emit(self,code,**kw): print(code,kw.get('run_id'),kw.get('observed'))\nfor rid in ['d117fq31p7-df-ph-prefill-p2048-abs-r01','neg8-window-end-r1']:\n b=a/'sources/claim-runs'/rid;ad=json.loads((b/'metadata.json').read_text())['environment_admission'];final=ad['attempts'][-1];counterfactual=copy.deepcopy(ad);counterfactual['attempts'][-1]['cpu_admission']['admitted']=True\n print(rid,{'cpu_conditions':final['cpu_admission']['conditions'],'watts_p95':final['cpu_admission']['processor_combined_power_w_p95'],'busy_fraction_only':busy_fraction_only(final['cpu_admission']),'actual':environment_admission_refusals(ad),'only_cpu_admitted_changed_in_memory':environment_admission_refusals(counterfactual)})\n member=next(m for m in r['members'] if m['run_id']==rid);q=json.loads((b/'summary_metrics.json').read_text());_Harvest._precheck_flags(Recorder(),member,{'precheck':_precheck_structure(q)},{'run_id':rid})\nrow=json.loads((a/'sources/claim-runs/whole-window-verdict.json').read_text());print('PARSE',_Harvest.whole_window_member_failures(Recorder(),row));print('DECIDING_REPLAY_OK')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PARSE listed",
          "DECIDING_REPLAY_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DECIDING_REPLAY_OK"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=/Users/edr/night-archive/b6-mt2-rootcause/tmp/sol-rootcause PYTHONPATH=/Users/edr/night-custody/measurement/JouleWise-measurement-20261017T1619Z-b6 /opt/homebrew/bin/python3.13 -B - <<'PY'\nfrom pathlib import Path\nfrom dataclasses import asdict\nimport json\nfrom joulewise.whole_window import validate_whole_window_verdict_row\ns=Path('/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z');r=s/'archive/sources/claim-runs';raw=(r/'whole-window-verdict.json').read_bytes();row=json.loads(raw);lines=(r/'campaign_log.jsonl').read_bytes().splitlines(keepends=True);matches=[l for l in lines if b'\"idle_admission_whole_window_verdict\"' in l]\nprint('INPUT',{'bundle_ids':row['bundle_ids'],'status':row['status'],'conditions':row['idle_admission_core']['conditions'],'verdict_rows':len(matches),'log_bytes_equal':matches==[raw]},flush=True)\nprint('VALIDATOR',asdict(validate_whole_window_verdict_row(row,r,set(row['bundle_ids']))),flush=True)\nprint('SUPERVISION',json.loads((s/'archive/withheld/desk-verdict-run.json').read_text()));print('V3_DONE')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "V3_DONE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "V3_DONE"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Fixes and archive replay procedure are proposed, not implemented or validated. No repository or evidence file was edited; no collection or canonical suite was run.",
      "needs": "Lead implements the bounded fixes, runs focused tests and the canonical suite, then performs the isolated archive replay."
    }
  ]
}
```

## Causal chain

`P` is the measurement checkout at `33816e4aa`. All deciding-function replays imported its code using Python 3.13 with `-B`. The lane differs from P only in `tests/b6/test_replay.py`.

`S` below means [the archived smoke directory](/Users/edr/night-b6/machine-test/MT-20261017T1735Z/smoke/d117_floor_qwen3-1p7b_v5-20261017T1735Z), and `A` means `S/archive`. No block-5 claim-window energy file was opened.

### 1. Smoke desk: an intentional cap skip encounters two incorrect interpretations

The hypothesis is substantially correct, with two important corrections.

**The decode member did leave records.** Its bundle contains `metadata.json` and a failed `summary_metrics.json`. Harvest’s `member.bytes_missing` identifies precisely:

```json
{"files_missing": ["raw/powermetrics.plist"]}
```

It was skipped before the measured request, as intended. The recorded `idle.wait_cap_skip` has 18 attempts and effective cap 1,500 s; metadata records `skip_reason: wait_cap_reached`.

Acceptance nevertheless treats a bundle carrying *any* `member.bytes_missing` as absent. In [acceptance.py:179](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/b6/acceptance.py:179), the deciding inputs were:

| Input | Archived value |
|---|---|
| Stage | `alpha-science-absolute` |
| Expected members | 1 |
| Member status | `failed` |
| `bundle_present` | `true` |
| `member.bytes_missing` | present |
| Recorded physical reason | `idle.wait_cap_skip` |
| Later successful bundles | prefill and end reference |
| Reference-only stage | false |

Re-executing `ACCEPTANCE.evaluate` returned:

```text
structural = true
structural_failures = ["structure.missing_stage_bundles"]
reasons = ["structure.missing_stage_bundles"]
physics_stop = true
physical_stop_kind = null
```

**That structural flag is not the immediate branch producing smoke status `fail`.** The stage journal records:

```json
{"stage_id":"alpha-science-absolute","kind":"campaign_collection","rc":1}
```

Its accepted exit codes are `[0]`. Consequently `stages_ok=false`, and [smoke.classify:372](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/b6/smoke.py:372) returns `fail` before considering incidental physical exclusions. There was no physical *chain stop*: collection continued.

Two real-code replays establish the distinction:

```text
actual stages_ok=false                         -> fail
same input, structural flag cleared in memory -> fail
stages_ok=true, archived acceptance and flags  -> physics
```

**Both acceptance and smoke stage interpretation need fixing.** Removing only `structure.missing_stage_bundles` will leave this machine test failing.

### Decisions I made

A stage whose members were deliberately skipped for recorded physical reasons is a collection loss, not evidence that collection code failed structurally. This applies to smoke and real windows. It requires records that explain each missing measurement; an incidental PHYSICS flag does not excuse a crash or unrelated record loss.

The governing lane texts support that distinction:

- [Design §13.1](/Users/edr/code/JouleWise-wt-b6-round2/docs/design/block6_collection_draft.md:541) excludes “a session in which the **collection code failed structurally** (crash, a missing record class, a hand-over that did not happen).”
- [Threshold design §3.1](/Users/edr/code/JouleWise-wt-b6-round2/docs/design/next_block_threshold_proportion.md:195) says: “On the cap being reached the run is skipped and flagged, and the session continues.”
- [Machine-test acceptance](/Users/edr/code/JouleWise-wt-b6-round2/docs/process/block6_machine_test.md:145) explicitly expects the cap member’s failed summary and `wait_cap_reached`, and expects smoke status `physics`.

The registration draft is on the separate local branch `records/2026-10-14-b6-registration-draft`, at `c9fe8086c`; it is not a file installed at P. I inspected it with `git show`. Its `docs/registrations/block6_replication_DRAFT.md` §4 says:

> “a stage with planned runs left none of their records while later stages ran”

That example does not describe this member: its admission and failed-summary records exist. The implementation substitutes “one required file missing” for “none of their records.”

This decision does **not** waive the registered survivor minimum. A physically lost target stage can still make a real window non-counting through `cell.below_minimum`.

### 2. Successful prefill member: the reducer and verdict writer retain block 5’s environment veto

Both successful members exhibit the same mismatch:

| Input | Prefill member | End reference |
|---|---:|---:|
| Summary status | succeeded | succeeded |
| Admission decision | admitted | admitted |
| `claim_reason` | null | null |
| Critical environment passed | true | true |
| Reference provenance present | true | true |
| Environment evaluation eligible | true | true |
| Final attempt admitted | true | true |
| `busy_fraction_admitted` | true | true |
| Embedded CPU result admitted | false | false |
| CPU busy-fraction p95 | 0.87254 | 0.8717 |
| Processor power p95, W | 0.406085 | 0.417253 |
| Sample count | 576 | 576 |
| CPU conditions | `cpu_busy_ratio_p95_exceeded` only | same |

The embedded criteria retain the 0.5 busy-fraction threshold and 1.0 W power threshold. Recomputing `evaluate_cpu_idle_admission` from each archived `rich_telemetry_idle.jsonl` reproduced its stored CPU result exactly. `busy_fraction_only` returned `true` for both.

The controller deliberately preserves that raw CPU result while admitting the member under block 6’s policy: [controller.py:2114](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/controller.py:2114) sets the final attempt’s `admitted=true` and `busy_fraction_admitted=true`, then emits `idle.busy_fraction_exceeded`.

But [environment_admission_refusals:558](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/environment_admission.py:558) still does:

```python
if cpu.get("admitted") is not True or refused:
    reasons.add("environment_admission_failed")
```

It does not recognize the block-6 busy-only admission.

Real archived-input replays returned, for **both** members:

```text
environment_admission_refusals -> ("environment_admission_failed",)
current_environment_refusals   -> ("environment_admission_failed",)
recomputed snapshot refusals   -> ()
post-run environment refusals -> ()
```

As an isolation check, changing only the nested CPU `admitted` boolean in an **in-memory copy** made `environment_admission_refusals` return `()`. No evidence bytes were changed.

For the prefill member, that error reaches two paths:

1. **Target precheck.** [reduce.py:739](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/reduce.py:739) applies the environment barrier to phase prechecks. The stored summary contains:

   ```json
   {"phase":{"prefill":{"eligible":false,"reasons":["environment_admission_failed"]}}}
   ```

   The real roster’s target path is `["phase","prefill"]`. Replaying [_Harvest._precheck_flags](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/b5/harvest.py:3995) on that roster and summary emitted exactly:

   ```text
   member.target_phase_precheck_failed
   observed = {"target":"phase/prefill",
               "reasons":["environment_admission_failed"]}
   ```

2. **Whole-window member failure.** [run_campaign.py:7180](/Users/edr/code/JouleWise-wt-b6-round2/scripts/run_campaign.py:7180) calls the same current environment validator. The verdict records:

   ```json
   {
     "member_id":"d117fq31p7-df-ph-prefill-p2048-abs-r01",
     "reason_code":"environment_admission_failed",
     "detail":"{\"claim_reason\":null,\"decision\":\"admitted\",\"reason_code\":\"environment_admission_failed\",\"source\":\"whole_window_environment_validation\"}"
   }
   ```

   Replaying [_Harvest.whole_window_member_failures](/Users/edr/code/JouleWise-wt-b6-round2/joulewise/b5/harvest.py:4599) returned `listed` and emitted `member.whole_window_member_failure` with that reason.

This is a **desk defect**, shared with reduction at collection time. It is not caused by the smoke’s reduced member count.

The policy is already decided. [Threshold council Q3](/Users/edr/code/JouleWise-wt-b6-round2/docs/design/next_block_threshold_proportion.md:468) says:

> “Adopt as a flag. 13 of 53 quiet rehearsal baselines fail it while their power is 0.17 to 0.42 W against a 1.0 W limit.”

The registration draft §§1.2 and 8.4 likewise makes busy fraction flag-only. No new threshold or ruling is needed.

### 3. Successful end reference: the same environment defect

`neg8-window-end-r1` follows the same whole-window path and produces the same `environment_admission_failed` member-failure detail.

Replaying `whole_window_member_failures` emitted:

```text
member.whole_window_member_failure
run_id = neg8-window-end-r1
observed.reasons = ["environment_admission_failed"]
```

It gets no `member.target_phase_precheck_failed` because its roster entry has no science target-precheck cell. That difference explains the two members’ different exclusion lists.

### What the whole-window flags actually establish

The verdict producer **ran and finished**. `A/withheld/desk-verdict-run.json` records:

```text
bundles=4
elapsed_s=98.545
timeout_s=1800
returncode=1
timed_out=false
group_gone=true
error=null
```

“Whole-window verdict running, … of 1800 s” was a heartbeat describing its budget.

The stored verdict is `failed`, with conditions:

```text
environment_admission_failed
neg8_drift_bound_underived
neg8_idle_sub_drift_bound_underived
whole_window_bundle_invalid
```

The reduced smoke lacks the full reference corpus; the intentionally skipped decode member is also recorded invalid. Those facts explain why this smoke should not acquire a passing claim-window verdict. They do not justify failing the two successful members’ environment checks.

Replaying `validate_whole_window_verdict_row` on the archived row returned:

```text
authentic=false, admitted=false, status=failed
reasons:
  calibration_ledger_snapshot_required
  cpu_admission_core_failed
  environment_admission_failed
  whole_window_neg8_verdict_failed
  whole_window_verdict_conflict
  whole_window_verdict_provenance_invalid
```

There is exactly one verdict row in `campaign_log.jsonl`, byte-identical to `whole-window-verdict.json`. Authentication failure therefore does not establish that the producer failed to run or that the file and journal disagree.

Moreover, harvest explicitly reads member failures **regardless of verdict authenticity**. The offending member codes come from the named environment failures, not from `whole_window.verdict_unauthenticated` or a blanket propagation of `whole_window.not_passed`.

### Would round 1 be affected?

| Defect | Real-window exposure and cost |
|---|---|
| Physical stage loss called structural | Yes, when every member of a science stage meets the absence predicate and later stages run. Complete loss of a target stage already fails its minimum; this defect additionally creates a false structural failure and can hold the whole loop before subsequent packs. A chance cap skip during the preceding reduced smoke also encounters the separate stage-exit misclassification. |
| Prefill’s busy-only admission rejected | Yes, whenever a run passes power and environment checks but fails only busy fraction. Cost: a false lost run, or whole quad for a comparative unit. Enough losses lose a window; otherwise the retained science set differs from the registered set and can change the printed result. |
| End reference’s busy-only admission rejected | Yes. Cost: a false lost reference. Losing one of three may preserve the window but change the survivor-dependent drift bound and allowance; losing enough references makes the screen undefined and loses the window. |

There is no evidence here of incorrect energy integration. These are classification and selection errors.

## Remediation

### Physical stage loss and smoke classification

Smallest bounded changes:

- **`joulewise/b6/acceptance.py`:** distinguish a recorded pre-measurement physical skip from unexplained missing stage records. For this case, require the matching cap flag and admission `skip_reason`; do not treat generic `member.bytes_missing` as proof that no stage records exist.
- **`joulewise/b6/smoke.py`:** distinguish an explained cap-skip stage exit from a stage crash. Derive that explanation from the exact dispatched members and their records. Keep unexplained nonzero exits failing.
- **Tests:** `tests/b6/test_acceptance.py` and `tests/b6/test_smoke.py`.

The missing regression is a production-shaped reduced stage containing one cap-skipped member, with its failed summary, metadata, missing measured plist and later successful stages. It should yield a physical smoke outcome without S1. A companion case must remove the explanation or introduce an unrelated crash and remain structural/failing.

### Busy-fraction interpretation: one fix for failures 2 and 3

The minimum fix for these member exclusions is in **`joulewise/environment_admission.py`**: honor an explicit busy-only admission while retaining the raw CPU evaluator output.

Require the recorded final admission, `busy_fraction_admitted=true`, and CPU conditions demonstrating that busy fraction is the only disqualifying measured criterion. Preserve the existing power, GPU, environment and missing-evidence checks. Do not simply trust the marker or change the embedded CPU result to `admitted=true`.

Also align **`joulewise/whole_window.py`** with that interpretation: its final core-member check currently requires every raw CPU decision to equal `admitted`, despite the writer deliberately preserving the failed busy-only result. That produces the related spurious `cpu_admission_core_failed` authentication reason.

The writer already removes the busy-fraction condition for explicitly admitted members at [run_campaign.py:7235](/Users/edr/code/JouleWise-wt-b6-round2/scripts/run_campaign.py:7235). Its earlier environment-validation call is where these named failures enter.

Tests should cover:

- `tests/test_environment_admission.py`: busy-only admission accepted; power failure, missing evidence and absent marker retain their existing outcomes.
- `tests/test_hazard_whole_window_verdict.py` and `tests/test_whole_window.py`: writer and validator agree while preserving the raw CPU result.
- `tests/test_harvest_b5_p3harv.py`: the resulting prefill precheck and member-failure list produce neither false member code.
- A legacy/block-5-shaped control without the block-6 admission marker remains unchanged.

No threshold increase is proposed. The existing 1.0 W physical test remains; 0.5 remains a recorded busy-fraction finding.

### Replay over this smoke

**A new collection is unnecessary to test these desk fixes.** The successful members’ raw telemetry, event markers and admission evidence are present.

The replay must regenerate the entire affected dependency chain in a fresh output location:

1. Read the immutable archived sources and original registration.
2. Re-reduce successful bundles under the corrected environment interpretation, preserving original summaries separately.
3. Regenerate member assessments and the whole-window judgment from those results.
4. Rebuild flags and exclusions, then run acceptance and smoke classification.
5. Re-run the machine-test report against those fresh judgments.

Re-running acceptance alone is insufficient: the old environment failure is already embedded in `summary_metrics.json`, member assessments and `whole-window-verdict.json`.

The existing `b6_replay_acceptance.py` only replays acceptance; it does not refresh those upstream judgments. Likewise, `b6_machine_test.report` reuses an existing `smoke-result.json`. A replay entry point should therefore be added to the existing session/report tooling—**`scripts/harvest_b6_session.py` and `scripts/b6_machine_test.py`**, with coverage in **`tests/b6/test_session_wrapper.py` and `tests/b6/test_smoke.py`**—that explicitly consumes regenerated judgments and writes only to a fresh replay root. It must preserve original source identities and record the correction rather than presenting rewritten summaries as original evidence.

Expected replay result: only the intended agent-overlap and cap members remain excluded, no false S1, and smoke status `physics`. The incomplete smoke’s claim-window and reference-count diagnostics can remain recorded.

## Disproved alternatives

- **No successful collection occurred:** both later members have succeeded summaries, no missing required files, empty strict-validation problem lists and original re-reductions identical to their stored summaries.
- **Prefill was too short or otherwise failed its target phase check:** its target node’s sole reason is `environment_admission_failed`.
- **The verdict timed out:** it finished after 98.545 s, without timeout.
- **Unauthenticated verdict automatically excluded both members:** harvest emitted the codes from their explicit `member_failures` entries.
- **Reduced smoke alone explains their environment failures:** both contain a genuine block-6 admission shape rejected by a shared validator. Full windows use the same path.
- **Clearing S1 alone repairs smoke:** the real classifier still returns `fail` while `stages_ok=false`.

## Residual risk

The fixes are proposed only. Focused tests, the canonical suite and the complete isolated replay remain lead work. The archive replay verifies corrected desk behavior; it does not replace a later live gate at the new pin.

## SUMMARY

1. **Smoke desk:** cap skip has records but is treated as an absent stage; its expected stage exit also forces `fail` — **desk defects** — recognize recorded physical skips in acceptance and smoke stage classification.
2. **Prefill:** shared environment validator reinstates block 5’s busy-fraction veto, contaminating target precheck and whole-window member failures — **desk defect** — honor verified busy-only admission and regenerate judgments.
3. **End reference:** same obsolete environment veto creates a named whole-window member failure — **desk defect** — apply the same fix and replay the survivor screen.