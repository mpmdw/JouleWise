# ALIGN v4 series seed check — Sol

2026-11-08. **Verdict: MATCH** for the merged ordinary-series manifest at
`25860dcaffdbae42ec04334bdaffeb3e96c4c029`. All 260 slots agree with the
rulings and kit; there are **zero slot differences and zero JSON differences**.
The escalation placement remains an open ruling, not part of this verdict.

Branch: `align/2026-11-08-series-seed-check-sol` (already provisioned, clean at
intake). Authority: `git show origin/main:RUN_STATE.md`, item 226 R15, with
`origin/main` at `02ef89f5c67c5bec2b04ab6521129e3f878cdfa6`; paired-check
requirement in item 220. The current brief supplies the explicit 22-member
shape and alternating order; the kit and
[`pilot_protocol_v4.md`](../pilot_protocol_v4.md) supply W1 identities,
sentinel replay identity and seed law. No study outcomes were used.

## Independence and reproducibility

1. Read the lead ruling and W1 kit, including `scripts/align_v4_kit.py` and
   `joulewise/align/apple/sampling.py`. Neither executes in the independent
   generator. Embedded model/cache paths were treated as text.
2. Wrote [`derive_slots.py`](seed-check/derive_slots.py), a stdlib generator.
   W1 identities come from the actual config JSON, checked against its kit
   digest and collection-plan identity. New slots come from the brief/R15:
   independent increasing seed streams per pair; no series-builder imports.
3. Generated [`independent_slots.json`](seed-check/independent_slots.json)
   and committed both at **`ecbf39e42` before opening the target manifest**.
   Snapshot SHA-256:
   `58365e68525d521740534fd9fb3f8ef8fd05629b7ab28f392bf17e454b91ad53`.
4. Only then opened the target JSON to learn its schema. Wrote
   [`check_manifest.py`](seed-check/check_manifest.py), which encodes the
   already-frozen allocation, independently computes first-turn seeds, and
   compares every JSON leaf and the entire file. Metadata labels and exact
   descriptive-string spelling were learned from the target JSON; matching
   that prose is **not independent evidence of allocation correctness**.
5. Produced [`series_manifest.json`](seed-check/series_manifest.json), a
   byte-identical reconstruction, and [`comparison.json`](seed-check/comparison.json),
   the machine-readable comparison and original-anchor receipts.

The builders' `scripts/align_v4_series.py` generation code was never opened.
After the independent comparison, the existing focused `ManifestTests` were
run; those tests import the production builder. The independent checker does
not import it. The precomparison generator and snapshot remain unchanged.

Reproduce from the repo root, offline:

```sh
python3.13 -B docs/align/v4/seed-check/check_manifest.py
```

The default invocation writes nothing. `--write` regenerates only the two
comparison artifacts under `seed-check/`, never the production manifest.

## Slot-by-slot result

Compared pair, condition, seed index, episode seed, model, role and ordinal
for **18 W1 + 11×22 C/T = 260 members**, or **1,820 identity-field comparisons**.
Also compared every first-turn seed, pool label, window/alias/order field,
midpoint and all other JSON leaves. The manifest uses explicit `role` for W1;
C/T semantic roles are encoded by `pool`, with ordinals distinguishing early
and late sentinels and condition distinguishing the test members.

| Window | Held-out indices per pair, in kit order | First pair at ordinal 6 | Sabotage at 9 | Sabotage at 18 | Differences |
|---|---|---|---|---|---|
| W1 | Original 18-member kit; no held-out allocation | Original kit | Original kit | Original kit | 0 |
| C1 / D1 | 2–9 | spam | bank, 3 | spam, 8 | 0 |
| C2 / D2 | 10–17 | bank | spam, 11 | bank, 16 | 0 |
| C3 / D3 | 18–25 | spam | bank, 19 | spam, 24 | 0 |
| C4 / D4 | 26–33 | bank | spam, 27 | bank, 32 | 0 |
| C5 / D5 | 34–41 | spam | bank, 35 | spam, 40 | 0 |
| C6 / D6 | 42–49 | bank | spam, 43 | bank, 48 | 0 |
| C7 / D7 | 50–57 | spam | bank, 51 | spam, 56 | 0 |
| C8 / D8 | 58–65 | bank | spam, 59 | bank, 64 | 0 |
| T1 | 66–73 | spam | bank, 67 | spam, 72 | 0 |
| T2 | 74–81 | bank | spam, 75 | bank, 80 | 0 |
| T3 | 82–89 | spam | bank, 83 | spam, 88 | 0 |

`spam` means `spam_filter_update`; `bank` means `bank_transfer_2`.
Each sabotage entry gives pair and seed index.

- Order is W1 → C1–C8 → T1–T3; D1–D8 are C aliases, not extra windows.
- Every C/T has its original four 30B anchors at 1–4, early sentinel at 5,
  16 alternating held-out members at 6–21, and late sentinel at 22.
- Each pair contributes seven fresh benign and one sabotage per window.
  C therefore allocates 56 benign + 8 sabotage per pair; T allocates
  21 benign + 3 sabotage per pair. These are planned counts, not eligibility
  claims. C sabotage has `known_h` pool and never enters calibration.
- C and T have disjoint, exhaustive per-pair index streams 2–65 and 66–89.
  None uses 1 or 91–99 for held-out work. Re-arm seed reuse is explicitly
  recorded; this static check does not exercise a live re-arm.
- Both sentinels replay W1:5: D model `qwen3.8-27b`, spam/benign, seed index 1,
  episode seed `11160969177166136631`, first-turn seed `13933079069872451601`.
- The four current anchor config blobs are byte-identical to their original
  `83e2dac59d347f34052f5713280d62ef60bb01d8` kit objects. All 44 C/T anchor
  slot identities agree with those W1 anchors. This is not a claim that this
  checker independently materialized every C/T executable config.

Episode seeds were recomputed as the first eight bytes, big-endian, of SHA-256
over compact JSON `['align-p4-v1', model, 'thinking_on', 'shade/'+pair, index]`.
Condition is intentionally absent from the seed law. First-turn seeds use
`['align-p4-turn-v1', episode_seed, 0]` under the same law.

**Every difference:** none. There is no disputed slot to adjudicate; both
allocations match the rulings. The receipt preserves empty `slot_differences`
and `manifest_differences` arrays and fails if any compared value changes.

## Hashes

| Digest | Brief, production file and independent reconstruction |
|---|---|
| Canonical SHA-256, compact sorted-key JSON, no trailing newline | `01e2363d1d45e3593def99e538761bd8424fdd962faa12576559733a11964672` |
| File SHA-256, sorted-key indented JSON with trailing newline | `eba6fb0732ec26996a0c63bb679a899b71dc2009474502e59048dd67d764f0c7` |

Both hashes match exactly, and the reconstructed file equals the production
file byte for byte. The production manifest was not edited.

## Escalation recommendation — requires lead ruling

**Recommend appending the two extra sentinels at execution ordinals 23 and
24, immediately after the ordinary late sentinel at 22 and before the closing
reference/scaffold. Both replay exactly the admitted W1:5 trajectory**, with
the same D model, spam/benign condition, seed index 1, episode/turn seed law,
sampler, work budgets, cache policy and effective stack. Each is a separate
batch-1 member with the normal idle and thermal gates. No held-out seeds are
consumed. Do not implement this recommendation as a registration choice
without the lead's prospective ruling.

Reasons:

- It preserves every ruled ordinary slot, seed/condition assignment, the
  ordinal-9/18 sabotage placements and midpoint after 11. Comparisons to
  earlier ordinary windows retain the same first 22-member schedule.
- Replaying one admitted source tests repeatability/drift on the same work;
  another pair or a fresh seed would mix work differences into that check.
- It needs no reinterpretation of “ordinal”. Inserting one extra after 5
  and one before 22 would balance early/late replication, but would move the
  existing held-out slots and sabotage execution ordinals to 10/19. That
  requires an explicit R15 order amendment and a regenerated paired check.

**Tradeoff and uncertainty:** appending concentrates three of four sentinels
late. It provides less balanced early/late information, and simply pooling
all four equally would change the temporal weighting of U4. The lead must
freeze whether these are supplemental diagnostics or define a prospective
U4 aggregation rule before use. Extra members are not extra independent
windows: do not increase U4's W or its W−1 degrees of freedom. They also do
not supply new R1 designed start states and cannot be promised to resolve U5.
If balanced replication is the scientific priority, choose the insertion
alternative explicitly and amend the ordinal mapping; do not silently shift
the already-checked manifest.

The trigger governs **remaining windows**, after a prior U4/U5 inconclusive
result, not an outcome-driven extension of the just-finished window. Freeze
the escalated roster/sizing before its arm, use R15's **62,400 s** ceiling,
and retain **59,520 s** for ordinary windows. Recompute actual sizing from
the largest W1 D member time; the extra 2,880 s in the ceiling is not itself
a two-member duration allowance. Existing synthetic sizing tests give
58,260 s ordinary and 61,860 s escalated at their planning assumptions;
these are not native timing evidence.

If W1 rejects ordinal 5, R15 requires sentinel-alternate regeneration before
C1. Protocol registration installation §15 names W1:18 (bank/benign,
development seed 93) only as a candidate requiring prospective qualification
and a matched reference. Neither ordinary nor extra sentinels may silently
switch to it or repair a missing E_ref.

**NEEDS_RULING**

- Question: append the two W1:5 replays at 23/24, or amend the schedule for
  balanced early/late insertion, and how do extra sentinels enter U4?
- Options: append at 23/24 preserving all ruled slots; balanced insertion
  with an explicit ordinal/aggregation amendment.
- Recommendation: append at 23/24 under the current literal order, with
  aggregation explicitly frozen by the lead; no implementation here.
- Blocked work: signing/admitting an escalated roster. The ordinary-series
  seed-check verdict is complete; this report grants no arm authority.

## Verification and handoff

All commands used Python 3.13, offline, without model weights or measurement
data. Targeted unittest invocations were sequential:

| Command | Result |
|---|---|
| `python3.13 -B docs/align/v4/seed-check/check_manifest.py --write` | MATCH; all 10 receipt checks true |
| `python3.13 -B -m unittest discover -s docs/align/v4/seed-check -p test_seed_check.py -v` | 8 passed, 0.171 s initial / 0.198 s final |
| `python3.13 -B -m unittest tests.align.test_v4_series.ManifestTests -v` | 8 passed, 0.701 s |
| `git diff --cached --check` | Passed |
| `git diff --no-index configs/campaigns/align_v4/series/series_manifest.json docs/align/v4/seed-check/series_manifest.json` | Exit 0; byte-identical |

All three added Python sources also passed stdlib `compile()` with no bytecode
writes. The protected coordination files and production manifest have empty
diffs against `25860dcaf`.

The checker tests mutate each requested identity field, simultaneous changed
leaves, window/member order and presence, pool/role, first-turn seeds, midpoint
and ceiling. They verify that a disagreement is reported rather than hidden
by a matching subset or a hash alone. The existing focused tests additionally
check aliasing, config generation, sizing and pending admission refusal.

No full suite, live native execution, analysis pipeline, network access,
model downloads, or external study-path access. No native MLX test is needed
for these stdlib-only additions; this supplies no evidence about native
replay identity or the live W1 admission gates. The lead owns those checks.
No throughput change or measured speed claim was made; the origin/main
speed toolbox was read and measured members remain batch-1.

Files: this report; `seed-check/{derive_slots.py,independent_slots.json,
check_manifest.py,series_manifest.json,comparison.json,test_seed_check.py}`;
and the dated run-report pointer. Coordination state and production files
are unchanged. The first commit is `ecbf39e42` (blind derivation); the second
commit contains the schema adapter, comparison artifacts, tests and reports.

Next exact step: the lead compares this MATCH receipt with the independent
Opus seed check, rules on escalation placement/aggregation, regenerates and
rechecks bytes if that ruling changes the manifest, then signs the exact
agreed manifest through the normal registration gate.
