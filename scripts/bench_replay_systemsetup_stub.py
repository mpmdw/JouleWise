#!/usr/bin/env python3
"""Stand in for `sudo -n systemsetup -setusingnetworktime <state>` on the bench.

Never toggles anything.  It exists so the ruled daytime bench replay (cold
gate #3 ruling 10 Q7) can run the REAL ``establish_network_time_off`` and the
REAL ``restore_network_time`` -- receipt writing, exact-stdout comparison,
refusal-before-settle, the restore in the executor's ``finally`` -- without
sudo and without touching the machine's clock discipline.  Brief D2: no new
branch is added to those two functions; the bench driver rebinds the module's
documented ``SUDO``/``SYSTEMSETUP`` executable constants to this file, which
is a seam the module already declares ("A test substitutes its own
executables by rebinding these names -- PATH cannot fake an absolute path").

The interlock.  This stub prints the OFF line the chain's imported comparator
demands ONLY when ``EVIDENCE_POWER_RECORDER_REPLAY`` is set in its own
environment.  Without it -- that is, if this file were ever reached from an
armed night, or from a desk shell that had not deliberately entered the bench
-- it prints NOTHING and exits 2, which makes ``establish_network_time_off``
raise and the night refuse before any settle, recorder or capture.  One
variable gates both halves of the bench: the recorder that replays frames and
the toggle that is not a toggle.

Argv shape is checked, not assumed: the last two arguments must be
``-setusingnetworktime`` and ``on``/``off``, and ``-n`` must be present, so a
mis-rebinding that sent this stub some other command exits 2 rather than
answering as if it had run it.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.arm_readiness import EXPECTED_NETWORK_TIME_OFF_STDOUT
from scripts.sample_quiet_predicate_evidence import REPLAY_ENV

# The chain does not compare the ON stdout to anything (no ON comparator is
# ruled; the restore's verdict is the set form's exit code), but a receipt
# that says nothing is worse than one that says what happened.
ON_STDOUT = "setUsingNetworkTime: On\n"
SUBCOMMAND = "-setusingnetworktime"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not os.environ.get(REPLAY_ENV):
        # Empty stdout and a non-zero code: the exact shape of a toggle that
        # did not happen.  The chain refuses the night on it.
        print(f"{Path(__file__).name}: refused; {REPLAY_ENV} is not set, and this "
              "stub is never a network-time toggle", file=sys.stderr)
        return 2
    if len(argv) < 2 or argv[-2] != SUBCOMMAND or argv[-1] not in ("on", "off") or "-n" not in argv:
        print(f"{Path(__file__).name}: refused; unexpected argv {argv!r}", file=sys.stderr)
        return 2
    sys.stdout.write(EXPECTED_NETWORK_TIME_OFF_STDOUT if argv[-1] == "off" else ON_STDOUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
