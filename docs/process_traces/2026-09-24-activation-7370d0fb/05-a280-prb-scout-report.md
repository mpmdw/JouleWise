```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Read-only inventory at 2ea6a7ec: PR B has additional idle-specific paths beyond the PR A lens, and the later integration synthesis changes several packet B requirements.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "exact",
    "head_start": "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b",
    "head_end": "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b",
    "upstream_end": "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "PR B implementation brief",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "shared night preparation, gate, installer, driver, courier and zero-capture paths"
      },
      {
        "row": "PR B implementation",
        "action": "wait_for",
        "wait_for": "A291 public interface and importer inputs named in the cited contracts",
        "collision_surface": "roster sequencing and scored records"
      },
      {
        "row": "bench dry run",
        "action": "wait_for",
        "wait_for": "PR B",
        "collision_surface": "production preparation through courier path"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD refs/remotes/origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b",
          "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b"
      }
    },
    {
      "id": "V2",
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
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only scout; no tests or live measurement were run.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The sources retain the open questions and conflicting earlier wording listed in T6.",
      "needs": "Keep them explicit in the brief; obtain rulings where implementation depends on them."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| PR B brief | start_now | — | Shared night paths listed in T1 |
| PR B implementation | wait_for | A291’s contract interface and importer inputs | Roster and scored custody |
| Bench dry run | wait_for | PR B | Preparation through courier |

## Critical path

PR A is merged; A280’s queue row places PR B next ([TASK_QUEUE.md:900](</Users/edr/code/wt-7370d0fb-a280scout/TASK_QUEUE.md:900>)). The recorded order is PR B → bench dry run → bench token pilot → registration packet and cold gate → shakedown and sizing receipt → headline nights ([19-headline-integration-synthesis.md:32](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:32>)).

## T1. Call-site inventory at `2ea6a7ec`

“Reads table” below distinguishes a lookup from selecting the **candidate’s** kind. The S3 list comes from [29-a280-pra-opus-lens.md, S3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-d8cc9c0a/29-a280-pra-opus-lens.md>).

| S3 site | Current idle assumption | Reads PR A table? |
|---|---|---|
| `locations` | Uses the idle prefix and measurement-root suffix for every generated path ([evidence_night.py:158](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:158>)). | **Yes**, through fixed `KIND`, not an input kind. |
| `prior_records` | Searches staging and custody with the idle plan-id prefix ([evidence_night.py:219](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:219>), [evidence_night.py:233](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:233>)). | **Yes**, through fixed `KIND`. |
| `sealed_candidate` | Selects the idle row in the caller and H-side snippet; imports its manifest module, requires the QPE registration digest, and checks `EVIDENCE_*` wrapper literals ([evidence_night.py:241](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:241>), [evidence_night.py:248](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:248>), [evidence_night.py:263](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:263>), [evidence_night.py:275](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:275>)). | **Yes**, but selects the idle row. |
| `notice_subject` | Prints `EVIDENCE` and the idle row’s receipt class ([evidence_night.py:296](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:296>)). | **Yes**, through fixed `KIND`. |
| `render_notice` | Reads idle protocol keys for the envelope schedule and non-observer rule ([evidence_night.py:300](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:300>), [evidence_night.py:310](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:310>)). | **Yes**, but selects the idle row. |
| Census snippet | Classifies against the idle receipt class in H, with an idle fallback ([evidence_night.py:1026](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:1026>), [evidence_night.py:1035](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:1035>), [evidence_night.py:1050](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:1050>)). | **Yes**, but selects the idle row. |
| `notice_unused` | Searches attempts under the idle date prefix ([evidence_night.py:1658](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:1658>)). | **Yes**, through fixed `KIND`. |
| `render_notice` idle-only sentences | The row supplies intro, envelope noun, work and follow-up; surrounding unconditional text describes the idle busy-core exclusion and abort, read-only `git show`, and results publication ([evidence_night.py:323](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:323>), [evidence_night.py:332](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:332>), [evidence_night.py:334](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:334>), [evidence_night.py:341](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:341>)). | **Partly**; four phrases come from the row. |
| Corecaptured t0 notice sentence | Always says the t0 log check runs, regardless of the row’s `corecaptured_at_arm_and_t0` flag ([evidence_night.py:340](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:340>)); the gate itself follows that flag ([night_gate.py:1541](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1541>)). | **No flag read** in notice. |

**NEW sites found by the wider grep:**

- **Preparation ownership:** `KIND` is initialized to the idle row; `prepare` refuses any other kind, while `candidate_state` requires the saved kind to equal `KIND` ([evidence_night.py:28](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:28>), [evidence_night.py:371](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:371>), [evidence_night.py:586](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:586>)). `sealed_state` expects `evidence_manifest.json` and invokes the idle-bound sealer ([evidence_night.py:612](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:612>), [evidence_night.py:635](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:635>)).
- **Wrapper generation:** `generate` selects the idle row, its manifest and executor; its exports and wrapper use `EVIDENCE_*` names ([gen_evidence_night.py:20](</Users/edr/code/wt-7370d0fb-a280scout/scripts/gen_evidence_night.py:20>), [gen_evidence_night.py:39](</Users/edr/code/wt-7370d0fb-a280scout/scripts/gen_evidence_night.py:39>), [gen_evidence_night.py:55](</Users/edr/code/wt-7370d0fb-a280scout/scripts/gen_evidence_night.py:55>)). This is an idle-specific generator today, although preparation calls its script from the selected row ([evidence_night.py:545](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:545>)).
- **Gate registration:** the table drives chain-source authentication and both t0 predicates ([night_gate.py:1388](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1388>), [night_gate.py:1541](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1541>), [night_gate.py:1583](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1583>)), but the ruled registration entries shown here carry the QPE-specific digest and labels ([night_gate.py:69](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:69>), [night_gate.py:95](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:95>), [night_gate.py:108](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:108>)). The registration check authenticates `chain_source_sha256` but does not compare a registration `payload_kind` to C5 ([night_gate.py:1700](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1700>)).
- **Installer and probe:** non-idle payloads take the calibration path in receipt validation and render inspection ([night_agent_install.py:793](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_agent_install.py:793>), [night_agent_install.py:1164](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_agent_install.py:1164>)). The driver’s verify-only worker likewise dispatches only the idle literal to the evidence probe ([run_night.py:3690](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:3690>)).
- **Driver and courier:** the artifact inventory names idle evidence files and walks only `night/evidence` ([run_night.py:1029](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:1029>), [run_night.py:1037](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:1037>)); courier text is conditional on `evidence_cleanup.json` ([run_night.py:1218](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:1218>)); cleanup repair checks the idle C5 literal and idle outcome file ([run_night.py:1324](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:1324>), [run_night.py:1344](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:1344>)). The prompt names only quiet-predicate evidence outputs ([NIGHT_COURIER_PROMPT.md:46](</Users/edr/code/wt-7370d0fb-a280scout/docs/process/NIGHT_COURIER_PROMPT.md:46>)).
- **Zero capture:** `zero_capture_facts` rejects a third payload literal and examines idle evidence directories and the idle envelope index ([zero_capture_facts.py:99](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/zero_capture_facts.py:99>), [zero_capture_facts.py:120](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/zero_capture_facts.py:120>)); watchdog release consumes its `.clean` result ([magistrate_watchdog.py:817](</Users/edr/code/wt-7370d0fb-a280scout/scripts/magistrate_watchdog.py:817>)).
- **Idle executor boundary:** `quiet_predicate_campaign.manifest_for` and `verify_manifest` expressly require the idle protocol and payload ([quiet_predicate_campaign.py:147](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/quiet_predicate_campaign.py:147>), [quiet_predicate_campaign.py:167](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/quiet_predicate_campaign.py:167>)). These are existing idle functions, not shared-kind dispatch.

## T2. Kind table

The immutable `NightKind` schema and `NIGHT_KINDS` mapping are in [night_kinds.py:24](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:24>) and [night_kinds.py:48](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:48>). A row carries: kind; plan prefix and root suffix; chain source and protocol paths; receipt class and window maximum; manifest function/module, generator script and executor module; chain authentication and registration-binding flags; corecaptured and non-observer flags; payload-kind flag; and four notice phrases ([night_kinds.py:25](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:25>)). The idle row gives concrete examples; calibration deliberately has null preparation fields and false evidence flags ([night_kinds.py:49](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:49>), [night_kinds.py:71](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:71>)).

For a scored payload to be recognized, its row needs `payload_kind=True` ([night_gate.py:150](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:150>)). For its t0 corecaptured and non-observer checks to run, it needs both predicate flags **and** `authenticate_chain_source=True`: C5 records `payload_kind` only in that authentication branch, and C3 reads the recorded value ([night_gate.py:1388](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1388>), [night_gate.py:1401](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1401>), [night_gate.py:1541](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1541>), [night_gate.py:1583](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1583>)); [final pass Q3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-d8cc9c0a/43-a280-pra-fable-final-pass.md>) calls out that coupling. A chain-bound scored registration also needs the row’s `requires_chain_bound_registration` flag and a ruled binding ([night_gate.py:1708](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1708>), [night_gate.py:1716](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1716>)). Packet B requires those two machine predicates for both evidence kinds ([09-headline-packet-b-scored-night.md §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md>)).

## T3. Runner obligations, verbatim

FT-9, [21-coldgate-fable-addendum-ruling.md:74](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:74>):

> **FT-9 (runner-lane obligation row, added to the CARRIED list as a non-field row).** "Runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; if it cannot, the runner reports `r+1` with every block `not_started`."

The requested CARRIED fields, the other runner-consumed field, and the obligation row, exactly as printed in [02d-a291-contract-v4-self-contained.md §7](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:672>):

```text
| `sizing_receipt_sha256` | CARRIED | scored-night arm gate (runner lane) | 45/10 §Q2 |
| `ceiling_s` | CARRIED | runner, kill timeout | 45/10 §Q2; Q17 |
| `scorer_id` | CARRIED | A292 and the runner | 45/10 §Q2 |
| `envelope_s`, `offset_s`, `pitch_s` | CARRIED | runner lane | 45/21 §7(G) |
| Runner sequencing | obligation | «Runner lane: envelope `r+1` does not start until `requeue_overrun` for `r` has returned and its roster is loaded; if it cannot, the runner reports `r+1` with every block `not_started`.» | FT-9 |
```

The same section states verbatim: “Every CARRIED row is a mandatory CONSUMED row in its consumer lane's gate.” ([02d-a291-contract-v4-self-contained.md:696](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:696>)). Section 3 gives the public `pack`, `requeue_overrun`, `verify_executed_roster`, and `executed_status` contracts to consume; the branch implementation is not the interface authority ([02d-a291-contract-v4-self-contained.md:267](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:267>), [02d-a291-contract-v4-self-contained.md:285](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:285>), [02d-a291-contract-v4-self-contained.md:367](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:367>)).

## T4. Condensed design inputs

1. Reuse the idle capture instrument and executor skeleton with a **separate model worker**. Prepare/load/warm up before capture; begin no envelope with an unready worker; write item records after recorder stop ([packet B §2](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:45>), [packet B §4](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:81>), [synthesis §1 M13](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:23>)).
2. Run **one thinking arm per night**, with pinned decoding/rendering, model identity, tokenizer and template; preserve the model artifact tree digest ([packet B §§2–3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:67>), [synthesis §1 M13](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:23>)).
3. Pin the registration, chain source, manifest, roster, selected items, prompts, scorer, model identities and capture parameters; authenticate the scored kind at arm and t0 ([packet B §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:71>)).
4. Use **gross energy between each block’s outer item edges** for the claim numerator. Offset, tail and unused capture are outside it; idle reference is a covariate ([synthesis §1 M7](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:17>); packet B’s frame/window record and synthetic-frame regression specify complete support and exact integration ([packet B §§4–5](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:81>)).
5. Keep immutable per-item identities, responses, token ids, markers, session id, envelope index, raw power/session files, exclusions and support flags; reject incomplete power-frame support over the scored window ([packet B §§2, 4–5](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:69>)).
6. Spread each model × arm × level cell across **at least five paired blocks in five distinct envelopes**; keep membership identical across models and block size per arm. No two blocks of a cell share an envelope ([synthesis §1 M8](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:18>)).
7. Retry an overrun block once as a block, then in single-problem envelopes; preserve long problems and use the ruled `requeue_overrun` interface and FT-9 sequencing ([synthesis §1 M12](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:22>), [02d §3.2](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:285>), [FT-9](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/15-coldgate-packet-a291-contract/20-addendum/21-coldgate-fable-addendum-ruling.md:74>)).
8. Keep **scorer authority at the desk**, reducing immutable night rows. Courier counts and numbers are PROVISIONAL; the desk reducer recomputes claim values ([synthesis §1 M11](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:21>), [packet B §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:78>)).
9. Keep the energy rail and floor identity consistent with Paper B’s pins; otherwise remeasure floors ([synthesis §1 M13](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:23>)).
10. Preserve the stated exclusions, worker cleanup, zero-capture facts, courier outputs and artifact custody; cover authentication, pins, isolation, frames, spread, retries and provisional labels in production-path regressions ([packet B §§2–5](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:69>), [TASK_QUEUE.md A280](</Users/edr/code/wt-7370d0fb-a280scout/TASK_QUEUE.md:900>)).
11. Run the **bench dry run before** the bench token pilot; exercise preparation, fixture arm check, render, driver, chain, MLX worker, harvest, scoring, summary and courier without live powermetrics ([packet B §6](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:106>), [synthesis §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:32>)).
12. Preserve the downstream inference boundary: block-aware paired bootstrap, floor/anchor widening, two Holm families, a guarded crossover definition, and descriptive-only J/token ([synthesis §1 M9–M10](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:19>)). These constrain PR B’s evidence and labels even where later lanes calculate the estimates.

## T5. Existing test surface

| Module | Existing acceptance coverage and production path it drives |
|---|---|
| [tests/test_night_kinds.py:216](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_night_kinds.py:216>) | Immutable rows, unknown kind, third-kind recognition and row mutations; drives `night_kinds.kind_row` and `night_gate.probe_payload_kind` ([night_kinds.py:96](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_kinds.py:96>), [night_gate.py:150](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:150>)). Its eight-artifact byte goldens and refusal parity drive real preparation, wrapper generation, sealing and notice rendering ([tests/test_night_kinds.py:249](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_night_kinds.py:249>), [tests/test_night_kinds.py:287](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_night_kinds.py:287>)). |
| [tests/test_evidence_night.py:44](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_evidence_night.py:44>) | Notice wording/bindings, preparation and arm predicates; drives `evidence_night.render_notice`, `prepare` and `check` ([evidence_night.py:300](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:300>), [evidence_night.py:371](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:371>), [evidence_night.py:1317](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/evidence_night.py:1317>)). |
| [tests/test_night_gate.py:359](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_night_gate.py:359>) | t0 corecaptured and registration/payload behavior; drives `night_gate` C5 authentication and C3 flags ([night_gate.py:1388](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1388>), [night_gate.py:1541](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_gate.py:1541>)). |
| [tests/test_gen_evidence_night.py:100](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_gen_evidence_night.py:100>) and [tests/test_quiet_predicate_campaign.py:97](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_quiet_predicate_campaign.py:97>) | Idle wrapper/manifest and executor outputs; drive `gen_evidence_night.generate` and `quiet_predicate_campaign.manifest_for`/executor ([gen_evidence_night.py:20](</Users/edr/code/wt-7370d0fb-a280scout/scripts/gen_evidence_night.py:20>), [quiet_predicate_campaign.py:147](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/quiet_predicate_campaign.py:147>)). |
| [tests/test_night_agent_install.py:1921](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_night_agent_install.py:1921>), [tests/test_run_night.py:4865](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_run_night.py:4865>), [tests/test_zero_capture_facts.py:12](</Users/edr/code/wt-7370d0fb-a280scout/tests/test_zero_capture_facts.py:12>) | Probe receipt/render, driver evidence branch, and zero-capture release facts; drive installer dispatch, driver probe/cleanup and `zero_capture_facts` ([night_agent_install.py:793](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/night_agent_install.py:793>), [run_night.py:3690](</Users/edr/code/wt-7370d0fb-a280scout/scripts/run_night.py:3690>), [zero_capture_facts.py:79](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/zero_capture_facts.py:79>)). |

The PR A final pass records named-module green evidence and the one time-of-day test flake; that is historical verification, not a test run in this scout ([43-a280-pra-fable-final-pass.md Q1](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-d8cc9c0a/43-a280-pra-fable-final-pass.md>)).

## T6. Open questions and source conflicts

- **Energy unit:** packet B describes level-window energy and gross *plus* net reporting; the synthesis names gross **block-edge** energy and rejects net as a peer number ([packet B §2](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:65>); [synthesis §1 M7](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:17>)).
- **Scoring custody:** packet B places scoring additions at harvest and gives the courier accuracy/J-per-correct; the synthesis reserves scoring to a desk reducer and makes courier counts provisional ([packet B §§3–4](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:78>); [synthesis §1 M11](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:21>)).
- **Overrun terminal state:** packet B says a second whole-block overrun becomes `not_estimable`; synthesis M12 sends the work to single-problem envelopes, and the later A291 contract gives detailed transition states ([packet B §2](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:61>); [synthesis §1 M12](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:22>); [02d §3.2](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:285>)).
- **Pilot sequence:** packet B calls the first scored night the 16-item sizing pilot; synthesis M4 places a 16-per-level bench token pilot before a short shakedown night ([packet B §§0, 6](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:11>); [synthesis §1 M4 and §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:14>)).
- **Decoding:** the thinking-on greedy-versus-seeded-sampling choice still calls for the bench determinism result before the pilot ([packet B §7 R3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:119>); [synthesis §2 E3 and §3](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:29>)).
- **Rail and floors:** packet B leaves the rail choice open; synthesis requires matching Paper B’s rail and floor identity or remeasurement ([packet B §7 R7–R8](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:123>); [synthesis §1 M13](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:23>)).
- **Scored successor:** packet B explicitly leaves D-182’s zero-capture successor behavior open; the current fact reader rejects any third payload kind ([packet B §7 R9](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-23-activation-1d3796d5/09-headline-packet-b-scored-night.md:125>); [zero_capture_facts.py:99](</Users/edr/code/wt-7370d0fb-a280scout/joulewise/zero_capture_facts.py:99>)).
- **A291 details visible to PR B:** the self-contained contract labels roster order, split-parent stage, single prediction, float evaluation and executed-status shape unruled or proposed; PR B consumes roster transitions and captured-window keys ([02d §10 X-1–X-5](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:759>); [02d §§3.2, 3.6](</Users/edr/code/wt-7370d0fb-a280scout/docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:285>)).