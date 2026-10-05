# Prospective whole-window NEG-8 references

Run `start_triplet/` at the window start, `midpoint/` near the temporal
midpoint, and `end_triplet/` at the window end. The seven members share the
canonical `df_rq_mid` scientific condition. Endpoint triplicates support
mean/standard-error screening; the midpoint makes the recorded drift allowance
trajectory-aware. These directories are prospective and do not replace or
modify the hash-pinned `p2_015_floors` campaign directories.

These v5 inputs use a 75-second idle. Run ids are retained because each
prospective window has fresh bound and claim runs roots; never reuse a
historical 30-second bundle root for this campaign.
