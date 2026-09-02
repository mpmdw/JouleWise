# DESIGN CONSULT — unattended quiet-machine windows (D-169: "unattended loop first")

You are one of three independent design seats (the others are different model
families). The magistrate synthesizes; you have explicit licence to disagree
with anything in the packet, the prior rulings' *ordering*, or the magistrate's
framing — but not with the fences marked UNCHANGED.

## Read first (all read-only)

1. The mechanical scout packet (facts, file:line, gap list, Ed-hands residue):
   `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/unattended-lane-scout.md`
2. Repo `/Users/edr/code/JouleWise` (main, head bdf557c9). Rulings D-115,
   D-127, D-128, D-149, D-150, D-167, D-169 in `docs/decision_log.md` (index
   rows near the top; sections by `## D-NNN`). The ruled T-0 design:
   `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
   and the ten-gate table in `debate-sol-critique.md` §2(c). Code:
   `scripts/launch_window.py`, `scripts/capture_t0_step.py`,
   `joulewise/arm_readiness_evidence_t0.py` (`:1312-1314`, `:1724`),
   `joulewise/t0_rehearsal.py`, `scripts/prewindow_check.sh`,
   `scripts/quiet_mac_prep.sh`, `docs/process/d149-go-receipt-template.md`,
   `docs/phase_2/window_runbook.md:800-830,1230-1260`.

## The forcing problem (Ed, 2026-09-01, verbatim)

"why are quiet windows still gated by me? why can't you do this? i'm tired of
having to be at the machine" … "bad. that should be done first. so you can
drive the experiments entirely."

## UNCHANGED fences (not up for design)

- Zero-agent capture: no `codex|claude|t3` process exists during T-0 census
  or capture (D-127 §2, D-128 §3; the code predicate is exact-exit-1 pgrep).
- The privileged install step, if any new one is needed, is Ed's one command
  (D-115, D-127 §3). The network-time sudoers slice is ALREADY installed and
  agent-usable via `sudo -n`; the powermetrics slice too.
- D-078 no-retry; D-149 mechanical T-0 conditions (2)-(5); D-167 evidence
  immutability; D-166 pre-registration; the C-028 gauntlet on every merge.
- No `danger-full-access`, no sandbox bypass, one-hop bridge depth.

## The target, in order of value

T1. **G2-a runs with nobody present**: a timer fires on a chosen night; the
    machine is checked quiet (no agent process, load/CPU/dwell per
    `prewindow_check.sh`); the D-149 (2)-(5) conditions are evaluated
    mechanically and a GO receipt is written into custody; the reviewed
    launcher runs the frozen window exactly once (D-078: no retry of the
    measurement itself); the result and every refusal reach Ed by EMAIL in
    the morning (phone push does not work; email does).
T2. **The agent comes back by itself**: after the window's completion event, a
    fresh headless agent session is launched with liveness proof (heartbeat
    file written by its first scripted action; launcher stands down only on
    proof; bounded retries with backoff; independent launchd fallback timer —
    D-127 §4 "never one mechanism"), and it harvests/judges/prepares the next
    pack. G2-a is a diagnostic window (D-167: lead discretion, no Ed GO);
    the `_v5` transaction proper still gates on Ed's recorded GO
    (`V5-TRANSACTION-GO-01`) — but that GO is a one-time email reply, not
    presence.
T3. The same machinery runs G2-b and the transaction nights.

## Questions you must answer (numbered, each with file:line grounding)

Q1. **Minimum mechanism set for T1.** Which of the scout's gaps G-1..G-9 are
    truly required for T1, which can be deferred to T2/T3, and is there a
    smaller shape than the scout's (e.g. can the GO-receipt producer and
    consumer be ONE module that `launch_window.py` calls; can the census
    producer be the launcher's own pre-exec step)? Give a staged plan where
    STAGE 1 is the smallest merge that removes Ed from a G2-a night.
Q2. **GO receipt post-D-167.** Condition C1 (council verdict) has no live
    producer. What replaces it for a diagnostic window — nothing (state
    the receipt class), or the pre-registration record (D-166)? Specify the
    receipt's machine-readable schema (reuse
    `joulewise.t0_unattended_d149_go_receipt.v1` from `t0_rehearsal.py:48` if
    it fits — say whether it does), who writes it, where in custody, and the
    exact by-class refusal in `launch_window.py` (name a registered reason
    code or the registration path).
Q3. **Scheduler and wake layers.** User LaunchAgent vs system LaunchDaemon
    (the window must run as `edr`, needs the GUI session for powermetrics?
    — verify what powermetrics needs); how the two D-127 §4 wake layers are
    made independent; what "stand down on liveness proof" means concretely
    (file, content, deadline — the T26 cold gate ruled a 600 s liveness
    bound, `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`).
    How does a failed night surface (refusal record + email) without any
    retry of the measurement?
Q4. **Who observes the machine when nobody is on it.** The G8 record
    (`process_lineage`: `agent_pid`, `agent_exit_monotonic_ns`,
    `pre_launch_census`, `capture_censuses`) has no producer. Design the
    producer for an UNATTENDED night: the agent that armed the night exits
    BEFORE T-0 (how is its exit proven — its own last act writes a record?
    the launcher observes the pid gone?), and the window chain takes the
    capture-time censuses itself. Address the idle-T3-Code-window case: an
    interactive `claude` process left open by Ed → refusal + email, never a
    hung night. Should the headless loop session replace the interactive one
    entirely on window nights?
Q5. **Interaction with the running /loop.** The magistrate today is an
    interactive session under a self-paced loop. Propose the night protocol:
    when does the loop stop itself, what does it write, and how does the
    relaunched headless session (T2) re-enter the loop with context (what file
    it reads first)? Keep Fable-token economy in mind: the relaunched session
    should be able to delegate the harvest to Sol/Opus.
Q6. **Rulings needed.** List every point that needs a magistrate ruling or
    Ed ratification before stage 1 can launch (E-10 runbook amendment; G7
    consumer entry point; receipt class names; anything else), each with the
    cite that makes it necessary. Fewer is better — but do not hide one.
Q7. **Risk register.** Top five ways stage 1 produces a wrong number or a
    silent failure, each with the detector that catches it.

## Output

Under 220 lines. Headings Q1..Q7, then "Stage plan" (table: stage, files
touched, new modules, interfaces, refusal codes, tests, Ed-hands residue,
rulings needed, est. LOC), then "Where I disagree with the packet or the
rulings' ordering" (may be empty), then a one-line confidence.
