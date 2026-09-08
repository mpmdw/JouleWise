# 21f2 — Magistrate terminal review, branch `bookkeeping/2026-09-09-rehearsal-arm` (headless activation 784a764e)

Written 1788880058 2026-09-08 08:07:38 PDT; content reviewed: the whole branch range 1c83f2af..HEAD (every branch commit) as of the commit that lands the 21e9 one-line corrections; this stamp predates that commit. Docs only.

## What this branch does
Records joulewise-53's stand-down (precondition (b)), the synthesis author's ruling of record on D-175 condition 5 (21c), and
amends 21b step 4 to that ruling: the census gates on foreign agent SESSIONS (ancestry outside the lock pid; regex
`(?i)(^|[\s/.])(codex|claude|t3)(?=$|[\s/.:-])`), excludes Ed's ChatGPT.app tree (descendants of its main binary, plus its own
Electron helpers reparented to launchd by the Frameworks path), prints the informational list and the production
`pgrep -lf "codex|claude|t3"` output, asserts the lock pid is an ancestor of the census process, and guards `chain()` against
cycles. The classifier is on its fourth formulation; any further change goes through rule 11's standing trigger, not a patch.

## What I read and ran myself
- The three zsh blocks and four PY heredocs at every round (`zsh -n`, `compile()`), and the step-4 block live as a dry
  classification (`pass3-census-classified.txt`: sessions = joulewise-53's descendants while pid 83953 lives; informational = Ed's
  app helpers and the fake vllm leak) and against nine mocked tables (`pass3-step4-bench.txt`).
- Reviews 21e5, 21e6, 21e7, 21e8 (all Opus) and the consult 21f-consult-2; every blocker's disposition is in the commits.

## Accepted limits (recorded, not cured by more prose)
- Delta 9 (21e9) found two more instances introduced by the previous commit; both were cured as one-line corrections and no new prose
  was added beyond this bullet. Deltas 5–8 each found the class "self-report contradicts its artifact" in text this magistrate wrote (pid narration, a stale head in
  this review, one over-claiming commit message ebf90cd6 corrected by 734dadec). Cure applied: deletion and one-line citations only;
  the classifier block is byte-identical since c6d64665. No further prose reformulation; residual risk is confined to prose, not to
  the arm-time mechanism, whose evidence is the artifacts under `21b-rehearsal-20260909-bench/`.

## Design-level answers
1. Soundness of the gate: step 4 is strictly more permissive than the night's own gate (`agent_census`, zero exclusions), so a
   step-4 false PASS cannot run the stub beside a live agent — the driver refuses `night_refused_agent_present` at t0, acceptable for
   a REHEARSAL_STUB with a disposable measurement root. A false ABORT costs the one-shot window; the classifier therefore stays.
2. Authority: no process rule amended; condition 5 is applied as ruled by its author; H = ae8f074f unchanged.
3. The binding constraint tonight is pid 83953 (the interactive session's terminal), which only Ed can close; if it lives in the
   window the arm aborts fail-closed and Ed gets a status email. Emails sent: `1a0816757635cf98`, `1a081723350aea55`,
   `1a0817fbc66d8737` (all on thread `1a0800cdb282c3f1`).
4. Same-signature: "prose contradicts its cited artifact" recurred across deltas 5–7 in text I wrote; the consult 21f-consult-2 ruled
   that deletion under R2 closes the class, named three residual sites (cited or deleted in the following commit) and two ungated
   channels (commit messages: from here every message claims only "edits as specified"; emails: kept minimal and factual).

## Prune
Nothing pruned; the superseded step-4 formulations survive only in the review reports, not in the operative block.
