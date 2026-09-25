# Charge — cold gate CLAIMGATE-01: rule the D-184 council's synthesis on the claim-admission gate and the equivalence rule

Assembled 2026-09-24 ≈11:40 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## Background in plain words

The claim gate (`joulewise/analysis_engine/claims.py`) decides whether a paper sentence about an energy difference is admitted. Desk simulations that call the production code (`ex-19-desk-simulations-README.md`, `ex-19-equivalence_replacement.md`) found four things:
- the gate misses 84 % of 5σ effects;
- its nominal interval covers about 56 % under shared shocks;
- the equivalence-night rule false-alarms 58 % of the time with no change;
- the proposed replacement is blind to a ×4 variance increase.

A Sol scout gathered the facts (`ex-55-packet-*`). Four blind seats answered brief `ex-58`: Sol `ex-59`, Astra `ex-60`, Opus `ex-61` and Fable `ex-62`. The magistrate's synthesis and proposed rulings CG-1..CG-4 are `ex-65-claimgate-synthesis.md`; its opening section builds the terms. You are the cold judge. The seats and the synthesis are arguments before you.

Ed's standard: "preventing bad science, not progress on the paper when models agree", and "make sure the barriers to acceptance aren't overly strict for no reason". A gate that admits no real effect fails that standard as surely as one that admits false ones.

## Questions (AFFIRM / write a different ruling; exact final text; BLOCKER / MATERIAL / NIT)

- **M1 (CG-1).** The directional rule: the replicate unit, the interval construction, the magnitude test (near endpoint > F_est vs point > F vs LCB > τ), scope, and Holm. Execute enough simulation, with the packet's harness or your own, to state false admission and power at 2σ and 5σ for the ruled rule.
- **M2 (CG-2).** The equivalence claim: the margin and the interval.
- **M3 (CG-3).** The equivalence night: m, the location and spread tests, the tolerances, and the re-based simulation precondition.
- **M4 (CG-4).** Implementation and rules-before-data. Is any existing registration or claim affected?
- **M5.** Anything the synthesis dropped or merged wrongly.

Finish with **"Claim-gate rulings (final texts)"**, executable without choosing, and a plain-language summary for Ed of at most 10 lines.

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Repository evidence may be read in your worktree, and simulations may run CPU-only under `/tmp`.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
5407ef832ad08b20250304d63eb2e41881f15d910a7c34c1b59e5aa66503f615  ex-19-desk-simulations-README.md
5c4466c63560a4280be07007fa44876774c1ea38f7ea8bd19a8d8332457c0da2  ex-19-equivalence_replacement.md
acbb25dc0433f857e0deaa5eda4044e23efc7635519f89ba6053ae0842d0ae1e  ex-55-packet-00-question.md
f0ba04a0b15262c4cd6f4f822f223bd1befa0009c170666c0565085a40bdc1fc  ex-55-packet-01-current-gate.md
a60feab598509823eea50bc2e983f60975ec0c5eef075a90e852aba652878d74  ex-55-packet-02-simulation-facts.md
4d8e803366e0d2dc90642f325e5f6db131c6651a7cf13181b73a44c0e31921b0  ex-55-packet-03-constraints.md
67943b4fe82e3f59a0f51304bbaf24f836a471dcacf1fe5f7630299c95fa0f50  ex-55-packet-04-options.md
b765971ebd7e1dab94562a3e3df565583bd907e43356f09dec45990066fb304b  ex-55-packet-05-open-facts.md
3a328ac01d0d6d434e99ff4b76a150e9136a535eec46bca677cee6a1d6db5c5c  ex-58-claimgate-council-seat-brief.md
e8858f661af0948b990b4d11f463dbe11e11a1a422b219ffbc53350819d54042  ex-59-claimgate-seat-sol.md
fda366c8e2d3886561e1b4539bdac0225ba39e93dcc68844e0d9804287175273  ex-60-claimgate-seat-astra.md
0df7231264e931cf16978c48f8c6581dcb261d1cfc032edbb9674a3572efc790  ex-61-claimgate-seat-opus.md
61ae8a608cbde1fd5930473102a4ecd1abe22f2694cecb0c88132dab711affd7  ex-62-claimgate-seat-fable.md
64a5e6449b956db3fdb53f7c6677bac101971623376743f7e63d4189a0a59d78  ex-65-claimgate-synthesis.md
```
