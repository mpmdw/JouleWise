# Arm-readiness network-time policy

**Why this row exists.** Every power sample is timestamped by the system clock. If macOS syncs network time
during or between measurement windows, it can step that clock, and the steps would land inside energy integration
windows. So network time stays OFF across windows. The only resync is in the arm step, before the window's OFF
receipt, its 600-second dwell and its first capture.

**The registry change.** The live registry `configs/arm_readiness/d117_row_registry_v2.json` used to require row
`clock.restore_recipe`: a close-out step that turned network time back ON after the verdict and both backups.
That doctrine is retired (D-186, 2026-09-29). Registry v2 has no retirement field: it requires exactly 35 sorted
rows, and every profile selects every row. So the row is replaced in place by `clock.network_time_policy`, with
predicate `clock.network_time_policy.v1`. Its phase (`FREEZE_AND_ARM`), applicability (`ALWAYS`), evidence kind
(`DOCTRINE_PIN`) and lifecycle policy (re-derivable) are unchanged. The archival v1 registry, the retired
predicate and every historical receipt keep their bytes and meaning.

**What the deriver checks** (`joulewise/arm_readiness_evidence.py::_derive_doctrine_pin`). It first normalizes the
runbook text: it removes Markdown emphasis and backticks and folds whitespace, keeping paragraph, checklist-item
and code-line boundaries. It then splits prose into sentences at `.`, `!` or `?` followed by whitespace. Re-wrapping
a line therefore changes nothing. The checks are exact text checks; the deriver does not interpret synonyms.

1. **Required sentences.** Each of the following must appear in §5A as a whole normalized sentence, not as a
   substring, so that a negating prefix also refuses:

- `Network time stays OFF after completion, refusal, crash, verdict and both backups.`
- `Resync happens only in the arm step.`
- `It then commands OFF and saves a write-once receipt, including failed attempts.`
- `The clock-disable step uses that saved receipt.`
- `It does not issue a second toggle.`
- `Record the OFF receipt and its identity in close-out; do not restore ON.`
- `No ON command is permitted after the first capture of a window.`
- `D-127 authorizes only the exact off and on writes; the arm step uses ON only for a needed resync and finishes with OFF.`
- `A manual /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on command is a supervised desk action between windows only.`
- `ED-OWED: exercise both exact vectors from a cold credential state, leaving off at the end, between windows only:`

2. **No other instruction to turn network time ON.** The deriver scans every runbook section whose hash the pack
   pins (§5, §5A, §5B, §5C, §6, §10) plus the backup section §11 and the close-out section §12. All eight hashes
   enter `pack_pin_material.runbook_section_sha256`; the `desk.arming_procedure.v1.runbook_sections` fact keeps its
   original six sections. A normalized sentence or code line matches, case-insensitively, if it has:

- A clock topic (`network time`, including hyphen/underscore separators;
  `time sync` and its suffix forms; `setusingnetworktime`, `systemsetup`,
  `sntp` or `timed`) together with an enabling form: `on`, `enable`,
  `re-enable`, `reenable`, `restore` or `resume`, including their
  `es`/`ed`/`ing` forms. This includes `turn`, `switch` or `set ... on`
  and `back on` because they contain `on`.
- Implicit clock forms even without a named topic: `restore ... ON`,
  `undo ... OFF` or `ON command`.

   A matching sentence refuses unless it sits in §5A and equals one of these current-doctrine sentences exactly.
   A changed permission or a negation does not qualify:

- `D-127 authorizes only the exact off and on writes; the arm step uses ON only for a needed resync and finishes with OFF.`
- `Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on`
- `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`
- `If needed, it enables network time at arm only and uses a 120-second polling budget (each command is bounded to 30 seconds) for the reference check to pass.`
- `No ON command is permitted after the first capture of a window.`
- `Record the OFF receipt and its identity in close-out; do not restore ON.`
- `A manual /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on command is a supervised desk action between windows only.`

   The cold-credential command line is allowed only together with the required between-windows, finishes-OFF
   sentence in list 1.

3. **Exactly two backups.** The pack-side `desk.arming_procedure` check refuses unless the frozen
stage graph has exactly two commands with `command_kind: backup` under each
stage's `launch.commands`. `closeout_attachments.backup_requirements` may be
absent; when present it must be a mapping, and its
`required_successful_backups` must be the integer 2 or absent.

4. **No clock command in the frozen recipe.** The serialized
frozen `arm_attachments.launch` recipe and `stage_graph` are scanned
case-insensitively for `setusingnetworktime`, `systemsetup`, `sntp` and `timed`;
any occurrence refuses, including in `argv_template` or another command
representation. Hashing a clock-control command does not permit it.

**What it emits.** The deriver emits the new clock fact and `desk.arming_procedure.v1`, never
`clock.restore_recipe.v1`. This is procedural doctrine evidence;
`clock.network_time_off` and its live `CLOCK_PROBE` requirements are unchanged.
Missing live OFF evidence still refuses ARM.

**Registry digest.** The live registry has no separate whole-file digest literal or sidecar to
advance. Its consumer requires canonical bytes equal to committed HEAD and
computes the SHA-256 reference. New plan trees, freeze receipts and ARM
receipts record that committed digest. No frozen pack, historical receipt,
histsem pinset, historical digest, archival v1 registry or old predicate is
rewritten. Historical verification uses its authenticated receipt coordinates
and retains the restore predicate's original semantics.
