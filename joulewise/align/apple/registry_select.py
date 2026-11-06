"""Narrow ALIGN v4 registry selector (WP14(c))."""
import json


def registry_for_config(config):
    """Return a gate registry only for an ALIGN episode gate map; never raise."""
    try:
        if config.workload_profile.name != 'align_episode':
            return None
        spec = json.loads(config.workload_profile.prompt_text or '')
        thermal = spec.get('thermal') if isinstance(spec, dict) else None
        if (not isinstance(thermal, dict) or not isinstance(thermal.get('sensors'), dict)):
            return None
        from joulewise.align.apple.thermal_gates import ThermalRegistry
        return ThermalRegistry()
    except Exception:
        return None
