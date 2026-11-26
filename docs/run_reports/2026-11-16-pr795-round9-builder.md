# PR #795 round-9 builder, 2026-11-16

Direct user priority on align/2026-11-14-fit-interim, starting clean at
41afd6eeaf4018acaa79bc0533c439eb7b1cc885. Mission M0: no active stop card, AGENT
lane; targeted RUN_STATE, queue/manual fences, owning plan/interface, playbook and
orchestration read. User-directed repair takes priority over the stale generated
queue in this worktree. One repository writer; no delegation or consult. Synthetic
data only: no recordings, real custody, MBP connection or quiet measurement. No merge.

Authority: cold Sol FINAL-MESSAGE.md at
/Volumes/JW-EXT/scratch/sol-look-r8-gate3/FINAL-MESSAGE.md (sha256
2ee2c81c3973874bd13326392910b440795c003fd01bbe1f9b9c1897517a627f), and its linked
full report at /Volumes/JW-EXT/tmp/jw-pr795-cold.fiiyAT/repo/docs/run_reports/2026-11-16-cold-review-pr795-41afd6eea.md.
Read RL-174 from origin/audit/2026-11-10-fable, including A.1–A.7 and D.3.
#804's producer source was read from fetched commit
2e8d898df8498432bb865bf0249de09930446cda, to match its existing marker,
SHA256SUMS and top-directory archive formats. No producer bytes were changed.

## Dispositions and clause map

| Finding / ruling | Change | Evidence |
|---|---|---|
| Cold Sol LOW, fit_interim.py:1012 | Require full column rank before OLS, including structural missing singular values and zero designs. Existing 1e-10 ratio stays. | Exact reproducer: two dates, P 9963/9961, N 2, two rows/five columns/rank two. Stage 2 accepted before repair; test now requires refusal. Zero-design control also refuses. |
| RL-174 A.2 | Stage 1 counts energy-fit legs with 1 < clock-fit excess <= 2 s. Count decides nothing; 2 s bound unchanged. Pinned manifest limitation says a pass does not prove no hidden hole. | Boundary/selection test covers None, 1, just over 1, 1.5, 2 and an excluded leg in the range. |
| RL-174 A.4 | Unreadable meter stream makes rule 4 false for every type-A fit leg in the span, including no-turn legs. Stage 1 prints span ids and refers a second unreadable span to the research lead. T runtime remains unread. | Generated stream corruption, replay isolated to true booleans, no-turn control; two-span id/referral test. |
| RL-174 A.7 | Sentence covers all twelve worlds in committed evidence: 0.001–0.693, default 0.421. Dictated-text hash updated under this ruling. | Read the committed pass-rate report table, no rerun. 0.08 and mandatory GPU backstop preserved. |
| RL-174 D.3 | Optional stage-1 archive plan expands pulled/decrypted #804 archives into a fresh staging root. Exact manifest bytes hash to marker; archive hash also matches marker; every extracted file hashes to its per-file manifest. Publish only after verification. Record span id, three hashes and file count in D. | Real CLI reads a generated span available only from staging. Exactly one changed byte refuses although archive hash matches marker. Wrong manifest/archive hashes and unsafe paths refuse; existing destinations preserved. Existing time-reader .zst refusals remain. |

The staging plan is a JSON list of {span_id, archive, manifest, marker}, passed with
--stage-archives and --staging-root to custody-mode stage 1. #804's typed verified
marker and SHA256SUMS format are reused; no new offload/marker schema is introduced.
Only custody metadata is parsed; payload bytes are copied and hashed without parsing
measurement fields. Marker authenticity, provider verification and decryption are the
upstream lead handoff. This tool neither contacts the provider nor claims to perform
those steps. Raw copies need no staging and record []. Subsequent readers use the
same raw stage root or explicit --span-dir mappings. No custody source is modified.

The stage-1 schema, manifest/ledger/code pins and both interface documents include
these fields. The package remains draft. Neither estimator constants nor the pinned
Step 3 arithmetic changed.

## Verification

The exact cold rank reproducer failed before the guard (LookInputError not raised)
and passes after it. Targeted integration: 51 tests, OK, 53.229 s; log in
/Volumes/JW-EXT/scratch/sol-look-r9/targeted.log. Initial fixture/cite errors were
corrected before stable-source verification; earlier logs are retained as diagnostics.

Stable-source focused suite: **407 tests OK (2 optional skips), 1156.909 s**.
Before/after source hashes are identical. The mutation harness passed its unmodified control, then **144/144 killed,
0 survivors, 0 invalid**, 1347.607 s including the control. Source hashes stayed
identical before/after both runs. All seven new guard-deletion mutants are killed.
Each private runner
records the exact command, exit, duration and source hashes before/after. Receipts:
sol-look-r9/{focused-final,mutants-final}.{json,log}, run_verified.py.

Twin: copied retained independent v5.2 code without changing estimator arithmetic.
Root added only the ruled D count/id fields and staging=[] for the R-only twin; the
existing twin already refuses n <= p and zero columns. Root authored this wire delta;
no new independent reviewer or independent staging implementation is claimed.
Comparison keeps the established tolerances and provenance exceptions and compares
the new D fields. All eleven D/O/C/P/cross sets pass, including the ten retained
sets and a new RL-174 print set (count 3; two named unreadable spans and referral).
All CLI exits are zero. The extra set initially retained excluded legs in E; both
implementations refused. Its corrected E lists exactly D's energy-fit legs; the
refused working artifacts are preserved separately. Independent twin unit suite:
68 tests OK after refreshing only the copied snapshots for the new D fields.
The first unit invocation lacked the optional jsonschema dependency; the final
run uses the already retained external .schema_deps directory, with no installation.
Optional schema/differential suite: 9 tests OK with those same retained dependencies. The first working adapter had a transient variable-name error in
an unnecessary rank edit; that edit was removed. The mixed working attempt is
preserved at agreement-working-adapter/ and twin/agree-working-adapter/ and is not
counted. Only the fresh stable-twin comparison is final evidence. Byte staging is
verified through the repository's real CLI and behavioral mutants.

Manifest SHA-256 at the agreeing stable source:
`b972fe1e196679d4c26e97492ab3b712a4fbc816bd6ab2c278cd3ebcb5eb9368`.
Twin source SHA-256:
`6ebc135300d5b8ddba0c445c81d0f14141721c7ba3aeab77e24c78cbb07d3468`.
Exact extra-field, CLI-exit and unchanged-manifest/source checks are recorded in
sol-look-r9/agreement/verification.json.

Canonical discovery is excluded by the user's synthetic-only constraint because it
includes real-recording fixtures. No whole-repository or hardware pass is claimed.
Manifest validate/dry pin, generated-state check and git diff --check pass.
An additional synthetic staging probe reorders valid SHA256SUMS lines without
changing the marker. The real function refuses; a private in-memory deletion of
the manifest-to-marker hash guard admits those bytes. This demonstrates the
binding independently of malformed-manifest diagnostics. Script and result:
sol-look-r9/staging_manifest_probe.py and staging-manifest-probe.log. Hosted
quick and exact PR body/head receipts are recorded in PR #795 after push.

## Remaining questions and handoff

RL-174 resolves the seven carried round-6 operational/scientific questions about
clock-fit signs and bound, hidden holes, interval scope, undecodable streams and
compressed input, ruling ids for hash corrections, storage compression and Q11's
sentence. A.5 supplies a standing id only for unchanged-output hash transcription;
a replacement with changed bytes still needs its own ruling. No historical ledger
replacement was made here.

Still lead-owned: the four malformed reader-shape policy cases; the persisted
coefficient read boundary's schema/code authentication; confirmation of the
non-admitting kept-R reproduction and stable custody provenance projection. The
package's final research/cross-model admission, real-custody dry run and merge-tree
whole-suite gates remain open. This builder does not commission a new seat or rule
those questions. No merge is authorized.

Root final diff review and stable local gates are complete. Invocation commands,
output hashes and diagnostic artifacts are indexed in
[the round-9 invocation manifest](2026-11-16-pr795-round9-invocations.jsonl).
No final verification or authority decision was delegated.

Final actions: commit with the requested
coauthor trailer, push this PR branch, verify exact-head required quick, edit PR #795
from /Volumes/JW-EXT/scratch/sol-look-r9/pr-body.md and read it back byte-for-byte.
Generated queue rankings and advisor-visible state are unchanged; PROJECT_STATUS.md
and the state kernel are preserved. RUN_STATE and TASK_QUEUE carry this lane's pointer.
