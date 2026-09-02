# Opus 5 contract-lens refuter — the fixture-shape packet (file 38), verbatim

Seat: Opus 5, contract lens, packet + primary evidence only, read-only on `/Users/edr/code/JouleWise-wt-paper-d2` at `73417fee`; built six fixtures (F0–F6) and a seeded generated-history differential with an independent oracle in its scratch directory. Scratchpad paths redacted to `<scratchpad>`.

---

## Refutation

**Charter digest check (§9).** Observed `shasum -a 256 docs/process/coldgate_charter.md` = `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`; expected value read out-of-band from `docs/process/coldgate_charter_registry.md:16` = identical. Proceeding on the merits.

---

### Q1 — Diagnosis: **AMEND** (the named cause is real but is a symptom of a deeper one)

I agree that each round added the fixture feature that kills the newest *named* wrong command, and the primary evidence says so in its own words: file 36's SF1 disposition writes that the cure is "a fixture history with three shape properties, each of which now kills a **named** wrong implementation" (`36-fresh-pass-disposition-and-reissue.md`, §Dispositions), and terra's cure recommendation is likewise mutant-shaped ("Extend the fixture with a later producer modification and a later change to another script", `37-terra-254-fresh-pass-2.md` §G1-SF1). So the packet's diagnosis is not wrong.

It is incomplete in a way that matters for Q2. The load-bearing weakness is not "assertions are missing a property statement." It is that **all discrimination is carried by the fixture, and adding assertions does not change that**, because an assertion only discriminates on a history shape the fixture actually instantiates. I proved this on the packet's own cure: the candidate asserts P3, and `git log -1 --format=%H --all -- <path>` still passes H1–H3 (fixture F1 below), dying only once I add a history feature H4 that P3 can bite on (F2). Cure item (i) is close to inert without item (ii), and item (ii) is still enumeration — of history shapes rather than of commands. Swapping one enumerated list for another is not a structural change; it just moves the open-endedness.

Second amendment, from the contract lens. `PROVENANCE_DISCLOSURE` (`scripts/issue_dg071_dg075_statistics.py:116-131`) does not state a property to the reader — it states a **command**: "the last commit in the repository's history that changed the producer script (`git log -1 --format=%H -- {SCRIPT_REPOSITORY_PATH}`)". The prose's only genuinely reader-facing promises are (a) `git show <git_commit>:<path>` hashes to the recorded `script_sha256` (= P1) and (b) re-running from any checkout where the script is unchanged since that commit reproduces both files. P2′ and P3 are not promises to the reader; they are the *reason* the command was chosen over `rev-parse HEAD`. When the contract is a command, the complete conformance test is a **differential against the command's semantics over generated histories**, not a property statement over a hand-built one. That shape exists, is cheap, and this module already uses exactly that pattern for the statistics (`tests/test_issue_dg071_dg075_statistics.py:33`, `_independent_reference`) — see Q2.

I reject the packet's alternative "the test should not exist." For the *reader*, P1 plus determinism genuinely is sufficient and both are independently verified (terra G2/G3). But the test's job is regression protection against the next edit to `_git_commit`, and that job is real.

### Q2 — Cure shape: **REFUTE.** It does not close the class, and in one respect it makes coverage *worse* than what is already committed

I built the candidate fixture and ran it. Method: mutant copies of `scripts/issue_dg071_dg075_statistics.py` with the single argv list at line 407 replaced, driven through the **real** `issue_artifacts` code path against scratch repositories, with both the current test's assertion set (equality to the fixture-known producer commit, `≠HEAD`, cross-repo byte identity) and the packet's P1/P2′a/P2′b/P3 applied. Fixtures:

- **F0** — byte-for-byte replica of the fixture now in the tree (`tests/…:653`): root → producer(add) → `unrelated.txt` → later-empty, two repos differing only in the last commit's date.
- **F1** — the packet's H1–H3: root → add placeholder → **modify to producer bytes** (H1) → change `scripts/unrelated_helper.py` (H2) → 1 vs 2 trailing empty commits across the two repos (H3).
- **F2** — F1 + **H4** (this seat's): a later change to the script on a ref *not reachable from HEAD*.
- **F4** — F2 with H2's decoy renamed to the near-miss `scripts/issue_dg071_dg075_statistics_extra.py`.
- **F3** — merge history: the script's last change lands on a side branch merged `--no-ff` into main.
- **F6** — the natural issuance shape: the producer's last change **is** HEAD.

| candidate (`_git_commit` argv) | F0 (in tree) | **F1 (packet's cure)** | F2 (+H4) | F4 (+near-miss) | F3 (merge) | F6 (producer==HEAD) |
|---|---|---|---|---|---|---|
| `log -1 --format=%H -- <path>` (reference) | PASS | PASS | PASS | PASS | PASS | **KILLED** |
| `rev-parse HEAD` | KILLED | KILLED | KILLED | KILLED | — | PASS |
| `rev-parse HEAD^` | KILLED | KILLED | KILLED | KILLED | — | KILLED |
| `rev-parse HEAD~2` | **PASS** | KILLED | KILLED | KILLED | — | KILLED |
| `log -1 --format=%H` (unscoped) | KILLED | KILLED | KILLED | KILLED | — | PASS |
| `log -1 --format=%H -- scripts/` | **PASS** | KILLED | KILLED | KILLED | KILLED | PASS |
| `log --diff-filter=A -1 -- <path>` | **PASS** | KILLED | KILLED | KILLED | KILLED | KILLED |
| `log --format=%H -- <path> \| tail -1` | **PASS** | KILLED | KILLED | KILLED | — | KILLED |
| `log --format=%H -- <path> \| sed -n 2p` | KILLED | KILLED | KILLED | KILLED | — | KILLED |
| **`log -1 --diff-filter=M -- <path>`** | **KILLED** | **PASS** ⚠ | **PASS** ⚠ | **PASS** ⚠ | PASS | KILLED |
| **`log -1 --all -- <path>`** | **PASS** | **PASS** ⚠ | KILLED | PASS ⚠ | PASS | PASS |
| **`log -1 -- ':(glob)**/*statistics*.py'`** | **PASS** | **PASS** ⚠ | PASS ⚠ | KILLED | PASS | PASS |
| `log -1 --first-parent -- <path>` | PASS | PASS | PASS | PASS | **KILLED** | KILLED |
| `log -1 --follow -- <path>` | PASS | PASS | PASS | PASS | PASS | KILLED |

Three results refute the packet:

1. **H1 destroys a kill the committed test already has.** `git log -1 --format=%H --diff-filter=M -- <path>` — "last *modification*", a textbook confusion of "changed" with "edited" — is **killed by the fixture in the tree today** (F0: the script's only change is its add, so the command returns empty and the producer refuses `git_commit_invalid`) and **survives the packet's candidate fixture** (F1/F2/F4), because H1 guarantees the last change is a modification. The candidate shape is not a superset of the current one. A fourth round landing H1–H3 as written would trade one survivor class for another — which is the standing trigger's "same signature" outcome, arriving as the outcome of the gate convened to prevent it.

2. **P3 is asserted but never exercised.** `git log -1 --format=%H --all -- <path>` passes H1–H3 with all four properties green, and dies only under H4. This one is *reader-harmful*, not merely non-conforming: `--all` can record a commit on a local or abandoned ref that is absent from the reader's clone, at which point `git show <git_commit>:<path>` — the exact verification the Method prose hands the reader — fails outright. The packet's claim that H1–H3 are "the failure modes of the property" is therefore false as stated: P3's failure mode is not in the list.

3. **The pathspec class is broader than "directory vs file".** `:(glob)**/*statistics*.py` survives H1–H3 and H4; it needs a sibling whose path is a near-miss of the pinned path (F4). H2 as specified ("a different file under `scripts/`") does not reach it.

**Is P1/P2′/P3 even a unique characterization?** No, and this is the deeper defect. On F3 (merge history) `--first-parent` records the *merge* commit `b74c371` rather than the commit that changed the script, `cbe35de` — and the merge commit satisfies **P1, P2′a, P2′b and P3**. Two distinct commits satisfy the property; only the equality-to-a-fixture-known-sha assertion separates them. So the packet's Q2 target — "every implementation that passes is correct on every full-history repository" — is unreachable from P1/P2′/P3, and after the cure the discrimination still rests on the fixture, exactly where it rests now.

**A shape the packet does not consider, which does close the class — and I built it.** Generated histories + an independent oracle, the pattern already in this module. A seeded generator draws linear histories from {change the script, change a sibling (from a pool including near-miss names), empty commit}, with the last script change carrying the producer bytes, and half the histories carrying an abandoned ref with a later script change. The oracle is ~12 lines of Python: walk `git rev-list HEAD`, return the newest commit whose blob at the path differs from its parent's. No mutant is named anywhere. Result over 30 seeded histories:

```
base          30/30      firstparent   30/30      follow        30/30
head          14/30      headcaret      3/30      head2          8/30
unscoped      14/30      dirpath       23/30      addonly        8/30
modonly       22/30      allrefs       12/30      globspec      24/30
oldest         8/30      secondlast     0/30
```

Every wrong implementation dies, including all three that survive the packet's cure, and it dies *without anyone having thought of it first* — which is the property the packet is actually looking for. Cost: ~0.2 s per history; 8 histories ≈ 1.7 s against the module's current 0.55 s total. That cost is real and should be stated rather than glossed; 8 histories is enough to kill every candidate above.

**`--follow` and `--first-parent`.** The packet says its bench replay finds both "indistinguishable from the reference on this fixture." That is right about the fixture and wrong about the semantics, in opposite directions:

- **`--follow` is correct, not merely lucky.** At `-n 1` it is identical to the reference by construction — rename-following only alters the walk once it reaches the path's creation, which `-1` never does. Verified under an actual rename (`scripts/old.py` → the pinned path): reference, `--follow`, `--first-parent` and `--all` all return `fb601e54`.
- **`--first-parent` is distinguishable and is non-conforming**, just not by any fixture without merges (F3 above). Under the prose — which names the exact command — it is wrong. Under what the reader needs it is harmless (P1 holds, `git show` works). If the project wants `--first-parent` to count as correct, the Method prose must stop naming a command and start naming a property; if it wants it to count as wrong, the fixture needs a merge. The packet's replay cannot answer this because it never built one.

**Simpler shape, if the differential is judged too expensive:** keep the two-repository byte-identity pair as-is (it tests a different thing — same producer commit ⇒ same bytes), and add a small set of *single-repository* shape cases, each asserting equality to that repo's own oracle-computed commit: {script only added; script modified after add; near-miss sibling changed later; abandoned ref with a later change; producer == HEAD; merge}. That is still enumeration, but of the six shapes above rather than of commands, and it kills every candidate in the table. It is strictly better than H1–H3 and strictly worse than the differential.

### Q3 — Merge gating: **REFUTE the framing.** The discriminant the question demands is provably constant across its own alternatives

"Give the reason in terms of what a reader of the paper's artifact loses in each case" presupposes that reader-loss differs between the branches. It does not. The cure under discussion is **test-only**: `_git_commit` is unchanged, the artifact bytes are unchanged, no re-issue occurs. A reader of `docs/paper/round7/dg071-dg075-statistics.{json,md}` receives byte-identical content whether the test is cured in-PR or on main. I verified the reader-facing half independently: the recorded `producer.git_commit` `6b6deb2f…` equals `git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py` at this head, and `producer.script_sha256` `d657d75f…` equals `git show 6b6deb2f:…| shasum -a 256`. Reader-loss is zero on both branches, so it cannot decide the question, and a seat instructed to answer in those terms is being steered toward manufacturing a harm story. Under charter §6 that is a hygiene defect in a question, and I decline the frame rather than the question.

The actual discriminant is regression exposure over the interval between merge and the kernel row landing, weighted by the chance anyone edits `_git_commit` in that interval — which is near zero, since the producer is finished, its values are frozen, and the only pending work on it *is* this test. Against that: a fourth in-PR fix round on a defect class that has now produced three survivors is precisely the spend the standing trigger reserves. And on my evidence the specific cure on offer would regress coverage (finding 1), so an in-PR round would not merely be the forbidden shape — it would land a net-negative fixture.

**Disposition: merge #276 now; cure on main as a kernel row, and not as H1–H3.** The kernel row should carry the differential shape (or the six-shape set), and the standing trigger's real instruction — that the next spend after a third survivor is a consult — has been satisfied by *this gate*, not by another bench fix.

### Q4 — Severity of G1-SF1 (should-fix) and G1-N1 (nit): **AGREE on both grades; AMEND the basis of SF1**

**G1-SF1 = should-fix is correct and, if anything, understated on its facts.** Correct because the defect is test discrimination with zero artifact consequence: nothing a reader sees is wrong, so it is not a blocker; and both survivors terra names are plausible implementations a maintainer could actually write, so it is not a nit. Understated because the committed fixture admits **eight** of my thirteen candidates, not the three terra's table reports: beyond `HEAD~2`, `scripts/` and `--diff-filter=A`, it also passes `--all`, `:(glob)**/*statistics*.py`, `--first-parent`, `--follow` (correctly), and `git log … | tail -1`. Of these, `--all` is the one with a genuine reader consequence. My F0 run reproduces terra's G1 table exactly on the six mutants it did test, so this is an extension of terra's finding, not a correction of it.

**G1-N1 = nit is correct as graded.** `git rev-parse HEAD~2` is a fixture-tuned constant rather than a plausible general implementation, exactly as terra says, and H3 kills the whole fixed-depth family at once. I would add only that its *diagnostic* value exceeded its severity: it was the cleanest available signal that the fixture's depth, not any asserted property, was doing the discriminating — which is the finding this gate is about.

I did not lower either grade, and the magistrate should not.

### Q5 — Process: **REFUTE.** File 36's "SF1 ≠ M1" reasoning was not correct when written, and it fails on the authority it cited

Three pieces of primary evidence, in ascending force.

1. **The finder classed it the other way.** Sol 253, who raised SF1, wrote: *"This is the same fixture-construction class as its predecessor, though narrower: the old test admitted HEAD itself; this one admits HEAD-relative parent logic"* (`35-sol-253-fresh-pass-round-4.md:171`). File 36 records this accurately — *"Sol names it the same fixture-construction class as M1, narrower"* — and then rules the opposite way in the same document, without giving a reason for departing from the finder's classification.

2. **The cited authority says something materially narrower than the paraphrase.** File 36 justifies itself by "apply[ing] the delta-3 cold gate's own ruling (file 32 Q1; file 33 Q1: a residual narrowed by a cure is not a recurrence of the defect the cure closed)." What file 32 Q1 actually holds is: *"A residual that the ruling **enumerated and accepted** is not a recurrence; **a recurrence is the same defect class appearing where the process believed it had closed it**"* (`32-coldgate-fable-ruling-delta3.md:15`). Two conditions were dropped in the paraphrase, and both are dispositive here. `HEAD^` was never enumerated or accepted in advance by any ruling. And file 34's round-4 cure was presented as closing the fixture-shape class — so SF1 arrives exactly where the process believed it had closed it, which is file 32's *definition* of a recurrence. Applied honestly, the cited authority points the other way. (Separately, file 33 Q1 does not contain the quoted principle at all; it holds that B1 was "the ruled mitigation instantiated at a size that cannot perform its ruled function" — "neither a recurrence … nor the residual". The citation is to a proposition its source does not state.)

3. **The distinction drawn is real but not load-bearing.** "Property absent" (M1: the producer genuinely lacked the property, so the test asserted a falsehood) versus "discrimination incomplete" (SF1: the producer has the property, the test is weak) is a true distinction, and I do not dismiss it — it is why M1 forced a producer change and SF1 did not. But rule 11's trigger is keyed to a *defect signature*, and the signature Sol identified is fixture-construction: a hand-built history whose accidental shape lets a wrong command return the right answer. That signature is identical in M1, SF1 and G1-SF1, and the packet now concedes as much for G1-SF1.

**For Ed, plainly:** the trigger should have fired at SF1, one round earlier. The cost of the error is small — one bench round, one fresh pass — and the magistrate has since withdrawn the distinction unprompted, which is the right instinct. What deserves attention is not the miss but its *shape*: the reasoning that produced it re-described a class boundary until the trigger did not reach, and it did so while citing a prior ruling whose actual test it failed. That is the failure mode a written trigger exists to prevent, and it recurred inside the paragraph announcing the trigger. The structural fix is not a new rule: it is that **the party proposing to continue should not be the party classifying the defect**. Classification against a written trigger belongs with the finder (who here got it right and was overruled) or with a cold seat — not with the agent deciding whether to do one more round.

---

## Findings

1. **BLOCKER (against the packet's candidate cure, not against the merge).** H1 as specified removes a kill the committed fixture already has: `git log -1 --format=%H --diff-filter=M -- <path>` is killed by the fixture in the tree (returns empty → `git_commit_invalid`) and survives H1–H3 (F1/F2/F4). Landing H1–H3 as written is a net coverage regression on this class. Minimum cure: the fixture set must contain both a repository whose script is only ever added and one whose script is modified after add — which the two-repository byte-identity pair cannot supply on its own, since it requires identical producer commits.
2. **BLOCKER (against the packet's completeness claim in Q2).** `git log -1 --format=%H --all -- <path>` satisfies P1, P2′a, P2′b and P3 on H1–H3 and passes the whole candidate shape. It is reader-harmful: it can record a commit on an unreachable ref that is absent from a reader's clone, defeating the `git show <git_commit>:<path>` check the Method prose hands the reader. The packet's statement that H1–H3 are "the failure modes of the property" is false: P3's failure mode is missing. Minimum cure: H4 — a later change to the script on a ref not reachable from HEAD.
3. **SHOULD-FIX.** P1/P2′/P3 is not a unique characterization of the recorded commit. On a merge history two distinct commits satisfy all four checks (the side commit and the merge commit; F3, `--first-parent` records `b74c371` where the reference records `cbe35de`, with no property failing). Q2's stated target — every passing implementation is correct on every full-history repository — is therefore unattainable from the property statement, and all residual discrimination stays on equality to a fixture-known sha.
4. **SHOULD-FIX.** Asserting a property does not discriminate unless the fixture instantiates its failure mode (`--all` passes H1–H3 *with P3 asserted and green*). Cure item (i) is near-inert without item (ii), and item (ii) is enumeration of history shapes. Cure item (iii) — "a future survivor is evidence the property statement is wrong" — is therefore not safe as written: findings 1–3 are survivors that indict the *fixture*, not the property.
5. **SHOULD-FIX.** The natural issuance shape — the producer's last change **is** HEAD, which is what you get when you commit the producer and immediately run it — is excluded by the fixture, and the current test's `assertNotEqual(payload["producer"]["git_commit"], head)` (`tests/…:762`) is *violated by the correct implementation* on that shape (F6). This is legitimate as a discriminator inside a fixture built to make it true, but it must not be promoted into the property statement, and the packet's candidate keeps it ("alongside the existing equality to the known sha") without flagging the constraint. Anyone adding history shapes will break the reference implementation on this assertion.
6. **SHOULD-FIX.** The pathspec survivor class is wider than "directory vs file": `:(glob)**/*statistics*.py` survives H1–H3 and H4, needing a sibling that is a *near-miss* of the pinned path (F4), which H2 as specified does not provide.
7. **SHOULD-FIX (process, Q5).** File 36's trigger reasoning cites `file 32 Q1` for a proposition materially broader than what that ruling holds — dropping "enumerated and accepted" and "where the process believed it had closed it", both dispositive against the conclusion drawn — and cites `file 33 Q1` for a principle that section does not contain. It also departs, without stated reason, from the finder's own same-class classification at `35-…:171`.
8. **SHOULD-FIX (packet hygiene, charter §6).** Q3 requires the answer "in terms of what a reader of the paper's artifact loses," a quantity that is provably identical across the two alternatives it offers (test-only cure, no re-issue, byte-identical artifact). The frame steers toward a manufactured harm and suppresses the discriminant that actually applies (regression exposure vs. a forbidden fourth same-signature round).
9. **NIT.** Q2 is compound — close the class / name a survivor / name a simpler shape / rule on `--follow` and `--first-parent` — which invites a partial answer to read as a complete one.
10. **NIT (credit, with a correction).** The packet's own mutant table reports `head2 : FAILED` and self-discloses the cause (a two-commit scratch root, collateral to other tests). That disclosure is good hygiene and I confirm the diagnosis: on a full-depth history `HEAD~2` survives F0, matching terra. But it means the packet's evidence block is not a clean replay of the finding it is adjudicating; the harness above supplies one.
11. **NIT.** The packet's "`--follow` … indistinguishable from the reference on this fixture" understates the result: at `-n 1` it is identical by construction, verified under an actual rename. `--follow` is a correct implementation, not a survivor, and should be recorded as such so no future round spends effort killing it.

---

## Executed evidence

All scratch under `<scratchpad>/coldgate-fixture-opus/`, `TMPDIR` exported there. Nothing was written under `/Users/edr/code/JouleWise-wt-paper-d2` (checkout detached at `73417fee`, `git status` clean at start and end).

```bash
# charter digest (charter §9)
shasum -a 256 /Users/edr/code/JouleWise-wt-paper-d2/docs/process/coldgate_charter.md
#  -> 099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81
#     == docs/process/coldgate_charter_registry.md:16

# baseline (unmutated)
cd /Users/edr/code/JouleWise-wt-paper-d2 && TMPDIR=$SCRATCH/tmp \
  /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics
#  -> Ran 27 tests in 0.555s / OK

# reader-facing provenance, re-verified at this head
git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py   # 6b6deb2f8f9b…
git show 6b6deb2f:scripts/issue_dg071_dg075_statistics.py | shasum -a 256  # d657d75f…
# artifact producer: git_commit 6b6deb2f8f9b…, script_sha256 d657d75f… (both equal)

# fixture-shape mutant matrix (harness.py; mutant copies + real issue_artifacts)
cd $SCRATCH && export TMPDIR=$PWD/tmp
/Users/edr/code/JouleWise/.venv/bin/python harness.py F0        # replicates terra G1 exactly
/Users/edr/code/JouleWise/.venv/bin/python harness.py F1,F2     # packet's cure; +H4
/Users/edr/code/JouleWise/.venv/bin/python harness.py F4,F6     # near-miss sibling; producer==HEAD
/Users/edr/code/JouleWise/.venv/bin/python harness.py F3 base,firstparent,follow,modonly,allrefs,globspec,dirpath,addonly

# generated-history differential (no mutant named in the test)
/Users/edr/code/JouleWise/.venv/bin/python differential.py      # base 30/30; every wrong impl < 30/30

# --follow / --first-parent under a real rename
#  scripts/old.py -(modify)-> -(git mv)-> scripts/issue_dg071_dg075_statistics.py -> empty commit
#  reference / --follow / --first-parent / --all all -> fb601e540240a2a9ce736420fc9c7fa9ae34471e
```

Key raw outputs (abridged; full tables in the Q2 matrix above):

```
=== fixture F0 (the fixture in the tree) ===
base PASS | head KILLED | headcaret KILLED | head2 PASS | unscoped KILLED
dirpath PASS | addonly PASS | firstparent PASS | follow PASS
modonly KILLED (REFUSED:git_commit_invalid) | allrefs PASS | globspec PASS
oldest PASS | secondlast KILLED

=== fixture F1 (the packet's H1-H3) ===
base PASS | head KILLED | headcaret KILLED | head2 KILLED | unscoped KILLED
dirpath KILLED | addonly KILLED | firstparent PASS | follow PASS
modonly PASS  <-- regression vs F0 | allrefs PASS  <-- P3 asserted, inert
globspec PASS | oldest KILLED | secondlast KILLED

=== fixture F6 (producer commit == HEAD) ===
base KILLED   repo0=EQ, P1/P2a/P2b/P3 all true, ne_head=false
```

Primary-evidence citations verified in this session: `scripts/issue_dg071_dg075_statistics.py:116-131` (`PROVENANCE_DISCLOSURE`), `:398-431` (`_git_commit`), `:592-593` (`script_sha256`/`git_commit`), `:766` (`script_path=Path(__file__).resolve()`, so `script_sha256` comes from the running module, not `--repository-root`); `tests/test_issue_dg071_dg075_statistics.py:33` (`_independent_reference`), `:653-779` (the fixture), `:761-762` (`≠HEAD`/`≠HEAD^`); `35-sol-253-fresh-pass-round-4.md:171`; `36-fresh-pass-disposition-and-reissue.md` §Dispositions and §Escalation-trigger statement; `37-terra-254-fresh-pass-2.md` §G1-SF1/§G1-N1/§G1 table; `32-coldgate-fable-ruling-delta3.md:15`; `33-coldgate-opus-refutation-delta3.md` §1.

---

## What this seat did NOT check

- **The rest of PR #276.** I audited the provenance test, `_git_commit`, and the artifact's two provenance fields. I did not review the PR's full diff, the statistics arithmetic, the tiling logic, the refusal paths, or the other 26 tests; my baseline run confirms only that all 27 pass.
- **Whether the original issuance ran with HEAD == the producer commit.** I established that F6 is reachable and is the natural order (commit producer → issue → commit artifact), and that the reference implementation fails the current assertion set there. I did not reconstruct the shell state of the run that produced the committed artifact.
- **Merge-history behaviour beyond one hand-built case.** F3 is a single `--no-ff` merge; the differential generator produces linear histories only, so its 30/30 for `--first-parent` and `--follow` is evidence about linear histories, not about merges. Octopus merges, `--simplify-merges`, and TREESAME edge cases are untested.
- **Non-`git log` implementation families.** I varied only the argv inside `_git_commit`. Wrong implementations that change `cwd`, ignore `repository_root`, parse differently, or cache across runs are outside my matrix (though `test_git_commit_unavailable`/`_invalid` mock `subprocess.run` wholesale, so those two tests discriminate nothing about the command).
- **CI wall-clock impact in the real pipeline.** I measured the differential shape at ~0.2 s per history on this machine only.
- **Anything about the rulings' ratification status or the gate record.** I read files 32, 33, 35, 36, 37 solely where their exact words are the object of Q4 and Q5; I did not read run state, status docs, briefs, transcripts, `MAGISTRATE-NOTES.md`, or the loop.
