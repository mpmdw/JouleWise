WRITE_SCOPE: ["docs/contracts/window_liveness.md","docs/process/MAGISTRATE_WATCHDOG.md","docs/process/NIGHT_HANDBACK.md","docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"]

# WINDOW-LIVENESS-DOCS-01 — REWRITE round under the writing standard (gpt-6-astra, HIGH, genre implementation; docs only)
Head 655b3368. The pedagogy + fidelity review at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ci-pedagogy-liveness-docs-astra-report.md
found the first draft fails the standard (A1 ~60 first-use failures, A2 not rebuildable from the example, A3 decision
table incomplete, B1/B2 code-fidelity defects). Rewrite docs/contracts/window_liveness.md from scratch to this BINDING
standard (Ed, 2026-08-19, verbatim): "The bar: a reader should be able to REPLICATE the mechanism from the text alone —
rebuild it, not follow the gist. First-use test (run mechanically before delivering): every term of art, criteria word,
or verb doing technical work is either (a) built from physical reality before first use, (b) glossed in plain words AT
first use, or (c) deleted. A term whose meaning arrives only in later text fails the draft. Why-chain: every mechanism
gets its forcing problem, a concrete worked example with real numbers, and — for anything spatial or algorithmic — a
diagram in which every visual element is named. An unexplained shape will be read as 'a circle', and the reader is
right. No word does unpaid work. If a later sentence would ever need to say a phrase 'has been doing a lot of work',
the explanation is out of order — restructure so the definition precedes the use."
Structure the rewrite as: (1) the forcing problem in physical terms (a status publisher running git/network work
during a power measurement contaminates it; the old machine-wide process-name grep could not tell a live chain from a
leaked test stub and tripped under parallel test shards); (2) the three physical facts the mechanism records — a
process id, its process group, and the kernel's process start time as printed by /bin/ps ("lstart") — each glossed
at first use with the exact ps invocation and a REAL six-field response line (take one by running
`/bin/ps -o pid=,pgid=,lstart= -p <your own shell pid>` if the sandbox allows; otherwise quote the historical capture
and label it); (3) the chain.started marker: exact JSON with real values, the two-step write (complete pid/pgid/epoch
first; start token added by atomic replace) with a named-element diagram (ASCII is fine) of the timeline claim →
spawn → first write → probe → replace, and what a reader sees at each instant; (4) the identity probe's decision
rule with the rc table (rc 1 + empty = DEAD; rc 0 + empty = UNKNOWN; six fields + matching token = LIVE; else
UNKNOWN) and why rc 0 + empty must not be DEAD (a probe replaced by /usr/bin/true); (5) the active-campaigns registry:
path (derived, with a real example), entry JSON with real values, who writes it, who removes it, what "stale" means
physically (the pid is gone or reused — show a reused-pid example with two different lstart values), and the
operator's exact repair command; (6) the census over custody parents, including the missing-parent = empty rule;
(7) the COMPLETE publish decision table: rows for every combination of (marker: absent / malformed / complete-no-token /
complete-with-token / exited) × (probe: LIVE / DEAD / UNKNOWN / not-run) × (registry: empty / entry-live / entry-dead /
entry-unknown / malformed) that can occur, with the refusal precedence stated as a rule and then applied; (8) a
worked end-to-end example with real numbers through publish and refuse. Fix every B1/B2 fidelity defect by citing the
implementing line for each mechanism sentence in a final "Code map" section (file:line at this head). Then re-do the
four pointer paragraphs so each glosses chain/campaign/custody/indeterminate at first use or links AFTER a one-line
gloss. Deliver a self-run first-use audit at the end of your report: the list of every term of art and where it is
built or glossed. Acceptance: tests.test_docs_freshness rc 0 to a log; git diff --check; no commit; header < 8192 bytes.
