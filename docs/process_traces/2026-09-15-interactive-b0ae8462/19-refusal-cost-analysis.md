# 19 — Why a t0 refusal costs ~3 hours, and the cure (magistrate b0ae8462, 2026-09-16 00:05 PDT)

Ed: "how have we not made this a lower cost to pay". Mechanism: the driver refuses at t0 in the first second
(night_refused_not_quiet / night_refused_agent_present / hid_idle / boot_clock), writes refusal.json, and the watchdog
still keeps the magistrate away for the FULL plan span (t0 + window_max_s 9000 + COURIER_DEADLINE_S 300) as if the
night had run; only then harvest → §2.5 → fresh plan → arm lead. Nothing scientific requires any of that after a
zero-capture refusal: no data was taken and the gate re-checks at the next t0.

Cure, registered as REFUSAL-FAST-RETRY-01 (P1, after LEAD-MARGIN-01): (a) the span ends at the refusal record when no
capture started (refusal.json present, no receipt / chain.started) and the watchdog relaunches on its next tick;
(b) a zero-capture t0 refusal is a pre-authorized retry in the same shape as A172 (spacing, install-close bound, every
NO stops) — PENDING Ed's ruling; refusals after a capture started stay on the cold-gate path (D-161 evidence fence
untouched); (c) tests for both, plus a counterfactual that a started chain never shortens the span. Effect: refusal
cost ≈ 15–20 min. Implementation starts from the A210 head once its round 4 lands (both edit the watchdog).
