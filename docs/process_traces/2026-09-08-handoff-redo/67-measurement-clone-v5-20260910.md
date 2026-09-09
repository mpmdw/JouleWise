# `_v5` measurement clone created (lead, bench, 2026-09-08 ~08:35 PDT) — G2A-FIRST-WINDOW-01 stage A

Per the runsheet recipe (docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md, "Plan-derived
measurement variables" clone-prep block; lines ~1501-1522 at 1c83f2af):

| Item | Value |
|---|---|
| MEASUREMENT_ROOT | `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a` |
| REVIEWED_HEAD | `1c83f2af48df5611c7bbf824bec818209c252d0d` (main; CI green; contains the G2-a routing series d477e138) |
| NIGHT_DATE (tentative) | 20260910 — the first night after rehearsal-20260909 is accepted; re-clone under the real date/head if the reviewed head moves |
| Clone | `git clone --no-hardlinks /Users/edr/code/JouleWise` then `checkout --detach`; HEAD verified equal to REVIEWED_HEAD |
| Interpreter | `.venv/bin/python` = Python 3.13.1 (`python3.13 -m venv .venv`) |
| Lock | `pip install -c env/mac-measurement-lock.txt -e ".[mac]"` + `charset-normalizer requests urllib3`; `diff` of the lock vs `pip freeze --exclude-editable` is EMPTY (rc 0). pip warned that the locked charset-normalizer 3.4.8 is a yanked release; installed as pinned. |
| Tree | see the status line recorded below; the protected historical clone `/Users/edr/JouleWise-measurement-20260813` (eeb4e133) is untouched |

Not done here (deliberately): no v2 plan authored, no night agents installed, no plan root under
`~/night-custody`. Those follow the rehearsal's acceptance and the email-then-arm procedure (D-175 conditions
apply to any REHEARSAL_STUB; the first real DIAGNOSTIC_NO_PACK plan follows D-169 stage 2 and the stage-1 plan
email). The local-clone `origin` is a transport source only; the publication remote must be configured and
verified before any reviewed-main/publication ceremony (scout trace 27 §1).

Status line after the venv build: `?? joulewise.egg-info/` (the editable install writes it; not gitignored at 1c83f2af). Harmless for G2-a (DIAGNOSTIC_NO_PACK) but `reviewed_main()` requires a clean tree for the later pack ceremony — either ignore the directory in a reviewed follow-up or remove it before that ceremony (G2A-FIRST-WINDOW-01 sub-item).
