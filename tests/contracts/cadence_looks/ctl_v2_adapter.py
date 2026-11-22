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
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCHEMA_COMMIT = "321357e431ae17ade5186ab84666235e077c2119"
SCHEMA_SHA = "0e749ba6fad2b43c68a8e9322f30c3123f4a7af530873d517ac0cec64fe177c1"
STAGE1_COMMIT = "e" * 40
STAGE1_SHA = "d7f36fcb3fec2d8e9d9b4a7ed745532d9b8604c20d3a67968a181a85c5b0f058"


def fixture_bytes(name, digest):
    raw = (FIXTURES / name).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise AssertionError("instrument fixture bytes changed")
    return raw


def synthetic_hold(sd=0.5, *, kit="f2-inst-01"):
    channel = {f"sd{width}_w": sd for width in analysis.FLOOR_WINDOWS}
    channel.update(mean_w=3, kept=[3, 3, 3], dropped=[0, 0, 0], drift_w_per_600s=0)
    return manifest.canonical({f"{kit}/L001": dict.fromkeys(("gpu_rail", "rail_sum", "dc_in"), channel)})


def instrument_artifacts():
    schema = fixture_bytes("lm-inst-01.restricted.schema.draft.json", SCHEMA_SHA)
    return {
        "instrument_manifest": manifest.canonical({
            "schema": "joulewise.cadence_look_manifest.v2", "look_id": "lm-inst-01",
            "look_kind": "description", "status": "committed",
            "kits": [{"kit_id": "f2-inst-01", "sha256": sha256(b"synthetic instrument kit").hexdigest()}],
            "code_pins": {"restricted_schema": {"path": manifest.INSTRUMENT_SCHEMA_PATH, "sha256": SCHEMA_SHA}},
        }),
        "instrument_floor_schema": schema,
        "hold": synthetic_hold(),
        "edges": manifest.canonical({"synthetic": "edges"}),
    }


def instrument_commitments():
    """Give the real gate an invented ledger commit and an exact schema fixture."""
    commits = {
        SCHEMA_COMMIT: {manifest.INSTRUMENT_SCHEMA_PATH:
                        fixture_bytes("lm-inst-01.restricted.schema.draft.json", SCHEMA_SHA)},
        STAGE1_COMMIT: {"instrument_stage1": fixture_bytes("lm-inst-01.stage1.synthetic.json", STAGE1_SHA)},
    }
    stage1 = dict(kind="stage1", look_id="lm-inst-01", status="committed", revision=STAGE1_COMMIT,
                  stage1_sha256=STAGE1_SHA, manifest_sha256=sha256(instrument_artifacts()["instrument_manifest"]).hexdigest())
    return commits, stage1


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
    artifacts.update(instrument_artifacts())
    return artifacts


def release_layout(directory):
    layout = {}
    for side in ("private", "public"):
        path = (directory / side / "lm-ctl-01").resolve()
        info = path.stat()
        layout[side] = dict(path=str(path), device=info.st_dev, inode=info.st_ino)
    return layout


def make_manifest(look, route, pins, *, layout=None):
    if layout is None:
        layout = {
            "private": dict(path="/invented/private/lm-ctl-01", device=1, inode=1),
            "public": dict(path="/invented/public/lm-ctl-01", device=1, inode=2),
        }
    return manifest.canonical(dict(schema=manifest.SCHEMA_ID, status="final", look_id=look,
                                   look_kind=route, kit_id="cl-ctl-01", pins=pins,
                                   release_layout=layout,
                                   instrument_output_schema=dict(commit=SCHEMA_COMMIT,
                                       path=manifest.INSTRUMENT_SCHEMA_PATH, sha256=SCHEMA_SHA),
                                   instrument_stage1=dict(ledger_commit=STAGE1_COMMIT, stage1_sha256=STAGE1_SHA)))


def read_frozen(state, first_read):
    commits, instrument_stage1 = instrument_commitments()
    manifest.verify_freeze(current_revision=state["current_revision"], committed={**state["committed"], **commits},
                           working=state["working"], history=[instrument_stage1, *state["history"]])
    return first_read()


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
