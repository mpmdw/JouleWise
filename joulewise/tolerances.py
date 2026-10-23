"""Physical resolution bars for stored-versus-rederived measurements."""

# A phase is attribution-limited at about 1 J. One mJ is 0.1% of that limit
# and catches a 1 ms edge displacement (0.047 J), far above binary64 noise.
NEG8_ENERGY_ABS_TOL_J = 1e-3

# Clock-anchor reads resolve about 125 us; 1 us is below 1% of that bound
# while comfortably exceeding float noise in the stored time scalars.
CALIBRATION_TIME_ABS_TOL_S = 1e-6
