"""(b) site 1: mint consumption session on the S10 BETA window, control vs forced wall deadline."""
import hashlib, json, time, types, traceback
from unittest import mock


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time'); self._now = time.monotonic()
    def monotonic(self):
        self._now += 1000.0; return self._now
    def __getattr__(self, n):
        return getattr(time, n)


def main():
    from joulewise import powermetrics_fiducial as pf, whole_window as ww
    from tests.b5_analysis import test_mint_kept_units as t
    from tests.b5_analysis.fixtures_s10 import chain_fixture
    refits = [0]; orig = pf.rederive_detection_from_artifacts
    def counted(*a, **k):
        refits[0] += 1; return orig(*a, **k)
    pf.rederive_detection_from_artifacts = counted
    chain = chain_fixture()
    R = {}
    def attempt(label, forced, cache=None):
        refits[0] = 0
        ctx = ww.shared_instrument_calibration_physics_cache(cache) if cache is not None else mock.patch.dict({}, {})
        try:
            with chain.seams(), ctx, (mock.patch.object(pf, 'time', JumpingClock()) if forced else mock.patch.dict({}, {})):
                entry = t.mint.compose_indexed_producers(chain.index, include_consumer=True)["beta"]
                ids = t.core._producer_bundle_ids(entry)
                with t.registered({str(entry.window.claim_runs_root.resolve()): entry}):
                    summaries, semantics = t.core._authenticated_consumption_summaries(entry.window.claim_runs_root, ids,
                        entry.verdict_row["evaluation_basis"]["sha256"], target_bundle_ids=ids,
                        consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                        calibration_ledger_snapshot=entry.ledger_snapshot)
            digest = hashlib.sha256(json.dumps(summaries, sort_keys=True, default=str).encode()).hexdigest()
            R[label] = dict(outcome='returned', members=len(summaries), all_ids=set(summaries) == ids,
                            semantics=semantics, digest=digest, refits=refits[0])
        except BaseException as exc:  # noqa: BLE001
            R[label] = dict(outcome=type(exc).__name__, code=getattr(exc, 'code', None),
                            msg=str(exc)[:300], refits=refits[0], where=traceback.format_exc().splitlines()[-3][:200])
    attempt('control', False)
    attempt('forced', True)
    warm = {}
    attempt('warm_fill', False, warm)
    attempt('forced_with_warm_cache', True, warm)
    print(json.dumps(R, indent=1, default=str))


if __name__ == '__main__':
    main()
