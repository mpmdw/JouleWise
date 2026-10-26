```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Inventory complete: 20 actual slots unfilled, audit/review and launch bindings pending; six native maxima total 62h23m and a conditional calendar fits the cutoff.",
  "workspace": {
    "base_requested": "82cc9462c515a18cfce25e84c58f1160e4b8fbe1",
    "base_mode": "exact",
    "head_start": "82cc9462c515a18cfce25e84c58f1160e4b8fbe1",
    "head_end": "82cc9462c515a18cfce25e84c58f1160e4b8fbe1",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    ".scratch-INV/INVENTORY.md",
    ".scratch-INV/assemble.py",
    ".scratch-INV/audit.py",
    ".scratch-INV/body.md",
    ".scratch-INV/collect.py",
    ".scratch-INV/envelope.json",
    ".scratch-INV/evidence/573delta.md",
    ".scratch-INV/evidence/574delta.md",
    ".scratch-INV/evidence/574fable.md",
    ".scratch-INV/evidence/agreement.md",
    ".scratch-INV/evidence/ancestry.txt",
    ".scratch-INV/evidence/audit.json",
    ".scratch-INV/evidence/b2.md",
    ".scratch-INV/evidence/b2fix.md",
    ".scratch-INV/evidence/b4.md",
    ".scratch-INV/evidence/b5.md",
    ".scratch-INV/evidence/bat-ruling.md",
    ".scratch-INV/evidence/burn.md",
    ".scratch-INV/evidence/c5.md",
    ".scratch-INV/evidence/c5fix.md",
    ".scratch-INV/evidence/data-refs.txt",
    ".scratch-INV/evidence/dry-run.md",
    ".scratch-INV/evidence/extra-inspection.txt",
    ".scratch-INV/evidence/facts.md",
    ".scratch-INV/evidence/final-workflows-573.json",
    ".scratch-INV/evidence/final-workflows-574.json",
    ".scratch-INV/evidence/final-workflows-577.json",
    ".scratch-INV/evidence/github-0.json",
    ".scratch-INV/evidence/github-1.json",
    ".scratch-INV/evidence/github-2.json",
    ".scratch-INV/evidence/github-3.json",
    ".scratch-INV/evidence/github-4.json",
    ".scratch-INV/evidence/github-5.json",
    ".scratch-INV/evidence/h-desk.md",
    ".scratch-INV/evidence/hazard-history.txt",
    ".scratch-INV/evidence/hz-fable.md",
    ".scratch-INV/evidence/hz-opus.md",
    ".scratch-INV/evidence/jobs-39889527052.json",
    ".scratch-INV/evidence/jobs-40017629350.json",
    ".scratch-INV/evidence/jobs-40022464859.json",
    ".scratch-INV/evidence/jobs-40022464861.json",
    ".scratch-INV/evidence/log-120205782758.txt",
    ".scratch-INV/evidence/log-120650324346.txt",
    ".scratch-INV/evidence/log-573-fences.txt",
    ".scratch-INV/evidence/main-state.txt",
    ".scratch-INV/evidence/merge-review.md",
    ".scratch-INV/evidence/pass1.md",
    ".scratch-INV/evidence/pr-527.md",
    ".scratch-INV/evidence/pr-535.md",
    ".scratch-INV/evidence/pr-542.md",
    ".scratch-INV/evidence/pr-544.md",
    ".scratch-INV/evidence/pr-547.md",
    ".scratch-INV/evidence/pr-565.md",
    ".scratch-INV/evidence/pr-567.md",
    ".scratch-INV/evidence/pr-573.md",
    ".scratch-INV/evidence/pr-574.md",
    ".scratch-INV/evidence/pr-575.md",
    ".scratch-INV/evidence/pr-576.md",
    ".scratch-INV/evidence/pr-577.md",
    ".scratch-INV/evidence/prep.md",
    ".scratch-INV/evidence/refs.txt",
    ".scratch-INV/evidence/remote-report-paths.txt",
    ".scratch-INV/evidence/validity.md",
    ".scratch-INV/evidence/workflows-0.json",
    ".scratch-INV/evidence/workflows-1.json",
    ".scratch-INV/evidence/workflows-2.json",
    ".scratch-INV/evidence/workflows-3.json",
    ".scratch-INV/evidence/workflows-4.json",
    ".scratch-INV/verification.log",
    ".scratch-INV/verify_inventory.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "slot and launch-contract rulings",
        "action": "needs_ruling"
      },
      {
        "row": "read-only desk evidence reconciliation",
        "action": "start_now"
      },
      {
        "row": "registration cold gate",
        "action": "wait_for",
        "wait_for": "complete slots, final integration and laptop suite"
      },
      {
        "row": "first claim t0",
        "action": "wait_for",
        "wait_for": "registration commit, disk recovery, reviewed pin and own passing smoke"
      },
      {
        "row": "measurement during this agent report",
        "action": "do_not_start"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "TMPDIR=/private/tmp/by-inv python3 -B .scratch-INV/audit.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Placeholder census: 45 occurrences; 25 unique strings; configs contain none",
          "Six exact disk identities and native window maxima verified; total 224580 seconds"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Six exact disk identities and native window maxima verified; total 224580 seconds"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "TMPDIR=/private/tmp/by-inv python3 -B .scratch-INV/verify_inventory.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Inventory verified: envelope, six rows, slot census, citations, schedule, unchanged HEAD and tracked tree"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^Inventory verified: envelope, six rows, slot census, citations, schedule, unchanged HEAD and tracked tree$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Missing floor/census receipt disposition, test-7 outcomes and production launch-tree ownership remain; future stage1-commit slot needs interface wording, not an invented pre-t0 hash.",
      "needs": "Lead resolves the reported registration/launch decisions before cold gate."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "#573 is CI red; #574 CI is green with red ledger and cold corrections; #577 correction/verification pending; pass-1 last CI has the 387-field defects failure. No suite or measurement run here.",
      "needs": "Close final-head reviews and integrated agreement, then run laptop whole suite and registration cold gate."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "At stated 98 GB only s6 fits P+smoke; s4 needs 118843585614 bytes, plus recovery for retained earlier sessions.",
      "needs": "Lead/operator establishes verified local space recovery and rechecks before each arm."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Requested gh commands could not connect; connected GitHub read tools supplied PR metadata, workflows, jobs and failure logs through 21:20 UTC.",
      "needs": ""
    }
  ]
}
```

## Scheduling matrix

**The first t0 is not ready. The date is still feasible if the lead closes the registration and integration gates over the next few days and restores disk space between sessions.** The registration requires filled slots → laptop whole suite before release-line merges → registration cold gate → registration commit → each sub-pack's fingerprint smoke (`docs/registrations/bytes_pack_v1.md:347`). None of those steps is waived by populated sizing rows. This is a report, not launch authority.

Snapshot: inventory HEAD `82cc9462c515a18cfce25e84c58f1160e4b8fbe1`, detached; pass-1 lane `1c458d71d`; cached main `cd20dac77`. The integrated lane already contains BY-G, BY-C5, BY-LOOP, BAT-3 and BY-TWIN at their recorded heads, but neither audit fix head nor newer main. Exact ancestry is recorded in `.scratch-INV/evidence/ancestry.txt:1`. GitHub snapshots were obtained on 2026-10-23 around 21:00–21:20 UTC (final #573/#574/#577 refresh at 21:20); treat their CI states as observations, not promises about later pushes. The initial worktree was clean; only this report directory was written. No tests, hardware probes, launchctl, measurement, blinded exports, secret keys or claim numerical data were read/run. H/H2 material inspected here is the explicitly authorized non-claim desk material (`.scratch-INV/evidence/bat-ruling.md:8`; `/Users/edr/night-bytes/h2-20261023T144711Z/desk.json:122`).

All durations below marked **estimate** are scheduling allocations, not measured bounds. Native session maxima are calculated bounds from the requested formula. “Mac measurement” means a later clean, lead-controlled session with agents absent; it is never an action authorized by this report.

### Slot census and evidence

State is the state of the **registration text on this tree**, not whether an older report contains a candidate. There are **45 occurrences / 25 distinct bracketed strings**: 21 actual §18 slot names and four explanatory legend patterns. No `⟦…⟧` occurs in the six selected pack JSONs, their campaign files, or recursively in `configs/bytes/`; their draft/null fields still need work. Replay: `.scratch-INV/audit.py:12` and `.scratch-INV/evidence/audit.json:1`. Of the 21 actual slots, **20 remain unfilled; the catalog digest is filled**. Three unfilled prose slots have populated, explicitly draft machine inputs: sizing, disk and clock spans (`configs/b6/registration/sizing_b5.json:920`, `:964`, `:986`, `:988`; other rows below).

| §18 slot / other bracket | Current state and location | Existing evidence that can fill it | Remaining work / owner |
|---|---|---|---|
| Manifest SHA-256 | **Unfilled**, registration `:80`, `:331` | Current `configs/bytes/bytes_manifest.json` hashes to `76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264` (`.scratch-INV/evidence/facts.md:3`). BY-G rederived all ten models (`docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md:110`). | Agent desk: insert final manifest digest, recompute if identity/config edits change the manifest. No new KV run merely to fill this slot. |
| Manifest table: W, occupied/allocated KV, R | **Unfilled**, registration `:80`, `:331` | BY-G exact W/R/KV/b table at `docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md:115`; per-layer occupied/allocated snapshots are in `configs/bytes/records/*.kv.json`; recorded cache endpoints and recurrent-layer qualifications at `configs/bytes/records/RUN.md:107`, `:119`, `:131`, `:140`. | Agent desk: render the registered table, explicitly distinguish occupied from allocated cache. BY-G's aggregate KV table alone is not every requested cache column. |
| 8B-8bit revision | **Unfilled**, registration `:48`, `:332`; config/roster still pending | Download and group-size-64 verification: `configs/bytes/records/RUN.md:145`; actual revision `48a0b75b1ae72503e21e1558d040bc227510ff06` also in manifest `:90258`. BY-G identifies remaining stale nulls (`docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md:238`); roster null at `configs/campaigns/bytes_v1/roster.json:107`. | Agent desk: fill prose **and** synchronize generator/roster/run configs and dependent config/manifest/pin hashes. No re-download evidenced as necessary. |
| 8B-8bit kept or dropped | **Unfilled**, registration `:55`, `:333` | H desk concludes **kept**, from five successful identifiable, bounded 512-output runs, decode 12.02–12.04 s; not an invented SNR cut (`.scratch-INV/evidence/h-desk.md:347`, especially `:361–373`). Frozen H data is JouleWise-data `8db1b40d6`, `bytes-h-desk-20261022/` (`docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md:73`). | Agent desk + lead adoption of this existing structural result. Its missing F_min diagnostic is separate; do not mistake it for a failed resolvability check. Dropping the model instead changes families/roster and needs a ruling (`docs/registrations/bytes_pack_v1.md:55`). |
| b range | **Unfilled**, registration `:57`, `:334` | **32-fold**: 39,852,331,520 / 1,232,243,840 = 32.34 (`docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md:169–171`). | Agent desk; valid for the retained ten-model roster. |
| R range | **Unfilled**, same locations | **71-fold**, not the draft's pilot-derived 69: 68,690,732,544 / 968,001,536 = 70.96 (same BY-G `:171`). | Agent desk; retain unrounded inputs and registered whole-number rounding. |
| C4 pins | **Unfilled**, registration `:98`, `:335`; evidence **filled-with-draft/limited scope** | `configs/bytes/identity_pins.json:701–703` is `FILE_IDENTITIES_ONLY`, eleven science/reference file identities; BY-G branch `lane/2026-10-22-bytes-c4-pins@683a37534` is already integrated (`.scratch-INV/evidence/ancestry.txt:4`). File hashing follows symlinks, but stack identity is empty / `runtime_stack_unobserved` (`docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md:244–249`). | Agent desk on paused Mac: bind final config inventories, runtime/tokenizer/quantization identity and executed interpreter. Populate the **consumed** shared identity/projection artifacts; the consumer reads `configs/b6/registration`, not automatically `configs/bytes` (`joulewise/b6/driver_lane.py:86–90`). Preserve the distinction between file evidence and observed runtime evidence. |
| P_limit per regime | **Unfilled**, registration `:95`, `:336` | H has phase durations but no F_min/census-power receipts (`.scratch-INV/evidence/h-desk.md:183–185`). H2's long-regime F_min/resolution/outside-power are also null (`/Users/edr/night-bytes/h2-20261023T144711Z/MEASUREMENTS.json:705–729`). Formula is F_min/(4·longest measured **decode phase**), not stream span (`scripts/bytes_gates.py:322–340`). | First agent desk: locate authentic **non-claim phase-floor/census derivation receipts**, as required by `configs/campaigns/bytes_mac_check/README.md:66–73`. No such usable receipts found in inspected H/H2 metadata/reports. If absent, lead specifies the missing physical measurement; cannot quote a defensible duration without that design. Do not use blinded claim floors or borrow ALPHA's floor. |
| Contention measurable or flag only | **Unfilled**, same locations | C5 computes measurability only with the floor/resolution receipt. An absent registered phase line or one below resolution gives flag-only; missing numerical operands are **unavailable**, not a measured below-resolution result (`scripts/bytes_gates.py:326–340`). Registered round-1 CPU alternative is not an adopted exclusion (`:341–366`). | Agent desk + ruling if these missing slots are to be filled by a documented unavailable/flag-only outcome rather than obtaining receipts. Existing w=5.432 and c_q=0.54 in `docs/registrations/block6_replication_DRAFT.md:857` are available prior measurement evidence, not automatically a session-bound BYTES receipt or per-regime floor. |
| Clock-gate values | Prose **unfilled**, registration `:96`, `:337`; six measured T_stream inputs **filled-with-draft** | Six T_stream maxima in sizing at `:920`, `:1025`, `:1130`, `:1235`, `:1340`, `:1434`; derived holds are **51.622227394, 48.651075651, 44.301404992, 34.728521784, 24.564105260, 44.580487778 ppm** (`.scratch-INV/evidence/facts.md:8–13`). | Agent desk: insert/review these candidates and measured-rate provenance; physical precheck again at each launch. Reconcile stale §5's “wait for frequency word” with governing S-7: hold uses measured rate r, word is diagnostic (`scripts/bytes_gates.py:78–91`; `docs/registrations/block6_replication_DRAFT.md:856`; B5 report `.scratch-INV/evidence/b5.md:76`). No new hours-long rate measurement is established merely by this slot. |
| Per-session disk footprint | Prose **unfilled**, registration `:97`, `:337`; P derivations **filled-with-draft** | Six P values and P+smoke below, directly in sizing / BY-SLOTS report. H-DISK form is P=2(B+WAIT)+fixed, **no added reserve** (`scripts/bytes_gates.py:98–115`; `docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md:91`). | Agent desk + gate: replace stale §5's extra **150 GiB** before-arm reserve with the adopted form; keep measured drawdown, planning P and physical free-space receipt distinct. Operator must free actual space. Do not add 150 GiB to these P values. |
| C5 sizing per sub-pack | Prose **unfilled**, registration `:92`, `:337`; six rows **filled-with-draft** | S at sizing `:988`, `:1093`, `:1198`, `:1303`, `:1397`, `:1491`; all measured-margin-complete flags true. H+H2 pools 168 timed observations, soaks 23/12; mean overhead 45.8590246 s (`docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md:57–59`, `:89–92`). | Agent desk/gate: adopt rows and populate §5; update pilot module est_minutes/draft notes. Review source provenance: computing base `1c458d71d`, changed-code hashes, `worktree_changes:true`, H data commit, H2 data_commit null (`configs/b6/registration/sizing_b5.json:989–1021`). These are honest derivation-time records; new commit 82cc does not retroactively change that provenance. |
| Test 7 per long regime | **Unfilled**, registration `:191`, `:338` | H2 now has start **and end** alternating workload/reference stages for 70B, 122B and Next-80B (`/Users/edr/night-bytes/h2-20261023T144711Z/MEASUREMENTS.json:2508–2527`, `:2550–2569`); H alone lacked ends (`.scratch-INV/evidence/h-desk.md:203`). | Agent desk first: compare each regime's start/end drift with reference drift and record outcomes. **No pass verdict found**; collection completion is not transfer validation (`.scratch-INV/evidence/b5.md:80`). A non-passed/not-established outcome keeps the already-registered scale=max(1,E/E_ref,T/T_ref), not an automatic rerun (`docs/registrations/bytes_pack_v1.md:191`). If the lead requires new data: about 16 min/regime plus shared frame, design allowance ~1 h (`docs/design/block6_collection_draft.md:556`; `docs/design/bytes_pack_design.md:156–157`). No numerical pass threshold should be invented. |
| Known-bytes stream test outcome | **Unfilled**, registration `:34`, `:339` | Tool and live procedure exist, but only fake-MLX/synthetic verification is reported (`.scratch-INV/evidence/b5.md:26`, `:81`). H2's stage list contains no companion stream test (`/Users/edr/night-bytes/h2-20261023T144711Z/MEASUREMENTS.json:2444–2592`). | **Mac measurement**, planned **1 h** plus capture/desk setup: concurrent rails and KM003C, explicit above-cache payload B and repeat N, integrate exact RAW-clock span (`configs/campaigns/bytes_mac_check/README.md:28–40`; `docs/design/bytes_pack_design.md:157`). Search bounded receipts first; no completed live outcome found in the named source set. |
| B2 coverage table, counts of 400 and fractions | **Unfilled**, registration `:228`, `:340`; existing table is a **candidate/historical build result** | On-tree `docs/contracts/bytes_tables.md:653–676` has HC3/OLS plain/ruled p03 rates for three worlds/boundaries/fits; e.g. minimum HC3 .9425 = **377/400**. Later NR1 cold-fix report confirms 400 redraws and all DC/rest offset coverage rates 1.0000 (`.scratch-INV/evidence/b2fix.md:207–215`). | Agent desk: reproduce at the final agreeing analysis pin and insert counts **and** fractions. Distinguish this calibration from 20-campaign descriptive coverage. Old NR1 is **already superseded by Addendum 9**, not a fresh unresolved science choice (`docs/contracts/bytes_tables.md:796–800`). |
| B2 estimator SHA-256 at agreeing pin | **Unfilled**, registration `:283`, `:341`; all 18 pass-1 estimator versions null | Current file SHA is `53e2a370f568fcd767607bc3c31cb7a1aab13b3a193b98e65ec31e95dad93894` (`.scratch-INV/evidence/facts.md:5`). It is **not an agreeing pin**: pass-1 defects campaign fails with 387 fields (`.scratch-INV/evidence/log-120205782758.txt:1769`). Older B2 digest `d278…` is at another build (`.scratch-INV/evidence/b2.md:21`). | Agent desk after #573/#574 integration/dispositions: demonstrate §12 agreement across required worlds/stages, hash that exact `joulewise/bytes_analysis.py`, put same 64-hex digest in all three estimators of each pack. Never substitute a Git SHA or the twin's digest. |
| B4 catalog SHA | **Filled**; §18 `:342` deliberately retains the slot name as an index label, Appendix A has its value at `:402` | Current hash **33e1c611…bccb6** equals Appendix A (`.scratch-INV/evidence/facts.md:4`). Old b5bce6… is explicitly historical. | Agent desk only if final merge changes catalog bytes (e.g. #573 adds a disclose code): update hash, effect snapshots and index consistently. Existing “filled” is true on this tree, not a pin for an unknown future merged tree. |
| B4 group key location | **Unfilled**, registration `:243`, `:343` | Code: `<pack_records_root>/bytes/blinding` (`joulewise/b6/blinding.py:102–111`); desk supplies `<loop_root>/packs` (`joulewise/b6/desk_lane.py:197`). B4 report's older concrete root is loop/packs (`.scratch-INV/evidence/b4.md:79`). | Agent desk: use the **selected runtime config**. With BYTES config `configs/b6/loop_bytes.json:3`, intended concrete root is `/Users/edr/night-b6/loop-bytes/packs/bytes/blinding`. Specify it without opening/drawing keys. |
| B4 withheld store path | **Unfilled**, registration `:247`, `:343` | `<pack_records_root>/bytes/withheld/<pack_id>/<session_id>.runs.csv`, sibling to keys (`joulewise/b6/blinding.py:91–98`; `.scratch-INV/evidence/b4.md:24`). | Agent desk: fill parameterized path and actual root, same config decision as above. No need to create or read held-out rows now. |
| B4 missing-store flag code | **Unfilled**, registration `:250`, `:343` | **`bytes.withheld_missing`**, with one-pass/missing behavior already implemented and tested (`.scratch-INV/evidence/b4.md:28–30`; on-tree `joulewise/bytes_analysis.py:753`, `:903`). | Agent desk: insert literal code; preserve the registered non-refusal and one-pass fallback. |
| B4 --stage1-commit | **Unfilled**, registration `:263`, `:343`; build interface exists | `scripts/b6_release_subset.py:21–23` requires a full 40/64-hex commit **at heldout release**; it records it at `:53–56`. B4 synthetic chain makes an actual prediction commit after fit (`.scratch-INV/evidence/b4.md:42–45`). | Agent desk: fill this **interface slot** with the implemented `--stage1-commit <actual stage-1 prediction commit>` requirement. **Ruling if §19 is interpreted as demanding the future actual prediction hash before first t0**: that would be circular; §11 obtains it after collection/fit. Recommendation: register the command/validation rule now, supply actual hash at release. No synthetic hash is production evidence. |
| Legend `⟦MAC: …⟧`, `⟦B2: …⟧`, `⟦B4: …⟧`, `⟦NEEDS_RULING: …⟧` | Explanatory grammar, registration `:6–9`, **not four missing observations** | Their own introductory definitions distinguish them from §18 values. | Agent desk: retain as legend or remove obsolete draft legend at registration; literal grep alone must not miscount these or §18's filled catalog label as unresolved science. |

Above, `BY-G-MANIFEST-REDERIVATION.md` abbreviates `docs/process_traces/2026-10-22-forward/BY-G-MANIFEST-REDERIVATION.md`; `BY-SLOTS-REPORT.md` abbreviates `docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md`. `…/h2-20261023T144711Z` is `/Users/edr/night-bytes/h2-20261023T144711Z`.

### Lane table

| Lane / PR | Observed state / open findings | What it blocks / required landing |
|---|---|---|
| **#573**, `fix/2026-10-22-audit-battery-term@eb31fe385` → `lane/2026-10-22-bytes-battery-term` | Open; absent from pass-1 ancestry. CI **failure**: fences + quick; gate-ledger failure (`.scratch-INV/evidence/workflows-0.json:1`; `.scratch-INV/evidence/jobs-40022464859.json:1`; `.scratch-INV/evidence/pr-573.md:2`). Fences still report stale g2_phase_d / reduce.py estimator pins (`.scratch-INV/evidence/log-573-fences.txt:1171` — search exact “pin g2_phase_d stale”; quick actual failures start `.scratch-INV/evidence/log-120650324346.txt:1723`). Cold Opus delta is **in progress**: compressed-corruption refusal differs; missing/empty/truncated variants still 243 fields above bar (`.scratch-INV/evidence/573delta.md:4`). PR ledger rows remain NOT-RUN (`.scratch-INV/evidence/pr-573.md:18`). | Finish/dismiss each delta finding with evidence, review coverage through fa9744805/eb31 and pin repair at current head; merge into battery-term, then pass-1. Supplies compressed readers, anchor invalidation, B6 claim_usable rule, harvest checkout/registration digests and review rows (`.scratch-INV/evidence/pr-573.md:28–42`). Blocks final archive/claim-path agreement, pin/gate cleanliness and final registration pin. Report's passing focused tests do not constitute final-head green. |
| **#574**, `fix/2026-10-22-audit-twin-parity@9c54ea2ed` → `lane/2026-10-22-bytes-twin-parity` | Open; final refresh at 21:20 UTC: CI **success**, gate-ledger **failure** (`.scratch-INV/evidence/final-workflows-574.json:1`). Latest Opus delta **ADMIT-WITH-CORRECTIONS**: polls-only/non-streaming header → 452 fields above bar; primary pass-mean false “blinded stage” reason; missing reason comparison; duplicate marker computation nit (`.scratch-INV/evidence/574delta.md:30–98`). Earlier rest-intercept ceiling, two-way census and stale-map checks now met (`:16–24`). | Correct/adjudicate these, rerun agreement + output census/coverage and cold deltas; merge into twin-parity, then pass-1. Brings twin BAT-2 arithmetic and expanded comparison of BAT/NR1/Q2 fields (`.scratch-INV/evidence/pr-574.md:26–49`). BAT-3's own cold passes remain separate (`.scratch-INV/evidence/pr-574.md:24`). This is the direct cure for pass-1's current 387-field defects failure, not evidence it is already cured on 82cc. |
| **BY-MERGE / #535**, `lane/2026-10-22-bytes-pass1@1c458d71d`; inventory adds 82cc sizing/C5 fix | Open against main, CI **failure**; only failed job on last lane head is shard 5, `test_defects_campaign`, 387 above bar (`.scratch-INV/evidence/workflows-2.json:1`; `.scratch-INV/evidence/log-120205782758.txt:1727`, `:1769`). Original shard-7 rehearsal conflict was fixed at 1c458 (`.scratch-INV/evidence/pass1.md:98–109`). BY-MERGE-REVIEW's execution never started; it is **not a clean executing review** (`.scratch-INV/evidence/merge-review.md:52–67`). | Merge reviewed #573/#574 lane tips + newer main + reviewed sizing commit into pass-1, resolve overlaps, execute final integration review/agreement/generators/pin checks and laptop whole suite. Do not use old PR body’s initial catalog/SCOPE_BLOCKED language as current state (`.scratch-INV/evidence/pr-535.md:6–10` versus `.scratch-INV/evidence/pass1.md:12`, `:38`). Registration commit and eventual release-line merge need the final tree, not these historical test tails. |
| **#576**, seal-era census | **Merged** `cf03b0f02`; #565/#567 merged after it; absent from inventory ancestry (`.scratch-INV/evidence/ancestry.txt:10–15`; `.scratch-INV/evidence/pr-576.md:2`). Explicit live pins remain enforced; historical seal files are checked at named commits (`.scratch-INV/evidence/pr-576.md:36–44`). | Take newer main into pass-1 before final fences/suite; cures historical-seal blockers without blessing #573's still-stale live reduce.py pins. |
| **#567**, durability | **Merged** `26d8be705`; main source changed `bundle.py`, `interfaces.py`, contract, tests (`.scratch-INV/evidence/pr-567.md:2`, `:26–33`). | Bring from main before measurement pin: temp-file/directory sync and macOS F_FULLFSYNC custody behavior. Final merged tests/reviews still required; real power-loss test was not claimed (`.scratch-INV/evidence/pr-567.md:49–56`). |
| **#565**, meter cross-check | **Merged** `dbba9897c`; slope/intercept diagnostic replaces idle-dominated ratio; its own final pin/CI evidence is in PR record (`.scratch-INV/evidence/pr-565.md:2`, `:28–38`, `:58–64`). | Bring from main: avoids known false meter diagnostics on quiet ~2 W idle; merge its refusal-registry/review coverage correctly with the BYTES branches. |
| **#577**, `fix/2026-10-23-hazard-h1-h5@acbb8c166` → main | Open; CI in progress; ledger skipped at snapshot (`.scratch-INV/evidence/pr-577.md:2`; `.scratch-INV/evidence/workflows-4.json:1`). PR says hazard H1–H5 **must land before next claim window** (`.scratch-INV/evidence/pr-577.md:28`). Both earlier cold passes at b49a9993e were ADMIT-WITH-CORRECTIONS (refusal census, cross-interval PID pinning, H3 false gap, missing-evidence dwell policy and harvest-copy gaps: `.scratch-INV/evidence/hz-fable.md:10–14`; `.scratch-INV/evidence/hz-opus.md:19–99`). Current acbb8c166 is the round-2 correction commit and explicitly labels its **H2 residual bound “to be revised”** (`.scratch-INV/evidence/hazard-history.txt:1`). Local round-2 report reports implemented R1–R7 but pending verification / process-census limitations (`/Users/edr/night-archive/seats-786c/hz-fix/report-r2.md:7`, `:31–50`). | Finish cold Fable+Opus corrections and final verification, then main → pass-1 (or lead-approved equivalent reviewed pin). Blocks next claim window even though not one of the three already-merged main PRs. Do not equate an earlier seat's synthetic passes with final integration. |
| **Already integrated** BY-G #527, BY-C5 #547, BY-LOOP #542, BAT-3 #544, BY-TWIN and BY-REV | Recorded seven merges at `.scratch-INV/evidence/pass1.md:7–23`; ancestry true for current tips (`.scratch-INV/evidence/ancestry.txt:2–6`). #547 head 4d722be8a has CI success (`.scratch-INV/evidence/workflows-3.json:1`); #575 is an older **CI-only, do-not-merge** combination (`.scratch-INV/evidence/pr-575.md:4`). | No redundant remerge of these same tips. Their code is present; final cold/review dispositions still have to cover their integrated behavior. BY-SLOTS report's whole-file sizing-copy blocker is **resolved in this tree**: `tests/b6/test_plan_inputs.py:31–39` now permits BYTES rows while preserving sealed B5 fields. No local rerun claimed. |
| **BY-VALIDITY / other audit reports** | Source audit proposes removing extra twin vetoes/prefixes; timeout semantics require a ruling; required synthetic execution never ran (`.scratch-INV/evidence/validity.md:3`, `:76–96`, `:134–138`). #574 delta explicitly defers that item (`.scratch-INV/evidence/574delta.md:115`). BURN-TRIAGE reports **0 confirmed / 0 refuted**, not 78 reproduced bugs (`.scratch-INV/evidence/burn.md:3`). | Lead must record what remains deferred versus required before certifying registration §12 agreement. Treat source candidates as risk/replay work, not silently completed fixes. Open MUT-BYTES #570 and other mutation PRs are not automatically all pass-1 collection gates; adjudicate relevant confirmed findings instead of waiting on every unrelated open PR (`.scratch-INV/evidence/github-0.json:1`; `.scratch-INV/evidence/burn.md:15`). |

CI source files above live under `.scratch-INV/evidence/`. PR state refs and workflow JSONs are machine snapshots, not tests performed here. The requested `gh pr list …` and `gh pr checks 535 …` both failed with “error connecting to api.github.com”; the connected GitHub plugin supplied equivalent open-PR metadata, commit workflow runs, jobs and failure logs. No approval or network bypass was used.

**Release-line distinction.** Integrating **main into pass-1** is different from merging BYTES/block-6 code **into main**. The B6 registration forbids its code merging to main before B5 release while explicitly permitting pinned-lane collection independent of that release (`docs/registrations/block6_replication_DRAFT.md:506–539`). Do not make B5/L9 numerical release an invented prerequisite to BYTES data collection, or merge #535 into main prematurely. The lead must name the agreeing, reviewed **measurement pin / release-line route** and honor the laptop-suite condition on either route (`docs/registrations/bytes_pack_v1.md:12`, `:317`, `:347`).

### Pack registration and launch-preparation state

All six pass-1 registrations have `status:draft`, three null estimator versions, **13 draft_notes each**, target/minimum 1/1 and the exact same t0 cutoff. All six campaign plan trees have `arm_attachments:{}`, `draft_status:draft`; all six collection plans have `status:draft` (`.scratch-INV/evidence/facts.md:15–20`; representative source `configs/b6/packs/bytes-s1-p1/registration.json:13–45`, `:353–359`; tree `:30`, `:73–88`; collection `:6`). Many notes are stale assertions about already-built C6/C7, missing revision and pilot sizing. Remove/update their generator source as part of finalization, not just six isolated JSON strings (`scripts/bytes_plan_trees.py:138`; `.scratch-INV/evidence/b4.md:98`).

`open_packs` requires a valid, tracked, clean, **registered** file and obtains its commit time; it rejects drafts even if their null versions are draft-valid (`joulewise/b6/pack_registration.py:45–58`, `:133–150`, `:169–193`). Changing status alone fails because null versions cease to be allowed and draft_notes must be absent. The validator only checks a nonempty version string; **registration §13** supplies the stronger file-SHA/agreeing-pin requirement. This is why populated sizing cannot open a pack (`docs/registrations/bytes_pack_v1.md:283`).

The fourteen-binding declaration belongs in **`arm_attachments.launch`**, schema `joulewise.stage_launch_bindings.v1`; names are `repo_root`, `ledger_path`, `claim_runs_root`, `bound_runs_root`, `operator_log_root`, `pre_calibration_dir`, `post_calibration_dir`, `claim_backup_destination`, `bound_backup_destination`, `bracket_session_id`, `pre_attempt_id`, `post_attempt_id`, `identity_epoch_json`, `t1_bindings_json` (`joulewise/night_gate.py:691–698`). The native writer requires exactly those typed declarations and the registered calibration path rules (`joulewise/b5/plan.py:454–488`); it binds their concrete session values later. `plan_inputs.build` supplies roots, identities and sizing; it **does not add the missing tree declaration** (`joulewise/b6/plan_inputs.py:79–120`).

**Who builds it:** BY-PREP-P assigned this to BY-SLOTS / final input binding (`.scratch-INV/evidence/prep.md:172–178`), but the completed sizing work expressly left plan trees untouched (`docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md:92`). Therefore **the lead must assign the remaining BY-PIN/production launch-prep work**; no completed production builder was found. There is an existing **non-claim H-only pattern**: copy the real floor tree's declaration, change root leaves, then construct identity projection (`scripts/bytes_h_session.py:139–155`, `:225`). The native synthetic planner test decorates a temporary tree only (`.scratch-INV/evidence/c5.md:130`). Neither has decorated these six committed production trees. Use reviewed production declarations/identity projections, regenerate all tree/config/projection pins afterward, and keep postcollection closeout fields empty until real receipts exist (`configs/campaigns/bytes-s1-p1/plan_tree.json:53–65`).

The dedicated BYTES runtime configuration is **`configs/b6/loop_bytes.json`**, with root `/Users/edr/night-b6/loop-bytes` and all twelve BYTES pack IDs (`:3–16`, `:28–40`). The default `configs/b6/loop.json:4` admits **only alpha/beta/gamma**, despite listing BYTES in base_order; `Loop._registrations` filters by pack_ids (`joulewise/b6/loop.py:80–82`). The launch owner must select the BYTES config explicitly (`scripts/b6_loop.py:35`, `:49`). This also resolves the concrete custody paths for the two B4 slots. Fresh staging/session IDs are necessary: prepared.json is reused before fresh preparation reads (`joulewise/b6/driver_lane.py:67–83`).

### Ordered punch list

The order below is dependency order; independent desk items can progress concurrently in separate authorized lead-owned lanes. This report delegates nothing and authorizes no edits elsewhere.

| ID | Action / concrete completion evidence | Owner kind | Estimated duration | Dependencies / collision surface |
|---|---|---|---|---|
| P0 | Record the remaining rulings/ownership: missing floor/census receipts vs accepted unavailable outcome; test-7 outcome handling; future stage1-commit interface wording; BY-PIN launch-tree owner; registration clock/disk reconciliation; disposition BY-VALIDITY. | **ruling** | 30–90 min lead time; science follow-up unbounded if new design is needed | First; use slot table authorities. A different floor policy, roster, uncertainty or count predicate cannot be improvised to save time. |
| P1 | Harvest/finish #573, #574 and #577 cold deltas, fix/disposition findings; close each final-head CI and review ledger. Bring #573/#574 to their named owner lanes. | **agent desk**, with lead-owned cold/review gates | **8–24 h estimate**, variable review cycles | P0 for count-changing policy; current blockers in lane table. Can overlap P2/P3. Final authority remains lead. |
| P2 | Adopt the already-computed H+H2 sizing provenance, reproduce six rows, inspect test-7 start/end outputs, convert coverage fractions to counts, fill manifest/revision/ranges/roster slots and restore BAT-RULING authority pointer. | **agent desk** | **3–6 h estimate** | H and H2 metadata already exist. The missing BAT ruling is located on `origin/lane/2026-10-22-battery-assist-audit` (snapshot `.scratch-INV/evidence/bat-ruling.md:1`); current tree absence is recorded in `.scratch-INV/evidence/extra-inspection.txt:5`. Do not remeasure the soaks or KV just because prose is empty. |
| P3 | Locate non-claim floor/census/CPU receipts, calculate per-regime P_limit and measurability; if missing, complete the approved measurement design. Interpret test-7 data with existing scaled fallback. | **agent desk** → **ruling / Mac measurement** if necessary | **1–3 h desk estimate**; physical part **not estimable until scoped** | P0. Cannot derive these from six P/S rows. Existing H2 nulls and README receipt contract cited in slots. This is the least-bounded science prerequisite. |
| P4 | Complete known-bytes companion probe and write integrated boundary outcome. | **Mac measurement** | **1 h programmed experiment**, allow **2 h total estimate** with setup/desk | P0/P3 as needed; code/capture context must be reviewed. No tests/agents or another measurement concurrently. Required by R8.6; protocol at `configs/campaigns/bytes_mac_check/README.md:28–40`. |
| P5 | Build production launch declarations and identity projections; synchronize final roster/revision, shared identity pins and runtime interpreter, trees, collection planning minutes, digest references and dedicated loop config/root. | **agent desk** (paused Mac for file/version attestation) | **3–6 h estimate** | P0 owner assignment; P2/P3/P4 candidate inputs. Current empty attachments and consumed paths above. No model load is shown necessary just to attest existing file hashes. |
| P6 | Integrate audit owner tips + newer main + 82cc sizing into pass-1; resolve shared twin/analysis/harvest/catalog conflicts. Reproduce production-shaped synthetic CLI/withholding chains, agreement at §12, coverage and pin/generator checks; fix remaining scoped failures; record exact agreeing module digest. | **agent desk** | **3–8 h estimate**, plus failed-review repair | P1, P2–P5; no local measurement concurrently. Historical source-only scouts do not satisfy executing review. Recheck scientific arithmetic after merges, not just textual conflict cleanliness. |
| P7 | Populate **all** §18 prose slots; finalize six registered JSONs (SHA versions, no draft_notes), final plan/config/projection bytes and smoke prerequisites. Review every intentionally unavailable outcome and future-interface slot. | **agent desk**, **ruling** where unresolved | **1–3 h estimate** | P6, all physical gaps dispositioned. `docs/registrations/bytes_pack_v1.md:3`, `:283`, `:327–347`; no merely-empty “registered” flip. |
| P8 | Run the **whole suite on the laptop** on final integrated candidate, quiet from measurement; resolve failures and record exact tree/tail; final CI/review ledger green. | **agent desk** / laptop verification | Reserve **8–12 h estimate**; not a timing measurement or assurance of pass | **After all slots filled, before release-line merges**, before cold gate. Required by §19; no suite run by inventory. Historical 387-field failure and #573 CI are material; report-era sizing assertion has already been fixed. |
| P9 | Cold-gate the complete registration and final integrated evidence; fix/adjudicate any remand before adoption. | **cold gate** | **2–6 h estimate**, remands extra | P7/P8; R8.8 (`docs/design/bytes_pack_design.md:160`) and §19. A cold pass of one fix is not this registration gate. |
| P10 | Lead commits the gated registration before first t0; records final measurement pin; verifies clean committed packs can open; merges to release line only when its separate B5/release conditions permit. Prepare fresh measurement checkout/ledger state. | **agent desk** / lead-owned commit | **30–90 min estimate** | P9. Must avoid an extra post-smoke code commit, which changes fingerprint. B6 §7 allows pinned-lane collection without B5 unblinding. |
| P11 | Recover genuine local free space, preserve immutable evidence/ledger captures, establish verified backup/offload/compression route and physical byte receipts. | **agent desk** / operator storage work | **1–4 h estimate**, bandwidth-dependent; repeated between sessions | Can begin now using separately authorized storage work; **no deletion/offload performed here**. Reach each P+smoke requirement, largest 118,843,585,614 B, and repeat after accumulated writes. Cannot count purgeable/cloud placeholder sizes as free allocated space. |
| P12 | For each s1…s6: precheck → its passing fingerprint smoke → notice/install/handoff → full session → structural/desk closeout before next arm. | **Mac measurement** | Smoke budget **75 min** each; native maxima below; **90 min** handoff estimate after each | P10/P11. No agent during collection. Smoke and full collection use separate non-claim/claim custody and ledger. §13.1 structural gate before next pack (`docs/design/block6_collection_draft.md:541`). |

For an early launch with the stated Mac availability, a **conditional** prep allocation is: P0/P2/P3 start Oct 23 afternoon; P1 fix/review work in parallel where possible; P4 takes a separate clean Mac interval; finish P5–P7 by Oct 24 evening; reserve overnight/next morning for P8 and P9; P10/P11 complete by **Oct 25 noon PDT**. This is an estimate with **no promised bound on P3 science work or cold-gate remands**. The calendar below demonstrates available capacity if that gate-ready milestone is met; it is not permission to arm.

### Fingerprint smoke, per sub-pack

A passing smoke matches code commit, OS build, model file hashes, runtime versions, boot session, meter device, powermetrics binary and pack/tree identity (`joulewise/b6/fingerprint.py:32–60`). No previous passing entry for that **same pack**, any differing field, or a null field makes smoke due (`:75–99`). The design specifically requires this for each new sub-pack's first session (`docs/registrations/bytes_pack_v1.md:347`; `docs/design/block6_collection_draft.md:540`).

| Pack | Reduced science + references (each run kept once) | Total runs | Evidence |
|---|---|---:|---|
| s1-p1 | 1.7B, 4B, start reference, end reference | 4 | `configs/b6/smoke_keep.json:2–7` |
| s2-p1 | 8B, 30B-A3B, start/end | 4 | `:14–19` |
| s3-p1 | 14B, Next-80B, start/end | 4 | `:26–31` |
| s4-p1 | 32B, 8B-8bit, start/end | 4 | `:38–43` |
| s5-p1 | 70B, start/end | 3 | `:50–54` |
| s6-p1 | 122B, start/end | 3 | `:60–64` |

Each smoke also needs opening/closing captures, same sealed code/production launch route/census/keep-awake context, copied ledger and separate roots; no corpus/bound derivation/midpoint/quads. It is followed by non-claim harvest, acceptance, analysis dry-run/expected outcome and independent recompute (`docs/design/block6_collection_draft.md:101–142`, `:156–159`; actual preparation `joulewise/b6/smoke.py:239–266`). The design gives **25–30 min measurement path + ~20 min harvest + 10 min other desk = ~55–60 min total**, with notice's 30 min overlapping. These are generic estimates, not measured BYTES-specific smoke timings; this schedule allocates **75 min per pack** including precheck/preparation margin (`docs/design/block6_collection_draft.md:119–142`; `.scratch-INV/evidence/facts.md:21`).

**Sharing:** two science models **within** s1–s4 already share the pack smoke. **One passing smoke cannot cover another sub-pack** because pack/tree is fingerprinted; the current fixed-pack driver also requires exactly one pack (`joulewise/b6/driver_lane.py:67–69`). A smoke can precede its full session in one unattended reservation, but remains a separate non-claim run with a copied ledger, not the claim session or its first units. Combining six smokes into one new pack/session would change the contract and need reviewed implementation/ruling; there is no present runtime evidence for that shortcut (`joulewise/b6/fingerprint.py:81–95`; `joulewise/b6/smoke.py:255–263`).

### Session maxima and disk

For each row compute `60 × ceil((ceil(S) + 3300 + 7200 + 7200)/60)` seconds. The source constants/writer are `joulewise/b5/plan.py:59–67`, `:813`, `:917–918`; the six source S/T values are the sizing pointers in the slot table. Exact disk and time calculations are in `.scratch-INV/evidence/facts.md:8–14` and replayed by `.scratch-INV/audit.py:25–44`.

| Pack | S seconds | Native maximum | P bytes | Retained smoke share bytes | Precheck P + smoke bytes |
|---|---:|---:|---:|---:|---:|
| s1-p1 | 19,217.679471871463 | **10 h 16 m** | 100,708,038,301 | 1,940,464,247 | 102,648,502,548 |
| s2-p1 | 20,205.635101731605 | **10 h 32 m** | 103,361,317,803 | 2,025,369,191 | 105,386,686,994 |
| s3-p1 | 21,639.34651295436 | **10 h 56 m** | 106,723,453,361 | 2,132,957,528 | 108,856,410,889 |
| s4-p1 | 23,229.354256286348 | **11 h 23 m** | 116,400,948,249 | 2,442,637,365 | 118,843,585,614 |
| s5-p1 | 19,051.636769862467 | **10 h 13 m** | 103,526,640,643 | 2,538,324,402 | 106,064,965,045 |
| s6-p1 | 14,846.686081818749 | **9 h 03 m** | 80,606,699,913 | 1,621,526,772 | 82,228,226,685 |

Total native maxima **62 h 23 m**. These reserve full T0/pause/WAIT allowances; do not add them again. Native maximum is not an end-to-end bound on terminal desk work, backups, compression, offload or review. P is a space requirement, **not an observed future disk consumption**; the smoke share excludes smoke fixed files and can still waste a smoke before a subsequent physical refusal (`.scratch-INV/evidence/prep.md:119`; `docs/process_traces/2026-10-23-magistrate-786c0858/BY-SLOTS-REPORT.md:18`).

At the user's approximate **98 GB = 98,000,000,000 B**, only s6 currently fits P+smoke. The largest s4 requirement is **20,843,585,614 B above** that starting figure, even before retaining earlier sessions. If “98” means **GiB**, free would be 105,226,698,752 B: s1 also fits, but s2–s5 still do not (`.scratch-INV/evidence/facts.md:29`; table arithmetic). No fresh free-space probe was performed. A continuous six-session schedule requires verified between-session space recovery or substantially more initial space; summing six planning budgets is not a measured capacity forecast. Recheck every physical device, not Cloud free disk (`joulewise/b6/session_paths.py:61–78`).

Disk ascending order is **s6, s1, s2, s5, s3, s4**. It gets the only immediately affordable candidate first, **after all registration prerequisites**, but deviates from the registered s1…s6/base-order sentence (`docs/registrations/bytes_pack_v1.md:88`; `configs/b6/loop_bytes.json:4–16`). Recommendation: restore disk and keep the registered order below. If the lead wants s6 first, record that scheduling ruling/config change before the cold gate; disk convenience is not implicit authority. No order removes the later disk requirement.

### Feasible back-to-back calendar (conditional)

All times below are **PDT, UTC−07**, Oct 25–28. Prerequisite: **registration cold gate passed and commit/launch prerequisites complete by Oct 25 12:00 PDT**, with genuine disk availability restored before each smoke. Reserve 75 min for each precheck/smoke/desk/notice and 90 min after each native maximum for structure/desk/backups/compression/offload/next preparation. The 90 min is a planning allocation, not a verified offload throughput; H's historical desk was about 1.05 h (`.scratch-INV/evidence/h-desk.md:221`). Every slip moves later rows; no concurrent measurement/agent work is assumed. Calculated calendar: `.scratch-INV/evidence/facts.md:21–28`.

| Pack | Precheck/smoke starts | Claim t0 | Native latest end | Structure/desk/storage gap ends |
|---|---|---|---|---|
| s1-p1 | Oct 25 12:00 | **Oct 25 13:15** | Oct 25 23:31 | Oct 26 01:01 |
| s2-p1 | Oct 26 01:01 | **Oct 26 02:16** | Oct 26 12:48 | Oct 26 14:18 |
| s3-p1 | Oct 26 14:18 | **Oct 26 15:33** | Oct 27 02:29 | Oct 27 03:59 |
| s4-p1 | Oct 27 03:59 | **Oct 27 05:14** | Oct 27 16:37 | Oct 27 18:07 |
| s5-p1 | Oct 27 18:07 | **Oct 27 19:22** | Oct 28 05:35 | Oct 28 07:05 |
| s6-p1 | Oct 28 07:05 | **Oct 28 08:20** | Oct 28 17:23 | Oct 28 18:53 |

The cutoff is the **literal offset-qualified `2026-11-02T00:00:00-08:00`**, not the older main-state prose's “PDT” label. It equals **Nov 2 08:00 UTC**; the example's last t0 is **2026-10-28T15:20Z**, leaving **112 h 40 m** until the cutoff. The cutoff applies to **t0**, not finishing by midnight, and does not itself guarantee a counting session (`docs/registrations/bytes_pack_v1.md:88`; pack registration `:354–357`).

For this s1…s6 order and these 75/90 min allocations, last t0 is gate-ready + **68 h 20 m**. Thus the mathematical latest gate-ready time is **strictly before Oct 30 04:40 PDT** (Oct 30 11:40 UTC; fixed −08 representation Oct 30 03:40), with **zero contingency**. Earlier readiness is strongly preferable; a new cold-gate remand, missing floor experiment or structural failure can consume days. This latest-start bound budgets only five preceding full sessions, because the sixth needs only to start before the cutoff (`.scratch-INV/evidence/facts.md:28`).

### Evidence-source map and limitations

Remote `git show` excerpts are preserved verbatim (original line numbers) under `.scratch-INV/evidence/`: `prep.md` = `origin/report/2026-10-22-by-prep-p@df851462d:.codex-report/BY-PREP-P.md`; `merge-review.md` = `origin/report/2026-10-22-by-merge-review@d0756e055`; `validity.md` = `origin/report/2026-10-22-by-validity@a6375ac04`; `h-desk.md` = `origin/lane/2026-10-22-bytes-h-desk@1b35c555e:docs/process_traces/2026-10-22-forward/BY-0-H-DESK.md`; `pass1.md` = `origin/lane/2026-10-22-bytes-pass1@1c458d71d:.codex-report/bytes-pass1-merge.md`; `c5.md/c5fix.md` = `origin/lane/2026-10-22-bytes-c5-gates@4d722be8a` reports. Full cached origin ref census is `.scratch-INV/evidence/refs.txt:1`; report-path search index is `.scratch-INV/evidence/remote-report-paths.txt:1`.

JouleWise-data snapshots: `b2.md` = `origin/codex/bytes-b2-report@b043466:reports/bytes-b2/REPORT.md`; `b2fix.md` = `origin/codex/bytes-b2-nr1-coldfix@e8f8ac5:reports/bytes-b2-nr1-coldfix/REPORT.md`; `b4.md` = `origin/codex/bytes-b4-report@cb07c8e:reports/bytes-b4/REPORT.md`; `b5.md` = `origin/codex/bytes-b5-report@111ed1d`; `574delta.md` = `origin/claude/cold-delta-574b-opus@cbb3a40:report.md`; `574fable.md` = `origin/claude/cold-delta-574-fable@e682dde`; `573delta.md` = `origin/claude/cold-delta-573d-opus@d7197c3:report.md`. `hz-fable.md` / `hz-opus.md` are `origin/claude/cold-hz-h1h5-{fable,opus}` at the refs in `.scratch-INV/evidence/data-refs.txt:1`, both `report.md`. H's frozen independent measurements/report are at data commit **8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b**; H2's current desk metadata has no data commit assigned in sizing provenance (`configs/b6/registration/sizing_b5.json:1005`, `:1013`). The detailed BY-SLOTS derivation/fixed-desk-decision scripts still exist in the by-slots worktree, though not in this worktree's absent `.scratch-SLOTS` (`.scratch-INV/evidence/extra-inspection.txt:2–4`).

`pr-N.md` snapshots begin with source URL and exact observed refs. Workflow files `workflows-0..4.json` correspond respectively to #573, #574, #535, #547 and #577 heads. Final 21:20 refresh (`.scratch-INV/evidence/final-workflows-573.json:1`, `.scratch-INV/evidence/final-workflows-574.json:1`, `.scratch-INV/evidence/final-workflows-577.json:1`) leaves #573 red, #574 CI green with red ledger, and #577 running. Supporting CI logs establish failures at those particular heads; no local suite was substituted. `dry-run.md` and `burn.md` explain why old report-only work is not executing/cold evidence. No report was interpreted as permission to read blinded B5/B6 data.

## Critical path

- **Missing physical receipt decisions + known-bytes outcome → all slots → final integration agreement/digest → finalized pack/tree inputs → laptop whole suite → registration cold gate → committed measurement pin → six pack-specific smokes/t0s.** The ordering authority is `docs/registrations/bytes_pack_v1.md:347`; existing rows supply only three slot families, not this chain.
- **#573/#574/#577 review dispositions and final-head checks → integrated pass-1 verification.** #574's battery twin closes the current defects failure; #573 changes ingress/export/readers and still has live pin failures; #577 is explicitly required before a claim window (`.scratch-INV/evidence/pr-577.md:28`). BY-VALIDITY's deferred count semantics must receive an explicit lead disposition rather than being hidden by nominal green worlds (`.scratch-INV/evidence/574delta.md:115`; `.scratch-INV/evidence/validity.md:134`).
- **Final tree/config/roster → identity projection and file digests → registered estimator digest/clean commits → fingerprint smoke.** Any later code/pack change invalidates the previous smoke (`joulewise/b6/fingerprint.py:54–60`, `:93–99`).
- **Space recovered and authenticated storage route → each smoke and full arm → immutable closeout/space recovery → next arm.** Current 98 GB cannot support the registered first pack or s4; 90-minute handoffs are assumptions, not storage evidence. Structure of each first claim session must be checked before the next pack (`docs/design/block6_collection_draft.md:541`).

The principal deadline risks are **unbounded floor/census evidence work**, more #573/#574 or registration cold remands, inability to reclaim local allocated space without violating custody, smoke/fingerprint churn after late commits or reboot, agent/census collisions, and a first-session structural failure needing fix/review/new smoke. The six native maxima themselves fit comfortably. The exact next lead step is **P0 plus P1/P2/P3 desk intake**, using the located evidence; no new soak, KV generation, launch or measurement is justified merely by an empty prose slot. If gate-ready slips past **Oct 30 04:40 PDT**, this particular conservative calendar no longer puts all six t0s before the cutoff; do not quietly extend the date or change allowances (`.scratch-INV/evidence/facts.md:28`; `docs/registrations/bytes_pack_v1.md:88`).
