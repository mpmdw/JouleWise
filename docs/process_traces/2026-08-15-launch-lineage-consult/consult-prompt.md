DESIGN CONSULT — WO-LAUNCH-BINDING F2: how a child collection/calibration writer receives the
authenticated launch lineage WITHOUT argv/env (the launcher consult rejected passing a receipt
path/token through argv or environment, but did not define the alternative). 1 round; license to
disagree.

WRITE_SCOPE: []

READ-ONLY; probes to $TMPDIR only.

CONTEXT:
- docs/process_traces/2026-08-15-launcher-binding-consult/consult.md (the adopted contract — steps
  1-5, the one-use FD handoff token, "no argv/env for the token")
- The partial implementation record: /private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/wo-launch-partial-record.md (F2 flag + scope request)
- The launcher already built: scripts/launch_window.py + verify_consumed_launch in
  joulewise/arm_readiness.py (on branch impl/wo-launch-binding — read via
  `git show impl/wo-launch-binding:scripts/launch_window.py`)
- The chain the lineage must survive: window-chain.zsh → collection writers (run_campaign.py,
  validate_powermetrics_fiducial.py) → reduce → verdict → extraction → mint; docs/decision_log.md
  WO-LAUNCH-BINDING contract (downstream provenance refusal requirement)

THE QUESTION: the launcher does consume→execve of the frozen chain. The chain's child writers
(collection, calibration) must STAMP their output bundles with the authenticated launch-consumption
lineage so downstream reduce/mint can reauthenticate it — but the token must not travel via argv or
environment (forgeable/observable). Design the lineage-locator: (a) does the launcher write a
FIXED-CUSTODY consumption receipt at a boot/pack-derived path the children independently locate and
authenticate (like the arm-readiness custody model)? (b) an inherited FD the execve'd chain passes
down (fragile across a zsh chain + multiple python children)? (c) a boot-session-bound file whose
presence+content the writers verify? For the chosen mechanism: the exact locator derivation, what
each writer authenticates before stamping, the bundle metadata field, how reduce/mint reauthenticate
it, the fail-closed refusals (registered under D-078), and how it interacts with the R1 content-bound
lifecycle (is the lineage receipt content-bound or session-bound?). Also: the successor-config
`launch_lineage_required` flag is Phase-2 (frozen packs can't be edited in place) — confirm that
staging or argue otherwise. DELIVER the mechanism + the exact staged work-order breakdown (which
stage lands on this branch vs Phase 2).
