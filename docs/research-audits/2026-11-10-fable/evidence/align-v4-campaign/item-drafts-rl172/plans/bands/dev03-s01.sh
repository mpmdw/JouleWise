pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794816000 ] && [ "$n" -le 1794825299 ]; then echo 13:14-13:15   # Mon 16 Nov 00:00:00 .. Mon 16 Nov 02:34:59
  elif [ "$n" -ge 1794825300 ] && [ "$n" -le 1794855000 ]; then echo 02:00-02:35   # Mon 16 Nov 02:35:00 .. Mon 16 Nov 10:50:00
  elif [ "$n" -ge 1794863700 ] && [ "$n" -le 1794890890 ]; then echo 02:00-02:35   # Mon 16 Nov 13:15:00 .. Mon 16 Nov 20:48:10
  elif [ "$n" -ge 1794890891 ] && [ "$n" -le 1794902399 ]; then echo 13:14-13:15   # Mon 16 Nov 20:48:11 .. Mon 16 Nov 23:59:59
  else echo NONE; fi
}
