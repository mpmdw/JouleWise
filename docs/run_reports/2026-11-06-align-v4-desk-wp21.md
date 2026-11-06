# ALIGN v4 WP21 desk implementation

Implemented the agent-safe portion of WP21: the thermal desk now accepts a
repeatable `--compare-session PILOT.json`, reads portable cross-session anchor,
sentinel, state-sensitivity and frozen-residual inputs, and computes U4–U6 with
the existing council rules. `session_desk_evidence(..., adapter=...)` is the
explicit integration seam for the off-repository `k_sessions.py`; no embedded
PILOT path is followed. Synthetic tests cover pass, fail and inconclusive
outcomes, plus adapter and raw-input computation.

The v3 anchor configuration and pinned measurement core were not changed. Live
Mac measurement/archive work was neither required nor run. Open protocol and
adapter questions are recorded in `docs/align/v4_desk.md`.

Verification: `python3 -m unittest tests.align.test_thermal_desk` passed (21
tests). The broader pilot-session check has a pre-existing generated-kit byte
mismatch (`hybrid_checkpoint_limit`) outside this diff. The canonical suite was
started separately; its terminal outcome is recorded in the final handoff.
