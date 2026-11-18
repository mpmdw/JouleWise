# PR #812 close proof by attempt order

Astra's third audit confirmed the two earlier timing repairs and reproduced
two close-proof failures and a close-time rounding failure. The lead's
frozen specification selects the latest **attempt**, then requires its own
receipt and passing restore readbacks. The code pin is
`df261f6a235e976be8859ab5314af737a08f6d7d`. The draft patch was generated
from audit head `f9b03c33d9996fcbb9c663201d519c5fe1ccbbad` and also applies
to `e26a566c1f2c9eaf12e47f75bb6e2facb2eaea46`.

| Finding | Repair and regression |
| --- | --- |
| Missing latest receipt | Start and Run consult the attempt ledger, including pending starts. The six emitted gates refuse and name a newer started span without a receipt despite valid older proof. |
| Stale proof after a wall rollback | Sequence order wins in a sequenced ledger. The fallback uses explicit boot order and then monotonic order within the latest boot. The Bash/Zsh rollback cases refuse the old proof and accept the later attempt's own receipt even though its wall close is earlier. |
| Receipt identity mismatch | Both shells refuse a receipt whose span id differs from the latest ledger attempt id. Restore failures on the matching receipt also refuse. |
| Close stamp rounding | The gates and child compare close and start in epoch nanoseconds. Both shells pass `T+.750` after a `T+.125` close and refuse one nanosecond early. The child test exercises the wall and projected clocks independently. |

The lead supplies the complete host attempt ledger, including earlier and
other-lane attempts, and identity-bound close Checks for receipt producers
that lack explicit span ids. Its record shapes are documented beside the
drafts. The qualification launcher rereads the selected proof under the
shared desk fence lock and publishes the new attempt before bootstrap. The
launch regression verifies a failed bootstrap still leaves an attempted
span with no receipt. The launcher passes the span id through to the
child. Its own receipt records that id and the exact close stamp.

| Kit | SHA-256 | Frozen paths verified |
| --- | --- | --- |
| cl-qual-01 | `32576b1f9508e9625f2557ecbc0b40cb8b2910eff1693a6b61b77765d4813b6f` | 38/38 |
| cl-qual-02 | `8c3687bc7886d269ad3b57cc16c5e67b18bdc63ec0424af17cf9745c4b37b7e6` | 38/38 |
| cl-qual-03 | `8887903fd18477381ff930a19d520d9e9a1226242dc80f9ae4934940b9c2d9a7` | 38/38 |

All 114 frozen hashes verified using Git blobs. Only the two entry script
hashes changed. The GitHub test-merge tree matches the pin's tree
`ea6f5fc234e63e1c2e93eb70ecd0c892c6ed8bc5`. All 109 focused Python 3.13
tests passed. The final wrapper passed 1,552 Bash/Zsh gate checks,
including 84 round-3 assertions, plus 91 pinned checks, 74 shell syntax
checks, 62 Python compile checks, 21 historical standing checks, nine
Round 10 tests and 13 generator checks. Local verification used synthetic
fixtures and left the tests that send process signals to hosted CI. The
local fixture census returned exit 2 because the environment denied `ps`.

Qualification remains `HOLD_FOR_FIT_FREEZE`. The lead owns the draft
commit and final Astra replay. [PR #812](https://github.com/mpmdw/JouleWise/pull/812) · [Exact-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44265227537)
