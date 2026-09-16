# Blacksmith as a CI-runner alternative — read-only investigation (2026-09-15)

Checked this session: `mpmdw` is a personal **User** account, the repo is **public**, MIT; `ci.yml` (branch `chore/2026-09-15-ci-trim-2`) has seven `runs-on: ubuntu-latest` sites, no `secrets.*`, no `permissions:` block (default `GITHUB_TOKEN` only), and uses `actions/{upload,download}-artifact@v5`; `main` has no branch protection and no rulesets. No file modified, no CI run.

## 1. What it is
A `runs-on` label swap: Blacksmith's GitHub App registers just-in-time runners per job. Labels: `blacksmith-{2,4,8,16,32}vcpu-ubuntu-{2204,2404}` (`-arm` variants), macOS `blacksmith-6vcpu-macos-latest` [S2]. Runners "boot off of the same image(s) as GitHub's runners" (actions/runner-images) [S2], so checkout@v5, setup-python@v6 (3.11/3.13/3.14), `sudo apt-get install zsh`, and artifact upload/download (GitHub-API side) need no change; only Docker builds need action substitutions, unused here [S1].

**Blocker:** "Blacksmith is limited to GitHub organizations and not available for personal repositories" [S1]. The repo would first have to be transferred to a (free) GitHub organization.

## 2. Concurrency and hardware
"Blacksmith does not impose any concurrency limits" on jobs or vCPUs [S2]. GitHub's cap is per plan: Free 20, Pro 40, Team 60 concurrent jobs [S5]. `ubuntu-latest` on a public repo is 4 vCPU/16 GB [S6]; `blacksmith-4vcpu` is 4 vCPU/16 GB/80 GB [S2]. Marketed "twice as fast" [S3]; the independent runs-on benchmark (2026-09-02) scores Blacksmith 2-vCPU (AMD EPYC) 4357 vs GitHub 2-vCPU 2193–3479, i.e. ~1.3–2x [S7]. Docker-layer/sticky-disk caches are irrelevant: ordinary shards do no pip install (setup 20–34 s measured tonight).

## 3. Cost
Blacksmith: 3,000 free min/month, then $0.004/min for every Linux x64 size (2–32 vCPU); macOS $0.08/min; free OSS program for active, permissively-licensed public repos (JouleWise qualifies on paper: MIT, public) [S4][S12].
GitHub today: standard runners are free and unlimited on public repos [S6][S9] → $0 on Free (20 concurrent) or $4/month on Pro (40 concurrent) [S5][S10].
Estimate (owner's assumptions: ~200 runner-min per code PR, 10 PRs/day peak, 22 days; main pushes ≈31 jobs ≈ ~290 runner-min, scaled from the measured ~195 runner-min for 21 jobs, 5/day):
- Peak: 44,000 + 32,000 ≈ 76,000 min → **~$300/month**; ~$150 if the 2x speedup holds; minus $12 free tier.
- Steady (3 PRs + 3 pushes/day): ~32,000 min → ~$130, ~$65 at 2x.
- Versus GitHub: $0 (Free) or $4 (Pro).

## 4. Setup
1. Create a GitHub Free organization ($0) [S9] and transfer the repo (GitHub keeps redirects; update local remotes and the magistrate's `gh` paths).
2. app.blacksmith.sh → sign in with GitHub → install the App on the org [S1]; add billing or apply to the OSS program [S4].
3. Edit seven `runs-on` lines. Job IDs, step names and matrix check names (`test (3.13, 1)` …) are unchanged; no protection to update.
macOS: M4 6/12-vCPU runners exist at $0.08/min [S2][S4] — not needed.

## 5. Risks
- Lock-in: none; reverting is the same seven lines.
- Reliability: 2026-07-21 control-plane outage ~5.5 h, jobs not picked up [S8]; StatusGator shows 2026-09-02 storage degradation (3 h 10 m), 2026-09-09 cache/website outage (5 m), three warnings 2026-09-13 [S11]. GitHub itself is not immune [S11].
- Secrets/data: the App asks Actions/Contents/Workflows/Pull requests/Checks read-and-write, Issues/Members read, self-hosted-runner administration; it does not request secrets and "cannot read secret values" [S13]. ci.yml exposes only the job-scoped `GITHUB_TOKEN` of a public repo. Contents/Workflows write is broader than this repo needs (it exists for their auto-migration PRs).
- `concurrency:` groups and `fromJSON` matrices are resolved by GitHub's workflow engine before a job is dispatched; Blacksmith only registers JIT runners [S13]. No documented incompatibility found.

## 6. Recommendation
Not yet. The measured bottleneck is GitHub's 20-job cap, not runner speed, and **GitHub Pro ($4/month) raises it to 40** [S5][S10] with zero migration — 40 ≥ the 31-job main matrix, so a main push and a 13-job PR mostly co-execute. Try Pro first, re-measure the same three-run table. Consider Blacksmith only via the OSS program (else $65–300/month vs $4) and only after an org transfer. If tried, per job:

```
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
```

Proof, either path: one PR run where every job's queue delay (job start − workflow created) is under 1 min and workflow wall ≈ longest job (~14–19 min) instead of 32–40.

## Sources
- S1 https://docs.blacksmith.sh/introduction/quickstart
- S2 https://docs.blacksmith.sh/blacksmith-runners/overview
- S3 https://docs.blacksmith.sh/introduction/why-blacksmith
- S4 https://www.blacksmith.sh/pricing
- S5 https://docs.github.com/en/actions/reference/limits
- S6 https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- S7 https://runs-on.com/benchmarks/github-actions-cpu-performance/
- S8 https://www.blacksmith.sh/blog/blacksmith-outage-on-july-21-2026
- S9 https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- S10 https://pullnotifier.com/tools/github-pricing (GitHub Pro $4/month; github.com/pricing omits Pro)
- S11 https://statusgator.com/services/blacksmith
- S12 https://www.ossperks.com/programs/blacksmith
- S13 https://docs.blacksmith.sh/blacksmith-administration/github-app
- Runner-image basis for ubuntu-latest = 24.04: https://github.com/actions/runner-images/issues/10636
