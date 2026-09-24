# D-184 council packet: live-epoch instrument acceptance

## Question and vocabulary

What is the fastest scientifically sound route to an issued calibration acceptance for macOS build **25G83**? This is a fact packet, not a recommendation. **D-079** is the instrument calibration decision; **D-102** governs identity-epoch freshness; **A243** is queue lane `INSTRUMENT-CADENCE-ATTRIBUTION-25G83-01`; **A179** is `ACCEPTANCE-EPOCH-25G83-01`. An *identity epoch* fixes OS build, hardware model, power policy, requested sampling interval, estimator revision, and pulse protocol. An *acceptance* is the issued artifact that supplies future calibration screens. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:15-30; TASK_QUEUE.md:828,872]

**r6/r7** name generations six/seven of the 17-member D-079 acceptance; **G2-a** is the registered first prefill probe window after live acceptance; **`qpe01`** is a separate quiet-predicate idle-power pilot; **KM003C** is the POWER-Z USB-C meter. **D-054** governs false-effect floors; **D-078** is the attribution-bound doctrine; **D-125/D-126** govern successor screen and corpus-size constraints. [configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:3-26; docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md:74-88; docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:20-22; docs/decision_log.md:4789-4814; configs/calibration/preregistration_d079_epoch_25g83_rev1.md:173-177,232-248]

## Fixed state

- Issued **r7** (`d079_calibration_acceptance_v2_n17_r7`) remains for 25F84, despite its newer estimator-code pin; its six-field identity still specifies 25F84 and 100 ms. [configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:3-26,495-505]
- The 25G83 pre-registration requests 100 ms and pins `/usr/bin/powermetrics` SHA-256 `b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5`. It sets three 12-slot windows on distinct days with retained n at least 19 for the fallback successor route. [configs/calibration/preregistration_d079_epoch_25g83_rev1.md:132-145,173-177]
- The two 19 September epoch-equivalence nights ended INCONCLUSIVE (m=4) and FAIL (m=7); Ed chose option (c): neither night counts and the instrument is resolved before more derivation nights. [docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md:71-85; docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:5-14]
- A prior critical-path scout found no currently registered science night armable on the stale acceptance. The later council's G2-a-first order explicitly left READY status unverified. [docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md:68-90; docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:50-54]

## What the six files contain

`01` separates measured native intervals, estimator changes, and unresolved causal attribution. `02` records the acceptance's quantities, refusals, and energy-bound implications. `03` inventories retained 25G83 captures and corpus eligibility. `04` gives the available paths with costs and dependencies but no selection. `05` lists unresolved facts and ten source spot-checks. All costs are bounds or planning estimates, never observed runtimes unless so marked. [docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md:30-62]
