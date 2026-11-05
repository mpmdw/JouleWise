PR #658 replacement body (prepared offline; not posted)

The rejected R0 tool decoded Apple Silicon #KEY in the wrong byte order,
selected small quantized/stale readings through a noise ratio, and installed
a temperature journal in pinned hazard/policy code. This fix moves decoding,
SMC inventory and the bundle-local sidecar into `joulewise/align/apple/`,
restores the five core modules, and leaves R0 as inventory/step data only.
R1 classification follows FINAL-DESIGN §2.6: physical ΔT, t63 ≤5 s, longest
cooling τ ≤300 s with ΔT ≥3 °C, and <1% errors. Coverage now tolerates sampling
jitter while retaining real gaps; quiet checks retain CPU/power/thermal evidence.

Binding authority: `docs/align/council-2026-11-05/FINAL-DESIGN.md` §2.6/V8
on the council branch, plus Amendment 1 (user ruling: W1 Qwen3.8-27B only;
Qwen3-Next dropped; Flash-Next later). The amendment file was unavailable in
the accessible Git refs; its exact commit is still requested from the lead.

Synthetic tests replay the reviewer's observed #KEY/ioft bytes and cover
selection, coverage, sidecar lifecycle and worker cleanup. Native SMC/MLX
validation remains PROVISIONAL; none was run in this sandbox. See the run
report for exact sequential commands/results and sandbox integration failures.
The reviewer previously passed driver 48/48 and import graph 6/6; those are
separate from this fix round's test results.

PR #666 must migrate the removed campaign/monitor hooks to the optional
ALIGN slot and in-process sidecar; all interface changes are listed in
`docs/align/smc_temperature.md`. No measurement data, existing policy/pack,
coordination state, full-suite run or network operation is part of this fix.
