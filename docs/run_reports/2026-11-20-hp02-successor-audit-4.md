# hp-02 successor audit round 4 repairs · 2026-11-20

Independent round-four execution blocked `c4967a810`. The three probes reached simulated bootstrap at local midnight with the previous date's rank evidence, at the opening of the instrument window, and after the host left Automatic during the claim write. The evidence is in the lead's scratch report at `pl-hp02-successor/audit-4/FINAL-MESSAGE.md`.

**G1.** The Run gate returns WAIT in the 120 seconds before a derived boundary. It reads the finite queue and applicable expiries, local date, higher-ranked eligibility windows and the counted calendar. It uses the pinned window and occupancy predicates to derive the argument, soak, leg-start and clearance boundaries. The final decision also protects the counted schedule and launcher deadline through the demonstrated startup bound. The 600-second expiry margin stays in effect.

**G2.** Run publishes the claim durably, then re-reads the published Start receipt, staged inputs, current observation and admission custody. It re-evaluates rank, the clock and occupancy, takes the live census, and reads the fence, marker and AC mode before dispatch. The gate performs no writes or sleeps on this final path. On a known pre-dispatch refusal it drops the unused claim. A state change after the final read remains the residual risk. The MBP is quiet under the magistrate, and host mode changes only through `measurement_mode`.

Run observations must now include complete dated `start_windows` for each higher rung, drawn from that contender's actual allowed pin and argument windows. Issue and Start use their existing records. The six frozen fixtures were checked byte for byte. The regressions cover 74,907 guard offsets, 32 midnight and instrument launch combinations, 24 read-last state and latency cases, and the previous R1–R3 suites. They use synthetic observations and make zero native-command attempts. The legacy replay preserves its expected held-item failures. The local suite is targeted, with the full suite delegated to hosted CI per CANONICAL.

Independent delta execution on the repair remains the next item gate.
