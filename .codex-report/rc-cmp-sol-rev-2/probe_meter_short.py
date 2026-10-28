import random

from probe_meter_fit import compare

rng = random.Random(2718)
for base in (10**15, 10**16, 10**17):
    largest = 0
    for n in (3, 4, 5, 8, 12):
        for trial in range(10000):
            points = []
            for i in range(n):
                x = i * 10000
                rx = base + x * 1000000 + rng.randrange(0, 3000000)
                points.append((x, rx, 1.0, 1))
            d = compare(points)
            largest = max(largest, d or 0)
            if d and d > 1:
                print("first", base, n, trial, d, points)
                break
        if largest > 1:
            break
    print("base_max", base, largest)
