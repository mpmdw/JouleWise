# Registration FILL bindings (Sol 6.1 high, read-only): derive every block-4 interface binding from the code

Worktree: /Users/edr/code/JouleWise-wt-dd5-fill, detached at 2c1f64de, the integration head before the X11 fix round. Interfaces should not move in X11; FLAG any binding that depends on a file X11 may change. Scratch /tmp/dd5-fill/ only. Read-only: WRITE_SCOPE is empty.

The registration draft is `git show origin/design/2026-10-04-v5-qualification-block:configs/campaigns/v5_qualification_25g83/registration_block4_draft.md`, with ruling 76 (addenda A-E) and record 44 on the same branch. It carries 45 `FILL[...]` tokens. For each token, produce one binding row:

- **CLI tokens** (`PLAN-WRITER-CLI`, `ARM-ONLY-CLI`, `ARM-ABORT-CHECK-CLI`, `QUALIFICATION-OBSERVE-CLI`, `DESK-CLOSEOUT-CLI`, `QUALIFICATION-HARVEST-CLI`, `G2B-HARVEST-CLI`, `TERMINAL-REFRESH-CLI`, `Q110-RECORD-CLI`, `G10-CONTROL-CLI`, `NULL-RESTORE-CLI`):
  - the exact script path and subcommand, and every required argument, with its meaning;
  - the outputs written, by path pattern and schema id;
  - the exit codes.
  
  Prove each with `--help` or a dry argument-parse run, and cite file:line. If a registered role has no CLI in the code, say so; that is a finding.
- **Map tokens** (`ROOTS-AND-CUSTODY-MAP`, `BATTERY-EVIDENCE-MAP`, `S1-QUALIFICATION-PRODUCER-MAP`, `BLIND-CUSTODY-MAP`, `PER-OCCURRENCE-ID-AND-RECEIPT-MAP`, `PER-OCCURRENCE-OFF-RECEIPTS`, `PER-OCCURRENCE-SHUTDOWN-CAPS`, `ARM-CONTROL-DEADLINE-RECIPE`, `BACKUP-DESTINATIONS-AND-VERIFICATION`, `STEP6-CUSTODY-PATHS-AND-RECORD-SHA256`):
  - the path layout the code fixes, as templates with their variables;
  - the producer and consumer file:line;
  - the schema ids.

  For the roots map, include the controls' ledger seed copies (addendum D item 4). Say whether the writer or ARM code accepts a `CALIBRATION_LEDGER` outside the four ARM roots, and prove it by reading the code.
- **Roster and constant tokens** (`S1-ROSTER`, `S1-COMPLETE-AUXILIARY-ROSTER`, `ONE-BLOCK-STOP-RC-AND-RECORD`, `S1-SUCCESSFUL-CHAIN-RC`, `PRODUCTION-POLICY-SHA256`, `PRODUCTION-LEDGER-SEED`, `V5-PACK-REGEN-RECORD`): the exact values, with source file:line or config digests at this head. Compute the SHA-256s yourself. `V5-PACK-REGEN-RECORD` is PR #481's merge `306840b7` plus the regenerated pack identities.
- **Seal-time tokens** (`H-FULL-SHA-AND-INTEGRATION-GATES`, `REGISTRATION-SHA256-AND-COLD-PAIR`, `SEALED-FILE-INVENTORY`, the three `*-PACK-DIGEST-AND-FREEZE`, `DESK-PROOF-AND-FAMILY-BINDINGS`, `BLOCK4-SEAL-RECORD-PATH`, `TERMINAL-REFRESH-CHANGED-PATH-MAP`, `RECOVERY-HEAD-EXTENSION-IF-NEEDED`, `CLAIM-PLAN-RELEASE-BINDING`, `L10-A-RATIFICATION-RECORD-PATH`, `G10-CONTROL-RECORD`, `Q110-RECORD-PATH`, `A1/A2/S1-AUTHORIZATION`):
  - say what produces the value and when;
  - for `SEALED-FILE-INVENTORY`, list the exact repo paths that §12 "Pinned at H" names, expanding every directory and class named there to concrete files at this head (the readers, validators, generators, templates). Mark any §12 class that maps to no file.

Output: `/Users/edr/night-archive/desk-day-v5/fill-bindings.json` (one object per token: `token`, `kind`, `value` or `template`, `evidence` [file:line or command], `due`, `finding`), and a short Markdown report. No energy or power values.

WRITE_SCOPE: []
No background processes. Finish in this turn.
