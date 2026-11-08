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
RECORDS_SCHEMA = "joulewise.align.records.v1"
ENGINE_SCHEMA = "joulewise.align_v4.analysis_input.v1"
COHORT = dict(identity=dict(model_source="synthetic/Qwen", model_revision="synthetic",
                            runtime_sha256="a" * 64, execution_policy_sha256="b" * 64),
              configuration=dict(max_episode_decode_tokens=16384, deadman_s=1200.0, max_tokens=4096, max_turns=12))
EXPORT_NOTES = (
    "policy.sensors: production and the engine use {s_fast, s_slow}; RECOMPUTE-opus.md's layout reads {fast, slow}",
    "run ids: R15 reuses the four anchor run ids in every window and a retried slot reuses its run ids; the "
    "recompute requires series-unique run ids, so its layout qualifies repeated ids with the window id",
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
    start = 2 + 8 * (number - 1) if window[0] == "C" else 66 + 8 * (number - 1)
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
        index = 93 if o == 18 else 1
        row = dict(ordinal=o, task_pair=pair, condition=cond, model_id=model, seed_index=index,
                   expected_episode_seed=episode_seed(model, pair, index), held_out=False,
                   series_role=kind, run_id=f"align-v4-w1-episodes-e{o:02}")
        if contrast:
            row["contrast"] = dict(template=contrast[0], arm=contrast[1], stage=0 if o <= 11 else 1)
        rows.append(row)
    return rows


def default_plan(zero_capture=True, escalated=True):
    """W1, C1-C8 (C3's first attempt is a zero-capture refusal, retried), T1-T3 (T3 escalated to 24)."""
    plan = [dict(window="W1", attempt=1, zero_capture=False, escalated=False)]
    for w in ORDER:
        if w == "C3" and zero_capture:
            plan.append(dict(window=w, attempt=1, zero_capture=True, escalated=False))
            plan.append(dict(window=w, attempt=2, zero_capture=False, escalated=False))
        else:
            plan.append(dict(window=w, attempt=1, zero_capture=False, escalated=escalated and w == "T3"))
    return plan


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
            + "\n").encode()


def write_series(root, synth, *, plan=None, seed=7, period_ns=NS, saboteur_extra=25.0, sigma=3.0,
                 beta=(40.0, 0.004, 0.25, 2e-6, 1e-7), turns=(3, 6)):
    """Write ``root/recompute`` (RECOMPUTE-opus.md layout), ``root/engine-input.json`` (engine raw-source
    manifest, its sources under ``root``) and ``root/crosswalk.json``. Returns the crosswalk."""
    root = Path(root)
    rec = root / "recompute"
    plan = plan or default_plan()
    rng = random.Random(seed)
    template = synth.FrameTemplate(n_tasks=0, seed=seed, clusters=0)
    epoch_offset = synth.EPOCH0_S * NS
    clock = 0
    series = {"schema": "joulewise.v4_recompute_input.series.v1", "windows": []}
    engine_windows, crosswalk, used_rec_runs = [], [], set()
    w1_sentinel_j = {}
    for step in plan:
        wid, attempt = step["window"], step["attempt"]
        role = "W1" if wid == "W1" else ("calibration" if wid[0] == "C" else "test")
        rec_wid = wid if not step["zero_capture"] else f"{wid}-z{attempt}"
        slots = w1_roster() if wid == "W1" else r15_roster(wid, escalated=step["escalated"])
        series["windows"].append({"window_id": rec_wid, "role": role})
        w_start = clock
        rec_members, identity, engine_records = [], {}, []
        for slot in slots:
            rid = slot["run_id"]
            rec_rid = rid if rid not in used_rec_runs else f"{rid}~{rec_wid.lower()}"
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
            ident = hashlib.sha256((f"traj-{identical}" if identical is not None else rid).encode()).hexdigest()
            extra = {"identity_sha256": ident, "seed": slot["expected_episode_seed"],
                     "cohort_sha256": synth.COHORT}
            synth.write_member(rec, rec_wid, m, epoch_offset, extra=extra)
            base = rec / "windows" / rec_wid / "members" / rec_rid
            # The recompute layout's episode gets the production gate "reference" too (ignored there).
            ep_path = base / "outputs" / "align_episode.json"
            ep = json.loads(ep_path.read_text())
            g0 = ep["hardware"]["thermal"]["intervals"][0]
            for g in ep["hardware"]["thermal"]["intervals"]:
                g["reference"] = dict(g0["release"])
            # Production attribution refuses a G0 that overlaps the episode (G0 precedes it); synth.py
            # starts the episode at the G0 start. Start the episode 5 s after G0 ends, in both layouts.
            ep["start_ns"] = g0["end_ns"] + 5 * NS
            ep["hardware"]["registered_span_ns"] = [ep["start_ns"], ep["end_ns"]]
            ep_path.write_text(json.dumps(ep, indent=1, sort_keys=True) + "\n")
            meta = json.loads((base / "metadata.json").read_text())
            engine_records.append(_engine_member(root, base, slot, ep, meta, ident, step, wid, w_start))
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
            # synth.write_meter writes 100 ms polls under rate_idx 2 (production STEP_MS: 20 ms), which the
            # production parser reads as dropped samples. Use rate_idx 1 (100 ms), matching the polls.
            text = mpath.read_text()
            mpath.write_text(text.replace('"rate_idx": 2', '"rate_idx": 1', 1))
            streams["km003c-0.jsonl"] = synth.sha256_file(mpath)
            meter_rel = dict(path=str(mpath.relative_to(root)), sha256=streams["km003c-0.jsonl"])
            for rec_row, er in zip(rec_members, engine_records):
                if er.get("captured") and rec_row["condition"] == "benign":
                    er["dc_streams"] = [meter_rel]
        synth.dump(rec / "windows" / rec_wid / "window.json", {
            "schema": "joulewise.v4_recompute_input.window.v1", "window_id": rec_wid, "role": role,
            "members": rec_members, "adjudication": {"final": True, "excluded": {}}, "identity": identity,
            "battery": {}, "meter": {"streams": streams}, "cohort_sha256": synth.COHORT})
        raw_doc = canonical(dict(members=engine_records))
        raw_path = root / "engine" / f"{wid}-a{attempt}.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw_doc)
        engine_windows.append(dict(window=wid, attempt_id=f"{wid}#{attempt}", status="final",
                                   roster=[{k: v for k, v in s.items() if k != "contrast"} for s in slots],
                                   raw_source=dict(path=str(raw_path.relative_to(root)),
                                                   sha256=sha256_bytes(raw_doc))))
    synth.dump(rec / "series.json", series)
    pilot = [0.004, -0.006, 0.003, 0.005, -0.002, 0.001, -0.004]
    synth.dump(rec / "u3_bar.json", {"signed": True, "beta": 0.05, "N": 16, "f": 1.5, "r1_d_screen": 0.004,
                                     "pilot_relative_differences": pilot})
    designed = [(38.0, 38.0, 1500.0), (40.0, 40.0, 1501.0), (42.0, 42.0, 1502.5)]
    synth.dump(rec / "references.json", {"r1_replay_pair_j": [1500.0, 1510.0], "delta_slow_c": 1.0,
                                         "r1_designed_start_states": [
                                             {"designed_slow_c": d, "g0_release_slow_c": g, "energy_j": e}
                                             for d, g, e in designed]})
    payload = dict(schema=ENGINE_SCHEMA, synthetic=True, cohort=COHORT, windows=engine_windows,
                   u3_evidence=dict(pilot_pairs=[dict(session=f"synthetic-pilot-{i}", ordinals=[2, 7],
                                                      prespecified=True, token_identical=True,
                                                      energies_j=[1000.0 * (1 - r / 2), 1000.0 * (1 + r / 2)])
                                                 for i, r in enumerate(pilot)],
                                    frozen_before_W1=True,
                                    r1_d_screen=dict(token_identical=True, eligible=True, relative_difference=0.004)),
                   reference=dict(qualified=True, r1_replay_j=[1500.0, 1510.0], w1_sentinel_j=w1_sentinel_j),
                   r1_sensitivity=dict(states=[dict(token_identical=True, g0_slow_c=g, turn_owned_j=e,
                                                    designed_target_c=d) for d, g, e in designed],
                                       r1_replay_j=[1500.0, 1510.0], delta_slow_c=1.0),
                   delta_slow_c=1.0, u6_split_rule="within_pair_episode_order",
                   custody="synthetic only; no native qualification")
    (root / "engine-input.json").write_bytes(canonical(payload))
    doc = dict(schema="joulewise.v4_release.crosswalk.v1", synthetic=True, members=crosswalk,
               export_notes=list(EXPORT_NOTES))
    (root / "crosswalk.json").write_bytes(canonical(doc))
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
    sensors = {"s_fast": policy["sensors"]["fast"], "s_slow": policy["sensors"]["slow"], "fan_keys": []}
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
    episode = dict(schema=RECORDS_SCHEMA, episode_id=slot["run_id"], task_pair="shade/" + slot["task_pair"],
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
                  registered_span_ns=span, identity_sha256=ident,
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
                      stage=slot["contrast"]["stage"], pilot7_token_identical=True)
    return record


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
