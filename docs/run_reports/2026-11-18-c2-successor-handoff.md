# C1-to-C2 successor desk handoff · 2026-11-18

**Tier 0 · DRAFT / INELIGIBLE.** The [unsigned worksheet](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/c2-prearm/C2-HANDOFF-DRAFT.md)
uses the existing terminal Check, record/series ledger, packet rebuild and
native arm route. Its operational fields are blank. The lead owns
integration, receipt admission and fresh READY. The magistrate owns the
terminal Check, notice and live arm. The Air stays reserved for the
approved look rehearsal and both stages.

## Sources and duplication check

| Source | SHA and use |
|---|---|
| `audit/2026-11-10-fable` | `56f239dd25e09a39aed8cfdbea8028ebaefbab77`. RLD 20155–20172 for priority, 20457–20512 for receipt/finality, 20874–20897 for series identity, release and ownership. RLD 20535 preserves the signing and record-publication hold. |
| Issued W1 `ops/2026-11-11-w1-presign` | `b2e01464d6d4fbf2901ff4d4154df9455104a12a`. Protocol 502–505, 850–902 and 941–949 and the pinned packet, triage, series and arm code. Fixture basis is `tests/align/test_v4_next_arm_packet.py` 39–94, 142–175 and 467–505, and `tests/align/test_v4_claim_b_packet.py` 140–180, plus the named regressions below. |
| PR #844 | `188014f9589ca1e7fca779ff85ac1e6595e9f456`, merged into audit and ancestral to the base. `c1-prearm/C1-READY-DRAFT.md` uses owner-fill tables for C1-GATE rows 20–26. It covers W1 full desk and close, W1→C1 receipt/admission/Part C and W1's U4 consequence on C1's roster, then C1's own READY and install. |
| PR #826 | `1fc28324d51f8057fa6228e6e7d42b5ea331d52c` at inspection, open draft, no merge commit, absent from the issued W1 ancestry. RLD 20451 cites earlier draft `98edcc0feb0f81e5beca0938e867a87f98a9c9c9`. The ruled digest-only and four-field unpack-receipt interface is prospective. |
| Typed header schema | `f1be75b21978da69fa20506640bcb76ec53f6df2`, the schema pin cited by PR #844. |

I checked the audit tree for C2/prearm/ready/handoff worksheet paths,
searched the public design text and reports for C1-to-C2 and C2 worksheet
names, and searched PR metadata on audit for `C2` titles and repository-wide
for `successor handoff` and `C1-to-C2` titles. These searches found no
existing C2-specific worksheet or authorization pointer. The issued R17
runbook already covers the generic predecessor record and desk workflow.
The C2 worksheet references it and supplies the C1 terminal-to-C2 owner
fills. [PR #844](https://github.com/mpmdw/JouleWise/pull/844) ·
[Issued R17 runbook](https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md#L130-L186) ·
[PR #826](https://github.com/mpmdw/JouleWise/pull/826)

## Invented packet cases

The driver used the pinned `Scenario` helper, Git commits inside temporary
fixture repositories, an in-memory rebuild, the triage consumer and the real
record, series and held-window predicates. The manifest came from the pinned
public `candidate()` design. Arm-only inputs were fixture booleans. Each
PASS below means the observed classification matched the assertion.

| Fixture | Observed classification | Regression |
|---|---|---|
| W1 final → C1 captured and provisional, unchanged bytes | C2 series binding and packet triage PASS. `continue`, C1 `provisional`, desk `deferred`, held-window check defers only C1. | PASS |
| Same C1 with a bound file's bytes changed and desk still running | REFUSE. Desk required, `full_desk_gate` and `member_eligibility` fail. Basis `full desk must complete and pass after W1 or a code/config change`. | PASS |
| Old C1 packet after canonical ledger advances to C2 | Canonical rebuild still matches. `_record_bound` is false and triage REFUSEs `record_committed` as stale. | PASS |
| C1 still lacks final sources at C3 arm | REFUSE. `R17: final eligibility of C1` reports `no final sources`. | PASS |
| Final C1 exclusion with `precheck.certain_exclusion`, no ruling | Packet triage PASS, arm hold REFUSE. `held_window: C1: precheck.certain_exclusion: no signed ruling`. | PASS |
| First final zero-capture C1 | `continue`, zero counted windows. Series binding accepts the C1 slot for `C1#2` and refuses C2 with `triage packet does not bind the frozen series/window`. | PASS |
| `C1#2` also final and zero-capture | C1 is barred, a calibration replacement is owed after primaries, and C2 binding and packet triage PASS. | PASS |

## Reproduction

From the assigned worktree, extract only Python source from the issued pin.
The packet fixture imports a watchdog test helper. Its import expects a
retired v1 JSON fixture. The initial source-only import stopped there. The
commands supply invented schema-only JSON for that import, whose retired
parser branch these tests never exercise. The delivered rehearsal plan was
outside this test's inputs. Python was 3.13.18.

```bash
seat="$(git rev-parse --absolute-git-dir)/c2-successor-seat"
mkdir -p "$seat/issued-w1/tests/fixtures" "$seat/tmp"
python3.13 -B - "$seat/issued-w1" <<'PY'
from pathlib import Path
import subprocess, sys, tarfile
rev = 'b2e01464d6d4fbf2901ff4d4154df9455104a12a'
paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', rev,
                                 '--', 'joulewise', 'scripts', 'tests'], text=True).splitlines()
with subprocess.Popen(['git', 'archive', rev, '--', *[p for p in paths if p.endswith('.py')]],
                      stdout=subprocess.PIPE) as git:
    with tarfile.open(fileobj=git.stdout, mode='r|') as archive:
        archive.extractall(Path(sys.argv[1]), filter='data')
    if git.wait():
        raise SystemExit('could not extract issued Python source')
PY
printf '%s\n' '{"schema":"joulewise.night_plan.v1"}' \
  > "$seat/issued-w1/tests/fixtures/night_plan_v1_retired.json"
(
  cd "$seat/issued-w1"
  TMPDIR="$seat/tmp" python3.13 -B -m unittest -q \
    tests.align.test_v4_next_arm_packet.PacketTests \
    tests.align.test_v4_next_arm_packet.HistoryChainTests \
    tests.align.test_v4_next_arm_packet.DeskDerivationTests \
    tests.align.test_v4_next_arm_packet.R17ProvisionalTests \
    tests.align.test_v4_next_arm_packet.R17ReviewFinalityTests \
    tests.align.test_v4_claim_b_packet.ClaimBPacketTests
)
```

Run the case driver from the issued-source directory with
`TMPDIR="$seat/tmp" python3.13 -B -` and this script as stdin.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from joulewise.align.apple import v4_cadence as cadence, v4_registration as registration
from scripts import align_v4_series as series, align_v4_session as session
from tests.align.test_v4_next_arm_packet import CODE_PATH, INTERNAL, NOW, Scenario, builder


def setup(root):
    path = Path(root) / series.MANIFEST
    path.parent.mkdir(parents=True)
    path.write_bytes(series.raw_json(series.candidate()))
    return Scenario(root, 'W1').finish()


def step(previous, window, target, *, held=False, **kwargs):
    attempt = Scenario(previous.root, window, previous=previous, **kwargs)
    attempt.next_plan['window'] = target
    if held:
        attempt.sources['exclusions']['reasons'] = ['precheck.certain_exclusion']
    return attempt.finish()


def read(attempt, packet):
    current = registration.artifact_set_digest(attempt.root)
    built, equal = builder.rebuild_and_compare(attempt.root, packet, now_epoch_s=NOW,
                                               current_artifact_set_sha256=current)
    assert equal
    triage = cadence.next_arm_triage(built, INTERNAL, {
        'artifact_set_sha256': current, 'record_commit_exists': True,
        'record_bound': session._record_bound(attempt.root, built),
    }, now_epoch_s=NOW)
    return triage, session.held_window_check(attempt.root, built)


with TemporaryDirectory() as root:
    c1 = step(setup(root), 'C1', 'C2', provisional=True)
    clean = c1.build()
    assert series.bind_packet(c1.root, 'C2', clean, authenticated_by_rebuild=True)
    triage, hold = read(c1, clean)
    assert triage['admitted'] and hold['ok'] and hold['deferred'] == ['C1']
    assert clean['checks']['full_desk_gate']['status'] == 'deferred'
    assert clean['calibration_windows'][0]['status'] == 'provisional'
    print('unchanged: C2 / continue / provisional / desk deferred / triage PASS')

    c1.write(CODE_PATH, b'synthetic-code-v2\n')
    changed = c1.build()
    triage, _ = read(c1, changed)
    desk = changed['checks']['full_desk_gate']
    assert not triage['admitted'] and triage['full_desk_required'] and desk['status'] == 'fail'
    assert changed['checks']['member_eligibility']['status'] == 'fail'
    print('changed: REFUSE /', desk['basis'])
    c1.write(CODE_PATH, b'synthetic-code-v1\n')

    c2 = step(c1, 'C2', 'C3')
    triage, _ = read(c2, clean)
    assert not triage['admitted'] and triage['derived']['record_bound'] is False
    print('stale: rebuild matches / REFUSE /', triage['checks']['record_committed']['basis'].split(':')[0])
    late = c2.build()
    triage, _ = read(c2, late)
    assert not triage['admitted'] and 'R17: final eligibility of C1' in late['calibration_error']
    print('late: C3 REFUSE /', late['calibration_error'])

with TemporaryDirectory() as root:
    held = step(setup(root), 'C1', 'C2', held=True)
    triage, hold = read(held, held.build())
    assert triage['admitted'] and not hold['ok'] and 'no signed ruling' in hold['reasons'][0]
    print('held: C2 packet triage PASS / arm hold REFUSE /', hold['reasons'][0])

with TemporaryDirectory() as root:
    c1 = step(setup(root), 'C1', 'C1#2', captured=False, provisional=True)
    retry = c1.build()
    triage, hold = read(c1, retry)
    assert triage['admitted'] and hold['ok'] and triage['calibration']['attempted'] == 0
    assert series.calibration_rows(series.candidate(), retry['series_history'])[1] == 'C1'
    assert series.bind_packet(c1.root, 'C1', retry, authenticated_by_rebuild=True)
    try:
        series.bind_packet(c1.root, 'C2', retry, authenticated_by_rebuild=True)
    except ValueError as error:
        assert 'does not bind the frozen series/window' in str(error)
        print('zero C1: continue / C1#2 retry / C2 REFUSE /', error)
    else:
        raise AssertionError('C2 skipped C1 retry')
    c1_retry = step(c1, 'C1#2', 'C2', captured=False, provisional=True)
    next_packet = c1_retry.build()
    triage, hold = read(c1_retry, next_packet)
    assert triage['admitted'] and hold['ok'] and triage['calibration']['barred_windows'] == ['C1#2']
    assert series.bind_packet(c1.root, 'C2', next_packet, authenticated_by_rebuild=True)
    print('zero C1#2: C1 barred / replacement owed after primaries / C2 triage PASS')
```

For the two-document diff, run from the worktree root after committing.

```bash
set -o pipefail
git diff --check 56f239dd2 HEAD
git diff --name-status 56f239dd2 HEAD
base=$(git rev-parse 56f239dd2)
git show "${base}:scripts/ci_docs_only.sh" | bash -s -- "$base" "$(git rev-parse HEAD)"
```

## Verification and remaining authority

The seven case assertions passed. The six focused test classes ran 51
tests in 774.120 s at the issued pin and passed. A document check verified 18 blank fill
rows, 46 pinned anchors, both relative links and the exact fixture script.
Hosted docs CI conclusions are tied to the final head in the draft PR. The full local suite is outside this two-document
diff's verification scope. Native restore, terminal close, receipt
verification on actual records, hardware admission, notice/veto and
installation remain operational gates for authorized owners. The captured
unpack-receipt refusal is untested at the issued pin because that predicate
is absent. The invented cases cover issued R17 finality and held-window
refusal. Successor admission remains a lead decision.

**NEEDS_SPEC** · None. The lead still needs to name and verify the
admitted operational pin and receipt/finality path before using the
worksheet on actual records. RL-163/RL-183b's hold remains in
effect while a successor is prospective. Once the pin is admitted, the next
step is the magistrate's C1 terminal Check and the lead's readback of the
applicable C1 desk and sequence branch before C2 READY.
