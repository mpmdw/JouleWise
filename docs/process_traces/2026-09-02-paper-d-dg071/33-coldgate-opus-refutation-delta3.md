# Cold gate, delta re-audit 3 — Opus 5 contract-lens refuter (2026-09-02)

Seat: Opus 5 (Agent tool, read-only), paired with the cold Fable seat (file 32) on packet 31. Ran in parallel with the cold seat; read only the packet and the primary evidence it lists. Report verbatim below; scratchpad paths redacted.

## Refutation

I verified every load-bearing fact below by running it in this session; commands and outputs are quoted inline. Nothing here is taken from the packet's paraphrase.

### 1. The packet's Q1 carries an embedded technical premise that is false, and I disproved it by execution

Q1 tells the seat: "no finite hermetic fixture set kills `values[:N]` for every N; only a test at the retained bundle's own cardinality (or above) discriminates the class at the cardinality that matters." The first clause is true and irrelevant. The clause that matters is: **every cap mutant that can change a published value must have N < 406** (a cap at N ≥ 406 leaves the artifact's numbers untouched — it is not a defect at all). So one hermetic fixture with more than 406 values kills the entire value-changing subclass, in CI, with no corpus.

I built it. One line in `/Users/edr/code/JouleWise-wt-paper-d2/tests/test_issue_dg071_dg075_statistics.py:478`, changing `range(rng.randint(2, 8))` to `range(600 if bundle_number == 0 else rng.randint(2, 8))`:

```
== wide-base ==      Ran 25 tests in 0.281s   OK
== wide-mut400 ==    Ran 25 tests in 0.193s   FAILED (failures=1)
FAIL: test_differential_against_independent_reference
```

(Baseline confirmation first: unmutated checkout `Ran 25 tests in 0.278s OK`; `sorted(values[:400])` mutant unwidened `Ran 25 tests in 0.299s OK`; that mutant's producer output on the retained bundle is `DG-071 400 120.9390 5.7079` / `DG-075 400 120.9391 5.7079` against committed `406 120.9186 5.9508` / `405 120.9224 5.8949`. Terra's B1 is exactly right on its facts.)

Runtime is unchanged. The class the packet calls unclosable closes for one line and zero seconds. Any Q1/Q2 reasoning that rests on "this cannot be closed hermetically" — the cold seat's likely path to (c), and the magistrate's own words ("the class cannot be closed hermetically") — is refuted.

### 2. What files 25 and 26 actually commit the process to — and it is neither of the two answers Q1 offers

File 26 clause 2 adopts the differential with a stated reason: *"because a computation mutant can agree on every fixed case, including the retained bundle."* Sol 250 §Q1 gives the same purpose — the differential exists "to catch input-conditional coincidences" — and in the same sentence specifies "several **2–8-record** valid bundles" (file 25 line 175). File 25 §Q2's not-killed table names, in its own row, "**Input-size-conditional behavior above eight records**" as uncovered (file 30 D2 quotes it back).

So the ruled shape contains a contradiction: clause 2's stated purpose is input-conditional coincidence, and clause 2's stated size is entirely below the cardinality of the only input that matters. The size was implemented; the purpose was not served. **B1 is therefore neither "a recurrence of the escalated signature" (terra) nor "the residual Sol named" (the magistrate). It is the ruled mitigation instantiated at a size that cannot perform its ruled function.** The cure is to conform clause 2's size to clause 2's purpose. That is finishing a ruling, not a fix round, and not an escalation.

The magistrate's "B1 is the residual Sol 250 named" is also imprecise on the merits. Sol's residual row is a mutant that agrees on all fixed cases *and potentially on the retained bundle* — genuinely unclosable, correctly accepted as a limitation. The cap-400 mutant **disagrees** on the retained bundle. It is closable, and I closed it. Filing a closable defect under an unclosable heading is how a limitation register becomes a place to put work you do not want to do.

Note also **packet-hygiene defect (charter §6): F3 is wrong.** It states "The brief for fix round 3 … dictated the differential's '2–8 records'. The magistrate chose that range." The range is Sol's recommendation in file 25 §Q1, adopted by file 26 clause 2 by reference. The misattribution is not cosmetic: it supports the packet's recusal framing and hides that the contradiction sits inside the ruled shape rather than in one party's parameter choice.

### 3. Q3 is a false binary, and the excluded third answer is verifiable and free

Q3 offers "defect in the producer/artifact" or "defect in the brief." There is a third answer, and it is the correct one: **the defect is the producer's definition of `git_commit`, and it is one function away from a definition under which byte-exact replay holds permanently — with the committed artifact bytes unchanged.**

`scripts/issue_dg071_dg075_statistics.py:377-380` defines `_git_commit` as `git rev-parse HEAD`. An artifact whose bytes contain the hash of the commit that contains those bytes is self-referential and impossible; F4 is right that far. But the artifact does not need HEAD. It needs the commit of the thing that produced it:

```
$ git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py     → 6d30c105…   (at HEAD 5f105823)
$ git log -1 --format=%H 6846363d -- scripts/issue_dg071_dg075_statistics.py → 6d30c105…
$ artifact producer.git_commit                                          → 6d30c105d42d7e161e252d94ed1f9c1910e78b6a
```

The three agree. Under that definition the committed artifact is byte-reproducible at `6846363d`, at `5f105823`, and at every later commit that does not touch the script — and the committed bytes do not change, so no re-issue is needed. `script_sha256` (`c745bcf5…`, content-addressed, already matching) covers uncommitted drift. The magistrate's position — "the F4 convention is correct and should be stated in one sentence in the provenance text" — takes the excluded-middle answer and documents a defect instead of removing it. The convention is not correct; it is merely current, and it is the sole reason a reviewer cannot replay the paper's artifact.

**A finding neither seat raised, and the reason this survived three reviews:** `tests/test_issue_dg071_dg075_statistics.py:629`, `test_two_checkout_roots_produce_byte_identical_json`, asserts a property the producer does not have. It passes only because the fixture manufactures two repos with pinned `GIT_AUTHOR_*`/`GIT_COMMITTER_*` identity and dates and the same empty commit, so both HEADs hash identically (lines 631-674); it does not strip `git_commit` before `assertEqual(outputs[0], outputs[1])`. Two *real* checkouts at different commits fail it. The suite has been telling every reader, including the brief author, that cross-checkout byte-identity holds. That is the machinery of the B2 confusion, and it is still in the tree.

Related, and squarely a writing-standard defect: `docs/paper/round7/dg071-dg075-statistics.md:12` publishes `- Git commit: \`6d30c105…\`` with no definition anywhere in the artifact. An unglossed term doing load-bearing work misled the magistrate's own brief. That is the first-use test failing in production.

### 4. Against the magistrate's remedy shape

- It leads with the half that has no regression power. The bench-only pin runs where the corpus exists and nowhere else; CI stays green through any future edit. The CI fixture is offered as an afterthought ("with the CI-enforced synthetic bundle **as well**"). The ordering is backwards: the CI fixture is the closure, the bench pin is the corroboration.
- "Then a fourth delta re-audit by Sol" fails the bench-vs-session threshold on its own doctrine. The change is one line plus one `skipTest`-guarded assertion. Verification is: run the suite, apply the mutant, run again. Three commands; I ran them in under a minute. Rule 9's "delta re-audit of every fix round" governs *delegated* rounds where the lead did not write the code. Spending a fourth seat here converts adjudication into perpetual review, which is its own failure mode.
- The closing line — "records that it is aware this is what a continuation-prone agent would say" — is not evidence and should carry no weight either way. Charter §2 requires continuation and stopping to be tested symmetrically; a party's self-diagnosis is argument, and under charter §7 the proponent still bears the burden. In this instance the argument happens to be right on (a) and wrong on ordering and on the fourth seat.

### 5. Against the cold seat's likely reasoning

The most probable cold ruling, reading this packet cold, is **(c) — accept as a registered limitation, four independent replications, merge**, reached via Q1's embedded "cannot be closed hermetically" plus charter §9's "the next spend is a consult or redesign, not round three." That reading is wrong twice. First, the premise is false; §1 above shows the closure costs one line. Second, §9's remedy has already been paid: the same-signature trigger fired at Opus 249 (file 23) and the consult it demanded was Sol 250. Firing the trigger again, on the consult's own enumerated residual, makes it self-perpetuating — every consult would license the next consult forever. And the proposed change is not "another same-shape round": the two prior rounds added hand fixtures at eight records; this changes the cardinality regime.

The second-most-likely cold outcome is **REFUSE on Q1/Q2 for packet defect**. The hygiene defects are real (F3's misattribution, Q1's embedded conclusion, Q3's false binary, and Q2(a)'s compound structure — a seat choosing (a) is forced to also license a fourth seat spend). But REFUSE is not needed: charter §4 expressly permits reading the code, and the missing fact is verifiable there in three commands. Refusing would leave a one-line closure unbought on a packet defect that the seat can itself cure.

---

## My answers

**Q1.** Neither. It is the ruled shape's own clause 2 implemented at a size that defeats its stated purpose. File 26 clause 2 adopts the differential *"because a computation mutant can agree on every fixed case, including the retained bundle"*; file 25 §Q1 (line 175) sizes it at "2–8-record valid bundles" and file 25 §Q2 simultaneously lists "input-size-conditional behavior above eight records" as not-killed. It is not the residual of file 25 §Q2's last row, because that row's class agrees on the retained bundle and this mutant changes it (`400 / 120.9390 / 5.7079` vs `406 / 120.9186 / 5.9508`, run above). It is not a recurrence of the escalated signature in rule 11's sense — "same defect class, another missed call site, another failed formulation" — because every plausible arithmetic mutant now dies: six prescribed plus two of terra's own choosing (file 30 D3). The one survivor is a constant tuned to 406 records; there is no cap, chunk, batch or pagination anywhere in `_describe` (`scripts/issue_dg071_dg075_statistics.py:179-182`) for such a defect to arise from.

**Q2.** **(a), amended — which is formally (d).** Land both halves, with the CI half load-bearing:

1. **Primary, CI-enforced:** widen `test_differential_against_independent_reference` so at least one bundle exceeds 406 records (`tests/…:478`, one line). Executed above: base OK, cap-400 mutant FAILED, module runtime 0.281s → 0.193s-class, no change.
2. **Secondary, bench-only:** the retained-bundle value-of-record pin, `skipTest` when the corpus is absent, on the `/Users/edr/code/JouleWise/tests/test_env_locks.py:57` precedent. Ten literals; it is the only place in the repo where the numbers the paper prints are asserted at all — I grepped: `120.9186` appears only in the producer's worked-example prose, the two artifacts, and a *fixture*-derived float64 regression test. No test pins the retained-bundle values today.
3. **No fourth delta re-audit.** Bench mutation replay, as above.

Why the others lose. **(b)** second consult: nothing is unknown. File 25 §Q2 already enumerated this exact class; a second consult would spend a seat to be told what file 25 says. **(c)** registered limitation: loses on the executed counter-example — registering a limitation for a defect with a demonstrated one-line hermetic cure is not error control. Four independent replications of the values (terra 248, Opus 249, luna 251, terra 252) establish that today's numbers are right; they establish nothing about tomorrow's edit, which is what a test is for. **(a)-as-written** loses on ordering and on the fourth seat.

**Sub-question — does a bench-only, CI-skipped pin satisfy the signature's "value-pinning test"? No.** A test CI never runs pins nothing against future edits; it records today's agreement. It is still worth its ten literals, because the paper's printed numbers deserve one literal assertion somewhere in the repo and the `test_env_locks.py:57` pattern is the repo's accepted shape for corpus-absent. But the signature is satisfied only by the ≥406-record CI fixture. **The fix must land both**, and the ≥406 fixture is the half that closes the class.

One thing stays open and should be stated as a limitation rather than chased: a mutant that agrees on every fixture *and* on the retained bundle (file 25 §Q2, last row) is unclosable by any test. That one is correctly accepted, and nobody should reopen it.

**Q3.** Neither of the offered options. The values are not defective — file 30 D4 and D5 replicate all eight, and the two replays are byte-identical to each other. The brief's D4 expectation (file 29 lines 55-58, "expect exact sha equality") was structurally impossible, so it is a brief error. But the reason it was impossible is a **producer defect**: `_git_commit` at `scripts/issue_dg071_dg075_statistics.py:377-380` records `git rev-parse HEAD`, which no committed artifact can ever contain. Change it to the last commit touching the producer script and byte-exact replay holds permanently — verified above, and the committed value `6d30c105…` is already that commit, so the artifact bytes do not change and no re-issue is required. Then the property everyone expected becomes true instead of documented-as-false. Yes, the artifact must also define the term: `docs/paper/round7/dg071-dg075-statistics.md:12` prints `- Git commit:` with no gloss anywhere in the document, and that unglossed line is what misled the brief. And `test_two_checkout_roots_produce_byte_identical_json` (`tests/…:629-681`) must be renamed and re-scoped to what it actually tests — that `input_bundle.path` is repo-relative — because as named it asserts a false property and is why nobody caught this earlier.

**Q4.** *Was terra right to call D6 an escalation?* Under the definition it was handed, yes, and it reported honestly and in full. Brief 29 D6 defines the signature as "a reported field with no value-pinning test where a plausible wrong computation differs" and instructs: "If yes, that is an escalation." Terra applied it literally and produced the mutant that satisfies it. But the definition is cardinality-blind and never asks whether the mutant is a defect anyone would write; as written it can be satisfied forever by choosing a constant just below whatever the largest fixture is. Terra was right to report; the definition is what needs the word "plausible" given teeth, and that is the magistrate's error, not terra's.

*Was the magistrate right to bring this here?* On the letter, yes and it was mandatory. Rule 11 lists "any second fix round on the same defect" as a convening trigger, this would be at least the third on the coverage defect, terra flagged both findings `level: blocking` with "adjudicate before accepting" (file 30 flags F1/F2), and B2 required reinterpreting a seat's verdict — which the magistrate is barred from doing alone. The bench-vs-session threshold governs *who types the fix*, not *who decides whether it is licensed*, so it does not excuse the gate. Where the magistrate went wrong is downstream: it convened correctly and then built a packet that carries its own conclusion inside two of the five questions (Q1's unclosability premise, Q3's binary), misattributes the parameter at issue (F3), and compounds Q2(a) with a fourth-seat licence. Charter §6 asks me to name the effect: those defects push the cold seat toward (c) or REFUSE, which are the two outcomes under which the one-line closure never gets bought. They are curable in synthesis by recording the executed disproof above; they do not require a re-issued packet.

**Q5. Severities as I read them.**

- **B1 — SHOULD-FIX (material), not blocker.** Real coverage gap — CI enforces nothing at the cardinality the paper publishes — but the survivor is not a plausible defect, the values are replicated four times independently, and I closed the class in one line and 0.2 seconds; a blocker label on a defect with an executed one-line cure inflates the word.
- **B2 — NOT-A-DEFECT in the artifact's numbers; MATERIAL against the producer's provenance definition and the artifact's undefined "Git commit:" line.** Terra is right that something is wrong and wrong about where; the failure is in `_git_commit`'s definition and in the brief, not in the issued values.
- **M1 (mine, new) — SHOULD-FIX.** `test_two_checkout_roots_produce_byte_identical_json` asserts a property the producer lacks and passes only by constructing two repos with identical commit hashes. It is the machinery that let the B2 misreading survive three reviews.
- **N1 — nit, agreed.** Cosmetic; the bound `golden_sha256` re-stated as a literal. Fix it while touching the file or leave it.

I do not concur with holding the merge on B1 as a blocker. I do consider B2's underlying provenance defect worth fixing before merge, because it is the difference between an artifact a reader can reproduce and one they cannot, and it costs one function and one sentence.

---

## What I did not check

- I did not re-derive the golden's expected values from the CSV literals — file 30 D1 and file 26's bench script did; I took the golden's correctness as established by them.
- I did not line-audit `_independent_reference`; my widened-differential result inherits whatever independence it has (file 30 D2 assesses it as an arithmetic, not end-to-end, oracle).
- I did not verify that a 600-record differential bundle's expected values are hand-derivable — they are not; that fixture's authority is the reference implementation, which is the correct division of labour but is worth stating in the fix.
- I measured runtime only on this machine, once, on the focused module; I did not measure CI wall-clock impact.
- I did not run the canonical suite (prohibited), and I did not check whether the widened fixture interacts with any test outside `tests/test_issue_dg071_dg075_statistics.py`.
- I did not audit refusal-branch coverage, the Method prose beyond the provenance line, the retained bundle's physics or claim suitability, or anything about PR #276 outside the files the packet lists.
- I did not verify the charter's digest against a registry value; no expected digest was supplied to me, and I am the refuter, not the cold seat. If that verification is required of me too, this is a packet defect.
- I made no edits under `/Users/edr/code`; all mutants and the widened-differential copies live under `…/scratchpad/coldgate-delta3-opus/`.
