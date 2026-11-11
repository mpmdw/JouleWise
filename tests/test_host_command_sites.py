"""Inventory literal host-command sites, including shell and isolated Python."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = Path(__file__).with_name("host_command_sites.json")
HOST = {"sudo", "systemsetup", "pmset", "caffeinate", "shutdown", "nvram", "kill", "killall"}
LAUNCH = {"bootstrap", "bootout", "load", "unload", "kickstart", "enable", "disable", "remove"}


def _read_only_pmset(tokens):
    from tests.host_command_guard import PMSET_GETTERS
    rest = [t.strip('"\'`$(){},') for t in tokens[1:4]]
    # A literal site is read-only only if the getter ends the command: the next token, if any, must not
    # continue the argv (a setter or more arguments after the getter keep it inventoried).
    if rest[:1] != ["-g"]:
        return False
    if len(rest) == 1 or rest[1] in {";", "&&", "||", "|"}:
        return True
    return rest[1] in PMSET_GETTERS and (len(rest) == 2 or rest[2] in {";", "&&", "||", "|", ")"} or not rest[2].startswith("-"))


def command_sites(tokens):
    """Conservative literal inventory, not a shell evaluation or data reader."""
    for index, token in enumerate(tokens):
        name = token.rsplit("/", 1)[-1].strip('"\'`$(){}')
        if name not in HOST | {"launchctl", "networksetup", "scutil", "defaults", "sys.executable", "PY", "PYTHON", "$PY", "$PYTHON", "${PYTHON}", "${PY}"} and not re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", name):
            continue
        rest = tokens[index + 1:]
        if name == "pmset" and _read_only_pmset(tokens[index:]):
            continue  # read-only getter: the runtime guard allows it (tests/host_command_guard.py)
        if (name in HOST or
            name == "launchctl" and (not rest or rest[0] not in {"print", "list", "blame"}) or
            name in {"networksetup", "scutil"} and any(a.startswith(("-set", "--set")) for a in rest) or
            name == "defaults" and rest and rest[0] == "write"):
            yield name
        if (re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", name) or name in {"sys.executable", "PY", "PYTHON", "$PY", "$PYTHON", "${PYTHON}", "${PY}"}) and any(
                a.startswith("-") and not a.startswith("--") and ("I" in a or "S" in a) for a in rest):
            yield "python-isolated"


def tokenize(text):
    if not re.search(r"sudo|systemsetup|pmset|caffeinate|shutdown|nvram|kill|launchctl|networksetup|scutil|defaults|python|executable|\$PY", text, re.I):
        return []
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()\n")
        lexer.whitespace_split = True
        lexer.commenters = "#"
        return list(lexer)
    except ValueError:
        return text.split()


def scan_source(file, source):
    sites = {}

    def add(locator, tokens, extra=()):
        commands = sorted(set(command_sites(tokens)) | set(extra))
        if not commands:
            return
        text = shlex.join(tokens)
        for command in commands:
            # Command content disambiguates multiple sites in one function and
            # remains stable when unrelated lines are inserted above it.
            digest = hashlib.sha256(text.encode()).hexdigest()[:16]
            entry = {"file": file, "locator": f"{locator}:{digest}", "command": command}
            sites[(entry["locator"], command)] = entry

    if file.endswith(".py"):
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.scope = []

            def visit_FunctionDef(self, node):
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()

            visit_AsyncFunctionDef = visit_FunctionDef
            visit_ClassDef = visit_FunctionDef

            def visit_Constant(self, node):
                if isinstance(node.value, str):
                    add(".".join(self.scope) or "<module>", tokenize(node.value))

            def visit_JoinedStr(self, node):
                value = ''.join(v.value if isinstance(v, ast.Constant) and isinstance(v.value, str)
                                else '{' + ast.unparse(v.value) + '}' for v in node.values)
                add(".".join(self.scope) or "<module>", tokenize(value))

            def visit_List(self, node):
                tokens = [n.value if isinstance(n, ast.Constant) and isinstance(n.value, str)
                          else ast.unparse(n) for n in node.elts]
                isolated = bool(node.elts and not isinstance(node.elts[0], ast.Constant)
                                and any(t in {"-I", "-S"} for t in tokens))
                add(".".join(self.scope) or "<module>", tokens,
                    ("python-isolated",) if isolated else ())
                # Whole string commands nested in a list need their own scan.
                self.generic_visit(node)

            visit_Tuple = visit_List
        Visitor().visit(ast.parse(source, filename=file))
    else:
        logical = source.replace("\\\n", " ")
        for line in logical.splitlines():
            if line.lstrip().startswith("#"):
                continue
            add("shell", tokenize(line))
    return list(sites.values())


def scan():
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "scripts/", "joulewise/"], cwd=ROOT).decode().split('\0')
    sites = []
    for file in tracked:
        if not file:
            continue
        try:
            source = (ROOT / file).read_text()
        except UnicodeDecodeError:
            continue  # Binary artifacts cannot contain executable source literals.
        sites.extend(scan_source(file, source))
    return sorted(sites, key=lambda row: (row["file"], row["locator"], row["command"]))


class HostCommandSiteTests(unittest.TestCase):
    def test_tracked_command_sites_match_reviewed_allowlist(self):
        expected = json.loads(ALLOWLIST.read_text())
        for entry in expected:
            self.assertEqual(set(entry), {"file", "locator", "command", "seam"})
            self.assertTrue(entry["seam"].strip())
        actual = scan()
        stripped = [{k: v for k, v in row.items() if k != "seam"} for row in expected]
        self.assertEqual(len(stripped), len({json.dumps(r, sort_keys=True) for r in stripped}), "duplicate allowlist entries")
        missing = [row for row in actual if row not in stripped]
        stale = [row for row in stripped if row not in actual]
        self.assertFalse(missing or stale, f"unlisted command sites: {missing}\nstale command sites: {stale}")

    def test_scan_synthetic_python_and_shell_sites(self):
        source = "def close():\n run(['/usr/bin/sudo', '-n', 'true'])\n run([sys.executable, '-I', '-c', 'pass'])\n"
        found = scan_source("scripts/fake.py", source)
        self.assertEqual({r['command'] for r in found}, {'sudo', 'python-isolated'})
        self.assertTrue(all(r['locator'].startswith('close:') for r in found))
        self.assertEqual(found, scan_source("scripts/fake.py", '\n\n' + source))
        found = scan_source('scripts/fake.sh', '# sudo ignored\nlaunchctl print x\nlaunchctl bootout x\nkill 1\ndefaults write key value\n')
        self.assertEqual({r['command'] for r in found}, {'launchctl', 'kill', 'defaults'})
        self.assertTrue(scan_source('scripts/fake.zsh', '"$PY" -S -c pass\n'))


if __name__ == '__main__':
    unittest.main()
