```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a bounded stream-minus-cache response test; non-detection cannot establish that the memory controller is excluded from the GPU rail.",
  "workspace": {
    "base_requested": "6731d524907a9c9f77eb51a5380410a705ffc657",
    "base_mode": "exact",
    "head_start": "6731d524907a9c9f77eb51a5380410a705ffc657",
    "head_end": "6731d524907a9c9f77eb51a5380410a705ffc657",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "Register diagnostic quantities, control, bounds and caveat wording",
        "action": "start_now"
      },
      {
        "row": "Run the companion experiment",
        "action": "wait_for",
        "wait_for": "Pass-1 collection complete and the existing lead-controlled quiet-Mac opportunity"
      },
      {
        "row": "Infer physical memory-controller inclusion or exclusion from non-detection",
        "action": "do_not_start"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git diff --exit-code && git diff --cached --exit-code && git ls-files --others --exclude-standard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "6731d524907a9c9f77eb51a5380410a705ffc657"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "6731d524907a9c9f77eb51a5380410a705ffc657"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B -c 'from decimal import Decimal as D; w=D((2**30)*150000); assert w==D(161061273600000); assert D(3000)/w*D(10)**12>D(18)/w*D(10)**12; assert D(\"1e6\")*D(\"2.2e-16\")*D(60000)<D(\"0.00013\"); print(\"EXAMPLE_ARITHMETIC_OK\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["EXAMPLE_ARITHMETIC_OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^EXAMPLE_ARITHMETIC_OK$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Rail activity and a null result do not identify the physical memory-controller boundary. A matched contrast supports an operational memory-traffic response statement.",
      "needs": "Use the qualified outcome classes and caveat wording proposed below."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No documented SLC capacity, stream timing, stream control result or stream-specific operative placement bound was available in the inspected sources. These remain measure-first operands.",
      "needs": "Record them with the existing non-claim companion test; unavailable operands produce an undetermined diagnostic."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Reading rule and receipt supplement | start_now | Nothing | Registration prose and companion probe only; lead implements |
| Companion measurement | wait_for | Pass 1 complete; agents absent | Existing quiet-Mac lane, own non-claim checkout |
| Outcome beside claim lines | wait_for | Companion result | Disclosure only; no estimator, exclusion or collected-number change |

**Recommendation:** register a test of **memory-traffic-associated boundary response**. The experiment cannot establish the physical location of the memory controller. In particular, a result consistent with zero cannot prove that the GPU rail excludes it.

### 1. Reported quantities and bounds

Let the receipt give the exact half-open span \(S=[s,e)\), duration \(T\), payload \(B\), repeats \(N\), and logical bytes \(W=BN\). Preserve integer nanoseconds and integer bytes throughout.

Report quantities for GPU alone, total rails \(R=\mathrm{CPU+GPU+ANE}\), DC input \(D\), and rest \(D-R\):

\[
Q_X=F_X(S)-T\widehat P_{0,X},
\qquad
q_X=Q_X/W.
\]

Here \(F_X\) is energy on the recorded boundary. Rails use native interval-support integration. DC uses the registered meter integration plus signed battery energy; missing battery readings must not silently become zero. Rest is formed by subtraction before normalization. These follow [registration §7](/Users/edr/code/jw-wt/kb-sol/docs/registrations/bytes_pack_v1.md:203) and [the meter integrator](/Users/edr/code/jw-wt/kb-sol/joulewise/external/km003c_parse.py:406).

**Idle source and span.** Add two explicit RAW-clock spans to the test harvest:

- \(I_-\): the companion capture’s quiet idle after allocation, initialization and synchronization, before the measured stream;
- \(I_+\): quiet idle after the workload and recovery, with the payload retained.

Both come from the **same continuous rails and meter capture** as the probe. Record their exact endpoints, lengths \(L_-,L_+\), trace identities, and recovery placement. Do not borrow an LLM run’s idle or a pass-1 average.

Use

\[
\widehat P_{0,X}
=\tfrac12\left[F_X(I_-)/L_-+F_X(I_+)/L_+\right].
\]

The current receipt contains neither idle span. Therefore the present receipt alone is insufficient; the smallest harvest supplement must identify them.

For each boundary, use an explicit additive budget:

\[
U(Q_X)=a_X(S)+
 \frac{T}{2}\left[\frac{a_X(I_-)}{L_-}+
                    \frac{a_X(I_+)}{L_+}\right]
 +T d_X.
\]

Then \(U(q_X)=U(Q_X)/W\). No term shrinks by \(1/\sqrt N\): \(N\) counts reductions inside one measured span.

| Term | Source and computation |
|---|---|
| Rails placement | Recompute the anchor-shift envelope on the **probe and idle spans**, under the companion capture’s operative timing bound. Use the GPU curve separately for GPU. The existing continuous envelope evaluates interior breakpoints as well as endpoints: [implementation](/Users/edr/code/jw-wt/kb-sol/joulewise/reduce.py:2064). |
| Approximately 1 J attribution scale | For scheduling and this conservative diagnostic, use \(a_R=\max(1\text{ J},\text{computed placement envelope})\), likewise for GPU. The 1 J is an **engineering reserve**, not a newly measured universal bound; [tolerances.py](/Users/edr/code/jw-wt/kb-sol/joulewise/tolerances.py:1) and §12 supply the scale. Do not add it again to an envelope that already exceeds it. |
| Rails interpolation | Zero for the registered native interval-support representation, as §7 requires. Do not add a separate 100 ms edge rectangle to that representation. |
| Meter timing and sampling | Start with §7’s \(u=(P_s+P_e)(r_{\max}+\Delta)\), using its specified edge maxima. \(\Delta=20\) ms at recorded 50 SPS; BY-H2’s \(r_{\max}=17.28\) ms. Use the test’s actual values. |
| Constant meter-label offset | §9 separately discloses its unresolved one-sided offset. For a conservative companion budget, add an offset envelope over \(0\leq\delta\leq\Delta+\mathrm{RTT}_{\max}\); a simple upper bound is \((P_s+P_e)(\Delta+\mathrm{RTT}_{\max})\). This intentionally exceeds §7’s existing budget where terms overlap. |
| Meter digital resolution | The decoder stores integer µV and µA. Conservatively allow one encoded unit each: \(\delta P\leq |I|10^{-6}+|V|10^{-6}+10^{-12}\) W, integrated over workload and scaled idle spans. This is digital resolution, **not meter accuracy**: [decoder](/Users/edr/code/jw-wt/kb-sol/joulewise/external/km003c_parse.py:160). |
| Battery | Carry §7’s \(v_s+v_e\), including the corresponding idle contribution. Its delay is \(2T_{\rm SMC}+\Delta t_p\); H recorded 2.302 s. A zero battery term is justified by recorded readings, including edge context. |
| Idle stability \(d_X\) | At minimum, half the pre/post idle-power difference, enlarged to cover observed idle-block variation. This is an observed stability allowance, conditional on idle during the experiment staying within that envelope. Arbitrary unobserved background activity has no finite bound derivable from endpoint idles. |
| Rest | \(U(Q_{\rm rest})=U(Q_D)+U(Q_R)\), conservatively. Preserve signed estimates and intervals. |

The 125 µs anchor-read resolution in `tolerances.py` is **not** the operative placement bound. Its 1 µs comparison tolerance and 1 mJ energy comparison tolerance are also not physical uncertainties.

Report the budget components. Missing coverage, unbounded placement, missing battery context or an unsupported stability assumption makes the affected diagnostic **undetermined**, with its reason; it changes no claim eligibility. The budget covers attribution, digital resolution and observed stability, not an unrecorded absolute sensor-gain calibration.

Print energies to §14’s 1 mJ and durations to 1 ms. Print \(q\) in **pJ per logical byte**, its half-width to two significant figures, and estimate/endpoints to the same decimal place; retain full precision in JSON.

### 2. Outcome classes and caveat rule

The deciding quantity is the matched control contrast from item 3:

\[
c_X=q_{X,\mathrm{stream}}-q_{X,\mathrm{cache}},
\quad
J_X=[c_X-U(c_X),c_X+U(c_X)].
\]

Sum arm bounds conservatively. Across repeated arms, average their systematic bounds without shrinkage and add an empirical repeatability allowance: the largest within-arm repeated-value difference, in the same units. Shared baseline terms may cancel algebraically when coefficients match exactly; otherwise retain them.

| Class | Rule | Supported interpretation |
|---|---|---|
| **Response detected** | Matched control is interpretable and \(\inf J_X>0\) | Extra boundary energy is associated with the external-memory workload under this control. For GPU, this supports “GPU rail carries a detectable memory-traffic-associated response.” |
| **No response resolved** | Control is interpretable and \(0\in J_X\) | No extra response was resolved. Print the upper limit \(\max(0,\sup J_X)\). A positive DC contrast makes this especially informative for GPU/rails. |
| **Undetermined** | Missing operands, unestablished cache contrast, stack-transfer problem, or a wholly negative contrast | Print the signed result and reason. A negative contrast indicates that this simple positive-response interpretation failed. |

**No outcome establishes “the GPU rail does not include the memory controller.”** That requires a defensible lower bound on the response expected if it did. Neither the registration nor probe supplies one. An architectural inclusion claim is also stronger than this experiment supports: caches, interconnect, stalls and GPU operating state can contribute.

Use **zero**, derived from the physical positive-response question, as the decision threshold. Do not substitute “1% of DC energy,” a rail/DC agreement percentage, or an arbitrary SNR.

Print these exact templates beside affected claim lines:

- **No response resolved:**  
  `Known-bytes check: no {boundary} memory-traffic response was resolved (upper limit {upper} pJ per logical byte); memory-controller inclusion is undetermined.`
- **Undetermined:**  
  `Known-bytes check: {boundary} memory-traffic attribution is undetermined ({reason}).`

For rails claims, include the GPU-specific outcome in that line. DC and rest get their own contrast outcome; a GPU non-detection alone does not imply DC or rest failed.

A detected result can carry the shorter informational line:

`Known-bytes check: {boundary} memory-traffic-associated response detected; this does not identify a physical memory-controller rail.`

If independent arithmetic is compared, preserve §12’s distinction between **agreement** and **physical detection**. One suitable energy comparison bar is

\[
b=\min(0.01U_{\min},0.00013\text{ J}),
\]

provided it exceeds \(10^6\epsilon E_{\rm scale}\). The cap is 1% of §12/§14’s smallest 0.013 J half-width. For the example below, \(10^6(2.2\times10^{-16})(60000)=0.0000132\) J, below 0.00013 J. Scale the bar by the exact byte denominator for normalized quantities. Classify using full-precision intervals, never this arithmetic agreement bar.

### 3. Control

**A contrast arm is necessary for a memory-traffic attribution statement.** The stock reduction-versus-idle result includes reduction arithmetic, dispatch, workspace and GPU activation. That remains useful descriptive output but cannot answer the attribution question.

Use the same GPU kernel structure, logical load count, additions, dispatch count, reduction/output structure and synchronization in both arms:

- **Stream:** addresses traverse a payload above the relevant cache capacity.
- **Cache:** the same work repeatedly addresses a warmed cache-resident tile.

An address-period parameter in one kernel is preferable to comparing `mx.sum(B)` with many `mx.sum(C)` calls: the latter changes dispatch counts and reduction topology. Compile and warm both before their recorded spans, and record the actual selected GPU backend. The stock probe currently constructs its first reduction inside the measured span.

Run **stream/cache/cache/stream**, using the already familiar ABBA ordering to balance approximately linear drift. This is one implementation of the companion experiment, not another campaign or admission gate. Cache/cache and stream/stream differences supply the empirical stability allowance above.

Even this contrast measures the workload’s associated energy, including changed cache/interconnect/stall behavior. It does not isolate controller circuitry. Keep \(BN\) labelled **logical payload reads**: the probe’s all-ones input and receipt provide no hardware DRAM byte count, as [the probe itself states](/Users/edr/code/jw-wt/kb-sol/scripts/bytes_stream_test.py:1).

### 4. Choosing B and N

**Cache capacity: measure first.** I found no documented SLC capacity in the inspected BYTES/design/registration material. Do not insert a remembered M3 Max cache size.

Obtain a documented upper bound for caches accessible to the selected GPU, including SLC, or retain a timing-versus-working-set characterization supporting the chosen cache and streaming regimes. Choose the stream payload above that bound, and the warmed control tile within a demonstrated resident regime. Capacity alone does not turn logical bytes into a physical DRAM counter. If the contrast is unestablished, report undetermined.

**Timing: measure first.** Measure synchronized iteration time after compilation/warm-up, allocation/workspace demand and recovery time. Then choose integer repeats from

\[
N=\left\lfloor T_{\rm allocated}/t_{\rm iteration}\right\rfloor.
\]

Use separate measured arm times where they differ. Keep work counts matched; use exact actual spans in the energy arithmetic. The [README](/Users/edr/code/jw-wt/kb-sol/configs/campaigns/bytes_mac_check/README.md:28) explicitly provides no guessed bandwidth default.

A possible hour allocation is two 300 s idle spans, four approximately 600 s arms, and 600 s for initialization, characterization and recovery:

\[
2(300)+4(600)+600=3600\text{ s}.
\]

These are scheduling choices, not registered thresholds.

A 1 J workload placement contribution over 600 s is 1.67 mW; over 3600 s it is 0.278 mW. However, the idle contribution is proportional to \(T/L\), and drift contributes \(Td_X\). Increasing \(N\) cannot remove either relative error indefinitely:

\[
\frac{a+Td_X}{T\Delta P}
=\frac{a}{T\Delta P}+\frac{d_X}{\Delta P}.
\]

Report the achieved bound-to-effect ratio. If baseline or control instability dominates, a longer loop supplies little benefit; the result can remain unresolved within the planned hour.

### 5. Smallest C4 stack repair

Add one **observed stack object to the companion harvest**, keyed to the receipt and capture digests. Collect it outside the measured spans using the same interpreter that executes the probe. No LLM load is needed.

Retain the eleven governed names from [the C4 builder](/Users/edr/code/jw-wt/kb-sol/joulewise/identity_pins.py:64):

| Field | Source for this probe |
|---|---|
| `hardware_unit` | Actual capture device metadata, `platform.machine()`, configured target; supplement with observed `hw.model` |
| `os_version` | `platform.platform()`; also record `sw_vers -buildVersion` |
| `runtime_version` | Measurement interpreter and observed MLX distribution version |
| `kernel_library` | Actual observed library identity; explicitly `unavailable` if unavailable |
| `model_artifact_sha256` | Explicitly inapplicable: no model; record probe/kernel source digest separately |
| `quantization` | Probe dtype `uint8`; model quantization inapplicable |
| `tokenizer_identity` | Explicitly inapplicable |
| `sampler_output_policy` | No token sampler; record reduction operation, payload initialization and output consumption |
| `batching_concurrency_policy` | Actual sequential execution/dispatch policy |
| `measurement_boundary_label` | Actual rail manifest and boundary labels; meter identity/rate alongside |
| `telemetry_backend` | Actual capture adapters |

Also retain Python and all seven packages returned by [`runtime_versions(sys.executable)`](/Users/edr/code/jw-wt/kb-sol/joulewise/flags/collect.py:878): `mlx`, `mlx-lm`, `mlx-metal`, `transformers`, `tokenizers`, `safetensors`, `numpy`, plus its canonical digest.

The recorded comparison target is Python 3.13.1, MLX 0.31.2, mlx-lm 0.31.3, mlx-metal 0.31.2 and OS build 25G83: [RUNTIME-OBSERVE.txt](/Users/edr/code/jw-wt/kb-sol/docs/process_traces/2026-10-23-magistrate-786c0858/RUNTIME-OBSERVE.txt:1).

Compare **observed** common machine/runtime/telemetry fields with pass-1 stack records. Do not copy expected pins into observed fields or demand equality of intentionally different model/tokenizer policies. Print changed field names. A stack mismatch qualifies transfer to pass 1; it does not exclude collected data.

### 6. Worked example

**Illustration only; these are not measured stream results.** Repository anchors are:

- BY-H2 reference rails: 37.121008004357314 J over 1.3108093057142856 s, or approximately 28.319 W: [FIX416A report](/Users/edr/code/jw-wt/kb-sol/docs/process_traces/2026-10-24-magistrate-7209d1b0/FIX416A-REPORT.md:34).
- BY-H2 meter residual 17.28 ms; recorded meter interval 20 ms: registration §7.
- A documented non-claim meter example has idle 69.258 W and zero battery contribution: [meter parser example](/Users/edr/code/jw-wt/kb-sol/joulewise/external/km003c_parse.py:44).
- The approximately 1 J attribution and 100 W workload scales come from tolerances.py and registration §12.

Assume future test receipts establish:

- \(B=2^{30}\) bytes, verified above cache; \(N=150000\), \(T=600\) s per arm.
- \(W=161061273600000\) logical bytes; throughput 268.435456 GB/s.
- Equal 300 s idle spans; idle GPU/rails/DC means 1/5/69.258 W.
- Stream GPU/rails/DC means 25/28.319152/100 W.
- Cache GPU/rails/DC means 20/23.319152/90 W.
- A **hypothetical measured** operative placement bound of 10 ms; computed rail envelopes below the 1 J reserve.
- Observed idle stability allowance \(d_X=0.01\) W; zero battery term and edge term; repeated arms agree.
- Eligible meter RTT at most 3 ms and approximately 28 V bus.

The placement bound, stream powers, cache powers and stability allowance are invented example inputs; actual operands are **measure first**.

Rails/GPU uncertainty per arm:

\[
U=1+(600/300)1+600(0.01)=9\text{ J}.
\]

For DC, the conservative timing span is

\[
0.01728+0.020+(0.020+0.003)=0.06028\text{ s}.
\]

For the stream arm:

\[
U_D=
2(100)(0.06028)
+2[2(69.258)(0.06028)]
+0.037227+6
=34.792716\text{ J}.
\]

The 0.037227 J is the workload-plus-idle digital-resolution term. The cache arm similarly gives 33.586902 J.

| Quantity | Stream above idle, J | Cache above idle, J | Contrast, pJ/logical byte |
|---|---:|---:|---:|
| GPU | 14400.000 ± 9.000 | 11400.000 ± 9.000 | 18.63 ± 0.11 |
| Rails | 13991.491 ± 9.000 | 10991.491 ± 9.000 | 18.63 ± 0.11 |
| DC input | 18445.200 ± 34.793 | 12445.200 ± 33.587 | 37.25 ± 0.42 |
| Rest | 4453.709 ± 43.793 | 1453.709 ± 42.587 | 18.63 ± 0.54 |

Full-precision GPU contrast:

\[
c_G=18.62645149,\quad
U(c_G)=0.11175871,\quad
J_G=[18.51469278,18.73821020]
\]

in pJ/logical byte. Its lower endpoint is positive, as are DC’s and rest’s. Outcome: **response detected**, conditional on the matched control and stack transfer. GPU contrast uncertainty is 0.6% of the effect; DC’s is approximately 1.14%. These are achieved ratios, not acceptance thresholds.

### 7. Decisions I made

- Use an operational memory-traffic response statement; anatomical controller inclusion/exclusion is unidentifiable here.
- Require a work-matched cache contrast for attribution; retain the original above-idle quantities as descriptive output.
- Use bracketing idle from the companion capture and propagate baseline uncertainty explicitly.
- Preserve systematic bounds across repetitions; use the approximately 1 J scale as a disclosed conservative reserve.
- Include the separately disclosed meter-label offset conservatively in this companion budget.
- Use zero for response detection; non-detection prints an upper limit.
- Record C4 fields in the harvest, with honest inapplicable/unavailable entries and comparisons of common stack fields.
- Treat the hour allocation and example as proposals, never measured facts.

**NEEDS_RULING: none.** No proposed choice changes claim data membership, estimator arithmetic or an existing printed claim number. No repository files changed; no measurements, blinded data or `/Users/edr/night-*` paths were opened. Verification was source inspection and example arithmetic; no suite was needed for this read-only report.

## Critical path

The reading rule and receipt supplement precede the companion test. The companion test follows pass-1 collection and precedes stage-1 unblinding under existing §19/P0 ruling 9. Its result supplies the disclosure beside claim lines. No additional process gate is proposed.