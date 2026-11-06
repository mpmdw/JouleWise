# ALIGN v4 off-Mac pre-qualification

Status: **pass** (stage r0). Software/model/config/fixture pre-qualification only. Grants no arm, R0 or R1 result.
Host: Mac16,13; checkout 105e78c692e7ed7002ffe0667445a86b9279c1cf (dirty=False); model backend: sibling.
Total wall time: 281.514 s.

| Check | Status | Seconds | Problems / reason |
|---|---|---|---|
| stack | pass | 0.055 |  |
| r0-config | pass | 0.323 |  |
| launcher | pass | 0.858 |  |
| kit | pass | 1.826 |  |
| d-pins | pass | 0.611 |  |
| d-pin-verifier | pass | 0.006 |  |
| d-tokenizer-files | pass | 0.085 |  |
| template-render | pass | 48.528 |  |
| nll-fixture-ids | pass | 2.165 |  |
| template-rewrites | diagnostic | 0.11 |  |
| tool-roundtrip | pass | 1.945 |  |
| checkpoint-native | pass | 12.799 |  |
| model-load | pass | 6.553 |  |
| load | pass | 167.621 |  |
| generated | diagnostic | 37.356 |  |

## Stays on the measurement Mac (measures the Mac itself)

- `r0.host`: pmset AC/powermode/thermal, iogpu.wired_limit_mb, hw.memsize on the Mac
- `r0.host-identity`: hw.model == Mac15,9 and >=128 GiB
- `r0.disk`: free bytes and D/anchor file hashes on the Mac's own disk
- `r0.smc`: SMC key enumeration and GPU step response (S_fast/S_slow)
- `r0.ladder`: effort-rung selection by decode cost on the M3 Max
- `r0.long-decode`: 40,960-position Metal memory growth
- `r0.memory`: peak Metal memory and swap at the context cap
- `r0.load (D numerics)`: teacher-forced NLL of the real D weights (needs the 29.5 GB artifact)
- `r0.generated/checkpoint (D, B7)`: B7 verdict and timing with real D generation
- `r0.model-load (D)`: loading the real D artifact into Metal memory
- `launcher.preflight`: AC power and free disk on the Mac
- `launcher.launch (live)`: LaunchAgent bootstrap, desk fence handoff, Spotlight pause on the Mac
- `r1.*`: powermode A-B-A, soak, high-power adoption, thermal/deadman/OS-load measurement
- `w1.w1_disk_gate`: 80 GB free and offload re-hash on the Mac's disk
- `w1.install`: launchd census and agent installation on the Mac
- `w1.disk_snapshot`: statvfs/important-capacity on the Mac
- `magistrate.census/fence/span`: live process table, desk fence and plan span on the Mac

Full evidence (IDs hashes, renders, cases, provenance) is in the companion JSON.
