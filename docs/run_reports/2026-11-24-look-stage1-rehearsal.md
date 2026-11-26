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
hashes in its draft ledger row. It fetches `origin/main` using the campaign
stage-1 fetch and checks the shared merge branch. The selected spans'
offload Check items still come from main. The verifier's temporary files
stay inside the private rehearsal directory.

## Fix-1 after Astra's audit

Astra demonstrated that the original branch-only guard let a rehearsal
create both artifacts inside a span registered on main. The next main
campaign run refused the unexpected file. The audit also reproduced
acceptance of a relative destination.

The rehearsal now inspects the ledger and registered manifests from the
shared rehearsal ref and freshly fetched main before creating its
destination. It refuses overlap in either direction, accounting for
physical paths, filesystem identity and case variants. A refusal names
the overlapping root. The checkout requires an absolute destination with
symlink-free components. A failed main fetch refuses before the
rehearsal creates a directory.

The synthetic reproduction starts with stale local main, registers
distinct inputs on the two shared refs, and attempts the same
destination inside a pinned span on main. The rehearsal refuses and
leaves the later campaign output byte-identical to the control. The
external destination succeeds. The focused suite also exercises a
main-only ledger root, a root registered through an alias, a destination
that would contain a future root, relative paths, a symlinked parent and
a failed main fetch. [PR #970](https://github.com/mpmdw/JouleWise/pull/970)

Seventeen focused tests and all 21 layout tests passed at utility
priority. The draft manifest and generated state checks also passed.
The CLI option test recognizes the rehearsal destination and still
checks every former path option.

## Fix-2 after the host-command inventory check

Shard 6 reported one missing row and zero stale rows. The repository's
`scan()` and a scan of the module docstring in isolation traced
`<module>:44c8da2be87da73a` to the documented
`python3 -I -B scripts/cadence_look_run.py stage1 --rehearsal NEW_DIRECTORY`
invocation. It gives the magistrate the rehearsal entry point with an
isolated interpreter and bytecode writes disabled. The docstring is
usage text and runs no command at import. The actual rehearsal uses the
existing Git seam to fetch main for the destination fence and the
existing isolated verifier to authenticate the selected spans. The
scanner reported only the new usage line. [Shard 6 run](https://github.com/mpmdw/JouleWise/actions/runs/45556571166)

Both inventory tests and all five rehearsal tests passed at utility
priority. The inventory also passed on Python 3.13, the shard's
interpreter. Astra's independent synthetic re-check at `f5b34c4d1`
returned MERGE. Fix-2 changes the test inventory and this report.

## Draft re-pin

`cadence_look_manifest.py pin --write` updates the three changed
digests for `scripts/cadence_look_run.py`,
`joulewise/cadence_looks/manifest.py` and
`joulewise/cadence_looks/custody_pins.py`, plus the draft
`LOOKS.json` row's manifest digest. D4 authorizes this re-pin.
The manifest's custody section now specifies the rehearsal's output
directory exception to the campaign path rule.
Fix-1 re-pins the runner and refreshes the ledger's draft manifest hash.
[Rehearsal rule](../process/cadence/looks/lm-interim-01.json#L105)
· [Pin intake and run contract](../process/cadence_look_manifest.md#7-stage-1-rehearsal-for-the-manifest-pass)

## Verification and handoff

The test fixture generates all of its own bytes. It exercises both a
committed manifest and a detached pre-pass draft. It compares the
campaign and rehearsal custody-read allowlists, checks the pin verifier
against mutations inside and outside the selected blocks, and checks
that a campaign run after rehearsal produces identical files. It
hashes before and after rehearsal across the ledger, custody and Git
metadata apart from Git's `FETCH_HEAD` record. It checks the destination
refusals and public summary.

The focused rehearsal, post-open allowlist and bytecode tests passed
9 checks. The state generator and draft pin check passed. The
orphan-fixture census could not inspect the process table because
`ps` returned Operation not permitted.

The full local discovery suite includes archived measurement fixtures
outside this seat's read scope. Hosted CI, independent executing review
and cold review are draft gates. The next MBP step is to run the
rehearsal on the lead's merged, input-bound commit and return the
summary to the lead.
