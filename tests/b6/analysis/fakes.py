"""Synthetic block-6 inputs and a fake of the L9 adapter.

Every number here is synthetic, derived from a hash of the session id, and
describes no measurement.  The fake has the signatures of
``joulewise.b6.analysis.adapter.L9Adapter`` and is defined at module level so
that a process pool can pickle it.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

from joulewise.b6.analysis.adapter import AdapterRefusal, SessionAnalysis

MODELS = {"alpha": "qwen3-1p7b", "beta": "qwen3-8b"}
PHASES = ("decode", "prefill-p2048")
FORMS = ("absolute", "comparative")
CONTRASTS = ("decode", "prefill-p2048")

# Block 6 as closed (RUN_STATE item 59): nine collected sessions, all counting
# (A r1/r3/r4, B r1/r2/r3, G r1/r2/r3).  ALPHA's round-2 attempt was a smoke
# hold, not a collected session, so it has no attempt line here.
CLOSED_BLOCK6 = (
    ("r1-alpha", "alpha", 1, "counting"), ("r1-beta", "beta", 1, "counting"), ("r1-gamma", "gamma", 1, "counting"),
    ("r2-beta", "beta", 2, "counting"), ("r2-gamma", "gamma", 2, "counting"),
    ("r3-gamma", "gamma", 3, "counting"), ("r3-alpha", "alpha", 3, "counting"), ("r3-beta", "beta", 3, "counting"),
    ("r4-alpha", "alpha", 4, "counting"),
)
# A synthetic collected ALPHA session that did not count (a physics stop), to
# exercise §11.4.  It describes no real session.
NONCOUNTING_ALPHA = ("r5-alpha", "alpha", 5, "physics_stopped")
WITH_NONCOUNTING = CLOSED_BLOCK6 + (NONCOUNTING_ALPHA,)


def unit(session_id: str, key: str, low: float, high: float) -> float:
    """A synthetic value in [low, high), fixed by the session and key."""
    digest = hashlib.sha256(f"{session_id}|{key}".encode()).digest()
    return low + (high - low) * int.from_bytes(digest[:8], "big") / 2 ** 64


def attempt_line(session_id, pack, round_number, status, *, codes=(), structure_ok=True, physics_stop=None):
    counting = status == "counting"
    line = {"session_id": session_id, "packs": [pack], "chain_rc": 0, "harvest_rc": 0, "verdict": "COLLECTED",
            "physics_stop": physics_stop if physics_stop is not None else ("chain.stop:sampler_down" if status == "physics_stopped" else None),
            "window_flags": [], "pack_flags": {pack: list(codes)}, "counts": {}, "structure_ok": structure_ok,
            "structure_defects": [], "minutes": {}, "compressed": True,
            "acceptance_verdict": "ACCEPT" if counting else "EXCLUDE", "counting": counting,
            "excluding_reasons": [] if counting else list(codes)}
    return {"session_id": session_id, "round": round_number, "packs": [pack], "t0": 1760000000.0 + round_number,
            "outcomes": {pack: {"status": status, "cause": None}}, "structure_ok": structure_ok,
            "registration_commit_times": {pack: 1759900000.0}, "line": line}


def write_loop_root(root: Path, sessions=CLOSED_BLOCK6, *, closed=True, overrides=None, reharvested=None) -> Path:
    """A loop root with attempts.jsonl and state.json, as joulewise.b6.loop writes them."""
    overrides = overrides or {}
    root.mkdir(parents=True, exist_ok=True)
    with (root / "attempts.jsonl").open("w") as stream:
        for session_id, pack, round_number, status in sessions:
            stream.write(json.dumps(attempt_line(session_id, pack, round_number, status,
                                                 **overrides.get(session_id, {}))) + "\n")
    state = {"state": "DONE" if closed else "NEXT", "round": 4, "packs": {}}
    if reharvested:
        state["reharvested"] = reharvested
    (root / "state.json").write_text(json.dumps(state))
    return root


def write_r2_gamma_exclusions(root: Path) -> Path:
    """A synthetic r2-gamma harvest whose exclusions say claim_usable: false
    from block 5's retired neg8.midpoint_lost_primary (RUN_STATE item 53)."""
    path = root / "sessions/r2-gamma/archive/derived/exclusions.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"claim_usable": False, "window_exclusions": ["neg8.midpoint_lost_primary"]}))
    return path


class FakeL9:
    """Fake L9: one session in, that session's synthetic results out.

    ``refuse`` maps a session id to a refusal token; ``contrasts`` maps a GAMMA
    session id (or "block5") to {contrast: (outcome, dbar)}; ``kept`` maps a
    session id to a kept-unit count used in every stratum; ``drift`` maps a
    session id to its drift-screen word.
    """

    def __init__(self, *, refuse=None, contrasts=None, kept=None, drift=None, noisy=True, whole_machine_on_gamma=False,
                 outcome_class=()):
        self.refuse = dict(refuse or {})
        self.outcome_class = frozenset(outcome_class)
        self.contrasts = dict(contrasts or {})
        self.kept = dict(kept or {})
        self.drift = dict(drift or {})
        self.noisy = noisy
        self.whole_machine_on_gamma = whole_machine_on_gamma

    def describe(self):
        return {"adapter": "synthetic_fake"}

    def _speak(self, session_id):
        # Synthetic numbers on every stream: the driver must keep them out of
        # public bytes (stdout, stderr and the record).
        if self.noisy:
            print(f"energy {unit(session_id, 'noise', 1, 2):.6f} J")
            print(f"floor {unit(session_id, 'noise2', 1, 2):.6f} J direction_supported", file=sys.stderr)
            os.write(1, b"fd-level 12.5 J\n")
            os.write(2, b"fd-level 0.25 J replicated\n")

    def _write(self, custody: Path, name: str, value) -> str:
        raw = json.dumps(value, sort_keys=True).encode()
        (custody / name).write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def _common(self, session_id, pack, custody):
        if session_id in self.refuse:
            raise AdapterRefusal(self.refuse[session_id])
        self._speak(session_id)
        n = self.kept.get(session_id, 10)
        return n, self.drift.get(session_id, "passed")

    def _floor(self, session_id, pack, custody):
        n, drift = self._common(session_id, pack, custody)
        model = MODELS[pack]
        quantities = {}
        for phase in PHASES:
            quantities[f"reported/{model}/{phase}/mean_j"] = unit(session_id, f"m{phase}", 20.0, 30.0)
            quantities[f"reported/{model}/{phase}/attribution_floor_j"] = unit(session_id, f"a{phase}", 1.0, 3.0)
            quantities[f"whole_machine/{model}/{phase}/mean_j"] = unit(session_id, f"w{phase}", 40.0, 60.0)
            for form in FORMS:
                quantities[f"floor/{model}/{phase}/{form}/operative_j"] = unit(session_id, f"f{phase}{form}", 0.3, 1.5)
                quantities[f"dominance/{model}/{phase}/{form}/R"] = unit(session_id, f"r{phase}{form}", 1.0, 4.0)
        quantities[f"floor/{model}/prefill-p42/absolute/operative_j"] = None   # expected not extractable
        kept = {f"{model}/{phase}": {"repeat": n, "null_quad": n} for phase in PHASES}
        digest = self._write(custody, "floor-result.json", quantities)
        return SessionAnalysis(session_id, pack, "ok", steps=(("1", "ok"), ("2", "ok"), ("3", "ok"), ("3b", "ok"),
                               ("4", "ok"), ("10", "ok"), ("11", "ok")), kept_units=kept, b_op_defined=True,
                               drift_screen=drift, outputs={"floor_result": digest}, quantities=quantities)

    def _gamma_values(self, session_id):
        values = self.contrasts.get(session_id, {})
        contrasts = {}
        for contrast in CONTRASTS:
            outcome, dbar = values.get(contrast, ("direction_supported", unit(session_id, f"d{contrast}", 2.0, 4.0)))
            contrasts[contrast] = {"outcome": outcome, "dbar": dbar}
        quantities = {f"contrast/{c}/energy_ratio": unit(session_id, f"e{c}", 3.0, 5.0) for c in CONTRASTS}
        if self.whole_machine_on_gamma:
            quantities["whole_machine/qwen3-8b/decode/mean_j"] = 1.0
        return contrasts, quantities

    def _status(self, result):
        return replace(result, status="outcome_class") if result.session_id in self.outcome_class else result

    def analyse_floor_session(self, request, custody):
        return self._status(self._floor(request.session_id, request.pack, Path(custody)))

    def analyse_gamma_session(self, request, alpha, beta, custody):
        n, drift = self._common(request.session_id, request.pack, custody)
        self._write(Path(custody), "received.json", {"alpha": alpha.session_id, "beta": beta.session_id})
        contrasts, quantities = self._gamma_values(request.session_id)
        kept = {f"contrast/{c}": {"contrast_quad": n} for c in CONTRASTS}
        digest = self._write(Path(custody), "claim-result.json", {"contrasts": contrasts, "quantities": quantities})
        return self._status(SessionAnalysis(request.session_id, request.pack, "ok",
                               steps=(("1", "ok"), ("5", "ok"), ("8", "ok"), ("6", "ok"), ("9", "ok"), ("9b", "ok"), ("11", "ok")),
                               kept_units=kept, b_op_defined=True, drift_screen=drift,
                               outputs={"claim_result": digest}, quantities=quantities, contrasts=contrasts))

    def block5_session(self, pack, custody):
        if "block5" in self.refuse:
            raise AdapterRefusal(self.refuse["block5"])
        if pack == "gamma":
            contrasts, quantities = self._gamma_values("block5")
            return SessionAnalysis("block5", pack, "ok", b_op_defined=True, drift_screen="passed",
                                   quantities=quantities, contrasts=contrasts)
        result = self._floor("block5-" + pack, pack, Path(custody))
        return SessionAnalysis("block5", pack, "ok", steps=result.steps, kept_units=result.kept_units,
                               b_op_defined=True, drift_screen="passed", outputs=result.outputs,
                               quantities=result.quantities)


def tree_digest(directory: Path) -> dict[str, str]:
    """Every file under a directory, by relative path, with its SHA-256."""
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(directory).rglob("*")) if path.is_file()}
