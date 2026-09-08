WRITE_SCOPE: ["scripts/magistrate_watchdog.py","scripts/install_magistrate_watchdog.sh","docs/process/MAGISTRATE_WATCHDOG.md","tests/test_magistrate_watchdog.py","tests/test_magistrate_watchdog_cli.py","tests/test_install_magistrate_watchdog.py"]

# Fix-round brief — WATCHDOG-CENSUS-01 / RESUME-DAEMON-01 landing, Opus contract-refuter findings (gpt-6-astra)

HEAD of this worktree is commit 898e5305 (the seat landing on branch feat/2026-09-08-watchdog-census-daemon).
An Astra execution refuter found nothing; an Opus contract refuter returned LAND-WITH-FIXES. Cure C1-C4 (required)
and C5-C7 (optional, only if cheap and safe). Each cure gets a defect-shaped regression whose docstring names the
counterfactual input; the four required regressions must FAIL on HEAD before your edit (prove it: run each new
test against a `git stash`-free copy is impossible here, so instead write the test first, run it, record the
failure tail, then fix).

## Findings (verbatim from the refuter; file:line at HEAD)

C1 should-fix — `scripts/magistrate_watchdog.py:991-996` vs `docs/process/MAGISTRATE_WATCHDOG.md:192`: a recorded
pair seen with a CHANGED start token at TERM (correctly `reused_skipped`) and absent at KILL is relabelled
`already_gone`, contradicting the doc's own definition ("`already_gone` means absent before any attempted signal,
while a changed token is `reused_skipped`"). Receipt understates PID reuse. Probe:
`reap_handoff({"interactive_pid":100,"owned":[{"pid":100,"start_time":"old"}]}, table_with(ProcessInfo(100,1,"newtoken",...)), lambda: None, sleep=drop100)`
→ `outcomes={'100':'already_gone'}`, `before_signal.term={'100':'newtoken'}`. Cure: label `reused_skipped` at KILL too.

C2 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:157,181`: the documented step-4 reconciliation can NEVER clear
a corrupt/unparseable `magistrate.lock`: `read_lock` returns `{}` (`:838-840`), `handoff_census` maps `{}` →
`handoff_lock_invalid` (`:936-938`), the block raises `handoff_lock_not_clear`; the installer's exclusive seed
refuses while any lock file exists, so a corrupt lock blocks install with no documented recovery. Cure: let step 4
clear a `{}`/corrupt lock when no owned/twin process is live (fail-closed if any is), with a regression, or document
an explicit alternative command.

C3 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:190`: "Resolve that process explicitly before clearing the
lock" is a gesture, not a verbatim command, and this is exactly the state a failed handoff lands in (late twin ⇒
receipt `fail` ⇒ next tick `HOLD_UNSAFE: dead_lock_resumed_twin` ⇒ step 4 refuses while the twin lives). Cure: the
exact operator commands (inventory the twin with `handoff-inventory`, stop it by pid with its start token
re-validated, re-check), fail-closed on token mismatch.

C4 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:157` vs `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:19`: the
reconciliation block says only "from an observer Terminal"; it never states INTERACTIVE MAGISTRATE / OPERATOR
ONLY and never cross-references the relaunch prompt's bar on headless sessions touching locks. Cure: say who, and
cite the relaunch prompt line (do not edit that file; it is being amended separately as D-175).

C5 nit — `scripts/install_magistrate_watchdog.sh:90-110` re-implements `handoff_process_role`'s token logic inline
instead of importing it; only the regex literal is pinned. Optional: a shared-corpus agreement test.
C6 nit — `tests/test_magistrate_watchdog.py:1727-1733`: shadow `reap_handoff` returns a self-declared pass; bounded.
C7 nit — `docs/process/MAGISTRATE_WATCHDOG.md:92`: step 0's "Before step 3, verify SHA-256 …" is stale now that
step 1 executes one of the five pinned files (`magistrate_watchdog.py handoff-daemons`). Fix the wording.

Also correct the landing note's "four original failures" figure: the refuter measured 16 methods / 28 attributable
failing outcomes when HEAD's tests run against HEAD~1's code. Put the corrected figure in your report body.

## Constraints
WRITE_SCOPE exhaustive (header). Do NOT run the repository-wide suite; acceptance = the three scoped modules
`python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog`
to a log with rc. Keep the reaper-block extraction contract (between `watchdog_checkout=` and `   PY`, three-space
indent) and re-run `zsh -n` + `compile()` on the edited block. No `git commit`. Envelope header < 8192 bytes;
`verdict.implementation` in {implemented, partial, no_change}, `verdict.acceptance` in {ready,
pending_verification, needs_ruling}. Body: per-finding cure, the counterfactual each regression kills, the
fail-before/pass-after tails, acceptance tail with rc.
