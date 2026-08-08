# D-117 v2 production-path fixture

This fixture anchors the issued D-079 acceptance bytes, the exact 76-receipt
authenticated ledger prefix, and its 38 content-addressed five-artifact
custody trees. Tests copy this seed into a temporary clean Git repository,
place mutable campaign evidence outside that repository, append fresh
finalized pre/post bracket sessions with the production ledger writer, extend
the custody store by the resulting content IDs, and commit the terminal head
pin before invoking the unpatched generalized v2 CLI.

`custody_store/manifest.json` is derived from the ledger; it is not an
authority for content IDs or artifact hashes. Every checked-in custody member
was SHA-256 verified against its finalization receipt before copying.
