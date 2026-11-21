# hp-02 gate machine audit round 1 · 2026-11-20

The audit's three VERIFIED HIGH findings reproduced on `2ed09e1b9` with zero launcher calls. All three are implementation gaps in existing frozen Q2 and L1 rules. The audit listed zero MED and LOW findings. The successor freeze remains `eafae0cb9`.

| Finding | Root cause | Repair and regression |
| --- | --- | --- |
| Q2 interruption after issue replacement | The primary issue ID keyed the only pending marker. | The marker now starts in independently locked queue custody at the admitted SHA and sequence and persists through observation and admission assessment. The regressions interrupt Issue, Start and Run, replace the issue, and repeat with the primary store absent. They exercise an incorrect digest and then the exact typed disposition. |
| L1 stale or competing host Check | Refusals raised by shared admission bookkeeping bypassed the machine's issue journal. | Shared admission refusals enter the same hold classifier and carry their source evidence. Tests cover an older Check, a conflicting receipt at the same end time, and a stale Check alongside an independent fence block. |
| Q2 lock-acquisition failure | The queue-custody handler covered opening the issue lock. Acquisition used the outer refusal path. | Both lock operations run inside the same custody boundary while the independent queue lock is held. Tests inject an I/O error at open and at acquisition in Issue, Start and Run. |

All new regressions run through `tests.test_hp02_successor_items`. Each latch is checked across a fresh attempt and verified clearance, followed by exactly one simulated launch. The Q2 cases also verify the canonical failed-read hash, scope and sequence directly from persisted records.

The new regression's first baseline run had ten failing scenarios across the three findings. The repaired run passed all fourteen scenarios with zero native-command attempts. The four original-and-audit CI tests passed locally, including the 60 original vectors, 54 occupancy decisions, 1,764 clock cases, 43 runner traces and 360 held-item replays. The frozen rulings partition passed all 300 Q2 recoveries. The [draft PR](https://github.com/mpmdw/JouleWise/pull/890) records the complete replay and hosted result for the repair head.

The six successor freeze entries and the six original fixtures remain byte-identical. The queue, regenerated items and pinned launcher retain their existing commitments. All executed inputs were synthetic or administrative. Independent execution and lead acceptance remain due before issue.
