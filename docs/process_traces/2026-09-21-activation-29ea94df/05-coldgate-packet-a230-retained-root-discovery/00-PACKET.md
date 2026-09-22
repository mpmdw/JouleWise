# Cold-gate packet — evidence-night entry, first live use: (1) which night records classify a discovered custody root as retained; (2) lane A230's runbook-versus-handback contradiction; (3) whether the magistrate's own idle MCP helper processes are FOREIGN to the pre-arm census (rule 11 triggers: a proposed process rule, and a reinterpretation of a prior verdict)

Assembled 2026-09-21 22:05 PDT by the resident magistrate (activation 29ea94df). Mechanically assembled: exhibits A–C are verbatim `git show <rev>:<path> | sed -n` extracts of main `9e0a4995`; exhibit D is verbatim command output captured this session; the magistrate wrote only this file. Nothing is armed on this machine. No measurement is running.

## What happened

The tracked entry point `python -m joulewise.evidence_night` (contract: Exhibit B1) was used live for the first time tonight. `prepare` succeeded (candidate `qpe01-pilot-n1-20260921-2238`, H `7e35d16a`). `check` refused with exactly two failing checks, `retained_roots` and `census`, and passed the other seven (Exhibit D1, D2).

**Retained roots.** `check` item 4 (Exhibit B1 lines 203–208; code Exhibit A1) inventories every `/Users/edr/night-custody/*/night_plan.json` and classifies a root as `retained` only if `night/courier.sent` or `night/result.json` exists; otherwise `UNKNOWN`, which refuses. Four roots were found (Exhibit D2, D7). Three carry both markers. The 2026-09-16 root `d079-epoch-25g83-derivation-n1-20260916` carries neither: its night fired at t0 (`chain.started` 09:45:02), the driver wrote `refusal.json` (`night_chain_alive`, 13:20), and the chain exited with signal 15 at 20:52 (`chain.exited`) when the machine was shut down for a move (Exhibit D3, D4). No night agents are installed (D5). Its 20-file harvest archive verifies 20/20 against both the archive copy and the live root (D6). The handback's dated addendum for that night says the clone and the night root are RETAINED because a ledger session opened (Exhibit C2). Consult 18, which the contract cites as authority, says discovery must "establish harvest/ownership/completion; unknown or active ownership stops. Never delete or hide roots to pass discovery" (Exhibit B2). The watchdog's own span rules (Exhibit A3) treat `chain.started` without `chain.exited` as active and `courier.sent` as complete; the installer's admission check (Exhibit A4, A5) treats `receipt.json`, `result.json`, `chain.started`, `chain.exited`, `courier.json`, `courier.sent` and every `refusal*.json` as night records that refuse re-admission of a plan into a used root.

**Lane A230** (Exhibit C3) registered, before tonight, that runbook §0.7 ("expect no output" from the discovery glob, Exhibit C1) and the handback's retention rule (Exhibit C2) contradict each other for every retained root, and named two reconciliations for "the cold gate or Ed".

**Census.** `check` item 5 (Exhibit A9; code A7, A8) refuses on ANY foreign PID. Tonight's foreign set contains two interactive Claude sessions belonging to the owner (roots 67916 and 68088, with their Codex helpers) AND the two Codex MCP server processes (75861, 75865) that the magistrate's own session spawned at launch: they are descendants of the magistrate's own session root 75838 but not in the caller's ancestor chain, and `classify_arm_census` (A7) exempts only the ancestor chain for a real plan (`idle_exemption` applies to `REHEARSAL_STUB` only), so they are FOREIGN (Exhibit D8). The prior real arm (2026-09-19, bench script set) observed the identical shape — foreign set = its own idle Codex MCP helpers — labelled it "diagnostic only; existing all-agents-closed rule still applies" and proceeded (Exhibit D9). The tracked check's own instruction text says "all owned agents, MCP children and helpers must be gone before REQUEST" (A8), i.e. before the exit deadline, not before publication.

The owner's interactive sessions are outside every question here: the census will and should refuse while they are alive.

The lead's labeled disposition (argument, not evidence): Q1 option (a); Q2 option (ii); Q3 option (a).

## Q1 — which night records classify a discovered custody root as retained (rule one option or write a better one)

- (a) Broaden item 4's marker set to the terminal driver records the installer already treats as night records: a root is `retained` when `night/` holds a regular `courier.sent`, `result.json`, `chain.exited`, or any file matched by `run_night._refusal_paths` (`refusal.json`, `refusal-N.json`, `calibration-refusal.json`, `calibration-refusal.json.*.json`). A root whose `night/chain.started` exists without `chain.exited` is `ACTIVE` and refuses; a root with a plan and none of these is `UNKNOWN` and refuses. The contract sentence at B1 lines 205–206 is rewritten to name that set. The 2026-09-16 root then classifies as `retained` (it has `refusal.json` and `chain.exited`).
- (b) Keep the marker set; retire the 2026-09-16 root out of `/Users/edr/night-custody` into `/Users/edr/night-archive` (its harvest archive already verifies 20/20) so discovery no longer sees it. Note this contradicts the handback's RETAINED ruling for that root (C2) unless Q2 is decided the other way, and consult 18's "never delete or hide roots to pass discovery" (B2).
- (c) Other, with the same burden: the ruled rule must classify every root in D7 without a lead judgment call, must refuse a root whose chain is open, and must not require moving or editing any night record.

Deliver: the ruled option; the exact marker set and classification labels; the exact replacement sentence(s) for B1 lines 205–206; whether the change is a contract change that pairs refuters; the reason with the deciding exhibit.

## Q2 — lane A230: which text holds

Runbook §0.7 (C1) says the discovery glob must print nothing before arming; the handback (C2) rules that a night root that opened a ledger session is RETAINED, which keeps it discoverable forever. Options named by the lane (C3):

- (i) retained roots move out of discovery to a retained-custody location that is not `/Users/edr/night-custody/<plan_id>`, with the handback's retention wording and the inventory updated;
- (ii) §0.7's precondition is restated as "no plan whose span is active or whose agents are installed", the executable check the watchdog already applies (A3) and the tracked check item 0 plus the Q1 classification implement; the runbook and the handback then say the same thing.
- (iii) Other.

Deliver: the ruled option, or REFUSE with the exact defect if this is a process-rule question the packet does not give you authority to decide; if ruled, the exact replacement text for the §0.7 check paragraph (C1, from "Check it, and expect no output" to the end of the fenced block).

## Q3 — the magistrate's own idle Codex MCP helper processes under the tracked check

Under item 5 as written (A9, A8), the magistrate's own idle MCP helpers (D8) are FOREIGN and the tracked check can never pass for a magistrate launched with an MCP server, although the prior real arm proceeded with the same processes alive (D9) and the check's own instruction expects owned helpers to leave before REQUEST, not before publication.

- (a) Procedure, no code change: the magistrate terminates its own MCP helper processes (descendants of its own session root that are not in its ancestor chain) before running `check`, and the handbook records that step; the classifier and the refusal stand unchanged.
- (b) Code: for a non-rehearsal plan, descendants of the caller's own session root (A7 `own_root`) that carry no workload are classed owned, not foreign, and are listed under the departure instruction; foreign remains every other session. This is a change to `arm_census.classify_arm_census` or to `census_check`, and it is measurement-adjacent (the same classifier the night driver's admission uses).
- (c) Other.

Deliver: the ruled option; if (a), the exact handbook step text; if (b), the exact classification rule and where it lives; the reason with the deciding exhibit.

## Q4 — regression specification for the ruled cures

For the Q1 cure (and the Q3 cure if it is code): the defect-shaped regressions a seat must add beside Exhibit A6, each with what correct code produces, what the assertion accepts, and the counterfactual mutation it kills (for example: a root with only `refusal.json` classed UNKNOWN; a root with `chain.started` and no `chain.exited` classed retained; the marker list reverted to two entries). State the acceptance command (single module `python3 -B -m unittest tests.test_evidence_night`).

## Constraints on the judge

Read-only. Nothing is armed; no load constraint applies beyond ordinary courtesy (no suite-wide runs; the single module above at most once, about 60 s). Probes allowed: `git show 9e0a4995:<path>`, `grep`/`rg`, `sed -n`, `ls`/`cat`/`shasum` under `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916` and `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916` (read only), single Python snippets under `/tmp`. Do not edit any tracked file other than writing the ruling. Never touch `/Users/edr/code/JouleWise` (canonical root), any `/Users/edr/JouleWise-measurement-*` directory, `/Users/edr/night-plan-staging`, `/Users/edr/night-custody/magistrate`, or `~/Library/LaunchAgents`. Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure (auto-loaded files, charter digest expected/observed/method); Packet hygiene; Q1; Q2; Q3; Q4; Executed probes (commands and outputs). Verdict per question AFFIRM / REJECT / REFUSE against the lead's labeled disposition, findings tiered BLOCKER / MATERIAL / NIT. Plain words; define each term at first use. Under 14 KB.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
431832b28aab2b098d8e059eb458e291041605cb2f62d8efc2781cc36bc2709c  exhibit-A-code-at-main.md
a0ce46cc274e71ffaf6e230343d9c095439dc8d74ebe7837454542bb54878704  exhibit-B-contract.md
7a3d1df5d3fa382af5ebf887ec9dfe143fda19360389485c5f3c9cd8ec3ad71c  exhibit-C-a230-texts.md
ac78f64276c7786feb6198ca9aad3f50d41ba56cb4fec87a0375a0e9d339095f  exhibit-D-executed-evidence.md
```
