# RL-181 dated transfer drafts · 2026-11-18

[Drafts and reproduction](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer/README.md)
are based on audit head e964c97d8278c023319b8ef748e75f0101011ca1,
which matched the remote audit head at intake. The branch is
align/2026-11-18-transfer-block.
The upstream audit branch subsequently advanced to ab63e041f with RL-182
and qualification's PR #812 draft successor. This delivery stays based on
the requested RL-181 commit and its transfer tooling reference. Recheck
the current issued ladder and admitted pin before any issue.

RL-181 approves 20 planned date places with one six-leg span each. Each
kit uses qualification's four A cells, one L pair, q0, Automatic and one
capture with five consumers. The four-place cycle is indexed by original
place, including a miss. The pin remains ab32a6c915a9a78f92554a89c5d0eb93333b7a39.
Expected pinned time is 12,262–12,310 s per span, worst case 24,750 s,
and pinned launch minimum 27,260 s. The draft queues are explicitly halted
and use a finite expired timestamp. Lead issue requires effective freeze
2, scientific registration and authenticated dated authority.

The first kit SHA-256 is
`62188932ab4011804d72bdce2d65c144e748f7ac62e45f0ebf4b747a47dddd9f`.
The [ordered roster of all kit and queue hashes](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer/date-place-roster.json)
has SHA-256 `cc2a29a95a0028f78ce85aaf9b7a7dd7f019130ddf75dcf02bdb589cb13cf6f6`.

| Finding | Regression check | Result |
| --- | --- | --- |
| Transfer uses the ruled one-span cells and both orders per ratio with fresh seeds. | Regenerate all 20 kits with pinned gen-legs, run pinned validate-kit including frozen-path hashes, and test alias, extra spans, split pair, missing order, stale ordinal and seed collisions. | PASS |
| Drafts bind one six-leg attempt and require dated authority. | Compare generated kit, queue, item and roster bytes. Run pinned queue validation, halted next and plan for each entry. | PASS |
| Ordinary midnight substitution, date bounds, priority and counted batch holds carry forward. | Structural fixtures cover same-date windows, post-t0 abort, pre-t0 refusal, substitute close-date deduplication, misses, cap, exclusive midnight and DST, the second qualification t0 and the two-stop trigger. The pinned launcher argv and child boundary logic were exercised with fake clocks. | PASS |
| The look fixes the signed daily interval and a closed public success shape. | Audit draft and hash-bound ledger validation, qualification-tail and interval contracts, and synthetic public type/extra-field refusals. The pinned v1 validator refuses the v2 transfer kind in draft and final modes. | PASS for draft checks |
| One synthetic span can run through Check on the pinned runner. | cl-transfer-01-s01 in the mock runner, six legs, exit 0, zero stops. | PASS |
| Generated queue and state sections stay in agreement. | python3.13 -B scripts/gen_state.py --check | PASS |
| Session-end fixture census. | The canonical check and a Python 3.13 retry both returned exit 2 because access to ps was denied. Fixture census is unverified. | FAIL |

This is audit tooling and draft content. The targeted checks used public
source and synthetic inputs. The full project suite was outside this
audit-only verification scope. No phase exit-checklist row closes and
no advisor-visible state changes.

The draft's file names and hash keys follow the page and qualification
look conventions. The audit look proposes a transfer-specific v2 variant,
one private score file plus the two process streams, and fixed failure
status 1. The named v1 validator has no transfer path. No scorer, stage-2
boundary or execution host is admitted here.

NEEDS_SPEC before issue or the terminal look:

- Resolve the final-window case where §3.2's substitute close date is
  later than §3.1's last window t0-date.
- Confirm the transfer v2 schema and dispatch, then fill the owned code
  pins, output contract and execution host under RL-181. Fable's cold pass
  covers the frozen arithmetic, output boundary and once/host checks.

The next exact step is for the lead to take the audit draft and the two
open spec points to Fable. The lead records effective freeze 2 and
scientific registration before issuing any transfer opportunity.
