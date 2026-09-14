# Refuter brief — ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01 install (branch fix/2026-09-13-arm-census-system-services), EXECUTION lens (Astra high; workspace-write for temp dirs, WRITE_SCOPE [])

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in a detached review worktree at the install branch's HEAD (base main `4b9a3411`; diff = `git diff 4b9a3411..HEAD`: `joulewise/arm_readiness_evidence_t0.py` +8/−4 and `tests/test_arm_readiness_evidence_t0.py` +141). Read-only on tracked files; temp dirs allowed; you may spawn and terminate processes a test itself starts, never signal any other process; your sandbox cannot list processes (`pgrep` exits 3) — say so where a check needs it; the lead ran the module live (record 40). Never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` may be used read-only), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. No network.

Authority (read-only, in `/Users/edr/code/JouleWise-wt-bk-24b9d3dd/docs/process_traces/2026-09-13-activation-24b9d3dd/34-coldgate-packet-arm-census-browser-probe/`): ruling 10 (Q1 argv, Q3 regression spec), pairing refuter 12 (A1–A4), synthesis 13 with its addendum (decoy-child control). Seat reports 36 and 38 beside the packet directory.

Try to BREAK the install:
1. Fidelity: the two constants equal the ruled strings byte-for-byte; `_derive_process_census` still issues exactly four `_fresh_probe` calls in the ruled order with the ruled labels; keep-awake and agent argv unchanged; `_expect_absent` and the emitted `derived` dict unchanged (diff the function body against `git show 4b9a3411:joulewise/arm_readiness_evidence_t0.py`). Any other change in the module is a finding.
2. G1/G2 (pure): run them; then confirm the mutation kills M1–M7 by applying each in a /tmp copy of the module (old alternation; drop `( |$)`; one browser name; bare `watch`; drop `/Contents/MacOS/`; drop `tail -f`; `Firefox` case) and pasting the failing test name per mutation. A mutation no test kills is should-fix.
3. G3 (authoring path, mocked probes): read it against the existing named-refusal matrix pattern; does it prove that a browser or monitor hit REFUSES the whole authoring (`T0EvidenceAuthoringError`, kind `PROCESS_CENSUS`, no source/evidence directory written) and that the four probes are issued in order? Would dropping `_expect_absent` for the browser probe (M8) or removing the monitor probe (M9) fail it? Apply both in /tmp and paste.
4. G4 (Darwin): read the decoy mechanism; confirm the decoy is the test's own child, terminated and waited in `finally`; that a decoy leak on assertion failure is impossible; that the assertions require the decoy's pid line to match the pattern under pgrep's own engine; that the negative checks cannot be satisfied vacuously (what happens if pgrep returns exit 1 and no lines? — must fail because exit_code 0 is asserted). State what M10 constructs it kills (`(?:…)` → rc 2; `\b`/`\d` → the decoy line absent) and any construct it would NOT catch.
5. Pinned-argv test and the AST census test (`_fresh_probe` site count; 600 s constant) pass: run `python3 -m unittest tests.test_arm_readiness_evidence_t0 -k argv -k fresh_probe -k census` (whatever selects them) and paste.
6. Contract-change check: `git diff 4b9a3411..HEAD -- configs/ joulewise/arm_readiness.py docs/contracts` empty; the registry's `t0.no_stray_keepawake` row untouched; `derived` fields unchanged. Confirm "not a contract change".
7. Writing standard: the module comment and the four docstrings — every term built or glossed (probe, decoy, dialect, M-numbers point at the ruling).
8. `git diff --check 4b9a3411..HEAD`; `git status --short` empty.

Report (claude-codex-report/v1, genre review) severity-tiered with file:line, pasted evidence, and "what the lead should double-check". Under 8000 bytes.
