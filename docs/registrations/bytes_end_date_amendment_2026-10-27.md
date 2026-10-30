# BYTES end-date amendment (Ed, 2026-10-27): no t0 after 2026-11-05T00:00:00-08:00

**Authority.** Ed, Claude Code session 015ASG1T, 2026-10-27, answering "yes" to the pipeline audit's decision 5
(`docs/process_traces/2026-10-27-pipeline-audit/SYNTHESIS.md` §7 item 5). The BYTES registration
(`docs/registrations/bytes_pack_v1.md`) states no procedure for changes after its cold gate, so this is the owner's
change, recorded here and in directive issue #589.

**Blind.** Made before any BYTES energy has been unblinded. It changes when collection stops, not what is computed,
excluded or printed. The reason is capacity only: about 8 counting sessions remain (pass-1 retries and pass 2), and
pass 1 lost 2 of 6 attempts. If pass 2 finishes before 2026-11-02, the amendment has no effect.

**Change.** In every BYTES pack registration (`configs/b6/packs/bytes-s{1..6}-p{1,2}/registration.json`),
`stopping.end_t0_before` changes from `2026-11-02T00:00:00-08:00` to `2026-11-05T00:00:00-08:00`. The offset is
deliberately -08:00 (PST). Wording elsewhere that says "2026-11-02 00:00 PDT" means this registered instant and is
superseded by the new one.

**How it is applied.** At a SESSION_DESK, by the orchestrator, with the pack generator (not by hand), regenerating
sidecars and plan trees. It lands as one measurement-checkout commit. Like any pin change it changes the session
fingerprint, so the next session of each pack smokes. CI and `--check` must pass. Unchanged: the replication packs
ALPHA, BETA and GAMMA (their end is 2026-11-01 and they are closed), and the order of sessions, including the
registered retry rule (§5: a lost attempt retries in the next BYTES slot).
