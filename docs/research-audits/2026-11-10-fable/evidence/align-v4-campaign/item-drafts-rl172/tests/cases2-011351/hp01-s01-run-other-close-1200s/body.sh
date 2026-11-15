effective_close || { echo "STOP: the receipt census failed; missing evidence stops the launch; mail the lead"; exit 1; }
HOST_LAST_CLOSE=$EFF_EPOCH    # the effective close (max of the census and OTHER_CLOSE_EPOCH), computed once (Sol confirm P1)
echo "host last close $HOST_LAST_CLOSE"
copy_gate || exit 1
test "$(date +%s)" -ge $((HOST_LAST_CLOSE + GAP)) || { echo "WAIT: close interval ($GAP s) after the latest close of anything on this host (RL-171 §6.1)"; exit 1; }
echo "REACHED-LAUNCH"