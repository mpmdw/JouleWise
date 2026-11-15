pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794729600 ] && [ "$n" -le 1794738899 ]; then echo 13:14-13:15   # Sun 15 Nov 00:00:00 .. Sun 15 Nov 02:34:59
  elif [ "$n" -ge 1794738900 ] && [ "$n" -le 1794768600 ]; then echo 02:00-02:35   # Sun 15 Nov 02:35:00 .. Sun 15 Nov 10:50:00
  elif [ "$n" -ge 1794777300 ] && [ "$n" -le 1794798450 ]; then echo 02:00-02:35   # Sun 15 Nov 13:15:00 .. Sun 15 Nov 19:07:30
  elif [ "$n" -ge 1794798451 ] && [ "$n" -le 1794815999 ]; then echo 13:14-13:15   # Sun 15 Nov 19:07:31 .. Sun 15 Nov 23:59:59
  else echo NONE; fi
}
