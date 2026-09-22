# Cold-gate packet 06 — RETAINED-ROOT-REFUSAL-CLASS-01 returns to the gate after round 3 (activation ce7c57a9)

Assembled mechanically by the magistrate at 23:5x PDT 2026-09-21. Exhibits are verbatim seat outputs, a git diff, and bench command outputs; the magistrate's own view is confined to §3 and labelled.

## §1 Why the lane is back

Packet 02's ruling (`../02-coldgate-packet-retained-root-round3/10-coldgate-fable-ruling.md`, Q1) set a structural change for fix round 3 — the fixing seat authors no prose, every documentation sentence is copied from the ruling, every rule sentence is probed, and (item 4) "if either re-audit finds a same-signature defect, the lane returns to this gate with a new packet; the lead does not open another fix round." Round 3 was applied at the bench exactly as ruled (record `../03-round3-under-the-gate.md`; fidelity of every ruled passage MATCH per exhibit B Q2). Both round-3 seats then found the same-signature class in the ruling's own text:

- Sol delta re-audit 4 (exhibit B): should-fix F1 — runbook §0.7's ruled sentence "a `Refused:` exit (for example a symlink anywhere under a root)" is false; the classifier applies `safe_path` only to the plan path and the inspected `night/` record paths. Nit F2 — mutation m16 (ruled reason assigned before the span rule, string unchanged) survives; observationally equivalent. Merge recommendation: do not merge; return to the gate.
- Blind Fable pedagogy-and-contract lens (exhibit A): rule-sentence audit finds two FALSE sentences — R6 (the same runbook sentence) and H1, the handbook preamble "the census classifies every process outside the caller's ancestor chain as foreign" (foreign = argv-matched `codex|claude|t3` PIDs minus the caller's ancestors; `arm_census.py:237`, `night_gate.py:90`); that preamble was authored in fix round 1 and stood at `af85b38a`. First-use test: nine FAILS (every process; plan span; older sibling plan; session root; custody root in item 4; arm; entry checkout; timing constants; diagnostic) plus two borderline (retained in the runbook/comment; chain is open). Its §4 carries PROPOSED wording, labelled, not applied.

Bench re-execution (exhibit D): unrelated symlinks under `night/` and under the root → `retained`, verdict `pass`; a symlinked `night/courier.sent` → `Refused: symlink/path collision`. The bench also ran the handbook `descendants()` probe against a live process tree (record 03 §4; the Sol seat's sandbox could not read the process list).

Everything else in round 3 closed: A1-F2, A1-F3, A2-F1..F4 CLOSED with executed evidence (exhibit B Q1); `gen_state.py --check` rc 0; kernel pointers resolve; whole module 103 tests OK; m8/m12/m14/m15 KILLED. The full sharded replay on the round-3 head is running at the bench.

## §2 The open items

| id | where | what | authored by |
|---|---|---|---|
| R6 / Sol F1 | runbook §0.7, "a `Refused:` exit (for example a symlink anywhere under a root)" | FALSE: only the plan path and the inspected record paths (and their ancestors) are symlink-checked | packet 02 ruling Q5 text |
| H1 | handbook preamble sentence before "The ruled text" | FALSE: "every process" — the census sees only `codex`/`claude`/`t3` argv matches | fix round 1 (seat), pre-existing at af85b38a |
| FAILS ×9 | contract item 4, runbook §0.7, handbook pre-check | terms used before being built or glossed for a reader without project grounding | mixed: rounds 1–2 (plan span, older sibling plan, custody_root, timing constants, entry checkout), packet 02 text (session root), project-wide operator vocabulary (arm, diagnostic, every process) |
| Sol F2 (nit) | tests | m16 survives; the ruled "assigned after the span rule" order is not observable | ruling Q4 order requirement |

## §3 Questions for the judge

Q1 EXACT TEXT for R6. Supply the replacement for the runbook sentence (whole sentence, verbatim) so that the example names only what the classifier refuses (symlink at the plan path, at `night/` or at any inspected record path, including a symlinked ancestor of those). The magistrate does not author it.

Q2 EXACT TEXT for H1. Supply the replacement for the handbook preamble sentence, verbatim, so that "every process" becomes the census's actual population (argv matching `[c]odex|[c]laude|[t]3`, `night_gate.AGENT_CENSUS_ARGV`) and "foreign" is defined as the code defines it.

Q3 FIRST-USE FAILS. Rule which of the nine must be glossed in THIS merge candidate (supply the gloss text verbatim for each you require) and which go to a registered follow-up lane (name the lane's goal in one sentence; the magistrate registers it in the kernel as a row, which is bookkeeping). Exhibit A §4 carries the seat's PROPOSED wording; adopt, amend, or reject each. Consider: contract item 4 is contract text and operator-facing; the runbook and handbook are the arm procedure; "arm", "entry checkout" and "diagnostic" are used across many project documents, so a local gloss may be the wrong home.

Q4 m16. Rule whether the assignment-order requirement in packet 02 Q4 stands (then supply the regression shape that observes it, if any exists) or is withdrawn as unobservable (the string and classification pins m12/m15 remain).

Q5 CLOSING SHAPE. Packet 02 Q1 item 4 forbids a bench round 4 and Q7 says the lane closes when both seats return no should-fix. After the gate's Q1–Q3 texts are applied at the bench: (a) does the gate's own executed probe of each supplied sentence (paste the command and output in the ruling) plus the bench's fidelity check (whitespace-normalized MATCH) close the lane, or (b) is another seat pass required, and of which lens? State what evidence the merge record must carry.

Q6 Anything in exhibits A–D a merge reviewer should refuse that §2 does not list.

## §4 Hard limits on the judge
Read this packet directory, `../02-coldgate-packet-retained-root-round3/10-coldgate-fable-ruling.md`, `../03-round3-under-the-gate.md`, and tracked files at the worktree head; do not read RUN_STATE.md, TASK_QUEUE.md beyond grep hits, docs/process_traces outside `docs/process_traces/2026-09-21-activation-ce7c57a9/`, or narrative state docs. Never touch /Users/edr/code/JouleWise, /Users/edr/night-custody, /Users/edr/night-plan-staging, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents. Foreground only; no subagents; 20-minute wall budget; fixtures only under /private/tmp; write the ruling to `10-coldgate-fable-ruling.md` in this directory with the Write tool; items not executed in budget are marked NOT EXECUTED. Every sentence you supply must come with one executed command whose output shows it true.
