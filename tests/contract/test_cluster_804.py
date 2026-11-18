"""Bind the cluster contract to the offload CLI and its actual crypto and copy code."""

import json
import os
from pathlib import Path
import shutil
import sys
import unittest

from joulewise import span_offload
from tests.contract.cluster import ClusterScenarios, FixtureHooks


def configure(world):
    openssl = shutil.which("openssl")
    if openssl is None:
        raise AssertionError("the offload contract requires openssl")
    recipient = world.root / "keys"
    fingerprint = span_offload.keygen(openssl, recipient, bits=3072)
    # Only the public key is available to the offload process.
    (recipient / "span-offload.key.pem").unlink()
    for name, value in (("provider_evicts", True), ("cloud_availability", "signed_in"),
                        ("forbid_private_inputs", False), ("air_input_reads", [])):
        world.boundary.put(name, value)
    (world.controls / "cloud-bytes").mkdir()
    config = {
        "schema": span_offload.MBP_CONFIG_SCHEMA,
        "recipient_public_key": str(recipient / "span-offload.pub.pem"),
        "recipient_sha256": fingerprint,
        "key_second_copy_attested_sha256": fingerprint,
        "stage_root": str(world.stage.resolve()),
        "marker_dir": str(world.markers.resolve()),
        "openssl": openssl,
        "backend": {
            "kind": "icloud",
            "root": str(world.cloud.resolve()),
            "brctl": str(world.command("brctl", PROVIDER)),
            "evict_timeout_s": 1,
            "poll_interval_s": 0.01,
        },
    }
    world.offload_config.write_text(json.dumps(config), encoding="utf-8")


def prepare(world, *, provider_evicts=None, cloud_availability=None, air_available=None,
            forbid_private_inputs=None):
    if provider_evicts is not None:
        world.boundary.put("provider_evicts", provider_evicts)
    if cloud_availability is not None:
        world.boundary.put("cloud_availability", cloud_availability)
        if cloud_availability == "missing_container":
            world.cloud.rename(world.cloud.with_name("unmounted-cloud"))
    if air_available is not None:
        world.test.assertIs(air_available, False)
        world.test.assertFalse(world.air_config.exists())
        world.ssd.rmdir()
    if forbid_private_inputs is not None:
        world.boundary.put("forbid_private_inputs", forbid_private_inputs)


def observe(world, name, *, span=None):
    if name == "provider_readbacks":
        calls = world.controls / "readbacks"
        return [line for line in calls.read_text().splitlines() if Path(line).parent.name == span.plan]
    if name == "encryption_recipient":
        marker, = world.markers.glob("*.ok")
        return json.loads(marker.read_bytes())["recipient_sha256"]
    if name == "air_input_reads":
        return world.boundary.get(name)
    raise AssertionError(f"unsupported offload observation: {name}")


def child_setup(boundary):
    # The synthetic provider represents the macOS dataless flag with an
    # empty placeholder. Production still checks for eviction and hashes
    # the actual redownloaded artifact.
    span_offload._is_dataless = lambda info: info.st_size == 0

    def advance_poll(seconds):
        boundary.step(wall=seconds, mono=seconds)

    span_offload.time.sleep = advance_poll
    if not boundary.get("forbid_private_inputs"):
        return
    root = boundary.root.parent

    def guard(event, args):
        if event != "open" or isinstance(args[0], int):
            return
        path = Path(os.fsdecode(args[0]))
        if (path.name in {"span-offload.key.pem", "air.json"} or path.name.endswith(".air.ok")
                or path.is_relative_to(root / "ssd")):
            boundary.put("air_input_reads", [*boundary.get("air_input_reads"), str(path)])
            raise AssertionError("offload opened an Air-side input")

    sys.addaudithook(guard)


PROVIDER = """\
import json
import os
from pathlib import Path
import shutil
import sys

control = Path(os.environ["JW_CLUSTER_BOUNDARY"])
command, arg = sys.argv[1:]
if command == "status":
    assert arg == "com.apple.CloudDocs"
    if json.loads((control / "cloud_availability").read_text()) == "signed_out":
        sys.exit(1)
    print("com.apple.CloudDocs client:idle caught-up")
elif command in {"evict", "download"}:
    path = Path(arg)
    assert path.is_relative_to(control.parent.resolve() / "cloud")
    remote = control / "cloud-bytes" / path.parent.name / path.name
    if command == "evict" and json.loads((control / "provider_evicts").read_text()):
        remote.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, remote)
        path.write_bytes(b"")
    if command == "download" and remote.exists():
        shutil.copyfile(remote, path)
        with (control / "readbacks").open("a") as log:
            print(path, file=log)
else:
    sys.exit(2)
"""


class TestCluster804(ClusterScenarios, unittest.TestCase):
    required_ports = ("O",)
    fixture_hooks = FixtureHooks(configure=configure, prepare=prepare, observe=observe, child_setup=child_setup)
