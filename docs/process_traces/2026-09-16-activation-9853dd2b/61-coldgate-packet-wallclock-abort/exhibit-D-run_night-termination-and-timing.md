# Exhibit D — scripts/run_night.py at main 5472ff53: timing constants, the process-group termination helper, the census loop's abort branch, the dead-man arithmetic (verbatim excerpts with line numbers)

```
62:CENSUS_INTERVAL_S = 30
64:COURIER_DEADLINE_S = 300
66:COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)
67:DEADMAN_GRACE_S = 3600
```

```
   390	def _terminate_process_group(
   391	    process: subprocess.Popen[Any],
   392	    night_dir: Path | None = None,
   393	    *,
   394	    pgid: int | None = None,
   395	) -> bool:
   396	    """Return True only when wait() proves that the child session exited."""
   397	
   398	    process_group = process.pid if pgid is None else pgid
   399	    try:
   400	        os.killpg(process_group, signal.SIGTERM)
   401	    except (ProcessLookupError, PermissionError):
   402	        pass
   403	    try:
   404	        exit_code = process.wait(timeout=30)
   405	    except subprocess.TimeoutExpired:
   406	        try:
   407	            os.killpg(process_group, signal.SIGKILL)
   408	        except (ProcessLookupError, PermissionError):
   409	            pass
   410	        try:
   411	            exit_code = process.wait(timeout=30)
   412	        except subprocess.TimeoutExpired:
   413	            return False
   414	    if night_dir is not None:
   415	        _record_chain_exit(night_dir, exit_code)
   416	    return True
   417	
   418	
   419	def _claim_chain_start(night_dir: Path) -> int | None:
   420	    try:
```

```
   538	def _run_chain_once(
   539	    chain_path: Path,
   540	    plan: NightPlan,
   541	    probes: Probes,
   542	    night_dir: Path,
   543	    claim_descriptor: int,
   544	    *,
   545	    command: list[str] | None = None,
   546	    abort_on_census: bool = True,
   547	) -> tuple[int | None, dict[str, Any] | None, int, list[dict[str, Any]], bool]:
   548	    """Run exactly one child session and continuously census it."""
   549	
   550	    census_path = night_dir / "censuses.jsonl"
   551	    stdout_path = night_dir / "chain.stdout.log"
   552	    stderr_path = night_dir / "chain.stderr.log"
   553	    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
   554	        environment = _chain_environment(plan, night_dir)
   555	        try:
   556	            process = subprocess.Popen(
   557	                command if command is not None else ["/bin/zsh", str(chain_path)],
   558	                stdin=subprocess.DEVNULL,
   559	                stdout=stdout,
   560	                stderr=stderr,
   561	                env=environment,
   562	                start_new_session=True,
   563	            )
   564	        except OSError as error:
   565	            launch_error = _complete_chain_launch_failure(claim_descriptor, error)
   566	            _record_chain_exit(night_dir, None, launch_failed=True)
   567	            return (
   568	                None,
   569	                _refusal_mapping(
   570	                    _CODES["chain_launch_failed"],
   571	                    "night chain process could not be launched",
   572	                    {"launch_error": launch_error},
   573	                ),
   574	                0,
   575	                [],
   576	                True,
   577	            )
   578	        pgid = _complete_chain_start(claim_descriptor, process, night_dir)
   579	        census_count = 0
   580	        census_hits: list[dict[str, Any]] = []
   581	        next_census = time.monotonic()
   582	        while process.poll() is None:
   583	            now = time.monotonic()
   584	            if now >= next_census:
   585	                probe, refusal = agent_census(probes)
   586	                record = _census_record(probe, refusal)
   587	                _append_census(census_path, probe, refusal)
   588	                census_count += 1
   589	                if refusal is not None:
   590	                    census_hits.append(record)
   591	                    if abort_on_census:
   592	                        proven = _terminate_process_group(
   593	                            process, night_dir, pgid=pgid
   594	                        )
   595	                        if not proven:
   596	                            _write_json(
   597	                                night_dir / "chain.unkilled",
   598	                                {"pgid": pgid, "epoch_s": time.time()},
   599	                            )
   600	                            return (
   601	                                process.poll(),
   602	                                _refusal_mapping(
   603	                                    _CODES["chain_alive"],
   604	                                    "process-group termination could not be proven",
   605	                                    record,
   606	                                ),
   607	                                census_count,
   608	                                census_hits,
   609	                                False,
   610	                            )
   611	                        return (
   612	                            process.poll(),
   613	                            _refusal_mapping(
   614	                                _CODES["aborted_agent_present"],
   615	                                "agent census refused while the chain was running",
   616	                                record,
   617	                            ),
   618	                            census_count,
   619	                            census_hits,
   620	                            True,
   621	                        )
   622	                next_census = now + CENSUS_INTERVAL_S
   623	            time.sleep(min(1.0, max(0.01, next_census - time.monotonic())))
   624	        exit_code = process.wait()
   625	        _record_chain_exit(night_dir, exit_code)
   626	        return exit_code, None, census_count, census_hits, True
   627	
   628	
```

```
1076:            (plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S + DEADMAN_GRACE_S)
1180:    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S
```
