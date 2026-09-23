**Where I disagree with the framing.** Windows are still the bottleneck. The limit is how many windows yield usable data, not how many can run.
- **No claim-bearing data yet.** On day 7, every executed night (`NIGHT_HANDBACK.md` §Executed) is instrument qualification. The 09-16 plan had Paper B data-complete on day 3.
- **No model-cell arm path.** `joulewise/evidence_night.py:21,307` accepts only `quiet_predicate_evidence`.
- **Refusals still cost hours.** A212/A234 are still READY. A zero-capture refusal still holds the machine about 3 h (`scripts/magistrate_watchdog.py:775–790`).
- **Gates and windows share one Mac.** Agents must be off during windows, so 4.5 windows/day leaves about 8–10 h for gates (est.).

**A. Gate throughput (ranked)**
1. **Remote desk sessions against origin.** Gates can then run during windows. Gain: about +1 gate/day (est.). Failure mode: seats that need bench evidence still need the Mac.
2. **Restore the council tiers** (`~/.claude/skills/council/SKILL.md:14–28`). "Fable on every merge" flattened them. A mechanical path list (reducers, admission predicates, plan writers, `analysis_plans.md`, `benchmark_import.py`) forces the full shape. Gain: +1–2 gates/day (est.). It is a process rule, so it needs a cold gate and Ed. Failure mode: a mislabelled path.
3. **Fewer fix rounds.** QPE01 took three. Briefs name the counterfactual input and the call site. Saves about 0.5 day per gate (est.).
4. **One EPCA registration packet** for the whole campaign. Saves about 3–4 gates (est.). Failure mode: one error voids more.
5. **Template re-arms.** Notice plus veto only, guarded by a template hash.

**B. Churn**
- **Refusals first.** Land A234 and A212 (`TASK_QUEUE.md:846,861`), then A271. A refusal then costs about 20 min instead of about 3 h (est.).
- **Headline critical path, built now in parallel:**
  - a scored-campaign kind in `evidence_night.py`;
  - a MATH importer cloned from the GSM8K one in `benchmark_import.py`;
  - a D-166/AP-5 amendment: `benchmark_import.py:88` says difficulty "licenses no difficulty … claim".
- **Size envelopes by decode tokens.** 64 8B thinking-off items take about 700 s (est.), which is more than 480 s. The thinking-on arm is about 8 h of decode (est.). The pilot sets items per envelope.

**C. Writing from day one**
- **Written before data:** Paper B methods and limitations, including the daemon-contamination episodes. Then the headline paper's intro, related work, the pre-registered plan, and both the crossover and the null paragraphs.
- **Who writes what:** Opus drafts. Sol writes figure code on `paper_rendering.py` against watermarked pilot data. Fable does the final pass and the first-use test.
- **Advisor in week 2:** send the methods and one pilot figure. This buys back about 5–8 days (est.).

**D. Result risk**
- **Crossover prior (est.):** thinking-off never crosses. The 8B costs about 3–4× per token, while its L5 accuracy advantage is at most about 2×. Thinking-on, where 1.7B traces hit the cap, is likelier.
- **Spend on items, not repeats.** Greedy repeats replicate energy only. Pair items across the two models.
- **Sizing the item count:** at n = 64 with accuracies 0.3 vs 0.6, the 95% interval excludes 1 only if R is at most about 0.65 (est.). 128 items per level narrows the interval about √2×.
- **What may adapt:** the pilot may set n and the cap. It may never choose which levels are reported (D-062).
- **Second ladder:** `affine_mod_ladder_v1` (`workloads.py:25`) sets difficulty in the generator and is contamination-free.
- **A quotable null:** per level, the break-even accuracy ratio, plus the decomposition J/token × tokens/attempt ÷ accuracy.

**E. Don't**
1. **Don't run agents on the Mac during windows, and don't thin claim-bearing gates.** The census already missed an interior of about 305 J vs about 152 J.
2. **Don't claim "intelligence per joule" or "difficulty causes energy".** AP-5 forbids both (`analysis_plans.md:258–276`). Don't present MATH accuracy as capability, since contamination can't be mitigated (`benchmark_import.py:84`).
