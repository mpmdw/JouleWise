# Q5 execution-lens evidence at efdaed879e1d13d06de719f10a4b7b504601cdb4

Production module, tests, and shell were unchanged. Real OS signals were delivered in child processes. The fake launchctl from tests/test_night_agent_install.py was the only launchctl executable. SIGKILL crash-seam coverage is explicitly out of scope.

Each interpreter has 317 cells: 305 primary cells and 12 additional signals inside the teardown body. Both standard foreground dispositions and six explicitly raising prior-disposition diagnostic cells were tested. The entry mask contains SIGUSR1 and differs from the construction mask.

Behavior pass requires return-code fidelity, no escaped exception, restoration of the invocation mask and all three dispositions, one effective teardown, and evidence that injection occurred. Strict pass also requires exactly one literal _teardown call; uninstall instead requires exactly one verified_bootout call because uninstall does not call Transaction._teardown. Coldgate-06 ruling 10(e) expressly permits the second terminal no-op _teardown in the except-body path; the literal count is therefore reported separately.

| Seam | Interpreter | Behavior pass | Strict pass |
|---|---|---:|---:|
| a_committed | 3.14.7 | 6/6 | 6/6 |
| a_committed | 3.9.6 | 6/6 | 6/6 |
| a_last_mutation | 3.14.7 | 6/6 | 6/6 |
| a_last_mutation | 3.9.6 | 6/6 | 6/6 |
| b_except | 3.14.7 | 6/6 | 0/6 |
| b_except | 3.9.6 | 6/6 | 0/6 |
| c_unwind_entry | 3.14.7 | 12/12 | 12/12 |
| c_unwind_entry | 3.9.6 | 12/12 | 12/12 |
| d_uninstall_block | 3.14.7 | 12/12 | 12/12 |
| d_uninstall_block | 3.9.6 | 12/12 | 12/12 |
| e_restore_loop | 3.14.7 | 162/222 | 162/222 |
| e_restore_loop | 3.9.6 | 162/222 | 162/222 |
| f_pair_entry | 3.14.7 | 4/4 | 4/4 |
| f_pair_entry | 3.9.6 | 4/4 | 4/4 |
| f_pair_sequential | 3.14.7 | 4/4 | 4/4 |
| f_pair_sequential | 3.9.6 | 4/4 | 4/4 |
| g_teardown | 3.14.7 | 12/12 | 12/12 |
| g_teardown | 3.9.6 | 12/12 | 12/12 |
| g_teardown_body | 3.14.7 | 12/12 | 12/12 |
| g_teardown_body | 3.9.6 | 12/12 | 12/12 |
| i_unwind_block | 3.14.7 | 12/12 | 12/12 |
| i_unwind_block | 3.9.6 | 12/12 | 12/12 |
| j_external_bootstrap | 3.14.7 | 6/6 | 6/6 |
| j_external_bootstrap | 3.9.6 | 6/6 | 6/6 |
| k_external_bootout | 3.14.7 | 3/3 | 3/3 |
| k_external_bootout | 3.9.6 | 3/3 | 3/3 |

## Exact failing cells and tracebacks

A negative process status is subprocess returncode (e.g. -15 = SIGTERM; shell status 143). Kernel termination cannot produce a Python traceback. In those cells checkpoint.json preserves the exact injection edge and completed teardown, and no normal return was observed.

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0002

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGTERM"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 143, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 143, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0049

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGINT"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 130, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 130, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0096

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGHUP"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 129, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 129, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0020

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0021

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0147

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGTERM"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 143, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 143, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0022

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0032

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0033

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0034

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0194

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGINT"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 130, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 130, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0044

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0045

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0046

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0241

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGHUP"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 129, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 129, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0065

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0066

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0067

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0068

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0069

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0077

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0078

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0079

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0080

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0081

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0089

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0090

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0091

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0092

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0093

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0116

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0128

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0140

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0165

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0166

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0167

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0177

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0178

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0179

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0189

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0190

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "1"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0191

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0210

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0211

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0212

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0213

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0214

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0222

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0223

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0224

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0225

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0226

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0234

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0235

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0236

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0237

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0238

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0261

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0273

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0285

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.14.7",
  "executable": "/opt/homebrew/opt/python@3.14/bin/python3.14",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "0",
    "1": "0"
  }
}
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0293

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 15
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0294

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 15
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0298

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0299

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 2
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0303

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
                                                                             ~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
    ~~~~~~~~~~~~^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 1
```

### 3.14.7 execution-lens-results execution-lens-results/py3.14.7/0304

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
             ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/signal.py", line 71, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 1
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0002

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGTERM"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 143, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 143, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0049

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGINT"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 130, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 130, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0096

Spec: `{"delivery": "self", "mode": "refusal", "seam": "b_except", "signal": "SIGHUP"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 129, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 129, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0020

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0021

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0022

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0147

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGTERM"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 143, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 143, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0032

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0033

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0034

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0194

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGINT"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 130, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 130, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0044

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0045

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0046

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0065

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0066

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0241

Spec: `{"delivery": "fake", "mode": "refusal", "seam": "b_except", "signal": "SIGHUP"}`

Observed: `{"checks": {"both_pending": true, "code": true, "dispositions": true, "injected": true, "mask": true, "returned": true, "teardown": true}, "dispositions_restored": true, "expected": 129, "mask_restored": true, "process_rc": 0, "process_terminated": null, "result": 129, "state": "ROLLED_BACK", "teardown_calls": 2, "teardown_effects": 1}`

Literal exactly-once assertion traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_audit.py", line 25, in <module>
    assert observed['teardown_calls']==1, '_teardown must be called exactly once; observed {}'.format(observed['teardown_calls'])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: _teardown must be called exactly once; observed 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0067

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0068

Spec: `{"delivery": "self", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0069

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0077

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0078

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0079

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0080

Spec: `{"delivery": "self", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0081

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0089

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0090

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0091

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0092

Spec: `{"delivery": "self", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0093

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0116

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0128

Spec: `{"delivery": "self", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0140

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGHUP",
    "delivery": "self",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0165

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0166

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0167

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0177

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0178

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0179

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0189

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 5}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 5,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0190

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "before"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_IGN"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0191

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -15, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGTERM",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    15
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_15",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0210

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0211

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0212

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0213

Spec: `{"delivery": "fake", "edge": "before", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0214

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0222

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0223

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0224

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0225

Spec: `{"delivery": "fake", "edge": "before", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0226

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "SUCCESS", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0234

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 4}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0235

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0236

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 5}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0237

Spec: `{"delivery": "fake", "edge": "before", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0238

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
KeyboardInterrupt
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0261

Spec: `{"delivery": "fake", "edge": "after", "mode": "refusal", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "refusal",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "ROLLED_BACK",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0273

Spec: `{"delivery": "fake", "edge": "after", "mode": "commit", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "commit",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 1,
  "teardown_effects": 1,
  "verified_bootout_calls": 0,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "SUCCESS",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0285

Spec: `{"delivery": "fake", "edge": "after", "mode": "uninstall", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": null, "dispositions_restored": null, "expected": null, "mask_restored": null, "process_rc": -1, "process_terminated": true, "result": null, "state": null, "teardown_calls": null, "teardown_effects": null}`

No Python traceback: kernel signal termination. Last checkpoint:
```json
{
  "spec": {
    "seam": "e_restore_loop",
    "mode": "uninstall",
    "signal": "SIGHUP",
    "delivery": "fake",
    "slot": 6,
    "edge": "after"
  },
  "python": "3.9.6",
  "executable": "/Library/Developer/CommandLineTools/usr/bin/python3",
  "teardown_calls": 0,
  "teardown_effects": 0,
  "verified_bootout_calls": 1,
  "injections": [
    1
  ],
  "restored_disposition_deliveries": [],
  "last_event": "before_kill_1",
  "state": "PARSED",
  "mask_at_event": [
    1,
    2,
    15,
    30
  ],
  "dispositions_at_event": {
    "2": "<built-in function default_int_handler>",
    "15": "Handlers.SIG_DFL",
    "1": "Handlers.SIG_DFL"
  }
}
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0293

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 15
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0294

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGTERM", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 15
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0298

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0299

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGINT", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 2
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0303

Spec: `{"delivery": "self", "edge": "after", "mode": "refusal", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 3, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "ROLLED_BACK", "teardown_calls": 1, "teardown_effects": 1}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 509, in run
    self._unwind()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 438, in _unwind
    signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 1
```

### 3.9.6 execution-lens-results execution-lens-results/py3.9.6/0304

Spec: `{"delivery": "self", "edge": "after", "mode": "uninstall", "prior": "raises", "seam": "e_restore_loop", "signal": "SIGHUP", "slot": 6}`

Observed: `{"checks": {"both_pending": true, "code": false, "dispositions": true, "injected": true, "mask": true, "returned": false, "teardown": true}, "dispositions_restored": true, "expected": 0, "mask_restored": true, "process_rc": 1, "process_terminated": null, "result": null, "state": "PARSED", "teardown_calls": 0, "teardown_effects": 0}`

Runtime traceback:
```text
Traceback (most recent call last):
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 215, in cell
    result = e.uninstall(adapter, stderr=io.StringIO()) if uninstalling else machine.run()
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/joulewise/night_agent_install.py", line 552, in uninstall
    signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 181, in wrapped_mask
    value = REAL_MASK(how, mask)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/signal.py", line 60, in pthread_sigmask
    sigs_set = _signal.pthread_sigmask(how, mask)
  File "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/exec-lens-copy/execution_lens_probe.py", line 34, in prior_raises
    raise PriorSignal('restored disposition delivered {}'.format(number))
cell.<locals>.PriorSignal: restored disposition delivered 1
```

## Harness checksums

- `execution_lens_audit.py` SHA256 `3247c6cac2753cb4b212fc9b0a8fb634ca0399fbeb9ad53c37bfeb18ef842638`
- `execution_lens_aux.py` SHA256 `2866783177f886dfceaa28e4ab25d89acaff37ff589bbe66f9fd5dcb386161db`
- `execution_lens_probe.py` SHA256 `90a5f9133529c41d626a2b48687f6671a180f3b53de8565a21085f9d86a5dfce`
- `execution_lens_probe_body.py` SHA256 `1f1f92ab5ca5c7551aad2c6de9ef278f4b9a44582f3644b651e811dc3c976ef6`
