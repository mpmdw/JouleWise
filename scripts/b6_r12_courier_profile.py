"""Fresh R12 external interpreter profile for the original file courier.

The shell and Python payload are pinned, byte-for-byte. Only the executable
input is redirected into the isolated interpreter, preserving argv and stdin.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shlex

PROMPT = "docs/process/NIGHT_COURIER_PROMPT.md"
COURIER = "scripts/b6_courier.sh"


def bootstrap_text():
    return ("from b6_r12_courier_profile import install_runtime\ninstall_runtime()\n"
            "from runtime import bootstrap\nraise SystemExit(bootstrap())\n")


def prepare_profile(root):
    root = Path(root)
    (root / "b6_r12_courier_profile.py").write_bytes(Path(__file__).read_bytes())
    (root / "bootstrap.py").write_text(bootstrap_text())
    # Global aliases also apply after the shell's exec precommand modifier.
    # The original pinned shell file is sourced unchanged, not parsed/rebuilt.
    alias = "/opt/homebrew/bin/python3.13=" + shlex.quote(str(root / "interpreter/python3.13"))
    (root / "courier-source.zsh").write_text(
        "#!/bin/zsh -f\nalias -g " + shlex.quote(alias) + '\nsource "$1" "${@:2}"\n')
    path = root / "manifest.json"
    value = json.loads(path.read_bytes())
    value["generator_files_sha256"][Path(__file__).name] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    value["courier_profile"] = {"kind": "original pinned file courier with isolated interpreter input",
        "bootstrap_sha256": hashlib.sha256((root / "bootstrap.py").read_bytes()).hexdigest(),
        "shell_input_sha256": hashlib.sha256((root / "courier-source.zsh").read_bytes()).hexdigest(),
        "seam": "b6_r12_runtime.install_sources -> returned ChainSources.rewritten; external executable input only",
        "interpreter_input": "/opt/homebrew/bin/python3.13 -> " + str(root / "interpreter/python3.13"),
        "judgments_and_writers": "original f31; no replacement", "network_or_message_delivery": False}
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return root


def export_prompt(root):
    from b6_r12_session_fixture import git_blobs
    raw = git_blobs([PROMPT])[PROMPT]
    target = Path(root) / "pin" / PROMPT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    path = Path(root) / "manifest.json"
    value = json.loads(path.read_bytes())
    value["pinned_input_sha256"][PROMPT] = hashlib.sha256(raw).hexdigest()
    value["courier_profile"]["courier_sha256"] = value["source_sha256"][COURIER]
    value["courier_profile"]["prompt_sha256"] = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def install_runtime():
    """Install only in the generator bootstrap, before pinned code imports."""
    import runtime
    original = runtime.install_sources
    if getattr(original, "_r12_courier_profile", False):
        return

    def install(root, clock):
        sources = original(root, clock)
        rewritten = sources.rewritten
        root = Path(root)
        profile = json.loads((root / "manifest.json").read_bytes())["courier_profile"]

        def command_input(argv):
            words = list(map(str, argv))
            if words and Path(words[0]).name == "b6_courier.sh":
                path = Path(words[0])
                if (path.is_absolute() and path.is_relative_to(root)
                        and path == path.resolve()
                        and path.parent.name == "scripts"
                        and hashlib.sha256(path.read_bytes()).hexdigest() == profile["courier_sha256"]):
                    return ["/bin/zsh", "-f", str(root / "shell.zsh"),
                            str(root / "courier-source.zsh"), *words]
            return rewritten(argv)

        sources.rewritten = command_input
        return sources

    install._r12_courier_profile = True
    runtime.install_sources = install
