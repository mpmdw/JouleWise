# Workload consult — shared blind brief (2026-08-28)

Three seats receive this identical brief with no contact between them: Sol
(gpt-5.6-sol, xhigh, read-only), Opus 5, and a fresh Fable 5. You read the
repository yourself; nothing in this brief is a finding, only a pointer.
You are read-only: do not edit, commit, or write files in the repo. Return
your answer as your final message (Markdown, ≤ ~250 lines). You are one seat
of three; do not attempt to synthesize for the others. No ruling is asked of
you; the magistrate rules later.

## Ed's words, verbatim (the forcing problem)

> "does that workload even make sense? … that feels like a very silly and
> arbitrary first workload profile to run i think we can do better like
> standard same length queries or the same benchmark question or something."

## Context (read these in the repo)

- Current production design: a fixed 512-token greedy decode on a pinned
  prompt plus a 256-token prefill arm —
  `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`.
- Design rationale: `docs/decision_log.md` D-117 and D-139 (also D-153,
  D-157, D-164).
- `joulewise/determinism_gate.py` — decode must be bit-exact across repeats.
- Paired-block design n=10 with per-cell detection floors ~1 J —
  `joulewise/detection_floor.py`.
- Resolvability rule: ≥3 overlapping sampling records per arm.
- Ed's actual research questions: `docs/research_question_registry.md` and
  `docs/research_question_bank.md`.
- The paper draft: `docs/paper/draft-v1.md` §3–§5.
- D-164 (Ed, today): the campaign moves to a newer model pair chosen from the
  model-panel survey; the design is being regenerated anyway as `_v5`, so the
  WORKLOAD IS OPEN for one more day. Tokenizer-identical same-family pairs
  preferred; thinking-mode models excluded unless pinned off.

## Questions (answer all four, numbered)

1. What workload makes the paper's headline figure meaningful to a reader
   and defensible to a metrologist? Options, at least:
   (a) keep fixed-length synthetic (current);
   (b) a fixed, pinned set of real benchmark questions (e.g. GSM8K / MMLU /
       HumanEval / MT-Bench items) with max_new_tokens capped, energy
       reported per query AND per generated token;
   (c) the same prompt set with natural stopping (length confound — say how
       to handle it);
   (d) a small mixed profile (short chat turn / long-form answer / code);
   (e) a standard-length "same question to both models" design.
   For EACH option state what it does to: determinism (bit-exact decode
   across repeats), block pairing, the floor arithmetic (energy per block
   must stay well above ~1 J), resolvability of the prefill arm (≥3
   overlapping sampling records), night duration, and the exact sentence
   the paper can honestly print.
2. The confound: energy scales with generated tokens; if models stop at
   different lengths, what is the right pre-registered quantity (per-token,
   per-query at a fixed cap, both with the cap declared)?
3. A concrete recommendation: the workload profile to freeze into `_v5`,
   with pinned data source, token caps, number of distinct prompts per
   block, and the night arithmetic (blocks × arms × repeats × seconds) —
   plus the strongest counter-argument to your own recommendation.
4. Which registered RQs (by ID from the registry/bank) each option answers.

Use real numbers from the repo (floor values, per-token timings if present,
n, block counts). Label every assumption you could not verify from the tree.

## Addendum (coordinator, sent to all three seats mid-consult as a follow-up question)

Ed, verbatim, on option (b): "this sounds promising. with an added benefit
of how close the problems get to solving it in their fixed budget. lot of
interesting meat there. investigate that type of path for workload
profiles."

So option (b) is the LEADING path and each seat must develop it: a pinned
benchmark question set, same questions to both models, fixed
max_new_tokens budget, and BOTH outcomes pre-registered — energy (per
query, per generated token) AND task outcome under the budget (correct /
incorrect / truncated-before-answer, scored by a pinned deterministic
checker, e.g. GSM8K exact-match on the final number). Answer:

(i) what pre-registered quantity is defensible for "energy per correct
    answer" / "joules per solved problem", and how it interacts with the
    paired-block design and the floor gate (the claim gate must stay on
    energy resolvability; accuracy is a labelled co-outcome, not a gate);
(ii) which benchmark(s) give deterministic scoring, license-clean pinned
    data, answer lengths that fit a cap of a few hundred tokens, and a
    plausible accuracy spread between a small and a large model of the
    same family;
(iii) how many distinct questions per block, and how repeats stay
    bit-exact when the question set is fixed;
(iv) the honest paper sentence and which RQ in the registry/bank it
    answers (Ed's bank likely already has an efficiency-vs-quality
    question — find it);
(v) the trap list (contamination, thinking-mode length blowups,
    answer-format parsing, cap-truncation bias against the large model).

Keep the other options as the comparison set.

Fact: the leading D-164 pair is Qwen3-1.7B-4bit / Qwen3-8B-4bit (survey:
`docs/process_traces/2026-08-28-model-panel/00-SURVEY.md`, PR #233).
Today's harness applies NO chat template and forces 512 tokens with
`suppress_eos=True` (`joulewise/adapters/mlx_runtime.py:294-303`), so
thinking mode is moot for the synthetic design — but a benchmark-question
workload needs a chat template and a pinned thinking setting (Qwen3:
`enable_thinking=False` or the `/no_think` directive) and natural EOS
under a cap; address how that changes determinism, length variance, and
the harness code path (suppress_eos off, template pinned by hash).
