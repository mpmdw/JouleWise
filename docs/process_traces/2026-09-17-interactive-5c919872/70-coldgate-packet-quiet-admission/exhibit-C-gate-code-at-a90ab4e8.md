# Exhibit C — the night gate as it stands, `joulewise/night_gate.py` at commit `a90ab4e8`

Every block is `sed -n '<range>p' joulewise/night_gate.py | nl -ba -v<start>`
output from this checkout at `a90ab4e8`: the leading integer on each line IS
the file's line number. No line has been edited, reordered or elided inside a
fence. The judge can reproduce any block with the same command.

## C1 — schema identifiers (lines 22–30)

```
    22	SCHEMA = "joulewise.unattended_night_receipt.v2"
    23	PLAN_SCHEMA = "joulewise.night_plan.v2"
    24	PLAN_SCHEMA_VERSION = 2
    25	PACK_PLAN_SCHEMA = "joulewise.night_plan.v3"
    26	PACK_PLAN_SCHEMA_VERSION = 3
    27	RECEIPT_CLASSES = (
    28	    "DIAGNOSTIC_NO_PACK",
    29	    "REHEARSAL_STUB",
    30	    "TRANSACTION_PACK",
```

Bearing on proposition 8: `v3` is already taken by the transaction-pack plan.

## C2 — the probe argument vectors and `LOAD_MAX` (lines 40–58)

```
    40	    "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
    41	)
    42	AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")
    43	
    44	PMSET_BATT_ARGV = ("/usr/bin/pmset", "-g", "batt")
    45	PMSET_GENERAL_ARGV = ("/usr/bin/pmset", "-g")
    46	HID_IDLE_ARGV = (
    47	    "/usr/bin/defaults",
    48	    "-currentHost",
    49	    "read",
    50	    "com.apple.screensaver",
    51	    "idleTime",
    52	)
    53	LOAD_AVG_ARGV = ("/usr/sbin/sysctl", "-n", "vm.loadavg")
    54	THERMAL_ARGV = ("/usr/bin/pmset", "-g", "therm")
    55	BOOT_SESSION_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")
    56	
    57	LOAD_MAX = 2.0
    58	PLAN_MAX_AGE_S = 36 * 60 * 60
```

`LOAD_MAX` is a module constant at line 57: it is code, not plan data, and no
plan field can change it today. `HID_IDLE_ARGV` (lines 46–52) reads the
screensaver's configured `idleTime` default, not a live idle timer — bearing on
the consult's first correction and on proposition 6.

## C3 — the injected probe surface and the plan dataclass (lines 179–221)

```
   179	@dataclass(frozen=True)
   180	class Probes:
   181	    run: Callable[[tuple[str, ...]], ProbeResult]
   182	    now_epoch_s: Callable[[], float]
   183	    monotonic_ns: Callable[[], int]
   184	    read_text: Callable[[str], str]
   185	    checkout_head: Callable[[], str]
   186	    measurement_head: Callable[[str], str]
   187	
   188	
   189	class CensusProbes(Protocol):
   190	    """Narrow census dependency, isolated from unrelated plan-pin probes."""
   191	
   192	    run: Callable[[tuple[str, ...]], ProbeResult]
   193	    monotonic_ns: Callable[[], int]
   194	
   195	
   196	@dataclass(frozen=True)
   197	class NightPlan:
   198	    plan_id: str
   199	    receipt_class: str
   200	    t0_epoch_s: float
   201	    window_max_s: int
   202	    authored_epoch_s: float
   203	    repo_head: str
   204	    measurement_root: str
   205	    measurement_head: str
   206	    chain_path: str
   207	    chain_sha256_path: str
   208	    custody_root: str
   209	    registration_path: str | None
   210	    pack_night: dict[str, object] | None = None
   211	
   212	    @staticmethod
   213	    def from_mapping(value: Mapping[str, object]) -> "NightPlan":
   214	        if not isinstance(value, Mapping):
   215	            raise PlanError("night_plan_malformed", "plan must be an object")
   216	        keys = set(value)
   217	        is_pack = value.get("receipt_class") == "TRANSACTION_PACK"
   218	        expected_keys = _PLAN_KEYS | {"pack_night"} if is_pack else _PLAN_KEYS
   219	        expected_schema = PACK_PLAN_SCHEMA if is_pack else PLAN_SCHEMA
   220	        expected_version = PACK_PLAN_SCHEMA_VERSION if is_pack else PLAN_SCHEMA_VERSION
   221	        if keys != expected_keys:
   222	            missing = sorted(repr(item) for item in expected_keys - keys)
   223	            extra = sorted(repr(item) for item in keys - expected_keys)
```

Line 221 is an EXACT key-set equality: a plan carrying an extra
`quiet_admission` key under the v2 schema is refused `night_plan_malformed`.
This is the mechanical reason the consult proposes a new schema id rather than
an optional field. Bearing on proposition 8.

## C4 — `evaluate_night`'s entry, one shot (lines 947–975)

```
   947	def evaluate_night(plan: NightPlan, probes: Probes, *, pack_arm_receipt=None, pack_conditions=None) -> Receipt:
   948	    # Retained compatibility argument has no authority; custody is re-evaluated.
   949	    del pack_conditions
   950	    pack_arm = None
   951	    rows = _initial_conditions(plan.receipt_class)
   952	    evidence: list[ProbeResult] = []
   953	
   954	    if (
   955	        plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}
   956	        and (not isinstance(plan.registration_path, str) or not plan.registration_path)
   957	    ):
   958	        return _finish(
   959	            plan,
   960	            probes,
   961	            rows,
   962	            Refusal(
   963	                "night_plan_malformed",
   964	                "registration_path must be a non-empty string for this receipt class",
   965	                (),
   966	            ),
   967	        )
   968	
   969	    # R-6: missed-fire guard.  No command or filesystem probe precedes it.
   970	    try:
   971	        now_epoch_s = float(_clock_value(probes, "epoch"))
   972	    except ProbeError as exc:
   973	        return _probe_refusal(plan, probes, rows, evidence, exc)
   974	    rows["C5"].measured = {
   975	        "t0_epoch_s": plan.t0_epoch_s,
```

The function has no loop and no deadline parameter: every predicate below is
evaluated once, in order, and the first failure returns.

## C5 — the screensaver-configuration probe (lines 1138–1150)

```
  1138	    # R-6's unattended HID predicate precedes the remaining quiet predicates.
  1139	    try:
  1140	        hid = _run(probes, HID_IDLE_ARGV)
  1141	    except ProbeError as exc:
  1142	        return _probe_refusal(plan, probes, rows, evidence, exc)
  1143	    evidence.append(hid)
  1144	    rows["C3"].evidence.append(_probe_citation(hid))
  1145	    rows["C3"].measured["hid_idle_raw"] = hid.stdout
  1146	    if not _completed_ok(hid) or hid.stdout.strip() != "0":
  1147	        return _finish(
  1148	            plan,
  1149	            probes,
  1150	            rows,
```

The predicate is `stdout.strip() != "0"` on the screensaver `idleTime`
DEFAULT read at line 46–52: a configuration value, not an observation of user
activity.

## C6 — the four `night_refused_not_quiet` sites, and thermal (lines 1160–1255)

```
  1160	        batt = _run(probes, PMSET_BATT_ARGV)
  1161	        evidence.append(batt)
  1162	        rows["C3"].evidence.append(_probe_citation(batt))
  1163	        rows["C3"].measured["ac_power_raw"] = batt.stdout
  1164	        if not _completed_ok(batt) or "AC Power" not in batt.stdout:
  1165	            return _finish(
  1166	                plan,
  1167	                probes,
  1168	                rows,
  1169	                Refusal(
  1170	                    "night_refused_not_quiet",
  1171	                    "ac_power",
  1172	                    tuple(evidence),
  1173	                ),
  1174	            )
  1175	
  1176	        settings = _run(probes, PMSET_GENERAL_ARGV)
  1177	        evidence.append(settings)
  1178	        rows["C3"].evidence.append(_probe_citation(settings))
  1179	        rows["C3"].measured["pmset_g_raw"] = settings.stdout
  1180	        display_match = _DISPLAY_SLEEP_RE.search(settings.stdout)
  1181	        rows["C3"].measured["displaysleep"] = (
  1182	            None if display_match is None else display_match.group(1)
  1183	        )
  1184	        if not _completed_ok(settings) or display_match is None:
  1185	            return _finish(
  1186	                plan,
  1187	                probes,
  1188	                rows,
  1189	                Refusal(
  1190	                    "night_refused_not_quiet",
  1191	                    "displaysleep predicate failed",
  1192	                    tuple(evidence),
  1193	                ),
  1194	            )
  1195	
  1196	        load = _run(probes, LOAD_AVG_ARGV)
  1197	        evidence.append(load)
  1198	        rows["C3"].evidence.append(_probe_citation(load))
  1199	        rows["C3"].measured["load_average_raw"] = load.stdout
  1200	        load_match = _LOAD_AVG_RE.fullmatch(load.stdout.strip())
  1201	        if not _completed_ok(load) or load_match is None:
  1202	            raise ProbeError(
  1203	                "load average output malformed: "
  1204	                f"exit={load.exit_code}, stdout={load.stdout[:200]!r}"
  1205	            )
  1206	        load_1m = float(load_match.group(1))
  1207	        rows["C3"].measured["load_1m"] = load_1m
  1208	        if load_1m > LOAD_MAX:
  1209	            return _finish(
  1210	                plan,
  1211	                probes,
  1212	                rows,
  1213	                Refusal(
  1214	                    "night_refused_not_quiet",
  1215	                    f"load_average predicate failed (maximum {LOAD_MAX})",
  1216	                    tuple(evidence),
  1217	                ),
  1218	            )
  1219	
  1220	        thermal = _run(probes, THERMAL_ARGV)
  1221	        evidence.append(thermal)
  1222	        rows["C3"].evidence.append(_probe_citation(thermal))
  1223	        rows["C3"].measured["thermal_raw"] = thermal.stdout
  1224	        thermal_limits: list[str] = []
  1225	        for thermal_line in thermal.stdout.splitlines():
  1226	            stripped_line = thermal_line.strip()
  1227	            if not stripped_line.startswith("CPU_Speed_Limit"):
  1228	                continue
  1229	            thermal_match = _THERMAL_RE.fullmatch(stripped_line)
  1230	            if thermal_match is None:
  1231	                raise ProbeError(
  1232	                    f"thermal output malformed: {thermal.stdout[:200]!r}"
  1233	                )
  1234	            thermal_limits.append(thermal_match.group(1))
  1235	        thermal_limit = thermal_limits[0] if thermal_limits else None
  1236	        rows["C3"].measured["cpu_speed_limit"] = thermal_limit
  1237	        if not _completed_ok(thermal):
  1238	            raise ProbeError(
  1239	                f"thermal probe exit {thermal.exit_code}: {thermal.stdout[:200]!r}"
  1240	            )
  1241	        if any(limit != "100" for limit in thermal_limits):
  1242	            return _finish(
  1243	                plan,
  1244	                probes,
  1245	                rows,
  1246	                Refusal(
  1247	                    "night_refused_not_quiet",
  1248	                    "thermal predicate failed",
  1249	                    tuple(evidence),
  1250	                ),
  1251	            )
  1252	    except ProbeError as exc:
  1253	        return _probe_refusal(plan, probes, rows, evidence, exc)
  1254	    rows["C3"].status = "PASS"
  1255	    rows["C3"].measured["detail"] = "agent, HID, AC, display, load, and thermal predicates passed"
```

Four `Refusal("night_refused_not_quiet", ...)` constructions appear at lines
1169–1174 (AC power), 1189–1194 (display sleep), 1213–1218 (load average) and
1246–1251 (thermal). One reason code carries four distinct physical causes.

Thermal semantics relevant to proposition 6: `thermal_limits` (line 1224) is
built only from lines starting `CPU_Speed_Limit`; if `pmset -g therm` emits no
such line the list is empty, `any(...)` over an empty list is `False`, and the
predicate PASSES. This is the consult's second correction.

## C7 — receipt validation entry (lines 1373–1385)

```
  1373	def validate_receipt(value: Mapping[str, object]) -> list[str]:
  1374	    defects: list[str] = []
  1375	    if not _exact_keys(value, _RECEIPT_KEYS, "receipt", defects):
  1376	        return defects
  1377	    if value.get("schema") != SCHEMA:
  1378	        defects.append(f"schema: must be {SCHEMA}")
  1379	    receipt_class = value.get("receipt_class")
  1380	    if receipt_class not in RECEIPT_CLASSES:
  1381	        defects.append("receipt_class: is not registered")
  1382	        defects.append("night_receipt_class_invalid: unknown receipt_class")
  1383	        class_rules = None
  1384	    else:
  1385	        class_rules = class_table()[receipt_class]
```

`_exact_keys` at line 1375 and the single-valued `SCHEMA` check at line 1377
are why new receipt fields require a new receipt schema id (proposition 8).
