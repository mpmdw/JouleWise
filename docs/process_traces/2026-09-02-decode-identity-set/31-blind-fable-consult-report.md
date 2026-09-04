# Blind Fable seat (Claude Fable 5, read-only, wt-decode-id2 @ e3f52884) — design consult report on packet 29

Custodied verbatim from the agent's final message (scratchpad paths redacted).

# Blind seat report — consult packet 29 (Q1–Q4), checkout `wt-decode-id2` @ `e3f52884`

Disclosure: the harness auto-loaded `~/.claude/CLAUDE.md`, `JouleWise/CLAUDE.md`, `CLAUDE.local.md` and the memory index into my context before I read the packet; I did not rely on them — rule 11 and the escalation signature are cited below only as the packet (file 29) and file 22 state them. I read files 29, 28, 06, 22 and the primary code named in them; nothing else in the trace directory, no decision log, no TASK_QUEUE.

## Q1 — S3: the gate's machine-absolute `pack_root`

### Executed (scratch script over `tests/test_analysis_inputs.py::_generated_frozen_gate_pack` :347 and `_production_floor_resolution` :577)

```
recorded pack_root : <scratchpad>/tmp-fable-cs/fable-cs-q1-5mg2n8z1/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5
recorded pack_sha256: 56491e238153e7d7efe9704be8236335bc33904c01d99773b1bf13ffefc0790a
[control, path exists]           status='exact' reasons=()
[pack_root -> /nonexistent/fable-cs/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5]
                                 status='refused' reasons=('consumer_identity_set_unauthenticated',)
  gate helper returns: frozenset()
  committed_pack_tree_sha256(bogus) raises: pack root is unreadable: [Errno 2] No such file or directory: '/nonexistent'
[repo moved; lineage keeps arming path]
                                 status='refused' reasons=('consumer_identity_set_unauthenticated',)
  digest at moved location   : 56491e238153e7d7efe9704be8236335bc33904c01d99773b1bf13ffefc0790a
  equals lineage pack_sha256 : True
[lineage re-rooted to moved pack]  status='exact' reasons=()
```

Second probe — what a re-rooted target must satisfy:

```
(i) plain copy, no git repo: ('Git proof failed: fatal: not a git repository (or any of the parent directories): .git',)
    production seam: refused ('consumer_identity_set_unauthenticated',)
(ii) marker committed; new digest : 6f15e2c5baf912c96da0821b74e32564470ecccf64daf8021d353da29a9d762b
     lineage digest (unchanged)   : f658c553ce6c3ac514b665766bbf1de0a1bb8d3a206f2ba7d972569a337943f0
     production seam: refused ('consumer_identity_set_unauthenticated',)
```

Third probe — the upstream chain the packet does not mention:

```
v5 A/decode config requires launch lineage at bundle load: True
authenticate_launch_lineage with a gone consumption path -> launch_consumption_missing | launch-lineage receipt is absent: /nonexistent/fable-cs/arm_readiness.consumptions/arm-0001.consumed.json: [Errno 2] No such file or directory: '/nonexistent/fable-cs/arm_readiness.consumptions/arm-0001.consumed.json'
```

### What `committed_pack_tree_sha256` requires of a re-rooted directory (`arm_readiness.py:2750–2874`, `:2737–2747`)

- It must sit inside a Git worktree (`git rev-parse --show-toplevel` from the pack root, `:2739`); a plain copy is refused `readiness_pack_not_committed` (probe (i)).
- `HEAD` of that worktree must contain ≥1 blob under the pack's path relative to that worktree's toplevel (`:2760`, `:2797–2800`).
- The on-disk tree must equal the committed tree exactly: no untracked file or directory, no missing committed entry, no symlink/special entry (`:2805–2848`), byte-equal to `git cat-file blob` and mode-equal (`:2853–2865`).
- The framed digest covers only pack-RELATIVE path, mode, byte length and content sha256 (`:2849–2874`, domain `joulewise.committed_pack_tree_sha256.v1\n` at `:46`). It does NOT include the repository root, the repository-relative prefix, or the commit. So the digest is location-independent (probe: the moved repo reproduces `56491e…` exactly) and "same committed tree" is required only in the sense of identical (path, mode, size, sha256) tuples — a one-file marker commit changes it (probe (ii)).

So a re-rooted resolution needs: a Git worktree, the same PACK-relative layout, and byte-identical committed content. It does not need the same repository root, the same repository-relative prefix (the digest never sees it), or the same commit.

### What a consumer could forge under (a) that it cannot today

Nothing. Under (a) the gate would still bind the re-rooted directory by `pack_sha256` at `inputs.py:3898`; any directory that passes has committed content byte-identical to the one the arming machine hashed (probe (ii): one extra committed file → refused). The declared set read from it (`:3994–4038`) is therefore identical. The only way to make a different pack pass is a SHA-256 collision, which is the same bar as today. The repository-relative projection (`arm_readiness.py:7074–7094`) is sufficient as a LOOKUP; requiring the recorded repository root would re-introduce exactly the non-portability (a) exists to remove, and adds no binding the digest does not already give.

### The finding the packet and Opus missed: the S3 scenario cannot reach line 3897 in production

`pack_root` in `row.launch_lineage` is not the raw stamp from the bundle. Production evidence rows are built by `_read_bundle` (`inputs.py:2735`), which calls `authenticate_bundle_launch_lineage` at `:2773–2778` and raises `AnalysisInputError` at `:2779–2782` on any `LaunchLineageError`. That authenticator (`arm_readiness.py:10608–10670`) delegates to `authenticate_launch_lineage` (`:10091`), which (i) reads the consumption receipt at the ABSOLUTE path the bundle recorded (`_read_v2_consumption`, `:8960–8985`), (ii) replays the consumed arm (`_replay_consumed_arm`, `:9304`), which does `Path(str(arm["pack"]["pack_root"])).resolve(strict=True)` at `:9333–9335` and, on failure, raises `launch_binding_mismatch: consumed arm pack root cannot be authenticated` (`:9348–9352`); it then recomputes `committed_pack_tree_sha256` via `_pack_record` (`:9345` → `:5242–5264`), (iii) resolves the launch manifest and the window root strict (`:10200–10205`, `:10222`) and the start/settle receipts by absolute path (`:10233–10252`). The returned mapping's `pack_root` is `str(pack_root)` from that resolve (`:10373`) and its `pack_sha256` is the consumption's, already checked equal to the freshly computed pack digest (`:10156–10174`, `:5259`).

Consequences:

1. In production, a bundle whose arming-time pack root no longer exists never becomes a `BundleEvidence` row: analysis input loading refuses with `launch_binding_mismatch` (or `launch_consumption_missing` if the consumption receipt is gone first — probe 3 shows that hop executed). The gate's `resolve(strict=True)` at `:3897` is a re-check of a path that was resolved strictly moments earlier; the `consumer_identity_set_unauthenticated` label for a missing root is reachable only through the direct-call seam (tests) or a caller that hands the gate a synthetic lineage.
2. The contract already says so: "every accepted bundle carries an authenticated launch lineage that resolves one pack root. The analysis input gate follows that already-authenticated root" (`identity_pin_projection.md:583–585`), and step (2) of the ruled eight-step paragraph reads "the pack root exists and the digest of its committed file tree … equals that pack digest" (`:607–614`).
3. Reproducibility from a clone is genuinely broken — but at the LINEAGE layer (consumption receipts, launch manifest, window root, lifecycle receipts, arm pack root: all machine-absolute, all resolved strict), not at the gate. Re-rooting the gate alone changes nothing an operator can observe.

### Option: (d), with the limitation recorded at the correct layer

- (a) buys nothing in production and introduces a new environmental input ("the checkout the analysis runs in") that the gate does not have today — the analysis engine has no repository-root notion (grep for `repository_root|repo_root|show-toplevel|parents[` in `joulewise/analysis_engine/*.py` returned nothing). Worse, the test fixture places its pack at `<tmp>/configs/campaigns/<PACK_ID>` (`tests/test_d117_contrast_v5_pack.py:342–344`), the same suffix as the real draft pack, so a re-root-under-the-analysis-checkout rule would point every gate test at the real repo's uncommitted draft pack and break all 12 tests unless re-rooting is a fallback after the recorded path fails — dead code in production, since the recorded path is guaranteed to exist by `:9333`.
- (b) adds a reason code to a closed set (`detection_floor.py` census, contract `:605–630`, tests) for a label production cannot emit, and it changes the ruled eight-step text at `:607–608`.
- (c) inherits both.
- (d) is correct, but the limitation must be worded honestly: "analysis of successor-lineage bundles runs on the arming machine's filesystem because launch lineage authenticates absolute receipt paths (`arm_readiness.py:9333`, `:10200`, `:10222`); the identity gate inherits that root." A relocatable lineage (repo-relative pack path + digest, relocatable receipt roots) is a new ruling, not this lane.

Biting counterfactual for (d) as a documentation change: none needed at the gate; the counterfactual that would justify (a) — "byte-identical bundle from a clone at another path reaches the gate and is refused with the forgery label" — is unreachable by construction (`:2773–2782`), which is why (a) should not be built. If the magistrate still wants file 27's accepted residual closed, the first-round test is: rewrite `pack_root` to a non-existent path on the direct seam and assert `('consumer_identity_set_unauthenticated',)` (my probe's second block is that test).

### Rule-11 answer

(a) would be an implementation choice inside R-6, not a reinterpretation: R-6(a) binds the set "read from the frozen receipt bound by the U8 readiness record" (`06-ruling-171a.md:70–73`) and says nothing about how the pack is located; the F-B closure binds by digest ("the same forged pack with a RE-STAMPED lineage is accepted, proving the pack-tree comparison and nothing upstream decided", `22:38–40`). But (a)/(b)/(c) all edit contract text that fix round 2 landed under the dictated-fills protocol (`:607–608` "the pack root exists"), so a change should be recorded with its reason. No enumerated rule-11 trigger (second round on the same defect, reversal of a verdict, irreversible action, proposed process rule) is met by any of the four options. I disagree with Opus that S3 belongs in front of a cold gate: the production-semantics consequence it names does not exist through this gate.

Packet correction (PD-1): `pack_roots` is described as coming "from the bundle's launch lineage" — it comes from the authenticator's return (`:10373`), after a strict resolve.

## Q2 — S2: what the plan's decode `workload` should carry

Grep (only `joulewise/`, `scripts/`, `tests/`; `configs/` are generators):

```
$ grep -rn "stack_scope\|measurement_arms" joulewise/ scripts/ tests/ --include="*.py"
tests/test_d117_floor_qwen25_7b_plan.py:1141:        stack = plan["stack_scope"]
```

That one test reads a different pack's `stack_scope.model_name/model_revision/quantization/*_condition_family_id` (`:1141–1148`), never `measurement_arms[*].workload`. No production consumer exists; nothing fixes the answer by its reading.

Packet correction: `stack_scope` is emitted by `build_plan` (`generate_configs.py:1758`) into `calibration_plan.json`, not by `build_tree` into `plan_tree.json` (executed: `plan_tree decode workload: (not under plan)`; `calibration plan decode workload: {... 'prompt_tokens': 42 ...}`). The freeze receipt pins `calibration_plan.json` by SHA (comment `:1767`), which is why this must land before P-8.

Digest: `python3 -m unittest tests.test_d165_dominance_closeout` → `Ran 47 tests in 7.086s / OK`. The test at `tests/test_d165_dominance_closeout.py:1754–1771` hashes `PINNED_DOMINANCE_CRITERION_BYTES` (`tests/test_d117_contrast_v5_pack.py:71`) and requires it to equal `frozen_json_bytes(generator.dominance_criterion_registration())` — canonical JSON (`sort_keys`, `(",", ":")`, `ensure_ascii=False`, UTF-8; `:104–110`) of the constant mapping at `generate_configs.py:490–556`. Executed: those bytes are byte-equal to the committed `d166_dominance_criterion_registration.json` (2032 bytes), hash to `1c0a4a11…`, and contain no `workload`/`prompt_tokens` content:

```
pinned bytes == on-disk registration JSON: True
sha256(pinned): 1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
keys hashed  : ['all_must_pass', 'common_mode', 'comparison', 'component_dispositions', 'denominator', 'exact_equality_policy', 'kind', 'mixed_outcome_policy', 'numerator', 'per_component', 'ratio_id', 'threshold', 'zero_denominator_policy']
mentions workload/prompt_tokens/DECODE_PROMPT: False
```

Removing the literal from `workload_for` cannot move it.

Facts that decide the shape (executed on the fixture):

```
DECODE_PROMPT_TOKENS: {'A': 42, 'B': 42}
workload_for('decode'): {'name': 'real_prompts_v1_chat_rendered', 'repetitions': 1, 'warmup_runs': 1, 'prompt_tokens': 42, 'output_tokens': 512}
emitted decode config workload (A): {'name': 'real_prompts_v1_chat_rendered', 'repetitions': 1, 'warmup_runs': 1, 'output_tokens': 512, 'suite_manifest_ref': 'configs/campaigns/…/decode_prompt_manifests/qwen3-1p7b/01_sky_color.json', 'suite_manifest_sha256': '49970e81…'}
emitted decode config workload (B): {... 'suite_manifest_ref': 'configs/campaigns/…/decode_prompt_manifests/qwen3-8b/01_sky_color.json', 'suite_manifest_sha256': '68387351…'}
prefill-pin A/B token ids equal: True
```

- Emitted decode configs carry no `prompt_tokens` at all (`generate_configs.py:1919–1929`); the common profile per R-2 is exactly `{name, repetitions, warmup_runs, output_tokens}`.
- `DECODE_PROMPT_TOKENS` is per-arm (`:1050`, one count per model enforced at `:975–981`); the fixture's two Qwen3 tokenizers happen to give 42/42, but a real pair need not, so a single arm-neutral `workload` cannot carry `prompt_tokens` honestly.
- The per-arm `suite_manifest_set` differs by arm (refs contain `MODEL_IDS[arm]`, `:1385–1389`; shas differ) and already lives where R-2 put it: `identity_units[*].declared_identity.workload_profile` (`:2634–2636`).
- After removal, `workload_for("decode")` has exactly one caller: `:1798` (`:1517` and `:1931` reach it only on the non-decode branch).

Recommendation: the common profile alone — `{"name", "repetitions", "warmup_runs", "output_tokens"}` — for the plan's descriptive `measurement_arms.decode.workload`. Not "common profile + `suite_manifest_set`" (that re-installs an arm-A-specific value in a field shared by both arms, the same defect R-2 removes), and not per-arm (the field is per measurement arm by construction, `:1792–1801`, and the per-arm declaration already has its ONE home). If a reader needs the rotation, one string pointer (`"prompt_rotation_declared_in": "arm_attachments.identity_pin_projection.identity_units[*].declared_identity.workload_profile.suite_manifest_set"`) is defensible, but it is optional and adds a key to a frozen-by-SHA file; I would not add it. Note the same "A" representative at `:1798` is used for prefill — harmless because A and B prefill token ids are identical (probe) — so the fix is decode-only. First-round finding, no cold gate: the ruling's clause is explicit (`06:43–45`) and was simply not installed.

## Q3 — S1: dictated paragraph vs `identity_pins.py:1541–1628`

Executed ordering probe (`_derive_projection_units` on the generated pack):

```
declared suite_manifest_ref      : configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/01_sky_color.json
pack_root / ref exists?          : False
_declared_manifest_path resolves : decode_prompt_manifests/qwen3-1p7b/01_sky_color.json
(1) manifest bytes tampered only         -> readiness_identity_environment_dirty | declared suite manifest is unauthenticated
(2) config bytes AND manifest tampered   -> readiness_identity_environment_dirty | config bytes changed for 01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a1.json
(3) config bytes tampered only           -> readiness_identity_environment_dirty | config bytes changed for 01_decode_contrast_blocks_01_05/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b01-a1.json
(4) declaration drift AND manifest tampered -> readiness_identity_environment_dirty | declared suite manifest is unauthenticated
(5) declaration drift only                -> readiness_identity_environment_dirty | identity unit 'A/decode' config declaration differs from pack
```

| Clause of the dictated paragraph | Verdict | Proving line(s) |
|---|---|---|
| "authenticates two kinds of bytes inside the pack before it compares declarations" | TRUE | configs `:1592` → `_read_unit_configs :1439–1451`; manifests `:1610–1630`; comparison `:1635–1654`; probe (4) |
| "for every declared suite-manifest member it opens the manifest file at the declared `suite_manifest_ref`" | TRUE | loop over `declared_by_manifest` `:1602–1612` (one entry per member; digests unique `:1531`) |
| "resolved as a regular file below the pack root" | TRUE but NOT REPLICABLE from the text | `_declared_manifest_path :1541–1568` keeps only the parts AFTER the pack directory's name (`:1546–1554`; refuses an ambiguous ref `:1547–1551`, an empty remainder `:1555–1559`), then `_resolve_config_path :1245–1259` (strict resolve, inside pack, non-symlink regular file). The declared ref is repository-relative (`generate_configs.py:1491–1493`); `pack_root / ref` does not exist (probe). A reader joining the ref under the pack root rebuilds the wrong gate. |
| "recomputes that file's sha256" | TRUE | `:1614` |
| "a file that cannot be read, or whose digest differs …, refuses with `readiness_identity_environment_dirty` ('declared suite manifest is unauthenticated')" | TRUE (incomplete) | unreadable `:1615–1620`; mismatch `:1621–1630`; the paragraph omits "cannot be resolved" `:1563–1568`, same code and message |
| "before any configuration is read" | CONTRADICTED | `_read_unit_configs` at `:1592` reads every inventoried config's bytes (`:1439`) and checks the inventory digest (`:1446–1451`) before the manifest loop at `:1610`; probe (2) |
| "Second, it authenticates every inventoried configuration's raw bytes against its inventory digest (step 1)" | TRUE as a fact, FALSE as an order | `:1446–1451`; it is first in code order |
| "an unauthenticated manifest binding therefore means either a declared manifest whose file bytes do not hash to its declared digest" | TRUE (incomplete: also unreadable/unresolvable) | `:1621`, `:1615`, `:1563` |
| "or a configuration whose digest/reference pair is not present as the exact declared pair" | TRUE | `:1661–1670` |
| "the first refuses before step 1" | CONTRADICTED | `:1592` precedes `:1610`; the manifest check sits after step 1 and before the step-3 equality (`:1648–1654`) and step-4 membership (`:1661`); probes (2), (4) |
| "the second refuses in step 4" | TRUE | `:1661–1670` ↔ contract step 4 `:463–464` |

Freeze-list insertion: NOT before step 1. Code order is step 1 (`:1592`) → member validation and common-profile derivation (`:1594–1601`, contract step 3's first clause) → manifest-file authentication (`:1610–1630`) → per-config equality/membership (`:1635–1670`). Insert as the second sentence of step 3 (`:456–462`), after "validates every exact three-field declared member": "It then resolves each declared `suite_manifest_ref` — a repository-relative path, of which only the part after the pack directory's name is kept — as a regular file inside the pack, reads it, and requires its SHA-256 to equal the declared `suite_manifest_sha256`; an unresolvable, unreadable, or mismatching manifest refuses `readiness_identity_environment_dirty` ("declared suite manifest is unauthenticated") before any configuration's declaration is compared." Placing it inside step 3 keeps steps 4–6 numbered as the replacement paragraph and `:486` cite them. The replacement paragraph's two contradicted clauses then become "the first refuses in step 3, before any declaration is compared" and drop "before any configuration is read".

Pre-existing nit outside the packet: step 1's "parses the configuration through `BenchmarkConfig`" (`:451–452`) happens at `:1636` (`_typed_config`) and `:1675` inside the per-config loop, after the manifest check — the list is already one step out of order there.

First-use table for the new paragraph (contract line numbers as they stand):

| Term | First use | Definition |
|---|---|---|
| identity projection | `:481` (new) | `:16` (bolded, §1) |
| pack / pack root | `:481` | `:34` (campaign pack); "pack directory" `:113` |
| declared suite-manifest member | `:482` | `:90–94` (declared manifest member) — the paragraph should use the defined name |
| `suite_manifest_ref` / `suite_manifest_sha256` | `:483` / `:487` | `:91–93` |
| regular file below the pack root | `:484` | nowhere — needs the gloss above (repository-relative ref, kept after the pack name) |
| `readiness_identity_environment_dirty` | `:486` | `:728` (refusal table; fixed identifier, acceptable per file 22 §Q2) |
| inventoried configuration / inventory digest | `:489` | `:112–115` |
| step 1 / step 4 | `:490` / `:494` | `:451` / `:463` |
| declaration | `:481` | `:83` |
| unauthenticated manifest binding | `:491` | defined in the sentence itself — fine |
| digest/reference pair | `:493` | `:100–102` (manifest class: "the reference paired with that digest") |

## Q4 — gating

No cold gate is required before the P-8 re-run, on the packet's own statement of the rule (`29:87–89`) and file 22's application of it (`22:15–16`, `:25–31`): none of S1–S3 is a second round on the same defect, a reversal/reinterpretation of a verdict, an irreversible action, or a proposed process rule. S1 and S2 are first-round findings on a contract paragraph and an uninstalled ruling clause; land them as one Sol fix round + delta re-audit + fresh pass, then P-8. S3: no code change — record the limitation at the lineage layer (Q1); I disagree with Opus's cold-gate placement because the production consequence it rests on is unreachable through the gate.

Two things the magistrate should still weigh: (1) file 22 `:69–77` fired the standing escalation signature on §6 prose and adopted dictation as the corrective; S1 is a third consecutive prose defect in the same section that survived the dictated round, and the dictated replacement in this packet itself carries two false ordering clauses — this consult is the consult that signature calls for, and the fix-round brief should carry the corrected paragraph WITH the proving lines above and require the delta re-audit to re-run probe (2)/(4). (2) S2 must precede the freeze because `calibration_plan.json` is SHA-pinned by the freeze receipt (`generate_configs.py:1767`).

## Residual risk

- My claim that a moved pack never reaches `inputs.py:3897` in production rests on reading `:2773–2782`, `arm_readiness.py:9333–9352`, `:10137–10144`, `:10362–10383`, and on executing only the first hop (probe 3); I did not build a full consumption/arm/launch-manifest chain and move it.
- `pack_root` equality at `:3884–3886` compares the authenticator's resolved string across rows; two checkouts armed separately on one machine would differ and refuse — correct, but a label the operator may also misread.

## What this pass did NOT check

- No full test suite; ran `tests.test_d165_dominance_closeout` (47 OK) and four scratch scripts only.
- No mutation table; no P-8 runbook; no hardware.
- I did not verify Opus's nits 1–4 or the R-1…R-8 clause table.
- I did not read files 07/13/19–21/23–27; if S3's upstream-chain point was already dispositioned there, I would not know.
