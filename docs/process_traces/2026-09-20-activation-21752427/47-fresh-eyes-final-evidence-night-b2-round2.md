# Record 47 — final fresh-eyes pass on B2 round 2 (`97b357ad`), 2026-09-20 ≈15:12 PDT

Auditor: Opus 5 subagent (same as record 45; read-only; /tmp/dr41-r2). Verbatim:

Round 2 delta re-audit (97b357ad, read-only in /tmp/dr41-r2): VERDICT PASS — E1–E4 land exactly as dictated, nothing wider, no new defect.

(1) E1–E4 confirmed.
- E1 tests/test_evidence_night.py:1513-1537 forges production:true into the EARLIER veto.json so the pre-attempt gate (evidence_night.py:1137) passes and only the boundary gate (:1203-1204) is live. Mutant with the boundary gate deleted: "AssertionError: boundary rehearsal evidence reached the installer" / FAILED (failures=1) — an outcome-shaped kill, not message-shaped. My round-1 survivor is dead.
- E2 :1199-1206 saves phase "observing-veto" durably, observes, then sets "publishing" + save() immediately before os.replace. probe_command gains timeout=None (:583-585, so installer_call's runner(argv, cwd=root) is unchanged) and the directive query passes timeout=60 (:998); "except subprocess.TimeoutExpired" precedes the broader SubprocessError handler (:1016-1018) — correct order — and the local channels are still observed after a timeout. The sleeping-runner test asserts timeouts == [60], phases == ["prepared","prepared","observing-veto","observing-veto"], directives error "timeout", 4 channels recorded, plan unmoved, custody empty.
- E3 the identical clause now appears in both docs (contract x2, handbook x1, byte-equal); the stale contract sentence "the lead repeats `check` at the publication boundary" is gone. Added: a phase table and "A refused or timed-out boundary veto leaves phase observing-veto and outcome not_published; it never reaches publishing."
- E4 render_notice :298 emits ["", *lines[4:]]; the notice test asserts body.splitlines()[:3] == [provenance, "", "Ed,"]; the composition test wraps notice() in redirect_stdout; the contract records that a successful real-launchctl publication is bench-only.

(2) Protected handbook regions byte-identical to origin/main: Executed->EOF 4c71305c61b0a8e3fea6b8fb9ec8b871; lines 68-144 fc6e3a97a4a5c7a650264f9facb7eed8. The handbook paragraph's last sentence matches the contract exactly (verified by string equality).

(3) Full suite under /opt/homebrew/bin/python3.11 (3.11.15): `Ran 92 tests in 158.356s / OK` (+5 tests vs round 1's 87). Targeted 3.13 run of the two E2 tests, E3, E4 and the notice render: `Ran 5 tests in 1.790s / OK`.

(4) Same-signature statements. "The entry point silently diverges from the bench procedure": now false in both directions. "An evidence-affecting side effect without a refusal path": none found — the 60 s directive timeout is fail-closed, recorded in the boundary record, and stops before any publication intent.

Remaining open item from round 1, unchanged and accepted by E4: no fixture exercises a successful real-launchctl publication (outcome: installed); that is now an explicit contract limitation rather than an unstated gap.
