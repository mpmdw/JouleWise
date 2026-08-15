DESIGN CONSULT — WO-LAUNCH-BINDING contract (rule-2 pre-decision; council-verdict Phase 0 / Opus
W7 — contract-bearing: adds an enforcement gate to the launch path and changes the operator's
night sequence; 1 round; license to disagree).

WRITE_SCOPE: []

READ-ONLY; probes to $TMPDIR only.

CONTEXT: docs/process_traces/2026-08-15-readiness-council/council-verdict.md (WO-LAUNCH-BINDING);
refuter-outputs/refuter-DG-out.md F3 + sol-out-refuter-DG.md F3 (both lenses CONFIRMED:
consume_launch_capability exists and emits a receipt but never execs; window-chain.zsh performs no
receipt check; zero downstream consumers authenticate launch-consumption lineage; a direct chain
invocation collects a normal-looking window with no refusal anywhere); docs/phase_2/
window_runbook.md §6 chain template + the E-9a/b/c sequence; joulewise/arm_readiness.py
consume_launch_capability (:4025-4095); decision log D-134 (atomic single-launch capability).

CONSTRAINTS (ruled): Ed — not an automated verdict — performs the physical launch; the binding
must preserve that. Fail-closed at a MACHINE, not at human close-out item 5.

QUESTION: design the atomic arm-consume-to-launch binding: (a) the reviewed launcher (consume →
revalidate → exec the frozen chain — exact crash semantics between consume and exec; what happens
if the chain dies pre-settle; single-use enforcement); (b) the DOWNSTREAM provenance refusal —
which consumer(s) (reduce? verdict? mint?) must authenticate the launch-consumption receipt for
this pack/boot, and the exact refusal reason-codes; (c) runbook §6 + E-step deltas; (d) the
regression shape proving a ceremony-skipping launch fails closed at every downstream stage.
DELIVER: the contract + contract deltas (D-134 clause additions if needed) + failure modes of
alternatives (e.g. chain-side check only, downstream-only).
