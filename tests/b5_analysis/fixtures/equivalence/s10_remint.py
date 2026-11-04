"""Re-mint a synthetic S10 custody tree at another analysis commit (D-188 comparator acceptance).

    python3 -B tests/b5_analysis/fixtures/equivalence/s10_remint.py SRC DST NEW_COMMIT [--mutate KIND]

SRC is a synthetic S10 custody tree (open-listed window index only); DST must not
exist. DST is SRC as the same analysis would have written it at NEW_COMMIT: the
commit lands in the floor artifacts (provenance.implementation.project_commit), the
paper floor acceptance anchor and the record, and every field derived from those
artifacts is re-derived with the producers' own functions:

* the per-producer component floor digests, producer pins and producer-set digest of
  each floor-mint pinset (scripts/emit_floor_mint_pinset.py: mint._artifact_sha256,
  mint._canonical_json_sha256), checked by the mint's own validator
  (mint._validate_v2_artifact_binding), and the aggregate's plan-set pin;
* the finalized manifest's evidence row and manifest_id
  (analysis_manifest_v3.calculate_manifest_id, render_manifest);
* the closeout's source references (dominance_closeout.canonical_json_sha256);
* the claim verdicts' input pins, embedded floor bytes and claim_verdicts_id
  (analysis_engine.artifact.calculate_claim_verdicts_id, render_claim_verdicts);
* every file digest and hex-named path that names a changed file, to a fixed point,
  and the record's committed output digests.

--mutate hides one result change behind those recomputed digests:

* 'floor': a floor value of the aggregate floor artifact (cells[0].floor_gate_j);
* 'manifest': a finalized-manifest field (design.synthetic_mutation);
* 'producer-drift': a drift allowance value of a pinset producer row;
* audit-keyed leaves of a referent (PR #643 review), each audit tier where it is stored:
  'floor-audit' (floor cell model identity, source_regime.stack_identity.model_artifact_sha256),
  'producer-audit' (producer row model_runtime_config.model_artifact_sha256),
  'producer-extraction-pin' (producer row extraction_spec.sha256 and its per-cell copies),
  'manifest-lineage' (finalized-manifest lineage.finalized_semantics_sha256) and
  'manifest-evidence' (the whole-window-verdict evidence pin set to a digest of no artifact,
  which the comparator must refuse as unverifiable).

Synthetic data only.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import itertools
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from joulewise.analysis_engine.artifact import calculate_claim_verdicts_id, render_claim_verdicts  # noqa: E402
from joulewise.analysis_manifest_v3 import calculate_manifest_id, render_manifest  # noqa: E402
from joulewise.dominance_closeout import canonical_json_sha256  # noqa: E402
from scripts import mint_floor_artifact_generalized as mint  # noqa: E402

RECORD = 'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
HEX = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
OPEN_S10_INDEX = '6e76ce7a2e31ea5e851875618f88e40864d73920aeed61520baa9f6d6047f2bc'
CONTAINMENT = ('mint_commit_contained_in_origin_main', 'head_pin_commit_contained_in_origin_main')
MUTATIONS = ('floor', 'manifest', 'producer-drift', 'floor-audit', 'producer-audit', 'producer-extraction-pin',
             'manifest-lineage', 'manifest-evidence')
FAKE = 'f' * 8 + '0123456789abcdef' * 3 + 'e' * 8      # a digest of no artifact


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def closeout_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()


def component(aggregate, pinset, index, variant):
    """The component the mint's validator rebuilds (mint._validate_v2_artifact_binding), at a containment variant."""
    producer = pinset['producer_plans'][index]
    provenance = aggregate['provenance']
    out = copy.deepcopy(aggregate)
    out['artifact_id'] = pinset['aggregate']['component_artifacts'][index]['artifact_id']
    plan = producer['plan']
    out['provenance'] = {
        'calibration_plan': {k: plan[k] for k in ('plan_id', 'declared_calibration_scope', 'relative_path', 'sha256')},
        'mint_tool_version': mint.V2_MINT_TOOL_VERSION, 'assurance': copy.deepcopy(mint.V2_ASSURANCE_PROFILE),
        'implementation': copy.deepcopy(provenance['implementation'])}
    config_set = mint.detection_floor.floor_mint_producer_config_set(producer)
    if config_set is not None:
        out['provenance']['producer_config_sets'] = [config_set]
    if provenance.get('calibration_custody_store') is not None:
        out['provenance']['calibration_custody_store'] = copy.deepcopy(provenance['calibration_custody_store'])
    lineage = provenance.get('launch_lineage')
    if 'producer_launch_lineages' in provenance:
        lineage = provenance['producer_launch_lineages'][index].get('launch_lineage')
    if lineage is not None:
        out['provenance']['launch_lineage'] = copy.deepcopy(lineage)
    cells = {c['cell_id']: c for c in aggregate['cells']}
    groups = {g['transport_group_id']: g for g in aggregate['transport_groups']}
    out['cells'] = [copy.deepcopy(cells[c['cell_id']]) for c in producer['cells']]
    out['transport_groups'] = [copy.deepcopy(groups[c['transport_group_id']]) for c in producer['cells']]
    for key, value in zip(CONTAINMENT, variant):
        out['provenance']['implementation'][key] = value
    return out


def matched_variant(aggregate, pinset, index):
    hits = [v for v in itertools.product((False, True, None), repeat=2)
            if mint._artifact_sha256(component(aggregate, pinset, index, v))
            == pinset['aggregate']['component_artifacts'][index]['sha256']]
    if len(hits) != 1:
        raise SystemExit(f'source pinset component {index} does not rebuild')
    return hits[0]


def remint_floor(aggregate, pinset, variants):
    """Re-derive the pinset's component, producer and producer-set digests and the aggregate's plan-set pin."""
    producers = pinset['producer_plans']
    for i, producer in enumerate(producers):
        producer['component_artifact']['sha256'] = mint._artifact_sha256(component(aggregate, pinset, i, variants[i]))
    entries = pinset['aggregate']['component_artifacts']
    for producer, entry in zip(producers, entries, strict=True):
        entry['sha256'] = producer['component_artifact']['sha256']
        entry['producer_pin_sha256'] = mint._canonical_json_sha256(producer)
    pinset['aggregate']['producer_set_sha256'] = mint._canonical_json_sha256(producers)
    aggregate['provenance']['calibration_plan']['sha256'] = pinset['aggregate']['producer_set_sha256']
    errors = [e for e in mint._validate_v2_artifact_binding(aggregate, mint._parse_v2_pinset(pinset))
              if 'hash' in e]
    if errors:
        raise SystemExit(f'mint validator refuses the re-minted pair: {errors[0]}')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('src', type=Path)
    ap.add_argument('dst', type=Path)
    ap.add_argument('commit')
    ap.add_argument('--mutate', choices=MUTATIONS)
    a = ap.parse_args(argv)
    if not re.fullmatch(r'[0-9a-f]{40}', a.commit):
        raise SystemExit('commit must be 40 lowercase hex')
    record = json.loads((a.src / RECORD).read_bytes())
    if record['window_index_sha256'] != OPEN_S10_INDEX:
        raise SystemExit('only the open-listed synthetic S10 index may be re-minted')
    old_commit = record['analysis_commit']
    shutil.copytree(a.src, a.dst, symlinks=True)
    shutil.rmtree(a.dst / 'equivalence', ignore_errors=True)
    restricted = a.dst / 'dry-run' / 'restricted'
    names = [o['name'] for row in record['steps'] for o in row['outputs']]
    files = {n: (restricted / n).read_bytes() for n in names}
    original = dict(files)

    def one(pattern):
        hits = [n for n in files if re.fullmatch(pattern, n)]
        if len(hits) != 1:
            raise SystemExit(f'expected one output matching {pattern}')
        return hits[0]

    floors = [one(r'mint/[0-9a-f]{64}-aggregate-floor\.json'), one(r'finalized/mint/[0-9a-f]{64}-aggregate-floor\.json')]
    pinsets = ['mint/floor-mint-pinset.json', 'finalized/mint/floor-mint-pinset.json']
    manifest = one(r'finalized/am-[0-9a-f]{64}\.finalized\.json')
    closeout = 'finalized/outputs/closeout.json'
    verdicts = one(r'outputs/[0-9a-f]{64}-claim-verdicts\.json')
    # The writers reproduce the source bytes exactly, so every rewrite below is the producer's format.
    for name, render in ((floors[0], mint._artifact_payload), (pinsets[0], mint._artifact_payload),
                         (manifest, render_manifest), (closeout, closeout_bytes), (verdicts, render_claim_verdicts)):
        if render(json.loads(files[name])) != files[name]:
            raise SystemExit(f'{name}: writer does not reproduce the source bytes')
    variants = [matched_variant(json.loads(files[floors[0]]), json.loads(files[pinsets[0]]), i) for i in range(2)]

    # 1. The new commit everywhere it is written (floor provenance, acceptance anchor, record).
    for name in files:
        files[name] = files[name].replace(old_commit.encode(), a.commit.encode())
    # 2. Optional hidden mutation, then the floor/pinset digests (both custody copies are byte copies).
    agg, pin = json.loads(files[floors[0]]), json.loads(files[pinsets[0]])
    if a.mutate == 'floor':
        cell = agg['cells'][0]
        cell['floor_gate_j'] = cell['floor_gate_j'] * 2 + 1
    elif a.mutate == 'producer-drift':
        pins = pin['producer_plans'][0]['cells'][0]['absolute']
        pins['drift_allowance_j'] = pins['drift_allowance_j'] * 2 + 1
    elif a.mutate == 'floor-audit':
        agg['cells'][0]['source_regime']['stack_identity']['model_artifact_sha256'] = FAKE
    elif a.mutate == 'producer-audit':
        pin['producer_plans'][0]['model_runtime_config']['model_artifact_sha256'] = FAKE
    elif a.mutate == 'producer-extraction-pin':
        # The extraction-spec pin of producer 0, everywhere the row states it (the mint requires them equal).
        old = pin['producer_plans'][0]['extraction_spec']['sha256']
        pin['producer_plans'][0] = json.loads(json.dumps(pin['producer_plans'][0]).replace(old, FAKE))
    remint_floor(agg, pin, variants)
    for name in floors:
        files[name] = mint._artifact_payload(agg)
    for name in pinsets:
        files[name] = mint._artifact_payload(pin)

    renames = {}

    def cascade():
        """Old digest -> new digest for every changed output, applied as text, to a fixed point."""
        history = {n: {sha(original[n])} for n in files}
        while True:
            for n in files:
                history[n].add(sha(files[n]))
            # Every digest a file has had (its original and any intermediate) maps to its current one.
            mapping = {old: sha(files[n]) for n in files for old in history[n] if old != sha(files[n])}
            changed = False
            for n in files:
                if n in (floors + pinsets):
                    continue
                data = HEX.sub(lambda m: mapping.get(m.group(0), m.group(0)), files[n].decode('utf-8', 'surrogateescape'))
                data = data.encode('utf-8', 'surrogateescape')
                data = derive(n, data)
                if data != files[n]:
                    files[n], changed = data, True
            if not changed:
                return mapping

    def derive(n, data):
        if n == manifest:
            value = json.loads(data)
            ev = value['evidence']['aggregate_floor_artifact']
            ev['sha256'] = sha(files[floors[1]])
            ev['path'] = re.sub(r'[0-9a-f]{64}', ev['sha256'], ev['path'])
            if a.mutate == 'manifest':
                value['design']['synthetic_mutation'] = 'hidden behind a recomputed manifest_id'
            elif a.mutate == 'manifest-lineage':
                value['lineage']['finalized_semantics_sha256'] = FAKE
            elif a.mutate == 'manifest-evidence':
                value['evidence']['whole_window_verdict']['sha256'] = FAKE
            value['manifest_id'] = calculate_manifest_id(value)
            return render_manifest(value)
        if n == closeout:
            value = json.loads(data)
            fm, floor = json.loads(files[manifest]), json.loads(files[floors[1]])
            value['finalized_manifest_sha256'] = sha(files[manifest])
            value['sources']['finalized_manifest'].update(canonical_json_sha256=canonical_json_sha256(fm),
                                                          identity=fm['manifest_id'])
            value['sources']['floor_artifact']['canonical_json_sha256'] = canonical_json_sha256(floor)
            return closeout_bytes(value)
        if n == verdicts:
            value = json.loads(data)
            inputs = value['inputs']
            inputs['analysis_manifest'].update(manifest_id=json.loads(files[manifest])['manifest_id'],
                                               file_sha256=sha(files[manifest]))
            inputs['floor_artifact'].update(file_sha256=sha(files[floors[1]]),
                                            embedded_bytes_base64=base64.b64encode(files[floors[1]]).decode('ascii'))
            value['claim_verdicts_id'] = calculate_claim_verdicts_id(value)
            return render_claim_verdicts(value)
        return data

    mapping = cascade()
    # 3. Write the tree: hex-named outputs take their new digest; the record re-commits every output.
    for n, data in files.items():
        new_name = HEX.sub(lambda m: mapping.get(m.group(0), m.group(0)), n)
        if new_name != n:
            (restricted / n).unlink()
            renames[n] = new_name
        (restricted / new_name).write_bytes(data)
    raw = (a.dst / RECORD).read_bytes().decode().replace(old_commit, a.commit)
    raw = HEX.sub(lambda m: mapping.get(m.group(0), m.group(0)), raw)
    rec = json.loads(raw)
    for row in rec['steps']:
        for out in row['outputs']:
            if sha((restricted / out['name']).read_bytes()) != out['sha256']:
                raise SystemExit(f'record does not re-commit {out["name"]}')
    (a.dst / RECORD).write_text(raw)
    print(json.dumps({'changed_outputs': sorted(n for n in files if files[n] != original[n]),
                      'renamed': len(renames), 'mutation': a.mutate}, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
