#!/usr/bin/env python3
"""One original-loop session with the fresh courier executable-input profile.

Each invocation ends at a completed original driver/desk boundary. An
interrupted phase cannot be resumed. The original loop writes the attempt;
this scheduler never invents DONE or combines attempts from separate roots.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import b6_r12_reduced_set as inputs
import b6_r12_single_pack as single
from b6_r12_courier_profile import prepare_profile, export_prompt, bootstrap_text
from b6_r12_verify import safe_root, sha

INITIALIZE_INPUTS = inputs.initialize
# Full-volume production sessions, one per pack (RL-48 item 5 / RL-98 term 3).
# Registered counts come from the pinned plan_tree configs; nothing is changed.
PACKS = ("alpha", "beta", "gamma")


def prediction(pack):
    if pack == "beta":  # byte-identical to the first (root-23) declaration
        return "original BETA roster/streams at full volume; completed production reader exits 0/comparator agrees; no closed-nine claim"
    return (f"original {pack.upper()} roster/streams at full volume; completed production reader exits 0/"
            "comparator agrees; no closed-nine claim")


def smoke_text(pack):
    return ("original supplier's reduced 65 s / one CPU; ordinary full " + pack.upper()
            + " r1 remains 335 s / 16 CPUs")


def initialize(main, prior, volume, declaration):
    original_prepare, original_export = inputs.prepare, inputs.export_chain_inputs

    def prepare(root):
        return prepare_profile(original_prepare(root))

    def export(root):
        original_export(root)
        export_prompt(root)

    # All substitutions below are our generator's input preparation, not
    # functions or defaults of the pinned collection chain.
    with patch.object(inputs, "prepare", prepare), \
         patch.object(inputs, "export_chain_inputs", export), \
         patch.object(inputs, "reduced_bootstrap", bootstrap_text):
        INITIALIZE_INPUTS(main, prior)
    source = main / "source-policy.json"
    policy = json.loads(source.read_bytes())
    policy.update(volume=volume, primary_stream_duration_s=335 if volume == "full" else 65,
                  token_first_s=1.0 if volume == "full" else .5,
                  token_next_s=.05 if volume == "full" else .001)
    source.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")
    path = main / "manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest["initialization_supplier"] = manifest.pop("reduced_set")
    manifest["initialization_supplier"]["scope"] = "input setup only; active profile declared below"
    manifest["volume"] = volume
    manifest["profile_session"] = {**declaration, "source_policy_before_loop": policy,
        "full_volume_claim": volume == "full", "registered_counts_and_thresholds": "unchanged",
        "ordinary_source_policy": "original b6_r12_orchestrate.session_policy, plus explicit single-pack scenario inputs",
        "smoke": smoke_text(declaration["pack"])}
    manifest["generator_files_sha256"][Path(__file__).name] = sha(Path(__file__))
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def run(outer, prior=None, pack=None, scenario=None, volume=None):
    outer = safe_root(outer)
    fresh = prior is not None
    if fresh:
        if outer.exists() or pack not in PACKS or scenario != "plain" or volume != "full":
            raise ValueError("first production-size profile requires new root, ALPHA/BETA/GAMMA plain/full")
        declaration = {"schema": "r12.courier-profile-session.v1", "pin": inputs.PIN,
            "synthetic_only": True, "runner_sha256": sha(Path(__file__)),
            "courier_profile_sha256": sha(Path(__file__).with_name("b6_r12_courier_profile.py")),
            "pack": pack, "scenario": scenario, "volume": volume,
            "prediction": prediction(pack)}
    else:
        declaration = json.loads((outer / "profile-inputs.json").read_bytes())
        if (declaration["runner_sha256"] != sha(Path(__file__))
                or declaration["courier_profile_sha256"] != sha(Path(__file__).with_name("b6_r12_courier_profile.py"))):
            raise ValueError("fresh source-profile implementation changed")
        pack, scenario, volume = (declaration[key] for key in ("pack", "scenario", "volume"))

    def prepared(main, seed):
        (outer / "profile-inputs.json").write_text(json.dumps(declaration, indent=2, sort_keys=True) + "\n")
        initialize(main, seed, volume, declaration)

    with patch.object(single.inputs, "initialize", prepared):
        # INITIALIZE_INPUTS above retains the generator's actual initializer;
        # single.inputs and inputs refer to the same module.
        return single.run(outer, prior, pack, scenario, declared_volume=volume)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--prior-chain-root", type=Path)
    parser.add_argument("--pack", choices=PACKS)
    parser.add_argument("--scenario", choices=("plain",))
    parser.add_argument("--volume", choices=("full",))
    args = parser.parse_args()
    return run(args.out, args.prior_chain_root, args.pack, args.scenario, args.volume)


if __name__ == "__main__":
    raise SystemExit(main())
