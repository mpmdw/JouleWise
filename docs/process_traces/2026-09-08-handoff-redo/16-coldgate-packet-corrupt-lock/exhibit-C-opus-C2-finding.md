C2 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:157,181`: the documented step-4 reconciliation can NEVER clear
a corrupt/unparseable `magistrate.lock`: `read_lock` returns `{}` (`:838-840`), `handoff_census` maps `{}` →
`handoff_lock_invalid` (`:936-938`), the block raises `handoff_lock_not_clear`; the installer's exclusive seed
refuses while any lock file exists, so a corrupt lock blocks install with no documented recovery. Cure: let step 4
clear a `{}`/corrupt lock when no owned/twin process is live (fail-closed if any is), with a regression, or document
an explicit alternative command.

C3 should-fix — `docs/process/MAGISTRATE_WATCHDOG.md:190`: "Resolve that process explicitly before clearing the
