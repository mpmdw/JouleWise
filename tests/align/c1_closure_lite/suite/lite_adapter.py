"""Small observation helpers for a candidate's check_view and exercise functions."""


def _observe(invoke):
    entries = 0

    def entered():
        nonlocal entries
        entries += 1

    decision = invoke(entered)
    return decision, entries


def view_decision(preflight):
    """preflight(entered) calls the real closure primitive and returns 'admit' or 'refuse'."""
    decision, entries = _observe(preflight)
    return {"decision": decision, "host": entries}


def consumer_decisions(install, direct_arm):
    """Run independent consumers; each fixture's first host stand-in calls entered()."""
    cli, cli_entries = _observe(install)
    arm, arm_entries = _observe(direct_arm)
    return {"cli": cli, "arm": arm, "host_cli": cli_entries, "host_arm": arm_entries}
