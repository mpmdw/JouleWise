SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (EXECUTION lens, read-only): EVIDENCE-NIGHT-ENTRY-01 slice B2 — commit 798bced1 on feat/2026-09-20-evidence-night-b2

Cwd is `/Users/edr/code/JouleWise-wt-lifecycle2-21752427` at `798bced1` (one commit over main `ff623dc8`; +501/−41 in `joulewise/evidence_night.py`, `tests/test_evidence_night.py`, `docs/contracts/evidence_night_entry.md`, `docs/process/NIGHT_HANDBACK.md`). Read-only in the repository (WRITE_SCOPE empty); copy to /tmp for runs/mutations; never touch `/Users/edr/code/JouleWise` (canonical) except read-only git queries; never run real `launchctl` or real `gh` (both are injected seams — use them); no mail, no network, no clone into `~`. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python`. Known sandbox artefact: `tests.test_run_night…test_blocked_journal…` fails at its 8 s watchdog in this sandbox; the bench decides it (432 OK) — do not spend on it. Do not end your turn before the report. Break it.

Design (brief 40 on main: `docs/process_traces/2026-09-20-activation-21752427/40-brief-seat-evidence-night-b2.md` — read it via `git show origin/main:<path>`): notice TRANSPORT stays with the magistrate's Gmail tool; the code adds `notice` (draft from the sealed state; requires a fresh armable `check.json`; writes `lifecycle/notice-draft.txt`), `veto` (owner-authored open directive issues via an injected `gh` runner; `standdown.request`/`STOP`; the manual mailbox-NO relay file `lifecycle/NO`; any read failure → refuse, never clear; writes `lifecycle/veto.json`), `publish-install` now requires a fresh clear `veto.json` too, the custody baseline after install (`lifecycle/baseline.json`) with drift reporting in `verify`, clone-side JSON on stdin, and the handbook's tracked-command sequence paragraph.

## Refute, with executed evidence
1. **Veto fail-closed:** every failure mode of the `gh` runner (nonzero, empty output, malformed JSON, an issue whose author is not `mpmdw`, an issue by mpmdw with an empty body) → what does `veto` do? A non-owner directive must NOT veto but must be reported; an owner directive MUST refuse; a runner error must refuse "cannot read directives". Mutants: make the runner error → clear; make a non-owner issue count as a veto.
2. **Freshness and binding of `veto.json`:** touch a sealed artefact or re-run `check` after `veto` → does `publish-install` refuse? Is `veto.json` bound to `prepare.json` (sha) and to `check.json`? Age bound? Race: `veto` clear, then a directive opens, then `publish-install` — the brief says publish-install requires FRESH clear veto evidence: how fresh (seconds?) and is the directive check repeated at publication? If not, is that a silent gap vs the bench step 4 ("stop files twice, directives empty")? Executed: simulate the race with the injected runner.
3. **Baseline:** after a fake-launchctl `publish-install`, mutate a custody file's size/mtime and add a file → `verify` must report drift (additions, removals, metadata); does it REFUSE or only report? Which is the bench step-5 semantics (read `17-arm-scripts-qpe01-pilot-r2/step5-verify-and-exit.zsh` lines 39–48)?
4. **stdin JSON:** intercept every `P -B -c` call and confirm no JSON payload remains in argv; a 1 MB inventory travels on stdin without error.
5. **Handbook:** `git diff origin/main -- docs/process/NIGHT_HANDBACK.md` is one hunk (+9) in §Census; both protected regions byte-identical (the lead's md5s match); is the paragraph accurate against the code (every command name and order; the fallback sentence)?
6. **Notice draft:** `notice` refuses without a fresh armable `check.json`; the draft's content equals `prepare.json`'s `notice_draft` refreshed against the sealed state — what "refreshed" changes (attempt number? prior candidates?) and is the draft byte-stable across reruns?
7. **Same-signature statements** for "the entry point silently diverges from the bench procedure" (step 4's stop-file and directive checks "twice"), and "an evidence-affecting side effect without a refusal path".

## Report
claude-codex-report/v1 envelope for --genre review; findings tiered with executed evidence; JSON header under 800 bytes; total under 8 KB.
