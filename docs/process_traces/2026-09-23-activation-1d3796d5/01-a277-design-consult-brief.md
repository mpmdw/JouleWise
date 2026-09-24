ROLE: design consult seat for JouleWise lane A277 (ZERO-CAPTURE-EVIDENCE-WRITER-01). You are a design peer with explicit licence to disagree with the lane text and with the magistrate. Read-only: do not edit, do not run the test suite, do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. The checkout you are in is a detached worktree at main 313efcca. Nothing is armed. Your answer is one input to a two-seat consult; the magistrate synthesizes and decides.

1. THE PROBLEM (verify each claim against the code; flag any that is wrong).
   D-182 (docs/decision_log.md) lets a night that the night gate refused at t0 on machine state, and that captured nothing, be followed by exactly ONE replacement night (a "successor") under a new plan id. Eligibility is `joulewise/arm_retry.py` `zero_capture_successor_allowed(result, receipt, delivery)` (line ~247), wrapped by `successor_arm_allowed` (~287). It demands a `zero_capture_evidence` block inside the receipt's C5 row (`receipt["conditions"][i]["measured"]["zero_capture_evidence"]` with chain_started_absent, reservation_absent, session_id, capture_writer_ran, instrument_validation_empty). NOTHING in production writes that block (grep it), so every live receipt returns `missing_zero_capture_evidence` and D-182 cannot deliver its successor. Also: as far as the magistrate can find, `successor_arm_allowed` has NO production caller at all — confirm or refute, and name what the real arm path of a successor is today (docs/process/NIGHT_HANDBACK.md, the night plan writer `joulewise/night_plan_writer.py`, the `evidence_night` check/arm/install commands in `joulewise/evidence_night.py`, `joulewise/arm_retry.py`).
   PR #393 (A234, merged ea4995d5) added a watchdog-side early release of the agent-free hold after such a refusal; it does NOT use the harvested block. It rebuilds the absence facts from disk: `scripts/magistrate_watchdog.py` `_zero_capture_disk_facts` (~851: no `night/chain.started`, no `*.consumed.json` reservation marker, no capture under RUNS_ROOT/instrument_validation or `night/evidence`, empty/absent `night/evidence_envelopes.jsonl`, symlinks count as present) combined with `arm_retry.terminal_zero_capture_refusal` (~202), which treats a bare C5 row as "neither evidence nor veto".

2. THE TWO OPTIONS the lane names (you may propose a third):
   (A) make the harvest write the `zero_capture_evidence` block into C5 (find where harvest happens and who owns the receipt bytes — is the receipt immutable custody? would writing into it violate evidence immutability?);
   (B) rebase `zero_capture_successor_allowed` eligibility on the on-disk facts, sharing ONE implementation with the watchdog's `_zero_capture_disk_facts` (move it into a joulewise module both import?), so the release and the successor read the same facts.

3. A CONSTRAINT FROM THE NEXT LANE. A270 (TASK_QUEUE.md row A270, D-182 Addendum 2026-09-23 in docs/decision_log.md) will route a chain abort on `non_observer_process_busy` with FEWER than minimum_retained (8) envelopes captured through this SAME one-successor route — i.e. a predecessor that DID capture 1..7 envelopes. Your design must not make A270 require tearing it back out: say how the eligibility function should be shaped so A270 adds a second, narrowly-typed door (captured-but-aborted) without weakening the zero-capture door (any capture/reservation fact on disk still blocks a zero-capture successor).

4. ANSWER THESE, each with file:line evidence you actually read:
   Q1. Which option (A/B/other), and why. Include which is fail-closed under a partial/torn harvest and under a symlinked or missing custody directory.
   Q2. The production call site: where must the eligibility check run so that a successor arm cannot happen without it (name the function and file; if none exists, specify the minimal one to add and who calls it).
   Q3. The regression list (each must fail on 313efcca and pass after, at the production call site): at minimum a live-shaped delivered zero-capture refusal licenses exactly one successor; a bare C5 row alone never licenses; any capture or reservation fact on disk blocks; second successor refused.
   Q4. The WRITE_SCOPE you would give the implementation seat (exact paths).
   Q5. Anything in the lane text or in this brief you believe is wrong.

5. OUTPUT: plain markdown, under 1,500 words, answers first. No code patches.
