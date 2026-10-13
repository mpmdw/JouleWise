#!/usr/bin/env python3
"""Copy checked verdicts and analysed-window structure to a fill input file."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys

REPO_ROOT=Path(__file__).resolve().parents[1]
if __package__ in (None,''):sys.path.insert(0,str(REPO_ROOT))
from joulewise.authentication_io import read_authentication_input_nofollow
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins, load_window_index, select_analysed_attempts
from joulewise.b5_analysis.archive import open_attempt_record
from joulewise.analysis_engine.inputs import block5_claim_gate_inputs
from joulewise.results_fill_adapter import ResultsFillAdapterError, adapt_claim_verdicts, render_results_fill_input, _object, _nonfinite

CHECK_CODES=frozenset({'results_fill_manifest_mismatch','results_fill_floor_mismatch',
    'results_fill_exclusions_mismatch','results_fill_kept_quads_mismatch','results_fill_contrast_census_mismatch',
    'results_fill_output_exists','results_fill_path_refused','results_fill_input_invalid'})


def _read_under(root,path):
    path=Path(path)
    if '..' in path.parts:raise ResultsFillAdapterError('results_fill_path_refused')
    absolute=path.absolute()
    try:relative=absolute.relative_to(root).as_posix()
    except ValueError:raise ResultsFillAdapterError('results_fill_path_refused') from None
    try:return read_authentication_input_nofollow(root,relative,grammar='json',label='results-fill custody input')
    except (OSError,ValueError,RuntimeError):raise ResultsFillAdapterError('results_fill_path_refused') from None


def _registered_contrast_ids(pack_id):
    from joulewise.paper_custody import _git_blob
    relative=f'configs/campaigns/{pack_id}/analysis_manifest_v3.json'
    raw=_git_blob(REPO_ROOT,'HEAD',relative)
    if raw!=read_authentication_input_nofollow(REPO_ROOT,relative,grammar='json',label='sealed GAMMA manifest'):
        raise ResultsFillAdapterError('results_fill_contrast_census_mismatch')
    return tuple(row['contrast_id'] for row in json.loads(raw)['contrasts'])


def build(window_index,custody_root,finalized_manifest,claim_verdicts):
    root=Path(custody_root).absolute()
    if '..' in Path(custody_root).parts or root.resolve(strict=True)!=root or not root.is_dir():
        raise ResultsFillAdapterError('results_fill_path_refused')
    manifest_raw=_read_under(root,finalized_manifest)
    verdicts_raw=_read_under(root,claim_verdicts)
    manifest=json.loads(manifest_raw.decode(),object_pairs_hook=_object,parse_constant=_nonfinite)
    record=manifest['evidence']['aggregate_floor_artifact']
    relative=record['path']
    if (type(relative) is not str or Path(relative).is_absolute() or
        any(p in ('','.','..') for p in relative.split('/'))):
        raise ResultsFillAdapterError('results_fill_path_refused')
    floor_path=root/relative;floor_raw=_read_under(root,floor_path)
    if hashlib.sha256(floor_raw).hexdigest()!=record['sha256']:
        raise ResultsFillAdapterError('results_fill_floor_mismatch')
    pins=SealPins.load()
    index=load_window_index(Path(window_index),seal_pins=pins)
    records=tuple(open_attempt_record(e,seal_pins=pins) for e in index.entries)
    windows=select_analysed_attempts(index,records,seal_pins=pins)
    expected=_registered_contrast_ids(windows['gamma'].pack_id)
    built=block5_claim_gate_inputs(Path(window_index),Path(finalized_manifest).absolute(),windows['gamma'].claim_runs_root)
    units=built['kept_units']
    campaigns={}
    for pack in ('alpha','beta'):
        window=windows[pack]
        from joulewise.b5_analysis.archive import open_archive
        archive=open_archive(window,seal_pins=pins)
        exclusions=archive.output_bytes('derived/exclusions.json')
        campaigns[pack]={'plan_id':window.plan_id,'attempt':window.attempt,
            'claim_usable':window.record.claim_usable,'exclusions_sha256':hashlib.sha256(exclusions).hexdigest(),
            'harvest_record_sha256':window.harvest_record_sha256}
    return adapt_claim_verdicts(verdicts_raw,campaigns=campaigns,finalized_manifest_raw=manifest_raw,
        floor_artifact_raw=floor_raw,exclusions_sha256=units.exclusions_sha256,
        kept_quads={cid:units.for_contrast(cid) for cid in expected},expected_contrast_ids=expected)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('window-index','custody-root','finalized-manifest','claim-verdicts','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args(argv)
    output_created=False
    try:
        if args.out.exists():raise ResultsFillAdapterError('results_fill_output_exists')
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            value=build(args.window_index,args.custody_root,args.finalized_manifest,args.claim_verdicts)
        raw=render_results_fill_input(value)
        try:
            with args.out.open('xb') as out:
                output_created=True
                out.write(raw)
        except FileExistsError:raise ResultsFillAdapterError('results_fill_output_exists') from None
        return 0
    except ResultsFillAdapterError as exc:
        code=str(exc).split(':',1)[0]
        print('error: '+(code if code in CHECK_CODES else 'results_fill_input_invalid'),file=sys.stderr)
    except AnalysisRefusal as exc:
        print('error: '+exc.code,file=sys.stderr)
    except Exception:
        if output_created:
            try:args.out.unlink(missing_ok=True)
            except OSError:pass
        print('error: results_fill_input_invalid',file=sys.stderr)
    return 2

if __name__=='__main__':raise SystemExit(main())
