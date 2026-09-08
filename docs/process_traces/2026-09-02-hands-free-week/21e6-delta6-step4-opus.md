# Delta-6 fresh-eyes review — bookkeeping/2026-09-09-rehearsal-arm @ c93b475b (READ-ONLY, Opus)

Worktree /Users/edr/code/JouleWise-wt-magistrate-1ef89702. Cures under review: `f0ace25c` + `c93b475b`
(2 commits, 5 files, +214/-13). Nothing written outside this file; no git write, no signal, no process touched.

## Executed evidence (this session)

- `zsh -n` on all three ```zsh blocks (21b:79-121, 163-227, 245-300): rc 0 / 0 / 0. `compile()` on all four PY
  heredocs (21b:100-113, 189-208, 219-226, 257-288): OK. AGENT (21b:269) is defined before its first use
  (`under_session` 21b:271, `sessions` 21b:282) both lexically and at runtime.
- Step-4 PY extracted verbatim (21b:257-288) and `exec`'d with `json.load`/`open`/`subprocess.run` mocked and a
  reconstructed ps table. Reconstruction validated: on the pass3 table my run reproduces the committed
  `pass3-census-classified.txt` session set exactly (7143, 7631-7634, 7644, 7901, 16479, 83953, 83975, 83977).
- `chain()` re-benched verbatim (3 s SIGALRM): 2-cycle 500↔501 → `[500,501]`, self-parent 600 → `[600]`,
  normal `[5,4,3]`, `start=1` `[]`, absent `[]`. No hang (delta-5 N1 gone).
- Live read-only `ps -axo pid=,ppid=,command=`: `82301←1`; `82303←1` and `82305←1` are
  `…/Contents/Frameworks/Codex Framework.framework/Versions/152.0.7977.83/Helpers/browser_crashpad_handler`;
  `82362←82301` = `…/Contents/Resources/codex -c features.code_mode_host=true app-server`; `82551←82301` =
  `/Users/edr/.codex/computer-use/Codex Computer Use.app/…/SkyComputerUseService`; `7210←7143` = `…/cua_node/bin/node_repl`;
  `83953←1282` still ALIVE; `83075` = `python …/scripts/magistrate_watchdog.py` (no keyword — does not self-abort).

## 1. Delta-5 disposition

| item | verdict | evidence |
|---|---|---|
| B1 prose misattribution | CURED | 21b:312-314 + 21c:244-248 now name pid 83953; `pass3-census-classified.txt` ancestry section is the artifact. But see D6-1 — the new sentence over-corrects. |
| B2 nobody asked Ed to close 83953 | CURED (repo-side) | 21b:315, 00-DURABLE-STATE:589-591; Gmail `1a081723350aea55` is not verifiable from the repo (no internalDate quoted, unlike DURABLE-STATE:549). |
| B3 `.codex` dot-boundary false PASS | CURED, live-proved | 21b:269 `[\s/.]`; 7143/16479 now classify as sessions in `pass3-census-classified.txt` — that regex change is load-bearing for them. |
| S1 T3 case-insensitivity | CURED | 21b:269 and 281 both `(?i)`. Bench: `/Applications/T3 Code.app/Contents/MacOS/T3 Code --resume` → rc 1. Production `pgrep -lf "codex\|claude\|t3"` (night_gate.py:38) is still case-sensitive; still unrecorded as a limitation. |
| S2 `eds_app` breadth | NOT CURED (widened) | 21b:272-278 still excludes the whole 82301 subtree, and now additionally any process whose own argv starts with `Contents/Frameworks/` regardless of ancestry. Bench Case 4 below. |
| S3 me-ancestry assert | CURED | 21b:267; bench Case 12 → `AssertionError` → non-zero exit → the `||` ABORT fires. |
| S4 handoff-daemons attribution | CURED | 21b:316-317 attributes rc 0 to joulewise-53 and records the ModuleNotFoundError. "wrong cwd" is an unsourced causal claim (the traceback shows only a failed `joulewise` import). |
| S5 F6 "no allowlist" line | NOT CURED | 21c:227 still reads `F6 → no allowlist`, while 21b:270-278 is a two-branch path allowlist. |
| N1 `chain()` cycle | CURED | 21b:265, benched above. |
| N5 21b:238 "the only exclusion is Ed's ChatGPT.app process tree" | NOT CURED, now more wrong | the second exclusion branch (`Contents/Frameworks/` orphans, any tree) is not covered by that sentence; it is operator-facing paste text. |
| N2 `"ps -axo" not in c` / N3 tee census to artifact | NOT CURED | bench Case 8: a foreign shell running `ps -axo … \| grep claude` is dropped from `hits` entirely. Step 8 still relies on manual capture of the printed lists. |

## 2. Attacking the classifier

(a) **False PASS shapes** (rc 0 with a real agent present). Benched:
- **Case 4 — a WORKING app-host Codex task under 82301 → rc 0.** `…/Contents/Resources/codex sandbox -- /bin/bash -lc git -C /Users/edr/code/JouleWise commit …` with ppid 82301 is classified *informational*. This is the documented `.codex-bridge/app-host-thread-id` route in CLAUDE.md, and pid 82362 (`code_mode_host … app-server`) is that route's live host right now. The ruling excuses "**idle** helper processes"; a working task is not idle, and the code cannot tell them apart. Ruling-covered, so not a landing blocker, but it is the hole and it is undocumented.
- **Case 10 — orphaned `cua_node` worker with a non-`claude` workdir → rc 0.** `…/Resources/cua_node/bin/node --experimental-vm-modules /var/folders/…/kernel.js --session-id … --working-dir /Users/edr/code/JouleWise` matches neither AGENT nor the coarse `hits` filter. Today's 7633/7634 are caught only incidentally, by `/private/tmp/claude-501/…` appearing in their `--working-dir`.
- Case 11 — a `Contents/Frameworks/` orphan passes even with **no ChatGPT main running at all**; the exclusion is unconditional on the app being alive.
- Correctly ABORTing (rc 1, benched): bare `claude`; `/Users/edr/.local/share/claude/ClaudeCode.app/Contents/MacOS/claude`; orphaned `bash …/codex-run-v3 …` + `codex exec`; `node scripts/claude-bridge-mcp.mjs`; `/Applications/T3 Code.app/…`. The tmp `…/T/tmpondt32c8/bin/vllm` stub stays informational.
- Residual (not benchable here): `mine()` drops the arming session's **own** Codex children (83123/83143) from `hits` entirely, so a skipped step 3b is invisible to the census; if any survive the session's exit reparented to 1, nothing sees them until the 02:56 gate turns the rehearsal into `night_refused_agent_present`.

(b) **False ABORT shapes outside the ruling.** Benched:
- **Case 3 — orphaned `/Applications/ChatGPT.app/Contents/Resources/codex app-server --listen stdio://` (ppid 1) → rc 1**, printed as a foreign session.
- **Case 3b — orphaned `/Users/edr/.codex/computer-use/Codex Computer Use.app/…/SkyComputerUseService` (ppid 1) → rc 1.**
  Both are named verbatim in the ruling's own enumeration of Ed's helpers (21c:236-237), so treating them as sessions contradicts "Do not hold the arm for the ChatGPT helpers alone" (21c:242).
  **Which ChatGPT-pathed processes are reparented today, from the artifacts:** `pass3-census-classified.txt` ancestry section — `82303 chain: [82303]` and `82305 chain: [82305]` (chain of length 1 ⇒ ppid 1; live: both `browser_crashpad_handler` under `Contents/Frameworks/`). **Every other** ChatGPT-pathed process in that section ends at 82301 (`82316/82317/82318/82354/82362/82386/82387/82551/83044/83054 chain: [pid, 82301]`). So the `Contents/Frameworks/` prefix cure covers exactly the one orphan shape observed, and leaves the two adjacent shapes fail-closed.
  **Acceptability:** fail-closed here is defensible in the abstract (the same argv is genuinely ambiguous between Ed's helper and an ex-agent child — 7631/7632/7644 are that same `Resources/codex …` shape under 83953), but it is *operationally* material tonight: Ed has been asked to close the joulewise-53 terminal before 1788944160 **and** to quit the ChatGPT app before 1788947100. He will plausibly do both in one sitting before the window; if the quit leaves any `Resources/`- or `~/.codex/computer-use`-pathed orphan, the one-shot 01:56–02:15 window is spent on an abort. Untested — no artifact shows what survives a quit.

## 3. Bench results (mocked lock=83086, ps, pgrep; own pid injected under 15932)

- **Case 1, exact pass3 table → rc 1.** sessions = `[83953, 83975, 83977, 7143, 16479, 7901, 7631, 7632, 7633, 7634, 7644]`; informational = `[82303, 82305, 82316, 82317, 82318, 82386, 82387, 83044, 83054, 82362, 82551, 58633]`. Identical to the committed artifact.
- **Case 2, 83953 and all descendants removed → rc 0.** sessions = `[]`; informational = the same 12 minus the 83953 tree. The ruling holds: with the interactive session gone, Ed's app alone does not hold the arm.
- **Case 3, Ed's app + orphaned `Contents/Resources/codex app-server` (ppid 1) → rc 1.** sessions = `[(9001, '/Applications/ChatGPT.app/Contents/Resources/codex app-server --listen stdio://')]`; informational = the 11 app processes. (Case 3b, orphaned SkyComputerUseService: rc 1, sessions = `[(9002, '…/Codex Computer Use.app/Contents/MacOS/SkyComputerUseService')]`.)

## 4. Syntax — see Executed evidence. All blocks parse; all heredocs compile; AGENT precedes first use.

## 5. R1 / R4 on the added prose

R1: clean. Every added typed HH:MM carries a same-line token — 21b:320 `02:45 PDT = epoch 1788947100`, 21c:239 `02:56 (t0 1788947760)`, 21c:241 `02:45 PDT (epoch 1788947100)`, 00-DURABLE-STATE:589 `before the belt, epoch 1788947100`; 21b:315 uses the bare epoch 1788944160. Belt 02:45 is corroborated at 21b:121. (The custodied review file 21e5 contains bare `01:56–02:15 PDT` / `before 01:56 PDT`; verbatim custody of an external report, out of scope, but it is the one R1-dirty added text.)

R4: two problems.
- **D6-1 (blocker).** 21b:312-314 and 21c:244-246 assert that "the ChatGPT-pathed `codex app-server` / `cua_node` / computer-use processes … were descendants of … pid 83953, **NOT** of Ed's ChatGPT.app pid 82301". The cited artifact refutes it for two of the three named shapes: `82362 chain: [82362, 82301]` is a ChatGPT-pathed `codex … app-server`, and `82551 chain: [82551, 82301]` is the computer-use service — both sit in that same artifact's *informational* list, and both are named in the ruling paragraph immediately above (21c:236-237) as the 82301 tree. The corrected sentence therefore contradicts the ruling it appends to, in the same class of defect as the B1 it cures (prose attributing processes to the wrong tree), and it points a successor at exactly the wrong repair — excluding `Resources/`-pathed processes by path, which is the Case-4 false-PASS hole.
- Unsourced/uncorroborated: Gmail `1a081723350aea55` and `1a0816757635cf98` (no internalDate quoted; not checkable from the repo); "ran from the wrong cwd" (21b:316) is an inference, the artifact shows only the failed import; and the commit message of `c93b475b` claims "bench 6 cases" while the commit adds no bench artifact — delta 3 recorded its benches in `pass3-lead-benches.txt`, delta 5 in 21e5, this round nowhere.

## 6. Same-signature and new defects

**Same signature, fired twice.** (i) Process classification is now on its **fourth** round — F3/F4 → F6 → delta-5 regex → delta-6 path rule — and delta 5 wrote in terms: "a fourth round on process classification should be a consult, not another patch." It was patched. This round finds two new false-PASS shapes (Cases 4, 10) and two new false-ABORT shapes (Cases 3, 3b), i.e. the round did not converge the class. (ii) The prose-attribution defect (B1) recurs immediately as D6-1. Per the standing escalation trigger the next classification change is a cold-gate consult, not delta 7 — and the structural point for that consult is that "is this argv an agent session" is undecidable when Ed's app and the agents ship the same `codex` binary under the same paths; the reliable gate is a precondition (app quit, then require **zero** foreign matches), not a shape allowlist.

New defects, severity + one-line cure:
- **D6-1 (blocker)** 21b:312-314 / 21c:244-246 over-correct: 82362 and 82551 are Ed's app's. Cure: "the ChatGPT-pathed processes in the SESSIONS list (7143/7631/7632/7633/7634/7644/16479) are 83953 descendants; the identically-shaped `codex app-server` 82362 and computer-use 82551 in the informational list are Ed's app's (ppid 82301)."
- **D6-2 (should-fix)** early app quit can orphan `Resources/`- or `~/.codex/computer-use`-pathed helpers and abort the one-shot window (Cases 3/3b). Cure: one line on thread `1a0800cdb282c3f1` asking Ed to quit the ChatGPT app **after 1788945300 and before 1788947100**, not before the window.
- **D6-3 (should-fix)** app-host WORKING Codex task passes cond. 5 (Case 4). Cure: record it in 21b as a named limitation of the ruling's exclusion, with the argv shape, and let the 02:56 gate catch it.
- **D6-4 (should-fix)** "bench 6 cases" claimed with no artifact. Cure: append the case list and rc output to `21b-rehearsal-20260909-bench/`.
- **D6-5 (should-fix)** 21c:227 `F6 → no allowlist` vs the two-branch allowlist now in step 4; 21b:238 "the only exclusion is Ed's ChatGPT.app process tree" omits the Frameworks-orphan branch. Cure: one clause in each pointing at the cond.-5 ruling and naming both branches.
- **D6-6 (nit)** the printed label "informational matches (Ed's ChatGPT.app tree / …)" is inaccurate for 82303/82305, which are in no tree. Cure: "(Ed's ChatGPT.app tree and its reparented Electron helpers / substring false positives)".
- **D6-7 (nit)** `"ps -axo" not in c` (21b:281) still drops a foreign session running its own census; the census output is still printed only, not tee'd to the artifact step 8 promises.

VERDICT: NOT LANDABLE — one blocker, D6-1 (21b:312-314 and the 21c:244-246 ruling appendix assert the ChatGPT-pathed `codex app-server` / computer-use processes are pid 83953's, when the cited artifact shows 82362 and 82551 under Ed's app 82301 — the same prose-vs-artifact class as the B1 it cures, and it aims a successor at the Case-4 false-PASS repair). The code itself is correct on the live table (Case 1 rc 1 reproduces the committed artifact; Case 2 rc 0), B1/B2/B3/S1/S3/S4/N1 are cured, and D6-1 is a one-sentence bench fix; D6-2 (email timing) should ride with it before the 01:56 window.
