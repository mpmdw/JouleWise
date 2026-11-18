# F2 stability kit manifest

RL-179 F-4 (b) and RL-180 row 13. Kit data on the admitted pin, class B, Tier 0.
Base [f2-inst-01.v1.1.json](../item-drafts-f2/f2-inst-01.v1.1.json).
Each kit yields twelve single-leg spans with a fresh soak and a 600 s loaded-idle hold before the turn.
The worst case per span is **5,850 s** (1,950 s soak + 1,200 s overhead + 2,700 s leg).

## Seed search and fields that differ

For each kit ID, scan integer master seeds **2026111444–2026211443 inclusive** in ascending order.
At each seed, call the pinned `sha256-cells-v1` generator with that `campaign_id` and the base
seed-law fields and decode defaults. Accept the first seed whose generated list matches the
base leg ID, prompt size, decode cap, G0 shape and band at every position, with the same leg count.
All candidates carry the base Automatic power-mode guards. No other property selects the seed.
Re-run the pinned `gen-legs` CLI at the first hit to produce the recorded list.

The only differences are `campaign_id`, `ruling.id`, `seed_law.master_seed` and the
derived `legs[*].seed` values. The cell law keys on `campaign_id`, so the derived leg
seeds are regenerated for each new ID. The copied title describes the source kit and its seed.
Kits `07` and `10` share the first-hit master seed `2026111733`. Their campaign IDs yield
different leg-seed lists. Indices below are zero-based in `legs`.

| Kit | SHA-256 | Runner pin | First-hit master seed | Candidates tested | First different index | Span drafts | Queue entries |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| [f2-stab-01](f2-stab-01.v1.1.json) | `dbad9c7b79088bb6f06aac1c1148c3631a0c616fd2ece596bab0f56657ce70fe` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112460 | 1017 | 0 | [12 items](items/ITEM-f2-stab-01.md) | [12 entries](queues/f2-stab-01.json) |
| [f2-stab-02](f2-stab-02.v1.1.json) | `1fe8dd1d0fb60fe1d481ecb0d4358fda595668c1e889a35a75695e290fcad505` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112341 | 898 | 0 | [12 items](items/ITEM-f2-stab-02.md) | [12 entries](queues/f2-stab-02.json) |
| [f2-stab-03](f2-stab-03.v1.1.json) | `ac4b303e228233765efda120b2d63f2f6e59d7f8565c4b913880c4a1aa1dc404` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112481 | 1038 | 0 | [12 items](items/ITEM-f2-stab-03.md) | [12 entries](queues/f2-stab-03.json) |
| [f2-stab-04](f2-stab-04.v1.1.json) | `494739dedbc07f2ee3a02b1e5f9561bb4812d765c7630e6931c24ea138525bff` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026111676 | 233 | 0 | [12 items](items/ITEM-f2-stab-04.md) | [12 entries](queues/f2-stab-04.json) |
| [f2-stab-05](f2-stab-05.v1.1.json) | `023febe9afc8532b8f06bb40dfe32dd64a933c99e8e080a51e2686e888246b11` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026111508 | 65 | 0 | [12 items](items/ITEM-f2-stab-05.md) | [12 entries](queues/f2-stab-05.json) |
| [f2-stab-06](f2-stab-06.v1.1.json) | `a02d18bafca780c580ae7dfe970e3a81e3e12b4051b269699db329f02c33172c` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026114403 | 2960 | 0 | [12 items](items/ITEM-f2-stab-06.md) | [12 entries](queues/f2-stab-06.json) |
| [f2-stab-07](f2-stab-07.v1.1.json) | `fb22cadce8be3c7d7642c9b55802aa0bd4ea90e41c7c0e9a5038e7a8dc88746d` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026111733 | 290 | 0 | [12 items](items/ITEM-f2-stab-07.md) | [12 entries](queues/f2-stab-07.json) |
| [f2-stab-08](f2-stab-08.v1.1.json) | `aaba2ad04cbc88e9872c292699dfa9f98dfb15ad9f7e0af23a1faf0091bebf00` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112349 | 906 | 0 | [12 items](items/ITEM-f2-stab-08.md) | [12 entries](queues/f2-stab-08.json) |
| [f2-stab-09](f2-stab-09.v1.1.json) | `9a2b863f7abbffdc2d33a3af6bee7d8381d0c54883dbb4a7cac41378572c5ce8` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112216 | 773 | 0 | [12 items](items/ITEM-f2-stab-09.md) | [12 entries](queues/f2-stab-09.json) |
| [f2-stab-10](f2-stab-10.v1.1.json) | `bb54fdaff1292ab24f53204698649d0925fa00beedca70604f760a340c9ee926` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026111733 | 290 | 0 | [12 items](items/ITEM-f2-stab-10.md) | [12 entries](queues/f2-stab-10.json) |
| [f2-stab-11](f2-stab-11.v1.1.json) | `e8cb23471f556d21514fb5ba37ffa409b9b697cfbd2519d3c2ab0c6922ed36fe` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026112450 | 1007 | 0 | [12 items](items/ITEM-f2-stab-11.md) | [12 entries](queues/f2-stab-11.json) |
| [f2-stab-12](f2-stab-12.v1.1.json) | `7a0440d3f15823760179782f85cad560e8ca917bf66201c02b1b911d79af35f9` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026111711 | 268 | 0 | [12 items](items/ITEM-f2-stab-12.md) | [12 entries](queues/f2-stab-12.json) |
| [f2-stab-13](f2-stab-13.v1.1.json) | `47c3d2f5f6133112e7a209c9522e48bb3388c7fa27f56e5ffdf86962d95f7de3` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026115694 | 4251 | 0 | [12 items](items/ITEM-f2-stab-13.md) | [12 entries](queues/f2-stab-13.json) |
| [f2-stab-14](f2-stab-14.v1.1.json) | `73fe743e013cddd6d5294e95e076c64933a81eb95933fb4aa5dfb85471b9402d` | `2d347f721552fe03bdd19f113e7bad7a7c24908e` | 2026114612 | 3169 | 0 | [12 items](items/ITEM-f2-stab-14.md) | [12 entries](queues/f2-stab-14.json) |

## Issue and reads

The first F2 stability leg of a local date is **rank 1**. Further F2 stability legs that date are **rank 4**.
The magistrate ranks at arm time under item 422. The kits have no age expiry or issue cap.
The issue template records the dated-block guard and how to assemble a queue under F-6. [Issue template](ISSUE.md)

RL-179 row 12 keeps the series sealed until freeze 2 is committed and `lm-stab-01` has its cold pass.
The series is descriptive and enters no fit or count. The manifest must name each read before it runs.
An authorized frozen read takes only legs closed at its stage-1 hash and follows F-12 as amended
by RL-180 for release. RL-180 requires spread estimates within a prompt-size cell.
The `lm-stab-01` read schedule awaits lead registration.

## Verification

Run `python3 -I -B tools/validate_kit.py KIT --repo PINNED_CHECKOUT --batch-window WINDOW`
from this directory. The audit-side tool checks RL-180’s cell comparison and calls the pinned
`validate-kit` for frozen-path and seeded-list validation. Both batch-window arguments passed
for all 14 kits. All 168 plans and 14 queue fixtures passed. Mock `f2-stab-01` L001 returned
`{"rc": 0, "legs": 1, "stops": []}`. [Recorded outputs](VERIFICATION.json)

## Qualification-pin kits

Use the manifest seed procedure above and freeze the result with the named pin's own `pin-kit`.
The qualification pin changes the frozen commit and path digests. The cell layout follows the same base.

| Kit | SHA-256 | Runner pin | First-hit master seed | Candidates tested | First different index | Span drafts | Queue entries |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| [f2-stab-15](qual-pin/f2-stab-15.v1.1.json) | `8dceffc2e1a10a03d25c6c06487756fe37f8f5a1c57d52e242a64faabcbc36a1` | `6e9d42f1dd3d308bc9239143d0d634ab965e50e1` | 2026112669 | 1226 | 0 | [12 items](qual-pin/items/ITEM-f2-stab-15.md) | [12 entries](qual-pin/queues/f2-stab-15.json) |
| [f2-stab-16](qual-pin/f2-stab-16.v1.1.json) | `0fc1139dfb4b92ab18e5fb4c0b66e0d211a02e218e841a4cf94fde1fb19f2b96` | `6e9d42f1dd3d308bc9239143d0d634ab965e50e1` | 2026113603 | 2160 | 0 | [12 items](qual-pin/items/ITEM-f2-stab-16.md) | [12 entries](qual-pin/queues/f2-stab-16.json) |
