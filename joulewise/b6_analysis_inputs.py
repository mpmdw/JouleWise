"""Read-only, relocated Block 6 inputs. No locator in an archive is followed.

The caller supplies custody digests in a separate run-input document. Source
bytes are checked against sources/SHA256SUMS; derived bytes against harvest's
outputs and the externally pinned acceptance. Compressed bytes additionally
match the desk record's decompressed digest *before* parsing.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess

from joulewise import desk_compress


class InputRefusal(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(x in ("..", ".") for x in p.parts):
        raise InputRefusal("input_path_invalid")
    return str(p)


class AuthenticatedInputs:
    def __init__(self, archive, pin):
        self.supplied_archive = Path(archive).absolute()
        if ".." in self.supplied_archive.parts:
            raise InputRefusal("input_path_invalid")
        if self.supplied_archive.is_symlink():
            raise InputRefusal("input_symlink")
        # Ancestors such as macOS /var and /tmp are outside the archive's
        # trust boundary. Resolve them once; never resolve a member path.
        self.archive = self.supplied_archive.resolve()
        self.expected, self.compressed = {}, {}
        self.zstd = None
        # These three digests must come from a verified custody handoff, not
        # from a sidecar generated from the copy about to be analysed.
        for name, field in (("harvest.json", "harvest_sha256"),
                            ("derived/b6-acceptance.json", "acceptance_sha256"),
                            ("sources/SHA256SUMS", "sha256sums_sha256")):
            self.add(name, pin[field])
        harvest = json.loads(self.read(self.archive / "harvest.json"))
        sums = self.read(self.archive / "sources/SHA256SUMS")
        for line in sums.decode().splitlines():
            sha, name = line.split("  ", 1)
            self.add("sources/" + relative(name), sha)
        clocks = {name for name in self.expected if name.endswith("/monitor/clock.jsonl")}
        if clocks and pin.get("clock_journal") not in clocks:
            raise InputRefusal("clock_journal_required")
        for name, sha in harvest["outputs"].items():
            self.add(relative(name), sha)
        # Extra collection products (notably the B6 flags and spans) may be
        # authenticated by their custody hashes if absent from harvest.outputs.
        for name, sha in pin.get("files", {}).items():
            self.add(relative(name), sha)
        self.record = {k: pin[k] for k in ("harvest_sha256", "acceptance_sha256", "sha256sums_sha256")}
        if pin.get("compression"):
            item = pin["compression"]
            name = relative(item["path"])
            self.add(name, item["sha256"])
            rows = self.read(self.archive / name).decode().splitlines()
            latest = {}
            for line in rows:
                row = json.loads(line)
                if row.get("event") not in ("compress", "restore"):
                    continue
                # Explicit string-prefix relocation only. Never probe the old
                # absolute path (it is often a sealed collection locator).
                original = row["path"]
                matches = []
                for old, new in item.get("relocations", {}).items():
                    if original.startswith(old.rstrip("/") + "/"):
                        matches.append(relative(new.rstrip("/") + "/" + original[len(old.rstrip("/")) + 1:]))
                if not matches and not PurePosixPath(original).is_absolute():
                    matches = [relative(original)]
                if len(matches) != 1:
                    raise InputRefusal("compression_relocation_ambiguous")
                latest[matches[0]] = row
            for name, row in latest.items():
                if row["event"] == "compress":
                    self.add(name, row["sha256"])
                    self.compressed[name] = row["sha256"]
            self.record["compression_sha256"] = item["sha256"]

    def add(self, name, sha):
        name = relative(name)
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise InputRefusal("input_digest_invalid")
        if name in self.expected and self.expected[name] != sha:
            raise InputRefusal("input_digest_conflict")
        self.expected[name] = sha

    def local(self, path):
        path = Path(path).absolute()
        root = next((root for root in (self.archive, self.supplied_archive)
                     if path.is_relative_to(root)), None)
        if root is None:
            raise InputRefusal("input_outside_archive") from None
        name = str(path.relative_to(root))
        relative(name)
        # Reject symlinks component by component, before accessing a target.
        cursor = self.archive
        if cursor.is_symlink():
            raise InputRefusal("input_symlink")
        for part in Path(name).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise InputRefusal("input_symlink")
        return name

    def binary_record(self):
        binary = shutil.which("zstd")
        if binary is None:
            raise InputRefusal("zstd_unavailable")
        try:
            version = subprocess.run([binary, "--version"], check=True, capture_output=True,
                                     text=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            raise InputRefusal("zstd_unavailable") from None
        self.zstd = {"path": binary, "version": version}
        return self.zstd

    def read(self, path):
        name = self.local(path)
        path = self.archive / name
        compressed = Path(str(path) + ".zst")
        self.local(compressed)
        if not Path(path).is_file() and compressed.is_file():
            if name not in self.compressed:
                raise InputRefusal("compression_record_missing")
            # desk_compress uses the zstd binary with stdout as its stream;
            # it never restores the archive in place.
            self.binary_record()
        elif not Path(path).is_file():
            raise FileNotFoundError(path)
        if name not in self.expected:
            raise InputRefusal("input_digest_missing")
        try:
            data = desk_compress.read_bytes(Path(path))
        except OSError:
            raise InputRefusal("input_decompression_failed") from None
        if digest(data) != self.expected[name]:
            raise InputRefusal("input_digest_mismatch")
        return data

    def verify_census(self):
        """Release re-verification: no stored decisions or hash cache."""
        for name in sorted(self.expected):
            self.read(self.archive / name)
        return {"files_verified": len(self.expected), **self.record, "zstd": self.zstd}
