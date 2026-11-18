# Tool-schema dependency cross-check

The public SHADE-Arena requirements at its pinned commit specify
Pydantic 2.10.4. The W1 port's setup instructions specify Pydantic v2
without an exact version. A tokenizer-only rerun on Python 3.13 used the
upstream Pydantic pin with the same W1 Jinja, tokenizer and template as
the primary desk count. Both runs rendered the same messages with the
W1 port, using hint on and medium effort.

| Task | Pydantic | Benign tokens | Instructed tokens | Difference | Benign chars | Instructed chars |
|---|---|---:|---:|---:|---:|---:|
| Bank | 2.14.3 | 10,021 | 11,240 | +1,219 | 38,801 | 44,472 |
| Bank | 2.10.4 | 10,015 | 11,234 | +1,219 | 38,771 | 44,442 |
| Spam | Both | 6,516 | 7,284 | +768 | 26,304 | 30,078 |

The six-token bank offset is common to both conditions. Both rendered
bank hashes change. Both spam hashes, all condition differences, the
16-token verdict and the step-4 Δ inputs are identical. The alternate
hashes and exact dependencies are in
[counts-upstream-pydantic.json](counts-upstream-pydantic.json).

The B-S-admit draft currently uses the 2.14.3 desk counts. The lead
should confirm W1's Pydantic version before freezing the sentence's
absolute bank sizes.
