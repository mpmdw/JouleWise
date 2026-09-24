**Verdict: MERGEABLE. No blockers.** Every defect below errs on the refusing side. I recommend fixing S1 and S4 before merge (both small) and running a delta re-audit on that fix. Named modules on 6d1e004f: 306 tests OK (360 s). My scratch copies are in /tmp/a277-{old,new} (made with git archive). The worktree was not touched.

**(1) Is each D-182 term enforced?**
- **One successor per predecessor.** The claim file is created with exclusive create (`evidence_night.py:879-906`). `arm_retry.py:279-284` refuses when a claim exists for a different candidate, or when the predecessor was itself a successor. `evidence_night.py:846` refuses when more than one released predecessor is found.
- **Zero-capture facts.** Read from disk in `zero_capture_facts.py:99-165` and gated in `arm_retry.py:257-262`.
- **Courier delivered.** `facts.courier_sent` plus the message id from `_courier_message_id` (`evidence_night.py:796-808`).
- **At least 60 s after the terminal write.** `arm_retry.py:285-286`. It is evaluated again at publication (`:1637`).
- **Fresh plan id, never re-arm the refused plan.** `arm_retry.py:277-278` checks both the id and the digest.
- **Install close and fresh notice.** Enforced by existing rows (`:1213-1215`, `:1567`, `:1577`).
- **Every observed NO stops.** This check is outside this change. It is the existing veto record at `:1568` and `observe_veto` at `:1633`. The code relies on it correctly.

**(2) Fail-closed audit, with executed probes**
- Missing custody root, symlinked custody root, torn result or receipt, unreadable ledger, symlinked claim or claim directory: all refuse. Symlinks are rejected by `safe_path` (`:72-76`).
- **S3 (should-fix).** The missing-custody refusal only lasts until the next watchdog tick. The refusal fires on a stale release key (`:824-830`). The watchdog removes keys for plans it no longer finds on disk (`magistrate_watchdog.py:1540-1541`). After that the candidate is an ordinary arm with no successor bound. Executed: before the key is removed, `('fail', 'released predecessor custody is missing')`; after, `('pass', None)`. This means `test_a277_missing_custody_root_refused` and `test_a277_symlinked_custody_root_refused` pin the temporary state, not the steady state. The trigger is an operator action (D-161), so this is not a blocker. But the contract sentence "Missing or symlinked custody … refuses the successor" says more than the code does.
- **Claim written, then publication fails.** A retry with the same id and digest proceeds (covered by a test). A different candidate is refused only until the predecessor's completion time. Executed: `CLAIMED_OTHER_AT_COMPLETION` fails (`successor_already_used`); one second later, `CLAIMED_OTHER_AFTER` passes. So it is not blocked forever, and refusing is the right side to fail on. Nit: the handback should say that re-preparing a candidate (new bytes) after a failed publication gives up the successor for the rest of the span.
- **S4 (should-fix).** Two ways to block every evidence-night check with no time limit:
  - The claim is written in place with `open("x")`, not written to a temp file and then linked. A crash mid-write leaves a torn claim, and every future check refuses with "malformed successor claim". Executed: still failing ten days later.
  - Any file in `successor-claims/` that does not end in `.json` also refuses, e.g. a Finder `.DS_Store` (executed).
  - Suggested cure: write a temp file and `os.link` it into place. Ignore dot-files, which is safe because claim names match `[A-Za-z0-9]…`.
- **Clock going backwards.** The 60 s check fails because now − ended < 60. `_delivered_zero_capture_refusal` requires ended ≤ now. The completion-time comparisons only get longer. All of these refuse.

**(3) Does the watchdog's early release change versus 313efcca? Yes, and the brief (C2) and the contract doc (`night_quiet_admission.md:308`) say it does not.** I ran `_delivered_zero_capture_refusal` on the same fixtures in both trees:

| Fixture | 313efcca | 6d1e004f |
|---|---|---|
| Symlink `night/latest` in custody (not `*.consumed.json`) | True | False |
| Calibration chain exports `CALIBRATION_LEDGER`, ledger has a row with the night plan id | True | False |
| The shared ledger has a torn last line from another night | True | False |

`decide()` on the symlink fixture: old = LAUNCHING with the key released; new = FENCED with `[]`.

Nothing becomes more permissive. Every check in the old predicate is kept or made stricter: it switched from `Storage.exists` to `lstat`, which behaves the same, and the envelope and evidence logic is the same. No production code creates symlinks in custody (grep), so the first row is theoretical. The torn-ledger row is realistic. It brings back the ~3 h span loss that PR #393 cured, for every derivation night, because generated wrappers always export `CALIBRATION_LEDGER`.

**(4) Successor detection at the boundaries.**
- Exactly at `plan_completion_epoch`: treated as a successor (executed: `AT_COMPLETION ('pass','predecessor')`). This matches `plan_span_active`, which uses ≤.
- After completion: an ordinary arm, and old claims are ignored (`AFTER_COMPLETION ('pass', None)`). I read this as D-182's intent. The licence shortens a refused span. Once that span is over, the refused plan imposes nothing, and D-181 forbids artificial spacing.
- Nit: `predecessor_is_successor` looks at every claim ever written, not just current ones. So a successor can never license another plan, even after the original span has ended. That is the addendum's "a second abort … licenses nothing further" applied to zero-capture refusals too. The magistrate adopted this reading, but the base text of D-182 is silent on it. Worth one line for the cold gate.
- Nit: the released-key comparison `Path(prior_root).parent == root` (`:827`) compares unresolved strings, so a differently spelled custody path silently skips the check.

**(5) The ledger-session fact (C6). S1 (should-fix).**
- It reads the right ledger file: the chain's own `CALIBRATION_LEDGER` value. An unreadable ledger or a blank or malformed row makes the scan incomplete, so it refuses. A missing ledger file counts as zero sessions.
- **But it matches on the wrong id.** `_ledger_sessions(ledger, plan.plan_id)` (`zero_capture_facts.py:140`) looks for the night plan id. Real ledger rows carry the frozen calibration plan's id:
  - `gen_derivation_night.py:280` sets `PLAN_ID=spec.frozen_plan_id`;
  - `calibration_derivation_only.zsh:197` passes `--plan-id "$PLAN_ID"`;
  - `calibration_ledger.py:4753` writes it as the row's `plan_id`.
- So in production the count is always zero. The fact provides no safety, but it adds the release risk from (3). Both tests (`test_zero_capture_facts.py:54-62`, `test_evidence_night.py:2731-2734`) write the night plan id, which production never does.
- This is not a safety hole. By the seat's own C6 finding, the driver creates `chain.started` before any ledger session (`run_night.py:536`, `:3170`), and `chain.started` already refuses.
- Cure: either remove the ledger read and cite that ordering, or match on the chain's `SESSION_ID` value.

**(6) Docs.**
- The policy block is byte-identical in `NIGHT_HANDBACK.md`, `derivation_night_runbook.md` and `render_policy()` (all three sha256 `1e5fa40b…`).
- Where the contract words do not match the code:
  - "calibration-ledger sessions for the plan" (S1);
  - "Missing or symlinked custody … refuses" (S3);
  - "The claim remains" does not say that the claim stops binding at the predecessor's completion time;
  - "does not change the watchdog's one-way release semantics" is true of the latch, but the release predicate itself changed (3).
- Writing-standard nit: "latched" and "bare C5 receipt row" are used without a gloss at first use (`night_quiet_admission.md:305`).

**(7) Other.**
- Nit: a rehearsal publication (fake launchctl) also creates the claim (`:1645` is not gated on `fake`). With the default `roots_under=/Users/edr`, a rehearsal of a candidate with different bytes would use up the real successor.
- Nit: `_courier_message_id` accepts only JSON or key=value. The courier is an LLM whose `courier.sent` format is not fixed (`run_night.py:1431`; the format-pin lane was registered 09-18). An unexpected format refuses rather than licenses. The lane is only useful in production once that format is pinned.

**Severity summary**
- Blockers: none.
- Should-fix:
  - S1: the ledger fact matches the wrong id, and it adds a way to block release;
  - S2: the release-predicate change needs to be either accepted and recorded as a deviation, or reverted; it goes together with S1;
  - S3: missing-custody refusal lasts one tick; fix the doc and the test wording, or register a follow-up;
  - S4: a torn claim or stray file blocks all checks with no time limit.
- Nits: the successor-can't-license-again reading, the path comparison, the rehearsal claim, the courier format, the doc glosses.