# BYTES deviation log

**What this is.** This log holds the dated departures from the BYTES registration
(`docs/registrations/bytes_pack_v1.md`). Each row is entered when the departure is found, with a statement of what
its author was blind to, and is never edited afterwards. A later row may qualify an earlier one. Before this file,
the BYTES lineage kept no deviation log: dated changes stood as their own files (for example
`bytes_end_date_amendment_2026-10-27.md`) or as dated registration sections (§21). Block 5's
`docs/analysis/b5/DEVIATION-LOG.md` is a separate log for Block 5.

**Authority.** Research lead ruling RL-44 (2026-11-11), `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`
on `audit/2026-11-10-fable`. The row text below is RL-44's, verbatim. The two sentences from "Separately" to "is not
known." were added the same day, verbatim from RL-45, before the row was merged.

| Id | Entered | Text |
|---|---|---|
| BY-BLIND-1 | 2026-11-11 | BY-BLIND-1 (entered 2026-11-11, before the stage-1 commitment; blind to every BYTES energy). §11 item 2 kept clock times out of analysis exports so that a held-out module's duration could not be read before the commitment. It did not cover reads of raw session records for hazard diagnosis. Two such reads were made on the pass-1 session of one held-out model, Llama-3.3-70B (`r1-bytes-s5-p1`): on 2026-10-27, thermal timing relative to request ends; on 2026-10-28, each science member's decode duration, which was committed to the project record. No energy or power field was read. Separately, the public operational record branches `night-results/r{1,2}-bytes-*` carry one timestamp per session stage, from which the wall time of a held-out stage can be derived coarsely, for every session; they carry no per-member or per-request clock. Whether anyone derived it is not known. §21 item 3 was motivated by the first read. The committed predictions cannot depend on either read: they are computed from the fit set by the estimator pinned on 2026-10-24, from the manifest frozen on 2026-10-22. Reporting: Llama-3.3-70B stays in the registered families and is marked in every table; the H1 summary is also stated over the other six held-out models, with the registered family sizes unchanged. Record: `docs/process_traces/2026-11-11-bytes-blindcheck/BLINDCHECK.md`. |

RL-44 adds a note on the reporting line. It is a reading of the per-model words that the registered analysis
already prints, so it adds no arithmetic and needs no code.
