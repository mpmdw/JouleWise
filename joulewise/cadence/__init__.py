"""Measurement-cadence machinery: campaign kits, the span queue, named stops,
the Air desk table, the BLOCK-QUEUE ledger and the campaign runner library.

Design: ``docs/process/cadence_queue_design.md`` (section 13: the campaign runner,
runner kind ``cadence-legs-v1``). Everything here is pure library code (no SSH, no
launchd, no host command). The kit/queue/ledger CLI is ``scripts/cadence_queue.py``;
the span runner is ``scripts/cadence_legs_runner.py``; the Air desk CLI is
``scripts/air/cadence_desk.py``. The Air watcher and RL-128 probe live on the
cadence-queue branch (they need ``joulewise.pipeline_time``).
"""
