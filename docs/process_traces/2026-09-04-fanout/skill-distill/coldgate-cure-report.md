# Cold-gate cure report — skill-distill, 2026-09-04

Starting revision: `d4d1507deaee6bc02f348275635c927f83c22e16` on
`feat/2026-09-04-packet-skill-distill`.

Authority: `coldgate-ruling-fable.md`, AMEND rulings Q1, Q3, and Q4. The
AFFIRMed clauses were left unchanged.

## Question → cure → location

| Question | Cure | File:line |
|---|---|---|
| Q1 | Installed the amended two-sentence discovery/lead-replay rule in M0 step 5, immediately after “A red suite is itself the mission”; removed the superseded wording from the addendum so it retains the incident pointer. | `docs/agent_playbook.md:73`; `docs/agent_playbook.md:485` |
| Q3 | Replaced the volatile model-name default with “lieutenant-directed executor lanes remain the standing default (model assignments live in D-129, not here)”. | `docs/orchestration.md:357` |
| Q4 | Replaced “bounded Sol seats” with “bounded executor seats” and “standing Opus-directed default” with “standing lieutenant-directed default”. | `docs/orchestration.md:368`; `docs/orchestration.md:371` |

## Verification

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/private/tmp/skill-distill-cure-pyc python3 -m unittest tests.test_docs_freshness
```

Result (`rc=0`):

```text
.......................
----------------------------------------------------------------------
Ran 23 tests in 0.851s

OK
```

The repository-wide discovery suite was deliberately not run: the task's
PREFLIGHT RULE authorizes only `tests.test_docs_freshness` and test modules
owned by changed files; the ruling's census found no additional owning module.
