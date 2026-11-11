"""Synthetic registration records only; never native evidence."""
from joulewise.align.apple import v4_registration as reg

def export():
    pairs = [dict(session=f'pilot-{i}', population='30B', phase='pilot',
                  ordinals=[5, 17], token_identical=True, clock_difference_fraction=0.,
                  eligible=True, configuration_sha256='b'*64, source_sha256='c'*64,
                  energies_j=[1000*(1-r/2), 1000*(1+r/2)])
             for i, r in enumerate([-.004, -.002, -.001, 0., .001, .002, .004], 4)]
    pairs.append(dict(pairs[0], session='R1', population='D', phase='R1', ordinals=[2, 3], qualification_only=True,
                      energies_j=[30000, 30030]))
    policy = dict(method='session_zero_rms_series_exact_v1', series_alpha=.05,
                  checks_by_window={'W1': {'30B': 4, 'D': 1},
                                    **{f'C{i}': {'30B': 0, 'D': 1} for i in range(1, 15)},      # RL-16: all C/T reserves, N = 24
                                    **{f'T{i}': {'30B': 0, 'D': 1} for i in range(1, 6)}},
                  d_transfer_factor=1.5, d_configuration_sha256='b'*64,
                  r1_configuration_sha256='b'*64, transfer_justification_sha256='f'*64,
                  r1_D_qualification='adjacent_matched_predecessor_screen_only',
                  selection='one_prespecified_pair_per_session', simulations=1000, seed=2203)
    return {'pairs': pairs, 'policy': policy}


def signed_bar():
    data = export()
    bar = reg.derive_u3(data['pairs'], {'pairs.json': 'a'*64, 'transfer.md': 'f'*64}, policy=data['policy'])
    bar.update(status='registered', lead_signature='lead: synthetic 2026-11-08',
               independent_gate={'verdict': 'ADMIT', 'path': 'docs/align/v4/synthetic-gate.json',
                                 'sha256': 'd'*64, 'derivation_sha256': bar['derivation_sha256']})
    return bar


def battery_policy():
    return dict(schema='joulewise.align_v4.battery_window.v1', status='registered',
                rule='zero_B_auto_resume_v1', lead_signature='lead: synthetic 2026-11-08')
