"""R1 phase table shared by the rehearsal driver and night outcome reporting."""

# LEAD-RULINGS-2 R5-2: the designed start states run warmest first (R + 4,
# R + 2, R + 0 C). R6-2 then precools S_slow to the G0 band of R before each
# of them (the ruling 1(c) post-D cooldown before the first, a bounded precool
# before the others), so each preheats from the same defined state.
PLANNING_RUN_ORDER_C = (4.0, 2.0, 0.0)

# A1 R1 item 4 replay pair (a, b) plus council ruling 1(b)'s bank/benign run.
# LEAD-RULINGS-2 R7-1 (round-6 cold MEDIUM-1, exec LOW-6): they run in this
# order, D_bank first, so both runs of the U5 replay pair follow a full gated
# D episode with the same idle (matched predecessors, CHAIR 1(g)); D_bank
# follows the R + 0 C planning turn and is not in the pair.
GATED_D_RUNS = (
    ("D_bank_benign_s1_gated_held", "d-bank-benign-s1"),
    ("D_spam_benign_s1_gated_held_a", "d-spam-benign-s1-a"),
    ("D_spam_benign_s1_gated_held_b", "d-spam-benign-s1-b"),
)

COOLDOWN_AFTER_D_MAX_S = 1500          # ruling 1(c)
# LEAD-RULINGS-2 R6-1 (supersedes R5-1's cool-to-band): the duty bar must
# reproduce W1's D-after-D G0. Every gated D run, and X-G, follows a D turn
# with exactly W1's inter-member schedule: the member's own configured idle
# (sampling.idle_seconds of the W1 kit config it runs), and nothing else; no
# cool-to-band. They consume step-D R_D (RL-59). A G0 timeout makes that
# run INCONCLUSIVE (recorded), never a night refusal. They therefore run after
# the designed start states: the R + 0 C planning turn (a D turn) precedes the
# first (D_bank, R7-1), and X-G follows D_spam b (W1's D -> X transition).
# R6-2: the calibration segments (step-d and each designed start state) start
# from a defined state: a bounded idle-until-soak precool (cap from the runtime
# config, calibration_precool_cap_s) to the G0 band of R. A G0 timeout there is
# retried once after another precool, then recorded INCONCLUSIVE; the kit
# decides downstream (fail closed at the kit, not mid-night).
PRECOOL_SUFFIX = ".precool"

# Ruling 16 legs: (label, AC powermode). LEAD-RULINGS-2 R5-5 (protocol v4
# :243-251): the A-B-A decision precedes step-d, so the D step that fills the
# slots, and every later D measurement, runs under the adopted series mode.
HIGH_POWER_LEGS = (("A1", 0), ("B", 2), ("A2", 0))

STEP_D_NAME = "step_D_prefill_10k_decode_4096"


def phase_plan(include_4bit=False, precool_cap_s=COOLDOWN_AFTER_D_MAX_S):
    """RL-59/RL-72 follow-up. Capture pair and planning precools are admission units.

    ``include_4bit`` remains an API argument for old callers; the follow-up
    cuts that fallback. It requires a separate qualification and ruling.
    """
    phases = [
        ("pre_calibration_bracket", "calibration-pre", None, "light"),
        ("idle_soak", "idle", 1800, "light"),
        ("step_30b", "step-30b", None, "heavy"),
    ]
    phases += [(f"high_power_{label}", f"high-power-aba-{label.lower()}", None, "heavy")
               for label, _ in HIGH_POWER_LEGS]
    phases += [
        ("capture_predecessor_30b", "capture-predecessor-30b", None, "heavy"),
        (STEP_D_NAME, "step-d", None, "heavy"),
        ("cooldown_after_D", "idle-until-soak", COOLDOWN_AFTER_D_MAX_S, "light"),
    ]
    for index, offset in enumerate(PLANNING_RUN_ORDER_C):
        name = f"planning_turn_R_plus_{int(offset)}C"
        if index:
            phases.append((name + PRECOOL_SUFFIX, "idle-until-soak", precool_cap_s, "light"))
        phases.append((name, f"d-planning-turn-r-plus-{int(offset)}c", None, "heavy"))
    phases += [(name, kind, None, "heavy") for name, kind in GATED_D_RUNS]
    phases += [("X_G_contrast", "x-g", None, "heavy"),
               ("post_calibration_bracket", "calibration-post", None, "light")]
    return phases
