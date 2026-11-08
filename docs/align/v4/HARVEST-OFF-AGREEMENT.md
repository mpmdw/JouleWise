# Harvest off the MBP: Opus/Sol agreement and recommended ruling

- **Rule:** Ed's paired-build rule (RUN_STATE 220/221). Opus has the final say under the window design council.
- **Date:** 2026-11-08.
- **Builds compared:**
  - **Opus:** `align/2026-11-08-harvest-off-opus` @ `b9fedca2a`, `docs/align/v4/HARVEST-OFF-opus.md`. It was committed before Sol's branch was read.
  - **Sol:** `align/2026-11-08-harvest-off-sol` @ `961ad48fb`, `docs/align/v4/HARVEST-OFF-sol.md`, code `95e5ec8b7`.
- **Base:** both branch from `05b6d04cb` (`align/2026-11-08-v4-r11`).
- **What was compared:** both design docs and Sol's diff (parse cache, hashing threads, transport and profile CLI). Sol's tests were not re-executed here.

## 1. Where the builds agree

1. **The harvest is the cost, and it is CPU-bound XML parsing.**
   - Opus measures 18 document parses per member and `members` at 97% of harvest.
   - Sol measures parser reuse removing two thirds of the XML decodes, and that XML is more than 99% of parser time.
   - Hashing and copying are minutes, not the bulk.
2. **Nothing in the harvest needs MBP hardware.** It needs the same bytes, the full evidence closure (ledger prefix, pins, custody, journals, meter, executed inventory, pack, registration), the same code and the same interpreter.
3. **The MBP keeps** terminal closure, finalize/commit, a short triage, compressed packing before the quiet dwell, cool-down, pre-arm and dwell.
4. **The MBP originals are never removed** by the offload. Every byte is re-hashed at the receiver, and the tree is published only after full verification.
5. **Byte identity of the whole archive** (177 files) was proven by both on the same constructed window. Both did it by restoring into the same absolute namespace, with emission seams fixed. Both say a relocated restore cannot be byte-identical, because absolute paths are embedded.
6. **U1-U3 can come from the thermal desk without the harvest.** Both use the existing `acceptance`/`window_report` rules, not a parallel rule set. U3 needs energy attribution and exact tokens, not an OS-temperature scan.
7. **The B2 full-desk gate after W1 or a code/config change is kept.** A `full_desk_gate: pass` must be bound to artifacts (record commit, `PILOT.json` digest, harvest success), not to a free-text basis. This is the eng-desk review's M1.1.
8. **Workers.** Start the Air with 2 member processes and measure RSS before going higher.
9. **The Air's disk is the binding constraint:** about 23-24 GiB free against an 18.6-26.4 GB window.
10. **Batching is n/a.** No stage runs inference. **No decision or refusal is cached.**

## 2. Where they differ

| # | Topic | Opus | Sol | Ruling |
|---|---|---|---|---|
| D1 | `member_eligibility` at the next arm | Passes on the **provisional** adjudication: every member classified, with X5, U3 pairs and calibration exclusions. Harvest exclusions finalize counts off the MBP. `calibration_stop` refuses at 8 until final. Needs a registration-text clarification (v4 not yet registered). | Under the current text, the **final** eligibility, meaning the harvest, must return before **every** arm. The Air harvest sits inside cool-down on the critical path: E = 25-60 min, turnaround 37-89 min. | **Opus, with Sol's guard added:** provisional at the arm, plus a hard bound. The Air full desk (harvest included) for window k must be final before the arm of window k+2, and before any arm that B2 already gates. See section 3. |
| D2 | Parse dedupe | Document-level memo: pickles keyed by the SHA-256 of the bytes, anchor-independent, covering every plist and rich telemetry of one member, with no size cap. 2.6-4.3× on members. | Record-level one-entry cache keyed by bytes plus anchor options, with deep copies and a **128 MiB cap** (larger files bypass). 1.45× on the harvest. | **Opus.** Real member plists are about 1 GB, so Sol's cap gives no native benefit. Its one-entry key also misses when callers alternate plists and anchor modes. Keep Sol's explicit max-size argument as an off switch. |
| D3 | Hashing | The 4-5 serial tree inventories are left alone. Opus estimates them at about 1-1.5 min on a real window. | `tree_inventory(workers=N)`, path-ordered, at most 8 threads; `io_workers` seam. | **Adopt Sol's.** It is small but free and order-preserving. Use 2 threads on the Air. |
| D4 | Transport | `harvest_offload`: tarfile plus zstd, single read with hash. Absolute symlinks kept literally. The ledger travels as an append-only external file. The same-path restore is enforced (relocation refuses). The receiver checks the checkout mirror (head, clean incl. untracked, interpreter and package digest). | `harvest_transport`: tee hash plus zstd, content-dedupe of identical files, preserves empty dirs. The manifest is **finalized on the MBP and bound to the record** (closes review M2). Uses the air-offload lane's lock, lease and two-copy retention. | **Merge.** Use Sol's manifest binding and air-offload lane integration, with Opus's same-path enforcement, mirror identity check and append-only ledger placement. Both preserve empty directories. |
| D5 | Byte identity in production | Accepts that host provenance differs. It declares five provenance fields and compares with `archive_projection()`. Tested: unpinned runs differ only there. | Wants a lead-installed **canonical deterministic emission/program envelope** before claiming identity, with processing-host attestation kept separate. | **Opus.** The projection keeps true provenance: the Air harvest does not pretend to be the MBP, which Sol also forbids. It needs no new envelope. N2 (one real window on both hosts, projections equal) is the production proof. |
| D6 | Stage profiling | Runner records the desk wall time only. | `--profile NEW.jsonl` on `harvest_b6_session.py`, per stage, outside custody. | **Adopt Sol's.** It is required for N1 (scenario A/B: does the desk-verdict child run?). |
| D7 | Light triage location | On the Air during cool-down. The MBP is the fallback. | Short MBP summaries (terminal, capture, meter). Thermal on the Air if the MBP projection costs heat or time. | **Agree.** Terminal, capture and meter summaries come from finalize on the MBP. Thermal and eligibility are computed on the Air. |
| D8 | MBP minutes saved / turnaround | 95-102 MBP min/window. Turnaround 33-63 min, or 75-115 min in scenario B at B2 barriers. | 88-100 MBP min. Turnaround 37-89 min, or 41-99 min at barriers. | Both are planning estimates. Under ruling D1, **about 95-100 MBP min/window and 33-63 min turnaround** off-barrier. |
| D9 | Desk PASS reachability | **P5:** `v4_B_bar = all(bar_pass)` with every `bar_pass = None`, so the full desk can never PASS, and the B2 gate after W1 cannot be met. | Not raised. | **Blocker for the lead,** independent of this design (section 4). |
| D10 | Scenario B (the whole-window verdict child) | It strict-validates serially without dedupe. After the speed-up it becomes the critical path; fix F1 opens the memo in the child. | Notes the child is not parallelized. | **Agree.** N1 decides whether it runs for ALIGN. If it does, land F1 before relying on the Air desk at the B2 barriers. |

## 3. Recommended ruling (Opus, final say)

**1. Adopt the hand-off.**
- **MBP:** finalize, pack (record-bound manifest), cool-down, pre-arm, dwell.
- **Air:** verified same-path restore, light triage during cool-down, then the unchanged harvest and full desk with 2 member processes, 2 hash threads and the document memo.

**2. Registration text, prospective** (v4 is unregistered, the lead owns it, and it goes in the public deviation log when registered).
- At the arm, `member_eligibility` passes on the provisional adjudication: every plan member classified, X5, U3 pairs and calibration exclusions.
- Rows enter `calibration_stop` as `provisional`. Only the Air full desk writes `final`.
- **Bound:** window k's final eligibility must be recorded before the arm of window k+2 and before any B2-gated arm. At most one window is ever unfinalized, and the 8th-window decision cannot read provisional counts. The existing `pending_final_eligibility` already enforces the latter.
- **Delete** RUN_STATE 216's "from window 6 on" clause. It belonged to the superseded count stop.
- **Why this is sound:** the harvest can only remove eligibility (proved: final ⊆ provisional), and before 8 windows the decision reads only captured counts (proved identical). A harvest-only instrument finding costs at most the running window, the risk B2 already accepts.

**3. Integration branch** (one reviewed candidate), in this order:
1. Opus memo.
2. Sol hashing threads plus the `--profile` CLI.
3. The merged transport (D4).
4. Opus `light_triage` and the runner.
5. Packet artifact binding (M1.1).

Then rerun both test sets, one module per process, and the whole-archive equality at workers 1/2 with I/O threads 1/2.

**4. Before first native use:**
- **P1:** free about 70 GB on the Air.
- **P5:** lead ruling on `v4_B_bar` gating.
- **Mirror:** the measurement checkout mirror on the Air at the same path.
- **Native smoke:** Sol's injection list (missing or corrupt file, worker death) through arm → finalize → pack → Air → packet.
- **N1/N2** on the first real window: the stage profile and the MBP-versus-Air `archive_projection` equality.

**5. No arm may use this route until** the integration candidate, its native smoke and N2 have passed.

## 4. Open items for the lead

- **P5** (both builds inherit it): define a full-desk PASS that can be met. One option: `v4_B_bar` reported but not gating until the lead sets the B bar. Also, the base fails `tests.align.test_v4_powermode_record::test_desk_check_passes_only_when_every_bundle_matches`, which is pre-existing.
- **Toolbox rule 6** says "content digests at most". The Opus memo keeps parsed content, scoped to one member, never a refusal, and its equality is tested. Approve it as an exception, or fall back to workers only (about 2-3× instead of about 8-10× on the members step).
- **Keep-home-clean exception:** the Air restores the session at its MBP path. Name the path, and prune it after `final`.
