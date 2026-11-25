# Interim look stage-1 rehearsal

The RL-180 B.2 packet needs the dev-01 to dev-04 stage-1 rehearsal before
the research lead's manifest pass. The campaign path creates its two
private files once. The rehearsal uses the manifest's range and the
same pinned verifier, stage-1 time readers, preflight and fit. It
creates its own private destination and returns the stage-1 public
fields to the lead. The campaign schema refuses the marked rehearsal
artifact. [Manifest dry-run rule](https://github.com/mpmdw/JouleWise/blob/9eb65f4f520f6d00a48cd7aec952f5f2996c82a3/docs/process/cadence/looks/lm-interim-01.json#L105)
· [Manifest-pass packet](https://github.com/mpmdw/JouleWise/blob/8efedc0da79911db59e788bbf207be513f653e59/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17745)

The pre-pass draft can run after its Git commit registers the custody
root, fills the pin table and binds the manifest, roster and verdict
hashes in its draft ledger row. It checks the shared merge branch and
`origin/main` using read-only Git operations. The selected spans'
offload Check items still come from main. The verifier's temporary files
stay inside the private rehearsal directory.

## Draft re-pin

`cadence_look_manifest.py pin --write` updates the three changed
digests for `scripts/cadence_look_run.py`,
`joulewise/cadence_looks/manifest.py` and
`joulewise/cadence_looks/custody_pins.py`, plus the draft
`LOOKS.json` row's manifest digest. D4 authorizes this re-pin.
The manifest's custody section now specifies the rehearsal's output
directory exception to the campaign path rule.
[Rehearsal rule](../process/cadence/looks/lm-interim-01.json#L105)
· [Pin intake and run contract](../process/cadence_look_manifest.md#7-stage-1-rehearsal-for-the-manifest-pass)

## Verification and handoff

The test fixture generates all of its own bytes. It exercises both a
committed manifest and a detached pre-pass draft. It compares the
campaign and rehearsal custody-read allowlists, checks the pin verifier
against mutations inside and outside the selected blocks, and checks
that a campaign run after rehearsal produces identical files. It
hashes before and after rehearsal across the ledger, custody and Git
metadata and checks the destination refusals and public summary.

The focused rehearsal, post-open allowlist and bytecode tests passed
9 checks. The state generator and draft pin check passed. The
orphan-fixture census could not inspect the process table because
`ps` returned Operation not permitted.

The full local discovery suite includes archived measurement fixtures
outside this seat's read scope. Hosted CI, independent executing review
and cold review are draft gates. The next MBP step is to run the
rehearsal on the lead's merged, input-bound commit and return the
summary to the lead.
