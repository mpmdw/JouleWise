# Cold-gate ruling — NIGHT-CENSUS-CHATGPT-APP-01

Judge: cold Fable 5.1 session, 2026-09-13, worktree `JouleWise-wt-coldgate-census` at main `27957b60`. Read-only; no tracked file edited. Validator: first run (typo'd charter sha) returned `REFUSE` / `charter_trusted_observed_mismatch`, rc 2; second run with the correct charter sha returned `PASS`, rc 0, all seven exhibit digests matching the manifest.

## Contamination disclosure

Auto-loaded before I chose anything: `/Users/edr/.claude/CLAUDE.md` (global rules), the worktree `CLAUDE.md` (Codex bridge notes), and the memory index `MEMORY.md`. The index carries one-line checkpoint summaries, including one that says the 09-13 night was refused at t0 on "Ed's interactive session pid 24974 + ChatGPT app helper in the census" and that a successor plan exists for 09-15. I opened no memory file, no `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/decision_log.md`, and no process trace outside the packet directory. The convening prompt itself also summarised the situation. Two probe accidents: the packet-allowed `osascript` login-items query hung on a headless AppleEvent and the harness moved my probe chain to the background on its own (it completed; I ran no subagent and started no task deliberately); and the live `pgrep` printed the argv of unrelated running Codex seats (a PR #329 review brief), which I read incidentally and do not use.

## Q1 — ruled: option (i), KEEP the pattern, with the app named in text and pinned by one test

Ruled option: **(i)**, strengthened. No production code changes. The runbook, the NIGHT_HANDBACK notice template and the arm-time census description each gain the sentence below, and one defect-shaped test pins the fact that the app's Codex server is an agent process, so nobody can later narrow the pattern "as a tidy-up" without a ruling.

Exact text for `docs/phase_2/derivation_night_runbook.md` §0.6, inserted after "`[QUIET-MAC]` nights are agent-free.":

```
Desktop apps that bundle an agent runtime count as agents. The ChatGPT desktop
app (`/Applications/ChatGPT.app`) runs the Codex CLI as an app server (`codex
… app-server`) and the Claude desktop app (`/Applications/Claude.app`) runs
`Claude Helper` processes; both match the census and both are quit by the
operator before the plan span and stay quit through t0. An app started after
the arm reaches t0 and refuses the night; that refusal is correct.
```

Exact text for the NIGHT_HANDBACK notice template (the "Precondition that only the operator can meet" sentence), replacing "no interactive agent session and no ChatGPT desktop app alive":

```
no interactive agent session, no ChatGPT desktop app and no Claude desktop
app alive (quit both from their menu bar; a running app refuses the night)
```

Exact text for the arm-time census description in `docs/phase_2/derivation_night_runbook.md` (the paragraph beginning "Before the arm census"), one added sentence after "abort the arm; do not signal them.":

```
The agent probe also matches the ChatGPT and Claude desktop apps by design;
the desk asks the operator to quit them and never narrows the pattern.
```

Regression specification, one test added to `tests/test_night_gate.py` beside `test_a_census_that_finds_lines_refuses_and_preserves_them`, using the file's existing `FakeProbeSource` and `result` helpers. The counterfactual it kills: a future edit that excludes `/Applications/ChatGPT.app/` argv (option ii) or otherwise narrows the literal.

```python
def test_a_desktop_app_bundled_agent_server_refuses_the_census(self) -> None:
    # Ruling 2026-09-13 (NIGHT-CENSUS-CHATGPT-APP-01): the ChatGPT app's
    # bundled Codex CLI is an agent process; the pattern is not narrowed.
    source = FakeProbeSource()
    source.results[night_gate.AGENT_CENSUS_ARGV] = result(
        night_gate.AGENT_CENSUS_ARGV,
        exit_code=0,
        stdout=(
            "25658 /Applications/ChatGPT.app/Contents/Resources/codex "
            "-c features.code_mode_host=true app-server\n"
        ),
    )
    _, refusal = night_gate.agent_census(source.probes())
    self.assertEqual("night_refused_agent_present", refusal.reason)
    self.assertIn("25658 /Applications/ChatGPT.app", refusal.detail)
    self.assertEqual(("/usr/bin/pgrep", "-lf", "codex|claude|t3"), night_gate.AGENT_CENSUS_ARGV)
```

Reason. The census exists for one thing, in the contract's words: "the governed agent census, a process-list check for agent presence" (Exhibit D). The question is therefore whether pid 25658 is an agent, not whether its match is a lucky substring. It is an agent: its argv is the Codex CLI binary itself, running as `app-server` with a code-mode host enabled (Exhibit F), and through it the app executes local turns that run shell commands and edit files on this machine. That is the same capability as `codex mcp-server`, which nobody proposes to exempt. Option (ii) would exclude exactly the process the census is for, on the ground that it lives under `/Applications`; that is convenience overriding purpose. The renderer and service helpers are incidental Chromium processes, but they are also an unmeasured background load of six or more processes during a capture that the night's quietness rule (`[QUIET-MAC]` nights are agent-free, runbook §0.6) already forbids, so exempting them buys nothing either. My live probe adds a fact the packet did not have: the Claude desktop app's helpers (`Claude Helper`, `Claude Helper (Renderer)`) and a `Codex Computer Use` service also match the pattern today. The Claude app can drive local agent work as well, so the same reasoning covers it; the sentence names both apps rather than one. Option (iii) is not needed: the arm-time probe uses the same literal and already refuses on the app (Exhibit B), so a by-name class would only relabel a refusal that already happens; the sentence in the census description gives the operator the name without a code change. The ruling does not depend on whether the app auto-launches at login: the operator instruction covers both cases (quit it, and if it is a login item, remove it from System Settings > General > Login Items before the plan span), and nights do not log the user in between arm and t0. The deciding probe, if anyone wants the fact on record, is the packet's own `osascript -e 'tell application "System Events" to get the name of every login item'`, run from an interactive session where System Events automation is already permitted; run headless it times out (AppleEvent error -1712, see Executed probes), so it is not a fact this judge could establish.

## Q2 — one definition or several

A single shared constant is a follow-up nit, not part of installing Q1, because this ruling changes no pattern: the desk and t0 literals are identical today, both are pinned by their own tests (`tests/test_night_gate.py:298`, `tests/test_arm_readiness_evidence_t0.py:2509`), and the new test above pins the t0 literal a second time, so drift would be caught before it reached a night. The rehearsal token regex at `joulewise/t0_rehearsal.py:52` is a different matcher but I checked it against the app-server argv by hand: `/codex ` and ` Codex (Service)` both satisfy its boundary rule under case-insensitive matching, so it agrees for this case too. Fold the constant into whatever next PR touches `night_gate.py`.

## Q3 — was the 09-13 refusal correct

Yes. Deciding line: `joulewise/night_gate.py` `agent_census` returns `Refusal("night_refused_agent_present", …)` on any census line, and the first line it saw was `24974 claude`, Ed's interactive session, with its two `codex mcp-server` children beside it (Exhibit C, `refusal.json`). Under runbook §0.6, "`[QUIET-MAC]` nights are agent-free", that alone is a correct refusal; the ChatGPT app is not needed to decide this question, and under Q1 it would have been a correct refusal on its own as well. A fence doing its job, not a defect.

## Executed probes

Validator, typo sha (expected refusal): `python3 scripts/validate_gate_packet.py --packet …/00-PACKET.md --charter docs/process/coldgate_charter.md --expected-charter-sha256 099de884…a880ff8c… --expected-packet-sha256 a815c147…` → `"reason":"charter_trusted_observed_mismatch","result":"REFUSE"`, rc=2.

Validator, correct sha: same argv with `…a870ff8c…` → `"result":"PASS"`, rc=0; seven exhibits, each `observed_sha256` equal to `expected_sha256`; `exhibit_manifest_sha256` d0f8cf7e….

`shasum -a 256 docs/process/coldgate_charter.md …/00-PACKET.md` → `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` and `a815c147a22536cc67933a5813f8b22da672c9c38954e29d0f09f13691e43734`, matching the convening prompt's pins.

`ls -la` of the packet directory → 00-PACKET.md plus exhibits A–G, sizes 1607–33949 bytes; `cat` of 00-PACKET.md and all seven exhibits.

`osascript -e 'tell application "System Events" to get the name of every login item'` → `44:48: execution error: System Events got an error: AppleEvent timed out. (-1712)`, rc=1 (after ~120 s; harness backgrounded the chain).

`/usr/bin/pgrep -lf "codex|claude|t3"` at ~07:05 PDT → rc=0; hits included `24974 claude`, four `codex mcp-server` pairs (24488/24507, 24994/24996, 31413/31422), the ChatGPT app processes 25641, 25643, 25658 (`…/Resources/codex -c features.code_mode_host=true app-server …`), 25661, 25662, 25859, 25868, 25871, 25872, plus `25716 …/Codex Computer Use.app/…/SkyComputerUseService`, `29816/29862/29863 …/Claude.app/…/Claude Helper --type=utility`, `29828/29835/29861 … Claude Helper (Renderer)`, `30091 … ShipIt com.anthropic.claudefordesktop…`, two `codex-run-v3` review seats and one `codex exec -m gpt-6-astra`.

`ps -axo pid,ppid,comm | grep ChatGPT.app/Contents/MacOS/ChatGPT$` → `25633     1 /Applications/ChatGPT.app/Contents/MacOS/ChatGPT` (parent is launchd, as for any GUI app; does not decide login-item status).

`git show 27957b60:docs/phase_2/derivation_night_runbook.md | sed -n '582,586p'` → §0.6 heading and "`[QUIET-MAC]` nights are agent-free…"; `| grep -n -iE ChatGPT` → no lines (the runbook does not name the app).

`git show 27957b60:docs/process/NIGHT_HANDBACK.md | grep -n -iE 'ChatGPT|quit the'` → lines 46, 49, 198; `sed -n '40,52p'` → the successor notice's "Precondition that only the operator can meet: no interactive agent session and no ChatGPT desktop app alive from the plan span (02:31 PDT on 2026-09-15) through t0."

`git show 27957b60:joulewise/night_gate.py | grep -n -E 'agent_census\(|AGENT_CENSUS_ARGV'` → lines 42, 498, 500, 508, 1033. `git show 27957b60:joulewise/t0_rehearsal.py | grep -n _AGENT_TOKEN_RE` → lines 52, 906 (`_AGENT_TOKEN_RE.search(" ".join(argv))`).

`git show 27957b60:tests/test_night_gate.py | grep -n -E '^def result|^class '` → `23:def result(`, `61:class FakeProbeSource:` (the helpers the regression uses).

`/usr/bin/pgrep -lf "Safari|Google Chrome|Chromium|Firefox|browser automation"` (the arm-time "browser" probe) → rc=0 with Firefox 24781 and its helpers, and ten always-present Safari system services (`SafariBookmarksSyncAgent`, `SafariPlatformSupport` XPC services, `SafariLaunchAgent`). Observation only, outside Q1–Q3: on this macOS the browser class matches system daemons even with no browser open, which is a separate lane for the magistrate to register if the arm-time `_expect_absent` is really applied to that probe.

Not executed: nothing in the packet's question set was left unexecuted; the login-item fact is undetermined for the reason given.
