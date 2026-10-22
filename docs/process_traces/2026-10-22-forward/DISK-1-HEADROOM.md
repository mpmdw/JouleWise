# DISK-1: disk headroom before the next arm

Internal record. Workflow `forward-work-measurement-path` (run wf_045f5fdc-e9f), interactive session 2dc9c377, 2026-10-21 18:29 to about 19:00 PDT. Windows are paused (RUN_STATE item 64, `ops/stop-pause`); nothing was armed, loaded or stopped. H's desk (pid 44586/44587, root `/Users/edr/night-bytes/h-20261021T185555Z`) was running throughout and was not touched.

## Result

| Reading | Free on /System/Volumes/Data |
|---|---|
| 18:29 PDT, `df -g` at item start | 83 GiB |
| 18:39 PDT, `df -k` just before the first offload or removal | 83557928 KiB = 79.69 GiB |
| 18:46 PDT, `df -k` after | 98015576 KiB = 93.47 GiB |

Target: 90.3 GiB = H's P (86,236,568,521 B = 80.3 GiB, `H-DISK-RULING.md`) plus the 10 GiB in-window `disk.low` stop. After: 93.47 GiB, so the margin is +3.17 GiB. Free space fell by about 3 GiB between 18:29 and 18:39 while this item only read (other workflows and seats were writing), so the margin is not fixed. Recompute the target when BY-C5 gives the pass-session P: if pass-session P plus 10 GiB exceeds the free space at arm time, the shortfall is reported, and the candidates in "Left in place" below are the next ones to examine.

Freed: 55 worktrees removed (16.4 GiB of checkouts, by `du` before removal) and 1.8 GB of session roots moved to iCloud Drive and evicted.

## Offloads to iCloud Drive

Tool: `/Users/edr/night-archive/tools/icloud_offload.py` (the 10-05 and 283e9802 practice). For each source it writes one uncompressed PAX tar into `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-archive/2026-10-21-disk1/`, hashing every regular file with SHA-256 as it is read; reads the tar back from disk and checks every member's type, size, SHA-256 and symlink target against the walk; only then removes the source and leaves `<source>.icloud-pointer.txt`. Symlinks are stored as links (the `measurement/` links into `/Users/edr/night-custody/measurement/` were not followed and their targets were not touched). No special files. Eviction: `/Users/edr/night-archive/tools/icloud_evict` evicts a tar only when iCloud reports it uploaded.

Per-member manifests (every file's path, type, size and SHA-256): next to each tar in iCloud, and copied to `/Users/edr/night-archive/icloud-offload-2026-10-05/<name>.manifest.json`; index lines appended to `/Users/edr/night-archive/icloud-offload-2026-10-05/INDEX.tsv`. The table gives the SHA-256 of each evicted file (the tar), re-hashed independently after the tool finished (all six equal the index), and the SHA-256 of each manifest (iCloud copy and local copy identical), which binds every member's SHA-256.

| Source (removed, pointer left) | Evicted tar SHA-256 | Files | Bytes in files | Tar members | Manifest SHA-256 | Eviction |
|---|---|---|---|---|---|---|
| `/Users/edr/night-bytes/h-20261021T162149Z` | `7392f859c92ea2a83c6b0e85831a56253000529f7666c6bdb58d9eda953601dd` | 25459 | 781,120,779 | 28268 | `33ae620b6af46ccd6980a7293bff0dd56a99a13167ffa6c85df483e4f49f78ab` | evicted (dataless) |
| `/Users/edr/night-bytes/h-20261021T173856Z` | `1975a672ae0c551e40b2ce53c73f45c146b2eb2e913cac48721b4fa3b90dcf64` | 25731 | 791,796,664 | 28592 | `84f60830069c459fe418f35983a15a9508ff94b01d1db3d20521d2039c56dae2` | evicted (dataless) |
| `/Users/edr/night-bytes/dry-20261021T155002Z` | `9b7208a97038bf6243bbc4deee8bdee7a1e8beb94cfcfc2d36e8ff56fdbe3001` | 13 | 1,246,477 | 137 | `7bd9d132adf0ab932619989ddcbda447e4218363322ecfc16cd2e0ef96a7ea07` | evicted (dataless) |
| `/Users/edr/night-bytes/dry-20261021T164743Z` | `e4e19a3fe5337d3332d8bb896d4fe5d9ada01a203d97cf8eec3527b29836e1fd` | 166 | 1,548,163 | 314 | `855fed675acb7bbeb651945ea9f54ee7de76777fae62b6aafb79cf42e36fb36e` | evicted (dataless) |
| `/Users/edr/night-bytes/dry-f1f6-h3` | `6fa6222b5be8c181ca147e3a24cf6c00495dd1bb8d3f659a7b099d9c176661cd` | 223 | 194,795,192 | 391 | `1fa807605085dc80ab0676434939dd90873deaade383edecd64fb68b1f61afc3` | evicted (dataless) |
| `/Users/edr/code/JouleWise-wt/fix-g2a-root-id-double/docs/paper/build/out/draft-v1.html` | `315adcbf25e58440a8accd9dc7da537b3a20cd87af4ef6d5efc0b32e9ad25a52` | 1 | 169,994 | 1 | `9eacf8ab31a5286d98c4141a7fcf642b125fceeb7b90dbafefdb79a19324ef42` | evicted (dataless) |

Why each could go: the two H roots are zero-run attempts of item H (named in RUN_STATE items 61 and 62 and in the c5a1d8fd, a69c5394 and f1f6b9f1 magistrate records); they are attempt evidence, so they were offloaded with a verified copy, never deleted. The H runner (`scripts/bytes_h_session.py`, `scripts/harvest_b6_session.py` at the h2 checkout) reads only its own session root, and no workflow plan item reads these roots. The dry roots are dry prepares of item H (named in those magistrate records, so the same rule applies). `draft-v1.html` was the only ignored file other than `__pycache__` in a worktree marked for removal (`JouleWise-wt/fix-g2a-root-id-double/docs/paper/build/out/`, a paper build output that differs from the canonical build); it was offloaded before that worktree was removed.

To restore: `tar -xf '<tar>' -C '<parent of source>'` (iCloud downloads the tar on first read), then check members against the manifest.

## Worktrees removed

`git -C /Users/edr/code/JouleWise worktree remove <path>`, never `--force`. Each one passed, re-checked immediately before its removal: HEAD unchanged since the survey; `git status -sb` shows no `ahead`; `git status --porcelain --untracked-files=all` empty (clean, no untracked files; ignored files were only `__pycache__`); no stash on its branch; HEAD contained in a remote ref (column "Pushed in"); no process with the path on its command line and no open file under it (`ps`, `lsof`). The local branch refs were kept.

It was also not on any NEVER TOUCH list: not `/Users/edr/code/jw-wt/**` or the session scratchpad; not `JouleWise-wt-l9-s10`/`-s10f` (no L9 worktree was removed at all: L9-4 is open and the lane reads blinded data); branch not the head of an open PR (`gh pr list --state open`, 16 PRs), not matching `lane/2026-10-21-align-*`, `lane/2026-10-22-*` or `ci/2026-10-2*`, and not one of the 44 branch names in this workflow's plan; detached HEADs not at the tip of any such branch. Extra rules applied here: not named in RUN_STATE items 37 to 65 or in any magistrate record (`docs/process_traces/*magistrate*`); not named by a live script (`~/Library/LaunchAgents`, `~/.local/bin`, repo `scripts/` and `ops/`, `night-archive/forward-20261021`); and no commit dated 10-20 or 10-21 unless it is a records branch already in origin/main. A path named only in historical records (old seat briefs, copies of `docs/` inside harvests) did not block removal, since its content is the pushed commit.

| Worktree | Branch | HEAD | Pushed in |
|---|---|---|---|
| `JouleWise-wt-283-rec` | `records/2026-10-21-283e` | `d39ee0acd777998ae4aacec63e27a2fecaa90ead` | `origin/main` |
| `JouleWise-wt-4ec5d597` | `records/2026-10-20-4ec5d597` | `b97a94a3b5f35115f7e848fb18f403b90a0377d8` | `origin/main` |
| `JouleWise-wt-6cff3515` | `records/2026-10-20-6cff3515` | `bcd70a2739375a71da79b701e890b28749566619` | `origin/main` |
| `JouleWise-wt-953a3565` | `records/2026-10-20-c634f6f3` | `8bff47841eeec4711ca657478ad3548d635e53db` | `origin/records/2026-10-20-c634f6f3` |
| `JouleWise-wt-a017-rec` | `records/2026-10-21-a017` | `bb76c297902d9284fc37b62eeb2a4383f54182b2` | `origin/records/2026-10-21-a017` |
| `JouleWise-wt-a693-rec` | `records/2026-10-21-a693` | `a06bd6f9f571a29fdc2a04f5363ccc1e2d74c72b` | `origin/records/2026-10-21-a693` |
| `JouleWise-wt-af419-rec` | `records/2026-10-20-af419` | `88973bb6b3cf52ead9119cf76a672d2a04c63945` | `origin/main` |
| `JouleWise-wt-b6-adapters` | `lane/2026-10-14-b6-adapters` | `165b1972f3185d8d61928f763713bb0174561adf` | `origin/lane/2026-10-14-b6-adapters` |
| `JouleWise-wt-b6-capscreen` | `(detached)` | `b2093a8b154a328b6f74093a925d48d6eb9ade6e` | `origin/ci/2026-10-16-capture-screen` |
| `JouleWise-wt-b6-cloud` | `lane/2026-10-14-b6-cloud` | `a8b986a96b85f98802d48c59887c168460c683e1` | `origin/lane/2026-10-14-b6-cloud` |
| `JouleWise-wt-b6-cold-a` | `lane/2026-10-15-b6-cold-chain` | `2b2bea4cc25c968dc1f456e35c3c7ba676cbd76a` | `origin/lane/2026-10-15-b6-cold-chain` |
| `JouleWise-wt-b6-cold-b` | `lane/2026-10-15-b6-cold-acceptance` | `f67854d41f656191fb0368790ca364a0de2e7d15` | `origin/lane/2026-10-15-b6-cold-acceptance` |
| `JouleWise-wt-b6-cold-c` | `lane/2026-10-15-b6-cold-packroot` | `76aa4788496bc0dcfc6b0c30eb8d46d87e9f19ec` | `origin/lane/2026-10-15-b6-cold-packroot` |
| `JouleWise-wt-b6-desk` | `lane/2026-10-14-b6-desk` | `8c69dff71a2192caf4fc35f3b87cd829bc94af3f` | `origin/lane/2026-10-14-b6-desk` |
| `JouleWise-wt-b6-driver` | `lane/2026-10-14-b6-driver` | `a1b2b59c3d02b93d5022f91cec1275140162810b` | `origin/lane/2026-10-14-b6-driver` |
| `JouleWise-wt-b6-harvest` | `lane/2026-10-14-b6-harvest` | `83163e6a45fe45c0ea6407565c1ffc815e169c66` | `origin/lane/2026-10-14-b6-harvest` |
| `JouleWise-wt-b6-loop` | `lane/2026-10-14-b6-loop` | `7bd443286e28e98d2b49e7a1267487c08f9efecb` | `origin/lane/2026-10-14-b6-loop` |
| `JouleWise-wt-b6-mtdelta` | `fix/2026-10-17-b6-mt-delta` | `afd6d865d4e7ca4732cfe78ed6e1f5d4eba23d7d` | `origin/fix/2026-10-17-b6-mt-delta` |
| `JouleWise-wt-b6-mtfix` | `fix/2026-10-16-b6-mt-fixes` | `bc099c85be57326d96bd8c331260bc667ea63576` | `origin/fix/2026-10-16-b6-mt-fixes` |
| `JouleWise-wt-b6-precheck` | `lane/2026-10-14-b6-precheck` | `82dfb8bdc41f2e8a440e6a53df6146c4c892a1a1` | `origin/lane/2026-10-14-b6-precheck` |
| `JouleWise-wt-b6-s3fix-rev` | `fix/2026-10-15-b6-s3-review` | `9409c83b22becd760445c04d9550d0568c93b0b0` | `origin/fix/2026-10-15-b6-s3-review` |
| `JouleWise-wt-bytes` | `lane/2026-10-15-bytes-build` | `298a292a72e0ccafc8e3ad1643f570db4d00870f` | `origin/lane/2026-10-15-bytes-build` |
| `JouleWise-wt-bytes-config` | `lane/2026-10-15-bytes-config` | `ccd6ce073341bbf2477563d214cd515b0fc9cfd1` | `origin/lane/2026-10-15-bytes-config` |
| `JouleWise-wt-c5a1-rec` | `records/2026-10-21-c5a1` | `7f1aa95502a4e7abf3bd707960be3c78d7da3e97` | `origin/main` |
| `JouleWise-wt-corpus18-seal` | `seal/2026-10-09-corpus18-text` | `f6a9de46e49d47b040e3903562a0b029bbfead0c` | `origin/seal/2026-10-09-corpus18-text` |
| `JouleWise-wt-dd5-block4` | `design/2026-10-04-v5-qualification-block` | `51c37ace2e2b47e9c7466a8637d1fdae0cf3839e` | `origin/design/2026-10-04-v5-qualification-block` |
| `JouleWise-wt-gate-accept-fable` | `(detached)` | `df83732925651d6b19f8855ba18e4aa5fbc71c3c` | `origin/main` |
| `JouleWise-wt-gate-accept-opus` | `(detached)` | `df83732925651d6b19f8855ba18e4aa5fbc71c3c` | `origin/main` |
| `JouleWise-wt-gate-reg-fable` | `(detached)` | `3ef26534535840e414115b2e5cb6b2ce36ea4a03` | `origin/main` |
| `JouleWise-wt-gate-reg-opus` | `(detached)` | `3ef26534535840e414115b2e5cb6b2ce36ea4a03` | `origin/main` |
| `JouleWise-wt-harvest` | `lane/2026-10-07-harvest-lane` | `7e6158d669cbb6fb35761aee18abf363f07c5d36` | `origin/lane/2026-10-07-harvest-lane` |
| `JouleWise-wt-harvest-cap` | `lane/2026-10-09-harvest-corpus-cap` | `224a264c5faaae90cdf56118df37e773a932700b` | `origin/lane/2026-10-09-harvest-corpus-cap` |
| `JouleWise-wt-harvest-sources` | `lane/2026-10-10-harvest-screen-sources` | `0699abbb0881ce64b39c46ba07de568cc3848260` | `origin/lane/2026-10-10-harvest-screen-sources` |
| `JouleWise-wt-harvest-trigger` | `lane/2026-10-11-harvest-trigger-scope` | `b517626d8515d9d3e754afa26c1c27d0beef91b3` | `origin/lane/2026-10-11-harvest-trigger-scope` |
| `JouleWise-wt-p2-adapt` | `lane/2026-10-06-p2-adapt` | `fd35d1a8fb8294ad2e1bc5c9806effc8e5c9b012` | `origin/lane/2026-10-06-p2-adapt` |
| `JouleWise-wt-paper-b` | `paper/2026-10-07-paper-b` | `3c9d36c481abe8f3521e2a40e9cb691a2445ffae` | `origin/paper/2026-10-07-paper-b` |
| `JouleWise-wt-rec-1a1261a5` | `records/2026-10-17-magistrate-1a1261a5` | `a7617f2eccd744f80d03fa7234a70d67d3df8a89` | `origin/main` |
| `JouleWise-wt-rec-52d50d1f` | `records/2026-10-17-magistrate-52d50d1f` | `83950d564b7737496920e49245ded421b5eea968` | `origin/main` |
| `JouleWise-wt-rec-88c501e5` | `(detached)` | `2016742b0fff79b8ba7069d94413566fc395819f` | `origin/main` |
| `JouleWise-wt-rec-d34bf254` | `records/2026-10-17-magistrate-d34bf254` | `dfb5f9c6e3c43e4caab89b68b3de37374ec102f7` | `origin/main` |
| `JouleWise-wt-record` | `lane/2026-10-08-seal-record` | `ff0b3881fa0bb719c488bf68d43bbaa8d2ce495d` | `origin/lane/2026-10-08-seal-record` |
| `JouleWise-wt-reg-a` | `design/2026-10-07-r12-a` | `0dfcc2f4b87d1400ec096cd60f4eeb357fb6f5e2` | `origin/design/2026-10-07-r12-a` |
| `JouleWise-wt-reg-b` | `design/2026-10-07-r12-b` | `ecc7201302cde55697064d2f7d4b0362dd6d9e2c` | `origin/design/2026-10-07-r12-b` |
| `JouleWise-wt-reg-c` | `design/2026-10-07-r12-c` | `9a88626052fc44be75299e1808918aa3e6cd06b9` | `origin/design/2026-10-07-r12-c` |
| `JouleWise-wt-reg-d` | `design/2026-10-07-r12-d` | `b77c825ffb0348f26c2b9fa5e092e1d2b90289a3` | `origin/design/2026-10-07-r12-d` |
| `JouleWise-wt-reg-e` | `design/2026-10-07-r12-e` | `1e0fd4bc5d646e025a109a0e1f5cbd1f5366c069` | `origin/design/2026-10-07-r12-e` |
| `JouleWise-wt-threshold-note` | `docs/2026-10-12-threshold-proportion` | `ca5afed944350030f55ec5002116fb32919ee5a5` | `origin/docs/2026-10-12-threshold-proportion` |
| `JouleWise-wt-tl-deadline` | `lane/2026-10-07-tl-deadline-budgets` | `667203c0a3ce9bc843da61e8abd3e5a9d8acc65d` | `origin/lane/2026-10-07-tl-deadline-budgets` |
| `JouleWise-wt-tl-monitor` | `lane/2026-10-07-tl-monitor-cost` | `9ed1b6224237790c621bdfeae9f9bd51780f4bf5` | `origin/lane/2026-10-07-tl-monitor-cost` |
| `JouleWise-wt/b6loop-interactive` | `fix/2026-10-17-b6loop-interactive` | `1706257c4bc5db21f80050fdb218a8cfa4f937bb` | `origin/fix/2026-10-17-b6loop-interactive` |
| `JouleWise-wt/fix-g2a-root-id-double` | `fix/2026-10-03-g2a-root-id-double` | `f7114d4d94521726a671ca5285a6e12defb42918` | `origin/fix/2026-10-03-g2a-root-id-double` |
| `JouleWise-wt/records-f4db0072` | `records/2026-10-17-magistrate-f4db0072` | `e8f0b17b9ef4843813b2ae9b977174a0a88b529b` | `origin/main` |
| `JouleWise-wt/review-460-fable` | `(detached)` | `b39d7015d84ed13e95a494a507dcbe97fd7bac76` | `origin/main` |
| `JouleWise-wt/review-460-sol` | `(detached)` | `b39d7015d84ed13e95a494a507dcbe97fd7bac76` | `origin/main` |
| `JouleWise-wt/seal-ext-hprime` | `(detached)` | `3260e280834b24130c1a7b9a82dfaccd95537107` | `origin/main` |

55 removed, all with result REMOVED.

## Left in place

### Worktrees kept (40), with the reason

| Worktree | Branch | Size | Reasons |
|---|---|---|---|
| `JouleWise-wt-283-b2` | `ci/2026-10-21-bytes-h` | 0.32 GiB | open-PR-head; protected-pattern; status-ahead; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-283-h` | `lane/2026-10-21-bytes-h-session` | 0.32 GiB | plan-branch; untracked:1; magistrate-record:9; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-283-hc` | `(detached)` | 0.31 GiB | recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-283-l9ci` | `ci/2026-10-21-l9` | 0.34 GiB | open-PR-head; protected-pattern; L9-lane(blinded; L9-4-open); recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-283-l9lane` | `(detached)` | 0.34 GiB | L9-lane(blinded; L9-4-open); recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-a017-b2probe` | `(detached)` | 0.31 GiB | magistrate-record:9; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-a017-b4` | `lane/2026-10-20-b6-blinding-group` | 0.31 GiB | plan-branch; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-af419-b3` | `lane/2026-10-20-bytes-twin` | 0.31 GiB | plan-branch; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-af419-kv` | `lane/2026-10-20-bytes-manifest-kv` | 0.31 GiB | plan-branch; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-b5-records` | `records/2026-10-block5` | 0.30 GiB | magistrate-record:25; RUN_STATE-37-65 |
| `JouleWise-wt-b6-accept` | `reg/2026-10-17-b6-acceptance` | 0.30 GiB | magistrate-record:19 |
| `JouleWise-wt-b6-int` | `integration/2026-10-14-b6-stage1` | 0.31 GiB | plan-branch |
| `JouleWise-wt-b6-mt2fix` | `fix/2026-10-17-b6-mt2-fixes` | 0.30 GiB | magistrate-record:9 |
| `JouleWise-wt-b6-packs` | `lane/2026-10-17-b6-packs-registered` | 4.36 GiB | open-PR-head; plan-branch; untracked:7595; magistrate-record:2 |
| `JouleWise-wt-b6-reg` | `records/2026-10-14-b6-registration-draft` | 0.30 GiB | magistrate-record:1 |
| `JouleWise-wt-b6-round2` | `lane/2026-10-16-b6-round2` | 0.31 GiB | open-PR-head; plan-branch; magistrate-record:9 |
| `JouleWise-wt-b6-s3cold-fix` | `lane/2026-10-15-b6-s3-cold` | 0.44 GiB | untracked:22260; magistrate-record:37 |
| `JouleWise-wt-b6reg-6cff` | `docs/2026-10-20-bytes-registration` | 0.31 GiB | plan-branch; recent-10-20/21(possible-live-lane) |
| `JouleWise-wt-dd5-records` | `records/2026-10-04-desk-day-v5` | 0.29 GiB | untracked:11 |
| `JouleWise-wt-dd5-sizing` | `(detached)` | 0.28 GiB | untracked:1 |
| `JouleWise-wt-dd5-x17` | `lane/2026-10-05-b4-x17` | 0.29 GiB | dirty |
| `JouleWise-wt-difficulty` | `lane/2026-10-14-difficulty-pack` | 0.33 GiB | untracked:166 |
| `JouleWise-wt-ia-claim` | `design/2026-10-05-v5-claim-block-draft` | 0.28 GiB | live-script:1 |
| `JouleWise-wt-l9` | `lane/2026-10-07-l9-analysis` | 0.33 GiB | L9-lane(blinded; L9-4-open); RUN_STATE-37-65 |
| `JouleWise-wt-l9-check` | `(detached)` | 0.34 GiB | L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-l9-check2` | `(detached)` | 0.63 GiB | L9-lane(blinded; L9-4-open); untracked:12444 |
| `JouleWise-wt-l9-judge` | `(detached)` | 0.32 GiB | L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-l9-s1` | `lane/2026-10-12-l9-s1` | 0.32 GiB | L9-lane(blinded; L9-4-open); untracked:114 |
| `JouleWise-wt-l9-s10` | `lane/2026-10-13-l9-s10` | 0.34 GiB | never-touch:L9-director-scripts; L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-l9-s10f` | `lane/2026-10-13-l9-s10-fixture` | 0.34 GiB | never-touch:L9-director-scripts; L9-lane(blinded; L9-4-open); RUN_STATE-37-65 |
| `JouleWise-wt-l9-s2` | `lane/2026-10-12-l9-s2` | 0.31 GiB | L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-l9-s3` | `lane/2026-10-12-l9-s3` | 0.33 GiB | L9-lane(blinded; L9-4-open); RUN_STATE-37-65 |
| `JouleWise-wt-l9-s3b` | `lane/2026-10-12-l9-fixtures-c` | 0.33 GiB | L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-l9-seats` | `(detached)` | 0.30 GiB | L9-lane(blinded; L9-4-open) |
| `JouleWise-wt-paper-inv` | `paper/2026-10-07-number-inventory` | 0.30 GiB | dirty |
| `JouleWise-wt-quiet-kit` | `lane/2026-10-14-quiet-kit` | 0.30 GiB | RUN_STATE-37-65 |
| `JouleWise-wt-recompute` | `lane/2026-10-14-independent-recompute` | 0.30 GiB | plan-branch |
| `JouleWise-wt-term-sweep` | `docs/2026-10-12-term-sweep` | 0.30 GiB | status-ahead |
| `JouleWise-wt-tl-reap` | `lane/2026-10-07-tl-child-reaping` | 0.30 GiB | dirty |
| `JouleWise-wt-watchdog-b6` | `fix/2026-10-16-watchdog-b6-bindings` | 0.31 GiB | magistrate-record:18 |

Reason keys: `plan-branch` = named in this workflow's plan; `recent-10-20/21` = possibly a live lane of the last two days, kept as uncertain; `magistrate-record` / `RUN_STATE-37-65` = named there and not worth an iCloud copy of a git checkout; `untracked:N` = has untracked files (see below); `status-ahead` = `git status -sb` shows `ahead` even where the commit is in origin/main (term-sweep), kept to the letter of the rule.

### Untracked files in kept worktrees

- `JouleWise-wt-b6-s3cold-fix/.scratch-fix` (137 MiB, named in 8 records): worktree kept anyway (named in 37 magistrate-record lines), so no offload.
- `JouleWise-wt-difficulty/.scratch-refute21`, `.scratch-refute22` (23 MiB, named in 5 records): kept; the plan's DIFFICULTY item may build from this lane, and the space is small.
- `JouleWise-wt-l9-check2/.scratch-s3`, `JouleWise-wt-l9-s1/.scratch-s1`: L9 reads blinded data, which stays local; not offloaded to iCloud.
- `JouleWise-wt-dd5-records`, `JouleWise-wt-dd5-sizing`: untracked `docs/process_traces/2026-10-04-desk-day-v5/` files (briefs and a sizing note) are records, not scratch; kept.
- `JouleWise-wt-b6-packs/.scratch-packs` (open PR #502 head): never touched.

### Not touched

- Everything on the item's NEVER TOUCH list: `/Users/edr/night-bytes/h-20261021T185555Z`, block-5 harvests and `/Users/edr/night-custody/v5-*`, the July `runs_*` in the canonical checkout, `/Users/edr/night-b6/**`, every measurement checkout, `/Users/edr/jw_models` and the Hugging Face cache, `/Users/edr/code/jw-wt/**`, the session scratchpad.
- `/Users/edr/code/JouleWise-wt/seat-out-460` (2 MB, not a worktree).
- Ten worktrees that other workflows created while this item ran (`JouleWise-wt-b62-lane`, `-b62-refuter`, `-byg`, `-byg-kit`, and six under `/Users/edr/code/jw-wt/`). The survey ran before they existed and none was removed; `git worktree list` lost exactly the 55 paths in the table above.
- `/private/tmp` seat directories. The largest: `accept.5Mmq` 4.6 GiB, `mtrev.FkeQ` 1.3 GiB, `cold-fable` 1.3 GiB, `wdrev.Oo4i` 1.0 GiB, `drev2.HXHX` 0.6 GiB, six `wdrev-*` checkouts and `drv.HVOO` at 0.3 GiB each, `mtfix2.*` 0.6 GiB in all; about 11.6 GiB together. The item's rule allows removal only of pushed data or data with a verified iCloud copy, and the target was met without them, so none was classified or removed. They are the next candidates if BY-C5's P needs more room.

