# Upstream fix kits, 2026-11-07

Four fix kits for upstream projects, built read-only. No agent ran, built, installed or imported any upstream code. None of these kits has been run. None of them has been posted anywhere.
Each kit has a `FACT-SHEET.md` (the facts, citations and risks, ending with `## Static review`) and a `RUN-ME.md` (sandboxed steps). The rest of each kit is the patches, repro scripts and `SHA256SUMS`.

## Status

| Kit | Upstream | Pinned commit | Run status | Reviewer verdict | What it fixes |
|---|---|---|---|---|---|
| [`mlx-vlm-d1/`](mlx-vlm-d1/) | [Neywa-Labs/mlx-vlm](https://github.com/Neywa-Labs/mlx-vlm) (formerly Blaizzy/mlx-vlm; both names had the same HEAD on 2026-11-07) | `a54f1a0d86fa45c466c00d819ac6ac5ba9d61ac4` | **UNRUN** | ready-with-caveats | `qwen4_exp` ignores QSA sparse attention in left-padded batches. The fix changes one file (+11/-16). |
| [`llama-cpp-qsa-convert/`](llama-cpp-qsa-convert/) | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | `f477f795cb071baf5b8af6488378366a72034ac4` | **UNRUN** | ready-with-caveats | The converter writes zero QSA compress ratios when `layer_types` says `indexed_attention`. There are two fix options (a/b), and the choice is Ed's. |
| [`mlx-lm-reasoning-content/`](mlx-lm-reasoning-content/) | [ml-explore/mlx-lm](https://github.com/ml-explore/mlx-lm) | `56230fa02b8ff8330daf26dc95c28480423ed5fe` | **UNRUN** | ready-with-caveats | The server sends `reasoning` but never maps an incoming `reasoning` back to `reasoning_content` for chat templates. The fix adds 6 lines. Acceptance risk is moderate to high. |
| [`km003c-rs-redelivery/`](km003c-rs-redelivery/) | [okhsunrog/km003c-rs](https://github.com/okhsunrog/km003c-rs) | `71f69e4a35c1184cc114a62145b8a8241d3e13e9` | **UNRUN** | ready-with-caveats | A meter re-delivery longer than 8 samples is integrated twice. The kit has `fix.patch` and `failing-test.patch`. |

Every verdict comes from a second agent's static review: it read the code and checked that the patches apply, without running anything. What only a run can settle is listed in each `FACT-SHEET.md`.

## Before using a kit

- **Paths.** The RUN-MEs refer to `/private/tmp/jwoss-ro/<key>/kit` and to a read-only clone at `/private/tmp/jwoss-ro/<key>/src`. `/private/tmp` is wiped on reboot, so use this directory as the kit path. The run steps make their own fresh clone at the pinned commit; the `src` clones only served the read-only review and are not saved here.
- **Checksums.** Each `SHA256SUMS` here was regenerated after `## Static review` was appended to `FACT-SHEET.md`. All other files match the checksums taken when the kits were written. Check with `(cd docs/oss/2026-11-07/<key> && shasum -a 256 -c SHA256SUMS)`.

## Ed's steps, when ready

1. **Read `RUN-ME.md`** for the kit, along with its `FACT-SHEET.md`, the patches and every script it runs. Nothing in a kit should run before you have read it.
2. **Run it in a fresh sandbox.** Use a new directory under `/Users/edr/code/CapstoneProject/jw-wt/`, a fresh clone of upstream at the pinned commit, a fresh venv or toolchain, and no repo hooks (no `pre-commit install`). Follow the RUN-ME's offline and cleanup steps. Record the before/after output. If a result disagrees with the fact sheet, stop and treat the kit as wrong until you understand why.
3. **Write the issue/PR in your own words** with the project's AI-disclosure, and post it **from your own account**. Each fact sheet records the project's rules; in brief:
   - **mlx-vlm:** open an issue first; maintainers have redirected unsolicited PRs. Add a one-line AI disclosure in the style of #2328. Sign your commits. Keep JouleWise's trailers off the upstream commit.
   - **llama.cpp:** AI-written PR text and agent-run pushes are prohibited, so write everything yourself. Fill in `AI usage disclosure: YES - ...` in the PR template. Use the commit trailer `Assisted-by: <assistant name>`, never `Co-authored-by`. New contributors may have only 1 open PR. Open the issue first ("Bug (misc.)" template); the PR follows about a day later.
   - **mlx-lm:** open the issue first. After a maintainer replies, open the PR and fill in its `AI usage disclosure:` field. The commit message is yours, with no trailers.
   - **km003c-rs:** the project has no CONTRIBUTING file or CLA ("Contributions welcome!"). Restate the fact sheet in your own words and say that you used AI assistance.
