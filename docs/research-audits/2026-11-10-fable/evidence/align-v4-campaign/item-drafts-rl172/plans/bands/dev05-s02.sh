pick_arg() {   # $1 = epoch; prints the --batch-window argument, or NONE (RL-171 §3; bands from this pin's own plan)
  n=$1
  if   [ "$n" -ge 1794988800 ] && [ "$n" -le 1794998099 ]; then echo 13:14-13:15   # Wed 18 Nov 00:00:00 .. Wed 18 Nov 02:34:59
  elif [ "$n" -ge 1794998100 ] && [ "$n" -le 1795027800 ]; then echo 02:00-02:35   # Wed 18 Nov 02:35:00 .. Wed 18 Nov 10:50:00
  elif [ "$n" -ge 1795036500 ] && [ "$n" -le 1795055590 ]; then echo 02:00-02:35   # Wed 18 Nov 13:15:00 .. Wed 18 Nov 18:33:10
  elif [ "$n" -ge 1795055591 ] && [ "$n" -le 1795075199 ]; then echo 13:14-13:15   # Wed 18 Nov 18:33:11 .. Wed 18 Nov 23:59:59
  else echo NONE; fi
}
