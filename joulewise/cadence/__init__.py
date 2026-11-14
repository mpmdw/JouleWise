"""Measurement-cadence machinery: campaign kits, the span queue, named stops,
the Air desk table, the RL-128 status-probe reader and the BLOCK-QUEUE ledger.

Design: ``docs/process/cadence_queue_design.md``. Everything here is pure
library code (no SSH, no launchd, no host command). The Air CLIs live in
``scripts/air/cadence_watch.py`` and ``scripts/air/cadence_desk.py``; the
kit/queue/ledger CLI is ``scripts/cadence_queue.py``.
"""
