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


def build_files(root=ROOT, *, extension=None):
    root = Path(root)
    if extension not in (None, 'qwen38-27b-8bit'):
        raise ValueError('unknown extension')
    kit = KIT if extension is None else Path('configs/campaigns/bytes_mac_check_ext')
    kit_id = 'bytes-mac-check' if extension is None else 'bytes-mac-check-ext'
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
        stage.update(stage_id=kit_id + "-" + label, entries=[], expected_count=len(conditions))
        directory = kit / "stages" / label
        rows = []
        for index, (source, model_id, purpose, end) in enumerate(conditions, 1):
            cfg = json.loads((root / source["config_path"]).read_bytes())
            run_id = source["run_id"] if extension else f"bytes-mac-check-{label}-r{index:02}"
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
                     "module_id": kit_id + "-" + model_id, "pack_id": kit_id}
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

    if extension:
        directory = Path('configs/campaigns/bytes_v1/extension') / extension / '01_decode_absolute'
        entries = json.loads((root / directory / 'order_manifest.json').read_bytes())['executed_order'][:CHECK_RUNS]
        extension_sources = [{**e, 'config_path': (directory / e['config']).as_posix()} for e in entries]

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
    if extension:
        first = collection('check-a', [(e, extension, 'check', 'middle') for e in extension_sources[:3]])
        last = collection('check-b', [(e, extension, 'check', 'middle') for e in extension_sources[3:]])
        stages = fixed[:5] + [first, fixed[5], last] + fixed[6:]
        members = [m for m in members if m['model_id'] == extension]
        files = {p: raw for p, raw in files.items() if p.parent.name in ('check-a', 'check-b')}
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
    files[kit / "collection_plan.json"] = raw
    tree["plan"] = {"path": "collection_plan.json", "plan_id": "bytes-mac-check",
                    "actual_sha256": sha(raw), "declared_sha256": sha(raw)}
    # Bind reservations to this kit rather than the inherited BETA floor plan.
    tree["external_inputs"] = [r for r in tree["external_inputs"] if "d117_floor_qwen3-8b_v5" not in json.dumps(r)]
    for stage in tree["stage_graph"]:
        for command in stage["launch"]["commands"]:
            for arg in command["argv_template"]["arguments"]:
                if arg == {"kind": "repo_path", "value": "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json"}:
                    arg["value"] = (kit / "collection_plan.json").as_posix()
    chain.stage_plan(tree)
    files[kit / "plan_tree.json"] = raw_json(tree)
    if extension:
        # Replace scaffold session identity recursively, including reservations and roots.
        tree = json.loads(json.dumps(tree).replace('bytes_mac_check_ext', 'bytes_mac_check').replace(kit_id, 'bytes-mac-check').replace('bytes-mac-check', kit_id).replace('bytes_mac_check', 'bytes_mac_check_ext'))
        collection_plan = json.loads(json.dumps(collection_plan).replace(kit_id, 'bytes-mac-check').replace('bytes-mac-check', kit_id))
        collection_plan.update(plan_id=kit_id, soak_runs_per_model=0, test7_pairs_per_end=0, long_regimes=[])
        raw = raw_json(collection_plan)
        files[kit / 'collection_plan.json'] = raw
        tree['plan'].update(plan_id=kit_id, actual_sha256=sha(raw), declared_sha256=sha(raw))
        files[kit / 'plan_tree.json'] = raw_json(tree)
        files[kit / 'README.md'] = EXT_README.encode()
        return files
    files[kit / "README.md"] = README.encode()
    smoke_path = Path("configs/b6/smoke_keep.json")
    smoke = json.loads((root / smoke_path).read_bytes())
    smoke["bytes_mac_check"] = compose.smoke_keep(layout)
    files[smoke_path] = raw_json(smoke)
    return files


def generate(output_root=ROOT, *, check=False, source_root=ROOT, extension=None):
    files = build_files(source_root, extension=extension)
    for path, raw in files.items():
        target = Path(output_root) / path
        if check:
            if target.read_bytes() != raw:
                raise ValueError("generated kit drifted: " + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


README = """# BYTES Mac check: non-claim, R8.6

Generated by `python3.13 scripts/bytes_mac_kit.py`; verify with `--check`.
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

Run `python3.13 scripts/bytes_stream_test.py --bytes B --repeats N --out RECEIPT`
under concurrent rails and KM003C capture on the quiet Mac. B and N are explicit
integer counts chosen for the available memory and the planned one-hour test;
there is no guessed bandwidth-derived default. Use a payload above cache
capacity when testing external-memory traffic. The receipt records B*N logical
uint8 payload bytes and its own CLOCK_MONOTONIC_RAW start/end, excluding initial
allocation/fill. It includes reduction workspace/dispatch in the span, and does
not claim a hardware memory-controller count. Keep the receipt with the harvest;
map/integrate rails and DC input over its exact start/end to compare boundaries.
MLX imports only on execution. This is a standalone companion probe; it is not
a new runtime adapter or a claim-bearing stage in the fixed tree.

## C5 measured receipts

Run `python3.13 scripts/bytes_gates.py --runs EXPORT.runs.csv
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



EXT_README = """# BYTES extension Mac check: non-claim

Generate: `python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit`.
Verify: add `--check`. The original kit is frozen and unchanged.

This separate fixed tree has five extension absolute runs (the exact source
run IDs r01..r05), split 3/2 around the inherited midpoint reference. It reuses
the block-6 corpus (18 planned, stop at 12 valid), start triplet, midpoint and
end triplet, calibration and launch scaffold. R2 is unchanged: 2,048 prompt
and 512 output tokens with existing warm-up and settle.

The original kit's R8.6 rule is "five structural runs per model and twelve
additional soak runs for 70B/122B". Its threshold note §4 row 7 implementation
uses "two large runs at each end" for 70B, 122B and Next-80B (alternating with
references per design §14). This 27B dense model is outside those regimes:
no soak or test-7 stages are added. No new numerical threshold is introduced.

Only the lead runs on the Mac, in a desk worktree with the loop held and no
agent alive. Never register this kit or add it to loop.json/base_order. Dedicated
roots are runs_bytes_mac_check_ext and runs_bytes_mac_check_ext_bound. C4,
calibration, pins and precheck remain lead-owned; do not integrate this change
into the measurement checkout without its fingerprint review.

Mac commands (Python 3.13 measurement venv; JW_B5_SYNTHETIC_ONLY must be unset
for live collection):

```sh
python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --check
python3.13 -B scripts/check_b5_chain.py --pack-root configs/campaigns/bytes_mac_check_ext --no-live-identity
```

Use the existing desk/chain tooling with fixed campaign
`configs/campaigns/bytes_mac_check_ext/plan_tree.json`, as for the original kit.
The check command validates the fixed tree without launching a measurement. Export explicitly with
`joulewise.b6.export_runs.export(..., non_claim=True)` (or the harvest CLI's
`--non-claim`); the tree label alone is not an export switch. Preserve native
EXPORT.runs.csv and EXPORT.session.json together, including scaffold rows and
failed/skipped rows. No blinding keys are used.

Harvest the lead-prepared session plan (PLAN, ARCHIVE, REGISTRATION and
PACK_RECORDS are the desk's existing session paths, not new pack registrations):

```sh
python3.13 -B scripts/harvest_b6_session.py --plan "$PLAN" --archive-root "$ARCHIVE" --registration-dir "$REGISTRATION" --pack-records-root "$PACK_RECORDS" --export-dir "$EXPORT_DIR" --non-claim
```

Prepare MEASUREMENTS.json with schema_version
joulewise.bytes_mac_measurements.v1, non_claim true, the export session_id,
and a runs map with every exported run_id. As in the original kit, each receipt
has request_s, member_wall_s (whole member including preparation and wind-down)
and stream_s (that run's first/last paired wall/RAW stamps, including idle).
Keep the source journals; do not substitute decode time or whole-session spans.
For step-7 sizing also supply sizing.fixed_desk_s and
sizing.collection_stage_overhead_s, disjoint measured terms as in the original kit.

```sh
python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --runs EXPORT.runs.csv --measurements MEASUREMENTS.json --out resolvability.json
```

Exit 0 passes, 2 fails the five-run rule, malformed input raises an error.
The checker requires five succeeded, unexcluded, 512-token runs with finite
positive dur_decode_s. It prints no energy result. It records runs_checked,
decode_phase_s_range, verdict, per-member walls and stream spans, and sizing
operands plus S and T_stream_max for the lead. S uses the registered formula
for the eventual 50-science-member single-model pack, 25 references and seven
collections; it is not the duration of this diagnostic kit. Missing scaffold
or sizing receipts leave S unavailable. Only Mac receipts may fill slots;
this checker never writes slots or registrations.
"""


def evaluate_extension(rows, sidecar, measured):
    """Native non-claim export only; no energy fields or new threshold."""
    import math
    from scripts.bytes_gates import sizing_span
    def positive(value):
        if isinstance(value, bool):
            raise ValueError('boolean duration')
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError('duration must be finite and positive')
        return value
    session = sidecar['session_id']
    if (sidecar.get('non_claim') is not True or sidecar.get('pack_id') != 'bytes-mac-check-ext'
            or measured.get('non_claim') is not True or measured.get('session_id') != session
            or measured.get('schema_version') != 'joulewise.bytes_mac_measurements.v1'):
        raise ValueError('requires matching non-claim extension session')
    by_id = {}
    for row in rows:
        if (row['run_id'] in by_id or row['session_id'] != session
                or row['pack_id'] != 'bytes-mac-check-ext' or row['non_claim'] != 'True'):
            raise ValueError('duplicate, claim or foreign export row')
        by_id[row['run_id']] = row
    if set(measured['runs']) != set(by_id):
        raise ValueError('timing receipt membership differs from export')
    if not by_id:
        raise ValueError('empty export')
    expected = [f'bytes-qwen38-27b-8bit-abs-r{i:02}' for i in range(1, 6)]
    details, phases = [], []
    for rid in expected:
        row = by_id.get(rid, {})
        ok = (row.get('status') == 'succeeded' and row.get('excluded') == 'False'
              and row.get('emitted_tokens') == '512')
        try:
            phase = positive(row.get('dur_decode_s'))
        except (ValueError, TypeError):
            phase, ok = None, False
        if phase is not None:
            phases.append(phase)
        details.append({'run_id': rid, 'pass': ok, 'decode_phase_s': phase})
    timings = {}
    for rid, receipt in measured['runs'].items():
        if by_id[rid]['status'] == 'succeeded':
            timings[rid] = {k: positive(receipt[k]) for k in ('request_s', 'member_wall_s', 'stream_s')}
            if min(timings[rid]['member_wall_s'], timings[rid]['stream_s']) < timings[rid]['request_s']:
                raise ValueError('member/stream shorter than request')
    verdict = 'pass' if all(d['pass'] for d in details) else 'fail'
    science = [timings[r] for r in expected if r in timings]
    refs = [v for r, v in timings.items() if by_id[r].get('role') in ('corpus', 'start', 'midpoint', 'end')]
    sizing = measured.get('sizing', {})
    span = None
    margin = None
    # The scaffold plans every row, including corpus skips. Do not size from
    # a partial harvest or a lone surviving reference.
    tree = json.loads((ROOT / 'configs/campaigns/bytes_mac_check_ext/plan_tree.json').read_bytes())
    inventory = set()
    for stage in tree['stage_graph']:
        ref = stage.get('input', {})
        if ref.get('kind') == 'manifest':
            manifest = json.loads((ROOT / ref['path']).read_bytes())
            inventory.update(e['run_id'] for e in manifest['executed_order'])
    if set(by_id) - inventory:
        raise ValueError('export contains unplanned runs')
    roles = {role: sum(by_id[r].get('role') == role for r in timings)
             for role in ('corpus', 'start', 'midpoint', 'end')}
    complete = (set(by_id) == inventory and roles['corpus'] >= 12
                and roles['start'] == 3 and roles['midpoint'] == 1 and roles['end'] == 3)
    if verdict == 'pass' and len(science) == 5 and complete:
        margin = max(v['request_s'] for v in science) / min(v['request_s'] for v in science) - 1
        if all(k in sizing for k in ('fixed_desk_s', 'collection_stage_overhead_s')):
            fixed, overhead = (float(sizing[k]) for k in ('fixed_desk_s', 'collection_stage_overhead_s'))
            if not all(math.isfinite(v) and v >= 0 for v in (fixed, overhead)):
                raise ValueError('invalid sizing duration')
            span = sizing_span(50 * sum(v['member_wall_s'] for v in science) / 5, 25,
                               sum(v['member_wall_s'] for v in refs) / len(refs), margin, 7, overhead, fixed)
    return {'non_claim': True, 'runs_checked': len(expected), 'verdict': verdict,
            'decode_phase_s_range': [min(phases), max(phases)] if phases else None,
            'runs': details, 'member_timings': timings, 'measured_margin': margin,
            'S': span, 'T_stream_max': max((v['stream_s'] for v in science), default=None)}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument('--extension', choices=['qwen38-27b-8bit'])
    parser.add_argument('--runs', type=Path, help='harvested native .runs.csv to evaluate')
    parser.add_argument('--measurements', type=Path, help='member timing receipts, as in the original kit')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    if args.runs:
        if not args.extension or not args.measurements or not args.out:
            parser.error('--runs requires --extension, --measurements and --out')
        import csv
        with args.runs.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        sidecar_path = args.runs.with_suffix('').with_suffix('.session.json')
        result = evaluate_extension(rows, json.loads(sidecar_path.read_bytes()),
                                    json.loads(args.measurements.read_bytes()))
        result['inputs_sha256'] = {str(p): sha(p.read_bytes()) for p in
                                  (args.runs, sidecar_path, args.measurements,
                                   ROOT / 'configs/campaigns/bytes_mac_check_ext/plan_tree.json')}
        args.out.write_bytes(raw_json(result))
        return 0 if result['verdict'] == 'pass' else 2
    generate(args.output_root, check=args.check, extension=args.extension)
    print("verified non-claim Mac kit" if args.check else "generated non-claim Mac kit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
