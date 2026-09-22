# Exhibit C — git diff af85b38a..cfc56921 for the three documents and the code (round 3 as applied), verbatim

```diff
diff --git a/docs/contracts/evidence_night_entry.md b/docs/contracts/evidence_night_entry.md
index 8116f30a..1b8d2758 100644
--- a/docs/contracts/evidence_night_entry.md
+++ b/docs/contracts/evidence_night_entry.md
@@ -218,24 +218,32 @@ with the clone's code. It then writes verdicts and evidence for:
 3. `shutil.which("claude")` finds the courier executable required by the
    unchanged installer. This checks availability; it never invokes the courier.
 4. Every `<roots_under>/night-custody/*/night_plan.json` is inventoried and
-   must be a regular non-symlink file; directories and special files refuse.
-   A root whose `night/chain.started` is a regular file without a regular
+   must be a regular non-symlink file; directories and special files refuse. A
+   root whose `night/chain.started` is a regular file without a regular
    `night/chain.exited` is ACTIVE and refuses. Otherwise an existing regular
    `night/courier.sent`, `night/result.json`, `night/chain.exited`, or any
    regular file matched by `run_night._refusal_paths` (`refusal.json`,
-   `refusal-01.json` and later numbers, `calibration-refusal.json`,
+   `refusal-N.json`, `calibration-refusal.json`,
    `calibration-refusal.json.*.json`) classifies its root as retained; the
-   record lists every marker found. Otherwise it is UNKNOWN and refuses.
-   A retained root whose plan span is still active by the watchdog's rule
-   (`scripts/magistrate_watchdog.plan_span_active`, evaluated on that root's
-   own `night_plan.json` at observation time with the entry checkout's timing
-   constants, which may differ from the head that authored an older sibling
-   plan) is ACTIVE and refuses; a root whose plan does not parse, or whose
-   `custody_root` is not its own directory, is UNKNOWN and refuses. Each row
-   records its reason. Discovery never removes a root, and has no fixed root
-   count. Classifying a root `retained` certifies only that a terminal record
-   exists and that the plan's span is over; it does not certify that the
-   courier's delivery succeeded.
+   record lists every marker found. Otherwise it is UNKNOWN and refuses. Here
+   `refusal-N.json` means any name matching `refusal-[0-9]*.json`, the second
+   glob in `run_night._refusal_paths` (`scripts/run_night.py:282`); the
+   driver's allocator writes `N` with a minimum of two digits (`{index:02d}` at
+   `scripts/run_night.py:273`: `refusal-01.json` … `refusal-99.json`, then
+   `refusal-100.json`), and a name with fewer digits, such as `refusal-7.json`,
+   also counts. A retained root whose plan span is still active by the
+   watchdog's rule (`scripts/magistrate_watchdog.plan_span_active`, evaluated
+   on that root's own `night_plan.json` at observation time with the entry
+   checkout's timing constants, which may differ from the head that authored an
+   older sibling plan) is ACTIVE and refuses; a root whose plan does not parse,
+   or whose `custody_root` is not its own directory, is UNKNOWN and refuses.
+   Each row records its reason. Discovery never removes a root, and has no
+   fixed root count. Classifying a root `retained` certifies only that a
+   terminal record exists and that the watchdog's span rule
+   (`scripts/magistrate_watchdog.plan_span_active`) reported the plan's span
+   inactive at observation time, which is also the answer for a plan whose span
+   has not yet begun (observation earlier than `t0 − PLAN_LEAD_S`); it does not
+   certify that the courier's delivery succeeded.
 5. The exact raw bracketed `night_gate.AGENT_CENSUS_ARGV` result is retained
    alongside `arm_census.observe_arm_census` and `classify_arm_census` evidence.
    The argv derivation and ancestry classification execute inside the clone's
diff --git a/docs/phase_2/derivation_night_runbook.md b/docs/phase_2/derivation_night_runbook.md
index 618abc62..ee247628 100644
--- a/docs/phase_2/derivation_night_runbook.md
+++ b/docs/phase_2/derivation_night_runbook.md
@@ -728,30 +728,25 @@ records show no terminal state. The executable form is
 `python -m joulewise.evidence_night check --candidate STAGING`, whose
 `night_agents` and `retained_roots` items must both pass with every inventoried
 root classified `retained` (contract item 4: `ACTIVE` and `UNKNOWN` refuse).
-For a manual read:
+For a manual read, run the same classifier the check binds, read-only, from the
+root of the entry checkout:
 
 ```zsh
-for p in /Users/edr/night-custody/*/night_plan.json(N); do
-  n=${p:h}/night; r=${p:h:t}
-  if [[ ! -f $p || -L $p ]]; then print -r -- "$r: REFUSED plan is not a regular file"; continue; fi
-  if [[ -f $n/chain.started && ! -f $n/chain.exited ]]; then print -r -- "$r: ACTIVE"; continue; fi
-  m=($n/courier.sent(N.) $n/result.json(N.) $n/chain.exited(N.) $n/refusal.json(N.) $n/refusal-<0-9>*.json(N.) $n/calibration-refusal.json(N.) $n/calibration-refusal.json.*.json(N.))
-  (( $#m )) && print -r -- "$r: retained ${m[1]:t}" || print -r -- "$r: UNKNOWN"
-done
+python3 -B -c 'import json; from joulewise import evidence_night as e; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'
 ```
 
-Every line must read `retained`; an `ACTIVE` or `UNKNOWN` line, or any
-installed night plist, stops the arm. Do not move or edit a root to change its
-line. This loop reads records only and cannot see the span rule; `check` binds.
-
-Source: cold-gate ruling 2026-09-21 (packet 05 Q2, lane A230). The `(N.)`
-qualifier restricts each glob to regular files, matching contract item 4's
-regular-file rule; it is the one correction to the ruled loop (record 02 of
-activation 29ea94df). The span half of the check above is `retained_roots`'s
-reuse of `scripts/magistrate_watchdog.plan_span_active`; the manual loop reads
-records only, so a root inside its span shows `retained` here and ACTIVE to the
-tracked check, which is the one that binds. `refusal-N.json` names are two-digit
-(`refusal-01.json` and later).
+It prints one row per `/Users/edr/night-custody/*/night_plan.json` with
+`classification`, `reason` and the full paths of every marker found, then
+`verdict`. Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a
+`Refused:` exit (for example a symlink anywhere under a root), or any installed
+night plist stops the arm. Do not move or edit a root to change its row. This
+is the same function `check` runs (contract item 4), evaluated at the current
+time with the entry checkout's timing constants, so it sees the span rule.
+
+Source: cold-gate ruling 2026-09-21 (packet 05 Q2, lane A230); the shell loop
+that ruling illustrated was replaced by the direct call on the cold gate's
+round-3 ruling (activation ce7c57a9, Q5) after it printed `retained` for a
+symlinked `night/` directory that the classifier refuses.
 
 ### 0.8 The clone's tree is clean, and the two desk inputs are written
 
diff --git a/docs/process/NIGHT_HANDBACK.md b/docs/process/NIGHT_HANDBACK.md
index 9ed2b3bf..1f453121 100644
--- a/docs/process/NIGHT_HANDBACK.md
+++ b/docs/process/NIGHT_HANDBACK.md
@@ -298,17 +298,32 @@ Record 17's script set remains the fallback until the first live use succeeds.
 Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3): the census
 classifies every process outside the caller's ancestor chain as foreign, and
 the tracked check refuses on any foreign PID, so the session's own MCP helpers
-must be gone first. The ruled text:
-
-Before running `check` on a real plan, this session terminates its own idle
-MCP helpers. List the children of the session root: `pgrep -lP
-<session-root-pid>`. For every child whose command line contains `codex
-mcp-server`, send SIGTERM to that child and its descendants (`pkill -TERM -P
-<child-pid>`; `kill -TERM <child-pid>`), wait until `pgrep -f 'codex
-mcp-server'` lists no descendant of the session root, and record the PIDs
-terminated in the check record. Terminate nothing outside the session root's
-descendants. Then run `check`. If the census still reports any descendant of
-the own session root as foreign, stop; never relabel it "diagnostic".
+must be gone first. The ruled text, with its commands corrected by the cold
+gate 2026-09-21 (activation ce7c57a9, round-3 packet, Q2; `pgrep -lP` prints
+process names only and `pkill -P` reaches immediate children only, both
+verified against the installed manual and a live process tree):
+
+Before running `check` on a real plan, this session terminates its own idle MCP
+helpers, and nothing else. Let `ROOT` be the session root's PID. List the
+session root's children with their full command lines: `pgrep -flP $ROOT`.
+Every child whose command line contains `codex mcp-server` is a helper. For
+each helper, enumerate all of its descendants, at every depth, and send SIGTERM
+to the helper and every descendant:
+
+```zsh
+descendants() { local pid; for pid in $(pgrep -P $1); do print -- $pid; descendants $pid; done }
+for h in $(pgrep -flP $ROOT | grep -F 'codex mcp-server' | cut -d' ' -f1); do
+  victims=($h $(descendants $h)); print -r -- "helper $h: TERM ${(j:,:)victims}"; kill -TERM $victims
+done
+```
+
+Then wait until no descendant of the session root, at any depth, has `codex
+mcp-server` in its command line: repeat `for d in $(descendants $ROOT); do ps
+-o pid=,command= -p $d; done | grep -F 'codex mcp-server'` until it prints
+nothing. Record every PID terminated, with its command line, in the check
+record. Terminate nothing that is not a descendant of `ROOT`. Then run `check`.
+If the census still reports any descendant of the session root as foreign,
+stop; never relabel it "diagnostic".
 
 **Timeline.** The plan's relative boundaries are: install strictly before
 t0 − 600 s (the close is excluded); REQUEST and magistrate exit at
diff --git a/joulewise/evidence_night.py b/joulewise/evidence_night.py
index 65970410..35189540 100644
--- a/joulewise/evidence_night.py
+++ b/joulewise/evidence_night.py
@@ -727,7 +727,7 @@ def retained_roots(state, now_epoch_s=None):
         elif not markers:
             classification, reason = "UNKNOWN", "no terminal night record"
         else:
-            classification, reason = "retained", "terminal record present; plan span over"
+            classification, reason = "retained", None
             try:
                 parsed = NightPlan.from_mapping(json.loads(plan.read_text(encoding="utf-8")))
                 if os.path.realpath(parsed.custody_root) != os.path.realpath(plan.parent):
@@ -736,7 +736,10 @@ def retained_roots(state, now_epoch_s=None):
                 elif plan_span_active(parsed, now, Storage(plan.parent)):
                     classification = "ACTIVE"
                     reason = "plan span active (scripts/magistrate_watchdog.plan_span_active)"
-            except (PlanError, ValueError, TypeError, OverflowError, OSError) as exc:
+                else:
+                    reason = ("terminal record present; plan span inactive at observation time "
+                              "(scripts/magistrate_watchdog.plan_span_active)")
+            except (PlanError, ValueError, TypeError, OverflowError, OSError, RecursionError) as exc:
                 classification, reason = "UNKNOWN", f"plan unreadable: {type(exc).__name__}: {exc}"
         inventory.append(dict(plan=str(plan), classification=classification, reason=reason,
                               evidence=[str(p) for p in markers]))
```
