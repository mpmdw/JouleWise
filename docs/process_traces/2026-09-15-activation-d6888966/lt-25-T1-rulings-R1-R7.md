# lt-25 — T1's five early returns, seven rulings, and a brief-assembly error of mine

Written 12:30 PDT 2026-09-15 (clock read). Branch head at T1e launch:
`6dc86461`.

## The pattern worth recording

T1 returned `NEEDS_RULING` **five times** before writing the engine, and was
right five times. Three were contradictions inside the magistrate's
adjudication; two were defects in my briefs. No seat on this lane has yet
guessed at a conflict, and the two most valuable findings of the whole
transactional lane so far came from a seat refusing to start.

**Two of the five were the same question asked twice, and that is my fault.** I
rebuilt T1's brief from the original each time I added a ruling, instead of
accumulating, so the D3-versus-`write_plist` ruling I issued to T1b vanished from
T1c's and T1d's briefs and the seat had to raise it again. Cured: `lt-20-T1e`'s
brief carries **R1..R7 in one cumulative block**, stated as standing rulings, with
that failure named in the brief so the seat knows it was not being ignored.

## The seven standing rulings

**R1 — `NullAdapter` nulls the LAUNCHCTL verbs only.** D7's "raises on any call"
cannot coexist with render-only writing plists. `bootstrap`/`bootout`/`print`
raise; `write_plist` stays available. The protected invariant is cold gate 28
Q6.3: render-only never invokes launchctl. Rendering files is not a launchctl
call.

**R2 — D3's proof requirement governs DELETION and RESTORATION, not
PUBLICATION.** `remove_plist`/`restore_prior` are the only functions that may
unlink or write prior bytes back, both demanding the `Absent` token;
`write_plist` is the authorised publisher via `os.replace` and needs no token;
nothing else touches plist bytes. I2 is *a file is REMOVED only after an ABSENT
proof* — publication is not removal, and it is already gated because PUBLISHED
is reachable only through ADMITTED, which required `require_absent` on both
labels.

**R3 — D9 is not T1's.** I pasted the dictation block whole, including its
documentation clauses, while T1's scope correctly excluded those files. T2 had
already landed D9 at `8f334b8f`.

**R4 — the proof obligation is a property of the TARGET DIRECTORY.** The sharpest
catch of the lane: D6's STAGED/PUBLISHED teardown demands proofs, R1 forbids
render-only from calling `print`, so a render-only failure after first
publication could obtain no proof and could not clean up. Ruled: type the target
(`LaunchdTarget` vs `RenderTarget`); only `LaunchdTarget` deletions and
restorations require the token; `RenderTarget` operations need no proof and
cannot reach launchctl; neither type can be constructed pointing at the other's
directory, pinned by a test. The reason is physical: `require_absent` exists
because the fence reads `<label>.plist` in the **launchd** directory, and
`--render-only DIR` is not that directory — no job is ever loaded from it and the
fence never reads it, so a liveness query about it would be meaningless, not
merely unavailable.

**R5 — D1's `-m` entrypoint stands; D7's isolation becomes a pinned invariant.**
Bench-confirmed: `joulewise/__init__.py` imports `joulewise.schemas` plus three
project modules, so `-m joulewise.night_agent_install` cannot satisfy D7's
literal "no project imports beyond the module". It holds today on 3.9.6; nothing
stopped a future edit from breaking it silently, and **a rehearsal night was
already lost on 2026-09-11** to launchd's 3.9 meeting a newer construct. Landed
at `6dc86461`: a guard asserting that importing `joulewise` under
`/usr/bin/python3` needs nothing outside the stdlib and the package. Plus an
executed stripped-environment uninstall test. **Flagged to the magistrate:**
moving the engine out of the package, or exec'ing by path instead of `-m`, would
give literal isolation but changes D1 — its call, not mine.

**R6 — `reproduce.py`: move the CLOCK READ, keep the PREDICATE.** The seat found
that the supplied audit script hooks `rm` and reads the clock **during backup
cleanup** — a directory D5 abolishes — and then classifies rc 0 with loaded
labels as class 1, which would condemn the very control D10 mandates. Ruled per
cold gate 28 Q1 and D10, and restated in the magistrate's own direction for this
lane: class 1's clock read is the one taken **after the last LAUNCHD mutation**;
sidecar or temp cleanup is not launchd state. The predicate, comparison and
reporting are untouched; only the read moves, to immediately after the final
`bootstrap`. The `control_…` case must pass and must not be reported as class 1.

**R7 — bridge protocol anchors supplied** (see lt-24 and below).

## Protocol compliance, continued

`bridge scope-check` returned `ATTRIBUTION_INDETERMINATE` for T1c because **no
governing lease matched the invocation** — `bridge lease-list` showed **zero
leases in the repository**. So alongside the §7 baseline omission recorded in
lt-24, I have been launching write seats all session without leases too.
Acquired for this lane: `lease-f4382692e249483db223325dfa87bde1`, invocation
`lt-t1-txn-20260915-1216`, access `write`, owner kind `codex-cli`, over the four
T1 paths, expiring 21:15Z. Baselines re-captured on each clean tree
(`…-1218`, `…-1229`).

**Both omissions are the lieutenant's and both span the whole activation.** What,
if anything, is owed for the earlier non-compliant sessions — all of whose work
is already committed — is the magistrate's to decide, as is whether the
lieutenant's launch procedure should permanently carry `lease-acquire` +
`baseline` before every workspace-write seat. I am not self-granting an
exception; I am recording that I broke a tracked contract unknowingly and have
complied from here.

## Landed so far on `feat/2026-09-15-install-windows-transactional`

| Sha | What |
|---|---|
| `8f334b8f` | T2: D9 operator docs (§3 byte-identical; docs_freshness OK) |
| `e867dee9` | the three-valued stateful fake launchctl — the instrument before the thing it measures; mutators model return code and effect INDEPENDENTLY, which is precisely the trust four rounds placed wrongly |
| `6dc86461` | the system-interpreter import guard (R5) |

T1e (pid 96853, 12:29:13) now builds the engine itself with every question
answered.
