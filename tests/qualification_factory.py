"""Create synthetic qualification records for reader fixtures only."""
from __future__ import annotations
import os
from pathlib import Path
from joulewise import receipt_readers as readiness
from joulewise.qualification_readers import safe_path, require, reference, attempt_record

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(readiness.render_json(value))



def create_record(path, value):
    path = safe_path(path, exists=False)
    require(path.parent.is_dir(), "output.parent_missing")
    raw = readiness.render_json(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return reference(path)


from joulewise import qualification_readers as _readers

def __getattr__(name):
    return getattr(_readers, name)

from joulewise.qualification_readers import HarvestRefusal, read
from scripts.harvest_g2a_window import archive
from scripts.harvest_window import inventory
import shutil



def archive_sources(sources, destination, *, previous=None, added=()):
    destination = Path(destination).absolute()
    if destination.exists() or any(destination == Path(p) or Path(p) in destination.parents
                                   or destination in Path(p).parents for p in sources.values()):
        raise HarvestRefusal("archive_exists_or_overlaps_source")
    original = _readers.census_sources(sources)
    if previous is not None:
        old = read(Path(previous) / "withheld/replay-locators.json")
        expected = {row["name"]: row for row in old["sources"]}
        current_names = set(sources) - set(added)
        if current_names != set(expected):
            raise HarvestRefusal("reharvest_source_census_changed")
        for name in current_names:
            if (str(sources[name]) != expected[name]["original_path"]
                    or original[name] != expected[name]["inventory"]):
                raise HarvestRefusal("reharvest_source_bytes_changed")
    destination.mkdir(parents=True)
    restricted = destination / "withheld"
    restricted.mkdir(mode=0o700)
    archived = archive(sources, restricted / "sources")
    locators = {"schema": "joulewise.v5_qualification_replay_locators.v1", "sources": [
        {"name": name, "original_path": str(path), "archived_path": str(restricted / "sources" / name),
         "inventory": archived[name]} for name, path in sorted(sources.items())]}
    write(restricted / "replay-locators.json", locators)
    public = {**locators, "sources": [
        {**row, "inventory": {path: {"sha256": item["sha256"]} for path, item in row["inventory"].items()
                              if "sha256" in item}}
        for row in locators["sources"]]}
    write(destination / "replay-locators.json", public)
    # Hash/path census is public; source bytes stay in restricted custody.
    sums = (restricted / "sources/SHA256SUMS").read_text()
    (destination / "SHA256SUMS").write_text("".join(
        f"{digest}  withheld/sources/{name}\n"
        for digest, name in (line.split("  ", 1) for line in sums.splitlines())))
    return original


def publish(destination, record):
    """Record is constructed field-by-field; never merge an evaluator document."""
    write(Path(destination) / "harvest.json", record)
    return record
