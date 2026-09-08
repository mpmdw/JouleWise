# Consult — deltas 5/6/7 prose class + step-4 classifier (READ-ONLY, one round)

Executed (PD-1, read-only): `git diff c6d64665..734dadec` (3 files, +58/-14); `git show --stat ebf90cd6` (1 file, +45);
grep sweeps over 21b/21c at 734dadec; 21c §Ruling of record; `night_gate.py:38,439-466`; `ps -p 83953` at 1788879702.

## 0. Correction to absorb first
`ebf90cd6`'s message asserts "no pid narration in 21b/21c … pass3-step4-bench.txt cited"; its diff is **one file, the
custodied 21e7**. The cures landed only in `734dadec`. Same class — a self-report contradicting its own artifact — in
the **commit-message channel**, uncovered by 21f R3's staged-diff gate and already named by 21f §1(b) (D1: "a commit
message asserted a cure that was not in the operative block"). Instance four, not three.

## 1. Does deletion close the class?
For the operative prose of 21b/21c, yes. Over the added lines of `c6d64665..734dadec` the only 4–5-digit tokens are
`83953` (×2), printed by `pass3-standdown-census.txt:3` (`--- pid 83953: ALIVE`). Every delta-7 blocker token
(renderer, crashpad, 7901, 7631–7644, 82303/82305, 82362, 82551) is gone from both files; 21c:228's `[superseded in
part]` and the 21b:338 `pass3-step4-bench.txt` citation also landed. Three residual channels have no mechanism:

1. **Pre-existing prose was never swept.** `21b:311` ("daemon 71666, spare 71687, both pty-hosts and the resumed twin
   71607 gone") and `21b:365-366` (71666/71596/71682/71687/71607) restate five pids with no same-line artifact. They
   sit in `21-activation-1ef89702/process-census-0055.txt`, uncited by either line; the stand-down census's
   `daemon/spare/pty-host/resume` section is empty and names no pid, so it cannot corroborate "gone" per pid. Same for
   `00-DURABLE-STATE.md:593` "pid 58633, since 09-04" (21e5 R4 flagged it; survives verbatim). Deletion hit the lines
   three reviewers named, not the class.
2. **The email channel is ungated.** The delta-5 B2 and delta-6 D6-2 cures are *emails* (`1a0816757635cf98`,
   `1a081723350aea55`) whose bodies assert process facts; the text is not in the repo, no reviewer can diff it, R2/R3
   bind `docs/` only. Rule: an outbound message either quotes artifact basename + line, or states the fact as an
   instruction with no pid ("close the terminal running joulewise-53").
3. **Commit messages** (§0). Extend R3 to cover `git log -1 --format=%B`, not only the staged diff.

## 2. Classifier: (a) keep as-is; no cold gate for it
The arm-time classifier is not the safety gate. `night_gate.agent_census` (`night_gate.py:38,456-466`) runs
`pgrep -lf "codex|claude|t3"` with **zero exclusions**, refusing on any non-empty match. Step 4 is strictly more
permissive (subtracting own-tree and Ed's app), stricter only in case-insensitivity. So a step-4 false PASS cannot arm
a run alongside a live agent: at t0 (1788947760) the driver's own census sees the same process and emits
`night_refused_agent_present`, which NIGHT_HANDBACK classes acceptable for a stub; and the plan is `REHEARSAL_STUB`
with a deliberately fake `/private/tmp/...` measurement root (`MAGISTRATE_WATCHDOG.md:298`) — no corpus, no claim,
nothing to contaminate. **False PASS** → that refusal receipt instead of `REHEARSAL_ONLY`: bounded, ruling-anticipated
(21c consequence (1)), recoverable by re-arming. **False ABORT** → the one-shot 01:56–02:15 window is spent, no stub
night, the rehearsal gating the first real window slips a day. The cheap direction is the fail-closed one, so a fifth
formulation buys nothing and spends the window it protects. Tighten nothing.

**The binding constraint tonight is not the classifier.** `ps -p 83953` at 1788879702 returns `83953 1282 claude` —
**alive**, ~18 h before the window. The ruling requires it gone; only Ed can close that terminal; he is remote and
asleep at 01:56–02:15. Absent an act by Ed the arm aborts on 83953 for reasons no classifier change touches, and
delta-6's precondition proposal ("Ed quits, then require zero foreign matches") carries the identical dependency.
Arming at all on a condition only a sleeping human can clear is what would deserve a cold gate; the classifier does
not. Still open: D6-2 — the sent email says quit the app "before the belt 1788947100", permitting a quit before
1788944160 that orphans `Resources/`-pathed helpers into a fail-closed abort.

## 3. Mechanical check for delta 8
Must print nothing (allowlist = the two pids the arm block names operationally: 83953, which the ruling requires gone, and 48645, which `21b:174` `ps -p`s):

    cd docs/process_traces/2026-09-02-hands-free-week && \
    git diff c6d64665..734dadec -- 21b-rehearsal-20260909-arm-plan.md 21c-ref-295-opus-contract.md \
      | grep -E '^\+' | grep -v '^+++' | grep -oE '\b[0-9]{4,5}\b' | grep -vE '^(83953|48645)$' | sort -u

Benched both ways: `c6d64665..734dadec` → **empty**; `c93b475b..c6d64665` (delta 6) → `16479 7143 7631 7644 7901 82301
82303 82305 82362 82551`, i.e. it fires on exactly the text delta 7 blocked. Being an added-lines check it misses
§1.1's 21b:311/365 — also run the extraction whole-file over 21b, clearing each hit against an artifact.
