# Opus counter-review — CONTRACT lens — PR #321 (NIGHT-INTERPRETER-PIN-01)

- **Heads reviewed:** started at `3b99a1a0` (fix round 3); the branch moved mid-review, so **every
  finding, command and line number below is at `6dddb545` (fix round 4)**, five commits over
  `origin/main` `1dddcfea`. Round 4 (`git diff 3b99a1a0..6dddb545`) is included in B(iv), C and E.
- Worktree `/Users/edr/code/JouleWise-wt-interp-pin`, read-only. No tracked file modified, no git
  state changed, no `~/night-custody`, no `~/Library/LaunchAgents`, no real `launchctl`, no network.
  Temp only under `/tmp/opus-321/`.
- Read: brief `.../58a3bcfc/03-brief-NIGHT-INTERPRETER-PIN-01.md`; refuter `.../58a3bcfc/09-refuter-contract-interp-pin.md`;
  `.../3dab9c89/02-brief-interp-pin-fix-round-3.md` and `03-seat-...md`; `.../58a3bcfc/13-arm-runbook-stub-20260912.md`;
  full `git diff origin/main..HEAD`.
- Baseline suite at HEAD:
  `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent tests.test_run_night`
  → `Ran 109 tests in 14.678s` / `OK`; `/bin/zsh -n scripts/install_night_agent.sh` rc 0;
  `python3 -m compileall -q scripts joulewise` rc 0.

---

## A. Contract sweep — does any clause promise what the code does not, or vice versa?

**No clause in `docs/contracts/*.md` pins the plist's argv[0] or the installer's flag set.** Re-verified
at HEAD, not inherited from refuter 09:

```
$ grep -rn "ProgramArguments" docs/contracts docs/process docs/phase_2 ; echo rc=$?
rc=0        # (no output)
$ grep -rn "usr/bin/env"      docs/contracts docs/process docs/phase_2 ; echo rc=$?
rc=0        # (no output)
```

`docs/process/MAGISTRATE_WATCHDOG.md:175` ("pins the installing `python3` process's absolute
`sys.executable`") governs the **watchdog** installer, a different script; the night installer now
matches that discipline rather than contradicting it. D-175 condition 2 (`docs/decision_log.md:11436`)
requires `install_night_agent.sh --render-only` from the pinned measurement checkout; that still works
with no `--python` (proved in §E1).

Per the four asked-about subjects:

| Subject | Doc clause | Code at HEAD | Verdict |
|---|---|---|---|
| plist argv[0] | none anywhere | `com.joulewise.night.plist.template:9` `<string>@@PYTHON@@</string>`; `install_night_agent.sh:198` `"@@PYTHON@@": escape(python)` | consistent |
| `--python` + default derivation | `NIGHT_HANDBACK.md:132–137`, `derivation_night_runbook.md:1249–1254,1330` | `install_night_agent.sh:50–67` | consistent |
| `preflight` coverage | `NIGHT_HANDBACK.md:143–149`, `derivation_night_runbook.md:175–178,1258–1264,2230` | `run_night.py:42–45` (module-scope), `:1866–1880` (JSON line) | consistent and correctly bounded — see below |
| uninstall independence from a venv | `NIGHT_HANDBACK.md:127–131` | `install_night_agent.sh:151–154` (`/usr/bin/python3`, plain JSON read, no project import), `:155` gates the whole preflight/DEADMAN block on `(( ! uninstall ))` | consistent |

Preflight coverage is now *exactly* stated and I checked it mechanically rather than trusting the
sentence: `grep -nE "^[[:space:]]+(import |from [A-Za-z_.]+ import )" scripts/run_night.py` → rc 1
(zero lazy imports left in the driver), and the six names in the JSON `modules` list are exactly the
module-scope project imports at `run_night.py:42–45`. Refuter 09's F5 ("runs the driver's imports"
over-promises) is cured: both docs now say "every project module it imports **at module scope**" and
explicitly disclaim "functions' lazy imports inside `joulewise`".

**The one contract-text defect this PR introduces is F1 below.**

### F1 — SHOULD_FIX — the round-3 "F3 cure" broke the contract table's declared provenance
`docs/contracts/pack_night_go_receipt.md:637` (changed by `3b99a1a0`).

§7.1's own preamble, `docs/contracts/pack_night_go_receipt.md:627–630`, says:

> "Line numbers below identify seams from the earlier baseline, with third-pass changed pins re-read at
> `d3cab2d4c2937886a25659756374483c7a8dc578`, not completed implementation locations."

The pre-diff pin `scripts/install_night_agent.sh:39–75,132–141` was **correct at that declared
baseline**, not stale:

```
$ git show d3cab2d4c2937886a25659756374483c7a8dc578:scripts/install_night_agent.sh | sed -n '39,44p;130,132p'
plan="${plan:A}"
custody_root="$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["custody_root"])' "$plan")"
courier_bin=""
courier_path=""
if (( ! uninstall )); then
  plan_fields=("${(@f)$(/usr/bin/python3 -B - "$plan" "$repo" <<'PY'
  local entry_minute="$5"
  local log_stem="$6"
  /usr/bin/python3 - "$template" "$out" ... <<'PY'
```

The cure replaced it with `:91–122,182–212`, i.e. `3b99a1a0` line numbers, in a table where **every
other cell still points at `d3cab2d4`**. Two consequences: (a) the table is now internally
inconsistent about which commit its numbers mean; (b) the new pin is already wrong one commit later —
round 4 added seven lines to `render()`, so the render block is `182–220` at HEAD:

```
$ grep -n "^render() {" scripts/install_night_agent.sh ; sed -n '219,220p' scripts/install_night_agent.sh
182:render() {
PY
}
```

**Cure (dictated):** revert `pack_night_go_receipt.md:637` to `scripts/install_night_agent.sh:39–75,132–141`.
If a current pin is genuinely wanted, do not renumber inside the baseline table — add one dated sentence
after `:630` of the form "2026-09-11: seat 2's `install_night_agent.sh` seams were re-read at
`<merge commit>` as `:91–122,182–220`." Note the refuter finding that prompted this (09 F3) was itself
wrong about staleness; the traces it also named (`67-arm-runbook…:192,197,441`) are historical records
and were correctly left alone.

---

## B. Round-3 semantics — `/usr/bin/env python3 -B -S -c '<json read>'`

Fixture: a real v2 `REHEARSAL_STUB` plan authored through `NightPlan`/`write_night_plan`, with a
space in `measurement_root` (`/private/tmp/opus-321/fx/measurement checkout`), at
`/tmp/opus-321/fx/night_plan.json`.

### (i) Safe under `/usr/bin/python3` = 3.9.6 — YES

```
$ /usr/bin/python3 -B -S -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])' /tmp/opus-321/fx/night_plan.json
/private/tmp/opus-321/fx/measurement checkout
rc=0
$ env -i PATH=/usr/bin:/bin /usr/bin/env python3 --version
Python 3.9.6
$ env -i PATH=/usr/bin:/bin /usr/bin/env python3 -B -S -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])' /tmp/opus-321/fx/night_plan.json
/private/tmp/opus-321/fx/measurement checkout
rc=0
```

And end to end — the strongest single proof of the round-3 design — the 3.9.6 that caused the
2026-09-11 crash does the bootstrap read while the plists still name a 3.13 venv:

```
$ /usr/bin/env -i PATH="/tmp/opus-321/bin:/bin:/usr/bin" HOME="$HOME" /bin/zsh scripts/install_night_agent.sh \
    --plan /tmp/opus-321/fx/night_plan.json --hour 0 --minute 30 --render-only /tmp/opus-321/render
{"preflight": "ok", "python": "…/python3.13", "version": "3.13.1", "modules": [...]}
validated pins: repo_head=6dddb545… measurement_root=/private/tmp/opus-321/fx/measurement checkout …
rc=0
$ env -i PATH="/tmp/opus-321/bin:/bin:/usr/bin" /usr/bin/env python3 --version
Python 3.9.6
```

### (ii) `-S` does not break the read under a venv or Homebrew python — CORRECT

```
$ /opt/homebrew/bin/python3 -m venv /tmp/opus-321/venv && /tmp/opus-321/venv/bin/python --version
Python 3.14.7
$ /tmp/opus-321/venv/bin/python -B -S -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["measurement_root"])' /tmp/opus-321/fx/night_plan.json
/private/tmp/opus-321/fx/measurement checkout
$ /tmp/opus-321/venv/bin/python -S -c 'import sys; print(sys.prefix, sys.version_info[:3])'
/private/tmp/opus-321/venv (3, 14, 7)
$ /opt/homebrew/bin/python3 -B -S -c 'import json, sys; print(...)' …
/private/tmp/opus-321/fx/measurement checkout
```

`-S` suppresses `site`, not the frozen `getpath` stdlib resolution, and the one-liner imports only
`json` and `sys`; `sys.prefix` still resolves correctly inside the venv. No breakage in either case.

### (iii) The `A && [[ -n … ]] || { …; exit 2; }` line refuses correctly — ALL FOUR

`scripts/install_night_agent.sh:54–57`. Each run used `--render-only`.

| Case | stderr | rc |
|---|---|---|
| empty `measurement_root` (`""`) | `cannot derive measurement_root/.venv/bin/python from /private/tmp/opus-321/plan-empty.json; pass --python ABS_PATH` | 2 |
| key absent | same message, `…/plan-nokey.json` | 2 |
| non-JSON file | same message, `…/plan-notjson.json` | 2 |
| no `python3` on PATH (`env -i PATH=/tmp/opus-321/emptybin`) | same message, `…/fx/night_plan.json` | 2 |

Nothing was rendered and no custody directory was created in any case. The zsh precedence is right:
if the substitution fails, `&&` short-circuits and the `||` block runs; if it succeeds with empty
output, `[[ -n … ]]` fails and the same block runs. `set -e` does not fire because the assignment is
part of an `&&` list.

**N2 — NIT — the message misdiagnoses the no-`python3` case.** `2>/dev/null` inside the substitution
swallows `env: python3: No such file or directory`, so a missing interpreter is reported as a plan
problem. Cure: capture stderr to a variable and append it, or add `; python3 must be on PATH for this
read` to the message.

### (iv) macOS/CI reachability, including round 4

- **CI is ubuntu-only** (`.github/workflows/ci.yml:18,124,187,292,363,382`; zsh installed at `:39–43`,
  `:309–313`). There is no macOS runner, so CI is a Linux oracle, never a macOS one.
- **Reachable on macOS, invisible to CI:** (1) real `launchctl bootstrap/bootout/print`
  (`install_night_agent.sh:230,253–270`) — stubbed in every test, unchanged by this PR; (2) the CLT
  shim behaviour of `/usr/bin/python3`, which the uninstall path still uses at `:153`. I hit the shim
  for real this session: a `python`-named symlink to `/usr/bin/python3` produced
  `xcode-select: Failed to locate 'python', requesting installation of command line developer tools.`
  and rc 2. Fail-closed, and irrelevant on a host with CLT installed, but no CI job can ever see it.
- **Reachable on CI, invisible locally:** nothing new. Every remaining absolute binary in the install
  path exists on ubuntu-latest — `/usr/bin/env`, `/usr/bin/grep`, `/usr/bin/git`,
  `/usr/bin/base64 --decode` (a GNU long option too), `/usr/bin/python3` (uninstall path only).
  `grep -c plutil scripts/install_night_agent.sh` → `0`, rc 1.
- **Round 4 adds no platform surface:** the only new import is `re`, inside the render heredoc that
  already runs under the validated `$python` (≥ 3.11).

---

## C. Defect-shaped tests — counterfactuals

**1. `tests/test_install_night_agent.py:274–276` `test_installer_has_no_plutil_dependency`.**
Counterfactual: any installer text containing `plutil`. Fails against `1b893ec4` by inspection —
that head's `:52` read `/usr/bin/plutil -extract measurement_root raw -o -`. Tests what its name says.
Limitation worth recording: it is a *text* tripwire, so it would not catch a regression to any other
macOS-only tool (`sw_vers`, `/usr/libexec/PlistBuddy`, `defaults read`).

**2. `tests/test_install_night_agent.py:292–316` `test_default_python_derivation_with_only_path_python3`
— F2 — SHOULD_FIX: not defect-shaped on macOS, and its name overclaims.**
Counterfactual that makes the pre-cure code fail it: *being on Linux*, where `/usr/bin/plutil` is
absent. On macOS the test passes on both sides, because the PATH it builds is
`f"PATH={self.bin_dir}:/bin:/usr/bin"` (`:296–297`) and `/usr/bin` supplies `python3` — so the
`(self.bin_dir / "python3")` symlink the test creates is **not load-bearing**. Proved:

```
$ ls /tmp/opus-321/bin           # courier only, no python3
claude
$ /usr/bin/env -i PATH="/tmp/opus-321/bin:/bin:/usr/bin" HOME="$HOME" /bin/zsh scripts/install_night_agent.sh \
    --plan /tmp/opus-321/fx/night_plan.json --hour 0 --minute 30 --render-only /tmp/opus-321/render
{"preflight": "ok", …}
validated pins: repo_head=6dddb545… 
rc=0
```

The seat's own report says as much ("would still pass on macOS, so it does not independently detect
the defect there"). Consequence: on the machine that arms nights, the *only* guard against a
re-introduced macOS-only bootstrap is finding 1's string match. **Cure:** symlink `id` (needed by
`install_night_agent.sh:180` `uid="$(id -u)"`) into `self.bin_dir` alongside `python3` and `claude`,
set `PATH={self.bin_dir}` alone, and rename to
`test_default_python_derivation_needs_only_a_path_python3`. Then removing the symlink fails the test
on macOS too.

**3. `tests/test_run_night.py:1575–1581`, the no-courier fixture change.**
There is **no** counterfactual: this is a fixture repair, not a regression. Pre-round-3 the test ran
with `PATH=<empty dir>` and reached the courier check; post-round-3 the derivation refuses first, so
the symlink restores the test's own precondition. It still tests what its name says — rc 2 and
`courier unavailable` with `claude` absent (`:1599–1600`), and the derivation succeeds because
`_installer_plan` already creates `<measurement_root>/.venv/bin/python`
(`tests/test_run_night.py:1452–1455`). Side effect → **F3 below**.

**4. Round 4, `tests/test_install_night_agent.py:278–290`
`test_rendered_argv0_is_the_validated_python_even_with_token_like_name`.**
Counterfactual proved by executing both algorithms against the real template:

```
$ python3 -c '<old str.replace loop vs new re.sub, real template, python name "…/python @@MODE@@ & pinned">'
OLD argv0: '/tmp/bin/python dead-man & pinned'
NEW argv0: '/tmp/bin/python @@MODE@@ & pinned'
intended : '/tmp/bin/python @@MODE@@ & pinned'
OLD label: com.joulewise.night.deadman | NEW label: com.joulewise.night.deadman
```

Pre-cure the plists named a nonexistent interpreter, so both `assertEqual(str(python), argv[0])` and
`assertTrue(Path(argv[0]).exists())` fail. Name accurate; the label substitution is unchanged. Using a
lambda (not a string) as the `re.sub` replacement is the right call — it also removes the
backslash-escape hazard a string replacement would have introduced.

### F3 — SHOULD_FIX — the entire round-3 refusal branch has zero test coverage
`scripts/install_night_agent.sh:54–57`.

```
$ grep -rn "cannot derive\|measurement_root/.venv" tests/ ; echo rc=$?
rc=0        # (no output)
```

The round-3 brief required rc 2 for "no `python3` on PATH, unreadable JSON, or a missing
`measurement_root` key" and "an empty string result must also refuse". All four behave correctly
(§B(iii)), but nothing in the suite asserts it, and the one test that previously used a minimal PATH
now seeds `python3` into it (finding 3 above), so the no-`python3` path is untested by construction.
**Cure:** one test in `tests/test_install_night_agent.py` with four `subTest`s — plan with
`measurement_root: ""`, plan with the key deleted, a non-JSON file, and `PATH` without a `python3` —
each asserting rc 2, the `cannot derive measurement_root/.venv/bin/python from <plan>` text, and
`assertFalse(self.rendered.exists())`.

---

## D. Docs pedagogy — first-use test on the changed sentences

Run mechanically, per file (`grep -n` first occurrences).

| Term | `docs/process/NIGHT_HANDBACK.md` | `docs/phase_2/derivation_night_runbook.md` |
|---|---|---|
| `--render-only` | **PASS** — first and only use `:132–133`, glossed in place: "(render the two job files to a directory without installing anything)" | **FAIL — F4** |
| LaunchAgent | **PASS** — first use `:142`, "A **LaunchAgent** is a macOS launchd job file" | **PASS** — first use `:172`, "the second LaunchAgent (a macOS launchd job file)", before `:201` and `:1248` |
| driver preflight | **PASS** — first use `:143`, definition in the same sentence | **PASS** — §Terms `:175–178` precedes `:1254`/`:1258`; glossary row `:2230` distinguishes it from the chain/input preflight (refuter 09 F8 cured) |
| `MIN_PYTHON` | **PASS** — `:136`, "at least `MIN_PYTHON` in `scripts/run_night.py` (currently 3.11)" — names file and value | **PASS** — `:1253`, same form |
| default derivation | **PASS** — `:132–134` states the rule rather than naming a term | **PASS** — `:1250–1252` |
| venv | **PASS** — glossed `:130–131` "a Python virtual environment (a project-specific Python installation)" before the bare uses at `:133,135` | **PASS** — `:299` "`$PY` is the **project venv interpreter**" |

### F4 — SHOULD_FIX — `--render-only` is unglossed and unbuilt in `derivation_night_runbook.md`
`docs/phase_2/derivation_night_runbook.md:1251`.

```
$ grep -n -- "render-only" docs/phase_2/derivation_night_runbook.md
1251:`--render-only` default to `<measurement_root>/.venv/bin/python` when
```

Exactly one occurrence in a 2200-line file, doing load-bearing work ("Install and `--render-only`
default to …"), with no gloss anywhere. This is refuter 09's F6 verbatim — cured in
`NIGHT_HANDBACK.md:132–133`, but the same sentence was carried into the second file without the
parenthetical. A reader of the runbook alone cannot act on it, and `--render-only` is the D-175
condition-2 validation step. **Cure:** copy the handback's gloss — "Install and `--render-only DIR`
(render the two job files into `DIR` without installing anything) default to …".

### N4 — NIT — `preflight` used six lines before its gloss
`docs/process/NIGHT_HANDBACK.md:137` runs `run_night.py preflight --plan PLAN.json` before
`:143` introduces "**A driver preflight** loads the driver module …". Same class as refuter 09 F7
(graded SHOULD_FIX there, at a 22-line gap). Cure: move the `:139–149` mechanism paragraph above the
`:132–137` operational paragraph.

### N7 — NIT — the round-2 `--python ignored on uninstall` notice is undocumented
`scripts/install_night_agent.sh:29–31` now *warns and continues* where it previously called `usage()`.
Neither in-scope doc mentions it, and `.../58a3bcfc/13-arm-runbook-stub-20260912.md:636–638` still
asserts the old behaviour (see §E, F5).

---

## E. Arming consequence — tonight's stub, default derivation, `.venv` = Python 3.13

**The mechanism works.** Faithful simulation at HEAD: `measurement_root` with a space in it,
`.venv/bin/python` → a real `python3.13 -m venv` interpreter, a `claude` stub on PATH, no `--python`:

```
$ PATH="/tmp/opus-321/bin:$PATH" /bin/zsh scripts/install_night_agent.sh \
    --plan /tmp/opus-321/fx/night_plan.json --hour 0 --minute 30 --render-only /tmp/opus-321/render
{"preflight": "ok", "python": "…", "version": "3.13.1", "modules": ["scripts.run_night", "joulewise.arm_readiness", "joulewise.arm_readiness_evidence_t0", "joulewise.t0_rehearsal", "joulewise.night_gate", "joulewise.measurement_liveness"]}
validated pins: repo_head=6dddb54569b71d56a3082453f9a899320fba6b55 measurement_root=/private/tmp/opus-321/fx/measurement checkout measurement_head=5a2b3a32…
rc=0
com.joulewise.night.plist         argv[0]= '/private/tmp/opus-321/fx/measurement checkout/.venv/bin/python'
com.joulewise.night.deadman.plist argv[0]= '/private/tmp/opus-321/fx/measurement checkout/.venv/bin/python'
```

The **bare** venv (no `pip install`, as record 13 §A4 directs) satisfies the preflight under the
stripped job environment — the specific risk A4 bets on:

```
$ /opt/homebrew/bin/python3.13 -m venv /tmp/opus-321/venv313
$ /usr/bin/env -i PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin" HOME="$HOME" \
    /tmp/opus-321/venv313/bin/python -B /Users/edr/code/JouleWise-wt-interp-pin/scripts/run_night.py \
    preflight --plan /tmp/opus-321/fx/night_plan.json
{"preflight": "ok", "python": "/private/tmp/opus-321/venv313/bin/python", "version": "3.13.1", "modules": [...]}
rc=0
```

The `env -i PATH=$courier_path` question resolves clean: the courier is `claude` on PATH,
`courier_path` is built once at `:149` and reused for the preflight (`:157`) and for `@@PATH@@`
(`:189`, `:206`), so the preflight environment and the plist's `EnvironmentVariables.PATH` are
byte-identical by construction (confirmed in the render above:
`PATH= /tmp/opus-321/bin:/usr/bin:/bin:/usr/sbin:/sbin` in both plists).

**Exact stderr an operator would see, per failure I could construct:**

| Failure | stderr (verbatim) | rc | side effects |
|---|---|---|---|
| `.venv` absent from the stub checkout | `missing executable interpreter: <measurement_root>/.venv/bin/python; pass --python ABS_PATH` | 2 | none |
| `.venv/bin/python` is a **real** Python 3.9.6 venv | `interpreter <measurement_root>/.venv/bin/python reports Python 3.9; minimum is 3.11` | 2 | none |
| explicit `--python` at a real 3.9.6 | `interpreter /tmp/opus-321/venv39/bin/python reports Python 3.9; minimum is 3.11` | 2 | none |
| no `python3` on the operator's PATH | `cannot derive measurement_root/.venv/bin/python from <plan>; pass --python ABS_PATH` | 2 | none (misleading text — N2) |
| `claude` not on PATH | `courier unavailable: command -v claude found no executable` | 2 | none |
| `--hour 7` | preflight JSON on stdout, then `refusing --hour 7: it is the dead-man hour (DEADMAN_HOUR=7); arm the night in another hour` | 2 | none |
| a driver import fails under the venv | Python `Traceback …` ending `ImportError: <message>`, no `"preflight": "ok"` line | 2 | no plists, no custody, no `launchctl` call — pinned by `tests/test_install_night_agent.py:327–357` |

The 3.9 refusal is now verified against a **genuine** 3.9.6 interpreter at HEAD, not the unit test's
spoofed `sys.version_info` (`/usr/bin/python3 -m venv /tmp/opus-321/venv39` → `Python 3.9.6`), which
closes refuter 09's F14 empirically for this head; the test-side gap remains.

### F5 — BLOCKER (for tonight's arm; not for merging) — record 13 asserts mechanisms the code no longer has
`docs/process_traces/2026-09-11-activation-58a3bcfc/13-arm-runbook-stub-20260912.md`.

That document is what the operator executes tonight. Four of its statements are false at `6dddb545`:

| Where | Says | Truth at HEAD |
|---|---|---|
| `:629–633` (§A4 reason 1) | "the installer extracts `measurement_root` from the plan with `/usr/bin/plutil -extract` — **no Python at all** … (`install_night_agent.sh:47–58` on the cure branch)" | `:54` runs `/usr/bin/env python3 -B -S -c …`; the block is `:50–62`. The "no Python at all" *rationale* for relying on the default is gone (the read now needs a `python3` on PATH — harmless, see §B(i), but the stated reason is wrong) |
| `:636–638` (§A4 reason 3) | "`--python` combined with `--uninstall` is a usage error (`(( uninstall && python_given )) && usage`)" | `:29–31` prints `--python ignored on uninstall` and **continues** (round 2, refuter 09 F4) |
| `:1122` (Fact table A8) | "default derivation at 47–58 via `/usr/bin/plutil -extract measurement_root`; preflight invocation at 152–154" | `:50–62` and `:155–158` |
| `:734`, `:1124` (A6/A10) | `install_night_agent.sh:123–125` creates `custody_root/night` | `:175` / `:178` |
| `:94`, `:96`, `:880`, `:1123` | pin checks `:81–96`; dead-man-hour refusal `:112–115` | `:128–143` and `:164–167` |

A4's *operational instruction* ("Do not pass `--python`") is still correct and still works (§E1); only
its evidence and its line pins are stale. **Cure:** a dated addendum at the top of record 13
correcting §A4 reasons 1 and 3, Fact-table rows A8/A9/A10, and the five line pins, before Block A
runs. Nothing in PR #321 needs to change for this.

### N5 — NIT — the two A6 paste lines can disagree cosmetically
`install_night_agent.sh:58` derives argv[0] as the **plan's** `<measurement_root>/.venv/bin/python`,
while the preflight JSON reports `sys.executable` (resolved). Record 13 sets
`STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout` (`:464`, `:786`), so both are
`/private/tmp/…` tonight and A6's `assert argv[0] == py` holds. Were a future `STUB_CHECKOUT` written
as `/tmp/…`, argv[0] would say `/tmp/…` and the JSON `/private/tmp/…`; launchd would still work, but
the operator's two paste lines would not match.

---

## Other findings

### N1 — NIT — the round-4 token regex can silently drift from the substitution dict
`scripts/install_night_agent.sh:209–217`. The pattern `r"com\.joulewise\.night|@@[A-Z_]+@@"` is
maintained by hand and today covers all ten template tokens (verified against
`configs/launchd/com.joulewise.night.plist.template`: `@@PYTHON@@ @@REPO@@ @@MODE@@ @@PLAN@@
@@COURIER_BIN@@ @@PATH@@ @@HOUR@@ @@MINUTE@@ @@CUSTODY_ROOT@@ @@LOG_STEM@@`). A future token with a
digit or lowercase letter would not match, would ship literally into the plist, and no test asserts
the absence of a residual `@@…@@` in a rendered file. Cure: build the alternation from the dict —
`re.compile("|".join(re.escape(key) for key in sorted(replacements, key=len, reverse=True)))` — and
add `assert "@@" not in text` before the write.

### N3 — NIT — only `@@PYTHON@@` is XML-escaped
`scripts/install_night_agent.sh:198` applies `escape()` to the interpreter; `repo`, `plan`, `custody`,
`courier`, `path` and `log_stem` are inserted raw (`:199–207`). An `&` or `<` in any of those yields a
malformed plist. Fail-closed in practice (`plutil -lint` and `launchctl bootstrap` reject it, `:255`
→ exit 3 with rollback), and pre-existing, but the asymmetry is now visible in one dict literal.

### N6 — NIT — carried forward from refuter 09, still true at HEAD
F11 (dead-man now shares the run path's import graph) and F12 (hoisted imports write `__pycache__`
unless `-B`; the plist's `ProgramArguments` has no `-B`) are unchanged by rounds 3 and 4 and remain
accepted properties rather than regressions.

---

## Findings index

| # | Severity | Location | One line |
|---|---|---|---|
| F5 | **BLOCKER (arming)** / not merge | `.../58a3bcfc/13-arm-runbook-stub-20260912.md:629–638,734,1122–1124,94,96,880` | Tonight's runbook asserts `plutil`, "no Python at all", a `--python`+`--uninstall` usage error, and five stale line pins |
| F1 | SHOULD_FIX | `docs/contracts/pack_night_go_receipt.md:637` (vs `:627–630`) | The round-3 "F3 cure" renumbered one cell of a table that declares its own `d3cab2d4` baseline; already stale again at HEAD |
| F2 | SHOULD_FIX | `tests/test_install_night_agent.py:292–316` | The restricted-PATH test is not defect-shaped on macOS (`/usr/bin` supplies `python3`); its name overclaims |
| F3 | SHOULD_FIX | `scripts/install_night_agent.sh:54–57`; `tests/` | Zero coverage of the new refusal branch (`grep "cannot derive" tests/` → nothing), and the one minimal-PATH test now seeds `python3` |
| F4 | SHOULD_FIX | `docs/phase_2/derivation_night_runbook.md:1251` | `--render-only` used, never glossed or built in that file — refuter 09 F6 cured in only one of the two docs |
| N1 | NIT | `install_night_agent.sh:209–217` | Hand-maintained token regex can drift from the dict; no residual-`@@`-token assertion |
| N2 | NIT | `install_night_agent.sh:54–55` | `2>/dev/null` turns "no `python3` on PATH" into a plan-shaped message |
| N3 | NIT | `install_night_agent.sh:198–207` | Only `@@PYTHON@@` is XML-escaped |
| N4 | NIT | `docs/process/NIGHT_HANDBACK.md:137` vs `:143` | `preflight` used six lines before its gloss |
| N5 | NIT | `install_night_agent.sh:58` vs `run_night.py:1870` | argv[0] is the plan-derived path, the JSON reports `sys.executable`; `/tmp` vs `/private/tmp` would diverge |
| N6 | NIT | `install_night_agent.sh:29–31` | The `--python ignored on uninstall` notice is documented nowhere |
| N7 | NIT | `run_night.py:42–45`, template `:9–15` | Refuter 09 F11/F12 unchanged: dead-man shares the import graph; no `-B` in `ProgramArguments` |

## VERDICT: MERGEABLE AFTER FIXES

Merge-blocking: none. F1 is the only defect this PR introduces into a contract document, and it is a
one-cell revert. F2–F4 are test-coverage and pedagogy debts that should land in this PR rather than
after it, because F3 leaves a brand-new refusal branch untested and F2 means the machine that arms
nights has no behavioural guard against a re-introduced macOS-only bootstrap. F5 is not this PR's
defect but it gates tonight: record 13 tells the operator the derivation uses `plutil` and "no Python
at all", which is exactly the claim that made the default-derivation choice look safe, and it must be
corrected by dated addendum before Block A.

**Residual risk.** The code path is now proven end to end on this host — the 3.9.6 interpreter that
caused the 2026-09-11 crash can do the bootstrap read, a bare 3.13 venv passes the preflight under the
stripped job environment, the plists name an absolute interpreter byte-identical to the validated one
even when its path contains a template token, and all four refusal modes exit 2 leaving nothing behind.
What remains unproven is everything only a real `launchctl bootstrap` exercises: no CI job runs on
macOS, so the install path beyond `--render-only` is covered solely by a fake `launchctl`, and the
uninstall path's `/usr/bin/python3` is a Command Line Tools shim whose failure mode (`xcode-select:
Failed to locate …`, which I reproduced by accident this session) is structurally invisible to the
Linux oracle. Second-order: the preflight is honest about its bound but the bound is real — a
`datetime.UTC`-class defect inside a lazy import deeper in `joulewise` (`arm_readiness.py:3833,5624,
8052`) would still reach the night unseen, and the hoist has made the dead-man share the run path's
import graph, so a module-scope break now takes down the safety net too. Both are accepted trades, not
new; the mitigation is that the arm-time preflight runs the exact interpreter under the exact PATH.
