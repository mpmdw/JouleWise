# Charge — cold Fable final pass A292-FINALPASS-01: the sealed scored reducer (lane A292)

Assembled 2026-09-25 10:17 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## What you rule on

- **Merge candidate:** branch `feat/2026-09-25-a292-scored-reduce` at head **e144bf07**, which includes a merge of main `95521871` and a records-only commit.
- **Code diff vs main:** `joulewise/scored_reduce.py` (new), `tests/test_scored_reduce.py`, `tests/scored_reduce_checker.py` (an independent stdlib oracle) and the witness generator. Everything else is `docs/process_traces/2026-09-25-activation-152c9255/`.

## Rulings it implements

- "A292 reducer rulings v1.1" (E2): `docs/process_traces/2026-09-25-activation-152c9255/09-coldgate-packet-a292/30-addendum/21-coldgate-fable-a292-addendum-ruling.md`.
- As amended by A292-ESC-01: `…/25-coldgate-packet-a292esc/20-coldgate-fable-a292esc-ruling.md` (the generated-witness spec G1–G6, and input bounds ENERGY_MAX_J = 10**12 and INT_MAX = 2**53).
- Magistrate errata readings (record 00 item 34): nine window keys; the CAP_BOUND_FRACTION witness at 0.30.

## Method

- A Sol-written RED harness and oracle, then an Opus implementation that never read the oracle, taken to GREEN.
- An Astra contract lens.
- A Sol M8 mutation sweep, three passes: 23, then 3 (escalated), then 0 non-equivalent survivors.

## Evidence

- `ex-02`: the Astra lens.
- `ex-04`, `ex-08`, `ex-11`: the sweeps. The final one has 119 mutants, all killed or proven equivalent.
- `ex-12`: the lead's bench run at `241ea65c`, reducer plus packer plus fuzz: Ran 111 tests, OK.

## Questions

- **A1.** Verify `scored_reduce.py` implements E2 as amended: the entry (the verifier as the first statement), the schemas, the refusal codes and their order, completeness (S7), the K3/K24 cap rules, energy summed once per counted window, terminal energy once per key, executed-status presentation, and the input bounds.
- **A2.** Verify the oracle and generator are independent of the implementation (no `joulewise` import; derived from the ruling) and adequate.
- **A3.** Run `tests.test_scored_reduce`, excluding the 200-night differential unless your budget allows (it takes about 35 minutes), plus `tests.test_scored_packer`.
- **A4.** Anything that would let a counted number be wrong, or an item be silently dropped, when the first scored night is reduced.
- **A5.** Rule MERGE, FIX-FIRST (with exact texts), or REFUSE.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`.
- The discovery suite and background tasks are not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
a0e418e75cc023b30f335485f7062950e9d09447de6e70eda91a68aa98c1154f  ex-02-astra-contract-lens.md
b8c4bc21e16fa448ea8664c83754cbbef79d639cbaf344f32b809cdf143aae12  ex-04-sol-mutation-lens.md
daa126162cf6d300ba5305ca066681939ef28b0e11d70df98dd70fe770f718eb  ex-08-delta-sweep-1.md
a64eea98583ebc9a4018969d6de496d27f596bea9ae494650281dd336618a491  ex-11-delta-sweep-2.md
b5b67d287f45fdff310cbbd36c4cf53c7b1219663a8338ece641c77170fdbf05  ex-12-lead-bench.md
```
