"""L9-ENV-5-OPUS-REV: reviewer mutants on the flag plumbing (applied in /tmp worktrees only)."""
WW = "joulewise/whole_window.py"
PICK = "            _rederive_operative_summary\n            if self.analysis_clamp\n"
OWN = {
 "R-M1_flag_ignored_with_archive_context": [(WW, PICK,
   "            _rederive_operative_summary\n            if self.analysis_clamp and self._archive_context is None\n")],
 "R-M2_flag_ignored_in_read_replay": [(WW, PICK,
   "            _rederive_operative_summary\n            if self.analysis_clamp and self.mode != \"read_replay\"\n")],
}
