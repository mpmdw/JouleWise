pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3 bands of this pin's own plan, cut by the 00:30 rule)
  n=$1
  if   [ "$n" -ge 1794731401 ] && [ "$n" -le 1794738899 ]; then echo 13:14-13:15   # Sun 15 Nov 00:30:01 .. Sun 15 Nov 02:34:59 (default-takes-over)
  elif [ "$n" -ge 1794738900 ] && [ "$n" -le 1794768600 ]; then echo 02:00-02:35   # Sun 15 Nov 02:35:00 .. Sun 15 Nov 10:50:00 (soak-wait)
  elif [ "$n" -ge 1794777300 ] && [ "$n" -le 1794795750 ]; then echo 02:00-02:35   # Sun 15 Nov 13:15:00 .. Sun 15 Nov 18:22:30 (00:30 rule)
  elif [ "$n" -ge 1794817801 ] && [ "$n" -le 1794825299 ]; then echo 13:14-13:15   # Mon 16 Nov 00:30:01 .. Mon 16 Nov 02:34:59 (default-takes-over)
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00 (soak-wait)
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794882150 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 18:22:30 (00:30 rule)
  else echo NONE; fi
}
