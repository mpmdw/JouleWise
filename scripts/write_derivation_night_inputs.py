#!/usr/bin/env python3
"""Write the two desk files a derivation night reserves its slots with.

A *derivation night* is a calibration night run on a machine whose identity no
longer matches the acceptance artifact currently in force: macOS was updated,
so the numbers that acceptance ratified were measured on a machine that no
longer exists, and a fresh derivation has to be captured before any bound can
be used again.

The two files:

* the *identity epoch* — the six fields
  ``joulewise.calibration_ledger.IDENTITY_EPOCH_FIELDS`` that name WHICH
  machine and WHICH measurement method a capture belongs to (OS build,
  hardware model, power policy, sampling interval, estimator revision, pulse
  protocol id).  Two captures may only be pooled when all six agree.
* the *T1 bindings* — the identity epoch plus the four execution pins that fix
  the exact binaries and files the capture ran with (the ``powermetrics``
  executable's digest, the clock-anchor method version, the MLX version, and
  the frozen protocol's digest).

``scripts/gen_derivation_night.py`` pins both files' digests into the night's
wrapper, and ``scripts/reserve_calibration_window_bracket.py`` copies their
bytes verbatim into every slot record, so what this script writes at the desk
is what the night's evidence will say it measured.  The values are therefore
NOT typed by hand here: they are read from this machine through the very
functions ``scripts/validate_powermetrics_fiducial.py`` itself calls at
capture time, so the reserved slot's copy and the writer's own measured vector
cannot disagree.

A *stale field* is an identity field whose value on this machine differs from
the active acceptance artifact's identity epoch.  A derivation night exists
precisely because at least one field is stale; if none is, this is an ordinary
night, the ordinary (non-derivation) path applies, and this script refuses
rather than hand a derivation night inputs it would reject at its first step.

This script never reads or writes the calibration ledger, never touches
``configs/calibration``, and never runs ``powermetrics``.  It reads
``sysctl``, hashes ``/usr/bin/powermetrics``, imports ``mlx.core``, and reads
the acceptance artifact — all desk reads.
"""

from __future__ import annotations

import argparse
import importlib
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    DEFAULT_ACCEPTANCE_BOUND_PATH,
)
from joulewise.calibration_ledger import (  # noqa: E402
    IDENTITY_EPOCH_FIELDS,
    T1_FIELDS,
)
from scripts.gen_derivation_night import CHAIN_POWER_POLICY  # noqa: E402
from scripts.generate_g2a_probe_inputs import (  # noqa: E402
    IDENTITY_EPOCH_NAME,
    T1_BINDINGS_NAME,
    _json_bytes,
    _sha256_bytes,
)

SAMPLER_BINARY = Path("/usr/bin/powermetrics")


class NightInputsRefusal(Exception):
    """A named desk refusal: nothing has been written when this is raised."""


def _derive_planned_vectors(power_policy: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read this machine exactly as ``_derive_live_vectors`` does at capture.

    The imports are deferred to call time and taken from the writer's module,
    so the values here are produced by the writer's own code path rather than
    by a second implementation that could drift from it.
    """

    try:
        from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
            PROTOCOL_ID,
            RESIDUAL_REGION_METHOD,
            SAMPLING_INTERVAL_MS,
            _planned_t1_bindings,
            _sysctl_identity,
        )

        planned_epoch = {
            "os_build": _sysctl_identity("kern.osversion"),
            "hardware_model": _sysctl_identity("hw.model"),
            "power_policy": power_policy,
            "sampling_interval_ms": SAMPLING_INTERVAL_MS,
            "estimator_revision": RESIDUAL_REGION_METHOD,
            "pulse_protocol_id": PROTOCOL_ID,
        }
        mx = importlib.import_module("mlx.core")
        planned_t1 = _planned_t1_bindings(
            planned_epoch=planned_epoch,
            sampler_binary=SAMPLER_BINARY,
            mlx_version=getattr(mx, "__version__", None),
        )
    except Exception as exc:  # noqa: BLE001 - one named desk derivation boundary
        raise NightInputsRefusal(
            f"machine vector derivation failed: {type(exc).__name__}: {exc}"
        ) from exc
    _refuse_incomplete_vector("identity epoch", planned_epoch, IDENTITY_EPOCH_FIELDS)
    _refuse_incomplete_vector("t1 bindings", planned_t1, T1_FIELDS)
    return planned_epoch, planned_t1


def _refuse_incomplete_vector(
    label: str, vector: Mapping[str, Any], fields: tuple[str, ...]
) -> None:
    """Refuse a vector the night's reserve step would refuse to record."""

    if set(vector) != set(fields):
        missing = sorted(set(fields) - set(vector))
        extra = sorted(set(vector) - set(fields))
        raise NightInputsRefusal(
            f"{label} keys are not exactly the expected fields "
            f"(missing={missing}, extra={extra})"
        )
    empty = sorted(field for field in fields if vector[field] in (None, ""))
    if empty:
        raise NightInputsRefusal(
            f"{label} fields are empty on this machine: {empty}; the night's "
            "reserve step refuses an empty binding, so fix the machine read "
            "(an absent MLX or an unreadable sampler is the usual cause)"
        )


def _stale_identity_fields(
    planned_epoch: Mapping[str, Any], acceptance_path: Path
) -> list[str]:
    """Name the identity fields that differ from the acceptance's epoch.

    The comparison is the live preflight's own: it refuses with
    ``acceptance_artifact_epoch_mismatch`` and the field list when this
    machine no longer matches the acceptance, and returns a screen value when
    it still does.  Returning normally therefore means NOTHING is stale.
    """

    from scripts.validate_powermetrics_fiducial import (  # noqa: PLC0415
        _AcceptancePreflightError,
        _derive_preflight_systematic_screen_s,
    )

    try:
        _derive_preflight_systematic_screen_s(
            planned_epoch, acceptance_path=acceptance_path
        )
    except _AcceptancePreflightError as exc:
        if getattr(exc, "reason", None) != "acceptance_artifact_epoch_mismatch":
            raise NightInputsRefusal(
                f"the acceptance at {acceptance_path} could not be read as an "
                f"issued artifact ({exc}), so no stale field can be "
                "established; name a readable issued acceptance with "
                "--acceptance"
            ) from exc
        stale = exc.context.get("stale_fields")
        if not stale:
            raise NightInputsRefusal(
                "the acceptance preflight reported an epoch mismatch without "
                "naming a field; refusing rather than guessing"
            ) from exc
        return sorted(str(field) for field in stale)
    raise NightInputsRefusal(
        "no identity field differs from the acceptance's epoch at "
        f"{acceptance_path}: this machine still matches the acceptance in "
        "force, so this is an ORDINARY night, not a derivation night: the "
        "writer's --derivation-only mode would refuse these inputs at d01 "
        "with the settle already spent. Run the ordinary window path instead"
    )


def _resolved_out_dir(raw: str) -> Path:
    out_dir = Path(raw).expanduser().absolute()
    if not out_dir.is_dir():
        raise NightInputsRefusal(
            f"--out-dir {out_dir} is not an existing directory; create the "
            "night root first, so that this script never invents the custody "
            "location the night's evidence is filed under"
        )
    return out_dir


def _refuse_overwrite(paths: tuple[Path, ...], *, force: bool) -> None:
    if force:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise NightInputsRefusal(
            f"refusing to overwrite {existing}; a night may already be pinned "
            "to those bytes. Pass --force only when you intend to invalidate "
            "any wrapper already generated from them"
        )


def write_night_inputs(
    *, out_dir: Path, power_policy: str, acceptance_path: Path, force: bool
) -> dict[str, Any]:
    """Derive, check, and write both inputs; return what was written."""

    if not power_policy or not power_policy.strip():
        raise NightInputsRefusal(
            "--power-policy is empty; the identity epoch's power_policy field "
            f"must be a non-empty value (the chain captures under "
            f"{CHAIN_POWER_POLICY!r})"
        )
    planned_epoch, planned_t1 = _derive_planned_vectors(power_policy)
    stale_fields = _stale_identity_fields(planned_epoch, acceptance_path)
    identity_path = out_dir / IDENTITY_EPOCH_NAME
    t1_path = out_dir / T1_BINDINGS_NAME
    _refuse_overwrite((identity_path, t1_path), force=force)
    identity_bytes = _json_bytes(planned_epoch)
    t1_bytes = _json_bytes(planned_t1)
    # Both files are written only after every refusal has passed, so a refusal
    # never leaves half a pair behind for a later run to pin.
    identity_path.write_bytes(identity_bytes)
    t1_path.write_bytes(t1_bytes)
    return {
        "identity_epoch": planned_epoch,
        "t1_bindings": planned_t1,
        "identity_path": identity_path,
        "t1_path": t1_path,
        "identity_sha256": _sha256_bytes(identity_bytes),
        "t1_sha256": _sha256_bytes(t1_bytes),
        "stale_fields": stale_fields,
        "acceptance_path": acceptance_path,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="write_derivation_night_inputs.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog=(
            "Output (paste both lines into the arm materials):\n"
            "  IDENTITY_EPOCH_JSON=<path> sha256=<64 hex>\n"
            "  T1_BINDINGS_JSON=<path> sha256=<64 hex>\n"
            "\n"
            "Then hand those two paths to scripts/gen_derivation_night.py as\n"
            "--identity-epoch-json and --t1-bindings-json.\n"
        ),
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help=(
            "Existing night root the two files are written into "
            f"(as {IDENTITY_EPOCH_NAME} and {T1_BINDINGS_NAME})."
        ),
    )
    parser.add_argument(
        "--power-policy",
        default=CHAIN_POWER_POLICY,
        help=(
            "Value of the identity epoch's power_policy field: the machine "
            "power setting the night captures under. The derivation chain "
            f"captures under {CHAIN_POWER_POLICY!r} and the wrapper generator "
            "refuses any other value (default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--acceptance",
        default=str(DEFAULT_ACCEPTANCE_BOUND_PATH),
        help=(
            "Acceptance artifact this machine is compared against, to report "
            "the STALE FIELDS - the identity fields whose value here differs "
            "from that artifact's identity epoch. Read for that diagnostic "
            "only; it is never written and never pinned into the night. A "
            "derivation night requires at least one stale field, so this "
            "script refuses when none differ (default: the active acceptance, "
            "%(default)s)."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite the two files if they already exist. Without it an "
            "existing file is a refusal, because a wrapper may already pin "
            "its digest."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        out_dir = _resolved_out_dir(args.out_dir)
        written = write_night_inputs(
            out_dir=out_dir,
            power_policy=args.power_policy,
            acceptance_path=Path(args.acceptance).expanduser().absolute(),
            force=bool(args.force),
        )
    except NightInputsRefusal as refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 2
    print(
        "stale identity fields vs "
        f"{written['acceptance_path']}: {', '.join(written['stale_fields'])}"
    )
    print(f"IDENTITY_EPOCH_JSON={written['identity_path']} "
          f"sha256={written['identity_sha256']}")
    print(f"T1_BINDINGS_JSON={written['t1_path']} sha256={written['t1_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
