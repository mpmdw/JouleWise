# Charge — cold FINAL PASS A291-FINALPASS-01: MERGE / NO-MERGE on PR #409 head `c5cbfd9e`

Assembled 2026-09-25 ≈04:10 PDT by the resident magistrate (Opus 5.5, activation 278ebc9e). Nothing is armed.

## What is asked

Rule MERGE or NO-MERGE on the exact merge candidate: PR #409, branch `fix/2026-09-24-a291-merge-candidate`, head **`c5cbfd9eeefe6aa3dc7f323f1da7f6593b069a59`**. The lane is A291, the scored-roster packer (`joulewise/scored_packer.py`, `joulewise/scored_registration.py`), with its independent checker, ownership-forgery harness, fuzz and stress modules. Ruling A291-PREMERGE-01 (`ex-112-premerge-ruling.md`, §3 V3) lists the ten items this packet must carry. Per that ruling, a missing item is a REFUSE of this pass, not a NO-MERGE. Items 1–3 must verify by your own execution.

## The ten items (exhibit map)

1. **The sha:** `ex-01-sha.txt`. It gives S, the parents, the merge-base, the file stat against main and the blob shas. `origin/main` has moved on since (docs-only interactive-4b commits); the magistrate checked that S merges with current main cleanly and that `gen_state --check` passes on the merged tree.
2. **The diff:** `ex-02a` is post-review commit d2e751df (V1 a+b). `ex-02b` is 37f47475 (the kernel retirement that cures main's generated-region drift). `ex-02c` is 7c56aa33 plus its revert 72808d82. `ex-02d` is b1913497 (the CI patch-target fix). `ex-02-diff-note.txt` gives the lane-only stat from `3fb98469` to S.
3. **Re-gate outputs:**
   - `ex-03-regate-d2e751df.log.txt`: 49 tests OK;
   - the new test FAILS with the 3fb98469 packer (RecursionError) and PASSES at d2e751df — reproduce it yourself (the charge allows own execution for items 1–3);
   - `ex-115b` (fresh eyes) re-ran the patch-target test under both import styles.
4. **Evidence transfer:** `ex-04-evidence-transfer.md` and `ex-04-packer-diff-6e2504b1-S.patch`.
5. **F-C replay evidence:** `ex-104-fc-replay.jsonl` (all nine REFUSED by `_replay_roster`, inv_38/inv_39). F-B's is in `ex-106-fb-adjudication-and-replay.jsonl`. The adjudications are `ex-104-fc-adjudication.jsonl` and the F-B file.
6. **Full suite:** `ex-06-fullsuite-summary.txt`. It ran at S: 7,131 tests, 1 failure outside the lane (a timing flake that passes when re-run alone and passes in hosted CI), 109 skipped. The lane-module tails are included. **Hosted CI:** `ex-11-ci-checks.txt` shows run 36098330718 on S, conclusion success; gate-ledger is pending rows 7, 9 and 12.
7. **Lens reports, counter-review and dispositions:** `ex-110a`, `ex-110b`, `ex-111b` and `ex-07-dispositions.md`. The fresh-eyes reports are `ex-113b`, `ex-114b` and `ex-115b`.
8. **The entry-witness code note:** in `ex-07-dispositions.md` and `ex-107b`/`ex-108b`. The INV-23/36/37 witnesses assert inv_38/inv_38/inv_11, not the listed inv_23/inv_36/inv_37.
9. **The R4-2 final text, verbatim:** `ex-85-a291-final-texts-r4.md` (R4-2 (a)–(e)) as amended by `ex-95-a291-final-texts-r4b.md`. The contract is v4.1 (`ex-89`).
10. **This charter pin with the validator receipt, and the PR ledger draft:** `ex-pr-ledger-draft.md`; `ex-10-validator-receipt.json` is the receipt of the validator run IN A JUDGE-STYLE WORKTREE on this packet as it stood before ex-10 was added (a packet cannot pin its own final digest). Your own validator run is the binding check. Re-convened after REFUSE run 1 (`20-refused-run1-ruling.md`, cure §2.2 applied: the gitignored `.log` exhibit is renamed `.log.txt` with identical bytes).

Other context: `ex-105-forger2-ruling.md` (the forger-seat rulings) and `ex-100b` (mutation kills).

## Constraints on the judge

- Read-only; nothing is armed.
- Never run `sudo`, `launchctl`, `powermetrics` or `systemsetup`.
- Never touch `/Users/edr/code/JouleWise`, `/Users/edr/night-custody`, `/Users/edr/JouleWise-measurement-*` or `~/Library/LaunchAgents`.
- Code evidence comes from `git show <rev>:<path>` at S or at the named revisions. Execute items 1–3 in a `git archive c5cbfd9e` copy under `/tmp`: the named tests, not the full suite.
- Write only the ruling file.
- Do not read RUN_STATE.md, TASK_QUEUE.md, council logs, memory, or `docs/process_traces` files outside this packet directory.

Finish with a one-line verdict **MERGE** or **NO-MERGE** (or REFUSE with the missing item), and the exact text the gate-ledger row 7 should carry.

## Charter pin

Charter (operative v2): `docs/process/coldgate_charter.md`
sha256
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## Exhibit manifest

```
ca755344c9d01b91e9b17049ca72bc40bd524416deea87a91773b448a41fd23a  ex-01-sha.txt
4ed8685cded47474f6bbc3adbc81f36aad62fab7879da21527baf014e5451e2b  ex-02-diff-note.txt
45c9f347fffbed4ffd02fe8cb1992ed5118f8c85c69892d1ec72b1fccae74f70  ex-02a-postreview-d2e751df.patch
1c5d30b5d2ba9403d12550bad5cc73e62d75bd0c0dd58fbca852baef77b46d75  ex-02b-postreview-37f47475.patch
1fcb0563392f95d07e9a36dc2625575b1b79b1c3ba0ee0213b34a2f6cf74274d  ex-02c-revert-72808d82.txt
0ea9309196a83a3f26cd3c79de833a1436f53f052b0dc8e3fd85431d590ee3ae  ex-02d-postreview-b1913497.patch
02d0224c89b9b3e6e962702ea1ba50e042fc31510d0de99df5f272ebf84bd559  ex-03-regate-d2e751df.log.txt
163718b0b3d25ce7aaa9789033c0f417aab297c6ebc74ce78f04dbfd8d538e4b  ex-04-evidence-transfer.md
226b0a052ce54c63914b5d2071fea5b0b9db1a318fc14c37d07f4957d3b92865  ex-04-packer-diff-6e2504b1-S.patch
051002a0a4e4d0f760f8ed262c1bf07963f03af84b15c54cf31bc977d4e54686  ex-06-fullsuite-summary.txt
fcce02d383da7a830b3f17da89c164a70ca050a7ab57459c0c0bf73b00517abc  ex-07-dispositions.md
f48180cb4e3099bdc9e4f751b59c377f0a57d7c104f8da88b46b89d25a4e9e65  ex-100b-a291-mutation-kills-report.md
74f939a525f502f1b24286e3e4e150c116d9dff6f9a6240045cfd24a66a0d9aa  ex-104-fc-adjudication.jsonl
6907ef161d63f3011859881bcdcc767d729c4589c4455b673979a2fa55c85203  ex-104-fc-replay.jsonl
80f54b7ad4557bf3123c977847343acea5a0692828a4598aa9abf64635417fdb  ex-105-forger2-ruling.md
2ba12cf54dbad0c8e726ace48c806a172200aa33ee7a7b808cce804f18029953  ex-106-fb-adjudication-and-replay.jsonl
caddf2b5b44b25d50c8daaaf5a147a970c7be36b17a5cd80ab482a0bf49e2676  ex-107b-a291-typed-code-line.md
c22c568c90ca02c94d1dfa600cbad60d214dc899817630bee025a30629878b1e  ex-108b-a291-entry-witness-report.md
3136c7665a2cb9932cbd46c4f9a2688dc9fea21e8f20c5f093b0bdee19d97f4a  ex-11-ci-checks.txt
7a5de37f1c3dd121a6b169eaa636907c0b4a617c89aeb1e00002df4a1c46b051  ex-110a-a291-r3-contract-lens-astra.md
81551579b7804c13d931e5c581429bcf3d5a66a4e4621f3b6ec678e4a0aeca6e  ex-110b-a291-r3-execution-lens-sol.md
7717e5485a8d70e1ec556bf06c41794e3e5281b13efb57c80b0861ef5044d2c6  ex-111b-a291-opus-counter-review.md
9e388c8c85fdce9aa81b17c546d7377eb658a7bb485e16962a04f3a12471df65  ex-112-premerge-ruling.md
d83ff90a5f2a740fa55ff36833f1b11e22006fa04a084c026b9302b108a760e2  ex-113b-a291-fresh-eyes.md
0a40a090b538eb6943a31e0256a33b7492067505820129002408f8c25e0fb98e  ex-114b-a291-fresh-eyes-2.md
477b801fe86078344bd3842d1ffbc97e2b4d77cc7984d6b0ef37d973a6669fda  ex-115b-a291-fresh-eyes-3.md
14692d3ad6ef23c3e90785b24c58fb528e1af5903059227e4b2703d5edac8923  ex-85-a291-final-texts-r4.md
d88d10ddd8e4482988b740068306976ce093ce82fdb31498245985d3a603306d  ex-89-a291-contract-v4-1-inv11-closed.md
63787c28d620c4811b327b85cf7d57db12eddf29aa40a0d17337ec87affd9b87  ex-95-a291-final-texts-r4b.md
5a04d0966395e4462a5ce398df10c7b3f63064e34624e989cdddc3aee1543ed3  ex-pr-ledger-draft.md
```
