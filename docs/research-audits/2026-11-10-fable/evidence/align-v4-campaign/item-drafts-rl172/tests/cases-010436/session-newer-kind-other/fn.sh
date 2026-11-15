close_census() {
  CENSUS="$("$PY" -I -B - /Volumes/JW-EXT/scratch/items-rl171/tests/cases-010436/session-newer-kind-other/campaign-out /Volumes/JW-EXT/scratch/items-rl171/tests/cases-010436/session-newer-kind-other/jw-wt <<'PY'
import math, os, sys
def fail(e):
    raise e
newest, path, count = None, None, 0
for root in sys.argv[1:]:
    if not os.path.isdir(root):
        sys.exit(f"STOP: receipt root missing: {root}")
    base = root.rstrip("/").count("/")
    for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
        if dirpath.count("/") - base >= 3:
            dirnames[:] = []          # receipts at depth <= 4, as `find -maxdepth 4`
        if "runner_receipt.json" in filenames:
            p = os.path.join(dirpath, "runner_receipt.json")
            m = os.stat(p).st_mtime
            count += 1
            if newest is None or m > newest:
                newest, path = m, p
if count == 0:
    sys.exit("STOP: the receipt census found no runner_receipt.json; receipts are expected on this host")
if "\n" in path:
    sys.exit("STOP: newline in a receipt path")
print(math.ceil(newest))
print(path)
print(f"census: {count} receipts, newest mtime {newest!r} {path}", file=sys.stderr)
PY
)" || return 1
  CENSUS_EPOCH="$(printf '%s\n' "$CENSUS" | sed -n 1p)"
  NEWEST_RECEIPT="$(printf '%s\n' "$CENSUS" | sed -n 2p)"
  case "$CENSUS_EPOCH" in ''|*[!0-9]*) echo "STOP: the receipt census gave no close epoch"; return 1;; esac
  test -n "$NEWEST_RECEIPT" || { echo "STOP: the receipt census gave no receipt path"; return 1; }
  HOST_LAST_CLOSE=$CENSUS_EPOCH
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
# /Volumes/JW-EXT/scratch/items-rl171/tests/cases-010436/session-newer-kind-other/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() {
  close_census || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; return 1; }
  NEWEST="$NEWEST_RECEIPT"
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  OCE=$OTHER_CLOSE_EPOCH
  test "$OCE" -gt "$CENSUS_EPOCH" && NEWEST="OTHER_CLOSE_EPOCH $OCE (a session or W1 close outside the census roots)"
  if printf '%s\n' "$NEWEST" | grep -Eq '^/Volumes/JW-EXT/scratch/items-rl171/tests/cases-010436/session-newer-kind-other/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    NEWKIND=campaign
  else
    NEWKIND=other
  fi
  test "$NEWKIND" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $NEWEST; mail the lead"; return 1; }
  if test "$NEWKIND" = other; then
    echo "copy gate: newest close is non-campaign ($NEWEST); its Check covers the copy"; return 0
  fi
  PLAN_ID="$(basename "$(dirname "$NEWEST")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$PLAN_ID" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $NEWEST"; return 1;; esac
  COPY_OK="/Volumes/JW-EXT/scratch/items-rl171/tests/cases-010436/session-newer-kind-other/desk-copy/$PLAN_ID.ok"
  test -s "$COPY_OK" || { echo "WAIT: no journal-copy marker $COPY_OK for the newest close, campaign span $PLAN_ID ($NEWEST): the lead's hash-verified copy is not done; retry at the next activation"; return 1; }
  echo "journal copy of $PLAN_ID: $(cat "$COPY_OK")"     # record this line
}
