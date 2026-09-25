# Opus 5.5 — blind consult on the A280 B0 escalation

## Q1. Root cause

**B0 swapped something that could never fail for something that can.** At base, every idle-only site used the constant `KIND`. Looking up a constant can't fail, so those sites had no failure modes of their own. Head replaces each lookup with a fresh read of files on disk:
- `selected_candidate_row` reads the wrapper, its digest sidecar, the chain source and the binding (`evidence_night.py:311-336`). It is called at 7 sites: `:341, :346, :689, :1088, :1128, :1719`, plus the pre-read in `sealed_candidate` at `:242-252`.
- `_custody_row` does the same in the driver (`run_night.py:1005-1027`).

Each new read can fail, and it fails on exactly the malformed inputs. It also runs before the base's own checks at that site, with its own refusal text. The diff adds 22 new refusal or raise texts. Every one of them is a place where idle behaviour can change.

A fix round cures the named inputs. It does not shrink the set of inputs on which the new reads fail, so the next audit finds another member of that set. The two rounds failed the same way for the same structural reason.

Executed probes that decide it:
- **The kind classifier is a heuristic, not an authenticator.** `probe_payload_kind` (`night_gate.py:150-164`) returns `calibration` for a stripped idle wrapper. It raises on duplicated declarations, on a mixed `CALIBRATION_LEDGER`, and on unknown kinds. At idle sites a stripped wrapper therefore becomes "no approved evidence handler", where base said "failed wrapper sidecar" (F2). A bare wrapper gets the same treatment in `_custody_row` (F4).
- **F1 comes from a second parser for data that was already checked.** Base parses the receipt with `json.loads(read_bytes())` (`run_night.py:1377`). `_custody_row` uses `read_text()` (`:1009`). Probe results:
  - BOM receipt: base `ok`, head `JSONDecodeError`.
  - UTF-16 receipt: base `ok`, head `UnicodeDecodeError`.

  Base's only kind source for cleanup was the payload kind in the C5 receipt, which it had already validated. Head adds a wrapper read on top of that, which adds a failure mode.
- **F3:** `MappingProxyType.get([])` and `.get({})` raise `TypeError` (lists and dicts can't be dictionary keys). This fires before the base refusal at `evidence_night.py:639`.
- **Order change:** the new check at `evidence_night.py:689` runs before `checkout_ok` (`:691`), so a changed bound source says "differs from sealed binding" instead of "dirty clone".

**Can lenses check "idle byte-identical on every path"?** Not as a semantic property. It is a claim about every possible input. A lens can produce counterexamples, but it can't show there are none left. The audit witnesses were already executed probes, which is ad-hoc differential testing.

The claim can become lens-checkable if the code is shaped so parity follows from local facts:
1. Idle inputs run base code, with base constants, in base order.
2. The function that picks the route is total (never raises) and returns the idle route whenever it isn't sure.
3. Every new refusal sits inside a branch that the production table can't reach.

A lens checks those three by reading. A harness then confirms them over a corpus.

## Q2. Candidate cures

| Option | Cost | Guarantee |
|---|---|---|
| (a) Differential harness, base vs head | One seat, about 3–4 h, 400–700 lines. Each side runs in its own subprocess, so module names don't collide. It reuses the existing fixtures (`render_fixture`, `refusal_fixture`, `FakeProbeSource`, `make_plan`) and the 72b scripts (`/tmp/278ebc9e/b0audit/{witnesses,delta_probes}.sh`) as seeds. | Exact, but only over the corpus. It sees nothing outside it. Needed as the acceptance test, but not enough on its own. |
| (b) Plain "validate as base, then route" | Small | Idle parity is strong. **But it can't admit the third row:** base validation hard-codes the `EVIDENCE_*` literals and the idle source, so no non-idle row can ever pass it. It needs the refinement in (d). |
| (c) One PR per surface | About 3 more gate cycles | Smaller diffs, but it doesn't touch the defect class: each surface can still re-read the kind. Only useful for sequencing. Not recommended unless the harness shows failures concentrated in one surface. |
| **(d) Recommended: idle-default routing, same validation order, new branches unreachable in production** | Small to medium: a reshape of head, not a rewrite | Production behaviour is identical to base **for all inputs**, not just idle ones. A lens can check this by reading; (a) confirms it by execution. |

Rules for (d):
- **Rule 1 (one total routing function per surface).** It wraps everything in `try/except Exception → None`. It reads only data the base already read at that site, with the base's parser. Cleanup takes its kind from the C5 receipt object `_evidence_cleanup_error` already parsed, with no wrapper read. The idle-only sites in `evidence_night` take the kind once, from where base already validates it (`candidate_state` and `sealed_state`), and pass it on. No disk reads in `notice_subject`, `render_notice`, `clone_census` or `notice_unused`.
- **Rule 2 (base kinds go down base code).** Define `BASE_KINDS = frozenset({idle, calibration})`. If the routing result is `None` or in `BASE_KINDS`, run the base path with base constants in base order. A calibration or stripped wrapper at an idle-only site therefore gets base code and the base text.
- **Rule 3 (new behaviour only for other kinds).** Only a kind outside `BASE_KINDS` reaches either:
  - the same validation sequence, driven by that row's fields; or
  - a typed "no approved handler" refusal.

  The production table contains nothing outside `BASE_KINDS`, so every new refusal text is unreachable in production. A kind declared in the wrapper only picks which validation runs. Acceptance still comes from that row's own digest, source and registration checks. The fallback is the status quo. So no second kind authority is created.
- **Rule 4 (type-check first).** Check the type of `state["kind"]` before any dictionary lookup, and keep the historical `Refused`.

**(e) Fallback:** at any site where driving the checks from the row would reorder them, add an explicit `elif kind not in BASE_KINDS:` branch and leave the idle lines untouched. The price is duplicated code in the new path, not idle risk.

## Q3. Plan for the next round

**Step 1: harness seat.** Astra high, since it already owns the witnesses. It writes tests only, and a different seat does the fix so the tests aren't fitted to it.

`WRITE_SCOPE: ["tests/parity/__init__.py", "tests/parity/b0_corpus.py", "tests/parity/b0_runner.py", "tests/test_b0_idle_parity.py"]`

What it builds:
- Base `2ea6a7ec` goes in a detached worktree under `/tmp/278ebc9e/b0par-base`. Both sides run the same harness code in separate subprocesses, with `PYTHONPATH` pointing at each checkout.

The corpus: every single-axis variation, plus all-pairs across axes, with a fixed seed.
- **Plan:**
  - validity: valid, missing, non-UTF-8, BOM, UTF-16, `[]`, missing keys
  - kind field: `[]`, `{}`, `1`, `null`, unknown, calibration
  - identity: `plan_id` mismatch
- **Wrapper `chain.zsh`:**
  - content: intact idle, calibration, declaration stripped, duplicated declaration, `CALIBRATION_LEDGER` added, unknown kind, quoted kind, `EVIDENCE_*` literal removed or changed
  - file state: missing, directory, symlink
  - encoding: non-UTF-8, BOM, UTF-16
- **Sidecars:** the digest sidecar matching, mismatched, missing, or with a wrong name token; the chain-source sidecar the same.
- **Chain source in the clone:** intact, modified, moved or deleted, non-UTF-8. Clone dirty, or at the wrong head.
- **Manifest:** intact, missing, altered.
- **`night/receipt.json`:** absent, UTF-8, BOM, UTF-16, invalid schema, `plan_id` mismatch, C5 FAIL, and C5 PASS with kind idle, calibration, missing or unknown. `chain.started` present or absent.
- **`evidence_outcome.json`:** absent, valid, invalid, non-UTF-8.
- **`prepare.json`:** partial steps, missing digests.

Entry points:
- evidence_night: `prepare` (fake builder and run), `candidate_state`, `sealed_state` (published and unpublished), `sealed_candidate`, `notice_subject`, `render_notice`, `notice_unused`, `clone_census(argv_only)`, `candidate_payload_kind`
- `gen_evidence_night --render-only`
- the gate's C5/C3 checks
- installer render, receipt validation, uninstall, veto and verify
- run_night: `_probe_worker` dispatch, `_artifact_list`, `_evidence_cleanup_error` and courier cleanup
- `zero_capture_facts`

What it records:
- return value
- exception class and message
- stdout and stderr
- the file tree afterwards (path, sha256, mode)
- external calls: subprocess argv, fake launchctl, and the number of `write_refusal` calls

Only the temporary root path is normalised; no text is normalised.

**Oracles:**
- **O1:** for every case, head's record equals base's record.
- **O2:** the set of refusal texts seen on head is a subset of those seen on base.
- **O3:** base against base gives an empty diff (catches nondeterminism).

**Seat acceptance.** The harness must go **red on `bee658c5`** and reproduce:
- F1: the BOM and UTF-16 cases
- F2: all five cases
- F3: both cases

It must be green for base against base, and finish in 10 minutes or less.

**Step 2: fix seat.** Sol 6.0 xhigh. It starts from `bee658c5` and reshapes to (d) Rules 1–4. `WRITE_SCOPE` is brief 10's list. The parity files are read-only. The seat may use (e) at any site where driving the checks from the row would reorder them. It must return `NEEDS_RULING` rather than change a base text.

**Gate** (all required; one lens):
- **G1:** the harness passes O1, O2 and O3, with an empty diff.
- **G2:** fuzz each routing function alone on at least 10,000 random byte strings and mutated wrappers: it never raises.
- **G3:** a grep-able shape check. Every new `Refused(` / `ValueError(` / `refusal_code` in `git diff 2ea6a7ec` sits inside a `kind not in BASE_KINDS` guard. `_custody_row` is either deleted or reads only the C5 receipt the caller already parsed.
- **G4:** the third-row test routes or refuses typed; unknown kinds are still refused.
- **G5:** the goldens and `test_refusal_parity` are green, with their expected bytes unchanged.
- **G6:** V1 is green apart from the 4 failures in 72b's R1 note, which the lead must confirm also fail at base (`2ea6a7ec`) in the same environment.
- **G7:** mutation. Hard-coding idle back at one site kills a third-row test. Moving one new check ahead of `checkout_ok` kills the harness (O1).

**Lens:** Opus contract lens checks Rules 1–4 and G3 by reading. It doesn't need to hunt for witnesses; the harness does that.

**Stop rule:** if G1 is still red after one fix round, split per (c), but only along the surfaces the harness names.

Nothing was written outside `/tmp/278ebc9e/b0esc-opus/`, which holds only the scratch files from the receipt probe.
