# 08n — Row 12: the magistrate's terminal read of the exact merge candidate `d5ec18bb` (b0ae8462, 2026-09-16 00:05 PDT)

Read in full, myself, not from summaries: `joulewise/night_agent_install.py` (726 lines) and
`scripts/install_night_agent.sh` (88 lines) at `d5ec18bb`, plus the round-8 diff against `69d668be`.

**Engine.** `Shield` owns three dispositions and never the mask: `install` records the first signal only (idempotent),
`poll` raises `Signalled` from ordinary code, `quiesce` sets SIG_IGN, `release` is for in-process callers. `main()`
installs before `parse_args` and quiesces in its `finally`; `run()` installs (no-op) and has one try/except/finally:
`_enter` polls at every state boundary; explicit polls precede each `write_plist`, each `bootstrap` and each
verification `print`; `_commit` = clock predicate → the last poll → direct `COMMITTED`. `_teardown` dispatches on state
only (COMMITTED → SUCCESS/0 with best-effort sidecar discard; PARSED/VALIDATED/ADMITTED → REFUSED; STAGED…VERIFIED →
verified bootout where loaded, absence proofs, restore or RETAINED 4, restore failure RETAINED 1); `_unwind` contains
any teardown exception as RETAINED 1 and always quiesces. `uninstall()` installs, verified-bootouts, proofs, removes
plists under proof, discards sidecars, returns 0/4/1, quiesces. Absence proofs are unforgeable (`_PROOF_KEY`, bound to
target/label/generation; every bootstrap/bootout bumps the generation). `LaunchctlAdapter.print` is the three-valued
predicate (rc 0 → LOADED; rc 113 + the exact stderr LINE → ABSENT; else UNKNOWN); timeouts and OS errors are UNKNOWN
with diagnostics. `write_plist` is the sole publisher (atomic `os.replace`); `bootstrap` refuses unless both plists
exist. `validate_install` imports the driver lazily, checks the template, plan age/authorship, both HEAD pins, courier,
driver preflight, schedule, existing night records, then the read-only admission. Render mode uses `NullAdapter`
(every verb raises). `grep -c pthread_sigmask` = 0. Exactly two exit-0 paths.

**Shell.** Every valued option requires a non-empty value or exits 2 with the usage line; options are forwarded in
order, never rebuilt; `--plan`/`--render-only` absolutised; uninstall pins `/usr/bin/python3`; install derives the
venv interpreter and checks MIN_PYTHON by parsing one line of the driver; `exec` with PYTHONPATH pinned and cwd the
checkout.

**Verdict on the code as read:** sound; matches adjudication 34 D1–D10 as amended (34 addendum), cold-gate rulings 10/13,
and consult packet 13. Nothing overbuilt remains after round 8 (the mask machinery is gone). Merge-ability of `d5ec18bb`
is conditional on: delta re-audit of round 8 CLEAN, execution lens 2 LANDABLE, the lead's replay PASS, CI green on the
PR (or Ed's ruling that a green local replay suffices pre-merge), and the live smoke already PASS (08m).
