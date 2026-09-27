# SWEEPCLASS-SAMESIG-01: paired Opus 5.5 contract-lens refuter

Tree: `/Users/edr/code/JouleWise-wt-samesig-sol-3ba66eeb` @ `315364b2` (detached, `git status --short` = 0 lines after every probe). Scratch `/tmp/samesig-refuter-3ba66eeb/`. Contamination: the harness loaded Ed's CLAUDE files and memory index; I used only D-161 and the 09-24 goal as the charge states them.

## SECTION A (written 03:28-03:31 PDT, BEFORE the ruling; `21-coldgate-fable-ruling.md` did NOT exist at 03:27:40)

**Executed evidence**
| Id | Probe | Output |
|---|---|---|
| A1 | `python -B -m unittest tests.test_bfgs_consumer_sweep -v` | 1 FAIL / 3: unlisted `('scripts/run_campaign.py','evaluate_member','direct:read_text')` (lines 2824, 2833); stale `('scripts/run_campaign.py','run_axi_spec_campaign','direct:read_bytes')` |
| A2 | `git diff 21213be7 cbfa9dc3 -- scripts/run_campaign.py`; `git diff cbfa9dc3 315364b2 -- scripts/run_campaign.py tests/test_bfgs_consumer_sweep.py` | Cause is S1's own fix round 3 (`cbfa9dc3`), not the main merge (both files identical across the merge): it **removed** `authenticate_window_members(((bundle_dir.name, bundle_dir),))` from `evaluate_member` (row appears) and **added** a window gate at `run_axi_spec_campaign:7848` (the pre-51 detector's "any gate anywhere in the function" rule then hides the `metadata.json` read at `:7686`, which precedes that gate) |
| A3 | Opus `p4.py` (sha `ae8e23ce`) and `p1.py` (`41d207a0`) re-run on this tree | 100 watched call sites, **0 in unvisited scopes** (B-1 closure is GREEN today); lambda / def-under-if / def-under-try / `__main__` call / `__main__` open / `map(lambda…)`: all SILENT; control reported. 103 `__main__` blocks, 51 compound-nested defs, 274 lambdas |
| A4 | `q1_dominance.py` (`ad1d4e0f`): enclosing branches in `run_axi_spec_campaign` | gate `:7848` sits in `If@7837` (`policy_binding is not None`); consumers `_idle_admission_core_evaluation :8047` and `classify_campaign_members :8115` sit in a **different** `If@8018` (same condition; `policy_binding` is a parameter, never reassigned) |
| A5 | `git ls-files '*.py'` by top dir; grep of `docs/paper/**.py` | 136 tracked `.py` under `docs/` outside the sweep's `joulewise/`+`scripts/` scope; `docs/paper/figures/reproduce_worked_examples.py:113` does `(path/'power_trace.csv').read_bytes()` and `:46` digests all four bundle files, feeding `worked-examples.json` (a paper exhibit). Today it is digest-pinned to a pre-directive corpus (historical-shaped, no leak) |
| A6 | `tests/test_bundle_read.py:560-579` protected list | `reduce.py`, `bundle.py`, `battery_float.py`, `powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `paper_excursion_decomposition.py`, `paper_anchor_correction_quantified.py`, `render_results_fills.py` (+ tests). **`bundle_read.py`, `envelope_gate.py`, `run_campaign.py` are not frozen** |

**1. Q1-Q2.** Adopt the consensus: an exhaustive static guarantee is not closable; same rule-11 signature (RSW-2 `_cache` -> B-3 `_path`; RSW-3 name rebinding -> B-2 behaviour patch; RSW-1 alias -> B-5 reference). Narrowed promise I would write: *"On tracked Python the sweep reports every call of a tolerant accessor and every call receiving a path expression to a watched name or raw capture, in every scope of the file, whose function (or lambda) is not dominated by a gate call; the reported set must equal the allowlist. It guarantees nothing against code that alters the gate's objects or bindings at run time, builds names or code at run time, or reads a file without naming it; those forms are listed in 51 (h)."* The promise must also state its **file scope** (A5): either widen it to every tracked `.py` outside `tests/` and `docs/process_traces/` (adds `docs/paper/**`, `configs/**`), or name the exclusion in 51 (h). I prefer widening: paper-figure scripts are the most likely place for a future accidental claim read.

**2. B-1..B-9.** B-1 close (every scope; lambda bodies never gated). B-5 close (references count, both caller checks). B-2 limitation (deliberate: stores into `battery_float`/`bundle_read`, `type()` subclasses). B-3 limitation for the static sweep; optional runtime path binding. B-4 production edit (below). B-6 take (regex widening, report count). B-7 take (wording). B-8 take. B-9 moot if B-4 is the production edit.

**3. B-3/B-4.** B-3: D-161 limitation; the ~6-line path binding in `BundleReader.metadata` is optional, own lane, not blocking. B-4: the two-line behaviour-identical `reader.metadata()` edit in `envelope_gate.py` (not frozen, A6), in S1's round-3 WRITE_SCOPE before the allowlist closes, because it is the only way the rows carry a true class; otherwise an explicit cold-gate exception with a true reason.

**4. Inventory failure.** Neither key may be accepted blindly. `evaluate_member` already has a ruled class: 51 (g) 3, `behind_gate` consumers form, `consumers = ((run_campaign, classify_campaign_members), (run_axi_spec_campaign, _idle_admission_core_evaluation))`. **But A4 shows that the consumers form FAILS 51 (d)'s own dominance rule in `run_axi_spec_campaign`**: the gate is in `If@7837`, the consumers in `If@8018`. The seat will hit this. Remedies: (a) behaviour-identical restructure so one `if policy_binding is not None:` encloses both gate and consumers (do **not** move the gate below `validate_attempt_ledger`/`_axi_discover_finalized_bundles`, which would put selection before authentication and break a kept invariant); or (b) a cold-gate named exception. The "stale" `run_axi_spec_campaign :7686` read does not vanish under 51: it precedes the gate and returns as a reported row; its content is `batch.admitted_request_count` only -> `non_claim` (i). Also: the consumers form, unlike the callers form, does not require that **every call** of the helper lie in a listed function; a new caller of `evaluate_member` that uses `.summary` elsewhere is silent (B-5's class, accidental). Add that clause.

**5. Fix round 3 order.** (1) Narrowed 51 promise + file scope; (2) 51 (a)-(e) detector with B-1 scopes and B-5 references; (3) 57-60 as ruled; (4) consumers form gains the all-callers clause; A4 remedy; (5) envelope two-line edit; (6) B-6/B-7/B-8; (7) allowlist recomputed and every row classed, count reported; (8) V1/V2. Stop: exact head has no ungated claim read, no false class, suite green, named mutation matrix RED->GREEN; any new form requiring the deliberate grammar is a 51 (h) line, not a round.

**6. Gated `summary()`.** Own lane, SHOULD-FIX, non-blocking for S1; it is the structural cure and the pre-committed next spend if B-1/B-5 fail again.

**Section A tiers:** BLOCKER (merge) the red sweep (A1). SHOULD-FIX: consumers-form dominance failure (A4); consumers form lacks all-callers clause; file scope excludes `docs/paper/**` (A5). No current leak found.

## SECTION B (ruling file appeared 03:45; read in full at 03:46-03:48, 65181 bytes, 505 lines, sha256 prefix `71b1c570e5226b1e`; Section A unchanged)

**Agreement first.** The ruling independently reached A's two main code facts: the inventory mechanism (its Z2 = my A2) and the consumers-form dominance failure (its Z9 = my A4). Its rule (d) 6 is the narrow, sound fix, with four counterfactuals. Its Z8 correction is right: the consensus inline `reader.metadata()` edit leaves both envelope rows reported, because at both sites `reader` is a loop variable; my Section A B-4 answer inherited that error. The helper of amendment 63 is the better edit. I also accept: B-2/B-3 as limitations, the B-3 runtime lane after merge, one refuter pass, and the gated-`summary()` lane.

**New executed evidence (Section B)**
| Id | Probe | Output |
|---|---|---|
| B1 | `q2_docs_scope.py` (`afc032c8`): the first judge's prototype `sweep59` over the 27 tracked `.py` files under `docs/paper` and `configs` | 2 rows, both in `docs/paper/figures/reproduce_worked_examples.py`: `historical … power_trace.csv :113`, `synthetic … power_trace.csv :47` |
| B2 | read `run_campaign.py:3983-4005, 4012-4031, 4048-4080, 8900-8910, 6649-6664, 515-523`, `campaign_cooldown_before_member` (anchor branch), `campaign_provenance.py:1040-1090`, `bundle_read.py:342-354` | see F1 |
| B3 | AST count: private names imported from `joulewise` modules into `joulewise/`+`scripts/` | 89 imports in 32 files; plus `scripts/build_battery_float_historical_bundles.py:245` calls `BundleReader(bundle)._strict_json("metadata.json")` |

### F1. BLOCKER (for merge, under the ruling's own A2/A3). Reading, NOT EXECUTED end to end. The consumers-form row of 64 (b) holds against its own condition: `evaluate_member`'s result is consumed **before** the gate, and one consumer persists an energy-class value past every gate.
- 51 (f) defines the consumers form as being "for a function that runs during collection and whose result is used only later". At this tree the result is also used **during** collection, before either gate:
  - `_first_eligible_cooldown_anchor(evaluations, …)` runs at `run_campaign:8900` and `run_axi_spec_campaign:7817`. Through `_anchor_from_evaluation` (`:3983`) it freezes `"baseline": evaluation.summary["idle_baseline"]`, an idle **power** baseline.
  - `cooldown_reference_eligibility` (`:3933`) checks idle-window, environment and policy provenance, and **no battery status**.
- The anchor is written to campaign provenance at `:8908-8910`. That write comes before the window gate at `:9032`.
- A later campaign with the same analysis manifest takes it as its frozen anchor through `prior_campaign_cooldown_anchor` (`:7408`, `:8350`). The catalog loader (`campaign_provenance.py:1040`) authenticates custody only. It has no verdict or battery filter.
- The later campaign's window gate covers only its **own** members (`:9021-9032`), so the anchor's source bundle is never battery-checked there.
- The anchor's baseline becomes the cooldown reference (`note["reference_selection"] = "frozen_clean_anchor"`). The note, with `anchor_provenance` (baseline included), is stored as `MemberEvaluation.preceding_campaign_cooldown`. That field is written into each member's verdict row (`:522-523`) and decides the admission reasons `cooldown_cap_hit` and `campaign_cooldown_evidence_missing` (`:6649-6664`).
- Result: a power value from a bundle never authenticated for that window reaches a whole-window verdict row (a claim artifact by 51 (f)) and drives an **exclusion decision**. That also touches the kept invariant "authentication precedes every exclusion decision".
- Within one campaign the window gate refuses the whole window, so the only escape is across campaigns. The route predates S1 (at main `evaluate_member` held no gate either, per Z2).
- The sweep promise cannot see this: the watched name enters inside `evaluate_member`. 64 (b)'s named-call check passes.
- **Fix, for the judge to rule:**
  1. Step 11 (Returns) receives this row explicitly. The lead opens a lane (e.g. BFGS-COOLDOWN-ANCHOR-01) that authenticates the anchor's source bundle with `authenticate_window_members` at freezing time or at reuse. `run_campaign.py` is a consumer that already imports it, it is not frozen, and it needs no `battery_float` import.
  2. The lane blocks merge only if the lead's trace confirms the route, which is A3 as the ruling words it.
  3. 64 (b)'s reason states the collection-time consumers truthfully.
- **Counterfactual:** a probe campaign pair where campaign N-1's anchor bundle carries a `battery_float_confounded` pair and campaign N reuses the anchor. The verdict row of N holds N-1's baseline: RED on the tree, GREEN after the lane.

### F2. SHOULD-FIX. The consumers form has no closure over its callers. 62 (b) gave the callers form "every call and every reference"; the consumers form got nothing like it.
- 64 (b) checks only that each **named** consuming call is dominated by a gate. Suppose someone adds a call of `evaluate_member`/`evaluate_members` in another function, or a new campaign mode, and that code uses `.summary`. Nothing reports it: the watched name enters inside the helper, and the helper's rows are allowlisted.
- This is B-5's class (ordinary refactor), so it is supported-zone, not deliberate.
- **Text:** in 51 (f)'s consumers form add "and every call of, or reference to, the row's function (and, transitively, of any function in `joulewise/` or `scripts/` that returns its result, here `evaluate_members`) lies in a function named in `consumers`".
- **GREEN on the tree:** the ruling's Z11 finds `evaluate_member` called only in `evaluate_members`, `run_campaign` and `run_axi_spec_campaign`, with 0 non-callee references. My `git grep` shows `evaluate_members` called only in `run_campaign`.
- **Row R51-17b:** `scripts/zz_new.py` with `def f(p, i): return evaluate_member(p, info=i, waivers={}).summary`. The sweep fails, naming `f`. Counterfactual: 64 (b) as ruled.

### F3. SHOULD-FIX. The file scope omits paper-producing Python. 61 (a) "Not promised 4" names "the tests, a notebook, a shell command". It does not name `docs/paper/**`, where figure and worked-example scripts write paper exhibits (claim artifacts: "a figure").
- A future paper-figure script that reads post-directive bundles is the most natural accidental claim read outside the tree the sweep walks.
- **Cost (B1):** widening the scope to `docs/paper/**.py` and `configs/**.py` adds exactly 2 rows. Both are in a digest-pinned worked-example script: fixture sha asserted at `:33`, corpus stream sha asserted at `:114`. The scope clause of 51 (b) 2's "any tracked file under `joulewise/` or `scripts/`" and the caller checks widen with it.
- Both rows need `historical`. Under 51 (g) 4 that needs a cold gate's words, so the ruling should grant them or rule them `non_claim` (i)/(ii).
- **Minimum alternative:** name `docs/paper/**` in "Not promised 4".

### F4. SHOULD-FIX (the matrix leaves a ruled rule unpinned). 62 (a) says a read inside a `lambda` is **never gated** and "no scope inherits a gate". R51-23 to R51-26 use sources with **no gate at all**, so a detector that lets a lambda or nested def inherit the enclosing gate passes every row.
- **Add R51-23b:** `def f(r: BundleReader): r.metadata(); g = lambda: r.raw_summary(); return g()`, expected reported. The same shape with a nested `def` under `if`, expected reported in `f.inner`.
- Counterfactual: lambda and nested bodies inherit the enclosing scope's gate.
- GREEN on the tree: the ruling's Z5 finds 0 lambda read sites.

### F5. NIT. 61 (b) clause 1 counts **reads** of private attributes as deliberate. Private reads are routine here (B3: 89 private-name imports in 32 files; an outside `._strict_json` call). That contradicts §4.3's definition ("must reach into the gate's own machinery").
- **Narrow it to:** "writes or deletes a `_`-prefixed attribute, or reads `_cache`, `_path` or a name-mangled attribute of a `joulewise` object from outside its module".
- Supported-form reads that happen to call a private helper are still reported by 51 (b) 2, so no row moves.

### F6. NIT. Wording fixes.
- Rule (d) 6: say "bound by nothing … anywhere in the function, **nested scopes included** (`nonlocal` in a nested def counts)".
- R60-7 runs `git show 315364b2:…` inside a test. Give it R51-13's clause: `skipTest` if the commit is absent (shallow CI clones).
- 61 (c), row 1 of the table: name the route for an A3 tree failure whose fix is unruled production code. As in F1: return to the lead, its own lane, cold gate. Otherwise "no, unless…" has no owner.

**Frozen files and imports.** Neither ruled production change touches a frozen path. `envelope_gate.py` and `bundle_read.py` are absent from the pin list (A6; the ruling's Z16). Neither adds a `battery_float` import to the eight consumers; `envelope_gate.py` is not one of them. The ruling did not open FT §E itself (its §10). The pin test is the repository's operational copy, so I have no evidence of a conflict. **Kept invariants:** no contradiction in the ruled texts. F1 is a pre-existing tree route that bears on "authentication precedes every exclusion decision". It is not introduced by the ruling.

**Fix-round-3 list.** Ordered, self-contained given the three-document authority chain, and each new rule has rows and counterfactuals, except F4's gap. The stop predicate is finite: A1-A5, one refuter pass, and a rule-11 exit to BFGS-GATED-SUMMARY-01. Two changes are needed. Step 8/11 must carry F1 as an explicit return. F2's clause belongs in step 7.

**Section B counts:** BLOCKER 1 (F1; reading-based, needs the lead's trace), SHOULD-FIX 3 (F2, F3, F4), NIT 2 (F5, F6). Not executed: F1's campaign-pair probe; F2/F4 rows as mutations; the full suite. `git status --short` in my tree: 0 lines after every probe.
