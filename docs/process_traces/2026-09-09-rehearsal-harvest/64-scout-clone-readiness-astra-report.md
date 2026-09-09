```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Preparation plan complete: 7ca2908f qualifies for the rehearsal cut; G2-a remains blocked by rehearsal acceptance, four plan inputs, and unresolved production-custody routing.",
  "workspace": {
    "base_requested": "7ca2908f",
    "base_mode": "exact",
    "head_start": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "head_end": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "upstream_end": "7ca2908f66819d534ebc53e3786f32106f6de5ba",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "findings": 5,
      "blocking": 2,
      "nonblocking": 3
    },
    "findings": [
      {
        "id": "F1",
        "text": "NIGHT-REHEARSAL-01 remains blocked on SECOND-STUB-NIGHT-RULING; PLAN_ID, NIGHT_ROOT, T0 and WINDOW_MAX_S remain unruled."
      },
      {
        "id": "F2",
        "text": "The production ledger contains 38 absolute iCloud custody locators. Copying their bytes into clone/runs alone does not redirect the default loader. A production restore route needs a magistrate ruling."
      },
      {
        "id": "F3",
        "text": "7ca2908f contains the inventory, census cure, seat 4 and merged stub-chain cure. Local main is older at 83ab38ed; use the explicit reviewed SHA."
      },
      {
        "id": "F4",
        "text": "Installer render-only writes plists and custody_root/night but does not install. Courier pinning is an executable path pin, not a content digest."
      },
      {
        "id": "F5",
        "text": "Cold gate 44 Q3 and the kernel make powermode recording a queued lane and powermode-zero a recommendation to Ed, not an installed arming gate."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import subprocess,hashlib; h=subprocess.check_output([\"git\",\"rev-parse\",\"HEAD\"],text=True).strip(); p=\"configs/production_custody_inventory.json\"; b=subprocess.check_output([\"git\",\"show\",h+\":\"+p]); assert b==open(p,\"rb\").read(); [subprocess.run([\"git\",\"merge-base\",\"--is-ancestor\",c,h],check=True) for c in [\"07681e95\",\"dee5cfbc\",\"edb4f0ed\",\"a52810c9\"]]; print(\"HEAD=\"+h); print(\"inventory_sha256=\"+hashlib.sha256(b).hexdigest()); print(\"PASS inventory bytes and census/seat4/PR307/PR309 ancestry\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD=7ca2908f66819d534ebc53e3786f32106f6de5ba",
          "inventory_sha256=706c4e78c813f463f49e2a9b1bc941a21fbbd7fe738799c42c5fec050c416cba",
          "PASS inventory bytes and census/seat4/PR307/PR309 ancestry"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS inventory bytes and census/seat4/PR307/PR309 ancestry$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "/bin/zsh scripts/install_night_agent.sh --help",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "usage: usage --plan PLAN.json --hour H --minute M [--uninstall] [--render-only DIR] [--launchctl-bin PATH]"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "usage: usage --plan PLAN.json.*--render-only DIR.*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "G2-a cannot arm from the current kernel state; the cure merged, but rehearsal acceptance and the second-stub-night ruling remain open.",
      "needs": "Obtain the cold-gate or Ed second-stub ruling, close rehearsal acceptance, then rule all four G2-a inputs together."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The literal 99co copy-into-runs recipe does not make the default loader consume copied custody when the immutable ledger locators are absolute iCloud paths.",
      "needs": "Rule the live production custody route and the reviewed inventory entry for the new production clone; preserve issued ledger and pin bytes."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Local main is 83ab38edcacd67312171c0051cc31cc70a9be682; detached HEAD and origin/main are 7ca2908f66819d534ebc53e3786f32106f6de5ba.",
      "needs": "Cut by explicit SHA, not the local main name."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No clone, plan, plist, ledger restore, installer render, hardware probe, measurement or test suite was executed. Prospective commands below require the magistrate's bench authority.",
      "needs": "Execute and retain the proposed preparation evidence at the bench."
    },
    {
      "id": "F5",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Powermode plan/receipt recording is not implemented by this scout; v2 has an exact key set. Do not add an invented powermode field or promote the recommendation to a gate.",
      "needs": "Continue POWERMODE-PREFLIGHT-RECORD-01 under its owning design process and include the recommendation in Ed's hardware handoff."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| A. Cut and inspect fresh rehearsal clone | start_now | Magistrate bench execution; code prerequisites are present | New independent directory only |
| B. Reconstruct locked environment and perform structural/render validation | start_now | A for clone-bound checks | Clone `.venv`, staging plists, fresh dry custody |
| C. Resolve production inventory and custody routing | needs_ruling | Magistrate disposition described below | Reviewed inventory, immutable ledger locators |
| D. Prepare production clone and authenticate restored evidence | wait_for | C | New production clone; retained production evidence |
| E. Close rehearsal acceptance and second-stub decision | needs_ruling | Cold gate or Ed | Stub schedule, courier evidence, both night-agent labels |
| F. Select four G2-a inputs and stage real plan | wait_for | D, E | Night identity, date-derived probe roots, watchdog discovery |
| G. Complete Ed hardware preparation | wait_for | Concrete production checkout and hardware checklist | Privilege and physical machine state |
| H. Email, publish and install diagnostic plan | wait_for | F, G and all fences below | Watchdog glob and two global LaunchAgent labels |
| I. Collect while this scout or another agent is active | do_not_start | Zero-agent window | Quiet-Mac measurement validity |

All commands below are **prospective**, except the probes recorded in the envelope. No scope expansion is needed to deliver this plan.

### A. Exact rehearsal cut

Authority aliases:

- **99co:** [clone plan and amendment](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process_traces/2026-09-08-handoff-redo/99co-magistrate-note-clone-readiness-plan.md)
- **99ey/13:** [second-gate magistrate synthesis](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process_traces/2026-09-08-handoff-redo/99ey-coldgate-packet-d176-second-gate/13-magistrate-synthesis.md)
- **99cd:** [G2-a draft README](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md)

**Qualifying head today:** `7ca2908f66819d534ebc53e3786f32106f6de5ba`.

The inventory-bearing file is `configs/production_custody_inventory.json`, SHA-256:

```text
706c4e78c813f463f49e2a9b1bc941a21fbbd7fe738799c42c5fec050c416cba
```

The head also contains:

- Census cure `07681e95`, including `joulewise/arm_readiness.py` and `joulewise/night_gate.py`.
- Seat-4 work and fix `dee5cfbc`, including `joulewise/t0_rehearsal.py`, merged through PR #307 at `edb4f0ed`.
- Stub-chain cure merged through PR #309 at `a52810c9`.

Thus the additional kernel instruction, “Cut the rehearsal clone only after NIGHT-GATE-STUB-CHAIN-01 merges,” is satisfied. This establishes **cut eligibility**, not night acceptance.

**Required form and location:**

> 99co:11: “Re-cut the clone at the post-merge main head … (recipe: trace 67 / runbook 27)”

Trace 67:11 supplies `git clone --no-hardlinks /Users/edr/code/JouleWise` followed by `checkout --detach`. Neither 99co nor 99ey requires a `git worktree` form for the new rehearsal. Use the independent-clone form; the historical `/private/tmp` detached worktree was a stub-specific arrangement.

> 99co:36: “fresh `JouleWise-rehearsal-<date>-<sha>` clone … NOT inventoried”

> 99ey/13:18–21: “must not equal, contain, or be contained by any `deployment_measurement_root` entry” and basename “must start with … `JouleWise-rehearsal-`”.

Use `/Users/edr/JouleWise-rehearsal-20260909-7ca2908`. `/Users/edr/` is the proposed non-iCloud parent, not an extra literal mandated by 99ey. The binding location rule is disjointness. Keep the clone outside `~/night-custody`; pack-rehearsal custody separately uses `~/night-custody/<window_id>` under 99ey/13:39–44.

```bash
# Magistrate bench; do not substitute the stale local main reference.
set -euo pipefail
export REVIEWED_HEAD=7ca2908f66819d534ebc53e3786f32106f6de5ba
export CUT_DATE=20260909
export MEASUREMENT_ROOT="/Users/edr/JouleWise-rehearsal-${CUT_DATE}-${REVIEWED_HEAD:0:7}"
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1

test ! -e "$MEASUREMENT_ROOT"
test ! -L "$MEASUREMENT_ROOT"
git -C /Users/edr/code/JouleWise cat-file -e "$REVIEWED_HEAD^{commit}"
git clone --no-hardlinks /Users/edr/code/JouleWise "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$REVIEWED_HEAD"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$REVIEWED_HEAD"
test -z "$(git -C "$MEASUREMENT_ROOT" status --porcelain=v1 --untracked-files=all)"
```

**“Un-inventoried” does not mean deleting the inventory file.** It means the rehearsal checkout is absent from the production deployment census and does not overlap its roots.

> 99ey/13:22–25: inventory bytes “must equal `git show <plan.repo_head>:configs/production_custody_inventory.json` … (never `HEAD:`)”.

> 99ey/13:9–12: production “runs, custody and ledger roots” come from the reviewed inventory.

> 99co:35,37: production is “never used for a rehearsal”; rehearsal “needs no ledger restore (its runs/ is its own).”

Therefore copy **no production `runs/`, physical ledger, custody, backups, prior night records, or existing `.venv`** into rehearsal. Retain committed configuration—including the inventory and committed ledger pin—unchanged. A fresh rehearsal may later create its own runs and custody through the governed rehearsal procedure.

Before building its environment, prove inventory identity, disjointness and absence of carried-over files:

```bash
cd "$MEASUREMENT_ROOT"
export PYTHONPATH="$MEASUREMENT_ROOT"

python3 -B - <<'PY'
import hashlib, json, os, subprocess
from pathlib import Path
from joulewise.arm_readiness import production_custody_roots

root = Path(os.environ["MEASUREMENT_ROOT"]).resolve(strict=True)
head = os.environ["REVIEWED_HEAD"]
assert root.name.startswith("JouleWise-rehearsal-")
inventory_file = root / "configs/production_custody_inventory.json"
assert not inventory_file.is_symlink()
raw = inventory_file.read_bytes()
assert raw == subprocess.check_output([
    "git", "-C", str(root), "show",
    head + ":configs/production_custody_inventory.json"
])
for member in production_custody_roots(
        home=Path("/Users/edr"), inventory=json.loads(raw)):
    assert member.resolution_error is None, member
    other = member.path.resolve(strict=False)
    assert root != other and root not in other.parents and other not in root.parents, member

assert not (root / "runs").exists() and not (root / "runs").is_symlink()
extra = subprocess.check_output([
    "git", "-C", str(root), "ls-files", "--others"
])
assert not extra, extra.decode()
print("inventory_sha256=" + hashlib.sha256(raw).hexdigest())
print("PASS fresh clone: disjoint census, no carried-over runs or untracked files")
PY
```

This is a fresh-cut proof. Once preparation creates `.venv` or rehearsal-owned evidence, preserve this baseline rather than expecting the empty-files condition to remain true.

### B. Environment, installer pins and dry validation

Use the runsheet’s **Plan-derived measurement variables / Future measurement clone preparation** recipe, with the preflight’s `PYTHONPATH` active:

```bash
cd "$MEASUREMENT_ROOT"
export PYTHONPATH="$MEASUREMENT_ROOT" PYTHONDONTWRITEBYTECODE=1
python3.13 -m venv .venv
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt \
  charset-normalizer requests urllib3
diff -u \
  <(grep -Ev '^(#|[[:space:]]*$)' env/mac-measurement-lock.txt | sort) \
  <(.venv/bin/python -m pip freeze --exclude-editable | sort)
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Expected: empty lock diff, clean tree. An ignored `*.egg-info/` directory does **not** excuse an extra `joulewise==0.1.0` in the lock comparison; 99co:5–13 explicitly identifies both separate defects.

The installer’s exact behavior is:

| Check | Source and consequence |
|---|---|
| Driver head | `repo` derives from the invoked script’s directory. Lines 80–87 compare `plan.repo_head` with `git -C "$repo" rev-parse HEAD`; mismatch exits 3. |
| Measurement head | Lines 89–96 compare `plan.measurement_head` with `git -C "$measurement_root" rev-parse HEAD`; mismatch exits 3. |
| Courier executable | Lines 97–103 use `command -v claude`, require an executable, and resolve it with `${courier_bin:A}`. The template receives that path as `--courier-bin`, plus a restricted PATH. **No courier SHA-256/version comparison exists.** |
| Plan validation | `NightPlan.from_mapping`; no future authorship; age at most 36 hours; additional root whitespace check. |
| Schedule | Valid hour/minute; rejects the dead-man hour. It does **not** itself prove hour/minute match T0 or that the whole window finishes before 07:00. |
| Prior records | Refuses existing files **or symlinks** named `receipt.json`, `result.json`, `refusal.json`, `chain.started`, `chain.exited`, `courier.json`, `courier.sent`. |
| Render-only | Creates render directory and `custody_root/night`, renders both plists, then exits before launchctl operations. |

Relevant script quotations:

```text
83–85: plan repo_head does not match driver checkout HEAD
92–94: plan measurement_head does not match measurement checkout HEAD
97:    courier_bin="$(command -v claude || true)"
103:   courier_bin="${courier_bin:A}"
193–195:
       if [[ -n "$render_only" ]]; then
         print "validated pins: repo_head=..."
         exit 0
```

[NIGHT_HANDBACK.md:116–138](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process/NIGHT_HANDBACK.md:116) requires installation **from the measurement checkout**. Consequently, for this procedure both plan heads equal the clone’s head. `repo_head` is not the magistrate’s changing development HEAD.

The installer has **no `--check` or supported `--help` flag**; `--help` produces usage and exit 2. The generator supports both `--help` and read-only `--check`. Do not combine `--emit-chain` with `--check`: emission is handled first and writes.

**Concrete render-only rehearsal probe**

This is a disposable `REHEARSAL_STUB` v2 plan, not G2-a approval or pack-rehearsal qualification. Use a fresh staging directory outside watchdog discovery. Set `DRY_T0` to a future whole-minute instant with an explicit offset.

```bash
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export DRY_ID="DRY-ONLY-clone-${CUT_DATE}-${REVIEWED_HEAD:0:7}"
export DRY_STAGE="/Users/edr/night-plan-staging/$DRY_ID"
export DRY_T0='<future whole-minute ISO timestamp with UTC offset>'
test ! -e "$DRY_STAGE"
test ! -L "$DRY_STAGE"

"$PY" -B scripts/gen_g2_phase_d.py --help
"$PY" -B scripts/gen_g2_phase_d.py --check

"$PY" -B - <<'PY'
import os, time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ["MEASUREMENT_ROOT"]).resolve(strict=True)
stage = Path(os.environ["DRY_STAGE"])
t0 = datetime.fromisoformat(os.environ["DRY_T0"])
assert t0.tzinfo is not None and t0.second == t0.microsecond == 0
t0 = t0.astimezone(ZoneInfo("America/Los_Angeles"))
deadline = t0.replace(hour=7, minute=0, second=0, microsecond=0)
if deadline <= t0:
    deadline += timedelta(days=1)
now = time.time()
assert now < t0.timestamp() <= now + 36 * 3600
assert t0.hour != 7 and t0.timestamp() + 900 + 300 < deadline.timestamp()
custody = stage / "custody"
plan = NightPlan.from_mapping({
    "schema": "joulewise.night_plan.v2",
    "schema_version": 2,
    "plan_id": os.environ["DRY_ID"],
    "receipt_class": "REHEARSAL_STUB",
    "t0_epoch_s": t0.timestamp(),
    "window_max_s": 900,
    "authored_epoch_s": now,
    "repo_head": os.environ["REVIEWED_HEAD"],
    "measurement_root": str(root),
    "measurement_head": os.environ["REVIEWED_HEAD"],
    "chain_path": str(custody / "chain.zsh"),
    "chain_sha256_path": str(custody / "chain.zsh.sha256"),
    "custody_root": str(custody),
    "registration_path": str(root / D166_REGISTRATION_PATH),
})
print(write_night_plan(stage / "night_plan.json", plan))
print(f"render schedule: --hour {t0.hour} --minute {t0.minute}")
PY

# Fill these from the printed schedule above.
scripts/install_night_agent.sh \
  --plan "$DRY_STAGE/night_plan.json" \
  --hour '<printed hour>' --minute '<printed minute>' \
  --render-only "$DRY_STAGE/render"

/usr/bin/plutil -lint "$DRY_STAGE/render/com.joulewise.night.plist"
/usr/bin/plutil -lint "$DRY_STAGE/render/com.joulewise.night.deadman.plist"
```

Expected installer tail:

```text
validated pins: repo_head=7ca2908f66819d534ebc53e3786f32106f6de5ba measurement_root=/Users/edr/JouleWise-rehearsal-20260909-7ca2908 measurement_head=7ca2908f66819d534ebc53e3786f32106f6de5ba
```

Inspect both plist driver paths, courier path, plan path and local schedules. Do not publish this dry plan into `~/night-custody`.

For the **production G2-a** validation, use 99cd’s `validate_plan.py --draft ...` after preparing a successor draft with the new production root, both full heads, and registration path. The existing draft hard-codes `1c83f2af`; exporting new environment variables does not retarget it. Its help probe succeeded:

```bash
"$PY" -B "$TRACE/validate_plan.py" --help
"$PY" -B "$TRACE/validate_plan.py" \
  --draft "$SUCCESSOR_DRAFT" \
  --plan-id "$PLAN_ID" --custody-root "$NIGHT_ROOT" \
  --t0 "$T0_ISO" --window-max-s "$WINDOW_MAX_S" \
  --authored-at "$AUTHORED_AT_ISO"
```

Expected final tail:

```text
PASS dry validation only; magistrate inputs are not approved and no live gate was evaluated
```

99cd:5–9 says this validator serializes in memory, syntax-checks the generated chain on stdin, and executes only its read-only routing prefix. Publish any eventual plan with `write_night_plan`; v2 has exactly 14 keys and no interpreter or powermode convenience field.

### C–D. Production re-cut and custody ruling

**The August checkout is preserved.** D-171 named `/Users/edr/JouleWise-measurement-20260813` as the checkout of record, but trace 27:159,192 and the current runsheet explicitly require a fresh production checkout and prohibit repurposing the protected historical clone. Nothing here requires Ed to move it.

Use the production recipe’s fresh path:

```text
/Users/edr/JouleWise-measurement-v5-<YYYYMMDD>-<head7>
```

Unlike rehearsal, it must remain an inventoried production deployment:

> 99co:35: “stays an inventoried production deployment”.

The shipped inventory names the old `...20260910-1c83f2a` clone, not a new `...-7ca2908` path. The magistrate must settle and review the new inventory locator and final head/name relationship; do not silently omit the replacement deployment, delete a retained entry, or move a frozen checkout.

**Newly observed custody problem:** the canonical physical ledger exists and contains 76 rows, with SHA-256:

```text
aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f
```

Its 38 distinct `custody_locator` values are **absolute paths under**:

```text
/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/
```

The committed pin is sequence 76, head digest:

```text
08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7
```

99co:14–17 requires:

> “Restore the ledger byte-exact: `rsync -a --checksum` … and every custody directory … into `<clone>/runs/` … `verify_custody=True` … pinned sequence, no rollback.”

However, `calibration_ledger.py:1786–1788` resolves only **relative** locators against `repo_root`. Absolute locators remain absolute. Copying these directories into the new clone therefore does not make the default loader authenticate the copies.

**NEEDS_RULING — production custody route**

- **Question:** Should live production authenticate the immutable ledger’s existing absolute custody locations, or use an explicitly governed local custody-store route?
- **Options:** preserve original-location consumption; or establish a reviewed local-store mechanism accepted by all live consumers.
- **Recommendation:** resolve the live-consumer route before claiming the local restore complete. Do not rewrite ledger locators, reset the pin, bootstrap a new ledger, or silently substitute a post-hoc relocation mechanism.
- **Blocked work:** final production restore/authentication certification. Rehearsal preparation remains independent.

The source ledger can be enumerated without accessing the iCloud custody contents:

```bash
python3 -B -c '
import json
from pathlib import Path
rows = [json.loads(s) for s in Path(
    "/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl"
).read_text().splitlines() if s.strip()]
locators = set()
def visit(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "custody_locator":
                locators.add(child)
            visit(child)
    elif isinstance(value, list):
        for child in value:
            visit(child)
for row in rows:
    visit(row)
print("\n".join(sorted(locators)))
'
```

After the ruling, the authorized bench copies the ledger using `rsync -a --checksum`, copies every required custody directory with preserved bytes and structure, and retains listing/hash comparisons. Then authenticate **from the production clone**:

```bash
"$PY" -B - <<'PY'
import json, os
from pathlib import Path
from joulewise.calibration_ledger import load_calibration_ledger_snapshot

root = Path(os.environ["MEASUREMENT_ROOT"])
pin = root / "configs/calibration/calibration_ledger_head.json"
snapshot = load_calibration_ledger_snapshot(
    root / "runs/calibration_observation_ledger.jsonl",
    pin,
    repo_root=root,
    verify_custody=True,
)
expected = json.loads(pin.read_text())
assert not snapshot.refusal_reasons, snapshot.refusal_reasons
assert snapshot.head_sequence == expected["sequence"]
assert snapshot.head_digest == expected["head_digest"]
print(f"PASS custody authentication sequence={snapshot.head_sequence}")
PY
```

That default-loader command still consumes the absolute locations unless the ruled mechanism changes the call appropriately. A byte hash of the ledger alone is not custody authentication.

### E–H. G2-a inputs and all applicable fences

**All four inputs remain NEEDS_RULING.** 99cd:55–67 recommends ruling them together **after rehearsal acceptance**, not adopting its dry samples.

| Input | Draft proposal |
|---|---|
| `PLAN_ID` | Fresh safe night identity. `DRY-ONLY-g2a-20260910` is explicitly non-authorizing. |
| `NIGHT_ROOT` | Fresh absolute, non-symlink `/Users/edr/night-custody/<identity>`; distinct from stub, probe, G2-b and claim roots. No selected production directory. |
| `T0` | Offset-aware ISO instant, whole local minute; derive probe date in `America/Los_Angeles`. `2026-09-10T02:56:00-07:00` is only an example. |
| `WINDOW_MAX_S` | Reviewed positive integer with actual runtime headroom. `10800` is only an example. At 02:56, window + 300 seconds ends at 06:01; the strict maximum is **less than 14340 seconds**. |

Before arming `DIAGNOSTIC_NO_PACK`:

1. **Close the current rehearsal dependency.** The kernel marks `NIGHT-REHEARSAL-01` BLOCKED/PARTIAL. PR #309’s cure is satisfied; `SECOND-STUB-NIGHT-RULING` remains pending for the cold gate or Ed. Cold-start evidence, inbox confirmation and morning-before dead-man acceptance are not all complete. The magistrate cannot waive them.
2. **Send acceptance item 4’s stage-1 email before diagnostic installation.** Exact kernel text: “The stage-1 plan email (first armed date; launches without Ed’s hand unless he replies NO) is sent before `install_night_agent.sh` arms a `DIAGNOSTIC_NO_PACK` plan.” Record delivery evidence and check for NO.
3. **Apply the clone separation.** Fresh production v5 clone, authenticated ledger/custody, clean tree and exact lock. Any further stub uses its separate reviewed rehearsal checkout. The 99ey live pack rehearsal and G1–G10 are requirements for the pack-bound route; do not invent a requirement that G2-a first obtain a transaction-pack receipt.
4. **Retire completed stub discovery roots and agents through the governed handback.** Preserve evidence; never reuse stub custody for G2-a.
5. **Freeze the reviewed head and concrete plan.** Rewrite and commit NIGHT_HANDBACK with actual pins before the email; if that creates a successor reviewed head, re-cut/re-pin and repeat validation. Freeze model revisions, environment, chain, registration, probe inventory, calibration plan, identity epoch and bindings.
6. **Authenticate G2-a inputs.** Use 99cd’s build/bind/check recipe; preserve the four-rung identity convention, five small-model members per rung, large-model probes, `SETTLE_S=600`, and the governed policy. Refuse reused date-derived evidence roots.
7. **Preserve class semantics.** G2-a is `DIAGNOSTIC_NO_PACK`; C2 is `NOT_APPLICABLE` with `no_pack_by_design`. Required registration, quiet-machine, boot/clock and no-retry checks still apply. No G2-b or claim collection is admitted by this class.
8. **Stage outside the watchdog glob.** Canonical writer → validate/render → inspect → email → atomic publication → install. No malformed or incomplete plan under `~/night-custody/*/night_plan.json`.
9. **Satisfy schedule and freshness checks.** Actual authorship, at most 36 hours old, not future-authored; local installer schedule equals T0; window plus 300-second courier budget finishes strictly before 07:00.
10. **Observe the agent and process fences.** No OTHER agent at arm time; arming session exits by T0−25 minutes; watchdog TERM/KILL fences at T0−16/T0−15. Driver census is its first act and repeats every 30 seconds. No active or indeterminate prior measurement ownership.
11. **Satisfy live readiness.** Governed privilege, model/runtime, clock, HID idle, thermal/load, physical machine-state and watchdog-health checks remain live gates. Do not invoke the full preflight from this scout: it has no no-sudo mode and imports MLX. Never manually run the night driver as a “test.”
12. **Retain the frozen triple and cancellation route.** Include `(plan_id, measurement_root, measurement_head)` in relaunch prompts until completion. Ed’s NO always cancels.

**D-175’s eight conditions:** [synthesis lines 35–52](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md:35) require committed handback; canonical staged writer/render/atomic move; fresh custody and both agents from the pinned checkout; prior email/no NO; no other agent; pin reachability; exit at T0−25 plus frozen triple; and the same safeguards on authorized re-arm/removal.

Those eight were explicitly attached to `REHEARSAL_STUB`. As 99cd:76–81 states:

> “D-175’s eight conditions specifically qualify `REHEARSAL_STUB`; they do not prove real measurement readiness.”

The diagnostic route inherits the standing staging/email/ownership discipline and additionally requires its real-machine gates.

**Powermode is a distinct record/recommendation item.** [Cold gate 44 Q3:170–185](/Users/edr/code/JouleWise-wt-ref-308-delta/docs/process_traces/2026-09-09-rehearsal-harvest/44-coldgate-ruling-replay-verdict.md:170) says:

> “registration only, design later”

and:

> “Arming recommendation for Ed (no gate installed by the magistrate)”.

`POWERMODE-PREFLIGHT-RECORD-01` remains queued. Its kernel fence says “the lane records, it does not gate”; refuse-versus-flag is deferred. Record `pmset -g custom` and `pmset -g batt`, establish calibration powermode with source/confidence, and carry the recommendation to Ed. Do not claim implementation is complete or add unrecognized fields to v2.

### G. Ed hardware handoff versus agent preparation

**Agent can pre-stage without Ed:**

- Independent clone creation, locked environment reconstruction and static checks.
- Production inventory proposal and custody enumeration/hash manifest.
- Ledger/custody restore once the routing ruling is settled and sources are readable.
- Canonical draft, generated chain, syntax/schema/routing validation and render-only plists.
- Concrete handback and email content, exact schedule and cancellation instructions.
- User-level night-agent installation after all prerequisites under the authorized procedure; it does not inherently require sudo.

**Ed’s batch should contain only concrete hardware/access needs:**

- Governed noninteractive authorization check:

  ```bash
  /usr/bin/sudo -n -l /usr/bin/powermetrics
  ```

  Missing authorization requires Ed’s governed sudoers/setup action. No password-prompt fallback at night; no capture is needed for this listing check.

- AC/high-power configuration, lid/display/backlight and sleep-state preparation; any still-applicable privileged service action must be confirmed before requesting it.
- Powermode recommendation: prefer mode 0 for real/pack nights until calibration state is established. Cold gate 44 names System Settings → Battery → Low Power Mode “Never”, or Ed’s `sudo pmset -a powermode 0`. Ask for calibration-state recollection with confidence if no record exists, plus whether Low Power Mode was on during replay `58d9225b`.
- Any source-access problem preventing authentication of the existing absolute custody locations.
- Privileged-anchor positive control when the pack-rehearsal lane requires it; this scout supplies no such hardware evidence.

Do **not** ask Ed to advance `/Users/edr/JouleWise-measurement-20260813`, manually paste transaction approval, or provide a new per-window GO. The fresh production clone replaces that operational role for G2-a; D-171’s automation delegation and Ed’s veto remain in force.

## Critical path

- **A → B:** clone cut precedes clone-bound environment and installer validation.
- **C → D:** inventory and absolute-custody routing decisions precede a credible production restore.
- **E → F:** rehearsal acceptance precedes selecting the four production coordinates.
- **D + F + G → H:** authenticated production checkout, reviewed plan and hardware readiness precede email/publication/installation.
- **H → agent exit → launchd:** the unattended driver, after the zero-agent fence, performs acquisition.
- **Separate pack route:** fresh un-inventoried clone plus 99ey’s real T0_REHEARSAL/G7/G1–G10 evidence precedes pack-bound qualification; neither this dry validation nor G2-a discharges it.

The next exact bench action is **A: cut the independent rehearsal clone at `7ca2908f` and retain its inventory/disjointness/freshness proof**. In parallel preparation, route the second-stub decision and production custody question to their authorities.