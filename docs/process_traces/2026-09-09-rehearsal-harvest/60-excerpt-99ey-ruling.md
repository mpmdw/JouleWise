# Cold-gate ruling — D-176 second gate (integrated head 4d72e524)

**Contamination disclosure:** the harness injected the global `~/.claude/CLAUDE.md` and the project memory index (`MEMORY.md` one-liners) into my system prompt before I read anything; I did not open any memory file, RUN_STATE.md, or the checkout's CLAUDE.md/AGENTS.md, and I did not act on the injected text. Read: packet (sha256 verified eea056b2…), exhibits A–D, and the named code at HEAD 4d72e524. Executed at the bench (this checkout, `.venv` python): census resolver with the real inventory; clone inspection. Everything else marked NOT EXECUTED.

## Executed evidence

- `production_custody_roots(home, _production_inventory())` resolves 9 roots, none with `resolution_error`. `_contains(<running checkout>, repo_runs)` → **True**. Finding 1 confirmed: every T0_REHEARSAL whose plan `measurement_root` is the checkout the consumer runs from refuses at `arm_readiness.py:9883` / `night_gate.py:874`.
- Inventory entries carry only `measurement_root`; all four `custody_root`/`ledger_path` are `null` (`configs/production_custody_inventory.json`).
- Packet claim "the v5 clone path does not yet exist" is **false on this machine**: `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a` exists at HEAD `1c83f2af`; `JouleWise-measurement-20260818` at `94dc3b34`. Neither has `configs/production_custody_inventory.json` at its HEAD, so `_production_inventory` (`arm_readiness.py:250–261`, `git show HEAD:` at `:4683`) refuses "production-root census incomplete" for any rehearsal launched from them today.

## Q1 — census semantics for the running deployment

**Q1.1 Candidate (c) is adopted; (a) and (b) are rejected.** What a rehearsal actually writes is `<custody_root>` (already fenced SIBLING_CHILD), `<measurement_root>/runs` (the ledger/runs home is the clone's own `runs/`, by the `repo_runs` derivation at `arm_readiness.py:243`), and nothing else the census names. So "a rehearsal never writes into a retained production runs root" is exactly "the rehearsal's `measurement_root` is not a retained production clone."
- (a) exempts the running deployment's own inventory entry: a rehearsal launched from `/Users/edr/code/JouleWise` would pass and write `runs/` into the canonical checkout. Fails the failure-mode test.
- (b) drops `measurement_root` from DISJOINT: same failure, from any production clone. Fails.
- (c) keeps DISJOINT of `measurement_root` against every inventory entry and adds a self-identity refusal. Passes: a retained clone can never host a rehearsal, and the only remaining hole is an un-inventoried production clone, which is inventory maintenance in every candidate.

**Q1.2 Installed rule (seat 4 or a bounded seat-2 follow-up), applied identically at `night_gate._pack_rehearsal_roots` and `arm_readiness._authenticate_go_purpose`:**
1. `self = Path(arm_readiness.__file__).resolve().parents[1]`; plan `measurement_root` resolved strict must **equal** `self`, else refuse `launch_go_receipt_invalid` detail `measurement_root: not the running checkout`. This binds executing bytes to the plan and makes `repo_runs` the rehearsal's own root by construction.
2. `repo_runs` is skipped for the `measurement_root` field only; it stays DISJOINT for `custody_root` and every ARM-context root.
3. `self` must not equal, contain, or be contained by any `deployment_measurement_root:*` entry; refuse `rehearsal_roots_not_disjoint: measurement_root`. This is the "running checkout is inventoried" refusal the packet asked for.
4. Regression: a test with the **real** resolver and real inventory, `measurement_root = <checkout>`, must pass the census; `tests/test_arm_readiness.py:2321`'s synthetic-home relocation is why the collision was missed and is not sufficient alone.

**Q1.3 By-construction property, additional.** The rehearsal clone's basename must start with a reviewed literal `JouleWise-rehearsal-` (constant next to `PRODUCTION_CUSTODY_ROOTS`). A clone named `JouleWise-measurement-*` is then refused even if the inventory is stale. This is the only clause that survives inventory neglect.

**Q1.4 Nits folded in:** `arm_readiness.py:9849` must import `t0_rehearsal.REHEARSAL_WINDOW_PREFIX` (exhibit A-5); gate and consumer must agree that a missing `pack_root` is `launch_go_receipt_missing` (A-6). Both fail closed today, so they are pre-night should-fixes, not blockers.

## Q2 — fitness for the first pack-bound night

**Q2.1 MUST close before the night:** Q1.2–Q1.3 with regression; seat 4 (rehearsal purpose + G7), because the ARM receipt is single-use at O_EXCL, so a rehearsal run without seat 4 cannot later discharge G7 and forces a second rehearsal; A-5 prefix unification. **Observational residue / bookkeeping:** A-2 clause-map cells, A-3 stale pins, A-4 "no commit" sentence (must precede calling the head final, not the night); A-6. **The four stubbed seams** (real ARM mint, real `_verify_arm_receipt` keyword contract, real T-0 authoring, Popen/execve) cannot be closed on the bench; the rehearsal night is their closure. **Ed-owned privileged-anchor control: NOT EXECUTED**; I could not locate what it gates at this checkout, so I do not rule it off the path.

**Q2.2 HEAD-pin is sound, and the packet's "must itself be an inventory entry" is withdrawn.** Under Q1 the rehearsal clone must **not** be inventoried. The pin only requires the inventory bytes to be committed at the clone's own HEAD. Exact ARM-time check the clone must satisfy: `git -C <measurement_root> rev-parse HEAD == plan.measurement_head` (already enforced, `night_gate.py:979–1003`), and `git show HEAD:configs/production_custody_inventory.json == working-file bytes` (already enforced, `arm_readiness.py:258–260`). Re-cutting the clone at a reviewed head H is sound iff H contains the inventory and the plan pins H. Today no existing clone satisfies this; the rehearsal clone must be cut after Q1 lands.

**Q2.3 Minimal live rehearsal:** one rehearsal-class pack night on a fresh `JouleWise-rehearsal-<date>-<sha>` clone at the reviewed head (Q1 + seat 4), not inventoried; prefixed window id; `custody_root = ~/night-custody/<window_id>`; real T-0 author, real `generate_arm_receipt`, real `_verify_arm_receipt`, real GO, real Popen with `stdin=DEVNULL` into the eight-flag launcher; consumer writes `launch_consumption.v3`; `verify_consumed_launch` live replay; then present the rehearsal GO to a production-plan launcher and record the class refusal as the **first** refusal (G7). A narrower in-process shape is rejected: it re-asserts the process boundary instead of executing it.

**Verdict: UPHELD WITH AMENDMENTS — head may land; no pack-bound night until Q1.2–Q1.3, seat 4, and a fresh un-inventoried rehearsal clone at a head carrying the inventory exist.**
