# Contract-lens refutation of the cold-gate ruling (Opus 5, 2026-08-30)

Seat: paired contract-lens refuter under rule 11. Read-only except this file.
I attacked the ruling; I did not attempt to improve it. Every verdict below is
grounded at a cited site I opened myself.

**Overall verdict: RATIFY-WITH-AMENDMENTS.** The two central holdings — Reading
B binds, and the ladder extends to 4096 — survive attack and should be ratified.
Four groups of supporting clauses do not survive:

- **A1** — the ruling states a falsehood about the record ("nothing in the
  record identifies a scientific cost to a longer prefill arm"; a seat raised
  exactly that cost as the strongest objection to its own recommendation), and
  rests Q1 on a premise ("8 appears nowhere") that is refuted three ways.
- **A2, blocker** — the exhausted-ladder branch conflates the pre-registered
  floor of 5 with the reducer's physical floor of 3 and would have the paper
  print an instrument refusal code the instrument did not emit.
- **A3, blocker** — the implementation clauses name one site out of at least
  four refusal sites and three pinning tests, and route the vacuity fix into a
  pre-registration object whose closed schema cannot hold it.
- **A4, blocker** — the rule is **not executable from the G2 record as ruled**:
  D-162's one-block G2 yields two small-model members on a 42-token decode
  prompt, i.e. zero observations at any rung. The ladder sweep exists only in an
  unmerged runsheet whose own threshold implements the reading this ruling
  overruled, and which is circular against the generator's fail-closed refusal.

None of these defeats the holdings; all four must be resolved before the D-166
row is rewritten. Amendments are enumerated exactly in §3.

---

## §1 Per-question verdicts

### Q1 — Reading-B derivation: **HOLDS-WITH-CAVEAT**

The *conclusion* (Reading B, count ≥ 5) survives. One supporting premise is
overstated and one is factually incomplete.

**What the seats actually said.** The convention *was* stated explicitly by a
seat, in two places, not one:

- `01-sol-seat.md:53` — "four or more gives one-record margin" (the site the
  ruling discloses in §0).
- `01-sol-seat.md:138` — **"Record the minimum overlap count and count margin
  relative to three."** This is a bare, unhedged statement of the
  `sample_count_margin` convention as a reporting requirement. The ruling does
  **not** cite it.

So the ruling's §1.Q1.1 sentence "the number 8 appears nowhere in any seat,
ruling, or measurement, and a hostile reviewer asking for its derivation gets
silence" is **wrong on its second half**. A hostile reviewer asking where 8
comes from gets a one-step derivation that is entirely in the record: a seat
directed that margin be counted against three, and the magistrate wrote
"margin (≥ 5)". Silence is not what the record offers. The literal numeral 8 is
indeed absent — that much is true and I verified it — but absence of the numeral
is a much weaker fact than the ruling trades on.

**Why the conclusion nevertheless holds.** Three grounds, in order of strength,
and only the first two are the ruling's:

1. *Unsatisfiability under A.* Verified: under Reading A no rung of the ruled
   ladder clears on any evidence available at ruling time or since. Projection
   §9 contingency table: 512 fails, 1024 fails, 2048 fails under A; §10 gives
   the slowdowns Reading A would require — 4.19× / 2.78× / 1.60× — against an
   assumed 1.133×. A reading that kills every option in the set the same
   sentence enumerates is not the reading that sentence bears.
2. *Sentence structure.* Holds as argued: under A the "≥ 3" clause is dead text.
3. *A ground the ruling missed, and should use:* Reading B is the only reading
   under which the ruled parenthetical is **continuous with the seats' own
   record counts**. Every count a seat wrote at the candidate lengths is a
   single-digit number in the 2–5 band (`02-opus-seat.md:83`: 2048 → "4–5
   records, passes with margin"; `03-fable-seat.md:41`: p256 → "2–3 records";
   `01-sol-seat.md:53`: "four or more"). "≥ 5" sits exactly at the top of the
   band the seats were arguing in. Under Reading A the magistrate would have
   been legislating a number 60% above the highest figure any seat put on the
   page, silently, in a parenthetical. That is the decisive textual argument and
   it is stronger than the one the ruling leads with.

**The caveat that must be recorded.** The ruling's §1.Q1.1 asserts the seats'
"highest projection at the ladder's top rung was 4–5 records at 2048 — and Opus
called that a PASS with margin." Correct (`02-opus-seat.md:83`). But note what
that concedes: **4–5 straddles 5**, so Reading B was not cleanly satisfiable on
the seat projections either — it is satisfiable only because the *measurement*
(projection §6: 2048 single-item counts 6 × 12, 7 × 2, smallest margin +3) came
in above the seat's fitted estimate. The asymmetry between the readings is real
but smaller than the ruling states: A is dead on every number anyone wrote; B
was borderline on the seats' numbers and is comfortable only on retained
measurement. Say that, rather than implying B was obviously satisfiable all
along.

**The premise is refuted a second time, and this one is fatal to it.** The
ruling says 8 appears in no "seat, ruling, or **measurement**." There is a
fourth category it did not check: **implementation**. The only place in this
repository where R-2 is turned into an executable test adopts **Reading A**.
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`, section
D2, on branch `origin/feat/window-provenance-check` (PR #229, still open):

```sh
'{... overlap_margin_above_three:($overlapping_power_interval_count-3)}'
...
  all_margin_ge_5: all(.[]; .overlap_margin_above_three >= 5)
```

`margin = count − 3`, threshold `>= 5` ⇒ **count ≥ 8**. The runsheet then states
in prose: "The `_v5` prefill length is the shortest of 512/1024/2048 whose row
has `all_margin_ge_5 == true`."

So an independent implementer, reading R-2 without this ruling, resolved the
ambiguity to Reading A and coded it. That is the strongest possible evidence
that the ambiguity was real and load-bearing — it also means the ruling's
"a hostile reviewer asking for its derivation gets silence" is not merely
overstated but demonstrably false: the derivation is running, in a shell script,
in this repo. This does not change the verdict (the magistrate has the authority
to rule the reading, and the reasons for B are good), but it converts a rhetorical
flourish into a checkable error, and it makes the runsheet a mandatory
implementation site (§3, A3).

**Severity: should-fix for the derivation; the implementation consequence is a
blocker.** The ruling's own cure — state the rule as a COUNT and never let the
bare word "margin" carry a threshold — is correct and is vindicated by exactly
this finding.

### Q2 — The 5 = 3 + 2 decomposition: **HOLDS-WITH-CAVEAT**

Is "+2 safety against adverse tile alignment and merged records" grounded, or
post-hoc? **Both, and the ruling should say so.**

**Grounded, component 1 (alignment): yes.** Projection §8 computes guaranteed
(shortest duration × p99 period) and typical (median × median) counts; at
2048/1.133× these are 5 and 6, at 1024/1.133× they are 3 and 4, at 512/1.133×
they are 2 and 3. The guaranteed-vs-typical spread is −1 across the board. The
ruling's "worth −1 versus typical" is exactly what §8 shows.

**Grounded, component 2 (merged records): existence yes, magnitude no.**
Projection §4 measures a 460.70 ms maximum record period against a 120.80 ms
median, and states the mechanism: "A few traces drop samples, which merges
intervals." So merged records are **measured, not invented** — the packet's
question ("is there measured evidence of merged records?") answers YES. But two
things the ruling gets wrong about them:

1. **Frequency is unquantified.** §4 says "a few traces"; no count, no rate, no
   per-corpus incidence. The projection reports the maximum and the percentiles
   and nothing between p99.9 (130.63 ms) and the 460.70 ms max.
2. **The magnitude exceeds the safety factor that is supposed to absorb it.**
   460.70 / 120.80 ≈ 3.8 median tiles. A single merged record inside a prefill
   window therefore costs roughly **2 to 3 records**, not one. "+2 whole records"
   does not cover the failure mode the ruling names it against. The arithmetic
   the ruling offers as the answer to "why 5?" does not close.

**What a hostile PC reviewer flags.** Not the existence of the mechanisms — the
*direction of derivation*. The number 5 was written into R-2 on 2026-08-28,
before the projection existed. The 3 + 2 decomposition was constructed on
2026-08-30 to explain it. That is a rationalization of a pre-registered constant,
which is **legitimate and normal** — but only if labelled as such. Presented as
the ruling presents it ("A guaranteed count of 5 buys, concretely: …"), it reads
as a derivation that produced 5, and a reviewer who checks the dates or the
merged-record arithmetic will find it did not.

**The honest framing is already in the record and the ruling should adopt it
verbatim.** Projection §9, exit 2: "The rule proper is `≥ 3`, which is what the
reducer enforces; **the margin is a pre-registration safety factor chosen at the
desk.** Lowering it is a decision about how much alignment risk the campaign
accepts." That is the defensible sentence: 3 is physics, 2 is a declared risk
appetite, chosen before collection, not computed from a bound.

There is also a purpose for the +2 that the ruling never states and that makes
it substantive rather than decorative: the rule is applied to **shakedown**
counts (a handful of members) but must protect the **campaign** (40 members,
20 small). The +2 is the headroom that keeps a campaign member from landing
below the reducer's floor of 3 on a draw worse than anything the shakedown saw.
State that and the safety factor has a job description; without it, "+2" is a
number with an anecdote attached.

**Severity: should-fix.**

### Q3 — 4096 added after seeing the projection: **HOLDS-WITH-CAVEAT**

**The strongest version of the objection**, stated as a hostile PC reviewer
would: *The authors pre-registered a three-rung ladder. They then ran an
analysis over their own retained corpus, learned that exactly one rung survives
and that it sits ~10% from failure, and responded by adding the one length in
their corpus with comfortable measured margin — the length that most reliably
delivers the outcome they want, which is a prefill contrast that resolves and
carries half the paper. The claim that "G2 has not run" is a technicality: the
decision-relevant quantity is record count versus prompt length, and the authors
had 1,127 bundles of exactly that before they amended. Pre-registration that can
be amended whenever the pre-registered option looks likely to fail is not
pre-registration.*

**Does the ruling's framing survive it? Yes — on one structural fact the ruling
states but under-develops (§1.Q2.4), plus two the ruling omits.**

1. **The extension is selection-preserving on the original domain.** The rule is
   "shortest rung that clears," and 4096 is appended as the *last* element of an
   ordered ladder. Therefore, for every G2 outcome in which any of
   {512, 1024, 2048} clears, the amended rule selects **exactly what the
   original rule selected**. The amendment can change the outcome in one branch
   only: the branch where the original ladder is exhausted — i.e. it converts a
   *refusal* into a *measurement*, and nothing else. An amendment that cannot
   change any non-refusal outcome cannot be steering the answer; it can only
   change what happens when there is no answer. This is a strong, checkable
   property and it should be stated in exactly these terms in the replacement
   text, because it is the whole defense.
2. **"Shortest that clears" forecloses the effect-size charge.** The reviewer's
   natural follow-on — "you picked the long prompt to inflate Δ" — is
   structurally impossible: the rule cannot select 4096 while a shorter rung
   clears. The ruling says this; it deserves to be first, not fifth.
3. **The repo's own pre-registration discipline is not violated, and the ruling
   never checks it.** The binding formulation in the decision log is
   pre-registration **before claim data** (`docs/decision_log.md:149`, D-124:
   "pre-registration in the D-117 packs BEFORE claim data"). The retained
   Qwen2.5 corpus is not `_v5` claim data — it is a different model pair, a
   different generation, and D-164 rules `_v4` "is never collected"
   (`docs/decision_log.md:191`). The amendment lands before any `_v5` byte
   exists. Cite D-124 and the objection loses its doctrinal footing, not merely
   its practical one.

**Where the ruling is affirmatively wrong, and it bears on this question.**
§1.Q2.3 asserts: "Nothing in the record identifies a scientific cost to a longer
prefill arm." **False.** The record identifies one, at length, twice, raised by
the seat that recommended the move as the strongest objection to its own
recommendation:

> `02-opus-seat.md:89` — "By moving prefill to 2048–4096 tokens I make the
> prefill contrast trivially resolvable (17–35× the bar), and the paper thereby
> loses the one place where its two-gate decision rule was going to be genuinely
> *tested* rather than merely *exercised*. … which a reviewer can read as the
> instrument being tuned until it agrees."

(Repeated at `02-opus-seat.md:207`.) The seat also supplies the answer — the
paper owns its hard case as a **printed negative**, and the projection now
strengthens that answer with primary evidence the seat did not have: 410 of 458
phases fail at 128 tokens and **211 of 650 fail at 512 tokens as suite items**
(projection §6). The two-gate rule is demonstrated on a real failure, in the
paper, with numbers.

So the ruling reaches the right place by asserting the record is silent when the
record is not. That is the single most quotable defect in the document: a
magistrate reading §1.Q2.3 would believe the objection was never raised.
Replace the false claim with the objection, named, and the seat's answer,
adopted, strengthened by §6's counts.

**Severity: blocker for the text, not for the holding.** (A1 in §3.)

### Q4 — The exhausted-ladder branch: **FAILS**

The branch is **not coherent as written**, and the incoherence is the kind that
would put a wrong instrument output in a published paper.

**The defect.** The branch says: if no rung clears, "the prefill arm is collected
at 4096 and the reducer's `not_resolvable_sample_count` refusal is printed as
that contrast's result." This **conflates two different thresholds**:

- the **pre-registered selection floor**, count ≥ 5 (this ruling), and
- the **reducer's physical floor**, `MIN_PHASE_SAMPLES = 3`
  (`joulewise/reduce.py:116`), which is what actually emits
  `not_resolvable_sample_count`.

They differ by 2 — which is precisely the safety factor the same ruling
introduces. So there is a **live gap at counts 3 and 4**: a G2 outcome in which
every rung including 4096 returns counts of 3 or 4 exhausts the ladder (no rung
clears ≥ 5) while every one of those phases is **perfectly resolvable to the
reducer**. In that branch the arm is collected at 4096, the reducer resolves it,
produces phase energies and a contrast — and the ruling instructs the paper to
print a refusal code the instrument **did not emit**.

That is not a drafting slip. Printing `not_resolvable_sample_count` as "that
contrast's result" when the reducer returned a number is misreporting an
instrument output, in a paper whose entire thesis is custody of instrument
outputs. It is also self-inconsistent: the ruling's own §1.Q3.4 reads counts
"from the production reducer's `summary_metrics.json` … never recomputed," and
that same reducer will have written a resolvable label.

**The source got this right and the ruling degraded it.** Projection §9, exit 3:
"**If the prefill arm is collected and refuses**, the paper prints
`not_resolvable_sample_count`…". The conditional is load-bearing and the ruling
dropped it.

**Does the branch terminate?** Yes — that part is sound. 4096 is a fixed
fallback with no further search, so the procedure is total: either a rung clears
and is selected, or 4096 is collected. No loop, no unbounded escalation.

**One sub-clause that does hold, and I checked it because I expected it to
fail.** "Holm family frozen at m = 2" is **already structurally enforced** and
needs no new mechanism: `joulewise/analysis_manifest.py:740` computes
`"m": len(family_contrast_ids)` from the **declared** contrast ids at
manifest-build time, not from which contrasts succeeded, and
`joulewise/analysis_engine/registry.py:431` asserts
`multiplicity == {"method": "holm", "alpha": 0.05, "q": None, "m": 2}` exactly.
A refused contrast cannot shrink the denominator. The ruling states this clause
as an obligation; it is in fact a description of existing behaviour, and saying
so removes it from the implementation list.

**Severity: blocker.** (A2 in §3.)

### Q5 — Vacuous satisfaction: **FAILS**, but not for the reason the ruling gives

The ruling diagnoses an open hole and proposes a sentence. In fact **an
enforcement site already exists, the ruling did not find it, and the fix as
drafted would not land there** — which is a worse position than the one the
ruling describes, because it looks closed while the running code is untouched.

**The site.** `SHAKEDOWN-G2-RUNSHEET.md` §D2 (branch
`origin/feat/window-provenance-check`) ends the selection block with:

```sh
/usr/bin/jq -e 'length == 3 and all(.members > 0)' \
  "$TRANSCRIPT_ROOT/d166-prefill-resolvability-summary.json"
```

`all(.members > 0)` is precisely the vacuity guard the ruling's §1.Q2.6 says is
missing: a rung with zero members fails the check and the run aborts. So the
mechanism exists — at a threshold of `> 0`, not at the ruling's suggested ≥ 3,
and on an unmerged branch. Note also `length == 3`, which hard-pins **three**
rungs and will refuse the four-rung ladder (see Q6).

**Why the verdict is still FAILS.** The ruling routes its fix into the
pre-registration object (§1.Q3.4, "the rung is evaluable (≥ 1 small-model member
at r; runbook minimum applies)") rather than into the jq that actually decides.
And the pre-registration object **cannot carry it**:

**There is no selection code, and the pin schema is CLOSED.** Nothing in
`joulewise/` reads a G2 record and applies the ladder rule; the selection is a
desk procedure whose only durable artifact is the prompt-pin file consumed by
the generator. Projection §12 confirms this is the intended shape ("The
selection is then mechanical") — mechanical by hand. And the pin file rejects
every field the ruling wants to add:

`configs/campaigns/d117_contrast_v5/generate_configs.py` (branch
`feat/v5-ladder-prep`), `_load_prefill_prompt_pin`, lines 797–811:

```python
    keys = {
        "schema_version", "selection_authority", "prefill_length",
        "tokenizer_json_sha256", "prompt_text", "prompt_text_utf8_sha256",
        "prompt_token_ids", "prompt_token_ids_sha256", "prompt_tokens",
        "repeat_count", "generation_method",
    }
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("prefill_prompt_pin_invalid: closed schema mismatch")
```

`set(value) != keys` is exact-set equality against `joulewise.prefill_prompt_pin.v1`
(:812-813). Therefore **every one of the ruling's §1.Q3 items 1–6 and 8 is
currently unrepresentable**: `ladder_prompt_tokens`,
`min_overlapping_power_interval_count`, `min_phase_samples_pinned`,
`sample_count_margin_floor`, the selection expression, the per-member SHA-256
shakedown binding, and the evaluability condition all trip the closed-schema
check. Item 8 additionally fails on type: the ruling would "upgrade
`selection_authority` from free text to the pair {G2 record path/ids, ruling
trace path}", but the loader validates it as a non-empty **string**
(:834-836).

So the ruling's Q3 answer requires a schema version bump to
`joulewise.prefill_prompt_pin.v2` plus loader and test changes — an
implementation clause of real size that the ruling does not name anywhere. Given
that this repository has a standing finding on exactly this failure mode
(rulings with implementation clauses that never reach code), shipping the
ruling without naming it repeats it.

**Severity: blocker.** (A3 in §3.)

### Q6 — Implementation clauses vs. the sites that exist: **HOLDS-WITH-CAVEAT**

**The named generator guard exists exactly as cited.** `generate_configs.py`
(branch `feat/v5-ladder-prep`), lines 864–870:

```python
    if prefill_length is None:
        raise ValueError(
            "prefill_length_unresolved: D-166 requires the G2 shakedown result; "
            ...
    if prefill_length not in {512, 1024, 2048}:
        raise ValueError("prefill_length_unknown: expected one of 512, 1024, 2048")
```

Verbatim as the ruling quotes, guard immediately after the refusal. ✓

**A site the ruling missed, and it is the one that fires first.**
`generate_configs.py:3253-3257`:

```python
    parser.add_argument(
        "--prefill-length",
        type=int,
        choices=(512, 1024, 2048),
    )
```

`argparse` `choices` rejects `--prefill-length 4096` with **exit code 2 before
`configure_model_pair` is ever called**, so amending only the `{512, 1024, 2048}`
guard the ruling names leaves the CLI refusing the new rung. Since the pack is
generated through this CLI (the inherited test at
`docs/process_traces/2026-08-30-t28-v5-prep/inherited-unowned/test_d117_contrast_v5_generator.py:79`
passes `str(prefill_length)` as a CLI argument), this is the operative refusal,
not a secondary one.

**The site that actually decides the question, and neither the ruling nor its
own §3.6 self-doubt reaches it.** `joulewise/analysis_manifest_v3.py:322-324` on
`feat/v5-ladder-prep`:

```python
_PROSPECTIVE_PREFILL_ARMS = frozenset(
    {"prefill_p256", "prefill_p512", "prefill_p1024", "prefill_p2048"}
)
```

The generator names its prefill arm `PREFILL_ARM = f"prefill_p{prefill_length}"`
(`generate_configs.py:1023`), so 4096 produces `prefill_p4096`, which is **not a
member**. The membership test at `analysis_manifest_v3.py:2127` then leaves
`prefill_arm = None`, `expected_condition_slots` collapses to `set()`, and the
validator refuses with `analysis_prospective_contrast_cover_mismatch`
(`:2136-2146`). This is not a passive library check: the generator validates its
own output and raises — `generate_configs.py:3135-3146`,
`raise ValueError("analysis_manifest_v3_refused: " + …)`. So with the two guards
above amended and this one left alone, `--prefill-length 4096` writes the entire
pack and then dies at the last step. A second hard-coded copy of the ladder sits
in the refusal detail string at `:2143-2145`
("(prefill_p256, prefill_p512, prefill_p1024, or prefill_p2048)") and becomes a
false operator message if only the frozenset is edited.

**And the precondition under it:** `joulewise/analysis_manifest_v3.py` **on
main** is still p256-only — `:2072-2073`, `:2160`, `:2311`, `:2320`, `:2647`.
The four-rung ladder is therefore meaningless unless PR #241's generalization of
this validator lands; today's main refuses *every* rung, 512 included, not just
4096. The ruling should state that dependency rather than assume it.

**Four more sites the ruling missed, all in the G2 runsheet and its test — and
these are where the rule is actually *executed*.** In
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` §D2 (branch
`origin/feat/window-provenance-check`, PR #229, OPEN):

| Site | Literal | Effect under the amended rule |
|---|---|---|
| §D2 collection loop | `for length in 512 1024 2048` | never collects the 4096 rung |
| §D2 record loop | `for length in 512 1024 2048` | never records the 4096 rung |
| §D2 verdict jq | `all_margin_ge_5: all(.[]; .overlap_margin_above_three >= 5)` | implements **Reading A (count ≥ 8)** — the overruled reading |
| §D2 final guard | `jq -e 'length == 3 and all(.members > 0)'` | **refuses a four-rung summary**; aborts the run |
| §D2 prose | "the shortest of 512/1024/2048 whose row has `all_margin_ge_5 == true`" | states the three-rung ladder and Reading A |

And the amendment is **mechanically blocked by a test**:
`tests/test_check_window_provenance.py:514-525` (same branch),
`test_runsheet_records_d166_prefill_resolvability_measurement`, asserts the
runsheet text contains `"for length in 512 1024 2048"`,
`"overlap_margin_above_three"` and `"all_margin_ge_5"`. Editing the runsheet to
the ruled four-rung, count-≥-5 form **fails this test** until the test is
updated in the same change. This is the single most concrete ruled-not-installed
risk in the package: the ruling changes a rule whose only implementation is
pinned in place by a green test.

**Test sites that enumerate the ladder** (coverage gaps rather than refusals,
but they encode the three-rung space and will need the fourth):
`docs/process_traces/2026-08-30-t28-v5-prep/inherited-unowned/test_d117_contrast_v5_generator.py:129`
and `:160`, both `for length in (512, 1024, 2048)`.

**On the floor-pack clause the ruling could not verify (its §3.6): it is
essentially a no-op for `_v5`, and the ruling should say so rather than leave an
unbounded obligation open.** The `_v5` generator is already fully parameterized
on `PREFILL_LENGTH` — the workload-profile name and `prompt_tokens`
(`generate_configs.py:1299`, `:1311-1314`), the family/plan/subcampaign ids
(`:991`, `:1003`, `:1023`, `:1051-1060`), the floor-dependency cell block
(`:1568`, keyed `f"prefill_p{PREFILL_LENGTH}_floor_dependency"`), and the
manifest metric tags (`:2306`, `:2362`). There is **no `p256` literal** anywhere
in the `_v5` generator. The hard-pinned `p256` cells the Opus seat named
(`02-opus-seat.md:79`, `:202`) live in the `_v4` pack
(`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/03_prefill_p256_contrast_blocks_*`),
which D-164 rules is **never collected** (`docs/decision_log.md:191`). So the
rename obligation the Opus seat raised was against a pack that no longer runs,
and the `_v5` packs accept any rung the generator accepts. The correct
amendment is to **close** this clause with that finding, not to carry it forward
as an unverified to-do.

**Verdict: HOLDS-WITH-CAVEAT** — the named site is real and correctly cited; the
site list is incomplete in one operative respect (argparse `choices`) and
over-broad in another (the floor-pack clause is already satisfied for `_v5`).

**Severity of the missed argparse site: blocker** (it would refuse the ruled
outcome space at runtime). Folded into A3.

### Q7 — "≥ 3 members per rung" vs. D-162 G2's one-block shape: **FAILS**

**How many small-model members does one block contain? Two.**
`configs/campaigns/d117_contrast_v5/generate_configs.py:1609` fixes the block as
`positions = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))` with
`MEMBERS_PER_BLOCK = 4` (`:145`); arm A is the small model (Qwen3-1.7B), arm B
the large. So one ABBA block = 4 members = **2 small-model members**.

D-162 G2 is exactly one such block —
`docs/process_traces/2026-08-28-live-smoke/proof-consult/04-MAGISTRATE-RULING.md:37-52`,
"real pack, real telemetry, one A/B/B/A block on the shakedown's own non-claim
runs root", with the runsheet's termination step
(`SHAKEDOWN-G2-RUNSHEET.md:612-628`) expecting exactly four block-1 bundles and
declaring a fifth science bundle an ABORT.

**So the ruling's suggested "≥ 3 small-model members per rung" is not satisfiable
from D-162 G2's ruled shape, which yields 2 — and, more importantly, that block
yields 0 members at *any* rung.** The ruled G2 block is a **decode**-arm block
(`generate_configs.py:1035-1064`: stages 1–2 are decode blocks 1–5 and 6–10;
prefill is stages 3–4), and the decode prompts are 42 tokens
(`configs/workloads/real_prompts_v1.json` against
`configs/model_panels/qwen3_4bit.json`). A 42-token prefill phase is far below
even the failing 128-token case (410/458 phases unresolvable, projection §6). The
ruled G2 record therefore contains **zero** observations at 512, 1024, 2048 or
4096.

**This is the finding that matters most in the package, and neither the ruling
nor the packet states it: as designed, the selection rule is not executable from
the G2 record.** The ladder sweep exists only as §D2 of the *unmerged* PR #229
runsheet, which (a) fixes no member count per rung — "every member named by its
SHA-bound order manifest", where those order manifests do not exist; (b)
generates no stages — `g2_prefill_resolvability` has zero hits in the `_v5`
generator on `feat/v5-ladder-prep`, whose CLI (`:3243-3258`) has no ladder,
arm, or block-count flag; and (c) is **circular**: §D2 sources its stages from
"the estate-12 mechanical re-cut" inside `$PACK_ROOT`, but the `_v5` generator
refuses to emit any bytes without a resolved `prefill_length`
(`:864-870`, `prefill_length_unresolved`), so the `_v5` pack cannot exist before
G2 while G2 §D2 requires the frozen `_v5` pack.

**Consequence for the ruling's Q3 defense.** The ruling's central answer to the
outcome-steering objection is "G2 measures the real Qwen3 counts before any
selection executes" (§1.Q2.4). That defense is sound *if and only if* a ladder
sweep actually runs. Today it does not exist. The amendment must therefore make
the sweep a condition of the rule, not an assumption behind it.

**Severity: blocker.** (A4 in §3.)

---

## §2 Findings by severity

**Blockers (must be resolved before ratification).**

- **B1 — The exhausted-ladder branch would misreport an instrument output.**
  Counts of 3 or 4 exhaust the ladder while remaining resolvable to the reducer
  (`joulewise/reduce.py:116`, `MIN_PHASE_SAMPLES = 3` vs. the ruled floor of 5);
  the ruling instructs the paper to print `not_resolvable_sample_count` in a
  branch where the reducer emits no such refusal. Q4.
- **B2 — The ruled pre-registration object is unrepresentable.** Seven of the
  eight §1.Q3 encodings trip the closed-schema check at
  `generate_configs.py:797-811`, and item 8 additionally fails the string type
  check at `:834-836`. Requires a `prefill_prompt_pin.v2` schema bump the ruling
  does not name. Q5.
- **B3 — The named implementation site list is incomplete in ways that would
  refuse the ruled outcome at runtime.** The ruling names one site; there are at
  least four refusal sites and three pinning tests. In order of when they fire:
  `argparse choices=(512, 1024, 2048)` (`generate_configs.py:3256`, exits before
  the named guard); the named guard itself (`:869-870`);
  `_PROSPECTIVE_PREFILL_ARMS` (`joulewise/analysis_manifest_v3.py:322-324`,
  which refuses *after* the whole pack is written, through the generator's
  self-validation at `generate_configs.py:3135-3146`); and the G2 runsheet's §D2
  loops, Reading-A verdict jq and `length == 3` guard. Pinned in place by
  `tests/test_check_window_provenance.py:514-525` and
  `tests/test_analysis_manifest_v3.py:569-575`. Q1, Q5, Q6.
- **B4 — The selection rule is not executable from the G2 record as designed.**
  Ruled G2 = one decode-arm block = 2 small-model members at 42 tokens = zero
  rung observations; the sweep exists only in unmerged PR #229 §D2, which is
  itself circular against the generator's `prefill_length_unresolved` refusal.
  Q7.
- **B5 — The ladder clause has an unstated precondition.**
  `joulewise/analysis_manifest_v3.py` on **main** is hard-pinned to
  `prefill_p256` at `:2072-2073`, `:2160`, `:2311`, `:2320`, `:2647`, and
  refuses every rung of the ladder. The amended rule is inert unless PR #241's
  generalization of that validator lands. Q6.

**Should-fix.**

- **S1 — §1.Q2.3 states a falsehood about the record.** "Nothing in the record
  identifies a scientific cost to a longer prefill arm" is contradicted by
  `02-opus-seat.md:89` and `:207`. Q3.
- **S2 — The "8 appears nowhere" premise is refuted three ways** (a seat stating
  the convention at `01-sol-seat.md:138`; the same seat at `:53`; and a working
  implementation of Reading A in the G2 runsheet). The conclusion survives; the
  reason must be rewritten. Q1.
- **S3 — The 3 + 2 decomposition is presented as a derivation and is a
  rationalization.** Alignment (−1) is grounded in projection §8; merged records
  are measured in existence (§4, 460.70 ms max) but unquantified in frequency,
  and a merged record costs ~2–3 records, more than the +2 that is meant to
  absorb it. Adopt projection §9's own framing — "the margin is a
  pre-registration safety factor chosen at the desk". Q2.
- **S4 — The floor-pack clause (§1.Q2.7, §3.6) should be closed, not carried.**
  The `_v5` generator is fully parameterized on `PREFILL_LENGTH` and contains no
  `p256` literal; the hard-pinned `p256` cells are in the `_v4` pack that D-164
  rules is never collected (`docs/decision_log.md:191`). Q6.

**Nits.**

- **N1 — The ~21 s cost figure applies a small-model duration delta to all 40
  members.** Projection §9's own basis; the large-model half is ~2.15× longer
  (projection §7), so ~33 s is the like-for-like figure, and the consult's Opus
  seat computed +106 s on its own basis (`02-opus-seat.md:85`). The conclusion
  (negligible against an hours-long window) is robust under every basis; the
  words "arithmetic checked" should not attach to it.
- **N2 — "Holm family frozen at m = 2" is not a new obligation.**
  `joulewise/analysis_manifest.py:740` sets `m` from the declared contrast ids at
  build time and `joulewise/analysis_engine/registry.py:431` asserts `m == 2`
  exactly; a refused contrast cannot shrink the denominator. Describe it, do not
  list it as work.
- **N3 — D-164's index row still says "prefill_p256 … transfer unchanged"**
  (`docs/decision_log.md:191`), now superseded by D-166 as amended. Consistency
  sweep item.

---

## §3 Amendments required (RATIFY-WITH-AMENDMENTS)

Ratify the two holdings — **Reading B (count ≥ 5) binds** and **the ladder
extends to {512, 1024, 2048, 4096}** — subject to all of the following.

**A1 (from S1, S2, S3 — the ruling's own text).**
1. Delete "the number 8 appears nowhere in any seat, ruling, or measurement, and
   a hostile reviewer asking for its derivation gets silence" (§1.Q1.3). Replace
   with: the convention *is* in the record (`01-sol-seat.md:53`, `:138`) and was
   implemented as Reading A in the G2 runsheet's §D2 jq — which is why the rule
   must be restated as a count, and why the runsheet must be corrected.
2. Add the ground the ruling missed: every record count any seat wrote at the
   candidate lengths lies in 2–5, so "≥ 5" sits at the top of the band the seats
   argued in, whereas Reading A would legislate a number 60% above the highest
   figure on the page, silently, in a parenthetical.
3. Record the concession that 4–5 at 2048 (`02-opus-seat.md:83`) straddles 5, so
   Reading B was borderline on seat projections and is comfortable only on
   retained measurement (projection §6: counts 6–7).
4. Replace §1.Q1.3's "+2" derivation with projection §9's framing: 3 is the
   reducer's physical floor; **2 is a declared risk appetite chosen at the desk
   before collection**, whose job is to keep a campaign member (20 small-model
   members) from falling below the floor on a draw worse than the shakedown's
   few members saw. State that merged-record frequency is unquantified and that
   a merged record can cost more than 2 records.
5. Delete "Nothing in the record identifies a scientific cost to a longer
   prefill arm" (§1.Q2.3). Replace with the objection named at
   `02-opus-seat.md:89`/`:207` and the seat's answer, strengthened by the
   printed negatives now measured: 410/458 phases fail at 128 tokens and
   **211/650 fail at 512 tokens as suite items** (projection §6).
6. Promote to first position in the Q2 derivation the selection-preserving
   property: appending 4096 to an ordered "shortest that clears" ladder cannot
   change the selection in any branch where an original rung clears; it can only
   convert a refusal into a measurement. Cite D-124 (`docs/decision_log.md:149`,
   pre-registration before **claim data**) and D-164 (`:191`, `_v4` never
   collected) to show the repo's own discipline is not strained.

**A2 (from B1 — the exhausted-ladder branch, mandatory rewrite).** Replace the
branch clause everywhere it appears (§1.Q2 rule statement, §1.Q3.6, and §2's
replacement sentence) with text that separates the two thresholds. Required
substance: *if no rung clears the pre-registered floor of 5, the prefill arm is
collected at 4096 and the contrast is reported as a **pre-registration
refusal** — declared as such, distinct from any reducer refusal code. If the
reducer additionally reports `not_resolvable_sample_count`, that code is printed
as the instrument's own output; if the reducer resolves the phase, the reducer's
number is reported alongside the declaration that the arm ran below the
pre-registered margin, and no reducer refusal code is printed. The Holm family
stays at m = 2 either way.* The paper must never print an instrument refusal the
instrument did not emit.

**A3 (from B2, B3, B5 — implementation clauses, exhaustive).** §1.Q2.7 must name all
of the following, and the magistrate should treat the list as the transaction's
checklist:
1. `configs/campaigns/d117_contrast_v5/generate_configs.py:869-870` — guard
   `{512, 1024, 2048}` → `{512, 1024, 2048, 4096}` (as ruled).
2. `configs/campaigns/d117_contrast_v5/generate_configs.py:3256` — argparse
   `choices=(512, 1024, 2048)` → `(512, 1024, 2048, 4096)`. **Not in the ruling;
   fires before (1).**
3. `joulewise/analysis_manifest_v3.py:322-324` — `_PROSPECTIVE_PREFILL_ARMS`
   must gain `prefill_p4096`, and the duplicated ladder in the refusal detail
   string at `:2143-2145` must be updated with it. **Not in the ruling; this is
   the site that refuses last, after the pack is written, via the generator's
   self-validation at `generate_configs.py:3135-3146`.**
4. `tests/test_analysis_manifest_v3.py:569-575` —
   `test_prospective_accepts_legacy_and_each_ruled_prefill_arm` loops the four
   legacy arms; its name claims coverage of "each ruled prefill arm" and would
   silently stop being true. Must gain `prefill_p4096`. **Not in the ruling.**
5. **Precondition, not an edit:** the ladder clause presumes PR #241's
   generalization of `joulewise/analysis_manifest_v3.py` lands. On main that
   file is p256-only (`:2072-2073`, `:2160`, `:2311`, `:2320`, `:2647`) and
   refuses every rung. State the dependency.
6. `generate_configs.py:797-813` — pin schema bumped to
   `joulewise.prefill_prompt_pin.v2` with the §1.Q3 fields added to the closed
   key set, `selection_authority` retyped from `str` to the ruled pair, and the
   `min_count − min_phase_samples == margin_floor` validity check installed.
   **Not in the ruling.**
7. `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` §D2 (PR
   #229) — both `for length in 512 1024 2048` loops extended; the verdict jq
   changed from `overlap_margin_above_three >= 5` (Reading A) to
   `overlapping_power_interval_count >= 5` (Reading B, as ruled); the
   `length == 3` guard changed to `length == 4`; the `all(.members > 0)` guard
   raised to the ruled per-rung minimum; the prose sentence updated. **Not in
   the ruling; this is the only executable implementation of R-2.**
8. `tests/test_check_window_provenance.py:514-525` — the three string assertions
   pinning the old ladder and Reading A updated in the same change, or the
   runsheet edit fails CI. **Not in the ruling.**
9. `docs/process_traces/2026-08-30-t28-v5-prep/inherited-unowned/test_d117_contrast_v5_generator.py:129,160`
   — ladder iterations extended to cover 4096.
10. **Close** the floor-pack clause with the finding in S4 rather than leaving it
    open: no `_v5` site needs changing; the `p256` cells belong to the
    never-collected `_v4` pack.
11. `docs/decision_log.md:193` — the D-166 index row rewritten with §2's
    replacement text (as amended by A2); `docs/campaign_packs/d117_contrast_v5.md:75,82`
    ("the shortest of 512, 1024, or 2048 tokens") updated; and `:191`'s stale
    `prefill_p256` reference noted (N3).

**A4 (from B4 — executability, the condition on which the whole rule rests).**
The ruling must add a clause making the ladder sweep a precondition rather than
an assumption. Required substance:
1. State plainly that the ruled D-162 G2 block (one ABBA block, decode arm,
   42-token prompts, 2 small-model members) supplies **zero** observations at
   any rung, so the rule cannot execute against G2 as ruled.
2. Make the rule conditional on PR #229's §D2 ladder stages landing, carrying
   the ruled reading (count ≥ 5) and the fourth rung.
3. Resolve the circularity explicitly: §D2 sources its stages from the frozen
   `_v5` pack, which the generator refuses to emit without a resolved
   `prefill_length`. Name the vehicle — a pre-mint diagnostic/draft pack that
   does not go through the `_v5` generator's refusal path — or rule that the
   sweep runs outside `$PACK_ROOT` entirely.
4. Fix the per-rung member minimum at a number the built design can deliver, and
   record it in the runbook, not only in the pre-registration object. Note that
   the ruling's suggested **≥ 3 is not achievable from an ABBA block (2
   small-model members)**; it is achievable only from purpose-built
   small-model-only stages, which is what §D2 nominally describes and does not
   yet generate. Whatever number is fixed, the `all(.members > 0)` guard in §D2
   is the site that enforces it.

**Not amended.** Reading B binds; the four-rung ladder binds; "shortest that
clears" binds; the Holm freeze at m = 2 binds (already enforced, N2); the
generator's `prefill_length_unresolved` fail-closed refusal is correct and
stays.

---

## §4 What I did not verify

1. I did not run any test or generate any pack; all code findings are static
   reads of `feat/v5-ladder-prep`, `origin/feat/window-provenance-check`, and
   main.
2. I did not reproduce the projection's numbers from raw bundle bytes; like the
   cold instance, I relied on its self-reported hash discipline and its
   1127/1127 reducer-label agreement.
3. I did not review PR #229's or PR #241's review threads, only their branch
   contents.
4. I did not audit whether a pre-mint diagnostic pack vehicle exists that could
   break the A4.3 circularity — I establish that the circularity exists, not
   that it is unsolvable.
