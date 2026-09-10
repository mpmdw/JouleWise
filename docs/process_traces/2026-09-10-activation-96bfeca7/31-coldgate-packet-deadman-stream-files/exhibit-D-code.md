# Exhibit D — driver dead_man and installer render (58d4696b)
```python
def dead_man(plan_path: Path, *, courier_bin: Path | None = None) -> int:
    try:
        plan = _load_plan(plan_path)
    except (OSError, ValueError, TypeError, PlanError) as error:
        return _malformed_plan_exit(plan_path, error, courier_bin)
    custody_root = Path(plan.custody_root)
    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    sent = night_dir / "courier.sent"
    if sent.exists():
        _fsync_path(sent)
        _append_log(custody_root, "dead-man skipped: courier already sent")
        return EXIT_GO
    completion_epoch_s = _completion_epoch_s(plan)
    if time.time() < completion_epoch_s:
        _append_log(
            custody_root,
            "dead-man fired before the night's completion epoch "
            f"{int(completion_epoch_s)}; standing down",
        )
        return EXIT_GO

    resolved_courier, courier_error, courier_substitution = _resolve_courier_bin(
        courier_bin
    )
    _record_courier_substitution(custody_root, courier_substitution)
    if _courier_lock_is_live(night_dir):
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            _CODES["courier_running"],
            "a fresh courier lock belongs to a live process",
        )
        _append_log(custody_root, "dead-man refused while courier was running")
```
```sh
    text = text.replace(old, new)
Path(output).write_text(text, encoding="utf-8")
PY
}

night_label="com.joulewise.night"
deadman_label="com.joulewise.night.deadman"
night_plist="$launch_dir/$night_label.plist"
deadman_plist="$launch_dir/$deadman_label.plist"
if [[ -z "$render_only" ]]; then
  if [[ "$launchctl_bin" != */* ]]; then
    launchctl_bin="$(command -v "$launchctl_bin" || true)"
  fi
  [[ -n "$launchctl_bin" && -x "$launchctl_bin" ]] || {
    print "launchctl executable not found" >&2
    exit 2
  }
  launchctl_bin="${launchctl_bin:A}"
fi
if (( uninstall )); then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  "$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  rm -f "$night_plist" "$deadman_plist"
  exit 0
fi

existing_night_records=()
for record in receipt.json result.json refusal.json chain.started chain.exited courier.json courier.sent; do
  # -L too: a dangling symlink is still a record name the run path would trip on.
  [[ -e "$custody_root/night/$record" || -L "$custody_root/night/$record" ]] && existing_night_records+=("$record")
done
if (( ${#existing_night_records[@]} )); then
  print "refusing install: existing night records: ${existing_night_records[*]}" >&2
  exit 3
fi

render "$night_label" run "$night_plist" "$hour" "$minute" "launchd.night"
render "$deadman_label" dead-man "$deadman_plist" "$deadman_hour" "$deadman_minute" "launchd.deadman"
if [[ -n "$render_only" ]]; then
  print "validated pins: repo_head=$plan_head measurement_root=$measurement_root measurement_head=$plan_measurement_head"
  exit 0
fi

"$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
"$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
if ! "$launchctl_bin" bootstrap "gui/$uid" "$night_plist"; then
  print "failed to bootstrap $night_label" >&2
  exit 3
fi
if ! "$launchctl_bin" bootstrap "gui/$uid" "$deadman_plist"; then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  print "failed to bootstrap $deadman_label; rolled back $night_label" >&2
  exit 3
fi
if ! "$launchctl_bin" print "gui/$uid/$night_label" || \
   ! "$launchctl_bin" print "gui/$uid/$deadman_label"; then
  "$launchctl_bin" bootout "gui/$uid/$night_label" 2>/dev/null || true
  "$launchctl_bin" bootout "gui/$uid/$deadman_label" 2>/dev/null || true
  print "launch agent verification failed; rolled back both agents" >&2
  exit 3
fi
```
