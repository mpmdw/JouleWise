"""Descriptor-bound ctl-01 layout, link probe and single-use state."""

from contextlib import ExitStack, contextmanager
import ctypes
import errno
import fcntl
import os
from pathlib import Path
import secrets
import stat
import sys

from .controls_manifest import canonical
from .controls_print import LOOK_ID, _hex_pin
from .qualification_manifest import _decode


PUBLIC_NAME = "PUBLIC.json"
PRIVATE_NAME = "RESTRICTED"
CONTROL_NAME = "look.lock"
MARKER_NAME = "read-started"
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK


class GateRefusal(Exception):
    """A closed blind diagnostic and its launcher exit code."""

    def __init__(self, token, *, status=2, special=False):
        self.status = status
        self.notice = f"REFUSE {token}\n" if special else f"REFUSE PREFLIGHT {token}\n"
        super().__init__(self.notice)


def _identity(info):
    return info.st_dev, info.st_ino


def _entry(parent, name, flags):
    # In a case-insensitive directory a differently spelled member can open.
    # Verify the actual entry as well as walking no-follow descriptors.
    fd = os.open(name, flags, dir_fd=parent)
    try:
        matches = [value for value in os.listdir(parent) if value.casefold() == name.casefold()]
        if matches != [name]:
            raise ValueError("ambiguous input component")
        return fd
    except BaseException:
        os.close(fd)
        raise


def absolute(value):
    if type(value) is not str or not value.startswith("/") or "\\" in value:
        raise ValueError("uncanonical absolute path")
    if any(part in ("", ".", "..") for part in value.split("/")[1:]):
        raise ValueError("uncanonical absolute component")
    return Path(value)


def open_directory(path):
    path = absolute(os.fspath(path))
    fd = os.open("/", DIR_FLAGS)
    ancestry = {_identity(os.fstat(fd))}
    try:
        for name in path.parts[1:]:
            child = _entry(fd, name, DIR_FLAGS)
            os.close(fd)
            fd = child
            ancestry.add(_identity(os.fstat(fd)))
        return fd, ancestry
    except BaseException:
        os.close(fd)
        raise


@contextmanager
def open_file(path):
    fd, _ = open_directory(path.parent)
    try:
        file = _entry(fd, path.name, FILE_FLAGS)
    finally:
        os.close(fd)
    with os.fdopen(file, "rb") as stream:
        if not stat.S_ISREG(os.fstat(file).st_mode):
            raise ValueError("input is not a regular file")
        yield stream


def plain_bytes(path):
    with open_file(path) as stream:
        return stream.read()


def _libc():
    return ctypes.CDLL(None, use_errno=True)


class _DarwinStatFS(ctypes.Structure):
    # sys/mount.h, 64-bit inode ABI.
    _fields_ = [("block_size", ctypes.c_uint32), ("io_size", ctypes.c_int32),
                ("counts", ctypes.c_uint64 * 5), ("fsid", ctypes.c_int32 * 2),
                ("owner", ctypes.c_uint32), ("type", ctypes.c_uint32),
                ("flags", ctypes.c_uint32), ("subtype", ctypes.c_uint32),
                ("type_name", ctypes.c_char * 16), ("mount_name", ctypes.c_char * 1024),
                ("source_name", ctypes.c_char * 1024), ("reserved", ctypes.c_uint32 * 8)]


def ownership_enabled(fd):
    if sys.platform == "darwin":
        libc = _libc()
        info = _DarwinStatFS()
        call = getattr(libc, "fstatfs$INODE64", None) or libc.fstatfs
        if call(fd, ctypes.byref(info)) != 0:
            raise OSError(ctypes.get_errno(), "could not verify mount ownership")
        return info.type_name in (b"apfs", b"hfs") and not info.flags & 0x00200000
    if sys.platform.startswith("linux"):
        device = os.fstat(fd).st_dev
        identifier = f"{os.major(device)}:{os.minor(device)}"
        with open("/proc/self/mountinfo", encoding="utf-8") as stream:
            types = {line.split(" - ", 1)[1].split()[0] for line in stream
                     if line.split(" ", 3)[2] == identifier}
        return bool(types) and types <= {"ext4", "xfs", "btrfs", "tmpfs", "overlay", "zfs"}
    return False


def _no_acl(fd):
    if sys.platform == "darwin":
        libc = _libc()
        libc.acl_get_fd_np.restype = ctypes.c_void_p
        acl = libc.acl_get_fd_np(fd, 0x100)
        if not acl:
            return ctypes.get_errno() == errno.ENOENT
        try:
            entry = ctypes.c_void_p()
            return libc.acl_get_entry(ctypes.c_void_p(acl), 0, ctypes.byref(entry)) == -1 and (
                ctypes.get_errno() == errno.EINVAL)
        finally:
            libc.acl_free(ctypes.c_void_p(acl))
    for name in ("system.posix_acl_access", "system.posix_acl_default"):
        try:
            os.getxattr(fd, name)
        except OSError as error:
            if error.errno != errno.ENODATA:
                return False
        else:
            return False
    return True


def require_private(fd, *, directory):
    info = os.fstat(fd)
    test = stat.S_ISDIR if directory else stat.S_ISREG
    expected_mode = 0o700 if directory else 0o600
    if (not test(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != expected_mode or not _no_acl(fd)
            or (not directory and info.st_nlink != 1)):
        raise ValueError("private mode, owner or ACL")


def require_private_root(fd):
    if os.geteuid() == 0 or not ownership_enabled(fd):
        raise ValueError("filesystem ownership is not enforced")
    require_private(fd, directory=True)


def _observation(fd, name):
    try:
        return os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return None


def _git_ancestor(path):
    return any(os.path.lexists(p / ".git") for p in (path, *path.parents))


def _outside_book(path, ancestry, roots):
    if _git_ancestor(path):
        raise ValueError("private path inside a checkout")
    identity = _identity(path.stat())
    for root, root_ancestry, root_identity in roots:
        if root_identity in ancestry or identity in root_ancestry or root.is_relative_to(path):
            raise ValueError("private path overlaps a checkout or object store")


def _book_roots(book):
    rows = book.git("worktree", "list", "--porcelain", "-z").split(b"\0")
    paths = [Path(os.fsdecode(row[len(b"worktree "):])) for row in rows if row.startswith(b"worktree ")]
    paths.extend(Path(row) for row in book.git(
        "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir", "--git-path", "objects"
    ).decode().splitlines())
    result = []
    for path in paths:
        try:
            physical = path.resolve(strict=True)
        except FileNotFoundError:
            if os.path.lexists(path):
                raise
            continue
        if physical.is_dir():
            fd, ancestry = open_directory(physical)
            try:
                result.append((physical, ancestry, _identity(os.fstat(fd))))
            finally:
                os.close(fd)
        else:
            raise ValueError("checkout or Git store is not a directory")
    return result


@contextmanager
def registered_directories(book, layout, protected_paths=()):
    with ExitStack() as stack:
        opened = []
        for role in ("private", "public"):
            pin = layout[role]
            path = absolute(pin["path"])
            fd, ancestry = open_directory(path)
            stack.callback(os.close, fd)
            identity = _identity(os.fstat(fd))
            if identity != (pin["device"], pin["inode"]):
                raise ValueError("registered directory changed")
            opened.append((fd, path, identity, ancestry))
        (private_fd, private, private_id, private_anc), (public_fd, public, public_id, public_anc) = opened
        if private_id[0] != public_id[0] or private_id in public_anc or public_id in private_anc:
            raise ValueError("invalid release root relationship")
        require_private_root(private_fd)
        roots = _book_roots(book)
        _outside_book(private, private_anc, roots)
        for path in protected_paths:
            fd, ancestry = open_directory(path)
            try:
                require_private_root(fd)
                _outside_book(path, ancestry, roots)
                if public_id in ancestry or _identity(os.fstat(fd)) in public_anc:
                    raise ValueError("protected inputs overlap public root")
            finally:
                os.close(fd)
        yield private_fd, public_fd


@contextmanager
def held_lock(private):
    fd = _entry(private, CONTROL_NAME, os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        require_private(fd, directory=False)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise GateRefusal("BUSY", special=True) from error
        if _identity(os.fstat(fd)) != _identity(_observation(private, CONTROL_NAME)):
            raise ValueError("lock inode replaced")
        yield
    finally:
        os.close(fd)


def write_exclusive(fd, name, data, mode=0o600):
    handle = os.open(name, os.O_WRONLY | os.O_NOFOLLOW | os.O_CREAT | os.O_EXCL, mode, dir_fd=fd)
    with os.fdopen(handle, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _probe(private, public):
    name = ".link-probe-" + secrets.token_hex(16)
    made_private = made_public = False
    try:
        fd = os.open(name, os.O_WRONLY | os.O_EXCL | os.O_CREAT | os.O_NOFOLLOW, 0o600, dir_fd=private)
        made_private = True
        with os.fdopen(fd, "wb") as stream:
            identity = _identity(os.fstat(stream.fileno()))
            os.fsync(stream.fileno())
        os.link(name, name, src_dir_fd=private, dst_dir_fd=public, follow_symlinks=False)
        made_public = True
        if _identity(_observation(public, name)) != identity:
            raise ValueError("probe inode mismatch")
        os.fsync(public)
    finally:
        try:
            if made_public:
                os.unlink(name, dir_fd=public)
        finally:
            if made_private:
                os.unlink(name, dir_fd=private)
            os.fsync(private)
            os.fsync(public)
    if _observation(private, name) is not None or _observation(public, name) is not None:
        raise ValueError("link probe cleanup")


def probe_link(private, public):
    try:
        _probe(private, public)
        # A child exercises the ACL inheritance and directory permissions used
        # for the actual no-replacement publication.
        child_name = ".link-probe-dir-" + secrets.token_hex(16)
        os.mkdir(child_name, 0o700, dir_fd=private)
        try:
            child = _entry(private, child_name, DIR_FLAGS)
            try:
                require_private(child, directory=True)
                _probe(child, public)
            finally:
                os.close(child)
        finally:
            os.rmdir(child_name, dir_fd=private)
            os.fsync(private)
    except (OSError, ValueError) as error:
        raise GateRefusal("PUBLIC_LINK") from error


def marker_valid(private, reservation, history):
    try:
        fd = _entry(private, MARKER_NAME, FILE_FLAGS)
        with os.fdopen(fd, "rb") as stream:
            require_private(fd, directory=False)
            raw = stream.read(8193)
        marker = _decode(raw)
        return (raw == canonical(marker)
                and marker.keys() == {"look_id", "manifest_sha256", "stage1_sha256", "device", "inode"}
                and marker["look_id"] == LOOK_ID
                and all(_hex_pin(marker[key], 64) for key in ("manifest_sha256", "stage1_sha256"))
                and any(row.get("look_id") == LOOK_ID and row.get("kind") == "stage1"
                        and all(row.get(key) == marker[key] for key in ("manifest_sha256", "stage1_sha256"))
                        for row in history)
                and reservation is not None and stat.S_ISDIR(reservation.st_mode)
                and (marker["device"], marker["inode"]) == _identity(reservation))
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def require_unspent_history(history):
    if any(row.get("look_id") == LOOK_ID and row.get("kind") in ("first_ctl_read", "published")
           for row in history):
        raise GateRefusal("SPENT", status=3, special=True)


def require_fresh(private, public, history):
    require_unspent_history(history)
    reservation = _observation(private, PRIVATE_NAME)
    if marker_valid(private, reservation, history):
        raise GateRefusal("SPENT", status=3, special=True)
    if (reservation is not None or _observation(private, MARKER_NAME) is not None
            or _observation(public, PUBLIC_NAME) is not None
            or any(row.get("look_id") == LOOK_ID and row.get("kind") == "reserved" for row in history)):
        raise GateRefusal("HALF_MADE", status=4, special=True)


def claim(private, public, public_record, redirect):
    made = False
    restricted = None
    try:
        os.mkdir(PRIVATE_NAME, 0o700, dir_fd=private)
        made = True
        os.fsync(private)
        restricted = _entry(private, PRIVATE_NAME, DIR_FLAGS)
        require_private(restricted, directory=True)
        redirect(restricted)
        device, inode = _identity(os.fstat(restricted))
        marker = {key: public_record[key] for key in ("look_id", "manifest_sha256", "stage1_sha256")}
        write_exclusive(private, MARKER_NAME, canonical(dict(marker, device=device, inode=inode)))
        os.fsync(private)
        return restricted
    except BaseException as error:
        try:
            if made and _observation(private, MARKER_NAME) is None:
                if restricted is not None:
                    for name in os.listdir(restricted):
                        if name not in ("stdout", "stderr"):
                            raise ValueError("unexpected claim setup artifact")
                        os.unlink(name, dir_fd=restricted)
                    os.fsync(restricted)
                try:
                    os.rmdir(PRIVATE_NAME, dir_fd=private)
                except FileNotFoundError:
                    pass
                made = False
                os.fsync(private)
        except (OSError, ValueError):
            pass
        finally:
            if restricted is not None:
                os.close(restricted)
        try:
            reservation = _observation(private, PRIVATE_NAME)
        except OSError:
            # If mkdir succeeded and removal is unconfirmed, keep the half-made
            # refusal until the reservation can be inspected.
            half_made = made
        else:
            half_made = reservation is not None and stat.S_ISDIR(reservation.st_mode)
        if half_made:
            raise GateRefusal("HALF_MADE", status=4, special=True) from error
        raise GateRefusal("CLAIM_SETUP") from error
