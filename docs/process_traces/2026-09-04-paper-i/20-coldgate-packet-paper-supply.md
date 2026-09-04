# Cold-gate packet: PAPER-SUPPLY (2026-09-04)

Assembled on `feat/2026-09-04-packet-paper-supply` from the PAPER-I rulings
revision `913bf3f76025f654e5b910670c5a00bfd82c34d4`. The seats receive this
packet, every exhibit in the manifest, the charter, and read-only access to
the specifically cited decision, contract, and code locations. This packet
asks atomic questions and offers no recommended verdict. The magistrate's
earlier dispositions are identified as positions, not evidence on the merits.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Assembly pins and seal-time replacement

The seam branch to be judged is
`origin/feat/2026-09-04-paper-custody-seam`. Its final head is
`<<SEAM-HEAD>>`.

The seam exhibits in this draft are labelled **DRAFT-HEAD** and were copied
from the locally agreeing branch and remote-tracking refs at
`2e3349e1f412349638c578b56a9927824fc4713d`. The assembly runner could not
network-refresh the ref because DNS access to GitHub was unavailable. The
DRAFT-HEAD contract has SHA-256
`523230f733d54981ae92dc826b01e2052c6c77be652e5c17c0149b6c8cd53bcb`;
the DRAFT-HEAD `joulewise/paper_custody.py` has SHA-256
`41d4b2129bfb387cd2797a7080dc4f0d7d6cf8ba476ad74b49ba7a4b52a43f5b`.
These labels identify draft custody only and make no final-head claim.

Before sealing, the magistrate must fetch the seam branch, replace every
DRAFT-HEAD seam exhibit with a verbatim copy from `<<SEAM-HEAD>>`, replace
every occurrence of the placeholder with that one full commit, regenerate
the exhibit manifest, and recompute the packet digest. A validator PASS on
this draft does not perform that replacement and does not authorize a
supplier merge, paper fill, or `_v5` collection.

## 3. Convening triggers (charter §3)

- §3 item 1 and charter §9: the provisional D-173 record and rulings 15/16
  say three supplier lanes each reached three occurrences of one
  caller-authority signature. Q-SIG asks the judge to verify both the count
  and the structural classification.
- §3 item 4: `composed_member_envelope_mean_t95_window.v1` is a proposed
  claim-bearing statistical composition rule. It must be ruled before any
  `_v5` collection consumes it.
- §3 item 4: Q-PROC presents a proposed extension of D-172's
  real-entry-point testing rule. It is not adopted.
- §3 items 3 and 4: D-173 is provisional and must be ruled before any paper
  supplier merges through the new shared trust boundary.

## 4. Objects and controlling locations

1. **D-173.** At `<<SEAM-HEAD>>`, read the exact D-173 index row and body in
   `docs/decision_log.md` and the normative
   `docs/contracts/paper_supply_custody.md`. The DRAFT-HEAD contract and
   implementation are copied in the seam exhibit subtree. Rulings 15 and 16
   record the magistrate's provisional adoption and amendments.
2. **R1 interval proposal.** PAPER-I ruling 06 §R1 registers the proposed
   rule ID and leaves `composed_member_envelope_mean.v1` as the current
   default. Consult packet 05 §R1 records the three competing constructions.
3. **R2 sidecar.** Ruling 06 initially selected a v2 sibling. Addendum 07
   replaced it with production `joulewise.claim_verdicts.v1` plus a
   separately content-addressed `joulewise.claim_side_bound.v1` sidecar.
   At PAPER-I revision `913bf3f7`, `docs/contracts/claims_ladder.md:21-30`
   and `docs/process/v5-artifact-flow.md:23-24,32` name v1 as the registered
   production claim artifact and do not yet name the sidecar as a flow edge.
4. **R4 map and receipts.** Addendum 09 requires a total map from the D-165
   producer's closed reason-code enumeration to professor-facing OR-01
   sentences. Addendum 07 names two follow-on receipt missions. At
   `<<SEAM-HEAD>>`, inspect `joulewise/dominance_closeout.py` for
   `D165_CLOSEOUT_REFUSAL_ENUMERATION`, `D165_CLOSEOUT_REFUSAL_CODES`, and
   `D165_OR01_REASON_SENTENCES`, and inspect the custody contract's family
   replay requirements.
5. **D-172.** At `<<SEAM-HEAD>>`, read `docs/decision_log.md` §D-172. Its
   adopted scope is the watchdog, installer, launchd templates, and session
   argv. It does not presently bind paper suppliers.

## 5. Questions (answer each atomically)

Use the charter verdicts AFFIRM, REJECT, or REFUSE for every numbered atom.
When an amendment is necessary, REJECT the superseded wording and state the
exact replacement wording being AFFIRMED. Every REFUSE must name the packet
defect and minimum cure.

### Q-D173 — ratification of the shared custody boundary

**Q-D173-1.** Should the exact provisional D-173 entry at `<<SEAM-HEAD>>` be
ratified as adopted before any D-123, gamma, transfer, or D-165 paper supplier
merges? Grade its core rule: caller supplies only a closed role name and runs
root; a clean-Git-anchored tracked supply map owns paths and expected digests;
fresh validator replay produces frozen verified objects; receipts corroborate
but never authorize; caller paths, digests, bytes, mappings, sequences, and
prevalidated objects cannot enter; refusals stay in the closed non-renderable
`paper_custody_*` namespace.

**Q-D173-2.** Does the normative
`docs/contracts/paper_supply_custody.md` at `<<SEAM-HEAD>>` completely and
unambiguously install D-173 without contradicting the registered claim,
floor, whole-window, transfer, authentication, or paper-rendering contracts?
If not, cite each conflicting clause and give the minimum amendment.

**Q-D173-3.** Does `joulewise/paper_custody.py` at `<<SEAM-HEAD>>` conform to
that decision and contract at the public wire, authority root, map lookup,
validator census, replay/receipt comparison, reopen boundary, lower-boundary
closures, refusal translation, and non-issuing fixture fence? This is an
implementation-conformance atom, not a presumption that policy ratification
requires accepting the current implementation.

### Q-R1-2 — preregistered composed interval

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

**Q-R1-2-1.** Ratify, amend, or refuse this rule before any `_v5` collection
consumes it. AFFIRM as written means the displayed arithmetic is sufficiently
defined and scientifically justified for preregistration. An amendment must
state the exact critical value/degree-of-freedom rule, variance convention,
authenticated allowance source and reduction, single-count relation, refusal
conditions, and whether the current default is replaced.

**Q-R1-2-2.** Does applying both the averaged member envelopes and the added
t/allowance terms preserve the project's single-count uncertainty doctrine,
or does it double-count a component already present in the member endpoints?
Name the exact source field or derivation that proves the answer.

### Q-R2 — claim-side-bound sidecar versus the registered ladder and flow

The amended design keeps `joulewise.claim_verdicts.v1` unchanged and adds
`joulewise.claim_side_bound.v1`. The sidecar is content-addressed, joins to the
v1 artifact through `claim_verdicts_sha256`, and carries the separately typed
`claim_side_bound` whose value is the named
`E_clock_anchor_shift_bound_j` contrast term, never
`deterministic_bounds.total` or the complete decision-interval half-width.
The gamma renderer reads v1 plus the sidecar and refuses every digest or
identity mismatch. D-173 places both inside one verified Claims family.

**Q-R2-1.** Should that v1-plus-sidecar design be ratified, rejected in favor
of a versioned `claim_verdicts.v2` successor, or refused pending a more
complete wire? Grade value identity, content identity, join direction,
single-count semantics, null/refusal behavior, and whether the sidecar can
ever become a gate rather than disclosure/sizing input.

**Q-R2-2.** If the sidecar design is affirmed, do the present
`claims_ladder.md` and `v5-artifact-flow.md` contracts already permit it, or
must both be amended before implementation or collection? State the exact
flow position, producer, consumer, and failure edge that must be registered;
do not silently reinterpret their existing v1-only language.

### Q-R4 — D-165 reason map and the two receipt missions

The proposed D-165 rule has one producer-owned refusal enumeration, an exactly
key-equal professor-sentence map, an enumeration test that fails on additions
or removals on either side, no rendering of exception/free text, and
STOP_FILL/structured refusal on an unknown code. Addendum 07 records these two
follow-on missions as queued in its ruling prose:

- `WHOLE-WINDOW-STOP-RECEIPT-01`: a typed validator must distinguish an
  authentic admission failure from provenance/structure failure, after which
  a governed producer issues the receipt. Until both exist, the whole-window
  stop path cannot issue paper prose.
- `CLAIM-NONISSUANCE-RECEIPT-01`: a missing claim-verdict artifact is
  non-issuance, not an authenticated outcome. The registered “required
  verdict absent” sentence cannot issue until a governed non-issuance artifact
  exists.

**Q-R4-1.** Ratify, amend, or refuse the total D-165 reason-code-to-sentence
map rule. Inspect the actual enumeration and map at `<<SEAM-HEAD>>`; identify
any producer-emittable code without exactly one safe sentence, any sentence
without a producer code, or any internal diagnostic that can leak into prose.

**Q-R4-2.** Ratify, amend, or refuse the whole-window receipt mission and its
blocking rule. Is a typed authenticity/admission result plus a governed,
independently anchored receipt both necessary and sufficient, or does the
proposal omit an authority or replay relation?

**Q-R4-3.** Ratify, amend, or refuse the claim-nonissuance receipt mission.
Can absence ever authorize the registered sentence without a positive
governed non-issuance artifact? If yes, state the non-self-authenticating proof
and exact failure semantics.

### Q-SIG — repeated signature and the shared-seam response

The provisional D-173 body and ruling 15 record three occurrences in each of
three lanes:

| Lane | Recorded recurring signature |
|---|---|
| D-123 reported means | A caller-supplied projection or embedded document is sealed beside its own digest instead of being derived from independently authenticated parent bytes. |
| Gamma claim renderer | Claim/floor values and their copied identities can be re-content-addressed together without an independently anchored source-cell authorization. |
| D-165 outcome renderer | Caller-selected paths/digests and a caller-constructible PASS receipt can authenticate caller-authored reasons or values. |

The consult seats 11/11-blind/12 and packet 14 argue that these are one trust
boundary defect, and rulings 15/16 choose one shared seam rather than another
same-shape per-lane fix or parking the suppliers.

**Q-SIG-1.** Do the exhibits establish three same-signature occurrences in
each named lane, rather than three merely similar symptoms? For each lane,
cite the three occurrences and the invariant authority defect. If the packet
lacks the underlying evidence for any count, REFUSE that lane and name the
missing exhibit.

**Q-SIG-2.** Given only the verified count and signature, was building the
shared seam the correct structural response rather than parking the affected
suppliers or attempting another per-lane repair? Grade whether the seam is the
smallest shared abstraction, whether it introduces an avoidable second trust
system, and whether its non-issuing fence prevents construction work from
silently licensing paper values.

### Q-PROC — proposed extension of D-172

D-172 arose from a watchdog that stayed unit-green while its real production
entry point was broken. The proposed extension, presented here and **not
adopted**, is:

> Any change to `joulewise/paper_custody.py`, the Git-tracked paper supply
> map, or a paper supplier/renderer production entry point must ship with a
> green test that runs the real paper supplier/renderer entry point as a
> subprocess, exercising real argv parsing where a CLI exists, role lookup,
> supply-map load, authentication-session construction, validator replay, and
> structured-refusal-to-exit behavior; at most the repository/runs-root
> location and unavoidable operating-system seams may be redirected to an
> isolated fixture. It must also carry at least one named mutation of the
> changed lines shown RED under that test. A unit test that directly
> constructs a verified result or injects readers or validators does not
> satisfy the rule.

**Q-PROC-1.** Should D-172's real-entry-point rule be extended to paper
suppliers using that text? Grade applicability, whether “real entry point” is
well-defined for library-only suppliers, whether the allowed fixture seams
make the test feasible without making the clean-tree anchor self-authenticating,
and whether D-173's auto-census mutation test already covers the same failure
class. If amending, give exact scope, allowed seams, RED mutation obligation,
drop/review trigger, and enforcement home.

### Q-HYGIENE — packet completeness and neutrality

**Q-HYGIENE-1.** Is this packet complete and neutrally assembled for every
question? Name any omitted contrary/supporting evidence, stale DRAFT-HEAD
claim, unsupported “queued” status, compound atom, leading formulation, or
authority conflict and identify every affected question.

## 6. Facts and tensions the ruling must preserve

- No exhibit issues a measurement value, paper fill, claim, or launch
  authorization. The seam contract's current roles are synthetic and
  non-issuing.
- Ruling 06 made `composed_member_envelope_mean.v1` the default; the t95/window
  rule remains a proposal until this gate rules it.
- Addendum 07 reversed ruling 06's in-place production-v2 direction after the
  seat found the registered v1 ladder/flow conflict. Ratifying the sidecar
  cannot be treated as if those registered contracts already named it.
- Addenda 07 and 09 use “queued” mission language; this packet proves the
  proposed mission semantics, not current state-kernel registration. Do not
  use queue presence or absence as evidence on the design merits.
- Ruling 15's D-173 is explicitly provisional. Ruling 16 changes who owns
  every digest and makes the caller wire role plus runs root only.
- A DRAFT-HEAD validator PASS binds only the copied bytes observed by that
  invocation. It does not bind the later `<<SEAM-HEAD>>` judge handoff.

## 7. What the seats must not do

Do not read `RUN_STATE.md`, `TASK_QUEUE.md`, run reports, council logs,
private doctrine, session memory, or scratchpads. Do not write to the
checkout, run state-changing commands, collect quiet-machine evidence, or
contact the operating session for clarification. Do not infer a paper value
from a fixture, infer adoption from implementation, treat a digest supplied
beside bytes as authority, or convert an undecidable atom into a favorable
merits verdict. Verify the charter digest independently before reading the
merits and report expected value, observed value, and method.

Return each numbered atom with AFFIRM/REJECT/REFUSE, severity, load-bearing
file:line or artifact:field evidence personally checked, explicit agreement
or disagreement with the magistrate's position, and a separate packet-hygiene
finding.

## 8. Exhibit manifest

```
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
523230f733d54981ae92dc826b01e2052c6c77be652e5c17c0149b6c8cd53bcb  20-exhibits/seam-draft-head-2e3349e1/docs/contracts/paper_supply_custody.md
a4d498f908b95d089401aa8d6f1dd6d2aa120dfae0cb6d6d32140d116f46e401  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/01-seat-landing-report.md
8a153042819b75faa48f8cdebb79d185c9c5db568742f9e7dbcd89bd029ba679  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/02-refuter-contract.md
d5f46526bbe78b05962ca6f51bac3c6234d415a4e74c828d8e7d93e65def7a91  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/02-refuter-execution.md
a8ae042ee88c39ae703da61d1d359ae77a0a00bcf19113e4947d4123826bd7d4  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/03-sol-fix-round-1-report.md
8943b8e45d3cba1daafb5e491ddbddf5f05bbb3a6be44450c3d6386ced291245  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/04-delta-reaudit-round-1.md
55f06c87f202824a3a1b851404dc82389e574dbf1311b1a5eb8901904d969364  20-exhibits/seam-draft-head-2e3349e1/docs/process_traces/2026-09-04-paper-custody/05-sol-fix-round-2-report.md
41d4b2129bfb387cd2797a7080dc4f0d7d6cf8ba476ad74b49ba7a4b52a43f5b  20-exhibits/seam-draft-head-2e3349e1/joulewise/paper_custody.py
```
