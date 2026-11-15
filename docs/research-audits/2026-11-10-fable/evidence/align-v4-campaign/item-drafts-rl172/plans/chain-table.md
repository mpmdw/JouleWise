| # | Item | Span | Gate (short) | Forecast t0 (local / epoch) | Argument | Exp end | Worst end | Fence end |
|---|---|---|---|---|---|---|---|---|
| 0 | item 331 (issued) | dev-01-s04 (item 331) | issued; t0 00:20 forecast by the lead | Sun 00:20:00 / 1794730800 | `13:14-13:15` | Sun 02:56:45 | Sun 06:27:30 | Sun 06:51:50 |
| 1 | ITEM-hp01-s01 | hp-01-s01 smoke | s04 closed + Check; RL-155 §5.2; line 2; line 9 s03 desk | Sun 03:01:45 / 1794740505 | `02:00-02:35` | Sun 04:56:48 | Sun 07:39:15 | Sun 08:03:35 |
| 2 | (remainder item, not drafted) | hp-01-s02 | smoke hand-read + R9; s04 desk final; CI base+0 | Sun 05:16:48 / 1794748608 | `02:00-02:35` | Sun 07:32:42 | Sun 10:39:18 | Sun 11:03:38 |
| 3 | (remainder item, not drafted) | hp-01-s03 | s02 closed clean; smoke desk final | Sun 07:37:42 / 1794757062 | `02:00-02:35` | Sun 10:14:27 | Sun 13:45:12 | Sun 14:09:32 |
| 4 | ITEM-dev02-s02 | dev-02-s02 | append committed; RL-155 §3.3; line 9 hp-01-s02 desk; Sunday | Sun 10:19:27 / 1794766767 | `02:00-02:35` | Sun 13:17:03 | Sun 17:11:57 | Sun 17:36:17 |
| - | (host event) | RL-172 (h) restart at 14:08 (± 15 min), then the readback; no F0 after 12:00 until done | dev-02-s02 closed; lead's remote proof of a clean return | Sun 14:08:00 / 1794780480 | - | Sun 14:28:00 (assumed 20 min) | - | - |
| 5 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Sun 14:48:00 / 1794782880 | `(c3f4)` | Sun 16:46:54 | Sun 18:11:00 | dl t0 + 14,400 s |
| 6 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Sun 18:48:00 / 1794797280 | `(c3f4)` | Sun 20:46:54 | Sun 22:11:00 | dl t0 + 14,400 s |
| 7 | ITEM-dev02-s03 | dev-02-s03 | s02 checked; line 9 hp-01-s03 desk; Monday | Mon 00:00:00 / 1794816000 | `13:14-13:15` | Mon 02:57:36 | Mon 06:52:30 | Mon 07:16:50 |
| 8 | ITEM-dev03-pilot | dev-03-s01 pilot | READY+staged; dev-02 closed; line 9 dev-02-s02 desk; dated Monday | Mon 03:02:36 / 1794826956 | `02:00-02:35` | Mon 04:59:40 | Mon 07:40:06 | Mon 08:04:26 |
| 9 | ITEM-dev03-rest | dev-03-s02 rest (nine) | hand-read R9 + L002 released; append; line 9 dev-02-s03 desk; dated Monday | Mon 05:19:40 / 1794835180 | `02:00-02:35` | Mon 09:32:23 | Mon 14:27:10 | Mon 14:51:30 |
| 10 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 09:37:23 / 1794850643 | `(c3f4)` | Mon 11:36:17 | Mon 13:00:23 | dl t0 + 14,400 s |
| 11 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 13:37:23 / 1794865043 | `(c3f4)` | Mon 15:36:17 | Mon 17:00:23 | dl t0 + 14,400 s |
| 12 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Mon 17:37:23 / 1794879443 | `(c3f4)` | Mon 19:36:17 | Mon 21:00:23 | dl t0 + 14,400 s |
| 13 | ITEM-dev04-s01 | dev-04-s01 | delta ADMIT; Q6; line 9 dev-03 pilot desk; dated Tuesday | Tue 00:00:00 / 1794902400 | `13:14-13:15` | Tue 02:55:07 | Tue 06:52:30 | Tue 07:16:50 |
| 14 | ITEM-dev04-s02 | dev-04-s02 | L005 released or >=4 of dev-03's 5 consumers; line 9 dev-03 rest desk; Tuesday | Tue 03:00:07 / 1794913207 | `02:00-02:35` | Tue 06:21:18 | Tue 09:52:37 | Tue 10:16:57 |
| 15 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 06:26:18 / 1794925578 | `(c3f4)` | Tue 08:25:12 | Tue 09:49:18 | dl t0 + 14,400 s |
| 16 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 10:26:18 / 1794939978 | `(c3f4)` | Tue 12:25:12 | Tue 13:49:18 | dl t0 + 14,400 s |
| 17 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Tue 14:26:18 / 1794954378 | `(c3f4)` | Tue 16:25:12 | Tue 17:49:18 | dl t0 + 14,400 s |
| 18 | ITEM-dev05-s01 | dev-05-s01 | delta ADMIT; Q6; line 9 dev-04-s01 desk; dated Wednesday | Wed 00:00:00 / 1794988800 | `13:14-13:15` | Wed 03:14:40 | Wed 06:52:30 | Wed 07:16:50 |
| 19 | ITEM-dev05-s02 | dev-05-s02 | line 9 dev-04-s02 desk; Wednesday | Wed 03:19:40 / 1795000780 | `02:00-02:35` | Wed 06:21:18 | Wed 10:12:10 | Wed 10:36:30 |
| 20 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 06:26:18 / 1795011978 | `(c3f4)` | Wed 08:25:12 | Wed 09:49:18 | dl t0 + 14,400 s |
| 21 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 10:26:18 / 1795026378 | `(c3f4)` | Wed 12:25:12 | Wed 13:49:18 | dl t0 + 14,400 s |
| 22 | STANDING-F0 | F0 (standing, trigger c) | no staged item can hold within 2 h 30 | Wed 14:26:18 / 1795040778 | `(c3f4)` | Wed 16:25:12 | Wed 17:49:18 | dl t0 + 14,400 s |
