"""Demonstrate that a differently named implicit-preserve generator is admitted."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness_evidence as evidence


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="joulewise-a94-probe-") as temporary:
        repository = Path(temporary)
        payload = repository / "payload.txt"
        payload.write_text("science-before\n", encoding="utf-8")
        generator = repository / "generate_configs.py"
        generator.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "if '--check' not in sys.argv:\n"
            "    raise SystemExit(2)\n"
            "saved = Path(__file__).with_name('payload.txt').read_bytes()\n"
            "print('accepted existing bytes', len(saved))\n",
            encoding="utf-8",
        )
        raw = generator.read_bytes()
        context = evidence._DerivationContext(
            pack_root=repository,
            repository=repository,
            tree={},
            pack_sha256="0" * 64,
            head_commit="0" * 40,
        )

        def check() -> dict[str, object]:
            result = evidence._recorded_generator_check(
                context,
                generator.name,
                raw,
                kind="PACK_AUTHENTICATION",
                preserve_current_frozen_bytes=False,
            )
            evidence._require_regenerated_generator_result(
                result, kind="PACK_AUTHENTICATION"
            )
            return result

        before = check()
        payload.write_text("tampered-science-after\n", encoding="utf-8")
        after = check()
        admitted = (
            before["exit_code"] == 0
            and after["exit_code"] == 0
            and before["derivation_mode"] == "regenerated"
            and after["derivation_mode"] == "regenerated"
        )
        print(
            json.dumps(
                {
                    "after_exit": after["exit_code"],
                    "after_mode": after["derivation_mode"],
                    "before_exit": before["exit_code"],
                    "before_mode": before["derivation_mode"],
                    "capability": evidence._generator_preserve_capability(
                        raw, kind="PACK_AUTHENTICATION"
                    ),
                    "tamper_admitted": admitted,
                },
                sort_keys=True,
            )
        )
        return 1 if admitted else 0


if __name__ == "__main__":
    raise SystemExit(main())
