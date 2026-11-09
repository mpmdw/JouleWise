**HOLD:** `effective_desk` can upgrade a mismatched desk containing a real exclusion. Committed synthetic evidence passes both packet preflight and the arm rebuild.

Only [R11-DELTA7-sol.md](/Volumes/JW-EXT/jw-wt/sol-r11-delta7-sol/docs/align/v4/R11-DELTA7-sol.md) changed.

- All 150 targeted tests pass.
- Measurement-core changes are timing-receipts-only; manifest SHA remains `21313cc2…`.
- Commit: `c923411a7` on `align/2026-11-08-r11-delta7-sol`.
- Tree clean; nothing pushed.
- Python 3.11 and native hardware remain unverified. Two short checks briefly overlapped and were rerun serially.

Next: repair desk/harvest reconciliation and rerun the report’s refusal witness.