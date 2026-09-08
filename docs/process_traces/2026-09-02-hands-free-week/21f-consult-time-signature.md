# Consult — PR #295 same-signature (self-reported times), read-only, one round

Read: 21c (F2), 21e (N1/N2 + Same-signature), /private/tmp/ref-295-delta2-opus.md (D3), 21b at 277d719f.
Bench-verified this session (PD-1): `zsh scripts/install_night_agent.sh --uninstall --plan <absent> --hour 2
--minute 56` -> rc 2 "plan not found"; `--uninstall` alone -> rc 2 usage; arg validation (`:26-28`) precedes the
uninstall branch (`:170-175`). Load-bearing for D5.

## 1. Structural cause

Three mechanisms, one hole: the lead is the only author here whose output never passes through the
artifact-derivation discipline it imposes on delegates.
(a) **No clock.** The lead cannot read the wall clock inside reasoning; any `HH:MM` it emits is an estimate
anchored on the last time it actually read, plus its own guess at elapsed effort. The error is systematically
FORWARD (F2: +15-30 min; N2: +8 min; D3: unverifiable), because headless work feels longer than it is. The
estimate cannot be caught from inside: the process that would check it is the process that produced it.
(b) **Blind edit channel.** Edits go in by python/sed replacement without re-reading, so the lead never sees the
artifact the reviewer sees; and three defects entered as the lead's own *review commentary written into the file
under review* (82622e70 -> N1/N2; the N8 reconciliation text -> D3). The 21d brief's rule ("replace EVERY
self-reported `~HH:MM`") bound the astra seat's edits, not the lead's later ones: scoped to the delegate, not the file.
(c) **Self-observation recorded as narrative.** Facts about the lead's own process tree arrive as tool responses
inside context and are re-stated from memory ("verified at 02:00 PDT: pid 16456 ppid 83086") instead of stdout
copied to a file. Evidence about the author is the one class with no external artifact unless one is
deliberately created — hence the class that survives every sweep.

## 2. Mechanical rule for this activation's remaining edits (PR #295 only, not a process amendment)

R1 — no time-of-record is typed. Any `HH:MM` written into a docs file must sit on the SAME LINE as a token a
reviewer can re-derive: an 8-hex short sha, `internalDate <10 digits>`, `epoch_s`, a bare `17XXXXXXXX` epoch,
`events.jsonl`, or the basename of an artifact committed in the same commit.
R2 — any observation about this session or this machine (pid/ppid/`ps`/`launchctl`/`date`) is captured as stdout
into `docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/pass3-<slug>.txt`, first line
`date '+%s %F %T %Z'`, committed in the SAME commit as the prose (the existing `pass2-*` convention); the prose
cites `pass3-<slug>.txt` and never stands alone. No artifact -> the sentence is deleted, not softened.
R3 — pre-commit gate, run in the worktree; it must print NOTHING:

    git diff --cached -U0 -- docs/ | grep -E '^\+' | grep -v '^\+\+\+' \
      | grep -E '[0-9]{1,2}:[0-9]{2}' \
      | grep -vE '\b[0-9a-f]{8}\b|internalDate [0-9]{10}|epoch_s|\b17[0-9]{8}\b|events\.jsonl|(pass[0-9]|bench)-[A-Za-z0-9._-]+'

Every printed line is either given a same-line source or deleted. The window constants already pass (they carry
1788944160/1788945300 on the line); rates like "~10 min" do not match. Second gate: every `pass3-*`/`bench-*`
basename cited in the staged diff must satisfy `git ls-files --error-unmatch <path>` in the same commit.
R4 — round 3 is a ZERO-NEW-FACTS round: each edit is a move, copy, deletion, or code token from a string pair
written down before editing. No new sentence asserting an observation, and the commit message claims only "edits
D1-D6 as specified" (D1 exists partly because a commit message asserted a cure that was not in the operative block).

## 3. One mechanical verification per pending edit

Reviewer first re-extracts the three ```zsh blocks (block0 historical `# F4/F5: historical sequence only`,
block1 = A, block2 = B `# Block B (re-derive every variable`); the count must still be 3 and all pass `zsh -n`.

- D1: `un-publishing the plan this session authored` occurs EXACTLY ONCE in 21b, and that line number lies
  between block2's opening and closing fence (i.e. inside block B), on the line also containing
  `--plan "$NIGHT_CUSTODY/night_plan.json" --hour 2 --minute 56`; block0's install line reads the bare
  `|| { print "ABORT: agent install failed"; exit 1; }`.
- D2: inside block2, `date +%s` occurs exactly once, on a line containing `-lt 1788945300`, and its line number
  is LESS than the line numbers of both `me = json.load` and `mkdir -p "$NIGHT_CUSTODY"`. (Bench: rc 0 at
  1788945299, rc 1 at 1788945300, same harness as N5.)
- D3: `grep -nE '02:00|16456' 21b-rehearsal-20260909-arm-plan.md` prints nothing, OR prints only lines naming a
  `pass3-*.txt` that `git ls-files --error-unmatch` resolves in this commit.
- D4: inside block2, `standdown.request` and `night_plan.json(N)` each occur exactly once, both line numbers less
  than the `me = json.load` line, and each line ends in a fatal `|| { print "ABORT: …"; exit 1; }`.
- D5: on the D1 line, the character index of `--uninstall` is LESS than that of `rm -f
  "$NIGHT_CUSTODY/night_plan.json"`, and the uninstall call carries `--plan "$NIGHT_CUSTODY/night_plan.json"
  --hour 2 --minute 56`. (Bench above: uninstall after the rm exits 2 "plan not found" and leaves both plists.)
- D6: `git diff -w <round-3 base>..HEAD -- docs/process/NIGHT_HANDBACK.md` is empty (whitespace-only change) and
  `awk 'length>110' NIGHT_HANDBACK.md` prints nothing.

## 4. Bench or delegate?

Split by class, not by size. All six are 1-4 line string moves inside code blocks the lead authored and holds the
ruling context for — below the delegation threshold, and a seat would need the whole D-175/ruling-B packet to
place D1 correctly. So: the lead does D1, D2, D4, D5, D6 at the bench, under R4 (exact old->new pairs written
first) and R3 (gate on the staged diff). D3 is the one it must NOT edit into new prose — cure it by DELETION of
the parenthetical (`— verified at 02:00 PDT: pid 16456 ppid 83086 —`), keeping the structural claim, or by R2
capture if the Monitor is still live; deletion is preferred because it adds zero bytes of new assertion.
The real delegation is downstream, not upstream: delta-3 must be run by a fresh reviewer seat against the six
checks above, and the lead must write NO review commentary into 21b — that channel produced N1, N2 and D3. If
the lead cannot express an edit as a byte move, that edit is the one to hand to a seat with dictated fills.
