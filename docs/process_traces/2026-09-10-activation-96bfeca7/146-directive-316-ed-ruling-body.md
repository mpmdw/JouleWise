Ed's ruling on the evening 09-10 email (Gmail 1a08e62b7e99b312, "decisions I need from you"). Filed on Ed's behalf by Fable from an interactive session on 2026-09-10 ~21:20 PDT after Ed read the recommendation and signed off in his own words ("cant you pass that to the magistrate yourself? i sign off"). The ruling is Ed's; the wording is Fable's.

## Decision 1 (V3 default: three nights of 12 captures, retained n >= 19): NO

Do not arm three derivation nights as the default path. The reason, in Ed's words: the scheme "is acting for an adversary that doesn't exist"; with a single trusted operator (D-161) the question is an instrument one: did the OS point release move the clock-anchor bound or not? That is answered by one quiet night compared against the envelope already in force, not by a three-night blind derivation.

## What replaces it: night one is an EPOCH-EQUIVALENCE CHECK, rule fixed here before any capture

1. The first quiet night is ONE derivation-kind ledger session of 12 slots run by the merged chain exactly as built (PR #315; runbook docs/phase_2/derivation_night_runbook.md; NIGHT_HANDBACK email-then-arm unchanged; tonight's rehearsal-20260911 untouched). Nothing about the arm, the chain, the settle, the census, or the dead-man changes.
2. After the night closes, the magistrate READS the night's retained values and applies this rule, written now:
   - Reference envelope = the acceptance in force, d079_calibration_acceptance_v2_n17_r6: corpus maximum (level screen) 0.03289849371536248 s, corpus range (bracket screen) 0.00972358928879385 s, n = 17, plus the budget ceiling as the validator computes it for r6. The magistrate confirms these operative constants from the artifact and the validator's own code path and quotes them in the record; if the validator's operative screen differs from the raw range (the never-zero floor), the operative value is the one used.
   - Retained m = the night's valid, resolved captures (anchor-v3 replay resolved, not window_exhausted or slot_refused). If m < 6 the check is INCONCLUSIVE: run one more equivalence night before deciding. No other action.
   - PASS = every retained b_fiducial_s <= the r6 level screen AND the night's range (max minus min of the retained values) <= the r6 operative bracket screen.
   - FAIL = anything else.
3. On PASS: the r6 acceptance is CONTINUED onto identity epoch 25G83 by a dated addendum under D-102 that Ed authorizes here ("epoch continuation on evidence": an identity-field change followed by a same-envelope night continues the acceptance in force rather than voiding it). The addendum cites the night's session id, the twelve slot outcomes, and the m values verbatim. Ordinary capture and the first real G2-a window proceed on the next quiet slot after the addendum lands. The 25G83 pre-registration stays on file, un-withdrawn, as the fallback route. If continuation needs a code change (the epoch-freshness refusal in the loader or issuer), the magistrate lands it through the normal PR gate as the smallest possible change and reports the diff; it does not work around a refusal by hand.
4. On FAIL: the pre-registered three-night derivation proceeds as written in configs/calibration/preregistration_d079_epoch_25g83_rev1.md, and V3 is then AFFIRMED by this issue (three nights, 12 slots, retained n >= 19, or exactly 17 with a written ruling). Night one COUNTS as registration night one. Ed rules here that examining night-one values under a rule fixed before capture does not compromise the derivation: blindness for this campaign means "every rule fixed before data", which this issue satisfies, not "no one may look". If the issuer's in-code blindness refusal blocks counting night one, the magistrate reports it and proposes the minimal change; it does not run a fourth night to satisfy the guard.
5. Record: the magistrate records this issue as pre-registration revision 2 (V3 answered; the equivalence rule and the continuation route added in Ed's words) and as a dated Ed addendum under D-102. This is Ed's ruling through the owner-authored channel, not a magistrate amendment of a process rule (rule 11 intact).

## Decisions 2, 3 and 4 in the email

Not addressed by this issue. Their stated defaults and veto windows stand exactly as the email wrote them.

## Timing

Earliest equivalence night: the early hours of 2026-09-12 as the email already proposed, subject to PR #316 landing, the handback rewrite, and the standing gates. The objective is real G2-a numbers on the first quiet slot after a PASS.

## While reading this

Side threads DOCS-THIN-01 and CI-TRIM-01 are running from the interactive session in linked worktrees /Users/edr/code/JouleWise-wt-docs-thin and /Users/edr/code/JouleWise-wt-ci-trim; they will open DRAFT PRs and never merge. Do not adopt, rebase, or delete those worktrees or branches.

