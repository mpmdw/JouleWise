"""Verified-byte reader extracted from the description look's input verifier."""

from contextlib import ExitStack, contextmanager
import hashlib
import io
import os
import stat

from .custody_pins import PinRefusal


@contextmanager
def _regular_file(path):
    """Open a regular file through directory descriptors without symlink traversal."""
    if not path.is_absolute() or ".." in path.parts:
        raise PinRefusal("uncanonical input path")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    with ExitStack() as stack:
        parent = None
        for part in (path.anchor, *path.parts[1:-1]):
            child = os.open(part, directory_flags, dir_fd=parent)
            stack.callback(os.close, child)
            if parent is not None and [name for name in os.listdir(parent)
                                       if name.casefold() == part.casefold()] != [part]:
                raise PinRefusal("pinned path spelling differs")
            parent = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        stack.callback(os.close, fd)
        if [name for name in os.listdir(parent) if name.casefold() == path.name.casefold()] != [path.name]:
            raise PinRefusal("pinned filename spelling differs")
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise PinRefusal("pinned input is not a regular file")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            yield stream


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
