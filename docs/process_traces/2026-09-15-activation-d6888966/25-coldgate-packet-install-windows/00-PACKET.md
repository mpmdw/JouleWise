# Cold-gate packet 25 — INSTALL-WINDOWS-MULTI-01: the fix loop stopped on the standing escalation trigger; structure, bound, cleanup, landing, and two design-bearing side items (assembled mechanically by activation d6888966, 2026-09-15 08:55 PDT)

Convened under rule 11 because the Opus lieutenant's delta auditor answered the same-signature question YES on two defect classes after fix round 1 (exhibit B), which is a MANDATORY cold-gate trigger ("any second fix round on the same defect"), and because two further items are design-bearing and not the lieutenant's or the magistrate's to decide alone: the FIX-5 narrowing of acceptance clause (c) (exhibit C) and the runbook §3 pre-registration constraint (exhibit G F2, exhibit D §8). The integration head is `df86cee6` on `int/2026-09-15-install-windows` (this checkout), with the blocker OPEN; no PR, nothing merged, nothing armed.

## What was found (from the exhibits; the judge verifies)

- Class 1 — missed boundary-check call site: seat A (exhibit F) omitted the listed-span check from every `close`-mode recheck; fix round 1 (exhibit C FIX-1) added the selected span's close to those checks; the delta (exhibit B) shows the FINAL dead-man bootstrap at `scripts/install_night_agent.sh:348` still crosses the span close — four executed fake-launchctl cases end exit 0 with both agents loaded, one crossing two span boundaries.
- Class 2 — incomplete failure cleanup: seat A left rendered plists after a failed bootstrap; fix round 1 (FIX-2) added an EXIT trap; the delta shows `set -e` inside `render()` skips that trap on zsh 5.9 (`/bin/zsh -c 'set -e; trap "print trap-fired" EXIT; f() { false; }; f'` exits 1 silently), leaving an overwritten plist and a leaked backup directory; and TERM/INT/HUP after the first bootstrap now delete BOTH plists while leaving the job LOADED — worse than before, because the installed-plist fence (exhibit E, watchdog) reads those files to see an armed plan.
- The lieutenant's structural hypothesis (exhibit A): the installer is a multi-step, non-atomic machine-state mutation with time-varying preconditions; point checks at call sites do not close the set. Offered restructure: refuse BEFORE the sequence unless `now + bootstrap budget < min(selected span close, install_close_epoch)`; on any failure, ONE idempotent teardown that bootouts by label and then removes files. Not implemented; it introduces a new constant and changes the refusal contract, and exhibit E rejected inventing ceiling constants (`MAX_PLAN_SPAN_S`) in this lane.
- Replay at `df86cee6`: 6094 tests, 0 failures (exhibit A's companion lt-91, on main). The blocker has no failing suite test because it is reachable only when the clock advances during the bootstrap sequence.
- FIX-5 (exhibit C): acceptance clause (c) "t0 may be any clock time" now reads "any whole minute that occurs exactly once in local time" (refusals `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`), ruled by the lieutenant fail-closed as the physical granularity of `StartCalendarInterval`; flagged for overrule.
- Runbook §3 (byte-identical, SHA-256 `71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`) keeps the FAIL route's "three windows on distinct calendar days" (exhibit I line 143) while D-181 (exhibit H) says windows run whenever the machine is quiet, several per day.

## Q1 — structure (rule one option, or write a better one)

(a) One more point check at `install_night_agent.sh:348` (final bootstrap) with a defect-shaped regression, then land. (b) The restructure in exhibit A: a pre-sequence refusal on the whole bootstrap budget plus one idempotent teardown (bootout by label, then remove files), replacing per-call-site checks and per-branch rollback. (c) Another shape you specify. Rule which, with the reason, and say whether it changes the installer's refusal contract as adjudicated in exhibit E (a contract change) or is a mechanism choice inside it.

## Q2 — the bound

If Q1 needs a pre-sequence budget: does exhibit E's rejection of invented ceiling constants extend to `MAX_INSTALL_DURATION_S`? If yes, name what carries the bound instead (an existing constant such as the grace or courier allowance already in `scripts/run_night.py`, a measured duration recorded at install time, or a derived margin) and its exact source; if no, say why this constant is different in kind and what pins its value.

## Q3 — cleanup shape

Is "bootout by label, then remove files, in one idempotent routine with a single entry" a mechanism choice, or does it need adjudication because the installed-plist fence depends on those files? Given the zsh 5.9 `set -e`/EXIT-trap finding, what cleanup shape is REQUIRED (state it so a seat can implement it without re-deciding), and what regression proves a signalled or failed install can never end with a loaded job and no plist?

## Q4 — landing (rule one option)

(i) The blocker must be closed (per Q1) before the lane lands. (ii) The lane may land now with a documented, test-pinned refusal of any span list other than the shipped whole-day default `(("00:00","24:00"),)` until the installer is restructured — the blocker is latent under that default. (iii) Other. The lieutenant explicitly does not recommend (ii). Rule which, and say whether (ii) would be a reinterpretation of D-181 clause 1 (exhibit H) that only Ed may make.

## Q5 — FIX-5 narrowing of acceptance clause (c)

AFFIRM (the narrowing is the physical granularity of `StartCalendarInterval` and fail-closed under D-161), AMEND (exact replacement: e.g. resolve the repeated DST minute deterministically to the first or second occurrence, with the reason), or REFUSE (the narrowing contradicts D-181 clause 1 "any clock time" and needs Ed). Say which and whether the kernel acceptance text for INSTALL-WINDOWS-MULTI-01 must change (give the text for the magistrate to record).

## Q6 — runbook §3 FAIL-route distinct-calendar-days constraint vs D-181

(i) No conflict: same-day installation is a machinery capability; the three FAIL-route registration windows keep the pre-registered distinct-day sampling design, and the runbook must SAY so at the install-span text (give the sentence). (ii) Conflict: the pre-registration constraint must be amended, which only Ed may do, before any FAIL-route night is scheduled on a same-day span. (iii) Other. Rule which; cite exhibit I line 143 and exhibit H.

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry or skill doctrine (name text changes as text for the magistrate to record). Cite exhibits by name; code by file:line only if you read it in this checkout (`df86cee6`). For Q1 and Q3, execute at least one probe: reproduce one of exhibit B's fake-launchctl crossing cases from `tests/test_install_night_agent.py` (single module or single test; never a real `launchctl bootstrap`; never touch `~/Library/LaunchAgents` or `/Users/edr/night-custody`). Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE.local.md or narrative state docs. Under 14 KB. Ending before the ruling file exists is a protocol failure.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
9aac4bcfb08ecc04a96292cae9796d96821247b7268afe8b0bb409ab6ff677ff  exhibit-A-consult-request-lt05.md
1cdcb1cdd46fc5b6bb2679636c8456f3c2e81a54c64a4e5074cbd9d65da420ae  exhibit-B-delta-re-audit-lt04.md
084d5f7a1c46e88efeac7e6596511483f3459920d91685ef9ef62915429d32ef  exhibit-C-fix-contract-lt03.md
3146a3250df050e9ece997573a847fd2a8572c27a9cf0a22db1f402d4bdf48fc  exhibit-D-refuters-lt02.md
cb101bd2a0d32c385848f118b8401fb73dbabb1b20ac29b18d38b2af16e5d8a4  exhibit-E-design-adjudication-06.md
a05726f84376d2aaa1128961d4a632b9fe2638dd4ca8edcdae3b23d90b414f00  exhibit-F-seat-A-report.md
34f48ef08908e50124845fc43390efe1646c98011ee75318a7b37af9eddca138  exhibit-G-seat-D-report.md
0a360d2134f09216c8010e781f9c3df59949c338bd9622b11937cc44b2a1101a  exhibit-H-D180-D181-decision-log-11739-11900.md
c7014ee4e5af060e8495dddca48c73404c0e78b061d023c072708b1bbc0bc0e9  exhibit-I-preregistration-135-155.md
```
