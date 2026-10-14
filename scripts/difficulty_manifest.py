#!/usr/bin/env python3
"""Create an external DIFFICULTY workload manifest."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.benchmark_import_math import load_math_test
from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.manifest import build_manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = Path.home() / "jw_data/math-prm800k-7ecc7947"
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    for argument, filename in (("test-jsonl", "prm_test.jsonl"), ("train-jsonl", "prm_train.jsonl"),
                               ("pointer-test", "ptr_test.txt"), ("pointer-train", "ptr_train.txt"),
                               ("license", "prm_LICENSE")):
        parser.add_argument("--" + argument, type=Path, default=source / filename)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        output = (args.out or Path.home() / "jw_data/difficulty" / f"manifest-{config['version']}.json").expanduser()
        if output.resolve().is_relative_to(ROOT.resolve()):
            parser.error("full manifests containing problem text must be written outside the repository")
        for filename in config["exclude_item_id_files"]:
            try:
                Path(filename).expanduser().read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ValueError(f"cannot read configured exclusion file {filename}: {exc}") from exc
        # Check readability separately: the importer wraps some read errors in ValueError.
        for path in (args.test_jsonl, args.train_jsonl, args.pointer_test, args.pointer_train, args.license):
            with path.expanduser().open("rb"):
                pass
        rows, _ = load_math_test(args.test_jsonl.expanduser(), args.train_jsonl.expanduser(),
                                pointer_test=args.pointer_test.expanduser(),
                                pointer_train=args.pointer_train.expanduser(), license_path=args.license.expanduser())
        manifest = build_manifest(config, rows)
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError) as exc:
        print(f"unusable config or source file: {exc}", file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
