# GOAL.md status-log entry template — lead appends after reviewing real evidence

Do not paste this as a completion claim before the native run. Keep unrun,
aborted and failed checks explicit. Preparation alone closes no GOAL item.

```text
- 2026-11-07 [time, zone]: P6/P7/P5 Mac validation [PASS / PARTIAL / ABORTED].
  MacBook Pro M3 Max 128 GB, macOS [build], mlx 0.31.2 / mlx-lm 0.31.3,
  canonical module [full sha256], source de4b8e4d43b917e7706784d8bb445c9af86a3540,
  artifact [maxfit / maxfit5], manifest ordinary SHA-256 [digest]. Source and
  converted model are on WD SN7100 / Express 1M2 APFS /Volumes/JW-EXT.
  GOAL 6: [result], contexts 4,096/16,384/40,960 incl decode, Metal peak [GB],
  RSS [GB, overlapping], PLE resident [GB, overlapping], swapout delta [0 or value],
  pressure [level + minimum free %], prediction error [%, accounting basis].
  GOAL 7: coherence/NLL [result + per-text report], XML tool round trips [result],
  GSM8K30/IFEval25 [counts], hosted bf16 identity [verified / operator-attested /
  unavailable], per-item comparison [result], top-k [result / unavailable + why].
  GOAL 8: low/medium/xhigh prefill/decode medians [report table], chunks 512/2048,
  P5 targets [met / missed / applicability pending]. PLE I/O [disk MB delta,
  elapsed, cache-state qualification]. Fallback [none / exact abort + fresh rerun].
  GOAL 11 full gold: [separate PR680 result + coverage evidence / still OPEN];
  Saturday end-to-end validation does not substitute for full 48-layer gold.
  Validation only, outside all measurement windows. External volume ejected
  and unplugged [time]. Evidence [immutable bundle + hashes], code [commit].
  Remaining gates [list]. No energy or study-result claim is made.
```
