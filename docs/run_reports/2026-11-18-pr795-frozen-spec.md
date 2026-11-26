# PR #795 frozen interim look build

The [AGENT] worktree started clean at `087ae10db2d8ae76c867281e47397fe53c936642`,
which matched PR #795 and its remote branch. Mission M0 found no active stop
card. The direct builder assignment took priority. RL-180 at `ddbb2df97`,
RL-179 F-12, and SPEC-795 govern the change in that order.

| Clause | Regression evidence |
| --- | --- |
| SPEC tests 1–2, F-12, RL-180 §1(a) | `test_interim_release.PublicSchema` tests the production writer, source bindings, non-integer tokens and 100 byte scans. `LookExecution.test_noisy_legwise_public_byte_invariance` compares all 53 perturbed reports with their original, masking only named SHA-256 values. Step 3 and twin comparison inputs in this particular invariance test come from fixture callbacks. |
| SPEC test 3, RL-180 §1(b) | `Reservation.test_failure_is_two_stderr_lines_and_one_exit_code` injects both a built-in and a dynamically named exception, checks exact stderr and exit status, and checks descriptor inheritance with a generated child. |
| SPEC test 4, RL-180 §1(c) | `Reservation` interrupts at 13 checkpoints and exercises competing callers, a different working directory and an uncommitted report. `LookExecution` checks wrong-host, missing-twin and NumPy refusals. |
| Freeze 2 and public ledger | `LookExecution.test_public_ledger_and_main_freeze_refuse_a_changed_coefficient_byte` uses a local test Git history. Only a mainline `yes` authorizes scoring. It checks that the ledger operation opens only public files and that a one-byte change refuses before scoring. |
| Retained scientific checks | Stage-1 no-energy spy, Los Angeles t0 date, rank before responses, fold-specific replay and equal-day prefix interval tests remain in the cadence suite. |
| Source census | `tests.test_single_count_discipline_census` scans the corrected U+2028 source escape. |

Every run in this worktree used generated inputs. The local filesystem
refuses creation of a directory with the canonical private basename. The
local reservation fixture checks that basename and substitutes a synthetic
basename for filesystem exercises. The hosted fixture exercises the literal
basename when the filesystem permits it.

The public branch census compared every advertised remote branch tip against
local refs and searched their reachable source history. The previous
agreement harness references an off-repo synthetic fit. It supplies no
tracked twin that reads the registered layout. The manifest stays draft and
stage 2 refuses before reservation until the independent reader and the
invocation and comparison interface are supplied.

The release uses an atomic rename from inside the reservation. Registration
must place both output roots on one filesystem. The operator must confirm
the campaign receipt host identifier matches the local hostname used by the
preflight. A hard interruption can consume an id without producing a failure
type. The research lead owns the corresponding ledger disposition and any
successor ruling. The qualification and v4 scorer entry points can use the
new mainline freeze gate when their integrations are available.

The PR body carries hosted CI and exact-head evidence. One independent Astra
audit follows the builder handoff.
