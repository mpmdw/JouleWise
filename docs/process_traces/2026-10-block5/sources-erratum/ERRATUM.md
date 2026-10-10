# Block 5, draft Erratum 2 (prospective): where the harvest takes a window's reference list from when the stored verdict records none

Drafted by the magistrate (activation cbe4230e, Opus 5.5) on 2026-10-10 for a cold gate under registration
section 10 (one judge, one refuter). Structure only: no energy, power or duration, no member's name. Line
numbers of the registration are those of the sealed file of the second seal
(`configs/campaigns/v5_claim_25g83/registration_block5.md`, sha256 `c7b3fdf7…db3f`); code line numbers are
those of the pinned harvest program's commit `224a264c5faaae90cdf56118df37e773a932700b`, which contains
the sealed tree.

## 1. The terms this erratum uses

- **Reference.** A short run of one fixed small workload. Each window runs three at its start, one at its
  midpoint and three at its end. If the machine's energy cost of that fixed workload changed between
  start and end by more than a bound, the window drifted and is removed.
- **Bound.** The largest start-to-end change that noise alone explains, computed from the spread of the
  window's own corpus (18 further runs of the same workload at the window's start; the deciding bound
  uses the first 12 clean ones and needs at least 10).
- **Screen.** The comparison of the references' start-to-end change with the bound. It needs at least 2
  usable references at the start and 2 at the end; with 2 instead of 3 the bound is widened by a
  registered formula for the smaller count (registration 0.12, near line 1172).
- **Spare.** One extra reference, a byte copy of a stage's first reference under its own run id. After a
  reference stage in which a reference did not succeed, the chain runs the stage's spare once.
- **Campaign manifest.** Each stage of a window is one invocation of the campaign runner. The runner
  writes one manifest file per invocation into the runs root's `campaign_manifests/` directory, listing
  the members it handled and how (`invoked`, `existing`, `blocked_before_invoke`), and appends to the
  runs root's campaign log one attestation of that file's exact bytes.
- **Authenticated catalog.** The function `campaign_provenance.load_authenticated_campaign_catalog`
  (`joulewise/campaign_provenance.py`, near line 1040). It returns the manifests of a runs root only if
  every manifest file there matches exactly one attestation in the campaign log for its current bytes;
  if any one does not, it returns nothing.
- **Verdict writer and stored verdict.** After the window, the harvest starts the measurement clone's own
  sealed program (`scripts/run_campaign.py --whole-window-verdict`), which writes
  `whole-window-verdict.json` into the claim runs root. That file lists the manifests it was written from
  (`row_provenance.source_campaign_manifests`, each a path and a SHA-256) and holds its own result of the
  screen (the stored bracket).
- **Re-screen.** The harvest does not trust the stored bracket. On every window whose bound was derived
  it runs the screen again itself, over "the reference bundles the verdict names" (registration near
  lines 2892 to 2917), after dropping every reference that was lost: one that did not succeed, failed
  validation, or overlapped a physical disturbance found at the harvest. "The re-screen alone decides",
  and "a re-screen that cannot run leaves it failed" (line 2915).

## 2. What happened

BETA attempt 1 of the second seal (`v5-b5-beta-a1-20261010T0742Z`) ran its whole chain. One end reference
was aborted at idle admission at run time, so the chain ran the end spare. The spare's child process
refused within about ten seconds and left no bundle; the runner recorded the spare in its manifest as
`invoked`, with exit code 1. At the harvest one start reference was dropped for a competing process that
overlapped its request. The references that remain usable are 2 at the start, 1 at the midpoint and 2 at
the end: a shape the registered screen is defined for. The bound was derived and validated.

The harvest nevertheless removed the window with `neg8.screen_failed`, and the screen was never
evaluated. The chain of causes, each step proved from the code by a Sol 6.1 seat
(`/Users/edr/night-archive/b5-consults/beta-a1/fix/sol-fix.md`) and each fact on the window proved by a
count program that prints closed-list words and integers only (`seal2-beta-a1-consult.md`):

1. All 10 manifests of the runs root authenticate (9 stages and the spare invocation). Authentication
   checks a manifest's bytes against the log; it does not require an invoked member's bundle to exist.
2. The sealed verdict writer, when it resolves the window's members from the manifests, treats an
   `invoked` member with no bundle as `terminal_absent`, and on a block-5 runs root one such member makes
   it reject the manifests as its source altogether (`scripts/run_campaign.py` near lines 7580, 7884,
   8018). It falls back to the bundle directories that have summaries, which carry no roles, and writes
   an empty source list (near 8106 and 8590).
3. With no roles the writer finds no references, so the stored bracket is "missing" with no claim family.
4. The harvest's source selection returns `source_manifests_unrecorded` when the verdict's source list is
   empty (`joulewise/b5/harvest.py` near line 1127), and the re-screen does not run.

The same count on the first seal's ALPHA attempt 3, the only other window in which a spare ran, shows the
same thing: one invoked spare, no bundle, exit code 1, a recorded child refusal. So on the evidence so
far the spare never produces a bundle in a live window, and every window that loses a reference at run
time is removed by this path whatever its physics. The registration's own estimate of that loss is 1
member in 37 (line 4638); with 7 references a window, roughly one window in six.

## 3. What the sealed text says, and why this is an erratum and not a program repair

The registered rule is the one quoted in section 1: the re-screen runs over the references the verdict
names, and a re-screen that cannot run leaves the screen failed. The passage near lines 4053 to 4062
covers the neighbouring case, a verdict whose sources do not authenticate: there the harvest reads the
campaign manifests "as written (… unauthenticated, used only to name references, never for an energy or a
passing screen)". Nowhere does the text tell the harvest to take the reference list from the
authenticated catalog when the verdict records no sources. The Sol seat read it the same way. So the
pinned harvest program does what the registration says, and changing it is a change of rule: section 10,
a prospective cold erratum. The rule's author did not foresee that the writer would discard an
authentic source list because a spare left no bundle; the text has no reason for that outcome.

## 4. The change

**Rule added to registration 6.5 and 0.12 (the re-screen), for every attempt armed after this erratum
is admitted.** When, and only when, the stored verdict's `row_provenance.source_campaign_manifests` is
absent or empty, the harvest takes the window's source manifests from the authenticated catalog of the
claim runs root, and the re-screen runs on them as follows.

1. *The catalog must load.* `load_authenticated_campaign_catalog(runs_root, campaign_log)` returns the
   manifests or nothing. Nothing means the re-screen cannot run and the screen is failed, as today.
2. *The same policy check as for recorded sources.* Every manifest must carry the campaign policy digest
   of the verdict row, and that digest must be a registered bracket policy. Member paths must be safe
   paths inside the runs root, and no bundle id may appear twice. Any failure: the re-screen cannot run.
3. *The references are the manifest members whose role and sentinel position are start, midpoint or
   end.* A spare has its slot's role and position, so it is a reference of that endpoint.
4. *The same loss rules as today, and one more.* A reference is lost if its summary status is not
   `succeeded`, if it fails strict validation or the custody triangle, if its energy cannot be read, or
   if it carries one of the harvest's loss codes (`NEG8_REFERENCE_LOSS_CODES`). In addition a reference
   whose bundle directory is absent is lost (`bundle_absent`); that is the spare of this case.
5. *The clean bound is required.* The recovery runs only with the clean bound of the corpus cap rule
   (first 12 clean corpus members, minimum 10). Without it the re-screen cannot run.
6. *The registered evaluator decides,* `whole_window.evaluate_neg8_point_drift`, with the count-adjusted
   bound for the surviving counts: 2 or 3 at each endpoint and 0 or 1 at the midpoint. Fewer than 2 at an
   endpoint is `neg8.screen_failed` with reason `references_insufficient`. More references than planned
   is a failure. The older protocol that accepts one reference per endpoint is not accepted here.
7. *The step that cannot be made.* For recorded sources the harvest first re-derives the bracket without
   its own losses and requires the stored bracket's endpoints and estimand, to prove "these are the
   bundles the verdict was written from". Here the stored bracket has no endpoints, so there is nothing
   to compare. In its place stand the two checks the comparison was a proxy for: the catalog's
   all-or-nothing authentication against the campaign log (item 1), and the harvest's own checks on each
   surviving reference bundle, which it applies to every member of the window (bytes against recorded
   hashes, strict validation, the custody triangle, the window's launch lineage).
8. *Disclosure.* `derived/neg8-screen.json` records `reference_source` as
   `claim_campaign_manifests_authenticated`, and a failed screen carries the same word in its `observed`
   field. The paper's attempt table marks every window whose screen was decided on this path.

**Unchanged.** Every threshold; the bound and its formula; the endpoint minimum of 2; the corpus rule;
the flag catalog and each code's effect (no code is added or removed); the roster; the blinding rules;
every file a window reads; the measurement clone, the claim head and the seal commit. A verdict that
records sources is handled exactly as before (the fix seat's test compares the derived output byte for
byte with the pinned program's). A verdict whose recorded sources do not authenticate is handled exactly
as before (lines 4053 to 4062).

**Why it cannot let a drifting window pass.** The recovery changes only where the list of references
comes from. The list it uses is authenticated by the same function and the same log the writer uses;
each reference then meets the same loss rules; the screen is the same evaluator with the same bound and
the same minimum. A window with fewer than 2 survivors at an endpoint, with a start-to-end change above
the bound, with a manifest that does not authenticate, or without a clean bound is removed exactly as
before.

**Registered deviation, added to the list in section 10.** In a live window the reference spare has so
far left no bundle (2 of 2 spare invocations, each with a recorded child refusal). Until a later change
to window code under section 7.5, a reference lost at run time is therefore not replaced, and the
passages that describe a succeeding spare (near lines 997 to 1003 and 1151 to 1168) describe the
design, not the observed behaviour. The cause of the refusal is not established; it is window code and
is not changed here. The consequence for the screen is only a smaller margin: an endpoint that loses
two of its three references removes the window.

## 5. Mechanics

- This erratum is a separate document. The sealed registration's bytes are not edited, in the clone or on
  main, so the registration digest that every plan carries stays `c7b3fdf7…db3f`, and no window input
  changes (registration 10 uses the same device for a new sizing file). It is pinned by its SHA-256 in a
  new addendum to the seal record `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`.
- The harvest program that implements it (branch `lane/2026-10-10-harvest-screen-sources`, changes in
  `joulewise/b5/harvest.py` and `joulewise/whole_window.py` and tests only) goes through the gates for
  desk code on the claim path (magistrate brief section 9: an independent executing review, the whole
  suite, CI, a cold Fable 5.1 pass, findings dispositioned) and is pinned by a new `B5-HARVEST-PIN:` line
  in the same addendum. No harvest relies on this rule before that pin is on main.
- An attempt may be armed as soon as the erratum is admitted, before the program is pinned: the rule is
  what must precede the window; the program runs after it.

## 6. Questions for the judge

- **J1. Is the rule sound,** and is item 7 (the comparison that cannot be made) adequately replaced?
- **J2. BETA attempt 1.** Section 10 says "None to §§3–9 for an armed or completed attempt." The draft's
  position: the rule is not applied to BETA attempt 1. That attempt stays collected, not claim-usable
  (`neg8.screen_failed`), kept and disclosed, its energies never analysed, and BETA attempt 2 is armed.
  The other reading: nobody has read an energy of this window, the change was decided from codes and
  counts alone, the removal has no physical cause, and applying the rule would save a six-hour window;
  against it, the rule would be written after seeing that this particular window fails under the old
  one, which is the thing section 10 exists to prevent, whatever the blinding. Rule which reading
  holds. If the rule may be applied, say what makes that sound and how the paper discloses it.
- **J3. Does BETA attempt 1 count toward the "same cause twice" rule** (registration 7.3) if a later BETA
  attempt is removed in the NEG-8 family for a different reason?
- **J4. Mechanics.** Is a separate pinned document enough, or must the registration be re-issued (a new
  seal commit and with it a new clone and a restart at ALPHA, which would cost the claim-usable ALPHA
  window)? Is the arm-before-pin order of section 5 sound?
- **J5. The spare.** Is the registered deviation the right handling for now, or does the evidence
  require the window-code fix (and the supersession it brings) before another window?
