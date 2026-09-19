# Cold-gate packet — GENERATOR-HEAD-FILE-BYTE-PIN-01 (kernel 244): may the live campaign generators stop byte-pinning the committed ledger head file? (rule 11: dropping a mechanism from what an armed pack asserts about calibration authority; changes an emitted manifest field)

Assembled 2026-09-19 ≈09:25 PDT by the resident magistrate (activation d0b83820). Mechanically assembled: every exhibit is a verbatim `git show`/`sed`/`grep`/`cat` extract of main `2f79e633`, of the repair branch `fix/2026-09-19-head-pin-test-drift`, or of records on the activation's bookkeeping branch. The magistrate's own view is confined to the option lists.

## What was found

The committed ledger head pin `configs/calibration/calibration_ledger_head.json` (D-109 R1.4's anti-rollback anchor) advances after every measurement night by the documented desk step (Exhibit B: runbook §3 item 4; append contract "advance-head-pin"). It advanced 76 → 126 → 176 on 2026-09-19. Twelve campaign generators reference the file and five byte-pin it (`LEDGER_HEAD_FILE_SHA256 = 6bbe2625…`, Exhibit A); the three LIVE v5 generators and the historical successor-generation paths refuse regeneration with `pinned input drifted` / `external input drift` once the bytes move. Consequence in the full suite (Exhibit D): ten test modules, about two dozen tests, fail after the first pin advance, and will fail again after every future advance. The acceptance binding already exists as a separate constant (`LEDGER_HEAD_SHA256` = the r6 acceptance's `ledger_cutoff` digest `08456d50…`, Exhibit A lines 214–216 / Exhibit C, Opus Q2); the emitted `issued_ledger_head.file_sha256` has no consumer in the repository (Exhibit C, Opus Q2, grep evidence). The pack passes `--head-pin <repo path>` at RUN time, so pack behaviour never depended on generation-time head bytes (Exhibit C).

The consult split (Exhibit C): Astra kept the byte pin and fixtured the tests (the generator tested as a function of its declared inputs; drift refusal stays in production); Opus called the byte pin a category error (a frozen byte pin on a file the contract licenses to advance nightly) and proposed B1: drop `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)` from the drift tuple, assert the semantic relation instead (`pin.sequence >= cutoff.sequence`, schemas equal, refuse `ledger head pin behind the acceptance cutoff`), drop `file_sha256` from `issued_ledger_head`, keep `head_sha256 = LEDGER_HEAD_SHA256` asserted equal to `cutoff["head_digest"]`. The lead adopted Astra's fixture for the repair PR and registered B1 for this gate (07a). The repair's round 1 fixtured two modules (Exhibit E); five more modules need the same fixture (Exhibit D), and the historical v2 → v3 successor-generation paths are among them.

## Q1 — the byte pin (rule one option or write a better one)

- (a) ADOPT B1 for the three live v5 generators exactly as Exhibit C (Opus Q3 B1) specifies; historical (frozen) generators keep their byte pin and echo mode; tests for frozen successor paths keep the fixture.
- (b) ADOPT B1 for every generator that declares `LEDGER_HEAD_FILE_SHA256`, live and historical alike, since the historical successor-generation tests (`test_d117_v3_family`, `…qwen25_*_plan`) also regenerate; state what "frozen" then means for a historical generator's committed pack bytes (the packs themselves are untouched; only the generator's drift set changes) and whether their committed `plan_tree.json` / pack custody is affected.
- (c) KEEP the byte pin everywhere; the test fixture (Exhibit E) is the permanent answer; every future generation re-pins the constant (one reviewed line per live generator per night).
- (d) Other, with the same burden: the ruled option must (i) keep D-109 anti-rollback (a pin rolled back below the cutoff refuses), (ii) keep drift refusal for the other four pinned inputs, (iii) keep frozen packs byte-identical and their custody receipts valid, (iv) have no false failure on the next pin advance.

Deliver: the ruled option; the exact code shape (the drift-tuple change, the semantic check text and its message, the manifest field change) for a seat to implement; and whether removing `issued_ledger_head.file_sha256` is a schema change that needs its own consumer sweep (name the consumers if any).

## Q2 — authority and sequencing

Is the ruled option a contract amendment (which text?) or a code change conforming to the contract as written (Exhibit B)? Must it land BEFORE or AFTER the test-only repair PR #361 (which cures CI without touching production)? If after, does the fixture in Exhibit E become dead weight to be removed in the same lane, or does it stay as the proof that generators are functions of their declared inputs?

## Q3 — what the test suite must prove afterwards

Under the ruled option, name the regressions (defect-shaped, one line each) that must exist: pin advanced past cutoff → generate succeeds byte-identically; pin rolled back below cutoff → refuses with the new message; pin schema altered → refuses; another pinned input drifted → still `pinned input drifted`; preserve/echo mode unchanged. State which existing tests become obsolete.

## Constraints on the judge

Read-only. NOTHING IS ARMED on this machine. Wall budget 15 minutes, hard. Probes allowed: `git show 2f79e633:<path>`, `rg`/`grep`, `sed -n`, and Python snippets under `/tmp`; at most one run of a single test module (`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_campaign_generator_core`, ≈ 3 s, read-only in the clean worktree `/Users/edr/code/JouleWise-wt-refc-d0b83820` at the repair branch's round-1 head). No `sudo`, no `powermetrics`. Never touch `/Users/edr/code/JouleWise` (canonical root), any `/Users/edr/JouleWise-measurement-*` directory, `/Users/edr/night-custody`, or `~/Library/LaunchAgents`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
fdf62af2c4c9af36aef3fae75bcf667b917baf9786e15e012feb4b4c34f978af  exhibit-A-live-generator-drift-set.md
6d731b57526e483f53adc02bc99788d72253aaccbb98d0b96a919a775e05910e  exhibit-B-contract-text.md
5c0adce4d750a0a05fcde08067306e42596b85c02057e22bb70b6dda77a28d8d  exhibit-C-consult-07-refuter-07-adjudication-07a.md
e5d01719c02cb6d55e05dfc03c9a5e45518647b51b51c926d69750692cc1e028  exhibit-D-full-suite-evidence.md
b242186f723e6cdb1ebd003c03a852e89d23a8404a1009366420edc0ddb119de  exhibit-E-round-1-fixture.md
```
