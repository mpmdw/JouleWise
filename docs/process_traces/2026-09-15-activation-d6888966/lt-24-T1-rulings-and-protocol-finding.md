# lt-24 — T1's early return: two adjudication contradictions, and a protocol finding against myself

Written 12:07 PDT 2026-09-15 (clock read).

## T2 landed first — `8f334b8f`, pushed

Astra high, pid 89801, 11:58:59 → 12:04. `status: clean`, D9 complete across the
three operator documents. §3 byte-identical (`71337a83…072b`, seat-verified
before and after); `tests.test_docs_freshness` OK seat-run and lead-run; the one
surviving "rolled back" in the runbook is at `:449` about the OS being rolled
back and is correctly untouched. I read the handback and courier diffs myself:
the new vocabulary — label, retained, UNKNOWN, idempotent — is glossed in plain
words at first use, which is the standard those documents are held to.

It documents an engine that does not exist yet. That is deliberate: the
adjudication ran T1 and T2 in parallel, and the commit message says so.

## T1 returned PRE-WRITE with four blocking flags and changed nothing. All four were right.

That is the early-return protocol doing exactly its job for the fifth time on
this lane. Two flags are contradictions inside the magistrate's adjudication;
two are defects in my brief.

### F1 — `NullAdapter` versus render-only writing plists (contradiction in 34)
D7 requires render-only to construct the machine with "a `NullAdapter` that
raises on any call"; D4 makes the adapter the sole mutation channel for
`launch_dir`; but render-only must WRITE both plists. If `write_plist` is an
adapter method, render-only cannot render.

**Ruled: the NullAdapter nulls the LAUNCHCTL verbs only** — `bootstrap`,
`bootout`, `print` raise; `write_plist` is a filesystem operation and remains
available. The invariant D7 protects is cold gate 28 Q6.3, *render-only never
invokes launchctl*; rendering files is not a launchctl call, render-only writes
to its own `--render-only DIR` and never bootstraps, so it cannot create the
fence-blind state. The seat is told to structure it so "render-only made a
launchctl call" is a TYPE ERROR rather than a test assertion. D4 is unaffected:
still exactly three mutators.

### F2 — D3's deletion rule versus `write_plist` publishing (contradiction in 34)
D3 says "no other function in the module may unlink or overwrite a plist", which
reads as forbidding the atomic `os.replace` publication D5 requires.

**Ruled: D3's proof requirement governs DELETION and RESTORATION, not
publication.** `remove_plist` and `restore_prior` are the only functions that may
unlink or write prior bytes back, and both require the `Absent` token;
`write_plist` is the only function that may publish new bytes; nothing else
touches plist bytes. The invariant D3 protects (I2) is *a file is removed only
after an ABSENT proof for its label* — publication is not removal, and it is
already gated, because PUBLISHED is reachable only through ADMITTED, which has
already required `require_absent` on BOTH labels.

**Both rulings preserve every stated invariant and neither is a design choice I
made freely — in each case only one reading leaves the adjudication coherent.
They are the magistrate's to overrule, and I have flagged them as rulings on ITS
text rather than on mine.**

### F4 — D9 was not T1's, and I gave it to T1 anyway (my defect)
I extracted the adjudication's dictation block programmatically to avoid
paraphrase, which was right, but the block includes D9's documentation clauses
while T1's WRITE_SCOPE correctly excludes those files. The seat saw a dictated
requirement it could not satisfy and stopped rather than write out of scope.
Corrected: D9 is excluded explicitly, it is assigned to T2, and T2 has already
landed it.

### F3 — the protocol finding, and it is against me
> `docs/contracts/bridge_protocol.md` §7: "Before every workspace-write session,
> `scripts/bridge baseline` MUST create an immutable baseline manifest… The
> prompt MUST provide `BASE_HEAD`, `BASELINE_MANIFEST`, and `BASELINE_DIGEST`."

**I have not supplied these for ANY workspace-write seat in this activation** —
not the reconciliation seat, not either fix round, not the FIX-5, render-only,
round-3, edit-1 or stub seats, and not the workspace-write delta auditors. Those
seats did not refuse; this one, at xhigh, read the contract and did. The
omission is mine and it spans the whole session.

Complied for T1: `scripts/bridge baseline --invocation-id lt-t1-txn-20260915-1210`
on a CLEAN tree at `8f334b8f`, manifest
`.codex-bridge/baselines/lt-t1-txn-20260915-1210.json`, digest
`sha256:ce6c1b3cf1522aac52af352c851eb684c977d061322acd3307bb40564553cc3c`,
supplied in the relaunch brief. (An earlier capture at 12:06,
`…20260915-1206`, was taken while T2's work was still dirty; it is superseded
and retained only as a record.)

**For the magistrate, not for me to decide:** whether the earlier non-compliant
sessions need anything — a recorded exception, a retrospective note, or nothing —
and whether the lieutenant's launch procedure should carry the baseline step
permanently. It is a contract requirement I broke unknowingly all day, and every
one of those seats' work is already committed.

## T1b relaunched — pid 91026, 12:06:27

Same model, effort, scope and sandbox; brief
`/tmp/magistrate-d6888966/brief-17-T1b.md` (22 608 bytes) carrying the three
rulings, the protocol anchors, D1–D8 and D10 verbatim with D9 explicitly
excluded, and the unchanged operational requirements — the three-valued stateful
fake launchctl, the product matrix with its 4-tuple and shared fence assertion,
the FIX mapping table, the `control_…` rename, the must-die set, the
`/usr/bin/python3` 3.9.6 constraint, and the lt-21 `reproduce.py` re-run
expecting NO/NO.
