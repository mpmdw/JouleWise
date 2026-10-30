"""Does a stored precheck carrying a claim-gate code reach the precheck's reasons? (run at head and under M9)"""
import sys; sys.path.insert(0, sys.argv[1])
from joulewise.analysis_engine.inputs import BundleEvidence, window_evidence_precheck
from pathlib import Path
ev = BundleEvidence(entry={}, bundle_id='syn', relative_path='syn', path=Path('/nonexistent'),
    summary={'status': 'succeeded', 'window_evidence_precheck': {'gross_request': {'eligible': False, 'reasons': ['paired_block_incomplete']}},
             'measurement_quality': {'cooldown_cap_hit': False}},
    metadata={}, raw_config={}, strict_problems=(), base_reason_codes=(), config_sha256='0'*64, summary_sha256='0'*64,
    replacement_classification='registered', inclusion_status='included')
r = window_evidence_precheck(ev, {'name': 'gross_energy_j', 'metric_tag': 'gross_request', 'window_class': 'request'})
print(sys.argv[2], 'reasons:', r['reasons'], '| paired_block_incomplete forwarded:', 'paired_block_incomplete' in r['reasons'])
