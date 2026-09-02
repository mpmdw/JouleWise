# Magistrate ruling — cold gate on the round-7 fence (subject A) and the T26 item-1/4 install (subject B)

Date 2026-09-02, session 540125d5. Packet: `00-PACKET.md` in this directory
(questions A1, A2, B1, B2, B3, B4). Three sealed seats, launched in parallel
with no cross-visibility:

| Seat | Model / lens | File |
| --- | --- | --- |
| Opus 5 contract-lens refuter | `Agent` model opus, detached worktree | `seat-opus-219.md` |
| Cold Fable adjudicator | fresh Fable session, packet-only read set | `seat-cold-fable-220.md` |
| Sol xhigh, read-only (`WRITE_SCOPE: []`) | contract + execution lens | `seat-sol-217.md` |

Charter `docs/process/coldgate_charter.md` sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`, verified
by all three seats. Contamination disclosed by the seats: harness-injected
doctrine text (cold Fable) and `AGENTS.md` prose (Sol); both state they relied
on neither. The magistrate (this session) is NOT a seat: it wrote the packet,
directed the rounds under review, and synthesises here (three-seat rule).

## Packet defects (charter §6 — disclosed by the seats, confirmed at the bench)

- **PD-1 (magistrate error).** Fact F1 quoted `_decimal` as
  `return value if isinstance(value, Decimal) else Decimal(str(value))` and
  labelled it "bench-verified". It was transcribed from Opus 207, not
  verified. The committed bytes at `3f1677b7:scripts/check_paper_round7_artifacts.py:369-372`
  already refuse `bool` and accept `(int, float, str)`; the quoted line lives
  in a different program (`scripts/render_results_fills.py:241`, whose input
  is registry TEXT — accepting `str` there is the input format, not this
  class). Consequence: the `bool→Decimal` counterfactual is not biting today;
  the `str→Decimal`, `int/float→bool` (`True == 1`) and `check_figure:565`
  `float()` acceptances are. All three seats ruled on the true bytes.
  Standing correction for the magistrate: a packet fact is labelled
  bench-verified only after the check has actually been run at the bench in
  this session.
- **PD-2.** The packet under-counted item 4's miss: the ruled glob covers 2 of
  30 post-cutoff `*RULING*.md` files and its heading trigger fires on 0 of
  those 2; 1 of the 30 carries `## Executed evidence`; 0 are dated ≥ 2026-09-03.

## Executed evidence

Run at the bench 2026-09-02 07:11 PDT in `/Users/edr/code/JouleWise-wt-t26-a2`
(detached @ 2d24ef70), subject A bytes via `git show 3f1677b7:`:

```text
$ /Users/edr/code/JouleWise/.venv/bin/python - <<'EOF'   # probe: exec 3f1677b7 checker; census; kernel deps
decimal_src ['def _decimal(value: Any) -> Decimal:', '    if isinstance(value, bool) or not isinstance(value, (int, float, str)):', '        raise ValueError(f"not a decimal scalar: {value!r}")', '    return Decimal(str(value))']
True==1 match: True | str->Decimal: Decimal('4.05')
bool refused: not a decimal scalar: True
MAGISTRATE-RULING files 22 post>=08-29 2 post+trigger 0
all *RULING*.md post>=08-29: 30 with Executed evidence: 1 dated>=09-03: 0
decision deps: {'MINT-GENERALIZE-01': [('D-110', 'start', 'pending')], 'V5-TRANSACTION-01': [('D-170', 'start', 'pending')]}
exit 0
```

Seat-side executions relied on: cold Fable probes P1–P5 (scratch checker,
baseline `R7F COMPARED 181 / MISMATCHES 0`, cured prototype re-run), Sol
V2–V5 (`seat-sol-217.md`), Opus mutation table (`seat-opus-219.md`).

## A1 — same defect class; cure shape

Seats: Opus AMEND (option (c): `_decimal` → `(int, float)` only, type-strict
`_comparison`, no resolver — "over-engineering"); cold Fable AMEND (option (a)
corrected: `parse_float=Decimal` at the loader, one `_typed(value, kind,
field)` resolver, type-strict `_comparison`, the unenumerated
`check_figure:565` `float()` site cured); Sol ADOPT (a) (+ a declarative
field-kind map and composite-leaf validation).

**Ruled: AMEND — the cold Fable shape, verbatim.** Classification: same
mechanism family as luna 189 ("scalar reads coerce instead of refuse"), NOT
the same defect (round 1 produced a wrong literal that matched; S1 can only
admit a re-issued artifact whose value still equals the literal under another
JSON type). This ruling IS the rule-11 second round on the family; any third
round on it returns to a cold gate without discretion.

Operative shape (production sites at the merged head after 781c8d78 — the seat
re-audits line numbers):

1. `load_json_artifacts`: `json.loads(text, parse_float=Decimal)` — no
   `float` object ever reaches a renderer; `Decimal(str(float))` disappears.
2. `_comparison`: `match = type(expected) is type(observed) and expected == observed`.
3. One resolver, the only path any renderer, `check_gates`, `check_figure`
   or the control-count rule uses to read an artifact scalar:
   `_typed(value, kind, field)` with `kind ∈ ("int", "number", "bool", "str")`;
   `int` = `isinstance(value, int) and not bool`; `number` = `int` or
   `Decimal`, not `bool`, returned as `Decimal`; `bool` = exactly `bool`;
   `str` = exactly `str`; refusal message
   `f"{field}: expected {kind}, found {type(value).__name__}: {value!r}"`.
   `_decimal` and `_exact_int` become thin wrappers; renderers pass the
   `SRC#path` label as `field`; `check_gates` reads through `_typed(..., "bool",
   ...)` and turns `ValueError` into a `REFUSED: …` observed value (existing
   MISSING branch kept); `check_figure` per-pulse reads through
   `_typed(..., "number", f"XD#per_pulse[{i}].{key}")` inside
   `try/except (KeyError, ValueError)` emitting a REFUSED comparison and
   `continue`; `failures[0]` read through `_typed(..., "str", ...)`.
4. After the cure `grep -n 'Decimal(str(\|float(' scripts/check_paper_round7_artifacts.py`
   is empty.

Rejected: Sol's declarative field-kind map and composite validation (kinds
are literal at 16 call sites; a map is a second source of truth); Opus's
site-patch shape (P3 — a per-pulse string `"16.0"` — passes today through a
site none of the refuters enumerated; the resolver is one 12-line function and
exists precisely so unenumerated sites cannot exist). **Opus dissent recorded:**
"one typed resolver is over-engineering against an operator-only adversary."
Answer: the threat is honest producer drift, and P3 is drift at a site the
site-patch approach missed.

Regressions (dictated): the cold Fable table over `_typed` (int rejects
`Decimal("15.9")`, `Decimal("15.0")`, `True`, `"15"`, `None`; number rejects
`"4.05"`, `True`, `None`, `[]`; bool rejects `1`, `Decimal("1.0")`, `"true"`,
`None`; str rejects `1`, `True`, `None`; accepts int←`15`, number←`15` /
`Decimal("4.05")`, bool←`True`, str←`"x"`); `_comparison` refuses `(True, 1)`,
`(True, 1.0)`, `(1, 1.0)`; three end-to-end CLI regressions through the
scratch-checker production path — P1 (AQ `max_absolute_pct: "4.046812"` → rc 2
naming `row DX-026` and `expected number, found str`), P2 (XD
`calibration_gate.b_fiducial_s_matches_exactly: 1` → gate label + `expected
bool, found int`), P3 (XD `per_pulse[0].onset_best_fit_lag_ms: "16.0"` →
`figure onset mark 0` + `expected number, found str`). P4 (JSON `4` where a
float is expected) is ACCEPTED by design (both are JSON numbers; the rendered
literal is exact). Not decided: a producer serialization contract.

## A2 — placement census and bare-prose scan

Seats: Opus → both to a kernel row, land only a vacuity disclosure line; cold
Fable → census in THIS PR self-gated on the registry's mandatory standing
sentence, prose scan to a fill-stage row scoped to the DX prose region; Sol →
both to a fill-stage row, nothing vacuous in this PR.

**Ruled: AMEND — census in this PR (cold Fable shape); prose scan to a kernel
row.** The census gates on the registry's own mandatory DX standing sentence
(`docs/paper/results-fill-registry.md:742-746`, required by
`fill-checklist.md:249-268` before any DX placement): `n_standing` = count of
the sentence's first clause (pinned as a module constant) in
`docs/paper/draft-v2-skeleton.md`. `n_standing == 0` → assert zero
`[FILL:DX-` markers (a placement without its standing paragraph is a checklist
violation); `n_standing ≥ 1` → each of the 16 non-identity rows
(DX-010..017, DX-020..027) appears as `[FILL:DX-nnn]` ≥ 1, each missing row a
`MISMATCH placement DX-nnn: expected ≥1, observed 0`. The tail always prints
`R7F PLACED n/16` (today `0/16` — Opus's vacuity disclosure, without a flag
that can rot). Regressions: skeleton copy with the standing sentence + 15
markers → rc 2 naming the 16th; `[FILL:DX-010] +13.0 ms` with no standing
sentence → rc 2; the current skeleton (0/0) passes. **Sol dissent recorded**
(nothing in this PR): overruled because the gate has a biting counterfactual
today (marker without standing sentence) and no maintenance surface.

Prose scan: kernel row `R7F-DX-PROSE-SCAN-01` (fill stage; magistrate
registers at the bench). Scope: the DX prose region (from the standing
sentence to the next `^#` heading); within it any DX rendered literal not
immediately preceded by its own marker is a MISMATCH; no global scan (`15`
hits 12 unrelated skeleton lines today). Acceptance: "refused 49 of 59 pulses"
unmarked inside the region → rc 2; same literal outside → pass; with marker →
pass. No acceptance row anywhere may record R7F as covering prose placement
until that row closes.

## B1 — item 4 enforcement fires on zero files

Seats: all three AMEND on option (i) (drop the heading trigger; the filename
is the trigger). Opus keeps a widened heading regex and a uniform 2026-09-03
cutoff (zero files today + a future-dated positive control); cold Fable
splits (a) `*MAGISTRATE-RULING*.md` ≥ 2026-08-29 with one enumerated
exemption / (b) `*RULING*.md` ≥ 2026-09-03; Sol scans all ≥ 2026-08-29 with a
four-line execution record. (ii) and (iii) REJECTED by all.

**Ruled: AMEND — cold Fable's (a)+(b), plus Opus's path-existence and Sol's
non-empty census.** Not a verdict reinterpretation (charter §9: the
enforcement paragraph is self-labelled machinery; the rule body is unchanged).

Operative enforcement text (replaces `COLD-GATE-RULING.md:281-290` by dated
addendum, never in place):

> Selected files: (a) every `docs/process_traces/<dated-dir>/**/*MAGISTRATE-RULING*.md`
> whose dated directory component (`YYYY-MM-DD` prefix, any depth) is
> ≥ 2026-08-29, except the closed list
> `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` (predates the
> install; custodied files are not edited in place); (b) every `**/*RULING*.md`
> under a dated directory ≥ 2026-09-03, excluding `NEEDS-RULING-*` inputs.
> The selected set must be non-empty. Each selected file must contain a
> `## Executed evidence` heading whose section (to the next `^## `) satisfies
> ONE of: (1) a fenced block with a line matching `^\$ .+` AND a different line
> matching `^\s*(?:exit|EXIT|rc|exit code|exit status)[\s=:]+\d+\s*$`; or (2) a
> citation `[A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml):\d+` whose path exists
> at HEAD. `.md:N` is a document pointer and satisfies nothing.

Consequences stated plainly: today the selected set is exactly
`2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` (passes via
branch 1); `171a-RULING-decode-identity.md` (dated 2026-09-02) is NOT selected
— that is the 1-R7 cost of not retro-failing 28 custodied files, accepted.
Rejected: Sol's `revision:/artifact:/Refusal path:` record (heavier than the
ruled text; shape-not-truth residual stands per `:288-290`); Opus's widened
heading regex (a vocabulary list is what failed).

Mutations (must fail after; pass at 2d24ef70): M7 delete the heading from the
09-02 ruling; M8 drop its `exit 0` line and its `.md` citation; a fence whose
only content is `$ echo exit`; a section citing only
`docs/contracts/bridge_protocol.md:48`; positive control: a scratch
`2026-09-09-probe/X-RULING-probe.md` with no evidence section → fails. The
kernel acceptance row `T26-RULING-INSTALL-01` evidence[1] ("mutation-killed")
is FALSE at 2d24ef70 and is corrected in the same commit.

## B2 — dependency placement and test assertions

Seats: all three AMEND to BOTH roles (gated tasks carry hard/start/pending;
the installer carries a non-start pending dep). Sol wrote `scope: finish`;
that value does not exist (`gen_state.py:63` `DEP_SCOPES`) — corrected to
`close`, as Opus and cold Fable wrote.

**Ruled: AMEND.** Bench kernel edit: `T26-RULING-INSTALL-01.dependencies` +=
`{kind: decision, target: D-170, strength: hard, scope: "close", state:
pending, evidence: null, required: "the four T26 verdict mechanisms are
installed and each is proven by a regression that fails when the ruled value
is absent"}`. Invariant 3 blocks only `start`; `_check_dependency`
(`gen_state.py:167-191`) refuses satisfied-without-evidence.

Test `test_open_decisions_name_an_installing_kernel_task`, for each
`open (installs via X)` row with D-number ≥ `DECISION_RULE_FLOOR` (a named
module constant, 170, shared with the B3 test): (1) `X in tasks`; (2) task X
carries ≥ 1 `kind: decision` dep targeting the D-id; (3) some task carries such
a dep with `strength: hard`, `scope: start`, `state: pending`; (4) the number
of index rows parsed equals the number of `^\| D-\d+ \|` rows — a malformed
status cell fails, never skips (Opus F5b). Rejected: Sol's per-decision
gated-task pin list (a maintenance list that limb 3 makes redundant once the
S9 rows register). Counterfactual M4 (`installs via ARM-PACKET-01`) fails at
limb 2; passes today.

## B3 — non-`open` row with a pending decision dep

Seats: Opus ADOPT with ≥ 170 guard; cold Fable ADOPT prospective ≥ 170 (D-110
is `accepted` with a pending dep today); Sol AMEND to a terminal-status list
(a `proposed` row is non-open but non-terminal).

**Ruled: ADOPT, amended with both guards.** For every index row with D-number
≥ `DECISION_RULE_FLOOR`: the leading status token must be in
`{"open", "proposed"} ∪ TERMINAL`, `TERMINAL = {"adopted", "accepted",
"ratified", "recorded", "executed", "adjudicated", "superseded"}`; any other
token FAILS naming the row (unknown status is a defect, not a skip). For a
TERMINAL row, no task may carry a `kind: decision` dep targeting it with
`state: pending`; the message names the status and the task. Controls:
unmodified kernel passes; M6c (D-170 → `adopted`, dep pending) fails; scratch
`D-171 adopted` with no dep passes; scratch `D-171 proposed` with a pending
dep passes. D-110 / `MINT-GENERALIZE-01` is a known pre-rule inconsistency:
kernel row `D110-MINT-DEP-RECONCILE-01` (magistrate registers; the row is
either not really accepted or the dep is stale — Ed's call, batched).

## B4

All seats: no S9 row changes B2. The S9 rows S9-01b/02/03/04/05/06/12 register
at the bench with the hard/start/pending dep and make limb 3 satisfiable by
more than one task, as intended.

## Disposition

Subject A: fix round 2b brief carries A1 + A2 verbatim; delta re-audit by a
model other than the fixing seat; the census tail line is part of the ruled
successful tail. Subject B: the t26-a fix round carries B1/B2/B3 plus the
refuter carry-overs (luna 209 F3/F4; Opus 210 F3/F5/F5b/F6/F7/F8); kernel
edits (dep object, S9 rows, two new rows) at the bench. Magistrate overrules
of a single seat above are each marked "dissent recorded"; no cold verdict on
which the seats agreed was overruled.
