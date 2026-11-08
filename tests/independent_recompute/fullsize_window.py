"""The full-size SYNTHETIC block-5 window (committed S10 fixtures) laid out for the recompute alone.

tests/fixtures/b5_analysis/s10/<pack>/archive.tar.xz holds each synthetic window's archive with its claim and
bound runs under archive/sources/night-custody/runs_claim and runs_bound (the synthetic custody the S10 builder
archived). The recompute needs only the archive and those two run roots, so this extracts them to

    DEST/<pack>/archive      (everything except archive/sources/night-custody/)
    DEST/<pack>/claim-runs   (archive/sources/night-custody/runs_claim/)
    DEST/<pack>/bound-runs   (archive/sources/night-custody/runs_bound/)

and skips the rest of the synthetic custody (the chain's night records, hazards, lineage), which the recompute
never reads; with no meter stream the whole-machine lines are meter_absent, as on every S10 restore. No L9 code,
no Git repository and no real data: about 1.2 GB on disk, under a minute to extract.
"""
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/b5_analysis/s10"
PACKS = ("alpha", "beta", "gamma")
_CUSTODY = "archive/sources/night-custody/"
_ROOTS = {_CUSTODY + "runs_claim/": "claim-runs/", _CUSTODY + "runs_bound/": "bound-runs/"}


def available():
    return all((FIXTURES / pack / "archive.tar.xz").is_file() for pack in PACKS)


def _target(name):
    for prefix, replacement in _ROOTS.items():
        if name.startswith(prefix):
            return replacement + name[len(prefix):]
    if name.startswith(_CUSTODY) or name + "/" == _CUSTODY:
        return None
    return name


def extract(dest):
    """Extract once into DEST (reused when DEST/<pack>/.extracted exists); return the recompute's argv."""
    dest = Path(dest)
    argv = []
    for pack in PACKS:
        target = dest / pack
        marker = target / ".extracted"
        if not marker.is_file():
            target.mkdir(parents=True, exist_ok=True)
            with tarfile.open(FIXTURES / pack / "archive.tar.xz") as blob:
                for member in blob:
                    name = _target(member.name)
                    if name is None:
                        continue
                    member.name = name
                    blob.extract(member, target, filter="data")
            marker.write_text("ok\n")
        argv += ["--" + pack, str(target / "archive"),
                 "--claim-runs-" + pack, str(target / "claim-runs"),
                 "--bound-runs-" + pack, str(target / "bound-runs")]
    return argv
