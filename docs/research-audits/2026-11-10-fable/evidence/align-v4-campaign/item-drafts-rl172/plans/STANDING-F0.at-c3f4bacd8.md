TBD. **Laptop lead (interactive, Opus 5.5), drafted by the items-rl165 drafter 2026-11-14 PST and re-drafted under RL-171 by the items-rl171 builder 2026-11-15 PST, ISSUED <LEAD FILLS: YYYY-MM-DD HH:MM:SS PST from `date`> (`date`): STANDING ITEM (RL-165 §3). MAGISTRATE: you may run filler F0, the Part C bridge, ON YOUR OWN, without a further item from the lead, whenever one of the three triggers below holds and every rule below holds: a FRESH TV0h/TV1h idle soak, then Part C only (`--fresh-soak --parts C`: the 30B predecessor, a full step-D on TV1h, the gated D_bank member seed 1, then X_G) on `c3f4bacd8013ca98c19cf8d41f830c701930cd41` (the merge of PR #783, head of `ops/2026-11-11-w1-presign`), in the staged worktree `/Users/edr/code/jw-wt/partc-c3f4`. Each run is a DIAGNOSTIC, journals only: it adopts nothing, enters nothing and produces no slots. ONE run per activation, with its own OUT. No prepare, no arm, no session, no W1, no other smoke. The launch is your LAST action and you exit at once. The item stays live after each run. It is VOID as soon as the W1-line head is not `c3f4bacd8` (the lead re-issues it with that merge), and it EXPIRES at <LEAD FILLS: issue time + 7 days, as a PST time and its epoch>. If any rule fails, do not launch; mail the lead.**

```pointer
owner: magistrate
wait: none
deadline: <LEAD FILLS: the expiry time, RFC 3339 with -08:00>
on_early_or_refused: any failed line of "Start and check", a void or expired item, a launch refusal (rc≠0 or no claimed fence), or a launch that cannot meet rules 5 to 7 (rule 6 is now the c3f4bacd8 launch window 02:35:00-22:40:00, RL-171): NOTHING launches; mail the lead. Do not retry, do not extend, do not reuse OUT. A launcher refusal at c3f4bacd8 is recorded and goes to the research lead (RL-164 §2(c)). A completed run, whatever its verdict (receipt rc 0 or 1 with an `evaluation` in smoke_part_c.json), is NOT a refusal: it is reported and compared line by line with the previous Part C's verdict (rule 10). A running F0 is never aborted (rule 9)
next_observable: the next activation after each run's fence is gone runs "Check" below and reports, by email to Ed and the lead, as the next RUN_STATE item and as one line on the standing notice: receipt rc, parts, soak rc and sha256, part-C rc; from smoke_part_c.json ONLY the evaluation, N_chunk and T_dead; the restore lines; the trigger that launched it
```

- **What this item is (RL-165 §3; RL-155a §2 row F0; RL-164 §5).** The filler ladder's F0 row, made self-executing. One RUN_STATE item, issued once, which you launch without the lead under the ten rules below. It needs no item per run. It does not change F0's design: the same Part C kit as items 319 and 325, at the commit item 325 runs. **F0's cap is not raised:** at most three a day, t0 at least 4 h apart (RL-165 §3, closing line).
- **Not a campaign span.** It does not count for RL-149 §2.8 line 9 (RL-155 §3.4; RL-165 §6). v4 sessions take the machine first (RL-155 R-A; rule 3 below).

**The ten rules (RL-165 §3; record each at every launch):**
1. **Pin.** The full sha `c3f4bacd8013ca98c19cf8d41f830c701930cd41`, the 17-hash table below, the Mac-check line below and the staged worktree `/Users/edr/code/jw-wt/partc-c3f4` (item 325's smoke worktree; created by the script if absent). The lead checked these once, for item 325: the Air tests at `c3f4bacd8` (`/Volumes/JW-EXT/scratch/partc2-c3f4/tests/`, six modules OK) and the 17 hashes, which equal Mythos's independent table (`/Volumes/JW-EXT/scratch/mythos-schedule-review/partc-paths-at-c3f4bacd8.txt`). No new Air check is made for this item.
2. **Void and expiry.** The item is VOID when the W1-line head (`origin/ops/2026-11-11-w1-presign`) is not `c3f4bacd8`. The lead re-issues it as part of that merge (for example PR #774's: RL-165 §9 lets a pass carry to #774's merge commit, but this item names a sha, so it is re-issued there). It EXPIRES 7 days after issue. A void or expired item launches nothing: mail the lead.
3. **When (the triggers; exactly one is recorded).**
   - (a) **REFUSAL:** a slot's arm refused (a failed "Start and check" line or a launcher refusal of a staged campaign span or session).
   - (b) **NOT_READY:** a slot's block is not READY at its earliest t0 (its item is not issued and staged, or one of its gate lines does not hold).
   - (c) **NO_STAGED:** a close leaves no staged item whose gate can hold within 2 h 30 min of that close (for example Sunday afternoon after the dev-02 pull: dev-02's second half, `dev-02-s03`, is the Monday span of the 6 + 6 split, so it cannot arm before Mon 00:00:00).
   - **Order (RL-165 §1, §2, §4).** F0 is the last rung. Sunday after `dev-01-s04`: the R1 slot session if READY, then hp-01's spans, then the dev-02 pull, then F0. Monday after dev-02 closes: the slot session if READY, then the dev-03 pilot, then hp-01's unrun spans, then P, then F0. After either G0-timeout contingency: the slot session if READY, hp-01's unrun spans, then F0. Do not use F0 to pass over a staged item that can launch now.
   - **R-A (RL-172 (f), which retires RL-165 §7's worst-case reservation).** From the lead's record that a v4 session is READY, nothing of lower priority arms, F0 included; the session takes the next clean close. Before that record F0 arms on its own rules.
4. **After a refusal (trigger a).** Mail the lead at once (suggested: "F0 STANDING: <span> refused at <time>: <reason>; F0 launches at <time + 20 min> unless you reply that you are clearing it"), record the send epoch, and wait 20 minutes. With no clearing reply, launch. **Any reply that unambiguously says the lead is clearing (or will clear) the stop counts, in any words** (Sol items review P1-5; RL-165 §3 rule 4); a subject or first line starting `CLEARING` is only a suggested format. A reply that is not clear either way: do not launch in this activation, and mail the lead once to ask. If the lead is clearing, do not launch: wait for the refused span's re-arm instead, and F0 waits for its next trigger. **An outstanding refusal takes precedence over every other trigger** (Sol items review P1-4): from the refusal until either this rule's 20-minute wait has passed with no clearing reply (F0 then launches under trigger (a)) or the refused span re-arms or the lead releases it, F0 may not launch under trigger (b) or (c), even if the same failed gate would also read as NOT_READY. Record OUTSTANDING_REFUSAL as the span until then, and none after.
5. **Spacing.** t0 at least 14,400 s after the last F0's t0 (any Part C run counts: items 319 and 325 and every run under this item), and at most three F0 t0s in one local calendar day. The ledger below carries the t0s.
6. **Launch window: 02:35:00 to 22:40:00 local (RL-171 §2 and §3; RL-156 §5's 22:40 restored).** RL-171 retires "launch + 12,180 s by 01:30" (RL-164 §5) and "no F0 between 01:30 and 02:40". What is left is what the bytes at `c3f4bacd8` do: `soak_child` refuses a soak whose start lies in (22:50:40, 02:35:00), because the soak plus Part C's cap (11,360 s) would meet 02:00-02:35 (run on the Air at `c3f4bacd8`: soak start 22:50:40 admitted, 22:50:41 refused, 02:34:59 refused, 02:35:00 admitted; `/Volumes/JW-EXT/scratch/items-rl171/probe/c3f4-soak-child-boundary.txt`). So the launch is at or after 02:35:00 and at or before 22:40:00 (ten minutes of preflight before the latest soak start). RL-171 §4 keeps this refusal until the slot session has run. A run that crosses 00:00 is recorded, not a gate.
7. **It never costs a counted span its day.** Launch + 12,180 s + 1,200 s is at or before the latest legal t0 of every staged counted span due that calendar day (each staged item states its latest legal t0; take the end of its last window). Under RL-171 a counted span's latest legal t0 is the end of its item's window (the calendar day for the dev-02 halves). Example: with the Sunday dev-02 pull staged and not yet run (window to Sun 23:59:59), an F0 may launch only by 20:16:59 (23:59:59 - 12,180 s - 1,200 s); a staged span inside the 10:50-13:15 band of its pin cannot arm there, so it does not bind rule 7 there.
8. **Host state and the restart (RL-172 (h)).** The MBP restarts once at 14:08 (± 15 min) on the first day no span is armed then (Sunday if dev-02's first half has closed): **no F0 arms after 12:00 that day until the lead records the restart done** (RESTART_PENDING). The lead's journal-copy marker is required after a campaign close, as for the campaign items (Sol items-rl171 P1). **Host state.** Every restore line of the latest close of anything on this host passed (its Check is reported), and no leg child's process group is unproven (RL-157 §2 condition 2). **"Restore unproven" (RESTORE_UNPROVEN) and any host-state stop (a change to host state outside `measurement_mode`, RL-149 §2.4) hold F0.** Other campaign stops (REFUSAL, disk, watcher down, INSTRUMENT_FAULT, CONTAMINATED_REDOS, LEG_OVERTIME, a frozen-kit-path change, a High Power `revoked` entry) do not hold it (RL-155 §3.1). A High Power marker present holds it (see Conditions).
9. **A running F0 is never aborted.** A span that the lead clears while F0 runs arms after F0's close + 20 minutes. RL-155 §4 rule 1's 30 minutes does not apply to an F0 begun under trigger (a), (b) or (c).
10. **After it.** One line on the standing notice (<LEAD FILLS: where the standing notice lives>), and the verdict line by mail to Ed and the lead. Journals only; nothing is adopted. The lead reads each verdict under RL-164 §3 against the previous Part C's. A line whose verdict differs from the previous run's goes to the research lead with both runs; this item stays live meanwhile.

- **Why F0 at this commit (RL-149 §5; RL-155a §2; RL-156 §4.1).** One more step-D leg and D_bank run on a new start and hour: G0 times by hour of day, onset, the first G1 after a hot turn if one occurs. Journals only. Its energy is not read under any look unless the research lead rules so (RL-149 §5 bridge; RL-155 §4 rule 5). Item 325's run at this commit is the counted pass that RL-149 §5 item 12 reads if it passes; runs under this item are F0 diagnostics and are compared with it.
- **Smoke commit `c3f4bacd8013ca98c19cf8d41f830c701930cd41`** (`origin/ops/2026-11-11-w1-presign`; merge of PR #783 head `0ec600128cb5e5040fe0dad2d30e4a10a38eae67` into `f30a97d00`). Its tree equals #783's head (`git diff 0ec600128 c3f4bacd8` is empty). It contains `f30a97d00` (PR #777's merge), `f006b7aa6` and `a6a09e6d7`. The commit, bytes, launcher CLI, runner spec and plist (`ProcessType Interactive`, `ExitTimeOut 400`) are exactly item 325's.
- **Condition-13 paths at `c3f4bacd8`** (`v4_registration.R1_EXECUTED_SOURCES`, the ten paths), and **Part C's executed paths** (seven). The 17 hashes, as in item 325:

| Path | sha256 at `c3f4bacd8` |
|---|---|
| `scripts/align_r1_rehearsal.py` | `2806f9eae61210d457ae19a5484cfe7dc7ac70a31c20b1ca0a2856f32178a825` |
| `scripts/align_r1_runtime.py` | `7403e69d9aedb54887bfc4218a45db84faa653329ca977bcf97edf20af88f923` |
| `joulewise/align/apple/r1_runtime.py` | `a5ba3cd4dce1b41c8448e2e26653789a9f607ffc2836a7b4a9339b991f9b6dac` |
| `joulewise/align/apple/r1_runtime_contract.py` | `4b9d1c69b0459a0382dfdd5e3aee56366e99f770ed2320cfff90539647ab6591` |
| `joulewise/align/apple/smc_enumeration.py` | `0132579cc33f8a997cdfd5f3dd84466352cdeeeebf9ca7de8dc1ec7990cea0a9` |
| `joulewise/align/apple/thermal_gates.py` | `c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d` |
| `configs/align/v4/r1_runtime.json` | `272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46` |
| `joulewise/align/apple/r1_phase_table.py` | `ffd6c025f4691771ea348f5d0f670c8f4bbfcb61afe67b83831afdd6c3d6f1ea` |
| `joulewise/align/apple/workload.py` | `837b74be97616c48c26b0c1277fe2a605b575d5cfc4396dc05e1139079daf1ba` |
| `joulewise/align/apple/thermal.py` | `b9b46f9ede50b265c245dcc05d3503139632ae129e313675622fa1dce25d39d7` |
| `scripts/launch_align_r0.py` | `242cd7aa0bf5788786ca8630e6931abcaaa3e01dc3bf014255a6191b50c6e799` |
| `scripts/run_align_r0_launchagent.sh` | `ac1dc2a223754cfc3295dd1352a838a3077671da140ffeeba484400e1bd249c6` |
| `scripts/run_align_r1_smoke.py` | `6f1fb9f4ac3109650b36b07012e24728c17e7112e7b59953e6557f2b5fdd35aa` |
| `scripts/align_r1_followup_kit.py` | `39dd7946e899058987038130b9c133298283a80ae3db4dceee79daad3c8e08b8` |
| `scripts/align_r1_part_c.py` | `b2c91c77ef9f1c227c5c172690fadf5f36cff22b4874d0eeaa66798ca9ef12b8` |
| `joulewise/align/apple/rl145_prints.py` | `b605195f9a23226a702376d9fbdb2e451546d6c3187297c39bd5b88e2e78f167` |
| `joulewise/align/apple/v4_registration.py` | `6815d1b65fee6bc67743a8905a3e61dcc8f5294b62fdd238938ca1e77b16ef57` |

  `verify_r1_executed_sources` at `c3f4bacd8` returns the full sha. The RL-89 Mac check prints `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46`.
- **What counts as completed (a diagnostic: there is no PASS bar).** As item 325: parts `{"C": true}`, `parts_requested` `"C"`, `fresh_soak` true, soak rc 0, one `close-volumes`, every feed proven stopped and hash-checked; `smoke_part_c.json` carries an `evaluation`; receipt rc 0 (verdict `pass`) or 1 (any other verdict). Anything else is reported in full and goes to the lead and the research lead. Nothing is re-run under this item except by a new trigger.
- **Conditions (RL-145 close §8, §12; RL-155 §3.1, §4).**
  - No agent session on the MBP during the run: you exit at once after the launch, and no other `claude` or `codex` process is running. No lead SSH, desk job, campaign span or R12 process until the fence is gone.
  - **Never while anything is armed** (RL-155 §4 rule 1): no desk fence, no `com.joulewise.(night|align-r0)` job, no `cadence_legs_runner` or `launch_cadence_span` process.
  - **The close interval (RL-171 §6.1, amending RL-155 R-B's 20 minutes)** after the latest close of anything on this host (span, Part C or F0, slot session, W1): every restore line of that close passed and its Check (with the hash-verified journal copy) is reported, and at least GAP seconds have passed. GAP is QUIET_CAMPAIGN_S when the latest close was a campaign span (300 s, confirmed by RL-172 §0), and 1,200 s after a Part C or F0, F2, a slot session or W1. The close is read from the newest `runner_receipt.json` under `/Users/edr/campaign-out` and `/Users/edr/code/jw-wt`, from a census that stops on a missing root, any lookup error or an empty result, with fractional mtimes rounded up; or OTHER_CLOSE_EPOCH for a session's close, which is required (a whole epoch or an explicit 0; unset or empty stops).
  - **The complete eligibility check runs twice:** in "Start and check" and again as the first step of "Run", on state re-read at that moment (the current clock, the current W1-line head, the expiry, the refusal and reply state, the staged items' window ends, the session READY record, LAST_CLOSE_KIND, the restart hold). The launch follows it with nothing in between but the deadline.
  - The usual restore before the launch and again in "Check": AC with powermode 0; network time OFF; the kernel frequency word at 0 (item 251's remedy if not); no stray `km003c_monitor.py`, `hazard_monitor.py` or root `powermetrics`; no High Power marker; `night.lock` with no holder (an hp-01 span holds it while it runs). `sudo -n -l /bin/kill` rc 0. Leave `night.lock` as found.
  - **High Power marker:** if `/Users/Shared/JouleWise/host-power/high-power.marker` exists, STOP and report. Never run `restore-owed` under this item.
  - The five kit tests that hard-coded TVh0 are not requested (as item 325).
  - **Blinding.** From `smoke_part_c.json` print ONLY `evaluation`, N_chunk and T_dead, with the "Check" script below. Never `cat`, `grep`, `jq` or Read `smoke_part_c.json` or `smoke.json`. Open no member bundle, transcript, energy, power or meter file, and no campaign OUT beyond the `stat` of its receipt.
- **Timing.** Part C's cap 9,560 s; the launcher's minimum for `--fresh-soak --parts C` is **12,180 s (3 h 23 min), the worst case**. Expected about 2 h (item 322's run: 7,134 s). The fence deadline is launch + 14,400 s (the 01:30 cap is retired with RL-164 §5's rule, RL-171 §2). At this commit the soak child refuses a soak start whose soak + Part C span (11,360 s) would meet 02:00-02:35: that is rule 6's window, 02:35:00-22:40:00. There is no 10:50-13:15 bound on this commit (its `OS_BATCH_WINDOW_LOCAL` is 02:00-02:35, so it has no midday soak wait): F0 is the one rung that fills 10:50-13:15 while the campaign pins `b4b6aeb19`, `dd206025a` and `2d347f721` cannot launch there. A run across 00:00 is recorded (the `/private/tmp` walk), not a gate.

**The ledger.** `$CUSTODY/standing-f0/ledger.tsv`, one line per Part C run: `t0_epoch<TAB>source<TAB>OUT`. On first use, create it with item 319's t0 (`1794703426`, Sat 16:43:46) and, if item 325 launched, its t0 from `$CUSTODY/r1-partc2-c3f4-out-*.txt`. Append one line at each launch under this item. Never edit a line.

**Start and check (while you are still alive).** From the staged worktree, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B`. The six dry-check modules of item 325 (`tests.align.test_rl145_gate_hashes`, `test_rl145_part_c`, `test_pr777_attack_repros`, `test_r1_smoke_launcher`, `test_v4_registration`, `tests.hazards.test_refusal_allowlist`, one module at a time, from a scratch worktree detached at the full sha) run ONCE on this host at this sha: skip them if item 325's Start and check recorded all six OK, or if `$CUSTODY/standing-f0/tests-ok-c3f4bacd8` exists; otherwise run them and, if all are OK, write that file. Any failure: nothing launches; mail the lead. Everything in the script below runs at every launch.

```sh
git -C /Users/edr/code/JouleWise fetch origin ops/2026-11-11-w1-presign
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
LEDGER="$CUSTODY/standing-f0/ledger.tsv"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter (do not resolve the symlink)}"
: "${MAGISTRATE_PID:?Set to the PID of this magistrate own claude process}"
ps -o pid=,comm= -p "$MAGISTRATE_PID"     # must show the claude process, not a tool shell

EXPIRY_EPOCH=<LEAD FILLS: EXPIRY_EPOCH>
QUIET_CAMPAIGN_S=300    # RL-171 §6.1, confirmed by RL-172 §0: 300 s after a campaign close; 1,200 s after F0, F2 or any other close
WT=/Users/edr/code/jw-wt/partc-c3f4
test -e "$WT" || git -C /Users/edr/code/JouleWise worktree add --detach "$WT" c3f4bacd8013ca98c19cf8d41f830c701930cd41
mkdir -p "$CUSTODY/standing-f0"

# ONE newest-close selection over both roots, used by the host gate and by copy_gate (Sol RL-172 re-check 1)
close_census() {
  CENSUS="$("$PY" -I -B - /Users/edr/campaign-out /Users/edr/code/jw-wt <<'PY'
import math, os, sys
def fail(e):
    raise e
newest, path, count = None, None, 0
for root in sys.argv[1:]:
    if not os.path.isdir(root):
        sys.exit(f"STOP: receipt root missing: {root}")
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
        if dirpath.count("/") - base >= 3:
            dirnames[:] = []          # receipts at depth <= 4, as `find -maxdepth 4`
        if "runner_receipt.json" in filenames:
            p = os.path.join(dirpath, "runner_receipt.json")
            m = os.stat(p).st_mtime
            count += 1
            if newest is None or m > newest:
                newest, path = m, p
if count == 0:
    sys.exit("STOP: the receipt census found no runner_receipt.json; receipts are expected on this host")
if "\n" in path:
    sys.exit("STOP: newline in a receipt path")
print(math.ceil(newest))
print(path)
print(f"census: {count} receipts, newest mtime {newest!r} {path}", file=sys.stderr)
PY
)" || return 1
  CENSUS_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  NEWEST_RECEIPT="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  case "$CENSUS_EPOCH" in ''|*[!0-9]*) echo "STOP: the receipt census gave no close epoch"; return 1;; esac
  test -n "$NEWEST_RECEIPT" || { echo "STOP: the receipt census gave no receipt path"; return 1; }
}
# The effective close, computed ONCE per gate (Sol confirm P1): max of the census and OTHER_CLOSE_EPOCH, with its path or label.
# The host gate's GAP and copy_gate's kind check both use EFF_EPOCH / EFF_PATH from the same call.
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  close_census || return 1
  EFF_EPOCH=$CENSUS_EPOCH; EFF_PATH="$NEWEST_RECEIPT"
  if test "$OTHER_CLOSE_EPOCH" -gt "$CENSUS_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH="OTHER_CLOSE_EPOCH $OTHER_CLOSE_EPOCH (a session or W1 close outside the census roots)"
  fi
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
# /Users/Shared/JouleWise/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() (   # a subshell: it reads EFF_PATH (from effective_close) and LAST_CLOSE_KIND and changes nothing the host gate reads
  test -n "${EFF_PATH:-}" || { echo "STOP: copy_gate needs effective_close first"; exit 1; }
  if printf '%s\n' "$EFF_PATH" | grep -Eq '^/Users/edr/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    newkind=campaign
  else
    newkind=other
  fi
  test "$newkind" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $EFF_PATH; mail the lead"; exit 1; }
  if test "$newkind" = other; then
    echo "copy gate: newest close is non-campaign ($EFF_PATH); its Check covers the copy"; exit 0
  fi
  plan_id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$plan_id" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $EFF_PATH"; exit 1;; esac
  copy_ok="/Users/Shared/JouleWise/desk-copy/$plan_id.ok"
  test -s "$copy_ok" || { echo "WAIT: no journal-copy marker $copy_ok for the newest close, campaign span $plan_id ($EFF_PATH): the lead's hash-verified copy is not done; retry at the next activation"; exit 1; }
  echo "journal copy of $plan_id: $(cat "$copy_ok")"     # record this line
)

# THE COMPLETE ELIGIBILITY CHECK (rules 1-8, expiry, reservation, current time, current head). It runs here AND again
# as the first step of "Run", on freshly re-read state (Sol items review P1-3). Any failure: return 1, nothing launches.
f0_eligible() {
  # Rule 2: void if the W1-line head moved (fetched fresh); expiry
  git -C /Users/edr/code/JouleWise fetch -q origin ops/2026-11-11-w1-presign || { echo "STOP: fetch failed"; return 1; }
  W1HEAD="$(git -C /Users/edr/code/JouleWise rev-parse origin/ops/2026-11-11-w1-presign)"
  test "$W1HEAD" = c3f4bacd8013ca98c19cf8d41f830c701930cd41 || { echo "VOID: the W1-line head is $W1HEAD; mail the lead"; return 1; }
  test "$(date +%s)" -le "$EXPIRY_EPOCH" || { echo "EXPIRED: mail the lead"; return 1; }
  # Rule 1: the pin, the clean worktree and the 17 hashes
  test "$(git -C "$WT" rev-parse HEAD)" = c3f4bacd8013ca98c19cf8d41f830c701930cd41 || { echo "STOP: worktree HEAD"; return 1; }
  test -z "$(git -C "$WT" status --porcelain)" || { echo "STOP: dirty worktree"; return 1; }
  git -C "$WT" diff --quiet 0ec600128cb5e5040fe0dad2d30e4a10a38eae67 HEAD || { echo "STOP: tree differs from PR #783's head"; return 1; }
  while read -r h p; do
    test "$(shasum -a 256 "$WT/$p" | cut -c1-64)" = "$h" || { echo "STOP: hash mismatch $p"; return 1; }
  done <<'HASHES'
2806f9eae61210d457ae19a5484cfe7dc7ac70a31c20b1ca0a2856f32178a825 scripts/align_r1_rehearsal.py
7403e69d9aedb54887bfc4218a45db84faa653329ca977bcf97edf20af88f923 scripts/align_r1_runtime.py
a5ba3cd4dce1b41c8448e2e26653789a9f607ffc2836a7b4a9339b991f9b6dac joulewise/align/apple/r1_runtime.py
4b9d1c69b0459a0382dfdd5e3aee56366e99f770ed2320cfff90539647ab6591 joulewise/align/apple/r1_runtime_contract.py
0132579cc33f8a997cdfd5f3dd84466352cdeeeebf9ca7de8dc1ec7990cea0a9 joulewise/align/apple/smc_enumeration.py
c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d joulewise/align/apple/thermal_gates.py
272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46 configs/align/v4/r1_runtime.json
ffd6c025f4691771ea348f5d0f670c8f4bbfcb61afe67b83831afdd6c3d6f1ea joulewise/align/apple/r1_phase_table.py
837b74be97616c48c26b0c1277fe2a605b575d5cfc4396dc05e1139079daf1ba joulewise/align/apple/workload.py
b9b46f9ede50b265c245dcc05d3503139632ae129e313675622fa1dce25d39d7 joulewise/align/apple/thermal.py
242cd7aa0bf5788786ca8630e6931abcaaa3e01dc3bf014255a6191b50c6e799 scripts/launch_align_r0.py
ac1dc2a223754cfc3295dd1352a838a3077671da140ffeeba484400e1bd249c6 scripts/run_align_r0_launchagent.sh
6f1fb9f4ac3109650b36b07012e24728c17e7112e7b59953e6557f2b5fdd35aa scripts/run_align_r1_smoke.py
39dd7946e899058987038130b9c133298283a80ae3db4dceee79daad3c8e08b8 scripts/align_r1_followup_kit.py
b2c91c77ef9f1c227c5c172690fadf5f36cff22b4874d0eeaa66798ca9ef12b8 scripts/align_r1_part_c.py
b605195f9a23226a702376d9fbdb2e451546d6c3187297c39bd5b88e2e78f167 joulewise/align/apple/rl145_prints.py
6815d1b65fee6bc67743a8905a3e61dcc8f5294b62fdd238938ca1e77b16ef57 joulewise/align/apple/v4_registration.py
HASHES
  # Rules 3 and 4: an outstanding refusal takes precedence over every other trigger (Sol items review P1-4)
  test -n "${OUTSTANDING_REFUSAL:-}" || { echo "STOP: set OUTSTANDING_REFUSAL (the refused span, or none)"; return 1; }
  if test "$OUTSTANDING_REFUSAL" != none; then
    test -n "${MAIL_EPOCH:-}" && test -n "${LEAD_REPLY:-}" || { echo "STOP: set MAIL_EPOCH and LEAD_REPLY for the refusal (rule 4)"; return 1; }
    test "$LEAD_REPLY" = none || { echo "HOLD: the lead replied that it is clearing $OUTSTANDING_REFUSAL; wait for its re-arm (rule 4)"; return 1; }
    test "$(date +%s)" -ge $((MAIL_EPOCH + 1200)) || { echo "WAIT: 20 min after the refusal mail (rule 4)"; return 1; }
    TRIGGER=refusal; TRIGGER_SPAN="$OUTSTANDING_REFUSAL"
  else
    case "${TRIGGER:-}" in
      not_ready|no_staged) ;;
      refusal) echo "STOP: TRIGGER refusal with no outstanding refusal recorded"; return 1;;
      *) echo "STOP: TRIGGER must be not_ready or no_staged when no refusal is outstanding"; return 1;;
    esac
  fi
  # Rule 8: host state of the latest close of ANYTHING on this host
  test "${HOST_RESTORE_OK:-}" = 1 && test "${UNPROVEN_GROUP:-}" = 0 && test "${HOLDING_STOP:-}" = none \
    || { echo "HOLD: restore unproven, an unproven leg child, or a host-state stop (rule 8); mail the lead"; return 1; }
  # Never while anything is armed; the close interval after the latest close of anything (RL-171 §6.1)
  test ! -e "$CUSTODY/desk_fence.json" || { echo "STOP: a desk fence is up"; return 1; }
  launchctl list | grep -qE 'com\.joulewise\.(night|align-r0)' && { echo "STOP: a night or smoke agent is loaded"; return 1; }
  pgrep -fl 'cadence_legs_runner|launch_cadence_span' >/dev/null && { echo "STOP: a campaign span is running"; return 1; }
  { test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker; } || { echo "STOP: High Power marker"; return 1; }
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be set to a whole epoch (rounded up) or an explicit 0 (unset or empty stops)"; return 1;; esac
  # The receipt census: every runner_receipt.json at depth <= 4 under both roots, fractional mtimes, ROUNDED UP.
  # Any lookup error, a missing root, or no receipt at all STOPS: missing evidence never becomes 0 (Sol re-check 2, 3).
  effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; return 1; }
  HOST_LAST_CLOSE=$EFF_EPOCH    # the effective close (max of the census and OTHER_CLOSE_EPOCH), computed once (Sol confirm P1)
  case "${LAST_CLOSE_KIND:-}" in campaign) GAP=$QUIET_CAMPAIGN_S;; other) GAP=1200;; *) echo "STOP: set LAST_CLOSE_KIND to campaign or other"; return 1;; esac
  test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval $GAP s after the latest close ($HOST_LAST_CLOSE; RL-171 §6.1)"; return 1; }
  copy_gate || return 1
  # RL-172 (h): on the restart day no F0 arms after 12:00 until the lead records the restart done
  case "${RESTART_PENDING:-}" in yes) test "$(date +%H)" -lt 12 || { echo "HOLD: the RL-172 (h) restart is pending today; no F0 after 12:00 until it is recorded done"; return 1; };; no) ;; *) echo "STOP: set RESTART_PENDING to yes (restart due today, not yet done) or no"; return 1;; esac
  # R-A: from the lead's READY record a v4 session takes the next clean close (RL-172 (f); RL-155 R-A)
  test "${SESSION_READY:-}" = no || { echo "CEDE: a READY v4 session takes this slot, or SESSION_READY is unset"; return 1; }
  # Rules 5, 6, 7 and the session reservation, on the current clock
  test -s "$LEDGER" || { echo "STOP: seed the ledger first (item 319's t0 1794703426; item 325's t0 if it launched)"; return 1; }
  F0_NOW="$("$PY" -I -B - "$LEDGER" "${COUNTED_LATEST:?}" none <<'PY'
import sys, time, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
now = time.time(); d = dt.datetime.fromtimestamp(now, TZ)
t0s = sorted(float(l.split("\t")[0]) for l in open(sys.argv[1]).read().splitlines() if l.strip() and not l.startswith("#"))
today = [t for t in t0s if dt.datetime.fromtimestamp(t, TZ).date() == d.date()]
if t0s and now < t0s[-1] + 14400: sys.exit(f"WAIT: F0 spacing, 4 h after the last Part C t0 {t0s[-1]:.0f} (rule 5)")
if len(today) >= 3: sys.exit("STOP: three F0 t0s already today (rule 5)")
hm = d.hour * 3600 + d.minute * 60 + d.second
if not (9300 <= hm <= 81600): sys.exit("STOP: outside 02:35:00-22:40:00, the c3f4bacd8 soak child's window (rule 6, RL-171)")
for e in ([] if sys.argv[2] == "none" else sys.argv[2].split()):
    if now + 12180 + 1200 > float(e): sys.exit(f"STOP: it would cost the counted span due by {e} its day (rule 7)")
print(int(now))
PY
)" || return 1
  echo "F0 ELIGIBLE at $F0_NOW; trigger $TRIGGER $TRIGGER_SPAN; host last close $HOST_LAST_CLOSE ($LAST_CLOSE_KIND, gap $GAP s)"
}

# State the function reads (set from RUN_STATE, the staged items, the mail and the last Check; re-set before "Run"):
#   OUTSTANDING_REFUSAL  none, or the span/session whose arm refused and whose rule-4 handling is not complete
#   MAIL_EPOCH, LEAD_REPLY  for an outstanding refusal: the send epoch of your mail, and clearing or none (rule 4)
#   TRIGGER, TRIGGER_SPAN   not_ready or no_staged (ignored while a refusal is outstanding)
#   HOST_RESTORE_OK, UNPROVEN_GROUP, HOLDING_STOP   rule 8
#   OTHER_CLOSE_EPOCH   REQUIRED: a whole epoch (rounded up) of a close outside the census roots (session, W1), or an explicit 0
#   LAST_CLOSE_KIND     campaign (the latest close was a campaign span) or other (Part C/F0, F2, slot session, W1)
#   SESSION_READY, COUNTED_LATEST   R-A (the lead's READY record, RL-172 (f)) and rule 7; RESTART_PENDING  RL-172 (h) (COUNTED_LATEST: the window-end epochs
#                       of every staged counted span due today, space-separated, or none)
f0_eligible || exit 1

# The staged worktree at the pin
cd /Users/edr/code/jw-wt/partc-c3f4
test "$(git rev-parse HEAD)" = c3f4bacd8013ca98c19cf8d41f830c701930cd41
git merge-base --is-ancestor f30a97d008b57acde9adec0f789dff13c9d6ef23 HEAD
git merge-base --is-ancestor a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe HEAD
git merge-base --is-ancestor f006b7aa665280253db10d7a167599ff385fcec4 HEAD
git diff --quiet 0ec600128cb5e5040fe0dad2d30e4a10a38eae67 HEAD || { echo "STOP: tree differs from PR #783's head"; exit 1; }
test -z "$(git status --porcelain)"
REPO="$PWD"
OUT="$REPO/.desk/r1-partc-f0-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')"
test ! -e "$OUT" || { echo "STOP: OUT exists"; exit 1; }
for p in scripts/align_r1_rehearsal.py scripts/align_r1_runtime.py joulewise/align/apple/r1_runtime.py joulewise/align/apple/r1_runtime_contract.py joulewise/align/apple/smc_enumeration.py joulewise/align/apple/thermal_gates.py joulewise/align/apple/r1_phase_table.py joulewise/align/apple/workload.py joulewise/align/apple/thermal.py configs/align/v4/r1_runtime.json \
         scripts/launch_align_r0.py scripts/run_align_r0_launchagent.sh scripts/run_align_r1_smoke.py scripts/align_r1_followup_kit.py scripts/align_r1_part_c.py joulewise/align/apple/rl145_prints.py joulewise/align/apple/v4_registration.py; do
  printf '%s %s\n' "$(shasum -a 256 "$p" | cut -c1-64)" "$p"; done        # compare with the table above
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
# must print c3f4bacd8013ca98c19cf8d41f830c701930cd41
# RL-89 Mac check: item 325's script, verbatim (R0=/Users/edr/night-align/r0-v4-20261108T0550Z/smc/r0.json, EXPECT e6231a8f…769b)
R0=/Users/edr/night-align/r0-v4-20261108T0550Z/smc/r0.json
"$PY" -I -B - "$R0" "$REPO/configs/align/v4/r1_runtime.json" <<'PY'
import hashlib, json, sys
EXPECT = "e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b"
raw = open(sys.argv[1], "rb").read()
got = hashlib.sha256(raw).hexdigest()
assert got == EXPECT, f"REFUSE: r0.json sha256 {got} != {EXPECT}"
rows = [r for r in json.loads(raw)["response"]["ranking"]
        if r["class"] in ("die", "heatsink") and r["eligible"] is True]
keys, classes = [r["key"] for r in rows], {r["key"]: r["class"] for r in rows}
config = json.load(open(sys.argv[2]))
assert config["sensors"]["r0_sha256"] == EXPECT, "REFUSE: config r0_sha256"
assert len(keys) == 60 and len(set(keys)) == 60, f"REFUSE: {len(keys)} eligible rows"
assert config["r0_classified_keys"] == keys, "REFUSE: r0_classified_keys != r0.json eligible rows (ranking order)"
assert config["r0_classes"] == classes, "REFUSE: r0_classes != r0.json classes"
s = config["sensors"]
assert (s["s_fast"], s["s_slow"], s["record_keys"]) == ("TV0h", "TV1h", ["Tf08"]), f"REFUSE: sensors {s}"
assert classes["TV1h"] == "die" and classes["TV0h"] == "die"
print("RL-89 MAC CHECK OK", got, len(keys), sum(c == "die" for c in classes.values()),
      sum(c == "heatsink" for c in classes.values()),
      hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest())
PY
"$PY" -B -m unittest tests.align.test_r1_smoke_launcher.LauncherTests.test_r1_smoke_plist_runs_interactive_like_the_night_templates   # must be OK
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker && test ! -L /Users/Shared/JouleWise/host-power/high-power.marker || { echo "STOP: High Power marker"; exit 1; }
lsof -- /Users/Shared/JouleWise/host-power/night.lock 2>/dev/null && { echo "STOP: night.lock has a holder"; exit 1; } || echo "night.lock: no holder"
sudo -n -l /bin/kill >/dev/null; echo "sudo kill rc $?"                 # must be 0
pgrep -fl 'b6_r12|r12' || echo "no r12"                                # must print "no r12"
pgrep -fl 'cadence_legs_runner|launch_cadence_span' || echo "no campaign span"   # must print "no campaign span"
pgrep -fl 'claude|codex' | grep -v "^$MAGISTRATE_PID " || echo "no other agent"   # must print "no other agent"
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
sudo -n systemsetup -getusingnetworktime                               # must say Off
# RL-172 (h): the OS daily batch time computed from the boot time (boot + 12 h + 48 s, then every 24 h). PRINT ONLY: it gates nothing
BOOT="$(sysctl -n kern.boottime | sed -E 's/^\{ sec = ([0-9]+),.*$/\1/')"
case "$BOOT" in
  ''|*[!0-9]*) echo "batch print: kern.boottime unreadable";;
  *) NEXT_BATCH=$((BOOT + 43248)); while [ "$NEXT_BATCH" -le "$(date +%s)" ]; do NEXT_BATCH=$((NEXT_BATCH + 86400)); done
     echo "boot $(date -r "$BOOT" '+%Y-%m-%d %H:%M:%S %Z'); next OS batch $(date -r "$NEXT_BATCH" '+%Y-%m-%d %H:%M:%S %Z') (boot + 12 h + 48 s + whole days)";;
esac      # record this line in the arm record
# kernel frequency word: read it as item 308 did; must be 0 (else item 251's remedy, then re-read)
pmset -g | grep -i powermode                                           # 0
launchctl list | grep -E 'com\.joulewise\.(night|align-r0)' || echo "no night/smoke agent"
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"       # ac_power true
# Deadline: launch + 4 h (RL-171 retires the 01:30 cap); the launcher refuses anything under 12,180 s
DEADLINE="$("$PY" -B -c "import time; print(time.time()+14400)")"
```

The Mac check must print the line above. The seventeen hashes must match the table, and `verify_r1_executed_sources` must return the full sha. Anything else means STOP.

**Run (your last action):**

```sh
# Re-read RUN_STATE, the staged items, the mail and the last Check NOW, and re-set every variable the function reads.
# Then the COMPLETE eligibility check again, on the current clock and the current W1-line head (P1-3):
f0_eligible || exit 1
DEADLINE="$("$PY" -B -c "import time; print(time.time()+14400)")"
T0=$(date +%s)
"$PY" -B scripts/launch_align_r0.py launch \
  --runner-kind r1-smoke --repo "$REPO" --python-bin "$PY" \
  --output "$OUT" --fresh-soak --parts C --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30 \
  && printf '%s\t%s\t%s\n' "$T0" "standing-f0:$TRIGGER:$TRIGGER_SPAN" "$OUT" >> "$LEDGER"
echo "$OUT"
```

Require exit 0, and `"next": "exit the magistrate session now"` with a claimed fence (fence `pid` ≠ `MAGISTRATE_PID`). Record PY, MAGISTRATE_PID, OUT, DEADLINE, T0, LAST_CLOSE_KIND, QUIET_CAMPAIGN_S, the two F0 ELIGIBLE lines, OUTSTANDING_REFUSAL, TRIGGER and TRIGGER_SPAN (with MAIL_EPOCH, LEAD_REPLY and the reply's text for a refusal), HOST_RESTORE_OK, UNPROVEN_GROUP, HOLDING_STOP, OTHER_CLOSE_EPOCH, the host last close, SESSION_READY, RESTART_PENDING, COUNTED_LATEST, the journal-copy line and the batch-time print in your RUN_STATE item and in `/Users/edr/night-custody/magistrate/r1-partc-f0-out-<activation>.txt`. Then exit at once, with no other `claude` or `codex` process running.

**Check (next activation, after the fence is gone):**

**Maintenance line first (RL-171 §5 item 1; as item 331). Print only: it gates nothing and is not a stop.** One read-only system-log query over the run's interval (from OUT's UTC launch stamp to the receipt's mtime) for the OS maintenance processes, saved BESIDE the journals as `$OUT/maintenance-log.txt`, with a per-10-minute count printed for the report. F0 now launches from 02:35, beside the second cluster (02:37-02:43) and the XProtect fast scans (05:08, 11:08, 17:08, 23:08 on the current boot); the line records what overlapped. Nothing is judged on it.

```sh
START_UTC="$(basename "$OUT" | sed -E 's/.*-([0-9]{8}T[0-9]{6}Z)$/\1/')"
START_LOCAL="$("$PY" -B -c 'import sys,datetime as d; t=d.datetime.strptime(sys.argv[1],"%Y%m%dT%H%M%SZ").replace(tzinfo=d.timezone.utc); print(t.astimezone().strftime("%Y-%m-%d %H:%M:%S"))' "$START_UTC")"
END_LOCAL="$(date -r "$(stat -f %m "$OUT/runner_receipt.json")" '+%Y-%m-%d %H:%M:%S')"
echo "maintenance window $START_LOCAL .. $END_LOCAL"
sudo -n /usr/bin/log show --style compact --start "$START_LOCAL" --end "$END_LOCAL" \
  --predicate 'process IN {"dasd","XProtect","XprotectService","XProtectPluginService","mds","mds_stores","mdworker","mdworker_shared","backupd","softwareupdated","mobileassetd"}' \
  > "$OUT/maintenance-log.txt" 2>"$OUT/maintenance-log.err"; echo "log show rc $?"
wc -l < "$OUT/maintenance-log.txt"
awk '{ if ($2 ~ /^[0-9][0-9]:[0-9][0-9]/) { b=substr($2,1,4) "0"; for (i=3;i<=NF;i++) if ($i ~ /\[[0-9]+:/) { split($i,a,"["); p=a[1]; break } ; c[b" "p]++ } } END { for (k in c) print k, c[k] }' "$OUT/maintenance-log.txt" | sort
```

Then item 325's Check, verbatim, with this run's `$OUT`:

```sh
"$PY" -B - "$OUT" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps({k: r.get(k) for k in ("rc", "parts", "parts_requested", "fresh_soak", "error")}, sort_keys=True))
print([(s["name"], s["rc"]) for s in r["steps"]])
soak = [s for s in r["steps"] if s["name"] == "soak"]
part_c = [s for s in r["steps"] if s["name"] == "part-C"]
print("soak", soak and soak[0].get("rc"), soak and soak[0].get("result", {}).get("soak_reference_sha256"))
print("part-C", part_c and part_c[0].get("rc"), part_c and part_c[0].get("error"))
assert r["parts"] == {"C": True} and r["parts_requested"] == "C" and r.get("fresh_soak") is True
assert soak and soak[0]["rc"] == 0
assert part_c and r["rc"] in (0, 1) and part_c[0]["rc"] == r["rc"]     # rc 1 = completed, verdict not "pass"
assert [s["name"] for s in r["steps"]].count("close-volumes") == 1
for feed in r["feeds"].values():
    assert feed["stop"]["proven_stopped"]
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
print("RECEIPT OK")
PY
# smoke_part_c.json: print ONLY evaluation, N_chunk, T_dead (and the kit's error text if there is no evaluation). Never print members/slots.
"$PY" -I -B - "$OUT/part-c/smoke_part_c.json" <<'PY'
import json, sys
g = json.load(open(sys.argv[1]))
ev = g.get("evaluation")
d_bank = (g.get("members") or {}).get("d_bank") or {}
print(json.dumps({"evaluation": ev,
                  "N_chunk": None if ev is None else ev.get("n_chunk_configured"),
                  "T_dead_s": (d_bank.get("deadman") or {}).get("T_dead_s"),
                  "error": None if ev is not None else g.get("error")}, indent=1, sort_keys=True))
PY
test ! -e "$CUSTODY/desk_fence.json"; launchctl list | grep -c 'com.joulewise.align-r0' || true   # expect 0
plutil -p "$CUSTODY"/r0-launches/<token>/*.plist | grep ProcessType      # must show Interactive
pmset -g | grep -i powermode                                            # 0
sudo -n systemsetup -getusingnetworktime                                # Off
# kernel frequency word: 0 (item 251 remedy if not)
test ! -e /Users/Shared/JouleWise/host-power/high-power.marker
pgrep -fl 'km003c_monitor.py|hazard_monitor.py' || echo "no stray monitor"
pgrep -u root -fl powermetrics || echo "no root powermetrics"
```

**Report** (by email to Ed and the lead, as the next RUN_STATE item, and one line on the standing notice):
- the trigger and its span; the receipt line and RECEIPT OK;
- the soak's rc, its reference sha256 and its two bands (TV0h, TV1h); part-C's rc;
- from `smoke_part_c.json` only: `evaluation` (its `verdict` and `disposition` as printed, each `lines` entry's `pass` and its detail, `d_bank_mechanics.checks.admitted_turns` with its `status`/`stop` if not judged, the `log` lines including the three-turn clause line and whether X_G ran, and `printed_not_judged`), N_chunk and T_dead;
- beside each `lines` entry, the previous Part C's `pass` for the same line (from its RUN_STATE report, not from its files);
- the maintenance line's counts (print only);
- the close used for the close interval and its kind (LAST_CLOSE_KIND, GAP), the previous F0 t0, this t0, and whether 00:00 fell inside the span;
- the restore lines. A failed restore line is the "restore unproven" stop: it holds every later arm (rule 8).

The verdict decides nothing here. Commit nothing from `$OUT`. The magistrate reports; it never decides.

**After (the lead, at the desk; not the magistrate).**
- Copy the OUT off the MBP between spans (never while a fence is up).
- Read the verdict under RL-164 §3 beside the previous Part C's, line by line. A differing line goes to the research lead with both runs; this item stays live.
- At each W1-line merge, re-issue this item at the new head as part of the merge, with the carry diff of RL-156 §4.1 recorded (RL-165 §3 rule 2; §9 for #774's one line).
