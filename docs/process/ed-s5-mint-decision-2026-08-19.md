# Ed decision packet — S5 freeze-0003 mints (2026-08-19)

## The one blocking decision

The D-147 transaction is EXECUTED THROUGH S4. The three `_v3` packs are
emitted (bound to r6 at birth), their D-134 evidence is authored (33
receipts, all PASS, committed `3a75a77`, landed on the branch), and the
recorded S5 procedure is extracted and verified against the T10 record.
The freeze mints themselves are BLOCKED by the Claude Code permission
classifier — for both the executing agent and the lead — on exactly these
command classes at the measurement checkout:

```
python3 scripts/project_identity_pins.py freeze <pack_root>      # U11, x3 first
python3 scripts/generate_arm_readiness.py freeze --pack-root <v3> --predecessor-pack-root <v2>   # x3
```

No mint was attempted through any workaround; no state changed. This is
the same harness class as the 2026-08-05 self-merge block (cured then by a
`settings.local.json` rule). The magistrate deliberately did NOT self-grant
a permission rule for claim-bearing identity mints while you were
reachable within the validity window.

**Options:**
1. You run the six commands yourself at `/Users/edr/JouleWise-measurement-20260818`
   (exact sequence below, ~5 minutes; the verification battery is scripted
   and Claude checks every receipt afterward).
2. You add a narrow Bash allow rule for the two scripts to
   `.claude/settings.local.json` and tell Claude to execute S5 under the
   already-issued license.
3. Defer — but the S4 evidence EXPIRES ~2026-08-20T16:51:33Z and dies on
   ANY REBOOT (boot session `da90818c-9c31-45d0-8813-deae65fba143`).
   After either event: `git rm -r` of the six governed evidence dirs and a
   full S4 re-author before S5 can run.

**DO NOT REBOOT the Mac before ruling.**

## Exact S5 sequence (as extracted from the T10 record; one commit per step)

At `/Users/edr/JouleWise-measurement-20260818`, branch
`impl/r2-s0-mint-resolver` @ `3a75a77`:

```
# U11 identity-pin projection (freeze refuses without it), commit each:
python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_1p5b_v3
python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_floor_qwen25_7b_v3
python3 scripts/project_identity_pins.py freeze configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
# freeze-0003 x3, commit each:
python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_floor_qwen25_1p5b_v3 --predecessor-pack-root configs/campaigns/d117_floor_qwen25_1p5b_v2
python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_floor_qwen25_7b_v3 --predecessor-pack-root configs/campaigns/d117_floor_qwen25_7b_v2
python3 scripts/generate_arm_readiness.py freeze --pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3 --predecessor-pack-root configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2
```

Landing is a pull FROM the measurement checkout (never a push from it);
Claude performs it plus the full receipt verification (path-binding,
PASS, `freeze-0003`, predecessor triple vs the `_v2` receipts, digests
for the confirmation table).

## Confirmation table (draft; [PENDING MINT] rows fill at S5)

| Item | Value |
|---|---|
| Live acceptance generation | `d079_calibration_acceptance_v2_n17_r6` |
| r6 file sha256 | `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d` |
| r6 pins moved vs r5 | `reduce.py`, `uncertainty_evidence.py` (fix-round edits; 19-member neutrality replay: 0 mismatches) |
| r5 file sha256 (retained history) | `92b9c0608bc97fbd7769050213b1433c32d3fe060d1292167920363e58b8cf0f` |
| 1p5b `_v2` freeze-0002 sha (predecessor) | `1277103b42090f3ce41df0e030a2a5f2a3998598efec12fef812ca5b36b89666` |
| 7b `_v2` freeze-0002 sha (predecessor) | `decd8cdc6a589397e28240b33b97e1b38575be860490a2c6de31be51611842d0` |
| contrast `_v2` freeze-0002 sha (predecessor) | `18855647c38ec8cf521167fcaae62a06914a8ab7087aeded96835cb418f9607e` |
| S4 evidence rollups (1p5b / 7b / contrast) | `0e353456…` / `1421ea4e…` / `653f22c0…` (full 99-row manifest in session custody) |
| 1p5b freeze-0003 sha + committed tree digest | [PENDING MINT] |
| 7b freeze-0003 sha + committed tree digest | [PENDING MINT] |
| contrast freeze-0003 sha + committed tree digest | [PENDING MINT] |

## Other accumulated Ed-owed (unchanged priorities, carried from T11/T12)

Family-marker particulars (recommendation: `_v3` landed first; marker
retrofits via its own co-design pass); R1 row-registry reserved values —
three of five are now supplied (`successor_pack_ids` = the `_v3` ids);
A4 contrast markers; environment-fingerprint semantics; the stored
anchor-v2 population disposition (magistrate recommends the registered
limitation paragraph); final exact-byte publication confirmation (this
table, post-mint).
