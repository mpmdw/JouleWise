# CGV-HARDEN-01: validator-receipt publication boundary

## Scope

This design covers durable storage of the cold-gate validator's canonical
receipt bytes. It does not cover delivery of validated packet bytes to a
judge. That separate concern remains owned by `COLDGATE-HANDOFF-01`.

## Forcing problem

The validator now emits its receipt only on standard output. A future
convening runner must store those exact bytes. A path-based sequence such as
“check directory, write temporary file, replace final path” has a
time-of-check-to-time-of-use race: another process can replace the named
directory after the check and redirect the write. Writing the final file
directly avoids that redirect only at the cost of exposing partial bytes after
a crash. A completed write is not durable until both the file and the parent
directory have been synchronized with the storage system.

## Options

1. Write the final path directly with exclusive creation. This prevents an
   overwrite but can expose a truncated receipt and does not close directory
   replacement.
2. Write a temporary path and replace the final path. This gives atomic
   visibility but path-based operations remain redirectable, and replacement
   silently overwrites an existing receipt.
3. Open the receipt directory once, then perform every operation relative to
   that open directory descriptor. Fully write and synchronize a private
   temporary file, publish it with an atomic no-overwrite hard link, remove the
   temporary name, then synchronize the directory. This prevents redirection,
   partial publication, and overwrite.

## Recommendation

Use option 3. `joulewise.coldgate_receipt.persist_validator_receipt` implements
that boundary. It fails closed when the path no longer names the directory
that was opened. A file-synchronization failure leaves no published receipt.
A directory-synchronization failure is reported as durability-uncertain,
because a complete final name is already visible but survival across a crash
has not been proved.

The missing convening runner is a separate integration decision. The future
runner should pass the exact validator standard-output bytes to this function
and treat every exception as non-success. Selecting that runner's file, command
line, receipt directory, and naming rule would create an interface not fixed by
the current row or its cited rulings; the lead must settle those choices when
the runner is introduced.

## Worked example

For a requested `validation.json`, the function opens the existing receipt
directory without following a symbolic link. It creates a private temporary
entry relative to the resulting directory descriptor, writes the validator's
bytes, and synchronizes the file. It then creates `validation.json` as a hard
link to that complete file. The operation fails if that name already exists.
After removing the temporary name, it synchronizes the same open directory.
Only then does it return the byte count and SHA-256 digest of the bytes that
were stored.
