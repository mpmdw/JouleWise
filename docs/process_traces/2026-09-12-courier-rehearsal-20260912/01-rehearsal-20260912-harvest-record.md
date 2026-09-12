# Record 01 — rehearsal-20260912 harvest record (night courier, 2026-09-12 00:30–00:40 PDT)

Written by the night courier session (pid 93256, Fable 5.1) that the night
driver launched at 00:30:17 PDT after the stub night completed. The courier
prompt (`docs/process/NIGHT_COURIER_PROMPT.md`) told it to continue with the
handback's next lane; the relaunched magistrate was not alive (the watchdog
held `HOLD_CENSUS` on this courier's own process), so the courier ran the
harvest under record 13 §Harvest pointer of activation 58a3bcfc and
checklist 13 §2 of activation 96bfeca7.

## 1. What fired

| Fact | Value |
|---|---|
| Plan | `rehearsal-20260912`, class `REHEARSAL_STUB`, t0 epoch 1789198200 (00:30:00 PDT 2026-09-12), window 900 s |
| Frozen triple | (`rehearsal-20260912`, `/private/tmp/joulewise-rehearsal-20260912-checkout`, `a7d1eb88aaf9f70f430d95da69f39c4190299a80`) |
| Driver start (launchd) | 00:30:04.29 PDT (`night.log` line 1: `night driver started`) |
| Gate verdict | `night gate verdict=REHEARSAL_ONLY` at 00:30:04.76 |
| Stub chain | pid 93114, started 00:30:04.79, exited 00:30:07.09, exit code 0, stdout `REHEARSAL`, stderr empty |
| Result | `result.json` verdict `REHEARSAL_ONLY`, `chain_exit_code` 0, `aborted_reason` null, `census_count` 1, `census_hits` [] |
| Results branch | `night-results/20260912` on origin: `99d099c1` (00:30:12, night records) then `e657f30f` (00:31:45, courier records); `night.log` carries both `durable record pushed` lines |
| Courier | attempt 1, heartbeat seen, sent; Gmail message id `1a09487237fa6be2` (thread `1a09487237fa6be2`), read back in the mailbox with label `SENT` at 00:31:19Z... (Gmail date `2026-09-12T07:31:19Z`) |
| `launchd.night.err` | EMPTY (0 bytes); `launchd.night.out` EMPTY |
| Launchd last exit | `com.joulewise.night` status 3 (the stub's unconditional status, ruling 61 Q4.3; not a refusal) |
| Watchdog at courier launch | `state.json` age 276.5 s, decision `FENCED`, `standdown_phase` COMPLETE; at 00:35 `HOLD_CENSUS` (own courier process), age 285.5 s; alive |

## 2. Ruling 06 C-7, clause by clause (all on disk under `01-harvest-evidence/`)

| C-7 clause | Evidence | Verdict |
|---|---|---|
| `receipt.json` verdict `REHEARSAL_ONLY` | `night/receipt.json` `verdict`, `refusal: null` | MET |
| C1 PASS with measured `registration_sha256` | C1 `status: PASS`, `registration_sha256` `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` for `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` | MET |
| C2 `NOT_APPLICABLE` basis `no_pack_by_design` | C2 `status: NOT_APPLICABLE`, `basis: no_pack_by_design` | MET |
| C3 PASS with measured `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`, `load_average_raw`, `thermal_raw` (`cpu_speed_limit` when present) | all five keys present with raw probe output; `cpu_speed_limit` null (absent from `pmset -g therm`, which reported no recorded CPU power status); `load_1m` 1.74; `displaysleep` 0; agent census exit 1 with empty stdout (both censuses in `censuses.jsonl`) | MET |
| C4 PASS with boot-UUID/clock pair | `boot_session_uuid` `bb7bacd0-9dda-4a2b-b105-dcfb652f894d`, `clock_epoch_s` 1789198204.752934, `clock_monotonic_ns` 623398146251791 | MET |
| C5 PASS with `chain_stub: built_in_stub_by_design`, `chain_sha256: null`, `expected_chain_sha256: null` | exactly so; driver/measurement/plan heads all `a7d1eb88…`; `observed_epoch_s` 1789198204.30 inside the window | MET |
| `result.json` `REHEARSAL_ONLY`, `chain_exit_code` 0 | as above | MET |
| `launchd.night.err` EMPTY | 0 bytes (the 09-11 traceback signature is absent) | MET |
| `night.log` lines | `night driver started`; `night gate verdict=REHEARSAL_ONLY` (not REFUSED); `durable record pushed branch=night-results/20260912` (twice); `courier attempt=1 heartbeat=True sent=True` | MET |
| `courier.sent` message id read back in the inbox | `1a09487237fa6be2`, `labelIds: ["SENT"]`, subject `[JouleWise night courier] rehearsal-20260912: REHEARSAL_ONLY, chain exit 0, all gate rows passed` | MET |
| Launchd last-exit 3 is not a refusal | observed 3 before uninstall; receipt `refusal: null` | noted |

**Judgment: every C-7 clause is MET. NIGHT-REHEARSAL-01 acceptance item 6 is
MET on rehearsal-20260912.** Item 5 was already MET (58a3bcfc record 01) and
this night needed nothing for it. This record is the courier's harvest; ruling
06 §7 asks that C-1…C-8 be cited by path in the arm record and the harvest
record — C-1…C-6 are cited in the arm record
(`docs/process_traces/2026-09-11-activation-1944317a/01-rehearsal-20260912-arm-record.md`),
C-7 here, C-8 in record 02 of this directory.

Ed's non-veto of R1 on the notice thread `1a0800cdb282c3f1`: the courier did
not re-read the thread (the 3fafd42c stand-down at 00:05 had verified no NO
as of then; the night fired, which the agents would not have done had a
stand-down been executed). The relaunched magistrate re-verifies the thread
before the equivalence-night install.

## 3. Preservation (checklist 13 §2, "preserve first")

1. `lstat` inventory of the live custody root (excluding `results-clone/`)
   taken at 00:34:45 PDT before any copy: `01-harvest-evidence/lstat-inventory.txt`
   (18 rows, `%N|%z|%m|%p|%u:%g`).
2. Byte-exact archive OUTSIDE plan discovery:
   `/Users/edr/night-archive/rehearsal-20260912-harvest-1789198485/` holding
   `custody-root.tar` (sha256 `fb336bff…dc78d`, without results-clone),
   `custody-root-full.tar` (sha256 `bb750d55…28e79`, whole root incl.
   results-clone), `copy/` (rsync of the whole root, 496 MB), `SHA256SUMS`.
   `diff -qr` of the live root against `copy/` was CLEAN over the whole root
   (00:36 PDT) and again after the uninstall (00:35:23, records only).
3. Repo copies: `01-harvest-evidence/` in this directory = `night.log`,
   `night_plan.json`, every `night/*` record (14 files incl. `courier.lock`
   and the two empty launchd streams), the lstat inventory and the tar
   digest, with `SHA256SUMS` (17 entries, all verified OK on write).
4. Results-branch check: `git ls-remote --exit-code origin refs/heads/night-results/20260912`
   → `e657f30f`; every file the branch holds under
   `docs/process_traces/night-results/20260912/` was `cmp`-identical to the
   custody record (9/9 SAME: censuses, chain.started/exited, courier.*,
   receipt.json, result.json).
5. Courier email read back: Gmail `get_message` on `1a09487237fa6be2` →
   label `SENT`, recipient `claude.ai.copper531@passmail.net`.

## 4. What this night disproved and what it does not say

- Disproved: the 09-11 defect (`python3` from PATH resolving to Python 3.9.6
  under launchd). The cured job file's absolute-interpreter line fired under
  launchd for the first time and the driver imported, gated, ran the stub,
  pushed, and couriered with an empty error stream.
- Live for the first time since PR #309 under a launchd-started driver: rows
  C1 (registration hash), C3 tail (HID, AC, display, load, thermal) and C4
  (boot UUID + clock pair), each with measured values.
- Not said: anything about the capture-timeout seam (powermode recorded, not
  gated), or about any measurement — the stub took none.
