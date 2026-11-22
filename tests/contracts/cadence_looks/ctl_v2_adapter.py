"""Synthetic stores and output paths for the frozen V2 integration suite."""

from contextlib import contextmanager
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from joulewise.cadence_looks import controls_analysis as analysis
from joulewise.cadence_looks import controls_manifest as manifest
from joulewise.cadence_looks import controls_release as release

ROOT = Path(__file__).resolve().parents[3]
INSTRUMENT = sha256(b"synthetic instrument").hexdigest()


@lru_cache(None)
def freeze_artifacts():
    from joulewise.align import records

    source_overlay = Path(records.__file__).resolve().parents[1]
    artifacts = {}
    for name, location in manifest.CODE_PATHS.items():
        local = ROOT / location
        if local.is_file():
            artifacts[name] = local.read_bytes()
        elif location.startswith("joulewise/align/"):
            artifacts[name] = (source_overlay / location.removeprefix("joulewise/")).read_bytes()
        else:
            # The fixed shared failure vocabulary is on main. This isolated
            # draft does not copy or edit that lane's module.
            artifacts[name] = subprocess.check_output(
                ["git", "show", f"5a8ac8ff6753caf76cac01bfc4d15d6f0385afc5:{location}"], cwd=ROOT
            )
    floor_schema = manifest.canonical({"$defs": {"undefined": {"properties": {
        "reason": {"type": "string", "enum": ["synthetic_floor_unavailable"]},
    }}}})
    artifacts.update(
        instrument_manifest=manifest.canonical({
            "schema": "joulewise.cadence_look_manifest.v2", "look_id": "lm-inst-01",
            "look_kind": "description", "status": "committed",
            "code_pins": {"restricted_schema": {"path": manifest.LOOK_DIR + "lm-inst-01.restricted.schema.json",
                                                "sha256": sha256(floor_schema).hexdigest()}},
        }),
        instrument_floor_schema=floor_schema,
        hold=manifest.canonical({"synthetic": "hold"}),
        edges=manifest.canonical({"synthetic": "edges"}),
    )
    return artifacts


def make_manifest(look, route, pins):
    return manifest.canonical(dict(schema=manifest.SCHEMA_ID, status="final", look_id=look,
                                   look_kind=route, kit_id="cl-ctl-01", pins=pins))


def read_frozen(state, first_read):
    return manifest.read_frozen(current_revision=state["current_revision"], committed=state["committed"],
                                working=state["working"], history=state["history"], first_read=first_read)


def append_row(row, append):
    manifest.append_withheld(row, append)


def apply_design(observations, append, issue):
    # In RL-197, V2's callback observes eligibility for the look's reservation.
    if manifest.select_reservation(observations=observations, append=append):
        issue(manifest.ISSUED_SETTINGS)


@lru_cache(None)
def _schemas():
    return tuple((ROOT / manifest.CODE_PATHS[role]).read_bytes()
                 for role in ("output_schema", "restricted_schema"))


@contextmanager
def _reserved_output(blind):
    public_bytes = release.prepare_public(blind, _schemas()[0])
    with TemporaryDirectory(prefix=".controls-v3-", dir=ROOT) as directory:
        root = Path(directory)
        restricted = root / "private" / "lm-ctl-01" / "synthetic-output"
        public = root / "public" / "lm-ctl-01" / release.PUBLIC_NAME
        for parent in (restricted.parent, public.parent):
            parent.mkdir(parents=True)
        release.reserve_directory(restricted, public)
        # The worker uses inherited descriptors. The in-process fixture
        # supplies the empty captured streams for this synthetic invocation.
        for name in ("stdout", "stderr"):
            (restricted / name).touch(mode=0o600, exist_ok=False)
        yield restricted, public, public_bytes


def _positive_pool():
    member = ("toy", "a" * 64, "L001")
    return analysis.pool_hold_windows(
        (analysis.HoldWindow(member, channel, width, 3, 0.5)
         for channel in ("gpu_rail", "rail_sum", "dc_in") for width in analysis.FLOOR_WINDOWS),
        {member},
    )


def publish(positions, blind, kernel, pooled):
    with _reserved_output(blind) as (restricted, public, public_bytes):
        release.publish_reserved(restricted, public, public_bytes, positions, kernel=kernel,
                                 pooled=_positive_pool() if pooled is None else pooled,
                                 gap_limits_ns=dict.fromkeys(analysis.CHANNELS, 2 * analysis.NS),
                                 instrument_manifest_sha256=INSTRUMENT, schema_bytes=_schemas()[1])
        return json.loads((restricted / "controls.json").read_bytes()), public.read_bytes()


def public_at_fork(blind, private):
    # A post-validation substitution at the same writer boundary. Keep the
    # injected private bytes exactly as the case supplies them.
    with _reserved_output(blind) as (restricted, public, public_bytes):
        release.write_outputs(restricted, public, manifest.canonical(private), public_bytes)
        return public.read_bytes()
