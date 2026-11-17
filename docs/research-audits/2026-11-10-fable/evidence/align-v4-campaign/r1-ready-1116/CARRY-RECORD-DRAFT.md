# Draft lead carry record / RUN_STATE 329 correction

DRAFT FOR LEAD ADOPTION, no RUN_STATE write. Sources: RL-168 §3,
RL-170 §2/§4, RL-172b §2 and RL-172c; source census at P.

Suggested lead record:

> The counted Part C accepted in item 329(3), executed at `c3f4bacd8`
> (item 328), carries to `b2e01464d6d4fbf2901ff4d4154df9455104a12a`
> under RL-170, RL-172b and RL-172c. The ten condition-13 files are
> unchanged. Over those ten plus the seven Part C paths, the only diff
> is #774's added `v4_desk_seal.py` entry in `v4_registration.py`'s
> EXECUTED_CLOSURE. That “one line” describes the path census only;
> it does not describe every changed module Part C imports. The full
> imported-module accounting is below. A new standing F0 is not a
> condition of the carry or R1. Item 346 was reissued at P.

| Imported module / data | What Part C reaches | Changed scope and ruled reason carry holds |
|---|---|---|
| `scripts/align_v4_session.py`, via follow-up kit | `weight_digest_preflight`, `runtime_stack_preflight`, `pilot.h.align_unit_id` | #774 changes `powermode_desk_check` and `desk`; no reached function changed. RL-168 §3 names this edge. |
| `scripts/align_pilot_session.py`, through v4 session | `h.align_unit_id` through the existing `bytes_h_session` binding | #774 changes `desk` and adds `_desk`, neither called by Part C. The definitions' defaults read existing `subprocess.run`, `KIT`, `SCHEMA`. RL-172b makes the import-time definition-binding exception exact. |
| `scripts/align_v4_kit.py`, through v4 session and lazy driver imports | Follow-up preflights reach `valid_digest`, module default uses `KIT`; driver imports `DEADMAN_FACTOR`, `L1_MARGIN_S`, `MEMBER_CAP_S`, `l1_t_dead`, `w1_inter_member_idle_s`, `r1_g0_timeout_s`; template name `W1_PLAN_TEMPLATE` and their unchanged dependencies | #790 changes admission/receipt functions, not these definitions. RL-170's own read counts 20 reached definitions, none changed; only added top-level import is `os`. The 20-definition count is the research lead's census, not a newly executed dynamic trace by this worker. |
| `joulewise/align/apple/v4_registration.py` | Source/identity checks and existing condition-13 tuple | One EXECUTED_CLOSURE entry for desk seal; Part C does not import/call the new desk seal. Ten source bytes unchanged. |
| `night_plan.template.json` and `identity_pins.json` | Driver reads template `members` and member configs; stack preflight reads `runtime_versions` | #790 removes only `g0_cap_receipt` template slot and moves tree hash; fields reached here unchanged (RL-170 §2). |
| `scripts/align_v4_w1_synthetic.py` | Nothing in production R1 or Part C | #798 changes synthetic desk oracle only, with strict synthetic caller boundary; RL-172b confirms no reached production/import effect. |

This transcribes the already cold-admitted import/call reasons. The fresh
source census independently checked the ten/17 path diffs and hashes;
it did not rerun the earlier four-child dynamic trace. The lead adopts
the combined record, rather than interpreting “one line” as a complete
import census.

The RL-170 carried text notes are prepared here too:

- Note 3 is explicitly **not gating**: next PR opening
  `docs/align/r1_runtime_contract.md` removes “without a receipt” from
  its X-G-not-measured sentence, retaining “that alone is never a
  refusal”. No protected pin or registration text is changed here.
- Note 4: the blind amendment names PR #790 merge P as the point where
  the kit ceased honouring the R10-2(a) receipt. AMENDMENT-R1-DRAFT
  supplies that sentence. No DEVIATIONS row is owed just for that
  retirement. The registered protocol's stale route is replaced only
  in the actual authorized amendment.

RL-159's earlier two text items (synthetic-pair comment; changed-pick
budget-procedure scope) were included in #790 per its reviewed PR body.
They are distinct from RL-170's note 3/4 and not new native gates.
