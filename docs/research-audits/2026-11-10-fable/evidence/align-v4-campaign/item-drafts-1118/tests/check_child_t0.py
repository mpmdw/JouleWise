"""Execute the candidate launcher and child CLIs with a synthetic handoff clock."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from unittest.mock import patch
from zoneinfo import ZoneInfo

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('kit', type=Path)
parser.add_argument('fixture', type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.source))

from scripts import cadence_legs_runner as runner, launch_cadence_span as launcher

date = '2026-11-22'
midnight = int(datetime(2026, 11, 23, tzinfo=ZoneInfo('America/Los_Angeles')).timestamp())
leg_ids = 'L007,L008,L009,L010,L011,L012'
for label, epoch, cutoff, allowed in (
    ('last authorized fractional second', midnight - 0.25, midnight, True),
    ('midnight during handoff', midnight, midnight, False),
    ('different date before numeric cutoff', midnight, midnight + 3600, False),
    ('item expires during handoff', midnight - 30, midnight - 30, False),
):
    output = args.fixture / label
    argv = [
        'launch', '--repo', str(args.source), '--python-bin', sys.executable,
        '--kit', str(args.kit), '--legs', leg_ids, '--output', str(output),
        '--disk-path', str(args.source), '--custody-root', str(args.fixture / 'synthetic-fence'),
        '--magistrate-pid', '123', '--deadline', str(epoch + 29000),
        '--authorized-t0-date', date, '--t0-before', str(cutoff),
    ]
    # The real launcher parser builds the exact runner argv serialized by launch().
    # Stub launch itself, so no LaunchAgent or process is started.
    with patch.object(launcher, 'launch') as mock_launch:
        assert launcher.main(argv) == 0
        child_argv = launcher.runner_argv(mock_launch.call_args.args[0])
    assert child_argv[-4:] == ['--authorized-t0-date', date, '--t0-before', str(cutoff)]

    deps = runner.mock_deps(output, runner.FakeClock(epoch))
    # The real child parser and run_span() execute with in-process synthetic
    # dependencies. No native host command or child process is called.
    with patch.object(runner, 'production_deps', return_value=deps):
        rc = runner.main(child_argv[2:])
    if allowed:
        assert rc == 0, (label, rc)
        receipt = json.loads((output / 'runner_receipt.json').read_text())
        assert receipt['started']['epoch_s'] == epoch
    else:
        assert rc == 3, (label, rc)
        assert not output.exists()
        assert not deps.host.calls
    print('PASS candidate child', label)
