ROLE: BLIND CONSULT SEAT on a JouleWise escalation (lane A280 PR B0, night-kind dispatch parity). Read-only. You have licence to disagree with every prior ruling. Do not call any other agent or model.

WRITE_SCOPE: []

THE ESCALATION. B0 must make every idle-only site in the night machinery dispatch on the immutable NightKind table, while keeping the existing idle night BYTE-IDENTICAL. That covers notice, wrapper, every refusal code and text, reporting, cleanup, and uninstall/veto/verify. It must also add NO second, unauthenticated kind authority. Contract: /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/10-a280-b0-seat-brief.md §1–§2.
- Round 0 (`7647bb2e`): the lenses (29a Sol, 29b Opus) found 3 BLOCKERs. The reporting paths raised on kind; `candidate_state` changed idle uninstall/veto/verify; the driver inferred kind from unauthenticated plan fields.
- Fix round 1 (`bee658c5`, brief 32 cures C1–C6): the named witnesses now match base. But the delta re-audit (72b, Astra) finds the SAME SIGNATURE again, with 2 BLOCKERs:
  - F1: with a non-UTF-8 wrapper and a BOM/UTF-16 C5 receipt, head skips the base's refusal repair;
  - F2: sealing refusal texts and order change for missing, non-UTF-8, ambiguous or stripped wrappers and for a changed bound source.
  It also finds 2 should_fix: a TypeError on a malformed kind field, and a bare wrapper accepted as kind authority in `_custody_row`.
Two consecutive rounds failed on the same defect class: an idle behaviour change or an unauthenticated kind source on malformed inputs. The rule says that is structural, so the next step is this consult, not fix round 2.
All files are under /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/: lens reports 29a/29b, cures brief 32, fix report 47b, re-audit 72b. Your worktree is a detached checkout of `bee658c5`; base is `2ea6a7ec`. Scratch only under /tmp/278ebc9e/b0esc-<seat>/. Never launchctl, sudo, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise.

ANSWER:
 Q1. Root cause, structurally. Why does each round preserve the named witnesses but change idle behaviour on the next malformed input? Is the contract "idle byte-identical on every path" checkable by lenses at all, or only by execution over a corpus?
 Q2. Candidate structural cures, with cost and guarantee. Include:
   (a) a DIFFERENTIAL PARITY HARNESS: a generated corpus of plan/wrapper/receipt/clone states, including malformed encodings, missing, ambiguous and stripped files, and moved sources. For the idle row, base `2ea6a7ec` and head outcomes (return values, refusal codes and texts, files written, calls made) must be identical. This becomes the acceptance test for B0.
   (b) narrowing B0: leave malformed-input paths on the base code, and dispatch on kind only after the base validation has succeeded ("validate as base, then route");
   (c) splitting B0 into per-surface PRs, each with its own parity corpus;
   (d) your own.
 Q3. Your recommended plan for the next round as executable text: seat, WRITE_SCOPE, what the harness must enumerate, and the gate.
OUTPUT: final message under ~8 KB, headed with your seat name; file:line for code claims; executed probes where they decide.
