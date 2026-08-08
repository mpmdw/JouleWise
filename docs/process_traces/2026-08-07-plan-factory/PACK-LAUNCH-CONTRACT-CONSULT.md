# U5-U7 pack launch-command contract — consult response of record (2026-08-07)

Sol xhigh (fast tier), read-only, via scripts/codex-bridge (audit rows in
.codex-bridge/invocation_manifest.jsonl). Resolves MAGISTRATE-DISPOSITIONS
§U5-U7 amendment 3 (the U8/U5-U7 launch-representation contradiction),
ordered resolved in the pack contract BEFORE U5 runs.

**MAGISTRATE ADOPTION (Fable, 2026-08-07): ADOPTED as the pack-contract
amendment.** Each executable stage node in `plan_tree.json` carries a
typed `launch` recipe (`joulewise.stage_launch.v1`): tool_id +
interface_id + typed argv tokens (literal / repo_path / binding /
binding_path / tree_pointer; no interpolation, env tokens, or shell
fragments), with the closed arm-binding vocabulary declared in
`arm_attachments.launch`. `plan_tree.sha256` authenticates the recipes
(no sibling launch_manifest.json). Absolute roots, interpreter/tool
paths, and tool-byte hashes live in the immutable READINESS record; U8's
revised charter materializes each recipe at arm time and requires exact
argv-array equality. Interface-ID indirection means a tool path move
never regenerates packs; an incompatible CLI change requires a new
interface ID and pack regeneration. Anything the consult parked on U8's
two owed Ed rulings stays parked (see memo tail). U5 generation may now
proceed against this contract once Ed's ruling 2 (reported-energy cells)
lands for the hash freeze.

---

## Positions

### 1. Decision

D-117 packs should freeze a **typed, full argv recipe for every executable stage**, not literal machine argv and not merely an entrypoint/config pair.

- Put the recipe directly in each `plan_tree.json.stage_graph[]` node.
- `plan_tree.sha256` therefore authenticates the recipes; do not add a sibling `launch_manifest.json`.
- Freeze tool/interface IDs, argument order, flags, repository-relative config/policy references, and named arm bindings.
- Keep absolute roots, interpreter/tool paths, and tool-byte hashes in the immutable readiness record.
- U8 materializes each recipe and requires exact argv-array equality.

This fills the omission at `DRAFT-U5U7.md:23923-23960` and `FABLE-EXAM-U5U7.md:31-37,183-187` while matching the landed command surface in `window_runbook.md:601-620,644-676,742-748`.

### 2. Why this boundary

An entrypoint/config pair under-freezes material behavior: it cannot detect omission or mutation of `--campaign-policy`, calibration binding, quiet-mode arming, countdown, `--max-failures`, root selection, or log destination.

A digest-only sibling is opaque and provides no decoupling: because its digest must be referenced by `plan_tree.json`, every change still rehashes the tree.

Literal absolute argv in pack bytes would freeze Ed’s checkout, `.venv`, custody, and run-root paths. A pure arm-time attachment would permit U8 to validate only operator-supplied bytes. The typed-recipe/arm-materialization split preserves both prevalidation and machine portability.

Tool paths are deliberately indirect: a pack freezes `tool_id` plus `interface_id`, while readiness supplies the reviewed absolute `argv_prefix` and artifact hashes. A path move or compatible tool fix does not require pack regeneration; an incompatible CLI change requires a new interface ID and pack regeneration.

### 3. Exact pack shape

Every executable stage row gains this exact `launch` member:

```json
{
  "schema_version": "joulewise.stage_launch.v1",
  "commands": [{
    "command_id": "alpha-science-absolute.collect",
    "command_kind": "campaign_collection",
    "argv_template": {
      "tool_id": "campaign_runner",
      "interface_id": "joulewise.run_campaign.cli.v1",
      "arguments": []
    },
    "cwd": {"kind": "binding", "value": "repo_root"},
    "success_exit_codes": [0]
  }]
}
```

No additional keys are allowed. `commands` is ordered and nonempty; closeout stages may contain multiple commands.

Each argument is exactly one of:

```json
{"kind":"literal","value":"--runs-dir"}
{"kind":"repo_path","value":"configs/campaigns/..."}
{"kind":"binding","value":"claim_runs_root"}
{"kind":"binding_path","value":"claim_runs_root","relative":"campaign_log.jsonl"}
{"kind":"tree_pointer","value":"/plan/plan_id"}
```

`repo_path` and `binding_path.relative` must be normalized relative paths without `.` or `..`. `tree_pointer` must resolve to a scalar string in the same captured tree. No interpolation strings, `$NAME`, `${NAME}`, `~`, shell fragments, or environment-variable tokens are permitted.

`arm_attachments.launch` declares the closed binding vocabulary and types, including at least:

- `repo_root`: existing absolute directory.
- `ledger_path`: existing absolute file.
- `claim_runs_root`, `bound_runs_root`: absolute fresh roots with leaves matching `roots`.
- `operator_log_root`, pre/post calibration directories, and claim/bound backup destinations: absolute paths.
- `bracket_session_id`, `pre_attempt_id`, `post_attempt_id`: non-path strings.
- `identity_epoch_json`, `t1_bindings_json`: authenticated absolute files.

U8 must additionally enforce:

```text
pre_calibration_dir =
  claim_runs_root/instrument_validation/pre_attempt_id
post_calibration_dir =
  claim_runs_root/instrument_validation/post_attempt_id
```

That relationship matches landed `validate_powermetrics_fiducial.py`, which names the output directory from the predeclared attempt ID.

### 4. Command-kind examples

Notation below is exact shorthand for the token forms above: `L` = `literal`, `R` = `repo_path`, `B` = `binding`, `BP` = `binding_path`, and `T` = `tree_pointer`.

1. **`bracket_reservation`**

Tool/interface: `bracket_reserver` / `joulewise.calibration_window_bracket_reservation.cli.v1`.

```text
L(--ledger), B(ledger_path),
L(--head-pin), R(configs/calibration/calibration_ledger_head.json),
L(--session-id), B(bracket_session_id),
L(--window-id), T(/window_identity/window_id),
L(--plan-id), T(/plan/plan_id),
L(--plan-sha256), T(/plan/actual_sha256),
L(--evidence-root-id), T(/window_identity/evidence_root_id),
L(--runs-root), B(claim_runs_root),
L(--pre-attempt-id), B(pre_attempt_id),
L(--post-attempt-id), B(post_attempt_id),
L(--pre-custody-locator), B(pre_calibration_dir),
L(--post-custody-locator), B(post_calibration_dir),
L(--identity-epoch-json), B(identity_epoch_json),
L(--t1-bindings-json), B(t1_bindings_json),
L(--execute)
```

2. **`calibration_capture`**

Tool/interface: `fiducial_capture` / `joulewise.powermetrics_fiducial.cli.v1`.

```text
L(--allow-live),
L(--output-root), BP(claim_runs_root,instrument_validation),
L(--session-id), B(bracket_session_id),
L(--slot), L(pre),
L(--attempt-id), B(pre_attempt_id),
L(--power-policy), L(ac_high_power)
```

The post command changes only `pre`/`pre_attempt_id` to `post`/`post_attempt_id`.

3. **`campaign_collection`**

Tool/interface: `campaign_runner` / `joulewise.run_campaign.cli.v1`.

Alpha absolute example:

```text
R(configs/campaigns/d117_floor_qwen25_1p5b_v1/01_phase_decode_absolute),
L(--runs-dir), B(claim_runs_root),
L(--log), BP(claim_runs_root,campaign_log.jsonl),
L(--campaign-policy), R(configs/campaign_policies/quiet_mac_p2_production.json),
L(--instrument-calibration-dir), B(pre_calibration_dir),
L(--instrument-power-policy), L(ac_high_power),
L(--arm-quiet-mode),
L(--arm-countdown-s), L(20),
L(--max-failures), L(1)
```

Bound and reference stages use this identical shape with their exact config directory and the appropriate claim/bound root.

4. **`bound_derivation`**

Tool/interface: `campaign_runner` / `joulewise.run_campaign.cli.v1`.

```text
L(--derive-neg8-drift-bound),
R(configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json),
L(--neg8-drift-bound-output), BP(bound_runs_root,neg8-drift-bound.json),
L(--runs-dir), B(bound_runs_root)
```

5. **`whole_window_verdict`**

Tool/interface: `campaign_runner` / `joulewise.run_campaign.cli.v1`.

```text
L(--whole-window-verdict),
L(--runs-dir), B(claim_runs_root),
L(--log), BP(claim_runs_root,campaign_log.jsonl),
L(--campaign-policy), R(configs/campaign_policies/quiet_mac_p2_production.json),
L(--neg8-drift-bound), BP(bound_runs_root,neg8-drift-bound.json)
```

No `--waivers`, `--environment-override`, `--cli-cmd`, or warning acknowledgement is permitted.

6. **`backup`**

Tool/interface: `backup_runs` / `joulewise.backup_runs.cli.v1`.

```text
B(claim_runs_root), B(claim_backup_destination)
```

A second command substitutes the bound root and bound backup destination.

This produces 14 pack-governed commands for alpha/beta and 13 for gamma, whose missing command is the absolute-floor science stage. U2’s successor probe and U8’s readiness invocation are runbook/bookend interfaces, not campaign-pack commands; keeping them outside pack bytes preserves the intended U2 firewall.

### 5. Readiness-record shape

Replace U8’s underspecified launch-command list with:

```json
{
  "launch_commands": {
    "bindings": {"repo_root": "/absolute/path"},
    "tool_bindings": [{
      "tool_id": "campaign_runner",
      "interface_id": "joulewise.run_campaign.cli.v1",
      "argv_prefix": [
        "/absolute/repo/.venv/bin/python",
        "/absolute/repo/scripts/run_campaign.py"
      ],
      "artifact_pins": [{
        "argv_index": 0,
        "lexical_path": "/absolute/repo/.venv/bin/python",
        "resolved_path": "/absolute/python",
        "sha256": "..."
      }]
    }],
    "commands": [{
      "stage_id": "alpha-science-absolute",
      "command_id": "alpha-science-absolute.collect",
      "argv": ["/absolute/repo/.venv/bin/python", "..."],
      "cwd": "/absolute/repo"
    }],
    "commands_sha256": "..."
  }
}
```

`commands_sha256` is SHA-256 over canonical JSON bytes of `commands`; the readiness receipt echoes it.

The outer operator command is U8-owned rather than pack-hashed. U8 should separately record exact expanded argv, launcher SHA, and plan-root path. The revised runbook should use `/usr/bin/caffeinate`, not PATH-dependent `caffeinate`, while preserving the landed one-command shape at `window_runbook.md:673-676`.

### 6. Arm-time comparison and refusals

U8 should:

1. Strictly validate every recipe during desk validation, including complete command inventory and stage order.
2. Validate every repo reference against the captured clean checkout and the stage’s exact manifest/config relationship.
3. Validate the closed binding map; missing and extra bindings both refuse.
4. Validate paths before expansion: canonical lexical absolute form, no `~`, `$`, `.`/`..`, aliasing, or root-leaf mismatch.
5. Resolve `tree_pointer` and typed paths without invoking a shell.
6. Materialize `expected_argv = tool_binding.argv_prefix + arguments`.
7. Compare expected and supplied `argv`, `cwd`, stage order, and command IDs **exactly**. Do not reorder flags, apply defaults, normalize the supplied command into equivalence, or treat Python aliases as equal.
8. Hash and authenticate tool bytes against the reviewed checkout/environment inventory.

No values are “environment-variable and excluded from the hash.” Binding names and types are pack-hashed; binding values, tool paths, tool hashes, cwd, and materialized argv are readiness-record-hashed.

Mutable roots and repository scripts must not traverse symlinks. Tool executables need a narrower rule: the landed `.venv/bin/python` is itself a symlink chain, so U8 must authenticate both its lexical path and resolved target rather than blanket-refusing it; otherwise every healthy D-117 night refuses.

Refusal vectors are: malformed/extra launch fields; missing, duplicate, or reordered commands; undeclared bindings; unsupported tool/interface; repository escape; config/stage mismatch; policy mismatch; relative or unresolved paths; untrusted tool bytes; argv/cwd mismatch; forbidden flags; retry command inconsistent with `attempt_policy`; and outer-launcher mismatch.

## Disagreements

- I disagree with U8’s earlier “literal absolute values everywhere” wording if applied to pack bytes. Literal absolute values belong in readiness bytes, not the pack.
- I disagree with authenticating launcher implementation bytes from the pack. The pack should authenticate the interface and arguments; U8 authenticates the current reviewed implementation.
- I disagree with a blanket symlink refusal for tool executables because it rejects the landed `.venv/bin/python`.
- A standalone `launch_manifest.json` adds indirection without solving re-freeze or trust.

## Open questions

1. **Zero-retry semantics remain Ed-owned.** The schema is settled now. Under the current zero-retry plan, emit exactly one pre and one post capture and no retry command. If Ed permits a retry, the two-slot capability, `attempt_policy`, stage graph, command inventory, and final pack digest must change before freeze. U5 may generate against the current zero-retry design, but those bytes must not be treated as finally ratified or armable until the ruling.
2. **Reason-code S1-domain remains Ed-owned.** The refusal conditions above are settled, but whether their `readiness_launch_*` labels enter the ratified S1 domain is not. If yes, S4 cold-gate procedure applies; if no, they remain readiness-receipt-only codes. This does not block U5–U7 generation.

## Recommendation

Adopt the typed in-tree recipe plus hashed arm-time materialization exactly as above. It closes the U5–U8 contradiction without freezing machine paths, inventing U2’s pending CLI, or weakening U8 into validating an operator-authored launch attachment.

No files were changed. The workspace was initially clean; two unrelated untracked cold-gate files appeared concurrently during the consult and were preserved untouched.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Specified an in-plan-tree typed argv recipe contract, exact arm-time materialization shape, validation rules, stage-kind examples, and explicit parking of the two Ed-owned rulings.","pathspec":[],"verification":["Read D-117, final U5-U7/U8 plans, Fable/Magistrate examinations, landed campaign runner/config/runbook surfaces at HEAD 9131c6f7eb6f2fae8cc325e5c6be947113c50003","Inspected run_campaign, bracket reservation, fiducial capture, and extraction CLI help/contracts: OK","git diff --check: OK; no edits by this worker","Final git status showed two concurrent untracked cold-gate files; preserved untouched"],"flags":["no_edits","concurrent_workspace_change_observed"]}
