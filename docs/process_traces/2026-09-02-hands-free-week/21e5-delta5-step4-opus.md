# Delta-5 fresh-eyes review — bookkeeping/2026-09-09-rehearsal-arm (READ-ONLY, Opus)

Reviewed `git -C /Users/edr/code/JouleWise-wt-magistrate-1ef89702 diff origin/main` (worktree HEAD 2e3a6098,
origin/main 1c83f2af, +103/-12). Nothing written outside this file; no git write, no signal.

## Executed evidence (this session)

- `zsh -n` on all three ```zsh blocks: rc=0/0/0. `compile()` on both PY heredocs (8-line PY0, 23-line PY1): OK.
- Step-4 PY1 extracted verbatim and `exec`'d with `subprocess.run` + lock `open()` mocked (ps table = own tree
  under lock pid 83086 + ChatGPT.app tree + fake vllm 58633; pgrep stubbed). rc by case — A baseline **0**;
  B interactive bare `claude` **1**; C `bash …/codex-run-v3` **1**; D `claude daemon run` reparented to pid 1 **1**;
  E `/Applications/T3 Code.app/…/T3 Code --resume` **0 (MISS)**; E2 `node …/t3-code/dist/cli.js` **1**; F orphan
  `…/cua_node/bin/node /Users/edr/.codex/plugins/…` ppid 1 **0 (MISS)**; G orphan `/Applications/ChatGPT.app/…/codex
  sandbox` ppid 1 **1**; H `node scripts/claude-bridge-mcp.mjs` **1** (nit, fail-closed); I `…/versions/2.1.261
  --resume` **1**; J `claude bg-pty-host` **1**; K `/Applications/Claude.app/…/Claude` **0**; L `codex_runner.py` +
  `…/t3code/host.js` **0**; M real 09-08 shape **1** (see B1).
- `chain()` bench (verbatim copy, 2 s SIGALRM): missing parent `[1282]`; normal `[5,4,3]`; `start=1` `[]`; absent
  start `[]`; **2-cycle 500↔501 HANG**; **self-parent 600 HANG**.
- Live read-only `ps`: `7143←83977←83975←83953`, `7210←7143`, `7631/7632/7644←7210`, `16479←83977`,
  `83953←1282 (-zsh)`, `82301←1`. Lock: pid 83086, activation 784a764e, ACTIVE. 58633 argv ends
  `…/T/tmpondt32c8/bin/vllm serve …`.
- Epochs: 1788944160 = 2026-09-09 01:56:00 −07:00; 1788945300 = 02:15:00 (1140 s); 1788947760 = 02:56:00 =
  1788944160+3600 = 1788945300+2460. 1788877254 = 2026-09-08 07:20:54 −07:00. All 14 cited SHAs are commits.

## 1. Does step 4 implement the ruling, and nothing more?

(a) `me` from the lock: yes, matches the live lock — but nothing asserts the lock pid is an ancestor of the running
python (S3). (b) `mine()`: correct; `chain()` includes `p`, so `mine(me)` is True. (c) `eds_app()`: excludes any
process with an ancestor whose command starts with `/Applications/ChatGPT.app/Contents/MacOS/ChatGPT` — the whole
subtree, not the four helper shapes the ruling enumerates (S2). (d) regex: B1/B3/S1/N4 below.

## Blockers

**B1 — the prose misattributes seven live processes; the delta's own artifact refutes it.** 21b:304 says "Ed's
ChatGPT.app tree (pid 82301) present" and 21c's ruling-of-record calls the ChatGPT-pathed `codex app-server`,
`cua_node` and computer-use processes "pid 82301 tree … informational". Live ps *and the ppid column of
`pass3-standdown-census.txt` itself* show 7143/16479 ← **83977** and 7631/7632/7633/7634/7644 ← 7210 ← 7143 ←
83977 ← 83975 ← **83953**: children of the FOREIGN interactive Claude session, not of ChatGPT.app. So (bench M)
`eds_app()` is False for all of them and the census **aborts** on them — the opposite of what the prose tells the
next reader. A successor trusting the prose either mis-reads a failing census as clean, or "fixes" `eds_app()` by
path prefix and thereby excludes live children of a foreign Claude session. Cure: correct both sentences (they are
83953 descendants that merely live under ChatGPT.app paths, and they DO abort) and hold the ruling's exclusion to
the pid-82301 tree it actually names.

**B2 — the arm will abort on a condition nobody has asked Ed to clear.** pid 83953 (`claude`, ppid 1282 `-zsh`) is
alive now; it stood down logically, not as a process. At 01:56–02:15 PDT its tree (83953, 83975, 83977, 7631,
7632, 7644 …) is six-plus foreign session matches → rc=1 → no arm. The only ask sent to Ed (21b:308,
DURABLE-STATE:591, Gmail `1a0816757635cf98`) is "quit the ChatGPT desktop app" — by construction the one tree that
does NOT gate the arm. Cure: a line in 21b plus a follow-up on thread `1a0800cdb282c3f1` asking Ed to close the
joulewise-53 terminal before 01:56 PDT; the ChatGPT ask stays receipt-cosmetic.

**B3 — false PASS on `/Users/edr/.codex/…` argv (bench F, rc=0).** `(^|[\s/])` does not admit a `.` before the
keyword, so `…/cua_node/bin/node /Users/edr/.codex/plugins/cache/openai-bundled/unified-computer-use/…` is
classified informational. Today that is masked only because ancestor 83977 matches; when 83953's terminal closes,
node children of this shape routinely survive reparented to 1 — precisely tonight's configuration. With B1 the
census can print "clean" while a live plugin child of a dead codex session runs. Cure:
`AGENT = re.compile(r"(^|[\s/.])(codex|claude|t3)(?=$|[\s/.:-])")` — re-benched, 58633 stays informational
because its "t3" is preceded by `d`.

## Should-fix

**S1 — case-sensitivity misses T3 Code (bench E, rc=0).** Ed's own harness is T3 Code; `/Applications/T3 Code.app/…`
and `T3 Code` argv match neither this regex nor the production `pgrep -lf "codex|claude|t3"` (`night_gate.py:38`),
so a T3-hosted session is invisible to BOTH gates unless it spawns a lowercase `claude` child. Cure: `re.IGNORECASE`
here; record the production-gate hole as a limitation (that change is outside this delta).

**S2 — `eds_app()` is broader than the ruling.** The ruling excuses "idle helper processes … Codex Framework
helpers, codex app-server, SkyComputerUseService, cua_node"; the code excuses everything under ChatGPT.app,
including a *working* app-host Codex task — the documented `.codex-bridge/app-host-thread-id` route in CLAUDE.md,
whose tool calls appear as `/Applications/ChatGPT.app/Contents/Resources/codex sandbox …`. That is a live session
with repo write reach passing cond. 5. Cure: re-admit any excluded command containing ` sandbox ` or ` exec `.

**S3 — `me` is trusted, never verified.** A stale-and-recycled lock pid makes every descendant of an unrelated
process "mine" (fail-OPEN). Cure: `assert me in chain(os.getpid())` before classification.

**S4 — "handoff-daemons rc 0" asserted; this delta's artifact shows rc=1.** `pass3-standdown-census.txt` records
`ModuleNotFoundError: No module named 'joulewise'` / `handoff-daemons rc=1` from `/private/tmp/mag784`, while
21b:300 states "`handoff-daemons` rc 0". The rc 0 is joulewise-53's (commit 1e0a5593); this activation's own
preflight is broken for want of `PYTHONPATH`. Cure: attribute it and say the arming session cannot re-run it.

**S5 — F6 reversal undocumented.** 21c:~229 still reads "F6 → no allowlist … fail-closed" while delta 5
introduces exactly an allowlist. Cure: one clause pointing F6 at the cond.-5 ruling.

## Nits

- N1 `chain()` hangs forever on a ppid cycle/self-parent (benched). Unreachable from a real `ps`, but a hang inside
  a 19-minute window is a silent miss, not an abort. Cure: `seen` set or `for _ in range(64)`.
- N2 `"ps -axo" not in c` is redundant (the ps child is `mine()`) and fail-open — it drops a foreign session that
  is running its own census. Cure: delete the clause.
- N3 The pgrep output is printed to the tool shell only, though step 8 promises a recorded census artifact.
  Cure: `tee` both lists into `21b-rehearsal-20260909-bench/arm-census.txt`.
- N4 `codex_runner.py`, `t3code`, `/Applications/Claude.app/…` miss on boundary/case (bench L, K).
- N5 21b:238 "the only exclusion is Ed's ChatGPT.app process tree" is false: B3/S1/N4 are three more.

## 5. R4 / R1

R4: B1 is the R4 violation — the pid-82301 attribution is contradicted by the delta's own artifact. Also
untraceable: "they end when the terminal closes" (prediction); "a leaked fake `vllm serve` test server **from
09-04** whose temp path contains 't3'" — the artifact truncates 58633 at 90 chars, so neither the tmp path nor the
09-04 provenance appears in any cited artifact (I confirmed the path live; the date is still unsourced); Gmail
`1a0816757635cf98` and session id `018PXMANyqqMtpXYryP26pEm` are unverifiable from the repo (no `internalDate`,
unlike the pre-existing `1a080d1adf46c7b2` line at DURABLE-STATE:549). SHAs, PR numbers, epochs and the 1140 s
window all check out.

R1 violations in added lines: DURABLE-STATE "before 02:45 PDT 9 Sep" (line carries only the 16-hex Gmail id, not an
8-hex SHA/epoch/internalDate); 21b:308 "before 02:45 PDT"; 21c "at 02:56" and "before 02:45 PDT on 9 Sep". All four
are forward deadlines derived from t0, not asserted observations, and 21c transcribes the ruling — but none is
fenced or labelled a quote, so they fail the mechanical test. Cure: append the epoch (t0 = 1788947760; 02:45 =
t0−660) to each, or fence the 21c section as a quote. The two artifact lines pass.

## 6. Same-signature

The F6 signature ("no allowlist / fail-closed") is reversed here without amending F6 — the third rewrite of the
census exclusion policy (F3/F4 → F6 → delta 5), and B1/B3 are again *ancestry/argv-classification* defects, the
same class. Authorised by the ruling, so not itself the escalation trigger; but a fourth round on process
classification should be a consult, not another patch.

VERDICT: NOT LANDABLE — blockers B1 (prose misattributes 7143/7210/7631/7632/7633/7634/7644 to pid 82301 when the
delta's own artifact puts them under foreign session 83953), B2 (the arm predictably aborts on the still-live
83953 tree while the only ask to Ed targets the non-gating ChatGPT app), B3 (`.codex` dot-boundary false PASS on
process shapes present on this machine tonight).
