# Charge — cold Fable final pass PRR-FINALPASS-01: PR-R, registration Revision 5 and issuer changes for the 25G83 calibration

Assembled 2026-09-25 09:52 PDT (clock-read) by the resident magistrate (Opus 5.5, activation 152c9255). Nothing is armed.

## What you rule on

- **Merge candidate:** branch `feat/2026-09-25-acc-registration-rev5` at head **8cd9e831750d6ac73d4b293148082187f0723ebf**, which includes a merge of main `95521871`. The diff is vs `origin/main`.
- **What it implements:** acceptance rulings v2.1 R4, R5, R9, R10 and R17 (`docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md` §5, on main):
  - the n1/n2 D-126 disposition, with registry and issuer consumer;
  - Revision 5 of the preregistration, with placeholders for the PR-L merge sha and the rendered-plist digests, to be filled at the seal;
  - the re-keyed v4 salvage (n ≥ 12, zero headroom, futility at 6);
  - the R10 simulation re-run;
  - the R17 pin-free cadence report.
- **Order:** PR-R merges after PR-L (PR #412).

## Review history (exhibits)

- Opus contract lens `ex-01`: no BLOCKER; S1–S6.
- Astra execution lens `ex-02`: no BLOCKER; archive content ids rebuilt; cadence report STOPs n1/n2 and passes Interactive; simulation seed-stable.
- Delta re-audit `ex-05`: no BLOCKER and no SHOULD-FIX; all closed; r7 validation byte-identical (266/266 keys); 387 tests OK.

## Questions

- **R1.** Verify the diff implements R4, R5, R9, R10 and R17 exactly. Verify that the four D-138 pinned files are byte-identical to main, and that r7's validation is unchanged.
- **R2.** Verify that the Revision 5 text has every element (a)–(o) as ruled, and that it cites a ruling file that exists on main.
- **R3.** Rule whether rule text R16-a (the T0-rehearsal exemption, affirmed by the PR-L final pass) must also appear in Revision 5 before sealing, or whether it belongs only to the acceptance rulings record. If it must appear, give the exact text.
- **R4.** Verify the seal mechanics: the issuer refuses while placeholders remain, and the seal step as written in Revision 5 is executable.
- **R5.** Run the touched modules: `tests.test_issue_calibration_acceptance_generation`, `tests.test_calibration_bracketing`, `tests.test_acc_25g83_rev5`, `tests.test_preregistration_chain_digest`, `tests.test_calibration_cadence_report` and `tests.test_reissue_calibration_acceptance`. The first takes about 10 minutes; run it if your budget allows.
- **R6.** Rule MERGE, FIX-FIRST (with exact texts), or REFUSE.

## Constraints on the judge

- Read-only.
- Never run `sudo`, `launchctl` or `powermetrics`.
- Never touch `/Users/edr/code/JouleWise` (the canonical root) or `/Users/edr/night-custody`. Archived data under `/Users/edr/night-archive` may be read.
- The discovery suite and background tasks are not allowed.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs or memory.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
23414fe345b78465868837b6e39f1f51fec8109343c2a3fd04c5e13a20761124  ex-01-opus-contract-lens.md
ef2e7863baa982ae41b504704e309c174edc46c91c743742a5625c87a2b2944e  ex-02-astra-exec-lens.md
c2361eacfca640fb889d10eedff84c2cd692b3d11e045d182b349ccfcfec8976  ex-05-delta-reaudit.md
```
