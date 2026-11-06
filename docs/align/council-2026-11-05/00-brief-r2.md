# Window design council, ROUND 2: cross-critique

All three round-1 designs are in `.council-out/` in the council workspace: r1-opus.md, r1-fable.md and r1-sol.md. Read all three in full. The original brief is /private/tmp/jwcouncil/align9/brief.md (for Sol: it is appended below).

Write `.council-out/r2-<seat>.md` with:
1. **Errors in the other two designs**: factual (model sizes, mlx-lm support, memory, record citations), arithmetic (budgets, window maxima, energy estimates), or scientific (confounds, calibration validity, held-out honesty). Cite the line or section. Verify claims against the repo, and for Claude seats the web, rather than trusting any design. Sol: list web facts that need checking.
2. **Best ideas you adopt from the others**, for example a deciding experiment, gate designs, parser and cache builds, or acceptance criteria.
3. **The contested decisions.** Give your position and reason on each:
   - (a) the model set and quantizations: Next 4-bit Thinking vs 8-bit Instruct; whether the 122B MoE is in or out; whether Qwen3.8-Flash-Next is truly infeasible;
   - (b) the window plan: qualification window vs a deciding experiment first, member counts, number of windows, and the per-model calibration target;
   - (c) the thermal gate's variable and form: start-temperature gate, per-turn gate to the episode's own start temperature, or chunked decode with holds, plus the token-budget vs wall-guard choice;
   - (d) the "under control" acceptance criteria: merge them into one set with numbers;
   - (e) the must-build list and its order;
   - (f) what Ed must do physically, and the questions only Ed can answer (for example which "Qwen 3.8" he meant).
4. **Your revised recommended design in one page.**
Be concise and quantitative. Do not edit other seats' files.
