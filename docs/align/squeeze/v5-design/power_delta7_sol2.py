#!/usr/bin/env python3
"""Synthetic-only delta7 replay; sequential, stdlib, no study-data imports.

Uses the byte-identical prior power_sim_sol2.py for the independent law.
For resized designs only its preassigned ROSTER is replaced. one_trial's
hardcoded capability/strong-label flags are ignored; its four rejection
flags and conjunction remain correct for the substituted roster. Its effect
denominators are corrected here. Honest gates are audited separately.

Author mode is a comparison, not the independent simulation. It calls the
author sampler sequentially with the exact jobs/seeds from jobs_all().
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import power_sim_sol2 as independent


def emit(record):
    print(json.dumps(record, sort_keys=True), flush=True)


def assigned_roster(windows, h4pw=8):
    rng = random.Random(independent.SEED + 91)
    result = []
    for w in range(windows):
        members = []
        for cell, offset in enumerate(independent.OFFSETS):
            phase = (w + offset) % 3
            for cls in ((0, 1), (0, 2), (1, 2))[phase]:
                members.append((cell // 3, cell, cls != 0))
        rng.shuffle(members)
        # A prospective abstract reallocation: promote two assigned covers.
        # This is not a substitute for freezing the final class roster at G12.
        extra = h4pw - 8
        for i, (pair, cell, subset) in enumerate(members):
            if extra and not subset:
                members[i] = (pair, cell, True)
                extra -= 1
        assert extra == 0
        assert len(members) == 12 and sum(x[2] for x in members) == h4pw
        assert all(any(x[1] == c and x[2] for x in members) for c in range(6))
        result.append(members)
    return result


def row(signal, law, reps, index, windows=28, h4pw=8):
    original = independent.ROSTER
    independent.ROSTER = assigned_roster(windows, h4pw)
    rng = random.Random(independent.SEED + 100003 * (index + 1))
    counts = [0] * 5
    sums = [0.0] * 4
    try:
        for _ in range(reps):
            events, effects, _q = independent.one_trial(rng, signal, law)
            for j, event in enumerate(events[:5]):
                counts[j] += event
            for j, effect in enumerate(effects):
                sums[j] += effect * (336 if j < 3 else 224) / (windows * (12 if j < 3 else h4pw))
    finally:
        independent.ROSTER = original
    return dict(signal=signal, law=law.name, windows=windows, h4pw=h4pw,
                effect=[round(x / reps, 6) for x in sums],
                **{h: independent.probability(k, reps)
                   for h, k in zip(independent.LABELS[:5], counts)})


def independent_run(reps):
    assert assigned_roster(28) == independent.ROSTER
    curves = []
    for index, law in enumerate(independent.LAWS[:4]):
        for signal in (.06, .07, .08, .09, .10, .11, .12, .13, .14):
            result = row(signal, law, reps, index)
            curves.append(result)
            emit(result)
        curve = [r for r in curves if r['law'] == law.name]
        emit(dict(MDE=law.name, **{
            h: next((r['signal'] for r in curve if r[h]['p'] >= .80), None)
            for h in independent.LABELS[:5]}))
    stress = independent.LAWS[3]
    intermediate = independent.Law('intermediate', rho=.15, regression=.035, missing=.035)
    for law, index in ((stress, 3), (intermediate, 6)):
        options = ((28, 8), (28, 10), (36, 8), (44, 8), (52, 8), (60, 8))
        for windows, h4pw in options:
            emit(dict(ladder=True, **row(.10, law, reps, index, windows, h4pw)))


def author_run(reps):
    import ruling_power_sim as author
    for job in author.jobs_all(reps):
        emit(author.simulate(job))
    emit(dict(null=author.simulate(dict(mu=0., rho=0., windows=28, h4pw=8,
                                        reps=reps, seed=99, **author.BASE))))


def binomial_pass(n, p, cutoff):
    return sum(math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(cutoff+1))


def gates_run(reps):
    for p in (.05, .075, .08, .10, .15):
        for n, cutoff in ((280, 14), (280, 22), (520, 22), (520, 40)):
            passed = binomial_pass(n, p, cutoff)
            emit(dict(binomial=True, n=n, true_fpr=p, cutoff=cutoff,
                      per_rule_fail=1-passed,
                      independent_six_fail=1-passed**6,
                      arbitrary_rule_dependence_fail_upper=min(1., 6*(1-passed))))
    for copy in (0., .3):
        rng = random.Random(independent.SEED + 707)
        old, new = 0, 0
        per_rule_fail = [0] * 6
        for _ in range(reps):
            counts = [0] * 6
            for _ in range(28):
                shared = [independent.scores(rng), independent.scores(rng)]
                for pos in range(10):
                    raw = shared[pos % 2] if rng.random() < copy else independent.scores(rng)
                    aa = independent.alarms(raw, independent.POP_THRESHOLDS)
                    for j, alarm in enumerate(aa):
                        counts[j] += alarm
            old += max(counts) <= 14
            new += max(counts) <= 22
            for j, k in enumerate(counts):
                per_rule_fail[j] += k > 22
        emit(dict(coupled_nominal_six=True, honest_copy=copy,
                  old_pass=independent.probability(old, reps),
                  new_pass=independent.probability(new, reps),
                  new_per_rule_fail=[independent.probability(k, reps) for k in per_rule_fail]))
    emit(dict(hoeffding_width=independent.average_conditional_upper(0, 280),
              hoeffding_at_22=independent.average_conditional_upper(22, 280)))


def icc_run(reps):
    # Test the baseline override even when the ICC tier selects rho=.30.
    for rho in (.15, .30, .40):
        law = independent.Law('baseline-icc-' + str(rho), rho=rho)
        emit(row(.10, law, reps, 10))


def transport_run(reps):
    from multiprocessing import get_context
    import ruling_power_sim as author
    jobs = [dict(mu=.1, rho=.3, windows=28, h4pw=8, reps=reps,
                 seed=2026110807, **law) for law in (author.BASE, author.STRESS)]
    serial = [author.simulate(job) for job in jobs]
    with get_context('spawn').Pool(1) as pool:
        spawned = pool.map(author.simulate, jobs)
    assert spawned == serial
    assert json.dumps(spawned, sort_keys=True).encode() == json.dumps(serial, sort_keys=True).encode()
    assert serial[0]['holm'] != serial[1]['holm']
    emit(dict(spawn_equals_serial=True, canonical_json_byte_equal=True, results=spawned))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('author', 'independent', 'gates', 'icc', 'transport'))
    parser.add_argument('--reps', type=int, default=2000)
    args = parser.parse_args()
    if args.reps <= 0:
        parser.error('reps must be positive')
    source = Path(__file__).with_name('power_sim_sol2.py').read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    assert digest == '1ed19bfb3a63337ccc53ecd85e982858eafa4e57d5a5e5c35c9f18f2ebe2760e'
    emit(dict(mode=args.mode, reps=args.reps, prior_sha256=digest,
              seed=independent.SEED, process_count=1))
    {'author': author_run, 'independent': independent_run,
     'gates': gates_run, 'icc': icc_run, 'transport': transport_run}[args.mode](args.reps)


if __name__ == '__main__':
    main()
