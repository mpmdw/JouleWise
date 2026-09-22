# Fixture sources — qpe01-pilot-n1-20260922-0217 (READ-ONLY archive)

Archive root: `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922`

Extracted by `extract_fixtures.py` in this directory.  The archive was
verified byte-exact against the live custody root by the harvesting
activation (`SHA256SUMS-check-against-live-root.txt`, 15801 OK); the
session digests below match exhibit C1 of the cold-gate packet
(`docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/exhibit-C-executed-evidence.md`).

| envelope | records | recorded anchor | session.json sha256 | powermetrics plist sha256 |
| --- | --- | --- | --- | --- |
| 01 | 2547 | wall_minus_monotonic_span_exceeded | `11f999b0f8c4992e271967933625e02acf85854170e2b7a50c7709182f7a08c6` | `ef4429b4a78546318d957ebedc5248d166f3bac4a4d75e8173aabdd891cf2dde` |
| 02 | 2535 | bounded | `bbeb51b8091304c22a0f021a49d0352d3dd808d66a4fee4310b0e91658bd6ba3` | `d88f88215e53d570b36d9ced75bbfed2f8dc2d128ff48184bbc77b54f1c9cb77` |
| 03 | 2504 | affine_clock_fit_empty | `15fd5e92d23fe2d263daae9e266baa1c28000d35ec11489ff0b12e8913f2f9e9` | `a7cbfc49461b780e713a71b224d513aaf4059c18a61c8251f67c21c0088d2c18` |
| 04 | 2482 | affine_clock_fit_empty | `30b8c392495b7ae51a37114414f997b45114c11d25da57ff4327b0b7004c5487` | `116eb2ebed788a94d1afb260b710025c47e0ddaa6de2472f2d00b14ba21d0c6a` |
| 05 | 2511 | bounded | `e10d95183894371bb8970bb1423bddd3f5d3f56e95ccd53abeb2144fd2721663` | `ecf01ab1711b0374a5007d9f34c80e029293f848d0756deb03d5222a80f1e772` |
| 06 | 2488 | bounded | `66239a264f86202a75280396ab68251a9bd57b27c1b348ae934ffce85305d3fc` | `93d9d11474499b187f567fb428a0dccbea03d7ddee1c20b145fc107b31e24e6a` |
| 07 | 2488 | wall_minus_monotonic_span_exceeded | `7f45379557cb8e34dc66b3229f0be57410fe0840d53716180124cca040f0397a` | `06561794454e444e37fd91e1be6e05bdebde4e12b8d2676e6d4ef684a50071ef` |
| 08 | 2532 | effective_clock_anchor_bound_exceeded | `cd56a38e581837ec82431950b05823a57cc0a8d2d85db15bad41eca612d92b99` | `117e2d51962dd9046523d925037316109175a88d994cc674f621a374cd6f8a18` |
| 09 | 2529 | effective_clock_anchor_bound_exceeded | `7fb73b249c3ea4bd74fe23d4aedc08bc1eed1bde76d429080cc90f28bea38cd0` | `a3e38147bb0ba01a76dc5ec8dc01e175b1739cce670399cbeb051f01d8adcc42` |
| 10 | 2502 | wall_minus_monotonic_span_exceeded | `6c16f672ff53b4d32ecc7bdc266e4128fe175eef209e0f50023996bde28b1f96` | `713c2b1f2b1eb76ad311525eba9cd948ff7a23b7e77803013c11b6f0c316caee` |
| 11 | 2513 | bounded | `f9dea9108a5708cc9f8edb543fed64188fe0b095a9119f06f657bd10bd121e1f` | `a797c292ca71f128553af2e696f22a253c87de9e4903f4acee0e574cf6c48772` |
| 12 | 2532 | bounded | `e42ae3fcdbe2b7c727a77e42f7bad69896bed940a4daf897da5ca9395471eb84` | `f77b72df88abdd3539736791634418580cc587019226275ac3d498378bdf7696` |

`exhibit-D-timed-log.txt` is a verbatim copy of the packet's
`exhibit-D-timed-log-0210-0435.txt` (191 lines, sha256
`70218c4a41b0ee87e20f032790e442451f36d713df49933ccbaba907395797b6`),
used by the timed-log attestation scanner regression.

## The two `--style syslog` captures (ruling 18 Q3 C6)

`exhibit-D-timed-log.txt` above was captured in `--style compact`, which is
NOT the style the production argv uses (`timed_log_argv` passes `--style
syslog`), and whose header line is therefore a different string:
`Timestamp               Ty Process[PID:TID]` against syslog's
`Timestamp                       (process)[PID]`.  The header guard
(`timed_log_has_header`) pins the RULED argv's own output, so the two
captures below — both taken live on this machine by activation 59857fe5 and
recorded verbatim as that activation's process-trace records `07c-exhibit-D2`
and `07c-exhibit-D3` — are the fixtures that carry it.  The compact capture
is kept as a NEGATIVE fixture and for the marker-count parity check (191
lines and 30 marker lines in both styles, so marker detection is
style-independent).

| fixture | lines | sha256 | what was captured |
| --- | --- | --- | --- |
| `exhibit-D2-timed-log-0210-0435-syslog.txt` | 191 | `dba7fb7cb92e9179a8e4d09e40290b578bbd68d12f29bb42eb417abcf6a4eb63` | the pilot night's own window, `--start '2026-09-22 02:10:00' --end '2026-09-22 04:35:00'`, 30 applied-correction marker lines |
| `exhibit-D3-timed-log-zero-match-syslog.txt` | 1 | `da1b28eff7848fc42698579387fb9881a2bd1ceda8151ba16617a3b63550718b` | a ZERO-match minute (`--start '2026-09-22 10:48:40' --end '2026-09-22 10:49:40'`), 50 bytes: the header line alone, and nothing else |

Capture argv shape, both: the module's own
`timed_log_argv(start_epoch_s, end_epoch_s)` —

    /usr/bin/log show --info --debug --style syslog \
        --predicate '<TIMED_LOG_PREDICATE>' \
        --start '<YYYY-MM-DD HH:MM:SS>' --end '<YYYY-MM-DD HH:MM:SS>'

read-only, no sudo, exit 0.  D3's predicate was additionally re-run against a
process that cannot exist (`process == "no_such_process_zzz"`) over the same
minute, with byte-identical output: an empty result set still prints the
header, which is the premise the guard rests on.

Provenance: activation 59857fe5, process-trace record 07c (2026-09-22 11:00
PDT), `docs/process_traces/2026-09-22-activation-59857fe5/`.
