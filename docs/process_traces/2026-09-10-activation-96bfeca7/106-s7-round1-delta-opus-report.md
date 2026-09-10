# 106 — Seat S7 fix round 1 DELTA RE-AUDIT (execution lens, Opus)

Worktree `/Users/edr/code/JouleWise-wt-s7-night-wrapper`, HEAD `2d43c985`,
round `94e4fc89 → 2d43c985`. Read-only except temporary mutation cuts to
`scripts/gen_derivation_night.py`, each restored and re-hashed
(`34ac162c…a40ef` before and after every cut; harness asserts it).
`git status --porcelain` empty at start and end. No git state changes, no
captures, no `[QUIET-MAC]` work, no sudo; canonical, `~/night-custody` and
other worktrees untouched. Every subprocess ran with
`PYTHONDONTWRITEBYTECODE=1`; every wrapper launch used the seat's fake
interpreter (stops at the reservation, rc 3 — never sleeps, never captures).

File hashes at HEAD:

```
34ac162c6737f42a52258bd4ba07a6fe0f284a3092e1965585d07f6c338a40ef  scripts/gen_derivation_night.py
cc8b5407de5372a2dcee1420881ff4016ef2f9e2d70905e8f9a90d3ab7cdfeb7  tests/test_gen_derivation_night.py
4d7dda5edc2280f1b83c2c46c489541247eb49eca81ea2f94d44b8ae1425e4e1  docs/.../SHAKEDOWN-G2-RUNSHEET.md
```

## VERDICT — should_fix

Every finding the round set out to answer is **cured and defect-shape tested**:
F1/B-1 (chain digest now a literal in the plan-pinned bytes — the exact 104
attack refuses before `exec`), B-2 (window-fit fence, boundary exact), F3
(digest taken from the measurement clone), S-1, S-2, F5, F6, S-4. 16 of 16
independent cuts were killed. `Ran 202 tests … OK`; both region checks PASS.

Three defects remain, two of them **introduced or left behind by this round**,
none of them a blocker (all fail safe, before `exec`):

- **D-1** the round's own arm-order step 4 prescribes an emission the generator
  refuses — the arm procedure as written cannot be executed;
- **D-2** F4 is cured for 3 of its 4 paths: the `jq` plan-id extraction still
  exits **1 with empty stderr**, under a comment this round added asserting the
  opposite;
- **D-3** `--slot-count-ruling` (new this round) is interpolated unescaped into
  the wrapper's header; a newline in it injects executable code that `zsh -n`
  accepts.

---

## Findings

### D-1 — SHOULD-FIX (new this round). The documented arm step 4 is unexecutable, and it is the step that makes B-1's cure useful.

Region, `SHAKEDOWN-G2-RUNSHEET.md` arm order step 4 (generator `render_region`):

> **Re-emit and assert byte equality** at arm time: emit a second copy **to a
> scratch path** and require identical bytes.

The generator refuses any `--out` that is not the plan's `chain_path`
(`build_spec`, and `test_an_out_path_that_is_not_the_plans_chain_path_refuses`
pins it). Executed at HEAD (`/tmp/s7-delta/step4.py`):

```
first emit rc 0
step-4 'emit a second copy to a scratch path' rc= 2 |
FAIL --out …/night-custody/derivation-20260912/scratch-chain.zsh is not the plan's
     chain_path '…/night-custody/derivation-20260912/chain.zsh'
scratch exists: False
```

This is the arm-time tripwire that turns the baked chain digest into a detection
(104 F1(b) is closed *by* this step), so an operator who follows the text, hits
`FAIL`, and improvises is improvising on the one step that catches a changed
capturing chain. Fix (documentation only): `cp` the emitted wrapper aside, re-run
the generator over `chain_path`, `cmp` the two — or add a `--verify-only` mode.

### D-2 — SHOULD-FIX. F4 is cured for three paths of four; the fourth still refuses with an EMPTY stderr, under a comment that says it cannot.

The wrapper now carries (rendered line 56–58):

```
# Every refusal below prints FAIL <reason> to stderr: the driver
# redirects this stream to a file, and an unattended night's only
# forensic record of a 3 a.m. refusal is what is written here.
```

Eleven lines below it, the plan-id extraction is an unguarded assignment:

```
observed_plan_id="$(/usr/bin/jq -er '.plan_id' "$PLAN")"
```

Under `set -e` a `jq` failure kills the wrapper with no `route_refuse`. Executed
at HEAD against a live emitted wrapper (`/tmp/s7-delta/probe.py`):

| frozen plan state | rc | stderr | calls |
|---|---|---|---|
| intact (baseline) | 3 | `''` | 2 (readiness + reservation) |
| `{ not json` | **5** | `jq: parse error: Invalid numeric literal at line 1, column 6` | 0 new |
| `{"other": 1}` (no `plan_id`) | **1** | `''` | 0 new |

The second row is verbatim the F4 defect the round claims to have eliminated —
rc 1, empty stream, indistinguishable from a `route_refuse` — and the commit
message's "FAIL `<reason>` on every refusal" and the emitted comment are both
false as written for this path. It fails safe (nothing ran), so it is
diagnosability, not correctness. Note also the ordering: because `jq` runs
*before* the digest comparison, a corrupt or truncated frozen plan reports a
`jq` parse error rather than `frozen plan bytes do not equal the arm-time
digest`. Fix (1 line): `… 2>/dev/null)" || route_refuse 'frozen plan is not JSON
with a plan_id'`, and/or move the digest check above the extraction.

### D-3 — SHOULD-FIX (new this round). `--slot-count-ruling` is interpolated into the wrapper's header with no escaping; a newline injects executable code and `zsh -n` passes.

`render_wrapper`'s `departure` block builds `f"# … Authorising ruling: {spec.slot_count_ruling}."`.
The value is never `_census_clean`ed and never checked for control characters
(every other emitted literal goes through `_census_clean` / `_require_absolute`).
Executed at HEAD (`/tmp/s7-delta/ruling.py`), ruling =
`"ok\nexport SLOT_COUNT=99\n# codex-claude"`:

```
emit rc 0
#!/bin/zsh
# GENERATED by scripts/gen_derivation_night.py — do not edit; re-emit.
# Derivation-night wrapper for night plan derivation-20260912.
#
# DEPARTURE FROM THE PRE-REGISTRATION: this night declares 6 slots,
# not the pre-registered 12. Authorising ruling: ok
export SLOT_COUNT=99          <-- live code, not a comment
# codex-claude.
...
zsh -n rc 0
```

`/bin/zsh -n` (arm step 5) accepts it, so the documented arm catches nothing.
In this instance the injected line is later overridden by the wrapper's own
`export SLOT_COUNT='6'`, so it is inert — but the injection point precedes all
wrapper code and any statement would run. This is a quoting defect, not only an
adversary story: a pasted multi-line ruling reference produces it by accident.
Fix (1 line): route the value through `_census_clean` and reject anything
matching `[[:cntrl:]]`, or comment-prefix every line of it.

### Nits (no action required)

- **N-1** 10 of the 18 `route_refuse` paths have no test asserting their reason
  (enumeration below). 104 executed four of them live at the previous HEAD.
- **N-2** Region pedagogy, first-use test: the refusal paragraph puts two
  *different* 300 s constants in adjacent clauses — "plus the 300 s pre-settle
  allowance" (`PRE_SETTLE_ALLOWANCE_S`) and "`t0 + window_max_s + 300 s` … (the
  dead-man)" (`COURIER_DEADLINE_S`) — and never distinguishes them; "pre-settle
  allowance" is used before it is built (the generator's own constant comment
  explains it; the region does not). A reader cannot tell from the text that
  these are two separate budgets that happen to share a number.
- **N-3** `git` (rendered line 27) is the only PATH-resolved external command in
  the wrapper — `shasum`, `awk`, `jq`, `zsh`, `sleep`, `date` are all absolute —
  and the driver hands the chain `os.environ.copy()` (`run_night.py:430`), so
  the arming operator's `PATH` reaches it. It can only *cause* a refusal here
  (verified below), and the digest literals pin the bytes regardless. D-161
  operator-adversary class; recorded, not a finding.

---

## Cut table (16/16 killed; generator sha256 identical before/after each)

| # | Cut | Test run | Result |
|---|---|---|---|
| C1 | in-wrapper chain-digest equality → no refusal (`route_refuse …` → `true`) | `test_rewriting_the_advisory_sidecar_cannot_move_the_pin` | KILLED (`3 != 1` — the night ran) |
| C2 | digest source → the generator's own repo (F3 regression) | `test_the_chain_is_digested_from_the_measurement_clone` | KILLED |
| C3 | `chain_sha256=` literal → constant (B-1 regression) | `test_the_chain_digest_is_a_literal_in_the_wrapper_bytes` | KILLED |
| C4 | `sha256_of` → truncated digest (`substr($1,1,32)`) | `test_rewriting_the_advisory_sidecar_cannot_move_the_pin` | KILLED |
| C5 | `+ PRE_SETTLE_ALLOWANCE_S` → `+ 0` | `test_a_window_too_short_for_the_programmed_span_refuses` | KILLED |
| C6 | `(slot_count − 1)` → `slot_count` | `test_the_span_constants_are_the_chains_own_defaults` | KILLED (`8280 != 7680`) |
| C7 | `DEFAULT_SETTLE_S` 600 → 599 | same | KILLED (`':-599}' not in 'SETTLE_S="${SETTLE_S:-600}"'`) |
| C8 | `DEFAULT_SLOT_CADENCE_S` 600 → 599 | same | KILLED |
| C9 | `DEFAULT_SLOT_CAPTURE_BUDGET_S` 480 → 479 | same | KILLED |
| C10 | one `FAIL` print removed (`… || route_refuse 't1 bindings json is missing'`) | `test_every_in_wrapper_refusal_prints_a_reason` | KILLED (`'' != 'FAIL t1 bindings json is missing'`) |
| C11 | identity-epoch digest refusal → `true` (S-1) | `test_modified_identity_or_t1_bytes_refuse` | KILLED |
| C12 | one `CHAIN_ANCHORS` text edited (trailing space) | `test_every_chain_citation_resolves_to_a_real_chain_line` | KILLED (`0 != 1`) |
| C13 | receipt-class allow-list → old pack-only guard | `test_a_non_diagnostic_receipt_class_refuses` | KILLED |
| C14 | `--slot-count-ruling` requirement removed | `test_departing_from_twelve_slots_requires_a_named_ruling` | KILLED |
| C15 | DEPARTURE header block removed | same | KILLED |
| C16 | region arm-order heading removed | `test_the_region_documents_the_third_file_and_the_arm_order` | KILLED |

Harness: `/tmp/s7-delta/cuts.py`, `/tmp/s7-delta/cut3.py` (each writes the cut,
runs one test, restores `ORIG` bytes, asserts sha256 == `34ac162c…a40ef`).

---

## Item-by-item verification

### 1. F1/B-1 — the 104 attack, live at HEAD (`/tmp/s7-delta/live.py`)

Emitted from the seat's fixture (real one-commit clone), launched exactly as
`run_night.py:430-444` does (`/bin/zsh <wrapper>`, `cwd=/`, `stdin=DEVNULL`,
env = `PATH=/usr/bin:/bin` + `NIGHT_PLAN_ID`/`MEASUREMENT_ROOT`/`MEASUREMENT_HEAD`/`PY`):

```
A baseline launch: rc 3, 2 calls (readiness + reservation)
B chain edited (1 byte) + advisory sidecar rewritten to match:
  rc 1  FAIL tracked derivation chain bytes do not match the arm-time digest   0 calls
C same, advisory sidecar DELETED:
  rc 1  FAIL tracked derivation chain bytes do not match the arm-time digest   0 calls
D re-emit after the chain edit → wrapper bytes CHANGED (e3315b2ecf2b4008 → 4a6895c493eeec52)
E restore the chain + re-emit → wrapper bytes byte-identical to the original
```

B is 104 F1(a) reproduced and now refused **before `exec`**; C shows the advisory
sidecar is genuinely not load-bearing; D is 104 F1(b) closed (the arm's re-emit
comparison now moves with the capturing bytes). Rendered wrapper line 80 carries
the literal `… = 'd6d23bff48d4…70a65' || route_refuse …`.

### 2. B-2 — window fit, boundary and constants

`test_a_window_too_short_for_the_programmed_span_refuses` asserts the exact
message `window_max_s 3600 < required 7680 + 300 = 7980`, then 7979 → rc 2 and
7980 → rc 0. The constants are the chain's own, read at HEAD from
`scripts/night_chains/calibration_derivation_only.zsh`:

```
66:SLOT_COUNT="${SLOT_COUNT:-12}"
67:SETTLE_S="${SETTLE_S:-600}"
68:SLOT_CADENCE_S="${SLOT_CADENCE_S:-600}"
71:SLOT_CAPTURE_BUDGET_S="${SLOT_CAPTURE_BUDGET_S:-480}"
```

600 + 11×600 + 480 = 7680; + 300 = 7980. C5–C9 each kill a test.

### 3. F4 — refusal-path enumeration of the rendered wrapper

18 `route_refuse` paths + 1 unguarded exit. "Reason asserted" = the reason string
appears in `tests/test_gen_derivation_night.py`.

| Rendered line | Refusal reason | Reason asserted by a test |
|---|---|---|
| 15 | `measurement_root is required` | no (104 executed) |
| 18 | `measurement_root must be an absolute path` | no |
| 20 | `measurement_root contains control characters` | no |
| 21 | `measurement_head must be a full 40-character lowercase SHA-1` | no |
| 23 | `night plan id does not match the wrapper` | **yes** |
| 24 | `measurement_root does not match the wrapper` | no (104 executed) |
| 25 | `measurement_head does not match the wrapper` | no (104 executed) |
| 27 | `checkout HEAD cannot be read` | no |
| 28 | `checkout HEAD does not equal measurement_head` | no (executed here, item 7) |
| 32 | `measurement venv Python is missing or not executable` | no |
| 62 | `frozen calibration plan is missing` | **yes** (C10-class) |
| 63 | `identity epoch json is missing` | **yes** |
| 64 | `t1 bindings json is missing` | **yes** (C10 kills it) |
| 67 | *(unguarded `jq` assignment — rc 1 empty stderr / rc 5)* | **no — D-2** |
| 68 | `frozen plan id does not equal the arm-time literal` | no (104 executed) |
| 69 | `frozen plan bytes do not equal the arm-time digest` | **yes** |
| 72 | `identity epoch bytes do not equal the arm-time digest` | **yes** (C11) |
| 73 | `t1 bindings bytes do not equal the arm-time digest` | **yes** |
| 80 | `tracked derivation chain bytes do not match the arm-time digest` | **yes** ×2 (C1, C4) |

8 of 18 asserted; the whole routing preamble is covered only indirectly by
`test_the_wrapper_reaches_the_reservation_with_all_bindings` (happy path) and by
104's live table at the previous HEAD. N-1.

### 4–6. S-1 / S-2 / F5 / F6

`test_modified_identity_or_t1_bytes_refuse` breaks each file's bytes and asserts
rc 1, the reason, and `calls == []` (C11 kills it).
`test_every_chain_citation_resolves_to_a_real_chain_line` asserts every
`CHAIN_ANCHORS` value occurs **exactly once** in the chain and that
`"calibration_derivation_only.zsh:"` appears nowhere in the generator (C12 kills
it); I confirmed the generator contains no such citation.
`REHEARSAL_STUB` → rc 2, `a derivation night is DIAGNOSTIC_NO_PACK; this plan is
REHEARSAL_STUB` (C13). `--allow-slot-count` without `--slot-count-ruling` → rc 2;
with it → rc 0, `DEPARTURE …` on stderr and the DEPARTURE block in the header
(C14, C15) — see D-3 for the escaping defect in that block.

### 7. Hostile environment at HEAD

Launched with `SLOT_COUNT=3 SESSION_ID=attacker WINDOW_END_EPOCH_S=1 SETTLE_S=0
SLEEP=/bin/true DATE=/bin/true PLAN_SHA256=0×64 REPO=/tmp` pre-set:

```
F rc 3 | reservation --slot-count 12 | 12 --slot-attempt-id |
  first attempt id derivation-20260912-epoch-d01
```

The wrapper's own `export` lines win over every pre-set value; nothing hostile
reached the reservation. With `shasum`, `awk`, `jq` and `git` all shadowed on
`PATH` by `echo EVIL` stubs:

```
G rc 1  FAIL checkout HEAD does not equal measurement_head   0 calls
```

Confirmed by inspection of the rendered bytes: the only external commands are
`/usr/bin/shasum`, `/usr/bin/awk`, `/usr/bin/jq`, `/bin/zsh` (absolute),
`/bin/sleep` and `/bin/date` (absolute, exported as `SLEEP`/`DATE`), `printf`
(builtin) — and bare `git`, which is PATH-resolved (N-3).

### 8. Region checks and prose

```
python3 scripts/gen_g2_phase_d.py --check      → PASS generated Phase D matches pinned runbook bytes   rc 0
python3 scripts/gen_derivation_night.py --check → PASS generated derivation-night wrapper region matches rc 0
```

Arm-order paragraph, first-use test: **"wrapper", "the clone", "the three
emitted files", "advisory", "programmed span" and "dead-man" are all built or
glossed at first use, and the why-chain (four driver variables vs thirteen chain
variables) precedes the mechanism** — above the bar. Two defects: step 4 is not
executable (D-1) and the two distinct 300 s constants are undifferentiated
(N-2).

### 9. Test run

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_derivation_night \
  tests.test_issue_calibration_acceptance_generation tests.test_run_night
Ran 202 tests in 75.514s
OK
```

## Reproducing commands

```
cd /Users/edr/code/JouleWise-wt-s7-night-wrapper           # HEAD 2d43c985
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/live.py    # F1/B-1 attack, hostile env, PATH shadow
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/probe.py   # D-2: jq path, empty stderr
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/step4.py   # D-1: documented arm step 4 refuses
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/ruling.py  # D-3: newline in --slot-count-ruling
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/cuts.py    # cut table C1..C16 (minus C3)
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s7-delta/cut3.py    # cut C3
```
