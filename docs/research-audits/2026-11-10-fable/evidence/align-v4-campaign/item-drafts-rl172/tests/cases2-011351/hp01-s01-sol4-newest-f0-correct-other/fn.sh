close_census() {
  CENSUS="$("$PY" -I -B - /Volumes/JW-EXT/scratch/items-rl171/tests/cases2-011351/hp01-s01-sol4-newest-f0-correct-other/campaign-out /Volumes/JW-EXT/scratch/items-rl171/tests/cases2-011351/hp01-s01-sol4-newest-f0-correct-other/jw-wt <<'PY'
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
}
# The effective close, computed ONCE per gate (Sol confirm P1): max of the census and OTHER_CLOSE_EPOCH, with its path or label.
# The host gate's GAP and copy_gate's kind check both use EFF_EPOCH / EFF_PATH from the same call.
effective_close() {
  case "${OTHER_CLOSE_EPOCH:-}" in ''|*[!0-9]*) echo "STOP: OTHER_CLOSE_EPOCH must be a whole epoch (rounded up) of a session/W1 close, or an explicit 0"; return 1;; esac
  close_census || return 1
  EFF_EPOCH=$CENSUS_EPOCH; EFF_PATH="$NEWEST_RECEIPT"
  if test "$OTHER_CLOSE_EPOCH" -gt "$CENSUS_EPOCH"; then
    EFF_EPOCH=$OTHER_CLOSE_EPOCH; EFF_PATH="OTHER_CLOSE_EPOCH $OTHER_CLOSE_EPOCH (a session or W1 close outside the census roots)"
  fi
}
# Sol items-rl171 P1 and Sol RL-172 re-check 1: the newest close of anything (the census above, or OTHER_CLOSE_EPOCH for a
# session/W1 close outside its roots) must agree with LAST_CLOSE_KIND. After a CAMPAIGN close, that receipt's journal copy must be
# complete and hash-verified on the Air: the lead copies by SSH, verifies, and only then writes
# /Volumes/JW-EXT/scratch/items-rl171/tests/cases2-011351/hp01-s01-sol4-newest-f0-correct-other/desk-copy/<plan-id>.ok (the copy manifest's sha256 and a `date` stamp). No SSH once a span is armed.
# A marker is only ever derived from a campaign receipt path; after a Part C, F0, F2, session or W1 close the Check covers the copy.
copy_gate() (   # a subshell: it reads EFF_PATH (from effective_close) and LAST_CLOSE_KIND and changes nothing the host gate reads
  test -n "${EFF_PATH:-}" || { echo "STOP: copy_gate needs effective_close first"; exit 1; }
  if printf '%s\n' "$EFF_PATH" | grep -Eq '^/Volumes/JW-EXT/scratch/items-rl171/tests/cases2-011351/hp01-s01-sol4-newest-f0-correct-other/campaign-out/cl-[a-z0-9-]+/cq-[a-z0-9-]+-a[0-9]+-[0-9]{8}T[0-9]{6}Z/runner_receipt\.json$'; then
    newkind=campaign
  else
    newkind=other
  fi
  test "$newkind" = "$LAST_CLOSE_KIND" || { echo "STOP: contradictory LAST_CLOSE_KIND ($LAST_CLOSE_KIND): newest close is $EFF_PATH; mail the lead"; exit 1; }
  if test "$newkind" = other; then
    echo "copy gate: newest close is non-campaign ($EFF_PATH); its Check covers the copy"; exit 0
  fi
  plan_id="$(basename "$(dirname "$EFF_PATH")" | sed -E 's/-[0-9]{8}T[0-9]{6}Z$//')"
  case "$plan_id" in cq-*-a[0-9]*) ;; *) echo "STOP: no campaign plan id in $EFF_PATH"; exit 1;; esac
  copy_ok="/Volumes/JW-EXT/scratch/items-rl171/tests/cases2-011351/hp01-s01-sol4-newest-f0-correct-other/desk-copy/$plan_id.ok"
  test -s "$copy_ok" || { echo "WAIT: no journal-copy marker $copy_ok for the newest close, campaign span $plan_id ($EFF_PATH): the lead's hash-verified copy is not done; retry at the next activation"; exit 1; }
  echo "journal copy of $plan_id: $(cat "$copy_ok")"     # record this line
)
