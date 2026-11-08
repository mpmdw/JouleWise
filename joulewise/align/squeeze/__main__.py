"""Read and validate desk configs only. This entrypoint never runs an episode."""
import argparse
import json

from .config import load_kit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("--kit", default="configs/align/squeeze")
    args = parser.parse_args()
    configs = load_kit(args.kit)
    print(json.dumps({"status": "DRAFT", "validated": len(configs),
                      "config_sha256": {name: value["config_sha256"] for name, value in configs.items()}},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
