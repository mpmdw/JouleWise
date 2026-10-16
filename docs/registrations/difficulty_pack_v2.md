# DIFFICULTY pack registration, version 2

**Status.** This is a pre-registration: the question, the problems, the sample sizes and every piece of arithmetic are fixed in writing before the data exist. A **pack** is one question with its own registration, collection and release (`docs/design/block6_collection_draft.md` section 14). Registered before any DIFFICULTY energy measurement exists: no power has been captured for any problem of this pack, and nothing below depends on such a measurement. The commit that adds this file is the registration time. It supersedes version 1 (`docs/registrations/difficulty_pack_v1.md`), withdrawn on 2026-10-14 before any DIFFICULTY energy existed, for the reasons in its header. Author: Opus 5.5, in the orchestrator role (the model seat that directs this project's work and records its decisions). Sources: specification v2 (`/Users/edr/night-archive/difficulty-pack/SPEC-v2.md`, "the spec"), the executing review of the code built from it (`REVIEW-v2.md` in the same folder; the reviewer ran the code rather than only reading it), the refuter of version 1 (`refuter/sol.md`; a different model that tried to break version 1 by running its code), the power simulation (`POWER-v2.md`) and the pilot (`/Users/edr/night-archive/pilots/difficulty/SUMMARY.md`). Paths under `/Users/edr/night-archive/` are the project's local archive on the measurement laptop.

**Revision before landing (2026-10-14, still before any DIFFICULTY energy).** A refuter (Sol 6.1, `refuter-v2/sol.md`) ran the code against this text's first draft (commit `8c47aa656`, never on main) and found nine faults; the orchestrator reproduced them and recorded what changed in `refuter-v2/DISPOSITIONS.md`. Two change the design, not only the words. The simulation that set the sizes assumed 4B spends 1.7 times as much per generated token as 1.7B; the pilot's own wall time says 2.06, and with that the draft's sizes resolved the level-5 comparison in only about half of simulated campaigns, so the thinking-off bench is now 400 problems at levels 3 and 4 and 600 at level 5 (section 4.1). And the claim that five 0.99 decisions keep the chance of any false decision at or below 0.05 holds only when each interval reaches its nominal coverage; section 4.1 now prints the worlds where it does not. The configuration's version string is `difficulty-v2.1`, so its bytes are not mistaken for the draft's.

**Revision 2.2 (2026-10-15, still before any DIFFICULTY energy).** A second refuter run (Sol 6.1, `refuter-v2.1/sol.md`) found six faults in revision 2.1; the orchestrator's dispositions are in `refuter-v2.1/DISPOSITIONS.md`. One changes the design. With 30 energy runs at level 1, the level-1 primary 0.99 interval covered only about 0.94 to 0.96 in the world built from the pilot's wall times, and near a level-1 tie the registered code printed a false "cheaper size changes with level" in 6% of campaigns. The thinking-off energy subset at level 1 is now 70 for each of the three thinking-off configurations, the smallest size tried that met both bars in simulation (section 4.1). Levels 2 to 5 stay at 30, and the bench sizes are unchanged. This adds 120 energy runs, about 2.9 h of machine time. The configuration's version string is `difficulty-v2.2`; only the level-1 thinking-off energy list changed, and its first 30 problems are revision 2.1's list. The other five findings were corrections to the text.

**Revision 2.3 (2026-10-15, still before any DIFFICULTY energy).** The bar for agreement between the main program and the twin (section 10) was relative 10⁻⁹. That is far finer than anything printed, so a harmless change in the order of a sum could have held the release. Every decimal value now agrees when it is within 10⁻⁶, relative or absolute in the column's own unit. That is about 10⁹ times the largest difference seen between the two programs (1.8 × 10⁻¹⁵) and below any printed digit. Words, verdicts, keys, whole numbers and text must still be identical. No list, size or arithmetic changes, and no registered code hash changes, since the bar is set in the agreement test.

## 1. The question, and why it is asked this way

A language model answers a math problem by writing text one **token** at a time (a token is a short piece of text: a word, part of a word, a digit or a symbol). Every token costs energy, so a long answer costs more than a short one. A larger model costs more energy per token but is right more often. What a user pays for a correct answer therefore depends on both: if a small model is wrong half the time, every correct answer also carries the energy of a wrong one.

The quantity that combines the two is the **energy per correct answer** (EPC): the joules spent over many attempts divided by the number of those attempts that were correct. Equivalently, the mean energy of one attempt divided by the fraction of attempts that are correct. For example, if attempts cost 140 J on average and 75% are correct, EPC = 140 / 0.75 = 186.7 J.

The models are Qwen3 language models of three sizes: 1.7, 4 and 8 billion learned weights ("1.7B", "4B", "8B"). Each can either write out its reasoning before the answer (**thinking on**) or answer directly (**thinking off**). A **configuration** is one model with one of these modes, written for example `qwen3-1.7b/off`.

The problems are from MATH (Hendrycks et al., 2021), a set of competition problems whose authors gave each a **level** from 1 (easiest) to 5 (hardest). The pilot (a trial of 20 problems per level, no power measured, with time per correct answer as a stand-in for energy) found that with thinking off, 1.7B's accuracy falls from 95% at level 1 to 30% at level 5, while 4B falls only to 65%. By time per correct answer 1.7B was cheapest at levels 1 and 2, and 4B about twice as cheap as 1.7B at level 5 (16 s against 29 s per correct answer; pilot summary, "Recommendation" item 2). If that holds in joules, which model is cheapest depends on how hard the problem is.

**Primary question.** At each level 1 to 5, which of two configurations uses fewer joules per correct answer: `qwen3-1.7b/off` or `qwen3-4b/off`? And does the cheaper one change between levels?

**Secondary questions.** At each level, which of all measured configurations is cheapest per correct answer, and whether that changes with level. How much of the energy of an attempt follows the number of tokens read and written.

Level is a label the dataset's authors attached to each problem before any model existed. Problems at different levels also differ in subject and length, so results are stated as "at level L", never as "difficulty causes".

## 2. What is run, and what is measured

**Machine.** One Apple M3 Max laptop with 128 GB of memory, running the models with Apple's MLX library.

**Configurations.** With thinking on, the model writes its reasoning between the markers `<think>` and `</think>` and then the answer; with thinking off, the prompt already contains an empty reasoning section, so the model answers directly. "4-bit" means each weight is stored in 4 bits. The **output cap** is the most tokens a configuration may write; an answer that reaches it is cut off and scored wrong.

| Configuration | Weights (Hugging Face repository at revision) | Output cap (tokens) | Status |
|---|---|---|---|
| `qwen3-1.7b/off` | `mlx-community/Qwen3-1.7B-4bit` at `3b1b1768f8f8cf8351c712464f906e86c2b8269e` | 4,096 | measured |
| `qwen3-4b/off` | `mlx-community/Qwen3-4B-4bit` at `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25` | 4,096 | measured |
| `qwen3-8b/off` | `mlx-community/Qwen3-8B-4bit` at `545dc4251c05440727734bcd94334791f6ab0192` | 4,096 | measured |
| `qwen3-4b/on` | `mlx-community/Qwen3-4B-4bit` at `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25` | 16,384 | measured |
| `qwen3-8b/on` | `mlx-community/Qwen3-8B-4bit` at `545dc4251c05440727734bcd94334791f6ab0192` | 16,384 | optional |

The revisions are the ones the pilot ran (`run_pilot.py` lines 35 to 37) and the ones the local copies under `/Users/edr/jw_models/mlx-community/` hold. An **optional** configuration is measured only if machine time allows before the end date (section 9); if any row of it exists, it is analysed exactly like the others. Qwen3-1.7B with thinking on is not measured. In the pilot (8 problems per level for it, 20 for 4B thinking off) it took 2.3 times as long per correct answer as 4B thinking off at level 1 and 4.1 to 6.1 times as long at levels 2 to 5, for accuracies of 100, 88, 88, 88 and 62% against 95, 95, 95, 85 and 65%: no accuracy gain beyond one problem in eight, at several times the cost. Caps are the pilot's: at 4,096 tokens most thinking-off answers that still hit the cap repeat the same text until cut off; 16,384 was reached by 2 of the pilot's 195 4B and 8B thinking-on answers (134 of those were run at that cap; the others had finished under the 4,096 cap of the pilot's first pass).

**Decoding.** Greedy: at each step the single most probable next token is written, with no randomness, so two runs of the same prompt should write the same text. The prompt is the problem followed by "Please reason step by step, and put your final answer within \boxed{}." in Qwen3's chat format (the importer's template `math_levels_v1/qwen3_chat_boxed_v1`, SHA-256 `1a0796c08f1175730c3dde6a9e7d38312904f985853cb2ad46d594a90dd2319d`).

**Scoring.** The last `\boxed{…}` answer is read as a rational number and compared with the reference answer (the merged importer's scorer `math_levels_v1/score_v1`). With thinking on, only the text after `</think>` is read. An answer cut off by the cap scores `truncated` (wrong); no box, or no `</think>` with thinking on, scores `malformed` (wrong). Scoring happens after generation, from the recorded text.

**One attempt** is one generation of one problem by one configuration. Two kinds are recorded:
- **Bench attempts**: text and token counts only, no power captured. They give accuracy and token counts.
- **Energy attempts** (also called **runs**): the same problem generated again while power is captured. They give the energy of the attempt. Runs happen in **sessions**, unattended stretches of measurement on the laptop with no other work on it.

**Energy of an attempt** (`energy_j`): gross whole-request energy, from the moment the prompt goes in to the moment the last token comes out, covering both reading the prompt and writing the answer, with the idle power of the machine not subtracted. It is recorded at two **boundaries** (what the meter sees):
- `rails`: the processor chip's CPU, GPU and neural-engine power as reported by macOS `powermetrics`. This is the headline boundary.
- `wall`: the whole machine, from a USB-C power meter on the laptop's charging cable. It is printed beside rails as a labelled line. When the laptop draws more than the charger supplies, the battery covers the gap and this meter misses it; such runs carry the flag `battery_assist` (recorded, not excluding).

The program that turns a captured run into rows of `energy.csv` (the energy adapter) is built and reviewed separately, before the first energy session. This registration fixes the columns it must write (spec section 5) and everything computed from them.

## 3. Which problems

### 3.1 The population

The MATH test split (5,000 distinct problems) as redistributed in OpenAI's PRM800K repository at commit `7ecc794703b2877f63226f2477a49b34f9b25163`, read through the project's merged MATH importer (`joulewise/benchmark_import_math.py`). The importer refuses source files whose SHA-256 differs from the recorded ones: `test.jsonl` `35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132` and `train.jsonl` `90d96daeac3fe343ebb1e22ce93dd99690f75983e957f88de42f87cffe1e8076` (the test problems are spread over both files). It keeps only problems that can be scored exactly: one problem that appears twice is dropped (both copies), 954 whose reference answer is not a single rational number are dropped, and 5 whose answer is ambiguous because of a comma are dropped. That leaves 4,040 problems, by level 381, 733, 924, 967 and 1,035.

From these, three sets are removed so that no problem used to design this pack is measured by it: the importer's own 16-per-level pilot set and 128-per-level test set (seeded orders in the importer, domains `joulewise.benchmark_import.math.pilot.v1` and `joulewise.benchmark_import.math.selection.v1`), and the 100 problems of the DIFFICULTY pilot (`/Users/edr/night-archive/pilots/difficulty/pilot_item_ids.txt`, SHA-256 `5ba18f9acf9c01f5cc1b8efe3f01a44f3c4db028e0f8d6d4322d3d2ea199bf88`). That removes 164 per level, 820 in all. What remains at level L is the **pool** of level L: 217, 569, 760, 803 and 871 problems at levels 1 to 5.

### 3.2 Seeded random selection

Every list of problems below is a **simple random sample**: each problem of the set it is drawn from is equally likely to be in it, and the draw is fixed by a published text string (the **seed**) so that anyone can repeat it exactly. The draw works by sorting. Each problem gets a **key** for each purpose:

key = SHA-256 of the text `D + "/" + tag + "/" + item_id`, written as 64 hexadecimal digits,

where SHA-256 is a standard cryptographic hash (any change to the text changes the key unpredictably), `D` is `joulewise.packs.difficulty.selection.v2/joulewise.packs.difficulty.v2` (a fixed prefix built from the seed `joulewise.packs.difficulty.v2`, so that this pack's keys differ from those of any other draw from the same problems), `tag` names the purpose and `item_id` names the problem. Sorting a set by key gives a random order that the seed fixes; the first k problems of it are a simple random sample of size k, and so is every shorter beginning of the list.

For each level L, in this order:
1. **Manifest list** `M_L`: the pool sorted by key with tag `level`, first 600 (the whole pool at levels 1 and 2, which hold 217 and 569). (The **manifest** is the file that lists the pack's problems with their text and reference answers.)
2. **Thinking-off bench**: `M_L` sorted by tag `bench/off/L`, first 200 at levels 1 and 2, 400 at levels 3 and 4, 600 at level 5 (all of `M_5`, in a new order).
3. **Thinking-off energy subset** (the bench problems that also get energy attempts): the thinking-off bench sorted by tag `energy/off/L`, first 70 at level 1 and first 30 at levels 2 to 5.
4. **Thinking-on bench**: `M_L` sorted by tag `bench/on/L`, first 64.
5. **Thinking-on energy subset**: the thinking-on bench sorted by tag `energy/on/L`, first 20.

The **holdout** of a mode is its bench minus its energy subset: 130, 170, 370, 370 and 570 problems at levels 1 to 5 with thinking off, 44 per level with thinking on. Every configuration of a mode uses that mode's lists, so all configurations answer the same problems.

Worked example (level 1, purpose `energy/off/1`). The text `joulewise.packs.difficulty.selection.v2/joulewise.packs.difficulty.v2/energy/off/1/math_test_prealgebra_1859` hashes to `00c578a19a44f7fc…`, the smallest key among the 200 level-1 bench problems, so `math_test_prealgebra_1859` is first in that order; `math_test_algebra_1624` (`04dc06aa…`) is second. The 70th is `math_test_prealgebra_789` (`6055d72b…`) and the 71st `math_test_algebra_1763` (`61273225…`), so the level-1 thinking-off energy subset ends at the 70th. Its first 30 are revision 2.1's level-1 subset, which ended at `math_test_algebra_1149` (`2c6b445c…`).

```
pool_L (217 to 871 problems)                 every remaining scorable level-L problem
 └─ M_L: up to 600 by key "level"            the manifest list (217, 569, 600, 600, 600)
     ├─ thinking-off bench: 200, 200, 400, 400, 600 by "bench/off/L"   accuracy and tokens, no power
     │   ├─ energy subset: 70 at L1, 30 at L2-5 by "energy/off/L"   power captured
     │   └─ holdout: the rest (130 to 570)         accuracy and token means for EPC
     └─ thinking-on bench: 64 by "bench/on/L"
         ├─ energy subset: 20 by "energy/on/L"
         └─ holdout: the other 44
```

Each name on the left is a set of problems, with its size; each indented set is drawn from the one above it by the key tag in quotes; the text on the right says what the set is used for. Because each list is a random sample of the same population, the energy subset and the holdout estimate the same problems' quantities; any difference between them (for example, Algebra and Prealgebra are 16 of the 30 level-3 energy problems but 182 of the 370 level-3 holdout problems) is sampling noise, and the intervals of section 6, which resample the measured problems, include it. Subject counts are printed as description only; no subject balance is claimed.

**The registered lists.** Built by `scripts/difficulty_manifest.py` (section 10) from the configuration in appendix A over the MATH files above: the sizes above, energy within bench within `M_L` for both modes, no short selection, and the two expected flags `short_level:1:217` and `short_level:2:569` (the manifest list at levels 1 and 2 is the whole pool, because 600 exceeds it). Two builds gave identical bytes. The selections file `selections-difficulty-v2.2.json` (problem ids only) has SHA-256 `08d66d9c3f01ac76700782d25c2232a5118ed80d921e948ad56d631e9c7b56e3`; the full manifest `manifest-difficulty-v2.2.json` (2,586 problems; it holds problem text and stays outside the repository) has SHA-256 `22079f592370a2e6d74cf2f03d60701eace14a90d7907ff6ec6b6f5f99ab82f9`. Both are kept at `/Users/edr/night-archive/difficulty-pack/v2.2-registration/` with the configuration. Against revision 2.1's lists (`v2.1-registration/`, selections `b16a5ad7…`, manifest `a800ccb8…`) only the level-1 thinking-off energy list differs: it holds 70 problems, and its first 30 are revision 2.1's. The seed was fixed in the spec before any list at these sizes was drawn and is not changed here. The draft's lists (`v2-registration/`, 200 per level) and revision 2.1's are superseded, and nothing was measured on either.

## 4. How many, and what that buys

| Mode | Bench per level | Energy subset per level | Holdout per level | Configurations |
|---|---:|---:|---:|---|
| thinking off | 200, 200, 400, 400, 600 | 70, 30, 30, 30, 30 | 130, 170, 370, 370, 570 | 1.7B, 4B, 8B |
| thinking on | 64 | 20 | 44 | 4B; 8B optional |

That is 570 thinking-off energy attempts ((70 + 4 × 30) × 3 configurations), 100 for 4B thinking on and 100 more if 8B thinking on is measured; 5,400 thinking-off bench attempts (1,800 × 3 configurations) and 320 per thinking-on configuration.

### 4.1 How the thinking-off sizes were chosen

Two words first. An interval at **nominal confidence** 0.99 is built so that, if the whole experiment were repeated many times, it would contain the true value in 99% of the repetitions; its **coverage** is the fraction in which it actually does. The **power** of a design is the probability that it gives the answer that is true.

The sizes come from simulations that ran the registered estimator code (section 10) on synthetic data. Each simulated **campaign** is one complete repetition of the pack. Every synthetic world is built from the pilot: at each level, the 20 pilot problems with their real correctness and token counts for each thinking-off model; each bench drawn from those 20 with replacement, the same draw for every configuration, so that a slot is one problem answered by all of them. Energy is made in one of three ways:

- **World A** (`POWER-v2.md`): energy = c × (generated tokens) × e^Z, with c = 1 for 1.7B, 1.7 for 4B and 2.4535 for 8B, and Z a normal random number with mean −s²/2 and standard deviation s, so that energy scatters by about s around the token line. The 1.7 is an assumption, not a pilot number: the pilot's wall seconds per generated token put 4B at 2.06 times 1.7B and 8B at 1.443 times 4B, and 2.4535 = 1.7 × 1.443 keeps only the second ratio.
- **World B**: world A with c = 2.0618 for 4B, the pilot's own ratio of wall seconds per generated token.
- **World C**: the energy of an attempt is 100 × (that problem's pilot wall time for that model, in seconds) × e^Z, as if every model drew the same power.

None is joules. B and C replace A's assumed cost factor with the pilot's time; if 4B draws more watts than 1.7B, the real level-5 ratio is closer to 1 than in C. Two spreads were run, s = 0.2 (20%) and s = 0.3 (30%). The true ln(EPC 1.7B / EPC 4B) by level is −0.579, −0.458, +0.161, −0.160, +0.670 in world A, −0.772, −0.651, −0.032, −0.353, +0.477 in B, and −0.986, −0.877, −0.040, −0.343, +0.574 in C (ln is the natural logarithm; −0.579 means 1.7B costs e^−0.579 = 0.56 times what 4B costs, +0.670 means 1.95 times). In all three, 1.7B is cheaper at levels 1, 2 and 4 and 4B at level 5; level 3 is close to even.

Two bars decide which sizes pass: the **intended pattern** (1.7B resolved cheaper at level 1 or 2 and 4B resolved cheaper at level 5, where a level is **resolved** when the 0.99 interval of the ratio EPC 1.7B / EPC 4B lies wholly above 1 or wholly below 1, so the data decide which is cheaper; section 7.3 gives the rule) in at least 0.8 of campaigns, and coverage of at least 0.97 for every 0.99 interval checked (the primary ratio at levels 1 and 5, and each thinking-off configuration's EPC at levels 1 and 5). Every rate carries its **Monte Carlo standard error** (MC SE), the uncertainty from simulating finitely many campaigns: √(p(1 − p)/R) for a rate p over R campaigns.

**The draft's sizes (bench 200, energy 30 at every level), world A, R = 2,000 campaigns per spread:**

| Spread | L1 resolved, 1.7B cheaper | L2 resolved, 1.7B cheaper | L5 resolved, 4B cheaper | Intended pattern | Some level resolved the wrong way | Worst coverage of a 0.99 interval |
|---|---:|---:|---:|---:|---:|---:|
| 20% | 0.993 ± 0.002 | 0.996 ± 0.001 | 0.909 ± 0.006 | 0.908 ± 0.006 | 0.002 ± 0.001 | 0.977 ± 0.003 (8B, level 1) |
| 30% | 0.906 ± 0.007 | 0.980 ± 0.003 | 0.856 ± 0.008 | 0.851 ± 0.008 | 0.001 ± 0.000 | 0.979 ± 0.003 (8B, level 1) |

In worlds B and C the same sizes fall below the bar: intended pattern 0.470 ± 0.035 (94 of 200) and 0.550 ± 0.035 (110 of 200) in B, 0.705 ± 0.032 (141 of 200) and 0.600 ± 0.035 (120 of 200) in C, at 20% and 30% spread (`refuter-v2/DISPOSITIONS.md`; recounted by a deterministic rerun of its script, `refuter-v2.1/DISPOSITIONS.md` F2). Level 1 and 2 still resolve in nearly every campaign; level 5 does not. What is missing is the precision of level-5 accuracy, which the holdout supplies: 1.7B answers about a third of level-5 problems, and 170 problems fix that fraction only to about 12% of itself (one standard error). Bench attempts capture no power and the level-5 pool holds 871 problems, so the bench grew instead of the energy subset.

**Revision 2.1's sizes (bench 200, 200, 400, 400, 600; energy 30 at every level):**

| World | Spread | R | L1 resolved, 1.7B cheaper | L2 resolved, 1.7B cheaper | L4 resolved, 1.7B cheaper | L5 resolved, 4B cheaper | Intended pattern | Some level resolved the wrong way | Lowest coverage of the primary 0.99 interval (L1, L5) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 20% | 112 | 0.991 ± 0.009 | 1.000 ± 0.000 | 0.000 ± 0.000 | 0.991 ± 0.009 | 0.991 ± 0.009 | 0.000 ± 0.000 | 0.991 (L5) |
| A | 30% | 112 | 0.911 ± 0.027 | 0.955 ± 0.020 | 0.027 ± 0.015 | 0.982 ± 0.013 | 0.973 ± 0.015 | 0.009 ± 0.009 | 0.991 (L1) |
| B | 20% | 112 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.545 ± 0.047 | 0.946 ± 0.021 | 0.946 ± 0.021 | 0.000 ± 0.000 | 1.000 (L1) |
| B | 30% | 257 | 0.977 ± 0.009 | 0.992 ± 0.005 | 0.494 ± 0.031 | 0.864 ± 0.021 | 0.864 ± 0.021 | 0.004 ± 0.004 | 0.992 (L1) |
| C | 20% | 112 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.536 ± 0.047 | 0.955 ± 0.020 | 0.955 ± 0.020 | 0.009 ± 0.009 | 0.946 (L1) |
| C | 30% | 256 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.371 ± 0.030 | 0.902 ± 0.019 | 0.902 ± 0.019 | 0.000 ± 0.000 | 0.961 (L1) |

R differs because the two 30% rows of B and C pool two runs. Every world passes the power bar. World C fails the coverage bar at level 1: there the 0.99 interval of the primary ratio covered 0.946 ± 0.021 and 0.961 ± 0.012 (pooled over every size tried in C, 1,201 of 1,251 campaigns, 0.960), because 1.7B's level-1 pilot times sit above that model's fitted plane by a residual of 21% of their observed mean (below). Level 1 is still resolved the right way in every campaign there, its true ln ratio being −0.99. Near a level-1 tie, however, the same shortfall prints false verdicts ("When the decisions can be wrong", below). The bench cannot fix it, since level 1 holds only 217 problems, but the level-1 energy subset can. With level-1 energy 100 at these bench sizes, the refuter of revision 2.1 found level-1 coverage 0.990 ± 0.007 in world C at 20% (R 200). Revision 2.2 therefore sets the level-1 energy size, as follows.

**The level-1 energy size (revision 2.2).** The level-1 thinking-off energy subset m1 was chosen from 30, 50, 70 and 100, one value for all three thinking-off configurations, with the bench and levels 2 to 5 unchanged. m1 had to fit within the 200-problem level-1 bench and meet two bars. First, the level-1 primary 0.99 interval had to cover the truth in at least 0.97 of campaigns in worlds A, B and C at both spreads. Second, the false "cheaper size changes with level" rate had to be at most 0.02 in the near-tie world: world C with every 4B energy multiplied by one constant, 0.3729 = e^−0.986. That world keeps the pilot's own level-1 departure, makes level 1 an exact tie and leaves 4B cheaper at levels 2 to 5 (true ln ratios 0, +0.109, +0.946, +0.644, +1.560). Each setting ran R = 400 campaigns per world through the registered code with B = 4,000, using the orchestrator's generator (`/Users/edr/night-archive/difficulty-pack/v2.2-sims/`). The bench draws and each slot's energy noise were shared across m1, so the first 30 level-1 energy problems were the same at every m1, as in the nested lists. The near-tie world is computed from each world-C campaign by rescaling: multiplying one configuration's energies by a constant shifts every ln-ratio replicate by the same amount. On 120 campaigns run directly, the rescaled results matched to within 1.5 × 10⁻¹⁵. At R = 400, m1 = 50 sat on both bars (world C level-1 coverage 0.970 ± 0.009 at 30%; near-tie rate 0.0175 ± 0.0066). Before any further runs, the orchestrator fixed a rule: a candidate is judged on R = 800 in world C. Under that rule m1 = 50 failed and m1 = 70 passed.

| Level-1 energy m1 | Lowest level-1 primary 0.99 coverage, worlds A, B, C, both spreads | False "changes with level", near-tie world, 20% | Same, 30% | Lowest intended pattern | Added energy runs | Added machine time |
|---:|---:|---:|---:|---:|---:|---:|
| 30 (revision 2.1) | 0.935 ± 0.012 (C, 20%; R 400, refuter of revision 2.1) | 0.060 ± 0.012 (R 400, same) | not run | 0.883 ± 0.016 (B, 30%) | 0 | 0 |
| 50 | 0.976 ± 0.005 (C, 30%; R 800) | 0.021 ± 0.005 (R 800) | 0.024 ± 0.005 (R 800) | 0.845 ± 0.018 (B, 30%) | 60 | 1.5 h |
| **70** | **0.984 ± 0.004 (C, 20%; R 800)** | **0.015 ± 0.004 (R 800)** | **0.014 ± 0.004 (R 800)** | **0.853 ± 0.018 (B, 30%)** | **120** | **2.9 h** |
| 100 | 0.993 ± 0.004 (C, 30%; R 400) | 0.005 ± 0.004 (R 400) | 0.008 ± 0.004 (R 400) | 0.855 ± 0.018 (B, 30%) | 210 | 5.1 h |

Added energy runs are 3 × (m1 − 30). Added machine time is their generation, at the pilot's mean seconds per level-1 attempt (1.171, 3.141 and 5.214 s for 1.7B, 4B and 8B), plus the collection design's ordinary idle baseline of about 85 s before each run. For m1 = 70 that is 40 × 9.526 s = 0.11 h of generation and 120 × 85 s = 2.83 h of baseline. Waits and re-measured runs come on top. The intended pattern barely depends on m1, because level 1 already resolves; its weakest world (B, 30%) is 3.0 Monte Carlo standard errors above 0.8 at m1 = 70.

**The registered sizes (bench 200, 200, 400, 400, 600; energy 70, 30, 30, 30, 30).** R = 400 per world; world C and the near-tie world ("C, global 4B factor") R = 800:

| World | Spread | R | L1 resolved, 1.7B cheaper | L2 resolved, 1.7B cheaper | L4 resolved, 1.7B cheaper | L5 resolved, 4B cheaper | Intended pattern | Some level resolved the wrong way | Level-1 primary 0.99 coverage | Level-5 primary 0.99 coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 20% | 400 | 1.000 ± 0.000 | 0.990 ± 0.005 | 0.013 ± 0.006 | 0.988 ± 0.006 | 0.988 ± 0.006 | 0.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| A | 30% | 400 | 0.978 ± 0.007 | 0.985 ± 0.006 | 0.015 ± 0.006 | 0.968 ± 0.009 | 0.968 ± 0.009 | 0.003 ± 0.003 | 0.995 ± 0.004 | 0.998 ± 0.002 |
| B | 20% | 400 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.580 ± 0.025 | 0.940 ± 0.012 | 0.940 ± 0.012 | 0.003 ± 0.003 | 0.998 ± 0.002 | 0.998 ± 0.002 |
| B | 30% | 400 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.535 ± 0.025 | 0.853 ± 0.018 | 0.853 ± 0.018 | 0.010 ± 0.005 | 1.000 ± 0.000 | 0.988 ± 0.006 |
| C | 20% | 800 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.396 ± 0.017 | 0.953 ± 0.008 | 0.953 ± 0.008 | 0.003 ± 0.002 | 0.984 ± 0.004 | 0.998 ± 0.002 |
| C | 30% | 800 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.335 ± 0.017 | 0.941 ± 0.008 | 0.941 ± 0.008 | 0.004 ± 0.002 | 0.986 ± 0.004 | 0.991 ± 0.003 |
| C, global 4B factor | 20% | 800 | 0.015 ± 0.004 (false) | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | — | 0.016 ± 0.005 | 0.984 ± 0.004 | 0.998 ± 0.002 |
| C, global 4B factor | 30% | 800 | 0.014 ± 0.004 (false) | 0.000 ± 0.000 | 0.000 ± 0.000 | 1.000 ± 0.000 | — | 0.014 ± 0.004 | 0.986 ± 0.004 | 0.991 ± 0.003 |

In the near-tie world, 4B is truly cheaper at levels 2 and 4, so resolving 1.7B there would be wrong; it never happened. Every false "changes with level" came from resolving the tied level 1 for 1.7B. Each configuration's own level-1 EPC 0.99 interval covered 0.970 ± 0.006 (1.7B) and 0.975 ± 0.006 (4B) in world C at 20%, and 0.974 ± 0.006 and 0.983 ± 0.005 at 30% (R 800). In worlds A and B the lowest such coverage was 0.985 ± 0.006 (4B at 30% spread, in A and in B), apart from 8B (below). The full tables, with counts, are in `v2.2-sims/TABLES.md`. An independent re-check of this revision (Sol 6.1, `refuter-v2.2/sol.md`, its own generator and seeds, R 400 per world) found level-1 primary coverage 0.990 to 1.000 in worlds A, B and C. It found the intended pattern 0.855 ± 0.018 at its lowest (B, 30%), and a near-tie false "changes with level" rate of 0.020 ± 0.007 (8 of 400, 20%). Pooled with the orchestrator's 12 of 800, that is 20 of 1,200 = 0.017 ± 0.004. This meets the 0.02 bar as a point estimate, but it does not show that the true rate is below 0.02.

Other sizes, in worlds B and C (about 120 campaigns each; 20% / 30% spread): level-5 bench 400 with levels 3 and 4 at 200 gave intended pattern 0.889 / 0.761 (B) and 0.957 / 0.897 (C); levels 3 to 5 at 400 gave 0.819 (B, 30%) and 0.983 / 0.949 (C); level-5 energy 40 instead of 30 gave no gain (0.775 in B and 0.892 in C, 30%, levels 3 to 5 at 400). Level 5 at 600 is taken for the margin in world B at 30% spread, and levels 3 and 4 at 400 because they raise the chance of resolving level 4 (true ratio about 0.71 in B and C, 1.7B cheaper) from about 0.11 to between 0.4 and 0.55. A bench above 217 is impossible at level 1, whose pool holds 217 problems, and levels 1 and 2 already resolve. In world A the level-3 and level-4 ratios (1.17 and 0.85) are rarely resolved at any size tried, the correct behaviour for ratios this close to 1. At levels 2 to 5 energy stays at 30: energy 20 at every level also passed the power bar in world A (intended pattern 0.890 ± 0.005 at 20% and 0.809 ± 0.004 at 30% over 7,652 campaigns, 1.9 Monte Carlo standard errors above 0.8), but its 8B level-1 coverage, 0.970 and 0.971, sat on the 0.97 bar within Monte Carlo error; version 1's energy shape (20, 20, 40, 40, 40) was about as powerful in world A (0.850 ± 0.008 at 30%, 0.921 ± 0.006 at 20%) and needs 480 runs against revision 2.1's 450.

**A cell the sizes cannot fix.** The 0.99 interval of 8B thinking-off EPC at level 1 covered between 0.969 and 0.988 at every size simulated in world A, with no trend in bench or energy size; its printed 0.95 interval covered 0.927 and 0.940 at bench 200 and energy 30. At the registered sizes with level-1 energy 50, 70 and 100 (R 400 each, 20% / 30% spread) the 0.99 interval covered 0.978 / 0.978, 0.973 / 0.968 and 0.978 / 0.973, and the 0.95 interval 0.938 / 0.925, 0.945 / 0.910 and 0.933 / 0.925. The pilot's level-1 8B lengths have one problem at 5.5 times the mean length (2,007 tokens against a mean of 366.3). The primary estimate (section 6.6) predicts energy from the holdout's tokens; when a check (section 6.8) finds a level's energy departing from that prediction, the cell falls back to the simpler direct estimate (mean energy divided by accuracy, section 6.3), and in this cell the direct interval undercovers. This is printed beside that cell (section 8.3). The larger level-1 energy subset of revision 2.2 did not change this, within Monte Carlo error.

**When the decisions can be wrong.** Section 7.1's bound of 0.05 on any false primary decision holds only if every level's 0.99 interval reaches its coverage. The refuter of this version and the orchestrator ran worlds in which the truth is known through the registered code, at the draft's sizes unless marked (R = 200 unless shown; where there are two numbers, the second is the orchestrator's independent rerun with its own generator and seeds):

| World: what is true in it | Some level falsely resolved | "Changes with level" printed falsely |
|---|---:|---:|
| A, with the level-3 ratio moved to +0.08 | 0.005 ± 0.005; 0.005 ± 0.005 | 0; 0 |
| A, level-3 ratio +0.08, with 5% of 1.7B level-3 runs at five times the energy | 0 | 0 |
| A, with 1.7B's energy growing faster than its tokens (G(1 + G/1000) instead of G) | 0 | 0 |
| Null 1: every ratio 1, made by multiplying 1.7B's joules per token by 1.78, 1.58, 0.85, 1.17 and 0.51 at levels 1 to 5 | 0.110 ± 0.016 (R 400); 0.095 ± 0.021 | 0; 0 |
| Null 1 drawn without replacement from pools of the real sizes | 0.140 ± 0.025 | 0 |
| Null 2: every ratio 1; 100 J per attempt, equal accuracies, each model right where the other is wrong (nearly complementary: in each odd-sized pool one problem is right for both) | 0.125 ± 0.023; 0.095 ± 0.021 | 0.010 ± 0.007; 0 |
| Null 3: null 1 with 0.5% of 1.7B level-1 runs at 101 times the energy, tokens unchanged | 0.665 ± 0.033 | 0 |
| A, level-3 ratio +0.08, with that 101-fold excursion at level 3 | 0.140 ± 0.025 | 0 (a true change verdict listed level 3 wrongly in 0.100 ± 0.021) |
| Null 1, revision 2.1 sizes (level-1 energy 30) | 0.063 ± 0.023 (R 111); 0.120 ± 0.016 (R 400, refuter of revision 2.1) | 0; 0 |
| Null 2, revision 2.1 sizes | 0.063 ± 0.023 (R 111); 0.038 ± 0.010 (R 400, same) | 0; 0 |
| Near tie: world C with every 4B energy × 0.3729 (level 1 tied, 4B cheaper at levels 2 to 5), revision 2.1 sizes | 0.060 ± 0.012 (R 400, refuter of revision 2.1) | 0.060 ± 0.012 |
| The same near tie, registered sizes (level-1 energy 70) | 0.016 ± 0.005 (R 800); 0.014 ± 0.004 at 30% spread | 0.015 ± 0.004; 0.014 ± 0.004 at 30% |

Each failure but the near tie needs a departure the pilot does not show. Null 1's false resolutions come from the model-based estimate when the misfit check (6.8) misses a level whose joules per token are off the configuration's line: at level 1, 17 of 81 campaigns resolved falsely when both cells used the model estimate, against 1 of 103 when 1.7B fell back to the direct one (refuter's 200 campaigns). Fitting the plane of 6.5 to the pilot's wall times (each model's 100 thinking-off answers, time standing in for energy), the levels depart from it by 0.1 to 4.9% (each level's mean residual as a fraction of its observed mean time), except 1.7B at level 1 by +21% (its fitted mean is 27% below the observed one), which is the kind of departure the misfit check exists for (on a complete synthetic pack built from those times it flagged that cell). Null 2 needs correctness that is anti-correlated between the two models; in the pilot it is positively correlated or near zero (7.2). Null 3 needs a rare energy excursion that the token counts do not show: thirty runs miss a 0.5% excursion 86% of the time, and no estimator recovers what the sample lacks; a 101-fold energy at the same tokens means a run about 100 times as long or at 100 times the power, which the physical flags of 5.1 are there to catch. Resampling both configurations on the same problems (paired streams) removed null 2's false resolutions (0.005 ± 0.005) but raised null 1's (0.150 ± 0.025) and lowered level-3 coverage, in world A with the level-3 ln ratio moved to +0.08, to 0.955 ± 0.015 (191 of 200; in ordinary world A, paired, 0.975 ± 0.011, 195 of 200, a difference not claimed significant), so the registered independent streams stay. The near tie needs none. It keeps the pilot's own times, including the 21% level-1 departure. Its one constant factor on 4B's energy is something the pilot cannot rule out, because the pilot timed answers without measuring power. At revision 2.1's level-1 energy of 30, the misfit check missed the 1.7B level-1 departure often enough that the model estimate put 1.7B cheaper than 4B at the tied level, so the code printed a false "cheaper size changes with level" in 0.060 ± 0.012 of campaigns. With level-1 energy 70 the rate is 0.015 ± 0.004. The misfit check firing more often is not most of the gain. In world C, 1.7B's level-1 cell fell back to the direct estimate in 0.74 and 0.41 of campaigns at 20% and 30% spread, against 0.67 and 0.42 at energy 30. The larger level-1 sample makes both level-1 estimates more precise, and level 1 has more weight in the fitted plane. The null worlds were not re-run at level-1 energy 70. These rates are printed with the results (section 8.3).

**Limits of the simulation.** Its population is the pilot's 20 problems per level; real pools hold 217 to 871 problems with tails the pilot may not have met. In worlds A and B energy follows tokens exactly, times a random factor, so the token prediction is right by construction; world C uses the pilot's measured times, which depart from one line per model by up to 21% of the observed level mean (1.7B at level 1, above), so it exercises the check of section 6.8. No world is joules.

### 4.2 Thinking-on sizes (not simulated)

Bench 64 and energy 20 per level are the spec's sizes, from the pilot's accuracy sizing (about ±10% on accuracy). Thinking-on configurations are never in the primary question. The executing review found that the 44-problem holdout can miss a rare very long problem: in the pilot's 4B thinking-on level 4, one problem ran to the 16,384 cap, held 21% of that level's tokens and was its only wrong answer; a 44-problem holdout misses it with probability 0.95^44 = 0.105, and that cell's 0.99 interval covered 0.89 in simulation. Thinking-on intervals are therefore printed as descriptive and carry the caveat of section 8.3 wherever the cell's bench contains a capped answer.

### 4.3 Machine time

From the pilot's mean seconds per attempt (thinking off, 4,096 cap, measured while other jobs ran, so upper bounds for a quiet machine): the 570 thinking-off energy attempts need about 1.02 h of generation (12.0 min for 1.7B, 19.8 for 4B, 29.3 for 8B; revision 2.1's 450 needed 0.91 h), and the 5,400 thinking-off bench attempts about 13.0 h (2.8 h for 1.7B, 4.1 for 4B, 6.0 for 8B; the draft's 3,000 needed 6.1 h). 4B thinking on needs about 3.8 h for its 64-per-level bench and about 1.2 h (20/64 of that) for its energy attempts; 8B thinking on about 5.6 h of bench. These exclude the idle baseline before each energy run, waits between runs and re-measured attempts. With the ordinary 85 s idle baseline before each run, the thinking-off energy runs take about 570 × 85 s + 1.02 h = 14.5 h of session time, 2.9 h more than revision 2.1's 450 runs.

## 5. Rows, flags, retries, and what counts

### 5.1 Rows and flags

Each bench attempt becomes one row of `bench.csv`; each energy attempt one row of `energy.csv` per boundary. Rows carry an **attempt number** (1 for the first time a configuration tried a problem, 2 for the second, and so on) and **flags**: short names of conditions recorded on the row. A flag never deletes a row; this section says which flags keep a row out of which computation. Every table is computed in two **lines**: the **primary line**, on which the claims rest, and the **flagged-inclusive line**, which keeps the rows that carry physical flags (5.4 gives the exact rule and an example).

| Flags | Meaning | Effect |
|---|---|---|
| `bad_number`, `bad_level`, `bad_mode`, `unknown_item`, `unknown_config`, `not_selected`, `unknown_boundary`, `duplicate`; on bench rows also `missing_text` | the row cannot be used as written: an unreadable number, a level or mode outside the design, a problem or configuration not registered, a problem not in that mode's registered list, a second row for the same attempt or a later attempt after a usable one | **always excluded**: never used |
| `runtime_failed` | the program failed; the row is not a model answer | never used; the attempt is re-run |
| `agent_overlap`, `sleep`, `contention_above_level`, `idle_wait_cap` | **physical flags**, written by the energy adapter: the run overlapped a sighting of an AI agent process on the machine (an agent draws 8 to 47 W when idle); the machine slept during the run; another process's power during the run exceeded the level set by the collection design (below); the idle wait before the run reached its 1,500 s limit | not used in the primary line; used in the flagged-inclusive line; the attempt is re-measured |
| `repetition_loop`, `loop_check_words`, `bad_flag`, `not_in_bench`, `token_mismatch`, `unknown_finish_reason`, `battery_assist`, `contention`, any other adapter flag | recorded conditions that do not make a measurement wrong: a loop in the answer (5.5), a malformed incoming flag, an energy row with no bench row or a different token count from it, a contention below the level | used, and counted in the output |

An answer cut off at the cap is used and scored wrong (column `cap_hit`), and so is an answer with a repetition loop.

**The contention level.** The level above which outside power excludes a run is the collection design's (`docs/design/block6_collection_draft.md` section 13, decision 2): the outside power at which the added energy reaches one quarter of the smallest detection floor the paper prints (a detection floor is the smallest energy difference the project's method can tell apart from noise), with watts measured on the quiet machine. This registration does not set it. The level in force at the first DIFFICULTY energy session is the registered one; the energy adapter writes the level it used into each session's record. The estimator only maps flag names.

**Physical flags belong on energy rows only.** A correct or wrong answer does not depend on whether an agent was running, so the recorder writes the four physical flags only into `energy.csv`, never into generation records. The pinned code treats a bench row carrying one as excluded from the primary line; if that happens, the problem is generated again.

### 5.2 Retries and duplicates

A **key** is (configuration, problem) for bench rows and (boundary, configuration, problem) for energy rows. Within a key, rows are ordered by attempt number:
1. A row with the same key and attempt number as an earlier row is a `duplicate`.
2. The first row carrying none of the excluding flags (the always-excluded set, `runtime_failed` and the four physical flags) is the key's **selected row**. Every later attempt is a `duplicate`.
3. Every other row of a key that has a selected row (an earlier attempt carrying an excluding flag, which is **replaced**, or a later `duplicate`) stays in the files, is counted in the cell's `replaced_rows`, and is not used in the primary line. `rows_not_used` counts every unused row of the cell, whether or not its problem has a selected row.

**Ruling (spec section 14 item 2, left open by the spec and the review).** Replacement covers every excluding flag, physical ones included, as the pinned code does. Collection re-measures an attempt that carries an excluding flag, in the same or a later session, until each selected problem has a usable row at both boundaries or the end date arrives. Reasons: an excluded attempt has no usable energy; without a re-measurement the problem silently leaves the sample, and long runs, which overlap agents and contention more often, would leave it more often, tilting the sample toward short problems; and the flag is a physical reading written before anyone sees the energy (energies are hidden until release, section 9), so a retry cannot be chosen by its result. The flagged-inclusive line (5.4) keeps the first attempt, so nothing is hidden. The collection design's rule "a measured science run that failed is never replaced" concerns its replication units, whose count is the design; here the unit is a selected problem. There is no limit on attempts; the end date bounds them, and every replaced row is counted in the output.

Worked example (spec case P item 3). Bench problems i00 to i24 all clean; energy subset {i00, i01}; energy rows i00 attempt 1 `runtime_failed`, i00 attempt 2 clean, i01 attempt 1 clean. Result: two energy rows used, `replaced_rows` 1, no duplicate, holdout 23 problems, cell complete. A further clean i01 attempt 2 would be a `duplicate`: still two energy rows used, and `replaced_rows` 2.

### 5.3 Targets and complete cells

A **cell** is one combination of line (primary or flagged-inclusive), boundary, configuration and level. Its targets come from the registered sizes, never from the data: with thinking off, energy 70, 30, 30, 30 and 30 and bench 200, 200, 400, 400 and 600 (holdout 130, 170, 370, 370 and 570); 64, 20 and 44 with thinking on. A cell is **complete** when its used bench rows, used holdout rows and used energy rows all equal their targets, **missing** when it has no used bench and no used energy rows, and **short** otherwise. The holdout is defined by the registered lists, so a missing energy row never moves its problem into the holdout.

A measured configuration always takes part in every comparison, complete or not. An optional configuration with no row in either file is `not_measured` and is left out of every comparison; with any row it takes part like the others.

### 5.4 Two lines: primary and flagged-inclusive

Every table is computed twice:
- **primary**: excludes the always-excluded flags, `runtime_failed` and the four physical flags. This is the line the claims rest on.
- **flagged-inclusive**: excludes the always-excluded flags and `runtime_failed` only. For each key it uses the first attempt that is not always-excluded or `runtime_failed`, physical flag or not. It is the result had nothing been excluded for physical reasons and nothing re-measured, with one row per problem in both lines.

Worked example (spec case Q). One cell, energy target 5, energies 10, 10, 10, 10 and 1,000 J, the last flagged `contention_above_level`. Primary: 4 rows, mean 10 J, cell short. Flagged-inclusive: 5 rows, mean 208 J. After a clean re-measurement of the flagged problem at 12 J: primary 5 rows, mean 10.4 J, one replaced row, cell complete; flagged-inclusive still uses the first attempt, mean 208 J. Had the flag been the plain `contention` (below the level), both lines would use all five, mean 208 J.

### 5.5 Repetition loops

A small model sometimes repeats the same passage until the cap. The scorer flags it, and the flag never excludes. Take the generated sequence (token ids when the recorder writes them; otherwise words, and the row also gets `loop_check_words`), keep its last quarter (rounded up), and for every run of 20 consecutive units count its non-overlapping occurrences in that tail from the left; if any reaches 3, the row gets `repetition_loop`. Worked example (spec case R): 180 distinct tokens followed by the same 20 tokens three times is flagged; 300 distinct followed by that block twice is not; the block three times followed by 300 distinct is not (the repeats lie in the first three quarters). On the pilot's text (words, since it kept no token ids) the detector flags 12 of the 15 thinking-off answers that hit the 4,096 cap (13 by eye) and 36 of all 633 answers. The output prints the loop rate of every cell.

## 6. Estimators

Notation for one cell: the holdout has n_h problems, k_h of them answered correctly, with prompt tokens P_j and generated tokens G_j; the energy subset has m attempts with energies E_i and token counts P_i, G_i. Two confidence levels are used, never combined: **descriptive** c_d = 0.95 for every interval printed as description, and **decision** c_D = 0.99 only for the decisions of section 7. A **standard error** is the spread an estimate would show across repetitions of the experiment, estimated from the data. Student's t quantile t_df(q) is the multiplier that gives probability q with df degrees of freedom (the number of independent pieces of information left for estimating scatter: for a mean of m values, df = m − 1; t_29(0.975) = 2.045230 at m = 30). The worked examples are the code's acceptance cases (spec section 12: fixed inputs whose outputs the code's tests require to the printed digits); their values were recomputed with the registered code for this registration.

### 6.1 Accuracy

Headline accuracy p = k/n over all used bench rows of the cell, with the **Wilson score interval** at c_d (it stays within 0 and 1 and behaves at 0 or n correct, both likely here): with z = 1.959964 (the normal quantile for 0.95), centre = (p + z²/(2n)) / (1 + z²/n), half-width = z·√(p(1 − p)/n + z²/(4n²)) / (1 + z²/n). Worked example (case A): 15 of 20 correct, p = 0.75; z² = 3.841459, z²/n = 0.192073; centre 0.709719, half-width 0.178420; interval [0.531299, 0.888138]. Also printed: holdout accuracy p_h = k_h/n_h, mean generated tokens, cap-hit rate and loop rate over the bench, and mean prompt and generated tokens over the holdout.

### 6.2 Mean energy per attempt

Ē = (E_1 + … + E_m)/m, with the interval Ē ± t_{m−1}(0.975)·s/√m, s the sample standard deviation (divisor m − 1); needs m ≥ 2. Worked example (case B): energies 100, 120, 140, 160 and 180 J; Ē = 140 J, s = 31.62278, s/√5 = 14.14214, t_4 = 2.776445, half-width 39.26486; interval [100.7351, 179.2649] J.

### 6.3 Direct EPC (secondary estimator)

EPC_direct = Ē / p_h. The accuracy comes from the holdout, not from the energy problems: wrong answers run longer, so if the same problems fed both Ē and p, a draw of hard problems would raise one and lower the other together and the interval would be too narrow. The holdout and the energy subset share no problem, so the two are independent. Interval: **MOVER** (method of variance estimates recovery; Zou and Donner, 2008), which combines the two intervals on the log scale. With D = ln Ē − ln p_h, the lower bound is exp(D − √((ln Ē − ln E_lo)² + (ln p_h,hi − ln p_h)²)) and the upper exp(D + √((ln E_hi − ln Ē)² + (ln p_h − ln p_h,lo)²)), using the t interval of Ē and the Wilson interval of p_h, both at c_d. Statuses: `ok`; `not_estimable_zero_correct` (k_h = 0, including n_h = 0); `not_estimable_few_attempts` (m < 2); `energy_lower_nonpositive` (E_lo ≤ 0, lower bound printed as 0). Worked example (case C): energies of case B, holdout 15 of 20 correct; EPC = 140/0.75 = 186.6667 J; D = 5.229324; lower exp(5.229324 − 0.370024) = 128.934 J, upper exp(5.229324 + 0.424229) = 285.303 J.

### 6.4 Joules per generated token

R = ΣE_i / ΣG_i (prompt energy included; the marginal cost of a token is b_g of 6.5). Interval R ± t_{m−1}(0.975)·se with d_i = E_i − R·G_i, se = √(Σd_i²/(m − 1) / (m·Ḡ²)). Worked example (case D): energies of case B, generated tokens 50, 70, 80, 90 and 110; R = 700/400 = 1.75 J per token; d = 12.5, −2.5, 0, 2.5, −12.5; se = √(81.25/(5 × 6,400)) = 0.0503891; interval [1.610097, 1.889903] J per token.

### 6.5 Decomposition of energy into tokens

Per line, boundary and configuration, over the N used energy rows of all five levels (N = 190 at the thinking-off target, 100 at the thinking-on), an **ordinary least squares** fit (the plane that makes the sum of squared differences between measured and fitted energy smallest) of E = a + b_p·P + b_g·G: a is the energy that does not follow tokens (J), b_p the joules per prompt token, b_g the joules per generated token. Standard errors come from σ²(XᵀX)⁻¹ with σ² = RSS/(N − 3), where RSS is the sum of squared **residuals** (measured minus fitted energy) and X the table of 1, P and G; each coefficient gets the interval estimate ± t_{N−3}(0.975)·standard error. Also printed: R² = 1 − RSS/TSS (TSS the sum of squared differences of E from its mean), the R² of E on G alone, the generated-token share b_g·Ḡ/Ē, and per level the mean residual with its t interval (section 6.8 adds a second interval for it). Status `few_rows` when N < 4 and `singular` when the token columns cannot separate the coefficients (tested exactly on the integer token counts). Worked example (cases E and F): six rows (P, G) = (100, 50), (120, 70), (80, 80), (150, 90), (110, 110), (90, 60) with E = 10 + 0.5P + 1.5G plus noise 2, −1, 0, −2, 1, 0, that is E = 137, 174, 170, 218, 231, 145 J. Fit: a = 13.980831 J (standard error 3.137012), b_p = 0.465176 (0.027441), b_g = 1.497284 (0.031545); t_3 = 3.182446; intervals a [3.997459, 23.964202], b_p [0.377846, 0.552506], b_g [1.396896, 1.597673]; R² = 0.999164; generated-token share 0.640698. Without the noise the fit returns a = 10, b_p = 0.5, b_g = 1.5 exactly.

### 6.6 Model-based EPC (primary estimator)

**The problem it solves.** At easy levels the mean energy of a few dozen attempts is dominated by rare long answers. The pilot's 8B thinking-off level-1 answers were 127, 180, 184, 184, 193, 198, 209, 216, 231, 231, 238, 244, 258, 290, 344, 369, 417, 450, 756 and 2,007 tokens long (mean 366.3, standard deviation 1.12 times the mean). A sample of 20 misses the 2,007-token kind of problem with probability 0.95^20 = 0.36 (0.95^30 = 0.21 at 30; 0.95^70 = 0.028 at 70, the level-1 energy size), and version 1's interval covered 0.83 at nominal 0.99. Energy follows tokens closely (the pilot's decode rate, tokens written per second, was nearly constant within a model: 156 to 260, 87 to 106 and 57 to 73 tokens per second for 1.7B, 4B and 8B), so the long tail can be measured where problems are many, in the holdout's token counts (130 problems at level 1; a 1-in-20 kind is missed with probability 0.95^130 = 0.0013), with the energy subset supplying only the joules-per-token coefficients.

**Definition.** With the fit (a, b_p, b_g) of 6.5 for the cell's line, boundary and configuration (one fit over all five levels) and the holdout means P̄_h and Ḡ_h of level L:

μ_L = a + b_p·P̄_h + b_g·Ḡ_h (the fitted energy of an average holdout attempt), and EPC_model = μ_L / p_h.

The holdout and the energy subset share no problem, so the coefficients and the holdout means come from independent samples; the holdout's token means and accuracy come from the same problems, and the resampling of 6.7 draws them together. Statuses: `ok`; `fit_few_rows` or `fit_singular`; `few_attempts` (fewer than 2 energy rows at this level); `zero_correct` (k_h = 0 or n_h = 0); `nonpositive` (μ_L ≤ 0); `bootstrap_invalid` (some resampled copy of the data in 6.7 could not be fitted, or gave μ ≤ 0). The point is printed whenever it can be computed; its interval only with status `ok`.

Worked example (case L). Energy rows (P, G, E): level 1 (100, 50, 135), (120, 70, 175), (80, 80, 170); level 2 (150, 90, 220), (110, 110, 230), (90, 60, 145); the fit is exact, a = 10, b_p = 0.5, b_g = 1.5. Level-1 holdout (P, G, correct): (100, 60, 1), (110, 80, 1), (90, 100, 0), (100, 40, 1), so P̄_h = 100, Ḡ_h = 70, p_h = 0.75; μ_1 = 10 + 50 + 105 = 165 J and EPC_model = 165/0.75 = 220 J. The direct estimator gives (135 + 175 + 170)/3 / 0.75 = 213.33 J. Level-2 holdout (130, 100, 1), (150, 120, 0): μ_2 = 10 + 70 + 165 = 245 J, p_h = 0.5, EPC_model = 490 J; direct 198.33/0.5 = 396.67 J.

### 6.7 Resampling (the bootstrap)

An interval for EPC_model has no simple formula, so it comes from a **bootstrap**: the experiment is imitated many times by drawing problems with replacement from those actually measured, the estimate is recomputed on each draw (a **replicate**), and the spread of the replicates gives the interval. Problems, not single numbers, are drawn, so a replicate keeps each problem's tokens, energy and correctness together.

For each line, boundary and configuration there is one random stream, Python's `random.Random` seeded with the text `joulewise.packs.difficulty.v2.bootstrap/<line>/<boundary>/<model>/<mode>` (for example `joulewise.packs.difficulty.v2.bootstrap/primary/rails/qwen3-1.7b/off`). Each configuration's stream ignores every other configuration, so adding the optional configuration changes no other configuration's numbers. Per level the used energy rows (m_L of them) and used holdout rows (n_L) are sorted by problem id. Each of B = 4,000 replicates then:
1. for levels 1 to 5 with m_L ≥ 1, draws m_L indices, each `randrange(m_L)` (a whole number from 0 to m_L − 1, each equally likely), and takes those energy rows;
2. then for levels 1 to 5 with n_L ≥ 1, draws n_L indices, each `randrange(n_L)`, and takes those holdout rows;
3. refits the plane of 6.5 on all drawn energy rows together, giving a*, b_p*, b_g* (fewer than 4 rows or a singular refit makes the replicate invalid);
4. per level, records r*, the mean energy Ē* of the level's drawn energy rows minus what the refit predicts for those rows (the misfit statistic of 6.8), and, with the drawn holdout's token means P̄*, Ḡ* and accuracy p* = k*/n_L, the fitted energy μ* = a* + b_p*·P̄* + b_g*·Ḡ* and the replicates EPC*_model = μ*/p* and EPC*_direct = Ē*/p* (+∞ when k* = 0).

Levels are drawn separately (stratified), because the design fixes each level's size. The draws depend only on the seed and the counts: in a complete thinking-off cell the first level-1 indices of the stream above (each `randrange(70)`) are 30, 32, 34, 9, 64, 35, 60, 54, 66, 60, whatever the data (with revision 2.1's 30 they were 7, 26, 8, 8, 2, 28, 16, 20, 26, 8).

**Percentile interval** of B replicates at confidence c: sort them, let k = max(1, ⌊B(1 − c)/2 + 10⁻⁹⌋), and take the k-th smallest and the k-th largest. At B = 4,000 that is the 100th and the 3,901st values at 0.95, and the 20th and the 3,981st at 0.99. Point estimates always come from the original data, never from the replicates.

Worked example (case N, configuration 1.7B, seed `case-N`, replicate 1). Eight energy rows per level at levels 1 and 2, twelve holdout rows per level. The stream `case-N/primary/rails/qwen3-1.7b/off` draws energy indices 1, 1, 7, 7, 0, 0, 1, 0 (level 1) and 4, 4, 1, 5, 0, 0, 7, 7 (level 2), then holdout indices 1, 3, 6, 11, 1, 9, 1, 4, 11, 6, 10, 6 and 3, 2, 5, 7, 6, 0, 2, 1, 0, 4, 9, 11. The refit on the 16 drawn energy rows gives a* = 13.1418, b_p* = 0.065525, b_g* = 0.410499. The drawn level-1 holdout has P̄* = 116.5, Ḡ* = 293.75 and 10 of 12 correct, so μ* = 141.360 J and EPC*_model = 141.360/(10/12) = 169.632 J; the direct replicate is Ē*/p* = 99.969/(10/12) = 119.962 J. Over 200 such replicates the 0.95 percentile interval of EPC_model at level 1 is [112.843767, 194.765079] J, around the point 146.127273 J.

### 6.8 The misfit rule

One fitted plane serves all five levels. If one level's energy departs from it (for example, an energy cost that does not follow tokens), the model-based estimate of that level is biased, so the level is tested. The misfit statistic of level L in a replicate is r* = Ē* − (a* + b_p*·P̄*_E + b_g*·Ḡ*_E): the mean energy of that level's drawn energy rows minus what the replicate's refit predicts for them. Level L is a **misfit** when the 0.95 percentile interval of its r* replicates lies above τ or below −τ, with τ = 10⁻⁹ × max(1, mean used energy of the configuration in this line and boundary) (so an exact fit is never called a misfit through rounding). The test needs all B replicates valid; otherwise it is not made, and the model estimate is `bootstrap_invalid` anyway.

The interval comes from the bootstrap and not from a t interval of the level's residuals (still printed), because the t interval ignores the error of the fitted coefficients; at level 1, where energies are small, that error dominates, and the t version flagged false misfits in 18% of simulated campaigns for 8B level 1 against an intended 5% (spec section 8.8).

Worked example (case M, 200 replicates). Five levels of four energy rows each, built as 10 + 0.5P + 1.5G plus small noise, with 12 J added at level 3. The fit is a = 33.503039, b_p = 0.271248, b_g = 1.542626. The 0.95 intervals of r* are level 1 [−5.748090, 0.946453], level 2 [−4.415225, 1.460235], level 3 [5.579092, 11.109952], level 4 [−6.475269, 2.171315], level 5 [−5.407524, 0.914395]. Only level 3's lies wholly above zero, so level 3 is a misfit.

### 6.9 Which EPC a cell reports

```
model-based status ok, and level not a misfit? ── yes ──> primary source = model
        │ no
        v
at least 1 correct in holdout and at least 2 energy rows? ── yes ──> primary source = direct
        │ no                                                (reason: misfit, or model_<status>)
        v
no EPC: status not_estimable_zero_correct or not_estimable_few_attempts
```

Each line ending in "?" is a test on the cell; "yes" and "no" are its answers; the last line is the outcome when both tests fail. The **source** is which estimator the cell reports. The reported EPC is the chosen source's point, with the 0.95 percentile interval of that source's replicates (the direct source also takes its interval from the bootstrap; its MOVER interval of 6.3 stays in its own columns as the secondary). The test is made once on the original data. In case M, level 3 reports the direct EPC 175.75/(5/6) = 210.9 J with interval [162.25, 518.25] J, while levels 1, 2, 4 and 5 report the model EPC 211.030519 J; the output lists `m/off:3` as a misfit cell.

## 7. Comparisons and decisions

### 7.1 Two confidences

A decision is taken at c_D = 0.99 and described at c_d = 0.95, from the same replicates. The primary question makes five decisions (one per level). If each level's 0.99 interval reached its nominal coverage, the chance of any false decision across the five would be at most 0.05 (Bonferroni's bound: five chances of 0.01). That is a condition, not a guarantee: the bootstrap's coverage depends on the data, and section 4.1 ("When the decisions can be wrong") prints the simulated worlds where the bound held and those where it failed (up to 0.11 to 0.14 when one configuration's joules per token differed between levels by 15 to 78%, 0.67 with a rare energy excursion the token counts do not show, and 0.06 near a level-1 tie at level-1 energy 30, which is 0.016 at the registered 70). This family is the primary question on the rails boundary in the primary line. The wall boundary, the flagged-inclusive line and the secondary comparison are printed beside it and are not further decisions in that family. Worked example (case O): replicates d_b = b/100 − 0.03 for b = 1 to 200. At 0.95, the rank of 6.7 is k = 5 and the interval is [0.02, 1.93], which excludes zero; at 0.99, k = 1 and the interval is [−0.02, 1.97], which contains zero, so the decision is unresolved although the description excludes zero.

### 7.2 Who may be compared

A configuration is **eligible** at a level when its cell is complete (5.3) and its EPC is estimable (6.9). For two eligible configurations x and y, replicate b of ln(EPC_x/EPC_y) is ln EPC*_x,b − ln EPC*_y,b, each from its own primary source and its own stream, paired by replicate number (+∞ − (+∞) is taken as 0: both draws had no correct answer, which says nothing about order). The point is ln(EPC_x/EPC_y) from the reported points. The streams are independent although the configurations answer the same problems. That widens the interval when the two configurations' token counts and correctness rise and fall together across problems, as in the pilot (thinking off, 1.7B against 4B on the same 20 problems per level: correlation of generated tokens +0.41 to +0.95 at every level; of correctness +0.31 to +0.64 at levels 3 to 5 and −0.05 at levels 1 and 2, where 18 of 20 problems were right for both); in world A of section 4.1 the 0.99 coverage was 0.995 to 0.998, above nominal. It narrows the interval when they move in opposite directions: in a constructed world where each model was right where the other was wrong (except one problem right for both in each odd-sized pool), the per-level false-resolution rate was 0.015 to 0.045 against a nominal 0.01. Resampling both configurations on the same problems (paired streams) was tried and not adopted (section 4.1).

### 7.3 The primary question

For a = `qwen3-1.7b/off` and b = `qwen3-4b/off`, at each level, the decision interval is the 0.99 percentile interval of the ln ratio replicates, and the descriptive interval the 0.95 one:
- **resolved, 4B cheaper** when the decision interval lies wholly above 0 (EPC_1.7B > EPC_4B);
- **resolved, 1.7B cheaper** when it lies wholly below 0;
- **unresolved** when it contains 0;
- **unresolved, incomplete** when either configuration is not eligible; the reason (for example `qwen3-4b/off:short`) is printed.

**The cheaper size changes with level** when two levels are resolved with different cheaper configurations; every resolved level is listed. Otherwise the verdict is **no resolved change**.

Worked example (case N, 200 replicates; two configurations whose energies differ by a factor of 2 at equal tokens). Level 1: EPC 146.127273 J (1.7B) against 267.9 J (4B), ln ratio −0.606136 (ratio 0.545); descriptive [−0.963820, −0.239224]; decision [−1.037935, −0.101456], wholly below zero: resolved, 1.7B cheaper. Level 2: 286.425 J against 458.28 J, ln ratio −0.470004 (ratio 0.625); decision [−1.002726, 0.507957] contains zero: unresolved. Verdict: no resolved change.

### 7.4 Secondary: cheapest of all measured configurations

At each level, over every configuration that takes part (5.3): the cheapest is the eligible one with the lowest EPC point (ties broken by name). Each other eligible configuration r (a **rival**) is **beaten** when the 0.99 decision interval of ln(EPC_r/EPC_cheapest) lies wholly above 0. Status: **resolved** when every configuration is eligible and every rival is beaten; **unresolved** when all are eligible and some rival is not beaten (those are listed as tied); **unresolved, incomplete** when any configuration is not eligible (the cheapest among the eligible is still printed, with the ineligible and their reasons); **none estimable** when no configuration is eligible. A non-estimable rival never disappears from the comparison. Zero correct is not estimable rather than "infinitely expensive": with 0 of 170 correct the true accuracy could still be 3.8% (the 0.99 Wilson upper bound), which a bootstrap cannot see (every resampled copy also has zero correct). The cheapest **changes with level** when two resolved levels have different cheapest configurations. Worked example (case P item 1): configuration A with 180 of 180 correct and twenty 100 J attempts; B with 0 of 180 correct and twenty 1 J attempts. Result: unresolved, incomplete; cheapest among the eligible A; incomplete `B:not_estimable_zero_correct`. Version 1 called A resolved.

## 8. What is printed, in every outcome

### 8.1 Tables

For each line (primary, flagged-inclusive) and boundary (rails, wall), from `scripts/difficulty_estimate.py` (section 10): `cells.csv` (every configuration that takes part, every level, data or not: cell status, targets and counts, accuracy and its interval, token, cap-hit and loop rates, holdout accuracy and token means, mean energy and its interval, model-based and direct EPC with intervals and statuses, the reported EPC with its source and reason, joules per token, token mismatches, rows not used and replaced rows); `decomposition.csv` (6.5, with coefficient intervals); `level_residuals.csv` (t and bootstrap intervals, misfit); `primary.csv` (7.3, per level: both EPCs and sources, ln ratio and ratio, descriptive and decision intervals, status, cheaper, reason); `rivals.csv` and `crossover.csv` (7.4); `summary.json` (verdicts per line and boundary, misfit cells, roster status, targets, both confidences, bootstrap seed and size, Python version, exclusion sets, counts of every flag, any selection-size mismatch, and a method note). All of these are printed whatever the outcome; the paper's tables come from them.

### 8.2 Words for each outcome

| Outcome | What the paper says |
|---|---|
| primary, resolved at level L | "At level L, [cheaper] used fewer joules per correct answer than [other]: ratio r, 99% interval [lo, hi]." |
| primary, unresolved at level L | "At level L the measurements do not resolve which is cheaper: ratio r, 99% interval [lo, hi] includes 1." Never "they are equal". |
| primary, unresolved, incomplete at level L | "At level L the comparison is incomplete ([reason]); no order is stated." The counts reached are printed. |
| cheaper size changes with level | "The cheaper of the two changes with level: [config] at levels …, [config] at levels …" |
| no resolved change | "No change of the cheaper size between levels is resolved." If every resolved level has the same cheaper configuration, those levels are named. |
| secondary, any status | the cheapest among the eligible, each rival's ratio and 99% interval, beaten or tied, and the incomplete list with reasons |
| misfit cell | the cell is named, and its reported EPC is marked "direct estimator (this level's energy departs from the token prediction)" |
| optional configuration not measured | "not measured" in the roster; it appears in no comparison |
| configuration short at the end date | its counts beside its targets, and "short"; every comparison it is in is unresolved, incomplete |

The wall boundary is printed under the same words as a labelled line beside rails. The flagged-inclusive line is printed beside the primary line under the same words, labelled; where the two lines differ in a status, both are shown.

### 8.3 Caveats printed with the results

- Beside 8B thinking-off at level 1: "In simulation this 95% interval covered 91 to 95% of true values at every sample size tried (the 99% interval used for decisions, 97 to 99%), because of a long-tailed length distribution; read it as roughly a 93% interval."
- Beside every thinking-on cell whose bench contains an answer cut off at the cap: "With 44 holdout problems this interval may miss a rare very long problem; in simulation one such cell's 99% interval covered 89%. Descriptive only."
- With the primary decisions: "The 99% intervals have their nominal coverage only where each configuration's energy follows one line in its token counts across levels, or the misfit check catches the level that does not, and no rare energy excursion lies outside the token counts. In simulations built from the pilot, a level was falsely resolved in 0 to 1% of campaigns, and in 1.6% when the two sizes were made to tie at level 1; in constructed worlds that break those conditions, in up to 14% (one configuration's joules per token differing by 15 to 78% between levels) and 67% (a 101-fold excursion in 0.5% of runs). The verdict that the cheaper size changes with level was false in 1.5 to 2% of campaigns in that near tie, 1% in one constructed world and never in the others." Beside the level-1 row also: "In the simulation built from the pilot's own wall times this 99% interval covered about 98% of true values."
- With every energy number: energy is gross whole-request energy (idle power not subtracted), from one machine.
- With every accuracy number: MATH (2021) and PRM800K (2023) predate Qwen3 and are widely copied, so the models may have seen these problems in training; accuracy describes this subset of rational-answer problems and is not a capability claim (importer contamination note).
- Level is a stratum, not a cause (section 1).

## 9. Blinding, collection and end date

**Blinding.** Until the analysis is frozen and the independent twin program (section 10) agrees with the main program on the real tables, every energy is multiplied at harvest (the program that reads each finished session's raw records and writes the tables) by a hidden factor drawn once for the pack (uniform between 0.8 and 1.25) and by a hidden factor per configuration (uniform between 0.97 and 1.03), as the collection design sets out (`docs/design/block6_collection_draft.md` section 16, item 3). The per-configuration factors can shift a blinded ln ratio by up to ±0.06, so blinded verdicts cannot be read as results. The analysis runs on the blinded sessions as they arrive; unblinding divides the factors out once. Accuracy and token counts are not energies and are not blinded.

**Collection.** Bench attempts are generated without power capture and scored afterwards. Energy attempts run inside the collection design's sessions, each with its own idle baseline (a quiet stretch measured just before the run). Within a session, the three thinking-off configurations' attempts on a level are interleaved, so that a slow change of the machine falls on all three alike rather than on one; the collection plan fixes and records the exact order, and a departure is a recorded flag that excludes nothing. Attempts carrying an excluding flag are re-measured (5.2). The counts of section 4 are fixed; there is no stopping on precision. Collection ends when every measured configuration has complete cells at both boundaries, or on **2027-01-31**, whichever comes first. A configuration short at the end date is printed with its counts and called short.

## 10. The code that computes it

The registered computation is the code at commit `fc40786675afaee7607b04f65f02ec1652c4e4d8` (`fc4078667`) on branch `lane/2026-10-14-difficulty-pack`, run with CPython 3.13.1 (`/opt/homebrew/bin/python3.13`; the bootstrap uses `random.Random` seeded from text). Files and their SHA-256 at that commit:

| File | SHA-256 |
|---|---|
| `joulewise/packs/__init__.py` (empty) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `joulewise/packs/difficulty/__init__.py` (empty) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `joulewise/packs/difficulty/config.py` | `4f91153f3b89de969896ec633644570d9e65bb073fb30108fa4bded8989c7675` |
| `joulewise/packs/difficulty/manifest.py` | `2a4f2794641670d5153138ca84d2ea73948ccafd83f0dde0ed2e65cfc9c7b1fa` |
| `joulewise/packs/difficulty/score.py` | `276526405a61038e9313c9b0a028fa6f4066cb4a86ca7aa0422779a41ae2d18a` |
| `joulewise/packs/difficulty/estimators.py` | `14c657f2f57a99977d5fedea8f9ea2de5f2184b1833d426a33491d5f60fd77d5` |
| `joulewise/benchmark_import_math.py` (the importer the pack reuses) | `bdb165fd9052302a3ae5d4a22fe69b581105d15dfd9e5832c917dcb9eef1c391` |
| `scripts/difficulty_manifest.py` | `730970196ab467f6e73835c5e2a98d5f9871eb1318616d6411672a6c102734a7` |
| `scripts/difficulty_score.py` | `6028b69657878a4317911e7611656224bdaa56e7d8c33b1dd2aab66d850745f8` |
| `scripts/difficulty_estimate.py` | `b39da89f1da4a6f37091cea6b111f0c0c2db4d65b72be2c1c3f0d22e5c283ee2` |
| `scripts/difficulty_twin.py` | `4ec1b833bb37e51bc1341543b5cbcd108d12d20087621019d1ab94d6481cbd8e` |
| `docs/contracts/difficulty_tables.md` | `8426920b9c527b171146dfa676e9d7df52a8f21770006b41a58c1eb67b8d0c05` |
| configuration, appendix A | `274994de6494074e3c716a981c5638ebed874aea84a4b61aa3d7c22b8dd7d9dd` |

Steps: `scripts/difficulty_manifest.py --config <appendix A> --out <path outside the repository>` builds the manifest and the selections file (section 3); `scripts/difficulty_score.py --manifest --config --generations --out bench.csv` scores recorded generations; `scripts/difficulty_estimate.py --config --selections --bench --energy --out DIR` writes the tables of section 8. The configuration file is the only source of confidences, sizes, exclusions and bootstrap settings; the programs take no overrides. The code may be merged or rebased; the registered result is what these bytes compute.

**Twin.** `scripts/difficulty_twin.py` is a second program written from the spec without reading the main estimator, using only Python's standard library, with the same inputs and outputs and the same random draws. Before unblinding, both run on the real tables and must agree: identical row keys and text fields in all six tables, numbers within 10⁻⁶ relative or absolute (revision 2.3; before it, 10⁻⁹), and the same `summary.json` apart from the method note: identical keys, structure, text, whole numbers and verdicts, with its decimal numbers within the same 10⁻⁶ (they repeat table values, and two independent programs need not round the last binary digit alike: on a complete synthetic pack the refuter of this version found seven such differences, the largest 1.8 × 10⁻¹⁵). A disagreement is a fault fixed before release, never averaged.

State of the code at registration: the four pack test modules (56 tests, including every acceptance case quoted in section 6) pass at `fc4078667`; the executing review re-ran every refuter witness of version 1 against it and found each fixed, and found main and twin in exact agreement on a registered-size synthetic campaign with defects of every kind (the two programs together took 92.6 s on it, on a loaded machine). At the sizes of appendix A, a complete production-shaped synthetic pack (6,040 bench and 1,543 energy rows: every configuration including the optional one, both boundaries, token counts and correctness from the pilot's rows, energy from its wall times, with a re-measured failed run, a re-measured physical flag, a later duplicate and a loop flag) ran through both programs: all 100 cells complete, all six tables within the tolerances above, `summary.json` within the rule above (20 decimal leaves differ in the last digits, none beyond tolerance); 29 s for the main program and 34 s for the twin, on a loaded machine (at revision 2.1's sizes: 1,303 energy rows, 15 such leaves). The code is unchanged by revisions 2.1 and 2.2; only the configuration and the lists changed.

## 11. What would make this registration wrong, and how an erratum is taken

The registration is wrong, and an erratum is needed, if any of these is found:
1. A DIFFICULTY energy session began before this file's commit time. Its data are then exploratory and are printed apart.
2. The problems measured are not the registered lists (selections file hash, section 3), or a model ran at another revision.
3. The tables were computed by code whose bytes differ from section 10, or with a configuration other than appendix A.
4. The text here and the registered code disagree about what is computed. The registered code is the arithmetic of record; the text's reading is printed beside it.
5. The registered code is shown, by running it, to compute something other than the estimator it implements (a defect such as a sign error), or a rule here is shown to remove data for a reason that is neither physical nor a row the arithmetic cannot use.

Not errors: an unresolved or incomplete result; real spreads or tails unlike the simulation's; a misfit at some level. These are printed as they come out.

**How an erratum is taken.** One refuter (a model other than the erratum's author) checks the claimed error by running the registered code on the case in question. The orchestrator then records a decision: dated, with its reason, the refuter's finding, and exactly what changes. Before the first DIFFICULTY energy session, an erratum may change anything and is issued as a new version of this file. After it, the result under this registration as written is always printed, and any changed result is printed beside it, labelled with the erratum's date; no registered arithmetic or exclusion is changed after unblinded energies have been seen, except as such a labelled line.

## 12. Decisions this registration makes beyond the spec

1. Thinking-off energy subset 70, 30, 30, 30 and 30 by level (spec: 20, 20, 40, 40, 40) and thinking-off bench 200, 200, 400, 400 and 600 (spec: 200 at every level), from the power simulations of section 4.1. The second set was run after the first refuter showed the first set rested on an assumed 4B/1.7B cost factor. The level-1 energy of 70 (revision 2.2) followed the second refuter's near-tie world.
2. Thinking-on sizes kept at 64 and 20 (not simulated); the review's thinking-on coverage finding is handled by the printed caveat (section 8.3) rather than a larger thinking-on bench, because thinking-on configurations are never in the primary question.
3. Re-measurement replaces attempts carrying any excluding flag, physical ones included (section 5.2; spec section 14 item 2).
4. Physical flags are written on energy rows only (section 5.1; review note N1).
5. The 4B and 8B revisions, left as "panel pin" in the spec, are the pilot's and the local copies' (section 2).
6. Rails is the headline boundary and the primary line carries the claims; the Bonferroni family is the five levels of the primary question there (section 7.1).
7. The contention level is the collection design's, as in force at the first DIFFICULTY energy session (section 5.1).
8. Thinking-off configurations are interleaved within sessions (section 9).
9. Collection ends on 2027-01-31 at the latest, matching the plan to run DIFFICULTY in December and January (`docs/design/block6_collection_draft.md` section 15, Timeline, which also says later packs set their own end dates). Version 1's 2026-11-07 is the last-data date of the same section's earlier six-week calendar, which the Timeline paragraph replaced for DIFFICULTY.
10. Independent bootstrap streams per configuration are kept; paired streams were simulated and not adopted (sections 4.1 and 7.2).

## Appendix A. The registered configuration

Byte for byte (UTF-8, two-space indent, final newline; SHA-256 `274994de6494074e3c716a981c5638ebed874aea84a4b61aa3d7c22b8dd7d9dd`; a copy is `/Users/edr/night-archive/difficulty-pack/v2.2-registration/pack_config_difficulty_v2.2.json`). It differs from the code's test fixture `tests/fixtures/difficulty/pack_config.json` only in the version string, `n_per_level` (600 instead of 200), the thinking-off bench sizes at levels 3 to 5 (400, 400, 600 instead of 200), the thinking-off energy sizes (70, 30, 30, 30, 30 instead of 20, 20, 40, 40, 40) and the 4B and 8B revisions.

```json
{
  "schema_version": "difficulty_config.v2",
  "version": "difficulty-v2.2",
  "seed": "joulewise.packs.difficulty.v2",
  "n_per_level": 600,
  "sizes": {
    "off": {
      "bench": {
        "1": 200,
        "2": 200,
        "3": 400,
        "4": 400,
        "5": 600
      },
      "energy": {
        "1": 70,
        "2": 30,
        "3": 30,
        "4": 30,
        "5": 30
      }
    },
    "on": {
      "bench": {
        "1": 64,
        "2": 64,
        "3": 64,
        "4": 64,
        "5": 64
      },
      "energy": {
        "1": 20,
        "2": 20,
        "3": 20,
        "4": 20,
        "5": 20
      }
    }
  },
  "exclude_importer_sets": true,
  "exclude_item_id_files": [
    "/Users/edr/night-archive/pilots/difficulty/pilot_item_ids.txt"
  ],
  "boundaries": [
    "rails",
    "wall"
  ],
  "configurations": [
    {
      "model": "qwen3-1.7b",
      "repo": "mlx-community/Qwen3-1.7B-4bit",
      "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
      "mode": "off",
      "output_cap": 4096,
      "status": "measured"
    },
    {
      "model": "qwen3-4b",
      "repo": "mlx-community/Qwen3-4B-4bit",
      "revision": "4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25",
      "mode": "off",
      "output_cap": 4096,
      "status": "measured"
    },
    {
      "model": "qwen3-8b",
      "repo": "mlx-community/Qwen3-8B-4bit",
      "revision": "545dc4251c05440727734bcd94334791f6ab0192",
      "mode": "off",
      "output_cap": 4096,
      "status": "measured"
    },
    {
      "model": "qwen3-4b",
      "repo": "mlx-community/Qwen3-4B-4bit",
      "revision": "4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25",
      "mode": "on",
      "output_cap": 16384,
      "status": "measured"
    },
    {
      "model": "qwen3-8b",
      "repo": "mlx-community/Qwen3-8B-4bit",
      "revision": "545dc4251c05440727734bcd94334791f6ab0192",
      "mode": "on",
      "output_cap": 16384,
      "status": "optional"
    }
  ],
  "primary_comparison": {
    "a": "qwen3-1.7b/off",
    "b": "qwen3-4b/off"
  },
  "descriptive_confidence": 0.95,
  "decision_confidence": 0.99,
  "bootstrap": {
    "replicates": 4000,
    "seed": "joulewise.packs.difficulty.v2.bootstrap"
  },
  "exclude_flags": [
    "runtime_failed"
  ],
  "physical_exclude_flags": [
    "agent_overlap",
    "sleep",
    "contention_above_level",
    "idle_wait_cap"
  ],
  "loop_detector": {
    "tail_fraction": 0.25,
    "min_span": 20,
    "min_repeats": 3
  }
}
```
