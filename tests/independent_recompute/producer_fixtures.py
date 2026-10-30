"""RC-CMP-10: fixture values built by L9's own producers, never typed by hand (synthetic inputs only).

The comparator imports no repository code; its tests may. Each value here comes out of the producer that prints
it in a real run: the history lines from disclosures._history_lines over attempt records shaped from a window index,
and the p42 refusal code from the paper-reported-energy issuer on the synthetic pack of tests/b5_analysis.
"""
import functools
from types import SimpleNamespace


def attempt_record(entry, *, bracket=None, g10_codes=None, collected=12, planned=12):
    """An attempt record (b5_analysis/archive.AttemptRecord's fields _history_lines reads) for one index entry."""
    harvested = entry["entry_kind"] != "no_archive"
    return SimpleNamespace(
        entry=SimpleNamespace(pack=entry["pack"], attempt=entry["attempt"], plan_id=entry["plan_id"], seal=entry["seal"],
                              cause_key=entry.get("cause_key"), g10_requested=entry.get("g10_requested", False),
                              g10_redraw_cycles=entry.get("g10_redraw_cycles")),
        kind="harvested" if harvested else "no_archive", verdict=entry["verdict"],
        yield_counts={"window": {"succeeded": collected, "planned": planned}} if harvested else None,
        flags_by_family={}, reference_source=None, g10_codes=dict(g10_codes or {}), calibration_bracket=bracket)


def history_lines(entries, **records):
    """disclosures._history_lines over the index's attempts (records: plan_id -> attempt_record keywords)."""
    from joulewise.b5_analysis import disclosures
    result = {"block_lines": []}
    disclosures._history_lines(result, None, [attempt_record(entry, **records.get(entry["plan_id"], {}))
                                              for entry in entries])
    return result["block_lines"]


@functools.lru_cache(maxsize=None)
def p42_refusal_code():
    """The code the issuer prints for a refused p42 reported cell (tests/b5_analysis/test_issuer.py T12's path)."""
    from tests.b5_analysis import fixtures_s8 as s8
    pack = s8.synthetic_pack()
    with s8.pack_seams(pack):
        value = s8.project(pack)
    (code,) = {row["code"] for row in value["refused_cells"] if "-prefill-p42-" in row["cell_id"]}
    return code
