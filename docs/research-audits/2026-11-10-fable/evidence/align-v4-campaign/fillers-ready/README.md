# Filled F2 queues

Runner pin `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Expiry **2026-11-24T12:35:29-08:00**.
Fast-forward by **2026-11-24T12:35:29-08:00** to retain an unexpired queue. See RUN_STATE.md items 422 and 425 on main.

| Kit | Queue | Queue SHA-256 |
| --- | --- | --- |
| f2-stab-01 | [f2-stab-01.json](queues/f2-stab-01.json) | `3884b5a7daa60e3983bf2abf5d32f20ba820908b6cb3e57fa6feb174f17b12f6` |
| f2-stab-02 | [f2-stab-02.json](queues/f2-stab-02.json) | `9ebaba3b985c69eab5da1004b2c6e49383cff71d46763048396393c2d2f42c28` |
| f2-stab-03 | [f2-stab-03.json](queues/f2-stab-03.json) | `18a79d1aada6f7bbabd45d9ec9208d70a0a938e16c8459e60da75aca8bda13ea` |
| f2-stab-04 | [f2-stab-04.json](queues/f2-stab-04.json) | `5eded096303a87cba421a8c70e851d0e5714e7d147bc6803e539c83c9ca5e7be` |
| f2-stab-05 | [f2-stab-05.json](queues/f2-stab-05.json) | `5ceccf92081435d6062fc21d3a892afa8dfe678d5fdef9a9f5b3a18253d84834` |
| f2-stab-06 | [f2-stab-06.json](queues/f2-stab-06.json) | `95e624286191b42e0232f66a444b401a6039017994ef1b102904775bcbf3544d` |
| f2-stab-07 | [f2-stab-07.json](queues/f2-stab-07.json) | `6f25a3dc93a431cfd1875388ea3ea3642830230a8868aab1c5d6af9ca9fbce05` |
| f2-stab-08 | [f2-stab-08.json](queues/f2-stab-08.json) | `e485ce18d528f07820675e205b0b2427be12727da336eb57acc07bb996908939` |
| f2-stab-09 | [f2-stab-09.json](queues/f2-stab-09.json) | `b9fab75048daab65dc1aeda1364270b7a3581853e2a7a9a89b1d7733c35c7c95` |
| f2-stab-10 | [f2-stab-10.json](queues/f2-stab-10.json) | `74b5a6b0f68100bd91c1eab9c0aec3327098c77d1d38a2d96f3241a60dda1ad3` |
| f2-stab-11 | [f2-stab-11.json](queues/f2-stab-11.json) | `07f4886956d295f8fea4a4347c79d9388ce7218cbca991bbee8554ed85779466` |
| f2-stab-12 | [f2-stab-12.json](queues/f2-stab-12.json) | `b83e8c45fdb541d304fea4a4e93ff61e8f29801715b995dc6ad52db8af839893` |
| f2-stab-13 | [f2-stab-13.json](queues/f2-stab-13.json) | `dd15946a64a3e7c64f7e534d6c3ffaa11ebb3b6280165fd1e9a848163aa69752` |
| f2-stab-14 | [f2-stab-14.json](queues/f2-stab-14.json) | `199474d75f7f7932694f42173167a269b0682d06b82f43b95d956ff5a3869a12` |
| f2-inst-01 | [f2-inst-01.json](queues/f2-inst-01.json) | `2c8aeb02c58cb8b7072a21effefecff298cb23334d94652b99d70ce1297d8eff` |
| f2-inst-02 | [f2-inst-02.json](queues/f2-inst-02.json) | `86884f2e706efedcf70de730133ff435eb231875f63fec63efcd6c127ecaefbe` |
| f2-inst-03 | [f2-inst-03.json](queues/f2-inst-03.json) | `b0cfbe401037d6527de903634fa9bdd4a1185dad677e8d728b89309ca4fbd5b3` |

Regenerate from the audit checkout root with `PINNED_CHECKOUT` set to a clean checkout of the runner pin.

`python3.13 -I -B docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-ready/tools/fill_queues.py --runner-repo "$PINNED_CHECKOUT"`

[Pinned validation results by SHA-256](VERIFICATION.json)
