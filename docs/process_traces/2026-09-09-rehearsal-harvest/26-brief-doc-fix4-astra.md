WRITE_SCOPE: ["docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md","docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md"]
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Doc fix round 4 — PR #308 (gpt-6-astra, medium, genre implementation; verify-each-fact)

Why a seat and not the lead: the round-3 delta (read it:
/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/21-delta-308-round3-astra-report.md)
found the lead's bench prose over-stating what the artifacts show (F1, F2, F4) and a note that describes an unmerged cure as present
behaviour (F3). Same defect class as round 1. The structural response is that every sentence you write below must be checked against the
named artifact under docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/night-harvest/ BEFORE you write it, and
anything not shown by an artifact is labelled "inferred" in the text.

Edits (minimal, in place; keep the rest of both files byte-identical):
F1 (21i, the "Harvest-before-uninstall ordering evidence" sentence): replace with: the copies' order relative to the uninstall is
INFERRED — no transcript of the copy command was captured; the supporting facts are (a) the harvest copies exist and hash 17/17 while
the source root was removed at the epoch in removal-output.txt, and (b) pre-uninstall-observations.txt embeds a state.json whose
last_clock.epoch_s (quote it exactly from the artifact) precedes the uninstall epoch in uninstall-output.txt (quote it) by the exact
difference you compute; say that this dates the watchdog clock sample, not the copy.
F2 (21i, the night.log digest sentence): the digest inside night-result.json covers the FIRST TWO lines of night.log; four lines were
appended afterwards — list their timestamps exactly as they appear in the harvested night.log (02:56:03, 02:56:10, 02:57:33, 02:57:35 —
verify each) and which process appended them only if an artifact says so (else say "appended after the result was sealed").
F3 (21i, the "## Record note (Opus contract review 10, S4 …)" section): qualify the first sentence as describing the cure ONCE LANDED —
"Once NIGHT-GATE-STUB-CHAIN-01 lands (branch fix/2026-09-09-night-gate-stub-chain, fix head 5db38b58, PR #309), the night gate
performs NO chain-identity check for REHEARSAL_STUB plans …; on main at 83ab38ed the gate still reads the chain unconditionally
(the forcing defect above)". Verify 5db38b58 exists locally (`git cat-file -t 5db38b58`) and that PR #309 is named in no other artifact
you can check — if you cannot verify the PR number, write "the PR opened for that branch" instead.
F4 (00-DURABLE-STATE.md, the courier pid sentence in the 628c2eed section): replace "the courier's own heartbeat records its shell pid
82210" with "pid 82210 is the pid recorded in its heartbeat and sent marker (night-courier.heartbeat, night-courier.sent)"; nothing
about process type.
Acceptance: `git diff --stat` shows only the two files; `git diff --check` clean; for each of F1–F4 quote in your report the artifact
line(s) you verified against. No commit. Header < 8192 bytes; genre implementation.
