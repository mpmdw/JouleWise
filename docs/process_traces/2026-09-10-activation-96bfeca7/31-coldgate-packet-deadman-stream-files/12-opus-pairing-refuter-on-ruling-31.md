# Opus contract-lens refutation — cold-gate ruling 10 (packet 31, dead-man stream files)

Read-only session, worktree `/Users/edr/code/JouleWise-wt-coldgate-gate-prose` at `58d4696b`. Nothing written, moved or deleted anywhere; custody touched only with `ls`/`stat`/`cat`/`wc`/`python3 os.lstat`.

## Summary (5 lines)

1. **The ruling's outcome is right, and on stronger ground than it cited.** The upstream ratified authority — the coldgate-d1 R-7 amendment the kernel names — is driver-scoped in terms: *"before it, the dead-man writes nothing but a log line and exits GO."* Nothing upstream of synthesis 65 requires `night/` to be empty.
2. **But the literal compression is not only in the 61→65→67 gloss — it is in the kernel itself**, at `/tasks/NIGHT-REHEARSAL-01/dependencies/1/required` ("nothing written into `night/`"). The ruling quotes that row in probe 3 and then argues as if the kernel spoke with one voice. That gap must be closed in text or the 09-11 activation hits the literal criterion again.
3. **Every mechanical fact in the ruling verified**, plus the Q3 courier claim (the courier `Popen` at `run_night.py:811–815` has no `stdout=`, so it inherits launchd's handle — the transcript really does go to `launchd.night.out`).
4. **Two probe claims are wrong.** `tests/test_run_night.py:816–817` *does* assert the stream paths lie inside `night/` (the ruling says nothing does), and the "no code path enumerates the directory" claim is over-broad (`produce_g7_control` rglobs a custody root).
5. **P1–P4 are executable at 03:30 tomorrow with lstat+grep, with one real false-negative hole**: P3 pins the handles' `mtime_ns` and pre-t0 membership, and the 09-11 07:00 dead-man re-firing can move both if the courier failed.

## Findings

| id | severity | claim | evidence |
|---|---|---|---|
| R-1 | cleared (strengthening) | The ratified upstream authority is driver-scoped and the ruling never cited it | `docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md:115–123`: "the dead-man writes nothing but a log line and exits GO … acceptance gains one rehearsal case: agents installed the morning BEFORE the armed night, so the pre-night 07:00 firing is observed standing down" |
| R-2 | should_fix | Q1 §1 asserts the literal wording is a 61/65/67 compression; the kernel carries it too and the ruling never reconciles it | `state_kernel.json` `/tasks/NIGHT-REHEARSAL-01/dependencies/1/required`: "the pre-night 07:00 dead-man stand-down observed with **nothing written into night/** (item 5)" — quoted in the ruling's own probe 3, absent from Q1's argument and from "the kernel acceptance text stands unamended" |
| R-3 | should_fix | Probe 8 is factually wrong: a test *does* pin the stream paths inside `night/` | `tests/test_run_night.py:816–817` `assertIn("@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out", template)` / `.err`; ruling probe 8 says "nothing asserts they lie inside or outside `night/`" |
| R-4 | should_fix | NIGHT-STREAM-PATHS-01 as specified would leave launchd unable to open the relocated handles | `scripts/install_night_agent.sh:125` creates only `"$custody_root/night"`; launchd creates no intermediate directories |
| R-5 | should_fix | P3 can record item 5 NOT MET on a post-t0 event that item 5's object excludes | 09-11 07:00 dead-man fires post-completion; if `courier.sent` is absent it spawns the courier at `run_night.py:811–815` with **no** `stdout=`/`stderr=`, inheriting `launchd.deadman.out/.err` → size>0 and `mtime_ns ≥ T0` → both handles leave `S` → `S = {} ≠ {out, err}` → NOT MET |
| R-6 | nit | Probe 9's blanket "no code path lists the directory" is over-broad | `run_night.py:1276` `control = Path(plan.custody_root)`; `:1316` `if any(path.is_file() and path not in allowed for path in control.rglob("*")): raise PackNightRefusal("G7 control must be fresh")` — inside `produce_g7_control`, a post-night command on a separate fresh root, so the conclusion survives |
| R-7 | should_fix | Q3's "these two files are expected to be NON-empty" is wrong for `.err` and contradicts its own next sentence | `21b-rehearsal-20260909-bench/night-harvest/SHA256SUMS:11` records `night-launchd.night.err` = `e3b0c442…` = sha256 of the empty file (verified: `printf '' \| shasum -a 256`) |
| R-8 | cleared | Q3's courier-stdout mechanism is correct and now bench-verified | courier `Popen` (811–815) has no redirection; the only `sys.stdout` write in the file is `:1859`, the `g7-control` subcommand, not `run` |
| R-9 | cleared | Every stated custody fact holds exactly | both handles: regular, mode `100644`, not symlinks, size 0, birth `1789048801.9481382` / `.9482262` (F+1.948 s), `mtime_ns` `1789048801948138143` / `1789048801948226143`; `night.log` 110 B, birth `1789048802.0925953` (144 ms later); `ls -1a night` = exactly those two entries, no hidden files, no subdirectories; no driver record present |
| R-10 | nit | P1/P3's `[F, F+60 s]` window is safe here but not a general form | the firing is already observed at F+2.09 s; a future post-sleep late launchd firing would fail a 60 s window |
| R-11 | cleared | Q3's time-exclusion of the night's own handles is correct | installer renders stem `launchd.night` (`install_night_agent.sh:191`); installed plist `123-arm-evidence/com.joulewise.night.plist:32–35` = `…/night/launchd.night.out`/`.err`, Hour 2 Minute 56 — disjoint names, birth ≥ T0 |
| R-12 | cleared | Packet digest and arithmetic | `cat 00-PACKET.md exhibit-A | shasum -a 256` = `a4dba85d627c5a813dcea226549da22f6c537670440a7cae928606f935769a60`; plan `t0 1789120560.0`, `window_max_s 900`, `REHEARSAL_STUB`; 1789120560+900+300 = 1789121760 = the logged epoch |

## Q1 — AUTHORITY

**The ruling's reading is correct, and the ruling under-argued it.** The kernel's acceptance text is a *quotation* of the coldgate-d1 R-7 amendment (it says so: "coldgate-d1 R-7 amendment"). That source reads: *"the dead-man may act only after the night's completion epoch …; before it, **the dead-man writes nothing but a log line and exits GO**. Stage-2 acceptance (NIGHT-REHEARSAL-01) gains one rehearsal case: agents installed the morning BEFORE the armed night, so the pre-night 07:00 firing is observed standing down."* The subject is the dead-man process and the acceptance object is the *observation of the stand-down*. Neither clause mentions `night/`. The cold seat expressly did not read coldgate-d1 (it grepped only `D-175`), so it reached the right verdict without its best authority.

**Ruling 61's parenthetical supports the ruling, not the literal reading** — verified at `61-…:130–134`: "with `night/` containing nothing from that firing (no `refusal.json`, no `courier.sent`, no `courier.json` before t0)". The parenthetical enumerates driver records. Refuter 62:155–156 is even more explicitly driver-scoped ("standing down **having written nothing but its log line**").

**The ruling's authority chain has a hole, however.** 61 also states at `:173–174` "an **empty pre-t0 `night/`**", synthesis 65:31 states "night/ holds nothing from that firing", and — the one the ruling must address — the **kernel itself** carries the compression at `/tasks/NIGHT-REHEARSAL-01/dependencies/1/required`. So "the kernel text (the authority; ruling 61/65/67 are its glosses)" is not accurate: the gloss is *also* kernel text. Runbook 67:456–464 (§UNVERIFIED) kept the literal reading deliberately live — "report any conflict with synthesis 65's literal acceptance to the magistrate; **this runbook does not relax it**".

**Is this a rule change the cold seat may not make?** No. I found **no** decision-log entry, no D-number and no Ed ruling ratifying the "`night/` holds nothing" formulation as a criterion (`grep` over `docs/decision_log.md` for `dead-man`/`deadman`/`NIGHT-REHEARSAL-01` returns only D-176 lane rows and the R-7 pointer). The only ratified text is R-7's driver-scoped sentence. The cold seat is therefore *applying* a criterion against its ratified source, which is exactly what rule 11 sends to a cold gate — not amending a ratified rule. **Authority: sound.** But the ruling must say so in text, and must name the kernel dependency row it is reading, or the 09-11 activation will read that row unamended.

## Q2 — FACTS

All verified this session (see R-9, R-11, R-12). Additional verifications: the template renders `@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out`/`.err` at lines 33/35 (committed `8c802bde`, 2026-09-02, a week before ruling 61 — the ruling's chronology holds). `_existing_record` (`:962`) refuses *only* the eight `_WRITE_ONCE_RECORDS` names (`:66–75`) by exact name, called at 1068 and 1430; unknown names cannot trip it. One line the ruling omits: `_write_rerun_refusal` (`:969–975`) writes `rerun-<epoch>.refusal.json`, a name outside that list — unreachable from `dead_man`, so it does not affect item 5, but it is a `night/` name the write-once list does not cover.

`dead_man`'s stand-down branch (`:1740–1747`) returns `EXIT_GO` before `_resolve_courier_bin`, before `_record_courier_substitution`, before any `_write_driver_refusal` and before `_durable_record` — verified by reading 1727–1762. `_append_log` (`:142–145`) opens `custody_root/"night.log"`, not `night/`. Directory enumeration: only R-6's `produce_g7_control` rglob; `joulewise/night_gate.py` has no `iterdir`/`listdir`/`night_dir` hit at all.

## Q3 — PREDICATE P1–P4

**Mechanically executable at 03:30 on 09-11 with `lstat` + `grep` alone: yes**, with these holes.

- **The one real hole (R-5).** P3 requires the two handles to be *in* `S` (`mtime_ns < T0`) *and* to carry today's exact `mtime_ns`. Because the courier inherits the driver's stdio, a *post-completion* 09-11 07:00 dead-man firing on a failed-courier night writes bytes through `launchd.deadman.out`, moving it past T0 and out of `S`. `S` then equals `{}`, which is not the required set, and the harvester records **NOT MET** for a reason item 5's own object excludes. At a 03:30 harvest this is moot; the predicate must say so rather than rely on it.
- **Refusal at 02:56 writing `refusal.json` after t0 (asked):** correctly excluded. `T0 = 1789120560` is the calendar-minute boundary at which launchd *spawns*; every driver write is strictly later, so `mtime_ns ≥ T0` and P4 holds. Fine.
- **launchd re-opening handles at t0 (asked):** the night job uses stem `launchd.night` (installer `:191`, installed plist `:32–35`), a disjoint name pair. The deadman handles are untouched at t0. No hole.
- **Calendar drift / late firing (asked):** P1's `[F, F+60 s]` is retrospectively safe — the 09-10 event is already observed at F+2.09 s and the handles' birth at F+1.948 s, so nothing about tomorrow can move it. As a *general* form the window is brittle (a post-sleep `StartCalendarInterval` job fires at wake), which is R-10.

## Q4 — the night's own `launchd.night.out`/`.err`

**Ruling correct on exclusion, wrong on expectation.** Exclusion by time is right (R-11) and the courier-transcript mechanism is right and now verified (R-8): `subprocess.Popen(_courier_argv(...), cwd=REPO_ROOT, start_new_session=True)` at `:811–815` passes no `stdout`/`stderr`, so the child inherits launchd's handles; and in `run` mode the driver writes nothing to its own stdout (the file's only `sys.stdout` use, `:1859`, is the `g7-control` subcommand). But **`.err` is expected EMPTY, not non-empty** — the 09-09 harvest's own `SHA256SUMS` records it at the empty digest — and the ruling's blanket "these two files are expected to be NON-empty" contradicts its immediately preceding sentence that non-empty stderr is a finding.

## Q5 — NIGHT-STREAM-PATHS-01 blast radius

Repo-wide `grep` for `launchd.night` / `launchd.deadman` / `LOG_STEM` over `scripts/`, `joulewise/`, `tests/`, `configs/`, `docs/`:

- **Live consumers: none.** No file under `docs/process/` (NIGHT_HANDBACK, MAGISTRATE_WATCHDOG, checklists) reads `night/launchd.night.out`; nothing in `joulewise/` mentions it. All other hits are frozen historical traces (`21b` bench renders, `21i:21`, `01-audit-night-loop.md`, `67:459`, `123-arm-evidence`) which must not be edited.
- **Breaks exactly one test:** `tests/test_run_night.py:816–817` (R-3). The ruling's proposed extension site (1504–1505) is the wrong one and would leave 816–817 red.
- **Needs one installer change the ruling did not name:** `install_night_agent.sh:125` creates only `$custody_root/night` (R-4).
- Checklist 13's row 82 ("do not exclude stream files from item 5") is a **preservation** instruction, not an acceptance criterion; relocating the paths does not conflict with it, but the harvest row wording should follow the files.

## Verdict — UPHOLD WITH AMENDMENTS

The verdict `(c) MET with a registered follow-up` stands. Five amendments, exact text:

**A1 — append to Q1 §5 / the "No rule change is needed" paragraph (closes R-2, adds R-1):**
> The kernel carries the literal compression too, at `/tasks/NIGHT-REHEARSAL-01/dependencies/1/required` ("the pre-night 07:00 dead-man stand-down observed with nothing written into `night/` (item 5)"). That phrase is read henceforth as the Q2 predicate, on the same ground as the 61→65→67 gloss: "written into `night/`" means written by the driver. The ratified upstream authority, the coldgate-d1 R-7 amendment (`docs/process_traces/2026-09-01-unattended/coldgate-d1-RULING.md:115–123`), is driver-scoped in terms — "before it, the dead-man writes nothing but a log line and exits GO" — and its stage-2 acceptance case says only "the pre-night 07:00 firing is observed standing down". No text upstream of synthesis 65 requires `night/` to be empty, and no decision-log entry or Ed ruling ever ratified the "holds nothing" formulation as a criterion.

**A2 — replace probe 8 (closes R-3):**
> 8. `sed -n '805,822p;1495,1508p' tests/test_run_night.py` → `test_launch_agent_template_disables_restart_and_installer_rejects_keepalive` ASSERTS the template contains `@@CUSTODY_ROOT@@/night/@@LOG_STEM@@.out` and `.err` (816–817), pinning the stream paths INSIDE `night/`; the render test asserts only that the night and dead-man paths differ (1504–1505).

**A3 — replace the NIGHT-STREAM-PATHS-01 scope sentence (closes R-3/R-4):**
> …with `scripts/install_night_agent.sh:125` extended to create the new directory as well as `night/` (launchd cannot open a stream path whose parent does not exist), `tests/test_run_night.py:816–817` amended to the new template strings, and a new assertion that neither rendered path starts with `<custody_root>/night/`; historical traces that name `night/launchd.night.out` are not edited.

**A4 — append to P3 (closes R-5):**
> P3 is evaluated on an inventory taken strictly before 07:00 PDT on 09-11 (epoch 1789135200). At or after that instant the 09-11 dead-man firing may have re-opened and written through the same two handles on a failed-courier night — a post-completion event outside item 5's object — in which case P3 is evaluated on the earliest inventory taken before it, or, failing that, on P1/P2 plus the absence of any pre-t0 driver record, with the handles' state recorded as post-t0.

**A5 — replace the Q3 closing sentence and probe 9's blanket clause (closes R-6/R-7):**
> Unlike the dead-man handles, `launchd.night.out` is expected to be NON-empty, because the courier is spawned with no stdout redirection (`run_night.py:811–815`) and inherits launchd's handle; `launchd.night.err` is expected to be EMPTY (the 09-09 harvest recorded `night-launchd.night.err` at `e3b0c442…`, the empty-file digest), and non-empty stderr is a finding for item 6. […probe 9…] the only `night_dir` checks on the run path are `_existing_record` by name (962, called at 1068, 1430); the file's one custody-root enumeration, `control.rglob('*')` at 1316, belongs to `produce_g7_control`, a post-night command against a separate fresh control root that no launchd agent writes into.

Nothing was fixed, edited or committed.
