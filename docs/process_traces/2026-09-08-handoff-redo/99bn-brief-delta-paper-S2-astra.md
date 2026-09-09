# Delta re-audit — paper S2 reported-energy supplier (gpt-6-astra, HIGH, genre review, READ-ONLY; EXECUTION lens)
Branch feat/2026-09-08-paper-S2, head 720b166c; the landing is `git diff e241e0b7 720b166c`. It implements the three-seat
ruling at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99be-coldgate-packet-paper-s2-semantics/13-magistrate-synthesis.md
(read it and the seat rulings 10/11/12 beside it). Audit with file:line and an executed check per claim:
1. ARITHMETIC: recompute, by hand or a throwaway script, the kernel's outputs on the synthetic control in
   tests/test_paper_reported_energy.py: the 50-member mean; V = 0.2²·s_r²/10 + 0.8²·s_b²/10 with ν = 9 (is s_r the
   sample SD over the 10 repeats and s_b over the 10 block MEANS, each with n−1?); h = t(0.975,9)·√V; B = Σ_kind
   mean over members of the kind bound; endpoints m ∓ (h + B); per-token ΣE/ΣT. State any discrepancy to the digit.
   Confirm the pooled-vs-stratified regression actually uses s_r ≠ s_b.
2. REGISTRATION: are the registrations in both generators byte-equivalent in substance, bound to each cell_id
   (decode, prefill-p42, prefill-p512), with refuse_reported_mean on any missing/invalid member, and pinned by the
   plan test such that removing a registration fails? Does the plan test still pass for the frozen v5 packs'
   OTHER content (no accidental change to floor members)?
3. CUSTODY: does every evidence input to the projection enter through open_paper_input roles; is the new validator
   in the transitive source census; does the renderer read ONLY the projection (never the mint report); is the
   production reported-energy gate ABSENT from _ISSUANCE_GATES; are there NO production digests in supply_map.json?
4. MUTATIONS: for each row in the seat's counterfactual table (report at
   /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bm-seat-paper-S2-relaunch-astra-report.md),
   read the assertion and state whether the counterfactual would actually change the asserted value/refusal; run
   at least four of them in memory.
5. F2 residue: list exactly which production provenance joins and which ordering proof (registration digest predates
   the spec's first existence) remain, and whether anything in this landing could be mistaken for them.
6. Any NEW defect. Verdict keys per genre review; severity per finding; ≤ 900 words; no edits; header < 8192 bytes.
