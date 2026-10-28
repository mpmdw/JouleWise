#!/usr/bin/env python3
"""Generate the R8.6 non-claim Mac session; never register it or edit loop.json."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.b5 import chain
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import load

KIT = Path("configs/campaigns/bytes_mac_check")
LONG = ("llama-70b", "qwen35-122b", "qwen3-next-80b")
# R8.6 specifies five structural runs per model and twelve additional soak
# runs for 70B/122B. Test 7: threshold note §4 row 7 specifies two large runs
# at each end; design §14 alternates them with two reference runs at each end.
CHECK_RUNS = 5
SOAK_RUNS = 12
TEST7_PAIRS = 2


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def build_files(root=ROOT):
    root = Path(root)
    # Use the actual block-6 composer for the calibrated reference/launch
    # scaffold. The kit is a fixed session, with no pack registration at all.
    reg = load(root / "configs/b6/packs/bytes-s1-p1/registration.json")
    seed = compose.layout(queue.Selection((reg.pack_id,), 1), {reg.pack_id: reg}, root)
    roster = json.loads((root / "configs/campaigns/bytes_v1/roster.json").read_bytes())["models"]
    source_science = next(s for s in seed.stages if s["stage_id"].endswith("-absolute"))
    reference = next(s for s in seed.stages if s["stage_id"].endswith("-reference-start"))["entries"][0]
    files, members = {}, []

    def collection(label, conditions):
        stage = deepcopy(source_science)
        stage.update(stage_id="bytes-mac-check-" + label, entries=[], expected_count=len(conditions))
        directory = KIT / "stages" / label
        rows = []
        for index, (source, model_id, purpose, end) in enumerate(conditions, 1):
            cfg = json.loads((root / source["config_path"]).read_bytes())
            run_id = f"bytes-mac-check-{label}-r{index:02}"
            cfg["run_id"] = run_id
            cfg["hardware_target"]["notes"] = "R8.6 non-claim structural session; never a registered pack."
            cfg["run_metadata"]["tags"] = ["bytes-mac-check", "non-claim", "launch_lineage_required",
                "bytes-model=" + model_id, "bytes-purpose=" + purpose, "bytes-end=" + end]
            raw = raw_json(cfg)
            filename = run_id + ".json"
            files[directory / filename] = raw
            entry = {"run_id": run_id, "config": filename, "config_path": (directory / filename).as_posix(),
                     "config_sha256": sha(raw), "index": index, "rep": index,
                     "role": "absolute_repeat", "block_id": None, "block_index": index,
                     "position": None, "position_in_block": 1, "arm": None,
                     "model_tag": model_id + "-mlx", "workload": cfg["workload_profile"]["name"],
                     "module_id": "bytes-mac-check-" + model_id, "pack_id": "bytes-mac-check"}
            rows.append(entry)
            members.append({"run_id": run_id, "model_id": model_id, "purpose": purpose, "end": end,
                            "stage_id": stage["stage_id"], "non_claim": True,
                            "config_path": entry["config_path"]})
        files[directory / "order_manifest.json"] = raw_json({
            "schema_version": "joulewise.order_manifest.v1", "manifest_id": stage["stage_id"],
            "planned_n_bundles": len(rows), "executed_order": rows})
        stage["entries"] = rows
        return stage

    sources = {}
    for model in roster:
        model_id = model["model_id"]
        directory = Path("configs/campaigns/bytes_v1") / model_id / "01_decode_absolute"
        entry = json.loads((root / directory / "order_manifest.json").read_bytes())["executed_order"][0]
        sources[model_id] = {**entry, "config_path": (directory / entry["config"]).as_posix()}

    def transfer(end):
        return [collection(f"test7-{model_id}-{end}", [
            (source, mid, "test7", end) for _ in range(TEST7_PAIRS)
            for source, mid in ((sources[model_id], model_id), (reference, "reference"))]) for model_id in LONG]

    checks = [collection("check-" + mid, [(sources[mid], mid, "check", "middle")] * CHECK_RUNS)
              for mid in sources]
    soaks = [collection("soak-" + mid, [(sources[mid], mid, "soak", "middle")] * SOAK_RUNS)
             for mid in LONG[:2]]
    fixed = [deepcopy(s) for s in seed.stages if not any(
        s["stage_id"].startswith(m["module_id"] + "-") for m in reg.modules)]
    # Corpus/start precede test 7, then all checks, shared midpoint and soaks,
    # test 7 at the end, end references and closing calibration.
    stages = fixed[:5] + transfer("start") + checks + [fixed[5]] + soaks + transfer("end") + fixed[6:]
    for stage in stages:
        stage["stage_id"] = stage["stage_id"].replace("bytes-s1-p1", "bytes-mac-check")
        stage.pop("spare_retry", None)
    layout = replace(seed, session_id="bytes-mac-check", packs=("bytes-mac-check",),
                     stages=tuple(stages), fixed_bytes=None, campaign_id="bytes_mac_check")
    tree, _ = compose.render(layout)
    # Use whole source manifests, with repository paths the fixed reader accepts.
    # Render's default manifests relocate config paths; these committed inputs
    # avoid '..' locators and keep each config digest independently checkable.
    for stage, source in zip(tree["stage_graph"], stages):
        entries = source["entries"]
        if entries:
            manifest = Path(entries[0]["config_path"]).parent / "order_manifest.json"
            raw = files[manifest] if manifest in files else (root / manifest).read_bytes()
            value = json.loads(raw)
            stage["input"] = {"kind": "manifest", "path": manifest.as_posix(),
                              "manifest_id": value["manifest_id"], "sha256": sha(raw)}
            stage["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = manifest.parent.as_posix()
    for key in ("condition_families", "downstream_contract", "decode_workload", "runtime_budget", "bytes_pass", "blinding_group", "draft_notes"):
        tree.pop(key, None)
    tree.update(non_claim=True, draft_status="non-claim", arm_attachments={},
                window_identity={"window_id": "bytes-mac-check", "evidence_root_id": "evidence-bytes-mac-check"},
                roots={"claim_root_leaf": "runs_bytes_mac_check", "bound_root_leaf": "runs_bytes_mac_check_bound"},
                generator={"path": "scripts/bytes_mac_kit.py", "sha256": sha(Path(__file__).read_bytes())})
    collection_plan = {"schema_version": "joulewise.bytes_mac_check.v1", "plan_id": "bytes-mac-check",
                       "non_claim": True, "members": members,
                       "check_runs_per_model": CHECK_RUNS, "soak_runs_per_model": SOAK_RUNS,
                       "test7_pairs_per_end": TEST7_PAIRS, "long_regimes": list(LONG),
                       "authority": "BYTES R2/R8.6; block-6 design §14; threshold note §4 test 7"}
    raw = raw_json(collection_plan)
    files[KIT / "collection_plan.json"] = raw
    tree["plan"] = {"path": "collection_plan.json", "plan_id": "bytes-mac-check",
                    "actual_sha256": sha(raw), "declared_sha256": sha(raw)}
    # Bind reservations to this kit rather than the inherited BETA floor plan.
    tree["external_inputs"] = [r for r in tree["external_inputs"] if "d117_floor_qwen3-8b_v5" not in json.dumps(r)]
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = (KIT / "collection_plan.json").as_posix()
    chain.stage_plan(tree)
    files[KIT / "plan_tree.json"] = raw_json(tree)
    files[KIT / "README.md"] = README.encode()
    smoke_path = Path("configs/b6/smoke_keep.json")
    smoke = json.loads((root / smoke_path).read_bytes())
    smoke["bytes_mac_check"] = compose.smoke_keep(layout)
    files[smoke_path] = raw_json(smoke)
    return files


def generate(output_root=ROOT, *, check=False, source_root=ROOT):
    files = build_files(source_root)
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError("generated kit drifted: " + str(path))
        elif not target.exists() or target.read_bytes() != raw:
            # Do not rewrite unchanged inputs outside the campaign (smoke_keep).
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


README = """# BYTES Mac check: non-claim, R8.6

Generated by `/opt/homebrew/bin/python3.13 scripts/bytes_mac_kit.py`; verify with `--check`.
The fixed tree uses the block-6 composer and chain interfaces. It has no
pack registration, never enters loop.json/base_order, and is never claim data.
Only the lead runs this on the quiet Mac after clearing agent sessions.
This cloud implementation has no hardware validation.

The tree has 5 runs for each of the ten roster models, 12 additional soak runs
for 70B and 122B, and test 7 at start/end for 70B, 122B and Next-80B. Each test-7
stage alternates large/reference/large/reference (two large runs per end,
threshold note §4 row 7; alternation from design §14). The largest workload is
the R2 exact 2,048-token prompt and 512-output-token workload, with the existing
warm-up/settle. The reference remains the existing 1,024/256 workload. Total:
98 kit members plus 18 corpus, 3 start, 1 midpoint and 3 end references = 123.
The corpus may stop at 12 valid members under the inherited non-claim scaffold;
record every planned export row, including skips. Timing/sizing requires all
5 checks and 12 soaks to succeed; it does not quietly size from fewer runs.

Use the fixed campaign at `configs/campaigns/bytes_mac_check/plan_tree.json`
with the existing desk/chain tooling and dedicated non-claim roots. C4 identities,
measurement-checkout pins, calibration and precheck setup belong to the lead's
Mac session; this generator issues none. Explicitly pass `non_claim=True` to
`joulewise.b6.export_runs.export` (or `--non-claim` to the harvest CLI); the tree
label alone is not an export switch. Keep the native `.runs.csv` and matching
`.session.json` together. Non-claim receipts never use blinding keys.

## Known-bytes companion probe

Follow [the known-bytes reading rule §2](../../../docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md#2-the-receipt-change-one-small-code-change-before-the-test)
for each call on the quiet Mac:

```sh
/opt/homebrew/bin/python3.13 scripts/bytes_stream_test.py --bytes B --repeats N --device DEVICE --idle-s 57.6 --settle-s 3 --out RECEIPT
```

Replace DEVICE with `hardware_target.id` from the non-claim checkout's run
config. B and N are explicit integer counts selected by the rule's §1 knee,
size and duration procedure for the eight-call test; there is no guessed
bandwidth-derived default. Use `--idle-s 0 --settle-s 0` only for the knee scan.

The `joulewise.bytes_stream.v2` receipt counts B*N logical uint8 payload bytes,
excluding the warm-up. The probe allocates/fills/evaluates and synchronizes the
payload, runs one warm reduction and synchronizes, waits one settle gap, then stamps pre-idle, stream
and post-idle spans on CLOCK_MONOTONIC_RAW. The three 3 s settle gaps enter no
quantity. The payload stays resident through post-idle. Stream duration excludes
allocation/fill, warm-up, idles and gaps; reduction workspace/dispatch work is
inside the stream span, but workspace bytes are excluded from B*N. This is not
a hardware memory-controller count.

One continuous powermetrics capture and one continuous KM003C meter stream
must cover all eight calls, with one meter clock fit for the test, from its own
non-claim checkout with the registration §19 chain extension. Keep every receipt
with the harvest. The harvest extension must integrate rails, the GPU series,
DC input and the battery term over the receipt's exact stamped spans using the
pass-1 integrators unchanged. Measure the test's own τ = 2*T_SMC + Δt_p; if τ
exceeds 3 s, compute both idle means after trimming the first τ − 3 s from each stamped
idle span, as §2 requires.

The receipt records the runtime stack and local comparison. At harvest, supply
the concurrent capture's `telemetry_backend` and
`measurement_boundary_label.rails` to `compare_stack(..., capture_stack=...)`;
missing capture identity remains pending. The embedded reference is the registered projection at
`6731d5249`, with source SHA256 values in every receipt. The running checkout's
full projected comparison with this reference is recorded, never raised.
`physical_differences` contains only OS/hardware and MLX/MLX-Metal versions;
other differences are disclosures. Git commit is printed, not compared; the
five model-specific fields are `not_applicable`.

Use `scripts/bytes_stream_test.py scan SCAN.json` on the three receipts per
scan size. The uncertainty-separated knee rule and undefined-pair reasons are
printed in full. Use `scripts/bytes_stream_test.py read INPUT.json` on the scan
result plus the eight receipts and governed harvest products (§4 documents the
JSON fields). This computes native meter/battery SEs separately, combines them
as se_DC = se_meter + se_battery, and propagates source-labelled meter gaps as
n × 20 ms × (adapter maximum + measured maximum battery discharge). Gaps do
not discard DC/rest. Descriptions with missing prerequisites print
`not defined (<reason>)`; the OS thermal description uses the notify-bus journal
`hazards/monitor/thermal.jsonl`. Probe execution alone does not implement or
validate the capture and span-integration extension.

MLX imports only on execution. This is a standalone companion probe; it is not
a new runtime adapter or a claim-bearing stage in the fixed tree.

## C5 measured receipts

Run `/opt/homebrew/bin/python3.13 scripts/bytes_gates.py --runs EXPORT.runs.csv
--measurements MEASUREMENTS.json --out C5.json` (one shell command).
It prints one status per gate and writes full arithmetic/provenance JSON.
Exit 0 means the measured gates clear, 2 means at least one fails, 1 means
missing/malformed inputs. `flag only` is disclosed and never converted into
an exclusion. All outputs remain registration candidates.

MEASUREMENTS.json uses schema_version `joulewise.bytes_mac_measurements.v1`,
`non_claim: true`, and the exact exported `session_id`. Its fields are:

- `runs`: map every exported run_id to `request_s`, `member_wall_s`, `stream_s`,
  `retained_bytes`, `thermal_level`, `outside_cpu_s` and `census_quanta`.
  Read request spans from the native event stamps; member wall seconds run
  from member start through preparation, warm-up, idle, request, cooldown,
  reduction and sampler wind-down. Stream seconds span the actual first/last
  paired wall/RAW clock readings used by that run's clock fit, including idle.
  Never use the whole kit/meter stream or a calibration capture as a run span. Thermal level is the maximum OS level;
  exported thermal pressure flags also fail the thermal line. CPU seconds C
  and quanta k come from the same overlapping census journal. Retained bytes
  count the run's raw bundle AND its retained archive copy (disk usage, not
  compressed logical bytes). Include failed/skipped planned rows explicitly;
  absent timing receipts cannot produce a sizing candidate.
- `regimes`: map each of the ten roster model_ids to `F_min_j`,
  `census_resolution_w`, `outside_power_w`, `operative_bound_s`,
  `registered_T10_s` and `registered_T_phase_s`. Floors are the non-claim
  phase-attribution floor derivation, not claim archive results. Keep its
  receipt, operative calibration bound and the census's power-resolution
  derivation beside this file. For T10/T_phase use null until a registered
  line exists; never copy another pack's value. C5 reports the R6 candidate
  F_min/(4*longest measured decode phase) separately from a registered line.
- `clock`: signed `rate_ppm` (measured clock-rate fit), signed
  `frequency_word_ppm` (live kernel word converted to ppm). No kit-level stream
  duration is substituted. The hold uses the longest measured run-level paired
  stamp span, including reference runs, with the registered 5 ms budget, h=0
  and 0.25 ppm frequency margin. The registered S-7 hold checks
  the measured rate r. The live word and whether it clears the same gate are
  printed as diagnostics (registration wins over R6 wording); the 15 ms
  illustrative design form is not used.
- `cpu_contention`: measured `w_j_per_cpu_s` and `c_q_cpu_s`. The registered
  S-8 alternative is w*max(0,C-k*c_q) >= F_min/4. Print every run's C, k,
  excess and energy; round 1 has not adopted this exclusion, so flag only.
- `disk`: integer `pre_arm_free_bytes` and `fixed_retained_bytes`. The latter
  covers all session artifacts outside the per-run bundle+archive bytes,
  counted once. Operational reserve is 150 GiB (design §15 / R6).
- `sizing`: measured `fixed_desk_s` and `collection_stage_overhead_s`.
  Fixed desk seconds is the sum of reservation, pre/post calibration,
  derivation, verdict and backup work, excluding per-member work, collection
  overhead and registered chain settles. Collection overhead excludes all
  of those terms. Preserve the journal timestamps used for each disjoint
  term; no pilot constants are substituted.

The margin is max(max(request_s)/min(request_s)-1) over each model's five
checks and each twelve-run soak (brief P6). Module est_minutes replaces the
pilot value with 50*mean(member_wall_s)*(1+margin)/60. Per-session rows add
reference members, actual stage overhead, registered 60 s chain settles
(before pre-calibration and each collection), and fixed desk work. The same
measured margin applies to member/reference time only. Disk projections use
the largest measured retained bytes per model/reference plus fixed artifacts,
with the 150 GiB reserve. Both pass trees are sized from their real membership;
fixed BYTES sessions bypass the modular 265-minute cap (Addendum 5.5).

The CLI hashes its export, sidecar, receipts and kit plan. Preserve the raw
journals/floor/census derivations behind the measured receipts. It neither
registers these candidates nor edits the twelve draft registrations. The
lead installs C5/C4 after the Mac checks and registration review. Resolvability
ratios are non-claim diagnostics; no invented SNR cut drops 8B-8bit. Test 7's
transfer decision and any roster drop stay with registration; absent a passed
test 7 the ruled scaled drift allowance still applies.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    generate(args.output_root, check=args.check)
    print("verified non-claim Mac kit" if args.check else "generated non-claim Mac kit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
