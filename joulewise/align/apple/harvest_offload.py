"""Verified raw offload of one finalized window for an off-MBP harvest (HARVEST-OFF-opus).

The MBP packs the finalized session root once (``pack``): every regular file is
read once, hashed (SHA-256) and streamed into a zstd-compressed tar; symlinks are
kept literally; any other file type refuses. The manifest records the absolute
source root, every path with its digest, size and mode, and the payload digest.

The Air restores it (``unpack``) only at the SAME absolute path, into a fresh
sibling staging directory that is renamed into place after every byte, link and
path matches the manifest exactly (no extra, missing or changed entry). The
harvest embeds absolute paths (plan, custody, archive, bundle locators), so a
same-path restore is what makes its output byte-identical to an MBP run; a
relocated restore is refused rather than silently producing different bytes.

Record binding (R17 review F1/F2 and the Sol seat-2 custody findings): ``finalized_manifest``
is written on the MBP at finalize and its digest is committed in the window record. It binds
the restore namespace, every tree entry and the finite closure of external inputs that the
tree's links point at. ``pack`` and ``unpack`` require it; the self-written transport manifest
is checked against it and is never the authority for a path, a destination or a namespace.
``pack_unbound``/``unpack_unbound`` are the separately named synthetic/legacy seams.

Nothing here reads outcome-bearing content: it moves bytes and compares digests.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tarfile
from typing import Any, BinaryIO

SCHEMA = 'joulewise.align_v4.harvest_offload.v1'
PAYLOAD = 'payload.tar.zst'
MANIFEST = 'MANIFEST.json'
CHUNK = 8 * 1024 * 1024
DEFAULT_LEVEL = 3


class OffloadRefused(ValueError):
    """The offload cannot be packed or restored without a byte mismatch."""


def zstd_path() -> str:
    return shutil.which('zstd') or '/opt/homebrew/bin/zstd'


class _HashingReader:
    def __init__(self, stream: BinaryIO):
        self.stream, self.digest, self.size = stream, hashlib.sha256(), 0

    def read(self, size: int = -1) -> bytes:
        data = self.stream.read(size)
        self.digest.update(data)
        self.size += len(data)
        return data


def _walk_error(error: OSError):
    # R17 delta D4: a directory that cannot be read refuses; it is never bound as empty.
    raise OffloadRefused(f'cannot read directory {error.filename}: {error.strerror or error}')


def _walk(root: Path):
    """Sorted, deterministic walk that never follows a symlink and refuses an unreadable directory."""
    entries = []
    for current, dirs, files in os.walk(root, followlinks=False, onerror=_walk_error):
        dirs.sort()
        here = Path(current)
        for name in sorted(dirs + files):
            path = here / name
            entries.append(path)
    return sorted(entries, key=lambda p: p.relative_to(root).as_posix())


EXTERNAL = '.external'
EXTERNAL_STAGING = '.external-staged'
# Never a session entry (Air-offload delta2, lead ruling): ``.external/`` is the transport namespace of the
# carried inputs, ``.external-staged`` where unpack stages them. finalize, pack and unpack refuse both.
RESERVED_NAMES = frozenset({EXTERNAL, EXTERNAL_STAGING})
FINALIZED_SCHEMA = 'joulewise.align_v4.finalized_manifest.v2'
FINALIZED_KEYS = frozenset({'schema', 'source_root', 'entries', 'closure'})
CLOSURE_KEYS = frozenset({'links', 'files', 'ignored', 'inputs', 'mirror', 'ignored_policy'})
# R17 review F1: the finite external-input closure. A link whose target leaves the session root is
# a dependency: it is bound either by the bytes it reaches (hashed at finalize, re-verified at pack
# and on the Air) or, for the measurement checkout, by the separately bound mirror identity. These
# bounds make the byte closure finite and are applied DURING each walk, before the offending hash.
# Anything past them refuses at finalize: it must become a declared mirror or input. Closure bytes
# are hashed in place, never copied, except the declared append-only externals (the calibration
# ledger). Model weights never fit the per-file bound.
CLOSURE_MAX_FILES = 4096
CLOSURE_MAX_DIRECTORIES = 4096
CLOSURE_MAX_BYTES = 1 << 30
CLOSURE_MAX_FILE_BYTES = 256 << 20
MAX_LINK_HOPS = 16
# R17 delta D3: Git identity does not cover ignored checkout content. Every ignored path a mirror
# link reaches is classified by this policy: covered by the interpreter identity (``identity_bound``),
# a regenerated cache never read as an input (``regenerated``), or inside a ``declared_directories``
# entry whose consumed files are exactly the declared ``inputs`` (the ledger, plus whatever the
# lead-owned native N1 census finds). Anything else is ``undeclared``: the production CLI refuses
# it; the library default binds its bytes (within the bounds) so a change on the Air refuses.
# ``declared_directory_mode`` (delta2, lead ruling 1): a declared directory is NOT an exemption. With
# ``consumed`` the caller has enumerated every file the harvest selects there and declared each as an
# input (bound by bytes); with ``bind`` (when that selection cannot be enumerated) the whole directory
# is bound by bytes and membership within the closure bounds, or finalize refuses.
DEFAULT_IGNORED_POLICY = {'identity_bound': ['.venv/'], 'regenerated': ['__pycache__', '*.pyc', '.DS_Store'],
                          'declared_directories': [], 'undeclared': 'bind', 'declared_directory_mode': 'bind'}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def manifest_sha256(manifest: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(manifest)).hexdigest()


def _tree_rows(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        if relative in RESERVED_NAMES:
            raise OffloadRefused(f'reserved name in the session root: {relative} (reserved_transport_name: '
                                 f'{EXTERNAL}/ carries the external inputs and {EXTERNAL_STAGING} stages them)')
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            rows[relative] = {'link': os.readlink(path)}
        elif stat.S_ISDIR(info.st_mode):
            rows[relative] = {'directory': True}
        elif stat.S_ISREG(info.st_mode):
            rows[relative] = {'sha256': _file_sha256(path), 'size': info.st_size}
        else:
            raise OffloadRefused(f'unsupported file type: {relative}')
    return rows


class _ClosureFiles:
    """Accumulates the closure's regular files under shared finite bounds, checked before any hash.

    ``files`` holds external link targets and declared inputs; ``ignored`` the byte-bound ignored
    checkout content (D3). ``listings`` deduplicates directory enumeration across links.
    """

    def __init__(self):
        self.files: dict[str, dict[str, Any]] = {}
        self.ignored: dict[str, dict[str, Any]] = {}
        self.listings: dict[str, list[str]] = {}
        self.trees: dict[str, list[str]] = {}       # directory entries ('.' and every subdirectory)
        self.total = 0
        self.count = 0

    def add(self, path: Path, why: str, *, into: str = 'files') -> None:
        key = str(path)
        if key in self.files or key in self.ignored:
            getattr(self, into).setdefault(key, (self.files.get(key) or self.ignored.get(key)))
            return
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            raise OffloadRefused(f'external closure reaches a further link ({why}): {path}; declare it as a mirror or input')
        if not stat.S_ISREG(info.st_mode):
            raise OffloadRefused(f'external closure entry is not a regular file ({why}): {path}')
        if info.st_size > CLOSURE_MAX_FILE_BYTES:
            raise OffloadRefused(f'external closure file over {CLOSURE_MAX_FILE_BYTES} bytes ({why}): {path}; '
                                 'large inputs (model weights) are never bound or copied; bind them by a mirror')
        self.total += info.st_size
        self.count += 1
        if self.count > CLOSURE_MAX_FILES or self.total > CLOSURE_MAX_BYTES:
            raise OffloadRefused(f'external closure is not finite within {CLOSURE_MAX_FILES} files / '
                                 f'{CLOSURE_MAX_BYTES} bytes ({why}); declare a mirror instead of traversing it')
        getattr(self, into)[key] = {'sha256': _file_sha256(path), 'size': info.st_size}


def _walk_tree(target: Path, collected: _ClosureFiles | None = None, *, why: str = '',
               into: str = 'files') -> tuple[list[str], list[str]]:
    """``(files, directories)`` below an external directory, in ONE walk; never follows a link; refuses an
    unreadable directory. ``directories`` holds ``'.'`` and every subdirectory, empty ones included.

    With ``collected`` each file is bound as the walk reaches it (bounds before its hash), and a
    directory already enumerated in this finalize is not walked again.
    """
    key = str(target)
    if collected is not None and key in collected.listings:
        return collected.listings[key], collected.trees[key]
    names, tree = [], ['.']
    for current, dirs, files in os.walk(target, followlinks=False, onerror=_walk_error):
        dirs.sort()
        here = Path(current)
        for name in dirs:
            if (here / name).is_symlink():
                raise OffloadRefused(f'external closure reaches a further link: {here / name}; declare it')
            tree.append((here / name).relative_to(target).as_posix())
            if len(tree) - 1 > CLOSURE_MAX_DIRECTORIES:
                raise OffloadRefused(f'external closure has over {CLOSURE_MAX_DIRECTORIES} directories: {target}')
        for name in sorted(files):
            if collected is not None:
                collected.add(here / name, why or str(target), into=into)
            elif len(names) + 1 > CLOSURE_MAX_FILES:
                raise OffloadRefused(f'external closure is not finite within {CLOSURE_MAX_FILES} files: {target}')
            names.append((here / name).relative_to(target).as_posix())
    names.sort()
    tree.sort()
    if collected is not None:
        collected.listings[key], collected.trees[key] = names, tree
    return names, tree


def _directory_listing(target: Path, collected: _ClosureFiles | None = None, *, why: str = '',
                       into: str = 'files') -> list[str]:
    """Regular files below an external directory (see :func:`_walk_tree`)."""
    return _walk_tree(target, collected, why=why, into=into)[0]


def _rebase(path: str, rebase) -> str:
    """On the Air, a hop into the restore namespace (not yet published) is resolved in the staged tree."""
    if rebase is None:
        return path
    namespace, staging = rebase
    parent = Path(os.path.realpath(os.path.dirname(path)))
    if _under(parent, namespace):
        return str(staging / parent.relative_to(namespace) / os.path.basename(path))
    return path


def _link_chain(path: Path, session_reals, rebase=None) -> tuple[list[str], str, bool]:
    """Follow a link hop by hop as the kernel does (D2, delta2).

    Each hop is joined to its link's directory WITHOUT lexical normalization, and inspected with
    lstat, so ``..`` after a symlinked parent selects what the OS opens. Returns the hop texts, the
    end path and whether any intermediate link lies outside the session (an external hop).
    """
    hops, current, external = [], str(path), False
    while True:
        text = os.readlink(current)
        hops.append(text)
        following = _rebase(os.path.join(os.path.dirname(current), text), rebase)
        try:
            is_link = stat.S_ISLNK(os.lstat(following).st_mode)
        except FileNotFoundError:
            is_link = False
        except OSError as exc:
            raise OffloadRefused(f'cannot inspect link target {following}: {exc}') from None
        if not is_link:
            return hops, following, external
        location = Path(os.path.realpath(os.path.dirname(following))) / os.path.basename(following)
        if not any(_under(location, root) for root in session_reals):
            external = True
        if len(hops) >= MAX_LINK_HOPS:
            raise OffloadRefused(f'link chain longer than {MAX_LINK_HOPS} hops: {path}')
        current = following


def _classify_link(path: Path, root_real: Path, mirror_real: Path | None, session_reals=None, rebase=None):
    """``(class, real target, hops)``: internal, mirror, session, absent or bytes.

    The hop chain is classified BEFORE the end is resolved (delta2, lead ruling 2): a chain with an
    external hop is external even when it ends back inside the session (class ``session``).
    """
    session_reals = (root_real,) if session_reals is None else session_reals
    hops, end, external_hop = _link_chain(path, session_reals, rebase)
    target = Path(os.path.realpath(end))
    if rebase is not None and _under(target, rebase[1]):
        # Report a target in the staged tree under the namespace it is published at (as at finalize).
        target = rebase[0] / target.relative_to(rebase[1])
    inside = any(_under(target, root) for root in session_reals)
    if inside and not external_hop:
        return 'internal', None, None
    if mirror_real is not None and _under(target, mirror_real):
        return 'mirror', target, hops
    if inside:
        return 'session', target, hops
    return ('absent' if not os.path.lexists(target) else 'bytes'), target, hops


def _has_dotdot(text) -> bool:
    return '..' in Path(os.fspath(text)).parts


def _policy_match(entry: str, patterns) -> bool:
    parts = [p for p in entry.rstrip('/').split('/') if p]
    for pattern in patterns:
        if pattern.startswith('*.') and parts and parts[-1].endswith(pattern[1:]):
            return True
        if pattern in parts:
            return True
    return False


def _git_ignored(mirror_real: Path, relative: str) -> list[str]:
    """Ignored paths at or below ``relative`` in the mirror checkout (Git collapses ignored directories)."""
    try:
        result = subprocess.run(['git', '-C', str(mirror_real), 'ls-files', '-z', '--others', '--ignored',
                                 '--exclude-standard', '--directory', '--', relative or '.'],
                                capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise OffloadRefused(f'cannot list ignored mirror content: {exc}') from None
    if result.returncode != 0:
        raise OffloadRefused('mirror is not a readable Git checkout: '
                             + result.stderr.decode(errors='replace').strip()[:200])
    return sorted(p for p in result.stdout.decode().split('\0') if p)


def _membership(directory: Path, skip: set[str], collected: _ClosureFiles | None = None) -> list[list[Any]]:
    """Sorted relative names and sizes below a byte-bound directory (delta2, lead ruling 3).

    Declared inputs (``skip``) carry no size: their bytes are bound separately and a transported
    ledger may be a shorter prefix on the receiver before placement.
    """
    rows = []
    for name in (collected.listings[str(directory)] if collected is not None and str(directory) in collected.listings
                 else _directory_listing(directory)):
        path = directory / name
        rows.append([name, None if os.path.realpath(path) in skip else os.lstat(path).st_size])
    return rows


def _mirror_ignored(target: Path, mirror_real: Path, policy: dict[str, Any], declared_real: set[str],
                    collected: _ClosureFiles | None, link: str) -> list[dict[str, Any]]:
    """Classify every ignored path a mirror link reaches (D3); bind or refuse the undeclared ones."""
    relative = target.relative_to(mirror_real).as_posix() if target != mirror_real else ''

    def bind(path, row):
        if path.is_dir() and not path.is_symlink():
            if collected is not None:
                _directory_listing(path, collected, why=link, into='ignored')
            row['members'] = _membership(path, declared_real, collected)
            row['directories'] = (collected.trees[str(path)] if collected is not None
                                  else _walk_tree(path)[1])
        elif collected is not None and str(path) not in declared_real:
            collected.add(path, link, into='ignored')
        return row

    rows = []
    for entry in _git_ignored(mirror_real, relative):
        # A file inside an ignored directory is listed as that directory: classify the file itself.
        if target.is_file():
            entry = relative
        path = mirror_real / entry
        if any(entry.startswith(prefix) for prefix in policy['identity_bound']):
            rows.append({'path': entry, 'class': 'identity_bound'})
        elif _policy_match(entry, policy['regenerated']):
            rows.append({'path': entry, 'class': 'regenerated'})
        elif target.is_file() and str(target) in declared_real:
            rows.append({'path': entry, 'class': 'declared_input'})
        elif not target.is_file() and any(entry.startswith(d) for d in policy['declared_directories']):
            row = {'path': entry, 'class': 'declared_directory'}
            # Not an exemption: either the consumed files are declared inputs (``consumed``), or the
            # whole directory is bound by bytes and membership (``bind``).
            rows.append(row if policy['declared_directory_mode'] == 'consumed' else bind(path, row))
        elif policy['undeclared'] == 'bind':
            rows.append(bind(path, {'path': entry, 'class': 'bound'}))
        else:
            raise OffloadRefused(f'mirror link {link} reaches an undeclared ignored input {entry}: declare it '
                                 '(ledger or N1 census) or remove the dependency')
        if target.is_file():
            break
    return rows


def _external_row(path: Path, relative: str, root_real: Path, mirror_real: Path | None, policy, declared_real,
                  collected: _ClosureFiles | None):
    kind, target, hops = _classify_link(path, root_real, mirror_real)
    if kind == 'internal':
        return None
    if any(_has_dotdot(hop) for hop in hops):
        # delta2: never resolve '..' on the dependency's behalf; the link must name its target plainly.
        raise OffloadRefused(f'external link {relative} contains a ".." component ({hops}); link the target directly')
    if len(hops) > 1 and kind not in ('mirror', 'session'):
        # D2: a link whose immediate target is another link refuses before anything behind it is read.
        raise OffloadRefused(f'external link {relative} points at a further link ({hops[0]}); link the target directly')
    row: dict[str, Any] = {'class': kind, 'target': str(target), 'hops': hops}
    if kind == 'mirror':
        row['mirror_path'] = target.relative_to(mirror_real).as_posix() if target != mirror_real else '.'
        row['ignored'] = _mirror_ignored(target, mirror_real, policy, declared_real, collected, relative)
    elif kind == 'bytes':
        if target.is_dir():
            files = _directory_listing(target, collected, why=relative)       # memoized: one walk per finalize
            tree = collected.trees[str(target)] if collected is not None else _walk_tree(target)[1]
            row.update(kind='directory', files=files, directories=tree)
        else:
            if collected is not None:
                collected.add(target, relative)
            row['kind'] = 'file'
    return row


def _closure(root: Path, *, mirror: dict[str, Any] | None, inputs: tuple[Path | str, ...],
             ignored_policy: dict[str, Any] | None) -> dict[str, Any]:
    if mirror is not None and (not isinstance(mirror, dict) or set(mirror) != {'root', 'identity'}
                               or not isinstance(mirror['identity'], dict)):
        raise OffloadRefused('mirror must be {root, identity}')
    policy = dict(DEFAULT_IGNORED_POLICY if ignored_policy is None else ignored_policy)
    if (set(policy) != set(DEFAULT_IGNORED_POLICY) or policy['undeclared'] not in ('bind', 'refuse')
            or policy['declared_directory_mode'] not in ('bind', 'consumed')):
        raise OffloadRefused('ignored_policy must name identity_bound, regenerated, declared_directories, '
                             'undeclared and declared_directory_mode')
    root_real = Path(os.path.realpath(root))
    mirror_real = Path(os.path.realpath(mirror['root'])) if mirror is not None else None
    collected = _ClosureFiles()
    declared: dict[str, dict[str, str]] = {}
    for value in inputs:
        path = Path(value)
        if (not path.is_absolute() or _has_dotdot(path) or path.is_symlink() or not path.is_file()
                or _under(path, root)):
            raise OffloadRefused(f'declared input must be an absolute regular file outside the root, without "..": {path}')
        # D1: the destination's real ancestry is bound and re-checked before any placement.
        declared[str(path)] = {'real': os.path.realpath(path)}
        collected.add(path, 'declared input')
    declared_real = {row['real'] for row in declared.values()}
    links: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        if path.is_symlink():
            relative = path.relative_to(root).as_posix()
            row = _external_row(path, relative, root_real, mirror_real, policy, declared_real, collected)
            if row is not None:
                links[relative] = row
    return {'links': links, 'files': collected.files, 'ignored': collected.ignored, 'inputs': declared,
            'mirror': mirror, 'ignored_policy': policy}


def finalized_manifest(root: Path | str, *, mirror: dict[str, Any] | None = None,
                       inputs: tuple[Path | str, ...] = (), ignored_policy: dict[str, Any] | None = None
                       ) -> dict[str, Any]:
    """The record-bound manifest, written on the MBP at finalize and committed with the record.

    ``entries``: relative path -> ``{sha256, size}`` (regular file), ``{link}`` (symlink, kept
    literally) or ``{directory: True}``. ``source_root``: the restore namespace. ``closure``: the
    finite inventory of the external inputs that links point at (R17 review F1, delta D1-D4):

    * every external link is followed hop by hop with lstat. A link to a further link refuses,
      unless the chain ends in the mirror, where every hop text is bound;
    * a link into ``mirror['root']`` (the measurement checkout) is bound by ``mirror['identity']``
      plus its mirror-relative target. Every ignored path it reaches is classified by
      ``ignored_policy``; undeclared ones are byte-bound (library default) or refused (CLI);
    * any other external link target is bound by the bytes it reaches (a file, or every regular file
      below a directory), within the finite bounds; an absent target stays bound as absent;
    * ``inputs`` are the declared absolute files bound by bytes and by their real path (the ledger).

    The external bytes are re-verified at pack and on the Air before the tree is published.
    """
    root = Path(root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise OffloadRefused('source root must be an absolute real directory')
    return {'schema': FINALIZED_SCHEMA, 'source_root': str(root), 'entries': _tree_rows(root),
            'closure': _closure(root, mirror=mirror, inputs=inputs, ignored_policy=ignored_policy)}


def _validate_finalized(finalized: Any) -> None:
    closure = finalized.get('closure') if isinstance(finalized, dict) else None
    if (not isinstance(finalized, dict) or set(finalized) != FINALIZED_KEYS
            or finalized.get('schema') != FINALIZED_SCHEMA or not isinstance(finalized.get('source_root'), str)
            or not isinstance(finalized.get('entries'), dict) or not isinstance(closure, dict)
            or set(closure) != CLOSURE_KEYS):
        raise OffloadRefused('finalized record manifest malformed (schema ' + FINALIZED_SCHEMA + ')')


def _as_finalized(rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for name, row in rows.items():
        if 'link' in row:
            out[name] = {'link': row['link']}
        elif row.get('dir'):
            out[name] = {'directory': True}
        else:
            out[name] = {'sha256': row['sha256'], 'size': row['size']}
    return out


def _check_finalized(rows, finalized_entries, where):
    actual = _as_finalized(rows)
    if actual != finalized_entries:
        missing = sorted(set(finalized_entries) - set(actual))
        extra = sorted(set(actual) - set(finalized_entries))
        changed = sorted(k for k in set(actual) & set(finalized_entries) if actual[k] != finalized_entries[k])
        raise OffloadRefused(f'{where} differs from the finalized record manifest: missing={missing[:5]} '
                             f'extra={extra[:5]} changed={changed[:5]}')


def _same_bytes(path: Path, row: dict[str, Any]) -> bool:
    try:
        info = os.lstat(path)
        return (stat.S_ISREG(info.st_mode) and info.st_size == row['size']
                and _file_sha256(path) == row['sha256'])
    except OSError:
        return False


def _verify_closure(closure: dict[str, Any], root: Path, *, mirror_identity: dict[str, Any] | None,
                    transported: frozenset[str] = frozenset(), where: str, namespace: str | None = None) -> None:
    """Re-verify the closure against this host's bytes.

    ``root`` is where the tree is now (or staged); ``namespace`` the restore path it will be published
    at, so a ``session``-class chain back into the session resolves as it did at finalize.
    """
    mirror = closure['mirror']
    if mirror is not None and mirror_identity != mirror['identity']:
        raise OffloadRefused(f'{where}: measurement checkout mirror differs from the finalized record manifest: '
                             + json.dumps({'finalized': mirror['identity'], 'here': mirror_identity}, sort_keys=True))
    for name, row in sorted(closure['inputs'].items()):
        if os.path.realpath(name) != row['real']:
            raise OffloadRefused(f'{where}: declared input {name} resolves to {os.path.realpath(name)}, '
                                 f'not the finalized {row["real"]}')
    root_real = Path(os.path.realpath(root))
    namespace_real = Path(os.path.realpath(namespace)) if namespace is not None else None
    session_reals = (root_real,) + ((namespace_real,) if namespace_real is not None else ())
    rebase = (namespace_real, root_real) if namespace_real is not None and namespace_real != root_real else None
    mirror_real = Path(os.path.realpath(mirror['root'])) if mirror is not None else None
    policy = closure['ignored_policy']
    declared_real = {row['real'] for row in closure['inputs'].values()}
    transported_real = {os.path.realpath(name) for name in transported} | set(transported)
    for relative, row in sorted(closure['links'].items()):
        kind, target, hops = _classify_link(root / relative, root_real, mirror_real, session_reals, rebase)
        if kind != row['class'] or str(target) != row['target'] or hops != row['hops']:
            raise OffloadRefused(f'{where}: external link {relative} resolves differently from the finalized '
                                 f'record manifest ({kind} {target} via {hops})')
        if kind == 'bytes' and row['kind'] == 'directory' and list(_walk_tree(target)) != [row['files'],
                                                                                           row['directories']]:
            raise OffloadRefused(f'{where}: external closure directory differs from the finalized record '
                                 f'manifest: {target}')
        if kind == 'bytes' and row['kind'] == 'file' and target.is_dir():
            raise OffloadRefused(f'{where}: external closure file became a directory: {target}')
        if kind == 'mirror':
            mirror_path = target.relative_to(mirror_real).as_posix() if target != mirror_real else '.'
            if mirror_path != row['mirror_path']:
                raise OffloadRefused(f'{where}: mirror link {relative} selects {mirror_path}, not {row["mirror_path"]}')
            here = _mirror_ignored(target, mirror_real, policy, declared_real, None, relative)
            if here != row['ignored']:
                raise OffloadRefused(f'{where}: ignored mirror content under {relative} differs from the finalized '
                                     'record manifest')
    for group in ('files', 'ignored'):
        for name, row in sorted(closure[group].items()):
            if name in transported_real:
                continue
            if not _same_bytes(Path(name), row):
                raise OffloadRefused(f'{where}: external closure input differs from the finalized record '
                                     f'manifest: {name}')


def byte_bound_inputs(finalized: dict[str, Any]) -> list[str]:
    """Every byte-bound closure input (Air-offload S1-04): declared inputs (the ledger, external terminal
    evidence), byte-bound link targets and byte-bound ignored content. A pack carries them all, so the
    Air copy restores on its own, without the MBP's external files."""
    closure = finalized['closure']
    return sorted(set(closure['files']) | set(closure['ignored']))


def _bound_row(finalized: dict[str, Any], path: str):
    closure = finalized['closure']
    return closure['files'].get(path) or closure['ignored'].get(path)


def _bound_real(finalized: dict[str, Any], path: str) -> str:
    """The real path a transported input is placed at: a declared input's bound resolution, else the
    closure key itself (link targets and ignored content are keyed by their real paths)."""
    row = finalized['closure']['inputs'].get(path)
    return row['real'] if row is not None else path


def bound_directories(finalized: dict[str, Any]) -> list[str]:
    """Every directory entry of every byte-bound directory target, empty ones included (Air-offload delta2):
    the pack carries them and unpack recreates them, so an empty external directory restores too."""
    closure = finalized['closure']
    mirror = closure['mirror']
    mirror_real = Path(os.path.realpath(mirror['root'])) if mirror is not None else None
    out = set()
    for row in closure['links'].values():
        if row['class'] == 'bytes' and row.get('kind') == 'directory':
            out.update(os.path.normpath(Path(row['target']) / entry) for entry in row['directories'])
        if row['class'] == 'mirror' and mirror_real is not None:
            for ignored in row.get('ignored', []):
                for entry in ignored.get('directories', []):
                    out.add(os.path.normpath(mirror_real / ignored['path'] / entry))
    return sorted(out)


def _make_bound_directory(path: Path) -> None:
    """Append-only: create a bound directory at its finalized real path; never through a link."""
    if os.path.lexists(path):
        if not stat.S_ISDIR(os.lstat(path).st_mode) or os.path.realpath(path) != str(path):
            raise OffloadRefused(f'bound external directory is not a real directory at its finalized path: {path}')
        return
    ancestor = path.parent
    while not os.path.lexists(ancestor):
        ancestor = ancestor.parent
    if os.path.realpath(ancestor) != str(ancestor):
        raise OffloadRefused(f'bound external directory {path} would be created through a link at {ancestor}')
    os.makedirs(path)
    if os.path.realpath(path) != str(path):
        raise OffloadRefused(f'bound external directory {path} resolves elsewhere after creation')


def _closure_external(finalized: dict[str, Any], path: str, sha256: str, size: int) -> None:
    row = _bound_row(finalized, path) if isinstance(path, str) else None
    if row is None:
        raise OffloadRefused(f'external file is not bound by the finalized record manifest: {path}')
    if row != {'sha256': sha256, 'size': size}:
        raise OffloadRefused(f'external input differs from the finalized record manifest: {path}')


def pack(source_root: Path | str, out_dir: Path | str, *, finalized: dict[str, Any] | None,
         level: int = DEFAULT_LEVEL, threads: int = 0, external: tuple[Path | str, ...] = (),
         mirror_identity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pack ``source_root`` into ``out_dir`` (new), bound to the finalized record manifest. Returns the manifest.

    ``finalized`` (the record-bound manifest from finalize) is REQUIRED (R17 review F2): every
    packed byte, link and directory must equal it, its external closure must still hold on this
    host (``mirror_identity`` is this host's checkout identity when it binds a mirror), and every
    ``external`` file must be a closure file with the bound bytes; otherwise the pack refuses and
    leaves nothing.

    ``external`` names absolute regular files outside the root that the harvest reads at their own
    path (the measurement checkout's calibration ledger, which the window appended to). They travel
    in the same payload and are restored at the same absolute path, append-only.
    """
    if finalized is None:
        raise OffloadRefused('pack requires the finalized record manifest (record-bound); '
                             'pack_unbound is the synthetic/legacy seam only')
    _validate_finalized(finalized)
    source = Path(source_root)
    if str(source) != finalized['source_root']:
        raise OffloadRefused('source root differs from the finalized record manifest')
    for path in external:
        if _bound_row(finalized, str(Path(path))) is None:
            raise OffloadRefused(f'external file is not a byte-bound input of the finalized record manifest: {path}')
    if source.is_dir() and not source.is_symlink():
        _verify_closure(finalized['closure'], source, mirror_identity=mirror_identity, where='pack')

    def check(rows, outside):
        _check_finalized(rows, finalized['entries'], 'packed tree')
        for row in outside.values():
            _closure_external(finalized, row['path'], row['sha256'], row['size'])

    return _pack(source, Path(out_dir), level=level, threads=threads, external=external, check=check,
                 finalized_sha256=manifest_sha256(finalized), external_directories=bound_directories(finalized))


def pack_unbound(source_root: Path | str, out_dir: Path | str, *, level: int = DEFAULT_LEVEL,
                 threads: int = 0, external: tuple[Path | str, ...] = ()) -> dict[str, Any]:
    """SYNTHETIC/LEGACY seam: pack with no record binding. Never the production route (the CLI refuses it)."""
    return _pack(Path(source_root), Path(out_dir), level=level, threads=threads, external=external,
                 check=None, finalized_sha256=None)


def _pack(source: Path, out: Path, *, level, threads, external, check, finalized_sha256,
          external_directories=None) -> dict[str, Any]:
    if not source.is_absolute() or source.is_symlink() or not source.is_dir():
        raise OffloadRefused('source root must be an absolute real directory')
    if any(os.path.lexists(source / name) for name in RESERVED_NAMES):
        raise OffloadRefused('reserved name in the session root: ' + ', '.join(sorted(RESERVED_NAMES)))
    externals = [Path(p) for p in external]
    for path in externals:
        if not path.is_absolute() or path.is_symlink() or not path.is_file() or _under(path, source):
            raise OffloadRefused(f'external entry must be an absolute regular file outside the root: {path}')
    out.mkdir(parents=True, exist_ok=False)
    try:
        rows: dict[str, dict[str, Any]] = {}
        outside: dict[str, dict[str, Any]] = {}
        payload = out / PAYLOAD
        with payload.open('wb') as sink:
            process = subprocess.Popen([zstd_path(), '-q', f'-{int(level)}', f'-T{int(threads)}', '-c'],
                                       stdin=subprocess.PIPE, stdout=sink)
            try:
                with tarfile.open(fileobj=process.stdin, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                    for path in _walk(source):
                        relative = path.relative_to(source).as_posix()
                        info = os.lstat(path)
                        tarinfo = tarfile.TarInfo(relative)
                        tarinfo.mode, tarinfo.mtime = stat.S_IMODE(info.st_mode), int(info.st_mtime)
                        tarinfo.uid = tarinfo.gid = 0
                        tarinfo.uname = tarinfo.gname = ''
                        if stat.S_ISLNK(info.st_mode):
                            tarinfo.type, tarinfo.linkname = tarfile.SYMTYPE, os.readlink(path)
                            tar.addfile(tarinfo)
                            rows[relative] = {'link': tarinfo.linkname}
                        elif stat.S_ISDIR(info.st_mode):
                            tarinfo.type = tarfile.DIRTYPE
                            tar.addfile(tarinfo)
                            rows[relative] = {'dir': True, 'mode': tarinfo.mode}
                        elif stat.S_ISREG(info.st_mode):
                            tarinfo.size = info.st_size
                            with path.open('rb') as stream:
                                reader = _HashingReader(stream)
                                tar.addfile(tarinfo, reader)
                            if reader.size != info.st_size:
                                raise OffloadRefused(f'file changed while packing: {relative}')
                            rows[relative] = {'sha256': reader.digest.hexdigest(), 'size': reader.size,
                                              'mode': tarinfo.mode}
                        else:
                            raise OffloadRefused(f'unsupported file type: {relative}')
                    for index, path in enumerate(externals):
                        info = os.stat(path)
                        tarinfo = tarfile.TarInfo(f'{EXTERNAL}/{index:04d}')
                        tarinfo.mode, tarinfo.mtime, tarinfo.size = (stat.S_IMODE(info.st_mode), int(info.st_mtime),
                                                                     info.st_size)
                        with path.open('rb') as stream:
                            reader = _HashingReader(stream)
                            tar.addfile(tarinfo, reader)
                        outside[tarinfo.name] = {'path': str(path), 'sha256': reader.digest.hexdigest(),
                                                 'size': reader.size, 'mode': tarinfo.mode}
            finally:
                process.stdin.close()
                code = process.wait()
            if code != 0:
                raise OffloadRefused(f'zstd failed with exit {code}')
        if check is not None:
            check(rows, outside)
        manifest = {'schema': SCHEMA, 'source_root': str(source), 'entries': rows, 'external': outside,
                    'files': sum('sha256' in r for r in rows.values()),
                    'bytes': sum(r.get('size', 0) for r in rows.values()),
                    'payload': {'name': PAYLOAD, 'sha256': _file_sha256(payload), 'size': payload.stat().st_size},
                    'zstd_level': int(level), 'finalized_manifest_sha256': finalized_sha256,
                    'external_directories': external_directories}
        (out / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    return manifest


def _under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(name: str) -> PurePosixPath:
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or any(p in ('', '.', '..') for p in relative.parts):
        raise OffloadRefused(f'unsafe path in payload: {name!r}')
    return relative


def _real_parent(staging: Path, relative: PurePosixPath) -> Path:
    """The member's parent inside staging; refuses unless every ancestor is a real directory already restored.

    A payload member can therefore never be written through a restored symlink (for example below the
    measurement view, which links into the checkout) or into a directory the manifest does not hold.
    """
    parent = staging
    for part in relative.parts[:-1]:
        parent = parent / part
        try:
            info = os.lstat(parent)
        except FileNotFoundError:
            raise OffloadRefused(f'unsafe path in payload (parent not restored first): {relative}') from None
        if not stat.S_ISDIR(info.st_mode):
            raise OffloadRefused(f'unsafe path in payload (through a link or file): {relative}')
    return parent


def unpack(offload_dir: Path | str, dest_root: Path | str | None = None, *,
           finalized: dict[str, Any] | None, finalized_sha256: str | None,
           mirror_identity: dict[str, Any] | None = None) -> dict[str, Any]:
    """Restore at the finalized source root after full verification. Returns the transport manifest.

    ``finalized`` and ``finalized_sha256`` (the digest committed in the window record) are REQUIRED
    (R17 review F2): the chain committed digest -> finalized manifest -> offload manifest -> restored
    bytes -> external closure on this host is checked before anything is published; the
    self-written transport manifest alone is never trusted. The restore namespace and every
    external destination come from the finalized manifest. ``mirror_identity`` is this host's
    checkout identity when the finalized manifest binds a mirror.

    ``dest_root`` must equal the recorded source root (it exists only to make the caller state it).
    The destination must not exist.
    """
    if finalized is None or finalized_sha256 is None or manifest_sha256(finalized) != finalized_sha256:
        raise OffloadRefused('finalized record manifest missing or not the committed digest')
    _validate_finalized(finalized)
    return _unpack(Path(offload_dir), dest_root, finalized=finalized, mirror_identity=mirror_identity)


def unpack_unbound(offload_dir: Path | str, dest_root: Path | str | None = None) -> dict[str, Any]:
    """SYNTHETIC/LEGACY seam: restore against the self-written manifest only. Never the production route."""
    return _unpack(Path(offload_dir), dest_root, finalized=None, mirror_identity=None)


def _unpack(offload: Path, dest_root, *, finalized, mirror_identity) -> dict[str, Any]:
    manifest = json.loads((offload / MANIFEST).read_bytes())
    if manifest.get('schema') != SCHEMA:
        raise OffloadRefused('not a harvest offload manifest')
    if finalized is not None:
        if manifest.get('source_root') != finalized['source_root']:
            raise OffloadRefused('offload manifest restore namespace differs from the finalized record manifest')
        if manifest.get('finalized_manifest_sha256') != manifest_sha256(finalized):
            raise OffloadRefused('offload manifest differs from the finalized record manifest (packed against another)')
        _check_finalized(manifest['entries'], finalized['entries'], 'offload manifest')
        for row in manifest.get('external', {}).values():
            _closure_external(finalized, row.get('path'), row.get('sha256'), row.get('size'))
    target = Path(manifest['source_root'])
    if dest_root is not None and Path(dest_root) != target:
        raise OffloadRefused('restore path differs from the recorded source root; harvest bytes would differ')
    if os.path.lexists(target):
        raise OffloadRefused('restore destination already exists')
    payload = offload / manifest['payload']['name']
    if _file_sha256(payload) != manifest['payload']['sha256']:
        raise OffloadRefused('payload digest mismatch')
    staging = target.with_name(target.name + '.restoring')
    if os.path.lexists(staging):
        raise OffloadRefused('stale staging directory present')
    entries = manifest['entries']
    externals = manifest.get('external', {})
    for name, row in externals.items():
        current = Path(row['path'])
        if os.path.lexists(current) and (current.is_symlink() or not current.is_file()):
            raise OffloadRefused(f'external destination is not a regular file: {current}')
    staging.mkdir(parents=True)
    seen: dict[str, dict[str, Any]] = {}
    external_seen: dict[str, dict[str, Any]] = {}
    directory_modes: list[tuple[Path, int, int]] = []
    try:
        with subprocess.Popen([zstd_path(), '-q', '-d', '-c', str(payload)], stdout=subprocess.PIPE) as process:
            with tarfile.open(fileobj=process.stdout, mode='r|') as tar:
                for member in tar:
                    if member.name.startswith(EXTERNAL + '/') and member.isfile():
                        if member.name not in externals or member.name in external_seen:
                            raise OffloadRefused(f'external payload entry not in the manifest: {member.name}')
                        external_seen[member.name] = _stage_external(tar, member, staging, first=not external_seen)
                        continue
                    relative = _safe_relative(member.name)
                    name = relative.as_posix()
                    if relative.parts[0] in RESERVED_NAMES:
                        raise OffloadRefused(f'reserved name in payload: {name}')
                    expected = entries.get(name)
                    # Every member is checked against the manifest BEFORE anything is written for it.
                    if expected is None or name in seen:
                        raise OffloadRefused(f'restored tree differs from manifest: extra={[name]}')
                    kind = 'link' if member.issym() else 'dir' if member.isdir() else 'file' if member.isfile() else None
                    if kind is None:
                        raise OffloadRefused(f'unsupported payload entry: {member.name}')
                    if kind != ('link' if 'link' in expected else 'dir' if expected.get('dir') else 'file'):
                        raise OffloadRefused(f'restored tree differs from manifest: changed={[name]}')
                    path = _real_parent(staging, relative) / relative.name
                    if kind == 'link':
                        os.symlink(member.linkname, path)
                        seen[name] = {'link': member.linkname}
                    elif kind == 'dir':
                        path.mkdir()
                        directory_modes.append((path, member.mode, member.mtime))
                        seen[name] = {'dir': True, 'mode': member.mode}
                    else:
                        stream = tar.extractfile(member)
                        digest, size = hashlib.sha256(), 0
                        with path.open('xb') as sink:
                            for chunk in iter(lambda: stream.read(CHUNK), b''):
                                digest.update(chunk)
                                size += len(chunk)
                                sink.write(chunk)
                        os.chmod(path, member.mode)
                        os.utime(path, (member.mtime, member.mtime))
                        seen[name] = {'sha256': digest.hexdigest(), 'size': size, 'mode': member.mode}
            process.stdout.close()
            if process.wait() != 0:
                raise OffloadRefused('zstd decompression failed')
        for path, mode, mtime in reversed(directory_modes):
            os.chmod(path, mode)
            os.utime(path, (mtime, mtime))
        if seen != entries:
            missing = sorted(set(entries) - set(seen))
            extra = sorted(set(seen) - set(entries))
            changed = sorted(k for k in set(seen) & set(entries) if seen[k] != entries[k])
            raise OffloadRefused(f'restored tree differs from manifest: missing={missing[:5]} '
                                 f'extra={extra[:5]} changed={changed[:5]}')
        expected_external = {name: {k: row[k] for k in ('sha256', 'size', 'mode')} for name, row in externals.items()}
        if external_seen != expected_external:
            raise OffloadRefused('external files differ from manifest')
        if finalized is not None:
            missing_inputs = sorted(set(byte_bound_inputs(finalized)) - {row['path'] for row in externals.values()})
            if missing_inputs:
                # Air-offload S1-04: the Air copy must restore on its own, without the MBP's external files.
                raise OffloadRefused(f'pack does not carry every byte-bound closure input: {missing_inputs[:5]}')
            mirror = finalized['closure']['mirror']
            if mirror is not None and mirror_identity != mirror['identity']:
                raise OffloadRefused('unpack: measurement checkout mirror differs from the finalized record manifest')
            directories = bound_directories(finalized)
            if manifest.get('external_directories') != directories:
                raise OffloadRefused('pack does not carry the directory entries of every byte-bound directory target')
            for directory in directories:      # empty ones included, before any file is placed or verified
                _make_bound_directory(Path(directory))
        # Place the bound external inputs (append-only, each at its finalized real path, re-checked right
        # before the write), so a fresh Air without the MBP's external files holds the whole closure; then
        # verify that closure on THIS host before the tree is published (R17 review F1).
        for name, row in sorted(externals.items()):
            real = _bound_real(finalized, row['path']) if finalized is not None else None
            _place_external(staging / EXTERNAL_STAGING / name.rsplit('/', 1)[1], Path(row['path']), real=real)
        if finalized is not None:
            _verify_closure(finalized['closure'], staging, mirror_identity=mirror_identity, where='unpack',
                            namespace=finalized['source_root'])
        shutil.rmtree(staging / EXTERNAL_STAGING, ignore_errors=True)
        os.rename(staging, target)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return manifest


def _stage_external(tar, member, staging: Path, *, first: bool) -> dict[str, Any]:
    """Stage one external inside the verified staging tree, in a directory this restore created itself.

    The directory is made without following anything and an existing entry refuses (seat-1 delta):
    a restored link at that name can never redirect the staged bytes outside the tree.
    """
    directory = staging / EXTERNAL_STAGING
    if first:
        try:
            os.mkdir(directory)
        except FileExistsError:
            raise OffloadRefused(f'external staging name already present in the restored tree: {EXTERNAL_STAGING}') from None
    info = os.lstat(directory)
    if not stat.S_ISDIR(info.st_mode):
        raise OffloadRefused(f'external staging is not a real directory: {directory}')
    stream = tar.extractfile(member)
    digest, size = hashlib.sha256(), 0
    with (directory / member.name.rsplit('/', 1)[1]).open('xb') as sink:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            digest.update(chunk)
            size += len(chunk)
            sink.write(chunk)
    os.chmod(directory / member.name.rsplit('/', 1)[1], member.mode)
    return {'sha256': digest.hexdigest(), 'size': size, 'mode': member.mode}


def _place_external(staged: Path, destination: Path, *, real: str | None = None) -> None:
    """Append-only placement: absent, identical, or the current bytes are a prefix.

    ``real`` (the finalized real path, D1) is re-checked immediately before the write: a retargeted
    ancestor of the destination refuses instead of writing through it.
    """
    if real is not None and os.path.realpath(destination) != real:
        raise OffloadRefused(f'external destination {destination} now resolves to {os.path.realpath(destination)}, '
                             f'not the finalized {real}')
    new = staged.read_bytes()
    if destination.exists():
        old = destination.read_bytes()
        if old == new:
            return
        if not new.startswith(old):
            raise OffloadRefused(f'external file is not an append-only extension: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.restoring')
    shutil.copy2(staged, temporary)
    os.replace(temporary, destination)


def verify_tree(root: Path | str, manifest: dict[str, Any]) -> list[str]:
    """Re-read a restored tree and return every path whose bytes or link differ."""
    root = Path(root)
    problems = []
    actual: dict[str, dict[str, Any]] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            actual[relative] = {'link': os.readlink(path)}
        elif stat.S_ISDIR(info.st_mode):
            actual[relative] = {'dir': True, 'mode': stat.S_IMODE(info.st_mode)}
        else:
            actual[relative] = {'sha256': _file_sha256(path), 'size': info.st_size,
                                'mode': stat.S_IMODE(info.st_mode)}
    for key in sorted(set(actual) | set(manifest['entries'])):
        if actual.get(key) != manifest['entries'].get(key):
            problems.append(key)
    return problems


# Fields that record WHERE and WHEN a harvest ran, not what it found. Two runs of
# the same code on the same bytes at the same paths differ only here (proven by
# tests/align/test_harvest_off.py); with the clock and boot seams pinned they do
# not differ at all. Everything else must match byte for byte.
PROVENANCE_FIELDS = {
    'derived/flags.jsonl': 'every line: emitted (wall_s, monotonic_ns, boot_session_uuid)',
    'derived/window_flags.json': 'window.boot_session_uuid; collector_errors[].elapsed_s',
    'withheld/collector-errors.json': 'errors[].elapsed_s',
    'withheld/desk-verdict-run.json': 'heartbeats; elapsed_s',
    'harvest.json': 'outputs digests of derived/flags.jsonl and derived/window_flags.json',
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def archive_projection(archive_root: Path | str) -> dict[str, str]:
    """Relative path -> SHA-256 of the archive with only PROVENANCE_FIELDS removed.

    Use it to compare an MBP harvest archive with an Air harvest archive of the
    same window (the native confirmation run): the dicts must be equal.
    """
    root = Path(archive_root)
    out: dict[str, str] = {}
    for path in _walk(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            out[relative] = 'link:' + os.readlink(path)
            continue
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if relative == 'derived/flags.jsonl':
            rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
            for row in rows:
                row.pop('emitted', None)
            raw = b'\n'.join(_canonical(row) for row in rows)
        elif relative == 'derived/window_flags.json':
            value = json.loads(raw)
            (value.get('window') or {}).pop('boot_session_uuid', None)
            for row in value.get('collector_errors') or []:
                row.pop('elapsed_s', None)
            raw = _canonical(value)
        elif relative == 'withheld/collector-errors.json':
            value = json.loads(raw)
            for row in value.get('errors') or []:
                row.pop('elapsed_s', None)
            raw = _canonical(value)
        elif relative == 'withheld/desk-verdict-run.json':
            value = json.loads(raw)
            for key in ('heartbeats', 'elapsed_s'):
                value.pop(key, None)
            raw = _canonical(value)
        elif relative == 'harvest.json':
            value = json.loads(raw)
            for key in ('derived/flags.jsonl', 'derived/window_flags.json'):
                (value.get('outputs') or {}).pop(key, None)
            raw = _canonical(value)
        out[relative] = hashlib.sha256(raw).hexdigest()
    return out
