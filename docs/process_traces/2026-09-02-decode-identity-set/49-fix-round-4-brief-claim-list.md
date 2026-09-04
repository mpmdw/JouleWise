# Fix round 4 brief — decode-identity lineage paragraph, formulation 4 (claim list by the magistrate; prose by the seat; every behavioural clause proven by execution)

Worktree: `/Users/edr/code/JouleWise-wt-decode-id`, branch `fix/2026-09-02-decode-identity-set` (head at launch named in the launch message).
WRITE_SCOPE: [docs/contracts/identity_pin_projection.md, docs/process_traces/2026-09-02-decode-identity-set/50-sol-round-4-landing-record.md]. Anything else → NEEDS_SCOPE.

## 1. What you are doing and why
The paragraph at `docs/contracts/identity_pin_projection.md` §Analysis consumption (currently `:609-621`) and the defined-terms block above it (`:580-594`) are rewritten from the CLAIM LIST in §3. You write the prose; you do not decide what it claims. Three earlier rounds failed on this section because prose was verified by citation; this round every behavioural clause is proven by an EXECUTED probe with a counterfactual, and every term is built before use. The cold gate's corrected text (file 46 §4) is the base wording; apply the corrections in §2. Read files 46 §4 and 47 §4.2–4.3 first; the probe scripts `46a-coldF-*.py.txt` are working starting points (copy them under `$TMPDIR`, never into the checkout).

## 2. Corrections to file 46 §4 that the gate requires
- (42-B) Say "the recorded paths" (two of them are directories: the pack root and the window plan root), never "recorded files".
- Keep the tag qualifier: only a bundle whose configuration carries the `launch_lineage_required` tag is lineage-checked; an untagged bundle is never lineage-checked (prove it: probe P-tag).
- No claim that the window plan root is "created outside the runs roots" (no code enforces it).
- The consumption receipt lives in the SIBLING custody directory of the arm receipt's (`arm_readiness.consumptions/` vs `arm_readiness.receipts/`); do not say "beside".
- The text must not claim the hop list is exhaustive.
- Demote the bold marks at `:671-672` (`**launch manifest**`, `**one-use consumption record**`) to plain text with a back-reference to the block, so each definition has one home.
- Extend the contract's status clause (`:10-11`, "The implementation in `joulewise/identity_pins.py` is authoritative when this text and code differ.") so that the lineage paragraph has a tie-breaker: add that for the launch-lineage sentences of §Analysis consumption, `joulewise/arm_readiness.py` and `joulewise/analysis_engine/inputs.py` are authoritative when text and code differ.

## 3. Claim list (each claim = one proposition; the probe that falsifies it; the EXPECTED output fixed now, before you run anything)
| # | Claim (what the prose must say) | Probe | Expected (from files 46/47, executed by both seats) |
|---|---|---|---|
| C1 | The pack root is copied into the arm receipt's `pack` record when the arm is issued (`_pack_record`, stored by `generate_arm_receipt`). | call `_pack_record` on a temp pack; read `receipt["pack"]["pack_root"]` | key present, equals `str(pack_root.resolve())` |
| C2 | The consumption receipt carries no pack root of its own. | `CONSUMPTION_RECEIPT_KEYS` and a real consumed receipt's keys | no `pack_root` key |
| C3 | Only bundles whose configuration carries the `launch_lineage_required` tag are lineage-checked; untagged bundles are admitted without the lineage read. | `_read_bundle` on an untagged bundle with a broken lineage | admitted; lineage `None`; no `LaunchLineageError` |
| C4 | Lineage authentication runs at input loading, before this gate; a refused bundle never reaches the gate. | tagged bundle with a gone artifact | `LaunchLineageError` raised from `_read_bundle`; gate function not entered |
| C5–C12 | In execution order, the artifact and the code emitted when it is gone: locator beside the bundle → `launch_consumption_missing`; consumption receipt → `launch_consumption_missing`; arm receipt → `launch_consumption_invalid`; pack root (must exist and re-authenticate) → `launch_binding_mismatch`; launch manifest → `launch_consumption_invalid`; window plan root → `launch_binding_mismatch`; `window.env` / `window-chain.zsh` → `launch_consumption_invalid`; start and settle lifecycle receipts → `launch_lifecycle_incomplete`. | delete each artifact alone on a settled lineage (one run per hop) | the code listed |
| C13 | The order claim: with every later artifact also gone, the earliest gone hop's code is emitted. | cascade: delete hop k and all later | code of hop k, for each k |
| C14 | A receipt whose `.sha256` sidecar is gone refuses with the same code as the missing receipt itself. | delete the consumption receipt's sidecar; then a lifecycle receipt's sidecar | same code as C6 / C12 respectively |
| C15 | Called directly with a lineage whose pack root does not resolve, this gate refuses with `consumer_identity_set_unauthenticated`. | direct call (file 46 P5) | that code |
| C16 | Consuming an arm spends its single launch authorization; a second write of the same consumption receipt is refused. | write twice (file 46 E1) | second write refused (`readiness_record_consumed` / O_EXCL failure) |
| C17 | The window plan root is the absolute directory the launch manifest names as `window_plan_root`; `window.env` and `window-chain.zsh` must resolve directly under it. | move `window.env` out of that directory | `launch_consumption_invalid` (per C11) |
| C18 | Lifecycle receipts are `launch_start`, `launch_settle` and, when present, `launch_completion`; each names the consumption receipt and its predecessor; bundle loading requires start and settle only (`require_completion=False` at `inputs.py:_read_bundle`). | read `_read_bundle`'s call; delete completion only | admitted (no error) |
| C19 | Analysis of lineage-checked bundles runs on the filesystem that armed and launched them; relocating the lineage is a separate design decision, not a property of this gate. | (no probe: statement of limitation; cite S3 ruling (d), file 32) | — |

## 4. Landing record (file 50) — MUST contain, in this order, before any verifier sees the text
1. The diff-scoped **first-use table** built mechanically (grammar: for every noun phrase of two or more words and every backticked literal in the added/moved lines, the line of first use and the line of its definition; a definition is a bold-marked term or a parenthetical gloss on the same or preceding line; match case-insensitively with hyphen/space/plural forms equal; aliases listed as rows naming both spellings). Every row PASS or the text is fixed before you commit. Use a script (start from the blind seat's, file 42 Executed evidence, or file 46 P7) and paste the script and its output.
2. For every claim C1–C18: the command, its pasted output, and the counterfactual (the control run showing the unmutated lineage passing). A `file:line` citation is not a probe.
3. `git diff --stat` and the commit sha.
4. The statement that no file outside WRITE_SCOPE changed (`git status --short`).

## 5. Rules
Read `docs/contracts/identity_pin_projection.md` in full first. Do not touch ruling (d) content. Do not run the full test suite (the verifier and integration replay do); run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_engine_inputs tests.test_arm_readiness_lifecycle` (or the nearest existing modules; name what you ran). Commit on the branch, do not push. Do not end your turn before file 50 and the commit exist. Final message under 8192 bytes: commit sha, the first-use table verdict, the C1–C18 result table (claim → observed code → PASS/FAIL), anomalies.
