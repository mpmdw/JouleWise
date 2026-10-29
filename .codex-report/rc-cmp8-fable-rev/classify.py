"""Classify sweep.out's exit-0 deletions: declared exemption / identity / text, versus a value or object the producer
writes unconditionally and the comparator compares when printed (the F1 class)."""
import re
import sys

EXEMPT = re.compile(
    r"(/(text|label|restricted)$)|schema_version|program_sha256|plan_id|attempt|harvest_pin|record_shape|_sha256|"
    r"family_instance_id|claim_verdicts_id|manifest_id|artifact_id|finalized_manifest|floor_artifact|"
    r"/reason_codes|/limitations|evidence_class|characterization|/equivalence|/mde$|metric/unit|ratio_estimand|"
    r"cell_a_id|cell_b_id|/planned|observed_complete_n|kept_n|removed_block_ids|kept_block_ids|bundle_blocks|"
    r"SE_repeat|SE_metrology|repeat_point_CI95|variance_contributions|excluded_stochastic_terms|exact_t|log_mean|log_sd|"
    r"randomization_check|sensitivity_status|without/status|floor/status|transport_verdict|arm_gates/\d/status|"
    r"resolutions/\d/status|transport_group_id|floor_row_ids|floor_source_cell_ids|/flag_count|stored_status|"
    r"family$|/code$|/blinding$|/count$|fixed_sentences|sensitivity_boundary|harvest_once|/windows(/|$)|"
    r"kept-units.*(/pack|roster|catalog|sensitivity_label|target|minimum|/n_r|/n_b|stratum|unit_id|positions|stage_ids|dropped|cell_id)|"
    r"mint.*(kind|extractable)|attained_by$|members/ALPHA/(corpus-r1|run-a/selected)|inputs/GAMMA|common_mode|"
    r"/direction$|assist_members_by_stratum|reported_cells/[^/]+/status|loo/rows$|estimator/raw_p|refused_cells|"
    r"projection-beta.json:cells$|/pack$|/cell_id$|/contrast_id$|/component$|floors/\d+$|cells/\d+$")
# A deletion that leaves a printed claim value absent: the fill's and the disclosure's numbers, objects and lines.
rows = [line.split("exit 0: ", 1)[1].strip() for line in open(sys.argv[1]) if "exit 0:" in line]
claim, exempt = [], []
for row in rows:
    (exempt if EXEMPT.search(row) else claim).append(row)
print(f"exit-0 deletions: {len(rows)}; declared exemption, identity or text: {len(exempt)}; "
      f"producer-unconditional claim value, object or line: {len(claim)}")
by_file = {}
for row in claim:
    by_file.setdefault(re.sub(r"[0-9a-f]{64}", "SHA", row.split(":", 2)[1] if row.startswith("l9") else "recompute"), []).append(row)
for name, items in by_file.items():
    print(f"\n{name}: {len(items)}")
    for row in items:
        print("  ", re.sub(r"[0-9a-f]{64}", "SHA", row.split(":", 2)[-1]))
