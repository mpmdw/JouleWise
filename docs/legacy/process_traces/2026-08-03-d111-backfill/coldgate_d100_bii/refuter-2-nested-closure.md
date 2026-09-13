[Banked verbatim by the magistrate from the Opus contract-lens refuter's final message, 2026-08-02 late evening. Paired cold-instance ruling: cold-ruling-2-nested-closure.md. Synthesis: D-107.]

# Opus contract-lens refuter — Cold Gate, D100-BII-BINDING-01 clause 3(c) nested-content closure

## POSITION SUMMARY

The trigger fired, and on **stronger** grounds than the packet states — I prove by probe that formulation 1 was not "position-enumeration" at all but the *same key-denylist miss* as formulation 2, in the same function, differing only by one missing spelling (`generated_text` voided at the exact positions where `model_output` licensed at `a6ce7af`). I do not oppose the packet on Q1, Q4, or the *direction* of C-A. I **break C-A as written** on both axes. On the value axis it is not merely incomplete but demonstrably open: I license workload payloads through **four** grammar-legal string fields on the live code — `environment_admission.failure`, matched event/summary `failure_reason`, `events[].message`, and `summary_metrics.failure_message` — two of which are new (not in delta F1), and a simulation of C-A's stated predicate (closed key set + type per key) admits all four. A pure grammar does **not** close value substitution; only per-leaf closed value domains do, and I show they are derivable here. On the false-refusal axis the packet's "Established fact 2" (over-refusal clean) is **false**: the live fix-1 code refuses **769/769** real bundles and **3/3 of the actual window-B b-ii subject bundles**, and it does so for reasons the delta audit never traced (`guard_observations[].phase == "after_attempt_1"`, and `metadata.extra.node_cleanup`). Worse, and outside the packet's frame entirely: at the **merged, ratified-as-inert head `bc2ab19`** the license tool refuses all three real subjects at the *artifact-inventory* gate — an earlier closed-admission-grammar formulation derived from an 8-file hand fixture meeting 22-file producer reality. That is direct empirical proof of exactly the failure mode C-A would repeat one level deeper over 520 dotted paths, and it falsifies D-106 clause 3's operative premise that closing (a)–(d) unblocks window B. My ruling: the fence **does** reach the nested-content surface; the only distinction that licenses an allowlist is *decidability plus producer-set derivation verified against the governed corpus* (D-097's own evidentiary standard, which the packet's fact 1 does not meet); this must **not** proceed as a same-arc round 2 as scoped, because the row's acceptance criteria are unfalsifiable in the direction that has actually failed 3/3 and must be amended at the decision level.

---

## Reproduction preamble

All probes below run read-only. `WT` = `/private/tmp/claude-501/-Users-edr-code-JouleWise/c701f4e3-95c0-4f1b-a387-854cf845264f/scratchpad/d100bii`; `PY` = `/Users/edr/code/JouleWise/.venv/bin/python`. Historical revisions extracted with `git show <rev>:joulewise/salvage_dangler.py`. No file was modified; `git status` in the worktree is unchanged from the packet's stated three-file dirty set plus `BRIEF.md`.

---

## F-1 — BLOCKER (outside the packet's frame): the license tool refuses 3/3 real b-ii subjects at the *inventory* gate, at the merged head. D-106 clause 3's premise is false.

**Probe** (live worktree, and re-run against `bc2ab19` / `a6ce7af`): iterate `~/JouleWise-window-custody/window_metrologyB_20260801/quarantine`, call `inspect_salvage_attempt` on each bundle.

**Observed, all three subjects, on live / `a6ce7af` / `bc2ab19` alike:**

```
mtadd-p2048o0128-r08__20260801T131705Z REFUSED: unexpected salvage artifact inventory:
  unexpected instrument_calibration/events.jsonl, unexpected instrument_calibration/instrument_evidence.json,
  unexpected instrument_calibration/manifest.json, unexpected instrument_calibration/power_trace.csv,
  unexpected instrument_calibration/raw/powermetrics.plist, unexpected logs/controller.log, ...
mtadd-p2048o0128-r08__20260801T133315Z REFUSED: (same)
mtnull-o0512-b04-b2__20260801T113258Z  REFUSED: (same)
```

These are precisely the bundles named in `.desk/winB-closure-facts.md:10,13,17`. The real bundle carries **22 regular files** (including `logs/`, `raw/`, `instrument_calibration/`, `logs/custody/`); the tool's expected sets are `_REQUIRED_BUNDLE_FILES | {rich_telemetry.jsonl}` (compact) or that plus the idle telemetry names (complete) — **8 paths max** (`joulewise/salvage_dangler.py:34-40`, `:677-689`), compared by **exact set equality** at `:701`, over a **recursive** walk (`_enumerate_artifacts`, `:278`). Production reaches this through `authorize_salvage_dangler_exclusion` → `inspect_salvage_attempt(attempt_path)` at `:1312`, called from `scripts/run_campaign.py:4814`.

**Why this is a gate finding, not a bench fix.** (a) It is *pre-existing at the merged head* `bc2ab19` that D-106 clause 1 ratified as "INERT" — inert is true only in the vacuous sense that it licenses nothing at all, including every legitimate subject. (b) The kernel row's goal states window B "unblocks on this row"; it does not. Closing (a)–(d) exactly as ruled still leaves the license refusing 3/3. (c) It is the same defect class as clause (c): a **closed admission grammar derived from a hand-built fixture rather than from producer output**. The fixture (`tests/fixtures/salvage_dangler/r5a_idle_abort/`) has 6 files and no subdirectories; the producer emits 22 across four subtrees. This is empirical proof, already on disk, of C-A's principal risk — and it happened at depth 1 over 8 paths. C-A proposes the same construction at depth 7 over 520.

---

## F-2 — BLOCKER: C-A as written does **not** close the value-substitution attack. Four live channels, two of them new.

**A closed grammar without value classification leaves every string-typed field an exfiltration channel.** Probe A (live code, real payload through grammar-legal fields):

```
EA-failure-payload                 LICENSED=True
failure_reason-payload             LICENSED=True
event-message-payload              LICENSED=True     <- NEW, not in delta F1
summary.failure_message            LICENSED=True     <- NEW, not in delta F1
```

Channels 3 and 4 are **not** in the delta re-audit's F1 scenario list, so the packet's characterization of the surviving surface is incomplete. Their gates are pure type checks: `events[].message` at `joulewise/salvage_dangler.py:838` (`not isinstance(row["message"], str)`), `summary.failure_message` admitted non-null at `:203-212` with **no** value predicate anywhere, `summary.failure_reason` at `:922`.

Probe B — C-A's own predicate simulated exactly as the packet words it (closed key set per container + type per key): all four channels grammar-legal → workload bytes ADMITTED.

**Scorecard against delta F1's four sub-scenarios.** C-A closes two *by grammar alone* — the NFKC fullwidth key and unknown empty/scalar children. It fails the other two, plus my two new ones.

**What actually closes it, and it is available.** Every one of these four leaves has a *closed producer value domain* on the governed b-ii surface:

- `environment_admission.failure` — 7 literals: `joulewise/environment_admission.py:28,32,34,36,38` plus `controller.py:1001`, `:1054`, `:1077-1079`. Corpus attests 2 distinct values over 24 abort bundles.
- `events[failure].message` — same closed set. Producer: `controller.py:1444-1449`; the only other `idle_baseline` `_StageFailure` site (`controller.py:1013`) occurs **before** `decision` is set to `"abort"`, so a bundle passing the b-ii predicate cannot carry an adapter-free-text message. Corpus: 2 distinct values, 24/24.
- `failure_reason` (event metadata and summary) — `FailureReason` enum, `joulewise/schemas.py:257-266`; corpus: `{'unknown_error': 24}`.
- `summary.failure_message` — same closed set as `.failure`.

So the value axis is closable **without** any false-refusal cost. But it must be *ruled*, because C-A as drafted does not require it and a good-faith implementer reading "exact type/value constraint" as `isinstance(str)` ships all four channels open.

---

## F-3 — BLOCKER: "Established fact 2" (over-refusal clean) is false. 769/769 real bundles and 3/3 real subjects refuse.

Probe: run the fix-1 `_validate_nested_metadata_classification` over every `runs_window_*/**/metadata.json`.

**Observed:** `PASS 0  REFUSED 769`, single cause: `metadata.environment_admission.guard_observations[1].phase contains unclassifiable workload evidence`.

**Root cause:** `joulewise/salvage_dangler.py:542-549` treats `phase` as workload evidence unless its value is in `{run, validate, prepare, idle_baseline, launcher}` or starts with `before_attempt_`. The producer emits `after_attempt_N` too: `controller.py:1175`, appended at `controller.py:1169-1171`. Corpus census over 773 metadata files: `{'before_attempt_1': 770, 'after_attempt_1': 770, 'before_attempt_2': 73, 'after_attempt_2': 73}`. On the three real subjects all four phases are present → nested classification REFUSES.

This defect is **pre-existing** at `bc2ab19`/`a6ce7af` (`_contains_workload_evidence(metadata)` returns True 769/769). It means the packet's "Established fact 3" — the subjects' shapes are the governed grammar — is **false as stated and uncited** (the only established-fact item with no file:line). It re-leans on `winB-closure-facts.md`, the artifact D-106's overruling ground (1) called out.

**Second false refusal in the live diff:** `metadata.extra.node_cleanup`. The controller writes it on the salvage path — `controller.py:2155-2158` builds `node_cleanup` from `_adapter_cleanup_report(...)`, `:2164-2165` sets `controller_extra["node_cleanup"]`, `:2167` lands it as `metadata.extra`, invoked from the failure path at `controller.py:1467`. Three shipping adapters implement `cleanup_report` (`adapters/vllm_runtime.py:71`, `adapters/node_client.py:138`, `adapters/nvidia_smi.py:80`). `_validate_extra_metadata` (`salvage_dangler.py:587-592`) → **void**. The delta's exculpatory phrasing — "no seventh **runner-owned scalar** field was found" — is a double hedge that misses a **controller-owned, list-valued** seventh field; its three traced ranges do not include `2155-2167`.

---

## F-4 — Trigger (Q1): fired, and the packet's characterization of formulation 1 is wrong in a way that *strengthens* the trigger.

Probe (`a6ce7af` classifier, loaded directly): `env_admission.model_output` → False (licensed); `env_admission.generated_text` → True (voided); same through lists. `_contains_workload_evidence` at `a6ce7af:509-540` already recursed through mappings **and** lists. Formulation 1 was therefore **a key-denylist spelling miss**, not a positional gap — and the round-1 "fix" consisted of adding one spelling and hoisting the same predicate into a raising walk. The two formulations are **the same predicate, same function, same failure**, one spelling apart. Trigger fires, unopposed; the packet should be corrected on the record.

---

## F-5 — The fence (Q3): the strongest reading reaches the nested-content surface; the escape is decidability *plus corpus-verified writer-set derivation* — not polarity.

The fence's operative second clause — "no third schema-shaped formulation may be proposed" — is **unqualified**, and its cited authority is "D-106 clause 3 (fix-kind discrimination)", the general in-kind test. Clause 3's governing sentence — "These are different IN KIND from the two failed enumerations" — attaches to (a)–(d) collectively, including (c). A closed admission grammar over **520 distinct dotted paths at depth 7** (measured over the 24 real abort bundles) is an enumeration; calling it an allowlist inverts its polarity, not its kind. F-1 is the empirical demonstration: the already-shipped closed *inventory* allowlist converted false-admit into **100% false-refuse**.

**The distinction that survives, as a condition:** an allowlist enumeration is different in kind from a denylist enumeration **iff** (i) membership is decidable over a finite admitted set, **and** (ii) the admitted set is *derived from producer code and verified to contain every value emitted by the producer across the governed corpus* — D-097's own standard, met explicitly there ("verified: run_campaign.py emits only v1; ... zero v2 manifests across all 29 corpora", decision_log:5946-5948). A hand-derived allowlist satisfies (i) but not (ii), and (ii) is where this project has failed three times. Corollary: C-A's exactness posture is the one D-105 struck; C-C's superset form is nearer the ratified pattern.

---

## F-6 — F2 disposition (Q4): bound-and-refuse is sound, with two amendments. No false-refusal edge exists.

Measured producer depth: metadata max-depth {7: 769}; event metadata max 4. A bound at 32 leaves >4× headroom. Amendment 1 — refuse, never truncate. Amendment 2 — note the boundary: `scripts/run_campaign.py:4822` catches `(OSError, SalvageAuthorizationError, ValueError)`; `RecursionError` escapes. `SalvageAuthorizationError` subclasses `ValueError` (`salvage_dangler.py:215`); the caller's handler `continue`s — fail-closed. `json.loads` on a 2000-deep document succeeds (C scanner), so the only recursion site is the Python walk. Live: 400-deep licenses (no crash); 995-deep raises.

---

## F-7 — Packet hygiene: four findings.

All D-106 / kernel-row / decisive-audit / delta-F1 / delta-F2 verbatim quotes checked match their sources exactly; discipline largely held. Four shortfalls: (1) Established fact 3 is uncited and false (refuted 3/3 by probe; re-leans on winB-closure-facts.md). (2) Established fact 2 launders a bounded six-field trace into "over-refusal check clean" — 769/769 refuse. (3) The delta's only open flag (G1: full canonical suite not rerun) is omitted while the packet asserts "CLEAN and delta-verified". (4) Two citations mislabelled: the D-105 quotes live in docs/council_log.md:2485-2492 (COLD GATE 3 addendum), not "C-040 addendum record"; D-097 cited without line (actual :5931-5948). Additionally the packet's Q1 framing of formulation 1 reproduces an untested (and false) source claim in the trigger record.

---

## Unopposed-landing scope

Not opposed: the Q1 verdict (trigger fired; strengthened, not contested); C-B rejected; C-A's *direction* (writer-set allowlist family — already the tool's idiom at depth 1: `_ADMISSION_METADATA_FIELDS` at `salvage_dangler.py:828` verified a superset of every real abort bundle's top-level keys, zero false refusals there); the Q4 bound shape; everything the delta certified clean that was not attacked (A2 closure and six canonical tests; interval containment; digest freeze; marker; three byte-identical test_d106_* methods; fixture manifest addition; manifest-less refusal test); Q5's one-commit-plus-fresh-audit arc once scope is corrected.

---

## REPLACEMENT CANDIDATE — **C-A′**: producer-derived closed admission grammar, with value domains, corpus-attested, over-refusal-gated

**1. Scope.** The grammar governs exactly the three surfaces the b-ii license reads — `metadata.json`, `events.jsonl` rows, `summary_metrics.json`. The bundle's other subtrees are handled by F-1's separate amendment.

**2. Derivation obligation (the in-kind discriminator; non-optional).** For each container, the admitted key set and each leaf's value domain are derived from producer code **and verified to contain every value emitted across the governed corpus** — every bundle satisfying the b-ii predicate (`environment_admission.decision == "abort"` and `claim_reason == "environment_admission_failed"`): the 24 in `runs_window_*/` plus the 3 in `~/JouleWise-window-custody/window_metrologyB_20260801/quarantine/`. A key or value present in a real governed bundle and absent from the grammar is a **defect of the grammar**, never of the bundle. Mirrors D-097's verification standard.

**3. Key axis.** Per-container closed key set; unknown key ⇒ void. Unicode: compare keys after NFKC casefold, **and** void any key whose NFKC-casefolded form differs from its raw form (refuse the ambiguity; do not silently normalize).

**4. Value axis (the crux).** Every admitted leaf carries a decidable predicate from exactly four kinds. **No leaf may be admitted on a bare `isinstance(str)` check.**
- **CLOSED-ENUM** — mandatory for, at minimum: `environment_admission.failure` (7 producer literals); `.decision` ∈ {"abort"} (b-ii branch); `.claim_reason` ∈ {"environment_admission_failed"}; `.on_fail` ∈ AdmissionFailureAction values; `guard_observations[].phase` ∈ {before_attempt_N, after_attempt_N} for N ≤ attempt count (**the F-3 repair**); event/summary `failure_reason` ∈ FailureReason values; terminal failure `events[].message` and `summary.failure_message` ∈ the same 7 literals.
- **HASH** — `^[0-9a-f]{64}$` (`*_sha256`; `git_commit` as `^[0-9a-f]{7,40}$`)
- **NUMBER / TIMESTAMP** — finite number, or ISO-8601 against a fixed regex
- **BOOL / NULL**

**5. `metadata.extra`.** Admitted key set = the six producer scalars **plus `node_cleanup`** (`controller.py:2155-2167`), the latter a list of mappings over a closed key set with HASH/BOOL/enum leaves. Absent `extra` remains admissible (0/773 real bundles carry one).

**6. Depth.** Bounded by construction; independent hard guard at 32 raising `SalvageAuthorizationError`, plus the boundary-catch note.

**7. Genuinely open containers.** Where a container's emitted set cannot be closed, apply D-105's two-sided documented decidable superset. On the b-ii surface: **none found** (zero string leaf paths exceeded 25 distinct values; the widest are sha256 and ISO timestamps).

**8. ACCEPTANCE GATE — new, mandatory.** The row does not close until:
- (i) `inspect_salvage_attempt` **LICENSES all three** real quarantine bundles, pinned by a regression reading them read-only (or a byte-faithful hash-pinned fixture minted from one);
- (ii) a regression proves each of the four F-2 channels **voids**;
- (iii) the extra allowlist (six + node_cleanup) is re-derived per §2 and recorded;
- (iv) the F-1 inventory grammar is corrected under the same §2 obligation and the corrected set recorded.

Without (i) the row's acceptance evidence is unfalsifiable in the direction that has now failed three times running.

---

## F-8 — Q5 disposition: NOT a gate-licensed round 2 within the current arc as scoped.

Clause (c) can land as one commit plus a fresh focused audit **only after** the decision level: (1) amends D-106 clause 3 / the kernel row's acceptance evidence to add the over-refusal gate (§8) and the F-1 inventory correction — as it stands the row's premise ("window B unblocks on closure") is falsified by probe; (2) rules the fence question explicitly in the conditional form of F-5; (3) corrects the three established-facts entries so the next audit does not inherit them. D-106 clause 3(d) — the condition-3 re-record with the repaired tool — is unaffected and remains open regardless.
