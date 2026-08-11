# D-117 v2 production-path fixture

This fixture anchors the issued D-079 acceptance bytes, the exact 76-receipt
authenticated ledger prefix, and its 38 content-addressed five-artifact
custody trees. The content directories are hydrated working data from the
digest-pinned release asset named by `transport_descriptor.json`; they are not
Git authority. Tests copy this seed into a temporary clean Git repository,
place mutable campaign evidence outside that repository, append fresh
finalized pre/post bracket sessions with the production ledger writer, extend
the custody store by the resulting content IDs, and commit the terminal head
pin before invoking the unpatched generalized v2 CLI.

`custody_store/manifest.json` is derived from the ledger; it is not an
authority for content IDs or artifact hashes. The packager verifies every
hydrated custody member against that census, and the production loader derives
and verifies the complete 190-member projection from the authenticated ledger.
Ordinary shards explicitly skip the full proof when the store is absent; the
required `d117-production-proof` workflow hydrates it and forbids that skip.
