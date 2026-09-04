# Process lessons distilled from the 2026-09-02/03 work

This record separates seven lessons that arose during the hands-free work. A
*wrapper* is a model session or launcher layer placed around another model
invocation. A *direct seat* is a bounded invocation started through
`codex-run-v3` without a model wrapper. A *preflight* is the intake and checking
done before an edit. A *replay* repeats a check at a named revision. A *packet*
is the bounded evidence set given to an independent reviewer. A *first-use
gate* checks whether a reader can understand a term at its first use. An
executed first-real-use probe is a separate proposed behavioral gate, not part
of the generally ratified rule. A *cold gate* is an independent review before
an irreversible process mechanism is accepted or installed.

## 1. Wrapper cost

The usage cutoff stopped the wrapper fleet while completed Sol work remained on
disk. On resumption, Ed's recorded 2026-09-03 budget regime moved
bounded Sol work to direct runner seats, reserved Fable for merge-bound reading
and the mandatory cold gate, and required disk harvest before relaunch. This is
evidence about that dated regime; it does not replace D-129's standing
Opus-directed Sol default.

- Evidence: `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`,
  “2026-09-03 19:45 update,” “2026-09-03 21:05 update,” and “Resume sequence
  after a usage stall.”
- Doctrine boundary: “Use direct bounded seats only when a separately recorded
  authority, such as Ed's 2026-09-03 budget regime, permits the
  exception; otherwise D-129's Opus-directed Sol default governs.”
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: record the direct-run safeguards as conditional
  on a separately authorized exception and preserve D-129's default.

## 2. Direct `codex-run-v3` pitfalls

Direct invocation removes a wrapper but not launch ceremony. Two clean seats
were reported as scope violations because the lead had added untracked files in
their linked worktrees. Another semantically clean review was unusable because
its JSON envelope exceeded the runner's declared byte cap. Successful later
reviews pinned an empty write scope, ran in a disposable archive or clone, kept
the machine-readable envelope small, and placed detail in the prose body.
Interrupted wrappers also required harvesting the worktree and output files
before any retry because the underlying run could finish after its wrapper
died.

- Evidence: `docs/process_traces/2026-09-02-dx-registry/MAGISTRATE-NOTES.md`;
  `docs/process_traces/2026-09-02-t26-items-1-4/MAGISTRATE-NOTES.md`;
  `docs/process_traces/2026-09-02-dx-registry/22a-terra-243-protocol-failure.md`;
  `docs/process_traces/2026-09-02-dx-registry/22-fresh-pass-brief.md`;
  `docs/process_traces/2026-09-02-hands-free-week/17i-watchdog-04-refuter-execution.md`;
  `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`.
- Proposed doctrine sentence: “A direct runner call must pin checkout, revision,
  comparison base, write scope, output, genre, and verification; isolate
  read-only work from lead dirt, keep the envelope within its byte contract,
  and harvest all named outputs before retrying.”
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: add a direct-run checklist and a harvest-before-
  retry branch to `codex-delegation`; distinguish semantic findings from runner
  failures caused solely by attributed pre-existing dirt.

## 3. The preflight trap

The general playbook says to run repository-wide discovery during preflight.
That default became counterproductive for a bounded watchdog review: discovery
entered a broader calibration test and was interrupted, while the named
watchdog module passed. The useful result was the focused review, not the
pre-edit broad run. Direct seats therefore need the task's explicit verification
rule to take precedence over the generic default, especially when the prompt
says “edit first,” names modules, or prohibits discovery.

- Evidence: `docs/process_traces/2026-09-02-hands-free-week/17k-watchdog-05-refuter-contract.md`,
  verification V1, V2, and flag G2; contrast the focused-only build record in
  `docs/process_traces/2026-09-02-hands-free-week/17f-watchdog-01-landing.md`.
- Proposed doctrine sentence: “When a task supplies a narrower or edit-first
  verification rule, preflight performs intake and workspace checks but defers
  testing until after the edit and runs only the named checks.”
- Installed in-repository: `docs/agent_playbook.md`, dated addendum.
- Proposed global-skill edit: make task-local verification precedence explicit
  in `codex-delegation` and `operation-loop`, and require the report to mark the
  broader suite deliberately not run rather than failed.

## 4. Replay hygiene

The day produced three complementary replay safeguards. A mutation restore
that also changed an adjacent command was caught by the full-file digest before
the next mutation. Later mutation probes began from a fresh restoration. The
merge-bearing paper replay named the exact scratch merge and both parents, kept
the full suite unpiped in a log, reissued the generated artifacts at the final
head, and compared their bytes with the issued copies.

- Evidence: `docs/process_traces/2026-09-02-hands-free-week/17c-planpin-06-fix-round-1.md`,
  “Mutation probes”; `docs/process_traces/2026-09-02-hands-free-week/17h-watchdog-03-fix-round-1.md`,
  “Mutation probes”; `docs/process_traces/2026-09-02-paper-d-dg071/43-integration-replay-and-terminal-review-e7425eef.md`.
- Proposed doctrine sentence: “A merge-bearing replay runs in a clean
  disposable tree at named revision and parents, records its unpiped log and
  exit status, starts each mutation from verified bytes, and byte-compares any
  artifact whose reproducibility it claims.”
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: add the clean-tree, exact-parent, restore-digest,
  and artifact-byte-comparison checks to `operation-loop` replay and final-head
  recipes.

## 5. Packet hygiene

The watchdog packet was mechanically strong but still carried decisive
defects: a proposed `--bg` behavior was described as executed fact; a
load-bearing audit was cited but omitted from the manifest; current-state facts
had no time pin; competing arguments were summarized asymmetrically; and
`claude --bg --help`, presented as a read-only inspection, actually started a
session and left processes visible to the production census. The cold seats
could recover only by independently rebuilding the missing evidence.

- Evidence: `docs/process_traces/2026-09-02-hands-free-week/12-coldgate-opus-refutation-packet-11.md`,
  “Q8 — Packet hygiene”; `docs/process_traces/2026-09-02-hands-free-week/14-coldgate-fable-ruling-packet-11.md`,
  “Q8 — Packet hygiene”; synthesis in
  `docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md`.
- Proposed doctrine sentence: “A cold-gate packet uses neutral atomic
  questions, labels observation versus proposal, pins volatile facts, manifests
  every load-bearing source or bounded excerpt, presents contrary evidence
  symmetrically, and executes no command until its side effects are known.”
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: add a packet-lint checklist to `council` and
  `adversarial-review`, including a prohibition on assuming that `--help`
  neutralizes a mode-changing option.

## 6. First-use gate outcomes

The first-use rule had two different outcomes, and both matter. The contract
review successfully exposed defined vocabulary that appeared before its plain-
language explanation. For the watchdog, however, the implementation existed
while the first install/stand-down rehearsal was not replicable; the contract
review therefore kept that artifact not landable. D-171's dated addendum
resolves the authority boundary: a first-use vocabulary table is mandatory for
changed terms and literals, while the general executed-probe rule remains
PROPOSAL PENDING ED. The magistrate may require a probe only for a brief it
commissions under its own authority.

- Evidence: `docs/process_traces/2026-09-02-projection-02/163-terra-proj02-pedagogy.md`;
  `docs/process_traces/2026-09-02-projection-02/181-luna-proj02-delta.md`;
  `docs/process_traces/2026-09-03-kernel-batch/01-lieutenant-report.md`,
  “Item 1 — the D-171 addendum”; `docs/process_traces/2026-09-02-hands-free-week/17k-watchdog-05-refuter-contract.md`,
  finding F4.
- Doctrine sentence: “A contract edit that changes defined terms or literals
  carries a pre-landing first-use table.” A behavioral-probe requirement must
  identify separate authority: pending Ed's decision, it applies only to a
  magistrate-commissioned brief when the magistrate requires it.
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: teach `consistency-sweep` to produce the ratified
  term table; do not install a universal behavioral-probe rejection rule unless
  Ed ratifies the pending proposal.

## 7. Cold-gate seat separation

The first watchdog convening placed both independent seats in the same scratch
directory. Even without a recorded overwrite, that arrangement made accidental
cross-reading and file collision possible and weakened the meaning of
independence. The relaunch assigned the cold adjudicator its own scratch
directory; the final synthesis records the cure.

- Evidence: `docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md`,
  final hygiene paragraph; the resumed plan in
  `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`, watchdog
  lane.
- Proposed doctrine sentence: “Each cold-gate seat receives a distinct scratch
  directory and sealed output, cannot read another seat's work before sealing
  its own, and is compared only by the lead after all seats finish.”
- Installed in-repository: `docs/orchestration.md`, dated addendum.
- Proposed global-skill edit: make per-seat scratch roots and post-seal harvest
  mandatory in `council` and `adversarial-review`.

## Distillation disposition

The in-repository doctrine changes are additive and evidence-linked. No global
skill was edited because those files are outside this session's write scope.
No state-kernel, queue, run-state, decision-log, or paper-skeleton change is
needed for this distillation: D-129 and D-171 already supply the controlling
boundaries. If the global skills are revised later, their version record should
point back to this file rather than copy the incident narrative.
