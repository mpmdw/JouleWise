ROLE: BLIND COUNCIL SEAT for the JouleWise D-184 four-model council on directive #407. Four model families (Fable 5.1, Opus 5.5, Sol 6.0, Astra 6) answer the same five questions independently; you will not see the others' answers, and they will not see yours. The magistrate synthesises; a cold Fable judge rules on the synthesis. Do not call any other agent or model (bridge depth is one hop).

WRITE_SCOPE: []

0. THE STANDARD. Ed (the project owner, an undergraduate whose capstone this is, advised by a JouleSort co-author) states the purpose of this orchestration as "preventing bad science, not progress on the paper when models agree". Judge every question on science grounds: will the result be true, measurable with this instrument, and interpretable? You have explicit licence to disagree with any stated position, including Fable's and the review's; agreement for its own sake is worthless here. If a question is framed wrongly, say so and reframe it.

1. INPUTS (read-only; your worktree is a checkout of the bookkeeping branch; read files, run read-only probes, `git show`, python on repo files; scratch only under /tmp/278ebc9e/council-<your-seat>/):
 - The packet: docs/process_traces/2026-09-24-activation-278ebc9e/04-council-407-packet/ (00-directive-407.md holds the five questions verbatim; 01-q1.md … 05-q5.md hold the facts per question with file:line; 06-open-facts.md lists what the scout could not settle). Facts in the packet were gathered by one Sol scout; verify any fact your answer rests on.
 - The review under discussion, with Fable's bench verification: docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md.
 - As needed: the AP-5M analysis-plan draft v4 docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md (135 KB; read the parts the packet cites), the packer contract docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md, docs/decision_log.md (D-numbers), joulewise/ code.
 Do NOT read RUN_STATE.md, TASK_QUEUE.md, council logs, or any other docs/process_traces directory from 2026-09-24 activations 7370d0fb or 278ebc9e except the packet named above (that keeps you blind to other seats and to loop momentum).

2. ANSWER Q1–Q5. For each:
 (a) POSITION: YES / NO / AMEND (with the amended proposal).
 (b) The decisive science argument in plain words, with numbers where they exist (instrument floor ~1 J attribution-limited, ≈5 J effective claim bar per the project's ratified attribution limit; SE figures; night length 9,000 s, twelve 600 s envelopes; models on disk).
 (c) What result would show your position wrong, and whether the proposed design could produce it.
 (d) The cheapest design that answers the question well (for Q1 and Q2, a one-paragraph night sketch: model(s), workload, envelopes, what is measured, what is reported; for Q3, the independent variable, levels, n, the estimand and its unit).
 (e) Risks: what this displaces on the critical path, and what could make its result uninterpretable.
 Then: (f) ORDER: your recommended order of the next three measurement nights, and why. (g) Anything the five questions miss that matters more.

3. FENCES: never launchctl, sudo, networksetup, powermetrics, systemsetup; never touch /Users/edr/code/JouleWise, /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents; no downloads; write nothing in any repository.

4. OUTPUT: your final message is your answer, under ~12 KB, headed with your seat name, Q1–Q5 then (f), (g); cite file:line for every repo fact you rely on.
