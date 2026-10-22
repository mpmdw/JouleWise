## PROGRESS

- Done: intake/M0; clean baseline 8386706f2 (descends bda481d5a), no stop card, 66 GiB available. Read H ruling, its exact rational implementation, Fable section 3, and data-branch byte-count shapes. No real session trees accessed.
- Done: gates fix evidence: bda481d5a exits 1 with ConversionSyntax and no C5; 8386706f2 exits 2 without ConversionSyntax and writes C5 on identical H inputs. Exit-code caller census checked.
- Next: lead rules on one-raw-copy rate input (see NEEDS_RULING), then implement exact rational pass disk terms, pack encoding and replay.
- Open: NEEDS_RULING on byte source; real 9+1 replay and CI remain director-owned. No commit/push attempts (local route). Baseline tests.test_bytes_gates passes all 11 tests.

## SUMMARY

BY-C5 is stopped for the required byte-source ruling before implementation.
The baseline already contains the stopped-session fix; before/after evidence confirms it.
All 11 baseline bytes_gates tests pass.
H MEASUREMENTS retained_bytes combines raw and archive allocations, unlike disk_h's raw-only rates.
Using that field doubles the required rate maxima, violating the brief's required agreement.
Only this report changed; no production code or sealed file changed.
Data records were extracted only to /tmp; no prohibited real session path was accessed.
No measurement, arm, install, launchctl, commit or push ran.

## GATES FIX

Baseline 8386706f2 preserves the author of 66b330b15, as directed. Evidence directory: `/tmp/jwtmp-byc5-evidence.zze_7sty` (temporary, not an enduring source). Both invocations use `/opt/homebrew/bin/python3.13 -B`, identical data-branch MEASUREMENTS and native export, and the repository kit plan. The old script was extracted with `git show bda481d5a:scripts/bytes_gates.py`.

- Before: exit 1, stderr `bytes_gates: [<class 'decimal.ConversionSyntax'>]`, no output JSON.
- After (8386706f2): exit 2, empty stderr, output JSON written. Exit 2 reflects failing computed lines on the stopped session; it is not a program fault.
- Sole production caller: scripts/bytes_h_session.py desk maps 1 to unavailable, 2 to fail, 0 to pass, other codes to program_fault, and its CLI returns gates_exit unchanged. Tests invoke bytes_gates directly; scripts/bytes_mac_kit.py only documents its command. Census: `rg -n 'bytes_gates|gates_exit' --glob '!*.json' --glob '!*.csv' --glob '!*.md' --glob '!*.html' .`.

## P PER SUB-PACK

Pending.

## PACK ENCODING

Pending.

## REPLAY PROGRAM

Pending. Director owns real replay; the worker must not access night-b6, night-bytes or night-custody trees.

## END-TO-END

Pending.

## SEALED INVENTORY

Checked the sealed inventory programmatically (all keys of its files mapping):

```python
paths = sorted(json.loads(Path("configs/campaigns/v5_claim_25g83/sealed_inventory.json").read_text())["files"])
subprocess.run(["git", "diff", "--name-only", "bda481d5a", "HEAD", "--", *paths], check=True)
subprocess.run(["git", "diff", "--name-only", "HEAD", "--", *paths], check=True)
```

Both commands exited 0 with empty stdout. No block-five changes.

## TESTS RUN

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates`

Exit 0; 11 tests in 1.132 seconds; OK, no skips or environmental failures. This is baseline verification; no implementation is claimed. Whole suite excluded by the task.

## R6 DRAFT

Pending final implementation numbers.

## CI

Director creates draft PR and reads CI under the local route. No PR number supplied yet.

## DECISIONS I MADE

Applied director precedence: H ruling and committed disk_terms win over the paraphrase; B is the maximum of two summed bases, each rounded once using exact rational arithmetic. c=2; measured c is disclosure. WAIT uses stream rate for registered 7200 seconds; fixed comes unchanged from disk.fixed_retained_bytes. Local route overrides cloud setup, commits and PR operations.

## OPEN ISSUES

Byte-source ruling blocks rate derivation and P; pass encoding, replay, end-to-end tests, R6 text and director live replay/CI remain. No PR number exists for this slice. Local branch by-c5; HEAD 8386706f2; director destination lane/2026-10-22-bytes-c5-gates. Proposed commit for this slice: BY-C5: record gates fix evidence and raw-byte source ruling request.

## NEEDS_RULING

Question: which authorized input must bytes_gates use for the single-raw-copy allocated bytes needed to derive r_s and r_w, given that H MEASUREMENTS has only raw-plus-archive retained_bytes?

Evidence (data branch 8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b):

- MEASUREMENTS.json derivation.retained_bytes explicitly says: POSIX st_blocks*512 for raw and archive bundle trees, inode-deduplicated; disk usage at desk snapshot.
- Every receipt has only census_quanta, member_wall_s, outside_cpu_s, request_s, retained_bytes, stream_s and thermal_level. There is no raw-only bytes field.
- Max retained_bytes/stream_s over timed receipts = 3611077.0337654105 B/s; max retained_bytes/member_wall_s = 2571518.0905389376 B/s.
- disk_h.json raw-only allocated maxima = 1805538.5168827053 B/s and 1285759.0452694688 B/s. Both receipt-derived maxima are exactly twice these, outside the required 1e-6 relative agreement.
- scripts/disk_h.py on the data branch independently reads each raw bundle tree and uses its allocated bytes. Those per-run counts are not recorded in MEASUREMENTS. Its summary contains rates by model, not a raw-byte receipt per run.
- Current producer scripts/bytes_h_session.py measurements() explicitly sums raw and archive bundle directories; APFS-clone sharing cannot be inferred from inode deduplication. A blanket division by two is not a supplied per-run measurement rule.

Options considered:

1. Director supplies per-run raw_allocated_bytes as additional measured receipts; bytes_gates uses those for rate derivation and keeps retained_bytes for its original diagnostic. This best preserves the brief's receipts-based rate requirement; producing the receipts is director work because the real trees are prohibited and scripts/bytes_h_session.py is outside WRITE_SCOPE.
2. Authorize bytes_gates to accept the already supplied disk_h.json raw-only rate summary as explicit disk evidence, with its source disclosed, rather than deriving these rates from MEASUREMENTS runs. This permits implementation using available evidence but changes the required input contract.
3. Infer raw bytes by halving retained_bytes. Rejected without a ruling: it changes which bytes count and assumes per-run raw/archive equality absent from the supplied receipts.

Recommendation: option 1. A director-supplied measured raw_allocated_bytes receipt lets bytes_gates derive the required maxima directly; do not silently divide a multi-tree count.

Completed independent work: intake, gates fix before/after reproduction, production exit-code caller census, baseline 11-test module, sealed inventory diff, durable report. Blocked work: rate-bearing C5 implementation and dependent P outputs, encoding evidence, replay and R6 numbers. No production edit made while the number-bearing input contract is unresolved.
