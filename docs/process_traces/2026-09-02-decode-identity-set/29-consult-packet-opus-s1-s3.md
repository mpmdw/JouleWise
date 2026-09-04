# Consult packet — disposition of the Opus counter-review's three should-fix items (file 28), 2026-09-02

Assembled by the magistrate for a bounded pre-decision consult (rule 2:
design consultation is the default; three-seat rule: Sol xhigh + the Opus
finding itself (file 28) + a BLIND fresh Fable seat). Seats are read-only
and read ONLY this packet, file 28, and the primary evidence named here.
The magistrate decides after the seats return; this packet proposes, it
does not rule. Checkout: `/Users/edr/code/JouleWise-wt-decode-id3` (or
`-wt-decode-id2`) detached at `7e888d82` (branch
`fix/2026-09-02-decode-identity-set`; round 2 closed clean, file 27).

## Executed evidence (bench, `wt-decode-id` at `7e888d82`, pasted)

```
$ sed -n 481,486p docs/contracts/identity_pin_projection.md
The identity projection authenticates the inventoried configuration bytes. It
does not independently open the suite-manifest files to recompute their
digests; manifest-file authentication remains with the pack and suite gates.
Within this contract, an unauthenticated manifest binding means a configuration
digest or reference not present as the exact declared pair, and that condition
refuses in step 4.
$ sed -n 1610,1621p joulewise/identity_pins.py
        for manifest_sha, member in declared_by_manifest.items():
            manifest_ref = member["suite_manifest_ref"]
            manifest_path = _declared_manifest_path(pack_root, manifest_ref)
            try:
                observed_manifest_sha = _sha256_bytes(manifest_path.read_bytes())
            except OSError as exc:
                raise IdentityPinProjectionError(
                    "readiness_identity_environment_dirty",
                    f"declared suite manifest is unauthenticated: {manifest_ref}",
                    observed={"suite_manifest_ref": manifest_ref},
                ) from exc
            if observed_manifest_sha != manifest_sha:
$ sed -n 5255,5258p joulewise/arm_readiness.py
        "plan_id": plan_id,
        "window_id": window_id,
        "pack_root": str(pack_root.resolve()),
        "pack_digest_algorithm": PACK_DIGEST_ALGORITHM,
$ sed -n 3897,3899p joulewise/analysis_engine/inputs.py
        pack_root = Path(next(iter(pack_roots))).resolve(strict=True)
        if committed_pack_tree_sha256(pack_root) != next(iter(pack_hashes)):
            return frozenset()
$ sed -n 1320,1322p configs/campaigns/d117_contrast_v5/generate_configs.py
            "warmup_runs": 1,
            "prompt_tokens": DECODE_PROMPT_TOKENS["A"],
            "output_tokens": 512,
$ sed -n 1798,1799p configs/campaigns/d117_contrast_v5/generate_configs.py
                    "workload": workload_for(measurement_arm, "A"),
                }
```

`OSError` from `resolve(strict=True)` is inside the gate's catch-all
(`inputs.py:4039–4048`), so a pack root recorded on another machine or
another checkout path collapses to `frozenset()` →
`consumer_identity_set_unauthenticated`. `repository_relative_projection`
(`arm_readiness.py:7074–7104`) is the repo's existing precedent for
comparing two recorded `pack_root`s by repository-relative suffix.

## Q1 — S3: the gate resolves the lineage's machine-absolute `pack_root`

Ruling 171a's F-B closure (file 22 §Q1) is "authenticate the pack inside
the gate": step (2) of the eight-step paragraph binds the pack bytes to
the launch by the committed-tree digest. That binding is by DIGEST; the
absolute path is only how the gate finds the bytes. Proposal on the table:

(a) Re-root: the gate takes the lineage `pack_root`, projects it to its
    repository-relative suffix (the `repository_relative_projection` rule:
    the path must be absolute, normalised, and END with the pack's
    repository-relative parts), and resolves that suffix under the
    repository root of the checkout the analysis runs in; step (2) then
    binds the re-rooted pack by digest exactly as today. A pack that
    exists at the same relative path but with a different committed tree
    is still refused by step (2).
(b) Keep the absolute path, but give the missing-root case its own honest
    label (e.g. `consumer_pack_root_unavailable`) instead of the forgery
    label — reproducibility from a clone stays broken but is no longer
    mislabelled.
(c) Both: re-root, and label an unresolvable root distinctly.
(d) Neither: record S3 as a limitation; analysis is defined to run in the
    arming checkout.

Questions: Which option, and why — in the mechanism's terms (what a
consumer can forge or lose under each)? Under (a)/(c), is the
repository-relative projection sufficient to find the pack, or must the
gate also require the repository root to be the one recorded somewhere in
lineage? Does (a) alter any RULED semantics (ruling 171a R-6; F-B closure)
— i.e. is this a reinterpretation of a prior verdict (rule 11 mandatory
cold-gate trigger) or an implementation choice inside it? Name the
biting counterfactual for whichever you recommend.

## Q2 — S2: ruling R-2's removal clause never installed

R-2 (`06-ruling-171a.md:36–45`): "`generate_configs.py:1334`'s hardcoded
`DECODE_PROMPT_TOKENS["A"]` is removed with it." It was not; `workload_for
("decode", …)` still emits `prompt_tokens = DECODE_PROMPT_TOKENS["A"]` and
`build_tree` writes it into `plan_tree.json`
`stack_scope.measurement_arms.decode.workload` for BOTH arms (line 1798).
Constraint: `configs/campaigns/d117_contrast_v5/generate_configs.py` may
change only with the D-166 registration digest
`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`
unchanged (`tests.test_d165_dominance_closeout`).

Question: what should the plan tree's decode `workload` carry once the
literal is removed — the common profile (the workload minus
`suite_manifest_ref`/`suite_manifest_sha256`/`prompt_tokens`) plus the
declared `suite_manifest_set`, the common profile alone, or a per-arm
value? Is there any consumer of `stack_scope[*].workload` (Opus found only
generators and one test) whose reading fixes the answer? Is this a
first-round finding (no cold gate) — the magistrate reads it so.

## Q3 — S1: the contract denies a check the code performs (dictated replacement; verify, do not rewrite)

Replace `identity_pin_projection.md:481–486` with:

> The identity projection authenticates two kinds of bytes inside the pack
> before it compares declarations. First, for every declared
> suite-manifest member it opens the manifest file at the declared
> `suite_manifest_ref`, resolved as a regular file below the pack root,
> and recomputes that file's sha256; a file that cannot be read, or whose
> digest differs from the declared `suite_manifest_sha256`, refuses with
> `readiness_identity_environment_dirty` ("declared suite manifest is
> unauthenticated") before any configuration is read. Second, it
> authenticates every inventoried configuration's raw bytes against its
> inventory digest (step 1). Within this contract, an unauthenticated
> manifest binding therefore means either a declared manifest whose file
> bytes do not hash to its declared digest, or a configuration whose
> digest/reference pair is not present as the exact declared pair; the
> first refuses before step 1, the second refuses in step 4.

Questions: is every clause true of `identity_pins.py:1541–1628` (cite the
line per clause)? Does the freeze procedure's numbered list (`:448–479`)
need a step inserted for the manifest-file check, and where (before step
1, since `declared_by_manifest` at :1602 is built before the config loop
— confirm)? First-use check on the new text.

## Q4 — gating

Given Q1–Q3: does anything here require a cold gate BEFORE the P-8
runbook re-run that freezes the three _v5 packs, or may the three fixes
land as one Sol fix round (first round on each defect) + delta re-audit +
fresh pass, with the P-8 run after merge? Opus (file 28) would put S3 in
front of a cold gate; say whether you agree and on which rule.
