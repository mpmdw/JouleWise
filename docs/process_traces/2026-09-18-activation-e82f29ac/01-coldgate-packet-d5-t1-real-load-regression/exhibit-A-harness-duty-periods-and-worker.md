# Exhibit A — harness code at `498ad1d0` (`git show 498ad1d0:scripts/sample_quiet_predicate_evidence.py`, lines 770–830 and 860–875)

```python
def duty_periods(share, duration_s, period_s, burn, clock, *, start=None):
    """Thread-CPU budgets, absolute wall deadlines, no catch-up burst.

    During the first five seconds calibrate the loop duty for measured period
    overhead and the batch size toward 100 us CPU. Then freeze both. An
    overshoot is charged against the next period; unsatisfied CPU is never
    carried forward under contention. Each batch and clock check is measured:
    reported overshoot bound = largest observed batch + accounting tail.
    This is a measured CPU bound, not a real-time scheduling guarantee.
    """
    start = clock.monotonic() if start is None else start
    end = start + duration_s
    duty, batch, debt = share, 1, 0.0
    rows = []
    index = 0
    previous_cpu_end = clock.cpu()
    while (now := clock.monotonic()) < end:
        boundary = min(end, start + (index + 1) * period_s)
        if boundary <= now:
            index = int((now - start) / period_s)
            boundary = min(end, start + (index + 1) * period_s)
        nominal_start = start + index * period_s
        elapsed = boundary - nominal_start
        calibrating = nominal_start - start < 5.0 - 1e-9
        cpu_start = previous_cpu_end
        carry_in = max(0.0, clock.cpu() - cpu_start)
        budget = share * elapsed
        work_budget = max(0.0, min(budget, duty * elapsed) - debt)
        quantum_max = 0.0
        current = clock.cpu()
        while current - cpu_start < work_budget and clock.monotonic() < boundary:
            previous = current
            burn(batch)
            current = clock.cpu()
            quantum = current - previous
            quantum_max = max(quantum_max, quantum)
            if calibrating and quantum > 0:
                batch = max(1, min(4096, int(batch * min(2, max(.5, .0001 / quantum)))))
        burn_used = current - cpu_start
        clock.sleep_until(boundary)
        cpu_end = clock.cpu()
        previous_cpu_end = cpu_end
        used = cpu_end - cpu_start
        debt = max(0.0, burn_used - work_budget)
        tail = max(0.0, used - burn_used)
        overrun = max(0.0, used - budget)
        rows.append({"period": index, "start_mono_s": nominal_start, "end_mono_s": boundary,
                     "elapsed_s": elapsed, "cpu_used_s": used, "budget_cpu_s": budget,
                     "work_budget_cpu_s": work_budget, "overrun_cpu_s": overrun,
                     "shortfall_cpu_s": max(0.0, budget - used),
                     "wake_late_s": max(0.0, clock.monotonic() - boundary),
                     "max_quantum_cpu_s": quantum_max, "overshoot_bound_cpu_s": quantum_max + tail + carry_in,
                     "accounting_cpu_s": carry_in,
                     "duty": duty, "batch": batch, "calibrating": calibrating})
        if calibrating:
            duty = max(0.0, min(share, duty + .25 * (budget - used) / elapsed))
        index += 1
    return rows


def stationarity(periods, target):
# ... lines 831-859 omitted ...

def load_worker(connection, config):
    try:
        set_qos(config["qos"])
        burn = burn_profile(config["profile"], config["seed"])
        worker_identity = identity(os.getpid())
        connection.send({"ready": True, "identity": worker_identity})
        start = connection.recv()
        clock = Clock()
        clock.sleep_until(start)
        periods = duty_periods(config["share"], config["duration_s"], config["period_s"],
                               burn, clock, start=start)
        connection.send({"identity": worker_identity, "periods": periods,
                         "stationarity": stationarity(periods, config["share"])})
    except BaseException as exc:
        connection.send({"error": f"{type(exc).__name__}: {exc}"})
```
