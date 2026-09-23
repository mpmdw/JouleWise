# A234+A212 at 4c76ab69 — Opus 5.5 contract-lens refuter report (verbatim hand-back)

Verdict: no blocker found. Three SHOULD-FIX, three NIT.

S1. plan_is_armed diverges from base for chain-started refusals (scripts/magistrate_watchdog.py ~857-861): the new branch returns now <= plan_completion_epoch whenever chain.started, chain.exited and a REFUSED result exist. Executed P1: delivered chain-started refusal at t0+60 s, base armed False, head True (more conservative). Executed P2 (regression): undelivered chain-started refusal at completion+60 s, base armed True (dead-man bound + courier-lock freshness), head False while plan_span_active is True — the plan drops out of plan_conflicts and fenced_checkouts before delivery. Fix: return now <= completion OR the base tail.

S2. The release latch is keyed by plan id + custody root only, not the refusal instance (_release_key ~808, decide ~1513-1525). Executed P3: state already holds the key; a new delivered refusal in the same plan id and root, census showing courier + driver alive -> decide returned LAUNCHING with census_calls = 0. Unlikely (installer refuses terminal roots; D-182 never re-arms) but not enforced by the latch. Fix: bind the key to result.json's ended_epoch_s or sha256.

S3. Doc paragraphs (NIGHT_HANDBACK.md:57, runbook:1856) fail the first-use test: "on machine state" (the five codes) undefined; "tick" used before its gloss at line 78; "owner veto" and "notice" undefined at use; "while the plan's scheduled window remains open" is t0-8 min .. t0 + window_max_s + COURIER_DEADLINE_S in code, and the courier deadline is unstated.

Verified true: census matches the courier (claude -p, run_night.py:1441) and the driver (--courier-bin resolves under /Users/edr/.local/share/claude/versions/, executed); unreadable state fails closed; release is one-way; runbook 25 -> eight minutes matches PLAN_LEAD_S = 8*60.

N1. The chain-field guard in terminal_zero_capture_refusal (arm_retry.py ~216) is untested: mutant `if False` -> 139 run, 0 failures (gap pre-exists on base).
N2. With a pending release and an owned session, decide now returns HOLD_CENSUS(adopt) where base returned STANDDOWN_{phase}(adopt); the resident supervisor still stands the session down via relevant_standdown_plan, so only the label changes.
N3. snapshot.errors now returns before fenced_checkouts is refreshed (~1498); stale value on HOLD_UNSAFE; no launch follows.

Spec map: A234 clauses each mapped to a test; A212(a) implemented stricter (release at first empty census after courier.sent, not at the refusal record's time) — a deviation that follows the cold review's finding 1 and should be acknowledged; (b) five codes incl. night_refused_bind_expired per D-182; (c) present. Consumers: decide passes state; resident supervisor step passes none and falls back to reading state.json (fails closed if unreadable); evidence_night.retained_roots relies on the sibling lookup (executed P4: unreadable state -> span True, fails closed; a watchdog under MAGISTRATE_WATCHDOG_CUSTODY_ROOT override would be ignored, fail-closed). arm_retry successor route now requires every receipt row's measured to be a dict; live receipts satisfy it. Tests executed: 139 passed, 222 subtests.
