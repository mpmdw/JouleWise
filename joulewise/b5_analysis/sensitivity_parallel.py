"""Ordered sensitivity passes; leaf derivations stay in the custody-mode census."""
from .sensitivity import derive_pack  # noqa: F401


def sensitivity_pass_pack(windows, kept_units, contexts, brackets, b_max, **kwargs):
    """Compute one pass and carry its caller-owned archive effects back.

    run_pack supplies this pass its member_worker_shares budget. The pass's
    derive_pack pool subdivides that share again, rather than using the whole
    run's budget. Failed passes are rerun serially by consume, preserving their
    partial archive censuses and the original refusal position.
    """
    from .context import _SourcesReplay
    from .sensitivity import sensitivity_pass

    record = sensitivity_pass(windows, kept_units, contexts, brackets, b_max, **kwargs)
    # Contrasts can replay sources for every pack, including archives whose
    # derivation census was already merged inside sensitivity_pass. GAMMA's
    # explicit handle need not be the same object as its replay archive.
    censuses = {pack: context.sources_replay.archive.census()
                for pack, context in contexts.items()
                if isinstance(context.sources_replay, _SourcesReplay)}
    return record, censuses, kwargs['gamma_archive'].census()
