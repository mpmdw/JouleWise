# Open-source contribution plan (2026-11-07)

**Track:** open-source contributions (audit track, 2026-11-07, part 3).
**Synthesizer:** Opus 5.5 (`claude-opus-5-5`). Inputs: two independent inventory seats (seat 1 Fable 5.1, seat 2 Opus 5.5; both verbatim in the appendix) and 40 candidate entries, each checked by a separate verifier on 2026-11-07. After merging near-duplicates this plan has 22 items worth pursuing and 1 rejected.

**What Ed asked for.** "Besides the instrument and using it to detect LLM sneakiness, I want to contribute anything germane from this work to the open source LLM community." Releasing the instrument itself (Paper 1) and ALIGN (its own paper) are therefore out of scope here. This plan covers everything else: bugs found while building, evidence and reference data, and methods and tools that other projects can use without running JouleWise. Some items offer pieces of the instrument (SMC reader, KM003C findings) to other projects. They are included because they reach users who will never run JouleWise.

**Status.** Planning only. Nobody has posted, filed, commented on, uploaded or opened anything upstream. Several targets forbid AI-written posts, so this document contains no draft upstream text. It is not a registration, a claim or a measurement. It uses no Block 5 value, no BYTES held-out row and no ALIGN outcome. No restricted path (`/Users/edr/jw-b5-*`, `night-*`, custody, archive, `restricted/`) was opened.

**Repo pins.**
- `origin/main` = `bd7a3efcd`.
- `origin/port/qwen4-exp-mlx` = `9452a2bb4` (holds the mlx-vlm D1 kit).
- `origin/lane/2026-11-06-qwen4exp-quality-ref` = `92042869a` (canonical module, gold harness, quant scorer).
- `origin/lane/2026-11-06-qwen4exp-port-r2` = `23bb066df`; `origin/lane/2026-11-05-qwen4exp-port-perf` = `1aeb9ff88`; `origin/lane/2026-11-05-qwen4exp-port-upstream` = `fd41a06e1`; `origin/lane/2026-11-07-qwen4exp-mbp-live` = `97d780d59`.
- `origin/records/2026-11-07-qwen4-l3-reference-top64` = `ade3bf7f5`.
- `origin/lane/2026-11-06-v4-r1-integrated` = `e901eb2a4`; `origin/lane/2026-11-05-align-pilot10-benign` = `5f817856b`.

Most of the material is **not on `main`**. `joulewise/align/**`, the qwen4_exp port, the BYTES tooling and the attribution modules live only on lanes, so every extraction starts from the lane named in its section.

---

## 1. Executive summary

- **Three kinds of contribution exist.**
  1. *Bugs found in other people's code while building.* These are mlx-vlm D1/F1/P5, the llama.cpp `indexed_attention` converter, the mlx-lm server `reasoning` round trip, and km003c-rs re-delivery. Each is small and concrete, needs no sealed data, runs on the Air, and costs at most 1.5 Ed-days. They earn the most credibility per hour.
  2. *Evidence and reference data.* This covers a Flash-Next reference computed with the official transformers code, SMC power keys checked against a meter, M3 Max support for zeus-apple-silicon, and CodeCarbon's undercount on Macs. Each needs a re-capture or one fresh, unregistered desk capture.
  3. *Methods and tools.* These are a guide to HF-to-MLX numerical parity, a Mac energy-measurement guide, a quiet-machine checker, an SMC thermometer classifier, `inspect-energy`, a windowed-energy package, an active-bytes method for hf-mem, preregistration templates, and an open dataset. They take longer, and three are gated on registered releases.
- **Verification changed the picture.** After merging, 23 items remain: 22 worth pursuing and one not (a transformers top-k tie-break). Only one part, mlx-vlm D1 inside item A, is a plain go; everything else is go-with-changes. The corrections fell into three groups:
  - *Prior art the candidates missed.* mlx-vlm already ships `qsa_kernel.py`, `ple_storage.py` and `moe_offload.py`. Other existing work: `huggingface/transformers-to-mlx` `compare_layers.py`; `mlx-kld` (two implementations); a 32 GB full-vocabulary Flash-Next bf16 logit dataset; macmon reading PSTR; and several 128 GB Flash-Next quants that publish KL against bf16.
  - *Numbers that came from our own endpoint rather than upstream code.* The 119-byte reasoning figure is one.
  - *Wrong statements about where code lives* ("on main", "never run live").
- **Do these four first:** mlx-vlm D1, then mlx-lm `reasoning_content`, then the llama.cpp converter, then km003c-rs. Each is ready or nearly ready, runs on the Air, needs no sealed data, and needs no MBP time.
- **One rule applies to every target.** Ed writes every word a maintainer reads. Where an AGENTS.md demands it (mlx-lm, llama.cpp), Ed also pushes, opens the PR and writes the commit message himself. He discloses AI assistance in each project's required form. Agents prepare reproducers, tests, patches and fact sheets; they never post. Agents also do not execute unvetted community code, so Ed runs the upstream reproducers or approves a sandbox.
- **One urgent action.** `/private/tmp/jwgold-run-l3/work/parity/head` (4.7 GB, still present when this was written; the Air's data volume is 89% full) holds the only fp32 and bf16 head outputs of the 48-layer gold pass. Item H's fp32 re-capture needs them, and `/tmp` is volatile. Copy them to durable non-home storage now (§5, day 0).
- **Blinding holds throughout.** No item uses sealed data. Item T (preregistration templates) publishes only after the Block 5 registered release. Item U (dataset) is staged per release. Item S may not print rows from the frozen BYTES manifest before stage 2; it re-derives counts fresh from public headers.
- **ALIGN comes first.** OSS work never takes MBP time from a measurement window. All MBP needs are folded into one desk-capture kit for the magistrate. Items that depend on port live work (I, J, K's M3 Max bench, L's streamed real-weight run) wait for the external SSD and the MBP live run.
- **Verification also found 16 internal defects and hygiene issues** (§7). Examples: an HF-cache symlink bug in the n-gram loader, 3 macOS-only test failures, `kv_size.py` overcounting hybrid models, and the bf16 reference sitting at about JouleWise's own quant acceptance bar.

## 2. Decisions for Ed

Each decision has a recommended default. The plan proceeds on the default unless Ed says otherwise. Process calls that are obvious have already been made (see "Lead rulings" at the end of this section).

1. **Licenses.**
   - *Recommendation:* keep the repo MIT. Add a `license` field to `pyproject.toml` and a `CITATION.cff` before any package or dataset ships.
   - *Extracted packages* (quiet checker, `inspect-energy`, windowed-energy, probes repo, thermometer probe): MIT, Copyright Ed R.
   - *Datasets we author* (active-bytes table, future energy dataset): CC-BY-4.0.
   - *Flash-Next logit records* (item H): `license: other`, `license_name: qwen-community-1.0`, shipped with Qwen's notice. The license is silent on outputs; this follows the jyohukuchan precedent.
   - *Write-ups:* CC BY 4.0, with an AI-assistance statement.
   - *Upstream contributions* take the target's license:
     - MIT: mlx-lm, llama.cpp, mlx-vlm, CodeCarbon, macmon, Inspect, ControlArena, hf-mem.
     - Apache-2.0, inbound = outbound: Zeus and zeus-apple-silicon.
     - MIT OR Apache-2.0: km003c-rs.
     - GPL-3.0-only: iSMC, and only if code ever goes there.
   - *Also confirm:* seven commits to the attribution modules (2026-10-22) carry the author "John Davis <mpmdw630@pm.me>". Ed should confirm this is his alias before those files are relicensed into a package (item R).
2. **What goes first.** Default order:
   - Week 1: A (D1 issue), C (repro and issue), B (issue), D (test and issue).
   - Week 2: the matching PRs as maintainers respond. Only one llama.cpp PR may be open at a time. In mlx-lm, C uses Ed's (probably single) open-PR slot before anything from I or K.
   - Then H and F stage 1.
3. **Which items need Ed's own words.** All upstream text, everywhere. The project-specific rules that bind:

   | Target | Rule that binds Ed |
   |---|---|
   | mlx-lm | AI-written issues, PR descriptions, discussions and replies are "strictly prohibited". The issue and PR templates make you tick an acknowledgement. AGENTS.md: agents must not write commit messages or PR descriptions, reply, push, or create PRs; violation means closure and a ban. Ed pushes, opens and writes the commit message. Our Co-Authored-By and Claude-Session trailers must not go on the upstream commit. Ed discloses AI use in the template field instead. |
   | llama.cpp | Same post ban. Undisclosed AI use can mean a permanent ban. The PR template requires the line `AI usage disclosure: YES/NO`; Ed answers YES. Use an `Assisted-by:` trailer, never Co-authored-by. Roughly 1 h of manual review per 200-400 LOC. One open PR for a new contributor. A bug-fix PR needs a reproducible issue and a regression test that fails before the fix and passes after. No trivial fixes. |
   | mlx-vlm | No written AI rule. Maintainers do use an "AI Slop" label and have redirected unsolicited PRs to "open an issue first". The visible norm is a one-line disclosure in the style of #2328. A bot flags unsigned commits. |
   | Zeus / zeus-apple-silicon | AI tools welcome; "meat proxies" (people relaying AI output) are warned, then blocked. Issue first. |
   | CodeCarbon | Four-tier AI disclosure is mandatory, and mis-tiering closes the PR. The submitter is the "Sole Responsible Author" of every line. No reinvented helpers. The PR template's "automated agent ... poop emoji" line is a honeypot; ignore it. |
   | Inspect AI | A code PR must link an issue a maintainer labelled `accepted`, or it is auto-closed. A one-line extensions-listing PR needs no issue. Disclose tools and include an "Agent review" section. |
   | ControlArena | No AI rule (the repo ships AGENTS.md and CLAUDE.md). Ed writes the text anyway. |
   | macmon | agents.md welcomes agent PRs. Our contributions there are data comments, written by Ed. |
   | exelban/stats | "Open source, not open contribution": only issues or data, no unsolicited PRs. |
   | hf-mem | Issue first. "Maintained by humans." Cites the Ghostty AI policy (not opened). |
   | km003c-rs | Maintainer: "not against AI ... someone who understands". Re-implements contributions and credits the contributor. |
   | transformers | Asks first-time contributors not to use code agents for issues or PRs. Not pursued (§6). |
   | HF community blog | "LLM-generated blog posts will be hidden"; repeat authors may lose access. |
   | arXiv | Disclose significant generative-AI use. CS review and position papers need prior peer review. |

4. **Running upstream code.** Agents do not execute unvetted community code, so Ed either runs these himself or approves a named sandbox:
   - mlx-vlm main, for the D1/F1 repro. The venv `/private/tmp/jwsol/venv-mlxvlm` already exists.
   - A llama.cpp build plus `convert_hf_to_gguf.py` (B).
   - `cargo test` in km003c-rs, after reading `build.rs` and its dependencies (D).
   - `mlx_lm.server` v0.32.2 (C).
   - A zeus-apple-silicon source build (G).
   - ControlArena main plus the `caf0324` shade-arena wheel (Q).
   - `codecarbon==3.3.2` plus macmon 0.11.0. Ed decides whether a Homebrew macmon counts as vetted (F).
   - A third, isolated mlx-lm-main venv on mlx ≥ 0.32.3 (I, K).

   Recommendation: approve throwaway venvs under `/Users/edr/code/CapstoneProject/jw-wt/` for A, C, F, Q. Ed builds B, D and G himself.
5. **Commit signing.** Set up SSH commit signing on GitHub before the first upstream push. mlx-vlm's bot flags unsigned commits, and the open issue #2692 and PR #2693 would make signing a rule.
6. **One desk-capture kit for the magistrate.** E, F (stage 2), G and M each need a fresh, unregistered capture taken outside every measurement window and outside every custody path. The default is a single kit of about 1.5-2 h of MBP time:
   - a KM003C stream;
   - SMC B0AC, B0AV, PDTR, PSTR and PPBR at 1 Hz;
   - powermetrics rails;
   - an IOReport sidecar;
   - `dump_channels` and `check_compatibility.py` for zeus-apple-silicon;
   - loads stepping idle, CPU-only, GPU-only and LLM decode, with sharp edges, plus one battery-assist segment.

   The Air-side alternative for G and F's evidence is to move the meter to the M4 Air, a chip Zeus already supports. Ed decides where the meter lives. The MBP stays on macOS 26 (25G83) and must not be upgraded to test macmon's macOS 27 path.
7. **Release ruling for the SMC journal (item O).** The Mac15,9 R0 SMC journal is under `night-*` custody, and agents cannot read it. A per-chip thermometer inventory needs a structure-only export: key, type, idle median, rise, tau, noise, class and reason, with no timestamps or run IDs. Default: export after R1 classification is frozen, done by Ed or the magistrate.
8. **qwen4_exp in mlx-lm (item I).** Default: offer only the torch-free test to #1788, and GOAL item 10 (an upstream PR) stays closed. Ed decides on a full PR only if #1788 stays silent for about two weeks after his comment.
9. **Flash-Next maxfit weights (item J).** Default: defer, and lead with the reference dataset (H). If the weights do go up, Ed decides:
   - whether to upload the 102 GB n-gram file or ship a script that rebuilds it bit-exactly from Qwen's own shards (recommended);
   - which namespace to use, and whether to buy HF PRO.
10. **Timing of write-ups against Paper 1.** Default: the Mac energy guide (M) may first go out methods-only. The figures "boundary moves about 1 J" and "37 of 50 phases unresolvable" are Paper 1 headline diagnostics; they wait for the Paper 1 preprint and are then cited. The HF blog needs either a PRO account or membership in a Team org, so Ed confirms which he has.
11. **Item T's "advisor critique" lesson.** No repo document records it; it rests only on Ed's 2026-11-06 remark. Ed either supplies the wording or the lesson is cut.

**Lead rulings recorded here** (the lead owns prereg rulings and obvious process calls; Ed is told after):
- *Item S:* the active-bytes counts are format arithmetic, not outcomes. However, `configs/bytes/bytes_manifest.json` is a frozen input to the sealed BYTES analysis: its hash is committed in `predictions.json`, and the registration's manifest table is still an unfilled ⟦MAC⟧ slot. So:
  - nothing ships from the frozen file;
  - public counts are re-derived fresh from public headers with the new tool;
  - no item claims that bytes per token predicts decode energy, since that is BYTES hypothesis H1.
- *Item P:* `phase_detect.match_tool_calls`, `ToolCallMatch`, the `tool_wait` relabel, `energy_residual.py` and `tamper.py` are energy-as-monitor science. They stay embargoed until the ALIGN paper and are excluded from every package.
- *Item T and item U:* items are prepared on lanes now and published only after their registered releases.

---

## 3. Ranked table

Items are ranked by value to the community times readiness, divided by effort. **Readiness** has four levels:
- *Ready:* the kit exists and only Ed's time is needed.
- *Prep:* agent work on the Air, then Ed.
- *Capture:* needs the desk-capture kit (decision 6).
- *Gated:* waits on the MBP live run, hardware or a registered release.

Effort is active working days. Upstream review wait comes on top.

| # | Item (§) | Target | Form | Verdict | Value | Readiness | Existing equivalents | First step | Effort |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A. mlx-vlm qwen4_exp defects: D1 ragged-batch QSA, F1 `indexed_attention`, P5 padded no-cache (§4.A) | Neywa-Labs/mlx-vlm | Issue, then a PR per defect; D1 first | D1 go; F1, P5 go-with-changes | High | Ready (kit on `port/qwen4-exp-mlx`; patches apply to main `a54f1a0d`) | None upstream; transformers already behaves correctly | Ed: enable signing, re-run the repro, write the D1 issue | D1 0.5-1 Ed-day; F1 0.5; P5 0.25-0.5 |
| 2 | C. mlx-lm server maps `reasoning` back to `reasoning_content` (§4.C) | ml-explore/mlx-lm | Issue, then a 2-3 line PR plus a test that fails on main | go-with-changes | High (every multi-turn Qwen agent loop) | Prep (Ed's repro on the stock server) | vLLM mirrors the field (precedent); nothing in mlx-lm; in #704 maintainers call it the client's job | Ed: cached_tokens repro with Qwen3.5-0.8B-4bit | 1-1.5 |
| 3 | B. llama.cpp converter drops QSA for `indexed_attention` (§4.B) | ggml-org/llama.cpp | Issue, then one PR (fix plus unittest) | go-with-changes | High and rising (every checkpoint re-saved with transformers ≥ 5.18) | Prep (agent drafts the test; Ed builds and runs) | vLLM and SGLang accept both names; nothing in llama.cpp | Ed: convert a tiny config, dump `compress_ratios` | 1-1.5 |
| 4 | D. km003c-rs integrates re-delivered samples twice (§4.D) | okhsunrog/km003c-rs (+ protocol-research docs) | Failing `#[test]` plus an issue; docs PR | go-with-changes | Medium | Prep | None | Agent drafts the Rust test; Ed runs cargo | 0.5-1 (+0.5-1 docs) |
| 5 | H. Flash-Next quality reference from the transformers chain, plus a scorer (§4.H) | HF Hub dataset (+ script) | Dataset, card, numpy scorer | go-with-changes | High (independent reference; can settle a disagreement between engines) | Prep (Air CPU); preservation is urgent | jyohukuchan bf16 logits (32 GB); two mlx-kld tools; KL figures on quant model cards | Preserve head outputs; re-capture fp32 and bf16 at K = 64 and 4096 | 3-5 |
| 6 | F. CodeCarbon's Apple Silicon undercount, then a backend (§4.F) | mlco2/codecarbon #731, #752, #1269 | Data comment, then restart #752 or build the #1269 SMC leg | go-with-changes | High (reach) | Stage 1 Prep (Air capture); stage 2 waits for maintainers | #752 (stalled); macmon 0.11.0 | Air: table of codecarbon 3.3.2 vs macmon vs SMC | 1, then 4-8 |
| 7 | G. zeus-apple-silicon: M3 Max support and rails vs whole-machine (§4.G) | ml-energy/zeus-apple-silicon | Chip PR (mocks); evidence issue | go-with-changes | Medium-high | Capture | No M3 Max support; no meter validation anywhere | Ed vets the code; magistrate runs `dump_channels` | 0.5 + 2-3 |
| 8 | E. SMC PDTR, PSTR and PPBR checked against a meter (§4.E) | vladkens/macmon #117 (pointer on #118), mactop, stats | Data comment plus public CSV | go-with-changes | Medium-high | Capture | No published meter validation; macmon already reads PSTR | Desk-capture kit to the magistrate; fit script on the Air | 1-1.5 |
| 9 | L. HF-to-MLX numerical parity pitfalls, plus the streamed parity harness (§4.L) | Blog or HF article; mlx-lm docs; PyPI later | Probes repo and guide; package in phase 2 | go-with-changes | Medium-high | Prep (re-verify the numbers against torch) | transformers-to-mlx `compare_layers.py`; pcuenca/mlx-lm-tests | Probe scripts run in `venv-both` | 3-4 (+8-20 package) |
| 10 | M. Practitioner guide to measuring LLM energy on a Mac (§4.M) | Blog or HF article; ML.ENERGY and mlx-lm communities | Ed-written guide and checklist | go-with-changes | High (reach) | Prep; the headline numbers wait for Paper 1 | ML.ENERGY Mac post (tooling only); GreenBench; Contra Collective wall-meter study | Provenance table | 4-6 |
| 11 | I. qwen4_exp in mlx-lm (§4.I) | ml-explore/mlx-lm #1788 | Torch-free pinned test offered to #1788; a PR only if #1788 stalls and Ed says go | go-with-changes | Medium-high | Gated (MBP live run; module reshape) | #1788 (stalled); mlx-vlm and llama.cpp already support the model | Run the upstream-shape suite against the canonical module | 1.5; PR 2-4 weeks |
| 12 | S. Active bytes per decoded token (§4.S) | alvarobartt/hf-mem; small script or dataset | Issue first; stripped script | go-with-changes | Medium | Prep | hf-mem (misses stacked experts; no per-token line) | Ed: hf-mem issue with 3 fresh test vectors | 0.5-1.5 |
| 13 | N. Quiet-machine benchmark checker (§4.N) | Own repo or PyPI; mlx-lm Discussion; llama.cpp #4167 | Stdlib script and write-up | go-with-changes | Medium | Prep | mlx-Chronos (no contention or Spotlight checks) | Recover the Spotlight doc; vendor the probes | 3 (+4-5 package) |
| 14 | K. Perf write-up for hybrid MoE in MLX, plus the QSA kernel (§4.K) | Blog; mlx#4509; mlx-lm kernels later | Write-up; benchmark; kernel PR later | go-with-changes | Medium | Prep, then Capture (M3 Max bench), then Gated (kernel PR) | mlx-vlm `qsa_kernel`, `moe_offload`; mlx-serve; kiarina's post | Kernel-vs-kernel benchmark on the Air | 1 + 2-3 |
| 15 | Q. ControlArena shade_arena defects and local-model docs (§4.Q) | UKGovernmentBEIS/control-arena; inspect_ai #6246 | Issue, fix PR, docs section | go-with-changes | Medium | Prep (Ed approves a sandbox) | ControlArena already works with any provider | 3 mockllm repros | 2-3 (+1-2 docs) |
| 16 | O. SMC thermometer classifier and per-chip inventory (§4.O) | macmon #12/#68; exelban/stats; iSMC | Method note and tables | go-with-changes | Medium | Prep, plus an export ruling | OSHI 15 °C floor; iSMC `guess`; Stats key lists | Standalone probe script; Air inventory | 2.5-5 |
| 17 | P. `inspect-energy` hooks (§4.P) | Own PyPI package plus Inspect's extensions listing | Package plus a one-line listing PR | go-with-changes | Medium | Prep | Nothing in Inspect; zeus-apple-silicon complements it | Characterise SMC cadence on the Air | 3.5-5 |
| 18 | J. Flash-Next maxfit MLX build (§4.J) | HF Hub model repo | Weights and card | go-with-changes (deferred) | Medium | Gated (MBP live run; POLICY) | Many 128 GB quants that publish fidelity | Fix the `resolve()` bug; card generator | 3-4 |
| 19 | R. windowed-energy attribution package (§4.R) | Own PyPI package plus methods note; Zeus later | Package | go-with-changes | Medium-low | Prep | Yang et al. 2023; ruptures; TokenPowerBench | Extract Trace types and attribution | 8-11 |
| 20 | V. Zeus Jetson INA3221 improvements (§4.V) | ml-energy/zeus | Issue and PR | go-with-changes | Low-medium | Gated (Orin hardware) | Zeus `jetson.py`; jtop | Fix the macOS test failures | ~5 |
| 21 | T. Templates for preregistered, blinded analysis (§4.T) | Own template repo plus note | Templates and write-up | go-with-changes | Medium | Gated (Block 5 release) | OSF; NeurIPS prereg workshops; arXiv 2605.28873 | De-B5 the templates on a lane (no publishing) | 6-10 |
| 22 | U. Open dataset of Apple Silicon inference energy (§4.U) | HF and/or Zenodo; ML.ENERGY | Staged dataset and datasheet | go-with-changes | Highest long-term | Gated per release | None equivalent | Stage-0 contract and exporter, run on mocks | 5-7, plus per stage |
| — | W. transformers top-k tie-break (§6) | huggingface/transformers | — | not-worth-it | — | — | — | Fix the wording of `canonical.md` deviation 7 | 0.25 |

---

## 4. Items

Each section lists the candidate entries it merges, what the contribution is, the verifier's verdict, existing equivalents, what has to change, the first step, effort, and gates. Verifier facts are dated 2026-11-07 unless stated.

### 4.A mlx-vlm qwen4_exp defects (D1, F1, P5)

*Merges:* "mlx-vlm qwen4_exp defect kit", "mlx-vlm qwen4_exp D1", and the mlx-vlm half of "`indexed_attention` layer type".

- **What.**
  - **D1.** In left-padded batches (decode and MTP verify), every QSA layer computes its top-512-block selection and then attends densely anyway. Any row with 2052 or more visible tokens diverges silently from the same request served alone, and from transformers.
  - The kit is on `origin/port/qwen4-exp-mlx` in `docs/align/upstream_mlxvlm_d1/`. It contains:
    - `FACT_SHEET.md` and `WALKTHROUGH.md`;
    - `fix.diff` (+11/-16, one file, `language.py`);
    - `repro_minimal.py` (exit 1 means the bug is present);
    - `test_qwen4_exp_ragged_qsa.py`;
    - `evidence/` (13 files, including `fix_plus_test_in_test_cache.diff`);
    - an independent reviewer's mutation test.
  - **F1.** transformers ≥ 5.18 (PR #48974, merged 2026-09-22) rewrites `full_attention` to `indexed_attention` on load and save. mlx-vlm `config.py` line 98 maps only `full_attention`, and line 115 rejects `output_gate_type=None`, so re-saved checkpoints refuse to load. The patch is `scripts/audit_mlxvlm/f1_indexed_attention_layer_type.patch` (+10/-2).
  - **P5.** A padded batch scored without a cache ignores the mask. `p5_padded_no_cache.patch` (+15) is a guard that fails loudly; it is not a fix.
- **Verdict.**
  - D1: **go**.
  - F1: go-with-changes. It needs a pytest test. The error string still says "must be sigmoid or silu" after `None` is allowed. Frame it as transformers' canonical name, which vLLM and SGLang already accept, not as a checkpoint quirk: a maintainer closed the compatibility shim in #2114 saying "supporting every busted conversion ... seems like a mistake".
  - P5: file an issue first, and offer either the guard or a row-wise fallback.
- **Existing equivalents.**
  - None upstream: 18 read-only searches found nothing. The `qwen4` issue search returns only #2581, #2526, #2048 and #2041.
  - Related but not overlapping: #2345/#2357, #2197, #2581/#2630 (hunks at lines 2001-2100), and #2521.
  - `language.py` (blob `9a9bee24`) is byte-identical at the kit's base `5cdc659b` and at today's main `a54f1a0d`, and `fix.diff` passes `git apply --check`. PyPI 0.7.12 carries all three bugs.
  - On F1's exposure: all 15 sampled Flash-Next derivatives on HF were saved with transformers 5.8-5.16, so none carries `indexed_attention` yet. Every checkpoint re-saved from now on will.
- **What must change.**
  - *The value claim.* Do not say Qwen's README recommends mlx-vlm for Apple silicon. That claim is unverified (it is cited in GOAL.md:7); the HF card recommends SGLang, KTransformers and vLLM. The defensible framing is that mlx-vlm is the only MLX runtime for Flash-Next.
  - *Re-running.* Ed re-runs everything against `a54f1a0d`. Expect exit 1 before the fix and exit 0 after, with 30 existing tests and 2 new ones passing.
  - *Internal paths.* Fix the hard-coded paths in `evidence/rerun_all.sh`, `evidence/insitu.py` and FACT_SHEET §12. These files are internal only and are never posted.
  - *Tests.* F1 and P5 need tiny-config pytest tests.
  - *Expected D1 pushback.* After the fix, ragged rows match in fp32 to about 3e-7. Against singleton requests in bf16, though, they are about 1 ulp off, and #2126 was about bitwise singleton parity. Keep the kernel-aware alternative (FACT_SHEET §9 Q2) ready.
  - *Thread discipline.* Keep F1, P5, P3 and P4 out of the D1 thread. Use one contributor identity: D1 first, then F1 and P5 only after a maintainer responds.
  - *Test placement.* The kit appends to `tests/test_cache.py`, which avoids regrouping `tests.yml`. The repo's contributing skill prefers `test_models.py`, so be ready to move the test.
- **First step.** Ed:
  1. Enables commit signing.
  2. Adds a worktree of `origin/port/qwen4-exp-mlx` under `jw-wt/`.
  3. Reads FACT_SHEET, then WALKTHROUGH (2-3 h).
  4. Runs `PYTHONPATH= /private/tmp/jwsol/venv-mlxvlm/bin/python docs/align/upstream_mlxvlm_d1/repro_minimal.py`, then again against the fixed checkout.
  5. Runs the pytest selection (`-k "qwen4 or qsa or QSA"`) and pre-commit.
  6. Writes the issue in the repo's reproducible-issue structure (Summary, Environment, Model, Reproduction, Expected, Actual). It carries the repro output and the code path from FACT_SHEET §3.2, and assigns no blame for #2126.
  7. About a day later, opens `fix/qwen4-exp-ragged-qsa-decode` with "Fixes #N" and a one-line AI disclosure.

  Optional agent prep (~1 h): fix the internal paths and draft the F1 and P5 tests for Ed to review.
- **Effort and gates.**
  - D1: 0.5-1 Ed-day, then 1-12 days elapsed for review (one approval from lucasnewman is typical).
  - F1: about 0.5 day. P5: 0.25-0.5 day.
  - No MBP time, no sealed data, no custody coupling: the repro and the test import only `mlx` and `mlx_vlm`.
- **Policy.** MIT. No CLA, no DCO, no AI rule. Pre-commit runs black 26.3.1, isort and autoflake. One review is required.

### 4.B llama.cpp converter drops QSA for `indexed_attention`

*Merges:* "llama.cpp converter: accept transformers' `indexed_attention`" and the llama.cpp half of "`indexed_attention` layer type".

- **What.** `conversion/qwen4exp.py:86-91` writes a compress ratio only when the layer type is literally `"full_attention"`. After the transformers rename, all 12 main QSA layers get ratio 0; only the appended MTP block keeps ratio 4.
  - At runtime, `src/models/qwen4exp.cpp:1018-1019` reads "no cache or no ratio means dense". Lines 62-78 skip zero ratios when deriving `indexer_kpool`. The indexer tensors still load (lines 261-273 build them by recurrence, not by ratio) but go unused.
  - Net effect: silent dense attention, with no warning. Output diverges from the reference beyond `indexer_budget + ratio` = 2052 tokens.
  - Describe it as "diverges from the reference beyond about 2k tokens, without any warning". Do not call the output "garbage". This was confirmed by reading the source only.
- **Verdict.** go-with-changes.
- **Existing equivalents.**
  - None in llama.cpp: a code search finds 0 hits for `indexed_attention`, and the 18 open qwen4exp PRs do not touch layer-type handling.
  - vLLM accepts both names (`vllm/config/model.py:119-125`, and `_QSA_LAYER_TYPES` in its qwen4_exp model). SGLang handles the new name too.
  - Correction to the earlier shortlist: vLLM #59756 is an issue, not a PR.
- **What must change.**
  - *A fresh regression test with no transformers dependency.* It follows `tests/test_conversion_fp8.py` (its `_convert` with `hparams_override`) and uses tiny hparams:
    - `layer_types=['linear_attention','indexed_attention']`, `indexer_compress_ratio=2`, `indexer_budget=4`;
    - it asserts that `compress_ratios == [0, 2]`, plus the MTP entry if exported;
    - on master it fails with `[0, 0]`.
    - Register it in `tests/CMakeLists.txt` (label `python behavior`), or give the run command in the PR. Neither test file appears to be wired into CI.
  - *Reuse.* JouleWise's F1 repro and patch target mlx-vlm and cannot be reused here.
  - *The fix design is Ed's choice.* Option (a) is `!= "linear_attention"`. Option (b) is an explicit set {`full_attention`, `indexed_attention`, `qwen_sparse_attention`}, matching transformers' `_LEGACY_LAYER_TYPE_REMAP`, plus a raise on any unknown type. The lean is (b).
  - *Confirmation on Ed's own checkout.* Dump `attention.compress_ratios` with gguf-py. Optionally, `llama-eval-callback` should show no `indexer_*` nodes on the main layers. Also optional: a real-weight logit comparison of `indexed_attention` against `full_attention`.
  - *Style.* ASCII only, plus the Python type check. Code owner for `/conversion/` is CISC.
  - *Open PRs.* Check that Ed has no other open llama.cpp PR; the verifier's check was rate-limited.
- **First step.** An agent writes the test file outside any llama.cpp clone, plus a fact sheet containing the file:line citations and the HF derivative survey, with no prose meant for upstream. Ed clones master, runs the test (fails), applies his fix (passes), writes the issue, and after it is up opens the single PR.
- **Effort and gates.** About 1-1.5 days, including the build and runtime confirmation. Add 0.5 day for the optional real-weight check. Must be Ed's first and only open llama.cpp PR.

### 4.C mlx-lm server: map `reasoning` back to `reasoning_content`

*Merges:* both "mlx-lm server reasoning" entries.

- **What.** The server sends thinking out as `message.reasoning` (`server.py` around line 1527), but `process_message_content` (line 212) never maps an inbound `reasoning` to `reasoning_content`. The Qwen3.5/3.6/3.8 templates read only `reasoning_content`.
  - A client that echoes the returned message therefore loses the thought from the rendered history.
  - Turn 2's prompt can also stop extending the cached prefix. A hybrid `ArraysCache` cannot be trimmed, so the server falls back to an earlier cache.
- **Scope.**
  - The official Qwen3.5/3.6 templates render `<think>` only for assistant turns after the last user query, i.e. inside the current tool chain. With `preserve_thinking=true` on 3.6 they render it for all turns.
  - The Qwen3.8 template keeps thinking by default.
  - Lead with Qwen3.5-0.8B. The 3.8 fixture comes from a mutable `main` revision.
- **Verdict.** go-with-changes.
- **Existing equivalents.**
  - None in mlx-lm. A code search finds `reasoning_content` only in `chat_templates/deepseek_v32.py`, and no issue or PR covers it.
  - Maintainer position in #704 (closed): clients should send `reasoning_content` back.
  - #903 (open) is the umbrella issue for Qwen3.5 caching. #1841 (closed, not merged) was a model-specific normalisation.
  - Precedent: vLLM `chat_message.py` mirrors `reasoning` into `reasoning_content`, tested in `test_assistant_reasoning_is_mirrored_to_reasoning_content`.
  - llama.cpp accepts `reasoning_content` inbound. froggeric's template PR #88 independently confirms the mismatch.
- **What must change.**
  - *The numbers.* The "119 bytes invalidated per turn vs 0" figure is not an `mlx_lm.server` measurement. It came from JouleWise's own `MlxEndpoint`, with a synthetic stream and a simulated negative control. Do not cite it.
  - *The re-measurement.* Re-measure on stock `mlx_lm.server` v0.32.2 with `mlx-community/Qwen3.5-0.8B-4bit`, using `usage.prompt_tokens_details.cached_tokens`. Keep thinking enabled, to isolate the field name from the separate `enable_thinking=false` drift (QwenLM/Qwen3#1826).
  - *The client claim.* One verifier confirmed that Inspect's `default_reasoning_handler` echoes back the same key it received. The other marked client behaviour unverified. Show one real client in the issue, or drop the claim.
  - *The patch.*
    - 2-3 lines, assistant messages only.
    - Copy when `reasoning_content` is absent and `reasoning` is a string; never overwrite.
    - Test in `tests/test_server.py` that fails on main, and that leaves user messages and reasoning-free messages unchanged.
    - Optionally a second test that renders a tiny inline template.
    - No JouleWise code, and no Qwen template fixture: Apache-licensed and mutable.
  - *The issue.* Answer #704's position before maintainers raise it: the server does not accept its own output key back. Link #903 and cite vLLM.
- **First step.** On the Air, Ed runs stock `mlx_lm.server` with a two-or-three-tool-call chain in which the client appends each returned message unchanged, and records `cached_tokens` per turn. He repeats the run with a client-side rename. If the first run falls back and the renamed run extends the cache, he writes the short issue. The PR follows only after a maintainer replies.
- **Effort and gates.** 1-1.5 days. Triage is heavy (#1146 was closed in the 2026-08-21 capacity purge), so open the issue first and keep the PR minimal. The PR occupies Ed's mlx-lm open-PR slot, so it goes before anything from I or K.

### 4.D km003c-rs integrates re-delivered samples twice (plus protocol docs)

*Merges:* "KM003C USB-C meter: stdlib reader + parser + monitor" and "km003c-rs: sample re-delivery is integrated twice".

- **What.** In `km003c-lib/src/measurement.rs` (main, pushed 2026-11-04), `MAX_CONSECUTIVE_REJECTED_SAMPLES = 8` (line 24). The eighth reject sets `previous = None` (lines 132-134), so any re-delivery longer than 8 samples restarts continuity and its remainder is integrated a second time.
  - `tests/fixtures/km003c/redelivery1000_slice.jsonl` contains a real 27-sample re-delivery at 1000 SPS: a backward step from 49816 to 49790 at sample 567 of 1227.
  - The verifier re-implemented their `push()` logic (not their code) and ran it on the fixture. Result: elapsed 1217 ms against a true 1199 ms. That is +18 ms, about 1.3 J per event at the slice's 73.3 W mean. JouleWise's parser drops all 27 samples.
- **Verdict.** go-with-changes:
  - (a) an issue plus a failing test;
  - (b) a docs PR to km003c-protocol-research, without the clock-drift claim;
  - (c) a standalone PyPI package, deferred; it is close to not worth doing.
- **Existing equivalents.**
  - No report of the bug among all 66 issues and PRs.
  - PyPI `km003c` 0.4.0 is km003c-rs's own binding, so it carries the same bug.
  - `adcqueue.md` documents the sequence counter but not re-delivery. Its dropped-sample snippet, `(seq - last) & 0xFFFF`, reads a re-delivery as about 65 s of dropped samples.
  - The plaintext MemoryRead fix for firmware 2.0.5 is already upstream (#62/#65) and is not ours.
- **What must change.**
  - *Severity, stated honestly:* "biases elapsed time and energy upward by (N - 8) sample periods per re-delivery longer than 8 samples". We know the frequency only at 1000 SPS.
  - *The test.* A Rust `#[test]` in the `measurement.rs` tests module using its `sample()` helper. Either replay the real sequence numbers and assert `elapsed_us == 1_199_000` with 27 discarded (main gives 1_217_000 and 8), or use the synthetic version: push 49790..=49816, re-push the same run expecting `None` each time, then `push(49817).elapsed_us == 27_000` (main gives 45_000).
  - *Fixes, offered rather than pushed:* a high-water mark of unwrapped device time, with host arrival time used only to tell a stall longer than half a wrap from a re-delivery.
  - *Docs PR content:* a re-delivery subsection, a signed 16-bit difference snippet, and the 63-samples-per-PutData cap.
  - *The clock note.* At most one optional line, labelled as single-meter evidence: +1.4 and +2.2 ppm against `CLOCK_MONOTONIC_RAW` on 20-30 s fixtures. Drift of a few ppm does not matter for energy. The −224 ppm from the 1.2 s slice is not evidence.
  - *Scrubbing.* Redact the meter serial and hardware ID from any fixture excerpt, and strip the night-archive provenance.
  - *Out of scope:* the SMC battery term and the clock fitting.
- **First step.** An agent drafts the test and an issue fact sheet locally in `jw-wt/`; nothing is posted. Ed reads `build.rs` and the dependency list, runs `cargo test -p km003c-lib measurement` to watch it fail, and writes the issue.
- **Effort and gates.** 0.5 day, plus about 0.5 day for vetting. Add 1 day if Ed writes the fix PR and the maintainer does not re-implement it (he usually does, and credits the contributor), and 0.5-1 day for the docs PR. The maintainer will ask for hardware verification at 50 and 1000 SPS, which only Ed can provide.
- **Policy.** km003c-rs is MIT OR Apache-2.0; the research repo is MIT. Neither has a CONTRIBUTING file or a CLA.

### 4.E SMC power keys checked against a meter (macmon, mactop, stats)

*Merges:* "Apple SMC reader, key census and power-key validation" and "macmon / mactop: meter validation".

- **What.** A table checking PDTR (DC input), PSTR (system) and PPBR (battery) against the KM003C plus the battery term (−B0AC × B0AV).
  - Loads: idle, CPU-only, GPU-only and LLM decode.
  - Each key's refresh period and lag are reported separately from its gain.
  - Machine: Mac15,9 (M3 Max), macOS 26 (25G83), 140 W adapter on a 28 V EPR contract. Add the M4 Air if it is measured too.
- **Verdict.** go-with-changes. The data is new; our reader code duplicates macmon's.
- **Existing equivalents.**
  - No published external-meter validation was found anywhere.
  - macmon reads PSTR as `sys_power`. PR #118 (homm, open, 0 comments) adds `dc_in_power` (PDTR), `battery_power` (PPBR) and `display_power` without validation.
  - On #117 the maintainer tested M1, M2 and M5: `dc_in_power` works, and `battery_power` is "wrong on AC" on all three and will be removed. He also says #118 becomes unnecessary once `chip_power` replaces `all_power`.
  - macmon's `agents.md` says: "Power-source readings need verification against an independent reference." `clpc-discovery.md` asks for the same.
  - Elsewhere: #77 (closed) did an M3 Max load-response check without a meter. Stats labels the keys without validation. mactop #96 reports PSTR and PDTR reading 0 W on an M5 Ultra under macOS 27. macpow calls these readings "direct" measurements.
- **What must change.**
  - *Where to post.* On #117, where decisions are made, with a one-line pointer on #118.
  - *Custody.* Do not cite the pooled in-repo PDTR slope upstream. Its 12 sources are the study's session meter streams, so treat the pool as containing Block 5 data. The "within about 1.4%", "−865 mA" and "B0AC at 1 Hz" findings trace to a night-archive probe and are public only as prose. Every number posted upstream comes from the fresh, unregistered desk capture (decision 6), with its raw CSV published.
  - *Separate gain from lag.* The in-repo slope mixes them, shifting about −0.014 per second of lag. Report the plateau ratio per load, each key's refresh period, and the lag from step-response cross-correlation.
  - *Cover all three keys.* Check PPBR's sign and magnitude against −B0AC × B0AV and against PSTR − PDTR. This needs a battery-assist segment.
  - *Correct the pitch.* A DC-input meter cannot validate macmon's CLPC CPU/GPU/ANE mappings directly; at most it gives delta-from-idle bounds. The MBP runs macOS 26, so macmon's macOS 27 path stays untested. The KM003C is an uncalibrated consumer meter, so "agreement" means agreement with that meter.
  - *No code goes upstream.* Publish a standalone stdlib analysis script and the CSV in a public JouleWise folder (for example `docs/upstream/smc-meter-validation/`).
- **First step.** The protocol goes into the combined desk-capture kit (decision 6). In parallel, an agent writes the fit script on the Air and tests it on synthetic streams: plateau ratios, refresh periods, cross-correlation lag, PPBR sign, and PSTR against meter plus battery term. Ed writes the comment from the resulting table, then links the same table from mactop and stats if it is well received.
- **Effort and gates.** 1-1.5 days, plus 30-60 min of magistrate time. An optional macOS 26 CLPC cross-check through a vetted macmon build adds about 1 day.

### 4.F CodeCarbon on Apple Silicon

*Merges:* "CodeCarbon Apple Silicon backend: adopt or validate #752" and "CodeCarbon flagship".

- **What.** CodeCarbon's dispatch tries psutil `cpu_load` before powermetrics. Apple runs therefore report a TDP-times-load model for the CPU and 0 for the GPU, and `methodology.md` says powermetrics is "effectively unreachable" (verifiers cite lines 129-152 and 149).
  - **Stage 1.** A measured undercount table on an mlx-lm decode run.
  - **Stage 2.** A backend.
- **Verdict.** go-with-changes. Both verifiers say to drop the plan for our own IOReport rail reader. It would duplicate macmon, which already provides rails, the macOS 27 CLPC workaround and PSTR `sys_power`. Maintainers chose a macmon CLI subprocess in #731 ("we are not going to copy the code rather use your library"). And CodeCarbon's AI policy (Law 2) rejects reinvented helpers.
- **Two viable stage-2 shapes.** Ed's first post asks the maintainers to choose:
  - (i) **Restart #752** on the current master: the macmon subprocess backend, about 150-250 lines, 4-6 days.
  - (ii) **The macOS leg of #1269**, an opt-in whole-machine backend. It reads SMC PSTR, PDTR and PPBR plus the B0AC × B0AV battery term, by porting `joulewise/hazards/smc.py` with its fake transport, or through `macmon pipe` JSON. About 5-8 days.
- **Existing equivalents.**
  - #752 (opened 2024-12-20) is "dirty" against master, its docs edits target a deleted Sphinx tree, it got a closure warning on 2026-10-09, and a maintainer asked a colleague to take it over.
  - macmon 0.11.0. macmon-lib exists but was not opened (unverified). zeus-apple-silicon; actop.
  - arXiv 2509.22092 reports CodeCarbon errors, on non-Apple hardware.
  - Nobody has published a CodeCarbon-vs-meter comparison on Apple Silicon.
- **What must change.**
  - *Stage 1 runs on the M4 Air, not the MBP.* For a 60 s mlx-lm decode, compare:
    - `codecarbon==3.3.2` with default settings;
    - `macmon pipe -i 100`;
    - SMC PDTR and PSTR via `joulewise.hazards.smc.read_once`.

    Tabulate joules and watts against an idle baseline, and state the sampling design (CodeCarbon's 15 s against macmon's 100 ms).
  - *If restarting #752:*
    - use `macmon pipe -s N -i MS` (current argument order);
    - parse JSON lines with `json` and `statistics`, not pandas;
    - add a subprocess timeout (as #1397 does);
    - treat all-zero CPU/ANE readings as "unavailable", per macmon's README;
    - report the GPU through the existing `AppleSiliconChip` pattern;
    - insert the check in `_try_platform_cpu_backend` before the psutil row;
    - update the methodology rows;
    - add tests driven by a recorded JSON-lines fixture.
  - *Code reuse.* Only `smc.py` crosses over, if anything, after scrubbing its night-archive docstring. `battery.py` and `battery_float.py` carry custody machinery and are not ported.
  - *Stage-2 validation figures.* These come from the desk capture, never from sealed sessions.
- **First step.** Ed reads `docs/how-to/ai_policy.md` and picks his disclosure tier. An agent prepares the Air capture script. Ed approves the venv and runs the capture. Ed writes the #731 comment, cross-linking #1269 and CodeCarbon's own methodology line, and ends it with the two scope questions:
  1. Is the macmon CLI dependency still the plan?
  2. Should `sys_power` be a whole-machine field, or wait for #1269?
- **Effort and gates.** Stage 1: 1 day. Stage 2: 4-8 days, plus weeks of review.

### 4.G zeus-apple-silicon: M3 Max support and rails vs whole-machine evidence

*Merges:* the Zeus parts of "Whole-machine energy measurement method" and "Zeus / zeus-apple-silicon".

- **What.**
  1. **M3 Max chip PR.** Run `examples/cpp/dump_channels` and `examples/python/check_compatibility.py` on the Mac15,9. Add mock cases to both `tests/tests_cpp/test_monitor.cpp` and `tests/tests_python/test_monitor.py`, including channels that must be ignored (SRAM, DTL). Add the README's tested-chips row.
  2. **Evidence issue.** Compare IOReport rail energy (`AppleEnergyMonitor`) with KM003C whole-machine energy over prefill and decode windows of one LLM run. Report the rail share (rho) and whether it is stable between phases. Explain how about 1 J can move between phases at a steep power change, and the rule that a phase covered by fewer than 3 sampler records is not resolvable.
- **Verdict.** go-with-changes.
- **Existing equivalents.**
  - M3 Max is absent; re-verified today. The tested chips are M1 Max, M3 Pro, M4, M4 Pro and M5 Max. The repo has never had an issue, and its 9 PRs are all by maintainers.
  - The README says IOReport values are "believed to be model-based estimates". RFC #159 never discusses accuracy.
  - Nearest prior art: an HN post comparing SMC system power with powermetrics on an M4 Max, without a meter; and Contra Collective's wall-meter J/token study (Kill A Watt, idle-subtracted, no battery term).
- **What must change.**
  - *Our data does not contain this comparison yet.* JouleWise has no IOReport or Zeus code; its rails come from powermetrics. The comparison needs either a fresh capture with a small IOReport sidecar sampler (about 0.5 day), or a reframing as powermetrics vs KM003C that asks maintainers whether the two read the same estimator.
  - *Vetting.* Running zeus-apple-silicon is running community code. Ed vets `apple_energy/apple_energy.hpp`, `dump_channels.cpp` and `check_compatibility.py` at the 2026-04-02 commit (#9) first.
  - *Rig.* The chip PR needs the MBP. The evidence capture can use the MBP desk slot or the Air with the meter moved (decision 6).
  - *The "about 1 J" and "fewer than 3 records" figures* are diagnostic-era. Present them as mechanism, not as results, and quote no D-078 values.
  - *Framing rho.* Whole-machine energy includes the display, SSD, fabric and VRM losses, so rho < 1 is expected.
- **First step.** Ed vets the code. During the next daytime non-window desk slot, the magistrate builds and runs `dump_channels` and `check_compatibility.py` (about 15 min) and saves the output under `jw-wt/`. That output is all the chip PR needs.
- **Effort and gates.** Chip PR: 0.5 day once the dump exists. Evidence issue: 2-3 days, about 1 of them MBP desk time.
- **Policy.** Apache-2.0, inbound = outbound. No CLA or DCO. Issue first. Tests must not need a GPU; `scripts/run_tests.sh` plus both lint scripts must pass. Maintainers: Jae-Won Chung and Ruofan Wu.

### 4.H Flash-Next quality reference from the transformers chain, plus a scorer

*Merges:* "Compact top-k quant-quality scorer + L3 bf16 reference" and "Flash-Next bf16 top-64 quality reference"; it also absorbs the lead-with-the-reference advice from §4.J.

- **What the reference is.**
  - Source: official transformers 5.22.1 `modeling_qwen4_exp`, run on CPU with torch 2.15, Qwen revision `de4b8e4d`, through the streamed 48-layer gold chain.
  - Contents: 12 prompts and 2,521 positions (the longest 507 tokens). Per token it stores the top-64 ids and logits, the full-vocabulary log-sum-exp, and the teacher-forced logit.
  - File: `records/qwen4/2026-11-07-l3-reference-top64/reference-top64.npz` on `ade3bf7f5` (486,267 bytes, sha256 `6c9dcb7c…`).
- **What the scorer computes.** Top-1 agreement, top-5 overlap, NLL delta, p99 KL, and a projected KL (top-K plus OTHER). The projected KL is a valid lower bound on full KL, because it is a coarse-graining of the full distribution.
- **Verdict.** go-with-changes. Publish it as an *independent, transformers-chain* reference in a compact format. Do not present it as "the" Flash-Next quality reference or as a new tool.
- **Existing equivalents.**
  - **jyohukuchan/qwen38-flash-next-bf16-logits** (HF, 2026-10-24). Full-vocabulary FP32 logits from the official BF16 model at the same revision: 21 cases, 32,359 positions including two 4097-token cases, about 32 GB, its own `compare.py`, qwen-community-1.0. Its engine cross-check *rejects* transformers 5.20.2 qwen4_exp (top-1 agreement 0.31 with exllamav3).
  - Scoring tools: sammcj/mlx-kld (top-K plus tail `.npz`; no license); asher/mlx-kld (PyPI, Apache-2.0, top-K teacher cache, loads only through mlx-lm); llama.cpp `--kl-divergence-base`.
  - Model cards that report KL against bf16: JANGQ JANG_6S, txgsync oQ5e, pipenetwork (dNLL with bootstrap CIs over 296,815 tokens), TheDrainFlorist (top-64 KL), ddalcu.
  - mlx-lm closed a KL command (#1146) for review capacity, so mlx-lm is not a target.
  - What is ours: a reference from the official transformers code path, a sub-MB teacher-free format, and a sound lower bound.
- **What must change.**
  1. **Preserve the head outputs** (§5, day 0). Copy all of `/private/tmp/jwgold-run-l3/work`, or at least `parity/head` plus the manifest and provenance files, to durable non-home storage.
  2. **Re-capture** fp32 and bf16 at K = 64 and at K ≈ 1024-4096 from the existing head outputs. No new gold pass is needed. Tail mass beyond the top 64 averages 0.010, with p99 0.29 and max 0.81, so the K = 64 bound is loose. Store per-position tail mass, and report an mlx-kld-style uniform-tail estimate beside the bound.
  3. **Publish the precision floor.** bf16 scored against fp32 gives mean projected KL 0.0208, p99 0.380, top-1 0.979. That is about the size of JouleWise's own quant acceptance bar (0.02 mean, 0.10 p99). Make fp32 the primary reference and ship bf16 beside it (internal consequence in §7).
  4. **Cross-engine check.**
     - Download only jyohukuchan's `corpus/all-cases.json` and `reference/en_prose_129.f32` (about 128 MB, data only; do not run their `compare.py`).
     - Stream our bf16 chain over those token ids and score with our scorer.
     - This settles whether our 5.22.1 chain behaves like the rejected 5.20.2. Our 88% top-1 on memorised text suggests not, but that is unconfirmed.
  5. **Long context.** Every prompt is at most 507 tokens, so QSA's sparse regime (2052 or more visible tokens) is never exercised. Add public-domain prompts of about 4k tokens: one streamed gold pass, about a day of unattended Air CPU. Profile it first; multi-day runs mean a broken process.
  6. **Decouple the scorer.**
     - Write a numpy-only capture/score of about 150 lines that takes any callable returning logits.
     - Replace the MLX adapter, which is tied to the measurement kit: it refuses to run while launchd measurement agents are loaded, forces `/Volumes/JW-EXT`, and loads through `load_verified_model`. Use mlx-vlm or generic adapters instead.
     - Drop the POLICY classification or label it as an example.
     - Scrub `/private/tmp` paths and internal ruling references from the sidecars, then re-bind the hashes.
     - Make the schema model-agnostic and record the vocab width (248,077 valid ids of 248,320).
  7. **Card.**
     - Method, and the teacher-forced chat template with thinking off.
     - Non-claims: projected KL is a lower bound; only 12 prompts; the continuations are memorised public-domain text (top-1 0.88 there).
     - Per-prompt clustered CIs.
     - The Qwen license notice. Strip the Project Gutenberg trademark text.
  8. **Optional:** an exporter to mlx-kld's cache layout and a converter to sammcj's sparse cache.
  9. **Review the lane.** Two base commits on the quality-ref lane say "cloud Sol ... applied by lead, unreviewed".
- **First step.** Day 0: preserve the outputs. Then, from a worktree of `lane/2026-11-06-qwen4exp-quality-ref`, run `scripts/run_qwen4_quant_quality.py capture` at both K values for bf16 and fp32, score bf16 against fp32, and log tail mass. Then run the cross-engine check. Ed decides on the HF release and writes the card.
- **Effort and gates.** 3-5 days, including about 1 day of unattended CPU. No MBP time and no custody data. Ed publishes under his namespace.

### 4.I qwen4_exp in mlx-lm

*Merges:* "qwen4_exp canonical MLX port, verified against transformers 5.22.1" and "qwen4_exp text-only port for mlx-lm".

- **What.**
  - *The module.* `joulewise/align/models/qwen4_exp.py` is 2054 lines on quality-ref and 2199-2200 on the compiled-decode and port-r2 lanes. It converged from two independent ports (Sol and an Opus twin).
  - *Tiny-config gold parity.* The Sol port reached 6e-8. The canonical module measures 2.5e-6 to 9.8e-6, inside the 1e-4 bound.
  - *Real-weight parity.* Layers 2 and 3 only (PR #669, open, untrusted-audit).
  - *The 48-layer streamed driver* (PR #680) is written but has run only natively on the tiny model, never on real weights.
- **Verdict.** go-with-changes. Contribute verification evidence to #1788 first. A separate PR is a *different, upstream-shaped* module, built only if #1788 stalls and Ed says go.
- **Existing equivalents.**
  - #1788 (eauchs): open, labelled "await verification", head `2097324` unchanged since 2026-09-26, last activity 2026-10-04. mlx-lm main has no `qwen4_exp.py`.
  - mlx-vlm supports the model (#2032, merged 2026-08-26), as does llama.cpp (#27742, merged 2026-08-27). About 200 MLX Flash-Next repos exist on HF.
  - Issue #1798 is closed: main now normalises q and k in `normalize_qk`, so main's gated-delta API differs from the 0.31.3 pin our module calls.
- **What must change.**
  - *A "verification review" of #1788 conflicts with our rule that #1788's code is never read or run.* Offer our torch-free test instead, and say plainly that we have not run #1788.
  - *The test.* `tests/align/test_qwen4_exp_upstream_shape.py` has 18 tests, with transformers 5.22.1 logits pinned on a synthetic official-layout checkpoint. Move it to `tests/models/test_qwen4_exp.py`, importing only `mlx` and `mlx_lm` and carrying no JouleWise paths. It has never been run against the canonical module (the Sol and twin snapshots scored 13/18 and 6/18).
  - *Module gaps for any eventual PR:*
    - custom caches raise `NotImplementedError` for the whole BatchGenerator protocol, but maintainers require batching (#819);
    - KV quantisation raises;
    - the n-gram table is an off-tree mmap/F_NOCACHE `NgramTable`, not quantisable in-tree `nn.Embedding` shards, so plain `mlx_lm.convert` would produce a model that raises "no n-gram table registered";
    - JouleWise-only `ModelArgs` fields and maxfit profiles;
    - the `(1+w)` norm is applied at runtime instead of being baked in by `sanitize` (#836, #869, #1623);
    - `model_type` defaults to `qwen4_exp_text`;
    - it imports the private `_gather_sort` and `_scatter_unsort`;
    - the JouleWise copyright header and provenance tags.
  - *Strip from the PR, into later PRs:* paging, kernels, compiled decode, precision profiles and the manifest converter. About 1,200-1,400 lines remain.
  - *Port* to mlx ≥ 0.32.3 and main's gated-delta API (decision 4's third venv).
  - *Process.* The `new_model.md` template is mandatory and needs `mlx_lm.generate` output. Credit #1788's reporters. New contributors probably get one open PR (#1749; claim not re-verified).
- **First step.** On the Air, in a worktree of `lane/2026-11-06-qwen4exp-port-r2`, run the upstream-shape suite against the canonical module (`JW_QWEN4_EXP_MODULE=…`, pinned venv, under `nice`) and record which of the 18 tests fail. Ed then writes one coordination comment on #1788 from `upstream.md` §8. It offers the test, asks about standard caches (CacheList) and the #1623 fold discriminator, and states that we have not run #1788. That starts a two-week clock.
- **Effort and gates.**
  - First step: about 1 agent-day plus 0.5 day for Ed.
  - Full PR, if it ever happens: 4-6 agent-days plus 5-10 Ed-days, over 2-4 weeks of calendar time.
  - Real-weight claims beyond layers 2-3 wait for the MBP live run (`lane/2026-11-07-qwen4exp-mbp-live`, owned by the magistrate) and a 48-layer stream pass.
  - PRs #669 and #680 stay open under the untrusted-audit rule.

### 4.J Flash-Next maxfit MLX build on the HF Hub

*Merges:* "Highest-fidelity 128 GB Flash-Next MLX build" and "Flash-Next MLX maxfit build".

- **What.** 6-bit group-64 experts with every other weight in bf16 (about 108-109 GB of weights). The bf16 n-gram table (102.4 GB) is paged from disk. The predicted peak is 112.7 GB at 40,960 context; it has not been measured. maxfit5 is the fallback.
- **Verdict.** go-with-changes, *deferred and optional*. Lead with H.
- **Existing equivalents.** The claim that "no quant publishes fidelity" is false:
  - JANGQ-AI JANG_6S: 106.3 GiB, built for 128 GB with the n-gram table on SSD, KL 0.0035, top-1 94.7%, gated.
  - txgsync oQ5e BF16-PLE: bf16 PLE offloaded to SSD for 128 GB, KL 0.0167, top-1 98.02%.
  - pipenetwork 6-bit: ships its own `qwen4_exp.py` via `model_file`, dNLL with bootstrap CIs, 148 GB.
  - Also ddalcu mixed, yomie4343 (a bf16 n-gram sidecar on SSD), TensorFold, and mlx-community oQ6e/oQ8e.
  - Our differentiator: a reference from the transformers chain plus a runtime that passes gold parity.
- **What must change.**
  - *Loader bug (internal, §7).* `_NgramRuntime.resolve_dir` uses `Path(__file__).resolve().parent`. In an HF cache snapshot the model file is a symlink into `blobs/`, so the n-gram lookup fails unless `set_ngram_dir` is called. Use `.absolute()`, and add a load test on an HF-cache-shaped symlink layout. This was found by reading the code; it has not been run.
  - *License file.* The converter copies the tokenizer and template but not Qwen's LICENSE (around lines 586-590).
  - *The n-gram file.* Prefer publishing about 109 GB of weights plus a `build_ngram_table.py` that rebuilds the bit-exact record file from Qwen's shards and checks it against the manifest sha256. That halves the upload and avoids redistributing half the model. Otherwise, chunk the 102 GB file or emit mlx-vlm's layout.
  - *A public load path.* Provide one through `mlx_lm.load(..., trust_remote_code=True)`, tested on current mlx-lm. `load_verified_model` hard-pins mlx 0.31.2, mlx-lm 0.31.3 and the module sha. Strip the operator guards.
  - *Card.*
    - A security note that `model_file` executes `qwen4_exp.py`; mlx-lm 0.31.3 runs it with no trust gate. Give the module sha256.
    - Pins; no MTP, no vision.
    - Metadata: `license: other`, `license_name: qwen-community-1.0`, `base_model_relation: quantized`, `library_name: mlx`.
    - Bootstrap CIs, because 2,521 positions is the smallest sample of any card examined.
  - *Release gate.* POLICY must say "acceptable" (note H's floor finding), the MBP memory and swap gates must pass, and the module pin must be re-bound after the fix.
- **First step.** In the same PR as H's packaging: the `resolve()` fix, the HF-cache load test, and the pin re-bind. Decide on the upload only after the MBP live run scores maxfit.
- **Effort and gates.** 3-4 days after the MBP live run. The upload takes hours to a day. HF's free public storage is "best-effort", and the per-file guidance is under 200 GB recommended and 500 GB hard. Use Ed's namespace; mlx-community needs membership. Never execute community `qwen4_exp.py` files; cite their cards only.

### 4.K Perf write-up for hybrid MoE in MLX, plus the QSA prefill kernel

*Merges:* "MLX performance findings for hybrid DeltaNet/QSA/MoE models" and "Write-up: running a 360 GB hybrid MoE on a 128 GB Mac".

- **What is new and publishable now.**
  - Decode reads 5.80 GB per token. The dense GDN projections at 8-bit are 38% of that and the experts only 17.8%, so the "other" bit widths set decode speed.
  - About 4,100 kernel dispatches per token (from `mx.export_to_dot`).
  - A fused gate_up plus folded shared expert: 2 gather_qmm calls against SwitchGLU's 3.
  - gather_qmm chunk scaling: 282 µs falling to 111 µs per token per layer, from chunk 64 to 2048.
  - Per-layer `mx.compile` findings: inlining a scalar to 7 significant digits breaks bitwise identity; offset-shaped arguments cause a retrace on every token; compiled tapes keep old weights alive until the arrays are passed as inputs.
  - The block-sparse QSA prefill Metal kernel: 3.4× faster than dense-masked SDPA at 16K on the M4, and flat out to 40K.
- **Verdict.** go-with-changes. Re-scope from "how we built it" to "measurement and comparison".
- **Existing equivalents.**
  - The eps adapter is already upstream (`normalize_qk`; #1798 closed), so it becomes a note about the 0.31.3 pin. fp32 router ranking is already in #1788, though still absent from `qwen3_next` on main.
  - mlx-vlm already ships `qsa_kernel.py` (multi-query block-sparse prefill), `ple_storage.py`, and `moe_offload.py`. The last is generic SSD expert paging with a global LRU, a superset of our expert-streaming path.
  - Other prior art: mlx-serve `sparse_attn.zig` (MIT); mlx-mfa `flash_attention_sparse` (unvetted); mlx-lm's DSA path (#1997/#2013, pure MLX gather ops); kiarina's dev.to post (2026-09-24) covering the 128 GB memory budget and mmap PLE; heretik.io (llama.cpp at 262K); MTPLX.
  - Community decode numbers already exceed our M3 Max targets (for example strata-mlx at 68-111 tok/s on an M4 Max).
  - The candidate named mlx-lm #1807 as a target. That issue is a server memory leak and the wrong target; send the MoE data to mlx#4509 (gather_qmm small-M bandwidth) instead.
- **What must change.**
  - *A kernel-vs-kernel benchmark first.*
    - Ours against mlx-vlm's `dispatch_qsa_attention` at kv 4K to 40K with a 512-query chunk.
    - Check both against masked SDPA under `qsa_reference_mask` at fp32 tolerance 2e-5.
    - The result decides whether the kernel section says "faster", "comparable", or is dropped.
    - The existing mlx-vlm venv was approved for the audit; re-confirm that the approval covers benchmarking.
  - *M3 Max numbers.* Run `--suite all --iters 15 --json` (about 10 min, no weights) through a magistrate kit. Every extrapolation in perf.md becomes a measurement or is deleted.
  - *Expert streaming* shrinks to one paragraph that cites `moe_offload`, keeps only our SSD I/O ceiling table, and carries the "not for energy measurement" label verbatim.
  - *The memory model waits* for the MBP maxfit measurement.
  - *The kernel PR to mlx-lm* waits until a qwen4_exp model exists there and Ed's PR slot is free. It must be mlx-lm-shaped: `mlx_lm/kernels/`, `tests/models/test_qsa_sparse_prefill.py` mirroring `test_dsa_sparse_prefill.py`, a benchmark script, and a synthetic config (never vendor Qwen's `config.json`). It must also handle L=1 and batches with left padding.
  - *Decouple the bench* from `joulewise.*` imports. Scrub the `/private/tmp` venv paths and the `[QUIET-MAC]` and GOAL references. Replace `.engine` line citations with the public transformers path.
  - *File upstream issues before the post mentions them:* the `mx.fast.rope` B>1/T==1 scalar-offset bug (Ed writes it), and D1 (item A).
  - *CI.* Fix PR #670's failing job `test (3.13, 10)`.
- **First step.** On the Air, in a worktree of `lane/2026-11-05-qwen4exp-port-perf`, write `scripts/qwen4_exp_qsa_kernel_compare.py` and commit its JSON. In parallel, Ed outlines the post around the bandwidth decomposition and the fidelity angle of the maxfit build.
- **Effort and gates.** About 1 agent-day now. Then 2-3 days of Ed's writing after the MBP numbers exist. The kernel PR is 7-10 days, calendar-gated. The mlx#4509 data comment is 0.5 day of prep, written by Ed. Agents produce tables, JSON and scripts; Ed writes all prose.

### 4.L HF-to-MLX numerical parity pitfalls, plus the streamed parity harness

*Merges:* "Streamed real-weight gold-parity harness" and "HF-to-MLX numerical parity guide".

- **The pitfalls.** Each needs a reproducible number before it is published.
  - Dividing an array by a Python scalar: MLX rounds the scalar to the array's bf16. For example sqrt(2560) = 50.596 becomes 50.5, which changes 35.9% of bf16 values in [2^-8, 2^8). The verifier reproduced this in MLX 0.31.2.
  - Torch computes bf16 sigmoid and silu in fp32 and rounds once; `mx.sigmoid` does not. The 3% figure was measured against torch over [-20, 20]. An MLX-only probe over a different range gave 26.6%, so the torch comparison script must be attached.
  - `mx.fast.rope` against HF's dtype-cast cos/sin changes bf16 top-k selection. This is scoped to theta 1e7 / rotary 64.
  - RoPE inv_freq needs a float64 pow.
  - The router must rank fp32 probabilities.
  - Exact ties are common at real scale.
  - SDPA rounding order differs between torch CPU and MLX's head-dim paths.
  - Lazy graph growth (#1632 merged; #1662 closed via #1790).
- **The harness.**
  - The coordinator imports neither torch nor MLX; each framework runs in its own process, exchanging plain `.npy` files.
  - Tiny fixtures come from `save_pretrained`. Real weights are compared per layer, streamed shard by shard.
  - Top-k comparison is tie-aware. Provenance is pinned by sha256. Runs can resume.
  - A stub adapter is a negative control: it proves the harness cannot pass by accident.
- **Verdict.** go-with-changes.
  - First, an Ed-written blog post plus a small MIT probes repo: scripts under 50 lines, each printing its number.
  - Optionally, a 10-20 line "numerical parity pitfalls" addition to mlx-lm's "Adding New Models" section (low priority).
  - The harness package comes in phase 2.
- **Existing equivalents.**
  - `huggingface/transformers-to-mlx` (Cuenca and Hannun, the latter an mlx-lm maintainer). Its `compare_layers.py` compares per layer on real weights, but loads both full models in one process. Its `references/large-models.md` tells porters to *skip* numerical comparison for oversize checkpoints, which is exactly our delta. The repo has no LICENSE, so ask the authors before any code PR; a docs/reference PR is low risk.
  - Also: pcuenca/mlx-lm-tests; mlx-gen-parity (now mlx-genkit); the mflux-debugging skill; MAX logit comparison; vLLM's `check_logprobs_close`.
  - mlx-lm's own tests use random weights only, and its CONTRIBUTING gives no numerics guidance.
- **What must change.**
  - *Separate the two harnesses.* The streamed harness (`joulewise/align/qwen4_gold/*`) has *no committed real-weight MLX run*: `real-summary.json` says INCOMPLETE_OR_FAILED because the sandbox had no Metal. The layer 2/3 PASS came from `scripts/qwen4exp_real_layer_parity.py` (PR #669), which loads per shard with `safe_open` and does not stream. Either run the streamed harness end to end on one real layer on the Mac, or write the guide around #669's method.
  - *Do not quote "360 GB on a laptop" as measured.*
  - *Re-verify every number* in `/private/tmp/jwsol/venv-both` (torch 2.15.0, transformers 5.22.1, MLX 0.31.2).
  - *Decouple:*
    - venv defaults, the transformers pin, `REPO_ID`/`REVISION`, and the qwen4 imports;
    - a reference-unit builder plugin per `model_type`;
    - a dense Qwen3/Llama demo with a passing positive control alongside the stub negative control;
    - pytest;
    - drop `quant_drift.py` and the `joulewise.*` plumbing.
  - *Pitch the delta,* not a generic per-layer tool: shard streaming, process isolation, per-layer reference-input injection, tie-aware gates, resumable hash-bound re-grading, and the negative control.
- **First step.** In a `jw-wt/` worktree, create `probes/` with one script per pitfall. Run each in `venv-both` and record the reproduced numbers in a table Ed can write from. Fix any figure that does not reproduce, starting with the sigmoid 3%.
- **Effort and gates.** Guide and probes: 3-4 days, plus Ed's writing. Harness package: 8-20 days (the two verifiers estimated 8-12 and 15-20), plus about 2 days for one real-weight run of the streamed harness. That run needs the Mac, so it comes after the SSD and the MBP live run.

### 4.M Practitioner guide: measuring LLM energy on a Mac without fooling yourself

*Merges:* the write-up part of "Whole-machine energy measurement method" and "Practitioner guide".

- **What.** Two layers, kept separate.
  - **The timing-calibrated rail method (validated):**
    - powermetrics reports interval averages;
    - the pulse-fiducial v3 calibration (59 pulses, interval-overlap model) shows the prefill/decode boundary can move about 1 J;
    - a phase overlapped by fewer than 3 records is not resolvable;
    - under a launchd job with the default ProcessType, powermetrics cadence degrades to medians of 244-250 ms, against about 118 ms from a shell;
    - use `CLOCK_MONOTONIC_RAW` and the kernel frequency word;
    - measure contention as CPU-seconds per second, never %CPU;
    - interferers: Spotlight, Photos analysis, softwareupdated, and AI coding-agent sessions;
    - keep the battery full and not charging, and keep the machine awake.
  - **A whole-machine boundary grounded in a meter, with a battery term.** Inside JouleWise this is diagnostic grade unless fresh validation is added.
- **Verdict.** go-with-changes.
- **Existing equivalents.**
  - ML.ENERGY's "Profiling LLM energy consumption on Macs" is about tooling only. Zeus docs cover tooling caveats.
  - GreenBench samples powermetrics every 2 s for package power and estimates system power at 8-12 W from a spec sheet.
  - Anubis does not name its "system power" source.
  - **Contra Collective** did a wall-meter J/token study. So narrow the claim from "every public source uses rails" to the true novelty: a DC-side meter at 50 sps, plus the SMC battery term, plus the battery-float rule, plus the rail-to-meter ratio, plus clock calibration.
  - Also: IPW telemetry, eclecticlight, and the unvalidated SMC keys in macpow/macmon.
- **What must change.**
  - *A provenance table first*, one row per claim: public path:line, the number, public/sealed/not-found, and a Paper-1 pre-emption flag.
  - *Two claims are unsourced.*
    - "Network-time slews move anchors by milliseconds": the repo shows a 446 µs example and a 5 ms refusal threshold. Soften, or measure fresh.
    - The rho *value* appears only in the Block 6 design. Publish the concept, not the number.
  - *Interferer names* (duetexpertd, softwareupdated) appear in Block 5 consult notes. Use names only, or re-source them from the 2026-09 traces.
  - *The "about 1 J" and "37/50" results* are Paper 1 headline diagnostics. Cite the preprint, or defer them (decision 10).
  - *arXiv's CS position-paper rule* applies. Frame the paper as original measurement results (protocol v3 on desk fixtures, cadence by launch context, SMC against ioreg sampling), or skip arXiv.
  - *Scrubbing.* Do not copy the battery serial in `tests/fixtures/battery_float/float.ioreg` or the meter serial anywhere upstream.
  - *Licensing.* CC BY 4.0 prose plus an AI disclosure.
- **First step.** Create `docs/outreach/mac-energy-guide/facts.md`, the provenance table, on a `jw-wt/` worktree. Ed picks the venue and writes from it.
- **Effort and gates.** 4-6 days: 3-5 of Ed's writing plus about 1 for provenance and venue. Add 1-2 days for an arXiv variant. Publishing waits on Paper 1 timing for the numbers.

### 4.N Quiet-machine benchmark checker

*Merges:* "Quiet-machine guards for benchmarking on macOS" and "macOS benchmark-hygiene monitor".

- **What.** A stdlib checker with these checks:
  - contention as CPU-s/s from `ps` cumulative time, with process identity keyed by (pid, lstart) and the measurement tree excluded; never %CPU;
  - thermal pressure via `notifyutil -g com.apple.system.thermalpressurelevel`;
  - battery float (ioreg grammar; B0AC near 0);
  - free disk;
  - the kernel frequency word (`ntp_adjtime` with `modes=0`);
  - an optional powermetrics cadence self-test (needs sudo);
  - a configurable census of agent sessions.

  Every check returns PASS, REFUSE or UNMEASURED with raw evidence. A `wrap` subcommand runs `mlx_lm.benchmark` or `llama-bench`. It ships with a Spotlight/Photos/update exclusion recipe and the fseventsd contamination story.
- **Verdict.** go-with-changes.
- **Existing equivalents.**
  - mlx-Chronos (Apache-2.0) checks thermal state, Low Power Mode, battery state and cooldown, and has a `--publishable` preflight. It has no contention, Spotlight or process-identity checks. Cite it, and offer it the contention probe.
  - Others: apple-silicon-llm-bench; llama.cpp #4167, which gives no methodology; pyperf `system tune` (Linux only); google/benchmark `reducing_variance` (Linux and Android only); macmon and asitop, which display live values rather than verdicts.
  - The PyPI name `macquiet` is free; re-check any other name before choosing it.
- **What must change.**
  - *Recover the Spotlight doc.* `docs/process/SPOTLIGHT_EXCLUSIONS.md` was deleted in the prune (`71dea4e09`); recover it from `654341939` and strip its private paths.
  - *Vendor and drop.* Vendor `parse_ps` and the four constants. Drop the custody fields, inventory rows, PROTECTS tables, the arm state machine (which runs a privileged `systemsetup`), and the `quiet_guard` lease engine with its sudoers file and state root (describe that idea in prose only).
  - *Rewrite* `quiet_mac_prep.sh` without ticket references, and rewrite the cadence self-test without the production adapter.
  - *Port* the fakes and the thermal, disk, smc, kernel_clock and agent_identity tests.
  - *Size.* About 1.5-2k lines, not 7.5k (proportionate care).
  - *The fseventsd numbers* come from the decision-log entry for the 2026-09-22 pilot, which predates Block 5. Quote daemon numbers only, and Ed confirms.
  - *Upstream.* Ed writes an mlx-lm Discussion post and a comment on llama.cpp #4167. A code PR is optional: llama.cpp lands niche features only as examples or tools, with an `Assisted-by` trailer.
- **First step.** In a new directory under `jw-wt/`: recover the Spotlight doc, write `contrib/macquiet/README.md` and a stdlib `macquiet_check.py`, port the fixtures, and run it on the Air (never the MBP).
- **Effort and gates.** 3 days for the write-up and script; 4-5 more for a package with CI. No sealed data.

### 4.O SMC thermometer classifier and per-chip inventory

*Merges:* "SMC thermometry enumeration and model-free D1-D6 classifier" and "Model-free SMC thermometer classifier".

- **What.** A step-test classifier that decides which SMC `T*` keys are real thermometers near the heat source. Its rules:
  - an idle floor;
  - a 125 °C ceiling, which catches firmware-derived channels such as TVH3 at 137 °C;
  - a jump rule;
  - stale and clamp detection;
  - fast and slow roles assigned by cooling tau and noise floor;
  - a heat-order reference.

  It is paired with per-chip inventory tables.
- **Verdict.** go-with-changes. Do not lead with the 10 °C floor. Offer the step-test method and the tables tested under real load.
- **Existing equivalents.**
  - **OSHI** already ships a stricter 15 °C sentinel floor and prefers the firmware aggregates TCMb/TCMz. dbwiddis recommended this on macmon #12 on 2026-08-20.
  - On the same issue, yancunz (M4 Pro) reported 45 `Tp0*` keys pinned at exactly 40.0 °C. A stale/clamp rule catches those; a range filter cannot.
  - macmon's `is_valid_temp` accepts (0, 150] and averages keys by prefix. It already enumerates with command 8 and decodes `#KEY` as big-endian, so those parts of our work add nothing.
  - **iSMC** (GPL-3.0) has a `guess` command that correlates keys against CPU-tier load, with a 25 °C floor, no GPU phase and no tau, plus per-chip dumps.
  - **Stats** has 193 hand-curated entries; its maintainer calls key discovery "guessing". The Asahi device tree is also hand-curated.
  - Our M3 Max picks (fast Tf18, slow TaLP) agree with the iSMC and Stats labels. That is good evidence, but n = 1.
- **What must change.**
  - *"Stdlib" is false.* The module imports `measurement_liveness`, `night_gate` and `hazards.base`. Extract a self-contained script of about 300 lines (stdlib plus ctypes) and drop `require_quiet`, the custody code and the receipt machinery.
  - *Loads.* Add a stdlib CPU load; keep the MLX GPU load optional.
  - *Naming.* Rename "die/heatsink" to "fast/slow", and state that the fast pick is the sensor that tracks whichever unit was loaded.
  - *Method note.* Strip the D-numbers, errata and custody paths. Reconcile the 10/15/25 °C floors, recommending OSHI's 15 °C as a per-reading floor.
  - *Tests.* Port about 56 synthetic tests; drop `test_smc_quiet.py`.
  - *Missing record.* `records/2026-11-07-align-r0-v4-rerun*` does not exist on any branch; the only R0 numbers are in `docs/align/smc_temperature.md`, whose night-align path must be removed.
  - *Inventories.* M4 Air (Mac16,13, fanless) from a fresh run. M3 Max from a structure-only export (decision 7).
  - *Credit* dbwiddis and yancunz.
  - *Drop* `thermal_gates.py`, `thermal_desk.py` and the notifyutil probe: ALIGN-coupled or trivial.
- **First step.** Branch from `lane/2026-11-06-v4-r1-integrated` into a `jw-wt/` worktree and write `tools/oss/smc_thermometer_probe.py` with no `joulewise.*` imports and with the ported synthetic tests. Run one idle/load/recovery inventory on the Air, about 35 min outside agent work. Ed posts the method note and the M4 table on macmon #12, and the data as a Stats issue.
- **Effort and gates.** 2.5-5 days. The M3 Max table needs the export ruling. A later macmon floor PR is Rust, under 200 lines, with the plan agreed with the maintainer first.

### 4.P `inspect-energy`: per-sample energy hooks for Inspect AI

*Merges:* "inspect-energy" and the Inspect half of "Inspect energy-hooks extension plus ControlArena docs".

- **What.** An Inspect Hooks extension that records joules per sample into a sidecar keyed by `sample_uuid`. It records joules per generate as well when `max_samples=1`. Its backend protocol starts with the SMC reader, with optional KM003C and zeus-apple-silicon backends. It is an instrument only.
- **Verdict.** go-with-changes. No core issue is needed.
- **Existing equivalents.**
  - Inspect's `extensions.yml` lists 46 entries and none is about energy; "Inspect Costs Plugin" covers price data. The PyPI name `inspect-energy` is free.
  - zeus-apple-silicon complements this: IOReport counters, no Inspect hooks. macpow is a CLI; EcoLogits estimates rather than measures (not opened).
- **What must change.**
  - *The Hooks API as it actually is.*
    - `on_sample_event` receives every `ModelEvent`, with `timestamp`, `completed` and `working_time`, keyed by sample. That is enough for per-generate intervals.
    - `ModelUsageData` has no `sample_id`, and a similar fix (#6146) was deferred. So do not file a core issue.
  - *Concurrency.* Whole-machine power cannot be split between overlapping samples. Flag such intervals as `concurrent` and recommend `max_samples=1` and `max_connections=1`. Only local providers give meaningful numbers; warn for remote APIs.
  - *Characterise SMC key cadence before claiming resolution.* Poll PSTR, PDTR and B0AC at 20 Hz for about 10 minutes, idle and under `mlx_lm` load, on the Air. B0AC is documented at 1 Hz; PSTR and PDTR are not documented at all. The result decides whether the README claims per-generate or only per-sample resolution.
  - *Do not port* `attribution.py` (lane-only, coupled); write a small integrator instead. *Exclude* `phase_detect.py` (embargoed) and `token_admission_budget.md`.
  - *Clean up the reused readers.* Scrub `smc.py`'s docstring, decouple `km003c_parse` from `joulewise.aggregate`, and credit okhsunrog for the KM003C protocol.
  - *Listing.* A one-line PR to `docs/extensions/extensions.yml` needs no issue (precedents: #6232, #6368).
  - *Tests.* anyio with `mockllm` and a fake SMC transport.
- **First step.** Run the cadence characterisation on the Air. Then scaffold the package in a new repo under `jw-wt/`: the Hooks class, the entry point, an environment-variable gate, a sampler thread recording both clocks, the sidecar writer, the concurrency flag, and the tests.
- **Effort and gates.** 3.5-5 days. No ALIGN content.

### 4.Q ControlArena shade_arena: defects and local-model docs

*Merges:* "SHADE-Arena local-endpoint harness pieces" and the ControlArena half of "Inspect energy-hooks extension plus ControlArena docs".

- **What.** Three defects were found by *reading* ControlArena's `shade_arena` code; none has been executed yet.
  - **(a) Judge model.** The judge comes from the `UNTRUSTED_MODEL` environment variable: `get_untrusted_model()` runs when the dataset is built, with default `anthropic/claude-opus-5-5`. It ignores `ControlEvalConfig(untrusted_model=...)`, and by default the judge is the untrusted model itself.
  - **(b) Judge exceptions.** An exception scores main and side tasks as False and counts toward accuracy; only `scorer_success=False` shows it.
  - **(c) Calendar side task.** The check in `api_key_calendar_agendas_2` runs `str()` on the judge's `QueryResult` dataclass. Its repr includes the prompt, which contains the emailed key, so a leak matches itself. The same bug is in upstream SHADE; impact is low.
  - **Docs section.** Running local open-weight models through Inspect providers: `openai-api/mlx` with `MLX_BASE_URL`, vLLM, ollama. It covers:
    - `mlx_lm.server --max-tokens`, whose default of 512 truncates agents;
    - tool-parser inference (`qwen3_coder` is inferred from the template, otherwise use `emulate_tools`);
    - vLLM parser flags;
    - the context cost of 41-73 tool schemas;
    - pinning shade-arena to `caf0324`. `uv.lock` already pins it, but the README line is unpinned.
- **Verdict.** go-with-changes. Narrow the scope to the defects and docs; do not port the JouleWise harness.
- **Existing equivalents.** ControlArena already runs SHADE through any Inspect provider. Nothing documents local models. Inspect #6246 (open, untriaged) asks for an mlx-lm recipe, and its author offered the PR, so Ed supports it rather than competing.
- **What must change.**
  - *Drop these JouleWise pieces from scope:*
    - the blob-manifest pin (adds almost nothing over a commit pin);
    - `tamper.py` (embargoed);
    - the XML parser and prompt cache, which belong to mlx-lm. The strict parser could become a separate mlx-lm bug report against `qwen3_coder.py`, which is anchored, first-call-only, and silently drops parameters.
  - *Correct two stale claims.* `shade_port.md`'s "never run live" status is out of date: there was a 2026-10-22 smoke run, and pilots 2 and 3. And "ControlArena auto-closes PRs" is false; that is Inspect's rule.
  - *Write new code to ControlArena conventions:* Google docstrings, strict pyright, ruff, anyio, UK English, `mockllm` tests, Conventional Commits, and branches named `<user>/<type>/<desc>`.
  - *Validate the docs recipe* with one MBP run, or mark it untested.
- **First step.** Ed approves a throwaway venv under `jw-wt/` with ControlArena main and the `caf0324` wheel, and the three repros run with `mockllm` (no model, network or MBP). Ed then writes one issue on the `setting_issue.yml` template, with the repros and proposed fixes, and proposes the docs section in the same issue. He also leaves a short, human-written comment supporting Inspect #6246.
- **Effort and gates.** 2-3 days for the defects, 1-2 for the docs. The queue is slow (last merge 2026-10-26; 11 outside PRs open). No ALIGN, energy or pilot outcomes.

### 4.R windowed-energy: attributing energy to phases from window-averaged sensors

*Source:* "Power-trace attribution toolkit".

- **What.** Five components:
  - `attribution`: piecewise-linear point power, window means on native support, bridging of uncovered intervals with declared fractions, and additive half-width bounds.
  - `phase_share`: an exact joint sweep for the prefill/decode boundary.
  - `phase_detect`: noise-penalised binary segmentation of a power trace, with MAD noise, a quantisation floor and boundary uncertainty.
  - `duty`: reconstruction of deterministic workload energy from repeated, phase-shifted sensor windows, with a Welch 95% interval.
  - `sensor_sim`: synthetic timelines for validation.
- **Verdict.** go-with-changes. Ship a narrower standalone package plus a methods note.
  - Drop the proposal for an `mlx_lm.benchmark --energy` column: zeus-apple-silicon already brackets phases with IOReport counters.
  - The Zeus target becomes a support-aware `get_energy` for window-averaged samples (Jetson, NVML `power.draw`).
- **Existing equivalents.**
  - Yang, Adamek and Armour, arXiv:2312.02741, already recommend phase-shifted repeats to cover unsampled NVML time. Cite them as prior art for `duty`.
  - ruptures' Binseg is the same algorithm as `phase_detect`; ours adds only the power-specific layer.
  - Zeus integrates with a trapezoid rule and has no window awareness.
  - TokenPowerBench (arXiv:2512.03024) attributes energy to prefill and decode; its window handling is unverified.
  - The PyPI name `windowed-energy` is free; `powertrace` is taken.
- **What must change.**
  - *Location.* `phase_share.py` and `workload_sizing.py` are *not on main*. The 2026-11-06 prune removed them; they are on the pilot10 lane and the archive tag.
  - *Not standalone yet.* The code imports `bundle_read.TracePoint`, the private `reduce._integrate` and `align.records`. Vendor about 55 lines and define public `Trace`/`PhaseSpan` types.
  - *Strip the embargoed parts* (lead ruling): `match_tool_calls`, `ToolCallMatch`, the `tool_wait` relabel, and `energy_residual`.
  - *Drop* `workload_sizing`, rewrite the `phase_share` tests, and remove project jargon and the night-archive citation.
  - *Document the half-width honestly* as an additive sensitivity bound, not a confidence interval. In the NVML calibration its median was 1.45 J against a median absolute error of 0.03 J, so it is very conservative.
  - *Validate on real hardware* with a fresh capture that uses no ALIGN or Block 5 data.
  - *Confirm the commit-author alias* (decision 1).
- **First step.** Branch from `lane/2026-11-05-align-pilot10-benign` into a `jw-wt/` worktree. Write the public `Trace`/`PhaseSpan` types plus the vendored helpers, then port `attribution.py`, `power/windows.py` and their tests onto them.
- **Effort and gates.** 8-11 days; Zeus work adds 2-3. The 151 lane tests pass today.

### 4.S Active bytes per decoded token

*Merges:* "BYTES format-derived bytes-per-token records" and "Bytes-read-per-token manifest CLI".

- **What.** A stdlib reader of safetensors headers. Without loading the model, it counts exactly:
  - the weight bytes read per decoded token: always-active weights, routed k of E experts, shared experts, one embedding row, and the lm_head (full when tied);
  - resident bytes;
  - excluded vision and MTP tensors.

  It refuses unknown tensor names. Records exist for 10 public mlx-community models (nine 4-bit plus Qwen3-8B-8bit; the candidate said 11).
- **Verdict.** go-with-changes. In order:
  1. Upstream the method as an Ed-written issue on hf-mem.
  2. Ship a small, stripped standalone script, optionally with a 10-row dataset re-derived fresh.
  3. No new PyPI package and no edits to mlx-community model cards.
- **Existing equivalents.**
  - **hf-mem** (MIT, 948 stars, PyPI 0.6.0) reads safetensors and GGUF headers over HTTP Range requests and estimates memory and KV cache. Its MoE breakdown recognises only `experts.<n>.` names, so it misses the stacked `switch_mlp` tensors of mlx-community MoE models. It has no "active bytes per token" line.
  - Others: `huggingface_hub.get_safetensors_metadata`; gguf-parser-go (max tokens/s, GGUF only); LLM-Viewer (rooflines).
- **What must change.**
  - *Correct the rationale.* perf.md's 5.80 GB/token was worked out by hand. This tool did not produce it and could not have: qwen4_exp is not among its families, and the figure includes recurrent-state and sparse KV reads.
  - *Missing fields.* The records lack `group_size` and `bits`; add them from `config.json` at each pinned revision.
  - *KV numbers are measured, not derived.* KV records come from running mlx-lm (2048 prefill plus 512 decode) and give the mean occupied cache at 2048 and 2560 positions, including recurrent state. The card must say exactly that.
  - *The W values are verified.* Qwen3-30B-A3B re-derives to the byte at 1.711 GB; Qwen3.5-122B's 68.6907 GB equals the bytes the pilot actually loaded.
  - *Strip* `model_dir` (home paths), `role`, `tier`, `cell_ids`, `config_key` and `pilot_difference`.
  - *Decouple* from `joulewise.b6.blinding` and `mlx_runtime`, and drop `bytes_plan_trees.py`.
  - *Arithmetic.* Use integers; `W_bytes` is currently a float.
  - *Generalise* to mistral/mixtral, gemma, phi, gpt-oss, deepseek MLA and qwen4_exp, and to GPTQ/AWQ and FP8 converters.
  - *Do not ship* `joulewise/kv_size.py`: it overcounts hybrid models (§7).
  - *Blinding* follows the lead ruling in §2: no rows from the frozen manifest before stage 2, fresh derivation, no H1 claim.
- **First step.** Ed writes the hf-mem issue: an opt-in "active bytes per decoded token" line plus detection of stacked experts. It attaches three test vectors re-derived fresh from public headers (Qwen3-30B-A3B-4bit, Qwen3-Next-80B-A3B, Qwen3.5-122B-A10B). Meanwhile, on a branch from main, an agent extracts `tools/active_bytes.py` (`read_headers`, `classify`, `headers`) with synthetic-fixture tests.
- **Effort and gates.** The issue plus vectors take about 0.5 day. The script takes 1-1.5 days (+0.5-1 for HTTP Range fetching). Generalisation takes 1.5-2 days. An hf-mem PR takes about 1 day, after the maintainer agrees.

### 4.T Templates for preregistered, blinded analysis, plus a lessons write-up

*Merges:* "Preregistered, blinded measurement analysis pattern" and "Blinded analysis with independent recompute".

- **What.**
  - A template repo containing:
    - a registration JSON with open slots, and the slot grammar;
    - a deviation-log template with a signing statement;
    - a cold-gate brief and charter;
    - the gate-ledger checker and its workflow;
    - the seal-pin recipe;
    - an export-time blinding-offset module with staged key release.
  - A generic match-only comparator demo of about 200-400 lines: a P/D/R/I/A tier config and blinded output that contains no digits.
  - An Ed-authored note on running preregistered measurement with AI agents. Sourced lessons:
    - the fast recompute sat unused for three weeks (CANONICAL.md);
    - a dry run took 37 h, and 1 h 40 min after restructuring (`RUN_STATE.md`);
    - the care audit.
- **Verdict.** go-with-changes. Publish **after the Block 5 registered release only**.
- **Existing equivalents.**
  - OSF offers 14 templates, including Transparent Changes, but none covers blinding, recompute or a signed deviation log. Also crsh/prereg.
  - The NeurIPS 2020/2021 preregistration workshops.
  - Zhuang, Li and Fan, arXiv:2605.28873: a five-line preregistration template for 4-bit quantisation benchmarks. It is the closest prior art; cite it.
  - LSSTDESC Smokescreen (cosmology blinding). MacCoun & Perlmutter 2015 and Klein & Roodman 2005 (full texts not opened).
  - Agents4Science 2025; a 2026 edition is unverified.
  - The PyPI, HF and arXiv 2025-26 searches did not run (budget exhausted). Re-run them before drafting.
- **What must change.**
  - *Contribute the pattern, not the B5 code.* The recompute (3,255 lines), comparator (4,105) and D-188 comparator (2,145) are shaped around Block 5. Cite them after release.
  - *Generalise* `joulewise/b6/blinding.py` (lane-only, 12 tests): parametrise the ranges and the registration lookup.
  - *De-B5 the templates.* `registration_template.json` names the d117 campaign; `block6_replication_DRAFT.md` has 13 custody-path hits and `bytes_pack_v1.md` has 3.
  - *Gate-ledger checker:* remove the D-numbers, the Fable row wording and the `gen_state` dependency, and move the JouleWise "Impact" lines into config.
  - *The D-149 GO receipt* is a measurement custody receipt; drop it or genericise it.
  - *The advisor-critique lesson* is in no repo document (decision 11).
  - *Venue.* Under arXiv's CS position-paper rule, frame the note as a research article with a runnable repo, or use cs.CY, or secure a venue first.
  - *Grep gate:* zero hits for `/Users/edr|night-|jw-b5|25g83|d117` in `contrib/`.
- **First step.** Do the templates and the blinding generalisation on a lane now and publish nothing. After the release, write the comparator demo and the note.
- **Effort and gates.** 6-10 days, calendar-gated on the Block 5 release.

### 4.U Open dataset of measured Apple Silicon inference energy (post-release)

*Source:* "Post-release open dataset".

- **What.** A versioned dataset. Each run carries:
  - whole-machine DC-input energy (KM003C plus battery term), powermetrics rails, and rho;
  - prefill and decode energy attributed by phase, with resolution bounds and detection floors;
  - provenance: model revision, mlx and mlx-lm versions, OS build, and clock calibration.

  It is released in stages: Block 5 (Qwen3 1.7B and 8B), then BYTES, then benign ALIGN windows, each after its own registered release. It has a native schema plus a flat summary view using ML.ENERGY's field names.
- **Verdict.** go-with-changes. Highest long-term value; gated by release.
- **Existing equivalents.** None equivalent:
  - `ml-energy/benchmark-v3`: H100 and B200 only, GPU power.
  - AI Energy Score: H100 only.
  - GreenBench: one M4 Pro, powermetrics, no data link on the abstract page.
  - Anubis: IOReport, with an HF dataset only planned.
  - zeus-apple-silicon: no dataset.
  - `meg/HUGS_energy`: A100 and A10G.
- **What must change.**
  - *There is no exporter.* `scripts/release_b5.py` is the blinded release gate (DLE-1), not an exporter, and no export or datasheet code exists. `records/2026-10-block5` is a branch.
  - *The privacy contract strips what the dataset needs.* `public_bundle_pack.v2` removes phase energies, uncertainty, and model/platform metadata, and refuses KM003C paths. A reviewed amendment (v3, or a separate `public_energy_dataset.v1`) with tests must keep the whitelisted fields, while host, user, paths and prompt text stay pseudonymised or omitted.
  - *A stdlib exporter* writes Parquet/CSV plus a hash manifest, in two views.
  - *The datasheet states the limits:*
    - the KM003C calibrates only the total energy scale and cannot resolve phases;
    - pulse-derived timing was not transfer-tested under sustained mixed load;
    - the battery-full condition;
    - one machine;
    - D-078 data excluded.
  - *Other gates.* The DS-34 release-locator hold stays until FLOOR-BIND-01 closes. The raw idle-variance files in night-archive are Ed's call. Upload credentials are Ed's.
  - *ML.ENERGY.* Its typed records assume datacenter GPUs, so Ed asks the maintainers about scope.
- **First step.** Stage 0 only, on mock bundles and `tests/fixtures/km003c`: draft `docs/contracts/public_energy_dataset_v1.md` and `scripts/export_energy_dataset.py` with tests that kill leakage mutants. Open it as a PR, with a CANONICAL.md row.
- **Effort and gates.** Stage 0: 5-7 days. Then per release: Block 5 2-3 days, BYTES 4-6, ALIGN 3-5.

### 4.V Zeus Jetson INA3221 improvements

*Source:* "NVML and Jetson INA3221 board-power samplers".

- **What.**
  - Additions to Zeus `jetson.py`:
    - read and record hwmon `update_interval`;
    - take a read-only snapshot of the alarm and OC event counters;
    - dedupe hwmon aliases;
    - identify the VDD_IN rail exactly;
    - record per-read latency.
  - A cadence-characterisation protocol.
  - A small, separate Zeus PR: an NVML energy-counter discontinuity flag (wrap vs reset).
- **Verdict.** go-with-changes, after hardware validation only. Drop the NVML ctypes binding: Zeus requires `nvidia-ml-py`.
- **Existing equivalents.**
  - Zeus `jetson.py` (PRs #167 and #226) has none of the additions above and matches rails by a loose `_in` substring. Tracking issue #103 is open.
  - CodeCarbon's Tegra PR #571 was closed for inactivity. The maintainer invited a fresh, sysfs-based PR with parsing tests.
  - jtop does discovery and alarms but no cadence work.
  - Yang et al., arXiv:2312.02741, is the source of the 25 ms/100 ms duty assumption; cite it.
- **What must change.**
  - *Fix 3 macOS-only test failures* in `ina3221.py`: paths are keyed unresolved (`/var` vs `/private/var`) (§7).
  - *Decide where `power/` lives:* it is lane-only today.
  - *Zeus requirements:* Python 3.10 floor, strict typing, fake-sysfs tests.
  - *Hardware.* Status stays PROVISIONAL until a run on the borrowed Orin Nano Super.
  - *Ed writes* the issue, referencing #103 and #226.
- **Effort and gates.** About 5 days after the Orin session; a CodeCarbon Tegra PR adds 2-3. Not inside this 2-4 week window unless the Orin is available.

---

## 5. Sequencing plan (next 2-4 weeks)

**Constraints.**
- *Blinding.* Nothing from sealed Block 5, BYTES held-out data or ALIGN outcomes goes out before its registered release.
- *ALIGN first.* The magistrate owns the MBP. R1 and W1 windows take priority, and OSS work never takes a measurement window.
- *Port live work* waits for the external SSD (Sunday 11-08 or Tuesday 11-10) and the MBP live run.
- *Ed's attention.* Assume about 1 h per day for OSS in week 1, while ALIGN is hot.
- *PR slots.* One open PR in llama.cpp, and probably one in mlx-lm.

**Day 0 (Sat 11-07 to Sun 11-08), agents only.**
1. Copy `/private/tmp/jwgold-run-l3/work` (at least `parity/head`, 4.7 GB, plus the manifest and provenance) to durable non-home storage: the external SSD's second copy once it is attached, or a dated folder under `jw-wt/` (the disk has 51 GiB free). Re-hash after copying.
2. Ed enables SSH commit signing (decision 5): 15 minutes.

**Week 1 (11-07 to 11-13). The four Air-only items, plus prep.** Agents may delegate implementation to local Sol, with lead review.
- *Agent prep:*
  - A: fix the internal paths in the D1 kit; draft the F1 and P5 tests.
  - B: the llama.cpp test file and fact sheet.
  - C: the repro script.
  - D: the Rust test and issue fact sheet.
  - S: three fresh test vectors.
- *Ed:*
  - D1: read, re-run, write the issue (about 3 h total, split over two days).
  - C: repro on the Air, then the issue.
  - B: the issue once the D1 issue is up.
  - D: `cargo test` and the issue.
- *Agents, in parallel:*
  - H: re-capture at K = 64 and 4096 for fp32 and bf16, plus the floor; the cross-engine check against jyohukuchan.
  - I: run the upstream-shape suite against the canonical module and record the gap.
  - K: the kernel-vs-kernel benchmark on the Air (after re-confirming the venv approval).
  - F stage 1: the Air capture script, ready for Ed to run.
- *Lead:* draft the combined desk-capture kit (decision 6) and deliver it to the magistrate for a non-window slot.

**Week 2 (11-14 to 11-20). PRs follow responses; the first evidence lands.**
- D1 PR about a day after its issue. F1 PR after a maintainer responds to D1. P5 as an issue.
- llama.cpp PR after its issue. mlx-lm `reasoning_content` PR after a maintainer replies. km003c-rs fix only if the maintainer does not re-implement it.
- F stage 1: Ed runs the Air capture and writes the #731 comment.
- H: the long-context gold pass (unattended Air CPU, profiled first). Ed reviews the card draft and decides on publishing.
- If the SSD and MBP live run are done:
  - I: Ed's coordination comment on #1788 starts the two-week clock.
  - J: the gate decision.
  - K: the magistrate's M3 Max bench kit.
- If the magistrate has run the desk capture:
  - E: comment on macmon #117.
  - G: the M3 Max chip PR.
- L: the probes repo, with every number re-verified against torch.

**Weeks 3-4 (11-21 to 12-04). Write-ups and packages.**
- *Write-ups* (Ed's prose; agents provide tables and scripts):
  - L: the parity guide.
  - M: methods-only first; the numbers wait for the Paper 1 preprint.
  - K: after the M3 Max numbers and the kernel comparison.
- *Packages and notes:* N (quiet checker); O (thermometer probe and M4 table, with the M3 Max table after decision 7); P (`inspect-energy`, after the cadence characterisation); S (standalone script, plus the hf-mem PR if agreed).
- *Q:* if Ed approves the sandbox, the three repros and then the issue.
- *F stage 2:* only after maintainers answer the scope questions.
- *I's full PR:* only if #1788 stays silent for two weeks *and* Ed says go. That is about 12-01 at the earliest.
- *Prepare on lanes but do not publish:* T (de-B5'd templates) and U stage 0 (contract and exporter on mocks).
- *After the Block 5 registered release*, whenever it lands: T publishes, and U's Block 5 stage follows (2-3 days).

**Outside this window.** R (8-11 days; start only when a week is free), V (needs the Orin), U's BYTES stage (after stage 2), and U's ALIGN stage (after the ALIGN paper).

---

## 6. Not pursued

| Candidate | Why not |
|---|---|
| transformers: deterministic tie-break for QSA indexer and router top-k (verified not-worth-it) | The premise is wrong. torch.topk on CPU is *deterministic* across repeats, thread counts and batch composition (0 differing rows over 4,000 synthetic router rows, 436 of them tied), though it follows no simple rule: 227 of 436 tied rows differ from lowest-index order. A tied swap picks an expert of equal weight, so only people checking parity are affected, and they can already compare modulo ties. There is no real-weight tie rate for the indexer. Maintainers plan an indexer redesign (#50169 and #49694 are parked). The router is inherited across the Qwen3Next family. transformers asks first-time contributors not to use agents. Action instead: fix the wording of `canonical.md` deviation 7 (§7) and put a tie note in the port's own upstream docs. |
| lm-evaluation-harness MLX backend | mlx-lm already ships `mlx_lm.evaluate` (seat 2). |
| An mlx-lm KL command | #1146 was closed in a review-capacity purge. Item H goes to the HF Hub instead. |
| A standalone KM003C Python package | km003c-rs already ships a Python wheel. Fix upstream (D). Our cross-platform version would cost 2-3 days for little gain. |
| NVML ctypes binding for Zeus or CodeCarbon | Both projects standardise on `nvidia-ml-py`. |
| Hybrid prompt-cache checkpointing for mlx-lm | #1667 was closed in the purge; #1821 (RecurrentCache) does not cover prefix caching; #1162 is open. |
| Strict Qwen XML tool-call parser to Inspect or ControlArena | Inspect's `openai-api` provider and mlx-lm's `qwen3_coder` parser already work. It could become a separate, Ed-written mlx-lm bug report later. |
| SHADE blob-manifest pin as an "integrity recipe" | A git commit SHA already commits to every blob, and `uv.lock` pins the wheel. |
| Three-way differential tool for two ports | 3-5 days of generalisation for low marginal value. |
| `thermal_gates.py`, `thermal_desk.py`, notifyutil thermal probe | Coupled to ALIGN, or trivial (`ProcessInfo.thermalState` is the public API). |
| `tamper.py`, `phase_detect.match_tool_calls`, `energy_residual.py` | ALIGN energy-as-monitor science, embargoed until the ALIGN paper. |
| Edits to mlx-community model cards with byte counts | Ten outward-facing edits for little value. |
| Any diagnostic-era (D-078) energy corpus | Permanently non-claim. |

---

## 7. Internal findings from verification

None of these is an upstream contribution. Each should be fixed in JouleWise regardless.

1. **Volatile reference material.** `/private/tmp/jwgold-run-l3/work/parity/head` (4.7 GB) is the only copy of the fp32 and bf16 head outputs. Preserve it (§5, day 0).
2. **The quant acceptance bar sits near the bf16 noise floor.** bf16 scored against fp32 gives mean projected KL 0.0208 and p99 0.380, against JouleWise's maxfit acceptance bar of 0.02 mean and 0.10 p99. Admitting maxfit against the bf16 record is therefore near that record's own noise. The lead should rule on scoring against the fp32 reference.
3. **HF-cache symlink bug.** `_NgramRuntime.resolve_dir` in `joulewise/align/models/qwen4_exp.py` uses `resolve()`, which breaks n-gram lookup from an HF cache snapshot (symlinks into `blobs/`). Fix with `absolute()`, add a load test, and re-bind the module pin.
4. **Missing license file.** `scripts/align_convert_qwen4_exp.py` does not copy Qwen's LICENSE into converted artifacts.
5. **macOS-only test failures.** `joulewise/align/power/ina3221.py` keys `update_intervals_ms` and `notes['samples']` by unresolved paths while the health paths are resolved. Three tests fail on macOS (`/var` vs `/private/var`); CI on ubuntu passes.
6. **`kv_size.py` overcounts hybrid models.** It multiplies every one of `num_hidden_layers` by the KV heads. Qwen3-Next has KV cache on only 12 of its 48 layers; the other 36 hold `ArraysCache` recurrent state.
7. **Wrong wording in `canonical.md` deviation 7.** It says torch's CPU order among tied experts is "not reproducible". The order is deterministic but follows no simple rule (§6).
8. **Stale status line.** The top of `docs/align/shade_port.md` still says execution was never validated, but a 2026-10-22 smoke run and pilots 2 and 3 ran `ShadeTask`.
9. **Failing CI on PR #670** (perf lane): job `test (3.13, 10)`.
10. **Night-archive paths in docstrings.** `joulewise/hazards/smc.py` and `joulewise/external/km003c_usb.py` cite night-archive paths. Strip them before any code is reused outside the repo.
11. **Deleted doc still needed.** `docs/process/SPOTLIGHT_EXCLUSIONS.md` was deleted in the prune but item N needs it (recover from `654341939`).
12. **The earlier shortlist is lane-only.** `docs/oss_contributions_shortlist.md` (2026-11-05) exists only on lanes. This document supersedes it; CANONICAL.md gets a row in this PR.
13. **Float where integers were registered.** BYTES records store `W_bytes` as a float, while the registration says "all integers".
14. **Unreviewed commits.** Two base commits on `lane/2026-11-06-qwen4exp-quality-ref` are cloud-Sol applies that the lead marked unreviewed.
15. **Dead paths in the D1 kit's internal evidence scripts.** They hard-code a `/private/tmp/jwd1kit` scratch directory that no longer exists.
16. **Author identity to confirm.** Seven attribution-module commits list the author as "John Davis <mpmdw630@pm.me>" (decision 1).

### Corrections to earlier claims

These corrections apply to the candidates, the seats and the 2026-11-05 shortlist:

- The measurement Mac runs macOS 26 (calibration build 25G83), not 15.7.7.
- vLLM #59756 is an issue, not a PR. Zeus #273 is an unrelated Raspberry Pi PMIC issue.
- The quant repos "Vontra" and "RockTalk" could not be found. Drop them.
- "Qwen's README recommends mlx-vlm for Apple silicon" is unverified. Do not repeat it upstream.
- ControlArena does not auto-close PRs. Inspect AI does.
- km003c-rs is MIT OR Apache-2.0, not MIT only. mlx-vlm is MIT (verified).
- A "verification review" of #1788 conflicts with our rule never to read or run #1788.
- The "48-layer streamed pass in PR #680" is a driver that has not run on real weights.
- `phase_share.py` and `workload_sizing.py` are not on main.
- "Every public Apple J/token source uses rails" is false (Contra Collective). So is "existing quants have no fidelity evidence".
- llama.cpp #27742 (qwen4exp) was merged 2026-08-27 (verified; seat 1 had it unverified).
- zeus-apple-silicon's tested-chip list was re-verified today: no M3 Max.
- Inspect's `ModelUsageData` indeed has no `sample_id`, but `on_sample_event` makes a core change unnecessary.

---

## 8. Provenance and method

- **Inputs.**
  - Two inventory seats, verbatim in Appendices A and B.
  - 40 candidate entries, each carrying a verifier's verdict, existing equivalents, policy notes, required changes, first step and effort. Verifiers checked repo paths with `git show`/`git ls-tree` on origin refs, and upstream state with `gh api` and WebFetch, on 2026-11-07. A verifier marked as UNVERIFIED any source it did not open; this plan keeps those markers.
- **What I re-checked for this synthesis.**
  - The branch pins listed at the top.
  - That `docs/align/upstream_mlxvlm_d1/` exists on `port/qwen4-exp-mlx`.
  - That `/private/tmp/jwgold-run-l3/work/parity/head` exists (4.7 GB), and the Air's free disk (51 GiB, 89% used).
  - Upstream facts were not re-fetched; they are the verifiers'.
- **Merging rules.**
  - Where two verifiers disagreed, this plan keeps the more conservative claim and names both options:
    - CodeCarbon stage 2 (restart #752, or the #1269 SMC leg);
    - the macmon thread (#117 over #118);
    - the Zeus capture rig (MBP or Air);
    - `inspect-energy` resolution (per generate via `on_sample_event`, or per sample).
  - Where one verifier found prior art that another missed (transformers-to-mlx; the jyohukuchan dataset), the prior art stands.
- **Out of scope.** Releasing the instrument itself (Paper 1) and ALIGN's energy-as-monitor method (ALIGN paper).
- **No restricted path was opened.** No upstream code was executed. Nothing was posted.

---

## Appendix A. Seat 1 inventory report (Fable 5.1), verbatim as relayed to the synthesizer

~~~~text
## Fable seat: OSS-contribution inventory of JouleWise (2026-11-07)

### Scope and method
- Canonical clone `/Users/edr/code/CapstoneProject/jw-wt/handoff`, `git fetch origin` done; `origin/main` at `ca2d1ee97`. All lane content was read with `git show <ref>:<path>` (no worktrees created, none to remove). No `~/jw-b5-*`, `~/night-*`, `night-custody`, `night-archive` or `restricted/` path was read or listed; Block 5 outcomes were not opened (the lead RESUME on main says Block 5 is "one defect from release", so B5 data is still sealed and is NOT proposed anywhere below).
- Branches inventoried: `origin/main`, `origin/port/qwen4-exp-mlx` (`9452a2bb4`), `origin/lane/2026-11-06-qwen4exp-quality-ref` (`92042869a`), `origin/lane/2026-11-06-v4-r1-integrated` (`e901eb2a4`), `origin/lane/2026-11-05-align-pilot10-benign` (`5f817856b`), plus `lane/2026-11-05-qwen4exp-port-perf`, `lane/2026-11-07-qwen4exp-mbp-live` and `records/2026-11-07-qwen4-l3-reference-top64` where the port docs pointed at them.
- Important structural fact: `origin/main` does NOT contain `joulewise/align/`, `joulewise/b6/`, `joulewise/bytes_analysis.py`, `docs/align/` or the qwen4_exp port. Those live only on the ALIGN/port lanes (merge-base with main is `d842f697f`, 2026-10-27; main is not an ancestor of the lanes). Any packaging effort must start from a lane, not main.
- Web verification: every upstream claim below was opened with WebFetch today (mlx-lm PR #1788, mlx-vlm issue search, zeus-apple-silicon README, CodeCarbon #731 and PR #752 and `docs/how-to/ai_policy.md`, mlx-lm and llama.cpp CONTRIBUTING, Zeus CONTRIBUTING, lm-eval `lm_eval/models` listing, ml-energy/leaderboard README, Inspect extensions page, km003c-rs, km003c-protocol-research, macmon PR #118, ControlArena `settings/shade_arena`). Items marked UNVERIFIED were not opened.
- An earlier Opus shortlist exists at `docs/oss_contributions_shortlist.md` (port and quality-ref lanes, dated 2026-11-05). This inventory covers what it excluded (the port itself, the D1 kit, the gold-parity and quant-quality harnesses, thermometry, guards, analysis pattern, SHADE pieces, datasets) and corrects three of its upstream facts (see "Corrections").

### Repo LICENSE status
- Root `LICENSE` on main: **MIT, "Copyright (c) 2026 Ed R (mpmdw)"**. `pyproject.toml` declares `joulewise` 0.1.0, core stdlib-only, extras `mac = ["mlx-lm>=0.31.3", "transformers<5.13"]`. No `license` field in `pyproject.toml` and no CITATION file; add both before any package release.
- The canonical port module header reads "Copyright 2026 JouleWise" (no SPDX line); fine under the root MIT, but an mlx-lm PR needs the MLX header style and Ed as author. MIT is compatible with every target found: mlx-lm (MIT), llama.cpp (MIT), mlx-vlm (MIT per its repo, UNVERIFIED this session), Zeus (Apache-2.0, contributions licensed Apache-2.0, no CLA), CodeCarbon (MIT, no CLA), Inspect AI (MIT), lm-eval (MIT, CLA per shortlist, UNVERIFIED).
- SHADE-Arena upstream is MIT (Scale AI et al.); JouleWise's port vendors nothing and pins commit `6614e771…` by a blob-hash manifest (`joulewise/align/shade/upstream.py`), so redistribution questions do not arise for the harness code.

### Custody constraints that bound every item
- Block 5 energies/outcomes: sealed until the registered release; nothing below uses them.
- BYTES: held-out rows are blinded; `scripts/b6_release_subset.py` releases keys only after the registered stage boundary. Only BYTES' non-energy, file-derived byte records are proposed now.
- ALIGN: no energy-as-monitor result before the paper. Only instruments, harness code and synthetic validation are proposed.
- KM003C fixtures in `tests/fixtures/km003c/` come from the 2026-10-06 desk/wall-meter probe and the repo's own 20 s desk recording (`provenance.json`), not from study windows: releasable.
- Upstream AI-use policies (opened today): mlx-lm and llama.cpp allow disclosed AI code but prohibit AI-written issues/PR text/replies; llama.cpp bans undisclosed AI use and limits new contributors to one open PR and no trivial fixes, bug-fix PRs need a failing-then-passing regression test; Zeus forbids "meat proxies" and wants an issue first; CodeCarbon requires an accurate four-tier AI disclosure and local testing. Consequence: Ed writes every upstream sentence himself; this inventory deliberately contains no draft PR text.

### Corrections to the 2026-11-05 shortlist (from today's fetches)
1. macmon PR #118: still open, zero review comments; the maintainer has NOT asked for independent validation (the shortlist implied the project asks for it). A validation table is still useful but unsolicited.
2. CodeCarbon: the macmon-based Apple backend PR #752 (opened Dec 2024) is still open, was threatened with closure on 2026-10-09, and a maintainer asked a colleague to take it over. That is a concrete "adopt the stalled PR" opening, not a from-scratch backend.
3. mlx-lm PR #1788 (qwen4_exp) is open since 2026-08-29, labelled "await verification: requires a human expert to verify its correctness", last activity 2026-10-04. JouleWise's gold-parity evidence is exactly the missing verification; the cheapest high-value move is a reviewer-style verification on #1788 (Ed-written) rather than a competing PR, with a competing PR only if the author has stalled. mlx-lm main has no qwen4_exp model file (consistent with #1788 unmerged).
4. mlx-vlm: today's issue search for `qwen4_exp` shows #2581, #2526 (open) and #2048, #2041 (closed); none mentions the ragged-batch QSA bug, `indexed_attention` or padded no-cache scoring, so D1/F1/P5 remain unreported.

### Sequencing suggestion (Ed's time, not agent time)
Week 1 (fixtures only, no Mac time): mlx-vlm D1 kit, llama.cpp `indexed_attention`, mlx-lm `reasoning_content` round trip, km003c re-delivery test and protocol-research docs, BYTES byte-records dataset. Week 2–3 (needs the Saturday MBP validation first): Flash-Next quant + model card, L3 top-64 reference dataset + quant scorer, #1788 verification. After Block 5 release: energy-methods note, prereg/blinded-analysis templates, Zeus/CodeCarbon validation tables (fresh unregistered captures), inspect-energy. Long-running: gold-parity package, power-trace attribution package, CodeCarbon backend adoption.
~~~~

## Appendix B. Seat 2 inventory report (Opus 5.5), verbatim as relayed to the synthesizer

The relayed text ended with a paragraph beginning "Rules (mandatory)". That paragraph is the workflow's rule block for this task (repo, worktree, blinding and commit-identity rules), not part of the seat's report, so it is omitted here. Its substance is reflected in the Status line and §8.

~~~~text
JouleWise open-source contribution inventory (Opus seat, 2026-11-07). Planning only. Nothing was posted, filed, commented or merged. No worktree was created and no file was written: every repo read used `git show` / `git ls-tree` on origin refs in /Users/edr/code/CapstoneProject/jw-wt/handoff after `git fetch origin`. Blinded paths (jw-b5-*, night-*, restricted/) were not touched.

1. REPO LICENSE STATUS
- mpmdw/JouleWise is PUBLIC. LICENSE is MIT, "Copyright (c) 2026 Ed R (mpmdw)", and GitHub detects it as MIT. The lanes inherit the same file.
- Gaps to fix before any package or dataset release:
  - pyproject.toml has no `license` field;
  - there is no CITATION.cff;
  - there is no NOTICE or third-party file.
- Third-party material in the tree:
  - The KM003C protocol constants and AES keys come from okhsunrog/km003c-protocol-research (MIT). The docstring cites a local night-archive copy; cite the public repo URL instead.
  - SHADE-Arena is fetched at a pinned commit and not vendored (jkutaso/SHADE-Arena, MIT).
  - The Qwen chat-template and tokenizer fixtures are under Qwen's model license. Qwen/Qwen3.8-Flash-Next is "qwen-community-1.0": redistribution of derivatives is allowed with the notice; the license is silent on sharing outputs or logits.
  - e2e items: GSM8K (MIT), IFEval excerpts, public-domain Austen.

2. PRIOR WORK
- docs/oss_contributions_shortlist.md (2026-11-05, ranked top 8) already exists, but only on lanes (port/qwen4-exp-mlx, lane/2026-11-06-qwen4exp-quality-ref, lane/2026-11-06-qwen4exp-port-r2), not on main.
- Per the prune/canonical rule, land ONE merged OSS doc on main with a CANONICAL.md row. This inventory extends the shortlist, which kept only upstream PRs, with datasets, packages, model cards and write-ups.
- Correction to that doc: it calls the measurement Mac "macOS 15.7.7". B5's calibration build 25G83 and the 11-07 resume ("macOS 26.6.2") say it runs macOS 26.

3. UPSTREAM STATE RE-VERIFIED TODAY (gh api / WebFetch)
- mlx-vlm qwen4_exp (Neywa-Labs/mlx-vlm, pushed 11-07): config.py lines 98-112 still maps only full_attention and raises on `indexed_attention`.
- llama.cpp conversion/qwen4exp.py line 89 still writes ratio only for "full_attention", so a re-saved checkpoint gets ratio 0.
- km003c-rs measurement.rs: MAX_CONSECUTIVE_REJECTED_SAMPLES=8 then previous=None (lines 24 and 132); the bug is still present.
- mlx-lm:
  - `reasoning_content` appears only in chat_templates/deepseek_v32.py, so the server round-trip bug is still unfixed and unreported.
  - PR #1788 (qwen4_exp) is OPEN, last update 2026-10-04; mlx-lm has no qwen4_exp model.
  - NEW: mlx-lm PR #1146 (`mlx_lm.kld`, a top-K plus tail-bucket KL cache) was closed 2026-08-21 by a maintainer for review capacity ("closing the non-essential ones"). So a quant-quality scorer should not target mlx-lm, and mlx-lm PRs generally must be essential and tiny.
- macmon:
  - PR #118 is open with 0 comments.
  - The README now says macOS 27 broke the rootless IOReport Energy Model; macmon uses undocumented AppleCLPC mappings, which raises the value of an independent meter reference.
  - Issues #12 (M4 temperatures wrong, 13 comments) and #68 (M2 Ultra GPU reads 5 °C) are open.
- CodeCarbon:
  - docs/explanation/methodology.md:93 says powermetrics is "Effectively unreachable on Apple Silicon" (cpu_load is chosen first).
  - #731 and #1269 are open.
- Energy leaderboards: AI Energy Score is H100-only; ML.ENERGY v3 covers H100/B200, though its release post invites runs on other hardware.
- Prior Apple J/token work: GreenBench uses powermetrics only; Anubis "system power" does not name its source. A meter-validated Mac dataset is still a gap.
- AI-use policies (CONTRIBUTING read):
  - mlx-lm and llama.cpp: AI code allowed if disclosed; AI-written posts strictly prohibited. llama.cpp can ban accounts for undisclosed AI use.
  - transformers asks first-time contributors not to use code agents for issues or PRs.
  - CodeCarbon: AI-assisted only, and the submitter must be the "Sole Responsible Author".
  - Zeus bans "meat proxy" submitters.
  - Inspect welcomes disclosed AI use.
  - mlx-vlm CONTRIBUTING has no AI section.
- So: Ed writes every word a human reads, and Ed (not an agent) runs any upstream code, because agents may not execute unvetted community code.

4. CUSTODY RULES APPLIED
- Block 5 is one defect (D5) from release, and nothing is unsealed without Ed.
- BYTES held-out rows and every ALIGN energy-as-monitor result stay sealed until their registered releases.
- Candidates 1-17 and 20 need no sealed data.
- Candidates 18-19 are after release only.
- Candidate 7's per-chip SMC inventory needs Ed or the magistrate to export R0 SMC journals from /Users/edr/night-align. They are engineering, not outcome-bearing, but they live under night-*.
- Candidate 5: the PDTR-vs-meter slope summary (0.968, SD 0.0034, 12 sessions) is already public in km003c_parse.py. Raw sources must not be reused without a custody check; a fresh desk capture is cleaner.
- Items needing the MBP (5, 6, 7, 8, 9, 13, 19) wait for the magistrate's ALIGN schedule.

5. SUGGESTED ORDER
- This week (Air-only, small, crisp, builds Ed's name): 1 (mlx-vlm D1), 2 (indexed_attention), 3 (mlx-lm reasoning round-trip), 4 (km003c-rs). Then 9 (Flash-Next top-64 reference on HF, after extending the prompts).
- Next: 5 and 7 (macmon data comments) once a fresh desk capture fits the MBP schedule.
- Then the flagship 6 (CodeCarbon backend), with 8 (Zeus) as a by-product.
- Write-ups 10, 12 and 14 can overlap Paper 1 writing.
- 11 (mlx-lm qwen4_exp) needs Ed's GOAL-item-10 go, and is probably best offered first as differential evidence on #1788.
- 18 and 19 follow the B5 and BYTES releases.
- 20 follows the ALIGN paper.

6. CONSIDERED, NOT RECOMMENDED
- lm-evaluation-harness MLX backend: mlx-lm already ships `mlx_lm.evaluate`.
- An mlx-lm KL command: see #1146 above.
- A new standalone KM003C Python package: km003c-rs already ships a Python wheel; fix upstream instead.
- NVML / INA3221 samplers: Zeus and jtop cover them.
- MoE routing hooks: low novelty.
- Hybrid prompt-cache checkpointing: mlx-lm #1596 and #1515 already closed, per the 11-05 doc.
- Any diagnostic-era voided (D-078) energy corpus.

7. SOURCES
- Opened today:
  - gh: ml-explore/mlx-lm PR #1788, PR #1146, CONTRIBUTING.md, code search for reasoning_content and kl_div.
  - gh: Neywa-Labs/mlx-vlm models/qwen4_exp and config.py; ggml-org/llama.cpp conversion/qwen4exp.py and CONTRIBUTING.md.
  - gh: okhsunrog/km003c-rs measurement.rs; km003c-protocol-research metadata.
  - gh: vladkens/macmon readme, PR #118, issues #12 and #68.
  - gh: mlco2/codecarbon methodology.md, AI_POLICY.md, #731, #1269; ml-energy/zeus CONTRIBUTING.md; zeus-apple-silicon metadata.
  - gh: UKGovernmentBEIS/inspect_ai #6246 and CONTRIBUTING.md; control-arena settings/shade_arena; jkutaso/SHADE-Arena metadata; huggingface/transformers CONTRIBUTING.md; exelban/stats metadata.
  - Web: https://huggingface.co/api/models?search=Flash-Next ; https://huggingface.co/api/models/Qwen/Qwen3.8-Flash-Next ; https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/main/LICENSE ; https://huggingface.github.io/AIEnergyScore/ ; https://buttondown.com/ml-energy/archive/release-the-mlenergy-leaderboard-v30 ; https://arxiv.org/abs/2608.28667 ; https://uncsoft.github.io/anubis-oss/analysis.html
- UNVERIFIED today (carried from the 11-05 shortlist, not re-opened):
  - zeus-apple-silicon's tested-chip list (no M3 Max);
  - transformers #48974, #50169 and #49694;
  - mlx-lm #1896, #1997 and #2013;
  - Inspect's missing ModelUsageData sample_id;
  - macmon agents.md validation wording.
~~~~
