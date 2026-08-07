TASK — labelled NON-CLAIM desk feasibility check: prefill contrast vs the effective bar.

Question: from HISTORICAL diagnostics only, is a 1.5B-vs-7B PREFILL energy CONTRAST
feasible against the project's effective claim bar (D-078 cl.11 doctrine: instrument
attribution limit ~1 J; effective bar = floor + claim-side margin ≈ 5 J — VERIFY the
exact bar wording/numbers in docs/decision_log.md D-078 before using them; if the
decision log contradicts this prompt, the decision log wins — flag the conflict).

CONTEXT you cannot discover: Ed has directed the MVP claim scope be "at least
decode/prefill". The proposed shape: a prefill CONTRAST between Qwen2.5 1.5B and 7B
only rides a fresh measurement window if this desk check says the prefill delta
clears the bar; otherwise prefill floors are claimed, the contrast stays decode-only,
and infeasibility becomes a limitations paragraph. Your output decides that fork's
desk recommendation. This is a FEASIBILITY TRIAGE over diagnostics — several
historical corpora are VOIDED for claim use by a time-anchor defect (D-078); using
them as rough-magnitude diagnostics for triage is exactly the sanctioned labelled
non-claim use. Label every number you emit NON-CLAIM / DIAGNOSTIC.

SOURCES (repo: /Users/edr/code/JouleWise, read-only):
- Historical window roots at repo top level: runs_window_a9_20260724 and
  runs_window_a10_20260725 (1.5B floors, the clean 2026-07-25 pair), runs_window_7bfloor_20260729
  (7B floor), runs_window_contrast_20260730 (decode contrast), plus *_bound siblings;
  older: runs_window_a..a8, runs_window_b/c/d (window B prefill ABBA `04_phase_prefill_abba`
  FAILED its verdict — diagnostic magnitude only), runs_window_metrologyA/B.
- Per-member summary_metrics.json files carry phase energy fields (frozen decode metric
  is `phase_energy_j.decode`; find the prefill analogue and confirm its exact key).
- runs/p2_015_floors_window_a/ contains older prefill ABBA members (p2015-*-ph-prefill-*).
- CLAIMS_STATUS.md, docs/decision_log.md (D-078, D-102, D-110, D-113) for what is
  voided/retired and what the bar is.

DELIVERABLES (final message = the report; also note: emit the report as your FINAL MESSAGE):
1. Per model (1.5B, 7B): prefill phase energy per member — mean, spread, n, WHICH root
   and files, and whether that corpus is voided/failed/clean.
2. Best-evidence estimate of the 1.5B-vs-7B prefill DELTA (with the prompt-length/token
   count each corpus used — prefill energy scales with input length; state the workload
   shapes and whether they are comparable across the two models).
3. Compare delta vs the verified effective bar. Account for how the bar applies to a
   CONTRAST (two floors' uncertainties compose).
4. VERDICT: FEASIBLE / MARGINAL / INFEASIBLE for a prefill ABBA contrast arm, with the
   sensitivity: what input length (if any) would make it clear the bar, if length is the
   lever.
5. If feasible/marginal: rough shape of the ABBA arm (members, minutes) using the proven
   10-absolute/40-null design as the reference point.
6. Caveats + "what the parent should double-check" + exact commands you ran.

CONSTRAINTS: READ-ONLY — no writes anywhere. Do not touch RUN_STATE.md, TASK_QUEUE.md,
decision/council logs. If reports, tests, and decision-log entries conflict, named
decisions win; flag any conflict in the final message. If the requested metric key or
corpus does not exist as described, do not force it — report what actually exists.
