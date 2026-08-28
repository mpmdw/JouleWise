# What was found this session (the verification sprint)

A verification sprint is a bounded audit that asks whether a rule recorded in prose is also enforced by the code that creates the files governed by that rule. We checked 460 such rules. Of these, 69 existed but lacked a check where the files were created, and 53 were not implemented at all. Together, 122 of 460 rules—26.5%, or about one in four—had been decided but were not enforced at the point of creation. The audit can have missed problems, so this is a lower bound rather than a complete census.

The most consequential example concerned the planned comparison of the 7-billion-parameter and 1.5-billion-parameter models in prompt processing and token generation. The two comparisons were supposed to be treated as one pair and corrected with the Holm procedure, which limits the chance of declaring an effect merely because two statistical tests were tried. A p-value is the probability, under the no-effect model used by the test, of obtaining a result at least as extreme as the one observed. With an overall false-positive limit of 0.05 and two tests, the procedure works as follows:

```text
two p-values → adjust the smaller for two tests → keep the larger adjustment
0.02 and 0.04 → 0.04 and 0.04 → both are at or below 0.05
```

Those figures illustrate the checked implementation; they are not campaign results. The agreed collection plan instead described only one test, omitted the block that joins both comparisons, and left the prompt-processing comparison unfinished. The plan-locking step—the point where analysis rules are fixed before data collection—did not validate this information. The campaign could therefore have run for about a week before the final analysis issued a recorded refusal: a decision that missing or inconsistent evidence does not support the planned result. The repair is to make plan locking reject a missing or inconsistent two-comparison plan before collection begins; this remained a pre-collection gate in the checked session record.

We also built a minutes-long desk check that puts known missing or inconsistent inputs into the path from plan creation through final analysis and confirms that they fail early. Later execution showed that synthetic data cannot yet produce an honest clean pass through every stage. The clean end-to-end proof therefore remains a planned live run of about 20 minutes on the real machine, isolated from publishable campaign data.

Finally, we reorganized the paper around the finding rather than the machinery: uncertainty about the boundary between prompt processing and token generation may set the smallest defensible phase-energy difference, while the model comparison demonstrates how the instrument accepts or refuses a result.

# What changed in the paper

The paper’s goal is now a single, testable question: on the named machine and software configuration, does uncertainty in assigning energy to the two phases contribute more to the measurement limit than ordinary variation among repeated runs? The paper no longer treats a difference between model sizes as its destination.

The main text fell from about 30,000 words to 9,980. The current Markdown file contains 17,634 words because that count also includes references and the reproduction appendix. The appendix was rewritten from the code so that a student can rebuild the calibration: it defines each quantity before use, states how the calculation searches the possible timing placements allowed by the recorded data, and explains how the final measurement limit is formed. The results section contains the planned tables and recorded-refusal rules but awaits the campaign’s measurements.

# The campaign plan and dates

The current working calendar slipped by one day during the August 27 pause. The instrument-verification rehearsal—a run that exercises the real measurement path without producing research claims—is planned for Saturday night, August 29. The campaign is planned to begin Sunday night, August 30, with the plan locked, the instrument authorized, and the first collection window opened. Its planned duration is 168 hours, so the working close date is Sunday, September 6. These dates remain a proposed operating calendar, not completed work.

# Honest limitations

First, the calibration uses commanded graphics-processor pulses under a lighter workload, but the result is applied to sustained inference. We have not yet tested whether that timing bound transfers to the real load regime; the campaign does not close this gap.

Second, we have no external power meter. The software counter therefore lacks an independent check of whole-system energy, and its processor-only boundary omits the rest of the computer. An external meter would check the total but would not, by itself, determine how to divide that total between prompt processing and token generation.

Third, the work uses one physical Apple M3 Max unit. Its numerical measurement limits do not transfer to another machine, operating-system build, model revision, or software configuration without a new calibration.

# What we would like your reaction to

We would especially value your reaction to three choices.

First, is the paper’s instrument-first framing—the choice to make the measured resolution bound the primary product—persuasive? The archived artifact calls this bound the detection floor, defined as the largest false difference this measurement system can manufacture. The model comparison then demonstrates that bound rather than carrying the paper.

Second, is one primary research question the right level of focus for the capstone, with one model-pair demonstration and one printed negative result—a recorded finding that the short prompt-processing phase cannot be resolved—supporting it rather than competing with it?

Third, are you comfortable with the simplified threat model—the list of ways a measurement could be wrong or faked that the design defends against? We propose retaining defenses against plausible mistakes, missing evidence, and choices made after seeing results, while dropping defenses whose only purpose is to stop a deliberately dishonest trusted operator. This aligns the safeguards with a single-researcher capstone while preserving the checks that protect the scientific result.
