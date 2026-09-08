# Delta-7 light review — bookkeeping/2026-09-09-rehearsal-arm @ c6d64665 (READ-ONLY, Opus)

Scope: `git diff c93b475b..c6d64665` only. Nothing written outside this file; no git writes; `~/night-custody` untouched.

## 0. Classifier-unchanged confirmation (required)
- `git diff c93b475b..c6d64665 -- …/21b-rehearsal-20260909-arm-plan.md | grep -c '^[-+].*def '` → **0**.
- Extracted the fenced block containing `def chain` from both `git show`n copies (3 fences each, 1 match each):
  `diff /tmp/py-c93b475b.txt /tmp/py-c6d64665.txt` → **no output, 55 lines, IDENTICAL**. (Naive line-window
  extraction shows a 3-line shift only; the block itself is byte-identical.) Code is unchanged; this delta is prose + artifacts.

## 1. Pid / tree-membership claims vs `pass3-census-classified.txt` (all paths under docs/process_traces/2026-09-02-hands-free-week/)
| Claim (21b:315-317, 21c:246-249) | Verdict | Artifact line |
|---|---|---|
| 7143 → 83953 | TRUE | classified:37 `7143 chain: [7143, 83977, 83975, 83953, …]` |
| 7631, 7632, 7633, 7634, 7644 → 83953 | TRUE | classified:39-43 |
| the written range **"7631–7644"** | **FALSE as written** | only 7631/7632/7633/7634/7644 have chains; 7635–7643 appear nowhere in the artifact. The dash asserts 9 pids that were never observed. |
| 7901 → 83953 | **NOT SUPPORTED by the cited artifact** | no `7901 chain:` line exists (the ancestry section filters to ChatGPT.app-or-`.codex/` argv; 7901 is `/opt/homebrew/…/codex-code-mode-host`). The fact is true only via a *different*, uncited artifact: `pass3-standdown-census.txt:13` `7901 83977`, +:27-28 `83977 83975` / `83975 83953`. Both sentences say membership is "decided per process by the chains printed in that artifact" — for 7901 it is not. |
| 7901 is a "ChatGPT-pathed process" (21c:246-247) | **FALSE** | classified:12 — argv is `/opt/homebrew/lib/node_modules/@openai/codex/…/codex-code-mode-host`. |
| 16479 → 83953 | TRUE | classified:44 |
| 82362 (`codex … app-server`) → 82301 | TRUE | classified:55 `82362 chain: [82362, 82301]` |
| 82551 (SkyComputerUseService) → 82301 | TRUE | classified:58 |
| "the **renderer** helpers" → 82301 | membership TRUE (classified:51-54,56-57,59-60: 82316/82317/82318/82354/82386/82387/83044/83054 all `[…, 82301]`); the word **"renderer" is FALSE-as-sourced** — zero occurrences of `renderer` in any file under `21b-rehearsal-20260909-bench/`; every Frameworks argv is truncated at ≤84 chars, ending `…/Contents/Frameworks/Code`. |
| 82303 / 82305 "had ppid 1" | **INFERRED, not printed** | classified:49-50 print `chain: [82303]` / `[82305]` and a self-root. `chain()` returns a singleton when the parent is 1 **or** absent from the table; no ppid column is printed anywhere in that artifact. |
| 82303 / 82305 are "**crashpad** helpers" | **FALSE-as-sourced** | `crashpad` occurs 0× in the whole bench directory; their argv is truncated to `…/Contents/Frameworks/Code`, i.e. rendered identically to 82316/82317/… The cited artifact cannot distinguish "crashpad" from "renderer" at all, so neither label is checkable. |
| 82303 / 82305 were "**present at the stand-down census**" (21c:246 governs the whole sentence through :249) | **FALSE** | `grep -c '82303' pass3-standdown-census.txt` → **0**; same for 82305 (and 82316). The census lists 82317/82318/82362/82386/82387/82551/83044/83054 only (census:17-25). Their pids are *lower* than pids that are listed, so this is not a "started later" explanation — the two processes are asserted into a census that does not contain them. |

## 2. `pass3-step4-bench.txt`
- Bracket: first line `1788879023 2026-09-08 07:50:23 PDT`, last line **identical**; `git show -s --format=%ct c6d64665` = **1788879023**. Brackets only in the degenerate sense start == commit == end. A zero-width bracket carries no evidence that the bench preceded the committed text; it is consistent with both date lines being emitted by one command.
- Nine result lines: 8 × `PASS rc=N expected=N` + 1 × `PASS-if-assert :: … AssertionError: lock pid is not an ancestor of this census process`. All read PASS. TRUE.
- Reproduced two cases under `mktemp -d /private/tmp/ref7-XXXX`, `HOME` redirected to the temp tree, mocked `ps` on `PATH` (real `/usr/bin/pgrep` left live — read-only, non-gating), census body extracted verbatim from the c6d64665 block:
  - case 1 "own + Ed's app (incl. orphan Frameworks helper) + fake vllm" → `sessions: []`, **rc=0** (expected 0).
  - case 3 "orphan `Contents/Resources/codex app-server` ppid 1" → `sessions: [(9400, '/Applications/ChatGPT.app/Contents/Resources/codex app-server --listen stdio://')]`, **rc=1** (expected 1) — byte-matches the artifact's line.
- **Orphan artifact:** `git grep -n 'pass3-step4-bench' c6d64665` → **no hits repo-wide**. The file 21e6-D6-4 asked for exists but no document cites it; nothing in 21b/21c points the arming session or a successor at it.

## 3. R1 / R4 over the added lines (17 added lines total)
- **R1: clean, vacuously.** `grep -E '[0-9]{1,2}:[0-9]{2}'` over the added lines returns nothing — this delta adds no typed HH:MM. (`stdio://`, `1788944160` are not clock times.)
- **R4: three violations**, all listed above: `renderer` (21b:316, 21c:248), `crashpad` (21b:317, 21c:249) — words present in no artifact and unrenderable from the truncated argv; and `7631–7644` asserting 9 unobserved pids (21b:315, 21c:247). Plus 7901's provenance swap (§1).
- Also new, and not a fact but a **rule**: 21c:252 "any further change to the classifier goes to a cold gate, not another patch." Delta 5 already wrote that same sentence in terms and delta 6 patched anyway; asserting it again in the ruling appendix is self-ratification of a process rule, which is not the lieutenant's to make in-place. It belongs to the cold gate it names.
- 21c:251 records the app-host-task limit in **21c**, whereas 21e6-D6-3's cure named **21b** (the document the arming session actually executes) and asked for the argv shape; neither landed. D6-2 (ask Ed to quit the app *after* 1788945300, not before 1788944160) is untouched by this delta and still open against a one-shot window.
- Narrowing: 21b:238 now reads "Electron helpers **reparented to launchd** (Frameworks path)", but the code excludes any `Contents/Frameworks/`-prefixed argv not `under_session()`, reparented or not. Prose is narrower than the branch it describes (nit; N5 substantially cured otherwise). S5's `[superseded in part …]` bracket at 21c:228 does cure the bare "no allowlist".

## 4. Same-signature statement
**SURVIVES.** "Prose contradicts its cited artifact" is now on its third consecutive round (delta-5 B1 → delta-6 D6-1 → delta 7). Surviving instances: `21c-ref-295-opus-contract.md:246` (82303/82305 asserted present at a census that does not contain them); `21b-rehearsal-20260909-arm-plan.md:315` and `21c:246-247` (7901 called ChatGPT-pathed and sourced to chains the artifact does not print for it); `21b:316-317` / `21c:248-249` ("renderer"/"crashpad" absent from every artifact). The delta cured the *direction* of D6-1 — 82362 and 82551 are now correctly Ed's app — and introduced four smaller instances of the identical class. Per the standing escalation trigger the next spend on this class is a consult, not a delta-8 prose patch.

VERDICT: NOT LANDABLE — blockers: (B1) 21c:246-249 asserts 82303/82305 were present at the stand-down census; the cited `pass3-standdown-census.txt` contains neither pid, and the "crashpad"/"renderer" labels are unrenderable from the ≤84-char-truncated argv in `pass3-census-classified.txt` — same prose-vs-artifact class as the D6-1 it cures, third round running; (B2) 21b:315 / 21c:246-247 sources 7901 to "the chains printed in that artifact" when that artifact prints no chain for it and its argv is homebrew-, not ChatGPT-pathed, and writes 7631–7644 as a range covering nine never-observed pids. Non-blocking but must ride: `pass3-step4-bench.txt` is cited by nothing; D6-2's window-timing email and D6-3's 21b-side limitation are still open; the classifier itself is byte-unchanged and both reproduced bench cases match.
