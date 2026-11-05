# ALIGN R0 daytime desk runbook

Run **on the measurement Mac only**, with no armed/active chain and all agent
apps/CLI sessions closed. This is selection data, not R1, thermal validation or
an arm authorization. Authority: council `219fb1515`, FINAL-DESIGN §§2.1, 2.2,
2.8. Keep the pinned stack: Python measurement venv, mlx 0.31.2, mlx-lm 0.31.3,
transformers 5.12.1. First integrate/review Stage-1 B1/B2 from
`lane/2026-11-05-align-v4-s1`; this runner refuses the old endpoint. Integrate
the SMC lane when ready. Do not run these commands from an agent session.

1. In Terminal at the integrated checkout, set the interpreter and config.
   The paths below are **examples to edit**, never auto-discovered. Model
   sources must be complete, materialized directories (no symlinks); revision
   pins are built in. Prepare/download/hash the pinned mirrors separately;
   this script never downloads. SHADE must already have its pinned cache.

   ```sh
   PY="$PWD/.venv/bin/python"
   mkdir -p .desk/align-r0
   cp docs/align/r0_desk.example.json .desk/align-r0/config.json
   nano .desk/align-r0/config.json
   ```

   Set both local model sources, SHADE cache parent, the measurement filesystem
   `disk_path`, any **additional measurement custody parents**, and verified pilot8/9
   offload destinations. `disk_path` must be on the measurement volume, not
   the offload volume. N revision is `9a2b46347bb170cb2924092175fa21554fe585a9`;
   D is `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9`.

   The real shared custody parent is `$JOULEWISE_CUSTODY_PARENT`, defaulting to
   `~/night-custody`; `JOULEWISE_ADDITIONAL_CUSTODY_PARENTS` (JSON array) is also
   always included. `custody_parents: []` in the example means no further extras.
   All resolved roots must exist as directories; missing/typo roots refuse the
   run and are recorded. Do not point this command at blinded study data.

2. Before the independently managed offload, save each source inventory to
   its configured inventory path. Set the four variables to the actual paths.
   Retain these JSON files outside the roots being offloaded. Offload/copy and
   any deletion remain the lead's verified-offload workflow.

   ```sh
   "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --inventory "$PILOT8_SOURCE" --output "$PILOT8_INVENTORY"
   "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --inventory "$PILOT9_SOURCE" --output "$PILOT9_INVENTORY"
   ```

3. Start the unattended desk run after the offloads and model preparation.
   Use a new record directory for every attempt; expect approximately 5–6 h,
   potentially longer for long-decode retries. AC power, Automatic initially.

   ```sh
   RECORD="$PWD/.desk/align-r0/$(date -u +%Y%m%dT%H%M%SZ)"
   nohup "$PY" -B scripts/align_r0_checks.py --config .desk/align-r0/config.json --output "$RECORD" >"$RECORD.log" 2>&1 &
   ```

   Every check can run separately with the same command plus, for example,
   `--checks template --models D`. Available checks: `host,disk,smc,load,template,generated,ladder,long-decode,memory`.
   A subset does not complete R0. The timeout is 7,200 s per long-decode
   **attempt**, ladder **episode**, generated **turn**, or other check. D's
   38,912-token decode at 10 tok/s takes about 3,891 s per attempt; two attempts
   get separate deadlines. A slow D host can use `--timeout 14400`. Native
   calls can delay signal delivery. A timeout fails the current check while
   retaining completed attempts/rungs/turns and sampled in-flight evidence.
   JSON/Markdown are saved at each progress boundary, including memory samples.
   Census failure refuses the run; there is no force option.
   If testing High Power, switch it manually and repeat `--checks host` into
   a new output directory; R1 owns the adoption decision.

4. Read `report.md` and its full `report.json`. Exit 0 means the selected
   checks passed; **`complete_r0: true` requires every check for both models**.
   Both files are updated after each check. Preserve failed/partial attempts.
   Local model SHA-256 lists authenticate the observed bytes only, not an HF
   revision. The SMC hook calls `scripts/align_smc_enumerate.py --output DIR`;
   absence is `unavailable`, never a pass. Confirm this CLI when that lane lands.

Interpretation: NLL uses the first 2,049 rendered benign SHADE IDs (2,048 next-token
targets), ≤3.0 nats/token. Synthetic rewrite tables diagnose templates; **generated**
transitions decide B7 (≥12 eligible transitions, D any closed-reasoning rewind;
N >10%). Insufficient transitions are inconclusive. D tries default xhigh,
medium, low, stopping at the first pass; N tries caps 4,096 then 8,192. Both
use spam/bank, indices 91–92, ≤6 turns/16,384 tokens. Screens admit only full-cap
turns that fit this total. D envelopes must parse ≥95% with no unsupported-format
flags. Long decode reaches 40,960 positions, logging
memory every 256 tokens; failure retries metadata evaluation at simulated
4,096-token boundaries and decode end. This is a diagnostic mitigation, not a
production change. Memory uses full context, N/D floor budgets 8,192/6,144,
guess bars 60/45 decimal GB, no swap growth. Disk needs ≥80 decimal GB free
after present weights and both offload hash matches (W1 two copies 37.2 GB;
D windows 52.9 GB). R1 must freeze actual budgets and other slots. The lead
reviews/commits the live record and handles B7, fallbacks, or a stack ruling
before R1; no live gate is claimed by this implementation lane.
