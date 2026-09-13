# Cold-gate packet — NIGHT-CENSUS-CHATGPT-APP-01: does the night's t0 agent census keep refusing on the ChatGPT desktop app's Codex helper? (ruling-first lane; rule 11: the magistrate does not change a gate rule at the desk)

Assembled 2026-09-13 ~06:50 PDT by the resident magistrate (activation 24b9d3dd). Mechanically assembled: every exhibit is a verbatim `git show`/`sed`/`rg` extract at main `27957b60`, a read-only copy of the refused night's record, or this machine's process list; the magistrate wrote only this file.

## What happened

The equivalence night `d079-epoch-25g83-derivation-n1-20260913` fired at 02:56:02 PDT on 2026-09-13 from its frozen clone and was REFUSED in 89 ms by the night gate's t0 agent census (Exhibit C). The census is one command, `/usr/bin/pgrep -lf "codex|claude|t3"` (Exhibit A, `AGENT_CENSUS_ARGV`); any match refuses with `night_refused_agent_present`. It matched three kinds of process: (1) Ed's interactive `claude` session pid 24974 and (2) its two `codex mcp-server` children — both plainly agent processes — and (3) six helper processes of the ChatGPT desktop app (`/Applications/ChatGPT.app/…/Codex (Service)`, `Codex (Renderer)`, and `/Applications/ChatGPT.app/Contents/Resources/codex … app-server`), which match because the word `codex` is in their paths (Exhibit F has the argv; pid 25658 is the bundled Codex CLI binary running as the app's server). The night captured nothing; it was re-planned for 09-15. The harvest record registered this lane (Exhibit C, F2; Exhibit D, kernel row): "either the app is quit for every night … or the pattern is narrowed under a ruling".

Two facts the packet holds and the judge should weigh:
- The same literal pattern is the "agent" probe of the ARM-TIME process census at the desk (Exhibit B, `_derive_process_census`), which refuses the arm on any match. The arm record of 09-12 (recorded in the kernel row's second evidence line) shows the arm-time census classifying hits by process ancestry — own (this activation's MCP server) versus foreign — while the t0 census in `night_gate.py` has no such classification: any match refuses.
- Pid 25658's argv is `codex -c features.code_mode_host=true app-server …`: the Codex CLI binary bundled inside the ChatGPT app, running as an app server. When the operator uses the app's Codex feature it executes local agent turns (shell, file edits, workloads) on this machine. Its renderer/service helpers are Chromium-class processes (`--type=renderer`, `--type=utility`).
- The 09-08 arm notice already asked Ed to quit the app before nights; the notice template and runbook §0.6 (Exhibit D) do not name it explicitly.

## Q1 — what the t0 agent census does from now on (rule one option, or write a better one)

- (i) KEEP the pattern unchanged. The ChatGPT desktop app becomes an operator-closed process for every armed night: runbook §0.6, the NIGHT_HANDBACK notice template and the arm-time census description gain one explicit sentence naming the app, so the desk refuses the arm while the app runs and only an app started after the arm can reach t0. No code change; a documentation and notice-text install.
- (ii) NARROW the t0 pattern so that processes whose argv begins `/Applications/ChatGPT.app/` are excluded, with a defect-shaped regression that still refuses `claude`, `codex mcp-server`, `codex exec` and `t3` processes (Exhibit E shows the existing tests' shape). The app's helpers would then be an unmeasured background load during captures.
- (iii) KEEP the pattern AND add the app to the arm-time census by name (its own class or the "browser" class, Exhibit B), plus (i)'s text — so the desk refuses the arm on the app by name rather than by the accidental `codex` substring.

Deliver: the ruled option (or a better one); the EXACT sentence(s) for the runbook/notice, or the exact code change and regression specification, in fenced blocks; and the one-paragraph reason grounded in what the census is FOR — Exhibit D's contract sentence ("the governed agent census, a process-list check for agent presence") and the night's quietness requirement — not in convenience. If the ruling depends on whether the app auto-launches at login, say so and state the probe that decides it.

## Q2 — one definition or several (for the record; code shape, not doctrine)

The pattern literal appears at `joulewise/night_gate.py:42`, `joulewise/arm_readiness_evidence_t0.py:1724`, as a token regex at `joulewise/t0_rehearsal.py:52`, wider in `scripts/prewindow_check.sh:149`, and in prose (Exhibit G). Is a single shared constant (so the desk and t0 cannot drift apart after this ruling) a REQUIRED part of installing Q1, or a follow-up nit? One sentence and the reason.

## Q3 — was the 09-13 refusal correct (for the record)

Under the text in force at `27957b60`, was refusing a correct outcome (a fence doing its job) rather than a defect? Yes/no with the deciding line.

## Constraints on the judge

Read-only. Probes allowed: `git show 27957b60:<path>`, `grep`/`rg`, `sed -n`, `ps`/`pgrep` reads, and the read-only login-items query `osascript -e 'tell application "System Events" to get the name of every login item'`. Do not edit any tracked file. Never touch `/Users/edr/code/JouleWise`, any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody` (Exhibit C is the copy you read). Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (ruled option; exact text/code in fenced blocks; the reason); Q2; Q3; Executed probes (commands and the lines they returned). Plain words; define each term at first use.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
d19e8dff435a51eec7079ce7e02c9185630236749d44138ba904a522a0bab048  exhibit-A-night_gate-agent_census.md
3403e77cc9a056be6cf9dea93a5192a32975bbf0a4b86d548f868c981b50c0d9  exhibit-B-arm_readiness-process-census.md
8a554299453a1fdb466c9c928701e920f684041f7dd5d8fe448eebb612d42b22  exhibit-C-refused-night-record.md
90128d55b970a276cbacfcfb98fa8c11745c2e75072172ebb07164ce232c208a  exhibit-D-governing-text.md
9e85be3666a25211c641a726ea47efbb2bd3dff76a62383aec267f1096731e8a  exhibit-E-existing-tests.md
aa7e0c9327d7abb73163102a662f5b1e5bdca2cafc246d8959ecb6cab1d82bfe  exhibit-F-process-list.md
96fc832477f3838a5d2d4cb160fef39b28870fe36c59b5b945492e7f665e9f60  exhibit-G-pattern-sites.md
```
