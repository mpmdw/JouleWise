# Re-harvest of the retained 09-16 plan root `d079-epoch-25g83-derivation-n1-20260916` (2026-09-18 19:56 PDT, bench)

Trigger: arm record 21 (activation d8ca3a36) found `~/night-archive/d079-epoch-25g83-derivation-n1-20260916-harvest-20260916/` EMPTY while its sibling `…SHA256SUMS` listed 20 files and its sibling lstat inventory 25 entries; the byte-copy step of the 09-16 harvest never landed. The live root under `~/night-custody/` is production custody (the night opened a ledger session) and is RETAINED; nothing in it was moved or modified.

## Executed (one bench chain, 19:56:08 → 19:56:11 PDT)

1. Guard: the archive directory existed and was empty (else abort).
2. Live root checked against the sibling sums BEFORE copying: `shasum -a 256 -c` → 20 OK, 0 non-OK.
3. `cp -Rp <root>/. <archive>/` rc 0 (249 MB including `results-clone/`).
4. Copy checked against the sibling sums: 20 OK, 0 non-OK.
5. `SHA256SUMS` written INSIDE the archive (every regular file, `results-clone/` excluded, same scope as the sibling): 20 lines, self-check 0 non-OK; the entry set is byte-identical to the sibling sums (sorted diff empty).
6. lstat inventories in the 09-17 format (`size mtime.ns ./path`, `results-clone/` excluded) taken from the live root and from the copy: regular-file rows IDENTICAL (directory rows differ only by the archive's added `SHA256SUMS` and the directory mtimes that `cp -Rp` does not preserve).

Evidence: `01-harvest-0916-evidence/` (both inventories, the archive's `SHA256SUMS`, the sibling sums).

## Queue data (registration seat)

- The 09-16 re-harvest finding in arm record 21 is closed; the root may be retired under NIGHT-ROOT-RETENTION-DISCOVERY-01 when that lane rules, with the archive now complete.
- Inventory format still differs between 09-16 (`path size mtime mode`, 25 rows incl. directories) and 09-17 (`size mtime.ns ./path`, files only); the retirement script assumes the 09-17 format — a status note, not a fix.
