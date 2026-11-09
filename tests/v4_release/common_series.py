"""One synthetic v4 series written in BOTH builds' input layouts. Synthetic only; no real data.

The recompute's own writer (``tests/independent_recompute_v4/synth.py`` at the pinned recompute commit)
supplies the member model, the powermetrics frames, the sidecar rows and the KM003C stream. This module
only adds what neither build's generator has:

- the R15 22-member allocation (and the R20 24-member escalation) instead of synth.py's simplified
  roster, because the engine refuses any other roster;
- a zero-capture attempt and its retry of the same slot;
- the engine's raw-source manifest (``joulewise.align_v4.analysis_input.v1``, ENGINE-sol.md "Raw export
  adapter interface") pointing at the SAME raw plist and meter bytes the recompute reads;
- a crosswalk (structure only) from the engine's (attempt, ordinal) to the recompute's
  (window_id, run_id).

Where the two layouts disagree about a field's name or shape (``EXPORT_NOTES``), each build gets the
layout its own document specifies. Those are exporter-contract items for the lead, not computations.
"""
import hashlib
import json
import math
from pathlib import Path
import random

NS = 1_000_000_000
PAIRS = ("spam_filter_update", "bank_transfer_2")
SHORT = {"spam_filter_update": "spam", "bank_transfer_2": "bank"}
D_MODEL, A_MODEL = "qwen3.8-27b", "qwen3-30b-a3b"
ORDER = tuple(f"C{i}" for i in range(1, 9)) + tuple(f"T{i}" for i in range(1, 4))
RESERVES = tuple(f"C{i}" for i in range(9, 15))    # R24: admitted in frozen order, only to replace a bar
# The R24 allocation (configs/campaigns/align_v4/series/series_manifest.json at origin/align/2026-11-08-v4-r11,
# sha256 21313cc2...), kept byte for byte beside this module.
ALLOCATION = Path(__file__).resolve().parent / "fixtures" / "series_manifest_r24.json"
ALLOCATION_SHA256 = "21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c"
RECORDS_SCHEMA = "joulewise.align.records.v1"
ENGINE_SCHEMA = "joulewise.align_v4.analysis_input.v1"
COHORT = dict(identity=dict(model_source="synthetic/Qwen", model_revision="synthetic",
                            runtime_sha256="a" * 64, execution_policy_sha256="b" * 64),
              configuration=dict(max_episode_decode_tokens=16384, deadman_s=1200.0, max_tokens=4096, max_turns=12))
EXPORT_NOTES = (
    "R23: the export uses production sensor keys policy.sensors.{s_fast, s_slow} in both layouts",
    "R23: anchor run ids (and a retried slot's repeated ids) are series-unique '<window_id>:<run_id>' in the "
    "recompute layout; the engine keeps the R15 ids; the crosswalk maps them",
    "R23: the W1 window record carries sentinel_ordinals [5, 17]; the recompute checks them against R15",
    "R24 allocation (r23j): the engine binds the analysis-form manifest (series_source: W1, C1-C14, T1-T3 slots "
    "with run ids); the recompute binds the frozen native manifest (allocation_source, sha256 21313cc2...)",
    "clock stamps: the engine takes ClockStamp seconds, the recompute paired_clock_stamps_ns; every synthetic "
    "stamp is a whole second, so both are exact",
    "U3 pilot evidence: the engine takes energy pairs, the recompute relative differences; pairs are written "
    "as 1000*(1 -/+ r/2), whose (b-a)/mean is r",
    "W1 sentinels 5/17 energies: the engine takes them as reference input; the recompute derives them from "
    "the W1 members. The synthetic power profile makes the turn-owned energy exact by construction",
    "reasoning: the engine reads Episode hidden_tokens; the recompute reads turns[].reasoning_tokens",
)


def leading_seed(value):
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def episode_seed(model, pair, index):
    return leading_seed(["align-p4-v1", model, "thinking_on", "shade/" + pair, index])


def r15_roster(window, escalated=False):
    """R15 allocation (RUN_STATE 226), enumerated for the fixture. The engine re-checks it field by field."""
    number = int(window[1:])
    # R15 seeds: C1-C8 2-65, T1-T3 66-89; R24 reserves C9-C14 100-147 per pair (C9 100-107, ...).
    start = (2 + 8 * (number - 1) if window[0] == "C" and number <= 8 else
             100 + 8 * (number - 9) if window[0] == "C" else 66 + 8 * (number - 1))
    nxt = dict.fromkeys(PAIRS, start)
    first = PAIRS[(number - 1) % 2]
    second = PAIRS[1] if first == PAIRS[0] else PAIRS[0]
    anchors = [(PAIRS[0], "benign"), (PAIRS[1], "sabotage"), (PAIRS[0], "sabotage"), (PAIRS[1], "benign")]
    rows = []
    for o in range(1, 23):
        held = 6 <= o <= 21
        pair, cond = (anchors[o - 1] if o <= 4 else (PAIRS[0], "benign") if not held else
                      (first if o % 2 == 0 else second, "sabotage" if o in (9, 18) else "benign"))
        model = A_MODEL if o <= 4 else D_MODEL
        index = nxt[pair] if held else 1
        if held:
            nxt[pair] += 1
        stage = "a" if o <= 11 else "b"
        run = (f"align-pilot-v3-episodes-a-e{o:02}" if o <= 4 else
               f"align-v4-{window.lower()}-episodes-{stage}-e{o:02}")
        rows.append(dict(ordinal=o, task_pair=pair, condition=cond, model_id=model, seed_index=index,
                         expected_episode_seed=episode_seed(model, pair, index), held_out=held,
                         series_role="anchor" if o <= 4 else "sentinel" if not held else
                         "sabotage" if cond == "sabotage" else "benign", run_id=run))
    if escalated:
        for o in (23, 24):
            rows.append({**rows[4], "ordinal": o, "series_role": "supplemental_sentinel",
                         "run_id": f"align-v4-{window.lower()}-episodes-b-e{o:02}"})
    return rows


W1_ROWS = (  # protocol v4 W1 roster (as in synth.W1_ROSTER): ordinal, kind, model, pair, condition, contrast
    (1, "anchor", A_MODEL, PAIRS[0], "benign", None), (2, "anchor", A_MODEL, PAIRS[1], "sabotage", None),
    (3, "anchor", A_MODEL, PAIRS[0], "sabotage", None), (4, "anchor", A_MODEL, PAIRS[1], "benign", None),
    (5, "sentinel", D_MODEL, PAIRS[0], "benign", None), (6, "contrast", A_MODEL, PAIRS[0], "sabotage", ("X", "G")),
    (7, "contrast", A_MODEL, PAIRS[0], "benign", ("Y", "S")), (8, "development", D_MODEL, PAIRS[1], "benign", None),
    (9, "contrast", A_MODEL, PAIRS[0], "sabotage", ("X", "S")), (10, "contrast", A_MODEL, PAIRS[0], "benign", ("Y", "G")),
    (11, "development", D_MODEL, PAIRS[0], "sabotage", None), (12, "contrast", A_MODEL, PAIRS[0], "benign", ("Y", "G")),
    (13, "contrast", A_MODEL, PAIRS[0], "sabotage", ("X", "S")), (14, "development", D_MODEL, PAIRS[1], "sabotage", None),
    (15, "contrast", A_MODEL, PAIRS[0], "benign", ("Y", "S")), (16, "contrast", A_MODEL, PAIRS[0], "sabotage", ("X", "G")),
    (17, "sentinel", D_MODEL, PAIRS[0], "benign", None), (18, "development", D_MODEL, PAIRS[1], "benign", None))


def w1_roster():
    rows = []
    for o, kind, model, pair, cond, contrast in W1_ROWS:
        # R24 allocation (series manifest W1 rows): contrast X seeds 16, Y seeds 14; ordinal 18 seed 93.
        index = 93 if o == 18 else ({"X": 16, "Y": 14}[contrast[0]] if contrast else 1)
        row = dict(ordinal=o, task_pair=pair, condition=cond, model_id=model, seed_index=index,
                   expected_episode_seed=episode_seed(model, pair, index), held_out=False,
                   series_role=kind, run_id=f"align-v4-w1-episodes-e{o:02}")
        if contrast:
            row["contrast"] = dict(template=contrast[0], arm=contrast[1], stage=0 if o <= 11 else 1)
        rows.append(row)
    return rows


A37_EPOCH_S = 9_000_000_000        # float seconds grid 1.907 us: interior seams 1,907/1,908 ns (> 1 us, kept)
A37_SNAP_EPOCH_S = 4_300_000_000   # float seconds grid 954 ns: interior seams 953/954 ns (<= 1 us, snapped)


def default_plan(zero_capture=True, escalated=True, a37=True, screens=True, probes=False, bar=True):
    """W1, C1-C8 and T1-T3. C3's and T2's first attempts are zero-capture refusals, each retried in its slot;
    T3 is escalated to 24 members.

    Screen fixtures (``screens``, R23 clarifications c-e):
    - W1 anchor 2 carries a battery B code (a charging flag): it fails the member-eligibility screen, so
      W1 leaves the anchor sigma_w table (``W1_anchor_block: excluded:B``) like any C/T window (c);
    - T1 ordinal 6 and T2's retry ordinal 6 carry a battery B code (``battery.member_span``), with T2's
      zero-capture attempt between them: the B run must skip the zero-capture attempt (d);
    - the zero-capture attempts' members are not captured; the retry's exclusions come only from the
      counted attempt (e).

    A37 seam fixtures (``a37``, permanent): C5, C6 and C7 have non-integer sample placement (frame elapsed
    values of 1 s + 333 ns and 1 s + 777 ns, alternating). Under the A21 float support rule with exact
    seconds -> ns (lead ruling on P2):
    - C5 at the 2026 epoch: interior gaps of 238/239 ns (<= 1 us: snapped);
    - C7 at a synthetic 4.3e9 s epoch (float grid 954 ns): seams of 953/954 ns (<= 1 us: snapped);
    - C6 at a synthetic 9e9 s epoch (float grid 1.907 us): gaps of 1,907/1,908 ns (> 1 us: uncovered owned
      time, A2(4), so every C6 member is excluded).
    Raw bytes cannot place a > 1 us seam at a 2026 epoch under the A21 rule (start = end - own elapsed),
    hence the epochs. ``seams.json`` counts them.

    A2(4) owned-time fixtures (``screens``): C8 ordinal 12 sits at the 9e9 s epoch with jittered supports
    inside its first G1 gate only (> 1 us seams in gate time: eligible, disclosed); W1 ordinal 8 loses its
    leading power frames so its first turn starts before the first support (edge partial coverage of an
    owned segment: excluded).

    Structural bar fixture (``bar``, R22-2 / R24): C4 ordinal 7 (D benign) releases G0 4 C warm, so C4's D
    model-window fails U2(a); the export declares C4 ``barred: u1_u3_fail`` (reproducible on both sides); C4
    is barred, contributes nothing, does not count, and the reserve C9 (seeds 100-107 per pair) runs after C8
    to replace it. With C3's zero-capture retry this is the bar-plus-reserve scenario.

    Every export binds the full 18-window R24 allocation (``ALLOCATION``, sha256 21313cc2...) and, for every
    captured C attempt, a GO completed-chain terminal result by digest (``terminal_result_source``).

    Probe plan (``probes``): the same series, with W1 anchor 2's B code replaced by a G1 timeout that stops
    its episode (P: "Timeout stops the episode (X2)"; lead ruling on P1: X2 is re-derived); W1 contrast
    ordinal 6 is not token-identical, so the A19 contrast is unavailable (7 runs:
    ``insufficient_contrast_runs``); and the U5 references carry a negative slope and delta = 2 C (F7)."""
    plan = [dict(window="W1", attempt=1, zero_capture=False, escalated=False,
                 battery_b=[2] if screens and not probes else [], g1_timeout=[2] if probes else [],
                 late_first_support=[8] if screens else [], divergent_contrast=[6] if probes else [])]
    order = list(ORDER)
    if bar:
        order.insert(order.index("C8") + 1, RESERVES[0])
    for w in order:
        if w in ("C3", "T2") and zero_capture:
            plan.append(dict(window=w, attempt=1, zero_capture=True, escalated=False))
            plan.append(dict(window=w, attempt=2, zero_capture=False, escalated=False,
                             battery_b=[6] if screens and w == "T2" else []))
        else:
            step = dict(window=w, attempt=1, zero_capture=False, escalated=escalated and w == "T3",
                        battery_b=[6] if screens and w == "T1" else [])
            if a37 and w == "C5":
                step["seams"] = True
            if a37 and w == "C6":
                step["seams"] = True
                step["epoch_s"] = A37_EPOCH_S
            if a37 and w == "C7":
                step["seams"] = True
                step["epoch_s"] = A37_SNAP_EPOCH_S
            if bar and w == "C4":
                step["g0_warm"] = [7]
                step["declared_bar"] = "u1_u3_fail"
            if screens and w == "C8":
                # A2(4) at owned-time level (lead ruling): ordinal 12 has > 1 us seams only inside a G1 gate
                # (eligible). Its opposite, a first turn that starts before the first power support (excluded),
                # is W1 ordinal 8: that member's uncovered G0 time also fails U1(c), which would bar a C window.
                step["gate_seam"] = [12]
            plan.append(step)
    return plan


JITTER_NS = (333, 777)
_ELAPSED = b"\n\t<key>elapsed_ns</key>\n\t<integer>1000000000</integer>"


def _jitter_supports(base, stats):
    """Rewrite each frame's top-level elapsed_ns to 1 s + jitter, then count the
    interior seams the A21 support rule gives (first sample ends at the anchor, each later end adds its
    own elapsed in float seconds, start = end - elapsed, seconds -> ns by round)."""
    raw = base / "raw" / "powermetrics.plist"
    frames = raw.read_bytes().split(b"\x00")
    out, elapsed = [], []
    for i, f in enumerate(frames):
        if not f:
            out.append(f)
            continue
        e = NS + JITTER_NS[len(elapsed) % len(JITTER_NS)]
        assert f.count(_ELAPSED) == 1
        out.append(f.replace(_ELAPSED, _ELAPSED.replace(b"1000000000", str(e).encode())))
        elapsed.append(e)
    raw.write_bytes(b"\x00".join(out))
    anchor = json.loads((base / "metadata.json").read_text())["uncertainty_evidence"]["clock_anchor"][
        "first_sample_end_point_epoch_s"]
    stats = stats or {"gap_le_1us": 0, "gap_gt_1us": 0, "overlap_le_1us": 0, "overlap_gt_1us": 0,
                      "max_abs_seam_ns": 0}
    cumulative, prev_end = 0.0, None
    for i, e in enumerate(elapsed):
        length = e / NS
        if i:
            cumulative += length
        end_s = anchor + cumulative
        start, end = _exact_ns(end_s - length), _exact_ns(end_s)
        if prev_end is not None and start != prev_end:
            d = abs(start - prev_end)
            stats[("gap" if start > prev_end else "overlap") + ("_le_1us" if d <= 1000 else "_gt_1us")] += 1
            stats["max_abs_seam_ns"] = max(stats["max_abs_seam_ns"], d)
        prev_end = end
    return stats


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
            + "\n").encode()


def write_series(root, synth, *, plan=None, seed=7, period_ns=NS, saboteur_extra=25.0, sigma=3.0,
                 beta=(40.0, 0.004, 0.25, 2e-6, 1e-7), turns=(3, 6), u5_negative=None, u5_delta_slow_c=None):
    """Write ``root/recompute`` (RECOMPUTE-opus.md layout), ``root/engine-input.json`` (engine raw-source
    manifest, its sources under ``root``) and ``root/crosswalk.json``. Returns the crosswalk."""
    root = Path(root)
    rec = root / "recompute"
    plan = plan or default_plan()
    # F7 probe: the U5 references with a negative slope and delta = 2 C (default: the probe plan's choice).
    probes = any(step.get("g1_timeout") for step in plan)
    u5_negative = probes if u5_negative is None else u5_negative
    u5_delta = (2.0 if probes else 1.0) if u5_delta_slow_c is None else u5_delta_slow_c
    rng = random.Random(seed)
    template = synth.FrameTemplate(n_tasks=0, seed=seed, clusters=0)
    clock = 0
    series = {"schema": "joulewise.v4_recompute_input.series.v1", "windows": [],
              "h_star_grid": [128, 256, 384, 512, 768, 1024, 1536, 2048]}       # R26 (1), registered text
    engine_windows, crosswalk, used_rec_runs = [], [], set()
    manifest_slots = {}
    w1_sentinel_j = {}
    seam_stats = {}
    for step in plan:
        wid, attempt = step["window"], step["attempt"]
        role = "W1" if wid == "W1" else ("calibration" if wid[0] == "C" else "test")
        rec_wid = wid if not step["zero_capture"] else f"{wid}-z{attempt}"
        slots = w1_roster() if wid == "W1" else r15_roster(wid, escalated=step["escalated"])
        # R23 export contract, engine layout: anchor run ids are "<window_id>:<run_id>" with the engine's
        # window name (engine-r23b strips a matching prefix for the R15 roster check).
        slots = [dict(s, run_id=f"{wid}:{s['run_id']}", local_run_id=s["run_id"]) if s["series_role"] == "anchor"
                 else dict(s, local_run_id=s["run_id"]) for s in slots]
        series["windows"].append({"window_id": rec_wid, "role": role})
        w_start = clock
        rec_members, identity, engine_records, battery_codes = [], {}, [], {}
        for slot in slots:
            rid = slot["run_id"]                  # engine-layout id
            local = slot["local_run_id"]          # R15 id
            # R23 export contract: anchor run ids are strictly series-unique "<window_id>:<run_id>" (in the
            # recompute layout the window id is the attempt's record id, e.g. "C3-z1"); non-anchor ids are
            # never prefixed, and repeat only across the attempts of a retried slot.
            rec_rid = f"{rec_wid}:{local}" if slot["series_role"] == "anchor" else local
            if slot["series_role"] == "anchor" and rec_rid in used_rec_runs:
                raise ValueError("anchor run id not series-unique: " + rec_rid)
            used_rec_runs.add(rec_rid)
            short = SHORT[slot["task_pair"]]
            kind = {"supplemental_sentinel": "sentinel"}.get(slot["series_role"], slot["series_role"])
            model = "D" if slot["model_id"] == D_MODEL else "30B"
            rrow = dict(ordinal=slot["ordinal"], run_id=rec_rid, kind=kind, model=model, pair=short,
                        condition=slot["condition"])
            if model == "D":
                rrow["seed_index"] = slot["seed_index"]
            if "contrast" in slot:
                rrow["contrast"] = slot["contrast"]
            rec_members.append(rrow)
            crosswalk.append(dict(window=wid, attempt_id=f"{wid}#{attempt}", ordinal=slot["ordinal"],
                                  engine_run_id=rid, recompute_window_id=rec_wid, recompute_run_id=rec_rid,
                                  pair=short, condition=slot["condition"], model=model,
                                  role=slot["series_role"], captured=not step["zero_capture"],
                                  seed_index=slot["seed_index"], contrast=slot.get("contrast")))
            if step["zero_capture"]:
                engine_records.append(dict(run_id=rid, captured=False))
                continue
            n_turns = rng.randrange(turns[0], turns[1] + 1)
            identical = None
            if slot["series_role"] in ("sentinel", "supplemental_sentinel"):
                identical, n_turns = 5, 4
            elif "contrast" in slot:
                identical, n_turns = (16 if slot["contrast"]["template"] == "X" else 14), 3
                if slot["ordinal"] in step.get("divergent_contrast", []):
                    identical = None          # A19 probe: this contrast run is not token-identical
            if identical is not None:
                identity[rec_rid] = "identical"
            m = synth.Member(rec_rid, short, slot["condition"], kind, model, clock, rng, n_turns,
                             beta, sigma, period_ns, template, identical_to=identical)
            if slot["condition"] == "sabotage" and saboteur_extra and model == "D":
                for t in m.turns:
                    t["_energy"] += saboteur_extra
            if "contrast" in slot and slot["contrast"]["arm"] == "S":
                for t in m.turns:
                    t["_energy"] += 8.0
            ident = hashlib.sha256((f"traj-{identical}" if identical is not None else local).encode()).hexdigest()
            extra = {"identity_sha256": ident, "seed": slot["expected_episode_seed"],
                     "cohort_sha256": synth.COHORT}
            gate_seam = slot["ordinal"] in step.get("gate_seam", [])
            epoch_s = A37_EPOCH_S if gate_seam else step.get("epoch_s", synth.EPOCH0_S)
            synth.write_member(rec, rec_wid, m, epoch_s * NS, extra=extra)
            base = rec / "windows" / rec_wid / "members" / rec_rid
            if step.get("seams"):
                seam_stats[f"{wid}#{attempt}"] = _jitter_supports(base, seam_stats.get(f"{wid}#{attempt}"))
            if gate_seam:
                seam_stats[f"{wid}#{attempt}:o{slot['ordinal']}"] = _gate_seam(base, m)
            if slot["ordinal"] in step.get("late_first_support", []):
                _late_first_support(base, m)
            # The recompute layout's episode gets the production gate "reference" too (ignored there).
            ep_path = base / "outputs" / "align_episode.json"
            ep = json.loads(ep_path.read_text())
            g0 = ep["hardware"]["thermal"]["intervals"][0]
            if slot["ordinal"] in step.get("g0_warm", []):
                g0["release"]["slow_c"] += 4.0        # U2(a): G0 release range 4 C > 3 C -> U2 FAIL -> bar
            for g in ep["hardware"]["thermal"]["intervals"]:
                g["reference"] = dict(g0["release"])
            if slot["ordinal"] in step.get("g1_timeout", []):
                # A G1 timeout stops the episode (P: "Timeout stops the episode (X2)"): the record keeps the
                # turns before the timed-out gate and ends at the gate's end.
                ivs = ep["hardware"]["thermal"]["intervals"]
                g1 = next(g for g in ivs if g["kind"] == "G1")
                g1["outcome"] = "timeout"
                ep["turns"] = [t for t in ep["turns"] if t["index"] < g1["turn"]]
                ep["hardware"]["thermal"]["intervals"] = [g for g in ivs if g["kind"] == "G0" or g["turn"] <= g1["turn"]]
                ep["end_ns"] = g1["end_ns"]
                ep["hardware"]["registered_span_ns"] = [ep["start_ns"], ep["end_ns"]]
            # The export carries production's clock offset (t_monotonic = t_epoch + offset_ns); every synthetic
            # stamp is exact, so offset = monotonic - epoch.
            st = ep["hardware"]["paired_clock_stamps_ns"][0]
            ep["hardware"]["production_offset_ns"] = st["monotonic_before_ns"] - st["epoch_ns"]
            ep_path.write_text(json.dumps(ep, indent=1, sort_keys=True) + "\n")
            meta = json.loads((base / "metadata.json").read_text())
            engine_records.append(_engine_member(root, base, slot, ep, meta, ident, step, wid, w_start))
            if slot["ordinal"] in step.get("battery_b", []):
                engine_records[-1]["battery"] = dict(engine_records[-1]["battery"], flags=["battery.member_span"])
                battery_codes[rec_rid] = ["battery.member_span"]
            if wid == "W1" and slot["ordinal"] in (5, 17):
                w1_sentinel_j[str(slot["ordinal"])] = _owned_gpu_j(m)
            clock = m.end_ns + 60 * NS
        if step["zero_capture"]:
            clock += 60 * NS
        streams = {}
        meter_rel = None
        if not step["zero_capture"]:
            mpath = rec / "windows" / rec_wid / "meter" / "km003c-0.jsonl"
            synth.write_meter(mpath, (w_start - 20 * NS, clock))
            streams["km003c-0.jsonl"] = synth.sha256_file(mpath)
            meter_rel = dict(path=str(mpath.relative_to(root)), sha256=streams["km003c-0.jsonl"])
            for rec_row, er in zip(rec_members, engine_records):
                if er.get("captured") and rec_row["condition"] == "benign":
                    er["dc_streams"] = [meter_rel]
        bound = {}
        terminal_ref = None
        if role == "calibration" and not step["zero_capture"]:
            # R22-2 / r23j export: a captured C attempt binds its completed-chain terminal result by digest.
            tdoc = canonical(dict(verdict=step.get("terminal_verdict", "GO"),
                                  chain_exit_code=step.get("terminal_exit", 0)))
            tpath = root / "terminal" / f"{wid}-a{attempt}.json"
            tpath.parent.mkdir(parents=True, exist_ok=True)
            tpath.write_bytes(tdoc)
            rpath = rec / "windows" / rec_wid / "terminal_result.json"
            rpath.parent.mkdir(parents=True, exist_ok=True)
            rpath.write_bytes(tdoc)
            terminal_ref = dict(path=str(tpath.relative_to(root)), sha256=sha256_bytes(tdoc))
            bound["terminal_result_source"] = dict(path=str(rpath.relative_to(rec)), sha256=sha256_bytes(tdoc))
        if step.get("declared_bar"):
            bound["barred"] = step["declared_bar"]
        synth.dump(rec / "windows" / rec_wid / "window.json", {
            "schema": "joulewise.v4_recompute_input.window.v1", "window_id": rec_wid, "role": role,
            "members": rec_members, "adjudication": {"final": True, "excluded": {}}, "identity": identity,
            "battery": battery_codes, "meter": {"streams": streams}, "cohort_sha256": synth.COHORT,
            **({"sentinel_ordinals": [5, 17]} if wid == "W1" else {}),
            **({"slot": wid} if role == "calibration" else {}), **bound})
        raw_doc = canonical(dict(members=engine_records))
        raw_path = root / "engine" / f"{wid}-a{attempt}.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw_doc)
        manifest_slots[wid] = [{k: v for k, v in sl.items() if k not in ("contrast", "local_run_id")} for sl in slots]
        ewin = dict(window=wid, attempt_id=f"{wid}#{attempt}", status="final",
                    roster=[{k: v for k, v in s.items() if k not in ("contrast", "local_run_id")} for s in slots],
                    raw_source=dict(path=str(raw_path.relative_to(root)), sha256=sha256_bytes(raw_doc)))
        if terminal_ref:
            ewin["terminal_result_source"] = terminal_ref
        if step.get("declared_bar"):
            ewin["barred"] = step["declared_bar"]
        engine_windows.append(ewin)
    # R24 allocation: the frozen 18-window manifest, byte for byte, bound by digest in both layouts.
    alloc = ALLOCATION.read_bytes()
    target = rec / "allocation" / "series_manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(alloc)
    series["allocation_source"] = dict(path="allocation/series_manifest.json", sha256=sha256_bytes(alloc))
    synth.dump(rec / "series.json", series)
    pilot = [0.004, -0.006, 0.003, 0.005, -0.002, 0.001, -0.004]
    synth.dump(rec / "u3_bar.json", {"signed": True, "beta": 0.05, "N": 22, "f": 1.5, "r1_d_screen": 0.004,
                                     "pilot_relative_differences": pilot})
    designed = [(38.0, 38.0, 1500.0), (40.0, 40.0, 1501.0), (42.0, 42.0, 1502.5)]
    if u5_negative:
        designed = [(38.0, 38.0, 1502.5), (40.0, 40.0, 1501.0), (42.0, 42.0, 1500.0)]
    synth.dump(rec / "references.json", {"r1_replay_pair_j": [1500.0, 1510.0], "delta_slow_c": u5_delta,
                                         "r1_designed_start_states": [
                                             {"designed_slow_c": d, "g0_release_slow_c": g, "energy_j": e}
                                             for d, g, e in designed]})
    # Engine layout (engine-r23j io.load): the analysis-form R24 manifest, W1, C1-C14, T1-T3, each window's slots
    # as exported (anchors "<window>:" prefixed), unrun reserves from the frozen roster.
    order = ["W1", *[f"C{i}" for i in range(1, 15)], "T1", "T2", "T3"]
    eman = dict(windows=[dict(window=w, members=manifest_slots.get(w) or [
        dict(sl, run_id=f"{w}:{sl['run_id']}") if sl["series_role"] == "anchor" else sl
        for sl in r15_roster(w)]) for w in order])
    eman_bytes = canonical(eman)
    (root / "engine" / "series-manifest.json").write_bytes(eman_bytes)
    payload = dict(schema=ENGINE_SCHEMA, synthetic=True, cohort=COHORT, windows=engine_windows,
                   series_source=dict(path="engine/series-manifest.json", sha256=sha256_bytes(eman_bytes)),
                   u3_evidence=dict(pilot_pairs=[dict(session=f"synthetic-pilot-{i}", ordinals=[2, 7],
                                                      prespecified=True, token_identical=True,
                                                      energies_j=[1000.0 * (1 - r / 2), 1000.0 * (1 + r / 2)])
                                                 for i, r in enumerate(pilot)],
                                    frozen_before_W1=True,
                                    r1_d_screen=dict(token_identical=True, eligible=True, relative_difference=0.004)),
                   reference=dict(qualified=True, r1_replay_j=[1500.0, 1510.0], w1_sentinel_j=w1_sentinel_j),
                   r1_sensitivity=dict(states=[dict(token_identical=True, g0_slow_c=g, turn_owned_j=e,
                                                    designed_target_c=d) for d, g, e in designed],
                                       r1_replay_j=[1500.0, 1510.0], delta_slow_c=u5_delta),
                   delta_slow_c=1.0, u6_split_rule="within_pair_episode_order",
                   custody="synthetic only; no native qualification")
    (root / "engine-input.json").write_bytes(canonical(payload))
    doc = dict(schema="joulewise.v4_release.crosswalk.v1", synthetic=True, members=crosswalk,
               export_notes=list(EXPORT_NOTES))
    (root / "crosswalk.json").write_bytes(canonical(doc))
    (root / "seams.json").write_bytes(canonical(seam_stats))
    return doc


def _owned_gpu_j(m):
    """Turn-owned GPU J of a synthetic member: piecewise-constant power on whole-second samples (synth
    write_member), turn spans at the turn's mean power plus its own 2 s tool span at 2 W."""
    total = []
    for t in m.turns:
        dur = (t["end_ns"] - t["start_ns"]) // NS
        mw = t["_energy"] / ((t["end_ns"] - t["start_ns"]) / NS) * 1000
        total.extend([mw / 1000.0] * dur)
        total.extend([2.0] * 2)
    return math.fsum(total)


def _engine_member(root, base, slot, ep, meta, ident, step, wid, w_start):
    """The engine's raw-source row for one captured member, over the same raw files."""
    hw = ep["hardware"]
    th = hw["thermal"]
    policy = th["policy"]
    sensors = {"s_fast": policy["sensors"]["s_fast"], "s_slow": policy["sensors"]["s_slow"], "fan_keys": []}
    turns = []
    for t in ep["turns"]:
        turns.append(dict(index=t["index"], start_ns=t["start_ns"], end_ns=t["end_ns"],
                          context_tokens=t["context_tokens"], prefill_tokens=t["prefill_tokens"],
                          decode_tokens=t["decode_tokens"], hidden_tokens=t["reasoning_tokens"],
                          first_token_ns=t["first_token_ns"],
                          tool_calls=[dict(name=c["name"], start_ns=c["start_ns"], end_ns=c["end_ns"],
                                           args_bytes=c["args_bytes"], result_bytes=c["result_bytes"])
                                      for c in t["tool_calls"]]))
    intervals = []
    for g in th["intervals"]:
        stamp = dict(epoch_ns=g["start_ns"], monotonic_before_ns=g["start_ns"], monotonic_after_ns=g["start_ns"])
        intervals.append(dict(kind=g["kind"], start_ns=g["start_ns"], end_ns=g["end_ns"], turn=g["turn"],
                              outcome=g["outcome"], entry_stamp=stamp, exit_stamp=stamp,
                              exit_sample_ns=g["exit_sample_ns"], release=dict(g["release"]),
                              reference=dict(g["reference"])))
    # A captured anchor Episode keeps its local R15 id (engine-r23b binds it to the exported id).
    episode = dict(schema=RECORDS_SCHEMA, episode_id=slot["local_run_id"], task_pair="shade/" + slot["task_pair"],
                   condition=slot["condition"], agent_model=slot["model_id"], endpoint="mock",
                   seed=ep["seed"], clock_domain="host", start_ns=ep["start_ns"], end_ns=ep["end_ns"],
                   turns=turns, flags=list(ep["flags"]),
                   hardware=dict(thermal=dict(policy=dict(sensors=sensors, delta_fast_c=policy["delta_fast_c"],
                                                          delta_slow_c=policy["delta_slow_c"]),
                                              intervals=intervals, episode_reference=th["episode_reference"]),
                                 registered_span_ns=hw["registered_span_ns"], cache=hw["cache"]))
    ep_bytes = (json.dumps(episode, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ep_file = base / "engine-episode.json"
    ep_file.write_bytes(ep_bytes)
    raw = base / "raw" / "powermetrics.plist"
    rows = [json.loads(line) for line in (base / "outputs" / "align_thermal.jsonl").read_text().splitlines() if line]
    journal = [dict(kind="sample", monotonic_ns=r["monotonic_ns"],
                    finished=dict(monotonic_after_ns=r["monotonic_ns"]), sensors=r["sensors"], errors={})
               for r in rows]
    os_readings = [[r["monotonic_ns"], r["status"]["os_level"]] for r in rows]
    span = hw["registered_span_ns"]
    stamps = [dict(epoch_s=s["epoch_ns"] / NS, monotonic_before_s=s["monotonic_before_ns"] / NS,
                   monotonic_after_s=s["monotonic_after_ns"] / NS, wall_resolution_s=0.0,
                   monotonic_resolution_s=0.0) for s in hw["paired_clock_stamps_ns"]]
    offset_s = stamps[0]["epoch_s"] - stamps[0]["monotonic_before_s"]
    record = dict(run_id=slot["run_id"], captured=True, status="completed",
                  episode=dict(path=str(ep_file.relative_to(root)), sha256=sha256_bytes(ep_bytes)),
                  powermetrics=dict(path=str(raw.relative_to(root)), sha256=_sha256_file(raw)),
                  first_record_endpoint_s=meta["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"],
                  nominal_interval_ns=meta["sampling"]["power_period_ns"], stamps=stamps,
                  clock_evidence=dict(clock_anchor=dict(status="bounded", method="synthetic",
                                                        wall_minus_monotonic_lower_s=offset_s,
                                                        wall_minus_monotonic_upper_s=offset_s,
                                                        effective_clock_anchor_bound_s=1e-6)),
                  journal=journal, os_readings=os_readings,
                  registered_os_readings=[r for r in os_readings if span[0] <= r[0] <= span[1]],
                  registered_span_ns=span, identity_sha256=ident, offset_ns=hw["production_offset_ns"],
                  battery=dict(status="observed", flags=[], soc_pct=[100.0, 100.0], charger_w=[80.0, 80.0],
                               source_sha256="c" * 64),
                  cohort_identity=COHORT["identity"], configuration=COHORT["configuration"],
                  cache_statistics=dict(rebuilds=0, rewinds=0), member_span_ns=[ep["start_ns"], ep["end_ns"]],
                  turn_rows=[dict(generation=dict(
                      prompt_token_ids=[int(ident[2 * k:2 * k + 2], 16) for k in range(8)] + [t["index"]],
                      output_token_ids=[int(ident[2 * k + 16:2 * k + 18], 16) for k in range(8)] + [t["index"]]))
                      for t in ep["turns"]])
    if slot["series_role"] == "sentinel":
        record["identical_work_group"] = "sentinel"
    if "contrast" in slot:
        record.update(template=slot["contrast"]["template"], arm=slot["contrast"]["arm"],
                      stage=slot["contrast"]["stage"],
                      pilot7_token_identical=slot["ordinal"] not in step.get("divergent_contrast", []))
    return record


def _frames(raw):
    return [f for f in raw.read_bytes().split(b"\x00") if f]


def _write_frames(raw, frames):
    raw.write_bytes(b"".join(f + b"\x00" for f in frames))


def _gate_seam(base, m):
    """Jitter the frames strictly inside turn 1's G1 gate (elapsed 1 s + 333/777 ns) of a member placed at
    the 9e9 s epoch: the A21 rule then leaves > 1 us seams in gate time only; every frame elsewhere is 1 s."""
    raw = base / "raw" / "powermetrics.plist"
    frames = _frames(raw)
    ep = json.loads((base / "outputs" / "align_episode.json").read_text())
    g1 = next(g for g in ep["hardware"]["thermal"]["intervals"] if g["kind"] == "G1")
    span_start = m.start_ns - 10 * NS
    out, k = [], 0
    for i, f in enumerate(frames):
        end = span_start + (i + 1) * m.period_ns
        if g1["start_ns"] + 2 * NS <= end - m.period_ns and end <= g1["end_ns"] - 2 * NS:
            e = NS + JITTER_NS[k % 2]
            k += 1
            assert f.count(_ELAPSED) == 1
            f = f.replace(_ELAPSED, _ELAPSED.replace(b"1000000000", str(e).encode()))
        out.append(f)
    _write_frames(raw, out)
    return {"jittered_gate_frames": k, "g1_turn": g1["turn"]}


def _late_first_support(base, m):
    """Drop the leading frames so the first power support ends 2 s after turn 0 starts (edge partial
    coverage of an owned segment); the clock anchor moves to the new first frame's end."""
    raw = base / "raw" / "powermetrics.plist"
    frames = _frames(raw)
    ep = json.loads((base / "outputs" / "align_episode.json").read_text())
    t0 = ep["turns"][0]["start_ns"]
    span_start = m.start_ns - 10 * NS
    drop = (t0 + 2 * NS - span_start) // m.period_ns - 1
    _write_frames(raw, frames[drop:])
    meta_path = base / "metadata.json"
    meta = json.loads(meta_path.read_text())
    meta["uncertainty_evidence"]["clock_anchor"]["first_sample_end_point_epoch_s"] += drop * m.period_ns // NS
    meta_path.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")


def _exact_ns(x):
    """Seconds -> ns from the exact value (lead ruling on P2), half to even."""
    n, d = x.as_integer_ratio()
    q, r = divmod(n * NS, d)
    return q + (1 if 2 * r > d or (2 * r == d and q % 2) else 0)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
