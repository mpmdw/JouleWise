#!/usr/bin/env python3
"""UNRUN: written by an agent on 2026-11-07 and never executed. Read it first.

Stdlib only. Imports, builds and runs no km003c-rs code. Run:

    python3 -I /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/model_push.py
    python3 -I /private/tmp/jwoss-ro/km003c-rs-redelivery/kit/model_push.py FIXTURE.jsonl

where FIXTURE.jsonl is the JouleWise capture, for example extracted with
    git -C /Users/edr/code/CapstoneProject/jw-wt/handoff show \
        origin/main:tests/fixtures/km003c/redelivery1000_slice.jsonl \
        > /private/tmp/jwoss-run/redelivery1000_slice.jsonl
(sha256 0a9978ae4080c4001c7b6b8cfaa3ea7965b60c57b8bd160f2e381a13cfa933ca).

A hand transliteration of the continuity, elapsed-time and energy parts of
MeasurementAccumulator::push() in km003c-lib/src/measurement.rs:104-195 at
okhsunrog/km003c-rs 71f69e4a35c1184cc114a62145b8a8241d3e13e9, with the
kit's fix.patch as a switch. 1000 SPS only. It is a model, not their code.

Expected output, derived by hand (not observed):
    scenario          variant  elapsed_us  accepted  discarded  energy_J
    synthetic (A)     pin           45000        47          8    0.2250
    synthetic (A)     fix           27000        28         27    0.1350
    observed seq (B)  pin         1217000      1219          8    6.0850
    observed seq (B)  fix         1199000      1200         27    5.9950
    fixture           pin         1217000      1219          8  (fix + ~1.300)
    fixture           fix         1199000      1200         27
"""

import json
import sys

MAX_CONSECUTIVE_REJECTED = 8  # measurement.rs:24
MAX_REDELIVERED = 64  # fix.patch
STEP = 1  # GraphSampleRate::Sps1000.sequence_step(), adcqueue.rs:48-50
MAX_FORWARD = (0xFFFF // 2 // STEP) * STEP  # measurement.rs:32-35
FIVE_WATTS_UW = 5_000_000


def run(samples, fixed):
    """samples: iterable of (sequence, power_uw) in arrival order."""
    previous = None  # (sequence, power_uw); None starts a continuity run
    consecutive = 0
    elapsed_us = accepted = discarded = 0
    energy_twice_uw_us = 0
    for sequence, power_uw in samples:
        if previous is not None:
            delta = (sequence - previous[0]) & 0xFFFF
            plausible = delta != 0 and delta <= MAX_FORWARD and delta % STEP == 0
            if not plausible:
                discarded += 1
                behind = (previous[0] - sequence) & 0xFFFF
                if fixed and behind % STEP == 0 and behind // STEP <= MAX_REDELIVERED:
                    continue
                consecutive += 1
                if consecutive >= MAX_CONSECUTIVE_REJECTED:
                    previous = None
                    consecutive = 0
                continue
            delta_us = delta * 1000
            energy_twice_uw_us += (previous[1] + power_uw) * delta_us
            elapsed_us += delta_us
        consecutive = 0
        previous = (sequence, power_uw)
        accepted += 1
    return elapsed_us, accepted, discarded, energy_twice_uw_us / 2 / 1e12


def constant(sequences):
    return [(s, FIVE_WATTS_UW) for s in sequences]


def fixture(path):
    """(sequence, power_uw) from the JouleWise capture's batch records."""
    out = []
    with open(path) as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("k") != "b":
                continue
            payload = bytes.fromhex(record["p"])
            for offset in range(0, len(payload) - len(payload) % 20, 20):
                sample = payload[offset : offset + 20]
                sequence = int.from_bytes(sample[0:2], "little")
                vbus_uv = int.from_bytes(sample[4:8], "little", signed=True)
                ibus_ua = int.from_bytes(sample[8:12], "little", signed=True)
                out.append((sequence, round(vbus_uv * ibus_ua / 1e6)))
    return out


def main():
    run_a = list(range(49_790, 49_817))
    scenarios = [
        ("synthetic (A)", constant(run_a + run_a + [49_817])),
        ("observed seq (B)", constant(list(range(49_250, 49_817)) + list(range(49_790, 50_450)))),
    ]
    if len(sys.argv) > 1:
        scenarios.append(("fixture", fixture(sys.argv[1])))
    print(f"{'scenario':<18}{'variant':<9}{'elapsed_us':>10}{'accepted':>10}{'discarded':>11}{'energy_J':>10}")
    for name, samples in scenarios:
        for variant, fixed in (("pin", False), ("fix", True)):
            elapsed_us, accepted, discarded, energy_j = run(samples, fixed)
            print(f"{name:<18}{variant:<9}{elapsed_us:>10}{accepted:>10}{discarded:>11}{energy_j:>10.4f}")


if __name__ == "__main__":
    main()
