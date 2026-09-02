## Disclosure

**Charter digest (computed):** `shasum -a 256 /Users/edr/code/JouleWise-wt-t26-a2/docs/process/coldgate_charter.md` → `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Matches the packet's expected value. Charter §3–§5, §8 read before merits.

**Prior context:** none (fresh seat).

**Read outside the packet's read set (all disclosed):**
- The harness injected `CLAUDE.md`, `CLAUDE.local.md`, and the memory index into my system prompt before I read anything. I did not open those files, but their text was in context. I relied on none of it; the rulings below cite only packet evidence.
- A task notification named an Opus "contract-lens cold refuter" output file (`tasks/a4a03dbc04ca77359.output`). I did NOT read it (sealing, §5).
- `git -C /Users/edr/code/JouleWise-wt-dx status --short` (dirty: `docs/paper/round7/fill-checklist.md`, `scripts/check_paper_round7_artifacts.py`, `scripts/paper_anchor_correction_quantified.py`) and one grep of the wt-dx working-tree `_decimal` (:386-389, byte-identical to 3f1677b7). All subject-A bytes otherwise via `git show 3f1677b7:`.
- `git grep` across 3f1677b7 to locate the packet's quoted `_decimal` line → found at `scripts/render_results_fills.py:241`, a different script.
- `docs/decision_log.md@2d24ef70` How-To :14-34 and the D-016 / D-110 index rows (:56, :150), beyond the D-170 citation; `docs/process/state_kernel.schema.json` scope enum; `scripts/gen_state.py:51-63` and the invariant list; the whole of kernel tasks `V5-TRANSACTION-01` / `MINT-GENERALIZE-01`.
- `docs/process_traces/**` heading/filename census (filenames + `## ` lines only), and the `## Executed evidence` section of `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`.

**Packet-hygiene defect (charter §6), disclosed not refused:** Fact F1 and Opus S1 quote `_decimal` as `return value if isinstance(value, Decimal) else Decimal(str(value))`. At 3f1677b7 (`scripts/check_paper_round7_artifacts.py:369-372`, also in `diff-fence-main-to-3f1677b7.patch`) it is:
```python
def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"not a decimal scalar: {value!r}")
    return Decimal(str(value))
```
It already rejects `bool`. The `str` and `int→Decimal` acceptances are real. I rule on the actual bytes.

**Probe method (all read-only, scratch under `…/scratchpad/coldfable/`):** scratch repo built from `git show 3f1677b7:` of the checker, test, registry, skeleton, checklist and the XD/AQ/XS/AS/F4 artifacts; per-probe copy mutates one artifact, re-pins the registry digest/size, runs `check_paper_round7_artifacts.py --repository-root <probe> --literals-only`. Baseline: `R7F COMPARED 181 / MISMATCHES 0`, rc=0.

| Probe | Mutation | 3f1677b7 result |
|---|---|---|
| P1 | AQ `summary.delta_v3_vs_stored_relative.max_absolute_pct: "4.046812"` (string) | rc=0 PASS |
| P2 | XD `calibration_gate.b_fiducial_s_matches_exactly: 1` | rc=0 PASS |
| P2b | AQ gate `matches_exactly: 1.0` | rc=0 PASS |
| P3 | XD `per_pulse[0].onset_best_fit_lag_ms: "16.0"` (string) | rc=0 PASS (via `float()` at :565 — a site S1 did not name) |
| P4 | `median_absolute_deviation_ms: 4` (int where float) | rc=0 PASS |
| P5 | `max_absolute_pct: true` | rc=2 `MISMATCH row DX-026 … REFUSED: ValueError: not a decimal scalar: True` |

Python: `True == 1` → `True`; `True == 1.0` → `True`.

---

## A1 — Same defect class? Cure shape.

**Verdict: AMEND** (adopt option (a) with two corrections; severity MATERIAL, not BLOCKER).

**Classification.** Same *mechanism family* (scalar reads coerce instead of refuse), NOT the same *defect*. luna 189's `int()` truncated `15.9 → 15` and produced a **wrong literal that matched** — a true wrong-number pass. Every S1 site (`_decimal` str/int acceptance, `_comparison` `==`, `check_figure:565 float()`) can only accept a re-issued artifact whose *value* still equals the pinned literal under a different JSON type. None can produce a wrong number in the paper. Rule 11's "second round, same signature" trigger is correctly fired for the family; the severity is producer-drift admission (D-161: re-issued artifacts, honest drift), which is MATERIAL.

**Two places the packet's framing is wrong; I rule against it:**
1. F1 misquotes the code (above). P5 already refuses. The bool→Decimal counterfactual is *not* biting today; the biting ones are P1, P2, P2b, P3.
2. Option (a)'s "refuse `float→Decimal`" cannot be applied at the resolver: all 12 decimal-rendered fields are JSON floats (probe: every `*_ms` / `*_pct` field is `float`, every count `int`, every gate `bool`). Refusing floats at the resolver fails the honest corpus. The float clause is implemented at the **loader**: `json.loads(text, parse_float=Decimal)` in `load_json_artifacts` (:323), so no `float` object ever reaches a renderer and `Decimal(str(float))` disappears.

**Operative code shape (prototype `coldfable/cured.py`; verified baseline 181/0 unchanged, P1/P2/P2b/P3/P5/M4/M7 all refused, P4 accepted):**
1. `load_json_artifacts`: `json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)`.
2. `_comparison`: `match = type(expected) is type(observed) and expected == observed`.
3. One resolver, the only path any renderer or gate uses to read an artifact scalar:
```python
KINDS = ("int", "number", "bool", "str")
def _typed(value: Any, kind: str, field: str) -> Any:
    if kind == "bool":   ok = isinstance(value, bool)
    elif kind == "int":  ok = isinstance(value, int) and not isinstance(value, bool)
    elif kind == "number": ok = isinstance(value, (int, Decimal)) and not isinstance(value, bool)
    elif kind == "str":  ok = isinstance(value, str)
    else: raise ValueError(f"unknown kind {kind!r}")
    if not ok:
        raise ValueError(f"{field}: expected {kind}, found {type(value).__name__}: {value!r}")
    return Decimal(value) if kind == "number" else value
```
   `_decimal(value, field)` → `_typed(value, "number", field)`; `_exact_int_field` → `_typed(value, "int", field)`; renderers pass `row.field_refs[i].label` (`SRC#path`) as `field`; `failures[0]` (control_count rule) → `_typed(failures[0], "str", "AQ#summary.control_v2_reproduction_failures[0]")`; `check_gates` → `value = _typed(resolve_field(...), "bool", f"{source}#{path}")` with `except ValueError as exc: value = f"REFUSED: {exc}"` (keeps the existing MISSING branch); `check_figure` per-pulse read → `_typed(pulses[index][value_key], "number", f"XD#per_pulse[{index}].{value_key}")` wrapped in `try/except (KeyError, ValueError)` emitting `_comparison(f"figure {name} mark {index}", "present and matching", f"REFUSED: {exc}")` and `continue` (the bare `float()` at :565 is a crash path for any non-numeric per-pulse value today, not a refusal).
4. Delete the free `_decimal(value)`/`float()` call forms; a grep `Decimal(str(` and `float(` over the checker must be empty after the cure.

**Regressions (dictated):**
- Table-driven unit test over `_typed`: `int` rejects `Decimal("15.9")`, `Decimal("15.0")`, `True`, `"15"`, `None`; `number` rejects `"4.05"`, `True`, `None`, `[]`; `bool` rejects `1`, `Decimal("1.0")`, `"true"`, `None`; `str` rejects `1`, `True`, `None`. Accepts: `int`←`15`, `number`←`15`/`Decimal("4.05")`, `bool`←`True`, `str`←`"x"`.
- Three end-to-end CLI regressions through `_run_scratch_checker` (production call site, per the counterfactual rule): P1 → rc 2 and output contains `row DX-026` and `AQ#summary.delta_v3_vs_stored_relative.max_absolute_pct: expected number, found str`; P2 → `gate XD#calibration_gate.b_fiducial_s_matches_exactly` and `expected bool, found int`; P3 → `figure onset mark 0` and `expected number, found str`.

**Biting counterfactual per kind:** number: P1 (`"4.046812"`) — passes today, must MISMATCH naming DX-026. bool: P2 (`1` for `true`) — passes today, must MISMATCH the gate label. int: `15.9` (M4) — already refused, must stay refused *through* `_typed`. str: `control_v2_reproduction_failures[0]: 20260722213749` (int) — passes today by `str()` in the f-string; must refuse.

**Not decided:** P4 (JSON int where a float is expected) is ACCEPTED by design — both are the JSON `number` category and the rendered literal is exact; a producer serialization contract (whether producers must emit floats) is out of scope; the pre-existing N1/N2/N3 items are not before me.

---

## A2 — Placement census and bare-prose scan: this PR or fill-stage row?

**Verdict: AMEND** — (i) census in THIS PR, self-gated on registry content rather than a CLI flag; (ii) bare-prose scan as specified REJECTED for this PR, re-scoped to a fill-stage kernel row.

**(i) Census — operative shape.** Gate on the registry's own mandatory DX standing sentence (`results-fill-registry.md:742-746`, which `fill-checklist.md:249-268` requires to precede every DX placement) rather than an invented flag: `n_standing` = count of occurrences of the standing sentence's first clause (pin the exact string as a module constant from the registry section) in `draft-v2-skeleton.md`. If `n_standing == 0`: assert zero `[FILL:DX-` markers (a DX placement without its standing paragraph is a checklist violation). If `n_standing ≥ 1`: each of the 16 non-identity rows (DX-010..017, DX-020..027; identity rows DX-001..003 excluded, they are provenance not prose) must appear as `[FILL:DX-nnn]` ≥ 1, each missing row a `MISMATCH placement DX-nnn: expected ≥1, observed 0`. Emit `R7F PLACED n/16` in the tail. Regression: skeleton copy with the standing sentence + 15 markers → rc 2 naming the 16th; skeleton with `[FILL:DX-010] +13.0 ms` and no standing sentence → rc 2. Current skeleton (0/0) passes.

**Biting counterfactual today:** a skeleton containing `[FILL:DX-010] +13.0 ms` and no standing sentence must fail; today it passes (only the literal-after-marker compare runs, vacuously true).

**(ii) Scan — why not this PR.** The proposed scan ("each row's rendered literal outside a marker") is unusable on this corpus: `15` (DX-020) hits 12 unrelated skeleton lines (e.g. :330, :381, :384); `4.0 ms`, `2.5 ms`, `+0.61 %` are plausible in non-DX prose. Installing it now means either a false-failing fence or a whitelist that rots. Rule: a kernel row at fill stage, scoped to the **DX prose region** (from the standing sentence to the next `^#` heading): within that region, any occurrence of a DX rendered literal not immediately preceded by its own `[FILL:DX-nnn]` marker is a MISMATCH; outside the region no scan. Acceptance for that row: regression with a DX-region sentence "refused 49 of 59 pulses" (no marker) → rc 2; the same literal outside the region → pass. The row's counterfactual is the same sentence *with* the marker → pass.

**Not decided:** the wording of the standing sentence, the DX prose region's location in the successor draft, and whether identity rows ever appear as prose.

---

## B1 — Item 4 enforcement fires on zero post-cutoff files.

**Verdict: AMEND** — option (i) with a closed one-file exemption and a prospective glob widening; (ii) REJECTED (brittle: `## 2. Rulings on…` already defeats a vocabulary list, and the next author's heading will too); (iii) REJECTED (a test that cannot fire is not an installation of the rule; keeping it "as ruled" installs nothing).

**Census (re-run; command in the transcript, `Path("docs/process_traces").rglob`):** 22 `*MAGISTRATE-RULING*.md`; trigger fires on 11/20 pre-cutoff, 0/2 post-cutoff. Post-cutoff `*RULING*.md` of any name: **30 files, of which 2 are MAGISTRATE-RULING, 1 carries `## Executed evidence`, 5 match the ruled heading trigger**; 0 dated ≥ 2026-09-03. So the ruled glob covers 2 of 30 post-cutoff rulings and the ruled trigger covers 0 of those 2. The rule as installed is dead by construction, and the kernel acceptance row "Executed-evidence shape test present and mutation-killed" (`state_kernel.json` T26-RULING-INSTALL-01 evidence[1]) is FALSE at 2d24ef70 (Opus M7/M8 survive) — must be corrected in the same install commit.

**Operative text (replaces the enforcement paragraph, :281-290; the rule body is unchanged):**
> Test: (a) every `docs/process_traces/<dated-dir>/**/*MAGISTRATE-RULING*.md` whose dated directory component (any depth, `YYYY-MM-DD` prefix) is ≥ 2026-08-29, EXCEPT the enumerated pre-install file `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` (predates the install; listed by exact path in the test with that reason; the list is closed); and (b) every `**/*RULING*.md` under a dated directory ≥ 2026-09-03 (prospective from install, so the ~28 existing short rulings are not retro-failed); must contain a `## Executed evidence` heading, and the section body (heading to the next `^## `) must satisfy ONE of: (1) a fenced block containing a line matching `^\$ .+` AND a *different* line matching `^\s*(?:exit|EXIT|rc|exit code|exit status)[\s=:]+\d+\s*$`; or (2) a citation matching `[A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml):\d+` — `.md:\d+` is a document pointer, not a code-path proof, and no longer satisfies (b) of the rule body. The heading trigger is dropped: the filename is the trigger.

The in-scope `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` passes under this shape via branch (1) (`$ python3 - <<'EOF'` … separate `exit 0` line — read directly); its `.md:48-49` citations no longer carry it, which is correct.

**Biting counterfactuals (all must fail after the amendment; all pass at 2d24ef70):** M7 (delete the `## Executed evidence` heading from the 09-02 ruling) — the primary one; M8 (drop the `exit 0` line AND the `.md` citation); a fence whose only content is `$ echo exit`; a section whose only evidence is `docs/contracts/bridge_protocol.md:48`.

**Not decided:** truth of the evidence (the "shape not truth" residual at :288-290 stands and is the right residual); whether the exempted stage-1 ruling should be amended to carry evidence (that is a magistrate decision about a custodied file); heading-vocabulary style.

---

## B2 — Item 1 dependency placement and test assertions.

**Verdict: AMEND** — placement is **both**, and the packet's `scope: finish` does not exist in the kernel vocabulary (`gen_state.py:51-63` `DEP_SCOPES = ("start","retain_evidence","interpret","close","live_promotion")`); the installer's dependency is `scope: "close"`.

**Reading ruled.** The rule body (:72-75) says the dependency goes "on every task the clause gates" — the seat's reading of *where the pending hard-start dep lives* is correct, and the literal reading (installer carries a pending hard `start` dep) is self-defeating under invariant 3 (`gen_state.py:357-366`) as the packet says. But enforcement (ii) (:94-97) says the `installs via` task itself must carry "a `kind: decision` dependency targeting the row's D-id", and the installed test does not check that on the named task — it checks *any* task (`test_docs_freshness.py:282-294`), which is why Opus M4 (`installs via ARM-PACKET-01`, an unrelated task) survives. Both clauses are honored by: every gated task carries `{kind: decision, target: D-NNN, strength: hard, scope: start, state: pending}`; the installing task carries `{kind: decision, target: D-NNN, strength: hard, scope: close, state: pending}` — well-typed, does not trip invariant 3 (only `start` scope blocks; verified `gen_state.py:357-366`), and satisfied when the row leaves `open`. `_check_dependency` (:167-191) already refuses pending-with-evidence / satisfied-without-evidence, so the installer dep cannot be quietly marked satisfied without evidence.

**Test assertion set (`test_open_decisions_name_an_installing_kernel_task`), all four required for each `open (installs via X)` row with D-number ≥ 170:**
1. `X in kernel["tasks"]`.
2. Task `X` carries ≥ 1 dependency with `kind == "decision"` and `target == D-id` (any scope, any state).
3. Some task (may be X or another) carries such a dependency with `strength == "hard"`, `scope == "start"`, `state == "pending"`.
4. (Opus F5b) the number of index rows parsed for this test equals the number of `^\| D-\d+ \|` rows in the index (no silent drop on a malformed status cell like `| decided|`; a malformed cell is a failure, not a skip).

The `D-number < 170` legacy exemption stays only for the pre-existing D-016 form (`open (provisional …)`), matched by exact row, not by number range.

**Biting counterfactual:** M4 — change D-170's row to `open (installs via ARM-PACKET-01)` (a real task with no decision dep on D-170) → must fail at assertion 2; passes today.

**Not decided:** whether `close`-scope pending deps should gain any gen_state enforcement beyond shape; S9 row registration (B4).

---

## B3 — Opus F4: non-`open` row with a pending decision dep is a contradiction.

**Verdict: AMEND (adopt, prospective).** The rule as literally proposed fails TODAY on a row nobody has questioned: `D-110` is `accepted (Ed 2026-08-03…)` (`decision_log.md:150`) while `MINT-GENERALIZE-01` carries a `pending` hard-start decision dep on D-110 (kernel; F4). Retro-applying would force either editing D-110's row or the mint task's dependency with no ruling behind it. Operative text: for every index row with D-number ≥ 170 whose leading status token is not `open`, no task in `state_kernel.json` may carry a `kind: decision` dependency targeting that D-id with `state: pending`; the failure message names the row status and the task. D-110 is recorded as a known pre-rule inconsistency in the test's comment, not exempted by a list (the ≥ 170 boundary already excludes it, and it is the same boundary the installed test uses).

**Biting counterfactual:** M6c — set D-170's row to `adopted (…)` while `V5-TRANSACTION-01` keeps its pending dep → must fail; passes today.

**Not decided:** what to do about D-110 / MINT-GENERALIZE-01 (magistrate's call: either the row is not really accepted or the dep is stale); whether `satisfied` deps on `open` rows are a contradiction (they are not — the ruling body allows satisfaction on evidence before the row flips).

---

## B4 — S9 rows

None of S9-01b/02/03/04/05/06/12 changes B2: each is an additional *gated* task and receives the hard/start/pending dep under the B2 placement; the installer's single `close`-scope dep is unchanged. Registering them at the bench will make B2 assertion 3 satisfiable by more than one task, which is intended.