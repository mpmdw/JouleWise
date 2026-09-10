PROPOSED (magistrate ruling due after rehearsal acceptance)

# G2-a night handback replacement — 2026-09-12

Paste the four sections below into `docs/process/NIGHT_HANDBACK.md` after
harvesting rehearsal-20260911. Keep that file's introduction and Standing
rules unchanged. Replace the H-CLONE marker with its literal path when
pasting; fill only the harvest facts from retained evidence. The inventory
proposal and activation commands after the replacement are bench material,
not courier text. This draft is not an arm record.

## Purpose of this night

Plan `d117-g2a-prefill-probe-20260912`, class `DIAGNOSTIC_NO_PACK`, is planned
for 2026-09-12 at 02:56:00 PDT (`t0`, epoch 1789206960; 09:56:00 UTC), with
a 12,600-second window. The measurement allocation ends at 06:26 PDT.
The courier deadline is `t0 + 12600 + 300`, epoch 1789219860, 06:31 PDT
that morning, 29 minutes before the 07:00 dead-man. This notice describes
the planned night; the arm record establishes whether installation happened.

This is the first real G2-a window: the unchanged full chain, including
calibration before and after the probes, four prompt lengths (512, 1024,
2048 and 4096 tokens), five small-model members and one large-model member
at each length. The small model is Qwen3-1.7B; the large model is Qwen3-8B.
A member is one recorded probe run. The chain includes its existing
600-second settles. Its programmed planning subtotal is about 2 hours
40 minutes before variable overhead; the window allows 3 hours 30 minutes.
These are diagnostic measurements, not claim-bearing campaign numbers.
There is no production pack and this night does not authorize G2-b.

The magistrate's 2026-09-10 disposition of short-first selects this unchanged
full chain as the first real window. Ed was emailed at 04:50 PDT with three
options (Gmail message `1a08b223b02862e9`); silence means full chain under
that disposition. An owner-authored directive issue can override the choice
until arm. Ed's NO on the night notice thread stands the night down.

`repo_head = measurement_head = H = this commit`: H is the main commit
that rewrites this handback and adds this deployment's inventory row,
after the rehearsal harvest and the gate-repair merge. The measurement root
is `<H-CLONE: /Users/edr/JouleWise-measurement-v5-20260911-g2a>`, a fresh,
independent GitHub clone detached at H. Both night agents are installed
FROM that clone. Its name has no head hash because its inventory row must
already be inside H. The provisional 078a13a4 clone is not the armed clone.

The production ledger lives in this clone's own
`runs/calibration_observation_ledger.jsonl`. The magistrate ruled a byte-exact
restore from the canonical ledger (76 records, SHA-256
`aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`), followed
by authentication with `verify_custody=True`. The ledger's custody locators
are absolute iCloud paths; no custody directories are copied or locators
rewritten. Record 05 documents this route on the provisional clone; the
activation repeats the authentication at H.

Install both agents on **2026-09-11 between 03:00 and 06:30 PDT**. The
first 07:00 dead-man that morning should stand down because this night's
completion time has not arrived. Never install in the 07:xx hour. Send the
consolidated notice after commit H and after retiring the stub, before the
plan is moved into place. This is an ordering rule; it adds no fixed minimum
notice interval. Record the accepted send and the available NO channel.

The arming activation exits after recording the arm. Its absolute exit
boundary is 2026-09-12 02:31:00 PDT, epoch 1789205460 (`t0 - 25 minutes`).
The watchdog's 02:45–03:30 belt does not reopen this longer window: the
plan span remains protected through the closed 06:31 completion boundary,
and later if delivery or recorded process termination is unresolved.
All agents must be gone for launch and acquisition. Power, clock and
machine readings taken at arm are observations; capture-time gates remain
live. A green stub says nothing about the capture-timeout seam.

## Executed — rehearsal-20260911

The prior night was armed by activation `7ce7af2a-8eb6-470e-bf56-70f714977293`
from the frozen triple (`rehearsal-20260911`,
`/private/tmp/joulewise-rehearsal-20260911-checkout`,
`57ddad20226c6921d81a87b9d78e61950c14a74f`), recorded in
`docs/process_traces/2026-09-09-rehearsal-harvest/123-rehearsal-20260911-arm-record.md`.
The harvest records result verdict `<HARVEST: result verdict>`, chain exit
`<HARVEST: chain exit>`, and `<HARVEST: receipt verdict, C1-C5 rows, or refusal
reason and detail>`. Courier message `<HARVEST: message id and inbox-delivery
evidence>` and results branch `night-results/20260911` at `<HARVEST: verified
remote results-branch SHA>` are retained with the harvest. The pre-night
dead-man line occurred at `<HARVEST: actual ISO line time>`; comparison with
the arm-time empty baseline shows `<HARVEST: night/ file inventory with sizes
and timestamps, and whether any file came from that firing>`. Acceptance
items 5/6 were `<HARVEST: magistrate acceptance decision and evidence record>`.
After preserving evidence and clearing recorded chain/campaign ownership,
both stub agents were `<HARVEST: uninstall result>`, and the disposable
checkout and plan root were `<HARVEST: removal result and evidence pointer>`.
These fields are filled from the harvest before H is committed; no expected
result is substituted for an observation. Item 4 closes only when the new
stage-1 notice is actually accepted before the diagnostic arm.

## Where the results are

- Night custody: `/Users/edr/night-custody/d117-g2a-prefill-probe-20260912`.
  Read `night/result.json`, then `night/receipt.json` or `night/refusal.json`
  as the result directs. Retain `chain.started`, `chain.exited`,
  `censuses.jsonl`, chain stdout/stderr, `courier.sent`, `courier.json` and
  launchd logs. A gate `GO` alone does not prove chain success: report its
  actual exit code and any abort.
- Driver log: the same custody root's `night.log`. Expect the 09-11 07:00
  pre-night stand-down line before the 09-12 night gate line; verify it.
- Results branch: `night-results/20260912` on `origin`, if the driver's push
  succeeded. Verify the branch and actual SHA; do not presume publication.
- Probe corpus: `/Users/edr/JouleWise-shakedown-g2/g2-a-20260912`.
  The separate probe root holds the member bundles, calibration custody,
  operator logs and `window-plan/` inputs and summaries. Its two key outputs
  are `d166-prefill-counts-receipt.json` and
  `d166-prefill-resolvability-summary.json` under `window-plan/`.
  A pushed night-results branch does not establish backup of this corpus.

## Next lane for d117-g2a-prefill-probe-20260912

The relaunched magistrate carries the frozen triple
(`d117-g2a-prefill-probe-20260912`,
`/Users/edr/JouleWise-measurement-v5-20260911-g2a`, H). It harvests after the
protected completion boundary, delivery checks and recorded chain/campaign
ownership are clear. `courier.sent` alone does not clear a running or
indeterminate process. Report the actual receipt, result, chain exit,
courier message, remote branch and watchdog liveness.

Acceptance needs a diagnostic `GO` receipt with C1/C3/C4/C5 `PASS`,
C2 `NOT_APPLICABLE/no_pack_by_design`, result chain exit 0 and no abort,
plus authenticated probe evidence at all four lengths. Preserve all 24
members and both calibrations. The post-bracket boundary must record
`session_state=finalized`, `pin_relation=physical_ahead`,
`refusal_code=calibration_ledger_head_mismatch`, and a non-null
`terminal_head_pin_candidate`. The tracked ledger pin stays unchanged
during the window; this expected terminal boundary is not a failed night
receipt. Cure any actual refusal before another attempt; never re-arm the
same plan on the same failure signature twice.

Before consuming any G2-a number, close `GATE-SENSIBILITY-SWEEP-01`, perform
the reviewed terminal-pin advancement and the owning desk checks, then
use the authenticated four-length summary for selection. Prompt-pin
issuance also needs the counts receipt, prompt ladder, input inventory
and selection record. Keep diagnostic and claim-bearing evidence distinct.

After evidence preservation and process clearance, uninstall the two
agents FROM the pinned clone and retire the discoverable plan through the
governed handback. Preserve the production clone and raw probe custody.
Do not apply the stub checkout/plan-root deletion recipe to this corpus.

**Standing rules** <!-- F11 -->

Retain the existing Standing rules block in NIGHT_HANDBACK unchanged,
including canonical `write_night_plan` authoring, clone-based installation,
the frozen-checkout list, plan-derived interpreter routing, and the separate
D-176 pack-bound rehearsal/G7 handback. See
[the existing block](../../process/NIGHT_HANDBACK.md).

---

## Production inventory row for H

Append exactly this object to the existing JSON array, preserving every
retained entry. Do not write a hash into the clone name or chase a commit
containing its own SHA-named path. The literal path replaces the H-CLONE
marker in the handback pasted above.

```json
{
  "deployment_id": "JouleWise-measurement-v5-20260911-g2a",
  "measurement_root": "/Users/edr/JouleWise-measurement-v5-20260911-g2a",
  "custody_root": null,
  "ledger_path": "/Users/edr/JouleWise-measurement-v5-20260911-g2a/runs/calibration_observation_ledger.jsonl",
  "notes": "G2-a production deployment for 2026-09-12; fresh GitHub clone at the handback and inventory commit H. Restore the canonical 76-record ledger byte-exact and authenticate its absolute iCloud custody locators with verify_custody=True; no separate deployment custody root is attested."
}
```

Constraints at inspected `078a13a461abd124c29796798da5107fe00190a6`:

- `joulewise/arm_readiness.py:279–309`: inventory is a nonempty list/tuple;
  each row has exactly `deployment_id`, `measurement_root`, `custody_root`,
  `ledger_path`, `notes`. ID is a unique nonempty string, notes is a string;
  measurement root is an absolute string, custody/ledger are absolute strings
  or null. There is no per-row SHA field or basename/head coupling.
- `arm_readiness.py:253–276`: the file is regular/non-symlink and its bytes
  must equal `git show <plan.repo_head>:configs/production_custody_inventory.json`.
  Separately the **plan's** measurement root resolves with `strict=True` and
  its Git HEAD must equal `measurement_head`. This runtime requirement is
  not a requirement that every inventory row exist before commit H.
- `arm_readiness.py:310–329`: missing production roots remain census members
  (`resolve(strict=False)`; `FileNotFoundError` is retained, not filtered).
  Resolution errors remain explicit. Adding this row also adds measurement,
  runs and ledger census roles; null custody adds no invented custody root.
- `tests/test_rehearse_t0_unattended.py:61–108` checks byte equality against
  the plan's commit, using fixtures/mocks; its real temporary-Git case
  explicitly retains `/absent/retained` (line 82). Lines 140–146 check that a
  changed or resolution-error census cannot false-pass G6. There is no
  hard-coded inventory cardinality or dependency on `/Users/edr` existing.
  The current eight-test module passes; an append of this exact valid object
  is compatible in principle and can pass CI without Ed's directories.
  The proposed diff itself was not applied or tested in this drafting turn.

### Exact activation Git sequence

Use the authorized linked bookkeeping worktree; **no Git operation in
`/Users/edr/code/JouleWise`**, even a fetch/status. The following commands
are prospective. The activation fills and reviews the handback and appends
the object above between the two blocks; it does not copy this whole trace
file over the live handback. A small direct bookkeeping commit to remote
main is the supplied repository convention. Never force-push or bypass a
non-fast-forward rejection.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?Set the activation's authorized linked worktree}"
cd "$BOOKKEEPING_ROOT"
test "$PWD" != /Users/edr/code/JouleWise
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
git switch -c bk/2026-09-11-g2a-handback-H origin/main
# Confirm the reviewed gate-repair merge is an ancestor before editing.
: "${REPAIR_MERGE:?Set the reviewed gate-repair main merge SHA}"
git merge-base --is-ancestor "$REPAIR_MERGE" HEAD
```

Fill §Executed from harvest, apply the four replacement sections and append
the exact inventory row. Keep the introduction and Standing rules bytes.
Remove the proposal-only banner, instructions and H-CLONE marker from the
live handback. H is expressed as “this commit,” not as a self-hash.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?authorized linked worktree}"
cd "$BOOKKEEPING_ROOT"
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tests.test_rehearse_t0_unattended tests.test_docs_freshness tests.test_run_night tests.test_magistrate_watchdog
python3 scripts/gen_state.py --check
git diff --check
git diff -- docs/process/NIGHT_HANDBACK.md configs/production_custody_inventory.json
git status --short
test -z "$(git diff --cached --name-only)"
git add -- docs/process/NIGHT_HANDBACK.md configs/production_custody_inventory.json
git diff --cached --stat
# Lead reviews the staged bytes and only these two paths before committing.
git commit -m 'Prepare G2-a 20260912 handback and production inventory'
export H="$(git rev-parse HEAD)"
git push origin HEAD:refs/heads/main
remote_main="$(git ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
test "$remote_main_head" = "$H"
git show "$H:docs/process/NIGHT_HANDBACK.md"
git show "$H:configs/production_custody_inventory.json"
```

If main advances or push rejects, stop and review/rebase in the linked
worktree under lead authority; rerun affected checks and derive the new H
before cloning or notice. Do not repair this by changing a pinned clone.
Runbook 68's fresh-cut block then clones GitHub at H into
`/Users/edr/JouleWise-measurement-v5-20260911-g2a`. Recommend that route over
fast-forwarding/renaming today's provisional clone: it follows the trusted
recipe and avoids moving venv/editable-install absolute paths. The supplied
warm-cache ledger/venv work took under a minute; repeat it and reauthenticate
at H. Keep the provisional clone intact and unpinned; later housekeeping is
separate. No Git command, inventory edit or live-handback edit above was
executed by this drafting session.
