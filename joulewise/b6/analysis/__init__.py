"""Block-6 analysis driver (registration B6-REPL §9 to §13), written blind.

The driver runs block 5's registered analysis once per block-6 session through
one adapter (:mod:`joulewise.b6.analysis.adapter`, the only place lane L9's
programs are called), pairs GAMMA by round (§6.2) and adds the block-6 lines:
the between-session summary (§10), the side-by-side table (§11.1), the
replication word (§11.2) and the flagged-inclusive line (§11.4).  Counting is
read from the session loop's acceptance (RUN_STATE item 53), never from a
harvest's ``exclusions.json``.  Public bytes are structure only (§12.1).
"""
