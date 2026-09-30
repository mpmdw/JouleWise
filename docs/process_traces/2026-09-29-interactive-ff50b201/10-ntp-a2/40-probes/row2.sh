#!/bin/bash
S=/private/tmp/claude-501/-Users-edr-code-JouleWise/ff50b201-b458-48cc-8d86-bb1b4bb19e19/scratchpad/n1delta3
T=$(cat $S/row2.tests)
(cd /Users/edr/code/JouleWise-wt-n1d3-new-ff50b201 && /opt/homebrew/bin/python3 -B -m unittest -v $T > $S/row2.new.log 2>&1; echo "new exit=$?")
(cd $S/oldov && /opt/homebrew/bin/python3 -B -m unittest -v $T > $S/row2.old.log 2>&1; echo "old exit=$?")
grep -E "\.\.\. |^Ran|^OK|^FAILED" $S/row2.new.log; echo "-----"; grep -E "\.\.\. |^Ran|^OK|^FAILED" $S/row2.old.log
