# Mythos 5.2 seat: is there any way to keep S? (ALIGN v4, after Ed chose option (c))

You are an independent research advisor for JouleWise, a blinded study that measures LLM inference energy on an Apple
M3 Max laptop (the "MBP") with a wall-power meter and macOS power counters. Ed, the PI, has just chosen option (c)
of the research lead's (Fable 5.2) question about the 27B model, and he asks you specifically:

> "see if mythos can find any way to keep S, even if some desk work is needed, desk work is cheap"

## The situation (read the sources; do not trust this summary)
- The registered v4 study has two tests on the 27B model: **K** (the tripwire: an energy alarm level set from
  ordinary 27B runs in 8 calibration sessions, then count ordinary 27B runs in 3 test sessions that trip it; the
  only confirmatory claim) and **S** (do 27B runs instructed to sabotage use more energy than ordinary ones).
- The 27B cannot run as registered: (1) heat: in normal power mode macOS leaves its nominal thermal state after
  about 2 min of continuous work; the registered rules exclude runs that leave nominal; long 27B turns run 2-7 min;
  (2) time: the ~996 s per-run cap leaves ~1 s for cooling waits after prefill + decode at ~12 tok/s.
- Ed chose **(c)**: keep K in normal power mode; 27B runs are described as "cooled to a set point before each turn",
  runs that heat up are kept in; a rewritten budget check is needed. The research lead's worry about S: "if the
  sabotage instruction changes how long the model works, it changes how hot the run gets, and S might have to be
  dropped or reported as description."

## Your task
Find every credible way to keep **S as a confirmatory (or at least pre-specified, error-controlled) test** under
(c), or under a minimal variant of (c), using desk work (analysis design, re-specification, covariates,
stratification, matching, normalisation, measurement-side changes that need no new hardware) — desk work is cheap.
For each idea:
1. State it precisely (estimand, statistic, what is conditioned on or adjusted for, decision rule).
2. Explain why it survives the heat confound (thermal state / throttling varying with sabotage-induced work length)
   and the time-budget problem, or what residual threat remains.
3. Say what it needs: desk work only? a registration amendment (which must be decided BLIND, before any v4 outcome
   is read)? new rehearsal nights? code changes (which files)?
4. Say what it costs in power/sensitivity, and whether it stays honest as a confirmatory claim (pre-registration
   fidelity: the change must be decided without seeing v4 outcomes; say how to show that).
5. Rate it: strong / plausible / weak, with the single biggest risk.
Then rank them and give your recommendation to the research lead, plus the cheapest desk experiments (from data
already allowed to be read — journals, clocks, temperatures, classifications) that would tell us fast whether the
top idea works. Consider at least: energy per token or per unit work instead of per run; conditioning on decode
length / thermal trajectory; matched pairs by token count; per-turn thermal-state covariates; restricting S to a
thermally safe sub-window (e.g. the first N tokens / prefill-only / a fixed token budget); capping or truncating
generation symmetrically across arms; equivalence of work and testing energy residuals; within-session
interleaving; whether the 30B (no-claim) runs could carry S; and anything better you find.

## BLINDING — absolute
ALIGN v4 outcomes are sealed. Do NOT open or read: any `r1_slots.json`, any transcript, any energy, power, meter
(KM003C) or powermetrics sample file, any `smoke_part_*.json` slot block, anything under `~/night-*` on any host.
Reading registration text, rulings, code, and the desk copy below (journals with turn stamps, clock mappings, thermal
level / temperature journals, classification files, failure records) is allowed — the research lead already allows
the desk to read exactly these (RL-145 §4). If you are unsure whether something is outcome-bearing, don't read it.

## Read-only
Edit nothing, commit nothing, comment nothing anywhere, run no measurement or analysis program, use no network
except what git/gh needs to read. Write only your report.

## Material
- Repo (read-only worktree at the RL-145 build, `f006b7aa6`): `/Volumes/JW-EXT/jw-wt/mythos-keep-s`. The v4
  registration and its docs: `docs/align/pilot_protocol_v4.md`, `docs/align/v4/` (DEVIATIONS.md, claim contracts,
  PREQUAL.md, …), `configs/campaigns/align_v4/`, the kit `scripts/align_v4_kit.py` and R1 kit scripts. Grep for
  "S", "sabotage", "tripwire", "K".
- Rulings: `/Volumes/JW-EXT/scratch/mythos-keep-s/mbp/`: `fable-rl145-r1fu-1113.md` (RL-145), `fable-rl145-addendum.md`,
  `fable-rl145-close.md`, `fable-rl145-close-erratum.md` (the question Ed answered, §3), `D-DEPENDENCIES.md` (every
  place the first session uses a 27B run), `round-rl145/` (the design-round brief and the Opus and Sol memos).
  Full ruling log: `git -C /Volumes/JW-EXT/jw-wt/mythos-keep-s show origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
- Desk copy (allowed data): `/Volumes/JW-EXT/scratch/mythos-keep-s/mbp/r1fu-1113-desk/` (DESK-P1-P5.md, P6-P8.md,
  tables.md, JOURNAL-TABLE.md, scripts/, in/, in2/).
- Ed's decision on record: RUN_STATE.md item 314 on origin/main.

## Output
Write `/Volumes/JW-EXT/scratch/mythos-keep-s/REPORT.md`: a one-paragraph answer first (can S be kept, and how), then
the ranked ideas with the five points each, the recommended next desk steps, what needs a blind amendment and what
needs the research lead's ruling, and a list of what you could not verify. End with a line confirming you opened no
blinded content. If the Write is denied, put the whole report in your final message.
