# Interim look hp-01 admission and draft verification

Worktree branch `ops/2026-11-24-look-hp01-admission` starts at `e3f2c7ae8`,
the `align/2026-11-14-look-manifest` head after PR #795 and #968. The lead's
2026-11-24 ruling keeps hp-01 on `lm-interim-01` as a stage-1-only describe
block under RL-180, including the `hp01_below_9` tripwire.

## Cold-seat findings

| Finding | Disposition |
| --- | --- |
| HIGH 1 | Admission binds the High Power grammar to `cl-hp-01`, writer `dd206025abb30fd5c07515cd4b34b3e653174810` and kit SHA-256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`. The pinned writer emits an integer mode `2`, a text marker path, typed close records and their step copies. Its spec and journal shapes share the Automatic writer's base grammar. A generated writer-shaped span exercises admission, and the negative cases cover other writers, a fabricated revision, a mismatched kit, and invalid JSON kinds. |
| MED 1 | Run [45525775863](https://github.com/mpmdw/JouleWise/actions/runs/45525775863) tested PR #793 against `align/2026-11-14-kit-v1-1`, whose merge tree carries `cl-ctl-01.draft.json`. The requested PR target at `e3f2c7ae8` lacks that file. Import the public controls draft byte-for-byte from `d29efd2da` and the public hp-01 kit byte-for-byte from `bbd34dc87`. Regenerate the table using the existing `KitTable` projection so both trees agree with the same inputs. The controls draft's zero frozen revision remains outside the admitted writer set. |
| LOW 1 | The frozen-copy fixture preserves the executable twin pin. The twin CLI fixture checks the copied bytes against that pin. The NumPy aggregate also exposed two rank-refusal tests that depended on Git metadata in the deliberately Git-free copy. Their fixture now supplies the synthetic commit alongside the mocked ledger. |
| LOW 2 | `post-no-maxima` continues to print the two private prediction-difference maxima for the authorized review under RL-184 §3.4. Custody is the access control for the stored comparison and the diagnostic output. |
| LOW 3 | An exception in the twin comparison yields `twin_agrees = not_evaluable` under RL-180. The CLI regression injects `AttributeError`, `IndexError` and `RuntimeError` and checks a successful primary report with `stage2_error = no`. |
| LOW 4 | The verifier's temporary directory is removed on normal exit and unwinds on SIGTERM. Cleanup is best effort. SIGKILL bypasses Python cleanup and can leave a `jw-look-verify-*` directory in the operating system's temporary directory. The SIGTERM regression uses invented digests in a private test directory. |

The cold input was `/Volumes/JW-EXT/scratch/mythos-795-cold-1124/FINAL-MESSAGE.md`
(SHA-256 `b4da987ca0990c60895a78e716815fc38c22ee80e3408fed770c869eb2697365`)
and `tmp/probe/probe_hp01.py` in the same seat
(SHA-256 `3df6f380b91fb417a628087878a401e5767d735c095a8adbe5bf9fb7eb38460a`).
The public `RUN_STATE.md` items 341–343 and the public kit and runner source
establish the hp-01 identity. Verification in this seat uses generated
fixtures and public repository metadata.

## Draft re-pin

Cold-seat HIGH 1 and the 2026-11-24 lead ruling authorize the draft re-pin.
`cadence_look_manifest.py pin --write` updates the three changed code
digests for `admission.py`, `admission_kits.py` and `cadence_look_run.py`,
plus the `LOOKS.json` draft row's manifest digest. These are the only
manifest and ledger value changes. The frozen corpus and its test-side
SHA-256 list remain byte-identical.

## Verification and next gate

Local tests run with `taskpolicy -c utility`, with at most two test
workers at a time. The focused admission, twin CLI and verifier run passed
52 tests. The six hp-01 and kit-table checks also pass without site packages.
The NumPy frozen-tree run exercised 482 tests and reported only the two
Git-metadata fixture failures above. After the fixture correction, all
four rank and pre-response checks passed on a Git-free frozen copy.
The full local discovery suite includes archived
measurement fixtures outside this seat's read scope. Hosted CI and
independent final-head review are draft gates. The PR ledger and the seat's
`FINAL-MESSAGE.md` record their status.
