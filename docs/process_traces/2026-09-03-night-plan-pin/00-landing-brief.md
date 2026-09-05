WRITE_SCOPE: ["joulewise/night_gate.py","scripts/run_night.py","scripts/install_night_agent.sh","configs/launchd/**","tests/test_run_night.py","tests/test_night_gate.py","tests/test_install_night_agent.py","docs/process_traces/2026-09-03-night-plan-pin/**"]
ORIGIN: claude-fable-5 magistrate via Claude Code Sol bridge | BRIDGE_ORIGIN: claude | BRIDGE_HOPS_REMAINING: 0 | GENRE: implementation | EFFORT: xhigh
BASE_HEAD: 2f59e791b166c6ec9f99cebdca315a8871678b2f
BASELINE_MANIFEST: .codex-bridge/baselines/planpin-20260903-sol-impl-01.json
BASELINE_DIGEST: sha256:35eaee3dc828a6416d7adac97f6650f36cb5f4f38cb08ac747ba1f0d29015f2d
EARLY_RETURN: NEEDS_SCOPE, NEEDS_RULING

# LAND: the night plan pins the MEASUREMENT checkout, not the dev tree (audit F1 / F9 / B7)

Linked worktree `/Users/edr/code/JouleWise-wt-planpin`, branch
`feat/2026-09-03-night-plan-pin` @ 2f59e791 (= origin/main). You cannot
`git commit` (linked-worktree index is unwritable in your sandbox); the
magistrate commits. Never run `python -m unittest discover`; run named modules
only. `TMPDIR` is preset under the scratchpad. Do NOT touch
`~/Library/LaunchAgents`, `~/night-custody` (read-only reference only), or any
file outside WRITE_SCOPE — if you need one, finish the authorized work and
return `NEEDS_SCOPE` naming the path. Bridge depth is one hop: never call
Claude by MCP, `claude -p`, or any launcher. Never start any `[QUIET-MAC]`
measurement.

## Forcing problem (read these sites first)

- `joulewise/night_gate.py:20` `PLAN_SCHEMA = "joulewise.night_plan.v1"`;
  `:104-115` `_PLAN_KEYS` (exact key set); `NightPlan.from_mapping`
  `:181-250` (`repo_head` at `:220-225`); the R-6 stale checks `:571-609`
  (age `:593-598`, `checkout_head != plan.repo_head` → `night_plan_stale`
  `:599-609`); the C5 row `:576-583`.
- `scripts/run_night.py:22-25` `REPO_ROOT = parents[1]` of the driver = the
  checkout the LaunchAgent runs the driver from (the plist renders
  `@@REPO@@/scripts/run_night.py` with `WorkingDirectory @@REPO@@`,
  `configs/launchd/com.joulewise.night.plist.template`); `make_probes()`
  `:267-282` — `checkout_head()` = `git -C REPO_ROOT rev-parse HEAD`, i.e.
  the DEV tree; `_malformed_plan_fallback`-style constructor at `:865-885`
  builds a `NightPlan(repo_head="0"*40, ...)`.
- `scripts/install_night_agent.sh:39-45`: `plan_head` = plan `repo_head`;
  `actual_head` = `git -C "$repo" rev-parse HEAD` (`$repo` = the script's
  parent = the dev tree); mismatch → exit 3 — on BOTH install and
  `--uninstall`.
- Tests today: `tests/test_night_gate.py:63-116` (FakeProbeSource with
  `checkout_head`), `:127,:148` (plan fixture), `:281` (malformed matrix),
  `:405-410` (`test_wrong_checkout_head_is_stale_...`), `:779-794` (the
  refusal-code → test-name registry: keep it exact); `tests/test_run_night.py:87,
  :206, :1097` (a real-checkout plan uses `git rev-parse HEAD`).
  `tests/test_install_night_agent.py` does not exist yet — you create it.

What broke: the plan pins `repo_head` = HEAD of the DEV checkout
(`/Users/edr/code/JouleWise`) and the gate compares against that same dev
HEAD. The magistrate's ordinary daytime work (pulls, merges — 115 commits in
17 h on 09-02) moves it, so an armed night is invalidated by ordinary work.
It happened on 2026-09-02 (`docs/process/NIGHT_HANDBACK.md:19-23,63-67`:
the night had to be RE-ARMED and re-pinned). Meanwhile the chain that
actually measures runs from the MEASUREMENT checkout of record,
`/Users/edr/JouleWise-measurement-20260813` (D-171 item 5,
`docs/decision_log.md:10616-10617`: "Measurement checkout of record =
`/Users/edr/JouleWise-measurement-20260813`; the magistrate fast-forwards it
and relocks its venv (no sudo)."), which only moves when the magistrate
deliberately fast-forwards it before an arm. Right now: dev HEAD 5e31288e,
measurement HEAD eeb4e133, the armed `rehearsal-20260903` plan pins
33290b8b — stale AGAIN under the current rule.

Fresh Fable audit (read-only; file lives in worktree
`/Users/edr/code/JouleWise-wt-decode-id/docs/process_traces/2026-09-02-fresh-fable-audit/01-audit-night-loop.md`,
read-only for you) §6 item 1 (`:256-261`, verbatim):

> 1. **Pin the plan to the measurement checkout, not the dev tree.** Add
>    `measurement_head` (HEAD of `/Users/edr/JouleWise-measurement-20260813`)
>    and make R-6's stale check compare that; keep `repo_head` only for the
>    installer/uninstaller, or drop the uninstall HEAD check. This is the one
>    change that turns tonight from a finding into a pass and removes B7/F9.
>    (Reinterprets R-6 → cold gate; small code.)

Findings F1 (`:221`), F9 (`:229` — "Uninstall requires HEAD == armed commit;
after a day of merges the uninstall itself fails and the dead-man fires
forever"), B7 (`:246` — "a real night needs either a frozen main from arm to
fire or a plan that pins the measurement checkout").

## Controlling rulings — quote every clause you reinterpret VERBATIM in the report

`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
R-6 (`:113-123`), the sentence being reinterpreted (`:117-118`, verbatim):

> A plan older than 36 h or whose `repo_head` is not
> the checkout's HEAD refuses with `night_plan_stale`.

R-7 (`:125-135`), the clause that names the dev tree HEAD as what R-6 binds
(`:129-132`, verbatim):

> from a fresh shallow clone under the custody root, never by checking
> out a branch in the development tree (that would move the HEAD R-6 binds
> to).

R-3 (`:72-80`, census first — unchanged by this landing; your change must not
reorder the gate: the R-6 window guard still precedes every command/filesystem
probe, and the census still follows the stale checks, exactly as `:571-621`
today). R-9 (`:159-169`, the arm protocol: the magistrate writes
`night_plan.json` — the plan author is the magistrate, by hand). Also D-127,
D-161 (operator-only adversary: refusals are for physics/evidence/
pre-registration integrity, never operator-conduct guards), D-169, D-171 in
`docs/decision_log.md` (index rows near `:217`; D-171 body `:10586-10640`).

This landing REINTERPRETS R-6 ("the checkout" = the measurement checkout of
record, not the driver's own tree) and goes to a cold gate before merge.
Implement cleanly; the report carries the design choice and its alternatives.

## Design — magistrate's lean, with explicit licence to disagree in the report

1. Schema: bump to `joulewise.night_plan.v2`, exact key set = v1 keys +
   `measurement_root` (absolute path, non-empty string; the plan is the ONE
   home for which checkout is pinned — never hard-code the path in code) +
   `measurement_head` (40 lowercase hex, same `_HEAD_RE`). A plan carrying
   schema `v1`, or missing/extra keys, refuses `night_plan_malformed` with a
   detail that says v1 is retired and the plan must be re-authored under v2
   (no dual-schema acceptance; fail-closed for evidence under D-161 is the
   ruled shape). Alternative you must weigh in the report: optional field
   under v1 with a strict rule (present ⇒ compared; absent ⇒ ?). State why
   you chose what you chose. Compatibility story for the two existing
   custody roots (`/Users/edr/night-custody/rehearsal-20260902` — a
   completed historical night whose plan the gate never re-reads;
   `rehearsal-20260903` — the ARMED plan, v1, pinning 33290b8b): say
   explicitly in the report that the armed 20260903 plan must be
   re-authored under v2 by the magistrate before its fire hour, and that
   merging this landing without re-authoring turns tonight's
   `night_plan_stale` refusal into `night_plan_malformed` (both fail closed;
   neither measures). Do NOT touch the custody roots.
2. Gate: the R-6 stale check compares `measurement_head` against a NEW probe
   `measurement_head(root: str) -> str` (= `git -C <measurement_root>
   rev-parse HEAD`, production wiring in `make_probes()`), with the plan's
   `measurement_root` as the argument. Probe failure (not a git repo, path
   missing) goes through the existing `_probe_refusal` path. Keep the dev
   tree `checkout_head` probe and RECORD it in the C5 measured row as
   informational (`driver_checkout_head` alongside `plan_repo_head`) — it
   never refuses. If you believe it should be dropped instead, say so and
   why, but land the lean.
3. `repo_head` stays a required v2 field (provenance: the dev commit whose
   driver authored the plan), validated for format only at the gate.
4. Installer `scripts/install_night_agent.sh`: on INSTALL check BOTH pins —
   `repo_head` == dev HEAD (arm-time consistency, harmless, cheap) AND
   `measurement_head` == HEAD of `measurement_root` (the pin that matters);
   mismatch → exit 3 with a message naming WHICH pin. On `--uninstall`
   check NEITHER pin — an uninstall must never be refused on a pin (F9: the
   dead-man fires forever otherwise). The plist template needs no change
   unless you find one is forced; say if so.
5. `scripts/run_night.py`: every `NightPlan(...)` constructor site and any
   place that reads `repo_head` gets the new fields; the fallback plan
   builder uses `"0"*40` and an empty/placeholder root consistently with
   its current style.
6. NO new refusal codes. `night_plan_stale` and `night_plan_malformed` carry
   the new details; keep the code registries (`night_gate.py:55-100`,
   `tests/test_night_gate.py:779-794`) exact.
7. Docs OUTSIDE your scope mention `repo_head` (`docs/process/NIGHT_HANDBACK.md:21,63,67`,
   the R-6 text itself): do NOT edit them; list every such site in the
   report under "Magistrate follow-ups" so the magistrate updates them.

## Tests (defect-shaped; each row below is one assertion that FAILS under its counterfactual)

- stale check keys on `measurement_head`: fake probe returns a different
  measurement head → `night_plan_stale`, detail names `measurement_head`.
- dev-tree HEAD movement no longer refuses: `checkout_head` probe returns
  something ≠ `repo_head` while `measurement_head` matches → gate proceeds
  past the R-6 checks (assert the census probe was invoked / the receipt is
  not `night_plan_stale`) and the C5 row records the driver head.
- a moved measurement checkout still refuses: real scratch git repo (init,
  commit, record HEAD, then commit again) → `night_plan_stale`.
- v1 plan / plan missing `measurement_head` / missing `measurement_root` /
  relative root / bad hex → `night_plan_malformed` with the retirement
  detail (extend the `:281` malformed matrix).
- installer (`tests/test_install_night_agent.py`, NEW, stdlib only, run the
  script via `subprocess` with `--render-only <dir>` and `--launchctl-bin`
  pointed at a scratch stub so nothing touches launchd; put a stub `claude`
  executable on PATH for the install path): install with both pins matching
  → renders the plist; install with `measurement_head` mismatched → exit 3
  and the message names `measurement_head`; install with `repo_head`
  mismatched → exit 3 naming `repo_head`; `--uninstall` with BOTH pins
  mismatched → proceeds (exit 0 with the stub launchctl). If the uninstall
  path cannot be exercised without `~/Library/LaunchAgents`, return
  NEEDS_RULING with the two options rather than touching it.
- `tests/test_run_night.py:1097`-style real-checkout test: point
  `measurement_root` at a scratch repo you init under TMPDIR.
- Mutation probe (paste the tail): revert the gate comparison to
  `checkout_head != plan.repo_head` in a scratch copy or via a one-line
  temporary edit, run `tests.test_night_gate`, show the named test FAILS,
  then restore. Same for the installer's uninstall skip (re-add the check
  → the uninstall test fails).

## Verify and report (verbatim tails)

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent`
  (baseline before your edits: `Ran 96 tests ... OK` for the first two).
- `zsh -n scripts/install_night_agent.sh`
- `git -C /Users/edr/JouleWise-measurement-20260813 rev-parse HEAD` (read
  only; paste — it is the value a real v2 plan would carry).
- `git status --porcelain` — only WRITE_SCOPE files dirty.

Write `docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md`
BEFORE ending your turn: executed evidence (command + verbatim tail for each
item above, including the mutation probes), the design choice and every
alternative weighed (schema bump vs optional field; keep vs drop the
install-time `repo_head` check; record vs drop the dev-head probe), every
clause of the ruling text you reinterpret quoted verbatim with `file:line`,
the compatibility story for both custody roots, "Magistrate follow-ups"
(out-of-scope doc sites), and a `## Clause map` section (contract
`docs/contracts/bridge_protocol.md` §1 "Clause map"): one row per
proposition — production site `file:line`, biting assertion (test method
`file:line`), counterfactual (the one-site edit that assertion fails on) —
at least these rows: (a) stale compares `measurement_head`; (b) dev HEAD
movement does not refuse; (c) moved measurement checkout refuses
`night_plan_stale`; (d) v1 / missing-field plan refuses `night_plan_malformed`;
(e) schema literal `joulewise.night_plan.v2`; (f) install refuses on
`measurement_head` mismatch; (g) install refuses on `repo_head` mismatch;
(h) uninstall ignores both pins; (i) gate order unchanged (window guard →
stale checks → census). Rows you cannot pin say `NOT PINNED: <reason>`.

FINAL message = `claude-codex-report/v1` envelope (implementation). The JSON
header MUST be under 8192 bytes: `verdict` = `{counts, findings}` only; all
evidence lives in the report file and the markdown body. Include a
`verification` entry per command, `flags` for any NEEDS_RULING/NEEDS_SCOPE
(verbatim, with question / options / recommendation / blocked work), a
5-line summary, files changed, and the test tails. Do not end your turn
before the report file exists.
