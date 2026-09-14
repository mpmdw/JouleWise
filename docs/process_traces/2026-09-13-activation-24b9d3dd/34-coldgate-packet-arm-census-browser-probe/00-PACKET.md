# Cold-gate packet — ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01: the arm-time process census refuses on macOS's own services (browser AND monitor classes); rule the cure (ruling-first lane; rule 11: the magistrate does not change a gate rule at the desk)

Assembled 2026-09-13 ~08:50 PDT by the resident magistrate (activation 24b9d3dd). Mechanically assembled: every exhibit is a verbatim `sed`/`rg`/`git` extract at main `4b9a3411` or a read-only live probe on this machine; the magistrate wrote only this file and the one labelled note at the end of Exhibit C.

## What was found

The arm-readiness evidence row `t0.no_stray_keepawake` (kind `PROCESS_CENSUS`; Exhibit A `_derive_process_census`) runs four fresh `pgrep` probes and refuses — `_expect_absent` raises `_underivable` — unless EACH exits 1 with empty output: keep-awake `pgrep -x caffeinate`; agent `pgrep -lf "codex|claude|t3"`; browser `pgrep -lf "Safari|Google Chrome|Chromium|Firefox|browser automation"`; monitor `pgrep -lf "powermetrics|window-chain|run_campaign|tail -f|watch"`. The row is `ALWAYS`-applicable and required by every plan profile (Exhibit B, registry). It is evaluated at a `TRANSACTION_PACK` night's t0 (Exhibit B, `scripts/run_night.py` `is_pack` branch) and by the desk tool `scripts/author_arm_evidence_t0.py`; `DIAGNOSTIC_NO_PACK` and `REHEARSAL_STUB` nights never reach it.

Live on this machine today (Exhibit C, pgrep's own exit codes): the BROWSER probe matches eight Apple system services that exist on every macOS login with no browser open (`SafariBookmarksSyncAgent`, `SafariWidgetExtension`, `SafariLinkExtension`, two `SafariPlatformSupport` XPC helpers, `CredentialProviderExtensionHelper`, `com.apple.Safari.SafeBrowsing.Service`, `SafariLaunchAgent`, `SafariConfigurationSubscriber`) — and, correctly, the operator's open Firefox. The MONITOR probe matches `/usr/libexec/watchdogd` (pid 574, root, a launchd child) through the token `watch`. Keep-awake is clean (exit 1). So on this macOS the row can NEVER pass: the first `TRANSACTION_PACK` arm refuses at the desk and at t0 regardless of what the operator does. The patterns entered on 2026-08-14 (Exhibit F); the 08-23 coverage table documents them; whether any earlier estate exercised the real probes on this row, or only mocked them, is Q2.

Facts the packet holds: `_fresh_probe` (Exhibit A) executes the argv as given after the R1 clock batch; there is no ancestry, owner or bundle classification anywhere in the row. The night gate's t0 agent census (`joulewise/night_gate.py`) is a different code path with only the agent pattern, ruled on 2026-09-13 (packet 05) and NOT in question here.

## Q1 — the cure for the browser and monitor classes (rule one option per class, or write a better one)

- (i) Narrow the patterns to the top-level browser executables: match `comm` (the executable name) exactly — `Safari`, `Google Chrome`, `Chromium`, `firefox`/`Firefox` — with `pgrep -x` (or `-lf` anchored to `/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)$`), so helpers and XPC services no longer match; for the monitor class drop the bare token `watch` (keep `powermetrics|window-chain|run_campaign|tail -f`) or anchor it as `(^|/)watch($| )`.
- (ii) Keep the patterns and post-filter hits by OWNER and PARENT: a hit whose user is `root` or whose parent is launchd (ppid 1) and whose path is under `/System/`, `/usr/libexec/` or `/System/Cryptexes/` is a system service and is ignored; anything under `/Applications/` or owned by the login user refuses.
- (iii) Keep the patterns and post-filter by BUNDLE: ignore hits whose executable path is inside a `.xpc`, `.appex` or `/System/…` bundle; refuse any other hit.
- (iv) Other, with the same burden: the ruled probe must refuse on a real running browser (the Firefox lines in Exhibit C) and on a real `powermetrics`/`tail -f`/`watch` monitor, and must NOT refuse on the nine system-service lines in Exhibit C.

Deliver: the ruled option per class; the exact new argv or filter (code-level, at the level a seat can implement from it: which function, what the emitted row's `derived` fields say so the evidence stays auditable — the row must still record what was seen); and the reason. If the ruling changes the emitted row's shape or the registry's `required_row_ids`, say so explicitly (that is a contract change and pairs refuters).

## Q2 — for the record: how did earlier estates pass this row?

Exhibit F lists the August records that mention a passing process census and the tests that touch `_fresh_probe`/`_execute_probe`. Was the real `pgrep` ever executed for this row on this Mac before today, or did every estate and test mock the probe? One paragraph with the deciding line (a test that patches `_execute_probe`; or a record showing a real refusal or pass). If the row never executed for real, say what that implies for the "eleven-kind census PASS" claim of the S-0 clone proof (a limitation to record, not a re-litigation).

## Q3 — the regression specification

Specify the defect-shaped regression(s) a seat must add beside the existing tests in Exhibit D: (a) the recorded system-service argv lines of Exhibit C (all nine, plus `watchdogd`) fed through the ruled probe/filter must NOT refuse; (b) the recorded Firefox top-level line and a `powermetrics` line MUST refuse; (c) the counterfactual each kills (name the mutation: e.g. reverting the pattern, dropping the filter, widening `watch`). State whether the desk proof `scripts/author_arm_evidence_t0.py` on this machine with no browser open must be part of acceptance (the kernel row says yes).

## Constraints on the judge

Read-only. Probes allowed: `git show 4b9a3411:<path>`, `rg`/`grep`, `sed -n`, read-only `pgrep`/`ps` on this machine (you may run the four patterns and your candidate patterns live; never signal any process), single test modules under `/tmp` copies. Do not edit any tracked file. Never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` may be used read-only), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (per class: ruled option, exact argv/filter, reason; contract-change statement); Q2; Q3 (regression spec in a fenced block); Executed probes. Plain words; define each term at first use.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
a12c8847da70b72e791cfb9dde20c413c7e23ab35d096c3dd9596b03868efd77  exhibit-A-process-census-code.md
7d953a54f50909bf222d8545983a1e60086608a727fcbb74b8bee6a51c8f0cb2  exhibit-B-evaluation-sites.md
9cc140018e34732b2769bc1cfa298334c30fd8033a3d6ce8a34e76f82613263e  exhibit-C-live-probes.md
12f536db03689eb72757058ac287b879a7e00065a10ca37013643dde55a0e438  exhibit-D-tests.md
9211aa22700457e8c52123837af9086686b58ab864dfcc81750eeb38186f6323  exhibit-E-governing-text.md
bd6e412084fce5e37676629148f53583e631705769259ee32c08dfc4b58b1f64  exhibit-F-prior-records.md
```
