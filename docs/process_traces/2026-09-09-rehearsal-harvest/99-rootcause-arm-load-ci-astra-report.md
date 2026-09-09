```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed: short host uptime makes the synthetic command-capture start negative; the fixed RAW anchor is not the failing comparison.",
  "workspace": {
    "base_requested": "17843715",
    "base_mode": "exact",
    "head_start": "17843715c9b05578902e561d667b151fe0fb9abc",
    "head_end": "17843715c9b05578902e561d667b151fe0fb9abc",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c 'from pathlib import Path\nfrom types import SimpleNamespace as NS\nfrom unittest.mock import patch\nfrom joulewise import arm_readiness_evidence_t0 as t\nfor now, expected in [(500_000_000_000, False), (600_000_000_990, False), (600_000_000_991, True), (800_000_000_000, True), (500_000_000_000_000, True)]:\n    start = now - t._MIN_IDLE_NS - 990\n    v = dict(schema_version=t._COMMAND_SCHEMA, step_id=\"clock-reference\", argv=[\"/fixture/probe\"], cwd=\"/fixture\", exit_code=0, stdout=\"\", stderr=\"\", started_monotonic_ns=start, finished_monotonic_ns=start+190, boot_session_id=\"fixture-boot\")\n    ctx = NS(captures={}, custody_pack_root=Path(\"/fixture\"), boot_session_id=\"fixture-boot\", clock=NS(monotonic_ns=lambda: now))\n    with patch.object(t, \"_canonical_object\", return_value=(v, {}, b\"\")):\n        try:\n            t._capture(ctx, \"clock-reference\", kind=\"CLOCK_ATTESTATION\")\n            passed = True\n        except t.T0EvidenceAuthoringError as exc:\n            assert str(exc) == \"clock-reference command capture fields are invalid or stale\"\n            passed = False\n    assert passed is expected, (now, passed)\nprint(\"CAPTURE_FLOOR_BOUNDARY=PASS; small=REFUSE; threshold=600000000991; large=PASS\")\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CAPTURE_FLOOR_BOUNDARY=PASS; small=REFUSE; threshold=600000000991; large=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CAPTURE_FLOOR_BOUNDARY=PASS; small=REFUSE; threshold=600000000991; large=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "17843715c9b05578902e561d667b151fe0fb9abc",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Production capture validation was exercised in memory. No filesystem authoring regression, Linux replay, full suite, or hardware measurement was run. Replacement code is proposed, not implemented.",
      "needs": "Lead applies the chosen correction and runs the targeted regressions in a writable environment, followed by the lane's required verification."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "This repeats consult 87's broader host-calibrated fixture-assumption class. A RAW-anchor-less-than-ordinary-now requirement would be a new, incorrect cross-clock constraint.",
      "needs": "Lead decides cold-gate routing; recommendation is to submit this diagnosis before another fix/replay round."
    }
  ]
}
```

## Causal chain

**The failed condition is `started_monotonic_ns < 1`, caused by subtracting ten minutes from a host uptime shorter than ten minutes.** Changing the synthetic RAW anchor alone cannot cure it.

The relevant tail of the field-validation condition in [arm_readiness_evidence_t0.py:550](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/arm_readiness_evidence_t0.py:550) is:

```python
        or not isinstance(value.get("started_monotonic_ns"), int)
        or not isinstance(value.get("finished_monotonic_ns"), int)
        or value["started_monotonic_ns"] < 1
        or value["finished_monotonic_ns"] < value["started_monotonic_ns"]
        or value.get("boot_session_id") != context.boot_session_id
    ):
        raise _underivable(kind, f"{step_id} command capture fields are invalid or stale")
    now = context.clock.monotonic_ns()
    if (
        value["finished_monotonic_ns"] > now
        or now - value["finished_monotonic_ns"] > _MAX_T0_SEQUENCE_AGE_NS
    ):
        raise _underivable(kind, f"{step_id} command capture is not a live T-0 artifact")
```

The reported message comes from the **first** guard. Future/stale capture validation has a different message and occurs afterward.

The exact construction in [make_t0_fixture:566](/Users/edr/code/JouleWise-wt-ref-308-delta/tests/test_arm_readiness_evidence_t0.py:566) is:

```python
time_origin = now_monotonic_ns - t0._MIN_IDLE_NS - 1_000
```

The clock-reference capture receives:

```python
time_origin + 10,     # started_monotonic_ns
time_origin + 200,    # finished_monotonic_ns
```

Since `_MIN_IDLE_NS = 600_000_000_000`:

| Field | Exact derivation |
|---|---|
| Capture start | `now − 600_000_000_990` |
| Capture finish | `now − 600_000_000_800` |
| Capture age at validation | `600_000_000_800` |
| R0 RAW anchor, with supplied sampler | `sample.raw − 600_000_000_980` |
| R0 RAW batch start | `R0.raw + 10` |
| R0 RAW batch finish | `R0.raw + 26` |
| R1 RAW start/finish | Supplied sampler’s RAW value; both `1_000_000_000_000` here |
| R1 ordinary start/finish | `now_monotonic_ns`, through `_DerivationClock.monotonic_ns` |

`_clock_reference_value` supplies three legs starting at `R0.raw + 20`, `+22`, and `+24`, each finishing one nanosecond later. Its final cursor is `R0.raw + 26`.

[author_environment:832](/Users/edr/code/JouleWise-wt-ref-308-delta/tests/test_arm_readiness_evidence_t0.py:832) independently installs:

```python
monotonic_ns=lambda: now_monotonic_ns
```

and the supplied `sample_anchor`. It does not derive ordinary monotonic time from RAW.

Consequently:

| Ordinary `now` | Capture start | Result of actual `_capture` |
|---:|---:|---|
| `100_000_000_000` | `−500_000_000_990` | Reported field-validation error |
| `500_000_000_000` | `−100_000_000_990` | Same error |
| `600_000_000_990` | `0` | Same error |
| `600_000_000_991` | `1` | Pass |
| `800_000_000_000` | `199_999_999_010` | Pass |
| `500_000_000_000_000` | `499_399_999_999_010` | Pass |

These outcomes were reproduced in memory. The exact reported runner uptime was not independently obtained.

The fixed RAW sample gives `R0.raw = 399_999_999_020`, independently of every row above. There is **no comparison of that RAW value against ordinary `now`** in this path.

### Four-module clock census

“No uptime dependency” below concerns this clock-origin defect; it does not promise completion under arbitrary process starvation.

| Location | Clock relationship | Small-uptime host | Large-uptime host |
|---|---|---|---|
| Integration `setUp`, lines 296–318 | Freezes ordinary time at one **real host reading**; independently supplies fixed RAW samples. | Enables the defect when census fixture subtracts 600 s. | Masks it. |
| Integration census test, lines 389–430 | Passes that frozen host reading into fixture creation and all authoring environments. | Fails below `600_000_000_991` ns, before any forbidden census observation. | No origin failure. |
| Integration `install_passing_evidence`, lines 176–218; callers at 326, 563 | RAW fields come from the fixed anchor. Receipt expiry and ordinary R1 finish both derive from `authored_now`. ARM checks RAW offset consistency separately from ordinary validity. | No RAW-versus-host comparison; no 600 s ordinary subtraction. | Same. |
| Integration skew/drift test, lines 333–375 | Mutates only live skew and `REALTIME−RAW`; ordinary time remains frozen. | No uptime dependency. | Same; one-nanosecond boundaries remain meaningful. |
| T0 fixture, lines 566–635 | Ordinary captures derive from supplied `now`; RAW reference derives independently from supplied sampler, or from synthetic `now` in the default branch. | Vulnerable **when a caller supplies short host uptime**. Default `now=10¹²` is safe. | No origin failure. |
| T0 author environment, lines 832–843 | Supplied ordinary `now`; explicit sampler or `coherent_clock_anchor(raw_ns=now)`. | No independent host read or cross-clock comparison. Cannot repair an invalid capture history. | Same. |
| T0 subprocess bootstrap, lines 284–305 and 398–405 | When `clock_override` exists, child ordinary time and default RAW observation use the same supplied synthetic value. An explicit anchor override can remain independent. | No uptime dependency in the synthetic path. | Same. |
| T0 setup/age/boundary tests, lines 865–899, 1171–1187, 1703–1789, 1837–1985, 2054, 2184 | Fixed or explicitly advanced synthetic ordinary/RAW values; test ordering, span, skew, drift and duration. | No ambient uptime dependency; failures are specified counterfactuals. | Same. |
| T0 volatile-receipt tests, lines 2244–2323; explicit consumption at 2822 | Authoring and consumers receive explicit synthetic ordinary times. Live-anchor observations are patched. | No ambient uptime dependency. | Same. |
| T0 clock-family test, lines 2344–2378 | Explicit ordinary `36×10¹²` ns and RAW offsets of ±`7.2×10¹²`; verifies separation. | No actual host clock input. | Same. |
| T0 acid helper, lines 2924–2940; real branch invoked at 3088 | Synthetic branch uses `10¹²`; **real branch reads host ordinary time and real RAW anchors**. | Real branch has the same missing-history defect below 600 s. Darwin-only caller; not this Linux failure. | No origin defect, but real skew/drift, elapsed-time and hardware prerequisites remain. |
| Lifecycle setup, lines 582–585; shared-evidence callers at 863 and 990 | Fixed RAW observations; shared helper authors ordinary expiry from live time. Consumption/deadlines remain live. | No RAW-versus-ordinary comparison or ten-minute subtraction here. | No origin failure; elapsed deadlines and race scheduling remain real. |
| Lifecycle expiry tests, lines 2769–2908; inventory tests, lines 3135–3183 | Explicit deadline `1000`, mocked consumers, and inventory validation at explicit `1000`. | No host-clock dependency. | Same. |
| Launch mint, lines 563–577, 611–619, 839–842 | Ordinary author time is `max(host_now, 0) + 600_000_001_000`; fixed RAW observation copied to subprocess; child capability clock stays live. | **Already protected:** first capture starts at `max(host_now, 0)+10`. | Protected; no upper-uptime limitation from integer arithmetic. |
| Launch clock-separation and skew/drift tests, lines 443–530 and 885–896 | Specified RAW/ordinary offsets and boundary samples. Separation test deliberately permits RAW ahead of ordinary time. | Deterministic; separation test stops after authoring. | Same. |
| Launch lifecycle fixture author, lines 2105–2115 | Capture timestamps derive from current ordinary time with approximately 100 ns subtraction; no RAW anchor. | Safe for minutes/seconds of uptime; artificial ordinary time below 100 ns could underflow its first start. | No origin failure. |

## Remediation

**Minimal cure: select the already-frozen integration clock from the synthetic fixture, instead of freezing the host’s uptime.** Preserve ordinary-clock behavior in the lifecycle and launch tests.

No algorithmic change to `coherent_clock_anchor` is necessary. Its exact retained implementation can be:

```python
def coherent_clock_anchor(
    clock_gettime_ns=None,
    *,
    raw_ns: int = 1_000_000_000_000,
    skew_ns: int = 1_000,
    drift_ns: int = 0,
) -> ClockAnchor:
    """Supply specified observations; callers own the ordinary timeline.

    Accept the production seam's optional positional clock reader.
    REALTIME minus RAW remains REALTIME_OFFSET_NS plus drift_ns.
    """
    return ClockAnchor(
        realtime_ns=REALTIME_OFFSET_NS + raw_ns + drift_ns,
        monotonic_raw_ns=raw_ns,
        read_skew_ns=skew_ns,
    )
```

In `ArmReadinessIntegrationTests.setUp`, replace:

```python
fixed_monotonic_ns = time.monotonic_ns()
```

with:

```python
# This class already freezes ordinary time. Select a synthetic instant
# with enough positive history for the complete ten-minute T-0 sequence.
fixed_monotonic_ns = coherent_clock_anchor().monotonic_raw_ns
```

All existing sampler call sites remain valid:

```python
side_effect=coherent_clock_anchor

sample_anchor=coherent_clock_anchor

coherent_clock_anchor(skew_ns=skew, drift_ns=drift)

coherent_clock_anchor(raw_ns=now_monotonic_ns)
```

This chooses equal origins **within this synthetic integration scenario**. It does not establish a general requirement that RAW equal or precede ordinary monotonic time.

Do not change only the census test’s local `now`: its subsequent `generate_arm_receipt` must use the same ordinary timeline. Updating the existing setup freeze covers authoring, evidence expiry, ARM generation and verification together.

### Regression proposals

Add this separate class to `tests/test_arm_readiness_integration.py`. It exercises the complete existing census test, including successful authoring, ARM verification and all forbidden/error census cases:

```python
class ArmReadinessIntegrationClockPortabilityTests(unittest.TestCase):
    def test_census_transaction_ignores_host_uptime(self) -> None:
        method = (
            "test_specified_census_observations_refuse_before_publication"
        )
        for host_now in (
            100_000_000_000,
            500_000_000_000,
            800_000_000_000,
            500_000_000_000_000,
        ):
            with self.subTest(host_now=host_now):
                result = unittest.TestResult()
                case = ArmReadinessIntegrationTests(method)
                with mock.patch.object(
                    time, "monotonic_ns", return_value=host_now
                ):
                    case.run(result)
                self.assertEqual(result.testsRun, 1)
                self.assertEqual(result.skipped, [])
                self.assertTrue(
                    result.wasSuccessful(),
                    (result.errors, result.failures),
                )
```

Before the fix, the first two cases fail at the reported capture guard. After the proposed setup change, every case uses a coherent synthetic transaction instant.

**A literal authoring `now_monotonic_ns=500_000_000_000` cannot pass the existing positive-history fixture unchanged.** It describes only 500 seconds of ordinary time while the fixture requires a preceding 600-second sequence. Simulate the small **host** reading and select a valid synthetic authoring instant, as above; do not weaken production capture validation.

Add these methods to `ArmReadinessEvidenceT0Tests` to retain deterministic refusal coverage:

```python
def test_insufficient_positive_capture_history_refuses(self) -> None:
    self._assert_clock_refusal(
        now_monotonic_ns=500_000_000_000,
        detail="clock-reference command capture fields are invalid or stale",
    )


def test_r0_raw_anchor_ahead_of_author_raw_refuses(self) -> None:
    now = SYNTHETIC_MONOTONIC_NS

    def mutate(inputs: Path) -> None:
        self._replace_r0(
            inputs,
            anchor_raw=now + 1,
            anchor_realtime=SYNTHETIC_REALTIME_OFFSET_NS + now + 1,
        )

    self._assert_clock_refusal(
        now_monotonic_ns=now,
        mutate=mutate,
        detail="T-0 RAW anchor span is below 600000000000 ns",
    )


def test_capture_finish_ahead_of_ordinary_now_refuses(self) -> None:
    now = SYNTHETIC_MONOTONIC_NS

    def mutate(inputs: Path) -> None:
        path = inputs / "clock-reference.json"
        capture = json.loads(path.read_text(encoding="utf-8"))
        capture["finished_monotonic_ns"] = now + 1
        _write_json(path, capture)

    self._assert_clock_refusal(
        now_monotonic_ns=now,
        mutate=mutate,
        detail="clock-reference command capture is not a live T-0 artifact",
    )
```

The two “ahead” refusals correctly compare timestamps **within their respective clock families**. A RAW anchor ahead of ordinary `now` alone should not refuse.

The existing `(1_000_000, 5_000_000)` passing boundary and the `1_000_001` skew / `5_000_001` drift refusal cases remain unchanged. `REALTIME−RAW = REALTIME_OFFSET_NS + drift_ns` remains exact.

### Same signature and cold gate

**Same signature: present at the host-calibrated fixture-assumption level.** [Consult 87](/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/87-consult-fixture-regression-portability-astra-report.md) identified assertions that depended on the Mac’s sample count/window geometry. This lane assumes the host already supplies enough positive ordinary-monotonic history.

The immediate mechanisms differ. This failure is deterministic below an uptime threshold; it is not scheduling jitter, census contamination or a timeout.

My recommendation is to route this diagnosis to the cold gate before another fix/replay round. The established launch fixture already documents and handles freshly booted runners, while the new census caller omitted that protection. The lead decides whether that recurrence invokes the standing escalation rule; this report neither waives nor installs a gate.

## Disproved alternatives

- **Fixed RAW exceeds ordinary `now`:** no such comparison causes the exception. RAW and ordinary capture timestamps are constructed separately.
- **Capture exceeded the staleness window:** capture age is always `600_000_000_800` ns here, below the 3600-second maximum.
- **Seven-year REALTIME offset:** the relevant checks subtract RAW from REALTIME; the fixed offset cancels.
- **Forbidden census observation or agent load:** the initial passing-probe authoring call fails before those counterfactuals run.
- **Linux-specific parser/type behavior:** integer arithmetic and the same production guard reproduce the reported message locally.

## Residual risk

The proposed end-to-end regressions remain unexecuted in this read-only environment. The real-clock Darwin acid path also retains the short-uptime history assumption; it needs separate lead treatment if included in this correction.

Next exact step: lead adjudicates the proposal, applies the integration setup change and regressions, then runs the portability regression and existing clock-boundary tests. The worktree remains clean; no files changed.