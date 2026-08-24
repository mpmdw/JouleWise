# Blacksmith runners — desk evaluation (TEST-SPEED-01 lever 3)

Date: 2026-08-23. Desk evaluation only: no account was created, no
application installed, no purchase made, and no Blacksmith service was
contacted beyond fetching their public documentation.

**Verdict: DO NOT ADOPT. Recommend `defer` — and, on the present facts,
`reject` until three separate conditions change.**

Throughout, a claim marked **[verified here]** was checked directly during
this evaluation. A claim marked **[researched]** comes from a delegated
web-research pass and is reproduced with its source and retrieval date but
was not independently re-derived.

---

## 1. What Blacksmith is, and what adopting it would mean mechanically

Blacksmith rents machines that run GitHub Actions jobs in place of the
machines GitHub itself provides. A GitHub Actions job names the machine it
wants with a `runs-on:` line. Adoption therefore looks like a one-line edit
per job — replacing GitHub's `ubuntu-latest` with a Blacksmith machine
label:

```yaml
    runs-on: blacksmith-2vcpu-ubuntu-2404   # instead of: ubuntu-latest
```

`blacksmith-2vcpu-ubuntu-2404` is the label Blacksmith's own quickstart
gives as the replacement for `ubuntu-latest` **[verified here** — fetched
https://docs.blacksmith.sh/introduction/quickstart on 2026-08-23**]**.
Larger sizes exist (`blacksmith-4vcpu-…`, `-8vcpu-`, `-16vcpu-`,
`-32vcpu-`) **[researched]**.

Because `runs-on:` is a per-job string, adoption is *per job* and reversal
is the inverse one-line edit. That reversibility is real and is Blacksmith's
best property. It is not, however, the binding consideration.

---

## 2. The blocking finding: this repository is ineligible

Blacksmith's quickstart states, verbatim:

> "Blacksmith is limited to GitHub organizations and not available for
> personal repositories."

**[verified here** — fetched from the quickstart page 2026-08-23, quoted
back exactly**]**

`JouleWise` is owned by a **personal user account**, not a GitHub
organization **[verified here** — `gh api repos/:owner/:repo` returns
`owner_plan: "User"`, `visibility: "PUBLIC"`, 2026-08-23**]**.

So adopting Blacksmith is not a workflow edit. It first requires
transferring the repository into a GitHub organization. That transfer
changes the repository's canonical URL — the address printed in
advisor-facing surfaces and cited by published artifacts. GitHub redirects
the old URL, but the identity of the artifact changes. For a capstone whose
argument rests on auditable provenance, changing the canonical identity of
the evidence repository in order to rent CPUs is a poor trade, and it is
not a decision this lane may take.

---

## 3. The cost comparison is against zero, not against a smaller number

GitHub-hosted standard runners are **free and unlimited on public
repositories** **[researched** — GitHub Docs runners reference, fetched
2026-08-23**]**. This repository is public **[verified here]** and every job
in `.github/workflows/ci.yml` uses the standard `ubuntu-latest` runner
**[verified here]**. **Current CI spend on this repository is $0, against
no minute quota.** The 41-minute wall clock measured under lever 1 is slow,
but it is free and it consumes no allowance.

Blacksmith's published pay-as-you-go rate is **$0.004/min for Ubuntu x64**
with **3,000 free minutes/month**, and no SLA on that tier (the 99.9% SLA
is an Enterprise-tier benefit) **[researched** — blacksmith.sh/pricing,
fetched 2026-08-23**]**. The headline rate is the **2-vCPU** rate; larger
instances cost proportionally more, and the exact multiplier is **not
published** — treat any 8-vCPU figure as unverified.

A single full CI run of this repository is on the order of a few hundred
runner-minutes today (the crash-matrix job alone is ~89 min × 2
interpreters). Under active multi-stream development the 3,000-minute
allowance would not last the month at 2 vCPU and would last far less at 8.

**Adoption converts a $0 line item into a usage-coupled, open-ended one.**
The absolute magnitude would be modest — tens of dollars per month — but
the comparison that matters is not "is this cheap," it is "is this cheaper
than free."

---

## 4. The hardware premise, corrected

The evaluation was commissioned on the belief that GitHub's free hosted
runners give 2 vCPUs. **That is wrong for this repository.** GitHub-hosted
`ubuntu-latest` gives **4 vCPU / 16 GB on public repositories** (2 vCPU /
8 GB is the *private*-repo tier) **[researched** — GitHub Docs runners
reference, fetched 2026-08-23**]**.

Two consequences, both against adoption:

1. The observed slowness is already happening on 4 vCPUs, so the
   "starved runner" thesis has less headroom than assumed.
2. Blacksmith's *documented* drop-in replacement for `ubuntu-latest` is the
   **2-vCPU** label. Taking the migration literally would **halve this
   repository's core count**. A genuine attempt to buy more cores must
   deliberately select `blacksmith-8vcpu-ubuntu-2404`, at unpublished cost.

Blacksmith does not publish CPU model or clock speed; the marketing claim
is "bare-metal gaming CPUs" and "2x faster hardware," which are vendor
self-measurements **[researched]**. The plausible ceiling is roughly 2×
cores × ~1.3–1.5× clock ≈ **3×** — against a 36× problem. Even granting
every vendor claim, the hardware does not close the gap.

---

## 5. Why more hardware is the wrong instrument here

The decisive evidence is in this repository, not on Blacksmith's website.
`TASK_QUEUE.md`'s WO-CRASHMATRIX-RELIABILITY row records three
observations of the same module **[verified here** — grepped from
`TASK_QUEUE.md`, 2026-08-23**]**:

| Condition | Runtime | Outcome |
| --- | --- | --- |
| M3 Max bench, standalone | 145.911 s | pass |
| M3 Max bench, **under load** | 1848.071 s | **FAILED, errors=3**, hitting 600-second per-case ceilings |
| GitHub hosted shard | 5317.216 s | pass (run 31536564643) |

The middle row settles it. **The fastest machine in this project takes
12.7× longer and outright fails merely because something else is running on
it.** That is not a machine too small for the work; it is a fixture whose
result depends on how contended the machine is.

The mechanism is visible in the test source **[verified here]**:
`tests/test_calibration_writer_crash_matrix.py` passes hard-coded
one-second wall-clock deadlines to the component under test
(`--sampler-ready-timeout-s 1.0`, `--rollover-timeout-s 1.0`), and its
survivor-guard case deliberately spawns a CPU-burning child —
`subprocess.Popen([sys.executable, '-c', 'while True: pass'])` at line 873
— which consumes a quarter of a 4-vCPU machine for the duration. Deadlines
tuned to bench-speed process startup do not degrade gracefully when startup
slows: a case that misses its budget pays the *entire* timeout instead of a
few milliseconds. The cost curve is therefore a **cliff**, not a slope, and
faster hardware moves the cliff without removing it.

This is why the ranking below puts a paid hardware upgrade last. Buying
speed would reduce how often deadlines blow. It would leave a suite whose
verdict is a function of machine load — the wrong defect to paper over with
a credit card in a project whose entire thesis is measurement rigor.

---

## 6. Availability risk

Blacksmith published a postmortem for a **five-hour total outage on
2026-07-21** — 33 days before this evaluation — in which, in their own
words, "customer jobs were not picked up by Blacksmith for several hours
during this outage, completely blocking development workflows"
**[researched** — blacksmith.sh/blog/blacksmith-outage-on-july-21-2026,
fetched 2026-08-23**]**. A third-party monitor reports 42 incidents in the
preceding 90 days **[researched;** aggregator counts can over-count from
status-page granularity and were not reconciled incident-by-incident —
treat the count as unverified, the order of magnitude as corroborated by
the vendor's own postmortem**]**.

`runs-on:` is a static string with no automatic failover. During a
Blacksmith outage, jobs queue and hang; recovery is a manual commit
reverting the label, which itself needs CI to validate. **A multi-hour
unannounced CI blackout is a materially worse failure for this project than
a slow job that finishes.** The current 89-minute job is irritating; it is
never *stuck*.

On security the assessment is genuinely favourable and should be recorded
as such: SOC 2 Type 1 and Type 2, jobs isolated in ephemeral Firecracker
microVMs with hardware (KVM) isolation, state destroyed at job end
**[researched]**. This repository's CI uses **no secrets at all**
**[verified here** — zero `secrets.` references in `ci.yml`**]** and the
source is already public, so the marginal exposure is CI metadata only.
Security is not the reason to decline.

---

## 7. Ranked options

1. **Split the slow work across more GitHub-hosted jobs (free).** Uses
   hardware already available without limit, costs nothing, adds no third
   party, and reverses in one commit. Implemented as TEST-SPEED-01 lever 2.
   Constraint to respect: GitHub Free permits **20 concurrent jobs**
   **[researched]**, and `ci.yml` currently defines 14, so the job budget
   is 6 — see the lever-2 evidence file for how it is spent.
2. **Fix the fixture (WO-CRASHMATRIX-RELIABILITY, already registered).**
   The only option that removes the cliff rather than lowering its
   probability, and it also retires the module's bench load-sensitivity.
   Out of scope here: it changes test semantics, which this lane is fenced
   against. Explicitly **not on the paper critical path** per its queue row.
3. **Blacksmith.** Reject on present facts.

**Revisit only if all three change:** the repository moves to a GitHub
organization for reasons of its own; Blacksmith's OSS sponsorship is
granted (making it free); and the fixture has been fixed — at which point
the capacity would no longer be needed.

Nothing here requires an Ed decision to *proceed*, because the
recommendation is to do nothing. The one item Ed alone could change is the
organization-transfer question, and this evaluation recommends against
raising it for CI reasons.
