# 11 — Opus contract-lens refuter (read-only), GENERATOR-HEAD-FILE-BYTE-PIN-01

Independent of the cold-gate judge's ruling (not seen). Worktree @ `a5905f67`; charter digest recomputed, MATCHES the packet pin.

## Q1 — ruled option: (a), with one amendment

**ADOPT B1 for the LIVE generators only; historical generators keep the byte pin
and the Exhibit E fixture.** Amendment: the live set is **two** files, not three
— `d117_contrast_v5/generate_configs.py` touches the head file only at run time
(line 2134, `--head-pin`), declaring no generation-time constant. Edit
`configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/generate_configs.py`.

### What the contract actually promises

D-109 R1.4 (Exhibit B) binds: (i) the acceptance artifact pins its *baseline*
ledger head; (ii) **evaluation** also requires the independent current-head pin
and verifies one non-forked chain extension baseline→current; (iii) a *physical*
head differing from the committed pin refuses. All three are evaluation-time
obligations against the physical ledger. The append contract then licenses the
pin file to move (`advance-head-pin`) and runbook §3 item 4 makes advancing it a
per-night duty. Nothing asks a **generator** to freeze those bytes. The
generator's share is (i), carried by a *different* constant `LEDGER_HEAD_SHA256 =
08456d50…` (Exhibit A 214–216) equal to the r6 `cutoff["head_digest"]`
(`joulewise/calibration_bracketing.py:813, 817-819`). B1 *conforms*; the byte pin
is what contradicts the contract — it makes a licensed nightly action a refusal.

### Adversarial pass against (a)/(b) — the strongest fence the byte pin gives

Three candidates; only the first survives.

1. **SURVIVES (partially): generation-time divergence detection.** `sequence >=
   cutoff.sequence` is an *ordering* test; a pin at sequence 126 whose
   `head_digest` is not a chain extension of the cutoff (D-109's `diverged`
   relation) passes ordering and fails a byte test. The byte pin catches that —
   but only by refusing *every* advance, licit ones included. It is not
   recoverable in a generator: the ledger is not a declared generator input
   (`external_inputs` in the committed `d117_floor_qwen25_1p5b_v3/plan_tree.json`
   lists only `settled_corpus.json` and the prefill candidate). It IS recovered
   where R1.4 puts it — `joulewise/calibration_ledger.py:2600-2613` compares the
   physical chain to the committed pin (`calibration_ledger_rollback`,
   `…_head_mismatch`, `…_head_uncommitted`), reached because the pack passes
   `--head-pin` at RUN time (`…qwen3-1p7b_v5/generate_configs.py:1625`).
   **Ruling: the loss is real and must be stated, not waved away** — the lane
   record and B1's comment must say fork/divergence is evaluation-owned.
2. **FAILS: "a consumer relies on `issued_ledger_head.file_sha256`."** None
   exists (grep → zero hits). The only `acceptance_policy` readers are
   `arm_readiness.py:6191-6198` and `arm_readiness_evidence.py:895-915`, both
   reading `issued_acceptance` only; no contract file mentions
   `acceptance_policy`. Removing the key is **not** a schema change needing a
   code consumer sweep — the only in-repo occurrences are the six committed
   historical `plan_tree.json` files, untouched by (a).
3. **FAILS: "a regenerated live pack becomes non-reproducible."** Opposite: the
   v5 pack is **not committed** (`git ls-files` → `generate_configs.py` alone),
   so under (a) it is emitted from declared constants only and stays
   byte-identical across advances. The option-(d) variant of recording the
   *observed* head digest is strictly worse — pack bytes would become a function
   of an undeclared mutable file, destroying the closure
   `test_generators_are_deterministic_closed_and_checkable` proves.

### Adversarial pass against (b) — REFUTED, it breaks constraint (iii)

Yes — a frozen pack's custody DOES hash the generator's pinned constants, twice:
the pack embeds a copy of the generator (`write_bytes(output_root, PACK_REL /
"generate_configs.py", source_raw)`) and the committed `plan_tree.json` records
its digest (`generator.sha256 = 120b60e8…` for `d117_floor_qwen25_1p5b_v3`;
emitted at `…qwen3-1p7b_v5/generate_configs.py:2862-2865`). Worse, the v2 → v3
successor path derives the successor's source **from the v2 file's own text**:
`embedded_generator_bytes()`, `…qwen25_1p5b_v2/generate_configs.py:381-391`,
reads `SOURCE_PATH` and substitutes the family suffix. So a constant edit in v2
changes the emitted v3 bytes → changes the v3 pack's `generator.sha256` → the
committed v3 pack no longer reproduces, and
`test_unedited_v2_generators_emit_v3_successors` fails for a *new* reason. (b)
cannot keep frozen packs byte-identical without re-committing them — which is
unfreezing them. **(b) is out.**

### Adversarial pass against (c) — the recurring cost, quantified

**2 constant edits per pin advance**, each regenerated-and-diffed, plus the
standing fixture across ≥7 test modules (Exhibits D/E) that (c) does not remove.
The pin advanced 76 → 126 → 176 on 2026-09-19 alone: six edits in one day. By the
(b) evidence each edit is also **custody-bearing** — it changes
`generator.sha256` in the next emitted pack. So it is not "one reviewed line" but
a pack-identity change on the night-critical path, hand-made at arm time: (c)
puts a mandatory hand-edit of an arming artifact inside the pre-arm window.
Reject.

### Exact code shape (two files)

Drift tuple at `…qwen3-1p7b_v5/generate_configs.py:2503-2509` — delete the
`(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)` row, leave the other four rows
untouched, and insert after the loop:

```python
    head_pin = json.loads((REPO_ROOT / LEDGER_HEAD_REL).read_text("utf-8"))
    cutoff = acceptance_cutoff()   # {sequence, head_digest, ledger_schema}
    sequence = head_pin.get("sequence")
    if (set(head_pin) != {"sequence", "head_digest", "ledger_schema"}
            or isinstance(sequence, bool) or not isinstance(sequence, int)):
        raise ValueError("ledger head pin shape invalid")
    if head_pin["ledger_schema"] != cutoff["ledger_schema"]:
        raise ValueError(
            "ledger head pin schema differs from the acceptance cutoff: "
            f"{head_pin['ledger_schema']!r} != {cutoff['ledger_schema']!r}")
    if sequence < cutoff["sequence"]:
        raise ValueError("ledger head pin behind the acceptance cutoff: "
                         f"{sequence} < {cutoff['sequence']}")
    if (sequence == cutoff["sequence"]
            and head_pin["head_digest"] != cutoff["head_digest"]):
        raise ValueError("ledger head pin diverges from the acceptance cutoff")
    # Chain extension BEYOND the cutoff (D-109 R1.4 `diverged`) is evaluation-
    # owned: the ledger is not a declared generator input.  See
    # joulewise/calibration_ledger.py:2600.
```

Delete `LEDGER_HEAD_FILE_SHA256` (211-213). Manifest 2886-2890: drop
`"file_sha256"`, keep `{"path": …, "head_sha256": LEDGER_HEAD_SHA256}`, assert
`LEDGER_HEAD_SHA256 == cutoff["head_digest"]` at import.

## Q2 — authority and sequencing

**Not a contract amendment.** It conforms to Exhibit B as written: R1.4's
anti-rollback stays where R1.4 puts it (evaluation against the physical ledger),
plus the new generation-time ordering refusal. No decision-log text changes; a
kernel NOTE that the generator's generation-time obligation is the *acceptance
baseline*, not the pin file's bytes, is bookkeeping.

**Sequencing: AFTER PR #361** — it is test-only and cures CI now; gating it on a
production change inverts the risk. **The Exhibit E fixture stays, not dead
weight:** under (a) historical generators keep their byte pin by design, and the
fixture applies exactly to labels `ALPHA`/`BETA` in
`test_campaign_generator_core` — the standing proof that a generator is a
function of its declared inputs. Only the *v5-facing* fixture
(`generation_repository()` + call sites in
`tests/test_d117_floor_qwen3_v5_generate.py`) retires in the B1 lane.

## Q3 — regressions that must exist afterwards (defect-shaped)

1. Pin advanced past the cutoff (176, valid digest) → generation succeeds,
   pack bytes **byte-identical** to a run at sequence 76.
2. Pin rolled back (sequence 75) → `ledger head pin behind the acceptance
   cutoff: 75 < 76`.
3. Pin AT the cutoff sequence with a different `head_digest` → `ledger head pin
   diverges from the acceptance cutoff` — the only divergence case a generator
   can see; must not be dropped.
4. `ledger_schema` altered → schema message; extra/missing key or a bool/str
   `sequence` → `ledger head pin shape invalid`.
5. Another pinned input drifted (`POLICY_REL`, acceptance artifact,
   `NEG8_SETTLED_REL`) → still `pinned input drifted: <path>`, tuple length
   asserted = 4 so a future edit cannot silently empty it.
6. `LEDGER_HEAD_SHA256` asserted equal to the registered r6 cutoff
   `head_digest` in `joulewise/calibration_bracketing.py`.
7. Preserve/echo mode and historical successor paths unchanged: `--check` and
   `test_unedited_v2_generators_emit_v3_successors` still pass with the byte pin
   intact.

**Obsolete after the lane:** `generation_repository()` and its four call sites in
`tests/test_d117_floor_qwen3_v5_generate.py`; any assertion that a *v5* generator
raises `pinned input drifted` / `external input drift` for
`calibration_ledger_head.json` — *replaced* by regressions 2–4, never deleted.

## Commands run (all read-only)

- `shasum -a 256 docs/process/coldgate_charter.md` → `099de884…95d81` MATCHES the pin; `git log --oneline -1` → `a5905f67`; `git ls-files configs/campaigns/d117_floor_qwen3-1p7b_v5` → `generate_configs.py` only.
- `grep -rn "issued_ledger_head" joulewise/ scripts/ tests/` → zero hits; `"acceptance_policy"` same dirs → `arm_readiness.py:6192`, `arm_readiness_evidence.py:897`; `docs/contracts/*.md` → zero.
- python load of `d117_floor_qwen25_1p5b_v3/plan_tree.json` → `issued_ledger_head.file_sha256 = 6bbe2625…`, `generator.sha256 = 120b60e8…`, `external_inputs` omits the head file.
- `grep -n "LEDGER_HEAD|issued_ledger_head" …qwen3-1p7b_v5/…` → 186, 211, 214, 1625, 2507, 2886-2889; `d117_contrast_v5` → 2134 only; `grep -n "def embedded_generator_bytes" -A12 …qwen25_1p5b_v2/…` → 381-391.
- `sed -n '2595,2645p' joulewise/calibration_ledger.py` → 2600-2613; `grep -n "head_digest|ledger_schema" joulewise/calibration_bracketing.py` → 813, 817-819, 1399-1403.
- `env … -m unittest tests.test_campaign_generator_core` in wt-refc @ `ff788ef7` → **OK**, 7 tests, 3.994 s, exit 0. No write outside this file and the scratch dir.
