# QUIET-GUARD-01 spec consult record (Sol high, thread 019fcb69-76aa-7f61-898b-d835851d78f7)

Full verbatim spec: rollout rollout-2026-08-03T23-15-14-019fcb69-76aa-7f61-898b-d835851d78f7.jsonl, sha256 83bd744b8ee3a0eed37df82410642cc440a3d993051d6d1be98b67a062353c62
(persists in ~/.codex/sessions; loss-insurance copy .desk/quiet-guard/).
Envelope valid (DISCUSSION; base_head_drift benign — lead commits 1bcd6f5/ac8a681 landed mid-consult).

Lead adoptions (pending the row's own gauntlet):
- TWO-PHASE HANDOFF core: t3 session creates handoff_pending (blocks new launchers), self-terminates; detached watcher acquires quiet_held ONLY after session exit + zero-agent census. Resolves the arm-while-agent-alive contradiction fail-closed.
- Atomic flock interlock spanning check-spawn-register in every launcher; independent census for bypassed paths; state root /Library/Application Support/JouleWise/quiet-guard/.
- Watcher = characterized instrument infrastructure, never an agent; blocks in waitpid; first round proves negligibility (A/B/B/A, Ed-predeclared threshold); NO energy subtraction.
- README banner = presentation projection; both modes built (mechanical_commit / deferred_projection), neither unattended until Ed rules identity/push; arm commit BEFORE head freeze.
- Lease releases BEFORE t3 relaunch; relaunch failure = closed_degraded, never re-lock.
- sudo -n only; §5A evidence complete_but_not_authorizing until SEC5A-REMOTE-01.
- 25 open questions in the rollout — implementation-packet intake; sharpest for Ed: state-root permissions (Q2), launch-perimeter enumeration (Q3), unattended git identity (Q10), relaunch fallback (Q13).
