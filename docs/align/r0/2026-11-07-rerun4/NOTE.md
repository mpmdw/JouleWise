# ALIGN v4 R0 fourth re-run, 2026-11-06 PST (record dated 11-07 UTC): load, generated and memory pass; refused at the start of `smc` by the machine census (a Spotlight worker's start-up burst)

Magistrate activation 08e39e3b (Opus 5.5, headless), writing up the run that activation
32189215 launched under RUN_STATE items 181, 185 and 188.

## Run

- Record `/Users/edr/night-align/r0-v4-20261107T0149Z`, launch id `b5f2efeba5344fb3bec538edafaae202`
  (runner 01:50:10-02:05:15 UTC = 17:50:10-18:05:15 PST, 905.1 s wall). Measurement checkout
  `165e12872` (#687), clean.
- `report.json` sha256 `ea09437b25d1181db0496a3a991054a9c291657e21d54f7ce8848a0ec121b061`;
  `report.md` sha256 `fc4ab2eb00c7bd0838b4e5f0ebddfa5325bf7a0e8959562cd5361340c35506e6`.
- Status `refused`, `complete_r0` false. Checks: host pass; disk diagnostic (free
  84,255,961,088 bytes after weights); host-identity pass (Mac15,9, 137,438,953,472 bytes);
  model-load pass; **load pass**; template diagnostic; **generated pass**; checkpoint
  not_required; **memory pass**; **smc refused** at its opening census. ladder and long-decode did
  not run, so there is no SMC journal, SMC key classification, effort rung or B7 verdict.
- **load (reference mode):** NLL 11.0368 nats/token on the 2,048 pinned SHADE targets against the
  HF fp32 reference 11.0642 (delta -0.027, limit +/-0.10); no non-finite values; exact-reproduction
  tier `not_pinned`. Generation: greedy, one `analyze_spam_patterns` call with
  `{"min_occurrences":2}`, 109 tokens, no retry. Same numbers as re-runs 2 and 3.
- **generated:** the 16-call prompt of #687; passed with 0 off-spec echo turns (49.8 s).
- **memory:** prompt 34,816 + decode 6,144 tokens = the 40,960 context cap; peak 37,025,381,468
  bytes against the 45,000,000,000 council bar; swap unchanged (9,237,954 bytes before and after);
  732.5 s.
- **The refusal:** `machine occupied or census indeterminate`. No agent, no night agent, no
  custody refusal (stale dead-owner warnings only), no chain; its one finding was
  `busy: [(18002, 6.0, mdworker_shared ... com.apple.mdworker.shared)]`, 6.0 % against the 5 % bar.
- D pins: `align_v4_verify_d_pins.py` PASS: 19 files, 7 LFS sha256 matched, 41
  `.cache/huggingface/` files ignored (`d-pin-verifier-output.txt`).
- Cleanup: fence removed by the wrapper; R0 LaunchAgent gone; corespotlightd 716 and
  spotlightknowledged 73957 in state `S`; photoanalysisd 13374 still held `T` (item 188).

## Cause: a Spotlight importer caught 0.6 s after it was spawned

The unified log shows launchd spawning `mdworker_shared` pid 18002 at 18:05:15.296 PST (the
xpcproxy lines for that pid); the run's last census, which refused, ran at about 18:05:15.9. The
`ps` `pcpu` column it reads is a decayed recent average, so a process 0.6 s old that has just done
its start-up work reads high for a short time.

These workers are not rare. launchd retired a `com.apple.mdworker.shared` instance about every
2-7 minutes from 15:15 to 18:05 PST (one per 5-minute bucket while idle; two or three per minute
around the R0 launches and ends at 17:35-17:37, 17:51-17:53 and 18:05, so R0's own file activity
probably triggers some of them).

The census runs often: this run's report holds 101 census receipts in 905 s, one about every
15 s during the memory check. A complete R0 (the 1,800 s SMC capture, the ladder and the long
decode) takes several hundred. One refusal in 101 samples here, at that sampling rate, makes an
unchanged re-run very likely to be refused again before it finishes.

A follow-up sample on the idle Mac (18:10-18:18 PST, `ps` every ~0.7 s; script and output kept
under `/tmp/r0probe/`, not committed) copied the 1 MB `report.json` and `report.md` into a
scratch folder in the home directory at 18:10:58. Within about a minute launchd spawned two
`mdworker_shared` workers (2.3 % and 3.1 % `pcpu` at 1 s of age) and the long-lived `mds_stores`
(pid 541, 23 days old, also on the census list) read 35.7 %, then 24.3 %, then 2.2 % over about
1.5 s. So a file R0 writes into an indexed folder can by itself put a census-listed process above
5 % for a second or two. The census then refuses a run for work that is over before it is seen.

## Disposition

Item 181/185 (3): an infrastructure fault, not a `load` failure and not a model result.

It is the second census refusal in a row, both by a start-up or post-write burst of a Spotlight
or Photos process that the census reads through `ps`'s decayed `%CPU`. Doctrine (Ed, 2026-10-05,
"physics refuses"): a contending process above 5 % CPU refuses, measured directly; a check that
reads a proxy is rewritten to measure the quantity. The repository already measures it directly
in `joulewise/hazards/contention.py` (CPU-seconds per second from the difference of cumulative
CPU time between two `ps` snapshots, limit 0.05, 30 s interval, both from `prewindow`). R0's
`QuietGuard` (`joulewise/align/r0_host.py`) still uses the single-snapshot `%CPU` proxy.

So no unchanged re-run. Fix lane `fix/2026-11-07-r0-census-cpu-interval` (cut from `165e12872`):
the guard judges each census-listed process by its CPU-seconds over an interval of at least 30 s,
against the same 0.05 CPU-s/s bar; a 0.6 CPU-s burst is 0.02 CPU-s/s over 30 s and passes, a
sustained 5 % contender still refuses. The decayed `%CPU` list stays in each receipt as a
diagnostic. Gates: Sol 6.1 build, an executing review by another model, CI on a draft PR into
`lane/2026-11-05-align-pilot10-benign`, cold Fable and Opus passes (measurement code). Then the
measurement checkout is fast-forwarded and R0 re-runs with a new record directory.

Size of what the fix lets through: below 0.05 CPU-s/s over 30 s is under 1.5 CPU-s per interval,
a few joules at most at one core's few watts; R0 is selection data, not a claim.
