```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The five sampled fixture refusals are justified; the historical builder misses 50 explicitly cited complete-bundle digests; RPT001 admission preserves void-only output, but text 19's renderer safeguard is not implemented at head.",
  "workspace": {
    "base_requested": "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7",
    "base_mode": "exact",
    "head_start": "24b79db349706c9945ce42789b1be862a4400edc",
    "head_end": "24b79db349706c9945ce42789b1be862a4400edc",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "Q2 sampled fixtures",
        "action": "needs_ruling",
        "finding": "Authorize fixture repairs; none of the five sampled refusals demonstrates improper admission policy. The non-MOCK numeric-oracle fixture needs battery evidence, not merely a matching config hash."
      },
      {
        "row": "Q3 complete-digest enumeration",
        "action": "start_now",
        "finding": "Return the builder omission to S1: df-ph-decode-floor-mint1.json cites 50 complete-bundle digests, all omitted."
      },
      {
        "row": "Q3 RPT001",
        "action": "needs_ruling",
        "finding": "Recommend exact historical admission after tree-pin authentication, explicitly acknowledging that retained bundle bytes are external to Git."
      },
      {
        "row": "Q3 publication safety",
        "action": "wait_for",
        "finding": "Do not credit the historical-battery renderer safeguard until implemented and tested; admission is not evidence of float."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/bfgs-astra/trace_q2.py /tmp/bfgs-astra/head",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Q2 traced_tests=5 distinct_refusals=6"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Q2 traced_tests=5 distinct_refusals=6"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/probe_q3.py /tmp/bfgs-astra/base",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["RPT001 gate_inputs=PASS", "renderer_battery_state_mentions=0", "registry_battery_state_mentions=0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RPT001 gate_inputs=PASS"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/probe_q3.py /tmp/bfgs-astra/head",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["RPT001 gate_inputs=FAIL exit=1", "renderer_battery_state_mentions=0", "registry_battery_state_mentions=0"]
      },
      "expected": {"exit_code": 0, "tail_regex": "RPT001 gate_inputs=FAIL exit=1"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/bfgs-astra/inventory.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tracked_files=9993 text_files=9983 citation_artifacts=2183 concrete_run_id_vocabulary=1803",
          "committed_complete_bundles=13 historical=13",
          "indirect_manifest_pins=10",
          "inventory=artifact-inventory.json; artifact-inventory.tsv; committed-bundles.json"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "committed_complete_bundles=13 historical=13"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/resolve_floor.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "root_floor_cited_digests=50",
          "exact_external_digest_matches=50",
          "reader_results={\"BundleReadError: battery_float_evidence_missing: prospective bundle\": 50}",
          "unresolved=[]"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "exact_external_digest_matches=50"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/bfgs-astra/check_builder.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "builder_source_class=None",
          "root_floor_literal_bundle_digest_count=50",
          "builder_entries=13",
          "root_floor_digests_in_set=0"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "root_floor_digests_in_set=0"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/admit_rpt.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "make_figures: OK — authenticated inputs; emitted void placeholders and voided claim row",
          "counterfactual_main_exit=0",
          "claim_status=voided",
          "counterfactual_admission_changes_repository_files=False"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "claim_status=voided"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/bfgs-astra/check_safety.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "oracle_initial=BundleReadError: config.json digest does not match metadata.config_sha256",
          "oracle_matching_hash=BundleReadError: battery_float_evidence_missing: prospective bundle",
          "renderer_input_battery_state_mentions=0",
          "renderer_without_battery_state=rendered",
          "rendered_has_numeric_floor=True"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "renderer_without_battery_state=rendered"}
    },
    {
      "id": "V9",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/paper_anchor_correction_quantified.py --corpus-root /Users/edr/code/JouleWise --out /tmp/bfgs-astra/anchor-head.json",
      "cwd": "/tmp/bfgs-astra/head",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "population "}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The historical set omits 50 complete digests already cited by a committed detection-floor artifact. RPT001 additionally requires an explicit tree-to-complete identity admission.",
      "needs": "Return the complete-digest omission to S1 and rule the six RPT001 identities."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Text 19's battery_state renderer safeguard is absent at head; a numeric renderer fixture succeeds without the field.",
      "needs": "Implement and verify the historical-battery publication gate before relying on it."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full quantified-anchor replay was interrupted during raw-plist parsing. No completed runtime verdict is claimed for that route. The census is a concrete-reference candidate inventory, not an automatically adjudicated admission list.",
      "needs": "Finish the long anchor replay if a complete runtime route census is required."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Cold-read disclosure: supplied AGENTS instructions, state-file section headings and the bridge contract were read before the charge restriction. The whole-tree citation scan later processed state files mechanically. No other cold-seat answer was read and no coordination occurred.",
      "needs": ""
    },
    {
      "id": "F5",
      "kind": "scope_deviation",
      "level": "nonblocking",
      "text": "An initial builder.build inspection used its default TemporaryDirectory outside /tmp; those temporary archive extractions were automatically removed. The recorded replay uses TMPDIR=/tmp. No repository file was edited.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

**Q2 — five executed samples**

All five tests pass at base. At head they produce four test failures and one setup error. Full commands, hashes and exception stacks are retained in [the trace script](/tmp/bfgs-astra/trace_q2.py), [trace output](/tmp/bfgs-astra/q2-traces.log), [base log](/tmp/bfgs-astra/q2-base-tests.log) and [head log](/tmp/bfgs-astra/q2-head-tests.log).

The controlling [text 8](/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:115) says:

- The reader “admits exactly three states and raises `BundleReadError` otherwise.”
- MOCK applicability is “decided only from the `config.json` whose digest `metadata.config_sha256` binds.”
- Historical admission requires the complete-bundle digest in the pinned set.
- `FROZEN_LEGACY_BUNDLE_IDENTITIES` “play no part.”

[Amendments 24–25](/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-6bec2aa6/60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md:100) add the verdict’s bundle digest and controlled status factories. **Neither adds a general config-binding requirement to historical state (ii).** Execution confirms historical lookup precedes MOCK binding.

| Row / fixture | Executed bundle facts and exact raising path | Ruled behaviour or overreach | action / wait_for / collision surface |
|---|---|---|---|
| B1: `test_audit_amplification…test_allowlisted_legacy_identity_allows_missing_workload_provenance` | MOCK bundle retains `{pre:null, post:null, not_applicable:"mock"}`. Test substitutes legacy metadata hash `ee80585a…`; actual config hash is `ad9a84f4…`. `validate_bundle:411 → _strict_problems:492 → measured_window:695 → metadata:364 → _battery_verdict:409 → _digest_bound_mock_config:426`. | **Ruled refusal.** This bundle seeks state (iii), whose config binding the test breaks. Patching `_check_config_sha256` does not authenticate MOCK applicability. Legacy identity does not exempt it. | `needs_ruling` / fixture scope / `tests/test_audit_amplification.py` |
| B2: `test_cli_run…test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes` | Same MOCK record; substituted hash `ee80585a…`, actual `6dd2277c…`. Same reader path, ending at line 426. | **Ruled refusal.** State (iii) explicitly requires the binding. Its spoofed legacy identity is irrelevant under text 8. | `needs_ruling` / fixture scope / `tests/test_cli_run.py` |
| B3: `test_window_duration_margins…test_hand_computed_numeric_oracle` | Synthetic `powermetrics` config; metadata has neither `config_sha256` nor battery evidence; completed digest is outside the set. `setUp:474 → _make_bundle:579 → summed_curve:526 → metadata:364 → _battery_verdict:409 → _digest_bound_mock_config:426`. | **Ruled refusal, but the triage repair description is incomplete.** Text 8 supplies no admissible state. The mismatch message diagnoses the failed attempt to establish state (iii); it is not an independent rule binding every historical bundle. After adding the correct hash in scratch, this fixture still refuses as `prospective bundle`. It needs honest non-MOCK evidence, not just a hash repair. | `needs_ruling` / fixture scope / `tests/test_window_duration_margins.py` |
| A1: `test_cli…test_reduce_default_replays_recorded_060_and_051_versions`, `0.5.1` subcase | Copies `d078_r01`, then replaces its summary with the committed 0.5.1 golden. Resulting digest `bbff0914…` differs from admitted fixture digest `b1328247…`. Config binding matches; backend is `powermetrics`; battery key absent. `main:2369 → _cmd_reduce:1872 → reduce_bundle:2653 → metadata:364 → _battery_verdict:414`. | **Ruled refusal.** The hybrid bundle is not the tracked fixture’s complete identity and has no passing pair. Text 8’s state (ii) does not admit arbitrary recombinations of committed files. | `needs_ruling` / fixture scope / `tests/test_cli.py` |
| A2: `test_floor_extraction…test_bracket_max_exceeding_minted_member_bound_refuses` | Two synthetic `powermetrics` members, matching config hashes, absent battery keys, digests `d9b9012f…` and `7d8db818…`, neither historical. `_current_core_rederivation_reasons:4229 → measured_window:695 → metadata:364 → _battery_verdict:414`. | **Ruled refusal.** Neither state (i), (ii), nor (iii) applies. The earlier refusal prevents reaching the test’s intended bracket-bound assertion. | `needs_ruling` / fixture scope / `tests/test_floor_extraction.py` |

Exact test tails:

```text
Ran 5 tests in 0.410s

OK
```

```text
Ran 5 tests in 0.109s

FAILED (failures=4, errors=1)
```

The decisive constructor counterfactual, executed by `check_safety.py`, was:

```text
oracle_initial=BundleReadError: config.json digest does not match metadata.config_sha256
oracle_matching_hash=BundleReadError: battery_float_evidence_missing: prospective bundle
```

**Q3 — artifact census and production consequences**

The complete path-by-path enumeration is in [artifact-inventory.tsv](/tmp/bfgs-astra/artifact-inventory.tsv); [artifact-inventory.json](/tmp/bfgs-astra/artifact-inventory.json) records each concrete identity reference and committed-directory matches. [The scanner](/tmp/bfgs-astra/inventory.py) covers all 9,993 archived files, including decompressed logs and the tar fixture. The remaining ten binary files are fonts and PNGs.

Its **2,183 reference-bearing candidates include planned configs, synthetic identities and documentary repetitions**. They are not 2,183 measured bundles. A run-ID match is recorded separately from authenticated byte identity; notably, eight floor-run names also name committed fixture revisions with different complete digests.

| Artifact class / count | Committed bytes and historical-set membership | Executed production consequence | action / wait_for / collision surface |
|---|---|---|---|
| RPT001 analysis artifacts: **8 files**, including **4 input/artifact manifests**, referencing six retained bundles | **0/6 bundle payloads committed; 0/6 admitted.** All six external bundles match the committed v2 tree pins. Complete hashes are listed below. | `make_figures.gate_inputs` passes at base; fails at head. All six individually return the prospective-bundle refusal. Counterfactual admission produces only void placeholders. | `needs_ruling` / exact admission / builder, set and pin |
| Root/environment/top-level references: **8 files**; decisive source is `df-ph-decode-floor-mint1.json` | This detection-floor artifact explicitly cites **50 complete-bundle digests**. **0/50 exact payloads committed; 0/50 admitted.** All 50 were resolved to matching external bytes. Same-name fixture revisions do not satisfy these pins. | All 50 exact external identities now fail `BundleReader.metadata()` with `battery_float_evidence_missing: prospective bundle`. The builder classifies this source as `None`, silently missing its 50 citations. | `start_now` / S1 correction / enumeration logic |
| Configuration and manifest references: **1,570 files**, including **103 manifest-named paths** | Mostly planned run membership, config identities and manifest pins. They do not establish complete measured-bundle identity. Nine committed fixture names recur; identity must still be checked by bytes. | Planning references are not themselves runtime refusals. They cannot be converted wholesale into historical admissions. | `do_not_start` automatic admission / resolved measured identities / config and manifest readers |
| Fixture references: **68 files**, including **10 manifest-named paths**; **13 complete committed bundle directories** | **13/13 exact committed bundles admitted.** Every one executes as `unobserved_historical`. Compressed fixture archive contains no additional bundle `metadata.json`. | No historical-reader refusal for the 13 unchanged fixture identities. Q2 failures concern constructed or modified identities. | `start_now` preserve exact fixture membership / none / fixture constructors |
| Paper supply maps: **2 files**—current map and committed exhibit copy; **10 indirect manifest/inventory pins** | Current map has **5 `test_fixture_non_issuing` roles**, **2 pending roles**, and no directly pinned completed production bundle population. | Focused reported-energy test passes at base and fails at head with `stale supply-map receipt digest: reported_energy_parents`. This is source-receipt collateral, not proof of a missing historical-bundle admission. | `wait_for` source freeze / receipt refresh / supply-map custody |
| Statistics script: **1**, `issue_dg071_dg075_statistics.py` | `69451609…` hashes **one `power_trace.csv`**, not a complete bundle. Matching external file exists. Its enclosing complete digest is `c2851728…`, one of the omitted 50. | Script succeeds at head and emits the same pinned timing statistics. It reads the CSV directly. | `start_now` classify digest domain correctly / none / builder’s constant parser |
| Figure/paper scripts with literal identity references: **5** | RPT001’s six bundles and calibration captures are external. Calibration-capture identities must not be conflated with bundle-reader historical membership. | RPT001 refuses. Excursion JSON/SVG generation succeeds. Full quantified-anchor replay was interrupted; no completed runtime verdict is claimed. The three paper derivation scripts and relevant fiducial/parser files have no base→head diff. | `wait_for` unfinished anchor replay only / none otherwise / paper derivations |
| Paper documents and inputs: **16 files** | Includes statistics outputs, anchor/excursion records, and the prefill projection’s many run/file references. File pins and run names are not complete-bundle pins. | The dynamically scanning prefill producer also succeeds at head, writing a result with **1,127 bundle rows**. Historical publication routes therefore are not uniformly blocked by S1. | `needs_ruling` publication disposition / historical-battery lane / claim consumers |
| Other documentary artifacts: **435 files** | Logs, reports, receipts and copied citations. The census retains their references, including 27 literal complete-digest values; repetition does not create new identities. | No independent executable route per document. Resolve references to the owning route; do not admit prose aliases automatically. | `do_not_start` automatic admission / typed identity resolution / documentary sources |
| Test code/goldens: **64 files** | Includes synthetic IDs and a synthetic digest literal. Three committed fixture identities recur. Synthetic strings are not measured historical evidence. | Q2 provides the executed failure sample. | `needs_ruling` fixture scope / exact constructor repair / tests |
| Other scripts: **4**; production modules: **2** | Literal identities include fixtures and legacy-name tables; these do not establish a new historical exemption. | Text 8 explicitly excludes legacy-name identity as an admission mechanism. | `do_not_start` name-based admission / none / legacy dispatch |

**RPT001 identity result for each retained bundle**

None can be recomputed **from committed bundle bytes**, because those bytes are absent from the archive. Each can be recomputed from the retained external corpus, whose independently computed tree digest matches the committed manifest. A tree hash is not mathematically convertible into the complete-bundle hash.

The following complete hashes were computed; all six have `tree_matches=true`, `committed_bytes=false`, and `historical=false`:

```text
example-mac-mlx-local__r1
9fa8c3f02e419d36ceb6fdb6c9ac4c9717c9b9ab1c7345f66a5b4acff988c3a6
example-mac-mlx-local__r2
c88b919ca1b9b9f48794b20b08a9fef44b6fc8f50a4c5524b4d07ce59ace1ecb
example-mac-mlx-local__r3
a16099609eb73ca5b29f6770e8b8b60f583c028b277f93737df7c7674c1a91fa
example-mac-mlx-qwen35-122b-512t__r1
598b6eef05af7483268ad1004e837596bd9a827f7a0010500a38aa3846fd7cb1
example-mac-mlx-qwen35-122b-512t__r2
120953cac8875aedccb7eac97250607fa36013f6874a12a4d2234b2245c3fa25
example-mac-mlx-qwen35-122b-512t__r3
a03e253f57091979181eaeab3b7ca86d27419e7534591928cae80bf298f98af5
```

Full tree hashes, complete hashes and individual strict-validation results: [base evidence](/tmp/bfgs-astra/rpt-base.json), [head evidence](/tmp/bfgs-astra/rpt-head.json).

The unmodified validation-step commands were:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/probe_q3.py /tmp/bfgs-astra/base
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgs-astra/probe_q3.py /tmp/bfgs-astra/head
```

Their exact gate output:

```text
RPT001 gate_inputs=PASS
```

```text
make_figures: ERROR: strict validation failed for example-mac-mlx-local__r1: ['strict: battery_float_evidence_missing: prospective bundle']
RPT001 gate_inputs=FAIL exit=1
```

Other completed production commands, run from `/tmp/bfgs-astra/head`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/issue_dg071_dg075_statistics.py --repository-root /Users/edr/code/JouleWise-wt-s1cg-92472459 --out /tmp/bfgs-astra/dg-head.json
```

```text
wrote /tmp/bfgs-astra/dg-head.json
wrote /tmp/bfgs-astra/dg-head.md
DG-071 median_ms=120.9186 iqr_ms=5.9508
DG-075 median_ms=120.9224 iqr_ms=5.8949
```

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out /tmp/bfgs-astra/excursion-head.json --svg /tmp/bfgs-astra/excursion-head.svg
```

```text
ok   b_fiducial_s: draft=0.030067931757111657 derived=0.030067931757111657
ok   projection_evaluated_cell_count: draft=122859 derived=122859
wrote /tmp/bfgs-astra/excursion-head.json
wrote /tmp/bfgs-astra/excursion-head.svg
```

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/paper_prefill_resolvability_projection.py --corpus-root /Users/edr/code/JouleWise --repo-root /tmp/bfgs-astra/head --out /tmp/bfgs-astra/prefill-head.json
```

```text
wrote /tmp/bfgs-astra/prefill-head.json (2414337 bytes)
```

## Critical path

**Recommendation: admit the six RPT001 identities as `unobserved_historical`, through an explicit cold-gate amendment.** The justification is authenticated historical identity and preserved void-only publication behaviour—not a claim that battery state was acceptable.

The runtime-only admission experiment added exactly those six authenticated complete digests to the existing lookup, then ran `make_figures.main()` into `/tmp`. It changed no source or pin file. Its exact output included:

```text
make_figures: OK — authenticated inputs; emitted void placeholders and voided claim row
admitted_statuses=["unobserved_historical", "unobserved_historical", "unobserved_historical", "unobserved_historical", "unobserved_historical", "unobserved_historical"]
counterfactual_main_exit=0
claim_status=voided
```

**Science answer:** that admission cannot release an RPT001 energy number through the tested current route: the output contains no measurement and remains permanently voided. Broader historical admission can make numbers readable, however. It must not be equated with evidence of float.

Moreover, [text 19](/Users/edr/code/JouleWise-wt-bk-92472459/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:139) describes a deliverable that **does not exist at this head**. The renderer and registry contain zero `battery_state` occurrences. Executing the renderer with an existing numeric fixture lacking that field yielded:

```text
renderer_input_battery_state_mentions=0
renderer_without_battery_state=rendered
rendered_has_numeric_floor=True
```

Even once implemented, an empty-column gate prevents **unclassified** publication; a nonempty `unobserved (pre-directive)` value does not prove absence of battery confounding. Known charging evidence still requires withdrawal or remeasurement under text 19.

Proposed amendment text for the lead’s consideration:

**36 — Historical identity census.** Before finalizing S1’s historical-set pin, enumerate committed artifacts by content and identity domain, including root-level detection-floor artifacts, analysis/input/artifact manifests, paper supply references, script constants, fixture bundles and documentary citations. Distinguish complete-bundle, tree, manifest and individual-file digests. The 50 complete-bundle digests explicitly cited by `df-ph-decode-floor-mint1.json` belong to text 8’s existing enumeration; a filename filter must not exclude them. Run IDs alone and synthetic digest placeholders confer no admission.

**37 — RPT001 admission.** Admit exactly the six identities recorded above as `unobserved_historical`, after independently authenticating retained bytes against the committed `rpt001-v2` tree pins and computing their complete-bundle digests. Record the tree algorithm, source manifest and complete-digest mapping. State that payload bytes are external to Git; do not describe this as reconstruction from committed payload bytes. Preserve the route’s void-only outputs. Any builder/set/pin change requires the lead’s explicit amendment to the current keep-identical constraint.

**38 — Publication separation.** Historical admission grants readable historical custody, not battery clearance or claim eligibility. Keep RPT001 permanently voided. Implement and verify text 19’s renderer input and empty-state refusal before crediting that safeguard for other claim-bearing historical numbers.

The missing 50 complete-digest admissions are an S1 enumeration defect, independent of the six new tree-domain admissions. The unresolved `69451609…` should be reclassified as a resolved CSV-file pin, not inserted into a complete-bundle set.

The five sampled fixture failures enforce the battery admission rule; one needs more than a hash repair.  
The historical-list builder misses fifty bundles already identified by complete digests.  
The six retained report bundles are externally stored, match committed tree pins, and remain void-only when admitted.  
The planned battery-state publication check is absent from the current renderer.  
No repository file changed; the lead’s next step is to rule exact admissions and return the enumeration defect to S1.