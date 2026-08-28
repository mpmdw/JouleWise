# What was found this session (the verification sprint)

A verification sprint is a bounded audit that asks whether a rule recorded in prose is also enforced by the code that creates the files governed by that rule. We checked 460 such rules. Of these, 69 existed but lacked a check where the files were created, and 53 were not implemented at all. Together, 122 of 460 rules—26.5%, or about one in four—had been decided but were not enforced at the point of creation. The audit can have missed problems, so this is a lower bound rather than a complete census.

The most consequential example concerned the planned comparison of the 7-billion-parameter and 1.5-billion-parameter models in prompt processing and token generation. The two comparisons were supposed to be treated as one pair and corrected with the Holm procedure, which limits the chance of declaring an effect merely because two statistical tests were tried. A p-value is the probability, under the no-effect model used by the test, of obtaining a result at least as extreme as the one observed. With an overall false-positive limit — the greatest allowed chance of declaring an effect when none exists — of 0.05 and two tests, the procedure works as follows:

```text
sort ascending:                     0.02, 0.04
multiply the smallest by two:       0.04, 0.04
                                      (leave the larger p-value as it is)
raise each to the largest adjustment seen so far: 0.04, 0.04
compare with 0.05:                  both pass
```

This step prevents a later adjusted value from becoming smaller than an
earlier one. For a failing counter-example, 0.03 and 0.04 first
become 0.06 and 0.04, then both become 0.06; neither passes the 0.05 limit.

Those figures illustrate the checked implementation; they are not campaign results. The agreed collection plan instead described only one test, omitted the block that joins both comparisons, and left the prompt-processing comparison unfinished. The plan-locking step—the point where analysis rules are fixed before data collection—did not validate this information. The campaign could therefore have run for about a week before the final analysis issued a recorded refusal: a decision that missing or inconsistent evidence does not support the planned result. The repair is to make plan locking reject a missing or inconsistent two-comparison plan before collection begins. This check remains a **gate** — an automated test with the authority to stop the pipeline, with no human able to wave it through — that must pass before collection begins.

We also built a minutes-long desk check that puts known missing or inconsistent inputs into the path from plan creation through final analysis and confirms that they fail early. Later execution showed that synthetic inputs cannot yet drive every stage to a genuine pass — some stages require real sampler output that no synthetic input reproduces. The clean end-to-end proof therefore remains a planned live run of about 20 minutes on the real machine, isolated from publishable campaign data.

Finally, we reorganized the paper around the finding rather than the machinery. Inference has two physically different **phases** — prompt processing, a dense burst of arithmetic, and token generation, a slower memory-bound stream — and uncertainty about where in time one ends and the other begins may set the smallest defensible per-phase energy difference. The model comparison demonstrates how the instrument accepts or refuses a result.

# What changed in the paper

The paper’s goal is now a single, testable question: on the named machine and software configuration, does uncertainty in assigning energy to the two phases contribute more to the **detection floor** — the largest energy difference this system can report between two runs that were in fact identical — than ordinary variation among repeated runs does? The paper no longer treats a difference between model sizes as its destination.

The main text fell from about 30,000 words to 9,980. The current Markdown file contains 17,634 words because that count also includes references and the reproduction appendix. The appendix was rewritten from the code so that a student can rebuild the calibration: it defines each quantity before use, states how the calculation searches the possible timing placements allowed by the recorded data, and explains how the final detection floor is formed. The results section contains the planned tables and recorded-refusal rules but awaits the campaign’s measurements.

# The campaign plan and dates

The current working calendar slipped by one day during the August 27 pause. The instrument-verification rehearsal—a run that exercises the real measurement path without producing research claims—is planned for Saturday night, August 29. The campaign is planned to begin Sunday night, August 30, with the plan locked, the instrument **armed** — given a single-use authorization to launch exactly the locked plan — and the first **collection window** opened: one uninterrupted sitting at an untouched, quiet machine that begins and ends by checking how software event times align with recorded power. Its planned duration is 168 hours, so the working close date is Sunday, September 6. These dates remain a proposed operating calendar, not completed work.

# Honest limitations

First, the calibration works by commanding the graphics processor on and off at software-chosen times and measuring how far those switches appear displaced in the power record; the largest such displacement is the **timing bound**. Those pulses run under a lighter load than sustained inference, and we have not yet tested whether the bound transfers to the real load regime; the campaign does not close this gap.

Second, we have no external power meter. Our only instrument is macOS `powermetrics`, which reports power for three named channels inside the processor package — CPU, GPU, and Neural Engine — so nothing independently checks its numbers, and display, storage, fans, and power-conversion loss fall outside what it sums. An external meter would check the total but would not, by itself, determine how to divide that total between prompt processing and token generation.

Third, the work uses one physical Apple M3 Max unit. Its numerical detection floors do not transfer to another machine, operating-system build, model revision, or software configuration without a new calibration.

# What we would like your reaction to

We would especially value your reaction to three choices.

First, is the paper’s instrument-first framing — the choice to make the detection floor defined above the primary product — persuasive? The model comparison then demonstrates that bound rather than carrying the paper.

Second, is one primary research question the right level of focus for the capstone, with one model-pair demonstration and one printed negative result—a recorded finding that the short prompt-processing phase cannot be resolved—supporting it rather than competing with it?

Third, are you comfortable with the simplified threat model—the list of ways a measurement could be wrong or faked that the design defends against? We propose retaining defenses against plausible mistakes, missing evidence, and choices made after seeing results, while dropping defenses whose only purpose is to stop a deliberately dishonest trusted operator. This aligns the safeguards with a single-researcher capstone while preserving the checks that protect the scientific result.
