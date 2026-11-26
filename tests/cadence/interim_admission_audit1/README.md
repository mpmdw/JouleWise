# Audit 1 fixture: a pinned writer's journals at its registered deadline

`deadline.json.gz` holds the four bundle journals (`config.json`, `events.jsonl`, `outputs/align_thermal.jsonl`,
`outputs/align_turns.jsonl`) that the pinned writers serialize when the episode deadman expires during the one turn.
Its turn carries `finish_reason` and `stop_condition` `episode.deadman` and the flag `episode.deadman:0`.

`generate_deadline.py` is `tests/cadence/interim_admission/freeze_journals.py` (frozen, unedited) with two
substitutions, so no frozen file changes: an `EpisodeDeadman` is attached to the endpoint before its one `chat` call,
and the fake clock sleeps one second past the deadman's budget instead of 0.4 s (profile `deadline`). Run as

    python3 -I -B generate_deadline.py PIN PINNED_SOURCE_TREE OUT_DIR deadline

at each of `b4b6aeb19`, `2d347f721` and `6e9d42f1d`; all three produce byte-identical
`<pin>-deadline.json.gz` (sha256 `d7dabe9ef9c16972f2b33f625229abd5af796a69d68cdbfec5f3d44e35a7418a`). Only a fake clock,
tokenizer, token stream and sensor reader are used; nothing here is a measurement.
