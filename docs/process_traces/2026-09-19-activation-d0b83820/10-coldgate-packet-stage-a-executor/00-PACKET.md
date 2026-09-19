# Cold-gate packet — QUIET-PREDICATE-EVIDENCE-01 Stage A executor: an evidence night under the night machinery needs (Q1) a registration guard change, (Q2) a frozen pilot protocol, (Q3) a new probe-receipt contract — rule 11: capture/pre-registration guards and probe obligations stay on the cold-gate path (NIGHT_HANDBACK.md:134)

Assembled 2026-09-19 ≈12:25 PDT by the resident magistrate (activation d0b83820). Mechanically assembled: exhibits A/B are verbatim `sed` line ranges at main `0c529f99`; C/D/E are the two consult seats' reports and the lead synthesis verbatim (with the prior adopted Stage A design). The magistrate's rulings-so-far are inside Exhibit E (44a) and are NOT binding on the judge.

## What was found

The quiet-admission cutoff for the night gate may not be activated until lane 232 supplies joules per 480 s slot under controlled synthetic load (cold gate 70 Q4). The harness that measures this merged today (PR #360, `scripts/sample_quiet_predicate_evidence.py`); nothing runs it. Its `collect` is `[QUIET-MAC]` work — no agent session may be alive — so the only unattended executor is the night LaunchAgent pair installed from a plan under NIGHT_HANDBACK. Two seats (Exhibits C, D) agree the executor should be a separate evidence payload under an unchanged v2 `DIAGNOSTIC_NO_PACK` plan (chain selected by `chain_path`, sealed manifest under the chain digest; v2 admission; load injected after GO inside the chain; teardown covering collector/load/recorder/sampler groups; a verification-only evidence probe). They disagree on three things the judge must rule (Q1–Q3), and the refuter found a blocker the consultant missed: `_check_registration` (Exhibit A, `night_gate.py:1333–1352`, constant :37–44; C1 must PASS :467–473) hashes the plan's `registration_path` bytes against the ONE hard-coded D-166 calibration pre-registration digest, so an evidence night either falsely attests the D-166 dominance-criterion pre-registration or the gate must learn a second digest. The v4 quiet-admission route cannot be used to admit the campaign that validates it (Exhibit A `quiet_admission.py:155–180`; Exhibit B contract :78–90: `busy_core_max > 0` and `cutoff_authority` required) and v2's load-average predicate is the one shown defective on 09-15/09-17, so it cannot protect the idle reference alone.

## Q1 — the registration guard for an evidence night (rule one option or write a better one)

- (a) The gate learns a SECOND registration digest: an evidence-campaign registration document (the pilot protocol frozen before arming, Q2) whose SHA-256 is bound the same way D-166's is, selected by the plan's `registration_path`; C1 PASS means "the registration named by the plan hashes to a ruled digest for THIS plan class". State how the gate knows which digest applies (plan field? chain manifest? the registration file's own declared class?) without adding a v2 schema key, or rule that a v2 key is acceptable here.
- (b) Keep the single D-166 gate and bind the campaign protocol separately through the chain manifest (the consultant's shape): rule whether C1 PASS on the D-166 digest is a false attestation for an evidence night, as the refuter says.
- (c) Other, with the same burden: no plan may be armed whose receipt attests a pre-registration it does not run under; every guard change goes through this gate (Exhibit B NIGHT_HANDBACK.md:134).

Deliver: the ruled option; the exact code shape (`night_gate.py` constant/table and `_check_registration`), the receipt row text, and the docs clauses that change (NIGHT_HANDBACK.md, runbook §verify-only probe row).

## Q2 — the pilot protocol, frozen before the first arm

Rule the FIRST window: (a) idle-only variance pilot (~75 min: settle, then N × 600 s `collect` envelopes with a predeclared interior 480 s analysis interval, the quiet-admission `sample_interval` recorder running for post-hoc exclusion, no load generator) — give N, the settle, the exclusion rules (census not clean; AC/thermal probe failure; cadence/anchor unresolved; incomplete support), and what its summary must report (paired-idle spread in J per 480 s; observer cost; cadence distribution; boot/OS build); (b) the consultant's 44-minute idle → 0.2-core → idle block as the first window; (c) both, in that order, as two plans. State the arithmetic that sizes block two from the pilot's measured spread (the refuter: n = 3 per cell suffices only if the paired-ΔJ spread ≲ 0.6 J; the deliverable is an upper bound, not a transition point) and the "no cutoff qualifies" branch.

## Q3 — the probe-receipt contract and the amendment scope

The calibration probe (Exhibit A `night_agent_install.py:745–800`, `run_night.py:3255–3275`) demands `CALIBRATION_LEDGER` / `LEDGER_HEAD_PIN` literals and reads the ledger; an evidence chain cannot satisfy it honestly. Rule: (a) a typed evidence probe receipt (verification-only; verifies the manifest bindings, interpreter, chain digest, harness identity; never starts `collect`/`load`/power) as a SECOND probe kind dispatched by payload identity — name its receipt schema, its admission gates, and whether it is a contract amendment (which clause: runbook :3040–3055 verify-only probe row; NIGHT_HANDBACK.md:88–110 arm steps); (b) other. Also rule: is the campaign authoring tool (forced: `gen_derivation_night.py:475–505` refuses non-derivation receipts and any slot count but twelve) lead authority once the receipt kind is ruled; and is the quiet-admission sampler running INSIDE the chain as a recorder (no admission effect) a contract matter under `night_quiet_admission.md:20–60` or plain code.

## Constraints on the judge

Read-only. NOTHING IS ARMED on this machine. Wall budget 15 minutes, hard. Probes allowed: `git show 0c529f99:<path>`, `rg`/`grep`, `sed -n`; no test runs required (none needed to rule); Python snippets under `/tmp` only. No `sudo`, no `powermetrics`. Never touch `/Users/edr/code/JouleWise` (canonical root), any `/Users/edr/JouleWise-measurement-*` directory, `/Users/edr/night-custody`, or `~/Library/LaunchAgents`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
ab7aef98d1c16e447d9c7d73c1866ce4f10af99de587beccff4b65a08e4c2e48  exhibit-A-code.md
7b5c6e6b8777a8a2f24988d4822deec19953af0c777a978cab96824fb3e47095  exhibit-B-contract-clauses.md
3e0aa5da71c726914b831a15b254fd61afba750b53ca4b781a01d5bab4e4e88d  exhibit-C-consult-44.md
c831de594910a2812cd38d9c22637d769ac17701c3b5e8f058141f0b0db6d9d1  exhibit-D-refuter-45.md
12cb55fa4eeb1097d9535e183b8059f020129d22e647a5ff6cfe07bcfa32f31d  exhibit-E-synthesis-and-prior-design.md
```
