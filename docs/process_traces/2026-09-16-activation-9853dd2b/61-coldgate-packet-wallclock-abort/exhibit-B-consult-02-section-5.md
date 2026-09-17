# Exhibit B — design consult record 02 (2026-09-16, Astra xhigh) §5 co-design with the sibling lanes (verbatim lines 96–107)

## 5. Co-design with the sibling lanes

**Neither deadline is redundant.** The custody deadline supplies an early, specific refusal before reservation writes. The driver deadline bounds other stalls and failures of that mechanism. Killing the chain at the window end cannot establish that no reservation intent was written.

For `NIGHT-STALL-WALLCLOCK-ABORT-01`, I recommend initiating termination at the exclusive window end, with separately bounded shutdown grace. A pre-termination grace permits acquisition beyond the declared window. Check the deadline independently of census cadence, including around potentially blocking census probes. Existing termination waits can consume up to 60 seconds. ([Driver loop](/Users/edr/code/JouleWise/scripts/run_night.py:483), [termination](/Users/edr/code/JouleWise/scripts/run_night.py:358))

Termination proof must cover the custody worker too. The current helper waits for the direct child; that alone does not demonstrate that every process-group member has disappeared. Courier launch must retain its existing “termination proven” condition.

For `DRIVER-REFUSAL-COLLISION-01`, use immutable distinct refusal documents with collision-resistant names or exclusive-create sequence allocation. **Do not append another JSON object to `refusal.json`**, and do not assume second-resolution epoch names are unique. Preserve both causes, reference their actual paths in the result/artifact inventory, and have the courier read them. The current artifact list hardcodes only `refusal.json`. ([Artifact inventory](/Users/edr/code/JouleWise/scripts/run_night.py:531))

Also update the sibling’s “daily firing” wording: current dead-man timing is already derived from plan completion plus grace, rounded to a minute. ([Current calculation](/Users/edr/code/JouleWise/scripts/run_night.py:961))

