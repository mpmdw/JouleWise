# 08 — Known conditions, gauge disclosure, yield

Primary sources: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`); `docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md` (sha256 `ce5e38ae505f078b4bd6b6530bdcdfa07f1cf9d8cf39ef95f68d917852579e37`); `docs/process_traces/2026-09-27-activation-3ba66eeb/00-activation-record.md` (sha256 `8efdc046143f93f02f44b4b0e20b9ad2fdb440fade72f74299048fabd686d394`).

### preregistration_d079_epoch_25g83_rev1.md lines 262–276

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Verbatim:

```text
## Known conditions (recorded, not rules)

**Display state at t0 is not constrained by the night gate.** The gate
(`joulewise/night_gate.py`, condition C3) requires the screensaver's
`idleTime` preference to read exactly `0` — meaning the screensaver never
engages, refusal reason `night_refused_hid_idle` — and for the display it only
requires that `pmset -g` yield a parseable `displaysleep` setting, recording
that value as evidence without demanding any particular one; it never probes
whether a panel is awake, dimmed, or asleep when the window opens, and the
derivation chain deliberately omits the writer flag
`--sleep-display-before-capture` that the G2-a chain passes, because no
operator is present to schedule a display action. These captures may therefore
differ systematically in display state from the G2-a corpus the resulting
acceptance will judge. That is recorded here as a known condition of this
corpus, not a rule: it edits no membership, moves no threshold, and licenses
```

### 00-activation-record.md lines 50–50

Primary source: `docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md` (sha256 `ce5e38ae505f078b4bd6b6530bdcdfa07f1cf9d8cf39ef95f68d917852579e37`). Verbatim:

```text
    - **S4 (new): the battery gauge's capacity figures stepped +12 mAh between d05 post (gauge time 09:52:45) and d06 pre (09:59:45).** `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` and `NominalChargeCapacity` each rose by 12. Voltage held at 12890 mV, and instantaneous and charging current were 0 at both readings. **Executed follow-up (the judge's NOT EXECUTED item):** `pmset -g log` for 2026-09-27 has **no charge, battery or AC-source event anywhere in the day**. Between 09:40 and 10:09 it shows only routine assertion summaries, cloudd network tasks, and one powerd darkwake inactivity-model query at 09:59:59 ([pmset-log-0940-1009.txt](10-w2-harvest/pmset-log-0940-1009.txt)). This is consistent with a gauge re-estimate, not charging. The registered verdict is defined on the endpoint readings and stands either way; the step is disclosed to Ed.
```

### 00-activation-record.md lines 40–42

Primary source: `docs/process_traces/2026-09-27-activation-77b1bee2/00-activation-record.md` (sha256 `ce5e38ae505f078b4bd6b6530bdcdfa07f1cf9d8cf39ef95f68d917852579e37`). Verbatim:

```text
      - **S1** (merge commit only): adopted. The merge uses `gh pr merge 434 --merge`.
      - **S2** (harvest notice content): the notice had already gone out, as Gmail `1a0e42d7ad74be5f`, carrying both battery lines. A **correction was sent as Gmail `1a0e43cab8a8ea93`**. It says W3 is *not permitted* (prereg: permitted only if fewer than 12 valid after W2; the issuer refuses it, `issue_…py:1838`), that n = 12 has zero margin, that the yield was 50 % against ≈79 % assumed, and that there is no top-up.
      - **Item 8 is corrected:** "W3 not needed" should read **"W3 not permitted"**. REV5-POST-W3-SHORTFALL-01 is **not moot**: it governs what happens if `prepare-candidate` refuses after W2, and that goes to Ed or a cold gate **before** `prepare-candidate` runs.
```

### 00-activation-record.md lines 38–38

Primary source: `docs/process_traces/2026-09-27-activation-3ba66eeb/00-activation-record.md` (sha256 `8efdc046143f93f02f44b4b0e20b9ad2fdb440fade72f74299048fabd686d394`). Verbatim:

```text
10. **Science note for W2 planning, not a gate.** The valid yield is 6/12 (50 %), below the pre-registration's projected valid rate near 30/38 (≈79 %). The rows were not opened. What the registration's stopping and replacement rules imply for W2 when the yield is this low is for the W2 planning step to read from the registration text itself.
```

The W2 gauge-step source is activation 77b1bee2 item 11 S4; the W1 6/12 comparison is activation 3ba66eeb item 10. The yield statements above are reproduced source text, not a packet ruling.
