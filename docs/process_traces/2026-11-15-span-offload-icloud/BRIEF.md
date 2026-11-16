You are a cold executing Sol 6.1 review seat for JouleWise PR #804. You did not build this change.

SESSION_MODE: delegated
WRITE_SCOPE: [] (no repository writes; all authored checkout/probes/report artifacts must stay under
/Volumes/JW-EXT/scratch/sol-offload-icloud/review/).

Review candidate da02b7fde on origin/ops/2026-11-15-air-independence. Fetch origin in
/Volumes/JW-EXT/jw-wt/mythos-repo, then create a detached checkout at
/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tree. Do not touch the builder's worktree. Do not commit,
push, merge, contact anyone, consult another agent, or operate any host/provider. Use
TMPDIR=/Volumes/JW-EXT/scratch/sol-offload-icloud/review/tmp and Python /opt/homebrew/bin/python3.13.

Scope: joulewise/span_offload.py, scripts/span_offload.py, tests/test_span_offload.py,
docs/ops/SPAN-OFFLOAD.md, CANONICAL.md, and consistency of the builder's bookkeeping. Review both the
whole tool and the iCloud delta from b9d688207. Read the full source/tests/runbook. Read RL-173 section A
verbatim at commit f35483d41, docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md,
heading '# RL-173'; read origin/main RUN_STATE items 347 and 350. Do not read custody or energy files.

Owner direction (2026-11-15 17:46 PST), verbatim: "use icloud, no? why would you not use icloud".
Provider iCloud Drive, no new credential. Destination is
~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-offload/<plan>/.
Required behavior:
- Ciphertext, wrapped key, manifest and descriptor copied via temporary names and atomic rename,
  without following links. Retain bytes-only handling, OPENSSL_CONF=/dev/null, single-name regular
  control files, per-plan lock, originals untouched, atomic .ok only if absent.
- Poll brctl status com.apple.CloudDocs synchronously with a deadline; parse only status text, never
  journals or CloudDocs databases. Timeout is nonzero UNVERIFIED, no .ok.
- After upload, evict, require an observed dataless placeholder, download, then compare downloaded
  sha256/size with the staged bytes. Marker includes manifest and ciphertext hashes/size and
  'icloud evict+redownload sha256 match' with times. If eviction/download cannot be done or observed,
  only .ok.unconfirmed is permitted, nonzero. Wrong bytes must never earn .ok.
- iCloud defaults and is the documented production path; tested optional rclone may remain.
  Install has no Google/rclone provisioning; maintenance line names bird, cloudd, fileproviderd.
  Runbook explicitly asks the research lead: is iCloud with evict+redownload readback the permanent
  tool under A.3? The software seat does NOT rule on that policy question or live macOS 26 qualification.

Execute the module tests using synthetic bytes only, fake brctl on PATH, real openssl:
python3.13 -B -m unittest tests.test_span_offload tests.test_docs_freshness tests.test_git_fixture_maintenance
No real brctl command, iCloud access, custody/energy/journal access or SSH anywhere. All dataless
observations in tests are explicit fakes, not hardware validation. The builder host is macOS 15.8.3;
live macOS 26 qualification is PROVISIONAL and belongs to the lead. Do not run the broad quick tier
or full suite here: the OS blinding blocks /restricted/ even in synthetic fixtures and legacy broad
suites attempt canonical custody paths. Full suite belongs in GitHub Actions.

Try to falsify marker correctness, no-link/no-hardlink handling (including ancestors), immutable retry,
status recognition/timeouts, real observed eviction requirements, failed/no-op eviction/download,
readback corruption/truncation, stage mutation, mixed confirmations and signal cleanup. Independently
probe the behavior where useful; do not just restate supplied tests. Grade by actual consequence.
A delayed/refused/unconfirmed result with no .ok is not a false success. No deliberate adversary seat
or unlimited hostile race model is requested; trusted control roots are provisioned by the lead.

Write REPORT.md in /Volumes/JW-EXT/scratch/sol-offload-icloud/review/ with commands and evidence,
numbered findings (BLOCKING, SHOULD-FIX, NOTE), suggested fixes, and explicit policy/live limitations.
End REPORT.md and your final response with exactly VERDICT: ADMIT or VERDICT: REFUSE, where any
standing BLOCKING finding means REFUSE. A missing/incomplete report is not an admitting seat.
