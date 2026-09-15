# 12 — Opus 5 pairing refuter on cold-gate ruling 10 (packet 65; contract lens; worktree 63ed10b1; delivered 2026-09-14 ~17:31 PDT)

Verbatim final report.

---

# Opus 5 pairing refuter — cold-gate packet 65 (contract lens), worktree `JouleWise-wt-coldgate-census` @ 63ed10b1

Charter digest: expected `099de884…c95d81` (convening prompt) = observed `shasum -a 256 docs/process/coldgate_charter.md` → match. All five exhibit digests re-hashed = manifest. Proceeding on the merits.

## Q1 — pack root: **AFFIRM (a), AMEND conditions 2 and 5**

Every factual claim in ruling §3 verified independently:

| Ruling claim | Verified |
|---|---|
| successor resolved through registry `successor_pack_ids`; unlisted name refuses `readiness_row_registry_mismatch` | `joulewise/arm_readiness.py:4436-4472` (raise at `:4468-4471`). The shape-only fallback at `:4476+` is unreachable here: registry `schema_version` is `joulewise.arm_readiness_row_registry.v2` = `R1_ROW_REGISTRY_SCHEMA` (`:49`), so the R1 branch always fires. |
| registry working bytes must equal HEAD blob → patch must be committed | `:4520-4535` (`_registry_reference`, `committed_raw != raw` → refuse) |
| `reviewed_main` requires HEAD == `refs/heads/main` == `refs/remotes/origin/main`, clean incl. untracked | `:5542-5570`; enforced pre-loop at `arm_readiness_evidence_t0.py:2266-2271` |
| live roster = three `_v5` Qwen3 packs | `configs/arm_readiness/d117_row_registry_v2.json:532-536` (exact lines) |
| `d117_floor_qwen25_1p5b_v3` fullmatches ALPHA | `arm_readiness.py:420-424` — `d117_floor_qwen25_1p5b_v(?:[2-9]|…)` |
| census argv are module constants no registry field touches | `arm_readiness_evidence_t0.py:57-58` |
| `freeze` absent from the T-0 author | `grep -c freeze` → 0 |
| `.venv/` gitignored | `.gitignore:6` |
| hygiene NIT: two `_v5` dirs exist, holding only `generate_configs.py`; contrast `_v5` absent | `ls configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5` |

**"Bench decision, not a contract change" is defensible.** Nothing in (a) is claim-bearing or irreversible, and I found a mitigation the ruling did not record, which strengthens it: the desk receipts bind the *patched* HEAD commit and the patched registry sha256 (`:2361`, `_discover_evidence(..., head_commit=head, pack_sha256=pack_sha)` at `:2377-2384`), and the registry reference records `sha256` of the patched bytes (`arm_readiness.py:4533`). Any later consumer binding against real main mismatches on both — the artefacts are self-detecting, not silently promotable. Outputs land only under `custody/<pack_id>/` (`:2367-2371`, `include_pack=False` at `:2384`); the tool writes nothing into the pack directory or the repo. D-161's operative test (MISTAKE vs DELIBERATE, exhibit E) is applied correctly: the residual is an operator-mistake class, and conditions are the right instrument.

**AMEND 2 — the origin is not read-only.** Exhibit A §A1 clones from `/Users/edr/code/JouleWise`, a writable non-bare repo; condition 2's phrase "the read-only origin it was cloned from" is factually wrong and `reviewed_main` *requires* `refs/remotes/origin/main` to survive, so the remote cannot simply be removed. Replacement: *"Never pushed. Immediately after cloning, run `git remote set-url --push origin no-push-desk-proof` in the clone and record its `git remote -v` output in the desk-proof record; the fetch URL and `refs/remotes/origin/main` stay intact because `reviewed_main` reads that ref (`arm_readiness.py:5546-5549`). No `generate_arm_readiness.py arm` is ever run from it."*

**AMEND 5 — name the check, not the intent.** Replacement: *"After harvest the clone is retired by Ed's hands, and the magistrate records that `ls -d /Users/edr/JouleWise-*` no longer lists it."*

Conditions 1, 3, 4 are sufficient as written for the named mistake class.

## Q2 — acceptance: **AFFIRM the (ii) rejection and the authority; AMEND the replacement text (false-pass hole)**

Verified. On any refusal the CLI emits exactly `status`/`kind`/`reason_codes`/`detail` (`scripts/author_arm_evidence_t0.py:63-82`) and writes nothing; the census detail is `f"fresh {label} census found a forbidden process"` (`arm_readiness_evidence_t0.py:1316-1318`) through `_underivable` (`:356-361`) — no argv, no stdout, no exit code. Sources/receipts are assembled only after the full loop (`:2316-2325` raises on the first failing row; staging at `:2367`; publish at `:2386-2401`). Row order `:103-117`, census 10th. **(ii) is correctly REJECTED.**

Equal-force of a standalone run: `_execute_probe` (`:431-476`) uses `Popen` with no shell, `env` = `{LANG:C, LC_ALL:C, PATH:/usr/bin:/bin:/usr/sbin:/sbin}`, `cwd` = repository, `start_new_session=True`. `argv[0]` is absolute, so PATH is inert; `cwd` is inert for pgrep; the patterns contain no locale-sensitive classes, so `LANG` is inert *for these bytes*. Equal force holds **for the argv actually executed**. The authority question is also answered correctly: exhibit B's `authority` note is "rule change needs a ruling", charter §3 trigger 4 makes a proposed rule cold-gate business, and charter §9's bar is on converting a *verdict* into its opposite — ruling 10's pattern cure is untouched.

**But the replacement text has a false-pass hole the ruling did not consider: there is no positive control.** The bar is "prints nothing and exits 1". A mis-typed or mis-pasted pattern that is still a valid ERE (a dropped leading `/`, a dropped `firefox`, a smart-quote-mangled `( |$)`) matches nothing and yields exactly that signature. macOS pgrep returns 2 only on an *invalid* pattern; a valid-but-wrong pattern is indistinguishable from a true pass. The lane's whole subject is a regex's matching behaviour, so an untested regex closing it inverts the lane. Exact amendment — insert after the fourth probe, before "The lane closes when":

> Then two positive controls, whose purpose is to prove the typed pattern reached `pgrep` intact and that this regex shape does match a real always-present process: `LANG=C LC_ALL=C /usr/bin/pgrep -lf '/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox|Finder)( |$)'` MUST exit 0 and print the `Finder` line, and `LANG=C LC_ALL=C /usr/bin/pgrep -lf 'powermetrics|window-chain|run_campaign|tail -f|(^|/)watchdogd( |$)'` MUST exit 0 and print `/usr/libexec/watchdogd`. If either control prints nothing, the whole run is VOID and the lane stays open. Every command is run with the pattern in single quotes and with the `LANG=C LC_ALL=C` prefix, matching `_execute_probe`'s environment (`joulewise/arm_readiness_evidence_t0.py:431-441`). Before marking the lane closed the magistrate diffs the recorded command lines byte-for-byte against `git show <sha>:joulewise/arm_readiness_evidence_t0.py | sed -n '57,58p'`; a diff voids the run. Ed records the probes BEFORE reopening any browser to post them.

(The two controls are proposed, not executed: running them is itself the Q3 hazard below.) Each control differs from the ruled pattern by one alternative only, so a control that fires proves the anchor `/Contents/MacOS/`, the alternation, the `( |$)` tail, the `(^|/)` prefix and the shell quoting all survived — which is precisely what the tool's own constants would have guaranteed and hand-typing does not. With this amendment (iii) is a sound substitute; without it, (iii) is weaker than the text it replaces in the one dimension that matters.

## Q3 — timing: **REFUTE "the (iii) block cannot disturb the night"; AMEND the bench bar**

The second probe's argv is `/usr/bin/pgrep -lf codex|claude|t3` — a command line that **literally contains `codex`**. `pgrep` excludes only itself, not another concurrent `pgrep`. The night censuses `("/usr/bin/pgrep","-lf","codex|claude|t3")` (`joulewise/night_gate.py:42`, `agent_census` `:498-525`) at the gate (`:1033`), at `scripts/run_night.py:1426`, `:1202`, `:1809`, and **every 30 s while the chain runs** (`CENSUS_INTERVAL_S = 30`, `:62`, `:479-513`), aborting the chain on a hit (`_CODES["aborted_agent_present"]`, `:508`). The repo already treats this exact hazard as known: `scripts/gen_derivation_night.py:58-62` — *"censuses `pgrep -lf "codex|claude|t3"` every 30 s and aborts the night on any hit, so no literal this wrapper bakes into a command line may contain one of these substrings."* Ed's probe block bakes in all three. Per-invocation overlap odds are small (~10 ms against a 30 s tick), the cost is a scarce armed night, and `run_night.py:1202`/`:1809` add further sampling points outside the chain. Replacement for the ruling's third §5 bullet:

> The (iii) probe block is read-only but is NOT free while a night is armed: its second command's argv contains the literal `codex`, which the night's own agent census (`joulewise/night_gate.py:42`, sampled at `scripts/run_night.py:479` every 30 s and at `:1202`, `:1426`, `:1809`) matches like any other process, aborting the night. Ed runs it only OUTSIDE the plan span — before 02:20 PDT 2026-09-15 or after the dead-man at 07:00 PDT — never between. Given the 2026-09-13 refusal at t0 on Ed's own interactive session, after the night is over is the default; tonight is permitted only with the pre-02:20 fence stated in the email.

**Bench bar for (i) is incomplete.** A5's expected refusal is raised by `_capture` for `clock-reference` — row 1 (`:520-537`, `_RUNBOOK_ARTIFACT_REASON_CODES:179`) — so rows 2-15 never derive. `reviewed_main`, `resolve_frozen_plan` and `committed_pack_tree_sha256` ARE pre-loop (`:2266-2286`) and so are proven, which makes the ruling's added clean-tree check (1) redundant-but-harmless. **But the terminal-review trailers are checked by `_derive_terminal_review`, row 3, inside the loop (`:1257-1283`)** — A5 never reaches them. A4 (verbatim `--cleanup`, three trailers, `Pack-Sha256` membership) is the fiddliest step in the whole preparation and is first exercised in Ed's own session at `scripts/capture_t0_step.py:215-252`. Add to the bench bar:

> (4) The magistrate verifies the A4 trailers at the bench without sudo: `git show -s --format=%B HEAD` shows exactly one `JouleWise-Terminal-Review: PASS` and one `JouleWise-Terminal-Review-Tree-Oid:` equal to `git rev-parse HEAD^{tree}`, and `committed_pack_tree_sha256(pack)` appears among the `JouleWise-Terminal-Review-Pack-Sha256` trailers, which are unique 64-hex — the exact predicate of `arm_readiness_evidence_t0.py:1266-1283`. A5 does not reach this row. (5) The email states the sudoers prerequisite explicitly: `sudo -n /usr/sbin/systemsetup` and `sudo -n /usr/bin/powermetrics -i 200 -n 1` must already be passwordless (`scripts/capture_t0_step.py:482`, `arm_readiness_evidence_t0.py:1809-1812`, `scripts/quiet_mac_prep.sh:47-50`), plus ≥20 GiB free on both backup destinations (`:1916-1941`) — otherwise the run dies at step 2 or row 15 after Ed has spent the evening. (6) All bench preparation (A1 clone, venv, pip, A5) finishes and every agent session closes well before 02:20 PDT: the clone+`pip install` burst can carry the 1-minute load average past `LOAD_MAX = 2.0` (`joulewise/night_gate.py:57`, `:1206-1213`) into `night_refused_not_quiet`, and the magistrate's own session is an agent-census hit.

## What the ruling did not consider

1. No positive control on the (iii) probes — a valid-but-wrong regex is indistinguishable from a pass (Q2 amendment).
2. Ed's own `pgrep` argv is an agent-census hit against the armed night (Q3 refutation).
3. A5 never reaches row 3, so the terminal-review trailers are unproven at the bench.
4. The desk clone's `origin` is the writable canonical repo, not a read-only remote.
5. Supporting, not refuting: desk receipts bind the patched HEAD and patched registry sha256, so they cannot be silently promoted into real evidence — worth recording as the residual-risk answer.
6. Bench-prep load and agent presence are themselves night-gate inputs; the ruling fenced Ed's run but not the magistrate's preparation.
7. MATERIAL packet hygiene: the acceptance text being replaced originates in `05-…/12-opus-pairing-refuter-on-ruling-10.md §5`, which exists in the repo but was NOT supplied as an exhibit while the packet forbade the judge from reading it. Neither reviewer could check whether exhibit B's registration faithfully states that authority, or why it was set at full-run strength. Cure on any re-convening: include §5 verbatim. My amendments make (iii) safe on its own terms regardless.
8. NIT: the ruling's recording channel ("a paste into the directive issue") normally needs a browser, which the same text forbids during the run — sequencing now explicit in the Q2 amendment.

## Commands run (tails)

- `shasum -a 256 docs/process/coldgate_charter.md` → `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (= pin)
- `shasum -a 256 …/exhibit-*.md` → all five equal the 00-PACKET manifest
- `sed -n '405,440p;4430,4545p;5530,5575p' joulewise/arm_readiness.py` → patterns/`_plan_profile`/`_registry_reference`/`reviewed_main` as cited
- `python3 -c "json.load(...); print(d['schema_version'], d['registry_id'])"` → `joulewise.arm_readiness_row_registry.v2 d117-row-registry-v2`
- `sed -n '528,540p' configs/arm_readiness/d117_row_registry_v2.json` → `"successor_pack_ids": {"ALPHA":"d117_floor_qwen3-1p7b_v5","BETA":"d117_floor_qwen3-8b_v5","GAMMA":"d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"}` at 532-536
- `grep -c freeze joulewise/arm_readiness_evidence_t0.py` → `0`; `sed -n '1,10p' .gitignore` → `.venv/` at line 6
- `sed -n '431,512p;1300,1330p;1714,1745p;2255,2410p' joulewise/arm_readiness_evidence_t0.py` → `_execute_probe` env, `_expect_absent`, `_derive_process_census`, pre-loop gate + publish path
- `sed -n '20,90p' scripts/author_arm_evidence_t0.py` → refusal dict is `status/kind/reason_codes/detail` only
- `sed -n '210,255p' scripts/capture_t0_step.py` → `_verify_terminal_review`
- `grep -rn 'codex.claude.t3' scripts/ joulewise/` → `night_gate.py:42`, `run_night.py` census sites, `gen_derivation_night.py:58-62` ("no literal … may contain one of these substrings"), `prewindow_check.sh:149`
- `grep -n 'LOAD_MAX' joulewise/night_gate.py` → `57: LOAD_MAX = 2.0`, checked `:1206`
- Not executed, deliberately: any `pgrep`, any capture step, the test suite, anything under `/Users/edr/code/JouleWise`, `JouleWise-*` clones, `night-custody`, `desk-proof-arm-census`, LaunchAgents. Wrote only `/tmp/opus-refuter-65/`.
