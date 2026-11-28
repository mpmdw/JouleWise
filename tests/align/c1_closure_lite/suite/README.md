# Frozen C1 LITE acceptance suite

The tape has **94 decisions**. There are 37 filesystem decisions and 57 integration decisions. The latter cover the 25 retained regression names with their original spellings, plus linked/copy staging, the reservation’s starting digest, an external file in the arm record, and a closed stage with the wrong dispatch. Every case uses invented bytes. A mocked host entry is evidence that preflight passed in the fixture.

Run from the delivery directory with Python 3.10+ and Git. Compare the manifest’s own SHA-256 with the handoff first. Supply the candidate adapter by absolute path.

```sh
shasum -a 256 -c SUITE.sha256
python3 -B suite/run.py --fixture-check
python3 -B suite/run.py --adapter /absolute/path/to/adapter.py > /tmp/c1-lite-observed.jsonl
cmp suite/expected.jsonl /tmp/c1-lite-observed.jsonl
```

`--fixture-check` builds the physical cases, verifies the offline history bundle and checks tape structure. Candidate acceptance requires a successful adapter run. The runner serializes **actual** observations as sorted, compact UTF-8 JSON with one LF per row. It compares the complete bytes with `expected.jsonl` and writes them to stdout only on equality. Adapter diagnostics go to stderr. The oracle is comparison data for the runner. Derive results from candidate behavior and actual entry into the host stand-in.

## Adapter

Implement two module functions. Directory arguments are `pathlib.Path` objects. Each call gets fresh disposable inputs. Use the candidate’s normal parser, packet CLI, closure and admission code with synthetic fixture data and a fake host. Only the local synthetic Git history is an evidence source.

```python
def check_view(request) -> dict: ...
def exercise(work, request, edit_source) -> dict: ...
```

The supplied `lite_adapter.py` collects the decisions and counts entries independently for each call. For example, a builder adapter can use the following wiring. The fixture functions in this example invoke the candidate. Their first host stand-in calls the supplied zero-argument `entered` callback before returning its synthetic response.

```python
from lite_adapter import consumer_decisions, view_decision

def check_view(request):
    return view_decision(lambda entered: run_content_preflight(request, entered))

def exercise(work, request, edit_source):
    with prepared_case(work, request, edit_source) as fixture:
        result = consumer_decisions(fixture.install, fixture.direct_arm)
        result.update(fixture.observations())  # build, selection or arm-record fields when requested
        return result
```

**`check_view`** calls the shared production C1/C2 comparison on `request['repo']` and `request['stage']`. Read the execution `commit` and the packet at `delivery_commit:packet` from the local `git` repository. `delivery_ref` names the attempt. The checkout’s HEAD points to the earlier execution commit. Each packet has just the `c1_closure` object so the primitive can run without a full arm fixture. Return `decision` (`admit` or `refuse`) and `host` (observed checkpoint entries, zero for this primitive).

`filesystem.py` supplies the eight frozen families. Each of code, policy, head pin, derivation, dispatch, identity, live ledger and packet gets a single missing leaf, a byte change, an unlisted hidden sibling and a link to an identical file outside both roots. The `.gitignore` in R matches those extra siblings. Five controls exercise an intact copy, a linked repo leaf, an in-view linked stage directory, an executable-bit change and an escaping directory link. In the missing-stage cases the committed inventory row remains. In the missing-packet case its blob remains on the attempt ref. No candidate code creates these perturbations.

**`exercise`** runs one integration request. `request` has `fixture`, `form`, `variant` and `report_build`. Build from `work / 'history.git'`, a fresh offline copy of the frozen R1 → W1 → escalated C1 history. `history-identity.json` names its series and predecessor. Use the production fixture helpers for materialization, dispatch and CLI invocation. The reviewed entry points are `tests/align/test_v4_next_arm_packet.py:47,64,110,141,407,455,561,681,799`. Start with the genuine 24-member kit, W1 desk, an expiry of 140 and evaluation at 111. Complete any required typed arguments, nested dependencies and session inputs inside `work` before finalizing on a fixture-local named ref.

When `edit_source` is supplied, call `payloads = edit_source(source_plan_tree)` exactly once before rendering or committing the inputs. Persist the mutated source tree and place the returned exact byte payloads at their logical launch names. The tested option begins omitted, except for the required derivation operand. Map the legacy ledger name to the one physical live file in S. The policy, head pin and derivation in these spelling cases reside in R. Freeze the execution commit, prepare S, then finalize the attempt commit. Keep all fields and unrelated gates valid except the specified delta.

Run install CLI and direct `arm_checks` independently with fresh host counters. Return `cli` (actual exit), `arm` (`admit` or `refuse`), `host_cli` and `host_arm` (integers). Intercept each entry point at its first host checkpoint, before real activity. On valid input the stand-in records one entry and supplies a successful synthetic continuation. A refused CLI returns 2 and a refused arm has its native refusal result, each with zero entries. Inspect the native reason in each negative fixture so an unrelated failure cannot pass the test. `report_build` asks for the actual packet CLI exit as `build`. When build rightly refuses an incomplete fixture, also present that condition directly to both consumers via a fixture-local incomplete attempt commit. A failed build cannot stand in for those observations.

## Integration deltas

`scenarios.json` freezes the names, spellings and variants. Use these deltas in the genuine starting fixture.

| Case | Change and observation |
|---|---|
| `audit7-derivation-binding`, `audit8-bare-ledger`, `audit8-default-policy`, `default-head-pin` | `forms.py` supplies the exact template edits and file bytes. On `clean`, return the SHA-256 of the file actually selected by the staged parser/loader as `selected`. Each spelling also gets `modified` and `unbound` with an initially successful packet build. For `modified`, append one LF to the selected file before either consumer enters preflight, keeping the commit and pins fixed. For R `unbound`, remove the selected export leaf with the Git commit fixed. For S `unbound`, leave the live ledger present and omit its starting row from the packet before finalizing the named ref. Preserve every other input. |
| `audit8-bare-ledger/default` | On the clean default also exercise reservation and later ledger readers on a fresh matching fixture. Make a legitimate fixture reservation append. Return `one_live_file` from checking that the reservation and all consuming paths resolve to the same physical file and the later readers see its updated contents. A same-byte private copy fails this observation. |
| `audit8-session-kind-bracket` | Omit the flag or explicitly pass `--session-kind bracket`. Supply no file named `bracket`. Return the actual parsed scalar as `selected`. |
| `audit1-relabeled-sentinels`, `audit1-wrong-ordinals` | In a coherent ordinary 22-member projection and its ledger, relabel ordinary members 20/21, or place the four genuine sentinel IDs at the wrong positions. Exercise each separately. |
| `audit2-w1-desk-from-r1`, `audit2-ordered-legacy-projection` | Give W1 a stale artifact set and point `last_passed_record` at matching R1. The separate #844 positive omits explicit ordinals only in the ordered projection and retains the genuine materialized order. |
| `audit3-swapped-kit`, `audit4-swapped-order`, `audit5-changed-derivation` | Keep the packet for 24. Select the ordinary 22 kit, replace only stage two’s order with the 22 dispatch, or change only one reference member in the staged derivation manifest, respectively. |
| `audit6-absent-from-stage-and-selection`, `missing-ledger-and-row`, `missing-policy-and-blob` | Omit the required derivation, starting ledger or default policy before building. Omit its pin too, or the tracked blob from the execution commit for a repo input. Use a consistent tree/inventory and leave the real command requiring the missing input. Both builder and consumers must refuse. |
| `semantic-desk-and-ready-forgery`, `wrong-predecessor`, `expired-packet` | Present ready and passing desk summaries over pending committed desk evidence. Separately substitute the wrong predecessor hash. For expiry use the good packet built at 111 and present it at 141. |
| `outside-default-ancestor` | Put a recognizable prospective-v3 marker one directory above the allowed root, with an invalid reference that would spoil the otherwise valid plan if selected. A search ending at the allowed root admits the inner plan. |
| `outside-env-ledger`, `outside-config-ref`, `outside-unknown-binding`, `ambient-shade-cache` | Set the campaign reader’s `CALIBRATION_LEDGER` to an identical fixture file outside R/S with no explicit override. Separately embed an absolute outside file in a selected config, use an unknown argument binding, or select a SHADE workload whose only upstream bytes are in an outside XDG cache. Keep all files inside the disposable fixture. Use offline cache resolution. All four refuse before the host checkpoint. |
| `preflight-routing`, `same-root-direct-arm` | Change only the staged session discriminator to W1 while the handoff selects C1. Separately pass identical legacy source/view root paths containing an extra untracked file. Exercise both entry points. |
| `staging-link-and-copy`, `dispatch-roster-with-closed-stage` | Present the genuine kit via in-view links and then via equal copies. Both admit. For the separate roster refusal, prepare the wrong second-stage order and its matching inventory row while retaining the expected 24-member K2 roster. Finalize this internally closed stage on the attempt ref. Establish that C1/C2 pass; the resolved dispatch must still refuse. |
| `reservation-start-digest` | Use a valid initial ledger and matching head with a packet pin for different starting bytes. Observe both preflight refusals. Also invoke the reservation starting-digest check directly on a fresh copy of this fixture before its first append. Return `reservation` from that decision and `appended` from whether the ledger acquired a record. |
| `external-arm-record` | The driver supplies `work / 'installed/frequency-helper'` as the installed helper read by an existing host check. It is external to R/S and is never a staged operand. Use a stand-in for the host command. Exercise the real arm-record writer and return its recorded row as `external` with the absolute `path` and `sha256` of the observed helper. The driver makes the recorded path relative to `work` for the tape. `scripts/align_v4_session.py:719,733,2119`. |

The fixture author may reuse existing test setup for each delta. Preserve the frozen form, bytes, authority and decision for that row. A change to the tape or packaged fixtures requires a new freeze.
