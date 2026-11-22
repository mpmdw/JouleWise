"""Synthetic registration records only; never native evidence."""
import json
from pathlib import Path
import time

from joulewise.align.apple import v4_registration as reg


def session_plan(root, state=None, *, now=None):
    """Supply a staged synthetic night plan for callers that fake prepare/install.

    Watchdog acceptance still reads the plan and checks its t0 after the fake
    installer returns. Keep that plan inside the caller's temporary fixture.
    """
    state = {} if state is None else state
    path = Path(state.setdefault('plan_path', str(Path(root) / 'night_plan.json')))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'plan_id': 'synthetic-v4',
                               't0_epoch_s': (time.time() if now is None else now) + 3600}))
    return state


def span_aware_watchdog(*, phase, plan=None, now=None, **_):
    """Synthetic watchdog answering as the installed one does: inside the plan span it fences.

    The batch admits an arm inside the span (t0 - 180 s) only on a fence (RL-56); witnesses that
    arm one second before t0 need a watchdog that has fenced, not the plain accepting stand-in.
    """
    import time as _time
    t0 = (plan or {}).get('t0_epoch_s')
    inside = phase == 'post_install' and t0 is not None and (now or _time.time)() >= t0 - 180
    return {'ok': True, 'state': 'FENCED' if inside else ('ACTIVE' if phase == 'post_install' else 'LAUNCHING'),
            'reason': 'synthetic watchdog', 'argv': ['synthetic-watchdog', '--dry-run'],
            'elapsed_s': 0.0, 'plan_read_proven': False}


def held_window_acceptance(measurement_root, packet, *, ruling_path=None):
    """Explicit stand-in for witnesses whose packet/Git evidence is synthetic."""
    return {'ok': True, 'reasons': [], 'synthetic': True}


def localize_c1_artifacts(root, paths=None):
    """Keep the legacy mirror's selected templates inside its fixture root."""
    for relative in sorted(reg.ARTIFACTS if paths is None else paths):
        path = Path(root)
        for part in Path(relative).parts[:-1]:
            path /= part
            if path.is_symlink() and path.is_dir():
                source = path.resolve()
                path.unlink()
                path.mkdir()
                for child in source.iterdir():
                    (path / child.name).symlink_to(child)
            if not path.is_dir():
                break
        else:
            path /= Path(relative).name
            if path.is_symlink():
                raw = path.read_bytes() if path.is_file() else None
                path.unlink()
                if raw is not None:
                    path.write_bytes(raw)


def fixture_c1_preflight(state, supplied, packet_builder):
    """Stand in for Git authority in the pre-existing cadence and runtime witnesses.

    The checkout mirrors in those witnesses are intentionally not attempt
    exports. test_c1_closure exercises the committed C1 authentication boundary.
    """
    from types import SimpleNamespace
    from scripts import align_v4_series as series

    root, view = (Path(state[name]) for name in ('source_measurement_root', 'measurement_root'))
    plan = json.loads((root / series.kit_path('C1') / series.C1_PLAN).read_bytes())
    current = reg.artifact_set_digest(root)

    def preflight(handoff, *, now_epoch_s, **_):
        packet, matches = packet_builder(root, supplied, now_epoch_s=now_epoch_s,
                                        current_artifact_set_sha256=current)
        if not matches:
            raise AssertionError('the cadence fixture builder did not match')
        return {'authority': root, 'state': state, 'plan': plan, 'packet': packet, 'packet_sha256': None,
                'current_digest': current, 'kit': {'ok': True},
                'view': SimpleNamespace(root=view, roots=SimpleNamespace(repo=root))}

    return preflight


def projection_arm_checks(arm):
    """Keep the independent Git/triage deltas on the packet projection path."""
    def run(root, plan, **kwargs):
        # These witnesses deliberately have no prepared attempt or O1 commit.
        # C1 admission and its host checkpoint are covered by the frozen tape.
        return arm(root, {key: value for key, value in plan.items() if key != 'window_id'}, **kwargs)

    return run


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
