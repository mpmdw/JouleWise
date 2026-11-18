# Unissued f2-inst-01 one-leg spans

RL-179 F-4(b) and (c). These drafts supersede the unissued multi-leg pieces
for this kit. [Frozen kit](../../item-drafts-f2/f2-inst-01.v1.1.json) · [Queue draft](../queues/f2-inst-01.json)

On `origin/main` at `d934178b9`, RUN_STATE items 407 and 411 confirm
that `f2-inst-p1` ran `L001–L003` and closed clean. Only `L004–L012`
appear below.

## Issue, start and check

- Rank 2, finite filler. The first `f2-stab` leg of the local date ranks
  first. Among eligible rank-2 spans, take `f2-inst-01`, then `f2-inst-02`,
  then `f2-inst-03`, in each kit's leg order. Re-rank at arm and protect
  each pending dated block's ability to take its t0 on its own date.
- Confirm the leg has never run. If a predecessor leg ran under a prior
  span ID, use that span's Check and record the mapping.
- Bind the issued item to the exact kit SHA,
  admitted runner pin and committed queue SHA. Record the item number,
  local issue time and Check target. Use `expires_epoch_s: null`.
  The draft's `not_before` is the local date RL-179 took effect. Fill the
  pinned queue format's required `expires_at` timestamp in the committed
  issue queue under F-6. Eligibility follows the admitted hashes and
  scoped stops. Use the pinned queue tool for `validate-queue` with the
  audit checkout as `--kits-root`.
- Apply F-2 and F-5 to the immediately preceding close on the host. Record
  the receipt, restore readback, stopped feeds, cleared fence, absent
  process group and clean process census. Confirm the copy has stopped
  before the new soak. Allow up to 600 s for copy verification, then
  carry copy debt under F-5. Apply any host-wide stop separately.
- Apply F-3(c) first-native hand-read eligibility before arming. All three
  kits use the same own-G0, q600, Automatic leg type on this pin.
- Verify the staged kit and queue hashes. Run the pinned `validate-kit`
  with frozen-path verification and `plan` with the selected `--legs`,
  actual t0 and applicable `--batch-window` (`02:00-02:35` or `13:14-13:15`).
  The plan must admit the sole leg and its fresh soak. Recheck before using
  the pinned launcher with the explicit leg and the refreshed fence deadline.
  Launch is the last action. After close, record the operational Check and
  apply the named holds at their F-3 and F-6 scopes.
- RL-169 §3 applies. These legs are sealed until freeze 2 is committed and
  `lm-inst-01` has its cold pass. Each leg is outside campaign data, enters
  no fit and counts nowhere.

## f2-inst-01-l004

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l004` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 4, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L004`, 2,000 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-p1` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l004-a1 after the fence is gone.
```

## f2-inst-01-l005

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l005` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 5, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L005`, 256 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l004` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l005-a1 after the fence is gone.
```

## f2-inst-01-l006

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l006` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 6, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L006`, 19,458 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l005` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l006-a1 after the fence is gone.
```

## f2-inst-01-l007

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l007` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 7, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L007`, 256 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l006` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l007-a1 after the fence is gone.
```

## f2-inst-01-l008

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l008` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 8, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L008`, 2,000 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l007` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l008-a1 after the fence is gone.
```

## f2-inst-01-l009

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l009` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 9, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L009`, 19,458 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l008` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l009-a1 after the fence is gone.
```

## f2-inst-01-l010

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l010` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 10, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L010`, 2,000 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l009` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l010-a1 after the fence is gone.
```

## f2-inst-01-l011

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l011` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 11, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L011`, 19,458 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l010` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l011-a1 after the fence is gone.
```

## f2-inst-01-l012

TBD. **Laptop lead, drafted by Sol 6.2. ISSUED <LOCAL ISSUE TIMESTAMP FROM DATE>. MAGISTRATE: arm only `f2-inst-01-l012` under items 418 (d) and 422, kit `f2-inst-01.v1.1.json` (SHA-256 `651d1815ca87ee23640a8db1483d4ecaf42d70d029855ad03c14bfa076116f2b`), queue `cq-f2-inst-01` seq 12, attempt 1, runner `cadence-legs-v1.1` at `2d347f721552fe03bdd19f113e7bad7a7c24908e`. Roster `L012`, 256 prompt tokens, own G0, q600, decode cap 512, Automatic. Fresh soak, one leg, worst case 5,850 s. Rank 2.**

```pointer
owner: magistrate
wait: none
deadline: <CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: Keep unarmed until same-kit predecessor `f2-inst-01-l011` has a clean Check. VOID this item if that predecessor closes unclean. On launcher refusal, record it and hold this kit until an input changes under F-6. This item authorizes one launch.
next_observable: operational Check for cq-f2-inst-01-l012-a1 after the fence is gone.
```
