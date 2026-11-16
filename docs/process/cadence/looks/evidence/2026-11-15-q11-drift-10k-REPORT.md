# RL-173 Q11: 8 % drift cell, rows at 10,000 repetitions (synthetic only)

**Decision by the rule (both ≤ .035 → 0.08, else 0.04): 0.08.** Both rows are at or under .035 at 10,000 repetitions.

| Row (cell, h = −9 %, d = 8 %) | rows false-signature rate, 10,000 reps | SE = sqrt(p(1−p)/n) | 1,000-rep value (RL-151) |
|---|---|---|---|
| B +30 % all | **0.0280** | 0.00165 | 0.034 |
| B bank +30 % / spam −11 % | **0.0231** | 0.00150 | 0.030 |

The rows statistic is scorer `iii` in `s_oc_rl149.py`, field `scorers.iii.signature`. It is the share of replicates whose `decide()` returns a signature, with the denominator equal to all reps. RL-151's report reads "rows .0265" for the worst10k cell, which equals `iii` = .0265 there, and that confirms the mapping. As a side figure, count cut (`v`) is .0228 and .0237.

## How the RL-151 cell was produced
- Script: `s_oc_rl149_named.py --set3` (sha 874ab2e8…; full identity below, the same as `meta.script_sha256` in `results_rl151_drift.json`). It imports `s_oc_rl149.py` (sha a76dbfbb…; full identity below, the same as `meta.rl149_sha256`), which imports `s_oc_sim.py` and `claim_b_power_copy.py`.
- `cells3()` cells `B +30% all d=0.080 h=-0.09` (length=0.30) and `B bank +30% / spam -11% d=0.080 h=-0.09` (length_pair bank 0.30 / spam −0.11), both with drift=0.08 and hot=−0.09. Every other setting is `s_oc_rl149.CFG`, with effect 0.
- Seed 20261114, reps 0..999, chunk 50, 8 workers. Each rep is seeded independently: `rng = Random(seed*1000003 + rep)` and `mrng = Random(seed*7919 + rep*31 + 5)`. Results therefore do not depend on chunking or worker count.

## Reproduction (1,000 reps, seed 20261114)
`results_q11_repro1k.json`: rows .034 and .030. **Exact match.** Every scorer field of both cells is identical to `results_rl151_drift.json`.

## Seeds for the 10,000-rep run
Seed 20261115, reps 0..9999. The draws are disjoint from the 1,000-rep run (seed 20261114, reps 0..999) and from the RL-151 worst10k run (the same seed, reps 0..9999):
- `rng` seeds differ by 1,000,003 per seed step, which is more than 9,999 reps.
- An `mrng` collision would need 7919 = 31·Δrep, which has no integer solution because 7919 is prime.

## Command
Copies of the four scripts, unchanged (hashes below), plus the driver `q11_run.py`. The driver limits `cells3()` to the two d=0.080 B rows and then calls the unmodified `s_oc_rl149_named.main()`.
```
cd /Volumes/JW-EXT/scratch/look-r6/q11
TMPDIR=/Volumes/JW-EXT/scratch/look-r6/q11/tmp python3 q11_run.py --set3 --reps 1000  --seed 20261114 --workers 8 --chunk 50 --out results_q11_repro1k.json
TMPDIR=/Volumes/JW-EXT/scratch/look-r6/q11/tmp python3 q11_run.py --set3 --reps 10000 --seed 20261115 --workers 8 --chunk 50 --out results_q11_10k.json
```
Python 3.14.6 ran on the Air, not the MBP. Wall times were 21 s and 249 s.

Full SHA-256 identities (retained in `/Volumes/JW-EXT/scratch/look-r6/q11/`):

| File | SHA-256 |
|---|---|
| `q11_run.py` | `52dcb6b3bc60cee50881d60c9f6de917b442948f76f8b4de307499af518c9401` |
| `s_oc_rl149_named.py` | `874ab2e80d71175b74b95363ccfca5e0d26a6c95b40343e6dfae1f5c27a4273f` |
| `s_oc_rl149.py` | `a76dbfbbcc2aa9c467945acd9f4df8f4e2d5e7d245b5ce6ea1967c759c6a135e` |
| `s_oc_sim.py` | `4ce227748b3ca547b144958b6b003f5c53055d2fb90e8837d51ab78725037e37` |
| `claim_b_power_copy.py` | `6ddcde86112a29f236647a7e0a48b56fcd67f6b2db9ead3995e04f0b8fc06fc7` |
| `results_q11_10k.json` | `5488add070af6ed1aa9949a08fca0104b89dfa555b4d63acd5c8da2b5419f521` |
| `results_q11_repro1k.json` | `086fec2b359640ee02deb698cf4ccd049277acf32bae4a2df17397b3f0fbe24b` |


## Finished
`date`: Sun Nov 15 15:09:48 PST 2026
