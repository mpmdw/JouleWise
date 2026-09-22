# Exhibit A — code and diff at the pinned revisions (feature head `489b0953`, scratch `447fd6bf..e52c7fbc`)

Generator output. Every extract below is `git show <rev>:<path>` located by `ast` or by the printed anchor string, with 1-based line numbers of the file at that revision. Nothing is paraphrased and nothing is hand-trimmed.

### Module constants (each with the contiguous comment block above it)

## A — `joulewise/quiet_predicate_campaign.py:47-52` at `489b0953` — `TIMED_LOG_MARKERS`

```python
   47  # ``timed`` writes one of these whenever it APPLIES a correction: a slewed
   48  # frequency/offset adjustment (``cmd,apply,src,``), the adjtime syscall, or a
   49  # hard step.  They are emitted at level Df, which plain ``log show`` drops --
   50  # hence ``--info --debug`` (ruling 14 R4 NIT: without them the scanner would
   51  # silently attest every envelope).
   52  TIMED_LOG_MARKERS = ("cmd,apply,src,", "ntp_adjtime", "settimeofday")
```

## A — `joulewise/quiet_predicate_campaign.py:53-53` at `489b0953` — `TIMED_LOG_PREDICATE`

```python
   53  TIMED_LOG_PREDICATE = 'process == "timed"'
```

## A — `joulewise/quiet_predicate_campaign.py:443-450` at `489b0953` — `TIMED_LOG_HEADER_FIELDS`

```python
  443  # `log show --style syslog` prints a column header -- `Timestamp ... Ty
  444  # Process[PID:TID]` -- before any entry, and prints it even when nothing
  445  # matched the predicate; the packet's own exhibit D opens with that line.  A
  446  # body that does not carry it therefore did not come from a query that ran:
  447  # zero bytes, an HTML error page or a truncated pipe all land here.  Such a
  448  # result must never buy `authenticated`, the one claim-bearing state, on the
  449  # reasoning that it "matched no correction".
  450  TIMED_LOG_HEADER_FIELDS = ("Timestamp", "Process")
```

## A — `joulewise/quiet_predicate_campaign.py:572-576` at `489b0953` — `ATTESTATION_TIMEOUT_FLOOR_S`

```python
  572  # The smallest query bound worth attempting.  A `log show` over one envelope's
  573  # window took 0.70-1.45 s on this machine (A269 gate C4), so five seconds is
  574  # already generous; it exists only so a registration with a tiny gap asks for a
  575  # real query rather than one guaranteed to time out.
  576  ATTESTATION_TIMEOUT_FLOOR_S = 5
```

## A — `joulewise/quiet_predicate_campaign.py:976-983` at `489b0953` — `CLEANUP_BUDGET_RESERVE_S`

```python
  976  # The gap between the end of one capture and the next spawn (20 s under v2:
  977  # slot_pitch_s 620 - envelope_s 600) holds the collector's exit, the plist
  978  # parse, the anchor derivation, the group teardown and the clock attestation.
  979  # The teardown's budget is the gap minus a reserve that the attestation's
  980  # `log show` fits in (worst observed 1.45 s; A269 gate C4 measured 0.70/0.84 s),
  981  # so a teardown can never eat the attestation's time or run into the next
  982  # spawn.  Derived from the registration at the call site, never a literal.
  983  CLEANUP_BUDGET_RESERVE_S = 5
```

### Functions

## A — `joulewise/quiet_predicate_campaign.py:429-440` at `489b0953` — `timed_log_argv`

```python
  429  def timed_log_argv(start_epoch_s, end_epoch_s):
  430      """``log show`` over one envelope's capture window, timed process only.
  431  
  432      ``log show`` takes LOCAL wall time as ``YYYY-MM-DD HH:MM:SS``.
  433      """
  434  
  435      def local(epoch_s):
  436          return datetime.fromtimestamp(epoch_s).strftime("%Y-%m-%d %H:%M:%S")
  437  
  438      return (LOG, "show", "--info", "--debug", "--style", "syslog",
  439              "--predicate", TIMED_LOG_PREDICATE,
  440              "--start", local(start_epoch_s), "--end", local(end_epoch_s))
```

## A — `joulewise/quiet_predicate_campaign.py:453-456` at `489b0953` — `timed_log_has_header`

```python
  453  def timed_log_has_header(text):
  454      """Did this body come from a ``log show`` that actually produced output?"""
  455      first = text.splitlines()[0] if text else ""
  456      return all(field in first for field in TIMED_LOG_HEADER_FIELDS)
```

## A — `joulewise/quiet_predicate_campaign.py:459-472` at `489b0953` — `timed_log_window_epoch_s`

```python
  459  def timed_log_window_epoch_s(argv):
  460      """The epochs the ``--start``/``--end`` strings actually name.
  461  
  462      ``timed_log_argv`` formats local wall time to whole seconds, so the query
  463      really runs over the union window TRUNCATED at both ends (wider at the
  464      start, and still past ``sampling_stopped`` at the end because of the one
  465      second of pad).  ``window_epoch_s`` keeps the float union window the
  466      envelope was placed by; this is what the argv strings say, parsed back
  467      from those same strings, so an auditor reading the record never has to
  468      re-derive the truncation to know what was queried.
  469      """
  470  
  471      return [datetime.strptime(argv[argv.index(flag) + 1], "%Y-%m-%d %H:%M:%S").timestamp()
  472              for flag in ("--start", "--end")]
```

## A — `joulewise/quiet_predicate_campaign.py:579-601` at `489b0953` — `attestation_timeout_s`

```python
  579  def attestation_timeout_s(protocol):
  580      """Bound the clock query by the GAP it runs in, never by a literal.
  581  
  582      The query runs between the end of one capture and the next spawn, and that
  583      inter-slot gap is ``slot_pitch_s - envelope_s`` (20 s under v2).  The
  584      retired literal of 300 s was thirty times the 10 s drift exclusion and a
  585      hundred and fifty times the 2 s abort bar: one slow `logd` would have
  586      pushed every later envelope off its schedule, and nothing measured the
  587      cost.  The bound here is the gap less the same
  588      ``CLEANUP_BUDGET_RESERVE_S`` the teardown leaves, floored at
  589      ``ATTESTATION_TIMEOUT_FLOOR_S``: 15 s under v2.  A timeout is not a
  590      failure of the night -- the envelope becomes ``asserted`` and excluded,
  591      which is the state a missing query already has.
  592  
  593      A teardown that spends its full 15 s budget AND a query that spends its
  594      full 15 s bound still exceed the 20 s gap; that residual is deliberate and
  595      visible rather than silent, because the next slot's spawn then drifts past
  596      ``start_drift_abort_s`` and the night ends REFUSED at a named abort
  597      instead of producing envelopes nobody can place on the wall timeline.
  598      """
  599  
  600      gap = protocol["slot_pitch_s"] - protocol["envelope_s"]
  601      return max(ATTESTATION_TIMEOUT_FLOOR_S, gap - CLEANUP_BUDGET_RESERVE_S)
```

## A — `joulewise/quiet_predicate_campaign.py:604-669` at `489b0953` — `attest_network_time`

```python
  604  def attest_network_time(out, blocked=None, timeout=ATTESTATION_TIMEOUT_FLOOR_S):
  605      """Authenticate one envelope's clock discipline from the ``timed`` log.
  606  
  607      A set-command receipt proves an instruction was accepted; it does not
  608      prove no correction was applied during the capture.  The unified log does:
  609      ``timed`` records every applied slew or step.  Zero matched lines over the
  610      capture window (:func:`attestation_window`) is an AUTHENTICATED envelope;
  611      any match is ``slew_attested`` and excluded; a failed query, or one that
  612      must not run because the capture is not provably over (``blocked``), is
  613      ``asserted`` and excluded.  Run immediately after the collector exits and
  614      its groups are reaped, because the log store is rotated -- never deferred
  615      to harvest.
  616      """
  617  
  618      attestation = {"state": "asserted", "method": TIMED_LOG_ATTESTATION_METHOD,
  619                     "window_epoch_s": None, "window_method": ATTESTATION_WINDOW_METHOD,
  620                     "log": None, "log_sha256": None,
  621                     "matched_lines": None, "exit_code": None, "argv": None,
  622                     "attested_epoch_s": time.time()}
  623      if blocked:
  624          attestation["reason"] = "attestation not run beside a live capture: " + blocked
  625          return attestation
  626      try:
  627          session = json.loads((out / "session.json").read_text())
  628          stamps = session["power"]["anchor"]["clock_stamps"]
  629          window = attestation_window(stamps)
  630          if not all(math.isfinite(moment) for moment in window):
  631              raise ValueError(f"capture window is not finite: {window}")
  632          # Formatting the window is inside the guard too: an absurd but finite
  633          # epoch (1e300) raises OverflowError out of `datetime.fromtimestamp`,
  634          # and an envelope whose window cannot even be written down is
  635          # `asserted`, never a traceback that ends the night.
  636          argv = timed_log_argv(*window)
  637          window_argv = timed_log_window_epoch_s(argv)
  638      except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
  639          attestation["reason"] = f"capture window unavailable: {type(exc).__name__}: {exc}"
  640          return attestation
  641      attestation.update(window_epoch_s=window, argv=list(argv),
  642                         window_argv_epoch_s=window_argv)
  643      try:
  644          completed = subprocess.run(list(argv), capture_output=True, text=True, timeout=timeout)
  645          path = out / TIMED_LOG_BASENAME
  646          path.write_text(completed.stdout)
  647      except subprocess.TimeoutExpired:
  648          # The query is abandoned at the gap's edge, not at 300 s: the envelope
  649          # loses its claim-bearing state, the night keeps its schedule.
  650          attestation["reason"] = f"timed log query timed out after {timeout:g} s"
  651          return attestation
  652      except (OSError, subprocess.SubprocessError) as exc:
  653          attestation["reason"] = f"timed log query failed: {type(exc).__name__}: {exc}"
  654          return attestation
  655      matched = timed_log_matches(completed.stdout)
  656      attestation.update(exit_code=completed.returncode, log=path.name,
  657                         log_sha256=digest(path.read_bytes()), matched_lines=matched,
  658                         matched_marker_lines=timed_log_marker_lines(completed.stdout))
  659      if completed.returncode != 0:
  660          attestation["reason"] = f"timed log query exited {completed.returncode}"
  661      elif not timed_log_has_header(completed.stdout):
  662          attestation["reason"] = "timed log query returned no header"
  663      elif matched:
  664          attestation.update(state="slew_attested",
  665                             reason=f"{matched} applied clock corrections inside the capture window")
  666      else:
  667          attestation.update(state="authenticated",
  668                             reason="no applied clock correction inside the capture window")
  669      return attestation
```

## A — `joulewise/quiet_predicate_campaign.py:672-714` at `489b0953` — `record_attestation`

```python
  672  def record_attestation(out, attestation):
  673      """Add the attestation to the envelope's own provenance, atomically.
  674  
  675      The collector has exited, so the chain owns this write; temp plus rename
  676      means a reader never sees a half-written session record, and a write that
  677      cannot land is reported in the attestation rather than raised (an
  678      unwritable envelope directory used to refuse the whole night from here).
  679      The attestation carries ``session_sha256_before`` -- the digest of the
  680      file this rewrite replaced -- so the one edit made after the collector
  681      exits is auditable from the record itself (A269 ruling 10 Q4 iii).
  682      Nothing else rewrites ``session.json`` after the collector exits:
  683      under cure 2 there is no finaliser pass, so this digest can only ever
  684      name the collector's own bytes.
  685      """
  686  
  687      path = out / "session.json"
  688      try:
  689          raw = path.read_bytes()
  690          session = json.loads(raw)
  691      except (OSError, ValueError):
  692          return False
  693      attestation["session_sha256_before"] = digest(raw)
  694      provenance = session.get("network_time_provenance")
  695      if not isinstance(provenance, dict):
  696          provenance = {"state": "unknown",
  697                        "reason": "collector recorded no network-time provenance"}
  698      provenance["attestation"] = attestation
  699      session["network_time_provenance"] = provenance
  700      temporary = path.with_name(path.name + ".tmp")
  701      try:
  702          temporary.write_text(json.dumps(session, sort_keys=True, indent=2, allow_nan=False) + "\n")
  703          os.replace(temporary, path)
  704      except OSError as exc:
  705          # One envelope's annotation must never refuse the NIGHT.  The write is
  706          # an annotation on a capture that is already complete and already on
  707          # disk; if it cannot land, the envelope loses its claim-bearing state
  708          # and says why.  `pilot_summary` reads the executor's own envelope
  709          # entry whenever the session record carries no attestation, so the
  710          # `asserted` state set here is the state the summary sees.
  711          attestation["state"] = "asserted"
  712          attestation["reason"] = f"session rewrite failed: {type(exc).__name__}: {exc}"
  713          return False
  714      return True
```

## A — `joulewise/quiet_predicate_campaign.py:356-426` at `489b0953` — `restore_network_time`

```python
  356  def restore_network_time(night_dir):
  357      """Turn network time back ON, on every path; report, never hide, failure.
  358  
  359      Runs as the first action of the executor's ``finally`` (after the signal
  360      handlers are neutralised), so a refusal, an exception and a SIGTERM all
  361      leave the machine as they found it.  The READ form is outside the sudoers
  362      slice -- the two ``systemsetup`` set forms the NOPASSWD entry grants -- so
  363      the prior state is unknowable without a password and ON is the ruled end
  364      state.  A failed restore does NOT invalidate the envelopes already
  365      captured under a proven OFF: it is reported as
  366      ``network_time_restored: false`` and a distinct exit code.
  367  
  368      Two rules hold the receipt itself.  (1) The ON receipt is added to the
  369      control record ONLY when that record is absent (nothing was established
  370      yet, so there are no bytes to protect) or reads back as an object.  A record
  371      that is unreadable, or parses to a list, a string, a number or ``null``,
  372      keeps its bytes and the receipt goes to a sibling
  373      ``network_time_control.restore.json``: rewriting it as ``{"off": null,
  374      ...}`` would leave an artifact asserting OFF was never established for a
  375      night whose every envelope carries the digest of the original bytes.
  376      (2) Nothing raises out of here.  This is the ``finally``; an exception
  377      escaping it replaces a measured outcome -- the outcome document, the
  378      refusal, the summary -- with no outcome at all, which is precisely what a
  379      control record parsing to ``null`` used to do (``TypeError`` on item
  380      assignment, caught by no except tuple in the call chain).
  381      """
  382  
  383      try:
  384          path = night_dir / NETWORK_TIME_CONTROL_BASENAME
  385          if not path.exists():
  386              # Nothing was ever established (a refusal before the toggle): no
  387              # bytes to protect, so the restore opens the record itself.
  388              control = {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None}
  389          else:
  390              try:
  391                  control = json.loads(path.read_text())
  392              except (OSError, ValueError):
  393                  control = None
  394          try:
  395              on = set_network_time("on")
  396          except Exception as exc:  # noqa: BLE001 - see rule (2) above
  397              on = {"argv": list(network_time_argv("on")), "exit_code": None, "stdout": None,
  398                    "error": f"{type(exc).__name__}: {exc}", "epoch_s": None, "monotonic_s": None}
  399          try:
  400              if isinstance(control, dict):
  401                  control["on"] = on
  402                  write_control_record(path, control)
  403              else:
  404                  write_control_record(night_dir / NETWORK_TIME_RESTORE_BASENAME,
  405                                       {"schema": NETWORK_TIME_CONTROL_SCHEMA,
  406                                        "off": {"state": "unreadable",
  407                                                "reason": f"{NETWORK_TIME_CONTROL_BASENAME} is "
  408                                                          "not a readable control record",
  409                                                "record": NETWORK_TIME_CONTROL_BASENAME},
  410                                        "on": on})
  411          except Exception:  # noqa: BLE001
  412              pass  # The exit code still reports the restore; never mask it here.
  413          # Success is the set form's own exit code: no READ form exists in the
  414          # slice to confirm the state, and no stdout comparator for ON is ruled.
  415          return on["exit_code"] == 0
  416      except Exception as exc:  # noqa: BLE001 - rule (2): the finally is sacred
  417          try:
  418              write_control_record(night_dir / NETWORK_TIME_RESTORE_BASENAME,
  419                                   {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None,
  420                                    "on": {"argv": list(network_time_argv("on")),
  421                                           "exit_code": None, "stdout": None,
  422                                           "error": f"{type(exc).__name__}: {exc}",
  423                                           "epoch_s": None, "monotonic_s": None}})
  424          except Exception:  # noqa: BLE001
  425              pass
  426          return False
```

## A — `joulewise/quiet_predicate_campaign.py:986-989` at `489b0953` — `cleanup_budget_s`

```python
  986  def cleanup_budget_s(protocol):
  987      """The per-slot teardown budget: the gap, less the attestation reserve."""
  988      gap = protocol["slot_pitch_s"] - protocol["envelope_s"]
  989      return max(1, gap - CLEANUP_BUDGET_RESERVE_S)
```

### Two sections of `execute`

