# DF-TELEM-ONOFF unavailable

No runnable config is emitted here. The current config schema cannot select the extra `tasks` sampler, and the powermetrics adapter uses the fixed sampler set `cpu_power,gpu_power,ane_power,thermal`. Running a normal-telemetry alias as B would not measure telemetry perturbation. The current-hardware layer and C-015/R2 smoke therefore remain unsatisfied; its floor is `unknown`.
