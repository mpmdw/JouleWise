# Bundle acceptance under RL-202a

Twenty additional launcher cases use fifteen profiles of the original 677 KiB synthetic archive. The packet has 79 named cases across three freezes. Four historical expectations need the release lead's disposition before anyone claims a cumulative pass. The source check and the installed-launcher check have different outputs. [Ruling, items 8 and 9](../../fable-rl202a.md) · [OPEN.md](../OPEN.md)

| Cases | What the candidate must demonstrate |
|---|---|
| `h_byte_identity` | Two isolated synthetic looks use the same registered bytes. All twelve actual DC maps carry the certified H in the first and zero at the kernel boundary in the second. Both output files compare byte for byte. On L002's penultimate 40 s of recovery the planted 12 W baseline gives 480 J in both. The endpoint peaks are 12 W each. At H = 24,000,000 ns the bound gains exactly 0.576 J, within 1e-12 J for floating arithmetic. Flags and coverage agree. |
| Three `boot_open` cases | Among two failed candidates, boot mismatch takes precedence over an unclosed stream. With no disposition, with a disposition for boot mismatch and with one for the lower cause, the reservation stays fresh. |
| Three `open_part` cases | An unclosed candidate outranks a same-boot partial stream. Only the matching research-lead disposition passes. The single disposed leg loses only its DC values. |
| `only_passing_stream_wins`, `same_boot_ends_inside` | A passing stream beside a boot-mismatched candidate gives `ok` and selects the passing path. One same-boot stream ending inside a leg gives `not_bracketed`. |
| Precedence and membership | An unusable anchor outranks excessive H. Excessive H outranks incomplete bracketing. A single stream can fail boot, cap and bracket. Another fails the header identity test despite missing its trailer and RAW anchor. A stream with a missing anchor stays in the candidate list. An interval touching the leg boundary also stays. On L002 the actual private certificate must list every candidate and its complete set of applicable failures, including empty sets for passing streams. |
| Sampled elsewhere, absent span and coverage | Sampled streams outside L002 give `not_bracketed`. An entire pilot span with zero streaming samples gives `meter_absent` on all three legs. Test both fresh refusal and matching disposition. Two dispositions with correct `not_bracketed` codes fail the hidden-leg / delivered-level minima in separate cases. |

`vectors.json` is the explicit oracle for stream membership, each failure set, disposition and final outcome. `bundle_cases.py` mutates only freshly unpacked synthetic copies. It writes native h/b/t monitor records, uses the same receipt member names and digests a real close would use, and updates the synthetic independent Check. All episodes still have empty trace and clock-map arrays. A raw stream with several defects carries independent evidence for each required failure. For example, the partial unclosed monitor starts inside the leg and lacks its header RAW stamp. This makes noncontainment and an unusable anchor independently observable despite the missing trailer.

## Verification

From the delivery directory, use Python 3.13 with bytecode disabled. Set `RUNNER_SRC` to public runner source matching the pinned readers, and `PUBLIC_REPO` to a local public Git object database containing the instrument source.

```sh
shasum -a 256 -c SUITE-v3.sha256
PYTHONPATH="$RUNNER_SRC" python3.13 -B suite/check_inputs.py
PYTHONPATH="$RUNNER_SRC" python3.13 -B suite-v2/check_vectors.py --repo "$PUBLIC_REPO"
PYTHONPATH="$RUNNER_SRC" python3.13 -B suite-v3/check_vectors.py
```

The last command decodes the synthetic raw files using the pinned KM003C reader, checks their names and close hashes, recomputes the candidate list and leg code on each of twelve positions in every profile, and measures the paired H interval on kernel `82542232d`. It does not invoke the launcher. For implementation acceptance use an independent driver on a disposable owner-enforcing synthetic bench, run all three suites and retain individual case results. Report the four legacy disagreements explicitly. A missing driver produces no candidate pass.

```sh
python3.13 -B suite/run_suite.py --driver "$CTL_TEST_DRIVER"
python3.13 -B suite-v2/run_cases.py --driver "$CTL_TEST_DRIVER"
python3.13 -B suite-v3/run_cases.py --driver "$CTL_TEST_DRIVER"
```

## Driver additions

The driver inherits freeze 2's `OP SOURCE BENCH FAULT` and its witnesses. The new runner reads the actual certificate, private report, public report, reservation marker and events. A bound certificate has `candidates` with one row per candidate, each carrying `stream` (receipt-relative path) and `failures` (unique codes). List order is immaterial to the comparison. The candidate must recompute it inside the actual reader from the very same verified bytes. The driver may observe real calls and inject the single paired test condition. It cannot choose the output or synthesize a certificate from the oracle.

For the paired case, `clone-fresh` creates a second isolated instance of the **pre-claim synthetic bench** at a sibling named `clone`. The two instances must see identical registered path, directory identities, manifest, ledger and stage-1 bytes. For example, clone a disposable VM at the preflight boundary and expose each guest's actual files to the comparator. The two branches have separate durable claim namespaces and both begin fresh. Never clear, roll back or reuse a spent claim. Changing the signed paths or normalizing output bytes would invalidate the comparison.

`stage2` with `observe_ruled_h` uses the real verified map unchanged. With `observe_zero_h` a **test-only, post-certificate-check** substitution replaces only DC's uncertainty at the delivery to the frozen computation. Both run the same installed worker, serialized output paths and publication code. JSON whitespace, ordering, hashes and terminal newline all participate in the comparison. Forced zero must be unreachable in the production launcher.

The independent observer writes `BENCH/kernel-observed.json` on each branch, outside the release inventory. Record the actual kernel-input `dc_mappings` by leg with method, offset_ns and uncertainty_ns. Record `interval` from L002's actual DC `trace_energy` call on [recovery end − 80 s, recovery end − 40 s], with leg_id, source, channel, start_ns, end_ns, adjacent_peak_w (two endpoints), joules, half_width_j and flags. The comparator checks the observed bound difference, central joules and actual released bytes. The normal production read still requires H to agree exactly with the committed certificate. An item 8 byte difference goes to the research lead before the byte pass.
