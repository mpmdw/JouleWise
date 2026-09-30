## 5A. Pre-window clock stabilization (administrator step; Ed performs it)

**This is operational stabilization, not a protocol waiver.** The 5 ms
wall-versus-monotonic anchor ceiling stays exactly where it is. It is never
relaxed, widened, or waived, and a member that trips it is still lost. The
steps below reduce how often the machine trips it. They do not change what
trips it.

### JW-MET-2 keyboard-backlight census control

Before the untouched idle begins, open **System Settings → Keyboard** and set
keyboard brightness to zero, turn **Adjust keyboard brightness in low light**
off, and set **Turn keyboard backlight off after inactivity** to **Never**.
Visually verify the zero level: macOS provides no reliable CLI for the actual
backlight level. Record these four literals exactly:

```text
keyboard_backlight.level=0
keyboard_backlight.automatic_adjust=false
keyboard_backlight.inactivity=never
keyboard_backlight.verification=operator_visual
```

`quiet_mac_prep.sh` inventories whether `ioreg` reports
`KeyboardBacklight`; `prewindow_check.sh` repeats the visual-verification
census note. Neither substitutes for Ed's System Settings observation. Make
no further keyboard or backlight adjustment after authoring T-0 evidence.

### What went wrong, in plain language

Every measured member must be anchored causally in time. The anchor check
compares two clocks: the **wall clock**, which is the machine's idea of the
current date and time and which network time synchronisation adjusts, and the
**monotonic clock**, a counter that only ever counts forward and is never
adjusted. The difference between them must stay within `5 ms`
(`MAX_WALL_MINUS_MONOTONIC_SPAN_S`, `joulewise/uncertainty_evidence.py:22`)
across a member's clock stamps. When it does not, the predicate at
`joulewise/uncertainty_evidence.py:367` refuses the member with the detail
string `wall_minus_monotonic_span_exceeded`.

Two consecutive window-C collection attempts on 2026-07-26 failed on exactly
that, and on nothing else:

| Attempt | Member that failed | Observed span | Implied rate |
|---|---|---:|---:|
| 1 | `p2015-df-cmp-abba-ph-decode-b02-b2` | 5.544 ms | about +110 ppm |
| 2 | `neg8-refcorpus-r11` | 7.769 ms | about −158 ppm |

Rates of that size are what `adjtime(2)` produces. `adjtime(2)` is the system
call network time synchronisation uses to correct the wall clock by speeding
it up or slowing it down by a fraction of a percent, instead of jumping it, so
that time keeps increasing. The evidence shows a **slew** — a gradual change
of rate — and not a demonstrated discrete step: no timestamp ever moved
backward, and the native powermetrics second counter advanced only by 0 or 1
whole seconds. A step hidden inside the roughly 44-second gap between stamps
cannot be categorically excluded.

Two things are unknown and must be written as unknown wherever this is
reported:

- **The responsible process is unknown.** `joulewise/environment.py:908`
  assigns `clock_sync.status = "limited_without_admin"` unconditionally, and
  the `timed_running` field only reports whether `pgrep` found the process.
  Every member, passing and failing alike, reported `timed_running=true`. The
  macOS `timed` daemon is therefore **plausible but unproven**; attributing it
  would require privileged inspection of the unified log.
- **The correlation with time of day is noted but unproven.** Window B had
  zero occurrences across 59 members, collected 23:57–03:15 local. Window C
  ran roughly 7% per member — 2 occurrences across about 30 members, collected
  03:17–05:19 local. Do not assert a nightly maintenance-window cause.

What is established: only a privileged wall-clock adjuster can produce this.
Ordinary sampling load, thermal state, and CPU activity cannot move the wall
clock relative to the monotonic clock. The excursion also self-clears — member
`neg8-refcorpus-r12`, collected immediately after the failing `r11`, anchored
cleanly with a 0.305 ms span.

### Before the window (administrator rights required)

macOS gates both the read and the write of this setting behind administrator
rights (`systemsetup -getusingnetworktime` and
`systemsetup -setusingnetworktime`). E-4's prior-state read remains an
interactive Ed action. D-127 authorizes only the exact `off` and `on` writes;
the capture wrapper and the T-0 author use the `off` vector, and restore uses
the `on` vector. No wildcard or privileged `get` is authorized.

The tracked D-127 fragment must contain exactly these bytes (final newline
included; SHA-256
`7dfe980be89a7912d69c6e72b5582649fc4c50db88bf709bcfbb4a1c34e4406d`):

```sudoers
# JouleWise D-127: fixed network-time toggle capability for operator edr.
Cmnd_Alias JOULEWISE_NETWORK_TIME = /usr/sbin/systemsetup -setusingnetworktime off, /usr/sbin/systemsetup -setusingnetworktime on
Defaults!JOULEWISE_NETWORK_TIME !requiretty
edr ALL=(root) NOPASSWD: JOULEWISE_NETWORK_TIME
```

- [ ] **ED-OWED:** after the reviewed tracked fragment
  `scripts/joulewise-network-time.sudoers` exists, run the authenticated,
  no-overwrite installer from
  `docs/legacy/process_traces/2026-08-08-d127-autonomous-loop/CONSULT-RESPONSE.md`
  with that source path and the digest above. Ed alone installs
  `/etc/sudoers.d/joulewise-network-time`; no repository script runs as root.
- [ ] **ED-OWED:** exercise both exact vectors from a cold credential state,
  restoring `on` at the end:

  ```sh
  /usr/bin/sudo -k
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
  ```

  A password prompt, any nonzero exit, or any other permitted
  `systemsetup` argv leaves D-127 unqualified and blocks T-0.

- [ ] **Confirm the system clock is actually correct first.** Disabling
  automatic time on a wrong clock freezes that error in place for the whole
  window. Compare the system clock against an independent trusted source and
  correct it before going further.
- [ ] Record the current setting so it can be restored:

  ```sh
  /usr/bin/sudo /usr/sbin/systemsetup -getusingnetworktime
  ```

- [ ] Disable automatic network time adjustment:

  ```sh
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off
  ```

- [ ] Preserve the independent-clock comparison and the captured prior
  `systemsetup` output as source evidence. Require an authenticated exact-key
  `CLOCK_ATTESTATION` receipt in
  `ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.evidence/`; its irreducible observation
  is an `OPERATOR_ATTESTATION`, not a hand-entered readiness verdict.
- [ ] After disabling network time, require the T-0 author's fresh,
  idempotent D-127 enforcement call
  `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` and an
  authenticated exact-key `CLOCK_PROBE` receipt in the same namespace. The
  successful exact write, not an operator-entered row value, establishes the
  current off postcondition. For both receipt kinds, “exact-key” means the top-level
  object contains exactly `schema_version`, `evidence_id`, `kind`, `status`,
  `issued_at_utc`, `valid_until_monotonic_ns`, `pack_sha256`, `head_commit`,
  `facts`, `checks`, `reason_codes`, and `assurance`; unknown or missing keys
  refuse.

- [ ] Do **not** hand-count a settle here. §5C removed the separate pre-launch
  settle step: the final 180-second settle is **chain-owned** (the `settle` at
  the top of `window-chain.zsh`, §6), and §5's ≥10-minute untouched idle
  covers this administrator action along with every other operator action
  before the §5C step-2 ledger pair. Your last action is the launch itself;
  step away immediately after it.

  The readiness row `clock.network_time_off` asks only for that fresh exact
  enforcement result.
  It does not introduce another hand-counted settle. The required quiet waits
  remain §5's completed ≥10-minute untouched idle and the chain-owned
  180-second settle after the operator's launch.
- [ ] After the window closes, meaning after `measurement_complete`, the
  whole-window verdict, and the backup, re-enable it:

  ```sh
  /usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on
  ```

  The restore comes last because re-enabling automatic network time permits
  the system to slew the wall clock, and the verdict, backup, and close-out
  steps are still reading clock-anchored evidence and custody metadata. Wake
  the display, confirm `measurement_complete`, then hand back — the restore
  is a separate tap after the magistrate's §9 and §11 steps.

- [ ] Record in the close-out that automatic time was disabled, when it was
  disabled, and when it was restored.

Leaving automatic time off is not a protocol state. It is a temporary machine
condition the operator owns for one window, and the close-out must show it was
returned.

### If a single member still fails the anchor

Stabilization lowers the rate; it does not make the failure impossible. When
one member refuses with `wall_minus_monotonic_span_exceeded`, no member-level
anchor retry is adopted. Under D-113 clause 9, no such retry occurs without a
prospective ruling made before the plan freeze:

- [ ] **Do not mint a bound, a verdict, or a floor from a basis that contains
  the invalid occurrence.** An invalid member never becomes a valid one.
- [ ] Preserve and quarantine the invalid member. Valid members already
  collected stay exactly where they are, but no replacement member is
  collected under an unruled retry.
- [ ] Stop the stage under the existing `--max-failures 1` behavior and take
  the disposition to the lead. Do not hand-retry, supersede, or rerun the
  dual-family bound mint as if a member-level retry were licensed.

`--max-failures` stays at 1. Every admission gate, every family screen, and
every refusal stays exactly as written. Calibration-only retry remains
governed as written in §6 and is not changed by this member-level prohibition.
