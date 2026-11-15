pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794902400 ] && [ "$n" -le 1794911699 ]; then echo 13:14-13:15   # Tue 17 Nov 00:00:00 .. Tue 17 Nov 02:34:59
  elif [ "$n" -ge 1794911700 ] && [ "$n" -le 1794941400 ]; then echo 02:00-02:35   # Tue 17 Nov 02:35:00 .. Tue 17 Nov 10:50:00
  elif [ "$n" -ge 1794950100 ] && [ "$n" -le 1794969190 ]; then echo 02:00-02:35   # Tue 17 Nov 13:15:00 .. Tue 17 Nov 18:33:10
  elif [ "$n" -ge 1794969191 ] && [ "$n" -le 1794988799 ]; then echo 13:14-13:15   # Tue 17 Nov 18:33:11 .. Tue 17 Nov 23:59:59
  else echo NONE; fi
}
