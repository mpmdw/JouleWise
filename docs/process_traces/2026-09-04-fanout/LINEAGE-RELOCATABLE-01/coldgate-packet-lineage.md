# Cold-gate packet — LINEAGE-RELOCATABLE-01 relocation proof (2026-09-04)

Mechanically assembled for an independent cold ruling on the relocation landing.
The source tree is pinned to branch `feat/2026-09-04-packet-lineage` at commit
`b420a45a58ecba69b8fb7a121eb27b864ba39325`. The packet and its manifest do
not authorize a merge. They present the magistrate's NR-1 through NR-3 ruling,
the complete lane history, the changed code, and the changed tests for a judge
to verify read-only and re-execute at that head.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Convening trigger and controlling authority

The ruling is copied verbatim in
`packet-exhibits/authority/01-magistrate-rulings.md`. Its controlling section
is lines 29-33 at the pinned head. It adopts:

- NR-1: an explicit non-authoritative relocation carrier over immutable issued
  bytes;
- NR-2: explicit post-hoc relocation only, with live launch and campaign replay
  remaining absolute-path and refusing relocation; and
- NR-3: the existing artifact-specific refusal codes, with every newly accepted
  relocated state proven same-byte/same-pack before merge, including an
  end-to-end moved-source regression and the six named refusal legs.

This sitting is mandatory both because merge is irreversible under charter §3
item 3 (`docs/process/coldgate_charter.md:29-39`) and because the magistrate
expressly made the NR-3 proof a pre-merge cold gate. The ruling is authority;
the seat and review reports are evidence, not authority.

## 3. Frozen object and exhibit map

All exhibit paths below are relative to this packet. Every exhibit is a
complete byte-for-byte copy, not an excerpt. Code and test line citations are
therefore stable against the pinned head.

| Exhibit | Source at `b420a45a58ecba69b8fb7a121eb27b864ba39325` | Relevant lines / role |
|---|---|---|
| A0 | `docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md` | `packet-exhibits/authority/01-magistrate-rulings.md:29-33`; NR-1..NR-3 authority |
| R1 | lane `01-sol-report.md` | `packet-exhibits/reports/01-sol-report.md:138-259`; forcing problem, design seat, proposed proof |
| R2 | lane `02-refuter-merge-base.md` | `packet-exhibits/reports/02-refuter-merge-base.md:110-153`; initial authority blocker |
| R3 | lane `03-sol-fix-round-1-report.md` | `packet-exhibits/reports/03-sol-fix-round-1-report.md:103-140`; proposed ruling cure |
| R4 | lane `04-sol-fix-round-1-report.md` | `packet-exhibits/reports/04-sol-fix-round-1-report.md:140-211`; implementation report and NR-3 proof |
| R5 | lane `05-delta-reaudit-round-1.md` | `packet-exhibits/reports/05-delta-reaudit-round-1.md:102-129`; DR-01 direct-API bypass finding |
| R6 | lane `06-sol-fix-round-2-report.md` | `packet-exhibits/reports/06-sol-fix-round-2-report.md:104-124`; DR-01 cure |
| C1 | `joulewise/arm_readiness.py` | `packet-exhibits/code/joulewise/arm_readiness.py`; carrier and authenticators |
| C2 | `scripts/launch_window.py` | `packet-exhibits/code/scripts/launch_window.py`; live launcher refusal |
| T1 | `tests/test_arm_readiness.py` | `packet-exhibits/code/tests/test_arm_readiness.py`; moved-source and refusal proofs |
| T2 | `tests/test_launch_window.py` | `packet-exhibits/code/tests/test_launch_window.py`; live launcher refusal proof |

No state document, run report, council log, private doctrine file, or session
memory is part of the read set. The only narrative evidence is R1-R6, which is
included to expose the full proposal, refutation, fix, and delta history. Grade
the claims below against A0 and primary exhibits C1-C2/T1-T2.

## 4. Q-NR1 — authority of the carrier

Answer each part AFFIRM, REJECT, or REFUSE.

1. Is the carrier non-authoritative over immutable issued bytes? In C1, inspect
   the frozen target-only context at lines 729-750, canonical exact-key loader
   and relative/no-symlink target checks at 9122-9255, refusal of a raw carrier
   at the public direct-lineage API at 10279-10308, and locator authentication
   before the private context is admitted at 10958-11034. Inspect also the
   returned deep copy of the original lineage at 10702-10722. AFFIRM only if
   the carrier selects read targets without rewriting an issued reference or
   making its own bytes evidence authority.
2. Does T1 bite that property? The positive at 1806-1827 requires the original
   absolute route to refuse, then requires explicit relocation to return the
   exact issued lineage object, its issued consumption digest, and a freshly
   recomputed committed-pack digest. The locator-binding tests at 1902-1924
   require an incorrect carrier digest to refuse and require direct raw-carrier
   use to refuse. AFFIRM only if those assertions would fail under an
   authoritative or reference-rewriting carrier.

State any carrier field or code path that can authorize changed evidence bytes.
Do not treat the carrier's own new location metadata as an issued artifact.

## 5. Q-NR2 — post-hoc boundary and ruled refusal legs

Answer each part AFFIRM, REJECT, or REFUSE.

1. **Live campaign replay:** C1 lines 10844-10856 rejects every supplied
   relocation carrier with `launch_binding_mismatch`; T1 lines 1829-1838 pins
   both the code and the `launch-lineage relocation is post-hoc only` detail.
2. **Live launch:** C2 lines 244-249 rejects the option before assembling launch
   inputs, and lines 280-285 does the same at the lifecycle entry point; T2
   lines 82-90 pins the launch refusal and existing code.
3. **Tamper:** T1 lines 1840-1843 changes copied `window.env` bytes and requires
   `launch_binding_mismatch`.
4. **Committed-pack-change:** T1 lines 1845-1859 commits different pack bytes in
   the clone and requires `launch_binding_mismatch` plus the authenticated-pack
   byte-difference detail.
5. **Repository-relative-move:** T1 lines 1861-1879 commits the same pack at a
   different repository suffix, changes only the carrier target, and requires
   `launch_binding_mismatch` plus the relative-location detail.
6. **Swapped-chain:** T1 lines 1881-1895 swaps start and settle primaries and
   regenerates only their filename sidecars; it requires the preserved
   `launch_consumption_invalid` code.
7. **Traversal:** T1 lines 1897-1900 supplies `../custody` and requires the
   preserved `launch_binding_mismatch` code.
8. **Symbolic-link:** T1 lines 1926-1930 replaces the selected window-plan
   directory with a symbolic link and requires the preserved
   `launch_binding_mismatch` code.

For any REJECT, give the exact input that passed or the exact expected/observed
reason-code difference. A refusal that occurs for an earlier authenticated
binding is still a valid refusal, but it must preserve the artifact-specific
code A0 requires.

## 6. Q-NR3 — every newly accepted state is same-byte/same-pack

Answer AFFIRM only if both the executed positive and the acceptance-path
inspection establish the proposition; otherwise REJECT or REFUSE and identify
the minimum counterexample or missing proof.

The implementation seat's proof is R4 lines 177-195. Re-execute it rather than
accepting the report. In primary evidence T1:

- lines 1499-1728 construct an issued consumption → start → settle lineage by
  calling the production consumption and lifecycle writers;
- lines 1730-1786 clone the Git repository with `--no-local`, copy custody,
  window-plan, and run inputs, then delete the original repository, custody,
  and arm-context roots; and
- lines 1806-1827 first prove the original absolute route refuses, then accept
  only with the explicit carrier and assert exact lineage equality, exact
  consumption-digest equality, and equality to a fresh committed-tree digest
  of the selected clone pack.

Inspect the acceptance route in C1 as well: arm bytes and pack identity bind at
9511-9554; consumption bytes bind at 10330-10353; the fixed manifest location
and manifest/environment/chain bytes bind at 10405-10511; fixed lifecycle
locations, receipt digests, identities, predecessor objects, and ordering bind
at 10513-10610 and 10643-10701; the bundle locator and carrier source digest
bind before admission at 11011-11034. The six Q-NR2 negative legs exercise the
ruled changed-byte, changed-pack, moved-pack, swapped-chain, traversal, and
symbolic-link counterfactuals.

Here “same pack” means the same committed pack-tree digest at the same
repository-relative location; a distinct absolute clone path is the relocation
being admitted. “Same byte” means every issued artifact read through the
carrier still satisfies its original digest/reference and chain bindings; it
does not require the non-authoritative carrier bytes to have existed at issue
time.

Question: after the replay and code-path inspection, is there any state newly
accepted only because a carrier is present in which an issued artifact differs
by one byte, the selected pack has a different committed-tree digest, or the
pack has a different repository-relative location? If yes, REJECT and give a
reproducible accepted counterexample. If no, AFFIRM. If the exhibits are
insufficient to enumerate the acceptance route, REFUSE and name the missing
primary evidence.

## 7. Required judge replay and assembler-observed tail

First verify `git rev-parse HEAD` is
`b420a45a58ecba69b8fb7a121eb27b864ba39325`. Then run exactly:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness.LaunchLineageRelocationTests tests.test_launch_window.LaunchWindowEntrypointTests.test_live_launcher_refuses_post_hoc_relocation_carrier_option
```

The assembly seat observed exit 0 and this exact tail at the pinned head. This
is disclosed evidence, not the judge's result:

```text
test_direct_relocation_refuses_carrier_without_locator_authentication (tests.test_arm_readiness.LaunchLineageRelocationTests.test_direct_relocation_refuses_carrier_without_locator_authentication) ... ok
test_live_campaign_replay_refuses_relocation_carrier (tests.test_arm_readiness.LaunchLineageRelocationTests.test_live_campaign_replay_refuses_relocation_carrier) ... ok
test_moved_source_authenticates_only_with_explicit_carrier (tests.test_arm_readiness.LaunchLineageRelocationTests.test_moved_source_authenticates_only_with_explicit_carrier) ... ok
test_relocated_committed_pack_change_keeps_launch_binding_mismatch (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocated_committed_pack_change_keeps_launch_binding_mismatch) ... ok
test_relocated_repository_relative_move_keeps_launch_binding_mismatch (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocated_repository_relative_move_keeps_launch_binding_mismatch) ... ok
test_relocated_swapped_chain_keeps_launch_consumption_invalid (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocated_swapped_chain_keeps_launch_consumption_invalid) ... ok
test_relocated_tamper_keeps_launch_binding_mismatch (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocated_tamper_keeps_launch_binding_mismatch) ... ok
test_relocation_carrier_traversal_keeps_launch_binding_mismatch (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocation_carrier_traversal_keeps_launch_binding_mismatch) ... ok
test_relocation_source_locator_digest_is_mandatory (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocation_source_locator_digest_is_mandatory) ... ok
test_relocation_target_symbolic_link_keeps_launch_binding_mismatch (tests.test_arm_readiness.LaunchLineageRelocationTests.test_relocation_target_symbolic_link_keeps_launch_binding_mismatch) ... ok
test_live_launcher_refuses_post_hoc_relocation_carrier_option (tests.test_launch_window.LaunchWindowEntrypointTests.test_live_launcher_refuses_post_hoc_relocation_carrier_option) ... ok

----------------------------------------------------------------------
Ran 11 tests in 8.991s

OK
```

Record the judge's own exit code and exact tail. No repository-wide suite,
hardware run, campaign, or quiet-machine measurement belongs to this gate.

## 8. Required ruling shape

For Q-NR1, Q-NR2 parts 1-8, and Q-NR3, return AFFIRM / REJECT / REFUSE with
load-bearing packet-local `file:line` citations and the replay result. Preserve
every disagreement with the implementation seat and delta refuter. Check packet
hygiene separately: name any omitted contrary evidence, compound question, or
unsupported claim and its effect. This gate can establish whether the landing
satisfies A0; it cannot merge the branch or retire the kernel row.

## 9. Exhibit manifest (sha256, verbatim copies)

```
469952438c228e750533f29588aeda35f9a23328b1ad8afec3b63365a07c6e12  packet-exhibits/authority/01-magistrate-rulings.md
7bc444cce53b7849cbe39c0423647f472d4d8ce49b5d1a61d966da5a0434e86c  packet-exhibits/code/joulewise/arm_readiness.py
8c8015c3a03e4aa7328c6b4d1596ac026b8e930d1f20ae2691d11c4f1257a339  packet-exhibits/code/scripts/launch_window.py
6e5b054b24cbf507e1bd4b1f7a62d73794f37a8e8dc6241b8f979916ac5dd9d2  packet-exhibits/code/tests/test_arm_readiness.py
b7393e91d864e0049ce51202dec5a4afdd2619b10e482c416342e39d9a1f5d0d  packet-exhibits/code/tests/test_launch_window.py
7412a613909788224a9f4b3ef00c221bcd7c0321b807d0965175833e420e88f0  packet-exhibits/reports/01-sol-report.md
0cb115c2c7d572f8b6dcd4451b7b09aff1081aa166068ddb9e9a0aa8ce581717  packet-exhibits/reports/02-refuter-merge-base.md
4c28d67f3e0ab433fa81581bca04cd7bf3094571592ff0998e9aa3003cf1c0ba  packet-exhibits/reports/03-sol-fix-round-1-report.md
9d3df4cd39a92cd78e39420b67fc948d524ac14fc868cbace122ecd68b0bdf12  packet-exhibits/reports/04-sol-fix-round-1-report.md
2a113f37a06adde1ce43323d7ca524e1d35cd37e377a1afd467fc5ae195ed56d  packet-exhibits/reports/05-delta-reaudit-round-1.md
1f3d79e1794318a0ae1087de663c8fe336a8882480f2f40d1d831909eed49e2c  packet-exhibits/reports/06-sol-fix-round-2-report.md
```

## 10. Derived assembly receipt

The validator's canonical receipt is stored at
`packet-exhibits/derived/assembly-validator-receipt.json`. It is derived after
the packet is sealed, is not a custody input, and is intentionally outside the
exhibit manifest to avoid a circular packet-hash dependency.
