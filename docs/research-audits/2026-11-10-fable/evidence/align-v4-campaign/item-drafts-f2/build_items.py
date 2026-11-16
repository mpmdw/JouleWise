"""Render self-contained drafts; verify bands with the real pinned, read-only plan.

Usage: python3 -B build_items.py /path/to/detached/2d347f721
No measurement command, network, host query, or custody access occurs here.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
PIN = '2d347f721552fe03bdd19f113e7bad7a7c24908e'
SOURCE = '1f683fc634ed6b8722a3976af400920ee1f7dd7d'
SHA = '651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b'
KIT_PATH = 'docs/process/cadence/kits/f2-inst-01.v1.1.json'
QUEUE_PATH = 'docs/process/cadence/queues/f2-inst-01.v1.1.queue-a.json'
TZ = ZoneInfo('America/Los_Angeles')
DEFAULT, ALT = '02:00-02:35', '13:14-13:15'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=HERE).decode()

def epoch(day, hms):
    return int(dt.datetime.fromisoformat(f'2026-11-{day}T{hms}').replace(tzinfo=TZ).timestamp())

def render(pin_repo):
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=pin_repo).decode().strip() == PIN
    kit_bytes = subprocess.check_output(['git', 'show', f'{SOURCE}:{KIT_PATH}'], cwd=pin_repo)
    assert hashlib.sha256(kit_bytes).hexdigest() == SHA
    # This is a kit DATA copy, not measured data.
    (HERE / 'f2-inst-01.v1.1.json').write_bytes(kit_bytes)
    kit = json.loads(kit_bytes)
    (HERE / 'queue-a.json').write_text(git('show', f'{SOURCE}:{QUEUE_PATH}'))
    gates = (HERE / 'gates.sh').read_text()
    specs = [(1, 16, 'cl-dev-03', 'dev-03-s02', list(range(4, 13)), '19:56:17'),
             (2, 17, 'f2-inst-01', 'f2-inst-p1', [1, 2, 3], '16:45:12'),
             (3, 17, 'f2-inst-01', 'f2-inst-p2', [4, 5, 6], '19:09:14'),
             (4, 18, 'f2-inst-01', 'f2-inst-p3', [7, 8, 9], '16:45:12')]
    records = []
    for n, day, pred_camp, pred, pred_legs, forecast in specs:
        name = f'f2-p{n:02d}'; span = f'f2-inst-p{n}'
        ids = [f'L{i:03d}' for i in range(3*n-2, 3*n+1)]; legs = ','.join(ids)
        a, z = epoch(day, '00:00:00'), epoch(day, '23:59:59')
        bs = [(a, epoch(day, '02:34:59'), ALT),
              (epoch(day, '02:35:00'), epoch(day, '10:50:00'), DEFAULT),
              (epoch(day, '13:15:00'), epoch(day, '22:18:10'), DEFAULT),
              (epoch(day, '22:18:11'), z, ALT)]
        log = [f'pin {PIN}; kit sha256 {SHA}; {name}: {legs}',
               'Synthetic schedule; actual pinned plan CLI; no measurement/custody reads.',
               'expected_s 7442; worst_case_s 11250; launch reserve 560; fence reserve 1460']
        probes = {(t, arg) for lo, hi, arg in bs for t in (lo, hi)}
        for hms in ('02:34:59','02:35:00','09:32:10','09:32:11','10:50:00','10:50:01','13:14:59','13:15:00','22:13:10','22:18:10','22:18:11'):
            probes.update((epoch(day, hms), arg) for arg in (DEFAULT, ALT))
        for t, arg in sorted(probes):
            r = subprocess.run([sys.executable, '-B', 'scripts/cadence_legs_runner.py', 'plan',
                                '--kit', str(HERE / 'f2-inst-01.v1.1.json'), '--legs', legs,
                                '--t0', str(t), '--batch-window', arg], cwd=pin_repo, text=True, capture_output=True,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'JW_B5_SYNTHETIC_ONLY': '1'})
            sec = t - a
            want = (9300 <= sec <= 39000 or 47700 <= sec <= 80290) if arg == DEFAULT else (sec <= 34330 or sec >= 47700)
            assert (r.returncode == 0) == want, (t, arg, r.stdout, r.stderr)
            if want:
                p = json.loads(r.stdout)
                assert (p['expected_s'], p['worst_case_s'], p['blackout_clear']) == (7442,11250,True)
                assert p['runner_kind'] == 'cadence-legs-v1.1' and p['batch_windows'] == [arg]
                assert [x['leg_id'] for x in p['legs']] == ids
            log.append(f"PASS {dt.datetime.fromtimestamp(t,TZ).isoformat()} epoch {t} arg {arg}: rc {r.returncode}, expected {'admit' if want else 'refuse'}")
        (HERE / 'evidence' / f'verify-{name}.txt').write_text('\n'.join(log)+'\n')
        pick = ['pick_arg() {', '  n=$1']
        for i,(lo, hi, arg) in enumerate(bs):
            pick.append(f'  {"if" if i == 0 else "elif"} [ "$n" -ge {lo} ] && [ "$n" -le {hi} ]; then echo {arg}')
        pick += ['  else echo NONE; fi', '}']
        pred_sha = '0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b' if n == 1 else SHA
        cfg = f'PIECE={n}; SPAN={span}; LEGS={legs}; PRED_CAMP={pred_camp}; PRED_SPAN={pred}; PRED_KIT_SHA={pred_sha}; PRED_ROSTER='+','.join(f'L{i:03d}' for i in pred_legs)+'\n'
        dates = dt.date(2026,11,day).strftime('%a %d Nov')
        row = ', '.join(f"{x['leg_id']} {x['prefill_tokens']:,} tokens" for x in kit['legs'] if x['leg_id'] in ids)
        queue_note = ('The committed queue a at `1f683fc6` contains this piece only.' if n == 1 else
                      'Queue b is intentionally absent until the lead records piece 1\'s PASS hand-read. The lead commits a new `cq-f2-inst-01-b` queue containing pieces 2–4 in kit order, expiry `2026-11-21T21:29:00-08:00`, and fills QUEUE_FILE and QUEUE_SHA below. Do not issue or stage this item before that commit.')
        queue_vars = ('QUEUE_FILE=/Users/edr/campaign-out/queues/f2-inst-01.v1.1.queue-a.json\nQUEUE_SHA=ca61c3bc09d8a594a60ec058b86d378012a165b44334f4309b4cd7546e842892' if n == 1 else ': "${QUEUE_FILE:?staged committed queue-b path}"; : "${QUEUE_SHA:?lead-committed queue-b sha256}"')
        heading = f'''TBD. **Laptop lead, drafted by Sol 6.1; ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): MAGISTRATE: arm F2 instrument-characterization piece {n} only, span `{span}`, kit `f2-inst-01.v1.1` (sha256 `{SHA}`), runner `cadence-legs-v1.1`, detached pin `{PIN}`. Roster {legs}: {row}; own-shaped G0, q600, decode cap 512, Automatic. Fresh soak, then three legs; expected 7,442 s, worst case 11,250 s. These are instrument legs, outside every campaign count and look. Predecessor `{pred}` must have a clean close receipt or this item is VOID and never skipped. EARLIEST {dates} 2026 00:00:00 PST ({a}); LIMIT {dates} 23:59:59 PST ({z}), shortened by 24 h after issue. F2 is a filler: it cedes to all armable counted work and a READY v4 session; use the complete priority trigger below. Launch is the last action; exit immediately. Nothing else is authorized.**

```pointer
owner: magistrate
wait: none
deadline: {dt.datetime.fromtimestamp(z+12710+3600,TZ).isoformat()}
on_early_or_refused: WAIT if predecessor has not closed or a higher rung can arm; VOID if predecessor is not clean, the date window is missed, or 24 h has elapsed since issue. No retry after a launcher/runner refusal; report to the lead. Never skip a predecessor, reuse OUT, re-run a leg, or queue another piece on this item's authority
next_observable: after the fence is gone, Check below reports operational receipt/leg records, feeds, restore and copy; piece 1's hand-read is lead-owned
```

- **Admission and authority (RL-169; RL-169a).** Data only; frozen pin and all 38 path hashes unchanged. {queue_note} Require the independent executing re-check, dev-03's first span closed on this same pin with all restore lines passed, line 2 carried from the dev-03 item by frozen-path equality (RL-165 §5), every applicable checklist line, watcher line 7 and campaign line-9 debt. F2 neither adds to nor pays down line 9. Record the evidence for each `*_OK` value below; a yes without its evidence is not authority. STATUS.md lists unfilled prerequisites. Nothing is issued across a class A, L002 or L005 hand gate (RL-173 D.4).
- **Issued ahead (RL-173 D).** Own predecessor `{pred}`, own date and own `pick_arg`; expires 24 h after ISSUED_EPOCH, checked twice. At most three counted spans ahead plus standing F0. No F2 item grants standing authority or authority to issue another item. Pieces 2–4 are not issuable before the piece-1 hand gate and queue-b commit.
- **Exact ladder.** READY v4 session takes the next clean close from the lead's READY record (RL-172 (f); no reservation at a merely intended session t0). Preserve the applicable counted development order: dev-03 pilot/remainder and dev-04/dev-05 dated spans are never displaced. The Monday ladder after dev-02 is READY slot session, dev-03 pilot, hp-01's unrun spans, P, F0; RL-169 appends F2 after F0, then DESIGN_QUEUE_LOW. F2 is eligible only when no counted item can arm within its worst case and ensuing close, hp-01 and P cannot arm, and F0 is ineligible under its own spacing, daily-cap or launch-window rule. `priority_gate` encodes that trigger and blocks unknown state, unresolved refusal, open F2 stop, or pending host-event disposition. Re-read all current issued/staged counted items and READY counted work awaiting staging twice; set NEXT_COUNTED_EPOCH to the earliest legal arm including the next day's spans. Do not omit a known item merely because staging is pending. Unknown gate readiness stops the arm. An explicit 0 requires a recorded complete empty census. This conservative check protects 13,010 s: 11,250 work + 560 launcher/runner reserve + 1,200 close; it also clears the 12,710 s fence. A new READY record before launch cedes immediately. Nothing aborts an already running span.
- **Day law.** F2 is outside development/day/cap counts (RL-172 (a)). This item's date is a bounded scheduling choice, not a new development date; a missed window needs a newly dated item from the lead. No shortening/re-cutting of the admitted four-piece layout is needed for the forecast gaps.
- **Bands verified at the pin:** 00:00:00–02:34:59 alternate `13:14-13:15`; 02:35:00–10:50:00 default `02:00-02:35`; 10:50:01–13:14:59 no launch; 13:15:00–22:18:10 default; 22:18:11–23:59:59 alternate. RL-171 retires RL-169a's 22:13:10/02:40 clock rules. The pin admits exactly 10:50:00; both arguments refuse one second later. `evidence/verify-{name}.txt` checks endpoints and adjacent seconds, including the alternate's 09:32:10/09:32:11 limit. All validate-kit, plan and launch commands name the same argument and explicit roster.
- **Close and copy.** 300 s after a campaign span close; **1,200 s after F2, F0 or any other close**, from the actual close with fence gone (RL-171 §6.1; RL-172 (d)). The latest close census rounds fractional mtimes up and stops on missing roots, errors, ambiguity or no receipt. Latest-close restore and process-group absence are proven. Copy marker is the MBP's verified encrypted cloud offload `.ok` or the Air's verified `.air.ok` for that plan; a failed/unverified offload holds every next arm, F0 included (RL-173 A). The writer guarantees plaintext manifest hash, ciphertext hash/size and provider confirmation, upload finished before soak; the key is safe off the MBP and originals retained. This item never manufactures a marker. For an out-of-census session supply OTHER_CLOSE_EPOCH and its OTHER_COPY_PLAN_ID. A mere `.ok` existence is trusted only because the authorized writer writes it after verification, as in the dev-03 pilot.
- **Quiet and host event.** Quiet is agent/process census and rule 5, not the retired night clock. No MBP agent, SSH, analysis, build or test during a span. Same measurement_mode, Automatic, network time OFF, frequency word 0, no night/smoke job, monitor, High Power marker, lock holder or desk fence. RL-172 (h), amended by RL-173: no password/physical step by an agent; service-stop readback or restart disposition is lead-owned, last point before freeze 2. Each arm prints boot + 12 h + 48 s batch time, a print only.
- **Blinding.** F2 measures only its own instrument streams. Neither this magistrate item nor its tests read campaign/v4 energy, power, meter samples, powermetrics, transcripts, slots or custody. F2's own energy is sealed until freeze 2; only the single analyst using frozen `lm-inst-01` may read it once. The operational Check reads only receipts, leg records and leg-summary projections. Recovery beyond the rails' 1 s tail is censored per RL-169a; no F2 number enters a fit, coefficient, threshold or score.
- **Stops.** Any F2 REFUSAL, INSTRUMENT_FAULT, CONTAMINATED_REDOS (three loaded legs) or LEG_OVERTIME (two above 1.5× budget) stops its queue; an open cadence-stop holds every queue. A G0 timeout alone, or one/two loaded legs, is recorded. No running span is aborted. Only the lead disposes a stop under RL-169a §4, with a new queue for unrun pieces; no member-bearing leg is repeated and unbundled legs of a stopped piece are dropped. Second stops go to the research lead. Restore unproven holds everything. A failed piece-1 hand-read leaves queue b uncommitted.

**Start and check** (on the MBP only after issue, by the magistrate; the builder never executes these blocks).

The lead stages `stage_mbp_span.sh {span}` in a clean close interval and supplies the arm-record observations used below. Stage and reuse one detached v1.1 worktree only; never stage the v1.1a variant. `QUEUE_FILE` is the staged queue path and `QUEUE_SHA` its committed hash. For piece 1 use queue-a's committed bytes; for later pieces use the lead's post-hand-read queue b. The watcher placeholders below are exactly the dev-03 pilot's. This item uses the hand-stamped watcher observation of RL-173 C.5, re-read at every arm; an API watcher would instead require C.4's completed run newer than the previous close.

```sh
set -eu
set -o pipefail
cd /Users/edr/code/jw-wt/cadence-{span}
PIN={PIN}
test "$(git rev-parse HEAD)" = "$PIN" && test -z "$(git status --porcelain)" || exit 1
git symbolic-ref -q HEAD >/dev/null && exit 1
REPO="$PWD"
: "${{PY:?existing pinned measurement-venv interpreter}}"
: "${{MAGISTRATE_PID:?this magistrate own process PID}}"
KIT=/Users/edr/campaign-out/kits/f2-inst-01.v1.1-{SOURCE[:9]}.json
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = {SHA} || exit 1
{queue_vars}
test "$(shasum -a 256 "$QUEUE_FILE" | cut -c1-64)" = "$QUEUE_SHA" || exit 1
{cfg}{chr(10).join(pick)}
{gates}
ARG="$(pick_arg "$(date +%s)")"; export ARG
all_gates || exit 1
CUSTODY="${{MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}}"
test ! -e "$CUSTODY/desk_fence.json" || exit 1
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
test ! -L /Users/Shared/JouleWise/host-power/high-power.marker || exit 1
sudo -n -l /bin/kill >/dev/null || exit 1
sudo -n systemsetup -getusingnetworktime  # Off
pmset -g | grep -i powermode             # 0; frequency word 0, AC power checked by checklist
MODE_VERIFY_RC=0
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify || MODE_VERIFY_RC=$?
echo "measurement_mode verify rc $MODE_VERIFY_RC"
# Only own-process-tree agent FAIL lines may be present, as dev-03's arm record; any other FAIL stops.
# Inspect the exit status and lines; CHECKLIST_OK=yes is set only with every applicable line proven.
"$PY" -B scripts/cadence_queue.py validate-kit "$KIT" --repo "$REPO" --batch-window "$ARG" || exit 1
# validate-queue during staging uses the kit at its committed relative path in a temporary kits-root.
# Here compare the staged committed queue hash/roster: never run `next` or `checklist` to grant authority.
"$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs {legs} --batch-window "$ARG" || exit 1
# expected_s 7442, worst_case_s 11250, blackout_clear true, batch_windows [ARG]. Record complete output.
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\\{{ sec = ([0-9]+),.*$/\\1/')"
case "$BOOT" in ''|*[!0-9]*) echo 'batch print: boot unreadable';; *) NEXT_BATCH=$((BOOT+43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH+86400)); done; echo "next OS batch epoch $NEXT_BATCH";; esac
OUT=/Users/edr/campaign-out/f2-inst-01/cq-${{SPAN}}-a1-$(date -u '+%Y%m%dT%H%M%SZ')
test ! -e "$OUT" || exit 1
```

**Run.** Re-read the issued/staged counted items, NEXT_COUNTED_EPOCH, v4 READY record, hp-01/P/F0 eligibility, all stop/restore records, copy marker and the watcher observation now. Update the observations; do not reuse a cached eligibility answer. A prior date's expired item is never counted as armable. Run once, then exit immediately.

```sh
all_gates || exit 1
test ! -e "$CUSTODY/desk_fence.json" || exit 1
# The pinned launcher rechecks host/checklist state, condition-13 and its process census under its lock.
DEADLINE="$("$PY" -I -B -c 'import time; print(time.time()+12710)')"
"$PY" -B scripts/launch_cadence_span.py launch \\
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs {legs} --batch-window "$ARG" \\
  --output "$OUT" --disk-path "$REPO" --custody-root "$CUSTODY" \\
  --magistrate-pid "$MAGISTRATE_PID" --deadline "$DEADLINE" \\
  --exit-wait-seconds 180 --start-wait-seconds 30
echo "$OUT"
```

**Check.** Only on the next activation, after the shared fence is gone. Read no stream, member output, feed file or custody content. This operational print is not the analyst read and never prints measured power/energy. All queue stops are judged by the pinned desk's operational projection and the lead; nothing is automatically re-armed.

```sh
"$PY" -I -B - "$OUT" "$LEGS" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); roster = sys.argv[2].split(',')
r = json.loads((root/'runner_receipt.json').read_text())
assert r['roster'] == roster and r['runner_kind'] == 'cadence-legs-v1.1'
assert r['kit']['sha256'] == '{SHA}' and r['kit']['frozen_commit'] == '{PIN}'
assert r['kit']['campaign_id'] == 'f2-inst-01' and r.get('mock') in (False,None)
print({{k:r.get(k) for k in ('rc','error','legs_planned','legs_finished','span_result','ended','batch_windows')}})
print('steps', [(x['name'],x['rc']) for x in r['steps']])
print('feed stops', {{k:v.get('stop') for k,v in r['feeds'].items()}})
print('meter operational', r.get('meter'))
assert r.get('feeds') and all(f.get('stop',{{}}).get('proven_stopped') is True for f in r['feeds'].values())
assert any(s['name']=='restore' for s in r['steps'])
assert all(s['rc']==0 for s in r['steps'] if s['name']=='restore' or s['name'].startswith(('stop-','close-')))
for leg in roster:
    rec = json.loads((root/'legs'/leg/'leg_record.json').read_text())
    result = rec.get('result') or {{}}
    keys = ('leg_status','g0_outcome','g0_wait_s','quiet_spans_ns','decode_tokens','decode_cap_reached','prefill_tokens')
    print(leg, {{k:result.get(k) for k in keys}}, 'attempt walls', [a.get('wall_s') for a in rec.get('attempts',[])])
    summary = json.loads((root/'desk-bundle'/'legs'/leg/'leg_summary.json').read_text())
    print(leg, {{k:summary.get(k) for k in ('wall_s','budget_s','contaminated_redos','admitted','g0_outcome')}})
print('RECEIPT OK' if r['rc']==0 and r['legs_finished']==3 else 'NOT CLEAN: report to lead; no retry')
PY
zsh /Users/Shared/JouleWise/measurement-mode/measurement_mode.zsh verify
sudo -n systemsetup -getusingnetworktime   # Off
pmset -g | grep -i powermode               # 0; report frequency word 0 and process-group absence
```

Report receipt/desk lines, named stops, actual close/fence-gone epochs, every restore line, feed-stop proof, copy/offload status, watcher observation, and the host-mode readback. Never hash/open stream files as an agent. The lead's deterministic desk uses `{PIN}` and the leg-summary projection only. The lead records Check and the verified copy before any next soak. No commit from OUT.

**After (lead).** Piece 1's hand-read uses only leg_record and runner_receipt: every leg complete or g0_unreleased, at least two complete; each complete leg has a quiet span ≥600 s and reached 512; meter present/clean, all feeds stopped and restore passed. Record each wall against 2,700 s and the 256-token leg's realized prefill. Keep and flag any short decode; a short 256 leg goes to the research lead before queue b. Only a PASS permits the lead to commit queue b and issue pieces 2–4. This item cannot cross that gate. Later pieces run once in order under their own issued items; after piece 4 F2 leaves the ladder. An issue after 24 h or a missed date needs a new item. No early energy read; `lm-inst-01` and its cold pass gate only the later analyst read, not these runs.
'''
        (HERE / f'ITEM-{name}.md').write_text(heading)
        records.append(dict(item=name, span=span, piece=n, date=f'2026-11-{day}', legs=ids,
                            predecessor=pred, predecessor_camp=pred_camp,
                            predecessor_legs=[f'L{i:03d}' for i in pred_legs],
                            bands=bs, forecast_epoch=epoch(day,forecast)))
    (HERE/'items.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Rendered four items; all pinned plan probes passed')

if __name__ == '__main__': render(Path(sys.argv[1]))
