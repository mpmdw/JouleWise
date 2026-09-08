# G2A-FIRST-WINDOW-01 — draft, not an armed plan

**NEEDS_RULING / PROVISIONAL.** All 14 v2 keys are present, but magistrate
inputs intentionally remain placeholders. The draft itself is not consumable
by the night driver. `validate_plan.py` substitutes explicit argv inputs,
loads the clone's `NightPlan.from_mapping`, serializes with the canonical
writer in memory, renders the clone's G2-a chain, syntax-checks it on stdin,
and executes only its read-only routing prefix. It never publishes a plan,
creates a chain, reserves a ledger bracket, invokes the driver, or collects.

The supplied worktree started clean at `ac092ccd507c2e369ac4642dfce31352769ee698`.
The measurement clone was inspected read-only at detached
`1c83f2af48df5611c7bbf824bec818209c252d0d`; its venv reports Python 3.13.1.
No clone, custody, scheduling, handback, or bookkeeping file was modified.

## Sources and every plan field

Source anchors below refer to the supplied measurement head unless noted.

- **R:** [trace 27 runbook](/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/27-scout-v5-readiness-astra-report.md), read in full; §§3–5 own rehearsal acceptance, first real plan and acquisition. Its old-routing finding is superseded by the landed routing source.
- **N:** [night_gate.py](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/joulewise/night_gate.py), constants, `_PLAN_KEYS`, `NightPlan.from_mapping` and freshness check.
- **W:** [night_plan_writer.py](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/joulewise/night_plan_writer.py), `night_plan_mapping`, `night_plan_json_bytes`, `write_night_plan`.
- **G:** [gen_g2_phase_d.py](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/scripts/gen_g2_phase_d.py), `render_g2a_night_chain` and `emit_g2a_night_chain`; [runsheet](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md), G2-a exports L328–351 and plan-derived variables L1534–1598.
- **I:** [installer](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/scripts/install_night_agent.sh), pin checks, render-only and install; [driver](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/scripts/run_night.py), `_run_chain_once`, completion/dead-man check.
- **H:** [NIGHT_HANDBACK](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/docs/process/NIGHT_HANDBACK.md), standing rules and next lane; [watchdog rules](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/docs/process/MAGISTRATE_WATCHDOG.md), fence/deadlines and first-real-window paragraph; [D-175 synthesis](/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a/docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/13-magistrate-synthesis.md).

| Field | Value/provenance |
|---|---|
| `schema` | `joulewise.night_plan.v2`; N/W, R §4 |
| `schema_version` | integer `2`; N/W |
| `plan_id` | `<PLAN_ID>`: magistrate selects a fresh night identity; R §4 does not name it. This is separate from the generated probe/calibration plan IDs. |
| `receipt_class` | `DIAGNOSTIC_NO_PACK`; R §4, D-169 stage 2. C2 is `NOT_APPLICABLE/no_pack_by_design`; G2-b is excluded. |
| `t0_epoch_s` | `<T0>`: magistrate supplies offset-aware ISO time via `--t0`; converted to epoch. Derive the chain's YYYYMMDD from **America/Los_Angeles** at this same instant. No actual start is selected here. |
| `window_max_s` | `<WINDOW_MAX_S>`: positive integer, magistrate input; R §4 supplies an estimate, not a frozen budget. |
| `authored_epoch_s` | `<AUTHORED_AT>`: use the actual publication preparation time, separately from scheduled T0. `--authored-at` is only for reproducible dry runs; arm-time writer uses `time.time()`. N caps age at 36 hours and refuses future authorship. |
| `repo_head` | clone's observed full HEAD above; R §4 installs driver from the measurement clone, so both heads agree. It is deliberately not the desk worktree head. |
| `measurement_root` | `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a`; user-supplied root, confirmed by Git and `.venv/pyvenv.cfg`. |
| `measurement_head` | clone's observed full HEAD above; `git -C <root> rev-parse HEAD`. |
| `chain_path` | `<NIGHT_ROOT>/chain.zsh`; R §4 and G. Chain bytes come exclusively from G at the pinned clone, with the ruled local date. |
| `chain_sha256_path` | `<NIGHT_ROOT>/chain.zsh.sha256`; G emits a GNU-format sidecar over the exact chain bytes. |
| `custody_root` | `<NIGHT_ROOT>`: fresh absolute night-custody directory chosen by magistrate, distinct from rehearsal, diagnostic probe, G2-b and claim roots; R §4/H. |
| `registration_path` | clone + N's `D166_REGISTRATION_PATH`; verified SHA-256 `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265`. |

There is **no interpreter field in v2**. I/G/preflight derive
`<measurement_root>/.venv/bin/python`; do not add a convenience key. G derives
`d117-g2a-prefill-probe-YYYYMMDD`, suffixes `-calibration`, `-cal-pre`,
`-cal-post`, and `evidence-` prefix, plus the probe root
`/Users/edr/JouleWise-shakedown-g2/g2-a-YYYYMMDD`. This root is distinct from
the night driver's `<NIGHT_ROOT>`. Reattempts must not reuse prior evidence;
the generator currently changes only the date, so a same-date identity
collision returns to the magistrate.

## NEEDS_RULING

**Question:** What fresh `PLAN_ID`, `NIGHT_ROOT`, local T0/date and reviewed
`WINDOW_MAX_S` should replace the placeholders for the first real attempt?

**Options considered:** freeze the rehearsal's 02:56 slot and a three-hour
budget without authorization; or retain explicit inputs until the magistrate
reviews the schedule, runtime headroom and custody inventory.

**Recommendation:** retain the placeholders and rule all four together after
rehearsal acceptance. The log's `2026-09-10T02:56:00-07:00`, `10800`, and
`DRY-ONLY-g2a-20260910` coordinates are structural examples, not selected
production values. At that sample T0, 10800 seconds plus 300 seconds ends at
06:01 PDT, before 07:00. The hard bound is strictly less than 14340 seconds
(239 minutes); equality refuses. Review actual headroom, not just arithmetic.

**Blocked work:** replacing inputs with approved production values and
certifying this draft ready to arm. There is no scope expansion request:
this assignment only prepares the four artifacts. All real-arm work below
belongs to a separately authorized magistrate session.

## Magistrate procedure after the ruling and prerequisite closure

These commands are prospective and were **not executed**. D-175's eight
conditions specifically qualify `REHEARSAL_STUB`; they do not prove real
measurement readiness. H and R §4 supply the first-real email-then-arm route.
Apply the staging discipline below to keep an incomplete real plan outside
watchdog discovery. No extra per-window Ed GO is owed under D-171; an Ed NO
always cancels the arm.

1. Accept and harvest the post-watchdog rehearsal: launchd origin, stub
   completion, actual courier delivery ID/results branch, applicable dead-man
   stand-down, owned-process absence and empty **production** census. A stub
   receipt refusing agents does not establish quietness. Uninstall both stub
   night agents from their recorded installing checkout. Inventory and archive
   every stub plan root outside `~/night-custody/*/night_plan.json` discovery,
   preserving evidence; never reuse a stub checkout for a real plan.
2. Close the prerequisites below, update the lead-owned H for this night and
   review the acquisition head. H currently describes the September 9 stub.
   Its rule to commit each night's rewrite may require a successor reviewed
   head: if so, re-pin this draft and re-run validation; do not silently move
   this clone or publish a plan with the old head. Freeze the reviewed clone,
   driver, environment, model bytes and chain inputs through the window.
3. In the magistrate's authorized shell, export the ruled values (angle
   brackets are instructions to fill, not runnable choices):

   ```sh
   set -euo pipefail
   export MEASUREMENT_ROOT=/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a
   export MEASUREMENT_HEAD=1c83f2af48df5611c7bbf824bec818209c252d0d
   export PY="$MEASUREMENT_ROOT/.venv/bin/python"
   export PYTHONPATH="$MEASUREMENT_ROOT" PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
   export PLAN_ID='<ruled fresh night identity>'
   export NIGHT_ROOT='<ruled /Users/edr/night-custody/identity>'
   export T0_ISO='<T0: offset-aware ISO timestamp>'
   export WINDOW_MAX_S='<ruled positive integer seconds>'
   export TRACE=/Users/edr/code/JouleWise-wt-g2a-plan/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan
   export STAGED_PLAN="/Users/edr/night-plan-staging/$PLAN_ID/night_plan.json"
   export RENDER_ROOT="/Users/edr/night-plan-staging/$PLAN_ID/render"
   cd "$MEASUREMENT_ROOT"
   export NIGHT_DATE="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; t=datetime.fromisoformat(os.environ["T0_ISO"]); assert t.tzinfo is not None; print(t.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d"))')"
   ```

   Confirm no old record or symlink at `NIGHT_ROOT`, the date-derived probe
   root, or `STAGED_PLAN`. Create the fresh night root only after that review.
   Use `"$PY" -B -c 'import os; from pathlib import Path; Path(os.environ["NIGHT_ROOT"]).mkdir(parents=True)'`;
   it refuses an existing final directory rather than reusing it.
   Prepare probe inputs using R §2/G's exact `build-probes`, `bind-window`,
   and `check` recipe (five small and one large member per rung). Authentication
   must pass before any bracket reservation. Do not source the full chain for
   desk preparation: it collects.

4. Emit and syntax-check the exact chain into the fresh night root:

   ```sh
   "$PY" -B scripts/gen_g2_phase_d.py --check
   "$PY" -B scripts/gen_g2_phase_d.py --emit-chain "$NIGHT_ROOT/chain.zsh" --night-date "$NIGHT_DATE"
   /bin/zsh -n "$NIGHT_ROOT/chain.zsh"
   ```

   Publish canonical writer bytes **to staging**, retaining final custody
   paths in the plan. The following is the exact `write_night_plan` call;
   the in-memory validation does not itself write custody:

   ```sh
   "$PY" -B - <<'PY'
   import hashlib, os, runpy, subprocess, time
   from datetime import datetime, timezone
   from pathlib import Path
   from joulewise.night_gate import NightPlan, D166_REGISTRATION_SHA256
   from joulewise.night_plan_writer import write_night_plan
   trace = Path(os.environ['TRACE'])
   author = time.time()
   author_iso = datetime.fromtimestamp(author, timezone.utc).isoformat()
   subprocess.run([os.environ['PY'], '-B', str(trace/'validate_plan.py'),
       '--t0', os.environ['T0_ISO'], '--window-max-s', os.environ['WINDOW_MAX_S'],
       '--plan-id', os.environ['PLAN_ID'], '--custody-root', os.environ['NIGHT_ROOT'],
       '--authored-at', author_iso], check=True)
   resolver = runpy.run_path(str(trace/'validate_plan.py'))['resolve_draft']
   mapping = resolver(trace/'night_plan.draft.json', t0=os.environ['T0_ISO'],
       window_max_s=int(os.environ['WINDOW_MAX_S']), plan_id=os.environ['PLAN_ID'],
       custody_root=os.environ['NIGHT_ROOT'], authored_at=author_iso)
   mapping['authored_epoch_s'] = author
   plan = NightPlan.from_mapping(mapping)
   root = Path(plan.measurement_root).resolve(strict=True)
   assert str(root) == plan.measurement_root
   assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'], text=True).strip() == plan.repo_head == plan.measurement_head == os.environ['MEASUREMENT_HEAD']
   custody = Path(plan.custody_root).resolve(strict=True)
   assert str(custody) == plan.custody_root
   assert not (custody/'night').exists() and not (custody/'night').is_symlink()
   assert not (custody/'night_plan.json').exists() and not (custody/'night_plan.json').is_symlink()
   chain = Path(plan.chain_path)
   generator = runpy.run_path(str(root/'scripts/gen_g2_phase_d.py'))
   expected = generator['render_g2a_night_chain'](generator['RUNSHEET_PATH'].read_text(), os.environ['NIGHT_DATE']).encode()
   assert chain.read_bytes() == expected
   assert Path(plan.chain_sha256_path).read_text() == hashlib.sha256(expected).hexdigest() + '  chain.zsh\n'
   assert hashlib.sha256(Path(plan.registration_path).read_bytes()).hexdigest() == D166_REGISTRATION_SHA256
   staged = Path(os.environ['STAGED_PLAN'])
   assert not staged.exists() and not staged.is_symlink()
   print(write_night_plan(staged, plan))
   PY
   ```

5. Derive `NIGHT_HOUR` and `NIGHT_MINUTE` from the same T0 in the machine's
   verified America/Los_Angeles timezone. Render and inspect **both** plists
   from the pinned clone:

   ```sh
   export NIGHT_HOUR="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.fromisoformat(os.environ["T0_ISO"]).astimezone(ZoneInfo("America/Los_Angeles")).hour)')"
   export NIGHT_MINUTE="$("$PY" -B -c 'import os; from datetime import datetime; from zoneinfo import ZoneInfo; print(datetime.fromisoformat(os.environ["T0_ISO"]).astimezone(ZoneInfo("America/Los_Angeles")).minute)')"
   scripts/install_night_agent.sh --plan "$STAGED_PLAN" --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" --render-only "$RENDER_ROOT"
   /usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.plist"
   /usr/bin/plutil -lint "$RENDER_ROOT/com.joulewise.night.deadman.plist"
   ```

   Render-only creates `NIGHT_ROOT/night/`; this is an intentional arm-time
   write. It does not install. Verify actual driver/courier paths, local time,
   both head pins and no prior night records. The full preflight command is
   `bash docs/process_traces/2026-08-28-live-smoke/preflight.sh "$STAGED_PLAN"`;
   it invokes sudo authorization and MLX imports and its agent census will
   refuse an active magistrate. Run only in its permitted machine lane;
   distinguish that expected census refusal from other unresolved failures.
6. **Email, then arm:** send Ed the reviewed plan notice with ID, class,
   absolute root, full heads, local/UTC T0, duration, chain/digest, custody,
   courier deadline and cancellation instructions. Record actual delivery ID.
   Confirm no NO on that thread and no OTHER agent session immediately before
   publication. Then atomically move staging into watchdog-visible custody
   and install both agents from the clone:

   ```sh
   "$PY" -B - <<'PY'
   import os
   from pathlib import Path
   target = Path(os.environ['NIGHT_ROOT'])/'night_plan.json'
   assert not target.exists() and not target.is_symlink()
   os.replace(os.environ['STAGED_PLAN'], target)
   PY
   scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE"
   ```

   Review successful installation of both labels. A publication/install
   failure returns to the authorized handback recovery path; do not leave a
   discovered plan unattended or overwrite evidence. Preserve pin reachability.
   Exit all agent work by T0−25 minutes; watchdog TERM/KILL fences are
   T0−16/T0−15. Launchd alone starts acquisition. Never manually invoke
   `run_night.py run` as a test. Production census must be empty at launch and
   throughout the chain. Harvest successful chain completion and authenticated
   four-rung counts/summary before any G2-a selection or later pack work.

## Remaining prerequisites and owners

| Prerequisite | Owner and current evidence |
|---|---|
| Rule the open identity, custody, T0 and budget | Magistrate; still open, as above. |
| Harvest rehearsal, courier, dead-man and stand-down; retire all active stub roots/agents | Magistrate; not inspected in live custody by this task. Kernel `G2A-FIRST-WINDOW-01` retains hard dependency on accepted `NIGHT-REHEARSAL-01`. |
| Update handback, preserve approved pins, adjudicate successor head if required | Magistrate. Clone predates desk head: `run_night.py` at desk head additionally records process start identity in `chain.started`. Routing/schema/generator/preflight/runsheet bytes agree between these heads, but this does not certify all driver behavior. |
| Clean measurement tree | Magistrate with clone write authority. `joulewise.egg-info/` is untracked (five files listed in log). It does not prevent schema/routing validation or importing JouleWise, but **fails preflight's all-untracked clean-tree gate**. Preserve/resolve through the authorized environment workflow; no ignore/deletion workaround was applied. |
| Exact environment lock and model authentication | Magistrate. Lock comparison fails with extra `joulewise==0.1.0` despite `--exclude-editable`; all other normalized requirements match. Inspect editable-install metadata and use governed lock recipe; do not hand-wave away this mismatch or refresh packages unpinned. `.venv/pyvenv.cfg`/`--version` confirm 3.13.1 only. MLX/Metal import and runtime checks were not performed. |
| Model bytes/revisions | Magistrate; authenticate `configs/model_panels/qwen3_4bit.json`: Qwen3-1.7B `3b1b1768f8f8cf8351c712464f906e86c2b8269e`, Qwen3-8B `545dc4251c05440727734bcd94334791f6ab0192`, exact tokenizer/template pins and local sources `/Users/edr/jw_models/mlx-community/`. Panel pins are specified, live bytes unverified. |
| Physical ledger continuity and custody | Magistrate; clone loader with preflight's `verify_custody=False` reports `calibration_ledger_missing, calibration_ledger_rollback`. Provision authentic `runs/calibration_observation_ledger.jsonl` and custody against committed `configs/calibration/calibration_ledger_head.json`; never invent an empty ledger/reset a pin. Full custody authentication remains owed. |
| Probe inputs and non-colliding roots | Magistrate; build/bind/check four rungs with G recipe, panel, ledger/pin, `configs/campaign_policies/quiet_mac_p2_production.json`, `POWER_POLICY=ac_high_power`. Freeze inventory, calibration plan, identity epoch, T1 bindings and prompt ladder before arm. No probe generation or root creation was performed. G fixes `SETTLE_S=600` and D-079 screen bound `0.032898493715362`; retain both. |
| Noninteractive powermetrics privilege | Ed for missing sudoers/install authorization; governed check is `/usr/bin/sudo -n -l /usr/bin/powermetrics` (lists authorization, does not capture). Not executed here. No password prompt fallback at night. |
| Physical and privileged quiet-Mac preparation | Ed: AC/high-power, lid open, display/backlight state, sleep settings and any required privileged service action (including the recorded outstanding fseventsd restart if still applicable). Magistrate verifies current need/readiness in its authorized lane; this task neither probes nor changes machine state. |
| Clock, HID idle, thermal/load, empty production census, watchdog health | Magistrate's governed readiness/stand-down path and night driver. These remain live gates; dry success supplies none of them. |
| Real-class email and two-agent installation | Magistrate under H/D-171 after prerequisites; Ed's NO cancels. Verify courier executable and delivery, 300-second reporting budget and 07:00 dead-man. D-175 rehearsal success alone is insufficient. |

No production pack freeze, step-6 table or pack ARM receipt is needed for this
G2-a class. D-169 stage 3 remains required for G2-b/TRANSACTION_PACK and later
claim collection, not for this diagnostic plan's schema validation.

## Verification and limits

See `preflight.log` for exact argv/output and subprocess return codes.
The log exists in this directory but matches the repository's log ignore rule;
the lead must explicitly include this exact evidence file in any later commit.
`validate_plan.py` returns **0** with explicitly non-authorizing sample
inputs. It validates the actual clone's parser, registration, generator and
routing, including overriding an invalid inherited `PY`. Full generated
chain bytes are syntax-checked but never executed. Chain/sidecar existence,
fresh live custody, probe authentication, quietness and live readiness are
not claimed. The full preflight was not run because it has no no-sudo mode
and imports MLX, which may initialize Metal. The logged independent subset
uses the clone as its working directory so Python's current-directory import
cannot shadow the clone with the desk checkout.

Only trace tooling/documentation changed; focused positive and refusal checks
replace the canonical full suite for this task. No fixture or dry result is
measurement evidence. Lead owns final review, real gate verification, and
any later commit/merge; this session makes no commit.
