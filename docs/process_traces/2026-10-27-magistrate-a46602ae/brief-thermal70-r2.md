# Council seat brief, round 2: Llama-3.3-70B BYTES cell, thermal tail hits (magistrate activation a46602ae, 2026-10-27)

You are one of two blind seats (the other is a different model family; you will not see its answer). Read-only design consult: write NO code into the main repo. Your only output is your report.

## Background
Round 1 brief, Sol report and Opus report (read all three first):
- brief: the "What happened" section below repeats it.
- Sol: branch `codex/by-thermal70-sol` of mpmdw/JouleWise, file `.codex-report/BY-THERMAL70-sol.md` (commit 512425faf).
- Opus: branch `claude/by-thermal70-opus` of mpmdw/JouleWise-data, file `reports/by-thermal70-opus.md` (commit c400efdaf).
Code: read `work/2026-10-23-by-slots-draft` at 991358f73 of mpmdw/JouleWise (the measurement checkout's source tree; file:line refs against it).

BYTES pass-1 session r1-bytes-s5-p1 (Llama-3.3-70B-Instruct-4bit, MLX, M3 Max 128 GB, 140 W adapter) counted (75/75 runs) but its cell `bytes-llama-70b-decode` is below minimum: 2/10 null-contrast quads kept (minimum 5), 9/10 absolute repeats kept. Every dropped unit carries `thermal.os_level_nonzero` (EXCLUDE_MEMBER); b04-b06 also carry charging codes (`battery.member_span`, `battery.accumulator_excursion`, `battery.capture_pair_failed`). No unit carries `thermal.powermetrics_pressure_elevated`. s1-s4 (models up to 32B dense) lost no units.

## New measurement (M1, run by the lead, 2026-10-27, structure only, no energy)
Round 1 both seats said "measure first: locate each in-force nonzero thermal read within the member". The lead ran Opus's appendix-B `thermal_locate.py` unchanged against the measurement checkout's `joulewise.b5.harvest` (`member_spans`, `read_monitor_journal`, `in_force`), the s5-p1 notify-bus journal `custody/hazards/monitor/thermal.jsonl`, and the 50 science bundles in collection order. Output verbatim:

```
thermal reads 3797, malformed 0, largest poll gap 5.3 s
bytes-llama-70b-abs-r07 ['after_end']
bytes-llama-70b-null-b02-a1 ['after_end', 'tail']
bytes-llama-70b-null-b03-b1 ['after_end', 'tail']
bytes-llama-70b-null-b04-b2 ['after_end', 'tail']
bytes-llama-70b-null-b05-a1 ['after_end', 'tail']
bytes-llama-70b-null-b05-a2 ['after_end', 'tail']
bytes-llama-70b-null-b06-a2 ['after_end', 'tail']
bytes-llama-70b-null-b07-a2 ['after_end', 'tail']
bytes-llama-70b-null-b09-a1 ['after_end', 'tail']
bytes-llama-70b-null-b10-b1 ['after_end', 'tail']
episode: length ~10 s, onset 25 s after latest request end, onset in gap
episode: length ~20 s, onset 20 s after latest request end, onset in bytes-llama-70b-null-b02-a1
episode: length ~25 s, onset 15 s after latest request end, onset in bytes-llama-70b-null-b03-b1
episode: length ~25 s, onset 15 s after latest request end, onset in bytes-llama-70b-null-b04-b2
episode: length ~15 s, onset 20 s after latest request end, onset in bytes-llama-70b-null-b05-a1
episode: length ~35 s, onset 10 s after latest request end, onset in bytes-llama-70b-null-b05-a2
episode: length ~25 s, onset 15 s after latest request end, onset in bytes-llama-70b-null-b06-a2
episode: length ~25 s, onset 20 s after latest request end, onset in bytes-llama-70b-null-b07-a2
episode: length ~35 s, onset 10 s after latest request end, onset in bytes-llama-70b-null-b09-a1
episode: length ~30 s, onset 15 s after latest request end, onset in bytes-llama-70b-null-b10-b1
```
Post-request tail (member span end minus request end, `member_spans`) over the 50 science members: min 22.9 s, median 23.4 s, max 23.9 s.

Reading: all ten level-1 episodes are short (10-35 s at the 5 s poll), start 10-25 s after the measured request ends, and fall in the 23 s post-request tail (drift sentinel / post-parse) or on the first read after the span. No hit is before the start, in the idle baseline, or in load. One episode per lost member; the other three members of each lost quad were clean. In Opus's terms H = 0: no pre-member wait (round-1 options 1-5) saves any lost unit. Ten episodes over 50 members; nine dropped units.

## Questions
Q1 (physics). Does a level-1 OS thermal-pressure reading that begins 10-25 s after the measured request ends bear on the decode energy number this cell prints (rails and DC-input decode energy over the decode interval, BAT-2 battery correction; see `joulewise/bytes_analysis.py`), or on the post-request drift sentinel's purpose? Name the mechanism by which it could, if any (e.g. throttling that started during decode but surfaced on the notify bus late; is the notify-bus level known to lag the SoC state, and by how much; would that throttling show in the 10 Hz powermetrics records, which raised no flag?). Say what measurement would settle it, from data already on disk if possible (powermetrics frequency/residency inside decode for lost vs kept members, structural only).

Q2 (pass 1, data already seen). The registered rule stands for s5-p1 (the cell prints unavailable). Under the project rule "if a registered threshold proves too strict, print the registered result and a labelled alternative beside it", specify the labelled alternative exactly (which in-force reads it would count, e.g. reads up to request end + a derived lag bound), whether it is worth printing, and the derivation of any bound it uses.

Q3 (pass 2, prospective; s5-p2 registration is still `draft` and has not run). Options: (a) collection procedure that prevents the post-load episode (e.g. Opus round-1 option 6, a pre-member thermal headroom hold on the battery thermistor or SoC die temperature; or a lower duty cycle via a longer pre-member cooldown) with cost arithmetic and "measure first" where the cooling rate is unknown; (b) a prospective change to the pass-2 thermal exclusion window for this cell, with its effect on pass-1/pass-2 comparability (the paper prints each pass, their mean and difference) and on outcome-informed design; (c) no change, and accept the one-pass fallback (Llama-70B may get no point). Recommend one, or a combination.

Q4. Battery: b04-b06 also carry charging exclusions. Does M1 change round 1's battery conclusions (charging hold saves non-onset members only)? Is there anything about recharge to fix prospectively regardless of thermal?

## Rules
- No silly numbers: every threshold, wait, lag bound or bar you propose carries its derivation from the physics (5 s notify-bus poll, 1 s SMC refresh, 10 Hz powermetrics, about 1 J attribution limit per run, the measured episode lengths and onsets above). If you cannot derive it, say "measure first" and name the measurement.
- No change to registered arithmetic or exclusions for data already seen; a labelled alternative is allowed.
- Decide anything the code and registration determine and list it under "Decisions I made". NEEDS_RULING only for a choice that changes which data count or a printed number.
- Execute where you can (production functions on synthetic production-shaped data).
- Report: one markdown file, first line your exact model id; sections: Findings (file:line), Answers Q1-Q4, Recommendation, Decisions I made, NEEDS_RULING.
