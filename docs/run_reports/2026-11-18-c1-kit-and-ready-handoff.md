# C1 kit and READY handoff · 2026-11-18

**DRAFT / INELIGIBLE · Tier 0.** The [unsigned C1 template](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/c1-prearm/C1-READY-DRAFT.md)
starts at the later W1-to-C1 handoff. It covers C1-GATE rows 20–26.
PR #822 owns the earlier Part C/W1 templates, PR #831 the row builder,
and PR #836 the release script and its frozen 244-test evidence.
[Pipeline](https://github.com/mpmdw/JouleWise/blob/f1be75b21/docs/process/PIPELINE.md#L10-L18) · [PR #822](https://github.com/mpmdw/JouleWise/pull/822) · [PR #831](https://github.com/mpmdw/JouleWise/pull/831) · [PR #836](https://github.com/mpmdw/JouleWise/pull/836)

## Synthetic rehearsal

The materializer read invented inputs and invented Git blobs in a
disposable root. The packet CLI used the public `Scenario` fixture, with
the next-plan sentinel roster derived from the materialized C1 and a
fixed fixture clock. The series manifest and first 22 members matched
the ordinary materialization. The escalated C1 had 24 members, four
sentinels at 5/22/23/24, and sixteen fresh at 6–21, seven benign and one
seeded instructed per pair. The midpoint stayed after 11 and 23/24
replayed W1:5 as supplemental diagnostics. The sizing ceiling was
**62,400 s (17 h 20 min)** and the synthetic maximum fit under it.

| DRAFT case | Result and stopping check |
|---|---|
| Positive W1→C1 | PASS. C1 materialize and `--check` passed. The committed-record builder's packet preflight and rebuild comparison passed, and `bind_packet` accepted the W1→C1 order with zero prior counted C windows. Live checks stayed pending. |
| Missing W1 full desk | PASS, refused. Packet CLI returned 2. `full_desk_gate` failed for the omitted W1 desk and `next_arm_triage` rejected it. The public regression also rejects a desk tied to a changed artifact set. |
| Wrong predecessor or hash | PASS, refused. Substituting R1's commit/path against the W1 series state, or changing the ledger's W1 hash, hit `series previous record binding mismatch`. Changing only the supplied record hash failed the canonical rebuild comparison. An R1 predecessor for C1 failed `bind_packet` frozen order. |
| Absent four-binding proof | PASS, refused in the PR #836 receipt validator. Each omitted digest failed the release artifact inventory check and each null digest failed digest validation. The lead checks the accepted four-binding receipt at C1 readiness. This used the receipt validator entry point only. |
| READY posted during a qualification pair | PASS in a tabletop lead check. Before the second span's launch record on main, `SESSION_READY=no` and the ordinary ladder continues. Through qual-03, the second span runs to a proven clean close before effective READY can claim the next eligible close. |

An effective READY attempt that refuses releases the ladder immediately to
the next eligible rung under any applicable stop. Incomplete prerequisites
or an ineffective READY leave the ordinary ladder active. All rehearsal
cases remained DRAFT. [Refusal and qualification rule](https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18827-L18832)

## Verification and limits

The seat-only driver loaded the unchanged public packet-fixture definitions
at `b2e01464d` and the receipt validator at PR #836 head `221031020`.
It exercised five DRAFT cases plus two frozen packet regressions. The
materializer used the explicit pending-W1 planning allowances. The
unexercised sizing step is deriving C1's final member bounds and disk
reservation from the accepted R1-filled W1 plan on the final operational
pin. The synthetic packet used a local fixture remote-tracking ref.
Authenticating the real committed W1 desk and history, verifying signed
series admission, reading the accepted receipt on the final tree and
performing live admission and veto checks remain with the owning seats.
Heavy verification is the hosted docs lane.

Commands for the disposable root and the two-document diff

```sh
python3 -B scripts/align_v4_series.py materialize --root "$fixture" --window-id C1 --extra-sentinels 2
python3 -B scripts/align_v4_series.py materialize --root "$fixture" --window-id C1 --extra-sentinels 2 --check
python3 -B scripts/align_v4_next_arm_packet.py --repo "$fixture" \
  --record-commit "$record_commit" --record-path "$record_path" \
  --series-commit "$series_commit" --series-path "$series_path" \
  --pushed-ref "$fixture_ref" --output "$fixture/DRAFT-packet.json"
PYTHONPATH="$seat/source" TMPDIR="$seat" python3 -B "$seat/c1_rehearsal.py" \
  C1DraftRehearsal PacketTests.test_w1_record_admits_and_binds_all_raw_bytes_without_following_custody \
  DeskDerivationTests.test_after_w1_or_a_code_change_the_full_desk_must_have_passed_on_the_current_state
python3 -B "$seat/check_c1_docs.py"
git diff --cached --check
bash scripts/ci_docs_only.sh "$(git rev-parse origin/audit/2026-11-10-fable)" "$(git rev-parse HEAD)"
```

The driver invoked both CLI entry points in process, including the
packet clock fixture. The document check verified 29 frozen anchors, the
relative report link, the unsigned fields and the DRAFT labels. Hosted CI
evidence is attached to the draft PR's
exact head. Tier 0 uses the docs-only CI classifier, fences, build and
installed-wheel jobs.

## Opus handoff

Fill the W1 desk, Check and clearance, final operational head and Part C
carry, accepted signature and four bindings, series admission and C1 kit
commitments, rebuilt packet and history, typed READY and clean predecessor
restore, C1 notice and veto, fresh host admission, real t0 and outcome.
The template lists earlier proof the lead can carry by reference.
The next lead step is to bind the accepted W1 full desk and final head
to the C1 prerequisites before making C1 READY effective.

**NEEDS_SPEC** · None.
