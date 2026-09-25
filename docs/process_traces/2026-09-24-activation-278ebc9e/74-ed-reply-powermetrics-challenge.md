# 74 — Ed's reply of 11:15:45 PDT 2026-09-24 (owner instruction), transcribed verbatim

Gmail message `1a0d4a18eb5f2c78`, thread `1a0d38b0e64ad452`, from `claude2.glaring610@passmail.net`, dated 2026-09-24T18:15:45Z. It replies to the magistrate's acceptance summary `1a0d38b0e64ad452`. The magistrate found it UNREAD at 12:06 PDT: the unread search had not run between ≈10:43 and 12:06, which is a slip against the every-slice rule, recorded here.

**Ed, verbatim:**

> are you sure about the powermetrics change? im pretty sure with a flag you can dictate the power timing, be very sure powermetrics changed, that drastic of a change in a .x bump in macos seems unlikely

## How the magistrate applies it

1. This is an owner challenge to a premise that cold ruling ACCEPTANCE-25G83-01 accepted: that `powermetrics` itself delivers about 0.245 s at a requested 100 ms on 25G83, against about 0.120 s under r6. The ruling made the cause attribution (lane A243) non-gating. Ed asks that the change be established with certainty before the project builds on it.
2. Action, immediately and at the desk (no sudo, no quiet window): a Sol evidence scout (brief 75) compares the EXACT `powermetrics` invocations recorded in the r6-era captures with those in the 25G83 captures: argv, `-i`/sample-rate flags, sampler set, output format, extra flags (for example process or thermal samplers that lengthen each sample), the binary sha and version, and the delivered `elapsed_ns` distributions per invocation. The question it settles is whether the ~0.245 s cadence is explained by a flag, sampler or harness difference rather than by macOS.
3. Until that evidence is in, no step of the acceptance lane that spends a quiet window (r8, the rev 4 seal, the W1 arm) proceeds. That lane is already gated on Fable. If the cause is a flag or harness difference, the acceptance ruling's premise changes: the right cure may be restoring the ~0.120 s cadence (option A) rather than a longer pulse. That goes back to the council and cold gate with the new evidence.
4. Ed gets a direct answer by email once the evidence is in, with numbers.
