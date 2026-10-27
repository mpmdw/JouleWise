"""The one place the block-6 driver calls lane L9 (block 5's analysis programs).

Registration §9 and §13: block 6 applies block 5's registered steps (B5-PLAN
§3.1 steps 1 to 11) unchanged, one session at a time.  The driver never
re-implements them; it asks an :class:`L9Adapter` for one session's results.

Two adapters satisfy the protocol:

* :class:`L9ProgramAdapter`, the production adapter.  It targets lane L9 at
  ``L9_TARGET_COMMIT`` (``lane/2026-10-27-l9-2``).  L9 is not merged into the
  block-6 code line yet (seat B6-AN-1, lead ruling of 2026-10-27), so each
  method imports L9 lazily and refuses with a structure token when the seam it
  needs is absent.  ``L9_TARGETS`` records the exact L9 functions each method
  maps to; the integration that lands L9 fills them in.
* the synthetic fake in ``tests/b6/analysis/fakes.py``, with the same
  signatures, used to test everything the driver owns.

Everything a :class:`SessionAnalysis` carries under ``quantities`` and
``contrasts`` is restricted (§12.1).  The other fields are structure.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

L9_TARGET_BRANCH = "lane/2026-10-27-l9-2"
L9_TARGET_COMMIT = "8ad47455ce55203949ea77a3ee330432d5a48101"

# What each adapter method runs at L9_TARGET_COMMIT, by L9's own names
# (joulewise/b5_analysis/dry_run.py step functions over one RunState).
L9_TARGETS = {
    "analyse_floor_session": (
        "dry_run.step_1 (cli validate-bundle --strict per kept bundle)",
        "dry_run.step_2 (cli reduce into restricted custody)",
        "dry_run.step_3 / RunState.prepare_tripwires (kept_units.load_kept_units)",
        "dry_run.step_3b / RunState.prepare_brackets",
        "dry_run.step_4 (scripts.extract_detection_floors.main --pack <pack>, steps.classify_step4_exit)",
        "dry_run.step_10 (scripts.issue_reported_energy.main --pack <pack>, require_step10_admission)",
        "dry_run.step_11 for the session (sensitivity, produce_b5_disclosures, build_results_fill_input)",
    ),
    "analyse_gamma_session": (
        "dry_run.step_1, step_2, step_3, step_3b for the GAMMA window",
        "dry_run.step_5 (emit_floor_mint_pinset, mint_floor_artifact_generalized) from the paired floor sessions' step-4 reports",
        "dry_run.step_8 (scripts.finalize_analysis_manifest.main)",
        "dry_run.step_6 (scripts.run_d165_closeout_from_custody.main)",
        "dry_run.step_9 (cli analyze-claims) and step_9b (_claim_open)",
        "dry_run.step_11 for the session",
    ),
    "block5_session": (
        "the block-5 release record and its restricted outputs (dry_run.run mode release)",
    ),
}

STATUSES = ("ok", "tooling_refusal", "outcome_class", "not_run", "deferred")
# An outcome-class stop is a registered result (B5-PLAN §3.1 "Refusals"), so
# its session's results feed the later lines like a completed one.
COMPLETED = ("ok", "outcome_class")
# A GAMMA unit whose pairing needs block 5's floor waits for the cross-block
# phase (design §5 rule 4); in the per-session phase it is deferred, not refused.
DEFERRED = "deferred"
DRIFT_WORDS = ("passed", "failed", "undefined")


class AdapterRefusal(RuntimeError):
    """A tooling refusal with a structure token."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SessionRequest:
    session_id: str
    pack: str
    round: int


@dataclass(frozen=True)
class SessionAnalysis:
    """One session's results.

    Structure: ``status``, ``code``, ``steps``, ``kept_units``,
    ``b_op_defined``, ``drift_screen``, ``outputs``.  Restricted:
    ``quantities`` (each printed quantity of §9 by a stable key, None when not
    estimable) and ``contrasts`` (per contrast id: ``outcome`` word and
    ``dbar``), with ``reasons`` naming why a quantity is None (for example
``not_estimable``).  For a tooling refusal, ``code`` is the refusal token; an
    outcome-class stop keeps its token restricted (``code`` None).
    """
    session_id: str
    pack: str
    status: str
    code: str | None = None
    steps: tuple = ()                      # ((step id, status word), ...)
    kept_units: Mapping = field(default_factory=dict)   # cell id -> stratum -> kept unit count
    b_op_defined: bool = False
    drift_screen: str = "undefined"
    outputs: Mapping = field(default_factory=dict)      # role -> sha256 of an L9 restricted output
    quantities: Mapping = field(default_factory=dict)   # RESTRICTED
    contrasts: Mapping = field(default_factory=dict)    # RESTRICTED
    reasons: Mapping = field(default_factory=dict)      # RESTRICTED: quantity key -> why it is None
    # RESTRICTED: run phase energies, "<run_id>/<decode|prefill|request>" -> J
    # (the comparison contract's run keys).
    run_energies: Mapping = field(default_factory=dict)
    # Structure: the binding's counting after the desk exclusion (design §4.6),
    # None when the binding does not report it.
    analysis_counting: bool | None = None

    def __post_init__(self):
        if self.status not in STATUSES or self.drift_screen not in DRIFT_WORDS:
            raise AdapterRefusal("session_analysis_malformed")


class L9Adapter(Protocol):
    def describe(self) -> dict: ...

    def analyse_floor_session(self, request: SessionRequest, custody: Path) -> SessionAnalysis: ...

    def analyse_gamma_session(self, request: SessionRequest, alpha: SessionAnalysis, beta: SessionAnalysis,
                              custody: Path) -> SessionAnalysis: ...

    def block5_session(self, pack: str, custody: Path) -> SessionAnalysis: ...


class L9ProgramAdapter:
    """Production adapter over L9's programs (see module docstring)."""

    def __init__(self, session_index: Path | None = None, block5_custody: Path | None = None):
        # The block-6 session index (joulewise.b6.analysis.session_index):
        # per session its archive root, claim-runs root and harvest record
        # digest; block 5's window index cannot name block-6 sessions.
        self.session_index = session_index
        self.block5_custody = block5_custody

    def describe(self) -> dict:
        return {"adapter": "l9_programs", "l9_branch": L9_TARGET_BRANCH, "l9_commit": L9_TARGET_COMMIT}

    def _l9(self):
        try:
            return importlib.import_module("joulewise.b5_analysis.dry_run")
        except ImportError:
            raise AdapterRefusal("l9_absent_from_checkout") from None

    def _seam(self, name: str):
        module = self._l9()
        # L9 at L9_TARGET_COMMIT exposes only the whole-block run(mode, index,
        # custody) over one block-5 window per pack.  A per-session seam is
        # named here so the integration can supply it without touching the
        # driver; until it exists the adapter refuses rather than reach into
        # RunState internals.
        function = getattr(module, name, None)
        if function is None:
            raise AdapterRefusal("l9_session_seam_absent")
        if self.session_index is None:
            raise AdapterRefusal("session_index_absent")
        from joulewise.b6.analysis.session_index import IndexRefusal, load_session_index
        try:
            load_session_index(self.session_index)
        except IndexRefusal as exc:
            raise AdapterRefusal(exc.code) from None
        return function

    def analyse_floor_session(self, request, custody):
        return self._seam("run_floor_session")(request, custody, index=self.session_index)

    def analyse_gamma_session(self, request, alpha, beta, custody):
        return self._seam("run_gamma_session")(request, alpha, beta, custody, index=self.session_index)

    def block5_session(self, pack, custody):
        if self.block5_custody is None:
            raise AdapterRefusal("block5_release_record_absent")
        return self._seam("released_block5_session")(pack, self.block5_custody)
