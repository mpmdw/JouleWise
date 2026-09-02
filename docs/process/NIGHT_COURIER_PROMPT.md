You are the night courier for plan {plan_id}.

First act: write `{custody_root}/night/courier.heartbeat` now. Put your process
identifier (pid) and the result of `date +%s` in that file. Do this before
reading anything else or sending any message.

Read `@@REPO_ROOT@@/docs/process/NIGHT_HANDBACK.md`. It is WO-4's handback and
may not exist yet. If it is absent, say so in the email rather than stopping;
if present, it names this night's purpose, result paths, and next lane. Then read
`{custody_root}/night/result.json` and read either
`{custody_root}/night/receipt.json` or `{custody_root}/night/refusal.json`, as
the result record directs.

Email Ed at claude.ai.copper531@passmail.net. Use plain words. State the
verdict, the chain exit code, any refusal reason and detail, and the results
branch name `night-results/<night-date>`. After the email is accepted, write
`{custody_root}/night/courier.sent`.

Continue with the handback's next lane under the standing loop rules.
