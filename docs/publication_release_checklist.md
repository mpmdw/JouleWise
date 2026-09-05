# Publication Release Checklist

This is the single ordered publication command/checklist. It separates the
clean-clone fixture/component smoke from controlled full regeneration and from
credentialed publication. A green smoke is not evidence that the private
six-bundle corpus was regenerated, that pinned Node tools were available, or
that any artifact was uploaded or deployed.

## Boundaries and owners

| Boundary | Gate | Owner / evidence |
|---|---|---|
| Source | Work from the intended commit in a clean clone; `git status --porcelain` must be empty. | Release operator records the commit and clean status. |
| Corpus | The retained six-bundle corpus may be used only to check the historical report-building path. Its energy values are permanently barred from claim use by D-078 because the power trace and workload events were joined through a defective time anchor. The future publication corpus is the admitted `_v5` transaction. | An authorized internal operator labels any six-bundle output `plumbing evidence only`; a claim-bearing release requires the `_v5` corpus and its governed admission artifacts. |
| Network | The release checker itself is offline. A fresh public clone and `npm ci` require network access, but no repository or deployment credential. | CI log or release operator records dependency installation from the two lockfiles. |
| Node / Marked | Exact rendered-site smoke requires the root lockfile's pinned Marked. If absent, `release_check.py` loudly identifies the boundary and exercises the built-in offline renderer without claiming the Marked seam. | CI supplies `JOULEWISE_MARKED_BIN` after `npm ci`. |
| Node / Lakebed | Exact capsule postcondition requires `site_capsule/package-lock.json` and Lakebed 0.0.29. If absent, the checker loudly identifies the boundary and exercises the estimator-only capsule path without claiming a measured Lakebed artifact. | CI supplies `JOULEWISE_LAKEBED_BIN` after the capsule `npm ci`. |
| Release credentials | Tag pushes and release-asset uploads require the repository host credential. No check, build, or packaging command reads it. | Ed performs or explicitly authorizes the manual publication and retains the URL/hash record. |
| Lakebed credentials | Lakebed deployment requires Ed's credential and network access. It is never automated and is never an agent action. | Ed alone records the deployment result. |

## Ordered release

1. Pin the source and prove the checkout is clean.

   ```sh
   git rev-parse HEAD
   test -z "$(git status --porcelain --untracked-files=all)"
   ```

2. Run the non-secret clean-clone gate.

   ```sh
   python3 scripts/release_check.py --dry-run
   ```

   Despite its name, `--dry-run` is not a preview. It creates a temporary clean
   Git snapshot and actually executes the source-only capstone drift check, a
   deterministic mock bundle, transformed bundle-pack construction and
   verification, site build, and capsule pack. Missing corpus or external tools
   are named loudly; no seam is silently skipped to green. This is
   fixture/component evidence only. It performs no network operation, reads no
   credential, and never deploys.

3. Optional historical plumbing check: at the controlled/internal corpus gate,
   regenerate the old report shape from the six retained strict-valid bundles.
   This step is unavailable in a pristine public clone and is not a CI
   prerequisite.

   **D-078 publication fence:** the six bundles were collected under the
   defective time anchor. Their energy values are permanently non-claim-bearing,
   even though the stored bundles pass strict validation. Output from the
   `rpt001` profile demonstrates only that the report-building path runs; it
   must be labelled `plumbing evidence only` and must never supply a paper,
   abstract, figure, comparison, or detection-floor claim. The claim-bearing
   publication corpus will be the admitted `_v5` transaction, which has not
   yet been collected.

   ```sh
   python3 scripts/build_capstone.py --profile rpt001 --full --offline --runs-root "$JOULEWISE_PRIVATE_RUNS"
   python3 scripts/build_capstone.py --profile rpt001 --offline --check
   ```

   Record the corpus/input-manifest hashes, the resulting artifact-manifest
   verification, and the D-078 non-claim label. `--offline` closes the network
   boundary; controlled corpus access remains mandatory.

4. If the historical bundles are released for method replication, construct
   and verify their privacy-transformed bundle pack. Construction performs
   strict validation, source-provenance eligibility checks, and the publication
   privacy transformation. It does not remove the D-078 bar: the pack and its
   release description must say that the enclosed energy values are retained
   instrument evidence, not claim-bearing measurements.

   ```sh
   python3 scripts/package_bundle_pack.py --output dist/jw-pack-2026-07-09 \
     "$JOULEWISE_PRIVATE_RUNS/example-mac-mlx-local__r1" \
     "$JOULEWISE_PRIVATE_RUNS/example-mac-mlx-local__r2" \
     "$JOULEWISE_PRIVATE_RUNS/example-mac-mlx-qwen35-122b-512t__r1"
   python3 scripts/package_bundle_pack.py --verify dist/jw-pack-2026-07-09
   ```

   Retain the pack manifest and top-level archive SHA-256 before any upload.

5. Manually publish the approved tag and release asset. This is the repository-
   credential boundary: Ed performs it or explicitly authorizes it. Verify the
   uploaded asset hash against the retained local hash. No CI job performs this
   step.

6. **Manual-dispatch reference, not a session step.** D-136 retired the site
   lane from every automatic and agent process. If Ed chooses the manual
   workflow dispatch, Ed alone handles generated-site regeneration and
   deployment. The retained `docs/site/DRIFT.md` file may inform that manual
   decision; routine documentation work, agent closeout, CI, and
   `release_check.py` do not refresh, regenerate, or deploy the site.

   In that Ed-controlled credentialed window only:

   ```sh
   npm ci --ignore-scripts --no-audit --no-fund
   npm --prefix site_capsule ci --ignore-scripts --no-audit --no-fund
   python3 scripts/build_site.py
   JOULEWISE_LAKEBED_BIN="$PWD/site_capsule/node_modules/.bin/lakebed" python3 scripts/pack_capsule.py
   (cd site_capsule && npx --no-install lakebed deploy)
   ```

   The two `npm ci` commands cross the network boundary without deployment
   credentials. The final command crosses both the Lakebed network and Ed-only
   credential boundaries. Record the reviewed drift report, source commit,
   measured capsule size, deployment identifier/URL, and post-deploy route
   checks. No agent regenerates or deploys the Lakebed site.

## Acceptance record

- Clean-clone `release_check.py --dry-run`: pass/fail, commit, and whether the
  exact Marked and Lakebed seams or their loud offline fallbacks ran.
- Controlled six-bundle plumbing check, if run: pass/fail plus corpus/input and
  output hashes and the D-078 non-claim label; never substitute fixture evidence
  or present the output as a publication result.
- Historical bundle pack, if released: construction and verification logs,
  retained archive hash, and the D-078 non-claim label.
- Release publication: Ed/manual authorization, asset URL, and matching hash.
- Site, only if manually dispatched by Ed: retained-drift review,
  regeneration/deployment log, and route checks at the same deployment window.
