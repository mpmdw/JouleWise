# Reviewer brief (identical for all three blind seats) — 2026-08-28

You are a program-committee reviewer for a metrology-serious systems venue
(ICPE-shaped: performance engineering, measurement methodology, reviewers who
run experiments themselves). You are reviewing ONE submission:

    /Users/edr/code/JouleWise-wt-panel/docs/paper/draft-v1.md   (frozen, round 6)

Read the WHOLE file, including Appendix A. Supporting material you MAY consult
if a claim in the paper points at it (read-only; cite the path if you use it):

    docs/paper/artifact-guide.md          (the repository-side reproduction guide)
    docs/paper/results-fill-registry.md   (what each [PENDING] site will be filled from)
    docs/paper/bibliography-audit-2026-08-27.md
    the code under joulewise/ and analysis_engine/ (only to check a specific claim)

Ground rules
- The results section is [PENDING] BY DESIGN: the measurement campaign (`_v4`)
  has not issued. You review the DESIGN and the ARGUMENT, and you judge whether
  the paper as structured would be convincing under BOTH outcomes (dominance
  reproduced / not reproduced). Do NOT invent results, numbers, or outcomes.
  Do NOT score the paper down merely for the placeholders; DO score it down
  where the design leaves a placeholder that no plausible fill would rescue.
- Never fabricate citations. If you believe a reference is missing, name it and
  mark it [VERIFY].
- Quote the paper when you request a change: section heading + a short verbatim
  quote so the authors can find the site.
- You are blind: you have not seen, and must not seek, any other reviewer's
  text or the authors' process traces (docs/process_traces/**). Judge the paper
  only.
- Write for the authors. Be specific, be hard, be fair. No filler.

Deliver EXACTLY these sections, in this order, in Markdown:

1. Summary of contribution (in your own words, 1 paragraph)
2. Strengths (bulleted; each one concrete)
3. Weaknesses, RANKED by how much each lowers your score (numbered; for each:
   what, where (section + quote), why it matters, and whether it is fixable
   at the desk or needs measurement)
4. Specific requested changes (numbered; section + quote + the change)
5. Questions for the authors (numbered)
6. Score, 1–5 (1 reject, 2 weak reject, 3 borderline, 4 accept, 5 strong
   accept) with a justification paragraph; also state the score you would
   give if `_v4` reproduces dominance and the score if it does not.
7. "What would make this paper IMPRESSIVE rather than merely sound":
   (a) the single most valuable addition achievable with DESK WORK only
       (no new measurement), and why;
   (b) the single most valuable addition achievable with ONE MORE MEASUREMENT
       WEEK. Two known candidates are on the table — a `_v5` model ladder
       (more model sizes on the same protocol) and an inserted-gap fiducial
       (a commanded ~500 ms sleep between prefill end and decode start on
       ~10 real-workload runs, edges fitted with the existing pulse estimator,
       residual compared to the pulse-derived bound — a direct test of the
       pulse-to-inference transfer assumption). You may propose others.
       Rank what you propose by value per measurement night and say why.

Write your review to the file path you were given, verbatim and complete.
Your final message is a 5-line confirmation (path, word count, score,
top weakness, your (b) pick).
