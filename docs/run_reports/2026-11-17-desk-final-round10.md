# PR #799 round 10 desk publication repair

The Astra operations audit reproduced a successful controller-side publication result while a Git ref lock prevented the verdict from being installed. The publisher now updates the local ref against the expected old object ID, checks Git's exit status, and reads the ref back before returning the signed commit.

The three SignedTransport regressions reproduced the locked ref, a concurrent writer, and a ref that disappeared after Git reported success. All three failed at `28ceeaba9`. All 80 desk-final tests passed with the repair. The tests used temporary local Git repositories and throwaway signing keys. No test from the launch integration module ran locally.

CI and admission are tracked on [PR #799](https://github.com/mpmdw/JouleWise/pull/799).
