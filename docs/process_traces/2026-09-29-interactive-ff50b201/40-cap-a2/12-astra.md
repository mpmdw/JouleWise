```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use a verified 17-member R8 for derivation windows, drop the 25G83 interim, and activate the successor only through an audited closing release.",
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
      {"id":"F1","severity":"blocker","question":1,"title":"R8 must preserve R7's 17 members; scientific neutrality requires proof and a limited meaning"},
      {"id":"F2","severity":"blocker","question":2,"title":"A1 expressly forbids the needed sequence"},
      {"id":"F3","severity":"blocker","question":4,"title":"Early successor registration recreates the hold problem and conflicts with the closing sequence"},
      {"id":"F4","severity":"should_fix","question":3,"title":"The 25G83 interim can be removed while retaining its useful verification"},
      {"id":"F5","severity":"should_fix","question":5,"title":"Preparation and promotion require distinct, successor-specific authority"},
      {"id":"F6","severity":"should_fix","question":6,"title":"Preserve selection, clock, lineage, and audit safeguards after resequencing"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD && git -C /Users/edr/code/JouleWise rev-parse origin/main",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","9eab16f81783c9cf079474c38d10c4a5bdf0f118","9eab16f81783c9cf079474c38d10c4a5bdf0f118"]},
      "expected":{"exit_code":0,"tail_regex":"9eab16f81783c9cf079474c38d10c4a5bdf0f118"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"python3 -B - <<'PY'\nimport hashlib, json, subprocess\nrepo = '/Users/edr/code/JouleWise'\ndef blob(path):\n    return subprocess.check_output(['git', '-C', repo, 'show', 'origin/main:' + path])\na = json.loads(blob('configs/calibration/calibration_acceptance_d079_v2_n17_r7.json'))\nprint('R7_BUILD=' + a['identity_epoch']['os_build'])\nprint('R7_MEMBERS=' + str(len(a['derivation_corpus']['members'])))\nprint('R7_PINS_MATCH_MAIN=' + str(all(hashlib.sha256(blob(p)).hexdigest() == h for p, h in a['prospective_rederivation']['estimator_code_sha256'].items())))\nPY",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["R7_BUILD=25F84","R7_MEMBERS=17","R7_PINS_MATCH_MAIN=True"]},
      "expected":{"exit_code":0,"tail_regex":"R7_BUILD=25F84\\nR7_MEMBERS=17\\nR7_PINS_MATCH_MAIN=True"}
    }
  ],
  "flags": [
    {
      "id":"R1",
      "kind":"lead_ruling",
      "level":"blocking",
      "text":"These are proposed amendments, not enacted authority. A1 currently forbids R8 substitution and requires the successor in force before closure.",
      "needs":"The cold judge must amend the sequence, membership text, closing conditions, and audit-release boundary before implementation."
    }
  ]
}
```

CONSULT ANSWER: astra

## Findings

Terminology: a **capture** is one power-sampler recording; a **member** is a capture included in a calibration’s calculation. **B** is a capture’s timing-uncertainty value. The **estimator** computes B; its **cell cap** limits the search work it may perform. A **digest** identifies exact file bytes; **code pins** are the estimator digests recorded in a calibration. An **epoch** is the instrument’s operating identity, including its operating-system build. The **default** is the calibration loaded when none is explicitly selected. **Registration in code** gives calibration bytes production authority; this differs from **preregistration**, which fixes experimental rules before observations. **H1** forbids claim-bearing windows—runs intended to produce reported results—at 25G83 until the cap ruling closes. **R8** below is a proposed new 25F84 generation; the **successor** is the future calibration from fresh 25G83 captures.

Evidence shorthand, with line numbers referring to the files actually read:

- `CAP` = records root supplied in the charge, `20-cap-council/21-coldgate-fable-ruling.md`.
- `A1` = that root, `20-cap-council/31-addendum-ruling.md`.
- `HOLD` = that root, `12-hold-consult/21-coldgate-fable-ruling.md`.
- `BRIEF` = that root, `12-hold-consult/40-owner-brief-2026-09-29.md`.
- `CLOCK` = that root, `40-sci-a2-network-time/31-addendum-ruling.md`.
- Code citations refer to `origin/main` at `9eab16f8`, except `promote_calibration_candidate.py`, read at `b953f4b0`.
- I read the supplied `30-r1-need/10-sonnet-r1-need-report.md` in full. Its conclusions were checked against the sources below.

**F1 — Question 1: use R8, with a corrected membership count and a bounded neutrality claim.**

**Answer.** Yes: R7 until the cap transaction, then a verified R7→R8 re-issue at 25F84 in that transaction. **R7 has 17 members, not 12.** The 12 belong to the 25G83 candidate. Main registers seven historical generations; R7 is the active default.

**Deciding reason.** The derivation route requires both current code pins and an epoch the default does not already judge. Unchanged R7 fails the first requirement after the cap change; a 25G83 default fails the second.

“Scientifically neutral” can mean that R8 preserves R7’s 17-member calculation and every numerical limit. It cannot mean that raising the cap preserves the population admitted by future captures. Changing that population is the reason fresh 25G83 calibration is needed.

R8 must carry:

- R7’s exact 17 members, their content identities and evidence hashes, decimal values, statistics, comparison limits, epoch and historical selection record.
- A new identifier, R7’s immutable predecessor reference, final estimator pins, regenerated internal seals, and an externally reviewed digest of the issued bytes.
- A clear account of what changed: code pins and issuance metadata; the historical members were selected under 165,000 cells. Preserve the old budget ruling as history and identify the new operative ruling and cap separately.
- The statement that R8 enables derivation work at 25G83 without calibrating that epoch. It must acquire no extension authorizing 25G83.

Admissibility requires authentication of the primary evidence and replay of all 17 members under the final estimator, with identical B values and independently reconstructed limits. Compare the relevant retained nonmembers too: newly resolving captures must be disclosed, not silently added. Keep the separate 12-member/24-capture 25G83 comparison required by A1 step 7. A changed member value defeats the pin-only route.

Verify that the new default loads, the code pins match, derivation input creation recognizes the 25G83 epoch mismatch, ordinary 25G83 calibration remains refused, and explicit historical calibration references remain authenticated. Update required consumers of the new identifier through review; changing the default pointer alone is insufficient.

I see no better bounded route. Separating derivation authorization from calibration would be cleaner architecture, but it is a new design with more behavior to prove. Skipping the code-pin check is not an admissible shortcut. Also, unchanged old numbers do not independently validate new prospective 25F84 claims under the enlarged cap: A1 overruled the old admission purpose specifically for 25G83.

**Evidence.** `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20–48,494–532`; `joulewise/calibration_bracketing.py:147–199`; `scripts/validate_powermetrics_fiducial.py:397–402,2081–2099`; `scripts/write_derivation_night_inputs.py:146–187`; `A1:100–110,199`; `scripts/floor_mint_pinsets/schema_v2.json:186–192`. V2 independently confirmed 17 members, build 25F84, and current pins.

**F2 — Question 2: replace A1 step 1 and S6 explicitly.**

**Answer.** I would issue these exact replacements.

**A1 §5, step 1:**

> **Complete D-138 option (a).** Land the disposition-registry loader repair, the promotion tool and their required verification. Do not register the 25G83 r1 calibration or land the withdrawn build-keyed hold. Preserve the candidate, issuance records and evidence unchanged. R7 remains the default until the cap transaction. That transaction shall include an authenticated re-issue of R7 at 25F84, provisionally called R8, preserving all 17 members and all numerical limits, with pins for the final estimator and the verification required by this addendum. A failure to prove that preservation stops the transaction for council review. The cap transaction does not wait for r1 registration. No calibration or epoch extension authorizing 25G83 enters production before the closing release specified in revised step 16.

**A1 §7, row S6:**

> **S6 — r1 is not registered under owner option (a). Adopted.** The former dependency on r1 issuance and the prohibition on re-pinning another epoch are withdrawn. A verified R7→R8 re-issue at 25F84 is authorized solely as the cap transaction’s calibration re-issue and derivation-window default. It does not authorize 25G83 claims. If R8 verification fails, or the historical 25G83 evidence loses scientific admissibility, stop for council review; do not substitute another calibration or member set without a ruling. No 25G83 interim re-issue is required.

**Deciding reason.** The existing words expressly prohibit the necessary R8 substitution. A new workflow note cannot override them.

These replacements also require the consequential amendments in F3 and F4; issuing only these two paragraphs would leave the plan contradictory.

**Evidence.** `A1:193–208,229`; `HOLD:303,328`; `BRIEF:39,45–47,53`.

**F3 — Question 4: defer production registration until an audited closing release.**

**Answer.** Choose resequencing. Keep every 25G83 calibration and every extension into 25G83 outside production authority while H1 stands. Prepare the successor and review its exact bytes before release. Do not revive the failed hold implementation as an incidental cap dependency.

**Deciding reason.** No scientific step identified here needs early production authority. Three failed rounds make another distributed hold a costly dependency with no demonstrated benefit to this sequence.

Required sequence amendments:

- **Step 9:** merge the cap with verified R8 as default; no 25G83 interim or registration.
- **Step 12:** derive the fresh successor, complete its science review, and prepare exact issuance bytes and the complete proposed registration change. Keep them inactive in production.
- **Steps 13–15:** audit the complete proposed release at its final commit, including registration, default movement, historical explicit selection, and all claim-producing code. Auditors independently derive the successor from raw evidence. Fixes retain A1’s restart obligations.
- **C4 replacement:** “The successor calibration is derived from the fresh captures, independently verified, and fixed by exact issued-byte digest and proposed release commit; production activation remains conditional on step 16.”
- **Step 16 replacement:** “The closing ruling verifies C1–C9 as amended and authorizes activation of the exact audited release. H1 lifts only upon verified activation of that release and its named successor; failed or partial activation leaves H1 in force. No claim-bearing window is authorized before that verification.”

There is an important boundary to state honestly: an isolated audit checkout can contain the proposed registration so reviewers can test the actual release. That checkout must not be an authorized measurement environment. “No registration” here means **no production activation**, not a prohibition on constructing the code reviewers must inspect. A requirement forbidding registration even in an isolated test checkout would conflict with testing the final release and would need a different audit contract.

Preserve the audit’s exact-commit requirement: promote the audited commit unchanged. Record the closing authorization separately so adding it does not silently create a different, unaudited measurement commit. If integration changes that commit, finish the required review at the actual final commit before activation.

**Absence is a narrower protection than the owner brief suggests.** It makes authentic 25G83 calibration unavailable and causes truthful 25G83 bracket evaluation to return stale. It does not itself prove that no manually invoked campaign can start a child process. Main’s campaign preflight explicitly returns without launch authentication for configurations lacking its launch marker. Keep the prohibition on claim authorization and verify the actual admission path; do not describe this as a comprehensive build-keyed code hold.

If early production registration is later demanded, this recommendation no longer supplies H1 protection. A separately authorized hold design must then pass before registration. The three failures justify changing the design and test boundary, not claiming that a universal hold is impossible.

**Evidence.** `A1:201–216,238–250`; `HOLD:281–305`; `BRIEF:15–29`; `joulewise/calibration_bracketing.py:1171–1183,1246–1257,2119–2124,2179–2182`; `scripts/run_campaign.py:1866–1881,8090–8094`; `joulewise/arm_readiness.py:10110–10132`.

**F4 — Question 3: drop the 25G83 interim, retain its comparison evidence.**

**Answer.** Use R8 for the windows, then the fresh successor only. Keep the historical candidate and its evidence available for scientific comparison.

**Deciding reason.** The interim’s stated operational job was to provide current estimator pins for new windows. R8 performs that job in the epoch the derivation route requires; the interim cannot.

The interim also documented numerical continuity across the cap change. Preserve that useful job as a signed-off replay record: all 12 existing member values unchanged, all 24 historical dispositions compared, and the eight original cap exclusions explicitly identified. Issuing another production-authorized file adds no independent scientific evidence.

Nothing scientific is lost if those records and the network-time comparison survive. What disappears is an administrative calibration generation that was never intended to support claims.

Amend `CAP` §5 item 2 and `A1:257` accordingly. Also amend S5’s description of the old 12 as “members of the predecessor”: under this sequence the successor’s computational predecessor is R8, with 17 members. Call the 12 **“members of the retained historical 25G83 candidate, selected under the 165,000-cell cap.”** Preserve their valid historical ledger status; exclude them from the fresh successor by a preregistered, content-identified disposition, not by relabeling them diagnostics.

**Evidence.** `CAP:175–179`; `A1:199–204,228,257`; `HOLD:328`; `scripts/issue_calibration_acceptance_generation.py:1795–1800,1980–1985`; `CLOCK:199`.

**F5 — Question 5: use successor preparation followed by narrowly generalized promotion.**

**Answer.** For the eventual 25G83 file, use `issue_calibration_acceptance_generation.py` to derive the fresh candidate, with the reviewed successor preregistration and historical-row handling. Then generalize `promote_calibration_candidate.py` to consume a separately reviewed issuance specification identifying that exact candidate.

Use `reissue_calibration_acceptance.py` as a starting point for R8 preparation, subject to compatibility checks and independent primary-data replay. Do not use it to manufacture a fresh 25G83 successor.

**Deciding reason.** These tools perform different operations. The re-issue script copies an authenticated predecessor’s member set and updates pins; it explicitly produces an unissued candidate. The promotion script changes issuance status without deriving a new corpus.

The generalized promotion operation should require the approved candidate digest, derivation-input digest, identifier, epoch, predecessor, applicable ruling references and issuance text. Preserve the scientific fields exactly, authenticate cited records, produce deterministic bytes, refuse conflicting overwrites, and support exact-output checking. It must neither choose the scientific authority itself nor install registry entries automatically.

Do not merely replace `dbad7cc7` and r1 constants. The current tool also hard-codes old ruling identifiers, disclosure requirements, network-time provenance and hold language. The successor needs its own reviewed content, including accurate H1 closure status; retaining a sentence saying H1 withholds authorization after release would be false.

R8 preparation is not proof of numerical neutrality: the re-issue helper authenticates stored evidence values and copies them. Separate replay under the changed estimator remains necessary. Give R8 its own reviewed issuance step; the current promotion script is specialized for the 25G83 candidate’s structure.

**Evidence.** `scripts/reissue_calibration_acceptance.py:2–8,127–238,249–288,577–602`; `scripts/issue_calibration_acceptance_generation.py:1795–1800,1957–1959,1980–1985,2234–2239`; `scripts/promote_calibration_candidate.py@b953f4b0:22–43,90–153,156–207,210–230`.

**F6 — Question 6: preserve these conditions to avoid false numbers or false descriptions.**

**Answer.** The amendments remove unnecessary issuance, not the scientific safeguards. These remain necessary:

- **Do not transplant the 12-member calibration into R8.** R8 preserves R7’s 17-member arithmetic. The fresh successor inherits its predecessor calculation from active R8, not from historical r1; the resulting ceiling still depends on the fresh data and registered formula.
- **Do not confuse sizing with validation.** Historical roster replay sets the cap; the later minimum of 24 captures tests the shipped cap. Neither a copied code pin nor an unchanged historical B establishes that prospective selection is unchanged.
- **Do not select survivors for publication.** Keep every attempted bracket visible. Apply the prescribed whole-window holds for stops and frame-range failures; do not publish an aggregate formed by quietly dropping the difficult captures.
- **Keep the new-data ordering intact.** Commit the complete cap-acceptance result before reading any B from those windows. The network-time comparison uses first-OFF-window data but must defer its B analysis until that cap result is committed. No B-based extra captures, exclusions, or reuse of a failed cap campaign as a successor corpus.
- **Keep clock-state evidence and historical disclosure.** The successor uses attested network time OFF; retain the historical ON-state comparison required by H7. Do not pool ON and OFF members without a rule sealed beforehand. An empty system log is not proof of no corrections.
- **Resolve the copied clock-rule discrepancy explicitly.** A1’s S2 text says 300 seconds, while the clock addendum’s replacement H6 specifies 180 seconds and a log-retention witness. Amend the cap text to cite that final H6 definition rather than leave two competing membership rules.
- **Do not overstate coverage.** Twenty-four successful captures are a commissioning minimum, not proof of a negligible failure probability. The 100–150 ms frame range includes unmeasured regions; the reserve and continuing tripwire protect those regions.
- **Audit the release that actually produces results.** A later estimator change, silent default change, or unreviewed registration amendment invalidates the claimed match between evidence, calibration and reported numbers.

**Deciding reason.** The largest remaining danger is a correct-looking number derived from a differently selected population, clock state, calibration lineage or executable than the record claims.

**Evidence.** `scripts/issue_calibration_acceptance_generation.py:1957–1977`; `CAP:171,175–179`; `A1:151–181,202–216,225,240–248`; `CLOCK:152,174–181,199`; `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:484–491`.

## Residual risk

This was an independent read-only consultation. I read no other seat’s answer, performed no hardware measurement or corpus replay, ran no test suite, and changed no files. The proposed R8, generalized promotion tool and release procedure do not yet exist as verified implementations. The historical hold failures are supported here by the named ruling and owner brief, not by newly executed bypass probes.

Use R8 at 25F84, preserving R7’s 17 members and proving their numbers unchanged.  
Remove the 25G83 interim, but keep its historical replay and network-time comparison.  
Keep 25G83 authority out of production until the audited closing release activates.  
Prepare the fresh successor from registered captures and promote only its reviewed exact bytes.  
Preserve selection, clock, lineage and final-commit checks before reporting any claim.