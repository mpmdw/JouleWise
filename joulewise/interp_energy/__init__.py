"""Interpretability/energy desk tools, exposed as lazy module namespaces.

Use ``interp_energy.forced_decode.replay`` and the other module APIs documented
in README.md. Importing or discovering these namespaces requires no numerical
backend and starts no collectors.
"""

from importlib import import_module

__all__ = (
    "behaviour_channel", "capture_hooks", "edit_frontier", "forced_decode", "lockin",
    "operand_stats", "power", "rail_data_dependence", "reference", "weight_edits",
)


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f".{name}", __name__)
    globals()[name] = module
    return module


def __dir__():
    return sorted(set(globals()) | set(__all__))
