# Exhibit B — the bind-loop ticker code at `73cdbbc4`

Source: `scripts/run_night.py` on branch `feat/2026-09-17-night-gate-quiet-admission`
at commit `73cdbbc46ab1862ee933b2074d25acc2cb444b97`, read in the detached
worktree `/Users/edr/code/JouleWise-wt-gate-quiet` with
`git show 73cdbbc4:scripts/run_night.py | nl -ba | sed -n '<a>,<b>p'`.
Line numbers are the file's own (`nl -ba`). Every block below is byte-exact
output of that command; nothing is paraphrased, reordered or elided inside a
block. The ranges are the ones exhibit A's delta-23 findings cite
(`S:2253,2263,2075,2078`; `S:2210,2052`; `S:2192,2422`; `S:2237`) plus the
surrounding context needed to check them for selective quotation.

## The invariant as the code states it (lines 1994-2000, 2048-2049)

```
  1994	
  1995	# A bounded protocol and two parent-owned service threads keep filesystem and
  1996	# exec work off the deadline-owning path. Neither service thread grants GO.
  1997	_BIND_MAX_PAYLOAD = 256 * 1024
  1998	_BIND_READ_BYTES = 64 * 1024
  1999	_BIND_READ_CALLS = 4
  2000	_BIND_MAX_JOBS = 32
  2048	class _BindLauncher:
  2049	    """Exec may wait for the executable's filesystem: do it off the ticker."""
```

The whole-file grep that found these two comments, run at `73cdbbc4`:

```
$ git show 73cdbbc4:scripts/run_night.py | nl -ba | grep -i "deadline-owning\|may wait for\|invariant"
  1996	# exec work off the deadline-owning path. Neither service thread grants GO.
  2049	    """Exec may wait for the executable's filesystem: do it off the ticker."""
```

## Lines 2050-2080 — `_BindLauncher`: the exec service thread, its `queue.Queue`, `submit`/`stop` (delta 23 F1 cites 2075, 2078; F2 cites 2052)

```
  2050	    def __init__(self):
  2051	        self.requests = queue.Queue(maxsize=_BIND_MAX_JOBS)
  2052	        threading.Thread(target=self._run, daemon=True, name='night-bind-launch').start()
  2053	
  2054	    def _run(self):
  2055	        while True:
  2056	            task = self.requests.get()
  2057	            if task is None:
  2058	                return
  2059	            try:
  2060	                if not task.cancelled:
  2061	                    argv = task.argv(task.writer)
  2062	                    # Publish the Popen object before __init__: pid becomes
  2063	                    # visible even if Popen is waiting for exec's error pipe.
  2064	                    task.process = subprocess.Popen.__new__(subprocess.Popen)
  2065	                    task.process.__init__(argv, start_new_session=True, close_fds=True, cwd=str(REPO_ROOT),
  2066	                        pass_fds=(task.writer,) + task.test_pass_fds, stdin=subprocess.DEVNULL,
  2067	                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  2068	            except Exception as error:
  2069	                task.launch_error = f'{type(error).__name__}: {error}'
  2070	            finally:
  2071	                os.close(task.writer)
  2072	                task.launch_done = True
  2073	
  2074	    def submit(self, task):
  2075	        self.requests.put_nowait(task)
  2076	
  2077	    def stop(self):
  2078	        self.requests.put_nowait(None)
  2079	
  2080	
```

## Lines 2150-2200 — `ready`/`result`/`cancel`/`poll_cleanup` with their bounded-work comments (delta 23 F3 cites 2192)

```
  2150	                return
  2151	
  2152	    def ready(self):
  2153	        # Cached flag lookup only; no child progress or transport operation.
  2154	        return self.envelope is not None
  2155	
  2156	    def result(self):
  2157	        # Cached capped object only; never read, join, or wait for EOF here.
  2158	        if self.envelope is None:
  2159	            raise night_gate.ProbeError('binding result is not published')
  2160	        if not self.envelope['ok']:
  2161	            raise night_gate.ProbeError(self.envelope['error'])
  2162	        return self.envelope['result']
  2163	
  2164	    def cancel(self):
  2165	        # One process-group signal and a fallback signal are non-waiting syscalls.
  2166	        self.cancelled = True
  2167	        pid = getattr(self.process, 'pid', None)
  2168	        if pid is not None:
  2169	            try:
  2170	                os.killpg(pid, signal.SIGKILL)
  2171	            except (ProcessLookupError, PermissionError):
  2172	                if not self.reaped:
  2173	                    try:
  2174	                        os.kill(pid, signal.SIGKILL)  # exec has not yet called setsid
  2175	                    except ProcessLookupError:
  2176	                        pass
  2177	
  2178	    def poll_cleanup(self):
  2179	        # One WNOHANG reap per tick; neither launch completion nor exit is awaited.
  2180	        if not self.cancelled:
  2181	            return False
  2182	        self.cancel()  # also reaches descendants when their direct parent exited
  2183	        pid = getattr(self.process, 'pid', None)
  2184	        if pid is not None and not self.reaped:
  2185	            try:
  2186	                found, status = os.waitpid(pid, os.WNOHANG)
  2187	                if found:
  2188	                    self.reaped = True
  2189	                    self.process.returncode = os.waitstatus_to_exitcode(status)
  2190	            except ChildProcessError:
  2191	                self.reaped = True
  2192	        if self.launch_done and (pid is None or self.reaped):
  2193	            if not self.closed:
  2194	                os.close(self.reader)
  2195	                self.closed = True
  2196	            return True
  2197	        return False
  2198	
  2199	
  2200	class _BindJournal:
```

## Lines 2200-2270 — `_BindJournal`: writer thread, `submit`, `stop` (delta 23 F1 cites 2253, 2263; F2 cites 2210; F6 cites 2237)

```
  2200	class _BindJournal:
  2201	    """Only this parent thread opens/writes/fsyncs journals; ACK follows fsync."""
  2202	    def __init__(self, night_dir):
  2203	        self.night_dir = night_dir
  2204	        self.requests = queue.Queue(maxsize=32)
  2205	        # An immutable snapshot is published in one assignment by the writer.
  2206	        self.snapshot = (0, hashlib.sha256(b'').hexdigest(), 0)
  2207	        self.failure = None
  2208	        self.submitted = 0
  2209	        self.done = False
  2210	        threading.Thread(target=self._run, daemon=True, name='night-bind-journal').start()
  2211	
  2212	    def _run(self):
  2213	        digest, lines = hashlib.sha256(), 0
  2214	        try:
  2215	            path = self.night_dir / 'quiet_samples.jsonl'
  2216	            # Startup replay is also off the ticker; never truncate old bytes.
  2217	            with path.open('ab+') as samples:
  2218	                samples.seek(0)
  2219	                for chunk in iter(lambda: samples.read(65536), b''):
  2220	                    digest.update(chunk)
  2221	                    lines += chunk.count(b'\n')
  2222	                self.snapshot = (0, digest.hexdigest(), lines)
  2223	                with (self.night_dir / 'censuses.jsonl').open('ab') as censuses:
  2224	                    while True:
  2225	                        item = self.requests.get()
  2226	                        if item is None or self.failure:
  2227	                            break
  2228	                        serial, kind, payload = item
  2229	                        handle = samples if kind == 'sample' else censuses
  2230	                        handle.write(payload)
  2231	                        handle.flush()
  2232	                        os.fsync(handle.fileno())
  2233	                        if kind == 'sample':
  2234	                            digest.update(payload)
  2235	                            lines += 1
  2236	                        self.snapshot = (serial, digest.hexdigest(), lines)
  2237	        except Exception as error:
  2238	            self.failure = f'{type(error).__name__}: {error}'
  2239	        finally:
  2240	            self.done = True
  2241	
  2242	    def submit(self, kind, value):
  2243	        # Immutable capped bytes + put_nowait; no filesystem operation or wait.
  2244	        try:
  2245	            payload = (json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode()
  2246	        except (ValueError, TypeError, RecursionError) as error:
  2247	            self.failure = f'journal record encoding failed: {error}'
  2248	            return None
  2249	        if len(payload) > _BIND_MAX_PAYLOAD:
  2250	            self.failure = 'journal record exceeds 256 KiB cap'
  2251	            return None
  2252	        try:
  2253	            self.requests.put_nowait((self.submitted + 1, kind, payload))
  2254	            self.submitted += 1
  2255	            return self.submitted
  2256	        except queue.Full:
  2257	            self.failure = 'journal queue saturated'
  2258	            return None
  2259	
  2260	    def stop(self):
  2261	        # Nonblocking sentinel submission; a stuck writer is never joined.
  2262	        try:
  2263	            self.requests.put_nowait(None)
  2264	        except queue.Full:
  2265	            self.failure = self.failure or 'journal queue saturated during cleanup'
  2266	
  2267	
  2268	def _binding_census(probes):
  2269	    probe, refusal = agent_census(probes)
  2270	    if (probe.exit_code not in (0, 1) or (probe.exit_code == 1 and probe.stdout.strip())
```

## Lines 2295-2300 — the binding entry: policy validation and the deadline epoch

```
  2295	    if sampler is not None and test_dispatch is None:
  2296	        raise ValueError("injected samplers require the explicit test_dispatch hook")
  2297	    policy = quiet_admission.validate_policy(plan.quiet_admission, window_max_s=plan.window_max_s)
  2298	    start_epoch_s = float(probes.now_epoch_s()) if start_epoch_s is None else start_epoch_s
  2299	    start_monotonic = monotonic() if start_monotonic is None else start_monotonic
  2300	    deadline_epoch = quiet_admission.bind_deadline_epoch(plan)
```

## Lines 2385-2430 — the tick loop head: deadline, census cadence, local sample timeout, transport advance, cleanup poll (delta 23 F3 cites 2422)

```
  2385	
  2386	    try:
  2387	        while True:
  2388	            try:
  2389	                # 1. Two clock reads and comparisons; absolute deadline is never recomputed.
  2390	                now = monotonic()
  2391	                if now >= deadline and phase != 'cleanup':
  2392	                    stop(_CODES['refused_bind_expired'], 'bind deadline expired')
  2393	                # 2. At most one cadence submission, using a bounded nonblocking queue.
  2394	                if phase != 'cleanup' and now >= next_census:
  2395	                    censuses.append(start('census', census_call, {}))
  2396	                    next_census += CENSUS_INTERVAL_S
  2397	                # A local timeout interrupts this interval, resets the run, and retries.
  2398	                if phase == 'sample' and foreground is not None:
  2399	                    began = next(at for job, _, at in jobs.values() if job is foreground)
  2400	                    if now >= began + policy['sample_interval_s'] + _BIND_SAMPLE_GRACE_S:
  2401	                        foreground.cancel()
  2402	                        foreground = None
  2403	                        quiet_run = 0
  2404	                        append_sample('error', night_gate.Refusal(_CODES['probe_error'], 'sample local deadline expired', ()))
  2405	                        phase = 'ack'
  2406	
  2407	                # 3. Fixed job-count cap times fixed read/byte budgets; no worker waits.
  2408	                for job, _, _ in list(jobs.values()):
  2409	                    job.advance()
  2410	                # 4. Fixed job-count cap times WNOHANG; cleanup runs on EVERY tick.
  2411	                for key, (job, _, _) in list(jobs.items()):
  2412	                    if job.poll_cleanup():
  2413	                        del jobs[key]
  2414	
  2415	                # All processing below handles bounded cached results, never pipe I/O.
  2416	                if writer.failure and phase != 'cleanup':
  2417	                    stop(_CODES['probe_error'], 'journal failure: ' + writer.failure)
  2418	                if phase == 'cleanup':
  2419	                    if not writer_stopped:
  2420	                        writer.stop()
  2421	                        writer_stopped = True
  2422	                    if not jobs:
  2423	                        if writer.done:
  2424	                            break
  2425	                        if time.perf_counter() >= cleanup_until:
  2426	                            writer.failure = writer.failure or 'journal acknowledgement unavailable at cleanup deadline'
  2427	                            break
  2428	                    # Refusal already latched: fake admission time need not advance during reaping.
  2429	                    sleep(0)
  2430	                    time.sleep(0.001)
```

## Lines 2485-2560 — ACK/phase transitions, the bounded yield, `finally` cleanup and the summary the receipt carries

```
  2485	
  2486	                # ACK and reaping are flags only; final checks follow storage ACK
  2487	                # so a slow filesystem cannot age hard predicates into a later GO.
  2488	                if phase in ('ack', 'go-ack') and writer.snapshot[0] >= (final_ack or math.inf):
  2489	                    if phase == 'go-ack':
  2490	                        if not censuses and not jobs:
  2491	                            phase = 'final'
  2492	                    else:
  2493	                        phase = 'pre'
  2494	                if phase == 'go-ready':
  2495	                    if censuses:
  2496	                        phase = 'go-ack'  # refresh final checks after delayed census
  2497	                    elif not jobs:
  2498	                        go_epoch = wall_clock()
  2499	                        if go_epoch < baseline_wall or go_epoch > deadline_epoch:
  2500	                            stop(_CODES['refused_boot_clock'], 'wall clock moved outside final-check/bind bounds')
  2501	                        else:
  2502	                            phase = 'cleanup'
  2503	                            cleanup_until = time.perf_counter() + _BIND_JOURNAL_FLUSH_S
  2504	                        continue
  2505	
  2506	                if foreground is None:
  2507	                    if phase == 'static':
  2508	                        foreground = start('static', lambda: night_gate.evaluate_static(plan, probes), {'plan': asdict(plan)})
  2509	                    elif phase in ('pre', 'post', 'final'):
  2510	                        if phase == 'pre':
  2511	                            pending = dict(wall_start=wall_clock(),
  2512	                                monotonic_start=now, boot_identity=baseline_boot, raw_sha256={}, metrics={})
  2513	                        foreground = start('hard', lambda: night_gate.evaluate_dynamic_hard(plan, probes, static),
  2514	                            {'plan': asdict(plan), 'static': json.loads(static.to_json_bytes())})
  2515	                    elif phase == 'sample':
  2516	                        foreground = start('sample', sampler, {'interval': policy['sample_interval_s'], 'observer_pid': os.getpid()})
  2517	                # Yield at most 50 ms; this is an explicit bounded timer, not a worker wait.
  2518	                if phase in ('ack', 'go-ack', 'go-ready') or (foreground is not None and foreground.ready()):
  2519	                    sleep(0)
  2520	                    time.sleep(0.001)
  2521	                else:
  2522	                    sleep(min(0.05, max(0, deadline - monotonic())))
  2523	            except Exception as error:
  2524	                stop(_CODES['probe_error'], f'binding observation failed: {type(error).__name__}: {error}')
  2525	    finally:
  2526	        if not writer_stopped:
  2527	            writer.stop()
  2528	        launcher.stop()
  2529	
  2530	    # Immutable ACK snapshot only: no finish-time journal read or child wait.
  2531	    _, digest, lines = writer.snapshot
  2532	    metrics = last.get('metrics', {}) if last else {}
  2533	    summary = dict(quiet_admission=policy, admission_is_capture_evidence=False,
  2534	        bind_deadline_epoch_s=deadline_epoch, go_epoch_s=None if refusal else go_epoch,
  2535	        samples_total=lines, samples_quiet_run_at_go=0 if refusal else quiet_run,
  2536	        quiet_samples_sha256=digest, quiet_samples_lines=lines,
  2537	        top_consumers_at_decision=metrics.get('top_consumers', []),
  2538	        load_avg_diagnostic=last.get('load_avg_diagnostic', {}) if last else {'error': 'no completed observation'},
  2539	        observer_cpu_s=max(0, _bind_cpu() - cpu_start))
  2540	    if writer.failure:
  2541	        summary['journal_failure'] = writer.failure
  2542	        if refusal is None:
  2543	            refusal = night_gate.Refusal(_CODES['probe_error'], 'journal failure: ' + writer.failure, ())
  2544	            summary.update(go_epoch_s=None, samples_quiet_run_at_go=0)
  2545	    if last and 'boot_identity_unavailable' in last:
  2546	        summary['boot_identity_unavailable'] = last['boot_identity_unavailable']
  2547	    if not summary['top_consumers_at_decision']:
  2548	        summary['attribution_unavailable'] = 'no measurable process deltas before decision'
  2549	    if refusal and refusal.reason == _CODES['refused_bind_expired']:
  2550	        refusal = replace(refusal, detail=refusal.detail + '; ' + json.dumps(dict(
  2551	            samples_total=lines, last_busy_cores=metrics.get('busy_cores'),
  2552	            top_consumers=summary['top_consumers_at_decision'], quiet_samples_sha256=digest,
  2553	            quiet_samples_lines=lines), sort_keys=True))
  2554	    return replace(current, schema=night_gate.QUIET_RECEIPT_SCHEMA, admission=summary,
  2555	        verdict='REFUSED' if refusal else ('REHEARSAL_ONLY' if plan.receipt_class == 'REHEARSAL_STUB' else 'GO'),
  2556	        refusal=refusal, authored_monotonic_ns=max(0, int(monotonic() * 1e9)))
  2557	
  2558	
  2559	def smoke_observation_round(interval_s):
  2560	    """Plan-free read-only round using production exec, census and journal work.
```

