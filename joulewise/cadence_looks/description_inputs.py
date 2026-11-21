"""Check description input pins using opaque bytes and the shared Check chain."""

from contextlib import ExitStack, contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

if __package__:
    from .custody_pins import PinRefusal, PinnedCustody, load_pin_list
else:
    # The verifier runs with -I and imports neither the package nor a decoder.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from custody_pins import PinRefusal, PinnedCustody, load_pin_list


@contextmanager
def _regular_file(path):
    """Open a regular file through directory descriptors without symlink traversal."""
    if not path.is_absolute() or ".." in path.parts:
        raise PinRefusal("uncanonical input path")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    with ExitStack() as stack:
        parent = None
        for part in (path.anchor, *path.parts[1:-1]):
            parent = os.open(part, directory_flags, dir_fd=parent)
            stack.callback(os.close, parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        stack.callback(os.close, fd)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise PinRefusal("pinned input is not a regular file")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            yield stream


def pin_inventory(document):
    return {f"{span['span_id']}/{entry['path']}": entry
            for span in document["spans"] for entry in span["files"]}


def verification_record(root, document):
    pins = pin_inventory(document)
    spans = [span["span_id"] for span in document["spans"]]
    layout = PinnedCustody(document, spans, lambda span: root / span)
    passed = True
    try:
        if {child.name for child in root.iterdir()} != set(spans):
            raise PinRefusal("pinned span inventory differs")
        for span in spans:
            layout._inventory(span)
    except (OSError, PinRefusal):
        passed = False
    digests = {}
    for name, entry in pins.items():
        observed = None
        size_matches = False
        try:
            with _regular_file(root / name) as stream:
                size_matches = os.fstat(stream.fileno()).st_size == entry["size"]
                observed = hashlib.file_digest(stream, "sha256").hexdigest()
        except (OSError, PinRefusal):
            pass
        if not size_matches or observed != entry["sha256"]:
            passed = False
        digests[name] = {"pinned_sha256": entry["sha256"], "observed_sha256": observed}
    return {"status": "pass" if passed else "fail", "digests": digests}


def run_verifier(root, pins):
    with tempfile.TemporaryDirectory(prefix="description-pin-check-") as temporary:
        report = Path(temporary) / "verification.json"
        invocation = subprocess.run(
            [sys.executable, "-I", "-B", str(Path(__file__).resolve()), str(root), str(report)],
            input=pins, capture_output=True, check=False,
        )
        if (invocation.returncode, invocation.stdout, invocation.stderr) != (0, b"", b""):
            raise PinRefusal("hash-only input verification refused")
        return report.read_bytes()


class PinnedInput:
    """Serve only the exact bytes verified in the confined stage-2 process."""

    def __init__(self, path, entry):
        self.path = path
        self.entry = entry
        self._payload = None

    def open(self, mode="r", *, encoding="utf-8", newline=None):
        if self._payload is None:
            with _regular_file(self.path) as stream:
                payload = stream.read()
            if (len(payload) != self.entry["size"]
                    or hashlib.sha256(payload).hexdigest() != self.entry["sha256"]):
                raise PinRefusal("stage-2 bytes differ from their pin")
            self._payload = payload
        stream = io.BytesIO(self._payload)
        return stream if mode == "rb" else io.TextIOWrapper(stream, encoding=encoding, newline=newline)


def main():
    try:
        root = Path(sys.argv[1])
        document = load_pin_list(sys.stdin.buffer.read())
        report = verification_record(root, document)
    except (IndexError, ValueError, OSError, PinRefusal):
        report = {"status": "fail", "digests": {}}
    with Path(sys.argv[2]).open("x", encoding="utf-8") as stream:
        json.dump(report, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
