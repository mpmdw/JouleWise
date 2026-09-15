# 13 — Magistrate synthesis: cold gate 28 ruling 10 ADOPTED with the Opus pairing amendments — 10:34 PDT (clock-read)

Magistrate `d6888966` (Fable 5.1). Inputs: ruling 10 (cold judge convened 10:18:53, file 10:24; both probes ran before
the ruling), pairing refuter 12 (Opus; independent answers first, refutation 10:33). Convergent on all six; no
overrule; no dissent.

## Adopted

- **Q1 — (a).** Delete `scripts/install_night_agent.sh:374`; `teardown`'s `:312` guard becomes the success branch that
  removes the backup (warning on failure), never calls launchctl, never changes the exit status; regressions (i)/(ii)
  and the two mutations as dictated. Definition: the class-1 invariant covers the two loaded jobs and the two plist
  files; a `TMPDIR` backup is not that state. POSITIVE RULE (Opus, material), recorded as the lane's invariant and
  pinned by the regression: *after the commit gate, no statement may fire `teardown`'s failure branch.* SIGPIPE
  residual: out of scope (installed state stands).
- **Q2 — (i)**, scope expansion of this lane's WRITE_SCOPE (same three files), not a contract change to exhibit H.
  Uninstall block verbatim from ruling 10 (bootout both, re-read `print` both, retain and `exit 4` if either loaded,
  else remove and `exit 0`); regression mirroring cell 9 + one-label variants; the existing
  `test_uninstall_ignores_both_pin_mismatches_and_invokes_launchctl` amended to bootout/print pairs. `:294` checks BOTH
  labels (dead-man-only preloaded → rc 3, zero bootstraps). Consequence named (Opus): the tracked assertion at
  `tests/test_install_night_agent.py:216` (`assertEqual(3, … "print ")`) becomes 4 — the brief must say so.
- **Q3 — round 3 AUTHORISED** (charter §9: dictated single-statement/single-block edits inside proven structure; F1's
  clock half is definitional; F2 is a never-briefed site). Round 3 carries exactly: Q1, Q2 (+ `:294`), Q4-F3. Then
  delta 3 with the isolated-reversion protocol AND the named survivor lists (below). **STOP CONDITION (Opus text,
  adopted verbatim):** delta 3 answers same-signature YES if, as an executed case at the round-3 head, either (class 1)
  the installer exits 0 with either label loaded while a clock read taken after the commit gate is at or past
  `min(selected_span_close, install_close_epoch)`; or (class 2) any path in `scripts/install_night_agent.sh` ends
  with a label loaded and its plist absent, or exits 0 while a label it attempted to bootout is still loaded. On YES:
  no round 4; the lieutenant launches no fix seat and hands back; the magistrate convenes the redesign consult (three
  seats: Astra + Opus + blind Fable, on a transactional installer — one Python state machine with a single commit and
  a single teardown, the shell reduced to argument parsing) and emails Ed in the same activation. The count is per
  CLASS, not per site. Decider: the magistrate. The lane never lands with a live class-1/2 site as a "registered lane";
  conservative should-fix residue may.
- **Q4 — F3 folded** (`trap '' INT TERM HUP` at the top of `teardown` after `local result=$?`; regression: TERM from
  the first restore `cp` → both priors byte-identical, no backup dir, rc unchanged). **F4 registered** as
  INSTALLER-BACKUP-WINDOW-01 (nit, conservative).
- **Q5 — REFUSE accepted (packet defect, mine).** Binding for landing: delta 3 re-runs BY NAME lt-04 §F4's 22 survivors
  and lt-10's 8 `teardown` + 3 tail survivors at the round-3 head and reports each; the must-die set = any survivor
  removing `trap - EXIT` (`:316`), the `exit 4` (`:329`), either `print` re-read (`:321,:324`), `cp -p` (`:334`), the
  render-only guard (`:317`), or the `:312` success guard (Opus); diagnostic-wording survivors are text-only.
- **Q6 — AFFIRM all three** lieutenant rulings; render-only must not refuse loaded labels.

## Process note

Second cold gate of the day on one lane; both convened hands-free in under ten minutes each; the pairing refuter
again supplied the load-bearing amendments (positive rule; observable stop condition; a test-assertion consequence).
The judge again reports auto-loaded user-level doctrine (packet 25 synthesis §Process observations stands).
