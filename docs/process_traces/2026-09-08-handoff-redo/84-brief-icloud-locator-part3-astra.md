WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","tests/test_calibration_ledger.py","tests/test_calibration_ledger_custody.py","tests/test_calibration_bracketing.py"]

# Seat brief — ICLOUD-CUSTODY-LOCATOR-01 part 3: REDESIGN under the magistrate's ruling (gpt-6-astra, medium)

HEAD of this worktree = parts 1-2 committed (WIP). Part 2 returned NEEDS_SCOPE for joulewise/authentication_io.py
because `V2AuthenticationReadSession.read`/`read_nofollow` hold the shared RLock during filesystem reads, so a
daemon-thread worker abandoned on timeout can retain the lock and block later authentication work. RULING: the
scope expansion is REFUSED. The authentication I/O layer (atomic first-digest enforcement, strict parsing, session
registry lock) is a fail-closed mechanism and is not touched by this lane. The daemon-thread-timeout pattern must
therefore NEVER wrap a call that enters an authentication session or takes any lock.

Required design:
1. The bounded probe is a PURE PATH PROBE run BEFORE and OUTSIDE any authentication session or lock: `Path.exists()` /
   `is_dir()` (and nothing else) of the custody locator path in a daemon thread with the 2 s budget. Timeout or any
   exception → the locator is treated exactly as ABSENT (verify what "absent" yields today and preserve it), and the
   authenticated read is NEVER attempted for that locator. Only after the probe returns True does the existing,
   UNBOUNDED, lock-safe authenticated read run as before. Document the residual race (the mount can stall between
   probe and read) as accepted: it narrows the hang window from "always" to "stalls within the ~2 s after a
   successful probe" and never leaves a lock held, because the read path is unchanged.
2. `JOULEWISE_BACKUP_ROOTS` semantics as in parts 1-2 (empty = locators under a default backup root are treated as
   absent without probing).
3. REMOVE any code from parts 1-2 that wraps an authenticated read, an authentication-session call, or a locked
   region in a worker thread. Re-express the regressions: blocked `Path.exists`/`is_dir` → absent within budget;
   a blocked authenticated READ after a successful probe is out of scope (do not test for a bound there);
   concurrency regression: after a timed-out probe, a subsequent authentication session on another locator proceeds
   normally (no lock retained) — this is the counterfactual for the refused design.
4. Acceptance = the touched test modules to a log with rc; also run tests.test_authentication_io unchanged as a
   sentinel (must still pass; you do not edit it). Never touch the real iCloud path; never the repository-wide
   suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys; body = the list of removed
   wrappers, the probe sites, counterfactuals, tails, rc.
