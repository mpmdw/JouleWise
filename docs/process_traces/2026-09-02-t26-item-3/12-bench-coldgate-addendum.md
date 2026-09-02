## Addendum 2026-09-02 — item 3 drift-envelope rationale

This addendum corrects item 3's stated metrology rationale; it moves no ruled
number. The `3.68 ppm × age` calculation states accumulated oscillator drift
only and implicitly assumes zero initial reference error. The predicate admits
`reference_bound_seconds <= 0.5 s`, so the guaranteed error envelope at age
`t` is instead

```text
reference_bound_seconds + 3.68e-6 × t
```

For Sol's admitted `reference_bound_seconds = 0.499 s` example, the envelope is
`0.499 + 3.68e-6 × 1830 = 0.5057344 s` (0.5057 s rounded) at the real-path
oldest-sample horizon, and
`0.499 + 3.68e-6 × (21_600 + 600 + 30) = 0.5808064 s` (0.5808 s rounded)
under the standalone 6 h + 600 s + 30 s envelope. At the admitted 0.5-second
ceiling, the corresponding guaranteed maxima are 0.5067344 s and 0.5818064 s.

This correction does not justify restoring the struck five-second issuance
bound: that bound was not the carrier of the initial reference error or the
oscillator-drift guarantee. The 600 s liveness bound, the 6 h horizon, the
[600 s, 3600 s] R0 span, the 30 s R1 batch bound, both 5 ms anchor gates, and
the standing fence are unchanged. Any change to a ruled number still requires
a cold gate.
