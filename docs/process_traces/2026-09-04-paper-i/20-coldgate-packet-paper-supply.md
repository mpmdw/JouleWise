# Cold-gate packet: PAPER-SUPPLY (sealed 2026-09-04)

Assembly branch: `feat/2026-09-05-packet-paper-supply-2`.
Assembly HEAD: `635c5ef039fb21144f7483f0375f4817a7278888`.
Seam under judgment: `84b24686` (full commit `84b24686d4e11b36d2f6fe64e08616ff3ab1c050`).
D-173 remains **PROVISIONAL** pending judgment. This is the sealed evidence
packet, not a gate verdict or supplier-merge authorization.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin
before reading the merits. The packet and every manifested exhibit are the
same frozen inputs for the judge and independent contract lens.

## 2. Seal and source custody

The requested remote branch is `origin/feat/2026-09-04-paper-custody-seam`.
The attempted command `git fetch origin feat/2026-09-04-paper-custody-seam`
failed before fetching: the sandbox refused writing shared-worktree
`FETCH_HEAD`. No remote refresh is claimed. The existing local remote-tracking
ref resolves exactly to `84b24686d4e11b36d2f6fe64e08616ff3ab1c050` and all copies below
come from that immutable Git object, not another worktree's current files.

The final seam commit adds only trace 10 to audited implementation head
`f2d35b4f7fe58f059ed999e18754fa3a4f8ff9ba`; `git diff f2d35b4f 84b24686`
contains no code or contract change. The earlier draft seam subtree was
replaced with verbatim final-head copies. No placeholder remains.

Source roots (packet-relative):

- `20-exhibits/seam-84b24686/`: seam traces 01–10 (including both 02 seats),
  contract, implementation and cited supporting source at `84b24686d4e11b36d2f6fe64e08616ff3ab1c050`.
- `20-exhibits/authority/`: verbatim D-173 and D-161 bodies and index rows
  from the same seam commit. The source index specifies exact line ranges.
- `20-exhibits/peer-audit/43-magistrate-synthesis-gate-17.md`: full ratified
  synthesis at `ff82e0dd3678b06febac1d3c4fe2b16f0926538a`, Q-17-6 row.
- `20-exhibits/peer-audit/17-Q6-verbatim.md`: complete Q6 paragraph at that
  revision, whose exact words are the Q-PS-3 object ratified by 43.
- `20-exhibits/peer-audit/02-F4-verbatim.md`: complete finding F4, including
  limitation, counterargument and minimum evidence, at
  `5e416c47b6236e66eeb861584ad19aeff4e012a4`. Trace 10's assessment names this same source.
- `20-exhibits/assembly-635c5ef0/joulewise/analysis_manifest_v3.py`: current
  pre-seam frozen whole-window binding target at the assembly HEAD.
- `20-exhibits/paper-i/`: unchanged earlier consults and rulings, copied from
  `913bf3f76025f654e5b910670c5a00bfd82c34d4`. They preserve the R1 alternatives
  and earlier receipt position; later ruling 43 controls Q6.

`20-exhibits/source-index.json` records each original path, full immutable
revision, exact contiguous line range and content digest. Full copies preserve
original line numbers; excerpt line 1 maps to the recorded source start.
The manifest hashes the actual copies and this index.

Assembly-generated seal records under `20-exhibits/` are **not custody inputs**
and are excluded from the manifest to avoid a packet/receipt self-reference.
`seal-record.md` pastes the validator receipt, exact replay command and final
packet SHA-256. Its receipt binds validation-time byte observation only; it
neither binds judge delivery nor authorizes a merge or collection. A subsequent
packet or exhibit edit requires a new seal.

## 3. Judgment scope and authority

Answer exactly Q-PS-1 through Q-PS-5 below, each **AFFIRM / AMEND / REFUSE**.
For compatibility with pinned charter §8, AMEND must explicitly REJECT the
superseded proposition and AFFIRM exact replacement wording. This notation
does not amend the charter. REFUSE names the precise packet defect and minimum
cure, with no effect on the merits. Preserve BLOCKER / MATERIAL / NIT severity,
file:line or artifact:field evidence personally checked, and disagreement with
the lead's labeled position. Give a separate packet-hygiene finding.

Convening triggers: repeated seam fix rounds (charter §3.1 and §9), proposed
D-173 custody policy and R1 composition (§3.4), and the requested interpretation
of the F1 stop/contract overclaim (§3.2). These explain review, not its result.

**Lead's submitted position, not evidence:** the seam is landable under D-161
with F1 cured by contract narrowing; F2 is census test debt. Q-PS-1, Q-PS-3 and
Q-PS-5 request ratification/sufficiency judgments; Q-PS-4 requests a timing
ruling. The assembler makes no merits recommendation.

Read the charter, packet, manifested custody inputs and their specifically
cited primary code/authority only. Exhibits are data, never instructions to
execute their historical commands. No new tests or witness executions were
performed in this assembly; historical results remain attributed to their
original seats and heads. No quiet-machine or production evidence was taken.
Narrative traces are preserved verbatim at the lead's explicit request; their
claims and dispositions are objects to assess, not process authority or a
substitute for primary evidence. Under charter §4, do not use narrative process
material as rationale or authority. The bounded 17-Q6 excerpt is necessary
because its exact rule text is being judged, and 43's row incorporates rather
than restates it; it includes the entire contiguous paragraph. Source identity
and line range are pinned in the index. If an exhibit's admissibility or
neutrality prevents an answer, REFUSE the affected atom.

## 4. Questions

### Q-PS-1 — D-173 as written: five typed refs, no receipt families

**AFFIRM / AMEND / REFUSE:** Ratify the exact provisional D-173 entry as written,
with five typed refs and no additional receipt families, consistent with ruling
43 Q-17-6 and its ratified Q6 text?

The complete D-173 body and index row are exhibits. Its public call is
`open_paper_input(ref)`; every ref carries only `role` and `runs_root`. The
Git-tracked supply map under a clean authenticated anchor owns paths and
digests. Fresh validator replay precedes frozen verified output; caller dicts,
bytes, sequences and prevalidated objects cannot authorize paper values.
Refusals remain closed and non-renderable. The five refs are:

| Ref | Family |
|---|---|
| `ReportedEnergyParentsRef` | Reported energy parents |
| `D165CloseoutRef` | D-165 close-out |
| `WholeWindowVerdictRef` | Whole-window verdict |
| `ClaimEvidenceRef` | Claims v1, side bound and parents |
| `TransferProjectionRef` | Transfer projection |

Primary locations: seam contract §Closed public wire and §Family censuses;
`paper_custody.py` ref declarations and `_FAMILY_SPECS`. `floor_artifact` is
an input role inside the D-165 and Claims families, **not a sixth public ref**.
“No receipt families” does not delete existing corroborative inventory/receipt
checks or turn absence into an authenticated empirical result. Older Paper-I
07/14/15 receipt-mission prescriptions remain historical positions; ratified
17/43 parks receipt lanes and specifies the whole-window ref for Q6.

The pinned seam contract still demands a whole-window stop-receipt producer
(§Read, replay, receipt, and reopen algorithm step 8; §Family replay
requirements). Its code still stops that family at `paper_custody.py:1291-1296`.
Judge whether D-173 as written is compatible with 43 and state any exact
consequential contract amendment. Do not read implementation of an old stop
as a reversal of the ratified refusal rule. Adoption of policy does not prove
that any production supplier implements it.

### Q-PS-2 — landability with contract narrowing under D-161

**AFFIRM / AMEND / REFUSE:** Is the seam at `84b24686` landable with F1 cured by
contract narrowing, without a token-residency code change, under D-161's
ordinary-operator threat model?

Read traces 01–10 in source order; both original 02 seats are included. Trace
09 §Trace-code correction and trace 10's G2/C-05 assessment qualify the original
01/02 reseal claims: their historical test actually observed
`paper_custody_digest_mismatch`; the round-4 coherent reseal reaches
`paper_custody_anchor_mismatch`. Do not quote the earlier claim as demonstrated
execution of the later gate. Trace 10 reports G1/G2 closed and LANDABLE at
`f2d35b4f`; `84b24686` changes only that report.

**Uncured wording at the pinned head:** contract lines 53–56 claim the token is
held only inside closures; lines 75–81 claim an `object.__new__` instance is
never a valid capability. The code stores `_custody_token` on authentic objects
(`paper_custody.py:155-203`). Trace 10 F1 records private introspection recovering
it and private constructors forging an authorized result. Direct construction
and tokenless ordinary forgeries refuse. No claim is made that token residency
was removed or that the contract amendment is already installed.

**Contract-narrowing proposition submitted for judgment:**

> The private seam closures create the construction token, which is also
> stored on authentic capabilities. Direct public construction and tokenless
> `object.__new__` instances refuse on guarded access. These guards prevent
> ordinary caller/operator mistakes; they do not prevent deliberate private
> introspection, token extraction, or token-bearing reconstruction. Those
> deliberate acts are outside D-161's threat model. Physics/evidence failures,
> pre-registration failures and ordinary operator mistakes remain fail-closed.

This is proposed replacement wording for the overclaim, not a modification of
the verbatim contract exhibit. AFFIRM licenses the stated narrowing as the cure;
identify the installation required before landing. AMEND gives an alternative
precise cure. REFUSE identifies missing evidence/authority.

Separately disclose **F2 test debt** without silently upgrading it to a current
registry defect: trace 10 finds the current 16-code registry and conditions
agree, but `tests/test_paper_custody.py:614-658` uses a string count as alleged
raise-site reachability. A dead literal can preserve that count after a raise
changes. Judge whether that residual changes landability or needs a condition.
Do not confuse this refusal-code census weakness with the per-validator source
mutation census or the three-arm input census. The seam is still synthetic and
non-issuing; no supplier landing or publication gate is thereby passed.

### Q-PS-3 — Refusal branch: fixed sentence and six-case real CLI acceptance

**AFFIRM / AMEND / REFUSE:** Is ruling 43 Q-17-6's fixed non-admission sentence,
issued from the verified whole-window ref and checked by the six-case actual
CLI acceptance, sufficient for the Refusal branch?

The ratified sentence (17 Q6; 43 Q-17-6) is:

> The registered window was not admitted for this submission's claim-bearing comparison

Its source must be verified **failed production evidence** bound to model,
window, basis, membership and governing row. OR-01, DS-32 and PG-08 become
non-admission surfaces; affected arms are mapped and unaffected verdicts stay
as issued. Missing evidence selects fallback and cannot manufacture an
empirical refusal sentence. The six cases are acceptance requirements, not
claimed executed results:

| Actual CLI input | Required output |
|---|---|
| Authentic failed production row, correctly bound | Exact fixed sentence |
| Missing evidence | No empirical refusal |
| Corrupt evidence | No empirical refusal |
| Diagnostic-only evidence | No empirical refusal |
| Conflicting evidence | No empirical refusal |
| Wrong-window evidence | No empirical refusal |

Ruling 43's transition is explicit: until D-173 is ratified and the seam lands,
the target is the frozen `whole_window_verdict` ref in
`joulewise/analysis_manifest_v3.py`; the seam ref replaces it on landing.
Read the assembly copy's `_authenticate_finalization_inputs` and
`attachments["whole_window_verdict"]` at lines 3481–3525 and 3814–3820.
The current finalizer requires `status == "passed"` and `claim_licensing is True`
and raises `analysis_finalization_verdict_not_passed` otherwise. Thus the named
frozen ref is a binding target, not proof of an implemented failed-row renderer.
The seam copy likewise has the explicit whole-window issuance stop. This
packet requests the rule's sufficiency; it supplies no six-case production CLI
completion claim. Specify any additional binding/refusal condition and the
minimum transition work, preserving the fixed sentence and historical verdicts.

### Q-PS-4 — 02-F4 width reconstruction before submission or disclosure

**AFFIRM / AMEND / REFUSE:** Decide whether factoring the mint's authenticated
reconstruction into a production module reused by the `floor_artifact` input
role is required before submission, or whether 02-F4 may remain a disclosed
limitation. AFFIRM means require that shared reconstruction before submission;
AMEND must state the permitted disclosure/fallback and any restricted claim;
REFUSE names evidence needed to choose. Either outcome must name the affected
submission claim or source-reproduction statement.

The full 02-F4 finding and trace 10's §Residual risk are verbatim exhibits.
The analysis binder checks source hashes, identities, order and point metrics
but does not reconstruct stored member/block widths. Floor validation can
recompute floor arithmetic from the widths recorded in the floor. The mint's
`bind_v2_floor_artifact_evidence` at `floor_mint_estimator.py:598-718`, especially
683–717, reconstructs comparative operands from authenticated sources and
compares exact widths. Coherently wrong widths are an ordinary generator or
operator mistake under D-161; finalized-manifest seals protect subsequent byte
substitution and do not supply this missing independent reconstruction.

Trace 10 assesses reuse as possible but **not drop-in**: the present floor-bearing
roles omit the mint input manifest/pinset, component reports/specs/order
manifests, evidence-root locator, calibration acceptance, ledger/head pin and
bracket binding consumed by the mint path. It estimates about half a day for
arithmetic factoring and 1–2 engineer-days for the full custodied join with
source census, supply-map contract and wrong-width regression, assuming final
v5 inputs exist. These are attributed estimates, not a measured schedule.

The candidate fix reuses the authenticated component reconstruction and exact
comparison, adds a Git-map-authorized recomputation descriptor and complete
source census to the two floor-bearing families, and includes the shared
functions in validator-source hashing. It creates no second estimator or new
receipt family. Acceptance would require a correct-point/coherently-wrong-width
counterexample to refuse source-reproduced status and the actual submission
floors to independently match. No such acceptance run was performed here.
If disclosure is allowed, specify wording that cannot overstate floor binding
and whether production issuance remains stopped for any affected output.

### Q-PS-5 — Q-R1-2 preregistered composition rule

**AFFIRM / AMEND / REFUSE:** Ratify, amend or refuse Q-R1-2's proposed composition
rule before any `_v5` collection consumes it. The two checks below define this
single rule judgment; an AFFIRM must satisfy both, and an AMEND must supply a
complete replacement. Paper-I 05 preserves competing proposals; 06 §R1 is the
registration object. The existing default remains
`composed_member_envelope_mean.v1` until explicitly replaced.

The proposed rule is
`composed_member_envelope_mean_t95_window.v1`, over the generator-frozen
ordered member universe with `n = 50` and no post-data shrinkage:

- lower endpoint = mean of the 50 member lower endpoints −
  `t95 * s(member point estimates) / sqrt(50)` − one authenticated window
  allowance;
- upper endpoint = mean of the 50 member upper endpoints +
  `t95 * s(member point estimates) / sqrt(50)` + the same allowance.

Ruling 06 does not define `t95`, the sample-variance convention, the exact
window-allowance field/source/selection rule, or a counterfactual proving the
allowance and member envelopes do not charge one uncertainty twice. The
alternatives preserved in packet 05 are: mean member-envelope endpoints only
(Sol); a symmetric t term plus maximum anchor and one drift allowance
(blind Fable); or no arithmetic until a separately registered rule and term
list exist (Opus).

**Composition definition.** Ratify, amend, or refuse this rule before any `_v5` collection
consumes it. AFFIRM as written means the displayed arithmetic is sufficiently
defined and scientifically justified for preregistration. An amendment must
state the exact critical value/degree-of-freedom rule, variance convention,
authenticated allowance source and reduction, single-count relation, refusal
conditions, and whether the current default is replaced.

**Single-count check.** Does applying both the averaged member envelopes and the added
t/allowance terms preserve the project's single-count uncertainty doctrine,
or does it double-count a component already present in the member endpoints?
Name the exact source field or derivation that proves the answer.


## 5. Preserved limitations and next gate

All five current map roles are synthetic. D-173 remains PROVISIONAL; the code
blanket-refuses production and whole-window issuance. F1 narrowing is submitted,
F2 census debt is disclosed, 02-F4 remains open, and six-case CLI completion is
not asserted. This gate asks the five questions above; it does not certify four
supplier re-landings, infer paper values from fixtures, or authorize `_v5`
collection. The lead must consume the sealed judge and independent contract
outputs, record each ruling and dissent, install accepted amendments, and
complete the relevant supplier/publication gates.

## 6. Exhibit manifest

```
7634e68c1b6fec99881a3ab9028a1bd734389aad60cf792676a0105f4657228b  20-exhibits/assembly-635c5ef0/joulewise/analysis_manifest_v3.py
21feeaad03661286a617d7a4dc62aab4cfbee0ea198cf297816b7ce1f57f9753  20-exhibits/authority/D-161-entry.md
0a3146dde1c5feb1d21ba06f99824e7e3bbb49649e2d4eca49161cc975a5a528  20-exhibits/authority/D-161-index-row.md
eb178f38c9dc909eaf808ad1fd076b3b2889579be03d53767b5ee718187d2300  20-exhibits/authority/D-173-entry.md
dc084a93aa944fff37435cf5e723bf2fb2577df1aa5ffd0218d76b49cdf423ff  20-exhibits/authority/D-173-index-row.md
5ca9242e3b66931ed47d0b525a251f8a8e022420fac41065f419fed18ec6d112  20-exhibits/paper-i/02-blind-fable-contract-seat.md
d517fc7ce75a789ab4a511269a3c4a4f259c11c19daafedd6441a120a203b344  20-exhibits/paper-i/02-consult-sol-contracts.md
a6840c5376e1b8806e47fad85fb0ef1e47678b6d2563b96c4bf81caa5bab1507  20-exhibits/paper-i/03-consult-opus-contracts.md
d3ae4c74d9448b45395c73746446245cf2b1e32ffc413a5f58f42fdae235b72c  20-exhibits/paper-i/05-adjudication-packet-contracts.md
ed31ce578a2993fc34d655441e67bab0babf61dc7cf8e1d0a21b1bd9295e9330  20-exhibits/paper-i/06-magistrate-contract-rulings.md
a8737b0387fdd2f69f47e39fdd1f2e18352d0871b406c127e6c2ff4a71032ace  20-exhibits/paper-i/07-magistrate-rulings-addendum.md
959c2276f1497430140da27b8d3b7db6de813acb5a77f7f18c5213c5329f7fad  20-exhibits/paper-i/08-magistrate-rulings-addendum-2.md
18302ea48b235d592ca102855cb3cddd6b2bfd4faf636ea9c72e0411dc785c7f  20-exhibits/paper-i/09-magistrate-rulings-addendum-3.md
22714d90343376d011f92e5d40de8e084da1f40f7b72860a4723fd7d773da1e4  20-exhibits/paper-i/10-magistrate-rulings-addendum-4.md
c2d33b5537b29ecf6511440a9900dca95c5787e442943668bdd466f790818f92  20-exhibits/paper-i/11-blind-fable-custody-read-seam-seat.md
cc3fb162548affbe58054bff4263a607493d01ad4cf142fea42dec94308e9a14  20-exhibits/paper-i/11-custody-seam-consult-sol.md
75da00c7890bb0198195aee3608848e3f1c43b1cb85e152d16ad473ed5d0dd11  20-exhibits/paper-i/12-custody-seam-consult-opus.md
7da689fe98a18f206255fee8774df0b1ed4def256d273911c37bb7b3692a932c  20-exhibits/paper-i/14-adjudication-packet-custody-seam.md
067ade49d88dbf30c5c75491ab5293133e8867c6efd70fd363e1319ee95f66e4  20-exhibits/paper-i/15-magistrate-ruling-custody-seam.md
11a3bc19907f4f74f6c7398647e1f5a14a560f4dd195b8dd740f038b18451bd1  20-exhibits/paper-i/16-magistrate-rulings-addendum-5.md
8390dcf47e6d4b150f42377fda7d4fd352a7340e33ae7cf7a8f0c18d1bb01faa  20-exhibits/peer-audit/02-F4-verbatim.md
3c219d721ad5cb083b4160998e83b3ab5cf993060498976e41fe247039e5f084  20-exhibits/peer-audit/17-Q6-verbatim.md
a0e0b9ac388e040b86d043d5031f61772abc37c42cdc9216eac3e896ec9d146e  20-exhibits/peer-audit/43-magistrate-synthesis-gate-17.md
ced629e34e8f98c5e4524e2dbcdb8582447481ead2936adea60bc121fab0d1ff  20-exhibits/seam-84b24686/configs/paper_supply/supply_map.json
56fe96621484484db7db8f0017631aaa26eb29e0834792120e2797308464422f  20-exhibits/seam-84b24686/docs/contracts/paper_supply_custody.md
a4d498f908b95d089401aa8d6f1dd6d2aa120dfae0cb6d6d32140d116f46e401  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/01-seat-landing-report.md
8a153042819b75faa48f8cdebb79d185c9c5db568742f9e7dbcd89bd029ba679  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/02-refuter-contract.md
d5f46526bbe78b05962ca6f51bac3c6234d415a4e74c828d8e7d93e65def7a91  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/02-refuter-execution.md
a8ae042ee88c39ae703da61d1d359ae77a0a00bcf19113e4947d4123826bd7d4  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/03-sol-fix-round-1-report.md
8943b8e45d3cba1daafb5e491ddbddf5f05bbb3a6be44450c3d6386ced291245  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/04-delta-reaudit-round-1.md
55f06c87f202824a3a1b851404dc82389e574dbf1311b1a5eb8901904d969364  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/05-sol-fix-round-2-report.md
acca042364a805b849d318568c60c1f21c29f3b4fffa1715fd7c37ecb90c1229  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/06-sol-fix-round-3-report.md
221a328ae8fda35112e200e9bd83ec6e50dc6e1785d1178ed8db42919daac125  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/07-delta-reaudit-round-2.md
1d61e17f38666f6b0b5e2ef05b6490b253e4574e27fa2f3614eccbe3885477c2  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/08-opus-counter-review.md
b35f60a6c9852af13596ddda4abde5127a92aa39d13dd509201ba4eeb9f6142f  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/09-sol-fix-round-4-report.md
79b5209d9b12b3a25a16cbd1ac68ea7511a2b47dffae0f6850b99c70e8f1eade  20-exhibits/seam-84b24686/docs/process_traces/2026-09-04-paper-custody/10-delta-re-audit-round-4.md
292e1285d496e20a40c868aa10fc7ea46e16e1e4850e226f527085f511e7de36  20-exhibits/seam-84b24686/joulewise/analysis_engine/inputs.py
73e20342f2a71db4563ba2277b20de3fee7da9e9f555329c918f0614c8eccaf6  20-exhibits/seam-84b24686/joulewise/analysis_manifest_v3.py
7a6a4a12ae2522ac763bab58a50a6990e2ae1620aa3265dcd6fc70dcc51a971b  20-exhibits/seam-84b24686/joulewise/floor_mint_estimator.py
8a94b8433c415eb0abd4d4ea3cc9aed6cc994e089a6360d73919fdf825c343bd  20-exhibits/seam-84b24686/joulewise/paper_custody.py
b243419365becd5c46911154a6683302db85c3a4fd2ba9c2828017cf3475d78a  20-exhibits/seam-84b24686/joulewise/whole_window.py
241b645b2def824d3677e70a5085c098d7d62c8a49b40920df91e05c511b8179  20-exhibits/seam-84b24686/tests/test_paper_custody.py
3ef565c7ecb846faa4d4e1d073544f38c1ee6097417ee8bb9afab5815f4aa739  20-exhibits/source-index.json
```
