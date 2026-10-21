# BYTES item H: disk refusal rule (lead ruling, activation 283e9802, 2026-10-21)

**Question.** The H runner's `prepare` refused on disk: required 307,042,815,642 B (footprint 145,981,542,042 B
plus R6's 150 GiB reserve) against 122,446,086,144 B free. The executing review (JouleWise-data ca761b4,
`reports/bytes-h-review/opus.md`, M3) found the rule would have refused all nine finished block-6 sessions.

**Seats** (blind, two models): Sol 6.1 high (local; `/Users/edr/night-archive/283-bytes-h/disk-consult-sol.md`) and
Fable 5.1 (JouleWise-data `claude/bytes-h-disk-consult-fable` 761921295, `reports/bytes-h-disk-consult/fable.md`).
Both agree on the form below. They differ only on the per-copy terms (Sol 76.52 GB, Fable 86.24 GB). Fable's terms
are adopted because they rest on two facts it verified. The sampler is model-blind: its interval and samplers are
fixed, and the measured bytes per stream second stayed within 1,751,608 to 1,846,209 B/s over 125 members. WAIT
samples continuously, so it accrues at the stream rate, not the member-wall rate.

## Ruling

1. `prepare` refuses only when the free bytes on the session volume are below P. Free bytes are statvfs
   `f_bavail × f_frsize`, purgeable excluded.
2. **P = c × (B + WAIT) + fixed**, where:
   - B = max(stream-rate basis, wall-rate basis), summed per model over count × that model's own allowance. The
     stream rate is the maximum observed bytes per stream second; the wall rate is the maximum observed bytes per
     member-wall second. Each model uses its own allowance, not the longest member's.
   - WAIT = stream rate × the registered 7,200 s session wait.
   - fixed = the committed fixed-artifact bytes.
   - c = 2 physical copies: raw plus the chain's rsync backups. The harvest archive is an APFS clone (`cp -c`,
     `joulewise/b5/harvest.py:1607`) and allocates nothing.
   - For H this gives P = 86,236,568,521 B.
3. **No reserve term.** R6's 150 GiB comes from design §15's model-download rule ("keep free disk above 150 GiB"
   while downloading pilot models). Nothing measured ties it to the window hazard. Inside a window, the existing
   10 GiB `disk.low` stop measures the hazard directly.
4. **Replay** (acceptance-rule requirement):
   - The same formula on r4-alpha's measured sums gives 69,948,643,530 B. The lowest free disk at desk start
     across the nine sessions is 113,618,456,576 B, so the rule refuses 0 of 9.
   - Measured whole-window drawdown (arm to desk start) reached 22,230,519,808 B (r3-beta, Sol's read of the arm
     receipts). That is inside the formula's 69.9 GB for that session shape.
   - H at 105 GB free arms with about 18.8 GB to spare.
5. **Disclosure, not refusal.** `prepare` prints P with each term and c, the free bytes, and the purgeable bytes.
6. **Open measurement.** The nine sessions' arm records give free_at_arm − free_at_desk_start, which measures c
   directly. The next H desk computes it and prints it beside c. It changes no refusal unless a measured value
   exceeds P's assumption.
7. **Scope.** This rule governs item H now. For BYTES pass sessions, R6's reserve goes to the J/C5 disk gate with
   this ruling as the proposal. The same form applies to each pass's counts and allowances.

## Executed evidence

Seat computations, both recorded in the reports above. The lead re-checked the replay inputs:

```
$ python3 /tmp/m283/replay.py   # reads the nine /Users/edr/night-b6/sessions/*/archive.desk/compression-summary.json; P = 69948643530
9 sessions; min free_bytes_before 113618456576 ; refused 0
exit 0
```

The Opus review's P6 probe recomputed the current rule's 145,981,542,042 B footprint exactly (cited at
JouleWise-data ca761b4 `reports/bytes-h-review/opus.md`, P6 block).
