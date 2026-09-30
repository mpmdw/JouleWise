```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Reissue the old-build calibration for evidence windows; activate only the fresh successor after audit and closing approval.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "exact",
    "head_start": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "head_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","summary":"The unchanged default becomes unusable after the cap changes; its replacement must preserve 17 members, not 12."},
      {"id":"F2","severity":"blocker","summary":"The required preliminary issuance conflicts with the owner's choice."},
      {"id":"F3","severity":"blocker","summary":"The interim new-build registration creates hold work without supplying the needed default."},
      {"id":"F4","severity":"blocker","summary":"The planned early successor registration precedes closure, and absence alone does not prove launch refusal."},
      {"id":"F5","severity":"should_fix","summary":"Preparation and promotion tools need separately governed support for the successor."},
      {"id":"F6","severity":"should_fix","summary":"The existing third-window rule conflicts with the cap test, and several scientific boundaries need explicit preservation."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch\ngit rev-parse HEAD\ngit -C /Users/edr/code/JouleWise rev-parse origin/main",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","9eab16f81783c9cf079474c38d10c4a5bdf0f118","9eab16f81783c9cf079474c38d10c4a5bdf0f118"]},
      "expected":{"exit_code":0,"tail_regex":"9eab16f81783c9cf079474c38d10c4a5bdf0f118"}
    }
  ],
  "flags": [
    {
      "id":"L1",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"Recommendations amend existing rulings; they do not themselves authorize implementation or release.",
      "needs":"The cold judge should replace the sequence, closing conditions, historical-row treatment, and successor window rule together."
    },
    {
      "id":"V2",
      "kind":"verification_gap",
      "level":"nonblocking",
      "text":"This consult inspected records and source code only; no corpus replay, test suite, or live measurement was performed.",
      "needs":"Perform the specified implementation, replay, audit, and release checks before activation."
    }
  ]
}
```

CONSULT ANSWER: sol

## Findings

Terminology: a **build** is the operating-system version identifier. A **calibration** is a file containing measurement acceptance limits; a **member** is a capture contributing a value to those limits. A **capture** is one recorded sampler run. **B** is its timing-uncertainty value. The **estimator** computes B; the **cap** limits the number of search rectangles, called **cells**, that it tests. A **digest** is a SHA-256 fingerprint of file bytes; a **pin** is an expected digest. A **window** is a scheduled measurement session. **Claim-bearing** means its results may be reported as findings. **H1** forbids claim-bearing windows at 25G83 until the cap question closes.

**R7** is the registered 25F84 calibration; **R8** means its proposed maintenance re-issue. **r1** is the archived 12-member 25G83 calibration discussed here. The **successor** is the calibration derived from fresh cap-acceptance windows. **Registration in code** makes exact calibration bytes trusted by production software; **pre-registration** seals the experimental plan before collecting evidence. **Issuance** approves calibration bytes and need not activate them in production. A **commit** identifies a saved repository version.

Evidence notation: `T/` means `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/`. `I/` means `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/`. Code citations are from `origin/main` at `9eab16f8`, except promotion-tool citations, explicitly from `b953f4b0`. I read the investigation in full and read no other current consult seat’s answer.

### F1 — Question 1: default during the cap windows

**Answer:** yes, use an authenticated R7→R8 re-issue at 25F84, merged with the cap change. But it preserves **17 members**, not 12. Keeping the 12 25G83 values while labelling the file 25F84 would misstate its origin.

**Deciding reason:** derivation windows require both current estimator pins and a default that does not judge 25G83. Unchanged R7 fails the first condition after the cap edit; a 25G83 default fails the second.

R8 can be neutral with respect to the historical calibration’s numbers, conditionally on verification. It is not neutral with respect to which future captures the enlarged cap admits. Nor does copying old values establish that the new estimator reproduces them.

For admissibility, require:

- Preserve R7’s complete identity, 17-member table, exact decimal values, limits, historical ledger cutoff, and exclusions. The **ledger** is the append-only capture history. Preserve R7 itself unchanged.
- Authenticate each member’s manifest, evidence, and primary-byte hashes; replay all 17 under the final estimator bytes and reproduce each B exactly. Recompute the limits independently and compare them exactly.
- Give R8 a separately approved identifier, new estimator pins, new file digest and derivation seal, and an issuance record linking R7 and this amendment.
- Distinguish historical facts from current operation. R7 records a 165,000-cell derivation budget and an August rejection of enlargement. R8 must identify those as historical provenance, disclose the new cap, and state that A1 overrules that admission policy for 25G83 only.
- Check the real loader, generation-validation row, default identifier/path, and dependent pins together. Show that derivation preparation proceeds through the expected build mismatch, while ordinary 25G83 capture and claim evaluation still refuse.
- Register no extension allowing R7 or R8 to judge 25G83. Do not present R8 as fresh validation of new 25F84 claim windows under a broader admitted population.

There is no cheaper sound route in the inspected design. A separate provenance-only calibration interface could avoid maintaining a default, but would require a new contract and changes to both derivation preparation and validation.

**Evidence:** `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20–48,519–532`; `scripts/validate_powermetrics_fiducial.py:397–402,535–579,2092–2098`; `scripts/write_derivation_night_inputs.py:162–186`; `joulewise/calibration_bracketing.py:353–389`; `docs/decision_log.md:10363–10380`.

### F2 — Question 2: exact replacements for A1 step 1 and S6

**Answer:** issue these replacements together with the downstream amendments below.

**Replacement for A1 §5 step 1:**

> 1. Complete the owner-selected D-138 option (a): land the disposition-registry loader repair, promotion tool and their required tests, without registering the 25G83 r1 calibration or landing the withdrawn hold mechanism. Preserve the approved r1 bytes and their provenance in the record; their production registration is not a prerequisite for the cap transaction. R7 remains the default until the cap transaction. That transaction must also issue and register its 25F84 maintenance re-issue, called R8 here, preserving R7’s 17 members and calibration values after authenticated primary-byte replay under the final estimator bytes. It updates every required dependent pin in the same reviewed change. If R8 authentication, replay, derivation equality or issuance fails, the cap transaction waits and returns to council; no failure is cured by changing the historical corpus or registering a 25G83 interim. H1 remains in force. No production calibration or registered extension may judge 25G83 before the closing release authorized by this addendum.

**Replacement for row S6:**

> S6 — Candidate issuance or registration does not complete. ADOPTED, REPLACED. The owner’s option (a) removes r1 production registration as a prerequisite. R7 may be re-issued as R8 at 25F84 solely under step 1’s authentication, replay, unchanged-calibration and atomic-pin conditions. Failure of those conditions blocks the cap transaction and returns to council. The archived 25G83 candidate is neither substituted for R8 nor made production authority while H1 stands.

**Deciding reason:** the old prerequisite demands exactly the registration the owner withdrew, while expressly forbidding the replacement the derivation path needs.

**Evidence:** `T/20-cap-council/31-addendum-ruling.md:193,229`; `T/12-hold-consult/40-owner-brief-2026-09-29.md:39,45–47`; `I/30-r1-need/10-sonnet-r1-need-report.md:17–19`.

### F3 — Question 3: the interim re-issue

**Answer:** drop the 25G83 same-12 interim from production issuance/registration. Keep R8 for the windows and issue the fresh successor for eventual claims.

**Deciding reason:** the interim’s operational job was to provide current estimator pins, but its build makes it unsuitable as the default for these derivation windows. R8 supplies that job without introducing 25G83 authority.

The interim also documented that the cap-only edit preserved the selected 12 values. Preserve that scientific check as a sealed replay report: all 12 values reproduce exactly; all 24 original captures retain their dispositions except the eight cap stops. Preserve the original member selection and explain its old-cap dependence.

Nothing required for final 25G83 claims is lost: the successor already replaces the selected corpus with fresh captures. What disappears is an additional issued maintenance file, not additional evidence. Keep r1 available as authenticated historical comparison material; registration is unnecessary for reading its recorded statistics.

Consequential amendments must replace original §5 item 2, A1 §9’s retained interim requirement, and A1 §10’s request to name an interim. Retain the owner’s naming approval for R8 and the successor.

**Evidence:** `T/20-cap-council/21-coldgate-fable-ruling.md:175–179`; `T/20-cap-council/31-addendum-ruling.md:199,201,257,264`; `T/12-hold-consult/21-coldgate-fable-ruling.md:326–328`; `scripts/validate_powermetrics_fiducial.py:2092–2098`.

### F4 — Question 4: enforcing H1 and releasing the successor

**Answer:** choose re-sequencing. Permit no production registration judging 25G83 before closure. Approve and audit the successor as staged bytes, then activate the exact reviewed release and lift H1 together.

**Deciding reason:** all three hold rounds found another route. Creating authority early reinstates the problem the owner chose to remove. Re-sequencing removes the need for that authority during the hold.

If a 25G83 file is registered early under option (a), there is no demonstrated replacement for the withdrawn comprehensive hold. Do not describe a sentence in an issuance record as enforcement. A separate build hold would need a new design and independent evidence, not another patch presented as continuation of the stopped transaction.

There is also a narrower but important qualification: **absence blocks accepted results; it does not prove every claim-bearing launch is impossible.** Main’s manual campaign preflight returns immediately for configurations without the launch marker. Its inspected go-receipt checks have no 25G83 build check. Therefore retain H1 as a lead-controlled prohibition on claim authorizations and launches, allow only declared non-claim windows, and state that limitation honestly. If universal machine-enforced launch refusal is required, that is a separate lane even without a registered successor.

Issue these sequence replacements:

> Step 9: Merge the cap change with the authenticated 25F84 R8 re-issue and dependent pins. R8 becomes the default. Register no calibration or extension judging 25G83.
>
> Step 12: Derive the fresh successor candidate, pass the cold science gate, and seal its approved issuance bytes in the record. Prepare its production registration and default movement on an unactivated release commit. H1 stands.
>
> Steps 13–15: Freeze and audit that exact release commit, including its proposed successor registration, all claim consumers, and the old-file explicit-selection routes. Audit execution is read-only; no claim-bearing campaign runs. Any fix invalidating captures or estimator sizing follows the existing restart rules.
>
> Step 16: The closing ruling names the exact successor bytes, final audited release commit and all closing evidence. It authorizes activation of that commit, with H1 ending only when that activation succeeds. Activate the successor, its default and dependent pins together; verify the installed commit and bytes before authorizing claims. Any changed release commit requires renewed review and audit.

Replace **C4** with:

> The successor is derived from the fresh registered corpus, scientifically approved, sealed as issued bytes, and present with its complete production registration in the audited, unactivated release commit. The closing ruling authorizes those exact bytes to enter force in the closing release.

Retain **C6’s exact-commit requirement**: claims run from the audited release commit. File the closing ruling as separately authenticated governance evidence; do not make an unaudited code commit to add its citation. This avoids requiring the successor to be active before the ruling that authorizes activation.

**Evidence:** `T/12-hold-consult/21-coldgate-fable-ruling.md:279–305`; `T/12-hold-consult/40-owner-brief-2026-09-29.md:15–23,39,47`; `T/20-cap-council/31-addendum-ruling.md:201–208,214–216,238–250`; `joulewise/calibration_bracketing.py:147–199,2179–2182`; `scripts/run_campaign.py:1866–1881,8090–8094`; `joulewise/arm_readiness.py:10111–10134`.

### F5 — Question 5: promotion and re-issue tools

**Answer:** use different existing tools for their actual jobs:

- R8 preparation: `reissue_calibration_acceptance.py`, followed by governed issuance assigning the approved new identity and pins.
- Fresh successor preparation: `issue_calibration_acceptance_generation.py`, amended for the successor’s actual registration.
- Successor issuance: generalize `promote_calibration_candidate.py` through an explicit, reviewed issuance specification. Preserve the r1-specific mode if still needed for historical reproducibility.

**Deciding reason:** the re-issue tool preserves an existing corpus and emits only a marked candidate. It neither derives the fresh successor corpus nor issues or registers it.

The promotion specification should bind the expected candidate file digest, input seal, identifier, build, rulings, issuance text and permitted changes. Require complete citations and correct digests; preserve candidate scientific fields and exact numeric meanings. Produce deterministic bytes and support exact-output checking. The tool should not modify production registries or choose the default.

Do not simply replace the hard-wired r1 constants with arbitrary command-line values. Test wrong candidate/build/identifier/seal, missing citations, changed members or limits, and unauthorized hold wording. Independently recompute the candidate and issued-file seals and verify the actual written output.

R8’s preparation tool authenticates stored member evidence, but the inspected authentication function does **not** replay primary power/event bytes. Its “PROCEED” result therefore cannot replace the required physical replay.

**Evidence:** `scripts/reissue_calibration_acceptance.py:1–8,173–223,249–288,577–602`; `scripts/issue_calibration_acceptance_generation.py:1730–1800,1980–1985,2226–2244`; `scripts/promote_calibration_candidate.py@b953f4b0:22–43,100–153,156–207,210–227`.

### F6 — Question 6: ways a number or its interpretation could become false

**Answer:** the amendments are sound only if these boundaries remain explicit.

**Deciding reason:** unchanged numbers do not establish unchanged selection, clock validity, or measurement authority.

1. **Historical selection must remain historical.** Neither the eight old cap exclusions nor the eleven September 19 values become successor members. Preserve the old 12 as members of the archived 25G83 calibration, not as members of R8 or the fresh successor.
   Evidence: `T/20-cap-council/21-coldgate-fable-ruling.md:175–179`; `T/20-cap-council/31-addendum-ruling.md:228`.

2. **Amend the historical-row recognition rule.** S5’s phrase “members of the predecessor” is misleading once the operative predecessor is R8. Name the 12 archived r1 members by content identifier and approved provenance, exempt only those rows from the successor’s outside-registration refusal, and preserve that refusal for every other unexplained valid row.
   Evidence: `scripts/issue_calibration_acceptance_generation.py:1430–1442,1905–1915`; `T/20-cap-council/31-addendum-ruling.md:228`.

3. **Fix the third-window contract before collecting data.** A1 permits W3 when fewer than 24 captures count toward the cap test; the current issuer refuses W3 once the first two contain 12 valid rows. Those are different quantities. Implement the amended cap-count rule without looking at B, separately state the calibration-member floor and futility rule, and retain every valid resolved member. Do not change these after seeing results.
   Evidence: `T/20-cap-council/31-addendum-ruling.md:175`; `scripts/issue_calibration_acceptance_generation.py:1832–1838,1867–1873,1897–1904`.

4. **Do not turn arithmetic into measured coverage.** A1’s fixed timing constants provide a reproducible design check, not proof of a universal execution-time bound. The 100–150 ms frame range is partly unmeasured, and 24 zero-stop captures do not establish a negligible future failure rate. Keep the per-window tripwire, whole-window holds for stops, and complete attempted-bracket accounting.
   Evidence: `T/20-cap-council/31-addendum-ruling.md:162–175,187,246–248`; `T/20-cap-council/21-coldgate-fable-ruling.md:171`.

5. **Keep clock controls and outcome blindness.** Require network-time-OFF receipts and readable, correction-free logs; commit cap-test evidence before reading new B values. No rejected window may be salvaged under another cap or by retaining convenient survivors.
   Evidence: `T/20-cap-council/31-addendum-ruling.md:175–179,224–225`; `T/20-cap-council/21-coldgate-fable-ruling.md:178`.

6. **Preserve actual successor arithmetic and identity.** Its operative predecessor is R8 at 25F84, carrying R7’s ceiling, not archived r1’s larger ceiling. Preserve the registered envelope calculation, including the special equality rule for 25G83, and audit explicit old-file selection after moving the default. No claim may evade the build check through a continuation or false identity.
   Evidence: `scripts/issue_calibration_acceptance_generation.py:1798–1800,1957–1985`; `joulewise/calibration_bracketing.py:353–363,450–483`; `joulewise/calibration_epoch_continuation.py:194–211,348–364`.

## Residual risk

These are source-based recommendations, not demonstrated implementation results. I did not retrieve or replay R7’s backup-held primary corpus; its recorded provenance says those power bytes are outside the repository. R8 neutrality and the exact release checks remain gates to execute, not facts established by this consult (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:521–523`). No repository files were modified.

R8 should preserve R7’s 17 members and serve the non-claim evidence windows.
Drop the 25G83 interim, but retain its historical evidence and exact-value replay.
Approve and audit the successor before activating it in the closing release.
Absence blocks accepted 25G83 results; H1 still needs controlled claim authorizations.
Settle the successor’s row handling and third-window rule before collecting new data.