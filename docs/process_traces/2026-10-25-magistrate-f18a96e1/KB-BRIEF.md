# Design seat: the reading rule for the BYTES known-bytes stream test

You are one of two blind design seats. Another model answers the same brief independently; the lead
decides and writes the final text. Disagree with anything below if the evidence says so.

## Repository and scope
- Tree: JouleWise at commit 6731d524907a9c9f77eb51a5380410a705ffc657 (branch integrate/2026-10-24-416).
  It is the registered BYTES pass-1 tree.
- Read only. Change no file in the repository. Your only output is your report.
- No measured BYTES energy exists that you may read, and you need none. Do not open any path under
  /Users/edr/night-* or any blinded data. Non-claim check-session records committed in the repository
  (H and BY-H2 under docs/process_traces/2026-10-2*/ and configs/bytes/records/) may be read.

## The problem
`docs/registrations/bytes_pack_v1.md` §1 says the recorded powermetrics samples carry no DRAM key, so memory-read
energy is split between rails (the chip's share) and rest (the memory chips' share). Whether the GPU rail includes
the memory controller is to be measured by the known-bytes stream test (R8 item 6 of
`docs/design/bytes_pack_design.md`; probe `scripts/bytes_stream_test.py`; usage in
`configs/campaigns/bytes_mac_check/README.md` "Known-bytes companion probe"). The test runs after pass-1
collection and before stage-1 unblinding (§19, P0 ruling 9). §19 says "a boundary that does not respond as
registered carries that outcome beside its claim lines", but nothing registers what "responds as registered"
means. The registration cold gate (Opus 5.5, finding 4, `docs/process_traces/2026-10-24-magistrate-7209d1b0/REGGATE-OPUS.md`)
asked that, before the test runs, the registration state (a) which quantity is reported, with its bound, and (b)
which outcome triggers the printed caveat. It also noted the probe's receipt records no OS/runtime stack (C4
fields), so a stack change between pass 1 and the test would be invisible.

## What to deliver (one markdown report)
1. **The reported quantity or quantities**, defined so a reader can compute them from the receipt and the
   rails/DC-input traces alone: e.g. rails energy (and GPU-rail energy specifically) above the idle baseline
   over the receipt's exact CLOCK_MONOTONIC_RAW span, divided by the receipt's logical payload bytes, and the
   same for DC input. Name the idle baseline's source and span. Give each quantity's uncertainty bound and
   where every term of that bound comes from (the instrument's ~1 J attribution limit per run, meter resolution
   and sample interval, clock-placement error; cite the repository's own values, e.g. `joulewise/tolerances.py`
   and the registration's §7 and §12/§14).
2. **The outcome classes and the caveat rule.** Which result means "the GPU rail includes the memory controller
   (or memory-traffic energy)", which means it does not, and which is undetermined; which outcome prints the
   caveat beside the claim lines, and its exact wording. Every threshold must carry its derivation from the
   physics or from printed precision (no number without a derivation; an agreement bar sits between 1e6 x float
   noise and 1% of the smallest printed uncertainty). If a threshold cannot be derived before measuring, say
   so and give the rule that sets it from the test's own data (for example, a control arm), rather than a number.
3. **A control.** Does the test need a contrast arm (for example, the same span with a cache-resident payload,
   or compute without memory traffic) so that "rail energy rose" can be attributed to bytes moved and not to
   GPU activity in general? Specify it or argue it is unnecessary.
4. **B and N.** How the payload size and repeats are chosen: above which cache capacity (cite the machine's
   documented SLC/cache size if the repository records it; otherwise give the rule), and N to fill the planned
   one hour with enough energy above idle that the bound in item 1 is small against the quantity. Show the
   arithmetic with the repository's own numbers where they exist; where a number would have to be invented,
   write "measure first" and the rule.
5. **The C4 stack gap.** The smallest change that makes the receipt (or the test's harvest) record the same
   stack fields as a pass-1 session, so a stack change is visible. Name the fields and the source of each.
6. **A worked example** with plausible real-shaped numbers taken from the repository's records (cite them),
   carried through items 1 and 2 to an outcome class.
7. **Decisions I made**: list choices the texts determine that you settled yourself. Use NEEDS_RULING only for
   a choice that would change which data count or a printed number.

Keep it proportionate: this outcome changes no collected number, exclusion or estimator; it adds one printed line
beside the claim lines. Do not add process or new gates.

WRITE_SCOPE: []
