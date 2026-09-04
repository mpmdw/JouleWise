# Exhibit: decision_log.md D-171, verbatim (object of Q7)

## D-171: hands-free week — Ed's delegations for unattended windows (Ed, 2026-09-02)

Ed, in-session at ~20:50 PDT on 2026-09-02, replying to the magistrate's
leave-checklist (verbatim: "1. yes handle yourself. 2. i dont want to have to
emial you anything back. im sure its fine, go ahead. 3. yes if i reply by
email you can consider it a permission but the goal here is to not need me at
all to run the expirement window - 4. yes, authorized. 5 and 6 sounds good i
trust you. 30 min before a window seems too much"). Ed is away from the
machine for up to a week from 2026-09-02; hands-free operation is required.

1. **E-10 amendment RATIFIED.** `docs/phase_2/window_runbook.md` E-10 ("Ed
   personally invokes the sole reviewed launcher exactly once") is amended:
   the unattended night driver invokes the reviewed launcher
   (`scripts/launch_window.py`) once per frozen pack. Kernel fence
   `UNATTENDED-LAUNCH-01` is released on this ground; the runbook clause is
   rewritten in the lane that installs the driver-side call.
2. **`hC` custody DELEGATED to the automation.** The step-6 confirmation
   digest is no longer operator-pasted per use; the cold gate on the
   watchdog/launch lane rules the concrete route (mode-0600 custody file or
   driver-derived), and the runbook's "never store hC in an env file"
   sentence is amended by that ruling.
3. **Transaction GO DELEGATED.** `V5-TRANSACTION-GO-01` (`ed_external`)
   is satisfied by the magistrate's own gate (cold-gate-adjudicated
   readiness) — Ed must not be needed to run a window. An email reply from
   Ed still counts as permission whenever one arrives. The step-6 YES on the
   family marker (D-150b) is delegated on the same sentence unless Ed
   objects before leaving.
4. **Relaunch watchdog install AUTHORIZED** (user-level launchd, no sudo)
   once it passes the gauntlet and a cold gate; it emails Ed at each launch
   and stand-down and honours a stop file.
5. Measurement checkout of record = `/Users/edr/JouleWise-measurement-20260813`;
   the magistrate fast-forwards it and relocks its venv (no sudo).
6. Batch-2 defaults adopted: pre-landing first-use table as a mandatory gate
   for contract edits that add/move/rename defined terms or code literals,
   PAIRED with executed probes for behavioural clauses (exact text goes
   through the cold gate on packet 45 of the decode-identity trace before
   installation); trace-path placeholders NO; D-161 governs tests NO;
   named-survivor rule YES as the definition of recurrence; the party
   proposing to continue does not classify the defect YES.
7. **Stand-down margin = 5 minutes before a window's t0** (30 was "too
   much"); email at stand-down and at relaunch; Ed reads, does not reply.

Machine state Ed leaves: lid open, AC attached, caffeinate running,
screen may lock, no logout, no reboot; FileVault is on, so an unplanned
reboot halts everything until someone types the disk password (accepted).
