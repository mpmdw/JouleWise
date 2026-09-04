# Opus contract-lens consult seat — F-N4 and the fourth prose signature

- **Packet:** `docs/process_traces/2026-09-02-decode-identity-set/38-consult-packet-fn4-fourth-prose-signature.md`
- **Packet head sha:** `fbedfb04`
- **Model / seat:** Opus 5 (`claude-opus-5[1m]`), independent CONTRACT lens, read-only
- **Checkout:** `/Users/edr/code/JouleWise-wt-decode-id`, branch `fix/2026-09-02-decode-identity-set`
- **Working tree at read time:** `2f3592c5` (three commits ahead of the packet head). I verified
  `git diff fbedfb04 HEAD -- docs/contracts/identity_pin_projection.md` is **empty** — the contract
  text I audited is byte-identical to the packet's head. The only diffs are trace files 37–40.
- **Blindness attested:** I did not open file 39, 40 or anything newer, and read no other seat's
  answer. `ls` showed 39 and 40 exist; I did not read them. Files read for history: 32, 33 (§R3-C
  header), 34 (first-use table + R3-C clause table), 37 (F-N4 finding).
- **Writes:** none under the checkout. This report is the only file written, to scratchpad.

---

## §0. Bench evidence log

Every claim in this report marked **[BENCH]** was produced by one of these commands, run by me in
this session in `/Users/edr/code/JouleWise-wt-decode-id`.

**B1 — contract text is the packet's text**
```
git diff fbedfb04 HEAD --stat            # only files 37,38,39,40 differ
git diff fbedfb04 HEAD -- docs/contracts/identity_pin_projection.md   # empty
```

**B2 — the paragraph under audit (:609–621)**
```
grep -n "" docs/contracts/identity_pin_projection.md | sed -n '595,630p'
```

**B3 — the four nouns across every contract**
```
grep -rn "consumption receipt\|window root\|lifecycle receipt\|launch manifest\|window_plan_root" docs/contracts/*.md
```
Result: only `identity_pin_projection.md`, at `:612`, `:613`, `:615`, and `:671`.

**B4 — mechanical first-use table (this is also the Q3 test)**
```
for t in "consumption receipt" "launch manifest" "window root" "lifecycle receipt" \
         "launch_binding_mismatch" "launch_consumption_missing" \
         "consumer_identity_set_unauthenticated" "evidence row" "launch lineage" \
         "pack root" "input loading" "arming time"; do
  first=$(grep -n "$t" docs/contracts/identity_pin_projection.md | head -1 | cut -d: -f1)
  def=$(grep -n "\*\*$t\*\*\|\*\*${t}s\*\*" docs/contracts/identity_pin_projection.md | head -1 | cut -d: -f1)
  printf "%-42s first=%-6s bolddef=%-6s\n" "$t" "${first:-NONE}" "${def:-NONE}"
done
```
Output verbatim:
```
consumption receipt                        first=612    bolddef=NONE
launch manifest                            first=612    bolddef=671
window root                                first=612    bolddef=NONE
lifecycle receipt                          first=613    bolddef=NONE
launch_binding_mismatch                    first=614    bolddef=NONE
launch_consumption_missing                 first=615    bolddef=NONE
consumer_identity_set_unauthenticated      first=620    bolddef=NONE
evidence row                               first=610    bolddef=NONE
launch lineage                             first=610    bolddef=NONE
pack root                                  first=464    bolddef=NONE
input loading                              first=614    bolddef=NONE
arming time                                first=NONE   bolddef=NONE
```

**B5 — executed refusal probe: which reason code does each missing arming-time path actually emit?**
```
python3 - <<'PY'
import sys, tempfile, pathlib
sys.path.insert(0,'.')
from joulewise import arm_readiness as ar
from joulewise.arm_readiness import LaunchLineageError
tmp = pathlib.Path(tempfile.mkdtemp()); gone = tmp / "gone.json"
def probe(name, fn):
    try: fn(); print(f"{name}: NO ERROR")
    except LaunchLineageError as e: print(f"{name}: reason_code={e.reason_code!r} :: {e}")
    except Exception as e: print(f"{name}: {type(e).__name__}: {e}")
probe("launch manifest missing", lambda: ar._read_exact_launch_reference(
    {"path": str(gone), "sha256": "0"*64}, max_bytes=1<<20, label="launch manifest"))
probe("lifecycle start receipt missing", lambda: ar._read_lifecycle_receipt(gone, expected_kind="launch_start"))
probe("consumption receipt missing", lambda: ar._read_v2_consumption(gone))
probe("window root missing", lambda: pathlib.Path(str(tmp/"nowhere")).resolve(strict=True))
PY
```
Output verbatim (temp paths abbreviated):
```
launch manifest missing:            reason_code='launch_consumption_invalid'  :: bound launch artifact is unreadable: …/gone.json
lifecycle start receipt missing:    reason_code='launch_lifecycle_incomplete' :: launch-lineage receipt is absent: …/gone.json
consumption receipt missing:        reason_code='launch_consumption_missing'  :: launch-lineage receipt is absent: …/gone.json
window root missing:                FileNotFoundError: [Errno 2] …/nowhere
```

**B6 — the code sites the packet names (verified myself; packet ranges NOT trusted)**
```
grep -n "launch_binding_mismatch\|launch_consumption_missing\|authenticate_bundle_launch_lineage" -r joulewise/
grep -n "def _read_lifecycle_receipt\|def _read_launch_lineage_primary\|def _validate_lineage_reference\|def _pack_record\|def authenticate_bundle_launch_lineage\|def _read_v2_consumption\|def _replay_consumed_arm\|def authenticate_launch_lineage" joulewise/arm_readiness.py
grep -n "launch_manifest\"\]\|window_plan_root\|_read_lifecycle_receipt(" joulewise/arm_readiness.py
sed -n '2735,2800p' joulewise/analysis_engine/inputs.py
sed -n '8835,8880p;8955,9100p;9304,9470p;9794,9812p;10078,10270p;10608,10670p' joulewise/arm_readiness.py
sed -n '669,702p;210,232p' joulewise/arm_readiness.py
sed -n '5242,5265p' joulewise/arm_readiness.py
```

Verified line facts (all **[BENCH]**):

| Packet claim | Verified | Actual |
|---|---|---|
| `inputs.py:2773–2782` `_read_bundle` → `authenticate_bundle_launch_lineage` | **TRUE** | `def _read_bundle` at :2735; call at :2773; `except LaunchLineageError → raise AnalysisInputError(f"{exc.reason_code}: …")` at :2778–2782 |
| `_replay_consumed_arm` ~:9333–9352 emits `launch_binding_mismatch` | **TRUE** | `def` at :9304; `launch_binding_mismatch` emissions at :9342, :9350, :9364, :9376, :9379, :9383, :9409, :9422, :9431 |
| `_read_v2_consumption` ~:8960–8985 emits `launch_consumption_missing` | **TRUE** | `def` at :8960; `missing_code="launch_consumption_missing"` at :8965 |
| launch manifest ~:10187–10198 / :10222 | **TRUE** | `_read_exact_launch_reference(consumption["launch_manifest"], …)` at :10188; argv re-bind check at :10222 |
| window root ~:10200–10205 | **TRUE** | `Path(str(manifest["window_plan_root"])).resolve(strict=True)` at :10200; `launch_binding_mismatch` at :10203–10204 |
| lifecycle receipts ~:10233–10252 | **TRUE** | start at :10236, settle at :10246, `lifecycle = (…)` at :10254; `_read_lifecycle_receipt` def at :9794 with `missing_code="launch_lifecycle_incomplete"` at :9798 |

So the packet's code cites are accurate. Its **prose about the contract** is not, in three places (§1
below).

---

## §1. Anomalies found in the packet and in the landed text

I put these first because two of them change the answer to Q1.

### A0 (headline) — the packet's premise that the FACTUAL class is fixed is false. **[BENCH]**

Packet §2: *"The corrective adopted after round 2 … fixed the FACTUAL class (every clause of the
round-3 texts was PROVEN by terra against the code) and did not touch the PEDAGOGY class."*

That is not true of the landed R3-C paragraph. I found **two factual defects in it that neither
Sol 266's clause table nor terra 267's delta re-audit caught.** I am not lowering F-N4's severity; I
am adding findings.

#### F-N5 (new, factual) — the reason-code parenthetical is wrong for two of the four artifacts it binds

Contract `:611–616`:

> it replays the consumed arm and resolves the recorded pack root strictly, **as it resolves the
> consumption receipt, the launch manifest, the window root and the lifecycle receipts**, so a
> bundle whose arming-time paths no longer exist is refused at input loading
> (`launch_binding_mismatch`, or `launch_consumption_missing` when the consumption receipt itself is
> gone) and never reaches this gate.

The sentence enumerates four artifacts and then binds the whole enumeration to exactly two reason
codes. **[BENCH, B5]** the actual codes are:

| Missing arming-time path | Contract says | Code actually emits | Source |
|---|---|---|---|
| pack root | `launch_binding_mismatch` | `launch_binding_mismatch` ✅ | `arm_readiness.py:9349–9352` |
| consumption receipt | `launch_consumption_missing` | `launch_consumption_missing` ✅ | `arm_readiness.py:8965` → `:8855–8859` |
| window root | `launch_binding_mismatch` | `launch_binding_mismatch` ✅ | `arm_readiness.py:10200–10205` |
| **launch manifest** | `launch_binding_mismatch` | **`launch_consumption_invalid`** ❌ | `arm_readiness.py:8996–9011` (`resolve(strict=True)` → `OSError` → `"launch_consumption_invalid"`) |
| **lifecycle receipts** | `launch_binding_mismatch` | **`launch_lifecycle_incomplete`** ❌ | `arm_readiness.py:9798` (`missing_code="launch_lifecycle_incomplete"`) |

`arm_readiness.py:221–231` **[BENCH]** shows `LAUNCH_LINEAGE_REASON_CODES` is a **seven-member**
frozenset (`launch_consumption_missing`, `launch_consumption_invalid`, `launch_binding_mismatch`,
`launch_lineage_conflict`, `launch_lineage_axi_unsupported`, `launch_lifecycle_incomplete`,
`launch_handoff_invalid`). The contract names two of the seven and implies they are exhaustive over
the enumerated cases. `inputs.py:2778–2782` surfaces `exc.reason_code` verbatim into the
`AnalysisInputError` message, so what a reader of this contract would build a client against is
directly falsified by what the loader emits.

Under Ed's replication bar this is not a nit: a reader replicating the refusal handling from this
paragraph alone gets two of five cases wrong.

#### F-N6 (new, factual) — the pack root's provenance sentence is wrong

Contract `:609`: *"That root is the machine-absolute pack path recorded **when the arm was
consumed**."*

**[BENCH]** `CONSUMPTION_RECEIPT_KEYS` (`arm_readiness.py:680–701`) contains **no** `pack_root` key.
The pack root is read exclusively from `arm["pack"]["pack_root"]` (`_replay_consumed_arm`
`:9333–9336`), which is written by `_pack_record` (`:5242–5264`, key `"pack_root": str(pack_root.resolve())`)
**at arm time**. Consumption *replays* it; consumption does not *record* it.

Sol 266's own clause table (file 34 §R3-C) proves this by accident: its row reads
*"Arm records an absolute pack root → `arm_readiness.py:5242-5259`"* — i.e. the seat verified
**"the arm records it"** while the contract sentence asserts **"the consumption recorded it."**
The clause table and the sentence are about different propositions. That is the mechanism of the
whole failure, and it is the substance of my Q3 answer.

#### Consequence for the packet

Packet §2's third row ("round 3 consult, S1: dictated text wrong twice") and its claim that round 3's
landing was factually clean cannot both stand. **Three consecutive formulations have now failed on
the FACTUAL axis as well** (round 1 F-N: sentence not matching code order; round 3 consult S1:
dictated text wrong twice; round 3 landing F-N5/F-N6: dictated text wrong twice again). The pedagogy
signature is real, but it is not the only one, and treating F-N4 as a purely pedagogical residue
under-reads the situation.

### A1 — packet §1 contradicts itself about `launch manifest`

§1 line 15–17 concedes *"**launch manifest** (bold-defined only later, at :671–673)"* and then line
32 asserts *"So none of the four nouns is defined in ANY contract."* **[BENCH, B3/B4]**
`**launch manifest**` **is** bold-defined, at `:671`. The true statement is an **ordering** defect
(definition 59 lines after first use), not an absence.

This is material, not cosmetic: **Cure A's entire rationale** — *"Rewrite so the paragraph names only
what this contract can define"* — rests on the false version. The contract *can* define launch
manifest; it already does.

### A2 — F-N4's extent is understated by two terms

**[BENCH, B4]** the same paragraph carries a **seventh** undefined-at-first-use item that neither the
packet nor terra 267 lists:

- `consumer_identity_set_unauthenticated` — first used at `:620`; the sentence that establishes its
  meaning is at `:634` ("The gate refuses with `consumer_identity_set_unauthenticated` when successor
  launch lineage exists but any one of the following steps … fails"). Forward reference of 14 lines.
- `evidence row` — first used at `:610`, never defined anywhere in the contract (**[BENCH]**
  `grep -n "evidence" … | awk -F: '$1<610'` returns only `:35, :40, :422, :567, :581, :582, :602`,
  none of which glosses "evidence row").

`consumer_identity_set_unauthenticated` matters because **Cure A explicitly keeps** the sentence that
first uses it ("the direct-call label" sentence). Cure A therefore leaves a first-use defect standing
inside the very paragraph it claims to have cleaned.

### A3 — `consumption receipt` is not undefined; it is a *synonym collision*

**[BENCH, B4]** the object is bold-defined at `:672` under a **different name**:
`**one-use consumption record** (the durable proof that this launch authorization has been spent
exactly once)`. The code calls it `consumption_receipt` / `validate_consumption_receipt`
(`arm_readiness.py:2586`, `:8960`). So this one contract carries two names for one object, 60 lines
apart, with no cross-reference.

This is worse than an undefined term, because **Cure B's proposed gloss** —
*"the consumption receipt — the durable one-use record that this launch authorization was spent"* —
reuses the later definition's exact vocabulary (*durable*, *one-use*, *spent*) **without saying they
are the same object**. Cure B would ship a contract that defines the same artifact twice, in
different words, under different names, and never says so. That fails the ONE-home convention this
project applies everywhere else.

### A4 — packet well-formedness as a rule-11 cold-gate packet

Rule 11 requires a cold Fable instance ruling on a **MECHANICALLY-assembled** packet, paired with an
Opus contract-lens refuter. This packet is magistrate-assembled and, by its own admission, the
magistrate "is the party proposing to continue." §1 is a narrative with a classification-adjacent
framing; §2 is a curated history table; §3 Q2 offers only magistrate-authored cures. As a *consult*
packet it is good and honestly self-flagging. As a *cold-gate* packet it is not mechanical, and if
the routing is (a) it must be re-assembled: raw quotes of the four audit findings verbatim, the four
landed texts verbatim, the code, no narrative and no pre-authored cures.

### A5 — minor: "before any evidence row exists" is over-broad

**[BENCH]** `_read_bundle` (`inputs.py:2735`) constructs and **returns** a `BundleEvidence` row at
`:2746–2763` (the missing-bundle-directory branch) *before* reaching
`authenticate_bundle_launch_lineage` at `:2773`. Harmless in effect — that branch has no lineage to
authenticate — but the contract sentence as written is falsifiable by a one-line counterexample, and
"before this gate runs" says the true thing for free.

### A6 — minor: `replays` is a term of art with two meanings in the code

**[BENCH]** `authenticate_launch_lineage` calls `_replay_consumed_arm(…, replay_arm_semantics=False)`
(`arm_readiness.py:10137–10144`), whereas `verify_consumed_launch` calls it with
`replay_arm_semantics=require_current_boot` (`:9455–9465`, docstring *"Replay a v2 consumption
without treating its arm as unconsumed"*). On the **bundle-loading path the contract is describing**,
the arm's PASS/GO derivation is **not** re-run — only the receipt and its pack binding are
re-authenticated. `authenticate_bundle_launch_lineage` (`:10608`) also passes **no**
`expected_pack_root` and leaves `require_current_boot=False`. So "replays the consumed arm" is the
strongest available reading of a weaker mechanism. This is exactly the class of unpaid word Ed's
standard forbids, and **Cure A retains it verbatim**.

---

## §2. Q1 — classification

**Answer: (a).** F-N4 is the same defect in the sense that triggers rule 11's mandatory cold gate
before any round-4 text lands. I hold this on three independent grounds, any one of which suffices,
and I note at the end why the classification is in fact **not load-bearing for the routing** — the
cold gate is mandatory on this packet regardless.

### The trigger text, read literally

Rule 11 and the standing trigger use **deliberately different words**:

- Rule 11, cold gate: *"Mandatory triggers, not discretion: **any second fix round on the same
  defect**; any reversal or reinterpretation of a stop signal or verdict; any irreversible action;
  **any proposed process rule**; any turn ending in a 'waiting' state on a scarce open resource."*
- Standing escalation trigger: *"two consecutive rounds failing with the **SAME SIGNATURE — same
  defect class**, another missed call site, another failed formulation — is evidence of a structural
  problem, and the next spend is a CONSULT, not round three."*

The doctrine therefore distinguishes **defect** (cold gate) from **defect class** (consult). A
literalist reading that individuates a defect by *finding ID* gives (b): F-N, F2, S1 and F-N4 are
four differently-named findings, and F-N4 sits in a paragraph (`:609–621`) that did not exist before
round 3, so it cannot be "the same defect" as F2.

I reject that individuation. Here is why.

### Ground 1 — the pedagogy defect has already had its fix round, and it failed

Individuate the defect by **what a fix round is trying to make true**, which is how "second fix round
on the same defect" must be read if it is to have any bite (otherwise every round renames the finding
and the trigger never fires — precisely the "eaten trigger" failure mode rule 11 exists to stop).

- The proposition "this contract section's prose introduces no term before it is defined" was first
  falsified in round 2 (**F2 / R-M5**, luna 263).
- Round 3 was the fix round on that section. Its brief (file 33 §R3-C) **required a first-use table**
  in the report. Sol 266 produced one (file 34) — and it omitted the new paragraph entirely.
- The same proposition is falsified again at landing (**F-N4**, terra 267).

Round 4 is therefore the **second fix round on the first-use defect**. Enumerated trigger met.

### Ground 2 — the factual defect has also already had its fix round, and it failed too (**[BENCH]**)

This ground did not exist before this session's bench work and is the stronger one, because it
requires no individuation subtlety.

- S1 (files 30–31) found the magistrate's **dictated** text factually wrong twice.
- The corrective (file 22 / file 32) was: dictate **with proving lines**, seat verifies
  **clause-by-clause**. Round 3's landing ran exactly that corrective.
- **F-N5 and F-N6 (§1 A0, bench-confirmed) are the same failure again**: the dictated text asserts a
  reason-code binding the code does not implement, and a provenance the receipt schema does not carry,
  and both survived the clause table *and* the delta re-audit.

Round 4 must fix F-N5/F-N6. Round 4 is therefore the **second fix round on the "dictated text is
factually wrong" defect** as well. Enumerated trigger met, independently.

### Ground 3 — the classification is moot, because Q4 is itself an enumerated trigger

*"any proposed process rule"* is enumerated in rule 11's mandatory list. Q4 of this packet **is** a
proposed process rule, and Q3's magistrate candidate is one in substance. So the cold gate is
mandatory for this packet on its face, whether F-N4 is classified (a) or (b). A magistrate-assembled
peer consult, however good, is not the cold gate: rule 11's cold gate is a **cold Fable instance,
fresh session, no loop context, on a mechanically-assembled packet, paired with an Opus contract-lens
refuter**. I am the Opus half. Whether the cold Fable half is present I cannot know under the
blindness rule; if it is not, the gate is not constituted.

### What (a) means operationally

Not "stop the branch." It means: **round 4's text does not land on a magistrate-only decision.** The
sequence I would hold to is —

1. Re-assemble the packet mechanically (A4), and add F-N5/F-N6 to it — they change what round 4 must
   fix and they falsify the packet's own §2 premise.
2. Cold Fable + this Opus lens rule on the re-assembled packet.
3. Round 4 lands under the cold gate's ruling, with a **delta re-audit that executes refusals**
   (§4), not one that cites lines.

I will state plainly that (a) is the answer **inconvenient** for the branch, which is why I checked
it hardest: the honest steelman for (b) is Ground-1-only, and Ground 2 defeats it on bench evidence
that did not exist when the packet was written.

---

## §3. Q2 — cure for the paragraph

Both candidates fail. I write a third (Cure C) below.

### Cure A — delete the upstream vocabulary

Proposed text (packet §3): *"Bundle loading authenticates the launch lineage before any evidence row
exists: it replays the consumed arm and resolves EVERY path recorded at arming time — the pack root
among them — strictly, so a bundle whose arming-time paths no longer exist is refused at input
loading with a launch-lineage reason code and never reaches this gate (`inputs.py` `_read_bundle`;
`arm_readiness.py` `_replay_consumed_arm`)."* — plus the retained sentences.

**First-use table — Cure A**

| Term | built / glossed / deleted | Where — verdict |
|---|---|---|
| `bundle loading` | compositional | PASS — plain English + code cite at end of sentence |
| `launch lineage` | **built** | `:584` `**Launch lineage**` — PASS **[BENCH B4]** |
| `evidence row` | **none** | first use `:610`, defined nowhere **[BENCH]** — **FAIL** |
| `replays` | **none** | undefined technical verb; and A6 shows the code's two meanings diverge, with the weaker one applying here — **FAIL (and factually over-strong)** |
| `consumed arm` | glossed by proxy | `:584` "consumed arm authorization" — marginal PASS |
| `EVERY path recorded at arming time` | **none, and false** | **[BENCH]** the launch manifest, window environment, window chain and window root come from the **consumption receipt / launch manifest** (`CONSUMPTION_RECEIPT_KEYS` `:694–697`; `manifest["window_plan_root"]` `:10200`), written at **launch** time, not arm time; only the pack root is arm-time (`_pack_record` `:5242`) — **FAIL on fact** |
| `arming time` / `arming-time` | **none** | never defined; **[BENCH B4]** the exact string "arming time" does not occur anywhere in the contract — **FAIL** |
| `the pack root` | glossed | `:492` "campaign-pack directory (the pack root)" precedes `:611` — PASS *for this paragraph* |
| `strictly` | **none, and false** | `resolve(strict=True)` for pack root/manifest/window root, but the consumption receipt is `resolve(strict=False)` then read (`:8963`), and lifecycle receipts are `read_bytes()` first and resolved only after success (`:9797, :9811`) — **FAIL** |
| `a launch-lineage reason code` | **none** | no such class is defined in this contract; §7's refusal table (`:755–760`) lists five `readiness_identity_*` codes and none of the seven launch-lineage codes — the reader cannot enumerate or even locate them — **FAIL** |
| `input loading` | compositional + cite | marginal PASS |
| `this gate` | built | `:599` "The analysis input gate" — PASS |
| `consumer_identity_set_unauthenticated` (retained sentence) | **none at first use** | first use `:620`, meaning at `:634` **[BENCH B4]** — **FAIL, and Cure A explicitly keeps it** |

**Verdict on Cure A: do not land.** It removes all six of the packet's listed items and introduces
**three new unbuilt terms, two of which are factually false** (`EVERY path recorded at arming time`;
`strictly`), retains two more (`replays`, `evidence row`), and leaves the seventh (A2) untouched. It
also **loses information the contract needs**: after Cure A a reader cannot tell *which* artifacts are
authenticated (the S3 ruling (d)'s whole point was that the limitation is *layer-wide*, not
pack-root-only) nor *which* code they will see. Against the replication bar it is a regression, not a
cure. And its stated rationale is built on A1's false premise.

### Cure B — gloss at first use

**First-use table — Cure B**

| Term | built / glossed / deleted | Where — verdict |
|---|---|---|
| `consumption receipt` | glossed inline | gloss is well-formed *in isolation*, but **A3**: the identical object is bold-defined at `:672` as `**one-use consumption record**`, and the gloss reuses that definition's exact words without reconciling the names — **FAIL on ONE-home / synonym collision** |
| `launch manifest` | glossed inline **+ forward ref** | duplicates the bold definition already at `:671–672` verbatim. Two definitions of one term in one document — **FAIL (maintenance hazard; the right move is to relocate, not duplicate)** |
| `window root` | glossed inline | gloss: *"the directory the window's evidence is written under"* — **UNPROVEN and probably wrong**. **[BENCH]** the value is `manifest["window_plan_root"]` (`:10200`), and what the code requires under it is `window.env` and `window-chain.zsh` (`:10206–10216`), i.e. the window's **plan/launch** root. The bundle's own locator is resolved from `bundle_path.parent` (`:10657`), not from this root. — **FAIL until proven** |
| `lifecycle receipts` | glossed inline | *"the per-stage records written as the window runs"* — directionally right but not replication-grade: the stages are **named** in code (`launch_start`, `launch_settle`, `launch_completion`, `:10236, :10246, :10312`) and the bundle path runs with `require_completion=False` (`inputs.py:2776`). "per-stage" is itself an unbuilt term — **PARTIAL FAIL** |
| `launch_binding_mismatch` / `launch_consumption_missing` | glossed inline | gloss: *"the reason codes bundle loading emits when the replayed lineage does not resolve / when the consumption receipt itself is gone"* — **factually wrong per F-N5 [BENCH B5]**: the launch manifest emits `launch_consumption_invalid` and lifecycle receipts emit `launch_lifecycle_incomplete`. Cure B **restates the very error F-N5 identifies, in more confident words** — **FAIL** |
| `replays` / `evidence row` / `strictly` | untouched | Cure B keeps the surrounding sentence — **FAIL (A6, A2)** |
| `consumer_identity_set_unauthenticated` | untouched | **FAIL (A2)** |

**Verdict on Cure B: do not land.** The packet's own stated cost is the accurate objection —
*"every gloss is a new factual claim that must be PROVEN"* — and I can already show **two of the five
glosses are wrong or unproven** before a seat has touched them. Cure B converts one pedagogy defect
into four new factual claims and would, on this branch's demonstrated track record, produce round 5.
Its stated cost ("~6 lines") is also understated: with the F-N5 correction the code enumeration alone
runs to five artifacts and three codes.

### Cure C — use the vocabulary block the contract already has, and stop enumerating codes

Neither candidate noticed the cheapest fact in the file: **`:580–594` is already a defined-terms
bullet block, immediately above §Analysis consumption**, and it already carries `**U8**`, `**U11**`,
`**Launch lineage**`, `**exact-cell route**`, `**Condition-family transport**`, `**transport
group**` **[BENCH B2]**. The contract's own established ONE home for this section's vocabulary sits
sixteen lines above the paragraph that violates first use.

So Cure C does not delete the vocabulary (Cure A) and does not mint new glosses in running prose
(Cure B). It **puts the terms where this document already puts terms**, and it moves the two
definitions that already exist rather than duplicating them.

**Cure C, part 1 — add to the `:580–594` bullet block** (each bullet is one factual claim with one
proving line, verifiable clause-by-clause):

> - The **arm receipt** is the U8 record that authorized this launch; among other things it records
>   the pack's **pack root** — the absolute filesystem path of the campaign-pack directory on the
>   machine that armed it (`arm_readiness.py` `_pack_record`).
> - The **one-use consumption record** (called the consumption receipt in code) is the durable proof
>   that one arm authorization was spent exactly once. It names, by absolute path and SHA-256, the
>   **launch manifest** — the JSON declaration of the reviewed command and its inputs — and the
>   window's environment and chain files (`arm_readiness.py` `CONSUMPTION_RECEIPT_KEYS`,
>   `validate_consumption_receipt`). It does **not** record a pack root of its own.
> - The **window plan root** is the directory named by the launch manifest's `window_plan_root`; the
>   window's `window.env` and `window-chain.zsh` must resolve directly under it
>   (`arm_readiness.py` `authenticate_launch_lineage`).
> - The **lifecycle receipts** are the `launch_start`, `launch_settle` and `launch_completion`
>   records written as the window runs; bundle loading requires start and settle, and requires
>   completion only when the caller asks for it (`arm_readiness.py` `_read_lifecycle_receipt`,
>   `authenticate_launch_lineage`).
> - The **launch-lineage reason codes** are the seven refusal labels of the launch-lineage layer
>   (`arm_readiness.LAUNCH_LINEAGE_REASON_CODES`). They are a different vocabulary from section 7's
>   refusal table, which governs only the bytes of a U11 receipt.

**Cure C, part 2 — the paragraph at `:609–621` becomes:**

> That root is the pack root the **arm receipt** recorded; the one-use consumption record carries no
> pack root of its own, and replaying the consumption is what recovers it. Bundle loading
> authenticates the launch lineage before this gate runs: for every registered bundle, `_read_bundle`
> re-reads the consumed arm receipt, re-authenticates the pack it names, and requires every absolute
> path the lineage records — the pack root, the one-use consumption record, the launch manifest, the
> window plan root and the lifecycle receipts — to still resolve to the same bytes it recorded
> (`joulewise/analysis_engine/inputs.py` `_read_bundle` →
> `joulewise/arm_readiness.py` `authenticate_bundle_launch_lineage`). It does not re-derive the arm's
> own PASS/GO decision on this path. If any of those paths no longer resolves, input loading raises
> with the launch-lineage reason code belonging to the artifact that failed and the whole analysis
> input set is refused; the bundle never reaches this gate. Analysis of successor-lineage bundles
> therefore runs on the filesystem that armed them; making the lineage relocatable is a separate
> design lane, not a property of this gate. Called directly — bypassing bundle loading — with a
> lineage whose pack root does not resolve, this gate refuses with
> `consumer_identity_set_unauthenticated`, defined below as the label for any pack this gate cannot
> authenticate.

**First-use table — Cure C**

| Term | built / glossed / deleted | Where — verdict |
|---|---|---|
| `arm receipt` | **built** | new bullet, `:~585`, precedes use at `:609` — PASS |
| `pack root` | **built** | new bullet; also pre-glossed at `:492` — PASS |
| `one-use consumption record` | **built** | new bullet; the code name "consumption receipt" is named in the same bullet, closing **A3** — PASS |
| `launch manifest` | **built** | definition **relocated** from `:671` into the bullet; `:671` keeps the bold mark only if it is demoted to plain text — PASS, no duplication |
| `window plan root` | **built** | new bullet, and it uses the **code's own name** (`window_plan_root`) instead of the invented "window root" — PASS |
| `lifecycle receipts` | **built** | new bullet, with the three stage names — PASS |
| `launch-lineage reason code` | **built** | new bullet, with the owning frozenset **and** the disambiguation from §7's table — PASS, and closes the §7 reader-trap |
| `launch lineage` | built | pre-existing `:584` — PASS |
| `evidence row` | **deleted** | replaced by "before this gate runs" / "for every registered bundle" — closes **A5** and **A2** |
| `replays` | **deleted** | replaced by "re-reads … re-authenticates … does not re-derive the arm's own PASS/GO decision" — closes **A6**, and the negative clause is the replication-grade half |
| `strictly` | **deleted** | replaced by "still resolve to the same bytes it recorded", which is **[BENCH]** true for all five (digest comparison at `:9024–9026`, `:10133–10136`, `:10240–10243`, `:10250–10253`, and the pack digest via `_pack_record`) — closes the Cure-A `strictly` failure |
| `arming time` | **deleted** | replaced by "every absolute path the lineage records", which is provenance-neutral and true — closes the Cure-A fact failure |
| two specific reason codes | **deleted** | replaced by "the launch-lineage reason code belonging to the artifact that failed" — closes **F-N5** without requiring the contract to maintain a five-row code map that will drift |
| `consumer_identity_set_unauthenticated` | **forward-ref made explicit** | "defined below as…" — the honest minimum; a full fix would move `:634`'s sentence up, which I do not recommend (it would break the numbered-step structure) — PASS |

**Cost of Cure C:** five bullets (~13 lines), a paragraph rewrite of similar length to the current
one, and demoting two bold marks at `:671–672` to plain text with a back-reference. Every new
sentence is a factual claim with a named proving callable, and — this is the point — **each one is
provable by executing a refusal, not by citing a line** (§4).

**Recommendation: land Cure C, not A and not B.** But land it under the cold gate (§2), and land it
in the same round as the F-N5/F-N6 corrections, because Cure C already contains them.

---

## §4. Q3 — the fourth formulation

### First: I ran the magistrate's candidate on the current paragraph. **[BENCH B4]**

**Would it have caught F-N4? YES — all six items, plus a seventh.** The output in §0 B4 flags
`consumption receipt` (no def), `window root` (no def), `lifecycle receipt` (no def),
`launch_binding_mismatch` (no def), `launch_consumption_missing` (no def), `launch manifest`
(def at 671 > first use at 612), and additionally `consumer_identity_set_unauthenticated`
(620 vs 634) and `evidence row` (610, none) — the two the packet and terra both missed.

**But the rule as stated is not well-formed.** Running it surfaced four concrete failure modes:

1. **Case sensitivity.** My grep for `**launch lineage**` returned NONE and the rule flagged it — but
   `**Launch lineage**` is defined at `:584`. A false positive on a correctly-defined term.
2. **Hyphenation.** The paragraph writes `arming-time`; the rule's noun phrase is `arming time`;
   `grep` returned `NONE` for both first use and definition, i.e. the term silently **fell out of the
   table entirely**. A false *negative* — the worst kind for a gate.
3. **Aliases / synonyms.** `pack root` first-uses at `:464` and is glossed at `:492` — the rule flags
   it as a violation, though `**campaign pack**` is defined at `:34` and `:492` names them the same
   thing. This is precisely how Sol 266's human table passed it: file 34's row reads
   `campaign pack / pack root | 34 | 34–35`, silently conflating two surface strings. The rule and
   the human fail in opposite directions, and neither states the alias.
4. **Scope.** The rule as written runs over "the new text" but greps "the contract", so it flags
   long-standing vocabulary (`pack root`, `input loading`). A writer facing a table where most rows
   are pre-existing noise learns to wave rows through — which is exactly the disposition that
   produced the omission in file 34.

**Amendments required for well-formedness (all mechanical):**

- **(i) Diff-scoped.** Build the candidate-term list from `git diff -U0` **added lines only**, plus
  any term whose first-use line *moved earlier* because of the diff. Pre-existing terms go in a
  separate, explicitly-labelled "pre-existing, not this edit" section that the verifier ignores.
- **(ii) Normalized matching.** Case-insensitive; hyphen ≡ space ≡ nothing; singular ≡ plural. One
  `sed` normalization pass over both the term and the file.
- **(iii) Declared alias register.** The writer states aliases explicitly
  (`pack root ≡ campaign pack, :34`) as table rows. A conflation that is *stated* is auditable; a
  conflation that is silent is what happened in file 34.
- **(iv) Mechanical definition test.** A "definition" is exactly one of: a bold-marked term
  (`\*\*term\*\*`), or a parenthetical gloss on the same or the preceding line
  (`term[^.]*\(…\)`). Anything else counts as NOT defined. No judgment calls.

### Would it have caught S1? **No** — and the packet is right about that. Here is what would.

S1, F-N5 and F-N6 are **behavioural** claims: an ordering ("before any configuration is read"), a
reason code ("`launch_binding_mismatch`"), a provenance ("recorded when the arm was consumed"). A
first-use table cannot touch them, and — this is the finding — **neither can a clause table.**

Diagnose the round-3 failure precisely. Sol 266's R3-C clause table (file 34) has ten rows. Every row
is true:

| Sol's row | True? | But the sentence asserts… |
|---|---|---|
| "Recorded pack root resolves strictly → `9333-9352`" | ✅ | …and that *all four other artifacts* refuse with the same code |
| "Launch manifest resolves/authenticates → `8996-9028, 10187-10192, 10222`" | ✅ | …and that its failure is `launch_binding_mismatch` (**it is `launch_consumption_invalid`**) |
| "Lifecycle receipts resolve/authenticate → `10233-10252, 9794-9811`" | ✅ | …and that their failure is `launch_binding_mismatch` (**it is `launch_lifecycle_incomplete`**) |
| "**Arm** records an absolute pack root → `5242-5259`" | ✅ | …but the sentence says the **consumption** recorded it |

**The clause decomposition dropped the sentence's quantifier and its binding.** Each clause is a
sub-proposition that the sentence *entails*; none of them is the proposition the sentence *asserts*.
A file:line cite can prove "this code path exists"; it structurally **cannot** prove "and this is the
only code path, and it emits this label."

### The fourth formulation — change the axis, not the author

Three formulations have failed. Look at what varied:

| Round | What was varied | Outcome |
|---|---|---|
| 1 | seat writes the prose | failed |
| 2 | seat writes it, brief adds first-use guidance | failed |
| 3 | **magistrate** dictates it, seat verifies clause-by-clause | failed (twice: S1 pre-landing, F-N4+F-N5+F-N6 post-landing) |

**All three moved the same dial: authorship.** The standing escalation trigger says two same-signature
rounds are "evidence of a structural problem" — the structure is that **authorship was never the
cause.** A fourth authorship variant (a cold seat writes it, two seats write it, etc.) is round 4 of
the same experiment. Do not run it.

**Formulation 4 varies what counts as PROOF, and splits prose clauses into two kinds with two
different proof obligations:**

- **Vocabulary clauses** (does this term have a meaning before it is used?) → the **diff-scoped
  mechanical first-use table** with amendments (i)–(iv), built by the writer BEFORE landing, pasted
  under Executed evidence, and **independently re-derived** by the verifying seat from the diff, not
  read from the writer's table.
- **Behavioural clauses** (an order, a refusal label, a provenance, a "before/after", a "never/only")
  → **an EXECUTED probe, pasted verbatim, with its counterfactual.** A file:line cite is not
  admissible proof of a behavioural clause. My §0 B5 is the shape: four lines of Python, one command,
  and it falsifies a sentence that two auditors passed. The rule is the prose analogue of the
  standing memory rule *"fix-round briefs must name the counterfactual input + production call site;
  today's-artifact cures kill nothing"* — a proving line is a today's-artifact cure for prose.

**Mechanical trigger for "this is a behavioural clause"** (so the writer cannot judge its way out):
the sentence contains a backticked reason code or identifier, **or** any of
`before | after | first | then | only | never | always | every | all | each | strictly | exactly`.
The R3-C paragraph fires on `before`, `strictly`, `every`, and two backticked codes.

**Would formulation 4 have caught everything?**

| Defect | Caught by | How |
|---|---|---|
| F-N (round 1, code order) | behavioural probe | `before/then` trigger → execute the ordering |
| F2 (round 2, first use) | first-use table | diff-scoped, would flag |
| S1 (round 3, "before any configuration is read") | behavioural probe | `before` trigger → the probe that files 30–31 actually ran |
| F-N4 (first use ×7) | first-use table | **[BENCH B4]** demonstrated above |
| **F-N5** (reason codes) | behavioural probe | **[BENCH B5]** demonstrated above — one command |
| **F-N6** (provenance) | behavioural probe | `CONSUMPTION_RECEIPT_KEYS` has no `pack_root` — one grep |

That is the first formulation that covers all six. It is also the first one that would have been
**cheaper** than the round it prevents: B4 and B5 together are two commands and about five minutes.

---

## §5. Q4 — the proposed process rule

**Position: the pre-landing first-use table should become mandatory for contract-prose edits — but
only in the amended form (i)–(iv), and only if it ships PAIRED with the executed-behavioural-clause
rule. Shipped alone it is actively dangerous.**

Why "dangerous" and not merely "insufficient": a first-use-table-only gate would have passed the
current paragraph on F-N5 and F-N6 and produced a *green* pre-landing record for text that is
factually wrong in two places. Adding a green gate that cannot see the defect class that has failed
three times out of four rounds would make the record read cleaner while the defect persists. That is
the "eaten trigger" pattern with better paperwork.

Rule 11 routing: I am not installing this, and neither should the magistrate. It is an enumerated
mandatory cold-gate trigger, and its destination is Ed.

### Cost per edit (measured, not estimated)

| Component | Writer | Verifier | Evidence |
|---|---|---|---|
| Diff-scoped first-use table | 1 command (B4 shape) + ~5 min to read the rows | ~5 min to re-derive from the diff | I built the full table for this paragraph in one shell loop |
| Executed behavioural probes | ~10 min per triggered clause; the R3-C paragraph has 4 | ~5 min to re-run the pasted commands | B5 covered all four in one 12-line script |
| **Total, prose edit with behavioural clauses** | **~45 min** | **~10 min** | |
| **Total, prose edit with none** | **~5 min** | **~5 min** | |

Against a fix round (implement + audit + delta re-audit + consult) this is well under 5%, and this
section alone has now spent **four** of them.

### Two-session drop test (rule 5)

Rule 5: *"a layer with zero unique catches over two sessions is dropped."* Attached as follows, with
one addition rule 5 does not currently make explicit and which this session shows is needed.

1. **Primary metric — unique pre-landing catches.** Per session containing at least one contract-prose
   edit, record the count of defects the gate caught **that the post-landing audit did not
   independently find**. A catch the delta re-audit would have made anyway is not unique to the gate.
2. **Drop condition.** Zero unique catches across **two consecutive qualifying sessions** → drop the
   layer, recorded in the council log with the two session IDs.
3. **Qualifying-session floor.** A session with no contract-prose edit does not count toward the two.
   Otherwise a quiet fortnight silently retires a working gate.
4. **Added: a noise-rate condition (this is the one rule 5 lacks).** Also record, per session, the
   ratio of table rows marked *"pre-existing / waived"* to rows flagged as new. If that ratio exceeds
   **2:1 across two consecutive qualifying sessions**, the gate is not dropped — the **scoping
   amendment (i) has failed** and must be re-cut before the gate is trusted. This condition exists
   because file 34 is direct evidence that a writer facing a noisy vocabulary table will wave rows
   through, and a waved-through gate scores zero unique catches for the wrong reason and would be
   dropped on metric 1 when the defect is in the gate's *scoping*, not its *value*.
5. **Instrument the pair separately.** The vocabulary half and the behavioural half get separate catch
   counts. On this session's evidence the behavioural half caught 2 unique defects (F-N5, F-N6) that
   two seats and a clause table missed, and the vocabulary half caught 2 unique (A2's seventh and
   eighth terms) beyond what terra found. Both start non-zero.

---

## §6. Summary of what I would tell the magistrate

1. **Q1 = (a)**, on three independent grounds; and it is moot anyway because Q4 is itself an
   enumerated cold-gate trigger. The cold gate is mandatory for this packet.
2. **The packet's §2 premise is false [BENCH]**: the factual class was **not** fixed. F-N5 (reason
   codes) and F-N6 (pack-root provenance) are live factual defects in the landed round-3 text, missed
   by Sol 266's clause table and by terra 267.
3. **Neither cure is landable.** Cure A introduces two false statements and loses information;
   Cure B restates F-N5's error in more confident words and duplicates an existing definition.
4. **Cure C** uses the contract's own `:580–594` defined-terms block, relocates the two definitions
   that already exist rather than duplicating them, deletes `replays` / `strictly` / `arming time`
   as unbuilt, and stops enumerating reason codes — closing F-N4, F-N5, F-N6 and A2–A6 in one edit.
5. **Round 4 must not be another authorship variant.** All three failed formulations moved the same
   dial. Change what counts as proof: mechanical diff-scoped first-use tables for vocabulary,
   **executed refusal probes** for behavioural clauses. A file:line cite cannot prove a reason-code
   claim; §0 B5 shows one command falsifying a sentence two auditors passed.
6. **Q4 yes, paired, never alone**, routed to Ed via the cold gate, with a two-session drop test that
   adds a noise-rate condition rule 5 currently lacks.
