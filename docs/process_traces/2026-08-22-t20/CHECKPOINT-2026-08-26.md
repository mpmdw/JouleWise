# Session checkpoint — 2026-08-26 morning (Ed-requested pause)

Everything is committed and pushed; nothing is in flight. A fresh session
resumes from this file plus RUN_STATE.md.

## Where the project stands

- **S-0 clone-proof: COMPLETE** (estate 10, full green through §5;
  S0-COMPLETION-RECORD.md). Ten estates; every earlier halt was a real
  instrument defect, cured on main.
- **D-155 pre-window worklist: W-0 through W-7 DONE.**
  - W-0 ruling: nr-synthesis-ruling.md (+ both seat reports custodied).
  - W-2 code (PR #199, merged 3c96b18f): terminal-review Pack-Sha256
    membership at BOTH parsers + window_status.sh freeze-span sentinel;
    full regression battery; gauntlet: contract-lens SOUND + magistrate
    bench execution of the producer-bytes seam (multi -m attestation parses
    all-three-PASS; CRLF fails closed).
  - W-3 docs (PR #198, merged): every D-155 doc reconciliation; its own
    refuter round (4 blockers cured: E3 draft/no-sidecar → E4
    render-final-then-sidecar; H1 seal/append; H2 struck; H5 equality
    predicate).
  - W-4: reviewed head DECLARED = 3c96b18f (CI run 32970864856, success).
    NOTE: later docs-only merges (W-6, this checkpoint) advance main;
    the runbook's Phase A re-declares the head at session time.
  - W-5: measurement checkout /Users/edr/JouleWise-measurement-20260813
    fast-forwarded to 3c96b18f, clean tree, reviewed_main exact_match true
    (run via the real predicate), zero _v4 output present.
  - W-6: prompt inventory (PR #200, merged): w6-prompt-inventory.md —
    six licensed ASK prompts verified unmatched by any allow rule; THREE
    NEEDS-ED items (below).
  - W-7: full suite at the reviewed head on a scratch clone:
    rc=0 in 2084 s (~35 min) — the budget's last unknown resolved.
- **W-8 (preflight) NOT run** — it belongs to the evening before the window.
- **W-9 (pre-shakedown, not pre-transaction):** standing rows
  CONSUME-CONFIRMATION-SUPPLY-01, T0-UNATTENDED-01, UNATTENDED-LAUNCH-01,
  the WINDOW-COUNCIL-GATE reconvene, and the V-5 scheduler-gate check.

## Ed's open items (the only gates left before the window)

1. **Venv relock** at -20260813 (~10 min): fresh-venv method in the runbook
   §1.1 checklist (mv .venv .venv.pre-v4 → rebuild from
   env/mac-measurement-lock.txt constraints → empty diff vs the 37-line
   lock). Wheel unavailability ⇒ fall back to a fresh checkout (NR-1 C).
2. **Permission hygiene (W-6 NEEDS-ED):** run the transaction session in
   MANUAL permission mode + add ask-rules for the two licensed command
   classes (auto mode's classifier makes prompt counts unguaranteeable);
   delete the six -20260818 blanket allows; suspend Bash(gh pr merge:*)
   from C11.1 until fixation is pushed. Also: launch the session from
   /Users/edr/code/JouleWise (the measurement checkout has NO .claude
   settings), and note Phase A (evening before, Ed absent) contains ~12
   unlicensed ASK rows — plan for someone to answer or pre-classify.
3. **One word on notification cadence** (NR-9): immediate pings per desk
   event (recommended) vs batched to phase boundaries.
4. **Pick the transaction night** — earliest credible 2026-08-28, chosen
   ahead of a week whose nights are free (168-hour campaign clock starts at
   the evidence commit; clean-nightly ≈ T+74 h, full-weather ≈ T+146 h).

## Paper state

Draft carries: P06 spec + D-152 values; §2 replay fence (43/43 mechanical
re-derivation, PR #189) with in-draft pointers; DS-08 option B (the §5
dominance numbers 10.92x/5.92x/7.02x with both floor terms built in prose);
§3/5/7 enumeration consistent. Results section awaits the transaction →
shakedown → claim windows.

## Known process notes for the next session

- codex-type coordinator agents end turns while their Sol run is in flight;
  budget one SendMessage resume nudge each (memory: codex-agent-turn-ending).
- The CI teardown-race flake (test_identity_pins ProjectionLifecycleTests
  tearDown rmtree on 3.14 runners) hit 6 shards once on PR #200 and passed
  on rerun — not yet registered as a kernel row; register if it recurs.
