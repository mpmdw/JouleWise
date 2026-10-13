#!/usr/bin/env python3
"""Issue reported energies from a sealed analysed floor window."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from joulewise.paper_reported_energy_issuer import issue_pack
from joulewise.b5_analysis.windows import AnalysisRefusal


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--window-index',type=Path,required=True)
    parser.add_argument('--pack',choices=('alpha','beta'),required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    output_created=False
    try:
        if args.output.exists():
            raise AnalysisRefusal('reported_energy_output_exists')
        value=issue_pack(args.window_index,args.pack)
        targets=[r for r in value['refused_cells'] if r['target']]
        if targets:
            raise AnalysisRefusal(targets[0]['code'])
        raw=(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
        try:
            with args.output.open('xb') as out:
                output_created=True
                out.write(raw)
        except FileExistsError:
            raise AnalysisRefusal('reported_energy_output_exists') from None
        structure={'pack':args.pack,'output_sha256':hashlib.sha256(raw).hexdigest(),
            'cells':[{'cell_id':c['cell_id'],'n_r':c['interval']['n_r'],'n_b':c['interval']['n_b'],
                'per_token_status':c['per_token']['status'],'per_token_reason':c['per_token']['reason']}
                for c in value['cells']],
            'refused_cells':[{k:r[k] for k in ('cell_id','code')} for r in value['refused_cells']]}
        print(json.dumps(structure,sort_keys=True,separators=(',',':')))
        return 0
    except AnalysisRefusal as exc:
        print('error: '+exc.code,file=sys.stderr)
    except Exception:
        if output_created:
            try:args.output.unlink(missing_ok=True)
            except OSError:pass
        print('error: reported_energy_input_invalid',file=sys.stderr)
    return 2

if __name__=='__main__':raise SystemExit(main())
