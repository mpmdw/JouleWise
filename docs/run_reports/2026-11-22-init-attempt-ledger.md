# RL-197c attempt-ledger initializer

The initializer publishes sequence 1 after the admitted ctl runner proves the
close of the inaugural pin-B span. It uses the desk lock created by that launch.
The ledger uses the pinned launchers' JSON serialization and the sidecar records
the exact proof output, both SHA-256 digests, the initializer commit and the
number of the initializer's typed RUN_STATE issue.

## Magistrate command

Use a clean, separate checkout at the full `INIT_COMMIT` named in the lead's
typed initializer issue (`INIT_ITEM`). The issue must bind the inaugural
pin-B dispatch item, its typed `SPAN_ID` (passed to that launch as `--span-id`),
the absolute `CLOSE_RECEIPT`, its full `RECEIPT_SHA256`, `CLOSE_NS` and
`INIT_COMMIT`. It must state “This attempt is the last armed span on the host.”
Take `LAST_ARMED_SPAN_ID` from that statement. If another span armed after the
inaugural close, hold and follow RL-197c §3. Use the absolute paths from the
issue for `INIT_CHECKOUT`, `CTL_CHECKOUT`, `PYTHON_BIN`, `ATTEMPT_LEDGER` and
`CUSTODY_ROOT`.

After the ordinary close, verify the restore readback, stopped feeds, absent
process groups and absence of foreign processes for `CLOSE_RECEIPT` in the
magistrate lane. Run this block only after all four checks pass.

```bash
test -n "$SPAN_ID" && test "$LAST_ARMED_SPAN_ID" = "$SPAN_ID" || exit 1
test "$(git -C "$INIT_CHECKOUT" rev-parse HEAD)" = "$INIT_COMMIT" || exit 1
init_status=$(git --no-optional-locks -C "$INIT_CHECKOUT" status --porcelain) || exit 1
test -z "$init_status" || exit 1
test "$(git -C "$CTL_CHECKOUT" rev-parse HEAD)" = f45e22e4efa6b48dd05f099f39eb62246e324177 || exit 1
export CLOSE_PROOF_RECEIPT="$CLOSE_RECEIPT"
export HOST_RESTORE_OK=1 FEEDS_STOPPED=1 GROUPS_ABSENT=1 FOREIGN_PROCESSES_ABSENT=1
"$PYTHON_BIN" -I -B "$INIT_CHECKOUT/scripts/init_attempt_ledger.py" \
  --ledger "$ATTEMPT_LEDGER" --custody-root "$CUSTODY_ROOT" \
  --span-id "$SPAN_ID" --close-receipt "$CLOSE_RECEIPT" \
  --receipt-sha256 "$RECEIPT_SHA256" --close-ns "$CLOSE_NS" \
  --ctl-checkout "$CTL_CHECKOUT" --python-bin "$PYTHON_BIN" \
  --run-state-item "$INIT_ITEM" || exit 1
printf 'First-row sidecar %s\n' "$ATTEMPT_LEDGER.first-row.json"
```

Record the printed ledger SHA-256 and sidecar path in RUN_STATE. On refusal
hold the pilot and report the refusal to the lead. If initialization was
interrupted, hold for the lead if either output exists. Each file is published
by a hard link, and a caught failure rolls back both under the lock. A host
failure between the two publications can leave a complete ledger by itself.

## Verification and handoff

- `python3 -B -m unittest -v tests.test_init_attempt_ledger` uses synthetic
  receipts and imports the read-only close-proof entry points from disposable
  sparse checkouts of both pinned commits. It checks exact ledger bytes and
  sidecar provenance, refusal paths, lock coverage and rollback on link/fsync
  errors. The local budget is one worker for the targeted tests.
- The draft awaits the independent executing Astra review and hosted suite
  before the lead issues initializer authority.
- **NEEDS_SPEC.** RL-197c names `git diff f45e22e4e -- scripts/` for the merge
  check. The requested `main` base already differs from the ctl pin across
  `scripts/`. Confirm whether the merger should use the PR delta from `main`
  to check initializer scope. The PR delta adds the initializer, its test and
  this report.
