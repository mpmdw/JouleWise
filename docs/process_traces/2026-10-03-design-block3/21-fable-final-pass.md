FINAL PASS: PASS

No path found to a wrong admission, verdict or selection; one MAJOR is recorded because the 300 s sizing argument is not sound as written, though it fails closed. The six listed test modules run 179 OK (1 skipped).

**1. MAJOR (non-blocking, fail-closed): the 300 s sizing argument and its test do not hold for real streams.** `tests/test_controller_retry_backoff.py:245-263`, `scripts/gen_g2_phase_d.py:45-52`
- **Stream length is understated.** The test models 75+300+75+60 = 510 s and the generator comment says "about 485 s". The 12 completed block-2 members on record (window 1748Z `runs/*/metadata.json`) show each idle attempt taking 101–104 s (750 frames at about 131 ms). The retried member `g2a-small-p0512-r02` ran 221.8 s with no wait, so about 522 s with a 300 s wait, and more for the large model at p4096.
- **The anchor half-width is ignored.** The v3 method caps the whole effective bound (half-width + span + resolution) at 5 ms (`joulewise/uncertainty_evidence.py:1374-1380`), not the span alone. The test's synthetic 1 s records give a half-width of 0.505 ms (I ran `anchor()` at 485–660 s). The recorded half-widths are 0.52–2.31 ms, and 9 of 12 exceed 1.03 ms.
- **Consequence at the cited drift.** At 522 s and 7.60 ppm the span is 3.97 ms, leaving 1.03 ms for the half-width, so most retried members would be voided with `effective_clock_anchor_bound_exceeded`.
- **Why it does not block.** All 12 completed block-2 members drifted 3.17–3.19 ppm. At that rate 522 s gives 1.66 ms, plus the worst recorded half-width of 2.3 ms, about 4.0 ms against the 5 ms cap. Tolerance is roughly 5.2 ppm at 522 s. A voided member is refused, never wrongly admitted, and 600 s would be worse, so choosing 300 over 600 is still right.
- **Fix.** Correct the comment and test to the real stream length (about 525–580 s) and a realistic half-width, and state the true tolerance rather than "bounded at 7.24–7.60 ppm".

**2. MINOR: the harvest lost its independent anchor on which policy is acceptable.** `scripts/generate_g2a_probe_inputs.py:1343-1360`, `scripts/harvest_g2a_window.py:138,189`
- Resolution itself is sound: the hash is verified, the path is confined to `configs/campaign_policies` in the measurement checkout, and `..`, absolute and symlink escapes are refused. Brackets are judged against the policy the inventory bound.
- Before, anything but production failed `campaign_policy_mismatch` (`:1191`). Now any file in that directory passes, including `quiet_mac_exploratory.json` (`require_bracket: false`, `on_fail: flag`); bind and check only schema-validate (`:877`, `:1194`).
- I found no check in the harvest or summary that each bundle's own `campaign_policy.sha256` equals the inventory's (grep only).
- This is reachable only if the chain's `POLICY` export differs, and the generator pins it (tested for exactly one export). Suggest an allowlist of the two hashes, or requiring `profile == production` with `require_bracket` true.
- Old windows still re-harvest: the 1748Z inventory stores the relative production path.

**3. NIT: the retry budget uses 75 s idle.** `scripts/gen_g2_phase_d.py:85-88` A recorded attempt is about 102 s plus guards, so a retry costs about 407 s against 405 s budgeted. This is negligible against the member allowances.

**4. NIT: a test label misleads.** `tests/test_controller_retry_backoff.py:53,161` The strict-bundle subtest labelled `600` loads the 300 s policy file, because `strict_fixture` overrides the `backoff` argument.

**5. NIT: `environment_admission.retry_backoff` is recorded but never validated.** `joulewise/controller.py:1115` No validator checks it against the policy or the gap between attempts. It is audit-only.

**Questions with no defect found**
- **Q1, backoff 0:** the controller change is one block guarded by `retry_backoff_s > 0` (`joulewise/controller.py:1111`).
  - The policy binding hash is over raw file bytes, and the production file is untouched: `b0d7b228…` matches the binding in the recorded block-2 bundles.
  - `CampaignPolicy.to_dict()` drops the key at 0 and has no production callers; nothing else serialises the policy (grep).
- **Q2, backoff > 0:** criteria, the single retry, the abort reason, promotion of attempt 2 and the guard phases are unchanged.
  - Attempt 2 cannot consume frames captured during the wait: `_capture_idle_slice` catches the cursor up and skips one straddling frame (`joulewise/adapters/powermetrics.py:1244-1254`).
  - The sampler has no `-n` count limit, `SystemClock.sleep` is a plain `time.sleep`, and `scripts/run_campaign.py` contains no timeout at all.
  - No validator exact-keys `environment_admission`. The 600 s admission-gap limit measures final attempt end to window start, so the wait does not touch it. The thermal scan starts at the final attempt.
- **Q3, other validators:** nothing besides the clock anchor in finding 1. The reducer was not separately traced for stream-length limits.
