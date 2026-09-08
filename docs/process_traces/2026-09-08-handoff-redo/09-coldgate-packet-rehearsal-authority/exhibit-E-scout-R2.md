**2. High × high: first-night intent exists, but its executable handback and authority conflict.**

Question 3: **observable headless activity is wired and has happened**—heartbeat, tool calls, and an acknowledged launch notice. **The first-night stub is not yet wired on this machine.**

The live sibling plan glob is empty, and the only installed JouleWise LaunchAgent plist is the magistrate. The watchdog observes plans; it does not install night agents or run their stub.

The resume plan says to arm a stub through `NIGHT_HANDBACK.md` (`00-DURABLE-STATE.md:265–266`), but that document still describes **September 3** and its old custody paths (`NIGHT_HANDBACK.md:26–49,54–88`). The relaunch prompt simultaneously directs email-then-arm (`:11–13`) and prohibits altering **plans or launchd configuration except heartbeat/ack** (`:19`). That is a lead-owned authority conflict.

The watchdog’s fake-root examples are stand-down fixtures, not installable nights: the night installer requires a real measurement checkout and matching HEAD (`install_night_agent.sh:80–94`).

Demonstration:

```sh
find "$HOME/night-custody" -mindepth 2 -maxdepth 2 -name night_plan.json -print
ls "$HOME/Library/LaunchAgents/"*joulewise*
nl -ba docs/process/MAGISTRATE_RELAUNCH_PROMPT.md
nl -ba docs/process/NIGHT_HANDBACK.md | sed -n '24,95p'
nl -ba scripts/install_night_agent.sh | sed -n '80,94p'
```

**Minimal cure:** rule narrowly on who may author/install the rehearsal, provide a current dated handback with real checkout pins, and install both night agents. Require the night driver’s own courier evidence. Its launch argv differs from the magistrate’s (`run_night.py:635–665`), so magistrate email success cannot substitute.


