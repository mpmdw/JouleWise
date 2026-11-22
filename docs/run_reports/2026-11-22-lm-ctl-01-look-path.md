# lm-ctl-01 look path | 2026-11-22

The first build stopped under RL-202 §1.3 when a synthetic regression
confirmed that the pinned attribution kernel applies H to the energy
uncertainty bound. RL-202a authorized the existing propagation and settled
the priority of competing DC failures. The resumed build uses both rulings.

The clean branch `align/2026-11-22-ctl01-look-path` matched `origin/main`
at `08279e20e776bb1f248636242baaab4421a56327` (PR #853). The remote
feature ref was absent at first intake.

## Finding, commit, and regression

| Finding | Commit | Regression | Result |
| --- | --- | --- | --- |
| RL-202 §1.3. Mapping H changes `EnergyEstimate.half_width_j` in the direct trace estimate, episode total, and segment estimate. | Frozen kernel `82542232dbb7459b0320c37380925e9372afb7e8` | Fixed synthetic 10 W plateau over 1 s, sampled at 50 Hz with a −7 s RAW-to-episode offset. Vary only H from 0 to 24 ms. | Reproduction PASS. The no-joule-change condition FAILS for the uncertainty bound. |

The local regression used the v3.1 frozen-kernel loader and called the
actual `trace_energy`, `attribute_episode`, and `phase_table` functions.
The source SHA-256s for the loaded attribution and phase modules matched
`suite/audited-kernel.json`.

| H | Direct, total, and segment half-width | Central integral | Phase sum | Phase closure |
| --- | --- | --- | --- | --- |
| 0 ns | 0 J | 10 J | 10 J | Pass |
| 24,000,000 ns | 0.48 J | 10 J | 10 J | Pass |

`_Trace.energy` adds `(adjacent_peak(start) + adjacent_peak(end)) × H / 1e9`
to the bound. `phase_table` checks whether the segment bound is finite.
Both bounds in this regression are finite. [Attribution source](https://github.com/mpmdw/JouleWise/blob/82542232d/joulewise/align/attribution.py#L440) · [Phase closure source](https://github.com/mpmdw/JouleWise/blob/82542232d/joulewise/align/apple/rl176_phases.py#L115)

Both delivery checksum manifests verified, including the synthetic bundle
archive, case files, and pinned vocabulary. The manifest hashes were
`7451b002ead2ddf1edc53326dc6a4486d7c3d5af538201978aae4ef08a01c4d5`
and `05b80b078839db31ae481390824ae8d79c42494fd47516e5b0cab59b4fed5dc6`.
The vocabulary hash was
`cbbab90b76b235c0d08fd89db0a65d738c74efbed5dd57e646cd169e26437d79`.
The cumulative v3 manifest adds 20 cases and also verified. Its SHA-256 is
`a159c0de5aabc7fe274c7333f06a7394f92f770be57d23f86829c11009dbafee`.
The copy retains the 29 v1 cases, 30 v2 cases and 20 v3 cases and their
original bytes. All executed checks used synthetic inputs and public source.

## Resumed build under RL-202a

The production launcher selects the registered ctl row on the authoritative
first-parent ref and loads verified Python source. The frozen kernel and
its audited dependency bytes match the seven recorded SHA-256s. Stage 1
constructs the private certificate, inventory and roster from the two
Check commitments. Preflight repeats the closure, bindings and native time
support checks and exercises the actual hard link under the analyst UID.
The private state marker precedes the first value read and is outside the
closed three-file output inventory. The worker passes H unchanged.

| Mythos finding | Implemented disposition | Regression |
| --- | --- | --- |
| 1. Native bundle lacked joined rails and DC | Verified controller CSV and paired rail mapping, independent receipt-listed RAW streams, exact timestamp slice certification, four channels joined in memory. | `bundle_ok`, `strip`, `rails_only`, `prepared_dc_is_not_native`, `component_missing_at_source`, `wrong_span_points`, restart and RL-202a precedence cases. |
| 2. Missing launcher and verified reader | Fixed launcher, stage-1 builder, first-parent authority, inventory schema, pinned source roles, actual post-start reader. | `working_stage1_changed`, `trace_digest_substitution`, `dc_payload_digest_substitution`, `terminal_map_substitution`, `sibling_ledger_only`, `reader_disagrees_on_one_stamp`. |
| 3. Link destination untested | Probe and clean up actual same-filesystem hard links before claim. | `0555_public_dir`. |
| 4. Reservation states indistinguishable | Stable lock, durable marker, explicit spent/half-made/busy and same-claim rollback. | `spent_reservation`, `empty_half_made`, `streams_only_half_made`, `failure_after_start`, `directory_fsync_after_mkdir`. |
| 5. Instrument null refused | Source-inventoried fallback list pins legal leaves and whole-member reasons, retaining numeric siblings. | `null_in_hold`, `hold_whole_member`, `hold_unknown_reason`, `known_fallback_hold_null`, `unknown_fallback_hold_reason`. |
| 6. Layout tried at read and volatile dev identity | `validate-final` and preflight use the registered device and inode and the effective link probe. A changed binding requires lead registration. | `0555_public_dir`, `ownership_disabled`. |
| 7. Private instrument operands confused with Git | Dedicated private mapping and active public tree blob-ID exclusion. | `private_operand_tracked`. |
| 8. Deployed kernel could differ from the byte pass | Pinned source bootstrap, complete installed inventory, seven audited hashes and separate manifest-bound byte-pass receipt. | `kernel_pin_drift`, `kernel_and_manifest_changed`, installed v3.1 and `h_byte_identity`. |
| 9. Invalid leg ended the whole look | Localize the ruled numerical exceptions and preserve post-start integrity failures. | `g0_overlap_reason`, `g0_overlap_digest_after_start`. |
| 10. Bridged rail gaps unmarked | Mark archived physical-part gaps privately without changing the rail integral or DC gap bar. | `hidden_decode_gap_marks`, `dc_gap_in_recovery`. |
| 11. Zero floor representation | Keep zero floor, null units and ruled baseline precedence. | `zero_duration_and_sd`, `zero_floor_baseline_null`. |
| 12. Ownership and other checkout overlap | Check real ownership enforcement and protected ACLs, plus physical ancestry of all worktrees and Git directories. | `other_worktree`, `ownership_disabled`. |

The synthetic bundle reached the real pinned reader and both serializers.
The 141,243 private bytes and 255 public bytes matched with H = 24 ms and
H = 0 at the kernel boundary. On the paired 40 s window, both integrals
were 480 J and the bound increased by 0.576 J. This local check preceded
the end-to-end paired release. The CI paired job makes two pre-claim ext4
images and mounts both at the original path on the original loop device,
preserving the registered device and directory identities. It compares the
two actual publications.

The frozen v1 runner reached the stage-1 and independent commitment checks
locally. Its own attempt to create a synthetic `RESTRICTED` directory for
`empty_half_made` returned `EPERM`. The local end-to-end reservation cases
therefore use CI's unprivileged Linux analyst. The bound-host blind preflight
and a production registration are separate lead-owned gates.

## Draft PR and executing evidence

The initial implementation is `2580c30649a6115c142e7daa433307324905ef79` in
draft PR #951. Its body was read back against the submitted gate ledger.
The 846 installed v3.1 tests and hand-vector tests passed locally and in CI.
The isolated paired release passed the frozen `h_byte_identity` case. The
public and private files matched byte for byte. The local unprivileged probe
also passed its write, cleanup and 0555 denial checks.

CI observed the four archived mismatches below. It also caught that the
synthetic registrar used the case ID instead of the injected fault name for
`private_operand_tracked`, so it omitted the synthetic tracked blob in that
case. The follow-up corrects the registrar and also verifies the public
authority tip before importing checkout code and again before claiming.
The paired case and all fixtures retain their original bytes.

The frozen checks on `f87743177afdb0f2039defd89a1fd871d7c29830` recorded v1
29/29, v2 26/30, v3 20/20 and v3.1 846/846. The standard suite caught three
integration issues. The ctl time lexer now has a ctl-only module path so
it does not replace the registered interim lexer. The extracted input
reader has only the verified-byte functions that ctl calls. The synthetic
registrar uses the repository's Git fixture helper. [Frozen checks](https://github.com/mpmdw/JouleWise/actions/runs/45041180148) · [Standard integration checks](https://github.com/mpmdw/JouleWise/actions/runs/45041180095)

The final standard shard identified two additional compatibility checks.
The native worker now carries its authenticated reader context through the
existing `first_read` argument. The shared KM003C parser accepts verified
bytes at its existing validation site, keeping the hazard refusal inventory
and its exact count intact.

[Draft PR #951](https://github.com/mpmdw/JouleWise/pull/951) · [Initial frozen checks](https://github.com/mpmdw/JouleWise/actions/runs/45039449189)

## Prospective cumulative bundle disposition

The lead resolved the four archived v2 expected-code assertions. RL-202a
§2.4 gives `meter_absent` when no receipt-listed stream in the span is
streaming with samples. It gives `not_bracketed` when sampled streams exist
outside the leg's candidate window. A missing or wrong-code disposition
refuses fresh with `INPUT_CHANNELS`. An eligible disposition names the
exact leg, code and certificate SHA-256. [RL-202a §2](https://github.com/mpmdw/JouleWise/blob/af98a171364799372025be8e7d1609706829c6f1/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25355)

Only the archived expected code on the named legs is superseded.

| Frozen v2 case | Affected legs | Governing frozen v3 checks |
| --- | --- | --- |
| `meter_absent_fresh` | L002 | `other_streams_exist_outside_leg` establishes the code for sampled siblings outside the leg. `no_streaming_samples_fresh` establishes the fresh refusal for span-wide absence. |
| `meter_absent_disposed` | L002 | `other_streams_exist_outside_leg` accepts a matching `not_bracketed` disposition. `no_streaming_samples_disposed` accepts matching `meter_absent` dispositions. |
| `dc_only_three_hidden` | L002, L005, L008 | `correct_code_too_few_hidden_legs` refuses fresh with three hidden legs after matching dispositions. |
| `dc_four_hidden_two_levels` | L005, L012 | `correct_code_too_few_hidden_levels` refuses fresh with four hidden legs across two delivered levels. |

CI retains the raw exit code, stdout and stderr for each of the 79 cases
as workflow artifacts. For each superseded assertion it proves the first
raw failure occurs in the original certificate comparator with the correct
leg identity and code-only mismatch. It then rechecks the complete
projection against the same observations with only the expected code
changed for the affected legs. Any other failure, missing result, repeated
result or unexpected historical pass blocks the cumulative bundle gate.
The required result is v1 29/29, all 26 unaffected v2 cases, v3 20/20, and
all four exact mismatch proofs. Report it as **75/79 raw, with four
superseded assertions**. The independent installed byte pass and the
bound-host blind preflight retain their separate gates.

The targeted local replay observed exit 1 at the original v2 comparator
in each of the four named cases. It confirmed the leg identity and
`not_bracketed` code on all seven affected case rows and rechecked every
other certificate. The gate tests rejected a generic comparator message,
an incorrect identity, an incorrect code, an unrelated failure and an
unexpected historical pass. The cumulative checksum manifest verified
without a byte change to any of the three suites.
