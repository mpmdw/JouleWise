# Record 01 — Ed's headline-experiment rulings (email 22:19 PDT 2026-09-23), and why two activations missed them

Interactive Fable session 02a24110, 2026-09-24 ≈04:30 PDT, prompted by Ed: "did you harvest all the decisions i posted via email? you keep emailing me about the decisions but i already emailed about most of them."

## 1. Audit of every reply Ed sent in the last eight days

Search: Gmail `from:claude2.glaring610@passmail.net OR from:claude.ai.copper531@passmail.net newer_than:8d` (all threads).

| Sent (PDT) | Thread | Ed said | Harvested? |
|---|---|---|---|
| 09-16 09:25 | `1a0a99fa2717d749` | "i did /exit" | yes (0bd12d79 armed on it) |
| 09-19 10:57 | `1a0ba221b52d3e38` | full authorization for (c) | yes, but only by the NEXT activation (a743be05 record 01); d0b83820 stood down recording "still pending" |
| 09-23 01:06 | `1a0ccfe8cb5c59ee` | D-182 addendum YES; block two (c); wait on major decisions for the new-model reads | yes (7a0f14bd; PR #384) |
| 09-23 22:19 | `1a0d12f08db9ef04` (reply to d8cc9c0a's LAUNCH email, not to the four-decisions email) | E1–E4 answers, verbatim below | **NO.** d8cc9c0a closed at 00:45 PDT 09-24 saying "your four decisions still open" (2.5 h after the reply). a65fb4fa then re-asked the same questions as "five decisions" at 02:39 PDT (message `1a0d2c87919abfe3`). |

## 2. Ed's words, verbatim (message `1a0d1db347b562c4`, 2026-09-24T05:19:53Z = 22:19:53 PDT 09-23)

> re the 4 decisions: yeah, why not publish it?
>
> 2. yes if you fable, opus 5.5 and astra all agree, then go ahead i trust the council
>
> 3 and 4, your decisions towards the best practices are authorized, just get at least opus 5.5 and astra to rule on it, with a fable 5.1 too at the end.

## 3. Reading, mapped to the questions as sent (email `1a0d069e15a52ba9`, 15:36 PDT 09-23)

- **E1 (publish the MATH problem text): publish.** "yeah, why not publish it?" reads as a yes to publishing. The recommendation in the email was the opposite (ids and hashes only, because of the AoPS copyright notice). Publication is hard to reverse, so the magistrate commits no problem text to a public branch until Ed confirms in one word that "publish" is what he meant; everything else in the lane proceeds.
- **E2 (adopt the AP-5M analysis-plan change): yes, conditional on a three-seat council.** Adopt when Fable 5.1, Opus 5.5 and Astra all agree on the text. Ed: "i trust the council."
- **E3 (decoding in thinking mode) and E4 (problems per level): delegated.** The magistrate decides toward best practice, provided Opus 5.5 and Astra both rule on it and a Fable 5.1 pass comes at the end. The recommendations were (b) seeded sampling with (a) greedy as the pre-registered fallback, and 128 per level after a bench pilot confirms the planning rates.
- **E5 / O-21 (instrument floor on top of the statistical test), asked only in the 02:39 PDT re-send:** still unanswered by Ed. Ed's E3/E4 sentence ("your decisions towards the best practices are authorized") does not cover it: the cold gate reserved O-21 to Ed explicitly. Ask Ed once, in the interactive session, not by another email.

## 4. Why the 22:19 reply was missed (mechanism, so it stops)

RUN_STATE's successor pointer said: "Read Ed's reply to Gmail `1a0d069e15a52ba9`". Ed replied on `1a0d12f08db9ef04` instead (the launch email is the newest mail in his inbox, so that is where a reply lands). Both activations looked at one thread id and found nothing. The 09-19 miss had the same shape: the reply was unread for ten hours while the session that asked stood down "pending".

Fix, directed by Ed in this session (2026-09-24, interactive) and installed in `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` (the watchdog re-reads the template at every launch, `scripts/magistrate_watchdog.py` `render_prompt`): at launch before the launch email, and before every work slice, the magistrate searches Gmail for unread messages FROM Ed's address across all threads, transcribes each one verbatim into a numbered activation record, applies it, marks it read only after the record is committed, and never re-asks a question such a message answers. The four Ed messages above are marked read by this session after this record is committed, so the next activation starts from an empty queue.

## 5. What the resident activation (7370d0fb, launched 03:46 PDT) must do

Directive issue opened by this session (label `directive`, author mpmdw) carries §2 and §3. On reading it: apply E2–E4 as ruled (three-seat council for E2; Opus 5.5 + Astra rulings + Fable 5.1 final pass for E3/E4), hold E1's text commit for Ed's one-word confirmation, hold O-21 for Ed's answer, and send Ed no further email that asks any of E1–E4 again.

## 6. Ed's answers in the interactive session (≈04:45 PDT 2026-09-24), asked in one batch per his instruction "while im at the machine any other decisions are posed to me"

- **E1 / O-20: ids and hashes only.** Ed: "im ok with 1" (option 1 = commit only problem ids and sha256 fingerprints; the MATH text stays in a local hash-bound custody path). The 22:19 "why not publish it?" is superseded. No problem text is committed.
- **O-21: YES.** A claimed joules-per-correct-answer difference must also exceed the instrument's detection floor F (`|estimate| > F`, single-count discipline from `detection_floor.md`), on top of Holm and the anchor-widened interval test. AP-5M registers the estimate-level floor check.
- **E8 (branch protection on main): add the missing required checks now.** Ed's condition, verbatim: "just make sure all checks in place are sensible for science reasons, my objective with the orchestration and multi agent communication is preventing bad science, not progress on the paper when models agree, so just be sensible...".
- **Standing principle from that sentence (binding on every gate design):** the orchestration and the cross-model machinery exist to PREVENT BAD SCIENCE. Agreement among models is not progress; a gate earns its place by catching bad science, and a gate that only slows the paper without protecting the science is not sensible.

Applied by this session: issue #405 comment with E1 and O-21; required status checks on `main` extended (see §7); the three-seat council for E2 and the Opus 5.5 + Astra + Fable rulings for E3/E4 remain the resident magistrate's work.
