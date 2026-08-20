# EXECUTION LENS — `joulewise/scheduler_gates.py` stages 1–2

Reviewer: Opus 5 execution lens (blind to the contract lens).
Target: worktree `…/scratchpad/wtIMPL`, head `088c20d` + untracked
`joulewise/scheduler_gates.py` (618 lines), `tests/test_scheduler_gates.py` (415 lines).
Method: everything below was **executed**, not read. Attack scripts live beside this
file (`atk1_failopen.py`, `atk2_pin.py`, `atk3_g4.py`, `atk45_writes_vocab.py`,
`atk6_race.py`, `atk7_containment.py`, `atk8_pinauth.py`, `atk9_packleak.py`) and are
re-runnable with `python3 <script>`.

---

## Verdict

**CONDITIONAL GO** for landing stages 1–2 as a PR.

Nothing in this code can authorize a window today: G1/G2/G3/G6 are
`NOT_IMPLEMENTED`, so the composed verdict is structurally `NO-GO` on every path I
could reach. Every malformed input I threw at it failed **closed**. The gate
ordering, the vocabulary closure mechanism, the real multi-process race, and the
"no pack writes" constraint all hold under execution.

The condition: **B-1 below is a latent fail-open in the one gate this stage actually
implements.** It is invisible today only because a sibling gate is a stub. Stage 6
flips those stubs and inherits the pin unchanged. Land stages 1–2 with B-1 fixed in
the same PR, or with B-1 registered as a named blocking row against G5 activation.
S-3 (a fabricated `clean: true` in a custody record) should also land in this round —
it is a three-line change and it is the class of defect this project treats as
disqualifying.

---

## BLOCKER

### B-1 — The G5 campaign boot pin is neither durable nor authenticated; losing or replacing it silently re-anchors the campaign span and G5 returns PASS

G5 exists to detect one falsifier: **a reboot mid-campaign**. Its entire memory of
"which boot this campaign belongs to" is a single plain JSON file,
`campaign_root/campaign_boot_pin.v1`. Three executed results:

**Deletion → silent re-anchor** (`atk2_pin.py` A2.3):

```
first eval (boot A):            verdict=PASS
post-reboot (boot B), pin intact: verdict=REFUSE codes=['scheduler_boot_pin_mismatch']
post-reboot (boot B), pin LOST:   verdict=PASS   codes=[]
new pin boot=22222222-…  (campaign span silently re-anchored to the NEW boot)
```

**The file is not durably linked** (`atk2_pin.py` A2.2). `_create_boot_pin` fsyncs the
file descriptor but never fsyncs the parent directory:

```
file fsync present: True
parent dir fsync present: False
arm_readiness._fsync_directory exists: True
```

This is a divergence from the sibling module's own established pattern, not a
judgement call. In `arm_readiness.py`, `_exclusive_write` (the same `O_EXCL` idea) is
*always* paired with `_fsync_directory(path.parent)` — `:7746`+`:7755`,
`:7758`+`:7762`, and 8 call sites in total. `scheduler_gates` reimplements the
exclusive write inline and drops the pairing. An unclean shutdown or panic can lose an
un-fsynced directory entry — and an unclean shutdown *is the very event G5 exists to
detect*. The gate's own trigger event can disarm the gate.

**The pin is unauthenticated** (`atk8_pinauth.py` 8.2, 8.3, unmocked against the real
`kern.bootsessionuuid` = `da90818c-9c31-45d0-8813-deae65fba143`):

```
8.1 legitimate campaign:  first: PASS
    files alongside the pin: ['campaign_boot_pin.v1']      <- no sha256 sidecar
8.2 hand-planted pin naming the CURRENT boot, backdated to 2023: verdict=PASS
8.3 pin mode = 0o100600 (owner-writable: True)
    after in-place rewrite: verdict=PASS, created_at recorded=1999-01-01T00:00:00Z
```

`O_EXCL` guards **creation only**. Nothing guards mutation or deletion, and there is no
digest to compare against — where `arm_readiness` writes a `gnu_sidecar` digest beside
custody artifacts at **19** call sites, `scheduler_gates` has **0**
(`atk8_pinauth.py` 8.4). The receipt records `pin_created_at_utc` verbatim from the
file and never compares it to anything, so a backdated or re-minted anchor leaves no
detectable trace.

The root design gap under all three: **absence of a pin is treated as "campaign has not
started"**, and nothing else in the custody root is consulted to contradict that.

*Fix shape* — (a) `_fsync_directory(path.parent)` after create, reusing
`arm_readiness._fsync_directory`; (b) write and verify a `gnu_sidecar` digest beside
the pin; (c) make "no pin" refutable — refuse pin creation when the custody root
already holds campaign evidence, so absence can never mean fresh-campaign mid-span.
(c) is the design-bearing part and may be the magistrate's call on scope.

---

## SHOULD-FIX

### S-1 — The pin read follows symlinks while the create refuses them

`atk2_pin.py` A2.6: a symlink planted at the pin path, pointing at another campaign's
pin file, is read and honoured:

```
live=A, pin is symlink->foreign(A): verdict=PASS
```

The asymmetry: `_create_boot_pin` passes `getattr(os, "O_NOFOLLOW", 0)`, which is dead
weight — `O_CREAT|O_EXCL` already refuses *any* existing name including a symlink
(proven at A2.7: a dangling symlink refuses with `scheduler_boot_pin_conflict`). The
create path is never the one that meets a symlink. The unguarded surface is
`Path.read_text` in `_read_boot_pin`. Fix: read via
`os.open(pin, os.O_RDONLY | os.O_NOFOLLOW)`.

### S-2 — The public entry leaks a foreign exception type, produces no receipt, and still leaves an irreversible span anchor behind

`atk9_packleak.py` 9.1/9.2, real `arm_readiness._pack_record` against a non-pack:

```
LEAKED joulewise.arm_readiness.ArmReadinessError: cannot read plan tree: …
 -> callers guarding on SchedulerGateError do not catch this; no refusal receipt exists
pin exists: True
 -> a campaign span is pinned by an evaluation that produced NO receipt
```

Two defects in one path. `evaluate_scheduler_gates` raises `ArmReadinessError`, which
is outside the module's declared error contract (`SchedulerGateError`), so a caller
written against this module's API does not catch it. And because `_pack_record` runs
*after* all six gates, the create-only pin has already been written — a failed
evaluation permanently anchors the campaign span with nothing recording that it did.
The in-code comment justifies the late `_pack_record` placement but does not address
either consequence.

### S-3 — G4 records `clean: true` for a working tree it never observed

`_evaluate_g4`'s `except Exception` fallback fabricates
`{"clean": True, …, "exact_match": False}`. This is reachable in the ordinary failure
modes, not an exotic one (`atk3_g4.py` A3.2/A3.3/A3.4):

```
PATH stripped of git   -> REFUSE, recorded clean=True head='unavailable'
.git chmod 000         -> REFUSE, recorded clean=True head='unavailable'
pack outside any repo  -> REFUSE, recorded clean=True head='unavailable'
   probe-error marker in observations: NONE
```

Three problems. (1) The receipt makes an affirmative claim — "the working tree was
clean" — about an observation that never happened; the fail-closed value is `False`.
(2) The emitted code is `readiness_reviewed_main_mismatch`, which asserts a *mismatch*
that was likewise never observed; `SCHEDULER_ENVIRONMENT_REASON_CODES` already exists
in the vocabulary and is currently unreachable as a gate refusal. (3) A consumer
cannot distinguish an exception from a real read — the records are the same shape
(A3.5):

```
genuine   : {"clean": true, "exact_match": false, "head_commit": "523b3173…", …, "origin_main_commit": "unavailable"}
fabricated: {"clean": true, "exact_match": false, "head_commit": "unavailable", …, "origin_main_commit": "unavailable"}
```

Reachability into a full receipt confirmed at `atk9_packleak.py` 9.3 — with a valid
pack record the fabricated `reviewed_main` lands verbatim in the receipt body.

### S-4 — `validate_scheduler_gate_receipt` does not enforce the staged invariants its docstring claims, and leaves `assurance`/`pack`/`reviewed_main` entirely unchecked

Docstring: *"Validate the exact v1 receipt shape and staged verdict invariants."*
Executed (`atk1_failopen.py`):

```
A1.1  6x PASS -> GO                              ACCEPTED
A1.2  6x RECORD_ONLY -> GO                       ACCEPTED
A1.3  6x PASS -> GO + claim_admissible=True      ACCEPTED
A1.14 assurance claims independent_attestation   ACCEPTED
```

No producer at this head can emit `PASS` for G1/G2/G3/G6, and the producer hardcodes
`claim_admissible: False` because G3 owns claim admission and is a stub — yet a receipt
asserting all four passed *and* that the window is claim-admissible validates clean.

`assurance` is checked only as `isinstance(Mapping)`. The sibling
`arm_readiness._validate_assurance` (`:1247-1252`) enforces
`dict(assurance) == ASSURANCE` exactly, refusing with *"must carry the D-120
qualifier"*. Here a receipt may claim `independent_attestation: true` — the precise
field arm_readiness protects. `pack` and `reviewed_main` are likewise any-Mapping,
where arm_readiness validates `PACK_KEYS` exactly (`:1369`).

Mitigating: the ruling binds the gate receipt into the GO receipt by sha, so forging
one requires custody write access. But this validator is the module's only stated
authentication surface, and its docstring currently overclaims. At minimum: correct
the docstring, adopt `_validate_assurance`'s exactness for `assurance`, and pin the
staged verdict set (G1/G2/G3/G6 ∈ {NOT_IMPLEMENTED, NOT_EVALUATED}) so stage 6 must
consciously remove the pin.

### S-5 — Refusal codes are closed at module level, not gate level

The per-gate sets `G1_REASON_CODES`…`G6_REASON_CODES` exist but are only unioned;
nothing binds a code to its gate (`atk45_writes_vocab.py` 4.2/4.3):

```
cross-gate mints accepted by _gate_refusal: 160
  e.g. ('G1','readiness_git_tree_dirty','G4'), ('G1','scheduler_b22_binding_absent','G3')
receipt validator: ACCEPTED G4 carrying G6's code 'scheduler_c4_network_time_on'
```

The receipt's `gate_id ↔ code` binding is exactly what a downstream consumer would use
to attribute a refusal, and it is unenforced at both mint and validate.

### S-6 — A failed pin write leaves a 0-byte pin that permanently bricks the campaign

`atk45_writes_vocab.py` 5.7 (write failure injected after the `O_EXCL` create succeeds,
i.e. the ENOSPC/EIO shape):

```
create refused: scheduler_boot_pin_conflict
residue left behind: exists=True size=0
subsequent evaluation: REFUSE ['scheduler_boot_pin_conflict']
   (campaign now permanently refusing with no in-module cure)
```

Fail-closed, but unrecoverable without manual filesystem surgery. `arm_readiness`
solves exactly this with `_atomic_replace` (mkstemp + `os.replace`, `:3585`).

---

## NITS

- **N-1 — the race test does not test the race.**
  `test_concurrent_create_loser_refuses_as_conflict` mocks `os.open` to raise
  `FileExistsError`; it exercises the `except` branch, not atomicity. I ran the real
  thing — 8 concurrent processes × 5 trials, 8 distinct boot ids, barrier-synchronised
  (`atk6_race.py` A6.1): **exactly one PASS per trial, the winner always matching the
  written pin, all 7 losers `scheduler_boot_pin_conflict`, zero exceptions.** The
  behaviour is correct; the test is simply not the evidence for it.
- **N-2 — containment breadth is asymmetric on the gate that must always produce a
  verdict.** `_evaluate_g4` catches bare `Exception`; `_evaluate_g5` catches only
  `SchedulerGateError`. Every G5 test mocks `_live_boot_session_id`, so the
  `ArmReadinessError → scheduler_boot_pin_underivable` translation inside it is never
  exercised by the suite. I exercised it directly and it is correct (A6.3); a
  non-`ArmReadinessError` from the probe escapes uncaught (A6.3/A6.4 — `UNCAUGHT
  OSError: boom <- no refusal receipt is produced at all`). In practice
  `_current_boot_session_id` normalises OSError/SubprocessError itself, so this is a
  narrow gap.
- **N-3** — a non-Mapping `receipt_boot_session_ids` raises `AttributeError` /
  `TypeError` / `ValueError` before the `try` block (A2.12): fail-closed crash, no gate
  result.
- **N-4** — `now_monotonic_ns` is caller-supplied and unvalidated beyond non-negative
  int; `2**80` is accepted and recorded verbatim (`atk7`). Harmless while G1/G2 are
  stubs; it is the input those gates will trust.
- **N-5** — G4 shells `git status`, which refreshes `.git/index`. That is the only
  repo-tree mutation observed (5.3: `.git` and `.git/index` mtimes changed). Inherited
  from `arm_readiness.reviewed_main` and pre-arm only, but flagged because "no pack
  writes" is a ruled constraint and this is adjacent to it.
- **N-6** — on a G5 refusal the receipt's top-level `boot_session_id` is the literal
  string `"unavailable"` and validates (non-empty string): a magic value in an identity
  field.

---

## POSITIVE FINDINGS (executed — worth recording so they are not re-litigated)

- **P-1 — writes are exactly what was ruled.** Full write tracer over `os.open` and
  `builtins.open` across a complete `evaluate_scheduler_gates` run
  (`atk45_writes_vocab.py` 5.1–5.6): **one** write-mode open in the entire evaluator —
  `campaign/campaign_boot_pin.v1`, mode `0o600`. Pack root byte-identical before and
  after (`pack/ entries changed: NONE`). The module contains no receipt write path at
  all (`write_text` occurrences: 0). The "no pack writes" constraint holds.
- **P-2 — G4 uses the real predicate and its classifier cannot be made to diverge.**
  `arm_readiness.reviewed_main` is called once with the pack root (A3.1) — the probe is
  not reimplemented. `_g4_failed_conjunct` was swept against `reviewed_main`'s own
  `exact_match` predicate over all 54 combinations of (head, local_main, origin_main)
  × clean (A3.6): **mismatches = 0**. No divergence input exists.
- **P-3 — every git hard-failure mode fails closed** (A3.2/A3.3/A3.4): git binary
  absent, `.git` unreadable, pack outside a repository → `REFUSE`.
- **P-4 — nine pin-corruption shapes all refuse** with `scheduler_boot_pin_conflict`
  (A2.5): truncated JSON, wrong shape, empty file, non-UTF-8 bytes, `null`, `[]`, bad
  schema_version, empty boot_session_id, non-string boot_session_id. Plus: pin is a
  directory, pin `chmod 000`, 10 MB pin, symlink-loop custody root, missing root, root
  is a file, read-only root — all refuse (`atk7`).
- **P-5 — the reboot falsifier is real, not a mock that always refuses.** Against the
  **unmocked** live `kern.bootsessionuuid` (A2.1 returns a genuine UUID): a planted
  foreign pin → `REFUSE scheduler_boot_pin_mismatch` (A6.5); a matching pin → `PASS`
  (5.5, 8.1). The refusal is driven by the comparison, not by the patch.
- **P-6 — composition cannot be talked into GO.** `NOT_IMPLEMENTED`, `NOT_EVALUATED`,
  or `REFUSE` in any slot, empty gate lists, six duplicated gate ids, reversed order,
  and unknown gate ids are all rejected (A1.4–A1.8). Gate order is pinned to G5-first
  and verified at runtime — observed call order
  `['G5:boot_probe', 'G4:reviewed_main', 'pack_record']` (9.4).
- **P-7 — vocabulary closure works where it is closed.** Unregistered codes are
  rejected at mint *and* at validate (4.1, A1.12). `mirrored_from` is **not spoofable**
  — the exact-key check rejects the extra key on a scheduler-only code (4.4), a wrong
  value (A1.10), and a stripped value (A1.11). Scheduler codes are disjoint from
  `READINESS_REASON_CODES`, G4's two codes are genuine members of it, and their `type`
  values agree with `arm_readiness.REASON_TYPE_BY_CODE` (4.5).

---

## Test-suite skips

**The new module contributes zero skips.**

```
python3 -m unittest tests.test_scheduler_gates -v
Ran 23 tests in 0.927s — OK      (0 skipped)
```

All 23 tests pass and none is conditional; there is no `skipUnless`, `skipIf`, or
`SkipTest` anywhere in `tests/test_scheduler_gates.py`. The reported +5 skip delta
(100 vs 95) therefore cannot be attributed to this change — it is environmental drift
in this checkout, not a skipped falsifier introduced by stages 1–2. Full-suite figures
appended below.

The two *falsifier-shaped* weaknesses I did find are not skips but **mocks standing in
for mechanisms** — N-1 (mocked `os.open` instead of a real race) and N-2 (mocked
`_live_boot_session_id` in every G5 test). I executed both mechanisms directly and both
are correct; the tests just do not prove it.

---
---

# DELTA RE-AUDIT — fix round (same two files, 618→761 / 415→574 lines)

All attacks below were **re-executed** against the fixed module
(`delta.py`, `delta_race.py`). Focused suite: **33/33 OK, 0 skips.**

## Per-finding disposition

| # | Finding | Status |
|---|---|---|
| B-1b | parent-dir fsync | **CURED** — 2 `_fsync_directory` calls in `_create_boot_pin`, pin and sidecar each fsync'd then dir-fsync'd |
| B-1c | pin sha256 sidecar + receipt binding | **CURED (for corruption/naive tamper)** — planted pin with no sidecar → REFUSE `conflict`; pin rewritten with stale sidecar → REFUSE `conflict`; validator enforces `campaign_boot_pin_sha256 == G5.observations.pin_sha256` and forbids a passing G5 with a null digest |
| F1 | forged staged GO | **CURED** — `6×PASS→GO`, `6×RECORD_ONLY→GO`, `GO+claim_admissible`, `G3/G6 RECORD_ONLY→GO` all refused by the new staged-verdict pins |
| S-5 | cross-gate codes | **CURED** — cross-gate mints accepted: **160 → 0**; validator refuses `scheduler_c4_network_time_on` under G4; own-code control still accepted |
| N-1 | race test was a mock | **CURED** — and re-verified independently: real 8-process × 5-trial race, **exactly one PASS per trial, winner always matches the pin, 0 exceptions**, both pin and sidecar present |
| B-1a | missing pin amid custody history | **PARTIAL — see ND-0** |
| S-1 | symlink-following read | **STILL-FAILS** |
| S-2 | `ArmReadinessError` leak + pin side effect | **STILL-FAILS** |
| S-3 | G4 fabricates `clean: true` | **STILL-FAILS** (and the fix route narrowed — see below) |
| S-4 | `assurance` unvalidated | **STILL-FAILS** (its `claim_admissible` limb is cured structurally) |
| S-6 | failed-write residue bricks the campaign | **STILL-FAILS, window widened** |

## New defects introduced by the fixes

**ND-0 — the empty-custody-root rule does not close B-1a.** The rule fires only
when *something else* is in the root. But this module writes **no receipts**, so
after a first evaluation the custody root contains exactly the pin and its sidecar —
that is the steady state of a stage-1/2 campaign. Delete both and the root is empty
again:

```
create:                                      PASS
root: ['campaign_boot_pin.v1', 'campaign_boot_pin.v1.sha256']
BOTH deleted -> root empty -> post-reboot boot B:  PASS
>>> BYPASS: re-pinned to 22222222 (the NEW boot)
```

The bypass B-1 described is intact whenever the pin and sidecar are lost together —
which is precisely what an unclean shutdown, a directory-level restore, or a cleanup
script does. (With other custody content present the rule does work: pin-only and
pin+sidecar deletion both REFUSE `scheduler_boot_pin_underivable`.)

**ND-1 — a legitimate campaign whose custody root is not literally virgin can never
be pinned, permanently, with no cure:**

```
fresh campaign, root holds one pre-existing plan file: REFUSE ['scheduler_boot_pin_underivable']
fresh campaign, root holds only .DS_Store:            REFUSE ['scheduler_boot_pin_underivable']
fresh campaign, root holds only an empty subdirectory: REFUSE ['scheduler_boot_pin_underivable']
```

On the target platform a Finder visit to the custody root creates `.DS_Store`. That
permanently blocks G5 for that campaign during a scarce hardware window. Fail-closed,
so it cannot authorize a bad window — but it can block a good one, and it is a
one-predicate fix (require "no pin AND no sidecar AND no *campaign evidence*", not
"no directory entries").

**ND-2 — the sidecar is self-referential, so it detects corruption, not substitution.**
Pin and sidecar are both 0600 and rewritten together:

```
pin+sidecar rewritten consistently: PASS
digest before=6d6bb592998f after=0d038560fb06 created_at now=1999-01-01T00:00:00Z
```

`campaign_boot_pin_sha256` is bound into the receipt but only ever compared to the
same receipt's own G5 observations. Nothing compares it across receipts, so a
substituted anchor is still undetected. Also: a hand-planted pin **with** a matching
sidecar PASSes.

## Still-failing, re-executed

```
symlinked pin+sidecar into a foreign campaign:  PASS   (S-1: reads still follow symlinks)
public entry, non-pack:  LEAKED ArmReadinessError ... ; pin created anyway: True   (S-2)
sidecar write fails after pin create: residue ['campaign_boot_pin.v1'];
   every later evaluation REFUSE ['scheduler_boot_pin_conflict']   (S-6, now a wider window)
assurance claims independent_attestation:  ACCEPTED   (S-4)
G4 with reviewed_main raising:  REFUSE ['readiness_reviewed_main_mismatch']
   recorded clean=True, probe marker=NONE   (S-3)
```

S-3's fix route narrowed: `scheduler_environment_error` now belongs to **no** gate, so
it is unmintable as a gate refusal (`ENV code under G5: refused`). Fixing S-3 properly
now needs a gate-owned probe-failure code, not just a call-site change.

## Vocabulary closure after the fix

```
vocabulary size: 33 (unchanged); cross-gate mints accepted: 0
scheduler-only codes disjoint from READINESS_REASON_CODES: True
G4 codes subset of READINESS_REASON_CODES: True
```

Closed, gate-scoped, no new codes. `mirrored_from` remains unspoofable.

## Suite counts

- Focused: `Ran 33 tests — OK`, **0 skips**.
- Full suite at the pre-fix head: `Ran 3783 tests in 2650s — OK (skipped=95)`.
  **The claimed +5 skip delta does not reproduce** — this head sits at 95, the same as
  the stated baseline, and none of the 95 comes from this module: 69 retired site lane,
  9 matplotlib absent, 3 U2 pending, 3 corpus absent, 2 D-079 inputs, 3 jsonschema, 1
  each Darwin-live opt-in / D117 partition / full-fixture proof. There is no skip
  regression and no skipped falsifier.
- The fix report's flag F1 is honest: its unmocked sysctl test hit a sandbox denial and
  exercised only G5's fail-closed branch. I verified the other branch directly — the
  real `kern.bootsessionuuid` derives cleanly here (`da90818c-…`) and drives both a
  genuine PASS and a genuine `scheduler_boot_pin_mismatch`.

## Delta verdict

**GO** to land stages 1–2 as a PR, with **ND-1 fixed in this round** (one predicate;
a `.DS_Store` should not be able to brick a hardware window) and **ND-0 + S-1 + S-3
registered as named blocking rows against G5/G4 activation** before any gate leaves
`NOT_IMPLEMENTED`. The fix round genuinely closed the forged-GO surface, the
cross-gate vocabulary leak, the durability gap, and both mocked mechanisms; what
remains is fail-closed or latent, and stages 1–2 still cannot compose a GO by
construction.
