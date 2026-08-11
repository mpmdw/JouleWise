from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest

from scripts.hydrate_d117_fixture import (
    FixtureTransportError,
    hydrate_fixture,
    load_descriptor,
)
from scripts.package_d117_fixture import (
    ARTIFACT_PATHS,
    CONTENT_COUNT,
    FIXTURE_ID,
    LOGICAL_FILE_COUNT,
    TRANSPORT_SCHEMA,
    file_sha256,
    find_zstd,
    load_census,
    package_fixture,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ROOT = REPO_ROOT / "tests" / "fixtures" / "d117_v2_production"
PRODUCTION_CENSUS = PRODUCTION_ROOT / "custody_store" / "manifest.json"
PRODUCTION_DESCRIPTOR = PRODUCTION_ROOT / "transport_descriptor.json"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _make_store(root: Path) -> tuple[Path, dict[str, bytes]]:
    store = root / "store"
    store.mkdir()
    contents = []
    files: dict[str, bytes] = {}
    for index in range(CONTENT_COUNT):
        content_id = hashlib.sha256(f"content-{index:02d}".encode()).hexdigest()
        hashes = {}
        for artifact in ARTIFACT_PATHS:
            relative = f"{content_id}/{artifact}"
            raw = f"{relative}\n".encode()
            files[relative] = raw
            hashes[artifact] = hashlib.sha256(raw).hexdigest()
        contents.append(
            {"content_id": content_id, "artifact_sha256": hashes}
        )
    contents.sort(key=lambda row: row["content_id"])
    census = {
        "schema_version": "joulewise.calibration_custody_store_manifest.v1",
        "ledger": {
            "schema_version": "joulewise.calibration_observation_ledger.v1",
            "head_sequence": 76,
            "head_digest": hashlib.sha256(b"head").hexdigest(),
        },
        "contents": contents,
    }
    census_raw = _canonical_bytes(census)
    files["manifest.json"] = census_raw
    for relative, raw in files.items():
        path = store.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return store, files


def _compress_tar(path: Path, entries: list[tuple[tarfile.TarInfo, bytes]]) -> None:
    uncompressed = io.BytesIO()
    with tarfile.open(fileobj=uncompressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for info, raw in entries:
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o644
            info.size = len(raw) if info.isreg() else 0
            archive.addfile(info, io.BytesIO(raw) if info.isreg() else None)
    result = subprocess.run(
        [find_zstd(), "-q", "-3", "-T1", "-c"],
        input=uncompressed.getvalue(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
    path.write_bytes(result.stdout)


def _regular_entries(files: dict[str, bytes]) -> list[tuple[tarfile.TarInfo, bytes]]:
    return [(tarfile.TarInfo(name), files[name]) for name in sorted(files)]


class D117FixtureTransportTests(unittest.TestCase):
    def test_packager_and_hydrator_round_trip_normalized_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store, files = _make_store(root)
            archive = root / "fixture.tar.zst"
            report_path = root / "report.json"
            report = package_fixture(store, archive, report_path)
            self.assertEqual(report["logical_file_count"], LOGICAL_FILE_COUNT)
            self.assertEqual(report["logical_bytes"], sum(map(len, files.values())))
            self.assertEqual(report["archive_sha256"], file_sha256(archive))
            self.assertEqual(json.loads(report_path.read_bytes()), report)
            second_archive = root / "fixture-second.tar.zst"
            second_report = package_fixture(
                store, second_archive, root / "report-second.json"
            )
            self.assertEqual(
                second_report["archive_sha256"], report["archive_sha256"]
            )
            self.assertEqual(second_archive.read_bytes(), archive.read_bytes())

            process = subprocess.Popen(
                [find_zstd(), "-q", "-d", "-c", str(archive)],
                stdout=subprocess.PIPE,
            )
            assert process.stdout is not None
            with tarfile.open(fileobj=process.stdout, mode="r|") as packaged:
                members = list(packaged)
            process.stdout.close()
            self.assertEqual(process.wait(), 0)
            self.assertEqual([member.name for member in members], sorted(files))
            self.assertEqual(len(members), LOGICAL_FILE_COUNT)
            for member in members:
                self.assertTrue(member.isreg())
                self.assertEqual(member.mtime, 0)
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
                self.assertEqual(member.uname, "")
                self.assertEqual(member.gname, "")
                self.assertEqual(member.mode, 0o644)

            destination = root / "hydrated"
            hydrated = hydrate_fixture(
                archive,
                destination,
                store / "manifest.json",
                str(report["archive_sha256"]),
                expected_logical_bytes=int(report["logical_bytes"]),
            )
            self.assertEqual(hydrated["logical_file_count"], LOGICAL_FILE_COUNT)
            self.assertEqual(hydrated["logical_bytes"], report["logical_bytes"])
            for relative, raw in files.items():
                self.assertEqual(
                    destination.joinpath(*relative.split("/")).read_bytes(), raw
                )

    def test_packager_refuses_ungoverned_and_unsafe_source_entries(self) -> None:
        cases = ("extra", "symlink", "root-symlink", "hardlink", "fifo")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                store, files = _make_store(root)
                source = store
                governed = sorted(name for name in files if name != "manifest.json")
                first = store.joinpath(*governed[0].split("/"))
                second = store.joinpath(*governed[1].split("/"))
                if case == "extra":
                    (store / "extra.txt").write_text("extra", encoding="utf-8")
                elif case == "symlink":
                    first.unlink()
                    first.symlink_to(second)
                elif case == "root-symlink":
                    source = root / "store-link"
                    source.symlink_to(store, target_is_directory=True)
                elif case == "hardlink":
                    first.unlink()
                    os.link(second, first)
                else:
                    os.mkfifo(store / "unexpected-fifo")
                with self.assertRaises(FixtureTransportError):
                    package_fixture(
                        source, root / "bad.tar.zst", root / "bad-report.json"
                    )

    def test_hydrator_refuses_archive_sha_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store, _files = _make_store(root)
            archive = root / "fixture.tar.zst"
            report = package_fixture(store, archive, root / "report.json")
            self.assertNotEqual(report["archive_sha256"], "0" * 64)
            with self.assertRaisesRegex(FixtureTransportError, "archive SHA mismatch"):
                hydrate_fixture(
                    archive,
                    root / "hydrated",
                    store / "manifest.json",
                    "0" * 64,
                )

    def test_hydrator_refuses_malicious_membership_and_types(self) -> None:
        cases = (
            "absolute",
            "dotdot",
            "duplicate",
            "unexpected",
            "missing",
            "symlink",
            "hardlink",
            "device",
            "socket",
            "fifo",
            "other",
            "manifest-bytes",
        )
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                store, files = _make_store(root)
                entries = _regular_entries(files)
                first_name = entries[0][0].name
                if case == "absolute":
                    entries.insert(0, (tarfile.TarInfo("/absolute"), b"x"))
                elif case == "dotdot":
                    entries.insert(0, (tarfile.TarInfo("../escape"), b"x"))
                elif case == "duplicate":
                    entries.append((tarfile.TarInfo(first_name), files[first_name]))
                elif case == "unexpected":
                    entries.append((tarfile.TarInfo("unexpected"), b"x"))
                elif case == "missing":
                    entries.pop(0)
                elif case == "manifest-bytes":
                    entries = [
                        (info, b"{}" if info.name == "manifest.json" else raw)
                        for info, raw in entries
                    ]
                else:
                    type_by_case = {
                        "symlink": tarfile.SYMTYPE,
                        "hardlink": tarfile.LNKTYPE,
                        "device": tarfile.CHRTYPE,
                        "socket": b"S",
                        "fifo": tarfile.FIFOTYPE,
                        "other": b"Z",
                    }
                    replacement = tarfile.TarInfo(first_name)
                    replacement.type = type_by_case[case]
                    if case in {"symlink", "hardlink"}:
                        replacement.linkname = "manifest.json"
                    entries[0] = (replacement, b"")
                archive = root / "malicious.tar.zst"
                _compress_tar(archive, entries)
                with self.assertRaises(FixtureTransportError):
                    hydrate_fixture(
                        archive,
                        root / "hydrated",
                        store / "manifest.json",
                        file_sha256(archive),
                    )

    def test_hydrator_refuses_destination_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store, _files = _make_store(root)
            archive = root / "fixture.tar.zst"
            report = package_fixture(store, archive, root / "report.json")
            with self.assertRaisesRegex(
                FixtureTransportError, "outside the repository"
            ):
                hydrate_fixture(
                    archive,
                    REPO_ROOT / "would-be-hydrated-fixture",
                    store / "manifest.json",
                    str(report["archive_sha256"]),
                )

    def test_transport_descriptor_has_only_governed_delivery_fields(self) -> None:
        descriptor = load_descriptor(PRODUCTION_DESCRIPTOR)
        self.assertEqual(descriptor["schema_version"], TRANSPORT_SCHEMA)
        self.assertEqual(descriptor["fixture_id"], FIXTURE_ID)
        self.assertEqual(
            descriptor["release_tag"], "fixture-d117-v2-production-v1"
        )
        self.assertEqual(
            descriptor["asset_name"],
            "d117_v2_production_custody_store.tar.zst",
        )
        self.assertEqual(descriptor["archive_format"], "tar.zst")
        self.assertEqual(descriptor["logical_file_count"], LOGICAL_FILE_COUNT)
        self.assertGreater(descriptor["logical_bytes"], 0)
        self.assertEqual(
            descriptor["custody_manifest_sha256"],
            file_sha256(PRODUCTION_CENSUS),
        )
        self.assertFalse(any("receipt" in key or "path" in key for key in descriptor))

    def test_descriptor_refuses_unknown_fields_and_bad_census_pin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            descriptor = {
                "schema_version": TRANSPORT_SCHEMA,
                "fixture_id": FIXTURE_ID,
                "release_tag": "fixture-d117-v2-production-v1",
                "asset_name": "d117_v2_production_custody_store.tar.zst",
                "archive_format": "tar.zst",
                "archive_sha256": "0" * 64,
                "logical_file_count": LOGICAL_FILE_COUNT,
                "logical_bytes": 1,
                "custody_manifest_sha256": "1" * 64,
                "receipt_path": "/not-allowed",
            }
            path = root / "descriptor.json"
            path.write_bytes(_canonical_bytes(descriptor))
            with self.assertRaisesRegex(FixtureTransportError, "fields mismatch"):
                load_descriptor(path)

            descriptor.pop("receipt_path")
            path.write_bytes(_canonical_bytes(descriptor))
            loaded = load_descriptor(path)
            self.assertNotEqual(
                loaded["custody_manifest_sha256"], file_sha256(PRODUCTION_CENSUS)
            )


if __name__ == "__main__":
    unittest.main()
