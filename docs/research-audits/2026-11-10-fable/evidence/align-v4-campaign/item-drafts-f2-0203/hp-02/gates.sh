# Call from the rendered item; each phase reads its own fresh record.
hp_gate() {
  phase=$1
  observation=$2
  "$PY" -I -B "$HP_DRAFTS/prepare_hp_items.py" gate "$SPAN" "$phase" \
    --repo "$REPO" --kit "$KIT" --queue "$QUEUE_FILE" \
    --issue "$HP_ISSUE" --issue-sha "$HP_ISSUE_SHA" --observation "$observation" \
    --custody "$CUSTODY" --output "$OUT" --magistrate-pid "$MAGISTRATE_PID"
}
