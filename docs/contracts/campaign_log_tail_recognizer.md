# Campaign-log torn-tail recognizer

Status: implementation contract for `C3-RECOGNIZER-EXACT-01`, governed by
[D-105](../decision_log.md) and the row's
[acceptance criteria](../process/state_kernel.json).

The campaign log uses JSON Lines: one JavaScript Object Notation object per
line. A crash can leave the final line incomplete. The reader may classify
that final byte sequence as a *torn prefix* only when at least one completion
belongs to the writer grammar described here. The classification permits the
append path to preserve the torn bytes in a sidecar file and then truncate the
log. It does not make the incomplete bytes scientific evidence.

## Forcing problem

The writer sorts object keys by their decoded Python strings but writes
non-ASCII characters as `\u` escapes. A byte prefix can therefore end before
the decoded character is known. In particular, the completed escape
`\ud83d` can be the high-surrogate half of a later non-Basic-Multilingual-Plane
character. Comparing that half as though it were a finished character can
falsely reject a real writer prefix.

A completed `\ud800\udc00` spelling is ambiguous too: it can come from one
non-Basic-Multilingual-Plane scalar or from two literal Python surrogate code
units. Those originals sort differently even though `json.dumps` emits the
same bytes. The recognizer therefore carries every feasible decoded original
through the key-order comparison instead of collapsing the spelling through
`json.loads`.

The number problem is different. Python chooses a shortest round-trip decimal
for each finite floating-point value. Deciding the exact image of that
algorithm inside a small incremental parser is the failed requirement struck
by D-105. An unconstrained decimal heuristic, however, accepts prefixes that
no writer spelling can complete. The parser therefore needs a finite,
documented superset: a grammar that can admit extra spellings but still
contains every real writer spelling.

## Options and ruling

1. Decode only complete escapes and compare that decoded prefix. This is
   small, but it loses the possible scalar represented by a high/low surrogate
   pair and caused the escaped-key blocker.
2. Enumerate possible suffix strings or reproduce Python's shortest-decimal
   selection. This seeks exactness at unnecessary and unbounded cost; D-105
   struck that requirement for numbers.
3. Carry an interval for the first unfinished escaped character and recognize
   a decidable numeric superset. This is the D-105 recommendation implemented
   by `joulewise.campaign_provenance`.

## Escaped-key completion rule

An unfinished `\u` escape denotes the hexadecimal interval obtained by
filling its missing digits with the lowest and highest hexadecimal digits.
That interval is intersected with the code units that `json.dumps` emits as
Unicode escapes. If it intersects the high-surrogate range, the upper bound is
lifted through the standard high-surrogate/low-surrogate arithmetic. If a high
surrogate is already complete and the following low-surrogate escape is only
partial, the interval is applied to that low surrogate instead.

Key ordering then uses the first position that is not already fixed:

- an earlier unequal decoded character decides the result;
- when the fixed decoded text equals the corresponding previous-key prefix,
  a completion is feasible if the pending character's maximum is at least the
  previous character at that position; and
- when the raw prefix ends at a character boundary, it can reproduce the rest
  of the previous key and append one more character.

This is an existential rule: it asks whether *some* canonical completion can
sort after the previous key. Later characters cannot repair an earlier
strictly smaller character. When a completed surrogate-pair spelling has more
than one feasible Python original, every still-orderable alternative is
retained for the next key rather than choosing one greedily.

## Finite-float superset

The exact integer spellings and the special floating-point literals `NaN`,
`Infinity`, and `-Infinity` are handled separately. A finite floating-point
spelling in the superset has an optional minus sign and one of these forms:

- fixed zero: `0.0`;
- fixed below one: `0.` followed by a first nonzero digit within the fixed
  exponent window and then decimal digits;
- fixed at least one: one to sixteen digits before the decimal point and at
  least one digit after it; or
- scientific: one nonzero digit, an optional decimal fraction ending in a
  nonzero digit, `e`, a required sign, and a two- or three-digit exponent.

Scientific negative exponents begin beyond the fixed lower boundary;
scientific positive exponents begin beyond the fixed upper boundary. A
single-digit negative exponent is accepted only as a prefix that can acquire
its required leading zero. A four-digit exponent, a non-normalized scientific
coefficient, and a fixed value whose first nonzero fractional digit lies
outside the fixed window refuse.

The grammar intentionally does not decide whether a permitted coefficient is
the shortest representation of a particular binary value. That is the
documented over-approximation allowed by D-105.

## Worked examples

After the key `\ue000`, the prefix ending in `\ud83d` remains feasible: the
unfinished key can add a low surrogate and become the non-Basic-Multilingual-
Plane key represented by `\ud83d\ude00`, which sorts later. The old decoded-only
comparison saw only the high surrogate and refused.

For numbers, `1e+10` remains feasible because one more digit can produce a
three-digit scientific exponent. `1e+1000` refuses because the exponent has
already exceeded the grammar's maximum width. Likewise, `0.000` can still add
a nonzero digit inside the fixed window, while `0.0000` cannot.

## Proof obligations

The focused tests enforce both directions of the amended acceptance contract:

- every accepted torn tail is shaped as a prefix of this documented grammar;
- every proper prefix of the deterministic `json.dumps(..., sort_keys=True)`
  writer corpus is accepted, including escaped non-Basic-Multilingual-Plane
  keys and randomized floating-point bit patterns; and
- the registered escaped-key and numeric over-acceptance counterexamples are
  pinned as literal bytes.

The existing preserve-before-truncate sidecar and recursive ASCII-only writer
key assertion remain separate, load-bearing custody controls under D-105.
